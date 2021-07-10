package lad

import (
	"net/http"
)

type List struct{}

func NewList() *List {
	return &List{}
}
func (l *List) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	Lad.ServeList(w, r)
}

type Record struct{}

func NewRecord() *Record {
	return &Record{}
}
func (r2 *Record) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	Lad.ServeRecord(w, r)
}

type Shoot struct{}

func NewShoot() *Shoot {
	return &Shoot{}
}
func (ss *Shoot) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	Lad.ServeShoot(w, r)
}

type RecordResult struct{}
type ProcessResult struct{}

func NewRR() *RecordResult {
	return &RecordResult{}
}
func NewPR() *ProcessResult {
	return &ProcessResult{}
}
func (rr *RecordResult) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	Lad.ServeRecordResult(w, r)
}
func (pr *ProcessResult) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	Lad.ServeProcessResult(w, r)
}
