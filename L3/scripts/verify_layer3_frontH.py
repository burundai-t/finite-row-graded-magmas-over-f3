#!/usr/bin/env python3
from __future__ import annotations
import csv, math, hashlib
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'tables'; TABLES.mkdir(exist_ok=True)
S=range(3)

def comp(a,b): return (-a-b)%3
def C(e): r,c=e; return (c,comp(r,c))
def J(e): r,c=e; return (c,r)
def Cinv(e): r,c=e; return (comp(r,c),r)
def compose(f,g): return lambda x: f(g(x))

edges=[(r,c) for r in S for c in S if r!=c]
q=[(i,(i+1)%3) for i in S]
p=[J(q[(-i)%3]) for i in S]
ordered=q+p
def lab(e):
    return f"q{q.index(e)}" if e in q else f"p{p.index(e)}"

def op(x,y,kind):
    r1,c1=x; r2,c2=y
    if r1==r2:
        o = r1 if c1==c2 else comp(c1,c2)
    else:
        o = r2 if kind=='pab' else comp(r1,r2)
    return (r1,o)

def abs_pairs(kind):
    return {(x,y) for x in edges for y in edges if y!=x and op(x,y,kind)==x}
def tr_pairs(f): return {(x,f(x)) for x in edges}

# exact matrices
def Z(n,m): return [[Fraction(0) for _ in range(m)] for __ in range(n)]
def I(n):
    A=Z(n,n)
    for i in range(n): A[i][i]=Fraction(1)
    return A
def neg(A): return [[-x for x in r] for r in A]
def T(A): return [list(r) for r in zip(*A)]
def MM(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def block(A,B,Cc,D): return [ra+rb for ra,rb in zip(A,B)] + [rc+rd for rc,rd in zip(Cc,D)]
def perm(n,mp):
    A=Z(n,n)
    for i,j in mp.items(): A[j][i]=Fraction(1)
    return A
def powm(A,n):
    R=I(len(A))
    for _ in range(n): R=MM(A,R)
    return R
def symp(A,Omega):
    B=MM(T(A),MM(Omega,A))
    if B==Omega: return 'symplectic'
    if B==neg(Omega): return 'anti-symplectic'
    return 'neither'

I3=I(3); Z3=Z(3,3); I6=I(6)
Omega=block(Z3,I3,neg(I3),Z3)
R=perm(3,{i:(i+1)%3 for i in S})
P=perm(3,{i:(-i)%3 for i in S})
Chat=block(R,Z3,Z3,R)
J0=block(Z3,P,P,Z3)
Jhat=block(Z3,neg(P),P,Z3)

def write(name,rows,fields):
    with (TABLES/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

# tables
write('layer3_frontH_edge_qp_chart.csv',
      [{'sector':'q','index':i,'edge':str(e),'C(edge)':lab(C(e)),'J(edge)':lab(J(e))} for i,e in enumerate(q)] +
      [{'sector':'p','index':i,'edge':str(e),'C(edge)':lab(C(e)),'J(edge)':lab(J(e))} for i,e in enumerate(p)],
      ['sector','index','edge','C(edge)','J(edge)'])

rels=[
 {'claim':'C^3=1 on M^x','result':str(all(C(C(C(e)))==e for e in edges)),'detail':'finite continuation order 3'},
 {'claim':'J^2=1 on M^x','result':str(all(J(J(e))==e for e in edges)),'detail':'finite reversal involution'},
 {'claim':'J C J = C^{-1}','result':str(all(J(C(J(e)))==Cinv(e) for e in edges)),'detail':'dihedral relation'},
 {'claim':'PAB AbsTrans={C,J}','result':str(abs_pairs('pab')==(tr_pairs(C)|tr_pairs(J))),'detail':'pure C/J'},
 {'claim':'row-complement AbsTrans={C^{-1},C^{-1}J}','result':str(abs_pairs('comp')==(tr_pairs(Cinv)|tr_pairs(compose(Cinv,J)))),'detail':'drifted reversal'}
]
write('layer3_frontH_CJ_finite_relations.csv',rels,['claim','result','detail'])

entries=[]
for nm,A in [('Omega',Omega),('C_hat',Chat),('J_unsigned',J0),('J_signed',Jhat)]:
    for i,row in enumerate(A):
        for j,x in enumerate(row):
            if x: entries.append({'matrix':nm,'row':i,'col':j,'value':str(x)})
write('layer3_frontH_signed_lift_matrices.csv',entries,['matrix','row','col','value'])

Jhat_inv=neg(Jhat)
aud=[
 {'object':'C_hat','check':'A^T Omega A','result':symp(Chat,Omega),'detail':'sector-preserving continuation lift'},
 {'object':'J_unsigned','check':'A^T Omega A','result':symp(J0,Omega),'detail':'literal q/p swap is anti-symplectic'},
 {'object':'J_signed','check':'A^T Omega A','result':symp(Jhat,Omega),'detail':'signed sector exchange is symplectic'},
 {'object':'C_hat^3','check':'equals I','result':str(powm(Chat,3)==I6),'detail':'exact'},
 {'object':'J_signed^2','check':'equals -I','result':str(MM(Jhat,Jhat)==neg(I6)),'detail':'projective involution'},
 {'object':'J_signed C_hat J_signed^{-1}','check':'equals C_hat^{-1}','result':str(MM(Jhat,MM(Chat,Jhat_inv))==powm(Chat,2)),'detail':'projective D3'}
]
write('layer3_frontH_symplectic_audit.csv',aud,['object','check','result','detail'])

# float path checks
def fMM(A,B): return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def fT(A): return [list(r) for r in zip(*A)]
def fZ(n,m): return [[0.0]*m for _ in range(n)]
def fI(n): return [[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
def fblock(A,B,Cc,D): return [a+b for a,b in zip(A,B)]+[c+d for c,d in zip(Cc,D)]
def fneg(A): return [[-x for x in r] for r in A]
def fsub(A,B): return [[A[i][j]-B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
def maxabs(A): return max(abs(x) for r in A for x in r)
Om=[[float(x) for x in r] for r in Omega]
def symperr(A): return maxabs(fsub(fMM(fT(A),fMM(Om,A)),Om))
Pf=[[float(x) for x in r] for r in P]
def Cpath(t):
    # rotation around (1,1,1), oriented so t=1 gives R e_i=e_{i+1}
    th=2*math.pi*t/3
    ux=uy=uz=1/math.sqrt(3); c=math.cos(th); s=math.sin(th)
    K=[[0,-uz,uy],[uz,0,-ux],[-uy,ux,0]]
    uu=[[ux*ux,ux*uy,ux*uz],[uy*ux,uy*uy,uy*uz],[uz*ux,uz*uy,uz*uz]]
    I0=fI(3)
    Rt=[[c*I0[i][j]+(1-c)*uu[i][j]+s*K[i][j] for j in range(3)] for i in range(3)]
    return fblock(Rt,fZ(3,3),fZ(3,3),Rt)
def Jpath(t):
    a=math.cos(math.pi*t/2); b=math.sin(math.pi*t/2); I0=fI(3)
    A=[[a*I0[i][j] for j in S] for i in S]
    B=[[-b*Pf[i][j] for j in S] for i in S]
    Cc=[[b*Pf[i][j] for j in S] for i in S]
    D=A
    return fblock(A,B,Cc,D)
Chatf=[[float(x) for x in r] for r in Chat]
Jhatf=[[float(x) for x in r] for r in Jhat]
path=[]
for fam,fn in [('C_t',Cpath),('J_t',Jpath)]:
    for t in [0,0.25,0.5,0.75,1.0]:
        err=symperr(fn(t))
        path.append({'family':fam,'t':t,'symplectic_error':f'{err:.3e}','passes_tol':str(err<1e-9)})
path.append({'family':'C_t','t':'endpoint_vs_C_hat','symplectic_error':f'{maxabs(fsub(Cpath(1),Chatf)):.3e}','passes_tol':str(maxabs(fsub(Cpath(1),Chatf))<1e-9)})
path.append({'family':'J_t','t':'endpoint_vs_J_signed','symplectic_error':f'{maxabs(fsub(Jpath(1),Jhatf)):.3e}','passes_tol':str(maxabs(fsub(Jpath(1),Jhatf))<1e-9)})
write('layer3_frontH_continuous_path_audit.csv',path,['family','t','symplectic_error','passes_tol'])

seq=['C','J','C','C','J']; st=q[0]; seen={st}
hpath=[{'step':0,'transition':'start','state':lab(st),'edge':str(st),'unique_so_far':1}]
for k,s in enumerate(seq,1):
    st=C(st) if s=='C' else J(st)
    seen.add(st)
    hpath.append({'step':k,'transition':s,'state':lab(st),'edge':str(st),'unique_so_far':len(seen)})
write('layer3_frontH_hamiltonian_path.csv',hpath,['step','transition','state','edge','unique_so_far'])
Phi=MM(Jhat,MM(Chat,MM(Chat,MM(Jhat,Chat))))
tick=[
 {'sequence':'C,J,C,C,J','check':'finite path visits all six directed edges','result':str(len(seen)==6),'detail':'starting at q0'},
 {'sequence':'C,J,C,C,J','check':'signed lift symplectic','result':symp(Phi,Omega),'detail':'composition of signed lifts'},
 {'sequence':'C,J,C,C,J','check':'signed entries present','result':str(any(x<0 for r in Phi for x in r)),'detail':'signs encode symplectic orientation'}
]
write('layer3_frontH_tick_map_audit.csv',tick,['sequence','check','result','detail'])
write('layer3_frontH_competitor_guardrail.csv',[
 {'candidate':'PAB','absorptions':'{C,J}','pure_J_kick':'yes','signed_symplectic_bridge':'clean C/J bridge','selector_role':'selected'},
 {'candidate':'row-complement','absorptions':'{C^{-1},C^{-1}J}','pure_J_kick':'no','signed_symplectic_bridge':'only if drifted reversal is allowed','selector_role':'rejected by finite pure C/J'},
 {'candidate':'policy','absorptions':'-','pure_J_kick':'-','signed_symplectic_bridge':'post-selection bridge, not selector dependency','selector_role':'guardrail'}
],['candidate','absorptions','pure_J_kick','signed_symplectic_bridge','selector_role'])
write('layer3_frontH_status_registry.csv',[
 {'item':'finite C/J geometry','status':'closed','claim':'C^3=1, J^2=1, JCJ=C^{-1}; PAB AbsTrans={C,J}'},
 {'item':'q/p chart','status':'closed','claim':'q_i=(i,i+1), p_i=J(q_-i); C preserves sectors; J exchanges sectors'},
 {'item':'literal unsigned J','status':'closed guardrail','claim':'anti-symplectic'},
 {'item':'signed lift','status':'closed','claim':'C_hat,J_hat in Sp(6); projective D3'},
 {'item':'continuous path','status':'closed','claim':'explicit smooth C_t,J_t in Sp(6)'},
 {'item':'selector dependency','status':'guardrail','claim':'not a replacement for finite pure C/J selector'}
],['item','status','claim'])

manifest=[]
for f in sorted(TABLES.glob('layer3_frontH_*.csv')):
    data=f.read_bytes()
    manifest.append({'table':f.name,'rows':sum(1 for _ in f.open(encoding='utf-8'))-1,'sha256':hashlib.sha256(data).hexdigest()})
write('layer3_frontH_table_manifest.csv',manifest,['table','rows','sha256'])

checks=[
 {'check':'finite D3 relations','result':'PASS' if all(r['result']=='True' for r in rels[:3]) else 'FAIL'},
 {'check':'absorption relations','result':'PASS' if all(r['result']=='True' for r in rels[3:]) else 'FAIL'},
 {'check':'signed symplectic audit','result':'PASS' if aud[0]['result']=='symplectic' and aud[1]['result']=='anti-symplectic' and aud[2]['result']=='symplectic' and all(a['result']=='True' for a in aud[3:]) else 'FAIL'},
 {'check':'continuous path samples','result':'PASS' if all(r['passes_tol']=='True' for r in path) else 'FAIL'},
 {'check':'Hamiltonian path','result':'PASS' if len(seen)==6 else 'FAIL'},
 {'check':'tick signed lift','result':'PASS' if tick[1]['result']=='symplectic' else 'FAIL'}
]
write('layer3_frontH_verifier_checks.csv',checks,['check','result'])
if any(c['result']!='PASS' for c in checks):
    print(checks)
    raise SystemExit(1)
print('Layer 3 Front H verifier: PASS')
print('  finite pure C/J geometry: D3 relations and PAB/competitor absorption transitions checked')
print('  canonical q/p chart: C preserves sectors and J exchanges sectors with reflection')
print('  signed symplectic lift: C_hat and J_hat lie in Sp(6); literal unsigned J is anti-symplectic')
print('  projective D3 lift: C_hat^3=I, J_hat^2=-I, J_hat C_hat J_hat^{-1}=C_hat^{-1}')
print('  continuous realization: explicit C_t and J_t paths in Sp(6) checked by endpoint/sample audit')
print('  tick bridge: C,J,C,C,J finite Hamiltonian path visits all six edges and has symplectic signed lift')
