// main.go
package main

import (
	"bufio"
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"

	pdf "github.com/ledongthuc/pdf"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/transform"
)

var (
	outPath   = flag.String("o", "output.csv", "output csv path")
	layoutSep = flag.String("sep", `\s{2,}|\t+`, "regex separator for columns")
	enc       = flag.String("enc", "utf8", "output encoding: utf8 | sjis")
)

func main() {
	flag.Parse()
	if flag.NArg() < 1 {
		fmt.Println("Usage: go run main.go input.pdf [-o output.csv] [--enc utf8|sjis] [--sep REGEX]")
		return
	}
	in := flag.Arg(0)

	f, r, err := pdf.Open(in) // rはClose不要（ファイル時はfをClose）
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	sep := regexp.MustCompile(*layoutSep)

	// 出力
	outFile, err := os.Create(*outPath)
	if err != nil {
		log.Fatal(err)
	}
	defer outFile.Close()

	var writer *csv.Writer
	var bw *bufio.Writer

	switch strings.ToLower(*enc) {
	case "sjis":
		// Windows Excel向け：Shift_JISで出力（BOM不要/付けない）
		bw = bufio.NewWriter(transform.NewWriter(outFile, japanese.ShiftJIS.NewEncoder()))
		writer = csv.NewWriter(bw)
	default:
		// UTF-8 (BOM付き) → Mac/Win両対応しやすい
		outFile.Write([]byte{0xEF, 0xBB, 0xBF})
		bw = bufio.NewWriter(outFile)
		writer = csv.NewWriter(bw)
	}

	// ページごとにテキスト取得（レイアウト保持寄り）
	total := r.NumPage()
	for i := 1; i <= total; i++ {
		p := r.Page(i)
		if p.V.IsNull() {
			continue
		}
		text, err := p.GetPlainText(nil) // ToUnicodeを使ったユニコードテキスト
		if err != nil {
			log.Fatalf("page %d: %v", i, err)
		}
		for _, line := range strings.Split(text, "\n") {
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}
			fmt.Println(line)
			cols := sep.Split(line, -1)
			if err := writer.Write(cols); err != nil {
				log.Fatal(err)
			}
		}
	}

	writer.Flush()
	if err := writer.Error(); err != nil {
		log.Fatal(err)
	}
	if err := bw.Flush(); err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Done -> %s (encoding=%s)\n", *outPath, *enc)
}
