#!/usr/bin/env python3
import csv,json,requests
from pathlib import Path
HERBS={
"GHF":["HERB001210","HERB002483","HERB002962","HERB002840","HERB004719","HERB004004","HERB000305","HERB000767","HERB000208","HERB000775"],
"NMT":["HERB000242","HERB004538","HERB004773","HERB005977","HERB003361"],
"BSDZG":["HERB005251","HERB000439","HERB005762","HERB000770","HERB006572","HERB005767","HERB004050","HERB000164","HERB003636","HERB005206","HERB005637"],
}
EPS=["http://herb.ac.cn/chedi/api/","http://47.92.70.12/chedi/api/"]
OUT=Path("herb2_inferred_targets");OUT.mkdir(exist_ok=True)
def call(hid):
 p={"func_name":"detail_api","key_id":hid,"label":"Herb","v":hid};es=[]
 for ep in EPS:
  try:
   r=requests.post(ep,json=p,timeout=60,headers={"User-Agent":"HERB2-CP-inferred/1.0","Content-Type":"application/json"})
   if r.status_code==200:return ep,r.json()
   es.append(f"{ep} HTTP {r.status_code}")
  except Exception as e:es.append(repr(e))
 raise RuntimeError(" ; ".join(es))
def u(v):
 if isinstance(v,list):return [u(x) for x in v]
 if isinstance(v,dict) and "title" in v:
  t=v["title"];return " ".join(map(str,t)) if isinstance(t,list) else t
 return v
def rows(t):
 if not isinstance(t,list) or not t:return []
 h=[str(u(x)) for x in t[0]]
 return [{k:u(r[i]) if i<len(r) else None for i,k in enumerate(h)} for r in t[1:] if isinstance(r,list)]
def pick(r,pfx):
 for v in r.values():
  for x in (v if isinstance(v,list) else [v]):
   if isinstance(x,str) and x.startswith(pfx):return x
 return ""
def gene(r):
 for k,v in r.items():
  kl=k.lower().replace(" ","_")
  if isinstance(v,str) and (kl in {"gene","gene_name","gene_symbol","target_name","target"} or ("target" in kl and "id" not in kl)):
   if v and not v.startswith("HBTAR"):return v
 return ""
def fdr(r):
 for k,v in r.items():
  kl=k.lower().replace(" ","_")
  if "fdr" in kl or ("adjust" in kl and "p" in kl):
   try:return float(v)
   except:pass
 return None
allr=[];errs={}
for f,ids in HERBS.items():
 for hid in ids:
  try:
   ep,o=call(hid)
   for r in rows(o.get("herb_target")):
    fd=fdr(r)
    allr.append({"formula":f,"herb_id":hid,"target_id":pick(r,"HBTAR"),"gene_symbol":gene(r),"fdr":fd,"source_endpoint":ep,**{f"upstream__{k}":v for k,v in r.items()}})
  except Exception as e:errs[hid]=repr(e)
flt=[r for r in allr if r["fdr"] is not None and r["fdr"]<0.01]
fields=[]
for r in allr:
 for k in r:
  if k not in fields:fields.append(k)
for name,data in [("all_herb_target.tsv",allr),("FDRlt0.01_herb_target.tsv",flt)]:
 with (OUT/name).open("w",encoding="utf-8",newline="") as fh:
  w=csv.DictWriter(fh,fieldnames=fields,delimiter="\t");w.writeheader()
  for r in data:w.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in r.items()})
summary=[]
for f in HERBS:
 rr=[r for r in flt if r["formula"]==f]
 summary.append({"formula":f,"FDRlt0.01_edges":len(rr),"herbs_with_edges":len({r["herb_id"] for r in rr}),"unique_targets":len({r["target_id"] for r in rr if r["target_id"]}),"unique_genes":len({r["gene_symbol"] for r in rr if r["gene_symbol"]})})
(OUT/"QC_report.json").write_text(json.dumps({"errors":errs,"summary":summary},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"errors":errs,"summary":summary},ensure_ascii=False,indent=2))
