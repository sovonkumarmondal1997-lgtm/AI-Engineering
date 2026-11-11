# Hypothesis Testing and Confidence Intervals

> **Module:** Stage 2C — Data Engineering_3  
> **Lesson:** 09 — Analytics Foundations for Data Engineers, Topic 03  
> **Target file:** `03-hypothesis-testing-and-confidence-intervals.md`  
> **Level:** Beginner → Intermediate → Advanced  
> **Scope:** Statistical inference and reliable analytical implementation. Experiment assignment and end-to-end A/B-test pipeline architecture belong to the next lesson.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- State null and alternative hypotheses and interpret a test statistic, p-value, significance level, and decision without overstating what they mean.
- Construct and interpret confidence intervals for means and proportions.
- Select and implement t-tests, Welch's t-test, proportion z-tests, chi-square tests, Mann–Whitney U tests, bootstrap intervals, and permutation tests.
- Check assumptions, recognize dependence and selection bias, and choose robust alternatives.
- Plan sample size from a minimum detectable effect (MDE), significance level, power, sidedness, and allocation.
- Control false discoveries across multiple metrics using Bonferroni, Holm, or Benjamini–Hochberg.
- Explain clustered observations, ratio metrics, the delta method, and CUPED at an awareness level.
- Build reproducible simulations that recover known effects, estimate empirical power, and measure false-positive rates.
- Separate statistical evidence from business value, causal claims, and data-quality guarantees.

## 2. Role of inference in analytics engineering

Descriptive statistics summarize the data observed. **Statistical inference** uses a sample or experiment to quantify uncertainty about a broader process or population. A pipeline may deliver perfectly valid rows and still support an invalid conclusion if the analysis treats repeated events as independent users, ignores missing outcomes, or selects a test after seeing the results.

A trustworthy inference workflow has four distinct layers:

1. **Data contract:** who/what is observed, assignment unit, metric definition, time window, exclusions, late-event policy, and missingness.
2. **Statistical design:** estimand, hypotheses, test, assumptions, significance level, power, and analysis plan.
3. **Computation:** validated input table, reproducible code, test statistic, p-value, interval, and effect size.
4. **Decision:** whether the estimated effect is meaningful given uncertainty, costs, risks, and guardrails.

A small p-value is not a data-quality test, proof of causality, or proof of commercial value. Random assignment and a sound measurement pipeline support causal interpretation; a test alone does not.

### Example

Suppose a checkout change has a measured conversion rate of 10.4% versus 10.0%. The observed absolute difference is 0.4 percentage points. Whether this is compelling depends on sample size and uncertainty. Whether it is worth shipping also depends on implementation cost, latency, errors, and the predeclared minimum worthwhile effect.

## 3. Prerequisites and environment setup

Assumptions: Python 3.10+ (the roadmap recommends Python 3.12+), basic probability and algebra, NumPy arrays, and familiarity with tabular data.

Create an isolated project:

```bash
mkdir inference-lab
cd inference-lab
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy scipy statsmodels pandas
```

Save the code blocks from Sections 13–14 in a file such as `inference_lab.py`, or run them in order in a notebook. Use fixed random seeds for simulations. Record package versions with:

```bash
python -c "import numpy, scipy, statsmodels, pandas; print(numpy.__version__, scipy.__version__, statsmodels.__version__, pandas.__version__)"
```

Examples use current common APIs from NumPy, SciPy, and statsmodels. Statistical API details can differ across versions; check the installed library documentation if a signature differs.

## 4. Hypothesis-testing foundations

### 4.1 Population, estimand, and hypotheses

A **population** is the set or process we want to understand. A **sample** is the observed subset. An **estimand** is the exact quantity we want to estimate—for example, the difference in user-level conversion probabilities between treatment and control over a specified window.

- \(H_0\), the **null hypothesis**, usually states a reference value such as no difference: \(\Delta = 0\).
- \(H_1\), the **alternative hypothesis**, describes the departure being investigated: \(\Delta \ne 0\), \(\Delta > 0\), or \(\Delta < 0\).

A two-sided test is appropriate when either direction matters. A one-sided test is defensible only when the direction and decision rule are specified before seeing results and an effect in the opposite direction would not be treated as evidence for the desired claim.

**Example:** \(H_0:p_T-p_C=0\), \(H_1:p_T-p_C\ne0\), where \(p_T\) and \(p_C\) are treatment and control conversion probabilities.

**Data-engineering check:** verify that the treatment label comes from the assignment table, the analysis unit matches randomization, each unit has one well-defined outcome, and the observation window is applied consistently.

### 4.2 Test statistic and p-value

A test statistic measures how far the observed result is from what the null model predicts, relative to its expected variability. For a difference in means, a simple statistic is

\[
t = \frac{\bar{x}_T-\bar{x}_C}{SE(\bar{x}_T-\bar{x}_C)}.
\]

The **p-value** is the probability, assuming the null hypothesis and the test's assumptions/model are true, of observing a test statistic at least as extreme as the one obtained, in the direction(s) defined by the test.

A p-value is **not**:
- the probability that \(H_0\) is true;
- the probability that the result is “due to chance”;
- the size or business importance of the effect;
- the probability that the finding will replicate.

A small p-value means the observed data are relatively incompatible with the specified null model, conditional on assumptions. It can also arise from a bad model, dependence, selection, measurement bugs, or multiple unreported analyses.

### 4.3 Significance level and decisions

The significance level \(\alpha\), often 0.05, is a prechosen long-run Type I error rate for a specified test under its assumptions. A conventional rule rejects \(H_0\) when \(p \le \alpha\); otherwise, **fail to reject** \(H_0\). Do not say “accept the null” simply because the test is not significant.

The decision is a statistical rule, not the business decision. A release decision should consider effect size, interval, MDE, costs, guardrails, and risk tolerance.

### 4.4 Type I error, Type II error, power, and effect size

| Term | Meaning |
|---|---|
| Type I error | Reject \(H_0\) when it is true; probability is controlled at \(\alpha\) for a valid single test |
| Type II error | Fail to reject \(H_0\) when a particular alternative is true; probability \(\beta\) |
| Power | \(1-\beta\): probability of rejecting \(H_0\) under a specified alternative |
| Effect size | Magnitude of the difference, such as a 0.01 absolute conversion lift or standardized mean difference |

Power is not a fixed property of a test: it depends on the true effect, variance, sample size, alpha, sidedness, allocation, and analysis method. “80% power” means that if the specified effect and assumptions are true, the planned procedure rejects the null in about 80% of repeated experiments.

**Numerical intuition:** if a valid test has \(\alpha=0.05\), then across many independent repetitions of the exact null scenario, approximately 5% of tests are expected to reject. This does not mean each observed significant result has a 5% chance of being false.

## 5. Confidence intervals

### 5.1 Frequentist interpretation

A 95% confidence-interval procedure is designed so that, over repeated sampling under its assumptions, 95% of the intervals produced by that procedure contain the fixed true parameter. After observing one interval, it is not correct in the ordinary frequentist interpretation to say there is a 95% probability that this fixed parameter lies inside that particular interval.

A confidence interval communicates a range of parameter values compatible with the data and method. It should be reported with the estimate and design context.

### 5.2 Confidence interval for a mean

If observations are independent and approximately normal—or the sample is sufficiently large for the sampling distribution of the mean to be adequately approximated—the one-sample t interval is

\[
\bar{x} \pm t_{1-\alpha/2,n-1}\frac{s}{\sqrt{n}},
\]

where \(\bar{x}\) is the sample mean, \(s\) is the sample standard deviation, and \(n\) is sample size. The t critical value accounts for estimating the standard deviation.

**Example:** for \(n=100\), mean latency 220 ms and sample SD 50 ms, the standard error is \(50/\sqrt{100}=5\) ms. A 95% interval is approximately \(220 \pm 1.984(5)\), or about [210.1, 229.9] ms.

This interval describes uncertainty about the population mean, not the range containing 95% of individual latencies. For strongly skewed data, the mean interval may still be valid with a sufficiently large independent sample, but inspect the sampling design, outliers, and target estimand. A bootstrap or robust method may be more suitable for other estimands.

### 5.3 Confidence interval for a proportion

For \(x\) successes among \(n\) independent Bernoulli trials, \(\hat p=x/n\). A simple Wald interval is

\[
\hat p \pm z_{1-\alpha/2}\sqrt{\frac{\hat p(1-\hat p)}{n}}.
\]

The Wald interval can have poor coverage, especially for small samples or probabilities near 0 or 1; it can even extend below 0 or above 1. Prefer Wilson or exact methods for many practical cases. The example code uses statsmodels' proportion interval method.

### 5.4 Width and sample size

For a mean with fixed variability, standard error decreases proportional to \(1/\sqrt{n}\). To halve the standard error, approximately four times as many independent observations are needed. For a proportion, the standard error is approximately \(\sqrt{p(1-p)/n}\), so the same inverse-square-root pattern applies when \(p\) is stable.

This relationship can fail as a practical planning shortcut when observations are clustered, sampling is biased, the variance changes, missingness increases, or the estimand changes. More rows do not fix systematic bias.

### 5.5 Interval for a difference

For independent groups, a difference estimate is \(\hat\Delta=\bar{x}_T-\bar{x}_C\) for means or \(\hat\Delta=\hat p_T-\hat p_C\) for proportions. The interval's standard error must match the design and estimator. A valid interval containing zero often corresponds to a non-significant two-sided test at the matching level, but only when the interval and test are duals under the same method and assumptions.

## 6. Statistical tests by metric type

Choose the test from the estimand, metric type, design, and assumptions—not by which result looks most significant.

### 6.1 One-sample t-test

**Question:** Is the population mean different from a reference value \(\mu_0\)?

\[
t=\frac{\bar{x}-\mu_0}{s/\sqrt{n}}, \quad df=n-1.
\]

Assumptions: independent observations; a normal population for exact small-sample inference, or a sufficiently well-behaved sampling distribution for large-sample approximation. Severe outliers and dependence can invalidate simple interpretation.

```python
import numpy as np
from scipy import stats

latency_ms = np.array([190, 205, 212, 198, 225, 207, 214, 201, 219, 209])
result = stats.ttest_1samp(latency_ms, popmean=200, alternative="greater")
print(result.statistic, result.pvalue)
assert np.isfinite(result.statistic) and 0 <= result.pvalue <= 1
```

Interpretation: the p-value addresses evidence against a mean of 200 ms in the greater-than direction. It does not tell whether the difference is operationally important. Do not use it when the observations are repeated measurements incorrectly treated as independent or the reference value was chosen after inspecting the data.

### 6.2 Independent two-sample t-test and Welch's t-test

**Question:** Do two independent groups have different means?

The pooled Student t-test assumes equal population variances. Welch's test does not require equal variances and is a strong default for independent groups:

\[
t=\frac{\bar{x}_1-\bar{x}_2}
{\sqrt{s_1^2/n_1+s_2^2/n_2}}.
\]

Welch's degrees of freedom are estimated using the Welch–Satterthwaite approximation. Welch's test still assumes independent sampling units and is not a cure for severe dependence or arbitrary selection.

```python
import numpy as np
from scipy import stats

control = np.array([10.2, 9.8, 10.1, 9.7, 10.4, 10.0, 9.9])
treatment = np.array([10.7, 10.3, 10.9, 10.1, 10.5, 10.8])
res = stats.ttest_ind(treatment, control, equal_var=False, alternative="two-sided")
print({"mean_difference": treatment.mean() - control.mean(), "p_value": res.pvalue})
assert 0 <= res.pvalue <= 1
```

Use a paired test instead if the design genuinely pairs the same units or matched units; do not pretend paired observations are independent. For skewed metrics, decide whether the target is mean, median, trimmed mean, or another quantity and use a method aligned to that estimand.

### 6.3 Z-test for two proportions

**Question:** Do independent groups have different success probabilities?

For \(x_T\) successes out of \(n_T\) and \(x_C\) out of \(n_C\), estimate \(\hat p_T\) and \(\hat p_C\). A common null test uses the pooled estimate under \(H_0:p_T=p_C\):

\[
\hat p=\frac{x_T+x_C}{n_T+n_C}, \quad
z=\frac{\hat p_T-\hat p_C}
{\sqrt{\hat p(1-\hat p)(1/n_T+1/n_C)}}.
\]

The normal approximation is more reliable when expected successes and failures are sufficiently numerous; small counts may require exact or score-based methods. The formula assumes independent Bernoulli units. If users contribute many events, the events are not automatically independent trials.

```python
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

successes = [520, 500]  # treatment, control
sample_sizes = [5000, 5000]
z_stat, p_value = proportions_ztest(successes, sample_sizes, alternative="two-sided")
p_t = successes[0] / sample_sizes[0]
p_c = successes[1] / sample_sizes[1]
ci_t = proportion_confint(successes[0], sample_sizes[0], alpha=0.05, method="wilson")
ci_c = proportion_confint(successes[1], sample_sizes[1], alpha=0.05, method="wilson")
print({"lift": p_t - p_c, "z": z_stat, "p": p_value, "treatment_wilson_ci": ci_t, "control_wilson_ci": ci_c})
assert 0 <= p_value <= 1
```

For a confidence interval on the *difference* in proportions, use a method designed for that difference (for example, Newcombe/Wilson-based or an appropriate bootstrap), rather than subtracting two marginal intervals and calling the result a 95% interval.

### 6.4 Chi-square tests

**Question:** Is there evidence of association between categorical variables, or do observed category counts differ from specified expected counts?

For a contingency table, the Pearson statistic is

\[
\chi^2=\sum_{cells}\frac{(O-E)^2}{E},
\]

where \(O\) and \(E\) are observed and expected counts. Under the null and suitable conditions, it follows an approximate chi-square distribution with degrees of freedom determined by the table.

```python
import numpy as np
from scipy.stats import chi2_contingency

# Rows: control/treatment; columns: converted/not converted
table = np.array([[500, 4500], [520, 4480]])
chi2, p_value, dof, expected = chi2_contingency(table, correction=False)
print({"chi2": chi2, "p": p_value, "dof": dof, "expected": expected})
assert expected.shape == table.shape and np.all(expected > 0)
assert 0 <= p_value <= 1
```

Assumptions include independent observations and adequate expected cell counts for the asymptotic approximation. Sparse tables may need Fisher's exact test or another suitable method. A chi-square association does not establish causality and does not show which cell drives the association without further inspection.

### 6.5 Mann–Whitney U test

**Question:** Do two independent samples differ in their rank distributions?

Mann–Whitney compares ranks and can be interpreted as a test related to stochastic ordering. It is **not a universal test of medians**. A median-shift interpretation requires additional assumptions, such as similarly shaped distributions differing mainly by location. Different distribution shapes or spreads can yield a significant result even when medians match.

```python
from scipy.stats import mannwhitneyu

control = [1, 2, 2, 3, 4, 5, 8]
treatment = [2, 3, 4, 4, 5, 7, 12]
u_stat, p_value = mannwhitneyu(control, treatment, alternative="two-sided", method="auto")
print({"U": u_stat, "p": p_value})
assert 0 <= p_value <= 1
```

Use it when rank-based evidence matches the question and samples are independent. If the goal is a median difference, estimate that difference and use a confidence interval appropriate for it. Handle ties and small samples using library-supported methods.

## 7. Assumptions and diagnostics

### 7.1 Independence is a design property

Independence is not proven by a normality test. Events from the same user, measurements from the same device, records from the same household, or observations within a store/day may be correlated. Treating them as independent often underestimates uncertainty.

Start with the randomization or sampling unit. If assignment is by user, a user-level outcome is often appropriate. If assignment is by store, users within a store may be clustered and the analysis must respect store-level assignment.

### 7.2 Normality and the central limit theorem

The central limit theorem says that under suitable conditions, a standardized sum or mean approaches a normal distribution as the sample grows. It does not mean raw data become normal, and it does not automatically rescue heavily dependent data or extreme heavy tails with unstable variance.

For small samples, inspect data and design; for larger samples, consider whether the sampling distribution approximation is adequate. A formal normality test can flag tiny, irrelevant departures at large \(n\) and miss important problems at small \(n\). Use plots and domain knowledge as diagnostics, not as an automatic test-selection oracle.

### 7.3 Equal variance

The pooled two-sample t-test assumes equal variances. Welch's t-test is generally safer when this assumption is uncertain. Do not use a preliminary variance test as a mechanical gate that selects a test based on a noisy p-value; select a robust method from the design in advance.

### 7.4 Data and pipeline checks before inference

- Validate unique assignment keys and expected allocation.
- Check duplicate events, late arrivals, timezone boundaries, bot/internal traffic rules, and identity stitching.
- Ensure every group uses the same metric definition and window.
- Report denominators, missing outcomes, exclusions, and sample flow.
- Compare event-level and unit-level row counts.
- Freeze analysis choices before inspecting outcomes where possible.
- Persist input snapshot/version, code version, parameters, seed, and package versions.

Missingness can bias estimates if outcome availability differs by group or depends on the outcome. Excluding missing rows is not automatically harmless. Missing-data mechanisms and imputation require explicit assumptions; do not silently replace missing values with zero.

## 8. Bootstrap and permutation methods

### 8.1 Bootstrap confidence intervals

The bootstrap approximates sampling uncertainty by resampling observed units with replacement and recalculating a statistic. It is useful for medians, trimmed means, and complex metrics without a convenient analytic interval.

For a difference between independent groups, resample **within each group**. For clustered data, resample clusters, not individual events. A bootstrap cannot correct selection bias or a nonrepresentative sample. Its validity can be poor for very small samples, extreme tails, boundary parameters, or statistics with difficult sampling behaviour.

```python
import numpy as np

def bootstrap_mean_difference(control, treatment, *, n_boot=5000, seed=2026):
    if not isinstance(n_boot, (int, np.integer)) or isinstance(n_boot, (bool, np.bool_)) or n_boot < 1:
        raise ValueError("n_boot must be a positive integer")
    rng = np.random.default_rng(seed)
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)
    if control.ndim != 1 or treatment.ndim != 1:
        raise ValueError("Each group must be a one-dimensional array")
    if control.size < 2 or treatment.size < 2:
        raise ValueError("Each group needs at least two observations")
    if not np.all(np.isfinite(control)) or not np.all(np.isfinite(treatment)):
        raise ValueError("Resolve missing and non-finite values before resampling")
    draws = np.empty(n_boot)
    for i in range(n_boot):
        c = rng.choice(control, size=control.size, replace=True)
        t = rng.choice(treatment, size=treatment.size, replace=True)
        draws[i] = t.mean() - c.mean()
    return np.quantile(draws, [0.025, 0.975]), draws

ci, draws = bootstrap_mean_difference([0, 1, 0, 1, 0, 0], [1, 1, 0, 1, 0, 1])
print("percentile bootstrap CI:", ci)
assert ci.shape == (2,) and ci[0] <= ci[1]
try:
    bootstrap_mean_difference([1.0, 2.0], [2.0, 3.0], n_boot=0)
except ValueError:
    pass
else:
    raise AssertionError("bootstrap must reject n_boot=0")
```

This is a percentile bootstrap interval. Other methods include basic, studentized, and BCa intervals; they have different properties and assumptions. The code is pedagogical and not optimized for very large datasets.

### 8.2 Permutation tests

A permutation test constructs a null distribution by shuffling group labels and recomputing the statistic. In a randomized experiment, treatment labels can be permuted according to the actual assignment design under a sharp null. For independent samples, simple label permutation assumes exchangeability under the null. For clustered or blocked designs, preserve those structures in the permutation scheme.

```python
import numpy as np

def permutation_test_mean_difference(control, treatment, *, n_perm=9999, seed=2026):
    if not isinstance(n_perm, (int, np.integer)) or isinstance(n_perm, (bool, np.bool_)) or n_perm < 1:
        raise ValueError("n_perm must be a positive integer")
    rng = np.random.default_rng(seed)
    c = np.asarray(control, dtype=float)
    t = np.asarray(treatment, dtype=float)
    if c.ndim != 1 or t.ndim != 1:
        raise ValueError("Each group must be a one-dimensional array")
    if c.size < 2 or t.size < 2:
        raise ValueError("Each group needs at least two observations")
    if not np.all(np.isfinite(c)) or not np.all(np.isfinite(t)):
        raise ValueError("Resolve missing and non-finite values before testing")
    observed = t.mean() - c.mean()
    pooled = np.concatenate([c, t])
    n_c = len(c)
    extreme = 0
    for _ in range(n_perm):
        permuted = rng.permutation(pooled)
        stat = permuted[n_c:].mean() - permuted[:n_c].mean()
        extreme += abs(stat) >= abs(observed)
    # Plus-one correction prevents a zero Monte Carlo p-value.
    p_value = (extreme + 1) / (n_perm + 1)
    return observed, p_value

observed, p = permutation_test_mean_difference([1, 2, 3, 4], [3, 4, 5, 6])
print({"difference": observed, "permutation_p": p})
assert 0 < p <= 1
try:
    permutation_test_mean_difference([1.0, 2.0], [2.0, 3.0], n_perm=0)
except ValueError:
    pass
else:
    raise AssertionError("permutation test must reject n_perm=0")
```

Permutation p-values are Monte Carlo approximations when only a subset of permutations is drawn. The plus-one correction is important for random permutation sampling. A permutation test does not automatically test equality of means under every possible unequal-variance distribution; validity depends on the null and exchangeability conditions.

## 9. Power analysis and sample-size planning

### 9.1 Define the planning problem

A sample-size answer is incomplete unless it specifies:

- primary estimand and metric;
- baseline rate or variance;
- MDE, in absolute or relative units;
- significance level \(\alpha\);
- target power \(1-\beta\);
- one- or two-sided test;
- allocation ratio;
- independent unit and expected clustering;
- exclusions, missing outcomes, and expected attrition.

The MDE is the smallest effect the design is intended to detect with the chosen power. It is not necessarily the smallest effect that matters to the business.

### 9.2 Worked proportion example: 1 percentage-point MDE

Assume two independent, equally allocated groups; baseline conversion \(p_C=0.10\), treatment conversion \(p_T=0.11\); absolute MDE \(=0.01\); two-sided \(\alpha=0.05\); power \(=0.80\); no clustering or attrition. The following uses statsmodels' normal-approximation power solver.

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

p_control = 0.10
p_treatment = 0.11
alpha = 0.05
target_power = 0.80
allocation_ratio = 1.0  # n_treatment / n_control
effect_size = proportion_effectsize(p_treatment, p_control)

analysis = NormalIndPower()
n_control = analysis.solve_power(
    effect_size=effect_size,
    power=target_power,
    alpha=alpha,
    ratio=allocation_ratio,
    alternative="two-sided",
)
n_per_group = int(__import__("math").ceil(n_control))
print({"effect_size_arcsine": effect_size, "n_per_group": n_per_group, "total": 2 * n_per_group})
assert n_per_group > 0
```

In the environment used to validate this lesson, this calculation returned 14,745 users per group (29,490 total); rerun it in your installed statsmodels version rather than assuming every version must print the same result. This is an approximation for planning, not a guarantee of realized power. Validate the planned design with simulation when the metric, assignment, or estimator is more complex. Increase the target for expected attrition and account for clustering via a design effect or a model appropriate to the design.

### 9.3 Empirical power and false-positive rate

Analytic power calculations rely on a model. Simulation gives an empirical check: repeatedly generate data under a specified alternative and count rejections; then repeat under the null. The Monte Carlo estimate itself has uncertainty. With \(R\) repetitions and a true rate \(q\), its standard error is approximately \(\sqrt{q(1-q)/R}\). At \(q=0.05\), \(R=1000\) gives a Monte Carlo standard error around 0.0069.

## 10. Multiple comparisons

Testing many outcomes or segments increases the chance of at least one false positive. If 20 independent null hypotheses are each tested at \(\alpha=0.05\), the probability of at least one false positive is

\[
1-(1-0.05)^{20}\approx 0.642.
\]

The independence calculation is illustrative; dependence changes the exact family-wise probability.

- **Bonferroni:** test each p-value against \(\alpha/m\), or multiply p-values by \(m\) and cap at 1. Controls family-wise error under arbitrary dependence, but can be conservative.
- **Holm:** step-down family-wise error control. Sort p-values; compare the smallest to \(\alpha/m\), next to \(\alpha/(m-1)\), and so on until the first failure. It is at least as powerful as simple Bonferroni in common settings and controls family-wise error under arbitrary dependence.
- **Benjamini–Hochberg (BH):** controls the expected false discovery rate (FDR), the expected fraction of false rejections among rejections, under independence and certain positive-dependence conditions. It does not control the probability of any false positive in the same way as Holm.

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

rng = np.random.default_rng(2026)
p_values = rng.uniform(0, 1, size=20)  # all 20 metrics are generated under the null
raw_reject = p_values < 0.05
holm_reject = multipletests(p_values, alpha=0.05, method="holm")[0]
bh_reject = multipletests(p_values, alpha=0.05, method="fdr_bh")[0]
print({
    "raw_rejections": int(raw_reject.sum()),
    "holm_rejections": int(holm_reject.sum()),
    "bh_rejections": int(bh_reject.sum()),
})
assert holm_reject.shape == bh_reject.shape == p_values.shape
```

One run can produce zero or more rejections; no particular count is guaranteed. Repeat the experiment many times to study long-run behaviour. Define the family of metrics and correction method before reviewing results. Corrections cannot fix p-hacking, biased measurements, or an invalid test.

## 11. Clustering, ratio metrics, and variance reduction

### 11.1 Unit of analysis and clustered observations

If treatment is assigned by user, the number of independent randomized units is generally the number of users, not the number of events. Users with many events can dominate event-weighted metrics. Decide whether the estimand is per-user conversion, per-event success, or something else before aggregation.

A simple simulation illustrates the issue: each user has a user-level propensity and multiple correlated events. An event-level test treats correlated rows as independent and often understates uncertainty. User-level aggregation makes the analysis unit explicit. In other designs, cluster-robust standard errors or hierarchical models may be needed; they require enough independent clusters and appropriate small-sample handling.

```python
import numpy as np
from scipy.stats import ttest_ind

rng = np.random.default_rng(2026)
n_users_per_group = 300
events_per_user = 20
# Shared user-level propensity induces within-user correlation.
control_propensity = rng.beta(2, 8, size=n_users_per_group)
treat_propensity = rng.beta(2, 8, size=n_users_per_group)
control_events = rng.binomial(1, control_propensity[:, None], size=(n_users_per_group, events_per_user))
treat_events = rng.binomial(1, treat_propensity[:, None], size=(n_users_per_group, events_per_user))

# Event-level analysis: illustrative and generally invalid if rows are dependent.
control_flat = control_events.ravel()
treat_flat = treat_events.ravel()
event_result = ttest_ind(treat_flat, control_flat, equal_var=False)
event_se = np.sqrt(control_flat.var(ddof=1) / len(control_flat) + treat_flat.var(ddof=1) / len(treat_flat))
# User-level conversion/outcome: one mean per user.
control_user_rates = control_events.mean(axis=1)
treat_user_rates = treat_events.mean(axis=1)
user_result = ttest_ind(treat_user_rates, control_user_rates, equal_var=False)
user_se = np.sqrt(
    control_user_rates.var(ddof=1) / len(control_user_rates)
    + treat_user_rates.var(ddof=1) / len(treat_user_rates)
)
print({
    "event_level_p_descriptive_only": event_result.pvalue,
    "event_level_naive_se": event_se,
    "user_level_p": user_result.pvalue,
    "user_level_se": user_se,
    "user_level_effect": treat_user_rates.mean() - control_user_rates.mean(),
})
```

This simulation is an illustration, not a universal claim that the event-level p-value will always be smaller. Dependence, unequal event counts, and the estimand determine the direction and magnitude of the distortion. In a real randomized experiment, analyse the randomized unit or use a method that correctly models the randomization and dependence.

### 11.2 Cluster-robust standard errors

When there are multiple observations per cluster and the estimand is not naturally one row per cluster, cluster-robust covariance estimators allow arbitrary within-cluster dependence while relying on independence across clusters. They are asymptotic and can perform poorly with few clusters. With few clusters, consider randomization inference, cluster-level analysis, or small-sample corrections appropriate to the design.

For example, if treatment is assigned to stores, use store as the cluster identifier. This illustration fits a linear model and clusters the covariance estimate by store; it is valid only if the number of independent stores is adequate and the model/estimand are appropriate.

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

rng = np.random.default_rng(77)
n_clusters = 80
rows_per_cluster = 15
cluster_ids = np.repeat(np.arange(n_clusters), rows_per_cluster)
cluster_assignment = rng.permutation(np.r_[np.zeros(n_clusters // 2), np.ones(n_clusters // 2)])
cluster_treatment = np.repeat(cluster_assignment, rows_per_cluster)
cluster_effect = np.repeat(rng.normal(0, 1, size=n_clusters), rows_per_cluster)
outcome = 5.0 + 0.25 * cluster_treatment + cluster_effect + rng.normal(0, 1, size=len(cluster_ids))
df = pd.DataFrame({"cluster_id": cluster_ids, "treatment": cluster_treatment, "outcome": outcome})
fit = smf.ols("outcome ~ treatment", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["cluster_id"]}
)
print({"treatment_effect": fit.params["treatment"],
       "cluster_robust_se": fit.bse["treatment"],
       "p_value": fit.pvalues["treatment"],
       "independent_clusters": df["cluster_id"].nunique()})
assert np.isfinite(fit.bse["treatment"]) and fit.bse["treatment"] > 0
```

This code uses cluster-robust standard errors, not a cluster-randomization test. Treatment is constant within cluster by construction. Do not interpret the row count as the independent sample size; the 80 clusters drive the large-sample approximation.

### 11.3 Ratio metrics and the delta method

Metrics such as revenue per user, clicks per impression, or cost per conversion are ratios \(R=A/B\). Variance of a ratio is not generally the variance of the numerator divided by the denominator squared, because numerator and denominator can both vary and be correlated.

For \(g(A,B)=A/B\), the first-order delta method uses a Taylor expansion around the means:

\[
\operatorname{Var}(A/B)\approx
\frac{\operatorname{Var}(A)}{\mu_B^2}
+\frac{\mu_A^2\operatorname{Var}(B)}{\mu_B^4}
-\frac{2\mu_A\operatorname{Cov}(A,B)}{\mu_B^3}.
\]

This is an approximation for sufficiently well-behaved distributions and a denominator not too close to zero. For user-level ratios, define whether the metric is a ratio of totals or an average of user-level ratios; they are different estimands. Bootstrap at the randomized unit is often a practical option.

### 11.4 CUPED awareness

CUPED (Controlled-experiment Using Pre-Experiment Data) uses a pre-treatment covariate \(X\) correlated with the outcome \(Y\) to reduce variance:

\[
Y_{\text{adjusted}}=Y-\theta(X-\bar X), \quad
\theta=\frac{\operatorname{Cov}(Y,X)}{\operatorname{Var}(X)}.
\]

The covariate must be measured before treatment and should not be affected by treatment. Under ideal linear conditions, variance reduction is related to the squared correlation between \(X\) and \(Y\). CUPED can improve precision but cannot repair assignment bugs, post-treatment leakage, missingness bias, or invalid inference. Freeze the method and validate the implementation.

## 12. Statistical pitfalls and responsible interpretation

- **P-hacking:** trying many analyses, subgroups, transformations, or stopping rules and reporting only favourable results.
- **Optional stopping:** repeatedly checking ordinary fixed-horizon p-values and stopping when one crosses 0.05 can inflate Type I error. Use a predeclared horizon, a valid sequential-testing design, or an always-valid procedure.
- **HARKing:** hypothesizing after results are known, then presenting the hypothesis as if it had been specified in advance.
- **Survivorship bias:** analysing only users, sessions, stores, or products that remain observable, excluding failures or dropouts in a way related to the outcome.
- **Statistical vs practical significance:** a tiny effect can be statistically significant at huge \(n\); a meaningful effect can be uncertain in a small study.
- **Causality:** a test on observational data does not remove confounding. Randomization supports causal inference only if assignment, exposure, outcome measurement, and analysis are valid.
- **Metric fishing:** report primary and guardrail metrics separately from exploratory metrics; apply multiplicity control where appropriate.
- **Bad denominators:** conversion is usually conversions divided by eligible randomized units, not arbitrary event rows.
- **Incomplete data:** differential missingness, delayed events, or broken instrumentation can create apparent effects. Validate data before interpreting inferential output.

### Bayesian alternative — awareness only

Bayesian inference combines a prior distribution with a likelihood to form a posterior distribution. A **credible interval** is an interval containing a stated posterior probability (for example, 95%) under the chosen model and prior. The posterior probability that treatment beats control can be directly expressed, but it depends on the prior, likelihood, data model, and estimand. A credible interval is not the same interpretation as a frequentist confidence interval. Bayesian analysis is not automatically immune to optional stopping or bad data; the model and decision rule still matter.

## 13. Python implementations

This section collects reusable helpers. All examples assume independent units unless stated otherwise.

### 13.1 A compact report for two independent means

```python
import numpy as np
from scipy import stats

def welch_summary(control, treatment, alpha=0.05):
    if not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)
    if control.ndim != 1 or treatment.ndim != 1:
        raise ValueError("Each group must be a one-dimensional array")
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("At least two observations per group are required")
    if not np.all(np.isfinite(control)) or not np.all(np.isfinite(treatment)):
        raise ValueError("Resolve missing and non-finite values before inference")
    estimate = treatment.mean() - control.mean()
    se = np.sqrt(control.var(ddof=1) / len(control) + treatment.var(ddof=1) / len(treatment))
    test = stats.ttest_ind(treatment, control, equal_var=False)
    # Welch-Satterthwaite degrees of freedom
    a = control.var(ddof=1) / len(control)
    b = treatment.var(ddof=1) / len(treatment)
    df = (a + b) ** 2 / (a**2 / (len(control) - 1) + b**2 / (len(treatment) - 1))
    critical = stats.t.ppf(1 - alpha / 2, df)
    return {
        "control_mean": control.mean(),
        "treatment_mean": treatment.mean(),
        "difference_treatment_minus_control": estimate,
        "standard_error": se,
        "confidence_interval": (estimate - critical * se, estimate + critical * se),
        "t_statistic": test.statistic,
        "p_value": test.pvalue,
        "degrees_freedom": df,
        "n_control": len(control),
        "n_treatment": len(treatment),
    }

summary = welch_summary([4, 5, 6, 5, 4], [6, 7, 6, 8, 7, 6])
print(summary)
assert summary["confidence_interval"][0] <= summary["confidence_interval"][1]
assert 0 <= summary["p_value"] <= 1
try:
    welch_summary([1.0, np.nan, 2.0], [2.0, 3.0])
except ValueError:
    pass
else:
    raise AssertionError("welch_summary must reject non-finite values")
```

The helper rejects non-finite values rather than silently dropping rows. Resolve missingness explicitly, report it by group, and assess whether exclusion is defensible before rerunning the summary. The helper also validates the confidence level and one-dimensional input shape.

### 13.2 Conversion rate difference with bootstrap interval

```python
import numpy as np
from statsmodels.stats.proportion import proportions_ztest

rng = np.random.default_rng(2026)
n_control = n_treatment = 5000
p_control, p_treatment = 0.10, 0.11
control = rng.binomial(1, p_control, size=n_control)
treatment = rng.binomial(1, p_treatment, size=n_treatment)

z, p_value = proportions_ztest(
    [treatment.sum(), control.sum()],
    [n_treatment, n_control],
    alternative="two-sided",
)

# Bootstrap difference in proportions, resampling randomized units within groups.
n_boot = 5000
boot = np.empty(n_boot)
for i in range(n_boot):
    c = rng.choice(control, size=n_control, replace=True)
    t = rng.choice(treatment, size=n_treatment, replace=True)
    boot[i] = t.mean() - c.mean()
ci = np.quantile(boot, [0.025, 0.975])
difference = treatment.mean() - control.mean()

print({"control_rate": control.mean(), "treatment_rate": treatment.mean(),
       "difference": difference, "z": z, "p": p_value, "bootstrap_ci": ci})
assert 0 <= p_value <= 1 and ci[0] <= ci[1]
```

The generated rates will vary with the fixed seed but are reproducible for a given compatible NumPy implementation. The z-test and bootstrap answer related but not identical inferential questions; compare the estimate and interval rather than expecting identical p-values. For large experiments, use vectorized or specialized bootstrap tooling to control runtime and memory.

## 14. Reproducible simulation lab

Run these exercises after installing the dependencies. Fixed seeds make the runs repeatable; finite simulations are noisy, so validate ranges rather than expecting exact counts.

### Lab 1 — Known difference and empirical power

Simulate independent normal outcomes with equal variance and a known mean difference. Power is the proportion of repetitions with \(p<0.05\).

```python
import numpy as np
from scipy.stats import ttest_ind

def simulate_rejection_rate(*, effect, n_per_group=100, repetitions=1000, seed=2026, alpha=0.05):
    rng = np.random.default_rng(seed)
    rejects = 0
    for _ in range(repetitions):
        control = rng.normal(0.0, 1.0, size=n_per_group)
        treatment = rng.normal(effect, 1.0, size=n_per_group)
        p = ttest_ind(treatment, control, equal_var=False).pvalue
        rejects += p < alpha
    return rejects / repetitions

power = simulate_rejection_rate(effect=0.3)
null_rate = simulate_rejection_rate(effect=0.0, seed=2027)
print({"empirical_power_at_effect_0.3": power, "null_false_positive_rate": null_rate})
# Loose Monte Carlo checks: these are not exact targets for any one finite run.
assert 0 <= power <= 1 and 0 <= null_rate <= 1
assert abs(null_rate - 0.05) < 0.04
```

The null-rate assertion is intentionally loose because 1,000 repetitions have Monte Carlo variation. Empirical power depends on the selected effect and sample size; increase \(n\) or effect size to generally increase power under this setup. The test uses Welch's t-test and continuous normal data.

### Lab 2 — Null simulations and Type I error

Run `simulate_rejection_rate(effect=0.0, repetitions=10000, seed=...)` with several seeds. The mean rejection rate should tend toward 0.05 under a correctly specified test, while individual runs fluctuate. If it is consistently too high, inspect the test assumptions, simulation, and stopping/reporting process.

### Lab 3 — One-percentage-point conversion MDE

Use Section 9.2 with baseline \(p_C=0.10\), treatment \(p_T=0.11\), two-sided \(\alpha=0.05\), 80% power, equal allocation, and independent users. Record the computed sample size per group. Then simulate the proposed sample size to verify that empirical power is near the target; exact agreement is not expected due to normal approximation and Monte Carlo error.

### Lab 4 — Twenty null metrics and multiplicity

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

rng = np.random.default_rng(303)
p = rng.uniform(size=20)
raw = p < 0.05
holm = multipletests(p, alpha=0.05, method="holm")[0]
bh = multipletests(p, alpha=0.05, method="fdr_bh")[0]
print({"p_values": p, "raw": int(raw.sum()), "holm": int(holm.sum()), "BH": int(bh.sum())})
assert np.all(holm <= raw) and np.all(bh <= raw)
```

Under the all-null setup, adjusted procedures should not create rejections that were not raw rejections. One run may have no raw rejections. To compare long-run false discoveries, repeat the 20-test experiment thousands of times and record the family-wise probability and rejection counts.

### Lab 5 — Optional stopping inflates false positives

This simulation performs repeated daily looks at independent null data, using a conventional fixed-horizon two-sample t-test at each look and stopping at the first \(p<0.05\). Because the repeated looks are not adjusted, the chance of at least one false positive exceeds the nominal single-look level in this setup.

```python
import numpy as np
from scipy.stats import ttest_ind

def optional_stopping_rate(*, experiments=2000, looks=10, n_per_group_per_look=20, seed=404):
    rng = np.random.default_rng(seed)
    false_positive = 0
    for _ in range(experiments):
        c_all = rng.normal(size=(looks, n_per_group_per_look))
        t_all = rng.normal(size=(looks, n_per_group_per_look))
        found = False
        for look in range(1, looks + 1):
            c = c_all[:look].ravel()
            t = t_all[:look].ravel()
            p = ttest_ind(t, c, equal_var=False).pvalue
            if p < 0.05:
                found = True
                break
        false_positive += found
    return false_positive / experiments

rate = optional_stopping_rate()
print({"false_positive_rate_with_repeated_looks": rate, "nominal_single_test_alpha": 0.05})
assert 0 <= rate <= 1
```

This simple simulation has accumulating sample sizes across looks and reuses earlier observations. Its exact false-positive rate depends on the look schedule and implementation; the point is that ordinary p-values are not calibrated for this unadjusted stopping rule. Use a fixed horizon or a formally valid sequential design rather than relying on this example's numerical output.

### Lab 6 — Clustering and the correct analysis unit

Use Section 11.1. Compare the event-level and user-level p-values and standard errors across multiple seeds. The event-level analysis is shown to illustrate the risk and is not recommended as the primary inference when user observations are correlated. In a production report, define the user-level estimand and preserve the assignment unit. For an event-weighted estimand, use a model and uncertainty estimator that account for within-user dependence.

### Lab 7 — Test implementation and validation

```python
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

# Known reference: identical arrays have zero mean difference.
x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
same = stats.ttest_ind(x, x, equal_var=False)
assert np.isclose(same.statistic, 0.0)
assert np.isclose(same.pvalue, 1.0)

# Wilson interval must be ordered and bounded in [0, 1].
low, high = proportion_confint(50, 100, alpha=0.05, method="wilson")
assert 0 <= low <= high <= 1

# A p-value must be finite and in [0, 1].
r = stats.ttest_1samp(x, popmean=0)
assert np.isfinite(r.pvalue) and 0 <= r.pvalue <= 1

print("Core validation checks passed.")
```

## 15. Exercises with solutions

### Exercise 1 — State the estimand

A product manager asks whether a new search ranking “improves engagement.” Define a measurable estimand, null and alternative hypotheses, the randomization unit, and one guardrail. Explain why a p-value alone cannot answer the product question.

**Solution sketch:** choose a predeclared metric such as user-level sessions with a meaningful search within seven days after assignment. Specify whether the target is a mean difference or probability difference. If randomized by user, use user as the unit. \(H_0:\Delta=0\), \(H_1:\Delta\ne0\) unless a justified one-sided alternative was predeclared. Include latency or error rate as a guardrail. Report effect size and interval; decide using business relevance and risk as well as statistical evidence.

### Exercise 2 — Select a method

Choose a method and state assumptions:
1. Mean order value for independent users in two arms.
2. Conversion success per randomized user.
3. Association between device type and conversion.
4. Two independent samples with strongly non-normal distributions where rank ordering is the target.
5. Difference in median session duration.

**Solution sketch:** (1) Welch's t-test plus an interval for mean difference, with bootstrap as a robustness option; (2) two-proportion z-test/score method with suitable counts, or exact/other method for sparse data; (3) chi-square if expected counts are adequate, otherwise an exact method; (4) Mann–Whitney U if its rank-distribution question matches the estimand; (5) estimate the median difference and use a suitable bootstrap or quantile method. Mann–Whitney is not automatically a median test.

### Exercise 3 — Interpret a result

A two-sided test gives \(p=0.03\), \(\alpha=0.05\), and estimated lift +0.1 percentage points with a 95% interval [0.01, 0.19] percentage points. What can and cannot be concluded?

**Solution sketch:** under the model and assumptions, the result is statistically significant at the specified level and the interval is above zero. The estimate is small; whether it is worthwhile depends on a predeclared practical threshold, costs, and guardrails. The p-value is not the probability the null is true, and statistical significance alone does not prove causality.

### Exercise 4 — Power and MDE

Why does detecting a 1 percentage-point lift from 10% to 11% usually require more users than detecting a 5-point lift from 10% to 15%, all else equal?

**Solution sketch:** a smaller effect is closer to the null relative to sampling variability, so the design needs a smaller standard error and therefore a larger sample. Use a stated power solver or simulation rather than a rule of thumb alone.

### Exercise 5 — Multiplicity

You test 20 null metrics at 0.05 and observe one raw p-value of 0.02. What should you report?

**Solution sketch:** disclose that 20 metrics were tested and state the family definition. Apply the preselected procedure. Bonferroni's threshold is 0.0025 for each test; a p-value of 0.02 does not pass. Holm and BH also need the full ordered p-value vector, so one p-value alone is insufficient to decide their result.

### Exercise 6 — Diagnose a suspicious result

Treatment has 10% more event rows than control, but assignment counts are balanced. The event-level test is highly significant; the user-level conversion test is not.

**Solution sketch:** check event volume per user, duplicate ingestion, treatment-driven exposure or logging changes, repeated-event dependence, and metric definition. The event-level result may target a different quantity and may understate uncertainty if events are correlated. Reconcile raw and curated tables and analyse at the unit aligned to the estimand.

## 16. Common mistakes

1. Interpreting \(p=0.04\) as a 96% chance that the effect is real.
2. Saying “accept the null” when \(p>\alpha\).
3. Reporting a p-value without an effect size, interval, metric definition, or sample counts.
4. Choosing one-sided tests after observing the direction of the result.
5. Using a pooled t-test when unequal variances are plausible without a design reason.
6. Treating the Mann–Whitney U test as a universal median comparison.
7. Assuming large sample size repairs dependence, bias, or bad instrumentation.
8. Ignoring missingness, attrition, duplicate events, or changed denominators.
9. Testing many metrics and reporting only the winner.
10. Repeatedly checking fixed-horizon p-values without sequential correction.
11. Confusing confidence intervals with intervals for individual observations.
12. Calling an effect causal based only on a statistical test.
13. Using event count as sample size when assignment and dependence are user-level.
14. Treating an approximate sample-size calculation as a guarantee of achieved power.
15. Confusing practical significance with statistical significance.

## 17. Knowledge checkpoint

Answer without looking back:

1. What does a p-value condition on?
2. What is the repeated-sampling meaning of a 95% confidence interval?
3. How do Type I error, Type II error, and power differ?
4. Why is Welch's t-test often a good default for independent means?
5. What does the central limit theorem say—and what does it not say?
6. When is a Mann–Whitney result not a median difference?
7. Why does repeated unadjusted peeking inflate false-positive risk?
8. What is the difference between Holm family-wise error control and BH false discovery rate control?
9. Why must uncertainty respect the unit of randomization and within-cluster dependence?
10. What assumptions are needed for a ratio's delta-method variance approximation?
11. What makes a Bayesian credible interval different from a frequentist confidence interval?
12. Which data-quality checks must pass before interpreting an experiment result?

## 18. Final competency checklist

- [ ] I can state a precise estimand, \(H_0\), and \(H_1\) before analysing results.
- [ ] I can explain p-values, alpha, Type I/II errors, power, and effect size accurately.
- [ ] I can compute and interpret mean and proportion confidence intervals.
- [ ] I can select and implement t-tests, Welch's test, proportion tests, chi-square, and Mann–Whitney U with explicit assumptions.
- [ ] I can use bootstrap intervals and permutation tests without violating the sampling or assignment design.
- [ ] I can plan sample size using a stated baseline, MDE, alpha, power, allocation, and sidedness.
- [ ] I can apply Bonferroni, Holm, and BH while distinguishing their goals.
- [ ] I can identify clustering and avoid treating repeated events as independent randomized units.
- [ ] I can explain ratio metrics, the delta method, and CUPED at an awareness level.
- [ ] I can detect optional stopping, p-hacking, HARKing, survivorship bias, and practical-significance errors.
- [ ] I can reproduce simulations, validate calculations, and report data-quality limitations.
- [ ] I distinguish statistical evidence from business decisions and causal claims.

## 19. Authoritative references

Use documentation matching the versions installed in your environment.

- SciPy statistical tests: <https://docs.scipy.org/doc/scipy/reference/stats.html>
- SciPy `ttest_ind`: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html>
- SciPy `mannwhitneyu`: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html>
- SciPy resampling methods: <https://docs.scipy.org/doc/scipy/reference/stats.html#resampling-and-monte-carlo-methods>
- statsmodels proportion tests: <https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html>
- statsmodels proportion confidence intervals: <https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html>
- statsmodels power analysis: <https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations>
- statsmodels multiple testing: <https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html>
- NumPy random Generator: <https://numpy.org/doc/stable/reference/random/generator.html>
- Wasserstein et al., *The ASA Statement on p-Values: Context, Process, and Purpose*: <https://doi.org/10.1080/00031305.2016.1154108>
- Lakens, *Sample Size Justification*: <https://doi.org/10.1525/collabra.33267>
- Deng, Xu, Kohavi, and Walker, *Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data*: <https://doi.org/10.1145/2433396.2433413>

---

**Completion criterion:** You are ready for the next roadmap lesson when you can explain the inference result and its assumptions, reproduce it from versioned inputs, validate the analysis unit and denominators, and communicate the effect and uncertainty without claiming more than the design supports.
