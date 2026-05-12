# Layer 3 Front F — hidden continuation contrast through the operator envelope

**Version:** Layer 3 v1.4 / Front F.  
**Purpose:** replace the previous statement
\[
\mathrm{PAB}: H_{tot}=7020,
\qquad H_-=0,
\qquad N_-=0
\]
by an operator-envelope explanation using the composition envelope
\[
\mathcal E=W_0\oplus W_1\oplus W_2
\]
closed in Front B.

The result of Front F is:

\[
\boxed{
\mathcal H\text{ is an internal distance contrast inside the row-target component }W_{\operatorname{row}(x)}.
}
\]

It remains a bridge, not a selector: PAB and the row-complement competitor have the same pure profile at \(d=000\).

---

## 1. Import from Front B

Front B classified the positive composition monoid of the PAB left regular operators:

\[
\operatorname{Mon}^+\langle L_x:x\in M\rangle.
\]

It has

\[
\boxed{|\operatorname{Mon}^+\langle L_x\rangle|=51.}
\]

The linear envelope is

\[
\mathcal E=\operatorname{span}\operatorname{Mon}^+\langle L_x\rangle,
\qquad
\boxed{\dim\mathcal E=27.}
\]

It decomposes by target row:

\[
\boxed{\mathcal E=W_0\oplus W_1\oplus W_2,}
\]

\[
\boxed{\dim W_r=9,}
\]

and the product law is

\[
\boxed{W_rW_s\subseteq W_r.}
\]

Thus every composition of left translations has a well-defined left target row. This is the exact operator infrastructure needed for \(\mathcal H\).

---

## 2. Operator distance form of \(\mathcal H\)

For deterministic basis maps \(T,U:k[M]\to k[M]\), define

\[
d(T,U)=\#\{m\in M:T(e_m)\ne U(e_m)\}.
\]

Since every deterministic basis map has one basis vector in each column,

\[
\boxed{\|T-U\|_{HS}^2=2d(T,U).}
\]

Layer 1H defines

\[
\mathcal I(x,y,z)=
\|L_{xy}L_z-L_xL_{yz}\|_{HS}^2,
\]

\[
\mathcal B(x,y,z)=
\|L_{(xy)z}-L_{x(yz)}\|_{HS}^2,
\]

\[
\mathcal H(x,y,z)=\mathcal I(x,y,z)-\mathcal B(x,y,z).
\]

Put

\[
P(x,y,z)=L_{xy}L_z,
\qquad
Q(x,y,z)=L_xL_{yz},
\]

\[
A(x,y,z)=L_{(xy)z},
\qquad
B(x,y,z)=L_{x(yz)}.
\]

Then

\[
\boxed{
\frac12\mathcal H(x,y,z)
=
 d(P(x,y,z),Q(x,y,z))
-
 d(A(x,y,z),B(x,y,z)).
}
\]

For PAB, all four operators lie in the same row-target component:

\[
\boxed{
P,Q,A,B\in W_{\operatorname{row}(x)}.
}
\]

Therefore \(\mathcal H\) is not merely a landscape count. It is a distance contrast inside the operator envelope:

\[
\boxed{
\mathcal H
=
2\left(
\text{continuation distance in }\mathcal E
-
\text{boundary left-operator distance}
\right).
}
\]

---

## 3. Pointwise dominance theorem for PAB

The Front F verifier checks the finite structural statement:

\[
\boxed{
 d(L_{xy}L_z,L_xL_{yz})
\ge
 d(L_{(xy)z},L_{x(yz)})
\qquad\forall x,y,z\in M.
}
\]

Equivalently,

\[
\boxed{
\mathcal H(x,y,z)\ge0
\qquad\forall x,y,z\in M.
}
\]

Thus the PAB profile is pure:

\[
\boxed{H_-=0,\\ N_-=0.}
\]

The totals are

\[
\boxed{I_{tot}=8904,}
\]

\[
\boxed{B_{tot}=1884,}
\]

\[
\boxed{H_{tot}=I_{tot}-B_{tot}=7020.}
\]

Since all pointwise terms are nonnegative,

\[
\boxed{H_+=7020.}
\]

---

## 4. Row-block decomposition

Use the same five row-pattern blocks as Layer 1:

| block | condition | triples | \(I_{tot}\) | \(B_{tot}\) | \(H_{tot}\) | normalized rawH |
|---|---|---:|---:|---:|---:|---:|
| RRR | \(y,z\) in row of \(x\) | 81 | 804 | 48 | 756 | 126 |
| RRS | \(y\) in row of \(x\), \(z\) external | 162 | 2268 | 756 | 1512 | 252 |
| RSR | \(z\) in row of \(x\), \(y\) external | 162 | 2916 | 756 | 2160 | 360 |
| RSS | \(y,z\) in the same external row | 162 | 0 | 0 | 0 | 0 |
| RST | three distinct rows | 162 | 2916 | 324 | 2592 | 432 |
| total | — | 729 | 8904 | 1884 | 7020 | 1170 |

The last column is compatible with the Layer 1H normalization:

\[
\boxed{H_{tot}=6\,rawH,}
\]

because

\[
6\cdot1170=7020.
\]

---

## 5. Hand-readable block mechanisms

### 5.1. RSS block is zero

Let rows be

\[
\operatorname{row}(x)=r,
\qquad
\operatorname{row}(y)=\operatorname{row}(z)=s\ne r.
\]

Then

\[
xy=(r,s),
\]

and both continuation maps collapse to the same constant map

\[
K_{r,s}.
\]

Also

\[
(xy)z=x(yz)=(r,s).
\]

Hence

\[
\boxed{\mathcal I=\mathcal B=\mathcal H=0}
\]

on all 162 RSS triples.

### 5.2. RST block is pure constant-vs-constant excess

Let

\[
\operatorname{row}(x)=r,
\quad
\operatorname{row}(y)=s,
\quad
\operatorname{row}(z)=t,
\quad
r,s,t\text{ distinct}.
\]

Then

\[
L_{xy}L_z=K_{r,t},
\qquad
L_xL_{yz}=K_{r,s}.
\]

These constants disagree on all 9 basis inputs, so

\[
d_E=9,
\qquad
\mathcal I=18.
\]

The boundary left operators are

\[
L_{(r,t)}
\quad\text{and}\quad
L_{(r,s)}.
\]

Both labels are off-diagonal in the same row, and two off-diagonal left translations in the same row differ on one input:

\[
d_L=1,
\qquad
\mathcal B=2.
\]

Therefore each RST triple contributes

\[
\boxed{\mathcal H=2(9-1)=16.}
\]

There are 162 such triples, hence

\[
162\cdot16=2592.
\]

### 5.3. RSR block

Rows:

\[
\operatorname{row}(x)=\operatorname{row}(z)=r,
\qquad
\operatorname{row}(y)=s\ne r.
\]

The continuation pair is always of type

\[
T\text{-vs-}K
\]

inside \(W_r\), and the Front F audit gives

\[
d_E=9
\]

for every RSR triple.

The boundary distance is controlled by the column of \(z=(r,c_z)\):

| condition | count | \(d_E\) | \(d_L\) | \(\mathcal H\) |
|---|---:|---:|---:|---:|
| \(c_z=r\) | 54 | 9 | 1 | 16 |
| \(c_z=s\) | 54 | 9 | 3 | 12 |
| \(c_z=\overline{rs}\) | 54 | 9 | 3 | 12 |

Thus

\[
54\cdot16+108\cdot12=2160.
\]

### 5.4. RRS block

Rows:

\[
\operatorname{row}(x)=\operatorname{row}(y)=r,
\qquad
\operatorname{row}(z)=t\ne r.
\]

The continuation pair is of type

\[
K\text{-vs-}T
\]

inside \(W_r\). The boundary distance and continuation distance depend on the column of \(x=(r,c_x)\):

| condition | count | \(d_E\) | \(d_L\) | \(\mathcal H\) |
|---|---:|---:|---:|---:|
| \(c_x=r\) | 54 | 5 | 1 | 8 |
| \(c_x=t\) | 54 | 9 | 3 | 12 |
| \(c_x=\overline{rt}\) | 54 | 7 | 3 | 8 |

Therefore

\[
54\cdot8+54\cdot12+54\cdot8=1512.
\]

### 5.5. RRR block

In RRR all three arguments remain in one row fiber. The calculation is completely internal to the six same-row block maps \(\mathcal B_r\) from Front B.

The verified distribution is:

| \(\mathcal I\) | \(\mathcal B\) | \(\mathcal H\) | count |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 3 |
| 2 | 2 | 0 | 12 |
| 4 | 0 | 4 | 12 |
| 12 | 2 | 10 | 12 |
| 14 | 0 | 14 | 42 |

Hence

\[
3\cdot0+12\cdot0+12\cdot4+12\cdot10+42\cdot14=756.
\]

---

## 6. Global distance-type collapse

Across all 729 triples, the operator-envelope normal-form audit collapses the calculation to 93 pair types and then to 9 distance types:

| \(\mathcal I\) | \(\mathcal B\) | \(\mathcal H\) | count | contribution to \(H_{tot}\) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 165 | 0 |
| 2 | 2 | 0 | 12 | 0 |
| 4 | 0 | 4 | 12 | 48 |
| 10 | 2 | 8 | 54 | 432 |
| 12 | 2 | 10 | 12 | 120 |
| 14 | 0 | 14 | 42 | 588 |
| 14 | 6 | 8 | 54 | 432 |
| 18 | 2 | 16 | 216 | 3456 |
| 18 | 6 | 12 | 162 | 1944 |

Summing the last column gives

\[
7020.
\]

This is the operator-envelope explanation of the Layer 1H number.

---

## 7. Guardrail: \(\mathcal H\) does not select PAB

The row-complement competitor

\[
g_{comp}=\overline{r_1r_2}
\]

has the same profile:

\[
\boxed{I_{tot}=8904,\qquad B_{tot}=1884,
\qquad H_{tot}=7020,
\qquad H_-=0,
\qquad N_-=0.}
\]

The exact column-blind \(d=000\) audit gives:

\[
\boxed{
\max\{H_{tot}:N_-=0\}=7020
\text{ on the column-blind }d=000\text{ slice},
}
\]

and the pure-Hmax locus on that slice is exactly

\[
\boxed{
\{g_1=r_2,\\ g_{comp}=\overline{r_1r_2}\}.
}
\]

Therefore \(\mathcal H\) reinforces the same two-point ambiguity that Layer 2 resolves by pure finite \(C/J\):

\[
\boxed{
\mathcal H\text{ is a continuation-purity bridge, not a final selector.}
}
\]

---

## 8. Verifier and generated tables

Run from the package root:

```bash
/usr/bin/python3 scripts/verify_layer3_frontF.py
```

Expected output:

```text
Layer 3 Front F verifier: PASS
  operator envelope: continuation operators L_(xy)L_z and L_xL_(yz) lie in E and in W_row(x)
  distance collapse: 729 triples -> 93 normal-form pair types -> 9 (I,B,H) distance types
  PAB H profile: I_tot=8904, B_tot=1884, H_tot=7020, H_-=0, N_-=0
  row-pattern decomposition: rawH contributions sum to 1170, hence H_tot=6*1170=7020
  guardrail: row-complement has the same H profile, so H is an operator bridge, not a selector
  column-blind d=000 audit: pure H maximum 7020 is attained exactly by PAB and row-complement
```

Generated tables:

- `tables/layer3_frontF_envelope_membership_summary.csv`
- `tables/layer3_frontF_operator_H_block_totals.csv`
- `tables/layer3_frontF_H_value_distribution.csv`
- `tables/layer3_frontF_distance_type_table.csv`
- `tables/layer3_frontF_operator_pair_normal_form_audit.csv`
- `tables/layer3_frontF_row_pattern_decomposition.csv`
- `tables/layer3_frontF_column_blind_d000_H_audit.csv`
- `tables/layer3_frontF_pab_comp_H_guardrail.csv`
- `tables/layer3_frontF_pab_comp_H_comparison.csv`
- `tables/layer3_frontF_pointwise_dominance_audit.csv`
- `tables/layer3_frontF_status_registry.csv`
- `tables/layer3_frontF_verifier_checks.csv`

---

## 9. Status

\[
\boxed{\mathrm{L3\text{-}F}\text{ is closed at the operator-envelope level.}}
\]

Closed:

1. \(\mathcal H\) is expressed as a distance contrast inside \(W_{\operatorname{row}(x)}\).
2. PAB has pointwise nonnegative \(\mathcal H\).
3. \(H_{tot}=7020\) is decomposed through \(\mathcal E\), row blocks, and normal-form pair types.
4. The row-complement guardrail is preserved: same \(H\)-profile, so no false selector claim.

Still open elsewhere:

\[
\boxed{
\max_{\Omega'}\{H_{tot}:N_-=0\}=7020
}
\]

over the full \(\Omega'\). This remains a Layer 1H global certification problem.
