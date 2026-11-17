# PROMPT — Generate `SYLLABUS-00-Prerequisite-Overview.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have trained, shipped, and monitored models in production, and you have debugged the failures that weak mathematical foundations cause: a percentage change reported as a percentage-point change, a log of a non-positive number, a variance computed with the wrong denominator, an off-by-one between `Σ_{i=1}^{n}` and `range(n)`, a unit mismatch, a float compared with `==`, a quantile computed by two libraries that disagree, a formula in a paper mistranslated into code. You have also mentored engineers who are strong programmers but have not touched mathematics since school. You teach the way you work: **compute exactly, check independently, state your assumptions, and make every statement verifiable.**

You are also a careful technical author. You never invent a function, a signature, a default, a formula, a constant, a version, a statistic, **a claim about how much mathematics any employer, interview, or job requires, a "time to learn" figure presented as fact, or a claim about how any real company or product works**. When unsure, you say so and mark it `[VERIFY]`; practitioner opinion is marked `[JUDGEMENT]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 4A — Basic Mathematics Prerequisite / 00-Prerequisite-Overview/` (module code **S4A-00**, the **Stage 4A orientation, planning, bridging, and readiness module**)

Output file name: **`SYLLABUS-00-Prerequisite-Overview.md`**, to be saved inside that folder.

All code, labs, worked examples, tools, and the project are in **Python**.

It must teach, **one after another, from beginner to advanced**, these 6 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 1 | Stage 4A orientation | `README.md` |
| 2 | Learning plan and pacing | `learning-plan.md` |
| 3 | How Stage 4A connects to Stage 4B and Stage 4C | `how-4a-connects-to-4b-and-4c.md` |
| 4 | Readiness checklist and self-assessment | `readiness-checklist-and-self-assessment.md` |
| 5 | Overview project index | `Projects/README.md` |
| 6 | Overview project: Prerequisite math workbook and readiness check | `Projects/01-prerequisite-math-workbook-and-readiness-check.md` |

Do **not** add, merge, skip, or reorder units. There is **no `practice-questions.md`** in this folder: self-check questions live inside each unit (Section 7), and the large item pool lives inside Unit 4. The Stage-level `../README.md` is **out of scope** (treat it as "defined separately"). **This module does not teach the content of Modules 01–15**; it orients, plans, maps, assesses, and integrates. Link to each lesson; never re-teach it beyond a one-line recall. Do not produce shallow summaries: this is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI Engineer who has finished Stages 0–3. They write working Python (functions, classes, modules, `venv`, `pytest`), use Git and a Linux shell, know Big-O and basic data structures and algorithms, and have seen logarithms, exponents, summations, and some number theory and geometry **inside algorithm contexts** (S3-01, S3-16). They have **not** necessarily studied mathematics as mathematics since school; some have gaps, some have maths anxiety, some are strong and want to skip ahead. **Assume school arithmetic only.** Everything else is taught or linked.
- **Stage position:** Stage 4A comes **after** Stage 3 and **before** Stage 4B (Mathematics for Machine Learning) and Stage 4C (Advanced Mathematics for Machine Learning — Deep Learning), which feed Stages 5A–5D. Where Stage 3 already taught a topic from the algorithm angle (e.g., `gcd`, primes, modular arithmetic, geometry primitives in S3-16; logarithms in S3-01), **link back and state what 4A adds** (the mathematical meaning and the ML connection), without duplicating.
- **Stage structure the syllabus must reflect** (module list, names, lesson counts, and module projects are fixed; verify against the repository tree and report any mismatch as `OPEN`):

| Code | Module (folder name) | Lessons | Module project (file in its `Projects/`) |
|---|---|---|---|
| 01 | `01-Number-Systems-and-Arithmetic-Essentials` | 8 | `01-number-system-explorer-in-python.md` |
| 02 | `02-Fractions-Ratios-and-Percentages` | 10 | `01-percentage-and-ratio-calculator.md` |
| 03 | `03-Algebra-Foundations` | 10 | `01-symbolic-algebra-checker-with-sympy.md` |
| 04 | `04-Equations-Inequalities-and-Systems` | 15 | `01-equation-and-system-solver-toolkit.md` |
| 05 | `05-Exponents-Roots-and-Growth` | 8 | `01-exponential-growth-and-scale-visualizer.md` |
| 06 | `06-Logarithms` | 8 | `01-logarithm-scale-and-log-likelihood-demo.md` |
| 07 | `07-Functions-and-Graphs` | 16 | `01-function-plotter-and-activation-gallery.md` |
| 08 | `08-Geometry-and-Trigonometry` | 7 | `01-trigonometry-and-unit-circle-visualizer.md` |
| 09 | `09-Vectors-as-Arrows-and-Data-Points` | 5 | `01-vector-arrows-and-angle-explorer.md` |
| 10 | `10-Sequences-Series-and-Summation` | 8 | `01-sequence-and-series-explorer.md` |
| 11 | `11-Counting-and-Combinatorics` | 6 | `01-counting-and-combinatorics-calculator.md` |
| 12 | `12-Descriptive-Statistics-Basics` | 7 | `01-descriptive-statistics-from-scratch.md` |
| 13 | `13-Limits-and-Rates-of-Change-Bridge` | 6 | `01-secant-to-tangent-limit-visualizer.md` |
| 14 | `14-Complex-Numbers-Optional` | 3 | `01-complex-plane-visualizer.md` |
| 15 | `15-Mathematical-Notation-Reasoning-and-Math-in-Code` | 8 | `01-formula-to-python-translation-workbook.md` |

  Stage totals to state **as repository facts to be re-verified**: 15 modules, 125 lessons, 192 files. Every module also has `README.md`, `practice-questions.md`, and `Projects/README.md`. Module 14 is **optional**. The overview folder is the only folder with the five files plus `Projects/` listed in Section 2. **Note:** the 15 module projects plus this overview's stage project make 16 projects in total; this overview's project is the **Stage 4A stage project**.
- **Downstream structure to map against** (names exactly as in the repository):
  - **4B:** 01 Vectors, Dot Product and Norms; 02 Matrices and Linear Transformations; 03 Eigenvalues, SVD and Low-Rank Structure; 04 Similarity, Distance and Embedding Geometry; 05 Derivatives and Single-Variable Optimization; 06 Integral Calculus; 07 Multivariable Calculus and Gradients; 08 Optimization Fundamentals; 09 Probability Fundamentals; 10 Common Distributions; 11 Sampling and Limit Theorems; 12 Inferential Statistics for Experiments and Evals; 13 Information Theory for ML; 14 Linear Models Mathematics.
  - **4C:** 01 Advanced Linear Algebra; 02 Multivariable and Matrix Calculus; 03 Optimization Theory and Training Algorithms; 04 Advanced Probability; 05 Statistical Estimation and Bayesian Inference; 06 Advanced Information Theory; 07 Mathematics of Deep Learning Training; 08 Mathematics of Convolutional and Recurrent Models; 09 Mathematics of Transformers and Representations; 10 Mathematics of Generative and Latent-Variable Models.
  - **Stages 5A–5D** (Machine Learning Foundation; Advanced Machine Learning; Deep Learning & Transformers; MLOps) are named as forward targets only.
- **Zero budget.** All work runs on a **local laptop** (WSL2 Ubuntu primary, native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid service, no network, **no scraping, no downloaded problem sets or textbooks, no accounts, no API keys, no real AI or cloud calls**. **Every problem, item, scenario, and dataset is original or synthetic**, and every tool stores data **locally in plain, human-readable files inside a project directory**. **On-disk footprint cap for any lab or project: default ≤ 64 MB, `--quick` ≤ 8 MB.**
- **Tool baseline (required):** **CPython 3.12** `[ASSUMPTION — state minimum 3.10 and note differences]`, `venv`, `pytest`, and the standard library: `fractions.Fraction`, `decimal`, `math`, `cmath` (Module 14 contrast only), `statistics`, `random` (**`random.Random(seed)` instances only**), `itertools`, `functools`, `dataclasses`, `typing`, `enum`, `json`, `csv`, `argparse`, `pathlib`, `tempfile`, `os` (`replace`), `textwrap`, `difflib`, `doctest`, `ast` (**read-only static checks; never `eval`/`exec` of untrusted text**), `platform` (environment capture without PII).
- **Optional helpers (flag as optional):** `sympy` (an **independent symbolic oracle**; Module 03's project uses it), `numpy` (Module 15 translates formulas to NumPy; **never required here**), `matplotlib` (plots only; text/SVG fallback must work), `hypothesis`, `ruff`, `mypy`.
- **Domain flavor:** after Level 1, examples come from what a data/ML engineer meets: reporting accuracy changes, learning-rate schedules, normalizing features, reading a loss formula, comparing two model scores, counting configurations in a hyperparameter grid, converting units, reading a paper's notation. **All original. No claims about any real company, benchmark, or product.**
- **Running example thread:** one scenario, **"the learner's Stage 4A math readiness portfolio"**, evolves through the folder: orient and set up (Unit 1) → build a personal plan (Unit 2) → map what each 4A skill is for downstream (Unit 3) → measure where the learner actually stands, honestly (Unit 4) → organise the evidence (Unit 5) → assemble the workbook, the diagnostic tool, and the readiness report into one package, `mathprep` (Unit 6). Reuse it so the learner sees one artifact grow through every lens.
- **Continuity and links:** link back to **S3-00 (stage overview and toolkit project)**, **S3-01** (logs, exponents, counted work), **S3-08** (graphs, topological order — used in Units 2 and 3), **S3-14** (stress harness and exact oracles — the verification backbone, **reused, not rebuilt**), **S3-16** (math/number theory/geometry), **S3-20** (practice log, error log, spaced-repetition deck, rubric and scorecard, Wilson intervals — **reused, not rebuilt**), and **S3-21** (stage exit conditions). Forward-link to Stage 4A Modules 01–15 (each `README.md` and relevant lessons), to Stage 4B/4C modules by name, and to Stages 5A–5D. State clearly what is **taught here vs. deferred**: this module teaches **orientation and study method for mathematics, planning as a dependency problem, prerequisite-to-ML mapping, assessment design and honest scoring, and integration of verified worked solutions**; **calculus, linear algebra, probability, inference, optimization, proof techniques beyond basic logic, exam preparation, and any credential are named and deferred**; **no outcome guarantees and no employer-specific claims are made**.

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–4 AND UNIT 6)

Each of these units progresses through **exactly these four levels**. Use identical headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the artifact and its purpose, follows the worked example, and applies the basic template to a small case with prompts. |
| **L2** | Intermediate — Working Practice | Applies the activity unaided to their own situation within a timebox, using the templates and tools, and avoids the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | States criteria as checkable properties, justifies decisions with exact computation and independent oracles, quantifies uncertainty, and defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Adapts to unfamiliar learners and gaps, diagnoses failures in others' plans, maps, and assessments, and could coach another engineer through Stage 4A. |

Unit 5 uses the structure in Section 9.

# 5. MANDATORY STRUCTURE FOR UNITS 1–4 AND UNIT 6

Use this exact skeleton, in this order. Do not omit a section; if one is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours, [ASSUMPTION]>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete, verifiable failure this prevents. No hype, no outcome claims.)

### N.1 Learning objectives
(6–10 measurable outcomes, each starting with an action verb: define, compute, map, plan, score, justify, critique…
Tag each with its level L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception.)
(One diagram: e.g., module dependency graph, 4A→4B→4C chain, diagnostic pipeline, plan-to-evidence flow — annotated for a worked example.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what)
- Guided exercise with an original example, exact Python code, expected output, and how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic worked example (complete, runnable Python), continuing the running example
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad practice → why it hurts → corrected version
- Exercise with measurable before/after numbers (checks passed, minutes, items correct)

### N.5 Level 3 — Advanced
- **Method card** (for activities) and **Tool card** (for tools): (1) goal and when to use, (2) inputs and outputs, (3) steps with timeboxes, (4) invariants or acceptance criteria stated as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) **status** (`PROVED`, `CITED` with `[VERIFY]`, `EVIDENCE ONLY` for exhaustive/seeded verification, `HEURISTIC`, `JUDGEMENT`), (8) oracle and test domain for tools
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure, how to avoid fooling yourself)
- Exercise requiring a defended justification, a derivation, or a counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial and unfamiliar situations (a learner with a 10-year gap; a learner who "knows it" but cannot compute; a map that drifts from the repo; a gamed diagnostic)
- Automation (aggregated verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's plan or self-assessment, giving evidence-based feedback
- Edge cases and platform differences (Python 3.10 vs 3.12; CPython vs PyPy; WSL2 vs native)

### N.7 Engineering lens
(Where weak mathematics fails in real ML engineering — verifiable arithmetic failures only; never a company claim. Failure modes and blast radius. Cost, time, and sustainability notes.)

### N.8 Integrity lens
(Measurement and reasoning risks: self-rating bias, test-the-bank memorization, small-sample overreading, cherry-picked scores. Ethics: honest self-representation, AI-assistance disclosure, no cheating, fairness and accessibility. Controls, each verifiable by a command, a test, or a written check.)

### N.9 Checklist
(Checkbox list the learner applies to the artifact. Every item is verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | **expected evidence** | **cleanup** | stretch goal. Idempotent, seeded, local-only, safe to re-run, with a `--quick` mode.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a "why the wrong answers are tempting" note for MCQs. At least one is a coding question with an oracle.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves under this module to prove completion.)

### N.13 Common interview questions
(5 questions about the unit's theme — e.g., "how do you know your self-assessment is trustworthy?" — with senior-level model answers; no claims about what any company asks.)

### N.14 Sources and verification notes
(References by name and section; items tagged [VERIFY]; every CITED claim named; every JUDGEMENT labeled.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated. **Every lesson contains at least two fully worked original examples (at least three in Units 3 and 4), each complete and verified.** **Every tool is taught with a Tool card, ships with tests (including exhaustive small-domain tests), and has deterministic behavior (injected clock and seeds).** **The module never re-teaches a 4A lesson, a Stage 3 algorithm, or an S3-14/S3-20 tool: it names it and links to it.**

**Conventions are stated once and used everywhere:**
- **Claims policy:** **every claim about learning efficacy, study method, "what works", hiring, interviews, or how much mathematics any role needs is exactly one of: (a) cited research tagged `[VERIFY]` with its limits; (b) practitioner opinion tagged `[JUDGEMENT]`; (c) a verifiable statement about mathematics, code, or the repository tree; or (d) omitted.** **No success rates, no outcome guarantees, no statements about what any named company asks, requires, or prefers, no invented quotes or anecdotes, no "N% of ML work uses X".** **All durations (hours per lesson, weeks per module) are `[ASSUMPTION]` planning templates the learner replaces with their own measured values.**
- **Mathematical correctness policy:** **every worked example and every assessment key is verified two independent ways: (1) a hand derivation shown in the text, and (2) an independent exact computation in Python** (`int`, `Fraction`, or `decimal` with stated context; **never float `==`**), with an optional third check (`sympy` or a float with a stated `math.isclose` tolerance). **Domains and conventions are stated before use:** division by zero; logarithm argument `> 0` and base `> 0, ≠ 1`; square roots of negatives (real vs complex); `0⁰` (a convention — `[VERIFY]`; Python returns `1` for `0**0`); rounding mode and number of decimals; units. **Numerical agreement on examples is evidence, not a proof of a general statement; say so.**
- **Index and notation convention:** **mathematical sums and sequences are written 1-based (`Σ_{i=1}^{n}`) and the Python translation is shown 0-based side by side with the off-by-one made explicit**; every symbol is defined at first use; plain-text math with Unicode (`Σ`, `√`, `≈`, `≤`, `∈`) — **avoid LaTeX that may not render**.
- **Original-content policy:** all problems, items, scenarios, and data are original or synthetic; named results (e.g., the Pythagorean theorem, the binomial theorem) are referred to **by name and statement only**, never by reproducing a textbook's wording, examples, or exercise sets; **no downloaded or scraped content**.
- **Assessment-item format (all items in Unit 4 and the workbook in Unit 6):** `ID`, `Module` (01–15), `Lesson link`, `Level` (L1–L4), `Skill tag` (a can-do statement ID from Unit 4), `Stem`, `Answer format` (MCQ-4 / numeric-exact / short-form), `Key` (exact; a `Fraction` string for rationals), `Hand solution`, `Oracle` (**the name of a registered pure Python function — never an expression string evaluated with `eval`**), `Distractor rationale` (**for each MCQ distractor: the specific misconception or slip that produces it, and its value computed by an error-model function, not typed by hand**), `Time estimate`, `Difficulty` (Easy/Medium/Hard defined by explicit criteria: number of steps, concepts combined, trap present), `Parameterization` (optional seeded template), `Tags`.
- **Python numeric-trap policy (taught explicitly, version-tagged where needed):** float representation (`0.1 + 0.2 != 0.3`; `Fraction(0.1)` vs `Fraction("0.1")`; **IEEE 754 — `CITED [VERIFY]`**); `round()` rounds half to even for exact ties and is subject to representation error; `/` vs `//`; floor division and `%` with negatives; `int()` truncates toward zero; `**` with negative exponents returns a float; `math.sqrt(-1)` raises `ValueError` (vs `cmath.sqrt`); `math.log(0)` raises `ValueError`; `statistics.variance`/`stdev` are **sample** (n − 1) and `pvariance`/`pstdev` are **population** (n); **`statistics.quantiles` has a documented `method` parameter and percentile definitions differ across tools**; `math.isclose` defaults (`rel_tol=1e-09`, `abs_tol=0.0`) and why `abs_tol` matters near zero; `sum` of floats vs `math.fsum`; `range` half-open vs closed mathematical intervals; **API availability by version** (`math.comb`/`math.perm`/`math.prod`/`math.isqrt`/`math.dist` and `statistics.fmean`/`statistics.quantiles` need 3.8+; `math.lcm` needs 3.9+; `statistics.correlation` and `statistics.linear_regression` need 3.10+ — `[VERIFY]` each against the "What's New" pages).
- **Data policy:** all data local, human-readable, validated, atomically written (`os.replace`); **no PII, no telemetry, no network**; self-assessment results are the learner's private data and stay on disk locally; loaders reject unknown fields and enforce size caps; never `pickle`/`marshal`/`eval`/`exec`; oracles are looked up **by name in a fixed registry**.
- **Integrity and ethics policy:** the workbook and assessments are **the learner's own work**; **AI assistance is allowed for explanation and review, must be disclosed in the evidence log, and may not produce the graded answers or solutions**; AI-generated solutions, problems, and feedback are **untrusted hypotheses verified with the oracle**; honest self-representation; no cheating in any assessment; fairness and accessibility awareness (extra time, alternative formats, language load); **mathematics anxiety is acknowledged as a real experience (awareness only; `[JUDGEMENT]`, no clinical claims)**.
- **Time and randomness policy:** tools take an injected clock/day number and never read the system clock inside logic (the CLI edge supplies it); every randomized component takes an explicit `random.Random` or seed; **no use of any structure here in a security context**.
- **Result status vocabulary:** **`PROVED`**, **`CITED`**, **`EVIDENCE ONLY`**, **`HEURISTIC`**, **`JUDGEMENT`** (also `[ASSUMPTION]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[VERIFY]` as markers).
- **Stage 4A gate convention (inherits the repository's Stage gates):** **80% or above → proceed; 60–79% → remediate named modules and retake; below 60% → repeat the prerequisite modules.** These thresholds, the per-module floor, and all weights are **`HEURISTIC`/`JUDGEMENT`, not validated**; **no certificate or external credential is implied.**

## Unit 1 — Stage 4A orientation (`README.md`)
- **L1:** **what Stage 4A is and is not**: school-level mathematics rebuilt for ML engineers — number sense, fractions and percentages, algebra, equations, exponents and logarithms, functions, geometry and trigonometry, vectors-as-data, sequences and sums, counting, descriptive statistics, a limits bridge, optional complex numbers, and notation and math-in-code; **not** calculus, linear algebra, probability theory, or inference (named, deferred to 4B/4C); **how the folder is organised** (15 modules, `README.md` + numbered lessons + `practice-questions.md` + `Projects/` in each; this overview folder first); **how to use a lesson** (a four-step loop: read → work the examples by hand → attempt practice → verify with Python; the "hand first, machine second" rule); **three kinds of mathematical skill** (computing, explaining/reasoning, translating to code) and why an ML engineer needs all three; **setting up** (`venv`, `pytest`, the `env_check` tool that reports Python version and which optional libraries are present); **first demo — exact vs approximate**: `0.1 + 0.2` vs `Fraction(1, 10) + Fraction(2, 10)`, and what that teaches; **the reading map** for the whole stage with links to every module `README.md`.
- **L2:** **navigating the tree** (a path map; naming conventions; where practice, projects, and evidence go); **the lesson loop as a timeboxed routine** (a template block of minutes per phase, `[ASSUMPTION]`); **the error log** (reusing the S3-20 error-log idea: slip vs misconception vs gap; one-line entries; weekly review); **the evidence folder** (`stage4a/NN-<module>/` with `notes/`, `practice/`, `project/`, `evidence-log.md`); **spaced review** (a simple expanding-interval schedule generated from a day number, `HEURISTIC`; research on retrieval practice and spacing named as `CITED [VERIFY]` with limits; reuse the S3-20 `Deck`, link only); **when to use a calculator, a CAS, or NumPy** and when not (the "oracle, not crutch" rule); **study habits that fail** (passive re-reading, copying solutions, checking the key first) with detection signals.
- **L3:** **stage objectives as checkable can-do statements**: each objective maps to lessons, at least one assessment item (Unit 4), and a project artifact (Units 5–6) — a traceability table stored as JSON and checked by a tool (`objtrace`: every objective has ≥ 1 lesson link, ≥ 1 item, ≥ 1 artifact; no orphan items; deterministic report; **exhaustively verified over all link sets for ≤ 4 objectives × ≤ 4 items = `2^16` graphs against a brute-force definition of coverage and orphan**); **definition of done for Stage 4A** (a checkable list); **the exact-vs-float policy** (when exactness matters: equality, money-like quantities, counting; when floats are fine: measured data, with tolerances); **what each Python numeric type guarantees** (documented behavior only; `[VERSION-SENSITIVE]` where relevant); **honest scoping** (what this stage will not make you).
- **L4:** **coaching a peer into the stage** (an intake conversation script and a checklist: background, goals, constraints, anxieties); **adapting the orientation** to a learner who is rusty, a learner who is strong, a learner with limited weekly time; **hostile cases** for `objtrace` (duplicate IDs, dangling links, cycles in a dependency field, huge files → all issues listed, none silently ignored); **testing**: golden-report tests, fuzzing malformed JSON, mutation lab (orphan item not flagged; uncovered objective counted as covered; off-by-one in coverage counting) with no surviving mutants; **keeping the orientation current when the tree changes** (a drift check against a directory listing).

## Unit 2 — Learning plan and pacing (`learning-plan.md`)
- **L1:** **what a learning plan is and is not** (a falsifiable schedule you revise, not a promise); **the default path** `01 → 15` with Module 14 optional and **why this order** (each module's prerequisites named from the tree: e.g., 03 before 04; 05 before 06; 07 after 03–06; 09 after 08; 10 before 13; 15 revisited throughout, not only at the end); **a first-week plan** (setup, Unit 4 entry check, Module 01 lessons 1–2); **time estimation basics** (measure your own minutes per lesson over the first week; replace `[ASSUMPTION]` defaults with data); **weekly rhythm template** (study blocks, a review block, a project block, a rest day — `[JUDGEMENT]`, no medical claims).
- **L2:** **three pathways, each a full original plan with milestones**: **Full** (all 125 lessons and all module projects), **Diagnostic-driven fast track** (skip or skim modules where the entry diagnostic shows ≥ the placement threshold, **with a required evidence item per skipped module**: one workbook problem and one practice set), and **Refresher** (Modules 15, 12, 13, 06, 02 first, then gap-fill); **hours-per-week variants** (5/10/15/20, `[ASSUMPTION]`) with calendars; **module gating** (a module is "done" only when its practice set and project meet its checklist); **the `plan.json` format** (modules, lessons, prerequisites, hours, review slots, milestones — a validated schema); **review scheduling** (spiral review: Module N's key skills revisited at the end of N+1 and N+3); **buffers and catch-up weeks**; **how to log planned vs actual** in the evidence log.
- **L3:** **planning as a dependency problem**: the module (and lesson) prerequisite DAG; **topological order and the critical path** (S3-08 recall; link, do not re-teach); **the `plan` tool** (Tool card: validates the DAG (no cycles, no unknown nodes), checks that no module is scheduled before its prerequisites, that weekly hours ≤ budget, that every module has a review slot; computes an order, the critical path length, and slack; **verified exhaustively against brute-force enumeration of all orderings on every DAG with ≤ 5 nodes** — a stated domain, e.g., all DAGs on 4 labelled nodes under a fixed topological labelling, `2^6` edge sets); **allocating a fixed budget of hours across modules by diagnostic gap** (a worked example where **greedy-by-gap-per-hour is suboptimal** against exact DP over small instances — S3-09/S3-11 recall — with a minimal counterexample); **effort estimation and the planning fallacy** (`CITED [VERIFY]` as awareness; buffer policy `JUDGEMENT`); **expanding-interval review schedule** (a function from a completion day to review days, `HEURISTIC`; properties checked: strictly increasing, deterministic); **measuring adherence** (planned vs actual hours, with the caveat that adherence is not learning).
- **L4:** **re-planning after slippage** (re-baseline with explicit trade-offs; protect verification over breadth: fewer lessons fully verified beats more lessons skimmed — `JUDGEMENT`); **compressing for a deadline** (which modules are safest to compress, justified from the Unit 3 dependency map, not from folklore); **overlapping 4A with early Stage 4B work** (a rule: only if the 4B module's prerequisite closure from Unit 3 is already satisfied); **plans for different constraints** (full-time, evenings only, interrupted study, accessibility needs); **hostile inputs for `plan`** (cycles, duplicate nodes, negative hours, enormous files → full issue list); **testing**: exhaustive small-DAG tests, fuzzing, golden schedules, mutation lab (prerequisite violation not flagged; slack off by one; review slot skipped) with no surviving mutants; **peer plan review checklist**; coaching approach ("a plan you cannot check against evidence is a wish").

## Unit 3 — How Stage 4A connects to Stage 4B and Stage 4C (`how-4a-connects-to-4b-and-4c.md`)
- **L1:** **the chain** 4A → 4B → 4C → 5A–5D in one picture (mermaid): what each stage adds; **five headline bridges, each a complete worked numeric example from school mathematics to an ML idea**, all exact and original: **(1) percentage points vs percent change** → comparing two model scores honestly; **(2) logarithms turn products into sums** → why log-likelihood is used; **(3) slope of a line → rate of change → gradient** (named, deferred to 4B-05/4B-07); **(4) vector length and angle** → norms, distance, cosine similarity (4B-01, 4B-04); **(5) mean, variance, standard deviation, z-score** → feature standardization (4B-11/12 forward link). Each example states precisely **what is still missing** that 4B/4C will supply.
- **L2:** **the full connection matrix**: for **every one of the 15 modules** (and for each lesson that is a deliberate bridge — e.g., `04/14-three-variable-systems-and-the-bridge-to-matrices`, `06/08-why-logarithms-matter-in-machine-learning`, `07/14-activation-shapes-sigmoid-tanh-and-relu`, `08/04-degrees-and-radians`, `13/*` as a whole, `15/08-translating-formulas-into-python-and-numpy`): **downstream 4B/4C modules (exact folder names), the specific skill used, the symptom of a missing skill ("you will be unable to …"), and a strength rating (essential / helpful / background — `JUDGEMENT`)**; **what 4A deliberately does not cover and where it is taught** (derivatives 4B-05; integrals 4B-06; matrices 4B-02; probability 4B-09; inference 4B-12; information theory 4B-13); **the handoff contract**: the exit criteria 4A hands to 4B (a checkable list, aligned with Unit 4); **reading the 4B and 4C overviews** (links).
- **L3:** **prerequisite claims as testable hypotheses**: skill-level traceability (a specific 4A skill → a specific later use), stored as JSON; **the `links` tool** (Tool card: loads the connection map; **computes the transitive prerequisite closure** of any 4B/4C module back to 4A lessons; computes the **minimal 4A lesson set** whose closure covers a chosen target; reports "what breaks if lesson X is omitted"; **verified against brute-force reachability on every DAG with ≤ 5 nodes**); **a proof that the closure algorithm is correct** (invariant on the visited set; termination on finite DAGs) written in full; **consistency checks** (every path in the map exists in a directory listing supplied as input; every module name matches the repository tree exactly; no 4A lesson mapped to a non-existent 4B module); **strength ratings are `JUDGEMENT`** — state how a reviewer can challenge one (a concrete test: attempt the downstream lesson's first derivation without the skill); **authoritative cross-references** (the *Mathematics for Machine Learning* book by Deisenroth, Faisal, and Ong and standard calculus/linear-algebra/probability texts as **topic references only, `[VERIFY]`**).
- **L4:** **symptom-to-root-cause triage**: given a stuck point in 4B/4C (e.g., "I cannot follow the log-likelihood derivation"), walk the map back to the 4A lesson(s) responsible — **at least six original triage cases with exact answers**; **learners who can skip** (evidence required, linking to Unit 4's placement rules); **maintaining the map** when 4B/4C change (drift detection against listings; a change log); **hostile inputs for `links`** (dangling edges, cycles, duplicate IDs, 10⁵-node files within caps → full issue lists); **testing**: exhaustive small-DAG tests, golden closures, mutation lab (closure misses a transitive edge; minimal-set returns a non-minimal set; off-by-one in listing check) with no surviving mutants.

## Unit 4 — Readiness checklist and self-assessment (`readiness-checklist-and-self-assessment.md`)
- **L1:** **why measure at all**: confidence is not competence, and a plan built on a wrong self-image fails; **two uses** — **placement** (before Stage 4A: where to start or skip) and **exit** (after: ready for 4B?); **a can-do checklist** (what it is, how to read a line, how to claim an item: only by doing a task unaided); **a first mini check of 10 original items** done by hand and then scored by a short script; **the three outcomes** (proceed / remediate / repeat) and **what a score does and does not mean** (it is not a credential and not a predictor of any job or interview outcome); **honest first steps** when the result is low (it is information, not a verdict).
- **L2:** **the full readiness checklist**: **≥ 5 can-do statements per module (≥ 75 total; Module 14 flagged optional)**, each with ID, level, linked lesson(s), a **"prove it" task** (a question answerable unaided in a stated time), and a link to the practice set; **the diagnostic blueprint**: **Component A** (auto-scored knowledge items, ≥ 150 in the pool, ≥ 10 per module), **Component B** (≥ 12 short free-response and math-in-code tasks with tests), **Component C** (calibration: a confidence rating per item), **Component D** (≥ 8 explanation prompts with a rubric); **two forms**: a **20-minute quick check** and a **90-minute full diagnostic**, `[ASSUMPTION]`; **scoring and gates**: module scores, a stage score, the 80/60 gate rules, **a per-module floor** (`HEURISTIC`), and the placement thresholds for the fast track; **remediation mapping** (a failed item → the lesson(s) and practice questions to revisit); **parallel forms** (the same blueprint with different numbers, seeded) for the exit retake; **pre/post comparison** with the cautions that a retake is not independent of the first sitting and that low early scores tend to rise on retest regardless (regression to the mean, `CITED [VERIFY]`).
- **L3:** **assessment rigor**: **(a) blueprint weights** (`HEURISTIC`: weights from lesson counts adjusted for downstream criticality, with the largest-remainder rounding written out and checked exhaustively for small totals); **(b) score uncertainty**: **Wilson interval for a module score of `k` correct out of `n` items** (formula stated, `CITED [VERIFY]`, with a learner-side exact-coverage check for small `n`) — worked example: **6/8 and 5/8 are not distinguishable at n = 8**, so a gate that treats them differently is over-reading; a **decision rule using the interval** (`HEURISTIC`); **(c) the random guesser**: expected score `n/k` and variance `n·(1/k)(1 − 1/k)` on `n` items with `k` options, derived in full, and a **guessing-aware pass mark** (the probability a pure guesser passes, computed exactly with `math.comb`); **(d) calibration**: the **Brier score** `(1/N)·Σ (f_i − o_i)²` — definition, properties (`CITED [VERIFY]`), and a worked example of an over-confident profile; **(e) item analysis on labeled synthetic response data only** (difficulty = proportion correct; discrimination = correlation of item with rest score; internal consistency via **KR-20/Cronbach's alpha, `CITED [VERIFY]` with limits**; no real population exists, so **no validity claim is made**); **(f) distractor design**: each distractor generated by an **error-model function** for a documented misconception (adding fractions straight across; treating a percent increase and decrease as cancelling; `log(a + b) = log a + log b`; `(a + b)² = a² + b²`; dividing by `n` instead of `n − 1` or the reverse; degrees entered where radians are required; off-by-one in a sum's upper limit) — **exactly one key; no distractor equals the key; no two options equal**; **(g) compensatory scoring masks a weak module** — a minimal counterexample (a 90% stage score with one module at 40%) and the per-module floor as a remedy; **(h) fairness review**: language load, unfamiliar contexts, calculator policy stated per item, accessibility notes.
- **L4:** **building the instruments**: **the `diag` tool** (Tool card: strict pool loader; blueprint sampler with seeded determinism and exact inclusion constraints; administration with an injected clock; scoring, Wilson intervals, calibration, gate advisor with an explicit **"what this cannot tell you"** section; **parallel-form generator** from ≥ 20 parameterized templates with exact `Fraction` keys; Markdown report) and **the `pool-verify` tool** (checks every key against its registered oracle on the item's stated domain and on seeded parameters; audits distractors against their error models; flags duplicate options, ambiguous keys, missing hand solutions, unknown fields); **diagnosing a response pattern** (an error-pattern classifier: which misconception does a wrong answer imply? — with the limit that one wrong answer can have several causes); **simple two-stage routing** (a short screener decides which module sets to administer; `HEURISTIC`, no validity claim); **anti-gaming** (rotating parameterized items, withholding keys until after a sitting, never reusing a sitting's items for the retake); **hostile inputs** (malformed pools, duplicate IDs, an oracle name not in the registry, a key not matching its oracle, answer strings that are not exact → full issue lists); **testing**: exact enumeration of the guesser distribution against `math.comb`; Wilson interval against exact enumeration on small `n`; the sampler's constraints exhaustively on tiny pools; the gate advisor's soundness; **mutation lab** (key off by one; distractor equals key; gate boundary `≥` vs `>`; wrong denominator in Brier; interval clipped wrongly) with no surviving mutants; **regression guard**; documentation.
- **Item pool (delivered inside this unit, as a clearly labeled section):** **≥ 150 original items, ≥ 10 per module for all 15 modules** (Module 14 flagged optional), with a **machine-readable key** (JSONL block per module), a hand solution, an oracle name, and distractor rationales for MCQs; plus **≥ 12 free-response/math-in-code tasks with pytest tests**, **≥ 8 explanation prompts with rubrics**, and **≥ 20 parameterized templates**. **Every item tests only content taught in the linked 4A lesson** (Pass 24/25 will check this).

# 7. SELF-CHECK AND PRACTICE REQUIREMENTS (REPLACES A STANDALONE PRACTICE FILE)

There is **no `practice-questions.md`** in this folder. Instead:
- Each of Units 1–4 and 6 contains **N.11 Self-check questions (6–10, each with a model answer and common wrong answers)** and N.10 labs.
- **Unit 4 carries the ≥ 150-item pool** described above (this is the module's large practice bank).
- Each Unit's N.11 includes **at least 2 mathematical items with exact answers verified by an oracle**, **2 scenario/critique items** (an original plan, map, or score report to critique), and **1 coding question** with a brute-force or exact-arithmetic oracle.
- Provide a scoring rubric for each unit's self-check with the 80/60 gate rule (curriculum convention; `HEURISTIC`).

# 8. UNIT 6 — OVERVIEW PROJECT: PREREQUISITE MATH WORKBOOK AND READINESS CHECK (REQUIREMENTS)

**Target file:** `Projects/01-prerequisite-math-workbook-and-readiness-check.md`. This is the **Stage 4A stage project**. Apply the four levels and sections N.0–N.14. **It integrates tools taught in Units 1–4 into one local Python package, `mathprep`**, and adds two new artifacts. It teaches **no new mathematics**.

**Project components (all required):**
1. **The math workbook (`wb`).** **≥ 60 original worked solutions across all 15 modules (≥ 4 per module; ≥ 2 for Module 14)**, each stored as a strict-schema plain-text record: problem, **hand solution steps**, **independent exact verification** (a registered oracle function), a **common-error note**, and an **ML connection** (linked to Unit 3's map). The `wb` tool validates schemas and **runs every check**, producing a deterministic report (`status`, `check`, `report`). **Includes the numeric-trap set**: at least 10 solutions demonstrating the Python traps in Section 6 (float equality, `round` ties, floor division with negatives, sample vs population variance, `statistics.quantiles` methods, `abs_tol` near zero, 1-based vs 0-based sums, and others).
2. **The readiness check (`diag`).** The Unit 4 tool, integrated; includes a **built-in, original 60-item quick-check set** drawn from the pool (≥ 4 per module), the 20-minute and 90-minute forms, scoring with intervals, calibration, gates, and remediation mapping to lesson links.
3. **The plan (`plan`) and the map (`links`).** The Unit 2 and Unit 3 tools, integrated; the project ships an original `plan.json` for the Full pathway and a `connections.json` for all 15 modules, both validated by their tools.
4. **Math-in-code conformance suite.** **≥ 20 formulas translated into Python with tests**, each with the 1-based/0-based mapping shown, domain checks that raise `ValueError` with a stable message format, and an independent exact oracle: percent change and percentage points; weighted average; compound growth; quadratic formula with discriminant (**with a demonstration of cancellation error and an exact `Fraction` oracle**); distance and unit vector; angle between vectors via the dot product; arithmetic and geometric partial sums; `n choose k` vs `math.comb`; sample vs population variance; z-score; and similar.
5. **Verification and mutation analysis.** Exhaustive small-domain tests; seeded random tests; adversarial inputs; **mutation lab** (planted off-by-one, wrong denominator, `>` vs `≥`, wrong tolerance) with **no surviving mutants**; **regression guard**; a **single command `mathprep verify`** that runs everything with `--quick` support and disk caps.
6. **The readiness report template.** A Markdown template the learner fills with **their own real results**: entry diagnostic with intervals, chosen pathway, plan, evidence-log excerpts, exit diagnostic with a **pre/post comparison and its caveats**, a gap list, and a signed integrity statement (AI use disclosed). **The syllabus ships the blank template and clearly labeled `[ILLUSTRATIVE]` synthetic example data — never fabricated "results".**
7. **Packaging.** `pyproject.toml` (local editable install only), a package layout diagram (mermaid), a `Makefile`-style command list, a reproducibility contract tested in a fresh `venv`.

**Project rubric (provide in full):** requirements traceability; correctness (oracle agreement); coverage of all 15 modules; numeric-trap handling; assessment-tool soundness; honesty of the report (uncertainty stated, no overclaiming); documentation; integrity statement. **Pass conditions** use the 80/60 gate (curriculum convention). **Stretch goals:** a text-mode or SVG plot of module scores with intervals; a peer review of someone else's plan; a Hypothesis-based property suite (optional).

# 9. UNIT 5 — PROJECTS README (REQUIREMENTS)

**Target file:** `Projects/README.md`. Unit 5 does **not** use the full N.0–N.14 skeleton; it uses this structure (each section substantial, original, and linked):
1. **What the Stage 4A projects are** and how they fit the stage (the 15 module projects feed the stage project as evidence; Module 15's `01-formula-to-python-translation-workbook.md` overlaps most with the Unit 6 conformance suite, so state how they differ).
2. **Index of all 16 projects** (15 module projects + the stage project) as a table: module | project | one-line purpose | key skill demonstrated | verification method | links (relative paths with the exact repo folder and file names from Section 3).
3. **How to choose and sequence projects** (by pathway from Unit 2; which can be skipped on the fast track and the evidence required).
4. **Project rules** (original data only; seeds; `--quick`; disk caps; no network; AI disclosure; honest results).
5. **Definition of done** common to all 4A projects (a checkable list) and **the evidence folder structure**.
6. **How the module projects feed the Unit 6 workbook** (which project supplies which workbook problems; no duplication).
7. **A review checklist** for the learner's own and a peer's project.
8. **Promises vs delivery:** Unit 5 may promise nothing that Unit 6 or the module folders do not deliver (Pass 4 will check this).
Include **3 original self-check questions** and links to every module's `Projects/README.md`.

# 10. UNIT 1 README — NOTE

Unit 1 (`README.md`) is a full Level 1–4 unit (Section 6), not a mere landing page. Its first screen (the first ~30 lines of the eventual file) must still work as a landing page: purpose, who it is for, folder map, how to start, and links to Units 2–6's files.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: src/mathprep/plan.py`).
2. **Every command and snippet is paired with expected output** (representative, labeled "example — yours will differ in timings, dates, and file paths") and a short interpretation.
3. **Code must run.** Python 3.10+ syntax only (state if 3.12 is required). Standard library unless marked optional. Type hints on all public functions. Clarity over cleverness. Every public tool states its **purpose, inputs/outputs, preconditions (with runtime checks), result status, and mutation contract** (**no mutation of caller inputs**).
4. **Every method and tool carries its Method card or Tool card** (Section 5, N.5) before the code.
5. **Conventions are stated once and applied everywhere** (Section 6). Mixing conventions is a defect.
6. **Exactness first.** Rational arithmetic with `Fraction`; floats only with a stated tolerance and a stated reason; no `==` on floats; rounding mode and decimals stated; units attached to every quantity in word problems.
7. **Every worked example, item, and tool ships with an independent oracle and tests** — exhaustive over a stated small domain, seeded random, and adversarial/edge inputs; tests pass on the reference code and fail on a deliberately broken variant. **Oracles are independent of the code under test (a different method, a spec-literal brute force, or exact arithmetic; never importing the function under test) and are labeled.**
8. **No unproven claims about learning, hiring, interviews, or real systems** (Section 6 claims policy). **Cited-only results** (Wilson interval, KR-20/Cronbach's alpha, Brier score properties, regression to the mean, planning fallacy, retrieval practice and spacing research, IEEE 754 behavior, API-availability-by-version statements) are **named and tagged `[VERIFY]`**, never presented as proved unless a full proof is in the text.
9. **Proof status is explicit** in every card and in Appendix F; **exhaustive or seeded testing never upgrades a status to `PROVED`**; weights, thresholds, floors, routing rules, and pacing templates are `HEURISTIC`/`JUDGEMENT`/`ASSUMPTION`.
10. **Proofs are written in full** where required (closure/topological-order correctness; random-guesser mean and variance; largest-remainder rounding properties; the "greedy suboptimal" counterexamples; the identity checks used in workbook solutions). **A counterexample is a disproof; numerical agreement is not a proof.**
11. **Do not teach CPython details as guarantees.** Separate documented behavior from implementation detail, tagged `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** every tool validates sizes before heavy work; exhaustive oracles have caps enforced in code; files are confined to the project directory; no tool loops unboundedly.
13. **Security, privacy, and input validation:** no `pickle`/`marshal`/`eval`/`exec`; JSON/CSV loaders validate shape, types, sizes, and reject unknown fields; oracles looked up by name in a fixed registry; `ast` read-only; no network; no PII; atomic writes.
14. **No secrets, no network access, no paid APIs, no downloaded content** in any lab. Original or synthetic data only, seeded, with size caps. `clean` targets list what they remove; no deletion outside the project directory; **the learner's own evidence log and results are never deleted unless explicitly requested.**
15. **Every lab ends with cleanup** and a verification that no stray files remain beyond those documented.
16. **Tag Python-version and implementation differences** (3.10 vs 3.12; CPython vs PyPy) `[VERSION-SENSITIVE]`.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every claim on **authoritative sources**: the official Python documentation (Library Reference pages for `fractions`, `decimal`, `math`, `cmath`, `statistics`, `random`, `itertools`, `dataclasses`, `json`, `csv`, `argparse`, `pathlib`, `tempfile`, `os.replace`, `ast`, `doctest`, `platform`; the Tutorial's "Floating Point Arithmetic: Issues and Limitations"; the "What's New" pages for version-sensitive behavior) and standard references cited **by title and topic, not page numbers you cannot confirm**: Pólya, *How to Solve It*; Graham, Knuth, and Patashnik, *Concrete Mathematics* (sums, binomials; by topic); Deisenroth, Faisal, and Ong, *Mathematics for Machine Learning* (downstream map; by topic); Goldberg (1991) on floating point; the IEEE 754 standard (by name); Wilson (1927) and Brown, Cai, and DasGupta (2001) for intervals; Brier (1950); Kuder and Richardson (1937) and Cronbach (1951) for reliability; Kahneman and Tversky on the planning fallacy; Roediger and Karpicke (2006) and Cepeda et al. (2006) on retrieval practice and spacing; Sweller on worked examples and cognitive load; Kruger and Dunning (1999) on miscalibrated self-assessment **with the replication and interpretation debates noted, `[VERIFY]`**; standard texts on classical test theory (by topic); the Stage 3 and Stage 4A/4B/4C repository modules themselves for all technique and topic content. **All of these are `[VERIFY]`** — you are writing from knowledge, not consulting them live. **Do not reproduce or paraphrase at length any copyrighted material.** Provide a URL only if certain it is canonical; otherwise cite by name and mark `[VERIFY]`.
- **Do not fabricate:** version numbers, timings, **success rates, hiring statistics, statements about how much mathematics a job or interview needs or what any company asks, "N% of ML practitioners…", time-to-learn figures as facts**, constants and formulas from memory without a derivation or `[VERIFY]`, CPython internals presented as guarantees, quotes, or anecdotes. If you need a number, derive it from a stated command or label it `[ASSUMPTION]` or `[ILLUSTRATIVE]`.
- **Mark uncertainty** with: `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[ASSUMPTION]`, `[JUDGEMENT]`.
- Keep a running **Claim Register** (Section 12.3) for every non-trivial claim.
- **Treat the repository tree as the source of truth** for module names, lesson names and counts, and file paths. Where this prompt and the tree could disagree, the tree wins and the discrepancy is reported as `OPEN`.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 6 units present, in order, with every required section (Sections 5–10), every unit-specific topic (Section 6), levels L1–L4, the required worked examples per lesson, the ≥ 150-item pool, the free-response tasks, and the ≥ 60-problem workbook. | Any missing section/topic/example/item. |
| 2 | **Convention-consistency audit** | Claims policy, mathematical-correctness policy, index/notation convention, original-content policy, item format, numeric-trap policy, data/privacy policy, integrity policy, gate convention, and naming are stated once and applied identically in every unit, tool, item, and test. | Any mixed or silently changed convention. |
| 3 | **Claims-honesty audit** | Every claim about learning, study method, hiring, interviews, or mathematical requirements of roles is cited and tagged `[VERIFY]` with limits, an explicit `[JUDGEMENT]`/`[ASSUMPTION]`, a verifiable statement, or absent; no success rates; no employer claims; all durations are `[ASSUMPTION]`. | Unsupported claim of efficacy, outcome, or requirement. |
| 4 | **Requirements-traceability audit** | Every stage objective has ≥ 1 lesson link, item, and artifact; every item maps to a can-do statement; Unit 5 promises nothing Unit 6 and the module folders do not deliver; Project components map to units. | Unverified objective, orphan item, or promise without delivery. |
| 5 | **Mathematical-correctness audit** | **Re-derive every definition, formula, worked example, and key by hand, independently of the draft**; check domains, signs, rounding, units, and the 1-based/0-based mapping; check every identity used. | Any wrong value, sign, domain, or definition. |
| 6 | **Item-key and distractor audit** | Every key equals its oracle on the stated domain and on seeded parameters; every distractor equals its error-model output; **exactly one correct option; no duplicate options; no distractor equal to the key**; every item answerable from the linked lesson alone. | Ambiguous key, duplicate options, key-oracle mismatch, out-of-scope item. |
| 7 | **Tool-card audit** | Every tool (`env_check`, `objtrace`, `plan`, `links`, `diag`, `pool-verify`, `wb`, `mathprep verify`) has a complete card consistent with its code and tests. | Missing or inconsistent card element. |
| 8 | **Proof and derivation audit** | Every proof or derivation is complete and re-derived independently: closure/topological-order correctness, random-guesser mean and variance, largest-remainder properties, the greedy-suboptimality counterexamples, trace-coverage definitions. | Any missing, circular, or invalid step. |
| 9 | **Cited-results audit** | Every cited-only result (Wilson interval, KR-20/alpha, Brier properties, regression to the mean, planning fallacy, retrieval-practice and spacing research, IEEE 754, API-by-version statements) is labeled as cited, tagged `[VERIFY]`, listed in Appendix C with a learner-side check where possible, and never presented as proved. | Cited result presented as proved or untagged. |
| 10 | **Statistical and psychometric validity audit** | Statements about a learner's score carry `n` and an interval; item-analysis and reliability statements appear only on labeled synthetic data; cut scores and weights are labeled judgements; regression-to-the-mean and small-sample cautions present; no validity or predictive claims. | Missing uncertainty, overclaim, or causal leap. |
| 11 | **Exhaustive-domain and oracle audit** | Every "verified on all small inputs" statement names its domain and size (e.g., `2^16` link sets; all DAGs on ≤ 5 nodes; all `(n, k)` guesser distributions up to `n = 12`); domains are feasible; oracles are independent, labeled, and size-capped; evidence is never called proof. | Overclaim, infeasible domain, or shared-logic oracle. |
| 12 | **Originality and IP audit** | All problems, items, scenarios, and data are original or synthetic; no copied statements, examples, or exercise sets; named results referred to by name and statement only. | Copied or closely paraphrased external content. |
| 13 | **Integrity, ethics, and fairness audit** | No cheating guidance; AI-assistance policy present and applied to every graded artifact; assessments not framed as a credential or predictor; accessibility and fairness notes present; maths-anxiety awareness stays non-clinical. | Cheating-adjacent advice, missing disclosure policy, or credential/predictor framing. |
| 14 | **Privacy and data-handling audit** | All data local, human-readable, validated, atomically written; no PII; environment capture excludes hostnames/usernames; no network; no telemetry. | PII collection, hidden network use, or unsafe storage. |
| 15 | **Time, clock, and determinism audit** | Injected clocks/day numbers; no system-clock reads in logic; seeded randomness; deterministic tie-breaks and outputs; no test depends on real timing. | Wall-clock dependence or nondeterminism. |
| 16 | **Technical accuracy (Python)** | Every function, signature, and behavior is real and correct (`fractions`, `decimal`, `math`, `cmath`, `statistics` incl. `variance` vs `pvariance` and `quantiles` methods, `round` tie behavior, `//` and `%` with negatives, `math.isclose` defaults, version availability). Mentally execute every code block and lab. | Any invented function, misused API, or wrong version claim. |
| 17 | **Executability** | Code blocks are syntactically valid; imports resolve; file paths and cross-references resolve; every test passes on the reference code and fails on a deliberately broken variant; every lab has steps, expected evidence, and cleanup; `mathprep` installs editable and `mathprep verify` passes. | Any broken, ambiguous, or unrunnable step. |
| 18 | **Repository-consistency audit** | Module names, lesson names, lesson counts (15/125/192), module-project file names, and every relative link match the repository tree exactly; Module 15's project (`01-formula-to-python-translation-workbook.md`) is listed; Module 14 is marked optional; 4B/4C module names match exactly. | Wrong name, count, path, or link. |
| 19 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept (can-do statement, blueprint, closure, Wilson interval, Brier score, error model) used before taught or explicitly forward-referenced; **the module re-teaches no 4A lesson, no Stage 3 algorithm, and no S3-14/S3-20 tool (links only)**; calculus, linear algebra, probability, inference, and optimization are deferred, not half-taught; the running example evolves coherently. | Forward dependency without a note; duplicated content; terminology drift. |
| 20 | **Resource-safety audit** | Every tool and oracle has caps before heavy work; files confined; no lab can exhaust memory/disk or hang. | Unbounded work/allocation. |
| 21 | **Input-validation and security audit** | No unsafe deserialization or `eval`/`exec`; strict loaders reject unknown fields; oracles looked up by name only; `ast` read-only; no network. | Unsafe example or missing validation. |
| 22 | **Currency** | Version-sensitive claims tagged; 3.10 minimum respected or differences noted; no claims about current practice without `[VERIFY]`/`[JUDGEMENT]`. | Stale, untagged, or over-general claims. |
| 23 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated outputs, misattributed results, invented constants, invented claims about employers or roles, and cited-only results presented as proved. | Any unsupported specific. |
| 24 | **Cross-consistency** | The item pool, workbook, and conformance suite test only taught content; every project deliverable maps to a unit and an objective; the pool covers all 15 modules in proportion to the blueprint; gate rules, thresholds, and floors are identical across Units 2, 4, 5, 6 and match the repository's Stage gate convention. | Orphan item, orphan deliverable, or contradiction. |
| 25 | **Adversarial review** | Re-read as a skeptical staff engineer and as a hostile reviewer: "What here is wrong, misleading, over-claimed, or would teach a bad habit (memorizing the bank, trusting a self-rating, over-reading a score, treating the CAS as a crutch)?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 26 | **Reproducibility** | Labs and projects run within the 4 CPU / 8 GB / 30 GB baseline and the stated disk caps, need no paid service, network, account, or download, are seeded and idempotent, have a `--quick` mode, and clean up without deleting the learner's own data. | Hidden cost, unseeded nondeterminism, external dependency, or deleted user state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendices)

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag (PROVED/CITED/EVIDENCE ONLY/HEURISTIC/JUDGEMENT/ASSUMPTION)`. Include at least **90 entries**, covering every standard-library behavior claim, every formula and derivation, every cited result, every attribution, and every judgement and assumption of consequence.

**Appendix B — Audit Report** (table for passes 1–26): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** all `[VERIFY]` / `[VERSION-SENSITIVE]` / `[JUDGEMENT]` / `[ASSUMPTION]` items and every `CITED` result grouped by area (Python documentation and version availability; floating-point behavior; interval and reliability formulas; calibration scoring; learning-science citations; repository-tree consistency), each with: *what to check*, *where to check (named source)*, *how to test it locally with one command or small script (preferably an exact enumeration or a `Fraction` recomputation)*. The reviewer must be able to close every item in **under 8 hours**.

**Appendix D — Known Limitations and Assumptions:** what the module intentionally does not cover (calculus, linear algebra, probability, inference, optimization, formal proof technique, exam preparation, credentials), assumed Python version, **the absence of any validated link between diagnostic scores and later success in 4B/4C or any job**, the small-`n` limits of a 10-item module score, the subjectivity of weights and floors, the synthetic nature of all psychometric demonstrations, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code, the oracles, the item pool, and the workbook, and re-derivation of the mathematics.

**Appendix F — Proof, Status, and Counterexample Index:** every method, tool, and technique with its status, acceptance criteria/invariants, proof technique, preconditions, and verification evidence (oracle domain, seeds, tolerances), and every counterexample with its minimal instance: float equality (`0.1 + 0.2`); percent change vs percentage points; mean of means ≠ overall mean for unequal sizes; `round` ties and representation error; floor division and `%` with negatives; 1-based sum vs `range`; sample vs population variance; percentile definitions that disagree; greedy gap-per-hour allocation suboptimal; compensatory score masking a weak module; `6/8` vs `5/8` indistinguishable at `n = 8`; regression-to-the-mean illusion on a retest; a pure guesser passing a short test with computed probability.

**Appendix G — Executable Verification Bundle:** a `verify_syllabus.py` script (standard library only) that extracts every fenced Python block with a `# File: …` first-line comment, writes them to a scratch directory, byte-compiles them (`py_compile`), runs the test suite in `--quick` mode with timeouts and a disk cap, and prints a PASS/FAIL list; plus a `verify_prereq.py` that: verifies `objtrace` (exhaustively over all link sets for ≤ 4 × 4), `plan` (all DAGs on ≤ 5 nodes vs brute-force orderings; review-schedule properties; the greedy-vs-DP counterexample), `links` (closure vs brute-force reachability; minimal-set properties; the listing-consistency checker on good and bad samples); verifies `diag` and `pool-verify` (every pool item's key vs its oracle on the stated domain and seeded parameters; every distractor vs its error model; the guesser distribution against exact `math.comb` enumeration for `n ≤ 12`; Wilson against exact coverage for small `n`; the sampler's constraints; the largest-remainder allocator exhaustively for small totals; parallel-form determinism and key correctness; the gate advisor's soundness; planted bad pools being caught); verifies every workbook record's check and the conformance suite against exact oracles; verifies that **all repository paths and module/lesson counts cited in the file match a directory listing supplied by the reviewer** (`find` output as input); and runs the mutation lab and regression guard.

## 12.4 Trust rules
- If an audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it actually was in your environment. Use "expected output (representative)" instead.
- Never state that content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.
- **Never present exhaustive or seeded testing as proof for all inputs; never present a diagnostic score as a predictor of success or as a credential; never present a cited finding or formula as proved.**
- **Never state success rates, hiring statistics, what any employer requires, or invent quotes or anecdotes; never present practitioner opinion as research.**
- Statements about **CPython internals** are implementation details: state only what the documentation says, tag `[VERSION-SENSITIVE]`, and prefer teaching the learner to **test the behavior** over asserting it.
- Attributions of results to people or papers must be correct or marked `[VERIFY]`; never invent a citation. Never state a formula from memory without proving it in the text or tagging it `[VERIFY]` with the learner-side check named in Appendix C.
- **Never provide advice that helps misrepresent skill or cheat in an assessment.** AI use is for explanation and review, disclosed, and verified; graded answers and solutions are the learner's own.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-00-Prerequisite-Overview.md`.
- Start with: title, one-paragraph abstract (**including the explicit statements that the module orients, plans, maps, assesses, and integrates; teaches no Module 01–15 content; makes no outcome or credential claims; and that every worked example and key is verified two independent ways**), metadata block (`Module: S4A-00`, `Stage: 4A`, `Language: Python`, `Estimated total time [ASSUMPTION]`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 1–6 in order, then Appendices A–G.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons, connection matrices, blueprints, schedules, and rubrics; fenced code blocks for all code; **mermaid** for diagrams (module dependency graph, 4A→4B→4C chain, diagnostic pipeline, package layout, plan-to-evidence flow); plain-text math with Unicode, no LaTeX.
- Each unit is **self-contained but cross-linked** (relative links to sibling target files, to every Module 01–15 `README.md`, to the S3 modules above, and to 4B/4C modules by exact folder name; URL-encode spaces and keep the em dash as in the repository path).
- **Depth target:** Units 1–4 each ≥ 2,500 words of teaching text excluding code, items, and tables; Unit 4 additionally carries the full item pool; Unit 5 ≥ 1,200 words; Unit 6 complete with all code. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 1 |
| 2 | Unit 2 |
| 3 | Unit 3 |
| 4 | Unit 4 part A: N.0–N.8, can-do checklist for all 15 modules, blueprint, scoring and gate rules, the `diag` and `pool-verify` tools |
| 5 | Unit 4 part B: item pool, Modules 01–08 (with JSONL keys, hand solutions, oracles, distractor rationales) |
| 6 | Unit 4 part C: item pool, Modules 09–15; free-response/math-in-code tasks; explanation prompts; parameterized templates; N.9–N.14 |
| 7 | Unit 5 (Projects README); Unit 6 part A: N.0–N.8, specification, scaffold, `wb`, workbook solutions 1–30 |
| 8 | Unit 6 part B: workbook solutions 31–60+, conformance suite, integration, verification and mutation analysis, report template, N.9–N.14, rubric |
| 9 | Appendices A–G (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/9 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–26, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 9 must run the **cross-part** audit (passes 2, 18, 19, 24, 25 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you approach the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 9, print the final assembly instruction: "Concatenate Parts 1–9 in order into `SYLLABUS-00-Prerequisite-Overview.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 6 units present in the specified order; Units 1–4 and 6 each with levels L1–L4 and sections N.0–N.14; Unit 5 with its eight required sections; each lesson has ≥ 2 fully worked original examples (≥ 3 in Units 3 and 4), verified two independent ways.
- [ ] Every unit-specific topic in Sections 6, 8, and 9 is taught at its stated level; the module re-teaches no Module 01–15 lesson, no Stage 3 algorithm, and no S3-14/S3-20 tool.
- [ ] Every method and tool has a complete **Method/Tool card**, an explicit **status**, stated preconditions with runtime checks, an independent oracle, exhaustive small-domain tests, seeded/adversarial tests, mutation sanity checks, and deterministic behavior (injected clocks and seeds).
- [ ] Conventions (claims, mathematical correctness, index/notation, original content, item format, numeric traps, data/privacy, integrity, gates) are stated once and applied consistently everywhere.
- [ ] **No unsupported claim about learning efficacy, hiring, interviews, how much mathematics any role needs, employers, or real systems appears anywhere.** No success rates, no invented quotes or anecdotes; every duration is a labeled assumption.
- [ ] The **≥ 150-item pool** (≥ 10 per module, Module 14 flagged optional) has machine-readable keys, hand solutions, registered oracles, and error-model distractors, all machine-checked by `pool-verify`; **≥ 12 free-response/math-in-code tasks**, **≥ 8 explanation prompts**, and **≥ 20 parameterized templates** are verified.
- [ ] The **≥ 60-problem workbook** covers all 15 modules (≥ 4 each; ≥ 2 for Module 14), includes the ≥ 10-item numeric-trap set, and every record verifies against an independent exact oracle.
- [ ] The **≥ 20-formula conformance suite** has explicit 1-based/0-based mappings, domain checks with stable error messages, and exact oracles.
- [ ] Every required proof or derivation is written in full, or cited-only results are labeled and tagged `[VERIFY]` (closure and order correctness; random-guesser mean and variance; largest-remainder properties; Wilson interval; Brier score; KR-20/alpha).
- [ ] These counterexamples are each demonstrated with a minimal instance: float equality; percent vs percentage points; mean of means; `round` ties; floor division with negatives; 1-based sum vs `range`; sample vs population variance; disagreeing percentile definitions; greedy allocation suboptimality; compensatory scoring masking a weak module; `6/8` vs `5/8` at `n = 8`; regression-to-the-mean illusion; a guesser passing a short test.
- [ ] Every cited-only result is tagged `[VERIFY]` with a learner-side check where one exists; **no diagnostic score is presented as a predictor or credential**; nothing is asserted about CPython internals.
- [ ] Every "verified on all small inputs" statement names its domain and size and is never described as a proof; oracles are labeled, independent, and size-capped.
- [ ] Module names, lesson names and counts (15 modules, 125 lessons, 192 files), module-project file names, 4B/4C module names, and all relative links match the repository tree; Module 15's project is listed and Module 14's optional status is stated.
- [ ] `mathprep` (with `wb`, `diag`, `pool-verify`, `plan`, `links`, `objtrace`, `env_check`) installs editable in a fresh `venv` and `mathprep verify` passes in `--quick` mode within the disk caps; the report template contains **no fabricated results**.
- [ ] All time-dependent logic uses injected clocks; randomized components take injected RNGs or seeds; tools are deterministic.
- [ ] All data is local, human-readable, validated, and atomically written; no PII; no `pickle`/`eval`/`exec`; oracles looked up by name; no network, accounts, or scraping.
- [ ] The integrity and ethics policy is present and consistent: no cheating guidance, AI use disclosed and verified, fairness and accessibility notes, maths-anxiety awareness non-clinical, gates framed as curriculum convention rather than a credential.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and a `--quick` mode.
- [ ] Appendices A–G present; Claim Register ≥ 90 entries; audit passes 1–26 reported candidly; `verify_syllabus.py` and `verify_prereq.py` delivered and consistent with the file-path comments in the code.
- [ ] A human can verify every open item in under 8 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/9**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 9 parts so the Claim Register, the conventions, the running example, and the shared tools stay consistent. If a part truncates, type `continue` and it resumes at the stated section boundary.
2. **Do the human verification yourself.** Run `verify_syllabus.py` and `verify_prereq.py` (Appendix G), re-derive by hand a sample of worked solutions and item keys from each module (the model's self-audit is not a substitute), re-derive the random-guesser mean/variance and the Wilson interval for small `n`, read the item pool for originality, ambiguity, and out-of-scope content, run `mathprep` in a fresh virtual environment, supply a `find` listing of the repository so the path/count checks run, and close each `[VERIFY]` item against the cited sources.
3. **Spot-check fabrication risk areas first:** any statement about how much mathematics ML roles or interviews require; any "time to learn" figure not marked `[ASSUMPTION]`; the learning-science citations (retrieval practice, spacing, planning fallacy, Kruger–Dunning); Python API version-availability statements (`math.lcm` 3.9, `statistics.correlation` 3.10, etc.); `statistics.quantiles` method behavior; `round` tie behavior; and any item key that was not checked against its oracle.
4. **Scope notes:** (a) the Stage-level `../README.md` is intentionally excluded (it is not in the unit list); generate it with a separate prompt or add it as a Unit 0. (b) **The five files in `00-Prerequisite-Overview/` and the `Projects/` files are currently empty** in the repository, so this prompt was designed from the repository tree, `Roadmap_ptree.md`, and the sibling Stage 3 prompts rather than from existing content. (c) This module **orients, plans, maps, assesses, and integrates**; it teaches none of Modules 01–15. (d) Module 15's project (`01-formula-to-python-translation-workbook.md`) overlaps with the Unit 6 conformance suite; the prompt asks the author to state how they differ. (e) The requested output name `SYLLABUS-00-Prerequisite-Overview/` was taken as the file `SYLLABUS-00-Prerequisite-Overview.md` (no trailing slash).
5. **Final file layout:** save the LLM output as `SYLLABUS-00-Prerequisite-Overview.md` in this folder. Later, split it into the six target files (`README.md`, `learning-plan.md`, `how-4a-connects-to-4b-and-4c.md`, `readiness-checklist-and-self-assessment.md`, `Projects/README.md`, `Projects/01-prerequisite-math-workbook-and-readiness-check.md`) and place the item pool, workbook records, and `mathprep` source under the corresponding directories.
6. **Size note:** the **≥ 150-item pool** (Unit 4) and the **≥ 60-problem workbook** (Unit 6) each need full verification artifacts. If output is too long, continue at the stated part boundaries (pool Modules 01–08 / 09–15; workbook 1–30 / 31–60+) rather than shortening them.
