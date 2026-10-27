# SYLLABUS — 13-Information-Theory-for-ML (S4B-13)

**Stage 4B — Mathematics for Machine Learning · Module 13 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy and the standard library; SciPy is **never required** (optional only for cross-checks), Matplotlib and pytest where stated. All datasets and corpora are **synthetic and generated in code**, which lets us compute the *true* entropy of the source and check every estimator against it. This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Information and surprise | `01-information-and-surprise.md` | Beginner |
| 3 | Entropy | `02-entropy.md` | Beginner → Intermediate |
| 4 | Cross-entropy as a loss | `03-cross-entropy-as-a-loss.md` | Intermediate |
| 5 | KL divergence | `04-kl-divergence.md` | Intermediate → Advanced |
| 6 | Perplexity | `05-perplexity.md` | Intermediate → Advanced |
| 7 | Practice question bank | `practice-questions.md` | All levels |
| 8 | Project index | `Projects/README.md` | Intermediate |
| 9 | Project: compute the perplexity of text | `Projects/01-compute-perplexity-of-text.md` | Intermediate → Advanced |
| 10 | Project: entropy and KL explorer | `Projects/02-entropy-and-kl-explorer.md` | Advanced |

**Prerequisites:** Module 05 (logarithms and their derivatives, `log(0)` hazards, stable log forms), Module 09 (probability, expectation, Bayes), Module 10 (categorical, softmax, `logsumexp`, Gaussian, Beta), Module 06 (integrals, numerical integration), Module 07 (gradient of softmax cross-entropy), Module 11–12 (sampling, standard errors, bootstrap intervals, paired comparisons). **Plan slot:** week 15 of `../00-Stage-4-Overview/learning-plan.md`. **Priority note `[JUDGEMENT]`:** required on every track: cross-entropy is the loss behind almost every classifier and language model, KL divergence appears in distillation, RLHF, VAEs and drift monitoring, and perplexity is the headline language-model metric.

**Teaching stance (industry, not university):** these quantities are introduced as **numbers you compute from a model's probabilities** and use to train, compare, and monitor models. Each lesson gives the definition, the code, the identity that ties it to the others, a check against a source whose true entropy is known, and the ways it is misread in practice (log bases, tokenization, zero probabilities, direction of KL).

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (formula, simulation or known answer, assertion they agree) → Failure modes → ML link.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

A classifier's loss, a language model's headline score, a distillation objective, an RLHF penalty, a VAE regularizer, and a drift alarm are all the same few quantities seen from different angles: **surprise**, **entropy**, **cross-entropy**, and **KL divergence**. Training a classifier by minimizing cross-entropy *is* maximum likelihood; perplexity *is* exponentiated cross-entropy; KL measures how much one distribution differs from another, and which *direction* you minimize determines whether a fitted model covers all modes or collapses onto one. Most production confusion here is mundane: mixing log bases, comparing perplexities across tokenizers, forgetting that `log(0)` is infinite, or minimizing KL in the wrong direction.

### 1.2 Outcomes

1. Compute self-information, entropy, cross-entropy, KL divergence, Jensen–Shannon divergence, and perplexity from probabilities, in bits and in nats, stably.
2. State and verify the identities `H(p, q) = H(p) + KL(p‖q)`, `KL ≥ 0`, `PPL = exp(H(p, q))`, and the one-hot cross-entropy `−log q_y`.
3. Explain why minimizing cross-entropy is maximum-likelihood estimation, and why it is a *proper* scoring rule while accuracy is not.
4. Explain the asymmetry of KL, demonstrate forward (mode-covering) vs reverse (mode-seeking) KL numerically, and identify where each appears in ML.
5. Compute perplexity and bits-per-character for n-gram language models, handle zero probabilities with smoothing, and know exactly when perplexities are and are not comparable.
6. Estimate entropy and KL from samples, quantify the bias of simple estimators, and build drift monitors with calibrated thresholds.
7. Verify every estimator against a source whose true entropy rate is known.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Information and surprise | Log-likelihood as negative surprise; code lengths | Surprise tables; Huffman vs `−log₂ p` |
| 2 | Entropy | Uncertainty, decision-tree splits, confidence | Entropy toolkit; estimator bias |
| 3 | Cross-entropy as a loss | Classification and LM training loss | CE from logits; `q − p` gradient; proper scoring |
| 4 | KL divergence | Distillation, RLHF, VAEs, drift | Forward vs reverse KL; Gaussian closed form |
| 5 | Perplexity | Language-model evaluation | N-gram perplexity vs true entropy rate |

### 1.4 Concept map

```
probability p(x) ──► surprise I(x) = −log p(x) ──average under p──► entropy H(p)  (best possible average code length; max at uniform)
                                                   │
                                  average of −log q(x) under p ──► cross-entropy H(p, q) = H(p) + KL(p‖q)  ≥ H(p)
                                       │                                   │
   one-hot p ──► −log q_y = the classification / language-model loss        └─► KL(p‖q) ≥ 0, = 0 iff p = q; asymmetric:
   MLE ⇔ minimize empirical cross-entropy                                         forward KL(p‖q): mode-covering · reverse KL(q‖p): mode-seeking
   exp(cross-entropy per token) = perplexity (effective branching factor)         uses: distillation, RLHF penalty, VAE, drift (PSI = KL(a‖e)+KL(e‖a))
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest          # scipy optional, for cross-checks only
```

Rules for every lab: **fix the log base and say it** (bits = `log₂`, nats = `ln`; frameworks report nats); implement each quantity in a numerically safe form (`0·log 0 = 0`, `logsumexp`, log-space products); **check every identity numerically** on random distributions (non-negativity, `H(p,q) = H(p) + KL`, `KL(p‖p) = 0`); validate estimators on a **source with known entropy**; report estimator error with an uncertainty (bootstrap over documents, Module 12); seed all randomness.

### 1.6 Checkpoint (from the stage plan)

Your cross-entropy equals `sklearn.metrics.log_loss` (if you have scikit-learn; otherwise a hand-computed reference) and your perplexity equals `exp(mean negative log-likelihood)`; all information identities hold to `1e-12` on random distributions; and your n-gram models' held-out perplexity is never below the true source perplexity (beyond sampling error).

### Check yourself (Unit 1)

1. Which quantity is the usual training loss of a classifier, and what does it equal when the target is one-hot?
2. Why is it important to state the logarithm base when reporting these quantities?

**Reference answers:** (1) Cross-entropy; `−log q_y`, the negative log-probability the model assigns to the correct class. (2) The same quantity differs by a factor `ln 2 ≈ 0.693` between bits and nats, and perplexity computed with mismatched bases is wrong (e.g., `2^{nats}`).

---

## Unit 2 — Information and surprise (`01-…md`)

### 2.1 Why ML needs this

Surprise is the atom of every loss in this module. A model's per-example loss is the *surprise it feels* on the true label; the training objective is to be less surprised, on average, by real data.

### 2.2 Intuition

Rare events are more surprising than common ones. If someone tells you the sun rose today you learn almost nothing; if they tell you it snowed in the desert, you learn a lot. **Information** is the number of yes/no questions' worth of surprise: a fair coin flip carries 1 bit.

### 2.3 Mechanics

- **Self-information (surprisal):** `I(x) = −log p(x) = log(1/p(x))`.
  - Base 2 ⇒ **bits**; base `e` ⇒ **nats**. `1 nat = 1/ln 2 ≈ 1.4427 bits`; `1 bit = ln 2 ≈ 0.6931 nats`.
  - `p = 1` ⇒ `I = 0` (no surprise); `p → 0` ⇒ `I → ∞`.
- **Additivity for independent events:** `I(x, y) = I(x) + I(y)` when `p(x, y) = p(x)p(y)` (the reason for the logarithm: products of probabilities become sums of surprises).
- **Meaning in coding:** an optimal code assigns a symbol of probability `p` about `−log₂ p` bits (rounded up in practice); **Huffman codes** achieve an average length `L` with `H ≤ L < H + 1` `[VERIFY: statement]`.
- **Log-likelihood is negative surprise:** the log-likelihood of data under a model is the *total negative surprise*; maximizing it minimizes total surprise (Lesson 3).
- **Probability vs probability density:** for a continuous variable `−log f(x)` is not a surprise in bits and can be negative (densities can exceed 1; Module 09 Lesson 6); information is defined relative to a discretization or via differential entropy.
- **Typical magnitudes:** a uniform choice among `K = 50,000` tokens costs `log₂ 50,000 ≈ 15.6 bits ≈ 10.8 nats`; a language model that assigns probability `0.5` to the correct token pays `1 bit`.

**Worked example:** `p = (0.5, 0.25, 0.125, 0.125)`: surprises `1, 2, 3, 3` bits; a prefix code with lengths `1, 2, 3, 3` exists (`0`, `10`, `110`, `111`) and its average length is `1.75` bits, which equals the entropy (Lesson 2) for this dyadic distribution.

### 2.4 Code

```python
import heapq, math
import numpy as np
rng = np.random.default_rng(0)

def surprise(p, base=2.0):
    p = np.asarray(p, float)
    with np.errstate(divide="ignore"): return -np.log(p) / math.log(base)         # inf for p = 0, by design

p = np.array([0.5, 0.25, 0.125, 0.125]); print("surprise (bits):", surprise(p), " (nats):", np.round(surprise(p, math.e), 4))
assert np.allclose(surprise(p, math.e) * (1 / math.log(2)), surprise(p, 2))                                         # base conversion

# --- additivity for independent events
px, py = 0.2, 0.05; assert np.isclose(surprise(px * py), surprise(px) + surprise(py))

# --- Huffman code lengths: average length L satisfies H ≤ L < H + 1
def huffman_lengths(probs):
    heap = [(q, i, [i]) for i, q in enumerate(probs) if q > 0]; heapq.heapify(heap); lengths = {i: 0 for _, i, _ in heap}; uid = len(probs)
    while len(heap) > 1:
        p1, _, s1 = heapq.heappop(heap); p2, _, s2 = heapq.heappop(heap)
        for i in s1 + s2: lengths[i] += 1
        uid += 1; heapq.heappush(heap, (p1 + p2, uid, s1 + s2))
    return lengths
for name, q in (("dyadic", p), ("skewed", np.array([0.7, 0.15, 0.1, 0.05])), ("uniform-8", np.full(8, 1 / 8)), ("random-20", rng.dirichlet(np.ones(20)))):
    L = huffman_lengths(q); avg = sum(q[i] * l for i, l in L.items()); H = float(-(q * np.log2(q)).sum())
    print(f"{name:10s} H = {H:.4f} bits   Huffman average length = {avg:.4f}   H ≤ L < H+1: {H - 1e-12 <= avg < H + 1}")
    assert H - 1e-12 <= avg < H + 1

# --- the log-probability of a sequence is the sum of per-token surprises (and underflows as a product)
token_p = rng.uniform(0.01, 0.5, 2000); print("product:", np.prod(token_p), " sum of surprises (nats):", surprise(token_p, math.e).sum())

# --- what a uniform guess over a vocabulary costs
for K in (2, 26, 50_000): print(f"K={K:6d}: log2 K = {math.log2(K):6.2f} bits = {math.log(K):6.2f} nats")

# --- a density is not a probability: −log f can be negative
f_at_0 = 1 / (0.01 * math.sqrt(2 * math.pi)); print("N(0, 0.01²) density at 0:", f_at_0, " −ln f =", -math.log(f_at_0), "(negative; not a surprise in bits)")
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `log(0)` in a loss (`p = 0` for the true class) | `inf`/`nan` loss and gradients | Compute from logits; clip or smooth probabilities (Lesson 3) |
| Mixing log bases (e.g., `exp` of a base-2 loss) | Wrong perplexity, values off by `ln 2` | Fix and state the base; convert once |
| Multiplying many probabilities | Underflow to `0.0` | Sum log-probabilities (Module 09 Lesson 2) |
| Treating a density as a probability | Negative "information" | Discretize (bin) or use differential entropy with care |
| Assuming code lengths are integers in theory | Off by up to 1 bit per symbol (Huffman bound) | Use `−log₂ p` as the ideal; block coding approaches it |
| Reading "bits" literally for a model's loss reported in nats | Misjudged magnitudes | Convert units before comparing papers/dashboards |

### 2.6 ML link

- **Per-token loss = surprise** of the true next token (Lesson 3, 5).
- **Log-likelihood training** minimizes total surprise on the data (Lesson 3; 4C-05).
- **Compression view of learning:** a better model gives shorter codes for the same data; language-model quality can be reported as **bits per character/byte** (Lesson 5).
- **Anomaly detection** by surprise: flag inputs a density/sequence model finds highly surprising (Stage 5B-06).

### 2.7 Lab (60 min)

1. Build a surprise table for six distributions; verify additivity and base conversion.
2. Implement Huffman code lengths and check `H ≤ L < H + 1` on 100 random distributions over 5–100 symbols; plot `L − H` against the distribution's entropy.
3. Compute the code length of a text under (a) a uniform character model and (b) a character-frequency model fitted to it; report bits per character and the saving.
4. Demonstrate underflow of a 2,000-token probability product and the log-space fix; compute surprise per token for a toy bigram model.

### Check yourself (Unit 2)

1. What is the self-information of an event of probability `1/8` in bits and nats?
2. Why does information use a logarithm?
3. What is the average length of an optimal prefix code relative to the entropy?

**Reference answers:** (1) `3` bits `= 3 ln 2 ≈ 2.079` nats. (2) It converts the product of independent probabilities into a sum of surprises, so information adds for independent events. (3) It lies in `[H, H + 1)` bits per symbol.

---

## Unit 3 — Entropy (`02-…md`)

### 3.1 Why ML needs this

Entropy is the average surprise of a distribution: a single number for how uncertain it is. It measures the confidence of a model's prediction, decides splits in decision trees, sets the floor for any language model's loss, and (via maximum entropy) motivates why softmax-style distributions appear.

### 3.2 Intuition

If the outcome is certain, entropy is zero. If all outcomes are equally likely, entropy is maximal. Entropy is "the average number of yes/no questions you need to identify the outcome", and `2^H` is the **effective number of equally likely outcomes**.

### 3.3 Mechanics

- **Definition (discrete):** `H(p) = −Σₓ p(x) log p(x) = E_p[−log p(X)]`, with the convention `0·log 0 = 0`.
- **Properties:** `H ≥ 0`; `H = 0` iff `p` is deterministic; `H ≤ log K` for `K` outcomes with equality iff uniform; `H` is concave in `p`; adding independent variables adds entropies.
- **Binary entropy:** `H(p) = −p log p − (1−p) log(1−p)`; maximal at `p = ½` (1 bit), zero at `p ∈ {0, 1}`.
- **Effective number of outcomes (perplexity of a distribution):** `2^{H}` (bits) or `e^{H}` (nats); uniform over `K` gives `K`.
- **Joint and conditional entropy:** `H(X, Y) = −Σ p(x,y) log p(x,y)`; `H(Y|X) = Σₓ p(x) H(Y|X = x)`; chain rule `H(X, Y) = H(X) + H(Y|X)`; `H(Y|X) ≤ H(Y)` (conditioning reduces uncertainty on average) `[VERIFY]`; full treatment and mutual information in 4C-06.
- **Information gain** (decision trees): `IG = H(Y) − Σ_children (n_c/n) H(Y_c)`: the entropy reduction from a split (Stage 5A-08).
- **Entropy of a model's prediction:** `H(softmax(z))` is a confidence/uncertainty score: low for peaked, high for flat; it rises with temperature (Module 10 Lesson 2).
- **Estimating entropy from samples:** the **plug-in** estimator uses empirical frequencies; it is **biased low** (more so with many categories and few samples). The Miller–Madow correction adds `(K̂ − 1)/(2n)` nats `[VERIFY]`. Estimating entropy of high-cardinality variables from small samples is notoriously unreliable.
- **Differential entropy** (continuous): `h(X) = −∫ f log f`; can be negative, changes under rescaling (`h(aX) = h(X) + log|a|`), and is not the limit of discrete entropy; Gaussian `½ log(2πeσ²)` is the maximum for a given variance `[VERIFY]` (4C-06).
- **Maximum-entropy principle (outline):** among distributions satisfying given constraints, choose the one with the largest entropy (the least assumptions); the exponential family and softmax arise this way (4C-05, 4C-06).
- **Entropy rate of a sequence source:** `lim H(X₁…Xₙ)/n`; for a stationary Markov chain with transition matrix `P` and stationary distribution `π`: `H_rate = Σᵢ πᵢ H(Pᵢ,·)`. This is the best achievable per-token cross-entropy for that source (Lesson 5).

**Worked example:** `p = (0.7, 0.2, 0.1)`: `H = 0.7·0.515 + 0.2·2.322 + 0.1·3.322 = 1.157` bits; effective number of outcomes `2^{1.157} = 2.23` (between 2 and 3).

### 3.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def entropy(p, base=2.0):
    p = np.asarray(p, float); assert np.all(p >= 0) and np.isclose(p.sum(), 1.0, atol=1e-8), "not a distribution"
    nz = p > 0; return float(-(p[nz] * np.log(p[nz])).sum() / math.log(base))                                          # 0·log 0 = 0

p = np.array([0.7, 0.2, 0.1]); print("H(p) =", entropy(p), "bits   effective outcomes 2^H =", 2 ** entropy(p))
assert abs(entropy(p) - 1.1568) < 1e-3 and entropy([1, 0, 0]) == 0.0 and np.isclose(entropy(np.full(8, 1 / 8)), 3.0)

# --- maximum at uniform: check on random distributions
for K in (2, 5, 50):
    Hs = [entropy(rng.dirichlet(np.ones(K))) for _ in range(5000)]; assert max(Hs) <= math.log2(K) + 1e-12
    print(f"K={K:3d}: log2 K = {math.log2(K):.3f}   max entropy among 5000 random distributions = {max(Hs):.3f}")

# --- binary entropy is concave with its maximum at p = 1/2
ps = np.linspace(1e-6, 1 - 1e-6, 1001); Hb = np.array([entropy([q, 1 - q]) for q in ps]); assert abs(ps[np.argmax(Hb)] - 0.5) < 1e-3 and np.isclose(Hb.max(), 1.0, atol=1e-5)

# --- chain rule  H(X,Y) = H(X) + H(Y|X)  and conditioning reduces entropy
J = rng.dirichlet(np.ones(12)).reshape(3, 4); px = J.sum(1); py = J.sum(0)
H_xy = entropy(J.ravel()); H_y_given_x = sum(px[i] * entropy(J[i] / px[i]) for i in range(3))
assert np.isclose(H_xy, entropy(px) + H_y_given_x) and H_y_given_x <= entropy(py) + 1e-12
print("H(X,Y) =", H_xy, " H(X) + H(Y|X) =", entropy(px) + H_y_given_x, " H(Y) =", entropy(py), " H(Y|X) =", H_y_given_x)

# --- information gain of a decision-tree split
y = np.r_[np.zeros(40), np.ones(60)].astype(int); left = np.r_[np.zeros(35), np.ones(10)].astype(int); right = np.r_[np.zeros(5), np.ones(50)].astype(int)
def ent_labels(v): c = np.bincount(v, minlength=2) / len(v); return entropy(c)
ig = ent_labels(y) - (len(left) / 100 * ent_labels(left) + len(right) / 100 * ent_labels(right)); print("H(parent) =", ent_labels(y), " information gain of the split =", ig)

# --- entropy of a softmax prediction rises with temperature
z = np.array([3.0, 1.0, 0.5, -1.0])
def softmax(z, T=1.0): e = np.exp((z - z.max()) / T); return e / e.sum()
print({T: round(entropy(softmax(z, T)), 3) for T in (0.25, 0.5, 1.0, 2.0, 10.0)}, " (max log2 4 = 2)")

# --- the plug-in estimator is biased low; Miller–Madow reduces the bias
K, true_p = 20, rng.dirichlet(np.ones(20) * 2); H_true = entropy(true_p)
def plug_in(sample):
    c = np.bincount(sample, minlength=K) / len(sample); return entropy(c)
def miller_madow(sample):
    c = np.bincount(sample, minlength=K); n = len(sample); return plug_in(sample) + (np.count_nonzero(c) - 1) / (2 * n) / math.log(2)
for n in (20, 50, 200, 1000, 10_000):
    est = [(plug_in(s), miller_madow(s)) for s in (rng.choice(K, size=n, p=true_p) for _ in range(1500))]
    e = np.array(est); print(f"n={n:6d}: true {H_true:.3f}   plug-in mean {e[:, 0].mean():.3f} (bias {e[:, 0].mean() - H_true:+.3f})   Miller–Madow mean {e[:, 1].mean():.3f} (bias {e[:, 1].mean() - H_true:+.3f})")

# --- entropy rate of a Markov source = Σ π_i H(P_i)
Pm = rng.dirichlet(np.ones(6) * 0.3, size=6); w, v = np.linalg.eig(Pm.T); pi = np.real(v[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
rate = float(sum(pi[i] * entropy(Pm[i]) for i in range(6))); print("entropy rate (bits/symbol):", rate, " vs log2 6 =", math.log2(6))
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `0·log 0` computed literally | `nan` | Mask zeros (`p > 0`) |
| Unnormalized "probabilities" | Entropy out of `[0, log K]` | Assert normalization |
| Plug-in entropy from few samples with many categories | Underestimated uncertainty | Larger samples; bias corrections; report uncertainty (bootstrap) |
| Comparing entropies across different alphabets or bin widths | Meaningless differences | Use consistent discretization; report relative to `log K` |
| Treating differential entropy like discrete entropy | Negative values, scale dependence | Know the differences; use discretized or relative quantities |
| Using softmax entropy as calibrated uncertainty | Overconfident or misleading scores | Calibrate (Stage 5B-04); compare with held-out error |
| Ignoring temperature when comparing prediction entropies | Apples to oranges | Fix `T` |
| Information gain favouring high-cardinality features | Spurious splits (IDs) | Gain ratio, regularization, cross-validation `[VERIFY]` |

### 3.6 ML link

- **Decision trees and random forests** split on entropy reduction (Stage 5A-08).
- **Predictive uncertainty:** entropy of the output distribution as a confidence score; decomposition into aleatoric/epistemic uncertainty (Stage 5B-02, 4C-05).
- **Floor on language-model loss:** the entropy rate of the data bounds achievable cross-entropy (Lesson 5).
- **Entropy regularization/bonuses** encourage exploration or prevent collapse (Stage 5B-13) `[JUDGEMENT]`.
- **Feature selection** via mutual information builds on entropy (Stage 5B-07, 4C-06).

### 3.7 Lab (75 min)

1. Implement `entropy`; verify the bounds on random distributions, the binary-entropy curve, and the chain rule for random joint tables.
2. Compute the information gain of three splits on synthetic labelled data and rank them; show the high-cardinality-ID pathology.
3. Plot the entropy of a softmax prediction vs temperature for three logit vectors; relate to effective number of outcomes.
4. Estimator study: plug-in vs Miller–Madow bias vs `n` for `K ∈ {5, 20, 100}`; add a bootstrap standard error.
5. Compute the entropy rate of a random Markov chain by formula and compare with `−(1/N) Σ log P(x_t | x_{t−1})` on a simulated path.

### Check yourself (Unit 3)

1. What is the entropy of a fair 8-sided die in bits?
2. When is entropy minimal and when maximal?
3. In which direction is the plug-in entropy estimator biased?

**Reference answers:** (1) `3` bits. (2) Minimal (zero) for a deterministic distribution; maximal (`log K`) for the uniform distribution. (3) Downward (it underestimates, especially for small samples and many categories).

---

## Unit 4 — Cross-entropy as a loss (`03-…md`)

### 4.1 Why ML needs this

Cross-entropy is the loss that trains classifiers and language models. Understanding what it *is* (the average surprise of a model on real data) explains its gradient, its relationship to maximum likelihood, why it rewards honest probabilities, and why it punishes confident mistakes so hard.

### 4.2 Intuition

If the data really follow `p` but you encode them with a code designed for `q`, you pay `H(p, q)` bits per symbol on average, more than the optimum `H(p)`. The excess is the KL divergence (Lesson 4). Training a model means choosing `q` to make this cost as small as possible on the data.

### 4.3 Mechanics

- **Definition:** `H(p, q) = −Σₓ p(x) log q(x) = E_p[−log q(X)]`.
- **Decomposition:** `H(p, q) = H(p) + KL(p‖q)`, so `H(p, q) ≥ H(p)` with equality iff `q = p`.
- **One-hot targets:** for a labelled example with true class `y`, `p = e_y` (entropy 0): `H(p, q) = −log q_y`, the **negative log-likelihood** of the correct class. Mean over a batch is the usual training loss.
- **Binary cross-entropy:** `−[y log q + (1−y) log(1−q)]`.
- **Maximum likelihood ⇔ cross-entropy minimization:** the average negative log-likelihood of data `x₁…xₙ` under `q_θ` equals `H(p̂, q_θ)` where `p̂` is the empirical distribution; minimizing it over `θ` is MLE (Module 10 Lesson 1, 4C-05). For a categorical model without features, the minimizer is the empirical frequencies.
- **Gradient with respect to the logits** (softmax output): `∂L/∂z = q − p` (Module 07 Lesson 5, Module 10 Lesson 2); averaged over a batch `(Q − P)/B`.
- **Stable computation from logits:** `L = logsumexp(z) − Σ pᵢzᵢ`; never `log(softmax(z))` (Module 10 Lesson 2).
- **Proper scoring rule:** the *expected* cross-entropy `E_{Y~p}[−log q(Y)]` is minimized uniquely at `q = p`, so it rewards **calibrated probabilities**. Accuracy, in contrast, depends only on the arg-max and is not proper; two models with equal accuracy can differ greatly in cross-entropy.
- **Punishing confident errors:** the loss of a wrong-class prediction with probability `q_y` is `−log q_y`: `q_y = 0.01` costs 4.6 nats, `q_y = 10⁻⁶` costs 13.8; a few extremely confident mistakes can dominate the mean loss.
- **Label smoothing:** replace the one-hot `p` by `(1−ε)e_y + ε/K`; the optimum then has a *finite* logit gap, discouraging over-confidence (4C-07) `[VERIFY]`.
- **Soft targets and distillation:** training against a teacher's probabilities (often at temperature `T > 1`) is cross-entropy with a soft `p`; equal to minimizing `KL(p_teacher‖q)` up to a constant (Lesson 4).
- **Class weights and focal loss (outline):** reweighting terms of the sum changes the effective data distribution `[VERIFY]`.
- **Units:** frameworks report nats; divide by `ln 2` for bits.
- **Relation to other losses:** MSE is the Gaussian counterpart (Module 08 Lesson 1, Module 10 Lesson 5); cross-entropy is the categorical one.

**Worked example:** logits `z = (2, 1, 0)`, true class 0: `q = (0.665, 0.245, 0.090)`; `L = −ln 0.665 = 0.408` nats `= 0.589` bits; gradient `q − p = (−0.335, 0.245, 0.090)`.

### 4.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def logsumexp(z, axis=-1):
    z = np.asarray(z, float); m = z.max(axis=axis, keepdims=True); return np.squeeze(m + np.log(np.exp(z - m).sum(axis=axis, keepdims=True)), axis=axis)
def softmax(z): z = np.asarray(z, float); return np.exp(z - logsumexp(z)[..., None] if z.ndim > 1 else z - logsumexp(z))
def cross_entropy(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    with np.errstate(divide="ignore"): terms = np.where(p > 0, -p * np.log(q), 0.0)            # 0 · log(anything) = 0
    return float(terms.sum())
def ce_from_logits(z, p): z = np.asarray(z, float); return float(logsumexp(z) - np.dot(p, z))
def entropy(p): p = np.asarray(p, float); nz = p > 0; return float(-(p[nz] * np.log(p[nz])).sum())
def kl(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    with np.errstate(divide="ignore", invalid="ignore"): t = np.where(p > 0, p * (np.log(p) - np.log(q)), 0.0)
    return float(t.sum())

# --- the decomposition H(p, q) = H(p) + KL(p‖q) on random distributions; one-hot reduces to −log q_y
for _ in range(1000):
    p, q = rng.dirichlet(np.ones(8)), rng.dirichlet(np.ones(8)); assert np.isclose(cross_entropy(p, q), entropy(p) + kl(p, q), atol=1e-12) and cross_entropy(p, q) >= entropy(p) - 1e-12
z = np.array([2.0, 1.0, 0.0]); q = softmax(z); onehot = np.array([1.0, 0, 0])
print("CE =", cross_entropy(onehot, q), " −ln q_y =", -math.log(q[0]), " from logits:", ce_from_logits(z, onehot), " in bits:", ce_from_logits(z, onehot) / math.log(2))

# --- the gradient with respect to the logits is q − p (finite differences)
def num_grad(f, x, h=1e-6): return np.array([(f(x + e * h) - f(x - e * h)) / (2 * h) for e in np.eye(len(x))])
p_soft = np.array([0.6, 0.3, 0.1]); assert np.allclose(num_grad(lambda t: ce_from_logits(t, p_soft), z), softmax(z) - p_soft, atol=1e-8)

# --- stable vs naive on extreme logits
zz = np.array([1000.0, 0.0, -1000.0]); print("stable CE for true class 2:", ce_from_logits(zz, np.array([0, 0, 1.0])), "  naive:", end=" ")
with np.errstate(all="ignore"): print(-np.log(np.exp(zz) / np.exp(zz).sum())[2])

# --- cross-entropy = average NLL = MLE: the empirical frequencies minimize the average loss
labels = rng.choice(4, size=5000, p=[0.5, 0.3, 0.15, 0.05]); counts = np.bincount(labels, minlength=4); emp = counts / counts.sum()
def avg_nll(qvec): return float(-np.mean(np.log(qvec[labels])))
best = min((rng.dirichlet(np.ones(4) * 5) for _ in range(20_000)), key=avg_nll); print("empirical frequencies:", np.round(emp, 3), " NLL:", avg_nll(emp), " best random q:", np.round(best, 3), avg_nll(best))
assert avg_nll(emp) <= avg_nll(best) + 1e-12 and np.isclose(avg_nll(emp), cross_entropy(emp, emp))

# --- proper scoring rule: expected CE is minimized by the TRUE probabilities; accuracy cannot see calibration
p_true = np.array([0.7, 0.3]); grid = np.linspace(0.01, 0.99, 981); exp_ce = [-(p_true[0] * math.log(g) + p_true[1] * math.log(1 - g)) for g in grid]
print("q minimizing expected CE:", grid[int(np.argmin(exp_ce))], "(true p = 0.7)")
y = (rng.random(100_000) < 0.7).astype(int); honest, overconf = np.full(len(y), 0.7), np.full(len(y), 0.99)
def logloss(y, q1): q = np.clip(q1, 1e-12, 1 - 1e-12); return float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))
print(f"same predicted class → same accuracy ({np.mean((honest > .5) == y):.3f}); log-loss honest {logloss(y, honest):.3f} vs overconfident {logloss(y, overconf):.3f}")

# --- confident errors dominate the mean loss
print("loss of a wrong prediction with q_true = 0.5, 0.1, 0.01, 1e-6:", [round(-math.log(v), 2) for v in (0.5, 0.1, 0.01, 1e-6)])

# --- label smoothing: finite optimal logit gap
K, eps = 5, 0.1; smooth = np.full(K, eps / K); smooth[0] += 1 - eps
gaps = np.linspace(0, 12, 1201)
def ce_gap(g): zz = np.zeros(K); zz[0] = g; return ce_from_logits(zz, smooth)
print("optimal gap with ε = 0.1:", gaps[int(np.argmin([ce_gap(g) for g in gaps]))], "  (without smoothing the loss keeps decreasing as the gap → ∞)")
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| `log(softmax(z))` or `log(0)` in the loss | `-inf`/`nan` | `logsumexp` form from logits |
| Feeding probabilities to a loss that expects logits (or vice versa) | Wrong loss, silent | Check the API; softmax applied twice |
| Mean vs sum reduction mix-ups | Loss scale (and effective learning rate) changes by `B` | State the reduction (Module 08) |
| Using accuracy alone to compare models | Hidden miscalibration | Report log-loss and a calibration measure (Stage 5B-04) |
| Confident wrong predictions dominating the loss | Training instability, large loss spikes | Label smoothing, clipping `q`, data cleaning for label noise |
| Comparing losses in different bases | Off by `ln 2` | Convert to one unit |
| One-hot `p` with label noise | Overfitting noisy labels | Smoothing, robust losses (Module 08), data audit |
| Class imbalance and the average loss | Majority class dominates | Class weights, resampling; evaluate per class |
| Treating cross-entropy as bounded by 1 | Misreading values (it is unbounded above) | Compare to the uniform baseline `log K` |

### 4.6 ML link

- **The loss of classifiers and language models** (Stage 5A-05, 5C-01, 5C-09).
- **Maximum likelihood:** training equals minimizing empirical cross-entropy (4C-05).
- **Calibration and proper scoring** (Stage 5B-04).
- **Label smoothing, distillation, and RLHF reward-model losses** are variations of cross-entropy with modified targets (4C-07, Stage 5C-11).
- **Gradient `q − p`** is what flows into the network at the logits (Module 07).

### 4.7 Lab (75 min)

1. Implement `cross_entropy`, `ce_from_logits`, `kl`, `entropy`; verify `H(p, q) = H(p) + KL(p‖q)` and non-negativity on 10,000 random pairs.
2. Gradient-check `q − p` for 50 random logit vectors and a batch with the `1/B` reduction.
3. MLE lab: fit a categorical model by gradient descent on cross-entropy (Module 08) and confirm convergence to the empirical frequencies.
4. Proper-scoring lab: compare honest vs over/under-confident predictors on simulated data with equal accuracy; produce a log-loss vs confidence curve.
5. Label-smoothing lab: show the optimal logit gap vs `ε`, and the effect on the loss of a wrong prediction.

### Check yourself (Unit 4)

1. What is the cross-entropy loss when the target is one-hot at class `y`?
2. What is `∂L/∂z` for softmax cross-entropy?
3. Why is minimizing cross-entropy equivalent to maximum-likelihood estimation?

**Reference answers:** (1) `−log q_y`. (2) `q − p` (softmax output minus target). (3) The average negative log-likelihood of the data under the model *is* the cross-entropy between the empirical distribution and the model, so minimizing one minimizes the other.

---

## Unit 5 — KL divergence (`04-…md`)

### 5.1 Why ML needs this

KL divergence measures how far one distribution is from another. It is the excess cost of cross-entropy over entropy, the regularizer in VAEs, the penalty that keeps an RLHF-tuned model close to its base model, the quantity matched in knowledge distillation, and a standard drift score. Its **asymmetry** is the most important practical fact: forward and reverse KL give qualitatively different fits.

### 5.2 Intuition

`KL(p‖q)` is the extra bits per symbol you pay by using a code built for `q` when the data come from `p`. It is zero only when `q = p`, never negative, and *not* symmetric: being wrong about a place where `p` has mass (and `q` has none) is infinitely costly, whereas the reverse is not.

### 5.3 Mechanics

- **Definition:** `KL(p‖q) = Σₓ p(x) log(p(x)/q(x)) = E_p[log p(X) − log q(X)] = H(p, q) − H(p)`.
- **Gibbs' inequality:** `KL(p‖q) ≥ 0`, with equality iff `p = q` (proof by Jensen's inequality applied to `−log`; Module 09 Lesson 7).
- **Not symmetric, not a metric:** `KL(p‖q) ≠ KL(q‖p)` in general; the triangle inequality fails.
- **Support mismatch:** if `q(x) = 0` while `p(x) > 0`, then `KL(p‖q) = ∞`. Practical fix: smooth or clip `q` (Module 09 Lesson 3), or use a bounded divergence.
- **Forward vs reverse KL** when fitting `q` to a target `p`:
  - **Forward** `KL(p‖q)` (minimize over `q`): `q` must put mass wherever `p` does (infinite penalty otherwise) ⇒ **mass-covering**, tends to spread across modes (a single Gaussian fit to a bimodal `p` becomes broad and sits between the modes). This is maximum likelihood: minimizing `H(p, q)` over `q`.
  - **Reverse** `KL(q‖p)`: `q` is penalized for putting mass where `p` has little ⇒ **mode-seeking**, tends to lock onto one mode. Variational inference (VAE/ELBO) and many policy-regularization terms are reverse KL.
- **Closed form (Gaussians):** `KL(N(μ₁, σ₁²) ‖ N(μ₂, σ₂²)) = ln(σ₂/σ₁) + (σ₁² + (μ₁ − μ₂)²)/(2σ₂²) − ½`. For the VAE prior `N(0, 1)`: `KL(N(μ, σ²)‖N(0,1)) = ½(σ² + μ² − 1 − ln σ²)`.
- **Jensen–Shannon divergence:** `JS(p, q) = ½KL(p‖m) + ½KL(q‖m)`, `m = (p + q)/2`; symmetric, always finite, bounded by `ln 2` (1 bit); its square root is a metric `[VERIFY]`.
- **Estimating KL from samples:** with samples `x_i ~ p` and known densities: `(1/n) Σ [log p(xᵢ) − log q(xᵢ)]` (unbiased Monte Carlo, with a standard error, Module 11). From histograms: binning and zero counts cause large bias or infinities; smooth and report uncertainty.
- **Drift monitoring:** compare a reference (training) distribution `e` to a current (serving) distribution `a` over bins. The **population stability index** `PSI = Σ (aᵢ − eᵢ) ln(aᵢ/eᵢ) = KL(a‖e) + KL(e‖a)` (the symmetrized KL) `[VERIFY]`; common rule-of-thumb thresholds (0.1, 0.25) are conventions, not laws: calibrate your own by simulating no-drift data at your sample size `[JUDGEMENT]` (Module 12).
- **Uses in ML:**
  - **Distillation:** minimize `KL(p_teacher‖q_student)` (cross-entropy with soft targets).
  - **RLHF/policy optimization:** penalize `KL(π_θ‖π_ref)` (or constrain it) to stay near a reference policy `[VERIFY: direction used in a given method]`.
  - **VAEs:** the ELBO contains `KL(q(z|x)‖p(z))` (4C-10).
  - **Trust-region methods** limit the KL between successive policies (Stage 5B-13) `[VERIFY]`.
  - **Mutual information** is the KL between the joint and the product of marginals (4C-06).
- **Relation to log-likelihood ratios and hypothesis testing:** `KL(p‖q)` is the expected log-likelihood ratio under `p`; it governs how quickly the two hypotheses can be distinguished (Stein's lemma `[VERIFY]`).

**Worked example:** `p = (0.5, 0.5)`, `q = (0.9, 0.1)`: `KL(p‖q) = 0.5 ln(0.5/0.9) + 0.5 ln(0.5/0.1) = 0.511` nats, while `KL(q‖p) = 0.9 ln 1.8 + 0.1 ln 0.2 = 0.368` nats: different, and `JS = 0.1017` nats (`< ln 2 = 0.693`).

### 5.4 Code

```python
import math
import numpy as np
rng = np.random.default_rng(0)

def kl(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    with np.errstate(divide="ignore", invalid="ignore"): t = np.where(p > 0, p * (np.log(p) - np.log(q)), 0.0)
    return float(t.sum())                                                                                    # inf when q = 0 where p > 0
def js(p, q): m = (np.asarray(p) + np.asarray(q)) / 2; return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# --- non-negativity, zero iff equal, asymmetry, JS bounds
for _ in range(2000):
    p, q = rng.dirichlet(np.ones(10)), rng.dirichlet(np.ones(10)); assert kl(p, q) >= -1e-12 and js(p, q) <= math.log(2) + 1e-12 and np.isclose(js(p, q), js(q, p))
assert np.isclose(kl(p, p), 0.0)
pa, qa = np.array([0.5, 0.5]), np.array([0.9, 0.1]); print(f"KL(p‖q) = {kl(pa, qa):.4f}  KL(q‖p) = {kl(qa, pa):.4f}  JS = {js(pa, qa):.4f}  (ln 2 = {math.log(2):.4f})")
print("support mismatch:", kl([0.5, 0.5, 0.0], [1.0, 0.0, 0.0]), "(p has mass where q has none) vs", kl([1.0, 0.0, 0.0], [0.5, 0.5, 0.0]), "(finite)")

# --- Gaussian closed form vs numerical integration (Module 06)
def kl_gauss(m1, s1, m2, s2): return math.log(s2 / s1) + (s1 ** 2 + (m1 - m2) ** 2) / (2 * s2 ** 2) - 0.5
def npdf(x, m, s): return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))
xs = np.linspace(-30, 30, 600_001); p_, q_ = npdf(xs, 1.0, 1.5), npdf(xs, -0.5, 2.0)
num = float(np.sum(p_ * (np.log(p_) - np.log(q_))) * (xs[1] - xs[0])); print("Gaussian KL closed form:", kl_gauss(1.0, 1.5, -0.5, 2.0), " numerical:", num); assert abs(num - kl_gauss(1.0, 1.5, -0.5, 2.0)) < 1e-6
print("VAE term, μ=0.5, σ=0.8:", 0.5 * (0.8 ** 2 + 0.5 ** 2 - 1 - math.log(0.8 ** 2)), "=", kl_gauss(0.5, 0.8, 0.0, 1.0))

# --- forward vs reverse KL: fit one Gaussian to a bimodal target on a grid
x = np.linspace(-14, 14, 2801); dx = x[1] - x[0]; target = 0.5 * npdf(x, -3, 1) + 0.5 * npdf(x, 3, 1); target /= target.sum() * dx
def kl_grid(a, b): return float(np.sum(a * (np.log(np.maximum(a, 1e-300)) - np.log(np.maximum(b, 1e-300)))) * dx)
best_f = best_r = (np.inf, None)
for mu in np.arange(-5, 5.01, 0.25):
    for s in np.arange(0.5, 6.01, 0.25):
        q = npdf(x, mu, s); q /= q.sum() * dx
        f, r = kl_grid(target, q), kl_grid(q, target)
        if f < best_f[0]: best_f = (f, (mu, s))
        if r < best_r[0] and mu > 0: best_r = (r, (mu, s))                       # restrict to μ>0 to name the locked-on mode (the problem is symmetric)
print("forward KL(p‖q) minimizer (μ, σ):", best_f[1], " (covers both modes: μ≈0, σ≈√(1+9)=3.16)")
print("reverse KL(q‖p) minimizer (μ, σ):", best_r[1], " (locks onto one mode: μ≈3, σ≈1)")

# --- Monte Carlo KL with a standard error (known densities)
N = 400_000; xs_mc = rng.normal(1.0, 1.5, N); vals = np.log(npdf(xs_mc, 1.0, 1.5)) - np.log(npdf(xs_mc, -0.5, 2.0))
print(f"MC KL = {vals.mean():.4f} ± {vals.std(ddof=1) / math.sqrt(N):.4f}   exact {kl_gauss(1.0, 1.5, -0.5, 2.0):.4f}")

# --- drift monitoring: PSI equals the symmetrized KL; thresholds must be calibrated for YOUR sample size
def psi(a, e): a, e = np.asarray(a, float), np.asarray(e, float); return float(np.sum((a - e) * np.log(a / e)))
e = np.array([0.1, 0.2, 0.4, 0.2, 0.1]); a = np.array([0.15, 0.25, 0.35, 0.15, 0.10]); assert np.isclose(psi(a, e), kl(a, e) + kl(e, a))
def binned(sample, edges): c = np.histogram(sample, bins=edges)[0] + 0.5; return c / c.sum()                   # additive smoothing so no bin is empty
edges = np.linspace(-4, 4, 11)
for n in (200, 1000, 10_000):
    null = [psi(binned(rng.normal(size=n), edges), binned(rng.normal(size=100_000), edges)) for _ in range(500)]
    shifted = [psi(binned(rng.normal(0.3, 1, size=n), edges), binned(rng.normal(size=100_000), edges)) for _ in range(500)]
    print(f"n={n:6d}: PSI under no drift: mean {np.mean(null):.4f}, 95th pct {np.quantile(null, .95):.4f} | under a 0.3σ mean shift: mean {np.mean(shifted):.4f}")
```

### 5.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Treating KL as symmetric or as a distance | Wrong comparisons; triangle-inequality assumptions fail | State the direction; use JS or a metric if symmetry is required |
| `q(x) = 0` where `p(x) > 0` | `KL = inf` | Smooth `q`; check supports; work in logits |
| Minimizing KL in the wrong direction for the goal | Mode collapse (reverse) or a blurry, over-broad fit (forward) | Pick by objective: coverage vs precision |
| Histogram-based KL with empty bins or too many bins | `inf` or large positive bias | Additive smoothing; fewer bins; report uncertainty |
| Fixed PSI/KL thresholds copied from a blog | False alarms at small `n`, missed drift at large `n` | Calibrate by simulation/permutation at your `n` (Module 12) |
| Computing KL between a discrete and a continuous distribution | Meaningless | Match the representation (discretize consistently) |
| KL from a Monte Carlo estimate without an error bar | Unverifiable | Report the standard error |
| Confusing `KL(p‖q)` argument order across papers/libraries | Sign/direction errors | Check the library's convention (e.g., target vs input) `[VERIFY]` |
| Interpreting small KL as small *practical* difference | Ignoring which regions matter | Pair with task metrics |

### 5.6 ML link

- **Knowledge distillation** (Stage 5C-11, 5D-10), **RLHF/DPO-style KL penalties** (Stage 5C-11), **VAEs** (4C-10), **trust-region policy optimization** (Stage 5B-13).
- **Data/prediction drift monitoring** with PSI/KL/JS (Stage 5D-12; Project 2).
- **Variational inference** is reverse-KL minimization (4C-05, 4C-10).
- **Model comparison on distributions:** comparing a model's output distribution to a reference.

### 5.7 Lab (90 min)

1. Verify non-negativity, asymmetry, JS bounds, and `H(p, q) = H(p) + KL` on 10,000 random pairs; produce a heatmap of `KL(Bern(a)‖Bern(b))`.
2. Reproduce the Gaussian closed form against numerical integration for 10 parameter pairs; compute the VAE term for a grid of `(μ, σ)`.
3. Forward vs reverse KL: fit a single Gaussian to a bimodal target and to a heavy-tailed target; plot the fitted densities; explain each in one sentence.
4. Monte Carlo KL estimation: error vs `N`; then the histogram estimator's bias vs bin count and sample size.
5. Drift monitor: simulate no-drift and shifted data across `n ∈ {200, 1,000, 10,000}`; calibrate a PSI threshold for a 1% false-alarm rate at each `n`; measure detection power for 0.1σ, 0.3σ, 0.5σ shifts.

### Check yourself (Unit 5)

1. What does `KL(p‖q) = 0` imply?
2. Which direction of KL leads to mode-seeking behaviour when fitting `q`?
3. Why can a fixed PSI threshold be misleading?

**Reference answers:** (1) `p = q` (as distributions). (2) Reverse KL, `KL(q‖p)`: `q` is penalized for putting mass where `p` has little, so it locks onto a mode. (3) The null distribution of the PSI depends on the sample size and binning, so a threshold that is right at one `n` produces many false alarms at small `n` and misses at large `n`.

---

## Unit 6 — Perplexity (`05-…md`)

### 6.1 Why ML needs this

Perplexity is the standard intrinsic metric for language models and the number quoted in most training-curve plots. It is simply **exponentiated cross-entropy per token**, which makes it easy to compute, and easy to misuse (comparing across tokenizers, evaluating on training text, ignoring unseen tokens).

### 6.2 Intuition

Perplexity is the model's *effective branching factor*: a perplexity of 20 means the model is, on average, as uncertain as if it were choosing uniformly among 20 equally likely next tokens. Lower is better; the best possible value is the perplexity of the data source itself.

### 6.3 Mechanics

- **Definition:** for a test sequence `w₁…w_N`: `PPL = exp(−(1/N) Σ_{t=1}^{N} ln q(w_t | w_{<t})) = exp(H(p̂, q))` (nats) `= 2^{(bits per token)}`. Use matching bases.
- **Boundary cases:** a uniform model over a vocabulary of `V` tokens has `PPL = V`; a perfect model has `PPL = 1`; a model assigning zero probability to any test token has `PPL = ∞` (hence **smoothing**).
- **Floor:** for data from a source with entropy rate `H_rate`, no model can achieve an expected cross-entropy below `H_rate`, so `PPL ≥ exp(H_rate)` in expectation; sampling noise can make a model's *measured* test perplexity dip slightly below on a finite sample.
- **Relation to the training loss:** `loss = ln PPL`; a loss reduction of `0.1` nats multiplies perplexity by `e^{−0.1} ≈ 0.905` (a 9.5% reduction): small loss changes are large perplexity changes at high perplexity.
- **N-gram models (the lab workhorse):**
  - **Unigram:** `q(w) = (count(w) + α)/(N + αV)`.
  - **Bigram:** `q(w | v) = (count(v, w) + α)/(count(v) + αV)`.
  - **Smoothing** (additive `α`; linear interpolation of orders `λ₁q₁ + λ₂q₂ + …`; backoff/Kneser–Ney are stronger and are described in Stage 5A-10 `[VERIFY]`). Held-out perplexity as a function of `α` is U-shaped: too little smoothing explodes on unseen events; too much washes out the data.
  - **Unknown tokens:** map rare/unseen test tokens to `<unk>`; the choice affects perplexity, so report it.
- **Comparability caveats (critical):**
  - Perplexity depends on the **tokenization and vocabulary**: a word-level model and a subword or character-level model assign probabilities to different units; their perplexities are *not comparable*. Convert to a common unit: **bits per character (BPC)** or **bits per byte**: `BPC = (total NLL in bits)/(number of characters)`.
  - It depends on the **dataset** (domain, cleaning, document length) and on the **context length** (more context lowers perplexity).
  - Evaluating on the **training set** is meaningless (memorization lowers it); hold out data, and watch for **leakage** between train and test.
- **Limitations:** low perplexity does not guarantee factual, safe, or useful generations; it measures how well the model predicts held-out text under its own tokenization. Task benchmarks and human evaluation complement it (Stage 5C-09/13).
- **Uncertainty:** perplexity on `N` tokens has sampling variability; compute an interval by bootstrapping **documents** (not tokens, because tokens within a document are dependent, Module 12 Lesson 2) and compare two models with a **paired** difference in per-document mean NLL.
- **Per-token vs per-sequence:** report the mean over tokens; sequence-level likelihoods shrink with length.

**Worked example:** a model assigns probabilities `(0.5, 0.25, 0.1, 0.4)` to the four tokens of a test string: NLL `= (0.693 + 1.386 + 2.303 + 0.916)/4 = 1.325` nats; `PPL = e^{1.325} = 3.76`; bits per token `= 1.912`.

### 6.4 Code

```python
import math
from collections import Counter
import numpy as np
rng = np.random.default_rng(0)

def perplexity_from_logprobs(logp): return math.exp(-float(np.mean(logp)))                                   # natural-log probabilities
print("worked example PPL:", perplexity_from_logprobs(np.log([0.5, 0.25, 0.1, 0.4])))
V = 30; assert np.isclose(perplexity_from_logprobs(np.full(1000, -math.log(V))), V)                           # uniform model over V tokens

# --- a source with a KNOWN entropy rate: a sparse random bigram chain
P = rng.dirichlet(np.full(V, 0.15), size=V)
w, vec = np.linalg.eig(P.T); pi = np.real(vec[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
H_rate = float(sum(pi[i] * -(P[i][P[i] > 0] * np.log(P[i][P[i] > 0])).sum() for i in range(V)))
def sample_chain(n, g):
    s = np.empty(n, int); s[0] = g.choice(V, p=pi)
    for t in range(1, n): s[t] = g.choice(V, p=P[s[t - 1]])
    return s
train, test = sample_chain(120_000, rng), sample_chain(30_000, np.random.default_rng(1))
print(f"true entropy rate {H_rate:.4f} nats → ideal perplexity {math.exp(H_rate):.3f}; uniform baseline {V}")

# --- the true model scores ≈ the ideal perplexity on its own samples (sampling error only)
lp_true = np.log(P[test[:-1], test[1:]]); print("true bigram model on test text: PPL", perplexity_from_logprobs(lp_true))

# --- unigram vs bigram with additive smoothing; held-out perplexity vs α (with 120k tokens and 900 parameters the curve is very flat and there is no overfitting; the dramatic U-shape needs little data: see the 3,000-token runs below)
uni = np.bincount(train, minlength=V); bi = np.zeros((V, V)); np.add.at(bi, (train[:-1], train[1:]), 1)
def ppl_unigram(alpha, data): q = (uni + alpha) / (uni.sum() + alpha * V); return perplexity_from_logprobs(np.log(q[data[1:]]))
def ppl_bigram(alpha, data, tr_bi=bi): q = (tr_bi + alpha) / (tr_bi.sum(1, keepdims=True) + alpha * V); return perplexity_from_logprobs(np.log(q[data[:-1], data[1:]]))
print("unigram PPL:", ppl_unigram(1.0, test), "  bigram PPL (α = 0.1):", ppl_bigram(0.1, test))
for alpha in (1e-6, 1e-3, 0.01, 0.1, 1.0, 10.0): print(f"α={alpha:<8g} bigram held-out PPL {ppl_bigram(alpha, test):8.3f}   (training-set PPL {ppl_bigram(alpha, train):8.3f})")
assert ppl_bigram(0.1, test) >= math.exp(H_rate) * 0.98                                                       # cannot beat the source (up to sampling noise)

# --- small training set: zero counts make α → 0 explode
small = bi.copy() * 0; np.add.at(small, (train[:3000 - 1], train[1:3000]), 1)
for alpha in (1e-9, 0.01, 0.5): print(f"3,000-token training set, α={alpha:<6g}: held-out PPL {ppl_bigram(alpha, test, small):10.3f}")

# --- interpolating unigram and bigram is more robust with little data
def ppl_interp(lam, alpha, data, tr_bi):
    q_bi = (tr_bi + alpha) / (tr_bi.sum(1, keepdims=True) + alpha * V); q_uni = (tr_bi.sum(0) + alpha) / (tr_bi.sum() + alpha * V)
    q = lam * q_bi[data[:-1], data[1:]] + (1 - lam) * q_uni[data[1:]]; return perplexity_from_logprobs(np.log(q))
print("interpolated (λ = 0.7, α = 0.01) with the 3,000-token model:", ppl_interp(0.7, 0.01, test, small))

# --- loss ↔ perplexity: small loss changes are large perplexity changes
for d in (0.01, 0.1, 0.5): print(f"loss −{d} nats → perplexity ×{math.exp(-d):.3f}")

# --- tokenization comparability: word-level PPL vs character-level PPL, compared via bits per character
words = ["".join(rng.choice(list("abcdefghij"), size=rng.integers(3, 8))) for _ in range(V)]                   # vocabulary of 30 'words'
text_words = train[:40_000]; chars_per_word = np.array([len(words[i]) + 1 for i in range(V)])                  # +1 for the space
nll_word_total = -np.log(P[test[:-1], test[1:]]).sum(); n_chars = chars_per_word[test[1:]].sum()
print(f"word-level PPL (true model) {math.exp(nll_word_total / (len(test) - 1)):.2f}   bits per character {nll_word_total / math.log(2) / n_chars:.3f}   (compare with a character-level model's bits per character in the lab: the PPL values differ hugely, the BPC values are comparable)")
```

### 6.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Comparing perplexities across tokenizers/vocabularies | Misleading rankings | Convert to bits per character/byte; same test text |
| Evaluating on training text | Implausibly low perplexity | Held-out data; check for leakage and duplicates |
| Zero probabilities in the test (unseen n-grams) | `inf` perplexity | Smoothing/interpolation; report the `<unk>` policy |
| Mixing `exp` with base-2 losses (or `2^` with nats) | Wrong values by a factor | Convert units before exponentiating |
| Averaging per-document perplexities instead of per-token NLL | Wrong aggregate | Pool token NLL, then exponentiate |
| Treating tokens within a document as independent for confidence intervals | Intervals too narrow | Bootstrap documents |
| Different context lengths or truncation between compared models | Unfair comparison | Fix the evaluation protocol |
| Equating low perplexity with good generations | Overstated quality claims | Add task/human evaluations |
| Reporting perplexity without the dataset, tokenizer, and context length | Unreproducible | Always report all three |

### 6.6 ML link

- **Language-model training and evaluation** (Stage 5C-08/09/10); training curves in nats are `ln PPL`.
- **Scaling-law studies** relate loss (log-perplexity) to compute and data (Stage 5C-10).
- **Compression view:** BPC/bits-per-byte links modelling to compression (Lesson 1).
- **Smoothing and interpolation** underpin classical NLP baselines (Stage 5A-10) and motivate back-off ideas.
- **Out-of-domain perplexity** as a coarse data-shift signal (Stage 5D-12) `[JUDGEMENT]`.

### 6.7 Lab (90 min)

1. Implement `perplexity_from_logprobs`; verify the uniform and perfect-model cases and the loss–PPL relation.
2. Generate text from a known Markov chain; compute its true entropy rate; compare the true model's, bigram's, and unigram's held-out perplexities.
3. Smoothing study: held-out perplexity vs `α` for training sizes `{1k, 10k, 100k}` tokens; locate the optimum and show that the optimal `α` shrinks as data grows.
4. Interpolation study: unigram–bigram mixtures vs additive smoothing on small data.
5. Comparability study: build a character-level n-gram model for the same text and show that word-level and character-level perplexities differ hugely while bits per character are comparable.

### Check yourself (Unit 6)

1. What is the perplexity of a uniform model over 50,000 tokens?
2. How does perplexity relate to cross-entropy?
3. Why can't you compare a word-level and a character-level perplexity directly?

**Reference answers:** (1) `50,000`. (2) `PPL = exp(cross-entropy per token)` (with nats; `2^{bits}` with bits). (3) They are averages over different units (words vs characters); convert both to bits per character (or per byte) on the same text for a fair comparison.

---

## Unit 7 — Practice question bank (`practice-questions.md`)

### 7.1 Structure

About 45 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 11 per tier, each with a hidden answer and a one-line rationale. Mix hand calculation, identity checks, runnable code, and evaluation-design judgement.

### 7.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 7.3 Seed items

**Q1 [L1] Surprise.** `I` of an event with `p = 1/16` in bits? → `4`.
**Q2 [L2] Entropy.** `p = (0.5, 0.25, 0.25)`: `H` in bits? → `0.5·1 + 0.25·2 + 0.25·2 = 1.5`.
**Q3 [L2] Max entropy.** Max entropy over 6 outcomes, in nats? → `ln 6 = 1.792`.
**Q4 [L2] Cross-entropy.** True class has model probability 0.2: loss in nats and bits? → `1.609` nats `= 2.322` bits.
**Q5 [L2] Gradient.** `q = (0.6, 0.3, 0.1)`, label class 3: `∂L/∂z`? → `(0.6, 0.3, −0.9)`.
**Q6 [L2] KL.** `p = (0.5, 0.5)`, `q = (0.25, 0.75)`: `KL(p‖q)` in nats? → `0.5 ln 2 + 0.5 ln(2/3) = 0.1438`.
**Q7 [L2] Perplexity.** Mean NLL `2.303` nats: PPL? → `10`.
**Q8 [L2] Uniform baseline.** A character model over 27 symbols that is uniform: PPL and bits per character? → `27`; `4.755`.
**Q9 [L2] Loss–PPL.** Loss drops from `3.0` to `2.9` nats: PPL change? → ×`e^{−0.1} = 0.905` (about `−9.5%`).
**Q10 [L3] Debug.** A training loss prints `nan` after a few steps; the model outputs probabilities and the loss is `−log(p[y])`. → Some `p[y] = 0` (underflow/saturation); compute from logits with `logsumexp`, or clip.
**Q11 [L3] Debug.** A team reports perplexity `18` for model A (subword) and `45` for model B (word-level) and picks A. → Not comparable across tokenizers; compare bits per character/byte on the same text.
**Q12 [L3] Debug.** `KL(p‖q)` returns `inf` when comparing today's prediction histogram with the training one. → Empty bins in `q`; apply additive smoothing/merge bins; or use JS.
**Q13 [L3] Analysis.** Two classifiers both have 91% accuracy but log-loss `0.25` and `0.60`. What differs? → Calibration/confidence: the second makes confident mistakes; compare reliability diagrams.
**Q14 [L3] Analysis.** A VAE's KL term collapses to ≈ 0 and reconstructions are poor. → The posterior ignores the latent (posterior collapse); the reverse-KL regularizer dominates; adjust weighting/annealing `[VERIFY]` (4C-10).
**Q15 [L3] Analysis.** Training perplexity is 2.1, test perplexity 85. → Overfitting/memorization or leakage-free test of a different domain; check duplicates, regularization, data split.
**Q16 [L4] Design.** Design a drift monitor for a model's input feature. → Bin using training quantiles, smooth, compute PSI/JS against the training histogram per window, calibrate the alert threshold by simulating no-drift windows at the production sample size, and set a false-alarm budget.
**Q17 [L4] Design.** Compare two language models trained with different tokenizers. → Evaluate on one held-out text; report bits per byte with a document-level bootstrap interval and a paired difference; state the context length and unknown-token policy.
**Q18 [L4] Design.** Choose forward or reverse KL to fit a unimodal approximation to a multimodal posterior and justify. → Reverse KL if you need a precise, mode-focused approximation (variational inference), forward KL if you need coverage (do not miss modes); state the consequences and verify on a toy problem.

### 7.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Information and surprise | 2 | 1 | 1 | 0 |
| Entropy | 2 | 3 | 1 | 0 |
| Cross-entropy | 2 | 3 | 3 | 0 |
| KL divergence | 2 | 2 | 3 | 2 |
| Perplexity | 1 | 3 | 3 | 1 |

### Check yourself (Unit 7)

1. Why include the "cross-tokenizer comparison" item?
2. Which items need runnable code?

**Reference answers:** (1) It is the most common misuse of perplexity in reports and model cards. (2) All L3 items and any whose answer depends on floating-point behaviour.

---

## Unit 8 — Project index (`Projects/README.md`)

### 8.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Compute the perplexity of text | N-gram language models, perplexity and bits per character, smoothing, honest comparison with intervals and a known entropy floor | 1, 3, 5 | 8–9 h |
| 2 | Entropy and KL explorer | Validated information-theory toolkit, forward vs reverse KL, estimator bias, calibrated drift monitoring | 1–4 | 8–9 h |

Order: 2 → 1 or 1 → 2 (both share the entropy/KL helpers; Project 1 uses Project 2's validated functions). Outputs feed `mlmath/info.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D12) and notebook `13_information.ipynb`. The n-gram code is reused in Stage 5A-10.

### 8.2 Data policy

**No downloads.** Project 1 generates its corpora from known Markov sources (so the true entropy rate is known) and may also run on any plain-text file you already have locally (keep it out of the repository and tests `[VERIFY: licence]`). Project 2 uses synthetic distributions and samples.

### 8.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness (identities hold; estimators match known truths; perplexity ≥ source floor within sampling error) | 30 |
| Failure-mode handling (zero probabilities, empty bins, log bases, tokenization, leakage) | 15 |
| Reproducibility (seeded, pinned, clean venv, no downloads) | 15 |
| Explanation and statistical honesty (intervals on metrics, estimator bias reported, scoped claims) | 15 |
| Code quality (types, log-space arithmetic, validated distributions, docstrings stating bases) | 15 |
| ML connection paragraph | 10 |

### 8.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 8)

1. What does Project 1 reuse from Project 2?
2. Which stage-library deliverable do these feed?

**Reference answers:** (1) The validated entropy, cross-entropy, and KL functions. (2) D12 (`mlmath/info.py`).

---

## Unit 9 — Project: Compute the perplexity of text (`Projects/01-…md`)

### 9.1 Brief

Build `pplkit`: character-level and word-level n-gram language models (unigram, bigram, trigram, with additive smoothing and linear interpolation), a perplexity and bits-per-character evaluator, and an evaluation protocol with **document-level bootstrap intervals** and **paired model comparisons**. Validate everything against **corpora generated from known Markov sources**, where the true entropy rate (and hence the best possible perplexity) is known.

**Industry framing:** perplexity numbers in model cards are only as good as their protocol. The deliverable is a small evaluation harness that states the tokenization, context, unknown-token policy, and an uncertainty for every number, and that can tell you when a reported improvement is smaller than the noise.

### 9.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Corpus generator | Sparse random Markov sources of order 1 (and order 2 as a stretch) over a configurable vocabulary; documents of random length; exact **entropy rate** by formula; train/validation/test splits by *document* |
| R2 | Tokenizers | Character-level and word-level (whitespace) with a frozen vocabulary from the training split; `<unk>` mapping with an explicit policy; start-of-document symbol |
| R3 | Models | Unigram, bigram, trigram with additive smoothing; linear interpolation of orders with weights fit on validation data (grid or EM); every conditional distribution sums to 1 (asserted) |
| R4 | Evaluator | `perplexity(model, docs)` from pooled token log-probabilities (log space, natural logs), plus bits per token and **bits per character**; refuses `p = 0` unless a policy says otherwise |
| R5 | Sanity suite | Uniform model PPL equals vocabulary size; the true source model's PPL is within sampling error of `exp(H_rate)`; training-set PPL < test PPL; shuffling the test tokens destroys the bigram advantage |
| R6 | Smoothing study | Held-out PPL vs `α` for several training sizes; U-shape; optimal `α` shrinks with data |
| R7 | Interpolation | Interpolated model vs best single order; fitted weights reported |
| R8 | Uncertainty | Document-level bootstrap interval for each model's perplexity (Module 12 Lesson 2); paired bootstrap interval for the *difference in mean NLL* between two models on the same documents |
| R9 | Comparability study | Word-level vs character-level models of the same text: report PPL (not comparable) and BPC (comparable); explain the difference quantitatively |
| R10 | Floor analysis | Tabulate best-`α` model perplexity vs training size against the **true model's perplexity on the same test documents** (which includes the document-start cost; `exp(H_rate)` is lower by about `(H(π) − H_rate)/L` nats per token for short documents); report the gap, which should shrink toward 0 with data |
| R11 | Leakage and domain-shift experiments | Duplicate 10% of test documents into training and show the optimistic perplexity; evaluate a model trained on one source on a different source |
| R12 | Report | `REPORT.md`: tables with intervals for every claim, the comparability warning, the floor analysis, and a "reporting checklist" for perplexity |

### 9.3 Layout and starter

```
pplkit/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/pplkit/{__init__,sources,tokenize,ngram,evaluate,bootstrap}.py
├── tests/{test_sources,test_ngram,test_evaluate,test_bootstrap}.py
├── notebooks/13_perplexity.ipynb
└── results/
```

```python
# src/pplkit/sources.py
import numpy as np

class MarkovSource:
    """First-order Markov chain over V symbols with a known entropy rate (nats/symbol)."""
    def __init__(self, V=30, concentration=0.15, seed=0):
        g = np.random.default_rng(seed); self.V = V; self.P = g.dirichlet(np.full(V, concentration), size=V)
        w, vec = np.linalg.eig(self.P.T); self.pi = np.real(vec[:, np.argmin(np.abs(w - 1))]); self.pi /= self.pi.sum()
    @property
    def entropy_rate(self):
        P = self.P; H = np.where(P > 0, -P * np.log(np.where(P > 0, P, 1)), 0).sum(1); return float(self.pi @ H)
    def sample_doc(self, length, rng):
        s = np.empty(length, int); s[0] = rng.choice(self.V, p=self.pi)
        for t in range(1, length): s[t] = rng.choice(self.V, p=self.P[s[t - 1]])
        return s
    def sample_docs(self, n_docs, mean_len, seed):
        rng = np.random.default_rng(seed); return [self.sample_doc(max(5, int(rng.poisson(mean_len))), rng) for _ in range(n_docs)]
```

```python
# src/pplkit/ngram.py
import numpy as np

class NGram:
    """Additive-smoothed n-gram (n = 1, 2) over integer tokens with an explicit start symbol (index V)."""
    def __init__(self, V, order=2, alpha=0.1): self.V, self.order, self.alpha = V, order, alpha
    def fit(self, docs):
        V = self.V; self.uni = np.zeros(V); self.bi = np.zeros((V + 1, V))                      # row V = context 'start of document'
        for d in docs:
            self.uni += np.bincount(d, minlength=V); self.bi[V, d[0]] += 1; np.add.at(self.bi, (d[:-1], d[1:]), 1)
        return self
    def cond(self):
        a, V = self.alpha, self.V
        if self.order == 1: return np.tile((self.uni + a) / (self.uni.sum() + a * V), (V + 1, 1))
        return (self.bi + a) / (self.bi.sum(1, keepdims=True) + a * V)
    def logprobs(self, doc):
        C = np.log(self.cond()); ctx = np.r_[self.V, doc[:-1]]; return C[ctx, doc]
```

```python
# src/pplkit/evaluate.py
import math
import numpy as np

def pooled_logprobs(model, docs): return np.concatenate([model.logprobs(d) for d in docs])
def perplexity(model, docs):
    lp = pooled_logprobs(model, docs)
    if not np.all(np.isfinite(lp)): raise ValueError("a test token has zero probability under the model: apply smoothing or an <unk> policy")
    return math.exp(-float(lp.mean()))
def bits_per_token(model, docs): return -float(pooled_logprobs(model, docs).mean()) / math.log(2)
```

```python
# src/pplkit/bootstrap.py
import numpy as np

def doc_bootstrap_ppl(model, docs, B=2000, seed=0, level=0.95):
    """Bootstrap DOCUMENTS (tokens within a document are dependent). Returns (point estimate, lo, hi)."""
    per_doc = [(-model.logprobs(d).sum(), len(d)) for d in docs]; nll = np.array([x[0] for x in per_doc]); n = np.array([x[1] for x in per_doc], float)
    g = np.random.default_rng(seed); idx = g.integers(0, len(docs), size=(B, len(docs)))
    reps = np.exp(nll[idx].sum(1) / n[idx].sum(1)); a = (1 - level) / 2
    return float(np.exp(nll.sum() / n.sum())), *map(float, np.quantile(reps, [a, 1 - a]))

def paired_doc_bootstrap_diff(model_a, model_b, docs, B=2000, seed=0, level=0.95):
    """Interval for mean-NLL(A) − mean-NLL(B) in nats per token (positive ⇒ B is better), resampling documents jointly."""
    na = np.array([-model_a.logprobs(d).sum() for d in docs]); nb = np.array([-model_b.logprobs(d).sum() for d in docs]); n = np.array([len(d) for d in docs], float)
    g = np.random.default_rng(seed); idx = g.integers(0, len(docs), size=(B, len(docs)))
    diffs = (na[idx].sum(1) - nb[idx].sum(1)) / n[idx].sum(1); a = (1 - level) / 2
    return float(na.sum() / n.sum() - nb.sum() / n.sum()), *map(float, np.quantile(diffs, [a, 1 - a]))
```

```python
# tests/test_evaluate.py
import math, numpy as np, pytest
from pplkit.sources import MarkovSource
from pplkit.ngram import NGram
from pplkit.evaluate import perplexity
from pplkit.bootstrap import doc_bootstrap_ppl, paired_doc_bootstrap_diff

class TrueModel:
    def __init__(self, src): self.src = src
    def logprobs(self, d): return np.r_[np.log(self.src.pi[d[0]]), np.log(self.src.P[d[:-1], d[1:]])]

def test_conditionals_sum_to_one():
    src = MarkovSource(20, seed=1); m = NGram(20, 2, 0.1).fit(src.sample_docs(50, 100, 0)); assert np.allclose(m.cond().sum(1), 1.0)

def test_uniform_model_perplexity_equals_vocabulary_size():
    class Uniform: 
        def logprobs(self, d): return np.full(len(d), -math.log(30))
    assert math.isclose(perplexity(Uniform(), [np.arange(10), np.arange(5)]), 30)

def test_true_model_matches_entropy_rate_and_floor_holds():
    src = MarkovSource(30, seed=2); test = src.sample_docs(400, 100, 99); true_ppl = perplexity(TrueModel(src), test)
    assert abs(math.log(true_ppl) - src.entropy_rate) < 0.03               # note: each document's first token costs H(π), not the rate, adding ≈ (H(π) − H_rate)/L nats per token
    m = NGram(30, 2, 0.05).fit(src.sample_docs(2000, 100, 1)); assert perplexity(m, test) >= true_ppl * 0.98       # cannot beat the source beyond sampling noise

def test_bigram_beats_unigram():
    src = MarkovSource(30, seed=3); tr, te = src.sample_docs(1000, 100, 1), src.sample_docs(300, 100, 2)
    uni, bi = NGram(30, 1, 0.5).fit(tr), NGram(30, 2, 0.05).fit(tr); assert perplexity(bi, te) < perplexity(uni, te)

def test_training_perplexity_is_lower_only_when_the_model_can_overfit():
    gaps = []
    for seed in range(10):                                                     # 4,000 training tokens, 900 parameters, almost no smoothing: genuine overfitting
        src = MarkovSource(30, seed=200 + seed); tr, te = src.sample_docs(40, 100, 1), src.sample_docs(300, 100, 2); bi = NGram(30, 2, 0.01).fit(tr)
        gaps.append(perplexity(bi, te) - perplexity(bi, tr))
    assert min(gaps) > 0                                                       # in a seeded run this held for 40/40 sources (mean gap ≈ 1.2); with 100k tokens it held for only 16/20

def test_bootstrap_interval_contains_estimate_and_paired_diff_is_positive():
    src = MarkovSource(30, seed=4); tr, te = src.sample_docs(1500, 100, 1), src.sample_docs(300, 100, 2)
    uni, bi = NGram(30, 1, 0.5).fit(tr), NGram(30, 2, 0.05).fit(tr)
    est, lo, hi = doc_bootstrap_ppl(bi, te, B=500); assert lo <= est <= hi
    d, lo2, hi2 = paired_doc_bootstrap_diff(uni, bi, te, B=500); assert lo2 > 0                                   # the bigram is better, beyond noise
```

`[VERIFY]` Confirm the numeric tolerances (`0.03` nats on the entropy rate, the `0.98` floor factor) by running the tests over several seeds; they depend on the test-set size. **Document-boundary effect:** the true model's measured perplexity on 100-token documents was about 1.4% above `exp(H_rate)` (7.768 vs 7.658 in a seeded run) because each document's first token costs the stationary entropy `H(π)` rather than the entropy rate, adding about `(H(π) − H_rate)/L` nats per token; for floor comparisons use the true model's perplexity on the *same test documents* as the reference, not `exp(H_rate)`. The original "training perplexity < test perplexity" assertion held for only 16 of 20 sources at 100,000 training tokens (there is no overfitting at that size), so the test now uses a 4,000-token training set. Verify that every `NGram.cond()` row sums to 1 for both orders.

### 9.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Source entropy rate verified against `−(1/N) Σ log P` on 10⁶ simulated tokens within sampling error; conditionals sum to 1 for every model |
| M2 | R4–R5 | All sanity checks pass (uniform = `V`; true model ≈ `exp(H_rate)`; floor; train < test; shuffled test worse for bigram) |
| M3 | R6–R7 | Smoothing U-curves for ≥ 3 training sizes with optimum `α` reported; interpolation weights fit on validation data |
| M4 | R8–R9 | Document-bootstrap intervals; paired differences; word-vs-character comparability table with BPC |
| M5 | R10–R11 | Floor analysis; leakage and domain-shift experiments quantified |
| M6 | R12 | `REPORT.md` regenerated by one script; every claim has an interval and `N` documents |

### 9.5 Statistical-honesty requirements

- Report **tokens, documents, tokenizer, vocabulary size, unknown-token policy, and context order** with every perplexity.
- Intervals come from **document-level** resampling; state the number of documents.
- Distinguish **a measured perplexity slightly below the floor** (sampling noise on a finite test set) from a genuine violation; show that the gap shrinks with more test data.
- Present at least one result where a bigger model is **not significantly better** than a simpler one (e.g., a trigram with too little data).

### 9.6 Failure modes to demonstrate

Zero-probability test tokens; evaluating on training data; duplicate/leaked documents; mixed log bases; comparing word-level and character-level perplexity; averaging per-document perplexities; token-level bootstrap intervals that are too narrow; a vocabulary built on the test set; very small `α` with a small training set.

### 9.7 Stretch goals

1. Order-2 Markov source and a true trigram model; show the bigram's irreducible gap `exp(H_rate(2)) − …`.
2. Interpolated Kneser–Ney smoothing and comparison with additive/interpolated models `[VERIFY: formula]`.
3. A tiny neural bigram/MLP language model trained by cross-entropy (Module 08) and compared with the count-based model; verify it approaches the same perplexity.
4. Byte-level modelling of real text you have locally and bits-per-byte vs a general-purpose compressor available in the standard library (`zlib`, `lzma`); explain the gap.
5. Perplexity as a data-shift detector: evaluate a model on drifted sources and calibrate an alert threshold by bootstrap.

### 9.8 ML connection (README prompt)

Write the "perplexity reporting checklist" you would require in a model review (dataset and split, tokenizer and vocabulary, context length, unknown-token policy, document-level uncertainty, comparability across tokenizers), and say which of your experiments justifies each line.

### Check yourself (Unit 9)

1. Why bootstrap documents rather than tokens?
2. What is the best possible perplexity on text from a known Markov source?
3. Why can a measured test perplexity fall slightly below the source's theoretical floor?

**Reference answers:** (1) Tokens within a document are dependent, so token-level resampling understates variability; documents are the approximately independent units. (2) `exp(H_rate)` (nats), the exponentiated entropy rate. (3) The floor applies to the *expected* cross-entropy; a finite test sample can by chance be easier than average, and the gap shrinks as the test set grows.

---

## Unit 10 — Project: Entropy and KL explorer (`Projects/02-…md`)

### 10.1 Brief

Build `infoviz`: a validated information-theory library (entropy, cross-entropy, KL, JS, mutual information from a joint table) and an exploration notebook that visualizes how these quantities behave: binary entropy, KL between Bernoulli pairs, Gaussian KL (closed form vs numerical), **forward vs reverse KL fits**, **estimator bias** (plug-in entropy, histogram KL), and a **drift monitor with calibrated thresholds**.

**Industry framing:** every training-loss, distillation, and monitoring pipeline depends on a handful of these functions being right. The deliverable is the tested library plus the evidence of when naive estimators mislead.

### 10.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | Core functions | `entropy`, `cross_entropy`, `kl`, `js`, `mutual_information(joint)`, all with a `base` argument, input validation (non-negative, sums to 1), the `0 log 0 = 0` convention, and explicit behaviour for `q = 0`; log-space paths from logits (`log_softmax`, `ce_from_logits`) |
| R2 | Identity test suite | On ≥ 10,000 random distribution pairs: `H(p, q) = H(p) + KL(p‖q)`; `KL ≥ 0`; `KL(p‖p) = 0`; `JS` symmetric and `≤ ln 2`; `I(X;Y) = H(X) + H(Y) − H(X,Y) = KL(joint‖product)`; chain rule; all to `1e-12` |
| R3 | Known-answer tests | Gaussian KL closed form vs numerical integration (≤ `1e-6`); binary entropy at `p = ½`; uniform entropy `log K`; Huffman bound; Markov entropy rate vs sample average |
| R4 | Visual explorer | Figures (headless): binary-entropy curve; heatmap of `KL(Bern(a)‖Bern(b))` and its asymmetry; entropy vs temperature of a softmax; Gaussian KL surface; each with a one-sentence takeaway |
| R5 | Forward vs reverse KL | Fit a single Gaussian to (a) a bimodal mixture, (b) a heavy-tailed (Student-`t`-like) target, (c) a skewed target, by grid search under both directions; report fitted parameters and the KL values; explain mode-covering vs mode-seeking |
| R6 | Estimator-bias study | Plug-in and Miller–Madow entropy bias vs `n` and `K`; histogram-based KL bias vs bins and `n`; Monte Carlo KL with the correct standard error; report with ≥ 500 repetitions per cell and their SEs |
| R7 | Drift monitor | Features with known drift scenarios (mean shift, variance change, new category, slow drift); metrics: PSI, KL (smoothed), JS; **thresholds calibrated by simulating no-drift windows at the production sample size** for a stated false-alarm rate; detection power and delay tables; compare with the fixed 0.1/0.25 PSI rules of thumb |
| R8 | Information gain | Decision-stump information gain on synthetic data; high-cardinality-ID pathology and the gain-ratio fix `[VERIFY]` |
| R9 | Calibration link | Show that cross-entropy decomposes into a calibration part and a refinement part on a binned reliability table (conceptual check on synthetic predictions) `[VERIFY: decomposition]`; compare log-loss, accuracy, and a calibration error for three predictors |
| R10 | Report | `REPORT.md`: identity tables, estimator-bias tables with SEs, forward/reverse fits, drift-monitor calibration, and a "which quantity when" decision guide |

### 10.3 Layout and starter

```
infoviz/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/infoviz/{__init__,core,gaussians,estimators,drift,plots}.py
├── tests/{test_core,test_gaussians,test_estimators,test_drift}.py
├── notebooks/13_entropy_kl_explorer.ipynb
└── results/
```

```python
# src/infoviz/core.py
import math
import numpy as np

def _check(p, name="p"):
    p = np.asarray(p, float)
    if np.any(p < 0) or not np.isclose(p.sum(), 1.0, atol=1e-8): raise ValueError(f"{name} must be a probability vector (non-negative, sums to 1)")
    return p

def entropy(p, base=math.e):
    p = _check(p); nz = p > 0; return float(-(p[nz] * np.log(p[nz])).sum() / math.log(base))

def cross_entropy(p, q, base=math.e):
    p, q = _check(p, "p"), _check(q, "q")
    if np.any((p > 0) & (q == 0)): return math.inf
    nz = p > 0; return float(-(p[nz] * np.log(q[nz])).sum() / math.log(base))

def kl(p, q, base=math.e):
    p, q = _check(p, "p"), _check(q, "q")
    if np.any((p > 0) & (q == 0)): return math.inf
    nz = p > 0; return float((p[nz] * (np.log(p[nz]) - np.log(q[nz]))).sum() / math.log(base))

def js(p, q, base=math.e): m = (_check(p) + _check(q)) / 2; return 0.5 * kl(p, m, base) + 0.5 * kl(q, m, base)

def mutual_information(joint, base=math.e):
    J = _check(np.asarray(joint, float).ravel()).reshape(np.shape(joint)); px, py = J.sum(1), J.sum(0)
    return kl(J.ravel(), np.outer(px, py).ravel(), base)

def log_softmax(z): z = np.asarray(z, float); m = z.max(); return z - (m + math.log(np.exp(z - m).sum()))
def ce_from_logits(z, p): return float(-np.dot(_check(p), log_softmax(z)))
```

```python
# src/infoviz/estimators.py
import math
import numpy as np
from .core import entropy

def plug_in_entropy(sample, K, base=math.e): return entropy(np.bincount(sample, minlength=K) / len(sample), base)
def miller_madow_entropy(sample, K, base=math.e):
    c = np.bincount(sample, minlength=K); return plug_in_entropy(sample, K, base) + (np.count_nonzero(c) - 1) / (2 * len(sample)) / math.log(base)
def smoothed_hist(sample, edges, alpha=0.5): c = np.histogram(sample, bins=edges)[0] + alpha; return c / c.sum()
```

```python
# src/infoviz/drift.py
import numpy as np
from .core import kl

def psi(a, e): a, e = np.asarray(a, float), np.asarray(e, float); return float(np.sum((a - e) * np.log(a / e)))
def calibrate_threshold(stat_fn, null_sampler, reps=2000, false_alarm=0.01, seed=0):
    """Threshold = the (1 − false_alarm) quantile of the statistic over no-drift windows drawn by null_sampler(rng)."""
    g = np.random.default_rng(seed); vals = np.array([stat_fn(null_sampler(g)) for _ in range(reps)]); return float(np.quantile(vals, 1 - false_alarm))
```

```python
# tests/test_core.py
import math, numpy as np, pytest
from infoviz.core import entropy, cross_entropy, kl, js, mutual_information, log_softmax, ce_from_logits

def test_identities_on_random_distributions():
    g = np.random.default_rng(0)
    for _ in range(3000):
        p, q = g.dirichlet(np.ones(8)), g.dirichlet(np.ones(8))
        assert math.isclose(cross_entropy(p, q), entropy(p) + kl(p, q), abs_tol=1e-12) and kl(p, q) >= -1e-12
        assert math.isclose(js(p, q), js(q, p), abs_tol=1e-12) and js(p, q) <= math.log(2) + 1e-12
    assert math.isclose(kl(p, p), 0.0, abs_tol=1e-12)

def test_mutual_information_equals_entropy_identity_and_independence_gives_zero():
    g = np.random.default_rng(1); J = g.dirichlet(np.ones(12)).reshape(3, 4); px, py = J.sum(1), J.sum(0)
    assert math.isclose(mutual_information(J), entropy(px) + entropy(py) - entropy(J.ravel()), abs_tol=1e-12)
    assert math.isclose(mutual_information(np.outer(px, py)), 0.0, abs_tol=1e-12)

def test_support_mismatch_is_infinite_and_validation_rejects_bad_inputs():
    assert kl([0.5, 0.5], [1.0, 0.0]) == math.inf and math.isfinite(kl([1.0, 0.0], [0.5, 0.5]))
    with pytest.raises(ValueError): entropy([0.5, 0.6])
    with pytest.raises(ValueError): kl([-0.1, 1.1], [0.5, 0.5])

def test_ce_from_logits_matches_probability_form_and_is_stable():
    z = np.array([2.0, 1.0, 0.0]); p = np.array([1.0, 0, 0]); q = np.exp(log_softmax(z)); assert math.isclose(ce_from_logits(z, p), cross_entropy(p, q), abs_tol=1e-12)
    assert np.isfinite(ce_from_logits(np.array([1000.0, 0.0, -1000.0]), np.array([0, 0, 1.0])))
```

```python
# tests/test_estimators.py
import math, numpy as np
from infoviz.estimators import plug_in_entropy, miller_madow_entropy
from infoviz.core import entropy

def test_plugin_is_biased_low_and_bias_shrinks_with_n():
    g = np.random.default_rng(0); K = 20; p = g.dirichlet(np.ones(K) * 2); H = entropy(p)
    bias = {}
    for n in (30, 300, 3000):
        bias[n] = np.mean([plug_in_entropy(g.choice(K, size=n, p=p), K) for _ in range(800)]) - H
    assert bias[30] < bias[300] < bias[3000] <= 0.01 and bias[30] < -0.05

def test_miller_madow_reduces_the_bias():
    g = np.random.default_rng(1); K = 20; p = g.dirichlet(np.ones(K) * 2); H = entropy(p); n = 50
    plug = np.mean([plug_in_entropy(g.choice(K, size=n, p=p), K) for _ in range(1500)]) - H
    mm = np.mean([miller_madow_entropy(g.choice(K, size=n, p=p), K) for _ in range(1500)]) - H
    assert abs(mm) < abs(plug)
```

`[VERIFY]` Confirm the bias thresholds in `test_plugin_is_biased_low_and_bias_shrinks_with_n` by running over seeds (they depend on the Dirichlet draw and `K`). Add `gaussians.py` (closed-form KL and the grid-fit routines from Lesson 4) and `plots.py` per the requirements.

### 10.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R3 | Identity suite passes at `1e-12` on ≥ 10,000 pairs; known-answer tests pass; invalid input rejected with clear errors |
| M2 | R4 | Figures regenerate headlessly from one script; each has a takeaway sentence |
| M3 | R5 | Forward/reverse fits for three targets: parameters and KL values tabulated; the bimodal case reproduces the covering/locking behaviour |
| M4 | R6 | Bias tables (≥ 500 repetitions per cell, with SEs) for entropy and histogram-KL estimators; Miller–Madow and smoothing effects quantified |
| M5 | R7 | Drift scenarios with calibrated thresholds at a stated false-alarm rate (verified by an independent no-drift simulation), power/delay tables, and the comparison with the fixed PSI rules of thumb |
| M6 | R8–R10 | Information-gain study; calibration link; `REPORT.md` regenerated by one script with the decision guide |

### 10.5 Statistical-honesty requirements

- Report estimator **bias with a standard error**, and state the number of repetitions per cell.
- The calibrated drift threshold's realized false-alarm rate must be **verified on an independent no-drift simulation** and reported with its binomial SE.
- Say what the forward/reverse fits depend on (grid range, resolution, restriction to one mode) and that results are for the chosen targets.
- Include a drift scenario that the monitor **misses** (e.g., a change confined to a rarely occupied bin) and discuss why.

### 10.6 Failure modes to demonstrate

Empty bins giving `inf` KL; mixed log bases; unnormalized inputs; KL direction swapped; plug-in entropy at tiny `n`; histogram KL with too many bins; fixed PSI thresholds at small `n`; JS mistaken for a metric on unnormalized data; mutual information of a joint with zero margins.

### 10.7 Stretch goals

1. Entropy and KL for continuous distributions via differential entropy and kernel density estimates; show the bandwidth sensitivity.
2. Mutual-information-based feature ranking compared with correlation on nonlinear dependencies.
3. A tiny variational fit: minimize reverse KL between a Gaussian and a non-Gaussian target by gradient descent (Module 08) and compare with the grid result.
4. Temperature-scaling calibration of softmax outputs minimizing cross-entropy on a validation set `[VERIFY]`.
5. Bootstrap confidence intervals for the plug-in and Miller–Madow estimates on real categorical data you have locally.

### 10.8 ML connection (README prompt)

For each of distillation, an RLHF-style KL penalty, a VAE, and a drift monitor, state which function from your library it uses, the direction of KL, and the failure mode from this project that you would test for first.

### Check yourself (Unit 10)

1. Why calibrate drift thresholds by simulating no-drift windows?
2. What does the forward-vs-reverse KL fit to a bimodal target show?
3. Why is the plug-in entropy estimator biased low?

**Reference answers:** (1) The null distribution of a divergence estimate depends on sample size and binning, so only a threshold calibrated at your production `n` delivers a known false-alarm rate. (2) Forward KL produces a broad fit covering both modes; reverse KL locks onto a single mode. (3) Empirical frequencies make the sample look less diverse than the true distribution (rare categories are missed or under-represented), which lowers the estimated uncertainty.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 5 lessons, 2 projects, 10 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to Modules 05–12, 4C-05/06/07/10, and Stage 5 pointers (5A-05/08/10, 5B-02/04/06/07/13, 5C-01/08–11, 5D-10/12) are derived from folder names only.
3. `[VERIFY]` Statements to confirm or cite before the final lesson files assert them: Huffman bound statement, Miller–Madow correction, concavity/maximum-entropy facts, JS-metric property, PSI as symmetrized KL and its rule-of-thumb thresholds, Stein's lemma, KL direction used in specific RLHF/trust-region methods, Kneser–Ney formula, the calibration–refinement decomposition, gain ratio.
4. `[VERIFY]` All printed numerical results (entropies, perplexities, estimator biases, drift thresholds) by running the code; report your own numbers rather than quoting any ratio.
5. `[VERIFY]` Starter code was run (NumPy 2.3, pytest 9): every lesson snippet executed; all 6 `pplkit` and all 6 `infoviz` tests passed. Defects found and fixed during the run: the worked-example Jensen–Shannon value (0.1017 nats, not 0.1109); a flaky "training perplexity < test perplexity" assertion (true in only 16 of 20 sources at 100,000 training tokens; now a 4,000-token overfitting setup that held in 40 of 40 sources); and the "floor" reference for short documents (see the document-boundary note in §9). Measured in seeded runs: (a) Huffman average lengths satisfied `H ≤ L < H + 1` (e.g., entropy 1.319 bits vs average length 1.450 for a skewed distribution); (b) the plug-in entropy estimator's bias for `K = 20` was −0.734 / −0.302 / −0.072 / −0.013 / −0.001 bits at `n = 20 / 50 / 200 / 1,000 / 10,000`, and Miller–Madow's was −0.353 / −0.079 / −0.005 / +0.001 / 0.000; (c) cross-entropy identities held to `1e-12` on random pairs; honest vs over-confident predictors with equal accuracy (0.699) had log-loss 0.611 vs 1.391; the label-smoothed optimum logit gap at `ε = 0.1`, `K = 5` was 3.83; (d) Gaussian KL closed form matched numerical integration (0.350182 vs 0.350182); the grid-fit forward KL minimizer was `(μ, σ) = (0, 3.25)` (covering both modes) and the reverse KL minimizer `(3, 1)` (one mode); (e) PSI under no drift had mean 0.041 / 0.0085 / 0.0010 at `n = 200 / 1,000 / 10,000`; calibrated 1% false-alarm thresholds were 0.1014 / 0.0201 / 0.0022 (realized false-alarm 0.0083 / 0.0123 / 0.0157, within the calibration noise), detecting a 0.3σ mean shift with power 0.69 / 1.00 / 1.00, while the fixed rule-of-thumb threshold 0.1 detected it with power 0.61 / 0.38 / 0.02; (f) language models from a known Markov source (30 symbols): true entropy rate 1.9358 nats (ideal perplexity 6.929, uniform baseline 30); on a long single chain the true model scored 6.865 and a bigram 6.879 (both slightly below the floor: sampling noise); the unigram scored 25.5; with only 3,000 training tokens `α = 1e-9` gave 12.98 vs 7.73 at `α = 0.5`; (g) with 100-token documents the best-`α` bigram's test perplexity versus the true model's 7.768 on the same documents closed from a gap of 2.11 at 1,000 training tokens to 0.008 at 300,000; duplicating 10% of the test documents into training lowered their perplexity from 8.70 to 7.44; a model trained on one source scored perplexity 1,305 on a different source (far *worse* than the uniform baseline of 30); document-bootstrap 95% interval for the bigram was 7.73–7.92 and the paired NLL difference (unigram − bigram) was 1.248 nats [1.237, 1.260]. Re-run after any change.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] Every quantity states its log base; no perplexity, entropy, KL, or threshold appears without the measurement that produced it and its uncertainty.
