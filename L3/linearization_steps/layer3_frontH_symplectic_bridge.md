# Layer 3 Front H — geometric bridge from finite pure C/J to continuous symplectic realization

**Version:** Layer 3 v1.8 / Front H.  
**Status:** closed as a bridge theorem package.  
**Scope:** post-selection geometry of the PAB directed-edge dynamics on \(M^\times\). This is not a new selector and does not reintroduce the old continuous symplectic step as a dependency of Layer 2.

---

## 1. Input from Layer 2

Layer 2 v0.7 closed finite selection by the pure directed-edge criterion

\[
\operatorname{AbsTrans}_{\mathrm{PAB}}=\{C,J\},
\]

where, on

\[
M^\times=\{(r,c):r\ne c\},
\]

\[
C(r,c)=(c,\overline{rc}),
\qquad
J(r,c)=(c,r).
\]

The row-complement competitor has

\[
\operatorname{AbsTrans}_{comp}=\{C^{-1},C^{-1}J\}.
\]

Thus PAB has pure continuation plus pure reversal; the competitor has drifted reversal.

Front H starts from this finite result and constructs the continuous/symplectic bridge after selection.

---

## 2. Directed-edge relations

The finite maps satisfy

\[
C^3=1,
\qquad
J^2=1,
\qquad
JCJ=C^{-1}.
\]

This is the finite skeleton of the geometric bridge.

---

## 3. Canonical \(q/p\) chart

Choose the positive \(C\)-cycle

\[
q_i=(i,i+1),
\qquad i\in\mathbb F_3.
\]

Define the opposite sector with the reversed index convention

\[
p_i=J(q_{-i}).
\]

Explicitly,

\[
q_0=(0,1),\quad q_1=(1,2),\quad q_2=(2,0),
\]

\[
p_0=(1,0),\quad p_1=(0,2),\quad p_2=(2,1).
\]

Then

\[
Cq_i=q_{i+1},
\qquad
Cp_i=p_{i+1},
\]

while

\[
Jq_i=p_{-i},
\qquad
Jp_i=q_{-i}.
\]

So \(C\) is sector-preserving and \(J\) is sector-exchanging. The index reflection in \(J\) is exactly the finite relation \(JCJ=C^{-1}\).

---

## 4. The symplectic carrier

Let

\[
V=\mathbb R^3_q\oplus\mathbb R^3_p
\]

with standard symplectic form

\[
\Omega=
\begin{pmatrix}
0&I_3\\
-I_3&0
\end{pmatrix}.
\]

Let \(R\) be the cyclic permutation matrix

\[
R e_i=e_{i+1},
\]

and let \(P\) be the reflection matrix

\[
P e_i=e_{-i}.
\]

Then

\[
P^2=I,
\qquad
PRP=R^{-1}.
\]

The continuation lift is

\[
\widehat C=
\begin{pmatrix}
R&0\\
0&R
\end{pmatrix}.
\]

It is symplectic:

\[
\widehat C^T\Omega\widehat C=\Omega.
\]

The literal unsigned lift of edge reversal is

\[
J_0=
\begin{pmatrix}
0&P\\
P&0
\end{pmatrix}.
\]

It is anti-symplectic:

\[
J_0^T\Omega J_0=-\Omega.
\]

Therefore the continuous symplectic bridge needs the signed lift

\[
\widehat J=
\begin{pmatrix}
0&-P\\
P&0
\end{pmatrix}.
\]

This sends

\[
q_i\mapsto p_{-i},
\qquad
p_i\mapsto -q_{-i}.
\]

After forgetting the sign, it covers the finite reversal \(J\). It is symplectic:

\[
\widehat J^T\Omega\widehat J=\Omega.
\]

The lifted relations are

\[
\widehat C^3=I,
\qquad
\widehat J^2=-I,
\qquad
\widehat J\widehat C\widehat J^{-1}=\widehat C^{-1}.
\]

Thus \(C,J\) lift to a projective dihedral system inside

\[
Sp(6,\mathbb R).
\]

The central sign is the exact correction needed to turn finite reversal into a symplectic sector-exchange.

---

## 5. Smooth symplectic paths

The bridge is continuous, not merely linear-discrete.

Let \(R(t)\) be the rotation through angle

\[
2\pi t/3
\]

around the axis \((1,1,1)\), oriented so that \(R(1)=R\). Then

\[
\widehat C_t=
\begin{pmatrix}
R(t)&0\\
0&R(t)
\end{pmatrix}
\in Sp(6,\mathbb R),
\]

with

\[
\widehat C_0=I,
\qquad
\widehat C_1=\widehat C.
\]

Similarly,

\[
\widehat J_t=
\begin{pmatrix}
\cos(\pi t/2)I&-\sin(\pi t/2)P\\
\sin(\pi t/2)P&\cos(\pi t/2)I
\end{pmatrix}
\in Sp(6,\mathbb R),
\]

with

\[
\widehat J_0=I,
\qquad
\widehat J_1=\widehat J.
\]

So the finite pure \(C/J\) data produce explicit smooth paths in the symplectic group.

---

## 6. Hamiltonian path bridge

Starting at

\[
q_0=(0,1),
\]

the finite word

\[
C,J,C,C,J
\]

visits all six directed edges:

\[
q_0\to q_1\to p_2\to p_0\to p_1\to q_2.
\]

Its signed lift is

\[
\widehat\Phi
=
\widehat J\widehat C\widehat C\widehat J\widehat C.
\]

Since both \(\widehat C\) and \(\widehat J\) are symplectic,

\[
\widehat\Phi\in Sp(6,\mathbb R).
\]

Replacing each factor by its path version gives a piecewise-smooth continuous symplectic realization of the finite tick word.

---

## 7. Guardrail: why this is not a selector

Front H proves

\[
\text{finite pure }\{C,J\}
\Rightarrow
\text{canonical signed symplectic bridge}.
\]

It does not prove

\[
\text{continuous symplecticity alone selects PAB}.
\]

The row-complement competitor has

\[
\{C^{-1},C^{-1}J\}.
\]

If one allows drifted reversal as a kick, one can build signed symplectic lifts of those maps too. The finite selector is therefore the purity statement:

\[
\boxed{\text{kick}=J,\text{ not }C^{-1}J.}
\]

Front H is a geometric consequence of the selected finite structure, not a replacement for the Layer 2 finite theorem.

---

## 8. Verifier

Run from the package root:

```bash
/usr/bin/python3 scripts/verify_layer3_frontH.py
```

Expected summary:

```text
Layer 3 Front H verifier: PASS
  finite pure C/J geometry: D3 relations and PAB/competitor absorption transitions checked
  canonical q/p chart: C preserves sectors and J exchanges sectors with reflection
  signed symplectic lift: C_hat and J_hat lie in Sp(6); literal unsigned J is anti-symplectic
  projective D3 lift: C_hat^3=I, J_hat^2=-I, J_hat C_hat J_hat^{-1}=C_hat^{-1}
  continuous realization: explicit C_t and J_t paths in Sp(6) checked by endpoint/sample audit
  tick bridge: C,J,C,C,J finite Hamiltonian path visits all six edges and has symplectic signed lift
```

---

## 9. Status

\[
\boxed{\mathrm{L3\text{-}H}\text{ closed as a geometric bridge.}}
\]

Closed claims:

1. finite \(C/J\) directed-edge relations;
2. canonical \(q/p\) chart;
3. exact signed symplectic lift;
4. projective dihedral relation inside \(Sp(6,\mathbb R)\);
5. smooth path realization;
6. symplectic signed lift of the finite tick word \(C,J,C,C,J\).

Open or deliberately not claimed:

1. a global symplectic selector on all of \(\Omega'\);
2. a proof that every non-PAB candidate lacks any symplectic lift;
3. a physical Hamiltonian model beyond the finite/signed symplectic bridge.
