### How to Build and Run this Tool

1. Initialize a Go module and fetch dependencies:
   ```bash
   go mod init proxybridge
   go get golang.org/x/net/proxy
   ```
2. Build the executable:
   ```bash
   go build -o proxybridge main.go
   ```
3. Run the bridge:
   * **Default parameters** (HTTP proxy on port `8080`, upstream SOCKS5 on port `1080`):
     ```bash
     ./proxybridge
     ```
   * **Custom parameters** with SOCKS5 authentication:
     ```bash
     ./proxybridge -http 127.0.0.1:8888 -socks5 12.34.56.78:1080 -user myuser -pass mypass

