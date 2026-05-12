# Layer 3 Front E — structural compression of the binary free PAB magma

**Version:** Layer 3 v1.6 / Front E.  
**Input:** Front D finite binary presentation, with \(|T_2(\mathrm{PAB})|=630\) and stabilization at minimal size 15.  
**Output:** a structural factorization of the 630-state binary term-function magma.

---

## E.0. Updated problem statement

Front D changed the status of the old free-magma question. The binary part is no longer an open “infinite or finite?” problem:

\[
|T_2(\mathrm{PAB})|=630,
\qquad
\text{new binary functions stop at size }15.
\]

Therefore Front E asks a sharper question:

\[
\boxed{\text{why does the binary closure have size }630?}
\]

The answer is the factorization

\[
\boxed{
T_2(\mathrm{PAB})
\cong
\{x,y\}\times \mathcal S_{21}\times \mathcal U_{15},
}
\]

so that

\[
\boxed{|T_2|=2\cdot21\cdot15=630.}
\]

---

## E.1. Leftmost-row theorem

Let \(t(x,y)\) be any binary PAB term. Define \(\ell(t)\in\{x,y\}\) to be the leftmost variable occurring in the binary tree of \(t\). Since PAB satisfies AX0,

\[
\operatorname{row}(ab)=\operatorname{row}(a),
\]

a direct induction gives

\[
\boxed{
\operatorname{row}(t(a,b))=
\operatorname{row}(\ell(t)(a,b)).
}
\]

Hence every binary term-function has an **owner**:

* owner \(x\): output row is always row\((x)\);
* owner \(y\): output row is always row\((y)\).

The verifier checks the exact split

\[
\boxed{|T_2^{(x)}|=315,
\qquad
|T_2^{(y)}|=315.}
\]

The variable-swap involution \(x\leftrightarrow y\) exchanges the two sectors freely:

\[
\boxed{315\text{ two-cycles, no fixed binary term-functions}.}
\]

---

## E.2. Normalized block coordinates

Fix an owner. Normalize the owner row to \(0\), and write the other row difference as

\[
\delta\in\{0,+1,-1\}\cong\{0,1,2\}.
\]

For an owner-\(x\) term-function \(f\), define three block maps by their output columns:

\[
S_f(a,b)=\operatorname{col} f((0,a),(0,b)),
\]

\[
P_f(a,b)=\operatorname{col} f((0,a),(1,b)),
\]

\[
M_f(a,b)=\operatorname{col} f((0,a),(2,b)).
\]

For owner \(y\), the same definition is used in owner-relative coordinates: owner column first, other column second.

Thus every binary term-function is encoded by

\[
(\operatorname{owner},S_f,P_f,M_f).
\]

---

## E.3. Cross-block unary collapse

The cross-row blocks do not retain two-column dependence. For every binary term-function there is a unary map

\[
u_f:S\to S
\]

such that

\[
\boxed{P_f(a,b)=u_f(a).}
\]

The minus block is determined by the plus block through the fixed involution

\[
\boxed{
\phi(u)(c)=-u(-c)\pmod3.
}
\]

That is,

\[
\boxed{M_f(a,b)=\phi(u_f)(a).}
\]

The set of possible cross-unary maps is

\[
\boxed{|\mathcal U_{15}|=15.}
\]

The 15 maps are listed in `tables/layer3_frontE_U15_cross_unary_maps.csv`.

---

## E.4. Same-row factor

The same-row restrictions form a 21-element set

\[
\boxed{|\mathcal S_{21}|=21.}
\]

These are the possible maps

\[
S:S^2\to S
\]

that occur when both inputs lie in the same row, written in owner-relative column coordinates.

The verifier classifies the 21 maps as follows:

* one constant map, dependency profile `00`, image size 1;
* four one-variable maps, profiles `10` or `01`, image size 3;
* sixteen genuinely two-variable maps, profile `11`, image size 3.

The full list is in `tables/layer3_frontE_S21_same_row_maps.csv`.

---

## E.5. Factorization theorem

For each owner sector,

\[
\boxed{
T_2^{(x)}\cong\mathcal S_{21}\times\mathcal U_{15},
\qquad
T_2^{(y)}\cong\mathcal S_{21}\times\mathcal U_{15}.
}
\]

Equivalently, every pair

\[
(S,u)\in\mathcal S_{21}\times\mathcal U_{15}
\]

occurs exactly once in each owner sector.

Therefore

\[
\boxed{
|T_2|=2\cdot21\cdot15=630.
}
\]

This is the main Front E compression theorem.

---

## E.6. Multiplication in factor coordinates

Let

\[
m(a,b)=
\begin{cases}
0,&a=b,\\
-a-b,&a\ne b
\end{cases}
\pmod3
\]

be the normalized one-row PAB product on columns.

For two same-row maps \(S,T:S^2\to S\), define

\[
(S\star T)(a,b)=m(S(a,b),T(a,b)),
\]

and

\[
(S\star T^{op})(a,b)=m(S(a,b),T(b,a)).
\]

For unary maps \(u,v:S\to S\), define

\[
(u\star v)(a)=m(u(a),v(a)).
\]

Then the product of two factor states is:

\[
(o,S,u)\cdot(o,T,v)
=
(o,S\star T,u\star v),
\]

while if the right factor has the opposite owner,

\[
(o,S,u)\cdot(o',T,v)
=
(o,S\star T^{op},\kappa),
\qquad
\kappa=111.
\]

Here `111` denotes the constant unary map \(a\mapsto1\) in owner-relative plus-row coordinates. Its paired minus-row block is \(\phi(111)=222\).

Thus the full \(630\times630\) Front D multiplication table is reproduced from:

* a \(21\times21\) same-owner \(\mathcal S_{21}\) table;
* a \(21\times21\) opposite-owner swapped \(\mathcal S_{21}\) table;
* a \(15\times15\) \(\mathcal U_{15}\) table;
* the owner law “the product owner is the left owner.”

The verifier checks this equality against every entry of the original \(630\times630\) table.

---

## E.7. Coarse profile distribution

The 630 states collapse to 24 coarse profiles if one records:

\[
\text{owner},
\quad
\text{dependency bits of }(S,P,M),
\quad
\text{image sizes of }(S,P,M).
\]

Because the owner sectors are symmetric, there are 12 profiles per owner. The largest profile is

\[
(11/10/10,
(3,2,2)),
\]

with 160 states per owner. It means:

* same-row block genuinely depends on both columns;
* both cross blocks depend only on the owner column;
* same-row image size is 3;
* cross-block image size is 2.

The full table is `tables/layer3_frontE_profile_distribution.csv`.

---

## E.8. Arity-growth guardrail

Front E does not claim an all-arity finite-basis theorem. It records a small arity-3 smoke computation to show the updated boundary:

| arity | size | new functions | cumulative |
|---:|---:|---:|---:|
| 3 | 1 | 3 | 3 |
| 3 | 2 | 9 | 12 |
| 3 | 3 | 45 | 57 |
| 3 | 4 | 207 | 264 |
| 3 | 5 | 1131 | 1395 |
| 3 | 6 | 4182 | 5577 |

Thus binary closure is completely finite and structurally compressed, but all-arity behavior remains open.

The next possible free-algebra question is not “is the binary part finite?” but:

\[
\boxed{
\text{does the factor mechanism }\mathcal S_{21}\times\mathcal U_{15}
\text{ extend to a general arity decomposition?}
}
\]

---

## E.9. Status

Closed in Front E:

\[
\boxed{T_2(\mathrm{PAB})
\cong
\{x,y\}\times\mathcal S_{21}\times\mathcal U_{15}.}
\]

\[
\boxed{|T_2|=630=2\cdot21\cdot15.}
\]

\[
\boxed{
\text{the }630\times630\text{ binary multiplication table compresses to }21/15\text{-factor tables.}
}
\]

Open after Front E:

* compact human-readable all-arity identity basis;
* full arity-growth theorem;
* possible generalization of the \(S/U\) factor mechanism beyond binary functions.
