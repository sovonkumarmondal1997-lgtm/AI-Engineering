# SYLLABUS — 01-Vectors-Dot-Product-and-Norms (S4B-01)

**Stage 4B — Mathematics for Machine Learning · Module 01 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (and SciPy/Matplotlib/pytest where stated). This syllabus is the blueprint for the files listed in §0; each unit gives the teaching content, labs, failure modes, ML links, and self-checks that the final lesson file should contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Vectors in n dimensions and NumPy arrays | `01-vectors-in-n-dimensions-and-numpy-arrays.md` | Beginner |
| 3 | Dot product and its geometric meaning | `02-dot-product-and-its-geometric-meaning.md` | Beginner → Intermediate |
| 4 | Projection onto a vector | `03-projection-onto-a-vector.md` | Intermediate |
| 5 | Norms (L1, L2, L∞) and distance | `04-norms-l1-l2-and-infinity-and-distance.md` | Intermediate |
| 6 | Linear combinations, span, linear independence | `05-linear-combinations-span-and-linear-independence.md` | Intermediate → Advanced |
| 7 | Practice question bank | `practice-questions.md` | All levels |
| 8 | Project index | `Projects/README.md` | Intermediate |
| 9 | Project: vector operations library in NumPy | `Projects/01-vector-operations-library-in-numpy.md` | Intermediate |
| 10 | Project: geometry of dot product explorer | `Projects/02-geometry-of-dot-product-explorer.md` | Intermediate → Advanced |

**Prerequisites (Stage 4A):** Module 09 (vectors as arrows and data points), Module 08 (trigonometry, cosine), Module 10 (summation notation), Module 15 (formula → Python). **Stage 4B Overview:** `../00-Stage-4-Overview/learning-plan.md` allots week 1 to this module.

**Every lesson follows the six-beat shape:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module comes first

Almost every object in ML is a vector: a feature row, a word embedding, a gradient, a weight vector, a residual, a token's hidden state. Almost every operation is a dot product or a norm: a linear layer's output, a similarity score, an L2 penalty, a distance in k-NN, an attention score. If you misread shapes or confuse norms here, every later module inherits the bug.

### 1.2 What you will be able to do

1. Represent data as NumPy arrays of the right shape and dtype, and predict `shape`, `ndim` before running code.
2. Write dot product, norm, distance, cosine, and projection both as loops and vectorized, and show they agree.
3. Explain `a·b = ‖a‖‖b‖cos θ` and use it to reason about alignment, orthogonality, and sign.
4. Choose L1, L2, or L∞ for a penalty or a distance and say what behaviour each induces.
5. Decide whether a set of feature vectors is linearly independent, and say what rank deficiency does to a model.
6. Recognize each concept inside a real ML component: linear layer, cosine retrieval, weight decay, lasso, k-NN.

### 1.3 Lesson sequence and time

`[JUDGEMENT]` about 8–10 hours total, matching week 1 of the default plan.

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Vectors and NumPy arrays | Feature rows, embeddings | `vectors.py` basics |
| 2 | Dot product | Linear model score, attention score | Dot-product tests |
| 3 | Projection | Least squares intuition, residual | `project()` + residual check |
| 4 | Norms and distance | Regularization, k-NN, loss | `norm()`, `distance()` |
| 5 | Span and independence | Collinear features, rank | `is_independent()` |

### 1.4 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "scipy>=1.11" matplotlib pytest
```

- Seed randomness: `rng = np.random.default_rng(0)`.
- Compare floats with `np.allclose`, never `==`.
- Write shapes in comments: `x: (d,)`, `X: (n, d)`.
- Every from-scratch function gets a test against a NumPy/SciPy reference.

### 1.5 Concept map

```
vector ──► dot product ──► angle / cosine ──► projection ──► residual (least squares, Module 14)
   │            │                                   
   └──► norm ──► distance ──► regularization (L1/L2), k-NN
   └──► linear combination ──► span ──► independence ──► rank (Module 02)
```

### 1.6 Assessment

`practice-questions.md` (Unit 7), two projects (Units 9–10), and the checkpoint: *your `dot`, `norm`, `cosine`, `project` agree with NumPy within `1e-10` on 100 random inputs, and you correctly predict 5 shape outcomes without running them.*

### Check yourself (Unit 1)

1. Name three ML objects that are vectors and one operation applied to each.
2. Why do we write shapes in comments?

**Reference answers:** (1) feature row → dot with weights; embedding → cosine against another; gradient → L2 norm for clipping. (2) Most silent bugs are shape or axis errors; stating shapes makes them visible.

---

## Unit 2 — Vectors in n dimensions and NumPy arrays (`01-…md`)

### 2.1 Why ML needs this

A row of a tabular dataset with 30 features is a point in 30-dimensional space. A sentence embedding with 768 numbers is a point in 768 dimensions. A model's parameters are one long vector. Understanding vectors as *both* an array of numbers and a point/arrow is the lingua franca between math notation and code.

### 2.2 Intuition

- **Three views:** a list of numbers; an arrow from the origin; a point. In 2D you can draw all three; in 768D you only keep the list, but the geometry still holds.
- **Operations:** add (tip to tail), scale (stretch/flip), and nothing else is needed yet.
- **Dimension** = number of components = `len(x)` = `x.shape[0]` for a 1-D array.

### 2.3 Mechanics

For `x, y ∈ ℝᵈ` and scalar `α`:

- `x + y = (x₁+y₁, …, x_d+y_d)`, `αx = (αx₁, …, αx_d)`.
- Zero vector `0`; negation `−x`; subtraction `x − y` is the arrow *from y to x*.
- Component access `x_i` (math is 1-indexed, Python is 0-indexed: the classic off-by-one from 4A-15).
- Elementwise (Hadamard) product `x ⊙ y` is **not** the dot product. NumPy's `*` is elementwise.

### 2.4 NumPy essentials for this lesson

| Concept | Code | Note |
|---|---|---|
| Create | `np.array([1., 2., 3.])` | Pass floats to avoid integer dtype |
| Shape | `x.shape == (3,)`, `x.ndim == 1` | 1-D is not a row or a column |
| Dtype | `x.dtype` | `float64` default; `float32` in deep learning |
| Row/column view | `x.reshape(1, -1)`, `x[:, None]` | Needed for matrix ops later |
| Stack data | `X = np.stack([x, y])` → `(2, d)` | Rows = samples |
| Slicing | `X[:, 0]` first feature of all rows | |
| Broadcasting | `X - X.mean(axis=0)` | Subtracts column means |
| Views vs copies | `y = x` aliases; `y = x.copy()` | Mutating aliases changes both |

**Worked example:** center a dataset.

```python
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(loc=5.0, scale=2.0, size=(100, 3))   # X: (n=100, d=3)
mu = X.mean(axis=0)                                  # mu: (3,)
Xc = X - mu                                          # broadcast (100,3) - (3,)
assert np.allclose(Xc.mean(axis=0), 0.0)
```

### 2.5 From scratch vs library

```python
def add(x, y):
    if len(x) != len(y):
        raise ValueError(f"dimension mismatch: {len(x)} vs {len(y)}")
    return [a + b for a, b in zip(x, y)]

def scale(alpha, x):
    return [alpha * a for a in x]

x, y = [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]
assert np.allclose(add(x, y), np.array(x) + np.array(y))
```

Then benchmark loop vs vectorized:

```python
import timeit
a = np.random.default_rng(0).normal(size=1_000_000)
b = np.random.default_rng(1).normal(size=1_000_000)
t_loop = timeit.timeit(lambda: [p + q for p, q in zip(a, b)], number=3)
t_vec  = timeit.timeit(lambda: a + b, number=3)
print(f"loop {t_loop:.3f}s  numpy {t_vec:.3f}s")   # report your own numbers, do not assume a ratio
```

### 2.6 Failure modes (the "break it" cell)

| Mistake | Symptom | Guard |
|---|---|---|
| Integer arrays: `np.array([1, 2, 3]) / 2` fine, but `x[0] = 0.5` truncates to 0 | Silent rounding | `dtype=float` |
| `(3,)` + `(4,)` | `ValueError: operands could not be broadcast` | Validate shapes |
| `(3,)` vs `(3,1)` | Unexpected `(3,3)` result via broadcasting | Print shapes; use `ravel()` |
| Aliasing: `y = x; y[0] = 9` | `x` changes too | `.copy()` |
| `float32` accumulation | Small errors in large sums | Use `float64` for checks |
| Python lists in math | `[1,2]*2` repeats the list | Convert with `np.asarray` |

### 2.7 ML link

- A dataset is `X: (n, d)`; a batch is `X: (B, d)`; an embedding table is `E: (V, d)`.
- Feature standardization (`(X - mu)/sigma`) is vector arithmetic with broadcasting.
- Parameters flattened into one vector are what optimizers update (Module 08).

### 2.8 Lab (30–45 min)

1. Build a tiny dataset of 5 houses (`area, rooms, age`) as `(5, 3)`; center and standardize it.
2. Predict then print `shape` for: `X[0]`, `X[:, 0]`, `X[:2]`, `X.T`, `X.mean(axis=1)`.
3. Create the aliasing bug on purpose and fix it.

### Check yourself (Unit 2)

1. What is the shape of `np.array([[1,2,3]])` vs `np.array([1,2,3])`?
2. Why is `x * y` not the dot product?
3. What does `X.mean(axis=0)` return for `X: (n, d)`?

**Reference answers:** (1) `(1, 3)` vs `(3,)`. (2) It multiplies elementwise and returns a vector; the dot product sums those products to a scalar. (3) The per-feature mean, shape `(d,)`.

---

## Unit 3 — Dot product and its geometric meaning (`02-…md`)

### 3.1 Why ML needs this

A linear model predicts `ŷ = w·x + b`. A neuron's pre-activation is a dot product. Attention scores are dot products of query and key vectors. Similarity search ranks by dot product or its normalized form. This is the single most-executed operation in ML.

### 3.2 Intuition

The dot product measures **alignment**: large positive when vectors point the same way, zero when perpendicular, negative when opposed. It also equals "how much of `a` lies along `b`, times the length of `b`".

### 3.3 Mechanics

- **Algebraic:** `a·b = Σᵢ aᵢbᵢ`.
- **Geometric:** `a·b = ‖a‖‖b‖cos θ`, so `cos θ = a·b / (‖a‖‖b‖)`.
- **Properties:** commutative, distributive over addition, `(αa)·b = α(a·b)`, `a·a = ‖a‖²`.
- **Sign:** `>0` acute, `=0` orthogonal, `<0` obtuse.
- **Cauchy–Schwarz:** `|a·b| ≤ ‖a‖‖b‖` (why cosine is in `[−1, 1]`).
- **Not scale-free:** doubling `a` doubles `a·b`. Cosine removes that.

**Worked example:** `a = (1, 2, 3)`, `b = (4, −5, 6)` → `4 − 10 + 18 = 12`. `‖a‖ = √14`, `‖b‖ = √77`, `cos θ = 12/√1078 ≈ 0.3655`, `θ ≈ 68.6°`.

### 3.4 Code

```python
import numpy as np

def dot_loop(a, b):
    if len(a) != len(b):
        raise ValueError("length mismatch")
    s = 0.0
    for x, y in zip(a, b):
        s += x * y
    return s

def dot_vec(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    return float(np.sum(a * b))

def angle_deg(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    c = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))   # clip: rounding can exceed ±1

a, b = np.array([1., 2., 3.]), np.array([4., -5., 6.])
assert np.isclose(dot_loop(a, b), a @ b) and np.isclose(dot_vec(a, b), np.dot(a, b))
print(round(angle_deg(a, b), 1))   # 68.6
```

Know the three spellings: `np.dot(a, b)`, `a @ b`, `np.inner(a, b)` agree for 1-D; they differ for higher dimensions (covered in Module 02).

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.arccos` of `1.0000000002` | `nan` | `np.clip(c, -1, 1)` |
| Zero vector in cosine | Division by zero, `nan` | Check norm; define or raise |
| Comparing raw dot products across different-length vectors | Longer vectors win unfairly | Normalize (cosine) |
| `np.dot` on `(n,1)` and `(n,1)` | Shape error | Use `.ravel()` or `a.T @ b` |
| `float32` overflow in huge dims | Inaccuracy | Accumulate in `float64` |

### 3.6 ML link

- **Linear model:** `ŷ = Xw + b` is a dot product per row (Module 14).
- **Attention (Stage 4C, 5C):** score `= q·k / √d`; the `√d` keeps magnitudes from growing with dimension `[VERIFY: statement of the variance argument in 4C-09]`.
- **Retrieval:** unit-normalized embeddings make dot product equal to cosine (Module 04).
- **Orthogonality:** uncorrelated or independent features contribute without overlap.

### 3.7 Lab (45–60 min)

1. Implement `dot_loop`, `dot_vec`, `angle_deg`; test on 100 random pairs against `np.dot` and `scipy.spatial.distance.cosine` (`cosine` returns *distance* `1 − cos θ`).
2. Show scaling: `a·b` vs `(10a)·b` vs cosine for both.
3. Make a 2-feature linear classifier by hand: pick `w`, draw the decision line `w·x = 0`, colour 200 random points by sign of `w·x`.

### Check yourself (Unit 3)

1. For unit vectors, what does the dot product equal?
2. If `a·b = 0` and neither is the zero vector, what is the angle?
3. Why can cosine similarity be preferred over dot product for text embeddings?

**Reference answers:** (1) `cos θ`. (2) 90°. (3) It ignores vector length, which may reflect frequency or document length rather than meaning.

---

## Unit 4 — Projection onto a vector (`03-…md`)

### 4.1 Why ML needs this

Projection splits a vector into the part explained by a direction and the part left over. Least squares regression is exactly this idea, applied to the target `y` and the span of the features (generalized in Module 14 and 4C-01). Gram–Schmidt, PCA's component scores, and "remove this direction" debiasing all start here.

### 4.2 Intuition

Shine a light perpendicular to `b` and see the shadow of `a` on the line through `b`. The shadow is the **projection**. What's left is the **residual**, which is perpendicular to `b`.

### 4.3 Mechanics

- **Scalar projection** (signed length of the shadow): `comp_b(a) = a·b / ‖b‖`.
- **Vector projection:** `proj_b(a) = (a·b / b·b) b`.
- **Residual:** `r = a − proj_b(a)`, with `r·b = 0` (orthogonality is the defining property).
- **Pythagoras:** `‖a‖² = ‖proj_b(a)‖² + ‖r‖²`.
- If `b` is a unit vector: `proj_b(a) = (a·b) b`.
- Projection is idempotent: projecting twice changes nothing.

**Worked example:** `a = (3, 4)`, `b = (1, 0)` → `proj = (3, 0)`, `r = (0, 4)`, `r·b = 0`. Then try `b = (1, 1)`: `proj = (3.5, 3.5)`, `r = (−0.5, 0.5)`, check `r·b = 0`.

### 4.4 Code

```python
import numpy as np

def project(a, b):
    """Project a onto the line spanned by b. Returns (proj, residual)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    bb = b @ b
    if np.isclose(bb, 0.0):
        raise ValueError("cannot project onto the zero vector")
    p = (a @ b / bb) * b
    return p, a - p

a, b = np.array([3., 4.]), np.array([1., 1.])
p, r = project(a, b)
assert np.allclose(r @ b, 0.0)                          # residual ⟂ b
assert np.isclose(a @ a, p @ p + r @ r)                 # Pythagoras
assert np.allclose(project(p, b)[0], p)                 # idempotent
```

**Bridge to regression (preview, 1 feature, no intercept):** the least-squares coefficient is the projection coefficient.

```python
rng = np.random.default_rng(0)
x = rng.normal(size=50)
y = 2.5 * x + rng.normal(scale=0.3, size=50)
w = (x @ y) / (x @ x)                                   # projection coefficient of y onto x
assert np.isclose(w, np.linalg.lstsq(x[:, None], y, rcond=None)[0][0])
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Projecting onto a zero or near-zero vector | Division blow-up | Check `b·b` with tolerance |
| Forgetting to divide by `b·b` when `b` is not unit | Wrong length | Test `r·b ≈ 0` |
| Confusing scalar and vector projection | Shape/scalar vs vector bug | Name variables `comp`, `proj` |
| Floating drift in repeated projections (Gram–Schmidt) | Loss of orthogonality | Re-orthogonalize or use QR (4C-01) |

### 4.6 ML link

- **Linear regression:** fitted values are the projection of `y` onto the column space; residuals are orthogonal to features (Module 14, 4C-01).
- **PCA:** component scores are projections onto principal directions (Module 03, 4C-01).
- **Debiasing embeddings:** subtracting the projection onto a "direction" removes that component `[JUDGEMENT: a common technique, with known limits]`.
- **Gradient components:** the part of a gradient along a direction is a projection.

### 4.7 Lab (45 min)

1. Implement `project`; plot `a`, `b`, projection, and residual in 2D with Matplotlib, drawing the right-angle marker.
2. Verify Pythagoras and idempotence on 100 random pairs.
3. Reproduce the single-feature regression above and plot residuals; confirm `x @ residual ≈ 0`.

### Check yourself (Unit 4)

1. Write `proj_b(a)` for unit `b`.
2. What property defines the residual?
3. In 1-D regression without an intercept, what is the slope in terms of dot products?

**Reference answers:** (1) `(a·b)b`. (2) It is orthogonal to `b`. (3) `(x·y)/(x·x)`.

---

## Unit 5 — Norms (L1, L2, L∞) and distance (`04-…md`)

### 5.1 Why ML needs this

Norms measure size. Distances are norms of differences. They define loss functions, penalties (weight decay is an L2 penalty; lasso is L1), nearest-neighbour search, gradient clipping, and convergence checks. Choosing the wrong norm changes model behaviour in ways that are visible in results.

### 5.2 Intuition: unit balls

The set `{x : ‖x‖ = 1}` has a different shape per norm in 2D: **L2** is a circle, **L1** a diamond, **L∞** a square. L1's corners lie on the axes, which is the geometric reason L1 penalties tend to give exact zeros (sparse solutions) while L2 shrinks all weights without zeroing them.

### 5.3 Mechanics

| Norm | Formula | Reads as | Behaviour |
|---|---|---|---|
| L1 | `‖x‖₁ = Σ|xᵢ|` | Manhattan / taxicab | Sparse-inducing, robust-ish to one large coordinate |
| L2 | `‖x‖₂ = √Σxᵢ²` | Euclidean length | Smooth, rotation-invariant, penalizes large entries heavily |
| L∞ | `‖x‖∞ = maxᵢ|xᵢ|` | Chebyshev | Worst-case coordinate |
| Lp | `(Σ|xᵢ|ᵖ)^{1/p}` | General family | `p<1` is not a norm (violates triangle inequality) |
| L0 | count of non-zeros | "Norm" | Not a true norm; proxy for sparsity |

**Norm axioms:** `‖x‖ ≥ 0` (zero only at `0`); `‖αx‖ = |α|‖x‖`; `‖x+y‖ ≤ ‖x‖+‖y‖`.
**Distance:** `d(x, y) = ‖x − y‖`; satisfies symmetry and the triangle inequality. **Ordering:** `‖x‖∞ ≤ ‖x‖₂ ≤ ‖x‖₁`, and `‖x‖₁ ≤ √d·‖x‖₂`, `‖x‖₂ ≤ √d·‖x‖∞`.
**Normalization:** `x/‖x‖₂` is a unit vector (needs `x ≠ 0`).

**Worked example:** `x = (3, −4, 0)` → `‖x‖₁ = 7`, `‖x‖₂ = 5`, `‖x‖∞ = 4`. Distance between `(1,1)` and `(4,5)`: L2 = 5, L1 = 7, L∞ = 4.

### 5.4 Code

```python
import numpy as np

def norm(x, p=2):
    x = np.asarray(x, float)
    if p == np.inf:
        return float(np.max(np.abs(x)))
    if p < 1:
        raise ValueError("p < 1 is not a norm")
    return float(np.sum(np.abs(x) ** p) ** (1.0 / p))

def distance(x, y, p=2):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape:
        raise ValueError(f"shape mismatch {x.shape} vs {y.shape}")
    return norm(x - y, p)

def normalize(x, eps=1e-12):
    n = norm(x)
    if n < eps:
        raise ValueError("cannot normalize a (near-)zero vector")
    return np.asarray(x, float) / n

x = np.array([3., -4., 0.])
for p in (1, 2, np.inf):
    assert np.isclose(norm(x, p), np.linalg.norm(x, ord=p))
assert np.isclose(distance([1, 1], [4, 5]), 5.0)
```

**Batch distances (shape discipline):**

```python
def pairwise_l2(A, B):
    """A: (n, d), B: (m, d) -> (n, m) Euclidean distances, no Python loops."""
    A2 = (A ** 2).sum(axis=1)[:, None]          # (n, 1)
    B2 = (B ** 2).sum(axis=1)[None, :]          # (1, m)
    D2 = A2 + B2 - 2.0 * A @ B.T                # ‖a‖² + ‖b‖² − 2a·b
    return np.sqrt(np.maximum(D2, 0.0))         # clip tiny negatives from rounding

rng = np.random.default_rng(0)
A, B = rng.normal(size=(5, 3)), rng.normal(size=(4, 3))
from scipy.spatial.distance import cdist
assert np.allclose(pairwise_l2(A, B), cdist(A, B), atol=1e-6)
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.sqrt` of tiny negative from `‖a‖²+‖b‖²−2a·b` | `nan` | `np.maximum(D2, 0)` |
| Features on different scales | One feature dominates distance | Standardize first |
| Normalizing a zero vector | `nan` | Epsilon check |
| Using `p < 1` as a "norm" | Triangle inequality fails | Reject or name it a quasi-norm |
| Confusing `np.linalg.norm` on matrices (Frobenius by default) | Unexpected value | Pass `axis=` for row-wise norms |
| Computing L2 of huge vectors naively | Overflow/underflow | Scale by max first, or use `np.linalg.norm` |

### 5.6 ML link

- **Regularization (Module 14):** ridge adds `λ‖w‖₂²`; lasso adds `λ‖w‖₁`. Use the unit-ball picture to explain sparsity.
- **k-NN and clustering (Stage 5A-09):** distance choice and scaling decide neighbours.
- **Gradient clipping (Stage 5C):** rescale gradient if `‖g‖₂ > c`.
- **Convergence checks (Module 08):** stop when `‖∇f‖₂ < tol`.
- **Adversarial robustness:** perturbation budgets are defined in L∞ or L2 balls `[JUDGEMENT: common convention in the literature]`.

### 5.7 Lab (60 min)

1. Implement `norm`, `distance`, `normalize`, `pairwise_l2`; test against `np.linalg.norm` and `cdist`.
2. Plot unit balls for `p ∈ {0.5, 1, 2, 4, ∞}` in 2D; note that `p = 0.5` is non-convex.
3. Experiment: on a dataset with one feature in thousands and one in 0–1, show k-NN neighbours change after standardization.
4. Gradient clipping: write `clip_by_norm(g, c)` and verify `‖result‖ ≤ c` and direction unchanged.

```python
def clip_by_norm(g, c):
    g = np.asarray(g, float)
    n = np.linalg.norm(g)
    return g if n <= c else g * (c / n)
```

### Check yourself (Unit 5)

1. Compute L1, L2, L∞ of `(−2, 1, 2)`.
2. Why does L1 produce sparser solutions than L2?
3. Why should features be standardized before a Euclidean k-NN?

**Reference answers:** (1) 5, 3, 2. (2) The L1 ball has corners on the axes, so the optimum of a loss plus L1 constraint often lands on a corner where some coordinates are zero. (3) Otherwise large-scale features dominate the distance.

---

## Unit 6 — Linear combinations, span, linear independence (`05-…md`)

### 6.1 Why ML needs this

A linear model's output is a linear combination of features. Whether features are independent determines whether weights are uniquely defined. Perfectly collinear features (e.g., a dummy-variable trap, or `weight_kg` and `weight_lb`) make regression ill-posed. Embedding dimensions, bases, and low-rank ideas (Module 03) all rely on span and independence.

### 6.2 Intuition

- **Linear combination:** mix vectors with scalar weights: `c₁v₁ + … + c_kv_k`.
- **Span:** all reachable mixtures. Two non-parallel vectors in 3D span a plane; adding a third that lies in that plane adds nothing.
- **Independent:** none of the vectors is reachable from the others. Dependent sets contain redundancy.

### 6.3 Mechanics

- `span{v₁,…,v_k} = { Σ cᵢvᵢ : cᵢ ∈ ℝ }`.
- **Independence:** `Σ cᵢvᵢ = 0` only when all `cᵢ = 0`. Dependent otherwise.
- **Test with a matrix:** stack vectors as columns of `V: (d, k)`. Independent ⇔ `rank(V) = k`. More than `d` vectors in `ℝᵈ` are always dependent.
- **Basis:** independent set that spans a space; its size is the dimension. Standard basis `e₁…e_d`.
- **Coordinates:** each vector in the span has *unique* coefficients if and only if the generators are independent.
- **Is `b` in the span?** Solve `Vc = b` (least squares plus a residual check; Module 02 teaches the full solver).

Numerical rank uses a **tolerance**: singular values below `tol` count as zero. This is what `np.linalg.matrix_rank` does `[VERIFY: default tolerance rule in the installed NumPy]`.

### 6.4 Code

```python
import numpy as np

def is_independent(vectors, tol=None):
    V = np.column_stack([np.asarray(v, float) for v in vectors])   # (d, k)
    return np.linalg.matrix_rank(V, tol=tol) == V.shape[1]

def in_span(b, vectors, atol=1e-8):
    V = np.column_stack([np.asarray(v, float) for v in vectors])
    c, *_ = np.linalg.lstsq(V, np.asarray(b, float), rcond=None)
    return bool(np.allclose(V @ c, b, atol=atol)), c

v1, v2, v3 = [1, 0, 0], [0, 1, 0], [1, 1, 0]
assert is_independent([v1, v2])
assert not is_independent([v1, v2, v3])             # v3 = v1 + v2
ok, c = in_span([2, 3, 0], [v1, v2])
assert ok and np.allclose(c, [2, 3])
assert not in_span([0, 0, 1], [v1, v2])[0]
```

**Collinear features break regression (hands-on):**

```python
rng = np.random.default_rng(0)
n = 100
kg = rng.normal(70, 10, n)
X = np.column_stack([kg, kg * 2.20462])              # same information twice
print(np.linalg.matrix_rank(X))                      # 1, not 2
print(np.linalg.cond(X))                             # enormous → ill-conditioned
```

Then add one noise-perturbed copy (`kg*2.2 + rng.normal(0, 1e-6, n)`) and watch rank return to 2 while `cond` stays huge: *full rank is not the same as numerically safe*.

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Treating exact rank as a boolean on float data | Near-dependence missed | Check `cond(V)` and singular values |
| Stacking vectors as rows when the test expects columns | Wrong answer | `column_stack`; assert shape |
| More vectors than dimension | Always dependent | Check `k ≤ d` first |
| One-hot encoding with all categories plus intercept | Exact dependence (dummy trap) | Drop one level, or regularize |
| Using `det` to test independence | Fails for non-square, unstable | Use rank / SVD |

### 6.6 ML link

- **Feature engineering:** redundant features add no information and destabilize closed-form fits (Module 14: normal equation).
- **Rank and capacity:** low-rank structure underlies PCA and low-rank adapters (Module 03, 4C-01) `[JUDGEMENT]`.
- **Embeddings:** the span of a set of embedding directions is the "subspace" a concept lives in.
- **Interpretation:** with collinear features, individual coefficients are not interpretable even if predictions are fine.

### 6.7 Lab (60 min)

1. Implement `is_independent`, `in_span`; add a tolerance parameter and test on near-dependent vectors.
2. Build a design matrix with a one-hot dummy trap; show rank deficiency and fix it two ways (drop one column; add ridge `λI` preview from Module 14).
3. Plot in 3D (or 2D projections) the span of two vectors and a point inside vs outside it.

### Check yourself (Unit 6)

1. Are `(1,2)`, `(2,4)` independent? Do they span ℝ²?
2. Can 4 vectors in ℝ³ be independent?
3. What does it mean for regression if two columns of `X` are identical?

**Reference answers:** (1) No; they span only a line. (2) No, at most 3. (3) The weights are not unique; the normal equation matrix is singular.

---

## Unit 7 — Practice question bank (`practice-questions.md`)

### 7.1 Structure

About 40 items in four tiers, each with a hidden answer and a one-line rationale. Mix of hand calculation, "predict the shape", code, debugging, and ML judgement. Tag each item `L1` (recall), `L2` (apply), `L3` (analyze/debug), `L4` (design). Aim for roughly 10 per tier.

### 7.2 Template for each item

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + short why + code if relevant>
</details>
```

### 7.3 Sample items (seed the file with these)

**Q1 [L1] Shapes.** `x = np.zeros((5,))`, `y = np.zeros((5, 1))`. What is `(x + y).shape`? → `(5, 5)` by broadcasting; this is a classic silent bug.

**Q2 [L2] Dot.** Compute `(2, −1, 3)·(4, 0, −2)`. → `8 + 0 − 6 = 2`.

**Q3 [L2] Angle.** Vectors `(1, 0)` and `(1, 1)`: angle? → `cos θ = 1/√2`, `θ = 45°`.

**Q4 [L2] Projection.** Project `(2, 3)` onto `(0, 5)`. → `(0, 3)`; residual `(2, 0)`.

**Q5 [L2] Norms.** `x = (1, −2, 2)`: L1, L2, L∞? → 5, 3, 2.

**Q6 [L3] Debug.** `cos = a @ b / (a.norm() * b.norm())` raises `AttributeError`. → NumPy arrays have no `.norm()`; use `np.linalg.norm(a)`.

**Q7 [L3] Debug.** `np.arccos(a@b/(‖a‖‖b‖))` occasionally returns `nan` for identical vectors. → Rounding gives a value just above 1; clip to `[-1, 1]`.

**Q8 [L3] Distance trick.** Your `pairwise_l2` returns `nan` for some pairs. Why? → `‖a‖²+‖b‖²−2a·b` can be slightly negative from rounding; clamp at 0 before `sqrt`.

**Q9 [L3] Independence.** `rank(V) = 3` yet `cond(V) = 1e15`. Safe to invert? → No, effectively singular in float; use `lstsq`, regularize, or drop features.

**Q10 [L4] Design.** Choose a similarity for a product-search embedding index and justify. → Normalize embeddings; use cosine (equal to dot on unit vectors) so length does not bias ranking; confirm with a retrieval metric on labelled queries (Stage 5).

**Q11 [L4] Penalty.** You need a model that drops uninformative features. L1 or L2 penalty? → L1 (sparse); caveat: with correlated features, which one survives is unstable.

**Q12 [L4] Scaling.** A k-NN model uses `age` (0–100) and `income` (0–200,000). Predict and fix the issue. → Income dominates Euclidean distance; standardize or use a scale-aware metric.

### 7.4 Required coverage matrix (use when writing the remaining items)

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Arrays and shapes | 3 | 3 | 2 | 1 |
| Dot product / angle | 2 | 3 | 2 | 1 |
| Projection | 1 | 3 | 2 | 1 |
| Norms / distance | 2 | 3 | 2 | 2 |
| Span / independence | 2 | 2 | 2 | 1 |

### Check yourself (Unit 7)

1. Why include "predict the shape" items at every tier?
2. Which items must include runnable code?

**Reference answers:** (1) Shape errors are the most common production bug in vectorized code. (2) All L3 debug items and any item whose answer depends on floating-point behaviour.

---

## Unit 8 — Project index (`Projects/README.md`)

### 8.1 Purpose

Describe the two projects, their order, what each proves, and the shared rubric.

### 8.2 Catalogue

| # | Project | Proves | Depends on lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Vector operations library in NumPy | Correct, tested, shape-safe numerics | 1–5 | 3–4 h |
| 2 | Geometry of dot product explorer | Geometric intuition, visualization, interactive reasoning | 2–4 | 3–4 h |

Do project 1 first; project 2 reuses its functions. Both feed the Stage 4B notebook library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`) as `mlmath/vectors.py` and a notebook `01_vectors.ipynb`.

### 8.3 Rubric (100 points; pass = 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs NumPy/SciPy reference | 30 |
| Failure-mode handling (zero vectors, shape mismatch, NaN/inf) | 15 |
| Reproducibility (seeded, pinned, clean venv) | 15 |
| Explanation quality (what each plot/result shows and why it matters for ML) | 15 |
| Code quality (types, docstrings with shapes) | 15 |
| ML connection paragraph | 10 |

### 8.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 8)

1. Which project depends on the other?
2. Where do the project outputs go afterwards?

**Reference answers:** (1) Project 2 reuses Project 1. (2) Into `mlmath/vectors.py` and `01_vectors.ipynb` of the stage library.

---

## Unit 9 — Project: Vector operations library in NumPy (`Projects/01-…md`)

### 9.1 Brief

Build `vecops`, a small package providing validated, vectorized vector primitives with both loop and NumPy implementations, a test-suite against references, and a benchmark.

**Industry framing:** teams keep thin, tested numerics helpers so shape and zero-vector bugs are handled once rather than in every notebook.

### 9.2 Requirements

| # | Function | Spec |
|---|---|---|
| R1 | `add`, `sub`, `scale` | Validate shapes; support `(d,)` and `(n, d)` batches |
| R2 | `dot(a, b)` | 1-D → scalar; `(n,d)·(n,d)` → row-wise `(n,)` |
| R3 | `norm(x, p)` | `p ∈ {1, 2, inf}` and general `p ≥ 1`; `axis` support |
| R4 | `distance(x, y, p)` | Via `norm`; broadcast-aware |
| R5 | `normalize(x)` | Raise on zero vector; optional `eps` |
| R6 | `cosine(a, b)` | Safe with zero vectors (documented behaviour); clipped to `[-1, 1]` |
| R7 | `angle(a, b, degrees=True)` | Uses `cosine` |
| R8 | `project(a, b)` | Returns `(proj, residual)`; batch-aware |
| R9 | `is_independent`, `in_span` | Tolerance parameter |
| R10 | `pairwise_l2(A, B)`, `pairwise_cosine(A, B)` | No Python loops |

### 9.3 Layout and starter

```
vecops/
├── pyproject.toml  requirements.txt  README.md
├── src/vecops/{__init__,core,geometry,independence,pairwise}.py
├── tests/{test_core,test_geometry,test_independence,test_pairwise}.py
├── notebooks/01_vectors.ipynb
└── bench/bench_loops_vs_numpy.py
```

```python
# src/vecops/core.py
from __future__ import annotations
import numpy as np
from numpy.typing import ArrayLike, NDArray

def _as_float(x: ArrayLike) -> NDArray[np.float64]:
    return np.asarray(x, dtype=np.float64)

def dot(a: ArrayLike, b: ArrayLike) -> NDArray[np.float64] | float:
    """a, b: (d,) -> scalar, or (n, d) -> (n,)."""
    a, b = _as_float(a), _as_float(b)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    out = np.sum(a * b, axis=-1)
    return float(out) if out.ndim == 0 else out

def norm(x: ArrayLike, p: float = 2, axis: int = -1):
    x = _as_float(x)
    if p == np.inf:
        return np.max(np.abs(x), axis=axis)
    if p < 1:
        raise ValueError("p must be >= 1")
    return np.sum(np.abs(x) ** p, axis=axis) ** (1.0 / p)

def cosine(a: ArrayLike, b: ArrayLike, eps: float = 1e-12):
    a, b = _as_float(a), _as_float(b)
    na, nb = norm(a), norm(b)
    denom = np.maximum(na * nb, eps)             # zero vector -> cosine 0.0 (documented)
    return np.clip(dot(a, b) / denom, -1.0, 1.0)
```

```python
# tests/test_core.py
import numpy as np, pytest
from scipy.spatial.distance import cosine as sp_cos
from vecops.core import dot, norm, cosine

rng = np.random.default_rng(0)

@pytest.mark.parametrize("trial", range(100))
def test_dot_and_norm_match_numpy(trial):
    a, b = rng.normal(size=8), rng.normal(size=8)
    assert np.isclose(dot(a, b), np.dot(a, b))
    for p in (1, 2, np.inf):
        assert np.isclose(norm(a, p), np.linalg.norm(a, ord=p))
    assert np.isclose(cosine(a, b), 1 - sp_cos(a, b))

def test_shape_mismatch_raises():
    with pytest.raises(ValueError):
        dot([1, 2, 3], [1, 2])

def test_zero_vector_cosine_is_finite():
    assert cosine([0, 0], [1, 2]) == 0.0

def test_batch_dot_shape():
    assert dot(np.ones((5, 3)), np.ones((5, 3))).shape == (5,)
```

### 9.4 Milestones with acceptance tests

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R5 plus tests | 100 random cases match NumPy; shape errors raise `ValueError` |
| M2 | R6–R8 | Orthogonality `residual·b ≈ 0` and Pythagoras hold on 100 random pairs |
| M3 | R9 | Exact duplicates, near duplicates (`1e-9` noise), and `k > d` classified as documented |
| M4 | R10 | Matches `scipy.spatial.distance.cdist` for `euclidean` and `cosine` metrics, `atol=1e-6` |
| M5 | Benchmark + notebook | Loop vs vectorized timing table from *your* machine; notebook runs top to bottom |

### 9.5 Benchmark requirement

Time loop vs NumPy for `d ∈ {10, 1e3, 1e6}` and `n` batch sizes; record machine, Python and NumPy versions with the results. Do not claim a speed-up factor you did not measure.

### 9.6 Failure-mode table (must be in the README)

At least 8 rows: function, breaking input, behaviour chosen, test that guards it. Seed with: zero vector in `normalize`, `p < 1`, `float32` input, `(n,1)` vs `(n,)`, near-dependent vectors, overflow-scale inputs, empty vectors, NaN input.

### 9.7 Stretch goals

1. `hypothesis` property tests: `dot(a,b) == dot(b,a)`, triangle inequality for all norms, Cauchy–Schwarz.
2. Add `float32` mode and quantify error against `float64`.
3. Add a `numba` or `einsum` variant and compare `[VERIFY: numba availability for your Python version]`.
4. `mypy --strict` on `src/`.

### 9.8 ML connection (README paragraph prompt)

Name where each of dot, norm, cosine, projection appears in a real model: linear layer, weight decay, retrieval, regression residual.

### Check yourself (Unit 9)

1. Why does `cosine` clamp its denominator and clip its output?
2. Which test proves the projection is correct?

**Reference answers:** (1) To stay finite for zero vectors and avoid `nan` from rounding past ±1. (2) Residual orthogonality plus Pythagoras, not just comparing numbers to one example.

---

## Unit 10 — Project: Geometry of dot product explorer (`Projects/02-…md`)

### 10.1 Brief

Build an explorer (Matplotlib notebook with `ipywidgets` sliders, or a static script generating figure grids) that makes the dot product, angle, projection, and norm-ball geometry visible, then use it to answer a set of ML-flavoured questions.

**Industry framing:** diagnostic visualizations are how engineers build intuition about embeddings and loss geometry before trusting metrics.

### 10.2 Required views

| # | View | Shows |
|---|---|---|
| V1 | Two draggable/parameterized vectors `a`, `b` in 2D | `a·b`, `‖a‖`, `‖b‖`, `cos θ`, `θ` live |
| V2 | Projection panel | Shadow of `a` on `b`, residual, right-angle marker |
| V3 | Sign map | Heatmap of `a·x` over a grid of `x`; zero contour = decision boundary |
| V4 | Unit balls | L1, L2, L∞ (and `p=0.5`, `p=4`) in one figure |
| V5 | Scale experiment | Dot vs cosine as `‖a‖` grows |
| V6 | High-dim angles | Histogram of angles between random vectors for `d ∈ {2, 10, 100, 1000}` |

### 10.3 Starter code

```python
import numpy as np
import matplotlib.pyplot as plt

def draw_projection(a, b, ax=None):
    ax = ax or plt.gca()
    b_hat = b / np.linalg.norm(b)
    p = (a @ b_hat) * b_hat
    r = a - p
    for v, c, lab in ((a, "C0", "a"), (b, "C1", "b"), (p, "C2", "proj"), (r, "C3", "residual")):
        ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=c))
        ax.text(*v, lab, color=c)
    ax.plot([a[0], p[0]], [a[1], p[1]], "k:", lw=1)
    lim = 1.3 * max(np.abs(np.r_[a, b]).max(), 1)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.grid(True)
    ax.set_title(f"a·b={a@b:.2f}   cosθ={a@b/np.linalg.norm(a)/np.linalg.norm(b):.2f}")

def high_dim_angles(d, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    U = rng.normal(size=(n, d)); V = rng.normal(size=(n, d))
    cos = np.sum(U * V, axis=1) / (np.linalg.norm(U, axis=1) * np.linalg.norm(V, axis=1))
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))

fig, axes = plt.subplots(1, 4, figsize=(14, 3), sharey=True)
for ax, d in zip(axes, (2, 10, 100, 1000)):
    ax.hist(high_dim_angles(d), bins=40); ax.set_title(f"d={d}"); ax.set_xlabel("angle (deg)")
plt.tight_layout()
```

Expected observation `[VERIFY by running]`: as `d` grows, random-vector angles concentrate near 90°. This is the first glimpse of the high-dimensional geometry developed in Module 04.

### 10.4 Questions the write-up must answer (with evidence from the views)

1. When is `a·b` negative, and what does that mean for a linear classifier's decision?
2. Why does doubling `‖a‖` change dot product but not cosine? Which ML tasks need which?
3. Where do the L1 and L2 balls touch a tilted line `w·x = c` first, and what does this predict about sparsity?
4. What does the high-dimension angle histogram imply for "nearest neighbour" in 1,000-D data?
5. Pick one embedding-search setting and justify dot vs cosine using your views.

### 10.5 Milestones

| Step | Work | Acceptance |
|---|---|---|
| M1 | V1–V2 | Numbers on screen equal `vecops` functions for 20 random inputs |
| M2 | V3–V4 | Boundary contour is at `a·x = 0` within pixel tolerance; unit-ball norms equal 1 on sampled points (test) |
| M3 | V5–V6 | Seeded, reproducible figures saved to `results/` |
| M4 | Write-up | Answers to all five questions, each citing a figure |

### 10.6 Stretch goals

1. Constrained-optimum picture: minimize `‖w - w0‖²` subject to `‖w‖₁ ≤ t` vs `‖w‖₂ ≤ t`; show where the solution lands.
2. Real embeddings: load any small pretrained word-vector file you have locally and repeat V6 on real vectors, noting the difference from random ones `[VERIFY: licence and file availability; do not assume a download]`.
3. 3D version with span of two vectors as a plane and a point inside vs outside.

### 10.7 Evaluation

Shared rubric (Unit 8). Extra bar: every figure has labelled axes and a one-sentence takeaway; no claim in the write-up is without a figure or a number from your own runs.

### Check yourself (Unit 10)

1. In the angle experiment, what concentrates near 90° and why does it matter?
2. Why should figures be seeded?

**Reference answers:** (1) Random high-dimensional vectors are almost orthogonal; this is why raw distances lose contrast as dimension grows. (2) So results are reproducible and reviewable.

---

## Appendix A — Open items

1. `[VERIFY]` Lesson and project counts against the tree (5 lessons, 2 projects, 10 files in the module).
2. `[VERIFY]` Expected angle concentration (run Unit 10 starter before publishing the claim).
3. `[VERIFY]` Cross-references to 4C-01 and 4C-09 lesson content.
4. `[VERIFY]` Library versions and `matrix_rank` tolerance behaviour in the pinned NumPy.

## Appendix B — Authoring checklist

- [ ] Each lesson file has the six beats, worked example, code with assertions, failure-mode table, ML link, lab, and check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix and has runnable code for L3 debug items.
- [ ] Both projects have tests, a failure-mode table, and seeded outputs.
- [ ] No timing or speed claim appears without the measurement that produced it.
