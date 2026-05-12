# Layer 1H controlled frontier theorem package

**Version:** v0.5 / level-2.5 final controlled package.

## Theorem H1 — normalized master formula

For every Layer 1 normal-form point

\[
(A,B,d)\in S^{18}\times S^3,
\]

the hidden continuation contrast satisfies

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)}.
\]

Here \(rawH\) is the normalized \(3^7=2187\)-term four-point sum over

\[
b,t,u,a,e,f,\ell\in S.
\]

The factor \(6=3\cdot2\) consists of the free \(\sigma\)-orbit normalization and the Hilbert--Schmidt basis-map factor.

## Theorem H2 — controlled exact range

The exact controlled strata give:

| stratum | points | range of \(H_{tot}\) | pure max |
|---|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | \([1836,7302]\) | 7020 |
| affine \(\times\Delta\) | 19,683 | \([-2268,7302]\) | 7020 |
| degree \(\le2\) \(\times\Delta\) | 14,348,907 | \([-2268,7302]\) | 7020 |

Thus on all three controlled strata:

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

## Theorem H3 — signed frontier structure

The raw controlled maximum has

\[
H_{tot}=7302,
\qquad
H_+=7308,
\qquad
H_-=6,
\qquad
N_-=3.
\]

The pure frontier has

\[
H_{tot}=7020,
\qquad
H_+=7020,
\qquad
H_-=0,
\qquad
N_-=0.
\]

Therefore the controlled transition \(7020\to7302\) uses a small local negative tail. Term signatures localize the negative tail to the RRR block.

The controlled minimum \(-2268\) splits into two signed-spectrum classes:

\[
(Assoc,H_+,H_-,N_-)=(81,972,3240,288),
\]

and

\[
(Assoc,H_+,H_-,N_-)=(189,1404,3672,432).
\]

## Theorem H4 — local shell geometry

Exact Hamming radius-1 and radius-2 shells around PAB, row-complement, H-min classes, H-max, and global Assoc endpoints show:

- PAB and row-complement have radius-1 neighbors with \(H_{tot}=7302\).
- Their radius-2 shell is entirely below \(7020\).
- H-max \(7302\) is a radius-2 cap: no radius-2 shell point reaches \(7302\).
- H-min \(-2268\) is a strict local minimum through radius 2 for both signed classes.

## Certificate stack

The package is verified by:

```bash
python3 -S scripts/h_master_formula_verify.py
python3 -S scripts/h_frontier_signatures.py
python3 -S scripts/h_local_shells.py
python3 -S scripts/verify_layer1H_final.py
```

The final verifier checks the master formula, controlled exact ranges, signed-spectrum consistency, frontier term signatures, and local shells.

## Status

This is a controlled theorem package. The global \(\Omega'\) H-range and global pure-frontier theorem remain future certification problems.
