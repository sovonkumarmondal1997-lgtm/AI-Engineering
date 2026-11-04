# PROMPT — Generate `SYLLABUS-Overview.md` (Stage 4B, module S4B-00)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is very large, so use the **Delivery Protocol** (Section 14): the model delivers numbered parts and you type `continue` between them. Save the concatenation as `SYLLABUS-Overview.md` in `Stage 4B — Mathematics for Machine Learning/00-Stage-4-Overview/`.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have trained, shipped, and monitored models in production, and you have debugged failures that trace back to weak mathematical foundations: a softmax that overflowed because nobody used log-sum-exp; a cross-entropy that returned `nan` from `log(0)`; a gradient that was wrong by a transpose and still "trained"; a cosine similarity computed on unnormalized vectors; a "significant" A/B result that was noise; a model comparison made on one seed; a perplexity compared across different tokenizers; a float32 reduction that disagreed with float64 in the fourth digit. You have also mentored engineers who write excellent Python but have not used calculus, linear algebra, or probability since university. You teach the way you work: **derive by hand, verify independently by computation, state assumptions and tolerances, and make every statement checkable.**

You are also a careful technical author. You never invent a function, signature, default, formula, constant, version, statistic, citation, **claim about how much mathematics any employer, interview, or role requires, "time to learn" figure presented as fact, or claim about how any real company, model, or product works**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion is marked `[JUDGEMENT]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 4B — Mathematics for Machine Learning / 00-Stage-4-Overview/` (module code **S4B-00**, the **Stage 4B orientation, planning, bridging, and integration module**).

Output file name: **`SYLLABUS-Overview.md`**, saved inside that folder.

All code, labs, worked examples, and the project are in **Python** (NumPy-centred; see Section 3).

Teach, **one after another, from beginner to advanced**, these 5 units in this exact order. Each unit maps to a file later written from this syllabus (the repository tree is exactly this; the files are currently empty):

| # | Unit | Target file |
|---|---|---|
| 1 | Stage 4B orientation | `README.md` |
| 2 | Learning plan and pacing | `learning-plan.md` |
| 3 | How Stage 4B connects to Stage 4A and Stage 4C | `how-4b-connects-to-4a-and-4c.md` |
| 4 | Overview project index | `Projects/README.md` |
| 5 | Overview project: Math-for-ML notebook library | `Projects/01-math-for-ml-notebook-library.md` |

Do **not** add, merge, skip, or reorder units. There is **no `practice-questions.md` and no readiness file** in this folder (the tree has none); self-check questions live inside each unit (Section 7), and the entry check links to Stage 4A's readiness material instead of rebuilding it. The Stage-level `../README.md` is **out of scope**. **This module does not teach the content of Modules 01–14**; it orients, plans, maps, and integrates. Link to every lesson; never re-teach it beyond a one-line recall. Do not write shallow summaries: this is the **teaching content itself**, not an outline.

**Priority:** Unit 3 is the intellectual core of this module and gets the deepest treatment (Section 6, Unit 3). Units 1, 2, 4, 5 must still meet their full requirements.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–3 and (ideally) Stage 4A. They write working Python (functions, classes, `venv`, `pytest`), use Git and a Linux shell, and know Big-O and basic algorithms. They have school-level algebra, functions, logarithms, exponents, summation, descriptive statistics, and vectors-as-arrows from 4A. They have **not** necessarily done calculus, linear algebra, or probability. Some are rusty, some strong and want to skip, some anxious about maths.
- **Stage position:** 4A (basic mathematics) → **4B (this stage: the mathematics every ML engineer uses daily)** → 4C (advanced mathematics for deep learning) → Stages 5A–5D (ML Foundation; Advanced ML; Deep Learning & Transformers; MLOps). Where Stage 3 or 4A taught a topic already, **link back and state what 4B adds**; never duplicate.
- **Stage structure the syllabus must reflect.** Module names, lesson names, and counts are fixed by the repository tree. **The tree is the source of truth**; report any mismatch with this prompt as `OPEN`. Stage totals to state as **repository facts to re-verify**: **15 folders (00–14), 80 lessons, 159 files**; the tree currently contains **32 project files** (1 overview + 31 module projects) while `Roadmap.md`'s summary table lists **30** in its project column. Report this as an `OPEN` discrepancy and do not resolve it by guessing.

| Code | Module (folder) | Lessons | Module projects (in its `Projects/`) |
|---|---|---|---|
| 01 | `01-Vectors-Dot-Product-and-Norms` | 5 | `01-vector-operations-library-in-numpy.md`, `02-geometry-of-dot-product-explorer.md` |
| 02 | `02-Matrices-and-Linear-Transformations` | 9 | `01-matrix-operations-from-scratch.md`, `02-gaussian-elimination-solver.md`, `03-linear-transformation-visualizer.md` |
| 03 | `03-Eigenvalues-SVD-and-Low-Rank-Structure` | 5 | `01-eigenvalue-power-iteration.md`, `02-image-compression-with-svd.md` |
| 04 | `04-Similarity-Distance-and-Embedding-Geometry` | 3 | `01-word-vector-similarity-explorer.md`, `02-curse-of-dimensionality-experiments.md` |
| 05 | `05-Derivatives-and-Single-Variable-Optimization` | 8 | `01-symbolic-and-numerical-derivative-comparison.md`, `02-numerical-gradient-checker.md` |
| 06 | `06-Integral-Calculus` | 6 | `01-numerical-integration-toolkit.md`, `02-area-under-a-density-curve-lab.md` |
| 07 | `07-Multivariable-Calculus-and-Gradients` | 4 | `01-gradient-field-and-contour-plotter.md`, `02-backpropagation-by-hand-on-a-tiny-network.md` |
| 08 | `08-Optimization-Fundamentals` | 5 | `01-gradient-descent-visualizer.md`, `02-optimizer-comparison-sgd-momentum-adam.md` |
| 09 | `09-Probability-Fundamentals` | 8 | `01-probability-simulations.md`, `02-bayes-spam-filter-by-hand.md` |
| 10 | `10-Common-Distributions` | 6 | `01-distribution-gallery-and-fitting.md`, `02-poisson-event-rate-simulator.md` |
| 11 | `11-Sampling-and-Limit-Theorems` | 4 | `01-sampling-from-a-next-token-distribution.md`, `02-clt-and-lln-simulation-lab.md` |
| 12 | `12-Inferential-Statistics-for-Experiments-and-Evals` | 7 | `01-is-prompt-b-really-better.md`, `02-bootstrap-confidence-interval-lab.md`, `03-ab-test-analysis-report.md` |
| 13 | `13-Information-Theory-for-ML` | 5 | `01-compute-perplexity-of-text.md`, `02-entropy-and-kl-explorer.md` |
| 14 | `14-Linear-Models-Mathematics` | 5 | `01-linear-regression-from-scratch-in-numpy.md`, `02-logistic-regression-from-scratch.md`, `03-ridge-versus-lasso-comparison.md` |

  Every module folder also has `README.md`, `practice-questions.md`, and `Projects/README.md`. Lesson file names inside each module are listed in the repository tree; **use them verbatim** in every link and table.
- **Neighbouring structure to map against** (names exactly as in the repository):
  - **4A:** 01 Number Systems and Arithmetic Essentials; 02 Fractions, Ratios and Percentages; 03 Algebra Foundations; 04 Equations, Inequalities and Systems; 05 Exponents, Roots and Growth; 06 Logarithms; 07 Functions and Graphs; 08 Geometry and Trigonometry; 09 Vectors as Arrows and Data Points; 10 Sequences, Series and Summation; 11 Counting and Combinatorics; 12 Descriptive Statistics Basics; 13 Limits and Rates of Change Bridge; 14 Complex Numbers (Optional); 15 Mathematical Notation, Reasoning and Math in Code (overview folder `00-Prerequisite-Overview`, with its readiness checklist).
  - **4C:** 01 Advanced Linear Algebra; 02 Multivariable and Matrix Calculus; 03 Optimization Theory and Training Algorithms; 04 Advanced Probability; 05 Statistical Estimation and Bayesian Inference; 06 Advanced Information Theory; 07 Mathematics of Deep Learning Training; 08 Mathematics of Convolutional and Recurrent Models; 09 Mathematics of Transformers and Representations; 10 Mathematics of Generative and Latent-Variable Models (overview folder `00-Stage-4C-Overview`, whose connection file is named `how-4c-connects-to-4b-and-the-ml-stages.md`).
  - **Stages 5A–5D:** forward targets. Read the lesson-level names from the repository tree for 5A (`01-Machine-Learning-Fundamentals-and-Problem-Framing` … `13-Stage-5A-Capstone`) and from the tree for 5B–5D; **use only names that exist in the tree**; otherwise name the stage only.
- **Zero budget.** Everything runs on a **local laptop** (WSL2 Ubuntu primary; native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. **No paid service, no GPU, no accounts, no API keys, no network at run time, no scraping, no downloaded problem sets, textbooks, or datasets.** **Every problem, scenario, and dataset is original or synthetic** (seeded generators). **Disk footprint cap for any lab or project: default ≤ 64 MB, `--quick` ≤ 8 MB.** One-time `pip install` of the pinned tools is the only permitted network use, stated explicitly, with an offline-after-install check.
- **Tool baseline:** **CPython 3.12** `[ASSUMPTION; minimum 3.10, differences noted]`, `venv`, `pytest`, **`numpy`** (required), **`scipy`** (required as an *independent oracle* and for distributions), **`sympy`** (symbolic oracle), **`matplotlib`** (plots; a text/ASCII fallback must exist), **`jupyterlab` + `nbclient`/`nbformat`** and **`jupytext`** (notebooks, Unit 5). Optional: `hypothesis`, `ruff`, `mypy`, `nbstripout`, `pandas` (display only), a deep-learning autograd library **only as an oracle for gradients if already installed — never required**. Pin versions in a `requirements.txt`/`pyproject.toml`; every version number is `[VERIFY]` against PyPI and the library's release notes. State the NumPy 1.x vs 2.x behavioural differences that matter to the labs (`[VERSION-SENSITIVE]`) rather than assuming one.
- **Domain flavour (all original, no real-company claims):** tokens and logits, softmax and temperature, embeddings and retrieval, loss curves, learning-rate choices, evaluation of two prompts or two models, A/B experiments, perplexity, regularization, low-rank compression, feature scaling.
- **Running example thread:** **"the learner's Math-for-ML notebook library `mlmath`"** evolves through the folder: orient and set up the environment (Unit 1) → schedule the 14 modules and their notebooks (Unit 2) → map every notebook's skills to what uses them downstream (Unit 3) → organise the project evidence (Unit 4) → assemble, test, and ship the library (Unit 5). Reuse it so the learner sees one artifact grow.
- **Continuity and links:** link back to **Stage 4A** (`00-Prerequisite-Overview` and the specific 4A modules named in Unit 3), **S3-14** (stress harness and exact oracles), **S3-20** (practice log, error log, spaced-repetition deck — **reuse, never rebuild**), and Stage 2/3 testing conventions. Forward-link to 4C modules and to Stages 5A–5D by exact names. State clearly **what is taught here vs deferred**: this module teaches **orientation and study method for ML mathematics, planning as a dependency problem, prerequisite→ML mapping with verification, numerical-correctness discipline, and integration of verified notebooks**; **vectors through linear models are taught in Modules 01–14; proofs, matrix calculus, measure-theoretic probability, Bayesian inference, and the mathematics of specific architectures are deferred to 4C**; **no outcome guarantees and no employer-specific claims are made**.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1, 2, 3, 5)

Each of these units progresses through **exactly these four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the artifact and its purpose, follows a worked example, applies the basic template to a small case with prompts. |
| **L2** | Intermediate — Working Practice | Applies it unaided to their own situation within a timebox, using the templates and tools, avoiding the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | States criteria as checkable properties, justifies decisions with exact computation and independent oracles, quantifies numerical and statistical uncertainty, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Adapts to unfamiliar learners and gaps, diagnoses failures in others' plans, maps, and notebooks, and could coach another engineer through Stage 4B. |

Unit 4 uses the structure in Section 9.

# 5. MANDATORY STRUCTURE FOR UNITS 1, 2, 3, AND 5

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
(Glossary table: term | precise definition | common misconception. One mermaid diagram annotated for a worked example.)

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
- Method card (activities) and Tool card (tools): (1) goal and when to use, (2) inputs/outputs, (3) steps with timeboxes, (4) invariants or acceptance criteria as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain for tools
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure; how to avoid fooling yourself)
- Exercise requiring a defended justification, derivation, or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial/unfamiliar situations (a learner with a 10-year gap; a learner who "knows it" but cannot derive it; a map that drifts from the repo; a notebook that passes only on one machine)
- Automation (aggregate verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's plan, map, or notebook with evidence-based feedback
- Edge cases and platform differences (Python 3.10 vs 3.12; NumPy 1.x vs 2.x; WSL2 vs native; BLAS thread count; float32 vs float64)

### N.7 Engineering lens
(Where weak mathematics fails in real ML engineering — verifiable numerical and statistical failures only, never a company claim. Failure modes, blast radius, cost.)

### N.8 Integrity lens
(Reasoning and measurement risks: self-rating bias, memorising derivations without understanding, p-hacking in the learner's own experiments, cherry-picked seeds, AI-assistance disclosure, fairness and accessibility. Controls, each verifiable by a command, test, or written check.)

### N.9 Checklist
(Checkbox list; every item verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, seeded, local-only, safe to re-run, with `--quick`.)

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

These topics are the **minimum**; add depth, never remove. **Every lesson-sized topic contains at least two fully worked original examples (at least three in Unit 3), each verified two independent ways.** **Every tool gets a Tool card, tests (including exhaustive small-domain tests), and deterministic behaviour (seeds, injected clocks).** **The module never re-teaches a 4A or 4B lesson, a Stage 3 algorithm, or an S3-14/S3-20 tool: it names and links.**

## Conventions stated once, used everywhere

- **Claims policy.** Every claim about learning efficacy, study method, hiring, interviews, or how much mathematics a role needs is exactly one of: (a) cited research tagged `[VERIFY]` with its limits; (b) practitioner opinion tagged `[JUDGEMENT]`; (c) a verifiable statement about mathematics, code, or the repository tree; or (d) omitted. **No success rates, no outcome guarantees, no statements about what any named company asks or requires, no invented quotes or anecdotes, no "N% of ML work uses X".** All durations are `[ASSUMPTION]` templates the learner replaces with measured values.
- **Mathematical correctness policy.** Every worked example and every key is verified **two independent ways**: (1) a hand derivation shown in the text, and (2) an independent computation in Python (exact `Fraction`/`sympy` where possible; otherwise NumPy/SciPy with a **stated tolerance and reason**; never float `==`). A third check (a different library, finite differences, or Monte Carlo with a stated error bar) is encouraged. **Domains and conventions are stated before use** (e.g., `log` argument > 0; `0·log 0 := 0` as a convention; `0⁰`; sample vs population `ddof`; row-vector vs column-vector convention; axis conventions; natural log vs log₂ and the units nats vs bits). **Numerical agreement on examples is evidence, not proof of a general statement; say so.**
- **Numerical-correctness policy (ML-specific, taught explicitly in Units 1 and 5).** float32 vs float64 and machine epsilon (`np.finfo`); `np.isclose`/`np.allclose` defaults (`rtol=1e-05`, `atol=1e-08`) and why `atol` matters near zero `[VERIFY]`; catastrophic cancellation; stable softmax and log-sum-exp (derive the shift identity); `log1p`/`expm1`; clipping vs epsilon-adding in cross-entropy and their different biases; why `np.linalg.inv` is avoided for solving (`solve`/`lstsq`); condition number; central vs forward finite differences and the step-size trade-off; relative-error gradient checking with stated thresholds (`HEURISTIC`); summation order and `math.fsum`; determinism (seeds, `np.random.default_rng`, BLAS thread effects) — **a result that cannot be reproduced is not a result**.
- **Index and notation convention.** Mathematical sums and indices are written **1-based** in text with the **0-based Python translation shown side by side**; every symbol is defined at first use; plain-text math with Unicode (`Σ`, `∇`, `∂`, `∈`, `≈`) — **avoid LaTeX that may not render**; shape annotations (`X: (n, d)`) on every array in every example; one stated convention for vectors (column) and data matrices (rows = samples) used everywhere, and where a lesson or library differs, say so.
- **Original-content policy.** All problems, data, and scenarios are original or synthetic. Named results (e.g., the chain rule, the Central Limit Theorem, the Eckart–Young theorem, Bayes' theorem) are referred to **by name and statement only**, never by reproducing a textbook's wording, examples, figures, or exercise sets. No downloaded or scraped content.
- **Randomness and time policy.** Every randomized component takes an explicit `np.random.Generator` or seed (never the legacy global state); tools never read the system clock inside logic (the CLI edge injects it); every Monte Carlo statement carries its sample size and a Monte Carlo error estimate.
- **Data and security policy.** All data local, human-readable (JSON/CSV/`.py`/`.ipynb`-with-outputs-stripped), validated, written atomically (`os.replace`); no PII, no telemetry, no network; never `pickle`/`marshal`/`eval`/`exec` on untrusted text; notebooks are **executed only from the learner's own project directory**, with the stated warning that opening a notebook runs code.
- **Integrity and ethics policy.** Notebooks and derivations are the learner's own work; AI assistance is allowed for explanation and review, **must be disclosed in the evidence log**, and AI-produced derivations or code are **untrusted hypotheses verified against an oracle**. Honest self-representation; fairness and accessibility awareness (screen-reader-friendly plot alternatives, text fallbacks); maths anxiety acknowledged as a real experience (awareness only, `[JUDGEMENT]`, no clinical claims).
- **Result status vocabulary:** `PROVED`, `CITED`, `EVIDENCE ONLY`, `HEURISTIC`, `JUDGEMENT` (markers: `[ASSUMPTION]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[VERIFY]`). **Exhaustive or seeded testing never upgrades a status to `PROVED`.**
- **Stage gate convention (inherits the repository's):** ≥ 80% proceed; 60–79% remediate named modules and retake; < 60% repeat prerequisites. Thresholds and weights are `HEURISTIC`/`JUDGEMENT`; **no certificate or credential is implied.**

---

## Unit 1 — Stage 4B orientation (`README.md`)

- **L1:** **what Stage 4B is and is not**: the mathematics an ML engineer uses to *read, implement, debug, and evaluate* models — vectors and matrices, eigen/SVD, similarity geometry, derivatives and integrals, gradients and backpropagation, optimizers, probability, distributions, sampling, inference for experiments and evals, information theory, and the mathematics of linear/logistic models; **not** a proof-based course and **not** 4C's architecture-specific mathematics; **how the folder is organised** (14 modules, each with `README.md` + numbered lessons + `practice-questions.md` + `Projects/`; this overview first); **the lesson loop** (read → derive by hand → implement in NumPy → verify against an oracle → explain aloud); **"hand first, machine second"**; **three kinds of skill** (derive, compute, translate-to-code-and-check) and why ML engineering needs all three; **setting up** (`venv`, pinned installs, `pytest`, a `env_check` tool reporting Python/NumPy/SciPy/SymPy/Matplotlib/Jupyter versions, BLAS thread info, and float32/float64 epsilon — no hostnames or usernames); **first demos**: (a) the stable-vs-naive softmax overflow, (b) a shape-error and a silent-broadcasting bug in NumPy, (c) a finite-difference derivative vs the analytic one; **reading map** for the whole stage with links to every module `README.md`; **"why this order"** in one picture.
- **L2:** **navigating the tree** (path map, naming conventions, where practice/projects/evidence live); **a timeboxed lesson routine** (template minutes per phase, `[ASSUMPTION]`); **the notebook-and-evidence layout** (`stage4b/NN-<module>/` with `notes/`, `notebooks/`, `practice/`, `project/`, `evidence-log.md`; **jupytext-paired `.py` files so diffs and tests work; outputs stripped before commit**); **the error log** (reuse S3-20: slip vs misconception vs gap; weekly review; **link, don't rebuild**); **spaced review** (reuse the S3-20 deck; retrieval practice and spacing research named `CITED [VERIFY]` with limits); **the 4A→4B entry check** (a link-only pointer to 4A's readiness checklist plus a 10-item **4B entry diagnostic of original items on the specific 4A skills 4B uses**, scored by script, with the 80/60 convention); **when to use NumPy/SciPy/SymPy/a calculator and when not** (the "oracle, not crutch" rule); **study habits that fail** (watching derivations, copying solutions, skipping the by-hand step) with detection signals; **reading ML papers' notation** (a short method; link to 4A Module 15).
- **L3:** **stage objectives as checkable can-do statements**, each tied to lessons, at least one practice item, and a project artifact — a traceability table in JSON checked by an `objtrace` tool (every objective has ≥ 1 lesson, ≥ 1 item, ≥ 1 artifact; no orphans; deterministic report; **verified exhaustively over all link sets for ≤ 4 objectives × ≤ 4 items against a brute-force definition**); **definition of done for Stage 4B** (a checkable list); **the numerical-correctness policy in depth** (machine epsilon, ulp spacing, cancellation, stable log-sum-exp **derived**, `allclose` semantics, condition number as an error amplifier — each with a worked example and a verification); **what each NumPy dtype and function guarantees** (documented behaviour only, `[VERSION-SENSITIVE]`); **honest scoping** (what this stage will not make you).
- **L4:** **coaching a peer into the stage** (an intake script: background, goals, constraints, anxieties; adapt for rusty/strong/time-limited learners); **hostile cases for `objtrace`** (duplicate IDs, dangling links, cycles, huge files → full issue lists, nothing silently ignored); **testing** (golden reports, fuzzing malformed JSON, a mutation lab — orphan item not flagged; uncovered objective counted covered; off-by-one in coverage — with no surviving mutants); **drift checks** against a directory listing when the tree changes; **reproducibility triage** (a notebook that differs across NumPy versions, BLAS thread counts, or float32/float64 — find the root cause).

## Unit 2 — Learning plan and pacing (`learning-plan.md`)

- **L1:** **what a plan is and is not** (a falsifiable schedule you revise); **the default path `01 → 14`** and **why this order**, derived from the tree: e.g., 01 → 02 → 03 (linear algebra spine) → 04 (uses 01 and 03); 05 → 06 → 07 → 08 (calculus-to-optimizer spine; 07 needs 02 and 05; 08 needs 07); 09 → 10 → 11 → 12 (probability-to-inference spine; 12 needs 11); 13 needs 09–10; 14 is the **integration module** needing 02, 07, 08, 09–10, 13 (**verify each edge against the lessons; mark disputed edges `JUDGEMENT`**); **a first-week plan** (setup, entry diagnostic, Module 01 lessons 1–2); **time estimation basics** (measure your own minutes per lesson; replace `[ASSUMPTION]` defaults); **weekly rhythm template** (study, review, project, rest — `JUDGEMENT`, no medical claims).
- **L2:** **three pathways, each a full original plan with milestones:** **Full** (all 80 lessons and all projects); **Interview-agnostic ML-engineer fast track** (the minimum closure needed for Stage 5A: derived from Unit 3's map, with a **required evidence item per skipped lesson** — one derivation and one oracle-checked notebook cell; **no claim about interviews or jobs**); **Refresher** (modules 09, 12, 13 first, then 02, 07, 08, then gap-fill); **hours-per-week variants** (5/10/15/20, `[ASSUMPTION]`) with calendars; **module gating** (a module is done only when its practice set and project meet their checklists); **the `plan.json` schema** (modules, lessons, prerequisites, hours, review slots, milestones — validated); **spiral review** (module N's key skills revisited after N+1 and N+3); **buffers and catch-up weeks**; **planned vs actual** logging; **parallel tracks** (a calculus track and a probability track can interleave once their prerequisites are met — show the rule).
- **L3:** **planning as a dependency problem**: the lesson-level prerequisite DAG; **topological order and critical path** (S3-08 recall: link, don't re-teach); **the `plan` tool** (Tool card: validates DAG (no cycles, no unknown nodes), no module before its prerequisites, weekly hours ≤ budget, every module has a review slot; outputs an order, critical-path length, slack; **verified exhaustively against brute-force enumeration of all orderings on every DAG with ≤ 5 nodes**); **allocating a fixed hour budget by diagnostic gap** (a worked example where **greedy gap-per-hour is suboptimal** vs exact DP on a small instance, with a minimal counterexample); **effort estimation and the planning fallacy** (`CITED [VERIFY]`; buffer policy `JUDGEMENT`); **an expanding-interval review schedule** (a pure function from a completion day to review days, `HEURISTIC`; properties checked: strictly increasing, deterministic); **measuring adherence** (adherence is not learning).
- **L4:** **re-planning after slippage** (verification over breadth: fewer lessons fully verified beats more skimmed — `JUDGEMENT`); **compressing for a deadline** (safest compressions justified from the Unit 3 map, not folklore); **overlapping 4B with early 4C or 5A work** (only if the target's prerequisite closure from Unit 3 is satisfied — a checkable rule); **plans for different constraints** (full-time, evenings, interrupted study, accessibility needs); **hostile inputs for `plan`** (cycles, duplicates, negative hours, enormous files → full issue list); **testing** (exhaustive small-DAG tests, fuzzing, golden schedules, mutation lab — prerequisite violation not flagged; slack off by one; review slot skipped — no surviving mutants); **peer plan-review checklist**; coaching approach.

## Unit 3 — How Stage 4B connects to Stage 4A and Stage 4C (`how-4b-connects-to-4a-and-4c.md`) — **core unit; deepest treatment**

- **L1 (the chain, concretely):** the chain **4A → 4B → 4C → 5A–5D** in one mermaid picture with what each stage adds; **seven headline bridges, each a complete, exact, original worked example that starts in 4A mathematics and ends in an ML engineering object, then names what 4B supplies and what 4C supplies:** **(1) logarithms + sums → log-likelihood and cross-entropy** (4A-06, 4A-10 → 4B-13, 4B-14 → 4C-06); **(2) slope → derivative → gradient → one step of gradient descent** (4A-13 → 4B-05, 07, 08 → 4C-02, 03); **(3) vector length and angle → dot product, norms, cosine similarity** (4A-09 → 4B-01, 04 → 4C-09); **(4) systems of equations → matrices → the normal equation** (4A-04 → 4B-02, 14 → 4C-01); **(5) mean/variance/z-score → sampling distributions, standard error, confidence intervals** (4A-12 → 4B-11, 12 → 4C-05); **(6) counting and percentages → probability, Bayes' rule, and a base-rate trap** (4A-02, 4A-11 → 4B-09 → 4C-04); **(7) exponentials and ratios → softmax and temperature** (4A-05 → 4B-10 → 4C-09). Each example is solved by hand and by NumPy/SymPy with an oracle, and ends with a **"what is still missing"** box.
- **L2 (the full connection matrix):** for **every 4B lesson (all 80)** — **grouped by module in tables** — give: **upstream 4A lesson(s) and module(s) (exact names)**, **downstream 4C module(s) (exact folder names)**, **the downstream 5A–5D stage/module where the skill appears (only names present in the tree, else stage only)**, **the specific skill used**, **the symptom of a missing skill ("you will be unable to …")**, and a **strength rating (essential / helpful / background — `JUDGEMENT`)**. Seed hypotheses to *test, not copy*: 01→4C-01/09; 02→4C-01/02/07; 03→4C-01/07 and PCA/low-rank ideas; 04→4C-09 and retrieval-style systems; 05→4C-02; 06→4C-04/10; 07→4C-02/07 (backprop); 08→4C-03/07; 09→4C-04/05; 10→4C-04/05/10; 11→4C-04/10 and Monte Carlo; 12→4C-05 and 5A evaluation modules; 13→4C-06/10; 14→4C-05 and 5A regression/classification modules. Also: **the 4B internal dependency graph** (mermaid, lesson-level for the spines); **what 4B deliberately does not cover and where it is taught** (e.g., proofs and four fundamental subspaces → 4C-01; matrix calculus and Jacobians/Hessians in depth → 4C-02; convex-optimization theory and Adam's analysis → 4C-03; measure-theoretic and multivariate probability → 4C-04; MLE/MAP/Bayesian inference → 4C-05; KL/mutual information in depth → 4C-06); **the two handoff contracts**: *4A → 4B* (what 4B assumes — a checkable list aligned with 4A's exit criteria) and *4B → 4C* (what 4C assumes — a checkable list aligned with Unit 4's artifacts); **link to the 4A and 4C overview connection files by exact path**.
- **L3 (testable prerequisite claims):** every edge in the map is a **hypothesis** with a concrete **challenge test** (attempt the downstream lesson's first derivation without the skill); store the map as JSON; **the `links` tool** (Tool card: loads the connection map; computes the **transitive prerequisite closure** of any 4B/4C/5x target back to 4A lessons; computes the **minimal lesson set** covering a chosen target; reports "what breaks if lesson X is omitted"; **verified against brute-force reachability on every DAG with ≤ 5 nodes**); **a full written proof of closure correctness** (invariant on the visited set; termination on finite DAGs); **consistency checks** (every path exists in a supplied directory listing; every name matches the tree exactly; no edge to a non-existent module; counts 15/80/159 re-derived from the listing); **the "same idea, three costumes" analysis** — trace four ML objects end to end, each with a runnable cross-stage derivation: **softmax/cross-entropy gradient** (`∂L/∂z = p − y`; derived by hand, verified by finite differences and SymPy), **PCA via SVD** (4B-03 → 4C-01), **linear regression three ways** (normal equation, gradient descent, `lstsq` — 4B-14), and **a paired model comparison** (4B-12 → 5A evaluation); **authoritative cross-references** used for topic mapping only, `[VERIFY]`: Deisenroth, Faisal & Ong, *Mathematics for Machine Learning*; Goodfellow, Bengio & Courville, *Deep Learning* (Part I); Boyd & Vandenberghe, *Convex Optimization*; Strang, *Linear Algebra and Its Applications*; Cover & Thomas, *Elements of Information Theory*; Casella & Berger, *Statistical Inference*.
- **L4 (diagnosis and maintenance):** **symptom-to-root-cause triage**: given a stuck point in 4C or 5x (e.g., "I cannot follow the derivation of the attention softmax gradient", "my logistic regression loss is `nan`", "my A/B result flips with the seed"), walk the map back to the 4B (and 4A) lessons responsible — **at least ten original triage cases with exact answers and the verifying command**; **learners who can skip** (evidence rules, linking to Unit 2); **maintaining the map** when 4B/4C change (drift detection vs listings, changelog); **hostile inputs for `links`** (dangling edges, cycles, duplicate IDs, 10⁵-node files within caps → full issue lists); **testing** (exhaustive small-DAG tests, golden closures, mutation lab — closure misses a transitive edge; minimal set non-minimal; off-by-one in listing check — no surviving mutants); **a reviewer's challenge protocol** for strength ratings.

## Unit 4 — Overview project index (`Projects/README.md`) — see Section 9

## Unit 5 — Overview project: Math-for-ML notebook library (`Projects/01-math-for-ml-notebook-library.md`) — see Section 8

# 7. SELF-CHECK AND PRACTICE REQUIREMENTS

There is **no standalone practice file** here. Each of Units 1, 2, 3, 5 contains N.10 labs and **N.11 self-check questions (6–10, each with a model answer and common wrong answers)**: at least **2 mathematical items with exact or tolerance-stated answers verified by an oracle**, **2 scenario/critique items** (an original plan, map, or notebook to critique), and **1 coding question** with an independent oracle. Unit 3 additionally carries the ≥ 10 triage cases. Provide a scoring rubric per unit with the 80/60 gate (curriculum convention, `HEURISTIC`). Unit 4 has 3 self-check questions.

# 8. UNIT 5 — OVERVIEW PROJECT: MATH-FOR-ML NOTEBOOK LIBRARY (REQUIREMENTS)

**Target file:** `Projects/01-math-for-ml-notebook-library.md`. This is the **Stage 4B stage project**. Apply the four levels and sections N.0–N.14. It **integrates the 14 modules into one local, tested Python package and notebook set, `mlmath`**, and teaches **no new mathematics**; it teaches **engineering a verified math reference**.

**Required components:**
1. **The library (`src/mlmath/`).** At least **one verified function group per module (≥ 40 functions total)**, NumPy-vectorised, type-hinted, with documented shape and dtype contracts and runtime precondition checks (`ValueError` with stable messages): e.g., `dot`/`norm`/`project`; `matmul`/`solve_gauss`/`rank`; power iteration, SVD low-rank approximation with Eckart–Young error check; `cosine_sim`/`pairwise_distance`; numerical derivative/gradient and `gradcheck`; trapezoid/Simpson integration; `softmax`/`log_softmax`/`logsumexp` (stable); gradient descent with momentum/RMSprop/Adam; Bayes update; distribution log-pmf/log-pdf; inverse-transform and categorical sampling with temperature/top-k/top-p; bootstrap CI, paired test, proportion test, power calculation; entropy/cross-entropy/KL/perplexity; linear/ridge/lasso/logistic from scratch. **Each function ships an independent oracle from a different method or library (SciPy, SymPy, brute force, or finite differences) and is never verified by importing itself.**
2. **The notebook set (`notebooks/`).** **One notebook per module (14)** plus one "capstone integration" notebook: each states its learning objective, derives by hand in Markdown, implements, verifies against the oracle, plots with a text fallback, and ends with a checklist; **jupytext-paired `.py`, outputs stripped, executed headlessly with a fixed seed and a timeout** in the test suite.
3. **Verification.** `pytest` suites with **exhaustive small-domain tests** (e.g., all 3×3 integer matrices with entries in a small range for rank/solve vs `sympy`), **seeded random tests with stated tolerances**, **adversarial inputs** (overflow, `log(0)`, singular matrices, empty arrays, NaN), and a **float32-vs-float64 sensitivity report**; **property tests** (optional Hypothesis): norm axioms, `softmax` sums to 1 and is shift-invariant, `KL ≥ 0`, symmetry of cosine similarity.
4. **Mutation analysis.** A **mutation lab** (planted: transposed matrix, wrong `ddof`, `log2` vs `ln`, missing max-shift in softmax, sign error in gradient step, off-by-one in a Riemann sum, `>` vs `≥` in a hypothesis-test decision) with **no surviving mutants**, and a **regression guard**.
5. **Reproducibility.** A single command **`mlmath verify`** (supports `--quick`; enforces the disk cap) that runs tests, executes the notebooks, checks outputs-stripped, and prints a PASS/FAIL list; a fresh-`venv` reproducibility contract; pinned requirements; **no network after install**.
6. **Documentation and ML-engineering quality.** `pyproject.toml` (local editable install only), a package-layout mermaid diagram, a Makefile-style command list, API reference generated from docstrings, a `CHANGELOG`, a **numerics notes** page (the policy from Section 6), and a **model-card-style "library card"**: scope, tested domains, known limitations, tolerances, versions, **what it must not be used for** (it is a teaching/reference library, not production numerics).
7. **The evidence report template.** A Markdown template the learner fills with **their own results**: per-module checklist status, oracle-agreement table, mutation score, reproducibility run, issues found, AI-use disclosure, signed integrity statement. **Ship the blank template and clearly labelled `[ILLUSTRATIVE]` synthetic example data; never fabricated results.**

**Rubric (provide in full):** requirements traceability; correctness (oracle agreement); coverage of all 14 modules; numerical robustness; notebook quality; test and mutation strength; reproducibility; documentation and library card; honesty of the report; integrity statement. Pass conditions use the 80/60 gate. **Stretch goals:** a text/SVG dashboard of the verify results; a peer review of another learner's notebook; an optional autograd-library oracle for gradients; an ML-systems "performance note" (vectorisation vs loops, measured locally with stated variance).

# 9. UNIT 4 — PROJECTS README (REQUIREMENTS)

**Target file:** `Projects/README.md`. Unit 4 does not use N.0–N.14. Use this structure (each section substantial, original, linked):
1. **What the Stage 4B projects are** and how the 31 module projects feed the stage project as evidence.
2. **Index of all projects in the tree** (1 stage project + each module's projects) as a table: module | project file | one-line purpose | key skill | verification method | relative link with exact folder and file names from Section 3. Re-count against the tree and report any discrepancy with `Roadmap.md` (30 vs 32) as `OPEN`.
3. **How to choose and sequence projects** by pathway (Unit 2), which may be skipped on the fast track, and the evidence required.
4. **Project rules** (original/synthetic data only; seeds; `--quick`; disk caps; no network; AI disclosure; honest results; numerical-correctness policy applies).
5. **Definition of done** common to all 4B projects (checkable) and the **evidence folder structure**.
6. **How module projects feed the `mlmath` library** (which project supplies which functions/notebooks; no duplication; a mapping table).
7. **A review checklist** for the learner's own and a peer's project.
8. **Promises vs delivery:** Unit 4 may promise nothing that Unit 5 or the module folders do not deliver.
Include **3 original self-check questions** and links to every module's `Projects/README.md`.

# 10. UNIT 1 README — NOTE

Unit 1 is a full L1–L4 unit, not a landing page. Its first ~30 lines must still work as a landing page: purpose, who it is for, folder map, how to start, and links to the other four target files.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and, where relevant, its path as a first-line comment (`# File: src/mlmath/linalg.py`).
2. Every command and snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus a short interpretation.
3. **Code must run** on Python 3.10+ (state if 3.12 is required), NumPy with documented 1.x/2.x differences, type hints on public functions, clarity over cleverness. Every public function states purpose, shapes, preconditions (runtime-checked), return status, and **no mutation of caller inputs**.
4. Every method and tool carries its Method/Tool card before the code.
5. Conventions are stated once and applied everywhere; mixing them is a defect.
6. Exactness first where possible; floats only with a stated tolerance and reason; **no `==` on floats**; `ddof`, `axis`, log base, and dtype stated.
7. Every worked example and tool has an **independent oracle** (a different method, a spec-literal brute force, exact arithmetic, or a different library; never importing the function under test), labelled, with tests that pass on the reference and fail on a deliberately broken variant.
8. **No unproven claims** about learning, hiring, interviews, or real systems. Cited-only results are named and tagged `[VERIFY]`, never presented as proved unless a full proof is in the text.
9. **Proof status is explicit** in every card and in Appendix F.
10. **Proofs are written in full** where required: closure and topological-order correctness; the stable log-sum-exp shift identity; the softmax–cross-entropy gradient `p − y`; the normal-equation derivation; the Eckart–Young error value for a rank-k truncation (or `CITED [VERIFY]` with a numerical check, stating clearly which); the greedy-suboptimality counterexample. A counterexample is a disproof; agreement on examples is not a proof.
11. Do not teach library internals as guarantees (NumPy/BLAS/LAPACK implementation details are `[VERSION-SENSITIVE]`; teach the learner to test).
12. **Resource safety:** every tool validates sizes before heavy work; exhaustive oracles have caps enforced in code; files confined to the project directory; no unbounded loops or allocations.
13. **Security and input validation:** no `pickle`/`eval`/`exec` on untrusted text; strict loaders reject unknown fields; oracles are looked up by name in a fixed registry; notebooks executed only from the project directory; no network at run time.
14. No secrets, no paid APIs, no downloaded content in any lab; `clean` targets list what they remove and never delete the learner's evidence log or results.
15. Every lab ends with cleanup and a check that no stray files remain.
16. Tag Python/NumPy/SciPy/SymPy version differences `[VERSION-SENSITIVE]`.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim must trace to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, standards, and library release notes | Python docs (`math`, `statistics`, `fractions`, `random`, `json`, `ast`); **NumPy docs** (`numpy.linalg`, `numpy.random.Generator`, `numpy.finfo`, `numpy.isclose`, broadcasting, NumPy 2.0 migration notes); **SciPy docs** (`scipy.stats`, `scipy.linalg`, `scipy.special.logsumexp`, `scipy.optimize`); **SymPy docs**; Matplotlib docs; Jupyter/nbclient/jupytext docs; **IEEE 754** (by name) | API behaviour, defaults, versions |
| **T2** | Peer-reviewed papers and established textbooks (cite by title/author/topic, **never invented page numbers**) | Deisenroth, Faisal & Ong, *Mathematics for Machine Learning*; Goodfellow, Bengio & Courville, *Deep Learning* Part I; Boyd & Vandenberghe, *Convex Optimization*; Strang (linear algebra); Cover & Thomas (information theory); Casella & Berger and Wasserman (inference); Efron & Tibshirani (bootstrap); Kingma & Ba (Adam, 2015); Goldberg (1991) and Higham, *Accuracy and Stability of Numerical Algorithms* (floating point); Eckart & Young (1936); Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments*; Dietterich (1998) and Demšar (2006) on comparing classifiers; Wilson (1927) / Brown, Cai & DasGupta (2001); Roediger & Karpicke (2006), Cepeda et al. (2006), Kahneman & Tversky (planning fallacy); Sweller (worked examples) | Definitions, theorems, cited results |
| **T3** | Reputable university lecture notes and engineering write-ups | Only as a pointer, only if canonical, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your own memory) | — | **Never sufficient.** Convert to a derivation, an oracle check, or `[VERIFY]` |

Rules:
- You are **writing from knowledge, not consulting sources live**, unless you actually have browsing and use it. If you browse, record the URL and access date in Appendix A; if not, state "written from knowledge; verify against current documentation." **All T1/T2 citations are `[VERIFY]`.** Provide a URL only if certain it is canonical; otherwise cite by name.
- **Computation is a source:** a hand derivation re-checked by an independent code oracle is stronger evidence than any citation; prefer it where possible.
- **Do not reproduce or closely paraphrase copyrighted text.** Name theorems and give your own statement.
- **Do not fabricate** version numbers, timings, success rates, hiring or interview statistics, statements about what any employer requires, "N% of ML practitioners…", time-to-learn figures as facts, constants or formulas without a derivation or `[VERIFY]`, library internals as guarantees, quotes, or anecdotes. If a number is needed, derive it from a stated command or label it `[ASSUMPTION]`/`[ILLUSTRATIVE]`.
- **Treat the repository tree as the source of truth** for names, counts, and paths; report conflicts as `OPEN`.
- Keep a running **Claim Register** (12.3) for every non-trivial claim.

## 12.2 Mandatory multi-pass self-audit (run after drafting, before delivering each part)

Run in order; fix every defect found.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 5 units, every required section (Sections 5–9), every unit-specific topic, L1–L4, required worked examples, all 80 lessons in the Unit 3 matrix, ≥ 10 triage cases, the full Unit 5 component list. | Any missing section/topic/example. |
| 2 | **Convention consistency** | Claims, correctness, numerical, index/notation (1-based vs 0-based, row/column convention, `ddof`, log base), original-content, randomness, data/security, integrity, gate conventions stated once and applied identically. | Any mixed or silently changed convention. |
| 3 | **Claims honesty** | Every claim on learning, study method, hiring, interviews, or role requirements is cited `[VERIFY]` with limits, `[JUDGEMENT]`/`[ASSUMPTION]`, a verifiable statement, or absent; all durations `[ASSUMPTION]`. | Unsupported efficacy, outcome, or requirement claim. |
| 4 | **Traceability** | Every objective → lesson, item, artifact; Unit 4 promises nothing Unit 5 and the folders don't deliver; every Unit 5 component maps to a unit and objective. | Orphan objective/item/promise. |
| 5 | **Mathematical correctness** | **Re-derive every definition, formula, worked example, and key by hand, independently of the draft**; check domains, signs, shapes, `ddof`, log base, units (nats/bits), transposes. | Any wrong value, sign, shape, or definition. |
| 6 | **Numerical-analysis audit** | Tolerances justified; no float `==`; stable softmax/log-sum-exp; clipping vs epsilon explained; finite-difference step sizes justified; float32 claims checked; cancellation examples verified. | Unjustified tolerance or numerically unsafe example. |
| 7 | **Tool-card audit** | `env_check`, `objtrace`, `plan`, `links`, and the `mlmath` functions/`mlmath verify` have complete cards consistent with code and tests. | Missing or inconsistent card element. |
| 8 | **Proof and derivation audit** | Every proof (Section 11 rule 10) is complete and independently re-derived; no circular or invalid step. | Any gap. |
| 9 | **Cited-results audit** | Every cited-only result (Eckart–Young if not proved, Adam, CLT, Wilson interval, planning fallacy, retrieval practice, IEEE 754, API-by-version) tagged `[VERIFY]`, listed in Appendix C with a learner-side check where possible, never presented as proved. | Cited result presented as proved or untagged. |
| 10 | **Statistical validity** | Statements from experiments carry n, seeds, and error bars or intervals; Monte Carlo error stated; no p-hacking; multiple-comparison and seed-variance cautions present in the Unit 5 report; no predictive claims. | Missing uncertainty or overclaim. |
| 11 | **Exhaustive-domain and oracle audit** | Every "verified on all small inputs" names its domain and size and is feasible; oracles independent, labelled, size-capped; never called proof. | Overclaim, infeasible domain, shared-logic oracle. |
| 12 | **Source-authenticity audit** | **Every non-trivial claim maps to a T1/T2 source (or a derivation) in Appendix A; no T4-only claims; no citation without author/title/topic; no invented page numbers, DOIs, or URLs; no misattributed result.** | Unsourced, misattributed, or invented citation. |
| 13 | **Originality and IP** | All problems, data, scenarios original or synthetic; named results by name and statement only. | Copied or closely paraphrased content. |
| 14 | **Integrity, ethics, fairness** | No cheating guidance; AI-assistance policy applied to every graded artifact; gates framed as curriculum convention, not credential; accessibility notes present; maths-anxiety awareness non-clinical. | Cheating-adjacent advice or credential framing. |
| 15 | **Privacy and data handling** | Local, human-readable, validated, atomic; no PII; `env_check` excludes hostnames/usernames; no telemetry; no network at run time. | PII, hidden network use, unsafe storage. |
| 16 | **Time, clock, determinism** | Injected clocks; `np.random.Generator` seeds everywhere; deterministic ordering/tie-breaks; thread-count effects acknowledged; no test depends on real timing. | Wall-clock dependence or nondeterminism. |
| 17 | **Technical accuracy (Python/NumPy/SciPy/SymPy)** | Every function, signature, default, and version claim is real and correct; **mentally execute every code block and lab**; NumPy 1.x vs 2.x differences tagged. | Invented API, misused function, wrong version claim. |
| 18 | **Executability** | Code syntactically valid; imports resolve; paths and cross-references resolve; tests pass on reference and fail on a broken variant; every lab has steps, evidence, cleanup; `mlmath` installs editable and `mlmath verify` passes. | Any broken or unrunnable step. |
| 19 | **Repository consistency** | Module names, lesson names/counts (15 folders, 80 lessons, 159 files), project file names (32 in the tree vs 30 in `Roadmap.md` flagged `OPEN`), 4A/4C names, and every relative link match the tree exactly (spaces URL-encoded; em dash preserved). | Wrong name, count, path, or link. |
| 20 | **Pedagogical consistency** | Progression real; nothing used before taught or forward-referenced; no re-teaching of 4A/4B lessons or S3-14/S3-20 tools; 4C topics deferred, not half-taught; running example coherent. | Forward dependency without note; duplication; terminology drift. |
| 21 | **Resource safety** | Caps before heavy work; files confined; no lab can exhaust memory/disk or hang (exhaustive matrix tests are size-capped). | Unbounded work. |
| 22 | **Input validation and security** | No unsafe deserialization or `eval`/`exec`; strict loaders; named oracle registry; notebooks run only from the project directory. | Unsafe example or missing validation. |
| 23 | **Currency** | Version-sensitive claims tagged; Python 3.10 minimum respected; no unmarked claims about current practice. | Stale or untagged claims. |
| 24 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated outputs, misattributed results, invented constants, employer/role claims, cited results presented as proved. | Any unsupported specific. |
| 25 | **Cross-consistency** | The connection map, `plan.json`, triage cases, notebooks, and library functions all agree on names and edges; gate rules identical across Units 1, 2, 4, 5. | Contradiction or orphan. |
| 26 | **Adversarial review** | Re-read as a skeptical staff engineer: "What here is wrong, misleading, over-claimed, or teaches a bad habit (trusting a plot, one seed, a CAS answer, `inv(A)@b`, an unchecked gradient)?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 27 | **Reproducibility** | Labs and project run within 4 CPU / 8 GB / 30 GB and disk caps; no paid service, account, or download beyond the one-time pinned install; seeded, idempotent, `--quick`; cleanup preserves learner data. | Hidden cost, nondeterminism, external dependency. |

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

**Appendix A — Source Register and Claim Register.** (i) A **Source Register** table: `Source ID | Tier (T1–T4) | Full citation (author, title, year/version) | Topics supported | Access (consulted live with URL+date / from knowledge) | [VERIFY] status`. (ii) A **Claim Register**: `ID | Unit | Claim | Source ID(s) or derivation | Confidence (High/Med/Low) | Tag (PROVED/CITED/EVIDENCE ONLY/HEURISTIC/JUDGEMENT/ASSUMPTION)`. At least **100 entries**, covering every library-behaviour claim, formula, derivation, cited result, attribution, and consequential judgement.

**Appendix B — Audit Report** (passes 1–27): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** every `[VERIFY]`/`[VERSION-SENSITIVE]`/`[JUDGEMENT]`/`[ASSUMPTION]` item and every CITED result, grouped by area (NumPy/SciPy/SymPy API and versions; floating point; optimization citations; statistics and experimentation citations; learning-science citations; repository-tree consistency), each with *what to check*, *where (named source)*, and *how to test locally in one command or small script*. The reviewer must be able to close every item in **under 8 hours**.

**Appendix D — Known Limitations and Assumptions:** what is intentionally not covered (4C topics, formal proofs beyond those listed, GPU numerics, production numerics, exam preparation, credentials); assumed versions; no validated link between this stage and any job outcome; subjectivity of ratings and weights; synthetic nature of demonstrations; anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code, oracles, and notebooks and human re-derivation of the mathematics.

**Appendix F — Proof, Status, and Counterexample Index:** every method/tool with status, invariants, proof technique, preconditions, and verification evidence; and a minimal instance for each counterexample: float `==`; naive softmax overflow; `log(0)` in cross-entropy and the clip-vs-epsilon bias difference; catastrophic cancellation; `inv(A) @ b` vs `solve` on an ill-conditioned system; forward vs central difference error; silent broadcasting bug; `ddof` mismatch; mean of means ≠ pooled mean; Simpson/trapezoid rule failure on a non-smooth integrand; greedy hour allocation suboptimal; a "significant" difference that disappears with another seed; correlation without causation (synthetic confounder).

**Appendix G — Executable Verification Bundle:** a standard-library-only `verify_syllabus.py` that extracts every fenced Python block with a `# File: …` first-line comment, writes them to a scratch directory, byte-compiles them, runs the test suite in `--quick` mode with timeouts and a disk cap, and prints a PASS/FAIL list; plus `verify_overview.py` that verifies `objtrace` (exhaustively for ≤ 4 × 4), `plan` (all DAGs on ≤ 5 nodes vs brute force; review-schedule properties; the greedy-vs-DP counterexample), `links` (closure vs brute-force reachability; minimal-set properties; listing consistency on good and bad samples), the 15/80/159 counts and every relative link against a reviewer-supplied `find` listing, every oracle-backed worked example, and the mutation lab and regression guard.

## 12.4 Trust rules

- If a pass finds a problem you cannot fix confidently, **leave it visible** as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it actually was in your environment; say "expected output (representative)".
- Never claim content "was verified against live documentation" unless you consulted it.
- Never present exhaustive or seeded testing as proof; never present a cited finding or formula as proved; never present a gate score as a predictor or credential.
- Never state success rates, hiring statistics, or what any employer requires; never invent quotes or anecdotes; never present opinion as research.
- Attributions must be correct or marked `[VERIFY]`; never invent a citation, DOI, URL, or page number.
- Never advise anything that helps misrepresent skill or cheat; AI use is for explanation and review, disclosed and verified.

# 13. OUTPUT FORMAT

- **One Markdown document**, `SYLLABUS-Overview.md`.
- Start with: title; one-paragraph abstract (**explicitly stating that the module orients, plans, maps, and integrates; teaches no Module 01–14 content; makes no outcome or credential claims; and that every worked example and key is verified two independent ways**); metadata block (`Module: S4B-00`, `Stage: 4B`, `Language: Python`, `Estimated total time [ASSUMPTION]`, `Last reviewed`, `Assumed tool baseline`); a **linked table of contents** to all units and appendices.
- Then Units 1–5 in order, then Appendices A–G.
- `#` for the title, `##` for units, `###`/`####` below; consistent anchors. Tables for comparisons, connection matrices, schedules, rubrics; fenced code with language tags; **mermaid** for diagrams (4A→4B→4C chain, 4B dependency graph, package layout, plan-to-evidence flow); plain-text math with Unicode, no LaTeX.
- Each unit is self-contained but cross-linked (relative links to sibling target files, every Module 01–14 `README.md`, 4A and 4C modules by exact folder name; URL-encode spaces; keep the em dash as in the repository path).
- **Depth target:** Units 1, 2, 5 each ≥ 2,500 words of teaching text excluding code and tables; **Unit 3 ≥ 5,000 words excluding the 80-row matrix and code**; Unit 4 ≥ 1,200 words. **Do not compress to fit**; use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no "see previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 1 |
| 2 | Unit 2 |
| 3 | Unit 3 part A: N.0–N.4 (L1 bridges, L2 matrix for modules 01–07) |
| 4 | Unit 3 part B: L2 matrix for modules 08–14, handoff contracts; L3 (`links` tool, closure proof, "same idea, three costumes") |
| 5 | Unit 3 part C: L4 (≥ 10 triage cases), N.7–N.14 |
| 6 | Unit 4 (Projects README); Unit 5 part A: N.0–N.5, specification, scaffold, library modules 01–07 |
| 7 | Unit 5 part B: library modules 08–14, notebooks, verification and mutation analysis, `mlmath verify`, library card, report template, N.6–N.14, rubric |
| 8 | Appendices A–G, including the completed audit across **all** parts |

Rules:
- End each part with: `PART n/8 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-part audit (passes scoped to that part) **before** printing, and keep a running Source and Claim Register.
- Part 8 runs the **cross-part** audit (passes 2, 12, 19, 20, 25, 26 especially) and may require **correcting earlier parts**: list each as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If near the length limit, stop at a clean boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 8, print: "Concatenate Parts 1–8 in order into `SYLLABUS-Overview.md` and apply all listed corrections."

# 15. QUALITY BAR — DEFINITION OF DONE

Complete only when **all** are true:

- [ ] All 5 units present in order; Units 1, 2, 3, 5 each with L1–L4 and N.0–N.14; Unit 4 with its eight sections; each lesson-sized topic has ≥ 2 worked original examples (≥ 3 in Unit 3), verified two independent ways.
- [ ] Every topic in Sections 6, 8, 9 is taught at its stated level; no Module 01–14 lesson, Stage 3 algorithm, or S3-14/S3-20 tool is re-taught.
- [ ] **Unit 3's matrix covers all 80 lessons** with upstream 4A, downstream 4C and 5x, skill, missing-skill symptom, and a `JUDGEMENT` rating; both handoff contracts present; ≥ 10 triage cases with verifying commands; the four cross-stage derivations are runnable and oracle-checked.
- [ ] Every method and tool has a Method/Tool card, explicit status, runtime-checked preconditions, an independent oracle, exhaustive small-domain tests, seeded and adversarial tests, mutation checks, and deterministic behaviour.
- [ ] Conventions (claims, correctness, numerical, notation, original content, randomness, data/security, integrity, gates) are stated once and applied consistently.
- [ ] **No unsupported claim about learning efficacy, hiring, interviews, role requirements, employers, or real systems.** Every duration is a labelled assumption.
- [ ] **Every non-trivial claim maps to a T1/T2 source or a derivation in the Source Register; no T4-only claim; no invented citation.**
- [ ] `mlmath` (≥ 40 verified functions across all 14 modules, 15 notebooks, tests, mutation lab, `mlmath verify`) installs editable in a fresh `venv` and passes `--quick` within the disk caps; the report template contains no fabricated results.
- [ ] Every required proof is written in full or labelled `CITED [VERIFY]` with a numerical check, stating which.
- [ ] Every counterexample in Appendix F is demonstrated with a minimal instance.
- [ ] Every "verified on all small inputs" statement names its domain and size and is never called proof.
- [ ] Names, counts (15 folders, 80 lessons, 159 files), project file names, 4A/4C names, and relative links match the tree; the 30-vs-32 project-count discrepancy is reported as `OPEN`.
- [ ] Randomness is seeded via `np.random.Generator`; time is injected; data is local, human-readable, validated, atomically written; no `pickle`/`eval`/`exec`; no network at run time.
- [ ] Integrity policy consistent: AI use disclosed and verified; accessibility notes; maths-anxiety awareness non-clinical; gates framed as curriculum convention.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and `--quick`.
- [ ] Appendices A–G present; Claim Register ≥ 100 entries; audit passes 1–27 reported candidly; `verify_syllabus.py` and `verify_overview.py` delivered and consistent with `# File:` comments.
- [ ] A human can close every open item in under 8 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/8**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Model and session:** use a long-context, high-capability model and keep one conversation across all 8 parts so the Source/Claim Registers, conventions, and shared tools stay consistent. Type `continue` between parts.
2. **Human verification is required.** Run `verify_syllabus.py` and `verify_overview.py` (Appendix G) with a `find` listing of the repository; hand-re-derive a sample of worked examples (especially the softmax–cross-entropy gradient, normal equation, and log-sum-exp identity); check every `[VERIFY]` citation against the real source (NumPy/SciPy docs and the cited books/papers); run `mlmath` in a fresh `venv`.
3. **Highest fabrication-risk spots:** library defaults and version claims (NumPy 1.x vs 2.x, `allclose` tolerances, `scipy.special.logsumexp`); the Eckart–Young statement; Adam/optimizer citations; any "time to learn" figure not tagged `[ASSUMPTION]`; any statement about roles or interviews; learning-science citations; lesson-level edges in the connection matrix (they are `JUDGEMENT` hypotheses, not facts).
4. **Design notes:** (a) modelled on `Stage 4A…/00-Prerequisite-Overview/PROMPT-Prerequisite-Overview.md`, but 4B's tree has **no readiness file**, so there are 5 units (not 6) and the entry check is a link plus a 10-item diagnostic inside Unit 1. (b) Unit 3 is weighted heaviest per your emphasis on `how-4b-connects-to-4a-and-4c.md`. (c) The tree has 32 project files while `Roadmap.md` says 30; the prompt makes the model report this as `OPEN` rather than guess. (d) 4B needs NumPy/SciPy/SymPy/Jupyter, unlike 4A's standard-library baseline. (e) An earlier `SYLLABUS-00-Stage-4-Overview.md` (713 lines) was removed in commit `e98b83c`; this prompt does not depend on it and can be retrieved with `git show e98b83c^:"<path>"` if you want to compare.
5. **Final layout:** save the output as `SYLLABUS-Overview.md` here, then split it into `README.md`, `learning-plan.md`, `how-4b-connects-to-4a-and-4c.md`, `Projects/README.md`, and `Projects/01-math-for-ml-notebook-library.md`.
