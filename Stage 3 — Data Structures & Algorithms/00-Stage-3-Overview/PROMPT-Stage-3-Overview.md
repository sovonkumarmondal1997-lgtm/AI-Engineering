# PROMPT — Generate `SYLLABUS-Stage-3-Overview.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Software Engineer with 15 years of industry experience** across backend systems, data platforms, and applied ML infrastructure. You have written and reviewed production code where an accidental O(n²) took a service down, tuned hot paths in Python, interviewed hundreds of candidates, and mentored engineers from first job to staff level. You teach the way you work: **measure before you claim, prove before you trust, and make every statement verifiable.**

You are also a careful technical author. You never invent a function, a complexity bound, a default, a version, or a statistic. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 3 — Data Structures & Algorithms / 00-Stage-3-Overview/` (module code **S3-00**)

Output file name: **`SYLLABUS-Stage-3-Overview.md`**

The language of all code, labs, and examples is **Python**.

It must teach, **one after another, from beginner to advanced**, these 7 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 0 | Stage orientation | `README.md` |
| 1 | Stage prerequisites and learning objectives | `stage-prerequisites-and-learning-objectives.md` |
| 2 | DSA topic map and interview coverage | `dsa-topic-map-and-interview-coverage.md` |
| 3 | Role-wise DSA relevance map | `role-wise-dsa-relevance-map.md` |
| 4 | Progress tracker and readiness checklist | `progress-tracker-and-readiness-checklist.md` |
| 5 | Overview project index | `Projects/README.md` |
| 6 | Overview project: Algorithm toolkit and benchmark | `Projects/01-algorithm-toolkit-and-benchmark.md` |

Do **not** add, merge, skip, or reorder units. `learning-plan.md` is in the folder but is **out of scope for this syllabus**; do not write it. Where a unit needs to reference the learning plan, link to it as `./learning-plan.md` and treat its contents as "defined separately". Do not produce shallow summaries: this is the **teaching content itself**, not an outline of it.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI Engineer who has finished Stages 0–2E (computer foundations, programming and computational thinking, Python for data engineering, data engineering, data architecture, production DevOps). They write working Python (functions, classes, comprehensions, generators, modules, virtual environments, basic `pytest`), use Git and a Linux shell, and read stack traces. They have **not** studied algorithm analysis formally and cannot yet solve unfamiliar problems under time pressure.
- **Stage position:** Stage 3 comes **before** the mathematics stages (4A/4B/4C). Do not assume mathematics beyond school algebra. Any logarithm, exponent, summation, or probability idea needed in this overview must be taught inline from first principles, with a forward pointer to Stage 4A/4B for depth.
- **Stage structure the syllabus must reflect** (module list is fixed; names exactly as below):

| Code | Module | Code | Module |
|---|---|---|---|
| 01 | Complexity and Big-O | 12 | Advanced Graph Algorithms |
| 02 | Arrays, Strings, and Hashing | 13 | Range Query Data Structures |
| 03 | Two Pointers, Sliding Window, and Binary Search | 14 | Advanced Problem-Solving Patterns |
| 04 | Stacks, Queues, and Linked Lists | 15 | String Algorithms |
| 05 | Recursion, Backtracking, and Sorting | 16 | Math, Number Theory, and Geometry |
| 06 | Trees and Tries | 17 | Probabilistic and Advanced Data Structures |
| 07 | Heaps and Priority Queues | 18 | Storage Engine and Large-Scale Data Algorithms |
| 08 | Graphs, BFS, DFS, and Shortest Paths | 19 | Similarity Search and AI Algorithms |
| 09 | Dynamic Programming | 20 | Coding Interview Method |
| 10 | Bit Manipulation and Bitwise Algorithms | 21 | Advanced DSA Capstone and Interview Readiness |
| 11 | Greedy Algorithms | | |

- **Stage constraint — zero budget.** All work runs on a **local laptop** (WSL2 Ubuntu primary, native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid service, no paid judge platform, no paid IDE. External practice platforms may be named as *optional*, never required.
- **Tool baseline (hands-on, required):** **CPython 3.12** `[ASSUMPTION — state the minimum 3.10 and note differences]`, `venv`, `pip`, `pytest`, `timeit`, `tracemalloc`, `cProfile`/`pstats`, `time.perf_counter_ns`, and the standard library data-structure modules `collections`, `heapq`, `bisect`, `itertools`, `functools`, `array`, `math`, `random`.
- **Optional helpers (flag as optional):** `hypothesis` (property-based testing), `ruff`, `mypy`, `matplotlib` (plots), `numpy` (contrast only, not for solving problems), `sortedcontainers` (awareness: the standard library has no balanced BST).
- **Domain flavor:** after the first level, examples should come from systems a data/AI engineer meets: top-k over event streams, deduplication of records, log-window analytics, dependency resolution for pipelines (DAGs), autocomplete, rate limiting, caching (LRU), nearest-neighbor search. Avoid toy-only examples beyond Level 1.
- **Cross-stage links:** point forward to Stage 4A/4B (mathematics), Stage 5A (ML foundations) and to the 21 modules of this stage. State clearly what is **taught in this overview vs. deferred** to a module, so no topic is half-covered or silently contradicted later.

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–4 AND UNIT 6)

Each of these units progresses through **exactly these four levels**, each building on the last. Use identical headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the concept, runs the basic Python snippet, reads the result. |
| **L2** | Intermediate — Working Practice | Applies it to realistic data/AI scenarios, follows standard patterns, avoids common mistakes. |
| **L3** | Advanced — Engineering Rigor | Designs, measures, and defends decisions with evidence (complexity proofs, benchmarks, trade-offs). |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses subtle failures, builds tooling and automation, reasons about scale, and could coach another engineer through it. |

Units 0 and 5 are index/orientation units and use the shorter structure in Sections 9 and 10.

# 5. MANDATORY STRUCTURE FOR UNITS 1–4

Use this exact skeleton, in this order. Do not omit a section; if a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete engineering or career failure this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, each starting with an action verb: implement, measure, prove, classify, justify…
Tag each with its level L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception.)
(One mermaid or ASCII diagram of the core structure.)

### N.3 Level 1 — Beginner
- Explanation from first principles (how and why it works, not only what to type)
- Guided exercise with exact Python code, expected output, and how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic example (complete, runnable Python)
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad example → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Rigor techniques (invariants, proofs of bounds, benchmark methodology)
- Measurement method (what to measure, with which tool, how to avoid fooling yourself)
- Exercise that requires a defended decision, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Automation (scripts, validators, CI checks, report generators)
- Team/organization concerns: standards, review checklists, how to coach others
- Edge cases and platform differences (CPython vs PyPy, 32/64-bit, Windows/WSL2/Linux, Python version differences)

### N.7 Engineering lens
- Where this shows up in real production systems (name the system class, never fabricate a company claim)
- Failure modes and blast radius (what breaks, for whom, how you would notice)
- Cost, capacity, and performance notes

### N.8 Integrity lens
- Study-integrity and correctness risks (illusion of competence, memorizing without understanding, benchmark self-deception, untested solutions)
- Controls and how to verify each with a command or a written check

### N.9 Checklist
(Checkbox list the learner can apply. Every item is verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | **expected evidence** | **cleanup** | stretch goal.
Labs must be idempotent and safe to re-run.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a "why the wrong answers are tempting" note for MCQs.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves under this stage to prove completion.)

### N.13 Common interview questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(References by name and section; items tagged [VERIFY]; version-sensitive claims.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated.

## Unit 1 — Stage prerequisites and learning objectives
- **L1:** what "data structures and algorithms" means and why a data/AI engineer needs it; what the stage assumes (programming, Python, Git, shell) and what it does not; the **Python fluency baseline** the learner must demonstrate: functions and recursion, lists/dicts/sets/tuples, slicing semantics, comprehensions, generators, classes and `__slots__`/dataclasses, exceptions, modules, `venv`, `pytest`; reading a stack trace; the mental model of references vs values (mutation, aliasing, the shallow-copy trap, mutable default arguments).
- **L2:** a **prerequisite self-diagnostic**: at least 20 short runnable tasks with expected results and a pass/fail rule, plus a `check_env.py` script that verifies Python version, `pytest`, `timeit`, recursion-limit awareness, and prints a PASS/FAIL report. Remediation map: each failed item → which earlier Stage (0–2E) lesson to revisit (refer to stage names, not invented file names). Environment setup: project layout, `venv`, `pyproject.toml` or `requirements.txt`, test discovery, a minimal `Makefile`/`justfile` with `test`, `lint`, `bench`, `clean`. Inline mini-lessons on the **only maths needed**: powers, logarithms as "how many halvings", sums such as 1+2+…+n, and counting steps; each ends with a runnable Python check.
- **L3:** the **stage learning objectives**: for each of the 21 modules, 3–5 measurable objectives in the form "Given X, the learner can Y, verified by Z", each tagged with level L1–L4 and mapped to the exit gate in Unit 4. A **competency model**: knowledge (explain), skill (implement), judgement (choose and defend), and speed (time-boxed). Entry/exit criteria for the whole stage. Python-specific realities to teach up front: CPython's call-stack limit and why recursion depth matters (`sys.getrecursionlimit`, no tail-call optimization), the cost of `list.pop(0)`, `in` on a list vs a set, string concatenation in loops, object overhead and memory (`sys.getsizeof` limits), hash randomization for `str`, `dict` insertion order guarantee, Timsort stability, integer arbitrary precision. For each claim, show the one-line experiment that proves it.
- **L4:** designing a personal **learning contract** (weekly hours, deliberate-practice rules: attempt → time-box → read hint → re-implement from memory), **learning science** applied honestly (spaced repetition, interleaving, retrieval practice) without citing studies you cannot name precisely; a **prerequisite-gate automation** script (reads a results file and refuses to unlock the next step below the threshold); common failure patterns of self-taught learners and countermeasures; how to adapt the stage when time is short (a documented "minimum viable path" with explicit risk trade-offs).
- **Must include:** the full 20+ task diagnostic with answer key, `check_env.py`, the 21-module objectives table, and a "Python performance facts" lab where every fact is demonstrated by a measurement the learner runs.

## Unit 2 — DSA topic map and interview coverage
- **L1:** what a data structure is vs an algorithm; the taxonomy (linear, hierarchical, graph, hashing-based, probabilistic; paradigms: brute force, divide and conquer, greedy, dynamic programming, backtracking, randomized); a **one-page map** from every one of the 21 modules to the topics it contains, the problem types it unlocks, and the prerequisite edges between modules (a **dependency graph in mermaid**, with a stated reason for every edge); an orientation to how interviews are structured (phone screen, coding round, system-design bridge, behavioral) described generally and without fabricated company-specific claims.
- **L2:** the **pattern-to-problem matrix**: pattern (two pointers, sliding window, binary search on answer, monotonic stack, top-k with heap, BFS/DFS, topological sort, union-find, prefix sums, intervals, backtracking, 1-D/2-D DP, bitmasks, trie, greedy exchange argument) → recognition signals in the problem statement → canonical Python tool (e.g., `heapq`, `bisect`, `collections.deque`, `Counter`) → typical complexity → module that teaches it. A **Python built-in complexity cheat sheet** for `list`, `dict`, `set`, `deque`, `heapq`, `bisect`, `str`, `sorted`, with each non-obvious entry tagged `[VERIFY: CPython TimeComplexity page and implementation notes]` and a runnable benchmark confirming at least five of them.
- **L3:** **interview coverage analysis**: coverage tiers (Core / Common / Advanced / Specialist) expressed as *engineering judgement with stated reasoning*, not as invented frequency statistics; a coverage matrix of topic × module × difficulty band (Easy/Medium/Hard defined by explicit criteria, e.g., number of insights required, state complexity); the difference between **interview DSA** and **production DSA** (where each shows up, where each is irrelevant); the gap between "knowing the idea" and "solving it in 30 minutes" and how modules 14, 20, and 21 close it; a **coverage-gap detector** script that reads the learner's completed-topic file and reports uncovered patterns.
- **L4:** the **system-design bridge**: how structures here map to real components (LRU/LFU cache, rate limiter, autocomplete, consistent hashing, Bloom filter, LSM tree, inverted index, top-k, HyperLogLog, ANN index) — one paragraph each with the DSA ingredient and the trade-off, no fabricated product claims; how to read a problem and decide the target complexity from the constraints (n ≤ 10⁵ ⇒ O(n log n), etc.) with the reasoning shown and a Python-specific caveat (CPython runs roughly 10⁷–10⁸ simple operations per second `[ILLUSTRATIVE — measure yours]`); how to extend the map when new topics appear; maintaining the map as a living document.
- **Must include:** the module dependency graph, the pattern-to-problem matrix (≥ 25 rows), the complexity cheat sheet with verification benchmark, the coverage-gap script, and the constraint-to-complexity guide.

## Unit 3 — Role-wise DSA relevance map
- **L1:** why DSA relevance differs by role; the role definitions used in the map (state each in two sentences): **Data Engineer, Analytics Engineer, Data Scientist, ML Engineer, Applied AI Engineer, LLM/GenAI Engineer, MLOps/Platform Engineer, Backend Engineer, SRE, Search/Retrieval Engineer, Research Engineer**; the difference between *needing to know the idea*, *needing to implement it*, and *needing to use a library built on it*.
- **L2:** the **relevance matrix**: for each role × each of the 21 modules, a rating from a defined 4-point scale (Essential / Important / Useful / Awareness) **with a one-line justification for every Essential and Important cell**; the scale must be defined by behavior ("would be expected to implement from scratch in an interview or on the job"). Concrete production examples per cell family (e.g., heaps → top-k and scheduling; graphs → lineage and DAG schedulers; tries → autocomplete and routing; hashing → dedup and sharding; ANN → retrieval), with no invented company claims.
- **L3:** **role-specific study paths**: for each role, an ordered module sequence, what to skip at first pass, what to deepen, and the capstone emphasis; a **trade-off analysis** of depth vs breadth for a learner targeting Applied AI Engineering specifically (the stage's primary target), with explicit reasoning for modules 17, 18, and 19; a script `role_path.py` that takes a role and available weeks and prints a prioritized module plan; honest statement of what the map **cannot** know (hiring practices vary; it is a judgement aid, not a prediction).
- **L4:** how to **validate the map against reality**: read three real job descriptions or three open-source codebases and compare, with a documented procedure and a template (the learner collects their own evidence; do not fabricate postings or repositories); how roles evolve and how to re-weight; how DSA knowledge compounds into design-review and code-review judgement; how to explain a DSA choice to a non-specialist stakeholder.
- **Must include:** the 11-role × 21-module matrix with justifications for all Essential/Important cells, role-specific paths, and `role_path.py` with a test.

## Unit 4 — Progress tracker and readiness checklist
- **L1:** why track progress; what "done" means for a DSA topic (explain it, implement it from memory, solve unseen problems, state complexity with proof sketch, test it); how to use a tracker file; the daily/weekly loop.
- **L2:** a **machine-readable tracker** (CSV or YAML schema) with fields for module, topic, status (not started / learning / implemented / solved unseen / mastered), date first solved, date last reviewed, confidence 1–5, time taken, hints used, and notes; a Python script `tracker.py` that validates the file, prints a per-module progress table, and lists items due for review under a **spaced-review schedule** (state the intervals as a chosen policy, not a scientific fact); a **readiness checklist** per module (concept, implementation, complexity, edge cases, tests, solved ≥ N unseen problems within time-box).
- **L3:** **readiness gates**: a gate rule per module and a stage-level exit gate with thresholds (use 80% proceed; 60–79% remediate; below 60% repeat, consistent with the rest of the roadmap); objective evidence required (tests passing, benchmark outputs, timed-solve logs); a **mock-interview scoring rubric** with criteria (problem understanding, approach, correctness, complexity analysis, code quality, testing, communication) and 4 performance bands with descriptors; analytics from the tracker: velocity, weak-topic detection, review debt; a weekly retrospective template.
- **L4:** automation: gate enforcement script, dashboard generation to Markdown/HTML from the tracker, review-debt alerts; guarding against **tracker gaming** (self-rating inflation: require evidence links, periodic blind re-solves); calibration of confidence vs actual outcome (a calibration table); when to re-enter a module; how to run a **study group or mentor review** using the tracker; the final **stage readiness checklist** (implementation, complexity analysis, Python idioms, testing, interview method, capstone) that the learner signs off with evidence.
- **Must include:** the tracker schema with a populated sample (clearly labeled sample data), `tracker.py` with tests, the per-module readiness checklist for all 21 modules, the mock-interview rubric, and the stage exit checklist.

# 7. SELF-CHECK AND PRACTICE REQUIREMENTS (REPLACES A STANDALONE PRACTICE FILE)

There is no `practice-questions.md` in this folder. Instead, every unit 1–4 has its N.11 self-check set, and the syllabus ends with a **cross-unit integration set** of **at least 25 questions** (inside Appendix F) covering the whole overview. Every question carries: ID, level (L1–L4), objective it tests, time estimate, **model answer**, and **common wrong answers**. Include at least 6 questions that require a written trade-off argument. Give a scoring rubric with the 80 / 60–79 / below-60 gate rule.

# 8. UNIT 6 — OVERVIEW PROJECT: ALGORITHM TOOLKIT AND BENCHMARK (REQUIREMENTS)

**Project:** *Algorithm Toolkit and Benchmark.* A small, installable Python package plus a benchmark harness that the learner will **extend through all 21 modules** and that feeds the Stage 3 capstone (`21-Advanced-DSA-Capstone-and-Interview-Readiness/Projects/01-dsa-algorithm-toolkit-capstone.md`). Because the algorithm modules come later, this project delivers the **scaffold, the harness, a seed set of algorithms, and the verification discipline**, and defines the extension contract.

This unit follows the four levels (Section 4) and the N.0–N.14 skeleton, **plus** the project specification below.

**Scenario:** An engineer keeps rewriting the same algorithms in interviews and at work without ever knowing whether the code is correct or how it scales. The learner builds a toolkit that proves its own correctness and measures its own complexity.

**Required deliverables (each with acceptance criteria that can be checked by command):**
1. Repository layout (`src/` layout, `tests/`, `bench/`, `docs/`, `pyproject.toml`) and a `Makefile` (or `justfile`) with targets: `install`, `lint`, `typecheck`, `test`, `bench`, `report`, `check`, `clean`, `all`.
2. A **registry mechanism**: algorithms register under a category, name, declared time and space complexity, and a reference oracle (a slow, obviously correct implementation). Provide the decorator/dataclass design and tests.
3. A **seed set of at least 8 algorithms**, each with oracle, tests, and declared complexity: linear search, binary search (with `bisect` as oracle), insertion sort, merge sort, quicksort with a randomized pivot, two-sum with hashing, a sliding-window maximum, and a simple heap-based top-k. Typed, documented, no `TODO` in required parts.
4. **Correctness harness:** table-driven tests, edge-case generators (empty, single, duplicates, sorted, reverse-sorted, large values), and **randomized differential testing against the oracle**, with a seeded RNG so failures reproduce. `hypothesis` property tests as an optional stretch.
5. **Benchmark harness:** a function that measures runtime over a ladder of input sizes using `time.perf_counter_ns`, repeats runs, reports **median and an upper percentile** (state which), handles warm-up, disables or controls garbage collection explicitly and says why, regenerates inputs per run where mutation matters (in-place sort), and records Python version and machine info. Memory measurement with `tracemalloc` and a note on what it does and does not capture.
6. **Empirical complexity estimation:** fit a log-log slope (pure Python least squares, no `numpy` required) to classify behavior as ≈ n, n log n, n², etc., with an explicit confidence caveat and a comparison against the declared complexity; a regression guard that fails `make check` when measured growth exceeds the declared class by a stated tolerance.
7. **Adversarial and worst-case inputs:** show quicksort without randomization degrading on sorted input, `list.pop(0)` queues vs `deque`, string concatenation in a loop vs `join`, and report measured results.
8. **Report generator:** a Markdown report (and optional PNG plots if `matplotlib` is present) with tables of runtime vs n, fitted exponents, declared vs observed complexity, pass/fail per algorithm, and environment metadata.
9. **Documentation:** architecture diagram, an ADR (≥ 3: registry design, benchmark methodology, tolerance policy), and an **extension guide** that tells the learner exactly how to add an algorithm from modules 02–21 (what to register, which oracle, which tests, which benchmark ladder).
10. **A results template** the learner fills with their own measurements. Provide the template; do not fabricate results.

**Include:** a milestone plan (5–6 milestones with time estimates), a grading rubric (100 points, criterion-level descriptors for Poor / Adequate / Strong / Exemplary), stretch goals (profile with `cProfile`, compare CPython with PyPy if installed, add a `pytest-benchmark`-style comparison, publish as a package), common failure points (timing noise, mutated inputs reused across runs, tiny n, GC pauses, misreading fitted slopes), a self-review checklist, and the exact evidence folder structure.

**Provide complete, runnable starter code** for the package, the registry, the 8 seed algorithms with oracles, the harness, the fitter, the report generator, the tests, the Makefile, and `pyproject.toml`. Every code file states its path in a first-line comment. Do not leave `TODO: implement` in required deliverables. Dependencies: standard library plus `pytest` for required parts.

# 9. UNIT 0 — README ORIENTATION (REQUIREMENTS)

Include: purpose of Stage 3; who it is for; **Gate In** mapped to Stage 2E exit and Unit 1; what the learner can do at the end (Gate Out) in observable terms; the **21-module map** and its dependency graph (consistent with Unit 2); the contents of this overview folder and the **order in which to read it**; a pointer to `./learning-plan.md` (defined separately; do not invent its contents); recommended pacing at two intensities (state hours per week as a plan, not a promise); tool matrix (Required vs Optional, with install-verification commands); environment checklist (Python version, disk, venv, cleanup); a **glossary** (≥ 30 terms, each defined precisely); a module-to-exit-criteria mapping; how evidence is stored; how practice questions and the module `Projects/` folders are used; a "how this connects to Stage 4A/4B and Stage 5A" table.

# 10. UNIT 5 — PROJECTS README (REQUIREMENTS)

Include: purpose of the overview `Projects/` folder; how the toolkit project relates to the 21 module projects and to the capstone (a dependency diagram); project index table (file, goal, estimated time, prerequisites, outputs); submission and evidence format; the 100-point grading scheme summary and pass thresholds; rules on originality (the learner must write the solutions; AI assistance policy: allowed for explanation and review, not for producing the graded implementations, and always disclosed in the evidence log); a template for the evidence log; a reproducibility checklist (seed, versions, machine info); and a "how to ask for a code review" template.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: src/algokit/registry.py`).
2. **Every command and snippet is paired with expected output** (representative, clearly labeled "example — yours will differ in timings and memory addresses") and a short interpretation.
3. **Code must run.** Python 3.10+ syntax only (state if 3.12 is required). Standard library unless marked optional. Use type hints on all public functions. Prefer clarity over cleverness.
4. **Complexity statements must be correct and precise:** state whether a bound is worst-case, average-case, or amortized; give both time and space; give the proof sketch or invariant for every non-trivial claim; distinguish the algorithm's complexity from the CPython implementation's constant factors.
5. **No unproven performance claims.** Every speed claim ties to a measurement the learner can run, with the method stated (warm-up, repeats, statistic). Otherwise label it `[ILLUSTRATIVE — measure yours]`.
6. **Benchmarks must avoid the usual errors:** timing a mutated input twice, measuring inside the noise floor, measuring only one n, trusting a single run, forgetting garbage collection and caching effects, confusing wall time with CPU time.
7. **No secrets, no network access, no paid APIs** in any required lab.
8. **Scripts are safe by default:** no deletion outside the project directory; `clean` targets list what they remove; random generators take explicit seeds.
9. **Every test shows how to run it** and what a failing run looks like (break the code on purpose once).
10. **Every lab ends with cleanup** and a verification that no stray files, processes, or virtual environments remain beyond those documented.
11. **Name Python-version and implementation differences** (CPython vs PyPy, 3.10 vs 3.12) wherever behavior or performance differs, tagged `[VERSION-SENSITIVE]`.
12. **WSL2 notes:** call out filesystem-performance differences (`/mnt/c` vs the Linux filesystem) and timing noise sources where they affect a lab.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You will act as author, then as an independent auditor of your own work, and you will include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every technical claim on **authoritative sources**: the official Python documentation (Language Reference, Library Reference, the `timeit`, `heapq`, `bisect`, `collections`, `tracemalloc` pages, the "Data model" section, and the Python Wiki **TimeComplexity** page for built-in operation costs), PEPs where relevant, and standard algorithm texts (e.g., *Introduction to Algorithms* — Cormen, Leiserson, Rivest, Stein; *Algorithms* — Sedgewick and Wayne; *The Algorithm Design Manual* — Skiena) cited by **title and chapter/section topic, not page numbers you cannot confirm**. Provide a URL only if you are certain it is canonical; otherwise cite the document by name and mark `[VERIFY]`.
- **Do not fabricate:** version numbers, release dates, benchmark results, hiring statistics, interview-frequency percentages, company interview practices, job-posting contents, salary figures, study-effectiveness numbers, quotes, or library behavior. If you need a number, derive it from a stated command or label it illustrative.
- **Mark uncertainty** with one of: `[VERIFY]` (check against current docs), `[ILLUSTRATIVE]` (example value, not a claim), `[VERSION-SENSITIVE]` (behavior varies by version; state the range you assume), `[ASSUMPTION]`, `[JUDGEMENT]` (a reasoned opinion on relevance or priority, not a measured fact).
- Keep a running **Claim Register** (Section 12.3) for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 7 units present, in order, with every required section (Sections 5, 9, 10), every unit-specific topic (Section 6, 8), level coverage L1–L4. | Any missing section/topic. |
| 2 | **Technical accuracy** | Every complexity bound, Python behavior, standard-library function, and signature is real and correct. Mentally execute every code block and lab. | Any wrong bound, invented function, or misused API. |
| 3 | **Executability** | Each code block is syntactically valid Python; imports resolve; file paths and cross-references between files resolve; each test would pass on the reference implementation and fail on a deliberately broken one; every lab has steps, expected evidence, and cleanup. | Any broken, ambiguous, or unrunnable step. |
| 4 | **Complexity and proof audit** | For each algorithm and structure: worst/average/amortized labels are right; space includes recursion stack and auxiliary storage; proof sketches or invariants are valid; Python constant-factor caveats are stated. | Any mislabeled or unproven bound. |
| 5 | **Benchmark validity** | Methodology is sound (warm-up, repeats, statistic stated, fresh inputs for mutating algorithms, GC handling, multiple sizes); the fitter's output is interpreted with caveats; no result is presented as measured unless it is a template or labeled representative. | Flawed method or fabricated numbers. |
| 6 | **Currency** | Version-sensitive claims are tagged; no deprecated or removed Python feature is taught as current; the 3.10 minimum is respected or differences noted. | Stale or untagged claims. |
| 7 | **Fabrication scan** | Hunt for invented statistics, fake citations, made-up interview frequencies, fabricated company practices, invented job postings, fake benchmark outputs, and invented library features. | Any unsupported specific. |
| 8 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept is used before it is introduced; terminology is consistent; maths stays at the stated level; the running example (the toolkit) evolves coherently. | Forward dependency without a note; terminology drift. |
| 9 | **Cross-consistency** | The 21-module list, names, and order match Section 3 exactly in every unit; the dependency graph, relevance matrix, tracker, and readiness checklists agree with one another; the objectives table maps 1:1 to the gate checklist; project deliverables map to units; the README does not promise anything the units do not deliver. | Any contradiction, missing module, or orphan deliverable. |
| 10 | **Adversarial review** | Re-read as a skeptical staff engineer and as a hostile interviewer: "What here is wrong, misleading, or would teach a bad habit?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 11 | **Reproducibility** | Labs run within the 4 CPU / 8 GB / 30 GB baseline, need no paid service or network, are idempotent, seeded, and clean up. | Hidden cost, nondeterministic result without seeding, or leftover state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendices)

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag ([VERIFY]/[VERSION-SENSITIVE]/[JUDGEMENT]/none)`. Include at least **50 entries**, covering every complexity claim of a built-in, every Python-behavior claim, and every relevance judgement of consequence.

**Appendix B — Audit Report** (table for passes 1–11): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** a list of **all `[VERIFY]` / `[VERSION-SENSITIVE]` / `[JUDGEMENT]` items** grouped by area (CPython built-ins and data model, standard-library modules, complexity claims, benchmark methodology, role-relevance judgements, interview-coverage judgements), each with: *what to check*, *where to check (named source)*, *how to test it locally with one command or small script*. The reviewer must be able to close every item in under 3 hours.

**Appendix D — Known Limitations and Assumptions:** what the overview intentionally does not cover, assumed Python version, CPython-vs-PyPy caveats, WSL2 timing caveats, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code and benchmarks.

**Appendix F — Cross-Unit Integration Questions** (Section 7).

**Appendix G — Executable Verification Bundle:** a single `verify_syllabus.py` script (standard library only) that extracts every fenced Python block marked `# File: …` from the syllabus, writes them to a scratch directory, byte-compiles them (`py_compile`), and runs the test suite; it prints a PASS/FAIL list. The reviewer can run it to check that the delivered code is at least syntactically valid and its tests pass.

## 12.4 Trust rules
- If an audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it was actually executed in your environment. Use "expected output (representative)" instead.
- Never state that content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.
- Relevance maps, interview-coverage tiers, and study-path advice are **judgements**. Tag them `[JUDGEMENT]` and explain the reasoning; never present them as data.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-Stage-3-Overview.md`.
- Start with: title, one-paragraph abstract, metadata block (`Module: S3-00`, `Stage: 3`, `Language: Python`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–6 in order, then Appendices A–G.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons, fenced code blocks for all code, mermaid for diagrams.
- Each unit must be **self-contained but cross-linked** (relative links to sibling target files, and to `./learning-plan.md` where relevant).
- **Depth target:** Units 1–4 each ≥ 2,500 words of teaching text excluding code; Unit 6 complete with all code; the integration set ≥ 25 items. Total expected length: very large. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0 (README), Unit 1 |
| 2 | Unit 2 |
| 3 | Unit 3, Unit 4 |
| 4 | Unit 5 (Projects README), Unit 6 part A: N.0–N.8 and the project specification and scaffold code |
| 5 | Unit 6 part B: harness, fitter, report generator, tests, N.9–N.14, grading rubric, results template |
| 6 | Appendices A–G (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/6 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–11, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 6 must run the **cross-part** audit (passes 8, 9, 10 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you are approaching the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 6, print the final assembly instruction: "Concatenate Parts 1–6 in order into `SYLLABUS-Stage-3-Overview.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 7 units present, in the specified order; Units 1–4 and 6 each with levels L1–L4 and sections N.0–N.14.
- [ ] Every unit-specific topic in Sections 6, 8, 9, and 10 is taught at its stated level.
- [ ] The 21 module names and order match Section 3 exactly everywhere they appear.
- [ ] The 11-role × 21-module matrix is complete, with justifications for every Essential/Important cell, all tagged `[JUDGEMENT]`.
- [ ] The prerequisite diagnostic (≥ 20 tasks), `check_env.py`, `tracker.py`, and `role_path.py` are complete and have tests.
- [ ] The toolkit project has complete runnable code, acceptance criteria, rubric, and a results template with **no fabricated results**.
- [ ] Every complexity claim is correctly labeled (worst/average/amortized, time and space) and every performance claim is tied to a measurement or tagged illustrative.
- [ ] Every lab has steps, expected evidence, and cleanup; all run within the free local baseline.
- [ ] No fabricated statistics, citations, versions, company practices, or interview frequencies; every uncertain item is tagged.
- [ ] Appendices A–G present; Claim Register ≥ 50 entries; audit passes 1–11 reported candidly; ≥ 25 integration questions.
- [ ] `verify_syllabus.py` is delivered and consistent with the file-path comments in the code.
- [ ] A human can verify every open item in under 3 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/6**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 6 parts so the Claim Register, the 21-module list, and the running toolkit example stay consistent.
2. **Do the human verification yourself.** The prompt makes the LLM list what to check (Appendix C) and ships `verify_syllabus.py` (Appendix G), but an AI self-audit is not independent. Run the code, run the benchmarks, and close each `[VERIFY]` item against the Python documentation and the Python Wiki TimeComplexity page.
3. **Spot-check fabrication risk areas first:** built-in complexity claims (`list`, `dict`, `set`, `deque`, `heapq`, `bisect`), interview-coverage tiers, role-relevance justifications, `tracemalloc` limits, and any "measured" number that is not a template.
4. **Scope note:** `learning-plan.md` is intentionally excluded, as requested. Generate it with a separate prompt later; the README and Projects README only link to it.
5. **Final file layout:** save the LLM output as `SYLLABUS-Stage-3-Overview.md` in this folder. Later, split it into the 7 target files (`README.md`, `stage-prerequisites-and-learning-objectives.md`, `dsa-topic-map-and-interview-coverage.md`, `role-wise-dsa-relevance-map.md`, `progress-tracker-and-readiness-checklist.md`, `Projects/README.md`, `Projects/01-algorithm-toolkit-and-benchmark.md`).
