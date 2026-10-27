# SYLLABUS — 12-Inferential-Statistics-for-Experiments-and-Evals (S4B-12)

**Stage 4B — Mathematics for Machine Learning · Module 12 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy and the standard library; **SciPy is never required** (the module builds the few distribution functions it needs, in Unit 1, and SciPy is optional only for cross-checks), Matplotlib and pytest where stated. All datasets are **synthetic and generated in code**, so true effects are known and every method can be audited. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation (and the shared `inferkit` helpers) | `README.md` | Beginner |
| 2 | Confidence intervals | `01-confidence-intervals.md` | Beginner → Intermediate |
| 3 | Bootstrap resampling | `02-bootstrap-resampling.md` | Intermediate |
| 4 | Hypothesis testing and p-values | `03-hypothesis-testing-and-p-values.md` | Intermediate |
| 5 | t-tests and paired tests for model comparison | `04-t-tests-and-paired-tests-for-model-comparison.md` | Intermediate → Advanced |
| 6 | Tests for proportions and A/B testing | `05-tests-for-proportions-and-ab-testing.md` | Intermediate → Advanced |
| 7 | Effect size, sample size, and statistical power | `06-effect-size-sample-size-and-statistical-power.md` | Advanced |
| 8 | Correlation vs causation, confounding, and sampling bias | `07-correlation-versus-causation-confounding-and-sampling-bias.md` | Advanced |
| 9 | Practice question bank | `practice-questions.md` | All levels |
| 10 | Project index | `Projects/README.md` | Intermediate |
| 11 | Project: is prompt B really better? | `Projects/01-is-prompt-b-really-better.md` | Intermediate → Advanced |
| 12 | Project: bootstrap confidence-interval lab | `Projects/02-bootstrap-confidence-interval-lab.md` | Advanced |
| 13 | Project: A/B test analysis report | `Projects/03-ab-test-analysis-report.md` | Advanced |

**Prerequisites:** Module 09 (probability, Bayes, independence, expectation/variance, correlation), Module 10 (binomial, normal, Beta, Poisson), Module 11 (sampling distributions, standard error, CLT/LLN, coverage studies, effective sample size, design effect), Module 08 (`σ²/B`, seeds as noise). **Plan slot:** weeks 14–15 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** required on every track, since this module turns "version B scored higher" into a defensible decision. Interviews and design reviews for ML evaluation routinely probe exactly these topics `[JUDGEMENT]`.

**Teaching stance (industry, not university):** the questions are *"Is this difference real, how big is it, how sure are we, and what should we do?"* Every method is introduced with (1) the decision it supports, (2) a from-scratch implementation, (3) a **simulation that checks its error rates** (false-positive rate, coverage, power), and (4) the situations where it is silently wrong. You never ship a p-value or interval whose operating characteristics you have not measured.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (formula, simulation, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Model comparison, prompt comparison, and product experiments all ask whether an observed difference is signal or noise. Test sets are finite, metrics are averages of noisy items, runs differ by seed, and teams look at many metrics, segments, and variants. Without inferential statistics, the typical outcomes are shipping noise ("B won by 0.6 points on 200 prompts"), missing real improvements (underpowered tests), and publishing intervals that do not mean what they claim.

### 1.2 Outcomes

1. Construct and interpret confidence intervals for means, proportions, and differences, and verify their coverage by simulation.
2. Implement the percentile, basic, and studentized bootstrap, including paired and cluster variants, and know when each fails.
3. State what a p-value is and is not; run permutation, t, Welch, paired, McNemar, and two-proportion tests; control multiplicity (Bonferroni, Holm, Benjamini–Hochberg).
4. Quantify how peeking, multiple metrics, and segment-fishing inflate false positives, and design analyses that avoid it.
5. Choose an effect-size measure, compute power and the minimal detectable effect, and plan the number of eval items or users *before* running a test.
6. Recognize confounding, selection bias, colliders, and leakage, and explain why randomization (not statistics) is the primary defence.
7. Deliver a complete, honest comparison report: effect, interval, test, power, assumptions, caveats, and a decision rule fixed in advance.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Confidence intervals | Error bars on every metric | CI toolkit; coverage checks |
| 2 | Bootstrap | Intervals for AUC, F1, medians, any metric | Paired/cluster bootstrap; failure cases |
| 3 | Hypothesis tests, p-values | "Is B better?"; many metrics | Permutation test; multiplicity; peeking inflation |
| 4 | t-tests, paired tests | Comparing models on shared items | Welch/paired t; McNemar; CV-fold pitfalls |
| 5 | Proportion tests, A/B testing | Conversion, win rate, rollout | z-test, Fisher, SRM, Bayesian A/B |
| 6 | Effect size, sample size, power | How many items/users? | Power curves; winner's curse |
| 7 | Causation, confounding, bias | Observational vs experimental evidence | Confounding, selection, leakage demos |

### 1.4 Concept map

```
data → estimate ± uncertainty:  SE → confidence interval (analytic: z/t/Wilson; resampling: bootstrap)
decision question "is B better?":   H0: no difference ─► test statistic ─► p-value ─► reject at level α?   (Type I error α, Type II error β)
       ├─ continuous scores:   t / Welch / paired t   (paired when both models see the same items)
       ├─ pass/fail outcomes:  McNemar (paired)  ·  two-proportion z / Fisher (independent arms)
       ├─ any statistic:       bootstrap / permutation
       └─ many looks, metrics, segments:  multiplicity (Bonferroni · Holm · BH) and optional-stopping inflation
planning:  effect size δ, α, power 1−β ─► required n  ·  minimal detectable effect  ·  winner's curse when underpowered
validity:  randomization ─► causal claim;  confounding / selection / leakage ─► a significant result can still be wrong
```

### 1.5 Environment, shared helpers, and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest        # scipy optional, for cross-checks only
```

The following small module (`inferkit.py`) supplies the normal and Student-`t` functions used by every lesson, so nothing depends on SciPy. It is verified against known quantiles in the Unit 2 lab.

```python
# inferkit.py
import math

def _betacf(a, b, x, itmax=300, eps=1e-14):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = d if abs(d) > 1e-300 else 1e-300
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = d if abs(d) > 1e-300 else 1e-300
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        d = 1.0 / d; delta = d * c; h *= delta
        if abs(delta - 1.0) < eps: break
    return h

def betainc(a, b, x):
    """Regularized incomplete beta function I_x(a, b) (continued-fraction evaluation)."""
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    ln_front = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1) / (a + b + 2): return math.exp(ln_front) * _betacf(a, b, x) / a
    return 1.0 - math.exp(ln_front) * _betacf(b, a, 1 - x) / b

def t_cdf(t, df):
    p_tail = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))        # P(T > |t|)
    return 1 - p_tail if t > 0 else p_tail

def t_ppf(q, df):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return (lo + hi) / 2

def norm_cdf(z): return 0.5 * math.erfc(-z / math.sqrt(2))
def norm_ppf(q):
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if norm_cdf(mid) < q else (lo, mid)
    return (lo + hi) / 2

def two_sided_p_from_z(z): return math.erfc(abs(z) / math.sqrt(2))
def two_sided_p_from_t(t, df): return 2 * (1 - t_cdf(abs(t), df))
```

Rules for every lab: **state the decision first** (what would you do if the result is significant / not?); **fix `α`, the test, and the metric before looking at results**; report an **effect size with an interval**, not only a p-value; for every method, **simulate its error rates** (false-positive rate under no difference, coverage, power under a known effect) with the **standard error of those rates**; seed all randomness; and state the assumptions (independence, pairing, tails) each time.

### 1.6 Checkpoints (from the stage plan)

- Bootstrap and analytic intervals for a mean agree closely on Gaussian data (width ratio ≈ 0.97 in a seeded run). On heavy-tailed data the audit shows something more useful than disagreement: the two methods *still agree with each other* (width ratio ≈ 0.95 for Pareto `α = 1.5`) while **both badly under-cover** (≈ 0.72 and 0.71 at `n = 100`), so agreement between two intervals is not evidence that either is valid.
- Your analysis procedure for "is prompt B better?" has a measured false-positive rate close to its nominal `α` under no true difference, and a measured power you can state for a stated effect and sample size.

### Check yourself (Unit 1)

1. Name the three things you must fix *before* looking at experimental results.
2. Why do we simulate a method's false-positive rate instead of trusting the textbook?

**Reference answers:** (1) The metric, the test (and `α`), and the stopping rule/sample size (also the decision threshold). (2) The textbook rate is asymptotic and assumption-dependent; heavy tails, dependence, small samples, peeking, and multiplicity can make the realized rate very different.

---

## Unit 2 — Confidence intervals (`01-…md`)

### 2.1 Why ML needs this

Every reported metric (accuracy, win rate, mean score, latency) is an estimate from a finite sample. A confidence interval says how precisely it is known and whether a claimed gain could be noise. "B is 2 points better" is not a finding without an interval.

### 2.2 Intuition

If you repeated the experiment many times and built an interval each time with a 95% procedure, about 95% of those intervals would contain the true value. The **procedure** has 95% coverage; any one computed interval either contains the truth or does not.

### 2.3 Mechanics

- **Interval for a mean:** `x̄ ± q · s/√n`, where `q` is the `t` quantile with `n − 1` degrees of freedom (`z = 1.96` for large `n`). For small `n` the `t` quantile is larger (`2.776` at 4 degrees of freedom), correcting for estimating `σ` by `s`.
- **Proportions:** Wald `p̂ ± z√(p̂(1−p̂)/n)` is poor near 0 or 1 or at small `n`; **Wilson** and **Clopper–Pearson** are the safer choices (Module 09–10).
- **Difference of independent means:** `(x̄₁ − x̄₂) ± q·√(s₁²/n₁ + s₂²/n₂)` (Welch degrees of freedom, Lesson 4). **Paired differences:** the interval for the mean of within-pair differences (Lesson 4).
- **Width:** `∝ s/√n`; quadrupling `n` halves the width (Module 11).
- **Confidence level trade-off:** higher level ⇒ wider interval (`z = 1.645, 1.96, 2.576` for 90/95/99%).
- **Correct interpretation:** "a procedure that captures the true parameter 95% of the time under repeated sampling". Not "95% probability the parameter is in this interval" (that is a *credible* interval, a Bayesian statement under a prior, Module 10 Lesson 6) `[VERIFY: wording]`.
- **Intervals vs tests (duality):** a 95% interval excludes `0` exactly when the corresponding two-sided test at `α = 0.05` rejects `H0: difference = 0`, for the *same* underlying statistic.
- **Overlapping intervals ≠ no significant difference:** two 95% intervals can overlap while their *difference* is significant, because the SE of a difference is `√(SE₁² + SE₂²)`, smaller than `SE₁ + SE₂`. Compare differences, not overlaps.
- **Interval vs prediction interval:** an interval for a mean is not a range for a new observation (`√(σ² + σ²/n)` wider).
- **Assumptions:** independence (clusters and time series need adjusted SEs, Module 11 Lesson 4), a roughly normal sampling distribution (CLT; skew and heavy tails need larger `n` or the bootstrap), and a representative sample (Lesson 7).
- **Reporting practice:** state the estimate, interval, level, `n`, and the method; prefer intervals to bare p-values.

**Worked example:** 200 eval prompts, 164 correct: `p̂ = 0.82`; Wilson 95% interval `≈ [0.761, 0.867]`; a rival model at 0.84 (also `n = 200`) lies well inside it: not distinguishable from 0.82.

### 2.4 Code

```python
import math
import numpy as np
from inferkit import t_ppf, norm_ppf, norm_cdf, two_sided_p_from_z
rng = np.random.default_rng(0)

# --- verify the helpers against known quantiles
for df, ref in ((1, 12.706), (4, 2.776), (9, 2.262), (29, 2.045), (1000, 1.962)): assert abs(t_ppf(0.975, df) - ref) < 1e-3
assert abs(norm_ppf(0.975) - 1.959964) < 1e-5

def mean_ci(x, level=0.95, kind="t"):
    x = np.asarray(x, float); n = len(x); se = x.std(ddof=1) / math.sqrt(n); a = 1 - (1 - level) / 2
    q = t_ppf(a, n - 1) if kind == "t" else norm_ppf(a)
    return x.mean() - q * se, x.mean() + q * se

def wilson(k, n, level=0.95):
    z = norm_ppf(1 - (1 - level) / 2); p = k / n; den = 1 + z * z / n; ctr = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den; return ctr - half, ctr + half

print("worked example Wilson(164/200):", np.round(wilson(164, 200), 3))

# --- the repeated-sampling meaning: simulate many experiments and count how often the interval contains the truth
mu, sigma, n, reps = 10.0, 3.0, 12, 20_000
X = rng.normal(mu, sigma, size=(reps, n)); xbar = X.mean(1); s = X.std(1, ddof=1)
for kind, q in (("z", 1.96), ("t", t_ppf(0.975, n - 1))):
    cov = np.mean(np.abs(xbar - mu) <= q * s / math.sqrt(n)); print(f"n={n}: {kind} interval coverage {cov:.3f} ± {math.sqrt(cov * (1 - cov) / reps):.3f}")

# --- width ∝ 1/√n
def half_width(n_):
    lo, hi = mean_ci(rng.normal(0, 1, n_)); return (hi - lo) / 2
for n_ in (25, 100, 400, 1600): print(f"n={n_:5d}: mean half-width {np.mean([half_width(n_) for _ in range(300)]):.4f}  (≈ t·1/√n; z-based 1.96/√n = {1.96 / math.sqrt(n_):.4f})")

# --- overlapping 95% intervals can still hide a significant difference
n = 100; a = rng.normal(0.00, 1, n); b = rng.normal(0.33, 1, n)
(lo_a, hi_a), (lo_b, hi_b) = mean_ci(a), mean_ci(b); se_d = math.sqrt(a.var(ddof=1) / n + b.var(ddof=1) / n); z = (b.mean() - a.mean()) / se_d
print(f"CI A [{lo_a:.2f}, {hi_a:.2f}]  CI B [{lo_b:.2f}, {hi_b:.2f}]  overlap: {lo_b < hi_a}   difference z = {z:.2f}, p = {two_sided_p_from_z(z):.3f}")

# --- Wald vs Wilson coverage for a small proportion
def cover_prop(method, p, n, reps=20_000):
    k = rng.binomial(n, p, reps); hit = 0
    for kk in k:
        ph = kk / n
        lo, hi = wilson(int(kk), n) if method == "wilson" else (ph - 1.96 * math.sqrt(ph * (1 - ph) / n), ph + 1.96 * math.sqrt(ph * (1 - ph) / n))
        hit += lo <= p <= hi
    return hit / reps
print("coverage at p=0.03, n=100:  Wald", round(cover_prop("wald", 0.03, 100), 3), "  Wilson", round(cover_prop("wilson", 0.03, 100), 3))

# --- the duality: a 95% CI for a difference excludes 0 iff the two-sided z test rejects (same statistic)
d = b.mean() - a.mean(); lo, hi = d - 1.96 * se_d, d + 1.96 * se_d; assert (lo > 0 or hi < 0) == (two_sided_p_from_z(d / se_d) < 0.05)

# --- confidence interval vs prediction interval
x = rng.normal(0, 2, 50); ci = mean_ci(x); pred_half = t_ppf(0.975, 49) * x.std(ddof=1) * math.sqrt(1 + 1 / 50)
print("mean CI half-width:", (ci[1] - ci[0]) / 2, " prediction-interval half-width:", pred_half)
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| "95% probability the true value is in this interval" | Misreported guarantee | State the repeated-sampling meaning, or use a credible interval explicitly |
| Wald interval for small or extreme proportions | Zero-width intervals, coverage far below 95% | Wilson / Clopper–Pearson |
| `z` instead of `t` at small `n` | Intervals too narrow | `t` quantile with `n − 1` degrees of freedom |
| Comparing groups by whether their intervals overlap | Real differences dismissed (or the reverse) | Compute the interval/test for the *difference* |
| Treating clustered or time-series rows as independent | Intervals far too narrow | Cluster-aware SEs; effective sample size (Module 11) |
| Interval for the mean read as the range of individual outcomes | Wrong operational meaning | Prediction interval |
| Reporting the interval but not `n`, level, or method | Not reproducible | Report all four |
| Skewed or heavy-tailed data with a normal interval | Under-coverage | Bootstrap / transformations / larger `n` (Lesson 3, Module 11) |
| Choosing the interval method after seeing the data | Selective reporting | Fix the method in advance |

### 2.6 ML link

- **Error bars on every offline metric** (accuracy, F1, mean rubric score, perplexity) and on online metrics (Stage 5A-06, 5D-12).
- **Eval-set sizing:** interval width tells you whether more test data will change a decision (Lesson 6).
- **Model cards and leaderboards** should report intervals; a ranking within overlapping uncertainty is not a ranking.
- **Seed variability:** an interval across training seeds is part of every serious comparison (Module 08 Project 2).

### 2.7 Lab (75 min)

1. Verify the `inferkit` quantiles against the tabulated values; plot the `t` quantile vs degrees of freedom converging to `1.96`.
2. Coverage lab: `z` vs `t` for normal data at `n ∈ {3, 5, 10, 30}`; report coverage with its binomial standard error (≥ 20,000 repetitions).
3. Proportion lab: Wald vs Wilson vs Clopper–Pearson (Module 10) at `(p, n) ∈ {(0.03, 100), (0.5, 100), (0.5, 20), (0.9, 50)}`.
4. Reproduce the overlapping-intervals trap; find the largest gap between means (in SE units) for which 95% intervals overlap yet the difference is significant.
5. Build `mean_ci`, `wilson`, and `diff_ci` as a tested function set (inputs validated; `n < 2` raises a clear error).

### Check yourself (Unit 2)

1. State precisely what "95% confidence" refers to.
2. Why can two overlapping 95% intervals still correspond to a significant difference?
3. Which interval for a proportion do you use at `p̂ = 0.02`, `n = 150`?

**Reference answers:** (1) The long-run fraction of intervals produced by the procedure that contain the true parameter. (2) The SE of the difference is `√(SE₁² + SE₂²)`, smaller than `SE₁ + SE₂`, so a difference of up to about `1.4×` the half-width can still be significant while the intervals overlap. (3) Wilson (or Clopper–Pearson); not Wald.

---

## Unit 3 — Bootstrap resampling (`02-…md`)

### 3.1 Why ML needs this

Most ML metrics (AUC, F1, BLEU-like scores, medians, ratios) have no simple standard-error formula. The bootstrap gives an SE and an interval for essentially **any statistic** by letting the data stand in for the population. It is also the practical tool for **paired model comparisons** and for **clustered** evaluation data.

### 3.2 Intuition

Treat your sample as if it were the population. Repeatedly draw new samples *from your sample* (same size, with replacement), recompute the statistic each time, and look at how it varies. That spread approximates the sampling variability you would see with fresh data.

### 3.3 Mechanics

- **Algorithm:** for `b = 1…B`: draw indices `i₁…i_n` uniformly with replacement; compute `θ̂*_b = T(x_{i₁}, …, x_{i_n})`. Use the `B` replicates.
- **Bootstrap SE:** the standard deviation of the replicates.
- **Intervals:**
  - **Percentile:** the `α/2` and `1 − α/2` quantiles of the replicates; simple and widely used.
  - **Basic (reverse percentile):** `[2θ̂ − q_{1−α/2}, 2θ̂ − q_{α/2}]`.
  - **Bootstrap-t (studentized):** bootstrap the pivot `(θ̂* − θ̂)/SE*`; better coverage for skewed statistics at the cost of needing an SE inside each replicate.
  - **BCa:** bias-corrected and accelerated percentile intervals; improved accuracy `[VERIFY: formula; outline only]`.
- **Choosing `B`:** 1,000–2,000 are typical for an SE, 5,000–10,000 for stable interval end-points; the Monte Carlo error of the interval shrinks with `B` but the statistical error depends on `n`.
- **Paired bootstrap for model comparison:** resample **items** (rows), keeping both models' outputs for each item together, and compute the metric *difference* on each resample: this preserves the pairing and gives an interval for the improvement.
- **Cluster bootstrap:** when rows are grouped (users, documents, prompts with several samples), resample **clusters**, not rows; otherwise intervals are too narrow (design effect, Module 11).
- **Block bootstrap:** for time series, resample contiguous blocks to preserve autocorrelation.
- **When the bootstrap fails:** very small `n`; extreme statistics (the maximum/minimum: the bootstrap distribution of the maximum cannot exceed the observed maximum, so intervals are inconsistent); heavy tails with infinite variance; dependent data resampled as i.i.d.; non-smooth statistics; a biased estimator (the bootstrap estimates variability, not bias).
- **Permutation vs bootstrap:** permutation tests (Lesson 3) resample *under the null* (shuffling labels); the bootstrap resamples to estimate the sampling distribution under the observed data.
- **Vectorized implementation:** `rng.integers(0, n, size=(B, n))` indexes all resamples at once; chunk if `B·n` is large.
- **Out-of-bag/validation analogue:** the ≈ 63.2% of distinct items per resample is a known property `1 − (1 − 1/n)ⁿ → 1 − e⁻¹` `[VERIFY]`.

**Worked example:** the median of 40 skewed values has no clean SE formula; 2,000 bootstrap resamples of the median give a distribution whose standard deviation is the SE and whose 2.5%/97.5% quantiles form the 95% percentile interval.

### 3.4 Code

```python
import math
import numpy as np
from inferkit import t_ppf
rng = np.random.default_rng(0)

def bootstrap_stats(x, stat, B=2000, rng=rng):
    x = np.asarray(x); idx = rng.integers(0, len(x), size=(B, len(x)))
    return np.array([stat(x[i]) for i in idx])

def percentile_ci(reps, level=0.95): a = (1 - level) / 2; return tuple(np.quantile(reps, [a, 1 - a]))
def basic_ci(theta_hat, reps, level=0.95): lo, hi = percentile_ci(reps, level); return 2 * theta_hat - hi, 2 * theta_hat - lo

# --- SE and intervals for a median (no simple formula)
x = rng.lognormal(0, 1, 40); reps = bootstrap_stats(x, np.median)
print("median", np.median(x), " bootstrap SE", reps.std(ddof=1), " percentile CI", np.round(percentile_ci(reps), 3), " basic CI", np.round(basic_ci(np.median(x), reps), 3))

# --- bootstrap vs analytic interval for a mean: normal data (agree) and heavy-tailed data (differ)
def t_interval(x): n = len(x); h = t_ppf(0.975, n - 1) * x.std(ddof=1) / math.sqrt(n); return x.mean() - h, x.mean() + h
for name, data in (("normal", rng.normal(5, 2, 100)), ("Pareto α=1.5", 1 + rng.pareto(1.5, 100))):
    lo_b, hi_b = percentile_ci(bootstrap_stats(data, np.mean, B=4000)); lo_t, hi_t = t_interval(data)
    print(f"{name:13s} t-interval width {hi_t - lo_t:7.3f}   bootstrap width {hi_b - lo_b:7.3f}   ratio {(hi_b - lo_b) / (hi_t - lo_t):.2f}")

# --- the bootstrap estimates variability, and its coverage must be checked: skewed data, small n
def coverage_boot(sampler, mu, n, reps_outer=1500, B=400):
    hit_p = hit_t = 0
    for _ in range(reps_outer):
        d = sampler(n); lo, hi = percentile_ci(bootstrap_stats(d, np.mean, B=B)); hit_p += lo <= mu <= hi
        lo2, hi2 = t_interval(d); hit_t += lo2 <= mu <= hi2
    return hit_p / reps_outer, hit_t / reps_outer
for n in (10, 30, 100):
    p_b, p_t = coverage_boot(lambda m: rng.exponential(size=m), 1.0, n); print(f"exponential n={n:3d}: percentile-bootstrap coverage {p_b:.3f}   t-interval coverage {p_t:.3f}")

# --- paired bootstrap for model comparison (resample ITEMS; keep both models' outcomes together)
n = 400; difficulty = rng.normal(size=n)
a = (rng.random(n) < 1 / (1 + np.exp(-(1.0 - difficulty)))).astype(float)
b = (rng.random(n) < 1 / (1 + np.exp(-(1.2 - difficulty)))).astype(float)
idx = rng.integers(0, n, size=(5000, n)); diffs = (b[idx] - a[idx]).mean(axis=1)
naive = np.array([b[rng.integers(0, n, n)].mean() - a[rng.integers(0, n, n)].mean() for _ in range(5000)])      # WRONG: breaks the pairing
print(f"observed difference {b.mean() - a.mean():+.3f}   paired-bootstrap SE {diffs.std(ddof=1):.4f}   unpaired (pairing broken) SE {naive.std(ddof=1):.4f}")
print("paired 95% CI for the improvement:", np.round(percentile_ci(diffs), 3))

# --- cluster bootstrap: rows grouped by user
users, per = 60, 15; u_eff = rng.normal(size=users)
y = (u_eff[:, None] + rng.normal(size=(users, per)))                         # rows within a user are correlated
rows = y.ravel(); true_se = np.std([(rng.normal(size=users)[:, None] + rng.normal(size=(users, per))).mean() for _ in range(4000)], ddof=1)
row_boot = bootstrap_stats(rows, np.mean, B=3000).std(ddof=1)
cl_idx = rng.integers(0, users, size=(3000, users)); cl_boot = y[cl_idx].mean(axis=(1, 2)).std(ddof=1)
print(f"true SE {true_se:.4f}   row bootstrap {row_boot:.4f} (too small)   cluster bootstrap {cl_boot:.4f}")

# --- failure: the bootstrap for the maximum cannot work (it never exceeds the observed max)
cover = 0
for _ in range(2000):
    u = rng.random(50); reps_max = bootstrap_stats(u, np.max, B=300); lo, hi = percentile_ci(reps_max); cover += lo <= 1.0 <= hi
print("percentile-bootstrap coverage of the true upper endpoint of Uniform(0,1) via the sample max:", cover / 2000)

# --- block bootstrap for an AR(1) series
def ar1(n, rho): e = rng.normal(size=n); s = np.empty(n); s[0] = e[0]; [s.__setitem__(t, rho * s[t - 1] + math.sqrt(1 - rho ** 2) * e[t]) for t in range(1, n)]; return s
series = ar1(500, 0.8); iid_se = bootstrap_stats(series, np.mean, B=2000).std(ddof=1)
L = 25; nb = len(series) // L; starts = rng.integers(0, len(series) - L + 1, size=(2000, nb))
blk_means = np.array([np.concatenate([series[s:s + L] for s in row]).mean() for row in starts]); true_se_ar = np.std([ar1(500, 0.8).mean() for _ in range(2000)], ddof=1)
print(f"AR(1) ρ=0.8: true SE {true_se_ar:.4f}   iid bootstrap {iid_se:.4f}   block bootstrap {blk_means.std(ddof=1):.4f}")
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Resampling rows when the data are clustered | Intervals far too narrow | Cluster bootstrap |
| Breaking the pairing in a model comparison | Wider intervals, lost power (or wrong inference) | Resample items jointly; compute the difference per resample |
| Bootstrapping the max/min or other extremes | Intervals that can never contain the truth | Different methods (e.g., extreme-value theory); do not bootstrap extremes |
| Using the bootstrap with tiny `n` (≲ 15) and trusting the nominal level | Under-coverage | Measure coverage; use exact methods |
| Ignoring dependence in time series | SE too small | Block bootstrap |
| Too few resamples (`B = 100`) | Noisy interval end-points | `B ≥ 2,000` for intervals; check stability across seeds |
| Believing the bootstrap corrects bias | Interval centred on a biased estimate | Bias correction (BCa) or a better estimator |
| Heavy tails with infinite variance | Unstable, wide, irregular bootstrap distributions | Trimming/winsorizing with justification; robust statistics |
| Computing intervals on data used for model selection | Optimistic intervals | Held-out data (Stage 5A-07) |

### 3.6 ML link

- **Intervals for AUC, F1, calibration error, BLEU/ROUGE-style scores, medians, latency percentiles**: any statistic (Stage 5A-06, 5B-04).
- **Paired bootstrap** is the standard way to compare two models or prompts on the same test items (Project 1).
- **Cluster bootstrap** for evaluation sets with many rows per user/document/prompt (Stage 5A-07).
- **Bootstrap aggregating (bagging)** uses the same resampling idea for ensembles (Stage 5A-08).
- **Out-of-bag evaluation** exploits the items left out of each resample (Stage 5A-08).

### 3.7 Lab (90 min)

1. Implement `bootstrap_stats`, percentile, basic, and bootstrap-t intervals; apply to the mean, median, trimmed mean, correlation, and AUC (Module 06 Lesson 5) of synthetic data.
2. Coverage study (≥ 1,500 outer repetitions, `B = 400`): percentile bootstrap vs `t` interval for normal, exponential, and lognormal data at `n ∈ {10, 30, 100}`; report coverage with standard errors.
3. Paired vs unpaired bootstrap for two correlated classifiers; report the SE ratio as a function of the correlation between their errors.
4. Cluster-bootstrap experiment: vary the intra-cluster correlation and compare row vs cluster bootstrap SEs with the true SE and with `√deff` (Module 11).
5. Reproduce the max-statistic failure and the AR(1) block-bootstrap fix; choose the block length by a small sensitivity study.

### Check yourself (Unit 3)

1. Why do we resample *with replacement*?
2. What must you resample when comparing two models on the same test items?
3. Name a statistic for which the bootstrap is known to fail.

**Reference answers:** (1) To mimic drawing a fresh sample of the same size from the population (each draw independent); without replacement every resample would equal the original. (2) Items (rows), jointly for both models, then compute the difference per resample. (3) The sample maximum (or minimum) / other extreme-value statistics.

---

## Unit 4 — Hypothesis testing and p-values (`03-…md`)

### 4.1 Why ML needs this

"Is B better than A?" is a decision under uncertainty. A hypothesis test calibrates how surprising the observed difference would be if there were *no real difference*. Misused (peeking, many metrics, many segments, many prompts) it manufactures false discoveries; used well it keeps a team from shipping noise.

### 4.2 Intuition

Assume nothing is going on (the **null hypothesis**). Ask how often chance alone would produce a difference at least as large as the one you saw. If that is rare (below a pre-set threshold `α`), reject the null. The **p-value** is that probability. It is not the probability the null is true.

### 4.3 Mechanics

- **Setup:** null `H₀` (e.g., no difference), alternative `H₁` (two-sided: any difference; one-sided: a specified direction), a **test statistic** `T`, and a rejection rule.
- **p-value:** `P(T is at least as extreme as observed | H₀)`. Under a true null with a continuous statistic, **p-values are uniformly distributed on [0, 1]**.
- **Errors and levels:** Type I (false positive) rate `α`, Type II (false negative) rate `β`, **power** `= 1 − β = P(reject | H₁ true)` (Lesson 6).
- **What a p-value is not:** not `P(H₀ | data)`; not the probability the result is a fluke; not the size of the effect; not a measure of importance. A tiny p-value with a trivial effect is *statistically* but not *practically* significant; a large p-value is *absence of evidence*, not evidence of no effect (check power/interval).
- **Permutation test (exact logic, assumption-light):** under `H₀` the group labels are exchangeable; shuffle labels many times, recompute the statistic, and take the fraction of shuffles at least as extreme as observed (add 1 to numerator and denominator: `(1 + count)/(1 + B)`).
- **Multiple comparisons:** testing `m` hypotheses at level `α` gives about `mα` false positives under the null; the chance of at least one false positive (**FWER**) grows toward 1.
  - **Bonferroni:** reject if `p ≤ α/m` (controls FWER; conservative).
  - **Holm:** step-down version, uniformly more powerful than Bonferroni with the same FWER control.
  - **Benjamini–Hochberg (BH):** controls the **false discovery rate** (expected fraction of false rejections among rejections) under independence/positive dependence `[VERIFY]`: sort `p₍₁₎ ≤ … ≤ p₍ₘ₎`, reject all with `p₍ᵢ₎ ≤ iα/m` up to the largest such `i`.
- **Optional stopping ("peeking"):** repeatedly testing as data accumulate and stopping at the first `p < 0.05` inflates the Type I error far above `α` (the more looks, the worse); use a fixed sample size, or a sequential design with corrected boundaries `[VERIFY: group-sequential/alpha-spending outline]`.
- **Forking paths / p-hacking:** choosing metrics, segments, exclusions, or tests after seeing results invalidates the nominal `α`. **Pre-register** the primary metric, test, and stopping rule.
- **One- vs two-sided:** choose before seeing the data; a one-sided test halves the p-value only if the direction was fixed in advance.
- **Statistical vs practical significance:** always report the effect size and interval (Lesson 2) alongside the p-value; decide with a pre-specified **minimal effect that matters**.
- **Statement caution:** the American Statistical Association's guidance on p-values stresses these points `[VERIFY: citation/wording]`.

**Worked example:** two prompts, mean scores `3.41` vs `3.55` on 50 items each with SD `0.8`: the difference `0.14` has SE `0.16`, `z = 0.88`, two-sided `p ≈ 0.38`: not significant; with SE `0.16` the interval `0.14 ± 0.31` is wide, so the data are *inconclusive* rather than showing "no difference".

### 4.4 Code

```python
import math
import numpy as np
from inferkit import two_sided_p_from_z, norm_ppf
rng = np.random.default_rng(0)

# --- p-values are uniform under a true null
reps, n = 20_000, 30
a, b = rng.normal(size=(reps, n)), rng.normal(size=(reps, n))
z = (b.mean(1) - a.mean(1)) / np.sqrt(a.var(1, ddof=1) / n + b.var(1, ddof=1) / n)
p = np.array([two_sided_p_from_z(v) for v in z]); print("fraction of p-values below 0.05 / 0.20 / 0.50 under H0:", (p < 0.05).mean(), (p < 0.2).mean(), (p < 0.5).mean(), "(≈ 0.05, 0.2, 0.5)")
print("decile counts:", np.histogram(p, bins=10, range=(0, 1))[0])

# --- permutation test for a difference in means
def perm_test(x, y, B=20_000, rng=rng):
    pooled = np.r_[x, y]; n1 = len(x); obs = abs(x.mean() - y.mean()); cnt = 0
    for _ in range(B):
        perm = rng.permutation(pooled); cnt += abs(perm[:n1].mean() - perm[n1:].mean()) >= obs
    return (1 + cnt) / (1 + B)
x, y = rng.normal(0, 1, 20), rng.normal(0.7, 1, 20)
se = math.sqrt(x.var(ddof=1) / 20 + y.var(ddof=1) / 20); print("permutation p:", perm_test(x, y), "  z-test p:", two_sided_p_from_z((y.mean() - x.mean()) / se))

# --- multiple testing: 100 hypotheses, 10 of them truly non-null (z ~ N(3, 1))
def adjust(pvals, alpha, method):
    m = len(pvals); order = np.argsort(pvals); sp = pvals[order]; rej = np.zeros(m, bool)
    if method == "none": rej = pvals <= alpha
    elif method == "bonferroni": rej = pvals <= alpha / m
    elif method == "holm":
        for i, pv in enumerate(sp):
            if pv <= alpha / (m - i): rej[order[i]] = True
            else: break
    elif method == "bh":
        ok = np.nonzero(sp <= (np.arange(1, m + 1) / m) * alpha)[0]
        if len(ok): rej[order[: ok.max() + 1]] = True
    return rej
m, k_true, alpha, R = 100, 10, 0.05, 3000; stats = {mth: [0, 0.0, 0.0] for mth in ("none", "bonferroni", "holm", "bh")}   # [any false rejection, FDP sum, power sum]
for _ in range(R):
    zs = rng.normal(size=m); zs[:k_true] += 3.0; pv = np.array([two_sided_p_from_z(v) for v in zs]); null = np.arange(m) >= k_true
    for mth in stats:
        rej = adjust(pv, alpha, mth); fd = (rej & null).sum(); stats[mth][0] += fd > 0; stats[mth][1] += fd / max(rej.sum(), 1); stats[mth][2] += (rej & ~null).sum() / k_true
for mth, (a_, f_, pw) in stats.items(): print(f"{mth:10s} P(any false rejection) {a_ / R:.3f}   mean FDP {f_ / R:.3f}   power {pw / R:.3f}")

# --- optional stopping: peek every 100 observations up to 1,000 under a TRUE null
reps = 20_000; x = rng.normal(size=(reps, 1000)); cs = np.cumsum(x, axis=1)
looks = np.arange(100, 1001, 100); zlook = cs[:, looks - 1] / np.sqrt(looks)
print("type I error with a single final look:", np.mean(np.abs(zlook[:, -1]) > 1.96), "  with 10 peeks (stop at first p<0.05):", np.mean(np.any(np.abs(zlook) > 1.96, axis=1)))

# --- statistical vs practical significance: a huge sample makes a trivial effect 'significant'
n = 2_000_000; d = 0.003; a_m, b_m = rng.normal(0, 1, n), rng.normal(d, 1, n); se = math.sqrt(2 / n); zz = (b_m.mean() - a_m.mean()) / se
print(f"effect {b_m.mean() - a_m.mean():+.4f} σ with n = {n}: z = {zz:.2f}, p = {two_sided_p_from_z(zz):.4f} (significant, but trivially small)")
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Reading `p` as `P(H₀ is true)` | Overconfident conclusions | State the correct definition; report an interval and effect size |
| Treating "not significant" as "no effect" | Missed improvements (low power) | Report the interval and power; equivalence margins (Lesson 6) |
| Testing many metrics/segments/variants without correction | Spurious "wins" (`mα` false positives) | Declare a primary metric; Holm/BH for families |
| Peeking and stopping at the first significant result | Type I error far above `α` | Fixed `n`, or a proper sequential design |
| Choosing the test or exclusions after seeing the data | Forking-paths inflation | Pre-register the analysis plan |
| One-sided test chosen after seeing the sign | Halved p-value is invalid | Decide direction in advance |
| Huge `n` and a trivial effect | "Significant" but irrelevant | Pre-specify the minimal effect that matters |
| Small `n`, large estimated effect, `p < 0.05` | Inflated effect (winner's curse, Lesson 6) | Power analysis; shrinkage; replication |
| Applying BH when tests are strongly negatively dependent | FDR not controlled | `[VERIFY]` conditions; use Benjamini–Yekutieli or Holm |
| Using the permutation test with non-exchangeable data (time order, clusters) | Invalid p-values | Permute within clusters/blocks |

### 4.6 ML link

- **Prompt/model comparisons on benchmark suites** test many tasks/metrics at once: a multiplicity problem (Project 1).
- **Leaderboard overfitting:** repeated looks at a test set are optional stopping; keep a final untouched holdout (Stage 5A-07).
- **A/B tests** need pre-registered metrics and stopping rules (Lesson 5, Project 3).
- **Feature-importance and ablation claims** across many features need FDR control (Stage 5B-07).

### 4.7 Lab (90 min)

1. Verify p-value uniformity under the null for three different tests; compute the Kolmogorov distance of the p-values from uniform.
2. Implement the permutation test and compare p-values with a z/t test across 200 simulated datasets (scatter and correlation).
3. Multiple-testing study: vary `m`, the number of true effects, and the effect size; tabulate FWER, FDR, and power for none/Bonferroni/Holm/BH.
4. Optional-stopping study: vary the number of looks (1, 2, 5, 10, 20) and plot the realized Type I error; implement a Pocock-style fixed critical value that restores `α` across 5 looks `[VERIFY: boundary value, about 2.41]` and measure it.
5. Write a one-page pre-registration template for an A/B test (primary metric, test, α, stopping rule, MDE, exclusions).

### Check yourself (Unit 4)

1. What is a p-value?
2. Why does peeking inflate the Type I error?
3. When would you prefer BH over Bonferroni?

**Reference answers:** (1) The probability, if the null hypothesis were true, of a test statistic at least as extreme as the one observed. (2) Each extra look gives another chance for chance fluctuations to cross the threshold, so the probability that *some* look crosses it exceeds `α`. (3) When you test many hypotheses and can tolerate a small fraction of false discoveries (FDR control) in exchange for more power, e.g., screening many features/metrics; Bonferroni is for strict family-wise control.

---

## Unit 5 — t-tests and paired tests for model comparison (`04-…md`)

### 5.1 Why ML needs this

Comparing two models or prompts almost always means comparing scores on the **same** test items, a *paired* design, and the paired structure is the main source of statistical power. For pass/fail outcomes the right paired test is **McNemar's**. Using an unpaired test on paired data wastes power; treating cross-validation folds as independent understates variance.

### 5.2 Intuition

Items differ in difficulty, and hard items hurt both models. Subtracting the two models' scores *item by item* removes that shared difficulty, leaving only the difference you care about. A paired test analyses those differences.

### 5.3 Mechanics

- **One-sample / paired t-test:** `t = d̄/(s_d/√n)` with `n − 1` degrees of freedom, where `d` are within-pair differences. Assumes the differences are roughly normal (CLT helps for larger `n`).
- **Two-sample (independent) tests:**
  - **Pooled-variance t-test** assumes equal variances; fails (wrong Type I error) when variances *and* group sizes differ.
  - **Welch's t-test** does not: `t = (x̄₁ − x̄₂)/√(s₁²/n₁ + s₂²/n₂)`, with Welch–Satterthwaite degrees of freedom `ν ≈ (a + b)²/(a²/(n₁−1) + b²/(n₂−1))`, `a = s₁²/n₁`, `b = s₂²/n₂`. **Default to Welch.**
- **Paired vs unpaired power:** the paired SE is `√((σ_a² + σ_b² − 2ρσ_aσ_b)/n)`; positive correlation `ρ` between the two models' scores makes it smaller than the unpaired SE.
- **Rank-based alternatives (outline):** the sign test and Wilcoxon signed-rank test for paired differences when normality is doubtful; Mann–Whitney for independent groups `[VERIFY: assumptions]`.
- **McNemar's test (paired binary outcomes):** let `b` = items A got right and B wrong, `c` = items B right and A wrong (the **discordant** pairs). Under `H₀` (equal accuracy) `b ~ Binomial(b + c, ½)`. Exact two-sided p-value `= min(1, 2·P(Bin(b+c, ½) ≤ min(b, c)))`; large-sample version `z = (b − c)/√(b + c)`. Items both models got right (or both wrong) carry no information about the difference.
- **Effect size for models:** the accuracy difference `(b − c)/n` with its interval; for scores, the mean difference and Cohen's `d_z = d̄/s_d` (paired).
- **Cross-validation caveats:** scores from different folds share training data, so they are positively correlated; the naive paired t-test across `k` folds understates the variance and inflates Type I error. The variance of the mean difference is about `(σ²/k)(1 + (k−1)ρ)`, so a corrected test uses `σ²(1/k + ρ/(1−ρ))`; the **Nadeau–Bengio corrected resampled t-test** uses `n_test/n_train` in place of `ρ/(1−ρ)` `[VERIFY: exact correction]`. Repeated random splits and different seeds are likewise *not* independent replicates of the data.
- **Seeds as repeated measures:** to compare training procedures, run ≥ 5–10 seeds each and report mean ± SE; pair runs by data split where possible.
- **LLM-as-judge evaluations:** judge noise adds measurement error that attenuates differences and inflates variance; calibrate the judge against human labels `[JUDGEMENT]` (Project 1).
- **Assumptions to check:** independence of items, pairing correctly defined, difference distribution not extremely heavy-tailed, no leakage between models' training data and the test set.

**Worked example (McNemar):** on 1,000 items, A and B disagree on 80: `b = 25` (A right only), `c = 55` (B right only): `z = (25 − 55)/√80 = −3.35`, `p ≈ 0.0008` (the exact binomial version gives `p ≈ 0.0011`); B's accuracy is `3.0` points higher. Nearly all information is in the 80 discordant items, not the 920 concordant ones.

### 5.4 Code

```python
import math
import numpy as np
from inferkit import t_cdf, two_sided_p_from_t, two_sided_p_from_z
rng = np.random.default_rng(0)

def welch(x, y):
    n1, n2 = len(x), len(y); a, b = x.var(ddof=1) / n1, y.var(ddof=1) / n2
    t = (x.mean() - y.mean()) / math.sqrt(a + b); df = (a + b) ** 2 / (a * a / (n1 - 1) + b * b / (n2 - 1)); return t, df, two_sided_p_from_t(t, df)
def pooled(x, y):
    n1, n2 = len(x), len(y); sp2 = ((n1 - 1) * x.var(ddof=1) + (n2 - 1) * y.var(ddof=1)) / (n1 + n2 - 2)
    t = (x.mean() - y.mean()) / math.sqrt(sp2 * (1 / n1 + 1 / n2)); return t, n1 + n2 - 2, two_sided_p_from_t(t, n1 + n2 - 2)
def paired(a, b): d = a - b; n = len(d); t = d.mean() / (d.std(ddof=1) / math.sqrt(n)); return t, n - 1, two_sided_p_from_t(t, n - 1)

# --- Type I error under H0 when variances AND group sizes differ: pooled breaks, Welch holds
reps = 6000; rej_p = rej_w = 0
for _ in range(reps):
    x, y = rng.normal(0, 4, 10), rng.normal(0, 1, 40)                      # same mean, small noisy group vs big quiet group
    rej_p += pooled(x, y)[2] < 0.05; rej_w += welch(x, y)[2] < 0.05
print(f"Type I error (α=0.05): pooled t {rej_p / reps:.3f}   Welch {rej_w / reps:.3f}")

# --- paired vs unpaired power on shared items (items differ in difficulty)
def power(delta, n, reps=4000, rho_share=0.8):
    pw_pair = pw_welch = 0
    for _ in range(reps):
        diff = rng.normal(size=n) * math.sqrt(rho_share)                        # shared item difficulty
        a = diff + rng.normal(size=n) * math.sqrt(1 - rho_share); b = diff + delta + rng.normal(size=n) * math.sqrt(1 - rho_share)
        pw_pair += paired(b, a)[2] < 0.05; pw_welch += welch(b, a)[2] < 0.05
    return pw_pair / reps, pw_welch / reps
print("power for δ=0.3, n=60 (paired, unpaired):", power(0.3, 60))

# --- McNemar: exact and z versions; Type I error under H0 with correlated errors
def binom_cdf_half(k, n): return sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
def mcnemar(a_correct, b_correct):
    b = int(np.sum(a_correct & ~b_correct)); c = int(np.sum(~a_correct & b_correct)); m = b + c
    if m == 0: return b, c, 1.0, 1.0
    p_exact = min(1.0, 2 * binom_cdf_half(min(b, c), m)); p_z = two_sided_p_from_z((b - c) / math.sqrt(m)); return b, c, p_exact, p_z
print("worked example (b=25, c=55):", mcnemar(np.r_[np.ones(25, bool), np.zeros(55, bool), np.ones(920, bool)], np.r_[np.zeros(25, bool), np.ones(55, bool), np.ones(920, bool)]))
reps, n_items = 6000, 500; rej_e = rej_z = 0
for _ in range(reps):
    difficulty = rng.normal(size=n_items); pr = 1 / (1 + np.exp(-(1.0 - difficulty)))                 # both models have the SAME accuracy profile
    A, B = rng.random(n_items) < pr, rng.random(n_items) < pr
    _, _, pe, pz = mcnemar(A, B); rej_e += pe < 0.05; rej_z += pz < 0.05
print(f"McNemar Type I error (α=0.05): exact {rej_e / reps:.3f}   z-version {rej_z / reps:.3f}")

# --- power of McNemar: model B has a shifted intercept in the same latent-difficulty model; report the REALIZED accuracy lift
def mcnemar_power(n_items, shift, reps=2000):
    hit = 0; lifts = []
    for _ in range(reps):
        difficulty = rng.normal(size=n_items); pa = 1 / (1 + np.exp(-(1.0 - difficulty))); pb = 1 / (1 + np.exp(-(1.0 + shift - difficulty)))
        A, B = rng.random(n_items) < pa, rng.random(n_items) < pb; hit += mcnemar(A, B)[2] < 0.05; lifts.append(np.mean(pb - pa))
    return hit / reps, float(np.mean(lifts))
for n_items in (500, 1000, 3000):
    pw, lift = mcnemar_power(n_items, shift=0.12); print(f"n={n_items:5d} items, realized true lift {lift:.4f}: McNemar power {pw:.3f}")

# --- naive paired t-test across k correlated CV folds inflates Type I error; the corrected variance restores it
def cv_type1(k, rho, corrected, reps=20_000):
    shared = rng.normal(size=(reps, 1)) * math.sqrt(rho); d = shared + rng.normal(size=(reps, k)) * math.sqrt(1 - rho)     # H0: mean difference 0
    m, s2 = d.mean(1), d.var(1, ddof=1); var_mean = s2 * ((1 / k + rho / (1 - rho)) if corrected else 1 / k)
    t = m / np.sqrt(var_mean); p = np.array([two_sided_p_from_t(v, k - 1) for v in t[:6000]]); return np.mean(p < 0.05)
for rho in (0.1, 0.3, 0.5): print(f"k=10 folds, fold-score correlation ρ={rho}: naive Type I {cv_type1(10, rho, False):.3f}   corrected (true ρ) {cv_type1(10, rho, True):.3f}")
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Unpaired test on paired data | Lost power; wide intervals | Paired t / McNemar / paired bootstrap |
| Pooled-variance t-test with unequal variances *and* sizes | Type I error far from `α` (demo above) | Welch by default |
| Pairing defined incorrectly (different items per model, shuffled order) | Meaningless differences | Join by item id; assert alignment |
| Ordinary t-test across CV folds | Inflated false positives | Corrected resampled t-test, repeated-CV with correction, or a held-out test set |
| Treating seeds/random splits as independent samples of the *data* | Understated uncertainty about generalization | Report seed variance separately from data variance |
| McNemar on unpaired or independent samples | Invalid | Two-proportion test for independent arms (Lesson 5) |
| McNemar with very few discordant pairs | Underpowered | Exact version; increase `n` |
| Using accuracy differences from different test sets | Not comparable | Same test set (or a pre-defined common benchmark) |
| Noisy LLM judge treated as ground truth | Attenuated, biased differences | Calibrate against humans; report judge agreement |
| Normality assumed for heavily skewed score differences at small `n` | Wrong p-values | Sign/Wilcoxon, bootstrap, transformations |

### 5.6 ML link

- **Model and prompt comparison on a shared test set:** McNemar for pass/fail, paired t or paired bootstrap for scores (Project 1).
- **Cross-validation comparisons** need the corrected test or a separate holdout (Stage 5A-07).
- **Seed studies** for training-procedure comparisons (Module 08 Project 2, Stage 5C-03).
- **Offline–online consistency checks** compare paired offline metrics with online A/B outcomes (Stage 5D-12).

### 5.7 Lab (90 min)

1. Implement `welch`, `pooled`, `paired`; validate p-values by Type I simulation for 5 scenarios (equal/unequal variances and sizes, skewed data).
2. Paired vs unpaired power as a function of the correlation between the two models' scores; plot power vs `ρ`.
3. Implement McNemar (exact and z) and verify the Type I error with correlated errors; compute power vs `n` for a 1-, 2-, and 3-point lift.
4. Reproduce the CV-fold inflation for `ρ ∈ {0.1, 0.3, 0.5}` and apply the corrected variance; estimate `ρ` from repeated CV on a synthetic learner `[JUDGEMENT]`.
5. Add the sign test and Wilcoxon signed-rank (via ranks, normal approximation) for a heavy-tailed difference distribution; compare power with the t-test.

### Check yourself (Unit 5)

1. Why is a paired design usually more powerful for comparing two models?
2. Which test do you use for two classifiers evaluated on the same items with pass/fail outcomes?
3. What goes wrong when a t-test is applied to `k` cross-validation fold scores?

**Reference answers:** (1) Item difficulty is shared by both models, so it cancels in the within-item difference, shrinking the variance of the quantity being tested. (2) McNemar's test (on the discordant pairs). (3) Fold scores are positively correlated through shared training data, so the naive variance is too small and the false-positive rate is inflated.

---

## Unit 6 — Tests for proportions and A/B testing (`05-…md`)

### 6.1 Why ML needs this

Conversion rates, click-through, pass rates, win rates, and rollout success are proportions compared between two **independent** arms: the standard A/B test. Doing it well means more than a z-test: checking the allocation, planning the sample size, avoiding peeking, correcting for multiple metrics, and reading the effect on a scale decision-makers understand.

### 6.2 Intuition

Split traffic randomly; compare the two arms' success rates; ask whether a gap this large could come from chance in the split alone.

### 6.3 Mechanics

- **Two-proportion z-test:** with `p̂₁ = x₁/n₁`, `p̂₂ = x₂/n₂`, pooled `p̂ = (x₁ + x₂)/(n₁ + n₂)`: `z = (p̂₂ − p̂₁)/√(p̂(1−p̂)(1/n₁ + 1/n₂))` (the pooled SE applies *under `H₀`*).
- **Confidence interval for the difference** uses the *unpooled* SE: `(p̂₂ − p̂₁) ± z√(p̂₁(1−p̂₁)/n₁ + p̂₂(1−p̂₂)/n₂)`.
- **Relative lift:** `p̂₂/p̂₁ − 1`; interval via the **delta method** on `log(p̂₂/p̂₁)`: `Var ≈ (1−p̂₁)/(n₁p̂₁) + (1−p̂₂)/(n₂p̂₂)` `[VERIFY]`, or the bootstrap. Report absolute *and* relative differences.
- **Chi-square test on the 2×2 table** is equivalent to the squared pooled z (`χ² = z²`).
- **Fisher's exact test** (small counts): condition on the margins; the cell count follows a hypergeometric distribution under `H₀`; two-sided p-value sums the probabilities of tables no more likely than the observed one.
- **Sample size per arm** to detect `p₁ → p₂` with level `α` (two-sided) and power `1 − β`: `n = (z_{α/2}√(2p̄q̄) + z_β√(p₁q₁ + p₂q₂))² / (p₂ − p₁)²` with `p̄ = (p₁ + p₂)/2`. Rule of thumb: the required `n` scales like `1/δ²`: halving the detectable lift quadruples the sample.
- **Sample ratio mismatch (SRM):** if the observed arm sizes deviate from the planned split (e.g., 50/50) more than chance allows (test `z = (n₁ − n/2)/√(n/4)`, with a strict threshold like `p < 0.001`), the assignment or logging is broken and **all results are suspect**. Always check SRM first.
- **Randomization unit and independence:** randomize by user (not by request) when users have several events; analyze at the same unit (cluster the SE otherwise).
- **Multiple metrics and variants:** designate one **primary metric**; treat others as secondary/guardrail; correct families with Holm/BH; with `k` variants compare against control with an adjusted level.
- **Sequential monitoring:** if you must look early, use a pre-specified sequential design (alpha spending, always-valid inference `[VERIFY]`) rather than repeated fixed-sample tests.
- **Variance reduction (outline):** using pre-experiment covariates (CUPED/regression adjustment) shrinks variance without bias `[VERIFY]`.
- **Common pitfalls:** novelty/primacy effects (effect drifts over time); interference/network effects (users affect each other); heterogeneous effects across segments (pre-specify a small number of segments); metric dilution (including users never exposed).
- **Bayesian A/B (outline):** with Beta priors the posteriors are `Beta(α + x, β + n − x)` (Module 10 Lesson 6); report `P(B > A)` and the expected loss, which answers "how likely is B better" directly but depends on the prior `[VERIFY]`.

**Worked example (sample size):** baseline conversion 10%, detect +1 point (to 11%) at `α = 0.05`, power 80%: `n ≈ (1.96·√(2·0.105·0.895) + 0.842·√(0.09 + 0.0979))² / 0.01² ≈ 14,750` users per arm.

### 6.4 Code

```python
import math
import numpy as np
from inferkit import norm_ppf, two_sided_p_from_z
rng = np.random.default_rng(0)

def two_prop_ztest(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2; pp = (x1 + x2) / (n1 + n2); se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se0; se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2); h = 1.96 * se
    return {"diff": p2 - p1, "z": z, "p": two_sided_p_from_z(z), "ci": (p2 - p1 - h, p2 - p1 + h)}

def sample_size_per_arm(p1, p2, alpha=0.05, power=0.8):
    za, zb = norm_ppf(1 - alpha / 2), norm_ppf(power); pbar = (p1 + p2) / 2
    return math.ceil((za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2)
n_plan = sample_size_per_arm(0.10, 0.11); print("planned n per arm:", n_plan)

# --- Type I error and power by simulation at the planned n
def simulate(p1, p2, n, reps=6000):
    x1, x2 = rng.binomial(n, p1, reps), rng.binomial(n, p2, reps); hit = 0
    for a, b in zip(x1, x2): hit += two_prop_ztest(int(a), n, int(b), n)["p"] < 0.05
    return hit / reps
print("Type I error at planned n:", simulate(0.10, 0.10, n_plan), "  power for +1 point:", simulate(0.10, 0.11, n_plan), "(target 0.80)")
print("halving the detectable lift (+0.5 point) needs n =", sample_size_per_arm(0.10, 0.105), "(≈ 4×)")

# --- chi-square on 2×2 equals the squared pooled z
x1, n1, x2, n2 = 120, 1000, 150, 1000; table = np.array([[x1, n1 - x1], [x2, n2 - x2]], float); E = table.sum(1, keepdims=True) * table.sum(0, keepdims=True) / table.sum()
chi2 = float(((table - E) ** 2 / E).sum()); print("chi² =", chi2, "  z² =", two_prop_ztest(x1, n1, x2, n2)["z"] ** 2)

# --- Fisher's exact test via the hypergeometric distribution
def fisher_exact(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c; N = n1 + n2
    def pm(x): return math.exp(math.lgamma(n1 + 1) - math.lgamma(x + 1) - math.lgamma(n1 - x + 1) + math.lgamma(n2 + 1) - math.lgamma(k - x + 1) - math.lgamma(n2 - k + x + 1)
                               - (math.lgamma(N + 1) - math.lgamma(k + 1) - math.lgamma(N - k + 1)))
    lo, hi = max(0, k - n2), min(k, n1); p_obs = pm(a); return sum(pm(x) for x in range(lo, hi + 1) if pm(x) <= p_obs * (1 + 1e-9))
print("Fisher exact for [[3, 17], [11, 9]]:", fisher_exact(3, 17, 11, 9), "  z-test p (unreliable at these counts):", two_prop_ztest(3, 20, 11, 20)["p"])

# --- sample ratio mismatch (SRM)
def srm_p(n1, n2): return two_sided_p_from_z((n1 - (n1 + n2) / 2) / math.sqrt((n1 + n2) / 4))
print("SRM p-values: 5,000/5,000 →", srm_p(5000, 5000), "  10,200/9,800 (2% imbalance, n=20,000) →", srm_p(10200, 9800), "  5,050/4,950 →", srm_p(5050, 4950))
print("5,200/4,800 (n=10,000, 4% imbalance) →", srm_p(5200, 4800), "  (the 2% case is NOT below the strict 0.001 threshold: small imbalances need large n to be flagged)")

# --- relative lift interval by the delta method vs the bootstrap
x1, n1, x2, n2 = 500, 5000, 560, 5000; p1, p2 = x1 / n1, x2 / n2; lift = p2 / p1 - 1
se_log = math.sqrt((1 - p1) / (n1 * p1) + (1 - p2) / (n2 * p2)); ci_delta = (math.exp(math.log(p2 / p1) - 1.96 * se_log) - 1, math.exp(math.log(p2 / p1) + 1.96 * se_log) - 1)
bs = (rng.binomial(n2, p2, 20_000) / n2) / (rng.binomial(n1, p1, 20_000) / n1) - 1
print(f"relative lift {lift:+.3f}: delta-method CI {np.round(ci_delta, 3)}   parametric-bootstrap CI {np.round(np.quantile(bs, [0.025, 0.975]), 3)}")

# --- Bayesian A/B with Beta(1,1) priors: P(B > A) and the expected loss from choosing B
a = rng.beta(1 + x1, 1 + n1 - x1, 400_000); b = rng.beta(1 + x2, 1 + n2 - x2, 400_000)
print("P(B>A) =", (b > a).mean(), "  expected loss if we ship B:", np.mean(np.maximum(a - b, 0)), "  two-sided z-test p:", two_prop_ztest(x1, n1, x2, n2)["p"])

# --- A/A tests: with a correct pipeline ~5% 'wins' by chance; with 10 peeks it is far higher
def aa_false_positive(peeks, n_total=10_000, reps=2000):
    hit = 0
    for _ in range(reps):
        x = rng.random((2, n_total)) < 0.1; ok = False
        for m in np.linspace(n_total // peeks, n_total, peeks).astype(int):
            if two_prop_ztest(int(x[0, :m].sum()), m, int(x[1, :m].sum()), m)["p"] < 0.05: ok = True; break
        hit += ok
    return hit / reps
print("A/A false-positive rate: 1 look", aa_false_positive(1), "  10 peeks", aa_false_positive(10))
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Skipping the SRM check | Confidently analysing a broken experiment | Test the allocation first; stop on a strict SRM failure |
| Peeking and stopping on the first `p < 0.05` | Type I error multiplied (A/A demo) | Fixed `n` or a sequential design |
| Underpowered test, "no significant difference" declared a tie | Missed real effects | Plan `n` from the MDE (Lesson 6); report the interval |
| Using the z-test with tiny counts | Invalid p-values | Fisher exact |
| Randomizing by request but analysing by user (or vice versa) | Wrong SE; interference | Align the randomization and analysis unit; cluster SEs |
| Many metrics, one hit | False win | Primary metric; Holm/BH for the family |
| Reporting only relative lift | Hides tiny absolute effects | Report both |
| Segment fishing after a null result | Spurious subgroup effects | Pre-specify a few segments; correct for multiplicity |
| Novelty effect or short duration | Effect that vanishes after launch | Run through full cycles; check time trends |
| Treating `P(B>A)` from a Bayesian analysis as prior-free | Overconfidence in a prior choice | Report the prior; sensitivity analysis |
| Ignoring interference (network effects, shared resources) | Biased lift | Cluster/geo randomization `[VERIFY]` |

### 6.6 ML link

- **Online evaluation of models, prompts, rankers, and recommenders** is A/B testing (Stage 5B-09/10, 5D-12).
- **Canary/shadow rollouts** use the same machinery for guardrail metrics (Stage 5D-08/12).
- **Win-rate evaluations** of LLMs (pairwise preference) are proportion tests with ties and judge noise (Project 1).
- **Experiment platforms** automate SRM, sequential tests, and variance reduction (Stage 5D-12 `[JUDGEMENT]`).

### 6.7 Lab (90 min)

1. Implement the z-test, the chi-square equivalence, Fisher's exact test, and the SRM check; verify Type I error and power by simulation.
2. Sample-size lab: tabulate `n` per arm for baselines `{1%, 5%, 20%, 50%}` and absolute lifts `{0.25, 0.5, 1, 2}` points; verify two cells by simulating power.
3. Peeking lab: A/A tests with 1, 2, 5, 10, 20 looks; plot the realized false-positive rate; apply a Bonferroni-split `α` over looks and measure its (conservative) effect.
4. Relative-lift interval lab: delta method vs bootstrap vs the unpooled-difference interval; check coverage by simulation.
5. Write the analysis-plan template (unit of randomization, primary and guardrail metrics, SRM rule, stopping rule, MDE, segments) and apply it to a simulated experiment.

### Check yourself (Unit 6)

1. Which standard error does the two-proportion z-test use, and which does the confidence interval use?
2. What is an SRM and what do you do if you see one?
3. Roughly how does the required sample size change if you want to detect half the effect?

**Reference answers:** (1) The test uses the pooled SE (valid under `H₀`); the interval uses the unpooled SE. (2) A sample-ratio mismatch: the observed arm sizes differ from the planned allocation beyond chance; stop and debug assignment/logging before interpreting any result. (3) It roughly quadruples (`n ∝ 1/δ²`).

---

## Unit 7 — Effect size, sample size, and statistical power (`06-…md`)

### 7.1 Why ML needs this

Before collecting an eval set or launching an experiment you must decide how much data is enough, which means deciding the smallest improvement worth detecting. Underpowered studies waste effort *and* mislead: the few that reach significance overstate the effect.

### 7.2 Intuition

**Power** is the chance a real effect of a given size will be detected. It rises with sample size, effect size, and the significance level, and falls with noise. The **minimal detectable effect (MDE)** is the smallest effect you have decent power to detect at a given `n`.

### 7.3 Mechanics

- **Effect-size measures:** raw difference (accuracy points, seconds, dollars: the one decision-makers use), **standardized** difference `d = (μ₂ − μ₁)/σ` (Cohen's `d`; paired version `d_z = d̄/s_d`), relative lift, odds ratio. Conventional "small/medium/large" labels (`0.2/0.5/0.8`) are rough conventions, not substitutes for domain thresholds `[JUDGEMENT]`.
- **Power for a two-sample mean comparison** (equal groups, known `σ`, two-sided `α`): `power ≈ Φ(δ/(σ√(2/n)) − z_{α/2})`. **Required `n` per group:** `n = 2σ²(z_{α/2} + z_β)²/δ²`. Conventional targets: `α = 0.05`, power `0.8` (or `0.9`) `[JUDGEMENT]`.
- **MDE** at fixed `n`: `δ_min = (z_{α/2} + z_β) σ √(2/n)`.
- **Dependence on design:** paired designs, covariate adjustment, and a lower-variance metric reduce `σ` (or its effective value) and raise power; clustering raises it (design effect, Module 11).
- **Underpowered studies and the winner's curse (type M error):** when power is low, the estimates that happen to cross the significance threshold are *exaggerated*; the average significant effect overstates the truth, and the sign can even be wrong (type S error). Replication and shrinkage are the remedies.
- **Post-hoc ("observed") power is uninformative:** it is a function of the p-value; plan power *before* the study from a meaningful effect, not from the observed one.
- **Planning workflow:** (1) pick the primary metric; (2) get `σ` (or `p`) from a pilot or history; (3) set the MDE from a decision threshold; (4) compute `n`; (5) check by simulation; (6) pre-register; (7) after the study, report the interval, not "significant/not".
- **Equivalence and non-inferiority (outline):** to *demonstrate* two models are practically the same (or that a cheaper model is not worse by more than `Δ`), test whether the interval lies within `±Δ` (two one-sided tests, **TOST**); "failing to reject a difference" does not show equivalence `[VERIFY]`.
- **Budgeting trade-off:** since `n ∝ 1/δ²`, detecting a 0.5-point gain takes 4× the data of a 1-point gain; tell stakeholders what resolution the planned eval can offer.
- **Precision-based planning:** alternatively choose `n` so that the interval half-width is below a target (`n ≈ (1.96σ/E)²`, Module 11).

**Worked example:** to detect a difference of `0.2σ` with 80% power at `α = 0.05` you need `n = 2(1.96 + 0.842)²/0.2² ≈ 393` per group. With only 40 per group the power is about `0.14`, and the rare significant results overstate the effect about 2.7-fold in simulation (Section 7.4).

### 7.4 Code

```python
import math
import numpy as np
from inferkit import norm_cdf, norm_ppf, two_sided_p_from_z
rng = np.random.default_rng(0)

def power_two_sample(delta_over_sigma, n, alpha=0.05):
    za = norm_ppf(1 - alpha / 2); s = delta_over_sigma / math.sqrt(2 / n); return (1 - norm_cdf(za - s)) + norm_cdf(-za - s)
def n_per_group(delta_over_sigma, alpha=0.05, power=0.8):
    return math.ceil(2 * (norm_ppf(1 - alpha / 2) + norm_ppf(power)) ** 2 / delta_over_sigma ** 2)
def mde(n, alpha=0.05, power=0.8): return (norm_ppf(1 - alpha / 2) + norm_ppf(power)) * math.sqrt(2 / n)

print("n per group for d=0.2 / 0.5 / 0.8:", n_per_group(0.2), n_per_group(0.5), n_per_group(0.8))
print("power at d=0.2 with n=40:", power_two_sample(0.2, 40), " MDE at n=40:", mde(40), " MDE at n=1000:", mde(1000))

# --- verify the analytic power and the planned n by simulation (z-test with known σ = 1)
def sim_power(d, n, reps=40_000):
    a, b = rng.normal(0, 1, (reps, n)), rng.normal(d, 1, (reps, n)); z = (b.mean(1) - a.mean(1)) / math.sqrt(2 / n)
    return np.mean(np.abs(z) > 1.96), z
for d, n in ((0.2, 40), (0.2, 393), (0.5, 64)): print(f"d={d}, n={n}: analytic power {power_two_sample(d, n):.3f}   simulated {sim_power(d, n)[0]:.3f}")

# --- the winner's curse: with low power, significant results overstate the effect
d, n = 0.2, 40; reps = 200_000
a, b = rng.normal(0, 1, (reps, n)), rng.normal(d, 1, (reps, n)); est = b.mean(1) - a.mean(1); z = est / math.sqrt(2 / n); sig = np.abs(z) > 1.96
print(f"true effect {d}; power {sig.mean():.3f}; mean estimate among SIGNIFICANT results: {est[sig].mean():.3f} (exaggeration ×{est[sig].mean() / d:.1f}); wrong-sign share among significant: {np.mean(est[sig] < 0):.4f}")
for n_ in (40, 100, 393, 1000):
    a, b = rng.normal(0, 1, (60_000, n_)), rng.normal(d, 1, (60_000, n_)); est = b.mean(1) - a.mean(1); sg = np.abs(est / math.sqrt(2 / n_)) > 1.96
    print(f"  n={n_:4d}: power {sg.mean():.3f}   exaggeration of significant estimates ×{est[sg].mean() / d:.2f}")

# --- post-hoc power is a function of the p-value
for p in (0.5, 0.1, 0.05, 0.01):
    z_obs = norm_ppf(1 - p / 2); print(f"observed p = {p:5.2f} → 'post-hoc power' {(1 - norm_cdf(1.96 - z_obs)) + norm_cdf(-1.96 - z_obs):.3f}  (uninformative)")

# --- paired designs and variance reduction raise power
n = 60; delta = 0.3
for rho in (0.0, 0.5, 0.8):
    sd_diff = math.sqrt(2 * (1 - rho)); se = sd_diff / math.sqrt(n); print(f"score correlation ρ={rho}: paired power for δ={delta}, n={n}: {(1 - norm_cdf(1.96 - delta / se)):.3f}")

# --- equivalence (TOST): is the cheaper model within ±1 point of accuracy?
def tost(diff, se, margin, alpha=0.05):
    z = norm_ppf(1 - alpha); return (diff - margin) / se < -z and (diff + margin) / se > z       # both one-sided tests reject
p_a, p_b = 0.800, 0.795
for n in (8000, 40_000):
    se = math.sqrt(2 * 0.8 * 0.2 / n)
    print(f"n={n:6d} per model: difference {p_b - p_a:+.3f}, SE {se:.4f}; equivalent within ±1 point: {tost(p_b - p_a, se, 0.01)}; within ±0.5 point: {tost(p_b - p_a, se, 0.005)}")
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Choosing `n` by convention or habit | Under- or over-powered tests | Power analysis from a stated MDE |
| Using the *observed* effect to compute power | Circular and uninformative | Plan from the smallest effect that matters |
| Treating a "significant" result from a small study as the true size | Inflated effect (winner's curse) | Report intervals; replicate; shrink |
| Declaring "no difference" from a non-significant, underpowered test | Missed effects | Equivalence testing with a margin; interval reporting |
| Computing `n` for the wrong variance (using the unpaired `σ` for a paired design, or the wrong baseline `p`) | Wrong sample size | Estimate the variance of the *actual* test statistic |
| Ignoring clustering/dependence in planning | Under-powered in practice | Inflate `n` by the design effect |
| Chasing tiny MDEs without cost awareness | Huge, expensive tests | Decide the smallest *valuable* effect first |
| Power computed with a normal approximation for small counts | Misleading | Simulate |
| Multiple primary metrics without adjusting `α` | Power/size mismatch | One primary metric or a corrected `α` |

### 7.6 ML link

- **Eval-set sizing:** how many prompts/items are needed to detect a 1-point improvement (Project 1; Stage 5A-06/07).
- **Seed counts:** how many training runs are needed to compare two training procedures (Module 08 Project 2).
- **Experiment duration and traffic allocation** from the MDE (Project 3; Stage 5D-12).
- **Replication and negative-result reporting** culture in ML research (Stage 5C-15) `[JUDGEMENT]`.

### 7.7 Lab (75 min)

1. Implement `power_two_sample`, `n_per_group`, and `mde`; verify by simulation on a grid of `(d, n)`; tabulate the MDE vs `n` for `σ = 1`.
2. Winner's-curse study: for `d ∈ {0.1, 0.2, 0.5}` and `n ∈ {20, 50, 200, 1000}`, tabulate power, exaggeration factor, and wrong-sign rate.
3. Paired vs unpaired planning: compute `n` for a model comparison with item-score correlation `ρ ∈ {0, 0.5, 0.8}`; verify by simulation.
4. Equivalence: implement TOST for accuracy and apply it to the "cheaper model" example with several margins and sample sizes.
5. Write a one-page "evaluation budget" memo: given a target resolution (e.g., 1 point of accuracy) and a baseline, state the number of eval items required, with the assumptions.

### Check yourself (Unit 7)

1. What determines statistical power?
2. Why are significant results from underpowered studies unreliable estimates of the effect?
3. How does halving the minimal detectable effect change the needed sample size?

**Reference answers:** (1) The true effect size, the noise (variance), the sample size, and the significance level (plus design: pairing, clustering). (2) Only estimates that happen to be large cross the threshold, so the significant ones are biased upward (winner's curse) and sometimes have the wrong sign. (3) It quadruples (`n ∝ 1/δ²`).

---

## Unit 8 — Correlation vs causation, confounding, and sampling bias (`07-…md`)

### 8.1 Why ML needs this

A statistically significant, well-measured association can still be the wrong basis for a decision. Observational data (logs, historical records, user behaviour) are full of confounders, selection effects, and leakage, and ML systems are routinely trained and evaluated on exactly such data. Randomized experiments are the primary defence; where you cannot randomize, you need to understand what can go wrong.

### 8.2 Intuition

`X` and `Y` can move together because `X` causes `Y`, `Y` causes `X`, a third factor drives both (**confounding**), or because of how the data were **selected**. Statistics can describe the association; only design (randomization) or assumptions about the causal structure license a causal claim.

### 8.3 Mechanics

- **Confounding:** `Z` affects both `X` and `Y`. The naive association of `X` with `Y` mixes the causal effect with `Z`'s influence. **Adjustment** (stratifying on `Z`, regression on `Z`) removes it *only if all confounders are measured and correctly modelled*.
- **Randomization** breaks the link between `Z` and treatment assignment in expectation, so the naive difference estimates the causal effect: the reason A/B tests work (Lesson 5).
- **Collider bias / selection bias:** conditioning (or selecting) on a common effect of two independent causes induces a dependence between them (Module 09 Lesson 4). Examples: analysing only admitted students, only users who clicked, only deployed models.
- **Simpson's paradox:** a trend in subgroups reverses on aggregation when the group sizes are unbalanced (Module 09 Lesson 2).
- **Survivorship and selection:** analysing only the surviving/observed units (successful startups, retained users, labelled examples) biases estimates.
- **Sampling bias and non-response:** the sample differs from the population of interest (volunteer users, logged-in users only); estimates do not generalize. **Label/measurement bias:** labels reflect annotator or process quirks.
- **Spurious correlation:** with trending or autocorrelated series, independent random walks routinely show large correlations; many candidate features and few samples also produce impressive but false correlations (multiplicity, Lesson 3).
- **Reverse causality and feedback loops:** a model's outputs change future data (recommenders, fraud filters): correlations learned from logged data may not hold under the new policy.
- **Data leakage:** features that encode the label or the future (target leakage), or train/test contamination, inflate offline metrics and fail in production. Check each feature: *would it be available at prediction time?*
- **Interference:** if units affect each other (social networks, marketplaces), a unit-level randomized comparison is biased `[VERIFY]`.
- **Experiments vs observational comparisons:** offline metrics on logged data estimate performance on the *logging policy's* distribution; policy changes need online tests or counterfactual methods (importance weighting, 4C-04, Stage 5B-10) `[VERIFY]`.
- **What ML's predictive success does and doesn't show:** a feature's predictive importance is not a causal effect; interventions on it may do nothing (feature attribution, Stage 5B-07).
- **Practical checklist:** (1) How was the unit assigned or selected? (2) Could a third factor drive both? (3) Could conditioning on an outcome-related variable create a collider? (4) Is the sample representative of where the result will be used? (5) Does any feature leak the label or the future? (6) Can we randomize?

**Worked example:** hospital logs show patients who receive an expensive treatment have *worse* outcomes. Sicker patients are more likely to be treated (severity confounds treatment and outcome), so the naive comparison blames the treatment for the patients' severity; stratifying by severity (or randomizing) corrects the sign.

### 8.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

# --- confounding: severity Z raises both the chance of treatment and the risk of a bad outcome; the true treatment effect is −0.5
n = 100_000; Z = rng.normal(size=n)
T = (rng.random(n) < 1 / (1 + np.exp(-2 * Z))).astype(float)                           # sicker patients are treated more
Y = 1.0 * Z - 0.5 * T + rng.normal(size=n)                                               # outcome: bad = higher
naive = Y[T == 1].mean() - Y[T == 0].mean()
X = np.c_[np.ones(n), T, Z]; beta = np.linalg.lstsq(X, Y, rcond=None)[0]                  # adjust for the confounder
Tr = (rng.random(n) < 0.5).astype(float); Yr = 1.0 * Z - 0.5 * Tr + rng.normal(size=n); randomized = Yr[Tr == 1].mean() - Yr[Tr == 0].mean()
print(f"true effect −0.50 | naive observational {naive:+.2f} | adjusted for Z {beta[1]:+.2f} | randomized {randomized:+.2f}")

# --- stratification also corrects the sign without a regression model, but coarse bins leave residual confounding (more bins or a regression get closer)
bins = np.quantile(Z, np.linspace(0, 1, 11)); strata = np.clip(np.digitize(Z, bins[1:-1]), 0, 9)
eff = [Y[(strata == s) & (T == 1)].mean() - Y[(strata == s) & (T == 0)].mean() for s in range(10)]
print("stratified (10 severity bins) effect:", np.mean(eff))

# --- unmeasured confounder: adjustment on a noisy proxy only partly helps
Zproxy = Z + rng.normal(scale=1.5, size=n); beta_p = np.linalg.lstsq(np.c_[np.ones(n), T, Zproxy], Y, rcond=None)[0]
print("adjusted for a noisy proxy of Z:", beta_p[1], "(still biased)")

# --- selection / collider bias: talent and looks are independent, but conditioning on being hired creates a negative correlation
talent, looks = rng.normal(size=n), rng.normal(size=n); hired = (talent + looks) > 1.5
print("corr(talent, looks) overall:", np.corrcoef(talent, looks)[0, 1], "  among the hired:", np.corrcoef(talent[hired], looks[hired])[0, 1])

# --- spurious correlation between independent random walks
def walk_corr(n_steps=250): a, b = np.cumsum(rng.normal(size=n_steps)), np.cumsum(rng.normal(size=n_steps)); return np.corrcoef(a, b)[0, 1]
r = np.array([walk_corr() for _ in range(5000)]); print("independent random walks: fraction with |r| > 0.5:", np.mean(np.abs(r) > 0.5), "  vs independent noise series:", np.mean([abs(np.corrcoef(rng.normal(size=250), rng.normal(size=250))[0, 1]) > 0.5 for _ in range(5000)]))

# --- many candidate features, few samples: the best of many noise features looks predictive
n_s, m = 40, 500; y = rng.normal(size=n_s); F = rng.normal(size=(n_s, m)); rs = np.array([np.corrcoef(F[:, j], y)[0, 1] for j in range(m)])
print("best |r| among 500 pure-noise features with n=40:", np.abs(rs).max(), "  a single pre-specified feature would exceed 0.31 only about 5% of the time")

# --- target leakage: a feature computed AFTER the outcome inflates offline accuracy
n_l = 20_000; true_signal = rng.normal(size=n_l); label = (true_signal + rng.normal(size=n_l) > 0).astype(float)
leak = label + 0.3 * rng.normal(size=n_l)                                                 # e.g., 'refund issued' recorded after the fraud label
def acc_with(feature):
    Xf = np.c_[np.ones(n_l), feature]; w = np.linalg.lstsq(Xf, label, rcond=None)[0]; return np.mean((Xf @ w > 0.5) == (label == 1))
print(f"accuracy using the legitimate signal: {acc_with(true_signal):.3f}   with the leaky feature: {acc_with(leak):.3f}")

# --- survivorship: average of surviving units overstates the typical outcome
growth = rng.normal(0.0, 1.0, size=100_000); survived = growth > -0.5
print("mean growth of all units:", growth.mean(), "  of survivors only:", growth[survived].mean())
```

### 8.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Reading a regression coefficient as a causal effect | Wrong sign or size (confounding demo) | Randomize, or state the causal assumptions and sensitivity |
| Adjusting for a *collider* or a post-treatment variable | Introduces bias | Draw the causal graph; adjust only for pre-treatment confounders |
| Assuming adjustment fixes *unmeasured* confounders | Residual bias | Sensitivity analysis; instruments/experiments |
| Analysing a selected subset (hired, clicked, retained) | Spurious associations | Model the selection; collect unselected data |
| Correlating trending series | Impressive spurious `r` | Detrend/difference; test on held-out periods |
| Screening hundreds of features and reporting the best | Selection of noise | Pre-specify; multiplicity correction; out-of-sample validation |
| Label or feature leakage | Offline gains that vanish online | Time-aware splits; audit features for availability at prediction time |
| Generalizing from a non-representative sample | Failure in the target population | Reweighting; stratified sampling; sampling-bias checks |
| Unit-level randomization with interference | Biased lift | Cluster/geo randomization `[VERIFY]` |
| Evaluating a new policy on logs from an old one | Optimistic or biased estimates | Online A/B or counterfactual evaluation |
| Interpreting predictive feature importance as causal | Futile interventions | Causal methods/experiments (Stage 5B-10) |

### 8.6 ML link

- **Offline vs online metric gaps** often trace to confounding, selection, or leakage (Stage 5D-12).
- **Train/test leakage and time-based splits** (Stage 5A-07).
- **Causal inference and experimentation** (Stage 5B-10) build on this lesson.
- **Fairness and data-collection bias:** sampling and label bias propagate into models (Stage 5C-15 `[JUDGEMENT]`; trustworthy ML).
- **Feedback loops in recommenders and ranking** (Stage 5B-09).
- **Interpretability caveats:** importance ≠ causation (Stage 5B-07).

### 8.7 Lab (75 min)

1. Reproduce the confounding demo; vary the strength of the confounder and plot the bias of the naive, adjusted, and randomized estimates.
2. Demonstrate that adjusting for a collider *creates* bias: add a variable caused by both `T` and `Y` and show the effect estimate move.
3. Build a selection-bias example from your own domain (e.g., analysing only users who clicked); show the distorted association and what unselected data would show.
4. Leakage audit: for a synthetic tabular dataset with timestamps, identify which features leak and show the offline-vs-time-split gap.
5. Write the six-question causal checklist as a review template and apply it to two imagined ML findings.

### Check yourself (Unit 8)

1. Why does randomization justify a causal interpretation of an A/B difference?
2. What is collider bias?
3. Why is "this feature is highly predictive" not evidence that changing it will change the outcome?

**Reference answers:** (1) It makes treatment assignment independent of every other factor (measured or not), in expectation, so the only systematic difference between arms is the treatment. (2) Conditioning or selecting on a common effect of two causes creates a spurious dependence between them (e.g., among the hired, talent and looks become negatively correlated). (3) The predictor may be a proxy for a cause or a confounded correlate; intervening on it need not change the outcome.

---

## Unit 9 — Practice question bank (`practice-questions.md`)

### 9.1 Structure

About 60 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 15 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, "which test?", runnable code, and experiment-design judgement.

### 9.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 9.3 Seed items

**Q1 [L1] Interpretation.** What does a 95% confidence interval mean? → A procedure that contains the true parameter in 95% of repeated samples.
**Q2 [L1] p-value.** Define it. → Probability, under the null, of a statistic at least as extreme as observed.
**Q3 [L2] Interval.** `x̄ = 52`, `s = 10`, `n = 25`: 95% interval? → `52 ± 2.064·2 = [47.9, 56.1]` (`t₂₄ = 2.064`).
**Q4 [L2] Proportion test.** 120/1000 vs 150/1000: pooled `z`? → `p̂ = 0.135`, SE `= 0.01532`, `z = 1.96`, `p ≈ 0.05`.
**Q5 [L2] McNemar.** `b = 30`, `c = 50`. `z` and conclusion at 5%? → `z = −20/√80 = −2.24`, `p ≈ 0.025`: reject.
**Q6 [L2] Sample size.** Detect `0.5σ` with 80% power, `α = 0.05`: `n` per group? → `2(2.802)²/0.25 ≈ 63`.
**Q7 [L2] Multiplicity.** 20 independent null tests at `α = 0.05`: `P(at least one false positive)`? → `1 − 0.95²⁰ ≈ 0.64`.
**Q8 [L2] Holm vs Bonferroni.** p-values `0.001, 0.012, 0.03, 0.2` (`m = 4`, `α = 0.05`). Rejections? → Bonferroni (`0.0125`): first two; Holm: `0.001 ≤ 0.0125`, `0.012 ≤ 0.0167`, `0.03 > 0.025` → first two.
**Q9 [L2] Bootstrap.** How many distinct rows appear in a bootstrap resample of size `n` (large `n`)? → About `63.2%`.
**Q10 [L3] Debug.** An A/B test is stopped the first time `p < 0.05`, checked daily for 30 days; the reported "5%" false-positive rate is wrong. → Optional stopping: many looks inflate Type I error (often well above 20%); use a fixed-horizon or sequential design.
**Q11 [L3] Debug.** The 95% intervals for models A and B overlap, so the team concludes "no difference". → Overlap does not imply a non-significant difference; test the paired difference.
**Q12 [L3] Debug.** A pooled-variance t-test gives `p = 0.03` for groups with `n = 10, σ = 4` vs `n = 40, σ = 1`. → The equal-variance assumption fails with unequal sizes: use Welch; the pooled test's Type I error is inflated.
**Q13 [L3] Debug.** 10-fold CV: model A beats B in 9 of 10 folds, and a paired t-test over folds gives `p = 0.004`. → Fold scores are correlated; the naive test is anti-conservative; use the corrected test or a separate holdout.
**Q14 [L3] Analysis.** Treatment arm 5,200 users, control 4,800 in a planned 50/50 split. → SRM (`z = 4`, `p ≈ 6e-5`): assignment or logging is broken; do not analyse the metric.
**Q15 [L3] Analysis.** A small study finds a significant effect of 0.8σ, but earlier work suggests 0.2σ. → Underpowered study + winner's curse: significant estimates are inflated; replicate with adequate power.
**Q16 [L3] Analysis.** Users who rate more movies churn less, so the team proposes prompting for more ratings. → Confounding by engagement; test by randomization.
**Q17 [L4] Design.** Design the analysis plan for "is prompt B better than A" on 500 items. → Same items for both; paired design; primary metric fixed (pass rate), McNemar + paired-bootstrap interval for the difference; MDE and power stated; judge-noise check; multiple metrics handled by Holm; decision rule written before running.
**Q18 [L4] Design.** You test 12 metrics in an A/B test. → One primary metric (no correction), guardrails with a one-sided non-inferiority margin, secondary metrics with BH at 10%; state it before launch.
**Q19 [L4] Design.** Decide how many eval items you need to resolve a 1-point accuracy difference near 85%. → Use the paired variance of the difference (pilot the discordance rate `(b+c)/n`); `n ≈ (z_{α/2}+z_β)² (b+c)/n / δ²`; verify by simulation.
**Q20 [L4] Design.** A team wants to compare two training procedures. → ≥ 10 seeds each with paired data splits, report mean difference ± SE, a paired test or bootstrap over seeds, and an equivalence margin if the claim is "no worse".

### 9.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Confidence intervals | 2 | 3 | 2 | 0 |
| Bootstrap | 2 | 2 | 2 | 1 |
| Hypothesis tests, p-values, multiplicity | 3 | 3 | 3 | 1 |
| t-tests, paired tests, McNemar | 2 | 2 | 3 | 1 |
| Proportion tests, A/B testing | 2 | 3 | 3 | 2 |
| Effect size, power, sample size | 2 | 2 | 1 | 2 |
| Causation, confounding, bias | 2 | 0 | 1 | 1 |

### Check yourself (Unit 9)

1. Why does the seed set include an SRM item and an optional-stopping item?
2. Which items need runnable code?

**Reference answers:** (1) They are the two most common causes of invalid A/B conclusions in practice. (2) All L3 items and any whose answer depends on simulation or floating-point behaviour.

---

## Unit 10 — Project index (`Projects/README.md`)

### 10.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Is prompt B really better? | A complete, error-rate-validated paired comparison workflow for an LLM eval | 1–7 | 8–9 h |
| 2 | Bootstrap confidence-interval lab | Implementations and coverage audits of bootstrap interval methods; failure cases | 1–2, 6 | 8–9 h |
| 3 | A/B test analysis report | End-to-end experiment analysis (SRM, metrics, intervals, multiplicity, decision memo) validated on simulated experiments with known truth | 3–7 | 9–10 h |

Order: 2 → 1 → 3 (Project 1 uses Project 2's bootstrap; Project 3 reuses both). Outputs feed `mlmath/infer.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D11) and notebook `12_inference.ipynb`. The report templates are reused in Stage 5A-06 and 5D-12.

### 10.2 Data policy

**No downloads.** All data are simulated from known models so that the true effect, true accuracy, and true conversion rates are available for auditing every method. You may additionally apply the tools to any evaluation logs you already have locally; keep them out of the repository and tests `[VERIFY: licence/privacy]`.

### 10.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (tests/intervals match references; error rates verified by simulation) | 30 |
| Failure-mode handling (pairing, clustering, SRM, peeking, tiny counts, heavy tails) | 15 |
| Reproducibility (seeded, pinned, clean venv, no downloads, analysis plan fixed before running) | 15 |
| Explanation and statistical honesty (error rates with SEs; power stated; caveats; no overclaiming) | 15 |
| Code quality (types, validation, docstrings stating assumptions) | 15 |
| ML connection paragraph | 10 |

### 10.4 Standard layout

```
project/
├── README.md  requirements.txt  ANALYSIS_PLAN.md
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 10)

1. Why is an `ANALYSIS_PLAN.md` part of every project?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) Fixing the metric, test, `α`, stopping rule, and decision rule *before* looking at results is what keeps the reported error rates valid. (2) D11 (`mlmath/infer.py`).

---

## Unit 11 — Project: Is prompt B really better? (`Projects/01-…md`)

### 11.1 Brief

Build `promptab`: a complete evaluation workflow for comparing two prompts (or models) on the same set of items, with outcomes that are pass/fail and (optionally) ordinal rubric scores, including a noisy "LLM judge". Implement the analysis (McNemar, paired bootstrap, paired t on scores, effect size, power and sample size), fix a **decision rule in advance**, and then **evaluate the decision procedure itself by simulation**: its false-positive rate when the prompts are identical and its power for a stated true improvement.

**Industry framing:** "B looked better on 200 prompts" is the most common unverified claim in applied LLM work. The deliverable is the machinery, and the evidence, that a team could use to make a statement of the form *"B is better by `d` points (95% CI `lo` to `hi`); the decision procedure's measured false-ship rate is `x%`; at this sample size it ships a true 2-point gain `y%` of the time"*, with every number measured rather than assumed. (In this module's seeded runs the rule's false-ship rate was 1.7–4.0% and it shipped a true 2-point gain only 7%, 20%, and 57% of the time at 200, 1,000, and 3,000 items, so *most* real 2-point improvements go unconfirmed at those sizes.)

### 11.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Simulator | `simulate_eval(n_items, acc_a, acc_b, difficulty_sd, judge_error, seed)` producing **paired** pass/fail outcomes via a latent item-difficulty model, with a controllable true accuracy difference and an optional symmetric judge error rate (labels flipped with probability `e`) |
| R2 | Per-prompt intervals | Wilson interval for each prompt's accuracy |
| R3 | Paired tests | McNemar exact and z; paired t on 1–5 rubric scores (also a sign test); each with p-values computed from your own code (`inferkit`) |
| R4 | Paired bootstrap | Interval for the accuracy difference by resampling items jointly; compare with the unpaired bootstrap and with the McNemar-based interval |
| R5 | Effect size | Absolute accuracy difference, odds ratio of discordant pairs `b/c` with an interval, Cohen's `d_z` for scores |
| R6 | Power and sample size | Analytic and simulated power for McNemar as a function of `n`, true lift, and discordance rate; required `n` for a 1- and 2-point lift; MDE at the current `n` |
| R7 | Decision rule | `ANALYSIS_PLAN.md` defining: primary metric, test, `α`, the minimum improvement that matters `δ*`, and the rule (e.g., *ship B iff the 95% paired-bootstrap interval for the improvement lies entirely above 0 **and** the point estimate ≥ `δ*`*); implemented as a function returning `ship`, `keep A`, or `inconclusive` |
| R8 | Operating characteristics | Simulate ≥ 2,000 evaluations under `acc_a = acc_b` (false-positive rate of the decision rule), and under a true lift of 1 and 2 points (power/ship rate) for `n ∈ {200, 500, 1000, 3000}`; each rate with its binomial SE |
| R9 | Judge noise | Show how a judge with symmetric error `e ∈ {0, 0.05, 0.1, 0.2}` attenuates the observed difference (`(1 − 2e)×`) and affects power; show how a *biased* judge (favouring longer answers) creates a false win `[JUDGEMENT]` |
| R10 | Multiple metrics | Evaluate 5 metrics where B has no true effect: show the false-win rate without correction and with Holm/BH; define one primary metric in the plan |
| R11 | Peeking study | Evaluate the decision rule if the team checks after every 100 items and stops at the first significant result; report the inflated false-positive rate |
| R12 | Report | `REPORT.md` containing: the worked comparison for one simulated eval (all statistics, one-line interpretation each), the operating-characteristics tables, the sample-size table, and a **decision memo** for a hypothetical stakeholder |

### 11.3 Layout and starter

```
promptab/
├── pyproject.toml  requirements.txt  README.md  ANALYSIS_PLAN.md  REPORT.md
├── src/promptab/{__init__,simulate,tests_paired,bootstrap,power,decision,inferkit}.py
├── tests/{test_simulate,test_mcnemar,test_bootstrap,test_decision}.py
├── notebooks/12_prompt_comparison.ipynb
└── results/
```

```python
# src/promptab/simulate.py
from functools import lru_cache
import numpy as np

@lru_cache(maxsize=None)
def _intercept(target, difficulty_sd):
    """Logit intercept c with mean(sigmoid(c − d)) = target for d ~ N(0, difficulty_sd²); cached so repeated simulations stay fast."""
    z = np.random.default_rng(12345).normal(size=100_000) * difficulty_sd; lo, hi = -15.0, 15.0
    for _ in range(50):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if np.mean(1 / (1 + np.exp(-(mid - z)))) < target else (lo, mid)
    return (lo + hi) / 2

def simulate_eval(n_items, acc_a, acc_b, difficulty_sd=1.0, judge_error=0.0, seed=0):
    """Paired pass/fail outcomes. Item difficulty is shared; the intercepts are chosen so the marginal accuracies equal acc_a and acc_b."""
    g = np.random.default_rng(seed); d = g.normal(size=n_items) * difficulty_sd
    ca, cb = _intercept(float(acc_a), float(difficulty_sd)), _intercept(float(acc_b), float(difficulty_sd))
    a = g.random(n_items) < 1 / (1 + np.exp(-(ca - d))); b = g.random(n_items) < 1 / (1 + np.exp(-(cb - d)))
    if judge_error > 0:                                                      # symmetric label noise on the observed outcomes
        a = np.where(g.random(n_items) < judge_error, ~a, a); b = np.where(g.random(n_items) < judge_error, ~b, b)
    return a, b
```

```python
# src/promptab/tests_paired.py
import math
import numpy as np
from .inferkit import two_sided_p_from_z

def mcnemar(a, b):
    """a, b: boolean arrays (item-aligned). Returns discordant counts and exact / z p-values."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if a.shape != b.shape: raise ValueError("outcome arrays must be aligned item by item")
    only_a, only_b = int(np.sum(a & ~b)), int(np.sum(~a & b)); m = only_a + only_b
    if m == 0: return {"b": 0, "c": 0, "p_exact": 1.0, "p_z": 1.0, "diff": 0.0}
    k = min(only_a, only_b); p_exact = min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m)
    return {"b": only_a, "c": only_b, "p_exact": p_exact, "p_z": two_sided_p_from_z((only_a - only_b) / math.sqrt(m)), "diff": (only_b - only_a) / len(a)}
```

```python
# src/promptab/bootstrap.py
import numpy as np

def paired_bootstrap_diff(a, b, B=4000, level=0.95, seed=0):
    g = np.random.default_rng(seed); n = len(a); idx = g.integers(0, n, size=(B, n))
    diffs = b.astype(float)[idx].mean(1) - a.astype(float)[idx].mean(1); lo, hi = np.quantile(diffs, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(b.mean() - a.mean()), float(lo), float(hi)
```

```python
# src/promptab/decision.py
from .bootstrap import paired_bootstrap_diff

def decide(a, b, min_improvement=0.01, B=2000, seed=0):
    """ANALYSIS_PLAN rule: ship B iff the 95% paired-bootstrap CI for (acc_B − acc_A) is entirely above 0 AND the estimate ≥ min_improvement;
    keep A iff the CI is entirely below 0; otherwise inconclusive."""
    d, lo, hi = paired_bootstrap_diff(a, b, B=B, seed=seed)
    if lo > 0 and d >= min_improvement: return "ship B", d, (lo, hi)
    if hi < 0: return "keep A", d, (lo, hi)
    return "inconclusive", d, (lo, hi)
```

```python
# tests/test_decision.py
import numpy as np
from promptab.simulate import simulate_eval
from promptab.tests_paired import mcnemar
from promptab.decision import decide

def test_simulator_hits_target_accuracies():
    a, b = simulate_eval(200_000, 0.80, 0.82, seed=1); assert abs(a.mean() - 0.80) < 0.004 and abs(b.mean() - 0.82) < 0.004

def test_mcnemar_type1_error_is_near_alpha():
    rej = sum(mcnemar(*simulate_eval(500, 0.8, 0.8, seed=s))["p_exact"] < 0.05 for s in range(1500)) / 1500
    assert 0.02 < rej < 0.07                                 # exact McNemar is conservative; [VERIFY] bounds against your own run

def test_decision_rule_false_ship_rate_is_small_under_the_null():
    ships = sum(decide(*simulate_eval(500, 0.8, 0.8, seed=s), B=500)[0] == "ship B" for s in range(600)) / 600
    assert ships < 0.05                                      # one-sided: ship only when the whole CI is above 0 [VERIFY] against your run

def test_misaligned_inputs_raise():
    import pytest
    with pytest.raises(ValueError): mcnemar(np.ones(5, bool), np.ones(6, bool))
```

`[VERIFY]` Copy `inferkit.py` from Unit 1 into the package. Confirm the numeric bounds in the Type-I tests by running them: exact McNemar is conservative (below the nominal 5%), and the "ship" rule is one-sided in effect. Record your measured rates.

### 11.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Simulator hits the target marginal accuracies within `0.4` points at `n = 2·10⁵`; McNemar Type I error within `[0.02, 0.07]` over ≥ 1,500 null evaluations; misaligned inputs rejected |
| M2 | R4–R5 | Paired-bootstrap interval vs McNemar-based interval agree within 10%; unpaired bootstrap shown to be wider on correlated outcomes; effect sizes with intervals |
| M3 | R6 | Power curves (analytic vs simulated within `0.03`); required-`n` table for 1- and 2-point lifts at three baseline accuracies; MDE at your `n` |
| M4 | R7–R8 | `ANALYSIS_PLAN.md` written *before* the simulations (check commit order); operating-characteristics tables with binomial SEs for `n ∈ {200, 500, 1000, 3000}` |
| M5 | R9–R11 | Judge-noise attenuation quantified; multiple-metric false-win rates with/without Holm/BH; peeking-inflation table |
| M6 | R12 | `REPORT.md` regenerated by one script; decision memo present; every rate cites `N` repetitions and its SE |

### 11.5 Statistical-honesty requirements

- The **analysis plan precedes the results**; any deviation is listed in the report as exploratory.
- Report the realized **false-positive and power rates of the decision rule** with standard errors, and state that they hold *for the simulated difficulty model*, which may not match real evals.
- Distinguish **"inconclusive"** from **"no difference"**; include the interval and the MDE at the achieved `n`.
- Show at least one scenario where the right decision is **"collect more data"** and quantify how much.
- State that LLM-judge errors are modelled as symmetric noise here; real judges have systematic biases and need calibration against human labels.

### 11.6 Failure modes to demonstrate

Unpaired analysis of paired data; different items for the two prompts; reusing the evaluation items to tune the prompt (selection on the test set); peeking; five metrics, one "win"; judge bias; a tiny discordant count; non-independent items (several variants of the same question treated as independent: cluster bootstrap); reporting accuracy without `n`.

### 11.7 Stretch goals

1. Cluster-aware version: items grouped into question families; compare the cluster bootstrap with the item bootstrap.
2. Win-rate evaluation with ties (pairwise preference): sign test with ties handled, and Bradley–Terry-style comparisons `[VERIFY]`.
3. Sequential design: a group-sequential boundary with 4 looks (Pocock or O'Brien–Fleming) and its measured operating characteristics `[VERIFY: boundaries]`.
4. Judge calibration: estimate judge error against a small human-labelled subset and correct the accuracy difference (`(observed)/(1 − 2e)`); propagate the uncertainty by bootstrap.
5. Bayesian version: a Beta–Dirichlet model for the discordant pairs; report `P(B > A)` and compare with the frequentist decision.

### 11.8 ML connection (README prompt)

Write the five sentences you would put in a model-launch review for a prompt change: the estimate and interval, the test and its assumptions, the power/MDE at this sample size, the decision rule fixed in advance, and the biggest remaining risk (judge noise, test-set reuse, distribution shift).

### Check yourself (Unit 11)

1. Why is the analysis plan written before the simulations?
2. Why can the same eval be "inconclusive" and yet *not* show "no difference"?
3. How does a noisy symmetric judge change the observed accuracy difference?

**Reference answers:** (1) It fixes the decision rule so its error rates are those of a pre-specified procedure rather than of a rule tuned to the results. (2) An interval that spans both zero and practically meaningful improvements means the data cannot distinguish them (low power), which is different from evidence of equality. (3) It shrinks the observed difference toward zero by a factor `(1 − 2e)` and adds variance, reducing power.

---

## Unit 12 — Project: Bootstrap confidence-interval lab (`Projects/02-…md`)

### 12.1 Brief

Build `bootlab`: implementations of the percentile, basic, and bootstrap-`t` intervals (and BCa as a stretch), applied to several statistics (mean, median, trimmed mean, correlation, AUC, ratio), with **coverage audits** across distributions and sample sizes, plus the failure cases (extremes, heavy tails, dependence, clusters).

**Industry framing:** teams use bootstrap intervals for metrics with no formula, usually without ever checking their coverage. The lab is that check: for *which statistics, distributions, and `n`* can you trust a bootstrap interval, and what does it cost when you cannot?

### 12.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Core resampler | Vectorized `(B, n)` index draws, memory-safe chunking, seeded via `SeedSequence`; supports row, paired, cluster, and block resampling |
| R2 | Interval methods | Percentile, basic, and bootstrap-`t` (with an inner SE estimate: analytic where available, else a nested bootstrap with a small inner `B`); validated input (`n ≥ 2`, `0 < level < 1`) |
| R3 | Statistics | mean, median, 20% trimmed mean, Pearson correlation, AUC via the rank formula (Module 06 Lesson 5), ratio of means, standard deviation |
| R4 | Coverage audit | For each (statistic × distribution × `n × method`) cell: coverage over ≥ 1,500 outer repetitions with `B = 500` and the binomial SE of the coverage; distributions include normal, exponential, lognormal, Pareto `α = 1.5`, Bernoulli 0.05, and a two-component mixture; `n ∈ {10, 30, 100, 300}` |
| R5 | Comparison with analytic intervals | `t`-interval and Wilson/Clopper–Pearson where applicable; table of coverage and mean width; "winner" per cell with the SE caveat |
| R6 | `B` sensitivity | Interval end-point stability vs `B ∈ {100, 500, 2000, 10000}`; Monte Carlo error of the end-points over repeated runs |
| R7 | Failure catalogue | (a) max/min statistic: coverage ≈ 0; (b) Pareto `α = 1.5` mean: persistent under-coverage; (c) AR(1) series: iid bootstrap under-covers, block bootstrap repairs with a block-length study; (d) clustered data: row vs cluster bootstrap; (e) tiny `n` |
| R8 | Paired/cluster/block variants | Implementations validated against a known truth (simulated SE) |
| R9 | Cost accounting | Time and memory of each method as `n`, `B` grow (your machine, with versions) |
| R10 | Report | `REPORT.md`: coverage tables with SEs, the `B` study, the failure catalogue, and a decision table "which interval for which statistic and situation" backed by the audit |

### 12.3 Layout and starter

```
bootlab/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/bootlab/{__init__,resample,intervals,stats,audit,inferkit}.py
├── tests/{test_resample,test_intervals,test_audit}.py
├── notebooks/12_bootstrap_lab.ipynb
└── results/
```

```python
# src/bootlab/resample.py
import numpy as np

def spawn_rngs(seed, k): return [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(k)]

def row_indices(n, B, rng): return rng.integers(0, n, size=(B, n))

def cluster_indices(cluster_ids, B, rng):
    ids = np.asarray(cluster_ids); uniq = np.unique(ids); groups = [np.nonzero(ids == u)[0] for u in uniq]
    out = []
    for _ in range(B):
        pick = rng.integers(0, len(uniq), len(uniq)); out.append(np.concatenate([groups[j] for j in pick]))
    return out                                                              # list of index arrays (lengths differ)

def block_indices(n, B, block, rng):
    nb = int(np.ceil(n / block)); starts = rng.integers(0, n - block + 1, size=(B, nb))
    return (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(B, -1)[:, :n]
```

```python
# src/bootlab/intervals.py
import numpy as np

def percentile_ci(theta_star, level=0.95): a = (1 - level) / 2; return tuple(np.quantile(theta_star, [a, 1 - a]))
def basic_ci(theta_hat, theta_star, level=0.95): lo, hi = percentile_ci(theta_star, level); return 2 * theta_hat - hi, 2 * theta_hat - lo

def bootstrap_t_ci(x, stat, se_fn, B=1000, level=0.95, rng=None):
    """Studentized bootstrap: pivot (θ* − θ̂)/SE*. `se_fn(sample)` must return a standard-error estimate for the statistic."""
    rng = rng or np.random.default_rng(0); x = np.asarray(x); n = len(x); th = stat(x); se = se_fn(x); t = np.empty(B)
    for b in range(B):
        xb = x[rng.integers(0, n, n)]; t[b] = (stat(xb) - th) / max(se_fn(xb), 1e-12)
    a = (1 - level) / 2; lo_q, hi_q = np.quantile(t, [a, 1 - a]); return th - hi_q * se, th - lo_q * se
```

```python
# tests/test_intervals.py
import numpy as np
from bootlab.resample import row_indices, block_indices, cluster_indices
from bootlab.intervals import percentile_ci, basic_ci, bootstrap_t_ci

def test_resample_shapes_and_range():
    g = np.random.default_rng(0); idx = row_indices(50, 200, g); assert idx.shape == (200, 50) and idx.min() >= 0 and idx.max() < 50
    b = block_indices(100, 10, 7, g); assert b.shape == (10, 100) and b.max() < 100
    cl = cluster_indices(np.repeat(np.arange(10), 5), 3, g); assert len(cl) == 3 and all(len(c) == 50 for c in cl)

def test_distinct_fraction_is_about_632():
    g = np.random.default_rng(1); n = 2000; idx = row_indices(n, 300, g); frac = np.mean([len(np.unique(r)) / n for r in idx])
    assert abs(frac - (1 - np.exp(-1))) < 0.01

def test_percentile_coverage_for_the_mean_of_normal_data():
    g = np.random.default_rng(2); hit = 0; reps = 600
    for _ in range(reps):
        x = g.normal(5, 2, 50); th = x[row_indices(50, 400, g)].mean(1); lo, hi = percentile_ci(th); hit += lo <= 5 <= hi
    p = hit / reps; assert abs(p - 0.94) < 4 * np.sqrt(0.94 * 0.06 / reps) + 0.01        # percentile intervals are slightly narrow at n = 50 [VERIFY]

def test_bootstrap_t_runs_and_orders_endpoints():
    g = np.random.default_rng(3); x = g.exponential(size=40)
    lo, hi = bootstrap_t_ci(x, np.mean, lambda s: s.std(ddof=1) / np.sqrt(len(s)), B=300, rng=g); assert lo < x.mean() < hi
```

`[VERIFY]` Run the tests; the coverage test's tolerance depends on the number of repetitions (`reps = 600` gives a standard error near 0.01): measure coverage over several seeds before asserting numeric bounds.

### 12.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Resamplers pass shape/range/distinct-fraction tests; statistics match NumPy/closed forms |
| M2 | R2, R4 | Coverage grid for ≥ 4 statistics × 6 distributions × 4 sample sizes × 3 methods, each with a binomial SE; run in a documented `--quick` mode under 5 minutes |
| M3 | R5–R6 | Comparison with analytic intervals; `B`-sensitivity table with end-point Monte Carlo error |
| M4 | R7–R8 | All five failure cases reproduced with numbers; block-length study; cluster and block variants validated against the simulated truth |
| M5 | R9–R10 | Cost table; `REPORT.md` regenerated by one script; decision table cites the audit cells |

### 12.5 Statistical-honesty requirements

- Every coverage value has its **binomial SE**; do not rank methods whose coverages differ by less than ~3 SE.
- State the **number of outer repetitions** and `B` for every table.
- Distinguish **Monte Carlo error from resampling** (`B`) from the **statistical error** of the interval (`n`); show both.
- Include a cell where the bootstrap **beats** the analytic interval and a cell where it **loses**, with numbers.
- Say explicitly that results apply to the listed distributions and sample sizes, not to "bootstrap in general".

### 12.6 Failure modes to demonstrate

The maximum/minimum; infinite-variance heavy tails; tiny `n`; dependent data resampled as i.i.d.; clustered rows; paired data resampled independently; too small `B`; a statistic with ties (the median of integers); percentile intervals for a biased statistic (the standard-deviation estimator); bootstrap-`t` with an unstable inner SE.

### 12.7 Stretch goals

1. BCa intervals (bias-correction `z₀` from the replicates and acceleration `a` from the jackknife) with a coverage comparison `[VERIFY: formulas]`.
2. Smoothed bootstrap for the median; compare coverage.
3. Wild bootstrap for regression residuals under heteroscedasticity `[VERIFY]`.
4. Subsampling / m-out-of-n bootstrap for the maximum; show it repairs the extreme-value failure only partly `[VERIFY]`.
5. A calibration step: adjust the nominal level until the audited coverage hits 95% (prepivoting-style calibration) `[VERIFY]`.

### 12.8 ML connection (README prompt)

For three metrics you use (accuracy, AUC, a latency percentile) state which interval method you would use and the audit evidence behind it; describe what you would do if the evaluation rows come from a few hundred users.

### Check yourself (Unit 12)

1. Why should coverage audits report the binomial standard error?
2. Why does the bootstrap fail for the sample maximum?
3. What is the difference between `B` and `n` in terms of the error they control?

**Reference answers:** (1) A coverage estimate from a finite number of repetitions is noisy; small differences between methods are not evidence. (2) Every bootstrap replicate is at most the observed maximum, so the replicate distribution can never place mass above it and the interval cannot contain a true endpoint beyond it. (3) `B` controls the Monte Carlo error of the *interval end-points* (cheap to reduce); `n` controls the statistical uncertainty of the estimate itself (expensive to reduce).

---

## Unit 13 — Project: A/B test analysis report (`Projects/03-…md`)

### 13.1 Brief

Build `abreport`: an end-to-end analysis pipeline for an online experiment on simulated user-level logs (control vs treatment), producing a **decision report**. The pipeline performs data-quality and **sample-ratio** checks, defines metrics at the randomization unit, computes effects with intervals and tests (proportion metrics, a heavy-tailed revenue metric, and a guardrail), corrects for multiple metrics, assesses power/MDE, handles segments responsibly, and ends with a ship / don't ship / continue recommendation. Then validate the *pipeline* on thousands of simulated experiments with known truth (A/A tests, known lifts, peeking, novelty effects).

**Industry framing:** the artifact is the **decision memo** with the analysis behind it, plus the evidence that the pipeline has the false-positive rate and coverage it claims. Any team can compute a p-value; trustworthy experimentation comes from the checks around it.

### 13.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Experiment simulator | `simulate_experiment(n_users, split, p_conv, lift_abs, rev_mean/skew, novelty, seed)`: per-user assignment, conversion (Bernoulli), revenue (zero-inflated heavy-tailed, e.g., lognormal for converters), a guardrail (e.g., latency or complaint rate), a sessions-per-user covariate, optional novelty decay of the effect over time, and an optional assignment bug (biased allocation) |
| R2 | Data checks | Duplicate users, missing values, impossible values; **SRM test** with a strict threshold (`p < 0.001`); pre-experiment covariate balance check (standardized differences) |
| R3 | Metric definitions | Primary: conversion rate per user; secondary: revenue per user; guardrail: complaint/latency; all defined at the randomization unit (user) |
| R4 | Proportion analysis | Two-proportion z-test, interval for the absolute difference, relative-lift interval (delta method), Fisher exact when counts are small; consistency with a bootstrap interval |
| R5 | Heavy-tailed metric | Revenue per user: Welch interval, percentile bootstrap, winsorized/trimmed variant, and a comparison of their coverage in simulation; explain which you pre-specify and why |
| R6 | Multiplicity | Primary metric tested at `α = 0.05`; guardrails with one-sided non-inferiority margins; secondary metrics with Holm or BH; reported adjusted p-values |
| R7 | Power and MDE | Planned `n` from baseline and MDE; achieved MDE at the actual `n`; post-experiment interval-based interpretation (not post-hoc power) |
| R8 | Segments | Pre-specified ≤ 3 segments with an interaction check; demonstrate segment-fishing false positives with ≥ 20 post-hoc segments and the multiplicity correction |
| R9 | Time and novelty | Daily effect plot data; test for effect drift (regression of daily lift on day); recommend a minimum duration |
| R10 | Sequential/peeking | Compare a fixed-horizon analysis with daily peeking; with a corrected sequential rule `[VERIFY]`; report the realized false-positive rates |
| R11 | Pipeline validation | ≥ 2,000 A/A experiments: false-positive rate per metric and the family-wise rate with/without correction; ≥ 1,000 experiments with a known lift: coverage of the reported interval and power; an SRM-bug scenario: detection rate |
| R12 | Decision memo | `REPORT.md` with a **one-page memo**: recommendation, estimates with intervals on absolute and relative scales, guardrail status, SRM/data-quality status, power/MDE, caveats, and what would change the decision; plus an appendix with the validation tables |

### 13.3 Layout and starter

```
abreport/
├── pyproject.toml  requirements.txt  README.md  ANALYSIS_PLAN.md  REPORT.md
├── src/abreport/{__init__,simulate,checks,metrics,multiplicity,decision,validate,inferkit}.py
├── tests/{test_simulate,test_checks,test_metrics,test_validate}.py
├── notebooks/12_ab_test_report.ipynb
└── results/
```

```python
# src/abreport/simulate.py
import numpy as np

def simulate_experiment(n_users=20_000, split=0.5, p_conv=0.10, lift_abs=0.0, rev_sigma=1.0, rev_mu=3.0, complaint_rate=0.02, alloc_bug=0.0, seed=0):
    """Per-user logs. `alloc_bug` shifts the realized treatment share away from `split` (e.g., 0.02 → 52% instead of 50%)."""
    g = np.random.default_rng(seed); share = split + alloc_bug
    arm = (g.random(n_users) < share).astype(int)                                          # 1 = treatment
    sessions = g.poisson(5, n_users) + 1                                                    # pre-experiment covariate
    conv = g.random(n_users) < np.clip(p_conv + lift_abs * arm, 0, 1)
    revenue = np.where(conv, g.lognormal(rev_mu, rev_sigma, n_users), 0.0)
    complaint = g.random(n_users) < complaint_rate
    return {"arm": arm, "sessions": sessions, "conv": conv, "revenue": revenue, "complaint": complaint}
```

```python
# src/abreport/checks.py
import math
import numpy as np
from .inferkit import two_sided_p_from_z

def srm_check(arm, planned_share=0.5, threshold=1e-3):
    n = len(arm); n1 = int(arm.sum()); z = (n1 - planned_share * n) / math.sqrt(n * planned_share * (1 - planned_share)); p = two_sided_p_from_z(z)
    return {"n_treatment": n1, "n_control": n - n1, "z": z, "p": p, "srm": p < threshold}

def standardized_difference(x, arm):
    a, b = x[arm == 1], x[arm == 0]; return float((a.mean() - b.mean()) / math.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))
```

```python
# src/abreport/metrics.py
import math
import numpy as np
from .inferkit import two_sided_p_from_z

def proportion_effect(conv, arm):
    x1, n1 = int(conv[arm == 1].sum()), int((arm == 1).sum()); x0, n0 = int(conv[arm == 0].sum()), int((arm == 0).sum())
    p1, p0 = x1 / n1, x0 / n0; pp = (x1 + x0) / (n1 + n0); se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0)); z = (p1 - p0) / se0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0); d = p1 - p0
    return {"diff": d, "ci": (d - 1.96 * se, d + 1.96 * se), "z": z, "p": two_sided_p_from_z(z)}

def mean_effect_welch(x, arm):
    a, b = x[arm == 1], x[arm == 0]; d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); z = d / se
    return {"diff": float(d), "ci": (float(d - 1.96 * se), float(d + 1.96 * se)), "z": float(z), "p": two_sided_p_from_z(z)}
```

```python
# src/abreport/multiplicity.py
import numpy as np

def holm(pvals, alpha=0.05):
    p = np.asarray(pvals, float); m = len(p); order = np.argsort(p); rej = np.zeros(m, bool)
    for i, idx in enumerate(order):
        if p[idx] <= alpha / (m - i): rej[idx] = True
        else: break
    return rej

def benjamini_hochberg(pvals, alpha=0.05):
    p = np.asarray(pvals, float); m = len(p); order = np.argsort(p); ok = np.nonzero(p[order] <= (np.arange(1, m + 1) / m) * alpha)[0]
    rej = np.zeros(m, bool)
    if len(ok): rej[order[: ok.max() + 1]] = True
    return rej
```

```python
# tests/test_validate.py
import numpy as np
from abreport.simulate import simulate_experiment
from abreport.checks import srm_check
from abreport.metrics import proportion_effect

def test_aa_false_positive_rate_is_near_alpha():
    reps = 1500; fp = sum(proportion_effect(d["conv"], d["arm"])["p"] < 0.05 for d in (simulate_experiment(8000, seed=s) for s in range(reps))) / reps
    assert abs(fp - 0.05) < 4 * np.sqrt(0.05 * 0.95 / reps) + 0.005

def test_srm_detects_a_two_point_allocation_bug_at_scale_and_not_without_it():
    bug = [srm_check(simulate_experiment(40_000, alloc_bug=0.02, seed=s)["arm"])["srm"] for s in range(200)]
    ok = [srm_check(simulate_experiment(40_000, seed=1000 + s)["arm"])["srm"] for s in range(200)]
    assert np.mean(bug) > 0.95 and np.mean(ok) < 0.02

def test_ci_covers_the_true_lift_about_95_percent():
    reps, truth = 800, 0.01; hit = 0
    for s in range(reps):
        d = simulate_experiment(20_000, lift_abs=truth, seed=s); lo, hi = proportion_effect(d["conv"], d["arm"])["ci"]; hit += lo <= truth <= hi
    p = hit / reps; assert abs(p - 0.95) < 4 * np.sqrt(0.95 * 0.05 / reps) + 0.01
```

`[VERIFY]` Copy `inferkit.py` from Unit 1 into the package. The SRM detection thresholds in the test depend on the allocation shift and `n`; with `n = 40,000` and a 2-point shift the expected `z ≈ 8`, but record your measured detection rates. Confirm the A/A tolerance by running with several seeds.

### 13.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Simulator reproduces target conversion, revenue, and allocation (checked by large-`n` tests); data checks and SRM tested on clean and buggy allocations |
| M2 | R4–R5 | Proportion and revenue analyses agree with bootstrap intervals; coverage of the revenue intervals audited for Welch, bootstrap, and winsorized variants (heavy-tailed revenue at several `n`) |
| M3 | R6–R8 | Multiplicity implemented and verified (A/A family-wise rate with/without correction); segment-fishing demonstration with ≥ 20 post-hoc segments |
| M4 | R9–R10 | Novelty/drift detection; peeking vs fixed-horizon vs corrected-sequential false-positive rates with binomial SEs |
| M5 | R11 | ≥ 2,000 A/A runs and ≥ 1,000 known-lift runs: false-positive rates near nominal, interval coverage near 95%, power reported; SRM detection rate reported |
| M6 | R12 | `REPORT.md` with a one-page decision memo and a validation appendix, regenerated by one script from a clean venv |

### 13.5 Statistical-honesty requirements

- `ANALYSIS_PLAN.md` (primary metric, guardrails, segments, `α`, MDE, duration, stopping rule) is committed **before** the analysis code is run on the experiment.
- Every error-rate claim is a **measured rate ± SE** from the validation runs, with `N` repetitions.
- The memo must state **what is exploratory** (anything not in the plan) and **what is not known** (long-term effects, interference).
- Include an experiment where the correct recommendation is **"continue"** or **"don't ship"** and explain what evidence would change it.
- Do not report post-hoc power; report the interval and the planned MDE.

### 13.6 Failure modes to demonstrate

SRM from a logging bug; analysing at the wrong unit; revenue outliers dominating a mean difference; peeking; ten metrics, one win; segment fishing; novelty effect inflating a short test; including never-exposed users (dilution); pre-experiment imbalance; a guardrail ignored because the primary metric won.

### 13.7 Stretch goals

1. CUPED/regression adjustment with the pre-experiment covariate; measure the variance reduction and the power gain `[VERIFY: estimator]`.
2. A group-sequential design with alpha spending; compare the expected sample size with the fixed horizon.
3. Cluster (geo) randomization with a design-effect-aware analysis.
4. Heterogeneous treatment effects with a held-out evaluation of subgroup claims.
5. A Bayesian decision analysis with expected loss, compared against the frequentist memo.

### 13.8 ML connection (README prompt)

Describe how this pipeline would evaluate a new ranking model or prompt in production: the randomization unit, the primary and guardrail metrics, the checks you would automate, and how offline metrics from Project 1 would feed the choice of what to put into the online test.

### Check yourself (Unit 13)

1. Why run A/A experiments to validate an experimentation pipeline?
2. What should you do first when an experiment shows an SRM?
3. Why define metrics at the randomization unit?

**Reference answers:** (1) With no true effect, the realized false-positive rate and interval coverage can be measured directly; deviations reveal bugs or violated assumptions. (2) Stop, find the cause in assignment/logging/filtering, and not interpret any metric from that experiment until fixed. (3) Units that are randomized are the independent observations; analysing at a finer level (events) treats correlated rows as independent and understates the uncertainty.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 7 lessons, 3 projects, 13 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 06, 08–11, 13, 4C-04, and Stage 5 pointers (5A-06/07/08, 5B-04/07/09/10, 5C-03/15, 5D-08/12) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: ASA p-value guidance wording, BH validity conditions and Benjamini–Yekutieli, Nadeau–Bengio correction, Pocock boundary values, Welch–Satterthwaite formula, delta-method variance for the log ratio, CUPED, always-valid/sequential inference, TOST, Fisher exact two-sided definition, BCa formulas, bootstrap-`t` conditions.
4. `[VERIFY]` All printed numerical results (coverage, false-positive rates, power, exaggeration factors) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, pytest 9): every lesson snippet executed; all 4 `promptab`, all 4 `bootlab`, and all 3 `abreport` tests passed. Defects found and fixed during the run: a width demo that subtracted the lower bound of one sample from the upper bound of another; a McNemar power demo whose "2-point lift" construction actually produced a much smaller lift (now an intercept shift with the realized lift reported); a TOST demo that never demonstrated equivalence (now shown at two sample sizes); `simulate_eval` recomputed its intercepts by 50-step bisection over 100,000 samples on every call, which stalled the tests (now cached; the suite runs in about 4 seconds); and the stage checkpoint about heavy tails (see §1.6). Measured in seeded runs: (a) `t` quantiles from `inferkit` matched the tabulated values (2.776, 2.262, 2.045, 12.706, 1.962); `z` vs `t` coverage at `n = 12` was 0.924 vs 0.949; Wald vs Wilson coverage at `p = 0.03`, `n = 100` was 0.801 vs 0.969; overlapping 95% intervals coexisted with a significant difference (`z = 2.40`); (b) bootstrap: the row bootstrap SE was 0.046 vs a true 0.132 for clustered data (cluster bootstrap 0.121), the iid bootstrap SE was 0.046 vs a true 0.131 for AR(1) data (block bootstrap 0.135), percentile coverage of the maximum's true endpoint was 0.0, and percentile-bootstrap coverage for exponential data was 0.870 / 0.910 / 0.939 at `n = 10 / 30 / 100` against the `t` interval's 0.914 / 0.923 / 0.942; (c) hypothesis tests: p-values below 0.05 occurred 5.45% of the time under a true null (20,000 tests); with 100 hypotheses (10 true) the chance of any false rejection was 0.988 uncorrected, 0.042 Bonferroni, 0.043 Holm, 0.237 BH, with BH's mean false-discovery proportion 0.044 and power 0.510 vs Holm's 0.321; 10 peeks inflated the Type I error to 0.193; (d) paired tests: pooled-variance `t` had Type I error 0.289 vs Welch's 0.045 (unequal variances and sizes); paired power was 0.954 vs 0.249 unpaired for strongly shared item difficulty; McNemar Type I error was 0.040 exact / 0.046 `z`; McNemar power for a realized 2.1-point lift was 0.118, 0.185, 0.480 at 500, 1,000, 3,000 items; naive CV-fold `t`-test Type I error was 0.152 / 0.346 / 0.513 at fold correlation 0.1 / 0.3 / 0.5, and 0.051 / 0.049 / 0.050 with the corrected variance; (e) A/B testing: the planned `n = 14,751` per arm gave Type I error 0.050 and power 0.805; halving the lift needed 57,763 (3.9×); Fisher's exact `p = 0.0187` vs a z-test `p = 0.0080` on `[[3, 17], [11, 9]]`; a 2% allocation imbalance at `n = 20,000` gave an SRM `p` of 0.0047 (not below the strict 0.001 threshold) while a 4% imbalance at `n = 10,000` gave `p ≈ 6e-5`; A/A false-positive rate was 0.050 with one look and 0.199 with 10 peeks; (f) power: analytic and simulated power agreed (0.145 vs 0.146 at `d = 0.2`, `n = 40`); significant estimates at that power were exaggerated 2.7× with 1.4% having the wrong sign, falling to 1.12× at `n = 393`; paired power for `δ = 0.3`, `n = 60` was 0.376 / 0.642 / 0.957 at score correlation 0 / 0.5 / 0.8; TOST declared equivalence within ±1 point at `n = 40,000` but not at `n = 8,000`; (g) causation: with a true effect of −0.50 the naive observational estimate was +0.73, the regression-adjusted −0.49, the randomized −0.51, the 10-bin stratified −0.42, and adjustment for a noisy proxy +0.46; 39% of independent random-walk pairs had |r| > 0.5 (0% for white noise); the best of 500 noise features had |r| = 0.478 at `n = 40`; a leaky feature raised accuracy from 0.750 to 0.953; (h) `promptab` decision rule: false-ship rate 0.017 / 0.017 / 0.040 at `n = 200 / 1,000 / 3,000`, ship rate for a true +2 points 0.073 / 0.203 / 0.567; a symmetric judge error `e` shrank the observed lift by `(1 − 2e)` (0.0238 vs 0.0240 predicted at `e = 0.2`); McNemar peeking at 10 looks gave a 0.159 false-positive rate; five null metrics gave a 0.222 chance of a false win uncorrected and 0.051 with Holm; (i) bootstrap vs `t` interval at `n = 100` (800 datasets): width ratio 0.971 (normal), 0.951 (Pareto `α = 1.5`), 0.965 (lognormal); coverage bootstrap/`t` 0.954/0.961, 0.724/0.706, 0.919/0.919. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has an `ANALYSIS_PLAN.md`, tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No p-value, interval, power, coverage, or false-positive rate appears without the measurement that produced it and its standard error.
