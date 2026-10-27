# SYLLABUS — 08-Optimization-Fundamentals (S4B-08)

**Stage 4B — Mathematics for Machine Learning · Module 08 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SymPy, Matplotlib, pytest where stated; PyTorch is **optional** and only for cross-checking optimizer conventions). This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Loss functions: MSE, MAE, Huber | `01-loss-functions-mse-mae-and-huber.md` | Beginner |
| 3 | Gradient descent | `02-gradient-descent.md` | Beginner → Intermediate |
| 4 | Learning rate and convergence | `03-learning-rate-and-convergence.md` | Intermediate |
| 5 | Stochastic and mini-batch gradient descent | `04-stochastic-and-mini-batch-gradient-descent.md` | Intermediate |
| 6 | Momentum, RMSprop, and Adam: intuition | `05-momentum-rmsprop-and-adam-intuition.md` | Intermediate → Advanced |
| 7 | Practice question bank | `practice-questions.md` | All levels |
| 8 | Project index | `Projects/README.md` | Intermediate |
| 9 | Project: gradient descent visualizer | `Projects/01-gradient-descent-visualizer.md` | Intermediate → Advanced |
| 10 | Project: optimizer comparison (SGD, momentum, Adam) | `Projects/02-optimizer-comparison-sgd-momentum-adam.md` | Advanced |

**Prerequisites:** Module 05 (derivatives, second derivatives and the `2/a` step-size limit, gradient checking), Module 07 (gradients, level sets, backprop), Module 02–03 (matrix products; eigenvalues for curvature and conditioning). **Plan slot:** weeks 9–10 of `../00-Stage-4-Overview/learning-plan.md`. **Checkpoint:** gradient descent converges on a quadratic; you can produce a divergent run by choosing `η > 2/L` and explain why.

**Scope:** this module teaches the optimizers *as used in practice* and the minimum theory needed to choose and debug them. Convergence proofs, convexity theory, constrained optimization, second-order methods, and full optimizer derivations (Nesterov, AdamW, schedules) are in Stage 4C-03.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Training a model *is* optimization: choose a loss, then repeatedly move parameters downhill. Most failed training runs trace back to this module's topics: a learning rate that is too large or too small, noisy mini-batches, badly scaled features, or an optimizer used with its defaults and no understanding. An engineer who can read a loss curve and say *which* of these is happening saves days of GPU time.

### 1.2 Outcomes

1. Choose between MSE, MAE, and Huber losses for a regression task and justify the choice from outliers, smoothness, and the quantity being estimated (mean vs median).
2. Implement gradient descent with sensible stopping criteria, and verify it against closed-form solutions.
3. Derive and measure the stable learning-rate range and the best constant step on a quadratic, and relate it to curvature and conditioning.
4. Diagnose a loss curve (too small, good, oscillating, diverging, noisy plateau) and propose a fix.
5. Implement SGD and mini-batch SGD, verify the gradient estimate is unbiased, and measure how its variance depends on batch size.
6. Implement momentum, Nesterov, RMSprop, and Adam from scratch; explain what each changes and why Adam's first step is about `η·sign(g)`.
7. Run a fair optimizer comparison (tuned learning rates, multiple seeds, uncertainty) and report results without over-claiming.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | MSE, MAE, Huber | Regression losses, outliers, mean vs median | Losses + gradients; robust line fit |
| 2 | Gradient descent | Linear and logistic regression training | GD with stopping rules and line search |
| 3 | Learning rate and convergence | LR range test, conditioning, schedules preview | Stability/rate experiments |
| 4 | SGD and mini-batch | Every deep-learning training loop | Unbiasedness and variance experiments |
| 5 | Momentum, RMSprop, Adam | Default optimizers in practice | From-scratch optimizers + tests |

### 1.4 Concept map

```
loss ℓ(r): MSE (mean, smooth) / MAE (median, robust, kink) / Huber (hybrid)
      │
      ▼
gradient descent θ ← θ − η∇L  ─►  learning rate: stable iff η < 2/L ; best ≈ 1/L ; conditioning κ = λmax/λmin
      │                                   │
      ├─► stochastic / mini-batch: unbiased noisy ∇, variance ∝ 1/B ─► noise floor, decay η
      │
      └─► fixes for ill-conditioning and noise:
            momentum (accumulate direction) ── RMSprop (per-parameter scale) ── Adam (both + bias correction)
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "sympy>=1.12" matplotlib pytest      # torch optional, for convention cross-checks only
```

Rules for every lab: **compare against a closed form or a trusted reference wherever one exists**; fix seeds and report **mean ± standard error over seeds** for any stochastic claim; tune the learning rate **per optimizer** before comparing; record the step/epoch budget; plot on a log scale for loss; always write down the convention used (loss reduction, momentum form, where `ε` sits).

### 1.6 Checkpoint

On a 2-D quadratic with `λ_max = 25`, your GD converges for `η = 0.07` and diverges for `η = 0.09` (threshold `2/25 = 0.08`), and you can explain each loss curve you produce in one sentence.

### Check yourself (Unit 1)

1. Which two failures of a training run does a learning-rate sweep help distinguish?
2. Why must each optimizer's learning rate be tuned before comparing optimizers?

**Reference answers:** (1) Divergence/oscillation (too large) versus slow progress (too small). (2) Each optimizer has a different good-LR range, so comparing at one shared LR measures LR mismatch rather than optimizer quality.

---

## Unit 2 — Loss functions: MSE, MAE, and Huber (`01-…md`)

### 2.1 Why ML needs this

The loss defines what "good" means, and it determines the optimization problem's smoothness and robustness. For regression, the three workhorses differ in how they treat large residuals, which often decides whether outliers wreck your model.

### 2.2 Intuition

Let the residual be `r = ŷ − y`.

- **MSE** penalizes `r²`: a residual of 10 costs 100×, so outliers dominate. It estimates the **mean**.
- **MAE** penalizes `|r|`: every unit of error costs the same. It estimates the **median**, so it ignores outliers, but its gradient has constant size and a kink at 0.
- **Huber** is quadratic near 0 (smooth, efficient on clean data) and linear in the tails (robust): a compromise controlled by a threshold `δ`.

### 2.3 Mechanics

Per-sample losses and their derivatives with respect to the residual:

| Loss | `ℓ(r)` | `dℓ/dr` | Behaviour |
|---|---|---|---|
| MSE | `r²` | `2r` | Grows linearly with `r`: large errors dominate the gradient |
| MAE | `|r|` | `sign(r)` | Constant magnitude; undefined at 0 (use a subgradient) |
| Huber(`δ`) | `½r²` if `|r| ≤ δ`, else `δ(|r| − ½δ)` | `clip(r, −δ, δ)` | Gradient is **clipped residual**: smooth core, bounded influence |
| Pinball (quantile `τ`) | `τ·max(r', 0) + (1−τ)·max(−r', 0)` with `r' = y − ŷ` | piecewise constant | Estimates the `τ`-quantile (preview) |

- **Convention warning:** Huber's quadratic part is `½r²`, while "MSE" is often `r²` or `½r²`; a factor of 2 changes the effective learning rate. State the convention.
- **Parameter gradient:** `∂L/∂θ = (1/n) Σ (dℓ/dr)ᵢ · ∂ŷᵢ/∂θ`. For a linear model `ŷ = Xw`: `∇_w L = (1/n) Xᵀ ψ(r)` where `ψ = dℓ/dr`. Changing the loss changes only `ψ`: MSE uses `2r`, Huber uses `clip(r, ±δ)`.
- **What each loss estimates (constant model `ŷ = c`):** `argmin_c Σ(yᵢ − c)² = mean(y)`; `argmin_c Σ|yᵢ − c| = median(y)` (any value between the two middle points for even `n`); Huber lies in between and approaches the mean for large `δ` and the median for small `δ`.
- **Influence of an outlier:** the gradient contribution is `∝ r` (MSE, unbounded), `±1` (MAE, bounded), `clip` (Huber, bounded by `δ`).
- **Smoothness:** MSE and Huber are differentiable; Huber's gradient is continuous. MAE is non-differentiable at 0, so GD with a constant step **cannot settle** exactly (it oscillates around the optimum) and needs a decaying step or a subgradient method `[VERIFY: per-method behaviour]`.
- **Choosing `δ`:** in *residual units*, so it depends on target scale; a common practice is `δ ≈ 1.35·σ̂` with `σ̂` a robust scale estimate (e.g., `1.4826·MAD` of residuals) because that gives roughly 95% efficiency under Gaussian noise `[VERIFY: constant and rationale]`.
- **Probabilistic view (preview of 4C-05):** MSE = maximum likelihood under Gaussian noise; MAE = Laplace noise; Huber = a Gaussian core with Laplace tails. The loss is a modelling assumption about the noise.
- **Scale and units:** MSE has squared units; RMSE restores units; MAE is in target units; metrics for reporting need not equal the training loss.
- **Reduction:** `mean` vs `sum` over samples changes the gradient scale by `n` (and therefore the stable `η`).

**Worked example:** `y = (1, 2, 3, 4, 100)`, constant model. MSE minimizer: mean `= 22`. MAE minimizer: median `= 3`. Huber(`δ=1`): `3.0` on a `0.005` grid in a seeded run, i.e. the median here (with `δ` this small relative to the spread, Huber behaves like MAE).

### 2.4 Code

```python
import numpy as np

def mse(r):               return np.mean(r ** 2)
def mae(r):               return np.mean(np.abs(r))
def huber(r, delta=1.0):
    a = np.abs(r); return np.mean(np.where(a <= delta, 0.5 * r ** 2, delta * (a - 0.5 * delta)))

# derivative of the *mean* loss w.r.t. each residual (so ∇_w L = Xᵀ ψ)
def psi_mse(r):           return 2 * r / len(r)
def psi_mae(r):           return np.sign(r) / len(r)
def psi_huber(r, delta=1.0): return np.clip(r, -delta, delta) / len(r)

# --- gradient check (away from the MAE kink)
rng = np.random.default_rng(0)
r = rng.normal(scale=2.0, size=25)
def num_psi(loss, r, h=1e-6):
    g = np.zeros_like(r)
    for i in range(len(r)):
        e = np.zeros_like(r); e[i] = h; g[i] = (loss(r + e) - loss(r - e)) / (2 * h)
    return g
assert np.allclose(psi_mse(r), num_psi(mse, r), atol=1e-8)
assert np.allclose(psi_mae(r), num_psi(mae, r), atol=1e-8)                       # fine as long as no r_i ≈ 0
assert np.allclose(psi_huber(r, 1.5), num_psi(lambda q: huber(q, 1.5), r), atol=1e-8)

# --- which statistic does each loss estimate? (constant model)
y = np.array([1., 2., 3., 4., 100.])
def argmin_const(L, grid=np.linspace(0, 110, 22_001)):
    return grid[np.argmin([L(y - c) for c in grid])]
print("mean", y.mean(), "| argmin MSE", argmin_const(mse))                       # 22
print("median", np.median(y), "| argmin MAE", argmin_const(mae))                 # 3
print("argmin Huber(δ=1)", argmin_const(lambda q: huber(q, 1.0)))                # near the median

# --- robust line fit: GD on each loss with 10% outliers
n = 200
x = rng.uniform(-3, 3, n); y_clean = 2.0 * x + 1.0
y_obs = y_clean + rng.normal(scale=0.3, size=n)
out = rng.choice(n, size=20, replace=False); y_obs[out] += rng.normal(loc=25, scale=5, size=20)   # contaminated
Xd = np.c_[x, np.ones(n)]                                                         # (n, 2): slope, intercept

def fit(psi, steps=20_000, eta=0.05, decay=False):
    w = np.zeros(2)
    for k in range(steps):
        r = Xd @ w - y_obs
        step = eta / np.sqrt(1 + k / 100) if decay else eta
        w -= step * (Xd.T @ psi(r))
    return w
for name, psi, dec in (("MSE", psi_mse, False), ("MAE", psi_mae, True), ("Huber(1.0)", lambda r: psi_huber(r, 1.0), False)):
    print(f"{name:11s} slope, intercept ≈", np.round(fit(psi, decay=dec), 3), "(truth: 2.0, 1.0)")
w_ols = np.linalg.lstsq(Xd, y_obs, rcond=None)[0]
assert np.allclose(fit(psi_mse), w_ols, atol=1e-4)                                # GD on MSE reaches the closed form

# --- Huber threshold from a robust scale estimate
res = Xd @ fit(psi_mse) - y_obs
sigma_hat = 1.4826 * np.median(np.abs(res - np.median(res)))
print("robust σ̂ =", sigma_hat, " δ ≈ 1.35σ̂ =", 1.35 * sigma_hat)

# --- pinball loss estimates a quantile
def pinball(y, yhat, tau):
    d = y - yhat; return np.mean(np.where(d >= 0, tau * d, (tau - 1) * d))
sample = rng.normal(size=20_001)
grid = np.linspace(-3, 3, 1_201)
for tau in (0.1, 0.5, 0.9):
    c = grid[np.argmin([pinball(sample, g, tau) for g in grid])]
    print(tau, c, np.quantile(sample, tau))                                      # argmin ≈ the τ-quantile
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Using MSE on heavy-tailed or contaminated targets | Fit dragged toward outliers | Huber/MAE, or clean/winsorize with justification |
| Using MAE with a constant-step GD | Parameters jitter forever around the optimum | Decaying step, or Huber |
| Huber `δ` chosen in the wrong units | Behaves like MSE (`δ` huge) or MAE (`δ` tiny) | Set from a robust residual scale; re-tune after rescaling `y` |
| Ignoring the factor-2 (or `½`) convention | Learning rate off by 2× when swapping losses | State the convention; check gradients numerically |
| Mean vs sum reduction | Stable `η` shifts by `n` | Fix the reduction, test with the checker |
| Evaluating a model with the training loss only | Metric/loss mismatch | Report the business metric too |
| Gradient check at `r = 0` for MAE | False failure at the kink | Use random continuous residuals |
| Treating median-regression as "better" always | Loses efficiency on clean Gaussian data | Choose by noise model and robustness need |

### 2.6 ML link

- **Regression training** (Stage 5A-04): choosing the loss is choosing what is estimated and how outliers act.
- **Linear models** (Module 14): `∇_w L = Xᵀψ(r)/…`; Huber regression and quantile regression are the same loop with a different `ψ`.
- **Likelihood view** (4C-05): loss = negative log-likelihood of a noise model.
- **Gradient clipping** (Stage 5C-03) is Huber-like: it bounds the influence of large gradients.
- **Uncertainty and quantiles** (Stage 5B-02): pinball loss trains quantile predictors.
- **Classification losses** (cross-entropy) come in Module 13–14.

### 2.7 Lab (75 min)

1. Implement the three losses and their `ψ` functions; gradient-check each (random residuals, avoiding 0 for MAE).
2. Show the mean/median/near-median minimizers for a skewed sample and for the contaminated sample.
3. Robust-line-fit experiment: sweep contamination `{0%, 5%, 10%, 20%}`; plot recovered slope vs contamination for MSE, MAE, Huber; report your numbers.
4. Sweep Huber `δ ∈ {0.1, 0.5, 1, 2, 5, 20}` and show the transition from MAE-like to MSE-like behaviour.
5. Quantile regression: train the pinball loss for `τ ∈ {0.1, 0.5, 0.9}` on heteroscedastic data and check empirical coverage of each quantile line.

### Check yourself (Unit 2)

1. What does MAE estimate for a constant model?
2. What is Huber's `dℓ/dr`?
3. Why can constant-step GD on MAE not converge exactly?

**Reference answers:** (1) The median. (2) The residual clipped to `[−δ, δ]`. (3) Its gradient has constant magnitude near the optimum, so a fixed step keeps overshooting the kink; a decaying step is needed.

---

## Unit 3 — Gradient descent (`02-…md`)

### 3.1 Why ML needs this

Gradient descent is the base algorithm beneath SGD, momentum, and Adam. Every optimizer in this module is a modification of one line: `θ ← θ − η·g`.

### 3.2 Intuition

Stand on a foggy hillside, feel the slope under your feet (the gradient), and take a small step downhill. Repeat. The **learning rate** `η` is the step length; the **stopping rule** is how you decide you have arrived.

### 3.3 Mechanics

- **Update:** `θₖ₊₁ = θₖ − η ∇L(θₖ)`.
- **Algorithm:** initialize `θ₀`; loop: compute gradient; update; check stopping criteria.
- **Stopping criteria** (use several): gradient norm `‖∇L‖ < ε_g`; relative loss decrease `|Lₖ − Lₖ₋₁| < ε_L·(1 + |Lₖ|)`; parameter change `‖θₖ₊₁ − θₖ‖ < ε_θ`; maximum steps. Always keep the max-steps guard, and report *which* criterion fired.
- **First-order guarantee:** for small `η`, `L(θ − η g) ≈ L(θ) − η‖g‖²`: the loss decreases. "Small enough" is set by curvature (Lesson 4).
- **Quadratic case `L = ½θᵀAθ`:** `θₖ = (I − ηA)ᵏ θ₀`. In the eigenbasis each component shrinks by `(1 − ηλᵢ)ᵏ`; the **slowest** component (smallest `λ`) controls the finish, the **largest** `λ` controls stability (Module 03 Lesson 2, Module 05 Lesson 6).
- **Linear regression by GD:** `∇L = Xᵀ(Xw − y)/n`; converges to the least-squares solution (Module 14). With features of very different scale the Hessian `XᵀX/n` is ill-conditioned and GD crawls.
- **Logistic regression by GD:** `∇L = Xᵀ(σ(Xw) − y)/n` (Module 07).
- **Backtracking line search (Armijo):** start from a large `η`; shrink by `β` until `L(θ − ηg) ≤ L(θ) − c·η‖g‖²`. Removes the need to hand-pick `η` for deterministic problems; too costly (extra loss evaluations) and not meaningful for noisy mini-batch losses.
- **Preprocessing matters:** standardizing features reduces the condition number of `XᵀX/n`, often by orders of magnitude.
- **GD only finds a stationary point:** on convex problems a global minimum, on non-convex ones a local minimum or saddle (Module 05 Lesson 7; 4C-03).
- **Cost per step:** one gradient evaluation over the **entire** dataset: `O(nd)` for linear models. That cost is the motivation for stochastic methods (Lesson 5).

**Worked example:** `L(w) = ½(w − 3)²·4`: `g = 4(w − 3)`, `η = 0.1` ⇒ `w ← w − 0.4(w − 3)`, error contracts by `0.6` per step: from `w₀ = 0`, after 10 steps the error is `3·0.6¹⁰ ≈ 0.018`.

### 3.4 Code

```python
import numpy as np

def gradient_descent(grad, x0, eta, steps=10_000, g_tol=1e-8, loss=None, l_tol=None):
    x = np.asarray(x0, float).copy(); hist = {"x": [x.copy()], "loss": [], "gnorm": []}
    why = "max_steps"
    for k in range(steps):
        g = grad(x); gn = np.linalg.norm(g); hist["gnorm"].append(gn)
        if loss is not None: hist["loss"].append(loss(x))
        if gn < g_tol: why = "grad_tol"; break
        if loss is not None and l_tol is not None and k > 0 and abs(hist["loss"][-1] - hist["loss"][-2]) < l_tol * (1 + abs(hist["loss"][-1])):
            why = "loss_tol"; break
        x = x - eta * g; hist["x"].append(x.copy())
        if not np.all(np.isfinite(x)): why = "diverged"; break
    return x, why, k, hist

def backtracking_step(loss, grad, x, eta0=1.0, c=1e-4, beta=0.5, max_halvings=60):
    g = grad(x); f0, eta = loss(x), eta0
    for _ in range(max_halvings):
        if loss(x - eta * g) <= f0 - c * eta * (g @ g): return eta
        eta *= beta
    return eta

# --- quadratic: one-step check of the contraction factor
A = np.diag([1.0, 4.0]); loss = lambda x: 0.5 * x @ A @ x; grad = lambda x: A @ x
x, why, k, _ = gradient_descent(grad, [1.0, 1.0], eta=0.2, steps=500, loss=loss)
print(why, k, np.linalg.norm(x))

# --- linear regression by GD equals the closed form
rng = np.random.default_rng(0)
n, d = 500, 4
X = rng.normal(size=(n, d)); w_true = np.array([1.0, -2.0, 0.5, 3.0]); y = X @ w_true + 0.1 * rng.normal(size=n)
Lr = lambda w: 0.5 * np.mean((X @ w - y) ** 2); gr = lambda w: X.T @ (X @ w - y) / n
H = X.T @ X / n; L_smooth = np.linalg.eigvalsh(H).max()
w_gd, why, k, _ = gradient_descent(gr, np.zeros(d), eta=1.0 / L_smooth, steps=50_000, g_tol=1e-10)
w_ls = np.linalg.lstsq(X, y, rcond=None)[0]
print(why, k); assert np.allclose(w_gd, w_ls, atol=1e-6)

# --- scaling features changes the condition number and the iteration count
Xbad = X * np.array([1.0, 1.0, 100.0, 0.01])                       # wildly different scales
for name, XX in (("standardized-ish", X), ("badly scaled", Xbad)):
    Hh = XX.T @ XX / n; ev = np.linalg.eigvalsh(Hh); kappa = ev.max() / ev.min()
    gr_ = lambda w, XX=XX: XX.T @ (XX @ w - y) / n
    _, why, k, _ = gradient_descent(gr_, np.zeros(d), eta=1.0 / ev.max(), steps=200_000, g_tol=1e-8)
    print(f"{name:18s} κ={kappa:10.1f}  steps={k:7d}  stop={why}")   # report your own numbers

# --- logistic regression by GD (loss decreases monotonically for η ≤ 1/L)
sig = lambda z: 1 / (1 + np.exp(-z))
yb = (rng.random(n) < sig(X @ np.array([1.0, -1.0, 0.0, 0.5]))).astype(float)
def logloss(w):
    z = X @ w; return np.mean(np.maximum(z, 0) - z * yb + np.log1p(np.exp(-np.abs(z))))
glog = lambda w: X.T @ (sig(X @ w) - yb) / n
_, why, k, hist = gradient_descent(glog, np.zeros(d), eta=1.0 / (np.linalg.eigvalsh(X.T @ X / n).max() / 4), steps=5000, loss=logloss, g_tol=1e-7)
L = np.array(hist["loss"]); assert np.all(np.diff(L) <= 1e-12)     # monotone decrease for a safe step
print(why, k, L[0], L[-1])

# --- backtracking line search on a non-quadratic (Rosenbrock) loss
f = lambda p: (1 - p[0]) ** 2 + 100 * (p[1] - p[0] ** 2) ** 2
g = lambda p: np.array([-2 * (1 - p[0]) - 400 * p[0] * (p[1] - p[0] ** 2), 200 * (p[1] - p[0] ** 2)])
p = np.array([-1.2, 1.0])
for it in range(5000):
    eta = backtracking_step(f, g, p); p = p - eta * g(p)
    if np.linalg.norm(g(p)) < 1e-3: break
print("Rosenbrock with line search:", it, p, f(p))                  # slow along the curved valley; report your numbers
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Sign error (`+η g`) | Loss increases from step 1 | Unit test: one tiny step must lower the loss |
| No max-steps guard | Infinite loop on non-convergence | Always cap steps; report the reason for stopping |
| Stopping only on small loss change | Stops on a plateau far from a minimum | Combine with a gradient-norm criterion |
| Using the sum instead of the mean in the loss | `η` that worked at `n=100` diverges at `n=10⁴` | Fix the reduction; normalize by `n` |
| Unscaled features | Millions of steps (huge `κ`) | Standardize; precondition |
| Initialization at a symmetric point/saddle (`θ₀ = 0` for networks) | No progress (zero gradient) | Random init (Module 07 Project 2 symmetry demo) |
| Non-finite values go unnoticed | `nan` propagates silently | Check `isfinite` every step and stop |
| Line search on stochastic losses | Wasted evaluations, erratic steps | Use it only for deterministic full-batch problems |
| Reporting "converged" without a criterion | Unverifiable claim | State criterion and threshold |

### 3.6 ML link

- **Linear/logistic regression training** (Module 14, Stage 5A-04/05): exactly this loop.
- **Closed form vs iterative:** normal equation is `O(d³)`, GD is `O(nd)` per step and scales to huge `n` and non-quadratic losses (Module 14 Lesson 3).
- **Feature scaling** is an optimization fix, not just a statistical nicety (Stage 5A-03).
- **Full-batch vs mini-batch:** the cost per step motivates Lesson 5.
- **Line search/trust-region/L-BFGS** appear in classical ML libraries (4C-03).

### 3.7 Lab (75 min)

1. Implement `gradient_descent` with all stopping criteria and the stopping-reason report; test on a quadratic, linear regression (vs `lstsq`), and logistic regression (loss monotone for `η ≤ 1/L`).
2. Feature-scaling experiment: for 5 scale ratios, record `κ(XᵀX/n)` and steps to tolerance; plot steps vs `κ` (log-log) and fit the slope.
3. Implement backtracking and compare steps and loss evaluations vs a hand-tuned fixed `η` on the quadratic and on Rosenbrock.
4. Demonstrate the sum-vs-mean bug: same `η`, `n ∈ {100, 1000, 10000}`.
5. Write a test that catches a sign error and a missing max-steps guard.

### Check yourself (Unit 3)

1. After `k` steps of GD on `½λx²` with step `η`, what is `xₖ`?
2. Name three stopping criteria.
3. Why does standardizing features speed up GD?

**Reference answers:** (1) `xₖ = (1 − ηλ)ᵏ x₀`. (2) Gradient norm below a threshold, small relative loss change, small parameter change (plus a max-step cap). (3) It lowers the condition number of the Hessian `XᵀX/n`, so the slowest direction is not tiny compared with the fastest.

---

## Unit 4 — Learning rate and convergence (`03-…md`)

### 4.1 Why ML needs this

The learning rate is the single most important hyperparameter in training. This lesson turns "try a few values" into a principled picture: a stability limit set by curvature, a best constant step, and convergence speed set by conditioning.

### 4.2 Intuition

Too small a step: you inch along and never finish. A bit larger: fast and smooth. Larger still: you overshoot the valley floor and zig-zag across it. Larger than a threshold: each step overshoots by more than the last and you fly off.

### 4.3 Mechanics

- **Quadratic `L = ½θᵀAθ`** with eigenvalues `λ_min ≤ … ≤ λ_max`: GD contracts component `i` by factor `ρᵢ(η) = |1 − ηλᵢ|`.
  - **Converges iff** `0 < η < 2/λ_max`. At `η = 2/λ_max` the top component flips sign without shrinking.
  - **Asymptotic rate** `ρ(η) = max(|1 − ηλ_min|, |1 − ηλ_max|)`.
  - **Best constant step:** `η* = 2/(λ_max + λ_min)` giving `ρ* = (κ − 1)/(κ + 1)` with `κ = λ_max/λ_min`. Steps to reduce error by `10⁻⁶`: about `ln(10⁶)/(−ln ρ*) ≈ (κ/2)·ln(10⁶)` for large `κ`: **iterations scale linearly with `κ`**.
  - **Monotone loss decrease** is guaranteed for `η ≤ 1/λ_max`; for `1/λ_max < η < 2/λ_max` the loss still converges but individual coordinates oscillate.
- **Smoothness constant `L`:** a bound on the largest curvature, `λ_max(∇²L) ≤ L` everywhere. For non-quadratic losses `η ≤ 1/L` is the standard safe choice `[VERIFY: statement and proof in 4C-03]`.
- **Smoothness of ML losses (useful constants):**
  - Mean squared error `½·mean((Xw − y)²)`: `L = λ_max(XᵀX)/n`.
  - Mean logistic loss: `L ≤ λ_max(XᵀX)/(4n)` because `σ′ ≤ ¼` (Module 05 Lesson 6): Hessian `= Xᵀ diag(p(1−p)) X / n ⪯ XᵀX/(4n)`. A safe starting `η` is `4n/λ_max(XᵀX)`.
- **Convergence regimes** (what the loss curve looks like):

| Regime | `η` vs `1/L` | Loss curve | Action |
|---|---|---|---|
| Too small | `≪ 1/L` | Smooth, very slow | Increase `η` |
| Good | `≈ 0.1–1 / L` | Fast, smooth, geometric | Keep |
| Oscillating | `1/L … 2/L` | Zig-zag but converging | Reduce a bit |
| Diverging | `> 2/L` | Grows or `nan` | Reduce by ≥ 2–10× |
| Noisy plateau (mini-batch) | any | Jitter at a floor | Decay `η` or enlarge batch (Lesson 5) |

- **Convergence speed vs problem type** `[VERIFY: rates in 4C-03]`: for smooth convex problems the loss gap shrinks like `O(1/k)`; with strong convexity it shrinks geometrically at a rate set by `κ`.
- **LR range test** (an empirical method): increase `η` exponentially each step while recording the loss; pick a value somewhat below where the loss starts to rise sharply `[JUDGEMENT; details vary]`.
- **Schedules (preview, 4C-03):** step decay, exponential/cosine decay, linear **warmup** for stability at the start. A schedule helps because the useful `η` changes as training proceeds (large early, small late to settle).
- **Why feature scaling and normalization layers help:** they reduce `κ`.
- **Learning rate and batch/loss scale:** halving the loss reduction (`sum → mean`) rescales the gradient and shifts the stable `η`.

**Worked example:** `A = diag(1, 100)`, `κ = 100`. Stability: `η < 0.02`. Best constant step: `η* = 2/101 ≈ 0.0198`, `ρ* = 99/101 ≈ 0.980`; steps for `10⁻⁶`: `ln(10⁶)/(−ln 0.980) ≈ 695`. Choose `η = 1/L = 0.01` instead: `ρ = 0.99` ⇒ `1375` steps (the smooth, monotone choice is about twice as slow).

### 4.4 Code

```python
import numpy as np

def contraction_rate(lams, eta):
    return np.max(np.abs(1 - eta * np.asarray(lams)))

lams = np.array([1.0, 100.0]); kappa = lams.max() / lams.min()
eta_star = 2 / (lams.max() + lams.min()); rho_star = (kappa - 1) / (kappa + 1)
assert np.isclose(contraction_rate(lams, eta_star), rho_star)

# measured vs predicted asymptotic rate on a 2-D quadratic
A = np.diag(lams)
def run(eta, steps=2000, x0=(1.0, 1.0)):
    x = np.array(x0, float); norms = []
    for _ in range(steps):
        x = x - eta * (A @ x); norms.append(np.linalg.norm(x))
        if not np.isfinite(norms[-1]) or norms[-1] > 1e100: break
    return np.array(norms)
for eta in (0.002, 0.01, eta_star, 0.0199, 0.021):
    nrm = run(eta, 3000)
    if np.all(np.isfinite(nrm)) and nrm[-1] < nrm[0]:
        tail = nrm[len(nrm) // 2:]; measured = np.exp(np.polyfit(np.arange(len(tail)), np.log(np.maximum(tail, 1e-300)), 1)[0])
    else:
        measured = np.nan
    print(f"η={eta:.4f}  predicted ρ={contraction_rate(lams, eta):.5f}  measured ρ={measured:.5f}  final‖x‖={nrm[-1]:.2e}")

# steps to reach 1e-6 vs κ at the best constant step
def steps_to_tol(kappa, tol=1e-6):
    l = np.array([1.0, float(kappa)]); eta = 2 / (l.sum()); x = np.array([1.0, 1.0]); k = 0
    while np.linalg.norm(x) > tol and k < 10_000_000:
        x = x - eta * l * x; k += 1
    return k
for k_ in (1, 2, 10, 100, 1000): print(f"κ={k_:5d}  steps ≈ {steps_to_tol(k_)}")                       # grows ≈ linearly in κ

# smoothness constants of ML losses
rng = np.random.default_rng(0)
n, d = 400, 5
X = rng.normal(size=(n, d)) * np.array([1, 2, 0.5, 3, 1.0])
yb = (rng.random(n) < 1 / (1 + np.exp(-X @ rng.normal(size=d)))).astype(float)
sig = lambda z: 1 / (1 + np.exp(-z))
L_mse = np.linalg.eigvalsh(X.T @ X / n).max(); L_log_bound = L_mse / 4
for _ in range(200):                                                       # Hessian of mean logistic loss at random θ
    th = rng.normal(scale=2.0, size=d); p = sig(X @ th)
    Hh = (X * (p * (1 - p))[:, None]).T @ X / n
    assert np.linalg.eigvalsh(Hh).max() <= L_log_bound + 1e-12
print("L_mse =", L_mse, " logistic L ≤", L_log_bound)

# LR range test on logistic regression: grow η geometrically, record the loss
def logloss(w):
    z = X @ w; return np.mean(np.maximum(z, 0) - z * yb + np.log1p(np.exp(-np.abs(z))))
glog = lambda w: X.T @ (sig(X @ w) - yb) / n
w = np.zeros(d); etas = np.geomspace(1e-4, 50, 300); losses = []
for e in etas:
    w = w - e * glog(w); losses.append(logloss(w))
losses = np.array(losses); first_bad = int(np.argmax(losses > losses.min() * 2 + 1.0))
print("loss rises sharply near η ≈", etas[first_bad], " | 4/λmax-based safe η =", 1 / L_log_bound)
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Choosing `η` by habit (`1e-3`) regardless of loss scale | Works on one problem, fails on the next | Estimate `L` or run an LR range test |
| Assuming `η = 1/L` is the *fastest* choice | Leaves speed on the table on quadratics | Best constant step is `2/(λ_max+λ_min)` (but less smooth) |
| Ignoring conditioning when the loss curve is slow | Raising `η` diverges; lowering barely helps | Check `κ`; standardize; use momentum/Adam |
| Treating oscillation as divergence (or vice versa) | Wrong fix | Look at `‖θ‖`/loss magnitude trend, not one step |
| Judging `η` on the first few steps only | Early speed ≠ late stability | Run to the plateau; use schedules |
| Same `η` after changing loss reduction/scale | Sudden divergence | Re-derive `L`; re-run the range test |
| Using a learning-rate range test on a noisy mini-batch loss without smoothing | Spurious spikes | Smooth the curve; use several seeds |
| Quoting convergence-rate theory for non-convex networks as guarantees | Overconfidence | Treat as local guidance only |
| Reading the LR-range-test blow-up point as the safe `η` for logistic loss | Its gradients are bounded, so a too-large `η` bounces instead of producing `nan`; in a seeded run the loss only rose sharply near `η ≈ 9` while `1/L ≈ 0.42` | Use `1/L` (or a fraction of the blow-up point) as the safe value, not the blow-up point itself |

### 4.6 ML link

- **Every training run's most sensitive hyperparameter** (Stage 5C-03).
- **Warmup and decay schedules** exist because curvature and gradient noise change during training (4C-03 Lesson 12).
- **Normalization layers and standardization** reduce effective conditioning (Stage 4C-07 Lesson 9, Module 14).
- **Largest Hessian eigenvalue ("sharpness")** limits stable `η` in deep networks `[JUDGEMENT; active research]` (4C-03).
- **LR range test** is a standard practical tool in deep-learning toolkits `[VERIFY: names/APIs]`.

### 4.7 Lab (90 min)

1. Reproduce the table of predicted vs measured contraction rates for 6 step sizes on three quadratics (`κ ∈ {10, 100, 1000}`); mark the best constant step and the stability threshold.
2. Plot steps-to-tolerance vs `κ` (log-log) and fit the slope.
3. Verify the logistic smoothness bound numerically over 500 random `θ` and several data scalings; use `1/L` as `η` and confirm monotone loss decrease.
4. Implement the LR range test and apply it to linear regression, logistic regression, and a tiny network (Module 07 Project 2); compare the chosen `η` with `1/L` when `L` is computable.
5. Diagnose six unlabeled loss curves (provided by a script that hides the `η` used) and write a one-sentence fix for each.

### Check yourself (Unit 4)

1. For `f = ½·50·x²`, what is the stability threshold on `η`, and the one-step-optimal `η`?
2. At the best constant step for `κ = 100`, what is the asymptotic contraction factor?
3. Why does standardizing features speed up gradient descent?

**Reference answers:** (1) `η < 2/50 = 0.04`; the one-step optimum is `1/50 = 0.02`. (2) `ρ* = (100 − 1)/(100 + 1) ≈ 0.980`. (3) It reduces `κ`: the stability limit is set by `λ_max` but progress along the flattest direction is set by `λ_min`, so a smaller ratio makes both limits compatible.

---

## Unit 5 — Stochastic and mini-batch gradient descent (`04-…md`)

### 5.1 Why ML needs this

Computing the gradient over the *entire* dataset every step is wasteful or impossible: datasets can have millions of rows, and the gradient is just an average. A random subset gives a cheap, noisy, **unbiased** estimate of that average, and almost every deep-learning training loop is built on it.

### 5.2 Intuition

To estimate the average height of a country, you do not measure everyone: a random sample of a few hundred gives a good estimate. The same holds for the gradient: a random mini-batch points roughly the same way as the full gradient, at a tiny fraction of the cost. The estimate is noisy, but the noise averages out over many steps, and a little noise can even help escape poor regions `[JUDGEMENT]`.

### 5.3 Mechanics

- **Full-batch GD:** `g = (1/n) Σᵢ ∇ℓᵢ(θ)`. Cost `O(n)` per step.
- **SGD (batch size 1):** `gᵢ = ∇ℓᵢ(θ)` for a random `i`.
- **Mini-batch SGD (size `B`):** `g_B = (1/B) Σ_{i∈batch} ∇ℓᵢ(θ)`.
- **Unbiased estimator:** if the batch is a uniformly random sample, `E[g_B] = ∇L(θ)`.
- **Variance:** with i.i.d. sampling, `Var(g_B) = σ²/B` where `σ²` is the per-sample gradient variance; sampling **without replacement** from a finite dataset of size `n` multiplies it by `(1 − (B−1)/(n−1))` (finite-population correction) `[VERIFY: exact factor]`. Larger batches reduce noise like `1/B`, with **diminishing returns**: the noise standard deviation falls like `1/√B`.
- **Epoch:** one pass through the data (`n/B` steps). Shuffle each epoch; process every sample once.
- **Trade-offs in `B`:** small `B`: cheap step, noisy, many steps, poor hardware utilization; large `B`: smooth, fewer steps per epoch, better hardware efficiency but more compute per step and, past some point, no faster progress per sample `[JUDGEMENT; depends on problem]`.
- **Constant `η` ⇒ noise floor:** SGD with a fixed step converges to a **neighbourhood** of the minimum whose size grows with `η` and noise, not to the minimum itself. **Decaying `η`** (Robbins–Monro conditions `Σηₜ = ∞`, `Ση²ₜ < ∞`) removes the floor `[VERIFY: statement]`. Practical alternatives: step/cosine decay, larger batches late, iterate averaging.
- **Learning rate vs batch size:** when you multiply `B` by `k`, a common heuristic is to scale `η` by about `k` up to a limit (linear scaling) or `√k`, usually with warmup `[JUDGEMENT; verify empirically per problem]`.
- **Gradient noise and curvature:** noise matters most where the loss is flat; near a sharp minimum it forces small `η`.
- **Cost accounting:** compare methods by **number of gradient evaluations** (samples processed), not by steps: one full-batch step = `n` evaluations.
- **Implementation details:** shuffle with a seeded RNG; handle the last short batch (drop or keep, but be explicit); keep data order independent of parameter state; `float64` for checks.
- **SGD on non-convex losses:** noise may help leave saddles; theory is partial (4C-03 Lesson 10).

**Worked example:** linear regression with `n = 10 000`, `B = 100`: one epoch is 100 steps, each costing `1/100` of a full gradient. After one epoch SGD has made 100 updates; full-batch GD has made 1, using the same gradient evaluations.

### 5.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

n, d = 4000, 5
X = rng.normal(size=(n, d)); w_true = np.array([1.0, -2.0, 0.5, 3.0, -1.0])
y = X @ w_true + 0.5 * rng.normal(size=n)
full_loss = lambda w: 0.5 * np.mean((X @ w - y) ** 2)
full_grad = lambda w: X.T @ (X @ w - y) / n
batch_grad = lambda w, idx: X[idx].T @ (X[idx] @ w - y[idx]) / len(idx)

def batches(n, B, rng):
    perm = rng.permutation(n)                       # reshuffle every epoch
    for s in range(0, n, B):
        yield perm[s:s + B]                         # last batch may be shorter: documented behaviour

# --- unbiasedness: the average of mini-batch gradients equals the full gradient
w0 = rng.normal(size=d); g_full = full_grad(w0)
for B in (1, 8, 64):
    G = np.array([batch_grad(w0, rng.choice(n, size=B, replace=False)) for _ in range(20_000)])
    bias = np.linalg.norm(G.mean(axis=0) - g_full) / np.linalg.norm(g_full)
    print(f"B={B:3d}  relative bias of the mean mini-batch gradient: {bias:.4f}")      # ≈ Monte-Carlo noise only

# --- variance ∝ 1/B (with a finite-population correction without replacement)
per_sample = X * (X @ w0 - y)[:, None]                       # (n, d) per-sample gradients
sigma2 = np.sum(per_sample.var(axis=0, ddof=1))              # total per-sample variance
for B in (1, 4, 16, 64, 256):
    G = np.array([batch_grad(w0, rng.choice(n, size=B, replace=False)) for _ in range(4_000)])
    var = np.mean(np.sum((G - g_full) ** 2, axis=1))
    pred = sigma2 / B * (1 - (B - 1) / (n - 1))
    print(f"B={B:4d}  measured Var={var:9.4f}  predicted={pred:9.4f}  B·Var={B * var:8.3f}")   # B·Var ≈ constant

# --- three trainers, compared by gradient evaluations
def train(kind, eta, evals_budget, B=None, seed=0, decay=False):
    g = np.random.default_rng(seed); w = np.zeros(d); evals = 0; curve = [(0, full_loss(w))]; t = 0
    while evals < evals_budget:
        if kind == "full":
            w -= eta * full_grad(w); evals += n
        else:
            bs = 1 if kind == "sgd" else B
            for idx in batches(n, bs, g):
                step = eta / np.sqrt(1 + t / 200) if decay else eta
                w -= step * batch_grad(w, idx); evals += len(idx); t += 1
                if evals % (n // 4) < len(idx): curve.append((evals, full_loss(w)))
                if evals >= evals_budget: break
        curve.append((evals, full_loss(w)))
    return w, curve
opt = full_loss(np.linalg.lstsq(X, y, rcond=None)[0])
for name, kw in (("full-batch", dict(kind="full", eta=0.3)), ("SGD B=1", dict(kind="sgd", eta=0.01)),
                 ("mini-batch B=32", dict(kind="mb", eta=0.1, B=32)), ("mini-batch B=32 + decay", dict(kind="mb", eta=0.1, B=32, decay=True))):
    gaps = [train(seed=s, evals_budget=20 * n, **kw)[1][-1][1] - opt for s in range(5)]
    print(f"{name:26s} final loss gap after 20 epochs: {np.mean(gaps):.2e} ± {np.std(gaps, ddof=1) / np.sqrt(5):.1e}")

# --- noise floor: constant η leaves a floor that shrinks with η
for eta in (0.2, 0.05, 0.01):
    gaps = [train("mb", eta, 40 * n, B=8, seed=s)[1][-1][1] - opt for s in range(5)]
    print(f"constant η={eta:5.2f}  floor ≈ {np.mean(gaps):.2e}")
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Not shuffling (or shuffling once) | Systematic bias from data order (e.g., sorted by class) | Reshuffle every epoch with a seeded RNG |
| Mini-batches with duplicates when you intended an epoch | Some samples seen twice, some never | Permutation-based batches |
| Comparing methods by steps instead of gradient evaluations | SGD looks "slower" or "faster" for the wrong reason | Compare per evaluation (and per wall-clock separately) |
| Constant `η` and expecting exact convergence | Loss plateaus at a floor | Decay `η` or enlarge batch near the end |
| Sum-reduction loss with variable-size last batch | Last batch gets over-weighted | Use mean reduction (or weight by batch size) |
| Batch statistics (e.g., `mean`) computed per batch for preprocessing | Train/serve mismatch | Compute statistics on the training set |
| Scaling `B` without touching `η` | Under-use of larger batches, or instability | Re-tune `η` (linear/√ scaling as a starting point) |
| Single-seed conclusions | Results are noise | ≥ 5 seeds, mean ± standard error |
| Evaluating the loss on the mini-batch only | Noisy, optimistic curve | Evaluate on a fixed held-out or full set periodically |

### 5.6 ML link

- **Every deep-learning training loop** (Stage 5C-03) iterates mini-batches with a shuffle per epoch.
- **Batch size as a hyperparameter:** affects noise, memory, throughput, and generalization `[JUDGEMENT]`.
- **Gradient accumulation** simulates a large batch by summing micro-batch gradients (Module 07 Lesson 4 additivity).
- **Learning-rate schedules and warmup** (4C-03) address the noise floor and early instability.
- **Data loading and ordering** are part of reproducibility (Stage 5A-11, 5D-06).

### 5.7 Lab (90 min)

1. Verify unbiasedness and the `σ²/B` variance law (with the finite-population factor) for `B ∈ {1, 4, 16, 64, 256}`; plot standard deviation vs `B` on log-log axes (slope near `−½`).
2. Compare full-batch, SGD, and mini-batch (`B ∈ {8, 32, 128, 512}`) by **gradient evaluations** on linear regression and logistic regression; ≥ 5 seeds; mean ± standard error.
3. Demonstrate the noise floor for three constant `η` and show it disappears (or shrinks) with decay and with a larger batch at the end.
4. Reproduce the data-order bug: train on data sorted by class without shuffling and compare with shuffled.
5. Test the linear-scaling heuristic: for `B ∈ {16, 64, 256}` find the best `η` per batch size by grid search and plot best-`η` vs `B`; report what you observe.

### Check yourself (Unit 5)

1. Is a mini-batch gradient an unbiased estimate of the full gradient? Under what sampling condition?
2. How does the standard deviation of the mini-batch gradient scale with `B`?
3. Why does constant-`η` SGD not converge exactly?

**Reference answers:** (1) Yes, if the batch is a uniform random sample of the data. (2) Like `1/√B`. (3) The gradient noise never vanishes, so each step perturbs the iterate; it settles in a neighbourhood whose size scales with `η`.

---

## Unit 6 — Momentum, RMSprop, and Adam: intuition (`05-…md`)

### 6.1 Why ML needs this

Plain SGD struggles with ill-conditioned landscapes (slow along narrow valleys, oscillating across them) and with parameters whose gradients live on very different scales. Momentum, RMSprop, and Adam are cheap fixes for these two problems, and Adam is the default for many deep-learning tasks. You should know exactly what each one computes.

### 6.2 Intuition

- **Momentum:** a heavy ball rolling downhill. It accumulates velocity in directions where the gradient points consistently (along the valley) and cancels directions that flip sign (across the valley).
- **RMSprop:** give each parameter its own step size: **divide by the recent typical gradient magnitude**. Parameters with large gradients take smaller steps; parameters with tiny gradients take larger ones.
- **Adam:** momentum (average of gradients) **plus** RMSprop (average of squared gradients), with a correction for the zero-initialized averages at the start.

### 6.3 Mechanics

Notation: `g = ∇L(θ)` (a mini-batch estimate in practice), learning rate `η`.

| Method | State | Update | Typical hyperparameters |
|---|---|---|---|
| SGD | none | `θ ← θ − η g` | `η` |
| **Momentum** (PyTorch-style) | `v` | `v ← βv + g`; `θ ← θ − η v` | `β = 0.9` |
| **Nesterov** | `v` | `v ← βv + g`; `θ ← θ − η (g + βv)` (look-ahead form) | `β = 0.9` |
| **RMSprop** | `s` | `s ← ρs + (1 − ρ)g²`; `θ ← θ − η g/(√s + ε)` | `ρ = 0.9 or 0.99`, `ε = 1e-8` |
| **Adam** | `m, v, t` | `m ← β₁m + (1−β₁)g`; `v ← β₂v + (1−β₂)g²`; `m̂ = m/(1−β₁ᵗ)`; `v̂ = v/(1−β₂ᵗ)`; `θ ← θ − η m̂/(√v̂ + ε)` | `β₁ = 0.9`, `β₂ = 0.999`, `ε = 1e-8`, `η = 1e-3` |

(All operations are elementwise on parameter vectors.)

- **Two momentum conventions exist:** `v ← βv + g; θ ← θ − ηv` (PyTorch) versus `v ← βv + ηg; θ ← θ − v` (Sutskever/classic). They are equivalent only for a constant `η`; when you schedule `η`, they differ. Always state which one you use and check against your framework `[VERIFY in the installed version]`.
- **Momentum effect:** with a constant gradient, `v → g/(1 − β)`, so the **effective step is `η/(1 − β)`**: `β = 0.9` multiplies the effective learning rate by 10 along consistent directions. Across oscillating directions the contributions cancel.
- **Why momentum helps on ill-conditioned quadratics:** it can improve the iteration count from `∝ κ` to `∝ √κ` with tuned parameters (heavy ball/Nesterov) `[VERIFY: statement and proof in 4C-03]`.
- **RMSprop/Adam per-parameter scaling:** the update is roughly *sign-like* with magnitude `≈ η`: parameters are updated by about the same amount regardless of gradient scale. This makes the optimizer insensitive to the absolute scale of the loss and helps with sparse or badly scaled gradients.
- **Adam bias correction:** `m` and `v` start at 0, so early estimates are biased toward 0, and `v` is biased far more than `m` at the default `β₂ = 0.999`. Dividing by `1 − βᵗ` fixes it. **Without** the correction the first update is *too large*, not too small: `m` is shrunk by `(1 − β₁) = 0.1` but `√v` by `√(1 − β₂) ≈ 0.032`, so the step is inflated by `(1 − β₁)/√(1 − β₂) ≈ 3.2×` for the defaults. At `t = 1`: `m̂ = g`, `v̂ = g²`, so the update is `η · g/(|g| + ε) ≈ η·sign(g)`: **the first Adam step has magnitude about `η` in every coordinate** (a useful sanity check).
- **`ε` placement and size** matter: `ε` inside vs outside the square root, and `1e-8` vs `1e-6` or larger, change behaviour for tiny gradients (especially in `float16`) `[VERIFY: framework-specific]`.
- **Weight decay with Adam:** adding `λθ` to the gradient (L2 regularization) is **not** the same as decoupled weight decay (AdamW); the distinction is in 4C-03 `[VERIFY]`.
- **Caveats:** Adam's per-parameter step can hurt generalization in some settings and can fail to converge on some constructed problems; SGD with momentum plus a good schedule remains competitive or better in several vision tasks `[JUDGEMENT; empirical, task-dependent]`. Adam often tolerates a wider range of `η` than plain SGD; verify on your problem.
- **Memory:** momentum stores one extra buffer per parameter; Adam stores two (important for large models, Stage 5D-06 `[VERIFY]`).
- **Defaults are starting points,** not truths: `η` is still the main knob.

**Worked example (momentum with a constant gradient `g = 1`, `β = 0.9`, `η = 0.1`):** `v` goes `1, 1.9, 2.71, …, → 10`; the per-step movement `ηv` goes `0.1, 0.19, …, → 1.0`: ten times the plain-SGD step.

### 6.4 Code

```python
import numpy as np

class SGD:
    def __init__(self, lr=0.1, momentum=0.0, nesterov=False):
        self.lr, self.mu, self.nesterov, self.v = lr, momentum, nesterov, None
    def step(self, x, g):
        if self.mu == 0.0: return x - self.lr * g
        self.v = g.copy() if self.v is None else self.mu * self.v + g
        upd = g + self.mu * self.v if self.nesterov else self.v
        return x - self.lr * upd

class RMSprop:
    def __init__(self, lr=1e-2, rho=0.9, eps=1e-8): self.lr, self.rho, self.eps, self.s = lr, rho, eps, None
    def step(self, x, g):
        self.s = (1 - self.rho) * g * g if self.s is None else self.rho * self.s + (1 - self.rho) * g * g
        return x - self.lr * g / (np.sqrt(self.s) + self.eps)

class Adam:
    def __init__(self, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.m, self.v, self.t = lr, b1, b2, eps, None, None, 0
    def step(self, x, g):
        self.t += 1
        if self.m is None: self.m, self.v = np.zeros_like(x), np.zeros_like(x)
        self.m = self.b1 * self.m + (1 - self.b1) * g
        self.v = self.b2 * self.v + (1 - self.b2) * g * g
        mh, vh = self.m / (1 - self.b1 ** self.t), self.v / (1 - self.b2 ** self.t)
        return x - self.lr * mh / (np.sqrt(vh) + self.eps)

# --- hand-checkable first steps
g = np.array([0.5, -2.0, 1e-3]); x0 = np.zeros(3)
x1 = Adam(lr=0.01).step(x0.copy(), g)
print("Adam first step:", x1 - x0)                             # ≈ -0.01·sign(g) for every coordinate
assert np.allclose(x1 - x0, -0.01 * np.sign(g), rtol=1e-3, atol=1e-6) or np.allclose(np.abs(x1 - x0), 0.01, rtol=1e-3, atol=2e-3)
assert np.allclose(SGD(0.1).step(x0.copy(), g) - x0, -0.1 * g)

# --- momentum with a constant gradient accelerates by 1/(1-β)
opt = SGD(lr=0.1, momentum=0.9); x = np.zeros(1); moves = []
for _ in range(100):
    x_new = opt.step(x, np.array([1.0])); moves.append(float((x - x_new)[0])); x = x_new
print(moves[0], moves[9], moves[-1])                            # 0.1 → ... → ≈ 1.0 (= lr/(1-β))
assert np.isclose(moves[-1], 0.1 / (1 - 0.9), rtol=1e-3)

# --- bias correction: without it the first Adam steps are too large (v is biased harder than m)
def adam_nocorr(lr, b1, b2, eps, g):
    m = (1 - b1) * g; v = (1 - b2) * g * g; return lr * m / (np.sqrt(v) + eps)
print("with correction:", 0.01 * 1.0 / (1.0 + 1e-8), " without:", adam_nocorr(0.01, 0.9, 0.999, 1e-8, 1.0))   # 0.01 vs ≈ 0.0316: too LARGE by (1−β1)/√(1−β2) ≈ 3.2×

# --- ill-conditioned quadratic: steps to ‖∇L‖ < 1e-6
A = np.diag([1.0, 100.0]); grad = lambda x: A @ x
def run(opt, steps=20_000, x0=(1.0, 1.0), tol=1e-6):
    x = np.array(x0, float)
    for k in range(steps):
        g = grad(x)
        if np.linalg.norm(g) < tol: return k
        x = opt.step(x, g)
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e6: return np.inf
    return np.nan                                                # did not converge in the budget
trials = {"GD η=1/L": SGD(0.01), "GD η=2/(λ+λ)": SGD(2 / 101), "momentum β=0.9 η=0.01": SGD(0.01, 0.9),
          "Nesterov β=0.9 η=0.01": SGD(0.01, 0.9, True), "RMSprop η=0.01": RMSprop(0.01), "Adam η=0.05": Adam(0.05)}
for name, o in trials.items(): print(f"{name:26s} steps: {run(o)}")                              # report your own numbers

# the same quadratic rotated by 45°: per-coordinate scaling no longer lines up with the curvature axes
th = np.pi / 4; R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
A = R @ np.diag([1.0, 100.0]) @ R.T                                  # same eigenvalues, rotated; grad uses the global A
for name, mk in (("GD η=2/(λ+λ)", lambda: SGD(2 / 101)), ("momentum β=0.9 η=0.01", lambda: SGD(0.01, 0.9)),
                 ("RMSprop η=0.01", lambda: RMSprop(0.01)), ("Adam η=0.05", lambda: Adam(0.05))):
    print(f"rotated: {name:24s} steps: {run(mk())}")                 # RMSprop may fail to reach the tolerance; report what you see

# --- Rosenbrock (non-convex valley)
f = lambda p: (1 - p[0]) ** 2 + 100 * (p[1] - p[0] ** 2) ** 2
gR = lambda p: np.array([-2 * (1 - p[0]) - 400 * p[0] * (p[1] - p[0] ** 2), 200 * (p[1] - p[0] ** 2)])
for name, o in (("SGD η=1e-3", SGD(1e-3)), ("momentum η=1e-4 β=0.9", SGD(1e-4, 0.9)), ("Adam η=0.02", Adam(0.02))):
    p = np.array([-1.2, 1.0])
    for _ in range(20_000): p = o.step(p, gR(p))
    print(f"{name:24s} f = {f(p):.3e}  p = {np.round(p, 3)}")
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Mixing momentum conventions (`ηg` inside vs outside the buffer) when scheduling `η` | Unexpected behaviour after a schedule change | State the form; test against the framework |
| Skipping Adam's bias correction | First steps about `(1−β₁)/√(1−β₂) ≈ 3.2×` too large with the defaults, then drift | Implement `m̂, v̂`; unit-test the first step ≈ `η·sign(g)` |
| `ε` too small in low precision (`float16`) | Division by ~0, `inf`/`nan` | Larger `ε`, higher-precision optimizer state |
| Using the Adam default `η = 1e-3` blindly | Divergence or stalling on some models | LR range test; tune |
| Adding L2 to the gradient and calling it "AdamW" | Different regularization effect | Decoupled weight decay (4C-03) |
| Momentum with an `η` tuned for plain SGD | Overshoot/instability (effective step ×10) | Re-tune; reduce `η` by about `1 − β` |
| Not re-initializing optimizer state when restarting a run | Stale `m, v` after a parameter reset | Create a fresh optimizer |
| Comparing optimizers at one shared `η` | Misleading ranking | Tune each (Project 2) |
| Assuming Adam always beats SGD (or vice versa) | Wrong choice for the task | Run a controlled comparison |
| Expecting RMSprop/Adam to fix any ill-conditioning | Per-coordinate scaling helps axis-aligned curvature but not rotated valleys | Test on a rotated problem; consider momentum, preconditioning, or feature decorrelation |
| Applying per-parameter scaling to features that are intentionally on different scales | Unexpected equalization of updates | Think about what normalization is wanted |

### 6.6 ML link

- **Default optimizers in practice** (Stage 5C-03): SGD+momentum and Adam/AdamW cover most training runs.
- **Large-model memory:** optimizer state size matters (Stage 5D-06, 5D-10) `[VERIFY]`.
- **Mixed precision and `ε`:** low-precision pitfalls (4C-07 Lesson 11).
- **Schedules and warmup** interact with Adam's bias correction and noisy early `v̂` (4C-03 Lesson 12).
- **Generalization debates** (Adam vs SGD) are empirical and task-dependent (Stage 5C-03 `[JUDGEMENT]`).

### 6.7 Lab (90 min)

1. Implement the five optimizers; unit-test first steps against hand calculations; cross-check against PyTorch's optimizers on a small problem if PyTorch is installed (not required) `[VERIFY: convention differences, e.g., momentum form, `ε` placement]`.
2. Demonstrate momentum's `1/(1 − β)` acceleration with a constant gradient and its oscillation-cancelling effect on a narrow valley (plot both paths on contours).
3. Bias-correction demonstration: plot Adam's first 20 steps with and without correction.
4. Ill-conditioned quadratic benchmark for `κ ∈ {10, 100, 1000}`, both **axis-aligned and rotated by 45°**: tune `η` for every optimizer by grid search; table of steps-to-tolerance; report who wins at each `κ` and by how much (your numbers), and explain why the ranking can change under rotation (per-coordinate scaling only helps when curvature is axis-aligned).
5. Scale-invariance test: multiply the loss by `100` and compare how plain GD and Adam respond (GD's effective step scales; Adam's barely changes).

### Check yourself (Unit 6)

1. What is the effective learning-rate multiplier of momentum with `β = 0.9` on a constant gradient?
2. What is the magnitude of Adam's first step (per coordinate)?
3. What does RMSprop divide by, and why?

**Reference answers:** (1) `1/(1 − 0.9) = 10`. (2) About `η` (the update is `η·g/(|g| + ε) ≈ η·sign(g)`). (3) The square root of a running average of squared gradients, to give each parameter a step scaled to its own typical gradient magnitude.

---

## Unit 7 — Practice question bank (`practice-questions.md`)

### 7.1 Structure

About 45 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 11 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, "predict the loss curve", runnable code, and tuning/diagnosis judgement.

### 7.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 7.3 Seed items

**Q1 [L1] Loss behaviour.** Which of MSE, MAE, Huber is least sensitive to outliers? → MAE (bounded gradient), with Huber close behind.
**Q2 [L2] Estimators.** A constant model is fit to `(2, 4, 6, 8, 100)`. MSE and MAE minimizers? → Mean `24`; median `6`.
**Q3 [L2] Huber gradient.** `δ = 2`, residuals `(−5, 0.5, 3)`: `dℓ/dr`? → `(−2, 0.5, 2)`.
**Q4 [L2] GD step.** `f(x) = 4x²`, `x₀ = 1`, `η = 0.1`. `x₁`? → `g = 8x = 8`; `x₁ = 1 − 0.8 = 0.2`.
**Q5 [L2] Stability.** `f = ½·40·x²`: largest stable `η`? → `2/40 = 0.05`.
**Q6 [L2] Best step.** Eigenvalues `1` and `9`: best constant `η` and `ρ*`? → `η* = 2/10 = 0.2`; `ρ* = 8/10 = 0.8`.
**Q7 [L2] Epochs.** `n = 50 000`, `B = 250`. Steps per epoch? → `200`.
**Q8 [L2] Momentum.** `β = 0.95`: effective learning-rate multiplier on a steady gradient? → `20`.
**Q9 [L2] Adam first step.** `lr = 0.002`, `g = (3, −0.01)`. Approximate first update? → `(−0.002, +0.002)` (≈ `lr·sign(g)`).
**Q10 [L3] Debug.** Loss is `nan` after step 1 with `η = 1`. Likely cause and first check? → `η` far above `2/L`; check `‖g‖` growth, lower `η` by 10×, verify loss reduction (sum vs mean).
**Q11 [L3] Debug.** Mini-batch loss curve is jagged and never falls below `0.31`; full-batch evaluation reaches `0.29`. → Constant-`η` noise floor and/or evaluating on a single batch; evaluate on a fixed set and decay `η`.
**Q12 [L3] Debug.** Training on data sorted by class without shuffling; loss spikes at each epoch boundary. → Missing shuffle; reshuffle each epoch.
**Q13 [L3] Analysis.** GD is slow, and raising `η` makes it diverge. What does that suggest and what are two remedies? → Large `κ`; standardize features, or use momentum/Adam.
**Q14 [L3] Analysis.** After adding momentum `β = 0.9` at the same `η`, training diverges. → Effective step ×10 exceeded `2/L`; reduce `η` by about 10×.
**Q15 [L3] Analysis.** Adam trains but SGD at default settings does not on the same model. Is Adam "better"? → Not necessarily; SGD's `η` may be mis-tuned; compare with tuned `η` for each.
**Q16 [L4] Design.** Design a fair comparison of SGD+momentum and Adam for a new model. → Same budget in gradient evaluations, tune `η` per optimizer (log grid), ≥ 5 seeds, report mean ± SE of final held-out metric and steps-to-target, include `η`-sensitivity curves, state conventions.
**Q17 [L4] Design.** Choose `η`, batch size, and schedule for a new regression task with 10⁶ rows. → Standardize features; LR range test; mini-batch with shuffle; mean reduction; warmup + decay; validate with a held-out set; revisit `η` if `B` changes.
**Q18 [L4] Design.** A target has 3% extreme outliers from a data bug you cannot fix quickly. → Huber or MAE as a stopgap with `δ` from a robust scale; report both RMSE and MAE; log the outlier rate and plan to fix the source.

### 7.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Loss functions | 2 | 3 | 1 | 1 |
| Gradient descent | 2 | 3 | 2 | 0 |
| Learning rate, convergence | 2 | 3 | 3 | 2 |
| SGD and mini-batch | 2 | 2 | 3 | 1 |
| Momentum, RMSprop, Adam | 3 | 3 | 3 | 2 |

### Check yourself (Unit 7)

1. Why is a "fair comparison" design question included at L4?
2. Which items need runnable code?

**Reference answers:** (1) Optimizer comparisons are the most commonly mis-run experiments in practice. (2) All L3 items and any whose answer depends on floating-point or sampling behaviour.

---

## Unit 8 — Project index (`Projects/README.md`)

### 8.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Gradient descent visualizer | Theory-vs-measurement of stability and rates; diagnostic plots | 2–4, 6 | 6–7 h |
| 2 | Optimizer comparison: SGD, momentum, Adam | Fair, statistically honest benchmarking; optimizer implementations | 4–6 | 8–9 h |

Order: 1 → 2 (Project 2 reuses Project 1's objective functions and diagnostics). Outputs feed `mlmath/optim.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D8) and notebook `08_optimization.ipynb`. Project 2's optimizer classes are reused in Module 14 and the Stage 5 modules.

### 8.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (theory predictions vs measurement; update rules vs hand calculation) | 30 |
| Failure-mode handling (divergence detection, `nan`, bad `η`, seeds that fail) | 15 |
| Reproducibility (seeded, pinned, clean venv, headless plotting) | 15 |
| Explanation and statistical honesty (mean ± SE, tuned baselines, scoped claims) | 15 |
| Code quality (types, docstrings, no hidden state) | 15 |
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

**Reference answers:** (1) The objective functions, gradient checks, and diagnostic/plotting utilities. (2) D8 (`mlmath/optim.py`).

---

## Unit 9 — Project: Gradient descent visualizer (`Projects/01-…md`)

### 9.1 Brief

Build `gdviz`: a toolkit that runs gradient descent (with optional momentum) on 2-D objectives, draws the paths over contours, plots loss/gradient-norm curves on log scales, and **checks every picture against theory**: the stability threshold `2/λ_max`, the contraction factor `max|1−ηλᵢ|`, the best constant step, and steps-to-tolerance vs `κ`.

**Industry framing:** optimizer diagnostics are standard debugging views, and a picture is only trusted when it comes with a number that confirms it.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Objective catalogue | Quadratics with chosen eigenvalues and rotation, Rosenbrock, Himmelblau, a linear-regression loss over `(w, b)` for synthetic data, a logistic-loss surface; analytic gradients, each gradient-checked |
| R2 | GD engine | `run_gd(f, grad, x0, eta, steps, momentum=0.0, nesterov=False, tol)` returning the path, loss/gradient history, stop reason (`converged`, `diverged`, `max_steps`, `nan`) |
| R3 | Path plots | Contours with log-spaced levels; paths for ≥ 4 learning rates; start/end markers; headless (`Agg`) |
| R4 | Curve plots | Loss and `‖∇L‖` vs step (log y); annotate regimes: slow / good / oscillating / diverging |
| R5 | Stability threshold | Sweep `η` on quadratics; find the empirical divergence threshold by bisection; compare with `2/λ_max` (within 2%) |
| R6 | Rate check | Fit the asymptotic contraction factor from the tail of `‖x_k‖`; compare with `max|1−ηλᵢ|` over a grid of `η` (within 1%) |
| R7 | Conditioning study | For `κ ∈ {1, 10, 100, 1000}`: best constant step, predicted vs measured `ρ*`, steps-to-tolerance vs `κ` (log-log slope ≈ 1) |
| R8 | Momentum study | Add momentum; show oscillation damping and the `1/(1−β)` effective step; find the stability region in the `(η, β)` plane for a 1-D quadratic and plot it |
| R9 | Real-loss diagnostics | Linear regression: loss surface over `(w, b)` with and without feature standardization; show elongation and the effect on steps-to-tolerance |
| R10 | Regime classifier | A function that labels a loss curve (`too_slow`, `good`, `oscillating`, `diverging`, `noisy_plateau`) from numeric features; evaluated on a labelled set of generated curves; report accuracy honestly |
| R11 | Report | `REPORT.md`: every figure with its takeaway and the theory number it was checked against |

### 9.3 Layout and starter

```
gdviz/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/gdviz/{__init__,objectives,engine,theory,plots,regimes}.py
├── tests/{test_objectives,test_engine,test_theory,test_regimes}.py
├── notebooks/08_gd_visualizer.ipynb
└── results/
```

```python
# src/gdviz/engine.py
import numpy as np

def run_gd(grad, x0, eta, steps=5000, momentum=0.0, nesterov=False, g_tol=1e-8, blowup=1e8, loss=None):
    x = np.asarray(x0, float).copy(); v = np.zeros_like(x)
    path, losses, gn = [x.copy()], [], []
    for k in range(steps):
        g = grad(x); n = float(np.linalg.norm(g)); gn.append(n)
        if loss is not None: losses.append(float(loss(x)))
        if not np.isfinite(n): return dict(path=np.array(path), loss=losses, gnorm=gn, reason="nan", steps=k)
        if n < g_tol:           return dict(path=np.array(path), loss=losses, gnorm=gn, reason="converged", steps=k)
        v = momentum * v + g
        upd = g + momentum * v if nesterov else v
        x = x - eta * upd; path.append(x.copy())
        if np.linalg.norm(x) > blowup:
            return dict(path=np.array(path), loss=losses, gnorm=gn, reason="diverged", steps=k)
    return dict(path=np.array(path), loss=losses, gnorm=gn, reason="max_steps", steps=steps)
```

```python
# src/gdviz/theory.py
import numpy as np

def contraction_factor(lams, eta):  return float(np.max(np.abs(1 - eta * np.asarray(lams))))
def best_constant_step(lams):       l = np.asarray(lams); return float(2 / (l.max() + l.min()))
def best_rate(lams):                l = np.asarray(lams); k = l.max() / l.min(); return float((k - 1) / (k + 1))
def stability_threshold(lams):      return float(2 / np.max(lams))

def measured_rate(norms, tail_fraction=0.5):
    n = np.asarray(norms); tail = n[int(len(n) * (1 - tail_fraction)):]
    tail = tail[tail > 1e-250]
    if len(tail) < 5: return float("nan")
    return float(np.exp(np.polyfit(np.arange(len(tail)), np.log(tail), 1)[0]))
```

```python
# tests/test_theory.py
import numpy as np
from gdviz.engine import run_gd
from gdviz.theory import contraction_factor, best_constant_step, best_rate, stability_threshold, measured_rate

def quad(lams):
    A = np.diag(lams); return (lambda x: 0.5 * x @ A @ x), (lambda x: A @ x)

def test_threshold_matches_two_over_lambda_max():
    lams = np.array([1.0, 25.0]); f, g = quad(lams); thr = stability_threshold(lams)
    assert run_gd(g, [1, 1], eta=0.97 * thr, steps=20_000)["reason"] == "converged"
    assert run_gd(g, [1, 1], eta=1.03 * thr, steps=20_000)["reason"] == "diverged"

def test_measured_rate_matches_prediction():
    lams = np.array([1.0, 10.0]); f, g = quad(lams)
    for eta in (0.05, 0.1, best_constant_step(lams), 0.15):
        r = run_gd(g, [1.0, 1.0], eta, steps=400, g_tol=0.0)
        norms = np.linalg.norm(r["path"], axis=1)
        assert abs(measured_rate(norms) - contraction_factor(lams, eta)) < 1e-2

def test_best_step_gives_best_rate():
    lams = np.array([1.0, 100.0]); etas = np.linspace(1e-4, 0.0199, 400)
    rates = [contraction_factor(lams, e) for e in etas]
    assert abs(etas[int(np.argmin(rates))] - best_constant_step(lams)) < 1e-3
    assert np.isclose(min(rates), best_rate(lams), atol=1e-3)
```

`[VERIFY]` Confirm the `1e-2` rate tolerance and the `0.97`/`1.03` threshold margins by running the tests; at `η` very near the threshold, convergence/divergence takes many steps, so keep the margins and step budget consistent.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2 | All objective gradients pass the checker (`< 1e-6`); engine reports the right stop reason for converged/diverged/max-steps/`nan` cases |
| M2 | R3–R4 | Path and curve figures generated headlessly for ≥ 3 objectives with ≥ 4 learning rates; regimes annotated |
| M3 | R5–R6 | Empirical threshold within 2% of `2/λ_max` on ≥ 5 spectra; measured rate within 1% of prediction on a grid of 20 `η` values |
| M4 | R7 | Table of `κ`, `η*`, predicted/measured `ρ*`, steps-to-tolerance (from your run); fitted log-log slope reported |
| M5 | R8–R9 | Momentum stability region plot; standardization effect on `(w, b)` loss surface and steps-to-tolerance |
| M6 | R10–R11 | Regime classifier with a reported confusion matrix on generated curves; `REPORT.md` regenerated by one script |

### 9.5 Questions the write-up must answer

1. How close are the measured threshold and rate to the theory, and where do they deviate (and why)?
2. Why is the best constant step on an ill-conditioned problem *not* the smoothest?
3. How does momentum change the stability region and the oscillation pattern?
4. What does standardizing features do to the loss surface and the step count?
5. Which regime-classifier errors are most common, and what does that say about diagnosing real curves?

### 9.6 Failure modes to demonstrate

Sign error; `η` exactly at `2/λ_max` (non-convergent oscillation); `nan` propagation; the max-steps cap hit before convergence near the threshold; momentum with the plain-SGD `η`; plotting with linear contour levels; comparing paths started from different points; fitting a rate from the transient instead of the tail.

### 9.7 Stretch goals

1. Backtracking line-search path vs fixed-`η` path on Rosenbrock.
2. A 3-D loss surface with the path lifted onto it.
3. Add RMSprop/Adam to the engine (reusing Project 2's classes) and overlay paths.
4. The heavy-ball optimal parameters for a quadratic (`η`, `β` from `λ_min, λ_max`) and a measured `√κ` scaling `[VERIFY: formulas]`.
5. A noisy-gradient mode (additive Gaussian noise) to preview the SGD noise floor.

### 9.8 ML connection (README prompt)

Describe how each diagnostic maps to a training-run decision: threshold ↔ the largest safe learning rate, rate/conditioning ↔ when to standardize or switch optimizers, momentum region ↔ how to re-tune `η` when adding momentum, regime labels ↔ reading real loss curves.

### Check yourself (Unit 9)

1. Why fit the contraction rate from the tail of the trajectory?
2. What stop reasons must the engine distinguish, and why?

**Reference answers:** (1) The early part is dominated by transients from components that decay faster; only the tail follows the slowest component's rate. (2) `converged`, `diverged`, `max_steps`, `nan`: each implies a different fix, and conflating them (e.g., calling a step cap "converged") is a common reporting error.

---

## Unit 10 — Project: Optimizer comparison: SGD, momentum, Adam (`Projects/02-…md`)

### 10.1 Brief

Build `optcmp`: implementations of SGD, momentum, Nesterov, RMSprop, and Adam, plus a **fair benchmarking harness** that tunes each optimizer's learning rate, runs multiple seeds, and reports mean ± standard error with learning-rate sensitivity curves, on a suite of problems: ill-conditioned quadratics, Rosenbrock, logistic regression with mini-batches, and a tiny neural network.

**Industry framing:** optimizer comparisons are among the most commonly flawed experiments in ML: untuned baselines, single seeds, and unreported budgets. The deliverable is a harness that makes the honest version the easy version.

### 10.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Optimizers | `SGD(momentum, nesterov)`, `RMSprop`, `Adam` with the Unit 6 conventions documented; `step(params, grads)` for dict or array params; fresh state per run |
| R2 | Update-rule tests | First steps checked against hand calculations; momentum steady-state `η/(1−β)`; Adam first step ≈ `η·sign(g)`; optional PyTorch cross-check (if installed) with documented differences |
| R3 | Problem suite | (a) quadratics `κ ∈ {10, 100, 1000}`, (b) Rosenbrock, (c) logistic regression on synthetic data with mini-batches, (d) a 2-layer tanh network on a synthetic nonlinear 2-class problem (spirals/moons generated in code) with mini-batch training; each with train/validation split where relevant |
| R4 | Fair-budget protocol | Same budget in **gradient evaluations** for every optimizer; fixed batch size per problem; documented step counts |
| R5 | LR tuning | Log-spaced grid (≥ 9 values, 3 decades) **per optimizer and per problem**; select by validation metric (or final loss for deterministic problems); report the chosen `η` and where it sits in the grid (edge-of-grid selections are flagged and the grid extended) |
| R6 | Seeds and statistics | ≥ 10 seeds for stochastic problems; mean ± standard error; paired differences between optimizers (same seeds/data order) with a confidence interval |
| R7 | Sensitivity curves | Final metric vs `η` for every optimizer; quantify "width" of the good region (e.g., range of `η` within 2× of the best metric) |
| R8 | Steps-to-target | Gradient evaluations to reach a target loss; handle runs that never reach it (censoring) and report the fraction that did |
| R9 | Failure accounting | Count and report diverged/`nan` runs per optimizer and `η`; never silently drop them |
| R10 | Momentum/β and Adam hyper-sweeps | Sweep `β ∈ {0, 0.5, 0.9, 0.99}` and Adam's `β₂ ∈ {0.9, 0.99, 0.999}`, `ε ∈ {1e-8, 1e-4}`; report effects |
| R11 | Scale-invariance experiment | Multiply the loss by 100; show how each optimizer's best `η` shifts |
| R12 | Report | `REPORT.md`: tables with budgets, tuned `η`, mean ± SE, paired comparisons; **claims scoped to the problems tested**, including at least one problem where the "default favourite" does not win |

### 10.3 Layout and starter

```
optcmp/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/optcmp/{__init__,optimizers,problems,harness,stats,report}.py
├── tests/{test_optimizers,test_problems,test_harness,test_stats}.py
├── notebooks/08_optimizer_comparison.ipynb
└── results/
```

```python
# src/optcmp/optimizers.py
import numpy as np

class Optimizer:
    def step(self, x, g): raise NotImplementedError

class SGD(Optimizer):
    def __init__(self, lr, momentum=0.0, nesterov=False):
        self.lr, self.mu, self.nesterov, self.v = lr, momentum, nesterov, None
    def step(self, x, g):
        if self.mu == 0.0: return x - self.lr * g
        self.v = g.copy() if self.v is None else self.mu * self.v + g
        return x - self.lr * ((g + self.mu * self.v) if self.nesterov else self.v)

class RMSprop(Optimizer):
    def __init__(self, lr, rho=0.9, eps=1e-8): self.lr, self.rho, self.eps, self.s = lr, rho, eps, None
    def step(self, x, g):
        self.s = (1 - self.rho) * g * g if self.s is None else self.rho * self.s + (1 - self.rho) * g * g
        return x - self.lr * g / (np.sqrt(self.s) + self.eps)

class Adam(Optimizer):
    def __init__(self, lr, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.m, self.v, self.t = lr, b1, b2, eps, None, None, 0
    def step(self, x, g):
        self.t += 1
        if self.m is None: self.m, self.v = np.zeros_like(x), np.zeros_like(x)
        self.m = self.b1 * self.m + (1 - self.b1) * g
        self.v = self.b2 * self.v + (1 - self.b2) * g * g
        mh, vh = self.m / (1 - self.b1 ** self.t), self.v / (1 - self.b2 ** self.t)
        return x - self.lr * mh / (np.sqrt(vh) + self.eps)
```

```python
# src/optcmp/problems.py
import numpy as np

def logistic_problem(n=2000, d=10, seed=0, scales=None):
    g = np.random.default_rng(seed)
    X = g.normal(size=(n, d)) * (np.ones(d) if scales is None else scales)
    w = g.normal(size=d); y = (g.random(n) < 1 / (1 + np.exp(-X @ w / np.sqrt(d)))).astype(float)
    cut = int(0.8 * n); return (X[:cut], y[:cut]), (X[cut:], y[cut:])

def logloss(w, X, y):
    z = X @ w; return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))))

def logloss_grad(w, X, y):
    return X.T @ (1 / (1 + np.exp(-(X @ w))) - y) / len(y)
```

```python
# src/optcmp/harness.py
import numpy as np

def run_minibatch(make_opt, grad_fn, x0, n, batch, evals_budget, seed, eval_fn=None, eval_every=None):
    """Mini-batch loop with per-epoch shuffling; returns (final_x, curve, status)."""
    g = np.random.default_rng(seed); x = np.array(x0, float); opt = make_opt(); evals = 0; curve = []
    while evals < evals_budget:
        perm = g.permutation(n)
        for s in range(0, n, batch):
            idx = perm[s:s + batch]
            x = opt.step(x, grad_fn(x, idx)); evals += len(idx)
            if not np.all(np.isfinite(x)): return x, curve, "nan"
            if eval_fn is not None and eval_every and (evals // len(idx)) % eval_every == 0: curve.append((evals, eval_fn(x)))
            if evals >= evals_budget: break
    return x, curve, "ok"

def tune_lr(make_opt_for_lr, lrs, run_for_lr, seeds):
    """Return {lr: array of final metrics over seeds (np.inf for diverged runs)}."""
    out = {}
    for lr in lrs:
        vals = []
        for s in seeds:
            m = run_for_lr(lr, s); vals.append(m if np.isfinite(m) else np.inf)
        out[lr] = np.array(vals)
    return out
```

```python
# src/optcmp/stats.py
import numpy as np

def mean_se(a):
    a = np.asarray(a, float); return float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))

def paired_diff_ci(a, b, z=1.96):
    d = np.asarray(a, float) - np.asarray(b, float); m, se = d.mean(), d.std(ddof=1) / np.sqrt(len(d))
    return float(m), float(m - z * se), float(m + z * se)
```

```python
# tests/test_optimizers.py
import numpy as np
from optcmp.optimizers import SGD, RMSprop, Adam

def test_sgd_step():
    g = np.array([1.0, -2.0]); assert np.allclose(SGD(0.1).step(np.zeros(2), g), -0.1 * g)

def test_adam_first_step_is_lr_sign_g():
    g = np.array([0.5, -2.0, 1e-3]); x1 = Adam(0.01).step(np.zeros(3), g)
    assert np.allclose(np.abs(x1), 0.01, rtol=1e-3, atol=2e-3)       # the tiny gradient sees ε: tolerance is loose for it
    assert np.all(np.sign(x1[:2]) == -np.sign(g[:2]))

def test_momentum_steady_state():
    o, x = SGD(0.1, 0.9), np.zeros(1); last = 0.0
    for _ in range(200):
        xn = o.step(x, np.array([1.0])); last = float((x - xn)[0]); x = xn
    assert np.isclose(last, 0.1 / (1 - 0.9), rtol=1e-3)

def test_all_converge_on_a_quadratic():
    A = np.diag([1.0, 10.0])
    for o in (SGD(0.05), SGD(0.02, 0.9), SGD(0.02, 0.9, True), RMSprop(0.01), Adam(0.05)):
        x = np.array([1.0, 1.0])
        for _ in range(5000): x = o.step(x, A @ x)
        assert np.linalg.norm(x) < 0.5                                # [VERIFY] loose bound: RMSprop/Adam hover near the optimum with a constant step
```

```python
# tests/test_stats.py
import numpy as np
from optcmp.stats import mean_se, paired_diff_ci

def test_mean_se_and_paired_ci():
    a = np.array([1.0, 2.0, 3.0, 4.0]); m, se = mean_se(a)
    assert np.isclose(m, 2.5) and np.isclose(se, a.std(ddof=1) / 2)
    d, lo, hi = paired_diff_ci(a + 0.5, a)                            # constant difference → zero-width interval
    assert np.isclose(d, 0.5) and np.isclose(lo, hi)
```

`[VERIFY]` Run `test_all_converge_on_a_quadratic` to confirm the loose `0.5` bound is a fair statement for RMSprop/Adam at these constant step sizes, and tighten it only with evidence (constant-step RMSprop/Adam typically oscillate in a neighbourhood of the optimum).

### 10.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2 | All update-rule tests pass; optional PyTorch cross-check differences documented (momentum form, `ε` placement) |
| M2 | R3–R4 | Problem suite implemented; every optimizer receives the same evaluation budget; budgets recorded in the results |
| M3 | R5–R7 | LR grids per optimizer/problem; no best-`η` at a grid edge (extend if so); sensitivity curves with the good-region width |
| M4 | R6, R8–R9 | ≥ 10 seeds; mean ± SE; paired-difference CIs; steps-to-target with censoring; divergence counts reported |
| M5 | R10–R11 | `β`, `β₂`, `ε` sweeps and the loss-scale experiment, each with a one-paragraph interpretation |
| M6 | R12 | `REPORT.md` regenerated by one script; every claim cites a table/figure with `N`, seeds, budgets; scope statement present |

### 10.5 Statistical-honesty requirements

- **Tune every optimizer equally** (same grid size, same number of seeds, same selection metric). Say so in the report.
- **Select `η` on a validation set**, then report on a separate test/held-out set when applicable; do not report the tuning metric as the result.
- **Report failures**: diverged and `nan` runs are results.
- **Report uncertainty**: mean ± SE and paired CIs; do not rank optimizers whose intervals overlap.
- **Scope the conclusion**: the findings hold for these problems, budgets, and batch sizes only. Include at least one result that contradicts the folklore ("Adam always wins" or "SGD always generalizes better").

### 10.6 Failure modes to demonstrate

Shared `η` across optimizers (misleading winner); best `η` at the grid edge; single seed; comparing by steps instead of gradient evaluations; leaking validation data into tuning; ignoring diverged runs when averaging; Adam `ε` too large or too small; momentum with SGD's `η`; loss-scale change shifting SGD's best `η` but not Adam's.

### 10.7 Stretch goals

1. Add AdamW (decoupled weight decay) and compare with Adam + L2 on a regularized logistic problem `[VERIFY: AdamW definition]`.
2. Learning-rate schedules (step, cosine, warmup) added to the harness; study their effect per optimizer.
3. Learning-rate **range test** automated and compared with the grid-search optimum.
4. Gradient-noise measurement: estimate the gradient noise scale at several points of training and relate it to the best batch size `[VERIFY: definition]`.
5. A real small dataset available locally (if you have one) replacing the synthetic problems; report how conclusions change.

### 10.8 ML connection (README prompt)

Write a one-page "optimizer selection runbook" for a new model: what to try first, how to tune the learning rate, how many seeds are enough to make a decision, what to log, and which results in this project justify each recommendation.

### Check yourself (Unit 10)

1. Why must each optimizer's learning rate be tuned separately?
2. What does a best learning rate at the grid edge mean?
3. Why compare optimizers per gradient evaluation instead of per step?

**Reference answers:** (1) Each optimizer's good-`η` region sits at a different scale, so a shared `η` penalizes whichever optimizer it mismatches. (2) The true optimum may lie outside the grid, so the comparison is not yet fair; extend the grid. (3) Steps can process different numbers of samples (full-batch vs mini-batch), so only evaluations measure equal compute.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 5 lessons, 2 projects, 10 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 13–14, 4C-03/05/07, and Stage 5 pointers (5A-03/04/05/11, 5B-02, 5C-03, 5D-06/10) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: Huber `δ ≈ 1.35σ̂` rationale, finite-population variance factor, Robbins–Monro conditions, linear/√ batch-size scaling, `O(1/k)` and `√κ` momentum rates, Adam/AdamW details, framework conventions for momentum and `ε`.
4. `[VERIFY]` All printed numerical results (iteration counts, rates, variances, success rates, optimizer rankings) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, SymPy 1.14): every lesson snippet executed (also under `-W error`); all 3 `gdviz` and all 5 `optcmp` tests passed. Findings from those runs that the final lesson files must reflect: (a) predicted and measured GD contraction factors on quadratics matched to the printed precision, and steps-to-tolerance at the best constant step grew about linearly in `κ` (1, 13, 71, 709, 7082 steps for `κ = 1, 2, 10, 100, 1000`); (b) minibatch-gradient variance times `B` stayed near constant (about 150–166 for `B = 1…256`), matching the finite-population formula; (c) on a `κ = 100` quadratic RMSprop was fastest when the curvature was axis-aligned (150 steps) but did not reach the tolerance when the same quadratic was rotated 45°, where momentum (166) and Adam (212) did; (d) without bias correction Adam's first step was 3.16× too **large** at the defaults (not too small); (e) in a tuned comparison on a badly scaled logistic problem (6 seeds, 30 epochs, batch 32) SGD, SGD+momentum, and Adam reached validation losses within 0.001 of each other (0.3462, 0.3457, 0.3468), so the paired difference was statistically detectable but practically negligible; (f) logistic loss does not blow up at large `η` (bounded gradients): the LR-range-test rise appeared near `η ≈ 9` while `1/L ≈ 0.42`. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, accuracy, convergence-rate, or ranking claim appears without the measurement that produced it.
