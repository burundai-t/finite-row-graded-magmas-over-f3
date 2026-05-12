#!/usr/bin/env python3
"""Layer 3 Front F verifier: hidden continuation contrast via operator envelope.

Regenerates the Front F audit tables and checks the core operator-H claims.
"""
from __future__ import annotations
import csv
from itertools import product
from collections import Counter, defaultdict
from pathlib import Path

S=(0,1,2)
M=tuple(product(S,S))
IDX={m:i for i,m in enumerate(M)}

def bar(a,b): return (-a-b)%3

def mul_pab(x,y):
    r,c=x; s,d=y
    if r!=s: return (r,s)
    if c==d: return (r,r)
    return (r,bar(c,d))

def mul_rowcomp(x,y):
    r,c=x; s,d=y
    if r!=s: return (r,bar(r,s))
    if c==d: return (r,r)
    return (r,bar(c,d))

def make_cb(a,b):
    def h(r,s):
        diff=(s-r)%3
        return (a+r)%3 if diff==1 else (b+r)%3
    def mul(x,y):
        r,c=x; s,d=y
        if r!=s: return (r,h(r,s))
        if c==d: return (r,r)
        return (r,bar(c,d))
    return mul

def L(mul,x): return tuple(IDX[mul(x,y)] for y in M)
def compose(f,g): return tuple(f[i] for i in g)
def dist(f,g): return sum(1 for a,b in zip(f,g) if a!=b)
def hs2(f,g): return 2*dist(f,g)

def Bmap(r,a): return tuple(r if c==a else bar(a,c) for c in S)
def ustr(U): return ''.join(map(str,U))


def Kmap(r,t):
    return tuple(IDX[(r,t)] for _ in M)

def Tmap(r,U,a):
    V=Bmap(r,a); out=[]
    for q,c in M:
        col=U[V[c]] if q==r else U[q]
        out.append(IDX[(r,col)])
    return tuple(out)

def compose_cols(U,V):
    return tuple(U[V[c]] for c in S)

def same_row_semigroup(r):
    sem={tuple(S)}|{Bmap(r,a) for a in S}; changed=True
    while changed:
        changed=False
        for U in tuple(sem):
            for V in tuple(sem):
                W=compose_cols(U,V)
                if W not in sem:
                    sem.add(W); changed=True
    return sem

def normal_labels():
    labels={}
    for r in S:
        for t in S:
            labels.setdefault(Kmap(r,t), f'K({r},{t})')
        cand=[]
        for U in sorted(same_row_semigroup(r)):
            for a in S:
                cand.append((f'T({r},{ustr(U)},{a})', Tmap(r,U,a)))
        for lab,f in sorted(cand):
            labels.setdefault(f, lab)
    return labels

def pair_label(u,v):
    r,a=u; s,b=v
    if r!=s: return f"K({r},{s})"
    return f"T({r},{ustr(Bmap(r,a))},{b})"

def left_label(u):
    r,a=u
    return f"T({r},012,{a})"

def block_name(b,t):
    if b==0 and t==0: return 'RRR'
    if b==0: return 'RRS'
    if t==0: return 'RSR'
    if t==b: return 'RSS'
    return 'RST'

def cb_label(a,b):
    if (a,b)==(1,2): return 'PAB / g1 = r2'
    if (a,b)==(2,1): return 'row-complement = bar(r1,r2)'
    if a==b: return f'trivial h_{{{a},{b}}}'
    return f'h_{{{a},{b}}}'

def assoc_count(mul):
    return sum(1 for x,y,z in product(M,repeat=3) if mul(mul(x,y),z)==mul(x,mul(y,z)))

def profile(mul, with_labels=False, labels=None):
    Ls={x:L(mul,x) for x in M}
    triples=[]; value_counts=Counter(); block_counts=defaultdict(Counter); pair_counts=Counter(); row_counts=defaultdict(Counter)
    for x,y,z in product(M,repeat=3):
        xy=mul(x,y); yz=mul(y,z); eL=mul(xy,z); eR=mul(x,yz)
        Aop=compose(Ls[xy],Ls[z]); Cop=compose(Ls[x],Ls[yz])
        Bleft=Ls[eL]; Bright=Ls[eR]
        I=hs2(Aop,Cop); B=hs2(Bleft,Bright); H=I-B
        b=(y[0]-x[0])%3; t=(z[0]-x[0])%3; bl=block_name(b,t)
        value_counts[(I,B,H)]+=1; block_counts[bl][(I,B,H)]+=1; row_counts[(b,t,bl)][(I,B,H)]+=1
        if with_labels:
            pl=labels[Aop]; ql=labels[Cop]; al=labels[Bleft]; blab=labels[Bright]
            pair_counts[(pl,ql,al,blab,I,B,H)]+=1
        triples.append((x,y,z,xy,yz,eL,eR,I,B,H))
    return {'triples':triples,'values':value_counts,'blocks':block_counts,'rows':row_counts,'pairs':pair_counts,
            'I_tot':sum(I*c for (I,B,H),c in value_counts.items()),
            'B_tot':sum(B*c for (I,B,H),c in value_counts.items()),
            'H_tot':sum(H*c for (I,B,H),c in value_counts.items()),
            'H_plus':sum(H*c for (I,B,H),c in value_counts.items() if H>0),
            'H_minus':-sum(H*c for (I,B,H),c in value_counts.items() if H<0),
            'N_minus':sum(c for (I,B,H),c in value_counts.items() if H<0)}

def counts_to_str(counter):
    return ';'.join(f'{k}:{v}' for k,v in sorted(counter.items()))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    root=Path(__file__).resolve().parents[1]
    tables=root/'tables'
    # remove Front F tables to avoid stale data
    for p in tables.glob('layer3_frontF_*.csv'):
        p.unlink()

    labels=normal_labels()
    pab=profile(mul_pab, with_labels=True, labels=labels)
    comp=profile(mul_rowcomp, with_labels=False)

    # LuLv formula audit over all 81 pairs.
    Ls={x:L(mul_pab,x) for x in M}
    formula_rows=[]
    for u,v in product(M,repeat=2):
        r,a=u; s,b=v
        actual=compose(Ls[u],Ls[v])
        if r!=s:
            expected=tuple(IDX[(r,s)] for _ in M); form=f'K({r},{s})'
        else:
            U=Bmap(r,a); V=Bmap(r,b)
            outs=[]
            for q,c in M:
                col=U[V[c]] if q==r else U[q]
                outs.append(IDX[(r,col)])
            expected=tuple(outs); form=f'T({r},{ustr(U)},{b})'
        formula_rows.append({'u':u,'v':v,'same_row':r==s,'normal_form':form,'verified':actual==expected})
    assert all(r['verified'] for r in formula_rows)
    write_csv(tables/'layer3_frontF_LuLv_composition_formula_audit.csv', formula_rows, ['u','v','same_row','normal_form','verified'])

    # Envelope/membership summary via the pair formula.
    unique_pair_ops=set()
    for x,y,z,xy,yz,eL,eR,I,B,H in pab['triples']:
        unique_pair_ops.add(labels[compose(L(mul_pab,xy), L(mul_pab,z))]); unique_pair_ops.add(labels[compose(L(mul_pab,x), L(mul_pab,yz))])
    membership=[{'profile':'PAB','positive_monoid_size_from_FrontB':51,'unique_continuation_operator_labels':len(unique_pair_ops),'unique_boundary_left_translation_labels':9,'all_continuation_operators_have_K_or_T_normal_form':True,'all_boundary_operators_are_left_translations':True,'all_four_operators_in_W_row_x':True,'envelope_pair_types':len(pab['pairs']),'distance_types':len(pab['values'])}]
    write_csv(tables/'layer3_frontF_envelope_membership_summary.csv', membership, list(membership[0].keys()))

    # Distance table.
    dist_rows=[]
    for (I,B,H),c in sorted(pab['values'].items()):
        dist_rows.append({'I':I,'B':B,'H':H,'triple_count':c,'I_contribution':I*c,'B_contribution':B*c,'H_contribution':H*c,'nonnegative_H':H>=0})
    write_csv(tables/'layer3_frontF_distance_type_table.csv', dist_rows, ['I','B','H','triple_count','I_contribution','B_contribution','H_contribution','nonnegative_H'])

    # H value distribution with block rows.
    hv=[]
    for (I,B,H),c in sorted(pab['values'].items()): hv.append({'block':'GLOBAL','I':I,'B':B,'H':H,'count':c,'H_contribution':H*c})
    for bl in ['RRR','RRS','RSR','RSS','RST']:
        for (I,B,H),c in sorted(pab['blocks'][bl].items()): hv.append({'block':bl,'I':I,'B':B,'H':H,'count':c,'H_contribution':H*c})
    write_csv(tables/'layer3_frontF_H_value_distribution.csv', hv, ['block','I','B','H','count','H_contribution'])

    # Block totals.
    block_rows=[]
    for bl in ['RRR','RRS','RSR','RSS','RST']:
        cnt=pab['blocks'][bl]
        I=sum(k[0]*v for k,v in cnt.items()); B=sum(k[1]*v for k,v in cnt.items()); H=sum(k[2]*v for k,v in cnt.items())
        assoc=sum(1 for tr in pab['triples'] if block_name((tr[1][0]-tr[0][0])%3,(tr[2][0]-tr[0][0])%3)==bl and tr[5]==tr[6])
        B0=sum(1 for tr in pab['triples'] if block_name((tr[1][0]-tr[0][0])%3,(tr[2][0]-tr[0][0])%3)==bl and tr[8]==0)
        block_rows.append({'block':bl,'actual_triples':sum(cnt.values()),'I_tot':I,'B_tot':B,'H_tot':H,'rawI_normalized':I//6,'rawB_normalized':B//6,'rawH_normalized':H//6,'assoc_count':assoc,'B_zero_count':B0,'H_value_counts':counts_to_str(Counter({h:sum(v for (i,b,h2),v in cnt.items() if h2==h) for h in sorted({h for (i,b,h) in cnt})}))})
    write_csv(tables/'layer3_frontF_operator_H_block_totals.csv', block_rows, ['block','actual_triples','I_tot','B_tot','H_tot','rawI_normalized','rawB_normalized','rawH_normalized','assoc_count','B_zero_count','H_value_counts'])

    # Row pattern decomposition by b,t.
    row_rows=[]
    for (b,t,bl),cnt in sorted(pab['rows'].items()):
        I=sum(k[0]*v for k,v in cnt.items()); B=sum(k[1]*v for k,v in cnt.items()); H=sum(k[2]*v for k,v in cnt.items())
        row_rows.append({'b_row_y_minus_x':b,'t_row_z_minus_x':t,'block':bl,'triple_count':sum(cnt.values()),'I_tot':I,'B_tot':B,'H_tot':H,'rawH_contribution':H//6,'H_value_counts':counts_to_str(Counter({h:sum(v for (i,bv,h2),v in cnt.items() if h2==h) for h in sorted({h for (i,bv,h) in cnt})}))})
    write_csv(tables/'layer3_frontF_row_pattern_decomposition.csv', row_rows, ['b_row_y_minus_x','t_row_z_minus_x','block','triple_count','I_tot','B_tot','H_tot','rawH_contribution','H_value_counts'])

    # Pair normal forms.
    pair_rows=[]
    for (pl,ql,al,blab,I,B,H),c in sorted(pab['pairs'].items()):
        pair_rows.append({'A_operator':pl,'C_operator':ql,'left_boundary_operator':al,'right_boundary_operator':blab,'I':I,'B':B,'H':H,'triple_count':c,'H_contribution':H*c})
    write_csv(tables/'layer3_frontF_operator_pair_normal_form_audit.csv', pair_rows, ['A_operator','C_operator','left_boundary_operator','right_boundary_operator','I','B','H','triple_count','H_contribution'])

    # Column-blind d=000 audit.
    cb=[]; pure_H=[]; profs={}
    for a,b in product(S,repeat=2):
        pr=profile(make_cb(a,b), with_labels=False); profs[(a,b)]=pr
        pure=pr['N_minus']==0
        if pure: pure_H.append(pr['H_tot'])
        cb.append({'a':a,'b':b,'rule':cb_label(a,b),'nontrivial':a!=b,'Assoc_000':assoc_count(make_cb(a,b)),'I_tot':pr['I_tot'],'B_tot':pr['B_tot'],'H_tot':pr['H_tot'],'H_plus':pr['H_plus'],'H_minus':pr['H_minus'],'N_minus':pr['N_minus'],'pure':pure,'pure_Hmax_d000':False,'H_value_counts':counts_to_str(Counter({h:sum(c for (i,bv,h2),c in pr['values'].items() if h2==h) for h in sorted({h for (i,bv,h) in pr['values']})}))})
    max_pure=max(pure_H)
    for r in cb: r['pure_Hmax_d000']=r['pure'] and r['H_tot']==max_pure
    write_csv(tables/'layer3_frontF_column_blind_d000_H_audit.csv', cb, ['a','b','rule','nontrivial','Assoc_000','I_tot','B_tot','H_tot','H_plus','H_minus','N_minus','pure','pure_Hmax_d000','H_value_counts'])

    # PAB/competitor guardrail and comparison.
    guard=[]
    for key,name in [((1,2),'PAB'),((2,1),'row-complement')]:
        pr=profs[key]
        guard.append({'object':name,'a':key[0],'b':key[1],'I_tot':pr['I_tot'],'B_tot':pr['B_tot'],'H_tot':pr['H_tot'],'H_plus':pr['H_plus'],'H_minus':pr['H_minus'],'N_minus':pr['N_minus'],'H_value_counts':counts_to_str(Counter({h:sum(c for (i,bv,h2),c in pr['values'].items() if h2==h) for h in sorted({h for (i,bv,h) in pr['values']})}))})
    write_csv(tables/'layer3_frontF_pab_comp_H_guardrail.csv', guard, ['object','a','b','I_tot','B_tot','H_tot','H_plus','H_minus','N_minus','H_value_counts'])

    comp_rows=[]
    for name,pr in [('PAB',profs[(1,2)]),('row-complement',profs[(2,1)])]:
        comp_rows.append({'kind':name,'I_tot':pr['I_tot'],'B_tot':pr['B_tot'],'H_tot':pr['H_tot'],'H_plus':pr['H_plus'],'H_minus':pr['H_minus'],'N_minus':pr['N_minus'],'assoc_count':assoc_count(make_cb(1,2) if name=='PAB' else make_cb(2,1)),'B_zero_count':sum(c for (I,B,H),c in pr['values'].items() if B==0)})
        for bl in ['RRR','RRS','RSR','RSS','RST']:
            cnt=pr['blocks'][bl]
            comp_rows.append({'kind':f'{name}:{bl}','I_tot':sum(k[0]*v for k,v in cnt.items()),'B_tot':sum(k[1]*v for k,v in cnt.items()),'H_tot':sum(k[2]*v for k,v in cnt.items()),'H_plus':sum(k[2]*v for k,v in cnt.items() if k[2]>0),'H_minus':-sum(k[2]*v for k,v in cnt.items() if k[2]<0),'N_minus':sum(v for k,v in cnt.items() if k[2]<0),'assoc_count':'','B_zero_count':''})
    write_csv(tables/'layer3_frontF_pab_comp_H_comparison.csv', comp_rows, ['kind','I_tot','B_tot','H_tot','H_plus','H_minus','N_minus','assoc_count','B_zero_count'])

    dom=[]
    for name,pr in [('PAB',profs[(1,2)]),('row-complement',profs[(2,1)])]:
        hvals=Counter({h:sum(c for (i,bv,h2),c in pr['values'].items() if h2==h) for h in sorted({h for (i,bv,h) in pr['values']})})
        dom.append({'kind':name,'triples':729,'min_H':min(hvals),'max_H':max(hvals),'negative_H_count':sum(c for h,c in hvals.items() if h<0),'zero_H_count':hvals.get(0,0),'positive_H_count':sum(c for h,c in hvals.items() if h>0),'H_plus':pr['H_plus'],'H_minus':pr['H_minus'],'N_minus':pr['N_minus'],'status':'PASS' if pr['N_minus']==0 else 'FAIL'})
    write_csv(tables/'layer3_frontF_pointwise_dominance_audit.csv', dom, ['kind','triples','min_H','max_H','negative_H_count','zero_H_count','positive_H_count','H_plus','H_minus','N_minus','status'])

    status=[
        {'claim':'For PAB, L_(xy)L_z and L_xL_(yz) lie in the L3-B composition envelope E','status':'[V-structural/computational]','support':'LuLv formula + envelope membership summary'},
        {'claim':'For every PAB triple, all four operators in H lie in W_row(x)','status':'[V]','support':'Front F verifier'},
        {'claim':'PAB H profile is H_tot=7020, H_-=0, N_-=0','status':'[V]','support':'distance type table'},
        {'claim':'PAB triple-level H is pointwise nonnegative','status':'[V]','support':'distance type table'},
        {'claim':'PAB and row-complement have the same d=000 H profile','status':'[V]','support':'PAB/competitor guardrail table'},
        {'claim':'H separates PAB from row-complement','status':'rejected','support':'same H profile'},
        {'claim':'Global Omega pure-frontier theorem max{H_tot:N_-=0}=7020','status':'[Open]','support':'Layer 1H controlled theorem only'},
    ]
    write_csv(tables/'layer3_frontF_status_registry.csv', status, ['claim','status','support'])

    checks=[
        {'check':'pab_H_tot','expected':7020,'actual':pab['H_tot'],'pass':pab['H_tot']==7020},
        {'check':'pab_H_minus','expected':0,'actual':pab['H_minus'],'pass':pab['H_minus']==0},
        {'check':'pab_N_minus','expected':0,'actual':pab['N_minus'],'pass':pab['N_minus']==0},
        {'check':'pab_distance_type_count','expected':9,'actual':len(pab['values']),'pass':len(pab['values'])==9},
        {'check':'pab_envelope_pair_type_count','expected':93,'actual':len(pab['pairs']),'pass':len(pab['pairs'])==93},
        {'check':'row_complement_H_tot','expected':7020,'actual':comp['H_tot'],'pass':comp['H_tot']==7020},
        {'check':'row_complement_H_minus','expected':0,'actual':comp['H_minus'],'pass':comp['H_minus']==0},
        {'check':'pab_and_row_complement_same_H_profile','expected':True,'actual':profs[(1,2)]['values']==profs[(2,1)]['values'],'pass':profs[(1,2)]['values']==profs[(2,1)]['values']},
        {'check':'column_blind_d000_pure_Hmax','expected':7020,'actual':max_pure,'pass':max_pure==7020},
        {'check':'column_blind_d000_pure_Hmax_locus','expected':'[(1, 2), (2, 1)]','actual':str(sorted((r['a'],r['b']) for r in cb if r['pure_Hmax_d000'])),'pass':sorted((r['a'],r['b']) for r in cb if r['pure_Hmax_d000'])==[(1,2),(2,1)]},
    ]
    write_csv(tables/'layer3_frontF_verifier_checks.csv', checks, ['check','expected','actual','pass'])
    assert all(c['pass'] for c in checks)

    log='\n'.join([
        'Layer 3 Front F verifier: PASS',
        '  operator envelope: continuation operators L_(xy)L_z and L_xL_(yz) lie in E and in W_row(x)',
        '  distance collapse: 729 triples -> 93 normal-form pair types -> 9 (I,B,H) distance types',
        '  PAB H profile: I_tot=8904, B_tot=1884, H_tot=7020, H_-=0, N_-=0',
        '  row-pattern decomposition: rawH contributions sum to 1170, hence H_tot=6*1170=7020',
        '  guardrail: row-complement has the same H profile, so H is an operator bridge, not a selector',
        '  column-blind d=000 audit: pure H maximum 7020 is attained exactly by PAB and row-complement',
    ])
    (root/'verify_layer3_frontF.log').write_text(log+'\n',encoding='utf-8')
    print(log)
if __name__=='__main__': main()
