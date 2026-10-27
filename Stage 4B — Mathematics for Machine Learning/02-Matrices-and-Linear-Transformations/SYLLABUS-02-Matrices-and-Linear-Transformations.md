# SYLLABUS — 02-Matrices-and-Linear-Transformations (S4B-02)

**Stage 4B — Mathematics for Machine Learning · Module 02 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SciPy/Matplotlib/pytest where stated). This file is the blueprint for the files in §0; each unit lists the teaching content, code, failure modes, ML links, labs, and self-checks the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Matrices as data tables and linear maps | `01-matrices-as-data-tables-and-linear-maps.md` | Beginner |
| 3 | Matrix-vector and matrix-matrix multiplication | `02-matrix-vector-and-matrix-matrix-multiplication.md` | Beginner → Intermediate |
| 4 | Transpose, identity, special matrices | `03-transpose-identity-and-special-matrices.md` | Beginner → Intermediate |
| 5 | Matrix shapes, broadcasting, batching | `04-matrix-shapes-broadcasting-and-batching.md` | Intermediate |
| 6 | Linear transformations: rotation, scaling, shear | `05-linear-transformations-rotation-scaling-and-shear.md` | Intermediate |
| 7 | Solving `Ax = b` and Gaussian elimination | `06-solving-ax-equals-b-and-gaussian-elimination.md` | Intermediate |
| 8 | Determinants and invertibility | `07-determinants-and-invertibility.md` | Intermediate |
| 9 | Matrix inverse and when it fails | `08-matrix-inverse-and-when-it-fails.md` | Intermediate → Advanced |
| 10 | Rank and column-space intuition | `09-rank-and-column-space-intuition.md` | Advanced |
| 11 | Practice question bank | `practice-questions.md` | All levels |
| 12 | Project index | `Projects/README.md` | Intermediate |
| 13 | Project: matrix operations from scratch | `Projects/01-matrix-operations-from-scratch.md` | Intermediate |
| 14 | Project: Gaussian elimination solver | `Projects/02-gaussian-elimination-solver.md` | Intermediate → Advanced |
| 15 | Project: linear transformation visualizer | `Projects/03-linear-transformation-visualizer.md` | Intermediate → Advanced |

**Prerequisites:** Module 01 (vectors, dot product, norms, span/independence), Stage 4A Modules 03–04 (algebra, equations and systems). **Plan slot:** weeks 2–3 of `../00-Stage-4-Overview/learning-plan.md` (lessons 1–5, then 6–9).

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library, assertion they agree) → Failure modes → ML link. Shapes are written in comments throughout.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

A dense layer is `Y = XW + b`. A batch of embeddings is a matrix. Attention is three matrix products. Linear regression is solving a linear system. PCA is a decomposition of a matrix. If you can read a matrix as **a table of data** *and* as **a function that moves vectors**, and can predict the shape of every product, you can read most ML code. Most real bugs here are shape, axis, broadcasting, and conditioning bugs, which this module trains explicitly.

### 1.2 Outcomes

1. Build matrices in NumPy; predict `shape` of slices, transposes, and products before running.
2. Implement matrix-vector and matrix-matrix multiplication three ways (loops, dot products, vectorized) and show agreement.
3. Explain `Ax` as a linear combination of columns, and `AB` as composition of maps.
4. Predict the broadcasting result of any two shapes; batch matmul with `@`.
5. Build rotation, scaling, shear matrices and describe their effect on the unit square.
6. Solve `Ax = b` by Gaussian elimination with partial pivoting; compare with `np.linalg.solve`.
7. Use determinant, condition number, and rank to decide if a system is safely solvable.
8. Explain why you almost never call `inv(A)` in production code, and what to do instead.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Matrices as tables and maps | Dataset `X`, weight matrix `W` | Shape drills |
| 2 | Multiplication | Dense layer, batching | `matmul` 3 ways |
| 3 | Transpose, identity, special matrices | `XᵀX`, covariance, orthogonal init | Property tests |
| 4 | Shapes, broadcasting, batching | Bias add, batched attention | Shape predictor quiz |
| 5 | Linear transformations | Feature maps, data augmentation, whitening preview | Transformation gallery |
| 6 | `Ax = b`, Gaussian elimination | Normal equations, linear solve | `solve()` with pivoting |
| 7 | Determinants | Volume scaling, singularity | `det` and log-det |
| 8 | Inverse and failure | Ill-conditioning, collinearity | Condition-number experiments |
| 9 | Rank and column space | Feature redundancy, low rank | Rank diagnostics |

### 1.4 Concept map

```
data table X (n,d) ─┐
                    ├─► Ax = linear combination of columns ─► column space ─► rank
weight W (d,k) ─────┘          │
                               ├─► AB = composition ─► batching / broadcasting
                               ├─► geometry: rotate / scale / shear ─► determinant (area scale)
                               └─► solve Ax=b ─► elimination ─► inverse ─► condition number
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "scipy>=1.11" matplotlib pytest
```

Seed randomness (`np.random.default_rng(0)`); compare with `np.allclose`; every from-scratch function has a reference test; every shape in a comment; **never** call `inv` where `solve` works.

### 1.6 Checkpoint (from the stage plan)

Given random `A (n×d)`, `B (d×k)`, your matmul equals `A @ B` within `1e-10`; you correctly predict 5 broadcast shapes without running them.

### Check yourself (Unit 1)

1. Give two meanings of the matrix `W` in a dense layer.
2. Which function should replace `np.linalg.inv(A) @ b`?

**Reference answers:** (1) A table of numbers, and a linear map from `ℝᵈ` to `ℝᵏ`. (2) `np.linalg.solve(A, b)`.

---

## Unit 2 — Matrices as data tables and linear maps (`01-…md`)

### 2.1 Why ML needs this

`X: (n, d)` is a dataset (rows = samples, columns = features). `W: (d, k)` is a layer's weights. The same object plays both roles; knowing which role you're in tells you what operations are meaningful.

### 2.2 Intuition

- **Table view:** rows are samples, columns are features; operations are about aggregation (`mean(axis=0)`).
- **Map view:** a matrix takes a vector in and returns a vector out. `A: (m, n)` maps `ℝⁿ → ℝᵐ`.
- **Column view of a map:** column `j` of `A` is where the basis vector `eⱼ` lands. This is the key to reading any matrix geometrically.

### 2.3 Mechanics

- Notation: `A ∈ ℝ^{m×n}`, entry `A_{ij}` (row `i`, column `j`); Python `A[i-1, j-1]`.
- Row `A[i, :]` has shape `(n,)`, column `A[:, j]` has shape `(m,)`; `A[i:i+1, :]` keeps 2-D `(1, n)`.
- **Linearity:** `A(x + y) = Ax + Ay`, `A(αx) = α(Ax)`. A function is linear iff it satisfies both. `f(x) = Ax + b` is **affine**, not linear (important for dense layers).
- **Columns land:** `Aeⱼ = A[:, j]`.
- Special shapes: square (`m=n`), tall (`m>n`), wide (`m<n`), row vector `(1,n)`, column vector `(n,1)`.

**Worked example:** `A = [[2, 0], [0, 3]]` sends `e₁ → (2,0)`, `e₂ → (0,3)`: stretches x by 2 and y by 3.

### 2.4 Code

```python
import numpy as np

A = np.array([[2., 0.], [0., 3.]])
e1, e2 = np.eye(2)
assert np.allclose(A @ e1, A[:, 0]) and np.allclose(A @ e2, A[:, 1])   # columns are images of basis vectors

rng = np.random.default_rng(0)
x, y = rng.normal(size=2), rng.normal(size=2)
assert np.allclose(A @ (x + 3 * y), A @ x + 3 * (A @ y))               # linearity

# affine is NOT linear
b = np.array([1., 1.])
f = lambda v: A @ v + b
assert not np.allclose(f(x + y), f(x) + f(y))
```

Shape drill (predict first, then run):

```python
X = rng.normal(size=(100, 4))
print(X.shape, X[0].shape, X[:, 0].shape, X[:5].shape, X[:, :2].shape, X.T.shape, X.mean(axis=0).shape)
# (100,4) (4,) (100,) (5,4) (100,2) (4,100) (4,)
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Calling an affine map "linear" | Wrong claim: `f(0) ≠ 0` | Test `f(0) == 0` |
| `np.matrix` instead of `ndarray` | `*` means matmul, surprising | Use `ndarray` only |
| Row vs column confusion `(n,)`, `(1,n)`, `(n,1)` | Silent broadcasting | Print shapes |
| Integer matrices | Truncation on assignment | `dtype=float` |
| Mutating a slice view | Parent array changes | `.copy()` |

### 2.6 ML link

- Dataset `X: (n, d)`; embedding table `E: (V, d)`; weights `W: (d, k)`.
- A dense layer is **affine**: `XW + b`. The nonlinearity after it is what makes a network more than one big matrix (two stacked linear layers collapse into one).
- Collapse demo: `W1 @ W2` is a single matrix. Show it numerically.

### 2.7 Lab (40 min)

1. Build `X` for 6 houses (`area, rooms, age`); compute column means; center it.
2. Verify linearity and non-linearity tests with random vectors.
3. Show two linear layers equal one: `(X @ W1) @ W2 == X @ (W1 @ W2)`.

### Check yourself (Unit 2)

1. Where does `A e₂` land?
2. Is `x ↦ 2x + 1` linear?
3. Why can't a stack of linear layers without nonlinearities model XOR?

**Reference answers:** (1) At the second column of `A`. (2) No, it is affine (`f(0) = 1`). (3) The stack equals one linear map; XOR is not linearly separable.

---

## Unit 3 — Matrix-vector and matrix-matrix multiplication (`02-…md`)

### 3.1 Why ML needs this

Every forward pass is a chain of matrix products. Understanding multiplication from the *column* and *row* viewpoints turns shape rules into something you derive rather than memorize.

### 3.2 Intuition: four equivalent views

For `A: (m, n)`, `x: (n,)`:

1. **Dot-product view:** `(Ax)ᵢ = rowᵢ(A) · x`.
2. **Column view:** `Ax = Σⱼ xⱼ · colⱼ(A)`, a linear combination of columns. (This links directly to span in Module 01 and to rank in Lesson 9.)
3. **Map view:** apply the transformation.
4. **For `AB`:** `(AB)ᵢⱼ = rowᵢ(A) · colⱼ(B)`; `AB` applies `B` first, then `A` (composition).

### 3.3 Mechanics

- `A: (m, n)` times `B: (n, p)` → `(m, p)`. Inner dimensions must match.
- **Not commutative:** `AB ≠ BA` in general (often one doesn't even exist).
- **Associative:** `(AB)C = A(BC)`, **distributive:** `A(B + C) = AB + AC`.
- **Cost:** `O(mnp)` multiply-adds; association order changes cost: `(AB)v` costs `O(n³)`, `A(Bv)` costs `O(n²)` for square `n×n`.
- `(AB)ᵀ = BᵀAᵀ`.
- Elementwise `A * B` (Hadamard) is a different operation; needs identical (or broadcastable) shapes.

**Worked example:** `A = [[1,2],[3,4]]`, `x = (5, 6)` → `Ax = (17, 39)`; column view: `5·(1,3) + 6·(2,4) = (17, 39)`.

### 3.4 Code

```python
import numpy as np

def matvec_loops(A, x):
    m, n = A.shape
    if x.shape != (n,):
        raise ValueError(f"shape mismatch: A {A.shape}, x {x.shape}")
    y = np.zeros(m)
    for i in range(m):
        for j in range(n):
            y[i] += A[i, j] * x[j]
    return y

def matmul_loops(A, B):
    (m, n), (n2, p) = A.shape, B.shape
    if n != n2:
        raise ValueError(f"inner dimensions differ: {A.shape} @ {B.shape}")
    C = np.zeros((m, p))
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    return C

def matmul_dots(A, B):                      # row · column view
    return np.array([[A[i] @ B[:, j] for j in range(B.shape[1])] for i in range(A.shape[0])])

def matmul_outer(A, B):                     # sum of outer products: AB = Σ_k col_k(A) row_k(B)
    return sum(np.outer(A[:, k], B[k]) for k in range(A.shape[1]))

rng = np.random.default_rng(0)
A, B, x = rng.normal(size=(4, 3)), rng.normal(size=(3, 5)), rng.normal(size=3)
ref = A @ B
for f in (matmul_loops, matmul_dots, matmul_outer):
    assert np.allclose(f(A, B), ref, atol=1e-10)
assert np.allclose(matvec_loops(A, x), A @ x)
assert np.allclose(A @ x, sum(x[j] * A[:, j] for j in range(3)))     # column view
```

Association cost experiment:

```python
import time
n = 1500
M = rng.normal(size=(n, n)); N = rng.normal(size=(n, n)); v = rng.normal(size=n)
t0 = time.perf_counter(); r1 = (M @ N) @ v; t1 = time.perf_counter(); r2 = M @ (N @ v); t2 = time.perf_counter()
print(f"(MN)v {t1-t0:.3f}s   M(Nv) {t2-t1:.4f}s   same: {np.allclose(r1, r2, rtol=1e-6, atol=1e-6)}")
# report your own numbers; do not quote a speed-up you did not measure
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `A * B` when you meant `A @ B` | Broadcast error or wrong values | Use `@` for algebra, `*` for elementwise |
| Inner-dimension mismatch | `ValueError: matmul: Input operand 1 has a mismatch` | Predict shapes; validate |
| `np.dot` on 3-D+ arrays | Surprising semantics | Prefer `@` or `einsum` |
| Wrong association order | Needless `O(n³)` | Multiply right-to-left when the last factor is a vector |
| Assuming `AB = BA` | Wrong refactors | Test with random matrices |
| `float32` accumulation | Small mismatches vs `float64` | Compare with tolerances |

### 3.6 ML link

- **Dense layer:** `H = X @ W + b`, `X: (B, d_in)`, `W: (d_in, d_out)`.
- **Attention:** `scores = Q @ K.T` (Stage 4C-09, 5C-07).
- **Order of products** decides memory/time in LoRA-style factorization: `x @ (A @ B)` vs `(x @ A) @ B` `[JUDGEMENT: cheaper when rank is small]`.
- **Backprop** uses `Wᵀ` and `Xᵀ` products (Module 07).

### 3.7 Lab (60 min)

1. Implement all three matmul variants and `matvec`; test 100 random shapes against `@`.
2. Prove the column view numerically; plot the linear combination in 2D.
3. Time loops vs `@` for `n ∈ {50, 200, 500}`; record machine and library versions.
4. Association experiment above.

### Check yourself (Unit 3)

1. What is the shape of `(5×3)(3×7)`? Of `(3×7)(5×3)`?
2. Write `Ax` as a combination of columns.
3. Why does `A(Bv)` beat `(AB)v` for large square matrices?

**Reference answers:** (1) `(5,7)`; the second product doesn't exist. (2) `Σⱼ xⱼ A[:, j]`. (3) It does two `O(n²)` matrix-vector products instead of one `O(n³)` matrix-matrix product.

---

## Unit 4 — Transpose, identity, and special matrices (`03-…md`)

### 4.1 Why ML needs this

`XᵀX` appears in least squares, covariance, and Gram matrices. Identity is the "do nothing" map in residual connections and ridge. Diagonal matrices are cheap scalings (normalization, Adam's per-parameter scaling), and orthogonal matrices preserve lengths (stable initialization, rotations).

### 4.2 Mechanics

| Matrix | Definition | Key property | ML appearance |
|---|---|---|---|
| Transpose `Aᵀ` | `(Aᵀ)ᵢⱼ = Aⱼᵢ` | `(AB)ᵀ = BᵀAᵀ`, `(Aᵀ)ᵀ = A` | Gradients, normal equations |
| Identity `I` | 1s on diagonal | `AI = IA = A` | Ridge `λI`, skip connections |
| Diagonal `D` | non-zeros only on diagonal | `Dx` scales each coordinate; product and inverse are cheap | Feature scaling, covariance with independent features |
| Symmetric | `A = Aᵀ` | Real eigenvalues (Module 03) | Covariance, Hessian, Gram matrix |
| Orthogonal `Q` | `QᵀQ = I` | Preserves norms and angles, `Q⁻¹ = Qᵀ` | Rotations, orthogonal init |
| Triangular | zeros above/below | Easy to solve (back-substitution) | Gaussian elimination result, Cholesky |
| Permutation `P` | rows of `I` reordered | Orthogonal; reorders rows | Pivoting, shuffling |
| Zero / ones | all 0 / all 1 | `1ᵀx = Σx` | Sums as products |

**Facts worth proving numerically:** `XᵀX` is symmetric and positive semidefinite (`vᵀXᵀXv = ‖Xv‖² ≥ 0`); the Gram matrix of rows is `XXᵀ`.

### 4.3 Code

```python
import numpy as np
rng = np.random.default_rng(0)
A, B = rng.normal(size=(3, 4)), rng.normal(size=(4, 2))

assert np.allclose((A @ B).T, B.T @ A.T)
X = rng.normal(size=(50, 4))
G = X.T @ X
assert np.allclose(G, G.T)
assert np.all(np.linalg.eigvalsh(G) >= -1e-10)               # PSD up to rounding

Q, _ = np.linalg.qr(rng.normal(size=(5, 5)))                 # random orthogonal matrix
v = rng.normal(size=5)
assert np.allclose(Q.T @ Q, np.eye(5))
assert np.isclose(np.linalg.norm(Q @ v), np.linalg.norm(v))  # norm preserved

d = np.array([2., 3., 4.])
D = np.diag(d)
assert np.allclose(D @ np.ones(3), d)                        # diagonal = per-coordinate scaling
assert np.allclose(d[:, None] * np.ones((3, 3)), D @ np.ones((3, 3)))   # cheaper without building D

S = A.T @ A                                                  # symmetrize helper
sym = lambda M: (M + M.T) / 2                                # clean up asymmetry from rounding
```

### 4.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Building a dense `diag(d)` for huge `d` | Memory blow-up | Use `d[:, None] * M` or `M * d` |
| Assuming a computed `XᵀX` is *exactly* symmetric | Tiny asymmetry breaks `eigh`-style assumptions | `sym(M)` before decomposition |
| Treating a *nearly* orthogonal matrix as exactly orthogonal after many multiplications | Drift | Re-orthogonalize with QR |
| `A.T` returns a **view** | Writing to it alters `A` | `.copy()` |
| Confusing `Aᵀ` with `A⁻¹` | Wrong unless `A` orthogonal | Test `AᵀA == I` first |

### 4.5 ML link

- **Normal equations (Module 14):** `XᵀXw = Xᵀy`.
- **Ridge:** `(XᵀX + λI)w = Xᵀy` makes the system solvable (Lesson 8).
- **Residual connections:** `y = x + f(x)` is "identity plus a map" (Stage 5C).
- **Orthogonal initialization** keeps activation norms stable across layers (Stage 4C-07, `[VERIFY]` exact claims there).
- **Covariance matrix** is symmetric PSD (Module 09 and 4C-04).

### 4.6 Lab (45 min)

1. Property-test transpose, symmetry of `XᵀX`, PSD-ness, orthogonality of QR's `Q`.
2. Show that repeated multiplication by a random non-orthogonal matrix explodes or vanishes a vector's norm, while an orthogonal `Q` does not (a preview of vanishing/exploding gradients).

```python
M = rng.normal(size=(50, 50)) / np.sqrt(50) * 1.2
Qm, _ = np.linalg.qr(rng.normal(size=(50, 50)))
v0 = rng.normal(size=50)
for name, W in (("random*1.2", M), ("orthogonal", Qm)):
    v = v0.copy()
    for _ in range(50): v = W @ v
    print(name, np.linalg.norm(v))
```

### Check yourself (Unit 4)

1. Why is `XᵀX` always symmetric?
2. What is `Q⁻¹` for an orthogonal `Q`?
3. Why avoid `np.diag(d) @ M` for large `d`?

**Reference answers:** (1) `(XᵀX)ᵀ = Xᵀ(Xᵀ)ᵀ = XᵀX`. (2) `Qᵀ`. (3) It allocates a dense `d×d` matrix and does a full product; `d[:, None] * M` is `O(dn)` and uses no extra square matrix.

---

## Unit 5 — Matrix shapes, broadcasting, and batching (`04-…md`)

### 5.1 Why ML needs this

This is the most bug-prone lesson in the module. Bias addition, per-feature normalization, batched attention, and loss reduction all depend on broadcasting and batched matmul. A shape error that *doesn't raise* is far worse than one that does.

### 5.2 Mechanics: the broadcasting rule

Align shapes **from the right**. For each pair of dimensions: equal, or one is 1, or one is missing (treated as 1). Otherwise error.

| A shape | B shape | Result | Note |
|---|---|---|---|
| `(5, 3)` | `(3,)` | `(5, 3)` | Bias add (row vector) |
| `(5, 3)` | `(5, 1)` | `(5, 3)` | Per-row scaling |
| `(5, 3)` | `(5,)` | **error** | `3 ≠ 5` |
| `(5,)` | `(5, 1)` | `(5, 5)` | **Silent outer-style blow-up** |
| `(2, 5, 3)` | `(3,)` | `(2, 5, 3)` | Batch bias |
| `(2, 5, 3)` | `(2, 3, 4)` | matmul → `(2, 5, 4)` | Batched matmul |
| `(8, 1, 5, 3)` | `(1, 4, 3, 2)` | matmul → `(8, 4, 5, 2)` | Batch dims broadcast |

- `@` on N-D arrays: the last two axes are the matrices; leading axes broadcast.
- `keepdims=True` keeps a reduced axis so results broadcast correctly.
- `np.newaxis`/`None`, `reshape(-1, 1)`, `expand_dims` create the axes you need.
- `np.einsum` is a precise way to write shapes: `np.einsum("bij,bjk->bik", A, B)`.

### 5.3 Code

```python
import numpy as np
rng = np.random.default_rng(0)

# bias add, per-feature standardization
X = rng.normal(size=(100, 3)); b = rng.normal(size=3)
H = X + b
Z = (X - X.mean(axis=0)) / X.std(axis=0)                 # (100,3) with (3,) broadcasts
assert np.allclose(Z.mean(axis=0), 0, atol=1e-12)

# the silent bug
y = rng.normal(size=5)                                   # (5,)
pred = rng.normal(size=(5, 1))                           # (5,1)
print((y - pred).shape)                                  # (5, 5)  <- a loss computed on this is wrong
assert (y - pred.ravel()).shape == (5,)                  # fix: make shapes agree

# softmax-style normalization needs keepdims
S = rng.normal(size=(4, 6))
P = np.exp(S - S.max(axis=1, keepdims=True))
P /= P.sum(axis=1, keepdims=True)
assert np.allclose(P.sum(axis=1), 1.0)

# batched matmul
Q = rng.normal(size=(2, 5, 8)); K = rng.normal(size=(2, 7, 8))
scores = Q @ K.transpose(0, 2, 1)                        # (2,5,7)
assert np.allclose(scores, np.einsum("bid,bjd->bij", Q, K))

def broadcast_shape(a, b):                               # predictor to train intuition
    return np.broadcast_shapes(a, b)
print(broadcast_shape((8, 1, 5, 3), (4, 1, 3)))          # (8, 4, 5, 3)
```

### 5.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `(n,)` vs `(n,1)` in a loss | `(n, n)` array, wrong mean, no error | Assert shapes at function boundaries |
| Reducing without `keepdims` then broadcasting | Wrong axis aligned or error | Use `keepdims=True` |
| Mixing batch-first and batch-last conventions | Transposed semantics | Document convention (`(B, T, D)`) |
| In-place ops on broadcast views | Error or surprising writes | Make explicit copies |
| `np.dot` vs `@` on 3-D | Different semantics | Prefer `@` / `einsum` |
| Silently broadcasting a mask | Masks applied to wrong axis | Print and assert shapes |

**Defensive helper:**

```python
def check_shape(x, expected, name="array"):
    if x.shape != tuple(expected):
        raise ValueError(f"{name}: expected {tuple(expected)}, got {x.shape}")
    return x
```

### 5.5 ML link

- **Batching:** `X: (B, d)`; sequences `(B, T, D)`; attention heads `(B, H, T, Dh)`.
- **Normalization layers** (Stage 4C-07): reduce over feature axes with `keepdims`.
- **Loss reduction:** shape of `(pred - target)` must match before `.mean()`.
- **GPU frameworks** (PyTorch/JAX) use the same broadcasting rules `[VERIFY: identical rules for the installed versions]`.

### 5.6 Lab (60 min)

1. "Shape predictor" quiz: 15 pairs, write the result or "error" first, then check with `np.broadcast_shapes`.
2. Write the `(n,)` vs `(n,1)` loss bug, catch it with `check_shape`, then add a regression test.
3. Implement a stable row-wise softmax and a batched `QKᵀ` with an `einsum` equivalence test.

### Check yourself (Unit 5)

1. What is `np.broadcast_shapes((5, 1), (1, 7))`?
2. Why is `(y - pred)` with `y:(n,)`, `pred:(n,1)` dangerous?
3. What does `keepdims=True` do?

**Reference answers:** (1) `(5, 7)`. (2) It silently yields `(n, n)`; the mean is over the wrong quantity. (3) Keeps the reduced axis as size 1 so the result broadcasts against the original.

---

## Unit 6 — Linear transformations: rotation, scaling, shear (`05-…md`)

### 6.1 Why ML needs this

Every linear layer is a transformation of feature space. Rotations and scalings explain what PCA and whitening do, what data augmentation does to images, and why `Xᵀ X`-based methods are sensitive to feature scale. Seeing them in 2D builds the intuition used in higher dimensions.

### 6.2 Mechanics

Read the matrix by its **columns** (where `e₁`, `e₂` land).

| Transform | 2D matrix | Effect on the unit square | `det` |
|---|---|---|---|
| Scaling | `[[sx, 0], [0, sy]]` | Stretches axes | `sx·sy` |
| Rotation by `θ` | `[[cos θ, −sin θ], [sin θ, cos θ]]` | Rotates; preserves length/angle | `1` |
| Shear (x by y) | `[[1, k], [0, 1]]` | Slants; preserves area | `1` |
| Reflection (x-axis) | `[[1, 0], [0, −1]]` | Flips orientation | `−1` |
| Projection onto x-axis | `[[1, 0], [0, 0]]` | Collapses a dimension | `0` |

- **Composition:** applying `B` then `A` is `AB`. Order matters: rotate-then-scale ≠ scale-then-rotate.
- **Affine** maps add a translation; use homogeneous coordinates `[x, y, 1]` to put translation in a matrix (Lesson 6.4).
- **Singular values/geometry preview:** any matrix = rotate, scale axes, rotate (SVD, Module 03).

### 6.3 Code

```python
import numpy as np

def rot(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])

def scale(sx, sy): return np.diag([sx, sy])
def shear_x(k):    return np.array([[1., k], [0., 1.]])

square = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], float)     # (2, 5): columns are points

R, S, H = rot(np.pi / 6), scale(2, 0.5), shear_x(0.8)
for M in (R, S, H):
    print(np.round(np.linalg.det(M), 6))           # 1.0, 1.0, 1.0

assert np.allclose(R.T @ R, np.eye(2))             # rotation is orthogonal
assert not np.allclose(R @ S, S @ R)               # order matters

# homogeneous coordinates: translation as a matrix
def translate(tx, ty): return np.array([[1., 0., tx], [0., 1., ty], [0., 0., 1.]])
P = np.vstack([square, np.ones(square.shape[1])])  # (3, 5)
moved = translate(2, 1) @ P
assert np.allclose(moved[:2], square + np.array([[2], [1]]))
```

Plot helper:

```python
import matplotlib.pyplot as plt
def show(M, ax, title):
    out = M @ square
    ax.plot(*square, "k--", label="original"); ax.plot(*out, "C3", label="transformed")
    ax.set_aspect("equal"); ax.grid(True); ax.set_title(f"{title}  det={np.linalg.det(M):.2f}")
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, (M, t) in zip(axes, ((R, "rotate 30°"), (S, "scale"), (H, "shear"))): show(M, ax, t)
```

### 6.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Degrees passed to `np.cos` | Wrong rotation | `np.deg2rad` |
| Points stored as rows but multiplied as columns | Transposed result | Fix a convention: points are columns `(2, N)` |
| Wrong composition order | Different geometry | Right-to-left; test on a simple point |
| Assuming rotation preserves a *non-uniformly scaled* shape | It doesn't | Check `det` and `RᵀR` |
| Treating translation as linear | `f(0) ≠ 0` | Use homogeneous coordinates |

### 6.5 ML link

- **Image augmentation:** rotation, scaling, shear are affine transforms (`[VERIFY]` convention in your library).
- **Whitening/standardization:** a diagonal (or full) scaling of feature space.
- **PCA:** rotate to axes of variance, then scale (Module 03).
- **Spatial transformer / attention-style feature mixing:** learned linear maps in high dimensions.

### 6.6 Lab (60 min)

1. Build the gallery for rotation, scaling, shear, reflection, and a singular projection; annotate `det`.
2. Show non-commutativity visually: rotate→scale vs scale→rotate.
3. Apply a shear to a 2-class scatter; show that a linear classifier trained before can fail after, and recover with the inverse transform.

### Check yourself (Unit 6)

1. What does the second column of a 2D transformation matrix tell you?
2. Why do rotation matrices have `det = 1`?
3. How can translation be written as a matrix product?

**Reference answers:** (1) Where `e₂` lands. (2) Rotations preserve area and orientation. (3) Add a homogeneous coordinate and use a 3×3 matrix with the translation in the last column.

---

## Unit 7 — Solving `Ax = b` and Gaussian elimination (`06-…md`)

### 7.1 Why ML needs this

Least squares reduces to `XᵀXw = Xᵀy`. Kernel methods, Gaussian processes, and Newton-type optimizers all solve linear systems. You should know what the library does and when it fails.

### 7.2 Intuition

`Ax = b` asks: *which combination of the columns of `A` gives `b`?* (Lesson 3 column view.) Each equation is a hyperplane; the solution is where they meet: a point, a line/plane (infinitely many), or nowhere.

### 7.3 Mechanics

- **Elimination:** use row operations (swap, scale, add multiple of one row to another) to reach **upper-triangular** form `U`, then **back-substitute**.
- **Pivoting:** swap in the largest-magnitude entry in the column (partial pivoting) to avoid dividing by tiny numbers.
- **Outcomes:** unique solution (full-rank square), none (inconsistent: `0 = c`), infinite (free variables; rank < columns).
- **Cost:** `O(n³)` for elimination, `O(n²)` for each extra right-hand side if you keep the factorization (**LU**: `PA = LU`).
- **Solve with LU:** `Ly = Pb` (forward), `Ux = y` (back).
- **Overdetermined** (`m > n`): usually no exact solution; least squares instead (Module 14).

### 7.4 Code

```python
import numpy as np

def gauss_solve(A, b, tol=1e-12):
    """Solve Ax=b for square A by Gaussian elimination with partial pivoting."""
    A = np.array(A, dtype=float); b = np.array(b, dtype=float)
    n = A.shape[0]
    if A.shape != (n, n) or b.shape != (n,):
        raise ValueError(f"need square A and matching b, got {A.shape}, {b.shape}")
    for k in range(n):
        p = k + np.argmax(np.abs(A[k:, k]))              # partial pivot
        if abs(A[p, k]) < tol:
            raise np.linalg.LinAlgError("matrix is singular to working precision")
        if p != k:
            A[[k, p]], b[[k, p]] = A[[p, k]], b[[p, k]]
        for i in range(k + 1, n):
            f = A[i, k] / A[k, k]
            A[i, k:] -= f * A[k, k:]
            b[i] -= f * b[k]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):                       # back-substitution
        x[i] = (b[i] - A[i, i + 1:] @ x[i + 1:]) / A[i, i]
    return x

rng = np.random.default_rng(0)
for n in (2, 5, 20, 50):
    A, b = rng.normal(size=(n, n)), rng.normal(size=n)
    assert np.allclose(gauss_solve(A, b), np.linalg.solve(A, b), atol=1e-8)
```

Why pivoting matters:

```python
A = np.array([[1e-20, 1.], [1., 1.]]); b = np.array([1., 2.])
def no_pivot(A, b):
    f = A[1, 0] / A[0, 0]
    u22 = A[1, 1] - f * A[0, 1]; c2 = b[1] - f * b[0]
    x2 = c2 / u22; x1 = (b[0] - A[0, 1] * x2) / A[0, 0]
    return np.array([x1, x2])
print(no_pivot(A, b), gauss_solve(A, b), np.linalg.solve(A, b))   # no_pivot gives x1 = 0; the others ≈ (1, 1)
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| No pivoting | Large errors with tiny pivots (demo above) | Partial pivoting |
| Singular or near-singular `A` | Division by ~0, huge `x` | Pivot tolerance, `cond(A)`, `lstsq` |
| Checking `det ≈ 0` for singularity | Unreliable scale-dependent test | Use rank/condition number |
| Solving with `inv(A) @ b` | Slower, less accurate | `np.linalg.solve` |
| Mutating the caller's `A` in place | Surprising side effects | Copy at entry |
| Overdetermined system given to `solve` | `LinAlgError` (non-square) | `np.linalg.lstsq` |

### 7.6 ML link

- **Normal equations** → Module 14; QR/Cholesky for stability → 4C-01.
- **Newton's method** solves `H p = −g` each step (4C-03).
- **Gaussian processes / kernel ridge** solve `(K + λI)α = y`.
- **Residual check** `‖Ax − b‖` is how you validate any solver output.

### 7.7 Lab (75 min)

1. Implement `gauss_solve` (above) and a version returning `L, U, P`; verify `P A = L U`.
2. Residual and error table for `n ∈ {10, 50, 200}` on random and on Hilbert matrices (`scipy.linalg.hilbert`); report your numbers.
3. Reproduce the no-pivot failure and explain it in two sentences.
4. Handle three outcome types: unique, inconsistent, underdetermined (use `lstsq`, show the minimum-norm solution).

### Check yourself (Unit 7)

1. What does partial pivoting do and why?
2. What is the cost of elimination in `n`, and what do you save by reusing LU?
3. Which function solves overdetermined systems in NumPy?

**Reference answers:** (1) Swaps in the largest entry in the pivot column to avoid dividing by tiny numbers and amplifying rounding error. (2) `O(n³)`; extra right-hand sides cost `O(n²)`. (3) `np.linalg.lstsq`.

---

## Unit 8 — Determinants and invertibility (`07-…md`)

### 8.1 Why ML needs this

The determinant is the **volume-scaling factor** of a transformation. It tells you whether a map collapses space (non-invertible), flips orientation, and it appears in the Gaussian density (`det Σ`) and in normalizing flows (Stage 4C-10). You'll rarely compute it directly in production, and when you do, you use log-determinants.

### 8.2 Mechanics

- 2×2: `det [[a,b],[c,d]] = ad − bc`. The signed area of the parallelogram spanned by the columns.
- **Properties:** `det(AB) = det A · det B`; `det(Aᵀ) = det A`; `det(A⁻¹) = 1/det A`; swapping two rows flips the sign; scaling a row scales `det`.
- **Invertible ⇔ `det ≠ 0` ⇔ columns independent ⇔ full rank ⇔ `Ax=0` has only `x=0`.**
- Triangular: `det` = product of diagonal. Via elimination: `det A = ± Π pivots`.
- **Numerics:** `det` over/underflows quickly; use `np.linalg.slogdet` → `(sign, log|det|)`.
- **Scale confusion:** `det(cA) = cⁿ det A`, so `det ≈ 0` is **not** a reliable singularity test (a well-conditioned `0.1·I₅₀` has `det = 1e-50`).

### 8.3 Code

```python
import numpy as np
rng = np.random.default_rng(0)

A = np.array([[2., 1.], [1., 3.]])
assert np.isclose(np.linalg.det(A), 2*3 - 1*1)

B = rng.normal(size=(4, 4)); C = rng.normal(size=(4, 4))
assert np.isclose(np.linalg.det(B @ C), np.linalg.det(B) * np.linalg.det(C))

# singular example: dependent columns
S = np.array([[1., 2.], [2., 4.]])
print(np.linalg.det(S), np.linalg.matrix_rank(S))        # 0.0  1

# why det is a poor singularity test
M = 0.1 * np.eye(50)
print(np.linalg.det(M), np.linalg.cond(M))               # ~1e-50 yet cond = 1 (perfectly conditioned)
sign, logdet = np.linalg.slogdet(M)
print(sign, logdet, 50 * np.log(0.1))                    # 1.0 -115.129... both equal

# Gaussian log-density uses logdet, never det
def gaussian_logpdf(x, mu, Sigma):
    d = len(mu); diff = x - mu
    sign, logdet = np.linalg.slogdet(Sigma)
    maha = diff @ np.linalg.solve(Sigma, diff)           # solve, not inv
    return -0.5 * (d * np.log(2 * np.pi) + logdet + maha)
```

Area check: the transformed unit square has area `|det|`:

```python
def polygon_area(P):                                     # shoelace, P: (2, N) closed polygon
    x, y = P
    return 0.5 * abs(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))
sq = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], float)
assert np.isclose(polygon_area(A @ sq), abs(np.linalg.det(A)))
```

### 8.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `det ≈ 0` as singular test | False alarms/misses by scale | `cond`, rank, singular values |
| `np.linalg.det` in high dimension | Overflow/underflow to `inf`/`0` | `slogdet` |
| Using `det` to solve systems (Cramer) | `O(n!)`-style cost/instability | Elimination/LU |
| Ignoring sign | Orientation flips unnoticed | Keep the `sign` from `slogdet` |
| Expecting `det(A+B) = det A + det B` | It is not | Test numerically |

### 8.5 ML link

- **Multivariate Gaussian** density: `½ log det Σ` (Module 09/4C-04); Σ must be PD.
- **Normalizing flows:** change of variables uses `log|det J|` (4C-10).
- **Feature redundancy:** `det(XᵀX) = 0` signals collinearity, though `cond` is the better alarm.
- **Volume intuition:** an expansion `|det| > 1` spreads data; `< 1` squeezes it.

### 8.6 Lab (45 min)

1. Verify the area property with the shoelace function across 5 transformations.
2. Show a failing `det` test (`0.1·I`) and fix it with `cond`/`slogdet`.
3. Compute a Gaussian log-density with `slogdet` and compare to `scipy.stats.multivariate_normal.logpdf`.

### Check yourself (Unit 8)

1. What does `|det A|` represent geometrically?
2. Why is `det(A) ≈ 1e-50` not proof that `A` is singular?
3. What should you call instead of `det` in high dimensions?

**Reference answers:** (1) The factor by which `A` scales area/volume. (2) It can come purely from scale (e.g., `0.1·I₅₀` is perfectly conditioned). (3) `np.linalg.slogdet`.

---

## Unit 9 — Matrix inverse and when it fails (`08-…md`)

### 9.1 Why ML needs this

The normal equation `w = (XᵀX)⁻¹Xᵀy` is in every textbook, and explicitly forming that inverse is the first thing you do **not** do in production. This lesson makes you fluent in why, and in what to do when a matrix is singular or nearly so.

### 9.2 Mechanics

- `A⁻¹` exists iff `A` is square and `det A ≠ 0` (equivalently full rank). `AA⁻¹ = A⁻¹A = I`.
- `(AB)⁻¹ = B⁻¹A⁻¹`; `(Aᵀ)⁻¹ = (A⁻¹)ᵀ`.
- **Condition number** `κ(A) = ‖A‖·‖A⁻¹‖` (2-norm: ratio of largest to smallest singular value). Rule of thumb: you can lose about `log₁₀ κ` digits of accuracy `[JUDGEMENT]`. In `float64` (~16 digits), `κ ≳ 1e12` is a red flag.
- **Instead of inverting:** `solve(A, b)`; `lstsq` for rectangular or rank-deficient; **ridge** `(XᵀX + λI)`; **pseudo-inverse** `pinv` (via SVD, Module 03); Cholesky for SPD systems (4C-01).
- **Forming `XᵀX` squares the condition number** (`κ(XᵀX) = κ(X)²`), so the normal equation is worse than QR/`lstsq` on the same data.
- **Inverse of special matrices is easy:** diagonal → reciprocals; orthogonal → transpose; 2×2 → `1/det · [[d,−b],[−c,a]]`.
- **Moore–Penrose pseudo-inverse** gives the minimum-norm least-squares solution.

### 9.3 Code

```python
import numpy as np
rng = np.random.default_rng(0)

A = rng.normal(size=(5, 5)); b = rng.normal(size=5)
x1 = np.linalg.solve(A, b); x2 = np.linalg.inv(A) @ b
assert np.allclose(x1, x2)                                # fine here; differ as cond grows

# ill-conditioned: Hilbert matrix
n = 12
H = 1.0 / (np.arange(n)[:, None] + np.arange(n)[None, :] + 1)    # Hilbert, (12, 12)
x_true = np.ones(n); bH = H @ x_true
print("cond", np.linalg.cond(H))                          # ~1e16
print("solve err", np.linalg.norm(np.linalg.solve(H, bH) - x_true))
print("inv   err", np.linalg.norm(np.linalg.inv(H) @ bH - x_true))   # report your own numbers

# collinear regression: normal equation vs lstsq vs ridge
n_s = 200
x = rng.normal(size=n_s)
X = np.column_stack([x, 2 * x + 1e-8 * rng.normal(size=n_s)])    # nearly collinear
y = 3 * x + rng.normal(scale=0.1, size=n_s)
print("cond(X)", np.linalg.cond(X), " cond(XtX)", np.linalg.cond(X.T @ X))
w_lstsq = np.linalg.lstsq(X, y, rcond=None)[0]
lam = 1e-3
w_ridge = np.linalg.solve(X.T @ X + lam * np.eye(2), X.T @ y)
print(w_lstsq, w_ridge)                                   # in a seeded run, default-rcond lstsq weights were huge (~1e6, opposite signs); ridge stayed small. Report your own.

# singular matrix: exact failure
S = np.array([[1., 2.], [2., 4.]])
try:
    np.linalg.inv(S)
except np.linalg.LinAlgError as e:
    print("LinAlgError:", e)
print(np.linalg.pinv(S))                                  # still defined
```

Safe-solve wrapper (used by Project 2):

```python
def safe_solve(A, b, cond_limit=1e12):
    c = np.linalg.cond(A)
    if not np.isfinite(c) or c > cond_limit:
        raise np.linalg.LinAlgError(f"ill-conditioned (cond={c:.2e}); use lstsq or regularize")
    return np.linalg.solve(A, b)
```

### 9.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `inv(A) @ b` | Slower and less accurate than `solve` | `solve` |
| Normal equation on collinear features | Huge, sign-flipping weights | `lstsq`, QR, ridge |
| Trusting `LinAlgError` to always fire | Near-singular matrices invert without error | Check `cond` |
| Checking `A @ inv(A) ≈ I` as validation | Passes even when `x` is wrong | Check residual `‖Ax − b‖` **and** conditioning |
| Adding tiny jitter blindly | Hides a data problem | Diagnose collinearity first |
| `pinv` on huge matrices | Cost | Use `lstsq` or iterative solvers |

### 9.5 ML link

- **Linear/ridge regression (Module 14):** `(XᵀX + λI)w = Xᵀy`; ridge fixes ill-conditioning.
- **Multicollinearity:** unstable, uninterpretable coefficients despite fine predictions (Module 01, Lesson 5).
- **Covariance inversion** (precision matrix) in Gaussian models, LDA; always regularize/shrink in practice.
- **Second-order optimization:** `H⁻¹g` via `solve` or approximations, never explicit inverses (4C-03).

### 9.6 Lab (75 min)

1. Condition-number sweep: random, Hilbert (`n = 4…14`), and near-collinear designs; plot `cond` and solve error vs `n`.
2. Compare normal equation, `lstsq`, and ridge on a collinear dataset: coefficients, train error, and stability across 20 resamples.
3. Implement and test `safe_solve`; add tests for singular, near-singular, and healthy matrices.
4. Write a one-paragraph runbook, "What I do when a solve is ill-conditioned."

### Check yourself (Unit 9)

1. What does the condition number measure, and what is a worrying value in `float64`?
2. Why is forming `XᵀX` risky?
3. Name three alternatives to `inv(A)`.

**Reference answers:** (1) Sensitivity of the solution to perturbations (ratio of extreme singular values); values around `1e12` and up. (2) It squares the condition number. (3) `solve`, `lstsq`/QR, ridge or `pinv` (also Cholesky for SPD matrices).

---

## Unit 10 — Rank and column-space intuition (`09-…md`)

### 10.1 Why ML needs this

Rank is the number of independent directions in your data or your map. It answers: are my features redundant, how many dimensions does this layer really use, and can this system be solved? Low-rank structure is the foundation of PCA, compression, and parameter-efficient fine-tuning.

### 10.2 Intuition

- **Column space** `C(A)` = all `Ax` = the span of the columns = the set of reachable outputs.
- **Rank** = `dim C(A)` = number of independent columns = number of independent rows (row rank = column rank).
- **Null space** `N(A) = {x : Ax = 0}`: inputs that are crushed to zero. **Rank–nullity:** `rank(A) + dim N(A) = n` (number of columns).
- `Ax = b` is solvable **iff** `b ∈ C(A)`. Unique iff `N(A) = {0}` (full column rank).

### 10.3 Mechanics

- `rank(A) ≤ min(m, n)`. **Full column rank** (`rank = n`) → columns independent; **full row rank** (`rank = m`); **rank-deficient** otherwise.
- `rank(AB) ≤ min(rank A, rank B)`; `rank(AᵀA) = rank(A)`.
- **Rank-1 matrix:** `A = uvᵀ` (outer product); every column is a multiple of `u`.
- **Numerical rank:** count singular values above a tolerance; `matrix_rank` does exactly this. Default tolerance is derived from machine epsilon and the matrix size `[VERIFY: exact rule in the installed NumPy]`.
- **Effective rank** from the singular-value spectrum is often more informative than hard rank; the full treatment comes in Module 03.
- **Summary table (square `A`):**

| Property | Full rank | Rank-deficient |
|---|---|---|
| Invertible | yes | no |
| `det` | ≠ 0 | 0 |
| `Ax = b` | unique solution | none or infinitely many |
| `N(A)` | `{0}` | non-trivial |

### 10.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

u, v = rng.normal(size=(6, 1)), rng.normal(size=(1, 4))
R1 = u @ v                                                # rank-1 by construction
print(np.linalg.matrix_rank(R1))                          # 1

A = rng.normal(size=(6, 4)); A[:, 3] = A[:, 0] + 2 * A[:, 1]   # force dependence
print(np.linalg.matrix_rank(A))                           # 3

def in_column_space(A, b, atol=1e-8):
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    return bool(np.allclose(A @ x, b, atol=atol)), x

b_in = A @ rng.normal(size=4)                             # reachable by construction
b_out = rng.normal(size=6)                                # generically unreachable
print(in_column_space(A, b_in)[0], in_column_space(A, b_out)[0])   # True False

# null space via SVD (Module 03 preview)
U, s, Vt = np.linalg.svd(A)
tol = s.max() * max(A.shape) * np.finfo(float).eps
rank = int((s > tol).sum())
null_basis = Vt[rank:].T                                  # (4, 4 - rank)
assert np.allclose(A @ null_basis, 0, atol=1e-10)
assert rank + null_basis.shape[1] == A.shape[1]           # rank-nullity

# near rank deficiency: spectrum tells the story
Xn = np.column_stack([A[:, :3], A[:, 0] + 2 * A[:, 1] + 1e-6 * rng.normal(size=6)])
print(np.linalg.matrix_rank(Xn), np.linalg.svd(Xn, compute_uv=False))   # rank may be 4 with a tiny σ₄
```

Feature-redundancy diagnostic (reusable):

```python
def rank_report(X, names=None, tol=None):
    s = np.linalg.svd(X - X.mean(axis=0), compute_uv=False)
    r = int((s > (tol if tol is not None else s.max() * max(X.shape) * np.finfo(float).eps)).sum())
    return {"n_features": X.shape[1], "numerical_rank": r,
            "cond": float(s.max() / s.min()) if s.min() > 0 else float("inf"),
            "singular_values": s}
```

### 10.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Treating rank as binary on noisy data | Near-dependence passes as full rank | Inspect the singular-value spectrum, `cond` |
| Not centering before a redundancy check | Constant offsets mask/mimic structure | Center columns (as in `rank_report`) |
| Confusing rank with number of non-zero rows | Wrong counts | Use SVD |
| One-hot of all levels + intercept | Exact dependence (dummy trap) | Drop one level |
| `rank > min(m, n)` claims | Impossible | Sanity-assert |
| More features than samples (`d > n`) | Always rank-deficient `XᵀX` | Regularize, reduce dimension |

### 10.6 ML link

- **Multicollinearity:** rank deficiency of `X` ⇒ non-unique weights (Lesson 9, Module 14).
- **PCA / SVD:** keep the top-`k` directions; rank-`k` approximation (Module 03).
- **Low-rank adapters:** update `ΔW = BA` with small inner dimension `r`, so the update has rank ≤ `r` (Stage 5C/5D mentions `[VERIFY]` module placement).
- **Embedding collapse / dimensional collapse:** low effective rank of embeddings is a recognized failure signal `[JUDGEMENT]`; the `rank_report` above is a simple monitor.
- **`d > n`:** far more features than samples makes the problem underdetermined; need regularization (Module 14).

### 10.7 Lab (75 min)

1. Construct matrices of known rank (outer-product sums) and verify with `matrix_rank` and SVD.
2. Build a design matrix with an exact dependency, a near-dependency, and a dummy-variable trap; run `rank_report` on each; fix the trap two ways.
3. Demonstrate rank-nullity numerically, and `Ax = b` solvability with `in_column_space`.
4. Take random embeddings vs embeddings from a low-dimensional latent (generated by you), compare spectra, and describe what "collapse" would look like.

### Check yourself (Unit 10)

1. Does `Ax = b` have a solution if `b` is outside the column space?
2. If `A` is `6×4` with rank 3, what is `dim N(A)`?
3. Why is "numerical rank" a tolerance-based notion?

**Reference answers:** (1) No. (2) `4 − 3 = 1`. (3) In floating point, tiny singular values from rounding or noise are indistinguishable from zero, so rank is decided by a threshold.

---

## Unit 11 — Practice question bank (`practice-questions.md`)

### 11.1 Structure

About 50 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 12 per tier, each with a hidden answer and a one-line rationale. Mix hand calculations, "predict the shape", runnable code, and ML judgement.

### 11.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 11.3 Seed items

**Q1 [L1] Shapes.** `(5×3)@(3×7)` shape? → `(5, 7)`.
**Q2 [L2] Column view.** `A = [[1,2],[3,4]]`, `x = (2, −1)`: compute `Ax` two ways. → `(0, 2)`; `2·(1,3) − (2,4) = (0,2)`.
**Q3 [L2] Composition.** Rotate 90° then scale x by 2. Matrix? → `S @ R`, with `R = [[0,−1],[1,0]]`, `S = diag(2,1)` → `[[0,−2],[1,0]]`.
**Q4 [L2] Determinant.** `det [[3,1],[2,4]]`? → 10.
**Q5 [L2] Broadcast.** `np.broadcast_shapes((8,1,5),(4,1))`? → `(8, 4, 5)`.
**Q6 [L3] Silent bug.** Loss `((y - pred)**2).mean()` with `y:(n,)`, `pred:(n,1)` returns an odd value. → Broadcasts to `(n, n)`; ravel `pred`.
**Q7 [L3] Solver.** `gauss_solve` returns garbage for `[[1e-20,1],[1,1]]`. → No pivoting; add partial pivoting.
**Q8 [L3] Det test.** `np.linalg.det(A) == 0` is false for a visibly singular float matrix. → Rounding; use rank or `cond`.
**Q9 [L3] Inverse.** `inv(XtX)` runs without error but weights are `±1e8`. → Near-collinear features; `cond(XtX)` huge; use `lstsq` or ridge.
**Q10 [L4] Design.** Choose how to solve least squares on a 100k×50 dataset. → `lstsq`/QR (or ridge via `solve` on `XᵀX+λI` if `cond` is checked); never explicit inverse; validate with residual and `cond`.
**Q11 [L4] Diagnostics.** Build a data-quality check for a feature table before fitting a linear model. → Center, `rank_report`, flag `rank < d`, large `cond`, `d > n`.
**Q12 [L4] Layers.** Why must a network have nonlinearities between linear layers? → Without them the stack collapses to a single matrix.

### 11.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Tables/maps, linearity | 2 | 2 | 1 | 1 |
| Multiplication | 2 | 3 | 2 | 1 |
| Transpose/special matrices | 1 | 2 | 2 | 1 |
| Shapes/broadcasting | 2 | 3 | 3 | 1 |
| Transformations | 1 | 2 | 1 | 1 |
| Solving/elimination | 1 | 2 | 2 | 1 |
| Determinants | 1 | 2 | 1 | 1 |
| Inverse/conditioning | 1 | 2 | 2 | 2 |
| Rank/column space | 1 | 2 | 2 | 2 |

### Check yourself (Unit 11)

1. Which item types need runnable code?
2. Why include a "silent bug" item?

**Reference answers:** (1) All L3 debug items and any answer that depends on floating-point behaviour. (2) Silent shape/broadcast errors are the most costly bug class in vectorized code.

---

## Unit 12 — Project index (`Projects/README.md`)

### 12.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Matrix operations from scratch | Correct, shape-safe multiplication and properties | 1–4 | 4–5 h |
| 2 | Gaussian elimination solver | Pivoting, LU, conditioning awareness | 6–9 | 5–6 h |
| 3 | Linear transformation visualizer | Geometry of maps, determinant, composition | 5, 7–10 | 4–5 h |

Order: 1 → 2 → 3 (3 reuses 1; 2 reuses `matmul` for verification). Outputs feed `mlmath/matrices.py` and `mlmath/linsolve.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverables D2–D3).

### 12.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs NumPy/SciPy reference | 30 |
| Failure-mode handling (singular, shape mismatch, NaN, tiny pivots) | 15 |
| Reproducibility (seeded, pinned, clean venv) | 15 |
| Explanation quality (what each plot/result shows, why it matters for ML) | 15 |
| Code quality (types, shape docstrings) | 15 |
| ML connection paragraph | 10 |

### 12.3 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 12)

1. Which project's output do you reuse as a reference in another?
2. Which stage-library deliverables do these projects feed?

**Reference answers:** (1) Project 1's `matmul` is reused to verify Project 2's `LU`, and by Project 3. (2) D2 and D3.

---

## Unit 13 — Project: Matrix operations from scratch (`Projects/01-…md`)

### 13.1 Brief

Build `matops`, a small library implementing matrix creation, multiplication, transpose, elementwise ops, and property checks **without calling `@`, `np.dot`, or `np.matmul` inside the implementation** (they're allowed in tests as references).

**Industry framing:** reimplementing the primitives once, with validation and tests, is how engineers internalize shape discipline and learn where performance and correctness traps are.

### 13.2 Requirements

| # | Function | Spec |
|---|---|---|
| R1 | `Matrix` wrapper or functions on `ndarray` | Validate 2-D, float dtype |
| R2 | `matvec(A, x)` | Loops and a vectorized-by-rows variant |
| R3 | `matmul(A, B, method)` | `method ∈ {"loops", "dots", "outer"}`; raises on mismatch with a clear message |
| R4 | `transpose(A)` | Returns a copy (documented) |
| R5 | `identity(n)`, `diag(d)`, `is_symmetric`, `is_orthogonal(tol)`, `is_triangular(kind)` | Tolerance-aware |
| R6 | `hadamard(A, B)` | Elementwise, with broadcasting check |
| R7 | `broadcast_add(A, b)` | Row-vector bias add; implemented manually |
| R8 | `batched_matmul(A, B)` | `(b,m,n)·(b,n,p)`; loop over `b`, then vectorize |
| R9 | `trace`, `frobenius_norm` | |
| R10 | `chain_cost(shapes)` | Returns multiply-add counts for left-to-right vs right-to-left association, and the best order for 3–4 matrices |

### 13.3 Layout and starter

```
matops/
├── pyproject.toml  requirements.txt  README.md
├── src/matops/{__init__,core,special,batched,cost}.py
├── tests/{test_core,test_special,test_batched,test_cost}.py
├── notebooks/02_matrices.ipynb
└── bench/bench_matmul.py
```

```python
# src/matops/core.py
from __future__ import annotations
import numpy as np
from numpy.typing import ArrayLike, NDArray

def _mat(x: ArrayLike, name: str = "A") -> NDArray[np.float64]:
    a = np.asarray(x, dtype=np.float64)
    if a.ndim != 2:
        raise ValueError(f"{name} must be 2-D, got ndim={a.ndim}")
    return a

def matmul(A: ArrayLike, B: ArrayLike, method: str = "dots") -> NDArray[np.float64]:
    """A: (m, n), B: (n, p) -> (m, p)."""
    A, B = _mat(A, "A"), _mat(B, "B")
    (m, n), (n2, p) = A.shape, B.shape
    if n != n2:
        raise ValueError(f"inner dimensions differ: {A.shape} @ {B.shape}")
    C = np.zeros((m, p))
    if method == "loops":
        for i in range(m):
            for j in range(p):
                for k in range(n):
                    C[i, j] += A[i, k] * B[k, j]
    elif method == "dots":
        for i in range(m):
            for j in range(p):
                C[i, j] = np.sum(A[i, :] * B[:, j])
    elif method == "outer":
        for k in range(n):
            C += np.outer(A[:, k], B[k, :])
    else:
        raise ValueError(f"unknown method {method!r}")
    return C
```

```python
# src/matops/cost.py
def matmul_flops(m, n, p):                     # multiply-adds for (m×n)(n×p)
    return m * n * p

def chain_cost(shapes):
    """shapes: [(m0,m1),(m1,m2),...]; returns (left_to_right, right_to_left, best_dp)."""
    dims = [shapes[0][0]] + [s[1] for s in shapes]
    for (a, b), (c, d) in zip(shapes, shapes[1:]):
        if b != c:
            raise ValueError(f"incompatible chain at {(a, b)} x {(c, d)}")
    ltr, cur = 0, dims[0]
    for i in range(1, len(shapes)):
        ltr += cur * dims[i] * dims[i + 1]
    rtl = 0
    for i in range(len(shapes) - 1, 0, -1):
        rtl += dims[i - 1] * dims[i] * dims[-1]
    n = len(shapes)
    dp = [[0] * n for _ in range(n)]
    for L in range(2, n + 1):
        for i in range(n - L + 1):
            j = i + L - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1] for k in range(i, j))
    return ltr, rtl, dp[0][n - 1]
```

(The DP is the classic matrix-chain ordering from Stage 3; link back to the relevant DSA lesson `[VERIFY]` and state what is new here: the ML meaning, i.e. `x @ (A @ B)` vs `(x @ A) @ B`.)

```python
# tests/test_core.py
import numpy as np, pytest
from matops.core import matmul

rng = np.random.default_rng(0)

@pytest.mark.parametrize("method", ["loops", "dots", "outer"])
@pytest.mark.parametrize("shape", [(1, 1, 1), (3, 4, 5), (7, 2, 9), (10, 10, 10)])
def test_matches_numpy(method, shape):
    m, n, p = shape
    A, B = rng.normal(size=(m, n)), rng.normal(size=(n, p))
    assert np.allclose(matmul(A, B, method), A @ B, atol=1e-10)

def test_inner_mismatch_raises():
    with pytest.raises(ValueError, match="inner dimensions"):
        matmul(np.ones((2, 3)), np.ones((4, 2)))

def test_not_commutative():
    A, B = rng.normal(size=(3, 3)), rng.normal(size=(3, 3))
    assert not np.allclose(matmul(A, B), matmul(B, A))
```

### 13.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R4 | 100 random shapes match `@` within `1e-10`; mismatches raise `ValueError` |
| M2 | R5–R7, R9 | Property tests: `(AB)ᵀ = BᵀAᵀ`, `QᵀQ = I`, `XᵀX` symmetric |
| M3 | R8 | Batched matches `A @ B` for `(b,m,n)·(b,n,p)`; broadcasting a single `B` across the batch works |
| M4 | R10 | `chain_cost` reproduces hand-computed counts for 3 examples; DP never exceeds either naive order |
| M5 | Bench + notebook | Timing table (loops/dots/outer vs `@`) for `n ∈ {50, 200, 500}` from your machine, with versions |

### 13.5 Failure-mode table (README, ≥ 8 rows)

Seed with: inner mismatch, 1-D input, non-float dtype, `(n,)` vs `(n,1)` bias, empty matrix, NaN entries, non-square for `trace`, near-orthogonal matrix after repeated products.

### 13.6 Stretch goals

1. `hypothesis` property tests for associativity/distributivity within tolerance.
2. Blocked (tiled) matmul and a cache-effect experiment; report only measured results.
3. `einsum` versions of every function with equivalence tests.
4. `mypy --strict`.

### 13.7 ML connection (README prompt)

Describe a dense layer, a batched attention-score computation, and a LoRA-style factor order choice using your functions and `chain_cost`.

### Check yourself (Unit 13)

1. Why are `@` and `np.dot` banned in the implementation but used in tests?
2. What does `chain_cost` teach about `x @ (A @ B)` vs `(x @ A) @ B`?

**Reference answers:** (1) The implementation must be independent so that tests compare against a trusted reference. (2) The cheaper association depends on shapes; when `x` is a vector or low-rank factors are narrow, multiplying `x` through first is far cheaper.

---

## Unit 14 — Project: Gaussian elimination solver (`Projects/02-…md`)

### 14.1 Brief

Build `linsolve`: a Gaussian-elimination / LU solver with partial pivoting, singularity and conditioning diagnostics, and a least-squares fallback; benchmark and stress-test it against `np.linalg.solve` and `scipy.linalg`.

**Industry framing:** production code wraps numerical routines with diagnostics, so failures become clear exceptions or warnings rather than silently wrong numbers.

### 14.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | `lu_decompose(A)` | Returns `P, L, U` with `P @ A == L @ U`; partial pivoting; tolerance-based singularity detection |
| R2 | `forward_sub`, `back_sub` | Triangular solves; validate triangularity |
| R3 | `solve(A, b)` | Uses R1–R2; supports `b: (n,)` and `(n, k)` (reuse the factorization) |
| R4 | `det_from_lu(A)` | Returns `(sign, logabsdet)`; compare to `slogdet` |
| R5 | `inverse(A)` | Built via `solve(A, I)`; docstring warns against use; for teaching only |
| R6 | `diagnose(A, b=None)` | Returns dict: `shape`, `numerical_rank`, `cond`, `singular`, `residual` (if `b`), and a verdict (`ok`, `ill_conditioned`, `singular`, `non_square`) |
| R7 | `solve_general(A, b)` | Routes: square & healthy → `solve`; ill-conditioned/rank-deficient/rectangular → `lstsq` with a warning and the minimum-norm solution; reports which path ran |
| R8 | Step trace mode | Optional `verbose=True` prints each row operation (for learning) |
| R9 | Outcome classification | For `Ax=b`: `unique`, `none`, `infinite` using rank of `A` vs `[A|b]` |

### 14.3 Layout and starter

```
linsolve/
├── pyproject.toml  requirements.txt  README.md
├── src/linsolve/{__init__,lu,triangular,diagnose,router}.py
├── tests/{test_lu,test_triangular,test_diagnose,test_router,test_stress}.py
├── notebooks/02_gaussian_elimination.ipynb
└── bench/bench_solve.py
```

```python
# src/linsolve/lu.py
import numpy as np

def lu_decompose(A, tol=1e-12):
    """Return P, L, U with P @ A = L @ U (partial pivoting)."""
    A = np.array(A, dtype=float)
    n = A.shape[0]
    if A.shape != (n, n):
        raise ValueError(f"square matrix required, got {A.shape}")
    P, L, U = np.eye(n), np.eye(n), A.copy()
    for k in range(n):
        p = k + int(np.argmax(np.abs(U[k:, k])))
        if abs(U[p, k]) < tol * max(1.0, np.abs(A).max()):
            raise np.linalg.LinAlgError(f"singular to working precision at column {k}")
        if p != k:
            U[[k, p]] = U[[p, k]]
            P[[k, p]] = P[[p, k]]
            L[[k, p], :k] = L[[p, k], :k]
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] -= L[i, k] * U[k, k:]
    return P, L, U
```

```python
# src/linsolve/triangular.py
import numpy as np

def forward_sub(L, b):
    n = L.shape[0]; y = np.zeros(n)
    for i in range(n):
        y[i] = (b[i] - L[i, :i] @ y[:i]) / L[i, i]
    return y

def back_sub(U, y):
    n = U.shape[0]; x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - U[i, i + 1:] @ x[i + 1:]) / U[i, i]
    return x
```

```python
# tests/test_lu.py
import numpy as np, pytest
from linsolve.lu import lu_decompose
from linsolve.triangular import forward_sub, back_sub

rng = np.random.default_rng(0)

@pytest.mark.parametrize("n", [2, 3, 10, 40])
def test_plu_reconstructs(n):
    A = rng.normal(size=(n, n))
    P, L, U = lu_decompose(A)
    assert np.allclose(P @ A, L @ U, atol=1e-9)
    assert np.allclose(np.tril(L), L) and np.allclose(np.triu(U), U)

@pytest.mark.parametrize("n", [3, 10, 40])
def test_solve_matches_numpy(n):
    A, b = rng.normal(size=(n, n)), rng.normal(size=n)
    P, L, U = lu_decompose(A)
    x = back_sub(U, forward_sub(L, P @ b))
    assert np.allclose(x, np.linalg.solve(A, b), atol=1e-8)

def test_singular_raises():
    with pytest.raises(np.linalg.LinAlgError):
        lu_decompose(np.array([[1., 2.], [2., 4.]]))
```

Outcome classification sketch (R9):

```python
def classify(A, b, tol=None):
    A, b = np.asarray(A, float), np.asarray(b, float)
    rA = np.linalg.matrix_rank(A, tol=tol)
    rAb = np.linalg.matrix_rank(np.column_stack([A, b]), tol=tol)
    if rA < rAb: return "none"
    return "unique" if rA == A.shape[1] else "infinite"
```

### 14.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | `P A = L U` and solutions match `np.linalg.solve` (`atol=1e-8`) on 200 random systems for `n ∈ [2, 60]` |
| M2 | R4, R8 | `det_from_lu` matches `slogdet` in sign and magnitude; trace output matches a hand-worked 3×3 example in the notebook |
| M3 | R6–R7, R9 | Correct verdict on: healthy, Hilbert (`n=12`), exactly singular, collinear design, wide and tall systems; `solve_general` never raises on a rectangular input |
| M4 | Stress and benchmark | Residual and relative-error table over `n ∈ {10, 50, 200}` vs `np.linalg.solve` and `scipy.linalg.lu_factor`; pivoting vs no-pivot demo included |
| M5 | Notebook and write-up | Runs end to end seeded; explains each failure case in two sentences |

### 14.5 Failure-mode catalogue (README, ≥ 10 rows)

Seed with: zero pivot, tiny pivot (1e-20), exact singular, near-singular (Hilbert), rectangular input, `b` shape `(n,)` vs `(n,1)`, NaN/inf entries, integer dtype input, very large scale differences between rows, `b` outside the column space.

Improve the router with **row scaling (equilibration)** as a stretch to see how pre-scaling changes `cond` `[VERIFY]` results on your data.

### 14.6 Stretch goals

1. Complete pivoting and compare error to partial pivoting.
2. Cholesky for SPD systems; compare cost and error to LU.
3. Iterative refinement: one step of `r = b − Ax; solve A d = r; x += d`; report the improvement.
4. Banded or sparse solver comparison with `scipy.sparse.linalg` `[VERIFY: API for the installed SciPy]`.

### 14.7 ML connection (README prompt)

Use `solve_general` to fit linear regression on (a) well-conditioned, (b) collinear, (c) `d > n` data; show the router's decisions and compare coefficients with ridge. Cross-link to Module 14.

### Check yourself (Unit 14)

1. Why does `lu_decompose` return `P`?
2. Which test shows pivoting actually helps?
3. How do you detect "no solution" vs "infinitely many"?

**Reference answers:** (1) Row swaps from pivoting are recorded so `P A = L U` holds. (2) A near-zero-pivot matrix such as `[[1e-20,1],[1,1]]` where the no-pivot variant fails and the pivoted one agrees with NumPy. (3) Compare `rank(A)` with `rank([A|b])`: if the latter is larger, none; if equal and less than the number of columns, infinite.

---

## Unit 15 — Project: Linear transformation visualizer (`Projects/03-…md`)

### 15.1 Brief

Build `lintrans`, a visualizer (Matplotlib; `ipywidgets` sliders optional) that shows how any 2×2 (and optionally 3×3) matrix transforms the plane: the grid, unit square, a point cloud, basis vectors, eigen-directions (preview), determinant as area, and what happens to a classifier's boundary.

**Industry framing:** diagnostic visuals help engineers reason about what a layer or preprocessing step does to a data distribution before they trust downstream metrics.

### 15.2 Required views

| # | View | Shows |
|---|---|---|
| V1 | Grid warp | A grid of lines before/after; the columns of `A` as arrows from the origin |
| V2 | Unit square/circle | Parallelogram/ellipse; area annotated with `det` |
| V3 | Gallery | Rotation, scaling, shear, reflection, projection (singular), each with `det` and `cond` |
| V4 | Composition | `A`, `B`, `AB`, `BA` side by side; shows non-commutativity |
| V5 | Point cloud | 2D Gaussian blob before/after; sample covariance printed (`AΣAᵀ`, verified numerically) |
| V6 | Inverse | `A⁻¹` undoes `A` for invertible; collapsed shape for singular, with the explanation |
| V7 | Classifier effect | Two-class data and a fixed linear boundary; apply `A`; show boundary mapping (`w' = A⁻ᵀw`) and accuracy before/after |
| V8 | Preview: SVD view | Circle → ellipse with semi-axes from singular values (`np.linalg.svd`); mark as a Module 03 preview |

### 15.3 Starter code

```python
import numpy as np
import matplotlib.pyplot as plt

def grid_lines(lim=3, n=13, pts=50):
    t = np.linspace(-lim, lim, pts)
    lines = []
    for c in np.linspace(-lim, lim, n):
        lines.append(np.vstack([t, np.full_like(t, c)]))      # horizontal, (2, pts)
        lines.append(np.vstack([np.full_like(t, c), t]))      # vertical
    return lines

def plot_transform(A, ax, title=""):
    for L in grid_lines():
        ax.plot(*L, color="0.85", lw=0.8)
        ax.plot(*(A @ L), color="C0", lw=0.8)
    for col, c in zip(A.T, ("C3", "C2")):
        ax.annotate("", xy=col, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=c, lw=2))
    theta = np.linspace(0, 2 * np.pi, 200)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    ax.plot(*(A @ circle), "k", lw=1.5)
    ax.set_aspect("equal"); ax.set_xlim(-4, 4); ax.set_ylim(-4, 4); ax.grid(False)
    ax.set_title(f"{title}  det={np.linalg.det(A):.2f}  cond={np.linalg.cond(A):.1f}")

# covariance of a transformed Gaussian cloud: verify AΣAᵀ
rng = np.random.default_rng(0)
A = np.array([[1.5, 0.5], [0.0, 0.8]])
Z = rng.normal(size=(2, 20000))                                # N(0, I)
Y = A @ Z
print(np.round(np.cov(Y), 2)); print(np.round(A @ A.T, 2))     # should match closely

# boundary mapping: points x with w·x = 0 map to x' = A x; new normal is A^{-T} w
w = np.array([1.0, -1.0]); A_inv_T = np.linalg.inv(A).T
w_new = A_inv_T @ w
x_on = np.array([1.0, 1.0]); assert abs(w @ x_on) < 1e-12
assert abs(w_new @ (A @ x_on)) < 1e-12                          # still on the boundary after mapping

# SVD view
U, s, Vt = np.linalg.svd(A)
print("semi-axes of the image ellipse:", s)
```

### 15.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | V1–V3 | Arrow endpoints equal `A[:, j]`; annotated `det` equals the shoelace-computed area of the image of the unit square (test, `atol=1e-9`) |
| M2 | V4 | `AB ≠ BA` shown for a rotation and a scaling; test compares the plotted points to `(A@B)@pts` |
| M3 | V5–V6 | Sample covariance within 5% of `AΣAᵀ` at `n=20000`; `A⁻¹(A pts) ≈ pts` for 5 random invertible `A`; singular case flagged, not crashed |
| M4 | V7–V8 | Boundary-mapping assertion passes; ellipse semi-axes match singular values (measured by sampling the image curve) |
| M5 | Write-up | Answers to the questions below, each citing a figure; figures seeded and saved to `results/` |

### 15.5 Questions the write-up must answer

1. What do the columns of `A` tell you about the transformation of the grid?
2. When `det < 0`, what changes visually (orientation), and does `|det|` still equal the area scale?
3. What happens to the image of the circle as `cond(A)` grows, and what does that imply for noise sensitivity of `Ax = b`?
4. Why is the mapped covariance `AΣAᵀ` and not `AΣ`?
5. After a shear, why can a previously good linear classifier lose accuracy, and how does transforming the boundary with `A⁻ᵀw` restore it?

### 15.6 Failure modes to demonstrate

Singular `A` (collapse to a line: `det = 0`, `cond = ∞`); near-singular (extremely thin ellipse); transposing points vs columns; degrees vs radians; applying `A` to row-stored points without transposing.

### 15.7 Stretch goals

1. 3D version for 3×3 matrices (unit cube → parallelepiped; `det` as volume).
2. Interactive sliders for matrix entries with live `det`, `cond`, singular values.
3. Animate the transformation as `M(t) = (1−t)I + tA` `[VERIFY: intermediate matrices may be singular for some A]`.
4. Fit a transformation: given before/after point sets, recover `A` with `lstsq`, compare with the truth, and report error vs noise.

### 15.8 Evaluation

Shared rubric (Unit 12). Extra bar: every figure has labelled axes and a one-sentence takeaway; no claim without a figure or a number from your own runs.

### Check yourself (Unit 15)

1. How do you draw the image of the unit square under `A`?
2. How does the normal vector of a boundary transform under `A`?
3. What does a very thin image ellipse tell you about `A`?

**Reference answers:** (1) Multiply the square's corner coordinates by `A` (points as columns) and connect them. (2) By `A⁻ᵀ`, not `A`. (3) A large condition number: nearly singular, so solving with it amplifies error.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 9 lessons, 3 projects, 15 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to 4C-01 (QR/Cholesky), 4C-03 (Newton), 4C-07 (normalization/init), 4C-10 (flows), and the Stage 3 matrix-chain lesson.
3. `[VERIFY]` `matrix_rank` tolerance rule and the `np.broadcast_shapes` availability in the pinned NumPy.
4. `[VERIFY]` All printed numerical results (Hilbert errors, association timings, covariance matches) by running the code; report your own numbers rather than quoting any ratio.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, speed-up, or accuracy figure appears without the measurement that produced it.
