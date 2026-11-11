# PROMPT — Generate `SYLLABUS-Complexity-and-Big-O.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Software Engineer with 15 years of industry experience** across backend systems, data platforms, and applied ML infrastructure. You have diagnosed production outages caused by an accidental O(n²), argued Big-O in design reviews, benchmarked Python hot paths, interviewed hundreds of candidates, and mentored engineers from first job to staff level. You teach the way you work: **prove it, then measure it, and never confuse the two.**

You are also a careful technical author. You never invent a bound, a function, a default, a version, or a statistic. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 3 — Data Structures & Algorithms / 01-Complexity-and-Big-O/` (module code **S3-01**)

Output file name: **`SYLLABUS-Complexity-and-Big-O.md`**

All code, labs, and examples are in **Python**.

It must teach, **one after another, from beginner to advanced**, these 12 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 1 | What an algorithm is | `01-what-an-algorithm-is.md` |
| 2 | Counting steps and growth | `02-counting-steps-and-growth.md` |
| 3 | Big-O notation | `03-big-o-notation.md` |
| 4 | Time vs space complexity | `04-time-vs-space-complexity.md` |
| 5 | Amortized analysis | `05-amortized-analysis.md` |
| 6 | Measuring real performance in Python | `06-measuring-real-performance-in-python.md` |
| 7 | Best, average, and worst-case analysis | `07-best-average-and-worst-case-analysis.md` |
| 8 | Complexity analysis of loops and recursion | `08-complexity-analysis-of-loops-and-recursion.md` |
| 9 | Comparing algorithmic complexities | `09-comparing-algorithmic-complexities.md` |
| 10 | Practice questions | `practice-questions.md` |
| 11 | Projects index | `Projects/README.md` |
| 12 | Project: Benchmark Python collections | `Projects/01-benchmark-python-collections.md` |

Do **not** add, merge, skip, or reorder units. The folder's own `README.md` is **out of scope for this syllabus**; do not write it (treat it as "defined separately"). Do not produce shallow summaries: this is the **teaching content itself**, not an outline of it.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI Engineer who has finished Stages 0–2E and Unit S3-00 (Stage 3 Overview: prerequisites, topic map, toolkit scaffold). They write working Python (functions, classes, comprehensions, generators, `venv`, basic `pytest`). They have **never analyzed an algorithm formally**.
- **Stage position:** Stage 3 comes **before** the math stages (4A/4B/4C). Assume **school algebra only**. Teach inline, from first principles, every piece of math used: powers, logarithms (as "how many times can I halve n"), summation of 1+2+…+n and of geometric series, floor/ceiling, and the idea of a limit as "what happens for very large n" (no calculus). Give a forward pointer to Stage 4A for depth.
- **Zero budget.** All work runs on a **local laptop** (WSL2 Ubuntu primary, native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid service, no network required.
- **Tool baseline (required):** **CPython 3.12** `[ASSUMPTION — state minimum 3.10 and note differences]`, `venv`, `pytest`, `timeit`, `time.perf_counter_ns`, `tracemalloc`, `sys.getsizeof`, `cProfile`/`pstats`, `gc`, and the standard library (`collections`, `heapq`, `bisect`, `itertools`, `functools`, `array`, `math`, `random`, `statistics`).
- **Optional helpers (flag as optional):** `matplotlib` (plots), `numpy` (contrast only), `hypothesis`, `ruff`, `mypy`, `pyperf`/`pytest-benchmark` (awareness), PyPy (awareness).
- **Domain flavor:** after Level 1, examples come from systems a data/AI engineer meets: deduplicating records, joining two datasets, top-k over event streams, sliding-window log analytics, batch ETL loops, an LRU cache, building a list of results in a loop, searching a sorted index. Avoid toy-only examples beyond L1.
- **Running example thread:** one problem, **"find duplicate user IDs in a growing list of events"**, appears in every unit and evolves: brute-force O(n²) → sort-based O(n log n) → hash-set O(n) → streaming with memory bounds → measured and compared. Reuse it so the learner sees the same task analyzed through every lens.
- **Continuity and links:** link back to the Stage 3 Overview toolkit (`../00-Stage-3-Overview/Projects/01-algorithm-toolkit-and-benchmark.md`) and forward to modules 02–21. State clearly what is **taught here vs. deferred** (e.g., recurrence solving beyond the basic Master Theorem cases, probabilistic analysis, lower-bound proofs for sorting are introduced here and deepened in modules 05, 14, 17).

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–9 AND UNIT 12)

Each unit progresses through **exactly these four levels**. Use identical headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the concept, runs the basic Python snippet, reads the result. |
| **L2** | Intermediate — Working Practice | Applies it to realistic data/AI code, follows standard patterns, avoids common mistakes. |
| **L3** | Advanced — Engineering Rigor | States and proves bounds, designs benchmarks, defends decisions with evidence and trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses subtle failures, reasons at scale and across implementations, builds tooling, and could coach another engineer. |

Units 10 and 11 use the structures in Sections 7 and 9.

# 5. MANDATORY STRUCTURE FOR UNITS 1–9

Use this exact skeleton, in this order. Do not omit a section; if one is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete engineering failure this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, each starting with an action verb: derive, prove, measure, classify, justify…
Tag each with its level L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception.)
(One mermaid or ASCII diagram.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what)
- Guided exercise with exact Python code, expected output, and how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic example (complete, runnable Python), continuing the running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad code → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Formal statement and proof (or proof sketch) of the key results
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure, with which tool, how to avoid fooling yourself)
- Exercise that requires a defended argument, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Automation (scripts, validators, regression guards)
- Team concerns: design-review checklist, how to coach others, how to document complexity in code
- Edge cases and platform differences (CPython vs PyPy, 32/64-bit, Python 3.10 vs 3.12, WSL2 vs native Linux)

### N.7 Engineering lens
- Where this shows up in real systems (name the system class; never fabricate a company claim)
- Failure modes and blast radius (what breaks, for whom, how you would notice)
- Cost, capacity, and performance notes

### N.8 Integrity lens
- Reasoning and measurement risks (hidden constants, benchmark self-deception, small-n illusions, confusing "fast" with "scalable")
- Controls and how to verify each with a command or a written check

### N.9 Checklist
(Checkbox list the learner can apply to real code. Every item is verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | **expected evidence** | **cleanup** | stretch goal.
Labs must be idempotent, seeded, and safe to re-run.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a "why the wrong answers are tempting" note for MCQs.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves under this module to prove completion.)

### N.13 Common interview questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(References by name and section; items tagged [VERIFY]; version-sensitive claims.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated.

## Unit 1 — What an algorithm is
- **L1:** definition (finite, unambiguous steps, defined input, defined output, terminates); algorithm vs program vs data structure vs heuristic; input/output specification; a problem versus an algorithm that solves it (many algorithms per problem); pseudocode and its translation to Python; tracing an algorithm by hand with a trace table; correctness as "does what the spec says for **every** valid input"; examples: find maximum, linear search, GCD (Euclid), checking for duplicates in three ways.
- **L2:** writing a precise specification (preconditions, postconditions); edge cases (empty, single element, duplicates, negative, very large, `None`, unhashable); testing as evidence vs proof; table-driven tests with `pytest`; differential testing against a slow oracle with a seeded RNG; the difference between **a correct algorithm and a correct implementation**; mutation of inputs and side effects as part of the contract; stability and determinism; choosing between algorithms on constraints, not taste.
- **L3:** **loop invariants**: initialization, maintenance, termination, with full worked invariant proofs for linear search, find-max, and insertion sort; termination arguments (a quantity that strictly decreases and is bounded); proof by induction for a recursive algorithm (e.g., sum of list, Euclid's GCD); partial vs total correctness; what a proof guarantees and what it does not (it does not guarantee the Python code has no bug, no overflow of the call stack, or no mutation surprise); runtime assertions as executable invariants.
- **L4:** computability and tractability at a **conceptual** level only (decidable vs undecidable, the halting problem in one paragraph, P vs NP named honestly without proof), why "algorithm" is a mathematical object and "code" is its artifact; randomized algorithms and Las Vegas vs Monte Carlo (definition only; depth in module 14/17); specification-by-contract tooling in Python (assertions, type hints, `hypothesis` as optional); formal-verification awareness (named, not taught); how to write a one-paragraph algorithm design note that a reviewer can check.
- **Must include:** worked invariant proofs for three algorithms, a differential-testing harness, a deliberately wrong "almost-correct" algorithm that passes weak tests and fails an edge case, and the duplicate-detection running example in its first three versions with correctness proofs.

## Unit 2 — Counting steps and growth
- **L1:** the idea of a "basic operation" and a cost model (unit-cost RAM model, stated honestly as a model); counting operations in simple loops, nested loops, and loops with early exit; building a table of n vs steps; instrumenting Python code with a counter; growth: constant, logarithmic, linear, linearithmic, quadratic, cubic, exponential, factorial — shown as tables and plots; the "double the input" experiment.
- **L2:** exact step counts as polynomials (T(n) = 3n² + 2n + 5), why constants and lower-order terms stop mattering for large n, but **do** matter for small n and in Python; counting comparisons vs swaps vs assignments; instrumented versions of linear search, selection sort, duplicate detection (brute force vs hash set); logarithms from first principles (halving loop, `math.log2`, `int.bit_length`), the sum 1+2+…+n = n(n+1)/2 with a proof, geometric sums, harmonic-number intuition (n/1 + n/2 + … ≈ n log n); counting steps in nested loops with dependent bounds.
- **L3:** formal cost models: unit-cost RAM vs bit-cost, and why big-integer arithmetic in Python breaks the "adding two numbers is O(1)" assumption (`int` is arbitrary precision; show the measurement); the cost of a Python operation is not one step (a list append, a dict lookup, a string slice, a function call, `len`); counting recursion calls; proof of the arithmetic series; derivation of the number of halvings as ⌊log₂ n⌋ + 1; empirical growth-rate estimation by doubling ratio (T(2n)/T(n)) and log-log slope, with a pure-Python least-squares fit.
- **L4:** hidden multipliers in real runtime (cache effects, interpreter overhead, memory allocation, GC) and why step counting predicts shape, not seconds; crossover points (when O(n²) with a small constant beats O(n log n)); tooling: a reusable `StepCounter` / instrumentation decorator and a doubling-ratio analyzer with caveats; false conclusions from small n, noise, or one data point.
- **Must include:** the instrumented-counter library with tests, a growth-class table with n = 10 … 10⁶ computed by script (state when the number is too large to print and how it is represented), the three proofs above, and the doubling-ratio analyzer.

## Unit 3 — Big-O notation
- **L1:** Big-O as "grows no faster than, up to a constant, for large n"; informal ordering O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!); dropping constants and lower-order terms; reading Big-O off simple code; common mistakes (O(2n) vs O(n), O(n + m) vs O(n)).
- **L2:** the formal definition of **O, Ω, Θ, o, ω** with plain-language reading of each; how to **prove** f(n) = O(g(n)) by exhibiting constants c and n₀ (worked proofs: 3n² + 2n + 5 = O(n²), n log n = O(n²), 2ⁿ is not O(nᵏ) sketch); multiple variables (O(n + m), O(n·m)); Big-O for functions of several inputs, and why you must name what n is (the **size of the input**: number of elements vs number of bits, e.g., primality testing by trial division is not polynomial in the bit length); the rules (sum, product, transitivity), with proofs for the sum rule.
- **L3:** the classic misconception that O means "worst case" (it is an upper bound on a function; the function may be best, average, or worst-case time); tight vs loose bounds; **Θ as the honest statement**; limit-based comparison (explained without calculus requirement; optional note for those with calculus); polylogarithmic and sub-polynomial classes; logarithm base irrelevance proof (change-of-base); Stirling-type bound for log(n!) = Θ(n log n) as a stated result with intuition; function-growth ordering exercises with proof; pitfalls: O(n) with a huge constant, "amortized" vs "average" confusion (forward link to Unit 5).
- **L4:** asymptotics vs engineering: when Big-O is the wrong tool (small n, constants, cache behavior, I/O-bound code); how to **document complexity in code** (docstring convention: time, space, worst/avg/amortized, assumptions, what n means), and how to **review** a complexity claim; automated claim checking: a script that compares a docstring-declared class to an empirically fitted class and flags disagreement; Big-O in API contracts (what a library promises vs what an implementation happens to do).
- **Must include:** a formal-proof worked set (≥ 6 proofs, increasing difficulty), a function-ordering exercise set with solutions, a complexity-docstring standard with a validator script, and a table of the **misconceptions** with a counterexample for each.

## Unit 4 — Time vs space complexity
- **L1:** time vs space; counting extra memory: variables, copies, new lists; in-place vs out-of-place; auxiliary space vs input space; examples: reverse a list in place vs by building a copy, duplicate detection with O(1) extra space (O(n²)) vs O(n) extra space (O(n)).
- **L2:** the **call stack** as space (recursion depth), with Python's recursion limit (`sys.getrecursionlimit`) and a demonstration of `RecursionError`; space of slicing (`lst[1:]` copies — a hidden O(n)), string concatenation, list comprehensions vs generators, `itertools`, `sorted` (O(n) extra) vs `list.sort` (in place; auxiliary space as documented `[VERIFY]`); measuring memory with `sys.getsizeof` (shallow, and why it misleads for containers) and `tracemalloc` (peak allocation); time-space trade-offs: memoization, precomputed lookup tables, hashing, caching with `functools.lru_cache` and the memory it holds.
- **L3:** space accounting rules (input vs auxiliary vs output space) and how to state each; recursion stack depth analysis (e.g., naive recursion O(n) stack for linked list traversal, O(log n) for balanced divide and conquer, O(n) worst case for quicksort and how the smaller-side-first trick bounds it); streaming and one-pass algorithms with bounded memory (running max, running mean via Welford's algorithm, reservoir sampling named with forward link to module 14); object overhead in CPython (per-object header, `__slots__`, `array.array` vs `list` for numbers) shown by measurement; time-space lower-bound intuition (e.g., you cannot answer exact distinct-count over a stream in o(n) bits, stated as a result with a forward link to module 17).
- **L4:** designing under a **memory budget**: choose between O(n) memory fast and O(1) memory slow with explicit numbers for a 1M-event and a 1B-event stream; external-memory thinking (data larger than RAM, chunked processing, `mmap` named with link to module 18); memory leaks vs memory growth (caches, closures, global references) and how to diagnose with `tracemalloc` snapshot diffs; cache-friendly vs cache-hostile layouts (conceptual, with a measured Python demo and honest limits of Python's ability to show it); documenting space in code.
- **Must include:** a memory-profiling lab with `tracemalloc` snapshot comparison, a `RecursionError` lab and its iterative rewrite, the running example solved under three memory budgets, and a time-space trade-off table with measured evidence.

## Unit 5 — Amortized analysis
- **L1:** the problem: an operation that is usually cheap and occasionally expensive; dynamic array growth; "average cost over a sequence of operations"; the difference between **amortized** and **average-case** (amortized is a worst-case guarantee over a sequence, with no probability); watching `list.append` cost through `sys.getsizeof` jumps and timing spikes.
- **L2:** the three methods, each with a worked proof: **aggregate** (total cost of n appends with doubling = O(n), so O(1) amortized), **accounting** (charge 3 per append; credit pays for copying), **potential** (define Φ, show amortized cost = actual + ΔΦ); the binary counter increment (O(1) amortized, O(log n) worst case); stack with multipop; why a growth factor must be multiplicative (additive growth gives O(n) amortized per append, proved and measured); CPython's list over-allocation is **an implementation detail** (`[VERIFY]` and tag `[VERSION-SENSITIVE]`; the learner infers growth from measurement rather than trusting a number).
- **L3:** dynamic array with growth factor g: derive the amortized cost and memory overhead as a function of g (trade-off table for g = 1.5 vs 2, with the argument for reuse of freed memory stated as a known argument, not asserted as fact); shrinking policy and thrashing (why shrink at 1/4, not 1/2); amortized cost of a queue from two stacks; amortized analysis of `dict` resize and of hash tables with rehashing (conceptual; forward link to module 02); the limits: amortized O(1) does **not** bound a single operation's latency (relevance for real-time and tail latency); proofs that the potential method is valid (sum of amortized ≥ sum of actual when Φ(final) ≥ Φ(initial)).
- **L4:** latency vs throughput: when amortized bounds are unacceptable (low-latency services, GC pauses, p99 spikes) and the engineering fixes (preallocation, incremental/rehashing-in-background, de-amortization named and sketched); adversarial sequences against amortized structures; measuring tail latency of `append` with a harness and reading the histogram; a reusable **amortization checker** that records per-operation cost and verifies total/n against a declared bound.
- **Must include:** all three proof methods applied to the same structure, the additive-vs-multiplicative growth experiment with measured results, a per-operation latency histogram lab, and the two-stacks queue with a proof.

## Unit 6 — Measuring real performance in Python
- **L1:** why measure; wall-clock vs CPU time; `time.perf_counter` / `perf_counter_ns` vs `time.time`; `timeit` from the command line and as a module; reading the output; why one run is not a measurement.
- **L2:** `timeit.repeat`, choosing `number` and `repeat`, taking the **minimum** vs median and the reasoning for each (and when each misleads); fresh input per run for mutating code (in-place sort on already-sorted data); timing setup separately from the measured statement; warm-up and cache effects; garbage collection (`gc.disable()` during timing, and why it can distort; restoring it afterward); benchmarking across a ladder of input sizes and plotting runtime vs n; benchmarking pitfalls (measuring `print`, measuring list construction instead of the operation, dead-code elimination does not exist in CPython but constant folding and the peephole optimizer do — show an example).
- **L3:** statistical hygiene: noise sources (CPU frequency scaling, background load, WSL2 clock/filesystem effects, thermal throttling), reporting median and spread (IQR or percentiles, defined precisely), outlier handling without cherry-picking, confidence in a comparison of two implementations (a simple, honest approach: repeated alternating runs and a bootstrap or permutation comparison in pure Python, stated as an approach and explained); measuring **growth rate** by log-log fitting and the doubling ratio with confidence caveats; profiling vs benchmarking (`cProfile`, `pstats`, `tracemalloc`; what the profiler overhead does to the result); comparing `lru_cache` hits vs misses, `list` vs `deque` vs `array` operations.
- **L4:** a **benchmark harness** library design (timer abstraction, input generators with seeds, size ladder, repeat policy, result schema, JSON output, environment capture: Python version, implementation, OS, CPU count); regression detection and the problems of CI noise (a tolerance policy, relative comparison within the same job); CPython vs PyPy differences (JIT warm-up) as `[VERSION-SENSITIVE]` awareness; microbenchmark vs macrobenchmark and why microbenchmarks lie; writing a benchmark report a reviewer can trust (methodology, environment, raw data, caveats); optional `pyperf`/`pytest-benchmark` as awareness.
- **Must include:** the reusable harness with tests, a "benchmark that lies" lab (three deliberately flawed benchmarks and their fixes), a noise-characterization lab (run the same benchmark 30 times, show the spread), and the log-log fitter with interpretation guidance.

## Unit 7 — Best, average, and worst-case analysis
- **L1:** best, average, and worst case defined by **input choice**, not by notation; linear search (found first / last / absent); insertion sort on sorted vs reverse-sorted input; why we usually plan for the worst case; why average case needs a stated input distribution.
- **L2:** worst-case, best-case, and average-case analysis of linear search, binary search, insertion sort, and quicksort (naive pivot) with step counting and measurement; the expected number of comparisons in linear search under a uniform-position assumption (derive (n+1)/2); constructing worst-case inputs deliberately; adversarial and "typical" data in data engineering (sorted logs, many duplicates, skewed keys); hash-table behavior with good vs bad hash functions (a deliberately colliding key class in Python via a custom `__hash__`, with measured degradation).
- **L3:** **expected-case analysis with indicator random variables** (linearity of expectation) applied to randomized quicksort (expected O(n log n) comparisons — give the proof), and to the "hiring problem"/running-maximum updates (expected H_n ≈ ln n updates — show the derivation); the difference between average-case over random input vs **expected case of a randomized algorithm** (no assumption on input); probability inline from first principles (events, expectation, linearity — taught here, no prior probability assumed); the role of the input distribution; **smoothed analysis** and **competitive analysis** named only; lower bounds: the comparison-sort Ω(n log n) decision-tree argument stated and proved in outline.
- **L4:** adversarial inputs in production: algorithmic-complexity attacks (hash-flooding, regex backtracking/ReDoS, quicksort killer inputs) with a safe, local demonstration that **does not target any external system**; CPython's hash randomization for `str`/`bytes` and what it does and does not defend `[VERSION-SENSITIVE]`; choosing between a worst-case-guaranteed algorithm and a faster-on-average one (decision framework); documenting best/average/worst in an API; **P50/P95/P99 latency** as the engineering counterpart of average vs worst case; designing tests that exercise the worst case.
- **Must include:** a worst-case-input generator library, the quicksort expected-comparisons proof and a script that checks it empirically, the colliding-hash lab, a safe local ReDoS-style demonstration of exponential backtracking in the `re` module with the fix, and the running example under adversarial input.

## Unit 8 — Complexity analysis of loops and recursion
- **L1:** single loops, nested loops, loops with `i *= 2` (logarithmic), `i += k` (linear), loop bodies with their own cost; sequential blocks add, nested blocks multiply; conditionals (take the worst branch); function calls (add the callee's cost); analysis of simple recursion (factorial, sum of list, binary search recursive) by unrolling.
- **L2:** nested loops with dependent bounds (`for j in range(i)` → n(n−1)/2), logarithmic-bound loops inside linear loops (n log n), loops over a halving variable, the cost of Python built-ins inside loops (`x in list` is O(n) → hidden quadratic; `list.insert(0, x)`; `s += c`; slicing; `list.pop(0)`; `sorted()` inside a loop), a **hidden-complexity audit** of five realistic snippets; recursion trees: draw the tree, count nodes, sum the work per level; recurrences T(n) = T(n−1) + c, T(n) = 2T(n/2) + n, T(n) = T(n/2) + c, and the Fibonacci tree with its exponential blow-up and the memoized fix.
- **L3:** solving recurrences by **substitution (with induction proof)**, by **recursion tree**, and by the **Master Theorem** (state the three cases precisely for T(n) = aT(n/b) + f(n), with worked examples for merge sort, binary search, Karatsuba as a stated example, and a case where the theorem does **not** apply, e.g., T(n) = 2T(n/2) + n/log n or non-polynomial gaps); Akra–Bazzi named only; unbalanced recursion (quicksort worst case T(n) = T(n−1) + n); recursion with memoization (state-space × work-per-state); mutual recursion; recursion depth vs time as separate analyses; tail recursion in Python (CPython does **not** optimize tail calls) and converting to iteration; a worked analysis of the **subset-generation** (2ⁿ) and **permutation** (n!) recursions.
- **L4:** analyzing code you did not write: a reading procedure (identify n, identify the dominant loop/recursion, find hidden costs, state assumptions); probabilistic loop bounds; analysis through **amortized** reasoning (e.g., a pointer that never moves backward — two-pointer loops are O(n) despite nesting; forward link to module 03); an **automated analyzer**: a tool using `ast` to flag nested loops, `in` over lists inside loops, string `+=` in loops, and recursion without a base case, with honest limits (static heuristics are not proofs); a code-review rubric for complexity; teaching others to read complexity.
- **Must include:** a recurrence-solving worksheet with ≥ 12 solved recurrences (substitution, tree, Master Theorem, at least one non-applicable case), a hidden-complexity audit lab, the `ast`-based linter with tests, and the Fibonacci naive/memoized/iterative comparison with measurement.

## Unit 9 — Comparing algorithmic complexities
- **L1:** comparing growth classes side by side with a table and a plot; which is "better" depends on n; choosing between two algorithms using their Big-O; a decision tree for the running example; reading complexity off an API's documentation.
- **L2:** a **complexity cheat sheet** for Python built-ins (`list`, `dict`, `set`, `deque`, `heapq`, `bisect`, `str`, `sorted`, `sum`, `max`, `min`, `in`, slicing, `append`, `pop`, `insert`, `extend`, `count`, `index`, `join`) — every non-obvious entry tagged `[VERIFY: Python Wiki TimeComplexity page and implementation notes]` and each of at least eight entries **confirmed by a benchmark the learner runs**; comparing a sort-based vs hash-based solution of the same problem; constraint-based target complexity (n ≤ 10⁵ → O(n log n); n ≤ 20 → exponential acceptable) with Python-specific caveats and the stated order of magnitude of Python's speed marked `[ILLUSTRATIVE — measure yours]`.
- **L3:** the **practical comparison method**: asymptotics + constants + input size + memory + implementation complexity + maintainability; **crossover analysis** (find n* where two algorithms swap, estimated by measurement and by model); hybrid algorithms and why they exist (Timsort's use of insertion sort on small runs — described from documentation `[VERIFY]`); worst-case vs average-case selection; the impact of the memory hierarchy at a conceptual level; **lower bounds** as comparison tools (you cannot beat Ω(n log n) for comparison sorting; what that means for the choice of counting sort, with a forward link to module 05); parallel and vectorized alternatives named honestly (NumPy as a contrast, with the same running example, clearly labeled as "different cost model: C loops");
- **L4:** building a **decision framework** for algorithm selection in a design review (inputs: n, distribution, memory, latency target, correctness risk, team familiarity), with a written decision-record template; scaling from 10⁴ to 10⁹ records (what changes: memory, I/O, distribution, sampling, approximation — forward links to modules 17–19); the cost of *premature* optimization and of *premature* pessimization; communicating a complexity trade-off to non-specialists; a **complexity budget** in a service (SLO → target complexity → test); a regression test that guards complexity in CI.
- **Must include:** the built-ins cheat sheet with confirmation benchmarks, a crossover-finding lab, a decision-record template filled for the running example, and a final "same problem, five implementations" comparison with measured results and a written recommendation.

# 7. PRACTICE QUESTIONS (UNIT 10) — REQUIREMENTS

Generate a full `practice-questions.md` body with **at least 150 questions**: ≥ 14 for each of Units 1–9, plus ≥ 20 cross-unit integration questions. Required distribution per unit (≥ 14 each):

- 4 × conceptual short-answer
- 3 × multiple choice (4 options; answer + explanation of every distractor)
- 3 × code analysis ("state the time and space complexity and justify")
- 2 × proof/derivation (loop invariant, induction, constants c and n₀, recurrence)
- 1 × measurement/benchmark interpretation ("Given this output, what is wrong with the benchmark or the conclusion?")
- 1 × code review / bug-finding (find ≥ 3 defects, including at least one hidden complexity)
- (Units 3–9) 1 × design question with a rubric

Every question carries: ID, level (L1–L4), objective it tests, time estimate, **model answer**, and **common wrong answers**. Include a difficulty progression and a scoring rubric with pass thresholds (80% proceed; 60–79% remediate; below 60% repeat, consistent with the stage's gate rules). Include 8 "whiteboard / design-review" prompts requiring written trade-off reasoning. Include 15 timed "interview-style" problems (15 minutes each) with model solutions, each asking the candidate to state the complexity aloud. Each question must test only content actually taught in Units 1–9.

# 8. SECTION NUMBER INTENTIONALLY UNUSED

(Kept so that section numbers match the other Stage 3 prompts. Nothing to generate here.)

# 9. UNIT 11 — PROJECTS README (REQUIREMENTS)

Include: purpose of the `Projects/` folder; how the project relates to Units 1–9 and to the Stage 3 toolkit (`../../00-Stage-3-Overview/Projects/01-algorithm-toolkit-and-benchmark.md`); project index table (file, goal, estimated time, prerequisites, outputs); submission and evidence folder structure; the 100-point grading scheme summary and pass thresholds; originality and AI-assistance policy (allowed for explanation and review, not for producing the graded implementations, always disclosed in the evidence log); an evidence-log template; a reproducibility checklist (seed, versions, machine info, command log); a "how to ask for a code review" template.

# 10. UNIT 12 — PROJECT: BENCHMARK PYTHON COLLECTIONS (REQUIREMENTS)

**Project:** *Benchmark Python Collections.* The learner builds a reproducible benchmark suite that **measures and explains** the cost of core operations on `list`, `dict`, `set`, `tuple`, `str`, `collections.deque`, `heapq`, `bisect` on a sorted list, `array.array`, and `collections.Counter`/`defaultdict`, then compares measured growth against the documented/theoretical complexity and writes a defensible report.

This unit follows the four levels and the N.0–N.14 skeleton **plus** the project specification below.

**Scenario:** A data team keeps writing code like `if x in big_list` inside loops and `list.pop(0)` queues. The learner produces evidence-based guidance for the team: which operation is cheap, which is not, where the cliffs are, and how sure they are.

**Required deliverables (each with acceptance criteria that can be checked by command):**
1. Repository layout (`src/` layout, `tests/`, `bench/`, `results/`, `docs/`, `pyproject.toml`) and a `Makefile` (or `justfile`) with targets: `install`, `lint`, `test`, `bench`, `fit`, `report`, `check`, `clean`, `all`.
2. A **benchmark harness** (Unit 6): seeded input generators, fresh input per run for mutating operations, size ladder, warm-up, repeat policy, median and p95 (stated), GC policy documented, environment capture, JSON results schema.
3. A **benchmark catalogue of ≥ 40 operations** with, for each: operation, data structure, declared complexity (from documentation, tagged `[VERIFY]` where needed), input-size ladder, expected growth class, and risk of measurement artifact. It must include at least: `list.append`, `list.insert(0, x)`, `list.pop()`, `list.pop(0)`, `x in list`, `list.index`, `list.sort`, `sorted`, slicing, `dict` get/set/delete/`in`, `set` add/`in`/union/intersection, `str +=` in a loop vs `''.join`, `deque.appendleft`/`popleft`, `heapq.heappush`/`heappop`/`nsmallest`, `bisect.insort`/`bisect_left`, `Counter` build, `array.array` vs `list` memory, and `lru_cache` hit vs miss.
4. **Growth-rate fitting** (Unit 2/6): pure-Python log-log least-squares slope and doubling ratio per operation; classification into a growth class with an explicit tolerance policy and a confidence statement; a table of **declared vs observed** class with agree/disagree and an explanation of every disagreement.
5. **Amortization and latency study** (Unit 5): per-operation latency histogram for `list.append` and `dict` insertion across resizes; identification of spikes and their relation to resizing.
6. **Memory study** (Unit 4): bytes per element for `list`, `tuple`, `set`, `dict`, `array.array`, `str` of various sizes, measured with `tracemalloc` and `sys.getsizeof` (and an explanation of the difference).
7. **Adversarial and worst-case study** (Unit 7): colliding-hash keys in a `dict`/`set`; sorted vs random input for insertion/`bisect.insort`; `heapq` on sorted input; a safe local regex backtracking demonstration.
8. **The running-example comparison** (Unit 9): duplicate detection implemented five ways (brute force, sort, set, `Counter`, a streaming bounded-memory variant), benchmarked over the size ladder, with crossover analysis and a written recommendation.
9. **Correctness tests:** each benchmark target has a test asserting the operation's result is correct (a fast wrong answer is not a result), and tests for the harness, the fitter, and the report generator.
10. **Regression guard:** `make check` fails if a measured growth class exceeds the declared class by more than the stated tolerance (and documents how to avoid flaky failures: relative comparison, sufficient sizes, repeats).
11. **Report generator:** a Markdown report (and optional PNG plots) with the methodology, environment, raw-data pointers, tables, fitted exponents, declared vs observed classes, caveats, and recommendations.
12. **Documentation:** architecture diagram, ADRs (≥ 3: statistic choice, GC policy, tolerance policy), a "limits of this benchmark" section, and a one-page **team guidance sheet** ("operations to avoid in hot loops and what to use instead").
13. **A results template** the learner fills with their own measurements. Provide the template; do not fabricate results.

**Include:** a milestone plan (5–6 milestones with time estimates), a grading rubric (100 points, criterion-level descriptors for Poor / Adequate / Strong / Exemplary), stretch goals (add PyPy comparison if installed, add `pyperf`/`pytest-benchmark` cross-check, `numpy` contrast, profile with `cProfile`, publish a short write-up), common failure points (benchmarking mutated input twice, tiny sizes inside the noise floor, one run per size, ignoring GC, mis-reading slopes, measuring construction instead of the operation), a self-review checklist, and the exact evidence folder structure.

**Provide complete, runnable starter code** for the harness, generators, catalogue, fitter, latency study, memory study, report generator, tests, Makefile, and `pyproject.toml`. Every code file states its path in a first-line comment. Do not leave `TODO: implement` in required deliverables. Dependencies: standard library plus `pytest` for required parts; everything else optional.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: src/bigo_bench/harness.py`).
2. **Every command and snippet is paired with expected output** (representative, clearly labeled "example — yours will differ in timings, sizes, and memory addresses") and a short interpretation.
3. **Code must run.** Python 3.10+ syntax only (state if 3.12 is required). Standard library unless marked optional. Type hints on all public functions. Clarity over cleverness.
4. **Complexity statements must be precise:** state whether a bound is worst-case, average-case, expected, or amortized; give time **and** space; state what n is; include the proof sketch or invariant for every non-trivial claim; separate the algorithm's complexity from CPython's constant factors and implementation details.
5. **No unproven performance claims.** Every speed or size claim ties to a measurement the learner can run with the method stated (warm-up, repeats, statistic). Otherwise label it `[ILLUSTRATIVE — measure yours]`. Never present a measured-looking number that was not measured; example outputs are labeled **representative**.
6. **Benchmarks must avoid the usual errors:** reusing mutated input, measuring inside the noise floor, one size only, a single run, ignoring GC and caching, confusing wall time with CPU time, measuring setup instead of the operation.
7. **No secrets, no network access, no paid APIs** in any lab. Adversarial demonstrations (hash collisions, regex backtracking) run **only locally against the learner's own code** with bounded size and a timeout, and the text says so.
8. **Scripts are safe by default:** no deletion outside the project directory; `clean` targets list what they remove; random generators take explicit seeds; long-running experiments have a documented size cap and a `--quick` mode.
9. **Every test shows how to run it** and what a failing run looks like (break the code on purpose once).
10. **Every lab ends with cleanup** and a verification that no stray files or processes remain beyond those documented.
11. **Tag Python-version and implementation differences** (CPython vs PyPy, 3.10 vs 3.12) `[VERSION-SENSITIVE]`.
12. **WSL2 notes:** call out timing-noise sources and the `/mnt/c` vs Linux filesystem difference where they affect a lab.
13. **Proofs are written in full** where required (constants c and n₀ stated; induction base case and step shown; invariant initialization/maintenance/termination all shown). "It is obvious" is not a proof.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You will act as author, then as an independent auditor of your own work, and you will include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every claim on **authoritative sources**: the official Python documentation (Language Reference; Library Reference pages for `timeit`, `time`, `tracemalloc`, `sys`, `gc`, `collections`, `heapq`, `bisect`, `functools`, `array`, `statistics`, `re`; the "Data model" section; the "What's New" pages for version-sensitive behavior), the Python Wiki **TimeComplexity** page for built-in operation costs, CPython source/documentation notes for implementation details (marked `[VERIFY]`), and standard texts cited by **title and chapter topic, not page numbers you cannot confirm**: *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein) — growth of functions, amortized analysis, recurrences, probabilistic analysis; *Algorithms* (Sedgewick and Wayne) — analysis of algorithms; *The Algorithm Design Manual* (Skiena) — algorithm analysis; *Concrete Mathematics* (Graham, Knuth, Patashnik) for summations and recurrences (awareness). Provide a URL only if you are certain it is canonical; otherwise cite by name and mark `[VERIFY]`.
- **Do not fabricate:** version numbers, benchmark results, timings, memory sizes presented as universal, CPython growth-factor constants, CVE or incident details, company practices, interview statistics, or quotes. If you need a number, derive it from a stated command or label it illustrative.
- **Mark uncertainty** with: `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[ASSUMPTION]`, `[JUDGEMENT]`.
- Keep a running **Claim Register** (Section 12.3) for every non-trivial claim.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 12 units present, in order, with every required section (Sections 5, 7, 9, 10), every unit-specific topic (Section 6), levels L1–L4. | Any missing section/topic. |
| 2 | **Mathematical correctness** | Every derivation, sum, recurrence solution, and proof is re-derived independently and checked at small n by hand or by a stated script; definitions of O/Ω/Θ/o/ω are exact; c and n₀ actually work. | Any wrong formula, invalid proof, or unjustified step. |
| 3 | **Technical accuracy** | Every Python function, signature, behavior, and complexity attribution is real and correct. Mentally execute every code block and lab. | Any invented function, misused API, or wrong bound. |
| 4 | **Executability** | Code blocks are syntactically valid; imports resolve; file paths and cross-references resolve; every test passes on the reference code and fails on a deliberately broken variant; every lab has steps, expected evidence, and cleanup. | Any broken, ambiguous, or unrunnable step. |
| 5 | **Complexity labeling audit** | Worst/average/expected/amortized labels are right; space includes recursion stack and auxiliary storage; "n" is always defined; amortized is never confused with average; Θ is used when tight; O is never described as "worst case". | Any mislabeled or ambiguous bound. |
| 6 | **Benchmark validity** | Methodology is sound (warm-up, repeats, statistic stated, fresh inputs for mutating code, GC policy, multiple sizes, noise acknowledged); fitted slopes are interpreted with caveats; no result is presented as measured unless it is clearly labeled representative or a template. | Flawed method or fabricated numbers. |
| 7 | **Currency** | Version-sensitive claims tagged; no deprecated Python feature taught as current; 3.10 minimum respected or differences noted; CPython implementation details are not presented as language guarantees. | Stale, untagged, or over-general claims. |
| 8 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated benchmark outputs, made-up CPython internals, and invented library features. | Any unsupported specific. |
| 9 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept (e.g., logarithm, expectation, induction) used before it is taught; terminology consistent; math stays at school-algebra level plus what is taught inline; the running example evolves coherently. | Forward dependency without a note; terminology drift. |
| 10 | **Cross-consistency** | Practice questions test only taught content; every project deliverable maps to a unit; the cheat sheet, benchmarks, and project catalogue agree; checklists agree with lessons; Unit 11 promises nothing Unit 12 does not deliver; links to the Stage 3 Overview and later modules are correct. | Orphan question, orphan deliverable, or contradiction. |
| 11 | **Adversarial review** | Re-read as a skeptical staff engineer and as a hostile interviewer: "What here is wrong, misleading, or would teach a bad habit?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 12 | **Reproducibility** | Labs run within the 4 CPU / 8 GB / 30 GB baseline, need no paid service or network, are seeded and idempotent, have size caps and a `--quick` mode, and clean up. | Hidden cost, unseeded nondeterminism, or leftover state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendices)

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. Include at least **60 entries**, covering every built-in complexity claim, every CPython behavior claim, every theorem or formula used, and every judgement of consequence.

**Appendix B — Audit Report** (table for passes 1–12): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** all `[VERIFY]` / `[VERSION-SENSITIVE]` / `[JUDGEMENT]` items grouped by area (CPython data model and built-ins, standard-library modules, complexity claims, mathematical results, benchmark methodology), each with: *what to check*, *where to check (named source)*, *how to test it locally with one command or small script*. The reviewer must be able to close every item in under 3 hours.

**Appendix D — Known Limitations and Assumptions:** what the module intentionally does not cover (e.g., formal Akra–Bazzi, advanced probabilistic analysis, cache-oblivious analysis, parallel complexity), assumed Python version, CPython-vs-PyPy caveats, WSL2 timing caveats, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code, proofs, and benchmarks.

**Appendix F — Formula and Proof Index:** every formula and proof in the syllabus with its unit, statement, and proof technique, so a reviewer can check each in one place.

**Appendix G — Executable Verification Bundle:** a single `verify_syllabus.py` script (standard library only) that extracts every fenced Python block with a `# File: …` first-line comment, writes them to a scratch directory, byte-compiles them (`py_compile`), runs the test suite in `--quick` mode, and prints a PASS/FAIL list; plus a `verify_math.py` that numerically checks the key identities and recurrence solutions at small n (arithmetic series, geometric series, harmonic bound, halving count, Master Theorem examples, the quicksort expected-comparison formula by simulation with a fixed seed).

## 12.4 Trust rules
- If an audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it actually was in your environment. Use "expected output (representative)" instead.
- Never state that content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.
- Statements about **CPython internals** (growth pattern of `list`, dict resize points, Timsort details, small-int caching, hash randomization) are implementation details. State them as such, tag `[VERSION-SENSITIVE]`, and prefer teaching the learner to **measure** them over asserting them.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-Complexity-and-Big-O.md`.
- Start with: title, one-paragraph abstract, metadata block (`Module: S3-01`, `Stage: 3`, `Language: Python`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 1–12 in order, then Appendices A–G.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons, fenced code blocks for all code, mermaid for diagrams, plain-text math (e.g., `T(n) = 2T(n/2) + n`) with Unicode symbols where clear; avoid LaTeX that may not render.
- Each unit is **self-contained but cross-linked** (relative links to sibling target files, the Stage 3 Overview, and later modules).
- **Depth target:** Units 1–9 each ≥ 2,500 words of teaching text excluding code; practice questions ≥ 150 items; project spec complete with all code. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 1 |
| 2 | Unit 2, Unit 3 |
| 3 | Unit 4, Unit 5 |
| 4 | Unit 6, Unit 7 |
| 5 | Unit 8, Unit 9 |
| 6 | Unit 10 (practice questions) |
| 7 | Unit 11 (Projects README), Unit 12 part A: N.0–N.8 and project specification with scaffold, harness, and catalogue code |
| 8 | Unit 12 part B: fitter, studies, report generator, tests, N.9–N.14, rubric, results template |
| 9 | Appendices A–G (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/9 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–12, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 9 must run the **cross-part** audit (passes 9, 10, 11 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you are approaching the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 9, print the final assembly instruction: "Concatenate Parts 1–9 in order into `SYLLABUS-Complexity-and-Big-O.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 12 units present, in the specified order; Units 1–9 and 12 each with levels L1–L4 and sections N.0–N.14.
- [ ] Every unit-specific topic in Sections 6, 7, 9, and 10 is taught at its stated level.
- [ ] Every required proof is written in full (invariants, induction, constants c and n₀, recurrences by substitution, tree, and Master Theorem).
- [ ] The ≥ 150 practice questions have model answers and distractor analysis; the 15 timed interview problems have model solutions.
- [ ] The project has complete runnable code, ≥ 40 cataloged operations, acceptance criteria, a rubric, and a results template with **no fabricated results**.
- [ ] Every complexity claim is correctly labeled (worst/average/expected/amortized, time and space, n defined) and every performance claim is tied to a measurement or tagged illustrative.
- [ ] Every CPython implementation detail is tagged `[VERSION-SENSITIVE]` and presented as something to measure, not assume.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and a `--quick` mode; all run within the free local baseline.
- [ ] No fabricated statistics, citations, versions, timings, or incident details; every uncertain item is tagged.
- [ ] Appendices A–G present; Claim Register ≥ 60 entries; audit passes 1–12 reported candidly.
- [ ] `verify_syllabus.py` and `verify_math.py` are delivered and consistent with the file-path comments in the code.
- [ ] A human can verify every open item in under 3 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/9**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 9 parts so the Claim Register and the running duplicate-detection example stay consistent.
2. **Do the human verification yourself.** Run `verify_syllabus.py` and `verify_math.py` (Appendix G), re-derive a sample of the proofs by hand, run the benchmarks on your machine, and close each `[VERIFY]` item against the Python docs and the Python Wiki TimeComplexity page.
3. **Spot-check fabrication risk areas first:** CPython list/dict growth behavior, Timsort claims, small-int and string interning claims, hash-randomization claims, `tracemalloc` vs `getsizeof` behavior, Master Theorem case statements, and any timing number that is not clearly a template.
4. **Scope note:** the folder's `README.md` is intentionally excluded, as it is not in the unit list you gave. Generate it with a separate prompt, or ask me to add it as a Unit 0.
5. **Final file layout:** save the LLM output as `SYLLABUS-Complexity-and-Big-O.md` in this folder. Later, split it into the 12 target files (`01-…09-…`, `practice-questions.md`, `Projects/README.md`, `Projects/01-benchmark-python-collections.md`).
