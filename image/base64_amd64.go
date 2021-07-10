// +build amd64

package image

import (
	//"goost.org/encoding/base64"
	"encoding/base64"
)

func EncodeToString(src []byte) string {
	return base64.StdEncoding.EncodeToString(src)
	//return base64.StdEncoding.EncodeToString(src)
}
