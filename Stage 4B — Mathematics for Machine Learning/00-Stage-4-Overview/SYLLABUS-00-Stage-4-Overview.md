# SYLLABUS — 00-Stage-4-Overview (S4B-00)

**Stage 4B — Mathematics for Machine Learning · orientation, planning, mapping, and integration module**

> Authoring conventions: `[VERIFY]` = a factual claim to re-check before relying on it. `[JUDGEMENT]` = practitioner opinion, not a fact. All code is Python 3.11+ with NumPy, SciPy, SymPy, Matplotlib, pytest. This module does **not** re-teach Modules 01–14. It orients, plans, maps, and integrates, and it links to every lesson instead of repeating it.

---

## 0. How to use this syllabus

This file is the blueprint for six deliverables. Each unit below maps to one file to be written in this folder.

| # | Unit | Target file | Level |
|---|---|---|---|
| 1 | Stage 4B orientation | `README.md` | Beginner |
| 2 | Learning plan and pacing | `learning-plan.md` | Beginner → Intermediate |
| 3 | How 4B connects to 4A and 4C | `how-4b-connects-to-4a-and-4c.md` | Intermediate |
| 4 | Overview project index | `Projects/README.md` | Intermediate |
| 5 | Overview project: Math-for-ML notebook library | `Projects/01-math-for-ml-notebook-library.md` | Intermediate → Advanced |

There is no `practice-questions.md` in this folder. Self-check questions sit inside each unit (§ "Check yourself"). The stage-level `../README.md` is defined separately.

**Repository facts to re-verify** `[VERIFY]` against the tree in `Roadmap.md`: 15 modules including this overview, 14 content modules, 80 lessons, 30 folders, 159 files (160 including this syllabus file). Lesson counts per module are in Unit 2.

**Learner assumed:** finished Stages 0–3 and Stage 4A. Writes working Python, uses Git and pytest, knows Big-O. Knows algebra, functions and graphs, logs and exponents, summation notation, and basic descriptive statistics from 4A. Has **not** necessarily used linear algebra, calculus, or probability as tools.

---

## Unit 1 — Stage 4B orientation (`README.md`)

### 1.1 What this stage is, in one paragraph

Stage 4B is the **working mathematics of machine learning**. Its job is to make every formula you meet in Stage 5 a thing you can compute, plot, differentiate, and debug. You learn it the way an engineer uses it: you implement it in NumPy, compare it with a trusted library, and watch it fail on bad inputs. It is deliberately not a proof course. Proofs appear only where they change how you write or debug code (e.g., why the normal equation breaks on collinear columns).

### 1.2 Industry-style versus university-style learning (the contract)

| University style | This stage |
|---|---|
| Theorem → proof → exercises | Problem in ML → minimum math needed → code → test → failure case |
| Hand computation on 2×2 | NumPy on realistic shapes, then hand-check on 2×2 |
| Answers are numbers | Answers are numbers **plus** a passing test and a plot |
| Notation is the goal | Notation is translated to code (4A Module 15 skill) |
| Failure = wrong answer | Failure = silent shape bug, NaN, unstable result, wrong denominator |

Every lesson in 4B follows the same six-beat shape, and the syllabus below assumes it:

1. **Why ML needs this** (a concrete model, loss, or metric that breaks without it).
2. **Intuition** (a picture or a tiny numeric example).
3. **Mechanics** (the formulas, with every symbol named).
4. **Code** (from scratch in NumPy, then the library call, then an assertion that they agree).
5. **Failure modes** (shape errors, overflow, ill-conditioning, wrong axis, small-sample traps).
6. **ML link** (where it reappears in Stage 4C and Stages 5A–5D).

### 1.3 The 14 modules at a glance

| Module | Topic | Lessons | One-line ML payoff |
|---|---|---|---|
| 01 | Vectors, dot product, norms | 5 | Features, embeddings, distances, regularizer penalties |
| 02 | Matrices and linear transformations | 9 | Every dense layer; solving linear systems; batching and broadcasting |
| 03 | Eigenvalues, SVD, low-rank structure | 5 | PCA, LoRA-style low-rank ideas, compression, spectral diagnostics |
| 04 | Similarity, distance, embedding geometry | 3 | Retrieval, RAG, nearest-neighbour search, curse of dimensionality |
| 05 | Derivatives, single-variable optimization | 8 | Activation gradients, gradient checking, chain rule |
| 06 | Integral calculus | 6 | Probabilities as areas, expectations, normalizing constants |
| 07 | Multivariable calculus, gradients | 4 | Gradients of losses, computational graphs, backprop by hand |
| 08 | Optimization fundamentals | 5 | Gradient descent, learning rate, SGD, momentum, Adam |
| 09 | Probability fundamentals | 8 | Bayes, random variables, expectation, covariance |
| 10 | Common distributions | 6 | Softmax as categorical, Gaussian assumptions, priors |
| 11 | Sampling and limit theorems | 4 | Sampling tokens, Monte Carlo, standard error |
| 12 | Inferential statistics for experiments and evals | 7 | Is prompt B really better? A/B tests, bootstrap, power |
| 13 | Information theory for ML | 5 | Cross-entropy loss, KL, perplexity |
| 14 | Linear-models mathematics | 5 | Linear/logistic regression, ridge/lasso: the capstone of the stage |

Total: 80 lessons.

### 1.4 What you can do at the end (outcomes)

Outcomes are written as observable behaviours. Each is checked by a lab or by the stage project (Unit 5).

1. Implement vector and matrix operations in NumPy without Python loops, and predict the output shape before running.
2. Explain a dense layer `y = XW + b` as a linear map, and diagnose a shape or broadcasting bug.
3. Compute eigenvalues and an SVD, build a low-rank approximation, and state what is lost.
4. Choose between dot product, cosine, and Euclidean similarity for a retrieval task and justify it.
5. Differentiate common functions (sigmoid, tanh, ReLU, log, exp) by hand and verify with a numerical gradient check.
6. Compute a gradient of a multivariable loss and run backprop by hand on a two-layer network.
7. Implement gradient descent, SGD, momentum, and Adam, and explain divergence from a bad learning rate.
8. Use Bayes' theorem, expectation, variance, covariance, and correlation correctly on data.
9. Pick the right distribution for a count, a yes/no event, a category, or a continuous quantity.
10. Show the law of large numbers and the CLT by simulation, and compute standard errors.
11. Produce a confidence interval (analytic and bootstrap) and a hypothesis test for a model comparison, with effect size and power.
12. Compute entropy, cross-entropy, KL divergence, and perplexity, and relate cross-entropy to the log loss you train with.
13. Fit linear and logistic regression with the normal equation and with gradient descent, and explain what ridge and lasso change.

### 1.5 Prerequisites and a 30-minute self-check

Before Module 01, you should be able to do the following without lookup. If you cannot, go to the named 4A module first.

| Skill | 4A module |
|---|---|
| Rearrange `y = mx + b` and solve a 2-equation linear system by substitution | 03, 04 |
| Simplify `exp(a)·exp(b)`, `log(ab)`, `log(a/b)` | 05, 06 |
| Read `Σ_{i=1}^{n} x_i y_i` and write the loop | 10, 15 |
| Sketch sigmoid, ReLU, `log(x)` and say where each saturates or is undefined | 07 |
| Compute sin/cos of an angle and explain the unit circle | 08 |
| Treat a vector as an arrow and as a data row; compute its length | 09 |
| Compute mean, variance, median, and percentile; state sample vs population denominators | 12 |
| State what a derivative is as a limit of slopes | 13 |
| Translate a formula with a subscript and a sum into NumPy | 15 |

### 1.6 Tooling and environment (reproducible from day one)

```bash
python -m venv .venv && source .venv/bin/activate
pip install "numpy>=1.26" "scipy>=1.11" "sympy>=1.12" "matplotlib>=3.8" \
            pandas pytest jupyterlab nbmake pytest-cov
python -c "import numpy, scipy, sympy, matplotlib; print(numpy.__version__, scipy.__version__)"
```

Rules used in every lab (state them once in the README, enforce them in the project):

- Seed all randomness: `rng = np.random.default_rng(0)`.
- Compare floats with `np.allclose` / `math.isclose`, never `==`.
- Every from-scratch function gets a test that compares against a library reference.
- Every plot has labelled axes and a one-sentence takeaway in the markdown cell below it.
- Pin versions in `requirements.txt` and note the Python version.

### 1.7 The five habits this stage builds (the real curriculum)

1. **Shape-first thinking.** Write shapes in comments: `X: (n, d)`, `W: (d, k)`, `Y: (n, k)`.
2. **Check against a reference.** NumPy/SciPy/SymPy/finite differences are your oracles.
3. **Know the failure region.** Every function has inputs where it breaks (`log(0)`, `exp(1000)`, singular matrices, tiny samples).
4. **Simulate before you believe.** If a statement is about randomness, run 10,000 trials.
5. **Connect to a loss.** Ask "which line of a training loop does this appear in?"

### 1.8 How the stage is assessed

- Per-module `practice-questions.md` (already in the tree) and per-module projects.
- The **Stage project** (Unit 5) integrates one deliverable from each module.
- A final **mastery gate** (Unit 2, §2.6) with pass criteria written as tests.

### Check yourself (Unit 1)

1. Name the six beats of every lesson and give one example of a "failure mode" beat for Module 02.
2. Which 4A module covers sample vs population variance, and where in 4B does it matter first?
3. Why do we pin a random seed and compare floats with `allclose`?

**Reference answers (for the file's footer):** (1) see §1.2; e.g., `A @ B` with mismatched inner dimensions, or `np.linalg.inv` on a singular matrix. (2) 4A Module 12; it matters in Module 09 (variance) and Module 11–12 (standard error, CIs). (3) Reproducibility and float rounding; exact equality fails after reordered operations.

---

## Unit 2 — Learning plan and pacing (`learning-plan.md`)

### 2.1 Pacing assumptions

`[JUDGEMENT]` Time figures below are planning estimates for a working engineer, not measurements. Assume about 8–10 focused hours per week: roughly 3 hours reading and worked examples, 4 hours coding labs, 1–2 hours projects and review. Adjust after week 2 using your own throughput (see §2.7).

### 2.2 Dependency map (what must come before what)

```
01 Vectors ──► 02 Matrices ──► 03 Eigen/SVD ──► 04 Similarity & Geometry
                    │                │
                    └────────────────┴──────────────► 14 Linear Models ◄─┐
05 Derivatives ──► 07 Multivariable ──► 08 Optimization ───────────────►─┤
     │                                                                    │
06 Integrals ──► 09 Probability ──► 10 Distributions ──► 11 Sampling     │
                      │                                      │           │
                      │                                      └► 12 Inferential Stats
                      └──────────────► 13 Information Theory ────────────┘
```

Hard dependencies: 02→03; 05→07→08; 06→09 (continuous variables); 09→10→11→12; 09→13; and 02+08+13 feed 14. Everything else can be reordered. Modules 04 and 06 are the safest to swap or defer.

### 2.3 The default 16-week plan

| Week | Modules / lessons | Core labs | Deliverable into the stage project |
|---|---|---|---|
| 1 | 01 (all 5 lessons) | Vector library; geometry of dot product | `mlmath/vectors.py` + tests |
| 2 | 02 lessons 1–5 | Matrix ops from scratch; broadcasting drills | `mlmath/matrices.py` |
| 3 | 02 lessons 6–9 | Gaussian elimination solver; inverse failure cases | `mlmath/linsolve.py` |
| 4 | 03 (all 5) | Power iteration; SVD image compression | `mlmath/decomp.py` |
| 5 | 04 (all 3) | Word-vector similarity; curse-of-dimensionality experiment | `mlmath/similarity.py` |
| 6 | 05 lessons 1–5 | Symbolic vs numerical derivative | `mlmath/calculus.py` |
| 7 | 05 lessons 6–8, 06 lessons 1–3 | Gradient checker; antiderivatives | `gradcheck()` |
| 8 | 06 lessons 4–6, 07 lessons 1–2 | Numerical integration toolkit; contour plotter | `mlmath/integrate.py` |
| 9 | 07 lessons 3–4, 08 lessons 1–3 | Backprop by hand; gradient descent visualizer | `mlmath/autograd_tiny.py` |
| 10 | 08 lessons 4–5, 09 lessons 1–3 | Optimizer comparison; Bayes spam filter | `mlmath/optim.py` |
| 11 | 09 lessons 4–8 | Probability simulations; covariance and correlation | `mlmath/prob.py` |
| 12 | 10 (all 6) | Distribution gallery and fitting; Poisson simulator | `mlmath/dists.py` |
| 13 | 11 (all 4), 12 lessons 1–2 | CLT/LLN lab; token sampling; bootstrap CI | `mlmath/sampling.py` |
| 14 | 12 lessons 3–7 | Prompt A vs B test; A/B test report | `mlmath/infer.py` |
| 15 | 13 (all 5) | Perplexity of text; entropy and KL explorer | `mlmath/info.py` |
| 16 | 14 (all 5) + stage project finish | Linear/logistic from scratch; ridge vs lasso | Notebook library release and mastery gate |

### 2.4 Compressed and extended tracks

| Track | Length | Who | What changes |
|---|---|---|---|
| **Fast** | 10 weeks | Learner who finished 4A with strong marks and has seen linear algebra or calculus | Skim Module 01, 05, 09 lessons with the self-check first; skip lessons you pass; do every module project |
| **Default** | 16 weeks | Most learners | As in §2.3 |
| **Gentle** | 22 weeks | Math anxiety or long gaps | One module per 1.5 weeks; re-do the 4A readiness items for the module before starting it |
| **Interview/eval-focused** | 12 weeks | Needs eval statistics soon | Modules 01, 02, 05, 07, 08 → 09, 10, 11, 12, 13 → 14; defer 03, 04, 06 `[JUDGEMENT]` |

### 2.5 The weekly rhythm

| Day | Activity | Time |
|---|---|---|
| Mon | Read lesson A, do worked examples by hand on small numbers | 1.5 h |
| Tue | Code lesson A from scratch + reference test | 2 h |
| Wed | Read lesson B; failure-mode experiments | 1.5 h |
| Thu | Code lesson B; plots | 2 h |
| Fri | Module project step or stage-project integration | 2 h |
| Sat | `practice-questions.md`, 20 min of spaced review of last week | 1 h |

**Spaced review rule:** each Saturday, re-do two questions from one module that is at least two weeks old.

### 2.6 Checkpoints and the mastery gate

Checkpoints are written as runnable checks. A module is "done" when its check passes without notes.

| After | Checkpoint (pass criteria) |
|---|---|
| Module 02 | Given random `A (n×d)`, `B (d×k)`, your matmul equals `A @ B` within `1e-10`; you correctly predict 5 broadcast shapes without running them |
| Module 03 | Rank-k SVD reconstruction error equals the sum of squared discarded singular values (Frobenius), within tolerance |
| Module 05 | Gradient checker passes (relative error < `1e-6`) on sigmoid, tanh, softplus, and a composed function |
| Module 08 | Gradient descent converges on a quadratic; you can produce a divergent run by choosing learning rate > `2/L` and explain why |
| Module 11 | CLT lab: standardized sample means from a skewed distribution look normal; you report the n at which a QQ-plot looks acceptable |
| Module 12 | Bootstrap CI and analytic CI for a mean agree within 5% on a Gaussian sample and disagree sensibly on a heavy-tailed one |
| Module 13 | Your cross-entropy equals `sklearn.metrics.log_loss`; perplexity equals `exp(mean NLL)` |
| Module 14 | Your linear regression coefficients match `np.linalg.lstsq`; your logistic regression log-loss is within 1% of scikit-learn with matching regularization settings |

**Stage mastery gate (all must pass):**

1. Every module project runs in a clean venv.
2. The notebook library's test suite is green and covers every from-scratch function.
3. You can complete, in 90 minutes, a closed-book exercise: *derive and implement the gradient of the regularized logistic loss, verify it numerically, and fit it on a synthetic dataset.* Pass = gradient check < `1e-6` and held-out accuracy above a baseline you predicted before fitting.
4. You can explain in five minutes, to a peer, why cross-entropy training equals maximum likelihood for a categorical model.

### 2.7 Adjusting the plan (feedback loop)

- Record hours per lesson in a simple CSV (`date, lesson, hours, confident 1-5`).
- After week 2, compute average hours per lesson. If it is above 1.6× the plan, switch to the Gentle track; below 0.7×, switch to Fast.
- A lesson with confidence ≤ 2 gets one extra lab the next week, not a re-read.

### 2.8 Common failure patterns (and what to do)

| Pattern | Symptom | Fix |
|---|---|---|
| Reading without coding | Understands slides, cannot write `softmax` | Code every formula the same day |
| Over-theorizing | Spends a week on one proof | Apply the six-beat shape; skip proofs not tied to a failure mode |
| Trusting a library blindly | Wrong axis, wrong denominator, silent broadcast | Always add a from-scratch reference |
| Skipping probability | Cannot read an eval report | Do Modules 09–12 even on the Fast track |
| Skipping failure modes | NaN loss in training | Run the "break it" cell in every lab |

### 2.9 Where each module is used next

See Unit 3 for the full map. In planning terms, finish Modules 05, 07, 08 and 14 before beginning Stage 4C Modules 02–03 and Stage 5A Module 04; finish 09–13 before Stage 4C Modules 04–06 and Stage 5A Module 06.

### Check yourself (Unit 2)

1. Why can Module 04 be deferred but Module 07 cannot?
2. Under the Gentle track, what do you do before starting each module?
3. A teammate says "my gradient check error is 1e-3". Is that a pass at the module checkpoint? Why or why not?

**Reference answers:** (1) Nothing downstream hard-depends on 04; 08 and 14 depend on 07. (2) Re-do the matching 4A readiness items. (3) No, the criterion is < `1e-6` for smooth functions in float64; 1e-3 suggests a bug or a poor step size.

---

## Unit 3 — How Stage 4B connects to 4A and 4C (`how-4b-connects-to-4a-and-4c.md`)

### 3.1 The one-page picture

```
Stage 3  (algorithms, Big-O, data structures)
   │
Stage 4A  Arithmetic · algebra · functions · logs · geometry · sequences · stats basics · limits · notation
   │      "I can read and manipulate the symbols."
   ▼
Stage 4B  Vectors → matrices → SVD → similarity | derivatives → gradients → optimization |
   │      probability → distributions → sampling → inference → information → linear models
   │      "I can compute, plot, and debug the objects ML is made of."
   ▼
Stage 4C  Vector spaces · matrix calculus · convexity · multivariate probability · estimation ·
   │      autograd · transformers/generative math
   │      "I can derive and defend the math behind deep learning."
   ▼
Stages 5A–5D  ML foundations → advanced ML → deep learning & transformers → MLOps
```

### 3.2 From 4A to 4B: what each 4B module assumes

| 4B module | Needs from 4A (module) | What 4B adds that 4A did not |
|---|---|---|
| 01 Vectors | 09 Vectors as arrows; 08 Geometry/Trig | n dimensions, NumPy arrays, norms as penalties, span/independence |
| 02 Matrices | 03 Algebra; 04 Equations and systems | Matrices as maps, shapes, broadcasting, solving `Ax=b` at scale, rank |
| 03 Eigen/SVD | 02 Matrices (above), 14 Complex numbers (optional) | Decomposition as compression and diagnosis |
| 04 Similarity | 08 Trigonometry (cosine); 09 | Cosine vs dot vs Euclidean in embedding search; high-dimensional behaviour |
| 05 Derivatives | 13 Limits and rates of change; 07 Functions | Rules, chain rule, activation derivatives, gradient checking |
| 06 Integrals | 10 Sequences, series, summation; 13 | Area, antiderivatives, numerical integration, density normalization |
| 07 Multivariable | 05 Derivatives (above); 07 Functions and graphs | Partials, gradient, computational graphs, backprop |
| 08 Optimization | 07 Functions; 05 | Loss functions, GD, SGD, momentum, Adam |
| 09 Probability | 11 Counting; 12 Descriptive stats | Axioms, Bayes, random variables, expectation, covariance |
| 10 Distributions | 05 Exponents; 06 Logarithms | Bernoulli → Dirichlet; softmax as categorical |
| 11 Sampling | 12 Descriptive stats | LLN, CLT, standard error, inverse-transform sampling |
| 12 Inferential stats | 12 Descriptive stats; 15 Notation | CIs, bootstrap, tests, power, A/B for model and prompt comparison |
| 13 Information theory | 06 Logarithms | Entropy, cross-entropy, KL, perplexity |
| 14 Linear models | 03, 04 Algebra and systems | Closed-form and iterative fits, regularization |

**Where Stage 3 already touched a topic** (logarithms in S3-01, geometry primitives in S3-16, modular arithmetic): 4B links back, and states only what is new: the ML meaning, not the algorithm. `[VERIFY]` section numbers against the Stage 3 tree before publishing the file.

### 3.3 From 4B to 4C: what is deepened

| 4B module | 4C module that deepens it | Shift in depth |
|---|---|---|
| 01–02 Vectors, matrices | 01 Advanced Linear Algebra | Computation → vector spaces, subspaces, QR/LU/Cholesky, positive definiteness |
| 03 Eigen/SVD | 01 Advanced Linear Algebra | Use SVD → derive SVD, pseudoinverse, Eckart–Young; PCA derivation |
| 05, 07 Derivatives, gradients | 02 Multivariable and Matrix Calculus | Scalar gradients → Jacobians, Hessians, Taylor, matrix calculus identities |
| 08 Optimization | 03 Optimization Theory and Training Algorithms | Run GD/Adam → convexity, convergence rates, conditioning, schedules |
| 09–10 Probability, distributions | 04 Advanced Probability | Univariate → multivariate Gaussian, change of variables, Markov chains, MCMC |
| 11–12 Sampling, inference | 05 Statistical Estimation and Bayesian Inference | Test and CI → MLE/MAP, estimator theory, Bayesian inference, EM |
| 13 Information theory | 06 Advanced Information Theory | Entropy, KL → mutual information, JS divergence, max entropy |
| 07 Backprop by hand | 07 Mathematics of Deep Learning Training | Two-layer by hand → reverse-mode autodiff, matrix-form backprop, normalization |
| 02, 04 Matrix shapes, similarity | 09 Mathematics of Transformers and Representations | Batched matmul and dot product → attention |
| 10–13 Distributions, KL, sampling | 10 Mathematics of Generative and Latent-Variable Models | Distributions and KL → VAEs, diffusion, latent-variable models |

(4C Module 08, convolutional and recurrent math, builds on 02 and 07 as well.)

### 3.4 From 4B to Stages 5A–5D: where you will use it

| Stage 5 module | 4B modules it leans on | Concrete use |
|---|---|---|
| 5A-04 Regression | 02, 14, 08 | Normal equation, residuals, regularization, gradient descent |
| 5A-05 Classification | 14, 10, 13 | Logistic regression, sigmoid/softmax, log-loss |
| 5A-06 Evaluation and metrics | 09, 12, 13 | Confusion-matrix probabilities, CIs on metrics, log-loss |
| 5A-07 Generalization and model selection | 12, 14 | Bias-variance intuition, regularization, significance of CV differences |
| 5A-09 Unsupervised learning | 01, 03, 04 | Distances, k-means geometry, PCA |
| 5B-02, 5B-04 Probabilistic prediction, calibration | 09, 10, 13 | Probability, proper scoring rules, cross-entropy |
| 5B-05 Dimensionality reduction | 03, 04 | SVD/PCA, distance preservation |
| 5B-10 Causal inference and experimentation | 09, 11, 12 | Confounding, A/B tests, power |
| 5C-01 to 5C-03 Neural networks, PyTorch, training | 02, 05, 07, 08 | Backprop, optimizers, learning-rate behaviour, gradient checks |
| 5C-06, 5C-07 Embeddings, attention | 01, 02, 04 | Dot-product similarity, batched matmul, scaled dot products |
| 5C-12 Decoding and sampling | 10, 11, 13 | Softmax, temperature, sampling from a next-token distribution, perplexity |
| 5D-12 Monitoring | 09, 11, 12, 13 | Distribution drift, KL divergence, statistical tests on streams |

`[VERIFY]` Module-level pointers above were derived from folder names. Confirm against each target module's lesson list before publishing.

### 3.5 Concept thread tracing (the most useful part of this file)

Four threads run through the whole curriculum. For each, the file lists the exact lesson sequence.

**Thread A — "a prediction is a matrix product."**
4A-09 vectors → 4B-01 dot product → 4B-02 `A @ x` and shapes → 4B-14 `Xw` → 4C-09 attention `QKᵀ` → 5C-07 Transformer layer.

**Thread B — "learning is following a gradient."**
4A-13 limits → 4B-05 derivative and chain rule → 4B-07 gradient and backprop → 4B-08 gradient descent and Adam → 4C-03 convergence → 4C-07 autograd → 5C-03 training loops.

**Thread C — "uncertainty is a distribution."**
4A-12 descriptive stats → 4B-09 random variables → 4B-10 distributions → 4B-11 sampling → 4B-12 inference → 4C-05 MLE/Bayes → 5B-04 calibration.

**Thread D — "loss is surprise."**
4A-06 logs → 4B-13 entropy → 4B-13 cross-entropy → 4B-14 log-loss gradient → 4C-05 MLE equivalence → 5C-11 post-training objectives.

**A worked example that ties all four, for the file:** training logistic regression on 4B-14.

```python
import numpy as np

def sigmoid(z):                      # 4B-05 lesson 5, 4B-10 (Bernoulli)
    return 1.0 / (1.0 + np.exp(-z))

def log_loss(w, X, y):               # 4B-13 cross-entropy; Thread D
    p = sigmoid(X @ w)               # 4B-02 shapes; Thread A
    eps = 1e-12
    return -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

def grad(w, X, y):                   # 4B-07 gradient; 4B-14 lesson 4
    return X.T @ (sigmoid(X @ w) - y) / len(y)

rng = np.random.default_rng(0)
X = np.c_[np.ones(200), rng.normal(size=(200, 2))]
w_true = np.array([0.5, 2.0, -1.0])
y = (rng.random(200) < sigmoid(X @ w_true)).astype(float)

w = np.zeros(3)
for _ in range(500):                 # 4B-08 gradient descent; Thread B
    w -= 0.5 * grad(w, X, y)
print(w, log_loss(w, X, y))          # Thread C: y is a Bernoulli draw
```

The file should annotate each line with its thread and lesson, as in the comments above, and then add the "break it" variant: set the learning rate to 50 and observe the divergence.

### 3.6 Handoff contract: what 4C will assume you know

Write as a checklist at the end of the file. Examples:

- You can write a gradient check from memory and run it on any new function.
- You can state the shape of every term in `XᵀXw = Xᵀy`.
- You can compute a covariance matrix with `np.cov` and verify it by hand, and know the `ddof` argument.
- You can explain why cross-entropy and KL differ by a constant that does not depend on the model.
- You can explain what a loss landscape and a learning rate do without equations.

If you cannot tick all five, revisit Modules 07, 14, 09, 13, and 08 respectively.

### Check yourself (Unit 3)

1. Which 4A module teaches the cosine, and which 4B module uses it for retrieval?
2. Name the 4C module that derives SVD and which 4B module uses SVD as a tool.
3. Trace Thread D from 4A to 5C in one sentence.

**Reference answers:** (1) 4A-08 → 4B-04. (2) 4C-01; 4B-03. (3) Logs (4A-06) become entropy and cross-entropy (4B-13), whose gradient trains logistic and softmax models (4B-14), justified by MLE in 4C-05 and reused in post-training objectives in 5C-11.

---

## Unit 4 — Overview project index (`Projects/README.md`)

### 4.1 Purpose

This file lists every project in Stage 4B, says what skill each one proves, and shows the order. It also holds the shared grading rubric so project files stay short.

### 4.2 Project catalogue

| Module | Project file | Proves |
|---|---|---|
| 00 | `01-math-for-ml-notebook-library.md` (**stage project**) | Integration, testing, packaging |
| 01 | `01-vector-operations-library-in-numpy.md` | Vectorized code, shape discipline |
| 01 | `02-geometry-of-dot-product-explorer.md` | Geometric intuition |
| 02 | `01-matrix-operations-from-scratch.md` | Matmul, transpose, shapes |
| 02 | `02-gaussian-elimination-solver.md` | Solving systems; pivoting |
| 02 | `03-linear-transformation-visualizer.md` | Maps as geometry |
| 03 | `01-eigenvalue-power-iteration.md` | Iterative eigen-computation |
| 03 | `02-image-compression-with-svd.md` | Low rank in practice |
| 04 | `01-word-vector-similarity-explorer.md` | Similarity choice |
| 04 | `02-curse-of-dimensionality-experiments.md` | High-dimensional behaviour |
| 05 | `01-symbolic-and-numerical-derivative-comparison.md` | SymPy vs finite differences |
| 05 | `02-numerical-gradient-checker.md` | Gradient checking |
| 06 | `01-numerical-integration-toolkit.md` | Integration methods and error |
| 06 | `02-area-under-a-density-curve-lab.md` | Probability as area |
| 07 | `01-gradient-field-and-contour-plotter.md` | Gradient geometry |
| 07 | `02-backpropagation-by-hand-on-a-tiny-network.md` | Backprop |
| 08 | `01-gradient-descent-visualizer.md` | Learning rate and convergence |
| 08 | `02-optimizer-comparison-sgd-momentum-adam.md` | Optimizer behaviour |
| 09 | `01-probability-simulations.md` | Simulation vs theory |
| 09 | `02-bayes-spam-filter-by-hand.md` | Bayes and base rates |
| 10 | `01-distribution-gallery-and-fitting.md` | Distribution choice and fit |
| 10 | `02-poisson-event-rate-simulator.md` | Count modelling |
| 11 | `01-sampling-from-a-next-token-distribution.md` | Temperature, top-k sampling |
| 11 | `02-clt-and-lln-simulation-lab.md` | Limit theorems |
| 12 | `01-is-prompt-b-really-better.md` | Significance for evals |
| 12 | `02-bootstrap-confidence-interval-lab.md` | Resampling |
| 12 | `03-ab-test-analysis-report.md` | Reporting standard |
| 13 | `01-compute-perplexity-of-text.md` | Perplexity |
| 13 | `02-entropy-and-kl-explorer.md` | Entropy, KL |
| 14 | `01-linear-regression-from-scratch-in-numpy.md` | Closed form and GD |
| 14 | `02-logistic-regression-from-scratch.md` | Log-loss gradient |
| 14 | `03-ridge-versus-lasso-comparison.md` | Regularization |

That is 32 projects: 31 module projects plus the stage project. `[VERIFY]` against the tree.

### 4.3 Suggested order

Follow module order. The stage project is built incrementally (one module's deliverable per week in the default plan) and finished last.

### 4.4 Shared project rubric (100 points)

| Criterion | Points | Evidence |
|---|---|---|
| Correctness against a reference | 30 | Tests compare to NumPy/SciPy/SymPy within stated tolerance |
| Failure-mode handling | 15 | Documented behaviour on singular, empty, NaN, extreme inputs |
| Reproducibility | 15 | Seeded, pinned versions, runs from a clean venv |
| Explanation quality | 15 | Markdown cells that say what a plot shows and why it matters for ML |
| Code quality | 15 | Typed signatures, docstrings with shapes, no hidden global state |
| ML connection | 10 | One paragraph naming where this appears in 4C or Stage 5 |

Passing is 70. A project below 70 on correctness is redone, regardless of total.

### 4.4b Standard project layout

```
project-name/
├── README.md            # problem, how to run, results, limitations
├── requirements.txt
├── src/<pkg>/…          # from-scratch code
├── tests/test_*.py      # reference comparisons
├── notebooks/*.ipynb    # exploration and plots
└── results/             # figures, tables (generated, not hand-edited)
```

### Check yourself (Unit 4)

1. What is the passing score, and what extra condition applies to correctness?
2. How many projects are in Stage 4B and which is the stage project?

**Reference answers:** (1) 70, and correctness must reach its own pass bar. (2) 32 `[VERIFY]`; `00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`.

---

## Unit 5 — Overview project: Math-for-ML notebook library (`Projects/01-math-for-ml-notebook-library.md`)

### 5.1 Project brief

Build **`mlmath`**, a small, tested Python package plus a set of notebooks that implements the core object from each Stage 4B module from scratch, compares it with a reference library, and documents where it fails. It is your personal reference you will keep using in Stages 4C and 5.

**Why this project (industry framing):** teams routinely carry an internal numerics utilities library and a "gradient check / stat check" harness. Writing one is the fastest way to turn this stage into reusable skill, and a green test suite is stronger evidence of understanding than a quiz.

**Time:** built incrementally across the 16-week plan; about 6–8 hours of integration work beyond module projects `[JUDGEMENT]`.

### 5.2 Required deliverables

| # | Deliverable | Source modules |
|---|---|---|
| D1 | `mlmath/vectors.py`: dot, norms (L1, L2, L∞), projection, cosine | 01 |
| D2 | `mlmath/matrices.py`: matmul, transpose, determinant (small), inverse with failure checks | 02 |
| D3 | `mlmath/linsolve.py`: Gaussian elimination with partial pivoting, rank estimate | 02 |
| D4 | `mlmath/decomp.py`: power iteration, truncated SVD reconstruction, Frobenius/spectral norm | 03 |
| D5 | `mlmath/similarity.py`: cosine, dot, Euclidean, top-k nearest neighbours | 04 |
| D6 | `mlmath/calculus.py`: numerical derivative, `gradcheck`, sigmoid/tanh/ReLU with derivatives | 05, 07 |
| D7 | `mlmath/integrate.py`: Riemann, trapezoid, Simpson | 06 |
| D8 | `mlmath/optim.py`: GD, SGD, momentum, Adam on arbitrary `f, grad` | 08 |
| D9 | `mlmath/prob.py`: Bayes update, expectation, variance, covariance, correlation | 09 |
| D10 | `mlmath/dists.py`: softmax (stable), Bernoulli/Poisson/Normal pmf/pdf, inverse-transform sampler | 10, 11 |
| D11 | `mlmath/infer.py`: bootstrap CI, two-sample test, power by simulation | 11, 12 |
| D12 | `mlmath/info.py`: entropy, cross-entropy, KL, perplexity | 13 |
| D13 | `mlmath/linmodels.py`: linear regression (closed form and GD), logistic regression, ridge | 14 |
| D14 | One notebook per module, run end to end by CI | all |
| D15 | `REPORT.md`: a failure-mode catalogue (see §5.6) | all |

### 5.3 Repository layout

```
math-for-ml-notebook-library/
├── pyproject.toml
├── requirements.txt
├── README.md
├── REPORT.md
├── src/mlmath/
│   ├── __init__.py
│   ├── vectors.py  matrices.py  linsolve.py  decomp.py  similarity.py
│   ├── calculus.py  integrate.py  optim.py  prob.py  dists.py
│   └── infer.py  info.py  linmodels.py
├── tests/
│   └── test_*.py            # one file per module above
├── notebooks/
│   └── 01_vectors.ipynb … 14_linear_models.ipynb
└── .github/workflows/ci.yml
```

### 5.4 Starter code (copy, run, extend)

`src/mlmath/calculus.py`: the gradient checker, which every later module uses.

```python
from __future__ import annotations
from typing import Callable
import numpy as np

def numerical_grad(f: Callable[[np.ndarray], float], x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """Central-difference gradient. x: (d,) -> (d,)."""
    x = np.asarray(x, dtype=float)
    g = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x)
        e[i] = h
        g[i] = (f(x + e) - f(x - e)) / (2 * h)
    return g

def gradcheck(f, grad, x, tol: float = 1e-6) -> float:
    """Return max relative error between analytic and numerical gradient; raise if above tol."""
    a, n = grad(x), numerical_grad(f, x)
    err = np.max(np.abs(a - n) / np.maximum(1e-8, np.abs(a) + np.abs(n)))
    if err > tol:
        raise AssertionError(f"gradient check failed: max rel err {err:.2e} > {tol:.0e}")
    return float(err)
```

`src/mlmath/dists.py`: a numerically stable softmax and its test.

```python
import numpy as np

def softmax(z: np.ndarray, axis: int = -1, temperature: float = 1.0) -> np.ndarray:
    z = np.asarray(z, dtype=float) / temperature
    z = z - z.max(axis=axis, keepdims=True)      # stability: avoids exp overflow
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)
```

`tests/test_dists.py`

```python
import numpy as np
from scipy.special import softmax as sp_softmax
from mlmath.dists import softmax

def test_matches_scipy():
    z = np.random.default_rng(0).normal(size=(4, 7))
    assert np.allclose(softmax(z), sp_softmax(z, axis=-1))

def test_survives_large_logits():
    p = softmax(np.array([1000.0, 1001.0, 1002.0]))
    assert np.isfinite(p).all() and np.isclose(p.sum(), 1.0)

def test_temperature_sharpens():
    z = np.array([1.0, 2.0, 3.0])
    assert softmax(z, temperature=0.1).max() > softmax(z, temperature=1.0).max()
```

`src/mlmath/info.py`: entropy and KL with explicit handling of zeros.

```python
import numpy as np

def entropy(p, base: float = 2.0) -> float:
    p = np.asarray(p, dtype=float)
    nz = p > 0                                    # define 0*log(0) = 0
    return float(-(p[nz] * np.log(p[nz])).sum() / np.log(base))

def kl(p, q, base: float = 2.0) -> float:
    p, q = np.asarray(p, float), np.asarray(q, float)
    if np.any((q == 0) & (p > 0)):
        return float("inf")                       # KL is infinite if q misses support of p
    nz = p > 0
    return float((p[nz] * np.log(p[nz] / q[nz])).sum() / np.log(base))
```

`tests/test_info.py` should assert: `kl(p, p) == 0`, `kl(p, q) >= 0`, `kl(p, q) != kl(q, p)` for a chosen pair, and `cross_entropy(p, q) == entropy(p) + kl(p, q)` (add `cross_entropy` yourself).

`.github/workflows/ci.yml` (minimal):

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e . pytest pytest-cov nbmake -r requirements.txt
      - run: pytest --cov=mlmath --cov-fail-under=90
      - run: pytest --nbmake notebooks/
```

`[VERIFY]` Action versions and flags against current docs before publishing the file.

### 5.5 Build stages (with acceptance tests)

| Stage | Work | Acceptance test |
|---|---|---|
| S1 (wk 1–5) | D1–D5 and notebooks 01–04 | Every function matches NumPy on 100 random inputs; shape-mismatch inputs raise `ValueError` with a clear message |
| S2 (wk 6–10) | D6–D8 and notebooks 05–08 | `gradcheck` passes on sigmoid, tanh, softplus, and a composed 2-layer loss; GD/Adam reach the minimum of a convex quadratic and the Rosenbrock function within a stated tolerance |
| S3 (wk 11–14) | D9–D11 and notebooks 09–12 | Bootstrap CI and `scipy.stats` CI agree for a Gaussian sample; empirical coverage of a 95% CI over 2,000 simulations lies in 0.93–0.97 |
| S4 (wk 15–16) | D12–D13, notebooks 13–14, CI, `REPORT.md` | Linear regression matches `np.linalg.lstsq`; logistic regression log-loss within 1% of scikit-learn at equal regularization; coverage ≥ 90% |

### 5.6 `REPORT.md`: the failure-mode catalogue

This is the part most learners skip and is where the project pays off. Write one table with at least 15 rows, each with: **function, input that breaks it, symptom, cause, fix, test that guards it**. Seed the table with:

| Function | Breaking input | Symptom | Fix |
|---|---|---|---|
| `softmax` (naive) | logits ≈ 1000 | `inf/inf = nan` | Subtract max |
| `log_loss` | probability exactly 0 or 1 | `-inf` | Clip with epsilon |
| `inverse` | collinear columns | huge entries or `LinAlgError` | Check condition number; use `lstsq` or `solve` |
| `kl(p, q)` | `q=0` where `p>0` | infinite | Smooth `q` or report `inf` by design |
| `np.var` | small sample | biased low | `ddof=1` for sample variance |
| `numerical_grad` | `h` too small (1e-12) | noise dominates | Use central difference with `h≈1e-5` |
| `normal equation` | `d > n` or collinearity | unstable or singular `XᵀX` | Ridge term or `lstsq` |
| `cosine_similarity` | zero vector | division by zero | Guard norm, return 0 or raise |

### 5.7 Stretch goals (optional, advanced)

1. Implement `einsum`-based batched versions of D1–D2 and benchmark against loops with `timeit`.
2. Add a `hypothesis` property-based test suite (e.g., `(A@B).T == B.T@A.T` for random shapes).
3. Add a mini reverse-mode autodiff `Value` class (preview of 4C-07) and verify against `gradcheck`.
4. Publish docs with MkDocs and a versioned release (`v0.1.0`) tagged in Git.
5. Add a type-checking step (`mypy --strict` on `src/`) to CI.

### 5.8 Evaluation

Use the rubric in Unit 4 §4.4. Additional stage-project criteria:

- Test coverage ≥ 90% on `src/mlmath` `[JUDGEMENT]`.
- All notebooks execute top to bottom in CI with seeded randomness.
- `REPORT.md` has ≥ 15 genuine rows, each guarded by a named test.
- `README.md` lets a stranger install and run the test suite in under 10 minutes.

### 5.9 What this proves (portfolio framing)

You can write numerically careful code, test it against references, and document its failure modes. Describe it honestly in a portfolio: "from-scratch math library with 90%+ coverage and a failure-mode catalogue", not as a replacement for NumPy.

### Check yourself (Unit 5)

1. Why does `softmax` subtract the maximum?
2. What is the relationship between cross-entropy, entropy, and KL divergence, and which test in this project verifies it?
3. A bootstrap CI covers the true mean in 71% of 2,000 simulations at nominal 95%. Name two possible causes.

**Reference answers:** (1) Shift invariance keeps `exp` from overflowing without changing the result. (2) `H(p, q) = H(p) + KL(p‖q)`; the identity test in `test_info.py`. (3) Too-small sample or heavy tails, a bug in the percentile or resampling step (e.g., resampling without replacement, wrong `n`), or a statistic for which the percentile bootstrap is known to be poor.

---

## Appendix A — Open items for the author

1. `[VERIFY]` Totals (80 lessons, 32 projects, 159 files excluding this syllabus) against the tree after any later edits.
2. `[VERIFY]` Stage 3 and Stage 5 cross-links in Unit 3 (derived from folder names only).
3. `[VERIFY]` CI action versions and package version floors in §1.6 and §5.4.
4. Decide whether Module 06 (integral calculus) should stay on the Interview/eval-focused track's deferral list.

## Appendix B — Authoring checklist for the five files

- [ ] `README.md` covers §1.1–1.8 and the self-check.
- [ ] `learning-plan.md` has the table, tracks, checkpoints, and mastery gate verbatim.
- [ ] `how-4b-connects-to-4a-and-4c.md` includes all three maps, the four threads, and the logistic-regression worked example.
- [ ] `Projects/README.md` lists every project and the rubric.
- [ ] `Projects/01-math-for-ml-notebook-library.md` includes the brief, deliverables, starter code, stages, report template, and stretch goals.
- [ ] No unverified claims about employers, interviews, or timings presented as fact.
