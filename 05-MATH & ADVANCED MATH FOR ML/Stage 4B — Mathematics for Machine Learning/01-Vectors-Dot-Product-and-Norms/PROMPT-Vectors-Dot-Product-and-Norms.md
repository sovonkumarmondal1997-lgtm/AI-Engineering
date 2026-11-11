# PROMPT — Generate `SYLLABUS-Vectors-Dot-Product-and-Norms.md` (Stage 4B, module S4B-01)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is very large, so use the **Delivery Protocol** (Section 14): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Vectors-Dot-Product-and-Norms.md` in `Stage 4B — Mathematics for Machine Learning/01-Vectors-Dot-Product-and-Norms/`.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have shipped retrieval, ranking, and deep-learning systems and debugged the failures that weak vector fundamentals cause: an embedding index searched with raw dot products when the vectors were not normalised; cosine similarity computed on a zero vector; a `(n,)` array silently broadcast against `(n, 1)` into an `n × n` matrix; a "copy" that was a view and corrupted the training data; an L2 norm that overflowed in float16; a feature matrix whose columns were linearly dependent so the solver returned garbage; an attention score whose scale grew with dimension. You teach the way you work: **derive by hand, verify independently by computation, state shapes, dtypes, conventions, and tolerances, and make every statement checkable.**

You are also a careful technical author. You never invent a function, signature, default, formula, constant, version, statistic, citation, **claim about how much mathematics any employer, interview, or role requires, "time to learn" figure presented as fact, benchmark or speed figure, or claim about how any real model, library internals, or product works**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion is marked `[JUDGEMENT]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 4B — Mathematics for Machine Learning / 01-Vectors-Dot-Product-and-Norms/` (module code **S4B-01**, the first mathematical module of Stage 4B and the entry to the linear-algebra spine).

Output file name: **`SYLLABUS-Vectors-Dot-Product-and-Norms.md`**, saved inside that folder.

Teach, **one after another, from beginner to advanced**, these 10 units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the repository tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | Vectors in n dimensions and NumPy arrays | `01-vectors-in-n-dimensions-and-numpy-arrays.md` |
| 2 | The dot product and its geometric meaning | `02-dot-product-and-its-geometric-meaning.md` |
| 3 | Projection onto a vector | `03-projection-onto-a-vector.md` |
| 4 | Norms (L1, L2, L∞) and distance | `04-norms-l1-l2-and-infinity-and-distance.md` |
| 5 | Linear combinations, span, and linear independence | `05-linear-combinations-span-and-linear-independence.md` |
| 6 | Practice questions | `practice-questions.md` |
| 7 | Projects index | `Projects/README.md` |
| 8 | Project: Vector operations library in NumPy | `Projects/01-vector-operations-library-in-numpy.md` |
| 9 | Project: Geometry of the dot product explorer | `Projects/02-geometry-of-dot-product-explorer.md` |

Do **not** add, merge, skip, or reorder units. Do not teach matrices (Module 02), eigenvalues/SVD (Module 03), cosine-similarity systems and the curse of dimensionality in depth (Module 04), or derivatives/gradients (Modules 05, 07): **name, link, and give a one-line preview only.** This is the **teaching content itself**, not an outline.

**Repository tree for this module (verify; report any mismatch as `OPEN`):**

```text
01-Vectors-Dot-Product-and-Norms/
├── Projects/
│   ├── 01-vector-operations-library-in-numpy.md
│   ├── 02-geometry-of-dot-product-explorer.md
│   └── README.md
├── 01-vectors-in-n-dimensions-and-numpy-arrays.md
├── 02-dot-product-and-its-geometric-meaning.md
├── 03-projection-onto-a-vector.md
├── 04-norms-l1-l2-and-infinity-and-distance.md
├── 05-linear-combinations-span-and-linear-independence.md
├── README.md
└── practice-questions.md
```

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–3 and Stage 4A. They write working Python, use `venv` and `pytest`, and know Big-O. From 4A they have **already met**: vectors as arrows and as lists of numbers, vector addition/subtraction/scaling in 2D/3D, vector length and unit vectors, the algebraic dot product used in length identities, direction/angle/perpendicularity *intuition*, linear combinations *as a term*, and a point-vs-vector type discipline. **This module does not re-teach those**; it states in one line what 4A covered, links to the exact 4A lesson, and then **generalises to n dimensions, adds the geometric dot product and its proofs, projection, other norms, span and independence, and does all of it in NumPy with engineering discipline.** Where 4A defined an angle by picture in 2D/3D, this module **defines** the angle in n dimensions via the dot product and proves the Cauchy–Schwarz inequality that makes the definition valid; state this definition-vs-theorem distinction explicitly.
- **Stage position:** 4A-09 (`09-Vectors-as-Arrows-and-Data-Points`) → **4B-01 (this module)** → 4B-02 (`02-Matrices-and-Linear-Transformations`), 4B-04 (`04-Similarity-Distance-and-Embedding-Geometry`), 4B-08 (`08-Optimization-Fundamentals`), 4B-14 (`14-Linear-Models-Mathematics`) → 4C-01 (`01-Advanced-Linear-Algebra`), 4C-09 (`09-Mathematics-of-Transformers-and-Representations`) → Stages 5A–5D. Link to the Stage 4B overview folder (`00-Stage-4-Overview`) and to its connection file `how-4b-connects-to-4a-and-4c.md`; read the lesson names of 4A-09, 4A-08, 4A-06 and 4A-13 from the repository tree and **use only names that exist**.
- **Zero budget.** Local laptop (WSL2 Ubuntu primary; native Linux/macOS secondary), ~4 CPU cores, 8 GB RAM, 30 GB disk. **No GPU, no paid service, no accounts, no API keys, no network at run time, no scraping, no downloaded datasets or embeddings.** **Every problem, scenario, and dataset is original or synthetic** (seeded generators); toy "embeddings" are generated, never copied from a real model. One-time pinned `pip install` is the only permitted network use. **Disk footprint cap for any lab or project: default ≤ 64 MB, `--quick` ≤ 8 MB.**
- **Tool baseline:** **CPython 3.12** `[ASSUMPTION; minimum 3.10]`, `venv`, `pytest`, **`numpy`** (required; pin a version and tag NumPy 1.x vs 2.x differences `[VERSION-SENSITIVE]`), **`sympy`** and **`fractions`** (exact oracles), **`scipy`** (an independent oracle only: `scipy.spatial.distance`, `scipy.linalg`), **`matplotlib`** (plots; a text/ASCII/SVG fallback must work). Optional: `hypothesis`, `ruff`, `mypy`. All version numbers `[VERIFY]` against PyPI/release notes.
- **Domain flavour (all original; no real-company, real-model, or real-dataset claims):** feature vectors for tabular samples, toy word/item embeddings, logits and scores, a linear layer as dot products, "which toy document is nearest the query", removing a component (a "direction") from embeddings, detecting redundant features. Dimensions such as `d = 768` appear only as `[ILLUSTRATIVE]` sizes for memory and cost arithmetic, never as claims about a model.
- **Running example thread:** **"the learner's `vecnp` library"** evolves through the module: arrays and shapes (Unit 1) → dot product and angle (Unit 2) → projection and component removal (Unit 3) → norms and distances (Unit 4) → rank and independence tests (Unit 5) → practice and integration (Unit 6) → packaged, tested, and explored (Units 8–9). Reuse it so the learner sees one artifact grow.
- **Continuity and links:** back to Stage 4A modules named above, S3-14 (stress harness/oracles), S3-20 (practice log, error log, spaced-repetition deck — **reuse, never rebuild**); forward to the 4B/4C modules above by exact folder name. State **taught here vs deferred**.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 0–5, 8, 9)

Each of these units progresses through **exactly four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the idea and its picture, follows worked examples, computes small cases by hand and in NumPy. |
| **L2** | Intermediate — Working Practice | Applies it unaided in NumPy to realistic ML cases, handles shapes/dtypes/axes correctly, avoids the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | Proves the key results, states precise conditions, quantifies numerical error, verifies with independent oracles, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in unfamiliar code and data, handles edge/degenerate/high-dimensional/float-limit cases, builds and mutation-tests tools, coaches others. |

Units 6 and 7 use the structures in Sections 7 and 9.

# 5. MANDATORY STRUCTURE FOR UNITS 0–5, 8, 9

Use this exact skeleton. If a section is genuinely not applicable, write one sentence saying why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours, [ASSUMPTION]>  |  **Prerequisites:** <list with links>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete, verifiable failure this prevents. No hype, no outcome claims.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4 and given an ID `S4B01.U<N>.O<k>`.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid diagram, annotated for a worked example.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what), with a picture (matplotlib/SVG with ASCII fallback) where geometric
- At least 3 fully worked original examples (hand derivation + independent computation + expected output)
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic worked ML example (complete, runnable, shapes annotated), continuing the running example
- At least 3 further worked examples
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad practice → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- **Proofs written in full** (listed per unit in Section 6), each stating its hypotheses; counterexamples where a hypothesis is dropped
- Method card / Tool card: (1) goal and when to use, (2) inputs/outputs with shapes and dtypes, (3) steps, (4) invariants/acceptance criteria as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Numerical analysis: error sources, tolerances with justification, float32 vs float64 comparison
- Exercise requiring a defended proof, derivation, or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Degenerate and adversarial inputs (zero vectors, NaN/Inf, empty arrays, huge magnitudes, near-parallel vectors, ill-conditioned sets, dtype surprises)
- Automation: aggregate verification commands, property tests, regression guards
- Coaching: reviewing a peer's code/derivation with evidence-based feedback
- Platform and version differences (Python 3.10 vs 3.12; NumPy 1.x vs 2.x; BLAS threads; float32 vs float64)

### N.7 Engineering lens
(Where the idea fails in real ML systems — verifiable numerical/shape failures only, never a company claim. Failure modes, blast radius, memory and compute cost arithmetic, vectorisation vs loops measured locally with stated variance.)

### N.8 Integrity lens
(Reasoning/measurement risks: trusting a plot, one seed, a library call as the oracle, memorised formulas without proof. AI-assistance disclosure. Controls verifiable by a command, test, or written check.)

### N.9 Checklist
(Checkbox list; every item verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, seeded, local-only, safe to re-run, with `--quick`.)

### N.11 Self-check questions
(6–10 questions with concise keys and a "why the wrong answers are tempting" note for MCQs; ≥ 2 mathematical with oracle-verified keys, ≥ 2 scenario/critique, ≥ 1 coding with an oracle.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview questions
(5 questions on the unit's theme with senior-level model answers; no claims about what any company asks.)

### N.14 Sources and verification notes
(References by name and section; every CITED claim named; every JUDGEMENT labelled; [VERIFY] items listed.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

These topics are the **minimum**; add depth, never remove. **Conventions below are stated once and applied identically everywhere.**

## Conventions

- **Claims policy.** Every claim about learning efficacy, study method, hiring, interviews, performance, library internals, or role requirements is exactly one of: (a) cited research/documentation tagged `[VERIFY]` with limits; (b) practitioner opinion tagged `[JUDGEMENT]`; (c) a verifiable statement about mathematics, code, or the tree; or (d) omitted. **No success rates, no employer claims, no invented quotes or anecdotes, no benchmark/speed/accuracy figures as facts.** All durations and illustrative sizes are `[ASSUMPTION]`/`[ILLUSTRATIVE]`.
- **Mathematical correctness policy.** Every worked example and key is verified **two independent ways**: (1) a hand derivation in the text, and (2) an independent computation — exact (`int`/`Fraction`/`sympy`) wherever possible, otherwise NumPy/SciPy with a **stated tolerance and reason** (never float `==`). **NumPy is the thing being taught, so NumPy results are never the sole oracle for a NumPy-based claim**: the oracle is exact arithmetic, a pure-Python reference, SymPy, or SciPy via a different code path. Numerical agreement on examples is evidence, not a proof of a general statement; say so.
- **Notation, shape, and index convention.** A vector `x ∈ ℝⁿ` is a **column** by default in mathematics and a **1-D array of shape `(n,)`** in NumPy; a data matrix `X` has shape `(n_samples, n_features)` with rows as samples; **every array in every example carries a shape annotation** (`# x: (n,)`); mathematical indices are **1-based**, Python **0-based**, shown side by side with the off-by-one explicit; `axis` names the dimension that is **collapsed**; the dot product is `u·v = uᵀv = Σᵢ uᵢvᵢ`; the angle `θ ∈ [0, π]`; `‖·‖₂` is the Euclidean norm; plain-text math with Unicode, **no LaTeX**.
- **Zero-vector and degenerate policy.** `cos θ`, normalisation, and projection onto the zero vector are **undefined**; every tool **raises `ValueError` with a stable message** (format `E-<TOOL>-<NNN>: <text>`) or returns a documented sentinel — chosen once and stated. Tiny-norm handling uses a stated threshold (`HEURISTIC`).
- **Numerical policy.** float32 vs float64 and `np.finfo`; `np.isclose`/`np.allclose` defaults (`rtol=1e-05`, `atol=1e-08`) and why `atol` matters near zero `[VERIFY]`; overflow-safe norms (scaling by `max|xᵢ|`); `float16` hazards; summation order and `math.fsum`; clipping the cosine to `[-1, 1]` before `arccos` (with the reason); `matrix_rank` tolerance `[VERIFY]`; determinism via `np.random.default_rng(seed)` only (never the legacy global state).
- **Original-content policy.** All problems, scenarios, data original/synthetic. Named results (the Cauchy–Schwarz inequality, the triangle inequality, the law of cosines, the Pythagorean theorem, norm equivalence, the Steinitz exchange/dimension theorem if mentioned) by **name and your own statement only**; never reproduce a textbook's wording, figures, or exercise sets.
- **Item format (all practice items and self-checks):** `ID`, `Lesson`, `Level` (L1–L4), `Can-do ID`, `Stem`, `Answer format` (MCQ-4 / numeric-exact / numeric-tolerance / short-proof / code), `Key`, `Hand solution`, `Oracle` (**the name of a registered pure Python function in a fixed registry — never an `eval`ed string**), `Distractor rationale` (**each MCQ distractor generated by an error-model function for a named misconception, not typed by hand; exactly one key; no distractor equals the key; no duplicate options**), `Time estimate [ASSUMPTION]`, `Difficulty` (Easy/Medium/Hard by explicit criteria: steps, concepts combined, trap present), `Tags`.
- **Data/security policy.** All data local, human-readable, validated, written atomically (`os.replace`); no PII, no telemetry, no network; never `pickle`/`marshal`/`eval`/`exec` on untrusted text; `np.load(..., allow_pickle=False)` where `.npy` is used; strict loaders reject unknown fields and enforce size caps.
- **Integrity policy.** Graded answers are the learner's own; AI assistance allowed for explanation/review, **disclosed in the evidence log**; AI-produced derivations or code are **untrusted hypotheses verified against an oracle**; accessibility (text fallbacks for every plot); maths anxiety acknowledged as real (awareness only, `[JUDGEMENT]`, no clinical claims).
- **Status vocabulary:** `PROVED`, `CITED`, `EVIDENCE ONLY`, `HEURISTIC`, `JUDGEMENT` (markers: `[ASSUMPTION]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[VERIFY]`). **Exhaustive or seeded testing never upgrades a status to `PROVED`.**
- **Gate convention (inherits the repository's):** ≥ 80% proceed; 60–79% remediate named lessons and retake; < 60% repeat the module; thresholds are `HEURISTIC`/`JUDGEMENT`; no credential implied.

## Unit 0 — Module orientation (`README.md`)

- **L1:** what S4B-01 is and is not; **what 4A already gave you (one line each, with links) vs what this module adds**; the lesson map with one-line purposes and links to all five lessons, practice, and both projects; how to use a lesson (read → derive by hand → implement in NumPy → verify against an exact oracle → explain aloud); "hand first, machine second"; **why vectors are the atom of ML** (a sample, an embedding, a gradient, a set of weights, a logit vector are all vectors — original illustrations only); environment setup (`venv`, pinned installs, `env_check` printing Python/NumPy/SciPy/SymPy versions and `float32/float64` epsilon, no hostname/username); a first demo: `(n,)` vs `(n, 1)` broadcasting surprise.
- **L2:** the lesson dependency graph (1 → 2 → 3; 2 → 4 (norm from dot product); 1, 2, 4 → 5; 3 → 5 for orthogonal bases) stated and justified; recommended order and pacing template (`[ASSUMPTION]`; link to the stage `learning-plan.md`); **the module can-do checklist** (≥ 5 per lesson, ≥ 25 total, IDs `S4B01.L<k>.C<j>`, each with a "prove it" task and practice link); the evidence folder layout (`stage4b/01-vectors/notes|notebooks|practice|project|evidence-log.md`); the error log (reuse S3-20; link only); spaced review (reuse the S3-20 deck).
- **L3:** module objectives as checkable statements with a traceability table (objective → lesson → practice items → project component); **definition of done**; **the definition-vs-theorem table** (what is a definition and what is a theorem in n dimensions: norm from dot product; angle from Cauchy–Schwarz; orthogonality; independence); **the shape/axis cheat-sheet** with executable examples; the exact-vs-float policy for the module.
- **L4:** coaching a peer through the module (intake questions; common misconceptions by lesson); adapting pacing for rusty/strong/time-limited learners; **drift check** (a script comparing the file list to a supplied directory listing); common failure patterns (normalising a zero vector, `np.dot` on mismatched shapes silently succeeding in a 2-D case, comparing unscaled features by distance, testing orthogonality with `==`) with detection signals.

## Unit 1 — Vectors in n dimensions and NumPy arrays

- **L1:** a vector in ℝⁿ as an ordered list of n reals; **the same object as data point, feature vector, embedding, weight vector, gradient, logit vector** (the meaning comes from context and naming, not the container); vector addition, subtraction, scalar multiplication componentwise (recall 4A-09, generalise to n); **NumPy basics**: `np.array`, `dtype`, `shape`, `ndim`, `size`, `itemsize`, `nbytes`; **`(n,)` vs `(n, 1)` vs `(1, n)`**; indexing, slicing, boolean masks; elementwise `+ - * /` vs the dot product; `np.zeros/ones/arange/linspace`; reading shapes and dtypes aloud; why vectorisation beats a Python loop (explained; speed claims measured locally, never asserted as facts).
- **L2:** **views vs copies** (slicing creates a view; `.copy()`; in-place ops and aliasing bugs, demonstrated with `np.shares_memory`/`np.may_share_memory`); **broadcasting rules** stated precisely and the classic silent-bug `(n,) + (n, 1) → (n, n)`; `axis` and reductions (`sum`, `mean`, `max`, `argmax`, `keepdims`); **batches of vectors** `(B, n)` and `(n_samples, n_features)`; centring and standardising a feature matrix (column-wise vs row-wise; link 4A-12); dtypes (`int`/`float32`/`float64`), **integer overflow and silent upcasting**, `float32` precision limits; memory arithmetic for `[ILLUSTRATIVE]` sizes (`n_vectors × d × itemsize`); contiguous layout and strides (awareness); `np.linalg.norm`, `np.dot`, `@`, `np.einsum` named, used only for shapes here; **reading vector code in a paper/repo** (a short method).
- **L3:** **proofs, written in full:** (a) ℝⁿ with componentwise operations satisfies the vector-space laws (list them; prove from the laws of ℝ); (b) uniqueness of the zero vector and of additive inverses; (c) the broadcasting result shape rule as a stated algorithm, with a small exhaustive check over shapes of rank ≤ 3 and dims ≤ 3 against a pure-Python reference implementation (`EVIDENCE ONLY`); (d) a counterexample showing floating-point addition is **not associative** (`(a+b)+c ≠ a+(b+c)`), with a minimal instance, and what that means for vector sums and reductions (`math.fsum`, pairwise summation awareness `CITED [VERIFY]`); **method card: shape-contract validation** (preconditions checked at runtime, stable errors, no mutation of inputs); **tool card for the `vecnp.core` module** (constructors with validation; NaN/Inf policy; dtype policy).
- **L4:** hostile inputs (ragged lists, object arrays, NaN/Inf, empty vectors, 0-d arrays, `bool` arrays, huge `n` within caps, non-contiguous inputs); **NumPy 1.x vs 2.x differences relevant here `[VERSION-SENSITIVE]`**; thread/BLAS nondeterminism awareness; **diagnosing a silently broadcast bug and a view-aliasing bug** from symptoms (≥ 2 original case studies, each with a fix and a regression test); a **mutation lab** (wrong axis, missing `keepdims`, in-place mutation of the argument) with no surviving mutants.

## Unit 2 — The dot product and its geometric meaning

- **L1 (new relative to 4A):** the dot product `u·v = Σ uᵢvᵢ` in n dimensions (recall the 2D/3D algebraic form from 4A-09 and link it); **the geometric form `u·v = ‖u‖‖v‖cos θ`** with pictures; **sign tells the angle class** (positive: acute; zero: orthogonal; negative: obtuse); orthogonality as `u·v = 0`; the dot product of a vector with itself `u·u = ‖u‖²`; computing in NumPy (`np.dot`, `@`, `np.inner`, `np.sum(u*v)`) and why the shapes must match; **a linear layer's pre-activation `w·x + b` as the first ML use**; **scores as dot products with a weight vector**; ≥ 3 worked examples including a hand angle in 2D and a 4-D case.
- **L2:** properties (commutative, distributive over addition, `(cu)·v = c(u·v)`; **not associative — `(u·v)·w` is meaningless**); **batched dot products** `(B, n)·(n,)` and `(B, n)` row-wise with `np.einsum('bn,bn->b')` / `(A*B).sum(axis=1)`; the angle `θ = arccos(u·v / (‖u‖‖v‖))` with **clipping to [-1, 1]** and the float failure it prevents; comparing a query to a collection by dot product; **dot product vs cosine similarity** (the role of magnitude; preview Module 04, link); **toy attention-style scores** `q·k` and the **`1/√d` scaling argument derived under a stated assumption (independent zero-mean unit-variance components → variance of `q·k` is `d`)**, labelled as a derivation under assumptions, not a claim about any real model; random vectors in high dimension are nearly orthogonal (an **experiment with seeds, sample sizes, and a Monte Carlo error estimate**; link to 04-03); dot product as a **similarity score, a projection coefficient, a weighted sum, and a measure of alignment** — four readings of one formula.
- **L3:** **proofs, written in full:** (a) algebraic properties; (b) **the law of cosines ⇒ `u·v = ‖u‖‖v‖cos θ`** in 2D (and why this is a theorem in 2D/3D but the **definition** of angle in n > 3); (c) **the Cauchy–Schwarz inequality `|u·v| ≤ ‖u‖‖v‖`** with the equality case (full proof, e.g., via the discriminant of `‖u − t v‖² ≥ 0` or via projection — state which); (d) **the triangle inequality** for `‖·‖₂` from Cauchy–Schwarz; (e) `u·v = ½(‖u‖² + ‖v‖² − ‖u − v‖²)` (polarisation) ; (f) **orthogonal vectors satisfy the Pythagorean identity `‖u+v‖² = ‖u‖² + ‖v‖²`**, and the converse; **numerical analysis**: error of a float32 dot product vs float64 vs exact `Fraction` on adversarial inputs (large cancelling terms); `math.fsum` oracle; **tool card for `vecnp.dot`** (batched dot, angle, cosine with clip and zero policy).
- **L4:** degenerate cases (zero vector, near-parallel vectors where `arccos` is ill-conditioned — derive why `arccos` loses accuracy near ±1 and give a more stable alternative `θ = atan2(‖r‖, u·v)` where `r = u − proj_v u` is the component of `u` orthogonal to `v` and `‖r‖ = ‖u‖ sin θ`; prove it from Units 2–3 and verify with a `Fraction`/high-precision oracle); **float16/float32 pitfalls**; **bilinear forms preview** (`xᵀAy`, link to Module 02); case studies (a retrieval index returning the "longest" vector because magnitudes were not normalised; scale drift of scores with dimension) as **original synthetic reproductions with fixes and regression tests**; mutation lab (missing clip, `arccos` argument not normalised, wrong axis in batched dot, `>` vs `≥` in the orthogonality test) with no surviving mutants.

## Unit 3 — Projection onto a vector

- **L1:** the idea (the shadow of `u` on the line through `v`); **scalar projection** `comp_v u = (u·v)/‖v‖` and **vector projection** `proj_v u = ((u·v)/(v·v)) v`; the **orthogonal decomposition `u = proj_v u + (u − proj_v u)`** with the residual orthogonal to `v`; when `v` is a **unit vector** the formula simplifies to `(u·v̂)v̂`; zero-vector undefined; ≥ 3 hand examples (2D, 3D, 5-D) and NumPy implementations with shape annotations.
- **L2:** **removing a component** (subtract the projection: "remove a direction" from every row of an `(N, d)` array — vectorised, shapes annotated, verified orthogonal afterwards); **centring a feature as removing the projection onto the all-ones direction** (link 4A-12 mean); **residuals and the idea of "the part explained by a direction"**; **1-D least squares as a projection**: the best coefficient `β = (x·y)/(x·x)` for `y ≈ βx` (derived by projection; **forward-link to `14-Linear-Models-Mathematics` and `4C-01`**); projecting onto several **orthogonal** directions sums the projections (statement; proof in L3); a **toy "bias direction removal" lab on synthetic embeddings** with before/after cosine measurements, seeds, and honest limits (it removes one linear direction, nothing more — no fairness claims); the projection **matrix** `P = vvᵀ/(vᵀv)` as a **preview only** (rank 1, symmetric, idempotent — stated, verified numerically, deferred to Module 02/4C-01).
- **L3:** **proofs, written in full:** (a) the projection formula from the requirement that the residual is orthogonal to `v`; (b) **uniqueness of the decomposition**; (c) **best-approximation property**: `proj_v u` is the closest point on the line `{t v}` to `u` (`‖u − tv‖²` minimised at `t = (u·v)/(v·v)`; both by calculus-free completion of the square and by Pythagoras); (d) `‖proj_v u‖ ≤ ‖u‖` with equality iff `u ∥ v`, and `‖u‖² = ‖proj_v u‖² + ‖u − proj_v u‖²`; (e) idempotence `proj_v(proj_v u) = proj_v u`; (f) linearity in `u`; (g) projections onto orthogonal vectors add; (h) the 1-D least-squares coefficient equals the projection coefficient; **numerical analysis**: loss of orthogonality after removing a component in float32 and how re-projection helps (`HEURISTIC`, measured); **tool card for `vecnp.project`**.
- **L4:** **a first Gram–Schmidt step by hand** (preview; the full procedure is `4C-01`); near-zero `v` and the threshold policy; projecting onto a nearly-null direction; **repeated component removal and order dependence when directions are not orthogonal** (a minimal counterexample showing that removing directions one at a time is not the same as removing their span unless they are orthogonal); hostile inputs; mutation lab (denominator `u·u` instead of `v·v`; missing residual check; wrong shape for batched projection) with no surviving mutants; case study: a "debiasing" step that silently reintroduced the removed component after an unrelated renormalisation (original synthetic reproduction).

## Unit 4 — Norms (L1, L2, L∞) and distance

- **L1:** what a norm measures (size/length of a vector); **L2 `‖x‖₂ = √(Σ xᵢ²)`** (recall 4A-09 length; now n-D), **L1 `‖x‖₁ = Σ|xᵢ|`**, **L∞ `‖x‖∞ = maxᵢ|xᵢ|`**, with unit-ball pictures in 2D; **distance `d(x, y) = ‖x − y‖`** and the three distances (Euclidean, Manhattan, Chebyshev) on the same pair of points, worked by hand and in NumPy (`np.linalg.norm(x, ord=…)` — **`[VERIFY]` the `ord` semantics for vectors**; `scipy.spatial.distance` as an independent oracle); `ord=0` is **not** a norm (pseudo-"count of non-zeros"; why); ≥ 3 worked examples.
- **L2:** **choosing a norm**: L2 (smooth, rotation-invariant), L1 (robust to coordinate-wise outliers, induces sparsity — **intuition only; the regularisation maths is `14-Linear-Models-Mathematics` lesson 05**), L∞ (worst-case error); **norms in ML practice**: weight-norm penalties (named, deferred), **gradient clipping by global L2 norm** (a worked, original NumPy example), **L2-normalising embeddings** so dot = cosine (link Module 04), **nearest-neighbour search under different norms** on a synthetic set with different answers, **feature scaling changes distances** (a worked example where an unscaled feature dominates, fixed by standardisation); the **`Lp` family** `(Σ|xᵢ|ᵖ)^{1/p}` for `p ≥ 1`, limit `p → ∞`; **`p < 1` is not a norm** (counterexample, triangle inequality fails); **Hamming distance** and mean absolute / squared error as scaled L1/L2 distances (link Module 08 losses); **distance-to-similarity conversions** named only.
- **L3:** **proofs, written in full:** (a) the **norm axioms** (positivity/definiteness, absolute homogeneity, triangle inequality) for L1, L2 (via Cauchy–Schwarz from Unit 2) and L∞; (b) **distance is a metric** (non-negativity, identity of indiscernibles, symmetry, triangle inequality) for every norm; (c) **norm equivalence in ℝⁿ with explicit constants**: `‖x‖∞ ≤ ‖x‖₂ ≤ ‖x‖₁ ≤ √n‖x‖₂ ≤ n‖x‖∞`, each inequality proved and shown tight by an explicit vector; (d) `‖x‖ₚ → ‖x‖∞` as `p → ∞` (proof); (e) a minimal counterexample for `p = ½`; (f) **squared L2 distance expansion `‖x − y‖² = ‖x‖² + ‖y‖² − 2x·y`** and the vectorised pairwise-distance identity built on it — **with its numerical hazard (catastrophic cancellation, tiny negative squared distances) demonstrated and the clip-at-0 remedy justified**; **overflow-safe L2 norm** (scale by `max|xᵢ|`; derive it; verify with an exact oracle on extreme inputs); **tool card for `vecnp.norms`** (all three norms + general `p`, distances, safe normalisation, pairwise distances with the identity above, vs a brute-force oracle).
- **L4:** **float16/float32/float64 norm behaviour** (overflow, underflow, accumulation error) measured locally; high-dimensional behaviour **previewed** (concentration of distances; deferred to `04-Similarity-Distance-and-Embedding-Geometry/03-high-dimensional-geometry-and-the-curse-of-dimensionality.md`); **unit balls of L1/L2/L∞ and the intuition for why L1 penalties favour sparse solutions** (geometry only, labelled `HEURISTIC`/intuition, with a small experiment); Mahalanobis distance **named only** (needs Module 09/4C); hostile inputs (NaN/Inf propagation policy, empty arrays, huge magnitudes, mixed dtypes); mutation lab (forgetting `abs` in L1; `sum` instead of `max` in L∞; missing square root; wrong `ord` mapping; negative squared distance not clipped) with no surviving mutants; case study: nearest-neighbour results changed after a silent dtype downcast (original synthetic reproduction).

## Unit 5 — Linear combinations, span, and linear independence

- **L1:** a **linear combination** `c₁v₁ + … + c_kv_k` (recall 4A-09 as a term; now n-D); **span** of a set of vectors (all linear combinations) with 2D/3D pictures (a point, a line, a plane, all of ℝ²/ℝ³); **is `b` in the span?** as solving `c₁v₁ + c₂v₂ = b` (small systems by hand; link 4A-04 and **forward-link `02-Matrices-and-Linear-Transformations/06-solving-ax-equals-b-and-gaussian-elimination.md`**); **linear independence** (no vector is a combination of the others; the only combination giving 0 is the trivial one) vs dependence, by hand for 2 and 3 vectors; the **standard basis**; ≥ 3 worked examples.
- **L2:** **independence in ML**: **redundant and collinear features** (a feature that is a multiple or sum of others), the **one-hot "dummy variable trap"** (original synthetic example: the one-hot columns sum to the all-ones column), why dependent columns make the normal equations singular (**forward-link `14-Linear-Models-Mathematics/02-the-normal-equation-and-closed-form-solution.md`**, `[VERIFY]` the exact filename in the tree); **testing independence in NumPy**: `np.linalg.matrix_rank` (**tolerance semantics `[VERIFY]`**), stacking vectors as columns `(n, k)`, and why **`k > n` vectors in ℝⁿ are always dependent**; **basis and dimension** (a basis = independent spanning set; dimension = size of a basis); **coordinates of a vector in a basis** (solve `Bc = x`; non-orthogonal vs orthogonal basis — orthogonal makes coordinates dot products, linking Unit 3); span of embeddings and "how many independent directions do these 1000 vectors really have?" (rank of a synthetic low-rank-plus-noise set; **preview of Module 03**).
- **L3:** **proofs, written in full:** (a) the span is closed under addition and scalar multiplication (a **subspace**; define; the zero vector is in it); (b) **a set containing the zero vector is dependent**; (c) **two vectors are dependent iff one is a multiple of the other**; (d) **a set is dependent iff some vector is a combination of the others**; (e) **`n + 1` vectors in ℝⁿ are dependent** (e.g., via the homogeneous system having more unknowns than equations, with the elimination argument written out; state precisely which result you rely on); (f) **non-zero mutually orthogonal vectors are linearly independent** (uses Unit 2); (g) uniqueness of coordinates in a basis; (h) every basis of ℝⁿ has exactly n vectors (**either prove it or state the result `CITED [VERIFY]` and say which**); **numerical analysis**: rank is **not robust in floating point** — a minimal example of a nearly dependent set where `matrix_rank` changes with the tolerance; a **tolerance-aware independence test** based on singular values (**preview only; the SVD is Module 03**) and the `HEURISTIC` status of any threshold; **tool card for `vecnp.span`** (exact independence/rank over `Fraction` via Gaussian elimination as the oracle; float rank with stated tolerance; membership-in-span test; coordinates in a basis).
- **L4:** **near-dependence and conditioning** (a set that is independent in exact arithmetic but numerically dependent; how the condition number — **named, defined in Module 02/03** — amplifies error); **exhaustive verification** of the exact rank tool against a brute-force definition (all integer `3×3` matrices with entries in `{−1, 0, 1}`: independence by checking all coefficient vectors in a bounded box is **not** a proof; state exactly what the exhaustive check shows) vs `sympy.Matrix.rank` (`EVIDENCE ONLY`); hostile inputs (zero columns, duplicates, ragged, NaN); mutation lab (off-by-one in pivot search, wrong tolerance direction, treating `k > n` as independent, forgetting to row-swap) with no surviving mutants; case study: a regression that "worked" in float but returned unstable coefficients because two features were nearly collinear (original synthetic reproduction with the diagnosis and the fix).

## Unit 6 — Practice questions (`practice-questions.md`) — see Section 7

## Unit 7 — Projects index (`Projects/README.md`) — see Section 9

## Unit 8 — Project: Vector operations library in NumPy (`Projects/01-vector-operations-library-in-numpy.md`) — see Section 8A

## Unit 9 — Project: Geometry of the dot product explorer (`Projects/02-geometry-of-dot-product-explorer.md`) — see Section 8B

# 7. UNIT 6 — PRACTICE QUESTIONS (REQUIREMENTS)

**Target file:** `practice-questions.md`. Not the four-level skeleton; use this structure:
1. **How to use this set** (hand first, then NumPy, then oracle; the 80/60 gate; honest self-scoring; AI-use disclosure).
2. **The question bank: ≥ 130 original items**: **≥ 20 per lesson (Units 1–5; 100 total)**, plus **≥ 12 cross-lesson integration items**, **≥ 10 ML-scenario/critique items** (an original code snippet or plan with a bug to find), and **≥ 8 coding tasks with pytest tests and independent oracles**. Each item follows the item format in Section 6. Difficulty spread per lesson: ~30% Easy, ~45% Medium, ~25% Hard. **≥ 20% of items are "trap" items** (zero vector, shape mismatch, NaN, float equality, `ord` confusion, `axis` confusion).
3. **A machine-readable key block** (JSONL) per lesson, with hand solutions, registered oracle names, and error-model distractor rationales.
4. **≥ 15 parameterised templates** (seeded) with exact `Fraction` keys where exactness is possible, so the learner can regenerate fresh practice.
5. **≥ 6 proof-completion/short-proof items** with rubrics (Cauchy–Schwarz, projection formula, norm axiom, independence lemma, norm equivalence, one more).
6. **A `qcheck` tool** (Tool card; verifies every key against its oracle on the stated domain and seeded parameters; audits distractors against error models; flags duplicate options, ambiguous keys, missing hand solutions, unknown fields; deterministic; hostile-pool tests; mutation lab with no surviving mutants).
7. **Scoring and gate rules**, remediation mapping (a missed item → lesson sections), and **small-n cautions** (a 20-item lesson score has wide uncertainty; give a Wilson interval example `CITED [VERIFY]`; no predictive claims).
8. **Every item tests only content taught in its linked lesson** (a later audit pass checks this).

# 8A. UNIT 8 — PROJECT 01: VECTOR OPERATIONS LIBRARY IN NUMPY (REQUIREMENTS)

**Target file:** `Projects/01-vector-operations-library-in-numpy.md`. Apply the four levels and N.0–N.14. It consolidates Units 1–5 into the local Python package **`vecnp`** (teaches no new mathematics; teaches **building a verified numerical library**).

**Required components:**
1. **API** (≥ 25 functions): validated constructors; dot, batched dot, cosine/angle (clip + zero policy); norms (`1`, `2`, `∞`, general `p ≥ 1`); safe normalise; Euclidean/Manhattan/Chebyshev distances; pairwise distances (identity-based and direct, with cancellation guard); scalar/vector projection; component removal (batched); residual; linear combination; span membership; rank/independence (float with tolerance and exact via `Fraction`); coordinates in a basis; Gram–Schmidt **single-step** only.
2. **Contracts:** documented shapes/dtypes, runtime preconditions, stable error codes (`E-VECNP-NNN`), **no mutation of caller inputs**, NaN/Inf policy, determinism.
3. **Oracles:** every function has an independent oracle (pure-Python `Fraction` reference, SymPy, or SciPy via a different path); the oracle never imports the code under test.
4. **Tests:** exhaustive small-domain tests (e.g., all integer vectors in `[-2, 2]³`), seeded random tests with stated tolerances, adversarial inputs, float32-vs-float64 sensitivity report, optional Hypothesis property tests (norm axioms; Cauchy–Schwarz; projection idempotence; shift invariance where applicable).
5. **Mutation lab** (wrong axis, missing clip, missing `abs`, wrong `ord`, `>` vs `≥`, denominator `u·u`, wrong tolerance direction) with **no surviving mutants**, plus a **regression guard**.
6. **Reproducibility:** `vecnp verify` (supports `--quick`; disk cap; PASS/FAIL list); `pyproject.toml` (local editable install only); fresh-`venv` contract; no network after install.
7. **Documentation:** package-layout mermaid diagram; API reference from docstrings; numerics notes; a **library card** (scope, tested domains, tolerances, versions, known limitations, "teaching/reference library — not a production numerics library").
8. **Report template** for the learner's own results (oracle-agreement table, mutation score, reproducibility run, issues found, AI-use disclosure, integrity statement) with the blank template and clearly labelled `[ILLUSTRATIVE]` synthetic example; **never fabricated results**.

**Rubric (provide in full):** traceability; correctness (oracle agreement); numerical robustness; test and mutation strength; reproducibility; documentation and library card; honesty of the report; integrity statement. Pass uses the 80/60 gate. **Stretch:** a `vecnp` vs plain-NumPy performance note (measured locally, variance stated); a peer code review.

# 8B. UNIT 9 — PROJECT 02: GEOMETRY OF THE DOT PRODUCT EXPLORER (REQUIREMENTS)

**Target file:** `Projects/02-geometry-of-dot-product-explorer.md`. Apply the four levels and N.0–N.14. It builds an **exploration tool** (CLI + notebook, matplotlib with a text/SVG fallback) that makes the dot product, angle, projection, and norms *visible*, and runs **seeded experiments** that connect geometry to ML behaviour. It uses `vecnp` (links Unit 8) or a minimal inlined equivalent.

**Required components:**
1. **2D/3D interactive-style explorer** (parameters via CLI/notebook widgets-free code): two vectors → dot product, angle, sign class, projection, residual, and orthogonality check, drawn to scale with a text fallback.
2. **Cauchy–Schwarz and triangle-inequality visual checks** over seeded random pairs, with the equality cases found and explained.
3. **Unit-ball gallery** for L1/L2/L∞ and `p ∈ {½, 1, 2, 4, ∞}` (showing `p = ½` is not convex).
4. **n-dimensional experiment lab** (all seeded; each reports sample size and Monte Carlo error): (a) **angle distribution of random pairs vs dimension** (nearly orthogonal in high dimension); (b) **variance of `q·k` vs dimension and the `1/√d` fix**; (c) **dot product vs cosine ranking** on a synthetic collection with varied magnitudes; (d) **removing a direction** from synthetic embeddings and re-measuring; (e) **near-dependence demo** (rank vs tolerance).
5. **Findings report** with honest interpretation: what each experiment shows, what it does **not** show, assumptions, and limits (**no claims about real models or datasets**).
6. **Verification:** every plotted/printed number matches an independent oracle; seeds fixed; `explorer verify --quick`; mutation checks on the geometry code (swapped angle sign, unnormalised cosine); regression guard; disk caps; accessibility: every figure has a text alternative.

**Rubric (provide in full)** analogous to Unit 8, plus "interpretive honesty". **Stretch:** an SVG-only renderer; a peer review.

# 9. UNIT 7 — PROJECTS README (REQUIREMENTS)

**Target file:** `Projects/README.md`. Not the four-level skeleton. Use this structure:
1. What the module's projects are and how they consolidate Units 1–5.
2. Index of both projects (project | purpose | key skills | verification method | links with exact repo paths).
3. How to choose and sequence them (Project 1 first; Project 2 depends on its functions or an inlined minimal version; fast-track rules and required evidence).
4. Project rules (original/synthetic data, seeds, `--quick`, disk caps, no network, AI disclosure, honest results, numerical policy).
5. Definition of done (checkable) and the evidence folder structure.
6. How the two projects feed the Stage 4B `mlmath` library (link `00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`) and later modules (02, 04, 08, 14).
7. A review checklist for self and peer.
8. **Promises vs delivery:** Unit 7 promises nothing Units 8–9 do not deliver.
Include **3 self-check questions**.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/vecnp/norms.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ with NumPy (1.x/2.x differences tagged), type hints on public functions, shape annotations on every array, runtime precondition checks, **no mutation of caller inputs**.
4. Every method and tool has its Method/Tool card before the code.
5. Conventions are stated once and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; `axis`, `ddof`, `ord`, dtype stated wherever relevant.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test); tests pass on the reference and fail on a deliberately broken variant.
8. **No unproven claims** about learning, hiring, interviews, performance, or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in Appendix F.
10. **Proofs are written in full where Section 6 requires them.** A counterexample is a disproof; agreement on examples is not a proof.
11. Library internals (BLAS, SIMD, pairwise summation, view/copy decisions in unusual cases) are **not guarantees**: teach the learner to test the behaviour; tag `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** sizes validated before heavy work; exhaustive oracles capped in code; files confined to the project directory; no unbounded loops/allocations.
13. **Security:** no `pickle`/`eval`/`exec` on untrusted text; strict loaders; oracles looked up by name in a fixed registry; `allow_pickle=False`.
14. No secrets, no paid APIs, no downloaded content; `clean` targets list what they remove and never delete the learner's evidence log.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `np.random.default_rng(seed)` / `random.Random(seed)`; no system-clock reads inside logic.

# 11. SCOPE GUARD

Never re-teach a 4A lesson, and never teach matrices, SVD, the curse of dimensionality, or calculus beyond the one-line previews named in Section 6. Link instead.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, standards, release notes | **NumPy docs**: array creation, `numpy.ndarray`, broadcasting, indexing and views vs copies, `numpy.dot`, `numpy.matmul`, `numpy.inner`, `numpy.einsum`, `numpy.linalg.norm`, `numpy.linalg.matrix_rank`, `numpy.finfo`, `numpy.isclose`, `numpy.random.Generator`, the **NumPy 2.0 migration guide**; **SciPy docs**: `scipy.spatial.distance`, `scipy.linalg`; **SymPy docs**: `Matrix.rank`, `Rational`; **Python docs**: `math` (`hypot`, `fsum`, `isqrt`), `fractions`, `random`; the **Python tutorial "Floating Point Arithmetic: Issues and Limitations"**; **IEEE 754** (by name) | API behaviour, defaults, versions |
| **T2** | Established textbooks and peer-reviewed papers (cite title/author/topic; **never invented page numbers, DOIs, or URLs**) | Deisenroth, Faisal & Ong, *Mathematics for Machine Learning* (vectors, norms, inner products, projections, independence); Strang, *Linear Algebra and Its Applications* and *Introduction to Linear Algebra*; Axler, *Linear Algebra Done Right* (inner products, Cauchy–Schwarz, independence); Horn & Johnson, *Matrix Analysis* (norms); Boyd & Vandenberghe, *Introduction to Applied Linear Algebra: Vectors, Matrices, and Least Squares* (VMLS); Goodfellow, Bengio & Courville, *Deep Learning*, Part I; Golub & Van Loan, *Matrix Computations*; Higham, *Accuracy and Stability of Numerical Algorithms*; Goldberg (1991) on floating point; Harris et al. (2020), "Array programming with NumPy", *Nature*; Vaswani et al. (2017) **only** for the origin of scaled dot-product attention if mentioned (`[VERIFY]`); Wilson (1927) / Brown, Cai & DasGupta (2001) for score intervals | Definitions, theorems, cited results |
| **T3** | Reputable university lecture notes, engineering write-ups | Pointer only, canonical only, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your memory) | — | **Never sufficient.** Convert to a derivation, an oracle check, or `[VERIFY]` |

Rules:
- You are **writing from knowledge, not consulting sources live**, unless you actually have browsing and use it. If you browse, record the URL and access date in Appendix A; otherwise state "written from knowledge; verify against current documentation." **All T1/T2 citations are `[VERIFY]`.** Give a URL only if certain it is canonical.
- **Computation is a source:** a hand derivation re-checked by an independent exact oracle is stronger than any citation; prefer it.
- **Do not reproduce or closely paraphrase copyrighted text**; name theorems and give your own statements and proofs.
- **Do not fabricate** version numbers, timings, benchmark or speed figures, success rates, hiring/interview statistics, employer requirements, "N% of …" figures, constants or formulas without a derivation or `[VERIFY]`, library internals as guarantees, quotes, or anecdotes. If a number is needed, derive it from a stated command or label it `[ASSUMPTION]`/`[ILLUSTRATIVE]`.
- **The repository tree is the source of truth** for names, counts, and paths; report conflicts as `OPEN`.
- Keep a running **Claim Register** (12.3).

## 12.2 Mandatory multi-pass self-audit (after drafting, before delivering each part)

Run in order; fix every defect.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 10 units, every required section (Sections 5–9), every topic and proof in Section 6, L1–L4, ≥ 3 worked examples per level L1–L2, the ≥ 130-item bank, both projects' full component lists. | Any missing section/topic/proof/example/item. |
| 2 | **Convention consistency** | Claims, correctness, shape/axis/index notation, zero-vector policy, numerical policy, original-content, item format, data/security, integrity, gate conventions identical in every unit, tool, item, test. | Any mixed or silently changed convention. |
| 3 | **Claims honesty** | Every claim on learning, hiring, performance, or role requirements is cited `[VERIFY]` with limits, `[JUDGEMENT]`/`[ASSUMPTION]`, verifiable, or absent; no speed/benchmark figures as facts. | Unsupported claim. |
| 4 | **Traceability** | Every objective → lesson, practice items, project component; Unit 7 promises nothing Units 8–9 do not deliver; every can-do has a "prove it" task. | Orphan or undelivered promise. |
| 5 | **Mathematical correctness** | **Re-derive every definition, formula, proof, worked example, and key by hand, independently of the draft**; check signs, shapes, domains, conventions, edge cases. | Any wrong value, sign, shape, or step. |
| 6 | **Proof audit** | Every proof listed in Section 6 is present, complete, states hypotheses, has no circular step; the **definition-vs-theorem** distinction for angles is respected; any result only cited is labelled `CITED [VERIFY]`. | Missing, circular, or invalid proof. |
| 7 | **Numerical-analysis audit** | Tolerances justified; no float `==`; clip before `arccos`; cancellation in the pairwise-distance identity demonstrated; overflow-safe norm derived; float32/64 claims checked; `matrix_rank` tolerance caveats present. | Unjustified tolerance or unsafe numerics. |
| 8 | **Oracle independence** | Every NumPy-based claim has an oracle that is exact, pure-Python, SymPy, or a different library path; no oracle imports the code under test; exhaustive domains named, sized, feasible, and never called proof. | Shared-logic oracle or overclaim. |
| 9 | **Item-key and distractor audit** | Every key equals its oracle; every distractor equals its error-model output; exactly one key; no duplicate options; every item answerable from its linked lesson alone. | Ambiguous key, duplicate options, out-of-scope item. |
| 10 | **Tool-card audit** | `env_check`, `vecnp` modules, `qcheck`, `explorer`, and `verify` commands have complete cards consistent with code and tests. | Missing or inconsistent element. |
| 11 | **Source-authenticity audit** | **Every non-trivial claim maps to a T1/T2 source or a derivation in Appendix A; no T4-only claim; no invented citation, DOI, URL, or page number; no misattributed result.** | Unsourced, misattributed, or invented citation. |
| 12 | **Cited-results audit** | Every cited-only result (NumPy API semantics, `ord` meanings, `matrix_rank` tolerance, pairwise summation, norm equivalence if not proved, dimension theorem if not proved, Wilson interval) is tagged `[VERIFY]`, listed in Appendix C with a learner-side check, never presented as proved. | Cited result presented as proved. |
| 13 | **Statistical validity** | Every experiment reports seeds, sample sizes, and Monte Carlo error; "nearly orthogonal in high dimension" and the `1/√d` argument are stated with their assumptions; no claim about real models/data. | Missing uncertainty or overclaim. |
| 14 | **Originality and IP** | All problems, data, scenarios original/synthetic; named results by name and own statement. | Copied or closely paraphrased content. |
| 15 | **Integrity, ethics, fairness** | No cheating guidance; AI-use disclosure applied to every graded artifact; accessibility text alternatives; debiasing demo makes no fairness claim; gates framed as curriculum convention. | Cheating-adjacent advice, overclaim, or credential framing. |
| 16 | **Privacy and data handling** | Local, human-readable, validated, atomic; no PII; `env_check` excludes hostnames/usernames; `allow_pickle=False`; no telemetry/network. | PII, hidden network, unsafe storage. |
| 17 | **Determinism** | `default_rng(seed)` everywhere; no system-clock reads in logic; thread/BLAS effects acknowledged; deterministic ordering/tie-breaks. | Nondeterminism or wall-clock dependence. |
| 18 | **Technical accuracy (Python/NumPy)** | Every function, signature, default, and version claim is real and correct; **mentally execute every code block and lab**; NumPy 1.x vs 2.x tagged. | Invented API, misuse, wrong version claim. |
| 19 | **Executability** | Syntactically valid code; imports resolve; paths and links resolve; tests pass on reference and fail on a broken variant; every lab has steps, evidence, cleanup; `vecnp` installs editable and `vecnp verify` passes. | Any broken or unrunnable step. |
| 20 | **Repository consistency** | Module/lesson/project names, counts, and all relative links match the tree exactly (spaces URL-encoded; em dash preserved); forward links to other modules point to names that exist, else are marked `OPEN`. | Wrong name, count, path, or link. |
| 21 | **Pedagogical consistency** | Real beginner→expert progression; nothing used before taught or forward-referenced; **no re-teaching of 4A lessons**; matrices/SVD/curse-of-dimensionality/gradients previewed only; terminology and symbols stable. | Forward dependency without note, duplication, drift. |
| 22 | **Resource safety** | Caps before heavy work; exhaustive tests size-capped; no lab can exhaust memory/disk/time. | Unbounded work. |
| 23 | **Security and input validation** | No unsafe deserialization or `eval`/`exec`; strict loaders; named oracle registry. | Unsafe example. |
| 24 | **Currency** | Version-sensitive claims tagged; Python 3.10 minimum respected. | Stale or untagged claims. |
| 25 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated outputs (outputs are labelled representative), misattributed results, invented constants, real-model claims, cited results presented as proved. | Any unsupported specific. |
| 26 | **Cross-consistency** | Practice bank, project code, tool cards, and lessons agree on names, error codes, conventions, and thresholds; stage-overview links resolve. | Contradiction or orphan. |
| 27 | **Adversarial review** | Re-read as a skeptical staff engineer: "What here is wrong, misleading, over-claimed, or teaches a bad habit (trusting `np.linalg.norm` as the oracle, an unclipped `arccos`, `inv`/`rank` without tolerance, one seed)?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 28 | **Reproducibility** | Labs and projects fit 4 CPU / 8 GB / 30 GB and disk caps; no paid service/account/download beyond the pinned install; seeded, idempotent, `--quick`; cleanup preserves learner data. | Hidden cost, nondeterminism, external dependency. |

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

**Appendix A — Source Register and Claim Register.** (i) **Source Register:** `Source ID | Tier (T1–T4) | Full citation (author, title, year/version) | Topics supported | Access (consulted live with URL+date / from knowledge) | [VERIFY] status`. (ii) **Claim Register:** `ID | Unit | Claim | Source ID(s) or derivation | Confidence (High/Med/Low) | Tag (PROVED/CITED/EVIDENCE ONLY/HEURISTIC/JUDGEMENT/ASSUMPTION)`. At least **90 entries**, covering every library-behaviour claim, formula, proof, cited result, attribution, and consequential judgement.

**Appendix B — Audit Report** (passes 1–28): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** every `[VERIFY]`/`[VERSION-SENSITIVE]`/`[JUDGEMENT]`/`[ASSUMPTION]` item and every CITED result, grouped (NumPy/SciPy/SymPy API and versions; floating point; linear-algebra citations; learning-science/statistics citations; repository consistency), each with *what to check*, *where (named source)*, and *how to test locally in one command or small script*. The reviewer must be able to close every item in **under 8 hours**.

**Appendix D — Known Limitations and Assumptions:** what is intentionally not covered (matrices, SVD, curse of dimensionality in depth, calculus, GPU/half-precision production numerics, exam preparation, credentials); assumed versions; synthetic nature of all data; no validated link between practice scores and any job outcome; anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code and tests and human re-derivation of the mathematics.

**Appendix F — Proof, Status, and Counterexample Index:** every method/tool/proof with status, hypotheses, technique, and verification evidence; and a **minimal instance** for each counterexample: `(n,)+(n,1)` silent broadcast; view-aliasing mutation; float addition non-associativity; unclipped `arccos` domain error; `arccos` inaccuracy near ±1; zero-vector cosine; `p = ½` violating the triangle inequality; `ord=0` not a norm; cancellation making a squared distance negative; removing non-orthogonal directions one at a time ≠ removing their span; independent in exact arithmetic but rank-deficient at a float tolerance; one-hot dummy-variable dependence; overflow in an unscaled L2 norm.

**Appendix G — Executable Verification Bundle:** a standard-library-plus-NumPy `verify_syllabus.py` that extracts every fenced Python block with a `# File: …` first-line comment, writes it to a scratch directory, byte-compiles it, runs the tests in `--quick` mode with timeouts and a disk cap, and prints PASS/FAIL; plus `verify_module01.py` that verifies: every proof's numerical sanity checks; every worked example against its oracle; every practice key against its registered oracle and every distractor against its error model (`qcheck`); the exact rank tool vs `sympy` on the stated exhaustive domain; the Cauchy–Schwarz and norm-equivalence inequalities on seeded samples and boundary cases; the pairwise-distance cancellation demo; mutation lab and regression guard; and **all repository paths and counts against a reviewer-supplied `find` listing**.

## 12.4 Trust rules

- If a pass finds a problem you cannot fix confidently, **leave it visible** as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim code "was tested/executed" unless it actually was; say "expected output (representative)".
- Never claim content "was verified against live documentation" unless you consulted it.
- Never present exhaustive or seeded testing as proof; never present a cited result as proved; never present a gate score as a predictor or credential.
- Never state benchmark or speed figures as facts, success rates, hiring statistics, or employer requirements; never invent quotes or anecdotes; never present opinion as research.
- Attributions must be correct or marked `[VERIFY]`; never invent a citation, DOI, URL, or page number.
- Never advise anything that helps misrepresent skill or cheat; AI use is for explanation and review, disclosed and verified.

# 13. OUTPUT FORMAT

- **One Markdown document**, `SYLLABUS-Vectors-Dot-Product-and-Norms.md`.
- Start with: title; one-paragraph abstract (**explicitly stating that the module generalises 4A vectors to n dimensions, teaches the geometric dot product, projection, norms and distance, and span/independence in NumPy with proofs and oracles; defers matrices, SVD, curse-of-dimensionality, and calculus; makes no outcome, credential, or real-model claims; and that every worked example and key is verified two independent ways**); metadata block (`Module: S4B-01`, `Stage: 4B`, `Language: Python`, `Estimated total time [ASSUMPTION]`, `Last reviewed`, `Assumed tool baseline`); a **linked table of contents** to all units and appendices.
- Then Units 0–9 in order, then Appendices A–G.
- `#` title, `##` units, `###`/`####` below; consistent anchors. Tables for comparisons, templates, rubrics; fenced code with language tags; **mermaid** for diagrams (lesson dependency graph, norm-relationship map, package layout, experiment pipeline); plain-text math with Unicode, no LaTeX; every plot has a text alternative.
- Each unit self-contained but cross-linked (relative links to sibling files, 4A lessons, later 4B/4C modules by exact name; URL-encode spaces, keep the em dash as in the repository path).
- **Depth target:** each of Units 1–5 ≥ 3,500 words of teaching text excluding code, proofs, items, and tables (proofs additional); Unit 0 ≥ 1,800; Units 8 and 9 ≥ 2,500 each; Unit 7 ≥ 1,000; Unit 6 carries the full bank. **Do not compress to fit**; use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no "see previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0 |
| 2 | Unit 1 (all levels, N.0–N.14) |
| 3 | Unit 2 |
| 4 | Unit 3 |
| 5 | Unit 4 |
| 6 | Unit 5 |
| 7 | Unit 6 part A: structure, `qcheck` tool, items for lessons 1–3, JSONL keys |
| 8 | Unit 6 part B: items for lessons 4–5, integration, scenario/critique, coding tasks, proof items, templates, scoring |
| 9 | Unit 7; Unit 8 part A (N.0–N.5, specification, `vecnp` modules core/dot) |
| 10 | Unit 8 part B (remaining modules, tests, mutation lab, `vecnp verify`, library card, report template, N.6–N.14, rubric) |
| 11 | Unit 9 (complete) |
| 12 | Appendices A–G, including the completed audit across **all** parts |

Rules:
- End each part with: `PART n/12 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-part audit (passes scoped to that part) **before** printing; keep a running Source and Claim Register.
- Part 12 runs the **cross-part** audit (passes 2, 11, 20, 21, 26, 27 especially) and may require **correcting earlier parts**: list each as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarise a unit to save space. If near the length limit, stop at a clean boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 12, print: "Concatenate Parts 1–12 in order into `SYLLABUS-Vectors-Dot-Product-and-Norms.md` and apply all listed corrections."

# 15. QUALITY BAR — DEFINITION OF DONE

Complete only when **all** are true:

- [ ] All 10 units present in order; Units 0–5, 8, 9 each with L1–L4 and N.0–N.14; Units 6 and 7 with their required structures; ≥ 3 worked original examples at each of L1 and L2, each verified two independent ways.
- [ ] Every topic and **every listed proof** in Section 6 is present and complete; the definition-vs-theorem distinction for angles in n dimensions is explicit; nothing from 4A is re-taught; matrices, SVD, curse-of-dimensionality, and calculus are previewed only.
- [ ] Every method and tool has a card with status, runtime-checked preconditions, an independent oracle, exhaustive small-domain tests, seeded and adversarial tests, mutation checks, and deterministic behaviour.
- [ ] Conventions (claims, correctness, shape/axis/index, zero-vector, numerical, original content, item format, data/security, integrity, gates) are stated once and applied consistently.
- [ ] **No unsupported claim** about learning, hiring, interviews, role requirements, performance/benchmarks, employers, real models, or library internals.
- [ ] **Every non-trivial claim maps to a T1/T2 source or a derivation in the Source Register; no T4-only claim; no invented citation, DOI, URL, or page number.**
- [ ] The **≥ 130-item bank** (≥ 20 per lesson) has machine-readable keys, hand solutions, registered oracles, and error-model distractors, all machine-checked by `qcheck`; ≥ 8 coding tasks, ≥ 6 proof items, ≥ 15 templates.
- [ ] `vecnp` (≥ 25 functions, tests, mutation lab, `vecnp verify`) installs editable in a fresh `venv` and passes `--quick` within disk caps; the explorer project runs seeded experiments with sample sizes and error estimates; report templates contain **no fabricated results**.
- [ ] Every counterexample in Appendix F is demonstrated with a minimal instance.
- [ ] Every "verified on all small inputs" statement names its domain and size and is never called proof.
- [ ] Names, counts, project file names, 4A/4B/4C links match the tree; unresolved forward links are marked `OPEN`.
- [ ] Randomness via `default_rng(seed)`; no wall-clock logic; data local, human-readable, validated, atomically written; no `pickle`/`eval`/`exec`; no network at run time.
- [ ] Integrity policy consistent: AI use disclosed and verified; text alternatives for plots; no fairness claims from the debiasing demo; gates framed as curriculum convention.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and `--quick`.
- [ ] Appendices A–G present; Claim Register ≥ 90 entries; audit passes 1–28 reported candidly; `verify_syllabus.py` and `verify_module01.py` delivered and consistent with the `# File:` comments.
- [ ] A human can close every open item in under 8 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/12**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Session:** use a long-context, high-capability model and one conversation across all 12 parts so the registers, conventions, and the `vecnp` running example stay consistent; type `continue` between parts.
2. **Scope decision:** 4A-09 already teaches length, unit vectors, the algebraic dot product, angle intuition, and a typed point/vector discipline, so this prompt makes S4B-01 **generalise and prove** (n dimensions, geometric dot product, Cauchy–Schwarz, projection, Lp norms, span/independence) in **NumPy** instead of repeating 4A. If you want 4A material re-taught, say so and I'll adjust.
3. **Numbering:** the unit table has 10 units (0–9) matching the 10 files in the tree.
4. **Human verification:** run `verify_syllabus.py` and `verify_module01.py` (Appendix G) with a `find` listing; hand re-derive Cauchy–Schwarz, the projection formula, the norm-equivalence chain, and the `1/√d` variance argument; check each `[VERIFY]` NumPy behaviour (`np.linalg.norm` `ord`, `matrix_rank` tolerance, broadcasting, NumPy 2.x changes) against the official docs.
5. **Highest fabrication-risk spots:** NumPy API defaults and version claims; "nearly orthogonal in high dimensions" (must be shown with a seeded experiment and error bars, not asserted); the `arccos` stability alternative; the dimension theorem if only cited; any speed claim; forward-link filenames in other modules (the prompt tells the model to mark unresolved ones `OPEN`).
6. **Final layout:** split the output into the ten target files plus supporting code under the project folders.
