#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'tables'
sys.path.insert(0, str(ROOT/'scripts'))
import h_core as hc

def read_csv(path):
    with open(path,newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def hamming_neighbors(x, radius):
    x=list(x); n=len(x)
    for idxs in combinations(range(n), radius):
        choices=[[c for c in '012' if c!=x[i]] for i in idxs]
        for repl in product(*choices):
            y=x[:]
            for i,c in zip(idxs,repl): y[i]=c
            yield ''.join(y)

def main():
    frontier=read_csv(TABLES/'H_degree2_frontier_loci.csv')
    hmin_assoc81=next(r['x21'] for r in frontier if r['locus']=='Hmin' and r['Assoc']=='81')
    hmin_assoc189=next(r['x21'] for r in frontier if r['locus']=='Hmin' and r['Assoc']=='189')
    hmax=next(r['x21'] for r in frontier if r['locus']=='Hmax')
    centers=[
        ('PAB','111111111222222222000'),
        ('row_complement','222222222111111111000'),
        ('affine_Hmin_assoc81_representative',hmin_assoc81),
        ('affine_Hmin_assoc189_representative',hmin_assoc189),
        ('degree2_Hmax_representative',hmax),
        ('global_Assoc_min_representative','210210210001021001100'),
        ('global_Assoc_max_representative','110001110011100011111'),
    ]
    cache={}
    def metrics(x):
        if x not in cache:
            m=hc.h_metrics(x); m['Assoc']=hc.assoc_tot(x); cache[x]=m
        return cache[x]

    center_rows=[]; summary=[]; hist=[]; examples=[]
    for label,x in centers:
        m=metrics(x)
        center={'center':label,'x21':x,'Assoc':m['Assoc']}
        for k in ['I_tot','B_tot','H_tot','H_pos','H_neg_abs','N_neg','h_loc_min','h_loc_max','H_RRR','H_RRS','H_RSR','H_SRR','H_DIST']:
            center[k]=m[k]
        center_rows.append(center)
        center_H=m['H_tot']
        for radius in (1,2):
            rows=[(y,metrics(y)) for y in hamming_neighbors(x,radius)]
            H=[m2['H_tot'] for _,m2 in rows]
            A=[m2['Assoc'] for _,m2 in rows]
            N=[m2['N_neg'] for _,m2 in rows]
            for val,count in sorted(Counter(H).items()):
                hist.append({'center':label,'radius':radius,'H_tot':val,'count':count})
            for kind,target in [('min',min(H)),('max',max(H))]:
                y,m2=next((y,m2) for y,m2 in rows if m2['H_tot']==target)
                examples.append({
                    'center':label,'radius':radius,'kind':kind,'x21':y,'Assoc':m2['Assoc'],
                    'H_tot':m2['H_tot'],'I_tot':m2['I_tot'],'B_tot':m2['B_tot'],
                    'H_pos':m2['H_pos'],'H_neg_abs':m2['H_neg_abs'],'N_neg':m2['N_neg'],
                    'h_loc_min':m2['h_loc_min'],'h_loc_max':m2['h_loc_max'],
                })
            summary.append({
                'center':label,'radius':radius,'center_H_tot':center_H,'neighbors':len(rows),
                'min_H_tot':min(H),'mean_H_tot_num':sum(H),'mean_H_tot_den':len(H),'max_H_tot':max(H),
                'below_center':sum(1 for h in H if h<center_H),
                'equal_center':sum(1 for h in H if h==center_H),
                'above_center':sum(1 for h in H if h>center_H),
                'min_Assoc':min(A),'max_Assoc':max(A),'min_N_neg':min(N),'max_N_neg':max(N),
                'pure_neighbors':sum(1 for n in N if n==0),
            })
    write_csv(TABLES/'H_center_profiles.csv',center_rows,list(center_rows[0].keys()))
    write_csv(TABLES/'H_local_shell_summary.csv',summary,list(summary[0].keys()))
    write_csv(TABLES/'H_local_shell_H_histogram.csv',hist,['center','radius','H_tot','count'])
    write_csv(TABLES/'H_local_shell_extreme_examples.csv',examples,list(examples[0].keys()))
    print('H local shells: PASS')

if __name__=='__main__':
    main()
