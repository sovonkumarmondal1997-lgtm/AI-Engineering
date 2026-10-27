# SYLLABUS — 11-Sampling-and-Limit-Theorems (S4B-11)

**Stage 4B — Mathematics for Machine Learning · Module 11 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy and the standard library; SciPy is **never required** (optional only for cross-checks), Matplotlib and pytest where stated. All datasets are **synthetic and generated in code**. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Random sampling and inverse-transform sampling | `01-random-sampling-and-inverse-transform-sampling.md` | Beginner → Intermediate |
| 3 | Law of large numbers | `02-law-of-large-numbers.md` | Intermediate |
| 4 | Central limit theorem | `03-central-limit-theorem.md` | Intermediate → Advanced |
| 5 | Sampling distributions and standard error | `04-sampling-distributions-and-standard-error.md` | Intermediate → Advanced |
| 6 | Practice question bank | `practice-questions.md` | All levels |
| 7 | Project index | `Projects/README.md` | Intermediate |
| 8 | Project: sampling from a next-token distribution | `Projects/01-sampling-from-a-next-token-distribution.md` | Intermediate → Advanced |
| 9 | Project: CLT and LLN simulation lab | `Projects/02-clt-and-lln-simulation-lab.md` | Advanced |

**Prerequisites:** Module 09 (PMF/PDF/CDF, expectation, variance, covariance, independence, effective sample size), Module 10 (distributions, softmax, exponential, normal, Beta; log-sum-exp), Module 06 (integrals, improper integrals and the Cauchy example), Module 08 (the `σ²/B` mini-batch variance law). **Plan slot:** week 13 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** required on every track: every confidence interval, A/B test, and Monte Carlo estimate in Stage 5 leans on this module, and token sampling is how every LLM produces text.

**Teaching stance (industry, not university):** these are the theorems that justify *averaging data* and *trusting an error bar*. Each lesson shows the theorem, the **simulation that demonstrates it**, and, just as importantly, **the conditions under which it fails** (heavy tails, dependence, small samples, rare events). Every claim carries the experiment that produced its numbers.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (formula, simulation, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Three questions run through every ML evaluation: *How do I generate random draws correctly?* *Why does averaging many things give a stable number?* *How uncertain is that number?* Sampling answers the first (Monte Carlo, mini-batches, data augmentation, token generation), the law of large numbers the second (empirical risk approximates expected risk), and the central limit theorem plus the standard error the third (confidence intervals, A/B tests, comparing models). When the assumptions fail (heavy tails, correlated samples, tiny rare-event counts) the error bars are wrong, silently.

### 1.2 Outcomes

1. Generate reproducible random draws, control seeds across parallel workers, and avoid common PRNG mistakes (modulo bias, correlated streams, global state).
2. Sample from arbitrary distributions by inverse transform, rejection sampling, and Box–Muller; sample categoricals; implement reservoir sampling and shuffles correctly.
3. State and demonstrate the law of large numbers, its `1/√n` rate, and its failure for distributions without a mean.
4. State and demonstrate the central limit theorem; measure how fast it kicks in for different distributions, and identify where it fails.
5. Compute and interpret standard errors for means, proportions, differences, and medians; build confidence intervals and check their *actual* coverage.
6. Plan a sample size for a target precision, and recognize the effect of dependence (design effect, effective sample size).
7. Implement temperature, top-k, and top-p sampling for a next-token distribution and validate each sampler against its target distribution.
8. Build a LLN/CLT simulation lab that reports honest convergence rates and failure cases.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Random and inverse-transform sampling | Monte Carlo, token sampling, mini-batches, reservoir sampling | Samplers validated by KS/frequencies |
| 2 | Law of large numbers | Empirical risk, Monte Carlo, metric stability | Running means; failure for heavy tails |
| 3 | Central limit theorem | Normal approximations, CIs, gradient noise | Convergence speed and coverage studies |
| 4 | Sampling distributions, standard error | Metric uncertainty, test-set size, seeds | SE, FPC, design effect, sample-size planning |

### 1.4 Concept map

```
Uniform(0,1) PRNG ──► inverse transform / rejection / Box–Muller ──► samples from any distribution ──► Monte Carlo estimates ─┐
                          └─► categorical sampling (searchsorted on cumsum) ──► next-token sampling: temperature · top-k · top-p      │
                                                                                                                                     ▼
iid X₁…Xₙ ──► sample mean X̄ ──LLN──► μ (rate σ/√n; needs a finite mean)  ──CLT──► √n(X̄ − μ)/σ ≈ N(0,1) (needs finite variance; speed ∝ skewness)
                              └─► sampling distribution of any statistic ──► standard error ──► CI = estimate ± z·SE ──► coverage (check it!)
dependence (clusters, time series) ──► design effect / effective sample size ──► wider true SE
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest          # scipy optional, for cross-checks only
```

Rules for every lab: use `rng = np.random.default_rng(seed)` (never the legacy global `np.random.seed`); **validate every sampler** (KS distance for continuous, frequency/total-variation distance with a tolerance derived from the sample size for discrete); report every simulated quantity with its **standard error** and `N`; **vectorize** (draw a `(reps, n)` matrix) rather than looping; for coverage studies use ≥ 2,000 repetitions and report the coverage with its own binomial standard error; state which distribution, `n`, and `μ, σ` each claim refers to.

### 1.6 Checkpoint

Your `limitlab` shows: LLN error with log-log slope near `−½` for finite-variance distributions; the CLT's KS distance shrinking with `n` for the exponential but **not** for the Cauchy; and the 95% interval's measured coverage below nominal for skewed data at small `n`. Your token sampler's empirical frequencies match the target distribution within the tolerance you derive.

### Check yourself (Unit 1)

1. Which theorem justifies using a sample average to estimate an expectation, and which justifies a normal-based confidence interval?
2. Why must a coverage claim be checked by simulation?

**Reference answers:** (1) The law of large numbers; the central limit theorem. (2) The nominal 95% is only asymptotic and assumption-dependent; at small `n`, with skew or dependence, the realized coverage can be far lower.

---

## Unit 2 — Random sampling and inverse-transform sampling (`01-…md`)

### 2.1 Why ML needs this

Everything stochastic in ML (initialization, mini-batch order, dropout masks, data augmentation, bootstrap resamples, Monte Carlo estimates, and the next token an LLM emits) comes from a random number generator and a method to turn its uniform draws into the distribution you need. Subtle mistakes here (reusing seeds, biased sampling, wrong parameterization) corrupt experiments without raising any error.

### 2.2 Intuition

A computer generates **pseudo-random** numbers: a deterministic stream that behaves like independent `Uniform(0, 1)` draws. Any other distribution can be built from those uniforms. The cleanest recipe is **inverse transform**: push a uniform through the inverse CDF.

### 2.3 Mechanics

- **PRNG and seeds:** `np.random.default_rng(seed)` uses a modern generator (PCG64 by default `[VERIFY]`); same seed ⇒ same stream ⇒ reproducibility. Prefer the `Generator` API over the legacy `np.random.seed` global state.
- **Independent streams for parallel work:** `np.random.SeedSequence(seed).spawn(k)` gives `k` statistically independent child seeds `[VERIFY: guarantees]`; adding `i` to a seed is *not* the recommended way.
- **Inverse transform sampling:** if `U ~ Uniform(0,1)` and `F` is a CDF with quantile function `Q = F⁻¹`, then `X = Q(U)` has CDF `F` (Module 09 Lesson 6).
  - Exponential: `X = −ln(1 − U)/λ` (use `1 − U` to avoid `ln 0`).
  - Discrete/categorical: build the cumulative sums `c_k`; `X = ` the first `k` with `U < c_k` (`np.searchsorted(c, u, side="right")`).
  - Empirical or piecewise-linear CDF: `np.interp(u, cdf_values, x_values)`.
- **Rejection (accept–reject) sampling:** target density `f`, proposal `g` (easy to sample), constant `M` with `f(x) ≤ M·g(x)`: draw `x ~ g`, `u ~ U(0,1)`, accept if `u·M·g(x) ≤ f(x)`. The acceptance probability is `1/M`; a loose `M` wastes samples, and a violated bound biases the result.
- **Box–Muller:** from `U₁, U₂` uniform, `Z₀ = √(−2 ln U₁) cos(2πU₂)`, `Z₁ = √(−2 ln U₁) sin(2πU₂)` are independent `N(0, 1)`.
- **Sampling a categorical from logits:** softmax then inverse transform, or the **Gumbel-max trick** (Module 10 Lesson 2).
- **Sampling with/without replacement:** `rng.choice(n, size, replace=...)`; without replacement use a **Fisher–Yates shuffle** (uniform over permutations). Mini-batch epochs are permutations (Module 08 Lesson 4); the bootstrap samples *with* replacement (Module 12).
- **Reservoir sampling (Algorithm R):** to draw a uniform sample of `k` items from a stream of unknown length, keep the first `k`; for item `i > k` (1-indexed) replace a random reservoir slot with probability `k/i`; every item ends up in the sample with probability `k/n`.
- **Modulo bias:** mapping random integers with `r % m` is biased unless `m` divides the range of `r` (e.g., a uniform integer on `0…255` taken `% 10` makes values `0…5` slightly more likely than `6…9`); use `rng.integers(0, m)`.
- **Monte Carlo estimation:** `E[g(X)] ≈ (1/N) Σ g(Xᵢ)` with standard error `s/√N` (LLN + CLT, Lessons 2–3).
- **Importance sampling (outline):** sample from `q`, reweight by `f/q`; unbiased if `q` covers `f`'s support but the variance can explode when `q` has lighter tails than `f` `[VERIFY: statement; developed in 4C-04]`.
- **Quality of randomness:** PRNG output passes statistical tests but is **not cryptographically secure**; use the `secrets` module for tokens/keys.

**Worked example:** exponential with rate 2: draw `u = 0.5` ⇒ `x = −ln(0.5)/2 = 0.3466`, the median. Rejection sampling for `Beta(2, 5)` (pdf `30x(1−x)⁴`, maximum `2.4576` at `x = 0.2`) from `Uniform(0,1)` with `M = 2.4576` accepts about `1/2.4576 ≈ 40.7%` of proposals.

### 2.4 Code

```python
import math
import numpy as np

def ks_distance(x, cdf):
    s = np.sort(np.asarray(x, float)); n = len(s); F = cdf(s)
    return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))
Phi = lambda z: 0.5 * (1 + np.vectorize(math.erf)(np.asarray(z) / math.sqrt(2)))

# --- reproducibility, and independent streams via SeedSequence.spawn
assert np.array_equal(np.random.default_rng(42).random(5), np.random.default_rng(42).random(5))
children = np.random.SeedSequence(123).spawn(4); gens = [np.random.default_rng(c) for c in children]
streams = np.array([g.random(200_000) for g in gens]); C = np.corrcoef(streams)
print("max |correlation| between spawned streams:", np.abs(C[np.triu_indices(4, 1)]).max())

# --- inverse transform: exponential, and the 1−U guard against ln(0)
rng = np.random.default_rng(0); lam = 2.0
x = -np.log1p(-rng.random(400_000)) / lam
print("KS distance to the exponential CDF:", ks_distance(x, lambda t: 1 - np.exp(-lam * t)), " mean:", x.mean(), "(0.5)")

# --- discrete inverse transform with searchsorted
p = np.array([0.1, 0.2, 0.4, 0.3]); cum = np.cumsum(p)
idx = np.minimum(np.searchsorted(cum, rng.random(400_000), side="right"), len(p) - 1)
freq = np.bincount(idx, minlength=4) / len(idx); print("frequencies:", np.round(freq, 4), " target:", p); assert np.allclose(freq, p, atol=0.004)

# --- piecewise-linear CDF via np.interp (triangular-ish density on [0, 3])
xs = np.array([0.0, 1.0, 2.0, 3.0]); cdf_pts = np.array([0.0, 0.5, 0.9, 1.0])
y = np.interp(rng.random(300_000), cdf_pts, xs)
print("P(Y ≤ 1) =", (y <= 1).mean(), "(0.5)   P(Y ≤ 2) =", (y <= 2).mean(), "(0.9)")

# --- rejection sampling for Beta(2, 5) from Uniform(0, 1)
f = lambda t: 30 * t * (1 - t) ** 4; M = f(0.2)
N = 600_000; prop = rng.random(N); accept = rng.random(N) * M <= f(prop); samp = prop[accept]
print(f"acceptance rate {accept.mean():.4f}  (1/M = {1 / M:.4f});  sample mean {samp.mean():.4f}  (Beta mean 2/7 = {2 / 7:.4f})")
beta_cdf = lambda t: np.clip(np.array([sum(f(np.linspace(0, ti, 2001)) * (ti / 2000) * np.r_[0.5, np.ones(1999), 0.5]) for ti in np.atleast_1d(t)]), 0, 1)
print("KS distance (subsampled):", ks_distance(samp[:3000], beta_cdf))

# --- Box–Muller
u1, u2 = 1 - rng.random(300_000), rng.random(300_000)                       # 1−u1 ∈ (0, 1]: no log(0)
z = np.concatenate([np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2), np.sqrt(-2 * np.log(u1)) * np.sin(2 * np.pi * u2)])
print("Box–Muller: mean", z.mean(), " std", z.std(), " KS", ks_distance(z[:100_000], Phi))

# --- modulo bias, computed exactly
r = np.arange(256); counts = np.bincount(r % 10, minlength=10); print("probabilities of r % 10 for uniform r ∈ 0…255:", np.round(counts / 256, 4), "(not uniform)")

# --- reservoir sampling (Algorithm R): each of n items is kept with probability k/n
def reservoir(stream, k, g):
    res = []
    for i, item in enumerate(stream, start=1):
        if i <= k: res.append(item)
        else:
            j = g.integers(0, i)                                               # uniform on 0…i−1
            if j < k: res[j] = item
    return res
g = np.random.default_rng(1); n, k = 20, 5; hits = np.zeros(n)
for _ in range(40_000):
    for it in reservoir(range(n), k, g): hits[it] += 1
print("inclusion frequencies:", np.round(hits / 40_000, 3).min(), "…", np.round(hits / 40_000, 3).max(), " target k/n =", k / n)

# --- Fisher–Yates: all 6 permutations of 3 items equally likely
def fisher_yates(a, g):
    a = list(a)
    for i in range(len(a) - 1, 0, -1):
        j = g.integers(0, i + 1); a[i], a[j] = a[j], a[i]
    return tuple(a)
from collections import Counter
perm_counts = Counter(fisher_yates([0, 1, 2], g) for _ in range(120_000)); print({k_: round(v / 120_000, 4) for k_, v in sorted(perm_counts.items())})

# --- Monte Carlo with a standard error: E[exp(Z)] for Z ~ N(0,1) is e^{1/2}
zz = rng.normal(size=1_000_000); w = np.exp(zz); print(f"MC estimate {w.mean():.4f} ± {w.std(ddof=1) / math.sqrt(len(w)):.4f}   exact {math.exp(0.5):.4f}")
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Legacy global `np.random.seed` with multiple libraries/threads | Irreproducible or accidentally shared state | `default_rng`; pass the generator explicitly |
| Seeds `0, 1, 2, …` for parallel workers without `SeedSequence` | Risk of correlated streams in some generators | `SeedSequence.spawn` `[VERIFY]` |
| `ln(U)` with `U = 0` | `-inf` | Use `1 − U` or `log1p(−U)` |
| Rejection sampling with `M` too small | Biased samples (the bound is violated) | Verify `f ≤ M g` on a grid; test the output with KS |
| Rejection sampling with `M` far too large | Almost everything rejected | Choose a proposal that matches `f` |
| Modulo mapping (`r % m`) | Slight non-uniformity | `rng.integers(0, m)` |
| `rng.choice(p=...)` with probabilities that do not sum to 1 | `ValueError` | Normalize in `float64` |
| Shuffling by sorting random keys with ties, or by a "swap with any index" loop | Non-uniform permutations | Fisher–Yates (swap with `j ∈ [0, i]`) |
| Reusing the same seed for training and evaluation sampling | Correlated or leaked randomness | Separate generators per role |
| Using PRNG output for security | Predictable tokens | `secrets` |
| Estimating a Monte Carlo quantity without its standard error | Unverifiable numbers | `s/√N` always |

### 2.6 ML link

- **Token sampling** in language models is categorical inverse-transform sampling after softmax/temperature/top-k/top-p (Project 1; Stage 5C-12).
- **Mini-batch order, dropout masks, augmentation** use reproducible, separately seeded generators (Stage 5C-03, 5D-06).
- **Bootstrap** resampling (Module 12) and **Monte Carlo** estimation of expectations (4C-04).
- **Reservoir sampling** for uniform samples from data streams (logging, monitoring; Stage 5D-12).
- **Reproducibility** of experiments depends on seed management (Stage 5A-11).

### 2.7 Lab (75 min)

1. Implement inverse-transform samplers for exponential, a discrete distribution, and a piecewise-linear CDF; validate each (KS or frequency tolerance derived from `N`).
2. Implement rejection sampling for `Beta(2, 5)`; verify the acceptance rate `1/M`; show the bias when `M` is set too small.
3. Implement Box–Muller and validate against the normal cdf; compare speed with `rng.normal` (your machine, your numbers).
4. Demonstrate modulo bias exactly, and the uniformity of `rng.integers`.
5. Implement reservoir sampling and Fisher–Yates; verify the inclusion probability `k/n` and permutation uniformity; show that a naive "for each `i`, swap with a random index in `0…n−1`" shuffle is not uniform for `n = 3` (in a seeded run its six permutation frequencies ranged from 0.146 to 0.186 against the uniform 0.1667).

### Check yourself (Unit 2)

1. What is the inverse-transform sample for an exponential with rate `λ` given `U`?
2. What fraction of proposals does a rejection sampler accept with bound `M`?
3. Why is `r % m` a biased way to draw uniformly from `0…m−1`?

**Reference answers:** (1) `X = −ln(1 − U)/λ`. (2) `1/M` (when `g` is a normalized density). (3) Unless `m` divides the number of possible values of `r`, some residues occur more often than others.

---

## Unit 3 — Law of large numbers (`02-…md`)

### 3.1 Why ML needs this

The law of large numbers (LLN) is why the average loss on a sample estimates the expected loss, why Monte Carlo works, and why more data stabilizes a metric. It is also a source of false comfort: it says nothing about small samples, needs a finite mean, and converges slowly.

### 3.2 Intuition

The sample mean `X̄ₙ` of i.i.d. draws settles toward the true mean `μ` as `n` grows. Early on it wanders; later it hugs `μ`; how fast depends on the spread `σ`.

### 3.3 Mechanics

- **Statement (i.i.d., finite mean `μ`):** `X̄ₙ → μ`.
  - **Weak LLN:** convergence *in probability*: for every `ε > 0`, `P(|X̄ₙ − μ| > ε) → 0`.
  - **Strong LLN:** convergence *almost surely* (with probability 1 the whole sequence converges) `[VERIFY: precise statement]`.
- **Chebyshev proof sketch (finite variance):** `Var(X̄ₙ) = σ²/n`, so `P(|X̄ₙ − μ| ≥ ε) ≤ σ²/(nε²) → 0` (Module 09 Lesson 7).
- **Rate:** the typical error is `σ/√n`: **to halve the error you need 4× the data.** (CLT makes this precise, Lesson 3.)
- **Needs a finite mean:** the Cauchy distribution has no mean; its running average never settles (Module 06 Lesson 4; demonstrated below). Heavy-tailed distributions with finite mean but infinite variance (Pareto with shape `1 < α ≤ 2`) satisfy the LLN but converge erratically and slowly.
- **Empirical frequencies:** `k/n → P(A)` (indicator variables, Module 09 Lesson 5).
- **Empirical CDF:** `F̂ₙ(x) → F(x)`, uniformly (Glivenko–Cantelli); the maximum gap shrinks like `1/√n` (the DKW inequality) `[VERIFY]`.
- **Empirical risk → expected risk:** for a *fixed* model, the average loss on `n` fresh i.i.d. samples converges to the expected loss by the LLN. A model *selected using the same data* is a different matter (optimism/overfitting; generalization theory, 4C-05).
- **What the LLN does not say:** no "law of averages" that compensates streaks: after five heads in a row the next flip is still `½` (independence). It also says nothing about averages of *dependent* data without further conditions.
- **Weighted/unequal batches:** the overall mean is the *size-weighted* mean of batch means; averaging per-batch means with unequal sizes is biased.
- **Monte Carlo integration** is the LLN applied to `g(X)`; error `σ_g/√N` regardless of dimension (Module 06 Lesson 6).

**Worked example:** a fair-coin running frequency of heads: after 100 flips it is typically within `±0.1` of `½` (`σ/√n = 0.05`, two SE); after 10,000 flips within `±0.01`.

### 3.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def running_mean(x): return np.cumsum(x) / np.arange(1, len(x) + 1)

# --- the sample mean settles: normal, exponential, Cauchy, Pareto(α = 1.5; classical Pareto = 1 + Lomax)
N = 1_000_000
draws = {
    "normal(0,1)": (rng.normal(size=N), 0.0),
    "exponential(1)": (rng.exponential(size=N), 1.0),
    "Pareto α=3 (finite var)": (1 + rng.pareto(3.0, size=N), 3 / 2),
    "Pareto α=1.5 (infinite var)": (1 + rng.pareto(1.5, size=N), 1.5 / 0.5),
    "Cauchy (no mean)": (rng.standard_cauchy(size=N), None),
}
marks = [10 ** k for k in range(2, 7)]
for name, (x, mu) in draws.items():
    rm = running_mean(x)
    print(f"{name:28s}", [round(float(rm[m - 1]), 3) for m in marks], " truth:", mu)

# --- error vs n over many repetitions: slope −1/2 for finite variance
def mean_abs_error(sampler, mu, ns, reps=400):
    out = []
    for n in ns:
        e = np.abs(sampler((reps, n)).mean(axis=1) - mu); out.append(e.mean())
    return np.array(out)
ns = np.array([10, 40, 160, 640, 2560, 10240])
for name, sampler, mu in (("normal", lambda s: rng.normal(size=s), 0.0), ("exponential", lambda s: rng.exponential(size=s), 1.0),
                          ("Pareto α=1.5", lambda s: 1 + rng.pareto(1.5, size=s), 3.0), ("Pareto α=1.1", lambda s: 1 + rng.pareto(1.1, size=s), 11.0)):
    err = mean_abs_error(sampler, mu, ns)
    print(f"{name:14s} fitted log-log slope of mean |X̄ − μ| vs n: {np.polyfit(np.log(ns), np.log(err), 1)[0]:.2f}")   # −0.5 only with finite variance

# --- Chebyshev bound holds (and is loose)
n, eps, reps = 100, 0.25, 200_000; xbar = rng.exponential(size=(reps, n)).mean(axis=1)
print("P(|X̄−1| ≥ 0.25) =", (np.abs(xbar - 1) >= eps).mean(), " Chebyshev bound σ²/(nε²) =", 1 / (n * eps ** 2))

# --- empirical CDF converges uniformly: sup-gap ~ 1/√n
for n in (100, 1000, 10000, 100000):
    gaps = []
    for _ in range(40):
        x = np.sort(rng.normal(size=n)); F = 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))
        gaps.append(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))
    print(f"n={n:6d}  mean sup|F̂−F| = {np.mean(gaps):.4f}   ×√n = {np.mean(gaps) * math.sqrt(n):.3f}")

# --- no 'law of averages': after 5 heads the next flip is still a fair coin
flips = rng.random((2_000_000, 6)) < 0.5; after5 = flips[flips[:, :5].all(axis=1)]
print("P(6th is heads | first five heads) =", after5[:, 5].mean(), " (n =", len(after5), ")")

# --- the mean of batch means is biased when batch sizes differ
vals = np.r_[rng.normal(10, 1, 9000), rng.normal(0, 1, 1000)]      # a large batch (mean 10) and a small one (mean 0)
batches = [vals[:9000], vals[9000:]]
print("mean of batch means:", np.mean([b.mean() for b in batches]), " size-weighted (true) mean:", vals.mean())

# --- Monte Carlo integration error is σ/√N in any dimension: volume of the unit ball in d = 10
#     (only ≈ 0.25% of points land inside, so at N = 10⁴ there are ~25 hits and the normal-based SE is unreliable: a rare-event warning)
d = 10; exact = math.exp((d / 2) * math.log(math.pi) - math.lgamma(d / 2 + 1))
for Nm in (10 ** 4, 10 ** 5, 10 ** 6):
    pts = rng.uniform(-1, 1, size=(Nm, d)); inside = (np.sum(pts ** 2, axis=1) <= 1).astype(float)
    est = 2 ** d * inside.mean(); se = 2 ** d * inside.std(ddof=1) / math.sqrt(Nm)
    print(f"N={Nm:8d}: volume estimate {est:.4f} ± {se:.4f}   exact {exact:.4f}")
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Applying the LLN to a distribution without a mean (Cauchy; Pareto `α ≤ 1`) | Running mean never settles | Check tails; use the median or trimmed means; confirm the mean exists |
| Expecting `σ/√n` behaviour with infinite variance | Erratic, slower convergence (fitted slope shallower than `−½`) | Check moments; heavy-tail-aware methods |
| Believing in the "law of averages" (gambler's fallacy) | Wrong predictions after streaks | Independence: no compensation |
| Averaging unequal-size batch metrics | Biased overall metric | Size-weighted mean |
| Treating dependent samples as i.i.d. | Convergence slower than `1/√n` | Effective sample size (Module 09 Lesson 4) |
| Evaluating a model on data used to select it | Optimistic "converged" estimate | Held-out data |
| Declaring convergence from one run | A lucky path | Many seeds; standard errors |
| Using a rare-event probability estimate from few hits | Huge relative error | Importance sampling; report the count of hits |

### 3.6 ML link

- **Empirical risk** approximates expected risk for fixed models (4C-05); the gap for *selected* models is what generalization theory studies.
- **Monte Carlo** methods (expectations, probabilities, integrals) rely on the LLN and its `1/√N` rate (Module 06 Lesson 6, 4C-04).
- **Metrics on larger test sets stabilize** with `σ/√n` (Lesson 4 below, Module 12).
- **Weighted averaging of batch metrics** matters in distributed evaluation (Stage 5D-12).
- **Heavy-tailed gradients/losses** make averages unreliable (Stage 5C-03) `[JUDGEMENT]`.

### 3.7 Lab (75 min)

1. Plot running means (log-x) for the five distributions, with `±2σ/√n` bands where they exist; describe each.
2. Fit the log-log slope of the mean absolute error vs `n` for four distributions; explain why the Pareto `α = 1.1` slope is much shallower.
3. Verify Chebyshev's bound and measure how loose it is for three distributions.
4. Plot the ECDF gap vs `n` and fit its slope.
5. Reproduce the gambler's-fallacy and unequal-batch-mean examples; compute the bias of the naive batch mean as a function of the batch-size imbalance.

### Check yourself (Unit 3)

1. If you need to halve the standard error of a mean, how much more data do you need?
2. Does the LLN hold for the Cauchy distribution?
3. After 10 heads in a row from a fair coin, what is `P(next is heads)`?

**Reference answers:** (1) Four times as much (error ∝ `1/√n`). (2) No: the mean does not exist and the running average does not converge. (3) `½`; the flips are independent.

---

## Unit 4 — Central limit theorem (`03-…md`)

### 4.1 Why ML needs this

The central limit theorem (CLT) is why the normal distribution appears everywhere averages do: confidence intervals for accuracy, A/B test statistics, the approximate Gaussian noise of mini-batch gradients. Knowing *how fast* it kicks in, and when it does not, tells you when a "95% interval" can be trusted.

### 4.2 Intuition

Average many independent small contributions and the result looks bell-shaped, **whatever shape the individual contributions had**, provided each has finite variance and none dominates.

### 4.3 Mechanics

- **Statement (i.i.d., mean `μ`, variance `σ² < ∞`):** `Zₙ = √n (X̄ₙ − μ)/σ → N(0, 1)` in distribution. Equivalently `X̄ₙ ≈ N(μ, σ²/n)` and `Σᵢ Xᵢ ≈ N(nμ, nσ²)`.
- **Practical use:** `P(|X̄ₙ − μ| ≤ 1.96 σ/√n) ≈ 0.95`; replacing `σ` by the sample standard deviation `s` gives the Wald interval `x̄ ± 1.96 s/√n`, accurate for large `n`.
- **Speed of convergence** depends on the shape of the parent distribution. The Berry–Esseen theorem bounds the maximum cdf error by `C·E|X−μ|³/(σ³√n)`: **error decays like `1/√n`, scaled by skewness/third-moment heaviness** `[VERIFY: statement and constant]`.
  - Symmetric light-tailed (uniform): near-normal at `n ≈ 5–10`.
  - Skewed (exponential, lognormal): needs `n` in the tens to hundreds.
  - Discrete with a rare outcome (Bernoulli `p = 0.02`): needs `np` large (≳ 10, Module 10); at small `n` the sample proportion is far from normal.
  - Heavy tails with finite variance: slow; the interval can be anti-conservative for a long time.
- **When the CLT fails:** infinite variance (Cauchy: the mean of `n` Cauchy draws is *again Cauchy*, no narrowing; Pareto `α < 2` converges to a non-normal *stable* law) `[VERIFY]`; strong dependence (use effective sample size, Module 09 Lesson 4); non-identical distributions with a dominating term (Lindeberg-type conditions); heavy-tailed gradients.
- **Coverage:** the interval's *actual* probability of containing `μ` can differ from 95%: skewed data and small `n` give coverage below nominal (the interval is too narrow on the skewed side). Always measure coverage by simulation for your distribution and `n`.
- **Normal approximation for sums and proportions:** `Binomial(n, p) ≈ N(np, np(1−p))` (Module 10 Lesson 1) is the CLT for Bernoulli sums.
- **Multivariate CLT:** `√n(X̄ₙ − μ) → N(0, Σ)` (Module 09 Lesson 9); this underlies elliptical confidence regions and the asymptotic normality of estimators (4C-05).
- **Gradient noise:** a mini-batch gradient is an average of per-sample gradients, so by CLT it is approximately Gaussian around the full gradient (Module 08 Lesson 4); the approximation is poor when per-sample gradients are heavy-tailed `[JUDGEMENT]`.
- **Delta method (outline):** smooth functions of a mean are also approximately normal: `g(X̄) ≈ N(g(μ), g′(μ)²σ²/n)` `[VERIFY; developed in 4C-05]`.
- **Why it matters for ML evaluation:** accuracy is a mean of 0/1 indicators; its interval comes from the CLT (or its exact/Wilson alternatives for small `n`, Module 09 and 10).

**Worked example:** exponential data (mean 1, SD 1, skew 2), `n = 30`: the mean has SD `1/√30 = 0.183`, so the nominal 95% interval is `x̄ ± 0.358` (with `σ` known); because the exponential is skewed, the measured coverage of the `x̄ ± 1.96 s/√n` interval at `n = 30` is below 95% in simulation (Section 4.4).

### 4.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)
Phi = lambda z: 0.5 * (1 + np.vectorize(math.erf)(np.asarray(z) / math.sqrt(2)))
def ks_to_normal(z): s = np.sort(z); n = len(s); F = Phi(s); return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))

DISTS = {   # name: (sampler(shape), mean, sd)
    "uniform":      (lambda s: rng.random(s), 0.5, math.sqrt(1 / 12)),
    "exponential":  (lambda s: rng.exponential(size=s), 1.0, 1.0),
    "lognormal(0,1)": (lambda s: rng.lognormal(0, 1, size=s), math.exp(0.5), math.sqrt((math.e - 1) * math.e)),
    "Bernoulli(0.02)": (lambda s: (rng.random(s) < 0.02).astype(float), 0.02, math.sqrt(0.02 * 0.98)),
}

# --- how fast do standardized means approach N(0,1)?  KS distance vs n
reps = 20_000
print("KS distance of standardized means to N(0,1)   (sampling floor with 20,000 reps ≈ 0.006)")
print(f"{'distribution':16s}" + "".join(f"n={n:<6d}" for n in (1, 5, 30, 200, 1000)))
for name, (draw, mu, sd) in DISTS.items():
    row = []
    for n in (1, 5, 30, 200, 1000):
        z = np.sqrt(n) * (draw((reps, n)).mean(axis=1) - mu) / sd; row.append(ks_to_normal(z))
    print(f"{name:16s}" + "".join(f"{v:<8.3f}" for v in row))
# note: for the discrete Bernoulli(0.02) the KS distance to a continuous normal is limited by the lattice of possible values and falls slowly

# --- Cauchy: the mean of n draws is Cauchy again; the spread does not shrink
for n in (1, 10, 1000):
    m = rng.standard_cauchy(size=(20_000, n)).mean(axis=1); q = np.quantile(m, [0.25, 0.75])
    print(f"Cauchy n={n:5d}: interquartile range of the sample mean = {q[1] - q[0]:.3f}   (stays ≈ 2)")

# --- coverage of x̄ ± 1.96 s/√n  (the Wald/z interval)
def coverage(draw, mu, n, reps=20_000):
    x = draw((reps, n)); xbar = x.mean(axis=1); s = x.std(axis=1, ddof=1)
    return float(np.mean(np.abs(xbar - mu) <= 1.96 * s / math.sqrt(n)))
print("\nempirical coverage of the nominal 95% interval  (binomial SE of each entry ≈ 0.0015)")
print(f"{'distribution':16s}" + "".join(f"n={n:<6d}" for n in (10, 30, 100, 1000)))
for name, (draw, mu, sd) in DISTS.items():
    print(f"{name:16s}" + "".join(f"{coverage(draw, mu, n):<8.3f}" for n in (10, 30, 100, 1000)))

# --- the CLT in Berry–Esseen form: KS error for the exponential falls roughly like 1/√n
ns = np.array([4, 16, 64, 256, 1024]); ks_vals = []
for n in ns:
    z = np.sqrt(n) * (rng.exponential(size=(60_000, n)).mean(axis=1) - 1.0); ks_vals.append(ks_to_normal(z))
print("KS(n):", np.round(ks_vals, 4), " fitted slope:", np.polyfit(np.log(ns), np.log(ks_vals), 1)[0], "(≈ −0.5 until the sampling floor ≈ 0.004)")

# --- sums: binomial as a sum of Bernoullis, normal approximation error
n, p = 100, 0.5; s = rng.binomial(n, p, size=500_000); z = (s - n * p) / math.sqrt(n * p * (1 - p))
print("binomial(100, .5): P(|Z| ≤ 1.96) =", np.mean(np.abs(z) <= 1.96), "(0.95 with a discreteness wiggle)")
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Applying the CLT to infinite-variance data (Cauchy, very heavy Pareto) | Intervals do not narrow; wild coverage | Check tails; use medians/trimmed means, bootstrap with care, or different models |
| Trusting a normal interval at small `n` with skewed data | Coverage well below 95% | Measure coverage; bootstrap/Wilson/exact methods; larger `n` |
| Rare-event proportions (`np < 10`) | Normal approximation poor; intervals outside `[0, 1]` | Wilson/exact interval (Module 09–10) |
| Using `σ` when only `s` is known and `n` is small | Intervals too narrow | `t` distribution (Module 12) |
| Treating dependent observations as i.i.d. | Intervals far too narrow | Effective sample size; block/cluster methods |
| Confusing the CLT (distribution of the *mean*) with a claim that *data* become normal | Normality assumptions on raw data | The CLT is about averages, not individual observations |
| Averaging non-identical heavy-tailed terms | One term dominates the sum | Check Lindeberg-type behaviour; examine the largest contributions |
| Reading a "95%" interval as a 95% probability for this one interval | Misinterpretation | State the repeated-sampling meaning (Module 12) |
| Skipping a coverage simulation when the stakes are high | Silent mis-calibration | Simulate with a distribution resembling the data |

### 4.6 ML link

- **Confidence intervals for accuracy and other mean metrics** (Module 12, Stage 5A-06).
- **A/B test statistics** (z-tests for means and proportions, Module 12).
- **Mini-batch gradient noise** approximately Gaussian under CLT (Module 08 Lesson 4); the approximation limits in heavy-tailed settings.
- **Asymptotic normality** of maximum likelihood estimators (4C-05) generalizes the CLT.
- **Normal approximation of sums** in capacity/queueing estimates (Module 10 Lesson 3).

### 4.7 Lab (90 min)

1. Reproduce the KS-vs-`n` table for five distributions (add Bernoulli with `p = 0.5` and a mixture); describe which converge quickly and why.
2. Show a QQ-statistic (quantile gaps at the 1% and 99% levels) for the sample mean of lognormal data at `n ∈ {10, 100, 1000}`.
3. Produce the coverage table; for each distribution, find the smallest `n` where coverage ≥ 0.94.
4. Demonstrate the Cauchy failure and the Pareto `α = 1.5` partial failure (finite mean, infinite variance): coverage and interval width vs `n`.
5. Verify the `1/√n` Berry–Esseen scaling and estimate the proportionality constant for two distributions.

### Check yourself (Unit 4)

1. State the CLT for the sample mean.
2. Why is coverage typically below 95% for skewed data at small `n`?
3. Does the CLT hold for Cauchy data?

**Reference answers:** (1) `√n(X̄ₙ − μ)/σ → N(0, 1)` for i.i.d. data with finite variance `σ²`. (2) The sample mean's distribution is still skewed, and `s` is correlated with `x̄` in skewed data, so the symmetric normal interval misses on one side more often than nominal. (3) No: it has infinite variance (indeed no mean); the sample mean is again Cauchy.

---

## Unit 5 — Sampling distributions and standard error (`04-…md`)

### 5.1 Why ML needs this

Every metric you report (accuracy, AUC, a mean loss, a difference between two models) is a *statistic computed from one sample*; rerun with another sample and it changes. The **sampling distribution** of the statistic describes that variation, and its standard deviation, the **standard error**, is the error bar. Misreading the standard error (as the standard deviation of the data, or as bias) is one of the most common reporting mistakes.

### 5.2 Intuition

Imagine repeating your whole experiment many times with fresh data and recording the statistic each time. The histogram of those values is its **sampling distribution**; its spread is the **standard error (SE)**. The SE is about *precision*, not accuracy: a biased estimator can have a tiny SE.

### 5.3 Mechanics

- **Standard deviation vs standard error:** SD describes the spread of *individual observations*; SE describes the spread of a *statistic* across samples. `SE(X̄) = σ/√n`; estimate `σ` with `s` (`ddof=1`).
- **Common standard errors:**

| Statistic | SE | Notes |
|---|---|---|
| Mean | `σ/√n` | estimate with `s/√n` |
| Proportion | `√(p(1−p)/n)` | estimate with `p̂`; unreliable near 0/1 |
| Difference of independent means | `√(s₁²/n₁ + s₂²/n₂)` | Welch form (Module 12) |
| Paired difference | `s_d/√n` | where `d` are within-pair differences; typically smaller than the unpaired SE when pairs are positively correlated |
| Median (normal data) | `≈ 1.2533 σ/√n` | about 25% larger than the mean's SE `[VERIFY]` |
| Sample variance (normal data) | `σ²√(2/(n−1))` | `[VERIFY]` |

- **Confidence interval:** `estimate ± z·SE` with `z = 1.96` for 95% (CLT-based); for small `n` with roughly normal data use the Student `t` quantile (e.g., `2.776` for 4 degrees of freedom at 95% `[VERIFY]`; Module 12).
- **Sample size planning:** to estimate a mean to within `±E` at 95% confidence, `n ≈ (1.96 σ/E)²`; for a proportion, `n ≈ 1.96² p(1−p)/E²` (worst case `p = ½`: `n ≈ 0.96/E²`).
- **Finite-population correction:** sampling `n` items without replacement from a finite population of size `N` shrinks the SE by `√((N − n)/(N − 1))` (negligible when `n ≪ N`).
- **Dependence inflates the SE:** for clusters of size `m` with intra-cluster correlation `ρ`, the **design effect** is `deff = 1 + (m − 1)ρ`, so the effective sample size is `n/deff`; for autocorrelated series see Module 09 Lesson 4.
- **Bootstrap (outline, Module 12):** resample the data with replacement, recompute the statistic, and use the spread of the replicates as an SE estimate (works for statistics without a formula, e.g., the median, AUC).
- **SE vs bias:** `MSE = bias² + variance`; an SE says nothing about bias from selection, leakage, or label noise.
- **Reporting practice:** report the estimate, the SE or interval, `n`, and the sampling scheme; for model comparisons use paired differences on the same items.
- **Seed variance:** run-to-run variation from random initialization/data order is another source of variability; report mean ± SE across seeds (Module 08 Project 2).

**Worked example (test-set size):** to distinguish accuracy 90% from 91% with 95% confidence on one test set you need an SE well below `0.5` points: `√(0.9·0.1/n) ≤ 0.005` ⇒ `n ≥ 3 600`; with `n = 1 000` the SE is `0.95` points, so a 1-point difference is within noise.

### 5.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

# --- SD vs SE: the sampling distribution of the mean
sigma, n, reps = 3.0, 25, 100_000
means = rng.normal(10, sigma, size=(reps, n)).mean(axis=1)
print("SD of data:", sigma, "   SD of the sample mean (SE):", means.std(ddof=1), "  theory σ/√n =", sigma / math.sqrt(n))

# --- the SE of the median is about 25% larger than that of the mean (normal data)
x = rng.normal(size=(100_000, 25)); print("SE ratio median/mean:", np.median(x, axis=1).std(ddof=1) / x.mean(axis=1).std(ddof=1), " (≈ 1.2533 for large n)")

# --- estimated SE s/√n tracks the true SE; and its own variability at small n
n = 10; x = rng.normal(0, 2, size=(100_000, n)); se_hat = x.std(axis=1, ddof=1) / math.sqrt(n)
print(f"n=10: mean of estimated SE = {se_hat.mean():.4f}, true SE = {2 / math.sqrt(n):.4f}, spread of SE estimates = {se_hat.std():.4f}")

# --- z vs t interval coverage at tiny n (normal data)
n = 5; x = rng.normal(0, 1, size=(200_000, n)); xbar = x.mean(axis=1); s = x.std(axis=1, ddof=1)
t975_df4 = 2.7764451
print("n=5 coverage with z=1.96:", np.mean(np.abs(xbar) <= 1.96 * s / math.sqrt(n)), "  with t(4 df)=2.776:", np.mean(np.abs(xbar) <= t975_df4 * s / math.sqrt(n)))

# --- proportions: SE and sample-size planning (±1 point at 95% for p = 0.5 → n ≈ 9 604)
p, E = 0.5, 0.01; n_plan = math.ceil(1.96 ** 2 * p * (1 - p) / E ** 2); print("planned n:", n_plan)
phat = rng.binomial(n_plan, p, size=200_000) / n_plan
print("fraction of estimates within ±1 point:", np.mean(np.abs(phat - p) <= E), "(≈ 0.95)")

# --- the test-set size needed to separate 90% and 91% accuracy
for n_test in (500, 1000, 3600, 10_000):
    se = math.sqrt(0.9 * 0.1 / n_test); print(f"n={n_test:6d}: SE of accuracy = {100 * se:.2f} points")

# --- finite-population correction (sampling without replacement)
Npop, n = 1000, 400; pop = rng.normal(size=Npop); sig = pop.std()
samples = np.array([rng.choice(pop, n, replace=False).mean() for _ in range(20_000)])
print(f"SE without replacement: {samples.std(ddof=1):.4f}   σ/√n = {sig / math.sqrt(n):.4f}   with FPC = {sig / math.sqrt(n) * math.sqrt((Npop - n) / (Npop - 1)):.4f}")

# --- design effect: clustered data have a larger SE than the iid formula says
clusters, m, rho = 50, 20, 0.3; reps = 20_000
shared = rng.normal(size=(reps, clusters, 1)) * math.sqrt(rho); noise = rng.normal(size=(reps, clusters, m)) * math.sqrt(1 - rho)
xbar = (shared + noise).mean(axis=(1, 2)); n_total = clusters * m
print(f"cluster-sampled SE: {xbar.std(ddof=1):.4f}   iid formula: {1 / math.sqrt(n_total):.4f}   ×√deff = {math.sqrt(1 + (m - 1) * rho) / math.sqrt(n_total):.4f}")

# --- bootstrap SE for the median: unbiased on average, but noisy from one dataset to the next
sim = np.array([np.median(rng.normal(size=200)) for _ in range(20_000)]).std(ddof=1)
est = np.array([np.median(rng.choice(rng.normal(size=200), size=(500, 200), replace=True), axis=1).std(ddof=1) for _ in range(150)])
print(f"true (simulated) SE of the median: {sim:.4f}   bootstrap SE over 150 datasets: mean {est.mean():.4f}, sd {est.std():.4f}, range {est.min():.4f}…{est.max():.4f}")

# --- paired vs unpaired SE for a model comparison (two models evaluated on the same items)
items = 400; difficulty = rng.normal(size=items)
a = (rng.random(items) < 1 / (1 + np.exp(-(1.0 - difficulty)))).astype(float)
b = (rng.random(items) < 1 / (1 + np.exp(-(1.2 - difficulty)))).astype(float)
d = b - a; se_paired = d.std(ddof=1) / math.sqrt(items); se_unpaired = math.sqrt(a.var(ddof=1) / items + b.var(ddof=1) / items)
print(f"difference {d.mean():+.3f}: paired SE {se_paired:.4f}  vs unpaired SE {se_unpaired:.4f}")
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Reporting the standard deviation of the data as an "error bar" for a mean | Error bar too wide by `√n` | Report SE (or a CI) and say which |
| Reporting SE but not `n` or the sampling scheme | Uninterpretable | State all three |
| Assuming `1/√n` precision for clustered/repeated data | Error bars too narrow (design effect) | Cluster-aware SE; effective sample size |
| Using a normal (`z`) interval at `n < 30` for a mean of roughly normal data | Coverage below 95% | `t` interval (Module 12) |
| Comparing two models with unpaired SEs when they share test items | Intervals too wide (or the difference looks insignificant) | Paired differences |
| Equating "small SE" with "accurate" | Biased estimate with a tight interval | Check for selection, leakage, label noise |
| Planning `n` from a guessed `σ` or `p` without a sensitivity check | Under- or over-powered studies | Use a pilot or the worst case |
| Treating a bootstrap SE as free of assumptions | Bootstrap fails for heavy tails, dependence, extremes | Validate on known cases |
| Using SE of the mean for a *prediction* interval of a single new observation | Intervals far too narrow | Add the observation variance: `√(σ² + σ²/n)` |

### 5.6 ML link

- **Error bars on every reported metric** (Stage 5A-06; Module 12).
- **Test-set size planning** for model comparisons (Stage 5A-07, Module 12 Lesson 6).
- **Seed variance and run-to-run noise:** report mean ± SE across seeds (Module 08 Project 2).
- **Clustered data** (many rows per user) require cluster-robust SEs and group-aware splits (Stage 5A-07).
- **Bootstrap** confidence intervals for AUC and other metrics (Module 12).
- **Monte Carlo error** in simulation-based evaluation (Module 09 Project 1, Stage 5B-10).

### 5.7 Lab (90 min)

1. Build the sampling distribution of the mean, median, and sample variance for normal and exponential data; compare their SEs with the formulas.
2. Verify `z` vs `t` coverage at `n ∈ {3, 5, 10, 30}` for normal data.
3. Sample-size planning: plan `n` for ±1 point on a proportion, verify by simulation; produce a table of `n` vs target precision for `p ∈ {0.1, 0.5, 0.9}`.
4. Design-effect experiment: vary `ρ` and cluster size; compare the realized SE with the iid formula and with `√deff`.
5. Paired-vs-unpaired experiment on two correlated classifiers; show the ratio of SEs as a function of the correlation between their errors.
6. Test-set resampling: bootstrap the AUC of a synthetic classifier and compare the bootstrap SE with a repeated-sampling SE.

### Check yourself (Unit 5)

1. What is the difference between the standard deviation and the standard error?
2. How many test items are needed to estimate accuracy near 90% to within ±1 point (95%)?
3. Why is a paired comparison usually more precise for two models evaluated on the same items?

**Reference answers:** (1) SD describes the spread of individual observations; SE describes the spread of a *statistic* (e.g., the mean) across repeated samples (`σ/√n` for the mean). (2) `n ≈ 1.96²·0.9·0.1/0.01² ≈ 3 457`. (3) Items that are hard for both models inflate each model's variance but cancel in the within-item difference, so the paired SE is smaller when errors are positively correlated.

---

## Unit 6 — Practice question bank (`practice-questions.md`)

### 6.1 Structure

About 45 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 11 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, "predict the simulation", runnable code, and experiment-design judgement.

### 6.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 6.3 Seed items

**Q1 [L1] Inverse transform.** State the recipe. → `X = F⁻¹(U)` with `U ~ Uniform(0,1)`.
**Q2 [L2] Exponential.** Rate 0.5; `u = 0.9`. Sample? → `−ln(0.1)/0.5 = 4.605`.
**Q3 [L2] Rejection.** Target max density 3 under a Uniform(0,1) proposal. Acceptance rate? → `1/3`.
**Q4 [L2] LLN rate.** The SE of a mean is 0.2 at `n = 100`. SE at `n = 400`? → `0.1`.
**Q5 [L2] SE.** `s = 12`, `n = 36`. SE of the mean and 95% interval half-width? → `2`; `3.92`.
**Q6 [L2] Proportion.** `p̂ = 0.8`, `n = 400`. SE? → `√(0.16/400) = 0.02`.
**Q7 [L2] Sample size.** ±2 points at 95% for a proportion near 0.5? → `1.96²·0.25/0.0004 ≈ 2 401`.
**Q8 [L2] CLT.** 100 iid draws, mean 5, SD 2. `P(X̄ > 5.4)`? → `z = 0.4/0.2 = 2`; `≈ 0.0228`.
**Q9 [L3] Debug.** `rng.integers(0, 256) % 10` is used to draw digits. What is wrong? → Modulo bias (values 0–5 slightly more likely); use `rng.integers(0, 10)`.
**Q10 [L3] Debug.** A rejection sampler's histogram is flat where the target has a peak. → `M` too small: the bound `f ≤ M g` is violated near the peak, clipping the target.
**Q11 [L3] Debug.** Averaging per-GPU accuracies (batch sizes 1000, 1000, 200) gives 0.912 while the pooled accuracy is 0.920. → Unweighted mean of unequal-size batches; use size-weighted averaging.
**Q12 [L3] Analysis.** The running mean of request latencies keeps jumping by large amounts even at `n = 10⁶`. → Heavy tails (possibly infinite variance/mean); use medians/quantiles; check the tail index.
**Q13 [L3] Analysis.** A 95% interval for a rare-event rate (`p = 0.01`, `n = 200`) covers the truth only 85% of the time in simulation. → Normal approximation fails with `np = 2`; use Wilson/exact intervals or Poisson-based intervals.
**Q14 [L3] Analysis.** 10,000 user-level rows come from 200 users; the interval is "too good". → Rows within a user are correlated: design effect; compute SE at the user level.
**Q15 [L4] Design.** Plan the evaluation set size to detect a 1-point accuracy improvement. → Use the paired SE of the difference (pilot estimate of the disagreement rate), set `n` from `(1.96+z_power)² · Var(d)/δ²`; verify by simulation.
**Q16 [L4] Design.** You need reproducible parallel simulations. → One `SeedSequence`, `spawn` per worker, record the root seed and worker index, and test that results are identical across worker counts.
**Q17 [L4] Design.** Choose a decoding strategy for a creative-writing assistant vs a code assistant. → Temperature/top-p for diversity in creative writing; low temperature or greedy for code where correctness matters; evaluate on task-specific metrics; log sampling parameters.

### 6.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Random and inverse-transform sampling | 2 | 3 | 2 | 1 |
| Law of large numbers | 2 | 2 | 2 | 0 |
| Central limit theorem | 2 | 2 | 3 | 0 |
| Sampling distributions, SE | 2 | 3 | 2 | 2 |
| Token sampling | 1 | 1 | 2 | 1 |

### Check yourself (Unit 6)

1. Why include the unweighted-batch-mean item?
2. Which items need runnable code?

**Reference answers:** (1) Averaging metrics across unequal batches is a frequent distributed-evaluation bug. (2) All L3 items and any whose answer depends on simulation or floating-point behaviour.

---

## Unit 7 — Project index (`Projects/README.md`)

### 7.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Sampling from a next-token distribution | Inverse-transform sampling in a realistic setting; temperature/top-k/top-p implemented and validated; diversity/likelihood trade-offs | 1 (and Module 10 Lesson 2) | 7–8 h |
| 2 | CLT and LLN simulation lab | Convergence rates, CLT speed, interval coverage, and honest failure cases | 2–4 | 7–8 h |

Order: either order works; Project 2's coverage and SE helpers are reused by Project 1 for validating sampler frequencies. Outputs feed `mlmath/dists.py`/`sampling.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverables D10–D11) and notebook `11_sampling_limits.ipynb`. The sampler code is reused in Stage 5C-12.

### 7.2 Data policy

**No downloads.** Project 1 builds a toy language model in code (a bigram model trained on a small synthetic corpus, or a hand-specified next-token distribution). Project 2 generates all data from known distributions so true parameters are available. You may additionally apply the tools to any model or dataset you already have locally; keep it out of the repository and tests `[VERIFY: licence]`.

### 7.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (samplers match targets; theorems demonstrated with measured rates) | 30 |
| Failure-mode handling (ties, `k > V`, `T → 0`, heavy tails, dependence, tiny `n`) | 15 |
| Reproducibility (seeded, `SeedSequence`, pinned, clean venv, no downloads) | 15 |
| Explanation and statistical honesty (standard errors, coverage with its own SE, scoped claims) | 15 |
| Code quality (types, validation, docstrings stating conventions) | 15 |
| ML connection paragraph | 10 |

### 7.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 7)

1. What does Project 1 reuse from Project 2?
2. Which stage-library deliverables do these feed?

**Reference answers:** (1) The standard-error and coverage helpers for validating empirical frequencies. (2) D10 and D11 (`mlmath/dists.py`, `mlmath/sampling.py`).

---

## Unit 8 — Project: Sampling from a next-token distribution (`Projects/01-…md`)

### 8.1 Brief

Build `tokensamp`: samplers for a next-token distribution (greedy, temperature, top-k, top-p/nucleus), implemented from scratch with inverse-transform sampling on cumulative sums, each **validated against its analytically defined target distribution**, then used to generate text from a toy language model and to measure the trade-off between diversity and likelihood.

**Industry framing:** every deployed LLM applies these exact transformations to its logits. Bugs here (top-p off by one, temperature applied after truncation, un-normalized probabilities) quietly change product behaviour. The deliverable includes a validation suite that makes such bugs fail a test.

### 8.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Toy language model | A bigram model trained on a small synthetic corpus (generated in code) that returns **logits** for the next token given the previous token; vocabulary size ≥ 40; a few deterministic and a few high-entropy contexts |
| R2 | Stable softmax | `softmax(logits, T)` via log-softmax; `T → 0` handled explicitly as argmax; validates `T > 0` |
| R3 | Categorical sampler | Inverse transform with `np.searchsorted` on `cumsum`; guards against cumulative sums slightly below 1 (clip index); batch version drawing `N` samples at once |
| R4 | Greedy | `argmax` with deterministic tie-breaking (documented) |
| R5 | Temperature | `softmax(z / T)`; verify against the closed-form for 3-token examples |
| R6 | Top-k | Keep the `k` largest logits (ties documented), renormalize; `k ≥ V` returns the full distribution; `k = 1` equals greedy |
| R7 | Top-p (nucleus) | Smallest set of tokens (in descending probability) whose cumulative probability is **≥ p**; renormalize; define the tie and boundary rules explicitly (include the token that crosses `p`) |
| R8 | Composition and order | Defined order (temperature → top-k → top-p) and a test showing that changing the order changes the distribution |
| R9 | Validation suite | For each sampler and a grid of `(T, k, p)`: empirical frequencies from `N` samples vs the analytic target distribution, using **both** a total-variation tolerance derived from the expected TV **and** a Pearson chi-square statistic with pooled small cells (the chi-square check is the sensitive one: a dropped-token bug can hide under a loose TV tolerance); also assert that no zero-probability token is ever sampled; fail loudly on mismatch; report the **power** of the suite against each bug in §8.5 (detection rate over ≥ 20 seeds) |
| R10 | Text generation | Generate sequences from the bigram model with each strategy; seeded; stop token or max length |
| R11 | Diversity/likelihood metrics | Per-sequence log-likelihood (log-space sum), distinct-1/2-gram ratios, repetition rate, entropy of the next-token distribution along the generated path; averages with SEs over ≥ 100 sequences |
| R12 | Temperature/top-p sweeps | Curves of diversity vs mean log-likelihood across `T ∈ [0.2, 2]` and `p ∈ [0.5, 1]`; identify greedy's repetition loops |
| R13 | Edge cases | `T` very small/large, `k = 0` (error), `p` near 0 (at least one token kept), `p = 1`, logits with `-inf` (masked tokens), ties, `float32` logits |
| R14 | Reproducibility | Per-run `Generator` objects; `SeedSequence.spawn` for parallel generation; same seed ⇒ same text |
| R15 | Report | `REPORT.md`: validation tables (TV vs tolerance), sweeps with SEs, repetition analysis, the bug gallery below with measured effect sizes |

### 8.3 Layout and starter

```
tokensamp/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/tokensamp/{__init__,lm,sampling,validate,generate,metrics}.py
├── tests/{test_sampling,test_validate,test_generate}.py
├── notebooks/11_next_token_sampling.ipynb
└── results/
```

```python
# src/tokensamp/sampling.py
import numpy as np

def log_softmax(z):
    z = np.asarray(z, float); m = np.max(z[np.isfinite(z)]) if np.any(np.isfinite(z)) else 0.0
    shifted = z - m; lse = np.log(np.sum(np.exp(shifted)))
    return shifted - lse

def softmax(z, T=1.0):
    if T <= 0: raise ValueError("temperature must be > 0 (use greedy for T → 0)")
    return np.exp(log_softmax(np.asarray(z, float) / T))

def top_k_filter(p, k):
    if k < 1: raise ValueError("k must be ≥ 1")
    p = np.asarray(p, float); k = min(k, len(p))
    keep = np.argsort(-p, kind="stable")[:k]                     # ties: lower index first (documented)
    out = np.zeros_like(p); out[keep] = p[keep]; return out / out.sum()

def top_p_filter(p, top_p):
    if not (0 < top_p <= 1): raise ValueError("top_p must be in (0, 1]")
    p = np.asarray(p, float); order = np.argsort(-p, kind="stable"); cum = np.cumsum(p[order])
    cutoff = int(np.searchsorted(cum, top_p - 1e-12, side="left")) + 1       # smallest prefix with cumulative prob ≥ top_p
    keep = order[:cutoff]; out = np.zeros_like(p); out[keep] = p[keep]; return out / out.sum()

def sample_categorical(p, rng, size=None):
    p = np.asarray(p, float)
    if not np.isclose(p.sum(), 1.0, atol=1e-8): raise ValueError(f"probabilities sum to {p.sum()}")
    cum = np.cumsum(p); u = rng.random(size)
    return np.minimum(np.searchsorted(cum, u, side="right"), len(p) - 1)

def next_token_distribution(logits, T=1.0, top_k=None, top_p=None):
    p = softmax(logits, T)                                       # temperature first
    if top_k is not None: p = top_k_filter(p, top_k)
    if top_p is not None: p = top_p_filter(p, top_p)
    return p
```

```python
# src/tokensamp/validate.py
import math
import numpy as np

def tv_distance(freq, target): return 0.5 * float(np.sum(np.abs(freq - target)))

def tv_expected(target, N):
    """E[TV] of an N-sample empirical distribution: 0.5 · √(2/π) · Σ SE_i, SE_i = √(p_i(1−p_i)/N)."""
    se = np.sqrt(target * (1 - target) / N); return 0.5 * math.sqrt(2 / math.pi) * float(se.sum())

def tv_tolerance(target, N, mult=1.6):
    """A multiple of the expected TV. mult = 1.6 was calibrated on this module's runs (correct samplers peaked at ≈ 1.3×); [VERIFY] it on your own."""
    return mult * tv_expected(target, N)

def chi_square(counts, target, min_expected=5.0):
    """Pearson statistic with small-expectation cells pooled into one; returns (statistic, degrees of freedom)."""
    N = counts.sum(); E = target * N; big = E >= min_expected
    obs = np.r_[counts[big], counts[~big].sum()]; exp = np.r_[E[big], E[~big].sum()]; keep = exp > 0
    return float(np.sum((obs[keep] - exp[keep]) ** 2 / exp[keep])), int(keep.sum()) - 1

def chi_square_limit(df): return df + 6 * math.sqrt(2 * df)             # mean + 6 SD of a χ²_df; correct samplers stay far below it

def check_sampler(target, rng, N=400_000):
    from .sampling import sample_categorical
    idx = sample_categorical(target, rng, size=N); counts = np.bincount(idx, minlength=len(target)); freq = counts / N
    tv, tol = tv_distance(freq, target), tv_tolerance(target, N)
    stat, df = chi_square(counts, target); lim = chi_square_limit(df)
    zero_mass_hit = bool(np.any((freq > 0) & (target == 0)))
    return {"tv": tv, "tv_tol": tol, "chi2": stat, "chi2_limit": lim, "ok": (tv <= tol) and (stat <= lim) and not zero_mass_hit}
```

```python
# tests/test_sampling.py
import numpy as np
from tokensamp.sampling import *
from tokensamp.validate import check_sampler

def test_temperature_closed_form():
    z = np.array([2.0, 1.0, 0.0]); p = softmax(z, 1.0)
    assert np.allclose(p, np.exp(z) / np.exp(z).sum())
    assert softmax(z, 0.01).argmax() == 0 and softmax(z, 0.01)[0] > 0.999
    assert np.allclose(softmax(z, 1000.0), 1 / 3, atol=1e-3)

def test_top_k_and_top_p_support():
    p = np.array([0.5, 0.25, 0.15, 0.07, 0.03])
    assert np.count_nonzero(top_k_filter(p, 2)) == 2 and np.allclose(top_k_filter(p, 2)[:2], [2 / 3, 1 / 3])
    q = top_p_filter(p, 0.8); assert np.count_nonzero(q) == 3                          # 0.5 + 0.25 = 0.75 < 0.8 → include the 3rd token
    assert np.count_nonzero(top_p_filter(p, 0.5)) == 1                                # first token already has cumulative probability 0.5 ≥ 0.5
    assert np.count_nonzero(top_p_filter(p, 1.0)) == 5 and np.count_nonzero(top_k_filter(p, 99)) == 5

def test_samplers_match_their_targets():
    rng = np.random.default_rng(0); z = np.random.default_rng(1).normal(size=50)
    for T, k, tp in ((1.0, None, None), (0.7, None, None), (1.0, 10, None), (1.0, None, 0.9), (1.3, 20, 0.95)):
        target = next_token_distribution(z, T, k, tp); res = check_sampler(target, rng)
        assert res["ok"], (T, k, tp, res)

def top_p_missing_crossing_token(p, top_p):                  # the classic off-by-one: forgets to keep the token that crosses top_p
    p = np.asarray(p, float); o = np.argsort(-p, kind="stable"); cum = np.cumsum(p[o])
    cut = max(1, int(np.searchsorted(cum, top_p, side="left"))); out = np.zeros_like(p); out[o[:cut]] = p[o[:cut]]; return out / out.sum()

def test_validator_catches_the_top_p_off_by_one():
    z = np.random.default_rng(1).normal(size=50); base = softmax(z, 1.0)
    good, bad = top_p_filter(base, 0.9), top_p_missing_crossing_token(base, 0.9)
    assert np.count_nonzero(bad) == np.count_nonzero(good) - 1
    rng = np.random.default_rng(3)
    assert check_sampler(good, rng)["ok"]                                  # the correct target validates
    res = check_sampler(bad, rng)                                           # samples drawn from the BUGGY distribution, checked against the correct target
    from tokensamp.validate import tv_distance
    idx = sample_categorical(bad, rng, size=400_000); counts = np.bincount(idx, minlength=len(good))
    from tokensamp.validate import chi_square, chi_square_limit
    stat, df = chi_square(counts, good); assert stat > chi_square_limit(df)

def test_order_matters():
    z = np.random.default_rng(2).normal(size=30)
    a = next_token_distribution(z, T=0.5, top_p=0.9)                                   # temperature → top-p
    b = top_p_filter(softmax(z, 1.0), 0.9); b = b ** 2 / np.sum(b ** 2)                # top-p → (T=0.5 on the survivors)
    assert not np.allclose(a, b)

def test_masked_logits_never_sampled():
    z = np.array([1.0, -np.inf, 0.5]); p = softmax(z); assert p[1] == 0.0 and np.isclose(p.sum(), 1.0)
```

`[VERIFY]` In a seeded run (5 configurations × 20 seeds, `N = 200 000`) correct samplers had a TV of at most about 1.33× the expected TV, so the `1.6×` multiplier leaves headroom; re-measure before trusting it. Confirm the top-p boundary convention (`cumulative ≥ p`) against the library you compare with. **Why two checks:** with an earlier, looser TV tolerance (4× a sum of standard errors) the dropped-token top-p bug was detected in 0 of 40 runs, because it moves the distribution by only TV 0.0117, while the chi-square check detected it in 40 of 40 runs with 0 false alarms on the correct sampler (statistic ≈ 4,800 vs ≈ 34 expected with 33 degrees of freedom).

### 8.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Toy LM produces valid logits; `softmax` stable for logits of ±1000; categorical sampler frequencies pass the TV check on 10 random distributions |
| M2 | R4–R8 | Closed-form and support-size tests pass for temperature/top-k/top-p; order-sensitivity test passes |
| M3 | R9 | Validation grid (≥ 25 parameter combinations) all pass; the measured TV and chi-square statistics reported with their spread over ≥ 20 seeds; a detection-rate table for every bug in §8.5 showing the suite catches each (and which check caught it) |
| M4 | R10–R12 | Generated text for each strategy; metric tables with SEs over ≥ 100 sequences; diversity vs likelihood curves; greedy's repetition rate quantified |
| M5 | R13–R14 | All edge cases handled with documented behaviour; reproducibility test (same seed ⇒ same text; spawned seeds ⇒ different texts) |
| M6 | R15 | `REPORT.md` regenerated by one script; bug gallery with measured effect sizes |

### 8.5 The bug gallery (each must be reproduced, detected by a test, and its effect measured)

1. Top-p implemented as cumulative `> p` instead of `≥ p` at an exact boundary, or without including the crossing token (support one token too small). In a seeded run this removed 1 of 34 tokens (TV 0.0117 from the correct distribution): invisible to a loose TV test, obvious to the chi-square check.
2. Temperature applied *after* truncation (changes which tokens survive vs the intended order).
3. Forgetting to renormalize after truncation (probabilities sum to `< 1`; `searchsorted` index out of range).
4. Softmax without the max-subtraction (`nan` for large logits).
5. `rng.choice(p=...)` with float32 probabilities that sum to `1 ± 1e-7`.
6. Reusing the same generator for all positions *and* all prompts in a way that correlates prompts, or seeding with the same value in every worker.
7. Top-k with ties broken by an unstable sort (nondeterministic support).
8. Sampling from the full distribution while *scoring* likelihood under the truncated one (inconsistent reporting).

### 8.6 Statistical-honesty requirements

- Every reported metric is a mean over ≥ 100 generated sequences **with a standard error**; compare strategies with paired seeds or report overlapping intervals.
- Distinguish **sampler correctness** (frequencies match the target) from **sampler quality** (text is good); this project validates the former rigorously and measures proxies for the latter, and says so.
- Report the tolerance rule for the TV test and how it was calibrated.
- State that the toy bigram model's behaviour is **not** evidence about large language models; it demonstrates the mechanics.

### 8.7 Stretch goals

1. Min-p and typical sampling; validate against their definitions `[VERIFY: definitions]`.
2. Repetition penalties and their effect on the distribution (a deterministic transformation of logits).
3. Gumbel-max sampling vs inverse transform: equivalence test and a speed comparison on your machine.
4. Beam search vs sampling: log-likelihood and diversity comparison on the toy model.
5. Importance-weighted estimation of the probability of a rare token sequence under the full model while sampling from a truncated one (preview of 4C-04).

### 8.8 ML connection (README prompt)

Explain in your own words how each decoding knob changes the output distribution and why it changes behaviour (temperature = sharpening/flattening; top-k/top-p = truncating the tail), which knob you would use for tasks needing exactness vs creativity, and how you would test a production sampler for correctness (distributional tests on fixed logits).

### Check yourself (Unit 8)

1. What does top-p sampling keep?
2. Why can the order of temperature and truncation matter?
3. How do you test that a sampler is correct without a reference implementation?

**Reference answers:** (1) The smallest set of highest-probability tokens whose cumulative probability reaches `p`, renormalized. (2) Temperature reshapes the probabilities, which changes cumulative sums and therefore which tokens a probability-based cutoff (top-p) keeps. (3) Fix the logits, draw many samples, and compare the empirical frequencies with the analytically defined target using a tolerance derived from the sample size (total-variation or chi-square).

---

## Unit 9 — Project: CLT and LLN simulation lab (`Projects/02-…md`)

### 9.1 Brief

Build `limitlab`: a reusable, vectorized simulation harness that **demonstrates the LLN and CLT with measured rates**, quantifies how fast the normal approximation and interval coverage become reliable for different distributions and sample sizes, and **systematically exhibits where the theorems fail** (heavy tails, rare events, dependence). The deliverable is a tested toolkit and a report with honest tables, not just pretty histograms.

**Industry framing:** teams routinely claim "95% confidence" from a normal interval. This lab is the check you run, on a distribution resembling your own data, before you trust that claim.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Distribution registry | ≥ 10 distributions with known mean/variance (or documented absence): uniform, normal, exponential, lognormal, Bernoulli (`p = 0.5, 0.02`), Poisson, Pareto (`α = 3, 1.5, 1.1`), Cauchy, a two-component mixture; each with a sampler and a flag for finite mean/variance |
| R2 | LLN module | Running means with `±2σ/√n` bands where defined; error-vs-`n` curves (mean absolute error over many repetitions) and fitted log-log slopes with uncertainty |
| R3 | CLT module | Standardized means vs `N(0,1)`: KS distance, skewness and excess kurtosis vs `n`, quantile gaps at 1%/99%; fitted `1/√n` scaling and constants |
| R4 | Interval coverage | Coverage of Wald-`z`, Student-`t` (use tabulated quantiles for the needed degrees of freedom, documented), and percentile bootstrap intervals over a grid of distributions × `n`; every entry with its binomial standard error; minimal `n` achieving coverage ≥ 0.94 |
| R5 | Failure catalogue | (a) Cauchy: spread of the mean does not shrink; (b) Pareto `α = 1.5`: finite mean, infinite variance: slow/erratic, coverage never reaches nominal in the tested range; (c) Bernoulli `p = 0.02` small `n`; (d) AR(1) dependent data with `ρ ∈ {0.5, 0.9}`: coverage collapse and the effective-sample-size correction (Module 09 Lesson 4); (e) clustered data and the design effect |
| R6 | SE verification | Compare analytic SEs with simulated SEs for the mean, proportion, difference of means, and median; report ratios |
| R7 | Sample-size planner | Given a target half-width and a distribution family, returns `n` from the CLT formula and the `n` actually needed (from simulation) to achieve the target coverage and half-width; shows the gap for skewed data |
| R8 | Harness quality | Fully vectorized `(reps, n)` draws with memory-safe chunking; `SeedSequence`-based reproducibility; caching of results; a `--quick` mode for tests |
| R9 | Self-validation | Unit tests that the harness reproduces known facts (normal coverage ≈ 0.95 at `n = 30`, exponential KS slope ≈ −0.5, Cauchy IQR constant); statistical tolerances derived from the number of repetitions |
| R10 | Report | `REPORT.md`: tables with standard errors, convergence-rate fits, a "when can I trust a normal interval?" decision table, and a runbook |

### 9.3 Layout and starter

```
limitlab/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/limitlab/{__init__,registry,lln,clt,coverage,failures,planner}.py
├── tests/{test_registry,test_lln,test_clt,test_coverage}.py
├── notebooks/11_clt_lln_lab.ipynb
└── results/
```

```python
# src/limitlab/registry.py
import math
import numpy as np

def _pareto(a): return lambda rng, shape: 1 + rng.pareto(a, size=shape)
REGISTRY = {   # name: (sampler(rng, shape), mean, variance); None = does not exist (infinite)
    "uniform":        (lambda rng, s: rng.random(s), 0.5, 1 / 12),
    "normal":         (lambda rng, s: rng.normal(size=s), 0.0, 1.0),
    "exponential":    (lambda rng, s: rng.exponential(size=s), 1.0, 1.0),
    "lognormal":      (lambda rng, s: rng.lognormal(0, 1, size=s), math.exp(0.5), (math.e - 1) * math.e),
    "bernoulli0.5":   (lambda rng, s: (rng.random(s) < 0.5).astype(float), 0.5, 0.25),
    "bernoulli0.02":  (lambda rng, s: (rng.random(s) < 0.02).astype(float), 0.02, 0.02 * 0.98),
    "pareto3":        (_pareto(3.0), 1.5, 3.0 / 4.0),                        # classical Pareto, scale 1: mean α/(α−1), var α/((α−1)²(α−2))
    "pareto1.5":      (_pareto(1.5), 3.0, None),                              # finite mean, infinite variance
    "cauchy":         (lambda rng, s: rng.standard_cauchy(size=s), None, None),
}
```

```python
# src/limitlab/clt.py
import math
import numpy as np

_erf = np.vectorize(math.erf)
def ks_to_normal(z):
    s = np.sort(np.asarray(z, float)); n = len(s); F = 0.5 * (1 + _erf(s / math.sqrt(2)))
    return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(0, n) / n)))

def standardized_means(sampler, mu, var, n, reps, rng):
    if mu is None or var is None: raise ValueError("CLT standardization needs a finite mean and variance")
    return math.sqrt(n) * (sampler(rng, (reps, n)).mean(axis=1) - mu) / math.sqrt(var)
```

```python
# src/limitlab/coverage.py
import math
import numpy as np

T975 = {2: 4.303, 4: 2.776, 9: 2.262, 29: 2.045, 99: 1.984}                  # two-sided 95% Student-t quantiles `[VERIFY]` (df → value)

def wald_coverage(sampler, mu, n, reps, rng, crit=1.96):
    x = sampler(rng, (reps, n)); xbar = x.mean(axis=1); s = x.std(axis=1, ddof=1)
    hit = np.abs(xbar - mu) <= crit * s / math.sqrt(n)
    p = float(hit.mean()); return p, math.sqrt(p * (1 - p) / reps)

def coverage_table(names, ns, reps, seed, registry):
    rng = np.random.default_rng(seed); out = {}
    for nm in names:
        sampler, mu, _ = registry[nm]
        out[nm] = {n: wald_coverage(sampler, mu, n, reps, rng) for n in ns}
    return out
```

```python
# tests/test_coverage.py
import numpy as np, math
from limitlab.registry import REGISTRY
from limitlab.coverage import wald_coverage
from limitlab.clt import ks_to_normal, standardized_means

def test_normal_data_covered_near_95_at_n30():
    s, mu, _ = REGISTRY["normal"]; p, se = wald_coverage(s, mu, 30, 20_000, np.random.default_rng(0), crit=2.045)   # t quantile, df = 29
    assert abs(p - 0.95) < 4 * se + 0.003

def test_skewed_small_n_undercovers():
    s, mu, _ = REGISTRY["exponential"]; p, se = wald_coverage(s, mu, 10, 20_000, np.random.default_rng(1))
    assert p < 0.94

def test_clt_ks_shrinks_for_exponential_not_for_cauchy():
    rng = np.random.default_rng(2); s, mu, var = REGISTRY["exponential"]
    k_small = ks_to_normal(standardized_means(s, mu, var, 4, 20_000, rng)); k_big = ks_to_normal(standardized_means(s, mu, var, 400, 20_000, rng))
    assert k_big < k_small / 3
    c, _, _ = REGISTRY["cauchy"]; q = [np.subtract(*np.quantile(c(rng, (20_000, n)).mean(axis=1), [0.75, 0.25])) for n in (1, 400)]
    assert abs(q[0] - q[1]) < 0.15 * q[0]                     # interquartile range of the mean does not shrink

def test_finite_variance_flags():
    assert REGISTRY["pareto1.5"][2] is None and REGISTRY["cauchy"][1] is None
```

`[VERIFY]` Confirm each tolerance by running the suite; the `skewed small-n` threshold (`p < 0.94`) and the Cauchy IQR tolerance depend on the number of repetitions: measure the actual values over several seeds and record them before asserting numeric bounds. Re-derive the Pareto mean/variance entries from the definition before trusting them.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1, R8 | Registry complete with documented moments; harness vectorized, chunked, reproducible; `--quick` mode under 30 seconds |
| M2 | R2 | Fitted LLN slope within 0.05 of −0.5 for normal/exponential; clearly shallower for Pareto `α = 1.1` and `1.5`; Cauchy flagged |
| M3 | R3 | KS-vs-`n` tables with the sampling floor stated; fitted `1/√n` slope for skewed distributions; kurtosis/skewness trends |
| M4 | R4, R6 | Coverage table (≥ 8 distributions × ≥ 6 values of `n`) with binomial standard errors; analytic-vs-simulated SE ratios within 3% |
| M5 | R5, R7 | All five failure cases reproduced with numbers; planner shows the CLT-formula `n` vs simulation-required `n` for at least three distributions |
| M6 | R9–R10 | Self-validation tests pass; `REPORT.md` regenerated by one script; decision table backed by the coverage data |

### 9.5 Statistical-honesty requirements

- Every coverage value comes with its **binomial standard error** (`√(p(1−p)/reps)`); do not compare coverages that differ by less than ~3 SE.
- State the **sampling floor** of each KS estimate (≈ `1/√reps`); a "KS = 0.006" at `reps = 20 000` is not zero.
- Fitted slopes include a **standard error** from the regression or from repeated seeds.
- The failure catalogue must include a **case where the naive interval looks fine at small `n` by luck** (e.g., one seed) and show it breaks under many seeds.
- Clearly separate **asymptotic** statements (CLT) from **finite-sample** measurements (this lab).

### 9.6 Failure modes to demonstrate

Cauchy and infinite-variance heavy tails; rare-event proportions; autocorrelated data treated as i.i.d.; clustered rows; using `z` instead of `t` at tiny `n`; too few repetitions for a coverage claim (coverage noise); memory blow-up from huge `(reps, n)` matrices; unseeded or reused generators; standardizing with an estimated `σ` and forgetting the extra variability.

### 9.7 Stretch goals

1. Studentized-mean and percentile-bootstrap-`t` intervals; compare coverage with Wald for skewed data `[VERIFY: methods]`.
2. Edgeworth-style skewness correction `[VERIFY]` and its effect on coverage.
3. Block bootstrap for the AR(1) series; compare with the effective-sample-size correction.
4. Delta-method intervals for a ratio or a log of a mean, validated by simulation.
5. Stable-distribution experiments: the scaled sum of Pareto `α < 2` variables converges to a non-normal limit; measure the scaling exponent `n^{1/α}` `[VERIFY]`.

### 9.8 ML connection (README prompt)

Write a one-page "can I trust this interval?" checklist for an evaluation metric (sample size, skew/tails, dependence between rows, rare outcomes), each item tied to a failure case in this lab, with the recommended alternative (Wilson/exact, bootstrap, cluster-robust SE, larger sample).

### Check yourself (Unit 9)

1. Why report the binomial standard error of a coverage estimate?
2. What does the Cauchy experiment show about the CLT?
3. What is the first thing to check before trusting a normal interval on skewed or rare-event data?

**Reference answers:** (1) A coverage estimate from a finite number of repetitions is itself noisy; differences smaller than a few SE are not evidence of a real difference. (2) That the CLT needs finite variance: the mean of Cauchy draws has the same spread however large `n` is. (3) Measure the actual coverage by simulating from a distribution that resembles your data at your sample size.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 4 lessons, 2 projects, 9 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 08–10 and 12–13, 4C-04/05, and Stage 5 pointers (5A-06/07/11, 5B-04/10, 5C-03/12, 5D-06/12) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: PCG64 default and `SeedSequence` independence guarantees, weak/strong LLN statements, DKW and Berry–Esseen forms and constants, stable-law behaviour for Pareto `α < 2`, Student-`t` quantile values, standard errors of the median and variance, importance-sampling variance behaviour, top-p/min-p/typical-sampling definitions.
4. `[VERIFY]` All printed numerical results (convergence slopes, KS tables, coverage tables, TV/tolerance ratios) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3): every lesson snippet executed; all 6 `tokensamp` and all 4 `limitlab` tests passed. Defects found and fixed during the run: the first sampler-validation design used a total-variation tolerance so loose (about 5× the actual TV) that the dropped-token top-p bug was detected in 0 of 40 runs, whereas a Pearson chi-square check detected it in 40 of 40 with 0 false alarms, so the validator now uses both and a test asserts the bug is caught; a one-dataset bootstrap-SE demo was misleading (0.053 vs a true 0.089) and now shows the spread over 150 datasets (mean 0.0915, SD 0.017, range 0.050–0.145). Measured in seeded runs: (a) rejection-sampling acceptance 0.4072 vs `1/M = 0.4069`; reservoir inclusion frequencies 0.246–0.253 vs `k/n = 0.25`; the naive swap-with-any-index shuffle gave permutation frequencies 0.146–0.186 vs 0.1667; (b) LLN: log-log slope of the mean absolute error vs `n` was −0.50 (normal, exponential), −0.30 (Pareto α = 1.5) and −0.01 (Pareto α = 1.1); the Cauchy running mean never settled; Chebyshev's bound was loose (0.0126 observed vs 0.16); (c) CLT: KS distance of standardized means to N(0,1) at `n = 30` was 0.007 (uniform), 0.030 (exponential), 0.059 (lognormal), 0.331 (Bernoulli 0.02); the Cauchy mean's interquartile range stayed ≈ 2 for `n = 1, 10, 1000`; the exponential KS slope was −0.45 down to the sampling floor; (d) coverage of the nominal 95% `z` interval at `n = 10, 30, 100, 1000`: exponential 0.869/0.917/0.938/0.947, lognormal 0.806/0.874/0.918/0.944, Bernoulli(0.02) 0.186/0.454/0.864/0.949; Pareto α = 3 at `n = 30, 300, 3000`: 0.860/0.925/0.948; Pareto α = 1.5: 0.646/0.735/0.782 (never reaching nominal); (e) dependent data (`n = 200`): AR(1) coverage of the iid-formula interval was 0.951, 0.743, 0.343 for `ρ = 0, 0.5, 0.9`, and 0.951, 0.954, 0.930 after the effective-sample-size correction; (f) with `n = 5` normal data the `z` interval covered 0.877 vs 0.950 for the `t` interval; clustered data's SE was 0.0823 vs 0.0316 from the iid formula (`√deff` prediction 0.0819); (g) `tokensamp` validation: correct samplers had TV at most about 1.33× the expected TV and chi-square statistics ≈ 34 (33 degrees of freedom). Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No convergence rate, coverage, interval, or tolerance figure appears without the measurement that produced it.
