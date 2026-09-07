package main

import (
	"io"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024 * 64,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func streamHandler(hub *Hub, w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Failed to upgrade connection:", err)
		return
	}
	client := &Client{
		hub:  hub,
		conn: conn,
		send: make(chan []byte, 10),
	}
	client.hub.register <- client
	go client.writePump()
}

func ingestHandler(hub *Hub, w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	frame, err := io.ReadAll(r.Body)
	if err != nil || len(frame) == 0 {
		http.Error(w, "Invalid frame data", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	select {
	case hub.broadcast <- frame:
		w.WriteHeader(http.StatusOK)
	default:
		// If the hub buffer is completely full, we drop the frame to prevent
		// backpressure from crashing the Python script or Go server.
		log.Println("Warning: Hub broadcast buffer full, dropping frame")
		w.WriteHeader(http.StatusServiceUnavailable)
	}
}

func main() {
	// Initialize and spin up the concurrent Hub
	hub := NewHub()
	go hub.Run()

	// Route configurations
	http.HandleFunc("/ingest", func(w http.ResponseWriter, r *http.Request) {
		ingestHandler(hub, w, r)
	})

	http.HandleFunc("/stream", func(w http.ResponseWriter, r *http.Request) {
		streamHandler(hub, w, r)
	})

	log.Println("Go Video Broadcasting Service running on :8080")
	log.Println("Python Ingestion Endpoint: POST http://localhost:8080/ingest")
	log.Println("React WebSocket Endpoint:  ws://localhost:8080/stream")

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal("ListenAndServe:", err)
	}
}
