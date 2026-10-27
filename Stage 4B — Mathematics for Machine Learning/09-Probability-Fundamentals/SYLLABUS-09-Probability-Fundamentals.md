# SYLLABUS — 09-Probability-Fundamentals (S4B-09)

**Stage 4B — Mathematics for Machine Learning · Module 09 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (SymPy, Matplotlib, pytest where stated; scikit-learn is optional and only for cross-checks). All example datasets are **synthetic and generated in code**; numbers shown as illustrations are labelled as such. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Sample spaces, events, and the probability axioms | `01-sample-spaces-events-and-probability-axioms.md` | Beginner |
| 3 | Conditional probability and the multiplication rule | `02-conditional-probability-and-the-multiplication-rule.md` | Beginner → Intermediate |
| 4 | Law of total probability and Bayes' theorem | `03-law-of-total-probability-and-bayes-theorem.md` | Intermediate |
| 5 | Independence | `04-independence.md` | Intermediate |
| 6 | Random variables: discrete and continuous | `05-random-variables-discrete-and-continuous.md` | Intermediate |
| 7 | PMF, PDF, and CDF | `06-pmf-pdf-and-cdf.md` | Intermediate |
| 8 | Expectation and variance | `07-expectation-and-variance.md` | Intermediate → Advanced |
| 9 | Covariance and correlation | `08-covariance-and-correlation.md` | Intermediate → Advanced |
| 10 | Practice question bank | `practice-questions.md` | All levels |
| 11 | Project index | `Projects/README.md` | Intermediate |
| 12 | Project: probability simulations | `Projects/01-probability-simulations.md` | Intermediate → Advanced |
| 13 | Project: Bayes spam filter by hand | `Projects/02-bayes-spam-filter-by-hand.md` | Advanced |

**Prerequisites:** Stage 4A Module 11 (counting and combinatorics) and Module 12 (descriptive statistics); Module 06 of this stage (integrals, CDF as a running integral, normalization, improper integrals); Module 01–03 (dot products, covariance matrices as symmetric PSD, eigenvalues); Module 08 (the `σ²/B` variance law is reused here). **Plan slot:** weeks 10–11 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** this module is required on every track, since Modules 10–13 and every evaluation in Stage 5 assume it.

**Teaching stance (industry, not university):** probability is taught as the language for *uncertain quantities in ML systems*: predictions, labels, errors, noise, samples. Every formula is checked by exact enumeration **and** by simulation, and every lesson names the ML situation in which the formula is the thing that goes wrong.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (exact, simulated, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

A classifier outputs `P(y | x)`. A language model is a product of conditional probabilities. An A/B test asks whether a difference could be chance. Training is maximum likelihood. Evaluation reports expectations and confidence intervals. All of it sits on the handful of rules in this module: the axioms, conditioning, Bayes' rule, independence, random variables, expectation, variance, and covariance. The most expensive production mistakes in this area are not exotic: base-rate neglect, assuming independence that is not there, confusing `P(A|B)` with `P(B|A)`, and averaging the wrong thing.

### 1.2 Outcomes

1. Build a sample space and compute event probabilities exactly (with `fractions`) and by simulation, and check that they agree within sampling error.
2. Apply the axioms and their consequences (complement, inclusion–exclusion, union bound).
3. Compute and interpret conditional probabilities, use the multiplication/chain rule, and avoid the `P(A|B) ≠ P(B|A)` fallacy.
4. Apply the law of total probability and Bayes' theorem, including to class-prior shift and spam filtering, and explain base-rate neglect.
5. Define independence, mutual vs pairwise independence, and conditional independence, and test claims numerically.
6. Distinguish discrete and continuous random variables and use PMF, PDF, and CDF correctly (including `pdf > 1`).
7. Compute expectation and variance, use linearity and `Var(X+Y)`, and avoid numerically unstable formulas.
8. Compute covariance and correlation, interpret their limits (linear only), and relate them to covariance matrices and PCA.
9. Build and statistically validate a simulation suite and a Naive Bayes spam filter from scratch.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Sample spaces, events, axioms | Prediction events, error rates | Enumerate vs simulate |
| 2 | Conditional probability, chain rule | `p(y|x)`, language-model factorization | Conditional tables; bigram sentence probability |
| 3 | Total probability and Bayes | Posterior, prevalence, prior shift, spam | Base-rate and prior-shift experiments |
| 4 | Independence | i.i.d. assumption, naive Bayes, leakage | XOR, collider, effective sample size |
| 5 | Random variables | Features, labels, losses as RVs | PMF by enumeration; transformations |
| 6 | PMF, PDF, CDF | Densities, CDFs, quantiles, sampling | Normalization checks; inverse transform |
| 7 | Expectation, variance | Risk, mean/variance of metrics, SGD noise | LOTUS, linearity, stable variance |
| 8 | Covariance, correlation | Feature redundancy, PCA, whitening | `np.cov` pitfalls, whitening, rank |

### 1.4 Concept map

```
sample space Ω, events, axioms ──► P(A) ──► conditioning P(A|B) ──► chain rule ──► Bayes: posterior ∝ likelihood × prior
                                              │                                   └─► naive Bayes (conditional independence)
                                              └─► independence: P(A∩B)=P(A)P(B); conditional independence; pairwise ≠ mutual
random variable X: Ω → ℝ ──► PMF / PDF / CDF (Module 06: integral, normalization) ──► quantiles, inverse-transform sampling
                         └─► E[X], Var(X) (linearity; Var(X+Y) needs Cov) ──► Cov, ρ (linear only), covariance matrix Σ (PSD) ──► PCA, whitening
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "sympy>=1.12" matplotlib pytest      # scikit-learn optional
```

Rules for every lab: **compute each probability two ways** (exact enumeration or formula, and simulation) and assert agreement within a stated number of standard errors; report **`± standard error`** for every simulated probability (`√(p(1−p)/N)`); seed all randomness (`np.random.default_rng(seed)`); use `fractions.Fraction` for exact small-case arithmetic; never compare floats with `==`.

### 1.6 Checkpoints

- Simulated and exact probabilities agree within `4·SE` for every worked example in the lessons.
- You can compute the posterior for a diagnostic test by hand, by natural frequencies, and by simulation, and the three agree.
- Your Naive Bayes posteriors sum to 1, match a hand calculation on a 3-word example, and do not underflow on a 1,000-word message.

### Check yourself (Unit 1)

1. Name three ML quantities that are conditional probabilities.
2. Why does every lab in this module report a standard error?

**Reference answers:** (1) `P(y|x)` from a classifier, `P(wordₜ | previous words)` in a language model, precision `P(y=1 | ŷ=1)` and recall `P(ŷ=1 | y=1)`. (2) A simulated probability is a random estimate; without its standard error you cannot tell a real discrepancy from sampling noise.

---

## Unit 2 — Sample spaces, events, and the probability axioms (`01-…md`)

### 2.1 Why ML needs this

Every probabilistic claim is about an **event** in a **sample space**: "the model errs on this input", "at least one of 20 checks fails", "the user clicks". Getting the sample space wrong is the root of most probability mistakes (the classic being "two dice sum to 7 is as likely as sum to 12").

### 2.2 Intuition

The **sample space** `Ω` is the list of everything that could happen. An **event** is a subset of `Ω`. Probability assigns each event a number between 0 and 1 so that nothing is double-counted and the whole space has probability 1.

### 2.3 Mechanics

- **Sample space** `Ω`: the set of all outcomes; outcomes must be mutually exclusive and exhaustive. **Event** `A ⊆ Ω`. Operations: union `A ∪ B` ("or"), intersection `A ∩ B` ("and"), complement `Aᶜ` ("not"). Events are **disjoint** (mutually exclusive) if `A ∩ B = ∅`.
- **Kolmogorov axioms:** (1) `P(A) ≥ 0`; (2) `P(Ω) = 1`; (3) for disjoint events `A₁, A₂, …`: `P(⋃Aᵢ) = ΣP(Aᵢ)`.
- **Consequences:**
  - `P(Aᶜ) = 1 − P(A)`; `P(∅) = 0`; `0 ≤ P(A) ≤ 1`.
  - **Monotonicity:** `A ⊆ B ⇒ P(A) ≤ P(B)`.
  - **Inclusion–exclusion:** `P(A ∪ B) = P(A) + P(B) − P(A ∩ B)`.
  - **Union bound (Boole):** `P(⋃Aᵢ) ≤ ΣP(Aᵢ)`: no independence needed.
- **Equally likely outcomes:** `P(A) = |A|/|Ω|`; counting comes from Stage 4A Module 11. This model is a *modelling assumption*: it is correct for fair dice and wrong for "sum of two dice".
- **Interpretations:** frequency (long-run fraction) and degree of belief; the maths is identical `[JUDGEMENT]`.
- **Monte Carlo estimate:** `P̂(A) = k/N` with standard error `√(P̂(1 − P̂)/N)`; the error shrinks like `1/√N`. A normal-approximation interval `P̂ ± 1.96·SE` is fine for large `N` and `P̂` away from 0/1; the **Wilson interval** is safer near the extremes `[VERIFY: formula]`.
- **Complement trick:** "at least one" is easiest as `1 − P(none)`. Example (birthday problem): `P(match among n people) = 1 − Π_{i=0}^{n−1} (365 − i)/365`; for `n = 23` this is about `0.507`.

**Worked example (exact):** two fair dice, `Ω` has 36 equally likely ordered pairs. `P(sum = 7) = 6/36 = 1/6`; `P(sum = 12) = 1/36`. Sums are *not* equally likely because outcomes of `Ω` (ordered pairs) are, not the sums.

### 2.4 Code

```python
import itertools, math
from fractions import Fraction
import numpy as np

# --- exact: enumerate the sample space of two dice
Omega = list(itertools.product(range(1, 7), repeat=2))                # 36 equally likely outcomes
P = lambda event: Fraction(sum(1 for w in Omega if event(w)), len(Omega))
assert P(lambda w: w[0] + w[1] == 7) == Fraction(1, 6) and P(lambda w: w[0] + w[1] == 12) == Fraction(1, 36)

# axioms and consequences, checked exactly
A = lambda w: w[0] + w[1] >= 10;   B = lambda w: w[0] == 6
assert P(lambda w: True) == 1 and P(lambda w: False) == 0
assert P(lambda w: not A(w)) == 1 - P(A)                                           # complement
assert P(lambda w: A(w) or B(w)) == P(A) + P(B) - P(lambda w: A(w) and B(w))       # inclusion–exclusion
assert P(lambda w: A(w) or B(w)) <= P(A) + P(B)                                    # union bound

# --- simulation with a standard error
rng = np.random.default_rng(0); N = 200_000
d = rng.integers(1, 7, size=(N, 2)); k = int(np.sum(d.sum(axis=1) == 7))
p_hat = k / N; se = math.sqrt(p_hat * (1 - p_hat) / N)
print(f"P(sum=7): exact {1/6:.5f}  simulated {p_hat:.5f} ± {se:.5f}")
assert abs(p_hat - 1 / 6) < 4 * se

# --- birthday problem: exact complement formula vs simulation
def birthday_exact(n): return 1 - math.prod((365 - i) / 365 for i in range(n))
def birthday_sim(n, trials=100_000, seed=1):
    b = np.sort(np.random.default_rng(seed).integers(0, 365, size=(trials, n)), axis=1)
    return float(np.mean(np.any(np.diff(b, axis=1) == 0, axis=1)))
for n in (10, 23, 50):
    ex, sm = birthday_exact(n), birthday_sim(n); se = math.sqrt(ex * (1 - ex) / 100_000)
    print(f"n={n:2d}  exact {ex:.4f}  simulated {sm:.4f}"); assert abs(sm - ex) < 4 * se

# --- a naive 'equally likely sums' model is wrong
naive = Fraction(1, 11)                                                            # 11 possible sums
print("naive P(sum=7) =", float(naive), " true =", float(P(lambda w: w[0] + w[1] == 7)))

# --- union bound is loose but valid: 20 independent 'checks', each failing with probability 0.02
p_each = 0.02; exact_any = 1 - (1 - p_each) ** 20
print("P(at least one failure) =", round(exact_any, 4), " union bound =", 20 * p_each)

# --- Wilson interval (safe near 0 or 1)
def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n; ctr = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - half, ctr + half
print(wilson(0, 200), "(normal approximation would give a zero-width interval at p̂=0)")
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Treating non-equally-likely outcomes as equally likely (sum of two dice) | Wrong probabilities | Enumerate the *fundamental* outcomes first |
| Double-counting in `P(A ∪ B)` | Probabilities above 1 | Inclusion–exclusion; subtract the overlap |
| Equating *disjoint* with *independent* | Wrong multiplication | Disjoint events with positive probability are **dependent** (Lesson 4) |
| Adding probabilities of non-disjoint events | `Σ P > 1` or over-estimate | Use the union bound only as a bound |
| Probabilities that do not sum to 1 (e.g., un-normalized scores) | Invalid distribution | Normalize (softmax); assert `sum == 1` |
| Reporting a simulated probability without a standard error | Noise taken as signal | `± √(p̂(1−p̂)/N)` always |
| Normal interval at `p̂ ∈ {0, 1}` | Zero-width interval | Wilson interval or exact (Clopper–Pearson) `[VERIFY]` |
| Using unseeded randomness | Irreproducible results | Seed every generator |

### 2.6 ML link

- **Classifier outputs** are probabilities of events (`y = 1`); their validity depends on the axioms (normalization, non-negativity), and un-normalized scores are not probabilities (Stage 5B-04 calibration).
- **Multiple checks/tests:** the union bound is the simplest multiple-comparison control (Bonferroni, Module 12).
- **Error rate as an event probability:** accuracy `= P(ŷ = y)`; its estimate from `N` test items has the standard error above (Module 12, Stage 5A-06).
- **Monte Carlo** as the universal estimator of event probabilities (Module 11).

### 2.7 Lab (60 min)

1. Enumerate three experiments (two dice, three coins, drawing two cards without replacement); verify the axioms and inclusion–exclusion exactly.
2. Estimate five probabilities by simulation with `± SE` and assert agreement with the exact values within `4·SE`.
3. Reproduce the birthday curve for `n = 1…60`; find the smallest `n` with probability above `0.5` and `0.99`.
4. Show the union bound's looseness as the events become positively correlated vs independent.
5. Compare the normal and Wilson intervals' empirical coverage at `p = 0.02`, `N = 100` over 5,000 repetitions.

### Check yourself (Unit 2)

1. What is `P(at least one 6 in 3 rolls of a fair die)`?
2. State inclusion–exclusion for two events.
3. Why is the union bound useful without independence?

**Reference answers:** (1) `1 − (5/6)³ = 91/216 ≈ 0.421`. (2) `P(A ∪ B) = P(A) + P(B) − P(A ∩ B)`. (3) It only needs the axioms, so it holds for any events, however dependent.

---

## Unit 3 — Conditional probability and the multiplication rule (`02-…md`)

### 3.1 Why ML needs this

`p(y | x)` is the object a classifier estimates. A language model factorizes a sentence probability into a chain of conditionals. Precision and recall are two *different* conditional probabilities of the same confusion matrix. Misreading which event is being conditioned on is the most common probabilistic error in reports.

### 3.2 Intuition

Conditioning on `B` means: *restrict attention to the worlds where `B` happened and re-normalize.* Out of those worlds, what fraction also have `A`?

### 3.3 Mechanics

- **Definition:** `P(A | B) = P(A ∩ B)/P(B)`, defined only when `P(B) > 0`.
- **Multiplication rule:** `P(A ∩ B) = P(A | B) P(B) = P(B | A) P(A)`.
- **Chain rule:** `P(A₁ ∩ … ∩ Aₙ) = P(A₁) P(A₂|A₁) P(A₃|A₁∩A₂) ⋯ P(Aₙ|A₁∩…∩Aₙ₋₁)`. For random variables: `p(x₁, …, xₙ) = Πᵢ p(xᵢ | x₁, …, xᵢ₋₁)`.
- **`P(· | B)` is itself a probability measure** (obeys the axioms): `P(Aᶜ | B) = 1 − P(A | B)`.
- **Direction matters:** `P(A|B) ≠ P(B|A)` in general (Lesson 3 gives the relationship). *Prosecutor's fallacy:* `P(evidence | innocent)` small does not mean `P(innocent | evidence)` small.
- **Conditioning changes the sample space,** so conditional probabilities can differ from marginals wildly. **Simpson's paradox:** a comparison can reverse when groups are pooled, because the group sizes differ across arms (the *confounder*).
- **Confusion-matrix conditionals** (`ŷ` prediction, `y` truth):

| Metric | Conditional probability |
|---|---|
| Recall / sensitivity / TPR | `P(ŷ=1 | y=1)` |
| Specificity / TNR | `P(ŷ=0 | y=0)` |
| Precision / PPV | `P(y=1 | ŷ=1)` |
| False-positive rate | `P(ŷ=1 | y=0)` |

- **Language-model factorization:** `p(w₁…wₙ) = Π p(wᵢ | w₁…wᵢ₋₁)`; a bigram model truncates the context to one word. Compute in **log space** (sum of logs) to avoid underflow.
- **Conditioning on a probability-zero event** is undefined for discrete events; for continuous variables it needs densities (4C-04).
- **Empirical conditional probability:** `k(A ∩ B)/k(B)` from data; its precision depends on the count of `B`, not `N`.

**Worked example:** two cards drawn without replacement: `P(2nd is ace | 1st is ace) = 3/51`; `P(both aces) = (4/52)(3/51) = 1/221`. **Worked example (Simpson, synthetic numbers):** treatment A: mild `90/100`, severe `3/10` (overall `93/110 ≈ 0.845`); treatment B: mild `19/20`, severe `28/80` (overall `47/100 = 0.47`). B beats A in *both* groups yet loses overall because A was given mostly mild cases.

### 3.4 Code

```python
import itertools
from collections import Counter
from fractions import Fraction
import math
import numpy as np

# --- conditioning as restriction + renormalization (two dice)
Omega = list(itertools.product(range(1, 7), repeat=2))
def P(ev, given=lambda w: True):
    space = [w for w in Omega if given(w)]
    return Fraction(sum(1 for w in space if ev(w)), len(space))
a, b = (lambda w: w[0] + w[1] == 8), (lambda w: w[0] == 3)
assert P(a, b) == Fraction(1, 6) and P(lambda w: a(w) and b(w)) == P(a, b) * P(b)          # multiplication rule
assert P(lambda w: not a(w), b) == 1 - P(a, b)                                              # P(·|B) is a probability

# --- cards without replacement: exact chain rule vs rejection-sampling simulation   (card % 13 == 0 → ace)
exact = Fraction(4, 52) * Fraction(3, 51); assert exact == Fraction(1, 221)
rng = np.random.default_rng(0)
draws = np.array([rng.permutation(52)[:2] for _ in range(60_000)])
first_ace = (draws[:, 0] % 13 == 0); second_ace = (draws[:, 1] % 13 == 0)
cond = second_ace[first_ace].mean(); n_cond = first_ace.sum()
print(f"P(2nd ace | 1st ace): exact {3/51:.4f}  simulated {cond:.4f} ± {math.sqrt(cond*(1-cond)/n_cond):.4f}  (based on {n_cond} samples)")
assert abs(cond - 3 / 51) < 4 * math.sqrt(cond * (1 - cond) / n_cond)

# --- precision vs recall: same confusion matrix, different conditionals
TP, FP, FN, TN = 80, 40, 20, 860                                # synthetic counts
recall, precision, specificity, fpr = TP / (TP + FN), TP / (TP + FP), TN / (TN + FP), FP / (FP + TN)
print(f"recall {recall:.3f}  precision {precision:.3f}  specificity {specificity:.3f}  FPR {fpr:.3f}")

# --- Simpson's paradox (synthetic numbers)
groups = {"A": {"mild": (90, 100), "severe": (3, 10)}, "B": {"mild": (19, 20), "severe": (28, 80)}}
for arm, g in groups.items():
    s, n = map(sum, zip(*g.values()))
    print(arm, {k: round(v[0] / v[1], 3) for k, v in g.items()}, "overall", round(s / n, 3))
rate = lambda arm, grp: groups[arm][grp][0] / groups[arm][grp][1]
assert rate("B", "mild") > rate("A", "mild") and rate("B", "severe") > rate("A", "severe")
assert sum(v[0] for v in groups["A"].values()) / 110 > sum(v[0] for v in groups["B"].values()) / 100      # reversal when pooled

# --- chain rule for a bigram language model (toy corpus), in log space
corpus = "the cat sat on the mat . the dog sat on the log .".split()
uni, bi = Counter(corpus[:-1]), Counter(zip(corpus[:-1], corpus[1:]))
def p_next(w2, w1): return bi[(w1, w2)] / uni[w1]
def sentence_logprob(words):
    return sum(math.log(p_next(w2, w1)) for w1, w2 in zip(words[:-1], words[1:]))
lp = sentence_logprob("the cat sat on the mat .".split())
print("log P =", lp, " P =", math.exp(lp))               # = (1/4)(1)(1)(1)(1/4)(1) = 1/16 with these counts

# --- underflow: the product of many probabilities vs the sum of logs
probs = np.full(1500, 0.05)
print("product:", np.prod(probs), " sum of logs:", np.log(probs).sum())          # 0.0 vs −4493.6
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Confusing `P(A|B)` with `P(B|A)` | Misread precision/recall, prosecutor's fallacy | Write the event being conditioned on, in words |
| Conditioning on an event of probability 0 or a tiny count | `0/0` or wildly noisy estimates | Check the conditioning count; smooth or merge |
| Ignoring group sizes when pooling (Simpson) | Reversed conclusion | Stratify by the confounder; report sizes |
| Multiplying probabilities in the product form for long sequences | Underflow to `0.0` | Sum of log-probabilities |
| Treating the chain rule as requiring independence | Wrong factorization | The chain rule is *always* valid; independence only simplifies the conditionals |
| Evaluating a conditional on data that was selected using the outcome (leakage/selection bias) | Optimistic estimates | Define the conditioning event *before* looking at the label |
| Reporting precision without prevalence | Not comparable across datasets | State prevalence; see Lesson 3 |

### 3.6 ML link

- **Classifiers estimate `p(y|x)`;** metrics are conditionals of the confusion matrix (Stage 5A-06).
- **Language models** use the chain rule over tokens (Stage 5C-08/09); perplexity (Module 13) is derived from the log of this product.
- **Confounding and Simpson's paradox** appear in observational data and A/B test segmentation (Module 12 Lesson 7, Stage 5B-10).
- **Conditioning on features** defines conditional distributions in Bayesian networks and generative models (4C-04, 4C-10).

### 3.7 Lab (75 min)

1. Verify the multiplication rule and the "conditional is a probability" property by enumeration on three experiments.
2. Estimate `P(second ace | first ace)` by simulation (with and without rejection) and compare with `3/51`.
3. From a synthetic confusion matrix, compute four conditional probabilities and say in one sentence what each answers; change prevalence and recompute precision and recall.
4. Build a Simpson's-paradox example from scratch (choose your own counts), show the reversal numerically, and stratify to resolve it.
5. Build a bigram model on a tiny corpus, compute sentence log-probabilities, and demonstrate underflow vs log-space for a 500-word sequence.

### Check yourself (Unit 3)

1. What is the multiplication rule for two events?
2. Which conditional probability is precision?
3. Why compute sequence probabilities in log space?

**Reference answers:** (1) `P(A ∩ B) = P(A|B) P(B)`. (2) `P(y = 1 | ŷ = 1)`. (3) A product of many probabilities underflows to `0.0` in floating point; a sum of logs stays finite.

---

## Unit 4 — Law of total probability and Bayes' theorem (`03-…md`)

### 4.1 Why ML needs this

Bayes' theorem turns "how likely is this evidence if the hypothesis is true?" into "how likely is the hypothesis given the evidence?", which is what a classifier, a diagnostic test, or a spam filter must answer. It also explains why precision collapses when a rare class is searched for, and how to correct a model when the class balance in production differs from training.

### 4.2 Intuition

Start with a **prior** belief. Multiply by how well each hypothesis **explains** the evidence (the **likelihood**). Renormalize. The result is the **posterior**. A strong test applied to a rare condition still produces mostly false alarms, because the rare condition's prior is tiny.

### 4.3 Mechanics

- **Partition:** events `A₁, …, Aₖ` that are disjoint and cover `Ω`.
- **Law of total probability:** `P(B) = Σᵢ P(B | Aᵢ) P(Aᵢ)`: average the conditionals over the partition, weighted by the priors.
- **Bayes' theorem:** `P(Aᵢ | B) = P(B | Aᵢ) P(Aᵢ) / P(B) = P(B | Aᵢ) P(Aᵢ) / Σⱼ P(B | Aⱼ) P(Aⱼ)`.
- **Posterior ∝ likelihood × prior:** the denominator is just the normalizer, and you can compute unnormalized scores and divide by their sum.
- **Odds form:** `posterior odds = likelihood ratio × prior odds`, with `LR = P(B|A)/P(B|Aᶜ)`.
- **Natural frequencies:** think "out of 10,000 people…" instead of percentages; it makes base-rate effects hard to miss.
- **Base-rate neglect:** for a test with sensitivity `s`, specificity `c`, prevalence `π`: `PPV = sπ / (sπ + (1 − c)(1 − π))`. With `π = 1%`, `s = 90%`, `c = 95%` (synthetic): `PPV ≈ 15.4%`.
- **Sequential updating:** yesterday's posterior is today's prior; for independent evidence the log-odds add.
- **Prior (label) shift:** if class priors change from `p(y)` (training) to `p′(y)` (deployment) while `p(x|y)` is unchanged, then `p′(y|x) ∝ p(y|x)·p′(y)/p(y)`. Recalibrating a classifier's output this way is a standard correction.
- **Naive Bayes** (Project 2) assumes features are conditionally independent given the class: `p(x₁…x_d | y) = Π p(xⱼ | y)`; classify with `argmax_y log p(y) + Σ log p(xⱼ | y)`.
- **Zero-likelihood problem:** a single zero likelihood kills a posterior; **additive (Laplace) smoothing** `(count + α)/(total + α·V)` avoids it.
- **Frequentist vs Bayesian use:** Bayes' *theorem* is uncontroversial; "Bayesian inference" (priors on parameters) is a modelling choice (4C-05).

**Worked example (synthetic):** prevalence 1%, sensitivity 90%, specificity 95%. In 10,000 people: 100 sick → 90 positive; 9,900 healthy → 495 positive. `P(sick | positive) = 90/(90 + 495) ≈ 0.154`.

### 4.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def bayes(prior, lik):
    """prior: P(A_i); lik: P(B|A_i). Returns posteriors P(A_i|B) and the evidence P(B)."""
    prior, lik = np.asarray(prior, float), np.asarray(lik, float)
    assert np.isclose(prior.sum(), 1.0) and np.all((lik >= 0) & (lik <= 1))
    joint = prior * lik; evidence = joint.sum()                     # law of total probability
    return joint / evidence, evidence

# --- diagnostic test: formula vs natural frequencies vs simulation
pi, sens, spec = 0.01, 0.90, 0.95
post, ev = bayes([pi, 1 - pi], [sens, 1 - spec])
ppv_formula = sens * pi / (sens * pi + (1 - spec) * (1 - pi)); assert np.isclose(post[0], ppv_formula)
print("PPV (formula):", post[0], " natural frequencies:", 90 / (90 + 495))
N = 1_000_000; sick = rng.random(N) < pi
test_pos = np.where(sick, rng.random(N) < sens, rng.random(N) < 1 - spec)
ppv_sim = (sick & test_pos).sum() / test_pos.sum(); se = math.sqrt(ppv_sim * (1 - ppv_sim) / test_pos.sum())
print(f"PPV simulated {ppv_sim:.4f} ± {se:.4f}"); assert abs(ppv_sim - post[0]) < 4 * se

# --- precision collapses as prevalence falls
for pr in (0.5, 0.1, 0.01, 0.001):
    print(f"prevalence {pr:6.3f}  PPV = {bayes([pr, 1 - pr], [sens, 1 - spec])[0][0]:.4f}")

# --- odds form and sequential updating: two independent positive tests
prior_odds = pi / (1 - pi); LR = sens / (1 - spec)
post_odds_2 = prior_odds * LR * LR; post_2 = post_odds_2 / (1 + post_odds_2)
step1 = bayes([pi, 1 - pi], [sens, 1 - spec])[0]; step2 = bayes(step1, [sens, 1 - spec])[0]
assert np.isclose(post_2, step2[0]); print("after two positives:", post_2)

# --- label (prior) shift correction, verified by simulation
# class 1 ~ N(+1, 1), class 0 ~ N(−1, 1); train with 50/50, deploy with 5% positives
def post1(x, prior1):
    l1, l0 = np.exp(-0.5 * (x - 1) ** 2), np.exp(-0.5 * (x + 1) ** 2)
    return prior1 * l1 / (prior1 * l1 + (1 - prior1) * l0)
x = rng.normal(loc=np.where(rng.random(400_000) < 0.05, 1.0, -1.0), scale=1.0)       # deployment distribution (5% positive)
# the same classifier trained at 50/50, then corrected by p'(y)/p(y):
p_train = post1(x, 0.5); odds = p_train / (1 - p_train) * (0.05 / 0.95) / (0.5 / 0.5); p_corrected = odds / (1 + odds)
assert np.allclose(p_corrected, post1(x, 0.05))
# calibration check on deployment data: among points with predicted prob ≈ 0.5, how often is y=1?
labels = rng.random(400_000) < 0.05; x2 = rng.normal(loc=np.where(labels, 1.0, -1.0), scale=1.0)
for name, pr in (("uncorrected (50/50 prior)", post1(x2, 0.5)), ("corrected (5% prior)", post1(x2, 0.05))):
    m = (pr > 0.45) & (pr < 0.55); print(f"{name:26s} predicted ≈ 0.5 → observed positive rate {labels[m].mean():.3f} (n={m.sum()})")

# --- zero likelihood and smoothing
counts = {"spam": {"free": 20, "meeting": 0}, "ham": {"free": 1, "meeting": 15}}
alpha, V = 1.0, 2
for cls, c in counts.items():
    tot = sum(c.values()); print(cls, {w: (n + alpha) / (tot + alpha * V) for w, n in c.items()})

# --- discrete-hypothesis coin: update a grid of biases after each flip
thetas = np.linspace(0.01, 0.99, 99); belief = np.ones_like(thetas) / len(thetas)
flips = rng.random(40) < 0.7
for f in flips:
    belief = belief * (thetas if f else 1 - thetas); belief /= belief.sum()
print("posterior mean bias:", float(thetas @ belief), " (empirical heads fraction:", flips.mean(), ")")
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Base-rate neglect | "99%-accurate test" misinterpreted | Compute PPV with prevalence; use natural frequencies |
| Using `P(B|A)` where `P(A|B)` is needed | Posterior and likelihood confused | Write Bayes explicitly; label prior/likelihood/posterior |
| Priors that do not sum to 1 / likelihoods > 1 | Invalid posterior | `assert` in `bayes()` |
| Zero likelihood from unseen features | Posterior collapses to 0 or `0/0` | Laplace smoothing; ignore out-of-vocabulary tokens consistently |
| Double-counting the same evidence | Overconfident posterior | Update once per *independent* piece of evidence |
| Assuming conditional independence when features are duplicated or correlated | Overconfident naive-Bayes posteriors (Project 2) | Check calibration; remove duplicates; use a model that captures dependence |
| Applying a classifier trained at one prevalence to another without correction | Biased posteriors, wrong thresholds | Prior-shift correction or re-calibration |
| Multiplying probabilities of many features in raw space | Underflow | Log-space sums |

### 4.6 ML link

- **Every probabilistic classifier** (logistic regression, naive Bayes, a softmax head) produces a posterior; Bayes' rule links them to class-conditional generative models (Module 14, Stage 5A-05).
- **Precision depends on prevalence:** reported precision on a balanced test set overstates production precision on a rare class (Stage 5A-06, 5B-03).
- **Prior-shift correction** for deployed models whose class balance drifts (Stage 5D-12 monitoring).
- **Naive Bayes** is the canonical spam/text baseline (Stage 5A-10; Project 2).
- **Bayesian inference** over parameters generalizes the coin-grid update (4C-05).

### 4.7 Lab (90 min)

1. Compute the diagnostic-test posterior three ways (formula, natural frequencies, simulation) and assert agreement.
2. Plot PPV vs prevalence for three tests with different sensitivity/specificity; mark the prevalence at which PPV = 50%.
3. Prior-shift experiment: train a threshold classifier at 50/50, deploy at 2%/5%/20% prevalence, compare precision and calibration with and without the odds correction.
4. Sequential-update experiment: feed 10 pieces of independent evidence and verify that log-odds add.
5. Show how one zero likelihood destroys a naive-Bayes posterior and how `α` smoothing repairs it; sweep `α ∈ {0, 0.01, 0.1, 1, 10}`.

### Check yourself (Unit 4)

1. State Bayes' theorem for a partition.
2. A test has sensitivity 99% and specificity 99%; prevalence is 0.1%. Is a positive test likely to be a true positive?
3. How do posterior odds relate to prior odds?

**Reference answers:** (1) `P(Aᵢ|B) = P(B|Aᵢ)P(Aᵢ) / Σⱼ P(B|Aⱼ)P(Aⱼ)`. (2) No: `PPV = 0.99·0.001/(0.99·0.001 + 0.01·0.999) ≈ 0.090` (about 9%). (3) Posterior odds = likelihood ratio × prior odds.

---

## Unit 5 — Independence (`04-…md`)

### 5.1 Why ML needs this

Almost every learning algorithm silently assumes independence somewhere: that training examples are independent draws (i.i.d.), that features are independent given the class (naive Bayes), that a noise term is independent of the input. When the assumption fails, standard errors are wrong, validation scores are inflated, and models are overconfident.

### 5.2 Intuition

`A` and `B` are independent if learning that `B` happened tells you **nothing** about `A`. Independence is a statement about probabilities, not about physical causation, and **it is not the same as being disjoint**: disjoint events with positive probability are strongly dependent (if one happens, the other cannot).

### 5.3 Mechanics

- **Definition:** `A ⊥ B ⇔ P(A ∩ B) = P(A) P(B)`; equivalently `P(A | B) = P(A)` when `P(B) > 0`.
- **Disjoint ≠ independent:** if `A ∩ B = ∅` and `P(A), P(B) > 0`, then `P(A ∩ B) = 0 ≠ P(A)P(B)`.
- **Mutual vs pairwise independence:** events `A, B, C` are *mutually* independent if every sub-collection factorizes (including `P(A∩B∩C) = P(A)P(B)P(C)`); *pairwise* independence does not imply it. **XOR example:** `A, B` fair independent bits, `C = A ⊕ B`: every pair is independent, but `P(A∩B∩C) = 0 ≠ 1/8`.
- **Conditional independence:** `A ⊥ B | C ⇔ P(A ∩ B | C) = P(A|C) P(B|C)`. It neither implies nor is implied by marginal independence.
  - **Common cause:** `C` influences both `A` and `B`: marginally dependent, conditionally independent given `C`.
  - **Collider (explaining away):** `A, B` independent causes of `C`: marginally independent, **dependent given `C`** (conditioning on a common effect creates dependence).
- **Independent random variables:** the joint factorizes, `p(x, y) = p(x)p(y)` (or `F(x, y) = F(x)F(y)`); then `E[XY] = E[X]E[Y]` and `Var(X+Y) = Var X + Var Y` (Lessons 7–8). Independence ⇒ zero covariance; **zero covariance does not imply independence.**
- **I.i.d. sample:** independent draws from the same distribution. Consequences used throughout: `Var(X̄) = σ²/n`; the law of large numbers and CLT (Module 11).
- **Dependence reduces information:** for positively autocorrelated samples (lag-1 correlation `ρ`, AR(1)), the variance of the sample mean is about `(σ²/n)(1+ρ)/(1−ρ)`, so the **effective sample size** is about `n(1−ρ)/(1+ρ)` `[VERIFY: AR(1) asymptotic formula]`.
- **Naive Bayes** assumes `x_j ⊥ x_k | y` for all feature pairs; it is often wrong and yet often a usable classifier, but its probabilities are typically over-confident when features are redundant.
- **Practical independence checks:** compare the joint frequency table with the product of marginals; for numeric data, check correlation *and* a nonlinear relation (a scatterplot or a rank/binning test); a formal test arrives in Module 12 `[VERIFY]`.

**Worked example:** two fair dice: `A = {first is even}`, `B = {sum is 7}`: `P(A) = 1/2`, `P(B) = 1/6`, `P(A ∩ B) = 3/36 = 1/12 = P(A)P(B)`, so independent (even though `B` involves both dice).

### 5.4 Code

```python
import itertools, math
from fractions import Fraction
import numpy as np
rng = np.random.default_rng(0)

Omega = list(itertools.product(range(1, 7), repeat=2))
P = lambda ev: Fraction(sum(1 for w in Omega if ev(w)), len(Omega))
A, B = (lambda w: w[0] % 2 == 0), (lambda w: w[0] + w[1] == 7)
assert P(lambda w: A(w) and B(w)) == P(A) * P(B)                               # independent

# --- disjoint events with positive probability are dependent
E1, E2 = (lambda w: w[0] + w[1] == 7), (lambda w: w[0] + w[1] == 8)
assert P(lambda w: E1(w) and E2(w)) == 0 and P(E1) * P(E2) > 0

# --- pairwise but not mutual independence: C = A xor B
bits = list(itertools.product([0, 1], repeat=2)); Pw = lambda ev: Fraction(sum(1 for w in bits if ev(w)), 4)
a_, b_, c_ = (lambda w: w[0] == 1), (lambda w: w[1] == 1), (lambda w: (w[0] ^ w[1]) == 1)
for X, Y in ((a_, b_), (a_, c_), (b_, c_)): assert Pw(lambda w: X(w) and Y(w)) == Pw(X) * Pw(Y)       # pairwise independent
assert Pw(lambda w: a_(w) and b_(w) and c_(w)) == 0 != Pw(a_) * Pw(b_) * Pw(c_)                       # not mutually independent

# --- common cause: dependent marginally, independent given C
N = 400_000
C = rng.random(N) < 0.5
Aa = rng.random(N) < np.where(C, 0.9, 0.1); Bb = rng.random(N) < np.where(C, 0.9, 0.1)
phi = lambda x, y: np.corrcoef(x, y)[0, 1]
print("corr(A,B) =", round(phi(Aa, Bb), 3), "| corr(A,B | C=1) =", round(phi(Aa[C], Bb[C]), 3), "| corr(A,B | C=0) =", round(phi(Aa[~C], Bb[~C]), 3))

# --- collider: independent causes become dependent given the effect
Ac, Bc = rng.random(N) < 0.5, rng.random(N) < 0.5; Cc = Ac | Bc
print("corr(A,B) =", round(phi(Ac, Bc), 3), "| corr(A,B | C=1) =", round(phi(Ac[Cc], Bc[Cc]), 3))      # ≈ 0, then clearly negative

# --- independence ⇒ zero covariance, but not conversely
x = rng.normal(size=N); y = x ** 2
print("cov(X, X²) =", round(np.cov(x, y)[0, 1], 3), " (≈ 0) yet Y is a deterministic function of X")

# --- effective sample size for autocorrelated data (AR(1))
def ar1(n, rho, g): 
    e = g.normal(size=n); x = np.empty(n); x[0] = e[0]
    for t in range(1, n): x[t] = rho * x[t - 1] + math.sqrt(1 - rho ** 2) * e[t]
    return x
n = 400
for rho in (0.0, 0.5, 0.9):
    means = np.array([ar1(n, rho, np.random.default_rng(s)).mean() for s in range(3000)])
    var_mean, iid = means.var(ddof=1), 1.0 / n
    print(f"ρ={rho}: Var(mean) = {var_mean:.5f}  iid σ²/n = {iid:.5f}  ratio = {var_mean / iid:.2f}  predicted (1+ρ)/(1−ρ) = {(1 + rho) / (1 - rho):.2f}  ESS ≈ {n * iid / var_mean:.0f}")

# --- duplicated feature breaks naive-Bayes calibration (preview of Project 2)
y_ = rng.random(N) < 0.5; f = rng.random(N) < np.where(y_, 0.7, 0.3)
def nb_post(copies):
    ll1, ll0 = np.where(f, 0.7, 0.3) ** copies, np.where(f, 0.3, 0.7) ** copies
    return ll1 / (ll1 + ll0)                                         # equal priors
for copies in (1, 2, 5):
    p = nb_post(copies); m = (f == 1)
    print(f"{copies} copy/copies: predicted P(y=1|f=1) = {p[m][0]:.3f}  true = {y_[m].mean():.3f}")   # overconfident as copies grow
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Equating *disjoint* with *independent* | Wrong multiplication or wrong "they can't both happen, so they are unrelated" | `P(A∩B) = 0` with positive marginals means dependence |
| Assuming pairwise independence gives mutual independence | Wrong joint probabilities (XOR) | Check the full joint |
| Multiplying probabilities of dependent events | Overconfident or underconfident joint | Use the chain rule with conditionals |
| Treating zero correlation as independence | Missed nonlinear dependence | Check a nonlinear dependence measure or a plot |
| Conditioning on a collider (selection on the outcome) | Spurious association (selection bias) | Draw the causal graph; avoid conditioning on common effects |
| Assuming i.i.d. for time series, repeated measures, or grouped data | Standard errors too small; leaked splits | Split by group/time; effective sample size; clustered standard errors |
| Duplicated or redundant features under naive Bayes | Overconfident posteriors | Deduplicate; check calibration (Project 2) |
| Randomly splitting near-duplicate rows into train and test | Inflated test score | Group-aware splits (Stage 5A-07) |

### 5.6 ML link

- **I.i.d. assumption** underlies empirical risk minimization and generalization arguments (4C-05 Lesson 7); violations drive train/test leakage failures (Stage 5A-07).
- **Naive Bayes** is a conditional-independence model (Project 2).
- **Effective sample size** corrects confidence intervals for autocorrelated data and MCMC samples (Module 12, 4C-04).
- **Collider bias / selection bias** distorts datasets built from filtered populations (Stage 5B-10).
- **Independence of noise from inputs** is assumed by most regression noise models (Module 14).

### 5.7 Lab (75 min)

1. Verify independence/dependence exactly for six event pairs on two dice; include one disjoint pair.
2. Reproduce the XOR example and a three-event example where pairwise independence fails to imply mutual independence.
3. Simulate the common-cause and collider structures; tabulate marginal and conditional correlations.
4. Estimate the effective sample size for AR(1) series at `ρ ∈ {0, 0.5, 0.9, 0.99}` by repeated simulation and compare with `n(1−ρ)/(1+ρ)`.
5. Demonstrate the leakage effect: duplicate 20% of training rows into the test split and show how a nearest-neighbour model's accuracy is inflated.

### Check yourself (Unit 5)

1. Can two events with positive probability be both disjoint and independent?
2. In the collider structure `A → C ← B` with independent `A, B`, what happens to the dependence between `A` and `B` after conditioning on `C`?
3. If you have `n` samples with lag-1 autocorrelation `0.9`, roughly how many independent samples do they behave like?

**Reference answers:** (1) No: disjoint means `P(A∩B) = 0`, but independence needs `P(A)P(B) > 0`. (2) They become dependent (explaining away). (3) About `n(1 − 0.9)/(1 + 0.9) ≈ n/19`.

---

## Unit 6 — Random variables: discrete and continuous (`05-…md`)

### 6.1 Why ML needs this

Features, labels, predictions, losses, gradients, and metrics are all **random variables** because they depend on random data. Treating them as such is what lets you ask for their expectation, variance, and distribution (Lessons 6–8, Modules 10–12).

### 6.2 Intuition

A random variable is a number produced by a random experiment: the face of a die, the number of heads in 10 flips, the waiting time for the next request. Formally it is a **function from outcomes to numbers**, `X: Ω → ℝ`; probabilities of events about `X` are probabilities of sets of outcomes.

### 6.3 Mechanics

- **Random variable:** `X: Ω → ℝ`. The event `{X = x}` is `{ω : X(ω) = x}`; `{X ≤ x}` is `{ω : X(ω) ≤ x}`.
- **Discrete RV:** takes countably many values (die, counts, class index); described by a PMF.
- **Continuous RV:** takes values in an interval (waiting time, a sensor reading); `P(X = x) = 0` for every single `x`; described by a PDF (Lesson 6).
- **Mixed:** a point mass plus a density (e.g., clipped values: an activation `max(0, X)` has a spike at 0).
- **Support:** the set of values with positive probability/density.
- **Transformation:** `Y = g(X)` is a random variable. Discrete case: `P(Y = y) = Σ_{x: g(x)=y} P(X = x)`. Continuous case: the change-of-variables formula (4C-04 Lesson 7).
- **Indicator variables:** `1[A]` is 1 if event `A` occurs else 0; then `E[1[A]] = P(A)`. Accuracy is the expectation of the error indicator, a trick used constantly (Lesson 7).
- **Random vector:** several RVs at once (`(X, Y)`, a feature vector); joint, marginal, and conditional distributions follow (4C-04).
- **Realization vs random variable:** `X` is the random quantity; `x` is a value it took. A dataset `x₁…xₙ` is *realizations* of RVs `X₁…Xₙ`.
- **Empirical distribution:** the distribution that puts mass `1/n` on each data point; the stand-in for the unknown true distribution (Module 11–12).
- **Sampling in NumPy:** `rng = np.random.default_rng(seed)`; `rng.integers`, `rng.random`, `rng.normal`, `rng.choice(..., p=...)`.

**Worked example:** `X` = sum of two fair dice: `X: Ω → {2,…,12}`. `P(X = 7) = 6/36`. `Y = X mod 3` has `P(Y = 0) = P(X ∈ {3, 6, 9, 12}) = (2 + 5 + 4 + 1)/36 = 1/3`.

### 6.4 Code

```python
import itertools
from collections import defaultdict
from fractions import Fraction
import numpy as np

Omega = list(itertools.product(range(1, 7), repeat=2))
X = lambda w: w[0] + w[1]                                      # a random variable is a function on Ω

# PMF by enumeration
pmf = defaultdict(Fraction)
for w in Omega: pmf[X(w)] += Fraction(1, len(Omega))
assert sum(pmf.values()) == 1 and pmf[7] == Fraction(1, 6)
print({k: str(v) for k, v in sorted(pmf.items())})

# transformation Y = g(X): push the PMF forward
pmf_y = defaultdict(Fraction)
for x, p in pmf.items(): pmf_y[x % 3] += p
assert pmf_y[0] == Fraction(1, 3) and sum(pmf_y.values()) == 1

# indicator variables: accuracy is the mean of an indicator, and E[1_A] = P(A)
rng = np.random.default_rng(0)
y_true = rng.integers(0, 2, 10_000); y_pred = np.where(rng.random(10_000) < 0.9, y_true, 1 - y_true)
err = (y_pred != y_true).astype(float)                         # indicator of the event "error"
print("error rate =", err.mean(), " accuracy =", 1 - err.mean())

# simulate and compare with the exact PMF
N = 300_000; s = rng.integers(1, 7, size=(N, 2)).sum(axis=1)
for v in (2, 7, 12):
    ph = (s == v).mean(); se = np.sqrt(ph * (1 - ph) / N); assert abs(ph - float(pmf[v])) < 4 * se

# a continuous RV: P(X = x) = 0 but intervals have positive probability
u = rng.random(1_000_000)
print("P(0.30 < U < 0.31) ≈", ((u > 0.30) & (u < 0.31)).mean(), " P(U == 0.3) =", (u == 0.3).mean())

# a mixed RV: ReLU of a normal has a point mass at 0 and a density on (0, ∞)
z = rng.normal(size=1_000_000); r = np.maximum(z, 0.0)
print("P(ReLU(Z) == 0) ≈", (r == 0).mean(), "(exact 0.5)")

# realization vs random variable: the sample mean is itself a random variable
means = np.array([rng.normal(size=50).mean() for _ in range(5000)])
print("sample mean varies from run to run: std ≈", means.std(ddof=1), " (σ/√n =", 1 / np.sqrt(50), ")")

# weighted sampling from a categorical distribution
cats, p = np.array(["a", "b", "c"]), np.array([0.2, 0.5, 0.3])
draw = rng.choice(cats, size=200_000, p=p); print({str(c): round((draw == c).mean(), 3) for c in cats})
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Confusing a random variable with its realized value | "The variance of this number" for a fixed number | Say which quantity is random; a fixed number has no variance |
| Computing `P(X = x)` for a continuous `X` and getting `0` | "Impossible event" confusion | Use intervals or densities |
| Building the PMF of `Y = g(X)` by transforming each probability instead of summing over preimages | Probabilities that exceed 1 or do not sum to 1 | Sum over all `x` with `g(x) = y` |
| Treating a mixed variable as purely continuous | Missing point mass (e.g., ReLU outputs) | Account for the spike explicitly |
| Mixing up the sample space and the range | Wrong enumeration | Enumerate `Ω` first, then map |
| Reusing a generator across "independent" simulations without seeds | Correlated results, irreproducibility | One seeded generator per experiment |
| Calling a *statistic* (sample mean) a constant | Ignoring its sampling variability | It is a random variable with its own distribution (Module 11) |

### 6.6 ML link

- **Losses, gradients, and metrics are random variables** over the data distribution; training minimizes an expectation (Lesson 7).
- **Labels as discrete RVs; targets as continuous RVs**, with different likelihood models (Module 10, 14).
- **Mixed variables:** ReLU outputs, clipped targets, zero-inflated counts.
- **Empirical distribution** is what the training set is; risk minimization on it is *empirical* risk minimization (4C-05).
- **Indicator trick** turns accuracy and error rates into expectations, giving standard errors for free.

### 6.7 Lab (60 min)

1. Define five RVs on small sample spaces; compute PMFs by enumeration; push forward through two transformations.
2. Verify each PMF by simulation with a `4·SE` bound.
3. Compute a classifier's accuracy as an indicator mean and attach a standard error.
4. Simulate a mixed RV (ReLU of normal; clipped exponential) and report the point mass and the density part.
5. Demonstrate that the sample mean is a random variable: plot the histogram of 5,000 sample means and compare its spread to `σ/√n`.

### Check yourself (Unit 6)

1. Is a random variable a number or a function?
2. For a continuous `X`, what is `P(X = 3)`?
3. What is `E[1[A]]`?

**Reference answers:** (1) A function from outcomes to numbers (its value on a particular outcome is a number). (2) `0`. (3) `P(A)`.

---

## Unit 7 — PMF, PDF, and CDF (`06-…md`)

### 7.1 Why ML needs this

These three objects are how every distribution in ML is specified and evaluated: a PMF for a categorical/count output, a PDF for a continuous noise or prior, a CDF for percentiles, p-values, and sampling. Mistaking a density for a probability (a `pdf > 1` "bug") is a classic confusion.

### 7.2 Intuition

- **PMF** `p(x) = P(X = x)`: bar heights that sum to 1.
- **PDF** `f(x)`: a *density*; probability is **area** under it, so `f(x)` can exceed 1 if the curve is narrow.
- **CDF** `F(x) = P(X ≤ x)`: the running total of probability; it starts at 0, ends at 1, never decreases.

### 7.3 Mechanics

- **PMF:** `p(x) ≥ 0`, `Σₓ p(x) = 1`.
- **PDF:** `f(x) ≥ 0`, `∫ f = 1` (Module 06 normalization), `P(a < X < b) = ∫ₐᵇ f`. Units of `f` are probability per unit of `x`.
- **CDF:** `F(x) = P(X ≤ x)`: `= Σ_{t ≤ x} p(t)` (discrete, a step function) or `∫_{−∞}^x f(t)dt` (continuous, Module 06 Lesson 2). Properties: nondecreasing, right-continuous, `F(−∞) = 0`, `F(∞) = 1`; `P(a < X ≤ b) = F(b) − F(a)`; **`f = F′`** where the derivative exists.
- **Survival function** `S(x) = 1 − F(x) = P(X > x)` (tail probability).
- **Quantile function** (inverse CDF) `Q(q) = inf{x : F(x) ≥ q}`: the median is `Q(0.5)`.
- **Inverse-transform sampling:** if `U ~ Uniform(0, 1)`, then `X = Q(U)` has CDF `F`. Exponential: `Q(u) = −ln(1 − u)/λ`. This is how samplers work (Module 11 Lesson 1).
- **Empirical CDF (ECDF):** `F̂ₙ(x) = (1/n) Σ 1[xᵢ ≤ x]`: a step function that converges to `F` (Glivenko–Cantelli `[VERIFY]`); the Kolmogorov–Smirnov statistic is `sup |F̂ₙ − F|` (Module 12).
- **Histogram as a density estimate:** with `density=True`, bar areas sum to 1; with counts, they do not.
- **Standard distributions** (Module 10): Bernoulli/binomial, categorical, Poisson, uniform, exponential, normal, beta.
- **Normal pdf and cdf:** `f(x) = exp(−(x−μ)²/(2σ²))/(σ√(2π))`; `F(x) = ½[1 + erf((x−μ)/(σ√2))]`.
- **Discrete vs continuous in code:** PMF on a finite support with `np.bincount`/`Counter`; PDF evaluated pointwise; CDF by `np.cumsum` (discrete) or running trapezoid integral (continuous).

**Worked example:** `X ~ Uniform(0, 0.1)`: `f(x) = 10` on `[0, 0.1]`, which exceeds 1, and `∫ f = 10 × 0.1 = 1` ✓. `F(0.05) = 0.5`.

### 7.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

# --- PMF: binomial(n=10, p=0.3); CDF is the cumulative sum
n, p = 10, 0.3
pmf = np.array([math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)])
cdf = np.cumsum(pmf)
assert np.isclose(pmf.sum(), 1.0) and np.isclose(cdf[-1], 1.0) and np.all(np.diff(cdf) >= 0)
samples = rng.binomial(n, p, size=300_000)
emp = np.bincount(samples, minlength=n + 1) / len(samples)
assert np.max(np.abs(emp - pmf)) < 0.004                                     # simulation matches

# --- PDF: normal; integrate numerically (Module 06) and compare with the erf-based CDF
def trapezoid(y, x): return float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2))
norm_pdf = lambda x, mu=0.0, s=1.0: np.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))
norm_cdf = lambda x, mu=0.0, s=1.0: 0.5 * (1 + np.vectorize(math.erf)((np.asarray(x) - mu) / (s * math.sqrt(2))))
xs = np.linspace(-10, 10, 200_001); fx = norm_pdf(xs)
assert np.isclose(trapezoid(fx, xs), 1.0, atol=1e-10)
cum = np.r_[0.0, np.cumsum(np.diff(xs) * (fx[1:] + fx[:-1]) / 2)]
assert np.max(np.abs(cum - norm_cdf(xs))) < 1e-9                              # CDF = running integral of PDF
print("P(-1.96 < Z < 1.96) =", norm_cdf(1.96) - norm_cdf(-1.96))

# --- pdf can exceed 1; it is a density, not a probability
a, b = 0.0, 0.1; f_unif = 1 / (b - a)
print("Uniform(0, 0.1) density =", f_unif, " integrates to", f_unif * (b - a))
sigma = 0.01; print("N(0, 0.01²) pdf at 0 =", norm_pdf(0.0, 0.0, sigma), "(≫ 1, still integrates to 1)")

# --- quantiles and inverse-transform sampling (exponential)
lam = 1.5
Q = lambda u: -np.log1p(-u) / lam
U = rng.random(400_000); X = Q(U)
ecdf = lambda x, data: np.searchsorted(np.sort(data), x, side="right") / len(data)
grid = np.linspace(0, 6, 200)
ks = np.max(np.abs(ecdf(grid, X) - (1 - np.exp(-lam * grid))))
print("KS distance to the true CDF:", ks); assert ks < 0.005

# --- histogram normalization: density=True vs counts
data = rng.normal(size=100_000)
counts, edges = np.histogram(data, bins=60); dens, _ = np.histogram(data, bins=60, density=True)
w = np.diff(edges)
print("sum(counts*1) =", counts.sum(), " area with density=True =", (dens * w).sum())
mid = (edges[1:] + edges[:-1]) / 2
print("max |hist density − true pdf| =", np.max(np.abs(dens - norm_pdf(mid))))

# --- survival function and a tail probability
S = lambda x: 1 - norm_cdf(x)
print("P(Z > 3) =", float(S(3.0)), " (≈ 0.00135)")

# --- P(a < X <= b) = F(b) − F(a) for a discrete variable
assert np.isclose(cdf[5] - cdf[2], pmf[3:6].sum())
```

### 7.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Reading a `pdf` value as a probability (`f(x) > 1` "impossible") | False bug reports | Probability is area; check `∫ f = 1` |
| Histogram with counts compared to a pdf | Curve and bars on different scales | `density=True`; or scale counts by `n·binwidth` |
| Evaluating a CDF outside its support | Wrong `0`/`1` handling | Clip to the support; define the boundaries |
| Using `P(X < x)` and `P(X ≤ x)` interchangeably for discrete `X` | Off-by-one-probability mass | Be explicit: `F(x) = P(X ≤ x)` |
| Discretizing a continuous variable too coarsely when building a PMF | Biased probabilities | Refine bins; keep a bin-width correction |
| Quantiles from an ECDF with too few samples | Noisy tails | State the sample size; use more data or a parametric tail |
| Assuming the normal tail is right for heavy-tailed data | Underestimated extremes | Check tail behaviour (Module 06 Lesson 4) |
| Inverse-transform with `U = 0` or `1` exactly | `inf` | Use `1 − U` or clip away from the ends |

### 7.6 ML link

- **Classifier softmax outputs are PMFs** over classes (Module 10 Lesson 2).
- **Likelihoods** of continuous targets are PDF values; a `pdf > 1` is fine, and negative log-likelihood can therefore be negative (Module 13, 4C-05).
- **CDFs/quantiles:** percentiles for latency SLOs, prediction intervals, p-values (Module 12).
- **Inverse-transform sampling** underlies sampling from model outputs and simulation (Module 11).
- **ECDF and KS distance** are used in drift monitoring (Stage 5D-12).

### 7.7 Lab (75 min)

1. Build the PMF/CDF of a binomial from scratch; check against simulation; compute `P(3 ≤ X ≤ 6)` two ways.
2. Verify that three PDFs (uniform, exponential, normal) integrate to 1 numerically; build each CDF by running integral and compare with closed forms.
3. Produce a case where `pdf > 1` and explain it in two sentences; compute its negative log-likelihood for a data point and show it can be negative.
4. Implement inverse-transform sampling for the exponential and for a custom piecewise-linear CDF; validate with ECDF and KS distance.
5. Reproduce the histogram-normalization bug and fix it.

### Check yourself (Unit 7)

1. How do you get `P(a < X ≤ b)` from the CDF?
2. How is the PDF related to the CDF?
3. If `U ~ Uniform(0,1)` and `F` is a continuous strictly increasing CDF, what is the distribution of `F⁻¹(U)`?

**Reference answers:** (1) `F(b) − F(a)`. (2) `f = F′` (and `F` is the running integral of `f`). (3) It has CDF `F`.

---

## Unit 8 — Expectation and variance (`07-…md`)

### 8.1 Why ML needs this

Training minimizes an **expected** loss. Evaluation reports a **mean** with a **standard error**. Gradient noise (Module 08) is a **variance**. Almost every statement about "typical" behaviour and "spread" in this stage reduces to `E` and `Var`, and a handful of rules make them easy to compute.

### 8.2 Intuition

The **expectation** is the probability-weighted average: the long-run mean of repeated draws, the "center of mass" of the distribution. The **variance** is the expected squared distance from that center: the spread.

### 8.3 Mechanics

- **Expectation:** `E[X] = Σ x p(x)` (discrete) or `∫ x f(x) dx` (continuous; requires `∫|x| f < ∞`: the Cauchy distribution has **no** mean, Module 06 Lesson 4).
- **LOTUS (law of the unconscious statistician):** `E[g(X)] = Σ g(x)p(x)` or `∫ g(x)f(x)dx`; no need to find the distribution of `g(X)`.
- **Linearity (always, even for dependent variables):** `E[aX + bY + c] = aE[X] + bE[Y] + c`. **Indicator trick:** `X = Σ 1[Aᵢ]` ⇒ `E[X] = ΣP(Aᵢ)`; e.g., the expected number of fixed points of a random permutation is `1`.
- **Not multiplicative in general:** `E[XY] = E[X]E[Y]` only if `X, Y` are uncorrelated (in particular independent).
- **Jensen's inequality:** for convex `g`, `E[g(X)] ≥ g(E[X])`; e.g., `E[X²] ≥ (E[X])²`, and (concave `log`) `E[log X] ≤ log E[X]`. In ML: the average of log-likelihoods ≠ the log of the average likelihood.
- **Variance:** `Var(X) = E[(X − μ)²] = E[X²] − μ²`; std `σ = √Var`.
  - `Var(aX + b) = a² Var(X)` (shifts do not matter, scale squares).
  - `Var(X + Y) = Var X + Var Y + 2 Cov(X, Y)`; **independent ⇒ variances add.**
  - For `n` i.i.d. draws: `Var(X̄) = σ²/n`, so the **standard error** is `σ/√n`.
- **Common values:** Bernoulli(`p`): mean `p`, var `p(1−p)`; fair die: mean `3.5`, var `35/12 ≈ 2.917`; Uniform(`a,b`): mean `(a+b)/2`, var `(b−a)²/12`; Exponential(`λ`): mean `1/λ`, var `1/λ²`; Normal(`μ,σ²`): mean `μ`, var `σ²`.
- **Sample estimators:** the sample mean `x̄` is unbiased for `μ`; the sample variance with divisor `n − 1` (`ddof=1`) is unbiased for `σ²`, while divisor `n` (`ddof=0`) is biased low; NumPy's `np.var` defaults to `ddof=0`, and `np.std` too (pandas `.var()` defaults to `ddof=1`) `[VERIFY in the installed versions]`.
- **Chebyshev's inequality:** `P(|X − μ| ≥ kσ) ≤ 1/k²` for any distribution with finite variance; **Markov:** for `X ≥ 0`, `P(X ≥ a) ≤ E[X]/a`. They are loose but distribution-free.
- **Numerical stability:** `E[X²] − μ²` suffers **catastrophic cancellation** when `|μ| ≫ σ`; compute `mean((x − mean)²)` (two-pass) or use **Welford's** online algorithm.
- **Risk:** the expected loss `R(θ) = E[ℓ(θ; X, Y)]` is what training approximates by a sample average (empirical risk).
- **Expectation conditional on an event** (and the law of total expectation `E[X] = E[E[X|Y]]`) are previewed here and developed in 4C-04.

**Worked example (fair die):** `E[X] = 3.5`; `E[X²] = 91/6`; `Var = 91/6 − (7/2)² = 35/12`. Two dice: `E[sum] = 7`, `Var = 35/6`.

### 8.4 Code

```python
import numpy as np
from fractions import Fraction
rng = np.random.default_rng(0)

# --- exact E and Var for a fair die, by definition
xs = [1, 2, 3, 4, 5, 6]; p = Fraction(1, 6)
E = sum(x * p for x in xs); E2 = sum(x * x * p for x in xs)
assert E == Fraction(7, 2) and E2 - E * E == Fraction(35, 12)

# --- LOTUS, linearity (with DEPENDENT variables), and variance of a sum
N = 1_000_000
X = rng.integers(1, 7, size=N).astype(float); Y = X ** 2                       # Y depends on X
assert np.isclose((X + Y).mean(), X.mean() + Y.mean())                         # linearity needs no independence
cov = np.mean((X - X.mean()) * (Y - Y.mean()))
assert np.isclose((X + Y).var(), X.var() + Y.var() + 2 * cov)
print("E[XY] =", (X * Y).mean(), " E[X]E[Y] =", X.mean() * Y.mean(), "(differ: X and Y are dependent)")

# --- Jensen: E[g(X)] ≥ g(E[X]) for convex g; E[log X] ≤ log E[X]
Z = rng.exponential(scale=2.0, size=N)
print("E[X²] =", (Z ** 2).mean(), "≥ (E[X])² =", Z.mean() ** 2)
print("E[log X] =", np.log(Z).mean(), "≤ log E[X] =", np.log(Z.mean()))

# --- Var(aX + b) = a² Var(X); Var(X̄) = σ²/n  (standard error)
a, b = 3.0, 10.0; assert np.isclose((a * Z + b).var(), a * a * Z.var(), rtol=1e-6)
n = 25
means = np.array([rng.exponential(scale=2.0, size=n).mean() for _ in range(40_000)])
print("Var(mean of 25) =", means.var(ddof=1), " σ²/n =", 4.0 / n)               # Exponential(scale 2): σ² = 4

# --- ddof: biased vs unbiased variance estimator
est0 = np.mean([rng.normal(size=5).var(ddof=0) for _ in range(100_000)])
est1 = np.mean([rng.normal(size=5).var(ddof=1) for _ in range(100_000)])
print(f"mean of var(ddof=0) = {est0:.3f}   var(ddof=1) = {est1:.3f}   (true σ² = 1)")      # ≈ 0.8 and ≈ 1.0

# --- Chebyshev is loose but valid
for k in (1.5, 2, 3):
    emp = np.mean(np.abs(Z - Z.mean()) >= k * Z.std())
    print(f"k={k}: empirical {emp:.4f} ≤ Chebyshev bound {1 / k ** 2:.4f}"); assert emp <= 1 / k ** 2

# --- catastrophic cancellation: E[X²] − μ² vs the two-pass formula
big = 1e9 + rng.normal(size=100_000)
naive = np.mean(big ** 2) - np.mean(big) ** 2
two_pass = np.mean((big - big.mean()) ** 2)
print("naive:", naive, " two-pass:", two_pass, " np.var:", big.var(), " (true ≈ 1)")

def welford(stream):
    n = 0; mean = 0.0; M2 = 0.0
    for x in stream:
        n += 1; d = x - mean; mean += d / n; M2 += d * (x - mean)
    return mean, M2 / (n - 1)
m, v = welford(big[:20_000]); assert np.isclose(v, big[:20_000].var(ddof=1), rtol=1e-6)

# --- indicator trick: expected fixed points of a random permutation is 1
fixed = np.mean([np.sum(rng.permutation(20) == np.arange(20)) for _ in range(40_000)]); print("E[#fixed points] ≈", fixed)

# --- expected loss and its sample estimate: accuracy has standard error sqrt(p(1-p)/n)
acc_true = 0.9; n_test = 1000
accs = np.array([(rng.random(n_test) < acc_true).mean() for _ in range(20_000)])
print("std of measured accuracy:", accs.std(ddof=1), " sqrt(p(1-p)/n) =", np.sqrt(acc_true * (1 - acc_true) / n_test))
```

### 8.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `E[g(X)] ≠ g(E[X])` assumed equal | Biased "average" of nonlinear transforms (e.g., mean of probabilities then log) | LOTUS; Jensen; transform first, then average, as the quantity of interest dictates |
| Adding standard deviations instead of variances | Wrong spread for sums | Add variances (if uncorrelated) |
| Ignoring covariance in `Var(X + Y)` | Understated/overstated variance | Include `2Cov(X, Y)` |
| `ddof=0` where an unbiased estimate is needed | Variance biased low (especially for small `n`) | `ddof=1`; state the convention |
| `E[X²] − μ²` on data with a large offset | Negative or wildly wrong variance | Two-pass or Welford |
| Assuming a mean exists | Sample mean never settles (Cauchy) | Check `∫|x|f < ∞`; use the median |
| Reporting a mean without a standard error | Differences taken at face value | `s/√n` (or the bootstrap, Module 12) |
| Treating `E[XY] = E[X]E[Y]` as general | Wrong for dependent variables | Needs uncorrelatedness |
| Averaging per-group means to get the overall mean with unequal group sizes | Wrong overall mean | Weight by group size |

### 8.6 ML link

- **Training is expected-loss minimization;** the sample average is the empirical risk (4C-05).
- **Standard error of a metric** `= σ/√n` (accuracy: `√(p(1−p)/n)`) drives every evaluation comparison (Module 12).
- **SGD gradient noise:** the mini-batch gradient's variance is `σ²/B` (Module 08 Lesson 4) because the batch mean has variance `σ²/B`.
- **Bias–variance decomposition** of squared error uses `Var` and `E` (Stage 5A-07, 4C-05).
- **Jensen** explains why the average of log-likelihoods differs from the log of the average (the ELBO, 4C-10).
- **Standardization** (`(x − μ)/σ`) uses these definitions with the right `ddof` (Module 14, Stage 5A-03).

### 8.7 Lab (75 min)

1. Compute `E`, `E[X²]`, `Var` of three discrete distributions exactly with `Fraction`; verify by simulation (with SE).
2. Linearity and `Var(X+Y)` with dependent variables; show `E[XY] ≠ E[X]E[Y]`.
3. Verify Jensen on three convex/concave functions and measure the gap.
4. `ddof` experiment: bias of the variance estimator vs sample size `n ∈ {2, 3, 5, 10, 50}`.
5. Numerical-stability experiment: offsets `10⁰, 10⁴, 10⁸, 10¹²` with the naive vs two-pass vs Welford formulas; find where the naive version fails.
6. Standard error experiment: verify `σ/√n` for three distributions and show the CLT-flavoured normality of the mean (preview of Module 11).

### Check yourself (Unit 8)

1. Is `E[X + Y] = E[X] + E[Y]` valid for dependent `X, Y`?
2. `Var(2X − 3)` if `Var(X) = 5`?
3. Why does `np.var` underestimate a population's variance for small samples by default?

**Reference answers:** (1) Yes, linearity needs no independence. (2) `4 · 5 = 20`. (3) `ddof=0` divides by `n`, which biases the estimate low by a factor `(n−1)/n`; `ddof=1` corrects this.

---

## Unit 9 — Covariance and correlation (`08-…md`)

### 9.1 Why ML needs this

Covariance describes how two quantities move together. The **covariance matrix** of a feature set is the object PCA decomposes (Module 03), the one whose near-singularity signals redundant features (Module 02 Lesson 9), and the one whitening inverts. Correlation is the most-reported (and most-misread) association measure in data analysis.

### 9.2 Intuition

If `X` tends to be above its mean exactly when `Y` is above its mean, they co-vary positively. Correlation rescales covariance to a unit-free number between `−1` and `1`, measuring how close the relationship is to a **straight line**. It says nothing about non-linear relationships or causation.

### 9.3 Mechanics

- **Covariance:** `Cov(X, Y) = E[(X − μₓ)(Y − μᵧ)] = E[XY] − μₓμᵧ`. Sign = direction of co-movement; magnitude depends on units. `Cov(X, X) = Var(X)`; `Cov(aX + b, cY + d) = ac·Cov(X, Y)`.
- **Variance of a combination:** `Var(aX + bY) = a²Var X + b²Var Y + 2ab·Cov(X, Y)`.
- **Pearson correlation:** `ρ = Cov(X, Y)/(σₓσᵧ) ∈ [−1, 1]` (Cauchy–Schwarz, Module 01). `|ρ| = 1` iff `Y = aX + b` exactly (`a ≠ 0`). **`ρ` is the cosine of the angle between the *centered* vectors** (Module 01, Module 04): `ρ = cos(x − x̄𝟙, y − ȳ𝟙)`.
- **What correlation misses:** `Y = X²` with `X` symmetric about 0 has `ρ = 0` yet is a deterministic function of `X`. **Independence ⇒ `Cov = 0`; `Cov = 0 ⇏` independence** (exception: jointly normal variables).
- **Sensitivity:** Pearson `ρ` is sensitive to outliers; **Spearman's rank correlation** is Pearson on the ranks and captures any *monotone* relationship (e.g., `Y = eˣ` has Spearman `1`, Pearson `< 1`).
- **Covariance matrix** of a vector `X ∈ ℝᵈ`: `Σ = E[(X − μ)(X − μ)ᵀ]`, `Σᵢⱼ = Cov(Xᵢ, Xⱼ)`, diagonal = variances. **Symmetric positive semidefinite** (`vᵀΣv = Var(vᵀX) ≥ 0`; Module 02 Lesson 3). Sample version: `Σ̂ = X_cᵀX_c/(n − 1)` with `X_c: (n, d)` centered.
- **NumPy pitfall:** `np.cov(X)` treats **rows as variables** by default (`rowvar=True`); for data `(n, d)` use `np.cov(X, rowvar=False)` or `np.cov(X.T)`; `ddof` defaults to 1 there (unlike `np.var`) `[VERIFY in the installed version]`. `np.corrcoef` has the same convention.
- **Correlation matrix** `R = D⁻¹ᐟ² Σ D⁻¹ᐟ²` (unit diagonal).
- **Rank limits:** `rank(Σ̂) ≤ min(d, n − 1)`: with `d ≥ n`, the sample covariance is singular; invert only with regularization/shrinkage (Module 02 Lesson 8, `[VERIFY]` shrinkage estimators).
- **PCA = eigendecomposition of `Σ`** (Module 03 Lesson 1): eigenvectors are principal axes, eigenvalues are variances along them.
- **Whitening:** `Z = X_c Σ^{−1/2}` has identity covariance (Module 03 Lesson 2: matrix functions via `eigh`).
- **Correlation ≠ causation:** confounders, selection, and colliders produce correlation without a causal effect (Lesson 4, Module 12 Lesson 7).
- **Correlation for evaluation:** correlation between predictions and targets is scale- and offset-invariant, so it hides systematic bias; report error metrics as well.

**Worked example:** `X ~ N(0,1)`, `Y = X + ε`, `ε ~ N(0, 0.5²)`: `Cov = 1`, `Var(Y) = 1.25`, `ρ = 1/√1.25 ≈ 0.894`.

### 9.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

# --- covariance from the definition vs np.cov; ddof
n = 1000; x = rng.normal(size=n); y = x + 0.5 * rng.normal(size=n)
cov_def = np.mean((x - x.mean()) * (y - y.mean()))                      # ddof=0
cov_np = np.cov(x, y)[0, 1]                                              # ddof=1 by default
assert np.isclose(cov_def * n / (n - 1), cov_np)
rho = np.corrcoef(x, y)[0, 1]; print("ρ =", rho, " expected ≈ 0.894")

# --- ρ is the cosine of the centered vectors (Module 01/04)
xc, yc = x - x.mean(), y - y.mean()
assert np.isclose(rho, xc @ yc / (np.linalg.norm(xc) * np.linalg.norm(yc)))

# --- Var(aX + bY) = a²VarX + b²VarY + 2ab Cov
a_, b_ = 2.0, -3.0
assert np.isclose(np.var(a_ * x + b_ * y, ddof=1), a_**2 * x.var(ddof=1) + b_**2 * y.var(ddof=1) + 2 * a_ * b_ * cov_np)

# --- correlation only sees LINEAR association
u = rng.normal(size=n); v = u ** 2
print("Pearson(X, X²) =", np.corrcoef(u, v)[0, 1], "(≈ 0, yet v = u² exactly)")

# --- Spearman = Pearson of the ranks; captures monotone relationships and resists outliers
def ranks(a): return np.argsort(np.argsort(a)).astype(float)             # no ties for continuous data
spearman = lambda a, b: np.corrcoef(ranks(a), ranks(b))[0, 1]
t = rng.normal(size=n); e = np.exp(t)
print("Pearson(t, e^t) =", np.corrcoef(t, e)[0, 1], " Spearman =", spearman(t, e))             # < 1 vs exactly 1
xo = np.r_[x, 50.0]; yo = np.r_[y, -50.0]                                                          # one outlier
print("with 1 outlier: Pearson", np.corrcoef(xo, yo)[0, 1], " Spearman", spearman(xo, yo))

# --- covariance matrix: rows-as-variables pitfall, symmetry, PSD
X = rng.normal(size=(500, 4)) @ rng.normal(size=(4, 4))                    # (n, d), correlated features
Sigma = np.cov(X, rowvar=False)                                            # (d, d) — correct
wrong = np.cov(X)                                                          # (n, n) — treats samples as variables!
print(Sigma.shape, wrong.shape)
assert np.allclose(Sigma, Sigma.T) and np.all(np.linalg.eigvalsh(Sigma) >= -1e-10)
Xc = X - X.mean(axis=0); assert np.allclose(Sigma, Xc.T @ Xc / (len(X) - 1))

# --- PCA via the covariance matrix: eigenvalues are variances along principal axes
w, V = np.linalg.eigh(Sigma); order = np.argsort(w)[::-1]; w, V = w[order], V[:, order]
assert np.allclose(np.var(Xc @ V, axis=0, ddof=1), w)

# --- whitening: Σ^{-1/2} makes the covariance the identity
W = V @ np.diag(1 / np.sqrt(w)) @ V.T; Z = Xc @ W
assert np.allclose(np.cov(Z, rowvar=False), np.eye(4), atol=1e-10)

# --- when d ≥ n the sample covariance is singular
Xs = rng.normal(size=(8, 20)); print("rank of sample covariance (n=8, d=20):", np.linalg.matrix_rank(np.cov(Xs, rowvar=False)), "(≤ n−1 = 7)")

# --- correlation matrix from the covariance matrix
D = np.sqrt(np.diag(Sigma)); R = Sigma / np.outer(D, D); assert np.allclose(R, np.corrcoef(X, rowvar=False)) and np.allclose(np.diag(R), 1)

# --- confounding: correlation without causation (synthetic)
Zc = rng.normal(size=n); Xcf = Zc + 0.3 * rng.normal(size=n); Ycf = Zc + 0.3 * rng.normal(size=n)       # Z causes both
print("corr(X, Y) =", np.corrcoef(Xcf, Ycf)[0, 1], " but X does not cause Y; regress out Z:",
      np.corrcoef(Xcf - np.polyval(np.polyfit(Zc, Xcf, 1), Zc), Ycf - np.polyval(np.polyfit(Zc, Ycf, 1), Zc))[0, 1])
```

### 9.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `np.cov(X)` on `(n, d)` data without `rowvar=False` | An `(n, n)` matrix of nonsense | Assert the output shape `(d, d)` |
| Reading `ρ ≈ 0` as independence | Missed nonlinear dependence | Plot; use rank/nonlinear measures |
| Reading correlation as causation | Wrong decisions | Consider confounders/colliders; run experiments (Module 12) |
| Pearson with outliers | One point flips the sign | Spearman or a robust method; inspect outliers |
| Comparing covariances across variables with different units | Meaningless magnitudes | Use the correlation matrix |
| Inverting a sample covariance when `d ≥ n` or features are collinear | `LinAlgError` or enormous values | Regularize/shrink; drop features (Module 02) |
| Mixing `ddof` conventions across libraries | Slightly different numbers | State and assert the convention |
| Using correlation between predictions and targets as the only metric | Misses bias and scale errors | Also report MAE/RMSE |
| Not centering before PCA via `XᵀX` | First component dominated by the mean | Center (Module 03 Lesson 3) |

### 9.6 ML link

- **PCA** diagonalizes the covariance matrix (Module 03, 4C-01, Stage 5B-05).
- **Multicollinearity:** high feature correlation makes `XᵀX` ill-conditioned (Module 02 Lesson 9, Module 14).
- **Whitening/standardization** in preprocessing (Stage 5A-03) and in normalization layers (4C-07).
- **Multivariate Gaussians** are parameterized by `Σ` (4C-04); Gaussian discriminant analysis and Gaussian processes need `Σ⁻¹` and regularization.
- **Feature selection by correlation** removes redundant features but cannot see nonlinear relations (Stage 5B-07).
- **Correlation vs causation** in feature-importance interpretation (Stage 5B-07, 5B-10).

### 9.7 Lab (75 min)

1. Verify covariance from the definition, `np.cov` (with the `ddof` and `rowvar` conventions), and the cosine-of-centered-vectors identity.
2. Build five datasets (linear, quadratic, monotone-nonlinear, clustered, one-outlier) with the same Pearson `ρ` ≈ 0.8 or a very different one; compute Pearson and Spearman; plot.
3. Covariance-matrix tasks: shape and symmetry assertions, PSD check, PCA via `eigh`, whitening to the identity.
4. Rank experiment: `d` fixed at 20, `n ∈ {5, 10, 20, 40, 200}`; plot the rank and the condition number of the sample covariance; apply shrinkage `(1−λ)Σ̂ + λ·(tr Σ̂/d)I` `[VERIFY: estimator]` and show the improvement.
5. Confounding demonstration: generate a common cause, show the spurious correlation, then remove it by partialling out the confounder.

### Check yourself (Unit 9)

1. Which function of `Cov` gives correlation, and what range does it have?
2. Why does `np.cov(X)` on an `(n, d)` array return the wrong thing?
3. Name the geometric meaning of Pearson correlation.

**Reference answers:** (1) `ρ = Cov/(σₓσᵧ)`, in `[−1, 1]`. (2) It treats rows as variables by default; you need `rowvar=False` (or transpose). (3) The cosine of the angle between the centered data vectors.

---

## Unit 10 — Practice question bank (`practice-questions.md`)

### 10.1 Structure

About 55 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 14 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, "predict the simulation", runnable code, and ML judgement.

### 10.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 10.3 Seed items

**Q1 [L1] Axioms.** State the three axioms. → Non-negativity; `P(Ω) = 1`; additivity for disjoint events.
**Q2 [L2] Complement.** `P(at least one head in 4 fair flips)`? → `1 − 1/16 = 15/16`.
**Q3 [L2] Conditional.** Two dice; `P(sum = 8 | first die = 3)`? → `1/6`.
**Q4 [L2] Bayes.** Prevalence 2%, sensitivity 95%, specificity 90%. PPV? → `0.019/(0.019 + 0.098) = 0.162`.
**Q5 [L2] Independence.** Two fair dice: are `{first even}` and `{sum even}` independent? → Yes: `P(A)=1/2`, `P(B)=1/2`, `P(A∩B)=1/4`.
**Q6 [L2] Expectation.** Expected number of heads in 10 flips with `p = 0.3`? → `3`.
**Q7 [L2] Variance.** `Var(X) = 4`, `Var(Y) = 9`, independent. `Var(2X − Y)`? → `4·4 + 9 = 25`.
**Q8 [L2] Correlation.** `Cov = 3`, `σₓ = 2`, `σᵧ = 3`. `ρ`? → `0.5`.
**Q9 [L2] CDF.** `X ~ Exp(λ = 2)`: `P(X > 1)`? → `e⁻² ≈ 0.135`.
**Q10 [L3] Debug.** A classifier is "95% accurate" but only 12% of its positive predictions are correct. What is likely going on? → Rare positive class (low prevalence) with a modest false-positive rate: base-rate effect; compute PPV.
**Q11 [L3] Debug.** `np.cov(X)` for `X.shape == (1000, 5)` returns a `(1000, 1000)` matrix. → `rowvar=True` default; use `rowvar=False`.
**Q12 [L3] Debug.** A naive-Bayes spam filter outputs `0.0` and `0.0` for both classes on a long email. → Underflow of the raw product; use log-probabilities and normalize with log-sum-exp.
**Q13 [L3] Debug.** Variance of a column of large timestamps comes out negative. → `E[X²] − μ²` cancellation; use the two-pass formula or `np.var`.
**Q14 [L3] Analysis.** Treatment B beats A in every subgroup but A beats B overall. Explain. → Simpson's paradox: unequal subgroup sizes (confounded allocation); stratify or adjust.
**Q15 [L3] Analysis.** 100k samples from an MCMC chain with lag-1 autocorrelation 0.95: how many independent draws? → About `100 000 × 0.05/1.95 ≈ 2 560`.
**Q16 [L3] Analysis.** `corr(X, Y) = 0.02` but a scatterplot shows a clear parabola. → Correlation measures linear association only.
**Q17 [L4] Design.** You must report the accuracy of a model on 800 test items with confidence. → Report `p̂ ± 1.96√(p̂(1−p̂)/n)` or a Wilson interval, state `n`, and compare models on the same items with a paired method (Module 12).
**Q18 [L4] Design.** Your deployed fraud rate drops from 5% to 0.5%; the classifier was trained at 5%. What changes and what do you do? → Posterior probabilities and precision shift; apply prior-shift correction or recalibrate; re-tune the threshold; monitor prevalence.
**Q19 [L4] Design.** You need to decide whether two features can both be kept. → Compute the correlation matrix and condition number, check a nonlinear dependence measure, and decide with a downstream metric (Module 02 Lesson 9).

### 10.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Sample spaces, axioms | 2 | 2 | 1 | 0 |
| Conditional probability | 2 | 2 | 2 | 0 |
| Total probability, Bayes | 2 | 3 | 3 | 2 |
| Independence | 2 | 2 | 2 | 1 |
| Random variables, PMF/PDF/CDF | 3 | 3 | 2 | 0 |
| Expectation, variance | 2 | 3 | 3 | 1 |
| Covariance, correlation | 1 | 2 | 3 | 1 |

### Check yourself (Unit 10)

1. Why does the seed set include a base-rate item and a Simpson's-paradox item?
2. Which items need runnable code?

**Reference answers:** (1) They are the two most frequent real-world probability errors in ML reporting. (2) All L3 items and any whose answer depends on floating-point or simulation behaviour.

---

## Unit 11 — Project index (`Projects/README.md`)

### 11.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Probability simulations | Exact-vs-simulated agreement, error bars, convergence, statistical validation of a simulator | 1–4, 7 | 6–7 h |
| 2 | Bayes spam filter by hand | Bayes' theorem, naive Bayes from scratch, smoothing, log-space, prior shift, calibration | 2–4 | 7–8 h |

Order: 1 → 2 (Project 2 reuses Project 1's validation helpers: confidence intervals and the "assert within `k·SE`" pattern). Outputs feed `mlmath/prob.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D9) and notebook `09_probability.ipynb`. Project 2's classifier is reused in Stage 5A-10 and in Module 12 (confidence intervals on accuracy).

### 11.2 Data policy

**No downloads.** Project 1 uses only simulated experiments. Project 2 uses a small hand-written corpus defined in code; you may additionally evaluate on any text dataset you already have locally (keep it out of the repository and out of tests) `[VERIFY: licence of any data you add]`.

### 11.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (exact vs simulated agreement; hand calculation vs code) | 30 |
| Failure-mode handling (underflow, zero counts, tiny `N`, degenerate cases) | 15 |
| Reproducibility (seeded, pinned, clean venv, no downloads) | 15 |
| Explanation and statistical honesty (standard errors, coverage checks, scoped claims) | 15 |
| Code quality (types, docstrings, no hidden state) | 15 |
| ML connection paragraph | 10 |

### 11.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 11)

1. What does Project 2 reuse from Project 1?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The confidence-interval helpers and the "agree within `k` standard errors" validation pattern. (2) D9 (`mlmath/prob.py`).

---

## Unit 12 — Project: Probability simulations (`Projects/01-…md`)

### 12.1 Brief

Build `probsim`: a vectorized Monte Carlo toolkit and a suite of classic probability experiments (dice, birthday problem, Monty Hall, coupon collector, conditional probability by rejection), each validated against an exact result with a stated tolerance, plus a statistical audit of the toolkit itself (confidence-interval coverage, `1/√N` convergence, seed reproducibility).

**Industry framing:** simulations are how ML teams sanity-check probability claims and estimate quantities with no closed form. A simulator is only useful if it ships with its own validation: error bars, coverage checks, and exact-answer regression tests.

### 12.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Estimator | `estimate_probability(event_fn, sampler, N, seed)` returning `p̂`, standard error, normal and Wilson intervals, `N`; vectorized samplers; seeded |
| R2 | Exact references | Exact answers via `fractions` or closed forms for every experiment |
| R3 | Dice | Distribution of the sum of 2–4 dice; exact via convolution/enumeration; `P(sum ≥ k)`; compare with simulation (χ²-style or `4·SE` check per outcome) |
| R4 | Birthday problem | Exact complement formula vs simulation for `n = 5…60`; generalize to `k`-fold matches (stretch) and to non-uniform birthdays (show probability *increases*) |
| R5 | Monty Hall | Strategies *stay*, *switch*, *random*; simulate with `N = 10⁶`; exact `1/3`, `2/3`, `1/2`; a variant with 100 doors |
| R6 | Coupon collector | Expected draws to collect `n` coupons `n·Hₙ` vs simulation for `n ∈ {5, 10, 50}`; distribution of the stopping time (tail behaviour) |
| R7 | Conditional probability by rejection | `P(A | B)` estimated from the accepted samples; effective `N` shown (accepted count) and its effect on the standard error; compare to the exact value in a card-drawing example |
| R8 | Law of total probability / Bayes check | Simulate the diagnostic-test model; compare PPV with the formula; show how SE depends on the number of positives |
| R9 | Convergence study | Error vs `N` (log-log) for three experiments; fitted slope ≈ `−½`; report your numbers |
| R10 | Coverage audit | For each interval type, the empirical coverage over ≥ 2,000 repetitions at several `(p, N)` combos, including `p` near 0 and `N` small; the normal interval's failure mode is shown |
| R11 | Reproducibility | Same seed → identical results; different seeds → independent; use `SeedSequence.spawn` for parallel streams `[VERIFY: API]` |
| R12 | Report | `REPORT.md`: every simulation with exact value, estimate, SE, and the agreement check; coverage tables; convergence plot |

### 12.3 Layout and starter

```
probsim/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/probsim/{__init__,estimator,experiments,exact,audit}.py
├── tests/{test_estimator,test_experiments,test_audit}.py
├── notebooks/09_probability_simulations.ipynb
└── results/
```

```python
# src/probsim/estimator.py
from __future__ import annotations
import math
import numpy as np

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n; den = 1 + z * z / n; ctr = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return ctr - half, ctr + half

def estimate_probability(event_fn, sampler, N: int, seed: int = 0) -> dict:
    """sampler(rng, N) -> array of N outcomes; event_fn(outcomes) -> boolean array of length N."""
    rng = np.random.default_rng(seed)
    hits = np.asarray(event_fn(sampler(rng, N)), dtype=bool)
    if hits.shape != (N,): raise ValueError(f"event_fn must return {N} booleans, got shape {hits.shape}")
    k = int(hits.sum()); p = k / N; se = math.sqrt(p * (1 - p) / N)
    return {"p": p, "se": se, "N": N, "k": k, "normal": (p - 1.96 * se, p + 1.96 * se), "wilson": wilson(k, N)}

def agrees(est: dict, exact: float, k_se: float = 4.0) -> bool:
    return abs(est["p"] - exact) <= k_se * max(est["se"], 1 / est["N"])
```

```python
# src/probsim/experiments.py
import math
import numpy as np

def two_dice_sum(rng, N):          return rng.integers(1, 7, size=(N, 2)).sum(axis=1)

def birthday_exact(n, days=365):   return 1 - math.prod((days - i) / days for i in range(n))
def birthday_sampler(n, days=365):
    def sampler(rng, N): return np.sort(rng.integers(0, days, size=(N, n)), axis=1)
    return sampler
def has_match(sorted_birthdays):   return np.any(np.diff(sorted_birthdays, axis=1) == 0, axis=1)

def monty_hall(strategy, N, seed=0):
    rng = np.random.default_rng(seed)
    car, pick = rng.integers(0, 3, N), rng.integers(0, 3, N)
    if strategy == "stay":   return pick == car
    if strategy == "switch": return pick != car            # the host always reveals a goat, so switching wins iff the first pick was wrong
    if strategy == "random": return np.where(rng.random(N) < 0.5, pick == car, pick != car)
    raise ValueError(strategy)

def coupon_collector(n, trials, seed=0):
    rng = np.random.default_rng(seed); out = np.empty(trials, dtype=int)
    for t in range(trials):
        seen = np.zeros(n, bool); count = 0; draws = 0
        while count < n:
            c = rng.integers(0, n); draws += 1
            if not seen[c]: seen[c] = True; count += 1
        out[t] = draws
    return out
def coupon_expected(n): return n * sum(1 / k for k in range(1, n + 1))
```

```python
# tests/test_experiments.py
import math, numpy as np
from probsim.estimator import estimate_probability, agrees
from probsim.experiments import *

def test_two_dice_seven():
    est = estimate_probability(lambda s: s == 7, two_dice_sum, 200_000, seed=1)
    assert agrees(est, 1 / 6)

def test_birthday_23():
    est = estimate_probability(has_match, birthday_sampler(23), 100_000, seed=2)
    assert agrees(est, birthday_exact(23)) and abs(birthday_exact(23) - 0.5073) < 1e-3

def test_monty_hall_strategies():
    N = 400_000
    for strat, exact in (("stay", 1 / 3), ("switch", 2 / 3), ("random", 1 / 2)):
        w = monty_hall(strat, N, seed=3); p = w.mean(); se = math.sqrt(p * (1 - p) / N)
        assert abs(p - exact) < 4 * se, strat

def test_coupon_collector_mean():
    x = coupon_collector(10, 4000, seed=4); se = x.std(ddof=1) / math.sqrt(len(x))
    assert abs(x.mean() - coupon_expected(10)) < 4 * se

def test_estimator_rejects_bad_event_shape():
    import pytest
    with pytest.raises(ValueError):
        estimate_probability(lambda s: np.array([True]), two_dice_sum, 100)
```

```python
# tests/test_audit.py
import numpy as np
from probsim.estimator import wilson

def coverage(p, N, reps=3000, seed=0):
    rng = np.random.default_rng(seed); cn = cw = 0
    for _ in range(reps):
        k = rng.binomial(N, p); ph = k / N; se = np.sqrt(ph * (1 - ph) / N)
        cn += (ph - 1.96 * se <= p <= ph + 1.96 * se); lo, hi = wilson(k, N); cw += (lo <= p <= hi)
    return cn / reps, cw / reps

def test_wilson_covers_better_for_extreme_p_small_n():
    cn, cw = coverage(0.02, 100)
    assert cw > cn and cw > 0.92                              # [VERIFY] thresholds against your own run
```

`[VERIFY]` Confirm the coverage thresholds by running the audit: the normal interval's coverage at `p = 0.02, N = 100` is expected to be clearly below 95%, but record your measured values before asserting numeric bounds.

### 12.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R2 | Estimator returns all fields; `agrees()` passes on dice and birthday against exact values; malformed inputs raise clear errors |
| M2 | R3–R5 | Exact vs simulated tables for dice, birthday (`n = 5…60`), Monty Hall (3 and 100 doors) all within `4·SE` |
| M3 | R6–R8 | Coupon-collector means within `4·SE`; rejection-sampling estimates with the accepted count reported; Bayes PPV matches the formula within `4·SE` |
| M4 | R9–R10 | Convergence slope within `0.1` of `−0.5`; coverage tables over ≥ 6 `(p, N)` combinations with the normal interval's failure documented |
| M5 | R11–R12 | Reproducibility tests pass; `REPORT.md` regenerated by one script; every claim cites an exact value, an estimate, and an SE |

### 12.5 Statistical-honesty requirements

- Every simulated number appears as **estimate ± SE with `N` and the seed**; never as a bare number.
- State the **tolerance rule** (`k·SE`) and justify `k`; with many comparisons expect a few misses (the union bound/Bonferroni, Lesson 1).
- Report the **coverage of your own intervals**, not just the nominal level.
- Include at least one case where simulation is a **poor tool** (very rare events: `p ≈ 10⁻⁶` with `N = 10⁵`) and explain why (huge relative error; importance sampling needed, 4C-04).

### 12.6 Failure modes to demonstrate

Unseeded runs; unvectorized loops that are 100× slower; birthday simulation with a bug counting adjacent only; Monty Hall where the host's choice is simulated incorrectly (host may reveal the car); conditional estimates from too few accepted samples; normal intervals at `p̂ = 0`; comparing a simulated probability to an exact one with no standard error; `N` too small for the claim.

### 12.7 Stretch goals

1. Antithetic variates or stratified sampling for one experiment, with a measured variance reduction.
2. Importance sampling for a rare-event probability (e.g., sum of 10 dice ≥ 55), with the weights' effective sample size.
3. A random walk / gambler's ruin experiment with exact solution.
4. Parallel simulation with `SeedSequence.spawn` and a reproducibility test across worker counts `[VERIFY: API]`.
5. Property-based tests (`hypothesis`) that the estimator's interval contains the exact value at the nominal rate.

### 12.8 ML connection (README prompt)

Explain how each experiment mirrors an ML task: birthday ↔ collision probability in hashing/deduplication, Monty Hall ↔ updating on information, coupon collector ↔ coverage of a categorical vocabulary by random sampling, rejection sampling ↔ conditioning on a filter (selection bias), the coverage audit ↔ validating a metric's confidence interval.

### Check yourself (Unit 12)

1. Why is the Wilson interval preferred over the normal interval for small `p` and `N`?
2. Why does conditioning by rejection inflate the standard error?
3. In Monty Hall, why does switching win with probability `2/3`?

**Reference answers:** (1) The normal interval can have zero width or poor coverage near `0`/`1`; Wilson keeps close to nominal coverage. (2) Only the accepted samples inform the estimate, so the effective sample size is the accepted count, not `N`. (3) The first pick is wrong with probability `2/3`, and then the host's reveal leaves the car behind the remaining door.

---

## Unit 13 — Project: Bayes spam filter by hand (`Projects/02-…md`)

### 13.1 Brief

Build `bayesspam`: a multinomial **Naive Bayes** spam classifier from scratch, with every step derived by hand first (`DERIVATION.md`), implemented in log space with additive smoothing, evaluated honestly (confusion matrix, precision/recall, calibration), and stress-tested against **prior shift**, **zero counts**, **underflow**, and **violated conditional independence**.

**Industry framing:** Naive Bayes is a standard baseline and a perfect vehicle for learning Bayes' theorem, smoothing, and calibration. The deliverable includes the paper derivation, the code, an agreement check between the two, and an honest account of where the model's probabilities cannot be trusted.

### 13.2 Data policy

The corpus is a **small synthetic collection of short messages written in code** (about 30 spam-like and 30 ham-like), so tests are deterministic and no data is downloaded. Optionally evaluate on any text dataset you already have locally; keep it out of the repository and tests `[VERIFY: licence]`.

### 13.3 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Hand derivation | `DERIVATION.md`: Bayes' theorem for two classes, the conditional-independence factorization, the smoothed estimator, the log-space decision rule, and a **fully worked posterior** for 2 short messages on a 6-message corpus, done on paper before coding |
| R2 | Tokenizer and vocabulary | Lower-casing, whitespace/punctuation splitting, out-of-vocabulary policy (ignore at prediction), documented |
| R3 | Training | Class priors; per-class word counts; smoothed likelihoods `(count + α)/(total + α·V)`; stored as log-probabilities |
| R4 | Prediction | `predict_log_joint`, `predict_proba` (normalize with log-sum-exp), `predict`; a `prior=` override for prior-shift experiments |
| R5 | Agreement checks | (a) Posterior matches the hand calculation from R1 to `1e-12`; (b) log-space result equals raw-product result on short messages; (c) posteriors sum to 1; (d) a brute-force Bayes computation by enumerating the training counts agrees |
| R6 | Underflow demonstration | Show the raw product → `0.0` for a 1,500-token message while the log version is finite; show log-sum-exp normalization |
| R7 | Smoothing study | `α ∈ {0, 0.01, 0.1, 1, 10}`: effect on accuracy and log-loss, and the zero-count failure at `α = 0`. **The failure is not automatic:** on the larger overlapping synthetic corpus (420 training messages) `α = 0` produced 0 errors in 180 test messages and accuracy differed by only 0.006 across the sweep. Construct messages that expose it (one word never seen in spam plus one never seen in ham → both scores `−∞`), and also show the *silent* one-sided case (a word unseen in only one class forces the other class with probability exactly 1.0) |
| R8 | Evaluation | Stratified train/test split (seeded); confusion matrix; accuracy, precision, recall, F1, log-loss; standard errors/Wilson intervals on accuracy |
| R9 | Calibration | Reliability table (predicted-probability bins vs observed spam rate); expected calibration error. In a seeded run the filter was close to calibrated on the synthetic corpus (e.g., bin `[0.8, 1.0)`: mean prediction 0.982, observed 0.975) because independence holds nearly by construction; report that honestly and show over-confidence where it actually appears (R11: duplicated features) |
| R10 | Prior-shift experiment | Train at one spam rate, test at others (`5%, 30%, 50%, 80%`); precision and calibration with and without the odds correction `p′(y)/p(y)` |
| R11 | Violated independence | Duplicate informative words into extra features; show the posterior becoming more extreme while accuracy barely changes; relate to Lesson 4's demo |
| R12 | Bernoulli vs multinomial | Implement the Bernoulli variant (word presence/absence, including absent-word likelihoods) and compare on the corpus |
| R13 | Report | `REPORT.md`: derivation agreement, underflow, smoothing, evaluation with intervals, calibration, prior shift, independence violation, a "when not to trust these probabilities" section |

### 13.4 Layout and starter

```
bayesspam/
├── pyproject.toml  requirements.txt  README.md  DERIVATION.md  REPORT.md
├── src/bayesspam/{__init__,corpus,model,evaluate,variants}.py
├── tests/{test_model,test_agreement,test_underflow,test_evaluate}.py
├── notebooks/09_bayes_spam_filter.ipynb
└── results/
```

```python
# src/bayesspam/corpus.py
import numpy as np

SPAM_W = ["free", "winner", "prize", "cash", "offer", "click", "now", "urgent", "claim", "credit", "deal", "bonus"]
HAM_W  = ["meeting", "tomorrow", "project", "lunch", "report", "team", "schedule", "thanks", "review", "call", "draft", "notes"]
COMMON = ["the", "a", "to", "you", "we", "please", "is", "for", "on", "and"]

def make_corpus(n_spam=30, n_ham=30, seed=0, length=8):
    """Synthetic messages: mostly class-specific words with some shared words (class overlap keeps it non-trivial)."""
    g = np.random.default_rng(seed); docs, labels = [], []
    for label, n, own, other in (("spam", n_spam, SPAM_W, HAM_W), ("ham", n_ham, HAM_W, SPAM_W)):
        for _ in range(n):
            words = [str(g.choice(own)) if r < 0.55 else (str(g.choice(other)) if r < 0.65 else str(g.choice(COMMON)))
                     for r in g.random(length)]
            docs.append(" ".join(words)); labels.append(label)
    idx = g.permutation(len(docs)); return [docs[i] for i in idx], [labels[i] for i in idx]
```

```python
# src/bayesspam/model.py
import math
from collections import Counter

def tokenize(text): return [w for w in text.lower().split() if w]

class NaiveBayes:
    def __init__(self, alpha: float = 1.0): self.alpha = alpha
    def fit(self, docs, labels):
        self.classes = sorted(set(labels)); n = len(labels)
        self.vocab = sorted({w for d in docs for w in tokenize(d)}); V = len(self.vocab)
        self.log_prior = {c: math.log(labels.count(c) / n) for c in self.classes}
        self.counts = {c: Counter() for c in self.classes}
        for d, l in zip(docs, labels): self.counts[l].update(tokenize(d))
        self.total = {c: sum(self.counts[c].values()) for c in self.classes}
        self.log_lik = {}
        for c in self.classes:
            den = self.total[c] + self.alpha * V
            self.log_lik[c] = {w: (math.log((self.counts[c][w] + self.alpha) / den) if (self.counts[c][w] + self.alpha) > 0 else -math.inf)
                               for w in self.vocab}
        return self
    def log_joint(self, text, log_prior=None):
        lp = self.log_prior if log_prior is None else log_prior
        toks = [w for w in tokenize(text) if w in self.log_lik[self.classes[0]]]       # ignore out-of-vocabulary tokens
        return {c: lp[c] + sum(self.log_lik[c][w] for w in toks) for c in self.classes}
    def predict_proba(self, text, prior=None):
        lp = None if prior is None else {c: math.log(prior[c]) for c in self.classes}
        lj = self.log_joint(text, lp); m = max(lj.values())
        if m == -math.inf: raise ValueError("all class scores are -inf (zero likelihood with alpha=0)")
        z = {c: math.exp(v - m) for c, v in lj.items()}; s = sum(z.values())            # log-sum-exp normalization
        return {c: v / s for c, v in z.items()}
    def predict(self, text, prior=None):
        p = self.predict_proba(text, prior); return max(p, key=p.get)
```

```python
# tests/test_agreement.py
import math
import pytest
from bayesspam.model import NaiveBayes, tokenize

TINY_DOCS = ["free cash now", "free prize", "meeting tomorrow", "project meeting review", "cash prize now", "lunch tomorrow"]
TINY_LABELS = ["spam", "spam", "ham", "ham", "spam", "ham"]

def test_matches_hand_calculation_on_tiny_corpus():
    m = NaiveBayes(alpha=1.0).fit(TINY_DOCS, TINY_LABELS)
    # hand values (derive them in DERIVATION.md): priors 1/2 each; spam tokens: free×2, cash×2, now×2, prize×2 → total 8
    # ham tokens: meeting×2, tomorrow×2, project×1, review×1, lunch×1 → total 7; vocabulary V = 9
    V = len(m.vocab); assert V == 9
    p_free_spam = (2 + 1) / (8 + 9); p_free_ham = (0 + 1) / (7 + 9)
    expected_spam = 0.5 * p_free_spam; expected_ham = 0.5 * p_free_ham
    post_spam = expected_spam / (expected_spam + expected_ham)
    assert m.predict_proba("free")["spam"] == pytest.approx(post_spam, rel=1e-12)

def test_probabilities_sum_to_one_and_log_equals_raw_product():
    m = NaiveBayes(1.0).fit(TINY_DOCS, TINY_LABELS); msg = "free cash meeting"
    p = m.predict_proba(msg); assert sum(p.values()) == pytest.approx(1.0)
    raw = {c: math.exp(m.log_prior[c]) * math.prod(math.exp(m.log_lik[c][w]) for w in tokenize(msg)) for c in m.classes}
    z = sum(raw.values()); assert p["spam"] == pytest.approx(raw["spam"] / z, rel=1e-12)

def test_zero_alpha_zero_likelihood_is_handled():
    m = NaiveBayes(alpha=0.0).fit(TINY_DOCS, TINY_LABELS)
    with pytest.raises(ValueError): m.predict_proba("free meeting")             # 'free' never appears in ham and 'meeting' never in spam
```

```python
# tests/test_underflow.py
import math, numpy as np
from bayesspam.model import NaiveBayes
from bayesspam.corpus import make_corpus

def test_log_space_survives_a_1500_token_message():
    docs, labels = make_corpus(seed=1); m = NaiveBayes(1.0).fit(docs, labels)
    msg = " ".join(["free winner prize cash offer"] * 300)                    # 1,500 tokens
    raw = math.prod(math.exp(m.log_lik["spam"][w]) for w in msg.split()); assert raw == 0.0
    p = m.predict_proba(msg); assert abs(sum(p.values()) - 1) < 1e-12 and p["spam"] > 0.99
```

`[VERIFY]` Confirm the tiny-corpus token counts in the hand-calculation test (spam total 8, ham total 7, `V = 9`) by running it; if they differ, fix the comments and the derivation, not the assertion's logic.

### 13.5 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1 | `DERIVATION.md` complete, with a worked posterior, **before** any model code is written (check the commit order) |
| M2 | R2–R5 | All agreement tests pass: hand calculation to `1e-12`, log vs raw product, posteriors sum to 1, brute-force enumeration |
| M3 | R6–R7 | Underflow demonstration; smoothing sweep table; explicit messages that trigger the `α = 0` zero-likelihood failure (both the error and the silent one-sided case) and the effect of `α` on log-loss |
| M4 | R8–R9 | Evaluation with Wilson intervals on accuracy; reliability table and ECE reported |
| M5 | R10–R12 | Prior-shift table (with/without correction); independence-violation experiment; Bernoulli vs multinomial comparison |
| M6 | R13 | `REPORT.md` regenerated by one script; each claim cites a table with `N`, seed, split |

### 13.6 Statistical-honesty requirements

- Report accuracy with an interval and the **test-set size**; with ~60 messages the intervals are wide; say so and, if conclusions depend on small differences, increase the synthetic corpus or use repeated seeds.
- Calibrate **and** discriminate: report log-loss and a reliability table, not accuracy alone.
- Report the prior-shift results for several test prevalences, and state that the correction assumes `p(x|y)` is unchanged (which is true by construction in the synthetic data and not guaranteed in real data).
- State clearly that the synthetic corpus makes the **independence assumption approximately true by construction**, so real-text performance cannot be inferred.

### 13.7 Failure modes to demonstrate

Raw-product underflow; `α = 0` zero-likelihood; out-of-vocabulary tokens handled inconsistently between training and prediction; features duplicated (over-confidence); priors estimated from a test set with different prevalence; probability reported without calibration; train/test leakage by splitting after de-duplication incorrectly; mixing Bernoulli and multinomial likelihoods.

### 13.8 Stretch goals

1. Compare with scikit-learn's `MultinomialNB` if installed (smoothing and prior conventions) and document differences `[VERIFY]`.
2. Log-odds feature attribution: list the words with the highest `log P(w|spam) − log P(w|ham)` and explain each contribution to a particular message.
3. TF-IDF weighting or binary features; compare with counts.
4. Temperature/Platt scaling to calibrate the posteriors and measure ECE before and after `[VERIFY: method]`.
5. Bootstrap confidence intervals for precision and recall (Module 12 preview).

### 13.9 ML connection (README prompt)

Explain, using your results: why naive Bayes can classify well yet be badly calibrated, why smoothing is a modelling decision rather than a hack, how prior shift changes precision, and what you would check before deploying a spam filter (prevalence drift, adversarial adaptation, calibration, leakage).

### Check yourself (Unit 13)

1. Why write the derivation before the code?
2. What breaks if `α = 0` and a word appears in only one class?
3. Why can naive Bayes be accurate but poorly calibrated?

**Reference answers:** (1) It gives you a specification to test against: a mismatch between hand and code points to a specific error. (2) That word's likelihood in the other class is 0, so every message containing it gets a zero (log `−∞`) score for that class. (3) Classification only needs the correct *ranking* of class scores, while correlated features multiply evidence and push the posterior toward 0 or 1, making probabilities overconfident.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 8 lessons, 2 projects, 13 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 10–14, 4C-04/05/10, and Stage 5 pointers (5A-03/05/06/07/10, 5B-03/04/07/10, 5C-08/09, 5D-12) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: AR(1) effective-sample-size formula, Wilson/Clopper–Pearson formulas, Glivenko–Cantelli statement, `np.var`/`np.cov`/pandas `ddof` defaults in the pinned versions, shrinkage-estimator definition, Platt scaling.
4. `[VERIFY]` All printed numerical results (simulated probabilities, coverage rates, effective sample sizes, calibration values) by running the code; report your own numbers rather than quoting any ratio. The AR(1) variance-inflation formula `(1+ρ)/(1−ρ)` is asymptotic: at `n = 400`, `ρ = 0.9` the measured ratio was 18.3 against 19.0.
5. `[VERIFY]` Starter code was run (NumPy 2.3, SymPy 1.14): every lesson snippet executed; all 6 `probsim` and all 4 `bayesspam` tests passed. Measured in those runs (seeded): (a) simulated vs exact probabilities agreed within `4·SE` for dice, birthday (`n = 23`: exact 0.5073), Monty Hall, coupon collector, and card conditioning; (b) `|error|` vs `N` for the birthday experiment fitted a log-log slope of −0.497; (c) interval coverage at `p = 0.02, N = 100`: normal 0.865, Wilson 0.952; at `p = 0.5, N = 400` both 0.954; Wilson was *below* nominal at `p = 0.3, N = 100` (0.933), so "Wilson is always better" is false; (d) a rare-event simulation (`P(sum of ten dice ≥ 55)`, `N = 10⁵`) produced a single hit, illustrating where plain Monte Carlo fails; (e) diagnostic-test PPV was 0.1538 by formula, natural frequencies, and simulation (0.1539 ± 0.0015); prior-shift correction moved the observed positive rate at predicted ≈ 0.5 from 0.049 to 0.501; (f) naive-Bayes on a 420/180 synthetic split reached 0.967 accuracy (Wilson interval 0.929–0.985), at 5% spam prevalence precision rose from 0.596 to 0.920 with the prior correction while recall fell from 0.960 to 0.810, and duplicating three informative words moved a posterior from 0.884 to 1.0. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No probability, rate, interval, or coverage figure appears without the exact value or measurement that produced it.
