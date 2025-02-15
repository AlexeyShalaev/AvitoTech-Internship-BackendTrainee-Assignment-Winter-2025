package pkg

import (
	"github.com/gin-gonic/gin"
)

type Server struct {
	router *gin.Engine
}

func NewServer(router *gin.Engine) *Server {
	return &Server{router: router}
}

func (s *Server) Run(addr string) error {
	return s.router.Run(addr)
}
