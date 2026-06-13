package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"strings"
	"time"

	"golang.org/x/net/proxy"
)

// Config holds the CLI configuration settings
type Config struct {
	HTTPAddr   string
	SOCKS5Addr string
	Username   string
	Password   string
}

// ProxyServer handles incoming HTTP and HTTPS proxy connections
type ProxyServer struct {
	config     Config
	dialer     proxy.Dialer
	httpClient *http.Client
}

func main() {
	// 1. Parse command line flags for flexible configuration
	httpAddr := flag.String("http", "127.0.0.1:8080", "Address for this HTTP proxy server to listen on")
	socks5Addr := flag.String("socks5", "127.0.0.1:1080", "Address of the upstream SOCKS5 proxy")
	username := flag.String("user", "", "Optional username for SOCKS5 authentication")
	password := flag.String("pass", "", "Optional password for SOCKS5 authentication")
	flag.Parse()

	config := Config{
		HTTPAddr:   *httpAddr,
		SOCKS5Addr: *socks5Addr,
		Username:   *username,
		Password:   *password,
	}

	log.Printf("Initializing HTTP-to-SOCKS5 proxy bridge...")
	log.Printf("Target Upstream SOCKS5: %s", config.SOCKS5Addr)

	// 2. Initialize SOCKS5 Auth if credentials are provided
	var auth *proxy.Auth
	if config.Username != "" || config.Password != "" {
		auth = &proxy.Auth{
			User:     config.Username,
			Password: config.Password,
		}
		log.Printf("SOCKS5 Authentication enabled (User: %s)", config.Username)
	}

	// 3. Create the SOCKS5 dialer (uses proxy.Direct as a fallback system dialer)
	socksDialer, err := proxy.SOCKS5("tcp", config.SOCKS5Addr, auth, proxy.Direct)
	if err != nil {
		log.Fatalf("Failed to initialize SOCKS5 dialer: %v", err)
	}

	// 4. Create a custom HTTP Client that routes standard HTTP requests via SOCKS5
	transport := &http.Transport{
		DialContext: func(ctx context.Context, network, address string) (net.Conn, error) {
			// SOCKS5 dialer does not natively support DialContext; wrap it
			return socksDialer.Dial(network, address)
		},
		MaxIdleConns:          100,
		IdleConnTimeout:       90 * time.Second,
		TLSHandshakeTimeout:   10 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	server := &ProxyServer{
		config: config,
		dialer: socksDialer,
		httpClient: &http.Client{
			Transport: transport,
		},
	}

	// 5. Start the HTTP proxy server
	httpServer := &http.Server{
		Addr:    config.HTTPAddr,
		Handler: server,
	}

	log.Printf("HTTP Proxy listening and ready on http://%s", config.HTTPAddr)
	if err := httpServer.ListenAndServe(); err != nil {
		log.Fatalf("Server stopped unexpectedly: %v", err)
	}
}

// ServeHTTP acts as the controller routing HTTP methods appropriately
func (p *ProxyServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Note: Log line can be removed or silenced in high-throughput environments
	log.Printf("[Proxy-In] %s %s", r.Method, r.URL.String())

	if r.Method == http.MethodConnect {
		// HTTPS uses the HTTP CONNECT method to create an opaque TCP tunnel
		p.handleConnect(w, r)
	} else {
		// Standard HTTP requests are forwarded using our SOCKS5-configured client
		p.handleHTTP(w, r)
	}
}

// handleConnect processes HTTPS proxying (HTTP CONNECT tunneling)
func (p *ProxyServer) handleConnect(w http.ResponseWriter, r *http.Request) {
	// 1. Establish a TCP connection to the destination host via the SOCKS5 proxy
	destConn, err := p.dialer.Dial("tcp", r.Host)
	if err != nil {
		log.Printf("[Err] SOCKS5 connection to %s failed: %v", r.Host, err)
		http.Error(w, fmt.Sprintf("Failed to reach target host via SOCKS5: %v", err), http.StatusBadGateway)
		return
	}
	defer destConn.Close()

	// 2. Hijack the HTTP client connection to switch to raw TCP tunneling
	hijacker, ok := w.(http.Hijacker)
	if !ok {
		log.Printf("[Err] ResponseWriter does not support hijacking")
		http.Error(w, "Webserver error (Hijacking unsupported)", http.StatusInternalServerError)
		return
	}

	clientConn, _, err := hijacker.Hijack()
	if err != nil {
		log.Printf("[Err] Hijacking client connection failed: %v", err)
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	defer clientConn.Close()

	// 3. Notify the client that the raw TCP tunnel has successfully established
	_, _ = clientConn.Write([]byte("HTTP/1.1 200 Connection Established\r\n\r\n"))

	// 4. Bidirectionally pipe the raw data between the client and SOCKS5 destination
	errChan := make(chan error, 2)
	go func() {
		_, err := io.Copy(destConn, clientConn)
		errChan <- err
	}()
	go func() {
		_, err := io.Copy(clientConn, destConn)
		errChan <- err
	}()

	// Wait until either side terminates or encounters a transmission error
	if err := <-errChan; err != nil {
		// Treat connection resets and EOFs as standard behavior during disconnects
		if !strings.Contains(err.Error(), "use of closed network connection") {
			log.Printf("[Info] Active tunnel to %s closed: %v", r.Host, err)
		}
	}
}

// handleHTTP processes standard raw HTTP requests
func (p *ProxyServer) handleHTTP(w http.ResponseWriter, r *http.Request) {
	// Standard web forwarding requests require rewriting some protocol properties
	// 1. Create a clean outbound request clone
	outReq, err := http.NewRequest(r.Method, r.URL.String(), r.Body)
	if err != nil {
		log.Printf("[Err] Outbound request initialization failed: %v", err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 2. Copy the headers from the client to the outbound request
	copyHeaders(outReq.Header, r.Header)

	// Remove hop-by-hop HTTP headers standard to proxies
	removeHopByHopHeaders(outReq.Header)

	// 3. Execute the request through our SOCKS5 client
	resp, err := p.httpClient.Do(outReq)
	if err != nil {
		log.Printf("[Err] SOCKS5 forwarding failed for request: %v", err)
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// 4. Send back the headers and status code of the response
	copyHeaders(w.Header(), resp.Header)
	removeHopByHopHeaders(w.Header())
	w.WriteHeader(resp.StatusCode)

	// 5. Pipe the body payload
	_, _ = io.Copy(w, resp.Body)
}

// Utility: Deep copy headers mapping
func copyHeaders(dst, src http.Header) {
	for k, vv := range src {
		for _, v := range vv {
			dst.Add(k, v)
		}
	}
}

// Utility: Standard proxy systems strip local connection hop-by-hop headers
func removeHopByHopHeaders(h http.Header) {
	hopHeaders := []string{
		"Connection",
		"Keep-Alive",
		"Proxy-Authenticate",
		"Proxy-Authorization",
		"Te",
		"Trailers",
		"Transfer-Encoding",
		"Upgrade",
	}
	for _, hh := range hopHeaders {
		h.Del(hh)
	}
}
