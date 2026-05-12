# Слой 2 v0.7 — селекция PAB из актуального ландшафта Layer 1 v3+H

**Статус:** стабилизированный theorem package после Front A–H. Front G встроил hidden continuation contrast \(\mathcal H\) как вспомогательный bridge, не как обязательный selector.  
**Назначение:** построить новый Layer 2 поверх актуального `layer1_landscape_v3.md`, а не редактировать старую ограниченную селекцию.

---

## Conceptual principle: non-vacuous compression

Layer 2 is governed by one selection principle, unfolded through several finite criteria:

\[
\boxed{
\text{selection = resource minimization subject to nontrivial content.}
}
\]

There are two axes.

**Axis 1 — economy.** What can the system avoid doing?  
It should not read hidden column data when row data suffice; it should not store unnecessary diagonal variation; it should not preserve accidental path coincidences; it should not introduce impure directed-edge dynamics.

**Axis 2 — content.** What must the system still do in order not to become empty?  
It must retain genuine right-argument dependence, fixed diagonal anchors, nontrivial path-sensitivity, and intrinsic directed-edge continuation/reversal dynamics.

Economy alone collapses to a trivial operation: maximal compression is achieved by doing nothing.  
Content alone permits expensive unconstrained operations.  
Selection is the intersection:

\[
\boxed{
\text{minimal resources with preserved nontrivial algebraic content.}
}
\]

Thus Layer 2 is conceptually similar to MDL / FEP at the algebraic level. The individual criteria
\[
\mathcal H_{acc}=0,\quad H_{diag}=0,\quad
\text{nontriviality},\quad
\text{diagonal idempotence},\quad
\min \operatorname{Assoc}_{000},\quad
\text{pure } C/J
\]
are not independent ad hoc filters. They are six local faces of the same principle: remove avoidable structure while preventing vacuous collapse.

The final survivor is PAB because it is the unique point where both axes meet.

## 0. Executive summary

Layer 1 стабилизировал пространство

\[
\Omega'\cong\mathcal G\times\Delta\cong S^{18}\times S^3,
\qquad
|\Omega'|=3^{21}.
\]

Layer 1 также установил главный guardrail для Layer 2:

\[
\operatorname{Assoc}(\mathrm{PAB})=219,
\qquad
\min_{\Omega'}\operatorname{Assoc}=63.
\]

Следовательно, PAB не выбирается глобальной минимизацией Assoc. Layer 2 использует Assoc только локально: после информационного сжатия, невырожденности и независимого выбора диагонали.

Текущая конечная chain theorem:

\[
\Omega'
\xrightarrow{\mathcal H_{acc}=0,\ H_{diag}=0}
9\times3
\xrightarrow{\text{nontrivial},\ \text{diagonal idempotence}}
6\times1
\xrightarrow{\min\operatorname{Assoc}_{000}}
2\times1
\xrightarrow{\text{pure }C/J\text{ drift-kick}}
1.
\]

Финальный survivor:

\[
\boxed{(g_1,000)=\mathrm{PAB}.}
\]

Ключевые уточнения v0.5–v0.7:

\[
\boxed{
\text{полная объяснительная цепочка и кратчайший конечный selector не совпадают.}
}
\]

Nontriviality и \(\operatorname{Assoc}_{000}\) остаются важными структурными guardrails, но после принятия finite pure \(C/J\)-selector они не являются кратчайшими зависимостями уникальности. Они сохранены в narrative chain, потому что делают селекцию понятной: сначала устраняются fake interactions, затем выявляется точная PAB / row-complement ambiguity, и только после этого включается конечная directed-edge dynamics.

Front G добавляет второй guardrail:

\[
\boxed{
\mathcal H\text{ усиливает интерпретацию PAB как pure-frontier point, но не отделяет PAB от row-complement и не входит в finite selector theorem.}
}
\]

На controlled strata обе точки \(g_1,000\) и \(\overline{r_1r_2},000\) имеют одинаковый профиль

\[
H_{tot}=7020,\qquad H_-=0,\qquad N_-=0.
\]

Поэтому \(\mathcal H\) фиксируется как operator-lifted continuation bridge, а не как новый selector.

---

## 1. Interface with Layer 1

Layer 2 импортирует только стабилизированные факты Layer 1 v3+H.

### 1.1. Normal form

\[
\Omega'=\mathcal G\times\Delta,
\qquad
|\mathcal G|=3^{18},
\qquad
|\Delta|=27.
\]

Cross-rule часть \(\mathcal G\) задаётся \(18\) координатами; diagonal часть \(\Delta\) задаётся тройкой

\[
d=(d_0,d_1,d_2)\in S^3.
\]

### 1.2. Information bridge from Layer 1

\[
\mathcal H_{acc}=0
\iff
 g\text{ is column-blind}.
\]

Column-blind rules parametrized by

\[
h_{a,b},
\qquad
 a=h(0,1),\quad b=h(0,2),\quad a,b\in S.
\]

There are exactly \(9\) such rules.

### 1.3. Assoc bridge from Layer 1

At \(d=000\), among nontrivial column-blind rules,

\[
\min\operatorname{Assoc}_{000}=219,
\]

achieved exactly by

\[
g_1=r_2,
\qquad
 g_{comp}=\overline{r_1r_2}.
\]

Layer 1 also proves the obstruction:

\[
\min_{\Omega'}\operatorname{Assoc}=63
<
219=
\operatorname{Assoc}(\mathrm{PAB}).
\]

Thus global Assoc extrema are landscape facts, not PAB-selection criteria.

### 1.4. Hidden continuation bridge

Hidden continuation contrast \(\mathcal H=\mathcal I-\mathcal B\) is integrated in v0.7 as an auxiliary bridge, not as a main selector. Its global \(\Omega'\)-certificate remains open; moreover, on the controlled strata PAB and row-complement have the same pure-frontier profile. Thus \(\mathcal H\) strengthens the continuation-level interpretation of the selected point without changing the finite uniqueness proof.

---

## 2. What selection means

Layer 2 does not claim that a single scalar functional globally selects PAB. The selection claim is conjunctive:

\[
\text{PAB is the unique point satisfying a hierarchy of independent criteria.}
\]

The intended explanatory order is:

\[
\text{information compression}
\rightarrow
\text{nondegenerate anchors}
\rightarrow
\text{path-dependence inside the compressed class}
\rightarrow
\text{finite directed-edge dynamics}.
\]

This order is not merely cosmetic. Assoc is meaningful as a selector only after \(\mathcal H_{acc}=0\), because global Assoc minimization selects column-dependent rules. The finite drift/kick step is meaningful only after column-blindness, because the absorption transitions used by the selector are not canonically defined on arbitrary column-dependent rules.

The diagonal sector is treated in parallel, because

\[
\Omega'=\mathcal G\times\Delta.
\]

So the cross-rule selector and the diagonal selector can be explained independently and then recombined.

---

## 3. Information compression I: \(\mathcal H_{acc}\) and column-blindness

### 3.1. Definition

For a cross-rule

\[
g(r_1,c_1,r_2,c_2),
\qquad r_1\ne r_2,
\]

put the uniform distribution on

\[
\Sigma_{cross}=\{(r_1,c_1,r_2,c_2):r_1\ne r_2\},
\qquad
|\Sigma_{cross}|=54.
\]

Let

\[
C_{out}=g(R_1,C_1,R_2,C_2).
\]

The access cost is

\[
\mathcal H_{acc}(g)=I(C_{out};C_1,C_2\mid R_1,R_2).
\]

It measures how much hidden column information the cross-rule reads after the two rows are already known. In the selection narrative this is the first global criterion: do not read hidden coordinates unless the coarse row data do not suffice.

### 3.2. Deterministic mutual-information collapse

Fix an ordered row pair \(r_1\ne r_2\). Once \((R_1,R_2)=(r_1,r_2)\) is fixed, \(C_{out}\) is a deterministic function of \((C_1,C_2)\). Hence

\[
H(C_{out}\mid C_1,C_2,R_1,R_2)=0.
\]

Therefore

\[
I(C_{out};C_1,C_2\mid R_1,R_2)
=
H(C_{out}\mid R_1,R_2).
\]

Consequently,

\[
\mathcal H_{acc}(g)=0
\]

if and only if, for every fixed row pair \(r_1\ne r_2\), the output column is constant over all nine column inputs \((c_1,c_2)\in S^2\). Equivalently,

\[
\boxed{\mathcal H_{acc}(g)=0\iff g(r_1,c_1,r_2,c_2)=h(r_1,r_2).}
\]

Thus zero access cost is exactly column-blindness.

### 3.3. Count of zero-access cross-rules

A column-blind rule is a \(\sigma\)-equivariant function

\[
h:\{(r_1,r_2):r_1\ne r_2\}\to S.
\]

The ordered row pairs split into two \(\sigma\)-orbits:

\[
(0,1)\to(1,2)\to(2,0),
\]

and

\[
(0,2)\to(1,0)\to(2,1).
\]

Hence a column-blind rule is determined by

\[
a=h(0,1),
\qquad
b=h(0,2),
\qquad a,b\in S.
\]

So there are

\[
3^2=9
\]

zero-access cross-rules.

The finite effect of the first information criterion is

\[
3^{18}\times27
\longrightarrow
9\times27.
\]

---

## 4. Information compression II: \(H_{diag}\) and constant diagonals

### 4.1. Definition

A diagonal map is represented by

\[
d=(d_0,d_1,d_2)\in S^3.
\]

Define diagonal information cost by Shannon entropy of the base triple:

\[
H_{diag}(d)=H(d_0,d_1,d_2).
\]

The point of this criterion is parallel to \(\mathcal H_{acc}\): the diagonal should not carry an unnecessary independent table of choices once the cross-rule architecture is being compressed.

### 4.2. Entropy-zero lemma

Entropy is zero exactly when the distribution is supported on one value. Therefore

\[
\boxed{H_{diag}(d)=0\iff d_0=d_1=d_2.}
\]

The entropy-zero diagonal maps are exactly

\[
000,
\qquad
111,
\qquad
222.
\]

Thus

\[
27\longrightarrow3.
\]

After both information criteria:

\[
3^{18}\times27
\longrightarrow
9\times3.
\]

### 4.3. Why \(H_{diag}\) belongs before idempotence

Diagonal idempotence alone does not select \(000\). Because \(\sigma\)-equivariance gives

\[
\delta(1,1)=\sigma(d_0),
\qquad
\delta(2,2)=\sigma^2(d_0),
\]

the condition

\[
(r,r)\cdot(r,r)=(r,r)
\qquad\forall r
\]

fixes only

\[
d_0=0.
\]

It leaves \(d_1,d_2\) free. Hence idempotence alone leaves \(9\) diagonals. The verifier also checks a stronger diagnostic: without \(H_{diag}=0\), minimizing Assoc over nontrivial column-blind rules and idempotent diagonals prefers \(d=021\) with Assoc \(189\), not \(d=000\). Thus \(H_{diag}=0\) is an essential diagonal information criterion, not a cosmetic simplification.

---

## 5. Nondegenerate anchors

After information compression, two residual degeneracies must be removed: fake right-argument dependence in the cross-rule sector, and non-fixed diagonal anchor states in the diagonal sector.

### 5.1. Cross-rule nontriviality

For column-blind \(h_{a,b}\), if

\[
a=b,
\]

then the output column does not depend on the right row \(r_2\). Indeed the rule is constant across the two row-difference orbits from the perspective of the left row. This is not a genuine binary interaction: the right argument is present syntactically but not functionally.

The nontriviality guardrail is therefore

\[
\boxed{a\ne b.}
\]

It yields

\[
9\times3
\longrightarrow
6\times3.
\]

Front F shows that this guardrail is not a shortest uniqueness dependency once pure \(C/J\) is accepted. It is still retained because it is structurally clean: Layer 2 should not call a fake right-input rule a candidate interaction.

### 5.2. Diagonal idempotence after entropy compression

After \(H_{diag}=0\), only

\[
000,
111,
222
\]

remain. Now require the diagonal anchor states to be fixed:

\[
(r,r)\cdot(r,r)=(r,r)
\qquad\forall r\in S.
\]

Among constant diagonals this selects uniquely

\[
\boxed{d=000=\delta_{std}.}
\]

Thus

\[
6\times3
\longrightarrow
6\times1.
\]

---

## 6. Path-dependence: \(\operatorname{Assoc}_{000}\) inside nontrivial column-blind rules

### 6.1. Guardrail: this is not global Assoc minimization

Once \(d=000\) is independently selected, define

\[
\operatorname{Assoc}_{000}(g)=\operatorname{Assoc}(g,000).
\]

This local use of Assoc is valid only inside the compressed and nondegenerate class. It is not a global selector. Layer 1 proves

\[
\operatorname{Assoc}(\mathrm{PAB})=219,
\qquad
\min_{\Omega'}\operatorname{Assoc}=63.
\]

So global minimization of Assoc selects column-dependent landscape minima, not PAB.

### 6.2. Direct theorem table

For the six nontrivial column-blind rules:

| \(a\) | \(b\) | rule | Assoc\(_{000}\) | selected by local min |
|---:|---:|---|---:|---|
| 0 | 1 | \(h_{0,1}\) | 273 | no |
| 0 | 2 | \(h_{0,2}\) | 273 | no |
| 1 | 0 | \(h_{1,0}\) | 273 | no |
| 1 | 2 | \(h(r_1,r_2)=r_2\) / PAB | 219 | yes |
| 2 | 0 | \(h_{2,0}\) | 273 | no |
| 2 | 1 | \(h(r_1,r_2)=\overline{r_1r_2}\) | 219 | yes |

Therefore

\[
\boxed{
\min_{\text{nontrivial column-blind}}
\operatorname{Assoc}_{000}=219
}
\]

and the equality locus is

\[
\boxed{
\{g_1=r_2,
\ \overline{r_1r_2}\}.
}
\]

Thus

\[
6\times1
\longrightarrow
2\times1.
\]

### 6.3. Normalized five-block profile

The finite theorem has a useful structural explanation through the five-block decomposition.

For PAB and row-complement:

\[
(RRR,RRS,RSR,RSS,RST)=(19,0,0,54,0).
\]

For the four discarded nontrivial column-blind rules:

\[
(RRR,RRS,RSR,RSS,RST)=(19,9,9,54,0).
\]

Since

\[
\operatorname{Assoc}=3\cdot rawAssoc,
\]

the difference

\[
273-219=54
\]

is exactly the extra

\[
9+9
\]

raw accidental associative coincidences in RRS and RSR, multiplied by the normalization factor \(3\).

This is why the criterion should be described as **path-dependence inside the information-compressed language**, not as a blanket preference for nonassociativity. The selected pair is the pair with the fewest accidental cross-row associativity coincidences after column information has already been suppressed.

### 6.4. Status and generated tables

Front D is checked by:

- `tables/layer2_path_dependence_table.csv`;
- `tables/layer2_assoc_block_decomposition_cb.csv`;
- `tables/layer2_assoc_stage_distribution.csv`;
- `tables/layer2_path_dependence_theorem.csv`;
- `tables/layer2_assoc_guardrail.csv`.

---

## 7. The PAB / row-complement ambiguity

After Front D, the remaining pair is

\[
\{g_1,g_{comp}\}
=
\{r_2,\overline{r_1r_2}\}.
\]

They agree on:

- \(\mathcal H_{acc}=0\);
- nontriviality;
- \(\operatorname{Assoc}_{000}=219\);
- the same normalized block profile \((19,0,0,54,0)\);
- basic structure profiles imported from Layer 1.

Therefore the final distinction must use another structure: finite dynamics on the off-diagonal directed-edge set

\[
M^\times=\{(r,c):r\ne c\}.
\]

This is the point at which the selector becomes less global and more specific. The criterion is not a new global landscape functional on \(\Omega'\); it is a finite dynamical audit on the prepared two-point ambiguity.

---

## 8. Canonical directed-edge geometry on \(M^\times\)

Identify \(M^\times\) with directed edges of the 3-point set. There are six directed edges and two intrinsic maps:

\[
C(r,c)=(c,\overline{rc}),
\]

\[
J(r,c)=(c,r).
\]

Interpretation:

- \(C\) is head-to-tail continuation: continue the oriented edge \(r\to c\) to the unique third vertex;
- \(J\) is edge reversal: reverse \(r\to c\).

The verifier checks the dihedral relations

\[
C^3=1,
\qquad
J^2=1,
\qquad
JCJ=C^{-1}.
\]

It also checks that \(C\) and \(J\) are natural under relabeling of the three symbols. This is important: the final selector is not an arbitrary coordinate choice. It uses the intrinsic directed-edge geometry of the off-diagonal set.

Absorption is defined by

\[
x\triangleright y
\iff
x\cdot y=x,
\qquad
x,y\in M^\times.
\]

For a prepared candidate, the two absorption transitions are extracted from the two absorbed neighbors of each \(x\in M^\times\).

---

## 9. Absorption transitions on the six nontrivial column-blind rules

The verifier audits all six nontrivial column-blind rules, not only the final pair.

Four rules with

\[
\operatorname{Assoc}_{000}=273
\]

are dynamically non-admissible already at the degree level: their absorption outdegree on \(M^\times\) is not constantly \(2\). Their outdegree profiles are:

\[
2,0,0,2,2,0
\]

or

\[
0,2,2,0,0,2.
\]

The two survivors have constant outdegree \(2\):

\[
\mathrm{PAB}:
\operatorname{AbsTrans}=\{C,J\},
\]

\[
g_{comp}:
\operatorname{AbsTrans}=\{C^{-1},C^{-1}J\}.
\]

Both systems have one order-3 transition and one involution. Therefore the orders alone do not separate them. The distinction is the factorization of the involution:

\[
J
\quad\text{versus}\quad
C^{-1}J.
\]

PAB has pure edge reversal. The competitor has drifted reversal.

---

## 10. Weak \(q/p\)-splitting audit — rejected as selector

A weak drift/kick criterion would say:

> choose one element from each involution pair as \(q\), the remaining three as \(p\); require the order-3 map to preserve \(q/p\), while the involution switches \(q/p\).

For each survivor, the verifier exhausts all

\[
2^3=8
\]

possible weak sector choices.

Result:

\[
\boxed{\text{PAB has 2 weak drift/kick splits.}}
\]

\[
\boxed{\text{row-complement also has 2 weak drift/kick splits.}}
\]

Therefore weak \(q/p\)-splitting does not separate the pair. This is a crucial audit result: the old coordinate-level symplectic intuition was too weak unless the kick is specified intrinsically.

The rejected criterion remains useful diagnostically: it explains why a naive “there exists a sector split” formulation would be coordinate-dependent and insufficient.

---

## 11. Finite pure \(C/J\) drift-kick selector

The finite selector is stronger and intrinsic:

\[
\boxed{\text{a survivor must have absorption transitions }\{C,J\}.}
\]

Equivalently:

- drift is pure head-to-tail continuation \(C\);
- kick is pure edge reversal \(J\);
- a drifted reversal \(C^{-1}J\) is not accepted as the intrinsic kick.

Then

\[
\mathrm{PAB}:
\operatorname{AbsTrans}=\{C,J\},
\]

but

\[
g_{comp}:
\operatorname{AbsTrans}=\{C^{-1},C^{-1}J\}.
\]

Therefore

\[
\boxed{
\{g_1,g_{comp}\}
\xrightarrow{\text{pure }C/J}
\{g_1\}.
}
\]

The verifier also checks the stronger fact:

\[
\boxed{\text{among all 9 column-blind rules, pure }C/J\text{ selects PAB directly.}}
\]

This is why Front F later distinguishes the full explanatory chain from the shortest finite uniqueness proof.

### 11.1. Relation to the old \(C^2\)-symplectic step

The old continuous \(C^2\)-symplectic tick-map theorem is no longer a dependency of finite selection. It is retained as a geometric bridge:

\[
\boxed{\text{finite selection uses pure }C/J;}
\]

\[
\boxed{C^2\text{ symplectic realization is an open geometric bridge.}}
\]

This makes Layer 2 cleaner. The selector is finite, checkable, and intrinsic on \(M^\times\). The continuous symplectic story can still be developed later, but it no longer bears the logical burden of uniqueness.

---

## 12. Full selection theorem, v0.7

The finite theorem is:

\[
\Omega'
\xrightarrow{\mathcal H_{acc}=0,\ H_{diag}=0}
9\times3
\xrightarrow{a\ne b,\ d\text{ idempotent}}
6\times1
\xrightarrow{\min\operatorname{Assoc}_{000}}
2\times1
\xrightarrow{\{C,J\}\text{ absorption}}
1.
\]

Final survivor:

\[
\boxed{(g_1,000)=\mathrm{PAB}.}
\]

Expanded statement:

\[
\mathrm{PAB}
=
\{(g,d)\in\Omega':
\mathcal H_{acc}(g)=0,
\ H_{diag}(d)=0,
\ g\text{ nontrivial},
\ d\text{ diagonal-idempotent},
\]

\[
\operatorname{Assoc}_{000}(g)=219,
\ \operatorname{AbsTrans}(g)=\{C,J\}
\}.
\]

The conjunction is intentionally redundant from the point of view of shortest uniqueness. Its redundancy is explanatory: each criterion removes a different type of degeneracy or ambiguity.

---

## 13. Independence and minimality registry

Front F distinguishes **explanatory independence** from **shortest logical uniqueness**.

### 13.1. Criterion roles

| criterion | scope | role | deletion consequence |
|---|---|---|---|
| \(\mathcal H_{acc}=0\) | cross-rule | domain-enabling essential | without it global Assoc minima are column-dependent and pure \(C/J\) is not globally defined |
| \(H_{diag}=0\) | diagonal | essential diagonal information compression | idempotence alone leaves 9 diagonals; Assoc over idempotent diagonals prefers \(d=021\), not \(d=000\) |
| nontriviality \(a\ne b\) | column-blind cross-rule | structural guardrail | removes fake binary interactions; not essential once pure \(C/J\) is accepted |
| diagonal idempotence | constant diagonals | essential anchor | \(H_{diag}=0\) alone leaves \(000,111,222\) |
| \(\min\operatorname{Assoc}_{000}\) | six nontrivial CB rules | explanatory algebraic bridge | exposes the PAB/row-complement ambiguity; not essential once pure \(C/J\) is accepted |
| pure \(C/J\) | column-blind absorption on \(M^\times\) | final finite selector | without it Assoc leaves two cross-rule survivors |

### 13.2. Important deletion facts

1. Without \(\mathcal H_{acc}=0\), Assoc is not a PAB selector:
   \[
   \min_{\Omega'}\operatorname{Assoc}=63
   \]
   while
   \[
   \operatorname{Assoc}(\mathrm{PAB})=219.
   \]

2. Without \(H_{diag}=0\), diagonal idempotence leaves \(9\) diagonals. If one then minimizes Assoc over nontrivial column-blind rules and idempotent diagonals, the minimum is
   \[
   \operatorname{Assoc}=189
   \]
   at
   \[
   d=021,
   \]
   not at \(d=000\). Thus \(H_{diag}=0\) prevents the diagonal from escaping to the wrong local Assoc frontier.

3. Without pure \(C/J\), the two-point ambiguity remains:
   \[
   \{g_1,\overline{r_1r_2}\}.
   \]

4. Without \(\operatorname{Assoc}_{000}\), pure \(C/J\) still selects PAB from all \(9\) column-blind rules. Therefore Assoc is explanatory rather than shortest-selector-essential.

5. Without nontriviality, the final result is still unique once Assoc and pure \(C/J\) are kept. Therefore nontriviality is a guardrail rather than a shortest dependency.

### 13.3. Minimal selector sets

The full narrative set is

\[
\mathcal H_{acc}=0,
\quad
H_{diag}=0,
\quad
\text{nontriviality},
\quad
\text{diagonal idempotence},
\quad
\min\operatorname{Assoc}_{000},
\quad
\text{pure }C/J.
\]

The current shortest finite uniqueness set is

\[
\boxed{
\mathcal H_{acc}=0,
\quad
H_{diag}=0,
\quad
\text{diagonal idempotence},
\quad
\text{pure }C/J.
}
\]

The recommended exposition still uses the full narrative set, because it proceeds from global criteria to specific criteria and makes the PAB/competitor ambiguity visible before resolving it.

### 13.4. Why this does not weaken the theorem

A shorter uniqueness proof is not automatically a better explanation. The full chain is retained because it answers external objections:

- why column information is not read;
- why fake right-input rules are excluded;
- why Assoc is local rather than global;
- why the row-complement competitor is a real ambiguity;
- why weak \(q/p\) sector choice is insufficient;
- why the final kick must be intrinsic edge reversal \(J\).

The deletion audit strengthens the package by making explicit which criteria are logical dependencies and which are explanatory guardrails.

---

## 14. Auxiliary bridge: hidden continuation contrast \(\mathcal H\)

Front G integrates the Layer 1H observable as an **auxiliary bridge**, not as a new required selector.

The observable is operator-lifted. For a finite magma \((M,\cdot)\), define left regular operators

\[
L_x e_y=e_{x\cdot y}.
\]

For triples \((x,y,z)\in M^3\), Layer 1H defines

\[
\mathcal I(x,y,z)=\|L_{x\cdot y}L_z-L_xL_{y\cdot z}\|_{HS}^2,
\]

\[
\mathcal B(x,y,z)=\|L_{(x\cdot y)\cdot z}-L_{x\cdot(y\cdot z)}\|_{HS}^2,
\]

\[
\boxed{\mathcal H(x,y,z)=\mathcal I(x,y,z)-\mathcal B(x,y,z).}
\]

The totals are

\[
I_{tot}=\sum_{x,y,z}\mathcal I(x,y,z),
\qquad
B_{tot}=\sum_{x,y,z}\mathcal B(x,y,z),
\qquad
H_{tot}=I_{tot}-B_{tot}.
\]

Layer 1H proves the normalized master formula

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)}
\]

with \(3^7=2187\) normalized terms. Thus \(\mathcal H\) is a landscape observable on the same normal-form coordinates \((A,B,d)\in S^{18}\times S^3\), but it sees operator-continuation structure rather than only associator equality.

### 14.1. Controlled pure frontier

Layer 1H certifies exact controlled atlases on three strata:

| stratum | points | \(H_{min}\) | \(H_{max}\) | pure count | pure \(H_{max}\) |
|---|---:|---:|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | 1836 | 7302 | 159 | 7020 |
| affine \(\times\Delta\) | 19683 | -2268 | 7302 | 723 | 7020 |
| degree \(\le2\times\Delta\) | 14348907 | -2268 | 7302 | 3177 | 7020 |

Here **pure** means

\[
N_-=0.
\]

On all three controlled strata,

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

PAB lies exactly on this controlled pure frontier:

\[
\mathrm{PAB}:
\qquad
H_{tot}=7020,
\qquad
H_-=0,
\qquad
N_-=0.
\]

This is a strong compatibility fact: the selected PAB point is not merely finite-selector unique; it is also pure-frontier for the operator-lifted continuation contrast on the certified controlled strata.

The v0.7 verifier also recomputes the entire column-blind \(\times\Delta\) H atlas directly. In that exact 243-point domain, the pure frontier contains six points. PAB and row-complement are both in this six-point locus, so the H bridge is compatible with the selected point but not unique at the final ambiguity scale.

### 14.2. Why \(\mathcal H\) is not a selector in v0.7

The same controlled profile holds for the row-complement competitor:

\[
g_{comp}=\overline{r_1r_2}:
\qquad
H_{tot}=7020,
\qquad
H_-=0,
\qquad
N_-=0.
\]

Therefore \(\mathcal H\) does **not** resolve the final PAB/competitor ambiguity. It reinforces the fact that the ambiguity is real: both surviving algebraic candidates are continuation-pure at the same frontier value.

The raw controlled maximum is higher:

\[
H_{tot}=7302,
\]

but it is not pure:

\[
H_-=6,
\qquad
N_-=3.
\]

So the controlled picture is:

\[
\text{raw frontier }7302
\quad\text{requires a small signed negative tail,}
\]

while

\[
\text{pure frontier }7020
\quad\text{contains PAB and row-complement.}
\]

This is why Front G records \(\mathcal H\) as a **purity/continuation bridge**, not as another filter in the finite selection chain.

### 14.3. Local shell diagnostics

Layer 1H also computes exact Hamming shells around PAB and row-complement. Both have the same local profile:

| center | radius | center \(H_{tot}\) | neighbors | min \(H_{tot}\) | max \(H_{tot}\) | above center |
|---|---:|---:|---:|---:|---:|---:|
| PAB | 1 | 7020 | 42 | 5604 | 7302 | 2 |
| PAB | 2 | 7020 | 840 | 4524 | 6924 | 0 |
| row-complement | 1 | 7020 | 42 | 5604 | 7302 | 2 |
| row-complement | 2 | 7020 | 840 | 4524 | 6924 | 0 |

Interpretation:

1. radius-1 has two nearby raw-H improvements to \(7302\), but they are not pure;
2. radius-2 is entirely below \(7020\);
3. the PAB/competitor pair has identical local \(\mathcal H\)-geometry at this resolution.

Again, this supports the policy:

\[
\boxed{\mathcal H\text{ strengthens the continuation picture but does not enter the selector theorem.}}
\]

### 14.4. Front G policy statement

The finite Layer 2 theorem remains:

\[
\Omega'
\xrightarrow{\mathcal H_{acc}=0,\ H_{diag}=0}
9\times3
\xrightarrow{\text{nontrivial},\ \text{diagonal idempotence}}
6\times1
\xrightarrow{\min\operatorname{Assoc}_{000}}
2\times1
\xrightarrow{\text{pure }C/J}
1.
\]

The hidden continuation contrast is attached as a side theorem:

\[
\mathrm{PAB}\in
\{H_{tot}=7020,\ N_-=0\}
\]

on the controlled strata certified by Layer 1H.

The following claims are deliberately **not** made in v0.7:

\[
\mathcal H\text{ globally selects PAB on }\Omega',
\]

\[
\mathcal H\text{ separates PAB from }\overline{r_1r_2},
\]

\[
\max_{\Omega'}\{H_{tot}:N_-=0\}=7020.
\]

The last statement is plausible and important, but it remains a Layer 1H global certification problem, not a Layer 2 selector dependency.

### 14.5. Front G verifier tables

Front G adds the following tables:

- `tables/layer2_frontG_H_controlled_summary.csv`;
- `tables/layer2_frontG_H_controlled_summary_imported.csv`;
- `tables/layer2_frontG_H_column_blind_audit.csv`;
- `tables/layer2_frontG_H_key_witnesses.csv`;
- `tables/layer2_frontG_H_pure_frontier_locus_cb.csv`;
- `tables/layer2_frontG_H_selector_guardrails.csv`;
- `tables/layer2_frontG_H_bridge_policy.csv`;
- `tables/layer2_frontG_H_auxiliary_bridge.csv`;
- `tables/layer2_frontG_H_status_registry.csv`;
- `tables/layer2_frontG_H_local_shell_summary.csv`.

The verifier checks the imported controlled facts needed for the policy:

\[
\max_{controlled}\{H_{tot}:N_-=0\}=7020,
\]

\[
\mathrm{PAB}:H_{tot}=7020,H_-=0,N_-=0,
\]

\[
\overline{r_1r_2}:H_{tot}=7020,H_-=0,N_-=0,
\]

\[
H_{tot}=7302\Rightarrow H_->0\text{ on the controlled Hmax witness.}
\]

## 15. Front H: package hardening and artifact integrity

Front H does not introduce a new selector. Its role is infrastructural: make the Layer 2 package hard to desynchronize. This became necessary because the theorem text, generated tables, and verifier can otherwise drift apart while the mathematical claims remain verbally unchanged.

Front H adds three final checks:

1. **Table integrity audit.** Every core table generated through Fronts B--G must be present, nonempty, and hashable. The verifier writes row counts and SHA-256 hashes to

   `tables/layer2_frontH_table_integrity_audit.csv`.

2. **Cross-table consistency audit.** The verifier checks that the generated tables still imply the central Layer 2 facts:

   \[
   6\xrightarrow{\min\operatorname{Assoc}_{000}}2,
   \qquad
   2\xrightarrow{\mathrm{pure}\ C/J}1,
   \]

   that weak \(q/p\) splitting is rejected, and that hidden continuation contrast remains auxiliary because PAB and row-complement share the same pure H profile at \(d=000\). The result is written to

   `tables/layer2_frontH_consistency_audit.csv`.

3. **Artifact manifest.** The verifier records the main theorem text, README, verifier, Front H integrity tables, and release bundle policy in

   `tables/layer2_frontH_artifact_manifest.csv`.

The final hardened package therefore has two layers of reproducibility:

\[
\text{finite theorem checks}
\quad+\quad
\text{artifact-level consistency checks}.
\]

Front H also writes:

- `tables/layer2_frontH_final_package_registry.csv`;
- `tables/layer2_frontH_open_bridge_registry.csv`.

The first records that Fronts A--H are closed. The second isolates what remains open without blocking the finite Layer 2 theorem:

\[
C^2\text{ symplectic realization bridge},
\qquad
\text{global }\Omega'\text{ H-certificate},
\qquad
\text{future hand-compression of finite checks}.
\]

The important consequence is:

\[
\boxed{\text{Layer 2 selection is now finite-closed; the remaining items are bridges or exposition upgrades.}}
\]

## 16. Status registry

| claim | status | comment |
|---|---|---|
| \(\Omega'\cong S^{18}\times S^3\) | imported [V] | Layer 1 v3+H |
| \(\mathcal H_{acc}=0\iff\) column-blind | closed/imported [V] | Front B |
| 9 column-blind rules | checked [V] | verifier |
| \(H_{diag}=0\iff d\) constant | checked [V] | Front B |
| 3 constant diagonals | checked [V] | verifier |
| idempotence after constant diagonal selects 000 | checked [V] | Front C |
| idempotence alone leaves 9 diagonals | checked [V] | Front F diagnostic |
| nontriviality leaves 6 rules | checked [V] / guardrail | Front C |
| \(\min\operatorname{Assoc}_{000}=219\) leaves PAB/competitor | checked [V] | Front D |
| five-block explanation of Assoc gap | checked [V] | extra RRS+RSR coincidences |
| weak \(q/p\)-split separates PAB | rejected | both survivors pass |
| finite pure \(C/J\) separates PAB | checked [V] | Front E finite core |
| pure \(C/J\) selects PAB from all 9 CB rules | checked [V] | Front F minimality |
| independence/minimality registry | checked [V] | Front F |
| hidden continuation contrast bridge | checked/imported [V] | Front G auxiliary bridge |
| Front H package hardening | checked [V] | artifact manifest + table integrity audit + consistency audit |
| PAB and row-complement share \(H_{tot}=7020,N_-=0\) | checked/imported [V] | Front G guardrail: H does not separate final pair |
| controlled pure H frontier \(7020\) | imported [V] | Layer 1H controlled strata only |
| \(C^2\) symplectic realization | open bridge | not a finite selector dependency |
| \(\mathcal H\) as global selector | not used / open | global H certificate absent; H does not separate PAB/competitor |

## 17. Open questions for Layer 2

1. Decide how much of the continuous symplectic realization belongs in Layer 2 versus a later geometric appendix.
2. Produce a polished proof narrative for finite pure \(C/J\), avoiding dependence on arbitrary \(q/p\)-coordinates.
3. Decide publication wording for the fact that \(\operatorname{Assoc}_{000}\) is explanatory rather than shortest-selector-essential.
4. Explore whether pure \(C/J\) can be generalized beyond the column-blind domain, or whether \(\mathcal H_{acc}=0\) is intrinsically required as a domain-enabling condition.
5. Check whether the diagonal selector \(H_{diag}=0\) admits a deeper derivation from continuation contrast or other operator-lifted invariants.
6. Complete the global Layer 1H certification problem for \(\mathcal H\): global \(H\)-range, global raw frontier, and global pure-frontier theorem over all \(\Omega'\).

---

## Appendix A. Verifier map

Run:

```bash
/usr/bin/python3 scripts/verify_layer2_selection_final.py
```

The verifier regenerates all core tables in `tables/` and checks the finite claims through Front H.

Expected summary includes:

```text
Layer 2 selection verifier v0.7: PASS
  Front B closed: information criteria formalized and finite cores checked
  Front C closed: nondegenerate anchors formalized and checked
  Front D closed: local path-dependence theorem checked on six nontrivial column-blind rules
  Front E finite core closed: pure C/J directed-edge selector separates PAB from row-complement
  Front F closed: independence/minimality registry and deletion audit generated
  Front G closed: hidden continuation contrast H integrated as auxiliary bridge
  H guardrail: PAB and row-complement both have H_tot=7020, H_-=0, N_-=0 at d=000
  H guardrail: global Omega' H certificate remains open; H is not a selector dependency
  Front H closed: artifact manifest, table integrity audit, and consistency audit generated
```

Core generated tables:

- `tables/layer2_selection_chain.csv`
- `tables/layer2_status_registry.csv`
- `tables/layer2_information_criteria.csv`
- `tables/layer2_hacc_column_blind_rules.csv`
- `tables/layer2_diag_entropy_table.csv`
- `tables/layer2_nondegenerate_anchor_audit.csv`
- `tables/layer2_path_dependence_table.csv`
- `tables/layer2_assoc_block_decomposition_cb.csv`
- `tables/layer2_frontE_canonical_maps.csv`
- `tables/layer2_frontE_nontrivial_cb_absorption_audit.csv`
- `tables/layer2_frontE_survivor_transition_factorization.csv`
- `tables/layer2_frontE_pure_drift_kick_theorem.csv`
- `tables/layer2_qp_splitting_audit.csv`
- `tables/layer2_weak_qp_splitting_details.csv`
- `tables/layer2_frontF_criterion_role_registry.csv`
- `tables/layer2_frontF_deletion_audit.csv`
- `tables/layer2_frontF_minimal_selector_sets.csv`
- `tables/layer2_frontF_dependency_matrix.csv`
- `tables/layer2_frontF_no_Hdiag_idempotent_assoc_audit.csv`

Hidden continuation bridge:

- `tables/layer2_frontG_H_column_blind_audit.csv`
- `tables/layer2_frontG_H_controlled_summary.csv`
- `tables/layer2_frontG_H_controlled_summary_imported.csv`
- `tables/layer2_frontG_H_key_witnesses.csv`
- `tables/layer2_frontG_H_pure_frontier_locus_cb.csv`
- `tables/layer2_frontG_H_selector_guardrails.csv`
- `tables/layer2_frontG_H_bridge_policy.csv`
- `tables/layer2_frontG_H_local_shell_summary.csv`
- `tables/layer2_frontG_H_auxiliary_bridge.csv`
- `tables/layer2_frontG_H_status_registry.csv`


Front H hardening:

- `tables/layer2_frontH_artifact_manifest.csv`
- `tables/layer2_frontH_table_integrity_audit.csv`
- `tables/layer2_frontH_consistency_audit.csv`
- `tables/layer2_frontH_final_package_registry.csv`
- `tables/layer2_frontH_open_bridge_registry.csv`

---


**Revision note v0.7.** Front H is closed. Front G remains closed: Hidden continuation contrast \(\mathcal H\) is integrated as an auxiliary controlled bridge with dedicated tables and verifier checks. Front H adds integrity/manifest/consistency tables. It remains outside the finite selector theorem because the global \(\Omega'\) \(H\)-certificate is open and because PAB and row-complement have the same controlled pure-frontier profile.
