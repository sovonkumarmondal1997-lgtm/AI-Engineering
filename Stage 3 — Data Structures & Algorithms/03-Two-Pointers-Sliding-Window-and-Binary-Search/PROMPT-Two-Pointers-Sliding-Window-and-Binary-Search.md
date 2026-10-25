# PROMPT — Generate `SYLLABUS-Two-Pointers-Sliding-Window-and-Binary-Search.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Software Engineer with 15 years of industry experience** across backend systems, data platforms, and applied ML infrastructure. You have written rate limiters and windowed log analytics, shipped a binary search with an off-by-one that only failed on the last element, tuned capacity thresholds by searching over a monotone predicate, and interviewed hundreds of candidates on exactly these patterns. You teach the way you work: **state the invariant, prove the pointer move is safe, then test the boundaries.**

You are also a careful technical author. You never invent a function, a complexity bound, a signature, a default, a version, or a statistic. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 3 — Data Structures & Algorithms / 03-Two-Pointers-Sliding-Window-and-Binary-Search/` (module code **S3-03**)

Output file name: **`SYLLABUS-Two-Pointers-Sliding-Window-and-Binary-Search.md`**

All code, labs, and examples are in **Python**.

It must teach, **one after another, from beginner to advanced**, these 12 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 1 | Two pointers | `01-two-pointers.md` |
| 2 | Sliding window | `02-sliding-window.md` |
| 3 | Binary search | `03-binary-search.md` |
| 4 | Binary search on the answer | `04-binary-search-on-the-answer.md` |
| 5 | Pattern recognition drills | `05-pattern-recognition-drills.md` |
| 6 | Fast and slow pointers | `06-fast-and-slow-pointers.md` |
| 7 | Interval-based problem patterns | `07-interval-based-problem-patterns.md` |
| 8 | Sorting and searching combinations | `08-sorting-and-searching-combinations.md` |
| 9 | Invariants and search-space reduction | `09-invariants-and-search-space-reduction.md` |
| 10 | Practice questions | `practice-questions.md` |
| 11 | Project: Log window analyzer | `Projects/01-log-window-analyzer.md` |
| 12 | Project: Search and window pattern library | `Projects/02-search-and-window-pattern-library.md` |

Do **not** add, merge, skip, or reorder units. The folder's `README.md` and `Projects/README.md` are **out of scope for this syllabus**; do not write them (treat them as "defined separately"). Where a unit needs to reference the Projects index, link to `./Projects/README.md` and do not invent its contents. Do not produce shallow summaries: this is the **teaching content itself**, not an outline of it.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI Engineer who has finished Stages 0–2E, S3-00 (Stage 3 Overview), S3-01 (Complexity and Big-O) and S3-02 (Arrays, Strings, and Hashing). They can analyze loops, prove simple bounds, write loop-invariant arguments, use prefix sums and hash maps, and benchmark with `timeit`. They know the *names* sliding window, binary search and Kadane from earlier previews but have **not** been taught the patterns rigorously. They cannot yet get binary-search boundaries right reliably.
- **Stage position:** Stage 3 comes **before** the math stages (4A/4B/4C). Assume school algebra plus S3-01/S3-02. Teach inline from first principles: the idea of a **monotone predicate** (a yes/no function that flips once), the number of halvings (⌈log₂ n⌉), closed vs half-open intervals as a counting convention, and the distance arithmetic behind cycle detection. Forward-link to Stage 4A for depth.
- **Zero budget.** All work runs on a **local laptop** (WSL2 Ubuntu primary, native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid service, no network required.
- **Tool baseline (required):** **CPython 3.12** `[ASSUMPTION — state minimum 3.10 and note differences, especially the `key=` parameter of `bisect` functions, added in 3.10 `[VERIFY]`]`, `venv`, `pytest`, `timeit`, `time.perf_counter_ns`, and the standard library (`bisect`, `collections.deque`, `collections.Counter`, `heapq`, `itertools`, `functools`, `math`, `random`, `statistics`, `datetime`).
- **Optional helpers (flag as optional):** `hypothesis`, `matplotlib`, `ruff`, `mypy`, `numpy` (contrast only: `searchsorted`, different cost model), `sortedcontainers` (awareness).
- **Domain flavor:** after Level 1, examples come from systems a data/AI engineer meets: windowed log analytics, rate limiting and burst detection, moving averages over metrics, deduplicating sorted records, merging sorted event streams, session and time-range queries, capacity planning by search over a monotone constraint, finding the smallest batch size or threshold that meets a target, locating a regression with a bisect-style search over versions or commits, and deadline/overlap scheduling. Avoid toy-only examples beyond L1.
- **Running example thread:** one scenario, **"a sorted stream of timestamped service events"**, evolves through the folder: find pairs of events with a target time gap (two pointers) → compute the busiest window and rolling statistics (sliding window) → locate a timestamp or threshold (binary search) → find the smallest capacity that satisfies an SLO (search on the answer) → detect a cycle in a retry/dependency chain (fast/slow) → merge outage intervals (intervals) → combine sorting and searching to answer batched queries → state the invariants that make all of it correct. Reuse it so the learner sees one problem solved through every lens.
- **Continuity and links:** link back to S3-01 (complexity, amortized analysis — *two-pointer loops are O(n) by amortization*), S3-02 (prefix sums, hash maps, Kadane, Dutch national flag partitioning) and the Stage 3 toolkit (`../00-Stage-3-Overview/Projects/01-algorithm-toolkit-and-benchmark.md`); forward to module 04 (stacks/queues/linked lists: monotonic deque, linked-list structure), 05 (sorting), 07 (heaps), 09 (DP), 11 (greedy: interval scheduling proofs), 13 (range queries), 14 (sweep line, advanced two-pointers/window, binary search on the answer at scale). State clearly what is **taught here vs. deferred**: e.g., this module teaches intervals with sorting and merging; sweep-line and difference-array depth are deferred to module 14; greedy-exchange proofs for interval scheduling are previewed here and proved in module 11; the minimal singly linked `Node` class is introduced here for fast/slow pointers and fully developed in module 04.

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–9 AND UNITS 11–12)

Each of these units progresses through **exactly these four levels**. Use identical headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the pattern, runs the basic Python snippet, reads the result. |
| **L2** | Intermediate — Working Practice | Applies the pattern to realistic data/AI code, follows standard templates, avoids common mistakes. |
| **L3** | Advanced — Engineering Rigor | States and proves correctness (invariants, why a pointer move never skips an answer) and bounds, defends decisions with evidence. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses subtle failures, handles adversarial and streaming input, builds tooling, and could coach another engineer. |

Unit 10 uses the structure in Section 7. Unit 5 follows the four levels but is organized as **drills** (see its requirements).

# 5. MANDATORY STRUCTURE FOR UNITS 1–9 AND 11–12

Use this exact skeleton, in this order. Do not omit a section; if one is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete engineering failure this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, each starting with an action verb: implement, prove, measure, derive, justify…
Tag each with its level L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception.)
(One mermaid or ASCII diagram of the pointer/window/search-space state.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why it works, not only what to type)
- Guided exercise with exact Python code, expected output, and how to read it
- "What just happened?" walkthrough (trace table showing pointer positions at every step)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic example (complete, runnable Python), continuing the running example
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad code → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Formal statement and proof of correctness (invariant: initialization, maintenance, termination; and the "pointer move never discards a valid answer" argument) and of complexity
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure, with which tool, how to avoid fooling yourself)
- Exercise that requires a defended argument, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial and scale concerns (worst-case inputs, huge n, streaming, memory limits, floating point)
- Automation (differential and property-based tests, boundary-test generators, regression guards)
- Team concerns: design-review checklist, how to coach others, how to document the invariant in code
- Edge cases and platform differences (CPython vs PyPy, Python 3.10 vs 3.12, WSL2 vs native)

### N.7 Engineering lens
- Where this shows up in real systems (name the system class; never fabricate a company claim)
- Failure modes and blast radius (what breaks, for whom, how you would notice)
- Cost, capacity, and performance notes

### N.8 Integrity lens
- Reasoning and measurement risks (off-by-one, infinite loops, non-monotone predicates, unsorted input assumed sorted, mutated windows, benchmark self-deception)
- Controls and how to verify each with a command, a test, or a written check

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
(5 questions with senior-level model answers, including the complexity statement spoken aloud.)

### N.14 Sources and verification notes
(References by name and section; items tagged [VERIFY]; version-sensitive claims.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated. Every algorithm is taught with: problem statement and specification (including the empty-input and not-found policy), brute-force baseline, the improved algorithm, an **invariant and a proof that each pointer move is safe**, time and space (worst/amortized, with n defined), edge cases, tests, and a measured comparison. Every pointer-based solution includes a **trace table** for one normal and one edge input.

## Unit 1 — Two pointers
- **L1:** what a "pointer" is in Python (an integer index, not a memory address); the two families: **opposite-ends** (`left` at start, `right` at end, moving inward) and **same-direction** (`read`/`write` or `slow`/`fast` indices); reverse an array in place; check a palindrome; pair sum in a **sorted** array (move `left` if the sum is too small, `right` if too large); why sortedness is the precondition; hand trace.
- **L2:** the template catalogue with recognition signals: *opposite-ends on sorted data* (two-sum II, container with most water, valid palindrome with skips), *read/write compaction* (remove duplicates from sorted array, remove element, move zeros — link to S3-02), *two sequences merged* (merge sorted arrays, intersection of two sorted arrays, is-subsequence), *partition with pointers* (link to the S3-02 Dutch flag), *three-sum via sort + two pointers* (with duplicate skipping; the full treatment is in Unit 8), *squares of a sorted array*, *trapping rain water with two pointers* (and its prefix/suffix alternative); handling duplicates and the "skip equal neighbors" idiom; returning indices vs values; mutation contracts (in place vs new list).
- **L3:** **proofs**: (a) pair-sum on sorted data — if `a[l] + a[r] < target` then no pair using `a[l]` and any index ≤ r can work, so discarding `l` loses nothing (full exchange-style argument, written with the invariant "if a solution exists, it lies within `[l, r]`"); (b) container-with-most-water — the greedy "move the shorter side" argument with a proof that discarding the shorter line cannot lose the optimum; (c) read/write compaction invariant (`a[:write]` is the deduplicated prefix of `a[:read]`); complexity: O(n) via **amortization** (each pointer moves at most n times; total moves ≤ n — link to S3-01 Unit 5/8); when two pointers is **not** valid (unsorted data, negative-number sums where the move rule breaks, non-monotone objective) with counterexamples; comparison with the hash-map solution (time/space/assumptions decision table); the cost of sorting first (O(n log n) dominates; space of `sorted` vs `list.sort`).
- **L4:** adversarial and edge inputs (all equal, one element, two elements, already-met pointers, overflow-free in Python but not in fixed-width languages — say so honestly); streaming and linked-structure variants (two pointers on a stream with bounded memory where possible); property-based tests with a brute-force O(n²) oracle; boundary-test generator (empty, single, duplicates at both ends, target at extremes, no solution); invariant assertions as executable checks (`assert` guarded by a debug flag, with the cost measured); coaching checklist: "what are the pointers, what does each pointer's position promise, what move preserves the promise?"
- **Must include:** the full proofs (a)–(c), a pointer-trace visualizer script that prints the state at each step, a two-pointer vs hash-map benchmark, and the first version of the running example (find event pairs with a target gap in a sorted timestamp list).

## Unit 2 — Sliding window
- **L1:** the window as a contiguous subarray `[left, right]` that expands on the right and shrinks on the left; **fixed-size window** (maximum sum of k consecutive elements; the O(n) slide: add the incoming element, subtract the outgoing one) vs the O(n·k) naive approach; hand trace; the relationship to prefix sums (S3-02) and when each is preferable.
- **L2:** **variable-size window** templates: *longest valid window* (expand always; shrink while invalid), *shortest valid window* (expand until valid; shrink while valid), *count windows* (the `at_most(k) − at_most(k−1)` identity for "exactly k"); state held in the window (running sum, a `Counter`/dict of counts, a `set`, a count of "distinct" or "unsatisfied" requirements); problems: longest substring without repeating characters (link S3-02), longest substring with at most k distinct characters, minimum size subarray sum ≥ target (positives), maximum average subarray, permutation in string / find all anagrams (fixed window with counter comparison and the O(1)-update "matches" counter), minimum window substring (the `need`/`have` counters), longest repeating character replacement, max consecutive ones with k flips, fruit into baskets; `collections.deque` for window contents; indices vs values stored.
- **L3:** **correctness**: the window invariant (e.g., "the window `[left, right]` contains no duplicate" / "the window is the longest valid ending at `right`") and **why shrinking is safe**: the **monotonicity requirement** — if a window is invalid, every larger window containing it is invalid (and its dual for shortest-valid) — proved for each template; **why the technique fails with negative numbers** for sum-based conditions (explicit counterexample) and the correct alternatives (prefix sums + hash map from S3-02; monotonic deque/Kadane-style); complexity O(n) by amortization (each element enters once and leaves at most once) with the formal potential argument; the `at_most` identity proof; **window maximum with a monotonic deque** (O(n); invariant: deque holds indices with strictly decreasing values; each index pushed and popped once) — taught here as a technique with the structure development deferred to module 04; comparison with a heap-based window maximum (lazy deletion, O(n log n)) and with the naive approach (measured); fixed vs variable window decision table.
- **L4:** **time-based windows** (window defined by timestamps, not counts: expire events older than `now − T`) and **out-of-order events** (watermarks named, bounded lateness handled with a buffer; honest limits); streaming with bounded memory; rolling statistics (mean, variance via incremental update with the numerical-stability caveat; rolling median named with a forward link to module 07); floating-point drift in running sums and the mitigation (periodic recomputation, `math.fsum` for recomputation); sliding-window rate limiter variants (fixed window counter vs sliding log vs sliding window counter — trade-offs table, no invented product claims); worst-case adversarial inputs for deque-based windows; testing with oracles and boundary generators; documenting the monotonicity assumption.
- **Must include:** the monotonicity proofs for longest-valid and shortest-valid templates, the negative-number counterexample, the monotonic-deque window maximum with its invariant proof, the `exactly k` identity with proof, a time-based window class with tests, and the running example's busiest window.

## Unit 3 — Binary search
- **L1:** the idea: halve the search space each step on **sorted** data; why it is O(log n) (halvings from S3-01); the three pointers `lo`, `mid`, `hi`; a basic implementation on a sorted list returning the index or −1; hand trace; why unsorted data breaks it.
- **L2:** **boundary-correct templates**: (1) *exact match* with closed interval `[lo, hi]` and `while lo <= hi`; (2) **lower bound** (first index with `a[i] >= x`) and **upper bound** (first index with `a[i] > x`) with half-open interval `[lo, hi)` and `while lo < hi` — presented as the **one template to master**: *find the first index where a monotone predicate becomes true*; computing `mid = lo + (hi - lo) // 2` (and the honest note that Python ints do not overflow but the idiom matters in fixed-width languages); first/last occurrence, count of occurrences (`upper − lower`), insertion position, floor/ceiling, closest element; Python's **`bisect`** module (`bisect_left`, `bisect_right`, `insort_left`/`insort_right`, the `key=` parameter `[VERSION-SENSITIVE: 3.10+]`, `lo`/`hi` parameters) and exact equivalence with the templates (prove it by test); the cost trap: `insort` is O(n) due to the list shift; searching in a sorted list of tuples/records; binary search on a rotated sorted array and on a peak/bitonic array (preview of search-space reduction, deepened in Unit 9); search in a 2-D sorted matrix (link to S3-02's staircase search).
- **L3:** **proof of correctness** for the lower-bound template with the invariant "all indices < lo satisfy ¬P; all indices ≥ hi satisfy P" and termination (the interval length strictly decreases; show why `lo = mid + 1` / `hi = mid` guarantees progress while `hi = mid - 1` with `lo < hi` can loop or skip); a catalogue of **the four classic bugs** (infinite loop from `mid` rounding, off-by-one on the closed/half-open mismatch, skipping the answer with `hi = mid - 1`, wrong return when not found) each with a failing input and the fix; the **exact comparison count** bound (⌊log₂ n⌋ + 1 for success, state precisely and test it) and the Ω(log n) lower bound for comparison-based search in a sorted array (decision-tree argument, stated with a proof sketch); binary search with duplicates and stability; comparing binary search with hash lookup, interpolation search (named with its assumptions and worst case), exponential/galloping search (O(log i) for unbounded or unknown-size sorted data — implement it), and a linear scan for small n (crossover measured).
- **L4:** binary search over **non-array structures** (a function `f(i)` evaluated lazily, a sorted file by offsets/`mmap` named with a forward link to module 18, version/commit bisection as in `git bisect` — explain the algorithm and assumptions, **do not claim implementation details of git you cannot confirm**); floating-point binary search (iteration count vs tolerance, why `while hi - lo > eps` can loop forever near the limits of precision, and the fixed-iteration alternative); comparison-function pitfalls (inconsistent ordering, NaN breaks ordering); testing: exhaustive small-input tests against `bisect` and a linear oracle for **all** targets including values below, between, and above the data; boundary-test generator; fuzzing; invariant assertions; documenting "sorted ascending, duplicates allowed, returns leftmost" in API docstrings; numpy `searchsorted` as contrast.
- **Must include:** the single predicate-based template with its invariant proof, the four-bugs lab with failing inputs, exhaustive tests against `bisect`, galloping search, a crossover benchmark (linear vs binary), and the running example's timestamp lookup.

## Unit 4 — Binary search on the answer
- **L1:** the shift in thinking: search not over array indices but over **possible answers**; the requirement — a **monotone feasibility predicate** `feasible(x)` that is false…false true…true (or the reverse); example: smallest integer whose square is ≥ n (integer square root); the search range `[lo, hi]` and how to choose safe bounds; hand trace.
- **L2:** the standard recipe in four steps: (1) define the answer space and its bounds, (2) define `feasible(x)` and **argue monotonicity**, (3) run the lower-bound template for the first feasible `x` (or the last, with the mirrored template), (4) verify with a brute force on small inputs. Problems: integer sqrt, Koko eating bananas, capacity to ship packages within D days, split array largest sum, minimum days to make m bouquets, aggressive cows / maximize the minimum distance (the *maximize-minimum* mirrored template), smallest divisor given a threshold, kth smallest in a multiplication table or in a sorted matrix, minimum time to complete trips; the feasibility check as a **greedy O(n) scan** (link to module 11), giving O(n log R) total where R is the answer range; choosing integer vs real-valued answers.
- **L3:** **monotonicity proofs** for at least four of the above (e.g., if capacity `C` suffices then `C+1` suffices — show it formally from the problem's definition), and what breaks when the predicate is **not** monotone (counterexample; the search returns garbage silently); the **correctness of the greedy feasibility check** (exchange or invariant argument — at least for shipping capacity and aggressive cows); complexity O(cost(feasible) · log R) with R derived from the data; **binary search on real numbers** (precision, fixed iteration count `⌈log₂((hi−lo)/ε)⌉`, termination proof, floating-point pitfalls); minimizing the maximum vs maximizing the minimum (the min–max duality and the two templates, with a decision table); **parametric search** named and explained as the general idea; combining with **prefix sums** or **sorting** to make `feasible` cheaper (e.g., kth smallest pair distance with two pointers inside the check); bound selection errors (too-small `hi` silently returns the wrong answer — a failing test).
- **L4:** engineering uses: finding the smallest batch size/worker count/threshold that meets an SLO, capacity planning, tuning a classifier threshold for a target precision on a monotone curve (state the monotonicity assumption honestly; precision is **not** always monotone in threshold — say so), searching for the largest input size that fits a memory budget, bisecting a regression; making `feasible` expensive (an experiment or simulation) and **bounding the number of evaluations** (⌈log₂ R⌉) as a cost model; noisy predicates and why binary search is fragile there (a robust variant: repeated trials with a confidence rule, described as an approach and marked `[JUDGEMENT]`); caching predicate results; testing with a brute-force linear scan over the answer space on small inputs; documenting the monotonicity assumption and bounds in code.
- **Must include:** ≥ 10 solved problems each with the four-step recipe and a monotonicity argument, a real-valued search with a termination proof, a non-monotone counterexample lab, a generic `first_true(lo, hi, pred)` / `last_true` library with tests, and the running example's smallest capacity meeting an SLO.

## Unit 5 — Pattern recognition drills
This unit is a **training unit**: its job is to turn the techniques of Units 1–4 (and S3-02) into fast, reliable *classification*. It still follows the four levels, but each level is organized around drills.
- **L1:** the classification vocabulary: *sorted or sortable?*, *contiguous or not?*, *pair/triple or window?*, *monotone predicate present?*, *answer over indices or over values?*; the **decision procedure** (a flowchart in mermaid and as a table) mapping problem signals to technique: two pointers (sorted + pair/partition), sliding window (contiguous + monotone validity), binary search (sorted + point query), binary search on the answer (min/max + feasibility), hash map/prefix sum (contiguous + negatives or exact-sum), fast/slow (cycle/structure traversal), intervals (ranges + overlap); 30 one-line problem statements with the technique named and the signal underlined, as worked examples.
- **L2:** **timed drills**: 40 short problem statements (≥ 4 per technique) the learner classifies in under 60 seconds each, then solves; **near-miss pairs** — two problems that look alike but need different techniques (e.g., "longest subarray with sum k" for positives vs with negatives; "pair sum in sorted vs unsorted array"; "shortest vs longest valid window"; "first vs last occurrence"); a **signal glossary** (phrases like "sorted", "contiguous", "at most k", "minimum possible maximum", "smallest x such that" and what each suggests, with counterexamples where the signal misleads).
- **L3:** **justification drills**: for each solved problem, write the three-sentence justification — *why this technique applies, what invariant it maintains, what its complexity is* — graded by a rubric; **counterexample drills** (construct an input where the wrong technique fails); **transformation drills** (rephrase a problem so a known technique applies: e.g., "exactly k" → "at most k" differences; "closest to target" → lower-bound neighbors; "kth smallest" → binary search on the answer); drills on choosing between two valid techniques by constraints (n, memory, sortedness cost), with a decision-record mini template.
- **L4:** **mixed-pattern drills** where two techniques combine (sort + two pointers + dedupe; binary search + sliding-window feasibility; prefix sums + binary search; interval merge + binary search for queries); **explain-it-to-a-peer drills** (a script template for a 5-minute explanation with the invariant); building a personal **pattern notebook** (template, signal, counterexample, three solved problems) and a script that quizzes from it with spaced repetition on the learner's own tracker (link to the S3-00 tracker; state the schedule as a chosen policy); error-log analysis (classify your own mistakes: wrong technique, boundary bug, missing precondition, complexity miss) with a tally script.
- **Must include:** the decision flowchart with every leaf reachable by at least two example problems, ≥ 70 drill items in total with answers and signal explanations, ≥ 10 near-miss pairs with the distinguishing reason, and the notebook/quiz script with tests.

## Unit 6 — Fast and slow pointers
- **L1:** the idea: two pointers moving at different speeds over a sequence or a linked structure; a minimal singly linked list (`class Node: val, next`) introduced here with a forward link to module 04; find the **middle** of a list (slow moves 1, fast moves 2); why fast reaches the end when slow is at the middle; hand trace for odd and even lengths and the **policy for the even case** (first or second middle).
- **L2:** **cycle detection** (Floyd's tortoise and hare): `slow = slow.next; fast = fast.next.next`, meeting implies a cycle; finding the **start of the cycle** (reset one pointer to the head, move both at speed 1); cycle length; problems: linked list cycle, linked list cycle II, middle of the linked list, happy number (cycle in a function iteration), **find the duplicate number** (array treated as a function `i → a[i]`; the no-modification, O(1)-space solution), palindrome linked list (middle + reverse half — mutation contract and restoring the list), remove the n-th node from the end (gap pointers: *same speed, offset start*), reorder list; the dummy/sentinel head idiom; null-pointer (`None`) safety in `fast and fast.next`.
- **L3:** **proofs**: (a) if a cycle exists, the pointers meet — the relative speed argument (fast gains 1 node per step on slow inside the cycle, so the gap shrinks by 1 modulo the cycle length and reaches 0); (b) the **cycle-start derivation**: let the tail length be `μ` and cycle length `λ`; at the meeting point slow has moved `μ + k` and fast `2(μ + k)`, so the difference is a multiple of `λ` and the distance from the meeting point to the cycle start equals `μ` modulo `λ` — hence resetting one pointer to the head and moving both at speed 1 meets at the start (write the algebra in full and verify numerically in `verify_math.py`); (c) correctness of the duplicate-number reduction (pigeonhole guarantees a cycle; the entry point is a duplicated value — prove it, including the precondition: values in `[1, n]`, array length n+1); complexity: O(μ + λ) time, O(1) space; comparison with the hash-set approach and with Brent's algorithm (named, with its constant-factor motivation), and with marking visited nodes (mutation trade-offs); when fast/slow fails (a function that is not eventually periodic does not exist for finite state spaces, but an unbounded stream may never cycle — define the termination policy).
- **L4:** cycle detection in real systems: retry/dependency chains, graph cycles (preview with a forward link to module 08, where DFS-based detection and topological sorting are developed), pseudo-random generator period reasoning and Pollard's rho named as awareness (no cryptographic claims), detecting loops in state machines and iterative data pipelines; handling **very long** chains iteratively (no recursion; the recursion limit); testing: generate lists with a cycle at every possible position and length via a seeded generator and compare against a `set`-based oracle; failure analysis of off-by-one in the even-length middle; documenting list-mutation contracts.
- **Must include:** the minimal `Node`/list-builder utilities with tests, the full cycle-existence and cycle-start proofs, the duplicate-number solution with its precondition proof, an exhaustive cycle-position test, a Floyd vs `set` memory benchmark, and the running example's retry-chain cycle detector.

## Unit 7 — Interval-based problem patterns
- **L1:** what an interval is (`[start, end]` closed or `[start, end)` half-open — a **convention that must be stated**); overlap definition (`a.start < b.end and b.start < a.end` for half-open; the closed-interval variant uses `<=`) and the **three relationships** (disjoint, overlapping, nested); representing intervals as lists/tuples/`dataclass`; sorting intervals by start; hand-merging two overlapping intervals.
- **L2:** **merge intervals** (sort by start; extend the last merged end — O(n log n)); **insert interval** (three phases: before, overlapping, after — O(n) on sorted input); **interval intersection** of two sorted lists (two pointers; advance the one that ends first); **meeting rooms I** (any overlap?) and **II** (minimum rooms: sort starts and ends separately and two-pointer, or a min-heap of end times — preview heaps with a forward link to module 07, compare both); **non-overlapping intervals / minimum removals** (sort by end — greedy, proof deferred to module 11 but the *recognition signal* and the sort-by-end rule taught here with a counterexample for sort-by-start); **remove covered intervals**; **employee free time**; **find right interval** (binary search over sorted starts, linking Unit 3); points covered by intervals; the sentinel and empty-input policies.
- **L3:** **correctness proofs**: merge intervals (invariant: `merged` is the union of the processed prefix in disjoint, sorted form; the last interval's `end` is the maximum end seen so far — why sorting by start makes a single pass sufficient); intersection of sorted lists (why advancing the earlier-ending interval never loses an intersection); minimum meeting rooms via sorted starts/ends (the invariant: the number of rooms in use at a time equals starts-seen minus ends-seen; the maximum over time is the answer); **why sort-by-end** for maximum non-overlapping intervals (exchange argument sketch with a forward link to module 11); complexity O(n log n) dominated by sorting; **interval trees** and **sweep line** named with forward links to modules 13/14 (do not teach them here); half-open vs closed pitfalls with failing tests (touching intervals `[1,2]` and `[2,3]` — overlap or not, depending on the spec); stability and tie-breaking in sorts of equal starts.
- **L4:** intervals in data engineering: time-range joins and overlap detection of sessions, outage consolidation, calendar/booking systems, coalescing adjacent ranges in a metadata store, merging sorted event streams from multiple partitions (k-way merge preview, link to module 07), range deduplication; large inputs: streaming merge on already-sorted partitions in O(1) extra space; handling timestamps (time zones, DST, inclusive end timestamps — use UTC and half-open intervals as the recommended convention, `[JUDGEMENT]` with reasoning); property-based tests (merged output is sorted, disjoint, covers the same points as the input — verified against a brute-force point-coverage oracle on small integer domains); documenting interval conventions in APIs.
- **Must include:** ≥ 10 solved interval problems with proofs where required, the touching-intervals spec lab, the merge-intervals invariant proof, the meeting-rooms two-approach comparison, a point-coverage oracle, and the running example's outage-interval consolidation.

## Unit 8 — Sorting and searching combinations
- **L1:** why sort first: sorting costs O(n log n) but can turn an O(n²) search into O(n) or O(log n) per query; Python's `sorted` and `list.sort` (stable; **Timsort** described from documentation, `[VERIFY]`), `key=` and `reverse=`; sort then binary search; sort then two pointers; a worked example that compares brute force, hash map, and sort-based solutions of the same problem.
- **L2:** **sort + two pointers**: three-sum (O(n²), duplicate skipping), four-sum / k-sum (generalization by recursion over `k` with the base case two-sum; O(n^(k−1))), three-sum closest, count pairs with sum ≤ target, two-sum less than k, valid triangle number, boats-to-save-people-style pairing; **sort + binary search**: batched queries over static sorted data, for each `x` find `target − x` with `bisect`, count elements in a range with `bisect_right − bisect_left`, smallest subarray with a property via prefix sums + binary search (positives), longest increasing subsequence via **patience sorting with `bisect`** (O(n log n), stated and implemented; DP link to module 09); **merge-based**: merge two sorted arrays, merge k sorted lists with `heapq.merge` (preview, link to module 07), counting inversions via merge sort (preview, link to module 05); custom sort keys and comparators (`functools.cmp_to_key`, largest number from digits — a comparator whose transitivity is **proved**); sort by multiple keys with stability; **search in rotated sorted array** (modified binary search, with and without duplicates and why duplicates degrade the worst case to O(n)); **median of two sorted arrays** in O(log(min(m, n))) (a hard problem taught with the partition invariant and a full correctness argument, with a brute-force oracle).
- **L3:** the **cost-model decision**: when does sorting pay for itself? derive break-even conditions (one query → scan O(n); q queries → sort once O(n log n) + q·O(log n) vs q·O(n); the learner computes the crossover q* and verifies it by measurement); **proofs**: three-sum correctness and its duplicate-skipping rule (no duplicate triplet is emitted and none is missed); the comparator transitivity proof for the largest-number problem; the rotated-array binary-search invariant (at each step at least one half is sorted, and the target's membership in the sorted half is decidable); the median-of-two-arrays partition invariant; lower bounds: Ω(n log n) for comparison sorting (decision-tree argument recalled from Unit 3/S3-01) and what it implies about when "sort first" cannot be beaten in the comparison model; non-comparison alternatives named (counting/radix, forward link to module 05) and `numpy` contrast; stable-sort-based multi-pass sorting; `sorted` with `key` evaluates the key once per element (state per documentation `[VERIFY]`) and why that matters for expensive keys.
- **L4:** sorting and searching in production data paths: external sort and sorted-file binary search (forward link to module 18), sorted indexes and range scans, batching queries by sorting them (offline processing: sort queries, sweep once), memory-bounded variants, stability requirements in multi-stage pipelines, locale-aware sorting pitfalls (`locale.strxfrm` named) and Unicode ordering surprises, sorting with `None`/mixed types (`TypeError`) and a safe key strategy, NaN in sort keys (breaks ordering — demonstrate), adversarial inputs for k-sum (quadratic/cubic blow-ups and output-size limits), differential testing against brute force and against `itertools.combinations` for small inputs, design-review checklist for "sort first?" decisions.
- **Must include:** three-sum/four-sum/k-sum with proofs and oracles, the break-even experiment for sort-then-search, patience-sorting LIS, the rotated-array search with duplicates analysis, median of two sorted arrays with its invariant proof, and the running example's batched timestamp queries answered offline.

## Unit 9 — Invariants and search-space reduction
- **L1:** what an **invariant** is (a statement true before and after every loop iteration); what a **search space** is (the set of candidates that could still be the answer); every pattern in this module as "shrink the search space without losing the answer": two pointers (candidate pairs), sliding window (candidate windows), binary search (candidate indices), cycle detection (candidate positions); the three-question habit: *what is the search space, what does each pointer guarantee, why is each move safe?*
- **L2:** writing the invariant **before** the code for each earlier unit's key algorithms and placing it as a comment; **loop variants** (a quantity that strictly decreases and is bounded below) for termination; closed `[lo, hi]` vs half-open `[lo, hi)` conventions and a **translation table** between them (what `lo`, `hi`, the loop condition, and the updates become in each convention); the off-by-one debugging procedure (test the smallest cases: n = 0, 1, 2, 3; evaluate the invariant by hand); executable invariants with `assert` and a tiny decorator/context helper that checks an invariant each iteration in debug mode; shrinking the search space in 2-D (staircase search from S3-02), in rotated arrays, in peak finding (`a[mid] < a[mid+1]` ⇒ a peak exists on the right — prove it), in bitonic arrays.
- **L3:** the **formal framework**: initialization / maintenance / termination written for **each** of binary search (lower-bound), sliding window, two-pointer pair-sum, Dutch flag (recall S3-02), Floyd's algorithm (the meeting-point invariant), and merge intervals; the **exchange argument** pattern for pointer moves (assume an optimal solution uses the discarded element; swap it out without making it worse); the **monotonicity / predicate** framework unifying binary search, binary search on the answer, and sliding-window shrinking (all are "find the boundary of a monotone predicate"); **potential/amortized** arguments for pointer loops (link to S3-01 Unit 5); search-space size accounting (after each step the space is ≤ half / ≤ n−1 / etc.) yielding the complexity; **peak-finding proof** (a local maximum exists in any slice whose boundary slopes point inward); **lower bounds by adversary argument** for searching (an adversary can always keep half the candidates alive — stated and proved for sorted-array search); when invariants are the wrong tool (stochastic, heuristic, or approximate algorithms need different guarantees — describe how correctness is stated there, forward link to modules 14/17).
- **L4:** **designing** a new two-pointer or search algorithm from the invariant outward (a worked case: find the smallest window containing all the distinct values, derived from scratch from the invariant, then coded); using invariants in **code review** (a checklist: state the invariant in a comment, check initialization, maintenance, termination, and empty/single/duplicate cases); generating **boundary-condition test suites automatically** from the interval convention (all positions of the target relative to the data, for sizes 0–8 exhaustively, then random); mutation-testing mindset (introduce each of the four classic off-by-one mutations and show your test suite catches them — a lab with a tiny hand-rolled mutator); teaching others (a 10-minute lesson plan for "invariant-first" development); formal tools as awareness only (Dafny, Why3, loop-invariant inference — named, not taught); documenting invariants in docstrings.
- **Must include:** the translation table between interval conventions with exhaustively tested equivalent implementations, the peak-finding proof, the exchange-argument write-up for at least two pointer rules, the invariant-checker helper with tests, the hand-rolled mutation lab, and the smallest-window-with-all-distinct-values derivation.

# 7. PRACTICE QUESTIONS (UNIT 10) — REQUIREMENTS

Generate a full `practice-questions.md` body with **at least 220 questions**: ≥ 16 for each of Units 1–9, plus ≥ 30 cross-unit integration questions. Required distribution per unit (≥ 16 each):

- 3 × conceptual short-answer
- 3 × multiple choice (4 options; answer + explanation of every distractor)
- 3 × code analysis ("state the output, the invariant, and the time and space complexity")
- 2 × proof/derivation (invariant, monotonicity, pointer-move safety, cycle algebra, complexity)
- 3 × coding problems (spec incl. empty/not-found policy, constraints, examples, model solution with tests, complexity)
- 1 × code review / bug-finding (find ≥ 3 defects, including at least one boundary or off-by-one defect)
- 1 × trace-table question (fill in the pointer states step by step)

Every question carries: ID, level (L1–L4), objective it tests, time estimate, difficulty (Easy/Medium/Hard defined by explicit criteria such as insights required and boundary subtlety), **model answer**, and **common wrong answers**. Include a difficulty progression and a scoring rubric with pass thresholds (80% proceed; 60–79% remediate; below 60% repeat, consistent with the stage's gate rules). Include 10 "whiteboard / design-review" prompts requiring written trade-off reasoning, 25 timed interview-style problems (20 minutes each) with model solutions that include the spoken complexity statement, the invariant, and the edge-case list, and a **boundary-bug clinic** of 15 buggy binary-search/window implementations where the learner finds the failing input and fixes it. Each question must test only content actually taught in Units 1–9 (plus S3-01 and S3-02).

# 8. SECTION NUMBER INTENTIONALLY UNUSED

(Kept so that section numbers match the other Stage 3 prompts. Nothing to generate here.)

# 9. SECTION NUMBER INTENTIONALLY UNUSED

(There is no Projects index unit in this syllabus; `./Projects/README.md` is defined separately.)

# 10. UNITS 11 AND 12 — PROJECTS (REQUIREMENTS)

Both follow the four levels and the N.0–N.14 skeleton **plus** the specification below.

## Unit 11 — Project: Log window analyzer
**Scenario:** A platform team ingests timestamped service logs and needs windowed analytics: request rates, error bursts, p95 latency over the last N minutes, and "busiest window" reports, without loading everything into memory and without trusting a single unverified loop. The learner builds an analyzer that is correct against brute-force oracles, bounded in memory, and benchmarked.

**Required deliverables (each with acceptance criteria checkable by command):**
1. Repository layout (`src/` layout, `tests/`, `bench/`, `data/`, `results/`, `docs/`, `pyproject.toml`) and a `Makefile`/`justfile` with targets: `install`, `lint`, `test`, `bench`, `report`, `check`, `clean`, `all`.
2. A **seeded synthetic log generator** (timestamps, service names, status codes, latencies; bursty, uniform, and adversarial profiles; sorted and mildly out-of-order modes) producing files up to a documented size cap, with a `--quick` mode. **No real data, no network.**
3. A **streaming reader** that processes lines with bounded memory and reports malformed lines with line numbers (a defined policy: skip-and-count vs fail-fast, configurable).
4. **Fixed-count and time-based sliding windows** (deque-based): requests per window, error rate per window, max and min latency per window via a **monotonic deque**, and moving average with a documented numerical-stability policy.
5. **Percentile over a sliding window (p50/p95)**: a correct baseline using a sorted structure with `bisect.insort` and removal (documented O(n) per update), compared with at least one improved approach you can justify (e.g., two heaps for the median, or a documented approximation), with a measured comparison and clear honesty about accuracy vs cost; percentile definition **stated explicitly** (nearest-rank or linear interpolation) and tested.
6. **Burst and busiest-window detection:** the busiest window of fixed duration (two pointers over sorted timestamps), the shortest window containing at least K errors (variable window), and the earliest time the rate exceeded a threshold (binary search on a prefix count of events).
7. **Rate-limiter study:** fixed-window counter, sliding-window log, and sliding-window counter implementations with a comparison table (accuracy, memory, burst behavior) verified by simulation with seeded traffic; no claims about any specific product.
8. **Interval consolidation:** merge outage intervals from multiple services (half-open UTC convention documented) and compute total downtime; correctness verified against a per-second coverage oracle.
9. **Out-of-order handling:** a bounded-lateness buffer (documented watermark policy and its limits), tested with seeded disorder; a test that demonstrates what happens without it.
10. **Differential and property tests:** every analyzer is compared with a brute-force O(n·w) or O(n²) oracle on seeded random inputs, including empty log, one event, all events at one timestamp, duplicate timestamps, window larger than the data, and window boundary ties (inclusive vs exclusive, documented and tested).
11. **Benchmarks:** throughput (events/second) and memory (`tracemalloc` peak) versus input size and window size; growth fitting against the declared complexity (O(n) for the deque-based analyzers) with the S3-01 harness methodology; a **regression guard** in `make check`.
12. **Documentation:** architecture diagram, ADRs (≥ 3: window boundary convention, percentile definition, out-of-order policy), a limits-of-this-analyzer section, and a one-page **operations guide** (what to monitor, how memory scales, what to do when logs are late or malformed).
13. A **results template** the learner fills with their own measurements. Do not fabricate results.

## Unit 12 — Project: Search and window pattern library
**Scenario:** An engineer keeps re-deriving two-pointer, window, and binary-search solutions and keeps shipping boundary bugs. They build a verified, benchmarked, documented library that plugs into the Stage 3 toolkit and encodes every pattern in this folder with its invariant.

**Required deliverables:**
1. Repository layout and `Makefile` as above, structured as a package `searchwindow_lib` with modules matching the units.
2. **At least 45 problems implemented** across: two pointers (≥ 6), sliding window (≥ 8 including monotonic-deque maximum and `exactly k`), binary search (≥ 6 including lower/upper bound, rotated array, peak, galloping), binary search on the answer (≥ 8 including a real-valued search and a maximize-minimum problem), fast/slow (≥ 4 including cycle start and duplicate number), intervals (≥ 7 including merge, insert, intersection, minimum rooms), and sort-plus-search combinations (≥ 6 including three-sum, k-sum, patience-sorting LIS, median of two sorted arrays). Each has: problem statement, constraints, **brute-force oracle**, optimized solution, declared time/space (worst/amortized, n defined), the **invariant written as a docstring field**, a mutation contract, unit tests, and edge cases.
3. A **generic `first_true`/`last_true` binary-search kernel** and a **generic sliding-window kernel** (variable-window with pluggable `add`, `remove`, `valid` callbacks) that most solutions are built on, with tests and a documented cost of the callback abstraction (measured).
4. **Executable invariant checks:** each solution can run in a debug mode that asserts its invariant each iteration; tests run in both modes and a benchmark measures the overhead.
5. **Differential and property tests:** randomized comparison of every solution with its oracle using seeded generators; adversarial generators per category (all equal, strictly increasing, strictly decreasing, many duplicates, all negative for sum problems, targets below/between/above the data, windows larger than input, cycle at every position); **exhaustive tests for all inputs up to size 6–8** for the binary-search family.
6. **Mutation lab:** a small, documented mutator that applies classic off-by-one mutations (`<` ↔ `<=`, `mid ± 1` swaps, wrong initial `hi`, missing shrink) to the kernels, and a test that fails if any mutant **survives** — reporting the mutation score.
7. **Benchmark integration:** register solutions with the Stage 3 toolkit registry (or a compatible interface if it is not yet built), benchmark over a size ladder, fit growth exponents, and add a regression guard failing `make check` when observed growth exceeds the declared class beyond a stated tolerance; include the sort-then-search break-even experiment.
8. **Technique index and decision flowchart:** a generated table mapping problem → technique → unit → complexity → recognition signal → invariant, and a mermaid flowchart validated by a test that every problem is reachable and every technique has ≥ 2 problems.
9. **Documentation:** architecture diagram, ADRs (≥ 3: kernel abstraction, invariant-checking policy, interval convention), a "bugs found by the oracle and mutation lab" log the learner fills in, and a one-page **review checklist for pointer/window/search code**.
10. A **results template** (declared vs observed complexity, mutation score, failures found, timed-solve log). Do not fabricate results.

**For both projects include:** a milestone plan (5–6 milestones with time estimates), a grading rubric (100 points, criterion-level descriptors for Poor / Adequate / Strong / Exemplary), stretch goals, common failure points, a self-review checklist, and the exact evidence folder structure; link to `./Projects/README.md` for submission rules without inventing its contents.

**Provide complete, runnable starter code** for each project: package, tests, generators, benchmark scripts, Makefile, `pyproject.toml`. Every code file states its path in a first-line comment. Do not leave `TODO: implement` in required deliverables. Dependencies: standard library plus `pytest` for required parts; everything else optional.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: src/searchwindow_lib/binary_search.py`).
2. **Every command and snippet is paired with expected output** (representative, clearly labeled "example — yours will differ in timings, sizes, and memory addresses") and a short interpretation.
3. **Code must run.** Python 3.10+ syntax only (state if 3.12 is required). Standard library unless marked optional. Type hints on all public functions. Clarity over cleverness. Every function states its **precondition** (e.g., "`a` sorted ascending"), its **not-found/empty policy**, and its **mutation contract**.
4. **Invariant first.** For every non-trivial loop, the invariant appears as a comment above the loop **before** the loop body is explained. Interval conventions (closed vs half-open) are stated at the top of every search or window function.
5. **Complexity statements must be precise:** worst-case, average-case, expected, or amortized; time **and** space; what n is; cost of any callback, key function, or comparison; the sorting cost when sorting is part of the algorithm; proof sketch or invariant for every non-trivial claim; algorithmic complexity separated from CPython constant factors.
6. **Every algorithm ships with a brute-force oracle and tests** that pass on the reference code and fail on a deliberately broken variant (show it once per unit). Binary-search code is tested **exhaustively** on small inputs against `bisect`/a linear oracle for targets below, equal to, between, and above the data.
7. **No unproven performance claims.** Every speed or size claim ties to a measurement the learner can run (warm-up, repeats, statistic stated). Otherwise label it `[ILLUSTRATIVE — measure yours]`. Example outputs are labeled **representative**; never present a measured-looking number that was not measured.
8. **Benchmarks must avoid the usual errors** (see S3-01 Unit 6): reused mutated input, noise-floor timings, one size, single run, GC and caching ignored, measuring setup instead of the operation. Always sort or generate inputs outside the timed region unless sorting is the thing being measured.
9. **Do not teach CPython implementation details as language guarantees.** State `bisect` behavior per its documentation; Timsort's stability is documented, its internal run-merging strategy is an implementation detail `[VERSION-SENSITIVE]`; `sorted`/`list.sort` key evaluation counts per documentation `[VERIFY]`.
10. **No secrets, no network access, no paid APIs, no real log data** in any lab. Synthetic data only, seeded, with size caps and a `--quick` mode. `clean` targets list what they remove; no deletion outside the project directory.
11. **Every lab ends with cleanup** and a verification that no stray files or processes remain beyond those documented.
12. **Proofs are written in full** where required (invariant: initialization, maintenance, termination; monotonicity: stated formally from the problem definition; exchange arguments: assume an optimal solution, show the swap does not worsen it; cycle algebra: all steps). "It is obvious" is not a proof.
13. **Tag Python-version and implementation differences** (CPython vs PyPy, 3.10 vs 3.12) `[VERSION-SENSITIVE]`; call out WSL2 timing-noise sources where they affect a lab.
14. **Python-specific correctness traps are taught explicitly:** negative indices silently wrapping (`a[-1]` when `right` underflows to −1), slicing copies inside loops (hidden O(n²)), mutating a list while two pointers walk it, float comparison and accumulation in real-valued binary search, `//` and `%` with negatives, NaN breaking sorted-order assumptions, `None` handling in linked lists, recursion limit in recursive search variants.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You will act as author, then as an independent auditor of your own work, and you will include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every claim on **authoritative sources**: the official Python documentation (Library Reference pages for `bisect` including the algorithm notes and the `key=` parameter, `sorted`/`list.sort` and the Sorting HOWTO, `collections.deque`, `heapq`, `functools.cmp_to_key`, `itertools`, `math`, `timeit`, `tracemalloc`, `datetime`; the "What's New" pages for version-sensitive behavior), the Python Wiki **TimeComplexity** page, and standard texts cited by **title and chapter topic, not page numbers you cannot confirm**: *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein) — loop invariants, binary search as an exercise/lower bounds for sorting and searching, medians and order statistics, greedy algorithms; *Algorithms* (Sedgewick and Wayne) — binary search, searching; *The Algorithm Design Manual* (Skiena) — binary search and related techniques; *Programming Pearls* (Bentley) for the binary-search invariant discussion and the documented history of bugs in binary search implementations (cite by chapter topic and **mark any specific historical claim `[VERIFY]`**); original attributions for named algorithms (Floyd's cycle-finding, Brent's cycle detection, Pollard's rho) cited by author and topic only where you are certain, otherwise `[VERIFY]`. Provide a URL only if you are certain it is canonical; otherwise cite by name and mark `[VERIFY]`.
- **Do not fabricate:** version numbers, benchmark results, timings, CPython internals presented as guarantees, claims about `git bisect` internals, company practices, interview statistics, rate-limiter product behavior, or quotes. If you need a number, derive it from a stated command or label it illustrative.
- **Mark uncertainty** with: `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[ASSUMPTION]`, `[JUDGEMENT]`.
- Keep a running **Claim Register** (Section 12.3) for every non-trivial claim.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 12 units present, in order, with every required section (Sections 5, 7, 10), every unit-specific topic (Section 6), levels L1–L4. | Any missing section/topic. |
| 2 | **Invariant and proof audit** | Every invariant is stated for initialization, maintenance, and termination; every pointer move has a safety argument; every monotonicity claim is proved from the problem definition; every exchange argument is complete; cycle algebra is re-derived independently. | Any missing, circular, or invalid argument. |
| 3 | **Boundary exhaustiveness** | Every search/window/pointer function is run mentally (and by the stated tests) on n = 0, 1, 2, 3, duplicates, targets below/between/above the data, all-equal, all-negative, and window > data; closed vs half-open conventions are consistent within each function. | Any boundary that fails or any inconsistent convention. |
| 4 | **Mathematical correctness** | Halving counts, comparison-count bounds, break-even derivations, cycle distance algebra, rate-limiter and percentile definitions are re-derived and checked at small values by hand or by a stated script. | Any wrong formula or unjustified step. |
| 5 | **Technical accuracy** | Every Python function, signature, and behavior is real and correct (e.g., `bisect_left/right`, `insort`, the `key=` parameter and its version, `heapq.merge`, `cmp_to_key`, `deque` operations). Mentally execute every code block and lab. | Any invented function, misused API, or wrong version claim. |
| 6 | **Executability** | Code blocks are syntactically valid; imports resolve; file paths and cross-references resolve; every test passes on the reference code and fails on a deliberately broken variant; every lab has steps, expected evidence, and cleanup. | Any broken, ambiguous, or unrunnable step. |
| 7 | **Complexity labeling audit** | Worst/average/expected/amortized labels are right; "n" is defined; sorting cost and callback cost are included; slicing copies are counted; O is never described as "worst case"; amortized is never confused with average. | Any mislabeled or ambiguous bound. |
| 8 | **Applicability audit** | Every technique states its precondition (sorted, monotone, positives-only, majority exists…); every "when NOT to use" has a counterexample that actually fails; no technique is presented as general when it is conditional. | Unstated precondition or unproven "fails" claim. |
| 9 | **Guarantee vs implementation audit** | Every CPython/stdlib statement is classified as documented guarantee or implementation detail and tagged; `bisect`/Timsort claims match the documentation. | Implementation detail presented as guarantee. |
| 10 | **Benchmark validity** | Methodology is sound; inputs prepared outside the timed region; no result is presented as measured unless clearly labeled representative or a template; fitted slopes interpreted with caveats. | Flawed method or fabricated numbers. |
| 11 | **Currency** | Version-sensitive claims tagged; no deprecated feature taught as current; 3.10 minimum respected or differences noted. | Stale, untagged, or over-general claims. |
| 12 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated benchmark outputs, misattributed algorithms, invented library features, and invented claims about third-party tools. | Any unsupported specific. |
| 13 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept (invariants, monotone predicate, amortization, linked nodes) used before it is taught or explicitly forward-referenced; terminology consistent; the running example evolves coherently. | Forward dependency without a note; terminology drift. |
| 14 | **Cross-consistency** | Practice questions test only taught content; every project deliverable maps to a unit; the decision flowchart, technique index, drills, and checklists agree with the lessons; Units 11–12 promise nothing the units do not teach; links to S3-00/01/02 and later modules are correct; the 9 lesson names match Section 2 exactly. | Orphan question, orphan deliverable, or contradiction. |
| 15 | **Adversarial review** | Re-read as a skeptical staff engineer and as a hostile interviewer: "What here is wrong, misleading, or would teach a bad habit?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 16 | **Reproducibility** | Labs run within the 4 CPU / 8 GB / 30 GB baseline, need no paid service or network, are seeded and idempotent, have size caps and a `--quick` mode, and clean up. | Hidden cost, unseeded nondeterminism, or leftover state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendices)

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. Include at least **90 entries**, covering every standard-library behavior claim, every complexity bound, every theorem or proof technique used, every algorithm attribution, and every judgement of consequence.

**Appendix B — Audit Report** (table for passes 1–16): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** all `[VERIFY]` / `[VERSION-SENSITIVE]` / `[JUDGEMENT]` items grouped by area (`bisect` and sorting documentation, standard-library modules, complexity claims, proofs, benchmark methodology, engineering-practice judgements), each with: *what to check*, *where to check (named source)*, *how to test it locally with one command or small script*. The reviewer must be able to close every item in under 4 hours.

**Appendix D — Known Limitations and Assumptions:** what the module intentionally does not cover (sweep line, interval trees, segment trees, advanced parametric search, concurrent/lock-free structures, formal verification tools), assumed Python version, CPython-vs-PyPy caveats, WSL2 timing caveats, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code, proofs, and benchmarks.

**Appendix F — Invariant and Proof Index:** every invariant, monotonicity argument, exchange argument, and formula in the syllabus with its unit, statement, and proof technique.

**Appendix G — Executable Verification Bundle:** a `verify_syllabus.py` script (standard library only) that extracts every fenced Python block with a `# File: …` first-line comment, writes them to a scratch directory, byte-compiles them (`py_compile`), runs the test suite in `--quick` mode, and prints a PASS/FAIL list; plus a `verify_math.py` that numerically checks: binary-search comparison-count bounds on all n up to a cap; the custom lower/upper-bound templates equal `bisect_left/right` on exhaustive small inputs; two-pointer pair-sum equals brute force on random sorted arrays; sliding-window solutions equal brute force on random inputs; the `exactly k = at_most(k) − at_most(k−1)` identity; the Floyd cycle-start derivation on every `(μ, λ)` pair up to a cap; the duplicate-number reduction on random valid arrays; merge-intervals output equals the brute-force point-coverage set; three-sum equals the `itertools.combinations` oracle; median-of-two-arrays equals the sorted-merge median on random inputs.

## 12.4 Trust rules
- If an audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it actually was in your environment. Use "expected output (representative)" instead.
- Never state that content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.
- Statements about **CPython internals** are implementation details: state them as such, tag `[VERSION-SENSITIVE]`, and prefer teaching the learner to **measure or inspect** them over asserting them.
- Historical claims (for example, about long-standing bugs in published binary-search code) must be stated only if you are certain and otherwise marked `[VERIFY]`; never invent an anecdote.
- Attributions of algorithms to people or papers must be correct or marked `[VERIFY]`; never invent a citation.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-Two-Pointers-Sliding-Window-and-Binary-Search.md`.
- Start with: title, one-paragraph abstract, metadata block (`Module: S3-03`, `Stage: 3`, `Language: Python`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 1–12 in order, then Appendices A–G.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons and trace tables, fenced code blocks for all code, mermaid for diagrams and flowcharts, plain-text math (e.g., `⌊log₂ n⌋ + 1`) with Unicode symbols where clear; avoid LaTeX that may not render.
- Each unit is **self-contained but cross-linked** (relative links to sibling target files, S3-00, S3-01, S3-02, and later modules).
- **Depth target:** Units 1–9 each ≥ 2,500 words of teaching text excluding code; practice questions ≥ 220 items; both projects complete with all code. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 1 |
| 2 | Unit 2 |
| 3 | Unit 3 |
| 4 | Unit 4 |
| 5 | Unit 5 |
| 6 | Unit 6 |
| 7 | Unit 7 |
| 8 | Unit 8 |
| 9 | Unit 9 |
| 10 | Unit 10 part A (units 1–5 questions) |
| 11 | Unit 10 part B (units 6–9 questions, integration, whiteboard, timed interview set, boundary-bug clinic) |
| 12 | Unit 11 part A: N.0–N.8 and specification with scaffold, generator, reader, window code |
| 13 | Unit 11 part B: percentile, burst, rate-limiter, intervals, out-of-order, tests, benchmarks, N.9–N.14, rubric, results template |
| 14 | Unit 12 part A: N.0–N.8, specification, kernels, first half of the problem set |
| 15 | Unit 12 part B: remaining problems, mutation lab, benchmark integration, technique index, N.9–N.14, rubric, results template |
| 16 | Appendices A–G (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/16 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–16, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 16 must run the **cross-part** audit (passes 13, 14, 15 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you are approaching the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 16, print the final assembly instruction: "Concatenate Parts 1–16 in order into `SYLLABUS-Two-Pointers-Sliding-Window-and-Binary-Search.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 12 units present, in the specified order; Units 1–9, 11, and 12 each with levels L1–L4 and sections N.0–N.14.
- [ ] Every unit-specific topic in Sections 6, 7, and 10 is taught at its stated level.
- [ ] Every required proof is written in full (pair-sum and container pointer moves; read/write compaction invariant; window monotonicity and the negative-number counterexample; monotonic-deque invariant; `exactly k` identity; lower-bound invariant and termination; monotonicity proofs for ≥ 4 answer-space problems; Floyd existence and cycle-start algebra; duplicate-number reduction; merge-intervals and meeting-rooms invariants; three-sum, rotated-array, and median-of-two-arrays arguments; peak-finding proof).
- [ ] Every algorithm has a stated precondition, empty/not-found policy, mutation contract, brute-force oracle, tests, and edge-case list; every binary-search function is tested exhaustively on small inputs.
- [ ] The ≥ 220 practice questions have model answers and distractor analysis; the 25 timed interview problems have model solutions; the 15-item boundary-bug clinic has fixes; Unit 5 has ≥ 70 drill items with answers.
- [ ] Project 1 (log window analyzer) has the generator, streaming reader, deque-based windows, percentile study, burst detection, rate-limiter study, interval consolidation, out-of-order handling, oracles, benchmarks, and regression guard; Project 2 has ≥ 45 problems with oracles and invariants, two generic kernels, executable invariant checks, a mutation lab, benchmark integration, and a technique index; both have rubrics and results templates with **no fabricated results**.
- [ ] Every complexity claim is correctly labeled (worst/average/expected/amortized, time and space, n defined, sorting and callback cost included) and every performance claim is tied to a measurement or tagged illustrative.
- [ ] Every technique states its precondition and has a failing counterexample for each "when NOT to use".
- [ ] Every CPython/stdlib implementation detail is tagged `[VERSION-SENSITIVE]` and documented guarantees are separated from implementation details.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and a `--quick` mode; all run within the free local baseline with synthetic data only.
- [ ] No fabricated statistics, citations, versions, timings, attributions, anecdotes, or incident details; every uncertain item is tagged.
- [ ] Appendices A–G present; Claim Register ≥ 90 entries; audit passes 1–16 reported candidly.
- [ ] `verify_syllabus.py` and `verify_math.py` are delivered and consistent with the file-path comments in the code.
- [ ] A human can verify every open item in under 4 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/16**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 16 parts so the Claim Register, the running example, the interval conventions, and the kernels stay consistent. If a part truncates, type `continue` and it resumes at the stated section boundary.
2. **Do the human verification yourself.** Run `verify_syllabus.py` and `verify_math.py` (Appendix G), re-derive the Floyd cycle-start algebra and the lower-bound invariant by hand, run the boundary tests on your machine, and close each `[VERIFY]` item against the Python docs (`bisect`, Sorting HOWTO).
3. **Spot-check fabrication risk areas first:** the `bisect` `key=` version claim, Timsort and `sorted`/`key` evaluation statements, `heapq.merge` behavior, comparison-count bounds, the Floyd derivation, the median-of-two-arrays invariant, any historical claim about binary-search bugs, any statement about `git bisect`, and any timing number that is not clearly a template.
4. **Scope note:** the folder's `README.md` and `Projects/README.md` are intentionally excluded, as they are not in the unit list you gave. Generate them with separate prompts, or ask me to add them as units. Sections 8 and 9 of this prompt are deliberately empty so numbering matches the other Stage 3 prompts.
5. **Final file layout:** save the LLM output as `SYLLABUS-Two-Pointers-Sliding-Window-and-Binary-Search.md` in this folder. Later, split it into the 12 target files (`01-…09-…`, `practice-questions.md`, `Projects/01-log-window-analyzer.md`, `Projects/02-search-and-window-pattern-library.md`).
