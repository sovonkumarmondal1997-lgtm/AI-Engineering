# SYLLABUS — 03-Eigenvalues-SVD-and-Low-Rank-Structure (S4B-03)

**Stage 4B — Mathematics for Machine Learning · Module 03 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SciPy, Matplotlib, Pillow, pytest where stated). This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Eigenvalues and eigenvectors | `01-eigenvalues-and-eigenvectors.md` | Beginner → Intermediate |
| 3 | Eigendecomposition and matrix powers | `02-eigendecomposition-and-matrix-powers.md` | Intermediate |
| 4 | SVD: intuition and computation | `03-singular-value-decomposition-intuition-and-computation.md` | Intermediate → Advanced |
| 5 | Low-rank approximation | `04-low-rank-approximation.md` | Advanced |
| 6 | Matrix norms: Frobenius and spectral | `05-matrix-norms-frobenius-and-spectral.md` | Advanced |
| 7 | Practice question bank | `practice-questions.md` | All levels |
| 8 | Project index | `Projects/README.md` | Intermediate |
| 9 | Project: eigenvalue power iteration | `Projects/01-eigenvalue-power-iteration.md` | Intermediate → Advanced |
| 10 | Project: image compression with SVD | `Projects/02-image-compression-with-svd.md` | Intermediate → Advanced |

**Prerequisites:** Module 01 (norms, orthogonality, projection), Module 02 (matrix multiplication, transpose, orthogonal and symmetric matrices, determinant, rank, `solve` vs `inv`). Stage 4A Module 14 (complex numbers) is **optional**: eigenvalues of rotations are complex, and Lesson 1 gives the minimum needed. **Plan slot:** week 4 of `../00-Stage-4-Overview/learning-plan.md`.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library, assertion they agree) → Failure modes → ML link. Shapes are written in comments throughout.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Eigenvalues and the SVD are how you find the **important directions** of a matrix and how much each one matters. PCA is an eigendecomposition of a covariance matrix. Image and embedding compression, latent semantic analysis, recommender-system factorization, and low-rank adapters all rest on the SVD. Eigenvalues of Jacobians and weight matrices decide whether iterations and recurrent networks explode or vanish. The same two ideas also supply the diagnostics: condition number, effective rank, spectral norm.

### 1.2 Outcomes

1. Compute eigenvalues and eigenvectors with NumPy; verify `Av = λv`; use `trace = Σλ` and `det = Πλ` as sanity checks.
2. Choose the right routine: `eigh` for symmetric matrices, `eig` for general, `svd` for anything rectangular.
3. Use `A = VΛV⁻¹` to compute `Aᵏ`; predict growth, decay, or oscillation from eigenvalues.
4. Explain the SVD `A = UΣVᵀ` geometrically (rotate, stretch, rotate) and relate singular values to eigenvalues of `AᵀA`.
5. Build the best rank-`k` approximation, state its exact error, and choose `k` from an energy curve.
6. Compute and interpret Frobenius, spectral, and nuclear norms; relate them to singular values.
7. Implement power iteration from scratch and explain its convergence rate.
8. Compress an image with SVD and report compression ratio versus quality with honest numbers.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Eigenvalues and eigenvectors | PCA directions, PageRank, stability | `eig` verification suite |
| 2 | Eigendecomposition and powers | RNN dynamics, Markov chains, diffusion | `matrix_power` via eigenbasis |
| 3 | SVD | PCA via SVD, pseudo-inverse, condition number | SVD from `eigh(AᵀA)` vs NumPy |
| 4 | Low-rank approximation | Compression, LSA, LoRA idea, embeddings | Error-vs-rank curves |
| 5 | Matrix norms | Spectral norm control, gradient and weight diagnostics | Norm identity tests |

### 1.4 Concept map

```
square A ──► eigenvalues λ, eigenvectors v ──► A = VΛV⁻¹ ──► Aᵏ, stability, Markov, PCA (symmetric case)
any A (m×n) ──► SVD: A = UΣVᵀ ──► σᵢ² = eig(AᵀA) ──► rank, cond, pinv
                      └──► keep top k ──► best rank-k approximation (Eckart–Young) ──► compression / LSA / LoRA
                      └──► ‖A‖_F = √Σσᵢ², ‖A‖₂ = σ₁, ‖A‖_* = Σσᵢ
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "scipy>=1.11" matplotlib pillow pytest
```

Seed randomness; compare with `np.allclose`; every from-scratch routine gets a reference test; sort eigen/singular values explicitly (libraries differ in order and sign conventions); never compare eigenvectors without fixing sign.

### 1.6 Checkpoint (from the stage plan)

Rank-`k` SVD reconstruction error (Frobenius) equals the square root of the sum of squared discarded singular values, within tolerance.

### Check yourself (Unit 1)

1. Which NumPy function for a symmetric matrix, and why prefer it?
2. Which decomposition applies to a rectangular matrix?

**Reference answers:** (1) `np.linalg.eigh`: guaranteed real eigenvalues, orthonormal eigenvectors, sorted ascending, faster and more accurate than `eig` for symmetric input. (2) The SVD.

---

## Unit 2 — Eigenvalues and eigenvectors (`01-…md`)

### 2.1 Why ML needs this

Eigenvectors of a covariance matrix are the principal components. The dominant eigenvector of a link matrix is PageRank. Eigenvalues of a Jacobian or of a recurrent weight matrix decide whether a signal grows or shrinks across steps.

### 2.2 Intuition

Most vectors change direction when a matrix acts on them. **Eigenvectors are the special directions that only get stretched or flipped**: `Av = λv`. The eigenvalue `λ` is the stretch factor (negative flips). A matrix that rotates has no real such direction; its eigenvalues are complex.

### 2.3 Mechanics

- **Definition:** `Av = λv`, `v ≠ 0`; equivalently `(A − λI)v = 0` has a non-trivial solution, so `det(A − λI) = 0` (the **characteristic polynomial**).
- For an `n×n` matrix there are `n` eigenvalues counted with multiplicity (possibly complex).
- **Sanity checks:** `trace(A) = Σλᵢ`, `det(A) = Πλᵢ`.
- Eigenvectors are defined **up to scale** (and sign): `v` and `−v` are equally valid.
- **Symmetric real `A`:** all `λ` real; eigenvectors for distinct eigenvalues are orthogonal; can be chosen orthonormal (spectral theorem; proof in 4C-01).
- **Triangular matrix:** eigenvalues are the diagonal entries.
- **Eigenvalue `0`** ⇔ singular matrix.
- **Rotation by `θ`** (2D): eigenvalues `cos θ ± i sin θ`; no real eigenvectors unless `θ ∈ {0, π}`.
- **Covariance matrix** `C = XcᵀXc/(n−1)`: symmetric PSD, so eigenvalues are ≥ 0 and are the **variances along the principal axes**.

**Worked example:** `A = [[2, 1], [1, 2]]`. `det(A − λI) = (2−λ)² − 1 = 0` → `λ = 3, 1`. For `λ=3`: `v = (1, 1)/√2`; for `λ=1`: `v = (1, −1)/√2`. Check: `trace = 4 = 3+1`, `det = 3 = 3·1`.

### 2.4 Code

```python
import numpy as np

A = np.array([[2., 1.], [1., 2.]])
w, V = np.linalg.eig(A)                       # columns of V are eigenvectors
for lam, v in zip(w, V.T):
    assert np.allclose(A @ v, lam * v)        # the definition
assert np.isclose(w.sum(), np.trace(A)) and np.isclose(w.prod(), np.linalg.det(A))

# symmetric -> use eigh: real, orthonormal, ascending
w_s, Q = np.linalg.eigh(A)
assert np.allclose(Q.T @ Q, np.eye(2)) and np.all(np.diff(w_s) >= 0)

# rotation: complex eigenvalues
th = np.pi / 3
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
print(np.linalg.eigvals(R))                   # cos(th) ± i sin(th), modulus 1
assert np.allclose(np.abs(np.linalg.eigvals(R)), 1.0)

# PCA directions = eigenvectors of the covariance matrix
rng = np.random.default_rng(0)
X = rng.normal(size=(500, 2)) @ np.array([[3., 0.], [1., 0.5]])     # correlated 2-D cloud
Xc = X - X.mean(axis=0)
C = Xc.T @ Xc / (len(Xc) - 1)
assert np.allclose(C, np.cov(X.T))
evals, evecs = np.linalg.eigh(C)
order = np.argsort(evals)[::-1]                # descending variance
evals, evecs = evals[order], evecs[:, order]
print("explained variance ratio:", evals / evals.sum())
proj_var = (Xc @ evecs).var(axis=0, ddof=1)    # variance along each principal axis
assert np.allclose(proj_var, evals)
```

Characteristic polynomial check: `np.poly(A)` gives its coefficients and `np.roots(np.poly(A))` returns the eigenvalues. This is for teaching only; real solvers do **not** work through the polynomial (it is numerically poor for larger `n`).

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `eig` on a symmetric matrix | Tiny imaginary parts, unsorted, non-orthogonal vectors | Use `eigh` |
| Comparing eigenvectors across libraries | "Different" signs | Fix a sign convention (e.g., largest component positive) |
| Assuming eigenvalues are sorted | Wrong "top" component | `argsort` explicitly |
| Real-world covariance not exactly symmetric | `eigh` reads only one triangle | Symmetrize `(C + Cᵀ)/2` |
| Assuming a non-symmetric matrix has orthogonal eigenvectors | Wrong projections | Check `VᵀV` |
| Expecting real eigenvalues from a non-symmetric matrix | `complex128` output | Check `np.iscomplexobj` |
| Root-finding on the characteristic polynomial | Large errors for `n ≳ 10` | Use library eigensolvers |
| Standardization forgotten before PCA | Largest-scale feature dominates | Standardize or state why not |

### 2.6 ML link

- **PCA** (Stage 5B-05, 4C-01 derivation): eigenvectors of the covariance; eigenvalues = variance explained.
- **PageRank / spectral methods:** dominant eigenvector of a stochastic matrix; spectral clustering uses eigenvectors of a graph Laplacian (Stage 5B-12) `[VERIFY]`.
- **Hessian eigenvalues:** curvature directions; negative eigenvalues mean saddles (Module 08, 4C-03).
- **Recurrent dynamics:** the spectral radius of the recurrent matrix hints at exploding or vanishing signals (Lesson 2).

### 2.7 Lab (60 min)

1. Verify `Av = λv`, `trace`, and `det` identities on 5 random matrices (symmetric and not).
2. Make a table: matrix → eigenvalues → "real or complex" for scaling, shear, rotation, reflection, projection, and a random matrix.
3. Do PCA by hand on a 2-D cloud: covariance → `eigh` → project → confirm projected variances equal eigenvalues; plot the cloud with principal axes scaled by `√λ`.
4. Show that the second principal component is orthogonal to the first (`evecs[:, 0] @ evecs[:, 1] ≈ 0`).

### Check yourself (Unit 2)

1. If `A` has eigenvalue `0`, what do you know about `A`?
2. Why are covariance eigenvalues never negative (for exact arithmetic)?
3. What is the sum of the eigenvalues of `[[4, 1], [2, 3]]`?

**Reference answers:** (1) It is singular (`det = 0`, non-trivial null space). (2) `vᵀCv = ‖Xc v‖²/(n−1) ≥ 0`, so `C` is PSD. (3) The trace, `7` (eigenvalues are `5` and `2`).

---

## Unit 3 — Eigendecomposition and matrix powers (`02-…md`)

### 3.1 Why ML needs this

Repeated application of a matrix (`Aᵏx`) models recurrent networks, Markov chains, linear dynamical systems, and iterative solvers. The eigendecomposition turns a hard matrix power into a trivial scalar power and tells you what happens as `k → ∞`.

### 3.2 Intuition

In the basis of eigenvectors, a matrix is just independent scalings. Change coordinates into that basis, scale each axis by `λᵢ`, change back. Applying it `k` times scales each axis by `λᵢᵏ`. The biggest `|λ|` wins; if `|λ| < 1` the direction dies out, if `> 1` it explodes, if complex it oscillates.

### 3.3 Mechanics

- **Diagonalization:** if `A` has `n` independent eigenvectors, `A = VΛV⁻¹` with `V = [v₁ … v_n]`, `Λ = diag(λ)`.
- **Powers:** `Aᵏ = VΛᵏV⁻¹`, and `Λᵏ = diag(λᵢᵏ)`. Also `f(A) = Vf(Λ)V⁻¹` for functions (`exp`, `sqrt`, inverse).
- **Symmetric case:** `A = QΛQᵀ` with orthogonal `Q`, with no inverse needed and numerically well-behaved.
- **Spectral radius** `ρ(A) = maxᵢ|λᵢ|`. `Aᵏx → 0` for all `x` iff `ρ(A) < 1`; generic `x` blows up if `ρ(A) > 1`.
- **Dominant direction:** for large `k`, `Aᵏx ∝ v₁` (if `|λ₁|` is strictly largest and `x` has a component along `v₁`). This is the idea behind power iteration (Project 1).
- **Not every matrix is diagonalizable.** `[[1, 1], [0, 1]]` has one eigenvalue `1` with only one independent eigenvector (a **defective** matrix). Repeated eigenvalues are not the problem; missing eigenvectors are.
- **Nearly defective / non-normal matrices:** eigenvectors can be almost parallel, `V` is ill-conditioned, and the transient behaviour of `Aᵏ` can be far larger than `ρ(A)ᵏ` suggests, so check `cond(V)`.
- **Markov chain:** a column- or row-stochastic matrix has eigenvalue `1`; the stationary distribution is its eigenvector (details in 4C-04).

**Worked example:** `A = [[2,1],[1,2]]`, `A¹⁰ = Q diag(3¹⁰, 1¹⁰) Qᵀ`; `3¹⁰ = 59049`, so `A¹⁰ ≈ (59049/2)·[[1,1],[1,1]] + (1/2)·[[1,−1],[−1,1]]` (diagonal entries 29525, off-diagonals 29524).

### 3.4 Code

```python
import numpy as np

def matrix_power_eig(A, k):
    w, V = np.linalg.eig(A)
    out = V @ np.diag(w ** k) @ np.linalg.inv(V)
    return out.real if np.allclose(out.imag, 0) else out

def matrix_power_sym(A, k):                     # symmetric: no inverse needed
    w, Q = np.linalg.eigh(A)
    return (Q * w ** k) @ Q.T                   # (Q * w**k) scales columns, avoiding a dense diag

A = np.array([[2., 1.], [1., 2.]])
assert np.allclose(matrix_power_eig(A, 10), np.linalg.matrix_power(A, 10))
assert np.allclose(matrix_power_sym(A, 10), np.linalg.matrix_power(A, 10))
print(np.linalg.matrix_power(A, 10))             # [[29525 29524] [29524 29525]]

# functions of a matrix: inverse and square root of an SPD matrix
w, Q = np.linalg.eigh(A)
A_inv = (Q / w) @ Q.T;           assert np.allclose(A_inv, np.linalg.inv(A))
A_sqrt = (Q * np.sqrt(w)) @ Q.T; assert np.allclose(A_sqrt @ A_sqrt, A)

# stability: spectral radius controls repeated application
rng = np.random.default_rng(0)
def run(W, steps=50):
    x = rng.normal(size=W.shape[0])
    for _ in range(steps):
        x = W @ x
    return np.linalg.norm(x)

W = rng.normal(size=(30, 30)) / np.sqrt(30)             # entries scaled so rho is about 1
rho = np.max(np.abs(np.linalg.eigvals(W)))
for scale in (0.8, 1.0, 1.2):
    print(f"scale {scale}: rho={scale * rho:.2f}  |x_50|={run(scale * W):.3g}")   # report your own numbers

# defective matrix: eigenvectors are (numerically) parallel
J = np.array([[1., 1.], [0., 1.]])
w, V = np.linalg.eig(J)
print(w, np.linalg.cond(V))                              # eigenvalues 1, 1; cond(V) is enormous
```

Markov chain preview:

```python
P = np.array([[0.9, 0.5], [0.1, 0.5]])                   # column-stochastic: columns sum to 1
w, V = np.linalg.eig(P)
i = np.argmin(np.abs(w - 1)); pi = np.real(V[:, i]); pi /= pi.sum()
print(pi)                                                # stationary distribution, about [0.833, 0.167]
assert np.allclose(P @ pi, pi)
x = np.array([0.0, 1.0])
for _ in range(100): x = P @ x
assert np.allclose(x, pi, atol=1e-8)                     # powers converge to the dominant eigenvector
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Diagonalizing a defective or nearly defective matrix | `V` singular/ill-conditioned; garbage `Aᵏ` | Check `cond(V)`; use Schur / `scipy.linalg.expm` / `fractional_matrix_power` `[VERIFY: API]` |
| Using `inv(V)` when `A` is symmetric | Extra error | Use `Q` and `Qᵀ` |
| Ignoring complex output | `complex128` leaks into downstream code | Check `np.iscomplexobj`; take `.real` only after verifying the imaginary part vanishes |
| Taking `w ** k` for negative real `w` with fractional `k` | `nan` | Only integer `k`, or cast to complex |
| Judging stability by `‖A‖` alone | Wrong conclusion for non-normal `A` | Use `ρ(A)` and check transient growth |
| Expecting dominant-eigenvector convergence when `|λ₁| = |λ₂|` | No convergence | Inspect the spectrum; shift or deflate |
| Starting vector orthogonal to `v₁` | Never reaches the dominant direction (in exact arithmetic) | Random start |

### 3.6 ML link

- **RNN/state-space models:** `hₜ = Whₜ₋₁ + …`; `ρ(W)` relates to exploding/vanishing signals; orthogonal or spectrally-controlled initialisation (Stage 4C-08, 5C-05) `[VERIFY]`.
- **Markov chains / MCMC / PageRank:** stationary distribution = eigenvector of eigenvalue 1 (4C-04).
- **Gradient descent on quadratics:** the error contracts by `(1 − ηλᵢ)` per step along each eigen-direction, so convergence is limited by the **smallest** and divergence by the **largest** curvature (Module 08, 4C-03).
- **Graph methods:** powers of an adjacency matrix count walks; diffusion on graphs (Stage 5B-12).

### 3.7 Lab (75 min)

1. Implement `matrix_power_eig` and `matrix_power_sym`; test against `np.linalg.matrix_power` for `k ∈ {1, 5, 20}` on 20 random symmetric and non-symmetric diagonalizable matrices.
2. Stability experiment: build matrices with `ρ ∈ {0.8, 1.0, 1.2}`, iterate 100 steps, plot `‖xₖ‖` on a log scale.
3. **Gradient descent on a quadratic** `f(x) = ½xᵀHx`: choose `H` symmetric PD, run GD with step `η`, and verify that the error along eigenvector `i` shrinks by `(1 − ηλᵢ)` each step; show divergence when `η > 2/λ_max`.
4. Show a defective matrix failing in `matrix_power_eig` (compare with `matrix_power`), and explain what went wrong.

```python
H = np.diag([1.0, 10.0]); x = np.array([1.0, 1.0]); eta = 0.15       # 2/λmax = 0.2
for _ in range(50): x = x - eta * (H @ x)
print(x)                                                              # shrinks along both axes
eta = 0.25
x = np.array([1.0, 1.0])
for _ in range(50): x = x - eta * (H @ x)
print(x)                                                              # grows along the λ=10 axis
```

### Check yourself (Unit 3)

1. Write `Aᵏ` using the eigendecomposition.
2. What condition on eigenvalues guarantees `Aᵏx → 0` for every `x`?
3. Why can diagonalization fail even when the characteristic polynomial has real roots?

**Reference answers:** (1) `VΛᵏV⁻¹`. (2) `ρ(A) = maxᵢ|λᵢ| < 1`. (3) The matrix may lack `n` independent eigenvectors (defective), as with `[[1,1],[0,1]]`.

---

## Unit 4 — SVD: intuition and computation (`03-…md`)

### 4.1 Why ML needs this

The SVD works for **any** matrix, rectangular or singular, and it is the workhorse behind PCA, low-rank approximation, the pseudo-inverse, rank and conditioning diagnostics, and latent semantic analysis. If you learn one decomposition in this stage, it is this one.

### 4.2 Intuition

Every matrix does three things in sequence: **rotate/reflect** (`Vᵀ`), **stretch along the axes** by non-negative amounts `σᵢ` (`Σ`), then **rotate/reflect** again (`U`). The unit circle becomes an ellipse whose semi-axes have lengths `σ₁ ≥ σ₂ ≥ …` and point along the columns of `U`.

### 4.3 Mechanics

- **Full SVD:** `A = UΣVᵀ`, `A: (m, n)`, `U: (m, m)` orthogonal, `Σ: (m, n)` diagonal with `σ₁ ≥ σ₂ ≥ … ≥ 0`, `V: (n, n)` orthogonal.
- **Reduced ("economy") SVD:** with `r = min(m, n)`: `U: (m, r)`, `s: (r,)`, `Vᵀ: (r, n)`. This is what you almost always use (`full_matrices=False`).
- **Outer-product form:** `A = Σᵢ σᵢ uᵢ vᵢᵀ`, a sum of rank-1 pieces ordered by importance. This is the basis of low-rank approximation (Lesson 4).
- **Link to eigen-things:** `AᵀA = V Σᵀ Σ Vᵀ` and `AAᵀ = U ΣΣᵀ Uᵀ`. So **`σᵢ² = eigenvalues of AᵀA`**, `V` = its eigenvectors, `U` = eigenvectors of `AAᵀ`. For symmetric PSD `A`, the singular values equal the eigenvalues.
- **Rank:** `rank(A)` = number of non-zero singular values. Numerical rank = count above a tolerance.
- **Condition number:** `κ₂(A) = σ₁/σ_r` (Module 02, Lesson 8 link).
- **Pseudo-inverse:** `A⁺ = V Σ⁺ Uᵀ`, where `Σ⁺` inverts the non-zero `σ` (and leaves zeros). It gives the minimum-norm least-squares solution.
- **Sign ambiguity:** `(uᵢ, vᵢ)` and `(−uᵢ, −vᵢ)` are equally valid; compare reconstructions, not raw factors.
- **PCA via SVD:** for centered `Xc: (n, d)` with SVD `Xc = UΣVᵀ`, the principal directions are the rows of `Vᵀ`, variances are `σᵢ²/(n−1)`, and scores are `UΣ = XcV`. SVD is numerically preferable to forming `XcᵀXc`, since forming it squares the condition number (Module 02, Lesson 8).
- **Cost:** about `O(mn·min(m,n))` for the full dense routine. Truncated/randomized methods (`scipy.sparse.linalg.svds`, `sklearn.utils.extmath.randomized_svd`) compute only the top `k` `[VERIFY: availability]`.

**Worked example (2×2):** `A = [[3, 0], [0, 2]]` → `σ = (3, 2)`, `U = V = I`. For `A = [[1, 1], [0, 0]]` → `σ = (√2, 0)`: rank 1; `u₁ = (1, 0)`, `v₁ = (1, 1)/√2`.

### 4.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)
A = rng.normal(size=(6, 4))

U, s, Vt = np.linalg.svd(A, full_matrices=False)          # U (6,4), s (4,), Vt (4,4)
assert np.allclose(U * s @ Vt, A)                         # reconstruction (U*s scales columns of U)
assert np.allclose(U.T @ U, np.eye(4)) and np.allclose(Vt @ Vt.T, np.eye(4))
assert np.all(np.diff(s) <= 1e-12)                        # sorted descending

# from scratch via eigh(A^T A)
w, V = np.linalg.eigh(A.T @ A)
order = np.argsort(w)[::-1]; w, V = w[order], V[:, order]
s_scratch = np.sqrt(np.maximum(w, 0.0))
assert np.allclose(s_scratch, s)
U_scratch = A @ V / s_scratch                             # u_i = A v_i / σ_i  (only valid for σ_i > 0)
assert np.allclose(np.abs(np.sum(U_scratch * U, axis=0)), 1.0)    # same up to sign

# rank-1 outer-product expansion
A_rebuilt = sum(s[i] * np.outer(U[:, i], Vt[i]) for i in range(4))
assert np.allclose(A_rebuilt, A)

# condition number and pseudo-inverse
assert np.isclose(np.linalg.cond(A), s[0] / s[-1])
A_pinv = (Vt.T / s) @ U.T
assert np.allclose(A_pinv, np.linalg.pinv(A))

# PCA via SVD matches PCA via covariance eigendecomposition
X = rng.normal(size=(300, 3)) @ rng.normal(size=(3, 3)); Xc = X - X.mean(axis=0)
_, s2, Vt2 = np.linalg.svd(Xc, full_matrices=False)
var_svd = s2 ** 2 / (len(Xc) - 1)
var_eig = np.sort(np.linalg.eigvalsh(np.cov(X.T)))[::-1]
assert np.allclose(var_svd, var_eig)

# rank-deficient: exact zero singular values
B = np.outer(rng.normal(size=5), rng.normal(size=4)) + np.outer(rng.normal(size=5), rng.normal(size=4))
print(np.linalg.svd(B, compute_uv=False))                 # two real values, two near machine zero
```

Geometry check, a unit circle mapped to an ellipse with semi-axes `σ`:

```python
theta = np.linspace(0, 2 * np.pi, 2000)
circle = np.vstack([np.cos(theta), np.sin(theta)])
M = np.array([[1.5, 0.5], [0.0, 0.8]])
img = M @ circle
radii = np.linalg.norm(img, axis=0)
print(radii.max(), radii.min(), np.linalg.svd(M, compute_uv=False))   # max ≈ σ1, min ≈ σ2
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting `full_matrices=False` | Huge `U` (`m×m`) for tall matrices; memory blow-up | Always use the economy form unless the full basis is needed |
| `np.linalg.svd` returns `Vᵀ`, not `V` | Transposed bug | Name it `Vt` |
| Treating `s` as a matrix | Shape errors | Use `U * s @ Vt` or `np.diag(s)` for small cases |
| Building `U` as `A V / σ` with `σ ≈ 0` | Division blow-up | Only for `σ > tol`; use library `svd` otherwise |
| Forming `AᵀA` for ill-conditioned `A` | Squares the condition number; loses small singular values | Use `svd` directly |
| Comparing `U`/`V` columns across runs | Sign flips | Compare reconstructions or fix signs |
| Full SVD of a huge matrix | Time/memory | Truncated or randomized SVD |
| Not centering before SVD-as-PCA | First component captures the mean | Center first |
| Hard rank threshold on noisy data | Spurious rank | Inspect the spectrum; use an energy criterion |

### 4.6 ML link

- **PCA** (Stage 5B-05): SVD of the centered data matrix; derivation and Eckart–Young in 4C-01.
- **Latent semantic analysis, recommenders:** SVD of a term-document or user-item matrix; low-rank factors are "topics" or "tastes" `[JUDGEMENT]` (real recommenders use regularized or implicit-feedback variants, Stage 5B-09).
- **Pseudo-inverse / least squares:** `lstsq` is SVD-based (Module 02, 14).
- **Diagnostics:** the singular-value spectrum of embeddings, activations, or weights shows effective dimensionality (Lesson 4 and Module 02, Lesson 9).
- **Whitening:** `Xc V Σ⁻¹ √(n−1)` decorrelates features (4C-01).

### 4.7 Lab (75 min)

1. Verify reconstruction, orthogonality, ordering, and `σ² = eig(AᵀA)` on 10 random shapes (tall, wide, square).
2. Implement SVD "from scratch" via `eigh(AᵀA)`, then show the accuracy loss on a Hilbert-like ill-conditioned matrix versus `np.linalg.svd` (report your numbers).
3. PCA two ways (covariance `eigh` and SVD) on a 5-feature synthetic dataset; confirm identical variances and equal projections up to sign.
4. Plot the circle-to-ellipse picture with `u₁σ₁` and `u₂σ₂` drawn as the ellipse axes.

### Check yourself (Unit 4)

1. How are singular values related to the eigenvalues of `AᵀA`?
2. What shapes do `U`, `s`, `Vt` have for a `100×20` matrix with `full_matrices=False`?
3. Why is computing the SVD preferable to eigendecomposing `XᵀX` for PCA?

**Reference answers:** (1) `σᵢ = √λᵢ(AᵀA)`. (2) `(100, 20)`, `(20,)`, `(20, 20)`. (3) Forming `XᵀX` squares the condition number and loses accuracy for small singular values.

---

## Unit 5 — Low-rank approximation (`04-…md`)

### 5.1 Why ML needs this

Real data is usually far less complex than its raw dimension: images are smooth, embedding spaces are redundant, user-item tables are driven by a few tastes. Keeping the top `k` singular directions gives the **best possible** rank-`k` summary, with an exact error formula. The same idea underlies PCA, compression, denoising, and low-rank adapters (LoRA).

### 5.2 Intuition

`A = Σ σᵢuᵢvᵢᵀ` is a sum of rank-1 layers ordered by importance. Keep the first `k` and you keep most of the signal if the singular values fall off quickly. If they decay slowly, the matrix is "genuinely high-rank" and truncation loses a lot.

### 5.3 Mechanics

- **Truncated SVD:** `A_k = U_k Σ_k V_kᵀ = Σ_{i≤k} σᵢuᵢvᵢᵀ`; `rank(A_k) = k`.
- **Eckart–Young–Mirsky theorem:** `A_k` is the **closest** rank-`k` matrix to `A` in both the Frobenius and the spectral norm:
  - `‖A − A_k‖_F = √(σ_{k+1}² + … + σ_r²)`
  - `‖A − A_k‖₂ = σ_{k+1}`
  (proof in 4C-01; here you **verify numerically**).
- **Energy / explained variance:** `E(k) = Σ_{i≤k}σᵢ² / Σ_iσᵢ²`. Choose the smallest `k` with `E(k) ≥ target` (e.g., 0.90, 0.95: choose by task, not tradition `[JUDGEMENT]`).
- **Storage:** a dense `m×n` matrix uses `mn` numbers; the factored rank-`k` form uses `k(m + n + 1)` (or `k(m + n)` if `σ` is absorbed). It saves memory only if `k < mn/(m+n+1)`.
- **Compute:** `A_k x = U_k(Σ_k(V_kᵀx))` costs `O(k(m+n))` instead of `O(mn)`.
- **Denoising:** if signal is low-rank and noise is spread across all directions, truncation removes noise (the optimal `k` is unknown in practice; use held-out validation or spectrum gaps `[JUDGEMENT]`).
- **Scree/elbow plots** of `σᵢ` and cumulative energy guide `k`. Elbows are heuristics, not guarantees.
- **Adapters (LoRA idea):** instead of learning a full update `ΔW ∈ ℝ^{d×d}`, learn `ΔW = BA` with `B: (d, r)`, `A: (r, d)`, so `rank(ΔW) ≤ r` and parameters drop from `d²` to `2dr` `[VERIFY: details in the Stage 5C/5D lessons]`.

### 5.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def truncated(A, k):
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    return (U[:, :k] * s[:k]) @ Vt[:k], s

# a matrix with decaying spectrum + noise
m, n, true_rank = 80, 60, 5
L = rng.normal(size=(m, true_rank)) @ rng.normal(size=(true_rank, n))
A = L + 0.1 * rng.normal(size=(m, n))

for k in (1, 3, 5, 10, 30):
    Ak, s = truncated(A, k)
    fro = np.linalg.norm(A - Ak, "fro")
    spec = np.linalg.norm(A - Ak, 2)
    assert np.isclose(fro, np.sqrt(np.sum(s[k:] ** 2)))        # Eckart–Young, Frobenius
    assert np.isclose(spec, s[k] if k < len(s) else 0.0)        # Eckart–Young, spectral
    print(k, round(fro, 3), round(spec, 3), "storage", k * (m + n + 1), "vs", m * n)

# energy curve and choosing k
s = np.linalg.svd(A, compute_uv=False)
energy = np.cumsum(s ** 2) / np.sum(s ** 2)
k95 = int(np.searchsorted(energy, 0.95) + 1)
print("k for 95% energy:", k95)

# no other rank-k matrix does better (random competitors)
k = 5
Ak, _ = truncated(A, k)
best = np.linalg.norm(A - Ak, "fro")
for _ in range(200):
    B = rng.normal(size=(m, k)) @ rng.normal(size=(k, n))          # random rank-k
    coef = np.sum(A * B) / np.sum(B * B)                            # best scaling of that B
    assert np.linalg.norm(A - coef * B, "fro") >= best - 1e-9

# low-rank matrix-vector product
x = rng.normal(size=n)
U, s_, Vt = np.linalg.svd(A, full_matrices=False)
y_fast = U[:, :k] @ (s_[:k] * (Vt[:k] @ x))                         # O(k(m+n))
assert np.allclose(y_fast, Ak @ x)

# LoRA-style parameter count
d, r = 4096, 8
print("full:", d * d, "low-rank:", 2 * d * r, "ratio:", d * d / (2 * d * r))
```

Denoising demonstration:

```python
clean = L / np.linalg.norm(L)
noisy = (L + 0.5 * rng.normal(size=L.shape)) / np.linalg.norm(L)
for k in (1, 3, 5, 8, 15, 40):
    Ak, _ = truncated(noisy, k)
    print(k, np.linalg.norm(Ak - clean))           # error typically bottoms out near the true rank
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Choosing `k` without looking at the spectrum | Under- or over-compression | Plot `σ` and cumulative energy |
| Assuming a "95% energy" threshold is right for every task | Poor downstream accuracy | Validate on the actual task metric |
| Forgetting to center before PCA-style truncation | Mean dominates the first component | Center, and add the mean back if reconstructing |
| Storing `U_k, Σ_k, V_k` for a nearly full-rank target | No savings, or larger storage than the original | Compute `k(m+n+1)` against `mn` |
| Treating Eckart–Young as covering *any* constraint | It holds for unconstrained rank-`k` only | Non-negativity, sparsity, missing entries need other methods (NMF, ALS) |
| Rank-`k` approximation of a matrix with missing entries by filling zeros | Biased factors | Use methods designed for missing data (Stage 5B-09) |
| Float `k` or `k > rank` | Index errors or no-ops | Clamp `k` to `min(m, n)` |
| Decaying spectrum assumed without checking | Poor approximation | Inspect |

### 5.6 ML link

- **PCA** = truncated SVD of centered data (Module 03 Lesson 3; Stage 5B-05).
- **Embedding compression and retrieval speed:** project embeddings onto top-`k` directions; verify recall on held-out queries `[JUDGEMENT]`.
- **LSA / topic structure:** truncated SVD on TF-IDF (Stage 5A-10).
- **Parameter-efficient fine-tuning:** low-rank updates (above).
- **Model compression:** factorize large weight matrices; accuracy impact must be measured (Stage 5D-10).
- **Recommenders:** low-rank factorization of the interaction matrix (Stage 5B-09).
- **Denoising and anomaly detection:** reconstruction error from a low-rank model as an anomaly score (Stage 5B-06) `[JUDGEMENT]`.

### 5.7 Lab (75 min)

1. Verify both Eckart–Young formulas for `k ∈ {1, …, r}` on 5 random matrices (random full-rank, decaying spectrum, exactly low-rank).
2. Plot spectrum, cumulative energy, and approximation error vs `k`; mark `k95`.
3. Run the random-competitor test and explain why none of them can win.
4. Denoising experiment: report where the error bottoms out and how that relates to the known generating rank.
5. Compare storage ratios `k(m+n+1)/(mn)` for square and for tall/wide matrices; find the break-even `k`.

### Check yourself (Unit 5)

1. What is `‖A − A_k‖₂` in terms of singular values?
2. For a `1000×1000` matrix, at what `k` does the factored form stop saving storage?
3. Does a 95% energy threshold guarantee good downstream accuracy?

**Reference answers:** (1) `σ_{k+1}`. (2) When `k(2000 + 1) ≥ 10⁶`, i.e. `k ≥ 499.75`, so savings stop at `k ≈ 500`. (3) No, validate on the real task metric.

---

## Unit 6 — Matrix norms: Frobenius and spectral (`05-…md`)

### 6.1 Why ML needs this

Matrix norms measure the "size" of weights, updates, and errors. The Frobenius norm is the matrix version of L2 and drives weight decay. The **spectral norm** is the **largest stretch** a matrix applies to any vector, so it bounds how much a layer can amplify inputs. That is why it appears in stability analysis, Lipschitz constraints, spectral normalization, and gradient diagnostics.

### 6.2 Intuition

- **Frobenius:** flatten the matrix into one long vector and take its L2 norm: total "energy".
- **Spectral (operator 2-norm):** the biggest factor by which `A` can stretch a unit vector: `max_{‖x‖=1}‖Ax‖`. Geometrically, the longest semi-axis of the image ellipse.
- **Nuclear:** the sum of singular values; the convex surrogate for rank.

### 6.3 Mechanics

| Norm | Definition | In singular values | NumPy |
|---|---|---|---|
| Frobenius | `√Σᵢⱼ Aᵢⱼ² = √trace(AᵀA)` | `√Σσᵢ²` | `np.linalg.norm(A, "fro")` |
| Spectral (2-norm) | `max_{‖x‖₂=1} ‖Ax‖₂` | `σ₁` | `np.linalg.norm(A, 2)` |
| Nuclear (trace) | `Σσᵢ` | `Σσᵢ` | `np.linalg.norm(A, "nuc")` |
| Induced 1-norm | max column absolute sum | n/a | `np.linalg.norm(A, 1)` |
| Induced ∞-norm | max row absolute sum | n/a | `np.linalg.norm(A, np.inf)` |
| Max-abs entry | `maxᵢⱼ|Aᵢⱼ|` | n/a | `np.abs(A).max()` (**not** `ord=np.inf` for matrices) |

- **Key inequalities:** `‖A‖₂ ≤ ‖A‖_F ≤ √r · ‖A‖₂` (`r = rank`); `‖A‖₂ ≤ ‖A‖_*`.
- **Sub-multiplicativity:** `‖AB‖ ≤ ‖A‖‖B‖` for the spectral and Frobenius norms; so a deep linear network's gain is at most the product of layer spectral norms.
- **Unitary invariance:** multiplying by an orthogonal matrix does not change `‖·‖_F` or `‖·‖₂`.
- **`‖Ax‖ ≤ ‖A‖₂‖x‖`** (the defining use). Lipschitz constant of `x ↦ Ax` in L2 is `‖A‖₂`.
- **Condition number via norms:** `κ₂(A) = ‖A‖₂‖A⁻¹‖₂`.
- **Cheap spectral-norm estimate:** a few steps of power iteration on `AᵀA` (Project 1; used in spectral normalization) `[VERIFY: details in Stage 5C lessons]`.
- **Gradient/weight clipping by global norm** uses the Frobenius (flattened L2) norm, a **different** quantity from the spectral norm of a weight matrix.

### 6.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)
A = rng.normal(size=(7, 5))
s = np.linalg.svd(A, compute_uv=False)

assert np.isclose(np.linalg.norm(A, "fro"), np.sqrt(np.sum(A ** 2)))
assert np.isclose(np.linalg.norm(A, "fro"), np.sqrt(np.trace(A.T @ A)))
assert np.isclose(np.linalg.norm(A, "fro"), np.sqrt(np.sum(s ** 2)))
assert np.isclose(np.linalg.norm(A, 2), s[0])
assert np.isclose(np.linalg.norm(A, "nuc"), s.sum())
assert np.isclose(np.linalg.norm(A, 1), np.abs(A).sum(axis=0).max())
assert np.isclose(np.linalg.norm(A, np.inf), np.abs(A).sum(axis=1).max())
assert np.linalg.norm(A, 2) <= np.linalg.norm(A, "fro") <= np.sqrt(len(s)) * np.linalg.norm(A, 2) + 1e-12

# spectral norm = max stretch: brute-force check by sampling unit vectors
X = rng.normal(size=(5, 200_000)); X /= np.linalg.norm(X, axis=0)
stretch = np.linalg.norm(A @ X, axis=0)
print(stretch.max(), "<=", s[0])                          # sampling approaches σ1 from below

# sub-multiplicativity and orthogonal invariance
B = rng.normal(size=(5, 4))
assert np.linalg.norm(A @ B, 2) <= np.linalg.norm(A, 2) * np.linalg.norm(B, 2) + 1e-12
Q, _ = np.linalg.qr(rng.normal(size=(7, 7)))
assert np.isclose(np.linalg.norm(Q @ A, "fro"), np.linalg.norm(A, "fro"))
assert np.isclose(np.linalg.norm(Q @ A, 2), np.linalg.norm(A, 2))

# the gotcha: ord=inf on a matrix is the max ROW SUM, not the max entry
print(np.linalg.norm(A, np.inf), np.abs(A).max())

# depth amplification: product of spectral norms bounds the gain
Ws = [rng.normal(size=(30, 30)) / np.sqrt(30) for _ in range(10)]
bound = np.prod([np.linalg.norm(W, 2) for W in Ws])
prod = np.linalg.multi_dot(Ws)
print(np.linalg.norm(prod, 2), "<=", bound)

# spectral normalization sketch: rescale W so that ||W||_2 = 1
W = Ws[0]; W_sn = W / np.linalg.norm(W, 2)
assert np.isclose(np.linalg.norm(W_sn, 2), 1.0)
```

Power-iteration estimate of `σ₁` (preview of Project 1):

```python
def spectral_norm_estimate(A, iters=50, seed=0):
    v = np.random.default_rng(seed).normal(size=A.shape[1])
    v /= np.linalg.norm(v)
    for _ in range(iters):
        u = A @ v;  u /= np.linalg.norm(u)
        v = A.T @ u; v /= np.linalg.norm(v)
    return float(np.linalg.norm(A @ v))
assert np.isclose(spectral_norm_estimate(A, 200), np.linalg.norm(A, 2), rtol=1e-6)
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.linalg.norm(A)` with no `ord` on a matrix | Frobenius, which may not be what you meant | Always pass `ord` explicitly |
| `ord=np.inf` thought to be the max entry | Max row sum instead | Use `np.abs(A).max()` |
| Using Frobenius to bound amplification | Overly loose bound | Use the spectral norm |
| Using the spectral norm of each layer to estimate total gain through nonlinearities | Only a bound | Remember it ignores activation structure |
| Computing the exact spectral norm of a huge matrix by full SVD | Cost | Power iteration / `svds` |
| Clipping gradients by per-matrix spectral norm while the code uses global Frobenius | Misunderstood behaviour | State which norm the framework uses `[VERIFY]` |
| Comparing norms of matrices with different sizes | Frobenius grows with size | Normalize by `√(mn)` or report the relative error `‖A−B‖/‖A‖` |

### 6.6 ML link

- **Weight decay / L2 regularization:** `λ‖W‖_F²` (Module 14).
- **Stability and Lipschitz control:** spectral norm of each layer bounds the amplification; spectral normalization in GAN discriminators `[VERIFY]`.
- **Nuclear norm:** convex relaxation for low-rank matrix completion (Stage 5B-09).
- **Gradient diagnostics:** global gradient norm tracked in training; spikes signal instability (Stage 5C-03).
- **Error reporting:** relative Frobenius error for approximations (Lesson 4 and Project 2).

### 6.7 Lab (60 min)

1. Verify every identity in the table on 10 random matrices (tall, wide, square, low-rank).
2. Sampling experiment showing `max‖Ax‖/‖x‖` approaches `σ₁` from below; plot the convergence versus the number of samples.
3. Implement `spectral_norm_estimate`; compare with `np.linalg.norm(A, 2)` for matrices with a large and a small gap between `σ₁` and `σ₂`, and explain the speed difference.
4. Depth experiment: stack 20 random layers (with and without spectral normalization) and plot `‖x_L‖/‖x₀‖`.

### Check yourself (Unit 6)

1. What is the spectral norm in terms of singular values? The Frobenius norm?
2. Which norm bounds `‖Ax‖/‖x‖` for all `x`?
3. What does `np.linalg.norm(A, np.inf)` return for a matrix?

**Reference answers:** (1) `σ₁`; `√Σσᵢ²`. (2) The spectral norm. (3) The maximum absolute row sum.

---

## Unit 7 — Practice question bank (`practice-questions.md`)

### 7.1 Structure

About 45 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 11 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation (kept to 2×2), "predict the output", runnable code, and ML judgement.

### 7.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 7.3 Seed items

**Q1 [L1] Definition.** State what it means for `v` to be an eigenvector of `A`. → `Av = λv`, `v ≠ 0`.
**Q2 [L2] Hand calc.** Eigenvalues of `[[4, 0], [1, 3]]`? → Triangular: `4` and `3`.
**Q3 [L2] Trace/det.** `A` is 2×2 with `trace = 5`, `det = 6`. Eigenvalues? → `λ² − 5λ + 6 = 0` → `2, 3`.
**Q4 [L2] Powers.** `A = diag(2, 0.5)`; what is `A¹⁰ x` doing to a generic `x`? → The first component grows by `2¹⁰ = 1024`, the second shrinks by `0.5¹⁰ ≈ 0.001`; the direction aligns with `e₁`.
**Q5 [L2] SVD shapes.** `A: 50×8`, economy SVD; shapes? → `U (50,8)`, `s (8,)`, `Vt (8,8)`.
**Q6 [L2] Eckart–Young.** `σ = (10, 4, 2, 1)`. Spectral and Frobenius errors for `k=2`? → `σ₃ = 2`; `√(4 + 1) = √5 ≈ 2.236`.
**Q7 [L3] Debug.** `np.linalg.eig` on a covariance matrix returns slightly complex values. → Matrix not exactly symmetric from rounding or from an inexact construction; symmetrize and use `eigh`.
**Q8 [L3] Debug.** Reconstruction `U @ np.diag(s) @ Vt` fails with a shape error for a `100×20` matrix with `full_matrices=True`. → `U` is `100×100`; use the economy form or slice `U[:, :20]`.
**Q9 [L3] Debug.** Two runs give PCA components with flipped signs. Bug? → No, sign is arbitrary; compare reconstructions or fix a sign convention.
**Q10 [L3] Analysis.** `np.linalg.norm(A, np.inf)` is far larger than `np.abs(A).max()`. Why? → For matrices `ord=inf` is the max row sum.
**Q11 [L3] Analysis.** A matrix has `ρ(A) = 0.9`, yet `‖Aᵏx‖` first grows large before decaying. Why? → Non-normal matrix; transient growth; `cond(V)` is large.
**Q12 [L4] Design.** Choose `k` for compressing 768-d embeddings for faster retrieval. → Plot the spectrum, then pick `k` by **recall on held-out queries**, not by a fixed energy threshold; re-measure latency.
**Q13 [L4] Design.** You must monitor "embedding collapse" in training. → Track the singular-value spectrum / effective rank of a batch of embeddings (centered), alert on a sharp drop in effective rank.
**Q14 [L4] Design.** A recurrent model's loss explodes. Which matrix quantity do you check first, and what are three remedies? → `ρ` (and spectral norm) of the recurrent weights; remedies: gradient clipping, orthogonal/spectrally-scaled initialization, gated architectures `[JUDGEMENT]`.

### 7.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Eigenvalues/eigenvectors | 2 | 3 | 2 | 1 |
| Eigendecomposition, powers | 1 | 3 | 2 | 1 |
| SVD | 2 | 3 | 3 | 1 |
| Low-rank approximation | 1 | 3 | 2 | 2 |
| Matrix norms | 2 | 3 | 2 | 1 |

### Check yourself (Unit 7)

1. Which items need runnable code?
2. Why include a "flipped sign" item?

**Reference answers:** (1) All L3 debug items and anything depending on floating-point behaviour. (2) Sign ambiguity is the most common false "bug report" in PCA/SVD code.

---

## Unit 8 — Project index (`Projects/README.md`)

### 8.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Eigenvalue power iteration | Iterative eigen-computation, convergence analysis, PageRank-style use | 1, 2, 5 | 4–5 h |
| 2 | Image compression with SVD | Low-rank approximation with honest quality/size trade-offs | 3, 4, 5 | 4–5 h |

Order: 1 → 2 (Project 2 reuses the norm and spectrum helpers). Outputs feed `mlmath/decomp.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D4) and notebook `03_eigen_svd.ipynb`.

### 8.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs NumPy/SciPy reference | 30 |
| Failure-mode handling (non-convergence, zero start vector, tied eigenvalues, `k > rank`) | 15 |
| Reproducibility (seeded, pinned, clean venv; no downloads required) | 15 |
| Explanation quality (what each plot shows and why it matters for ML) | 15 |
| Code quality (types, shape docstrings) | 15 |
| ML connection paragraph | 10 |

### 8.3 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 8)

1. What does Project 2 reuse from Project 1?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) Norm/spectrum helpers and the verification pattern. (2) D4 (`mlmath/decomp.py`).

---

## Unit 9 — Project: Eigenvalue power iteration (`Projects/01-…md`)

### 9.1 Brief

Build `eigpower`: power iteration, inverse iteration, shifted iteration, and deflation, with convergence diagnostics, plus a PageRank application, all from scratch and verified against `np.linalg.eigh`/`eig`.

**Industry framing:** large-scale systems never run a full dense eigensolver on web-scale matrices; they use iterative methods. Understanding why they converge and when they stall is the practical skill.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | `power_iteration(A, tol, max_iter, seed)` | Returns `(λ, v, history)`; normalizes each step; stops on residual `‖Av − λv‖ < tol`; reports non-convergence honestly |
| R2 | Rayleigh quotient | `λ = vᵀAv / vᵀv`; used for the eigenvalue estimate |
| R3 | `inverse_iteration(A, shift)` | Solves `(A − σI)y = v` each step with `solve` (factor once with LU if you implement it, linking to Module 02 Project 2) → eigenvalue **closest to the shift** |
| R4 | `deflate(A, λ, v)` | Hotelling deflation for symmetric `A`: `A − λvvᵀ`; use to find the top-`k` eigenpairs |
| R5 | `top_k_eigs(A, k)` | Combines R1 and R4; compares with `eigh`; documents error growth with successive deflations |
| R6 | Convergence-rate study | Empirically fit `error ~ (|λ₂|/|λ₁|)^t`, plot on log scale, compare with theory |
| R7 | `spectral_norm(A)` and `top_singular_triplet(A)` | Power iteration on `AᵀA` implicitly (never form `AᵀA`) |
| R8 | `pagerank(P, d, tol)` | Damped power iteration on a column-stochastic matrix; handles dangling nodes; validates on a tiny graph by hand |
| R9 | Failure handling | Zero start vector, tied dominant eigenvalues (`|λ₁| = |λ₂|`), start vector orthogonal to `v₁`, non-convergence |

### 9.3 Layout and starter

```
eigpower/
├── pyproject.toml  requirements.txt  README.md
├── src/eigpower/{__init__,power,inverse,deflate,svdlite,pagerank}.py
├── tests/{test_power,test_inverse,test_deflate,test_svdlite,test_pagerank,test_failures}.py
├── notebooks/03_power_iteration.ipynb
└── bench/convergence_study.py
```

```python
# src/eigpower/power.py
from __future__ import annotations
import numpy as np

def power_iteration(A, tol=1e-10, max_iter=10_000, seed=0):
    """Dominant eigenpair of A (n×n). Returns (lam, v, history); raises RuntimeError if not converged."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if A.shape != (n, n):
        raise ValueError(f"square matrix required, got {A.shape}")
    v = np.random.default_rng(seed).normal(size=n)
    v /= np.linalg.norm(v)
    lam, hist = 0.0, []
    for it in range(max_iter):
        w = A @ v
        nrm = np.linalg.norm(w)
        if nrm == 0.0:
            raise RuntimeError("A @ v = 0: start vector in the null space (or A = 0)")
        v_new = w / nrm
        lam = float(v_new @ (A @ v_new))                      # Rayleigh quotient (unit v)
        resid = float(np.linalg.norm(A @ v_new - lam * v_new))
        hist.append((it, lam, resid))
        v = v_new
        if resid < tol:
            return lam, v, hist
    raise RuntimeError(f"no convergence after {max_iter} iterations (last residual {resid:.2e})")
```

```python
# src/eigpower/deflate.py
import numpy as np
from .power import power_iteration

def top_k_eigs(A, k, **kw):
    A = np.array(A, dtype=float)                               # copy: do not mutate the caller's matrix
    if not np.allclose(A, A.T):
        raise ValueError("Hotelling deflation as implemented requires a symmetric matrix")
    vals, vecs = [], []
    for _ in range(k):
        lam, v, _ = power_iteration(A, **kw)
        vals.append(lam); vecs.append(v)
        A = A - lam * np.outer(v, v)
    return np.array(vals), np.column_stack(vecs)
```

```python
# src/eigpower/pagerank.py
import numpy as np

def pagerank(P, d=0.85, tol=1e-12, max_iter=1000):
    """P: column-stochastic (columns sum to 1; dangling columns allowed as all zeros)."""
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    dangling = P.sum(axis=0) == 0
    r = np.full(n, 1.0 / n)
    for _ in range(max_iter):
        r_new = d * (P @ r + r[dangling].sum() / n) + (1 - d) / n
        if np.abs(r_new - r).sum() < tol:
            return r_new
        r = r_new
    raise RuntimeError("PageRank did not converge")
```

```python
# tests/test_power.py
import numpy as np, pytest
from eigpower.power import power_iteration
from eigpower.deflate import top_k_eigs

rng = np.random.default_rng(0)

def sym(n):
    M = rng.normal(size=(n, n)); return (M + M.T) / 2

@pytest.mark.parametrize("n", [3, 10, 30])
def test_dominant_matches_eigh(n):
    A = sym(n); A = A + n * np.eye(n)                          # shift: make dominant eigenvalue positive and well separated
    lam, v, _ = power_iteration(A, tol=1e-10)
    w, _ = np.linalg.eigh(A)
    assert np.isclose(lam, w[np.argmax(np.abs(w))], atol=1e-8)
    assert np.allclose(A @ v, lam * v, atol=1e-7)

def test_zero_start_in_nullspace_raises():
    with pytest.raises(RuntimeError):
        power_iteration(np.zeros((3, 3)))

def test_tied_eigenvalues_do_not_silently_pass():
    A = np.diag([1.0, -1.0, 0.1])                              # |λ1| = |λ2|: power iteration oscillates
    with pytest.raises(RuntimeError):
        power_iteration(A, max_iter=500)

def test_top_k_matches_eigh():
    A = sym(8); A = A @ A.T + np.eye(8)                        # SPD, positive spectrum
    vals, _ = top_k_eigs(A, 3, tol=1e-12)
    ref = np.sort(np.linalg.eigvalsh(A))[::-1][:3]
    assert np.allclose(vals, ref, atol=1e-6)
```

`[VERIFY]` The tie test depends on the start vector (a start exactly inside one eigenspace could converge). In a seeded run of this starter code all 6 tests passed; re-run after any change.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2, R9 | Matches `eigh` on 100 random symmetric matrices with a separated dominant eigenvalue (`atol=1e-8`); every failure case in R9 raises a clear error instead of returning a wrong value |
| M2 | R3 | Inverse iteration with shift `σ` finds the eigenvalue nearest `σ` (compare with `eigh`) for 20 random shifts |
| M3 | R4–R5 | Top-`k` matches `eigh` for `k = 3` on SPD matrices; a table shows error growth across successive deflations |
| M4 | R6 | Fit of log-error slope vs `log|λ₂/λ₁|` within 10% for 5 matrices with controlled eigenvalue ratios (build `A = QΛQᵀ` yourself) |
| M5 | R7–R8 | `spectral_norm` matches `np.linalg.norm(A, 2)` (`rtol=1e-6`); PageRank on a 4-node hand-worked graph matches your hand computation and the eigenvector of the Google matrix |
| M6 | Notebook and write-up | Runs top-to-bottom seeded; every claim has a plot or a number from your run |

### 9.5 Convergence-study requirement

Construct `A = Q diag(λ) Qᵀ` with `λ₁ = 1`, `λ₂ ∈ {0.5, 0.9, 0.99}`, others small. Record iterations to reach `1e-8` residual. State the relationship you observe versus the theory (error shrinks roughly like `|λ₂/λ₁|ᵗ`), and report your numbers rather than quoting a formula's prediction as a measurement.

### 9.6 Failure-mode table (README, ≥ 8 rows)

Seed with: start vector with zero component along `v₁`; `|λ₁| = |λ₂|` (sign-alternating or complex pair); `λ₂` very close to `λ₁` (slow); dominant eigenvalue negative (Rayleigh quotient handles the sign, the vector flips each step); non-symmetric matrix with complex dominant pair; zero matrix; deflation error accumulation; dangling nodes in PageRank.

### 9.7 Stretch goals

1. Lanczos or Arnoldi sketch for the top eigenpairs; compare with `scipy.sparse.linalg.eigsh` `[VERIFY: API]`.
2. Block power iteration (subspace iteration) for the top-`k` at once; show it beats sequential deflation in stability.
3. Randomized SVD (random projection + power iterations) vs exact SVD on a decaying-spectrum matrix; report accuracy vs speed from your own runs.
4. Sparse PageRank with `scipy.sparse` on a few-thousand-node synthetic graph; report time per iteration.
5. `hypothesis` property tests: Rayleigh quotient lies within `[λ_min, λ_max]` for symmetric `A`.

### 9.8 ML connection (README prompt)

Explain how (a) PCA's top components can be found without a full decomposition, (b) spectral normalization estimates `σ₁` cheaply, and (c) PageRank is an eigenvector problem, with a pointer to the code in this project for each.

### Check yourself (Unit 9)

1. Why does power iteration converge to the dominant eigenvector, and what controls the speed?
2. What goes wrong if `|λ₁| = |λ₂|`?
3. Why is `A − λvvᵀ` valid only for symmetric `A`?

**Reference answers:** (1) Components along each eigenvector scale by `λᵢᵗ`, so the largest `|λ|` dominates; speed is set by `|λ₂/λ₁|`. (2) No unique dominant direction; the iterate may oscillate or converge to a mix depending on the start. (3) For symmetric `A` the eigenvectors are orthogonal, so subtracting `λ₁v₁v₁ᵀ` zeroes that eigenvalue and leaves the others unchanged; for non-symmetric `A` this fails (left and right eigenvectors differ).

---

## Unit 10 — Project: Image compression with SVD (`Projects/02-…md`)

### 10.1 Brief

Build `svdimg`: compress grayscale and color images with truncated SVD, then quantify the trade-off between **rank, storage, and quality** with honest metrics, and test where low-rank compression works well (smooth images) and where it does not (texture, noise, text).

**Industry framing:** compression and quality trade-offs are always reported as a table with a measured quality metric and a measured size, never as a bare "we kept 95%". The same reporting habit applies to embedding compression and model factorization.

### 10.2 Data policy

No downloads are required. The project must run on **synthetic images generated in code** (gradients, shapes, texture, noise, a rendered text image) so tests are deterministic. You may additionally use any image you have locally via Pillow; keep such images out of the repository and out of the tests `[VERIFY: licence of any image you add]`.

### 10.3 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | `load_gray(path)` / `synthetic(kind, size, seed)` | Float arrays in `[0, 1]`, shape `(H, W)`; kinds in the starter: `gradient`, `shapes`, `checker`, `texture`, `noise`; add a `text` kind yourself (render with Pillow `ImageDraw`, optional) |
| R2 | `compress(img, k)` | Returns `(U_k, s_k, Vt_k)` from the economy SVD; clamps `k` to `min(H, W)` |
| R3 | `reconstruct(factors)` | Clip to `[0, 1]` after reconstruction |
| R4 | Metrics | `rel_fro_error`, `mse`, `psnr` (with `max=1.0`), optional `ssim` via scikit-image `[VERIFY: optional dependency]`; guard `psnr` against zero MSE |
| R5 | Storage accounting | `stored_numbers(H, W, k) = k(H + W + 1)`; `ratio = H·W / stored`; flag `k` values where `ratio < 1` (compression is a loss) |
| R6 | Spectrum tools | Singular values, cumulative energy, `k_for_energy(img, target)` |
| R7 | Rank sweep | For `k` in a grid, a table with `k, ratio, rel_error, PSNR, energy`; results saved as CSV |
| R8 | Color handling | Per-channel SVD, plus an alternative that works on the YCbCr-like decomposition with different `k` for luma and chroma `[JUDGEMENT]`; compare |
| R9 | Eckart–Young test | Verify `‖A − A_k‖_F² = Σ_{i>k}σᵢ²` on every synthetic image |
| R10 | Comparison baseline | Compare against a simple alternative at the same stored-number budget (e.g., downsample + upsample); report measured results honestly |
| R11 | Blockwise variant (stretch in R-level) | SVD per 8×8/16×16 block; compare with global SVD |

### 10.4 Layout and starter

```
svdimg/
├── pyproject.toml  requirements.txt  README.md
├── src/svdimg/{__init__,images,core,metrics,sweep,color}.py
├── tests/{test_images,test_core,test_metrics,test_sweep}.py
├── notebooks/03_svd_compression.ipynb
└── results/   # CSV tables and figures (generated)
```

```python
# src/svdimg/images.py
import numpy as np

def synthetic(kind: str, size: int = 128, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size] / (size - 1)
    if kind == "gradient":
        img = 0.5 * x + 0.5 * y
    elif kind == "shapes":
        img = ((x - 0.3) ** 2 + (y - 0.4) ** 2 < 0.04).astype(float) * 0.8
        img += ((np.abs(x - 0.7) < 0.15) & (np.abs(y - 0.7) < 0.15)) * 0.5
    elif kind == "checker":
        img = ((np.floor(x * 8) + np.floor(y * 8)) % 2).astype(float)
    elif kind == "texture":
        img = 0.5 + 0.25 * np.sin(40 * x + 7 * np.sin(23 * y)) + 0.1 * rng.normal(size=(size, size))
    elif kind == "noise":
        img = rng.random((size, size))
    else:
        raise ValueError(f"unknown kind {kind!r}")
    return np.clip(img, 0.0, 1.0)
```

```python
# src/svdimg/core.py
import numpy as np

def compress(img, k):
    U, s, Vt = np.linalg.svd(img, full_matrices=False)
    k = int(max(1, min(k, len(s))))
    return U[:, :k], s[:k], Vt[:k]

def reconstruct(factors):
    U, s, Vt = factors
    return np.clip((U * s) @ Vt, 0.0, 1.0)

def stored_numbers(h, w, k):
    return k * (h + w + 1)

def k_for_energy(img, target=0.95):
    s = np.linalg.svd(img, compute_uv=False)
    e = np.cumsum(s ** 2) / np.sum(s ** 2)
    return int(np.searchsorted(e, target) + 1)
```

```python
# src/svdimg/metrics.py
import numpy as np

def rel_fro_error(a, b):
    return float(np.linalg.norm(a - b, "fro") / np.linalg.norm(a, "fro"))

def mse(a, b):
    return float(np.mean((a - b) ** 2))

def psnr(a, b, peak=1.0):
    m = mse(a, b)
    return float("inf") if m == 0.0 else float(10 * np.log10(peak ** 2 / m))
```

```python
# tests/test_core.py
import numpy as np, pytest
from svdimg.images import synthetic
from svdimg.core import compress, reconstruct, stored_numbers
from svdimg.metrics import rel_fro_error

@pytest.mark.parametrize("kind", ["gradient", "shapes", "checker", "texture", "noise"])
def test_eckart_young_unclipped(kind):
    img = synthetic(kind, 64)
    U, s, Vt = np.linalg.svd(img, full_matrices=False)
    k = 8
    Ak = (U[:, :k] * s[:k]) @ Vt[:k]                          # unclipped, so the identity is exact
    assert np.isclose(np.linalg.norm(img - Ak, "fro") ** 2, np.sum(s[k:] ** 2))

def test_full_rank_reconstruction_is_lossless():
    img = synthetic("shapes", 32)
    assert rel_fro_error(img, reconstruct(compress(img, 32))) < 1e-10

def test_storage_break_even():
    h = w = 100
    assert stored_numbers(h, w, 49) < h * w < stored_numbers(h, w, 50)    # break-even near k = 49.75

def test_error_is_monotone_in_k():
    img = synthetic("texture", 64)
    errs = [rel_fro_error(img, reconstruct(compress(img, k))) for k in (1, 4, 16, 32)]
    assert all(a >= b - 1e-12 for a, b in zip(errs, errs[1:]))
```

`[VERIFY]` `test_error_is_monotone_in_k` uses the clipped reconstruction. In a seeded run of this starter code all 8 tests passed, but clipping is non-linear and gives no monotonicity guarantee; if it flakes, test on the unclipped reconstruction.

### 10.5 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3, R9 | Full-rank reconstruction error `< 1e-10`; Eckart–Young identity holds on all synthetic kinds |
| M2 | R4–R6 | Metrics tested against hand-computed tiny cases; `k_for_energy` verified against the cumulative-energy array |
| M3 | R7 | CSV for each image kind with `k, ratio, rel_error, PSNR, energy`; break-even `k` marked |
| M4 | R8, R10 | Color and baseline comparison tables from **your** runs; honest statement of when the baseline wins |
| M5 | Notebook and write-up | Runs end to end seeded; answers the questions below, each citing a table or figure |

### 10.6 Questions the write-up must answer

1. Why do `gradient` and `shapes` compress far better than `noise` and `texture`? Show the spectra.
2. At what `k` does compression stop saving storage for a `128×128` image? Show the arithmetic and a figure.
3. Does a high PSNR always mean the image looks right? Show an example where numbers and visuals disagree (e.g., `checker` or `text` at low `k` shows ringing).
4. For the same stored-number budget, does SVD beat downsampling? On which image kinds?
5. What does this teach you about compressing **embedding matrices** and **weight matrices**, and what would you measure before trusting it?

### 10.7 Failure modes to demonstrate

`k > rank`; `k = 0`; constant (rank-1) image; all-zero image (division by zero in `rel_fro_error`; guard it); values outside `[0, 1]` after reconstruction (clipping changes the error identity); integer `uint8` input forgotten to be scaled; color images treated as `H×(W·3)` by accident; PSNR with `peak` wrong for 8-bit data.

### 10.8 Stretch goals

1. Blockwise SVD (R11) and a comparison with global SVD, with error and storage in a single plot.
2. Randomized SVD for a large image; report accuracy and measured time against the full SVD.
3. SVD denoising: add Gaussian noise, truncate, and plot the PSNR gain vs `k`; find the best `k` and compare with the spectrum gap.
4. Compress a real embedding matrix you have locally and measure nearest-neighbour recall at several `k` (instead of an image) `[VERIFY: data availability; do not assume a download]`.
5. Quantize the factors to 8-bit and report the combined effect on size and quality.

### 10.9 ML connection (README prompt)

Relate the project to: PCA (center → SVD → scores), LoRA (`ΔW = BA`), embedding compression, and weight factorization; state which metric (not PSNR) you would use for each, and why.

### Check yourself (Unit 10)

1. What is the stored-number count for a rank-`k` approximation of an `H×W` image?
2. Why test Eckart–Young on the **unclipped** reconstruction?
3. Why can PSNR mislead?

**Reference answers:** (1) `k(H + W + 1)`. (2) Clipping to `[0, 1]` is a non-linear operation, so the exact identity applies only to the raw truncated sum. (3) It is a pixel-wise average error and does not capture structured artifacts such as ringing or lost edges.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 5 lessons, 2 projects, 10 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to 4C-01 (spectral theorem, SVD proof, PCA), 4C-04 (Markov chains), 4C-08 (recurrent math), and Stage 5 module pointers (PCA, LSA, recommenders, adapters, compression, monitoring).
3. `[VERIFY]` All printed numerical results (stability scales, convergence iteration counts, Hilbert-like error comparisons, storage break-even values) by running the code; report your own numbers rather than quoting any ratio.
4. `[VERIFY]` The two flagged tests in Projects 1 and 2 (tied eigenvalues; clipped monotonicity), and optional dependencies (`scikit-image`, `scipy.sparse.linalg`).

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, speed-up, compression, or accuracy figure appears without the measurement that produced it.
