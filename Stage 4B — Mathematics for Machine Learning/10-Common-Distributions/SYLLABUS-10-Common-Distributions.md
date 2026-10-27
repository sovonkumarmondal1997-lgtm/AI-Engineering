# SYLLABUS — 10-Common-Distributions (S4B-10)

**Stage 4B — Mathematics for Machine Learning · Module 10 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy and the standard library (`math`); SciPy is **never required** (optional only for cross-checks), Matplotlib and pytest where stated. All datasets are **synthetic and generated in code**. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Bernoulli and binomial | `01-bernoulli-and-binomial.md` | Beginner |
| 3 | Categorical, multinomial, and softmax | `02-categorical-multinomial-and-softmax.md` | Beginner → Intermediate |
| 4 | Poisson distribution | `03-poisson-distribution.md` | Intermediate |
| 5 | Uniform and exponential distributions | `04-uniform-and-exponential-distributions.md` | Intermediate |
| 6 | Normal distribution | `05-normal-distribution.md` | Intermediate → Advanced |
| 7 | Beta and Dirichlet distributions (in outline) | `06-beta-and-dirichlet-distributions-in-outline.md` | Intermediate → Advanced |
| 8 | Practice question bank | `practice-questions.md` | All levels |
| 9 | Project index | `Projects/README.md` | Intermediate |
| 10 | Project: distribution gallery and fitting | `Projects/01-distribution-gallery-and-fitting.md` | Intermediate → Advanced |
| 11 | Project: Poisson event-rate simulator | `Projects/02-poisson-event-rate-simulator.md` | Advanced |

**Prerequisites:** Module 09 (PMF/PDF/CDF, expectation, variance, covariance, Bayes, independence), Module 06 (integrals, normalization, improper integrals, `erf`), Module 05 (log-sum-exp and stable forms, derivatives of sigmoid/log), Module 07 (gradient of cross-entropy preview). **Plan slot:** week 12 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** required on every track; Lessons 1, 2, 5 and 6 are used constantly in Stage 5 (losses, softmax, noise models, priors).

**Teaching stance (industry, not university):** a distribution is a *modelling choice for a real quantity*. Each lesson answers four practical questions: **What does it model? What are its parameters and moments? How do I sample, evaluate, and fit it? When does it silently fail?** Every closed form is checked against simulation, and every approximation is checked for where it breaks.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (formula, simulation, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

A model is a distribution plus a way to estimate its parameters. The labels of a classifier are Bernoulli or categorical, the softmax is a categorical distribution over classes, regression noise is usually Gaussian, event counts are Poisson, waiting times are exponential, and probabilities themselves can be given Beta or Dirichlet priors. Loss functions are *negative log-likelihoods* of these distributions: cross-entropy is the Bernoulli/categorical NLL and mean squared error is the Gaussian NLL. Knowing the family tells you the loss, the metric, the right interval, and the failure mode.

### 1.2 Outcomes

1. For each distribution: state what it models, its support, parameters, mean, and variance; evaluate pmf/pdf and cdf; sample from it; fit its parameters by maximum likelihood (or method of moments) and check the fit.
2. Use the log-pmf/log-pdf form for numerical stability (log-gamma, log-sum-exp) and avoid overflow/underflow.
3. Explain softmax as the map from logits to a categorical distribution, derive the cross-entropy gradient `p − y`, and implement a stable log-softmax.
4. Recognize the relationships between distributions (binomial → Poisson, exponential ↔ Poisson process, sums of normals, Beta–Binomial and Dirichlet–Multinomial conjugacy, sigmoid as 2-class softmax).
5. Detect **model misfit**: overdispersion for counts, heavy tails for continuous data, clustering that breaks the binomial.
6. Choose a distribution from the data type and constraints, and justify it.
7. Build a distribution gallery with fitting and goodness-of-fit (with honest p-values by parametric bootstrap) and a Poisson simulator with alert thresholds validated for false-alarm rate.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Bernoulli, binomial | Binary labels, accuracy as a binomial, BCE | pmf in log space; exact CI; overdispersion |
| 2 | Categorical, multinomial, softmax | Softmax heads, cross-entropy, sampling | Stable softmax; CE gradient; Gumbel-max |
| 3 | Poisson | Count data, event rates, alerts | Binomial→Poisson; dispersion; thresholds |
| 4 | Uniform, exponential | Random init/search, waiting times | Memoryless; log-uniform search; scale pitfall |
| 5 | Normal | Noise model, init, standardization, MSE | MLE; LL↔MSE; QQ; heavy tails |
| 6 | Beta, Dirichlet | Priors, smoothing, Bayesian updating | Conjugate update; Dirichlet via Gammas |

### 1.4 Concept map

```
Bernoulli(p) ─sum of n iid─► Binomial(n,p) ─n→∞, np=λ─► Poisson(λ) ◄─counts in a window of─ Poisson process ─gaps─► Exponential(λ) ─(log-)uniform U(0,1) via inverse CDF
      │                           │ normal approx (np large)                                                    ▲
      │                           └──────────────────────────► Normal(μ,σ²)  ◄── CLT (Module 11) ── sums/averages
Categorical(π) ◄── softmax(logits) ── generalizes ── Bernoulli (sigmoid = 2-class softmax)
   └─ counts ─► Multinomial(n, π)
Beta(α,β) ── conjugate prior for p ──► posterior Beta(α+k, β+n−k)     Dirichlet(α) ── conjugate prior for π ──► Dirichlet(α+counts)
loss = −log-likelihood:  BCE (Bernoulli) · cross-entropy (categorical) · MSE (Normal) · Poisson deviance (Poisson)
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest          # scipy optional, for cross-checks only
```

Rules for every lab: **implement the pmf/pdf from the formula (using `math.lgamma` for factorials), then check it three ways**: it sums/integrates to 1; its moments match the formulas; a large simulated sample matches it within `4·SE` (or a KS bound); work in **log space** for anything with factorials, products, or exponentials; **state the parameterization** (rate vs scale, `σ` vs `σ²`, `α, β` vs mean/concentration) every time; seed all randomness; report fitted parameters with uncertainty (standard error or bootstrap).

### 1.6 Checkpoint

For every distribution in the module, your own pmf/pdf, cdf, sampler, mean/variance, and MLE agree with simulation within stated tolerances, and you can name the loss function each one implies.

### Check yourself (Unit 1)

1. Which loss corresponds to a Gaussian noise model, and which to a categorical output?
2. Why is it important to state the parameterization of a distribution?

**Reference answers:** (1) Mean squared error; cross-entropy (negative log-likelihood). (2) Libraries differ (e.g., NumPy's exponential takes the *scale* `1/λ`, not the rate), and mixing them silently changes results.

---

## Unit 2 — Bernoulli and binomial (`01-…md`)

### 2.1 Why ML needs this

A binary label is a Bernoulli variable. The number of correct predictions on `n` independent test items is binomial, which is exactly why accuracy has standard error `√(p(1−p)/n)` (Module 09). The Bernoulli log-likelihood is binary cross-entropy. Dropout masks and click events are Bernoulli draws.

### 2.2 Intuition

One yes/no trial with success probability `p` is **Bernoulli(p)**. Count the successes in `n` independent such trials and you get **Binomial(n, p)**.

### 2.3 Mechanics

| | Bernoulli(`p`) | Binomial(`n, p`) |
|---|---|---|
| Support | `{0, 1}` | `{0, …, n}` |
| pmf | `pˣ(1−p)^{1−x}` | `C(n,k) pᵏ (1−p)^{n−k}` |
| Mean | `p` | `np` |
| Variance | `p(1−p)` | `np(1−p)` |
| Notes | maximal variance at `p = ½` | sum of `n` i.i.d. Bernoulli(`p`) |

- **Sum rule:** independent `Binomial(n₁, p)` + `Binomial(n₂, p)` = `Binomial(n₁ + n₂, p)` (same `p`).
- **MLE:** `p̂ = k/n` (the sample proportion). **Log-likelihood** of Bernoulli data `x₁…xₙ`: `Σ [xᵢ ln p + (1−xᵢ) ln(1−p)]`, whose negative mean is **binary cross-entropy** (Module 13–14).
- **Standard error:** `SE(p̂) = √(p̂(1−p̂)/n)`; intervals: normal (Wald), **Wilson**, and the **exact Clopper–Pearson** interval, obtained by inverting the binomial cdf (`P(X ≥ k | p_L) = α/2`, `P(X ≤ k | p_U) = α/2`) `[VERIFY: formulas]`.
- **Normal approximation:** `Binomial(n, p) ≈ N(np, np(1−p))` when `np` and `n(1−p)` are both large (rule of thumb ≥ 10 `[JUDGEMENT]`); poor for small `n` or extreme `p` (use the exact pmf or Poisson for rare events, Lesson 4).
- **Numerical stability:** `C(n, k)` overflows for large `n`; compute `log pmf = lgamma(n+1) − lgamma(k+1) − lgamma(n−k+1) + k ln p + (n−k) ln(1−p)` and handle `p ∈ {0, 1}` explicitly.
- **Assumptions that break:** independence (clustered data, repeated measures, correlated users) and a common `p` (heterogeneous items). The symptom is **overdispersion**: observed variance exceeds `np(1−p)`.
- **Sampling:** `rng.binomial(n, p)`, `rng.random(n) < p`.

**Worked example:** a classifier with true accuracy `0.9` on `n = 200` items: correct count `~ Binomial(200, 0.9)`, mean `180`, SD `√(200·0.9·0.1) ≈ 4.24`, so accuracy `0.9 ± 0.021`; a 95% range for measured accuracy is roughly `[0.86, 0.94]`.

### 2.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def binom_logpmf(k, n, p):
    if p == 0.0: return 0.0 if k == 0 else -math.inf
    if p == 1.0: return 0.0 if k == n else -math.inf
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p))
binom_pmf = lambda k, n, p: math.exp(binom_logpmf(k, n, p))

# --- pmf sums to 1, moments match, simulation agrees
n, p = 30, 0.2
pmf = np.array([binom_pmf(k, n, p) for k in range(n + 1)])
assert np.isclose(pmf.sum(), 1.0) and np.isclose((np.arange(n + 1) * pmf).sum(), n * p)
assert np.isclose(((np.arange(n + 1) - n * p) ** 2 * pmf).sum(), n * p * (1 - p))
s = rng.binomial(n, p, size=400_000); emp = np.bincount(s, minlength=n + 1) / len(s)
assert np.max(np.abs(emp - pmf)) < 0.003

# --- large n: the naive formula overflows, the log form does not
print("C(2000, 1000) as float:", end=" ")
try: print(float(math.comb(2000, 1000)))
except OverflowError: print("overflow")
print("log-pmf(1000; 2000, 0.5) =", binom_logpmf(1000, 2000, 0.5))

# --- Bernoulli MLE = sample proportion; negative mean log-likelihood = BCE
x = (rng.random(500) < 0.35).astype(float)
ps = np.linspace(0.01, 0.99, 981)
ll = np.array([np.sum(x * np.log(q) + (1 - x) * np.log(1 - q)) for q in ps])
assert abs(ps[np.argmax(ll)] - x.mean()) < 2e-3
bce = lambda x, q: -np.mean(x * np.log(q) + (1 - x) * np.log(1 - q))
assert np.isclose(bce(x, 0.4), -ll[np.argmin(np.abs(ps - 0.4))] / len(x))

# --- normal approximation: good for n=1000, p=0.5; poor for n=20, p=0.05
def normal_pdf(x, mu, s): return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))
for n_, p_ in ((1000, 0.5), (20, 0.05)):
    ks = range(0, min(n_, 60) + 1)
    err = max(abs(binom_pmf(k, n_, p_) - normal_pdf(k, n_ * p_, math.sqrt(n_ * p_ * (1 - p_)))) for k in ks)
    print(f"n={n_:4d}, p={p_}: max |pmf − normal| = {err:.4f}   (np = {n_ * p_:g})")

# --- exact (Clopper–Pearson) interval by bisection on the binomial cdf
def binom_cdf(k, n, p): return sum(binom_pmf(i, n, p) for i in range(0, k + 1))
def clopper_pearson(k, n, alpha=0.05):
    def bisect(f, lo=0.0, hi=1.0):
        for _ in range(80):
            mid = (lo + hi) / 2; lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return (lo + hi) / 2
    # bisect() expects a DECREASING function (positive on the left, negative on the right)
    lower = 0.0 if k == 0 else bisect(lambda q: alpha / 2 - (1 - binom_cdf(k - 1, n, q)))    # P(X ≥ k | q) increases with q
    upper = 1.0 if k == n else bisect(lambda q: binom_cdf(k, n, q) - alpha / 2)               # P(X ≤ k | q) decreases with q
    return lower, upper
print("CP(0/100):", clopper_pearson(0, 100), "  CP(90/100):", clopper_pearson(90, 100))

# --- overdispersion: heterogeneous p breaks the binomial variance
n = 50; reps = 100_000
iid = rng.binomial(n, 0.3, size=reps)
p_i = rng.beta(1.5, 3.5, size=reps)                       # per-run success probability, mean 0.3
clustered = rng.binomial(n, p_i)
print("binomial var:", n * 0.3 * 0.7, "| iid sample var:", iid.var(), "| clustered sample var:", clustered.var(), "(overdispersed)")
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `math.comb`/factorials for large `n` | `OverflowError`/`inf` | Log-gamma form |
| `log(0)` at `p ∈ {0, 1}` | `-inf`/`nan` | Handle edges explicitly; clip with care |
| Normal interval at small `n` or extreme `p` | Zero-width or out-of-`[0,1]` intervals | Wilson or Clopper–Pearson |
| Assuming independence for clustered data (users with many rows, repeated runs) | Overdispersion; intervals far too narrow | Cluster-aware intervals; compare observed variance with `np(1−p)` |
| Treating the "n" as the number of rows rather than independent trials | Overstated confidence | Count effective independent units |
| Reporting accuracy without `n` | Uninterpretable | `p̂ ± SE` with `n` |
| Using the binomial for sampling *without* replacement from a small population | Wrong variance | Hypergeometric / finite-population correction (Module 08) |
| Equating `p̂ = 0` with `p = 0` | "Impossible" claims | Upper bound (rule of three: `≈ 3/n`) `[VERIFY]` |

### 2.6 ML link

- **Binary labels and BCE:** the Bernoulli NLL is the logistic-regression loss (Module 13–14).
- **Accuracy as a binomial proportion:** intervals and A/B comparisons of conversion rates (Module 12).
- **Dropout** applies a Bernoulli mask to activations (Stage 5C-03).
- **Overdispersion** is the symptom of correlated or heterogeneous units in evaluation sets; group-aware splits and clustered standard errors (Stage 5A-07).
- **Rare-event rates** (fraud, defects) call for exact/Poisson treatment (Lesson 4).

### 2.7 Lab (60 min)

1. Implement the log-pmf; verify normalization, moments, and simulation for three `(n, p)` pairs, including `n = 5000`.
2. Reproduce the BCE ↔ Bernoulli-log-likelihood identity and find the MLE by grid and in closed form.
3. Map the region of `(n, p)` where the normal approximation has error above `0.01` in the pmf.
4. Build the Clopper–Pearson interval and compare its empirical coverage with Wald and Wilson at `p = 0.02`, `n = 100` (5,000 repetitions); report your numbers.
5. Produce an overdispersed dataset (heterogeneous `p`) and compute the dispersion ratio `Var/(np̂(1−p̂))`.

### Check yourself (Unit 2)

1. Mean and variance of `Binomial(100, 0.3)`?
2. What is the MLE of `p` from `k` successes in `n` trials?
3. What does overdispersion indicate?

**Reference answers:** (1) `30` and `21`. (2) `k/n`. (3) The independence/constant-`p` assumptions fail (clustering or heterogeneity), so the variance exceeds `np(1−p)`.

---

## Unit 3 — Categorical, multinomial, and softmax (`02-…md`)

### 3.1 Why ML needs this

Every multi-class classifier ends in a softmax that outputs a **categorical distribution** over classes, and trains with **cross-entropy**, its negative log-likelihood. Token sampling in a language model is a categorical draw from a softmax. Getting softmax and log-softmax numerically right is a daily production concern.

### 3.2 Intuition

**Categorical(π)** is a die with `K` faces and face probabilities `π₁…π_K` (summing to 1). **Multinomial(n, π)** counts how many times each face appears in `n` rolls. **Softmax** turns arbitrary real scores (*logits*) into probabilities: exponentiate, then normalize.

### 3.3 Mechanics

- **Categorical:** `P(Y = k) = πₖ`, `Σπₖ = 1`; encode as a **one-hot** vector. Mean of the one-hot vector is `π`; covariance `diag(π) − ππᵀ`.
- **Multinomial(`n, π`):** counts `(k₁…k_K)` with `Σkᵢ = n`; pmf `n!/(Πkᵢ!) Π πᵢ^{kᵢ}`; `E[kᵢ] = nπᵢ`, `Var(kᵢ) = nπᵢ(1−πᵢ)`, **`Cov(kᵢ, kⱼ) = −nπᵢπⱼ`** (negative: a fixed total forces trade-offs).
- **MLE:** `π̂ₖ = kₖ/n` (counts divided by total); with additive smoothing `(kₖ + α)/(n + Kα)` (Module 09, Lesson 3; the Dirichlet-prior view in Lesson 6).
- **Softmax:** `softmax(z)ᵢ = exp(zᵢ) / Σⱼ exp(zⱼ)`.
  - **Shift invariance:** `softmax(z + c𝟙) = softmax(z)`, so subtract `max(z)` for stability.
  - **Temperature:** `softmax(z/T)`: `T → 0` approaches argmax (one-hot), `T → ∞` approaches uniform.
  - **Sigmoid is 2-class softmax:** `σ(z) = softmax([z, 0])₁`.
  - **Log-softmax:** `log softmax(z)ᵢ = zᵢ − logsumexp(z)`; compute it directly, never as `log(softmax(z))` (underflow gives `-inf`).
  - **logsumexp:** `m + log Σ exp(zⱼ − m)` with `m = max z`.
- **Cross-entropy loss** for label `y`: `L = −log softmax(z)_y = logsumexp(z) − z_y`.
- **Gradient (the identity to memorize):** `∂L/∂zᵢ = softmax(z)ᵢ − 1[i = y]`, i.e. **`p − y`** (Module 07). Averaged over a batch: `(P − Y)/B`.
- **Sampling from a categorical:** inverse transform on the cumulative sums (Module 09 Lesson 6), or `rng.choice(K, p=π)`. **Gumbel-max trick:** `argmax_i (zᵢ + Gᵢ)` with `Gᵢ = −ln(−ln Uᵢ)` i.i.d. Gumbel samples exactly from `softmax(z)` `[VERIFY: statement]`.
- **Top-k / top-p (nucleus) sampling** truncate and renormalize the categorical before sampling (Module 11, Stage 5C-12).
- **Saturation:** with large logit gaps the softmax is nearly one-hot and gradients vanish for the dominant class; label smoothing and temperature mitigate (4C-07).
- **Calibration:** softmax outputs are not automatically calibrated probabilities (Stage 5B-04).

**Worked example:** logits `z = (2, 1, 0)`: `exp = (7.389, 2.718, 1)`, sum `11.107`, `p = (0.665, 0.245, 0.090)`; for `y = 0`: `L = −ln 0.665 = 0.408`, gradient `p − y = (−0.335, 0.245, 0.090)`.

### 3.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def logsumexp(z, axis=-1, keepdims=False):
    z = np.asarray(z, float); m = z.max(axis=axis, keepdims=True)
    out = m + np.log(np.exp(z - m).sum(axis=axis, keepdims=True))
    return out if keepdims else np.squeeze(out, axis=axis)
def log_softmax(z, axis=-1): z = np.asarray(z, float); return z - logsumexp(z, axis, keepdims=True)
def softmax(z, axis=-1, T=1.0): return np.exp(log_softmax(np.asarray(z, float) / T, axis))

z = np.array([2.0, 1.0, 0.0]); p = softmax(z)
assert np.allclose(p, np.exp(z) / np.exp(z).sum()) and np.isclose(p.sum(), 1.0)
assert np.allclose(softmax(z + 1000), p)                                         # shift invariance
big = np.array([1000.0, 999.0, 0.0])
with np.errstate(over="ignore", invalid="ignore"): naive = np.exp(big) / np.exp(big).sum()
print("naive:", naive, " stable:", softmax(big))                                  # nan vs finite
assert np.all(np.isfinite(log_softmax(np.array([0.0, -2000.0])))) and np.isclose(log_softmax(np.array([0.0, -2000.0]))[1], -2000.0)

# --- sigmoid = 2-class softmax; temperature
sig = lambda t: 1 / (1 + np.exp(-t))
for t in (-4.0, 0.3, 5.0): assert np.isclose(sig(t), softmax(np.array([t, 0.0]))[0])
for T in (0.1, 1.0, 10.0): print(f"T={T:5}: ", np.round(softmax(z, T=T), 3))

# --- cross-entropy gradient is p − y (check against finite differences)
def ce(z, y): return float(logsumexp(z) - z[y])
def ce_grad(z, y): g = softmax(z); g[y] -= 1.0; return g
z0 = rng.normal(size=5); y0 = 3
num = np.array([(ce(z0 + e * 1e-6, y0) - ce(z0 - e * 1e-6, y0)) / 2e-6 for e in np.eye(5)])
assert np.allclose(ce_grad(z0, y0), num, atol=1e-8)

# --- multinomial: mean and the NEGATIVE covariance
pi = np.array([0.5, 0.3, 0.2]); n = 20
C = rng.multinomial(n, pi, size=300_000)
print("empirical cov:\n", np.round(np.cov(C, rowvar=False), 3)); print("theory: n(diag(π) − ππᵀ):\n", np.round(n * (np.diag(pi) - np.outer(pi, pi)), 3))
assert np.allclose(np.cov(C, rowvar=False), n * (np.diag(pi) - np.outer(pi, pi)), atol=0.06)

# --- MLE and smoothing
counts = np.array([7, 3, 0]); print("MLE:", counts / counts.sum(), " smoothed α=1:", (counts + 1) / (counts.sum() + 3))

# --- Gumbel-max sampling reproduces softmax probabilities
logits = np.array([1.5, 0.5, -0.5, 0.0]); N = 400_000
G = -np.log(-np.log(rng.random((N, 4)))); draws = np.argmax(logits + G, axis=1)
freq = np.bincount(draws, minlength=4) / N; print("Gumbel-max freq:", np.round(freq, 4), " softmax:", np.round(softmax(logits), 4))
assert np.allclose(freq, softmax(logits), atol=0.004)

# --- inverse-transform sampling of a categorical from cumulative sums
cum = np.cumsum(softmax(logits)); idx = np.searchsorted(cum, rng.random(N), side="right").clip(0, 3)
assert np.allclose(np.bincount(idx, minlength=4) / N, softmax(logits), atol=0.004)
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.exp(z)/sum` on large logits | `inf/inf = nan` | Subtract the max (use `log_softmax`/`softmax` above) |
| `np.log(softmax(z))` | `-inf` for very unlikely classes | `log_softmax` / `logsumexp` |
| Cross-entropy on probabilities with `p = 0` | `-inf` loss, `nan` gradients | Compute from logits |
| Forgetting `1/B` when averaging over a batch | Gradient scale off by `B` | State the reduction; check numerically |
| Softmax over the wrong axis (batch vs class) | Rows do not sum to 1 | Assert `p.sum(axis=-1) ≈ 1` |
| Temperature `T = 0` | Division by zero | Treat as argmax explicitly |
| Treating softmax scores as calibrated probabilities | Overconfident predictions | Calibrate (Stage 5B-04) |
| Float32 probabilities not summing to exactly 1 for `rng.choice` | `ValueError: probabilities do not sum to 1` | Renormalize in float64 |
| Sampling with `p` containing negatives | Error or bias | Validate non-negativity |

### 3.6 ML link

- **Classification heads:** softmax + cross-entropy, gradient `p − y` (Module 07, 14, Stage 5C-01).
- **Language-model decoding:** categorical sampling from softmax with temperature/top-k/top-p (Module 11, Stage 5C-12).
- **Multinomial** is the likelihood for bag-of-words counts (naive Bayes, Module 09 Project 2) and topic models.
- **Label smoothing, logit scaling, calibration** (4C-07, Stage 5B-04).
- **Gumbel-softmax / reparameterization** for discrete latent variables (4C-10) `[VERIFY]`.

### 3.7 Lab (75 min)

1. Implement stable `logsumexp`, `softmax`, `log_softmax`; show failures of the naive versions on logits `≥ 1000` and `≤ −1000`.
2. Verify the cross-entropy gradient `p − y` numerically on 50 random logit vectors, and for a batch with the `1/B` reduction.
3. Verify sigmoid = 2-class softmax, shift invariance, and the temperature limits.
4. Simulate multinomial counts; compare the empirical covariance matrix with `n(diag(π) − ππᵀ)`; explain the negative off-diagonals.
5. Sample from a softmax three ways (`rng.choice`, inverse transform, Gumbel-max) and compare frequencies; time them on `N = 10⁶` (your machine, your numbers).

### Check yourself (Unit 3)

1. What is `∂L/∂z` for softmax cross-entropy?
2. Why is `Cov(kᵢ, kⱼ) < 0` for a multinomial?
3. Write `log softmax(z)ᵢ` in a stable form.

**Reference answers:** (1) `softmax(z) − onehot(y)`. (2) The counts must sum to `n`, so more of one category means fewer of the others. (3) `zᵢ − logsumexp(z)` with `logsumexp(z) = m + log Σ exp(zⱼ − m)`, `m = max z`.

---

## Unit 4 — Poisson distribution (`03-…md`)

### 4.1 Why ML needs this

Many targets and monitoring signals are **counts of events in a window**: requests per second, defects per batch, clicks per hour, mentions per document. The Poisson distribution is the first model for them, and its failure (overdispersion) is the most common real-world modelling error with count data.

### 4.2 Intuition

Events occur independently at a constant average **rate**. The number in a fixed window follows a **Poisson(λ)**, where `λ` is the average count. The waiting times between events follow an **exponential** distribution (Lesson 5): two views of the same *Poisson process*.

### 4.3 Mechanics

- **pmf:** `P(N = k) = e^{−λ} λᵏ / k!`, `k = 0, 1, 2, …`; **mean `λ`, variance `λ`** (the hallmark `Var = mean`).
- **Rate and exposure:** for a window of length `t` and rate `r` per unit time, `N ~ Poisson(rt)`; always carry the exposure.
- **Binomial limit:** `Binomial(n, p)` with `n → ∞`, `p → 0`, `np = λ` tends to Poisson(`λ`). Good approximation when `n` is large and `p` small.
- **Sums:** independent `Poisson(λ₁) + Poisson(λ₂) = Poisson(λ₁ + λ₂)` (superposition). **Thinning:** keeping each event independently with probability `q` gives `Poisson(qλ)` (splitting).
- **Poisson process ↔ exponential gaps:** the gaps between events are i.i.d. `Exponential(rate λ)`; counting events in `[0, T]` gives `Poisson(λT)`.
- **MLE:** `λ̂ = x̄` (sample mean); log-likelihood `Σ (kᵢ ln λ − λ − ln kᵢ!)`.
- **Dispersion index:** `Var/mean`. `≈ 1` Poisson; `> 1` **overdispersion** (clustering, varying rates, bursts: modelled by negative binomial / gamma–Poisson mixtures `[VERIFY]`); `< 1` underdispersion (regularity).
- **Zero-inflation:** more zeros than Poisson predicts (e.g., many users never act).
- **Tail probabilities for alerting:** `P(N ≥ k) = 1 − Σ_{j<k} pmf(j)`; choose the threshold `k` so the false-alarm probability is below a target `α`. The **normal approximation** is poor for small `λ` and in the tail.
- **Poisson regression** (preview): log-linear rate `λ = exp(w·x)` trained by the Poisson NLL (Module 14, 4C-05).
- **Numerics:** compute the pmf in logs (`k ln λ − λ − lgamma(k+1)`).

**Worked example:** a service averages `λ = 4` errors per minute. `P(N = 0) = e⁻⁴ ≈ 0.0183`; `P(N ≥ 10) ≈ 0.0081`. An alert at `N ≥ 10` fires on about 0.8% of normal minutes (if the Poisson model holds).

### 4.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def pois_logpmf(k, lam):
    if lam == 0: return 0.0 if k == 0 else -math.inf
    return k * math.log(lam) - lam - math.lgamma(k + 1)
pois_pmf = lambda k, lam: math.exp(pois_logpmf(k, lam))
pois_cdf = lambda k, lam: sum(pois_pmf(j, lam) for j in range(0, k + 1))
pois_sf_ge = lambda k, lam: 1.0 - pois_cdf(k - 1, lam) if k > 0 else 1.0       # P(N ≥ k)

lam = 4.0; ks = np.arange(0, 80); pmf = np.array([pois_pmf(k, lam) for k in ks])
assert np.isclose(pmf.sum(), 1.0) and np.isclose((ks * pmf).sum(), lam) and np.isclose(((ks - lam) ** 2 * pmf).sum(), lam)   # mean = var = λ
x = rng.poisson(lam, size=400_000); assert abs(x.mean() - lam) < 0.02 and abs(x.var() - lam) < 0.05
print("P(N=0) =", pois_pmf(0, lam), " P(N≥10) =", pois_sf_ge(10, lam))

# --- binomial → Poisson: total-variation distance shrinks as n grows with np = λ
def binom_pmf(k, n, p): return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p))
for n in (10, 100, 1000, 10000):
    p = lam / n; tv = 0.5 * sum(abs(binom_pmf(k, n, p) - pois_pmf(k, lam)) for k in range(0, min(n, 60) + 1))
    print(f"n={n:6d}  TV(Binomial, Poisson) = {tv:.5f}")

# --- Poisson process: exponential gaps → Poisson counts; superposition and thinning
def process_counts(rate, T, windows, g):
    counts = np.zeros(windows, int)
    for w in range(windows):
        t, c = 0.0, 0
        while True:
            t += g.exponential(1 / rate)                              # NumPy takes the SCALE = 1/rate
            if t > T: break
            c += 1
        counts[w] = c
    return counts
c = process_counts(rate=2.0, T=3.0, windows=20_000, g=rng)
print("process counts: mean", c.mean(), " var", c.var(), " (both ≈ λT = 6)")
a, b = rng.poisson(3.0, 300_000), rng.poisson(5.0, 300_000); print("superposition: mean/var of sum:", (a + b).mean(), (a + b).var(), "(≈ 8)")
n_ev = rng.poisson(10.0, 300_000); kept = rng.binomial(n_ev, 0.3); print("thinned (q=0.3): mean/var:", kept.mean(), kept.var(), "(≈ 3)")

# --- overdispersion: rates that vary from window to window (gamma–Poisson mixture)
lam_i = rng.gamma(shape=2.0, scale=lam / 2.0, size=400_000)            # mean λ, variance λ²/2
over = rng.poisson(lam_i)
print(f"dispersion index: Poisson {x.var() / x.mean():.2f}   mixture {over.var() / over.mean():.2f}   (theory 1 and {1 + lam / 2:.1f})")

# --- the alert threshold that assumes Poisson fires far too often under overdispersion
alpha = 1e-3; thr = next(k for k in range(1, 200) if pois_sf_ge(k, lam) <= alpha)
print(f"threshold N ≥ {thr} (design false-alarm rate ≤ {alpha}); actual rate when counts are Poisson: {(x >= thr).mean():.5f}; when overdispersed: {(over >= thr).mean():.5f}")

# --- MLE, and a normal-approximation tail that is badly off for small λ
lam_hat = x[:1000].mean(); print("MLE λ̂ =", lam_hat)
lam_small = 1.0; exact_tail = pois_sf_ge(5, lam_small)
normal_tail = 0.5 * math.erfc((4.5 - lam_small) / math.sqrt(2 * lam_small))                    # continuity-corrected P(N ≥ 5) = 1 − Φ((4.5 − λ)/√λ)
print(f"λ=1, P(N≥5): exact {exact_tail:.5f}  normal approx {normal_tail:.5f}")
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Poisson for overdispersed counts | Alerts and intervals too tight; false alarms (demo above) | Dispersion index; negative binomial / quasi-Poisson |
| Ignoring exposure (window length, user count) | Rates not comparable | Model `rate × exposure` |
| Assuming a constant rate | Daily/weekly seasonality inflates variance | Model the rate (time of day), or window by phase |
| `k!` overflow | `OverflowError` for large `k` | Log form with `lgamma` |
| Normal approximation for small `λ` or far tails | Wrong tail probabilities | Exact pmf/cdf |
| Zero-inflated data modelled as Poisson | Misfit at 0 | Zero-inflated models; separate the "never" population |
| Using the sample variance as `λ̂` | Biased under overdispersion | `λ̂ = x̄` for the mean; report dispersion separately |
| Treating dependent events as Poisson (cascades, retries) | Burstiness underestimated | Check autocorrelation of counts; model the dependence |
| Comparing counts across different window sizes without normalizing | Spurious "increases" | Convert to rates |

### 4.6 ML link

- **Count targets** (clicks, purchases, sensor events) use Poisson/negative-binomial regression (Module 14, Stage 5A-04).
- **Event-rate monitoring and alerting** thresholds from tail probabilities (Stage 5D-12; Project 2).
- **Rare-event classification** as a Poisson limit of many small-probability trials (fraud, defects).
- **Language statistics** (word counts) and **recommendation exposures** use Poisson factorization ideas (Stage 5B-09) `[JUDGEMENT]`.
- **Queueing and capacity planning** via Poisson arrivals + exponential service (Stage 5D-09/11) `[JUDGEMENT]`.

### 4.7 Lab (90 min)

1. Implement the log-pmf, cdf, and tail probability; verify mean = variance = `λ` by simulation for `λ ∈ {0.5, 4, 50}`.
2. Binomial → Poisson convergence table (TV distance) for `λ ∈ {1, 4, 20}`.
3. Simulate a Poisson process by exponential gaps; verify the counts, superposition, and thinning identities.
4. Generate overdispersed counts (gamma–Poisson); compute the dispersion index; build a Poisson alert threshold and measure its real false-alarm rate on Poisson vs overdispersed traffic.
5. Compare exact and normal-approximation tail probabilities for `λ ∈ {1, 4, 25, 100}` at the `1e-3` tail.

### Check yourself (Unit 4)

1. What are the mean and variance of `Poisson(λ)`?
2. How does the sum of two independent Poisson variables behave?
3. What does a dispersion index of 3 tell you?

**Reference answers:** (1) Both `λ`. (2) It is Poisson with rate `λ₁ + λ₂`. (3) Strong overdispersion: counts are more variable than a Poisson allows (varying rate or clustering), so Poisson-based thresholds and intervals will be too tight.

---

## Unit 5 — Uniform and exponential distributions (`04-…md`)

### 5.1 Why ML needs this

The **uniform** distribution is the raw material of all random sampling (inverse transform, Module 09 Lesson 6) and the basis of random initialization and random hyperparameter search. The **exponential** distribution models waiting times and lifetimes and is the unique memoryless continuous distribution. Both come with parameterization traps that cause real bugs.

### 5.2 Intuition

- **Uniform(a, b):** every value in `[a, b]` is equally likely.
- **Exponential(λ):** the time until the next event when events happen at constant rate `λ`; it has *no memory*: having waited a while tells you nothing about how much longer.

### 5.3 Mechanics

| | Uniform(`a, b`) | Exponential(rate `λ`) |
|---|---|---|
| pdf | `1/(b − a)` on `[a, b]` | `λe^{−λx}`, `x ≥ 0` |
| cdf | `(x − a)/(b − a)` | `1 − e^{−λx}` |
| Mean | `(a + b)/2` | `1/λ` |
| Variance | `(b − a)²/12` | `1/λ²` |
| Quantile | `a + u(b − a)` | `−ln(1 − u)/λ` |
| MLE | `â = min xᵢ`, `b̂ = max xᵢ` (biased inward) | `λ̂ = 1/x̄` |

- **Memoryless property:** `P(X > s + t | X > s) = P(X > t)`. Constant hazard rate `λ`.
- **Minimum of independent exponentials:** `min(X₁…X_m) ~ Exponential(Σλᵢ)`; the minimizer is `i` with probability `λᵢ/Σλⱼ`.
- **Relation to Poisson:** exponential gaps ↔ Poisson counts (Lesson 4).
- **Parameterization trap:** NumPy's `rng.exponential(scale)` takes `scale = 1/λ` (the mean), not the rate; many texts use the rate. State which.
- **Uniform on `[0, 1)`:** NumPy's `rng.random()` excludes 1 and may return 0, so `log(u)` can be `-inf`; use `1 − u` or `rng.random()` clipped away from 0 when taking logs.
- **Log-uniform:** if `log₁₀ X ~ Uniform(a, b)`, then `X` spans orders of magnitude evenly; use it for scale parameters such as learning rates and regularization strengths.
- **Uniform weight initialization** (Xavier/Glorot uniform draws from `U(−√(6/(fan_in + fan_out)), +√(6/(fan_in + fan_out)))`; the limit is chosen so the variance is `2/(fan_in + fan_out)`) `[VERIFY: formula and framework conventions]` (4C-07 Lesson 8).
- **Weibull/gamma** generalize the exponential to non-constant hazard (survival analysis; out of scope).

**Worked example:** requests arrive at rate `λ = 2` per second: mean gap `0.5 s`; `P(gap > 1 s) = e⁻² ≈ 0.135`; having already waited `3 s`, `P(wait more than 1 s) = e⁻²` again.

### 5.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

# --- uniform: moments and the inverse transform
a, b = 2.0, 5.0; u = rng.uniform(a, b, size=1_000_000)
assert abs(u.mean() - (a + b) / 2) < 0.005 and abs(u.var() - (b - a) ** 2 / 12) < 0.005
# MLE of the endpoints is biased inward: expected gap at the ends is (b-a)/(n+1)
n = 20; mins = np.array([rng.uniform(a, b, n).min() for _ in range(40_000)])
print("E[min] =", mins.mean(), " theory a + (b−a)/(n+1) =", a + (b - a) / (n + 1))

# --- exponential: rate vs scale — the NumPy pitfall
lam = 2.0
x_ok = rng.exponential(scale=1 / lam, size=1_000_000); x_bug = rng.exponential(lam, size=1_000_000)   # second one treats λ as the scale
print("scale=1/λ → mean", x_ok.mean(), "(expected 0.5)   |   passing λ as scale → mean", x_bug.mean(), "(a bug: that is Exponential(rate 0.5))")
assert abs(x_ok.mean() - 1 / lam) < 0.002 and abs(x_ok.var() - 1 / lam ** 2) < 0.003

# --- memoryless property: P(X > s + t | X > s) = P(X > t)
s, t = 0.8, 0.6
cond = (x_ok[x_ok > s] > s + t).mean(); marg = (x_ok > t).mean(); theory = math.exp(-lam * t)
print(f"P(X>s+t | X>s) = {cond:.4f}   P(X>t) = {marg:.4f}   e^(-λt) = {theory:.4f}")
assert abs(cond - theory) < 0.005

# --- constant hazard: empirical hazard in bins ≈ λ
edges = np.linspace(0, 2, 9); hz = []
for lo, hi in zip(edges[:-1], edges[1:]):
    at_risk = (x_ok >= lo).sum(); events = ((x_ok >= lo) & (x_ok < hi)).sum(); hz.append((events / at_risk, hi - lo))
naive_h = [q / w for q, w in hz]; fixed_h = [-math.log(1 - q) / w for q, w in hz]
print("naive hazard (events/at-risk/width):", np.round(naive_h, 2), " ≈ (1−e^{−λw})/w =", round((1 - math.exp(-lam * 0.25)) / 0.25, 3), "(a bin-width artifact)")
print("corrected  −ln(1 − events/at-risk)/width:", np.round(fixed_h, 2), " (λ = 2: constant hazard)")

# --- minimum of independent exponentials and who wins
rates = np.array([1.0, 2.0, 3.0]); X = rng.exponential(1 / rates, size=(500_000, 3))
mn = X.min(axis=1); who = X.argmin(axis=1)
print("min mean:", mn.mean(), " theory 1/Σλ =", 1 / rates.sum(), "| win freq:", np.bincount(who) / len(who), " theory:", rates / rates.sum())

# --- MLE of the rate and its sampling error
lam_hats = np.array([1 / rng.exponential(1 / lam, 100).mean() for _ in range(20_000)])
print("λ̂: mean", lam_hats.mean(), "(biased upward for small n)  std", lam_hats.std(ddof=1), " ≈ λ/√n =", lam / 10)

# --- log-uniform vs uniform for a learning-rate search
lr_uniform = rng.uniform(1e-5, 1e-1, size=100_000); lr_log = 10 ** rng.uniform(-5, -1, size=100_000)
for name, v in (("uniform", lr_uniform), ("log-uniform", lr_log)):
    print(f"{name:12s} fraction in each decade [1e-5..1e-1]:", np.round([np.mean((v >= 10 ** k) & (v < 10 ** (k + 1))) for k in range(-5, -1)], 3))

# --- uniform in (0,1) and logs
u0 = rng.random(10_000_000); print("min of rng.random():", u0.min(), " (can be 0 → log(0) = −inf); use 1 − u for logs")
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Passing a rate where NumPy expects a scale (or vice versa) | Mean off by `λ²`; silent | State the parameterization; test the sample mean |
| `log(u)` with `u = 0` | `-inf` | Use `1 − u`, or clip |
| Using uniform sampling for scale hyperparameters | Most trials land in the largest decade (demo above) | Log-uniform |
| Estimating `[a, b]` by sample min/max and reporting as exact | Bounds too narrow, biased inward | Bias correction `(b−a)/(n+1)` or a wider interval |
| Assuming memorylessness for lifetimes with wear-out or burn-in | Wrong remaining-time predictions | Check the hazard; Weibull/gamma |
| Using the exponential for heavy-tailed waiting times | Underestimated long waits | Check the tail (log-survival plot is not a straight line) |
| Comparing `rng.exponential` results across libraries without checking the convention | Different means | Verify the mean on a large sample |
| Rate in the wrong time unit (per second vs per minute) | 60× errors | Carry units |

### 5.6 ML link

- **Random initialization and random search** (Stage 5C-03; log-uniform for learning rates and regularization).
- **Inverse-transform sampling** underlies sampling from custom CDFs (Module 11).
- **Waiting times and Poisson processes** for arrival modelling, session lengths, retry/backoff (Stage 5D-09/11, Lesson 4).
- **Survival analysis** (time-to-event models) generalizes the exponential (Stage 5B-10) `[JUDGEMENT]`.
- **Dropout/noise schedules and random augmentations** draw from uniform ranges (Stage 5C-04).

### 5.7 Lab (60 min)

1. Verify moments, quantiles, and CDFs of both distributions by simulation; implement inverse-transform samplers and a KS check.
2. Demonstrate the rate/scale bug and write a regression test that catches it.
3. Verify memorylessness numerically and show where it fails for a Weibull(`k=2`) waiting time.
4. Verify the minimum-of-exponentials results and the "who wins" probabilities.
5. Run a toy hyperparameter search (quadratic bowl in `log₁₀ lr`) with uniform vs log-uniform sampling; compare the best loss found over 20 trials, 200 repetitions.

### Check yourself (Unit 5)

1. Mean and variance of `Exponential(rate 4)`?
2. What does "memoryless" mean?
3. Why sample learning rates log-uniformly?

**Reference answers:** (1) `0.25` and `0.0625`. (2) `P(X > s + t | X > s) = P(X > t)`: the elapsed waiting time gives no information about the remaining time. (3) Good values span orders of magnitude, and log-uniform sampling spends equal effort in each decade, whereas uniform sampling puts ~90% of draws in the largest decade.

---

## Unit 6 — Normal distribution (`05-…md`)

### 6.1 Why ML needs this

The normal distribution is the default noise model in regression (so mean squared error *is* a Gaussian negative log-likelihood), the basis of standardization and normalization layers, the common choice for weight initialization and priors, and the limit that averages tend to (Module 11). It is also frequently used where it should not be: real data often has heavier tails.

### 6.2 Intuition

The bell curve: a sum of many small independent effects. It is fully described by its center `μ` and spread `σ`, with thin tails that make extreme values very rare.

### 6.3 Mechanics

- **pdf:** `f(x) = exp(−(x − μ)²/(2σ²))/(σ√(2π))`; mean `μ`, variance `σ²`. cdf `Φ((x − μ)/σ)` with `Φ(z) = ½[1 + erf(z/√2)]` (no elementary closed form; Module 06 Lesson 2).
- **Standardization:** `z = (x − μ)/σ ~ N(0, 1)`.
- **Empirical rule:** about 68.27%, 95.45%, 99.73% of mass within `±1σ, ±2σ, ±3σ`; `P(|Z| ≤ 1.96) = 0.95`.
- **Closure:** `aX + b ~ N(aμ + b, a²σ²)`; independent normals add: `N(μ₁, σ₁²) + N(μ₂, σ₂²) = N(μ₁ + μ₂, σ₁² + σ₂²)` (variances add, not standard deviations).
- **CLT intuition:** sample means of many independent draws are approximately normal (Module 11).
- **MLE:** `μ̂ = x̄`, `σ̂² = (1/n) Σ(xᵢ − x̄)²` (**divisor `n`**, i.e. `ddof=0`, biased low); the unbiased estimator uses `n − 1`.
- **Gaussian NLL:** `−ln f(x) = ½ ln(2πσ²) + (x − μ)²/(2σ²)`. For fixed `σ`, maximizing the likelihood over the mean is **exactly minimizing the squared error**: MSE is the Gaussian noise model (Module 08 Lesson 1; 4C-05).
- **Multivariate normal** `N(μ, Σ)`: pdf `∝ exp(−½ (x − μ)ᵀΣ⁻¹(x − μ))`; **Mahalanobis distance** `d² = (x − μ)ᵀΣ⁻¹(x − μ)`; sampling via the Cholesky factor `Σ = LLᵀ`: `x = μ + Lz` (Module 02 Lesson 7, 4C-01); `E[d²] = dim` `[VERIFY: χ² with d degrees of freedom]` (full treatment 4C-04).
- **Normality checks:** QQ plot (sorted data vs theoretical quantiles), skewness, excess kurtosis (`E[z⁴] − 3`, zero for a normal); formal tests are covered in Module 12.
- **Heavy tails:** real-world errors, prices, gradients, and latencies often have more extreme values than a normal predicts (Student-`t` with few degrees of freedom, log-normal, Pareto); the Gaussian then underestimates risk.
- **Outlier handling:** `z`-scores use `μ̂` and `σ̂`, which outliers themselves inflate; a **robust** `z` uses the median and `1.4826·MAD`.
- **Initialization and priors:** He/Glorot normal initializations set `σ` from fan-in/out (4C-07); a Gaussian prior on weights corresponds to L2 regularization (4C-05) `[VERIFY]`.
- **Truncation and clipping:** clipped or truncated "normals" are no longer normal (mixed point masses).

**Worked example:** heights `~ N(170, 8²)` cm: `P(155 < X < 185) = P(|Z| < 1.875) ≈ 0.939`; the 95th percentile is `170 + 1.645·8 ≈ 183.2`.

### 6.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

pdf = lambda x, mu=0.0, s=1.0: np.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))
cdf = lambda x, mu=0.0, s=1.0: 0.5 * (1 + np.vectorize(math.erf)((np.asarray(x) - mu) / (s * math.sqrt(2))))
def ppf(q, mu=0.0, s=1.0):                                        # inverse CDF by bisection (no SciPy)
    q = np.atleast_1d(q).astype(float); out = np.empty_like(q)
    for i, qi in enumerate(q):
        lo, hi = -40.0, 40.0
        for _ in range(100):
            mid = (lo + hi) / 2; lo, hi = (mid, hi) if cdf(mid) < qi else (lo, mid)
        out[i] = mu + s * (lo + hi) / 2
    return out

# --- empirical rule and standard quantiles
for k in (1, 2, 3): print(f"P(|Z| ≤ {k}) = {float(cdf(k) - cdf(-k)):.6f}")
print("97.5% quantile:", ppf(0.975)[0], "(1.959964)")
assert abs(float(cdf(1.96) - cdf(-1.96)) - 0.95) < 1e-4

# --- closure under linear maps and sums (variances add)
x = rng.normal(2.0, 3.0, 1_000_000); y = rng.normal(-1.0, 4.0, 1_000_000)
s = x + y; print("sum: mean", s.mean(), "(1)  var", s.var(), "(25 = 9 + 16, not (3+4)² = 49)")
assert abs(s.var() - 25) < 0.15 and abs((2 * x + 5).var() - 36) < 0.3

# --- MLE: variance uses 1/n (biased low), unbiased uses 1/(n−1)
small = [rng.normal(0, 1, 5) for _ in range(100_000)]
print("mean σ̂² (MLE, ddof=0):", np.mean([d.var(ddof=0) for d in small]), "  unbiased (ddof=1):", np.mean([d.var(ddof=1) for d in small]))

# --- Gaussian likelihood ↔ squared error: argmax over μ of log-likelihood equals argmin of MSE equals the mean
data = rng.normal(3.0, 2.0, 200); mus = np.linspace(0, 6, 6001)
sigma = 2.0
ll = np.array([np.sum(-0.5 * np.log(2 * np.pi * sigma ** 2) - (data - m) ** 2 / (2 * sigma ** 2)) for m in mus])
mse = np.array([np.mean((data - m) ** 2) for m in mus])
assert mus[np.argmax(ll)] == mus[np.argmin(mse)] and abs(mus[np.argmax(ll)] - data.mean()) < 1e-3

# --- multivariate normal via Cholesky; Mahalanobis² has mean = dimension
Sigma = np.array([[2.0, 1.2, 0.0], [1.2, 1.5, 0.4], [0.0, 0.4, 1.0]]); mu = np.array([1.0, -1.0, 0.5])
L = np.linalg.cholesky(Sigma); Z = rng.normal(size=(300_000, 3)); Xm = mu + Z @ L.T
assert np.allclose(np.cov(Xm, rowvar=False), Sigma, atol=0.02) and np.allclose(Xm.mean(0), mu, atol=0.01)
D = Xm - mu; d2 = np.einsum("ni,ij,nj->n", D, np.linalg.inv(Sigma), D)
print("E[Mahalanobis²] =", d2.mean(), "(dimension = 3)")

# --- QQ comparison: normal vs heavy-tailed data
def excess_kurtosis(v): z = (v - v.mean()) / v.std(); return float(np.mean(z ** 4) - 3)
norm_d = rng.normal(size=200_000); t3 = rng.standard_t(3, size=200_000)
# note: the t distribution with 3 degrees of freedom has INFINITE kurtosis, so its sample excess kurtosis is huge and unstable across seeds
for name, d in (("normal", norm_d), ("Student-t (3 dof)", t3)):
    z = (d - d.mean()) / d.std()
    print(f"{name:18s} excess kurtosis {excess_kurtosis(d):7.2f}   P(|z|>3) = {np.mean(np.abs(z) > 3):.5f}   (normal: 0.00270)")
qs = np.linspace(0.01, 0.99, 25); emp_q = np.quantile((t3 - t3.mean()) / t3.std(), qs)
print("QQ gap at the extremes (t vs normal):", emp_q[[0, -1]], ppf(qs[[0, -1]]))

# --- outliers inflate σ; a robust z-score resists
v = np.r_[rng.normal(0, 1, 200), 25.0]
z_cls = (v - v.mean()) / v.std(ddof=1); mad = 1.4826 * np.median(np.abs(v - np.median(v))); z_rob = (v - np.median(v)) / mad
print("outlier z (classic):", z_cls[-1], "  robust:", z_rob[-1])
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Assuming normality for heavy-tailed data | Tail risk underestimated (3σ events far more frequent) | QQ plot, kurtosis, tail frequencies; heavier-tailed models |
| Adding standard deviations instead of variances | Wrong spread for sums | Add variances (if independent) |
| Using `σ` and `σ²` interchangeably (library conventions) | Wrong scale (`scale` is `σ` in NumPy) | State; test the sample std |
| `ddof=0` where an unbiased estimate is needed (or vice versa for an MLE) | Biased variance | Match the estimator to its purpose |
| `z`-scores from outlier-contaminated `μ̂, σ̂` | Outliers hide themselves | Robust z (median/MAD) |
| Standardizing using statistics computed on test data | Leakage | Fit statistics on training data only |
| Computing `Φ` for extreme `z` as `1 − cdf` | Catastrophic cancellation (`1 − 1`) | Use `erfc` for tails |
| Inverting a nearly singular `Σ` (Mahalanobis) | Huge or `nan` distances | Regularize; `solve`, not `inv` |
| Treating clipped/truncated data as normal | Point masses at the limits | Censored/truncated models |

### 6.6 ML link

- **Regression noise model:** Gaussian NLL ⇔ MSE (Module 08, 14, 4C-05).
- **Standardization and normalization layers** (Stage 5A-03, 4C-07).
- **Initialization and priors:** Gaussian weights; weight decay as a Gaussian prior (4C-05, 4C-07).
- **Gaussian processes, VAEs, diffusion** use (multivariate) normals as building blocks (4C-04, 4C-10).
- **Anomaly detection:** `z`-score/Mahalanobis baselines and their failure on heavy tails (Stage 5B-06).
- **Confidence intervals** via normal approximation of means (Module 11–12).

### 6.7 Lab (75 min)

1. Implement the pdf, cdf (via `erf`), and inverse cdf (bisection); verify the empirical rule and the `1.96` quantile.
2. Verify the sum/linear-transformation rules by simulation; show the `(σ₁ + σ₂)²` error.
3. Demonstrate the log-likelihood ↔ MSE equivalence on three datasets; extend to the weighted case (heteroscedastic `σᵢ`) and say what loss that implies.
4. Multivariate lab: sample via Cholesky, verify the covariance, compute Mahalanobis distances and flag outliers at the `χ²₃` 99% cut-off; compare with a per-feature `z`-score rule on correlated data.
5. Tail audit: for five datasets (normal, `t₃`, log-normal, exponential, a mixture), compute excess kurtosis and tail frequencies beyond `3σ`; decide where the normal model is safe.

### Check yourself (Unit 6)

1. What is `Var(X + Y)` for independent `N(0, 9)` and `N(0, 16)`?
2. What loss does Gaussian noise imply, and why?
3. Why does the MLE variance use `1/n`?

**Reference answers:** (1) `25`. (2) Squared error: the Gaussian negative log-likelihood is `const + (x − μ)²/(2σ²)`, so maximizing likelihood minimizes squared error. (3) It is the exact maximizer of the likelihood; it is biased low, and `1/(n−1)` removes the bias.

---

## Unit 7 — Beta and Dirichlet distributions (in outline) (`06-…md`)

### 7.1 Why ML needs this

When a *probability itself* is uncertain (a click-through rate, a class prior, a model's probability estimate), the natural distribution over it is **Beta** (two outcomes) or **Dirichlet** (many outcomes). They are the conjugate priors for Bernoulli/binomial and categorical/multinomial data, so Bayesian updating is just adding counts, and they explain Laplace smoothing. This lesson is an outline: enough to use them correctly, with full inference in 4C-05.

### 7.2 Intuition

A **Beta(α, β)** is a distribution over `[0, 1]`; think of `α − 1` pseudo-successes and `β − 1` pseudo-failures seen before the data. After observing `k` successes and `n − k` failures the belief becomes **Beta(α + k, β + n − k)**: counts simply add. A **Dirichlet(α₁…α_K)** does the same for `K` category probabilities that sum to 1.

### 7.3 Mechanics

- **Beta(α, β), `α, β > 0`:** pdf `x^{α−1}(1−x)^{β−1}/B(α, β)` on `(0, 1)`, with `B(α, β) = Γ(α)Γ(β)/Γ(α+β)`.
  - Mean `α/(α + β)`; variance `αβ/((α + β)²(α + β + 1))`; **concentration** `α + β` controls spread.
  - Mode `(α − 1)/(α + β − 2)` for `α, β > 1`.
  - Shapes: `α = β = 1` uniform; `α, β < 1` U-shaped (mass near 0 and 1; the pdf is unbounded at the ends); `α, β > 1` unimodal bell; `α > β` skews toward 1.
- **Conjugacy (Bernoulli/binomial):** prior `Beta(α, β)` × likelihood of `k` successes in `n` ⇒ posterior `Beta(α + k, β + n − k)` (posterior ∝ `p^{α+k−1}(1−p)^{β+n−k−1}`).
  - **Posterior mean** `(α + k)/(α + β + n)`: a compromise between the prior mean and `k/n`, weighted by `α + β` vs `n`.
  - **Laplace smoothing = Beta(1,1) prior:** `(k + 1)/(n + 2)`.
  - **Credible interval:** central interval from posterior quantiles (analytic via numerical inversion or sampling); distinct from a frequentist confidence interval `[VERIFY: interpretation]`.
- **Dirichlet(α₁…α_K):** density `Π xᵢ^{αᵢ−1}/B(α)` on the simplex (`xᵢ ≥ 0`, `Σxᵢ = 1`). With `α₀ = Σαᵢ`: `E[xᵢ] = αᵢ/α₀`, `Var(xᵢ) = αᵢ(α₀ − αᵢ)/(α₀²(α₀ + 1))`; `α = 1` is uniform over the simplex; **`α < 1` favours sparse vectors** (most mass on a few categories).
- **Conjugacy (categorical/multinomial):** prior `Dirichlet(α)` + counts `k` ⇒ posterior `Dirichlet(α + k)`; posterior mean `(αᵢ + kᵢ)/(α₀ + n)` = additive smoothing with `α` (Lesson 2, Module 09).
- **Sampling a Dirichlet:** draw independent `gᵢ ~ Gamma(αᵢ, 1)` and set `xᵢ = gᵢ/Σgⱼ` (also `rng.dirichlet`); for tiny `αᵢ` many `gᵢ` underflow to 0: work in log space or accept exact zeros `[VERIFY]`.
- **Relations:** Beta is Dirichlet with `K = 2`; Beta(`α`, `β`) arises as the ratio `G₁/(G₁ + G₂)` of Gammas.
- **Uses in ML:** Bayesian A/B testing (posterior of two conversion rates, Module 12), smoothing categorical estimates, **Thompson sampling** for bandits (Beta posteriors, Stage 5B-13), **topic models (LDA)** place Dirichlet priors on document–topic and topic–word distributions (Stage 5A-10/5B `[JUDGEMENT]`), and priors over class probabilities.
- **Outline only here:** hierarchical models, Dirichlet processes, and variational inference belong to 4C-05/4C-10.

**Worked example:** prior `Beta(2, 2)` (mean 0.5), data: 7 successes in 10 trials ⇒ posterior `Beta(9, 5)`, mean `9/14 ≈ 0.643` (MLE `0.7`, prior mean `0.5`: the posterior sits between them).

### 7.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def log_beta_fn(a, b): return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
def beta_pdf(x, a, b):
    x = np.asarray(x, float); out = np.zeros_like(x); m = (x > 0) & (x < 1)
    out[m] = np.exp((a - 1) * np.log(x[m]) + (b - 1) * np.log1p(-x[m]) - log_beta_fn(a, b)); return out
def trapezoid(y, x): return float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2))

# --- normalization and moments (use a, b ≥ 1 where the pdf is bounded)
xs = np.linspace(0, 1, 200_001)
for a, b in ((1, 1), (2, 5), (5, 2), (3, 3)):
    f = beta_pdf(xs, a, b); mean = trapezoid(xs * f, xs); var = trapezoid((xs - mean) ** 2 * f, xs)
    assert abs(trapezoid(f, xs) - 1) < 1e-4 and abs(mean - a / (a + b)) < 1e-4
    assert abs(var - a * b / ((a + b) ** 2 * (a + b + 1))) < 1e-4

# --- conjugate update: posterior ∝ prior × likelihood equals Beta(α+k, β+n−k) (checked on a grid)
a0, b0, k, n = 2.0, 2.0, 7, 10
grid = np.linspace(1e-6, 1 - 1e-6, 100_001)
unnorm = beta_pdf(grid, a0, b0) * grid ** k * (1 - grid) ** (n - k); post_num = unnorm / trapezoid(unnorm, grid)
assert np.max(np.abs(post_num - beta_pdf(grid, a0 + k, b0 + n - k))) < 1e-3
print("posterior mean:", (a0 + k) / (a0 + b0 + n), " MLE:", k / n, " prior mean:", a0 / (a0 + b0))

# --- Laplace smoothing is the Beta(1,1) posterior mean
for k_, n_ in ((0, 5), (3, 5), (5, 5)): assert np.isclose((k_ + 1) / (n_ + 2), (1 + k_) / (1 + 1 + n_))

# --- credible interval from samples, and a frequentist-style Wald interval for contrast
post = rng.beta(a0 + k, b0 + n - k, size=400_000); lo, hi = np.quantile(post, [0.025, 0.975])
print(f"95% credible interval for p: [{lo:.3f}, {hi:.3f}]   Wald: {k / n:.2f} ± {1.96 * math.sqrt(0.7 * 0.3 / n):.3f}")

# --- sequential updating: counts just add
a_, b_ = 1.0, 1.0
for flip in (rng.random(200) < 0.3): a_ += flip; b_ += 1 - flip
print("after 200 flips: Beta(%d, %d), mean %.3f (true 0.3)" % (a_, b_, a_ / (a_ + b_)))

# --- Dirichlet via normalized Gammas vs NumPy; moments; sparsity for α < 1
alpha = np.array([2.0, 3.0, 5.0]); a0_ = alpha.sum(); N = 300_000
g = rng.gamma(alpha, size=(N, 3)); D = g / g.sum(axis=1, keepdims=True)
print("mean:", D.mean(0), " theory:", alpha / a0_)
print("var :", D.var(0), " theory:", alpha * (a0_ - alpha) / (a0_ ** 2 * (a0_ + 1)))
assert np.allclose(D.mean(0), rng.dirichlet(alpha, size=N).mean(0), atol=0.005)
for a_s in (0.1, 1.0, 10.0):
    S = rng.dirichlet(np.full(10, a_s), size=50_000)
    print(f"α={a_s:5}: mean largest component = {S.max(axis=1).mean():.3f}  (uniform-ish vs sparse)")

# --- Dirichlet–multinomial update = additive smoothing
counts = np.array([7, 3, 0]); alpha_prior = np.array([1.0, 1.0, 1.0])
print("posterior mean:", (alpha_prior + counts) / (alpha_prior.sum() + counts.sum()), " MLE:", counts / counts.sum())
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `α` or `β ≤ 0` | Invalid distribution; `nan` | Validate parameters |
| Reading the pdf value at 0/1 for `α < 1` as an error | Infinite density is legitimate there | Probability is area; inspect the CDF |
| Confusing mean and mode | Reporting the wrong "most likely" value | `α/(α+β)` vs `(α−1)/(α+β−2)` |
| An overly strong prior on small data | Posterior ignores the data | Check `α + β` vs `n`; prior-sensitivity analysis |
| Believing "conjugate" means "correct prior" | Convenient but wrong model | Conjugacy is a computational convenience |
| Naive `log(x)` of Dirichlet samples with tiny `α` | `-inf` from exact zeros | Log-space samplers; clip with care |
| Using the Beta posterior for dependent trials | Overconfident interval | Count independent units (Lesson 2 overdispersion) |
| Reporting a credible interval as if it were a confidence interval | Misstated guarantees | State the interpretation |
| Mixing Beta mean/concentration and `(α, β)` parameterizations | Wrong shape | Convert explicitly: `α = μκ`, `β = (1−μ)κ` |

### 7.6 ML link

- **Smoothing in naive Bayes and language models** is a Dirichlet prior (Module 09 Project 2; Lesson 2).
- **Bayesian A/B testing and Thompson sampling** use Beta posteriors (Module 12, Stage 5B-10/13).
- **Topic models** use Dirichlet priors (Stage 5A-10/5B `[JUDGEMENT]`).
- **Conjugate updating** is the simplest instance of Bayesian inference (4C-05).
- **Calibration and uncertainty over probabilities** (Stage 5B-02/04) build on distributions over `[0, 1]`.

### 7.7 Lab (75 min)

1. Verify the Beta pdf normalization and moments for six `(α, β)` pairs; plot the shape family and describe each.
2. Conjugate update: verify numerically that prior × likelihood normalizes to `Beta(α + k, β + n − k)`; show the posterior mean moving from the prior mean to the MLE as `n` grows.
3. Compare the Beta credible interval with Wald, Wilson, and Clopper–Pearson at `k = 0, 3, 50` of `n = 100`.
4. Sample a Dirichlet via Gammas; verify moments; show sparsity as `α` varies; compute the posterior after multinomial counts.
5. Thompson-sampling toy: three Bernoulli arms with Beta posteriors; compare cumulative regret with random and greedy strategies over 2,000 rounds (your numbers, many seeds).

### Check yourself (Unit 7)

1. What is the posterior after `k` successes in `n` trials with a `Beta(α, β)` prior?
2. What prior gives Laplace smoothing?
3. What does `α < 1` do to a Dirichlet?

**Reference answers:** (1) `Beta(α + k, β + n − k)`. (2) `Beta(1, 1)` (uniform) for two outcomes, or `Dirichlet(1, …, 1)`. (3) It favours sparse probability vectors: most mass on a few categories.

---

## Unit 8 — Practice question bank (`practice-questions.md`)

### 8.1 Structure

About 50 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 12 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, "which distribution?", runnable code, and fitting/diagnosis judgement.

### 8.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 8.3 Seed items

**Q1 [L1] Choose.** Which distribution models the number of correct predictions among 200 independent test items? → Binomial(200, p).
**Q2 [L2] Binomial.** `P(exactly 2 heads in 5 fair flips)`? → `C(5,2)/32 = 10/32 = 0.3125`.
**Q3 [L2] Softmax.** Logits `(0, 0, 0)`; probabilities? Cross-entropy for class 1? → Uniform `1/3`; `ln 3 ≈ 1.099`.
**Q4 [L2] Gradient.** Softmax cross-entropy with `p = (0.7, 0.2, 0.1)`, label 2 (0-indexed 1). `∂L/∂z`? → `(0.7, −0.8, 0.1)`.
**Q5 [L2] Poisson.** `λ = 3`; `P(N = 0)` and `P(N ≥ 1)`? → `e⁻³ ≈ 0.0498`; `0.9502`.
**Q6 [L2] Exponential.** Rate 0.5 per minute: mean waiting time and `P(wait > 4)`? → `2` min; `e⁻² ≈ 0.135`.
**Q7 [L2] Normal.** `X ~ N(100, 15²)`: `P(X > 130)`? → `P(Z > 2) ≈ 0.0228`.
**Q8 [L2] Beta.** Prior `Beta(1, 1)`, data 3 successes in 4 trials: posterior and mean? → `Beta(4, 2)`, mean `2/3`.
**Q9 [L2] Variance of a sum.** `X ~ N(0, 4)`, `Y ~ N(0, 9)` independent. Distribution of `X − Y`? → `N(0, 13)`.
**Q10 [L3] Debug.** `rng.exponential(5)` is meant to have rate 5 but its sample mean is ≈ 5. → NumPy takes the *scale* `1/rate`; use `rng.exponential(1/5)`.
**Q11 [L3] Debug.** `np.log(softmax(z))` returns `-inf` for one class with logits around ±800. → Underflow of the softmax value; use `log_softmax`.
**Q12 [L3] Analysis.** Hourly error counts have mean 4 and variance 14. What does it imply for a Poisson-based alert? → Overdispersion (index 3.5): the alert's real false-alarm rate is far above the design level; use a negative binomial or empirical thresholds.
**Q13 [L3] Analysis.** A 95% Wald interval for `p̂ = 0` with `n = 40` is `[0, 0]`. What is wrong and what do you use? → The normal approximation fails at `p̂ = 0`; use Wilson/Clopper–Pearson (upper bound ≈ `3/n` by the rule of three).
**Q14 [L3] Analysis.** `P(|z| > 3)` is 1.1% in your residuals but 0.27% under a normal model. → Heavy tails; the Gaussian model underestimates extremes; consider Student-`t` or robust methods.
**Q15 [L4] Design.** Choose a distribution for each target: daily page views, time between failures, probability a coin is fair, a 5-class label, measurement noise. → Poisson/negative binomial (check dispersion); exponential/Weibull; Beta; categorical; Gaussian (check tails).
**Q16 [L4] Design.** You need a hyperparameter search over learning rate `10⁻⁵…10⁻¹` and weight decay `10⁻⁶…10⁻²`. → Log-uniform sampling for both; seeded; record the sampled values.
**Q17 [L4] Design.** Build an alert for request counts (mean 20/min) with a false-alarm budget of 1 per week. → Use an exact Poisson (or overdispersed) tail threshold with `α ≈ 1/10 080` per minute, verify on historical data for dispersion and seasonality, and monitor the realized alert rate.
**Q18 [L4] Design.** Estimate a click-through rate for an item with 3 views and 0 clicks. → Beta posterior (e.g., `Beta(1 + 0, 1 + 3)` or an informed prior from similar items) rather than `0/3`; report a credible interval.

### 8.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Bernoulli, binomial | 2 | 2 | 2 | 1 |
| Categorical, multinomial, softmax | 2 | 3 | 3 | 1 |
| Poisson | 2 | 2 | 2 | 2 |
| Uniform, exponential | 2 | 2 | 2 | 1 |
| Normal | 2 | 3 | 2 | 1 |
| Beta, Dirichlet | 2 | 2 | 1 | 2 |

### Check yourself (Unit 8)

1. Why does the seed set include a "which distribution?" design item?
2. Which items need runnable code?

**Reference answers:** (1) Choosing the right family is the modelling decision that determines the loss, interval, and failure mode. (2) All L3 items and any whose answer depends on floating-point or simulation behaviour.

---

## Unit 9 — Project index (`Projects/README.md`)

### 9.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Distribution gallery and fitting | From-scratch pmf/pdf/cdf/sampler/MLE for the module's families; goodness-of-fit with honest p-values; misspecification detection | 1–6 | 8–9 h |
| 2 | Poisson event-rate simulator | Poisson-process simulation, exact thresholds, overdispersion failure, interval coverage | 3, 4 | 6–7 h |

Order: 1 → 2 (Project 2 reuses Project 1's Poisson/exponential implementations and the bootstrap helper). Outputs feed `mlmath/dists.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D10) and notebook `10_distributions.ipynb`. The softmax and log-sum-exp code is reused in Module 11 and Module 13.

### 9.2 Data policy

**No downloads.** All data are generated by the project's own samplers with known parameters (so fitted parameters can be compared with the truth). You may additionally run the fitting tools on any dataset you already have locally; keep it out of the repository and tests `[VERIFY: licence]`.

### 9.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (normalization, moments, simulation agreement, MLE accuracy) | 30 |
| Failure-mode handling (overflow, edge parameters, misspecification, zero counts) | 15 |
| Reproducibility (seeded, pinned, clean venv, no downloads) | 15 |
| Explanation and statistical honesty (standard errors, calibrated p-values, scoped claims) | 15 |
| Code quality (types, parameter validation, docstrings stating parameterizations) | 15 |
| ML connection paragraph | 10 |

### 9.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 9)

1. What does Project 2 reuse from Project 1?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The Poisson/exponential implementations and the parametric-bootstrap helper. (2) D10 (`mlmath/dists.py`).

---

## Unit 10 — Project: Distribution gallery and fitting (`Projects/01-…md`)

### 10.1 Brief

Build `distgallery`: from-scratch implementations of Bernoulli, binomial, categorical, Poisson, uniform, exponential, normal, and Beta distributions (pmf/pdf, cdf, sampler, moments, MLE or method-of-moments), plus a **fitting and goodness-of-fit** toolkit that selects among candidate families and **detects misspecification** honestly.

**Industry framing:** fitting a distribution is routine (latency models, count models, noise models); the professional part is checking the fit and knowing how it fails. The toolkit's job is to make a bad fit *loud*.

### 10.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Parameter validation | Every distribution validates parameters (`p ∈ [0,1]`, `λ > 0`, `σ > 0`, `α, β > 0`, …) with clear errors; docstrings state the parameterization (rate vs scale, `σ` vs `σ²`) |
| R2 | pmf/pdf in log space | `logpdf`/`logpmf` for each family (using `math.lgamma`); no overflow for large `n`, `k`; edge parameters handled |
| R3 | cdf and quantile | Closed form where available (exponential, uniform), `erf` for the normal, summation for discrete, bisection inverse for the normal and Beta (numeric integration of the pdf, Module 06) |
| R4 | Samplers | Own inverse-transform samplers where possible (exponential, uniform, categorical), NumPy generators for the rest; each validated by KS (continuous) or a chi-square-style statistic (discrete) |
| R5 | Moments | Analytic mean/variance, compared with sample moments on `N = 10⁶` within `4·SE` |
| R6 | Estimators | MLE: Bernoulli, binomial `p`, categorical, Poisson, exponential, normal (`ddof=0`), uniform (min/max); method of moments for Beta; each with a standard error (analytic or bootstrap) |
| R7 | Consistency study | Estimation error vs sample size for each estimator (log-log slope near `−½` for regular cases); the uniform endpoint MLE converges faster (`≈ −1`): report and explain |
| R8 | Goodness of fit | KS statistic (continuous) and Pearson chi-square (discrete, with bins merged so expected counts ≥ 5); **p-values by parametric bootstrap** (refit on every bootstrap sample); verify that p-values are approximately uniform when the model is true (empirical rejection rate at 5% within `[0.02, 0.09]`) |
| R9 | Model selection | AIC/log-likelihood comparison across candidate families on data from known sources (Poisson vs negative-binomial-like overdispersed counts; normal vs Student-`t` vs Laplace); report how often the true family wins vs sample size |
| R10 | Misspecification demos | (a) overdispersed counts fit by Poisson: dispersion index and GOF rejection; (b) heavy-tailed data fit by a normal: kurtosis and tail frequency; (c) clustered binary data fit by a binomial |
| R11 | Visual gallery | Headless figure grid: pmf/pdf shapes across parameters, QQ plots for good and bad fits, ECDF vs fitted CDF |
| R12 | Report | `REPORT.md`: a table per family (formula, moments, estimator, SE), the calibration check of the bootstrap p-values, the model-selection table, and a "which distribution when" decision guide backed by your results |

### 10.3 Layout and starter

```
distgallery/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/distgallery/{__init__,discrete,continuous,fit,gof,select}.py
├── tests/{test_discrete,test_continuous,test_fit,test_gof}.py
├── notebooks/10_distribution_gallery.ipynb
└── results/
```

```python
# src/distgallery/continuous.py
import math
import numpy as np

def _check(cond, msg):
    if not cond: raise ValueError(msg)

class Normal:
    """Normal(mu, sigma): sigma is the STANDARD DEVIATION (not the variance)."""
    def __init__(self, mu=0.0, sigma=1.0): _check(sigma > 0, "sigma must be > 0"); self.mu, self.sigma = mu, sigma
    def logpdf(self, x): x = np.asarray(x, float); return -0.5 * np.log(2 * math.pi * self.sigma ** 2) - (x - self.mu) ** 2 / (2 * self.sigma ** 2)
    def cdf(self, x): return 0.5 * (1 + np.vectorize(math.erf)((np.asarray(x) - self.mu) / (self.sigma * math.sqrt(2))))
    def sample(self, rng, n): return rng.normal(self.mu, self.sigma, n)
    mean = property(lambda s: s.mu); var = property(lambda s: s.sigma ** 2)
    @staticmethod
    def fit(x): x = np.asarray(x, float); return Normal(x.mean(), x.std(ddof=0))            # MLE: divisor n

class Exponential:
    """Exponential(rate): rate = 1/mean. (NumPy's `scale` is 1/rate.)"""
    def __init__(self, rate=1.0): _check(rate > 0, "rate must be > 0"); self.rate = rate
    def logpdf(self, x): x = np.asarray(x, float); return np.where(x >= 0, math.log(self.rate) - self.rate * x, -np.inf)
    def cdf(self, x): x = np.asarray(x, float); return np.where(x >= 0, 1 - np.exp(-self.rate * np.maximum(x, 0)), 0.0)
    def ppf(self, u): return -np.log1p(-np.asarray(u, float)) / self.rate
    def sample(self, rng, n): return self.ppf(rng.random(n))                                 # own inverse transform
    mean = property(lambda s: 1 / s.rate); var = property(lambda s: 1 / s.rate ** 2)
    @staticmethod
    def fit(x): return Exponential(1.0 / np.mean(x))

class Uniform:
    def __init__(self, a=0.0, b=1.0): _check(b > a, "need b > a"); self.a, self.b = a, b
    def logpdf(self, x): x = np.asarray(x, float); return np.where((x >= self.a) & (x <= self.b), -math.log(self.b - self.a), -np.inf)
    def cdf(self, x): return np.clip((np.asarray(x, float) - self.a) / (self.b - self.a), 0, 1)
    def sample(self, rng, n): return self.a + (self.b - self.a) * rng.random(n)
    mean = property(lambda s: (s.a + s.b) / 2); var = property(lambda s: (s.b - s.a) ** 2 / 12)
    @staticmethod
    def fit(x): x = np.asarray(x, float); return Uniform(x.min(), x.max())
```

```python
# src/distgallery/discrete.py
import math
import numpy as np

class Poisson:
    def __init__(self, lam): 
        if lam <= 0: raise ValueError("lam must be > 0")
        self.lam = lam
    def logpmf(self, k): k = np.asarray(k); return k * math.log(self.lam) - self.lam - np.vectorize(math.lgamma)(k + 1.0)
    def pmf(self, k): return np.exp(self.logpmf(k))
    def cdf(self, k): return np.array([sum(math.exp(j * math.log(self.lam) - self.lam - math.lgamma(j + 1)) for j in range(int(ki) + 1)) for ki in np.atleast_1d(k)])
    def sample(self, rng, n): return rng.poisson(self.lam, n)
    mean = property(lambda s: s.lam); var = property(lambda s: s.lam)
    @staticmethod
    def fit(x): return Poisson(float(np.mean(x)))

class Binomial:
    def __init__(self, n, p):
        if n < 1 or not (0 <= p <= 1): raise ValueError("need n ≥ 1 and 0 ≤ p ≤ 1")
        self.n, self.p = int(n), p
    def logpmf(self, k):
        k = np.asarray(k); n, p = self.n, self.p
        if p in (0.0, 1.0): return np.where(k == (0 if p == 0 else n), 0.0, -np.inf)
        lg = np.vectorize(math.lgamma)
        return lg(n + 1.0) - lg(k + 1.0) - lg(n - k + 1.0) + k * math.log(p) + (n - k) * math.log1p(-p)
    def pmf(self, k): return np.exp(self.logpmf(k))
    def sample(self, rng, n): return rng.binomial(self.n, self.p, n)
    mean = property(lambda s: s.n * s.p); var = property(lambda s: s.n * s.p * (1 - s.p))
```

```python
# src/distgallery/gof.py
import numpy as np

def ks_statistic(x, cdf):
    s = np.sort(np.asarray(x, float)); n = len(s); F = cdf(s)
    return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))

def parametric_bootstrap_pvalue(x, fit, stat, B=200, seed=0):
    """P(stat* ≥ stat_obs) with parameters RE-ESTIMATED on every bootstrap sample (using the same fit as the data)."""
    rng = np.random.default_rng(seed); x = np.asarray(x); model = fit(x); obs = stat(x, model)
    boots = np.empty(B)
    for b in range(B):
        xb = model.sample(rng, len(x)); boots[b] = stat(xb, fit(xb))
    return float((1 + np.sum(boots >= obs)) / (B + 1)), obs
```

```python
# tests/test_gof.py
import numpy as np
from distgallery.continuous import Normal, Exponential
from distgallery.gof import ks_statistic, parametric_bootstrap_pvalue

ks_stat = lambda x, m: ks_statistic(x, m.cdf)

def test_pvalue_roughly_calibrated_under_the_true_model():
    rng = np.random.default_rng(0); rejections = 0; reps = 150
    for r in range(reps):
        x = rng.normal(2.0, 3.0, 100)
        p, _ = parametric_bootstrap_pvalue(x, Normal.fit, ks_stat, B=120, seed=r)
        rejections += (p < 0.05)
    assert 0.01 <= rejections / reps <= 0.11              # [VERIFY] bounds from your own run (Monte-Carlo noise with 150 reps)

def test_bad_model_is_rejected():
    rng = np.random.default_rng(1); x = rng.standard_t(2, 400)
    p, _ = parametric_bootstrap_pvalue(x, Normal.fit, ks_stat, B=150, seed=1)
    assert p < 0.05

def test_sampler_matches_cdf():
    rng = np.random.default_rng(2); m = Exponential(1.7); x = m.sample(rng, 100_000)
    assert ks_statistic(x, m.cdf) < 0.006
```

`[VERIFY]` In a seeded run (300 repetitions, `B = 100`) the measured rejection rate was 4.3%, inside the test's bounds; a parametric-bootstrap KS test with re-estimated parameters is *calibrated*, unlike the textbook KS test with plugged-in parameters, which rejected 0% in the same experiment. Record your own measured rate in the report.

### 10.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Each pmf/pdf normalizes (sum/integral within `1e-8`); cdf matches closed forms; invalid parameters raise `ValueError`; `n = 10⁵` binomial `logpmf` finite |
| M2 | R4–R5 | KS/chi-square validation of every sampler passes; sample moments within `4·SE` of analytic moments |
| M3 | R6–R7 | MLEs recover true parameters (error table over `n ∈ {20, …, 20 000}`); fitted slopes reported; the uniform-endpoint exception explained |
| M4 | R8 | Bootstrap p-values calibrated (empirical 5% rejection rate in `[0.02, 0.09]` over ≥ 300 repetitions) and powerful against the misspecification demos |
| M5 | R9–R10 | Model-selection table (true-family win rate vs `n`); three misspecification demos with numbers |
| M6 | R11–R12 | One script regenerates all figures/tables headlessly; `REPORT.md` decision guide cites your measured evidence |

### 10.5 Statistical-honesty requirements

- Every fitted parameter appears with a **standard error or bootstrap interval** and the sample size.
- State clearly that **a non-rejected fit is not proof** the model is right (limited power at small `n`): show the power curve for one misspecification.
- Report the **calibration of your own p-values**, not just the nominal level.
- When AIC picks the true family only part of the time, report the fraction: do not present one winning run.

### 10.6 Failure modes to demonstrate

Parameterization mix-ups (rate/scale, `σ`/`σ²`); `log(0)` at the edge of the support; overflow in `C(n, k)`; KS with plugged-in parameters (conservative p-values); chi-square with expected counts below 5; overdispersed counts fit by Poisson; heavy tails fit by a normal; MLE for uniform endpoints biased inward; fitting a discrete variable with a continuous density (ties).

### 10.7 Stretch goals

1. Negative binomial (gamma–Poisson) with method-of-moments and MLE; show it fixes the overdispersion demo.
2. Student-`t` and Laplace families for robust regression noise; link Laplace to MAE and Student-`t` to heavy-tailed losses (Module 08).
3. Mixture of two normals fit by a simple EM loop (preview of 4C-05).
4. Beta MLE by Newton iterations on the digamma equations (implement `digamma` numerically) `[VERIFY: equations]`.
5. Bayesian version: conjugate posteriors (Beta, Gamma–Poisson, Normal-known-variance) with credible intervals compared against bootstrap intervals.

### 10.8 ML connection (README prompt)

For each family, name one ML situation, the loss function it implies, and the diagnostic that reveals when the family is wrong; then describe how you would use the gallery to choose a noise model for a regression target and a count model for an event stream.

### Check yourself (Unit 10)

1. Why must a parametric-bootstrap goodness-of-fit test re-estimate the parameters on every bootstrap sample?
2. What does a non-significant goodness-of-fit result tell you?

**Reference answers:** (1) The observed statistic used fitted parameters; the null distribution must reflect the same fitting step, otherwise p-values are miscalibrated (too conservative). (2) Only that the data do not contradict the model at this sample size; with small `n` the test has low power, so it is not evidence the model is correct.

---

## Unit 11 — Project: Poisson event-rate simulator (`Projects/02-…md`)

### 11.1 Brief

Build `poissim`: a simulator of event streams (homogeneous and time-varying Poisson processes, plus overdispersed traffic) and a monitoring toolkit that sets **alert thresholds from exact Poisson tails**, estimates rates with **exact confidence intervals**, and quantifies how badly the Poisson assumption fails under overdispersion, seasonality, and bursts.

**Industry framing:** most request-rate, error-rate, and defect-rate alerts are Poisson models in disguise. The deliverable validates that the alert actually fires at its design false-alarm rate on realistic traffic, and shows how it breaks when it does not.

### 11.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Homogeneous process | Simulate by exponential gaps and by per-window `Poisson(λΔt)` draws; show equivalence of count distributions (KS/chi-square) |
| R2 | Time-varying rate | **Thinning (Lewis–Shedler):** simulate a non-homogeneous process with `λ(t) ≤ λ_max`; verify that the expected count equals `∫λ(t)dt` `[VERIFY: algorithm]` |
| R3 | Superposition and splitting | Verify numerically that merged streams are Poisson with summed rates and that random thinning gives Poisson with `qλ` |
| R4 | Exact tails | `poisson_sf(k, λ)`, `poisson_cdf`; threshold function `threshold(λ, α)` giving the smallest `k` with `P(N ≥ k) ≤ α`; compare with the normal approximation across `λ` |
| R5 | Alert simulation | Monte-Carlo the false-alarm rate per window for the Poisson threshold under (a) true Poisson traffic, (b) overdispersed traffic (gamma–Poisson with several dispersion levels), (c) seasonal rate (diurnal sinusoid) with a constant `λ̂`; report rates with standard errors |
| R6 | Dispersion diagnostics | Dispersion index with a simulation-calibrated test (parametric bootstrap under the Poisson null); show its power vs dispersion level and sample size |
| R7 | Exact rate interval | Garwood interval for `λ` from `k` events (inverting the Poisson cdf by bisection; relation to the Gamma distribution as a `[VERIFY]` cross-check); coverage study over `λ ∈ {0.5, 2, 10, 50}` |
| R8 | Detection delay | After a step change in the rate (`λ → cλ`), simulate how many windows pass before a threshold alert fires (distribution of delay), for `c ∈ {1.5, 2, 3}`; trade-off with the false-alarm budget |
| R9 | Robust alternative | Empirical-quantile or negative-binomial threshold fit on a training window; show it restores the design false-alarm rate on overdispersed traffic |
| R10 | Reproducibility | Seeded streams; `SeedSequence.spawn` for independent replicates `[VERIFY: API]`; same seed ⇒ identical results |
| R11 | Report | `REPORT.md`: tables of design vs realized false-alarm rates, coverage of the exact interval, detection-delay distributions, and an "alerting runbook" |

### 11.3 Layout and starter

```
poissim/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/poissim/{__init__,process,tails,alerts,intervals,diagnostics}.py
├── tests/{test_process,test_tails,test_alerts,test_intervals}.py
├── notebooks/10_poisson_simulator.ipynb
└── results/
```

```python
# src/poissim/tails.py
import math

def poisson_logpmf(k, lam): return k * math.log(lam) - lam - math.lgamma(k + 1)
def poisson_cdf(k, lam):
    if k < 0: return 0.0
    return min(1.0, sum(math.exp(poisson_logpmf(j, lam)) for j in range(k + 1)))
def poisson_sf_ge(k, lam):                 # P(N ≥ k), summing the upper tail directly for accuracy at small tails
    if k <= 0: return 1.0
    total, j = 0.0, k
    while True:
        term = math.exp(poisson_logpmf(j, lam)); total += term; j += 1
        if term < 1e-18 * total and j > lam: break
    return total
def threshold(lam, alpha):
    k = max(0, int(lam))
    while poisson_sf_ge(k, lam) > alpha: k += 1
    return k
```

```python
# src/poissim/process.py
import numpy as np

def homogeneous_counts(rate, T, windows, rng, method="gaps"):
    if method == "poisson": return rng.poisson(rate * T, size=windows)
    out = np.zeros(windows, int)
    for w in range(windows):
        t, c = 0.0, 0
        while True:
            t += rng.exponential(1 / rate)                         # NumPy: scale = 1/rate
            if t > T: break
            c += 1
        out[w] = c
    return out

def thinning(rate_fn, rate_max, T, rng):
    """Lewis–Shedler thinning: event times of a non-homogeneous Poisson process on [0, T]."""
    t, times = 0.0, []
    while True:
        t += rng.exponential(1 / rate_max)
        if t > T: return np.array(times)
        if rng.random() < rate_fn(t) / rate_max: times.append(t)

def overdispersed_counts(mean, shape, windows, rng):
    lam = rng.gamma(shape, mean / shape, size=windows)             # window-level rate with mean `mean`, var mean²/shape
    return rng.poisson(lam)
```

```python
# src/poissim/intervals.py
from .tails import poisson_cdf, poisson_sf_ge

def garwood(k, alpha=0.05):
    def bisect(f, lo, hi):
        for _ in range(100):
            mid = (lo + hi) / 2; lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else bisect(lambda lam: alpha / 2 - poisson_sf_ge(k, lam) , 1e-12, k + 10 * (k ** 0.5) + 20)
    upper = bisect(lambda lam: poisson_cdf(k, lam) - alpha / 2, 1e-12, k + 10 * (k ** 0.5) + 20)
    return lower, upper
```

```python
# tests/test_tails.py
import numpy as np
from poissim.tails import poisson_cdf, poisson_sf_ge, threshold
from poissim.process import homogeneous_counts, overdispersed_counts, thinning
from poissim.intervals import garwood

def test_threshold_meets_design_false_alarm_rate():
    lam, alpha = 20.0, 1e-3; k = threshold(lam, alpha)
    assert poisson_sf_ge(k, lam) <= alpha < poisson_sf_ge(k - 1, lam)

def test_poisson_counts_have_mean_equal_variance():
    c = homogeneous_counts(2.0, 3.0, 20_000, np.random.default_rng(0)); assert abs(c.mean() - 6) < 0.1 and abs(c.var() - 6) < 0.3

def test_overdispersion_inflates_false_alarms():
    rng = np.random.default_rng(1); lam = 20.0; k = threshold(lam, 1e-3)
    ok = (rng.poisson(lam, 400_000) >= k).mean(); over = (overdispersed_counts(lam, 4.0, 400_000, rng) >= k).mean()
    assert ok < 3e-3 and over > 5 * ok

def test_thinning_expected_count():
    rng = np.random.default_rng(2); f = lambda t: 5 + 4 * np.sin(2 * np.pi * t); T = 3.0     # ∫ = 5T
    n = np.array([len(thinning(f, 9.0, T, rng)) for _ in range(4000)])
    assert abs(n.mean() - 15.0) < 4 * n.std(ddof=1) / np.sqrt(len(n))

def test_garwood_contains_truth_about_95_percent():
    rng = np.random.default_rng(3); lam = 6.0; ks = rng.poisson(lam, 1500); hit = 0
    for k in ks: lo, hi = garwood(int(k)); hit += (lo <= lam <= hi)
    assert hit / len(ks) >= 0.94                              # exact intervals are conservative: coverage ≥ nominal [VERIFY by running]
```

`[VERIFY]` The `garwood` bisection brackets and the monotonic direction of each root function must be confirmed by running the coverage test; adjust the brackets only with evidence. Confirm the `5×` inflation and the `3e-3` bound in `test_overdispersion_inflates_false_alarms` against your own run before asserting them.

### 11.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Gap-based and direct-Poisson counts agree (KS/chi-square, `p > 0.01` over 20 seeds); thinning's expected count within `4·SE` of `∫λ`; superposition/splitting identities verified |
| M2 | R4 | `threshold` meets `P(N ≥ k) ≤ α < P(N ≥ k−1)` for a grid of `(λ, α)`; normal-approximation threshold errors tabulated |
| M3 | R5–R6 | Realized false-alarm rates under (a) Poisson, (b) four dispersion levels, (c) seasonality; dispersion-test power curves |
| M4 | R7 | Garwood coverage ≥ nominal for all tested `λ` (exact intervals are conservative; report how conservative) |
| M5 | R8–R9 | Detection-delay distributions for `c ∈ {1.5, 2, 3}`; robust thresholds restore the design false-alarm rate on overdispersed traffic |
| M6 | R10–R11 | Reproducibility tests; `REPORT.md` regenerated by one script; runbook included |

### 11.5 Statistical-honesty requirements

- Every false-alarm rate is reported as **realized rate ± standard error** with the number of windows; rates around `10⁻³` need ≥ `10⁶` windows for a usable error bar. State the rare-event limitation (Module 09 Project 1).
- Show the **design vs realized** rate side by side for every scenario, and never claim an alert "has a false-alarm rate of α" without the traffic assumption attached.
- Report detection delay as a **distribution** (median and tail), not just a mean.
- Include one scenario where the Poisson model **fails badly** and one where a naive fix (just raising the threshold) trades false alarms for missed detections, with numbers.

### 11.6 Failure modes to demonstrate

Exposure/window-length mismatch (per-minute rate used for 5-minute windows); rate estimated on a different phase of the daily cycle than the alert window; overdispersed bursts (retries, batch jobs); correlated events (cascades); thresholds computed from the normal approximation at small `λ`; sample rate estimated from too few windows; counting windows with missing data as zeros.

### 11.7 Stretch goals

1. Negative-binomial thresholds with parameters fit by method of moments; compare false-alarm control with the empirical-quantile threshold.
2. A CUSUM or sequential probability-ratio test for a rate change; compare its detection delay at equal false-alarm rate with the simple threshold `[VERIFY: SPRT formulas]`.
3. Seasonality-aware baseline (hour-of-week rate table with smoothing); evaluate the false-alarm rate on a simulated weekly pattern.
4. Hawkes-style self-exciting process simulation to generate bursts, and the resulting dispersion index `[VERIFY: model]`.
5. Multiple-alert correction: with `m` independent monitors, the probability that at least one fires per window (union bound, Module 09).

### 11.8 ML connection (README prompt)

Write a one-page "event-rate alerting" runbook: which assumptions the Poisson threshold makes, how to check them from data (dispersion, autocorrelation, seasonality), how to set `α` from a weekly false-alarm budget, and how the same ideas apply to monitoring model-prediction volumes and label rates in production (Stage 5D-12).

### Check yourself (Unit 11)

1. How do you pick the alert threshold for a target false-alarm probability?
2. Why can an alert tuned for a Poisson stream fire far too often in production?
3. Why do exact Poisson confidence intervals over-cover?

**Reference answers:** (1) The smallest `k` with `P(N ≥ k) ≤ α` under the fitted rate. (2) Real traffic is overdispersed (bursts, varying rate), so counts exceed the Poisson tail much more often than the model predicts. (3) The Poisson counts are discrete, so inverting the cdf at the tail level guarantees at least the nominal coverage and typically exceeds it.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 6 lessons, 2 projects, 11 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 11–14, 4C-01/04/05/07/10, and Stage 5 pointers (5A-03/04/07/10, 5B-02/04/06/09/10/13, 5C-03/04/12, 5D-09/11/12) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: Clopper–Pearson and Garwood formulas and the Gamma relationship, rule of three, Gumbel-max exactness, Glorot-uniform limits and He/Glorot conventions, Lewis–Shedler thinning, Dirichlet sampling at tiny `α`, SPRT/CUSUM formulas, Hawkes model, `χ²` distribution of Mahalanobis `d²`.
4. `[VERIFY]` All printed numerical results (coverage rates, dispersion indices, false-alarm rates, bootstrap p-value calibration, regret) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, SymPy 1.14): every lesson snippet executed; all 3 `distgallery` and all 5 `poissim` tests passed. Defects found and fixed during the run: the Clopper–Pearson bisection had its sign convention reversed for both bounds (it returned `(0.0, 1.0)` for 0/100; corrected values `(0, 0.0362)` and `(0.8238, 0.9510)` for 0/100 and 90/100), and the Poisson normal-approximation tail had a misplaced `√2` (the correct normal value for `P(N ≥ 5)` at `λ = 1` is 0.00023 against an exact 0.00366, i.e. the normal approximation understates this tail about 16×). Measured in seeded runs: (a) parametric-bootstrap KS p-values were calibrated (4.3% rejection at the 5% level over 300 true-model repetitions) whereas the textbook KS test with fitted parameters rejected 0% (conservative); power against `t₃` data fit by a normal was 0.42, 0.78, 1.00 at `n = 50, 100, 400`; (b) estimator error vs `n` had log-log slopes −0.50 (normal mean), −0.51 (exponential rate) and −0.98 (uniform upper endpoint); (c) a Poisson alert designed for a 0.001 false-alarm rate (`λ = 20`, threshold 36) realized 0.00078 on Poisson traffic but 0.0045, 0.037, 0.091, 0.173 at dispersion indices 1.4, 3, 6, 21 (4.5× to 173× the design), and 0.034 under ±50% seasonality with a constant `λ̂`; normal-approximation thresholds were 1–2 counts too low, giving realized tail probabilities 0.0017–0.0037 vs the 0.001 design; (d) Garwood coverage was 0.983, 0.984, 0.975, 0.956 for `λ = 0.5, 2, 10, 50` (conservative, as expected for exact intervals); (e) detection delay after a rate step at the threshold of 36: median 5 windows (95th percentile 18) for ×1.5, 1 for ×2 and ×3; (f) an empirical-quantile threshold fit on overdispersed training traffic (threshold 71) realized 0.00089 on fresh overdispersed traffic, restoring the design rate, but a threshold that high would no longer catch a 2× step from `λ = 20` (new mean 40), which is the false-alarm vs detection trade-off the report must show. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] Every distribution states its parameterization; no fitted value, interval, coverage, or false-alarm rate appears without the measurement that produced it.
