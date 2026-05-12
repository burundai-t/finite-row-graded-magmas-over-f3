# Layer 3 Front A — analytic spectral/Jordan hardening

**Status:** closed in Layer 3 v1.1.  
**Scope:** replace the verifier-only statement about spectra, minimal polynomials, and the off-diagonal Jordan block by a row-fiber proof.

Layer 3 studies the already selected PAB point
\[
(g_1,000)=\mathrm{PAB},
\]
imported from the finite Layer 2 selector. The relevant multiplication is
\[
(r_1,c_1)\cdot(r_2,c_2)=
\begin{cases}
(r_1,r_2),&r_1\ne r_2,\\
(r_1,\overline{c_1c_2}),&r_1=r_2,\ c_1\ne c_2,\\
(r_1,r_1),&r_1=r_2,\ c_1=c_2,
\end{cases}
\]
where \(\overline{ab}=-a-b\pmod3\).

---

## 1. Row-fiber normal form

Let
\[
V=k[M],\qquad F_q=\operatorname{span}\{e_{(q,d)}:d\in S\}.
\]
For fixed \(x=(r,c)\), write
\[
L_x=\iota_r A_x,
\]
where \(A_x:V\to F_r\) is \(L_x\) with codomain restricted to the target row, and \(\iota_r:F_r\hookrightarrow V\) is inclusion. Define the fiber block
\[
B_{r,c}=A_x\iota_r=L_x|_{F_r}:F_r\to F_r.
\]

For a source row \(q\ne r\), PAB gives
\[
A_x(e_{(q,d)})=e_{(r,q)}\qquad(d\in S).
\]
Thus each cross-row source fiber is collapsed by the augmentation functional onto the target basis vector indexed by the source row.

On the same row,
\[
B_{r,c}e_{(r,d)}=
\begin{cases}
e_{(r,r)},& d=c,\\
e_{(r,\overline{cd})},& d\ne c.
\end{cases}
\]

Because \(A_x\iota_r=B_{r,c}\), the powers satisfy
\[
\boxed{L_x^n=\iota_r B_{r,c}^{\,n-1}A_x\qquad(n\ge1).}
\]
The block form is therefore
\[
L_x=\begin{pmatrix}
B_{r,c}&U_s&U_t\\
0&0&0\\
0&0&0
\end{pmatrix}
\]
for \(\{s,t\}=S\setminus\{r\}\). Hence
\[
\boxed{\chi_{L_x}(\lambda)=\lambda^6\chi_{B_{r,c}}(\lambda).}
\]

Finally, \(A_x\) is onto \(F_r\): the two cross-row blocks give \(e_{(r,s)}\) and \(e_{(r,t)}\), while \(B_{r,c}e_{(r,c)}=e_{(r,r)}\). Therefore
\[
\boxed{\operatorname{rank}L_x=3,
\qquad
\dim\ker L_x=6.}
\]

---

## 2. Diagonal case

Let \(x=(r,r)\), and let \(s,t\) be the two elements of \(S\setminus\{r\}\). Then
\[
B_{r,r}e_{(r,r)}=e_{(r,r)},
\qquad
B_{r,r}e_{(r,s)}=e_{(r,t)},
\qquad
B_{r,r}e_{(r,t)}=e_{(r,s)}.
\]
So
\[
B_{r,r}^2=I_{F_r},
\qquad
\chi_{B_{r,r}}(\lambda)=(\lambda-1)^2(\lambda+1).
\]
Using \(L_x^n=\iota_rB^{n-1}A_x\),
\[
L_x^3=\iota_rB_{r,r}^{2}A_x=\iota_rA_x=L_x.
\]
Thus \(L_x\) is annihilated by
\[
\lambda(\lambda-1)(\lambda+1).
\]
The eigenvalues \(1\), \(-1\), and \(0\) all occur: \(1\) and \(-1\) already occur on \(F_r\), and \(0\) occurs because \(\operatorname{rank}L_x=3<9\). Therefore the minimal polynomial is exactly
\[
\boxed{\mu_{L_x}(\lambda)=\lambda(\lambda-1)(\lambda+1).}
\]
The characteristic polynomial is
\[
\boxed{\chi_{L_x}(\lambda)=\lambda^6(\lambda-1)^2(\lambda+1).}
\]
The zero algebraic multiplicity is \(6\), and \(\dim\ker L_x=6\). Since the minimal polynomial is square-free, \(L_x\) is semisimple.

---

## 3. Off-diagonal case

Let \(x=(r,c)\) with \(c\ne r\), and put
\[
u=\overline{rc}=-r-c\pmod3.
\]
Then \(\{r,c,u\}=S\), and the same-row block is
\[
B_{r,c}e_{(r,c)}=e_{(r,r)},
\qquad
B_{r,c}e_{(r,r)}=e_{(r,u)},
\qquad
B_{r,c}e_{(r,u)}=e_{(r,r)}.
\]
The vectors
\[
e_{(r,r)}+e_{(r,u)},
\qquad
e_{(r,r)}-e_{(r,u)},
\qquad
e_{(r,c)}-e_{(r,u)}
\]
are eigenvectors of \(B_{r,c}\) with eigenvalues \(1\), \(-1\), and \(0\), respectively. Hence
\[
\chi_{B_{r,c}}(\lambda)=\lambda(\lambda-1)(\lambda+1),
\qquad
B_{r,c}^3=B_{r,c},
\qquad
\operatorname{rank}B_{r,c}=2.
\]
Consequently,
\[
\boxed{\chi_{L_x}(\lambda)=\lambda^7(\lambda-1)(\lambda+1).}
\]
The power identity becomes
\[
L_x^4=\iota_rB_{r,c}^{3}A_x=\iota_rB_{r,c}A_x=L_x^2.
\]
So \(L_x\) is annihilated by
\[
\lambda^2(\lambda-1)(\lambda+1).
\]

The square on the zero factor is necessary. Choose any basis vector \(y\in F_c\). Since \(c\ne r\), this is a cross-row input, and
\[
L_x y=e_{(r,c)}.
\]
But
\[
L_x^3y=
\iota_rB_{r,c}^{2}A_xy
=\iota_rB_{r,c}^{2}e_{(r,c)}
=e_{(r,u)}\ne e_{(r,c)}.
\]
Therefore
\[
L_x^3\ne L_x.
\]
The polynomial \(\lambda(\lambda-1)(\lambda+1)\) does not annihilate \(L_x\), while \(\lambda^2(\lambda-1)(\lambda+1)\) does. Since the \(\pm1\) eigenspaces occur already inside \(F_r\), the exact minimal polynomial is
\[
\boxed{\mu_{L_x}(\lambda)=\lambda^2(\lambda-1)(\lambda+1).}
\]

The algebraic multiplicity of \(0\) is \(7\), from \(\chi_{L_x}\). The geometric multiplicity is
\[
\dim\ker L_x=9-\operatorname{rank}L_x=6.
\]
Moreover
\[
\operatorname{rank}L_x^2=\operatorname{rank}B_{r,c}=2,
\qquad
\dim\ker L_x^2=7.
\]
Thus the zero-primary Jordan structure has six blocks with total size seven and nilpotent index two. Therefore
\[
\boxed{
J_0(L_x)=J_2(0)\oplus J_1(0)^{\oplus5}.
}
\]
This proves the central Front A distinction:
\[
\boxed{
\text{diagonal }L_x\text{ are semisimple, while off-diagonal }L_x\text{ carry exactly one }J_2(0).
}
\]

---

## 4. Front A theorem statement

For the PAB left regular operators on \(k[M]\):

\[
x=(r,r)
\Longrightarrow
\mu_{L_x}(t)=t(t-1)(t+1),
\quad
\chi_{L_x}(t)=t^6(t-1)^2(t+1),
\quad
L_x\text{ semisimple}.
\]

\[
x=(r,c),\ r\ne c
\Longrightarrow
\mu_{L_x}(t)=t^2(t-1)(t+1),
\quad
\chi_{L_x}(t)=t^7(t-1)(t+1),
\quad
J_0=J_2(0)\oplus J_1(0)^{\oplus5}.
\]

The verifier `scripts/verify_layer3_frontA.py` checks the normal forms and writes:

- `tables/layer3_frontA_fiber_block_normal_forms.csv`;
- `tables/layer3_frontA_operator_spectral_proof_audit.csv`;
- `tables/layer3_frontA_offdiag_nonsemisimple_witnesses.csv`;
- `tables/layer3_frontA_verifier_checks.csv`.

Front A is therefore closed at the Layer 3 v1.1 standard: the result is now a structural proof with a finite audit table, not a bare matrix-computation claim.
