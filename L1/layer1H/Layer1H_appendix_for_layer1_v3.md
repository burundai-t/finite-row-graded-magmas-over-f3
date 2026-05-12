# Appendix H patch for `layer1_landscape_v3.md`

## Appendix H. Hidden continuation contrast \(\mathcal H\)

Layer 1 also admits an operator-lifted four-point landscape observable. For a finite magma \((M,\cdot)\), let

\[
L_xe_y=e_{x\cdot y}.
\]

For triples \((x,y,z)\in M^3\), define

\[
\mathcal I(x,y,z)=\|L_{x\cdot y}L_z-L_xL_{y\cdot z}\|_{HS}^2,
\]

\[
\mathcal B(x,y,z)=\|L_{(x\cdot y)\cdot z}-L_{x\cdot(y\cdot z)}\|_{HS}^2,
\]

\[
\boxed{\mathcal H(x,y,z)=\mathcal I(x,y,z)-\mathcal B(x,y,z).}
\]

The total

\[
H_{tot}=\sum_{x,y,z}\mathcal H(x,y,z)
\]

is an isomorphism invariant. In the Layer 1 normal form \((A,B,d)\in S^{18}\times S^3\), it has a normalized master formula

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)},
\]

where \(rawH\) is a \(3^7\)-term four-point sum.

### Controlled exact results

| stratum | points | range of \(H_{tot}\) | pure max |
|---|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | \([1836,7302]\) | 7020 |
| affine \(\times\Delta\) | 19,683 | \([-2268,7302]\) | 7020 |
| degree \(\le2\) \(\times\Delta\) | 14,348,907 | \([-2268,7302]\) | 7020 |

where pure means

\[
N_- = \#\{(x,y,z):\mathcal H(x,y,z)<0\}=0.
\]

Thus the controlled frontier statement is

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

PAB has

\[
H_{tot}=7020,
\qquad
H_+=7020,
\qquad
H_-=0,
\qquad
N_-=0.
\]

The controlled raw maximum has

\[
H_{tot}=7302,
\qquad
H_+=7308,
\qquad
H_-=6,
\qquad
N_-=3.
\]

The working interpretation is:

\[
\boxed{
\text{high pure continuation contrast stops at }7020,
\text{ while }7302\text{ requires local signed cancellation.}
}
\]

The full global \(\Omega'\) H-range and global pure-frontier theorem remain open certification problems.

### Artifacts

This appendix is backed by the `layer1H_v0_5` package:

```text
Layer1H.md
Layer1H_controlled_frontier_theorem.md
scripts/verify_layer1H_final.py
tables/H_controlled_summary.csv
tables/H_degree2_exact_summary.csv
tables/H_frontier_locus_class_summary.csv
tables/H_frontier_term_signature_summary.csv
tables/H_local_shell_summary.csv
```
