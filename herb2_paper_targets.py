#!/usr/bin/env python3
import csv,json,time,hashlib
from pathlib import Path
import requests
HERBS={
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
ENDPOINTS=["http://herb.ac.cn/chedi/api/","http://47.92.70.12/chedi/api/"]
OUT=Path("herb2_paper_targets"); OUT.mkdir(exist_ok=True)
def call(hid):
 p={"func_name":"detail_api","key_id":hid,"label":"Herb","v":hid}; es=[]
 for ep in ENDPOINTS:
  try:
   r=requests.post(ep,json=p,timeout=60,headers={"User-Agent":"HERB2-CP-paper/1.0","Content-Type":"application/json","Accept":"*/*"})
   if r.status_code!=200: es.append(f"{ep} HTTP {r.status_code}"); continue
   return ep,r.json()
  except Exception as e: es.append(repr(e))
 raise RuntimeError(" ; ".join(es))
def unwrap(v):
 if isinstance(v,list): return [unwrap(x) for x in v]
 if isinstance(v,dict) and "title" in v:
  t=v["title"]; return " ".join(map(str,t)) if isinstance(t,list) else t
 return v
def rows(tab):
 if not isinstance(tab,list) or not tab:return []
 h=[str(unwrap(x)) for x in tab[0]]
 return [{k:unwrap(r[i]) if i<len(r) else None for i,k in enumerate(h)} for r in tab[1:] if isinstance(r,list)]
def pick(r,prefix):
 for v in r.values():
  vals=v if isinstance(v,list) else [v]
  for x in vals:
   if isinstance(x,str) and x.startswith(prefix): return x
 return ""
def pick_gene(r):
 for k,v in r.items():
  kl=k.lower().replace(" ","_")
  if isinstance(v,str) and (kl in {"gene","gene_name","gene_symbol","target_name","target"} or ("target" in kl and "id" not in kl)):
   if v and not v.startswith("HBTAR"): return v
 return ""
def grade(r):
 for k,v in r.items():
  kl=k.lower().replace(" ","_")
  if "grade" in kl or "evidence_level" in kl:
   return str(v)
 return ""
allr=[]; errors={}; summary=[]
for f,ids in HERBS.items():
 for hid in ids:
  try:
   ep,obj=call(hid)
   rr=rows(obj.get("drug_paper_target"))
   for r in rr:
    allr.append({"formula":f,"herb_id":hid,"target_id":pick(r,"HBTAR"),"gene_symbol":pick_gene(r),"native_grade":grade(r),"source_endpoint":ep,**{f"upstream__{k}":v for k,v in r.items()}})
  except Exception as e: errors[hid]=repr(e)
for f,ids in HERBS.items():
 rr=[r for r in allr if r["formula"]==f]
 summary.append({"formula":f,"paper_edges":len(rr),"herbs_with_edges":len({r["herb_id"] for r in rr}),"unique_targets":len({r["target_id"] for r in rr if r["target_id"]}),"unique_genes":len({r["gene_symbol"] for r in rr if r["gene_symbol"]}),"grades":sorted({r["native_grade"] for r in rr if r["native_grade"]})})
fields=[]
for r in allr:
 for k in r:
  if k not in fields:fields.append(k)
with (OUT/"paper_target_edges.tsv").open("w",encoding="utf-8",newline="") as fh:
 w=csv.DictWriter(fh,fieldnames=fields,delimiter="\t");w.writeheader()
 for r in allr:w.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in r.items()})
(OUT/"QC_report.json").write_text(json.dumps({"errors":errors,"summary":summary},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"errors":errors,"summary":summary},ensure_ascii=False,indent=2))
