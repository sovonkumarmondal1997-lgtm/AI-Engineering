# SYLLABUS — 04-Similarity-Distance-and-Embedding-Geometry (S4B-04)

**Stage 4B — Mathematics for Machine Learning · Module 04 · beginner → advanced**

> Conventions: `[VERIFY]` = re-check before relying on it. `[JUDGEMENT]` = practitioner opinion. All code is Python 3.11+ with NumPy (Matplotlib and pytest where stated; no SciPy required). This file is the blueprint for the files in §0; each unit lists teaching content, code, failure modes, ML links, labs, and self-checks that the final file must contain.

---

## 0. Module map

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Module orientation | `README.md` | Beginner |
| 2 | Cosine similarity | `01-cosine-similarity.md` | Beginner → Intermediate |
| 3 | Euclidean vs cosine vs dot-product similarity | `02-euclidean-versus-cosine-versus-dot-product-similarity.md` | Intermediate |
| 4 | High-dimensional geometry and the curse of dimensionality | `03-high-dimensional-geometry-and-the-curse-of-dimensionality.md` | Intermediate → Advanced |
| 5 | Practice question bank | `practice-questions.md` | All levels |
| 6 | Project index | `Projects/README.md` | Intermediate |
| 7 | Project: word-vector similarity explorer | `Projects/01-word-vector-similarity-explorer.md` | Intermediate → Advanced |
| 8 | Project: curse-of-dimensionality experiments | `Projects/02-curse-of-dimensionality-experiments.md` | Intermediate → Advanced |

**Prerequisites:** Module 01 (dot product, norms, cosine, projection), Module 02 (matrix products and shapes, `XXᵀ`), Module 03 (SVD, low-rank structure; used in Project 1). **Plan slot:** week 5 of `../00-Stage-4-Overview/learning-plan.md`. This module is deferrable on the eval-focused track, but it is the geometry behind retrieval and RAG `[JUDGEMENT]`.

**Every lesson uses the six beats:** Why ML needs this → Intuition → Mechanics → Code (from scratch, library-style, assertion they agree) → Failure modes → ML link. Shapes are written in comments throughout.

---

## Unit 1 — Module orientation (`README.md`)

### 1.1 Why this module matters

Retrieval, RAG, semantic search, recommendation, deduplication, clustering, k-NN, and contrastive learning all reduce to one question: **which vectors are "close"?** The answer depends on a choice (cosine, dot product, Euclidean) that engineers often make by copying a tutorial. Making it wrongly can quietly degrade search quality, bias results toward popular or long items, or make an index return nonsense. In high dimensions, intuition from 2-D and 3-D also fails in specific, predictable ways; knowing them is what separates debugging from guessing.

### 1.2 Outcomes

1. Compute cosine similarity and cosine/angular distance for single pairs, matrices, and sparse-like inputs, handling zero vectors and precision.
2. Explain when cosine, dot product, and Euclidean distance give the **same ranking** and when they differ, using `‖a−b‖² = ‖a‖² + ‖b‖² − 2a·b`.
3. Decide which measure to use from how the embedding model was trained, and verify the choice on labelled queries.
4. Implement exact top-`k` search with matrix products and `argpartition`, and explain what approximate indexes trade away.
5. Demonstrate and explain distance concentration, near-orthogonality of random vectors, ball-volume collapse, and hubness.
6. Choose and test remedies: normalization, dimensionality reduction, intrinsic-dimension estimates, evaluation by recall.
7. Build a word-vector explorer and a curse-of-dimensionality experiment suite with honest, measured results.

### 1.3 Lesson sequence

| Order | Lesson | ML anchor | Lab output |
|---|---|---|---|
| 1 | Cosine similarity | Semantic search, TF-IDF, embeddings | `cosine`, pairwise matrix, top-k |
| 2 | Euclidean vs cosine vs dot | Metric choice, MIPS, norm bias | Ranking-agreement experiment |
| 3 | High-dimensional geometry | k-NN decay, ANN indexes, hubness | Concentration and volume experiments |

### 1.4 Concept map

```
vectors (Module 01) ─► cosine = dot of unit vectors ─► angular distance
                                 │
dot product ◄── ‖a−b‖² = ‖a‖²+‖b‖²−2a·b ──► Euclidean distance
      │                  (equal ranking iff norms equal / vectors normalized)
      └──► MIPS: norm matters ─► popularity / length bias
high dimension d ─► distances concentrate ─► relative contrast → 0 ─► hubness ─► need: normalize, reduce (PCA/SVD, Module 03), evaluate recall
```

### 1.5 Environment and rules

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" matplotlib pytest      # scikit-learn and scipy optional for cross-checks
```

Seed randomness; compare with `np.allclose`; report measured numbers only; **evaluate similarity choices on a labelled retrieval set, never by eyeballing a few examples**.

### 1.6 Checkpoint (module-level)

Given any embedding matrix `E: (N, d)`, you can (a) build cosine top-`k` search without Python loops, (b) show that after L2-normalization cosine, dot, and Euclidean give identical rankings, and (c) produce a distance-concentration plot for `d ∈ {2, 10, 100, 1000}` with your own numbers.

### Check yourself (Unit 1)

1. Name three applications that rest on "which vectors are close?"
2. Why should a similarity choice be validated on labelled queries?

**Reference answers:** (1) Semantic search/RAG, recommendation, deduplication (also k-NN classification and clustering). (2) Visual inspection of a few examples is biased and cannot detect systematic failures such as length bias; recall/precision on labelled queries can.

---

## Unit 2 — Cosine similarity (`01-…md`)

### 2.1 Why ML needs this

Text and image embeddings are compared with cosine more than any other measure. It ignores vector length, which often reflects document length or frequency rather than meaning, and compares **direction** only.

### 2.2 Intuition

Two arrows pointing the same way are "similar" regardless of how long they are. Cosine is `+1` for the same direction, `0` for perpendicular, `−1` for opposite. In non-negative spaces (e.g., TF-IDF), values lie in `[0, 1]`.

### 2.3 Mechanics

- `cos(a, b) = a·b / (‖a‖‖b‖)` ∈ `[−1, 1]` (Cauchy–Schwarz, Module 01).
- **Normalize first:** with `â = a/‖a‖`, `cos(a, b) = â·b̂`. A matrix of unit rows `Ê` gives all pairwise cosines as `Ê Êᵀ: (N, N)`.
- **Cosine distance** `1 − cos(a, b)` ∈ `[0, 2]`. It is **not a metric**: the triangle inequality can fail. **Angular distance** `arccos(cos(a, b))/π` **is** a metric. This matters for metric-tree indexes and for proofs, less for ranking.
- **Scale invariance:** `cos(αa, b) = cos(a, b)` for `α > 0`; `α < 0` flips the sign.
- **Not shift-invariant:** adding a constant to every coordinate changes cosine. **Mean-centering** first turns cosine into **Pearson correlation** (`cos(a − ā𝟙, b − b̄𝟙)`). This is the right measure when vectors have an arbitrary per-vector offset (e.g., user rating bias).
- **Dataset-level centering:** subtracting the dataset mean vector from all embeddings often improves cosine-based retrieval when embeddings share a large common component (anisotropy) `[JUDGEMENT; validate on your data]`.
- **Zero vector:** cosine is undefined (`0/0`). Decide the policy (return `0`, `nan`, or raise) and document it.
- **Precision:** float32 normalization is usually fine for ranking, but values can land at `1.0000001`; clip before `arccos`.
- **Top-`k`:** compute scores `S = Q Êᵀ`, then `np.argpartition(-S, k)[:k]` is `O(N)` per query versus `O(N log N)` for a full sort; sort only the `k` winners.

**Worked example:** `a = (1, 2, 3)`, `b = (2, 4, 6)`: `cos = 1` (same direction) though `‖a − b‖ ≈ 3.74`. For `a = (1, 0)`, `b = (0, 1)`: `cos = 0`.

### 2.4 Code

```python
import numpy as np

def l2_normalize(X, axis=-1, eps=1e-12):
    X = np.asarray(X, dtype=float)
    n = np.linalg.norm(X, axis=axis, keepdims=True)
    return X / np.maximum(n, eps)                      # zero vectors stay zero (cosine to anything = 0)

def cosine(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.clip(l2_normalize(a) @ l2_normalize(b), -1.0, 1.0))

def cosine_matrix(A, B=None):
    """A: (n, d), B: (m, d) -> (n, m)."""
    An = l2_normalize(A)
    Bn = An if B is None else l2_normalize(B)
    return An @ Bn.T

def top_k(query, E_norm, k=5):
    """query: (d,), E_norm: (N, d) unit rows -> (indices, scores) sorted by descending cosine."""
    scores = E_norm @ l2_normalize(query)              # (N,)
    k = min(k, len(scores))
    idx = np.argpartition(-scores, k - 1)[:k]
    idx = idx[np.argsort(-scores[idx])]
    return idx, scores[idx]

rng = np.random.default_rng(0)
a, b = np.array([1., 2., 3.]), np.array([2., 4., 6.])
assert np.isclose(cosine(a, b), 1.0) and np.isclose(cosine(a, -b), -1.0)
E = rng.normal(size=(1000, 64)); En = l2_normalize(E)
q = rng.normal(size=64)
idx, sc = top_k(q, En, 5)
full = np.argsort(-(En @ l2_normalize(q)))[:5]
assert np.array_equal(idx, full)                       # same as the O(N log N) full sort

# Pearson = cosine of centered vectors
x, y = rng.normal(size=50), rng.normal(size=50)
assert np.isclose(cosine(x - x.mean(), y - y.mean()), np.corrcoef(x, y)[0, 1])

# cosine distance is not a metric: triangle inequality can fail
p, q_, r = np.array([1., 0.]), np.array([1., 1.]), np.array([0., 1.])
d = lambda u, v: 1 - cosine(u, v)
print(d(p, r), "vs", d(p, q_) + d(q_, r))              # 1.0  vs  ≈ 0.586 → d(p,r) > d(p,q)+d(q,r)
assert d(p, r) > d(p, q_) + d(q_, r)

# angular distance is a metric
ang = lambda u, v: np.arccos(np.clip(cosine(u, v), -1, 1)) / np.pi
assert ang(p, r) <= ang(p, q_) + ang(q_, r) + 1e-12

# zero-vector policy
print(cosine(np.zeros(3), np.array([1., 2., 3.])))     # 0.0 by our documented policy
```

TF-IDF-style demo (pure NumPy, tiny corpus):

```python
docs = ["the cat sat on the mat", "the dog sat on the log", "stock prices fell sharply today"]
vocab = sorted({w for d in docs for w in d.split()})
tf = np.array([[d.split().count(w) for w in vocab] for d in docs], float)
df = (tf > 0).sum(axis=0)
tfidf = tf * np.log((1 + len(docs)) / (1 + df) + 1)    # a common smoothed variant; check your library's variant
print(np.round(cosine_matrix(tfidf), 2))               # docs 0 and 1 similar; doc 2 near 0
```

### 2.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Dividing by a zero norm | `nan` scores propagate into sorting | `eps` clamp and a documented policy |
| Using cosine **distance** where a metric is required | Metric-tree or proof assumptions break | Use angular distance, or normalize and use Euclidean |
| Comparing cosine across differently-trained models | Scores aren't comparable | Compare ranks / evaluate per model |
| Treating raw cosine values as calibrated probabilities | Thresholds drift across models and domains | Calibrate a threshold on labelled pairs |
| Skipping centering when all vectors share a big mean component | Everything looks similar (high baseline cosine) | Inspect the mean cosine of random pairs; try centering |
| `float16` normalization | Visible ranking noise | Normalize in `float32` or higher |
| Full `N×N` cosine matrix on large `N` | Memory blow-up (`N²` floats) | Block/chunked top-`k`, or an ANN index |
| `np.argsort` on every query | Needless `O(N log N)` | `argpartition` + sort the `k` |

### 2.6 ML link

- **Semantic search / RAG:** embed query and chunks, rank by cosine (Stage 5C-06; the RAG stack is in the agents/LLM stages `[VERIFY]` placement).
- **TF-IDF classifiers and clustering** (Stage 5A-10): cosine on sparse vectors.
- **Contrastive learning:** losses often compute cosine similarity of normalized embeddings, scaled by a temperature (Stage 5C-06) `[VERIFY]`.
- **Deduplication:** a cosine threshold on embeddings flags near-duplicates; choose the threshold from labelled pairs.
- **Recommenders:** item-item cosine on interaction vectors (Stage 5B-09).

### 2.7 Lab (60 min)

1. Implement `l2_normalize`, `cosine`, `cosine_matrix`, `top_k`; test against a brute-force loop on 100 random queries.
2. Show scale invariance, sign flip, shift sensitivity, and Pearson equivalence numerically.
3. Reproduce the triangle-inequality failure and the angular-distance fix.
4. Build the TF-IDF mini-example; add a duplicated document twice as long and show cosine ignores the length while raw dot product does not.
5. Timing: full sort vs `argpartition` for `N ∈ {1e4, 1e5}`; record your machine and NumPy version.

### Check yourself (Unit 2)

1. What is cosine similarity of `(3, 4)` and `(6, 8)`? Of `(1, 1)` and `(−1, −1)`?
2. Why is cosine distance not a metric?
3. How does mean-centering change cosine, and what is it called then?

**Reference answers:** (1) `1`; `−1`. (2) The triangle inequality can fail (example above). (3) It removes a per-vector offset and yields the Pearson correlation coefficient.

---

## Unit 3 — Euclidean vs cosine vs dot-product similarity (`02-…md`)

### 3.1 Why ML needs this

Vector databases and libraries expose several metrics (L2, inner product, cosine). They are **not interchangeable**. Picking by habit can bias results toward long vectors (popular items, long documents) or break an index built under a different metric.

### 3.2 Intuition

- **Euclidean** asks "how far apart are the tips?" (sensitive to length and offset).
- **Dot product** asks "how aligned *and* how large?" (rewards large norms).
- **Cosine** asks "how aligned?" only.

If all vectors have the same length, all three tell the same story.

### 3.3 Mechanics

- **Master identity:** `‖a − b‖² = ‖a‖² + ‖b‖² − 2 a·b`.
- **Unit-norm case:** `‖a − b‖² = 2 − 2cos(a, b)`, so ranking by smallest Euclidean distance = ranking by largest cosine = ranking by largest dot product.
- **General case (varying norms):** for a fixed query `q`, ranking items `x` by
  - cosine: `q·x / ‖x‖` (item norm divides out),
  - dot product: `q·x` (item norm rewards),
  - Euclidean (ascending): `‖x‖² − 2q·x` (item norm *penalizes* large `‖x‖` while the dot term rewards it).
  These can rank differently.
- **MIPS (maximum inner product search)** is the problem "find the `x` maximizing `q·x`" and is **not** the same as nearest-neighbour search when norms vary. A standard reduction adds one coordinate to turn MIPS into Euclidean NN `[VERIFY: construction and its caveats]`.
- **Norm bias:** in many models, vector norm correlates with frequency or popularity; with dot product, frequent items dominate results. In recommenders the learned item norm can encode popularity `[JUDGEMENT; test in your data]`.
- **Choose by training objective:** use the metric the model was trained/evaluated with (model card or paper); if embeddings are trained with normalized cosine, normalize at index time; if trained for inner product, don't normalize `[VERIFY per model]`.
- **Other measures (brief):**

| Measure | Use | Note |
|---|---|---|
| Manhattan (L1) | Robust to a few large coordinate differences | Less affected by single outlier dimensions than L2 |
| Mahalanobis | Account for feature covariance: `√((a−b)ᵀΣ⁻¹(a−b))` | Needs a stable `Σ⁻¹` (Module 02, Lesson 8; shrinkage) |
| Hamming / Jaccard | Binary or set data | Not for dense real embeddings |
| Learned metric | Metric learning, cross-encoders | Beyond this stage |

- **Approximate NN indexes** (IVF, HNSW, product quantization) trade recall for speed and are built **for one metric**; switching metric means rebuilding `[VERIFY: library specifics]`. Always report **recall@k against exact search** on a sample.

**Worked example:** `q = (1, 0)`; `x₁ = (1, 0)` and `x₂ = (10, 5)`. Dot: `1` vs `10` (`x₂` wins); cosine: `1` vs `0.894` (`x₁` wins); Euclidean: `0` vs `√106 ≈ 10.3` (`x₁` wins). Metrics disagree.

### 3.4 Code

```python
import numpy as np
rng = np.random.default_rng(0)

def l2_normalize(X, eps=1e-12):
    return X / np.maximum(np.linalg.norm(X, axis=-1, keepdims=True), eps)

def scores(Q, E, kind):
    """Q: (q, d), E: (N, d) -> (q, N); higher is better for every kind."""
    if kind == "dot":
        return Q @ E.T
    if kind == "cosine":
        return l2_normalize(Q) @ l2_normalize(E).T
    if kind == "euclid":
        d2 = (Q ** 2).sum(1)[:, None] + (E ** 2).sum(1)[None, :] - 2 * Q @ E.T
        return -np.sqrt(np.maximum(d2, 0.0))             # negate: smaller distance = better
    raise ValueError(kind)

def topk_idx(S, k):
    idx = np.argpartition(-S, k - 1, axis=1)[:, :k]
    order = np.argsort(-np.take_along_axis(S, idx, axis=1), axis=1)
    return np.take_along_axis(idx, order, axis=1)

def overlap_at_k(A, B):                                   # mean fraction of shared top-k items
    return float(np.mean([len(set(a) & set(b)) / len(a) for a, b in zip(A, B)]))

# 1) unit-norm: all three agree exactly
E = l2_normalize(rng.normal(size=(2000, 32))); Q = l2_normalize(rng.normal(size=(50, 32)))
tops = {k: topk_idx(scores(Q, E, k), 10) for k in ("dot", "cosine", "euclid")}
assert np.array_equal(tops["dot"], tops["cosine"]) and np.array_equal(tops["dot"], tops["euclid"])

# 2) varying norms (e.g., popularity-scaled): the metrics diverge
norms = rng.lognormal(mean=0.0, sigma=0.8, size=(2000, 1))
E2 = l2_normalize(rng.normal(size=(2000, 32))) * norms
tops2 = {k: topk_idx(scores(Q, E2, k), 10) for k in ("dot", "cosine", "euclid")}
for a, b in (("dot", "cosine"), ("dot", "euclid"), ("cosine", "euclid")):
    print(a, "vs", b, "top-10 overlap:", round(overlap_at_k(tops2[a], tops2[b]), 3))   # report your own numbers

# 3) the item-norm bias: how many results are high-norm items?
nrm = norms.ravel()
for k in ("dot", "cosine", "euclid"):
    print(k, "mean norm of returned items:", round(float(nrm[tops2[k]].mean()), 3), "| catalogue mean:", round(float(nrm.mean()), 3))

# the worked example
q = np.array([[1., 0.]]); X = np.array([[1., 0.], [10., 5.]])
for k in ("dot", "cosine", "euclid"):
    print(k, scores(q, X, k).round(3))                    # winners differ

# identity check
a, b = rng.normal(size=8), rng.normal(size=8)
assert np.isclose(np.sum((a - b) ** 2), a @ a + b @ b - 2 * a @ b)
```

Mahalanobis with a regularized covariance (never invert a raw covariance blindly):

```python
X = rng.normal(size=(500, 3)) @ np.array([[3., 0, 0], [1., 0.5, 0], [0, 0, 0.2]])
mu = X.mean(0); S = np.cov(X.T) + 1e-6 * np.eye(3)
def mahalanobis(a, b):
    d = a - b
    return float(np.sqrt(d @ np.linalg.solve(S, d)))     # solve, not inv (Module 02)
print(mahalanobis(X[0], X[1]), np.linalg.norm(X[0] - X[1]))
```

Evaluation harness (the part that actually decides the metric):

```python
def recall_at_k(retrieved, relevant_sets, k):
    """retrieved: (q, >=k) index array; relevant_sets: list of sets of relevant ids."""
    return float(np.mean([len(set(r[:k]) & rel) / max(1, min(k, len(rel))) for r, rel in zip(retrieved, relevant_sets)]))
```

### 3.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Normalizing vectors from a model trained for raw inner product | Lost signal in norm; relevance drops | Follow the model's training metric; A/B on labelled queries |
| Using dot product with unnormalized embeddings in a heterogeneous corpus | Long/popular items dominate | Normalize, or correct for norm; check returned-norm statistics |
| Building an ANN index under one metric and querying under another | Silent recall loss | Rebuild; record the metric in index metadata |
| Treating "L2 index + normalized vectors" as different from cosine | Unnecessary confusion | They give identical rankings (identity above) |
| Using cosine on features with wildly different scales that are not embeddings | One feature dominates | Standardize first (Module 01, Lesson 4) |
| Trusting a threshold from one metric after switching | Wrong cutoffs | Re-calibrate on labelled pairs |
| Evaluating only on a few hand-picked queries | Missed systematic bias | Use a labelled set and report recall@k / MRR |
| Inverting a covariance in Mahalanobis without shrinkage | Unstable distances | Regularize; `solve` not `inv` |

### 3.6 ML link

- **Vector databases / RAG retrieval:** the index metric must match the embedding model (Stage 5C-06 and downstream `[VERIFY]`).
- **Recommenders:** inner product of user and item factors; item norms capture popularity (Stage 5B-09).
- **Attention (Stage 5C-07):** dot-product scores `q·k/√d`, where norms matter by design, which is why attention is **not** cosine.
- **Clustering (Stage 5A-09):** k-means uses Euclidean; spherical k-means normalizes and effectively uses cosine.
- **Duplicate detection and k-NN classification:** metric choice changes neighbours and accuracy; validate.

### 3.7 Lab (90 min)

1. Verify the identity and the unit-norm equivalence for 5 random datasets; assert identical rankings.
2. Overlap experiment: sweep the norm-variance `σ ∈ {0, 0.25, 0.5, 1.0}`; plot top-10 overlap between each metric pair vs `σ`.
3. Build a small labelled retrieval set from synthetic clusters whose **relevance is defined by direction only**, with item norms randomly scaled. Show recall@10 for each metric, and explain which metric wins and why. Then invert the construction (relevance tied to norm) and show the winner changes.
4. Compute the mean norm of returned items per metric and relate it to popularity bias.
5. Mahalanobis vs Euclidean on correlated data; show where they disagree.

### Check yourself (Unit 3)

1. For unit-norm vectors, how do `‖a−b‖²`, `cos`, and `a·b` relate?
2. In the worked example, which item does each metric rank first?
3. Why does attention not use cosine?

**Reference answers:** (1) `‖a−b‖² = 2 − 2a·b = 2 − 2cos`. (2) Dot product: `x₂`; cosine and Euclidean: `x₁`. (3) Attention is trained with unnormalized dot products where vector magnitude carries useful information (and the `1/√d` scale controls their size); it is a design choice, not an accident `[VERIFY: 4C-09]`.

---

## Unit 4 — High-dimensional geometry and the curse of dimensionality (`03-…md`)

### 4.1 Why ML needs this

Embeddings have hundreds to thousands of dimensions, and tabular features can too. Several things that are true in 2-D fail in high dimension: "nearest" and "farthest" become nearly indistinguishable, random directions are almost perpendicular, and volume concentrates in a thin shell. These explain why k-NN degrades with irrelevant features, why exact search gets expensive, why indexes need approximations, and why a few items ("hubs") appear in everyone's neighbour list.

### 4.2 Intuition

- **Space is mostly corners and shell.** Almost all of a high-dimensional cube's volume is near its surface and far from its centre; a unit ball occupies a vanishing fraction of the cube that contains it.
- **Distances concentrate.** Between random points, the nearest and farthest distances become close in relative terms.
- **Directions decorrelate.** Two random vectors are nearly orthogonal: their cosine concentrates at `0` with spread about `1/√d`.
- **Data is rarely truly high-dimensional.** Real data often lies near a lower-dimensional structure (intrinsic dimension), which is why ML still works.

### 4.3 Mechanics

- **Near-orthogonality:** for independent random directions in `ℝᵈ`, `Var(cos θ) = 1/d` (for isotropic Gaussians), so the angle concentrates near 90°.
- **Concentration of distances:** for i.i.d. coordinates, `‖x − y‖²` is a sum of `d` terms; its mean grows like `d` while its standard deviation grows like `√d`, so the **coefficient of variation shrinks like `1/√d`**.
- **Relative contrast:** `RC(d) = (D_max − D_min)/D_min` over distances from a query to `N` points. It tends to shrink as `d` grows for i.i.d. data; exact rates depend on the distribution and `N` `[VERIFY: cite specific theorem if stated in the final file]`.
- **Ball volume:** `V_d(r) = π^{d/2} r^d / Γ(d/2 + 1)`. The unit ball's volume peaks around `d = 5` and then falls toward 0; the ratio to the enclosing cube `[−1,1]ᵈ` is `V_d(1)/2ᵈ → 0` very fast.
- **Shell concentration:** fraction of a ball's volume within radius `(1−ε)r` is `(1−ε)ᵈ`; for `ε = 0.01`, `d = 1000`, that is `≈ 4.3e-5`, so nearly all volume lies in the outer 1% shell.
- **Gaussian norm concentration:** for `x ~ N(0, I_d)`, `‖x‖ ≈ √d` with `O(1)` fluctuations. Samples lie on a thin spherical shell, not near the origin.
- **Hubness:** in high dimension some points appear in the `k`-NN lists of many others (**hubs**), while others appear in none (anti-hubs). Measure with the **`k`-occurrence** `N_k(x)` distribution and its skewness. Hubness is stronger for dense, high-intrinsic-dimension data and with some metrics `[JUDGEMENT]`; centering or normalization sometimes reduces it, and it must be tested.
- **Irrelevant features hurt k-NN:** adding `m` pure-noise features to `p` informative ones inflates distance variance and lowers neighbour quality.
- **Intrinsic dimension:** estimate from the PCA/SVD spectrum (Module 03), "participation ratio" `(Σλ)²/Σλ²`, or neighbour-distance-ratio estimators `[VERIFY: method before relying on it]`.
- **Practical remedies:** (1) feature selection and standardization; (2) dimensionality reduction (PCA/SVD, random projection; Johnson–Lindenstrauss preserves pairwise distances up to `1±ε` with about `log N/ε²` dimensions `[VERIFY: constants]`); (3) normalization and centering; (4) ANN indexes; (5) **measure recall/quality**, since asymptotic worry doesn't replace an evaluation.
- **When the "curse" is milder than feared:** data on low-dimensional manifolds, strongly clustered data, and learned embeddings optimized for retrieval often retain useful contrast `[JUDGEMENT]`.

### 4.4 Code

```python
import numpy as np
import math
rng = np.random.default_rng(0)

# 1) near-orthogonality: std of cosine between random vectors ≈ 1/sqrt(d)
def random_cosines(d, n=20000):
    U, V = rng.normal(size=(n, d)), rng.normal(size=(n, d))
    return np.sum(U * V, 1) / (np.linalg.norm(U, axis=1) * np.linalg.norm(V, axis=1))
for d in (2, 10, 100, 1000):
    c = random_cosines(d)
    print(f"d={d:5d}  std(cos)={c.std():.4f}  1/sqrt(d)={1/np.sqrt(d):.4f}")

# 2) relative contrast of distances
def relative_contrast(d, N=2000, trials=20):
    out = []
    for _ in range(trials):
        X = rng.random((N, d)); q = rng.random(d)             # uniform in the unit cube
        D = np.linalg.norm(X - q, axis=1)
        out.append((D.max() - D.min()) / D.min())
    return float(np.mean(out))
for d in (2, 10, 100, 1000):
    print(f"d={d:5d}  relative contrast={relative_contrast(d):.3f}")   # shrinks with d; report your own numbers

# 3) ball volume and ball/cube ratio (log-space to avoid under/overflow)
def log_ball_volume(d, r=1.0):
    return (d / 2) * math.log(math.pi) + d * math.log(r) - math.lgamma(d / 2 + 1)
for d in (1, 2, 3, 5, 10, 20, 50, 100):
    v = math.exp(log_ball_volume(d)); ratio = math.exp(log_ball_volume(d) - d * math.log(2))
    print(f"d={d:3d}  V={v:10.4g}  ball/cube={ratio:.3e}")
assert math.isclose(math.exp(log_ball_volume(2)), math.pi) and math.isclose(math.exp(log_ball_volume(3)), 4 * math.pi / 3)

# 4) Monte-Carlo check of ball/cube ratio at small d
for d in (2, 5, 10):
    P = rng.uniform(-1, 1, size=(200_000, d))
    print(d, "MC:", (np.linalg.norm(P, axis=1) <= 1).mean(), "exact:", math.exp(log_ball_volume(d) - d * math.log(2)))

# 5) shell concentration and Gaussian norms
for d in (10, 100, 1000):
    print(d, "fraction of volume in the outer 1% shell:", 1 - 0.99 ** d)
X = rng.normal(size=(5000, 1000)); n = np.linalg.norm(X, axis=1)
print("||x|| mean/std for d=1000:", n.mean(), n.std(), "sqrt(d) =", np.sqrt(1000))

# 6) k-NN with irrelevant features: signal drowned by noise dimensions
def knn_accuracy(n_noise, n=600, p=2, k=5, seed=0):
    g = np.random.default_rng(seed)
    y = g.integers(0, 2, n)
    signal = g.normal(size=(n, p)) + 3.0 * y[:, None]         # two classes separated in p dims
    X = np.hstack([signal, g.normal(size=(n, n_noise))])
    tr, te = slice(0, n // 2), slice(n // 2, n)
    D2 = (X[te] ** 2).sum(1)[:, None] + (X[tr] ** 2).sum(1)[None] - 2 * X[te] @ X[tr].T
    nn = np.argsort(D2, axis=1)[:, :k]
    pred = (y[tr][nn].mean(1) > 0.5).astype(int)
    return float((pred == y[te]).mean())
for m in (0, 10, 100, 1000):
    print(f"noise dims={m:5d}  kNN accuracy={knn_accuracy(m):.3f}")

# 7) hubness: skewness of the k-occurrence distribution
def k_occurrence_skew(d, N=2000, k=10, seed=0):
    g = np.random.default_rng(seed); X = g.normal(size=(N, d))
    D2 = (X ** 2).sum(1)[:, None] + (X ** 2).sum(1)[None] - 2 * X @ X.T
    np.fill_diagonal(D2, np.inf)
    nn = np.argpartition(D2, k, axis=1)[:, :k]
    Nk = np.bincount(nn.ravel(), minlength=N).astype(float)
    return float(((Nk - Nk.mean()) ** 3).mean() / Nk.std() ** 3), int(Nk.max())
for d in (3, 20, 100, 500):
    print(f"d={d:4d}  skewness, max N_k = {k_occurrence_skew(d)}")      # report your own numbers

# 8) remedy: PCA (via SVD, Module 03) when data lives on a low-dimensional subspace
Z = rng.normal(size=(1000, 5)) @ rng.normal(size=(5, 200)) + 0.05 * rng.normal(size=(1000, 200))
Zc = Z - Z.mean(0); s = np.linalg.svd(Zc, compute_uv=False)
lam = s ** 2
print("participation ratio (effective dim):", lam.sum() ** 2 / (lam ** 2).sum())   # near 5, not 200
```

### 4.5 Failure modes

| Mistake | Symptom | Guard |
|---|---|---|
| Assuming 2-D/3-D intuition about "nearest" holds in 1000-D | Poor retrieval, no obvious bug | Measure relative contrast and recall |
| Adding features "just in case" to a k-NN model | Accuracy collapses as noise dims grow | Feature selection; standardize; reduce |
| Treating the curse as universal | Over-engineering on data with low intrinsic dimension | Estimate intrinsic dimension first |
| Computing `V_d(r)` with the naive formula for large `d` | Overflow/underflow | Work in log space with `lgamma` |
| Ignoring hubness | A handful of items dominate every result list | Check the `N_k` distribution; try centering, normalization, or rank-based corrections `[VERIFY]` |
| Evaluating ANN speed without recall | Fast but wrong | Always report recall@k vs exact |
| Distance-threshold rules reused across `d` | Thresholds meaningless | Calibrate per dataset and dimension |
| Using a tiny `N` to claim concentration results | Noisy conclusions | Report `N`, repetitions, and variability |
| Random projection to too few dimensions | Distance distortion | Check distortion on a sample before adopting |

### 4.6 ML link

- **k-NN / kernel methods / clustering** degrade with irrelevant or redundant features (Stage 5A-09).
- **Retrieval at scale** needs ANN indexes; recall/latency trade-offs (Stage 5D-09, 5D-10 `[VERIFY]`).
- **Embedding dimension choice and compression:** reducing dimension (PCA, truncation, quantization) trades storage for quality; measure it (Module 03, Lesson 4).
- **Anomaly detection in high-dimensional spaces:** distance-based detectors lose contrast (Stage 5B-06).
- **Regularization and overfitting:** more features than samples (`d ≥ n`) creates degenerate geometry (Module 02, Lesson 9; Module 14).
- **Initialization scales** use `1/√d`-type factors to keep activations stable, the same concentration idea (Stage 4C-07, 5C-03 `[VERIFY]`).

### 4.7 Lab (90 min)

1. Reproduce experiments 1–5 above; make a 2×2 figure (cosine histograms; relative contrast vs `d`; ball/cube ratio vs `d`; shell fraction vs `d`) from your own runs.
2. Run the k-NN noise-dimension experiment with 5 seeds; plot mean ± std accuracy vs noise dimensions; then fix it with (a) feature selection (drop the known-noise features) and (b) PCA to `p` components, and compare.
3. Compute `N_k` skewness for Gaussian data of increasing `d`; then apply centering and L2-normalization and measure whether skewness changes.
4. Estimate intrinsic dimension of three datasets you generate (low-rank + noise, a swiss-roll-like curve in 50-D, i.i.d. Gaussian) using the participation ratio; discuss where the estimate is misleading (the curve is non-linear).
5. Write a half-page "runbook": *What I check before trusting nearest-neighbour results in a new embedding space.*

### Check yourself (Unit 4)

1. What is the approximate standard deviation of the cosine between two random vectors in `ℝ¹⁰⁰⁰`?
2. What fraction of a 1000-D ball's volume lies in the outer 1% shell?
3. Name two remedies for k-NN degradation due to irrelevant features.

**Reference answers:** (1) About `1/√1000 ≈ 0.032`. (2) `1 − 0.99¹⁰⁰⁰ ≈ 0.99996`. (3) Feature selection/standardization and dimensionality reduction (e.g., PCA); also validating by recall.

---

## Unit 5 — Practice question bank (`practice-questions.md`)

### 5.1 Structure

About 36 items in four tiers (`L1` recall, `L2` apply, `L3` debug/analyze, `L4` design), roughly 9 per tier, each with a hidden answer and a one-line rationale. Mix hand calculations (2-D/3-D), "predict the ranking", runnable code, and retrieval-design judgement.

### 5.2 Item template

```
### Q<n> [L<level>] <topic>
<question>
<details><summary>Answer</summary>
<answer + why + code if relevant>
</details>
```

### 5.3 Seed items

**Q1 [L1] Range.** What range can cosine similarity take for non-negative vectors? → `[0, 1]`.
**Q2 [L2] Hand calc.** `cos((1, 2), (2, 1))`? → `4/5 = 0.8`.
**Q3 [L2] Identity.** `a = (3, 4)`, `b = (0, 5)`; verify `‖a−b‖² = ‖a‖²+‖b‖²−2a·b`. → `9 + 1 = 10`; `25 + 25 − 40 = 10`.
**Q4 [L2] Unit norm.** Unit vectors with `a·b = 0.6`. What is `‖a−b‖`? → `√(2 − 1.2) = √0.8 ≈ 0.894`.
**Q5 [L2] Ranking.** `q = (1, 0)`, `x₁ = (2, 0)`, `x₂ = (1, 1)`. Rank under dot, cosine, Euclidean. → Dot: `x₁` (2) > `x₂` (1); cosine: `x₁` (1) > `x₂` (0.707); Euclidean distance: `x₁` (1) vs `x₂` (1): tie. (Highlights that ties and disagreements arise even in tiny cases.)
**Q6 [L2] Concentration.** Std of cosine of random vectors at `d = 400`? → `≈ 1/20 = 0.05`.
**Q7 [L3] Debug.** `arccos(cos)` returns `nan` occasionally. → Rounding beyond ±1; clip.
**Q8 [L3] Debug.** Search returns many near-duplicate chunks and the mean pairwise cosine of random chunk pairs is 0.8. Why and what to try? → Shared mean component (anisotropy); subtract the dataset mean (and re-normalize); validate with recall.
**Q9 [L3] Debug.** A vector DB built with an inner-product index gives different results than your cosine code on the same embeddings. → Embeddings are not unit norm; normalize or switch the index metric; compare rankings.
**Q10 [L3] Analysis.** After adding 300 extra features, k-NN accuracy drops from 0.95 to 0.62. Explain and fix. → Noise dimensions dominate distances; remove or down-weight them, standardize, reduce dimensionality.
**Q11 [L3] Analysis.** One document appears in the top-10 of 40% of queries. → Possible hub; inspect `N_k`, its norm, and whether centering or normalization removes it.
**Q12 [L4] Design.** You must pick a metric for a new embedding model with no documentation. → Test cosine/dot/L2 on a labelled set (recall@k, MRR), check norm statistics, and verify whether norms carry information; pick the best and record it in the index metadata.
**Q13 [L4] Design.** You want to cut index memory 4× by reducing dimension. → Measure recall@k vs dimension for PCA/truncation/quantization on held-out queries; choose the smallest dimension meeting the quality bar.
**Q14 [L4] Design.** Design a duplicate-detection threshold. → Build labelled positive/negative pairs, plot score distributions, choose the threshold by precision/recall target, and re-validate when the model changes.

### 5.4 Coverage matrix

| Topic | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Cosine | 2 | 3 | 2 | 1 |
| Metric comparison and MIPS | 2 | 3 | 3 | 2 |
| High-dimensional geometry | 2 | 3 | 3 | 2 |
| Evaluation and index design | 1 | 1 | 1 | 2 |

### Check yourself (Unit 5)

1. Why does the seed set include a tie case (Q5)?
2. Which items need runnable code?

**Reference answers:** (1) Rankings near ties are fragile; learners should know to expect and handle them. (2) L3 debug items and any question whose answer depends on floating-point or random-sample behaviour.

---

## Unit 6 — Project index (`Projects/README.md`)

### 6.1 Catalogue

| # | Project | Proves | Lessons | Est. time `[JUDGEMENT]` |
|---|---|---|---|---|
| 1 | Word-vector similarity explorer | Build embeddings, run neighbours and analogies, compare metrics, evaluate | 1–2 (and Module 03) | 5–6 h |
| 2 | Curse-of-dimensionality experiments | Reproducible experiments with honest statistics | 3 | 4–5 h |

Order: 1 → 2 (Project 2 reuses the `scores` and `top_k` helpers). Outputs feed `mlmath/similarity.py` in the stage library (`../../00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`, deliverable D5) and notebook `04_similarity.ipynb`.

### 6.2 Data policy

**No downloads are required.** Project 1 builds embeddings from a small synthetic corpus generated in code (so tests are deterministic). You may optionally load pretrained vectors you already have locally (GloVe/word2vec text format) through the same loader; keep such files out of the repository and out of tests `[VERIFY: licence of any vectors you use]`.

### 6.3 Rubric (100 points; pass 70 with correctness at its own bar)

| Criterion | Points |
|---|---|
| Correctness vs reference (brute-force loops, identities, known values) | 30 |
| Failure-mode handling (zero vectors, ties, `k > N`, NaN) | 15 |
| Reproducibility (seeded, pinned, clean venv; no downloads required) | 15 |
| Explanation quality (what each plot shows and why it matters for retrieval/ML) | 15 |
| Code quality (types, shape docstrings) | 15 |
| ML connection paragraph | 10 |

### 6.4 Standard layout

```
project/
├── README.md  requirements.txt
├── src/<pkg>/…   tests/test_*.py   notebooks/*.ipynb   results/
```

### Check yourself (Unit 6)

1. Why is the synthetic-corpus approach used?
2. Which stage-library deliverable do these projects feed?

**Reference answers:** (1) Deterministic tests, no dependency on downloads or licences. (2) D5 (`mlmath/similarity.py`).

---

## Unit 7 — Project: Word-vector similarity explorer (`Projects/01-…md`)

### 7.1 Brief

Build `wordsim`: construct word embeddings from a synthetic corpus (co-occurrence → PPMI → truncated SVD, tying to Module 03), then build an explorer for nearest neighbours, analogies, metric comparison, and a small evaluation, with an optional loader for real pretrained vectors.

**Industry framing:** teams validate any new embedding space by inspecting neighbours, testing known relations, and measuring retrieval quality on labelled pairs, and they log which metric the index uses.

### 7.2 Requirements

| # | Feature | Spec |
|---|---|---|
| R1 | `make_corpus(seed, p_topic, n_sentences)` | Synthetic sentences from topic word lists (e.g., animals, vehicles, fruits, tech) with shared function words; deterministic; difficulty controlled by `p_topic` and `n_sentences`; returns plain `str` tokens |
| R2 | `cooccurrence(sentences, window)` | Symmetric word-word counts `C: (V, V)` |
| R3 | `ppmi(C, alpha)` | Positive PMI with optional context smoothing `[VERIFY: smoothing variant]`; guards `log(0)` |
| R4 | `embed(P, dim)` | Truncated SVD (`U_k √s_k` or `U_k s_k`: document your choice) |
| R5 | `Vocab` helper | `word → id`, `id → word`, safe lookup with a clear `KeyError` message |
| R6 | `neighbors(word, metric, k)` | `metric ∈ {cosine, dot, euclid}`; excludes the query word; handles ties deterministically |
| R7 | `analogy(a, b, c, k)` | Returns top-`k` for `b − a + c` excluding `a, b, c`; reports cosine scores |
| R8 | Metric comparison | For a set of query words, report top-`k` overlap between metrics and the mean norm of returned words (norm/frequency bias) |
| R9 | Evaluation | Same-topic retrieval: for each word, precision@`k` of neighbours being in the same topic; compare metrics and dimensions |
| R10 | Dimension sweep | `dim ∈ {2, 5, 10, 20, 50}`: precision@`k` and mean pairwise cosine of random word pairs (anisotropy) |
| R11 | Centering experiment | Subtract the mean vector, re-normalize; measure R9 before/after |
| R12 | Optional loader | `load_text_vectors(path, limit)` for local GloVe-style files; same API |
| R13 | Failure handling | OOV word, zero vector, `k > V`, empty corpus, `dim > V` |

### 7.3 Layout and starter

```
wordsim/
├── pyproject.toml  requirements.txt  README.md
├── src/wordsim/{__init__,corpus,embed,search,evaluate}.py
├── tests/{test_corpus,test_embed,test_search,test_evaluate}.py
├── notebooks/04_word_vectors.ipynb
└── results/
```

```python
# src/wordsim/corpus.py
import numpy as np

TOPICS = {
    "animals":  ["cat", "dog", "horse", "cow", "sheep", "lion", "tiger", "wolf"],
    "vehicles": ["car", "bus", "train", "truck", "bike", "plane", "boat", "tram"],
    "fruits":   ["apple", "pear", "grape", "mango", "peach", "plum", "lemon", "melon"],
    "tech":     ["laptop", "server", "router", "cloud", "kernel", "compiler", "database", "network"],
}
FUNCTION = ["the", "a", "and", "with", "near", "of", "is", "was"]

def make_corpus(n_sentences=6000, length=8, seed=0, p_topic=0.7):
    """Each sentence is drawn mostly from one topic's words plus function words."""
    rng = np.random.default_rng(seed)
    names = list(TOPICS)
    out = []
    for _ in range(n_sentences):
        t = TOPICS[names[rng.integers(len(names))]]
        sent = [str(rng.choice(t)) if rng.random() < p_topic else str(rng.choice(FUNCTION)) for _ in range(length)]
        out.append(sent)
    return out

def word_topic():
    return {w: t for t, ws in TOPICS.items() for w in ws}
```

```python
# src/wordsim/embed.py
import numpy as np

def build_vocab(sentences):
    words = sorted({w for s in sentences for w in s})
    return {w: i for i, w in enumerate(words)}, words

def cooccurrence(sentences, w2i, window=3):
    V = len(w2i); C = np.zeros((V, V))
    for s in sentences:
        ids = [w2i[w] for w in s]
        for i, a in enumerate(ids):
            for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                if i != j:
                    C[a, ids[j]] += 1.0
    return C

def ppmi(C, alpha=0.75):
    """Positive PMI with context-distribution smoothing exponent alpha."""
    total = C.sum()
    pw = C.sum(1, keepdims=True) / total
    pc = C.sum(0, keepdims=True) ** alpha
    pc = pc / pc.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((C / total) / (pw * pc))
    pmi[~np.isfinite(pmi)] = 0.0
    return np.maximum(pmi, 0.0)

def embed(P, dim=10):
    if dim > min(P.shape):
        raise ValueError(f"dim={dim} exceeds min(P.shape)={min(P.shape)}")
    U, s, _ = np.linalg.svd(P, full_matrices=False)
    return U[:, :dim] * np.sqrt(s[:dim])
```

```python
# src/wordsim/search.py
import numpy as np

def _scores(q, E, metric):
    if metric == "dot":
        return E @ q
    if metric == "cosine":
        return (E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)) @ (q / max(np.linalg.norm(q), 1e-12))
    if metric == "euclid":
        return -np.linalg.norm(E - q, axis=1)
    raise ValueError(f"unknown metric {metric!r}")

def neighbors(word, E, w2i, words, k=5, metric="cosine"):
    if word not in w2i:
        raise KeyError(f"{word!r} is not in the vocabulary")
    i = w2i[word]
    s = _scores(E[i], E, metric).astype(float)
    s[i] = -np.inf                                         # exclude the query itself
    k = min(k, len(words) - 1)
    order = np.lexsort((np.arange(len(s)), -s))[:k]        # ties broken by index: deterministic
    return [(words[j], float(s[j])) for j in order]

def analogy(a, b, c, E, w2i, words, k=3):
    """Words x such that a : b :: c : x, via b - a + c (cosine ranking, inputs excluded)."""
    q = E[w2i[b]] - E[w2i[a]] + E[w2i[c]]
    s = _scores(q, E, "cosine").astype(float)
    for w in (a, b, c):
        s[w2i[w]] = -np.inf
    order = np.lexsort((np.arange(len(s)), -s))[:k]
    return [(words[j], float(s[j])) for j in order]
```

```python
# src/wordsim/evaluate.py
import numpy as np
from .search import neighbors
from .corpus import word_topic

def precision_at_k(E, w2i, words, k=5, metric="cosine"):
    topic = word_topic()
    scored = [w for w in words if w in topic]
    hits = []
    for w in scored:
        nb = [n for n, _ in neighbors(w, E, w2i, words, k=k, metric=metric)]
        hits.append(np.mean([topic.get(n) == topic[w] for n in nb]))
    return float(np.mean(hits))

def mean_random_cosine(E, n=5000, seed=0):
    g = np.random.default_rng(seed)
    i, j = g.integers(0, len(E), n), g.integers(0, len(E), n)
    keep = i != j
    A, B = E[i[keep]], E[j[keep]]
    c = np.sum(A * B, 1) / np.maximum(np.linalg.norm(A, axis=1) * np.linalg.norm(B, axis=1), 1e-12)
    return float(c.mean())
```

```python
# tests/test_search.py
import numpy as np
from wordsim.corpus import make_corpus
from wordsim.embed import build_vocab, cooccurrence, ppmi, embed
from wordsim.search import neighbors
from wordsim.evaluate import precision_at_k

def build(dim=10, seed=0):
    s = make_corpus(n_sentences=3000, seed=seed)
    w2i, words = build_vocab(s)
    return embed(ppmi(cooccurrence(s, w2i)), dim), w2i, words

def test_topic_structure_is_recovered():
    E, w2i, words = build()
    assert precision_at_k(E, w2i, words, k=5) > 0.8       # well above 0.25 (chance with 4 topics)

def test_neighbors_exclude_query_and_are_deterministic():
    E, w2i, words = build()
    a = neighbors("cat", E, w2i, words, k=5); b = neighbors("cat", E, w2i, words, k=5)
    assert a == b and all(w != "cat" for w, _ in a)

def test_oov_raises_clear_error():
    E, w2i, words = build()
    try:
        neighbors("zebra", E, w2i, words)
        assert False
    except KeyError as e:
        assert "zebra" in str(e)
```

### 7.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1–R5 | Corpus deterministic for a seed; `C` symmetric; `PPMI ≥ 0` with no `nan`/`inf`; `embed` rejects `dim` larger than the vocabulary |
| M2 | R6–R7, R13 | Neighbours of a topic word are mostly in the same topic; every failure case in R13 raises a clear error |
| M3 | R8 | Table of top-`k` overlap between metric pairs and mean returned-word norm for 20 queries, from your own run |
| M4 | R9–R11 | Precision@`k` table by metric × dimension; anisotropy (mean random-pair cosine) before/after centering; a one-paragraph interpretation |
| M5 | R12 (optional) and notebook | Same code path runs on local pretrained vectors if available; notebook runs end to end seeded |

### 7.5 Questions the write-up must answer

1. Which metric gives the best precision@`k`, and does the answer change when the dimension changes?
2. Do returned words under dot product skew toward high-norm (frequent) words? Show the norms.
3. What happens to the mean random-pair cosine as you change `dim`, and what does centering do to it?
4. Do analogies work on this synthetic corpus? Why or why not (what structure does the corpus actually contain)?
5. What would you measure before trusting these embeddings in a retrieval product?

### 7.6 Failure-mode table (README, ≥ 8 rows)

Seed with: corpus too easy so every metric scores 1.0 (make it harder); OOV query; ties in scores; `k > V`; zero-count words (all-zero PPMI rows → zero vectors); `dim > V`; forgetting to exclude the query word; analogy returning one of its inputs; dot product dominated by frequent words.

### 7.7 Stretch goals

1. Replace PPMI+SVD with a tiny skip-gram trained by SGD in NumPy (links to Stage 5C-06 and Module 08) and compare precision@`k`.
2. Add a bias probe: make a corpus with a skewed co-occurrence of two word groups and measure association with a cosine-based score (WEAT-style) `[VERIFY: method]`. Discuss limits of such probes.
3. Add an exact-vs-approximate comparison: random-projection hashing (LSH-style) top-`k` vs exact; report recall@`k` and measured time.
4. Visualize the space with PCA to 2-D; label points; explain what the picture can and cannot show.
5. Evaluate on a real local vector file if you have one, and report how results differ from the synthetic corpus.

### 7.8 ML connection (README prompt)

Relate the explorer to: embedding-based retrieval, the relationship between PPMI+SVD and neural embeddings `[VERIFY: stated equivalence holds under specific conditions]`, and why an index's metric must match training.

### Check yourself (Unit 7)

1. Why exclude the query word from its own neighbours?
2. Why can a synthetic corpus still teach something real about embeddings?
3. What does a high mean random-pair cosine suggest?

**Reference answers:** (1) Its similarity to itself is the maximum and would occupy rank 1 uselessly. (2) The pipeline (co-occurrence → PPMI → SVD → metric choice → evaluation) is the same, and the ground-truth topics let you measure quality exactly. (3) Anisotropy: embeddings share a large common component; consider centering and check the effect on retrieval quality.

---

## Unit 8 — Project: Curse-of-dimensionality experiments (`Projects/02-…md`)

### 8.1 Brief

Build `cursekit`: a reproducible experiment suite that measures distance concentration, near-orthogonality, volume effects, k-NN degradation with noise features, hubness, and the effect of remedies, with confidence intervals across seeds and honest conclusions about when the "curse" applies.

**Industry framing:** experiment reports state `N`, seeds, variability, and limits. A claim like "high dimensions break nearest neighbours" is replaced by a measured, scoped statement.

### 8.2 Requirements

| # | Experiment | Spec |
|---|---|---|
| R1 | Cosine concentration | `std(cos)` vs `d` for Gaussian, uniform-cube, and sparse random vectors; compare with `1/√d` |
| R2 | Relative contrast | `(D_max − D_min)/D_min` vs `d` for `N ∈ {100, 1000, 10000}`; also under L1, L2, and cosine distance |
| R3 | Volume | Ball volume, ball/cube ratio, shell fraction in log space; Monte-Carlo cross-check for small `d` |
| R4 | Gaussian shell | Distribution of `‖x‖` vs `√d` |
| R5 | Noise-feature k-NN | Accuracy vs number of noise dims, over ≥ 10 seeds with mean ± standard error; fix with feature selection and PCA |
| R6 | Hubness | `N_k` skewness and max vs `d`, under raw / centered / normalized data |
| R7 | Structured vs unstructured data | Repeat R2 and R6 on low-rank-plus-noise and clustered data; show the curse is milder when intrinsic dimension is low |
| R8 | Intrinsic dimension | Participation ratio (and one other estimator you choose, documented) for each data family |
| R9 | Random projection | Distortion of pairwise distances vs target dimension; compare with the Johnson–Lindenstrauss guideline, honestly reporting where it is loose |
| R10 | Report | `REPORT.md` with figures, tables with `N`, seeds, uncertainty, and a "what we can and cannot conclude" section |
| R11 | Harness | One CLI `python -m cursekit run --all --seed 0 --out results/`; every figure/table regenerates from it |

### 8.3 Layout and starter

```
cursekit/
├── pyproject.toml  requirements.txt  README.md  REPORT.md
├── src/cursekit/{__init__,geometry,knn,hubness,datasets,intrinsic,projection,cli}.py
├── tests/{test_geometry,test_knn,test_hubness,test_datasets,test_projection}.py
├── notebooks/04_curse.ipynb
└── results/
```

```python
# src/cursekit/geometry.py
import math
import numpy as np

def log_ball_volume(d, r=1.0):
    return (d / 2) * math.log(math.pi) + d * math.log(r) - math.lgamma(d / 2 + 1)

def ball_cube_ratio(d):
    """Volume of the unit ball over the cube [-1,1]^d, in log space for stability."""
    return math.exp(log_ball_volume(d) - d * math.log(2))

def shell_fraction(d, eps):
    return 1.0 - (1.0 - eps) ** d

def relative_contrast(X, q, metric="l2"):
    if metric == "l2":
        D = np.linalg.norm(X - q, axis=1)
    elif metric == "l1":
        D = np.abs(X - q).sum(1)
    elif metric == "cosine":
        D = 1 - (X @ q) / (np.linalg.norm(X, axis=1) * np.linalg.norm(q))
    else:
        raise ValueError(metric)
    return float((D.max() - D.min()) / D.min())

def cosine_std(d, n=20000, seed=0):
    g = np.random.default_rng(seed)
    U, V = g.normal(size=(n, d)), g.normal(size=(n, d))
    c = np.sum(U * V, 1) / (np.linalg.norm(U, axis=1) * np.linalg.norm(V, axis=1))
    return float(c.std())
```

```python
# src/cursekit/datasets.py
import numpy as np

def gaussian(n, d, seed=0):
    return np.random.default_rng(seed).normal(size=(n, d))

def low_rank_plus_noise(n, d, rank=5, noise=0.05, seed=0):
    g = np.random.default_rng(seed)
    return g.normal(size=(n, rank)) @ g.normal(size=(rank, d)) + noise * g.normal(size=(n, d))

def clustered(n, d, clusters=8, spread=0.3, seed=0):
    g = np.random.default_rng(seed)
    centers = g.normal(size=(clusters, d)) * 3
    lab = g.integers(0, clusters, n)
    return centers[lab] + spread * g.normal(size=(n, d)), lab
```

```python
# tests/test_geometry.py
import math, numpy as np
from cursekit.geometry import log_ball_volume, ball_cube_ratio, shell_fraction, cosine_std

def test_known_volumes():
    assert math.isclose(math.exp(log_ball_volume(2)), math.pi)
    assert math.isclose(math.exp(log_ball_volume(3)), 4 * math.pi / 3)

def test_ball_cube_ratio_monotone_after_small_d_and_tiny_at_100():
    r = [ball_cube_ratio(d) for d in (2, 3, 5, 10, 20, 50, 100)]
    assert all(a > b for a, b in zip(r, r[1:]))
    assert r[-1] < 1e-60

def test_shell_fraction():
    assert math.isclose(shell_fraction(1000, 0.01), 1 - 0.99 ** 1000)

def test_cosine_std_tracks_inverse_sqrt_d():
    for d in (10, 100, 1000):
        assert abs(cosine_std(d, n=20000) * math.sqrt(d) - 1.0) < 0.05
```

`cursekit.hubness` and `cursekit.knn` follow the Unit 4 code (items 6–7), with the `argpartition` fix noted there (`np.argpartition(D2, k)` after setting the diagonal to `inf`).

### 8.4 Milestones and acceptance

| Step | Work | Acceptance |
|---|---|---|
| M1 | R1, R3–R4 | Theory-vs-measurement tables: `std(cos)·√d` within 5% of 1; Monte-Carlo ball/cube matches the log-space value within sampling error for `d ≤ 10`; `‖x‖/√d → 1` as `d` grows |
| M2 | R2 | Relative contrast curves for 3 metrics × 3 values of `N`, with repetitions and error bars; written statement of what you observe, scoped to the distributions tested |
| M3 | R5 | Accuracy-vs-noise curve over ≥ 10 seeds; feature-selection and PCA fixes shown with the same seeds |
| M4 | R6–R8 | Hubness and intrinsic-dimension tables across the three data families; explicit comparison showing structure mitigates the curse |
| M5 | R9 | JL-style distortion table; honest statement of where the guideline is conservative |
| M6 | R10–R11 | `REPORT.md` regenerated by the single CLI command from a clean venv; every claim has a figure/table with `N` and seeds |

### 8.5 Statistical-honesty requirements

- Report **mean ± standard error** over seeds, not a single run.
- State `N`, `d`, and distribution for every plot.
- Mark any claim that only holds for the tested distributions.
- Include at least one **negative or null result** (e.g., a case where the curse did **not** hurt: clustered or low-rank data) and discuss it.

### 8.6 Failure modes to demonstrate

Overflow in naive ball volume at large `d`; `D_min = 0` (duplicate points) in relative contrast; hubness measured on too-small `N`; comparing metrics at different scales without normalization; using `argsort` on a matrix with `inf` on the diagonal incorrectly; PCA fitted on test data (leakage) in R5; random projection with too few dimensions.

### 8.7 Stretch goals

1. Add a nearest-neighbour approximation (random hyperplane LSH or a tiny IVF) and plot recall@`k` vs speed across `d`; report only measured numbers.
2. Show the effect of the **metric** on hubness (L2 vs cosine vs L1) and of **centering** on cosine hubness.
3. Estimate intrinsic dimension with a neighbour-ratio method (e.g., two-NN) and compare with the participation ratio on a curved manifold `[VERIFY: estimator definition]`.
4. Evaluate a real embedding matrix you have locally: relative contrast, hubness, intrinsic dimension; compare with random data of the same shape.
5. `hypothesis` property tests: scaling data by `α` leaves relative contrast and cosine unchanged.

### 8.8 ML connection (README prompt)

Write a one-page checklist, "Before deploying nearest-neighbour search on a new embedding space", with each item mapped to one experiment in this project.

### Check yourself (Unit 8)

1. Why report mean ± standard error over seeds?
2. Why include a null result?
3. Why is PCA fitted on test data a problem in R5?

**Reference answers:** (1) A single seed may be unrepresentative; uncertainty shows whether differences are real. (2) It scopes the claim: the "curse" depends on data structure, and showing where it fails to bite prevents overgeneralization. (3) It leaks test information into preprocessing and inflates accuracy; fit PCA on the training split only.

---

## Appendix A — Open items

1. `[VERIFY]` Counts: 3 lessons, 2 projects, 8 files in the module (including `README.md`, `practice-questions.md`, `Projects/README.md`).
2. `[VERIFY]` Cross-references to 4C-07 and 4C-09, and Stage 5 module pointers (5A-09, 5A-10, 5B-06, 5B-09, 5C-06, 5C-07, 5D-09, 5D-10); folder-name derived only.
3. `[VERIFY]` Statements about MIPS reductions, ANN index metric dependence, JL constants, relative-contrast rates, hubness behaviour, WEAT-style probes, and PPMI+SVD vs neural-embedding equivalence: confirm or cite before the final lesson files assert them.
4. `[VERIFY]` All printed numerical results (overlaps, accuracies, skewness, contrast, timings) by running the code; report your own numbers.
5. `[VERIFY]` Starter code was run: all 3 `wordsim` tests and all 4 `cursekit` tests passed. With the default corpus (`p_topic=0.7`, 6000 sentences) precision@5 was already 1.0 for `dim ≥ 5` across cosine, dot, and Euclidean, and only `dim=2` separated the metrics (dot was clearly worse). The default corpus is therefore **too easy** to compare metrics; the write-up must also use a harder corpus (lower `p_topic`, fewer sentences, or overlapping topic vocabularies) and report which setting separates the metrics. Re-run to get your own numbers.

## Appendix B — Authoring checklist

- [ ] Each lesson has the six beats, a worked example, code with assertions, a failure-mode table, an ML link, a lab, and a check-yourself.
- [ ] `practice-questions.md` meets the coverage matrix; L3 items have runnable code.
- [ ] Each project has tests, a failure-mode table, seeded outputs, and an ML-connection paragraph.
- [ ] No timing, speed-up, accuracy, or recall figure appears without the measurement that produced it.
