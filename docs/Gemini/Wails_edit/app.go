package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"regexp"
)

type App struct {
	ctx          context.Context
	filePath     string
	fileHandle   *os.File
	fileSize     int64
	chunkSize    int64
}

type SearchResult struct {
	LineNumber int    `json:"lineNumber"`
	ByteOffset int64  `json:"byteOffset"`
	Text       string `json:"text"`
}

func NewApp() *App {
	return &App{
		chunkSize: 30 * 1024, // 30 KB optimal scroll step size
	}
}

func (a *App) OpenLargeFile(path string) (map[string]interface{}, error) {
	if a.fileHandle != nil {
		a.fileHandle.Close()
	}
	file, err := os.OpenFile(path, os.O_RDWR, 0644)
	if err != nil {
		return nil, err
	}
	a.fileHandle = file
	a.filePath = path

	info, err := file.Stat()
	if err != nil {
		return nil, err
	}
	a.fileSize = info.Size()

	return map[string]interface{}{
		"size":      a.fileSize,
		"chunkSize": a.chunkSize,
	}, nil
}

// ReadNextChunk handles the infinite scrolling retrieval pipeline
func (a *App) ReadNextChunk(offset int64) (string, error) {
	if a.fileHandle == nil {
		return "", fmt.Errorf("no file open")
	}
	if offset >= a.fileSize {
		return "", nil // Reached end of file
	}

	length := a.chunkSize
	if offset+length > a.fileSize {
		length = a.fileSize - offset
	}

	buffer := make([]byte, length)
	_, err := a.fileHandle.ReadAt(buffer, offset)
	if err != nil && err.Error() != "EOF" {
		return "", err
	}
	return string(buffer), nil
}

// GlobalSearch runs a fast line-by-line regex sweep across the entire file on disk
func (a *App) GlobalSearch(pattern string) ([]SearchResult, error) {
	if a.filePath == "" {
		return nil, fmt.Errorf("no active file loaded")
	}

	// Re-open fresh read handle to avoid modifying the concurrent read pointer position
	file, err := os.Open(a.filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	re, err := regexp.Compile("(?i)" + pattern) // Case-insensitive matching standard
	if err != nil {
		return nil, fmt.Errorf("invalid search pattern: %v", err)
	}

	var results []SearchResult
	scanner := bufio.NewScanner(file)
	
	var lineNumber int = 0
	var currentByteOffset int64 = 0

	for scanner.Scan() {
		lineNumber++
		lineText := scanner.Text()
		
		if re.MatchString(lineText) {
			results = append(results, SearchResult{
				LineNumber: lineNumber,
				ByteOffset: currentByteOffset,
				Text:       lineText,
			})
		}
		// Track accurate byte location for jumps
		currentByteOffset += int64(len(lineText) + 1) // +1 for the newline separator block
	}

	return results, scanner.Err()
}

