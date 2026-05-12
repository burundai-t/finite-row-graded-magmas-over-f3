# Layer 3 Front G — companion Lie package on the PAB carrier

**Version:** Layer 3 v1.7 / Front G.  
**Status:** closed as a structural companion package.  
**Role:** describe the Lie-algebraic package naturally carried by the PAB linearization carrier
\[
k[M]\cong \operatorname{Mat}_3(k),
\qquad e_{(r,c)}\leftrightarrow E_{rc}.
\]

Front G follows the positive formulation fixed before starting the front: the goal is to record the structure emitted by the carrier, not to overcorrect into defensive non-claims. The technical boundary is one line:

\[
\mu_{\mathrm{PAB}}\ne \mu_{\mathrm{Mat}},
\]

while both products live on the same matrix-unit carrier. This is enough to keep the package precise.

---

## G.1 Carrier theorem

The selected PAB point has underlying set

\[
M=S\times S,
\qquad S=\mathbb F_3.
\]

Linearization gives

\[
k[M]=\bigoplus_{(r,c)\in M}k e_{(r,c)}.
\]

The row/column indexing gives a canonical matrix-unit carrier

\[
\boxed{
\Xi:k[M]\longrightarrow \operatorname{Mat}_3(k),
\qquad
\Xi(e_{(r,c)})=E_{rc}.
}
\]

This is the carrier on which the companion Lie package lives.

---

## G.2 Matrix companion algebra

On the same carrier define ordinary matrix multiplication and the commutator

\[
[X,Y]=XY-YX.
\]

On matrix units:

\[
\boxed{
[E_{ij},E_{kl}]
=
\delta_{jk}E_{il}-\delta_{li}E_{kj}.
}
\]

The verifier checks this formula for all 81 ordered pairs of matrix units. Therefore the companion Lie algebra is

\[
\boxed{\mathfrak{gl}(3,k).}
\]

The PAB product is a different bilinear product, but its cross-row part is already matrix-coordinate visible:

\[
\mu_{\mathrm{cross}}(A,B)=AJB^\top=(A\mathbf1)(B\mathbf1)^\top.
\]

On basis elements with different rows,

\[
E_{ij}\cdot_{\mathrm{PAB}}E_{kl}=E_{ik}=E_{ij}J E_{kl}^\top,
\qquad i\ne k.
\]

Thus the matrix carrier is not ornamental: it expresses an actual PAB multiplication sector.

---

## G.3 Central plus adjoint split

Let

\[
I=E_{00}+E_{11}+E_{22}.
\]

Then

\[
\boxed{
\mathfrak{gl}(3,k)=kI\oplus\mathfrak{sl}(3,k).
}
\]

The center is the one-dimensional trivial adjoint module:

\[
[kI,\mathfrak{gl}(3,k)]=0.
\]

The traceless sector is eight-dimensional:

\[
\dim\mathfrak{sl}(3,k)=8.
\]

Therefore the matrix carrier has the companion adjoint decomposition

\[
\boxed{
k[M]=\mathbf1\oplus\mathbf8.
}
\]

Here \(\mathbf1=kI\), and \(\mathbf8=\mathfrak{sl}(3,k)\) under the companion commutator action.

---

## G.4 Compatibility with the PAB automorphism group

For every permutation \(\rho\in S_3\), simultaneous relabeling acts by

\[
(r,c)\mapsto(\rho(r),\rho(c)).
\]

On the matrix carrier this is conjugation by the permutation matrix \(P_\rho\):

\[
E_{rc}\mapsto E_{\rho(r),\rho(c)}=P_\rho E_{rc}P_\rho^{-1}.
\]

The verifier checks both compatibilities:

\[
\rho(x\cdot_{\mathrm{PAB}}y)=\rho(x)\cdot_{\mathrm{PAB}}\rho(y),
\]

and

\[
[P_\rho XP_\rho^{-1},P_\rho YP_\rho^{-1}]
=
P_\rho[X,Y]P_\rho^{-1}.
\]

Thus the same \(S_3\) relabeling symmetry is visible in both the PAB product and the companion Lie bracket.

---

## G.5 The selected compact three-dimensional sector

Inside \(\mathfrak{sl}(3,\mathbb R)\), define

\[
\boxed{
\mathfrak{so}(3)
=
\operatorname{span}\{E_{01}-E_{10},\ E_{02}-E_{20},\ E_{12}-E_{21}\}.
}
\]

This sector is:

1. three-dimensional;
2. closed under the commutator;
3. stable under simultaneous \(S_3\)-relabeling;
4. Killing-negative with
   \[
   B(X,Y)=6\operatorname{tr}(XY),
   \qquad
   B|_{\mathfrak{so}(3)}=-12 I_3
   \]
   in the displayed basis.

The symmetric traceless complement is

\[
\mathfrak p=
\{X\in\mathfrak{sl}(3,\mathbb R):X^\top=X\}.
\]

The Cartan split is

\[
\boxed{
\mathfrak{sl}(3,\mathbb R)=\mathfrak{so}(3)\oplus\mathfrak p,
\qquad
\dim\mathfrak{so}(3)=3,
\quad
\dim\mathfrak p=5.
}
\]

The bracket relations are verified:

\[
[\mathfrak{so}(3),\mathfrak{so}(3)]\subseteq\mathfrak{so}(3),
\]

\[
[\mathfrak{so}(3),\mathfrak p]\subseteq\mathfrak p,
\]

\[
[\mathfrak p,\mathfrak p]\subseteq\mathfrak{so}(3).
\]

---

## G.6 Compact Lie group type

The companion carrier therefore gives the compact Lie package:

\[
\boxed{
SU(3)\times SU(2)\times U(1).
}
\]

The three factors are attached as follows:

| component | Lie algebra piece | compact group type |
|---|---|---|
| traceless companion algebra | \(\mathfrak{sl}(3)\) | \(SU(3)\) |
| selected compact 3D sector | \(\mathfrak{so}(3)\), simply-connected cover \(\mathfrak{su}(2)\) | \(SU(2)\) |
| center | \(\mathfrak u(1)\) | \(U(1)\) |

This is a statement about the compact Lie group type canonically attached to the companion matrix/Lie package on \(k[M]\). It is not a physical identification; it is the exact Lie-theoretic type visible in the carrier.

---

## G.7 Operation boundary and positive interpretation

The right interpretation is:

\[
\boxed{
\text{PAB exposes a canonical }3\times3\text{ matrix-unit carrier, and this carrier carries the companion Lie package.}
}
\]

The boundary is:

\[
\boxed{
\text{PAB does not need to equal matrix multiplication in order to expose the matrix/Lie companion package.}
}
\]

The bridge facts are concrete:

* the same basis \(E_{rc}\) carries both structures;
* simultaneous \(S_3\)-relabeling acts correctly for both PAB and the bracket;
* cross-row PAB is exactly \(AJB^\top\) on matrix units;
* PAB and ordinary matrix multiplication coincide on exactly nine basis pairs;
* the companion commutator yields \(\mathfrak{gl}(3)\), \(\mathfrak{sl}(3)\), \(\mathfrak{so}(3)\), \(1\oplus8\), and the compact group type \(SU(3)\times SU(2)\times U(1)\).

---

## G.8 Verifier summary

The Front G verifier checks:

```text
Layer 3 Front G verifier: PASS
  carrier: k[M] identified with Mat3 matrix units; bracket structure constants checked
  decomposition: gl3 = kI + sl3 and adjoint carrier split 1+8 checked
  S3 compatibility: simultaneous relabeling preserves PAB, bracket, so3, and p
  compact sector: so3 is S3-stable, Killing-negative, and Cartan split sl3=so3+p checked
  companion group type: SU(3) x SU(2) x U(1) recorded as the compact Lie package
  boundary: PAB and matrix multiplication share the carrier; cross-row AJB^T and 9 basis coincidences checked
```

Generated tables:

```text
tables/layer3_frontG_lie_carrier_basis.csv
tables/layer3_frontG_bracket_structure_constants.csv
tables/layer3_frontG_decomposition_summary.csv
tables/layer3_frontG_s3_equivariance_audit.csv
tables/layer3_frontG_cartan_decomposition_audit.csv
tables/layer3_frontG_killing_form_audit.csv
tables/layer3_frontG_carrier_compatibility_audit.csv
tables/layer3_frontG_matrix_product_coincidences.csv
tables/layer3_frontG_compact_group_package.csv
tables/layer3_frontG_status_registry.csv
tables/layer3_frontG_table_manifest.csv
tables/layer3_frontG_verifier_checks.csv
```

---

## G.9 Status after Front G

Closed:

\[
\boxed{k[M]\cong\operatorname{Mat}_3(k)\text{ as canonical matrix carrier}.}
\]

\[
\boxed{\mathfrak{gl}(3)=kI\oplus\mathfrak{sl}(3),\qquad k[M]=\mathbf1\oplus\mathbf8.}
\]

\[
\boxed{\mathfrak{sl}(3,\mathbb R)=\mathfrak{so}(3)\oplus\mathfrak p,
\quad \mathfrak{so}(3)\text{ compact and }S_3\text{-stable}.}
\]

\[
\boxed{\text{companion compact group type }SU(3)\times SU(2)\times U(1).}
\]

Front G therefore closes the companion Lie package block of Layer 3.
