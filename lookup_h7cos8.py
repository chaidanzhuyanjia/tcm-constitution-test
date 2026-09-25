#!/usr/bin/env python3
import requests, json, pathlib
out=pathlib.Path("uniprot_lookup"); out.mkdir(exist_ok=True)
urls=[
 "https://rest.uniprot.org/uniprotkb/H7COS8.json",
 "https://rest.uniprot.org/uniprotkb/search?query=accession:H7COS8&format=json"
]
res={}
for u in urls:
    try:
        r=requests.get(u,timeout=60,headers={"User-Agent":"Mozilla/5.0"})
        res[u]={"status":r.status_code,"text":r.text[:20000]}
    except Exception as e:
        res[u]={"error":repr(e)}
(out/"H7COS8.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(res,ensure_ascii=False)[:12000])
