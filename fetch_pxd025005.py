#!/usr/bin/env python3
import requests, json
from pathlib import Path
urls=[
"https://pmc.ncbi.nlm.nih.gov/articles/PMC8733275/bin/mmc1.xlsx",
"https://pmc.ncbi.nlm.nih.gov/articles/instance/8733275/bin/mmc1.xlsx",
"https://pmc.ncbi.nlm.nih.gov/articles/PMC8733275/bin/mmc1.xlsx?download=1",
]
out=Path("pxd025005_fetch"); out.mkdir(exist_ok=True)
log=[]
for u in urls:
    try:
        r=requests.get(u,timeout=120,headers={"User-Agent":"Mozilla/5.0"},allow_redirects=True)
        log.append({"url":u,"status":r.status_code,"final":r.url,"bytes":len(r.content),"type":r.headers.get("content-type")})
        if r.status_code==200 and r.content[:2]==b"PK" and len(r.content)>1000000:
            (out/"mmc1.xlsx").write_bytes(r.content)
            break
    except Exception as e:
        log.append({"url":u,"error":repr(e)})
(out/"fetch_log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
if not (out/"mmc1.xlsx").exists():
    raise SystemExit("No valid mmc1.xlsx downloaded")
print(log)
