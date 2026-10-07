#!/usr/bin/env python3
"""OCR poster -> teks (opsional; butuh `pip install easyocr`). Dipakai untuk mengisi kolom ocr_text pada template 50 poster.
Hasil OCR sering salah ketik -> tinjau manual sebelum dievaluasi."""
import argparse, sys
from pathlib import Path
import pandas as pd
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv", required=True); ap.add_argument("--img_dir", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    import easyocr
    reader = easyocr.Reader(["id", "en"], gpu=False)
    df = pd.read_csv(a.csv)
    for i, r in df.iterrows():
        p = Path(a.img_dir) / r.image_file
        if p.exists() and not isinstance(r.get("ocr_text"), str):
            df.at[i, "ocr_text"] = "\n".join(reader.readtext(str(p), detail=0, paragraph=True))
            print("ok", r.case_id)
    df.to_csv(a.out, index=False, encoding="utf-8-sig")
if __name__ == "__main__": main()
