#!/usr/bin/env python3
import pandas as pd, requests, networkx as nx, json
from pathlib import Path
BASE="https://raw.githubusercontent.com/Barabasi-Lab/COVID-19/main/data/"
out=Path("ppi_diag"); out.mkdir(exist_ok=True)
for fn in ["DatasetS2.csv","interactome_2019_merged_protAnnots.csv"]:
    r=requests.get(BASE+fn,timeout=180); r.raise_for_status(); (out/fn).write_bytes(r.content)
ppi=pd.read_csv(out/"DatasetS2.csv")
ann=pd.read_csv(out/"interactome_2019_merged_protAnnots.csv")
print("PPI columns",ppi.columns.tolist())
print("PPI shape",ppi.shape)
print(ppi.head().to_string())
print("ANN columns",ann.columns.tolist())
print("ANN shape",ann.shape)
print(ann.head().to_string())
# infer first two endpoint cols
cols=ppi.columns.tolist()
a,b=cols[0],cols[1]
edges=[]
nodes=set()
loops=0
for x,y in zip(ppi[a],ppi[b]):
    x=str(x).strip(); y=str(y).strip()
    if not x or not y or x=="nan" or y=="nan": continue
    nodes.update([x,y])
    if x==y: loops+=1
    else: edges.append((x,y))
G=nx.Graph(); G.add_edges_from(edges)
cc=max(nx.connected_components(G),key=len)
H=G.subgraph(cc).copy()
res={
 "ppi_shape":list(ppi.shape),"endpoint_cols":[a,b],
 "unique_nodes_all":len(nodes),"self_loop_rows":loops,
 "simple_graph_nodes_after_loop_removal":G.number_of_nodes(),
 "simple_graph_edges_after_loop_removal":G.number_of_edges(),
 "giant_nodes":H.number_of_nodes(),"giant_edges":H.number_of_edges(),
 "n_components":nx.number_connected_components(G)
}
(out/"ppi_diagnostic.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
print(json.dumps(res,indent=2))
