# SYLLABUS — 06-Integral-Calculus (S4B-06)

**Stage 4B — Mathematics for Machine Learning · Module 06 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SymPy for symbolic cross-checks; Matplotlib and pytest where stated; SciPy is optional and never required). This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Antiderivatives and the indefinite integral | `01-antiderivatives-and-the-indefinite-integral.md` | Beginner |
| 3 | Definite integrals and the fundamental theorem of calculus | `02-definite-integrals-and-the-fundamental-theorem-of-calculus.md` | Beginner → Intermediate |
| 4 | Integration by substitution and by parts | `03-integration-by-substitution-and-by-parts.md` | Intermediate |
| 5 | Improper integrals | `04-improper-integrals.md` | Intermediate |
| 6 | Numerical integration: Riemann sums and the trapezoid rule | `05-numerical-integration-riemann-sums-and-the-trapezoid-rule.md` | Intermediate → Advanced |
| 7 | Double integrals: introduction | `06-double-integrals-introduction.md` | Intermediate → Advanced |
| 8 | Practice question bank | `practice-questions.md` | All levels |
| 9 | Project index | `Projects/README.md` | Intermediate |
| 10 | Project: numerical integration toolkit | `Projects/01-numerical-integration-toolkit.md` | Intermediate → Advanced |
| 11 | Project: area under a density curve lab | `Projects/02-area-under-a-density-curve-lab.md` | Intermediate → Advanced |

**Prerequisites:** Module 05 (derivatives, chain rule, product rule, exp/log/trig derivatives, numerical vs analytical checking); Stage 4A Module 10 (sequences, series, summation) and Module 13 (limits). **Plan slot:** weeks 7–8 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** this module is safe to defer on the eval-focused track, but Lessons 2, 4, 5 and 6 are the mathematics behind probability densities, expectations, and normalizing constants, so complete at least those before Module 09.

**Teaching stance (industry, not university):** integration by hand is taught only as far as it lets you *read derivations* and *check results*. In practice you will (1) look up or symbolically compute an antiderivative, (2) integrate numerically, or (3) estimate by sampling. Every analytic result below is verified numerically and, where possible, symbolically.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Derivatives tell you how a quantity changes; **integrals accumulate it**. In ML, probabilities of continuous variables are *areas under density curves*, expectations are *integrals weighted by a density*, normalizing constants are *integrals that must equal 1*, and a CDF is a *running integral of a pdf*. ROC-AUC is literally an area. Many "intractable" quantities in Bayesian inference, VAEs, and diffusion models are integrals that nobody can solve analytically, which is why numerical and sampling-based integration exist.

### 1.2 Outcomes

1. Explain the integral as accumulated change and as (signed) area, and connect it to the derivative through the fundamental theorem of calculus.
2. Find antiderivatives of standard functions and **verify** them by differentiation.
3. Apply substitution and integration by parts, and recognise which results are non-elementary (e.g., `∫e^{−x²}dx`).
4. Decide whether an improper integral converges, and detect a diverging one numerically.
5. Implement left/right/midpoint Riemann sums, trapezoid, Simpson, and Gauss–Legendre rules, and measure their convergence orders.
6. Compute probabilities, CDFs, quantiles, means, and variances of continuous densities by numerical integration.
7. Evaluate double integrals on grids and by Monte Carlo, and explain why grids fail in high dimension.
8. Compute ROC-AUC as an area and show it equals the rank-based formula.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Antiderivatives | CDF as an antiderivative; softplus ↔ sigmoid | SymPy + differentiate-to-verify |
| 2 | Definite integrals and the FTC | Probability = area; mean value = expectation | Cumulative integral, CDF of exponential |
| 3 | Substitution and parts | Gaussian normalization, Gamma function, `E[X]` | Hand derivation checked numerically |
| 4 | Improper integrals | Infinite supports, heavy tails, divergence | Truncation study; Cauchy mean |
| 5 | Numerical integration | Densities without closed forms; AUC | Rule zoo + order-of-convergence plot |
| 6 | Double integrals | Joint densities, marginals, 2-D normalization | Grid vs Monte Carlo; polar Gaussian |

### 1.4 Concept map

```
derivative (Module 05) ◄── FTC ──► definite integral = signed area = accumulated change
        │                                   │
   antiderivative F, +C                     ├─► pdf → CDF (running integral) → probabilities, quantiles
        │                                   ├─► expectation E[g(X)] = ∫ g(x) p(x) dx
   substitution / parts                     ├─► improper: infinite support, heavy tails, divergence
   (chain/product rule reversed)            ├─► numerical: Riemann → trapezoid → Simpson → Gauss; error orders
                                            └─► double integral: joint density, marginals, 2-D normalization
                                                grids cost N^d  ──►  Monte Carlo (Module 11)
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "sympy>=1.12" matplotlib pytest      # scipy optional, for cross-checks only
```

Rules for every lab: **check an integral three ways when possible** (closed form, numerical rule, SymPy); verify an antiderivative by differentiating it; report absolute **and** relative error with the number of function evaluations; test on an integral with a known answer *before* trusting the code on an unknown one; seed all sampling; use `float64`.

**NumPy note:** the trapezoid helper has been renamed across NumPy versions (`np.trapz` vs `np.trapezoid`) `[VERIFY in your pinned version]`. This module implements its own `trapezoid` so nothing depends on the name.

### 1.6 Checkpoint

Your integration toolkit reproduces `∫₀^π sin x dx = 2` with the trapezoid and Simpson rules, shows measured convergence slopes of about `2` and `4` on a log-log plot, and your density lab shows that the standard normal pdf integrates to `1` and that `P(−1.96 < Z < 1.96) ≈ 0.95` to at least 6 digits.

### Check yourself (Unit 1)

1. Give three ML quantities that are integrals.
2. Why implement your own `trapezoid` instead of calling NumPy's?

**Reference answers:** (1) A probability of a continuous event, an expectation, a normalizing constant (also a CDF, ROC-AUC). (2) The NumPy function name differs across versions; our own version is dependency-free and lets us count evaluations.

---

## Unit 2 — Antiderivatives and the indefinite integral (`01-…md`)

### 2.1 Why ML needs this

A CDF is an antiderivative of a pdf. The antiderivative of the sigmoid is softplus, which is why softplus appears inside stable log-loss formulas. Recognising these pairs lets you check derivations in papers and test code.

### 2.2 Intuition

Differentiation asks "given a curve, what is its slope everywhere?" Antidifferentiation asks the reverse: "given the slope everywhere, what curve produces it?" Many curves share the same slope; they differ by a vertical shift, the **constant `C`**.

### 2.3 Mechanics

- **Definition:** `F` is an antiderivative of `f` if `F′ = f`. The **indefinite integral** is the whole family: `∫ f(x) dx = F(x) + C`.
- **Linearity:** `∫(αf + βg) = α∫f + β∫g`.
- **Basic table** (check each by differentiating):

| `f(x)` | `∫ f(x) dx` | Note |
|---|---|---|
| `xⁿ` | `xⁿ⁺¹/(n+1) + C` | `n ≠ −1` |
| `1/x` | `ln|x| + C` | the missing power-rule case; domain excludes 0 |
| `eˣ` | `eˣ + C` | |
| `aˣ` | `aˣ/ln a + C` | `a > 0, a ≠ 1` |
| `sin x` | `−cos x + C` | radians |
| `cos x` | `sin x + C` | |
| `1/(1 + x²)` | `arctan x + C` | |
| `σ(x) = 1/(1+e⁻ˣ)` | `ln(1 + eˣ) + C` (softplus) | Module 05 |
| `tanh x` | `ln cosh x + C` | |

- **Always verify by differentiating:** if `F′ = f` you are right; if not, you are not. This is the cheapest correctness test in calculus.
- **Non-elementary integrals:** some elementary functions have no elementary antiderivative, e.g. `e^{−x²}`, `sin(x)/x`, `1/ln x`. `∫e^{−x²}dx` is expressed via the **error function**: `∫₀ˣ e^{−t²}dt = (√π/2) erf(x)`. The normal CDF is built from it.
- **The constant of integration matters** when you use an antiderivative to solve an initial-value problem or fit to data: `F(x) + C` with `C` fixed by `F(x₀) = y₀`.
- **Integral of a rate is a total:** if `f` is a rate (per second), `∫ f` is an amount.

**Worked example:** `∫ (3x² + 2/x) dx = x³ + 2 ln|x| + C`. Check: `d/dx = 3x² + 2/x` ✓.

### 2.4 Code

```python
import numpy as np
import sympy as sp

x = sp.symbols("x", real=True)

def check_antiderivative(f_expr, F_expr, pts=(0.3, 0.9, 1.7)):
    """Return True if d/dx F == f at sample points (numeric, avoids simplify pitfalls)."""
    d = sp.lambdify(x, sp.diff(F_expr, x), "numpy"); f = sp.lambdify(x, f_expr, "numpy")
    return all(np.isclose(d(p), f(p), rtol=1e-10) for p in pts)

assert check_antiderivative(3*x**2 + 2/x, x**3 + 2*sp.log(x))
assert check_antiderivative(1/(1 + sp.exp(-x)), sp.log(1 + sp.exp(x)))       # sigmoid → softplus
assert check_antiderivative(sp.tanh(x), sp.log(sp.cosh(x)))
assert check_antiderivative(sp.sin(x), -sp.cos(x))
assert not check_antiderivative(sp.sin(x), sp.cos(x))                         # a wrong answer is caught

# let SymPy find antiderivatives, then verify them
for f in (x**2, 1/x, sp.exp(-x), sp.exp(-x**2), sp.sin(x)**2):
    F = sp.integrate(f, x); print(f, "→", F)
    assert check_antiderivative(f, F)

# the constant: the same slope, different curves; fix C with a data point
F0 = lambda t: t**3                                    # one antiderivative of 3x²
C = 5.0 - F0(2.0)                                      # require F(2) = 5
F = lambda t: F0(t) + C
print(F(2.0), "C =", C)

# softplus is the antiderivative of sigmoid (numerical check, no SymPy)
sig = lambda t: 1 / (1 + np.exp(-t)); sp_ = lambda t: np.logaddexp(0, t)
for t in (-3.0, 0.0, 2.5):
    assert np.isclose((sp_(t + 1e-6) - sp_(t - 1e-6)) / 2e-6, sig(t), rtol=1e-6)

# non-elementary: e^{-x^2} → error function
import math
def gaussian_antiderivative(t): return math.sqrt(math.pi) / 2 * math.erf(t)    # ∫_0^t e^{-s²} ds
h = 1e-6
assert np.isclose((gaussian_antiderivative(0.8 + h) - gaussian_antiderivative(0.8 - h)) / (2 * h), math.exp(-0.64), rtol=1e-6)
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting `+ C` | Wrong answer in initial-value problems | Write it; fix it from a condition |
| Power rule with `n = −1` | `x⁰/0` division by zero | `∫1/x = ln|x|` |
| `ln x` instead of `ln|x|` | Wrong on negative `x` | State the domain |
| Not verifying by differentiation | Silent algebra slips | `check_antiderivative` test |
| Expecting a closed form for every integrand | Wasted time | Recognise non-elementary cases; go numerical or use `erf`-style special functions |
| Trusting SymPy output blindly (assumptions, branch cuts) | Different forms or conditions | Verify numerically at sample points |
| Mixing degrees and radians in trig integrals | Off by `π/180` | Radians |

### 2.6 ML link

- **CDF = antiderivative of the pdf** (Lesson 2, Module 09): `F(x) = ∫_{−∞}^{x} p(t) dt`.
- **Softplus = ∫ sigmoid** (Module 05): the form inside stable BCE and smooth ReLU variants.
- **Normal CDF** uses `erf`: the reason `scipy.stats.norm.cdf` exists; no closed form in elementary functions (Module 10).
- **Log-partition and normalizers:** many "∫ exp(…) dx" terms are non-elementary, which motivates approximation methods (4C-05, 4C-10).

### 2.7 Lab (45 min)

1. Build a table of 12 integrals; derive by hand; verify each with `check_antiderivative` and SymPy.
2. Plot a family `F(x) + C` for several `C` and show they all have the same slope field.
3. Verify softplus ↔ sigmoid and `ln cosh` ↔ tanh numerically.
4. Compute `∫₀^1 e^{−x²}dx` via `erf` and via a rule you write yourself; compare.

### Check yourself (Unit 2)

1. What is `∫ 1/x dx`, and why does the power rule not apply?
2. How do you verify an antiderivative without trusting your algebra?
3. Does `e^{−x²}` have an elementary antiderivative?

**Reference answers:** (1) `ln|x| + C`; the power rule would divide by `n + 1 = 0`. (2) Differentiate it and compare with the integrand. (3) No; it is expressed with the error function.

---

## Unit 3 — Definite integrals and the fundamental theorem of calculus (`02-…md`)

### 3.1 Why ML needs this

`P(a < X < b) = ∫ₐᵇ p(x) dx` and `E[X] = ∫ x p(x) dx` are definite integrals. The FTC is what links a pdf and its CDF, and it is why cumulative sums of a rate recover a total.

### 3.2 Intuition

Slice the region under a curve into thin vertical strips, add the strip areas, and let the strips get thinner: that limit is the **definite integral**. Areas below the axis count **negatively**. The FTC says this total can be computed from any antiderivative: *net change = end value − start value*.

### 3.3 Mechanics

- **Definition (Riemann):** `∫ₐᵇ f(x) dx = lim_{n→∞} Σ f(xᵢ*) Δx`, `Δx = (b − a)/n`.
- **FTC, part 1:** if `G(x) = ∫ₐˣ f(t) dt` then `G′(x) = f(x)`. (Accumulate, then differentiate: you get the integrand back.)
- **FTC, part 2:** `∫ₐᵇ f(x) dx = F(b) − F(a)` for any antiderivative `F` (the `+C` cancels).
- **Properties:** linearity; additivity `∫ₐᵇ = ∫ₐᶜ + ∫ᶜᵇ`; reversing limits flips the sign; `|∫f| ≤ ∫|f|`; if `f ≤ g` then `∫f ≤ ∫g`.
- **Signed vs absolute area:** `∫₀^{2π} sin x dx = 0` but the geometric area is `∫|sin x| = 4`.
- **Mean value of a function:** `f̄ = (1/(b−a)) ∫ₐᵇ f(x) dx`. For `X ~ Uniform(a, b)` this is exactly `E[f(X)]`: *an average of `f` over a continuous interval is an expectation under a uniform density.*
- **Expectation and probability (preview of Module 09):** for a pdf `p`: `∫p = 1`, `P(a<X<b) = ∫ₐᵇ p`, `E[g(X)] = ∫ g(x)p(x)dx`.
- **Accumulation view:** distance = ∫ speed; total loss over a continuous range of a hyperparameter = ∫ loss rate.

**Worked example:** `∫₁³ (2x + 1) dx = [x² + x]₁³ = (9 + 3) − (1 + 1) = 10`. Exponential pdf `p(x) = λe^{−λx}`: `F(x) = ∫₀ˣ p = 1 − e^{−λx}`, and `P(1 < X < 2) = e^{−λ} − e^{−2λ}`.

### 3.4 Code

```python
import numpy as np

def trapezoid(f, a, b, n=1000):
    x = np.linspace(a, b, n + 1); y = f(x); h = (b - a) / n
    return h * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2)

def cumtrapz(y, x):
    """Running integral: out[i] = ∫_{x0}^{x_i} y dx (trapezoid), same length as x."""
    return np.r_[0.0, np.cumsum(np.diff(x) * (y[1:] + y[:-1]) / 2)]

# FTC part 2: area = F(b) - F(a)
f = lambda t: 2 * t + 1;  F = lambda t: t ** 2 + t
assert np.isclose(trapezoid(f, 1, 3), F(3) - F(1), rtol=1e-12)               # exact for linear f

# signed vs absolute area
assert abs(trapezoid(np.sin, 0, 2 * np.pi, 10_000)) < 1e-9
assert np.isclose(trapezoid(lambda t: np.abs(np.sin(t)), 0, 2 * np.pi, 100_000), 4.0, rtol=1e-8)

# FTC part 1: derivative of the running integral returns the integrand
xs = np.linspace(0, 3, 30_001); g = lambda t: np.sin(t ** 2)
G = cumtrapz(g(xs), xs)
dG = np.gradient(G, xs)
assert np.max(np.abs(dG[5:-5] - g(xs[5:-5]))) < 1e-4

# exponential distribution: CDF as a running integral of the pdf
lam = 1.5
pdf = lambda t: lam * np.exp(-lam * t)
t = np.linspace(0, 12, 120_001)
cdf = cumtrapz(pdf(t), t)
assert np.max(np.abs(cdf - (1 - np.exp(-lam * t)))) < 1e-8
p_1_2 = np.interp(2, t, cdf) - np.interp(1, t, cdf)
assert np.isclose(p_1_2, np.exp(-lam) - np.exp(-2 * lam), atol=1e-8)

# mean value = expectation under a uniform density
a, b = 0.0, 2.0; fn = lambda u: u ** 2
mean_value = trapezoid(fn, a, b, 100_000) / (b - a)                         # (1/(b-a)) ∫ f
rng = np.random.default_rng(0)
mc = fn(rng.uniform(a, b, 2_000_000)).mean()                                # E[f(U)], U ~ Uniform(a, b)
print(mean_value, mc)                                                       # 4/3 and ≈ 1.333 (Monte Carlo error ~1e-3)

# properties: additivity and reversal
assert np.isclose(trapezoid(np.cos, 0, 2, 20_000) + trapezoid(np.cos, 2, 5, 20_000), trapezoid(np.cos, 0, 5, 40_000), rtol=1e-8)
assert np.isclose(trapezoid(np.cos, 5, 0, 20_000), -trapezoid(np.cos, 0, 5, 20_000))     # reversed limits (h < 0)
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Treating net signed area as geometric area | A positive and negative region cancel | Split at sign changes, or integrate `|f|` |
| Evaluating `F(b) − F(a)` across a discontinuity or singularity of `F` (e.g., `∫₋₁¹ 1/x² dx` via `−1/x`) | Wrong finite answer for a divergent integral | Check continuity of `f` on `[a, b]`; Lesson 4 |
| Reversing limits without flipping the sign | Sign error | Apply the property explicitly |
| Forgetting that a pdf is a *density*, not a probability | `p(x) > 1` seems "impossible" | `P` is area; a narrow pdf can exceed 1 |
| Using the running integral at grid resolution too coarse for a sharp peak | Wrong CDF values | Refine near the peak; check normalization |
| Using `np.gradient` at the boundary of the grid | Edge error | Exclude edge points when verifying |
| Confusing `∫f` with `Σf` | Missing the `Δx` factor | Always multiply by the spacing |

### 3.6 ML link

- **CDF and probabilities** (Module 09, 10): `P(a<X<b)` is an area; the CDF is a running integral.
- **Expectation** (Module 09): `E[g(X)] = ∫ g p`.
- **Mean value of a loss over a range** of a hyperparameter or time window is an integral average.
- **ROC-AUC** is the area under the ROC curve (Lesson 5).
- **Cumulative metrics** (cumulative gain, cumulative explained variance) are running integrals/sums.

### 3.7 Lab (60 min)

1. Verify `∫ₐᵇ f = F(b) − F(a)` on 6 functions with known antiderivatives using your `trapezoid`.
2. Build `cumtrapz`, then verify FTC part 1 on `sin(t²)` (a function with no elementary antiderivative).
3. Compute the CDF of an exponential and of a triangular density by running integral; verify against closed forms; compute three interval probabilities.
4. Demonstrate signed vs geometric area, and the pdf-can-exceed-1 point with `Uniform(0, 0.1)`.

### Check yourself (Unit 3)

1. What does FTC part 1 say about `d/dx ∫ₐˣ f(t) dt`?
2. Compute `∫₀^π sin x dx`.
3. Why can a pdf value exceed 1?

**Reference answers:** (1) It equals `f(x)`. (2) `2`. (3) A pdf is a density; probability is area, so a narrow density must be tall.

---

## Unit 4 — Integration by substitution and by parts (`03-…md`)

### 4.1 Why ML needs this

These are the two techniques behind most closed-form derivations you will meet: normalizing the Gaussian, computing the mean of an exponential, building the Gamma function, and the expected-value identities in Module 09–10. You will rarely integrate by hand at work, but you must be able to **follow and check** such derivations.

### 4.2 Mechanics

- **Substitution (the chain rule in reverse):** `∫ f(g(x)) g′(x) dx = ∫ f(u) du` with `u = g(x)`. For definite integrals, **change the limits** to `u`-values: `∫ₐᵇ f(g(x))g′(x)dx = ∫_{g(a)}^{g(b)} f(u)du`.
- **By parts (the product rule in reverse):** `∫ u dv = uv − ∫ v du`. Choose `u` so that `du` is simpler (LIATE heuristic: Logarithmic, Inverse trig, Algebraic, Trig, Exponential `[JUDGEMENT]`).
- **Standard results used in ML:**
  - Linear substitution: `∫ e^{−λx} dx = −e^{−λx}/λ + C`.
  - Standardizing a Gaussian: `z = (x − μ)/σ` turns `∫ (1/(σ√2π)) e^{−(x−μ)²/(2σ²)} dx` into `∫ (1/√2π) e^{−z²/2} dz`, which is `1` (the value of `∫e^{−z²/2}dz = √(2π)` is derived with a double integral in Lesson 6).
  - Exponential mean: `E[X] = ∫₀^∞ x λe^{−λx} dx = 1/λ` (by parts with `u = x`, `dv = λe^{−λx}dx`).
  - Gamma function: `Γ(s) = ∫₀^∞ x^{s−1} e^{−x} dx`; by parts, `Γ(s + 1) = sΓ(s)`, so `Γ(n) = (n − 1)!` for integers, and `Γ(½) = √π`.
  - Substitution `x = u²` rewrites `Γ(s) = 2∫₀^∞ u^{2s−1} e^{−u²} du`, which removes the endpoint singularity at `0` for `s < 1`, a numerical-stability use of substitution.
  - `∫ ln x dx = x ln x − x + C` (by parts); related to entropy integrals (Module 13).
- **Where hand integration stops:** products like `e^{x} sin x` need repeated parts; `e^{−x²}` is non-elementary; many Bayesian integrals have no closed form. Switch to numerics or sampling.

**Worked example (parts):** `∫ x eˣ dx`: `u = x, dv = eˣdx` ⇒ `x eˣ − ∫ eˣ dx = (x − 1)eˣ + C`. **Worked example (substitution):** `∫₀^1 2x e^{x²} dx`: `u = x²`, `du = 2x dx`, limits `0 → 1` ⇒ `∫₀^1 eᵘ du = e − 1`.

### 4.3 Code

```python
import math
import numpy as np
import sympy as sp

x = sp.symbols("x", positive=True)

# verify hand results symbolically
assert sp.simplify(sp.integrate(x * sp.exp(x), x) - (x - 1) * sp.exp(x)) == 0           # by parts
assert sp.simplify(sp.integrate(sp.log(x), x) - (x * sp.log(x) - x)) == 0
assert sp.simplify(sp.integrate(2 * x * sp.exp(x ** 2), (x, 0, 1)) - (sp.E - 1)) == 0     # substitution

# numerical integrator (Gauss–Legendre, from Lesson 5) to check definite results
def gauss_legendre(f, a, b, n=64):
    xs, ws = np.polynomial.legendre.leggauss(n)
    t = 0.5 * (b - a) * xs + 0.5 * (a + b)
    return 0.5 * (b - a) * np.sum(ws * f(t))

# substitution: ∫_0^1 2x e^{x²} dx = e − 1
assert np.isclose(gauss_legendre(lambda t: 2 * t * np.exp(t ** 2), 0, 1), math.e - 1, rtol=1e-12)

# exponential mean E[X] = 1/λ  (truncate the infinite range far into the tail)
lam = 2.0
EX = gauss_legendre(lambda t: t * lam * np.exp(-lam * t), 0, 40 / lam, n=200)
assert np.isclose(EX, 1 / lam, rtol=1e-10)

# Gamma function by parts: Γ(s+1) = s Γ(s), and the u² substitution for s < 1
def gamma_via_integral(s, U=8.0):
    # Γ(s) = 2 ∫_0^∞ u^{2s−1} e^{−u²} du ; smooth at 0 for s ≥ 1/2
    return 2 * gauss_legendre(lambda u: u ** (2 * s - 1) * np.exp(-u ** 2), 0, U, n=200)
for s in (0.5, 1.0, 2.5, 4.0):
    assert np.isclose(gamma_via_integral(s), math.gamma(s), rtol=1e-9), s
assert np.isclose(gamma_via_integral(0.5), math.sqrt(math.pi), rtol=1e-9)
for s in (1.3, 2.7): assert np.isclose(math.gamma(s + 1), s * math.gamma(s), rtol=1e-12)
assert math.gamma(6) == 120.0                                                           # (6−1)!

# Gaussian normalization after standardizing (substitution z = (x − μ)/σ)
mu, sigma = 1.7, 0.6
pdf = lambda t: np.exp(-0.5 * ((t - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
assert np.isclose(gauss_legendre(pdf, mu - 12 * sigma, mu + 12 * sigma, n=300), 1.0, rtol=1e-12)
```

### 4.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting to convert limits after `u`-substitution | Wrong definite value | Convert, or revert to `x` before applying limits |
| Forgetting the `du` factor (e.g., `2x dx`) | Missing constant | Write `du = g′(x) dx` explicitly |
| Choosing `u` and `dv` badly in parts | The integral gets harder | Try the other assignment; LIATE as a heuristic only |
| Sign error in `uv − ∫v du` | Off-by-sign result | Differentiate the answer |
| Truncating an infinite range too early | Missing tail mass | Check the tail beyond the cut-off analytically (`e^{−λT}`) |
| Integrating hard analytic cases by hand | Wasted time | SymPy first; numerics as a check |
| Evaluating `x^{2s−1}` at `0` for `s < ½` | `inf` | Use the substitution only where the integrand is finite, or treat as improper (Lesson 4) |

### 4.5 ML link

- **Gaussian density normalization** underlies Module 10 and 4C-04.
- **Exponential / Gamma / Poisson families:** their normalizers and means come from these two techniques (Module 10, 4C-05).
- **Gamma function** appears in the Beta/Dirichlet normalizers (Module 10 Lesson 6) and the volume of high-dimensional balls (Module 04 Lesson 3).
- **Entropy integrals** `−∫ p ln p` use parts and substitutions (Module 13, 4C-06).
- **Reparameterization** in VAEs is a change of variables, i.e., substitution for random variables (4C-04 Lesson 7, 4C-10) `[VERIFY]`.

### 4.6 Lab (75 min)

1. Do 10 substitution and 10 by-parts integrals by hand; verify each with SymPy and numerically.
2. Derive `E[X]` and `Var(X)` for the exponential distribution by parts; verify against numerical integration.
3. Show `Γ(s+1) = sΓ(s)` numerically and compute `Γ(½)` by the `u²` substitution; compare the naive integrand's behaviour at `0` with the substituted one.
4. Confirm that the standardized Gaussian integrates to 1 for three `(μ, σ)` pairs.

### Check yourself (Unit 4)

1. Evaluate `∫₀^1 x e^{x²} dx`.
2. By parts, what is `E[X]` for the exponential distribution with rate `λ`?
3. Why does `Γ(n) = (n−1)!` follow from integration by parts?

**Reference answers:** (1) `u = x²`: `½(e − 1)`. (2) `1/λ`. (3) The by-parts identity gives `Γ(s+1) = sΓ(s)` with `Γ(1) = 1`, so induction yields `(n−1)!`.

---

## Unit 5 — Improper integrals (`04-…md`)

### 5.1 Why ML needs this

Most continuous distributions have **infinite support** (normal, exponential), so their normalization and moments are improper integrals. Heavy-tailed distributions can have *infinite* means, and a number of ML quantities (KL divergence, importance weights, some losses) can diverge. Knowing when an integral exists is part of knowing when an estimator is trustworthy.

### 5.2 Intuition

An improper integral is a definite integral with an infinite limit, or an integrand that blows up inside the interval, handled by a limit: `∫ₐ^∞ f = lim_{T→∞} ∫ₐᵀ f`. If the limit exists and is finite the integral **converges**; otherwise it **diverges**.

### 5.3 Mechanics

- **Types:** (I) infinite limits; (II) unbounded integrand at a point.
- **p-test:** `∫₁^∞ x^{−p} dx` converges iff `p > 1` (value `1/(p−1)`); `∫₀^1 x^{−p} dx` converges iff `p < 1` (value `1/(1−p)`). The boundary case `p = 1` diverges **logarithmically** (`ln T` grows without bound but very slowly).
- **Comparison test:** if `0 ≤ f ≤ g` and `∫g` converges then `∫f` converges; if `∫f` diverges then `∫g` diverges.
- **Standard values:** `∫₀^∞ e^{−λx}dx = 1/λ`; `∫_{−∞}^∞ e^{−x²}dx = √π`; `∫₀^∞ x^{s−1}e^{−x}dx = Γ(s)` (`s > 0`).
- **Absolute convergence:** `∫|f| < ∞` implies `∫f` exists. A density's mean `E[X] = ∫x p(x)dx` exists only if `∫|x|p(x)dx < ∞`.
- **Cauchy distribution:** `p(x) = 1/(π(1 + x²))` integrates to 1 but `∫|x|p(x) dx` diverges (like `ln T`), so its **mean is undefined** and the sample mean never settles (contrast with the law of large numbers, Module 11).
- **Heavy tails in practice:** tail exponent decides which moments exist; power-law tails with `p ≤ 2` can have infinite variance `[JUDGEMENT; check the specific distribution]`.
- **Numerical handling:** (1) truncate at `T` and **bound the tail analytically**; (2) change variables to a finite interval, e.g. `x = t/(1 − t)`, `dx = dt/(1−t)²`, `t ∈ [0, 1)`; (3) use a rule that never evaluates the endpoints (midpoint, Gauss–Legendre); (4) for endpoint singularities use `x = u^k` substitutions.
- **Divergence detection:** compute the integral for `T = 10, 100, 1000, …`. A converging integral stabilizes; a diverging one keeps growing (`p = 1` grows like `ln T`; `p < 1` like a power).

### 5.4 Code

```python
import math
import numpy as np

def gauss_legendre(f, a, b, n=200):
    xs, ws = np.polynomial.legendre.leggauss(n)
    t = 0.5 * (b - a) * xs + 0.5 * (a + b)
    return 0.5 * (b - a) * np.sum(ws * f(t))

def panels_gl(f, a, T, n=32):
    """Composite Gauss–Legendre on panels that grow geometrically away from a (never use n in the thousands:
    np.polynomial.legendre.leggauss builds an n×n eigenproblem and becomes very slow)."""
    k = max(2, int(np.ceil(np.log2(T - a + 1))) + 1)
    edges = a + (np.geomspace(1.0, T - a + 1.0, k) - 1.0)
    return sum(gauss_legendre(f, lo, hi, n) for lo, hi in zip(edges[:-1], edges[1:]))

# p-test: ∫_1^T x^{-p} for growing T
for p in (0.5, 1.0, 1.5, 2.0):
    vals = [panels_gl(lambda t: t ** (-p), 1, T) for T in (1e1, 1e2, 1e3, 1e4)]
    print(f"p={p}: ", [round(v, 4) for v in vals], "limit:", (1 / (p - 1) if p > 1 else "diverges"))
# p=1 grows like ln T; p=2 settles at 1; report your own numbers

# map [0, ∞) → [0, 1):  x = t/(1−t),  dx = dt/(1−t)²   (Gauss–Legendre never touches t = 1)
def integrate_0_inf(f, n=300):
    g = lambda t: f(t / (1 - t)) / (1 - t) ** 2
    return gauss_legendre(g, 0.0, 1.0, n)
assert np.isclose(integrate_0_inf(lambda x: np.exp(-x)), 1.0, rtol=1e-9)
assert np.isclose(integrate_0_inf(lambda x: x * np.exp(-x)), 1.0, rtol=1e-8)          # Γ(2)
assert np.isclose(integrate_0_inf(lambda x: np.exp(-x ** 2)), math.sqrt(math.pi) / 2, rtol=1e-8)

# endpoint singularity: ∫_0^1 x^{-1/2} dx = 2  — substitute x = u²
naive = gauss_legendre(lambda x: x ** -0.5, 0, 1, 200)                                # converges slowly (singular endpoint)
sub = gauss_legendre(lambda u: 2.0 * np.ones_like(u), 0, 1, 10)                       # x^{-1/2} · 2u du = 2 du
print(naive, sub)                                                                     # naive is visibly less accurate; sub = 2 exactly

# Cauchy: normalizes, but the mean does not exist
cauchy = lambda x: 1 / (math.pi * (1 + x ** 2))
total = integrate_0_inf(cauchy) * 2                                                   # symmetric → twice the half-line
assert np.isclose(total, 1.0, rtol=1e-8)
for T in (1e1, 1e2, 1e4, 1e8):
    first_abs_moment = 2 * panels_gl(lambda x: x * cauchy(x), 0, T) if T <= 1e4 else 2 * (math.log(1 + T ** 2) / (2 * math.pi))   # beyond 1e4 use the closed form ln(1+T²)/(2π)
    print(T, first_abs_moment)                                                        # grows like ln T: ∫|x|p diverges

# the sample mean of Cauchy draws does not settle (contrast with a normal)
rng = np.random.default_rng(0)
for name, draw in (("normal", rng.normal(size=1_000_000)), ("cauchy", rng.standard_cauchy(size=1_000_000))):
    run = np.cumsum(draw) / np.arange(1, len(draw) + 1)
    print(name, [round(float(run[k - 1]), 3) for k in (10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6)])
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Truncating at a fixed `T` and calling it converged | A divergent integral looks finite | Repeat with larger `T`; plot value vs `log T` |
| Ignoring the tail beyond `T` | Normalization slightly below 1 | Add an analytic tail bound |
| Evaluating the integrand at a singular endpoint | `inf`/`nan` | Endpoint-free rules or a substitution |
| Assuming a density has a mean | Sample mean never stabilizes (Cauchy) | Check `∫|x|p < ∞` |
| `p = 1` mistaken for convergent because growth is slow | `ln T` keeps rising | Use the p-test, not "it looks flat" |
| Reading "not stabilized" as "divergent" (e.g., `x^{−1.5}` has tail `≈ 2/√T`, still drifting at `T = 10⁵`) | A convergent integral is declared divergent | A numerical stability check can only say "not settled"; decide with the p-test or an analytic tail bound |
| Variable change without the Jacobian `1/(1−t)²` | Wrong value | Differentiate the substitution |
| Using `np.inf` as a limit in a plain rule | Garbage or `nan` | Map to a finite interval |
| Oscillatory improper integrals (e.g., `sin x / x`) treated like positive ones | Slow, conditionally convergent | Specialized methods; do not rely on truncation alone |

### 5.6 ML link

- **Moments of heavy-tailed data and gradients:** infinite variance breaks the central limit theorem's usual conclusion and makes averages unreliable (Module 11, Module 12). Gradient noise with heavy tails is an active research topic `[JUDGEMENT]`.
- **Normalization of unbounded densities** (normal, exponential, Gamma) rests on improper integrals (Module 10).
- **KL divergence can be infinite** when supports differ (Module 13).
- **Importance sampling:** the estimator has infinite variance if the weight tails are too heavy (4C-04 Lesson 10).
- **Numerical safety:** `log(0)` and `1/0` in loss code are the discrete shadows of endpoint singularities (Module 05).

### 5.7 Lab (75 min)

1. p-test study: plot `∫₁^T x^{−p}` vs `T` (log axis) for `p ∈ {0.5, 1, 1.5, 2}`; fit growth rates; state which diverge and how.
2. Implement `integrate_0_inf` and verify on four integrals with known values; compare against naive truncation at several `T` (with the tail bound).
3. Endpoint-singularity study: `∫₀^1 x^{−1/2}dx` and `∫₀^1 ln x dx` with a naive rule vs the substitution; plot error vs number of evaluations.
4. Cauchy vs normal running-mean experiment with 20 seeds; show the spread of the final running means for each, and explain the difference.

### Check yourself (Unit 5)

1. For which `p` does `∫₁^∞ x^{−p} dx` converge?
2. Why does the Cauchy distribution have no mean even though its pdf integrates to 1?
3. Why use `x = t/(1 − t)` with Gauss–Legendre?

**Reference answers:** (1) `p > 1`. (2) `∫|x|p(x)dx` diverges (logarithmically), so `E[X]` is undefined. (3) It maps `[0, ∞)` to `[0, 1)` and Gauss–Legendre never evaluates the singular endpoint.

---

## Unit 6 — Numerical integration: Riemann sums and the trapezoid rule (`05-…md`)

### 6.1 Why ML needs this

Most integrals you meet in practice have no closed form: a probability under a custom density, an expected loss, a normalizing constant in one dimension, the area under an ROC curve. Numerical rules turn each into a handful of function evaluations with a known error behaviour.

### 6.2 Mechanics

Split `[a, b]` into `n` intervals of width `h = (b − a)/n`.

| Rule | Formula | Error order (smooth `f`) | Exact for |
|---|---|---|---|
| Left Riemann | `h Σ f(xᵢ)` | `O(h)` | constants |
| Right Riemann | `h Σ f(xᵢ₊₁)` | `O(h)` | constants |
| Midpoint | `h Σ f(mᵢ)` | `O(h²)` | linear |
| Trapezoid | `h[½f₀ + f₁ + … + f_{n−1} + ½f_n]` | `O(h²)` | linear |
| Simpson (`n` even) | `(h/3)[f₀ + 4f₁ + 2f₂ + … + 4f_{n−1} + f_n]` | `O(h⁴)` | cubics |
| Gauss–Legendre (`m` nodes) | `½(b−a) Σ wⱼ f(tⱼ)` | very fast for smooth `f` | degree `2m − 1` |

- **Error scales** as `C hᵖ`: doubling `n` divides the error by `2ᵖ`. Measure `p` from the slope of a log-log plot of error vs `h`.
- **Trapezoid error term:** `−(b−a)h² f″(ξ)/12`: it is **exact for linear** `f` and biased low (high) for convex (concave) `f`.
- **Richardson/Romberg idea:** combine rules at `h` and `h/2` to cancel the leading error term (Simpson is the first step from trapezoid) `[VERIFY]`.
- **Adaptive methods** refine only where the integrand is difficult; the cost is measured in function evaluations.
- **Rule choice:** smooth integrands → Gauss–Legendre or Simpson; data given only as samples on a grid → trapezoid; kinks or jumps → split the interval at the non-smooth point (otherwise Simpson falls from `O(h⁴)` to about `O(h²)` at a kink, and every rule falls to `O(h)` at a jump discontinuity); oscillatory/peaked → refine locally.
- **A testing trap:** on `∫₀^π sin x dx` the integrand vanishes at both endpoints, so left and right Riemann sums coincide with the trapezoid rule and appear second-order. Use `∫₀^{π/2} sin x dx` (or any integrand with unequal endpoint values) when measuring the order of the one-sided rules.
- **Round-off:** summing many terms of the same sign is stable; the practical limit is truncation, not round-off, for moderate `n` (use `np.sum`'s pairwise summation, and `math.fsum` for audits `[VERIFY]`).
- **Monte Carlo integration (preview, Module 11):** `∫ₐᵇ f ≈ (b−a)·mean(f(Uᵢ))` with error `O(1/√N)` that **does not depend on dimension**, unlike grid rules (Lesson 6).
- **ROC-AUC as an integral:** `AUC = ∫₀¹ TPR d(FPR)`. With an empirical ROC curve the trapezoid rule is *exact* for that piecewise-linear curve, and equals the probability that a random positive outscores a random negative (ties counting ½): the Mann–Whitney identity.

**Worked example:** `∫₀^π sin x dx = 2`. With `n = 4` the trapezoid rule gives `(π/4)[0 + 0.7071 + 1 + 0.7071 + 0] ≈ 1.896`; error `≈ 0.104`. Doubling `n` to 8 gives error `≈ 0.026` (a factor ≈ 4: second order).

### 6.3 Code

```python
import numpy as np

def left_riemann(f, a, b, n):
    x = np.linspace(a, b, n + 1); return (b - a) / n * np.sum(f(x[:-1]))
def right_riemann(f, a, b, n):
    x = np.linspace(a, b, n + 1); return (b - a) / n * np.sum(f(x[1:]))
def midpoint(f, a, b, n):
    x = np.linspace(a, b, n + 1); return (b - a) / n * np.sum(f((x[:-1] + x[1:]) / 2))
def trapezoid(f, a, b, n):
    x = np.linspace(a, b, n + 1); y = f(x); return (b - a) / n * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2)
def simpson(f, a, b, n):
    if n % 2: raise ValueError("Simpson's rule needs an even number of intervals")
    x = np.linspace(a, b, n + 1); y = f(x)
    return (b - a) / n / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
def gauss_legendre(f, a, b, n):
    xs, ws = np.polynomial.legendre.leggauss(n)
    t = 0.5 * (b - a) * xs + 0.5 * (a + b); return 0.5 * (b - a) * np.sum(ws * f(t))

RULES = {"left": left_riemann, "right": right_riemann, "midpoint": midpoint, "trapezoid": trapezoid, "simpson": simpson}

# convergence orders on a smooth integral: ∫_0^{π/2} sin = 1  (f(0)=0 but f(π/2)=1: endpoint values differ)
exact = 1.0
ns = np.array([4, 8, 16, 32, 64, 128, 256])
for name, rule in RULES.items():
    err = np.array([abs(rule(np.sin, 0, np.pi / 2, n) - exact) for n in ns])
    slope = np.polyfit(np.log(np.pi / 2 / ns), np.log(err), 1)[0]
    print(f"{name:10s} fitted order ≈ {slope:.2f}")                        # ≈ 1, 1, 2, 2, 4
for m in (2, 4, 6, 8):
    print("gauss", m, abs(gauss_legendre(np.sin, 0, np.pi / 2, m) - exact))    # drops extremely fast

# trap: on ∫_0^π sin the endpoint values are both 0, so left/right Riemann coincide with the trapezoid rule
# and show order 2, not 1. Always test a rule on an integrand that does not hide its weakness.
for name in ("left", "right", "trapezoid"):
    err = np.array([abs(RULES[name](np.sin, 0, np.pi, n) - 2.0) for n in ns])
    print(name, "on [0, π]: fitted order ≈", round(float(np.polyfit(np.log(np.pi / ns), np.log(err), 1)[0]), 2))

# exactness checks
assert np.isclose(trapezoid(lambda t: 3 * t + 2, 0, 5, 1), 3 * 25 / 2 + 10)             # linear: exact with n=1
assert np.isclose(simpson(lambda t: t ** 3 - t, 0, 2, 2), 4 - 2)                         # cubic: exact with n=2
assert np.isclose(gauss_legendre(lambda t: t ** 7, 0, 1, 4), 1 / 8)                      # degree 2m−1 = 7 exact

# a kink hurts: |x−0.3| on [0,1]. Simpson falls from order 4 to about 2 unless we split at the kink.
# (Do not put the kink at 1/3: with power-of-two grids Simpson's error happens to cancel there, hiding the effect.)
g = lambda t: np.abs(t - 0.3); exact_g = 0.3 ** 2 / 2 + 0.7 ** 2 / 2
errs = [abs(simpson(g, 0, 1, n) - exact_g) for n in (16, 32, 64, 128, 256)]
print("Simpson, kink inside:", errs, "fitted order ≈", round(float(np.polyfit(np.log(1 / np.array([16, 32, 64, 128, 256])), np.log(errs), 1)[0]), 2))
print("split at the kink:", abs(simpson(g, 0, 0.3, 32) + simpson(g, 0.3, 1, 32) - exact_g))   # ~1e-16

# ROC-AUC: trapezoid area under the empirical ROC equals the pairwise (Mann–Whitney) formula
def roc_auc_trapezoid(y, s):
    order = np.argsort(-s, kind="stable"); y, s = y[order], s[order]
    tps, fps = np.cumsum(y), np.cumsum(1 - y)
    idx = np.r_[np.where(np.diff(s))[0], len(s) - 1]                     # last index of each distinct score (handles ties)
    tpr = np.r_[0.0, tps[idx] / tps[-1]]; fpr = np.r_[0.0, fps[idx] / fps[-1]]
    return float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2))
def auc_pairs(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return float((pos[:, None] > neg[None]).mean() + 0.5 * (pos[:, None] == neg[None]).mean())
rng = np.random.default_rng(0)
y = rng.integers(0, 2, 400); s = np.round(rng.normal(size=400) + 1.2 * y, 1)        # rounding creates ties
assert np.isclose(roc_auc_trapezoid(y, s), auc_pairs(y, s))
```

### 6.4 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Choosing `n` by guesswork | Unknown error | Convergence check: compare `n` and `2n`; report the difference |
| Simpson with odd `n` | Wrong result or error | Enforce even `n` |
| Integrating across a kink or jump with a high-order rule | Simpson drops to ~`O(h²)` at a kink; all rules drop to `O(h)` at a jump | Split at the non-smooth point |
| Using a grid rule on a narrow peak with a coarse grid | Peak missed entirely | Plot the integrand; refine or use adaptive |
| Comparing methods by `n` instead of function evaluations | Misleading cost comparison | Count evaluations (Simpson needs `n+1`; Gauss needs `m`) |
| Trapezoid on noisy sampled data and treating the result as exact | Noise passes into the answer | State uncertainty; smooth first if justified |
| Ties ignored when computing AUC | Wrong value | Evaluate ROC only at distinct thresholds (as above) |
| `np.trapz`/`np.trapezoid` name mismatch across NumPy versions | `AttributeError` or deprecation warning | Own implementation or a version check |
| Infinite limits passed to a finite rule | `nan` | Lesson 4 transformation |

### 6.5 ML link

- **Probabilities and expectations under custom densities** (Module 09, 10, 12).
- **ROC-AUC / PR-AUC** are areas (Stage 5A-06); the trapezoid rule is exact for the empirical ROC, while PR-AUC by the trapezoid rule is known to be optimistic `[VERIFY: interpolation issue for PR curves]`.
- **Monte Carlo** replaces grids when dimension grows (Module 11, 4C-04).
- **Numerical normalization of an unnormalized 1-D density** (e.g., a custom prior): integrate on a grid, divide.
- **Cumulative metrics** (e.g., cumulative gain curves) are running integrals.

### 6.6 Lab (90 min)

1. Implement all six rules; reproduce the convergence-order table on three integrands (smooth `sin` on `[0, π/2]`, `e^{−x²}`, and a kinked `|x − 0.3|`); explain the differences in orders, and reproduce the vanishing-endpoint trap on `[0, π]`.
2. Plot error vs number of function evaluations (log-log) for each rule on a smooth integral; identify the most efficient rule and explain why Gauss–Legendre wins here and when it would not.
3. Verify the exactness claims (linear/cubic/degree `2m−1`).
4. Normalize a 1-D unnormalized density `exp(−x⁴ + x²)` numerically; compute its mean and variance; check with a finer grid.
5. AUC: compute ROC-AUC for three synthetic classifiers with and without ties; verify the trapezoid-vs-pairs identity; compare with any library routine you have installed `[VERIFY: optional]`.

### Check yourself (Unit 6)

1. If the trapezoid error is `O(h²)`, what happens to the error when you double `n`?
2. For which polynomials is Simpson's rule exact?
3. Why is the trapezoid rule exact for the empirical ROC area?

**Reference answers:** (1) It drops by about a factor of 4. (2) Polynomials of degree up to 3. (3) The empirical ROC is piecewise linear, and the trapezoid rule integrates piecewise-linear functions exactly.

---

## Unit 7 — Double integrals: introduction (`06-…md`)

### 7.1 Why ML needs this

Joint densities of two variables, marginalization (`p(x) = ∫ p(x, y) dy`), 2-D normalization, and expectations of functions of two variables are all double integrals. The same ideas, with more variables, are the integrals behind latent-variable models (4C-10). Seeing exactly why grids become hopeless as dimension grows motivates Monte Carlo (Module 11).

### 7.2 Intuition

A single integral adds up thin strips under a curve; a **double integral** adds up thin columns under a surface `z = f(x, y)`: the signed **volume** over a region `R`. Integrate in one variable at a time (**iterated integral**).

### 7.3 Mechanics

- **Over a rectangle:** `∬_R f dA = ∫ₐᵇ ( ∫_c^d f(x, y) dy ) dx`.
- **Fubini's theorem:** for well-behaved (e.g., continuous or absolutely integrable) `f`, the order of integration can be swapped.
- **General regions:** limits of the inner integral may depend on the outer variable, e.g. a triangle `0 ≤ y ≤ x ≤ 1`: `∫₀^1 ∫₀^x f dy dx`.
- **Separable integrands:** if `f(x, y) = g(x) h(y)` over a rectangle, then `∬ f = (∫g)(∫h)`; this is the integral form of **independence** (Module 09).
- **Polar coordinates:** `x = r cos θ`, `y = r sin θ`, `dA = r dr dθ`. Key result: `(∫_{−∞}^{∞} e^{−x²}dx)² = ∬ e^{−(x²+y²)} dA = ∫₀^{2π}∫₀^∞ e^{−r²} r dr dθ = π`, hence `∫e^{−x²}dx = √π` (this gives the Gaussian normalization used in Lessons 3 and 4).
- **Joint density:** `p(x, y) ≥ 0`, `∬ p = 1`; **marginal** `p_X(x) = ∫ p(x, y) dy`; `P((X, Y) ∈ R) = ∬_R p`; `E[g(X, Y)] = ∬ g p`.
- **Bivariate normal with correlation `ρ`:** `p(x, y) = exp(−(x² − 2ρxy + y²)/(2(1−ρ²))) / (2π√(1−ρ²))`; its marginals are standard normal (check numerically).
- **Numerical double integrals:** tensor-product rules (apply a 1-D rule in each direction: cost `Nᵈ` for `d` dimensions); Monte Carlo (cost independent of `d`, error `O(1/√N)`).
- **Curse of dimensionality for grids (Module 04 Lesson 3):** `N = 100` points per axis in `d = 10` needs `10²⁰` evaluations. Monte Carlo and quasi-Monte Carlo are the practical alternatives.
- **Monte Carlo estimate with an error bar:** `Î = V·mean(f(Uᵢ))`, standard error `V·std(f)/√N` (for uniform sampling over a region of volume `V`).

**Worked example:** `∬ over [0,1]² of xy dA = (∫₀^1 x dx)(∫₀^1 y dy) = ½·½ = ¼`. Probability that a uniform point in `[−1, 1]²` lies in the unit disc: `π/4` (area ratio), estimated by Monte Carlo in the lab.

### 7.4 Code

```python
import math
import numpy as np

def gl_nodes(a, b, n):
    xs, ws = np.polynomial.legendre.leggauss(n)
    return 0.5 * (b - a) * xs + 0.5 * (a + b), 0.5 * (b - a) * ws

def double_integral(f, ax, bx, ay, by, nx=64, ny=64):
    """Tensor-product Gauss–Legendre over a rectangle. f(X, Y) must accept 2-D arrays."""
    x, wx = gl_nodes(ax, bx, nx); y, wy = gl_nodes(ay, by, ny)
    X, Y = np.meshgrid(x, y, indexing="ij")
    return float(wx @ f(X, Y) @ wy)

# separable integrand = product of 1-D integrals
assert np.isclose(double_integral(lambda X, Y: X * Y, 0, 1, 0, 1), 0.25)

# Fubini: swapping the order gives the same answer
f2 = lambda X, Y: np.exp(-X * Y) * np.sin(X + Y)
a = double_integral(f2, 0, 2, 0, 3)
b = double_integral(lambda Y, X: f2(X, Y), 0, 3, 0, 2)                    # roles swapped
assert np.isclose(a, b, rtol=1e-12)

# non-rectangular region (triangle 0 ≤ y ≤ x ≤ 1) by an inner variable-limit integral
def triangle_integral(f, n=64):
    x, wx = gl_nodes(0, 1, n); total = 0.0
    for xi, wi in zip(x, wx):
        y, wy = gl_nodes(0, xi, n); total += wi * np.sum(wy * f(xi, y))
    return total
assert np.isclose(triangle_integral(lambda x, y: x * y), 1 / 8)           # ∫_0^1 x · x²/2 dx

# Gaussian integral: Cartesian vs polar
cart = double_integral(lambda X, Y: np.exp(-(X ** 2 + Y ** 2)), -8, 8, -8, 8, 200, 200)
r, wr = gl_nodes(0, 8, 200)
polar = 2 * math.pi * float(np.sum(wr * np.exp(-r ** 2) * r))
assert np.isclose(cart, math.pi, rtol=1e-10) and np.isclose(polar, math.pi, rtol=1e-10)
assert np.isclose(math.sqrt(cart), math.sqrt(math.pi))                   # ∫e^{-x²}dx = √π

# bivariate normal: normalization and marginalization
rho = 0.6
pxy = lambda X, Y: np.exp(-(X ** 2 - 2 * rho * X * Y + Y ** 2) / (2 * (1 - rho ** 2))) / (2 * math.pi * math.sqrt(1 - rho ** 2))
assert np.isclose(double_integral(pxy, -8, 8, -8, 8, 200, 200), 1.0, rtol=1e-9)
y, wy = gl_nodes(-8, 8, 200)
for x0 in (-1.0, 0.0, 1.5):
    marginal = float(np.sum(wy * pxy(np.full_like(y, x0), y)))
    assert np.isclose(marginal, math.exp(-x0 ** 2 / 2) / math.sqrt(2 * math.pi), rtol=1e-9)   # N(0,1) pdf
# expectation of g(X,Y) = XY equals the correlation
EXY = double_integral(lambda X, Y: X * Y * pxy(X, Y), -8, 8, -8, 8, 200, 200)
assert np.isclose(EXY, rho, rtol=1e-8)

# Monte Carlo: P(point in unit disc) for uniform on [-1,1]², with a standard error
rng = np.random.default_rng(0); N = 400_000
P = rng.uniform(-1, 1, size=(N, 2)); inside = (P[:, 0] ** 2 + P[:, 1] ** 2 <= 1).astype(float)
est, se = inside.mean(), inside.std(ddof=1) / math.sqrt(N)
print(f"MC {est:.4f} ± {se:.4f}  vs π/4 = {math.pi / 4:.4f}")
assert abs(est - math.pi / 4) < 4 * se

# grid cost grows exponentially with dimension
for d in (1, 2, 3, 6, 10): print(f"d={d:2d}  grid evaluations with 100 points/axis: {100 ** d:.1e}")
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Forgetting the Jacobian `r` in polar coordinates | Off by a factor / wrong integral | `dA = r dr dθ` |
| Swapping order on a non-rectangular region without re-deriving limits | Wrong region | Sketch the region; rewrite limits |
| Assuming Fubini on a non-absolutely-integrable function | Orders disagree | Check absolute integrability |
| Truncating infinite domains too tightly in 2-D | Missing mass; normalization < 1 | Check the tail; verify `∬ p ≈ 1` |
| Using a coarse tensor grid on a sharply peaked or correlated density (e.g., `ρ → 1`) | Poor accuracy | Rotate/whiten coordinates or refine |
| Passing 1-D arrays where `meshgrid` shapes are expected | Broadcasting bugs | Use `indexing="ij"` consistently; assert shapes |
| Monte Carlo reported without a standard error | Unverifiable claim | Always report `± se` and `N` |
| Using a grid in `d ≥ 4` | Impossible cost | Monte Carlo or structure-exploiting methods |
| Treating samples as independent when the sampler is correlated (MCMC) | Understated error | Effective sample size (4C-04) |

### 7.6 ML link

- **Joint and marginal densities** (Module 09, 10; 4C-04): marginalization is integration.
- **Bayesian inference:** the evidence `p(D) = ∫ p(D|θ)p(θ) dθ` is a (usually high-dimensional) integral; approximations are variational inference and MCMC (4C-05).
- **Latent-variable models** (VAE, 4C-10): the marginal likelihood is `∫ p(x|z)p(z) dz`.
- **Independence = factorization** of the joint density (Module 09).
- **Monte Carlo** is the default numerical integrator beyond a few dimensions (Module 11).

### 7.7 Lab (90 min)

1. Verify Fubini on three integrands; draw the region for a triangle and a disc and set up limits both ways.
2. Reproduce the Cartesian and polar Gaussian integrals; plot error vs grid size for the Cartesian one.
3. Bivariate normal lab: verify normalization, marginals, `E[XY] = ρ`, and `P(X > 0, Y > 0) = ¼ + arcsin(ρ)/(2π)` numerically for `ρ ∈ {0, 0.5, 0.9}`.
4. Monte Carlo vs grid: estimate the volume of the unit ball in `d ∈ {2, 3, 5, 8, 12}` by Monte Carlo; compare with the closed form from Module 04 (via `math.lgamma`); show that the grid cost explodes while the MC error stays about `1/√N`.
5. Estimate a 2-D integral with a known answer at three sample sizes and verify the standard error scales as `1/√N`.

### Check yourself (Unit 7)

1. What is `dA` in polar coordinates?
2. Why does `∬ g(x)h(y) dA` over a rectangle factor?
3. Why can't you use a 100-points-per-axis grid in 10 dimensions?

**Reference answers:** (1) `r dr dθ`. (2) The inner integral does not depend on the outer variable, so the iterated integral is a product of two single integrals. (3) It needs `100¹⁰ = 10²⁰` function evaluations.

---

## Unit 8 — Practice question bank (`practice-questions.md`)

### 8.1 Structure

About 40 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 10 per tier, each with a hidden answer and a one-line rationale. Mix hand integration (kept short), "predict the value/convergence", runnable code, and ML judgement.

### 8.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 8.3 Seed items

**Q1 [L1] Constant.** Why does the indefinite integral include `+ C`? → Antiderivatives differ by constants since constants have zero derivative.
**Q2 [L2] Antiderivative.** `∫ (4x³ − 1/x + eˣ) dx`? → `x⁴ − ln|x| + eˣ + C`.
**Q3 [L2] FTC.** `∫₀² 3x² dx`? → `[x³]₀² = 8`.
**Q4 [L2] Substitution.** `∫₀^1 3x² cos(x³) dx`? → `u = x³`: `sin(1) ≈ 0.8415`.
**Q5 [L2] Parts.** `∫ x ln x dx`? → `(x²/2) ln x − x²/4 + C`.
**Q6 [L2] Improper.** `∫₁^∞ x^{−3} dx`? → `½`.
**Q7 [L2] Probability.** `X ~ Exp(λ = 2)`; `P(X > 1)`? → `e^{−2} ≈ 0.1353`.
**Q8 [L2] Error order.** Trapezoid with `n = 50` has error `4e-4`. Estimate the error at `n = 100`. → About `1e-4`.
**Q9 [L2] Mean value.** Average of `x²` on `[0, 3]`? → `(1/3)(9) = 3`.
**Q10 [L3] Debug.** Your numerical CDF ends at `0.9987`, not `1`. List likely causes. → Truncated tail; too-coarse grid near the peak; endpoint treatment in `cumtrapz`. Check by extending the range and refining.
**Q11 [L3] Debug.** Simpson's rule gives a wrong answer for `n = 25`. → Needs even `n`.
**Q12 [L3] Debug.** Simpson's rule on `|x − 0.3|` over `[0,1]` converges at only about `O(h²)`, not `O(h⁴)`. → The kink breaks the smoothness assumption; split the interval at `x = 0.3`.
**Q13 [L3] Analysis.** The sample mean of 10⁶ Cauchy draws is 17.4 and 10⁷ draws gives −3.1. Why? → No mean exists; the law of large numbers does not apply.
**Q14 [L3] Analysis.** `∫₀^1 x^{−1} dx` computed with a midpoint rule seems to converge to ~7 for `n = 1000`. Is it convergent? → No, it diverges logarithmically; the number is an artefact of the discretization and grows with `n`.
**Q15 [L4] Design.** Choose a method to compute `E[f(X)]` for a smooth density on `ℝ`. → Map to a finite range or truncate with a tail bound; use Gauss–Legendre/Simpson with a convergence check; if `f` or the density is not smooth, split intervals or use Monte Carlo.
**Q16 [L4] Design.** You need a normalizing constant for an unnormalized 6-D density. → Grids are infeasible (`N⁶`); use Monte Carlo/importance sampling or MCMC, report the standard error and effective sample size.
**Q17 [L4] Design.** You want to report ROC-AUC confidently. → Compute via the pairwise identity or trapezoid on distinct thresholds, handle ties, and add a bootstrap confidence interval (Module 12).

### 8.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Antiderivatives | 2 | 2 | 1 | 0 |
| Definite integrals, FTC | 2 | 3 | 2 | 1 |
| Substitution and parts | 1 | 3 | 1 | 0 |
| Improper integrals | 2 | 2 | 3 | 1 |
| Numerical integration | 2 | 3 | 3 | 3 |
| Double integrals | 1 | 2 | 1 | 2 |

### Check yourself (Unit 8)

1. Why include a "divergent but looks convergent numerically" item (Q14)?
2. Which items need runnable code?

**Reference answers:** (1) Slowly diverging integrals (log growth) are the classic way numerics mislead. (2) All L3 items and any whose answer depends on floating-point or sampling behaviour.

---

## Unit 9 — Project index (`Projects/README.md`)

### 9.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Numerical integration toolkit | Correct rules, measured convergence orders, honest cost accounting, improper/2-D support | 3–7 | 6–7 h |
| 2 | Area under a density curve lab | Probabilities, CDFs, quantiles, moments, AUC from integration; heavy-tail awareness | 2, 4–6 | 5–6 h |

Order: 1 → 2 (Project 2 reuses the toolkit's rules). Outputs feed `mlmath/integrate.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D7) and notebook `06_integrals.ipynb`.

### 9.2 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs known integrals / SymPy / closed forms | 30 |
| Failure-mode handling (kinks, singularities, infinite ranges, odd `n`, heavy tails) | 15 |
| Reproducibility (seeded, pinned, clean venv; no downloads) | 15 |
| Explanation quality (what each plot shows and why it matters for ML) | 15 |
| Code quality (types, docstrings, evaluation counting) | 15 |
| ML connection paragraph | 10 |

### 9.3 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 9)

1. What does Project 2 reuse from Project 1?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The integration rules, `cumtrapz`, and the improper-integral transformation. (2) D7 (`mlmath/integrate.py`).

---

## Unit 10 — Project: Numerical integration toolkit (`Projects/01-…md`)

### 10.1 Brief

Build `integkit`: a small library of 1-D and 2-D numerical integrators with error estimates, evaluation counting, adaptive refinement, and support for improper integrals and Monte Carlo, plus a systematic convergence study.

**Industry framing:** any team that computes probabilities or normalizers numerically wants a tested integrator that reports *how many evaluations it spent and how sure it is*. A bare number without an error estimate is not a result.

### 10.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Fixed rules | left, right, midpoint, trapezoid, Simpson, Gauss–Legendre; vectorized; clear `ValueError` for bad `n`, `a == b`, non-finite limits |
| R2 | Evaluation counting | Wrap `f` in a counter; every result returns `(value, n_evals)` |
| R3 | Error estimation | `integrate(f, a, b, rule, tol)` doubles `n` until `|I_{2n} − I_n| < tol` (for Simpson/trapezoid use the Richardson-style error estimate; document it); returns value, estimated error, evaluations |
| R4 | Adaptive Simpson | Recursive with a depth limit, tolerance splitting, and an evaluation budget; compare against the fixed rule on a peaked integrand |
| R5 | Improper integrals | `[a, ∞)`, `(−∞, b]`, `(−∞, ∞)` via variable change; endpoint-singular integrands via `x = a + u^k`; detection of divergence (value not stabilizing across `T`) |
| R6 | Monte Carlo | Plain MC with a standard error; seeded; optional antithetic/stratified variance reduction |
| R7 | 2-D integrator | Tensor-product Gauss–Legendre on rectangles; triangle/disc via inner limits or polar coordinates; MC alternative |
| R8 | Convergence study | Error-vs-`n` and error-vs-evaluations plots with fitted orders for ≥ 6 integrands: smooth, oscillatory, kinked, peaked, endpoint-singular, infinite range |
| R9 | Property tests | Exactness (linear/cubic/degree `2m−1`), linearity, additivity, reversal, scaling `∫f(ct)dt`; run on random polynomials |
| R10 | Report | `REPORT.md` with a decision table ("which rule for which integrand") backed by the measured study |

### 10.3 Layout and starter

```
integkit/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/integkit/{__init__,rules,counting,adaptive,improper,montecarlo,multi}.py
├── tests/{test_rules,test_adaptive,test_improper,test_montecarlo,test_multi,test_properties}.py
├── notebooks/06_integration_toolkit.ipynb
└── results/
```

```python
# src/integkit/counting.py
import numpy as np

class Counted:
    """Wrap a vectorized f and count how many points it is evaluated at."""
    def __init__(self, f): self.f, self.n = f, 0
    def __call__(self, x):
        x = np.asarray(x, dtype=float); self.n += x.size
        return self.f(x)
```

```python
# src/integkit/rules.py
import numpy as np
from .counting import Counted

def _check(a, b, n):
    if not (np.isfinite(a) and np.isfinite(b)):
        raise ValueError("finite limits required (use integkit.improper for infinite ranges)")
    if n < 1 or int(n) != n:
        raise ValueError("n must be a positive integer")

def trapezoid(f, a, b, n):
    _check(a, b, n); x = np.linspace(a, b, n + 1); y = f(x)
    return (b - a) / n * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2)

def simpson(f, a, b, n):
    _check(a, b, n)
    if n % 2: raise ValueError("Simpson's rule needs an even n")
    x = np.linspace(a, b, n + 1); y = f(x)
    return (b - a) / n / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())

def gauss_legendre(f, a, b, n):
    _check(a, b, n); xs, ws = np.polynomial.legendre.leggauss(int(n))
    t = 0.5 * (b - a) * xs + 0.5 * (a + b); return 0.5 * (b - a) * np.sum(ws * f(t))

def integrate(f, a, b, rule=simpson, tol=1e-10, n0=8, max_doublings=20):
    """Double n until successive estimates agree. Returns (value, est_error, n_evals)."""
    c = Counted(f); n, prev = n0 + (n0 % 2), rule(c, a, b, n0 + (n0 % 2))
    for _ in range(max_doublings):
        n *= 2; cur = rule(c, a, b, n)
        err = abs(cur - prev)
        if err < tol * max(1.0, abs(cur)):
            return float(cur), float(err), c.n
        prev = cur
    raise RuntimeError(f"no convergence to tol={tol:g} after {max_doublings} doublings (last diff {err:.2e})")
```

```python
# src/integkit/adaptive.py
import numpy as np

def adaptive_simpson(f, a, b, tol=1e-10, max_depth=40, budget=200_000):
    evals = [0]
    def F(x): evals[0] += 1; return float(f(np.array([x]))[0])
    def S(fa, fm, fb, a, b): return (b - a) / 6 * (fa + 4 * fm + fb)
    def rec(a, b, fa, fm, fb, whole, tol, depth):
        m = (a + b) / 2; lm, rm = (a + m) / 2, (m + b) / 2
        flm, frm = F(lm), F(rm)
        left, right = S(fa, flm, fm, a, m), S(fm, frm, fb, m, b)
        delta = left + right - whole
        if depth >= max_depth or evals[0] > budget:
            return left + right
        if abs(delta) <= 15 * tol:
            return left + right + delta / 15           # Richardson correction
        return rec(a, m, fa, flm, fm, left, tol / 2, depth + 1) + rec(m, b, fm, frm, fb, right, tol / 2, depth + 1)
    fa, fb, fm = F(a), F(b), F((a + b) / 2)
    val = rec(a, b, fa, fm, fb, S(fa, fm, fb, a, b), tol, 0)
    return val, evals[0]
```

```python
# src/integkit/improper.py
import numpy as np
from .rules import gauss_legendre

def int_0_inf(f, n=300):
    g = lambda t: f(t / (1 - t)) / (1 - t) ** 2          # x = t/(1−t), dx = dt/(1−t)²
    return gauss_legendre(g, 0.0, 1.0, n)

def int_a_inf(f, a, n=300):   return int_0_inf(lambda x: f(x + a), n)
def int_neg_inf_b(f, b, n=300): return int_0_inf(lambda x: f(b - x), n)
def int_real_line(f, n=300):  return int_0_inf(f, n) + int_0_inf(lambda x: f(-x), n)

def _panels(f, a, T, n=32):
    # composite Gauss–Legendre on geometrically growing panels (a large single leggauss(n) is very slow)
    k = max(2, int(np.ceil(np.log2(T - a + 1))) + 1)
    edges = a + (np.geomspace(1.0, T - a + 1.0, k) - 1.0)
    return sum(gauss_legendre(f, lo, hi, n) for lo, hi in zip(edges[:-1], edges[1:]))

def detect_divergence(f, a, Ts=(1e1, 1e2, 1e3, 1e4, 1e5), rtol=1e-3):
    vals = [_panels(f, a, T) for T in Ts]
    stable = abs(vals[-1] - vals[-2]) <= rtol * max(1.0, abs(vals[-1]))
    return stable, vals
```

```python
# tests/test_rules.py
import numpy as np, pytest
from integkit.rules import trapezoid, simpson, gauss_legendre, integrate

def test_exactness():
    assert np.isclose(trapezoid(lambda t: 3 * t + 2, 0, 5, 1), 3 * 25 / 2 + 10)
    assert np.isclose(simpson(lambda t: t ** 3 - t, 0, 2, 2), 2.0)
    assert np.isclose(gauss_legendre(lambda t: t ** 7, 0, 1, 4), 1 / 8)

def test_convergence_orders():
    ns = np.array([8, 16, 32, 64, 128]); h = np.pi / ns
    for rule, order in ((trapezoid, 2), (simpson, 4)):
        err = np.array([abs(rule(np.sin, 0, np.pi, n) - 2.0) for n in ns])
        assert abs(np.polyfit(np.log(h), np.log(err), 1)[0] - order) < 0.3

def test_bad_inputs():
    with pytest.raises(ValueError): simpson(np.sin, 0, 1, 7)
    with pytest.raises(ValueError): trapezoid(np.sin, 0, np.inf, 10)

def test_integrate_reports_error_and_evals():
    v, err, n = integrate(np.sin, 0, np.pi)
    assert abs(v - 2.0) < 1e-9 and err < 1e-9 and n > 0
```

### 10.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Exactness and order tests pass; every call reports evaluations; bad input raises `ValueError` |
| M2 | R4 | Adaptive Simpson beats the fixed rule in evaluations (to equal tolerance) on a peaked integrand, and the study states by how much *from your run* |
| M3 | R5 | Four improper integrals with known values to `1e-8`; `detect_divergence` reports "not stabilized" for `∫₁^∞ 1/x` and "stable" for `∫₁^∞ 1/x²`. It also reports "not stabilized" for the **convergent** `∫₁^∞ x^{−1.5}` on the default `T` grid (tail ≈ `2/√T`): explain why, and why the p-test or an analytic tail bound is needed to *decide* convergence |
| M4 | R6–R7 | MC estimates lie within `4·se` of the truth in ≥ 95% of 200 seeded repeats; 2-D integrals match closed forms (`xy` on `[0,1]²`, Gaussian over `ℝ²`, triangle) |
| M5 | R8–R9 | Convergence plots with fitted slopes; property tests pass on 100 random polynomials |
| M6 | R10 | `REPORT.md` decision table, every row citing a plot/table from your runs |

### 10.5 Statistical-honesty requirements

- Every number states the rule, `n`, number of evaluations, and estimated error.
- Monte Carlo results report `± se` and `N`, and the coverage check in M4 is shown, not asserted.
- Include one case where the toolkit **fails or is slow** (a kink without splitting, an oscillatory integrand, or a near-singular endpoint) and analyse why.

### 10.6 Failure modes to demonstrate

Odd `n` in Simpson; kink without splitting; endpoint singularity with a rule that evaluates the endpoint; infinite limit passed to a finite rule; divergent integral that "looks" convergent for a single `T`; tolerance too tight for `float64` (stagnation near `1e-15`); a peaked integrand missed by a coarse fixed grid; adaptive recursion hitting its depth/budget limit (must report, not silently return).

### 10.7 Stretch goals

1. Romberg integration (Richardson on trapezoid) and its convergence table.
2. Tanh–sinh (double-exponential) quadrature for endpoint singularities `[VERIFY: formula]`.
3. Quasi-Monte Carlo (Sobol/Halton, implemented or imported if available) vs plain MC error in dimensions 2–8 `[VERIFY: library availability]`.
4. Gauss–Hermite rule for `∫ f(x) e^{−x²}dx` and its use for Gaussian expectations (`numpy.polynomial.hermite.hermgauss`).
5. `hypothesis` property tests for linearity and the change-of-variable rule.

### 10.8 ML connection (README prompt)

Describe when you would use each tool in an ML setting: a 1-D normalizing constant, an expected loss over a Gaussian input noise (Gauss–Hermite vs MC), an ROC area, and a 10-D marginal likelihood, and what evidence (error estimate/evaluation count) you would report.

### Check yourself (Unit 10)

1. Why must every integrator return its evaluation count?
2. Why include a case where the toolkit fails?

**Reference answers:** (1) Cost is half the trade-off; comparing rules at equal accuracy requires equal-evaluation accounting. (2) Knowing a tool's failure region is what makes it safe to use; hiding it produces overconfident results.

---

## Unit 11 — Project: Area under a density curve lab (`Projects/02-…md`)

### 11.1 Brief

Build `densitylab`: a lab that treats probability distributions as functions to be integrated. Verify normalization, build CDFs by running integrals, compute probabilities and quantiles, compute moments by integration and compare them to closed forms, study heavy tails, and relate AUC to area.

**Industry framing:** teams routinely need a probability, a quantile, or a tail risk from a density that has no library function (a custom prior, a mixture, an empirical density). The lab builds the numerical machinery and, just as important, the habit of verifying it against known cases.

### 11.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Density library | Normal, exponential, uniform, triangular, Beta(a,b), Cauchy, a Gaussian mixture, and a user-supplied unnormalized density; each with support, closed-form CDF/moments where they exist |
| R2 | Normalization check | `∫p ≈ 1` with a stated tolerance; normalize an unnormalized density numerically and report the constant |
| R3 | CDF by running integral | `cumtrapz` or higher-order running integral on an adaptive grid concentrating points near the mass; max error vs closed form |
| R4 | Probabilities | `P(a < X < b)` from the numerical CDF and by direct integration; tail probabilities; the 68–95–99.7 rule for the normal to 6 digits |
| R5 | Quantiles | Inverse CDF by monotone interpolation and by bisection/root-finding on the CDF; round-trip test `cdf(quantile(q)) ≈ q`; link to inverse-transform sampling |
| R6 | Moments by integration | Mean, variance, skewness, entropy `−∫p ln p`; compare to closed forms; handle improper limits |
| R7 | Sampling cross-check | Draw samples (inverse transform from your CDF); compare histogram to the pdf and the empirical CDF to your CDF (max gap = the Kolmogorov–Smirnov statistic) |
| R8 | Heavy-tail study | Cauchy and Student-t-like densities: show `∫p = 1`, a diverging first absolute moment for Cauchy, running-mean instability, and how truncation changes the answers |
| R9 | KL divergence by integration | `KL(N(μ₁,σ₁²) ‖ N(μ₂,σ₂²))` numerically vs closed form; show an infinite-KL case with mismatched support; preview of Module 13 |
| R10 | AUC as area | ROC-AUC for synthetic Gaussian classes: numerical area under the **theoretical** ROC (from the two densities) vs the empirical AUC from samples vs the closed form `Φ(Δμ/√(σ₁²+σ₂²))` for equal-shape Gaussians |
| R11 | Report | `REPORT.md` with every figure/table seeded and every claim tied to a measured number |

### 11.3 Layout and starter

```
densitylab/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/densitylab/{__init__,densities,cdf,moments,quantile,tails,divergence}.py
├── tests/{test_densities,test_cdf,test_quantile,test_moments,test_tails}.py
├── notebooks/06_density_lab.ipynb
└── results/
```

```python
# src/densitylab/densities.py
import math
import numpy as np

def normal_pdf(x, mu=0.0, sigma=1.0):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1 + np.vectorize(math.erf)((np.asarray(x) - mu) / (sigma * math.sqrt(2))))
def exponential_pdf(x, lam=1.0):
    x = np.asarray(x, float); return np.where(x >= 0, lam * np.exp(-lam * np.maximum(x, 0)), 0.0)
def exponential_cdf(x, lam=1.0):
    x = np.asarray(x, float); return np.where(x >= 0, 1 - np.exp(-lam * np.maximum(x, 0)), 0.0)
def cauchy_pdf(x, x0=0.0, gamma=1.0):
    return 1 / (math.pi * gamma * (1 + ((np.asarray(x) - x0) / gamma) ** 2))
def cauchy_cdf(x, x0=0.0, gamma=1.0):
    return 0.5 + np.arctan((np.asarray(x) - x0) / gamma) / math.pi
def mixture_pdf(x, weights=(0.3, 0.7), mus=(-2.0, 1.5), sigmas=(0.7, 1.0)):
    return sum(w * normal_pdf(x, m, s) for w, m, s in zip(weights, mus, sigmas))
```

```python
# src/densitylab/cdf.py
import numpy as np

def cumtrapz(y, x):
    return np.r_[0.0, np.cumsum(np.diff(x) * (y[1:] + y[:-1]) / 2)]

def numeric_cdf(pdf, lo, hi, n=200_001):
    x = np.linspace(lo, hi, n); c = cumtrapz(pdf(x), x)
    total = c[-1]
    return x, c, total                      # `total` should be ≈ 1; the caller decides whether to renormalize

def quantile_interp(x, c, q):
    c = c / c[-1]                           # enforce monotone CDF ending at 1
    return np.interp(q, c, x)

def ks_statistic(samples, cdf):
    s = np.sort(samples); n = len(s); F = cdf(s)
    return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))
```

```python
# tests/test_cdf.py
import math, numpy as np
from densitylab.densities import normal_pdf, normal_cdf, exponential_pdf, exponential_cdf
from densitylab.cdf import numeric_cdf, quantile_interp, ks_statistic

def test_normal_normalizes_and_cdf_matches():
    x, c, total = numeric_cdf(normal_pdf, -10, 10)
    assert abs(total - 1.0) < 1e-9
    assert np.max(np.abs(c - normal_cdf(x))) < 1e-8

def test_68_95_997_rule():
    x, c, _ = numeric_cdf(normal_pdf, -10, 10)
    P = lambda k: np.interp(k, x, c) - np.interp(-k, x, c)
    assert abs(P(1) - 0.682689492) < 1e-6 and abs(P(2) - 0.954499736) < 1e-6 and abs(P(3) - 0.997300204) < 1e-6

def test_quantile_roundtrip_and_196():
    x, c, _ = numeric_cdf(normal_pdf, -10, 10)
    q = quantile_interp(x, c, 0.975)
    assert abs(q - 1.959963985) < 1e-4
    qs = np.array([0.01, 0.1, 0.5, 0.9, 0.99])
    assert np.allclose(np.interp(quantile_interp(x, c, qs), x, c), qs, atol=1e-8)

def test_ks_small_for_inverse_transform_samples():
    x, c, _ = numeric_cdf(exponential_pdf, 0, 40)
    u = np.random.default_rng(0).uniform(size=20_000)
    samples = quantile_interp(x, c, u)
    assert ks_statistic(samples, exponential_cdf) < 0.02
```

AUC area helper for R10:

```python
import math, numpy as np
def theoretical_auc_equal_gaussians(mu0, mu1, sigma):
    z = (mu1 - mu0) / (sigma * math.sqrt(2)); return 0.5 * (1 + math.erf(z / math.sqrt(2)))
def numeric_auc_from_densities(mu0, mu1, sigma, n=20001):
    t = np.linspace(-10, 10, n)
    fpr = 1 - 0.5 * (1 + np.vectorize(math.erf)((t - mu0) / (sigma * math.sqrt(2))))      # P(score > t | class 0)
    tpr = 1 - 0.5 * (1 + np.vectorize(math.erf)((t - mu1) / (sigma * math.sqrt(2))))
    order = np.argsort(fpr); f, tp = fpr[order], tpr[order]
    return float(np.sum(np.diff(f) * (tp[1:] + tp[:-1]) / 2))
assert abs(numeric_auc_from_densities(0, 1.0, 1.0) - theoretical_auc_equal_gaussians(0, 1.0, 1.0)) < 1e-6
```

`[VERIFY]` Run `test_quantile_roundtrip_and_196` to confirm the `1e-4` tolerance is appropriate for `n = 200_001` and the chosen range; tighten or loosen only with evidence.

### 11.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2 | Each density normalizes to within `1e-8` (finite-support) or `1e-6` (infinite support with analytic tail bound); the unnormalized-density helper recovers a known constant |
| M2 | R3–R5 | CDF errors vs closed forms ≤ `1e-8` for the normal and exponential; `P(−1.96 < Z < 1.96)` within `1e-6` of 0.95; quantile round-trip `< 1e-8` |
| M3 | R6–R7 | Moments match closed forms to `1e-6`; KS statistic from `N = 20 000` inverse-transform samples is below the `≈ 1.36/√N`-scale threshold you derive and report `[VERIFY: critical value]` |
| M4 | R8 | Heavy-tail figures: Cauchy running mean vs normal, first-absolute-moment growth `∝ ln T`, truncation sensitivity table |
| M5 | R9–R10 | Numerical KL within `1e-6` of the closed form; infinite-KL case reported correctly; AUC from densities matches the closed form within `1e-6` and the empirical AUC within sampling error |
| M6 | R11 | Report regenerated by one script from a clean venv; every claim tied to a figure/table with `N`, seeds, and tolerances |

### 11.5 Questions the write-up must answer

1. How wide must the integration range be for an infinite-support density to normalize to `1e-8`? Show the tail bound.
2. Why does the numerical CDF error behave as it does when the grid is refined? (Fit the order.)
3. What changes when you integrate a mixture with two well-separated narrow components on a coarse grid?
4. Why does the Cauchy distribution break moment calculations, and what does the experiment show?
5. How does the integral definition of AUC relate to the "probability a positive outscores a negative"?

### 11.6 Failure modes to demonstrate

Range too narrow (normalization `< 1`); grid too coarse for a narrow component (missing mass); CDF not exactly monotone from numerical noise (interpolation failure); quantile requests at `q = 0` or `1` on infinite support; discontinuous density (uniform edges) with the trapezoid rule; heavy-tail moments computed with a truncation that silently decides the answer; renormalizing a density that was truncated and thereby hiding a tail problem; KL with `q(x) = 0` where `p(x) > 0`.

### 11.7 Stretch goals

1. Entropy of each density by integration vs closed form (Gaussian: `½ ln(2πeσ²)`), previewing Module 13.
2. Student-t family: how the moment existence changes with degrees of freedom; show variance diverging for `ν ≤ 2` `[VERIFY: statement]`.
3. A kernel density estimate of samples, integrated to check normalization and compared against the true density by integrated squared error.
4. Highest-density interval for a bimodal mixture vs the equal-tailed interval.
5. Use Gauss–Hermite quadrature for `E[g(X)]` under a normal and compare accuracy/evaluations with Monte Carlo.

### 11.8 ML connection (README prompt)

Connect each result to a downstream use: CDFs and quantiles in confidence intervals and prediction intervals (Module 12), inverse-transform sampling in token sampling (Module 11), KL in training objectives (Module 13), heavy tails in evaluation metrics and gradients, AUC in classifier evaluation (Stage 5A-06).

### Check yourself (Unit 11)

1. What check proves your numerical CDF is correct before you trust a quantile from it?
2. Why can renormalizing a truncated density be dangerous?

**Reference answers:** (1) Compare it with a closed-form CDF on a known density, confirm `CDF(hi) ≈ 1`, monotonicity, and the round-trip `cdf(quantile(q)) ≈ q`. (2) Dividing by the truncated total silently absorbs missing tail mass, which can hide a range that is too narrow or a density that does not integrate to 1.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 6 lessons, 2 projects, 11 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 04, 09–13, 4C-04/05/06/10, and Stage 5 pointers (5A-06) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: PR-AUC trapezoid optimism, Romberg/tanh–sinh details, KS critical values, Student-t moment existence, framework conventions for `np.trapz`/`np.trapezoid`, `math.fsum` guidance.
4. `[VERIFY]` All printed numerical results (fitted orders, growth rates, MC errors, KS values) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, SymPy 1.14): every lesson snippet executed; all 4 `integkit` and all 4 `densitylab` tests passed; adaptive Simpson reached an error of about 1e-12 on a sharply peaked integrand with 4,593 evaluations, and the fixed doubling rule reached about 3e-12 with 4,097 evaluations (both on that single integrand; report your own comparison). Defects found and fixed during the run: (a) `leggauss` with `n` in the thousands is impractically slow (replaced by composite panels), (b) on `∫₀^π sin` the left/right Riemann rules show order 2 because both endpoint values are 0 (demo moved to `∫₀^{π/2} sin`), (c) a kink at `x = 1/3` makes Simpson's error cancel on power-of-two grids (kink moved to `0.3`; measured order at the kink ≈ 2, not 1). Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, accuracy, error-order, or tolerance figure appears without the measurement that produced it.
