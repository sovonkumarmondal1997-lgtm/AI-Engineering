# SYLLABUS — 07-Multivariable-Calculus-and-Gradients (S4B-07)

**Stage 4B — Mathematics for Machine Learning · Module 07 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SymPy for symbolic cross-checks; Matplotlib and pytest where stated). This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Functions of several variables and level sets | `01-functions-of-several-variables-and-level-sets.md` | Beginner |
| 3 | Partial derivatives | `02-partial-derivatives.md` | Beginner → Intermediate |
| 4 | Gradients and the direction of steepest ascent | `03-gradients-and-the-direction-of-steepest-ascent.md` | Intermediate |
| 5 | Computational graphs and backpropagation by hand | `04-computational-graphs-and-backpropagation-by-hand.md` | Intermediate → Advanced |
| 6 | Practice question bank | `practice-questions.md` | All levels |
| 7 | Project index | `Projects/README.md` | Intermediate |
| 8 | Project: gradient field and contour plotter | `Projects/01-gradient-field-and-contour-plotter.md` | Intermediate → Advanced |
| 9 | Project: backpropagation by hand on a tiny network | `Projects/02-backpropagation-by-hand-on-a-tiny-network.md` | Advanced |

**Prerequisites:** Module 05 (derivatives, chain rule, sigmoid/tanh/ReLU derivatives, gradient checking, `Dual`), Module 01 (dot product, norms, angle between vectors), Module 02 (matrix products, shapes, transpose), Module 03 Lesson 2 (eigenvalues, used for ellipse axes). **Plan slot:** weeks 8–9 of `../00-Stage-4-Overview/learning-plan.md`. **Checkpoints:** (from the stage plan) gradient checker passes on the tiny network; you can run backprop by hand and match autodiff.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link. Shapes are written in comments throughout.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

A loss function takes *many* parameters and returns *one* number. To train, you need to know how that number changes with every parameter at once. The vector of those sensitivities is the **gradient**, and backpropagation is the chain rule applied to a computational graph so the whole gradient costs about one extra pass. This module is where Module 05's single-variable machinery becomes the engine of every optimizer in Module 08 and every training loop in Stage 5C.

### 1.2 Outcomes

1. Read a function `f(x₁, …, xₙ)` as a surface or a set of level sets, and sketch/plot contours for a bowl, saddle, valley, and a loss surface.
2. Compute partial derivatives by hand, symbolically, and numerically, and check them against each other.
3. Define the gradient, prove numerically that it points in the direction of steepest ascent and is perpendicular to level sets, and use it for first-order approximation and a descent step.
4. Write the gradients of the linear, quadratic, least-squares, and logistic losses in vector form.
5. Draw a computational graph, run a forward and a backward pass by hand, and explain why gradients from different paths add.
6. Implement a scalar reverse-mode autodiff class and a vectorized backward pass, and verify both against finite differences.
7. Train a tiny network (XOR) with hand-derived gradients, and detect injected backprop bugs.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Functions of several variables and level sets | Loss surfaces, decision boundaries, conditioning | Contour/level-set tools |
| 2 | Partial derivatives | Sensitivity of loss to one weight | Partials: hand, SymPy, numeric |
| 3 | Gradients and steepest ascent | Gradient descent, linear/logistic gradients | Direction and orthogonality experiments |
| 4 | Computational graphs and backprop | Backprop, autodiff, layer gradients | `Value` class, vectorized layer backward |

### 1.4 Concept map

```
f: ℝⁿ → ℝ ──► surface / level sets ──► conditioning (ellipse shape)
   │
   ├─► partial derivatives ∂f/∂xᵢ (others frozen; Module 05 per coordinate)
   │         │
   │         └─► gradient ∇f = (∂f/∂x₁ … ∂f/∂xₙ)
   │                 ├─ D_u f = ∇f·u = ‖∇f‖cosθ   (Module 01 dot product)  → steepest ascent = ∇f
   │                 ├─ ∇f ⟂ level sets
   │                 ├─ f(x+δ) ≈ f(x) + ∇f·δ      → gradient descent x ← x − η∇f   (Module 08)
   │                 └─ linear / quadratic / least-squares / logistic gradients
   └─► computational graph ──► forward pass ──► backward pass (chain rule; fan-out sums)
                                  └─► autodiff (reverse mode) ──► backprop in networks (Stage 5C, 4C-07)
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "sympy>=1.12" matplotlib pytest
```

Rules for every lab: **derive by hand, then check numerically, then check symbolically**; always write shapes in comments (`X: (n, d)`, `w: (d,)`, `g: (d,)`); gradient shape must equal parameter shape; test with Module 05's central-difference checker at 10–20 random points; seed randomness; use `float64` for checks; for plots, use `matplotlib.use("Agg")` in scripts so they run headless.

### 1.6 Checkpoint

Your gradient checker reports relative error `< 1e-6` for every gradient in this module, including the tiny network's four parameter arrays, and you can show on paper and in code that the backward pass of `y = tanh(w₁x₁ + w₂x₂ + b)` matches finite differences.

### Check yourself (Unit 1)

1. What is the shape of the gradient of a loss with respect to a weight matrix `W: (d, k)`?
2. Why does this module come before Optimization Fundamentals?

**Reference answers:** (1) Also `(d, k)`: a gradient always has the shape of the parameter. (2) Every optimizer consumes gradients; Module 08 assumes you can compute and verify them.

---

## Unit 2 — Functions of several variables and level sets (`01-…md`)

### 2.1 Why ML needs this

A model's loss is a function of all its parameters: `L(w₁, …, wₙ)`. Understanding that function as a **landscape** (valleys, ridges, plateaus, saddles) explains why some problems train easily and others crawl, and why the learning rate must be chosen with the landscape's *shape* in mind. Level sets also describe decision boundaries (`w·x + b = 0`) and regularizer shapes (L1 diamond, L2 circle from Module 01).

### 2.2 Intuition

- `f(x, y)` assigns a height to each point of the plane: a **surface**.
- A **level set** (contour) `{(x, y) : f(x, y) = c}` is a horizontal slice of that surface at height `c`. Closely spaced contours mean a steep slope; widely spaced contours mean a flat region.
- In `n` dimensions you cannot draw the surface, but level sets and 1-D slices still work.

### 2.3 Mechanics

- **Function of several variables:** `f: ℝⁿ → ℝ`. A vector-valued function `F: ℝⁿ → ℝᵐ` outputs `m` numbers (a layer); Jacobians come in 4C-02.
- **Standard landscapes** to know by sight:

| Function | Shape | Contours | Why it matters |
|---|---|---|---|
| `x² + y²` | Round bowl | Circles | Easiest case; GD converges directly |
| `½(x² + κy²)`, `κ ≫ 1` | Narrow valley | Long thin ellipses (axis ratio `√κ`) | **Ill-conditioning**: slow, zig-zagging GD (Module 08) |
| `x² − y²` | Saddle | Hyperbolas | Critical point that is neither min nor max |
| `(1−x)² + 100(y−x²)²` (Rosenbrock) | Curved narrow valley | Banana-shaped | Classic non-convex optimizer test |
| `(x²+y−11)² + (x+y²−7)²` (Himmelblau) | Four minima | Four basins | Initialization dependence |
| `w·x` (linear) | Plane/ramp | Parallel straight lines/hyperplanes | Linear models; decision boundary at `w·x = 0` |
| Logistic loss over `(w₁, w₂)` | Convex, flat tails | Smooth bowl with plateaus | Saturation, separable data |

- **Level sets of quadratics:** `f(x) = ½ xᵀAx` (A symmetric positive definite): `{f = c}` is an ellipsoid whose semi-axes are `√(2c/λᵢ)` along the eigenvectors of `A` (Module 03). The ratio of longest to shortest axis is `√(λ_max/λ_min) = √κ`.
- **Level sets of linear functions** are hyperplanes `w·x = c` perpendicular to `w` (Module 01): a **linear classifier's decision boundary is a level set**.
- **Level sets of norms** are the unit balls of Module 01 (diamond for L1, circle for L2, square for L∞).
- **Slices:** restrict `f` to a line `x(α) = x₀ + α d`, giving a 1-D function `φ(α) = f(x₀ + αd)` you can plot and differentiate with Module 05 tools. This is how people visualize high-dimensional loss landscapes `[VERIFY: normalization conventions in the loss-landscape literature]`.
- **Vectorized evaluation:** build a grid with `np.meshgrid(xs, ys, indexing="xy")` (default) so `Z[i, j] = f(xs[j], ys[i])`; mixing `indexing` conventions is the most common plotting bug.
- **Domain and range matter:** `log` needs positive arguments; saturating functions have flat tails.

**Worked example:** `f(x, y) = x² + 4y²`. Level set `f = 4` is the ellipse `x²/4 + y² = 1`, semi-axes `2` and `1`. Along `y = 0` the function is `x²` (curvature 2); along `x = 0` it is `4y²` (curvature 8): *the landscape is 4× steeper in `y` than in `x`*.

### 2.4 Code

```python
import numpy as np

# --- grid evaluation: be explicit about indexing
xs, ys = np.linspace(-3, 3, 7), np.linspace(-2, 2, 5)
X, Y = np.meshgrid(xs, ys)                         # default indexing="xy": X, Y have shape (len(ys), len(xs))
f = lambda x, y: x ** 2 + 4 * y ** 2
Z = f(X, Y); assert Z.shape == (5, 7) and np.isclose(Z[1, 2], f(xs[2], ys[1]))   # Z[i, j] = f(xs[j], ys[i])

# --- a catalogue of landscapes (also reused by Project 1)
LANDSCAPES = {
    "bowl":       lambda x, y: x ** 2 + y ** 2,
    "ill":        lambda x, y: 0.5 * (x ** 2 + 25 * y ** 2),
    "saddle":     lambda x, y: x ** 2 - y ** 2,
    "rosenbrock": lambda x, y: (1 - x) ** 2 + 100 * (y - x ** 2) ** 2,
    "himmelblau": lambda x, y: (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2,
}

# --- level sets of a quadratic are ellipses with semi-axes sqrt(2c / λ_i)
A = np.array([[1.0, 0.0], [0.0, 100.0]])
lam, V = np.linalg.eigh(A)
theta = np.linspace(0, 2 * np.pi, 20_000); U = np.vstack([np.cos(theta), np.sin(theta)])   # unit directions (2, N)
r = np.sqrt(2.0 / np.einsum("in,ij,jn->n", U, A, U))          # radius where ½ rᵀ... = 1 along each direction
print("axis ratio:", r.max() / r.min(), " sqrt(λmax/λmin) =", np.sqrt(lam.max() / lam.min()))
assert np.isclose(r.max() / r.min(), np.sqrt(lam.max() / lam.min()), rtol=1e-6)
pts = U * r                                                   # points on the level set ½ xᵀAx = 1
assert np.allclose(0.5 * np.einsum("in,ij,jn->n", pts, A, pts), 1.0)

# --- a linear function's level sets are hyperplanes ⟂ w
w = np.array([2.0, -1.0, 0.5]); c = 3.0
rng = np.random.default_rng(0)
x0 = c * w / (w @ w)                                          # a point on {w·x = c}
for _ in range(20):
    d = rng.normal(size=3); d -= (d @ w) / (w @ w) * w        # direction ⟂ w (Module 01 projection)
    assert np.isclose(w @ (x0 + 1.7 * d), c)                  # staying in the plane keeps w·x = c

# --- 1-D slice through a high-dimensional function
def rosenbrock_nd(x): return np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)
x0 = rng.normal(size=50); d = rng.normal(size=50); d /= np.linalg.norm(d)
alphas = np.linspace(-1, 1, 201)
phi = np.array([rosenbrock_nd(x0 + a * d) for a in alphas])  # φ(α) = f(x0 + α d), a plottable 1-D function
print(phi.min(), phi[100])

# --- contour plot (Matplotlib; run headless)
# import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
# xs, ys = np.linspace(-2, 2, 400), np.linspace(-1, 3, 400); X, Y = np.meshgrid(xs, ys)
# plt.contour(X, Y, LANDSCAPES["rosenbrock"](X, Y), levels=np.logspace(-1, 3, 12)); plt.gca().set_aspect("equal")
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Mixing `meshgrid` indexing (`"xy"` vs `"ij"`) | Transposed contour plot, wrong axes | Assert `Z[i, j] == f(xs[j], ys[i])` for the chosen convention |
| Unequal axis scaling in plots | Ellipses look like circles; conditioning hidden | `set_aspect("equal")` |
| Linear contour levels for a function with huge range | Nothing visible (Rosenbrock) | `np.logspace` levels |
| Evaluating outside the domain (`log` of negatives) | `nan` regions | Mask or restrict the grid |
| Interpreting a 2-D slice as the whole high-dimensional landscape | Overconfident conclusions about "convexity" | State that the slice is one direction through one point |
| Equating small `‖∇f‖` with a minimum | Saddles and plateaus also have small gradients | Check curvature (Module 05 Lesson 7; Hessian in 4C-02) |
| Treating feature scales as irrelevant | Valleys become needle-thin | Standardize (Module 14); check `κ` |

### 2.6 ML link

- **Loss landscape:** every training run is a path over `L(θ)`; the picture explains learning-rate sensitivity and slow convergence (Module 08).
- **Conditioning:** the ellipse axis ratio `√κ` governs GD speed; feature scaling shapes it (Module 14).
- **Decision boundary = level set** `w·x + b = 0` of the score; logistic regression's boundary is the `0.5`-probability contour (Module 14).
- **Regularizer geometry** (Module 01 Lesson 4, Module 14): L1 vs L2 constraint sets as level sets.
- **Saddles and multiple minima** in non-convex networks (4C-03).

### 2.7 Lab (75 min)

1. Plot contours (log-spaced levels) and a 3-D surface for the five landscapes; mark critical points.
2. Verify numerically that the level set of `½xᵀAx = 1` has axis ratio `√κ` for three different `A`; overlay the eigenvector directions.
3. Draw a classifier's decision boundary as the `w·x + b = 0` level set and shade by the sign of the score; add the `±1` margin contours.
4. Build slices `φ(α)` through a random point of a 50-D function in three random directions; compare shapes.
5. Plot the logistic loss surface over `(w₁, w₂)` for separable and non-separable 2-D data; explain the flat tail.

### Check yourself (Unit 2)

1. What shape are the level sets of `x² + 9y²`, and what is the axis ratio?
2. Why is a linear classifier's decision boundary a level set?
3. What goes wrong if you pass `indexing="ij"` but index as if it were `"xy"`?

**Reference answers:** (1) Ellipses; semi-axis ratio `3` (`√9`). (2) It is the set where the linear score `w·x + b` equals the constant `0`. (3) The grid arrays are transposed, so values land at the wrong coordinates and plots come out rotated or reflected.

---

## Unit 3 — Partial derivatives (`02-…md`)

### 3.1 Why ML needs this

`∂L/∂wⱼ` answers: *"if I nudge weight `j` by a tiny amount and hold everything else fixed, how much does the loss change?"* Every gradient entry is one partial derivative, and every finite-difference gradient check computes them one coordinate at a time.

### 3.2 Intuition

Treat all variables except one as constants, then differentiate as in Module 05. Geometrically, a partial derivative is the slope of the surface in the direction of one coordinate axis.

### 3.3 Mechanics

- **Definition:** `∂f/∂xᵢ (x) = lim_{h→0} [f(x + h eᵢ) − f(x)]/h` where `eᵢ` is the `i`-th standard basis vector (Module 01).
- **Notation:** `∂f/∂x`, `fₓ`, `∂ₓf`. The curly `∂` signals "other variables held fixed"; `d` is for single-variable functions.
- **Rules carry over:** sum, product, quotient, chain rule (applied to the one variable), with others as constants.
- **Higher-order and mixed partials:** `∂²f/∂x∂y` is differentiate in `y`, then in `x`. If the second partials are continuous, **mixed partials are equal** (Clairaut/Schwarz): `f_{xy} = f_{yx}`. These form the Hessian (4C-02) and its symmetry is why the Hessian of a smooth loss is a symmetric matrix (Module 02 Lesson 3; Module 03).
- **Numerical partials:** central difference per coordinate, with `h ≈ 1e-5·max(1, |xᵢ|)` (Module 05); the cost is `2n` evaluations for all `n` partials.
- **Worked example:** `f(x, y) = x²y + sin(xy)`:
  `f_x = 2xy + y cos(xy)`, `f_y = x² + x cos(xy)`; mixed: `f_{xy} = 2x + cos(xy) − xy sin(xy) = f_{yx}`.
- **Worked ML example (least squares, one sample, two weights):** `L(w₁, w₂) = ½(w₁x₁ + w₂x₂ − y)²` ⇒ `∂L/∂wⱼ = (ŷ − y)xⱼ` with `ŷ = w₁x₁ + w₂x₂`. For `n` samples with mean loss `L = (1/2n)Σ(ŷᵢ − yᵢ)²`: `∂L/∂wⱼ = (1/n)Σ(ŷᵢ − yᵢ)xᵢⱼ`: the residual times the feature, averaged.
- **Worked ML example (logistic regression):** `L = −[y ln p + (1−y)ln(1−p)]`, `p = σ(w·x + b)`: `∂L/∂wⱼ = (p − y)xⱼ`, `∂L/∂b = p − y` (Module 05 Lesson 4 chain rule, now per coordinate).
- **Partial vs total derivative:** if the variables themselves depend on a parameter `t` (`x(t), y(t)`), the **total** derivative is `df/dt = f_x x′(t) + f_y y′(t)` (multivariable chain rule, Lesson 4).
- **Independent vs dependent variables:** `∂f/∂x` is ambiguous if `y` depends on `x`; state what is held fixed.

### 3.4 Code

```python
import numpy as np
import sympy as sp

# --- symbolic partials and mixed-partial symmetry
x, y = sp.symbols("x y", real=True)
f = x ** 2 * y + sp.sin(x * y)
fx, fy = sp.diff(f, x), sp.diff(f, y)
assert sp.simplify(sp.diff(fx, y) - sp.diff(fy, x)) == 0            # Clairaut: f_xy = f_yx
print(fx, "|", fy)

f_np  = sp.lambdify((x, y), f,  "numpy")
fx_np = sp.lambdify((x, y), fx, "numpy"); fy_np = sp.lambdify((x, y), fy, "numpy")

# --- numerical partials, one coordinate at a time (Module 05 central difference)
def partial_numeric(F, x, i, h=1e-5):
    x = np.asarray(x, float); e = np.zeros_like(x); step = h * max(1.0, abs(x[i])); e[i] = step
    return (F(x + e) - F(x - e)) / (2 * step)

F = lambda v: f_np(v[0], v[1])
rng = np.random.default_rng(0)
for _ in range(20):
    p = rng.uniform(-2, 2, 2)
    assert np.isclose(partial_numeric(F, p, 0), fx_np(*p), rtol=1e-6, atol=1e-8)
    assert np.isclose(partial_numeric(F, p, 1), fy_np(*p), rtol=1e-6, atol=1e-8)

# --- least-squares partials: ∂L/∂w_j = (1/n) Σ (ŷ_i − y_i) x_ij
n, d = 40, 3
X = rng.normal(size=(n, d)); y_ = X @ np.array([1.0, -2.0, 0.5]) + 0.1 * rng.normal(size=n)
w = rng.normal(size=d)
L = lambda w: 0.5 * np.mean((X @ w - y_) ** 2)
grad_manual = np.array([np.mean((X @ w - y_) * X[:, j]) for j in range(d)])    # one partial at a time
grad_vector = X.T @ (X @ w - y_) / n                                            # all partials at once: Xᵀ(Xw − y)/n
grad_num = np.array([partial_numeric(L, w, j) for j in range(d)])
assert np.allclose(grad_manual, grad_vector) and np.allclose(grad_vector, grad_num, rtol=1e-6)

# --- logistic partials: ∂L/∂w_j = mean (p − y) x_j,  ∂L/∂b = mean (p − y)
sig = lambda z: 1 / (1 + np.exp(-z))
yb = (rng.random(n) < sig(X @ np.array([1.0, -1.0, 0.0]))).astype(float)
def logloss(theta):
    w_, b_ = theta[:-1], theta[-1]; z = X @ w_ + b_
    return np.mean(np.maximum(z, 0) - z * yb + np.log1p(np.exp(-np.abs(z))))      # stable BCE with logits
theta = rng.normal(size=d + 1)
p = sig(X @ theta[:-1] + theta[-1])
g_ana = np.r_[X.T @ (p - yb) / n, np.mean(p - yb)]
g_num = np.array([partial_numeric(logloss, theta, j) for j in range(d + 1)])
assert np.allclose(g_ana, g_num, rtol=1e-6, atol=1e-9)

# --- total vs partial: f(x(t), y(t)) with x = cos t, y = sin t
t0 = 0.8; xt, yt = np.cos(t0), np.sin(t0)
total = fx_np(xt, yt) * (-np.sin(t0)) + fy_np(xt, yt) * np.cos(t0)               # f_x x' + f_y y'
h = 1e-6; total_num = (f_np(np.cos(t0 + h), np.sin(t0 + h)) - f_np(np.cos(t0 - h), np.sin(t0 - h))) / (2 * h)
assert np.isclose(total, total_num, rtol=1e-6)
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Differentiating with respect to the wrong variable | Gradient entry of the wrong feature | Label every symbol; numeric check each coordinate |
| Forgetting `1/n` (mean vs sum) | Constant-factor gradient error | State the reduction; check against numeric |
| Treating `∂f/∂x` as if `y` were fixed when `y` depends on `x` | Partial vs total confusion | Write what is held fixed |
| Using a single `h` for coordinates of different scale | Noisy partials for tiny or huge parameters | Scale `h` per coordinate (Module 05) |
| Computing all `n` partials numerically in training | `2n` forward passes per step | Numerics for tests only; use backprop |
| Assuming mixed partials commute for non-smooth `f` | `f_xy ≠ f_yx` at kinks | Smoothness assumption (or ReLU nets away from kinks) |
| Dropping the bias partial | Model cannot shift | Include `∂L/∂b = mean(p − y)` |

### 3.6 ML link

- **Gradient entries are partials** (Lesson 3).
- **Feature sensitivity:** `∂L/∂wⱼ ∝ mean(residual · feature j)`, so a feature with large scale dominates its partial (why scaling matters; Module 14).
- **Numerical partial derivatives** are the oracle in gradient checking (Module 05 Lesson 8; Projects 2).
- **Hessian symmetry** (4C-02) rests on the equality of mixed partials.

### 3.7 Lab (60 min)

1. Derive partials by hand for 8 functions of 2–3 variables; verify each with SymPy and with central differences at 20 random points.
2. Derive and verify the least-squares and logistic partials above; add an `L2` penalty `λ‖w‖²/2` and its partial `λwⱼ`.
3. Verify Clairaut's symmetry numerically with a second finite difference in two variables, `(f(x+h,y+h) − f(x+h,y−h) − f(x−h,y+h) + f(x−h,y−h))/(4h²)`.
4. Reproduce the total-derivative check along a curve and a parametrized weight path `w(t) = w₀ + t d`.

### Check yourself (Unit 3)

1. Compute `∂/∂x` and `∂/∂y` of `x² + 3xy + y³`.
2. What is `∂L/∂wⱼ` for the mean squared-error loss `(1/2n)Σ(w·xᵢ − yᵢ)²`?
3. When can you swap the order of mixed partials?

**Reference answers:** (1) `2x + 3y`; `3x + 3y²`. (2) `(1/n) Σᵢ (w·xᵢ − yᵢ) xᵢⱼ`. (3) When the second partials are continuous (e.g., smooth losses); not necessarily at kinks.

---

## Unit 4 — Gradients and the direction of steepest ascent (`03-…md`)

### 4.1 Why ML needs this

Gradient descent is `θ ← θ − η ∇L(θ)`. The reason it works, *why that direction*, is the content of this lesson, and the reason it can fail (scale, curvature, saddles) follows from the same geometry.

### 4.2 Intuition

Stand on a hillside. Of all directions you could step, one goes uphill fastest. The gradient points that way, and its length tells you how steep it is. Contour lines run **across** the slope, so the gradient is perpendicular to them.

### 4.3 Mechanics

- **Gradient:** `∇f(x) = (∂f/∂x₁, …, ∂f/∂xₙ)ᵀ ∈ ℝⁿ`. Same shape as `x`.
- **Directional derivative** along a **unit** vector `u`: `D_u f(x) = ∇f(x)·u = ‖∇f‖ cos θ`, where `θ` is the angle between `u` and `∇f` (Module 01 Lesson 2).
  - **Steepest ascent:** `θ = 0`, `u = ∇f/‖∇f‖`, rate `‖∇f‖`.
  - **Steepest descent:** `u = −∇f/‖∇f‖`, rate `−‖∇f‖`.
  - **No change:** `θ = 90°`: directions tangent to the level set.
- **Gradient ⟂ level set:** along a level set `f` is constant, so `D_t f = ∇f·t = 0` for every tangent `t`.
- **First-order approximation (linearization):** `f(x + δ) ≈ f(x) + ∇f(x)·δ`, with error `O(‖δ‖²)`. Gradient descent uses it: choose `δ = −η∇f` ⇒ `f` decreases by about `η‖∇f‖²` for small `η`.
- **Critical points:** `∇f = 0` (minimum, maximum, saddle; classification needs second derivatives: Module 05 Lesson 7 extended by the Hessian in 4C-02). Small `‖∇f‖` is a common *stopping criterion* but does not prove a minimum.
- **Scale dependence:** the gradient is **not** invariant to rescaling variables: if `x = 100 z` then `∂f/∂z = 100 ∂f/∂x`. This is the origin of the need for feature scaling and for adaptive optimizers (Module 08).
- **Gradients of the functions you will use constantly** (all with `x, w ∈ ℝⁿ` unless noted):

| `f` | `∇f` | Note |
|---|---|---|
| `c·x` (linear) | `c` | gradient is constant |
| `‖x‖²` | `2x` | points away from the origin |
| `‖x‖₂` | `x/‖x‖` | unit vector (undefined at 0) |
| `½ xᵀAx` | `½(A + Aᵀ)x` (`= Ax` if `A` symmetric) | quadratic bowl |
| `½‖Xw − y‖²` | `Xᵀ(Xw − y)` | least squares; `/n` for the mean |
| `λ‖w‖₂²/2` | `λw` | weight decay force |
| logistic loss (mean) | `Xᵀ(σ(Xw) − y)/n` | clean `p − y` form |

- **Descent step and learning rate:** `θ ← θ − η∇L`; the first-order model says "any small enough `η` decreases `L`"; curvature caps usable `η` (Module 05 Lesson 6: `η < 2/λ_max`).
- **Zig-zag in a narrow valley:** the gradient is perpendicular to contours, which in a long thin ellipse points mostly across the valley, not along it. That is why plain GD is slow on ill-conditioned problems and why momentum helps (Module 08).
- **Normalized gradient step:** `δ = −ε ∇f/‖∇f‖` moves a fixed *distance*; useful in analysis, clipping, and adversarial-example generation `[JUDGEMENT]`.

**Worked example:** `f(x, y) = x² + 4y²` at `(1, 1)`: `∇f = (2, 8)`, `‖∇f‖ = √68 ≈ 8.25`; steepest-ascent direction `(0.243, 0.970)` (mostly `y`); `D_u f` for `u = (1, 0)` is `2`.

### 4.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def num_grad(F, x, h=1e-5):
    x = np.asarray(x, float); g = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x); s = h * max(1.0, abs(x[i])); e[i] = s
        g[i] = (F(x + e) - F(x - e)) / (2 * s)
    return g

f  = lambda v: v[0] ** 2 + 4 * v[1] ** 2
gf = lambda v: np.array([2 * v[0], 8 * v[1]])
p = np.array([1.0, 1.0]); g = gf(p)
assert np.allclose(g, num_grad(f, p))

# directional derivative D_u f = ∇f · u, checked by finite differences along random unit vectors
for _ in range(50):
    u = rng.normal(size=2); u /= np.linalg.norm(u)
    D_num = (f(p + 1e-6 * u) - f(p - 1e-6 * u)) / 2e-6
    assert np.isclose(D_num, g @ u, rtol=1e-6)

# steepest ascent: among 200k random unit directions, the best is ≈ ∇f/‖∇f‖ and the best rate is ‖∇f‖
U = rng.normal(size=(200_000, 2)); U /= np.linalg.norm(U, axis=1, keepdims=True)
rates = U @ g
best = U[np.argmax(rates)]
print(rates.max(), np.linalg.norm(g), best, g / np.linalg.norm(g))
assert np.isclose(rates.max(), np.linalg.norm(g), rtol=1e-4)
assert np.allclose(best, g / np.linalg.norm(g), atol=0.02)

# gradient ⟂ level set: stepping along the tangent barely changes f; along the gradient it changes at rate ‖∇f‖
t = np.array([-g[1], g[0]]) / np.linalg.norm(g)
eps = 1e-4
d_tan, d_grad = f(p + eps * t) - f(p), f(p + eps * g / np.linalg.norm(g)) - f(p)
print(d_tan, d_grad)                                                # O(ε²) vs ≈ ε‖∇f‖
assert abs(d_tan) < 1e-3 * abs(d_grad)

# first-order approximation error is O(‖δ‖²)
for scale in (1e-1, 1e-2, 1e-3):
    delta = scale * np.array([0.6, -0.8])
    err = abs(f(p + delta) - (f(p) + g @ delta)); print(scale, err, err / scale ** 2)   # ratio ≈ constant

# gradients of common functions, all checked numerically
n, d = 60, 4
X = rng.normal(size=(n, d)); y = rng.normal(size=n); w = rng.normal(size=d)
A = rng.normal(size=(d, d))                                          # NOT symmetric
checks = {
    "x·c":          (lambda v: v @ w,                                  lambda v: w),
    "‖x‖²":         (lambda v: v @ v,                                  lambda v: 2 * v),
    "‖x‖":          (lambda v: np.linalg.norm(v),                      lambda v: v / np.linalg.norm(v)),
    "½xᵀAx (A nonsym)": (lambda v: 0.5 * v @ A @ v,                    lambda v: 0.5 * (A + A.T) @ v),
    "LS":           (lambda v: 0.5 * np.mean((X @ v - y) ** 2),        lambda v: X.T @ (X @ v - y) / n),
    "LS + ridge":   (lambda v: 0.5 * np.mean((X @ v - y) ** 2) + 0.05 * v @ v, lambda v: X.T @ (X @ v - y) / n + 0.1 * v),
}
for name, (F, G) in checks.items():
    v = rng.normal(size=d); err = np.linalg.norm(G(v) - num_grad(F, v)) / (np.linalg.norm(G(v)) + 1e-12)
    assert err < 1e-6, (name, err); print(f"{name:20s} rel err {err:.1e}")
v = rng.normal(size=d); assert not np.allclose(A @ v, 0.5 * (A + A.T) @ v)     # Ax is the WRONG gradient for nonsymmetric A

# gradient descent: well- vs ill-conditioned quadratic
def gd(A, x0, eta, steps):
    x = x0.copy(); traj = [x.copy()]
    for _ in range(steps): x = x - eta * (A @ x); traj.append(x.copy())
    return np.array(traj)
x0 = np.array([1.0, 1.0])
for kappa in (1, 10, 100):
    A_ = np.diag([1.0, float(kappa)]); eta = 1.0 / kappa             # stable: η ≤ 1/λmax
    traj = gd(A_, x0, eta, 200)
    print(f"κ={kappa:3d}  ‖x_200‖ = {np.linalg.norm(traj[-1]):.2e}")  # slower as κ grows (report your own numbers)
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Using `Ax` as the gradient of `½xᵀAx` for non-symmetric `A` | Wrong gradient (passes only if `A` is symmetric) | Use `½(A + Aᵀ)x`, or symmetrize `A` |
| Gradient shape ≠ parameter shape | Broadcasting bug or silent wrong update | Assert shapes |
| Forgetting that the gradient depends on the variable scaling | Big-scale features dominate updates | Standardize features |
| Using the *unnormalized* gradient as a step *length* analysis | Confused step size | Distinguish `η∇f` from a normalized step |
| Treating `‖∇f‖ ≈ 0` as proof of a minimum | Saddle/plateau misread | Check curvature or compare with neighbours |
| Step size too large | Loss increases (the linear model is only local) | Smaller `η`; line search; Module 08 |
| Gradient of `‖x‖` at `0` | `nan` | Guard with an epsilon or a subgradient |
| Sign error: ascending instead of descending | Loss grows | Test that one small step reduces the loss |

### 4.6 ML link

- **Gradient descent and every variant** (Module 08) use `−∇L` as the update direction.
- **Linear/logistic regression gradients** are the first hand-derived gradients you will implement (Module 14).
- **Weight decay** adds `λw` to the gradient (Module 14, Module 05 Lesson 2).
- **Gradient clipping** rescales `∇L` by its norm (Module 01 Lesson 4; Stage 5C-03).
- **Adversarial examples (FGSM-style)** step the *input* along the sign/direction of the loss gradient `[JUDGEMENT]`.
- **Conditioning and feature scaling:** the thin-ellipse picture (Lesson 1) is why preconditioning/adaptive methods exist (Module 08, 4C-03).

### 4.7 Lab (75 min)

1. Verify `D_u f = ∇f·u`, the steepest-ascent claim, and gradient ⟂ level set on three functions (a bowl, a saddle, Rosenbrock) at 10 random points each.
2. Table of gradients for the seven functions above; check each with `num_grad` at 20 random points; include the non-symmetric `A` trap.
3. Linearization experiment: error of `f(x + δ)` vs `f(x) + ∇f·δ` as `‖δ‖` shrinks; fit the slope of the log-log plot (should be ≈ 2).
4. GD on `½xᵀAx` for `κ ∈ {1, 10, 100, 1000}` with the largest stable step; plot trajectories on contours and report iterations to `‖x‖ < 1e-6`.
5. Show that rescaling a feature by `100×` changes the gradient component for that feature and slows GD; fix it by standardization.

### Check yourself (Unit 4)

1. Gradient of `f(x, y) = x²y` at `(2, 3)`, and the steepest-ascent unit direction?
2. Why is the gradient perpendicular to level sets?
3. What is the gradient of `½‖Xw − y‖²`?

**Reference answers:** (1) `∇f = (2xy, x²) = (12, 4)`; direction `(12, 4)/√160 ≈ (0.949, 0.316)`. (2) Along a level set `f` is constant, so the directional derivative along any tangent is `∇f·t = 0`. (3) `Xᵀ(Xw − y)`.

---

## Unit 5 — Computational graphs and backpropagation by hand (`04-…md`)

### 5.1 Why ML needs this

Backpropagation is the algorithm that computes the gradient of a loss with respect to *every* parameter in time comparable to one forward pass. It is nothing more than the multivariable chain rule applied systematically on a **computational graph**, caching forward values. Doing it by hand on a tiny network is the fastest way to stop treating `loss.backward()` as magic and to be able to debug a custom layer.

### 5.2 Intuition

Write the computation as a graph of elementary operations. **Forward:** evaluate nodes left to right. **Backward:** start at the loss with `∂L/∂L = 1` and move right to left; each node multiplies the incoming gradient by its **local derivative** and passes it on. When a value is used in two places, the gradients arriving from both paths **add**.

### 5.3 Mechanics

- **Computational graph:** nodes are values/operations (`+`, `×`, `tanh`, `log`, …); edges are data dependencies. It must be acyclic (a DAG).
- **Multivariable chain rule:** if `L` depends on `x` through several intermediates `u₁…u_m`, then `∂L/∂x = Σⱼ (∂L/∂uⱼ)(∂uⱼ/∂x)`: **sum over paths**. This is why gradient buffers **accumulate** (`+=`) and must be zeroed between steps.
- **Node recipe:** for a node `z = op(a, b)`, with upstream gradient `ḡ = ∂L/∂z`: `∂L/∂a += ḡ · ∂z/∂a`, `∂L/∂b += ḡ · ∂z/∂b`.
- **Local derivatives to memorize:**

| Op | Backward |
|---|---|
| `z = a + b` | `ā += ḡ`, `b̄ += ḡ` (gradient copies) |
| `z = a·b` | `ā += ḡ·b`, `b̄ += ḡ·a` (swap) |
| `z = a/b` | `ā += ḡ/b`, `b̄ −= ḡ·a/b²` |
| `z = aᵏ` | `ā += ḡ·k·aᵏ⁻¹` |
| `z = tanh a` | `ā += ḡ(1 − z²)` |
| `z = σ(a)` | `ā += ḡ·z(1 − z)` |
| `z = eᵃ` | `ā += ḡ·z` |
| `z = ln a` | `ā += ḡ/a` |
| `z = max(0, a)` | `ā += ḡ·1[a > 0]` |

- **Matrix form of a dense layer** `Z = XW + b`, `X: (n, d)`, `W: (d, k)`, `b: (k,)`, upstream `dZ: (n, k)`:
  `dW = Xᵀ dZ` `(d, k)`; `db = Σ_rows dZ` `(k,)`; `dX = dZ Wᵀ` `(n, d)`. (Check shapes: they must match the quantity being differentiated.)
- **A tiny network by hand** (`2 → h → 1`, `tanh` hidden, sigmoid output, BCE loss, `n` samples, mean):
  `Z1 = XW1 + b1`, `H = tanh Z1`, `z2 = H w2 + b2`, `p = σ(z2)`, `L = mean BCE`.
  Backward: `dz2 = (p − y)/n` ⇒ `dw2 = Hᵀ dz2`, `db2 = Σ dz2`, `dH = dz2 w2ᵀ`, `dZ1 = dH ⊙ (1 − H²)`, `dW1 = Xᵀ dZ1`, `db1 = Σ_rows dZ1`.
- **Forward vs reverse mode:** forward mode (Module 05 `Dual`) carries one directional derivative per pass: cost scales with the number of *inputs*; reverse mode computes the gradient of a scalar with respect to *all* inputs in one backward pass, but needs the cached forward values (memory). For a scalar loss with millions of parameters, reverse mode wins. `[VERIFY: complexity statement in 4C-07]`.
- **Autodiff implementation sketch:** each value stores `data`, `grad`, its parents, and a closure computing its parents' contributions; `backward()` topologically sorts the graph, seeds the output gradient with `1`, and calls closures in reverse order.
- **Vanishing/exploding gradients** are products of local derivatives along paths (Module 05 Lesson 4–5); residual connections add parallel paths so gradients sum rather than only multiply.
- **Common backprop bugs:** overwriting instead of accumulating (`=` vs `+=`); not zeroing gradients between steps; wrong local derivative; using the post-activation where the pre-activation is needed (or vice versa); transposing `W` incorrectly; wrong reduction axis for biases; dropping the `1/n`; calling backward on a graph in non-topological order.

**Worked example (fan-out):** `f(x) = x·x + x`. Graph: `a = x·x`, `f = a + x`. Backward: `f̄ = 1`; `ā = 1`, `x̄ += 1` (from the `+`); `a = x·x` contributes `x̄ += ā·x + ā·x = 2x`. Total `df/dx = 2x + 1` ✓: *three arrows into `x`, three contributions added.*

### 5.4 Code

```python
import math
import numpy as np

class Value:
    """Scalar reverse-mode autodiff node."""
    def __init__(self, data, parents=(), op=""):
        self.data, self.grad = float(data), 0.0
        self._parents, self._backward, self.op = parents, (lambda: None), op

    @staticmethod
    def _w(o): return o if isinstance(o, Value) else Value(o)

    def __add__(self, o):
        o = Value._w(o); out = Value(self.data + o.data, (self, o), "+")
        def _b(): self.grad += out.grad; o.grad += out.grad
        out._backward = _b; return out
    __radd__ = __add__

    def __mul__(self, o):
        o = Value._w(o); out = Value(self.data * o.data, (self, o), "*")
        def _b(): self.grad += out.grad * o.data; o.grad += out.grad * self.data
        out._backward = _b; return out
    __rmul__ = __mul__

    def __pow__(self, k):
        assert isinstance(k, (int, float)); out = Value(self.data ** k, (self,), f"**{k}")
        def _b(): self.grad += out.grad * k * self.data ** (k - 1)
        out._backward = _b; return out

    def __neg__(self): return self * -1.0
    def __sub__(self, o): return self + (-Value._w(o))
    def __rsub__(self, o): return Value._w(o) + (-self)
    def __truediv__(self, o): return self * Value._w(o) ** -1
    def __rtruediv__(self, o): return Value._w(o) * self ** -1

    def tanh(self):
        t = math.tanh(self.data); out = Value(t, (self,), "tanh")
        def _b(): self.grad += out.grad * (1 - t * t)
        out._backward = _b; return out
    def exp(self):
        e = math.exp(self.data); out = Value(e, (self,), "exp")
        def _b(): self.grad += out.grad * e
        out._backward = _b; return out
    def log(self):
        out = Value(math.log(self.data), (self,), "log")
        def _b(): self.grad += out.grad / self.data
        out._backward = _b; return out
    def sigmoid(self):
        z = self.data; s = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
        out = Value(s, (self,), "sigmoid")
        def _b(): self.grad += out.grad * s * (1 - s)
        out._backward = _b; return out

    def backward(self):
        topo, seen = [], set()
        def build(v):
            if id(v) not in seen:
                seen.add(id(v)); [build(p) for p in v._parents]; topo.append(v)
        build(self)
        self.grad = 1.0                                        # seed ∂L/∂L = 1
        for v in reversed(topo): v._backward()                 # parents receive += contributions

# --- fan-out: f(x) = x·x + x  →  f'(x) = 2x + 1
x = Value(3.0); f = x * x + x; f.backward()
assert np.isclose(f.data, 12.0) and np.isclose(x.grad, 7.0)

# --- a single neuron: y = tanh(w1 x1 + w2 x2 + b), compared with finite differences
def neuron(w1, w2, b, x1, x2): return math.tanh(w1 * x1 + w2 * x2 + b)
w1, w2, b = Value(0.4), Value(-0.7), Value(0.1); x1, x2 = 1.5, -0.5
y = (w1 * x1 + w2 * x2 + b).tanh(); y.backward()
h = 1e-6
for g_auto, args in ((w1.grad, (0.4, -0.7, 0.1)),):
    num = (neuron(args[0] + h, args[1], args[2], x1, x2) - neuron(args[0] - h, args[1], args[2], x1, x2)) / (2 * h)
    assert np.isclose(g_auto, num, rtol=1e-6)
t = math.tanh(0.4 * x1 - 0.7 * x2 + 0.1); assert np.isclose(w1.grad, (1 - t * t) * x1) and np.isclose(b.grad, 1 - t * t)

# --- the bug that fan-out teaches: overwrite (=) vs accumulate (+=)
class BadValue(Value):
    def __mul__(self, o):
        o = Value._w(o); out = BadValue(self.data * o.data, (self, o), "*")
        def _b(): self.grad = out.grad * o.data; o.grad = out.grad * self.data     # BUG: overwrites
        out._backward = _b; return out
xb = BadValue(3.0); fb = xb * xb; fb.backward()
print(xb.grad)        # not 6: the second use of x overwrote the first contribution

# --- vectorized dense layer: dW = Xᵀ dZ, db = Σ dZ, dX = dZ Wᵀ — verified numerically
rng = np.random.default_rng(0)
n, d, k = 5, 3, 2
X, W, b_ = rng.normal(size=(n, d)), rng.normal(size=(d, k)), rng.normal(size=k)
T = rng.normal(size=(n, k))
loss = lambda W_, b__: 0.5 * np.sum((X @ W_ + b__ - T) ** 2)
dZ = X @ W + b_ - T                                               # (n, k) upstream gradient
dW, db, dX = X.T @ dZ, dZ.sum(axis=0), dZ @ W.T
assert dW.shape == W.shape and db.shape == b_.shape and dX.shape == X.shape
for i in range(d):
    for j in range(k):
        E = np.zeros_like(W); E[i, j] = 1e-6
        assert np.isclose((loss(W + E, b_) - loss(W - E, b_)) / 2e-6, dW[i, j], rtol=1e-6)
for j in range(k):
    e = np.zeros(k); e[j] = 1e-6
    assert np.isclose((loss(W, b_ + e) - loss(W, b_ - e)) / 2e-6, db[j], rtol=1e-6)
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `grad = …` instead of `grad += …` | Wrong gradient whenever a value is used twice | Fan-out test: `f = x·x + x` must give `2x + 1` |
| Not zeroing gradients between steps | Gradients accumulate across iterations | `zero_grad()` each step; test two consecutive backward passes |
| Wrong local derivative (e.g., `tanh′ = 1 − tanh`) | Gradient check fails | Per-op numeric check |
| Using pre-activation where post-activation is needed | Error of a constant-ish factor | Cache both `z` and `a` separately |
| Shape errors in matrix backward (`dW = dZ Xᵀ`) | Shape mismatch or silent wrong values | Check shapes equal the parameter shapes |
| Bias gradient summed over the wrong axis | Wrong shape/values | `axis=0` over the batch |
| Forgetting `1/n` in the loss | Constant-factor mismatch | Compare with numeric gradient; check ratio |
| Non-topological backward order | Some nodes use stale/zero gradients | Topological sort (as in `Value.backward`) |
| Recursion depth on a long graph | `RecursionError` | Iterative topological sort for deep graphs |
| Gradient through a non-differentiable op (`argmax`, rounding) | Zero or undefined gradient | Use a relaxation (softmax) or a straight-through estimator `[JUDGEMENT]` |

### 5.6 ML link

- **Backpropagation in every framework** is reverse-mode autodiff on a dynamically or statically built graph (Stage 5C-01, 5C-02; derivation in 4C-07).
- **Layer gradients** `dW = Xᵀ dZ` are the building block of every dense layer, and attention/conv layers generalize them (4C-08, 4C-09).
- **Gradient accumulation** across micro-batches relies on the additive property of gradients (Stage 5C-03).
- **Autodiff caveats:** memory for cached activations, checkpointing, and non-differentiable ops (Stage 5C-03, 5D-06) `[VERIFY]`.
- **Gradient checking** with finite differences is how you test a custom `backward` (Module 05, Project 2).

### 5.7 Lab (90 min)

1. Hand-derive the backward pass of `L = (σ(w₁x₁ + w₂x₂ + b) − y)²`; draw the graph with every local derivative; verify against `Value` and finite differences.
2. Implement `Value` (above); test `tanh`, `sigmoid`, `exp`, `log`, division, power; build a 2-input neuron and a 2-layer network out of `Value`s; compare all gradients with finite differences (`< 1e-6` relative).
3. Reproduce the fan-out bug and the missing-`zero_grad` bug; write tests that catch both.
4. Implement the vectorized backward for a dense layer, `tanh`, and a sigmoid + BCE head; chain them into the 2-hidden-unit network; verify every gradient with the Module 05 checker.
5. Count operations: show reverse mode needs one backward pass for all `p` parameters while central differences need `2p` forward passes; measure on networks with `p ∈ {10, 100, 1000}` (your machine, your numbers).

### Check yourself (Unit 5)

1. What is `df/dx` for `f = x·x + x`, and why do three backward contributions appear?
2. Shapes of `dW`, `db`, `dX` for `Z = XW + b` with `X: (n, d)`, `W: (d, k)`?
3. Why must gradient buffers be zeroed between optimization steps?

**Reference answers:** (1) `2x + 1`; `x` is used in three places (two inputs of the product, one input of the sum), and gradients from every path add. (2) `dW: (d, k)`, `db: (k,)`, `dX: (n, d)`. (3) Backward *accumulates* with `+=`, so leftover values from the previous step would be added to the new gradient.

---

## Unit 6 — Practice question bank (`practice-questions.md`)

### 6.1 Structure

About 40 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 10 per tier, each with a hidden answer and a one-line rationale. Mix hand derivations, "predict the shape/value", runnable code, and ML judgement.

### 6.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 6.3 Seed items

**Q1 [L1] Definition.** What is a level set of `f`? → `{x : f(x) = c}`.
**Q2 [L2] Partials.** `f = x²y + y³`. Find `f_x`, `f_y`. → `2xy`; `x² + 3y²`.
**Q3 [L2] Gradient.** `f(x, y, z) = xyz` at `(1, 2, 3)`: `∇f`? → `(yz, xz, xy) = (6, 3, 2)`.
**Q4 [L2] Directional.** Rate of change of `f = x² + y²` at `(1, 1)` along `(1, 0)`? → `∇f = (2, 2)`; `D_u f = 2`.
**Q5 [L2] Steepest.** Steepest-ascent direction and rate for `f = 3x + 4y`? → `(3, 4)/5`; rate `5`.
**Q6 [L2] Least squares.** `L = ½‖Xw − y‖²`. Gradient and its shape for `X: (50, 4)`? → `Xᵀ(Xw − y)`, shape `(4,)`.
**Q7 [L2] Backprop.** `L = (wx − y)²`, `w = 2, x = 3, y = 5`. `dL/dw`? → `2(wx − y)x = 2(1)(3) = 6`.
**Q8 [L2] Shapes.** `Z = XW + b`, `X: (32, 10)`, `W: (10, 5)`. Shape of `dW`? Of `db`? → `(10, 5)`; `(5,)`.
**Q9 [L3] Debug.** Your gradient of `½xᵀAx` is `Ax`, but the numeric check fails. `A` is random. → `A` is not symmetric; the gradient is `½(A + Aᵀ)x`.
**Q10 [L3] Debug.** `f = x·x` built with a `Value` class gives `x.grad = 3` for `x = 3` (should be 6). → Gradient overwritten (`=`) instead of accumulated (`+=`) when `x` appears twice.
**Q11 [L3] Debug.** Training loss increases from step 1. List three gradient-related causes. → Sign error (ascending), learning rate too large, wrong gradient (check with finite differences); also missing `zero_grad` (gradients accumulate).
**Q12 [L3] Analysis.** GD on `½(x² + 1000y²)` with `η = 0.01` diverges, but converges with `η = 0.001`. Why? → Stability needs `η < 2/λ_max = 0.002`; `0.01` exceeds it.
**Q13 [L3] Analysis.** `‖∇L‖` is `1e-6` but the loss is still high. Possible explanations? → Plateau/saddle, vanishing gradients (saturated activations), or a very flat valley; inspect curvature and activations.
**Q14 [L4] Design.** Write the test plan for a custom layer's backward pass. → Forward-value tests on known inputs; per-parameter finite-difference check at several seeds in `float64`; shape assertions; fan-out/accumulation test; avoid kinks; mutation-test the checker itself (Module 05 Project 2).
**Q15 [L4] Design.** Features have scales `1` and `10⁴`. Predict GD behaviour and propose fixes. → Elongated valley (large `κ`); standardize features, or use an adaptive/preconditioned optimizer; verify via the conditioning of `XᵀX`.
**Q16 [L4] Design.** You must backprop through `argmax`. → The gradient is zero or undefined; use a differentiable relaxation (softmax with temperature) or a straight-through estimator; state the bias this introduces.

### 6.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Functions, level sets | 2 | 2 | 1 | 1 |
| Partial derivatives | 2 | 3 | 2 | 0 |
| Gradients, steepest ascent | 2 | 3 | 3 | 1 |
| Computational graphs, backprop | 2 | 3 | 4 | 2 |

### Check yourself (Unit 6)

1. Why include the non-symmetric `A` item?
2. Which items need runnable code?

**Reference answers:** (1) `Ax` as the gradient of `½xᵀAx` is a very common slip that only a numeric check reveals. (2) All L3 debug items and any answer that depends on floating-point behaviour.

---

## Unit 7 — Project index (`Projects/README.md`)

### 7.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Gradient field and contour plotter | Landscapes, analytic vs numeric gradients, gradient ⟂ contours, GD paths | 1–3 | 5–6 h |
| 2 | Backpropagation by hand on a tiny network | Hand derivation, scalar autodiff, vectorized backward, gradient-checked training | 3–5 | 7–8 h |

Order: 1 → 2 (Project 2 reuses the gradient-checking utilities from Project 1 and Module 05). Outputs feed `mlmath/calculus.py` (deliverable D6) and `mlmath/autograd_tiny.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`), plus notebook `07_gradients.ipynb`. Project 2's network is reused in Module 08 (optimizer comparison) and Module 14.

### 7.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (gradients match finite differences / SymPy; training converges as claimed) | 30 |
| Failure-mode handling (kinks, domain edges, bad seeds, injected bugs detected) | 15 |
| Reproducibility (seeded, pinned, clean venv, headless plotting) | 15 |
| Explanation quality (what each figure shows and why it matters for training) | 15 |
| Code quality (types, shape docstrings, no hidden state) | 15 |
| ML connection paragraph | 10 |

### 7.3 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 7)

1. What does Project 2 reuse from Project 1?
2. Where is Project 2's network reused later?

**Reference answers:** (1) The gradient-checking utilities (and Module 05's checker). (2) In Module 08 (optimizer comparison) and Module 14 (linear/logistic models).

---

## Unit 8 — Project: Gradient field and contour plotter (`Projects/01-…md`)

### 8.1 Brief

Build `gradplot`: a library plus notebook that evaluates 2-D landscapes on grids, computes analytic and numerical gradients (cross-checked), draws contour maps with gradient fields, verifies the geometry (gradient ⟂ contour, steepest ascent), and overlays gradient-descent paths for several learning rates and conditioning levels.

**Industry framing:** loss-landscape and optimizer diagnostics are standard debugging views. The deliverable is a tested toolkit, not a one-off plot, and every picture is backed by a numerical check.

### 8.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Landscape catalogue | ≥ 7 functions with analytic gradients: bowl, ill-conditioned bowl (param. `κ`), saddle, Rosenbrock, Himmelblau, a 2-D logistic-loss surface on a synthetic dataset, a rotated ill-conditioned bowl |
| R2 | Grid evaluation | `evaluate_grid(f, xlim, ylim, n)` returning `X, Y, Z` with a documented indexing convention and a test that `Z[i, j] == f(x[j], y[i])` |
| R3 | Gradient tools | Analytic gradient, central-difference gradient (per-coordinate `h`), relative-error check across the grid; fail loudly on mismatch |
| R4 | Gradient field | Quiver data on a coarse grid; options for raw, normalized, and magnitude-coloured arrows (and a note on what each hides) |
| R5 | Orthogonality test | At random points, a step along the tangent changes `f` by `O(ε²)` while a step along the gradient changes it by `≈ ε‖∇f‖` (automated test) |
| R6 | Steepest-ascent test | Among sampled unit directions the best matches `∇f/‖∇f‖` and its rate `‖∇f‖` (automated test) |
| R7 | GD path tool | `gd_path(f, grad, x0, eta, steps)` with divergence detection; overlay paths for ≥ 3 learning rates on contours; record steps to tolerance |
| R8 | Conditioning study | For `κ ∈ {1, 10, 100, 1000}`: largest stable `η`, steps to reach `‖∇f‖ < 1e-6`, path shape; compare with the `2/λ_max` and `κ`-based predictions |
| R9 | Slice tool | `slice_1d(f, x0, d, alphas)` through a point in any dimension; plot and differentiate the slice numerically |
| R10 | Critical points | Locate critical points of the catalogue by Newton/GD from a grid of starts; classify by the sign pattern of the curvature (2×2 Hessian eigenvalues from finite differences) |
| R11 | Headless plotting | All figures generated by one script with `matplotlib.use("Agg")` to `results/`; seeded |
| R12 | Report | `REPORT.md`: each figure with a one-sentence takeaway and the numerical check that backs it |

### 8.3 Layout and starter

```
gradplot/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/gradplot/{__init__,landscapes,grid,gradients,paths,critical,plots}.py
├── tests/{test_landscapes,test_grid,test_gradients,test_geometry,test_paths}.py
├── notebooks/07_gradient_field.ipynb
└── results/
```

```python
# src/gradplot/landscapes.py
import numpy as np

def bowl(p):        x, y = p; return x ** 2 + y ** 2
def g_bowl(p):      return 2 * np.asarray(p, float)

def ill(kappa=25.0):
    f = lambda p: 0.5 * (p[0] ** 2 + kappa * p[1] ** 2)
    g = lambda p: np.array([p[0], kappa * p[1]])
    return f, g

def saddle(p):      return p[0] ** 2 - p[1] ** 2
def g_saddle(p):    return np.array([2 * p[0], -2 * p[1]])

def rosenbrock(p):  x, y = p; return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2
def g_rosenbrock(p):
    x, y = p; return np.array([-2 * (1 - x) - 400 * x * (y - x ** 2), 200 * (y - x ** 2)])

def himmelblau(p):  x, y = p; return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2
def g_himmelblau(p):
    x, y = p; return np.array([4 * x * (x ** 2 + y - 11) + 2 * (x + y ** 2 - 7),
                               2 * (x ** 2 + y - 11) + 4 * y * (x + y ** 2 - 7)])

def logistic_surface(X, y):
    """Mean logistic loss over (w1, w2), no bias; X: (n, 2), y in {0,1}."""
    def f(w):
        z = X @ np.asarray(w, float); return np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z))))
    def g(w):
        z = X @ np.asarray(w, float); p = 1 / (1 + np.exp(-z)); return X.T @ (p - y) / len(y)
    return f, g

def rotated(f, g, theta):
    c, s = np.cos(theta), np.sin(theta); R = np.array([[c, -s], [s, c]])
    return (lambda p: f(R.T @ np.asarray(p, float))), (lambda p: R @ g(R.T @ np.asarray(p, float)))
```

```python
# src/gradplot/grid.py
import numpy as np

def evaluate_grid(f, xlim, ylim, n=200):
    """Returns X, Y, Z with indexing='xy': Z[i, j] = f((x_j, y_i)); shapes (n, n)."""
    xs, ys = np.linspace(*xlim, n), np.linspace(*ylim, n)
    X, Y = np.meshgrid(xs, ys)
    Z = np.array([[f(np.array([x, y])) for x in xs] for y in ys])
    return X, Y, Z

def numeric_grad(f, p, h=1e-5):
    p = np.asarray(p, float); g = np.zeros_like(p)
    for i in range(p.size):
        e = np.zeros_like(p); s = h * max(1.0, abs(p[i])); e[i] = s
        g[i] = (f(p + e) - f(p - e)) / (2 * s)
    return g
```

```python
# src/gradplot/paths.py
import numpy as np

def gd_path(grad, x0, eta, steps=500, tol=1e-8, blowup=1e8):
    x = np.asarray(x0, float).copy(); path = [x.copy()]
    for k in range(steps):
        g = grad(x)
        if np.linalg.norm(g) < tol: return np.array(path), "converged", k
        x = x - eta * g; path.append(x.copy())
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > blowup:
            return np.array(path), "diverged", k
    return np.array(path), "max_steps", steps
```

```python
# tests/test_geometry.py
import numpy as np
from gradplot import landscapes as L
from gradplot.grid import numeric_grad

CASES = {"bowl": (L.bowl, L.g_bowl), "saddle": (L.saddle, L.g_saddle),
         "rosenbrock": (L.rosenbrock, L.g_rosenbrock), "himmelblau": (L.himmelblau, L.g_himmelblau)}

def test_analytic_equals_numeric():
    rng = np.random.default_rng(0)
    for name, (f, g) in CASES.items():
        for p in rng.uniform(-2, 2, size=(20, 2)):
            ga, gn = g(p), numeric_grad(f, p)
            assert np.linalg.norm(ga - gn) / (np.linalg.norm(ga) + 1e-12) < 1e-6, name

def test_gradient_orthogonal_to_contour():
    rng = np.random.default_rng(1); eps = 1e-5
    for name, (f, g) in CASES.items():
        for p in rng.uniform(-2, 2, size=(10, 2)):
            gp = g(p); n = np.linalg.norm(gp)
            if n < 1e-3: continue                                   # skip near-critical points
            t = np.array([-gp[1], gp[0]]) / n
            d_tan = abs(f(p + eps * t) - f(p)); d_grad = abs(f(p + eps * gp / n) - f(p))
            assert d_tan < 1e-2 * d_grad, name

def test_gradient_is_steepest_ascent():
    rng = np.random.default_rng(2)
    f, g = L.rosenbrock, L.g_rosenbrock; p = np.array([0.3, -0.2]); gp = g(p)
    U = rng.normal(size=(100_000, 2)); U /= np.linalg.norm(U, axis=1, keepdims=True)
    rates = U @ gp
    assert np.isclose(rates.max(), np.linalg.norm(gp), rtol=1e-4)
    assert np.allclose(U[np.argmax(rates)], gp / np.linalg.norm(gp), atol=0.02)
```

```python
# tests/test_paths.py
import numpy as np
from gradplot.landscapes import ill
from gradplot.paths import gd_path

def test_stability_threshold_matches_two_over_lambda_max():
    f, g = ill(kappa=25.0)                                         # λ_max = 25 → stable iff η < 2/25 = 0.08
    _, status_ok, _ = gd_path(g, [1.0, 1.0], eta=0.07, steps=5000)
    _, status_bad, _ = gd_path(g, [1.0, 1.0], eta=0.09, steps=5000)
    assert status_ok == "converged" and status_bad == "diverged"
```

`[VERIFY]` Confirm the tolerances in the geometry tests (`1e-2` ratio, `atol=0.02`) and the `0.07`/`0.09` step sizes by running them; adjust only with evidence.

### 8.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | All catalogue gradients match central differences (`< 1e-6` relative) at 20 random points each; grid indexing test passes |
| M2 | R4–R6 | Quiver data computed; orthogonality and steepest-ascent tests pass on ≥ 4 landscapes |
| M3 | R7–R8 | Paths for ≥ 3 learning rates per landscape; measured stability threshold within 5% of `2/λ_max` for the quadratic cases; steps-to-tolerance table for `κ ∈ {1, 10, 100, 1000}` from your run |
| M4 | R9–R10 | Slice plots for a 50-D function; critical points of Himmelblau (four minima) and Rosenbrock found and classified correctly |
| M5 | R11–R12 | One script regenerates all figures headlessly; each figure in `REPORT.md` has its check and takeaway |

### 8.5 Questions the write-up must answer

1. Why are contours of the ill-conditioned bowl elongated, and how does that shape the gradient direction relative to the valley?
2. At which `η` does GD start to diverge on the quadratic, and how does that compare with `2/λ_max`?
3. Does a normalized gradient field hide information? Show what changes between raw and normalized arrows.
4. Where does GD get stuck on Himmelblau and on the saddle, and what does it depend on?
5. What does a 1-D slice of a high-dimensional landscape tell you, and what can it not tell you?

### 8.6 Failure modes to demonstrate

`meshgrid` index swap; unequal axis aspect; linear contour levels on Rosenbrock; quiver arrows scaled so they overlap; gradients near critical points normalized to noise; GD on the saddle starting exactly on the stable manifold (`y = 0`) vs slightly off; divergence detection missing `nan`; numeric gradient with a fixed `h` across parameters of very different scale.

### 8.7 Stretch goals

1. Momentum and Nesterov paths overlaid on the same contours (preview of Module 08).
2. A 3-D surface plot with the GD path lifted onto the surface.
3. Hessian eigen-directions drawn at critical points via finite differences (preview of 4C-02).
4. A real 2-parameter loss surface from a tiny model on a toy dataset you generate (e.g., the logistic surface for separable vs non-separable data) and a discussion of the flat tail.
5. Property tests (`hypothesis`): `∇f(x)·t ≈ 0` for tangents, and gradient linearity `∇(af + bg) = a∇f + b∇g`.

### 8.8 ML connection (README prompt)

Explain how each view maps to training diagnostics: conditioning ↔ slow convergence and scaling, step-size threshold ↔ learning-rate choice, saddles/basins ↔ initialization dependence, normalized vs raw gradients ↔ gradient clipping and normalized optimizers.

### Check yourself (Unit 8)

1. Why test the orthogonality of the gradient numerically instead of only plotting it?
2. What does a diverging path on the quadratic tell you about `η`?

**Reference answers:** (1) A plot can look right at a glance while a wrong gradient (e.g., a swapped component) still looks plausible; a numeric test fails loudly. (2) That `η` exceeded `2/λ_max` of the curvature along the steepest direction.

---

## Unit 9 — Project: Backpropagation by hand on a tiny network (`Projects/02-…md`)

### 9.1 Brief

Build `tinybp`: a tiny `2 → h → 1` network (tanh hidden units, sigmoid output, binary cross-entropy) trained on XOR with **four independent gradient implementations that must agree**: (1) a hand-derived scalar-by-scalar backward pass, (2) a vectorized NumPy backward pass, (3) a `Value`-based reverse-mode autodiff, and (4) finite differences. Then inject bugs and show the checks catch them.

**Industry framing:** when a custom layer is written, its gradient is validated against an independent implementation before training. The deliverable includes the paper derivation, the code, the agreement table, and an honest account of when training succeeds and when it does not.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Hand derivation | `DERIVATION.md` (or notebook cells): graph diagram, forward equations, every local derivative, the full backward pass for all parameters (`W1, b1, w2, b2`), written **before** the code |
| R2 | Scalar backward | Pure-Python loops over samples and units, no NumPy in the backward pass; each line labelled with the derivation step |
| R3 | Vectorized backward | `dz2 = (p − y)/n`, `dw2 = Hᵀdz2`, `db2`, `dH`, `dZ1 = dH⊙(1−H²)`, `dW1 = Xᵀ dZ1`, `db1`; shape assertions |
| R4 | `Value` autodiff | Reuse the Unit 5 class; build the network from `Value`s; loss as a `Value`; `backward()` fills all parameter gradients |
| R5 | Agreement test | All four gradient sets agree: `< 1e-6` relative error between any pair at 20 random parameter initializations and random data |
| R6 | Training | Gradient descent on XOR with a configurable hidden size, learning rate, steps; record loss and accuracy per step; multiple seeds |
| R7 | Convergence study | For hidden sizes `{2, 3, 4, 8}` and ≥ 20 seeds: fraction of runs reaching 100% accuracy within a step budget, median steps, failure patterns (stuck plateaus); **report honestly**, including runs that fail |
| R8 | Bug-injection suite | ≥ 8 injected backprop bugs (overwrite instead of accumulate, missing `1/n`, wrong `tanh′`, transposed `W2`, wrong bias axis, post- vs pre-activation, sign flip, missing fan-out path); each flagged by the checker; detection table |
| R9 | Gradient accumulation | Demonstrate micro-batch accumulation: summing gradients over 4 single-sample passes equals the full-batch gradient (with the `1/n` handled); and the failure when `zero_grad` is forgotten |
| R10 | Initialization-scale experiment | Per-layer gradient norms and per-unit saturation fraction (`|tanh| > 0.99`) vs initial weight scale (e.g., `0.1 … 10`). **Do not assume the outcome:** in a seeded run of this starter code the total gradient norms *grew* with scale (tiny weights give tiny gradients because gradients are products of small weights), so "large weights make gradients vanish" was not what the network showed. Report what you measure, and relate it to Module 05 vanishing gradients and 4C-07 initialization |
| R11 | Cost accounting | Count forward passes: backprop (1 forward + 1 backward) vs finite differences (`2p` forwards); table for several `h` |
| R12 | Report | `REPORT.md`: agreement table, detection matrix, convergence statistics, saturation plot, and a short "how I would debug a wrong gradient" runbook |

### 9.3 Layout and starter

```
tinybp/
├── pyproject.toml  requirements.txt  README.md  DERIVATION.md  REPORT.md
├── src/tinybp/{__init__,network,scalar_bp,value,gradcheck,bugs,train}.py
├── tests/{test_agreement,test_training,test_bugs,test_accumulation}.py
├── notebooks/07_backprop_tiny_network.ipynb
└── results/
```

```python
# src/tinybp/network.py
import numpy as np

def init_params(d=2, h=3, seed=0, scale=0.5):
    g = np.random.default_rng(seed)
    return {"W1": g.normal(scale=scale, size=(d, h)), "b1": np.zeros(h),
            "w2": g.normal(scale=scale, size=(h, 1)), "b2": np.zeros(1)}

def forward(P, X):
    Z1 = X @ P["W1"] + P["b1"]            # (n, h)
    H = np.tanh(Z1)
    z2 = H @ P["w2"] + P["b2"]            # (n, 1)
    return Z1, H, z2

def loss(P, X, y):
    _, _, z2 = forward(P, X); z = z2.ravel()
    return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))))   # stable BCE with logits

def backward(P, X, y):
    n = len(X); Z1, H, z2 = forward(P, X)
    p = 1 / (1 + np.exp(-z2.ravel()))
    dz2 = ((p - y) / n)[:, None]                              # (n, 1)
    dw2, db2 = H.T @ dz2, dz2.sum(0)                          # (h, 1), (1,)
    dH = dz2 @ P["w2"].T                                      # (n, h)
    dZ1 = dH * (1 - H ** 2)                                   # tanh'
    dW1, db1 = X.T @ dZ1, dZ1.sum(0)                          # (d, h), (h,)
    return {"W1": dW1, "b1": db1, "w2": dw2, "b2": db2}

XOR_X = np.array([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
XOR_Y = np.array([0., 1., 1., 0.])
```

```python
# src/tinybp/gradcheck.py
import numpy as np

def flatten(P): return np.concatenate([P[k].ravel() for k in sorted(P)])
def unflatten(v, like):
    out, i = {}, 0
    for k in sorted(like):
        n = like[k].size; out[k] = v[i:i + n].reshape(like[k].shape); i += n
    return out

def numeric_grads(loss_fn, P, h=1e-5):
    v = flatten(P); g = np.zeros_like(v)
    for i in range(v.size):
        s = h * max(1.0, abs(v[i])); up, dn = v.copy(), v.copy(); up[i] += s; dn[i] -= s
        g[i] = (loss_fn(unflatten(up, P)) - loss_fn(unflatten(dn, P))) / (2 * s)
    return unflatten(g, P)

def rel_error(A, B, eps=1e-12):
    a, b = flatten(A), flatten(B)
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(a) + np.linalg.norm(b), eps))
```

```python
# tests/test_agreement.py
import numpy as np
from tinybp import network as N
from tinybp.gradcheck import numeric_grads, rel_error

def test_vectorized_matches_finite_differences():
    for seed in range(20):
        rng = np.random.default_rng(seed)
        X, y = rng.normal(size=(7, 2)), rng.integers(0, 2, 7).astype(float)
        P = N.init_params(h=3, seed=seed)
        ana = N.backward(P, X, y); num = numeric_grads(lambda Q: N.loss(Q, X, y), P)
        assert rel_error(ana, num) < 1e-6

def test_shapes_equal_parameter_shapes():
    P = N.init_params(h=4); g = N.backward(P, N.XOR_X, N.XOR_Y)
    assert all(g[k].shape == P[k].shape for k in P)
```

```python
# tests/test_training.py
import numpy as np
from tinybp import network as N

def train(h=3, seed=0, eta=0.5, steps=5000):
    P = N.init_params(h=h, seed=seed)
    for _ in range(steps):
        g = N.backward(P, N.XOR_X, N.XOR_Y)
        for k in P: P[k] -= eta * g[k]
    z = N.forward(P, N.XOR_X)[2].ravel()
    return N.loss(P, N.XOR_X, N.XOR_Y), bool(np.all((z > 0) == (N.XOR_Y > 0.5)))

def test_loss_decreases_and_most_seeds_solve_xor():
    results = [train(h=4, seed=s) for s in range(10)]
    assert all(l < 0.69 for l, _ in results)                  # better than chance (ln 2 ≈ 0.693)
    assert sum(ok for _, ok in results) >= 7                  # [VERIFY] threshold from your run
```

`[VERIFY]` The `>= 7 of 10` threshold depends on the architecture, learning rate, and initialization scale; set it from your own convergence study (R7). In a seeded run (η = 0.5, 5,000 full-batch steps, initial scale 0.5, seeds 0–19) XOR was solved by 14/20 runs with 2 hidden units and by 20/20 runs with 3, 4, and 8 hidden units; the failures with 2 units ended with a loss as high as 0.35.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1 | `DERIVATION.md` complete before any code is written (check the commit order); every parameter's gradient derived |
| M2 | R2–R3 | Scalar and vectorized backward agree with finite differences to `< 1e-6` at 20 random inits |
| M3 | R4–R5 | `Value`-based gradients agree with the other three implementations (pairwise table of relative errors) |
| M4 | R6–R7 | XOR training curves; convergence table (hidden size × success rate × median steps) from ≥ 20 seeds, failures reported and explained |
| M5 | R8–R9 | All ≥ 8 injected bugs flagged (`rel_error > 1e-3`); accumulation equivalence verified; the forgot-`zero_grad` bug demonstrated and caught |
| M6 | R10–R12 | Saturation plot, cost table, and `REPORT.md` with the debugging runbook |

### 9.5 Statistical-honesty requirements

- State the number of seeds, learning rate, step budget, and initialization scale for every training claim.
- Report the **fraction of failed runs**, not just the best run, and characterize failures (plateau near `ln 2`, saturated units).
- For gradient agreement, report the **distribution** of relative errors over many initializations, not a single number.
- Say which injected bugs the finite-difference check detects **weakly**, if any, and why.

### 9.6 Failure modes to demonstrate

Overwrite vs accumulate; missing `1/n`; `tanh′` evaluated on pre-activation; transposed `w2`; bias gradient summed over the wrong axis; XOR stuck on a plateau; `float32` precision breaking the agreement test; checking at `x = 0` where symmetric initialization makes hidden units identical (symmetry-breaking: all-zero initial weights give identical gradients for all hidden units); learning rate too high causing oscillation.

### 9.7 Stretch goals

1. A second architecture with ReLU hidden units; show the kink issue in gradient checking and the dead-unit failure.
2. Softmax + cross-entropy head for a 3-class toy problem; derive `p − y` and verify.
3. Minibatch SGD with gradient accumulation; show equivalence to the full batch in the limit.
4. Add L2 regularization and verify the `λW` term in the gradient.
5. Add a directional-derivative check (`∇L·v` vs finite difference along random `v`) as a cheap check for larger networks (preview of Module 05 Project 2 stretch).

### 9.8 ML connection (README prompt)

Explain, using your own results: how reverse mode differs from finite differences in cost, why gradient checks use `float64` and avoid kinks, what symmetric initialization does to hidden units, and which of your injected bugs correspond to real bugs seen in custom layers (Stage 5C-01, 5C-02).

### Check yourself (Unit 9)

1. Why write the derivation before the code?
2. Why can XOR training fail for some seeds with only two hidden units?
3. What does agreement among four independent implementations prove, and what does it not prove?

**Reference answers:** (1) It forces a specification to test against, and a mismatch then points to either the math or the code. (2) The loss has plateaus and poor local structure for tiny hidden layers, so some initializations get stuck near the chance-level loss. (3) It proves the backward pass is consistent with the forward pass's own function; it does not prove the forward pass itself (or the model/loss choice) is right, so forward values need separate tests.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 4 lessons, 2 projects, 9 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 08 and 14, 4C-02/03/07/08/09, and Stage 5 pointers (5C-01/02/03, 5D-06) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: loss-landscape slice conventions, reverse-vs-forward-mode complexity, straight-through estimator guidance, FGSM description.
4. `[VERIFY]` All printed numerical results (iteration counts, success rates, stability thresholds, timings) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, SymPy 1.14): every lesson snippet executed; all 4 `gradplot` and all 3 `tinybp` tests passed. A separate study on the tiny network found: `Value` autodiff vs vectorized backward max relative error ≈ 2e-16 and vectorized vs finite differences ≈ 2e-10 over 20 seeds; all 8 injected bugs were flagged (relative error 1.1e-2 to 7.5e-1, the weakest being `tanh′` evaluated on the pre-activation); micro-batch accumulation equals the full-batch gradient; zero initialization gives exactly zero `W1` gradients and constant initialization gives identical hidden-unit gradients. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, accuracy, success-rate, or tolerance figure appears without the measurement that produced it.
