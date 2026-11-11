# PROMPT — Generate `SYLLABUS-Matrices-and-Linear-Transformations.md` (Stage 4B, module S4B-02)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is very large, so use the **Delivery Protocol** (Section 14): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Matrices-and-Linear-Transformations.md` in `Stage 4B — Mathematics for Machine Learning/02-Matrices-and-Linear-Transformations/`.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have shipped models whose cores are matrix products and linear solves, and you have debugged the failures that weak matrix fundamentals cause: a weight matrix applied as `Wx` in one file and `xW` in another; `X @ W` with `W` transposed and a square shape hiding the bug; a "batched" multiply that silently broadcast; `np.linalg.inv(A) @ b` returning garbage on a near-singular `A` with no error; a determinant used as a singularity test and wrongly reporting "singular" for a perfectly healthy matrix; a normal-equation solve on collinear features; a rotation applied in the wrong order; a low-rank factorisation whose rank was misjudged because of a tolerance. You teach the way you work: **derive by hand, verify independently with exact arithmetic, state shapes, conventions, and tolerances, and make every statement checkable.**

You are also a careful technical author. You never invent a function, signature, default, formula, constant, version, statistic, citation, **claim about how much mathematics any employer, interview, or role requires, "time to learn" figure presented as fact, benchmark or speed figure, or claim about how any real model, library internals, or product works**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion is marked `[JUDGEMENT]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 4B — Mathematics for Machine Learning / 02-Matrices-and-Linear-Transformations/` (module code **S4B-02**, the matrix and linear-map core of the linear-algebra spine).

Output file name: **`SYLLABUS-Matrices-and-Linear-Transformations.md`**, saved inside that folder.

Teach, **one after another, from beginner to advanced**, these 15 units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | Matrices as data tables and linear maps | `01-matrices-as-data-tables-and-linear-maps.md` |
| 2 | Matrix–vector and matrix–matrix multiplication | `02-matrix-vector-and-matrix-matrix-multiplication.md` |
| 3 | Transpose, identity, and special matrices | `03-transpose-identity-and-special-matrices.md` |
| 4 | Matrix shapes, broadcasting, and batching | `04-matrix-shapes-broadcasting-and-batching.md` |
| 5 | Linear transformations: rotation, scaling, and shear | `05-linear-transformations-rotation-scaling-and-shear.md` |
| 6 | Solving Ax = b and Gaussian elimination | `06-solving-ax-equals-b-and-gaussian-elimination.md` |
| 7 | Determinants and invertibility | `07-determinants-and-invertibility.md` |
| 8 | Matrix inverse and when it fails | `08-matrix-inverse-and-when-it-fails.md` |
| 9 | Rank and column-space intuition | `09-rank-and-column-space-intuition.md` |
| 10 | Practice questions | `practice-questions.md` |
| 11 | Projects index | `Projects/README.md` |
| 12 | Project: Matrix operations from scratch | `Projects/01-matrix-operations-from-scratch.md` |
| 13 | Project: Gaussian elimination solver | `Projects/02-gaussian-elimination-solver.md` |
| 14 | Project: Linear transformation visualizer | `Projects/03-linear-transformation-visualizer.md` |

Do **not** add, merge, skip, or reorder units. Do not teach eigenvalues/SVD (Module 03), similarity and embedding geometry (Module 04), matrix calculus or Jacobians (Modules 07 and 4C-02), the full theory of LU/QR/Cholesky, subspaces, rank–nullity and the four fundamental subspaces (4C-01), or least-squares/regression (Module 14): **name, link, and give a one-line preview only.** This is the **teaching content itself**, not an outline.

**Repository tree for this module (verify; report any mismatch as `OPEN`):**

```text
02-Matrices-and-Linear-Transformations/
├── Projects/
│   ├── 01-matrix-operations-from-scratch.md
│   ├── 02-gaussian-elimination-solver.md
│   ├── 03-linear-transformation-visualizer.md
│   └── README.md
├── 01-matrices-as-data-tables-and-linear-maps.md
├── 02-matrix-vector-and-matrix-matrix-multiplication.md
├── 03-transpose-identity-and-special-matrices.md
├── 04-matrix-shapes-broadcasting-and-batching.md
├── 05-linear-transformations-rotation-scaling-and-shear.md
├── 06-solving-ax-equals-b-and-gaussian-elimination.md
├── 07-determinants-and-invertibility.md
├── 08-matrix-inverse-and-when-it-fails.md
├── 09-rank-and-column-space-intuition.md
├── README.md
└── practice-questions.md
```

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–3, Stage 4A, and **S4B-01** (`01-Vectors-Dot-Product-and-Norms`). They write working Python, use `venv`/`pytest`, know Big-O, and can use NumPy arrays, dot products, norms, projections, span, and independence from S4B-01.
- **Already taught — link, never re-teach:** from **4A**: solving systems by substitution and elimination (`04-Equations-Inequalities-and-Systems/11-…substitution`, `12-…elimination`, `13-special-cases-no-solution-and-infinitely-many-solutions`, and especially **`14-three-variable-systems-and-the-bridge-to-matrices`**), degrees/radians and the unit circle (`08-Geometry-and-Trigonometry/04`, `06`), vectors (`09-Vectors-as-Arrows-and-Data-Points`); from **S4B-01**: n-D vectors and NumPy shapes (`01-vectors-in-n-dimensions-and-numpy-arrays`), the dot product and Cauchy–Schwarz (`02`), projection (`03`), norms (`04`), span/independence/basis and the `matrix_rank` caveat (`05`). **State in one line what each already gave, link to the exact lesson (names read from the repository tree), and state what this module adds.** Specifically: S4B-01 introduced `matrix_rank` and independence on collections of vectors; **this module makes the matrix the central object, and rank/column space gets its matrix-level treatment here (Unit 9)** without re-proving S4B-01's independence lemmas.
- **Stage position:** S4B-01 → **S4B-02 (this module)** → `03-Eigenvalues-SVD-and-Low-Rank-Structure`, `04-Similarity-Distance-and-Embedding-Geometry`, `07-Multivariable-Calculus-and-Gradients`, `14-Linear-Models-Mathematics` → 4C-01 (`01-Advanced-Linear-Algebra`), 4C-02 (`02-Multivariable-and-Matrix-Calculus`), 4C-09 (`09-Mathematics-of-Transformers-and-Representations`) → Stages 5A–5D. Link the stage overview `00-Stage-4-Overview` and `how-4b-connects-to-4a-and-4c.md`. **Use only module and lesson names that exist in the tree.**
- **Zero budget.** Local laptop (WSL2 Ubuntu primary; native Linux/macOS secondary), ~4 CPU cores, 8 GB RAM, 30 GB disk. **No GPU, no paid service, no accounts, no API keys, no network at run time, no scraping, no downloaded datasets.** **Every problem, scenario, and dataset is original or synthetic** (seeded generators). One-time pinned `pip install` is the only permitted network use. **Disk footprint cap for any lab or project: default ≤ 64 MB, `--quick` ≤ 8 MB.** Matrix sizes in labs are capped (default `n ≤ 512`, `--quick` `n ≤ 128`) so nothing exhausts 8 GB.
- **Tool baseline:** **CPython 3.12** `[ASSUMPTION; minimum 3.10]`, `venv`, `pytest`, **`numpy`** (required; tag NumPy 1.x vs 2.x differences `[VERSION-SENSITIVE]`), **`fractions.Fraction` and `sympy`** (exact oracles), **`scipy`** (independent oracle: `scipy.linalg`, `scipy.sparse` awareness), **`matplotlib`** (plots; a text/SVG fallback must work). Optional: `hypothesis`, `ruff`, `mypy`. All version numbers `[VERIFY]`.
- **Domain flavour (all original; no real-company, real-model, or real-dataset claims):** a data table as a matrix of samples × features; a dense layer as `y = Wx + b` and as `Y = XWᵀ + b`; a batch of layers; a toy attention-shaped `QKᵀ` multiply (shapes and cost only, **no claim about any real model**); 2D point-cloud transformations; collinear-feature regression design matrices; a rank-`r` factorisation parameter-count calculation. Sizes such as `d = 768` appear only as `[ILLUSTRATIVE]`.
- **Running example thread:** **"the learner's matrix toolkit"** evolves through the module: tables and maps (Unit 1) → multiplication (2) → special matrices (3) → shapes and batching (4) → geometric maps (5) → solving (6) → determinant (7) → inverse and conditioning (8) → rank (9) → practice (10) → three projects (12–14): `matscratch` (from-scratch operations), `gesolve` (elimination solver), `ltviz` (visualizer). Reuse it so the learner sees one artifact grow.
- **Continuity and links:** back to 4A and S4B-01 as above, S3-14 (stress harness/oracles) and S3-20 (practice log, error log, spaced-repetition deck — **reuse, never rebuild**); forward to later modules by exact folder name. State **taught here vs deferred**.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 0–9 AND 12–14)

Each of these units progresses through **exactly four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the idea and picture, follows worked examples, computes small cases by hand and in NumPy. |
| **L2** | Intermediate — Working Practice | Applies it unaided in NumPy to realistic ML cases, handles shapes/axes/conventions, avoids classic failure modes. |
| **L3** | Advanced — Engineering Rigor | Proves the key results, states precise conditions, quantifies numerical error and cost, verifies with independent exact oracles, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in unfamiliar code and data, handles singular/ill-conditioned/degenerate cases, builds and mutation-tests tools, coaches others. |

Units 10 and 11 use the structures in Sections 7 and 9.

# 5. MANDATORY STRUCTURE FOR UNITS 0–9 AND 12–14

Use this exact skeleton. If a section is genuinely not applicable, write one sentence saying why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours, [ASSUMPTION]>  |  **Prerequisites:** <list with links>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete, verifiable failure this prevents. No hype, no outcome claims.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4 with an ID `S4B02.U<N>.O<k>`.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid diagram, annotated for a worked example.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what), with a picture (matplotlib/SVG with ASCII fallback) where geometric
- At least 3 fully worked original examples (hand derivation + independent exact computation + expected output)
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic worked ML example (complete, runnable, every array shape annotated), continuing the running example
- At least 3 further worked examples
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad practice → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- **Proofs written in full** (listed per unit in Section 6), each stating hypotheses; counterexamples where a hypothesis is dropped
- Method card / Tool card: (1) goal and when to use, (2) inputs/outputs with shapes and dtypes, (3) steps, (4) invariants/acceptance criteria as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain
- Cost analysis (flop and memory counts derived, not asserted) and numerical analysis (error sources, tolerances with justification, float32 vs float64)
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Exercise requiring a defended proof, derivation, or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Degenerate and adversarial inputs (singular and near-singular matrices, zero rows/columns, NaN/Inf, empty/1×1/non-square shapes, huge magnitudes, dtype surprises)
- Automation: aggregate verification commands, property tests, regression guards
- Coaching: reviewing a peer's code/derivation with evidence-based feedback
- Platform and version differences (Python 3.10 vs 3.12; NumPy 1.x vs 2.x; BLAS threads; float32 vs float64)

### N.7 Engineering lens
(Where the idea fails in real ML systems — verifiable numerical/shape failures only, never a company claim. Failure modes, blast radius, memory and compute cost arithmetic, vectorisation vs loops measured locally with stated variance.)

### N.8 Integrity lens
(Reasoning/measurement risks: trusting a plot, one seed, a library call as the only oracle, memorised procedures without proof. AI-assistance disclosure. Controls verifiable by a command, test, or written check.)

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

- **Claims policy.** Every claim about learning efficacy, study method, hiring, interviews, performance, library internals, or role requirements is exactly one of: (a) cited research/documentation tagged `[VERIFY]` with limits; (b) practitioner opinion tagged `[JUDGEMENT]`; (c) a verifiable statement about mathematics, code, or the tree; or (d) omitted. **No success rates, no employer claims, no invented quotes or anecdotes, no benchmark/speed/accuracy figures as facts.** Durations and illustrative sizes are `[ASSUMPTION]`/`[ILLUSTRATIVE]`.
- **Mathematical correctness policy.** Every worked example and key is verified **two independent ways**: (1) a hand derivation in the text, and (2) an independent computation — **exact (`Fraction` matrices / `sympy`) wherever possible**, otherwise NumPy/SciPy with a **stated tolerance and reason** (never float `==`). **NumPy results are never the sole oracle for a NumPy-based claim**; use exact arithmetic, a pure-Python reference, SymPy, or SciPy via a different code path. Agreement on examples is evidence, not proof of a general statement; say so.
- **Notation, shape, and convention.** `A ∈ ℝ^{m×n}` has `m` rows and `n` columns; `A_{ij}` is row `i`, column `j`; vectors are **columns** (`x ∈ ℝⁿ`, NumPy `(n,)` or `(n, 1)` — always say which); a data matrix `X` is `(n_samples, n_features)` with **rows as samples**; a dense layer is written **both** ways — `y = Wx + b` with `W: (d_out, d_in)` (column-vector convention) and `Y = XWᵀ + b` (row-sample convention) — **and the module uses these two forms consistently and says which one each example uses**; **every array carries a shape annotation** (`# A: (m, n)`); mathematical indices are 1-based, Python 0-based, shown side by side; `axis` names the collapsed dimension; plain-text math with Unicode (`ᵀ`, `⁻¹`, `∈`, `≈`, `Σ`), **no LaTeX**.
- **Degenerate-case policy.** Singular matrices, non-square inverses, shape-mismatched products, and zero pivots **raise `ValueError` (or a documented `SingularMatrixError(ValueError)`) with a stable message** of the form `E-<TOOL>-<NNN>: <text>`; no tool returns a silent wrong answer; near-singularity is **reported with a condition-number estimate**, never silently ignored. Thresholds are stated and `HEURISTIC`.
- **Numerical policy.** float32 vs float64 and `np.finfo`; `np.isclose`/`np.allclose` defaults (`rtol=1e-05`, `atol=1e-08`) and why `atol` matters near zero `[VERIFY]`; **never use the determinant as a singularity test in floating point** (taught explicitly); **never form `A⁻¹` to solve `Ax = b`** (taught explicitly with a measured counterexample); partial pivoting and why; backward error and residual `‖Ax − b‖` vs forward error (definition level; theory `CITED [VERIFY]`); `matrix_rank` tolerance semantics `[VERIFY]`; summation order and `math.fsum`; determinism via `np.random.default_rng(seed)` only.
- **Original-content policy.** All problems, scenarios, and data are original/synthetic. Named results (associativity of matrix multiplication, the multiplicative property of the determinant, the invertible-matrix equivalences, the row-rank = column-rank theorem, Rouché–Capelli) are referred to **by name and your own statement only**; never reproduce a textbook's wording, figures, or exercise sets.
- **Item format (all practice items and self-checks):** `ID`, `Lesson`, `Level` (L1–L4), `Can-do ID`, `Stem`, `Answer format` (MCQ-4 / numeric-exact / numeric-tolerance / matrix-exact / short-proof / code), `Key` (exact; `Fraction` strings for rationals; matrices as JSON lists of `Fraction` strings), `Hand solution`, `Oracle` (**the name of a registered pure Python function in a fixed registry — never an `eval`ed string**), `Distractor rationale` (**each MCQ distractor produced by an error-model function for a named misconception — e.g., multiplying elementwise instead of by matrix product; `(AB)ᵀ = AᵀBᵀ`; `(AB)⁻¹ = A⁻¹B⁻¹`; `det(A+B) = det A + det B`; row-vs-column convention swap; applying rotations in the wrong order; forgetting to swap rows when a pivot is zero — not typed by hand; exactly one key; no distractor equals the key; no duplicate options**), `Time estimate [ASSUMPTION]`, `Difficulty` (Easy/Medium/Hard by explicit criteria: steps, concepts combined, trap present), `Tags`.
- **Data/security policy.** All data local, human-readable, validated, written atomically (`os.replace`); no PII, no telemetry, no network; never `pickle`/`marshal`/`eval`/`exec` on untrusted text; `np.load(..., allow_pickle=False)`; strict loaders reject unknown fields and enforce size caps; matrix sizes validated before allocation.
- **Integrity policy.** Graded answers are the learner's own; AI assistance allowed for explanation/review, **disclosed in the evidence log**; AI-produced derivations or code are **untrusted hypotheses verified against an oracle**; every plot has a text alternative; maths anxiety acknowledged as real (awareness only, `[JUDGEMENT]`, no clinical claims).
- **Status vocabulary:** `PROVED`, `CITED`, `EVIDENCE ONLY`, `HEURISTIC`, `JUDGEMENT` (markers: `[ASSUMPTION]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[VERIFY]`). **Exhaustive or seeded testing never upgrades a status to `PROVED`.**
- **Gate convention (inherits the repository's):** ≥ 80% proceed; 60–79% remediate named lessons and retake; < 60% repeat the module; thresholds are `HEURISTIC`/`JUDGEMENT`; no credential implied.

## Unit 0 — Module orientation (`README.md`)

- **L1:** what S4B-02 is and is not; **what 4A and S4B-01 already gave (one line each, linked) vs what this module adds**; the lesson map with one-line purposes and links to all nine lessons, practice, and the three projects; how to use a lesson (read → derive by hand → implement → verify against an exact oracle → explain aloud); "hand first, machine second"; **why matrices are the workhorse of ML** (a data table, a linear layer, a transformation, a system of equations, a weight update — original illustrations only); environment check (`env_check` printing Python/NumPy/SciPy/SymPy versions and float epsilon; no hostname/username); first demo: the same `2×2` matrix read as a table, as a map on the plane, and as a system.
- **L2:** the lesson dependency graph (1 → 2 → 3, 2 → 4, 1 → 5 (needs 2), 2 → 6, 6 → 7, 6 → 8, 7 → 8, 6 → 9, 8, 9 closing the "when does a solution exist and is it unique" thread), stated and justified; recommended order and pacing (`[ASSUMPTION]`; link to the stage `learning-plan.md`); **the module can-do checklist** (≥ 5 per lesson, ≥ 45 total, IDs `S4B02.L<k>.C<j>`, each with a "prove it" task and practice link); evidence folder layout (`stage4b/02-matrices/notes|notebooks|practice|project|evidence-log.md`); the error log and spaced review (reuse S3-20; link only).
- **L3:** objectives as checkable statements with a traceability table (objective → lesson → practice items → project component); **definition of done**; **the "five faces of a matrix" table** (table of data; linear map; system of equations; collection of column/row vectors; operator in a computation graph) with where each appears in the module; **the convention sheet** (shape, row/column, `Wx` vs `XWᵀ`, 1- vs 0-based) with executable examples; the exact-vs-float policy for the module.
- **L4:** coaching a peer through the module; adapting pacing for rusty/strong/time-limited learners; **drift check** (a script comparing the file list to a supplied directory listing); failure patterns (swapped row/column convention hidden by a square shape, `A*B` for `A@B`, `inv` to solve, det as singularity test, wrong composition order) with detection signals.

## Unit 1 — Matrices as data tables and linear maps

- **L1:** a matrix as a rectangular table of numbers (rows, columns, entries, `m×n`); **matrix as data table** (`X: (n_samples, n_features)`); **matrix as a collection of vectors** (columns or rows); **matrix as a function**: `x ↦ Ax` takes `ℝⁿ → ℝᵐ`; **what "linear" means** (`T(u + v) = T(u) + T(v)`, `T(cu) = cT(u)`) with pictures; a concrete 2×2 map worked by hand on several vectors; **columns of `A` are the images of the standard basis vectors** (the key idea); NumPy: `np.array`, `.shape`, indexing rows/columns/blocks, `np.zeros/ones/eye`; shape reading aloud; ≥ 3 worked examples.
- **L2:** **`Ax` as a linear combination of the columns of `A`** (and as dot products with the rows) — both views, both verified; **affine vs linear** (`Wx + b` is affine; the bias breaks linearity — counterexample `T(0) ≠ 0`); **a dense layer** `y = Wx + b` with `W: (d_out, d_in)` and its row-sample form `Y = XWᵀ + b`; weight matrices and parameter counting (`d_out·d_in + d_out`, `[ILLUSTRATIVE]` sizes); **matrices as graphs** (adjacency/weight matrices — named, one example); **sparse vs dense** (`scipy.sparse` CSR/COO awareness, a memory comparison on a synthetic sparse matrix, no speed claims as facts); memory arithmetic (`m·n·itemsize`); dtype choices; reading a matrix expression in code or a paper (short method).
- **L3:** **proofs, written in full:** (a) **every linear map `T: ℝⁿ → ℝᵐ` equals `x ↦ Ax` for a unique matrix `A` whose `j`-th column is `T(eⱼ)`**; (b) `x ↦ Ax` is linear (from the definition of the product); (c) `T(0) = 0` for any linear map, and a linear map is determined by its values on a basis; (d) the set of `m×n` matrices is a vector space under entrywise operations (laws listed and proved from ℝ); (e) **a counterexample**: `x ↦ Ax + b` with `b ≠ 0` is not linear; **tool card** for `matscratch.core` (validated constructors, shape contract, row/column accessors, no mutation of inputs, `Fraction`/`float` element policy).
- **L4:** hostile inputs (ragged nested lists, object dtype, NaN/Inf, empty `0×n`, `1×1`, huge declared shape rejected before allocation); **row-vs-column convention bugs** diagnosed from symptoms (≥ 2 original case studies where a square shape hides a transposed `W`, each with a fix and regression test); **NumPy 1.x vs 2.x differences relevant here `[VERSION-SENSITIVE]`**; `np.matrix` vs `ndarray` (why to avoid `np.matrix`, `[VERIFY]` its status); mutation lab (transposed constructor, row/column swap in accessor, in-place mutation) with no surviving mutants.

## Unit 2 — Matrix–vector and matrix–matrix multiplication

- **L1:** the shape rule `(m×n)(n×p) = (m×p)` and why inner dimensions must match; **matrix–vector product** (rows·vector; combination of columns); **matrix–matrix product** entry by entry `C_{ij} = Σ_k A_{ik}B_{kj}` (1-based, with the 0-based Python loop shown); **multiplication is not commutative** (a 2×2 counterexample `AB ≠ BA`; sometimes `AB` exists and `BA` does not); **elementwise `*` vs matrix `@`** (the commonest beginner bug); NumPy `@`, `np.matmul`, `np.dot`, `np.einsum('ij,jk->ik')`; ≥ 3 worked examples including a non-square case.
- **L2:** **four views of `AB`**: (1) dot products of rows and columns, (2) each column of `AB` is `A` times a column of `B`, (3) each row of `AB` is a row of `A` times `B`, (4) **sum of outer products** `Σ_k a_k b_kᵀ` (columns of `A` × rows of `B`) — each shown and verified equal; **composition of maps**: `(AB)x = A(Bx)`, so the product is composition (applied right-to-left); **matrix powers** and repeated application; **block multiplication** (statement, a worked example); **cost**: derive that a naive `m×n · n×p` product uses `mnp` multiplications and `mp(n−1)` additions; **parenthesisation changes cost**: `(AB)x` vs `A(Bx)` with `[ILLUSTRATIVE]` sizes (derive the counts); **a low-rank factorisation `W ≈ UVᵀ`** reduces both parameters and cost (arithmetic only, `[ILLUSTRATIVE]`, no claim about any named method); a dense-layer forward pass for a batch; precision: float32 accumulation error vs float64 and exact `Fraction` on an adversarial example.
- **L3:** **proofs, written in full:** (a) **associativity `(AB)C = A(BC)`** (index proof, and via composition of maps); (b) **distributivity** over addition and compatibility with scalars; (c) **`AB` represents the composition `T_A ∘ T_B`** (using Unit 1(a)); (d) **the outer-product expansion `AB = Σ_k (column k of A)(row k of B)`**; (e) **non-commutativity and zero divisors**: `AB = 0` with `A ≠ 0`, `B ≠ 0` (explicit instance); `AB = AC` does **not** imply `B = C` (explicit instance); (f) `(A + B)² ≠ A² + 2AB + B²` in general; **matrix-chain cost**: for three matrices, the parenthesisation cost formulas and a small exhaustive check that the cheapest order can differ (`EVIDENCE ONLY`; recall S3 DP — link only); **tool card** for `matscratch.mul` (three loop orders `ijk`/`ikj`/`jki`, shape checks, exact `Fraction` mode, vs NumPy and SymPy oracles).
- **L4:** loop-order and memory-access discussion (**awareness; measured locally with stated variance; never asserted as fact**; `[VERIFY]`); **BLAS awareness** (NumPy delegates large products to optimised libraries; thread-count effects on determinism `[VERSION-SENSITIVE]`); hostile inputs (shape mismatch, empty inner dimension `m×0 · 0×p`, huge sizes rejected before allocation, mixed dtypes, integer overflow in `int32`); exhaustive verification over all pairs of small integer matrices (domain named and sized; `EVIDENCE ONLY`); mutation lab (swapped indices, `ikj` off-by-one, `*` instead of `@`, missing accumulation) with no surviving mutants; case study: a silently elementwise `*` that "worked" for a `(n,1)·(n,1)` shape (original reproduction).

## Unit 3 — Transpose, identity, and special matrices

- **L1:** the transpose `(Aᵀ)_{ij} = A_{ji}` and its shape effect; the **identity** `I` (`AI = IA = A`); **diagonal**, **symmetric** (`A = Aᵀ`), **triangular** (upper/lower), **permutation** (a reordering of rows/columns), **zero** and **scalar** matrices — each with a small example and a NumPy constructor (`np.eye`, `np.diag`, `np.triu`, `np.tril`, `.T`); the **trace** `tr(A) = Σ A_{ii}`; ≥ 3 worked examples.
- **L2:** **orthogonal matrices** (`QᵀQ = I`; columns orthonormal) and **what they do** (preserve lengths and dot products, so they rotate/reflect — verified numerically here, proved in L3); **why special structure matters in computation** (diagonal multiply costs `O(n)`; triangular solves cost `O(n²)`; derive the counts; symmetric matrices store half); **Gram matrix `XᵀX` and `XXᵀ`** (symmetric; entries are dot products — links S4B-01; a first look at covariance as a scaled `XᵀX` after centring, link `09-Probability-Fundamentals/08-covariance-and-correlation.md` — `[VERIFY]` the exact name in the tree); **outer product `uvᵀ`** as a rank-1 matrix (preview of Unit 9); symmetrising `(A + Aᵀ)/2` and testing symmetry with a tolerance; the **projection matrix `P = uuᵀ/(uᵀu)`** from S4B-01 lesson 03 now as a matrix (symmetric, `P² = P`); the **centring matrix** (`I − (1/n)11ᵀ`) applied to a data matrix, verified against column-mean subtraction.
- **L3:** **proofs, written in full:** (a) **`(AB)ᵀ = BᵀAᵀ`**; (b) `(Aᵀ)ᵀ = A`, `(A + B)ᵀ = Aᵀ + Bᵀ`; (c) **`tr(AB) = tr(BA)`** (and a counterexample that `tr(ABC) ≠ tr(ACB)` in general); (d) **`AᵀA` is symmetric and `xᵀAᵀAx = ‖Ax‖² ≥ 0`** (positive semidefinite; define; deeper theory is `4C-01`); (e) **orthogonal `Q` preserves norms and dot products: `‖Qx‖ = ‖x‖`, `(Qx)·(Qy) = x·y`**; **`Q⁻¹ = Qᵀ`**; (f) products of orthogonal matrices are orthogonal; (g) products of upper-triangular matrices are upper-triangular; (h) a permutation matrix is orthogonal; (i) `P = uuᵀ/(uᵀu)` satisfies `P = Pᵀ`, `P² = P`, `rank P = 1`; **tool card** for `matscratch.special` (predicates `is_symmetric`, `is_orthogonal`, `is_upper_triangular` with exact and tolerance modes; constructors; justified tolerances).
- **L4:** **numerical checks for structure** (a matrix that is symmetric only to rounding error; why `A == A.T` is the wrong test; `np.allclose` with stated `atol`; orthogonality drift after many multiplications and re-orthogonalisation as a `HEURISTIC`); **structure-exploiting algorithms** named (not taught): `scipy.linalg` triangular/banded/Cholesky solvers `[VERIFY]`; hostile inputs (non-square for symmetric tests, NaN, empty); **exhaustive verification** of the predicates over all `{−1,0,1}` `3×3` matrices against definition-literal references (`EVIDENCE ONLY`); mutation lab (testing `Aᵢⱼ = Aⱼᵢ` for `i < j` only up to the wrong bound; `QQᵀ` vs `QᵀQ` for non-square; tolerance direction) with no surviving mutants; case study: a "symmetric" covariance estimate that fails a Cholesky call due to asymmetry at `1e-17` (original synthetic reproduction with the fix).

## Unit 4 — Matrix shapes, broadcasting, and batching

- **L1:** **shape algebra** (`(m,n)@(n,p) → (m,p)`; `(m,n)@(n,) → (m,)`; `(n,)@(n,m) → (m,)`; `(n,)@(n,) → ()`) read aloud and predicted before running; row vector vs column vector vs 1-D array (`(n,)`, `(1,n)`, `(n,1)`); `reshape`, `.T`, `np.newaxis`, `keepdims`; **elementwise broadcasting** in plain words (a `(d,)` bias added to an `(n, d)` matrix); the **three most common shape bugs** (silent `(n,)+(n,1) → (n,n)`; transposed weight; wrong `axis`) each with a symptom and a one-line fix; ≥ 3 worked examples.
- **L2:** **broadcasting rules** stated precisely (align trailing dimensions; sizes must match or be 1) with worked cases; **batched matrix multiply** `(B, m, n) @ (B, n, p) → (B, m, p)` and batch-dimension broadcasting in `@` `[VERIFY]`; `einsum` as a shape-checked notation (`'bij,bjk->bik'`, `'ij,ij->i'`, `'bqd,bkd->bqk'`) — each derived from the index definition and checked against explicit loops; **a toy score matrix `QKᵀ`** `(n_q, d)·(n_k, d)ᵀ → (n_q, n_k)` with cost and memory arithmetic (`[ILLUSTRATIVE]`; shapes only, no claim about any model); **pairwise squared distances via `XXᵀ`** (links S4B-01 lesson 04 identity); a mini-batch through two dense layers, shapes annotated at each step; axis permutations (`transpose`, `swapaxes`, `moveaxis`); memory layout (C- vs Fortran-order, views from transposes — awareness, tested with `flags`); **a "shape contract" practice** (assert shapes at function boundaries; a decorator the learner writes).
- **L3:** **proofs/derivations, written in full:** (a) the **broadcasting result-shape rule** as a stated algorithm, with proof that it is well-defined and symmetric in its operands, plus an **exhaustive check over all shape pairs of rank ≤ 3 with dims ≤ 3 against a pure-Python reference** (`EVIDENCE ONLY`); (b) **batched matmul equals the loop over the batch** (definition-level); (c) **`einsum` of the stated patterns equals the explicit sums** (index proof); (d) **`(AB)ᵀ = BᵀAᵀ` applied to batches** (axis bookkeeping); **numerical/cost analysis**: flops and bytes for the toy score matrix; why materialising an `n×n` intermediate can dominate memory (arithmetic only); **tool card** for `matscratch.shapes` (a shape-inference function for `@`, broadcasting, and `einsum` patterns, with stable errors, verified against NumPy **and** the pure-Python reference).
- **L4:** **diagnosing silent broadcasting and transposition bugs from numerical symptoms** (≥ 3 original case studies, each with a failing test that catches it); `np.matmul` vs `np.dot` semantics for ≥ 3-D arrays `[VERIFY]`; `np.einsum` optimisation flag `[VERIFY]` (awareness); **NumPy 1.x vs 2.x differences** `[VERSION-SENSITIVE]`; hostile inputs (zero-size dimensions, mismatched batch sizes, object arrays); mutation lab (wrong axis in a reduction, `(n,)` vs `(n,1)` confusion, swapped batch dims, wrong broadcast alignment) with no surviving mutants.

## Unit 5 — Linear transformations: rotation, scaling, and shear

- **L1:** the 2D transformation gallery as matrices — **scaling** `diag(sx, sy)`, **rotation** `R(θ) = [[cos θ, −sin θ],[sin θ, cos θ]]` (derived from where `e₁` and `e₂` land, using the unit circle — link 4A `08-Geometry-and-Trigonometry/04-degrees-and-radians.md` and `06-unit-circle-and-basic-trigonometric-identities.md`), **shear** `[[1, k],[0, 1]]`, **reflection** across an axis; what each does to the **unit square**, a **grid**, and a **circle**; applying a matrix to several points by hand and in NumPy (`(N, 2)` row-sample vs `(2, N)` column convention — state which and show the transpose); **linear maps keep the origin fixed and keep straight lines straight and parallel lines parallel**; ≥ 3 worked examples; degrees vs radians trap (`np.cos` takes radians).
- **L2:** **composition and order**: `T₂∘T₁` is `A₂A₁` (right-to-left), with the worked demonstration that **rotate-then-shear ≠ shear-then-rotate**; **the area scale factor equals `|det|`** (preview, with a numerical check using the shoelace formula; proof in Unit 7); **orthogonal matrices as rotations/reflections** (link Unit 3); **projection as a (non-invertible) linear map** (link S4B-01 lesson 03); **anisotropic scaling and distances** (a scaling that changes nearest neighbours — original synthetic example; link S4B-01 lesson 04); **homogeneous coordinates** so that translation becomes a matrix (the `3×3` form; why translation is not linear but is affine in 2D); a data-augmentation-style rotation of a synthetic `(N, 2)` point cloud; **how a matrix changes a cloud's covariance** (`A Σ Aᵀ`, stated and verified numerically on seeded data; **forward-link to `03-Eigenvalues-SVD-and-Low-Rank-Structure` and `09-Probability-Fundamentals`**; the proof belongs to 4C); **a 3D rotation about a coordinate axis** (matrix; awareness of non-commutativity; no Euler-angle theory).
- **L3:** **proofs, written in full:** (a) `R(θ)` is orthogonal with `det = 1`; (b) **`R(α)R(β) = R(α + β)`** (derived from matrix multiplication, which **proves** the angle-addition identities for sine and cosine — and say so); (c) **`R(θ)⁻¹ = R(−θ) = R(θ)ᵀ`**; (d) a linear map sends lines to lines (or to a point) and preserves parallelism and the origin; (e) the **shear has determinant 1 and is not orthogonal** (it preserves area but not lengths — explicit instance); (f) a reflection is orthogonal with `det = −1`; (g) a **minimal counterexample** that `T₂∘T₁ ≠ T₁∘T₂`; (h) **uniform scaling commutes with every matrix; non-uniform scaling does not** (instance); **tool card** for `ltviz.maps` (constructors for the gallery, composition with exact `Fraction` entries where angles are Pythagorean-triple rotations — **e.g., cos θ = 3/5, sin θ = 4/5 — as an exact oracle; general angles use float with a stated tolerance**).
- **L4:** **accumulated floating-point drift when composing many rotations** and re-orthogonalisation (`HEURISTIC`, measured); **the distinction between a coordinate change and moving the points** (active vs passive; `R` vs `Rᵀ` — an original case study where the wrong one flips a rotation); **eigen-directions previewed** (directions a map only stretches — a numerical look, formal theory in `03-Eigenvalues-SVD-and-Low-Rank-Structure/01-eigenvalues-and-eigenvectors.md`); **singular maps** (a projection collapses the plane to a line: non-invertible; link Units 7–9); hostile inputs (NaN in points, wrong shapes, `(N,2)` vs `(2,N)` mix-ups); mutation lab (sign of `sin` flipped, `R` vs `Rᵀ`, degrees passed as radians, composition order reversed) with no surviving mutants.

## Unit 6 — Solving Ax = b and Gaussian elimination

- **L1:** a system of linear equations as **`Ax = b`** (link 4A `04-…/11`, `12`, `13`, and the bridge `14-three-variable-systems-and-the-bridge-to-matrices`); the **augmented matrix** `[A | b]`; the **three elementary row operations** (swap, scale, add a multiple of one row to another) and **why they do not change the solution set**; **forward elimination to row-echelon form** and **back substitution**, by hand on `2×2` and `3×3` systems; **pivots**; the **three outcomes** (exactly one solution, none, infinitely many) seen in the eliminated form; checking a solution by substitution; `np.linalg.solve` for a square system; ≥ 3 worked examples.
- **L2:** **reduced row-echelon form (Gauss–Jordan)**; **free and pivot variables and a parametric description of infinitely many solutions**; **inconsistency detection** (a row `0 = c`, `c ≠ 0`); **rank and solvability** (link Unit 9): the system is consistent iff `rank A = rank [A | b]`; **partial pivoting** (why swapping to the largest pivot matters, with a worked tiny-pivot example where naive elimination loses all accuracy in float64 and the pivoted version does not — **verified against an exact `Fraction` solve**); **residuals** `r = b − Ax̂` as the practical check and **why a small residual does not prove a small error** (a worked ill-conditioned example; link Unit 8); `np.linalg.solve` vs `np.linalg.lstsq` for square, overdetermined, and underdetermined systems (statement of what each returns; least-squares theory deferred to `14-Linear-Models-Mathematics`); the cost of elimination (derive `≈ (2/3)n³` flops by counting, `[VERIFY]` against a reference), and why you solve many right-hand sides by factorising once (**LU named and previewed; the theory is `4C-01` lesson 05 — `[VERIFY]` the filename in the tree**).
- **L3:** **proofs, written in full:** (a) **elementary row operations preserve the solution set** (each is invertible); (b) **correctness and termination of forward elimination to echelon form** (induction on columns); (c) **back substitution solves an upper-triangular system with non-zero diagonal** and gives uniqueness; (d) **classification of solution sets by pivot structure** (a self-contained proof of the Rouché–Capelli statement from the elimination process); (e) **the tiny-pivot counterexample**, a concrete system where unpivoted elimination fails in float64 and its error computed exactly; (f) **elimination as left-multiplication by elementary matrices** (each row op is `E·A`; product gives an `LU`-style factorisation — statement and a worked `3×3` example, theory deferred); **numerical analysis**: backward error, residual vs forward error (definition-level; the stability of partial pivoting `CITED [VERIFY]` with the standard growth-factor caveat stated, not proved); **tool card** for `gesolve` (exact `Fraction` elimination as the oracle; float elimination with partial pivoting; RREF; rank; solution-set classification; parametric solution; step trace; stable errors; verified against `sympy` and `scipy.linalg` on stated domains).
- **L4:** **ill-conditioned systems**: the Hilbert matrix as an original demonstration (exact vs float error growth with `n`, `[VERIFY]` the standard facts), the **condition number as an error amplifier** (defined in Unit 8; theory `CITED [VERIFY]`); **singular and near-singular systems** and what `np.linalg.solve` does (raises `LinAlgError` for exactly singular, may return large garbage for near-singular — **demonstrated and tested, not asserted**); **rank-deficient least-squares** (named only); structured systems (triangular, banded) named; hostile inputs (zero rows, duplicated equations, huge coefficients, sizes rejected before allocation); **exhaustive verification** of the classifier over all `2×2` and `3×3` integer systems with coefficients in `{−1,0,1}` against `sympy` (domain named and sized; `EVIDENCE ONLY`); mutation lab (no row swap when the pivot is zero; wrong pivot choice; forgetting to update `b`; off-by-one in back substitution; wrong tolerance) with no surviving mutants.

## Unit 7 — Determinants and invertibility

- **L1:** the determinant of a `2×2` matrix `ad − bc` and what it measures — **the signed area scale factor of the map** (unit square → parallelogram; sign = orientation flip); the `3×3` determinant (cofactor/Sarrus-free expansion by hand) and **volume**; **`det = 0` means the map collapses space** (flattens a plane to a line); invertible ⇔ `det ≠ 0` (statement and the 2×2 case); NumPy `np.linalg.det`; ≥ 3 worked examples.
- **L2:** **properties used in practice**: `det(AB) = det(A)det(B)`, `det(Aᵀ) = det(A)`, `det(cA) = cⁿ det(A)`, `det(Aⁿ) = det(A)ⁿ`, `det(A⁻¹) = 1/det(A)`; **the determinant of a triangular matrix is the product of its diagonal**; **computing a determinant by elimination** (product of pivots with sign for each swap) vs **cofactor expansion** (cost `O(n!)`-style growth derived vs `O(n³)`); the determinant and **orientation/area** for the Unit 5 gallery (rotation `1`, shear `1`, reflection `−1`, scaling `sx·sy`, projection `0`); **`log|det|` and `slogdet`** (why `slogdet` exists: overflow/underflow of `det` for large `n` — demonstrated; where `log det` appears downstream — Gaussian log-likelihood, named, deferred to `4C-05`); **why the determinant is a poor numerical test for singularity** (taught explicitly): **`det(0.1·Iₙ) = 10⁻ⁿ` is tiny yet the matrix is perfectly well-conditioned, and large-determinant matrices can be nearly singular** — each demonstrated and the correct tools named (rank via SVD, condition number).
- **L3:** **proofs, written in full:** (a) the 2×2 determinant is the **signed area** of the image of the unit square; (b) **`det(AB) = det(A)det(B)`** — **prove it for `2×2` by direct computation; for general `n` either give a complete proof (e.g., via elementary matrices) or state it `CITED [VERIFY]` and say which**; (c) `det` of a triangular matrix; (d) **effect of each elementary row operation on the determinant** (swap flips the sign, scaling a row scales it, adding a multiple of a row leaves it unchanged) and the **correctness of determinant-by-elimination**; (e) **`det(A) = 0` ⇔ the columns are linearly dependent ⇔ `A` is singular** for square `A` (proof via elimination, linking Units 6 and 9; uses S4B-01 lesson 05); (f) `det(cA) = cⁿ det(A)`; (g) **the "tiny det, healthy matrix" counterexample** with exact numbers; **numerical analysis**: relative error of `det` computed by elimination vs by cofactor on a small float example; **tool card** for `gesolve.det` (exact `Fraction` determinant by elimination; float with partial pivoting; `slogdet`-style sign/log output; verified against `sympy.Matrix.det` and a cofactor reference on a stated domain).
- **L4:** **overflow/underflow** (`det` of a `500×500` random matrix; `slogdet` fix; capped sizes); **Jacobian determinants and change of variables** named only (forward-link `07-Multivariable-Calculus-and-Gradients` and `4C-02`; **do not teach**); **orientation-aware code** (a reflection flipping handedness in a toy geometry pipeline — original reproduction); hostile inputs (non-square, empty `0×0` convention — state it: `det` of the empty matrix is `1` by convention `[VERIFY]` in NumPy; NaN); **exhaustive verification** of the exact determinant over all `{−1,0,1}` `3×3` matrices against the cofactor reference and `sympy` (domain named and sized; `EVIDENCE ONLY`); mutation lab (sign error on a swap; forgetting a row-scaling factor; Sarrus applied to a `4×4`; `det(A+B)` used as `det A + det B`) with no surviving mutants.

## Unit 8 — Matrix inverse and when it fails

- **L1:** the inverse as the "undo" map (`A⁻¹A = AA⁻¹ = I`); **the `2×2` inverse formula** `(1/(ad−bc))·[[d, −b],[−c, a]]` (derived, not memorised); **an inverse exists only for square matrices with `det ≠ 0`**; singular matrices and why no inverse can exist (the map collapses information: two inputs, one output); `np.linalg.inv`, and the **`LinAlgError` for exactly singular** input; using the inverse to solve `Ax = b` by hand in a tiny case; ≥ 3 worked examples.
- **L2:** **computing the inverse by Gauss–Jordan on `[A | I]`** (by hand and in code); **the invertible-matrix equivalences for square `A`** (inverse exists ⇔ `det ≠ 0` ⇔ rank `n` ⇔ columns independent ⇔ `Ax = b` has a unique solution for every `b` ⇔ `Ax = 0` has only `x = 0`) as a **checklist with a worked example for each**; **`(AB)⁻¹ = B⁻¹A⁻¹`** (and the reversal order trap), `(Aᵀ)⁻¹ = (A⁻¹)ᵀ`, `(cA)⁻¹ = c⁻¹A⁻¹`; **special inverses** (diagonal, orthogonal `Q⁻¹ = Qᵀ`, rotation, `2×2`); **do not form `A⁻¹` to solve `Ax = b`**: the reasons (cost, accuracy, structure loss) with a **measured, seeded comparison of `inv(A) @ b` vs `solve(A, b)` residuals on ill-conditioned and well-conditioned matrices (sizes capped; sample sizes and variance stated)**; **the condition number** `κ(A) = ‖A‖·‖A⁻¹‖` (2-norm; defined here at an intuitive level, **full theory deferred to `03-Eigenvalues-SVD-and-Low-Rank-Structure/05-matrix-norms-frobenius-and-spectral.md` and `4C-01`**) and the rule of thumb "relative error can be amplified by up to `κ`" stated as `CITED [VERIFY]`; **regularisation `A + λI`** as a way to make a matrix invertible (preview of `14-Linear-Models-Mathematics/05-ridge-and-lasso-regularization-mathematics.md`); **pseudo-inverse** named, with the full-column-rank formula `(XᵀX)⁻¹Xᵀ` shown **only as a preview** (theory: Module 03 and Module 14).
- **L3:** **proofs, written in full:** (a) **uniqueness of the inverse** and that a one-sided inverse of a square matrix is two-sided (**prove it, or state `CITED [VERIFY]` and say which**); (b) **`(AB)⁻¹ = B⁻¹A⁻¹`**; (c) the **2×2 formula**; (d) **the chain of equivalences** for square `A` (the elimination-based proof tying Units 6, 7, and 9 together, stated with exactly which lemmas it uses); (e) **`A + λI` is invertible for symmetric positive-semidefinite `A` and `λ > 0`**, via `xᵀ(A + λI)x ≥ λ‖x‖² > 0` for `x ≠ 0` (uses Unit 3(d)); (f) **a singular matrix is not invertible** (two vectors map to one image); (g) **an explicit near-singular example** with its exact inverse showing entries of size `~1/ε`; **numerical analysis**: the forward-error bound `‖δx‖/‖x‖ ≤ κ(A)·‖δb‖/‖b‖` — **statement `CITED [VERIFY]` and a numerical demonstration, not a proof, unless you give one**; **tool card** for `gesolve.inverse` (Gauss–Jordan exact and float; singularity detection with a condition-number estimate and stable errors; verified against `sympy.Matrix.inv` and `scipy.linalg.inv` on stated domains).
- **L4:** **near-singular behaviour**: `inv` returns garbage without an error — **a seeded, reproducible demonstration** with detection via `np.linalg.cond` (`[VERIFY]` the definition and default norm); condition number growth for Vandermonde/Hilbert-style matrices (original construction; sizes capped); **solving with the Cholesky/QR/LU factorisations named** (`scipy.linalg.solve`, `assume_a`, `[VERIFY]`; theory deferred to `4C-01`); **the normal equations square the condition number** (statement `CITED [VERIFY]` with a numerical check; forward-link `14-Linear-Models-Mathematics/02-the-normal-equation-and-closed-form-solution.md`); **rank-deficient design matrices** (collinear features; the Gram matrix `XᵀX` singular — original case study with diagnosis via rank and condition number, and fixes: drop a feature, add `λI`, use `lstsq`); hostile inputs (non-square, zero, NaN, `inf`); mutation lab (reversed order in `(AB)⁻¹`; missing row swap; dividing by `det` before checking zero; wrong tolerance direction in the singularity test) with no surviving mutants.

## Unit 9 — Rank and column-space intuition

- **L1:** the **column space** of `A` = all vectors `Ax` = the span of its columns (link S4B-01 lesson 05) — **the set of right-hand sides `b` for which `Ax = b` is solvable**; the **row space**; **rank = the number of independent columns = the number of pivots**; a first look at rank on `2×2` and `3×3` examples by elimination; **full rank**, **rank-deficient**; **rank is at most `min(m, n)`**; the **outer product `uvᵀ` has rank 1**; `np.linalg.matrix_rank`; ≥ 3 worked examples.
- **L2:** **rank and solvability** (`Ax = b` solvable ⇔ `b ∈ col(A)` ⇔ `rank A = rank [A | b]`); **rank and the number of solutions** (free variables = `n − rank` when consistent; link Unit 6); **the null space intuition** (`Ax = 0` — vectors the map sends to zero; **formal definition, subspaces, and the rank–nullity theorem are `4C-01`**; here a worked intuition with the count `n − rank`); **row rank = column rank** (statement, a worked example, and the proof in L3 or `CITED [VERIFY]`); **rank of a product** (`rank(AB) ≤ min(rank A, rank B)`) and what it means for stacking layers (a **bottleneck**: a product through a width-`r` layer has rank `≤ r` — arithmetic and an original demo, no model claims); **low-rank matrices as sums of rank-1 outer products** (`Σ_{k=1}^{r} u_k v_kᵀ`; a seeded low-rank-plus-noise matrix; **forward-link `03-Eigenvalues-SVD-and-Low-Rank-Structure/04-low-rank-approximation.md`**); **parameter and cost savings of a rank-`r` factorisation** (`(m + n)r` vs `mn`, `[ILLUSTRATIVE]`; a generic mention that low-rank parameterisations are used in practice `[VERIFY]`, **no named-method claims**); **rank in data**: redundant/collinear features, one-hot dummy dependence (link S4B-01 lesson 05), duplicate rows, and "how many independent directions does this table really have?".
- **L3:** **proofs, written in full:** (a) **column space is closed under addition and scalar multiplication** (and `Ax = b` solvable ⇔ `b ∈ col A`); (b) **`rank(AB) ≤ min(rank A, rank B)`**; (c) **`rank(AᵀA) = rank(A)`** (via `Ax = 0 ⇔ AᵀAx = 0`, using `xᵀAᵀAx = ‖Ax‖²` from Unit 3 — and say why this matters for the normal equations); (d) **rank equals the number of pivots in the echelon form** (elimination does not change the row space; pivot rows form a basis) and **row rank = column rank** (**give the proof via RREF or state `CITED [VERIFY]` and say which**); (e) **rank of an outer product is 1** and a sum of `r` rank-1 matrices has rank `≤ r`; (f) **`rank A = n` (full column rank) ⇔ `Ax = 0` has only the trivial solution ⇔ the columns are independent**; **numerical analysis**: **numerical rank is a tolerance decision** — a worked example where `matrix_rank` returns different values for different tolerances; the **default tolerance formula `S.max() · max(M, N) · eps`** stated `CITED [VERIFY]` with a local check against the installed version; singular-value-based rank previewed (SVD is Module 03); **tool card** for `gesolve.rank` (exact rank over `Fraction` by elimination; float rank with stated tolerance and the singular values reported where available; column-space membership; verified against `sympy.Matrix.rank` on stated domains).
- **L4:** **near-rank-deficiency and what to do** (a nearly collinear design matrix: the rank at several tolerances, the condition number, and the effect on a solve — original reproduction); **rank in float32 vs float64** (measured); **rank decisions in pipelines** (a unit test that asserts the full rank of a design matrix with an explicit tolerance and fails loudly; a monitoring check, awareness only); **exhaustive verification** of the exact rank tool over all `{−1,0,1}` `3×3` (and a capped `3×4`/`4×3`) matrices against `sympy` (domain named and sized; `EVIDENCE ONLY`); hostile inputs (zero matrix, single row/column, wide and tall matrices, NaN); mutation lab (off-by-one in pivot counting; skipped row swap; wrong tolerance direction; counting zero rows as pivots) with no surviving mutants; case study: a regression "working" in float but unstable because two columns were nearly dependent (original reproduction with diagnosis and fix).

## Unit 10 — Practice questions (`practice-questions.md`) — see Section 7

## Unit 11 — Projects index (`Projects/README.md`) — see Section 9

## Unit 12 — Project: Matrix operations from scratch (`Projects/01-matrix-operations-from-scratch.md`) — see Section 8A

## Unit 13 — Project: Gaussian elimination solver (`Projects/02-gaussian-elimination-solver.md`) — see Section 8B

## Unit 14 — Project: Linear transformation visualizer (`Projects/03-linear-transformation-visualizer.md`) — see Section 8C

# 7. UNIT 10 — PRACTICE QUESTIONS (REQUIREMENTS)

**Target file:** `practice-questions.md`. Not the four-level skeleton; use this structure:
1. **How to use this set** (hand first, then NumPy, then oracle; the 80/60 gate; honest self-scoring; AI-use disclosure).
2. **The question bank: ≥ 200 original items**: **≥ 18 per lesson (Units 1–9; 162 total)**, plus **≥ 16 cross-lesson integration items**, **≥ 12 ML-scenario/critique items** (an original code snippet or plan with a bug to find: shape bug, convention swap, `inv`-to-solve, det-as-test, wrong rotation order, rank misjudgement), and **≥ 10 coding tasks with pytest tests and independent oracles**. Difficulty spread per lesson: ~30% Easy, ~45% Medium, ~25% Hard. **≥ 20% of items are "trap" items** (non-commutativity, elementwise vs matrix product, transposed convention, singular/near-singular, zero pivot, tolerance).
3. **A machine-readable key block** (JSONL) per lesson, with hand solutions, registered oracle names, and error-model distractor rationales; matrix keys as exact `Fraction` strings.
4. **≥ 20 parameterised templates** (seeded) with exact `Fraction` keys (matrix products, `2×2`/`3×3` inverses and determinants, elimination, rank, rotation compositions with rational `cos/sin`), so the learner can regenerate fresh practice.
5. **≥ 8 proof-completion/short-proof items** with rubrics (associativity, `(AB)ᵀ = BᵀAᵀ`, `R(α)R(β) = R(α+β)`, elementary row operations preserve solutions, `(AB)⁻¹ = B⁻¹A⁻¹`, `rank(AᵀA) = rank(A)`, `det` of a triangular matrix, `tr(AB) = tr(BA)`).
6. **A `qcheck` tool** (Tool card; verifies every key against its oracle on the stated domain and seeded parameters; audits distractors against error models; flags duplicate options, ambiguous keys, missing hand solutions, unknown fields; deterministic; hostile-pool tests; mutation lab with no surviving mutants).
7. **Scoring and gate rules**, remediation mapping (a missed item → lesson sections), and **small-n cautions** (an 18-item lesson score has wide uncertainty; a Wilson interval example `CITED [VERIFY]`; no predictive claims).
8. **Every item tests only content taught in its linked lesson** (a later audit pass checks this).

# 8A. UNIT 12 — PROJECT 01: MATRIX OPERATIONS FROM SCRATCH (REQUIREMENTS)

**Target file:** `Projects/01-matrix-operations-from-scratch.md`. Apply the four levels and N.0–N.14. It consolidates Units 1–4 into the local package **`matscratch`**: a **pure-Python (no NumPy in the core)** matrix library with exact `Fraction` and `float` element modes, with NumPy/SymPy used **only as independent oracles**. It teaches no new mathematics; it teaches **building a verified numerical library**.

**Required components:**
1. **API (≥ 22 operations):** validated constructors (`from_rows`, `zeros`, `identity`, `diag`, `from_columns`); `shape`, row/column access, slicing; add, subtract, scalar multiply; **matrix–vector and matrix–matrix multiply with three loop orders**; elementwise (Hadamard) product as a *separate, clearly named* operation; power by repeated squaring (derive the multiplication count); transpose; trace; `is_symmetric`, `is_orthogonal`, `is_upper_triangular`, `is_diagonal` (exact and tolerance modes); block assembly; Frobenius-style norm (preview); outer product; conversion to/from NumPy arrays at the edge only.
2. **Contracts:** documented shapes, runtime preconditions, stable error codes (`E-MATSCRATCH-NNN`), **no mutation of caller inputs**, deterministic, element-type policy (no silent `int`→`float`), size caps checked before allocation.
3. **Oracles:** every operation has an independent oracle (`Fraction`/`sympy` for exact mode; NumPy/SciPy via a different path for float mode); no oracle imports the code under test.
4. **Tests:** exhaustive small-domain (e.g., all pairs of `2×2` integer matrices with entries in `[−2, 2]`; all `3×3` over `{−1,0,1}` for predicates), seeded random with stated tolerances, adversarial inputs, and algebraic **property tests** (associativity, `(AB)ᵀ = BᵀAᵀ`, `tr(AB) = tr(BA)`, `(A+B)C = AC+BC`; optional Hypothesis).
5. **Performance study (measurement hygiene):** a local, seeded benchmark of the three loop orders and of `matscratch` vs NumPy for capped sizes, reporting medians **with spread and the machine-state caveats, and never presented as a general fact**; a cost-model check comparing derived operation counts to counted operations.
6. **Mutation lab** (swapped indices, off-by-one in the accumulation, `*` for `@`, transposed result, missing shape check, wrong tolerance direction) with **no surviving mutants**, plus a **regression guard**.
7. **Reproducibility:** `matscratch verify` (supports `--quick`; disk cap; PASS/FAIL list); `pyproject.toml` (local editable install); fresh-`venv` contract; no network after install.
8. **Documentation:** package-layout mermaid diagram; API reference from docstrings; a **library card** (scope, tested domains, tolerances, versions, limits, "teaching library — not production numerics").
9. **Report template** for the learner's own results (oracle-agreement table, mutation score, benchmark with spread, issues found, AI-use disclosure, integrity statement) with the blank template and clearly labelled `[ILLUSTRATIVE]` synthetic example; **never fabricated results**.

**Rubric (provide in full):** traceability; correctness (oracle agreement); contracts and error handling; test and mutation strength; measurement honesty; reproducibility; documentation and library card; integrity statement. Pass uses the 80/60 gate. **Stretch:** Strassen's algorithm for `2^k` sizes as an optional exploration with a correctness oracle and an honest cost discussion; a peer code review.

# 8B. UNIT 13 — PROJECT 02: GAUSSIAN ELIMINATION SOLVER (REQUIREMENTS)

**Target file:** `Projects/02-gaussian-elimination-solver.md`. Apply the four levels and N.0–N.14. It builds **`gesolve`**: a solver that works in **exact `Fraction` arithmetic** and in **float with partial pivoting**, **explains itself** step by step, and reports numerical health.

**Required components:**
1. **Core:** forward elimination, back substitution, RREF, **solution-set classification** (unique / none / infinite with a **parametric solution**), rank, determinant, inverse (Gauss–Jordan), and a **row-operation trace** (human-readable "show your work" output, with each operation labelled `R_i ← R_i − c·R_j`).
2. **LU as a by-product (preview only):** record the multipliers and verify `PA = LU` numerically and exactly on the test set (**theory deferred to `4C-01`; say so**).
3. **Numerical-health report:** residual `‖Ax̂ − b‖`, condition-number estimate (via a documented method, stated limits), warnings for near-singularity, and a **comparison of exact vs pivoted-float vs unpivoted-float** on the tiny-pivot and Hilbert families.
4. **Oracles and tests:** exact `Fraction` solution as the oracle for float mode; `sympy` (`linsolve`, `Matrix.rank/det/inv`) and `scipy.linalg` as independent cross-checks; **exhaustive classification test over all `2×2` and `3×3` integer systems with coefficients in `{−1, 0, 1}` (domain named and sized; `EVIDENCE ONLY`)**; seeded random well-conditioned systems; adversarial systems (zero pivots forcing swaps, duplicated equations, inconsistent rows, huge/tiny coefficients).
5. **Mutation lab** (no row swap on a zero pivot; wrong pivot selection; forgetting to update `b`; off-by-one in back substitution; wrong rank counting; wrong tolerance direction) with **no surviving mutants**, plus a **regression guard**.
6. **CLI and file format:** reads a strict, versioned, human-readable JSON/CSV system (unknown fields rejected, size caps, no NaN/inf by default); writes results atomically; `gesolve verify --quick`; disk cap.
7. **ML application:** a **collinear design-matrix diagnosis** (`XᵀX` singular; rank, condition number, and the fixes) on a seeded synthetic dataset, with an honest interpretation (**no real data, no model claims**).
8. **Documentation, library card, and report template** as in Unit 12 (no fabricated results).

**Rubric (provide in full)** analogous to Unit 12, plus "numerical-health honesty". **Stretch:** a banded/tridiagonal solver and its cost comparison; a peer review.

# 8C. UNIT 14 — PROJECT 03: LINEAR TRANSFORMATION VISUALIZER (REQUIREMENTS)

**Target file:** `Projects/03-linear-transformation-visualizer.md`. Apply the four levels and N.0–N.14. It builds **`ltviz`**: a tool that makes 2D linear maps **visible** and ties geometry to the algebra of Units 1–9.

**Required components:**
1. **Gallery and composer:** scaling, rotation, shear, reflection, projection, arbitrary `2×2`, and composition in either order, shown on the unit square, a grid, a circle, and a seeded point cloud; (matplotlib with a **text/ASCII/SVG fallback**, and a **text alternative for every figure**).
2. **Quantities displayed and verified:** the images of `e₁`, `e₂` (the columns), **determinant as signed area** (checked against an independent **shoelace-formula** area of the transformed unit square), orientation flips, and rank (a rank-1 map collapsing the plane onto a line).
3. **Composition-order demonstration** (`T₂∘T₁` vs `T₁∘T₂`) with side-by-side plots and the matrix products verified exactly.
4. **Exact mode:** rotations by angles with rational `cos/sin` (Pythagorean pairs) verified with `Fraction`; float mode with stated tolerance for general angles.
5. **Optional forward previews (clearly labelled as previews):** eigen-directions (lines a map only stretches) and the **circle → ellipse** image whose axes are the singular directions (`03-Eigenvalues-SVD-and-Low-Rank-Structure`; **no theory taught here**); the effect of a matrix on a cloud's covariance (`AΣAᵀ`) verified numerically on seeded data.
6. **Verification:** every plotted/printed number matches an independent oracle; seeds fixed; `ltviz verify --quick`; mutation checks on the geometry code (sign of `sin` flipped, `R` vs `Rᵀ`, degrees-as-radians, composition order reversed); regression guard; disk caps.
7. **Accessibility and honesty:** every figure has a text description; the findings report states what each visualisation shows and **does not show**; no claims about real models or datasets.
8. **Documentation, library card, and report template** as in Unit 12 (no fabricated results).

**Rubric (provide in full)** analogous to Unit 12, plus "visual–numerical agreement" and "accessibility". **Stretch:** an SVG-only renderer; a 3D rotation demo with an explicit non-commutativity check; a peer review.

# 9. UNIT 11 — PROJECTS README (REQUIREMENTS)

**Target file:** `Projects/README.md`. Not the four-level skeleton. Use this structure:
1. What the module's three projects are and how they consolidate Units 1–9.
2. Index of the three projects (project | purpose | key skills | verification method | links with exact repo paths).
3. How to choose and sequence them (Project 1 after Units 1–4; Project 2 after Units 6–9; Project 3 after Unit 5 and ideally Units 7 and 9; fast-track rules and required evidence).
4. Project rules (original/synthetic data, seeds, `--quick`, disk caps, no network, AI disclosure, honest results, the numerical policy; size caps).
5. Definition of done (checkable) and the evidence folder structure.
6. How the projects feed the Stage 4B `mlmath` library (link `00-Stage-4-Overview/Projects/01-math-for-ml-notebook-library.md`) and later modules (03, 04, 07, 14).
7. A review checklist for self and peer.
8. **Promises vs delivery:** Unit 11 promises nothing Units 12–14 do not deliver.
Include **3 self-check questions**.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/matscratch/mul.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ (NumPy 1.x/2.x differences tagged), type hints on public functions, shape annotations on every array, runtime precondition checks, **no mutation of caller inputs**.
4. Every method and tool has its Method/Tool card before the code.
5. Conventions are stated once and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; `axis`, `dtype`, and the row/column convention stated wherever relevant.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test); tests pass on the reference and fail on a deliberately broken variant.
8. **No unproven claims** about learning, hiring, interviews, performance, or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in Appendix F.
10. **Proofs are written in full where Section 6 requires them.** A counterexample is a disproof; agreement on examples is not a proof.
11. Library internals (BLAS, LAPACK routines, threading, loop-order performance) are **not guarantees**: teach the learner to test the behaviour; tag `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** sizes validated before allocation; exhaustive oracles capped in code; files confined to the project directory; no unbounded loops/allocations; default `n ≤ 512`, `--quick` `n ≤ 128`.
13. **Security:** no `pickle`/`eval`/`exec` on untrusted text; strict loaders; oracles looked up by name in a fixed registry; `allow_pickle=False`.
14. No secrets, no paid APIs, no downloaded content; `clean` targets list what they remove and never delete the learner's evidence log.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `np.random.default_rng(seed)` / `random.Random(seed)`; no system-clock reads inside logic; benchmark timing is read only at the CLI edge and reported with spread.

# 11. SCOPE GUARD

Never re-teach a 4A or S4B-01 lesson. Never teach eigenvalues/SVD, matrix calculus, formal subspaces/rank–nullity, full LU/QR/Cholesky theory, or least-squares/regression beyond the one-line previews named in Section 6. Link instead.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, standards, release notes | **NumPy docs**: `numpy.matmul`, `numpy.dot`, `numpy.einsum`, broadcasting, `numpy.linalg` (`solve`, `inv`, `det`, `slogdet`, `lstsq`, `matrix_rank`, `cond`, `LinAlgError`), `numpy.finfo`, `numpy.isclose`, `numpy.random.Generator`, the **NumPy 2.0 migration guide**; **SciPy docs**: `scipy.linalg` (`solve`, `lu`, `inv`, `det`), `scipy.sparse`; **SymPy docs**: `Matrix.rank/det/inv/rref`, `linsolve`, `Rational`; **Python docs**: `fractions`, `math`, `random`; **Python tutorial "Floating Point Arithmetic: Issues and Limitations"**; **IEEE 754** (by name); **LAPACK Users' Guide** (by name, for what `gesv`-style solvers do — `[VERIFY]`) | API behaviour, defaults, versions |
| **T2** | Established textbooks and peer-reviewed papers (cite title/author/topic; **never invented page numbers, DOIs, or URLs**) | Strang, *Introduction to Linear Algebra* and *Linear Algebra and Its Applications*; Axler, *Linear Algebra Done Right*; Deisenroth, Faisal & Ong, *Mathematics for Machine Learning* (matrices, linear mappings, systems, rank); Boyd & Vandenberghe, *Introduction to Applied Linear Algebra* (VMLS); Horn & Johnson, *Matrix Analysis*; Golub & Van Loan, *Matrix Computations* (elimination, pivoting, conditioning, flop counts); Trefethen & Bau, *Numerical Linear Algebra* (conditioning, stability, backward error); Higham, *Accuracy and Stability of Numerical Algorithms*; Goldberg (1991) on floating point; Harris et al. (2020), "Array programming with NumPy", *Nature* | Definitions, theorems, cited results |
| **T3** | Reputable university lecture notes, engineering write-ups | Pointer only, canonical only, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your memory) | — | **Never sufficient.** Convert to a derivation, an oracle check, or `[VERIFY]` |

Rules:
- You are **writing from knowledge, not consulting sources live**, unless you actually have browsing and use it. If you browse, record the URL and access date in Appendix A; otherwise state "written from knowledge; verify against current documentation." **All T1/T2 citations are `[VERIFY]`.** Give a URL only if certain it is canonical.
- **Computation is a source:** a hand derivation re-checked by an independent exact oracle is stronger than any citation; prefer it.
- **Do not reproduce or closely paraphrase copyrighted text**; name theorems and give your own statements and proofs.
- **Do not fabricate** version numbers, timings, benchmark or speed figures, success rates, hiring/interview statistics, employer requirements, "N% of …" figures, constants or formulas without a derivation or `[VERIFY]` (including the `(2/3)n³` flop count, the default `matrix_rank` tolerance, and any growth-factor or condition-number bound), library internals as guarantees, quotes, or anecdotes. If a number is needed, derive it from a stated command or label it `[ASSUMPTION]`/`[ILLUSTRATIVE]`.
- **The repository tree is the source of truth** for names, counts, and paths; report conflicts as `OPEN`.
- Keep a running **Claim Register** (12.3).

## 12.2 Mandatory multi-pass self-audit (after drafting, before delivering each part)

Run in order; fix every defect.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 15 units, every required section (Sections 5–9), every topic and proof in Section 6, L1–L4, ≥ 3 worked examples at each of L1 and L2, the ≥ 200-item bank, all three projects' full component lists. | Any missing section/topic/proof/example/item. |
| 2 | **Convention consistency** | Claims, correctness, shape/row-column/`Wx`-vs-`XWᵀ`/index notation, degenerate-case policy, numerical policy, original-content, item format, data/security, integrity, gate conventions identical in every unit, tool, item, test. | Any mixed or silently changed convention. |
| 3 | **Claims honesty** | Every claim on learning, hiring, performance, or role requirements is cited `[VERIFY]` with limits, `[JUDGEMENT]`/`[ASSUMPTION]`, verifiable, or absent; no speed/benchmark figures as facts. | Unsupported claim. |
| 4 | **Traceability** | Every objective → lesson, practice items, project component; Unit 11 promises nothing Units 12–14 do not deliver; every can-do has a "prove it" task. | Orphan or undelivered promise. |
| 5 | **Mathematical correctness** | **Re-derive every definition, formula, proof, worked example, and key by hand, independently of the draft**; check signs, shapes, orders of multiplication, domains, and edge cases. | Any wrong value, sign, shape, order, or step. |
| 6 | **Proof audit** | Every proof listed in Section 6 is present, complete, states hypotheses, has no circular step (e.g., the equivalence chain in Unit 8 and the row-rank/column-rank argument in Unit 9 do not assume what they prove); anything only cited is labelled `CITED [VERIFY]` and says which. | Missing, circular, or invalid proof. |
| 7 | **Numerical-analysis audit** | Tolerances justified; no float `==`; **no determinant singularity test and no `inv`-to-solve anywhere except as labelled counterexamples**; partial-pivoting claims checked against exact solutions; condition-number statements tagged; `matrix_rank` tolerance formula tagged and locally checked; cancellation/overflow demonstrations verified. | Unjustified tolerance or numerically unsafe example. |
| 8 | **Oracle independence** | Every NumPy-based claim has an exact, pure-Python, SymPy, or different-library oracle; no oracle imports the code under test; exhaustive domains named, sized, feasible, and never called proof. | Shared-logic oracle or overclaim. |
| 9 | **Item-key and distractor audit** | Every key equals its oracle; every distractor equals its error-model output; exactly one key; no duplicate options; every item answerable from its linked lesson alone. | Ambiguous key, duplicate options, out-of-scope item. |
| 10 | **Tool-card audit** | `env_check`, `matscratch`, `gesolve`, `ltviz`, `qcheck`, and all `verify` commands have complete cards consistent with code and tests. | Missing or inconsistent element. |
| 11 | **Source-authenticity audit** | **Every non-trivial claim maps to a T1/T2 source or a derivation in Appendix A; no T4-only claim; no invented citation, DOI, URL, or page number; no misattributed result.** | Unsourced, misattributed, or invented citation. |
| 12 | **Cited-results audit** | Every cited-only result (`det(AB) = det A det B` for general `n` if not proved, row rank = column rank if not proved, one-sided inverse ⇒ two-sided if not proved, the condition-number error bound, the `(2/3)n³` flop count, partial-pivoting stability, `matrix_rank` default tolerance, NumPy API semantics, Wilson interval) is tagged `[VERIFY]`, listed in Appendix C with a learner-side check, never presented as proved. | Cited result presented as proved. |
| 13 | **Statistical and measurement validity** | Every experiment and benchmark reports seeds, sample sizes, spread, and caveats; no performance claim stated as a general fact; no claim about real models or data. | Missing uncertainty or overclaim. |
| 14 | **Originality and IP** | All problems, data, scenarios original/synthetic; named results by name and own statement. | Copied or closely paraphrased content. |
| 15 | **Integrity, ethics, fairness** | No cheating guidance; AI-use disclosure applied to every graded artifact; plot text alternatives present; gates framed as curriculum convention. | Cheating-adjacent advice or credential framing. |
| 16 | **Privacy and data handling** | Local, human-readable, validated, atomic; no PII; `env_check` excludes hostnames/usernames; `allow_pickle=False`; no telemetry/network. | PII, hidden network, unsafe storage. |
| 17 | **Determinism** | `default_rng(seed)` everywhere; no system-clock reads in logic; BLAS-thread effects acknowledged; deterministic ordering and tie-breaks (e.g., pivot ties). | Nondeterminism or wall-clock dependence. |
| 18 | **Technical accuracy (Python/NumPy/SciPy/SymPy)** | Every function, signature, default, and version claim is real and correct; **mentally execute every code block and lab**; NumPy 1.x vs 2.x tagged. | Invented API, misuse, wrong version claim. |
| 19 | **Executability** | Syntactically valid code; imports resolve; paths and links resolve; tests pass on reference and fail on a broken variant; every lab has steps, evidence, cleanup; all three packages install editable and their `verify` commands pass. | Any broken or unrunnable step. |
| 20 | **Repository consistency** | Module/lesson/project names, counts, and all relative links match the tree exactly (spaces URL-encoded; em dash preserved); forward links to other modules point to names that exist, else are marked `OPEN`. | Wrong name, count, path, or link. |
| 21 | **Pedagogical consistency** | Real beginner→expert progression; nothing used before taught or forward-referenced (e.g., `|det|` area in Unit 5 is flagged as a preview of Unit 7; rank in Unit 6 as a preview of Unit 9); **no re-teaching of 4A or S4B-01**; eigen/SVD, matrix calculus, formal subspaces, full factorisation theory, and regression previewed only; symbols stable. | Forward dependency without note, duplication, drift. |
| 22 | **Resource safety** | Size caps before allocation; exhaustive tests capped; no lab can exhaust memory/disk/time; benchmark sizes capped. | Unbounded work. |
| 23 | **Security and input validation** | No unsafe deserialization or `eval`/`exec`; strict loaders; named oracle registry. | Unsafe example. |
| 24 | **Currency** | Version-sensitive claims tagged; Python 3.10 minimum respected; `np.matrix` status tagged. | Stale or untagged claims. |
| 25 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated outputs (outputs labelled representative), misattributed results, invented constants, real-model claims, cited results presented as proved. | Any unsupported specific. |
| 26 | **Cross-consistency** | Practice bank, project code, tool cards, and lessons agree on names, error codes, conventions, and thresholds; stage-overview links resolve. | Contradiction or orphan. |
| 27 | **Adversarial review** | Re-read as a skeptical staff engineer: "What here is wrong, misleading, over-claimed, or teaches a bad habit (`inv(A) @ b`, `det` as a singularity test, a square shape hiding a transpose, trusting one benchmark run, a rank without a tolerance)?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 28 | **Reproducibility** | Labs and projects fit 4 CPU / 8 GB / 30 GB and disk caps; no paid service/account/download beyond the pinned install; seeded, idempotent, `--quick`; cleanup preserves learner data. | Hidden cost, nondeterminism, external dependency. |

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

**Appendix A — Source Register and Claim Register.** (i) **Source Register:** `Source ID | Tier (T1–T4) | Full citation (author, title, year/version) | Topics supported | Access (consulted live with URL+date / from knowledge) | [VERIFY] status`. (ii) **Claim Register:** `ID | Unit | Claim | Source ID(s) or derivation | Confidence (High/Med/Low) | Tag (PROVED/CITED/EVIDENCE ONLY/HEURISTIC/JUDGEMENT/ASSUMPTION)`. At least **120 entries**, covering every library-behaviour claim, formula, proof, cited result, attribution, and consequential judgement.

**Appendix B — Audit Report** (passes 1–28): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** every `[VERIFY]`/`[VERSION-SENSITIVE]`/`[JUDGEMENT]`/`[ASSUMPTION]` item and every CITED result, grouped (NumPy/SciPy/SymPy API and versions; floating point and conditioning; linear-algebra theorems; learning-science/statistics citations; repository consistency), each with *what to check*, *where (named source)*, and *how to test locally in one command or small script*. The reviewer must be able to close every item in **under 10 hours**.

**Appendix D — Known Limitations and Assumptions:** what is intentionally not covered (eigenvalues/SVD, matrix calculus, formal subspaces/rank–nullity, full LU/QR/Cholesky theory, sparse-matrix algorithms, GPU/half-precision numerics, production numerics, exam preparation, credentials); assumed versions; synthetic nature of all data; no validated link between practice scores and any job outcome; anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code and tests and human re-derivation of the mathematics.

**Appendix F — Proof, Status, and Counterexample Index:** every method/tool/proof with status, hypotheses, technique, and verification evidence; and a **minimal instance** for each counterexample: `AB ≠ BA`; `AB = 0` with `A, B ≠ 0`; `AB = AC` with `B ≠ C`; `(A+B)² ≠ A² + 2AB + B²`; `x ↦ Ax + b` not linear; `(AB)ᵀ ≠ AᵀBᵀ`; `(AB)⁻¹ ≠ A⁻¹B⁻¹`; `det(A+B) ≠ det A + det B`; rotate-then-shear ≠ shear-then-rotate; `tr(ABC) ≠ tr(ACB)`; the silent broadcast `(n,)+(n,1)`; a square shape hiding a transposed weight; the tiny-pivot failure of unpivoted elimination; `det(0.1·Iₙ) = 10⁻ⁿ` for a healthy matrix; `inv` returning garbage on a near-singular matrix; a small residual with a large error; `matrix_rank` changing with tolerance; a "symmetric" matrix asymmetric at `1e-17`; `A == A.T` failing for a numerically symmetric matrix.

**Appendix G — Executable Verification Bundle:** a standard-library-plus-NumPy `verify_syllabus.py` that extracts every fenced Python block with a `# File: …` first-line comment, writes it to a scratch directory, byte-compiles it, runs the tests in `--quick` mode with timeouts and a disk cap, and prints PASS/FAIL; plus `verify_module02.py` that verifies: every worked example against its oracle; every practice key against its registered oracle and every distractor against its error model (`qcheck`); the exact multiplication, determinant, inverse, rank, and classification tools against `sympy` on the stated exhaustive domains; the algebraic identities on seeded and boundary cases; the tiny-pivot, Hilbert, near-singular, and `det(0.1·Iₙ)` demonstrations; the rotation-composition identities with exact rational angles; the mutation labs and regression guards; and **all repository paths and counts against a reviewer-supplied `find` listing**.

## 12.4 Trust rules

- If a pass finds a problem you cannot fix confidently, **leave it visible** as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim code "was tested/executed" unless it actually was; say "expected output (representative)".
- Never claim content "was verified against live documentation" unless you consulted it.
- Never present exhaustive or seeded testing as proof; never present a cited result as proved; never present a gate score as a predictor or credential.
- Never state benchmark or speed figures as facts, success rates, hiring statistics, or employer requirements; never invent quotes or anecdotes; never present opinion as research.
- Attributions must be correct or marked `[VERIFY]`; never invent a citation, DOI, URL, or page number.
- Never advise anything that helps misrepresent skill or cheat; AI use is for explanation and review, disclosed and verified.

# 13. OUTPUT FORMAT

- **One Markdown document**, `SYLLABUS-Matrices-and-Linear-Transformations.md`.
- Start with: title; one-paragraph abstract (**explicitly stating that the module makes the matrix the central object — as data, as a linear map, and as a system — teaches multiplication, special matrices, shapes and batching, geometric transformations, elimination, determinants, inverses, and rank in NumPy with proofs and exact oracles; defers eigenvalues/SVD, matrix calculus, formal subspaces, factorisation theory, and regression; makes no outcome, credential, or real-model claims; and that every worked example and key is verified two independent ways**); metadata block (`Module: S4B-02`, `Stage: 4B`, `Language: Python`, `Estimated total time [ASSUMPTION]`, `Last reviewed`, `Assumed tool baseline`); a **linked table of contents** to all units and appendices.
- Then Units 0–14 in order, then Appendices A–G.
- `#` title, `##` units, `###`/`####` below; consistent anchors. Tables for comparisons, templates, rubrics; fenced code with language tags; **mermaid** for diagrams (lesson dependency graph, the "five faces" map, the invertibility-equivalence web, package layouts, experiment pipelines); plain-text math with Unicode, no LaTeX; every plot has a text alternative.
- Each unit self-contained but cross-linked (relative links to sibling files, 4A lessons, S4B-01 lessons, later 4B/4C modules by exact name; URL-encode spaces, keep the em dash as in the repository path).
- **Depth target:** each of Units 1–9 ≥ 3,500 words of teaching text excluding code, proofs, items, and tables (proofs additional); Unit 0 ≥ 1,800; Units 12–14 ≥ 2,500 each; Unit 11 ≥ 1,000; Unit 10 carries the full bank. **Do not compress to fit**; use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no "see previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0 |
| 2 | Unit 1 |
| 3 | Unit 2 |
| 4 | Unit 3 |
| 5 | Unit 4 |
| 6 | Unit 5 |
| 7 | Unit 6 |
| 8 | Unit 7 |
| 9 | Unit 8 |
| 10 | Unit 9 |
| 11 | Unit 10 part A: structure, `qcheck` tool, items for lessons 1–5, JSONL keys |
| 12 | Unit 10 part B: items for lessons 6–9, integration, scenario/critique, coding tasks, proof items, templates, scoring |
| 13 | Unit 11; Unit 12 (complete) |
| 14 | Unit 13 (complete) |
| 15 | Unit 14 (complete) |
| 16 | Appendices A–G, including the completed audit across **all** parts |

Rules:
- End each part with: `PART n/16 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-part audit (passes scoped to that part) **before** printing; keep a running Source and Claim Register.
- Part 16 runs the **cross-part** audit (passes 2, 11, 20, 21, 26, 27 especially) and may require **correcting earlier parts**: list each as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarise a unit to save space. If near the length limit, stop at a clean boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 16, print: "Concatenate Parts 1–16 in order into `SYLLABUS-Matrices-and-Linear-Transformations.md` and apply all listed corrections."

# 15. QUALITY BAR — DEFINITION OF DONE

Complete only when **all** are true:

- [ ] All 15 units present in order; Units 0–9 and 12–14 each with L1–L4 and N.0–N.14; Units 10 and 11 with their required structures; ≥ 3 worked original examples at each of L1 and L2, each verified two independent ways.
- [ ] Every topic and **every listed proof** in Section 6 is present and complete or labelled `CITED [VERIFY]` with which; nothing from 4A or S4B-01 is re-taught; eigen/SVD, matrix calculus, formal subspaces, factorisation theory, and regression are previewed only.
- [ ] The two explicit engineering rules — **never use the determinant as a floating-point singularity test; never form `A⁻¹` to solve `Ax = b`** — are taught with measured counterexamples and observed in all later code.
- [ ] Every method and tool has a card with status, runtime-checked preconditions, an independent oracle, exhaustive small-domain tests, seeded and adversarial tests, mutation checks, and deterministic behaviour.
- [ ] Conventions (claims, correctness, shape and row/column, degenerate cases, numerical, original content, item format, data/security, integrity, gates) are stated once and applied consistently.
- [ ] **No unsupported claim** about learning, hiring, interviews, role requirements, performance/benchmarks, employers, real models, or library internals.
- [ ] **Every non-trivial claim maps to a T1/T2 source or a derivation in the Source Register; no T4-only claim; no invented citation, DOI, URL, or page number.**
- [ ] The **≥ 200-item bank** (≥ 18 per lesson) has machine-readable keys, hand solutions, registered oracles, and error-model distractors, all machine-checked by `qcheck`; ≥ 10 coding tasks, ≥ 8 proof items, ≥ 20 templates.
- [ ] `matscratch` (≥ 22 operations), `gesolve`, and `ltviz` install editable in a fresh `venv` and pass `verify --quick` within disk caps; benchmarks report spread and caveats; report templates contain **no fabricated results**.
- [ ] Every counterexample in Appendix F is demonstrated with a minimal instance.
- [ ] Every "verified on all small inputs" statement names its domain and size and is never called proof.
- [ ] Names, counts, project file names, and 4A/S4B-01/4B/4C links match the tree; unresolved forward links are marked `OPEN`.
- [ ] Randomness via `default_rng(seed)`; no wall-clock logic; data local, human-readable, validated, atomically written; no `pickle`/`eval`/`exec`; no network at run time.
- [ ] Integrity policy consistent: AI use disclosed and verified; text alternatives for plots; gates framed as curriculum convention.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and `--quick`.
- [ ] Appendices A–G present; Claim Register ≥ 120 entries; audit passes 1–28 reported candidly; `verify_syllabus.py` and `verify_module02.py` delivered and consistent with the `# File:` comments.
- [ ] A human can close every open item in under 10 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/16**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Session:** use a long-context, high-capability model and one conversation across all 16 parts so the registers, conventions, and the running example stay consistent; type `continue` between parts. This is the largest module prompt so far (9 lessons, 3 projects).
2. **Scope decisions:** (a) S4B-01 already introduced independence/`matrix_rank`, so Unit 9 gives rank its **matrix-level** treatment and does not re-prove S4B-01's lemmas; (b) 4A-04 lesson 14 already bridges systems to matrices, so Unit 6 links it rather than repeating it; (c) eigenvalues/SVD, matrix calculus, formal subspaces/rank–nullity, and LU/QR/Cholesky theory are previewed only and linked to `03`, `07`, and `4C-01`/`4C-02`.
3. **Two engineering rules are enforced throughout:** never use the determinant as a floating-point singularity test, and never form `A⁻¹` to solve `Ax = b`. Each is taught with a measured counterexample and then observed in all code.
4. **Human verification:** run `verify_syllabus.py` and `verify_module02.py` (Appendix G) with a `find` listing; hand re-derive associativity, `(AB)ᵀ = BᵀAᵀ`, `R(α)R(β) = R(α+β)`, the tiny-pivot example, `det(AB)` for 2×2, and `rank(AᵀA) = rank(A)`; check each `[VERIFY]` NumPy behaviour (`matrix_rank` default tolerance, `matmul` batch broadcasting, `det` of the empty matrix, `np.matrix` status) against the official docs.
5. **Highest fabrication-risk spots:** the `(2/3)n³` flop count and condition-number error bound (must be derived or `CITED [VERIFY]`); the partial-pivoting stability claim (growth-factor caveat); the default `matrix_rank` tolerance formula; NumPy 1.x/2.x differences; any benchmark number (must carry spread and caveats); forward-link filenames in other modules (the prompt tells the model to mark unresolved ones `OPEN`).
6. **Final layout:** split the output into the fifteen target files plus supporting code under the three project folders.
