#!/usr/bin/env python3
import requests, tarfile, io, re, json
from pathlib import Path
out=Path("pxd025005_fetch"); out.mkdir(exist_ok=True)
log=[]
oa="https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC8733275"
r=requests.get(oa,timeout=120,headers={"User-Agent":"Mozilla/5.0"})
r.raise_for_status()
text=r.text
log.append({"oa_status":r.status_code,"oa_url":r.url,"oa_text":text[:2000]})
m=re.search(r'href="(ftp://[^"]+\.tar\.gz)"',text)
if not m:
    m=re.search(r'href="(https?://[^"]+\.tar\.gz)"',text)
if not m:
    raise SystemExit("No OA tar.gz link found: "+text[:1000])
url=m.group(1)
if url.startswith("ftp://"):
    url="https://"+url[len("ftp://"):]
rr=requests.get(url,timeout=180,headers={"User-Agent":"Mozilla/5.0"})
rr.raise_for_status()
log.append({"package_url":url,"status":rr.status_code,"bytes":len(rr.content),"type":rr.headers.get("content-type")})
tf=tarfile.open(fileobj=io.BytesIO(rr.content),mode="r:gz")
names=tf.getnames()
log.append({"members_matching_mmc1":[n for n in names if "mmc1" in n.lower()]})
cand=[n for n in names if n.lower().endswith("mmc1.xlsx")]
if not cand:
    cand=[n for n in names if n.lower().endswith(".xlsx") and "mmc1" in n.lower()]
if not cand:
    raise SystemExit("mmc1.xlsx not found; xlsx members="+str([n for n in names if n.lower().endswith(".xlsx")][:30]))
data=tf.extractfile(cand[0]).read()
(out/"mmc1.xlsx").write_bytes(data)
(out/"fetch_log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
print(json.dumps(log,indent=2))
print("saved",len(data))
