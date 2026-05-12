#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv, sys
from itertools import product
from pathlib import Path
import numpy as np
from h_generate_controlled_atlas_batch import METRIC_FIELDS, all_params, affine_table, build_M, batch_metrics, batch_assoc, x21_from_parts
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated'; OUT.mkdir(exist_ok=True)
def main():
    d=sys.argv[1]
    params=all_params(); tabs=np.stack([affine_table(p) for p in params]); pairs=list(product(range(27),range(27)))
    A_batch=np.stack([tabs[i] for i,j in pairs]); B_batch=np.stack([tabs[j] for i,j in pairs])
    M=build_M(A_batch,B_batch,d); mets=batch_metrics(M); ass=batch_assoc(M)
    fields=['stratum','A_param','B_param','d','x21','Assoc']+METRIC_FIELDS
    with open(OUT/f'affine_chunk_{d}.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for (i,j),A,B,m,assoc in zip(pairs,A_batch,B_batch,mets,ass):
            pa=''.join(map(str,params[i])); pb=''.join(map(str,params[j])); x=x21_from_parts(A.tolist(),B.tolist(),[int(c) for c in d]); r={'stratum':'affine','A_param':pa,'B_param':pb,'d':d,'x21':x,'Assoc':assoc}; r.update(m); w.writerow(r)
    print('done',d)
if __name__=='__main__': main()
