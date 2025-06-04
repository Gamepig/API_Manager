package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

type APIResponse struct {
	Message   string  `json:"message"`
	Timestamp float64 `json:"timestamp"`
	Language  string  `json:"language"`
}

func handler(w http.ResponseWriter, r *http.Request) {
	response := APIResponse{
		Message:   "Hello from Golang API!",
		Timestamp: float64(time.Now().UnixNano()) / 1e9,
		Language:  "Golang",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/", handler)
	port := 8003
	fmt.Printf("Starting Golang API on port %d...\n", port)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", port), nil))
}
