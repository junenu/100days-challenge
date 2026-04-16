package main

import (
	"log"
	"net/http"
	"os"

	"notes-api/handler"
	"notes-api/store"
)

func main() {
	dataFile := envOr("DATA_FILE", "notes.json")
	addr := envOr("ADDR", ":8080")

	s := store.New(dataFile)
	if err := s.Load(); err != nil {
		log.Fatalf("store load: %v", err)
	}

	mux := handler.NewMux(s)

	log.Printf("notes-api listening on %s  (data: %s)", addr, dataFile)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("server: %v", err)
	}
}

func envOr(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
