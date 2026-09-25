#!/usr/bin/env python3
import csv, json, time, gzip, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

HERBS = {
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
DIRECT=["http://47.92.70.12/chedi/api/","http://herb.ac.cn/chedi/api/"]
OUT=Path("herb2_output"); RAW_H=OUT/"raw_herb"; RAW_I=OUT/"raw_ingredient"
RAW_H.mkdir(parents=True,exist_ok=True); RAW_I.mkdir(parents=True,exist_ok=True)
TLS=threading.local()

def session():
    if not hasattr(TLS,"s"):
        TLS.s=requests.Session()
        TLS.s.headers.update({"User-Agent":"HERB2-CP-GHA/3.0","Content-Type":"application/json"})
    return TLS.s

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

def api_detail(eid,label,retries=3):
    payload={"func_name":"detail_api","key_id":eid,"label":label,"v":eid}
    errs=[]
    for attempt in range(retries):
        for url in DIRECT:
            try:
                r=session().post(url,json=payload,timeout=60)
                r.raise_for_status()
                obj=json.loads(r.text)
                return obj,url,r.content
            except Exception as e:
                errs.append(f"attempt={attempt+1} {url}: {type(e).__name__}: {e}")
        time.sleep(min(4, 0.8*(2**attempt)))
    raise RuntimeError(" | ".join(errs[-6:]))

def pick_id(row,prefix):
    for v in row.values():
        vals=v if isinstance(v,list) else [v]
        for x in vals:
            if isinstance(x,str) and x.startswith(prefix): return x
    return ""

def pick_gene(row):
    # HERB ingredient_target rows observed in public examples expose Target name;
    # retain all upstream columns regardless, this is only a convenience field.
    for k,v in row.items():
        kl=k.lower().replace("_"," ").strip()
        if isinstance(v,str) and v and not v.startswith("HBTAR"):
            if kl in {"target name","gene","gene symbol","target"} or "gene symbol" in kl:
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

# Phase 1: 26 herb details -> complete herb_ingredient
herb_details={}; herb_errors={}; source_herb={}
hi_edges=[]; ingredient_to_herbformulas={}
for formula,ids in HERBS.items():
    for hid in ids:
        try:
            obj,ep,raw=api_detail(hid,"Herb")
            source_herb[hid]=ep
            (RAW_H/f"{hid}_detail.json.gz").write_bytes(gzip.compress(raw,compresslevel=6))
            herb_details[hid]=obj
            hi=table_rows(obj.get("herb_ingredient"))
            if not hi:
                herb_errors[hid]="zero herb_ingredient rows"
            for r in hi:
                iid=pick_id(r,"HBIN")
                if not iid: continue
                hi_edges.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,**r})
                ingredient_to_herbformulas.setdefault(iid,set()).add((formula,hid))
        except Exception as e:
            herb_errors[hid]=repr(e)

ingredient_ids=sorted(ingredient_to_herbformulas)
print(f"PHASE1 herbs={sum(len(v) for v in HERBS.values())} unique_HBIN={len(ingredient_ids)} memberships={len(hi_edges)} herb_errors={len(herb_errors)}",flush=True)

# Phase 2: all unique HBIN ingredient details -> ingredient_target
def fetch_ingredient(iid):
    try:
        obj,ep,raw=api_detail(iid,"Ingredient")
        with gzip.open(RAW_I/f"{iid}_detail.json.gz","wb",compresslevel=6) as f:
            f.write(raw)
        rows=table_rows(obj.get("ingredient_target"))
        return iid,ep,rows,None
    except Exception as e:
        return iid,None,[],repr(e)

ingredient_results={}; ingredient_failures={}; source_ing={}
workers=int(__import__("os").environ.get("HERB_WORKERS","6"))
with ThreadPoolExecutor(max_workers=workers) as ex:
    futs={ex.submit(fetch_ingredient,iid):iid for iid in ingredient_ids}
    done=0
    for fut in as_completed(futs):
        iid,ep,rows,err=fut.result()
        done+=1
        if err is not None:
            ingredient_failures[iid]=err
        else:
            source_ing[iid]=ep
            ingredient_results[iid]=rows
        if done%100==0 or done==len(ingredient_ids):
            print(f"PHASE2 {done}/{len(ingredient_ids)} failed={len(ingredient_failures)}",flush=True)

# Phase 3: typed rows + full paths
it_edges=[]; paths=[]; zero_target_ingredients=[]
for iid in ingredient_ids:
    rows=ingredient_results.get(iid)
    if rows is None: continue
    if len(rows)==0:
        zero_target_ingredients.append(iid)
        continue
    owners=sorted(ingredient_to_herbformulas.get(iid,set()))
    for r in rows:
        tid=pick_id(r,"HBTAR"); gene=pick_gene(r)
        it_edges.append({"ingredient_id":iid,"target_id":tid,"gene_symbol":gene,**r})
        if not (tid or gene): continue
        for formula,hid in owners:
            paths.append({"formula":formula,"herb_id":hid,"ingredient_id":iid,"target_id":tid,"gene_symbol":gene})

summary=[]
for formula,ids in HERBS.items():
    fp=[r for r in paths if r["formula"]==formula]
    row={
      "formula":formula,
      "mapped_herbs":len(ids),
      "herbs_with_target_paths":len({r["herb_id"] for r in fp}),
      "unique_ingredients_on_target_paths":len({r["ingredient_id"] for r in fp}),
      "unique_HBTAR_targets":len({r["target_id"] for r in fp if r["target_id"]}),
      "unique_gene_symbols":len({r["gene_symbol"] for r in fp if r["gene_symbol"]}),
      "path_rows":len(fp)
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
write_tsv(OUT/"failed_ingredient_requests.tsv",[{"ingredient_id":k,"error":v} for k,v in sorted(ingredient_failures.items())])
(OUT/"zero_target_ingredients.txt").write_text("\n".join(zero_target_ingredients)+("\n" if zero_target_ingredients else ""),encoding="utf-8")

success_ing=len(ingredient_results)
completion=success_ing/len(ingredient_ids) if ingredient_ids else 0
primary_ready=(
    not herb_errors
    and not ingredient_failures
    and len(ingredient_ids)>0
    and all(x["unique_HBTAR_targets"]>=5 and x["herbs_with_target_paths"]>0 for x in summary)
)
qc={
 "herb_request_errors":herb_errors,
 "unique_HBIN_discovered":len(ingredient_ids),
 "herb_ingredient_memberships":len(hi_edges),
 "ingredient_detail_success":success_ing,
 "ingredient_detail_failures":len(ingredient_failures),
 "ingredient_completion_fraction":completion,
 "ingredients_with_legitimate_zero_target_rows":len(zero_target_ingredients),
 "ingredient_target_rows":len(it_edges),
 "formula_path_rows":len(paths),
 "summary":summary,
 "primary_ready":primary_ready,
 "primary_ready_rule":"requires zero herb request failures, zero ingredient request failures, and >=5 HBTAR targets per formula"
}
(OUT/"QC_report.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"run_manifest.json").write_text(json.dumps({
 "source":"HERB 2.0 live detail_api direct POST",
 "endpoints":DIRECT,
 "frozen_herbs":HERBS,
 "ingredient_request_count":len(ingredient_ids),
 "workers":workers,
 "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
},ensure_ascii=False,indent=2),encoding="utf-8")
print("FINAL_QC",json.dumps(qc,ensure_ascii=False),flush=True)
