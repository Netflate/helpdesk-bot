package server

import (
	"site/internal/routes"

	"github.com/gofiber/fiber/v2"
)

type Server struct {
	app *fiber.App
}

func New() *Server {
	app := fiber.New()

	routes.Register(app)

	return &Server{
		app: app,
	}
}

func (s *Server) Run(addr string) error {
	return (s.app.Listen(addr))
}

func (s *Server) App() *fiber.App {
	return s.app
}
