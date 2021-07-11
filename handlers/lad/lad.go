package lad

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
)

type ProcessRequest struct {
	pType  string
	id     int
	face   bool
	green  bool
	resize bool
}

type LAD struct {
	Shoot        bool
	Recording    bool
	Recorded     [][]byte
	Mu           sync.Mutex
	PicCount     int `json:"picCount"`
	RecCount     int `json:"recCount"`
	RecFrame     int
	CurrentFrame int
	MaxFrames    int
}

func (lad *LAD) DoProcess(pr ProcessRequest) bool {
	lad.Mu.Lock()
	defer lad.Mu.Unlock()
	switch pr.pType {
	case "vid":
		if lad.RecCount < pr.id {
			return false
		}
	case "img":
		if lad.PicCount < pr.id {
			return false
		}
	default:
		log.Fatal("invalid process type")
	}

	cmd := exec.Command("ls", "-ll")
	err := cmd.Run()
	return err == nil
}

func (lad *LAD) DoRecord() bool {
	lad.Mu.Lock()
	defer lad.Mu.Unlock()
	if lad.Shoot {
		return false
	}
	lad.Recording = !lad.Recording //进行状态变更
	fmt.Println("recording=", lad.Recording)
	if lad.Recording { //开始录像
		lad.RecCount++
		err := os.MkdirAll(fmt.Sprintf("raw/recorded/%d", lad.RecCount), 0777)
		if err != nil {
			log.Fatal(err)
		}
		return true
	} else { //结束录像
		for i, v := range lad.Recorded {
			err := ioutil.WriteFile(fmt.Sprintf("raw/recorded/%d/IMG%d.jpg", lad.RecCount, i+1), v, 0777)
			if err != nil {
				log.Fatal(err)
			}
		}
		lad.Recorded = make([][]byte, 0)
		return false
	}
}
func (lad *LAD) DoShoot() bool {
	lad.Mu.Lock()
	defer lad.Mu.Unlock()
	if lad.Recording {
		return false
	} else {
		lad.Shoot = true
		return true
	}
}
func NewLad() *LAD {

	var dirs = []string{"shot", "recorded"}
	for _, v := range dirs {
		os.RemoveAll("raw/" + v)
		os.Mkdir("raw/"+v, 0777)
		os.Create("raw/" + v + "/.gitkeep")
		os.RemoveAll("processed/" + v)
		os.Mkdir("processed/"+v, 0777)
		os.Create("processed/" + v + "/.gitkeep")
	}
	return &LAD{
		Shoot:        false,
		Recording:    false,
		Recorded:     make([][]byte, 0),
		PicCount:     0,
		RecCount:     0,
		RecFrame:     0,
		CurrentFrame: 1,
		MaxFrames:    0,
	}
}
func (lad *LAD) ServeList(w http.ResponseWriter, r *http.Request) {

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	b, _ := json.Marshal(lad)
	w.Write(b)
}
func (lad *LAD) ServeShoot(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	result := make(map[string]bool)
	result["success"] = lad.DoShoot()
	b, _ := json.Marshal(result)
	w.Write(b)
}
func (lad *LAD) ServeRecord(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	result := make(map[string]bool)
	result["recording"] = lad.DoRecord()
	b, _ := json.Marshal(result)
	w.Write(b)
}
func (lad *LAD) ServeRecordResult(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	v := r.URL.Query()
	sid := v.Get("id")
	files, _ := ioutil.ReadDir(fmt.Sprintf("raw/recorded/%s", sid))
	result := make(map[string]int)
	result["frameCount"] = len(files) - 1
	b, _ := json.Marshal(result)
	w.Write(b)
}

func (lad *LAD) ServeProcess(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	v := r.URL.Query()
	var id int
	_, err := fmt.Sscanf(v.Get("id"), "%d", &id)
	if err != nil {
		log.Fatal(err)
	}
	pr := ProcessRequest{
		pType:  v.Get("type"),
		id:     id,
		face:   v.Get("face") == "true",
		green:  v.Get("green") == "true",
		resize: v.Get("resize") == "true",
	}
	result := make(map[string]bool)
	result["success"] = Lad.DoProcess(pr)
	b, _ := json.Marshal(result)
	w.Write(b)
}

var Lad = NewLad()
