# Layer 1H — hidden continuation contrast

**Version:** v0.5, level-2.5 final controlled theorem package.

**Role.** This module adds an operator-lifted four-point landscape observable to the Layer 1 normal form

\[
(A,B,d),\qquad A,B:S^2\to S,\qquad d\in S^3.
\]

It is a Layer 1 landscape extension: the observable uses left regular operators as a measuring device, but it is computed over points of

\[
\Omega'\cong S^{18}\times S^3.
\]

---

## 0. Executive summary

For a finite magma \((M,\cdot)\), define left regular operators

\[
L_x e_y=e_{x\cdot y}.
\]

For \((x,y,z)\in M^3\), set

\[
\mathcal I(x,y,z)=\|L_{x\cdot y}L_z-L_xL_{y\cdot z}\|_{HS}^2,
\]

\[
\mathcal B(x,y,z)=\|L_{(x\cdot y)\cdot z}-L_{x\cdot(y\cdot z)}\|_{HS}^2,
\]

\[
\boxed{\mathcal H(x,y,z)=\mathcal I(x,y,z)-\mathcal B(x,y,z).}
\]

The current certified master formula is

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)}
\]

with \(3^7=2187\) normalized four-point terms.

Controlled exact strata:

| stratum | points | \(H_{min}\) | \(H_{max}\) | pure count | max pure \(H\) | \(H>7020\) | \(H\ge7020\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | 1836 | 7302 | 159 | 7020 | 12 | 18 |
| affine \(\times\Delta\) | 19,683 | -2268 | 7302 | 723 | 7020 | 12 | 18 |
| total-degree \(\le2\) polynomial \(\times\Delta\) | 14,348,907 | -2268 | 7302 | 3,177 | 7020 | 12 | 18 |

Thus the controlled frontier statement is verified on three exact strata:

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

The exact degree \(\le2\) pass found no point below \(-2268\) and no point above \(7302\).

---

## 1. Four-point combinatorial form

For basis maps,

\[
\|T_f-T_g\|_{HS}^2=2\#\{w:f(w)\ne g(w)\}.
\]

Therefore

\[
\frac12\mathcal I(x,y,z)=\#\{w:(xy)(zw)\ne x((yz)w)\},
\]

\[
\frac12\mathcal B(x,y,z)=\#\{w:((xy)z)w\ne (x(yz))w\},
\]

and

\[
\frac12\mathcal H(x,y,z)=D_I(x,y,z)-D_B(x,y,z).
\]

The total invariants are

\[
I_{tot}=\sum_{x,y,z}\mathcal I(x,y,z),\qquad
B_{tot}=\sum_{x,y,z}\mathcal B(x,y,z),\qquad
H_{tot}=I_{tot}-B_{tot}.
\]

The signed spectrum records

\[
H_+=\sum_{H(x,y,z)>0}H(x,y,z),
\]

\[
H_-=\sum_{H(x,y,z)<0}|H(x,y,z)|,
\]

\[
N_-=\#\{(x,y,z):\mathcal H(x,y,z)<0\}.
\]

So

\[
\boxed{H_{tot}=H_+-H_-.}
\]

---

## 2. Normalized master formula

Use normalized variables

\[
x=(0,a),\qquad y=(b,e),\qquad z=(t,f),\qquad w=(u,\ell).
\]

Let

\[
M_1(a,e)=A(a,e),\qquad M_2(a,e)=B(a,e),
\]

\[
M_0^d(a,e)=
\begin{cases}
d_a,&a=e,\\
-a-e,&a\ne e.
\end{cases}
\]

The normalized continuation mismatch term is

\[
\Phi_I=
\left[
M_t\bigl(M_b(a,e),\,t+M_{u-t}(f-t,\ell-t)\bigr)
\ne
M_b\bigl(a,\,b+M_{u-b}(M_{t-b}(e-b,f-b),\ell-b)\bigr)
\right].
\]

The normalized endpoint-propagation baseline term is

\[
\Phi_B=
\left[
M_u\bigl(M_t(M_b(a,e),f),\ell\bigr)
\ne
M_u\bigl(M_b(a,b+M_{t-b}(e-b,f-b)),\ell\bigr)
\right].
\]

Then

\[
rawH(A,B,d)=
\sum_{b,t,u,a,e,f,\ell\in S}
(\Phi_I-\Phi_B).
\]

There are \(3^7=2187\) normalized terms, and

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d).}
\]

The factor \(6\) is \(2\) from the Hilbert--Schmidt basis-map distance and \(3\) from the free \(\sigma\)-orbit normalization.

The verifier `scripts/h_master_formula_verify.py` checks direct \(9^4\) computation against normalized \(3^7\) computation.

---

## 3. Controlled exact atlas

### 3.1. Column-blind and affine exact strata

| stratum | points | \(H_{min}\) | \(H_{max}\) | pure count | max pure \(H\) | max \(N_-\) |
|---|---:|---:|---:|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | 1836 | 7302 | 159 | 7020 | 108 |
| affine \(\times\Delta\) | 19,683 | -2268 | 7302 | 723 | 7020 | 441 |

The frontier statement on these exact strata is

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

### 3.2. Exact total-degree \(\le2\) polynomial pass

Each of \(A,B:S^2\to S\) is represented by a total-degree \(\le2\) polynomial

\[
c_0+c_a a+c_e e+c_{aa}a^2+c_{ae}ae+c_{ee}e^2.
\]

There are \(3^6=729\) such tables for \(A\), and independently \(729\) for \(B\). With \(27\) diagonals, the exact stratum size is

\[
729^2\cdot27=14,348,907.
\]

The exact degree \(\le2\) result:

| quantity | value |
|---|---:|
| points | 14,348,907 |
| \(H_{min}\) | -2268 |
| \(H_{min}\) count | 8 |
| \(H_{max}\) | 7302 |
| \(H_{max}\) count | 12 |
| pure count \(N_-=0\) | 3,177 |
| max pure \(H_{tot}\) | 7020 |
| max pure count | 6 |
| max \(N_-\) | 468 |
| \(H_{tot}>7020\) | 12 |
| \(H_{tot}\ge7020\) | 18 |
| \(H_{tot}<-2268\) | 0 |
| \(H_{tot}>7302\) | 0 |
| Assoc range in this stratum | 69 to 567 |

Thus

\[
\boxed{\max_{\deg A,\deg B\le2}\{H_{tot}:N_-=0\}=7020}
\]

and

\[
\boxed{-2268\le H_{tot}\le7302}
\]

on the exact total-degree \(\le2\) stratum.

---

## 4. Key witnesses

| witness | Assoc | \(I_{tot}\) | \(B_{tot}\) | \(H_{tot}\) | \(H_+\) | \(H_-\) | \(N_-\) | local min | local max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PAB | 219 | 8904 | 1884 | 7020 | 7020 | 0 | 0 | 0 | 16 |
| row-complement | 219 | 8904 | 1884 | 7020 | 7020 | 0 | 0 | 0 | 16 |
| degree \(\le2\) H-max representative | 195 | 9150 | 1848 | 7302 | 7308 | 6 | 3 | -2 | 18 |
| affine H-min class A | 81 | 9396 | 11664 | -2268 | 972 | 3240 | 288 | -14 | 16 |
| affine H-min class B | 189 | 7452 | 9720 | -2268 | 1404 | 3672 | 432 | -14 | 16 |
| global Assoc-min representative | 63 | 5778 | 4296 | 1482 | 1968 | 486 | 183 | -6 | 18 |
| global Assoc-max representative | 597 | 2616 | 264 | 2352 | 2364 | 12 | 6 | -2 | 12 |

The standard-six table is stored in `tables/H_standard_six.csv` and reproduced by the verifier.

---

## 5. Frontier orbit and signed-class atlas

Effective \(S_3\)-orbit counts:

| locus | points | effective orbits | \(H_{tot}\) |
|---|---:|---:|---:|
| \(H_{tot}=7302\) | 12 | 6 | 7302 |
| \(H_{tot}=-2268\) | 8 | 5 | -2268 |
| \(H_{tot}=7020,N_-=0\) | 6 | 4 | 7020 |

The degree \(\le2\) frontier agrees with the affine frontier at all three controlled loci.

The new v0.4 signed-class compression shows that the negative endpoint has two internal classes:

| locus | points | effective orbits | Assoc | \(I_{tot}\) | \(B_{tot}\) | \(H_{tot}\) | \(H_+\) | \(H_-\) | \(N_-\) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H-max | 12 | 6 | 195 | 9150 | 1848 | 7302 | 7308 | 6 | 3 |
| H-min A | 2 | 1 | 81 | 9396 | 11664 | -2268 | 972 | 3240 | 288 |
| H-min B | 6 | 4 | 189 | 7452 | 9720 | -2268 | 1404 | 3672 | 432 |
| pure frontier | 6 | 4 | 219 | 8904 | 1884 | 7020 | 7020 | 0 | 0 |

This is stored in `tables/H_frontier_locus_class_summary.csv`.

---

## 6. Frontier term signatures

The term-signature pass examines all \(243\) normalized local triples \((b,t,a,e,f)\) across each frontier locus.

Main signature facts:

1. On the pure frontier, no block has a negative local term.
2. On the H-max locus, the local negative tail is confined to RRR.
3. RRS, RSR, SRR and DIST are sign-stable on both H-max and pure-frontier loci.
4. DIST is completely rigid on both H-max and pure-frontier loci: all 54 normalized DIST terms have local value \(16\).

Compact table:

| locus | block | terms | always \(>0\) | always \(=0\) | negative union | local range |
|---|---:|---:|---:|---:|---:|---:|
| H-max | RRR | 27 | 21 | 0 | 6 | \([-2,18]\) |
| H-max | RRS | 54 | 54 | 0 | 0 | \([4,14]\) |
| H-max | RSR | 54 | 54 | 0 | 0 | \([12,16]\) |
| H-max | SRR | 54 | 0 | 54 | 0 | \([0,0]\) |
| H-max | DIST | 54 | 54 | 0 | 0 | \([16,16]\) |
| pure frontier | RRR | 27 | 12 | 0 | 0 | \([0,14]\) |
| pure frontier | RRS | 54 | 54 | 0 | 0 | \([8,12]\) |
| pure frontier | RSR | 54 | 54 | 0 | 0 | \([12,16]\) |
| pure frontier | SRR | 54 | 0 | 54 | 0 | \([0,0]\) |
| pure frontier | DIST | 54 | 54 | 0 | 0 | \([16,16]\) |

This gives the current local mechanism for the controlled frontier:

\[
H_{max}=7302
\]

is obtained by increasing the positive RRR/RSR contribution above the pure frontier while introducing a tiny local negative tail:

\[
H_+=7308,\qquad H_-=6,\qquad N_-=3.
\]

The pure frontier stops at

\[
H_{tot}=7020
\]

with

\[
H_-=0,\qquad N_-=0.
\]

So the controlled frontier phenomenon is visible locally: the extra \(+282\) total units above PAB/pure frontier come together with local signed cancellation concentrated in the RRR block.

Tables:

- `tables/H_frontier_term_signature_summary.csv`
- `tables/H_frontier_local_value_histogram.csv`
- `tables/H_frontier_term_signature_detail.csv`

---

## 7. Local Hamming shells

v0.4 integrates exact radius-1 and radius-2 Hamming shells around seven centers. In the normal \(21\)-coordinate representation:

\[
|\partial_1|=21\cdot2=42,\qquad
|\partial_2|=\binom{21}{2}\cdot 2^2=840.
\]

Summary:

| center | r | center H | min H | mean H | max H | below | equal | above | pure neighbors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PAB | 1 | 7020 | 5604 | 6308.000 | 7302 | 40 | 0 | 2 | 10 |
| PAB | 2 | 7020 | 4524 | 5672.071 | 6924 | 840 | 0 | 0 | 63 |
| row-complement | 1 | 7020 | 5604 | 6308.000 | 7302 | 40 | 0 | 2 | 10 |
| row-complement | 2 | 7020 | 4524 | 5672.071 | 6924 | 840 | 0 | 0 | 63 |
| H-min A, Assoc 81 | 1 | -2268 | -1398 | -1278.000 | -954 | 0 | 0 | 42 | 0 |
| H-min A, Assoc 81 | 2 | -2268 | -1458 | -449.657 | 384 | 0 | 0 | 840 | 0 |
| H-min B, Assoc 189 | 1 | -2268 | -1830 | -1259.429 | -624 | 0 | 0 | 42 | 0 |
| H-min B, Assoc 189 | 2 | -2268 | -1560 | -452.286 | 468 | 0 | 0 | 840 | 0 |
| H-max | 1 | 7302 | 5688 | 6563.714 | 7302 | 41 | 1 | 0 | 5 |
| H-max | 2 | 7302 | 4554 | 5908.329 | 6924 | 840 | 0 | 0 | 51 |
| Assoc-min 63 | 1 | 1482 | 288 | 1960.714 | 2934 | 7 | 0 | 35 | 0 |
| Assoc-min 63 | 2 | 1482 | -6 | 2331.143 | 3870 | 129 | 1 | 710 | 0 |
| Assoc-max 597 | 1 | 2352 | 1830 | 2548.571 | 3420 | 18 | 0 | 24 | 0 |
| Assoc-max 597 | 2 | 2352 | 1296 | 2656.200 | 4464 | 263 | 4 | 573 | 2 |

Interpretation:

- PAB/pure frontier is not a raw local H-maximum: radius 1 has two \(7302\) neighbors.
- H-max \(7302\) is a radius-2 strict cap: no radius-2 neighbor reaches it.
- H-min \(-2268\) is strict in both radius 1 and radius 2 for both signed classes.
- Assoc extrema remain far from H-extrema.

Tables:

- `tables/H_center_profiles.csv`
- `tables/H_local_shell_summary.csv`
- `tables/H_local_shell_H_histogram.csv`
- `tables/H_local_shell_extreme_examples.csv`

---

## 8. Structural reading

The controlled exact data now supports the following working structural reading.

### 8.1. Stable high-H skeleton

Both pure-frontier and raw H-max loci share a stable high-H skeleton:

\[
H_{RRS}=1512,
\qquad
H_{SRR}=0,
\qquad
H_{DIST}=2592.
\]

The two main differences are:

\[
H_{RRR}:756\to930,
\]

\[
H_{RSR}:2160\to2268.
\]

This accounts for a positive lift of \(288\), while H-max pays \(6\) units of negative signed cancellation:

\[
7308-6=7302.
\]

### 8.2. Pure frontier mechanism

The pure frontier is the high-H locus with a zero negative tail:

\[
H_-=0,\qquad N_-=0.
\]

The current exact data show that, on the controlled strata, increasing beyond \(7020\) forces a local negative term. In the H-max locus this negative term is small and localized:

\[
h_{loc}^{min}=-2,\qquad N_-=3,
\]

and appears only in RRR.

### 8.3. Negative endpoint mechanism

The H-min endpoint has two signed-spectrum classes. Both have

\[
H_{tot}=-2268,
\]

but class A has

\[
(Assoc,H_+,H_-,N_-)=(81,972,3240,288),
\]

whereas class B has

\[
(Assoc,H_+,H_-,N_-)=(189,1404,3672,432).
\]

Thus the same total \(H\)-minimum is achieved by two different signed-cancellation profiles. This is why \((H_+,H_-,N_-)\) should remain part of the Layer 1H atlas.

---


## 9. Controlled frontier theorem package

This section compresses the current Layer 1H result into a theorem-style package.

### Theorem H1. Master formula

For every point 

\[
(A,B,d)\in S^{18}\times S^3
\]

in the Layer 1 normal form,

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)}
\]

where \(rawH\) is the \(3^7\)-term normalized four-point sum from §2.

**Proof sketch.** The operator definitions are reduced to basis-map mismatch counts by

\[
\|T_f-T_g\|_{HS}^2=2\#\{w:f(w)\neq g(w)\}.
\]

This turns \(\mathcal I\) and \(\mathcal B\) into four-point indicator sums. The diagonal \(\sigma\)-action on \((x,y,z,w)\in M^4\) has three normalized representatives after fixing the first row coordinate of \(x\) to zero, giving the free \(\sigma\)-orbit factor \(3\). The Hilbert--Schmidt mismatch contributes the factor \(2\). Hence the total scaling is \(6=3\cdot2\). The script `h_master_formula_verify.py` checks the formula against direct \(9^4\) computation on standard-six, frontier, and random/representative points.

### Theorem H2. Controlled exact range and pure frontier

On the three controlled exact strata

\[
\text{column-blind}\times\Delta,
\qquad
\text{affine}\times\Delta,
\qquad
\deg A,\deg B\le2,
\]

the following statements hold:

\[
\boxed{H_{tot}\in[1836,7302]}
\]

on `column-blind × Δ`, and

\[
\boxed{H_{tot}\in[-2268,7302]}
\]

on both `affine × Δ` and `degree ≤2 × Δ`.

Moreover, on all three controlled strata,

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

The pure frontier locus is represented by PAB and its row-complement orbit family:

\[
H_{tot}=7020,
\qquad
H_+=7020,
\qquad
H_-=0,
\qquad
N_-=0.
\]

**Proof status.** Exact enumeration. The largest controlled pass is

\[
729^2\cdot27=14,348,907
\]

points for total-degree \(\le2\) polynomial \((A,B)\). The final verifier checks the recorded tables and signed-spectrum identities.

### Theorem H3. Frontier signed structure

The controlled raw maximum

\[
H_{tot}=7302
\]

has signed profile

\[
H_+=7308,
\qquad
H_-=6,
\qquad
N_-=3.
\]

Thus the transition from the pure frontier value \(7020\) to the raw controlled maximum \(7302\) occurs through a small local negative tail. The frontier term-signature table localizes this tail to the RRR block.

The controlled minimum

\[
H_{tot}=-2268
\]

has two signed-spectrum classes:

\[
(Assoc,H_+,H_-,N_-)=(81,972,3240,288),
\]

and

\[
(Assoc,H_+,H_-,N_-)=(189,1404,3672,432).
\]

Thus \(H_{tot}\) alone does not fully describe the frontier; the signed spectrum \((H_+,H_-,N_-)\) is part of the invariant atlas.

### Theorem H4. Local shell geometry

Exact radius-1 and radius-2 Hamming shells around the named centers show:

\[
\text{PAB has radius-1 neighbors at }H_{tot}=7302,
\]

but its entire radius-2 shell is below \(7020\). The controlled H-max point \(H_{tot}=7302\) is a radius-2 cap: no radius-2 point reaches \(7302\).

The H-min classes at \(-2268\) are strict local minima through radius 2 in the tested shells.

### Reading of the controlled theorem package

Layer 1H now records a stable controlled phenomenon:

\[
\boxed{
\text{high pure continuation contrast stops at }7020,
\text{ while }7302\text{ requires local signed cancellation.}
}
\]

This is the useful mathematical content of the H-extension at level 2.5.

---
## 10. Artifact map

| path | role |
|---|---|
| `Layer1H.md` | this module text |
| `README.md` | compact run instructions |
| `scripts/h_core.py` | dependency-free master formula, direct checker, normal-form utilities |
| `scripts/h_master_formula_verify.py` | direct \(9^4\) vs normalized \(3^7\) smoke verifier |
| `scripts/h_frontier_signatures.py` | frontier term-signature generator |
| `scripts/h_local_shells.py` | exact radius-1/radius-2 shell generator |
| `scripts/h_degree2_aggregate_chunks.py` | aggregates exact degree ≤2 chunk outputs into final frontier tables |
| `scripts/h_generate_controlled_atlas_batch.py` | batch NumPy controlled-atlas generator |
| `scripts/h_degree2_targeted.cpp` | exact degree \(\le2\) polynomial C++ scanner with offset/limit |
| `scripts/verify_layer1H_final.py` | level-2.5 final verifier |
| `tables/H_standard_six.csv` | standard-six reproduction |
| `tables/H_column_blind_all_diags.csv` | exact column-blind \(\times\Delta\) atlas |
| `tables/H_affine_all_diags.csv` | exact affine \(\times\Delta\) atlas |
| `tables/H_controlled_summary.csv` | controlled-strata summary |
| `tables/H_key_witnesses.csv` | key witnesses |
| `tables/H_degree2_exact_summary.csv` | exact degree \(\le2\) summary |
| `tables/H_degree2_frontier_loci.csv` | exact degree \(\le2\) frontier points |
| `tables/H_degree2_frontier_orbits.csv` | exact degree \(\le2\) frontier orbit atlas |
| `tables/H_frontier_locus_class_summary.csv` | signed-class compression of frontier loci |
| `tables/H_frontier_term_signature_summary.csv` | block-level frontier term signatures |
| `tables/H_frontier_local_value_histogram.csv` | local H-value histograms on frontier |
| `tables/H_frontier_term_signature_detail.csv` | normalized term-level signatures |
| `tables/H_center_profiles.csv` | shell center profiles |
| `tables/H_local_shell_summary.csv` | exact local shell summary |
| `tables/H_local_shell_H_histogram.csv` | local shell H histograms |
| `tables/H_local_shell_extreme_examples.csv` | shell extremal examples |
| `tables/H_status_registry.csv` | status registry |
| `Layer1H_controlled_frontier_theorem.md` | theorem-style compression of the level-2.5 result |
| `Layer1H_appendix_for_layer1_v3.md` | compact appendix patch for the main Layer 1 v3 text |

---

## 11. Verifier commands

From this directory:

```bash
python3 -S scripts/h_master_formula_verify.py
python3 -S scripts/h_frontier_signatures.py
python3 -S scripts/h_local_shells.py
python3 -S scripts/verify_layer1H_final.py
```

The final verifier checks:

1. PAB \(H_{tot}=7020\);
2. direct \(9^4\) vs normalized \(3^7\) consistency;
3. standard-six reproduction;
4. exact column-blind and affine ranges;
5. exact degree \(\le2\) polynomial pass;
6. purity frontier on controlled strata;
7. signed-spectrum consistency \(H_{tot}=H_+-H_-\);
8. frontier term signatures;
9. local-shell integration.

---

## 12. Status registry

| claim | status | support |
|---|---|---|
| Operator definition of \(\mathcal I,\mathcal B,\mathcal H\) | [V] | finite-magma definition |
| Four-point combinatorial form | [V] | basis-map HS norm identity |
| Isomorphism invariance of totals | [V] | permutation conjugation |
| Normalized master formula \(H_{tot}=6rawH\) | [V-computational] | direct vs normalized verifier |
| PAB \(H_{tot}=7020\) | [V] | `verify_layer1H_final.py` |
| Column-blind \(\times\Delta\) range \([1836,7302]\) | [V-exact enumeration] | 243 points |
| Affine \(\times\Delta\) range \([-2268,7302]\) | [V-exact enumeration] | 19,683 points |
| Degree \(\le2\) polynomial range \([-2268,7302]\) | [V-exact enumeration] | 14,348,907 points |
| Controlled purity frontier \(\max\{H_{tot}:N_-=0\}=7020\) | [V-exact enumeration] | column-blind, affine, degree \(\le2\) |
| Frontier signed-class split | [V-computational] | `H_frontier_locus_class_summary.csv` |
| Frontier term signatures | [V-computational] | `H_frontier_term_signature_summary.csv` |
| Radius-1/radius-2 local shell integration | [V-exact enumeration] | `H_local_shell_summary.csv` |
| Full global H-range on \(\Omega'\) | [Open] | requires separate certificate |
| Full global pure-frontier theorem | [Open] | requires separate certificate |
| Full H distribution \(Z_H\) or joint \((I,B,H,N_-)\) distribution | [Open] | future census/certificate |

---

## 13. Current open extensions

1. Global H-range certificate on \(\Omega'\): decide whether any point has \(H_{tot}<-2268\) or \(H_{tot}>7302\).
2. Global pure-frontier theorem on \(\Omega'\): decide whether \(\max\{H_{tot}:N_-=0\}=7020\) globally.
3. Full distribution \(Z_H(q)\) or joint distribution \((I,B,H,N_-)\).
4. Full hand proof of the global H-frontier, beyond controlled strata.
5. Relation of H-frontier stability to the Assoc proof-obligation structure in Layer 1 v3.
