# SYLLABUS — 14-Linear-Models-Mathematics (S4B-14)

**Stage 4B — Mathematics for Machine Learning · Module 14 · beginner → advanced · the capstone module of the stage**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy and the standard library; SciPy and scikit-learn are **never required** (optional only for cross-checks), Matplotlib and pytest where stated. All datasets are **synthetic and generated in code**, so true coefficients are known and every estimator can be audited. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain. The stage-level `../README.md` shown at the bottom of the project tree is defined separately and is out of scope here.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Linear regression: design matrix and residuals | `01-linear-regression-design-matrix-and-residuals.md` | Beginner → Intermediate |
| 3 | The normal equation and the closed-form solution | `02-the-normal-equation-and-closed-form-solution.md` | Intermediate |
| 4 | Gradient descent vs closed form for linear regression | `03-gradient-descent-versus-closed-form-for-linear-regression.md` | Intermediate |
| 5 | Logistic regression: sigmoid and the log-loss gradient | `04-logistic-regression-sigmoid-and-log-loss-gradient.md` | Intermediate → Advanced |
| 6 | Ridge and lasso regularization mathematics | `05-ridge-and-lasso-regularization-mathematics.md` | Advanced |
| 7 | Practice question bank | `practice-questions.md` | All levels |
| 8 | Project index | `Projects/README.md` | Intermediate |
| 9 | Project: linear regression from scratch in NumPy | `Projects/01-linear-regression-from-scratch-in-numpy.md` | Intermediate → Advanced |
| 10 | Project: logistic regression from scratch | `Projects/02-logistic-regression-from-scratch.md` | Advanced |
| 11 | Project: ridge versus lasso comparison | `Projects/03-ridge-versus-lasso-comparison.md` | Advanced |

**Prerequisites (this module pulls the whole stage together):** Module 01 (projection, norms, L1/L2 balls), Module 02 (matrix products, `solve`, `inv` vs conditioning, rank, collinearity), Module 03 (SVD, `κ`), Module 05 (sigmoid derivatives, stable forms, gradient checks), Module 07 (gradients of least squares and logistic loss), Module 08 (GD, learning rate, conditioning, SGD, losses), Module 09–10 (Gaussian noise, Bernoulli, softmax), Module 12 (standard errors, intervals, cross-validation caveats), Module 13 (cross-entropy, log-loss). **Plan slot:** week 16 of `../00-Stage-4-Overview/learning-plan.md` with the stage mastery gate. **Checkpoints:** your linear-regression coefficients match `np.linalg.lstsq`; your logistic-regression log-loss is within 1% of a reference at equal regularization.

**Teaching stance (industry, not university):** linear and logistic regression are the baselines every ML project starts with and the models whose behaviour you can fully verify. Every formula below is **checked against an independent solver**, every closed form is compared with its iterative counterpart, and every regularizer is shown doing something measurable (shrinking, selecting, stabilizing) with the cases where it does not.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Linear models are where the stage's mathematics becomes a working system: the design matrix (Module 02), the normal equation and projection (Module 01–02), conditioning and the SVD (Module 02–03), gradients and descent (Module 07–08), the Gaussian and Bernoulli likelihoods (Module 10), cross-entropy (Module 13), and standard errors and intervals (Module 12) all appear in a few lines of NumPy. They are also strong baselines in production, interpretable, fast, and the foundation for neural networks (a dense layer is a linear model; the last layer of a classifier is softmax regression).

### 1.2 Outcomes

1. Build a design matrix, fit linear regression four ways (normal equation, QR, SVD/`lstsq`, gradient descent), and show they agree.
2. Explain the fitted values as a projection, the residuals as orthogonal to the features, and read `R²`, leverage, and residual diagnostics.
3. Compute coefficient standard errors and intervals, and verify their coverage by simulation.
4. Diagnose collinearity and ill-conditioning, and choose the right numerical method.
5. Derive and implement logistic regression: sigmoid, log-loss, gradient `Xᵀ(p − y)/n`, Hessian, Newton/IRLS, and understand separability.
6. Derive ridge and lasso, implement ridge by closed form and SVD, lasso by coordinate descent with soft-thresholding, and compare them on dense, sparse, and correlated problems.
7. Choose regularization strength by cross-validation without leakage, and compare models with honest uncertainty (Module 12).

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Design matrix, residuals | Every tabular baseline | Projection and residual checks; `R²`, leverage |
| 2 | Normal equation, closed form | Least squares at scale; conditioning | Four solvers; SEs and CIs |
| 3 | GD vs closed form | Training loops; when `n` or `d` is huge | Steps vs `κ`; SGD; early stopping ≈ ridge |
| 4 | Logistic regression | Classification baselines; softmax heads | Newton vs GD; separability; odds ratios |
| 5 | Ridge and lasso | Regularization, sparsity, weight decay | Shrinkage paths; coordinate descent; selection stability |

### 1.4 Concept map

```
data (X: n×d, y) ──► design matrix [1, X] ──► ŷ = Xw  (fitted values = projection of y onto the column space; residual ⟂ columns)
        │
        ├─ squared error ─► ∇ = Xᵀ(Xw − y)/n = 0 ─► NORMAL EQUATION XᵀXw = Xᵀy ─► solve / QR / SVD (never invert)   κ(XᵀX) = κ(X)²
        │                       └─► gradient descent (rate ∝ κ; Module 08) ◄── early stopping ≈ ridge
        ├─ Bernoulli likelihood ─► log-loss ─► ∇ = Xᵀ(σ(Xw) − y)/n ─► no closed form: GD / Newton (IRLS); separable data ⇒ no finite MLE
        └─ add a penalty:  ridge λ‖w‖² ─► (XᵀX + λI)w = Xᵀy (shrinks along small singular values; always solvable)
                           lasso λ‖w‖₁ ─► soft-thresholding / coordinate descent (exact zeros; L1-ball corners, Module 01)
inference: Var(ŵ) = σ²(XᵀX)⁻¹ ─► SE, CI (Module 12);  Gaussian noise ⇒ MSE = MLE;  Gaussian prior ⇒ ridge (MAP)
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest          # scipy / scikit-learn optional, for cross-checks only
```

Rules for every lab: **compare every from-scratch solver against an independent reference** (`np.linalg.lstsq`, a finite-difference gradient, the closed-form special case); **standardize features inside the training fold only** (leakage otherwise); never form `inv(XᵀX)` where `solve`/`lstsq` works; report **test** error with an interval over seeds or a bootstrap, never training error alone; seed all randomness; state the loss scaling (`1/n`, `1/(2n)`, or sum) because it changes the meaning of `λ` and the learning rate.

### 1.6 Checkpoints (from the stage plan)

- Your linear-regression coefficients match `np.linalg.lstsq` to `1e-8` on 50 random problems, and your standard errors give 95% intervals with empirical coverage within sampling error of 0.95.
- Your logistic-regression log-loss is within 1% of a reference solution at equal regularization, and your gradient passes the Module 05 checker.
- Stage mastery gate item 3 (from `../00-Stage-4-Overview/learning-plan.md`): derive and implement the gradient of the regularized logistic loss, verify it numerically, and fit it on synthetic data, with a gradient-check error below `1e-6` and held-out performance above a baseline you predicted before fitting.

### Check yourself (Unit 1)

1. Which two earlier-module results combine to show that least-squares residuals are orthogonal to every feature?
2. Why must standardization be fitted on the training split only?

**Reference answers:** (1) Projection onto a column space leaves a residual orthogonal to it (Module 01 Lesson 3), and the normal equation `Xᵀ(y − Xw) = 0` is exactly that condition (Module 02). (2) Using test statistics in preprocessing leaks information about the test set into training and inflates the measured performance.

---

## Unit 2 — Linear regression: design matrix and residuals (`01-…md`)

### 2.1 Why ML needs this

Linear regression is the default baseline for any numeric target and the template for every "feature matrix times weights" model. Getting the design matrix, the shapes, and the interpretation of residuals right is most of the battle.

### 2.2 Intuition

Predict the target as a weighted sum of the features plus an intercept. Fitting means choosing weights so the predictions are as close as possible (in squared error) to the targets. Geometrically, `y` is a vector in `ℝⁿ`; the model can only produce vectors in the span of the feature columns; the best fit is the **projection** of `y` onto that span, and the leftover **residual** is perpendicular to it.

### 2.3 Mechanics

- **Model:** `ŷᵢ = w₀ + w₁xᵢ₁ + … + w_d xᵢ_d`; in matrix form `ŷ = Xw` with the **design matrix** `X ∈ ℝ^{n×p}` (`p = d + 1`, first column all ones for the intercept), `w ∈ ℝᵖ`.
- **Residuals:** `r = y − Xw`. **Loss:** `L(w) = (1/2n)‖r‖²` (mean squared error up to the factor `½`; state the convention).
- **Projection view:** at the optimum `ŷ = Hy` with the **hat matrix** `H = X(XᵀX)⁻¹Xᵀ` (symmetric, idempotent `H² = H`, `trace(H) = p`); residual `r = (I − H)y ⟂` every column of `X`.
- **Orthogonality consequences:** `Xᵀr = 0`; with an intercept column, **residuals sum to zero**; residuals are uncorrelated with each fitted value and with each feature.
- **Leverage:** `hᵢᵢ = Hᵢᵢ ∈ [0, 1]`, `Σhᵢᵢ = p`; points far from the feature centroid have high leverage and pull the fit. **Cook's distance** combines leverage and residual size to flag influential points `[VERIFY: formula `Dᵢ = rᵢ²hᵢᵢ/(p s²(1−hᵢᵢ)²)`]`.
- **Goodness of fit:** `R² = 1 − SSR/SST` where `SSR = Σrᵢ²`, `SST = Σ(yᵢ − ȳ)²`; `R² ∈ [0, 1]` on the training data (with an intercept) and never decreases when features are added; **adjusted** `R² = 1 − (SSR/(n−p))/(SST/(n−1))` penalizes extra features; **test-set `R²` can be negative** (worse than predicting the training mean).
- **Feature engineering within a linear model:** polynomial and interaction terms (still linear *in the weights*), one-hot encoding with one level dropped (the **dummy-variable trap**: a full set of dummies plus an intercept is exactly collinear, Module 02 Lesson 9), standardization (puts coefficients on a comparable scale; does not change predictions when unpenalized).
- **Interpreting coefficients:** `wⱼ` is the change in the prediction per unit of feature `j` holding the others fixed; with correlated features individual coefficients are unstable even when predictions are fine; association, not causation (Module 12 Lesson 7).
- **Noise model:** `y = Xw* + ε`, `ε ~ N(0, σ²)` independent ⇒ least squares is the maximum-likelihood estimate (Module 10 Lesson 5).
- **Assumptions behind the *inference* (not the fit):** linearity, independent errors, constant variance (homoscedasticity), roughly normal errors for small-sample intervals. Fitting works without them; the standard errors and intervals do not.
- **Diagnostics (numeric):** residual-vs-fitted correlation (≈ 0 by construction), a heteroscedasticity check (residual magnitude vs fitted), leverage and Cook's distance, and held-out error.

**Worked example:** `x = (1, 2, 3, 4)`, `y = (2, 3, 5, 6)`: slope `1.4`, intercept `0.5`; fitted `(1.9, 3.3, 4.7, 6.1)`, residuals `(0.1, −0.3, 0.3, −0.1)` sum to 0 and are orthogonal to `x` (`0.1 − 0.6 + 0.9 − 0.4 = 0`); `R² = 1 − 0.2/10 = 0.98`.

### 2.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def design(X, intercept=True): X = np.atleast_2d(np.asarray(X, float)); return np.c_[np.ones(len(X)), X] if intercept else X

# --- worked example
x = np.array([1., 2., 3., 4.]); y = np.array([2., 3., 5., 6.]); A = design(x[:, None])
w = np.linalg.lstsq(A, y, rcond=None)[0]; r = y - A @ w; print("w =", w, " fitted =", A @ w, " residuals =", r, " R² =", 1 - r @ r / ((y - y.mean()) ** 2).sum())
assert np.allclose(w, [0.5, 1.4]) and np.isclose(r.sum(), 0) and np.isclose(A[:, 1] @ r, 0)

# --- projection view: hat matrix properties on a random problem
n, d = 80, 4; X = rng.normal(size=(n, d)) * np.array([1, 5, 0.2, 2.0]); w_true = np.array([1.0, 0.5, -2.0, 3.0, 0.7]); A = design(X); y = A @ w_true + rng.normal(scale=1.5, size=n)
Hm = A @ np.linalg.solve(A.T @ A, A.T)
assert np.allclose(Hm, Hm.T) and np.allclose(Hm @ Hm, Hm) and np.isclose(np.trace(Hm), A.shape[1]) and np.all((np.diag(Hm) >= -1e-12) & (np.diag(Hm) <= 1 + 1e-12))
w_hat = np.linalg.lstsq(A, y, rcond=None)[0]; res = y - A @ w_hat
assert np.allclose(A.T @ res, 0, atol=1e-8) and np.allclose(A @ w_hat, Hm @ y) and np.isclose(res.sum(), 0, atol=1e-8)
print("max |leverage|:", np.diag(Hm).max(), " mean leverage p/n =", A.shape[1] / n)

# --- R² vs adjusted R²; adding pure-noise features raises R² but not adjusted R²
def r2(y, yhat): return 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
def adj_r2(y, yhat, p): n = len(y); return 1 - (((y - yhat) ** 2).sum() / (n - p)) / (((y - y.mean()) ** 2).sum() / (n - 1))
for extra in (0, 10, 30):
    Ax = np.c_[A, rng.normal(size=(n, extra))]; wx = np.linalg.lstsq(Ax, y, rcond=None)[0]; yh = Ax @ wx
    print(f"+{extra:2d} noise features: R² {r2(y, yh):.3f}   adjusted R² {adj_r2(y, yh, Ax.shape[1]):.3f}")

# --- the dummy-variable trap: a full set of dummies plus an intercept is rank-deficient
cat = rng.integers(0, 3, n); D = np.eye(3)[cat]; full = np.c_[np.ones(n), D]; drop = np.c_[np.ones(n), D[:, 1:]]
print("rank with all 3 dummies + intercept:", np.linalg.matrix_rank(full), "of", full.shape[1], "| dropping one level:", np.linalg.matrix_rank(drop), "of", drop.shape[1])

# --- standardization changes coefficients' scale, not predictions
mu, sd = X.mean(0), X.std(0, ddof=0); As = design((X - mu) / sd); ws = np.linalg.lstsq(As, y, rcond=None)[0]
assert np.allclose(As @ ws, A @ w_hat); print("raw coefficients:", np.round(w_hat[1:], 3), "| standardized coefficients:", np.round(ws[1:], 3))

# --- polynomial features are linear in the weights; high degree fits training noise
xs = np.sort(rng.uniform(-1, 1, 30)); ys = np.sin(2.5 * xs) + rng.normal(scale=0.2, size=30); xt = np.sort(rng.uniform(-1, 1, 400)); yt = np.sin(2.5 * xt)
for deg in (1, 3, 5, 9, 14):
    P = np.vander(xs, deg + 1); wp = np.linalg.lstsq(P, ys, rcond=None)[0]; print(f"degree {deg:2d}: train MSE {np.mean((P @ wp - ys) ** 2):.4f}   test MSE {np.mean((np.vander(xt, deg + 1) @ wp - yt) ** 2):.4f}")

# --- heteroscedasticity check and a high-leverage point
resid_mag_corr = np.corrcoef(np.abs(res), A @ w_hat)[0, 1]; print("corr(|residual|, fitted):", resid_mag_corr, "(≈ 0 when the variance is constant)")
Xo = np.r_[X, [[15.0, 60.0, 3.0, 20.0]]]; yo = np.r_[y, 0.0]; Ao = design(Xo); Ho = Ao @ np.linalg.solve(Ao.T @ Ao, Ao.T); print("leverage of the far-away point:", Ho[-1, -1])
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting the intercept column | Biased fit; residuals do not sum to zero | Add a ones column (or center `y` and `X`) |
| Dummy-variable trap | Singular `XᵀX`; huge or unstable coefficients | Drop one level or use a penalty (Lesson 5) |
| Judging a model by training `R²` | Overfitting looks great | Held-out error; adjusted `R²`; cross-validation |
| Test `R²` assumed to lie in `[0, 1]` | Confusion at negative values | A negative value means worse than the training mean |
| Interpreting coefficients of correlated features individually | Sign flips between fits | Report predictions or use regularization; check collinearity |
| Extrapolating outside the training feature range | Large errors; high leverage | Check the feature range; flag out-of-range inputs |
| Treating non-constant variance as irrelevant for intervals | Wrong standard errors | Heteroscedasticity-robust SEs `[VERIFY]` or transform the target |
| Fitting with unscaled features and then comparing coefficient sizes | Misleading importance | Standardize for comparison |
| A few high-leverage outliers | Fit driven by single points | Leverage/Cook's distance; robust losses (Module 08 Lesson 1) |
| Standardizing with statistics from the whole dataset | Leakage into the test set | Fit scaling on training data only |

### 2.6 ML link

- **Baseline for tabular regression** and a sanity check for any more complex model (Stage 5A-04).
- **Feature engineering and encoding** (Stage 5A-03): one-hot encoding, polynomial features, standardization.
- **Residual analysis and error analysis** (Stage 5A-12).
- **A dense neural layer is `XW + b`** (Stage 5C-01): everything here applies to it, minus the nonlinearity.
- **Influence and leverage** inform data cleaning and robust training (Module 08 Lesson 1).

### 2.7 Lab (75 min)

1. Reproduce the worked example by hand and in code; verify residual orthogonality and the zero-sum property.
2. Hat-matrix lab: verify symmetry, idempotence, trace `= p`, and leverage bounds on 20 random designs; plot leverage vs distance from the centroid.
3. `R²` lab: add `0…50` pure-noise features; plot training `R²`, adjusted `R²`, and test `R²` vs the number of features.
4. Polynomial lab: train/test error vs degree (average over 50 seeds with standard errors) and the same with 10× the data.
5. Dummy-trap lab: show the rank deficiency, the unstable coefficients, and three fixes (drop a level, `pinv`, ridge).

### Check yourself (Unit 2)

1. What are `XᵀX` and the shape of `X` for `n` samples and `d` features with an intercept?
2. What does `trace(H) = p` tell you?
3. Can test `R²` be negative? What does it mean?

**Reference answers:** (1) `X` is `n × (d + 1)` and `XᵀX` is `(d + 1) × (d + 1)`. (2) The hat matrix projects onto a `p`-dimensional space, so it has `p` unit eigenvalues (the model uses `p` degrees of freedom) and the average leverage is `p/n`. (3) Yes; the model predicts worse than simply using the training-set mean.

---

## Unit 3 — The normal equation and the closed-form solution (`02-…md`)

### 3.1 Why ML needs this

The closed-form solution is the exact optimum of least squares in one linear solve. It is what `np.linalg.lstsq` and `LinearRegression` compute, and understanding *how* they compute it (and how the naive textbook formula fails) is what separates a reliable implementation from one that quietly returns garbage on collinear data.

### 3.2 Intuition

Set the gradient of the squared error to zero. The resulting linear system says the residual must be perpendicular to every feature. Solving it is a linear-algebra problem, and the numerical method (normal equations, QR, SVD) determines how accurate the answer is when the features are nearly collinear.

### 3.3 Mechanics

- **Derivation:** `L(w) = (1/2n)‖y − Xw‖²` ⇒ `∇L = −Xᵀ(y − Xw)/n = 0` ⇒ **`XᵀXw = Xᵀy`** (the *normal equations*; Module 07 Lesson 4). If `X` has full column rank, `XᵀX` is symmetric positive definite and `ŵ = (XᵀX)⁻¹Xᵀy` is the unique minimizer; the loss is convex (Hessian `XᵀX/n ⪰ 0`).
- **Never form the inverse explicitly:** use `np.linalg.solve(XᵀX, Xᵀy)`, or better, avoid `XᵀX` entirely (below).
- **Conditioning:** `κ(XᵀX) = κ(X)²` (Module 02 Lesson 8, Module 03 Lesson 3): forming `XᵀX` squares the condition number and loses about twice as many digits as a method working on `X` directly.
- **Solvers, from fast to robust:**
  - **Normal equations + Cholesky/solve:** `O(nd² + d³)`; fastest, least accurate when `κ` is large.
  - **QR decomposition:** `X = QR`, solve `Rw = Qᵀy` by back-substitution; works with `κ(X)` instead of `κ(X)²` (4C-01).
  - **SVD / `lstsq`:** `X = UΣVᵀ`, `ŵ = VΣ⁺Uᵀy`; most robust, handles rank deficiency (Module 03 Lesson 3); this is the library default.
- **Rank deficiency and collinearity:** if columns are linearly dependent `XᵀX` is singular and the solution is **not unique** (any null-space direction can be added). The **pseudoinverse** gives the **minimum-norm** least-squares solution (Module 03); `np.linalg.lstsq` and `pinv` do this; the normal-equation `solve` raises an error or returns noise.
- **Wide data (`n < d`):** `XᵀX` has rank `≤ n`; the problem is underdetermined; regularization (Lesson 5) or minimum-norm solutions are required.
- **Uncertainty of the coefficients** (under the linear-Gaussian model, Module 12): `Var(ŵ) = σ²(XᵀX)⁻¹`; estimate `σ̂² = SSR/(n − p)`; `SEⱼ = σ̂√[(XᵀX)⁻¹]ⱼⱼ`; the interval `ŵⱼ ± t_{n−p, 0.975}·SEⱼ` (Student-`t`, Module 12 Lesson 1). Highly correlated features make `(XᵀX)⁻¹` large, so individual coefficients have **large standard errors** even when predictions are accurate.
- **Gauss–Markov (outline):** among linear unbiased estimators, least squares has the smallest variance under uncorrelated, equal-variance errors `[VERIFY]`.
- **Cost model:** forming `XᵀX` costs `O(nd²)`, solving `O(d³)`; for `n ≫ d` the first dominates; for very large `d` the cubic term and memory make iterative methods preferable (Lesson 3).
- **Weighted and ridge variants** change only the system: `XᵀWXw = XᵀWy`; `(XᵀX + λI)w = Xᵀy`.

**Worked example (2 features):** `XᵀX = [[4, 2], [2, 3]]`, `Xᵀy = [8, 5]` ⇒ `det = 8`, `ŵ = (1/8)[[3, −2], [−2, 4]]·[8, 5] = (1.75, 0.5)`; check `4(1.75) + 2(0.5) = 8` ✓.

### 3.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

# --- worked 2×2 example
XtX = np.array([[4., 2.], [2., 3.]]); Xty = np.array([8., 5.]); print("w =", np.linalg.solve(XtX, Xty)); assert np.allclose(np.linalg.solve(XtX, Xty), [1.75, 0.5])

# --- four solvers agree on a healthy problem
def solve_normal(A, y): return np.linalg.solve(A.T @ A, A.T @ y)
def solve_qr(A, y): Q, R = np.linalg.qr(A); return np.linalg.solve(R, Q.T @ y)                   # R is upper-triangular (np.linalg.solve is fine for a small demo)
def solve_svd(A, y): U, s, Vt = np.linalg.svd(A, full_matrices=False); return Vt.T @ ((U.T @ y) / s)
def solve_lstsq(A, y): return np.linalg.lstsq(A, y, rcond=None)[0]
n, d = 200, 5; A = np.c_[np.ones(n), rng.normal(size=(n, d))]; w_true = rng.normal(size=d + 1); y = A @ w_true + rng.normal(scale=0.5, size=n)
ref = solve_lstsq(A, y)
for name, f in (("normal", solve_normal), ("QR", solve_qr), ("SVD", solve_svd)): assert np.allclose(f(A, y), ref, atol=1e-9), name

# --- ill-conditioning: a degree-12 polynomial design; normal equations lose twice the digits
x = np.linspace(0, 1, 60); P = np.vander(x, 13, increasing=True); w_star = rng.normal(size=13); yy = P @ w_star           # noiseless, so the true w is recoverable
print("cond(P) =", np.linalg.cond(P), "  cond(PᵀP) =", np.linalg.cond(P.T @ P))
for name, f in (("normal eq.", solve_normal), ("QR", solve_qr), ("SVD", solve_svd), ("lstsq", solve_lstsq)):
    try: print(f"{name:10s} relative error in w: {np.linalg.norm(f(P, yy) - w_star) / np.linalg.norm(w_star):.2e}")
    except np.linalg.LinAlgError as e: print(f"{name:10s} failed: {e}")

# --- collinear features: normal equations break, pinv/lstsq return the minimum-norm solution
Ac = np.c_[np.ones(n), A[:, 1], 2 * A[:, 1] + 0.0]; yc = A[:, 1] * 3 + rng.normal(scale=0.1, size=n)
print("rank:", np.linalg.matrix_rank(Ac), "of 3  cond(AᵀA) =", np.linalg.cond(Ac.T @ Ac))
w_pinv = np.linalg.pinv(Ac) @ yc; w_ls = solve_lstsq(Ac, yc); print("pinv:", w_pinv, " lstsq:", w_ls, " (minimum-norm: the weight is split between the duplicate columns)")
assert np.allclose(w_pinv, w_ls, atol=1e-8) and np.allclose(Ac @ w_pinv, Ac @ (w_pinv + np.array([0, 2, -1]) * 5), atol=1e-8)                     # moving along the null space leaves predictions unchanged

# --- standard errors and 95% intervals; check coverage by simulation (t quantile for n − p = 46 degrees of freedom is ≈ 2.013)
def ols_se(A, y): w = np.linalg.lstsq(A, y, rcond=None)[0]; r = y - A @ w; s2 = r @ r / (len(y) - A.shape[1]); return w, np.sqrt(s2 * np.diag(np.linalg.inv(A.T @ A)))
n, d, reps, t975 = 50, 3, 4000, 2.013; w0 = np.array([1.0, 2.0, -1.0, 0.5]); hit = np.zeros(4)
for _ in range(reps):
    Ar = np.c_[np.ones(n), rng.normal(size=(n, d))]; yr = Ar @ w0 + rng.normal(scale=2.0, size=n); w, se = ols_se(Ar, yr); hit += np.abs(w - w0) <= t975 * se
print("empirical 95% CI coverage per coefficient:", np.round(hit / reps, 3), "(binomial SE ≈ 0.0035)")

# --- correlated features inflate standard errors even though predictions are fine
for rho in (0.0, 0.9, 0.99):
    z = rng.normal(size=(n, 1)); Xc = np.c_[z, rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=(n, 1))]; Ac2 = np.c_[np.ones(n), Xc]; y2 = Xc @ np.array([1.0, 1.0]) + rng.normal(size=n)
    w, se = ols_se(Ac2, y2); print(f"feature correlation {rho}: SE of the two slopes {np.round(se[1:], 3)}   prediction RMSE on the training data {np.sqrt(np.mean((y2 - Ac2 @ w) ** 2)):.3f}")
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.linalg.inv(XᵀX) @ Xᵀy` | Slower, less accurate; fails on collinearity | `solve`, QR, or `lstsq` |
| Normal equations on an ill-conditioned design (polynomials, near-collinear features) | Large error (squared condition number) | QR/SVD; standardize/orthogonalize features |
| Ignoring a rank-deficient design | Non-unique, arbitrary coefficients | Check rank/condition; drop/combine features; ridge |
| `d > n` without regularization | Interpolates the data; unstable | Ridge/lasso or fewer features |
| Reading a large coefficient SE as a bad model | Misdiagnosis | Collinearity inflates SEs; the predictions may be fine |
| Using `z = 1.96` for small `n − p` | Intervals too narrow | Student-`t` quantile (Module 12) |
| Applying the SE formula under feature-linked heteroscedastic or dependent errors | Wrong intervals (slope coverage ≈ 0.77 at `n = 100` in a seeded run) | Robust/clustered SEs `[VERIFY]`; bootstrap (Module 12) |
| Forgetting that `σ̂²` divides by `n − p`, not `n` | Biased variance estimate | Use the degrees-of-freedom correction |
| Fitting on unscaled features then thresholding coefficients | Arbitrary selection | Standardize first |
| Assuming the solution is the same across solvers on near-singular problems | Different outputs | Pin the solver; report the condition number |

### 3.6 ML link

- **Library regression routines** use QR/SVD-based `lstsq` (Stage 5A-04).
- **Closed-form ridge, Gaussian-process regression, and kernel ridge regression** are the same linear solve with a modified matrix (4C-05; Stage 5B-02).
- **Second-order optimization:** a Newton step on a quadratic is exactly a normal-equation solve (Lesson 4, 4C-03).
- **Feature-collinearity monitoring** with condition numbers and standard errors (Stage 5A-12).
- **Linear probing of embeddings** solves a regression on frozen features (Stage 5C-06).

### 3.7 Lab (90 min)

1. Implement the four solvers; verify agreement on 50 random problems (`1e-9`); compare run time and memory for `(n, d) ∈ {(10⁴, 10), (10⁴, 500), (10³, 2000)}` on your machine.
2. Conditioning lab: Vandermonde designs of degree `3…15`; plot relative coefficient error vs `κ(X)` for each solver and identify where the normal equations fail.
3. Collinearity lab: exact duplicates, near-duplicates (`1e-6` noise), and linear combinations; compare `solve`, `lstsq`, `pinv`, and ridge; show the null-space non-uniqueness.
4. Inference lab: verify SEs and 95% intervals by coverage simulation for `n ∈ {10, 30, 100}`; compare `z` vs `t` quantiles at `n = 10`.
5. Heteroscedasticity lab: errors with variance growing with `x`; show the coverage failure of the classical SE and the repair by a bootstrap interval (Module 12).

### Check yourself (Unit 3)

1. State the normal equations.
2. Why is QR preferred over the normal equations for ill-conditioned designs?
3. What does the pseudoinverse solution minimize when `XᵀX` is singular?

**Reference answers:** (1) `XᵀXw = Xᵀy`. (2) Forming `XᵀX` squares the condition number; QR works with `X` directly, so it keeps about twice as many accurate digits. (3) Among all least-squares solutions it has the smallest norm `‖w‖₂`.

---

## Unit 4 — Gradient descent vs closed form for linear regression (`03-…md`)

### 4.1 Why ML needs this

The closed form is exact but cubic in the number of features; gradient descent is approximate but scales to huge `n` and `d`, works online, and is the same algorithm that trains neural networks. Knowing when each wins, and how conditioning and feature scaling decide GD's speed, is the practical bridge from classical regression to deep learning.

### 4.2 Intuition

Both find the bottom of the same bowl. The closed form jumps there in one algebraic step; gradient descent walks downhill step by step. A long thin bowl (badly scaled or correlated features) makes the walk slow, which is exactly what standardization fixes.

### 4.3 Mechanics

- **Gradient descent:** `w ← w − η ∇L(w)`, `∇L = Xᵀ(Xw − y)/n` (Module 07, 08). Stable for `η < 2/L` with `L = λ_max(XᵀX/n)`; convergence factor `max|1 − ηλᵢ|`; iterations to a tolerance scale with the condition number `κ = λ_max/λ_min` (Module 08 Lesson 3).
- **Feature scaling** reduces `κ` dramatically (Module 08 Lesson 3); centering the columns also removes the intercept's coupling with the other features.
- **Cost comparison:** closed form `O(nd² + d³)` once; GD `O(nd)` per step × `k` steps, so GD wins when `d` is large or `n` is huge/streaming, and the closed form wins for moderate `d` and when exactness matters.
- **Stochastic/mini-batch GD:** an unbiased noisy gradient from a batch (Module 08 Lesson 4); with a constant step size it converges to a neighbourhood of `ŵ` (noise floor), with decaying steps to `ŵ`.
- **Newton's method** on a quadratic converges in one step to the normal-equation solution (the Hessian `XᵀX/n` is constant), which is why second-order methods and the closed form coincide here (4C-03).
- **Warm starts and online updates:** previous weights as the starting point; **recursive least squares** and rank-one updates of `(XᵀX)⁻¹` for streaming data (outline) `[VERIFY]`.
- **Early stopping as implicit regularization:** gradient descent started at zero moves first along high-curvature (large-singular-value) directions and only later fits the low-variance directions; stopping after `k` steps behaves like **ridge regression** with `λ ≈ 1/(ηk)` `[VERIFY: approximation]`. Early stopping therefore trades bias for variance without an explicit penalty.
- **When the closed form fails or is impractical:** collinear designs without regularization; `d` in the tens of thousands (memory `d²`); data that do not fit in memory; non-quadratic losses (logistic regression has no closed form, Lesson 4).
- **Convergence diagnostics:** gradient norm, relative loss decrease, and parameter distance to the closed form (available here as a ground truth for debugging an optimizer).

**Worked example:** with `λ_max = 4` and `λ_min = 0.04` (`κ = 100`), the best constant step `η* = 2/(4 + 0.04) = 0.495` gives a contraction factor `(κ − 1)/(κ + 1) = 0.980`; reducing the error by `10⁻⁶` takes about `ln(10⁶)/0.0202 ≈ 684` steps. After standardization `κ` may fall to `~2`, needing `~25` steps.

### 4.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def make_problem(n=2000, d=6, scales=None, seed=0):
    g = np.random.default_rng(seed); X = g.normal(size=(n, d)) * (np.ones(d) if scales is None else scales)
    w = g.normal(size=d); y = X @ w + 0.3 * g.normal(size=n); return X, y, w
def gd(X, y, eta, steps=200_000, tol=1e-10):
    n, d = X.shape; w = np.zeros(d)
    for k in range(steps):
        g = X.T @ (X @ w - y) / n
        if np.linalg.norm(g) < tol: return w, k
        w -= eta * g
    return w, steps

# --- GD reaches the closed form; step from the smoothness constant
X, y, w_true = make_problem(); w_cf = np.linalg.lstsq(X, y, rcond=None)[0]
H = X.T @ X / len(y); lam = np.linalg.eigvalsh(H); eta = 2 / (lam.max() + lam.min()); w_gd, k = gd(X, y, eta)
print(f"κ = {lam.max() / lam.min():.2f}, steps = {k}, ‖w_gd − w_closed‖ = {np.linalg.norm(w_gd - w_cf):.2e}"); assert np.allclose(w_gd, w_cf, atol=1e-6)

# --- iterations vs conditioning: badly scaled features
for name, sc in (("well scaled", None), ("scales 1…10", np.geomspace(1, 10, 6)), ("scales 1…100", np.geomspace(1, 100, 6))):
    Xs, ys, _ = make_problem(scales=sc); Hs = Xs.T @ Xs / len(ys); l = np.linalg.eigvalsh(Hs); _, ks = gd(Xs, ys, 2 / (l.max() + l.min()), steps=2_000_000, tol=1e-8)
    mu, sd = Xs.mean(0), Xs.std(0); Z = (Xs - mu) / sd; lz = np.linalg.eigvalsh(Z.T @ Z / len(ys)); _, kz = gd(Z, ys - ys.mean(), 2 / (lz.max() + lz.min()), steps=2_000_000, tol=1e-8)
    print(f"{name:14s} κ = {l.max() / l.min():9.1f}  GD steps (raw) = {ks:8d} | after standardization κ = {lz.max() / lz.min():.2f}, steps = {kz}")

# --- mini-batch SGD: noise floor with a constant step, convergence with decay
def sgd(X, y, eta0, epochs, batch=32, decay=False, seed=0):
    g = np.random.default_rng(seed); n, d = X.shape; w = np.zeros(d); t = 0
    for _ in range(epochs):
        perm = g.permutation(n)
        for s in range(0, n, batch):
            i = perm[s:s + batch]; eta = eta0 / np.sqrt(1 + t / 50) if decay else eta0; w -= eta * X[i].T @ (X[i] @ w - y[i]) / len(i); t += 1
    return w
Xw, yw, _ = make_problem(n=5000, seed=1); wcf = np.linalg.lstsq(Xw, yw, rcond=None)[0]; l = np.linalg.eigvalsh(Xw.T @ Xw / len(yw))
for name, kw in (("constant η", dict(eta0=0.1)), ("decaying η", dict(eta0=0.1, decay=True))):
    print(f"SGD {name}: ‖w − w_closed‖ after 20 epochs = {np.mean([np.linalg.norm(sgd(Xw, yw, epochs=20, seed=s, **kw) - wcf) for s in range(5)]):.4f}")

# --- Newton's method on a quadratic reaches the solution in ONE step
w0 = rng.normal(size=X.shape[1]); w_newton = w0 - np.linalg.solve(H, X.T @ (X @ w0 - y) / len(y)); assert np.allclose(w_newton, w_cf, atol=1e-9)

# --- early stopping behaves like ridge: compare the GD path with ridge solutions of λ ≈ 1/(η k)
Xr, yr, _ = make_problem(n=300, d=8, scales=np.geomspace(1, 3, 8), seed=2); Hr = Xr.T @ Xr / len(yr); br = Xr.T @ yr / len(yr); lm = np.linalg.eigvalsh(Hr).max(); eta = 1 / lm
w = np.zeros(8); path = {}
for k in range(1, 3001):
    w = w - eta * (Hr @ w - br)
    if k in (10, 30, 100, 300, 1000, 3000): path[k] = w.copy()
for k, wk in path.items():
    lam_eq = 1 / (eta * k); w_ridge = np.linalg.solve(Hr + lam_eq * np.eye(8), br)
    print(f"k={k:5d}: ‖w_GD(k)‖ = {np.linalg.norm(wk):.3f}  ridge(λ=1/(ηk)={lam_eq:.4f}): ‖w‖ = {np.linalg.norm(w_ridge):.3f}   distance between them = {np.linalg.norm(wk - w_ridge):.4f}")   # the match is approximate and weakest early (k = 10: distance ≈ 0.41 with ‖w‖ ≈ 2), tightening as both approach OLS
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Unscaled features with GD | Millions of steps or divergence | Standardize; derive the step from `λ_max` |
| Step size from habit (`1e-3`) | Slow or unstable | Compute `L = λ_max(XᵀX/n)` or run an LR range test (Module 08) |
| Declaring convergence from a small loss change | Stopped far from the optimum | Gradient-norm and parameter-distance criteria; compare with the closed form |
| Using GD where the closed form is cheap and exact | Needless approximation | Closed form for moderate `d` |
| Using the closed form for huge `d` | Memory/time blow-up (`d²`, `d³`) | GD/SGD, conjugate gradient, or low-rank methods |
| SGD with a constant step reported as "converged" | Noise floor | Decay the step or average iterates (Module 08) |
| Thinking early stopping has no regularizing effect | Surprising underfitting/overfitting with epochs | Treat the stopping point as a hyperparameter chosen on validation data |
| Initializing with large weights and comparing with ridge | The equivalence assumes initialization at zero | Start from zero when relying on the early-stopping view |
| Ignoring the intercept's scale | Slow convergence in the intercept direction | Center features and target |

### 4.6 ML link

- **Training loops** are GD/SGD on a loss (Stage 5C-03); linear regression is the one case where the answer is known exactly, so it is the best optimizer test bench.
- **Early stopping as regularization** in neural-network training (Stage 5C-03, 4C-03).
- **Conjugate gradient, L-BFGS, and Newton methods** for larger linear systems and logistic regression (4C-03).
- **Online learning and streaming regression** (Stage 5D-13) use recursive/SGD updates.
- **Learning-rate and conditioning intuition** transfers directly to deep models (Module 08).

### 4.7 Lab (90 min)

1. Implement GD with the step from `λ_max`; verify convergence to `lstsq` on 20 random problems; plot loss and distance-to-solution vs step on a log scale.
2. Conditioning lab: feature-scale ratios `1, 10, 100, 1000`; tabulate `κ`, steps raw vs standardized, and fit steps vs `κ` (log-log).
3. SGD lab: batch sizes `{1, 8, 32, 256}` with constant and decaying steps; compare error vs gradient evaluations (Module 08 Lesson 4).
4. Early-stopping lab: tabulate the distance between the GD path and the ridge path for several `λ`-matching rules; find the best matching constant empirically for a few spectra.
5. Cost lab: time the closed form and GD for `d ∈ {10, 100, 1000, 5000}` at fixed `n`; locate the crossover on your machine (your numbers).

### Check yourself (Unit 4)

1. When does gradient descent beat the closed form?
2. How many Newton steps does least squares need, and why?
3. What is the relationship between early stopping and ridge regression?

**Reference answers:** (1) When `d` is large (cubic cost and `d²` memory of the closed form), `n` is huge or streaming, or the loss is not quadratic. (2) One: the loss is quadratic with constant Hessian `XᵀX/n`, so one Newton step lands on the minimizer. (3) Stopping GD (started at zero) after `k` steps behaves approximately like ridge with `λ ≈ 1/(ηk)`: both shrink the poorly determined (low-variance) directions.

---

## Unit 5 — Logistic regression: sigmoid and the log-loss gradient (`04-…md`)

### 5.1 Why ML needs this

Logistic regression is the standard linear classifier and the template for every neural-network classification head: a linear score, a sigmoid (or softmax), and cross-entropy loss, with the beautifully simple gradient `Xᵀ(p − y)/n`. It is also the first model where there is no closed form, so optimization (and its failure when data are separable) matters.

### 5.2 Intuition

Compute a linear score, squash it to a probability with the sigmoid, and train by making the probabilities assigned to the true labels as large as possible (maximum likelihood = minimum cross-entropy). The decision boundary is where the score is zero, a hyperplane.

### 5.3 Mechanics

- **Model:** `p(y = 1 | x) = σ(w·x + b)`, `σ(z) = 1/(1 + e⁻ᶻ)`; the **logit** `z = ln(p/(1 − p))` is linear in `x`; `σ′ = σ(1 − σ)` (Module 05 Lesson 5).
- **Log-loss (cross-entropy, Module 13 Lesson 3):** `L(w) = −(1/n) Σ [yᵢ ln pᵢ + (1 − yᵢ) ln(1 − pᵢ)]`; stable form from logits: `max(z, 0) − z y + ln(1 + e^{−|z|})`.
- **Gradient (Module 07 Lesson 4):** `∇L = Xᵀ(p − y)/n` with `p = σ(Xw)`; for the bias term the corresponding entry is `mean(p − y)`.
- **Hessian:** `∇²L = Xᵀ S X/n` with `S = diag(pᵢ(1 − pᵢ))`; positive semidefinite ⇒ the loss is **convex**; `S ⪯ ¼I` ⇒ `λ_max(∇²L) ≤ λ_max(XᵀX)/(4n)`, a safe constant step `η = 4n/λ_max(XᵀX)` (Module 08 Lesson 3).
- **No closed form; two standard solvers:**
  - **Gradient descent / SGD / L-BFGS** (Module 08).
  - **Newton's method / IRLS** (iteratively reweighted least squares): `w ← w − (XᵀSX)⁻¹Xᵀ(p − y)`, equivalently solving a *weighted* least-squares problem at each step; **quadratic convergence** (typically 5–10 iterations) but `O(nd² + d³)` per step.
- **Decision boundary:** `w·x + b = 0` (the 0.5-probability contour; a level set, Module 07 Lesson 1); a different threshold `τ` shifts it (`w·x + b = ln(τ/(1 − τ))`).
- **Interpretation:** `e^{wⱼ}` is the **odds ratio** per unit increase of feature `j` (odds multiply by `e^{wⱼ}`); standardized features make coefficients comparable; non-causal (Module 12 Lesson 7).
- **Separable data:** if some `w` separates the classes perfectly, the likelihood increases without bound as `‖w‖ → ∞`: **the unregularized MLE does not exist** and GD's weights grow forever (loss → 0, `‖w‖ ~ ln t`); symptoms: huge coefficients, probabilities of exactly 0/1, Newton failing (singular `S`). **Regularization** (Lesson 5) or early stopping fixes it.
- **Standard errors:** at the (unregularized) MLE, `Var(ŵ) ≈ (XᵀSX)⁻¹` (observed information); Wald intervals `ŵⱼ ± 1.96 SEⱼ` `[VERIFY]` (Module 12).
- **Class imbalance:** accuracy misleads; use log-loss/AUC and tune the **threshold** or class weights; the intercept adapts to the base rate; for prior shift see Module 09 Lesson 3.
- **Calibration:** unregularized logistic regression is typically well calibrated *in-sample* when the model is correctly specified; regularization and misspecification can distort it (Stage 5B-04).
- **Multiclass (softmax regression):** `P = softmax(XW)`, loss `−(1/n) Σ ln P_{i, yᵢ}`, gradient `Xᵀ(P − Y)/n` with one-hot `Y` (Module 10 Lesson 2); binary logistic regression is the 2-class case.
- **Regularized form:** `L(w) + (λ/2)‖w‖²` adds `λw` to the gradient (not on the intercept); this also makes the Hessian `XᵀSX/n + λI` positive definite.

**Worked example:** one feature, weight `w = 1.5`, bias `b = −0.5`, `x = 2`: `z = 2.5`, `p = σ(2.5) = 0.924`; if `y = 1` the loss is `0.0789`, if `y = 0` it is `2.579`; the gradient entries are `(p − y)x = −0.152` (`y = 1`) and `+1.848` (`y = 0`).

### 5.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def sigmoid(z): z = np.asarray(z, float); e = np.exp(-np.abs(z)); return np.where(z >= 0, 1 / (1 + e), e / (1 + e))
def logloss(w, X, y, lam=0.0):                                                       # X includes the intercept column; the intercept is not penalized
    z = X @ w; return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))) + 0.5 * lam * np.sum(w[1:] ** 2))
def grad(w, X, y, lam=0.0): g = X.T @ (sigmoid(X @ w) - y) / len(y); g[1:] += lam * w[1:]; return g
def num_grad(f, w, h=1e-6): return np.array([(f(w + e * h) - f(w - e * h)) / (2 * h) for e in np.eye(len(w))])

# --- worked example
z = 1.5 * 2 - 0.5; p = float(sigmoid(z)); print("p =", p, " loss(y=1) =", -np.log(p), " loss(y=0) =", -np.log(1 - p), " gradient wrt w:", (p - 1) * 2, (p - 0) * 2)

# --- synthetic data with known weights; gradient check
n, d = 3000, 3; Xf = rng.normal(size=(n, d)); w_true = np.array([-0.5, 1.5, -2.0, 1.0]); X = np.c_[np.ones(n), Xf]; y = (rng.random(n) < sigmoid(X @ w_true)).astype(float)
w0 = rng.normal(size=d + 1) * 0.5
for lam in (0.0, 0.1): assert np.allclose(grad(w0, X, y, lam), num_grad(lambda v: logloss(v, X, y, lam), w0), atol=1e-7)

# --- GD with the safe step 4n/λmax(XᵀX), vs Newton / IRLS
def fit_gd(X, y, lam=0.0, steps=100_000, tol=1e-9):
    eta = 4 * len(y) / np.linalg.eigvalsh(X.T @ X).max() / (1 + 0.0); w = np.zeros(X.shape[1])
    for k in range(steps):
        g = grad(w, X, y, lam)
        if np.linalg.norm(g) < tol: return w, k
        w -= eta * g
    return w, steps
def fit_newton(X, y, lam=0.0, max_iter=50, tol=1e-10):
    w = np.zeros(X.shape[1]); R = lam * np.eye(X.shape[1]); R[0, 0] = 0
    for k in range(max_iter):
        p = sigmoid(X @ w); g = grad(w, X, y, lam); S = p * (1 - p); Hs = (X * S[:, None]).T @ X / len(y) + R
        step = np.linalg.solve(Hs, g); w = w - step
        if np.linalg.norm(step) < tol: return w, k + 1
    return w, max_iter
w_gd, k_gd = fit_gd(X, y); w_nt, k_nt = fit_newton(X, y)
print(f"GD: {k_gd} steps, Newton: {k_nt} iterations; ‖w_gd − w_newton‖ = {np.linalg.norm(w_gd - w_nt):.2e}; true w {w_true}, fitted {np.round(w_nt, 3)}")
assert k_nt <= 12 and np.allclose(w_gd, w_nt, atol=1e-4)

# --- Wald standard errors from (XᵀSX)⁻¹ and coverage by simulation
def wald_se(X, w): p = sigmoid(X @ w); S = p * (1 - p); return np.sqrt(np.diag(np.linalg.inv((X * S[:, None]).T @ X)))
hit = np.zeros(d + 1); reps = 600
for _ in range(reps):
    Xr = np.c_[np.ones(500), rng.normal(size=(500, d))]; yr = (rng.random(500) < sigmoid(Xr @ w_true)).astype(float); wr, _ = fit_newton(Xr, yr); hit += np.abs(wr - w_true) <= 1.96 * wald_se(Xr, wr)
print("Wald 95% CI coverage (n = 500):", np.round(hit / reps, 3), "(binomial SE ≈ 0.009)")

# --- odds ratios
print("odds ratios per unit of each feature:", np.round(np.exp(w_nt[1:]), 3), "  true:", np.round(np.exp(w_true[1:]), 3))

# --- separable data: the MLE does not exist; weights grow, loss → 0; L2 regularization gives a finite solution
Xs = np.c_[np.ones(200), np.r_[rng.normal(-2, 0.4, 100), rng.normal(2, 0.4, 100)]]; ys = np.r_[np.zeros(100), np.ones(100)]
w = np.zeros(2); eta = 1.0; hist = []
for k in range(1, 100_001):
    w -= eta * grad(w, Xs, ys)
    if k in (10, 100, 1000, 10_000, 100_000): hist.append((k, float(np.linalg.norm(w)), logloss(w, Xs, ys)))
print("separable data, GD steps → (‖w‖, loss):", [(k, round(nw, 2), f"{l:.2e}") for k, nw, l in hist])
w_reg, _ = fit_newton(Xs, ys, lam=0.01); print("with L2 (λ = 0.01): ‖w‖ =", np.linalg.norm(w_reg), " loss =", logloss(w_reg, Xs, ys, 0.01))

# --- imbalance: accuracy of the majority-class rule vs log-loss; the intercept tracks the base rate
Xi = np.c_[np.ones(20_000), rng.normal(size=(20_000, 2))]; wi = np.array([-4.0, 1.0, 0.5]); yi = (rng.random(20_000) < sigmoid(Xi @ wi)).astype(float)
wf, _ = fit_newton(Xi, yi); print(f"base rate {yi.mean():.3f}; majority-class accuracy {1 - yi.mean():.3f}; fitted intercept {wf[0]:.2f} (true −4)")

# --- softmax regression gradient: Xᵀ(P − Y)/n, checked numerically
K = 3; Wm = rng.normal(size=(d + 1, K)) * 0.3; Y = np.eye(K)[rng.integers(0, K, 400)]; Xm = np.c_[np.ones(400), rng.normal(size=(400, d))]
def sm(Z): Z = Z - Z.max(1, keepdims=True); E = np.exp(Z); return E / E.sum(1, keepdims=True)
def ce(Wf): return float(-np.mean(np.sum(Y * np.log(sm(Xm @ Wf.reshape(d + 1, K))), axis=1)))
g_an = (Xm.T @ (sm(Xm @ Wm) - Y) / 400).ravel(); g_num = num_grad(ce, Wm.ravel()); assert np.allclose(g_an, g_num, atol=1e-7)
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.log(sigmoid(z))` or `log(0)` in the loss | `-inf`, `nan` | Loss from logits (stable form) |
| Missing intercept column or penalizing the intercept | Biased probabilities | Include and exempt the intercept |
| Separable data with no regularization | Exploding weights, `p = 0/1`, singular Hessian | L2/early stopping; check separability |
| Newton without safeguards on bad starts or near-singular `S` | Divergence or `LinAlgError` | Damping/line search; regularize; start from zero |
| Reading accuracy on imbalanced data | "99% accurate" majority class | Log-loss, AUC, precision/recall, threshold tuning |
| Interpreting coefficients on unscaled features | Misleading magnitudes | Standardize or report per-SD odds ratios |
| Using the Wald interval with small `n` or near separation | Poor coverage | Profile-likelihood or bootstrap intervals `[VERIFY]` |
| Treating the logit coefficient as a probability change | Misread effect sizes | Convert to odds ratios or average marginal effects |
| Threshold fixed at 0.5 when costs/prevalence differ | Suboptimal decisions | Choose the threshold on validation data |
| Forgetting the `1/n` in the gradient while using a step derived with it | Divergence or slowness | State the scaling (Module 08) |

### 5.6 ML link

- **The classification baseline** (Stage 5A-05) and the last layer of nearly every classifier (softmax regression; Stage 5C-01).
- **Cross-entropy, calibration, and thresholds** (Module 13; Stage 5A-06, 5B-03/04).
- **Generalized linear models** extend the same recipe (Poisson, Gamma regression; Stage 5A-04, 4C-05).
- **Newton/IRLS** is the classical solver in statistical packages; L-BFGS in ML libraries (4C-03).
- **Weight decay** on classification heads corresponds to the L2 term here (Lesson 5).

### 5.7 Lab (90 min)

1. Implement the stable log-loss, gradient, and Hessian; gradient-check with and without the L2 term on 20 random problems.
2. Compare GD, Newton/IRLS, and mini-batch SGD: iterations, wall time, and final loss vs `n` and `d`; measure Newton's quadratic convergence (log error per iteration).
3. Separability lab: increase class separation until the data become separable; plot `‖w‖` and loss vs step for GD with and without L2; find the `λ` that gives a stable finite solution.
4. Interpretation lab: fit with known `w`; compute odds ratios and Wald intervals; verify coverage by simulation for `n ∈ {100, 500, 5000}`.
5. Threshold lab: vary prevalence and cost ratio; choose the threshold that minimizes expected cost on validation data; compare with 0.5.

### Check yourself (Unit 5)

1. What is the gradient of the mean log-loss with respect to `w`?
2. Why is the unregularized MLE undefined for perfectly separable data?
3. How do you interpret `e^{wⱼ}`?

**Reference answers:** (1) `Xᵀ(σ(Xw) − y)/n`. (2) The likelihood keeps increasing as `‖w‖ → ∞` along a separating direction, so no finite maximizer exists. (3) The multiplicative change in the odds of the positive class per unit increase in feature `j`, holding the others fixed.

---

## Unit 6 — Ridge and lasso regularization mathematics (`05-…md`)

### 6.1 Why ML needs this

With many features, correlated features, or few samples, unregularized fits have huge variance: coefficients swing between datasets and overfit. A penalty on the weight size trades a little bias for a large drop in variance. **Ridge** shrinks all weights smoothly; **lasso** also sets many exactly to zero (feature selection). Both appear everywhere as weight decay, sparsity penalties, and priors.

### 6.2 Intuition

Minimize the usual error *plus* a charge for large weights. The ridge charge (sum of squares) pulls every weight toward zero in proportion to its size; the lasso charge (sum of absolute values) pulls with constant force, so small weights reach exactly zero. Geometrically (Module 01 Lesson 4): the L2 constraint set is a ball with no corners, the L1 constraint set is a diamond whose corners lie on the axes, and the loss contours tend to touch the diamond at a corner.

### 6.3 Mechanics

- **Ridge:** `min_w (1/2n)‖y − Xw‖² + (λ/2)‖w‖²` (intercept unpenalized; standardize features first) ⇒ `(XᵀX/n + λI)w = Xᵀy/n`; always solvable for `λ > 0`; as `λ → 0` approaches (pseudo-inverse) least squares; as `λ → ∞` weights → 0.
  - **SVD view (Module 03):** with `X = UΣVᵀ`, ridge multiplies the least-squares coordinate along singular direction `i` by the shrinkage factor `σᵢ²/(σᵢ² + nλ)` (with the `1/n` convention): directions with small singular values (poorly determined, collinear) are shrunk the most.
  - **Effective degrees of freedom:** `df(λ) = Σ σᵢ²/(σᵢ² + nλ)` (decreases from `p` to `0`).
  - **Bias–variance:** shrinkage adds bias and reduces variance; the optimal `λ > 0` exists when the unregularized variance is large.
  - **Bayesian view:** the ridge solution is the MAP estimate under a zero-mean Gaussian prior on the weights with Gaussian noise (Module 10 Lesson 5) `[VERIFY: λ = σ²/(nτ²) mapping]`.
  - **Weight decay:** adding `λw` to the gradient is the same as the ridge penalty for SGD; with adaptive optimizers the equivalence breaks (decoupled weight decay, Module 08 Lesson 5, 4C-03).
- **Lasso:** `min_w (1/2n)‖y − Xw‖² + λ‖w‖₁`: convex, no closed form in general.
  - **Orthonormal design** (`XᵀX/n = I`): `ŵⱼ = S(ŵⱼ^{OLS}, λ)` with the **soft-thresholding** operator `S(a, λ) = sign(a)·max(|a| − λ, 0)`.
  - **Coordinate descent:** cycle over coordinates, each update the 1-D lasso solution `wⱼ ← S(ρⱼ, λ)/zⱼ`, with `ρⱼ = Xⱼᵀ(r + Xⱼwⱼ)/n`, `zⱼ = XⱼᵀXⱼ/n` and `r = y − Xw`; the objective never increases. **Stop on the KKT violation** (below), not on a small objective decrease per sweep: with correlated features the objective flattens long before the optimality conditions are met.
  - **Optimality (KKT) conditions:** for the solution `ŵ` and residual `r`: `Xⱼᵀr/n = λ·sign(ŵⱼ)` if `ŵⱼ ≠ 0`, and `|Xⱼᵀr/n| ≤ λ` if `ŵⱼ = 0`; useful as a convergence check. The smallest `λ` giving `ŵ = 0` is `λ_max = max_j |Xⱼᵀy|/n` (for centered data).
  - **Regularization path:** `ŵ(λ)` is piecewise linear in `λ`; features enter as `λ` decreases.
  - **Behaviour with correlated features:** lasso tends to keep one or a few members of a correlated group and drop the rest, with *which* members varying across resamples (in the Unit 6 demo it split a 95%-correlated pair unevenly, 1.78 and 1.09), while ridge spreads weight across them (1.40 and 1.40); **elastic net** `λ(α‖w‖₁ + (1−α)‖w‖₂²/2)` combines both `[VERIFY: parameterization]`.
  - **Bias:** lasso shrinks the *selected* weights too; a **relaxed lasso** (refit the selected features by OLS) can reduce that bias at the cost of optimism `[JUDGEMENT]`.
  - **When `p > n`:** lasso selects at most `n` features `[VERIFY]`.
- **Choosing `λ`:** K-fold cross-validation over a log-spaced grid, **standardizing inside each training fold** (preprocessing leakage otherwise); the "one-standard-error rule" picks the largest `λ` within one SE of the best CV error to favour simpler models `[JUDGEMENT]`; remember fold scores are correlated (Module 12 Lesson 4).
- **Feature scaling matters:** penalties act on coefficient size, which depends on the feature's units, so *always* standardize before penalizing (and do not penalize the intercept).
- **Logistic regression with penalties:** add `(λ/2)‖w‖²` or `λ‖w‖₁` to the log-loss; L2 fixes separability (Lesson 4); L1 gives sparse classifiers.
- **Scaling conventions:** with `(1/2n)` loss and `λ` as above, `λ` is comparable across `n`; with a *sum* loss `λ` must grow with `n`; libraries differ (e.g., an inverse `C = 1/λ` convention), so state the form `[VERIFY in your library]`.

**Worked example (orthonormal design):** OLS coefficients `(3.0, −1.2, 0.4, 0.05)`, lasso `λ = 0.5` ⇒ `(2.5, −0.7, 0, 0)`: the two small coefficients are removed, the others shrink by `0.5`.

### 6.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def standardize(X): mu, sd = X.mean(0), X.std(0); return (X - mu) / sd, mu, sd
def ridge(X, y, lam):                                                                      # X standardized, y centered, (1/2n) loss: (XᵀX/n + λI) w = Xᵀy/n
    n, p = X.shape; return np.linalg.solve(X.T @ X / n + lam * np.eye(p), X.T @ y / n)
def soft(a, t): return np.sign(a) * np.maximum(np.abs(a) - t, 0.0)
def kkt_violation(X, y, w, lam):
    """Largest violation of the lasso optimality conditions (0 at the exact solution)."""
    g = X.T @ (y - X @ w) / len(y); nz = w != 0
    return max(float(np.max(np.abs(g[nz] - lam * np.sign(w[nz])), initial=0.0)), float(np.max(np.maximum(np.abs(g[~nz]) - lam, 0.0), initial=0.0)))
def lasso_cd(X, y, lam, iters=50_000, tol=1e-9):
    n, p = X.shape; w = np.zeros(p); r = y.copy(); z = (X ** 2).sum(0) / n
    for it in range(iters):
        for j in range(p):
            rho = X[:, j] @ r / n + z[j] * w[j]; wj = soft(rho, lam) / z[j]; r += X[:, j] * (w[j] - wj); w[j] = wj
        if kkt_violation(X, y, w, lam) < tol: break                       # stop on optimality, not on a small objective decrease (which stalls with correlated features)
    return w

# --- orthonormal design: lasso = soft-thresholded OLS (worked example)
print(soft(np.array([3.0, -1.2, 0.4, 0.05]), 0.5))
Q, _ = np.linalg.qr(rng.normal(size=(500, 6))); Xo = Q * np.sqrt(500); yo = Xo @ np.array([3.0, -1.2, 0.4, 0.05, 0, 0]) + rng.normal(scale=0.3, size=500); yo -= yo.mean()
assert np.allclose(Xo.T @ Xo / 500, np.eye(6), atol=1e-10); w_ols = Xo.T @ yo / 500
for lam in (0.05, 0.2, 0.5): assert np.allclose(lasso_cd(Xo, yo, lam), soft(w_ols, lam), atol=1e-6)

# --- a regression problem with correlated features and a sparse truth
n, p = 150, 20; base = rng.normal(size=(n, p)); X = base.copy(); X[:, 1] = 0.95 * X[:, 0] + 0.05 * rng.normal(size=n); Xs, mu, sd = standardize(X)
w_true = np.zeros(p); w_true[[0, 5, 10]] = [3.0, -2.0, 1.5]; y = Xs @ w_true + rng.normal(size=n); y = y - y.mean()

# --- KKT conditions for the lasso solution
lam = 0.15; w = lasso_cd(Xs, y, lam); g = Xs.T @ (y - Xs @ w) / n
nz = w != 0; assert kkt_violation(Xs, y, w, lam) < 1e-8 and np.allclose(g[nz], lam * np.sign(w[nz]), atol=1e-8) and np.all(np.abs(g[~nz]) <= lam + 1e-8)
print("lasso at λ = 0.15 selects features:", np.nonzero(nz)[0], "(true support: [0, 5, 10])   λ_max =", np.max(np.abs(Xs.T @ y)) / n)

# --- ridge via the SVD shrinkage factors (identical to the direct solve) and effective degrees of freedom
U, s, Vt = np.linalg.svd(Xs, full_matrices=False); lam_r = 0.3
w_svd = Vt.T @ ((s / (s ** 2 + n * lam_r)) * (U.T @ y)); assert np.allclose(w_svd, ridge(Xs, y, lam_r))
for lm in (0.0, 0.01, 0.3, 3.0): print(f"λ = {lm:5}: effective df = {np.sum(s ** 2 / (s ** 2 + n * lm)):6.2f} of {p}   ‖w‖ = {np.linalg.norm(ridge(Xs, y, lm) if lm > 0 else np.linalg.lstsq(Xs, y, rcond=None)[0]):.3f}")

# --- ridge / lasso paths: number of nonzeros and coefficient norm vs λ
for lm in (0.02, 0.05, 0.1, 0.2, 0.4, 0.8): w = lasso_cd(Xs, y, lm); print(f"λ = {lm:4}: lasso nonzeros = {int((np.abs(w) > 1e-10).sum()):2d}   ridge nonzeros = {int((np.abs(ridge(Xs, y, lm)) > 1e-10).sum())} (never exactly zero)")

# --- correlated pair: ridge splits the weight equally; lasso splits it unevenly and, at larger λ, tends to keep only one (features 0 and 1 are 95% correlated copies; true weight on feature 0 only)
w_l, w_r = lasso_cd(Xs, y, 0.1), ridge(Xs, y, 0.1); print("coefficients on the correlated pair (0, 1): lasso", np.round(w_l[:2], 3), "  ridge", np.round(w_r[:2], 3))

# --- cross-validation for λ with standardization INSIDE each fold (no leakage)
def kfold_cv(X, y, lams, fit, K=5, seed=0):
    g = np.random.default_rng(seed); idx = g.permutation(len(y)); folds = np.array_split(idx, K); err = np.zeros((K, len(lams)))
    for k, te in enumerate(folds):
        tr = np.setdiff1d(idx, te); Xtr, mtr, str_ = standardize(X[tr]); ytr = y[tr] - y[tr].mean(); Xte = (X[te] - mtr) / str_
        for j, lm in enumerate(lams): w = fit(Xtr, ytr, lm); err[k, j] = np.mean((y[te] - y[tr].mean() - Xte @ w) ** 2)
    return err
lams = np.geomspace(0.005, 1.0, 12)
for name, fit in (("ridge", ridge), ("lasso", lasso_cd)):
    e = kfold_cv(X, y, lams, fit); m, se = e.mean(0), e.std(0, ddof=1) / np.sqrt(e.shape[0]); j = int(np.argmin(m)); one_se = int(np.max(np.nonzero(m <= m[j] + se[j])[0]))
    print(f"{name}: best λ = {lams[j]:.4f} (CV MSE {m[j]:.3f}); one-SE-rule λ = {lams[one_se]:.4f}")

# --- why scaling matters: unstandardized features are penalized unevenly
Xu = np.c_[rng.normal(size=n) * 100, rng.normal(size=n)]; yu = Xu[:, 0] * 0.05 + Xu[:, 1] * 3 + rng.normal(size=n); yu -= yu.mean()
print("ridge on RAW features (the 100×-scaled feature is almost unpenalized):", np.round(ridge(Xu - Xu.mean(0), yu, 1.0), 4), "| standardized:", np.round(ridge(standardize(Xu)[0], yu, 1.0), 4))
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Penalizing unstandardized features | Arbitrary, scale-dependent shrinkage/selection | Standardize inside each training fold |
| Penalizing the intercept | Biased predictions | Exempt it (center `y`/`X` or leave the ones column unpenalized) |
| Standardizing (or choosing `λ`) with the full dataset | Leakage; optimistic CV | Fit preprocessing within folds |
| Choosing `λ` by training error | `λ → 0` always "wins" | Cross-validation or a validation set |
| Reading lasso support as "the" important features | Unstable under correlation/resampling | Stability selection (selection frequency under bootstrap) `[VERIFY]` |
| Mixing penalty scalings (sum vs mean loss, `C` vs `λ`) across libraries | `λ` off by `n` or inverted | State the objective; convert explicitly |
| Coordinate descent stopped too early | Not converged; wrong support | Duality-gap/KKT check, objective-decrease tolerance |
| Using the one-SE rule without fold-correlation awareness | Overconfident rule | Treat as a heuristic; check stability |
| Assuming ridge selects features | It shrinks but never zeros | Lasso/elastic net for selection |
| Expecting lasso to be unbiased | Shrunk coefficients | Relaxed lasso/refit, or report shrinkage |
| Regularizing a model whose problem is bias, not variance | Worse fit | Diagnose with learning curves (Stage 5A-07) |

### 6.6 ML link

- **Weight decay** (L2) in neural-network training; sparsity penalties and pruning (L1-type) (Stage 5C-03, 5D-10).
- **Regularized linear/logistic baselines** (Stage 5A-04/05) and feature selection (Stage 5B-07).
- **Bayesian priors:** L2 ↔ Gaussian prior, L1 ↔ Laplace prior (4C-05).
- **High-dimensional data** (`p ≫ n`: text, genomics, embeddings) where unregularized fits are impossible (Stage 5A-10).
- **Low-rank/spectral viewpoint:** ridge shrinks small singular directions (Module 03; LoRA-style low-rank adapters in Stage 5C/5D).

### 6.7 Lab (90 min)

1. Implement ridge (direct and SVD forms), soft-thresholding, and lasso by coordinate descent; verify the orthonormal special case and the lasso KKT conditions on 20 problems.
2. Regularization paths: coefficients vs `λ` for ridge and lasso on the correlated-features problem; plot and describe how features enter and shrink.
3. Cross-validated `λ`: implement leak-free K-fold; compare best-`λ` and one-SE-rule models on held-out error over 30 seeds with standard errors.
4. Scaling lab: features with units differing by `10³`; show unequal penalization and its repair.
5. Weight decay lab: show that SGD with an added `λw` gradient term reproduces the ridge solution on a linear model (compare with the closed form).

### Check yourself (Unit 6)

1. Write the ridge closed form.
2. What does soft-thresholding do, and which regularizer produces it?
3. Why must features be standardized before applying a penalty?

**Reference answers:** (1) `ŵ = (XᵀX + λ'I)⁻¹Xᵀy` (with `λ' = nλ` under the `1/n` convention). (2) It shrinks a coefficient toward zero by `λ` and sets it to exactly zero if its magnitude is below `λ`; the L1 (lasso) penalty produces it. (3) The penalty acts on coefficient *size*, which depends on feature units; unscaled features are shrunk unevenly.

---

## Unit 7 — Practice question bank (`practice-questions.md`)

### 7.1 Structure

About 55 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 14 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, shape reasoning, runnable code, and modelling judgement.

### 7.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 7.3 Seed items

**Q1 [L1] Shapes.** `X` is 500 samples × 12 features with an intercept column added. Shapes of `X`, `XᵀX`, `w`? → `(500, 13)`, `(13, 13)`, `(13,)`.
**Q2 [L1] Normal equation.** State it. → `XᵀXw = Xᵀy`.
**Q3 [L2] Residuals.** Why do OLS residuals sum to zero with an intercept? → The intercept column gives `1ᵀr = 0` from `Xᵀr = 0`.
**Q4 [L2] Fit.** Points `(0, 1), (1, 3), (2, 5)`: fitted line and `R²`? → `y = 1 + 2x`, `R² = 1`.
**Q5 [L2] Gradient.** Linear regression loss `(1/2n)‖Xw − y‖²`: gradient? → `Xᵀ(Xw − y)/n`.
**Q6 [L2] Logistic.** `z = 0`: `p`, loss for `y = 1`, gradient factor `p − y`? → `0.5`, `ln 2 = 0.693`, `−0.5`.
**Q7 [L2] Odds ratio.** Coefficient `0.693`. Odds ratio? → `e^{0.693} = 2`.
**Q8 [L2] Ridge.** `XᵀX/n = I`, OLS `ŵ = 2`, ridge `λ = 1`. Ridge coefficient? → `2/(1 + 1) = 1`.
**Q9 [L2] Lasso.** Orthonormal design, OLS `ŵ = (2, −0.3)`, `λ = 0.5`. Lasso? → `(1.5, 0)`.
**Q10 [L3] Debug.** `np.linalg.inv(X.T @ X)` raises `LinAlgError: Singular matrix`. → Collinear or duplicate columns (dummy trap, `d ≥ n`); use `lstsq`/ridge, or drop columns.
**Q11 [L3] Debug.** GD on linear regression diverges at `η = 0.5` but converges at `η = 0.01`. → `η` exceeds `2/λ_max(XᵀX/n)`; standardize and set `η` from `λ_max`.
**Q12 [L3] Debug.** Logistic-regression weights reach `±40` and probabilities are exactly 0/1. → Separable (or nearly) data: the MLE diverges; add L2 or stop early; check for label leakage.
**Q13 [L3] Debug.** CV selects `λ` near 0 for ridge although the model overfits on new data. → Preprocessing leakage (standardization on all data) or duplicated rows across folds; refit scaling inside folds; use group-aware splits.
**Q14 [L3] Analysis.** Two correlated features have coefficients `+8` and `−7.5` and huge standard errors, yet predictions are accurate. → Collinearity: individual coefficients are unidentifiable; use ridge or merge features; do not interpret them separately.
**Q15 [L3] Analysis.** Lasso selects feature A in one bootstrap resample and feature B (a near-copy) in the next. → Selection instability under correlation; use stability selection or elastic net.
**Q16 [L3] Analysis.** Unregularized training `R²` is 0.99, test `R²` is −0.2. → Overfitting (too many features/degree); regularize, reduce features, or add data.
**Q17 [L4] Design.** Choose a method for `n = 10⁶`, `d = 100,000` sparse features, binary target. → L2/L1-regularized logistic regression by SGD/L-BFGS on sparse matrices (no closed form, no `d²` matrix), standardized/scaled features, `λ` by validation, threshold by cost.
**Q18 [L4] Design.** Decide between ridge and lasso for 5,000 correlated genetic features with a few expected causal ones. → Elastic net (sparsity with grouped selection) with stability selection and CV; report selection frequencies; avoid causal claims.
**Q19 [L4] Design.** You need coefficient intervals that are trustworthy with heteroscedastic noise. → Bootstrap (pairs) or heteroscedasticity-robust SEs; check coverage in a simulation matching the noise pattern (Module 12).
**Q20 [L4] Design.** Build a calibration and evaluation plan for a logistic baseline on 2% positives. → Log-loss and AUC with bootstrap intervals, reliability table, threshold chosen from the cost matrix on validation data, stratified splits, prevalence-shift check (Module 09 Lesson 3).

### 7.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Design matrix, residuals | 3 | 2 | 1 | 0 |
| Normal equation, solvers | 3 | 2 | 3 | 1 |
| GD vs closed form | 2 | 2 | 2 | 1 |
| Logistic regression | 3 | 3 | 3 | 2 |
| Ridge and lasso | 3 | 3 | 5 | 2 |

### Check yourself (Unit 7)

1. Why include a "collinear coefficients" item?
2. Which items need runnable code?

**Reference answers:** (1) Misreading unstable individual coefficients is the most common interpretation error in linear models. (2) All L3 items and any whose answer depends on floating-point or simulation behaviour.

---

## Unit 8 — Project index (`Projects/README.md`)

### 8.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Linear regression from scratch in NumPy | Multiple solvers agreeing with a reference, inference, diagnostics, conditioning | 1–3 | 8–9 h |
| 2 | Logistic regression from scratch | Gradient-checked training, Newton vs GD, separability, interpretation, calibration | 4 | 8–9 h |
| 3 | Ridge versus lasso comparison | Regularization mathematics, leak-free CV, selection stability, honest model comparison | 5 | 9–10 h |

Order: 1 → 2 → 3 (each reuses the previous project's solvers and checkers). Outputs feed `mlmath/linmodels.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D13) and notebook `14_linear_models.ipynb`; completing them is the final integration step of the stage and feeds the mastery gate. The code is reused in Stage 5A-04/05.

### 8.2 Data policy

**No downloads.** All data are generated from known models (true coefficients, known noise, known sparsity pattern) so every estimator can be audited against the truth. You may additionally run the tools on tabular data you already have locally; keep it out of the repository and tests `[VERIFY: licence/privacy]`.

### 8.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (agreement with independent solvers/gradients; recovered truth; error rates verified by simulation) | 30 |
| Failure-mode handling (collinearity, separability, ill-conditioning, leakage, scaling) | 15 |
| Reproducibility (seeded, pinned, clean venv, no downloads, preprocessing inside folds) | 15 |
| Explanation and statistical honesty (held-out error with intervals, SEs, CIs with checked coverage, scoped claims) | 15 |
| Code quality (types, shape docstrings, stated loss scaling, no hidden state) | 15 |
| ML connection paragraph | 10 |

### 8.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 8)

1. Why does each project reuse the previous one's code?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The solvers and gradient checkers built in one project become the trusted references for the next. (2) D13 (`mlmath/linmodels.py`).

---

## Unit 9 — Project: Linear regression from scratch in NumPy (`Projects/01-…md`)

### 9.1 Brief

Build `linreg`: a `LinearRegression` class that fits by the normal equation, QR, SVD (`lstsq`-equivalent), full-batch GD, and mini-batch SGD, with optional intercept and standardization; a `summary()` giving standard errors, `t`-statistics, and intervals; and diagnostics (residuals, hat-matrix leverage, Cook's distance, condition number). Validate every solver against `np.linalg.lstsq`, verify the coverage of the reported intervals by simulation, and demonstrate collinearity, ill-conditioning, and overfitting honestly.

**Industry framing:** "I used linear regression" should come with the evidence that the solver is right, the intervals are calibrated, and the failure cases are known. The deliverable is the tested class plus the report that proves it.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Class API | `fit(X, y, method="qr"\|"normal"\|"svd"\|"gd"\|"sgd", fit_intercept=True, standardize=False)`, `predict`, `score` (`R²`), `summary()`; shape and finiteness validation with clear errors |
| R2 | Solvers | Normal equation (`solve`), QR, SVD/pseudoinverse, GD with a step from `λ_max`, SGD with batching and a decaying step; each checked against `np.linalg.lstsq` |
| R3 | Preprocessing | Intercept handling by an unpenalized column; optional standardization **fitted on the training data only** and applied to new data; coefficients reported on the original scale |
| R4 | Inference | `σ̂²`, standard errors `σ̂√diag((XᵀX)⁻¹)`, `t`-statistics, Student-`t` intervals (use the `t_ppf` from Module 12's `inferkit`), `R²` and adjusted `R²` |
| R5 | Diagnostics | Residual vector, fitted values, leverage `diag(H)` computed without forming `H` (via QR), Cook's distance, studentized residuals `[VERIFY]`; heteroscedasticity indicator (corr of `|r|` with fitted); condition number of the design |
| R6 | Coverage audit | ≥ 3,000 simulated datasets: empirical coverage of the 95% interval for every coefficient at `n ∈ {10, 30, 100}` under Gaussian, heavy-tailed (`t₂`), and feature-linked heteroscedastic errors; report with binomial SEs and say which assumption violations actually broke coverage and which did not |
| R7 | Conditioning study | Vandermonde and near-collinear designs: relative coefficient error vs `κ(X)` for each solver; where the normal equation fails |
| R8 | Collinearity | Exact and near duplicates: rank, minimum-norm solution, inflated SEs, and the effect on prediction vs interpretation |
| R9 | Overfitting study | Polynomial degree sweep with train/test error, adjusted `R²`, and K-fold CV; averages over ≥ 30 seeds with SEs |
| R10 | Influence | Inject outliers/high-leverage points; show effects on coefficients; compare OLS with a Huber-loss fit by GD (Module 08 Lesson 1) |
| R11 | Report | `REPORT.md`: solver agreement table, coverage tables with SEs, conditioning plot data, collinearity and overfitting demonstrations, and a "when to trust the coefficients" checklist |

### 9.3 Layout and starter

```
linreg/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/linreg/{__init__,model,solvers,inference,diagnostics,inferkit}.py
├── tests/{test_solvers,test_inference,test_diagnostics}.py
├── notebooks/14_linear_regression.ipynb
└── results/
```

```python
# src/linreg/solvers.py
import numpy as np

def solve_normal(A, y): return np.linalg.solve(A.T @ A, A.T @ y)
def solve_qr(A, y): Q, R = np.linalg.qr(A); return np.linalg.solve(R, Q.T @ y)
def solve_svd(A, y, rcond=1e-12):
    U, s, Vt = np.linalg.svd(A, full_matrices=False); keep = s > rcond * s.max(); return Vt.T[:, keep] @ ((U.T @ y)[keep] / s[keep])
def solve_gd(A, y, steps=500_000, tol=1e-10):
    n = len(y); lam = np.linalg.eigvalsh(A.T @ A / n); eta = 2 / (lam.max() + lam.min()) if lam.min() > 1e-12 else 1 / lam.max(); w = np.zeros(A.shape[1])
    for _ in range(steps):
        g = A.T @ (A @ w - y) / n
        if np.linalg.norm(g) < tol: break
        w -= eta * g
    return w
def solve_sgd(A, y, epochs=50, batch=32, eta0=0.05, seed=0):
    g = np.random.default_rng(seed); n = len(y); w = np.zeros(A.shape[1]); t = 0
    for _ in range(epochs):
        perm = g.permutation(n)
        for s in range(0, n, batch):
            i = perm[s:s + batch]; w -= eta0 / np.sqrt(1 + t / 100) * A[i].T @ (A[i] @ w - y[i]) / len(i); t += 1
    return w
SOLVERS = {"normal": solve_normal, "qr": solve_qr, "svd": solve_svd, "gd": solve_gd, "sgd": solve_sgd}
```

```python
# src/linreg/model.py
import numpy as np
from .solvers import SOLVERS

class LinearRegression:
    def __init__(self, method="qr", fit_intercept=True, standardize=False): self.method, self.fit_intercept, self.standardize = method, fit_intercept, standardize
    def _prep(self, X, fit):
        X = np.asarray(X, float)
        if X.ndim != 2 or not np.all(np.isfinite(X)): raise ValueError("X must be a finite 2-D array")
        if self.standardize:
            if fit: self.mu_, self.sd_ = X.mean(0), X.std(0); self.sd_[self.sd_ == 0] = 1.0
            X = (X - self.mu_) / self.sd_
        return np.c_[np.ones(len(X)), X] if self.fit_intercept else X
    def fit(self, X, y):
        y = np.asarray(y, float); A = self._prep(X, fit=True)
        if len(y) != len(A): raise ValueError("X and y have different numbers of rows")
        self.w_ = SOLVERS[self.method](A, y); self.A_, self.y_ = A, y; return self
    def predict(self, X): return self._prep(X, fit=False) @ self.w_
    def score(self, X, y): y = np.asarray(y, float); r = y - self.predict(X); return 1 - r @ r / ((y - y.mean()) ** 2).sum()
    @property
    def coef_original_scale(self):
        w = self.w_.copy()
        if not self.standardize: return w
        b0 = w[0] if self.fit_intercept else 0.0; slopes = w[1:] / self.sd_ if self.fit_intercept else w / self.sd_
        return np.r_[b0 - (slopes * self.mu_).sum(), slopes] if self.fit_intercept else slopes
```

```python
# src/linreg/diagnostics.py
import numpy as np

def leverage(A): Q, _ = np.linalg.qr(A); return (Q ** 2).sum(axis=1)                                 # diag(H) without forming H
def cooks_distance(A, y):
    w = np.linalg.lstsq(A, y, rcond=None)[0]; r = y - A @ w; n, p = A.shape; s2 = r @ r / (n - p); h = leverage(A)
    return (r ** 2 / (p * s2)) * h / (1 - h) ** 2
```

```python
# tests/test_solvers.py
import numpy as np
from linreg.model import LinearRegression
from linreg.diagnostics import leverage, cooks_distance

def problem(seed, n=300, d=5):
    g = np.random.default_rng(seed); X = g.normal(size=(n, d)); w = g.normal(size=d + 1); y = np.c_[np.ones(n), X] @ w + g.normal(scale=0.5, size=n); return X, y

def test_all_solvers_match_lstsq():
    for seed in range(10):
        X, y = problem(seed); A = np.c_[np.ones(len(y)), X]; ref = np.linalg.lstsq(A, y, rcond=None)[0]
        for m, tol in (("normal", 1e-8), ("qr", 1e-8), ("svd", 1e-8), ("gd", 1e-5)): assert np.allclose(LinearRegression(m).fit(X, y).w_, ref, atol=tol), (seed, m)

def test_residuals_orthogonal_and_hat_trace():
    X, y = problem(0); m = LinearRegression("qr").fit(X, y); r = y - m.predict(X)
    assert np.allclose(m.A_.T @ r, 0, atol=1e-8) and np.isclose(leverage(m.A_).sum(), m.A_.shape[1])

def test_standardized_fit_has_identical_predictions_and_recoverable_coefficients():
    X, y = problem(1); a, b = LinearRegression("qr").fit(X, y), LinearRegression("qr", standardize=True).fit(X, y)
    assert np.allclose(a.predict(X), b.predict(X)) and np.allclose(a.w_, b.coef_original_scale, atol=1e-8)

def test_cooks_distance_matches_leave_one_out_refit():
    X, y = problem(2, n=60); A = np.c_[np.ones(60), X]; D = cooks_distance(A, y); w = np.linalg.lstsq(A, y, rcond=None)[0]; r = y - A @ w; s2 = r @ r / (60 - A.shape[1])
    for i in (0, 7, 33):
        keep = np.arange(60) != i; wi = np.linalg.lstsq(A[keep], y[keep], rcond=None)[0]; dw = w - wi
        assert np.isclose(D[i], dw @ A.T @ A @ dw / (A.shape[1] * s2), rtol=1e-6)
```

```python
# tests/test_inference.py
import numpy as np
from linreg.inferkit import t_ppf

def test_confidence_interval_coverage_matches_nominal_for_gaussian_errors():
    g = np.random.default_rng(0); n, d, reps = 30, 2, 2500; w0 = np.array([1.0, 2.0, -1.0]); q = t_ppf(0.975, n - d - 1); hit = np.zeros(3)
    for _ in range(reps):
        A = np.c_[np.ones(n), g.normal(size=(n, d))]; y = A @ w0 + g.normal(scale=2.0, size=n); w = np.linalg.lstsq(A, y, rcond=None)[0]; r = y - A @ w
        se = np.sqrt(r @ r / (n - A.shape[1]) * np.diag(np.linalg.inv(A.T @ A))); hit += np.abs(w - w0) <= q * se
    cov = hit / reps; assert np.all(np.abs(cov - 0.95) < 4 * np.sqrt(0.95 * 0.05 / reps) + 0.005)
```

`[VERIFY]` Copy `inferkit.py` from Module 12 Unit 1 into the package. Confirm the tolerances (`1e-5` for GD; the coverage band) by running the suite over several seeds.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | All solvers match `np.linalg.lstsq` (`1e-8`; GD/SGD within stated tolerances) on 50 random problems; standardization round-trips; invalid inputs rejected |
| M2 | R4–R5 | Standard errors and intervals implemented; leverage and Cook's distance validated against leave-one-out refits |
| M3 | R6 | Coverage tables (3 sample sizes × 3 error types) with binomial SEs; the heteroscedastic/heavy-tailed failures documented and the bootstrap repair shown |
| M4 | R7–R8 | Conditioning and collinearity studies with numbers; the normal equation's failure point identified |
| M5 | R9–R10 | Overfitting curves averaged over ≥ 30 seeds with SEs; influence experiments with the robust fit |
| M6 | R11 | `REPORT.md` regenerated by one script from a clean venv; every claim has `N`, seeds, and an uncertainty |

### 9.5 Statistical-honesty requirements

- Coverage claims are **measured rates ± binomial SE** from simulations; state the error distribution used.
- Test errors are reported as **mean ± SE over seeds**, never as a single split.
- State clearly which results rely on the **linear-Gaussian assumptions** and which survive without them (the point estimates do; the classical intervals do not).
- Include at least one case where the **classical interval fails** and report its measured coverage. In this module's seeded runs the failing case was **feature-linked heteroscedasticity** (noise standard deviation growing with `|x₁|`): the slope on `x₁` had coverage 0.83 / 0.79 / 0.77 at `n = 10 / 30 / 100` (it gets *worse* with `n`, because the standard-error formula is biased, not merely noisy), while the other coefficients stayed near 0.95. **Heavy-tailed `t(2)` errors did not break coverage** at these sample sizes (0.94–0.96), so do not assume they do: measure.

### 9.6 Failure modes to demonstrate

Missing intercept; dummy trap; `inv(XᵀX)` on collinear data; normal equations at `κ ≈ 10⁸`; GD with unscaled features; standardization on all data (leakage); training `R²` as evidence; heteroscedastic errors with classical SEs; a single high-leverage outlier; `d ≥ n`.

### 9.7 Stretch goals

1. Weighted least squares and heteroscedasticity-robust (sandwich) standard errors; compare coverage `[VERIFY: estimator]`.
2. Recursive least squares for streaming updates; verify equality with batch refits.
3. Conjugate gradient solver for large sparse designs.
4. Leave-one-out CV via the hat-matrix shortcut `rᵢ/(1 − hᵢᵢ)`; verify against explicit refits.
5. Prediction intervals vs confidence intervals for the mean; coverage of each.

### 9.8 ML connection (README prompt)

Explain how this class is the baseline for a regression task in your own work: which solver, which preprocessing, which diagnostics you would run before trusting its coefficients or intervals, and what result would make you move to a regularized or nonlinear model.

### Check yourself (Unit 9)

1. How can you compute leverages without forming the `n × n` hat matrix?
2. Why do the classical intervals fail under heteroscedastic errors?
3. Which part of an OLS fit survives violations of the Gaussian-noise assumption, and which does not?

**Reference answers:** (1) With a thin QR factorization `A = QR`, `hᵢᵢ` is the squared norm of row `i` of `Q`. (2) The standard error formula assumes constant error variance; if the variance varies with the features the formula is biased, so coverage departs from nominal. (3) The least-squares point estimates (and their unbiasedness) survive; the exact `t` intervals/tests rely on the noise assumptions (normality, constant variance, independence).

---

## Unit 10 — Project: Logistic regression from scratch (`Projects/02-…md`)

### 10.1 Brief

Build `logreg`: binary and multiclass (softmax) logistic regression with stable log-loss, a gradient verified by finite differences, solvers (GD, mini-batch SGD, Newton/IRLS), optional L2 regularization, Wald standard errors and odds ratios, class-imbalance and threshold handling, and calibration diagnostics. Demonstrate separability, the effect of regularization, and the behaviour of each solver.

**Industry framing:** the logistic baseline is the model other classifiers must beat. The deliverable is a trustworthy implementation, with a gradient check, a convergence analysis, and calibration evidence, that a team could use as the reference baseline.

### 10.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Stable loss and gradient | Loss from logits (never `log(sigmoid)`), analytic gradient `Xᵀ(p − y)/n (+ λw)`, Hessian `XᵀSX/n (+ λI)`; intercept unpenalized; gradient check `< 1e-6` at 50 random points with and without `λ` |
| R2 | Solvers | GD with the safe step `4n/λ_max(XᵀX)`, mini-batch SGD with decay, Newton/IRLS with a damping/line-search safeguard; convergence criteria and stop reasons reported |
| R3 | Convergence study | Iterations to tolerance vs conditioning (raw vs standardized features); Newton's quadratic convergence (log error per iteration); GD vs Newton wall time as `d` grows |
| R4 | Separability | Detect (linear-programming-free check: train until `‖w‖` grows and loss `< 1e-6`); demonstrate divergence of GD and Newton failure; show L2 and early stopping fixes; relation between `λ` and the final weight norm |
| R5 | Inference and interpretation | Wald SEs and intervals, odds ratios per SD; coverage by simulation for `n ∈ {100, 500, 5000}` and near-separation; a profile-likelihood or bootstrap interval for the near-separation case `[VERIFY]` |
| R6 | Evaluation | Log-loss, accuracy, AUC (rank formula, Module 06 Lesson 5), calibration table (reliability bins) and expected calibration error, each with bootstrap intervals (Module 12) |
| R7 | Imbalance and thresholds | Simulate 1–2% positives; compare accuracy, log-loss, AUC, precision/recall; choose the threshold from a cost matrix on validation data; class-weight variant and its effect on calibration; prior-shift correction (Module 09 Lesson 3) |
| R8 | Multiclass | Softmax regression with gradient `Xᵀ(P − Y)/n` verified numerically; binary case equals the 2-class softmax |
| R9 | Comparison with a reference | If scikit-learn is installed, compare coefficients and log-loss at matching regularization (document the `C = 1/λ` and `1/n` conventions); otherwise compare with your Newton solution to 1e-8 |
| R10 | Report | `REPORT.md`: gradient-check table, convergence plots/data, separability demonstration, interval coverage with SEs, imbalance/threshold study, calibration evidence |

### 10.3 Layout and starter

```
logreg/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/logreg/{__init__,core,solvers,inference,metrics}.py
├── tests/{test_gradient,test_solvers,test_separability,test_metrics}.py
├── notebooks/14_logistic_regression.ipynb
└── results/
```

```python
# src/logreg/core.py
import numpy as np

def sigmoid(z): z = np.asarray(z, float); e = np.exp(-np.abs(z)); return np.where(z >= 0, 1 / (1 + e), e / (1 + e))
def loss(w, X, y, lam=0.0):
    z = X @ w; return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))) + 0.5 * lam * np.sum(w[1:] ** 2))
def grad(w, X, y, lam=0.0): g = X.T @ (sigmoid(X @ w) - y) / len(y); g[1:] += lam * w[1:]; return g
def hessian(w, X, lam=0.0):
    p = sigmoid(X @ w); H = (X * (p * (1 - p))[:, None]).T @ X / len(X); R = lam * np.eye(len(w)); R[0, 0] = 0.0; return H + R
```

```python
# src/logreg/solvers.py
import numpy as np
from .core import grad, hessian, loss

def fit_gd(X, y, lam=0.0, steps=200_000, tol=1e-9):
    eta = 4 * len(y) / np.linalg.eigvalsh(X.T @ X).max(); w = np.zeros(X.shape[1])
    for k in range(steps):
        g = grad(w, X, y, lam)
        if np.linalg.norm(g) < tol: return w, "grad_tol", k
        w -= eta * g
    return w, "max_steps", steps

def fit_newton(X, y, lam=0.0, max_iter=100, tol=1e-10):
    w = np.zeros(X.shape[1])
    for k in range(max_iter):
        g = grad(w, X, y, lam); H = hessian(w, X, lam)
        try: step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError: return w, "singular_hessian", k
        t = 1.0; f0 = loss(w, X, y, lam)                                           # backtracking safeguard
        while loss(w - t * step, X, y, lam) > f0 + 1e-12 and t > 1e-8: t /= 2
        w = w - t * step
        if np.linalg.norm(t * step) < tol: return w, "converged", k + 1
    return w, "max_iter", max_iter

def fit_sgd(X, y, lam=0.0, epochs=30, batch=64, eta0=0.5, seed=0):
    g = np.random.default_rng(seed); n = len(y); w = np.zeros(X.shape[1]); t = 0
    for _ in range(epochs):
        perm = g.permutation(n)
        for s in range(0, n, batch):
            i = perm[s:s + batch]; w -= eta0 / np.sqrt(1 + t / 100) * grad(w, X[i], y[i], lam); t += 1
    return w, "epochs", epochs
```

```python
# src/logreg/metrics.py
import numpy as np

def auc(y, score):                                                                  # rank formula (no ties assumed for continuous scores; ties get average rank below)
    order = np.argsort(score, kind="mergesort"); ranks = np.empty(len(score)); ranks[order] = np.arange(1, len(score) + 1)
    uniq, inv, counts = np.unique(score, return_inverse=True, return_counts=True)
    if len(uniq) < len(score):
        sums = np.bincount(inv, weights=ranks); ranks = (sums / counts)[inv]
    n1, n0 = y.sum(), len(y) - y.sum(); return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
def reliability(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1); idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    return [(float(p[idx == b].mean()), float(y[idx == b].mean()), int((idx == b).sum())) for b in range(bins) if (idx == b).any()]
def ece(y, p, bins=10): rows = reliability(y, p, bins); n = len(y); return float(sum(c / n * abs(m - o) for m, o, c in rows))
```

```python
# tests/test_gradient.py
import numpy as np
from logreg.core import grad, loss, sigmoid, hessian
from logreg.solvers import fit_gd, fit_newton

def data(seed, n=500, d=3):
    g = np.random.default_rng(seed); X = np.c_[np.ones(n), g.normal(size=(n, d))]; w = g.normal(size=d + 1); y = (g.random(n) < sigmoid(X @ w)).astype(float); return X, y, w

def num(f, w, h=1e-6): return np.array([(f(w + e * h) - f(w - e * h)) / (2 * h) for e in np.eye(len(w))])

def test_gradient_and_hessian_match_finite_differences():
    for seed in range(20):
        X, y, _ = data(seed); w = np.random.default_rng(100 + seed).normal(size=X.shape[1])
        for lam in (0.0, 0.1):
            assert np.allclose(grad(w, X, y, lam), num(lambda v: loss(v, X, y, lam), w), atol=1e-7)
            Hn = np.array([num(lambda v, j=j: grad(v, X, y, lam)[j], w, 1e-5) for j in range(len(w))]); assert np.allclose(hessian(w, X, lam), Hn, atol=1e-5)

def test_newton_and_gd_agree_and_newton_is_fast():
    X, y, _ = data(3); wn, why, k = fit_newton(X, y); wg, _, _ = fit_gd(X, y)
    assert why == "converged" and k <= 12 and np.allclose(wn, wg, atol=1e-4)
```

```python
# tests/test_separability.py
import numpy as np
from logreg.core import grad, loss
from logreg.solvers import fit_newton

def test_weights_grow_without_regularization_and_stay_finite_with_it():
    g = np.random.default_rng(0); X = np.c_[np.ones(200), np.r_[g.normal(-2, 0.4, 100), g.normal(2, 0.4, 100)]]; y = np.r_[np.zeros(100), np.ones(100)]
    w = np.zeros(2); norms = []
    for k in range(1, 20_001):
        w -= 1.0 * grad(w, X, y)
        if k in (100, 1000, 10_000, 20_000): norms.append(np.linalg.norm(w))
    assert norms[0] < norms[1] < norms[2] < norms[3]                            # keeps growing (≈ logarithmically)
    wr, why, _ = fit_newton(X, y, lam=0.01); assert why == "converged" and np.linalg.norm(wr) < 1.5 * np.linalg.norm(w) and loss(wr, X, y, 0.01) > 0
```

```python
# tests/test_metrics.py
import numpy as np
from logreg.metrics import auc, ece

def test_auc_matches_pairwise_definition_with_ties():
    g = np.random.default_rng(0); y = g.integers(0, 2, 400); s = np.round(g.normal(size=400) + y, 1)
    pos, neg = s[y == 1], s[y == 0]; pairs = ((pos[:, None] > neg[None]).mean() + 0.5 * (pos[:, None] == neg[None]).mean()); assert np.isclose(auc(y, s), pairs)

def test_calibrated_predictions_have_small_ece_and_overconfident_ones_do_not():
    g = np.random.default_rng(1); p = g.random(50_000); y = (g.random(50_000) < p).astype(float)
    assert ece(y, p) < 0.02 and ece(y, np.clip(p * 1.0 + 0.4 * (p - 0.5), 0.001, 0.999)) > 0.05
```

`[VERIFY]` Run the tests over several seeds; the ECE thresholds and the Newton iteration bound depend on data size and conditioning. Add `inference.py` (Wald SEs, odds ratios) per R5.

### 10.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1 | Gradient and Hessian match finite differences (`< 1e-6`/`1e-5`) at 50 random points, with and without `λ`; loss stable for logits of ±1000 |
| M2 | R2–R3 | All three solvers agree (`1e-4` for GD/SGD, `1e-8` Newton vs a second Newton run from a different start); convergence data for raw vs standardized features; Newton ≤ 12 iterations on well-conditioned problems |
| M3 | R4 | Separability demonstrated: growing weights, singular-Hessian failure, and fixes; weight-norm vs `λ` table |
| M4 | R5–R6 | Wald coverage (with SEs) for 3 sample sizes and a near-separated case; metrics with bootstrap intervals; reliability table |
| M5 | R7–R9 | Imbalance/threshold study with a cost matrix; multiclass gradient check; comparison with a reference solution |
| M6 | R10 | `REPORT.md` regenerated by one script; every claim has `N`, seeds, and an uncertainty |

### 10.5 Statistical-honesty requirements

- Report held-out log-loss/AUC/calibration with **bootstrap intervals** (Module 12), and compare solvers on the *same* splits.
- Wald-interval coverage is a **measured rate ± SE**, including the cases where it fails (small `n`, near-separation).
- State the loss scaling and the `λ` convention; show that the comparison with any library uses matching conventions.
- Do not claim calibration from a single reliability plot; report ECE with an interval and the bin counts.

### 10.6 Failure modes to demonstrate

`log(sigmoid(z))` losses; missing/penalized intercept; separable data; unscaled features with GD; Newton with a singular Hessian; accuracy on imbalanced data; fixed 0.5 threshold; Wald intervals at small `n`; odds ratios on unscaled features; class weights silently destroying calibration.

### 10.7 Stretch goals

1. L1-regularized logistic regression by proximal gradient / coordinate descent (preview of Project 3).
2. L-BFGS implementation or comparison `[VERIFY]`.
3. Temperature/Platt scaling to repair calibration after regularization or class weighting `[VERIFY]`.
4. Firth-style bias reduction for rare events / separation `[VERIFY]`.
5. Generalized linear models: Poisson regression with the same IRLS code.

### 10.8 ML connection (README prompt)

Explain how this implementation is the final layer of a neural classifier (linear map → softmax → cross-entropy → `p − y`), which parts of your gradient check carry over to a framework's autograd, and which failure modes (separability, calibration, imbalance) you would monitor first in production.

### Check yourself (Unit 10)

1. Why does Newton's method converge in so few iterations on logistic regression?
2. What is the symptom of separable data in GD training?
3. Why does the intercept not receive an L2 penalty?

**Reference answers:** (1) The loss is smooth and locally almost quadratic near the optimum, so Newton converges quadratically (the error roughly squares each step). (2) The weight norm keeps increasing (roughly logarithmically in the step count) while the loss decays toward zero, with predicted probabilities saturating at 0 and 1. (3) Penalizing it would bias predictions toward a fixed base rate and make the fit depend on the target's arbitrary offset.

---

## Unit 11 — Project: Ridge versus lasso comparison (`Projects/03-…md`)

### 11.1 Brief

Build `regcmp`: ridge (closed form and SVD), lasso and elastic net (coordinate descent with soft-thresholding), regularization paths, leak-free cross-validation for `λ`, and a **controlled comparison** across three regimes: a sparse truth with many irrelevant features, a dense truth with many small effects, and groups of highly correlated features. Measure prediction error, coefficient error, support recovery, and selection stability, with honest uncertainty across seeds.

**Industry framing:** teams choose between ridge, lasso, and elastic net by habit. The deliverable is the evidence for *when each wins* and the diagnostics (selection stability, CV-curve flatness) that tell you which regime you are in.

### 11.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Ridge | Closed form `(XᵀX/n + λI)w = Xᵀy/n` on standardized `X` and centered `y`; SVD form with shrinkage factors; effective degrees of freedom; intercept recovered on the original scale |
| R2 | Lasso | Coordinate descent with soft-thresholding, warm starts along a decreasing `λ` path, convergence by objective decrease **and** KKT residual; `λ_max` computed from the data; handles `p > n` |
| R3 | Elastic net | Coordinate-descent update with the combined penalty; reduces to ridge/lasso at the limits (tested) |
| R4 | Paths | Coefficient paths vs `λ` (log grid of ≥ 50 values) for each method; nonzero counts; effective degrees of freedom |
| R5 | Leak-free CV | `K`-fold (and repeated K-fold) with standardization/centering inside each training fold; best-`λ` and one-SE rules; group-aware variant for clustered rows |
| R6 | Regime experiments | (a) sparse: `n = 100`, `p = 200`, 5 true nonzeros; (b) dense: `n = 200`, `p = 50`, all coefficients small; (c) correlated groups: blocks of 5 features with pairwise correlation 0.9 and one true feature per block; each over ≥ 50 seeds |
| R7 | Metrics | Test MSE (fresh data), coefficient error `‖ŵ − w*‖`, support precision/recall (lasso/elastic net), selection stability (frequency each feature is selected over 200 bootstrap resamples), with mean ± SE over seeds |
| R8 | Bias study | Shrinkage of selected coefficients by lasso; relaxed-lasso refit; effect on test error |
| R9 | Scaling and leakage demos | Unstandardized features; standardizing with all data vs inside folds; measured optimism of the leaky CV |
| R10 | Correctness tests | Orthonormal-design lasso equals soft-thresholded OLS; ridge direct equals SVD; elastic net limits; KKT conditions on random problems; objective monotone decrease in coordinate descent |
| R11 | Report | `REPORT.md`: regime-by-regime tables with SEs, paths, stability plots, the leakage demonstration, and a decision guide "which penalty when" tied to your measured results |

### 11.3 Layout and starter

```
regcmp/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/regcmp/{__init__,penalized,cv,experiments,stability}.py
├── tests/{test_penalized,test_cv,test_stability}.py
├── notebooks/14_ridge_vs_lasso.ipynb
└── results/
```

```python
# src/regcmp/penalized.py
import numpy as np

def standardize(X): mu, sd = X.mean(0), X.std(0); sd = np.where(sd == 0, 1.0, sd); return (X - mu) / sd, mu, sd
def soft(a, t): return np.sign(a) * np.maximum(np.abs(a) - t, 0.0)

def ridge(X, y, lam):
    n, p = X.shape; return np.linalg.solve(X.T @ X / n + lam * np.eye(p), X.T @ y / n)

def ridge_svd(X, y, lam):
    n = len(y); U, s, Vt = np.linalg.svd(X, full_matrices=False); return Vt.T @ ((s / (s ** 2 + n * lam)) * (U.T @ y))

def kkt_violation(X, y, w, lam, alpha=1.0):
    """Largest violation of the elastic-net optimality conditions (alpha = 1 → lasso)."""
    g = X.T @ (y - X @ w) / len(y) - lam * (1 - alpha) * w; nz = w != 0
    return max(float(np.max(np.abs(g[nz] - lam * alpha * np.sign(w[nz])), initial=0.0)), float(np.max(np.maximum(np.abs(g[~nz]) - lam * alpha, 0.0), initial=0.0)))

def elastic_net_cd(X, y, lam, alpha=1.0, w0=None, iters=50_000, tol=1e-9):
    """min (1/2n)‖y − Xw‖² + lam·(alpha‖w‖₁ + (1−alpha)‖w‖²/2).  alpha = 1 → lasso, alpha = 0 → ridge. Stops on the KKT violation, not on a small objective decrease."""
    n, p = X.shape; w = np.zeros(p) if w0 is None else w0.copy(); r = y - X @ w; z = (X ** 2).sum(0) / n
    for _ in range(iters):
        for j in range(p):
            rho = X[:, j] @ r / n + z[j] * w[j]; wj = soft(rho, lam * alpha) / (z[j] + lam * (1 - alpha)); r += X[:, j] * (w[j] - wj); w[j] = wj
        if kkt_violation(X, y, w, lam, alpha) < tol: break
    return w

def lasso_path(X, y, n_lams=50, ratio=1e-3):
    lam_max = np.max(np.abs(X.T @ y)) / len(y); lams = lam_max * np.geomspace(1, ratio, n_lams); w = np.zeros(X.shape[1]); out = []
    for lm in lams: w = elastic_net_cd(X, y, lm, 1.0, w0=w); out.append(w.copy())
    return lams, np.array(out)
```

```python
# src/regcmp/cv.py
import numpy as np
from .penalized import standardize

def kfold_scores(X, y, lams, fit, K=5, seed=0):
    g = np.random.default_rng(seed); idx = g.permutation(len(y)); folds = np.array_split(idx, K); err = np.zeros((K, len(lams)))
    for k, te in enumerate(folds):
        tr = np.setdiff1d(idx, te); Xtr, mu, sd = standardize(X[tr]); ymean = y[tr].mean(); Xte = (X[te] - mu) / sd         # preprocessing fitted INSIDE the fold
        for j, lm in enumerate(lams): err[k, j] = np.mean((y[te] - ymean - Xte @ fit(Xtr, y[tr] - ymean, lm)) ** 2)
    return err

def choose_lambda(err, lams, rule="min"):
    m, se = err.mean(0), err.std(0, ddof=1) / np.sqrt(err.shape[0]); j = int(np.argmin(m))
    return lams[j] if rule == "min" else lams[int(np.max(np.nonzero(m <= m[j] + se[j])[0]))]
```

```python
# tests/test_penalized.py
import numpy as np
from regcmp.penalized import ridge, ridge_svd, elastic_net_cd, soft, standardize, lasso_path, kkt_violation

def test_ridge_direct_equals_svd():
    g = np.random.default_rng(0); X = standardize(g.normal(size=(120, 15)))[0]; y = g.normal(size=120); y -= y.mean()
    for lam in (0.01, 0.3, 5.0): assert np.allclose(ridge(X, y, lam), ridge_svd(X, y, lam), atol=1e-9)

def test_lasso_on_an_orthonormal_design_is_soft_thresholded_ols():
    g = np.random.default_rng(1); Q, _ = np.linalg.qr(g.normal(size=(400, 6))); X = Q * np.sqrt(400); y = X @ np.array([3, -1.2, 0.4, 0.05, 0, 0]) + g.normal(scale=0.3, size=400); y -= y.mean()
    for lam in (0.05, 0.2, 0.5): assert np.allclose(elastic_net_cd(X, y, lam, 1.0), soft(X.T @ y / 400, lam), atol=1e-6)

def test_elastic_net_limits_and_kkt_conditions():
    g = np.random.default_rng(2); X = standardize(g.normal(size=(150, 10)))[0]; y = X[:, 0] * 2 - X[:, 3] + g.normal(size=150); y -= y.mean(); lam = 0.1
    assert np.allclose(elastic_net_cd(X, y, lam, 0.0), ridge(X, y, lam), atol=1e-6)
    w = elastic_net_cd(X, y, lam, 1.0); gr = X.T @ (y - X @ w) / 150; nz = w != 0
    assert kkt_violation(X, y, w, lam) < 1e-8 and np.allclose(gr[nz], lam * np.sign(w[nz]), atol=1e-8) and np.all(np.abs(gr[~nz]) <= lam + 1e-8)

def test_lasso_path_starts_empty_and_grows():
    g = np.random.default_rng(3); X = standardize(g.normal(size=(100, 20)))[0]; y = X[:, 0] * 3 + X[:, 1] + g.normal(size=100); y -= y.mean()
    lams, W = lasso_path(X, y, n_lams=30); counts = (np.abs(W) > 1e-10).sum(1); assert counts[0] == 0 and counts[-1] >= 2 and np.all(np.diff(counts) >= -2)
```

```python
# tests/test_cv.py
import numpy as np
from regcmp.cv import kfold_scores, choose_lambda
from regcmp.penalized import ridge

def test_cv_curve_has_an_interior_minimum_for_a_noisy_problem_and_one_se_is_not_smaller_lambda():
    g = np.random.default_rng(0); n, p = 80, 40; X = g.normal(size=(n, p)); y = X[:, :3] @ np.array([2.0, -1.0, 0.5]) + g.normal(scale=2.0, size=n)
    lams = np.geomspace(1e-3, 10, 20); e = kfold_scores(X, y, lams, ridge, K=5); j = int(np.argmin(e.mean(0))); assert 0 < j < len(lams) - 1
    assert choose_lambda(e, lams, "one_se") >= choose_lambda(e, lams, "min")
```

`[VERIFY]` Confirm tolerances by running the suite over several seeds (the coordinate-descent tolerances and the interior-minimum assertion depend on noise level and sample size). Add `experiments.py` (the three regimes) and `stability.py` (bootstrap selection frequencies).

### 11.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3, R10 | Ridge direct = SVD (`1e-9`); orthonormal-design lasso equals soft-thresholded OLS (`1e-6`); elastic-net limits and KKT conditions hold on 50 random problems; objective decreases monotonically |
| M2 | R4 | Paths regenerated for all methods; nonzero counts and effective degrees of freedom tabulated |
| M3 | R5, R9 | Leak-free CV implemented; the optimism of the leaky version measured with an interval |
| M4 | R6–R7 | Regime tables over ≥ 50 seeds: test MSE, coefficient error, support precision/recall, stability, each mean ± SE; paired differences between methods |
| M5 | R8 | Shrinkage-bias and relaxed-lasso results |
| M6 | R11 | `REPORT.md` regenerated by one script; decision guide cites the regime tables |

### 11.5 Statistical-honesty requirements

- Compare methods on **the same data splits** and report **paired** differences in test MSE with intervals (Module 12 Lesson 4).
- Every table cell has `N` seeds and a standard error; do not rank methods whose intervals overlap.
- State that the regime conclusions apply to the **designed regimes** (sample sizes, correlation, sparsity), not to "lasso in general".
- Include a regime where the **"obvious" choice loses** (for example, lasso underperforming ridge on a dense truth, or ridge matching lasso despite a sparse truth at low signal-to-noise).
- Report selection-stability results alongside the selected sets; a feature selected in 55% of resamples is not "selected".

### 11.6 Failure modes to demonstrate

Unstandardized features; standardization or CV preprocessing with the full dataset; penalized intercept; lasso on correlated groups (unstable support); `λ` chosen by training error; coordinate descent stopped early; mixing penalty scalings across implementations; interpreting lasso support as causal; `p > n` without regularization.

### 11.7 Stretch goals

1. Stability selection with half-sampling and a selection-probability threshold, compared with plain lasso support `[VERIFY: procedure]`.
2. Adaptive lasso and relaxed lasso with measured bias/variance trade-offs `[VERIFY]`.
3. Group lasso for the correlated blocks `[VERIFY: update]`.
4. Logistic regression with L1/L2 (reusing Project 2) and the regularization path of its coefficients.
5. Bayesian ridge: posterior mean/covariance and marginal-likelihood choice of `λ` compared with CV `[VERIFY]`.

### 11.8 ML connection (README prompt)

Relate your findings to practice: weight decay in neural networks (ridge), sparsity-promoting penalties and pruning (lasso-like), embeddings with many correlated dimensions (elastic net/ridge), and how you would decide, from CV-curve shape and selection stability alone, which regime a new dataset is in.

### Check yourself (Unit 11)

1. Why must standardization be done inside each CV fold?
2. In which regime do you expect lasso to beat ridge, and in which the reverse?
3. What does low selection stability tell you about a lasso-selected feature?

**Reference answers:** (1) Statistics computed on all data leak information from the held-out fold into training, making the CV error optimistic. (2) Lasso tends to win when the truth is sparse (few strong features among many irrelevant ones); ridge tends to win, or tie, when many features each carry a small effect (a dense truth). Correlation alone does not decide it: in this module's seeded run, 5-feature blocks with 0.9 correlation and one true feature per block still favoured lasso (test MSE 1.33 vs ridge 1.75). (3) That the selection depends on the particular sample (often because of correlated alternatives), so the feature should not be reported as reliably important.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 5 lessons, 3 projects, 11 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`); the stage-level `../README.md` is out of scope.
2. `[VERIFY]` Cross-references to Modules 01–13, 4C-01/03/05/07, and Stage 5 pointers (5A-03/04/05/06/07/10/12, 5B-02/03/04/07, 5C-01/03/06, 5D-10/13) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: Cook's distance formula, Gauss–Markov statement, early-stopping ↔ ridge `λ ≈ 1/(ηk)` approximation, ridge MAP mapping `λ = σ²/(nτ²)`, lasso support limit (`≤ n` when `p > n`), elastic-net parameterization, the one-standard-error rule, Wald/profile-likelihood intervals for logistic regression, IRLS equivalence, recursive least squares, stability-selection procedure, scikit-learn's `C = 1/λ` and `1/n` conventions.
4. `[VERIFY]` All printed numerical results (coverage, convergence steps, selection frequencies, CV errors) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, pytest 9): every lesson snippet executed; all 5 `linreg`, 5 `logreg`, and 5 `regcmp` tests passed. Defects found and fixed during the run: the coordinate-descent lasso stopped on a small objective decrease and failed the KKT optimality check with correlated features (now stops on the KKT violation, in the lesson code and the project solver); the failure case for the classical OLS intervals was misattributed to heavy tails (see below); and the lasso-vs-ridge description for correlated features was too strong. Measured in seeded runs: (a) solvers: on a degree-12 polynomial design with `κ(X) ≈ 6.8·10⁸`, the normal equations had relative coefficient error 1.50 vs 2.4e-8 (QR), 2.3e-8 (SVD), 1.9e-8 (`lstsq`); with feature correlation 0, 0.9, 0.99 the slope standard errors were about 0.13–0.16, 0.35, 1.0 while the training RMSE stayed near 1; (b) OLS interval coverage (95% nominal, 1,500–3,000 repetitions): Gaussian errors 0.94–0.96 at `n = 10, 30, 100`; heavy-tailed `t₂` errors 0.94–0.96 (no failure at these sizes); feature-linked heteroscedastic errors left the affected slope at 0.828 / 0.792 / 0.766 (worsening with `n`) while the other coefficients stayed near 0.95; (c) GD vs closed form: GD matched `lstsq` to 3e-11; at scale ratios 1 / 10 / 100 between features `κ` was 1.2 / 96 / 9,593 and GD took 8 / 1,130 / 134,782 steps, versus 7–9 steps after standardization; Newton reached the least-squares solution in one step; SGD's distance to the closed form after 20 epochs was 0.034 (constant step) vs 0.005 (decaying); the early-stopping ↔ ridge distance (λ = 1/(ηk)) fell from 0.41 at `k = 10` to 0.003 at `k = 3,000`; (d) logistic regression: Newton needed 7 iterations vs GD's 133; Wald 95% interval coverage was 0.94–0.96 at `n = 100` and `n = 500` and 0.96–0.98 at `n = 60` with a strong signal, where 25 of 800 fits failed or diverged; on separable data `‖w‖` grew from 1.93 to 7.92 across steps 10 to 100,000 (logarithmically) while the loss fell to 6.6e-6, and L2 with `λ = 0.01` gave `‖w‖ = 2.34`; at 4% prevalence accuracy at threshold 0.5 equalled the majority-class rate (0.960) with recall 0.053, AUC was 0.842 and ECE 0.0035; lowering the threshold to 0.05 gave recall 0.680 at precision 0.141; a ×20 class-weighted fit kept AUC 0.842 but its mean predicted probability was 0.287 against a true 0.040 (ECE 0.2465); (e) ridge vs lasso vs elastic net (α = 0.5), 5-fold CV with preprocessing inside folds, `λ` at the CV minimum, 12 seeds each, mean ± SE of test MSE (noise variance 1, so about 1 is the best possible): sparse (`n = 100`, `p = 200`, 5 true) ridge 12.482 ± 0.415, lasso 1.378 ± 0.048, elastic net 2.597 ± 0.190, paired lasso − ridge −11.105 ± 0.388, with lasso selecting 25.2 features on average (support precision 0.236, recall 1.0); dense (`n = 200`, `p = 50`, small effects) ridge 1.291 ± 0.026, lasso 1.307 ± 0.030, elastic net 1.299 ± 0.029, paired lasso − ridge +0.017 ± 0.008, lasso recall 0.935; correlated groups (`n = 100`, `p = 50`, blocks of 5 at correlation 0.9, one true feature per block) ridge 1.747 ± 0.053, lasso 1.331 ± 0.032, elastic net 1.522 ± 0.042, paired lasso − ridge −0.415 ± 0.038, lasso selecting 25.6 features (precision 0.405); (f) not measured in this build and left to the learner per the project requirements: the leaky-vs-leak-free CV optimism, bootstrap selection stability, the relaxed-lasso bias study, and a comparison against scikit-learn. Coordinate descent in the regime runs was capped at 1,500 sweeps with a KKT tolerance of 1e-6. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] Every solver is compared with an independent reference; preprocessing is fitted inside training folds; no coverage, error, or selection claim appears without the measurement that produced it and its uncertainty.
