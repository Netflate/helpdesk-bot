package main

import (
	"log"
	"site/internal/server"
)

func main() {
	s := server.New()

	if err := s.Run(":8080"); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
