#!/usr/bin/env python3
import requests,json
from pathlib import Path
out=Path("pxd025005_fetch"); out.mkdir(exist_ok=True)
urls=[
 "https://ars.els-cdn.com/content/image/1-s2.0-S1535947621001481-mmc1.xlsx",
 "https://ars.els-cdn.com/content/image/1-s2.0-S1535947621001481-mmc1.xls",
]
log=[]
for u in urls:
    try:
        r=requests.get(u,timeout=180,headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.sciencedirect.com/"},allow_redirects=True)
        log.append({"url":u,"status":r.status_code,"final":r.url,"bytes":len(r.content),"type":r.headers.get("content-type"),"prefix":r.content[:16].hex()})
        if r.status_code==200 and r.content[:2]==b"PK" and len(r.content)>1000000:
            (out/"mmc1.xlsx").write_bytes(r.content); break
    except Exception as e:
        log.append({"url":u,"error":repr(e)})
(out/"fetch_log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
print(json.dumps(log,indent=2))
if not (out/"mmc1.xlsx").exists(): raise SystemExit("No valid Elsevier xlsx")
