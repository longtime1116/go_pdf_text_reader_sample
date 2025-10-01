#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
import sys
import pandas as pd

try:
    import tabula
except Exception as e:
    print("tabula-py が見つかりません。先に:\n  /usr/bin/python3 -m pip install --user tabula-py pandas\n", file=sys.stderr)
    raise

def parse_args():
    ap = argparse.ArgumentParser(description="PDFの表をTabulaでCSV化（lattice/stream, columns対応）")
    ap.add_argument("input", help="入力PDFパス")
    ap.add_argument("-o", "--outdir", default="csv_out", help="CSV出力ディレクトリ")
    ap.add_argument("-p", "--pages", default="all", help='抽出ページ（例: "all" / "1-3,5"）')
    ap.add_argument("-a", "--area", default=None, help='抽出領域（pt）: "top,left,bottom,right"')
    ap.add_argument("--mode", choices=["lattice","stream"], default="lattice", help="抽出モード")
    ap.add_argument("--guess", choices=["true","false"], default="true", help="Tabulaの推測を使うか")
    ap.add_argument("--columns", default=None, help='列の分割x座標（pt）: "x1,x2,..."')
    ap.add_argument("--merge", action="store_true", help="検出テーブルを1CSVに結合")
    ap.add_argument("--outfile", default="tables.csv", help="--merge時のファイル名")
    ap.add_argument("--no-bom", action="store_true", help="UTF-8のBOMを付けない（既定はBOM付）")
    ap.add_argument("--stream-fallback", action="store_true", help="latticeで0件ならstreamで再試行")
    return ap.parse_args()

def ensure_java():
    from shutil import which
    if which("java") is None:
        sys.exit("java が見つかりません。`brew install openjdk` 実行後、PATH/JAVA_HOMEを通してください。")

def parse_float_list(s):
    return [float(x.strip()) for x in s.split(",") if x.strip()]

def write_csv(df: pd.DataFrame, path: Path, add_bom: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    enc = "utf-8-sig" if add_bom else "utf-8"
    df.to_csv(path, index=False, encoding=enc)

def main():
    args = parse_args()
    ensure_java()

    pdf_path = Path(args.input).expanduser().resolve()
    if not pdf_path.exists():
        sys.exit(f"入力ファイルが見つかりません: {pdf_path}")

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    lattice = (args.mode == "lattice")
    stream  = (args.mode == "stream")
    guess   = (args.guess.lower() == "true")

    read_kwargs = dict(
        pages=args.pages,
        lattice=lattice,
        stream=stream,
        guess=guess,
        multiple_tables=True,
        pandas_options={"dtype": str}
    )
    if args.area:
        try:
            top, left, bottom, right = map(float, args.area.split(","))
            read_kwargs["area"] = (top, left, bottom, right)
        except Exception:
            sys.exit('areaの形式が不正です。例: -a "110,28,555,820"')

    if args.columns:
        try:
            read_kwargs["columns"] = parse_float_list(args.columns)
        except Exception:
            sys.exit('columnsの形式が不正です。例: --columns "95,245,330,420,510,600,690,780"')

    print(f"[INFO] mode={args.mode} guess={guess} pages={args.pages} area={args.area or 'FULL'} columns={args.columns or '-'}")

    try:
        tables = tabula.read_pdf(str(pdf_path), **read_kwargs)
    except Exception as e:
        sys.exit(f"Tabula実行エラー: {e}")

    if (not tables or len(tables) == 0) and args.stream_fallback and lattice:
        print("[WARN] latticeで0件。streamで再試行します（guess=false推奨）。")
        read_kwargs.update(lattice=False, stream=True, guess=False)
        try:
            tables = tabula.read_pdf(str(pdf_path), **read_kwargs)
        except Exception as e:
            sys.exit(f"Tabula(stream)実行エラー: {e}")

    if not tables or len(tables) == 0:
        sys.exit("[ERROR] テーブルが検出できませんでした。-a を調整、または --mode stream --guess false と --columns を指定してください。")

    # 正規化（NaN→""、前後空白除去）
    norm = []
    max_cols = 0
    for df in tables:
        df = df.fillna("").applymap(lambda x: str(x).strip())
        norm.append(df)
        max_cols = max(max_cols, df.shape[1])

    # 列数を最大に合わせてパディング（空セル保持）
    fixed = []
    for df in norm:
        if df.shape[1] < max_cols:
            for i in range(max_cols - df.shape[1]):
                df[f"_pad{i+1}"] = ""
        df = df.reindex(sorted(df.columns, key=lambda c: (c.startswith("_pad"), c)), axis=1)
        fixed.append(df)

    if args.merge:
        merged = []
        for i, df in enumerate(fixed):
            merged.append(df)
            if i != len(fixed) - 1:
                merged.append(pd.DataFrame([[""] * df.shape[1]]))
        outpath = outdir / args.outfile
        write_csv(pd.concat(merged, ignore_index=True), outpath, add_bom=not args.no_bom)
        print(f"[DONE] {outpath}  tables={len(fixed)}")
        return

    for i, df in enumerate(fixed, start=1):
        outpath = outdir / f"table_{args.mode}_{i:03d}.csv"
        write_csv(df, outpath, add_bom=not args.no_bom)
    print(f"[DONE] {len(fixed)}ファイルを書き出しました -> {outdir}")

if __name__ == "__main__":
    main()
