# README_L3 — Layer 3 linearization package, v1.8 final

**Layer:** Layer 3 — linearization of the selected PAB magma.  
**Version:** v1.8 final / Front H.  
**Mode:** cumulative theorem package.

Layer 3 starts after Layer 2 has selected

\[
(g_1,000)=\mathrm{PAB}.
\]

Layer 3 does **not** reselect PAB. It records the linear, operator, binary-term, companion Lie, hidden-continuation, and symplectic-bridge structures carried by the already selected PAB magma.

---

## 1. Final package core

Normalized final layout:

```text
README_L3.md
layer3_linearization_v1_8.md
scripts/
tables/
linearization_steps/
```

If using the uploaded archive names, normalize them before verification:

```bash
unzip scripts3.zip && mv scripts3 scripts
unzip tables3.zip && mv tables3 tables
unzip linearization_steps.zip
```

The verifier stack expects `scripts/` and writes/reads `tables/`.

---

## 2. Closed fronts

```text
L3-A  spectral/Jordan hardening of left translations
L3-B  composition-envelope normal form
L3-C  constant-endomorphism intertwiners
L3-F  hidden continuation contrast through the operator envelope
L3-D  finite binary presentation of PAB term-functions
L3-E  structural compression of T2(PAB)
L3-G  companion Lie package on the PAB carrier
L3-H  geometric bridge from finite pure C/J to signed symplectic realization
```

---

## 3. Main results

| block | final result |
|---|---|
| carrier | \(k[M]\cong\operatorname{Mat}_3(k)\) as vector spaces, with \(e_{(r,c)}\leftrightarrow E_{rc}\) |
| product boundary | PAB multiplication is not ordinary matrix multiplication |
| left regular span | \(\dim\operatorname{span}\{L_x:x\in M\}=9\) |
| rank | \(\operatorname{rank}L_x=3\) for all \(x\in M\) |
| diagonal spectrum | \(\mu_{L_x}(t)=t(t-1)(t+1)\), semisimple |
| off-diagonal spectrum | \(\mu_{L_x}(t)=t^2(t-1)(t+1)\), exactly one \(J_2(0)\) block |
| composition monoid | \(|\operatorname{Mon}^+\langle L_x\rangle|=51\) |
| envelope | \(\mathcal E=W_0\oplus W_1\oplus W_2\), \(\dim W_r=9\), \(\dim\mathcal E=27\), \(W_rW_s\subseteq W_r\) |
| endomorphisms | \(\operatorname{End}(M,\cdot)=6\) automorphisms \(+3\) constants |
| intertwiners | automorphism spaces have dimension \(1\); constant spaces have dimension \(2\); total dimension \(12\) |
| cross-row formula | \(\mu_{\mathrm{cross}}(A,B)=AJB^\top=(A\mathbf1)(B\mathbf1)^\top\) |
| absorption matrix | \(A_{\mathrm{abs}}=(C+J)^\top\), spectrum \(\{2,0,0,0,-1,-1\}\) |
| binary term algebra | \(|T_2(\mathrm{PAB})|=630\) |
| binary compression | \(T_2\cong\{x,y\}\times\mathcal S_{21}\times\mathcal U_{15}\), hence \(630=2\cdot21\cdot15\) |
| hidden continuation | PAB has \(I_{tot}=8904\), \(B_{tot}=1884\), \(H_{tot}=7020\), \(H_-=0\), \(N_-=0\) |
| companion Lie package | \(\mathfrak{gl}(3)=kI\oplus\mathfrak{sl}(3)\), \(k[M]=\mathbf1\oplus\mathbf8\) |
| compact type | \(SU(3)\times SU(2)\times U(1)\) |
| Front H bridge | finite pure \(\{C,J\}\) admits a signed projective dihedral lift in \(Sp(6,\mathbb R)\) |

---

## 4. Front H bridge

Layer 2’s final selector is finite pure directed-edge dynamics:

\[
\operatorname{AbsTrans}_{\mathrm{PAB}}=\{C,J\},
\qquad
C(r,c)=(c,\overline{rc}),
\qquad
J(r,c)=(c,r).
\]

Front H turns this into a geometric bridge. Define

\[
q_i=(i,i+1),
\qquad
p_i=J(q_{-i}).
\]

Then \(C\) preserves the \(q/p\) sectors and \(J\) exchanges them. On

\[
\mathbb R^3_q\oplus\mathbb R^3_p,
\qquad
\Omega=\begin{pmatrix}0&I\\-I&0\end{pmatrix},
\]

the signed lifts are

\[
\widehat C=\begin{pmatrix}R&0\\0&R\end{pmatrix},
\qquad
\widehat J=\begin{pmatrix}0&-P\\P&0\end{pmatrix}.
\]

They satisfy

\[
\widehat C,\widehat J\in Sp(6,\mathbb R),
\qquad
\widehat C^3=I,
\qquad
\widehat J^2=-I,
\qquad
\widehat J\widehat C\widehat J^{-1}=\widehat C^{-1}.
\]

The literal unsigned reversal lift is anti-symplectic; the signed lift is essential.

---

## 5. Verifier commands

From the normalized package root:

```bash
/usr/bin/python3 scripts/verify_layer3_frontH.py
```

Expected:

```text
Layer 3 Front H verifier: PASS
```

Cumulative runner:

```bash
/usr/bin/python3 scripts/verify_layer3_all.py
```

Expected final line:

```text
Layer 3 cumulative verifier clean runner: PASS
```

If optional dependencies are absent, the cumulative runner may report explicit dependency skips rather than silent failure.

---

## 6. File map

| path | role |
|---|---|
| `layer3_linearization_v1_8.md` | final cumulative Layer 3 theorem text through Front H |
| `README_L3.md` | compact final package map |
| `linearization_steps/` | standalone notes for Fronts A, B, C, D, E, F, G, H |
| `scripts/verify_layer3_all.py` | cumulative smoke verifier |
| `scripts/verify_layer3_frontH.py` | current-front verifier |
| `scripts/verify_layer3_frontA.py` | spectral/Jordan verifier |
| `scripts/verify_layer3_frontB.py`, `scripts/verify_layer3_frontB_envelope.py` | composition-envelope verifiers |
| `scripts/verify_layer3_frontC.py` | intertwiners verifier |
| `scripts/verify_layer3_frontD.py` | finite binary presentation verifier |
| `scripts/verify_layer3_frontE.py` | binary compression verifier |
| `scripts/verify_layer3_frontF.py` | hidden-continuation operator bridge verifier |
| `scripts/verify_layer3_frontG.py` | companion Lie package verifier |
| `tables/` | generated audit/theorem tables |

The README intentionally does not enumerate every CSV. The table namespace is organized by front prefixes:

```text
tables/layer3_frontA_*.csv
tables/layer3_frontB_*.csv
tables/layer3_frontC_*.csv
tables/layer3_frontD_*.csv
tables/layer3_frontE_*.csv
tables/layer3_frontF_*.csv
tables/layer3_frontG_*.csv
tables/layer3_frontH_*.csv
```

---

## 7. Guardrails

1. Layer 3 studies the selected object; it does not participate in the Layer 2 selection proof.
2. The final selector is finite pure `C/J`; continuous symplectic realization is a bridge, not a selector dependency.
3. PAB and row-complement have the same controlled \(\mathcal H\)-profile, so \(\mathcal H\) is not a final separator.
4. PAB multiplication and matrix multiplication share the carrier but are distinct products.
5. The binary term-function algebra is closed and compressed; the all-arity problem remains open.

---

## 8. Open bridges after v1.8

The Layer 3 package is closed through Front H. Remaining work is external or future-facing:

1. compact publication-style proof compression for selected finite verifier checks;
2. all-arity free PAB magma theorem or counter-theorem;
3. global Layer 1H certification of the hidden-continuation \(\mathcal H\) range and pure frontier over all \(\Omega'\);
4. optional development of the continuous symplectic bridge beyond the signed finite lift;
5. functorial explanation of the relation between PAB multiplication and the companion \(\mathfrak{gl}(3)\) package.

---

## Final status

Layer 3 v1.8 is the final cumulative linearization package for PAB. It closes the operator spectrum, composition envelope, intertwiners, binary term-function algebra, binary structural compression, hidden-continuation operator bridge, companion Lie package, and the finite `C/J` to signed symplectic bridge.
