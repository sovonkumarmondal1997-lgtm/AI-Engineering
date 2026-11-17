# PROMPT — Generate `SYLLABUS-Semi-Supervised-Active-and-Weak-Supervision.md` (Stage 5B, module S5B-11)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is large, so use the **Delivery Protocol** (Section 13): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Semi-Supervised-Active-and-Weak-Supervision.md` in `Stage 5B — Advanced Machine Learning/11-Semi-Supervised-Active-and-Weak-Supervision/`. Then split it into the target files listed in Section 2.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have seen label-scarce projects fail in predictable ways: a self-training loop whose pseudo-labels amplified the model's own early mistakes until "confidence" meant nothing; a semi-supervised gain measured against a baseline tuned on a different, larger validation set; a "10x label saving" claimed from one lucky seed and a validation set that had itself been selected by uncertainty sampling; an active-learning loop whose labelled pool drifted so far from the deployment distribution that the model's calibration collapsed; a labelling-function set whose votes were correlated copies of one rule, so the label model was overconfident; weak labels evaluated on weak labels; label noise treated as random when it was class-dependent and annotator-dependent; a "clean" test set that was never audited and carried the same errors as the training set; unlabeled data from a different population than the labeled data, so the "free" data hurt; a labelling budget spent on the hardest, most ambiguous examples, which were also the least learnable. You teach the way you work: **first ask what the labels cost, what the unlabeled data actually is, and which assumption makes unlabeled data informative at all; measure every method against a strong supervised baseline with the same labelling budget and the same untouched, representatively sampled evaluation set; treat a label as a noisy measurement with a cost and an error model, not as truth; and never present a result you cannot reproduce from a seed.**

You are also a careful technical author. You never invent a function, signature, default, version, statistic, citation, or **claim about how much label saving a method achieves in general, "X% fewer labels" figure presented as fact, claim about how any real company labels or deploys such systems, general ranking of methods ("FixMatch beats self-training", "uncertainty sampling beats random", "Snorkel beats hand labels"), claim that unlabeled data "always helps", claim that a method "removes" label noise without stating its noise model, claim of legal, privacy, or regulatory sufficiency, or rule-of-thumb threshold (a confidence cut-off such as 0.95, a query batch size, a noise-rate bound) as a law**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion and rules of thumb are marked `[JUDGEMENT]` or `HEURISTIC`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 5B — Advanced Machine Learning / 11-Semi-Supervised-Active-and-Weak-Supervision/` (module code **S5B-11**, the **statistics and engineering of learning when labels are scarce, expensive, or unreliable: labeled versus unlabeled data and the assumptions that make unlabeled data useful; pseudo-labeling and self-training with consistency regularisation; active learning and query strategies; and weak supervision and learning with noisy labels**).

Output file name: **`SYLLABUS-Semi-Supervised-Active-and-Weak-Supervision.md`**, saved inside that folder.

All code, labs, worked examples, and the project are in **Python** (NumPy/SciPy/pandas/scikit-learn-centred). The learner implements **from scratch, as spec-literal references, and checks them against scikit-learn and SciPy**: a label-budget learning-curve harness with a strong supervised baseline; label-propagation/label-spreading on a similarity graph; a self-training loop with threshold, top-k, and class-balanced selection rules; a consistency-regularisation objective (noise-perturbation form, on tabular/feature inputs); uncertainty, margin, entropy, query-by-committee, and diversity (k-center / clustering-based) query strategies with batch selection; an active-learning simulator with a hidden oracle and cost accounting; labelling functions, a labelling-function matrix, majority vote, and a generative label model (agreement/accuracy estimation under conditional independence) with a diagnostics report; noise-transition-matrix estimation, forward/backward loss correction, small-loss sample selection, and confident-learning-style issue detection. See Section 3 for the library list.

Teach, **one after another, from beginner to advanced**, these units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | Labeled versus unlabeled data | `01-labeled-vs-unlabeled-data.md` |
| 2 | Pseudo-labeling and self-training | `02-pseudo-labeling-and-self-training.md` |
| 3 | Active learning and query strategies | `03-active-learning-and-query-strategies.md` |
| 4 | Weak supervision and noisy labels | `04-weak-supervision-and-noisy-labels.md` |
| 5 | Practice questions | `practice-questions.md` |
| 6 | Projects index | `Projects/README.md` |
| 7 | Project 1: label efficiency study | `Projects/01-label-efficiency-study.md` |

Tree (source of truth):

```
11-Semi-Supervised-Active-and-Weak-Supervision/
├── Projects/
│   ├── 01-label-efficiency-study.md
│   └── README.md
├── 01-labeled-vs-unlabeled-data.md
├── 02-pseudo-labeling-and-self-training.md
├── 03-active-learning-and-query-strategies.md
├── 04-weak-supervision-and-noisy-labels.md
├── README.md
└── practice-questions.md
```

Do not add, rename, or merge files. `PROMPT-…md` is this prompt and is not part of the syllabus.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–4B, **all of Stage 5A**, and `../00-Stage-Overview/` to `../10-…` of 5B (the 5B protocol card; nested and deployment-matched validation and planted-truth evaluation (5B-01); uncertainty (5B-02); imbalance and thresholds (5B-03); calibration (5B-04); representations and reduction (5B-05); anomaly detection (5B-06); explanation (5B-07); forecasting (5B-08); recommendation and exposure bias (5B-09); causal inference, selection bias, and off-policy estimators (5B-10)). They know supervised learning, regularisation, probability and the bootstrap. They have **not** yet studied deep learning in depth (Stage 5C): **teach semi-supervised and weak-supervision ideas on tabular, low-dimensional, and precomputed-feature data**, and mention image/text large-scale methods only as clearly labelled previews with `[VERIFY]` citations.
- **Already taught — link, never re-teach:** probability, Bayes' rule, expectation and variance (Stage 4B); logistic regression, SVM, trees, ensembles, k-NN, clustering, PCA (5A); cross-validation, the bootstrap, learning curves (5A/5B-01); calibration and reliability (5B-04); uncertainty estimates (5B-02); embeddings and k-NN structure (5B-05); selection bias and propensity ideas (5B-10). Reference them by exact folder/file names from the repository tree; never invent a path. If you are unsure a path exists, say `[VERIFY path]`.
- **Environment:** Python 3.10+, NumPy, SciPy, pandas, scikit-learn, matplotlib (optional), pytest. No network at run time, no downloaded datasets or models, no paid APIs. **All data are synthetic or scikit-learn bundled/generated datasets** (`make_moons`, `make_classification`, `make_blobs`, generated text-free feature tables), with **planted truth**: the true labels of every "unlabeled" point, the true noise transition matrix, and the true labelling-function accuracies are known to the harness and hidden from the learner's method.
- **Time:** assume 6–8 hours per unit plus the project; mark every time figure `[ASSUMPTION]`.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–4 AND 7)

Each of these units progresses through **exactly these four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Says what a label costs, what unlabeled data is, and which assumption makes it useful; follows a worked example; runs the basic method on a small case. |
| **L2** | Intermediate — Working Practice | Applies the method unaided to their own data within a timebox, with a correct baseline and evaluation set, avoiding the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | States acceptance criteria as checkable properties, justifies design decisions with measurement over many seeds, quantifies uncertainty, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in others' label pipelines, chooses (or refuses) a method for a given budget and data situation, and could coach a peer. |

Units 0, 5, and 6 use their own structures (Section 6, 7, 8).

# 5. MANDATORY STRUCTURE FOR UNITS 1–4 AND 7

Use this exact skeleton. If a section is genuinely not applicable, write one sentence saying why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours, [ASSUMPTION]>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete, verifiable failure this prevents. No hype, no outcome claims.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid diagram.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what)
- Guided exercise: original example, exact Python, expected output, how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic worked example (complete, runnable), continuing the running example
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad practice → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Method card and Tool card: (1) goal and when to use, (2) inputs/outputs, (3) steps, (4) invariants/acceptance criteria as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure; how to avoid fooling yourself: seeds, budgets, baselines, evaluation-set hygiene)
- Exercise requiring a defended justification or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial situations specific to the unit (see Section 6)
- Automation (aggregate verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's label-budget plan or label-quality audit with evidence-based feedback
- Edge cases and library differences (scikit-learn version changes in `SelfTrainingClassifier`, `LabelPropagation`, `LabelSpreading` defaults and `-1` unlabeled convention)

### N.7 Engineering lens
(Where this fails in real ML engineering — verifiable failures only, never a company claim or a failure-rate statistic. Failure modes, blast radius, cost of labels, labelling-tool and review workflow, versioning of label sets and label provenance.)

### N.8 Integrity lens
(Measurement risks: tuning on the evaluation set, cherry-picked seeds, evaluation set drawn by the active learner, leakage of true labels into pseudo-label selection, copying notebooks, AI-assistance disclosure. Controls, each verifiable by a command, test, or written check.)

### N.9 Checklist
(Checkbox list; every item verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, seeded, local-only, safe to re-run, with a `--quick` mode.)

### N.11 Self-check questions
(6–10 questions with concise keys and a "why the wrong answers are tempting" note for MCQs; at least one coding question with an oracle.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview questions
(5 questions on the unit's theme with senior-level model answers; no claims about what any company asks.)

### N.14 Sources and verification notes
(References by name and section; every CITED claim named; every JUDGEMENT labelled; [VERIFY] items listed.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

## Conventions stated once, used everywhere (state them in Unit 0, apply in all units)

- **The label-budget card** (one per experiment): task and cost per label; labelled set size *n_l*; unlabeled pool size *n_u* and **how it was drawn relative to the labeled set** (same distribution / shifted / contaminated with out-of-class); evaluation set (size, how sampled, **never touched by any selection, pseudo-labelling, or query step**, and drawn representatively, not by the learner); supervised baseline at the **same** *n_l* with its own tuned hyperparameters; method and hyperparameters (and how tuned on labelled data only); seeds; metric; planted-truth check; decision.
- **Evaluation hygiene rules:** (1) one frozen, representatively sampled evaluation set per experiment; (2) hyperparameters of semi-supervised methods tuned on labelled data only, never on the evaluation set or on pseudo-labels; (3) every claimed gain reported as mean ± spread over ≥ 20 seeds (quick mode ≥ 5) with the **paired** difference to the supervised baseline and a bootstrap interval; (4) the baseline gets equal tuning effort; (5) a learning curve over *n_l*, not a single point.
- **Label-quality convention:** a label is a measurement with an error model. Always state the noise model (symmetric / class-conditional / instance-dependent / annotator-dependent) and whether the evaluation labels are themselves noisy.
- **Seed convention:** `SeedSequence` with named spawn keys; results independent of `n_jobs`.

## Unit 0 — Module orientation (`README.md`)

Why label scarcity is an engineering and cost problem; the four methods families and the **decision map** (when to use none of them and just label more; when unlabeled data helps; when active learning helps; when weak supervision fits; when label-noise methods fit); prerequisites; the label-budget card and evaluation hygiene rules; how units connect (running example reused across units); what is out of scope; safety notes (privacy of labelling data, annotator welfare and fair pay as an engineering constraint, not an afterthought); how to use the evidence log. Not four-level; ≤ 2 pages equivalent plus the decision-map diagram.

## Unit 1 — Labeled versus unlabeled data

- **L1:** what a label is and costs; supervised, unsupervised, semi-supervised, and weakly supervised problems defined precisely; labeled/unlabeled/evaluation split vocabulary; *why unlabeled data can help at all*: the semi-supervised **assumptions** — smoothness, **cluster/low-density separation**, manifold — stated with a small 2-D picture-by-numbers example (`make_moons`) and a **counter-example where unlabeled data does not help or hurts** (wrong cluster structure, covariate shift, out-of-class unlabeled points). Show the learning curve vs supervised baseline.
- **L2:** the **label-budget learning curve harness**; label propagation and label spreading (scikit-learn `LabelPropagation`/`LabelSpreading`, `-1` convention, kernels `rbf` and `knn`, `gamma`, `n_neighbors`, `alpha`) and a from-scratch graph-Laplacian version on a tiny graph checked against a closed-form solution; generative/mixture-model view (EM with a Gaussian mixture, labelled + unlabeled likelihood) as one equation with a small implementation; transductive vs inductive; **sampling the labeled set** (random vs convenience vs stratified) and what each does to the baseline.
- **L3:** formalise: when does *p(x)* inform *p(y|x)*? State the assumptions and give the known **negative/limit results as cited and `[VERIFY]`-tagged** (do not invent theorems); mismatched unlabeled distribution (covariate shift, class-prior shift, out-of-distribution contamination) and diagnostics for it (domain classifier AUC, density-ratio sanity check); **evaluation of semi-supervised claims** (equal tuning, paired seeds, learning curves); computational cost of graph methods (*O(n²)* memory; sparse k-NN graphs) with sizes guarded before allocation; connection to representation learning (5B-05) and calibration (5B-04) (does unlabeled data change calibration?).
- **L4 adversarial situations:** unlabeled pool from a different population; "improvement" that disappears with a tuned baseline; labelled set chosen by convenience; leakage of evaluation points into the graph (transductive leakage); an evaluation set that is also in the unlabeled pool; a learner who equates "more data" with "more labels".
- Running example for Units 1–4: **a synthetic multi-class tabular problem with a planted cluster structure, a planted noise model, and a hidden oracle**, with the true labels of all points held by the harness.

## Unit 2 — Pseudo-labeling and self-training

- **L1:** the loop in plain words (train → predict unlabeled → keep confident → add → retrain); worked example by hand on ~10 points; `SelfTrainingClassifier` basic use; the fundamental risk: **confirmation bias** (errors reinforce themselves).
- **L2:** selection rules (threshold, top-k per iteration, class-balanced, curriculum); iteration limits and stop criteria; **calibration of the base classifier matters** because confidence is the selection signal (link 5B-04) — show a miscalibrated base model degrading self-training; hard vs soft pseudo-labels; **co-training** (two views) and **tri-training/disagreement** as short methods; consistency regularisation in its simplest form (prediction should not change under small input noise) on tabular features; mean-teacher/EMA and FixMatch-style ideas as **named previews only** (deep learning is Stage 5C), each with a `[VERIFY]` citation.
- **L3:** pseudo-label noise analysis: the effective noise rate of the pseudo-labelled set as a function of threshold, measured against planted truth; coverage–accuracy trade-off curve; class-imbalance interaction (5B-03) — pseudo-labels follow the majority class; confirmation-bias diagnostics (pseudo-label accuracy per iteration, class-prior drift, calibration drift); **negative results**: when self-training hurts (with a reproducible counter-example); `SelfTrainingClassifier` internals (`threshold`, `criterion`, `k_best`, `max_iter`, `termination_condition_`, `transduction_`) as **behaviours to test, not guarantees** `[VERSION-SENSITIVE]`; stopping with a labelled validation set only.
- **L4 adversarial situations:** self-training on a model with overconfident outputs; threshold 0.95 copied from a paper onto a different problem; imbalanced classes producing an all-majority pseudo-label set; pseudo-labels leaking evaluation labels through a shared feature; a loop with no stop criterion; a reported gain from a single seed.

## Unit 3 — Active learning and query strategies

- **L1:** the loop (train → score pool → query oracle → add → retrain); the oracle and its cost; pool-based vs stream-based vs membership-query settings; random sampling as the baseline you must beat; a worked toy example.
- **L2:** **uncertainty sampling** (least-confident, margin, entropy) with equations and from-scratch code; **query-by-committee** (vote entropy, KL disagreement; bootstrap committees); **diversity and representativeness** (k-center greedy, clustering-based, density-weighted); **batch-mode** selection and why top-*k* uncertainty gives redundant batches; cold-start problem and seeding; stopping criteria; the active-learning **simulator** with cost accounting.
- **L3:** **sampling bias**: an actively sampled labelled set is not an i.i.d. sample, so (i) never evaluate on it, (ii) accuracy and calibration are distorted — link importance weighting and selection bias (5B-10) and state the weighted-estimator idea with the assumptions, `[VERIFY]` for cited results; **model-dependence of the labelled set** (reusing the set for a different model); expected-error-reduction and expected-model-change as costlier alternatives (name, equation, cost); **cost-sensitive and noisy-oracle** active learning (annotator error, varying label cost); active learning for imbalanced and rare-event problems (5B-03); **honest evaluation**: learning curves over many seeds vs random sampling with paired differences, label-budget-to-target-metric, and **when active learning gives no gain** (reproduce this).
- **L4 adversarial situations:** evaluation set sampled by the active learner; "hard" examples that are actually mislabeled or ambiguous (the oracle is wrong most where the model is uncertain); batch queries collapsing to one cluster; cold start with a single class; a labelling workflow with drifting guidelines; a one-seed "50% label saving" claim.
- MLOps hooks: label-queue design, labeller throughput, label versioning, and **provenance of every label** (who, when, which guideline version, which model queried it).

## Unit 4 — Weak supervision and noisy labels

- **L1:** what a noisy or weak label is (heuristic rules, distant supervision, crowd workers, model outputs); **noise taxonomy** (symmetric, class-conditional, instance-dependent, annotator-dependent); why noise in training and noise in the *evaluation* set are different problems; a worked example showing accuracy bounded by label noise.
- **L2:** **programmatic weak supervision**: labelling functions with abstain, the label matrix, coverage, overlap, conflict, empirical accuracy on a small gold set; majority vote; the **generative label model** (estimate LF accuracies from agreements under conditional independence; probabilistic labels) implemented from scratch on planted LFs; training the end model on probabilistic labels (soft-label loss); the **named reference framework** Snorkel and its libraries are cited as `[VERIFY]`, not required for the labs. **Learning with noisy labels**: robust losses (e.g. MAE-type, symmetric/clipped), **loss correction via a noise transition matrix** (forward/backward) with an implementation and the check that it recovers the planted truth; small-loss sample selection; **confident learning / label-issue detection** (per-class thresholds on out-of-sample predicted probabilities, cross-validated) with an oracle test against planted flipped labels.
- **L3:** limits and assumptions: conditional independence of LFs and what correlated LFs do (the "ten copies of one rule" case) and how to **detect** it (pairwise agreement and correlation); identifiability of the transition matrix (anchor points, `[VERIFY]` cited); estimation error of the transition matrix and its sensitivity; **class-dependent noise on imbalanced data**; noise in the evaluation set: **measure the ceiling** and report metrics with noisy-label correction or an audited gold subset; annotator aggregation (Dawid–Skene-style EM, named with an implementation on planted annotators); the **cost–quality trade-off** (more noisy labels vs fewer clean ones) quantified by simulation; auditing a label set (disagreement sampling, per-class error, confusion between guideline definitions); governance: fair pay, guidelines, and review as quality controls.
- **L4 adversarial situations:** weak labels evaluated against weak labels; LFs derived from the very features the model uses (circularity); LFs written after looking at the evaluation set (leakage); a label model that is overconfident because LFs are duplicates; class-flip noise misdiagnosed as random; a gold set too small to estimate LF accuracy; a "clean" test set that carries the same systematic errors.

## Unit 5 — Practice questions (`practice-questions.md`) — see Section 7

## Unit 6 — Projects index (`Projects/README.md`) — see Section 8

## Unit 7 — Project 1: label efficiency study (`Projects/01-label-efficiency-study.md`) — see Section 9

# 7. UNIT 5 — PRACTICE QUESTIONS (REQUIREMENTS)

At least **60 questions**, tagged by unit and level (L1–L4) and by type, with a worked answer key: conceptual short answer; MCQ with "why the wrong answers are tempting"; derivations (the label-spreading closed form; the EM update for a labelled+unlabeled Gaussian mixture; the forward loss-correction equation; the entropy/margin/least-confident ranking differences on a 3-class probability table); **code-reading and bug-finding** (a self-training loop that tunes the threshold on the evaluation set; an active-learning evaluation on the queried set; an LF matrix with duplicated functions; pseudo-labels that include evaluation points); **design-a-protocol** questions (given a budget, a data description, and a cost per label, choose and defend a method or choose to simply label more); 5 **interview-style scenario** questions with senior answers; 5 **negative-result** questions ("show a case where…"). Keys give the reasoning, not just the answer; every numeric key is verified by an independent computation.

# 8. UNIT 6 — PROJECTS README (REQUIREMENTS)

Explain the project's purpose; prerequisites; the deliverable layout (`labelbench/` package, `tests/`, `reports/`, `results/`); the grading rubric as **checkable properties** (not subjective); the reproducibility contract (`make quick`, `make full`, root seed, hashes of config and outputs); the integrity rules from Section 6; how the project connects to later modules (graph ML (`../12-…`), RL foundations (`../13-…`), capstones (`../15-…`)); and a short "how to present your results to a non-ML stakeholder" template (what budget, what gain, how sure, what it assumes).

# 9. UNIT 7 — THE PROJECT (REQUIREMENTS)

## `Projects/01-label-efficiency-study.md` — builds **`labelbench`**

**Goal:** an honest, reproducible study answering: *for this data situation and this labelling budget, which of {supervised baseline, label spreading, self-training, active learning (≥ 3 query strategies), weak supervision (label model), noise-robust training} gets the most accuracy per label, and how sure are we?*

Required:

1. **Planted-truth data generator** with controllable cluster structure, class imbalance, label-noise model (symmetric / class-conditional / annotator-dependent), unlabeled-pool shift, and an oracle with per-label cost; the harness holds all true labels.
2. **Strong supervised baseline** per budget with equal hyperparameter-tuning effort, and a **learning curve** over a grid of labelled sizes.
3. **At least five methods** implemented spec-literally from earlier units (label spreading, self-training with ≥ 2 selection rules, active learning with random / uncertainty / margin / committee / diversity, label model with ≥ 6 labelling functions including deliberately correlated ones, noise-transition loss correction or confident-learning cleaning).
4. **Evaluation protocol:** frozen representative evaluation set never touched by any method; ≥ 20 seeds (`--quick` ≥ 5); paired differences to baseline with bootstrap intervals; label-budget-to-target-metric table; reported **negative results** (where a method is no better or worse than baseline).
5. **Stress scenarios (≥ 4):** shifted unlabeled pool; heavy class imbalance; class-conditional noise; correlated labelling functions; noisy oracle in active learning; evaluation labels themselves noisy (with the measured ceiling).
6. **Diagnostics:** pseudo-label accuracy per iteration, class-prior drift, calibration drift, coverage–accuracy curves, active-learning sampling-bias check, label-model accuracy-estimate error against planted truth.
7. **Engineering deliverables:** `pytest` suite with oracle tests that **pass on the reference and fail on a deliberately broken variant** for each method; a deterministic run log; a label-provenance table (who/what/when/cost) for the active-learning runs; a **decision memo** (≤ 2 pages) with the label-budget card for each scenario, the recommendation, its assumptions, and what would change it.
8. **Acceptance criteria** as commands and expected checks; a self-review checklist; stretch goals (batch active learning with diversity; Dawid–Skene annotator aggregation; importance-weighted evaluation of the actively sampled set).

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/labelbench/selftrain.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ (version differences tagged `[VERSION-SENSITIVE]`), type hints on public functions, shape/dtype annotations, runtime precondition checks (the `-1` unlabeled convention; no overlap between labelled, pool, and evaluation indices; probabilities sum to 1; non-empty classes in the labelled set; no `NaN` unless stated), and **no mutation of caller inputs (verified by a hash-before/after test)**.
4. Every method and tool has its Method/Tool card before the code; **every experiment ends with a label-budget card**.
5. Conventions are stated once (Section 6) and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; **every tool has a spec-literal reference implementation and an agreement test with scikit-learn/SciPy on tiny and random inputs, including ties in uncertainty scores, a single labelled class, empty pools, perfectly separable data, and duplicate points**; budgets and sizes (seeds × methods × rounds × bootstrap; *n²* graph memory) are guarded before allocation.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test; exact, closed-form, or planted-truth oracle preferred); tests pass on the reference and fail on a deliberately broken variant.
8. **No unproven claims** about label savings, hiring, interviews, best methods, library defaults, thresholds, or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in the appendix; every heuristic is labelled `HEURISTIC` with its measured behaviour on the planted-truth data.
10. Proofs are written in full where a unit requires them; a counterexample is a disproof; agreement on examples is not a proof.
11. Library internals (`SelfTrainingClassifier`, `LabelPropagation`, `LabelSpreading`, `LogisticRegression` default regularisation, `cross_val_predict` fold semantics, `NearestNeighbors` ties and metrics) are **not guarantees**: teach the learner to test the behaviour.
12. **Resource safety:** fit/replicate budgets validated and enforced; graph and distance matrices sized from shapes before allocation; simulations capped in code; files confined to the project directory.
13. **Security/privacy:** no `pickle`/`eval`/`exec` on untrusted input; strict loaders reject unknown fields and duplicate IDs; synthetic data only; logs hold metrics and hashed IDs, never raw rows; no network at run time.
14. No secrets, paid APIs, or downloaded datasets/models; `clean` targets list what they remove and never delete the learner's evidence log.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `SeedSequence`/`np.random.default_rng(seed)`/`random_state` derived from the recorded root seed with named spawn keys; no system-clock reads inside logic; timing only at the CLI edge, reported with spread.

# 11. SCOPE GUARD

Never re-teach Stage 1–4, 5A, or 5B-00 to 5B-10 content (link it). Do not teach deep self-supervised or contrastive pre-training, deep semi-supervised vision/NLP methods, or large-language-model-based labelling in depth (Stage 5C and later; name as one-line previews with `[VERIFY]` citations only), graph neural networks (`../12-…`), reinforcement learning (`../13-…`), full crowdsourcing-platform operations, or annotation-tool product comparisons. Do not recommend any commercial tool as "the best".

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, release notes, standards | Python docs; **NumPy**, **SciPy**, **pandas**; **scikit-learn docs** (`semi_supervised` module: `SelfTrainingClassifier`, `LabelPropagation`, `LabelSpreading`; `metrics`, `model_selection`, `calibration`, `mixture`) | API behaviour, defaults, versions |
| **T2** | Peer-reviewed papers and established textbooks (cite by title/author/venue/topic, **never invented page numbers or figures**) | Chapelle, Schölkopf & Zien, *Semi-Supervised Learning* (MIT Press); Zhu & Goldberg, *Introduction to Semi-Supervised Learning*; Zhu, Ghahramani & Lafferty (2003) on Gaussian fields and harmonic functions; Zhou et al. (2004) on learning with local and global consistency; Yarowsky (1995) on self-training; Blum & Mitchell (1998) on co-training; Lee (2013) on pseudo-labels; Arazo et al. (2020) on pseudo-labelling and confirmation bias; Settles, *Active Learning* (Synthesis Lectures) and the Settles (2009) literature survey; Seung, Opper & Sompolinsky (1992) on query by committee; Sener & Savarese (2018) on core-set active learning; Ratner et al. (2016, 2017/2019) on data programming and Snorkel; Dawid & Skene (1979); Natarajan et al. (2013) on learning with noisy labels; Patrini et al. (2017) on loss correction; Northcutt, Jiang & Chuang (2021) on confident learning; Frénay & Verleysen (2014) survey on classification in the presence of label noise; Song et al. (2022) survey on learning from noisy labels; Sohn et al. (2020) FixMatch, Tarvainen & Valpola (2017) mean teacher (previews only) | Definitions, methods, equations, known limits |
| **T3** | Reputable university lecture notes and engineering write-ups | Only as a pointer, only if canonical, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your own memory) | — | **Never sufficient.** Convert to a derivation, a check, or `[VERIFY]` |

Rules:
1. Every definition, equation, and attributed method cites a T1/T2 source **by name** in the unit's `N.14` and in the appendix source ledger. Paper titles and authors may be given only if you are confident; otherwise write the topic and `[VERIFY]`.
2. **Never fabricate** a citation, DOI, URL, page, figure, dataset result, or quote. A claim you cannot trace is rewritten as a derivation, replaced by a runnable check on planted data, or removed.
3. Numerical statements are either (a) the output of code in the syllabus with a seed, (b) an exact derivation, or (c) cited and `[VERIFY]`.
4. Version-specific API facts name the version checked and are tagged `[VERSION-SENSITIVE]`.

## 12.2 Mandatory multi-pass self-audit (run after drafting, before delivering each part)

- **Pass A — Factual audit:** list every factual claim in the part; assign each a tier and status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT); fix or remove any with none.
- **Pass B — Mathematical audit:** re-derive every equation and every numeric answer key independently (second method); check dimensions and indices; check every sign.
- **Pass C — Code audit:** every snippet is complete, runs as written, has a stated oracle independent of the function under test, and its printed output matches what the code would produce; seeds and budgets present.
- **Pass D — Leakage audit:** for every experiment, confirm in writing that evaluation indices never enter selection, tuning, pseudo-labelling, graph construction, query pools, or label-model fitting.
- **Pass E — Over-claim audit:** hunt for universal claims ("always", "never", "best", "X% fewer labels") and replace with conditional, measured, or cited statements.
- **Pass F — Consistency audit:** names, paths, conventions, seeds, and cross-references match the tree and the other units.
- **Pass G — Safety and integrity audit:** privacy, annotator welfare, resource caps, no network, no secrets.

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

- **Appendix A — Source ledger:** every cited work: name, authors, year, tier, what it is used for, `[VERIFY]` flag.
- **Appendix B — Claim ledger:** every non-trivial claim: unit, claim, status, evidence.
- **Appendix C — `[VERIFY]` register:** every unresolved item with exactly how the reader can verify it (which doc or paper, which check).
- **Appendix D — Audit report:** results of Passes A–G per unit (what was found, what was changed), and an honest list of residual risks.
- **Appendix E — Proof and status table; Appendix F — Version and platform notes; Appendix G — Glossary.**

## 12.4 Trust rules

- Say "I could not verify this" rather than guess. Mark residual uncertainty explicitly; never hide it.
- No claim about the model's own browsing: if you have no tool access to sources, say the citations are from memory, tag each `[VERIFY]`, and list what the human should check first.
- The human operator will perform a final source check; make that easy (Appendix C).

# 13. OUTPUT FORMAT AND DELIVERY PROTOCOL

**Format:** one Markdown document; headings exactly as Section 5; code in fenced blocks with language tags; tables for catalogues; Mermaid for diagrams; no HTML.

**The output is too large for one response.** Deliver in numbered parts:

1. **Part 0:** an outline: unit list with planned sizes, the conventions block, the running-example specification, the source ledger (draft), and the part plan. Then stop.
2. **Parts 1–N:** one unit per part (Unit 0 and 1 may share; Unit 7 may take two). Each part ends with `PART k/N COMPLETE — audit Passes A–G done — type "continue"`. Never summarise a unit instead of writing it; never truncate with "etc." or "similar to above".
3. **Final part:** Appendices A–G and a **coverage matrix** mapping every bullet in Sections 6–9 to the heading where it is taught.

If a part would be cut off, stop at a clean boundary and say so; resume exactly there on `continue`.

# 14. QUALITY BAR — DEFINITION OF DONE

- [ ] Every unit in Section 2 present, in order, matching the tree; no extra files.
- [ ] Every unit (1–4, 7) has all four levels and every skeleton heading `N.0`–`N.14`.
- [ ] Every Section 6 bullet is taught and appears in the coverage matrix.
- [ ] Every method has a Method/Tool card, a from-scratch reference, a library agreement test, and an independent oracle; broken variants fail the tests.
- [ ] Every experiment has a label-budget card, a supervised baseline at equal budget, an untouched evaluation set, ≥ 20 seeds (quick ≥ 5), paired differences with intervals.
- [ ] Negative results are present for semi-supervised learning, self-training, active learning, and weak supervision.
- [ ] The project (labelbench) is complete with stress scenarios, diagnostics, tests, and decision memo.
- [ ] ≥ 60 practice questions with verified keys.
- [ ] All Section 12 audit passes done; Appendices A–G present; every `[VERIFY]` registered; no fabricated citation.
- [ ] No hype, no outcome or hiring claims, no company claims.

# 15. START

Begin with **Part 0** now. Do not ask clarifying questions; record any assumption as `[ASSUMPTION]`.

=== END PROMPT ===

## Notes for the human operator (not part of the prompt)

- **Audit step is yours too.** The prompt makes the model self-audit and emit Appendices A–D, but a model without browsing can only cite from memory. Before accepting the syllabus, work through **Appendix C (`[VERIFY]` register)**: check each cited paper/book and each scikit-learn behaviour (`SelfTrainingClassifier`, `LabelPropagation`, `LabelSpreading`) against the official docs for the version you install, and run every code block and `pytest` suite.
- Split the finished syllabus into the seven target files listed in Section 2; keep this prompt file alongside.
- If a part comes back truncated or summarised, reply `redo part k in full`.
