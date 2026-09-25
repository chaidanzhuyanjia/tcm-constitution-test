#!/usr/bin/env python3
import json, requests, time
from pathlib import Path
Path("diag_output").mkdir(exist_ok=True)
out={}
payload={"func_name":"detail_api","key_id":"HERB000242","label":"Herb","v":"HERB000242"}
for name,url in [
    ("herb_domain","http://herb.ac.cn/chedi/api/"),
    ("herb_ip","http://47.92.70.12/chedi/api/")
]:
    try:
        t=time.time()
        r=requests.post(url,json=payload,timeout=5,headers={"Content-Type":"application/json","User-Agent":"HERB2-CP-diagnostic/1.0"})
        out[name]={"status":r.status_code,"elapsed":time.time()-t,"len":len(r.content),"prefix":r.text[:300]}
    except Exception as e:
        out[name]={"error":repr(e)}
for name,method,url,body in [
    ("pipe_search_meta","GET","https://gateway.pipeworx.io/v1/tools/herb_tcm_herb_search",None),
    ("pipe_detail_meta_candidate","GET","https://gateway.pipeworx.io/v1/tools/herb_tcm_herb_detail",None),
    ("pipe_pack_search","POST","https://gateway.pipeworx.io/v1/tools/search_packs",{"query":"HERB herb detail traditional Chinese medicine"})
]:
    try:
        t=time.time()
        if method=="GET": r=requests.get(url,timeout=8)
        else: r=requests.post(url,json=body,timeout=8,headers={"Content-Type":"application/json"})
        out[name]={"status":r.status_code,"elapsed":time.time()-t,"len":len(r.content),"prefix":r.text[:5000]}
    except Exception as e:
        out[name]={"error":repr(e)}
Path("diag_output/diagnostic.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False,indent=2))
