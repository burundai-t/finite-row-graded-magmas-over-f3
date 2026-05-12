#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'tables'
sys.path.insert(0, str(ROOT/'scripts'))
import h_core as hc

BLOCKS=['RRR','RRS','RSR','SRR','DIST']

def read_csv(path):
    with open(path,newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def main():
    frontier=read_csv(TABLES/'H_degree2_frontier_loci.csv')
    local_cache={}
    for r in frontier:
        local_cache.setdefault(r['x21'], hc.local_values(r['x21'])[2])

    sig=[]; hist=[]; detail=[]
    for locus in sorted({r['locus'] for r in frontier}):
        xs=[r['x21'] for r in frontier if r['locus']==locus]
        Hmat=[local_cache[x] for x in xs]
        for bidx,bname in enumerate(BLOCKS):
            idxs=[i for i,(b,t,a,e,f) in enumerate(hc.TERMS5) if hc.block_id(b,t)==bidx]
            byterm=[[H[i] for H in Hmat] for i in idxs]
            terms=len(idxs)
            always_pos=sum(all(v>0 for v in vs) for vs in byterm)
            always_zero=sum(all(v==0 for v in vs) for vs in byterm)
            always_neg=sum(all(v<0 for v in vs) for vs in byterm)
            sign_stable=always_pos+always_zero+always_neg
            value_stable=sum(len(set(vs))==1 for vs in byterm)
            pos_union=sum(any(v>0 for v in vs) for vs in byterm)
            zero_union=sum(any(v==0 for v in vs) for vs in byterm)
            neg_union=sum(any(v<0 for v in vs) for vs in byterm)
            per_point_scaled=[3*sum(H[i] for i in idxs) for H in Hmat]
            sig.append({
                'locus':locus,'block':bname,'points':len(xs),'terms':terms,
                'always_pos_terms':always_pos,'always_zero_terms':always_zero,'always_neg_terms':always_neg,
                'sign_stable_terms':sign_stable,'sign_variable_terms':terms-sign_stable,
                'value_stable_terms':value_stable,'value_variable_terms':terms-value_stable,
                'pos_union_terms':pos_union,'zero_union_terms':zero_union,'neg_union_terms':neg_union,
                'local_H_min':min(v for vs in byterm for v in vs),
                'local_H_max':max(v for vs in byterm for v in vs),
                'block_H_tot_per_point_min':min(per_point_scaled),
                'block_H_tot_per_point_max':max(per_point_scaled),
                'block_H_tot_per_point_mean_num':sum(per_point_scaled),
                'block_H_tot_per_point_mean_den':len(per_point_scaled),
                'aggregate_block_H_total_over_points':3*sum(sum(vs) for vs in byterm),
            })
            cnt=Counter(v for vs in byterm for v in vs)
            for val,count in sorted(cnt.items()):
                hist.append({'locus':locus,'block':bname,'local_H_value':val,'count':count})
            for i,vs in zip(idxs,byterm):
                b,t,a,e,f=hc.TERMS5[i]
                detail.append({
                    'locus':locus,'block':bname,'term_index':i,'b':b,'t':t,'a':a,'e':e,'f':f,
                    'values':';'.join(map(str,vs)),
                    'min':min(vs),'max':max(vs),'stable_value':str(len(set(vs))==1),
                    'sign_pattern':''.join('+' if v>0 else '-' if v<0 else '0' for v in vs),
                })

    write_csv(TABLES/'H_frontier_term_signature_summary.csv',sig,list(sig[0].keys()))
    write_csv(TABLES/'H_frontier_local_value_histogram.csv',hist,['locus','block','local_H_value','count'])
    write_csv(TABLES/'H_frontier_term_signature_detail.csv',detail,list(detail[0].keys()))

    # signed-class compression for frontier locus
    groups=defaultdict(list)
    for r in frontier:
        key=(r['locus'],r['Assoc'],r['I_tot'],r['B_tot'],r['H_tot'],r['H_pos'],r['H_neg_abs'],r['N_neg'],r['h_loc_min'],r['h_loc_max'],r['H_RRR'],r['H_RRS'],r['H_RSR'],r['H_SRR'],r['H_DIST'])
        groups[key].append(r)
    cls=[]
    for key,rs in sorted(groups.items()):
        locus,Assoc,I_tot,B_tot,H_tot,H_pos,H_neg_abs,N_neg,hmin,hmax,H_RRR,H_RRS,H_RSR,H_SRR,H_DIST=key
        cls.append({
            'locus':locus,'point_count':len(rs),'effective_orbit_count':len({r['canonical_x21'] for r in rs}),
            'Assoc':Assoc,'I_tot':I_tot,'B_tot':B_tot,'H_tot':H_tot,
            'H_pos':H_pos,'H_neg_abs':H_neg_abs,'N_neg':N_neg,'h_loc_min':hmin,'h_loc_max':hmax,
            'H_RRR':H_RRR,'H_RRS':H_RRS,'H_RSR':H_RSR,'H_SRR':H_SRR,'H_DIST':H_DIST,
            'representative_x21':sorted({r['x21'] for r in rs})[0],
        })
    write_csv(TABLES/'H_frontier_locus_class_summary.csv',cls,list(cls[0].keys()))
    print('H frontier term signatures: PASS')

if __name__=='__main__':
    main()
