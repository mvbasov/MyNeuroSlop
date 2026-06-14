package main

import (
	"embed"
	"log"
	"://github.com"
)

// Wails pulls the index.html directly from this folder
//go:embed frontend/*
var assets embed.FS

func main() {
	app := application.New(application.Options{
		Name: "SlidingWindowEditor",
		Assets: application.AssetOptions{
			Handler: application.AssetFileServerFS(assets),
		},
	})

	app.Bind(NewApp()) // Binds your app.go file

	if err := app.Run(); err != nil {
		log.Fatal(err)
	}
}

