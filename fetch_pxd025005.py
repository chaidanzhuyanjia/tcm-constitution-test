#!/usr/bin/env python3
import requests, re, json, urllib.parse
from pathlib import Path
out=Path("pxd025005_fetch"); out.mkdir(exist_ok=True)
log=[]
xml_url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8733275/fullTextXML"
r=requests.get(xml_url,timeout=120,headers={"User-Agent":"Mozilla/5.0"})
r.raise_for_status()
xml=r.text
(out/"fullTextXML.xml").write_text(xml,encoding="utf-8")
log.append({"xml_url":xml_url,"status":r.status_code,"bytes":len(r.content)})
# capture supplementary href containing mmc1 or xlsx near supplemental data 1
hrefs=re.findall(r'(?:xlink:href|href)="([^"]+)"',xml)
cands=[h for h in hrefs if "mmc1" in h.lower()]
if not cands:
    cands=[h for h in hrefs if h.lower().endswith(".xlsx")]
log.append({"mmc1_candidates":cands[:20]})
if not cands:
    raise SystemExit("No mmc1/xlsx href in Europe PMC XML")
h=cands[0]
urls=[]
if h.startswith("http"):
    urls=[h]
else:
    urls=[
      urllib.parse.urljoin("https://pmc.ncbi.nlm.nih.gov/articles/PMC8733275/",h),
      urllib.parse.urljoin("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8733275/",h),
      urllib.parse.urljoin("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8733275/",h),
    ]
for u in urls:
    try:
        rr=requests.get(u,timeout=180,headers={"User-Agent":"Mozilla/5.0"},allow_redirects=True)
        log.append({"url":u,"status":rr.status_code,"final":rr.url,"bytes":len(rr.content),"type":rr.headers.get("content-type"),"prefix":rr.content[:16].hex()})
        if rr.status_code==200 and rr.content[:2]==b"PK" and len(rr.content)>1000000:
            (out/"mmc1.xlsx").write_bytes(rr.content)
            break
    except Exception as e:
        log.append({"url":u,"error":repr(e)})
(out/"fetch_log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
if not (out/"mmc1.xlsx").exists():
    raise SystemExit("No valid xlsx downloaded; log="+json.dumps(log))
print(json.dumps(log,indent=2))
