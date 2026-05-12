#!/usr/bin/env python3
from __future__ import annotations
import csv, os, sys
from itertools import product
from pathlib import Path
import numpy as np
S=(0,1,2); ROOT=Path(__file__).resolve().parents[1]; TABLES=ROOT/'tables'; TABLES.mkdir(exist_ok=True)
METRIC_FIELDS=['rawI','rawB','rawH','I_tot','B_tot','H_tot','H_pos','H_neg_abs','N_neg','h_loc_min','h_loc_max','H_RRR','H_RRS','H_RSR','H_SRR','H_DIST']
V7=np.array(list(product(S, repeat=7)), dtype=np.int16); b7,t7,u7,a7,e7,f7,l7=[V7[:,i] for i in range(7)]
V5=np.array(list(product(S, repeat=5)), dtype=np.int16); b5,t5,a5,e5,f5=[V5[:,i] for i in range(5)]
block5=np.array([0 if b==0 and t==0 else 1 if b==0 else 2 if t==0 else 3 if t==b else 4 for b,t,a,e,f in V5]); MASKS=[block5==k for k in range(5)]
def comp(a,e): return (-a-e)%3
def x21_from_parts(A,B,d): return ''.join(str(int(v)%3) for v in list(A)+list(B)+list(d))
def affine_table(p):
    A,B,C=p; return np.array([((A*a+B*e+C)%3) for a,e in product(S,S)], dtype=np.int16)
def build_M(A_batch,B_batch,d):
    N=A_batch.shape[0]; M=np.zeros((N,3,3,3),dtype=np.int16); D=np.array([int(c) for c in d],dtype=np.int16)
    for a,e in product(S,S): M[:,0,a,e]=D[a] if a==e else comp(a,e); M[:,1,a,e]=A_batch[:,3*a+e]; M[:,2,a,e]=B_batch[:,3*a+e]
    return M
def batch_metrics(M):
    N=M.shape[0]; nidx=np.arange(N)[:,None]
    xy=M[:,b7,a7,e7]; zw_abs=(t7[None,:]+M[:,(u7-t7)%3,(f7-t7)%3,(l7-t7)%3])%3; leftI=M[nidx,t7[None,:],xy,zw_abs]
    yz=M[:,(t7-b7)%3,(e7-b7)%3,(f7-b7)%3]; yzw_abs=(b7[None,:]+M[nidx,(u7-b7)[None,:]%3,yz,(l7-b7)[None,:]%3])%3; rightI=M[nidx,b7[None,:],a7[None,:],yzw_abs]
    epL=M[nidx,t7[None,:],xy,f7[None,:]]; epR=M[nidx,b7[None,:],a7[None,:],(b7[None,:]+yz)%3]; leftB=M[nidx,u7[None,:],epL,l7[None,:]]; rightB=M[nidx,u7[None,:],epR,l7[None,:]]
    Imis=(leftI!=rightI).reshape(N,3,3,3,3,3,3,3).transpose(0,1,2,4,5,6,3,7).reshape(N,243,9); Bmis=(leftB!=rightB).reshape(N,3,3,3,3,3,3,3).transpose(0,1,2,4,5,6,3,7).reshape(N,243,9)
    Iloc=2*Imis.sum(axis=2); Bloc=2*Bmis.sum(axis=2); Hloc=Iloc-Bloc; rawI=(Iloc.sum(axis=1)//2).astype(int); rawB=(Bloc.sum(axis=1)//2).astype(int); rawH=rawI-rawB
    out=[]
    for i,H in enumerate(Hloc):
        blocks=[int(3*H[m].sum()) for m in MASKS]
        out.append({'rawI':int(rawI[i]),'rawB':int(rawB[i]),'rawH':int(rawH[i]),'I_tot':int(6*rawI[i]),'B_tot':int(6*rawB[i]),'H_tot':int(6*rawH[i]),'H_pos':int(3*H[H>0].sum()),'H_neg_abs':int(3*(-H[H<0]).sum()),'N_neg':int(3*np.count_nonzero(H<0)),'h_loc_min':int(H.min()),'h_loc_max':int(H.max()),'H_RRR':blocks[0],'H_RRS':blocks[1],'H_RSR':blocks[2],'H_SRR':blocks[3],'H_DIST':blocks[4]})
    return out
def batch_assoc(M):
    N=M.shape[0]; nidx=np.arange(N)[:,None]; lhs=M[nidx,t5[None,:],M[:,b5,a5,e5],f5[None,:]]; yz=M[:,(t5-b5)%3,(e5-b5)%3,(f5-b5)%3]; rhs=M[nidx,b5[None,:],a5[None,:],(b5[None,:]+yz)%3]
    return (3*np.count_nonzero(lhs==rhs,axis=1)).astype(int).tolist()
def tau_x21(x):
    vals=[int(c) for c in x]; y=[0]*21
    def idx(a,b,e): a%=3; b%=3; e%=3; return 3*a+e if b==1 else 9+3*a+e
    for a,e in product(S,S): y[idx(-a,2,-e)]=(-vals[idx(a,1,e)])%3; y[idx(-a,1,-e)]=(-vals[idx(a,2,e)])%3
    y[18]=(-vals[18])%3; y[19]=(-vals[20])%3; y[20]=(-vals[19])%3; return ''.join(map(str,y))
def canonical_x21(x): return min(x,tau_x21(x))
def write_csv(path,rows,fields):
    with open(path,'w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def all_diags(): return [''.join(map(str,d)) for d in product(S, repeat=3)]
def all_params(): return list(product(S, repeat=3))
def main():
    print('Generating Layer1H tables...', flush=True)
    # standard six
    tabs=[]; d0='000'
    A1=np.array([1]*9); B1=np.array([2]*9); tabs.append(('g1_PAB',A1,B1))
    A2=np.array([e for a,e in product(S,S)]); tabs.append(('g2_transparent',A2,A2.copy()))
    A3=np.array([a if a==e else comp(a,e) for a,e in product(S,S)]); tabs.append(('g3_su2_transparent',A3,A3.copy()))
    A4=np.array([a for a,e in product(S,S)]); tabs.append(('g4_echo',A4,A4.copy()))
    A5=np.array([0]*9); tabs.append(('g5_self_referential',A5,A5.copy()))
    A6=np.array([1 if e==1 else comp(1,e) for a,e in product(S,S)]); B6=np.array([2 if e==2 else comp(2,e) for a,e in product(S,S)]); tabs.append(('g6_anti_complement',A6,B6))
    M=build_M(np.stack([t[1] for t in tabs]),np.stack([t[2] for t in tabs]),d0); mets=batch_metrics(M); ass=batch_assoc(M); rows=[]
    for (label,A,B),m,a in zip(tabs,mets,ass): r={'label':label,'x21':x21_from_parts(A.tolist(),B.tolist(),[0,0,0]),'Assoc':a}; r.update(m); rows.append(r)
    write_csv(TABLES/'H_standard_six.csv',rows,['label','x21','Assoc']+METRIC_FIELDS)
    # column-blind
    cb=[]
    for d in all_diags():
        pairs=list(product(S,S)); A_batch=np.stack([np.array([a]*9,dtype=np.int16) for a,b in pairs]); B_batch=np.stack([np.array([b]*9,dtype=np.int16) for a,b in pairs]); M=build_M(A_batch,B_batch,d); mets=batch_metrics(M); ass=batch_assoc(M)
        for (a,b),A,B,m,assoc in zip(pairs,A_batch,B_batch,mets,ass): r={'stratum':'column_blind','rule':f'cb_{a}{b}','a':a,'b':b,'d':d,'x21':x21_from_parts(A.tolist(),B.tolist(),[int(c) for c in d]),'Assoc':assoc}; r.update(m); cb.append(r)
    write_csv(TABLES/'H_column_blind_all_diags.csv',cb,['stratum','rule','a','b','d','x21','Assoc']+METRIC_FIELDS)
    # affine
    params=all_params(); tabarr=np.stack([affine_table(p) for p in params]); pairs=list(product(range(27),range(27))); aff=[]
    for d in all_diags():
        A_batch=np.stack([tabarr[i] for i,j in pairs]); B_batch=np.stack([tabarr[j] for i,j in pairs]); M=build_M(A_batch,B_batch,d); mets=batch_metrics(M); ass=batch_assoc(M)
        for (i,j),A,B,m,assoc in zip(pairs,A_batch,B_batch,mets,ass):
            pa=''.join(map(str,params[i])); pb=''.join(map(str,params[j])); r={'stratum':'affine','A_param':pa,'B_param':pb,'d':d,'x21':x21_from_parts(A.tolist(),B.tolist(),[int(c) for c in d]),'Assoc':assoc}; r.update(m); aff.append(r)
        print('  d',d,'done', flush=True)
    write_csv(TABLES/'H_affine_all_diags.csv',aff,['stratum','A_param','B_param','d','x21','Assoc']+METRIC_FIELDS)
    def summary(name,rows):
        H=[int(r['H_tot']) for r in rows]; pure=[r for r in rows if int(r['N_neg'])==0]
        return {'stratum':name,'points':len(rows),'H_min':min(H),'H_max':max(H),'H_mean_num':sum(H),'H_mean_den':len(H),'pure_count':len(pure),'pure_H_max':max(int(r['H_tot']) for r in pure),'N_neg_max':max(int(r['N_neg']) for r in rows),'count_above_PAB_7020':sum(1 for h in H if h>7020),'count_ge_PAB_7020':sum(1 for h in H if h>=7020)}
    write_csv(TABLES/'H_controlled_summary.csv',[summary('column_blind_x_Delta',cb),summary('affine_x_Delta',aff)],['stratum','points','H_min','H_max','H_mean_num','H_mean_den','pure_count','pure_H_max','N_neg_max','count_above_PAB_7020','count_ge_PAB_7020'])
    # key witnesses and frontiers
    byx={r['x21']:r for r in aff+cb}
    keys=[('PAB','111111111222222222000'),('row_complement','222222222111111111000'),('global_Assoc_min_representative','210210210001021001100'),('global_Assoc_max_representative','110001110011100011111'),('column_blind_Hmax_example','000000000111111111220')]
    for label,H,pure in [('affine_Hmin_first',-2268,False),('affine_Hmax_first',7302,False),('affine_pure_frontier_first',7020,True)]:
        for r in aff:
            if int(r['H_tot'])==H and (not pure or int(r['N_neg'])==0): keys.append((label,r['x21'])); break
    keyrows=[]
    for label,x in keys:
        if x in byx: base=byx[x]; r={'label':label,'x21':x,'tau_x21':tau_x21(x),'canonical_x21':canonical_x21(x),'Assoc':base['Assoc']}; r.update({k:base[k] for k in METRIC_FIELDS})
        else:
            A=np.array([[int(c) for c in x[:9]]]); B=np.array([[int(c) for c in x[9:18]]]); M=build_M(A,B,x[18:21]); m=batch_metrics(M)[0]; r={'label':label,'x21':x,'tau_x21':tau_x21(x),'canonical_x21':canonical_x21(x),'Assoc':batch_assoc(M)[0]}; r.update(m)
        keyrows.append(r)
    write_csv(TABLES/'H_key_witnesses.csv',keyrows,['label','x21','tau_x21','canonical_x21','Assoc']+METRIC_FIELDS)
    frontier=[]
    for source,rows in [('affine',aff),('column_blind',cb)]:
        for r in rows:
            H=int(r['H_tot']); n=int(r['N_neg'])
            if H in (7302,-2268) or (H==7020 and n==0):
                locus='Hmax_7302' if H==7302 else 'Hmin_minus2268' if H==-2268 else 'pure_frontier_7020'; out={'source':source,'locus':locus,'stratum':r.get('stratum',''),'rule':r.get('rule',''),'a':r.get('a',''),'b':r.get('b',''),'A_param':r.get('A_param',''),'B_param':r.get('B_param',''),'d':r['d'],'x21':r['x21'],'tau_x21':tau_x21(r['x21']),'canonical_x21':canonical_x21(r['x21']),'Assoc':r['Assoc']}; out.update({k:r[k] for k in METRIC_FIELDS}); frontier.append(out)
    bx={}
    for r in frontier: bx.setdefault(r['x21'],r)
    frontier=list(bx.values()); write_csv(TABLES/'H_frontier_loci.csv',frontier,['source','locus','stratum','rule','a','b','A_param','B_param','d','x21','tau_x21','canonical_x21','Assoc']+METRIC_FIELDS)
    groups={}
    for r in frontier: groups[(r['locus'],r['canonical_x21'])]=r
    orbits=[]
    for (locus,canon),r in sorted(groups.items()):
        mem=sorted(set([r['x21'],tau_x21(r['x21'])])); orbits.append({'locus':locus,'canonical_x21':canon,'orbit_members':';'.join(mem),'orbit_size_effective_S3':len(mem),'tau_fixed':str(len(mem)==1),'representative_x21':mem[0],'H_tot':r['H_tot'],'I_tot':r['I_tot'],'B_tot':r['B_tot'],'H_pos':r['H_pos'],'H_neg_abs':r['H_neg_abs'],'N_neg':r['N_neg']})
    write_csv(TABLES/'H_frontier_orbits.csv',orbits,['locus','canonical_x21','orbit_members','orbit_size_effective_S3','tau_fixed','representative_x21','H_tot','I_tot','B_tot','H_pos','H_neg_abs','N_neg'])
    print('Layer1H generation PASS', flush=True)
if __name__=='__main__': main()
