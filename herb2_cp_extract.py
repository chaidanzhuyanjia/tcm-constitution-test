#!/usr/bin/env python3
import csv, json, time, hashlib
from pathlib import Path
import requests

HERBS = {
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
ENDPOINTS=["http://herb.ac.cn/chedi/api/","http://47.92.70.12/chedi/api/"]
OUT=Path("herb2_output"); RAW=OUT/"raw"; RAW.mkdir(parents=True,exist_ok=True)

def sha256(b): return hashlib.sha256(b).hexdigest()

def post_detail(herb_id):
    payload={"func_name":"detail_api","key_id":herb_id,"label":"Herb","v":herb_id}
    errs=[]
    for endpoint in ENDPOINTS:
        try:
            r=requests.post(
                endpoint, json=payload, timeout=90,
                headers={
                    "User-Agent":"HERB2-CP-GHA/2.0",
                    "Accept":"*/*",
                    "Content-Type":"application/json",
                    "Origin":endpoint.split("/chedi")[0],
                    "Referer":endpoint.split("/chedi")[0]+f"/Detail/?v={herb_id}&label=Herb",
                }
            )
            raw=r.content
            if r.status_code!=200:
                errs.append(f"{endpoint} -> HTTP {r.status_code}: {raw[:180]!r}")
                continue
            obj=json.loads(raw.decode("utf-8"))
            return endpoint,obj,raw,payload
        except Exception as e:
            errs.append(f"{endpoint} -> {repr(e)}")
    raise RuntimeError(" ; ".join(errs))

def unwrap(v):
    if isinstance(v,list): return [unwrap(x) for x in v]
    if isinstance(v,dict) and "title" in v:
        t=v["title"]
        if isinstance(t,list): return " ".join(map(str,t))
        return t
    return v

def table_to_rows(table):
    if not isinstance(table,list) or not table: return []
    hdr=[str(unwrap(x)) for x in (table[0] if isinstance(table[0],list) else [])]
    out=[]
    for row in table[1:]:
        if not isinstance(row,list): continue
        out.append({h:unwrap(row[i]) if i<len(row) else None for i,h in enumerate(hdr)})
    return out

def pick_id(row,prefix):
    for v in row.values():
        vals=v if isinstance(v,list) else [v]
        for x in vals:
            if isinstance(x,str) and x.startswith(prefix):
                return x
    return ""

def pick_gene(row):
    preferred=[]
    for k,v in row.items():
        kl=k.lower().replace(" ","_")
        if ("gene" in kl or kl in {"target_name","target"}) and isinstance(v,str):
            preferred.append(v)
    for v in preferred:
        if v and not v.startswith("HBTAR"):
            return v
    return ""

def write_tsv(path,rows):
    if not rows:
        path.write_text("",encoding="utf-8"); return
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
        w.writeheader()
        for r in rows:
            rr={k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in r.items()}
            w.writerow(rr)

hi_edges=[]; it_edges=[]; paths=[]; errors={}; raw_manifest=[]
for formula,ids in HERBS.items():
    for hid in ids:
        try:
            endpoint,obj,raw,payload=post_detail(hid)
            raw_name=f"{hid}_detail.json"
            (RAW/raw_name).write_bytes(raw)
            raw_manifest.append({
                "formula":formula,"herb_id":hid,"endpoint":endpoint,
                "payload":payload,"raw_file":f"raw/{raw_name}",
                "sha256":sha256(raw),"retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
            })
            hi=table_to_rows(obj.get("herb_ingredient"))
            it=table_to_rows(obj.get("ingredient_target"))
            ing_ids={pick_id(r,"HBIN") for r in hi}; ing_ids.discard("")
            if not hi:
                raise RuntimeError("herb_ingredient section missing or empty")
            for r in hi:
                iid=pick_id(r,"HBIN")
                hi_edges.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,**r})
            for r in it:
                iid=pick_id(r,"HBIN"); tid=pick_id(r,"HBTAR"); gene=pick_gene(r)
                it_edges.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,"target_id":tid,"gene_symbol":gene,**r})
                if iid and iid in ing_ids and (tid or gene):
                    paths.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,"target_id":tid,"gene_symbol":gene})
            if not it:
                raise RuntimeError("ingredient_target section missing or empty")
        except Exception as e:
            errors[hid]=repr(e)

summary=[]
for formula,ids in HERBS.items():
    fp=[r for r in paths if r["formula"]==formula]
    summary.append({
        "formula":formula,
        "mapped_herbs":len(ids),
        "herbs_with_paths":len({r["herb_id"] for r in fp}),
        "unique_ingredients":len({r["ingredient_id"] for r in fp if r["ingredient_id"]}),
        "unique_targets":len({r["target_id"] for r in fp if r["target_id"]}),
        "unique_genes":len({r["gene_symbol"] for r in fp if r["gene_symbol"]}),
        "paths":len(fp)
    })
    genes=sorted({r["gene_symbol"] for r in fp if r["gene_symbol"]})
    tids=sorted({r["target_id"] for r in fp if r["target_id"]})
    (OUT/f"{formula}_genes.txt").write_text("\n".join(genes)+("\n" if genes else ""),encoding="utf-8")
    (OUT/f"{formula}_HBTAR.txt").write_text("\n".join(tids)+("\n" if tids else ""),encoding="utf-8")

write_tsv(OUT/"herb_ingredient_edges.tsv",hi_edges)
write_tsv(OUT/"ingredient_target_edges.tsv",it_edges)
write_tsv(OUT/"formula_paths.tsv",paths)
write_tsv(OUT/"formula_summary.tsv",summary)

qc={
    "errors":errors,
    "summary":summary,
    "raw_calls":len(raw_manifest),
    "herb_ingredient_edges":len(hi_edges),
    "ingredient_target_edges":len(it_edges),
    "paths":len(paths),
    "primary_ready":(
        not errors
        and all(x["unique_targets"]>=5 for x in summary)
        and all(x["herbs_with_paths"]==x["mapped_herbs"] for x in summary)
    )
}
(OUT/"QC_report.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
manifest={
    "source":"HERB 2.0 live detail_api",
    "endpoints":ENDPOINTS,
    "frozen_herbs":HERBS,
    "raw_calls":raw_manifest,
    "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
}
(OUT/"run_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(qc,ensure_ascii=False,indent=2))
