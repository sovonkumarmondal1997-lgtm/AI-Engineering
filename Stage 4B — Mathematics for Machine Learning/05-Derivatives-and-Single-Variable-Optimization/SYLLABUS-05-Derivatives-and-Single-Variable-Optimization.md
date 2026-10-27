# SYLLABUS — 05-Derivatives-and-Single-Variable-Optimization (S4B-05)

**Stage 4B — Mathematics for Machine Learning · Module 05 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy; SymPy is needed for Project 1 and for symbolic cross-checks; Matplotlib and pytest where stated. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | The derivative from limits: slope of a curve | `01-the-derivative-from-limits-slope-of-a-curve.md` | Beginner |
| 3 | Derivative rules | `02-derivative-rules.md` | Beginner |
| 4 | Derivatives of exponential, logarithmic, trigonometric functions | `03-derivatives-of-exponential-logarithmic-and-trigonometric-functions.md` | Beginner → Intermediate |
| 5 | The chain rule | `04-the-chain-rule.md` | Intermediate |
| 6 | Derivatives of sigmoid, tanh, ReLU | `05-derivatives-of-sigmoid-tanh-and-relu.md` | Intermediate |
| 7 | Second derivatives and curvature | `06-second-derivatives-and-curvature.md` | Intermediate |
| 8 | Finding minima and maxima | `07-finding-minima-and-maxima.md` | Intermediate |
| 9 | Numerical vs analytical derivatives and gradient checking | `08-numerical-versus-analytical-derivatives-and-gradient-checking.md` | Intermediate → Advanced |
| 10 | Practice question bank | `practice-questions.md` | All levels |
| 11 | Project index | `Projects/README.md` | Intermediate |
| 12 | Project: symbolic and numerical derivative comparison | `Projects/01-symbolic-and-numerical-derivative-comparison.md` | Intermediate → Advanced |
| 13 | Project: numerical gradient checker | `Projects/02-numerical-gradient-checker.md` | Advanced |

**Prerequisites:** Stage 4A Module 13 (limits and rates of change), Module 05–07 (exponents, logarithms, functions and graphs), Module 04 (solving equations). Module 01–02 of this stage for vector and shape habits. **Plan slot:** weeks 6–7 of `../00-Stage-4-Overview/learning-plan.md` (lessons 1–5, then 6–8). **Checkpoint:** gradient checker passes (relative error < `1e-6`) on sigmoid, tanh, softplus, and a composed function.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Training a model means changing parameters to reduce a loss, and the derivative tells you **how the loss responds to each parameter**. Every optimizer in Module 08, every backpropagation step in Module 07 and Stage 5C, and every "why is my loss NaN?" investigation rests on the ideas here. This module is deliberately **single-variable**: you learn the machinery on one dimension, where you can plot everything, then Module 07 lifts it to many.

### 1.2 Outcomes

1. Explain the derivative as the limit of secant slopes, as a rate of change, and as the best local linear approximation.
2. Differentiate polynomials, products, quotients, exponentials, logs, and trig functions, and check each result numerically.
3. Apply the chain rule to compositions and draw the forward/backward computation as a chain of local derivatives.
4. Derive and implement the derivatives of sigmoid, tanh, ReLU (and softplus), and explain saturation and "dying ReLU".
5. Use the second derivative to classify critical points, reason about curvature, and predict a stable learning rate on a quadratic.
6. Find minima numerically with gradient descent, Newton's method, and derivative-free search, and recognise local minima, saddles, and non-differentiable minima.
7. Implement finite-difference, complex-step, and forward-mode (dual-number) derivatives, and explain their error behaviour.
8. Write a reusable gradient checker and use it to catch injected bugs.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Derivative from limits | Sensitivity of loss to a parameter | Secant-to-tangent plot; error-vs-`h` curve |
| 2 | Rules | Derivatives of squared error and penalties | Rule table + numeric checks |
| 3 | Exp / log / trig | Log-loss, softplus, log-likelihood | Derivative catalogue |
| 4 | Chain rule | Backprop as a chain of local derivatives | Forward/backward on a tiny chain |
| 5 | Sigmoid / tanh / ReLU | Activations, vanishing gradients | Saturation experiments |
| 6 | Second derivatives | Curvature and learning rate | Stable-step experiment |
| 7 | Minima and maxima | Loss minimization, local minima | 1-D optimizers |
| 8 | Numerical vs analytical | Gradient checking, autodiff | `numerical_grad`, complex-step, `Dual` |

### 1.4 Concept map

```
limit of secant slopes ─► derivative f'(x) ─► rules (sum, product, quotient)
                               │                     │
                               │                     └► exp, log, trig ─► sigmoid, tanh, ReLU, softplus
                               ├► chain rule ─► backprop (Module 07)
                               ├► f'' ─► curvature ─► learning-rate limit (Module 08)
                               ├► f' = 0 ─► minima / maxima / saddle ─► optimization
                               └► numerical check: central difference, complex step, dual numbers ─► gradcheck
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "sympy>=1.12" matplotlib pytest
```

Rules for every lab: **derive by hand, then check numerically, then check symbolically**; report relative error, not just "looks right"; test away from non-differentiable points and at them on purpose; seed any randomness; use `float64` for checks.

### 1.6 Checkpoint

Your gradient checker reports relative error `< 1e-6` for sigmoid, tanh, softplus, and a composed function such as `softplus(tanh(3x) − x²)`, **and** flags an injected bug (e.g., a missing factor) with error `> 1e-3`.

### Check yourself (Unit 1)

1. Give three interpretations of `f′(x)`.
2. Why does this module stay single-variable?

**Reference answers:** (1) Limit of secant slopes; instantaneous rate of change; slope of the best local linear approximation. (2) So every idea can be plotted and verified before Module 07 generalizes to gradients.

---

## Unit 2 — The derivative from limits: slope of a curve (`01-…md`)

### 2.1 Why ML needs this

A derivative answers "if I nudge this parameter by a tiny amount, how much does the loss change?" That sentence is the whole of gradient-based learning. It also underlies finite-difference checks, which you will use to test every hand-written gradient.

### 2.2 Intuition

Take two points on a curve and draw the line through them (a **secant**). Slide the second point toward the first. The secant's slope settles to a number: the slope of the **tangent**. That number is the derivative. Equivalently, near `x`, the function looks like a straight line: `f(x + h) ≈ f(x) + f′(x)·h`.

### 2.3 Mechanics

- **Definition:** `f′(x) = lim_{h→0} [f(x + h) − f(x)] / h`.
- **Finite-difference approximations** (what you compute on a machine):

| Scheme | Formula | Truncation error |
|---|---|---|
| Forward | `[f(x+h) − f(x)]/h` | `O(h)` |
| Backward | `[f(x) − f(x−h)]/h` | `O(h)` |
| Central | `[f(x+h) − f(x−h)]/(2h)` | `O(h²)` |

- **The two-sided trade-off:** shrinking `h` reduces truncation error but **amplifies floating-point round-off** (subtracting nearly equal numbers loses digits). Total error is V-shaped in `h`. Rules of thumb for `float64` `[JUDGEMENT]`: forward `h ≈ √ε·|x| ≈ 1e-8·|x|`, central `h ≈ ε^{1/3}·|x| ≈ 6e-6·|x|`, where `ε ≈ 2.2e-16`. Use `max(|x|, 1)` as the scale.
- **Differentiability:** `f` must have a well-defined tangent. `|x|` at `0` has a corner (left slope `−1`, right slope `+1`): no derivative. ReLU at `0` is the same. Continuity does **not** imply differentiability.
- **Subgradient (preview):** at a corner, any slope between the left and right slopes is a valid "sub-derivative". Frameworks pick a convention (e.g., ReLU′(0) = 0).
- **Meaning of the sign and size:** `f′ > 0` increasing, `f′ < 0` decreasing, `f′ = 0` flat (candidate extremum), `|f′|` large means steep.
- **Gradient descent in one line:** `x ← x − η f′(x)` moves downhill.

**Worked example:** `f(x) = x²` at `x = 3`: secant slope from `3` to `3 + h` is `(6h + h²)/h = 6 + h → 6`, so `f′(3) = 6`. Linear approximation: `f(3.01) ≈ 9 + 6(0.01) = 9.06` versus exact `9.0601`.

### 2.4 Code

```python
import numpy as np

def forward_diff(f, x, h=1e-8):  return (f(x + h) - f(x)) / h
def backward_diff(f, x, h=1e-8): return (f(x) - f(x - h)) / h
def central_diff(f, x, h=1e-5):  return (f(x + h) - f(x - h)) / (2 * h)

f = lambda x: x ** 2
assert np.isclose(central_diff(f, 3.0), 6.0, atol=1e-8)

# secant slopes converging to the tangent slope
for h in (1.0, 0.1, 0.01, 0.001, 1e-6):
    print(f"h={h:<8g} secant slope = {(f(3 + h) - f(3)) / h:.6f}")      # → 6

# linear approximation quality
x0, h = 3.0, 0.01
print(f(x0 + h), f(x0) + 6.0 * h, abs(f(x0 + h) - (f(x0) + 6.0 * h)))   # error is O(h²)

# the V-shaped error curve: truncation vs round-off
g, dg, x0 = np.sin, np.cos, 1.0
hs = np.logspace(-16, 0, 33)
err_fwd = [abs(forward_diff(g, x0, h) - dg(x0)) for h in hs]
err_cen = [abs(central_diff(g, x0, h) - dg(x0)) for h in hs]
print("best forward h ≈", hs[int(np.argmin(err_fwd))], " best central h ≈", hs[int(np.argmin(err_cen))])
# report your own minimum errors; do not quote values you did not measure

# non-differentiable point: left and right slopes disagree
a = lambda x: abs(x)
print(backward_diff(a, 0.0, 1e-6), forward_diff(a, 0.0, 1e-6))          # -1.0  and  1.0
```

Plot (Matplotlib): `log-log` error vs `h` for forward and central differences; mark the optimum; add reference lines with slopes `+1` and `+2` in the truncation-dominated region, and a `−1` line in the round-off region.

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `h` too small (`1e-12`) | Noisy or zero derivative (catastrophic cancellation) | Use `h ≈ 1e-5` central; `1e-8` forward; scale by `max(|x|, 1)` |
| `h` too large | Biased derivative (truncation) | Compare two `h` values; error should shrink as predicted |
| Differentiating at a corner (`|x|`, ReLU at 0) | Meaningless number, differs by scheme | Check left/right slopes; use a subgradient convention |
| `float32` arithmetic | Only ~3–4 reliable digits | Use `float64` for checks |
| Integer `x` inputs | Division/rounding oddities | `float(x)` |
| Evaluating `f` outside its domain at `x ± h` (e.g., `log` near 0) | `nan`/`-inf` | Choose `h` smaller than the distance to the boundary |

### 2.6 ML link

- **Sensitivity of loss to a weight:** `∂L/∂w` is the derivative with the other parameters frozen (Module 07 generalizes).
- **Gradient descent:** the update uses the sign and size of the slope (Module 08).
- **Finite differences as a debugging oracle:** Lesson 8 and both projects.
- **ReLU at 0:** frameworks use a convention; it rarely matters because exact zeros are measure-zero for continuous inputs, but it matters for integer-valued or zero-padded inputs `[JUDGEMENT]`.

### 2.7 Lab (60 min)

1. Plot a curve with secants for `h ∈ {2, 1, 0.5, 0.1}` converging to the tangent at a chosen point.
2. Build the V-shaped error plot for three functions (`sin`, `exp`, `x³`) at three points; record the best `h` for each scheme.
3. Show that halving `h` halves the forward error and quarters the central error in the truncation regime (fit the slopes on a log-log plot).
4. Evaluate derivatives of `|x|` and ReLU around `0`, and describe what each scheme returns.

### Check yourself (Unit 2)

1. Why is central difference more accurate than forward difference?
2. What happens to a finite-difference derivative as `h → 1e-16`, and why?
3. Is `|x|` continuous at 0? Differentiable?

**Reference answers:** (1) Its truncation error is `O(h²)` because the first-order error terms cancel by symmetry. (2) It becomes garbage (often `0` or noise): `f(x+h) − f(x)` underflows to cancellation error. (3) Continuous, not differentiable (corner).

---

## Unit 3 — Derivative rules (`02-…md`)

### 3.1 Why ML needs this

Losses and activations are assembled from sums, products, and quotients of simple pieces. Knowing the rules lets you differentiate a loss by hand, which you need for debugging and for understanding what autodiff computes.

### 3.2 Mechanics

| Rule | Formula |
|---|---|
| Constant | `(c)′ = 0` |
| Constant multiple | `(c f)′ = c f′` |
| Sum / difference | `(f ± g)′ = f′ ± g′` |
| Power | `(xⁿ)′ = n xⁿ⁻¹` (any real `n`, where defined) |
| Product | `(f g)′ = f′ g + f g′` |
| Quotient | `(f/g)′ = (f′ g − f g′)/g²`, `g ≠ 0` |
| Reciprocal | `(1/g)′ = −g′/g²` |
| Linearity | derivative is a linear operator: `(αf + βg)′ = αf′ + βg′` |

- **Polynomial:** `p(x) = Σ aₖxᵏ → p′(x) = Σ k aₖ xᵏ⁻¹`.
- **Common mistake:** `(f g)′ ≠ f′ g′`; `(f/g)′ ≠ f′/g′`.
- **Worked ML example (one parameter):** squared error `L(w) = (w x − y)²` for fixed `x, y`:
  `L′(w) = 2(w x − y)·x`. Set `L′ = 0` ⇒ `w* = y/x`, the weight that fits that single point exactly.
- **Mean squared error over `n` points, one weight, no intercept:** `L(w) = (1/n) Σ (w xᵢ − yᵢ)²` ⇒ `L′(w) = (2/n) Σ (w xᵢ − yᵢ) xᵢ` ⇒ `w* = Σ xᵢyᵢ / Σ xᵢ²` (the projection coefficient from Module 01, Lesson 4).
- **L2 penalty:** `d/dw [λ w²] = 2λ w` (the "weight decay" force pulls `w` toward zero).
- **L1 penalty:** `d/dw [λ |w|] = λ·sign(w)` for `w ≠ 0` (constant-size push; non-differentiable at 0).

### 3.3 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def num_deriv(f, x, h=1e-5): return (f(x + h) - f(x - h)) / (2 * h)

f, g = (lambda x: x ** 3 + 2 * x), (lambda x: np.sin(x) + 3)
fp, gp = (lambda x: 3 * x ** 2 + 2), (lambda x: np.cos(x))

for x in rng.uniform(-2, 2, 20):
    assert np.isclose(num_deriv(lambda t: f(t) * g(t), x), fp(x) * g(x) + f(x) * gp(x), rtol=1e-6, atol=1e-8)          # product
    assert np.isclose(num_deriv(lambda t: f(t) / g(t), x), (fp(x) * g(x) - f(x) * gp(x)) / g(x) ** 2, rtol=1e-6, atol=1e-8)  # quotient
    wrong = fp(x) * gp(x)                                                                                          # the classic mistake: (fg)' ≠ f'g'
    assert abs(num_deriv(lambda t: f(t) * g(t), x) - wrong) > 1e-3 or abs(wrong) < 1e-3                             # the wrong formula disagrees (except by coincidence)

# MSE with one weight: derivative and closed-form minimum
x = rng.normal(size=50); y = 2.0 * x + rng.normal(scale=0.1, size=50)
L  = lambda w: np.mean((w * x - y) ** 2)
dL = lambda w: 2 * np.mean((w * x - y) * x)
for w in (-1.0, 0.5, 3.0):
    assert np.isclose(dL(w), num_deriv(L, w), rtol=1e-6)
w_star = (x @ y) / (x @ x)
assert abs(dL(w_star)) < 1e-12

# gradient descent in 1-D
w = 0.0
for _ in range(100): w -= 0.5 * dL(w)
assert np.isclose(w, w_star, atol=1e-6)

# penalties: L2 is smooth, L1 has a kink at 0
l2, l1 = (lambda w: w ** 2), (lambda w: abs(w))
print(num_deriv(l2, 0.0), num_deriv(l1, 1e-3), num_deriv(l1, -1e-3))     # 0.0, 1.0, -1.0
```

Symbolic cross-check (SymPy):

```python
import sympy as sp
x = sp.symbols("x")
expr = (x**3 + 2*x) * (sp.sin(x) + 3)
print(sp.simplify(sp.diff(expr, x)))
d = sp.lambdify(x, sp.diff(expr, x), "numpy")
assert np.isclose(d(0.7), num_deriv(sp.lambdify(x, expr, "numpy"), 0.7), rtol=1e-6)
```

### 3.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `(fg)′ = f′g′` | Wrong gradient that "looks plausible" | Numeric check at random points |
| Forgetting the `1/n` in the mean loss | Gradient off by a constant factor | Check `dL` vs numeric |
| Quotient rule sign error | Wrong sign | Verify with SymPy and numerics |
| Differentiating at a kink (`|w|` at 0) | Undefined | Use `sign(w)` with a convention; subgradient |
| Sum vs mean in the loss | Learning-rate sensitivity changes by `n` | State the reduction explicitly |
| Dividing by a function that crosses zero | Infinite derivative | Check the domain |

### 3.5 ML link

- **MSE gradient (Module 14):** exactly the one-weight derivative above, in vector form.
- **Weight decay:** L2 term contributes `2λw` to the gradient (`λw` in the common `½λw²` convention; check your framework `[VERIFY]`).
- **Lasso (Module 14):** `λ·sign(w)` pushes small weights to exactly zero.
- **Reduction choice (sum vs mean):** changes the effective learning rate.

### 3.6 Lab (45 min)

1. Build a rule table and verify each rule on 20 random points with relative error `< 1e-6`.
2. Derive and verify the MSE gradient for one weight; find `w*` three ways: closed form, gradient descent, and `scipy`-free bisection on `L′`.
3. Show the L1 and L2 penalty derivatives and describe the behaviour near `0`.
4. Make the classic mistake deliberately, catch it with the numeric check, and write a regression test.

### Check yourself (Unit 3)

1. Differentiate `x² sin x`.
2. Differentiate `1/(1 + x²)`.
3. For `L(w) = (1/n)Σ(w xᵢ − yᵢ)²`, where is the minimum?

**Reference answers:** (1) `2x sin x + x² cos x`. (2) `−2x/(1 + x²)²`. (3) `w* = Σxᵢyᵢ / Σxᵢ²`.

---

## Unit 4 — Derivatives of exponential, logarithmic, and trigonometric functions (`03-…md`)

### 4.1 Why ML needs this

Probabilities are multiplied, so likelihoods use logs; sigmoids and softmaxes are built from exponentials; positional encodings use sines and cosines. The log-loss gradient and the sigmoid derivative both fall out of these few formulas.

### 4.2 Mechanics

| Function | Derivative | Domain / note |
|---|---|---|
| `eˣ` | `eˣ` | Its own derivative: the defining property of `e` |
| `aˣ` | `aˣ ln a` | `a > 0` |
| `ln x` | `1/x` | `x > 0` |
| `log_a x` | `1/(x ln a)` | |
| `sin x` | `cos x` | radians |
| `cos x` | `−sin x` | radians |
| `tan x` | `1/cos² x = 1 + tan² x` | undefined where `cos x = 0` |
| `softplus(x) = ln(1 + eˣ)` | `eˣ/(1 + eˣ) = σ(x)` | smooth ReLU |
| `ln(f(x))` | `f′/f` | **logarithmic derivative**; useful for products |

- **Log turns products into sums:** `ln(Πpᵢ) = Σ ln pᵢ`, so the derivative of a log-likelihood is a sum of simple terms.
- **Log-derivative trick:** `f′ = f · (ln f)′`. It is the basis of the policy-gradient identity in RL (Stage 5B-13) `[VERIFY]`.
- **Worked ML example (log loss for one probability):** `ℓ(p) = −ln p` ⇒ `ℓ′(p) = −1/p`, which blows up as `p → 0`: confident wrong predictions are punished hard, and clipping or logit-space computation is needed for stability.
- **Derivatives of trig use radians.** `sin(°)` in degrees picks up a factor `π/180`.
- **Sinusoidal positional encodings** `sin(pos/10000^{2i/d})` have derivatives that are shifted sinusoids (Stage 5C-07 `[VERIFY]`).

### 4.3 Code

```python
import numpy as np
num = lambda f, x, h=1e-5: (f(x + h) - f(x - h)) / (2 * h)
rng = np.random.default_rng(0)
xs = rng.uniform(0.2, 3.0, 25)

table = {
    "exp":      (np.exp,                    np.exp),
    "2^x":      (lambda x: 2.0 ** x,        lambda x: 2.0 ** x * np.log(2.0)),
    "ln":       (np.log,                    lambda x: 1.0 / x),
    "log10":    (np.log10,                  lambda x: 1.0 / (x * np.log(10.0))),
    "sin":      (np.sin,                    np.cos),
    "cos":      (np.cos,                    lambda x: -np.sin(x)),
    "tan":      (np.tan,                    lambda x: 1.0 / np.cos(x) ** 2),
    "softplus": (lambda x: np.log1p(np.exp(x)), lambda x: 1.0 / (1.0 + np.exp(-x))),
}
for name, (f, df) in table.items():
    err = max(abs(num(f, x) - df(x)) / max(1.0, abs(df(x))) for x in xs)
    assert err < 1e-6, (name, err)
    print(f"{name:9s} max relative error {err:.1e}")

# stable softplus and its derivative for large |x|
def softplus(x):  return np.logaddexp(0.0, x)                       # ln(1+e^x) without overflow
def sigmoid(x):   return np.where(x >= 0, 1 / (1 + np.exp(-np.abs(x))), np.exp(-np.abs(x)) / (1 + np.exp(-np.abs(x))))
assert np.isfinite(softplus(1000.0)) and np.isclose(softplus(-1000.0), 0.0)
assert np.isclose(num(softplus, 0.7), sigmoid(0.7), rtol=1e-6)
# naive version overflows:
with np.errstate(over="ignore"): print(np.log1p(np.exp(1000.0)))     # inf

# log loss behaviour near 0 and the logit-space fix
p = np.array([0.5, 0.1, 1e-3, 1e-8]); print(-np.log(p), -1 / p)      # loss and slope explode
def bce_with_logits(z, y):                                           # stable: max(z,0) - z y + log(1+e^{-|z|})
    return np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))
z = np.array([-50.0, 0.0, 50.0]); y = np.array([1.0, 1.0, 0.0])
print(bce_with_logits(z, y))                                         # finite: [50, 0.693, 50]

# degrees vs radians
f_deg = lambda d: np.sin(np.deg2rad(d))
print(num(f_deg, 30.0), np.cos(np.deg2rad(30.0)) * np.pi / 180)      # factor pi/180 appears
```

SymPy cross-check:

```python
import sympy as sp
x = sp.symbols("x", positive=True)
for e in (sp.exp(x), 2**x, sp.log(x), sp.tan(x), sp.log(1 + sp.exp(x))):
    print(e, "→", sp.simplify(sp.diff(e, x)))
```

### 4.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `log(0)` or `log` of a negative | `-inf` / `nan` | Clip with `eps`, or compute in logit space |
| `exp` of a large number | `inf` and later `nan` | `logaddexp`, subtract the max, stable forms |
| `log(1 + exp(x))` for large `x` | Overflow | `np.logaddexp(0, x)` |
| Degrees in trig derivatives | Off by `π/180` | Convert to radians |
| `tan` near `π/2` | Huge values, noisy derivatives | Avoid or reparameterize |
| `ln` of a *sum* treated as a sum of `ln`s | Wrong algebra | `ln(a + b) ≠ ln a + ln b` |
| Differentiating `log10`/`log2` as `ln` | Constant factor off | Include `1/ln a` |

### 4.5 ML link

- **Cross-entropy / log loss (Module 13, 14):** `−ln p` and its derivative; why logits-based losses exist.
- **Softplus** appears in smooth ReLU variants and as the `log(1+eˣ)` inside stable BCE.
- **Log-likelihood** turns products into sums (4C-05).
- **Policy gradients:** log-derivative trick (Stage 5B-13).
- **Positional encodings:** sinusoids (Stage 5C-07).

### 4.6 Lab (60 min)

1. Verify the full derivative table at 25 random points each; report the max relative error for each function.
2. Show overflow of the naive `log(1 + exp(x))` and fix with `logaddexp`; compare against `softplus` derivative `σ(x)`.
3. Plot `−ln p` and `−1/p` for `p ∈ (0, 1]`; explain the clipping issue.
4. Implement `bce_with_logits` and its derivative `σ(z) − y`; check numerically across `z ∈ [−50, 50]`.

### Check yourself (Unit 4)

1. What is `d/dx ln(1 + e^x)`?
2. Why is `−ln p` dangerous near `p = 0`?
3. What is `d/dx 3ˣ`?

**Reference answers:** (1) `σ(x) = eˣ/(1 + eˣ)`. (2) It tends to infinity with an infinite slope; floating-point `p = 0` gives `inf` and NaN gradients; use logits or clip. (3) `3ˣ ln 3`.

---

## Unit 5 — The chain rule (`04-…md`)

### 5.1 Why ML needs this

A neural network is a composition of simple functions, and the chain rule is how you differentiate one. Backpropagation is **exactly** the chain rule applied systematically, reusing intermediate values from the forward pass. Understanding it on a one-variable chain makes Module 07 and Stage 5C straightforward.

### 5.2 Intuition

If `y` changes `3×` as fast as `u`, and `u` changes `2×` as fast as `x`, then `y` changes `6×` as fast as `x`. **Rates multiply along a chain.**

### 5.3 Mechanics

- **Chain rule:** `d/dx f(g(x)) = f′(g(x)) · g′(x)`.
- **Leibniz form:** `dy/dx = (dy/du)(du/dx)`; for a longer chain `x → u → v → y`: `dy/dx = (dy/dv)(dv/du)(du/dx)`.
- **Computational graph:** break an expression into elementary nodes; compute **forward** values `x → u → v → y`, then compute **local derivatives** at each node and multiply **backward** from the output.
- **Reverse-mode idea:** to get `dL/dx` for many inputs, start with `dL/dL = 1` and push backward, reusing forward values. Cost is a small multiple of the forward pass (Module 07, 4C-07).
- **Worked example:** `y = (3x + 1)²`: `u = 3x + 1`, `y = u²` ⇒ `dy/dx = 2u · 3 = 6(3x + 1)`.
- **Worked ML example (logistic regression, one feature):** `z = w x + b`, `p = σ(z)`, `L = −[y ln p + (1−y) ln(1−p)]`.
  - `dL/dp = −y/p + (1−y)/(1−p)`
  - `dp/dz = p(1−p)`
  - `dz/dw = x`
  - Chain: `dL/dw = (dL/dp)(dp/dz)(dz/dw) = (p − y)·x`. The `p(1−p)` cancels, which is why cross-entropy plus sigmoid is "nice".
- **Vanishing/exploding gradients:** a long chain multiplies many local factors; if they are all `< 1` the product vanishes, if `> 1` it explodes. For a depth-`n` sigmoid chain the factor is at most `0.25ⁿ` (Lesson 5).
- **Shared variables:** if `x` feeds into two branches, derivatives from both paths **add** (preview of multivariable chain rule, Module 07).

### 5.4 Code

```python
import numpy as np
num = lambda f, x, h=1e-6: (f(x + h) - f(x - h)) / (2 * h)

# y = (3x+1)^2 via an explicit forward/backward pass
def forward_backward(x):
    u = 3 * x + 1                  # forward
    y = u ** 2
    dy_du = 2 * u                  # local derivatives
    du_dx = 3.0
    return y, dy_du * du_dx        # chain
y, dy = forward_backward(0.7)
assert np.isclose(dy, num(lambda t: (3 * t + 1) ** 2, 0.7), rtol=1e-8)

# a longer chain as a list of (function, derivative) pairs
chain = [
    (lambda x: 3 * x + 1,   lambda x: 3.0),
    (np.tanh,               lambda x: 1 - np.tanh(x) ** 2),
    (lambda x: x ** 2,      lambda x: 2 * x),
    (np.exp,                np.exp),
]
def chain_value_and_grad(x0, chain):
    xs = [x0]
    for f, _ in chain: xs.append(f(xs[-1]))           # forward, caching every intermediate
    g = 1.0
    for (_, df), xin in zip(reversed(chain), reversed(xs[:-1])):
        g *= df(xin)                                  # backward: multiply local derivatives
    return xs[-1], g
val, g = chain_value_and_grad(0.3, chain)
f_all = lambda t: np.exp(np.tanh(3 * t + 1) ** 2)
assert np.isclose(g, num(f_all, 0.3), rtol=1e-6)

# logistic regression, one feature: dL/dw = (p - y) x
sigmoid = lambda z: 1 / (1 + np.exp(-z))
def loss(w, b, x, y):
    p = sigmoid(w * x + b); return -(y * np.log(p) + (1 - y) * np.log(1 - p))
w, b, x, y = 0.4, -0.2, 1.7, 1.0
p = sigmoid(w * x + b)
assert np.isclose((p - y) * x, num(lambda t: loss(t, b, x, y), w), rtol=1e-6)
assert np.isclose(p - y,       num(lambda t: loss(w, t, x, y), b), rtol=1e-6)   # dL/db = p - y

# vanishing gradient: depth-n sigmoid chain
def depth_grad(n, x0=0.5):
    s, xv, g = sigmoid, x0, 1.0
    for _ in range(n):
        a = s(xv); g *= a * (1 - a); xv = a
    return g
for n in (1, 5, 10, 20, 40): print(n, depth_grad(n))             # shrinks geometrically; ≤ 0.25**n
assert depth_grad(20) <= 0.25 ** 20
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting the inner derivative: `d/dx (3x+1)² = 2(3x+1)` | Missing factor of 3 | Name each intermediate; verify numerically |
| Evaluating the outer derivative at `x` instead of `g(x)` | Wrong value | Cache and use forward intermediates |
| Recomputing forward values in backward | Slower, error-prone | Store them once |
| Dropping a branch when a variable is used twice | Missing gradient term | Sum over all paths |
| Computing `p(1−p)` for `p` saturated at `0` or `1` | Zero gradient (true or numeric) | Logit-space losses |
| Derivative of the loss w.r.t. the wrong variable | Gradient of different shape/meaning | Label every symbol |
| Treating the loss gradient as `p − y` for a **different** output activation | Wrong formula | Re-derive per loss/activation pair |

### 5.6 ML link

- **Backpropagation:** the chain rule over a computational graph (Module 07 Lesson 4; 4C-07 reverse-mode autodiff).
- **Logistic regression gradient `(p − y)x`** is the first gradient you will use in Module 14.
- **Vanishing/exploding gradients:** products of local derivatives (Stage 4C-07, 5C-03) `[VERIFY]`.
- **Residual connections** add a path so that derivatives sum rather than only multiply (Stage 5C).

### 5.7 Lab (75 min)

1. Implement `chain_value_and_grad` and test it on 10 random chains built from {`tanh`, `sin`, `exp`, polynomial} by comparing with central differences (relative error `< 1e-6`).
2. Derive logistic-regression `dL/dw` and `dL/db` by hand; verify numerically; run 200 steps of 1-D gradient descent on a small dataset and watch the loss.
3. Vanishing-gradient plot: `|dy/dx|` vs depth for sigmoid, tanh, and ReLU chains (random inputs); describe what you see.
4. Draw the computational graph of `L(w) = (σ(wx + b) − y)²` and annotate every local derivative.

### Check yourself (Unit 5)

1. Differentiate `sin(x²)` and `e^{−x²}`.
2. In logistic regression, why does `dL/dz = p − y` look so clean?
3. Why does a deep sigmoid chain produce tiny gradients?

**Reference answers:** (1) `2x cos(x²)`; `−2x e^{−x²}`. (2) The `p(1−p)` from the sigmoid cancels the denominators from the log loss. (3) Each layer multiplies the gradient by `σ′ ≤ 0.25`, so the product shrinks geometrically.

---

## Unit 6 — Derivatives of sigmoid, tanh, and ReLU (`05-…md`)

### 6.1 Why ML needs this

Activation functions decide how gradients flow through a network. Their derivatives determine whether learning is fast, slow, or stuck: saturation (sigmoid, tanh) and dead units (ReLU) are among the most common reasons a model fails to train.

### 6.2 Mechanics

| Activation | Formula | Derivative | Range of `f′` |
|---|---|---|---|
| Sigmoid | `σ(x) = 1/(1 + e⁻ˣ)` | `σ(x)(1 − σ(x))` | `(0, 0.25]`, max at `x = 0` |
| Tanh | `tanh x = (eˣ − e⁻ˣ)/(eˣ + e⁻ˣ)` | `1 − tanh² x` | `(0, 1]`, max at `x = 0` |
| ReLU | `max(0, x)` | `1` if `x > 0`, `0` if `x < 0`, convention at `0` | `{0, 1}` |
| Leaky ReLU | `max(αx, x)`, small `α` | `1` or `α` | `{α, 1}` |
| Softplus | `ln(1 + eˣ)` | `σ(x)` | `(0, 1)` |
| GELU | `x Φ(x)` (Φ the standard normal CDF) | `Φ(x) + x φ(x)` (φ the pdf) | slightly negative to `> 1` near `x ≈ 1` `[VERIFY numerically]` |

- **Derivative derivations:**
  - `σ′`: `σ = (1 + e⁻ˣ)⁻¹` ⇒ `σ′ = e⁻ˣ/(1 + e⁻ˣ)² = σ(1 − σ)`.
  - `tanh′`: quotient rule ⇒ `1 − tanh²`; also `tanh x = 2σ(2x) − 1` ⇒ `tanh′ = 4σ′(2x)`.
- **Saturation:** for large `|x|`, `σ′` and `tanh′` ≈ 0 ⇒ gradients vanish ⇒ learning stalls. Because `σ′ ≤ 0.25`, a chain of sigmoids shrinks gradients at least `4×` per layer.
- **Not zero-centred:** sigmoid outputs are in `(0, 1)`, so downstream pre-activations see all-positive inputs and weight gradients share a sign; tanh is zero-centred `[JUDGEMENT]`.
- **Dying ReLU:** if a unit's pre-activation is negative for all inputs, its gradient is exactly `0` and it never recovers. Causes: large learning rates, bad initialization, large negative bias.
- **ReLU at 0:** conventions differ; frameworks choose `0` `[VERIFY]`. It rarely matters in practice but breaks naive gradient checks at exactly `0` or on integer-valued data.
- **Stable sigmoid:** `1/(1 + exp(−x))` overflows `exp` for large negative `x`; use the piecewise form.

### 6.3 Code

```python
import numpy as np
num = lambda f, x, h=1e-6: (f(x + h) - f(x - h)) / (2 * h)

def sigmoid(x):
    x = np.asarray(x, float)
    e = np.exp(-np.abs(x))                                   # stable for both signs
    return np.where(x >= 0, 1 / (1 + e), e / (1 + e))
def d_sigmoid(x): s = sigmoid(x); return s * (1 - s)
def d_tanh(x):    return 1 - np.tanh(x) ** 2
def relu(x):      return np.maximum(0.0, x)
def d_relu(x):    return (np.asarray(x) > 0).astype(float)   # convention: derivative 0 at x = 0
def leaky(x, a=0.01):   return np.where(x > 0, x, a * x)
def d_leaky(x, a=0.01): return np.where(x > 0, 1.0, a)

xs = np.linspace(-6, 6, 241)
for f, df, name in ((sigmoid, d_sigmoid, "sigmoid"), (np.tanh, d_tanh, "tanh")):
    err = max(abs(num(f, x) - df(x)) for x in xs)
    assert err < 1e-8, (name, err)
assert abs(sigmoid(1000.0) - 1.0) < 1e-12 and sigmoid(-1000.0) >= 0.0          # no overflow warning/NaN
assert np.isclose(d_sigmoid(0.0), 0.25) and np.isclose(d_tanh(0.0), 1.0)
assert np.allclose(np.tanh(xs), 2 * sigmoid(2 * xs) - 1)                       # identity

# ReLU: check away from 0, and look at 0 on purpose
xs_nz = xs[np.abs(xs) > 1e-3]
assert max(abs(num(relu, x) - d_relu(x)) for x in xs_nz) < 1e-6
print("ReLU numeric derivative at 0:", num(relu, 0.0), "| our convention:", d_relu(0.0))   # 0.5 vs 0.0

# saturation: derivative magnitude vs input
for x in (0, 2, 5, 10, 20): print(x, float(d_sigmoid(x)), float(d_tanh(x)))

# depth experiment: gradient magnitude after n layers (scalar toy network, weight 1)
def grad_through_depth(act, dact, n, x0=0.5):
    a, g = x0, 1.0
    for _ in range(n):
        g *= dact(a); a = act(a)
    return abs(g)
for n in (5, 20, 50):
    print(n, grad_through_depth(sigmoid, d_sigmoid, n), grad_through_depth(np.tanh, d_tanh, n), grad_through_depth(relu, d_relu, n))

# dying ReLU: a unit with a large negative bias gets no gradient
rng = np.random.default_rng(0)
x = rng.normal(size=1000); w, b = 1.0, -10.0
alive = (w * x + b > 0).mean()
print("fraction of inputs with nonzero gradient:", alive)            # 0.0 → this unit cannot learn
```

GELU check (uses `math.erf`; no SciPy):

```python
import math
Phi = np.vectorize(lambda t: 0.5 * (1 + math.erf(t / math.sqrt(2))))
phi = lambda t: np.exp(-0.5 * t * t) / math.sqrt(2 * math.pi)
gelu, d_gelu = (lambda t: t * Phi(t)), (lambda t: Phi(t) + t * phi(t))
assert max(abs(num(gelu, x) - d_gelu(x)) for x in xs) < 1e-6
```

### 6.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `1/(1+np.exp(-x))` for very negative `x` | Overflow warning, `inf` intermediate | Use the stable piecewise form |
| Sigmoid/tanh in very deep stacks | Gradients ~0, loss stalls | ReLU-family, normalization, residuals, good init |
| Dead ReLUs | Many units output 0 for every input | Smaller LR, leaky ReLU, better init; monitor the active fraction |
| Gradient-checking ReLU at `x = 0` | Mismatch (0.5 vs 0) | Avoid exact zeros; use random continuous inputs |
| Using `d_sigmoid(σ)` instead of `d_sigmoid(x)` | Wrong gradient | `σ′` in terms of the **output** is `s(1−s)`; in terms of input call `σ` first |
| Assuming tanh gradients never vanish | They do when saturated | Monitor activations |
| Applying an activation derivative to already-activated values twice | Squared factors | Cache pre-activations `z` and activations `a` separately |

### 6.5 ML link

- **Vanishing gradients** historically limited deep sigmoid/tanh networks; ReLU-family activations and residual connections mitigate it (Stage 5C-03).
- **Dying ReLU and leaky variants:** monitor the fraction of active units in training `[JUDGEMENT]`.
- **Sigmoid output + log loss** gives the clean `p − y` gradient (Lesson 4, Module 14).
- **GELU / SiLU** in transformers: smooth gates (Stage 5C-07, 4C-07).
- **Gates in LSTM/GRU** use sigmoid/tanh (4C-08).

### 6.6 Lab (75 min)

1. Implement stable sigmoid and the full activation-derivative set; verify each numerically.
2. Plot each activation and derivative on `[−6, 6]`; annotate maxima and saturation regions.
3. Depth experiment above; log-scale plot of gradient magnitude vs depth for the three activations.
4. Dying-ReLU experiment: train a tiny 1-D regression with a ReLU unit and a large learning rate; record the active fraction per step; reproduce a dead unit and then fix it with leaky ReLU.
5. Add `check_activation(f, df, xs)` helper to the project library with a configurable tolerance and a skip-zero option.

### Check yourself (Unit 6)

1. What is the maximum of `σ′` and where?
2. Why can a ReLU unit "die"?
3. Express `tanh′` in terms of `tanh`.

**Reference answers:** (1) `0.25` at `x = 0`. (2) If its pre-activation is negative for all inputs its gradient is exactly zero, so its weights never update. (3) `1 − tanh²`.

---

## Unit 7 — Second derivatives and curvature (`06-…md`)

### 7.1 Why ML needs this

The first derivative says which way is downhill; the **second derivative says how fast the slope changes**: the curvature. Curvature sets how large a gradient-descent step can safely be, explains why ill-conditioned problems are slow, and is the one-dimensional version of the Hessian (4C-02) used by second-order optimizers.

### 7.2 Intuition

- `f″ > 0`: the curve bends **up** (a bowl, convex). Slope increases left to right.
- `f″ < 0`: bends **down** (a cap, concave).
- `|f″|` large: a sharply curved, steep-walled valley; `|f″|` small: a flat basin.
- **Inflection point:** `f″` changes sign (not necessarily a minimum or maximum).

### 7.3 Mechanics

- `f″(x) = d/dx f′(x)`.
- **Second-order Taylor expansion:** `f(x + h) ≈ f(x) + f′(x)h + ½ f″(x)h²`. It is the quadratic model used by Newton's method.
- **Finite difference:** `f″(x) ≈ [f(x+h) − 2f(x) + f(x−h)]/h²`; error `O(h²)`; round-off grows like `ε/h²`, so the best `h` is larger than for first derivatives, about `ε^{1/4} ≈ 1.2e-4` `[JUDGEMENT]`.
- **Quadratic model of a loss:** `f(x) = ½ a x²` has `f′ = a x`, `f″ = a`.
- **Gradient descent on a 1-D quadratic:** `x ← x − η a x = (1 − ηa) x`. Converges iff `|1 − ηa| < 1`, i.e. **`0 < η < 2/a`**; fastest at `η = 1/a` (one step); oscillates when `η > 1/a`; diverges when `η > 2/a`.
- **Newton's method in 1-D:** `x ← x − f′(x)/f″(x)` (jumps to the quadratic's minimum; exact in one step on a quadratic). Needs `f″ ≠ 0`; heads to a **maximum** if `f″ < 0`.
- **Curvature and sharpness:** a high `f″` at the solution means a sharp minimum; the maximum stable learning rate shrinks proportionally. In many dimensions the largest Hessian eigenvalue plays the role of `a` (Module 03 Lesson 2; 4C-03).
- **Condition number preview:** in `n` dimensions the ratio of the largest to smallest curvature controls convergence speed (Module 08, 4C-03).

### 7.4 Code

```python
import numpy as np

def second_diff(f, x, h=1e-4): return (f(x + h) - 2 * f(x) + f(x - h)) / h ** 2

f = lambda x: x ** 4 - 3 * x ** 2 + x
d2 = lambda x: 12 * x ** 2 - 6
for x in (-1.5, 0.0, 0.5, 1.3):
    assert np.isclose(second_diff(f, x), d2(x), rtol=1e-4, atol=1e-4)

# GD on f(x) = a/2 x^2 : step-size regimes
def gd_quadratic(a, eta, x0=1.0, steps=20):
    x = x0; traj = [x]
    for _ in range(steps):
        x = x - eta * a * x; traj.append(x)
    return np.array(traj)
a = 4.0
for eta, label in ((0.1, "slow"), (1 / a, "optimal (1/a)"), (0.4, "oscillating, converging"), (2 / a, "boundary"), (0.6, "diverging")):
    t = gd_quadratic(a, eta)
    print(f"eta={eta:<5} {label:26s} |x_20| = {abs(t[-1]):.3g}")
assert abs(gd_quadratic(a, 1 / a, steps=1)[-1]) < 1e-12           # one-step convergence at eta = 1/a
assert abs(gd_quadratic(a, 0.6)[-1]) > abs(gd_quadratic(a, 0.6)[0])  # 0.6 > 2/a = 0.5 → diverges

# Newton in 1-D on a non-quadratic, with a guard for the wrong curvature sign
def newton_1d(f1, f2, x0, steps=50, tol=1e-12):
    x = x0
    for _ in range(steps):
        h = f2(x)
        if abs(h) < 1e-12: raise RuntimeError("zero curvature: Newton step undefined")
        step = f1(x) / h
        x -= step
        if abs(step) < tol: break
    return x
f1 = lambda x: 4 * x ** 3 - 6 * x + 1
x_star = newton_1d(f1, d2, 1.5)
print("Newton →", x_star, " f''=", d2(x_star), "(>0 minimum)")
x_bad = newton_1d(f1, d2, 0.1)                                     # may converge to a max or another critical point
print("Newton from 0.1 →", x_bad, " f''=", d2(x_bad))

# quadratic Taylor model quality
x0, h = 0.5, 0.1
exact = f(x0 + h); lin = f(x0) + (4*x0**3 - 6*x0 + 1) * h; quad = lin + 0.5 * d2(x0) * h ** 2
print(abs(exact - lin), abs(exact - quad))                          # quadratic is much closer
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Learning rate above `2/a` | Divergence (loss grows geometrically) | Estimate curvature; use `η ≲ 1/a` |
| Newton with `f″ ≤ 0` | Moves to a maximum/saddle | Check the sign; fall back to gradient steps or damping |
| `h` too small in `f″` finite differences | Round-off noise `~ε/h²` | `h ≈ 1e-4`, validate by varying `h` |
| Confusing "convex" and "positive derivative" | Wrong conclusions | Convex ⇔ `f″ ≥ 0` (for twice-differentiable `f`) |
| Treating `f″ = 0` as proof of an inflection | `x⁴` has `f″(0) = 0` but is a minimum | Use higher-order or sign-change tests |
| Using a single global learning rate when curvature varies widely | Slow in flat directions, unstable in steep ones | Preconditioning / adaptive optimizers (Module 08) |
| Quoting `2/a` for non-quadratic losses as exact | It is local | Treat as a local guide |

### 7.6 ML link

- **Learning-rate limit:** `η < 2/λ_max(Hessian)` generalizes the 1-D result (Module 08, 4C-03).
- **Conditioning:** big curvature spread ⇒ slow convergence; explains why feature scaling helps (Module 14).
- **Newton / quasi-Newton / second-order methods** (4C-03).
- **Sharp vs flat minima** discussions in generalization (Stage 5C-03) `[JUDGEMENT; contested topic]`.
- **Convexity of losses:** MSE and logistic loss are convex in the weights (Module 14).

### 7.7 Lab (75 min)

1. Implement `second_diff` and verify on 5 functions with known `f″`; scan `h` and plot the V-shaped error.
2. Reproduce all learning-rate regimes for `a ∈ {1, 4, 25}`; plot trajectories and the contraction factor `|1 − ηa|` vs `η`.
3. Newton vs gradient descent on `f(x) = x⁴ − 3x² + x` from five starting points; tabulate where each ends (min, max, or non-convergent) and `f″` at the end.
4. Show the linear vs quadratic Taylor model error as `h` shrinks (log-log, slopes 2 and 3).
5. Build a 2-feature linear regression where one feature is scaled `100×`; measure the maximum stable learning rate before and after standardization (preview of Module 08 and Module 14; use the Hessian `XᵀX/n`).

### Check yourself (Unit 7)

1. For `f(x) = 5x²`, what are the maximum stable and optimal gradient-descent step sizes?
2. What sign of `f″` do you need at a local minimum?
3. What does Newton's method do on an exact quadratic?

**Reference answers:** (1) `f″ = 10`: stable for `η < 0.2`, optimal `η = 0.1`. (2) `f″ ≥ 0` (strictly positive guarantees a strict minimum; zero is inconclusive). (3) Converges in a single step.

---

## Unit 8 — Finding minima and maxima (`07-…md`)

### 8.1 Why ML needs this

Training is minimization. Understanding critical points, local versus global minima, saddles, flat regions, and non-differentiable minima in one dimension prepares you for what optimizers face in millions of dimensions.

### 8.2 Mechanics

- **Critical point:** `f′(x) = 0` (or `f′` undefined). Every interior extremum of a differentiable function is a critical point; the converse is false.
- **Second-derivative test:** at a critical point, `f″ > 0` ⇒ local minimum; `f″ < 0` ⇒ local maximum; `f″ = 0` ⇒ inconclusive (`x⁴`: minimum; `−x⁴`: maximum; `x³`: neither, an inflection).
- **First-derivative (sign-change) test:** `f′` goes `− → +` ⇒ minimum; `+ → −` ⇒ maximum; no change ⇒ neither.
- **Global vs local:** compare all candidates and the **boundary** of the domain. A function can be unbounded below.
- **Convex functions:** any local minimum is global (`f″ ≥ 0` everywhere). Squared error and logistic loss in the weights are convex; neural-network losses are not (Module 08, 4C-03).
- **Non-differentiable minima:** `|x|` has its minimum at `0` where `f′` does not exist: L1-regularized problems put minima at corners (sparsity).
- **Solving for the minimum:**
  1. Analytic: solve `f′ = 0`.
  2. **Gradient descent:** `x ← x − η f′(x)`.
  3. **Newton:** Lesson 7.
  4. **Bracketing without derivatives:** golden-section search for unimodal `f` on `[a, b]`.
  5. **Root finding on `f′`:** bisection (needs a sign change).
- **Initialization matters** for non-convex `f`: different starts reach different local minima.
- **Plateaus and saddles:** `f′ ≈ 0` for a long stretch slows optimizers; a saddle in 1-D is an inflection with `f′ = 0`.
- **Constrained 1-D problems:** minimum on `[a, b]` may be at an endpoint, with a nonzero derivative there.

### 8.3 Code

```python
import numpy as np

f  = lambda x: x ** 4 - 3 * x ** 2 + x
f1 = lambda x: 4 * x ** 3 - 6 * x + 1
f2 = lambda x: 12 * x ** 2 - 6

# 1) critical points from f' = 0 (roots of a cubic) + second-derivative test
roots = np.sort(np.roots([4, 0, -6, 1]).real)
for r in roots:
    kind = "min" if f2(r) > 0 else ("max" if f2(r) < 0 else "inconclusive")
    print(f"x={r:+.4f}  f={f(r):+.4f}  f''={f2(r):+.3f}  → {kind}")
best = min(roots, key=f); print("global minimum among critical points:", best)

# 2) bisection on f' (needs a sign change)
def bisect(g, lo, hi, tol=1e-12):
    glo, ghi = g(lo), g(hi)
    if glo * ghi > 0: raise ValueError("no sign change on the interval")
    while hi - lo > tol:
        mid = (lo + hi) / 2; gm = g(mid)
        if glo * gm <= 0: hi, ghi = mid, gm
        else: lo, glo = mid, gm
    return (lo + hi) / 2
assert abs(bisect(f1, 1.0, 2.0) - roots[-1]) < 1e-9

# 3) golden-section search (derivative-free) on a unimodal interval
def golden(fun, lo, hi, tol=1e-9):
    phi = (np.sqrt(5) - 1) / 2
    c, d = hi - phi * (hi - lo), lo + phi * (hi - lo)
    fc, fd = fun(c), fun(d)
    while hi - lo > tol:
        if fc < fd: hi, d, fd = d, c, fc; c = hi - phi * (hi - lo); fc = fun(c)
        else:       lo, c, fc = c, d, fd; d = lo + phi * (hi - lo); fd = fun(d)
    return (lo + hi) / 2
assert abs(golden(f, 0.5, 2.0) - roots[-1]) < 1e-6

# 4) gradient descent: different starts land in different minima
def gd(x0, eta=0.01, steps=5000):
    x = x0
    for _ in range(steps): x -= eta * f1(x)
    return x
for x0 in (-2.0, -0.5, 0.2, 0.5, 2.0):
    xe = gd(x0); print(f"start {x0:+.1f} → {xe:+.4f}  f={f(xe):+.4f}")

# 5) inflection / saddle in 1-D: f = x^3 has f'(0) = 0 but no extremum; x^4 has f''(0)=0 but a min
for g_, name in ((lambda x: x ** 3, "x^3"), (lambda x: x ** 4, "x^4"), (lambda x: -x ** 4, "-x^4")):
    print(name, [round(float(g_(x)), 8) for x in (-0.1, 0.0, 0.1)])

# 6) non-differentiable minimum: |x| + 0.5 (x-1)^2 → soft-thresholding solution
def lasso_1d(z, lam): return np.sign(z) * np.maximum(abs(z) - lam, 0.0)       # argmin 0.5(x-z)^2 + lam|x|
for z, lam in ((2.0, 0.5), (0.3, 0.5), (-1.2, 0.5)):
    xs = np.linspace(-3, 3, 600001); xm = xs[np.argmin(0.5 * (xs - z) ** 2 + lam * np.abs(xs))]
    assert abs(xm - lasso_1d(z, lam)) < 1e-5
```

### 8.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Declaring every `f′ = 0` a minimum | Maximum/saddle chosen | Second-derivative or sign-change test |
| Ignoring domain boundaries | Missed global optimum | Evaluate endpoints |
| Trusting a single gradient-descent run on a non-convex function | Stuck in a poor local minimum | Multiple starts; compare final loss |
| Using golden-section on a non-unimodal interval | Wrong local min | Bracket first; plot |
| Bisection without a sign change | Error or wrong answer | Verify `g(lo)·g(hi) < 0` |
| `f″(x*) = 0` interpreted as "not a minimum" | `x⁴` counterexample | Inspect higher-order or the sign of `f′` |
| Applying `f′ = 0` where `f′` does not exist | Miss the corner minimum (`|x|`) | Check the points where `f` is not differentiable |
| Step size too large (cf. Lesson 7) | Bouncing between basins | Reduce `η` |

### 8.5 ML link

- **MSE with one weight** has a closed-form minimum (Lesson 2) and is the 1-D case of the normal equation (Module 14).
- **Logistic loss** is convex: one global minimum (unless the data is separable: the minimum is at infinity, and weights grow without bound; regularize) `[VERIFY: Module 14 coverage]`.
- **Non-convex neural-network losses:** many local minima and saddles; empirically, optimizers reach good solutions anyway `[JUDGEMENT; theory incomplete]` (4C-03).
- **L1 / soft-thresholding:** the corner minimum becomes exact sparsity (Module 14).
- **Early stopping, restarts, and learning-rate schedules** as practical remedies (Module 08, 4C-03).

### 8.6 Lab (75 min)

1. For three functions (a polynomial, `x e^{−x²}`, and `|x| + 0.1x²`), find all minima/maxima by (a) analysis, (b) root finding on `f′`, (c) a grid search, (d) gradient descent from 10 random starts; compare.
2. Plot `f` with markers for each method's answer; show which starts lead to which minimum (basins of attraction on the `x`-axis).
3. Implement golden-section search and compare function evaluations needed against bisection on `f′` (count evaluations; report your numbers).
4. Verify soft-thresholding as the exact minimizer of `0.5(x − z)² + λ|x|` by brute force.
5. Logistic-loss in 1-D with *separable* data: show the loss decreases forever as `w → ∞`, and add an L2 penalty to create a finite minimum.

### Check yourself (Unit 8)

1. Does `f′(x) = 0` imply a minimum?
2. Classify the critical point of `f(x) = x³` at `0`.
3. Where is the minimum of `0.5(x − z)² + λ|x|` for `|z| ≤ λ`?

**Reference answers:** (1) No: it can be a maximum or an inflection/saddle. (2) Neither: an inflection (`f′ = f″ = 0`, no sign change in `f′`). (3) At `x = 0`.

---

## Unit 9 — Numerical vs analytical derivatives and gradient checking (`08-…md`)

### 9.1 Why ML needs this

Every hand-written backward pass has a bug the first time. Comparing your analytical gradient with a numerical one is the standard test, and it is how you trust a custom layer or loss. The same ideas (finite differences, complex-step, dual numbers) are the intellectual ladder to automatic differentiation.

### 9.2 Mechanics

| Method | How | Accuracy | Cost | Caveats |
|---|---|---|---|---|
| Analytical | Derive by hand | Exact | 1 eval | Easy to get wrong |
| Symbolic (SymPy) | CAS differentiation | Exact | Expression swell for big graphs | Not for programs with control flow |
| Forward difference | `(f(x+h) − f(x))/h` | `O(h)` + round-off | 1 extra eval per input | Poor accuracy |
| Central difference | `(f(x+h) − f(x−h))/2h` | `O(h²)` + round-off | 2 evals per input | Standard for checks |
| **Complex-step** | `Im f(x + ih)/h` | Machine precision, `h` can be `1e-30` | 1 complex eval per input | Needs analytic `f` and complex-safe ops (no `abs`, `max`, comparisons) |
| **Forward-mode autodiff (dual numbers)** | Carry `(value, derivative)` | Exact up to float | 1 pass per input direction | Cost scales with number of inputs |
| **Reverse-mode autodiff** | Backprop on the graph | Exact up to float | 1 backward pass for all inputs | Memory for intermediates (Module 07, 4C-07) |

- **Gradient check for `f: ℝⁿ → ℝ`:** compute `g_num[i] = (f(x + hᵢeᵢ) − f(x − hᵢeᵢ))/(2hᵢ)` for each coordinate (cost `2n` evaluations, so only for debugging).
- **Relative error:** `‖g_a − g_n‖ / max(‖g_a‖ + ‖g_n‖, ε)`, or per coordinate `|a − n| / max(|a| + |n|, ε)`. Plain absolute error is misleading when gradients are tiny or huge.
- **Practical thresholds** `[JUDGEMENT]` for `float64`: `< 1e-7` excellent; `1e-7…1e-5` acceptable for smooth functions; `> 1e-3` almost certainly a bug. With `float32` expect `~1e-3…1e-2` at best.
- **Dual numbers:** `(a + bε)` with `ε² = 0`; arithmetic rules reproduce the product and chain rules automatically. Implementing a tiny `Dual` class is the best way to see autodiff as "the rules, mechanised".
- **What to avoid when checking:** non-smooth points (ReLU/`abs` at 0, max-pool ties), random layers (dropout) unless fixed, non-determinism, `float32`, loss values near saturation (tiny gradients), checking only a few coordinates when the bug is in one slice.
- **Testing strategy:** check **each layer/loss separately**, then the composition; check at random points; fix seeds; also check *the scale* of the gradient (a bug that is a constant factor shows as relative error ≈ `|1 − c|`).

### 9.3 Code

```python
import numpy as np

def numerical_grad(f, x, h=1e-5):
    x = np.asarray(x, float); g = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x); e.flat[i] = h * max(1.0, abs(x.flat[i]))     # scale h per coordinate
        g.flat[i] = (f(x + e) - f(x - e)) / (2 * e.flat[i])
    return g

def rel_error(a, n, eps=1e-12):
    a, n = np.asarray(a, float), np.asarray(n, float)
    return float(np.linalg.norm(a - n) / max(np.linalg.norm(a) + np.linalg.norm(n), eps))

def gradcheck(f, grad, x, tol=1e-6, h=1e-5):
    a, n = grad(x), numerical_grad(f, x, h)
    err = rel_error(a, n)
    if err > tol:
        worst = int(np.argmax(np.abs(a - n)))
        raise AssertionError(f"gradcheck failed: rel_err={err:.2e} (> {tol:.0e}); worst index {worst}: analytic={a.flat[worst]:.6g}, numeric={n.flat[worst]:.6g}")
    return err

# a composed function of a vector: f(x) = softplus(tanh(3 x0) - x1^2) + 0.5 * x0 * x1
sp = lambda t: np.logaddexp(0.0, t)
sig = lambda t: 1 / (1 + np.exp(-t))
def f(x): return sp(np.tanh(3 * x[0]) - x[1] ** 2) + 0.5 * x[0] * x[1]
def grad(x):
    u = np.tanh(3 * x[0]) - x[1] ** 2
    du0, du1 = 3 * (1 - np.tanh(3 * x[0]) ** 2), -2 * x[1]
    s = sig(u)                                                   # d softplus / du
    return np.array([s * du0 + 0.5 * x[1], s * du1 + 0.5 * x[0]])
rng = np.random.default_rng(0)
for _ in range(20): print(f"{gradcheck(f, grad, rng.normal(size=2)):.1e}", end=" ")

# catch an injected bug (missing factor of 3 in the chain rule)
def grad_bug(x):
    g = grad(x).copy()
    u = np.tanh(3 * x[0]) - x[1] ** 2
    g[0] = sig(u) * (1 - np.tanh(3 * x[0]) ** 2) + 0.5 * x[1]       # forgot the inner 3
    return g
try:
    gradcheck(f, grad_bug, np.array([0.3, -0.4]))
except AssertionError as e:
    print("\ncaught:", e)

# complex-step derivative: accurate to machine precision with a tiny h
def complex_step(f, x, h=1e-30): return np.imag(f(x + 1j * h)) / h
g = lambda x: np.exp(x) / np.sqrt(np.sin(x) ** 3 + np.cos(x) ** 3)
x0 = 1.5
d_cs = complex_step(g, x0); d_cd = (g(x0 + 1e-5) - g(x0 - 1e-5)) / 2e-5
import sympy as sp_; X = sp_.symbols("X"); d_exact = float(sp_.diff(sp_.exp(X) / sp_.sqrt(sp_.sin(X)**3 + sp_.cos(X)**3), X).subs(X, x0))
print(abs(d_cs - d_exact), abs(d_cd - d_exact))                     # complex-step error ~1e-16, central ~1e-10

# forward-mode autodiff with dual numbers
class Dual:
    def __init__(self, v, d=0.0): self.v, self.d = v, d
    def _w(self, o): return o if isinstance(o, Dual) else Dual(o, 0.0)
    def __add__(s, o): o = s._w(o); return Dual(s.v + o.v, s.d + o.d)
    __radd__ = __add__
    def __sub__(s, o): o = s._w(o); return Dual(s.v - o.v, s.d - o.d)
    def __rsub__(s, o): return Dual(o, 0.0) - s
    def __mul__(s, o): o = s._w(o); return Dual(s.v * o.v, s.d * o.v + s.v * o.d)
    __rmul__ = __mul__
    def __truediv__(s, o): o = s._w(o); return Dual(s.v / o.v, (s.d * o.v - s.v * o.d) / o.v ** 2)
    def __pow__(s, n): return Dual(s.v ** n, n * s.v ** (n - 1) * s.d)
def d_exp(a): e = np.exp(a.v); return Dual(e, e * a.d)
def d_sin(a): return Dual(np.sin(a.v), np.cos(a.v) * a.d)
def d_tanh(a): t = np.tanh(a.v); return Dual(t, (1 - t * t) * a.d)

h_ = lambda x: d_tanh(3 * x) * d_sin(x * x) + x ** 3
out = h_(Dual(0.7, 1.0))
num = (lambda t: np.tanh(3 * t) * np.sin(t * t) + t ** 3)
assert np.isclose(out.d, (num(0.7 + 1e-6) - num(0.7 - 1e-6)) / 2e-6, rtol=1e-6)
```

### 9.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Using absolute error to judge a gradient | Tiny gradients "pass" wrongly, huge ones "fail" | Use relative error with an epsilon floor |
| `h` too small or too large | Noisy or biased numeric gradient | `h ≈ 1e-5` central, scaled by `max(1, |x|)`; test two values of `h` |
| Gradient-checking at a kink (ReLU at 0) | False failures | Random continuous inputs; skip/perturb exact zeros |
| Checking in `float32` | Apparent bugs from precision | Use `float64` for the check |
| Random layers (dropout) active during the check | Different forward passes for `x±h` | Disable or fix the mask/seed |
| Checking only the total gradient norm | A bug in one coordinate is hidden | Report per-coordinate worst index |
| Complex-step on non-analytic ops (`abs`, `max`, comparisons) | Wrong or error | Use central differences there |
| Forgetting the loss reduction (`mean` vs `sum`) | Constant-factor mismatch | State the reduction; the relative error ≈ `|1 − c|` reveals it |
| Passing the check once at one point | Coincidental pass | Check at 10–20 random points and corner cases |
| Treating a passing check as proof of correctness | Bug in the **forward** pass is invisible | The check only compares `f` with its own gradient; also test `f` itself against known values |

### 9.5 ML link

- **Custom layers and losses:** gradient-check before trusting them (Module 07 Project 2; Stage 5C-01 and 5C-02).
- **Autodiff:** dual numbers are forward mode; reverse mode is what frameworks use for scalar losses with many parameters (4C-07).
- **Debugging NaN losses:** the first step is to check each component's gradient (Stage 5C-03).
- **Testing culture:** gradient tests belong in the repo's CI (Stage 5D-02) `[JUDGEMENT]`.

### 9.6 Lab (90 min)

1. Implement `numerical_grad`, `rel_error`, `gradcheck`; run on 6 functions (polynomial, `sigmoid`, `tanh`, `softplus`, composed, vector-valued reduction) at 20 random points each.
2. **Mutation testing:** inject 5 different bugs into `grad` (missing factor, sign flip, wrong index, swapped arguments, off-by-one in a sum) and verify the checker catches all with error `> 1e-3`.
3. Compare central, forward, complex-step, and dual-number derivatives on 3 functions; table of absolute errors against SymPy's exact derivative (your numbers).
4. Gradient-check logistic regression's loss (with the `(p − y)x` gradient) in vector form for `d = 5`, and a loss with a ReLU unit (observe the kink issue; fix it).
5. Extend `Dual` with `log`, `sigmoid`, and division; differentiate a small expression graph and check it with `gradcheck`.

### Check yourself (Unit 9)

1. Why prefer relative error over absolute error?
2. What is the cost of a numerical gradient for `n` parameters, and why is it only for debugging?
3. What does the complex-step method need from `f`?

**Reference answers:** (1) It is scale-free: absolute error cannot distinguish a tiny gradient with a 100% error from a large one with a small error. (2) `2n` function evaluations (each a full forward pass); too slow for training, fine for tests. (3) That `f` is analytic and implemented with complex-safe operations (no `abs`, `max`, or comparisons).

---

## Unit 10 — Practice question bank (`practice-questions.md`)

### 10.1 Structure

About 55 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 14 per tier, each with a hidden answer and a one-line rationale. Mix hand derivations, "predict the number", runnable code, and ML judgement.

### 10.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 10.3 Seed items

**Q1 [L1] Definition.** State the limit definition of `f′(x)`. → `lim_{h→0}(f(x+h) − f(x))/h`.
**Q2 [L2] Rules.** Differentiate `x³ ln x`. → `3x² ln x + x²`.
**Q3 [L2] Chain rule.** Differentiate `e^{sin x}`. → `cos x · e^{sin x}`.
**Q4 [L2] Sigmoid.** Compute `σ′(0)`. → `0.25`.
**Q5 [L2] Tanh.** Compute `tanh′(0)`. → `1`.
**Q6 [L2] ReLU.** What is `d/dx max(0, 2x − 3)` at `x = 1`? At `x = 2`? → `0` at `x = 1`; `2` at `x = 2`.
**Q7 [L2] Curvature.** `f(x) = 3x² − 12x + 5`: minimum and `f″`? → `x = 2`, `f″ = 6 > 0`.
**Q8 [L2] Learning rate.** For `f(x) = 8x²`, what `η` converges fastest in one step, and what is the stability limit? → `f″ = 16`: `η = 1/16`; limit `η < 1/8`.
**Q9 [L2] MSE.** Minimize `Σ(w xᵢ − yᵢ)²` for `x = (1, 2, 3)`, `y = (2, 4, 7)`. → `w* = Σxy/Σx² = 31/14 ≈ 2.214`.
**Q10 [L3] Debug.** Forward-difference derivative of `sin` at 1 gives errors of order `1e-8` with `h = 1e-8` but `1e-1` with `h = 1e-16`. Explain. → Round-off dominates at tiny `h`; optimal `h ≈ √ε ≈ 1e-8` for forward differences.
**Q11 [L3] Debug.** A gradient check reports relative error `0.33`. What bug class does a constant-factor discrepancy suggest? → A missing/extra constant (e.g., forgot `1/n`, the factor 2, or an inner derivative like the `3` in `tanh(3x)`).
**Q12 [L3] Debug.** Gradient check fails only for inputs exactly equal to 0. → ReLU/`abs` kink; use random continuous inputs or skip exact zeros.
**Q13 [L3] Analysis.** Training a 30-layer sigmoid network, early-layer gradients are `~1e-20`. Why? → Each layer multiplies by `σ′ ≤ 0.25`: `0.25³⁰ ≈ 8.7e-19` at best.
**Q14 [L3] Analysis.** 40% of ReLU units output zero for all inputs. What happened and what to try? → Dead units (large negative pre-activations); lower the learning rate, check init/bias, try leaky ReLU, and monitor the active fraction.
**Q15 [L3] Analysis.** Newton's method from `x₀ = 0.1` on `x⁴ − 3x² + x` lands at a maximum. Why? → Newton seeks `f′ = 0` regardless of curvature sign; near `x₀` the curvature is negative.
**Q16 [L4] Design.** You must verify a custom loss's gradient in CI. → A `gradcheck` test over random points in `float64`, per-coordinate reporting, fixed seed, tolerance `1e-6`, mutation tests for the checker, and a forward-value test against known cases.
**Q17 [L4] Design.** Choose a learning rate for `f(x) ≈ ½ a x²` when `a` is unknown. → Estimate curvature (second finite difference or line search), set `η ≲ 1/a` (never above `2/a`); consider adaptive methods.
**Q18 [L4] Design.** An L1-regularized 1-D fit returns exactly 0 for small `z`. Explain. → Soft-thresholding: the corner of `|x|` makes `x = 0` the minimizer when `|z| ≤ λ`.

### 10.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Limit definition, finite differences | 2 | 2 | 3 | 1 |
| Rules | 2 | 3 | 1 | 1 |
| Exp/log/trig | 2 | 3 | 2 | 1 |
| Chain rule | 1 | 3 | 2 | 2 |
| Sigmoid/tanh/ReLU | 2 | 3 | 3 | 1 |
| Second derivatives | 1 | 2 | 1 | 2 |
| Minima/maxima | 2 | 2 | 1 | 2 |
| Numerical vs analytical, gradcheck | 2 | 2 | 3 | 2 |

### Check yourself (Unit 10)

1. Why does the seed set include a constant-factor gradient-check bug?
2. Which items need runnable code?

**Reference answers:** (1) Constant-factor errors are the most common backward-pass bug (missing `1/n`, a factor of 2, an inner derivative) and have a recognisable signature. (2) All L3 debug items and any answer that depends on floating-point behaviour.

---

## Unit 11 — Project index (`Projects/README.md`)

### 11.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Symbolic and numerical derivative comparison | Correct derivative catalogue; error-vs-`h` analysis; honest method comparison | 1–5, 8 | 5–6 h |
| 2 | Numerical gradient checker | Production-quality checker, mutation-tested, applied to a tiny network | 4–6, 8 | 6–7 h |

Order: 1 → 2 (Project 2 reuses the derivative catalogue and error utilities). Outputs feed `mlmath/calculus.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D6) and notebook `05_derivatives.ipynb`; Project 2's checker is reused in Module 07 and beyond.

### 11.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs reference (SymPy, known values) | 30 |
| Failure-mode handling (kinks, domain edges, `float32`, NaN) | 15 |
| Reproducibility (seeded, pinned, clean venv) | 15 |
| Explanation quality (what each plot/table shows and why it matters for ML) | 15 |
| Code quality (types, docstrings, shape notes) | 15 |
| ML connection paragraph | 10 |

### 11.3 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 11)

1. What does Project 2 reuse from Project 1?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The derivative catalogue, error metrics, and plotting utilities. (2) D6 (`mlmath/calculus.py`).

---

## Unit 12 — Project: Symbolic and numerical derivative comparison (`Projects/01-…md`)

### 12.1 Brief

Build `derivcmp`: a catalogue of functions, each with a hand-derived derivative, a SymPy symbolic derivative, and several numerical methods (forward, central, complex-step, dual-number), then a systematic comparison of accuracy, cost, and failure behaviour.

**Industry framing:** teams choose a differentiation strategy by measured accuracy, cost, and failure modes, not by habit, and they keep a regression suite of known derivatives.

### 12.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Function catalogue | ≥ 15 entries: polynomials, `exp`, `log`, `sin/cos/tan`, sigmoid, tanh, softplus, ReLU (with convention), `|x|`, GELU, a composed function, a rational function, `x^x`, `sqrt` near 0; each with domain, hand derivative, and notes |
| R2 | Symbolic layer | SymPy `diff` → `lambdify("numpy")`; `simplify` compared with the hand derivative via sampling (not string equality) |
| R3 | Numeric methods | Forward, backward, central, complex-step (where valid), `Dual` forward-mode |
| R4 | Error studies | For each function and method: error vs `h` on a log grid (V-curve), best `h`, minimum error, convergence order fitted by log-log slope |
| R5 | Domain/kink handling | Catalogue records points to avoid; harness tests them deliberately (e.g., `|x|` at 0, `log` near 0, `tan` near `π/2`) and records what each method returns |
| R6 | Cost model | Count function evaluations per derivative for each method; measure wall time per call on your machine (report with versions, no assumed ratios) |
| R7 | Second derivatives | Central second difference vs SymPy; optimal `h` study |
| R8 | Precision study | Repeat key comparisons in `float32` vs `float64`; summarize loss of accuracy |
| R9 | Report | `REPORT.md`: tables and figures with the **recommended method per situation** and evidence for each claim |
| R10 | Regression tests | pytest parametrized over the catalogue; tolerances justified per method |

### 12.3 Layout and starter

```
derivcmp/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/derivcmp/{__init__,catalogue,symbolic,numeric,dual,studies,report}.py
├── tests/{test_catalogue,test_numeric,test_dual,test_studies}.py
├── notebooks/05_derivative_comparison.ipynb
└── results/
```

```python
# src/derivcmp/catalogue.py
from dataclasses import dataclass
from typing import Callable
import numpy as np
import sympy as sp

x = sp.symbols("x", real=True)

@dataclass(frozen=True)
class Entry:
    name: str
    expr: sp.Expr                    # symbolic definition
    hand: Callable                   # hand-derived derivative (NumPy)
    points: tuple                    # safe evaluation points
    avoid: tuple = ()                # kinks / domain edges (tested separately)
    complex_ok: bool = True          # False if the NumPy form uses abs/max/comparisons

    @property
    def f(self):  return sp.lambdify(x, self.expr, "numpy")
    @property
    def df(self): return sp.lambdify(x, sp.diff(self.expr, x), "numpy")

CATALOGUE = [
    Entry("poly",     x**3 - 2*x + 1,                lambda t: 3*t**2 - 2,                      (-1.3, 0.2, 2.1)),
    Entry("exp",      sp.exp(x),                      np.exp,                                    (-2.0, 0.0, 1.5)),
    Entry("log",      sp.log(x),                      lambda t: 1/t,                             (0.3, 1.0, 4.0), avoid=(0.0,)),
    Entry("sin",      sp.sin(x),                      np.cos,                                    (-1.0, 0.5, 3.0)),
    Entry("tan",      sp.tan(x),                      lambda t: 1/np.cos(t)**2,                  (-1.0, 0.4, 1.2), avoid=(np.pi/2,)),
    Entry("sigmoid",  1/(1 + sp.exp(-x)),             lambda t: (1/(1+np.exp(-t)))*(1-1/(1+np.exp(-t))), (-4.0, 0.0, 3.0)),
    Entry("tanh",     sp.tanh(x),                     lambda t: 1 - np.tanh(t)**2,               (-2.0, 0.3, 1.7)),
    Entry("softplus", sp.log(1 + sp.exp(x)),          lambda t: 1/(1 + np.exp(-t)),              (-3.0, 0.0, 2.0)),
    Entry("composed", sp.log(1 + sp.exp(sp.tanh(3*x) - x**2)),
                      lambda t: (1/(1+np.exp(-(np.tanh(3*t)-t**2)))) * (3*(1-np.tanh(3*t)**2) - 2*t), (-0.8, 0.1, 0.9)),
    Entry("rational", 1/(1 + x**2),                   lambda t: -2*t/(1+t**2)**2,                (-2.0, 0.5, 1.5)),
    Entry("abs",      sp.Abs(x),                      lambda t: np.sign(t),                      (-1.0, 0.7), avoid=(0.0,), complex_ok=False),
    Entry("relu",     sp.Max(0, x),                   lambda t: np.where(np.asarray(t) > 0, 1.0, 0.0), (-1.0, 0.7), avoid=(0.0,), complex_ok=False),
]
```

```python
# src/derivcmp/numeric.py
import numpy as np

def forward(f, x, h=None):
    h = h if h is not None else 1e-8 * max(1.0, abs(x));  return (f(x + h) - f(x)) / h
def central(f, x, h=None):
    h = h if h is not None else 1e-5 * max(1.0, abs(x));  return (f(x + h) - f(x - h)) / (2 * h)
def complex_step(f, x, h=1e-30):
    return float(np.imag(f(x + 1j * h)) / h)
def second_central(f, x, h=None):
    h = h if h is not None else 1e-4 * max(1.0, abs(x));  return (f(x + h) - 2 * f(x) + f(x - h)) / h ** 2
```

```python
# tests/test_numeric.py
import numpy as np, pytest
from derivcmp.catalogue import CATALOGUE
from derivcmp.numeric import central, complex_step

@pytest.mark.parametrize("e", CATALOGUE, ids=lambda e: e.name)
def test_hand_matches_symbolic(e):
    for p in e.points:
        assert np.isclose(float(e.hand(p)), float(e.df(p)), rtol=1e-9, atol=1e-12)

@pytest.mark.parametrize("e", CATALOGUE, ids=lambda e: e.name)
def test_central_matches_symbolic(e):
    for p in e.points:
        assert np.isclose(central(e.f, p), float(e.df(p)), rtol=1e-6, atol=1e-8)

@pytest.mark.parametrize("e", [e for e in CATALOGUE if e.complex_ok], ids=lambda e: e.name)
def test_complex_step_is_near_machine_precision(e):
    for p in e.points:
        assert np.isclose(complex_step(e.f, p), float(e.df(p)), rtol=1e-12, atol=1e-14)
```

`[VERIFY]` Some SymPy-lambdified expressions (e.g., `Max`, `Abs`) are not complex-safe in NumPy, and `sp.lambdify` for `Max(0, x)` produces `numpy.amax`-style code; the catalogue marks them `complex_ok=False`, but confirm each entry by running the tests.

### 12.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2 | Hand derivative equals SymPy derivative on all safe points (`rtol=1e-9`) for all catalogue entries |
| M2 | R3, R10 | Central matches SymPy to `1e-6` relative; complex-step matches to `1e-12` for all complex-safe entries; `Dual` matches on the entries it supports |
| M3 | R4 | V-shaped error plots for every entry and method; table of best `h`, min error, fitted slopes; fitted truncation-regime slopes near 1 (forward) and 2 (central) |
| M4 | R5 | Table of kink/domain behaviour with a one-line explanation per row; no unhandled exceptions or silent NaNs |
| M5 | R6–R8 | Cost and precision tables generated by the harness (your machine, your numbers) |
| M6 | R9 | `REPORT.md` with a decision table: *"which method when"*, each row citing a figure or table |

### 12.5 Questions the report must answer

1. Which method is most accurate when it applies, and what restricts it?
2. At what `h` does each finite-difference scheme bottom out, and how does it depend on `x` and `f`?
3. How much accuracy is lost going from `float64` to `float32`, and what does that imply for gradient checks?
4. What do the methods return at a kink, and which is the least misleading?
5. When would you prefer symbolic, dual-number, or reverse-mode differentiation in a real project?

### 12.6 Failure modes to demonstrate

`h` too small/large; `log` near 0 with `x − h < 0`; `tan` near `π/2`; `|x|`/ReLU at 0; `float32`; integer input; complex-step on `abs`; SymPy `simplify` producing a form that is slow or numerically worse than the raw derivative; `lambdify` with a function that SymPy cannot map to NumPy.

### 12.7 Stretch goals

1. Add Richardson extrapolation to the central difference and show the error improvement.
2. Add automatic `h` selection (e.g., compare derivative estimates at `h` and `h/2`) and test its robustness.
3. Reverse-mode mini-autodiff for scalar expressions (a `Value` class) and compare with the dual-number approach on a function of many inputs, counting passes (preview of 4C-07).
4. `hypothesis` property tests for the product/quotient/chain rules using the numeric methods.
5. Interval or high-precision (`mpmath`) reference for the derivative at tricky points; compare it with SymPy `[VERIFY: availability]`.

### 12.8 ML connection (README prompt)

Explain which of these methods your framework uses for training (reverse-mode autodiff) and which you use for testing (finite differences / complex-step), and why each is chosen.

### Check yourself (Unit 12)

1. Why are `abs` and `relu` flagged `complex_ok=False`?
2. What should the fitted log-log slope of truncation error versus `h` be for forward and for central differences?

**Reference answers:** (1) They rely on comparisons or magnitudes that break the analytic extension to complex numbers, so the complex-step trick does not apply. (2) About 1 and 2 respectively, in the truncation-dominated regime.

---

## Unit 13 — Project: Numerical gradient checker (`Projects/02-…md`)

### 13.1 Brief

Build `gradchk`: a reusable, mutation-tested gradient checker that supports vector and dictionary-of-arrays parameters, per-coordinate reporting, configurable tolerances and step sizes, and then use it to verify a tiny two-layer network with a hand-written backward pass. Include a bug-injection suite proving the checker catches realistic mistakes.

**Industry framing:** a gradient checker is a test utility that earns its keep every time someone writes a custom layer. Its quality is measured by the bugs it catches and the false alarms it avoids.

### 13.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | `numerical_grad(f, params, h)` | Works for a flat `ndarray` and for a `dict[str, ndarray]`; per-coordinate `h` scaled by `max(1, |θ|)`; leaves the input unmodified |
| R2 | `rel_error` | Per-coordinate and aggregate; `eps` floor; configurable |
| R3 | `gradcheck(f, grad, params, tol, h, n_points)` | Returns a structured report (`max_rel_err`, worst parameter and index, analytic vs numeric values, pass/fail); raises on request |
| R4 | Sampling | Option to check a random subset of coordinates for large parameter tensors; seeded |
| R5 | Kink guard | Option to detect near-kink evaluations (`|pre-activation| < δ`) and warn/skip |
| R6 | Reduction awareness | Report the estimated constant ratio `analytic/numeric` to hint at factor bugs |
| R7 | Tiny network | `x:(n,d)` → `tanh(xW1 + b1)` → `hW2 + b2` → MSE; hand-written backward for all four parameter arrays |
| R8 | Bug-injection suite | ≥ 8 injected bugs (missing `1/n`, factor 2, sign, transposed `W`, wrong axis in bias sum, forgot activation derivative, stale cache, off-by-one slice); each must be flagged |
| R9 | False-alarm study | Show conditions producing false failures (ReLU at 0, `float32`, dropout) and the guards that fix them |
| R10 | CLI/pytest integration | `pytest` fixture/helper `assert_gradients_close(...)` with readable messages |
| R11 | Report | `REPORT.md`: detection matrix (bug × detected?), error magnitudes per bug, recommended thresholds with evidence |

### 13.3 Layout and starter

```
gradchk/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/gradchk/{__init__,core,report,tinynet,bugs}.py
├── tests/{test_core,test_tinynet,test_bugs,test_false_alarms}.py
├── notebooks/05_gradient_checker.ipynb
└── results/
```

```python
# src/gradchk/core.py
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

def _flatten(params):
    if isinstance(params, dict):
        keys = list(params); shapes = {k: params[k].shape for k in keys}
        vec = np.concatenate([np.asarray(params[k], float).ravel() for k in keys])
        return vec, keys, shapes
    p = np.asarray(params, float); return p.ravel().copy(), None, p.shape

def _unflatten(vec, keys, shapes):
    if keys is None: return vec.reshape(shapes)
    out, i = {}, 0
    for k in keys:
        n = int(np.prod(shapes[k])); out[k] = vec[i:i + n].reshape(shapes[k]); i += n
    return out

def numerical_grad(f, params, h=1e-5, idx=None):
    vec, keys, shapes = _flatten(params)
    g = np.zeros_like(vec)
    for i in (range(vec.size) if idx is None else idx):
        step = h * max(1.0, abs(vec[i]))
        up, dn = vec.copy(), vec.copy(); up[i] += step; dn[i] -= step
        g[i] = (f(_unflatten(up, keys, shapes)) - f(_unflatten(dn, keys, shapes))) / (2 * step)
    return g, keys, shapes

@dataclass
class Report:
    max_rel_err: float
    worst_index: int
    analytic: float
    numeric: float
    ratio: float
    passed: bool

def gradcheck(f, grad, params, tol=1e-6, h=1e-5, subset=None, seed=0, eps=1e-8, raise_on_fail=False):
    vec, keys, shapes = _flatten(params)
    idx = None
    if subset is not None and subset < vec.size:
        idx = np.random.default_rng(seed).choice(vec.size, size=subset, replace=False)
    g_num, _, _ = numerical_grad(f, params, h, idx)
    a = grad(params)
    g_ana = np.concatenate([np.asarray(a[k], float).ravel() for k in keys]) if keys else np.asarray(a, float).ravel()
    sel = np.arange(vec.size) if idx is None else idx
    num, ana = g_num[sel], g_ana[sel]
    rel = np.abs(ana - num) / np.maximum(np.abs(ana) + np.abs(num), eps)
    j = int(np.argmax(rel))
    ratio = float(np.dot(ana, num) / max(np.dot(num, num), eps))        # least-squares scale: ≈ 1 if correct
    rep = Report(float(rel[j]), int(sel[j]), float(ana[j]), float(num[j]), ratio, bool(rel[j] <= tol))
    if raise_on_fail and not rep.passed:
        raise AssertionError(f"gradcheck failed: {rep}")
    return rep
```

```python
# src/gradchk/tinynet.py
import numpy as np

def init(d=3, hdim=4, out=1, seed=0):
    g = np.random.default_rng(seed)
    return {"W1": g.normal(scale=0.5, size=(d, hdim)), "b1": g.normal(scale=0.1, size=hdim),
            "W2": g.normal(scale=0.5, size=(hdim, out)), "b2": g.normal(scale=0.1, size=out)}

def forward(P, X):
    Z1 = X @ P["W1"] + P["b1"]          # (n, h)
    H = np.tanh(Z1)
    Yh = H @ P["W2"] + P["b2"]          # (n, out)
    return Z1, H, Yh

def loss(P, X, Y):
    _, _, Yh = forward(P, X)
    return 0.5 * np.mean(np.sum((Yh - Y) ** 2, axis=1))        # mean over samples

def backward(P, X, Y):
    n = len(X)
    Z1, H, Yh = forward(P, X)
    dYh = (Yh - Y) / n                                          # (n, out)
    dW2 = H.T @ dYh;  db2 = dYh.sum(0)
    dH = dYh @ P["W2"].T                                        # (n, h)
    dZ1 = dH * (1 - H ** 2)                                     # tanh'
    dW1 = X.T @ dZ1;  db1 = dZ1.sum(0)
    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}
```

```python
# tests/test_tinynet.py
import numpy as np
from gradchk.core import gradcheck
from gradchk import tinynet as T

def test_correct_backward_passes():
    rng = np.random.default_rng(1)
    X, Y = rng.normal(size=(8, 3)), rng.normal(size=(8, 1))
    P = T.init()
    rep = gradcheck(lambda p: T.loss(p, X, Y), lambda p: T.backward(p, X, Y), P, tol=1e-6)
    assert rep.passed and abs(rep.ratio - 1.0) < 1e-5

def test_missing_inner_derivative_is_caught():
    rng = np.random.default_rng(1)
    X, Y = rng.normal(size=(8, 3)), rng.normal(size=(8, 1)); P = T.init()
    def bad(p):
        g = T.backward(p, X, Y)
        Z1, H, Yh = T.forward(p, X)
        dZ1 = (((Yh - Y) / len(X)) @ p["W2"].T)                # forgot tanh'
        g["W1"], g["b1"] = X.T @ dZ1, dZ1.sum(0)
        return g
    rep = gradcheck(lambda p: T.loss(p, X, Y), bad, P)
    assert not rep.passed and rep.max_rel_err > 1e-3
```

`[VERIFY]` `ratio` is a least-squares scale estimate; it is near `1` for a correct gradient and near the constant factor for a pure scale bug, but it is only a hint for other bug types. Confirm on your injected-bug suite.

### 13.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Passes on 6 analytic functions at 20 random points (`tol=1e-6`); input arrays are verified unchanged after a call |
| M2 | R4–R6 | Subset sampling is seeded and reproducible; kink guard flags ReLU-at-0 cases; ratio ≈ 1 for correct gradients and ≈ the injected factor for scale bugs |
| M3 | R7 | Tiny network passes the check for all four parameter arrays at 20 random initializations |
| M4 | R8 | All ≥ 8 injected bugs flagged with `max_rel_err > 1e-3`; detection matrix recorded |
| M5 | R9–R10 | False-alarm cases reproduced and fixed by documented guards; a pytest helper with a readable failure message |
| M6 | R11 | `REPORT.md` with the detection matrix, error magnitudes, and threshold recommendations backed by the measured distributions (correct-gradient errors vs buggy-gradient errors) |

### 13.5 Statistical-honesty requirements

- Report the **distribution** of relative errors for correct gradients (over ≥ 100 random points) and for each injected bug, not a single number.
- Recommend a tolerance **between** the two distributions, and show the margin.
- State any bug your checker **missed** or detected only weakly, and explain why (e.g., a bug affecting only exact-zero inputs).

### 13.6 Failure modes to demonstrate

ReLU at exactly 0 (false alarm); `float32` precision (false alarm); dropout/randomness (non-deterministic forward); `h` too small (noise) and too large (bias); parameters of very different scales (hence per-coordinate `h`); a bug in the **forward** pass that the check cannot see; checking at a single point that happens to hide the bug; mutating shared arrays during evaluation.

### 13.7 Stretch goals

1. Directional-derivative check for huge parameter sets: compare `(f(θ + hv) − f(θ − hv))/2h` with `∇f·v` for random unit vectors `v` (cost `O(1)` evaluations per direction), and show how many directions are needed to catch each bug.
2. Complex-step variant for analytic losses and compare sensitivity with central differences.
3. Support vector-valued outputs by checking the Jacobian-vector product (preview of Module 07 and 4C-07).
4. Add a second network with a softmax cross-entropy output and check its backward pass (`p − y` form).
5. Integrate with `pytest` as a plugin-style fixture and publish it as an installable package with a version tag.

### 13.8 ML connection (README prompt)

Write a short guide titled "How I verify a new layer or loss before training with it," listing the checks (forward values, gradient check, shape tests, kink handling) and which parts of this project implement each.

### Check yourself (Unit 13)

1. Why scale `h` per coordinate?
2. What does `ratio ≈ 2.0` suggest?
3. What kind of bug can a gradient check never reveal?

**Reference answers:** (1) Parameters have different magnitudes; a fixed `h` is too large for tiny parameters and too small relative to large ones. (2) The analytic gradient is twice the numeric one: a missing/extra factor of 2 (or a `1/n` mismatch between loss and gradient). (3) A bug in the forward computation itself, because the check compares the function with its own gradient; verify forward values separately.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 8 lessons, 2 projects, 13 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Module 07/08/13/14, 4C-02/03/05/07/08, and Stage 5 pointers (5B-13, 5C-01/02/03/07, 5D-02) are derived from folder names only.
3. `[VERIFY]` Numerical rules of thumb for `h` (`√ε`, `ε^{1/3}`, `ε^{1/4}`) and gradient-check thresholds: confirm by running Lab 2.7/9.6 and report your own values.
4. `[VERIFY]` Claims about GELU derivative range, framework ReLU′(0) conventions, weight-decay conventions (`λw` vs `2λw`), and sharp-vs-flat minima: confirm or cite before the final lesson files assert them.
5. `[VERIFY]` Starter code was run (SymPy 1.14, NumPy 2.3): all lesson snippets executed; all 34 `derivcmp` tests and both `gradchk` tests passed after one fix (the ReLU hand derivative failed on a plain Python float). A separate run injected 8 bugs into the tiny network's backward pass (missing `1/n`, factor 2, sign flip, row-swapped `W1`, wrong bias reduction, forgotten `tanh′`, rolled `W2`, zeroed `b1`); all were flagged (`max_rel_err` ≥ 0.33) while the correct gradient scored about 3e-10. `ratio` matched the injected factor only for pure scale bugs (8.0 and 2.0) and is otherwise just a hint. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, accuracy, or tolerance figure appears without the measurement that produced it.
