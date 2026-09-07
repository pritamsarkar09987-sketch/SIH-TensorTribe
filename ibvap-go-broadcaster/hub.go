package main

import (
	"log"
	"time"

	"github.com/gorilla/websocket"
)

type Client struct {
	conn *websocket.Conn
	hub  *Hub
	send chan []byte
}

type Hub struct {
	clients    map[*Client]bool
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
}

func NewHub() *Hub {
	return &Hub{
		broadcast:  make(chan []byte, 100), // Buffer to prevent blocking the Python ingestion
		register:   make(chan *Client),
		unregister: make(chan *Client),
		clients:    make(map[*Client]bool),
	}
}

func (h *Hub) Run() {
	for {
		select {
		case client := <-h.register:
			h.clients[client] = true
			log.Printf("Client connected. Total client: %d", len(h.clients))

		case client := <-h.unregister:
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
				log.Printf("CLient disconnected. Total client: %d", len(h.clients))
			}

		case frame := <-h.broadcast:
			// High-speed frame ingested from Python; push to all active React clients
			for client := range h.clients {
				select {
				case client.send <- frame:
					// Frame successfully queued for this client
				default:
					// If the client's send buffer is full (e.g., slow network),
					// we drop the client to prevent cascading system failure.
					close(client.send)
					delete(h.clients, client)
				}
			}
		}
	}
}

func (c *Client) writePump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	// 1. 'range' pulls each frame automatically
	for frame := range c.send {
		c.conn.SetWriteDeadline(time.Now().Add(2 * time.Second))

		// 2. Write the frame directly to the websocket
		if err := c.conn.WriteMessage(websocket.BinaryMessage, frame); err != nil {
			return // Trigger defer cleanup on network failure
		}
	}

	// 3. Reached only when c.send is closed by the Hub
	c.conn.WriteMessage(websocket.CloseMessage, []byte{})
}
