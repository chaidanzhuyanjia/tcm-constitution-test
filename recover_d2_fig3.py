#!/usr/bin/env python3
import requests, fitz, re, json
from pathlib import Path

URL="https://www.nature.com/articles/s41467-025-64954-2.pdf"
OUT=Path("d2_recovery"); OUT.mkdir(exist_ok=True)
r=requests.get(URL,timeout=120,headers={"User-Agent":"Mozilla/5.0"})
r.raise_for_status()
(OUT/"paper.pdf").write_bytes(r.content)
doc=fitz.open(stream=r.content,filetype="pdf")
for pageno in [5,6]:
    page=doc[pageno]
    text=page.get_text("text")
    (OUT/f"page_{pageno+1}_text.txt").write_text(text,encoding="utf-8")
    words=page.get_text("words")
    (OUT/f"page_{pageno+1}_words.json").write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding="utf-8")
    pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
    pix.save(OUT/f"page_{pageno+1}.png")
print("pages",doc.page_count,"bytes",len(r.content))
