#!/usr/bin/env python3
import json, re, os
from pathlib import Path
import requests, openpyxl

BASE="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-64954-2/MediaObjects/"
OUT=Path("cpcpps_supp"); OUT.mkdir(exist_ok=True)
manifest=[]
hits=[]
for n in range(3,15):
    ds=n-2
    fn=f"41467_2025_64954_MOESM{n}_ESM.xlsx"
    url=BASE+fn
    r=requests.get(url,timeout=90)
    r.raise_for_status()
    p=OUT/f"Supplementary_Dataset_{ds}.xlsx"
    p.write_bytes(r.content)
    wb=openpyxl.load_workbook(p,read_only=True,data_only=True)
    for ws in wb.worksheets:
        rows=ws.max_row; cols=ws.max_column
        sample=[]
        matched=[]
        for ri,row in enumerate(ws.iter_rows(values_only=True),1):
            vals=[("" if v is None else str(v)) for v in row]
            if ri<=8: sample.append(vals[:20])
            blob="\t".join(vals)
            if re.search(r"network|proximal|gene|z.?score|string|propagat",blob,re.I):
                if len(matched)<50: matched.append({"row":ri,"values":vals[:30]})
        rec={"dataset":ds,"file":p.name,"sheet":ws.title,"rows":rows,"cols":cols,"sample":sample,"matches":matched}
        manifest.append(rec)
        if matched or 80 <= rows <= 140:
            hits.append(rec)
(OUT/"scan_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"candidate_sheets.json").write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps([{"dataset":x["dataset"],"sheet":x["sheet"],"rows":x["rows"],"cols":x["cols"],"match_count":len(x["matches"])} for x in hits],ensure_ascii=False,indent=2))
