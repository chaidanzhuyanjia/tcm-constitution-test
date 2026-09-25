#!/usr/bin/env python3
import csv, json, time
from pathlib import Path
import requests

HERBS = {
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
DIRECT=[
 "http://47.92.70.12/chedi/api/",
 "http://herb.ac.cn/chedi/api/",
]
OUT=Path("herb2_output"); RAW=OUT/"raw"; RAW.mkdir(parents=True,exist_ok=True)

def unwrap(v):
    if isinstance(v,list): return [unwrap(x) for x in v]
    if isinstance(v,dict) and "title" in v:
        t=v.get("title")
        return " ".join(map(str,t)) if isinstance(t,list) else t
    return v

def table_rows(t):
    if not isinstance(t,list) or not t: return []
    hdr=[str(unwrap(x)) for x in t[0]]
    out=[]
    for row in t[1:]:
        if not isinstance(row,list): continue
        out.append({h:(unwrap(row[i]) if i<len(row) else None) for i,h in enumerate(hdr)})
    return out

def direct_detail(hid):
    payload={"func_name":"detail_api","key_id":hid,"label":"Herb","v":hid}
    errs=[]
    for url in DIRECT:
        try:
            r=requests.post(url,json=payload,timeout=45,headers={"User-Agent":"HERB2-CP-GHA/2.0","Content-Type":"application/json"})
            r.raise_for_status()
            raw=r.content
            obj=json.loads(r.text)
            (RAW/f"{hid}_detail.json").write_bytes(raw)
            return obj,url
        except Exception as e:
            errs.append(f"{url}: {repr(e)}")
    raise RuntimeError(" | ".join(errs))

def pick_id(row,prefix):
    for v in row.values():
        vals=v if isinstance(v,list) else [v]
        for x in vals:
            if isinstance(x,str) and x.startswith(prefix): return x
    return ""

def pick_gene(row):
    for k,v in row.items():
        kl=k.lower()
        if isinstance(v,str) and v and not v.startswith("HBTAR"):
            if kl in {"target name","gene","gene symbol","target"} or "gene symbol" in kl or "target name" in kl:
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

hi_edges=[]; it_edges=[]; paths=[]; summary=[]; errors={}; source_ep={}
for formula,ids in HERBS.items():
    for hid in ids:
        try:
            obj,ep=direct_detail(hid); source_ep[hid]=ep
            hi=table_rows(obj.get("herb_ingredient"))
            it=table_rows(obj.get("ingredient_target"))
            ing_ids={pick_id(r,"HBIN") for r in hi}; ing_ids.discard("")
            for r in hi:
                hi_edges.append({"formula":formula,"herb_id":hid,"ingredient_id":pick_id(r,"HBIN"),**r})
            for r in it:
                iid=pick_id(r,"HBIN"); tid=pick_id(r,"HBTAR"); gene=pick_gene(r)
                it_edges.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,"target_id":tid,"gene_symbol":gene,**r})
                if iid and iid in ing_ids and (tid or gene):
                    paths.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,"target_id":tid,"gene_symbol":gene})
            if not hi:
                errors[hid]="detail_api returned zero herb_ingredient rows"
            elif not it:
                errors[hid]="detail_api returned zero ingredient_target rows"
        except Exception as e:
            errors[hid]=repr(e)
        time.sleep(0.2)

for formula,ids in HERBS.items():
    fp=[r for r in paths if r["formula"]==formula]
    row={
        "formula":formula,"mapped_herbs":len(ids),
        "herbs_with_paths":len({r["herb_id"] for r in fp}),
        "unique_ingredients":len({r["ingredient_id"] for r in fp if r["ingredient_id"]}),
        "unique_targets":len({r["target_id"] for r in fp if r["target_id"]}),
        "unique_genes":len({r["gene_symbol"] for r in fp if r["gene_symbol"]}),
        "paths":len(fp)
    }
    summary.append(row)
    genes=sorted({r["gene_symbol"] for r in fp if r["gene_symbol"]})
    tids=sorted({r["target_id"] for r in fp if r["target_id"]})
    (OUT/f"{formula}_genes.txt").write_text("\n".join(genes)+("\n" if genes else ""),encoding="utf-8")
    (OUT/f"{formula}_HBTAR.txt").write_text("\n".join(tids)+("\n" if tids else ""),encoding="utf-8")

write_tsv(OUT/"herb_ingredient_edges.tsv",hi_edges)
write_tsv(OUT/"ingredient_target_edges.tsv",it_edges)
write_tsv(OUT/"formula_paths.tsv",paths)
write_tsv(OUT/"formula_summary.tsv",summary)
qc={
 "errors":errors,"source_endpoint_by_herb":source_ep,"summary":summary,
 "primary_ready":not errors and all(x["unique_targets"]>=5 and x["herbs_with_paths"]==x["mapped_herbs"] for x in summary)
}
(OUT/"QC_report.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"run_manifest.json").write_text(json.dumps({
 "source":"HERB 2.0 live detail_api direct POST","endpoints":DIRECT,
 "frozen_herbs":HERBS,"retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(qc,ensure_ascii=False,indent=2))
