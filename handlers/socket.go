package handlers

import (
	"bytes"
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"nhooyr.io/websocket"

	"github.com/gen2brain/cam2ip/handlers/lad"
	"github.com/gen2brain/cam2ip/image"
	"github.com/gen2brain/cam2ip/reader"
)

// Socket handler.
type Socket struct {
	reader reader.ImageReader
	delay  int
}

// NewSocket returns new socket handler.
func NewSocket(reader reader.ImageReader, delay int) *Socket {
	return &Socket{reader, delay}
}

// ServeHTTP handles requests on incoming connections.
func (s *Socket) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	conn, err := websocket.Accept(w, r, nil)
	if err != nil {
		log.Printf("socket: accept: %v", err)
		return
	}

	ctx := context.Background()

	for {
		img, err := s.reader.Read()
		if err != nil {
			log.Printf("socket: read: %v", err)
			break
		}

		w := new(bytes.Buffer)

		err = image.NewEncoder(w).Encode(img)
		if err != nil {
			log.Printf("socket: encode: %v", err)
			continue
		}

		b64 := image.EncodeToString(w.Bytes())

		// strap on
		lad.Lad.Mu.Lock()
		if lad.Lad.Shoot {

			lad.Lad.PicCount++
			err := ioutil.WriteFile(fmt.Sprintf("raw/shot/IMG%d.jpg", lad.Lad.PicCount), w.Bytes(), 0777)
			if err != nil {
				log.Fatal(err)
			}
			lad.Lad.Shoot = false
		} else if lad.Lad.Recording {
			lad.Lad.Recorded = append(lad.Lad.Recorded, w.Bytes())
		}
		lad.Lad.Mu.Unlock()

		// end strap on
		err = conn.Write(ctx, websocket.MessageText, []byte(b64))
		if err != nil {
			break
		}

		time.Sleep(time.Duration(s.delay) * time.Millisecond)
	}

	conn.Close(websocket.StatusNormalClosure, "")
}
