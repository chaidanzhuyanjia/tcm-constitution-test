#!/usr/bin/env python3
import csv, json, time, hashlib, gzip
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

HERB_ID="HERB005030"
ENDPOINTS=["http://herb.ac.cn/chedi/api/","http://47.92.70.12/chedi/api/"]
OUT=Path("herb2_acorus_alt"); RAW=OUT/"raw"; RAW.mkdir(parents=True,exist_ok=True)

def sha256(b): return hashlib.sha256(b).hexdigest()
def post_detail(entity_id,label,timeout=40):
    payload={"func_name":"detail_api","key_id":entity_id,"label":label,"v":entity_id}
    errs=[]
    for endpoint in ENDPOINTS:
        try:
            root=endpoint.split("/chedi")[0]
            r=requests.post(endpoint,json=payload,timeout=timeout,headers={
                "User-Agent":"HERB2-CP-Acorus-alt/1.0","Accept":"*/*","Content-Type":"application/json",
                "Origin":root,"Referer":root+f"/Detail/?v={entity_id}&label={label}"})
            if r.status_code!=200:
                errs.append(f"{endpoint} HTTP {r.status_code}"); continue
            raw=r.content
            return endpoint,json.loads(raw.decode("utf-8")),raw
        except Exception as e: errs.append(repr(e))
    raise RuntimeError(" ; ".join(errs))
def unwrap(v):
    if isinstance(v,list): return [unwrap(x) for x in v]
    if isinstance(v,dict) and "title" in v:
        t=v["title"]; return " ".join(map(str,t)) if isinstance(t,list) else t
    return v
def rows(table):
    if not isinstance(table,list) or not table: return []
    h=[str(unwrap(x)) for x in table[0]]
    return [{k:unwrap(r[i]) if i<len(r) else None for i,k in enumerate(h)} for r in table[1:] if isinstance(r,list)]
def pick(r,prefix):
    for v in r.values():
        vals=v if isinstance(v,list) else [v]
        for x in vals:
            if isinstance(x,str) and x.startswith(prefix): return x
    return ""
def gene(r):
    for k,v in r.items():
        kl=k.lower().replace(" ","_")
        if isinstance(v,str) and (kl in {"gene","gene_name","gene_symbol","target_name","target"} or ("gene" in kl and "id" not in kl)):
            if v and not v.startswith("HBTAR"): return v
    return ""

ep,obj,raw=post_detail(HERB_ID,"Herb")
hi=rows(obj.get("herb_ingredient"))
ingredients=sorted({pick(r,"HBIN") for r in hi if pick(r,"HBIN")})
(OUT/"herb_detail.json").write_bytes(raw)

def fetch(iid):
    ep,o,raw=post_detail(iid,"Ingredient")
    return iid,ep,raw,rows(o.get("ingredient_target"))

edges=[]; errors={}
with ThreadPoolExecutor(max_workers=6) as ex:
    futs={ex.submit(fetch,i):i for i in ingredients}
    for fut in as_completed(futs):
        iid=futs[fut]
        try:
            iid,ep,raw,rr=fut.result()
            for r in rr:
                edges.append({"ingredient_id":iid,"target_id":pick(r,"HBTAR"),"gene_symbol":gene(r),"source_endpoint":ep,
                              **{f"upstream__{k}":v for k,v in r.items()}})
        except Exception as e: errors[iid]=repr(e)

fields=[]
for r in edges:
    for k in r:
        if k not in fields: fields.append(k)
with (OUT/"ingredient_target_edges.tsv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter="\t"); w.writeheader()
    for r in edges:
        w.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in r.items()})
targets=sorted({r["target_id"] for r in edges if r["target_id"]})
genes=sorted({r["gene_symbol"] for r in edges if r["gene_symbol"]})
(OUT/"HERB005030_HBTAR.txt").write_text("\n".join(targets)+("\n" if targets else ""),encoding="utf-8")
(OUT/"HERB005030_genes.txt").write_text("\n".join(genes)+("\n" if genes else ""),encoding="utf-8")
qc={"herb_id":HERB_ID,"herb_ingredient_rows":len(hi),"unique_ingredients":len(ingredients),
    "ingredient_queries":len(ingredients),"ingredient_errors":errors,"unique_targets":len(targets),"unique_genes":len(genes),
    "ready":not errors and len(targets)>0}
(OUT/"QC_report.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(qc,ensure_ascii=False,indent=2))
