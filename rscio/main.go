package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"

	"rsc.io/pdf"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: go run main.go input.pdf output.csv")
		return
	}

	input := os.Args[1]
	output := os.Args[2]

	doc, err := pdf.Open(input)
	if err != nil {
		log.Fatal(err)
	}

	outFile, err := os.Create(output)
	if err != nil {
		log.Fatal(err)
	}
	defer outFile.Close()
	writer := csv.NewWriter(outFile)
	defer writer.Flush()

	// 空白2つ以上 or タブで列を分割
	re := regexp.MustCompile(`\s{2,}|\t+`)

	// 全ページを処理
	fmt.Println(doc.NumPage())
	for i := 1; i <= doc.NumPage(); i++ {
		page := doc.Page(i)
		if page.V.IsNull() {
			continue
		}
		content := page.Content()
		for _, t := range content.Text {
			fmt.Println(t.S)
			line := strings.TrimSpace(t.S)
			if line == "" {
				continue
			}
			cols := re.Split(line, -1)
			writer.Write(cols)
		}
	}

	fmt.Println("Done! ->", output)
}
