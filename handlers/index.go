package handlers

import (
	"io/ioutil"
	"net/http"
	"os"
)

// Index handler.
type Index struct {
}

// NewIndex returns new Index handler.
func NewIndex() *Index {
	return &Index{}
}

// ServeHTTP handles requests on incoming connections.
func (i *Index) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" && r.Method != "HEAD" {
		http.Error(w, "405 Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}
	fd, _ := os.Open("html/index.html")
	content, _ := ioutil.ReadAll(fd)
	w.Write((content))
}
