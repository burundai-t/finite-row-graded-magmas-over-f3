#!/usr/bin/env python3
from itertools import product
import json

S=(0,1,2)
M=tuple((r,c) for r in S for c in S)

def comp(a,b): return (-a-b)%3

def assoc_master_x21(x):
    A=x[:9]; B=x[9:18]; d=x[18:21]
    def m(b,a,e):
        b%=3; a%=3; e%=3
        if b==0:
            return d[a] if a==e else comp(a,e)
        return (A if b==1 else B)[3*a+e]
    raw=0
    blocks={"RRR":0,"RRS":0,"RSR":0,"RSS":0,"RST":0}
    for b,t,a,e,f in product(S,S,S,S,S):
        if b==0 and t==0: label="RRR"
        elif b==0 and t!=0: label="RRS"
        elif b!=0 and t==0: label="RSR"
        elif b!=0 and t==b: label="RSS"
        else: label="RST"
        xy=m(b,a,e)
        lhs=m(t,xy,f)
        yz=m(t-b,e-b,f-b)
        rhs=m(b,a,b+yz)
        if lhs==rhs:
            raw+=1; blocks[label]+=1
    return 3*raw,{k:3*v for k,v in blocks.items()}

def mult_x21(x,p,q):
    A=x[:9]; B=x[9:18]; d=x[18:21]
    r1,c1=p; r2,c2=q
    if r1==r2:
        if c1==c2: return (r1,(r1+d[(c1-r1)%3])%3)
        return (r1,comp(c1,c2))
    b=(r2-r1)%3; a=(c1-r1)%3; e=(c2-r1)%3
    val=(A if b==1 else B)[3*a+e]
    return (r1,(r1+val)%3)

def assoc_direct_x21(x):
    c=0
    for p,q,r in product(M, repeat=3):
        if mult_x21(x,mult_x21(x,p,q),r)==mult_x21(x,p,mult_x21(x,q,r)):
            c+=1
    return c

def vec18_from_x21(x):
    A=x[:9]; B=x[9:18]
    out=[]
    for c1 in S:
        for r2 in (1,2):
            for c2 in S:
                out.append((A if r2==1 else B)[3*c1+c2])
    return out

def s(vals): return ''.join(str(v) for v in vals)

witnesses={
    "previous_search_min63":[2,1,0,2,1,0,2,1,0,0,0,1,0,2,1,0,0,1,1,0,0],
    "previous_search_max597":[1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,0,1,1,1,1,1],
    "solver_found_min63":[0,1,0,2,1,0,0,1,0,0,2,1,0,2,1,0,2,1,1,0,0],
    "solver_found_max597":[2,0,2,0,2,0,0,2,0,2,2,0,0,0,2,0,0,2,0,0,0],
}
# Note: previous_search vectors above are x21 from known A/B/d in prior summaries.
res={}
for name,x in witnesses.items():
    am,blocks=assoc_master_x21(x)
    ad=assoc_direct_x21(x)
    expected = 63 if "min63" in name else 597
    assert am == ad == expected, (name, am, ad, expected)
    res[name]={
        "x21": ''.join(map(str,x)),
        "A": s(x[:9]),
        "B": s(x[9:18]),
        "d": s(x[18:21]),
        "vec18": s(vec18_from_x21(x)),
        "assoc_master": am,
        "assoc_direct": ad,
        "raw_master_terms": am//3,
        "blocks": blocks,
        "master_direct_agree": am==ad,
    }
print(json.dumps(res, indent=2, sort_keys=True))
print("All f3 witness checks passed.")
