#!/usr/bin/env -S python3 -S
from __future__ import annotations
from itertools import product
S=(0,1,2)
M_ELEMS=tuple(product(S,S))
TERMS7=tuple(product(S, repeat=7))
TERMS5=tuple(product(S, repeat=5))
UL_TERMS=tuple(product(S, repeat=2))
METRIC_FIELDS=['rawI','rawB','rawH','I_tot','B_tot','H_tot','H_pos','H_neg_abs','N_neg','h_loc_min','h_loc_max','H_RRR','H_RRS','H_RSR','H_SRR','H_DIST']

def comp(a,e): return (-a-e)%3
def idx(a,e): return 3*(a%3)+(e%3)
def parse_x21(x):
    vals=[int(c) for c in x] if isinstance(x,str) else [int(v) for v in x]
    if len(vals)!=21: raise ValueError('x21 length must be 21')
    return vals
def x21_from_parts(A,B,d): return ''.join(str(int(v)%3) for v in list(A)+list(B)+list(d))
def mtab(x):
    vals=parse_x21(x); M=[0]*27
    for a,e in product(S,S):
        i=idx(a,e); M[i]=vals[18+a] if a==e else comp(a,e); M[9+i]=vals[i]; M[18+i]=vals[9+i]
    return M
def mv(M,s,a,e): return M[(s%3)*9+(a%3)*3+(e%3)]
def block_id(b,t):
    if b==0 and t==0: return 0
    if b==0: return 1
    if t==0: return 2
    if t==b: return 3
    return 4

def h_raw_counts(x):
    M=mtab(x); rawI=rawB=0
    for b,t,u,a,e,f,l in TERMS7:
        xy=mv(M,b,a,e)
        zw_abs=(t+mv(M,u-t,f-t,l-t))%3
        yz_rel=mv(M,t-b,e-b,f-b)
        if mv(M,t,xy,zw_abs)!=mv(M,b,a,(b+mv(M,u-b,yz_rel,l-b))%3): rawI+=1
        if mv(M,u,mv(M,t,xy,f),l)!=mv(M,u,mv(M,b,a,(b+yz_rel)%3),l): rawB+=1
    return rawI,rawB,rawI-rawB

def local_values(x):
    M=mtab(x); I=[]; B=[]; H=[]
    for b,t,a,e,f in TERMS5:
        di=db=0; xy=mv(M,b,a,e); yz_rel=mv(M,t-b,e-b,f-b); epL=mv(M,t,xy,f); epR=mv(M,b,a,(b+yz_rel)%3)
        for u,l in UL_TERMS:
            zw_abs=(t+mv(M,u-t,f-t,l-t))%3
            if mv(M,t,xy,zw_abs)!=mv(M,b,a,(b+mv(M,u-b,yz_rel,l-b))%3): di+=1
            if mv(M,u,epL,l)!=mv(M,u,epR,l): db+=1
        I.append(2*di); B.append(2*db); H.append(2*(di-db))
    return I,B,H

def h_metrics(x):
    I,B,H=local_values(x); rawI=sum(I)//2; rawB=sum(B)//2; rawH=rawI-rawB
    blocks=[0]*5; pos=neg=nneg=0
    for (b,t,a,e,f),h in zip(TERMS5,H):
        blocks[block_id(b,t)]+=h
        if h>0: pos+=h
        elif h<0: neg+=-h; nneg+=1
    return {'rawI':rawI,'rawB':rawB,'rawH':rawH,'I_tot':6*rawI,'B_tot':6*rawB,'H_tot':6*rawH,'H_pos':3*pos,'H_neg_abs':3*neg,'N_neg':3*nneg,'h_loc_min':min(H),'h_loc_max':max(H),'H_RRR':3*blocks[0],'H_RRS':3*blocks[1],'H_RSR':3*blocks[2],'H_SRR':3*blocks[3],'H_DIST':3*blocks[4]}

def assoc_tot(x):
    M=mtab(x); c=0
    for b,t,a,e,f in TERMS5:
        if mv(M,t,mv(M,b,a,e),f)==mv(M,b,a,(b+mv(M,t-b,e-b,f-b))%3): c+=1
    return 3*c

def mult_from_x21(x):
    M=mtab(x)
    def mult(p,q):
        r1,c1=p; r2,c2=q; rel=mv(M,r2-r1,c1-r1,c2-r1); return (r1,(r1+rel)%3)
    return mult

def h_direct_tot(x):
    mult=mult_from_x21(x); I=B=0
    for X,Y,Z in product(M_ELEMS, repeat=3):
        xy=mult(X,Y); yz=mult(Y,Z); epL=mult(xy,Z); epR=mult(X,yz)
        for W in M_ELEMS:
            if mult(xy,mult(Z,W))!=mult(X,mult(yz,W)): I+=2
            if mult(epL,W)!=mult(epR,W): B+=2
    return I,B,I-B

def tau_x21(x):
    vals=parse_x21(x); y=[0]*21
    def cidx(a,b,e):
        a%=3; b%=3; e%=3
        return 3*a+e if b==1 else 9+3*a+e
    for a,e in product(S,S):
        y[cidx(-a,2,-e)]=(-vals[cidx(a,1,e)])%3; y[cidx(-a,1,-e)]=(-vals[cidx(a,2,e)])%3
    y[18]=(-vals[18])%3; y[19]=(-vals[20])%3; y[20]=(-vals[19])%3
    return ''.join(map(str,y))
def canonical_x21(x): return min(x,tau_x21(x))
def column_blind_x21(a,b,d='000'): return x21_from_parts([a]*9,[b]*9,[int(c) for c in d])
def affine_table(p):
    A,B,C=p; return [((A*a+B*e+C)%3) for a,e in product(S,S)]
def affine_x21(pa,pb,d): return x21_from_parts(affine_table(pa),affine_table(pb),[int(c) for c in d])
def standard_six():
    A1=[1]*9; B1=[2]*9; A2=[e for a,e in product(S,S)]; A3=[a if a==e else comp(a,e) for a,e in product(S,S)]; A4=[a for a,e in product(S,S)]; A5=[0]*9; A6=[1 if e==1 else comp(1,e) for a,e in product(S,S)]; B6=[2 if e==2 else comp(2,e) for a,e in product(S,S)]; d=[0,0,0]
    return {'g1_PAB':x21_from_parts(A1,B1,d),'g2_transparent':x21_from_parts(A2,A2,d),'g3_su2_transparent':x21_from_parts(A3,A3,d),'g4_echo':x21_from_parts(A4,A4,d),'g5_self_referential':x21_from_parts(A5,A5,d),'g6_anti_complement':x21_from_parts(A6,B6,d)}
