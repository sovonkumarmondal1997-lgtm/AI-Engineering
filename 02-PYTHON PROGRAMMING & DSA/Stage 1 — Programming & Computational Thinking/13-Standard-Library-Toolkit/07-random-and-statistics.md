# Randomness and Statistics with Python's Standard Library

> **Module 13 · Phase C — Security Primitives and Numbers · Lesson 07**  
> **Runtime target:** Python 3.12+  
> **Focus:** `random`, `statistics`, reproducible sampling, stream algorithms, and simulation.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain pseudorandomness, seeds, generator state, and why `random` is not a cryptographic API.
- Choose correctly among sampling with replacement, sampling without replacement, weighted selection, shuffling, and streaming reservoir sampling.
- Use independent `random.Random` instances to keep components and tests from interfering with one another.
- Compute descriptive statistics while distinguishing a population from a sample and handling empty or insufficient data deliberately.
- Use `statistics.NormalDist`, correlation, covariance, and linear regression without confusing descriptive summaries with causal or inferential conclusions.
- Build a reproducible Monte Carlo experiment and report uncertainty honestly.
- Test invariants and reproducibility, while understanding that one empirical run is not a proof of a statistical property.
- Know when `secrets`, NumPy's `Generator`, or specialist statistical tools are more appropriate.

## Prerequisites and roadmap boundaries

This lesson follows `06-hashlib-hmac-secrets-and-uuid.md` in Phase C of `13-Standard-Library-Toolkit/`. It builds on Python collections, iterators/generators, functions, exceptions, and pytest. The broader Stage 1 roadmap also develops files, configuration, safe writes, idempotency, and testing; these are useful when recording experiment configurations and creating deterministic test fixtures.

The roadmap's purpose here is reproducible sampling, train/test splits, simulations, test data, and quick descriptive summaries. NumPy is a later-stage option for vectorized numerical workloads, and broader statistical inference belongs to later mathematics/data-science modules. This lesson does not replace those courses.

## 1. Foundations: what randomness means in a program

### 1.1 Pseudorandom number generators

A pseudorandom number generator (PRNG) is a deterministic algorithm that expands an initial state into a sequence designed to have useful statistical properties. Given the same compatible algorithm, state, and calls, it can reproduce the same sequence. A **seed** initializes that state; it is not a promise that all Python versions or all algorithms will always produce identical results.

Why it matters: reproducibility lets engineers debug a failed simulation, regenerate a sample, compare pipeline runs, and create repeatable test fixtures. The trade-off is that deterministic state can be predicted or recovered in some threat models, so ordinary PRNG output must not be used for passwords, API keys, session tokens, or other secrets.

Python's default `random` generator uses MT19937 (Mersenne Twister), whose period is \(2^{19937}-1\). Its large state/period and statistical properties make it useful for simulation, but it is designed for simulation, not cryptographic security. Do not confuse statistical quality for a simulation with unpredictability against an attacker.

```python
import random

random.seed(7)  # Resets the module-global generator state.
print(random.random())

rng = random.Random(7)  # Prefer a local generator in reusable code.
print(rng.random())
```

In this same runtime, the two calls print the same value because each generator starts from seed `7`. Python specifically documents a compatibility guarantee for the `random()` sequence when a compatible seeder is used with the same seed; do not generalize that guarantee to higher-level algorithms such as `sample()`, `choices()`, or `gauss()`. If exact experiment replay matters, record the Python version and relevant implementation details.

### 1.2 `random`, `secrets`, and `SystemRandom`

| API | Intended use | Reproducible from a chosen seed? | Security-sensitive tokens? |
|---|---|---:|---:|
| `random.Random(seed)` / module `random` | Simulation, sampling, deterministic fixtures | Yes, within documented limits | **No** |
| `random.SystemRandom` | Draws from operating-system randomness; no reproducible state | No | Suitable low-level option, but prefer `secrets` for token-oriented APIs |
| `secrets` | Password-reset tokens, bearer tokens, security-sensitive choices | No | **Yes**, when used with sound token design and storage |
| `os.urandom(n)` | Raw bytes from the OS cryptographic randomness source | No | Suitable primitive for cryptographic needs; `secrets` is usually more convenient |

A secure random source does not by itself make an authentication workflow secure: token length, expiry, storage, transport, rate limiting, and revocation still matter. This lesson focuses on `random` and `statistics`; the previous lesson covers `secrets` in more depth.

## 2. Beginner `random` operations

Create a local generator so that calls in unrelated code do not change your result:

```python
import random

rng = random.Random(2025)
unit_interval = rng.random()          # float in [0.0, 1.0)
integer = rng.randint(1, 6)           # inclusive at both ends
item = rng.choice(["bronze", "silver", "gold"])
several = rng.choices(["A", "B", "C"], k=5)  # with replacement
unique = rng.sample(range(100), k=5) # without replacement
values = [1, 2, 3, 4]
rng.shuffle(values)                   # mutates this list in place
measurement = rng.uniform(10.0, 20.0)
normal_draw = rng.gauss(mu=100, sigma=15)
```

- `random()` returns a float from the half-open interval `[0.0, 1.0)`.
- `randint(a, b)` includes both endpoints; it is equivalent in range semantics to `randrange(a, b + 1)` for integer endpoints.
- `choice(sequence)` chooses one element; the sequence must be non-empty.
- `choices(population, k=n)` draws `n` times **with replacement**, so an item can repeat. It supports `weights=` or `cum_weights=`.
- `sample(population, k=n)` samples **without replacement from population positions**; `k` cannot exceed the population size. If the input itself contains duplicate values, equal-valued copies at different positions can both appear in the sample. In Python 3.11+, a set is not accepted as the population; convert to a deliberately ordered sequence if needed.
- `shuffle(mutable_sequence)` shuffles in place and returns `None`; it does not return the shuffled list.
- `uniform(a, b)` draws over the numeric interval; floating-point rounding can affect whether the upper endpoint is representable in a particular case.
- `gauss(mu, sigma)` draws from a normal distribution with the given mean and standard deviation. It is a model assumption, not a guarantee that real data are normally distributed. Treat `sigma` as a non-negative standard deviation; zero produces the constant `mu`. The documentation notes a thread-safety caveat for concurrent calls to `gauss()` on one shared generator: separate calls can return the same value under a race. Use separate generator instances per thread or another suitable method when this matters.

### Sampling with versus without replacement

Use `choices` for repeated independent draws such as simulated dice rolls or repeated customer selections. Use `sample` for unique row positions, a fixed-size audit sample from a materialized batch, or a train/test split without duplicate observations.

```python
import random

rng = random.Random(17)
population = ["a", "b", "c"]
with_replacement = rng.choices(population, k=8)
without_replacement = rng.sample(population, k=3)
assert len(without_replacement) == len(set(without_replacement))
```

The second assertion is an invariant, not a claim that every item is equally likely in every possible implementation or adversarial setting. For a standard `sample` from a finite population, uniform sampling is the documented intent.

### Weighted selection

Weights express relative selection probabilities, not necessarily percentages. For example, weights `[1, 2, 7]` represent relative proportions 10%, 20%, 70% for a single draw if the total is positive and the weights are valid. `cum_weights` is a cumulative sequence such as `[1, 3, 10]` for the same proportions.

```python
import random

rng = random.Random(31)
segment = rng.choices(
    population=["control", "variant_a", "variant_b"],
    weights=[70, 20, 10],
    k=100,
)
```

Weighted sampling with `choices` is with replacement. Weights are relative, not percentages; validate that they are finite and non-negative and that their total is positive. Cumulative weights must be valid cumulative totals. For large populations, `choices` can be efficient; avoid treating a short empirical run as proof of the intended probabilities. If you require weighted sampling **without** replacement, `choices` is not the right primitive; choose an algorithm designed for that problem and test its assumptions.

## 3. Seeds, generator state, and reproducibility

### 3.1 Why prefer `Random(seed)` over global `seed()`?

`random.seed(x)` resets the module-global generator. Any other code using that global generator can affect later results, creating hidden coupling. A local `rng = random.Random(seed)` makes ownership explicit and is easier to inject into functions and tests.

```python
from random import Random


def choose_partition(rows, *, seed: int, size: int):
    """Return a reproducible sample without mutating rows."""
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("size must be an integer")
    if size < 0:
        raise ValueError("size must be non-negative")
    rng = Random(seed)
    return rng.sample(rows, k=size)
```

A seed is only one part of an experiment record. Record at least:

- Python version and implementation where relevant;
- the seed and the generator/API used;
- algorithm version and code revision;
- input dataset identity/version and preprocessing rules;
- sample sizes, weights, partition keys, and configuration;
- relevant dependency versions and hardware/backend details for numerical libraries.

Python documents reproducibility guarantees carefully: algorithms or seeding behavior can change between versions, and adding or removing a random call changes all later draws from that generator. Do not promise bit-for-bit cross-version reproducibility merely because a seed is recorded.

### 3.2 Independent generators per component or partition

Independent instances prevent accidental call-order coupling, but they are not a proof of mathematical independence. Avoid deriving seeds by naïve concatenation of ambiguous strings; use a stable, documented derivation scheme or store explicit per-component seeds.

```python
from random import Random


def make_generators(master_seed: int):
    # Explicitly distinct child seeds; record these with the run metadata.
    return {
        "split": Random(master_seed + 101),
        "augmentation": Random(master_seed + 202),
        "simulation": Random(master_seed + 303),
    }

rngs = make_generators(9001)
train_rows = rngs["split"].sample(range(1000), k=800)
noise = [rngs["augmentation"].uniform(-0.01, 0.01) for _ in range(5)]
```

For distributed or parallel simulations, avoid assuming that a simple seed offset always yields statistically independent streams. Use a library with an explicit parallel-stream strategy when the scale or rigor requires it; NumPy's random infrastructure is a better fit for many large numerical workloads. Its suitability comes from array integration and documented bit-generator/stream-management options, not a blanket guarantee that every NumPy generator is 'higher quality' than every alternative.

### 3.3 Reproducible splits and partition sampling

For a fixed, versioned dataset, a seeded `sample` can generate a reproducible selection. For production data pipelines, define whether sampling is over rows, unique entities, time windows, or partitions. If row order can change, the same seed can select different records even if the underlying set is unchanged. A stable entity-key sort before sampling can help, but sorting itself must use a deterministic key and tie-breaking rule.

```python
from random import Random


def split_indices(row_count: int, *, seed: int, test_size: int):
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (row_count, test_size)):
        raise TypeError("row_count and test_size must be integers")
    if row_count < 0 or not 0 <= test_size <= row_count:
        raise ValueError("invalid row_count or test_size")
    rng = Random(seed)
    test_indices = set(rng.sample(range(row_count), test_size))
    train = [i for i in range(row_count) if i not in test_indices]
    test = sorted(test_indices)
    return train, test
```

This is an index split, not a statistically stratified split and not a guarantee against leakage. If related records belong to the same customer, device, patient, or time interval, split by the correct group/time boundary instead of randomly splitting rows.

## 4. Beginner descriptive statistics

The `statistics` module is suitable for common descriptive statistics on ordinary Python numeric data. Decide whether an input is a population or a sample, validate missing values, and report sample size alongside the statistic.

| Function | Meaning | Empty / insufficient data behavior to plan for |
|---|---|---|
| `mean(data)` | Arithmetic average | Empty input raises `StatisticsError` |
| `median(data)` | Middle value or average of two middle values | Empty input raises `StatisticsError` |
| `mode(data)` | Single most common value; ties follow documented behavior | Empty input raises `StatisticsError` |
| `multimode(data)` | All values tied for highest frequency | Empty input returns `[]` |
| `variance(data)` | Sample variance, denominator `n - 1` | Requires at least two data points |
| `stdev(data)` | Sample standard deviation, square root of sample variance | Requires at least two data points |
| `pvariance(data)` | Population variance, denominator `n` | Requires at least one data point |
| `pstdev(data)` | Population standard deviation | Requires at least one data point |
| `quantiles(data, n=4)` | Cut points dividing ordered data into `n` intervals | Needs enough observations for the selected method; empty/small inputs can raise |

`mode` returns the first encountered mode when values tie in current Python (this behavior changed in Python 3.8); `multimode` is often clearer when ties are meaningful. Do not silently replace missing data with zero unless zero is the correct domain value. Reject, filter, or impute missing observations under an explicit documented policy.

```python
from statistics import mean, median, multimode, quantiles, stdev

latencies_ms = [18.0, 20.0, 21.0, 22.0, 90.0]
report = {
    "n": len(latencies_ms),
    "mean_ms": mean(latencies_ms),
    "median_ms": median(latencies_ms),
    "modes_ms": multimode(latencies_ms),
    "sample_stdev_ms": stdev(latencies_ms),
    "quartile_cut_points_ms": quantiles(latencies_ms, n=4),
}
```

The large 90 ms value pulls the mean upward, while the median is more robust to this single high observation. Neither summary explains why the outlier occurred. In latency reporting, percentiles and distribution shape often matter more than an average alone.

### Population versus sample

- A **population** is the entire set you want to describe. If you have every event in the reporting window and the target is exactly that window, population measures may be appropriate.
- A **sample** is used to estimate or describe a larger population. Sample variance and sample standard deviation use `n - 1` (Bessel's correction) under the usual sample-variance definition.

Use `pstdev` when describing the full population in hand; use `stdev` for a sample when the sample statistic is intended. Do not select based only on which number looks better.

### A robust reporting wrapper

```python
from math import isfinite
from statistics import StatisticsError, fmean, median, pstdev, stdev


def descriptive_report(values):
    """Summarize finite numeric values; reject empty input explicitly."""
    data = list(values)
    if not data:
        raise ValueError("at least one observation is required")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in data):
        raise TypeError("observations must be int or float, not bool or other types")
    if any(isinstance(x, float) and not isfinite(x) for x in data):
        raise ValueError("float observations must be finite; handle NaN/inf explicitly")
    try:
        average = fmean(data)
    except OverflowError as exc:
        raise ValueError("values exceed the floating-point range supported by this report") from exc
    result = {"n": len(data), "mean": average, "median": median(data),
              "population_stdev": pstdev(data)}
    if len(data) >= 2:
        result["sample_stdev"] = stdev(data)
    else:
        result["sample_stdev"] = None  # Not defined for n < 2.
    return result
```

This wrapper deliberately materializes the iterable, so it uses O(n) memory. It rejects booleans despite `bool` being a subclass of `int`, and checks finiteness only for floats so extremely large integers are not needlessly converted to float. For a large stream, use an online algorithm appropriate to the desired statistic rather than blindly calling `list()`.

## 5. Intermediate statistics APIs

### 5.1 `fmean`, geometric and harmonic means

- `statistics.fmean(data)` computes a floating-point arithmetic mean; it is available from Python 3.8.
- `statistics.geometric_mean(data)` computes a geometric mean; available from Python 3.8. It rejects negative inputs; a zero input yields `0.0`, and empty input raises `StatisticsError`. For a strictly positive multiplicative-growth interpretation, validate that every value is greater than zero before calling it.
- `statistics.harmonic_mean(data)` is useful for rates and ratios when observations are expressed on a compatible basis. Negative values are rejected; a zero causes a result of zero, and the implementation may return at the first zero without validating later values. If input validation matters, validate the entire collection yourself before calling it.

Use geometric means for multiplicative growth factors and harmonic means for certain rate averages (for example, equal-distance speeds). Do not swap them with arithmetic mean without understanding the data-generating process.

### 5.2 Covariance, correlation, and linear regression

`statistics.covariance(x, y)`, `correlation(x, y)`, and `linear_regression(x, y)` were added in Python 3.10. They require paired data with equal lengths and enough variation/observations for the requested calculation. Correlation describes linear association, not causation. A correlation near zero does not rule out nonlinear relationships, and outliers can strongly influence both correlation and least-squares regression.

```python
from statistics import correlation, covariance, linear_regression

hours = [1, 2, 3, 4, 5]
output = [3, 4, 4, 7, 8]
print(correlation(hours, output))
print(covariance(hours, output))
fit = linear_regression(hours, output)
print(fit.slope, fit.intercept)
```

The exact floating-point output should be generated in the current runtime rather than copied from a different Python implementation. In a report, state units, sample size, exclusions, and whether the relationship is observational.

### 5.3 `NormalDist`

`statistics.NormalDist` (Python 3.8+) represents a normal distribution using mean `mu` and standard deviation `sigma`. Its `cdf(x)` returns the cumulative probability up to `x`; `inv_cdf(p)` returns the quantile for probability `p`; it also supports comparisons/overlap between normal distributions.

```python
from statistics import NormalDist

standard_normal = NormalDist(mu=0, sigma=1)
p_below_1_96 = standard_normal.cdf(1.96)
q_95 = standard_normal.inv_cdf(0.95)
overlap = standard_normal.overlap(NormalDist(mu=1, sigma=1))
```

This is useful for quick distribution calculations when the normal model is justified. `overlap(other)` returns the overlap area between two normal probability density functions, on a 0-to-1 scale. For example, `NormalDist(0, 1).overlap(NormalDist(1, 1))` quantifies overlap between two equal-spread distributions with shifted means. It does not test whether your data are normal, does not automatically account for parameter-estimation uncertainty, and does not turn a descriptive calculation into a full inferential analysis.

### 5.4 Floating-point and exactness

Binary floating-point cannot represent many decimal fractions exactly. Rounding may accumulate in numerical workflows, and extreme values can overflow or lose precision. Some `statistics` functions can preserve exact arithmetic for rational inputs (such as `Fraction`) where supported, but it is incorrect to claim that the entire module always uses exact fractions internally. `fmean` is explicitly floating-point-oriented. For money, use `Decimal` or integer minor units according to domain requirements; for large vectorized numerical workloads, use NumPy and understand its dtype/precision rules.

## 6. Streaming sampling: reservoir sampling (Algorithm R)

### Problem

You need a uniform sample of `k` items from a stream whose total length is unknown or too large to materialize. `sample()` normally needs access to a population; reservoir sampling retains only `k` items and processes the stream once.

### Algorithm R

1. Fill a reservoir with the first `k` stream items.
2. For the item at zero-based stream index `i >= k`, draw a uniform integer `j` from `0` through `i` inclusive.
3. If `j < k`, replace reservoir slot `j` with the new item; otherwise discard it.

**Pseudocode:** Fill the reservoir with the first `k` items. For each later item at zero-based index `i`, draw `j = rng.randrange(i + 1)`. Replace reservoir slot `j` only when `j < k`. Count every stream item, including items discarded from the reservoir.

Here is the complete, runnable version used in tests:

```python
from random import Random
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def reservoir_sample(stream: Iterable[T], k: int, *, rng: Random) -> list[T]:
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer")
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []  # Do not consume a potentially expensive one-pass stream.
    reservoir: list[T] = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = rng.randrange(i + 1)
            if j < k:
                reservoir[j] = item
    if len(reservoir) < k:
        raise ValueError("k cannot exceed the stream length")
    return reservoir
```

**Complexity:** O(n) stream processing and O(k) retained sample memory. The sample is uniform under the assumption that `randrange` gives the intended uniform integer draws and the algorithm is implemented as shown. The proof intuition is that when item `i` arrives, it is selected with probability `k/(i+1)`; each previously retained item has probability `1 - 1/(i+1)` of surviving that step, yielding equal final inclusion probability `k/n` for every stream position. This is a mathematical argument, not something established by a unit test.

For `k = 0`, the result is `[]`; if the stream has fewer than `k` elements, this implementation raises `ValueError`. A stream may be consumed only once, and a one-pass stream cannot be restarted for another sample unless it is replayable or buffered.

## 7. Stratified sampling

Stratified sampling divides a population into meaningful groups (strata) and samples within each group. It can ensure that small but important segments appear in a sample. It does not automatically produce an unbiased estimate for the whole population: if allocation is disproportionate, aggregate estimates may require weights that reflect each stratum's population share.

```python
from random import Random


def stratified_sample(groups, allocation, *, seed):
    """Sample each named stratum without replacement.

    groups: mapping of stratum -> sequence of records
    allocation: mapping of stratum -> sample count
    """
    rng = Random(seed)
    result = {}
    if set(groups) != set(allocation):
        raise ValueError("groups and allocation must have identical keys")
    for name, records in groups.items():
        count = allocation[name]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("allocations must be non-negative integers")
        if count > len(records):
            raise ValueError(f"sample exceeds stratum size: {name}")
        result[name] = rng.sample(list(records), count)
    return result
```

This example assumes the input strata and their record ordering are stable. For a production audit or survey, record stratum definitions, sampling fractions, non-response, and weights. If records are grouped by customer or time, decide whether the unit of selection is the record or the group.

## 8. Monte Carlo simulation: estimating π

Monte Carlo methods estimate a quantity by repeated random sampling. To estimate π, sample points uniformly in the square `[0, 1] × [0, 1]` and count points satisfying `x² + y² <= 1`. The quarter-circle area is π/4, so `π_hat = 4 * hits/n`.

The standard error is an estimated standard deviation of the estimator under the Bernoulli model, not a guaranteed bound on the error in one run. It is zero if all trials agree, which does not mean the estimate is certainly exact; for small samples, normal-approximation intervals can be poor. Report `n`, seed, estimate, and uncertainty. Monte Carlo error typically decreases on the order of `1/sqrt(n)`, so reducing error by a factor of 10 often requires about 100 times as many trials.

Use this straightforward loop as the reference implementation:

```python
from math import sqrt
from random import Random


def estimate_pi(n: int, *, seed: int) -> dict[str, float | int]:
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n <= 0:
        raise ValueError("n must be positive")
    rng = Random(seed)
    hits = 0
    for _ in range(n):
        x, y = rng.random(), rng.random()
        if x * x + y * y <= 1.0:
            hits += 1
    p_hat = hits / n
    return {
        "n": n,
        "hits": hits,
        "estimate": 4.0 * p_hat,
        "standard_error": 4.0 * sqrt(p_hat * (1.0 - p_hat) / n),
    }
```

The function above is the canonical implementation used by the tests. A reproducible seed makes the run repeatable in a compatible environment, not more accurate by itself. Its reported standard error is a plug-in estimate under the Bernoulli model; a simple normal-approximation interval such as `estimate ± 1.96 * standard_error` can be poor for small `n` or estimates near the bounds. Use an interval method appropriate to the binomial proportion if a defensible interval is required.

## 9. Data interpretation cautions

### Sampling bias

A large sample can still be biased if its inclusion mechanism systematically excludes part of the target population. Examples include sampling only active users, excluding failed jobs, or collecting latency only from successful requests. Random sampling from the wrong frame does not fix the frame.

### Outliers and skew

The mean and standard deviation are sensitive to extreme values; the median and quantiles are often more robust. But an outlier can be a data defect, a rare but real incident, or a meaningful tail event. Investigate before deleting it. For skewed operational metrics, report quantiles and counts rather than only mean ± standard deviation.

### Simpson's paradox

An aggregate trend can reverse within subgroups when group sizes or mix differ. For example, overall error rate can improve because traffic shifts to an easier workload, even while error rates worsen in every workload category. Compare relevant strata and explain weighting; do not infer a causal effect from an aggregate statistic alone.

### Correlation is not causation

A correlation can arise from confounding, selection, time trends, or chance. `statistics.correlation` measures linear association in the supplied paired data. It does not establish causality, statistical significance, or model validity.

## 10. Deterministic test data and property-based testing

Use a local seeded generator to build repeatable fixtures. Keep production secrets out of fixtures, and avoid making tests depend on exact random sequences unless that sequence itself is the API contract.

```python
from random import Random


def make_latency_fixture(seed: int, count: int) -> list[float]:
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer")
    if count < 0:
        raise ValueError("count must be non-negative")
    rng = Random(seed)
    return [max(0.0, rng.gauss(40.0, 8.0)) for _ in range(count)]

assert make_latency_fixture(5, 10) == make_latency_fixture(5, 10)
```

Property-based testing (for example, with Hypothesis, introduced in later roadmap work) can generate many inputs and shrink failures. It complements, but does not replace, deterministic unit tests. For random algorithms, test structural invariants and edge cases; use statistical goodness-of-fit tests only when designed with appropriate significance levels and enough repetitions.

## 11. When to move to NumPy

Use the standard library for simple scalar statistics, modest samples, basic random selection, deterministic fixtures, and readable simulations. Consider NumPy's `numpy.random.Generator` and `default_rng()` when you need:

- vectorized array generation and numerical calculations;
- large simulations where Python-level loops are a bottleneck;
- distributions and numerical operations integrated with array dtypes;
- documented strategies for spawning independent streams in parallel workloads.

NumPy is not automatically “more correct” for every task. Choose and record the bit generator, seed/SeedSequence strategy, NumPy version, and array dtype if reproducibility matters. Do not use either Python's `random` or NumPy's ordinary PRNG as a replacement for cryptographic randomness. Use `secrets` or a vetted cryptographic API for secrets.

## 12. Common mistakes

- Using module-global randomness in a reusable library and unexpectedly changing a caller's state.
- Assuming the same seed guarantees the same results forever across Python versions, algorithms, call sequences, or input ordering.
- Using `sample` when duplicates are meaningful, or `choices` when uniqueness is required.
- Passing a negative `k`, requesting a sample larger than the population, or ignoring empty input errors.
- Treating `stdev` as population standard deviation or reporting it for one observation.
- Assuming a normal distribution because `gauss` was used to generate synthetic data.
- Treating correlation as causation or interpreting a short-run frequency as proof of uniformity.
- Materializing an unbounded stream to call `sample`, instead of using a stream algorithm.
- Using `random` for passwords, tokens, reset links, or security challenges.
- Forgetting that a seeded split over unstable row order is not stable at the entity level.
- Ignoring group leakage, time leakage, sampling-frame bias, or disproportionate strata.

## 13. Tests

The following tests target invariants and deterministic behavior. Save the tested functions in `random_stats_lesson.py` or place the implementations in a project module, then save the tests as `test_random_stats_lesson.py`. They are examples of unit tests, not a mathematical proof of randomness or a certification of a statistical model.

```python
# test_random_stats_lesson.py
from random import Random
from statistics import (StatisticsError, quantiles, variance, pvariance, stdev, pstdev, mean, multimode)
import sys
import pytest

from random_stats_lesson import (
    choose_partition,
    descriptive_report,
    estimate_pi,
    make_generators,
    make_latency_fixture,
    reservoir_sample,
    split_indices,
    stratified_sample,
)


def test_sample_size_and_reproducibility():
    rows = list(range(100))
    assert choose_partition(rows, seed=12, size=10) == choose_partition(rows, seed=12, size=10)
    assert len(choose_partition(rows, seed=12, size=10)) == 10
    assert len(set(choose_partition(rows, seed=12, size=10))) == 10


def test_choose_partition_boundaries():
    assert choose_partition([1, 2], seed=1, size=0) == []
    assert sorted(choose_partition([1, 2], seed=1, size=2)) == [1, 2]
    with pytest.raises(ValueError):
        choose_partition([1], seed=1, size=2)
    with pytest.raises(ValueError):
        choose_partition([1], seed=1, size=-1)
    with pytest.raises(TypeError):
        choose_partition([1], seed=1, size=True)


def test_independent_generators_are_reproducible_and_separate():
    first = make_generators(100)
    second = make_generators(100)
    assert first["split"].random() == second["split"].random()
    # Advancing one component does not advance another component's state.
    first["split"].random()
    assert first["simulation"].random() == second["simulation"].random()


def test_descriptive_report_handles_one_and_rejects_bad_values():
    assert descriptive_report([5]) == {
        "n": 1, "mean": 5.0, "median": 5, "population_stdev": 0.0,
        "sample_stdev": None,
    }
    with pytest.raises(ValueError):
        descriptive_report([])
    with pytest.raises(ValueError):
        descriptive_report([1, float("nan")])
    with pytest.raises(TypeError):
        descriptive_report([True])
    with pytest.raises(ValueError):
        descriptive_report([10**1000])


def test_reservoir_sample_invariants_and_reproducibility():
    population = range(1000)
    first = reservoir_sample(population, 20, rng=Random(7))
    second = reservoir_sample(range(1000), 20, rng=Random(7))
    assert first == second
    assert len(first) == 20
    assert len(set(first)) == 20
    assert all(0 <= x < 1000 for x in first)


def test_reservoir_boundaries():
    untouched = iter([1, 2])
    assert reservoir_sample(untouched, 0, rng=Random(1)) == []
    assert next(untouched) == 1  # k=0 returns without consuming the stream
    assert reservoir_sample(iter([1, 2]), 2, rng=Random(1)) == [1, 2]
    with pytest.raises(ValueError):
        reservoir_sample(iter([1]), 2, rng=Random(1))
    with pytest.raises(ValueError):
        reservoir_sample(iter([1]), -1, rng=Random(1))
    with pytest.raises(TypeError):
        reservoir_sample(iter([1]), True, rng=Random(1))


def test_stratified_sample_validates_allocations():
    groups = {"small": [1, 2], "large": [3, 4, 5]}
    a = stratified_sample(groups, {"small": 1, "large": 2}, seed=8)
    b = stratified_sample(groups, {"small": 1, "large": 2}, seed=8)
    assert a == b
    assert len(a["small"]) == 1 and len(a["large"]) == 2
    with pytest.raises(ValueError):
        stratified_sample(groups, {"small": 3, "large": 1}, seed=8)


def test_monte_carlo_configuration_and_reproducibility():
    a = estimate_pi(20_000, seed=99)
    b = estimate_pi(20_000, seed=99)
    assert a == b
    assert a["n"] == 20_000
    assert 0 <= a["hits"] <= a["n"]
    assert 0 <= a["estimate"] <= 4
    assert a["standard_error"] >= 0
    with pytest.raises(ValueError):
        estimate_pi(0, seed=99)
    with pytest.raises(TypeError):
        estimate_pi(True, seed=99)



def test_population_and_sample_statistics_formulas():
    values = [1, 2, 3]
    assert mean(values) == 2
    assert variance(values) == 1  # sum((x - mean)**2) / (n - 1)
    assert pvariance(values) == pytest.approx(2 / 3)  # denominator n
    assert stdev(values) == 1
    assert pstdev(values) == pytest.approx((2 / 3) ** 0.5)
    assert multimode([]) == []


def test_random_api_boundaries_and_replacement_semantics():
    rng = Random(123)
    assert rng.randint(5, 5) == 5
    assert rng.sample(["same", "same"], k=2) == ["same", "same"]
    assert rng.choices(["never", "always"], weights=[0, 1], k=10) == ["always"] * 10
    values = [1, 2, 3]
    assert rng.shuffle(values) is None
    assert sorted(values) == [1, 2, 3]
    with pytest.raises(IndexError):
        rng.choice([])
    with pytest.raises(ValueError):
        rng.sample([1], k=2)
    with pytest.raises(ValueError):
        rng.choices([1, 2], weights=[0, 0], k=1)


def test_quantiles_single_observation_version_behavior():
    if sys.version_info >= (3, 13):
        assert quantiles([1]) == [1, 1, 1]
    else:
        with pytest.raises(StatisticsError):
            quantiles([1])


def test_fixture_reproducibility_and_split_invariants():
    assert make_latency_fixture(5, 20) == make_latency_fixture(5, 20)
    train, test = split_indices(100, seed=3, test_size=20)
    assert len(test) == 20 and len(train) == 80
    assert set(train).isdisjoint(test)
    assert sorted(train + test) == list(range(100))
    with pytest.raises(TypeError):
        split_indices(True, seed=3, test_size=1)
```

### What these tests do and do not establish

They establish that the tested implementation meets specific deterministic invariants in the tested runtime: expected sample size, uniqueness where required, reproducibility for the same local seed and call sequence, boundary handling, and disjoint splits. They do **not** prove that every item has exactly equal probability under all conditions. Uniformity is supported by the algorithm and the generator's documented behavior; empirical frequency tests are diagnostics that can fail by chance and should not be mistaken for proof.

## 14. Mini-project: reproducible batch audit sampler

Build a command-line script that:

1. Accepts a stable input batch (or iterator), a master seed, and a requested sample size.
2. Records the Python version, seed, input version/hash, sample method, and code revision alongside the result.
3. Uses `Random(seed)` for a materialized batch or Algorithm R for a one-pass stream.
4. Emits sample IDs rather than copying sensitive records into a log.
5. Reports `n`, mean, median, sample standard deviation when defined, and selected quantiles for a numeric measure.
6. Rejects invalid sizes and missing/non-finite measurements according to an explicit policy.
7. Tests repeated runs, changed input order, empty inputs, insufficient stream length, and split leakage at the entity/group level.

**Design trade-offs:** A seed and a versioned input provide reproducibility but may not guarantee cross-version byte-for-byte sequence identity. A sample of rows may overrepresent prolific entities. Stratification can improve segment coverage but may require weights for population-level estimates. Keep sensitive records out of diagnostics and retain only the minimum metadata needed for auditability.

## 15. Hands-on exercises

1. Explain why `Random(seed)` is preferable to `random.seed(seed)` inside a library function.
2. Use `choices` to simulate 1,000 categorical events with weights 2:3:5. Compare observed proportions with expected proportions, and explain why they will not match exactly.
3. Implement a reproducible train/test split and prove with assertions that the sets are disjoint and exhaustive.
4. Run Algorithm R on a stream of one million integers with `k=100`. Measure memory use conceptually and explain why it is O(k), not O(n).
5. Compare `mean` and `median` for a heavily skewed latency sample. Explain what each communicates and what neither explains.
6. Estimate π at two sample sizes. Compare absolute error and estimated standard error; do not claim the larger sample must be closer in every run.
7. Describe a Simpson's paradox scenario in an operational metric and identify the subgroup variables that should be inspected.
8. Decide whether `random`, `secrets`, or NumPy's `Generator` is appropriate for: a password-reset token, a deterministic unit-test fixture, and a vectorized Monte Carlo simulation.

## 16. Self-check answers with explanations

1. **Why local RNGs?** They isolate state and prevent unrelated code from changing the sequence. This improves testability and composability; it does not by itself guarantee cross-version reproducibility or parallel-stream independence.
2. **Why do weighted observed counts differ from target proportions?** Random samples fluctuate. The weights define probabilities, not quotas. Larger sample sizes usually reduce relative sampling variation, but individual runs can still deviate.
3. **Which function is sample standard deviation?** `statistics.stdev`; `statistics.pstdev` is population standard deviation. The choice depends on the target being described, not on preference.
4. **Why use reservoir sampling?** It processes a one-pass stream in O(n) time and O(k) sample memory. Its uniformity depends on the algorithm being implemented correctly and uniform integer draws; a test does not constitute a proof.
5. **Why is a seed not a full experiment record?** Input order/data version, Python/library version, algorithm, configuration, and number/order of RNG calls can all affect output.
6. **Why not use `random` for a token?** Mersenne Twister is not designed to resist prediction by an adversary. Use `secrets` or an appropriate cryptographic API.
7. **Does correlation show causation?** No. It summarizes linear association in observed pairs and is vulnerable to confounding, selection effects, time trends, and outliers.
8. **When should you use NumPy?** For vectorized arrays, high-throughput simulation, and numerical workflows requiring its richer generator ecosystem. The standard library remains effective for simple scalar work and small scripts.

## 17. Final reference checklist

| Need | Recommended API / method | Important caveat |
|---|---|---|
| Repeatable scalar draws | `random.Random(seed)` | Record environment and call sequence when exact reproducibility matters |
| One random element | `rng.choice(seq)` | Sequence must be non-empty |
| Repeated weighted draws | `rng.choices(population, weights=..., k=...)` | With replacement; weights are relative |
| Unique fixed-size sample | `rng.sample(population, k)` | `k` must not exceed population size |
| Shuffle a list | `rng.shuffle(list_)` | Mutates in place; returns `None` |
| Stream sample | Reservoir Algorithm R | O(k) memory; one pass; verify edge cases |
| Arithmetic average | `statistics.mean` / `fmean` | `fmean` returns float; empty data need a policy |
| Robust middle summary | `statistics.median` | Does not describe tails alone |
| Most common value(s) | `mode` / `multimode` | Know tie and empty-input behavior |
| Sample spread | `stdev` / `variance` | Requires at least two observations |
| Population spread | `pstdev` / `pvariance` | Requires at least one observation |
| Quantile cut points | `quantiles` | Choose method and document small-sample limits |
| Normal-model calculation | `statistics.NormalDist` | Assumes a normal model; not a normality test |
| Paired linear association | `correlation`, `covariance`, `linear_regression` | Python 3.10+; no causal claim |
| Secure token | `secrets` | Not `random`; lifecycle controls still matter |
| Vectorized numerical work | NumPy `Generator` / `default_rng` | Record generator, seed strategy, version, and dtype |

## 18. Version and API notes

- The lesson targets Python 3.12+ as required by the Module 13 roadmap.
- `statistics.NormalDist`, `fmean`, `geometric_mean`, and `quantiles` were introduced in Python 3.8. `quantiles()` changed in Python 3.13 to accept a single data point; Python 3.12 and earlier raise `StatisticsError` for one observation.
- `statistics.correlation`, `covariance`, and `linear_regression` were introduced in Python 3.10.
- Since Python 3.11, `random.sample` requires a sequence and no longer automatically converts sets; use a stable sequence if sampling from a set-derived collection.
- The `random` documentation guarantees that `random()` continues to produce the same sequence when the compatible seeder is used with the same seed; most other algorithms and seeding details can change across versions. Higher-level calls such as `sample()`, `choices()`, or `gauss()` should not be assumed to preserve an identical full sequence across Python versions. Consult the documentation for the exact guarantee relevant to your use case.

## References

- Python documentation, [`random`](https://docs.python.org/3/library/random.html)
- Python documentation, [`statistics` (current)](https://docs.python.org/3/library/statistics.html)
- Python 3.12 [`statistics`](https://docs.python.org/3.12/library/statistics.html) and Python 3.13 [`statistics`](https://docs.python.org/3.13/library/statistics.html) for version-sensitive `quantiles()` behavior
- Python documentation, [`random` reproducibility and generator notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility)
- Python documentation, [`secrets`](https://docs.python.org/3/library/secrets.html)
- NumPy documentation, [Random sampling](https://numpy.org/doc/stable/reference/random/index.html)
- Python documentation, [Typing](https://docs.python.org/3/library/typing.html)
