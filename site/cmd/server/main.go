package main

import (
	"log"
	"site/internal/config"
	"site/internal/server"
)

func main() {
	s := server.New()

	if err := s.Run(":8080"); err != nil {
		log.Fatalf("server error: %v", err)
	}

	db := config.ConnectDB("postgres://user:password@localhost:5432/support")
}
