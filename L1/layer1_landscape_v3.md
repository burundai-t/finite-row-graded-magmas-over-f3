# Слой 1 v3+H — финальная карта ландшафта $\sigma$-эквивариантных магм AX0 + AX2

**Версия:** Layer 1 v3+H, документационное обновление после Global Assoc proof-skeleton / tail-reduction stabilization и интеграции Layer 1H controlled theorem package.  
**Назначение:** дать самодостаточное описание пространства
\[
\Omega'\cong \mathcal G\times\Delta\cong S^{18}\times S^3
\]
и основных вычислительно/аналитически закреплённых инвариантов Layer 1, включая Assoc / \(Z(q)\) и hidden continuation contrast \(\mathcal H\).  
**Граница слоя:** Layer 1 описывает ландшафт. Он не селектирует PAB, не вводит symplectic/drift-kick как критерий отбора и не переходит к линеаризации $k[M]$. Селекция относится к Layer 2; линеаризация относится к Layer 3.

---

## 0. Executive summary

Главный итог v3:

\[
\boxed{\Omega'\cong S^{21},\qquad |\Omega'|=3^{21}=10\,460\,353\,203.}
\]

Для landscape-инварианта

\[
\operatorname{Assoc}(x)
=
\#\{(a,b,c)\in M^3:(a\cdot b)\cdot c=a\cdot(b\cdot c)\}
\]

теперь известны не только witnesses, а полный finite census:

\[
\boxed{\min_{\Omega'}\operatorname{Assoc}=63,\qquad
\max_{\Omega'}\operatorname{Assoc}=597.}
\]

\[
\boxed{Z(q)=\sum_{x\in\Omega'}q^{\operatorname{Assoc}(x)}\text{ известен точно.}}
\]

Ключевые численные итоги:

| invariant | value |
|---|---:|
| $|\Omega'|$ | $3^{21}=10\,460\,353\,203$ |
| $\min\operatorname{Assoc}$ | $63$ |
| $[q^{63}]Z(q)$ | $24$ |
| $\max\operatorname{Assoc}$ | $597$ |
| $[q^{597}]Z(q)$ | $6$ |
| nonzero coefficients of $Z(q)$ | $167$ |
| $\mathbb E[\operatorname{Assoc}]$ | $245$ |
| $\operatorname{Var}(\operatorname{Assoc})$ | $27820/27$ |
| mode | $237$ |
| coefficient at mode | $426\,317\,976$ |

Endpoint loci:

\[
\boxed{|\mathcal M_{63}|=24,\qquad |\mathcal M_{63}/S_3|=12,}
\]

\[
\boxed{|\mathcal M_{597}|=6,\qquad |\mathcal M_{597}/S_3|=3.}
\]

Global Assoc theorem now has a separated internal structure:

\[
\text{range theorem }(21\le rawAssoc\le199),
\]

\[
\text{endpoint theorem }(raw=21,199\text{ equality patterns}),
\]

\[
\text{distribution theorem }(Z(q)\text{ known exactly}).
\]

The finite proof is no longer treated as an undifferentiated search over \(S^{21}\): it is organized by the analytic RRR lemma, four diagonal-class cross-compatibility obligations, and compact lower/upper tail reductions.

Основной bridge-тезис:

\[
\boxed{\text{global Assoc extrema are landscape facts, not PAB-selection criteria.}}
\]

PAB имеет $\operatorname{Assoc}=219$, тогда как глобальный минимум равен $63$. Более того, ни один global minimizer/maximizer не является column-blind.

Layer 1 now also includes a second controlled landscape observable, the hidden continuation contrast

\[
\mathcal H=\mathcal I-\mathcal B.
\]

It has a normalized four-point formula

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d)},
\]

with \(3^7=2187\) normalized terms. On the three exact controlled strata currently certified,

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

The controlled raw maximum is \(H_{tot}=7302\), but it has a small negative local tail \(H_-=6, N_-=3\). Thus \(\mathcal H\) exposes continuation-level signed-cancellation geometry not visible to Assoc.

---

## 1. Базовые объекты

Пусть

\[
S=\mathbb F_3=\{0,1,2\},
\qquad
M=S\times S.
\]

Элемент $M$ записывается как пара $(r,c)$: $r$ — строка, $c$ — столбец. Циклический сдвиг

\[
\sigma(i)=i+1\pmod 3
\]

действует диагонально:

\[
\sigma(r,c)=(r+1,c+1).
\]

Магма — это бинарная операция $\cdot:M\times M\to M$. В Layer 1 рассматриваются магмы, удовлетворяющие:

**AX0 / row-grading**
\[
(x\cdot y)_{row}=x_{row}.
\]

**AX2 / Steiner fiber**
если $x=(r,c_1)$, $y=(r,c_2)$ и $c_1\ne c_2$, то

\[
x\cdot y=(r,\overline{c_1c_2}),
\qquad
\overline{ab}=-a-b\pmod 3.
\]

Диагональные значения $(r,c)\cdot(r,c)$ и cross-row значения при $r_1\ne r_2$ остаются свободными с точностью до $\sigma$-эквивариантности.

---

## 2. Нормальная форма: $\Omega'=\mathcal G\times\Delta$

### 2.1. Cross-rule sector

При $r_1\ne r_2$ операция имеет вид

\[
(r_1,c_1)\cdot(r_2,c_2)
=
(r_1,g(r_1,c_1,r_2,c_2)).
\]

$\sigma$-эквивариантный cross-rule задаётся на 18 представителях, например при $r_1=0$:

\[
(c_1,r_2,c_2)\in S\times\{1,2\}\times S.
\]

Поэтому

\[
\boxed{|\mathcal G|=3^{18}=387\,420\,489.}
\]

Удобно записывать cross-rule как пару таблиц

\[
A,B:S^2\to S,
\]

где $A$ соответствует row-difference $+1$, а $B$ — row-difference $+2$.

### 2.2. Diagonal sector

Diagonal map задаётся тройкой

\[
d=(d_0,d_1,d_2)\in S^3,
\]

где $d_k=\delta(0,k)$, остальные значения восстанавливаются по $\sigma$-эквивариантности. Поэтому

\[
\boxed{|\Delta|=3^3=27.}
\]

### 2.3. Полное пространство

\[
\boxed{\Omega'=\mathcal G\times\Delta\cong S^{18}\times S^3\cong S^{21}.}
\]

\[
\boxed{|\Omega'|=3^{21}=10\,460\,353\,203.}
\]

Стандартная PAB-точка в этом пространстве:

\[
\mathrm{PAB}=(g_1,d=000),
\qquad
g_1(r_1,c_1,r_2,c_2)=r_2.
\]

Layer 1 только указывает, что PAB является одной точкой $\Omega'$. Обоснование её выбора — задача Layer 2.

---

## 3. $S_3$-действие и орбиты

Группа $S_3$ действует на символах $S$ и индуцирует действие на $\mathcal G$, $\Delta$ и $\Omega'$. Эффективная нетривиальная часть для orbit-count задач сводится к транспозиции $\tau$; $C_3$ действует тривиально на нормализованных координатах.

Стабилизированные Burnside-counts:

\[
\boxed{|\mathcal G/S_3|=\frac{3^{18}+3^9}2,}
\]

\[
\boxed{|\Delta/S_3|=15,}
\]

\[
\boxed{|\Omega'/S_3|=\frac{3^{21}+3^{10}}2.}
\]

Практически это означает, что orbit sizes в рассматриваемой нормальной форме равны $1$ или $2$. Для endpoint loci все орбиты имеют размер $2$.

---

## 4. Universal facts and column-blind stratum

Для любой магмы из $\Omega'$:

* $\sigma$ является автоморфизмом;
* AX0 и AX2 выполнены по построению;
* коммутирующие ordered pairs — ровно пары с одинаковой строкой, поэтому commutativity count равен $27/81=1/3$.

### 4.1. Column-blind rules

Cross-rule называется column-blind, если

\[
g(r_1,c_1,r_2,c_2)=h(r_1,r_2),
\]

то есть output-column не читает $c_1,c_2$.

Информационный functional

\[
\mathcal H_{acc}(g)=I(C_{out};C_1,C_2\mid R_1,R_2)
\]

обнуляется ровно на column-blind rules:

\[
\boxed{\mathcal H_{acc}(g)=0\iff g\text{ column-blind}.}
\]

Таких правил ровно

\[
\boxed{9}
\]

из $3^{18}$.

При $d=000$ column-blind table:

| a | b | type | Assoc | label |
|---|---|---|---|---|
| 0 | 0 | trivial | 489 | $g_5=r_1$ |
| 0 | 1 | nontrivial | 273 |  |
| 0 | 2 | nontrivial | 273 |  |
| 1 | 0 | nontrivial | 273 |  |
| 1 | 1 | trivial | 381 |  |
| 1 | 2 | nontrivial | 219 | $g_1=r_2$ / PAB |
| 2 | 0 | nontrivial | 273 |  |
| 2 | 1 | nontrivial | 219 | $\overline{r_1r_2}$ |
| 2 | 2 | trivial | 381 |  |

Итоговая важная неоднозначность:

\[
\min_{\text{nontrivial column-blind},\,d=000}
\operatorname{Assoc}=219
\]

достигается ровно на двух правилах:

\[
g_1=r_2
\qquad\text{и}\qquad
\overline{r_1r_2}.
\]

---

## 5. Assoc: normalized master formula

Используем координаты

\[
(A,B,d),
\qquad
A,B:S^2\to S,
\qquad
d\in S^3.
\]

Положим

\[
M_1(a,e)=A(a,e),
\qquad
M_2(a,e)=B(a,e),
\]

\[
M_0^d(a,e)=
\begin{cases}
d_a, & a=e,\\
-a-e, & a\ne e.
\end{cases}
\]

Тогда normalized raw count равен

\[
rawAssoc(A,B,d)
=
\sum_{b,t,a,e,f\in S}
\mathbf 1\left[
M_t(M_b(a,e),f)
=
M_b\bigl(a,b+M_{t-b}(e-b,f-b)\bigr)
\right].
\]

Есть ровно $3^5=243$ normalized terms, и

\[
\boxed{\operatorname{Assoc}=3\,rawAssoc.}
\]

В v3 endpoint theorem эквивалентен

\[
\boxed{21\le rawAssoc\le199.}
\]

---

## 6. Five-block decomposition and proof skeleton

243 normalized terms разбиваются на пять row-pattern blocks:

| block | condition | raw terms |
|---|---|---:|
| RRR | $b=0,t=0$ | 27 |
| RRS | $b=0,t\ne0$ | 54 |
| RSR | $b\ne0,t=0$ | 54 |
| RSS | $b\ne0,t=b$ | 54 |
| RST | $b\ne0,t\ne0,t\ne b$ | 54 |

\[
rawAssoc=rawRRR+rawRRS+rawRSR+rawRSS+rawRST.
\]

### 6.1. Solved analytic block: RRR

For the one-row operation

\[
m_d(a,e)=M_0^d(a,e),
\]

\[
rawRRR(d)=\#\{(a,e,f):m_d(m_d(a,e),f)=m_d(a,m_d(e,f))\}.
\]

Define

\[
E(d)=\#\{(i,j):i\ne j,\ d_i=d_j\},
\]

\[
N(d)=\#\{(i,j):i\ne j,\ d_i=j,\ d_j=j\}.
\]

Then

\[
\boxed{rawRRR(d)=9+E(d)+2N(d).}
\]

Consequently:

| diagonal class | rawRRR | RRR contribution |
|---|---:|---:|
| permutation | 9 | 27 |
| two-valued, no fixed point | 11 | 33 |
| two-valued, with fixed point | 13 | 39 |
| constant | 19 | 57 |

This is the main hand-readable finite lemma of v3.

### 6.2. Minimum-side equality skeleton

The global minimum $rawAssoc=21$ has exactly two raw equality patterns:

\[
(11,2,2,2,4)
\]

and

\[
(9,2,2,4,4).
\]

Thus the sharp proof targets are:

\[
rawRRR=9\Rightarrow rawCross\ge12,
\]

\[
rawRRR=11\Rightarrow rawCross\ge10.
\]

The minimum is an RRR/RSS trade-off:

\[
(9,2,2,4,4)\leftrightarrow(11,2,2,2,4),
\]

so on all minima

\[
rawRRR+rawRSS=13,
\qquad
rawRRS=rawRSR=2,
\qquad
rawRST=4.
\]

### 6.3. Maximum-side equality skeleton

The global maximum $rawAssoc=199$ has one equality pattern:

\[
(19,36,36,54,54).
\]

All maximizers are on constant diagonals. On every maximizer,

\[
rawRSS=54,
\qquad
rawRST=54.
\]

So the maximum-side proof target is:

\[
rawCross\le180,
\]

with equality only when

\[
d\text{ is constant},\quad
rawRRS=rawRSR=36.
\]

### 6.4. Cross-block compatibility after tail reductions

Write

\[
rawCross=rawRRS+rawRSR+rawRSS+rawRST.
\]

The Global Assoc range is now organized around four diagonal-class compatibility obligations:

| diagonal class | rawRRR | certified rawCross range | rawAssoc consequence | endpoint role |
|---|---:|---:|---:|---|
| permutation | 9 | $12\ldots180$ | $21\ldots189$ | lower endpoint via $(9,2,2,4,4)$ |
| two-valued, no fixed point | 11 | $10\ldots162$ | $21\ldots173$ | lower endpoint via $(11,2,2,2,4)$ |
| two-valued, with fixed point | 13 | $12\ldots174$ | $25\ldots187$ | no global endpoint |
| constant | 19 | $12\ldots180$ | $31\ldots199$ | upper endpoint via $(19,36,36,54,54)$ |

Thus the range theorem follows by diagonal class:

\[
\begin{aligned}
RRR=9&:\quad 9+12\le rawAssoc\le9+180=189,\\
RRR=11&:\quad 11+10\le rawAssoc\le11+162=173,\\
RRR=13&:\quad 13+12\le rawAssoc\le13+174=187,\\
RRR=19&:\quad 19+12\le rawAssoc\le19+180=199.
\end{aligned}
\]

Hence

\[
\boxed{21\le rawAssoc\le199.}
\]

The lower-tail reduction uses the one-table splitting

\[
RRS=RRS_A+RRS_B,
\qquad
RSS=RSS_A+RSS_B.
\]

For a proposed lower threshold \(rawCross\le T\), any feasible pair \((A,B)\) must satisfy

\[
(RRS_A+RSS_A)(A)+(RRS_B+RSS_B)(B)\le T.
\]

This gives a small necessary candidate filter before full cross-block evaluation.

The upper-tail reduction uses half-blocks and the one-table upper part

\[
F_A(A,d)=RRS_A(A,d)+RSS_A(A,d),
\]

\[
F_B(B,d)=RRS_B(B,d)+RSS_B(B,d).
\]

The remaining four half-blocks have at most \(108\) true terms, so

\[
rawCross\ge T\Rightarrow F_A+F_B\ge T-108.
\]

This reduces the global exclusion \(rawAssoc\ge200\) to \(514,356\) candidate pairs, all directly checked infeasible by the compact tail-reduction verifier.

### 6.5. Current proof status

The range theorem is finite-certified and now proof-skeleton stabilized. The RRR block is hand-readable. The cross-block part is reduced to four finite compatibility obligations with a compact recompute verifier. The remaining mathematical enhancement is a fully hand-compressed proof of those four obligations; this is no longer a search or endpoint-discovery task.

---

## 7. Exact Assoc range and certificate

The certified theorem:

\[
\boxed{\min_{\Omega'}\operatorname{Assoc}=63,\qquad
\max_{\Omega'}\operatorname{Assoc}=597.}
\]

Raw form:

\[
\boxed{21\le rawAssoc\le199.}
\]

Certificate stack:

| component | content | status |
|---|---|---|
| finite space | $S^{21}$ | exact |
| master formula | 243 normalized terms | exact |
| five-block decomposition | $RRR+RRS+RSR+RSS+RST$ | exact |
| RRR lemma | $rawRRR(d)=9+E(d)+2N(d)$ | hand-readable finite lemma |
| cross-compatibility obligations | four diagonal-class rawCross ranges | finite-certified |
| lower-tail reduction | $rawAssoc\le20$ excluded by one-table candidate checks | UNSAT / recomputed |
| upper-tail reduction | $rawAssoc\ge200$ reduced to $514,356$ candidates | UNSAT / recomputed |
| endpoints | witnesses and equality cases at 21 and 199 | verified |
| independent checks | direct $9^3=729$ triples and master $3^5=243$ terms | passed |
| $Z(q)$ check | endpoint coefficients $24$ and $6$ | passed |

The compact verifier `scripts/global_assoc_tail_reduction_verify.py` checks the proof-obligation layer only; it is intentionally narrower than the full histogram verifier.

Representative witnesses:

| endpoint | A | B | d | raw | Assoc | raw blocks |
|---|---|---|---|---:|---:|---|
| min | `210210210` | `001021001` | `100` | 21 | 63 | `11,2,2,2,4` |
| max | `110001110` | `011100011` | `111` | 199 | 597 | `19,36,36,54,54` |

---

## 8. Extremal loci

Define

\[
\mathcal M_{63}=\{x\in\Omega':\operatorname{Assoc}(x)=63\},
\]

\[
\mathcal M_{597}=\{x\in\Omega':\operatorname{Assoc}(x)=597\}.
\]

Complete endpoint census:

| locus | points | $S_3$-orbits | $\tau$-fixed | support diagonals | raw block patterns |
|---|---:|---:|---:|---|---|
| $\mathcal M_{63}$ | 24 | 12 | 0 | `100,101,120,121,200,201,220,221` | `(11,2,2,2,4)` x 12; `(9,2,2,4,4)` x 12 |
| $\mathcal M_{597}$ | 6 | 3 | 0 | `000,111,222` | `(19,36,36,54,54)` x 6 |

For the minimum:

\[
\mathcal D_{63}=
\{100,101,120,121,200,201,220,221\}.
\]

For the maximum:

\[
\mathcal D_{597}=
\{000,111,222\}.
\]

---

## 9. Tail geometry and term signatures

The minimum endpoint locus has a radius-1 plateau:

\[
\#\{\{x,y\}\subset\mathcal M_{63}:d_H(x,y)=1\}=12.
\]

Since $|\mathcal M_{63}|=24$, this is a perfect matching. Every such edge keeps $(A,B)$ fixed and changes exactly one diagonal coordinate, exchanging

\[
(9,2,2,4,4)
\longleftrightarrow
(11,2,2,2,4).
\]

The maximum endpoint locus is locally isolated:

\[
\min_{x\ne y\in\mathcal M_{597}}d_H(x,y)=8.
\]

Radius shell summary:

| center | radius | incidences | unique neighbors | min Assoc | max Assoc | mean Assoc |
|---|---|---|---|---|---|---|
| min | 1 | 1008 | 996 | 63 | 150 | 95.25 |
| max | 1 | 252 | 252 | 486 | 579 | 525.2857142857143 |

Term signatures:

| locus | block | terms | always | never | variable |
|---|---|---|---|---|---|
| min | RRR | 27 | 9 | 12 | 6 |
| min | RRS | 54 | 0 | 30 | 24 |
| min | RSR | 54 | 0 | 30 | 24 |
| min | RSS | 54 | 0 | 18 | 36 |
| min | RST | 54 | 0 | 18 | 36 |
| max | RRR | 27 | 15 | 0 | 12 |
| max | RRS | 54 | 12 | 0 | 42 |
| max | RSR | 54 | 12 | 0 | 42 |
| max | RSS | 54 | 54 | 0 | 0 |
| max | RST | 54 | 54 | 0 | 0 |

Interpretation:

\[
\mathcal M_{63}:
\text{ no cross-block term is always true across all minima},
\]

\[
\mathcal M_{597}:
\text{ all RSS and all RST terms are true on every maximum}.
\]

---

## 10. Full distribution $Z(q)$

Define

\[
Z(q)=\sum_{x\in\Omega'}q^{\operatorname{Assoc}(x)}.
\]

v3 computes $Z(q)$ exactly. It has 167 nonzero coefficients and total mass

\[
\sum_a[q^a]Z(q)=3^{21}.
\]

Moments:

\[
\boxed{\mathbb E[\operatorname{Assoc}]=245,}
\]

\[
\boxed{\operatorname{Var}(\operatorname{Assoc})=\frac{27820}{27}.}
\]

Mode:

\[
\boxed{\operatorname{Assoc}=237,\qquad [q^{237}]Z(q)=426\,317\,976.}
\]

Top coefficients:

| rank | raw | Assoc | count | probability |
|---|---|---|---|---|
| 1 | 79 | 237 | 426,317,976 | 4.075560% |
| 2 | 80 | 240 | 424,861,236 | 4.061634% |
| 3 | 78 | 234 | 422,200,248 | 4.036195% |
| 4 | 81 | 243 | 418,884,660 | 4.004498% |
| 5 | 77 | 231 | 412,869,822 | 3.946997% |
| 6 | 82 | 246 | 408,267,852 | 3.903003% |
| 7 | 76 | 228 | 398,330,424 | 3.808002% |
| 8 | 83 | 249 | 393,974,556 | 3.766360% |
| 9 | 75 | 225 | 378,844,818 | 3.621721% |
| 10 | 84 | 252 | 376,365,396 | 3.598018% |

Low tail:

| raw | Assoc | count |
|---|---|---|
| 21 | 63 | 24 |
| 22 | 66 | 36 |
| 23 | 69 | 96 |
| 24 | 72 | 48 |
| 25 | 75 | 126 |
| 26 | 78 | 288 |
| 27 | 81 | 450 |
| 28 | 84 | 480 |
| 29 | 87 | 1,386 |
| 30 | 90 | 1,476 |

High tail:

| raw | Assoc | count |
|---|---|---|
| 178 | 534 | 36 |
| 179 | 537 | 51 |
| 180 | 540 | 12 |
| 181 | 543 | 36 |
| 183 | 549 | 84 |
| 185 | 555 | 18 |
| 187 | 561 | 21 |
| 189 | 567 | 7 |
| 193 | 579 | 12 |
| 199 | 597 | 6 |

The exact assembly is diagonal-orbit reduced:

\[
Z(q)=\sum_{[d]\in\Delta/S_3}|[d]|Z_d(q),
\qquad
Z_d(q)=\sum_{g\in\mathcal G}q^{\operatorname{Assoc}(g,d)}.
\]

Fixed-diagonal summary:

| d | orbit | members | min | min count | max | max count | mean | var |
|---|---|---|---|---|---|---|---|---|
| 000 | 1 | 000 | 93 | 4 | 597 | 2 | 265/1 | 3104/3 |
| 001 | 2 | 001;020 | 75 | 1 | 543 | 2 | 247/1 | 864/1 |
| 002 | 2 | 002;010 | 90 | 16 | 561 | 1 | 257/1 | 968/1 |
| 011 | 2 | 011;022 | 90 | 16 | 561 | 1 | 257/1 | 968/1 |
| 012 | 1 | 012 | 81 | 4 | 567 | 1 | 255/1 | 8812/9 |
| 021 | 1 | 021 | 81 | 22 | 531 | 1 | 235/1 | 2368/3 |
| 100 | 2 | 100;200 | 63 | 2 | 519 | 1 | 231/1 | 6868/9 |
| 101 | 2 | 101;220 | 63 | 2 | 519 | 1 | 231/1 | 6868/9 |
| 102 | 2 | 102;210 | 81 | 22 | 531 | 1 | 235/1 | 2368/3 |
| 110 | 2 | 110;202 | 75 | 1 | 543 | 2 | 247/1 | 864/1 |
| 111 | 2 | 111;222 | 93 | 4 | 597 | 2 | 265/1 | 3104/3 |
| 112 | 2 | 112;212 | 90 | 16 | 561 | 1 | 257/1 | 968/1 |
| 120 | 2 | 120;201 | 63 | 6 | 513 | 1 | 225/1 | 6004/9 |
| 121 | 2 | 121;221 | 63 | 2 | 519 | 1 | 231/1 | 6868/9 |
| 122 | 2 | 122;211 | 75 | 1 | 543 | 2 | 247/1 | 864/1 |

The full coefficient table is included in Appendix A and in `tables/layer1_v3_Zq_full_assoc_distribution.csv`.

---


## 11. Hidden continuation contrast \(\mathcal H\)

Layer 1 has a second landscape observable besides Assoc / \(Z(q)\): the **hidden continuation contrast**. It is operator-lifted because it uses the left regular operators as a measurement device, but it is evaluated over the same normal-form landscape

\[
(A,B,d)\in S^{18}\times S^3.
\]

### 11.1. Definition

For a finite magma \((M,\cdot)\), define

\[
L_x e_y=e_{x\cdot y}.
\]

For triples \((x,y,z)\in M^3\), set

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
I_{tot}=\sum_{x,y,z}\mathcal I(x,y,z),\qquad
B_{tot}=\sum_{x,y,z}\mathcal B(x,y,z),\qquad
H_{tot}=I_{tot}-B_{tot}.
\]

A four-point combinatorial form follows from

\[
\|T_f-T_g\|_{HS}^2=2\#\{w:f(w)\ne g(w)\}.
\]

Thus

\[
\frac12\mathcal I(x,y,z)=\#\{w:(xy)(zw)\ne x((yz)w)\},
\]

\[
\frac12\mathcal B(x,y,z)=\#\{w:((xy)z)w\ne (x(yz))w\}.
\]

The signed spectrum records

\[
H_+=\sum_{\mathcal H(x,y,z)>0}\mathcal H(x,y,z),
\]

\[
H_-=\sum_{\mathcal H(x,y,z)<0}|\mathcal H(x,y,z)|,
\]

\[
N_- = \#\{(x,y,z):\mathcal H(x,y,z)<0\},
\]

so that

\[
\boxed{H_{tot}=H_+-H_-.}
\]

### 11.2. Normalized master formula

In Layer 1 normal coordinates \((A,B,d)\), use normalized variables

\[
x=(0,a),\qquad y=(b,e),\qquad z=(t,f),\qquad w=(u,\ell).
\]

There are \(3^7=2187\) normalized terms, indexed by

\[
b,t,u,a,e,f,\ell\in S.
\]

The certified formula is

\[
\boxed{H_{tot}(A,B,d)=6\,rawH(A,B,d).}
\]

The factor \(6=3\cdot2\) combines free \(\sigma\)-orbit normalization and the Hilbert--Schmidt basis-map distance factor.

### 11.3. Controlled exact atlas

The current exact controlled results are:

| stratum | points | range of \(H_{tot}\) | pure count | max pure \(H_{tot}\) |
|---|---:|---:|---:|---:|
| column-blind \(\times\Delta\) | 243 | \([1836,7302]\) | 159 | 7020 |
| affine \(\times\Delta\) | 19,683 | \([-2268,7302]\) | 723 | 7020 |
| degree \(\le2\) \(\times\Delta\) | 14,348,907 | \([-2268,7302]\) | 3,177 | 7020 |

Here pure means \(N_-=0\). Therefore, on all three controlled strata,

\[
\boxed{\max\{H_{tot}:N_-=0\}=7020.}
\]

PAB has

\[
H_{tot}=7020,\qquad H_+=7020,\qquad H_-=0,\qquad N_-=0.
\]

The controlled raw maximum has

\[
H_{tot}=7302,\qquad H_+=7308,\qquad H_-=6,\qquad N_-=3.
\]

Thus the controlled transition

\[
7020\to7302
\]

uses a small local signed-cancellation tail. Term signatures localize this negative tail to the RRR block.

The controlled minimum \(H_{tot}=-2268\) splits into two signed-spectrum classes:

| class | points | effective orbits | Assoc | \(H_+\) | \(H_-\) | \(N_-\) |
|---|---:|---:|---:|---:|---:|---:|
| H-min A | 2 | 1 | 81 | 972 | 3240 | 288 |
| H-min B | 6 | 4 | 189 | 1404 | 3672 | 432 |

### 11.4. Local shell geometry

Exact Hamming shells of radii 1 and 2 around PAB, row-complement, H-frontier representatives, and Assoc endpoint representatives show:

* PAB and row-complement have radius-1 neighbors with \(H_{tot}=7302\).
* Their radius-2 shell is entirely below \(7020\).
* The H-max locus \(H_{tot}=7302\) is a radius-2 cap: no radius-2 shell point reaches \(7302\).
* The H-min locus \(H_{tot}=-2268\) is a strict local minimum through radius 2 for both signed classes.

### 11.5. Status

The hidden continuation contrast is a controlled Layer 1H theorem package. Its current certified scope is:

\[
\text{master formula}
+\text{controlled exact atlas}
+\text{signed spectrum}
+\text{frontier orbits}
+\text{term signatures}
+\text{local shells}
+\text{verifier stack}.
\]

The global \(\Omega'\) questions remain future certification problems:

\[
\min_{\Omega'}H_{tot}=-2268?,\qquad
\max_{\Omega'}H_{tot}=7302?,\qquad
\max_{\Omega'}\{H_{tot}:N_-=0\}=7020?.
\]

The H-module is documented in the bundled `layer1H/` package and referenced in the artifact map below.

---

## 12. Selection bridge: what Layer 1 does and does not select

Layer 1 v3 proves that global Assoc extrema are not PAB-selection criteria.

\[
\operatorname{Assoc}(\mathrm{PAB})=219,
\]

while

\[
\min_{\Omega'}\operatorname{Assoc}=63.
\]

Also,

\[
\boxed{\text{no global minimizer or maximizer is column-blind.}}
\]

The selection-relevant landscape fact is instead:

\[
\mathcal H_{acc}=0
\iff
\text{column-blind},
\qquad
|\mathcal G_{cb}|=9.
\]

Inside the nontrivial column-blind stratum at $d=000$, Assoc minimization leaves exactly two cross-rules:

\[
g_1=r_2
\qquad\text{and}\qquad
\overline{r_1r_2}.
\]

Thus Layer 1 supplies the landscape and the obstruction:

\[
\boxed{\text{Layer 1 leaves a PAB/competitor ambiguity; Layer 2 resolves it.}}
\]

Layer 2 uses additional criteria, especially symplectic/drift-kick, to select PAB. Layer 1 should not claim that PAB is selected by global Assoc minimization.

---

## 13. Structure bridge toward Layer 3

Targeted structure profiles were computed for:

\[
30\text{ endpoint points} + 9\text{ column-blind points at }d=000.
\]

Compact summary:

| family | points | orbits | Assoc | Aut sizes | End sizes | idempotents | identity profile |
|---|---:|---:|---|---|---|---|---|
| global min | 24 | 12 | 63 | 3 | 3 | 0 | $I_1,I_2,I_3$ false; $(\star)$ true |
| global max | 6 | 3 | 597 | 6 | 33 | 3 | $I_1,I_2,I_3$ true; $(\star)$ true |
| PAB / competitor anchors | 2 | — | 219 | 6 | 9 | 3 | $I_1,I_2,I_3$ true; $(\star)$ true |

Important consequence:

\[
I_1,I_2,I_3
\]

do not characterize PAB inside the landscape: they also hold on the global maxima and on the competitor. Similarly, basic Aut/End/rank/absorption profiles do not separate PAB from $\overline{r_1r_2}$.

This is a Layer 3 bridge, not a Layer 1 selector.

---

## 14. Updated open questions after v3+H

Closed compared to earlier Layer 1 drafts:

1. global Assoc extrema on $\Omega'$;
2. endpoint support diagonals;
3. full endpoint loci up to $S_3$;
4. full exact $Z(q)$.

Remaining / future work:

1. **Full hand analytic compression of cross-block compatibility.**  
   The RRR block is solved and the cross-block part has been compressed to four diagonal-class compatibility obligations with compact tail-reduction verification. The remaining task is to replace those finite candidate checks by short structural lemmas.

2. **Formal proof-log artifact for the range theorem.**  
   Current status is a finite computational certificate plus compact recompute verifier. A DRAT/MaxSAT/MILP/BDD-style independently checkable proof log would further strengthen it, but is not required for the current Layer 1 theorem package.

3. **Global canonical representative map for all $\Omega'/S_3$.**  
   Endpoint orbits are classified, but a full atlas navigator remains infrastructure/future work.

4. **Elementary formula grammar.**  
   The historical $g_1,\ldots,g_6$ list is not a classification of $\mathcal G$; a formal grammar of elementary cross-rules remains open.

5. **Full structural distributions over $\Omega'$.**  
   Targeted Aut/End/identity profiles are available, but full distributions are not needed for v3 and remain future work.

6. **Global H-certificate on \(\Omega'\).**  
   The controlled Layer 1H module proves \([-2268,7302]\) and pure frontier \(7020\) on three exact controlled strata. The global questions over all \(\Omega'\) remain open: whether \(\min_{\Omega'}H_{tot}=-2268\), \(\max_{\Omega'}H_{tot}=7302\), and \(\max_{\Omega'}\{H_{tot}:N_-=0\}=7020\).

7. **Expansion to $\Omega'_{full}$ without AX2.**  
   This changes the family and belongs to a later programme.

---

## 15. Status registry

| # | claim | status | support |
|---|---|---|---|
| 1 | Нормальная форма $\Omega^\prime\cong S^{18}\times S^3$ и $\|\Omega^\prime\|=3^{21}$ | [V] | v1/v7 classification + v3 final |
| 2 | $\|\mathcal G\|=3^{18}$, $\|\Delta\|=27$ | [V] | orbit count under $\sigma$ |
| 3 | $\|\Delta/S_3\|=15$ и $\|\Omega^\prime/S_3\|=(3^{21}+3^{10})/2$ | [V] | Burnside / effective $C_2$ |
| 4 | $\min\operatorname{Assoc}=63$, $\max\operatorname{Assoc}=597$ | [V-certified/computational] | F3 B&B certificate + tail-reduction verifier + independent checks + $Z(q)$ |
| 5 | RRR lemma $rawRRR(d)=9+E(d)+2N(d)$ | [V-exact finite lemma] | Block 02 |
| 6 | Полные extremal loci: $24/12$ minima, $6/3$ maxima/orbits | [V-certified/computational] | Block 03 + verifier |
| 7 | Полный $Z(q)$ известен; $E[Assoc]=245$, $Var=27820/27$ | [V-certified/computational] | Block 04 + verifier |
| 8 | $\mathcal H_{acc}=0\iff$ column-blind; таких правил 9 | [V] | Layer 1/2 bridge |
| 9 | Hidden continuation contrast master formula $H_{tot}=6rawH$ | [V-certified/computational] | Layer 1H verifier: direct $9^4$ vs normalized $3^7$ |
| 10 | Exact controlled H-atlas on column-blind, affine, and degree $\le2$ strata | [V-certified/computational] | Layer 1H controlled atlas + verifier |
| 11 | Controlled pure frontier $\max\{H_{tot}:N_-=0\}=7020$ | [V-certified/computational] | Layer 1H frontier tables + verifier |
| 12 | Global Assoc extrema не селектируют PAB | [V] | Block 05 |
| 13 | PAB/competitor ambiguity after column-blind + nontrivial + Assoc | [V] | column-blind $d=000$ table |
| 14 | Полный ручной proof cross-block compatibility | [Open] | compact four-obligation certificate exists; hand-compression remains future work |
| 15 | Global H-range and global H pure-frontier theorem on $\Omega'$ | [Open] | controlled strata certified; global certificate future work |

---

## 16. Minimal artifact map

| path | role |
|---|---|
| layer1_landscape_v3.md | финальный самодостаточный текст Layer 1 v3 |
| tables/layer1_v3_Zq_full_assoc_distribution.csv | полный coefficient table для $Z(q)$ |
| tables/layer1_v3_fixed_diagonal_summary.csv | 15 fixed-diagonal orbit histograms summary |
| tables/layer1_v3_extremal_loci_solutions.csv | все 30 endpoint points |
| tables/layer1_v3_extremal_loci_orbits.csv | 15 endpoint $S_3$-orbits |
| tables/layer1_v3_column_blind_d000_table.csv | column-blind selection bridge table |
| tables/layer1_v3_structure_bridge_summary.csv | targeted Aut/End/identity structure bridge |
| tables/layer1_v3_term_signature_summary.csv | term signatures on endpoint loci |
| scripts/verify_layer1_v3_final.py | compact final verifier |
| scripts/global_assoc_tail_reduction_verify.py | compact Global Assoc proof-obligation verifier |
| scripts/f3_cert_extrema.cpp | core F3 branch-and-bound certificate kernel |
| scripts/full_zq_vectorized_histogram.cpp | exact fixed-diagonal histogram kernel |
| layer1H/Layer1H.md | full Layer 1H hidden continuation contrast module |
| layer1H/Layer1H_controlled_frontier_theorem.md | compact theorem-style H statement |
| layer1H/Layer1H_appendix_for_layer1_v3.md | source appendix patch used for the integrated §11 |
| layer1H/tables/H_controlled_summary.csv | controlled H range summary |
| layer1H/tables/H_degree2_exact_summary.csv | degree $\le2$ exact H summary |
| layer1H/tables/H_frontier_locus_class_summary.csv | signed frontier class summary |
| layer1H/tables/H_frontier_term_signature_summary.csv | H-frontier term signatures |
| layer1H/tables/H_local_shell_summary.csv | H local shell summary |
| layer1H/scripts/verify_layer1H_final.py | Layer 1H final verifier |

---

## Appendix A. Exact coefficient table for $Z(q)$

| raw | Assoc | count |
|---|---|---|
| 21 | 63 | 24 |
| 22 | 66 | 36 |
| 23 | 69 | 96 |
| 24 | 72 | 48 |
| 25 | 75 | 126 |
| 26 | 78 | 288 |
| 27 | 81 | 450 |
| 28 | 84 | 480 |
| 29 | 87 | 1386 |
| 30 | 90 | 1476 |
| 31 | 93 | 2706 |
| 32 | 96 | 3372 |
| 33 | 99 | 5262 |
| 34 | 102 | 8388 |
| 35 | 105 | 11634 |
| 36 | 108 | 17976 |
| 37 | 111 | 25338 |
| 38 | 114 | 36924 |
| 39 | 117 | 52386 |
| 40 | 120 | 75600 |
| 41 | 123 | 106008 |
| 42 | 126 | 146928 |
| 43 | 129 | 206928 |
| 44 | 132 | 285936 |
| 45 | 135 | 398337 |
| 46 | 138 | 549468 |
| 47 | 141 | 760026 |
| 48 | 144 | 1049004 |
| 49 | 147 | 1436610 |
| 50 | 150 | 1972308 |
| 51 | 153 | 2678160 |
| 52 | 156 | 3620664 |
| 53 | 159 | 4893906 |
| 54 | 162 | 6548556 |
| 55 | 165 | 8739069 |
| 56 | 168 | 11584188 |
| 57 | 171 | 15329643 |
| 58 | 174 | 20041128 |
| 59 | 177 | 26054448 |
| 60 | 180 | 33624936 |
| 61 | 183 | 43030839 |
| 62 | 186 | 54443208 |
| 63 | 189 | 68263794 |
| 64 | 192 | 84515664 |
| 65 | 195 | 103638168 |
| 66 | 198 | 125592696 |
| 67 | 201 | 150156153 |
| 68 | 204 | 177129780 |
| 69 | 207 | 206386101 |
| 70 | 210 | 236852028 |
| 71 | 213 | 268059990 |
| 72 | 216 | 298806528 |
| 73 | 219 | 328316196 |
| 74 | 222 | 355203096 |
| 75 | 225 | 378844818 |
| 76 | 228 | 398330424 |
| 77 | 231 | 412869822 |
| 78 | 234 | 422200248 |
| 79 | 237 | 426317976 |
| 80 | 240 | 424861236 |
| 81 | 243 | 418884660 |
| 82 | 246 | 408267852 |
| 83 | 249 | 393974556 |
| 84 | 252 | 376365396 |
| 85 | 255 | 356471142 |
| 86 | 258 | 334836984 |
| 87 | 261 | 312350886 |
| 88 | 264 | 289097340 |
| 89 | 267 | 266155647 |
| 90 | 270 | 243401184 |
| 91 | 273 | 221406327 |
| 92 | 276 | 200583132 |
| 93 | 279 | 180854604 |
| 94 | 282 | 162382656 |
| 95 | 285 | 145425681 |
| 96 | 288 | 129572592 |
| 97 | 291 | 115236783 |
| 98 | 294 | 102106920 |
| 99 | 297 | 90289886 |
| 100 | 300 | 79564440 |
| 101 | 303 | 70045857 |
| 102 | 306 | 61418148 |
| 103 | 309 | 53814315 |
| 104 | 312 | 46975560 |
| 105 | 315 | 41001972 |
| 106 | 318 | 35652888 |
| 107 | 321 | 30986835 |
| 108 | 324 | 26867452 |
| 109 | 327 | 23314956 |
| 110 | 330 | 20089764 |
| 111 | 333 | 17313030 |
| 112 | 336 | 14905020 |
| 113 | 339 | 12832854 |
| 114 | 342 | 10963272 |
| 115 | 345 | 9423501 |
| 116 | 348 | 8031888 |
| 117 | 351 | 6880749 |
| 118 | 354 | 5857164 |
| 119 | 357 | 5007942 |
| 120 | 360 | 4245852 |
| 121 | 363 | 3639651 |
| 122 | 366 | 3084528 |
| 123 | 369 | 2639835 |
| 124 | 372 | 2237136 |
| 125 | 375 | 1910016 |
| 126 | 378 | 1601784 |
| 127 | 381 | 1363473 |
| 128 | 384 | 1147356 |
| 129 | 387 | 971835 |
| 130 | 390 | 807288 |
| 131 | 393 | 677721 |
| 132 | 396 | 566616 |
| 133 | 399 | 473250 |
| 134 | 402 | 398100 |
| 135 | 405 | 334035 |
| 136 | 408 | 272040 |
| 137 | 411 | 232596 |
| 138 | 414 | 190764 |
| 139 | 417 | 158112 |
| 140 | 420 | 128508 |
| 141 | 423 | 108372 |
| 142 | 426 | 84948 |
| 143 | 429 | 72480 |
| 144 | 432 | 58632 |
| 145 | 435 | 48387 |
| 146 | 438 | 37236 |
| 147 | 441 | 32109 |
| 148 | 444 | 23580 |
| 149 | 447 | 20133 |
| 150 | 450 | 14640 |
| 151 | 453 | 13089 |
| 152 | 456 | 9924 |
| 153 | 459 | 9141 |
| 154 | 462 | 6936 |
| 155 | 465 | 6528 |
| 156 | 468 | 4596 |
| 157 | 471 | 4425 |
| 158 | 474 | 3252 |
| 159 | 477 | 2832 |
| 160 | 480 | 2004 |
| 161 | 483 | 1680 |
| 162 | 486 | 1284 |
| 163 | 489 | 945 |
| 164 | 492 | 900 |
| 165 | 495 | 852 |
| 166 | 498 | 588 |
| 167 | 501 | 426 |
| 168 | 504 | 144 |
| 169 | 507 | 270 |
| 170 | 510 | 156 |
| 171 | 513 | 305 |
| 172 | 516 | 132 |
| 173 | 519 | 210 |
| 174 | 522 | 84 |
| 175 | 525 | 210 |
| 176 | 528 | 36 |
| 177 | 531 | 111 |
| 178 | 534 | 36 |
| 179 | 537 | 51 |
| 180 | 540 | 12 |
| 181 | 543 | 36 |
| 183 | 549 | 84 |
| 185 | 555 | 18 |
| 187 | 561 | 21 |
| 189 | 567 | 7 |
| 193 | 579 | 12 |
| 199 | 597 | 6 |

---

## Appendix B. Recommended Layer 2 handoff

The Layer 2 starting point should be:

\[
\Omega'
\xrightarrow{\mathcal H_{acc}=0}
9\times 27
\xrightarrow{\text{nontrivial}}
6\times 27
\xrightarrow{\min\operatorname{Assoc}\text{ inside CB}}
2\times 27
\xrightarrow{\text{symplectic/drift-kick}}
1\times 27
\xrightarrow{H_{diag}=0}
1\times 3
\xrightarrow{\text{diagonal idempotence}}
1.
\]

Layer 1 v3 does not prove this chain as selection. It supplies the landscape facts that make the chain necessary.

---

**Final v3+H statement.** Layer 1 is now a finite landscape theorem package: normal form, orbit counts, exact Assoc range, endpoint loci, local tail geometry, full $Z(q)$, hidden continuation contrast $\mathcal H$ with controlled frontier atlas, and bridge facts to Layers 2 and 3. The remaining mathematical enhancements are hand proof-compression of the Assoc cross-block compatibility certificate and global certification of the H-range / pure-frontier theorem over all $\Omega'$.
