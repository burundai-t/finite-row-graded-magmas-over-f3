# Stage 6 — Global hidden-continuation frontier

Draft v1 for manuscript-level integration.

This version separates Stage 6 into two manuscript units.

```text
Part I  -> Layer 1: landscape of the family
Part II -> Layer 2: two-candidate application
```

---

# Part I. Landscape theorem package

## 1. Global hidden-continuation problem on \(\Omega'\)

Let
\[
S=\mathbb F_3,
\qquad
\Omega'=S^{21}
\]
be the Stage-6 normal-form landscape. A point
\[
x\in\Omega'
\]
encodes the two cross-row column tables and the same-point diagonal data in the usual normal coordinates.

The hidden-continuation observable is the signed contrast
\[
\mathcal H=\mathcal I-\mathcal B.
\]
For a completed normal-form point \(x\), write
\[
H_{tot}(x)
=H_{RRR}(x)+H_{RRS}(x)+H_{RSR}(x)+H_{SRR}(x)+H_{DIST}(x).
\]
Stage 6 uses the exact normalization
\[
\boxed{
H_{tot}(x)=6\,rawH(x).
}
\]
The local decomposition is indexed by
\[
q=(b,t,a,e,f)\in S^5.
\]
For each \(q\), let \(h_q(x)\) denote the local hidden-continuation contribution. The signed local defect count is
\[
\boxed{
N_-(x)=3\,\#\{q\in S^5:h_q(x)<0\}.
}
\]
Thus the pure hidden-continuation condition is the finite local system
\[
\boxed{
N_-(x)=0
\quad\Longleftrightarrow\quad
h_q(x)\ge0\quad(q\in S^5).
}
\]
Since
\[
|S^5|=3^5=243,
\]
purity is a finite system of \(243\) local inequalities.

---

## 2. Local distance reduction

For a completed normal-form point \(x\), let \(M_s\) denote the Stage-6 local table read. The tables \(M_1\) and \(M_2\) are the two cross-row tables, while \(M_0\) is the same-row diagonal/complement rule.

For
\[
q=(b,t,a,e,f)\in S^5,
\]
define
\[
xy=M_b(a,e),
\qquad
 yz=M_{t-b}(e-b,f-b),
\]
\[
z_R=b+yz,
\qquad
 ep_L=M_t(xy,f),
\qquad
 ep_R=M_b(a,z_R).
\]
Define the left-translation signature
\[
L_c(u,\ell)=M_u(c,\ell)
\]
and its Hamming distance
\[
D_L(c,c')=d(L_c,L_{c'}).
\]
Define the continuation signature
\[
C_{s,\alpha,z}(u,\ell)
=
M_s\!\left(
\alpha,
       s+M_{u-s}(z-s,\ell-s)
\right)
\]
and the continuation-signature distance
\[
D_C(s,\alpha,z;s',\alpha',z')
=
 d(C_{s,\alpha,z},C_{s',\alpha',z'}).
\]

The Stage-6 local contribution satisfies the exact identity
\[
\boxed{
h_q
=
2\left(
D_C(t,xy,f;b,a,z_R)-D_L(ep_L,ep_R)
\right).
}
\]
Consequently,
\[
rawH(x)=\sum_{q\in S^5}\frac{h_q(x)}2,
\qquad
H_{tot}(x)=6\,rawH(x)=3\sum_{q\in S^5}h_q(x).
\]

This is the symbolic reduction behind the global theorem. The remaining statements are exact finite consequences of this reduction.

---

## 3. Theorem 6.1. Global hidden-continuation frontier of \(\mathcal H\)

For every normal-form point \(x\in\Omega'\), the following assertions hold.

### 3.1. Unrestricted global range

The exact unrestricted range of \(H_{tot}\) on \(\Omega'\) is
\[
\boxed{
\min_{x\in\Omega'}H_{tot}(x)=-2268,
\qquad
\max_{x\in\Omega'}H_{tot}(x)=7302.
}
\]
Equivalently,
\[
\boxed{
\min_{x\in\Omega'}rawH(x)=-378,
\qquad
\max_{x\in\Omega'}rawH(x)=1217.
}
\]
Both endpoints are attained. The lower endpoint has multiplicity \(8\), and the upper endpoint has multiplicity \(12\).

One minimum witness is
\[
012120201012120201012,
\]
with
\[
rawH=-378,
\qquad
H_{tot}=-2268,
\qquad
N_-=432.
\]
One maximum witness is
\[
000000000111111111220,
\]
with
\[
rawH=1217,
\qquad
H_{tot}=7302,
\qquad
N_-=3.
\]

### 3.2. Pure global frontier

The pure hidden-continuation frontier is
\[
\boxed{
\max_{x\in\Omega'}\{H_{tot}(x):N_-(x)=0\}=7020.
}
\]
Equivalently, no pure point satisfies
\[
H_{tot}>7020,
\]
and the value \(7020\) is attained by pure points.

### 3.3. Signed-cancellation layer above the pure frontier

The entire region above the pure frontier is the unrestricted maximum layer:
\[
\boxed{
\{x\in\Omega':H_{tot}(x)>7020\}
=
\{x\in\Omega':H_{tot}(x)=7302\}.
}
\]
This set has exactly \(12\) points. Every point in it is impure and has the same signed local profile:
\[
rawH=1217,
\qquad
H_{tot}=7302,
\qquad
N_-=3,
\]
\[
H_{pos}=7308,
\qquad
H_{\mathrm{neg\_abs}}=6,
\qquad
h_{\mathrm{loc,min}}=-2,
\qquad
h_{\mathrm{loc,max}}=18.
\]
Thus all excess over the pure frontier is concentrated in a twelve-point impure signed-cancellation spike.

---

## 4. Proof of Theorem 6.1

The proof is finite and exact. The analytic part is the local distance identity of Section 2. The global exclusions are certified by exhaustive finite evaluation and by the complete pure-frontier certificate.

### Lemma 6.2. Exact local identity

For every \(x\in\Omega'\) and every \(q=(b,t,a,e,f)\in S^5\),
\[
h_q
=
2\left(
D_C(t,xy,f;b,a,z_R)-D_L(ep_L,ep_R)
\right).
\]
Consequently,
\[
rawH(x)=\sum_{q\in S^5}\frac{h_q(x)}2,
\qquad
H_{tot}(x)=6\,rawH(x)=3\sum_{q\in S^5}h_q(x).
\]

**Proof.** The direct local definition has two nine-term Hamming counts,
\[
d_I(q)=\sum_{(u,\ell)\in S^2}\Phi_I(q,u,\ell),
\qquad
 d_B(q)=\sum_{(u,\ell)\in S^2}\Phi_B(q,u,\ell).
\]
The continuation signatures \(C_{s,\alpha,z}\) encode exactly the nine values compared by \(\Phi_I\), and the left-translation signatures \(L_c\) encode exactly the nine values compared by \(\Phi_B\). Hence
\[
d_I(q)=D_C(t,xy,f;b,a,z_R),
\qquad
 d_B(q)=D_L(ep_L,ep_R).
\]
Since the local form is
\[
h_q=2(d_I(q)-d_B(q)),
\]
the identity follows. Summing over \(S^5\) gives the formulas for \(rawH\) and \(H_{tot}\). \(\square\)

### Lemma 6.3. Pure condition as local inequalities

For every \(x\in\Omega'\),
\[
N_-(x)=0
\quad\Longleftrightarrow\quad
h_q(x)\ge0\quad\text{for all }q\in S^5.
\]
Equivalently,
\[
N_-(x)=0
\quad\Longleftrightarrow\quad
D_C(t,xy,f;b,a,z_R)
\ge
D_L(ep_L,ep_R)
\quad\text{for all }q=(b,t,a,e,f)\in S^5.
\]

**Proof.** By definition,
\[
N_-(x)=3\,\#\{q\in S^5:h_q(x)<0\}.
\]
Therefore \(N_-(x)=0\) exactly when no local term is negative. Substitution of Lemma 6.2 gives the distance-inequality form. \(\square\)

### Lemma 6.4. Unrestricted global range

On the full landscape \(\Omega'=S^{21}\),
\[
\min_{x\in\Omega'}rawH(x)=-378,
\qquad
\max_{x\in\Omega'}rawH(x)=1217.
\]
Equivalently,
\[
\min_{x\in\Omega'}H_{tot}(x)=-2268,
\qquad
\max_{x\in\Omega'}H_{tot}(x)=7302.
\]
The lower endpoint has multiplicity \(8\), and the upper endpoint has multiplicity \(12\).

**Proof.** The exact H1 evaluator enumerates all
\[
|\Omega'|=3^{21}=10460353203
\]
normal-form words. It evaluates \(rawH\), \(H_{tot}=6rawH\), \(N_-\), and the block decomposition through the exact local formula. The run records no witness to either counterexample threshold
\[
rawH\ge1218
\qquad\text{or}\qquad
rawH\le -379.
\]
It also records attained witnesses with \(rawH=-378\) and \(rawH=1217\), with endpoint counts \(8\) and \(12\). Since all \(3^{21}\) points are covered, the range is exact. \(\square\)

### Lemma 6.5. Pure high-\(\mathcal H\) exclusion

No pure point satisfies
\[
H_{tot}(x)>7020.
\]
Equivalently,
\[
\max_{x\in\Omega'}\{H_{tot}(x):N_-(x)=0\}\le7020.
\]

**Proof.** Since \(H_{tot}=6rawH\) and \(rawH\) is integral,
\[
H_{tot}>7020
\quad\Longleftrightarrow\quad
rawH\ge1171.
\]
By Lemma 6.3, a pure high-\(H\) counterexample must satisfy
\[
h_q\ge0\quad(q\in S^5)
\]
together with
\[
rawH\ge1171.
\]

The interval branch layer first removes nodes whose completions are already pure-impossible or whose sound upper bound is at most \(7020\). The remaining depth-9 live frontier contains \(18540\) nodes. For each live node, the fixed-coordinate assumptions of that node are added to the exact one-hot S6-CERT-IF / S6-RED SMT interface. The query
\[
(h_q\ge0\ \forall q\in S^5)\wedge rawH\ge1171
\]
is certified UNSAT for every one of the \(18540\) live nodes:
\[
18540/18540\ \text{UNSAT},
\qquad
SAT=0,
\qquad
UNKNOWN=0.
\]
Thus no live branch contains a pure completion with \(H_{tot}>7020\). Together with the interval-pruned branches, this covers the full landscape. \(\square\)

### Lemma 6.6. Attainment of the pure frontier

There exist pure points \(x\in\Omega'\) such that
\[
H_{tot}(x)=7020,
\qquad
rawH(x)=1170,
\qquad
N_-(x)=0.
\]
Consequently,
\[
\max_{x\in\Omega'}\{H_{tot}(x):N_-(x)=0\}=7020.
\]

**Proof.** The finite witness check records normal-form words with \(rawH=1170\), \(H_{tot}=7020\), and \(N_-=0\). Lemma 6.5 gives the matching upper bound for all pure points. Hence the pure maximum is exactly \(7020\). \(\square\)

### Lemma 6.7. Signed-cancellation spike above the pure frontier

The region above the pure frontier is exactly the unrestricted maximum layer:
\[
\{x\in\Omega':H_{tot}(x)>7020\}
=
\{x\in\Omega':H_{tot}(x)=7302\}.
\]
It contains exactly \(12\) points. Every point in this set has
\[
rawH=1217,
\qquad
H_{tot}=7302,
\qquad
N_-=3,
\]
\[
H_{pos}=7308,
\qquad
H_{\mathrm{neg\_abs}}=6,
\qquad
h_{\mathrm{loc,min}}=-2,
\qquad
h_{\mathrm{loc,max}}=18.
\]

**Proof.** The signed-cancellation classifier enumerates the full landscape \(\Omega'=S^{21}\), using the exact local quantities \(h_q\). It records every point with
\[
H_{tot}>7020
\quad\Longleftrightarrow\quad
rawH\ge1171.
\]
The classifier returns
\[
high\_points=12,
\qquad
high\_pure\_points=0,
\qquad
high\_impure\_points=12,
\]
and its only high-region pair count is
\[
(rawH,N_-)=(1217,3)
\quad\text{with count }12.
\]
Thus there are no points with intermediate values
\[
1171\le rawH\le1216,
\]
and all points above the pure frontier are exactly the \(12\) unrestricted maximizers from Lemma 6.4. The recorded positive/negative local decomposition gives the stated signed profile. \(\square\)

### Completion of Theorem 6.1

Part 3.1 is Lemma 6.4.

Part 3.2 follows from Lemma 6.5 and Lemma 6.6.

Part 3.3 is Lemma 6.7.

Together these prove the global hidden-continuation frontier theorem on \(\Omega'\). \(\square\)

---

## 5. Certificate and reproducibility record

This subsection records the finite certificate obligations behind Part I. It is intended as a reproducibility layer below the theorem and proof.

### 5.1. Certificate obligations

| theorem component | certificate obligation | artifact / verifier handle |
|---|---|---|
| local identity | direct local formula equals S6-RED distance formula | `S6-RED`, `S6-CERT-IF` |
| unrestricted range | exact full-landscape range scan over \(3^{21}\) words | `h1/raw/`, `verify_stage6_bundle.py --only-h1` |
| pure high-\(H\) exclusion | full depth-9 pure-frontier coverage, \(18540/18540\) UNSAT | `S6-CERT-PACK-FINAL`, `verify_stage6_bundle.py --only-certpack-final` |
| pure frontier attainment | exact evaluation of retained pure-frontier witnesses | `verify_stage6_bundle.py --only-h3` |
| signed-cancellation spike | exact full-landscape signed-cancellation scan | `h4/raw/`, `verify_stage6_bundle.py --only-h4` |

### 5.2. Pure-frontier certificate

The pure-frontier upper bound is certified by the query
\[
(h_q\ge0\ \forall q\in S^5)\wedge rawH\ge1171.
\]
The depth-9 live frontier has \(18540\) nodes. The final coverage condition is
\[
18540/18540\ \text{certified UNSAT},
\qquad
SAT=0,
\qquad
UNKNOWN=0.
\]

The certified segments are:

| segment | range | certified UNSAT |
|---|---:|---:|
| S6-CERT-PACK-1 | \([0,162)\) | 162 |
| S6-CERT-PACK-2 | \([162,324)\) | 162 |
| S6-CERT-PACK-5 | \([324,972)\) | 648 |
| S6-CERT-PACK-6 | \([972,2268)\) | 1296 |
| S6-CERT-PACK-7 | \([2268,3564)\) | 1296 |
| S6-CERT-PACK-8 | \([3564,4860)\) | 1296 |
| S6-CERT-PACK-9 | \([4860,18540)\) | 13680 |

Thus the full coverage interval is
\[
[0,18540),
\]
with no gap, no overlap, no SAT witness, and no unresolved node.

### 5.3. Unrestricted range certificate

The H1 evaluator covers
\[
|\Omega'|=3^{21}=10460353203
\]
points. It checks the counterexample thresholds
\[
rawH\ge1218
\quad\text{and}\quad
rawH\le -379,
\]
and records no violations. The resulting exact range is
\[
rawH\in[-378,1217],
\qquad
H_{tot}\in[-2268,7302].
\]

Endpoint witnesses:

| endpoint | word | count | rawH | \(H_{tot}\) | \(N_-\) |
|---|---|---:|---:|---:|---:|
| minimum | `012120201012120201012` | 8 | -378 | -2268 | 432 |
| maximum | `000000000111111111220` | 12 | 1217 | 7302 | 3 |

### 5.4. Signed-cancellation certificate

The H4 classifier covers the same full landscape and records the entire region above the pure frontier:
\[
H_{tot}>7020
\quad\Longleftrightarrow\quad
rawH\ge1171.
\]
The final summary is:

```text
checked_points      = 10460353203
high_points         = 12
high_pure_points    = 0
high_impure_points  = 12
pair_counts         = (rawH=1217, N_-=3) -> 12
max_H_tot           = 7302
max_rawH            = 1217
```

The twelve unrestricted maximum witnesses are:

```text
000000000111111111220
000000000111111111221
000000000222222222101
000000000222222222121
111111111000000000220
111111111000000000221
111111111222222222100
111111111222222222200
222222222000000000101
222222222000000000121
222222222111111111100
222222222111111111200
```

Each has
\[
rawH=1217,
\qquad
H_{tot}=7302,
\qquad
N_-=3.
\]

### 5.5. Verifier commands

Run from the bundle directory:

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py
```

Focused theorem checks:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h1
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-certpack-final
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h3
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h4
```

The `--only-certpack-final` command is the focused H2 / pure-frontier
certificate-pack audit.

Raw artifact directories:

```text
h1/raw/
h2/raw/
h4/raw/
```

---

## 6. Landscape interpretation

The global theorem separates two features of \(\mathcal H\).

First, the pure hidden-continuation frontier is
\[
7020.
\]
Second, the unrestricted maximum is
\[
7302.
\]
The difference is not a broad high-\(H\) region. It is exactly a twelve-point impure signed-cancellation spike:
\[
\{H_{tot}>7020\}
=
\{H_{tot}=7302\},
\qquad
|\{H_{tot}>7020\}|=12,
\qquad
N_-=3.
\]
Thus the landscape-level role of \(\mathcal H\) is to distinguish
\[
\text{pure hidden-continuation compatibility}
\]
from
\[
\text{impure signed local cancellation}.
\]

This completes the Layer-1 global hidden-continuation theorem.

---

# Part II. Selection interface

Part II records how the landscape theorem is used after the Layer-2 finite selection chain has already reduced the family to the final two candidates.

The purpose of this part is not to restate the whole global certificate. The certificate belongs to Part I. The purpose here is to say how the theorem participates in the selection narrative.

---

## 7. The two final candidates

After information compression, diagonal compression, nondegenerate anchoring, diagonal idempotence, and local path-dependence, the finite selection chain leaves two normal-form candidates.

The first is
\[
\mathrm{PAB}=111111111222222222000.
\]
In the column-blind notation of the selection layer, its cross-row rule is
\[
h(r_1,r_2)=r_2.
\]

The second is the row-complement candidate, denoted here by
\[
\mathrm{comp}_{r_1r_2}=222222222111111111000.
\]
In the same notation, its cross-row rule is
\[
h(r_1,r_2)=\overline{r_1r_2},
\]
where \(\overline{r_1r_2}\) is the third element of \(S\) distinct from \(r_1\) and \(r_2\) in the nondegenerate cross-row case.

Both candidates are already present before the final pure \(C/J\) criterion is applied.

---

## 8. Corollary 6.8. Position of the final two candidates on the global frontier

The two final candidates satisfy
\[
H_{tot}(\mathrm{PAB})=7020,
\qquad
rawH(\mathrm{PAB})=1170,
\qquad
N_-(\mathrm{PAB})=0,
\]
and
\[
H_{tot}(\mathrm{comp}_{r_1r_2})=7020,
\qquad
rawH(\mathrm{comp}_{r_1r_2})=1170,
\qquad
N_-(\mathrm{comp}_{r_1r_2})=0.
\]
Therefore, by Theorem 6.1,
\[
\boxed{
\mathrm{PAB},\mathrm{comp}_{r_1r_2}
\in
\operatorname{PureFrontier}_{\mathcal H}(\Omega').
}
\]

**Proof.** Direct evaluation of the two normal-form words gives \(rawH=1170\), \(H_{tot}=7020\), and \(N_-=0\) for both. Theorem 6.1 proves that no pure point has \(H_{tot}>7020\). Hence both evaluated candidates lie on the global pure hidden-continuation frontier. \(\square\)

---

## 9. How Theorem 6.1 enters the selection chain

Theorem 6.1 upgrades the hidden-continuation status of the final two candidates from a controlled or local observation to a global landscape statement.

Before Stage 6, the selection layer knew that the two final candidates have the same pure hidden-continuation profile:
\[
H_{tot}=7020,
\qquad
N_-=0.
\]
After Stage 6, the selection layer can say more:
\[
H_{tot}=7020
\]
is not merely a shared computed value for the two candidates. It is the global pure frontier of \(\mathcal H\) on \(\Omega'\).

Thus the role of \(\mathcal H\) in Layer 2 is:

\[
\boxed{
\text{the final two candidates are placed on the global pure hidden-continuation frontier.}
}
\]

The final distinction between the two candidates remains the pure \(C/J\) directed-edge criterion. On the six-point directed-edge set \(M^\times\), the absorption transitions are
\[
\operatorname{AbsTrans}_{PAB}=\{C,J\},
\]
and
\[
\operatorname{AbsTrans}_{comp}=\{C^{-1},C^{-1}J\}.
\]
The selection criterion accepts the undrifted continuation/reversal pair \(\{C,J\}\), and hence selects PAB.

Stage 6 therefore enters the selection story at a specific point:

\[
\text{local path-dependence leaves }
\mathrm{PAB},\mathrm{comp}_{r_1r_2}
\]
\[
\Downarrow
\]
\[
\text{Theorem 6.1 places both on the global pure }\mathcal H\text{-frontier}
\]
\[
\Downarrow
\]
\[
\text{pure }C/J\text{ distinguishes the undrifted candidate.}
\]

---

## 10. Manuscript integration status

The active v14 manuscript has integrated this bundle as Theorem 7.2 in the landscape layer.  The theorem states the unrestricted range, pure frontier, and twelve-point signed-cancellation spike, while Section 21 records the H1/H2/H3/H4 certificate handles.

In the selection layer, the bundle is used for global placement: PAB and row-complement both lie on the pure hidden-continuation frontier.  The final separation remains the pure \(C/J\) directed-edge criterion.

The detailed raw artifacts, chunk logs, and audit commands remain in the separate `mathcal_H/` bundle rather than in the compact manuscript-facing `tables/` corpus.

---

## 11. Replacement summary

The clean two-layer summary is:

\[
\boxed{
\textbf{Layer 1:}
\quad
\min_{\Omega'}H_{tot}=-2268,
\quad
\max_{\Omega'}H_{tot}=7302,
\quad
\max_{N_-=0}H_{tot}=7020.
}
\]

\[
\boxed{
\textbf{Layer 1:}
\quad
\{H_{tot}>7020\}
=
\{H_{tot}=7302\},
\quad
|\{H_{tot}>7020\}|=12,
\quad
N_-=3.
}
\]

\[
\boxed{
\textbf{Layer 2:}
\quad
\mathrm{PAB},\mathrm{comp}_{r_1r_2}
\in
\operatorname{PureFrontier}_{\mathcal H}(\Omega'),
\quad
\text{then pure }C/J\text{ selects PAB.}
}
\]
