#!/usr/bin/env python3
import csv, json, time, hashlib, gzip, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

HERBS = {
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
ENDPOINTS=["http://herb.ac.cn/chedi/api/","http://47.92.70.12/chedi/api/"]
OUT=Path("herb2_output")
RAW=OUT/"raw"
RAW.mkdir(parents=True,exist_ok=True)

def sha256(b): return hashlib.sha256(b).hexdigest()

def post_detail(entity_id,label,timeout=30):
    payload={"func_name":"detail_api","key_id":entity_id,"label":label,"v":entity_id}
    errs=[]
    for endpoint in ENDPOINTS:
        try:
            root=endpoint.split("/chedi")[0]
            r=requests.post(
                endpoint,json=payload,timeout=timeout,
                headers={
                    "User-Agent":"HERB2-CP-GHA/3.0",
                    "Accept":"*/*",
                    "Content-Type":"application/json",
                    "Origin":root,
                    "Referer":root+f"/Detail/?v={entity_id}&label={label}",
                }
            )
            raw=r.content
            if r.status_code!=200:
                errs.append(f"{endpoint} -> HTTP {r.status_code}: {raw[:160]!r}")
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
    hdr0=table[0] if isinstance(table[0],list) else []
    hdr=[str(unwrap(x)) for x in hdr0]
    rows=[]
    for row in table[1:]:
        if not isinstance(row,list): continue
        rows.append({h:unwrap(row[i]) if i<len(row) else None for i,h in enumerate(hdr)})
    return rows

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
        if isinstance(v,str):
            if kl in {"gene","gene_name","gene_symbol","target_name","target"}:
                preferred.append(v)
            elif "gene" in kl and "id" not in kl:
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
            rr={k:(json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()}
            w.writerow(rr)

# -------- Phase 1: all 26 herbs -> herb_ingredient --------
herb_edges=[]
herb_errors={}
herbs_zero_ingredient=[]
herb_manifest=[]
for formula,ids in HERBS.items():
    for hid in ids:
        try:
            endpoint,obj,raw,payload=post_detail(hid,"Herb",timeout=45)
            raw_table=obj.get("herb_ingredient")
            rows=table_to_rows(raw_table)
            herb_manifest.append({
                "formula":formula,"herb_id":hid,"endpoint":endpoint,
                "full_response_sha256":sha256(raw),
                "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                "row_count":len(rows)
            })
            if not rows:
                herbs_zero_ingredient.append(hid)
            for r in rows:
                iid=pick_id(r,"HBIN")
                herb_edges.append({
                    "formula":formula,"herb_id":hid,"ingredient_id":iid,
                    "source_endpoint":endpoint,
                    **{f"upstream__{k}":v for k,v in r.items()}
                })
        except Exception as e:
            herb_errors[hid]=repr(e)

unique_ingredients=sorted({r["ingredient_id"] for r in herb_edges if r["ingredient_id"]})
print(f"PHASE1 herbs={sum(map(len,HERBS.values()))} edges={len(herb_edges)} unique_HBIN={len(unique_ingredients)} herb_errors={len(herb_errors)}",flush=True)

# -------- Phase 2: each unique HBIN -> ingredient_target --------
ingredient_errors={}
ingredient_status=[]
ingredient_target_edges=[]
raw_relation_path=RAW/"ingredient_target_raw_tables.jsonl.gz"
lock=threading.Lock()
done_count=0

def fetch_ingredient(iid):
    last=None
    for attempt in range(1,4):
        try:
            endpoint,obj,raw,payload=post_detail(iid,"Ingredient",timeout=35)
            raw_table=obj.get("ingredient_target")
            rows=table_to_rows(raw_table)
            return {
                "ok":True,"ingredient_id":iid,"endpoint":endpoint,
                "raw_table":raw_table,"rows":rows,"sha256":sha256(raw),
                "attempt":attempt,
                "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
            }
        except Exception as e:
            last=repr(e)
            time.sleep(min(2**attempt,8))
    return {"ok":False,"ingredient_id":iid,"error":last}

with gzip.open(raw_relation_path,"wt",encoding="utf-8") as rawout:
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(fetch_ingredient,iid):iid for iid in unique_ingredients}
        for fut in as_completed(futs):
            res=fut.result()
            iid=res["ingredient_id"]
            done_count+=1
            if not res["ok"]:
                ingredient_errors[iid]=res["error"]
            else:
                rows=res["rows"]
                ingredient_status.append({
                    "ingredient_id":iid,"row_count":len(rows),
                    "endpoint":res["endpoint"],"attempt":res["attempt"],
                    "full_response_sha256":res["sha256"],
                    "retrieved_utc":res["retrieved_utc"]
                })
                rawout.write(json.dumps({
                    "ingredient_id":iid,
                    "endpoint":res["endpoint"],
                    "retrieved_utc":res["retrieved_utc"],
                    "full_response_sha256":res["sha256"],
                    "ingredient_target_raw_table":res["raw_table"]
                },ensure_ascii=False,separators=(",",":"))+"\n")
                for r in rows:
                    tid=pick_id(r,"HBTAR")
                    gene=pick_gene(r)
                    ingredient_target_edges.append({
                        "ingredient_id":iid,
                        "target_id":tid,
                        "gene_symbol":gene,
                        "source_endpoint":res["endpoint"],
                        "full_response_sha256":res["sha256"],
                        "evidence_class":"HERB ingredient_target database cross-reference / computational association",
                        **{f"upstream__{k}":v for k,v in r.items()}
                    })
            if done_count%100==0 or done_count==len(unique_ingredients):
                print(f"PHASE2 {done_count}/{len(unique_ingredients)} ok={done_count-len(ingredient_errors)} errors={len(ingredient_errors)} edges={len(ingredient_target_edges)}",flush=True)

# -------- Join formula -> herb -> ingredient -> target --------
by_iid={}
for r in ingredient_target_edges:
    by_iid.setdefault(r["ingredient_id"],[]).append(r)

paths=[]
for hi in herb_edges:
    iid=hi["ingredient_id"]
    for it in by_iid.get(iid,[]):
        paths.append({
            "formula":hi["formula"],
            "herb_id":hi["herb_id"],
            "ingredient_id":iid,
            "target_id":it["target_id"],
            "gene_symbol":it["gene_symbol"],
            "evidence_class":it["evidence_class"]
        })

summary=[]
for formula,ids in HERBS.items():
    fpaths=[r for r in paths if r["formula"]==formula]
    fherb_edges=[r for r in herb_edges if r["formula"]==formula]
    ing_all={r["ingredient_id"] for r in fherb_edges if r["ingredient_id"]}
    ing_targeted={r["ingredient_id"] for r in fpaths if r["ingredient_id"]}
    targets={r["target_id"] for r in fpaths if r["target_id"]}
    genes={r["gene_symbol"] for r in fpaths if r["gene_symbol"]}
    herbs_targeted={r["herb_id"] for r in fpaths}
    summary.append({
        "formula":formula,
        "mapped_herbs":len(ids),
        "herbs_with_ingredients":len({r["herb_id"] for r in fherb_edges}),
        "herbs_with_target_paths":len(herbs_targeted),
        "unique_ingredients":len(ing_all),
        "target_bearing_ingredients":len(ing_targeted),
        "unique_targets":len(targets),
        "unique_genes":len(genes),
        "paths":len(fpaths)
    })
    (OUT/f"{formula}_HBTAR.txt").write_text("\n".join(sorted(targets))+("\n" if targets else ""),encoding="utf-8")
    (OUT/f"{formula}_genes.txt").write_text("\n".join(sorted(genes))+("\n" if genes else ""),encoding="utf-8")

write_tsv(OUT/"herb_ingredient_edges.tsv",herb_edges)
write_tsv(OUT/"ingredient_target_edges.tsv",ingredient_target_edges)
write_tsv(OUT/"ingredient_status.tsv",ingredient_status)
write_tsv(OUT/"formula_paths.tsv",paths)
write_tsv(OUT/"formula_summary.tsv",summary)

zero_target_ingredients=sorted({r["ingredient_id"] for r in ingredient_status if int(r["row_count"])==0})
qc={
    "phase1":{
        "herb_count_expected":26,
        "herb_errors":herb_errors,
        "herbs_zero_ingredient":herbs_zero_ingredient,
        "herb_ingredient_edges":len(herb_edges),
        "unique_ingredients":len(unique_ingredients)
    },
    "phase2":{
        "ingredient_queries_expected":len(unique_ingredients),
        "ingredient_queries_completed":len(ingredient_status)+len(ingredient_errors),
        "ingredient_errors":ingredient_errors,
        "ingredients_with_zero_target_rows":zero_target_ingredients,
        "ingredient_target_edges":len(ingredient_target_edges)
    },
    "formula_summary":summary,
    "primary_ready":(
        not herb_errors
        and not herbs_zero_ingredient
        and not ingredient_errors
        and all(x["unique_targets"]>=5 for x in summary)
    )
}
(OUT/"QC_report.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
manifest={
    "source":"HERB 2.0 live detail_api",
    "endpoints":ENDPOINTS,
    "frozen_herbs":HERBS,
    "phase1_manifest":herb_manifest,
    "phase2_raw_relation_file":"raw/ingredient_target_raw_tables.jsonl.gz",
    "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
    "policy":{
        "primary_chain":"formula -> herb -> herb_ingredient -> ingredient -> ingredient_target -> target",
        "herb_target_used":False,
        "ADME_filtering":False,
        "NMT_unmapped_components":["四季红/头花蓼","芙蓉叶"],
        "BSDZG_sensitivity_only_alternative":"HERB005030"
    }
}
(OUT/"run_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(qc,ensure_ascii=False,indent=2),flush=True)
