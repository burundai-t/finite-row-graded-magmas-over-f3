#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv
from pathlib import Path
from h_core import METRIC_FIELDS, h_metrics, assoc_tot, tau_x21, canonical_x21, column_blind_x21
ROOT=Path(__file__).resolve().parents[1]; TABLES=ROOT/'tables'
def read(name):
    with open(TABLES/name,newline='') as f: return list(csv.DictReader(f))
def write(name, rows, fields):
    with open(TABLES/name,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def summary(name, rows):
    H=[int(r['H_tot']) for r in rows]; pure=[r for r in rows if int(r['N_neg'])==0]
    return {'stratum':name,'points':len(rows),'H_min':min(H),'H_max':max(H),'H_mean_num':sum(H),'H_mean_den':len(H),'pure_count':len(pure),'pure_H_max':max(int(r['H_tot']) for r in pure),'N_neg_max':max(int(r['N_neg']) for r in rows),'count_above_PAB_7020':sum(1 for h in H if h>7020),'count_ge_PAB_7020':sum(1 for h in H if h>=7020)}
def row_for_x(label,x,byx):
    if x in byx:
        b=byx[x]; r={'label':label,'x21':x,'tau_x21':tau_x21(x),'canonical_x21':canonical_x21(x),'Assoc':b['Assoc']}; r.update({k:b[k] for k in METRIC_FIELDS}); return r
    m=h_metrics(x); r={'label':label,'x21':x,'tau_x21':tau_x21(x),'canonical_x21':canonical_x21(x),'Assoc':assoc_tot(x)}; r.update(m); return r
def main():
    cb=read('H_column_blind_all_diags.csv'); aff=read('H_affine_all_diags.csv')
    write('H_controlled_summary.csv',[summary('column_blind_x_Delta',cb),summary('affine_x_Delta',aff)],['stratum','points','H_min','H_max','H_mean_num','H_mean_den','pure_count','pure_H_max','N_neg_max','count_above_PAB_7020','count_ge_PAB_7020'])
    byx={r['x21']:r for r in aff+cb}
    keys=[('PAB',column_blind_x21(1,2,'000')),('row_complement',column_blind_x21(2,1,'000')),('global_Assoc_min_representative','210210210001021001100'),('global_Assoc_max_representative','110001110011100011111'),('column_blind_Hmax_example',column_blind_x21(0,1,'220'))]
    for label,H,pure in [('affine_Hmin_first',-2268,False),('affine_Hmax_first',7302,False),('affine_pure_frontier_first',7020,True)]:
        for r in aff:
            if int(r['H_tot'])==H and (not pure or int(r['N_neg'])==0): keys.append((label,r['x21'])); break
    write('H_key_witnesses.csv',[row_for_x(label,x,byx) for label,x in keys],['label','x21','tau_x21','canonical_x21','Assoc']+METRIC_FIELDS)
    frontier=[]
    for source,rows in [('affine',aff),('column_blind',cb)]:
        for r in rows:
            H=int(r['H_tot']); n=int(r['N_neg'])
            if H in (7302,-2268) or (H==7020 and n==0):
                locus='Hmax_7302' if H==7302 else 'Hmin_minus2268' if H==-2268 else 'pure_frontier_7020'
                out={'source':source,'locus':locus,'stratum':r.get('stratum',''),'rule':r.get('rule',''),'a':r.get('a',''),'b':r.get('b',''),'A_param':r.get('A_param',''),'B_param':r.get('B_param',''),'d':r['d'],'x21':r['x21'],'tau_x21':tau_x21(r['x21']),'canonical_x21':canonical_x21(r['x21']),'Assoc':r['Assoc']}; out.update({k:r[k] for k in METRIC_FIELDS}); frontier.append(out)
    bx={}
    for r in frontier: bx.setdefault(r['x21'],r)
    frontier=list(bx.values())
    write('H_frontier_loci.csv',frontier,['source','locus','stratum','rule','a','b','A_param','B_param','d','x21','tau_x21','canonical_x21','Assoc']+METRIC_FIELDS)
    groups={}
    for r in frontier: groups[(r['locus'],r['canonical_x21'])]=r
    orbits=[]
    for (locus,canon),r in sorted(groups.items()):
        mem=sorted(set([r['x21'],tau_x21(r['x21'])])); orbits.append({'locus':locus,'canonical_x21':canon,'orbit_members':';'.join(mem),'orbit_size_effective_S3':len(mem),'tau_fixed':str(len(mem)==1),'representative_x21':mem[0],'H_tot':r['H_tot'],'I_tot':r['I_tot'],'B_tot':r['B_tot'],'H_pos':r['H_pos'],'H_neg_abs':r['H_neg_abs'],'N_neg':r['N_neg']})
    write('H_frontier_orbits.csv',orbits,['locus','canonical_x21','orbit_members','orbit_size_effective_S3','tau_fixed','representative_x21','H_tot','I_tot','B_tot','H_pos','H_neg_abs','N_neg'])
    print('Layer1H postprocess PASS')
if __name__=='__main__': main()
