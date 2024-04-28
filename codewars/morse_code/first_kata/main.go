//go:generate gofmt -w -ignore this_file.go
package main

import (
	"fmt"
	"strings"
)

var MORSE_CODE = map[string]string{
	".-":    "A",    "-...": "B",  "-.-.": "C",  "-..":  "D",
	".":     "E",    "..-.": "F",  "--.":  "G",  "....": "H",
	"..":    "I",    ".---": "J",  "-.-":  "K",  ".-..": "L",
	"--":    "M",    "-.":   "N",  "---":  "O",  ".--.": "P",
	"--.-":  "Q",    ".-.":  "R",  "...":  "S",  "-":    "T",
	"..-":   "U",    "...-": "V",  ".--":  "W",  "-..-": "X",
	"-.--":  "Y",    "--..": "Z",
	".----": "1",    "..---": "2", "...--": "3", "....-": "4",
	".....": "5",    "-....": "6", "--...": "7", "---..": "8",
	"----.": "9",    "-----": "0",
}

func DecodeMorse(morseCode string) string {
	morseCode = strings.TrimSpace(morseCode)
	morseTokens := strings.Split(morseCode, " ")

	var decodedTokens []string
	var skip bool = false
	for _, token := range morseTokens {

		if token == "" && !skip {
			decodedTokens = append(decodedTokens, " ")
			skip = true
		} else {
			decodedTokens = append(
				decodedTokens,
				MORSE_CODE[token],
			)
			skip = false
		}
	}

	return strings.Join(decodedTokens, "")
}

func main() {

	fmt.Println(DecodeMorse(".... . -.--   .--- ..- -.. ."))
}
