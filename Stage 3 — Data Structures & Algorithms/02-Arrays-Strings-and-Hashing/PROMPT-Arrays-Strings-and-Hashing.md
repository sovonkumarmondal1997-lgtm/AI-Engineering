# PROMPT — Generate `SYLLABUS-Arrays-Strings-and-Hashing.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Software Engineer with 15 years of industry experience** across backend systems, data platforms, and applied ML infrastructure. You have deduplicated billion-row datasets, debugged a service that slowed down because of hash collisions, replaced quadratic string handling in ETL jobs, built in-memory indexes, and interviewed hundreds of candidates on exactly these topics. You teach the way you work: **understand the mechanism, prove the bound, measure the result, and distrust anything you have not verified.**

You are also a careful technical author. You never invent a function, a complexity bound, an implementation detail, a default, a version, or a statistic. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 3 — Data Structures & Algorithms / 02-Arrays-Strings-and-Hashing/` (module code **S3-02**)

Output file name: **`SYLLABUS-Arrays-Strings-and-Hashing.md`**

All code, labs, and examples are in **Python**.

It must teach, **one after another, from beginner to advanced**, these 18 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 1 | Arrays and dynamic arrays | `01-arrays-and-dynamic-arrays.md` |
| 2 | Strings and immutability | `02-strings-and-immutability.md` |
| 3 | Hash tables internals | `03-hash-tables-internals.md` |
| 4 | Hash map and set patterns | `04-hash-map-and-set-patterns.md` |
| 5 | Prefix sums | `05-prefix-sums.md` |
| 6 | Frequency counting patterns | `06-frequency-counting-patterns.md` |
| 7 | Multidimensional arrays and matrices | `07-multidimensional-arrays-and-matrices.md` |
| 8 | String manipulation and patterns | `08-string-manipulation-and-patterns.md` |
| 9 | Subarrays, substrings, and subsequences | `09-subarrays-substrings-and-subsequences.md` |
| 10 | Hashing, collisions, and performance trade-offs | `10-hashing-collisions-and-performance-tradeoffs.md` |
| 11 | Kadane and maximum-subarray patterns | `11-kadane-and-maximum-subarray-patterns.md` |
| 12 | Boyer-Moore voting and majority element | `12-boyer-moore-voting-and-majority-element.md` |
| 13 | Dutch national flag and in-place partitioning | `13-dutch-national-flag-and-in-place-partitioning.md` |
| 14 | Rolling hash and Rabin-Karp | `14-rolling-hash-and-rabin-karp.md` |
| 15 | Practice questions | `practice-questions.md` |
| 16 | Projects index | `Projects/README.md` |
| 17 | Project: Build a hash map from scratch | `Projects/01-build-a-hash-map-from-scratch.md` |
| 18 | Project: Array and string problem toolkit | `Projects/02-array-and-string-problem-toolkit.md` |

Do **not** add, merge, skip, or reorder units. The folder's own `README.md` is **out of scope for this syllabus**; do not write it (treat it as "defined separately"). Do not produce shallow summaries: this is the **teaching content itself**, not an outline of it.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI Engineer who has finished Stages 0–2E, Unit S3-00 (Stage 3 Overview: prerequisites, topic map, toolkit scaffold) and S3-01 (Complexity and Big-O). They can state and prove simple Big-O bounds, count steps, distinguish worst/average/amortized, and benchmark with `timeit`. They can write working Python and basic `pytest`. They have **not** studied hash tables internally, nor the standard array/string/hashing interview patterns.
- **Stage position:** Stage 3 comes **before** the math stages (4A/4B/4C). Assume school algebra plus S3-01. Teach inline from first principles any math used here: modular arithmetic (remainders, congruence, modular exponentiation), basic probability for collisions (the birthday intuition, load factor, expected chain length), and polynomial evaluation (Horner's rule). Forward-link to Stage 4A/4B for depth.
- **Zero budget.** All work runs on a **local laptop** (WSL2 Ubuntu primary, native Linux/macOS secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid service, no network required.
- **Tool baseline (required):** **CPython 3.12** `[ASSUMPTION — state minimum 3.10 and note differences]`, `venv`, `pytest`, `timeit`, `time.perf_counter_ns`, `tracemalloc`, `sys.getsizeof`, `dis` (awareness), and the standard library (`collections`, `array`, `itertools`, `functools`, `bisect`, `heapq`, `string`, `re`, `hashlib`, `random`, `statistics`, `sys`).
- **Optional helpers (flag as optional):** `numpy` (contrast only: different cost model), `hypothesis`, `matplotlib`, `ruff`, `mypy`, `memory_profiler`-style tools (awareness).
- **Domain flavor:** after Level 1, examples come from systems a data/AI engineer meets: deduplicating records, joining datasets on a key, windowed log analytics, token and n-gram counting, feature hashing, sessionization, histogram bucketing, matrix/tensor shape handling, text normalization, majority/heavy-hitter detection in event streams. Avoid toy-only examples beyond L1.
- **Running example thread:** one scenario, **"an event stream of user actions with string keys"**, evolves through the folder: store events in arrays → group and count by key with a hash map → query ranges with prefix sums → find the best window with Kadane/sliding patterns → detect the dominant action with Boyer-Moore → deduplicate with hashing and bound memory with a rolling hash. Reuse it so the learner sees one problem solved through every lens.
- **Continuity and links:** link back to S3-01 (complexity analysis, amortized analysis, benchmarking) and to the Stage 3 toolkit (`../00-Stage-3-Overview/Projects/01-algorithm-toolkit-and-benchmark.md`); forward to module 03 (two pointers, sliding window, binary search), 04, 05, 14 (patterns), 15 (string algorithms: KMP, Z, suffix structures), 17 (Bloom filter, count-min sketch, HyperLogLog), 18 (storage engines, external hashing), 19 (locality-sensitive hashing). State clearly what is **taught here vs. deferred**: e.g., Rabin-Karp is taught here; KMP/Z/suffix arrays are deferred to module 15; sliding window as a general technique is deferred to module 03 but fixed-window sums appear here with a forward link.

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–14 AND UNITS 17–18)

Each of these units progresses through **exactly these four levels**. Use identical headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Understands the concept, runs the basic Python snippet, reads the result. |
| **L2** | Intermediate — Working Practice | Applies the structure or pattern to realistic data/AI code, follows standard idioms, avoids common mistakes. |
| **L3** | Advanced — Engineering Rigor | States and proves correctness and bounds, designs experiments, defends decisions with evidence and trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses subtle failures, reasons about scale and adversarial input, builds tooling, and could coach another engineer. |

Units 15 and 16 use the structures in Sections 7 and 9.

# 5. MANDATORY STRUCTURE FOR UNITS 1–14

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
(One mermaid or ASCII diagram of the core structure or the algorithm's state.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why it works, not only what to type)
- Guided exercise with exact Python code, expected output, and how to read it
- "What just happened?" walkthrough (trace table or memory diagram)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic example (complete, runnable Python), continuing the running example
- Pattern catalogue: pattern | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad code → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Formal statement and proof (or proof sketch) of correctness and complexity; loop invariants where relevant
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure, with which tool, how to avoid fooling yourself)
- Exercise that requires a defended argument, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial and scale concerns (worst-case inputs, huge n, memory limits, streaming)
- Automation (property-based or differential tests, validators, regression guards)
- Team concerns: design-review checklist, how to coach others, how to document complexity
- Edge cases and platform differences (CPython vs PyPy, Python 3.10 vs 3.12, 32/64-bit, WSL2 vs native)

### N.7 Engineering lens
- Where this shows up in real systems (name the system class; never fabricate a company claim)
- Failure modes and blast radius (what breaks, for whom, how you would notice)
- Cost, capacity, and performance notes

### N.8 Integrity lens
- Reasoning and measurement risks (off-by-one, aliasing, hidden copies, hash-order assumptions, benchmark self-deception)
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

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated. Every algorithm is taught with: problem statement and specification, brute-force baseline, the improved algorithm, an invariant or proof, time and space (labeled worst/average/amortized, with n defined), edge cases, tests, and a measured comparison.

## Unit 1 — Arrays and dynamic arrays
- **L1:** what an array is (contiguous memory, index arithmetic, O(1) random access); Python `list` as a dynamic array of **references** (not a C array of values); indexing, negative indexing, slicing (copy semantics), `append`, `pop`, `insert`, `del`, `extend`, `len`; iteration; `list` vs `tuple` vs `array.array` vs `bytearray`; off-by-one errors; the aliasing trap (`b = a` vs `b = a[:]` vs `copy.deepcopy`); in-place vs out-of-place.
- **L2:** costs of every common list operation with reasons (access, append, pop(), pop(0), insert, remove, `in`, slicing, concatenation, `sort`, `reverse`, `index`, `count`) linked back to S3-01's cheat sheet and confirmed by benchmarks; list comprehension vs loop vs generator; two-array and in-place techniques (reverse, rotate by k with the three-reversals trick, remove duplicates from a sorted array in place, move zeros, merge two sorted arrays); `list.sort` vs `sorted`; key functions; stability; `enumerate`, `zip`, `reversed`; the mutable-default-argument and loop-variable-capture traps.
- **L3:** the dynamic-array **abstraction** implemented from scratch (capacity vs size, growth policy, amortized O(1) append with the potential-method proof from S3-01, shrink policy and thrashing), including a `DynamicArray` class using `ctypes` or a fixed-size list as backing store **with a clear statement that it models, not replicates, CPython's list**; memory: pointer-array overhead, object overhead, `array.array` for homogeneous numerics, `memoryview` and `bytes`/`bytearray` for zero-copy slicing; `bisect` on sorted arrays; invariants for in-place algorithms (e.g., the read/write pointer invariant); CPython list over-allocation is an **implementation detail** the learner infers by measurement (`sys.getsizeof` jumps) `[VERSION-SENSITIVE]`.
- **L4:** cache locality and the honest limits of demonstrating it in Python; `numpy` as a contrast (contiguous typed buffer, vectorization) with the same task, clearly labeled "different cost model"; tail latency of `append` (resize spikes) and mitigation by preallocation; large-array memory budgeting (1M vs 100M elements of Python `int` vs `array('i')`); in-place algorithms under adversarial input; designing a safe API that does not mutate caller data by surprise; documenting complexity and mutation contracts.
- **Must include:** a `DynamicArray` with tests and an amortization experiment, the rotation-by-reversal proof, a measured `list` vs `array.array` vs `numpy`-contrast memory table, and the first version of the running example (events stored and scanned).

## Unit 2 — Strings and immutability
- **L1:** a string as an immutable sequence of Unicode code points; indexing and slicing; `len`; iteration; common methods (`split`, `join`, `strip`, `replace`, `find`, `startswith`, `lower`); comparison and ordering; `str` vs `bytes`; why `s[0] = 'a'` fails; ASCII vs Unicode in one honest page (code point, encoding, UTF-8, why `len('é')` can differ from the byte length).
- **L2:** immutability consequences: every "modification" creates a new string; `+=` in a loop vs `''.join` (measured; CPython's occasional in-place optimization of `+=` is an **implementation detail, not a guarantee** `[VERSION-SENSITIVE]`); slicing cost O(k); `in` and `find` on strings; building strings from pieces with `io.StringIO`, lists, and `join`; f-strings and `format`; `str.translate`/`maketrans`; case folding vs lowercasing (`casefold`); Unicode normalization (`unicodedata.normalize`) and why two visually identical strings can compare unequal; `ord`/`chr`; `string` module constants.
- **L3:** why immutability enables hashing and safe sharing; interning (`sys.intern`) and the difference between `==` and `is` for strings (never rely on `is`); CPython's flexible string representation (PEP 393) at a conceptual level `[VERIFY]` and its memory consequences (one non-Latin-1 character can widen the whole string) shown by `sys.getsizeof`; grapheme clusters vs code points (named; `len` is not "number of characters the user sees"); `bytes`/`bytearray`/`memoryview` for mutable byte processing; cost of repeated slicing in recursive string algorithms (hidden O(n²)) and the index-passing fix; comparing strings costs O(min(len)) (so hashing strings is not O(1)).
- **L4:** text-processing pipelines at scale (streaming lines, chunked reads, avoiding materializing huge strings); regex cost and backtracking risk (`re`, with a safe local ReDoS demo from S3-01 as a callback); encoding bugs in data pipelines (mojibake, BOM, surrogate escapes) and defensive decoding (`errors=`); security-relevant string issues (homoglyph and normalization confusion, injection through concatenation — described, not exploited); documenting and testing text contracts.
- **Must include:** a `+=` vs `join` vs `StringIO` benchmark, a Unicode-normalization lab, a `sys.getsizeof` width lab, and the second version of the running example (normalize event keys).

## Unit 3 — Hash tables internals
- **L1:** the idea: key → hash → index → bucket; why lookup can be O(1) on average; the hash function, the table, the collision; Python `dict` and `set` usage; hashability (what is hashable and why mutable built-ins are not); `hash()`, `__hash__`/`__eq__` contract (equal objects must have equal hashes); insertion, lookup, deletion, resize described informally.
- **L2:** **collision resolution**: separate chaining and open addressing (linear probing, quadratic probing, double hashing), each implemented in simple form and traced by hand; **load factor** α, resize policy, rehash; deletion in open addressing (tombstones), and why naive deletion breaks lookup; expected cost of chaining under uniform hashing (1 + α, derived); what "O(1) average" assumes (a good hash, bounded α); a small `HashTable` with chaining and tests.
- **L3:** CPython's `dict`: the compact, insertion-ordered design (an index table plus a dense entries array), open addressing with perturbation-based probing, load-factor-driven resizing, key-sharing for instance dicts — described from documentation and the CPython design notes and **tagged `[VERSION-SENSITIVE]`/`[VERIFY]`**; guaranteed insertion order (language guarantee since 3.7) vs the internal layout (implementation detail); `set` similarities and differences; `hash` of `int`, `str`, `tuple`, `frozenset`; why `hash(-1) == hash(-2)` in CPython (a documented implementation quirk `[VERIFY]`); string hash randomization (`PYTHONHASHSEED`) and what it defends; `__eq__` and `__hash__` pitfalls (defining one without the other, mutating a key after insertion); proof sketch of expected O(1) under the simple uniform hashing assumption; resize amortization (link to S3-01 Unit 5).
- **L4:** worst-case behavior and adversarial keys (hash flooding) with a **safe local demonstration** using a custom colliding `__hash__` and bounded size; measuring dict resize spikes and memory per entry; iteration-while-mutating errors and their cause; memory footprint of dicts of dicts; alternatives and when to use them (`dict` vs `OrderedDict` vs `defaultdict` vs `Counter` vs sorted array + `bisect`); cuckoo hashing, Robin Hood hashing, and Swiss-table-style designs as **awareness** (named, one paragraph each, no fabricated claims about which language uses which); consistent hashing named with a forward link to module 18.
- **Must include:** hand-traced collision examples for chaining and linear probing, the expected-chain-length derivation, a probing-sequence visualizer script, a colliding-key degradation lab, and a table separating *language guarantees* from *CPython implementation details*.

## Unit 4 — Hash map and set patterns
- **L1:** the three core uses: **membership** (is it seen?), **lookup/association** (key → value), **counting** (key → count); canonical problems solved first by brute force then by hashing: contains-duplicate, two-sum, first non-repeating element, intersection of two arrays.
- **L2:** the pattern catalogue with recognition signals: *seen-set*, *complement lookup* (two-sum), *index map* (last/first position), *grouping by canonical key* (anagram groups with sorted-string or count-tuple keys), *set difference/intersection for diffing*, *visited set* for cycles, *two-pass vs one-pass*, *hash of a derived key* (normalization), *memoization* via dict; `defaultdict`, `Counter`, `dict.setdefault`, `dict.get`, `collections.OrderedDict` use cases, dict/set comprehensions; set algebra (`|`, `&`, `-`, `^`) and their costs; choosing a **hashable key**: tuple vs string vs `frozenset` and the canonicalization trade-offs; longest-consecutive-sequence with a set in O(n) (proof of why each run is started once).
- **L3:** correctness proofs for one-pass two-sum (invariant: the map contains all elements before index i), longest consecutive sequence (each element is the start of at most one counted run), and group-anagrams (canonical-key correctness); complexity with hashing cost for long keys (O(L) per key, so total O(n·L)); trade-offs: hash map vs sort vs two pointers (decision table with when each wins, including memory); handling of duplicates, unhashable items, `None`, and `float('nan')` keys (NaN is not equal to itself — a real surprise); iteration-order assumptions (relying on insertion order is legitimate; relying on set order is not); memory trade-offs of storing indices vs storing values.
- **L4:** streaming and bounded-memory variants (approximate membership by sampling, a pointer to Bloom filters in module 17; windowed seen-set with expiry using `deque` + dict); joins as hash joins (build side, probe side, memory choice) with a mini hash-join implementation over two CSV-like inputs and the complexity O(n + m); partitioned/external dedup (forward link to module 18); property-based tests comparing hash-based solutions with brute-force oracles; reviewing a pattern choice in a design review.
- **Must include:** ≥ 12 solved problems across the patterns (each with brute force, optimized, proof or invariant, complexity, tests), a hash-join implementation, and the third version of the running example (group and count events by key).

## Unit 5 — Prefix sums
- **L1:** the idea: precompute cumulative sums so that any range sum is a subtraction; building `prefix[i] = sum(a[:i])` (length n+1 convention) and the off-by-one rules; range sum `sum(a[l:r])` = `prefix[r] − prefix[l]`; the build is O(n), each query is O(1), versus O(n) per query naively.
- **L2:** `itertools.accumulate`; 1-D prefix sums for range-sum queries; prefix counts (counting a value in a range), prefix products and the division-free variant (product of array except self with prefix × suffix), prefix XOR (named, link to module 10), **subarray sum equals k** with a prefix-sum + hash map (and why a sliding window fails with negatives), count of subarrays with sum divisible by k (prefix mod and a counter), pivot index, running balance; difference arrays for **range updates** and their reconstruction by prefix sum.
- **L3:** correctness proofs (the telescoping argument; the invariant for subarray-sum-equals-k: the counter holds counts of prefix sums seen so far, including the empty prefix); **2-D prefix sums** (summed-area table) with inclusion–exclusion and a proof of the query formula; when prefix sums are the right tool vs a Fenwick or segment tree (forward link to module 13: static data → prefix sum; updates → tree); integer overflow does not occur in Python but floating-point accumulation error does (show a measurement; mention `math.fsum`); memory/time trade-offs; modular prefix sums and negative remainders in Python (`%` result sign convention `[VERIFY]` and a worked example).
- **L4:** prefix sums at scale: chunked/streaming cumulative statistics, parallel prefix (scan) named as awareness, prefix sums in analytics (cumulative metrics, windowed aggregates, histograms and CDFs), time-series bucketing; testing with an oracle on random arrays (seeded); common review findings (off-by-one, forgetting the empty prefix, mutating the source array between builds); documenting preconditions (static array vs updates).
- **Must include:** 1-D and 2-D prefix-sum implementations with oracle tests, the subarray-sum-equals-k proof, the difference-array range-update lab, and the running example extended with range queries over event counts.

## Unit 6 — Frequency counting patterns
- **L1:** counting with a dict, with `Counter`, and with a fixed-size array for a small alphabet (`[0]*26`); `most_common`; counting characters, words, and numbers; comparing two frequency tables; the idea of a **histogram**.
- **L2:** anagram checks (sorted vs count array vs `Counter` equality) with costs; first unique character; ransom-note / can-construct; top-k frequent elements with `Counter.most_common`, with a heap (`heapq.nlargest`), and with bucket sort by frequency (O(n)) — compare all three on complexity and measurement; frequency of frequencies; sliding-window character counts (fixed window, forward link to module 03); valid-anagram with Unicode (why a 26-array is not general); counting pairs (n choose 2 from frequencies; handling large counts); sorting by frequency then key (stable tie-breaks).
- **L3:** correctness of bucket-sort top-k (bounded frequencies ≤ n); complexity of `Counter.most_common(k)` as documented (`[VERIFY]` how it is implemented and its cost for k vs all); array-vs-dict trade-offs (alphabet size, memory, speed, constants) measured; `Counter` arithmetic (`+`, `-`, `&`, `|`) semantics including dropping non-positive counts `[VERIFY]`; the **multiset** abstraction and its invariants; frequency-based reasoning for permutations, palindromes (at most one odd count), and "minimum deletions to make frequencies unique" (greedy with justification, forward link to module 11); counting with a **comparison to a sort-based approach** and when sorting wins.
- **L4:** heavy hitters in streams (link to Unit 12 Boyer-Moore and the generalization, Misra-Gries, named and sketched; Count-Min sketch awareness with forward link to module 17); bounded-memory frequency estimation vs exact counting (cost, error, when acceptable); parallel/partitioned counting and merging `Counter`s; skewed key distributions (Zipf-like) and hot keys; testing against oracles; memory footprint of large `Counter`s.
- **Must include:** the three top-k implementations benchmarked head to head, ≥ 10 solved problems, a Unicode-aware anagram implementation, and the running example's top-k actions.

## Unit 7 — Multidimensional arrays and matrices
- **L1:** a matrix as a list of lists; indexing `m[r][c]`; rows vs columns; iterating by row, by column, and diagonally; dimensions `(rows, cols)`; creating a matrix **correctly** and the classic bug `[[0]*n]*m` (shared rows, with a memory-diagram explanation) vs `[[0]*n for _ in range(m)]`; printing and visualizing.
- **L2:** transpose (comprehension and `zip(*m)`), reverse rows/cols, rotate 90° (transpose + reverse, and the in-place layer-by-layer method with a proof of the index mapping), spiral traversal (boundary-shrinking with invariants), set-matrix-zeroes (O(1) extra space with marker rows, with the trap of overwriting markers), diagonal traversal, search in a row/column-sorted matrix (staircase search, O(m + n) with proof), neighbors with direction arrays (`dirs = [(0,1),(1,0),(0,-1),(-1,0)]`) and bounds checking, flattening and index mapping `i*cols + j` ↔ `(i, j)`; grid problems as setup for BFS/DFS (forward link to module 08).
- **L3:** row-major vs column-major order and cache behavior (measured honestly in Python, with the limits stated), memory of list-of-lists vs flat list vs `array.array` vs `numpy` contrast; 2-D prefix sums (link to Unit 5); matrix multiplication naive O(n³) and the standard optimization of loop order (measured), Strassen named (awareness); in-place algorithms and their invariants; sparse matrices as a dict of `(r, c)` → value (trade-offs, complexity of operations); jagged arrays; bounds-handling strategies (sentinels/padding vs checks); proof that rotation by transpose + reverse equals rotation.
- **L4:** designing a `Matrix` class with safe indexing, shape validation, and documented complexity; large-grid memory budgeting; tensors and shape reasoning for ML (`reshape`, broadcasting rules as awareness, row-major strides conceptually, with a hand-written stride calculation in pure Python); testing with random matrices and an oracle; detecting aliasing bugs with tests; avoiding quadratic work in grid traversal by visited-marking.
- **Must include:** the aliasing-bug demonstration and tests, in-place rotation and spiral with proofs, a staircase-search proof, a sparse-matrix class, and a stride-calculator lab.

## Unit 8 — String manipulation and patterns
- **L1:** reversing, palindromes (two-index check), case handling, counting vowels/words, splitting/joining/trimming, character classification (`isalpha`, `isdigit`, `isalnum`, `isspace`), comparing, simple parsing with `split`; building strings from pieces.
- **L2:** valid palindrome (normalize with a two-pointer skip), longest common prefix (vertical scan, with complexity O(S) where S is the total characters), reverse words (split vs in-place on a `list` of chars), string compression (run-length encoding with write pointer), isomorphic strings (two maps), valid parentheses as a pointer to module 04 (stack) with a short solution, roman-numeral and integer conversions, atoi-style parsing with a **specification of all edge cases** (whitespace, sign, overflow policy, invalid input), add binary strings, `str.split` vs `re.split`, `partition`; text normalization pipeline (strip, casefold, collapse whitespace, remove punctuation) as a tested function.
- **L3:** correctness arguments and invariants for two-pointer string algorithms (palindrome check, compression write-pointer); **expand-around-center** for longest palindromic substring (O(n²) time, O(1) space, proof) and Manacher's algorithm named with a forward link to module 15; the cost model of Python string slicing in loops and how index passing avoids hidden O(n²); building results with a list and one `join`; parsing with state machines (a small finite-state parser for numbers with a transition table, tested); regular expressions as a tool and as a risk (backtracking), and when a hand-written scanner is safer; comparing O(n) one-pass solutions with simpler O(n log n) ones for maintainability.
- **L4:** tokenizers and lexers (a minimal tokenizer for arithmetic expressions as a mini-project, with tests), streaming parsers for large inputs, Unicode-correct manipulation (casefolding, normalization, grapheme awareness), robust input handling (never assume ASCII), property-based tests (round-trip: decode(encode(x)) == x; idempotence of normalization), fuzzing a parser with seeded random strings, code-review checklist for string code.
- **Must include:** ≥ 12 solved problems with proofs/invariants where required, the tokenizer, the number-parsing state machine, the normalization pipeline with property tests, and the running example's key normalization at scale.

## Unit 9 — Subarrays, substrings, and subsequences
- **L1:** precise definitions: a **subarray/substring is contiguous**, a **subsequence preserves order but need not be contiguous**, a **subset** ignores order; counting them (n(n+1)/2 contiguous, 2ⁿ subsequences, with proofs); generating all subarrays with nested loops and their O(n²) count (and O(n³) if you sum each naively); examples worked by hand.
- **L2:** the standard techniques for contiguous problems: brute force → prefix sums → hash map → sliding window (named, deferred to module 03) → Kadane; longest substring without repeating characters (hash map of last index, with window-start invariant), longest substring with at most k distinct characters (preview, deferred depth), count of subarrays with a property; is-subsequence (two pointers, O(n)); longest common subsequence **defined** and previewed with the brute-force exponential and a pointer to module 09 (DP); distinct subsequences counted and deferred; generating subsets with bitmasks and with recursion (preview; forward link to modules 05 and 10); how to decide which technique applies from the constraints and the property (a decision table).
- **L3:** proofs for the contiguous-count formulas and 2ⁿ; correctness of longest-substring-without-repeats (window invariant: no duplicates in `s[left:right+1]`, with the "jump left to last index + 1" move justified); why sliding window needs a **monotone** property (adding elements never fixes a violation, removing never creates one) and why it fails for sum-equals-k with negatives (counterexample); complexity of enumerating subsequences and the necessity of pruning/DP; the relationship among problems (maximum subarray sum, subarray sum equals k, longest subarray with sum k, shortest subarray with sum ≥ k — which technique each needs and why); output size vs computation (printing all subsequences is Ω(n·2ⁿ) regardless of cleverness).
- **L4:** designing for correct problem classification under time pressure (a classification procedure); mapping real tasks to the taxonomy (windowed log analytics → contiguous; event pattern detection → subsequence; feature combinations → subset); streaming variants with bounded memory; a **brute-force oracle library** that enumerates subarrays/subsequences for small n and drives differential tests; review checklist for window-boundary bugs.
- **Must include:** the contiguous/subsequence/subset comparison table with counts proved, ≥ 10 solved problems, the technique decision table with counterexamples, and the oracle library with tests.

## Unit 10 — Hashing, collisions, and performance trade-offs
- **L1:** what a hash function must do (deterministic, fast, uniform, avalanche intuition); non-cryptographic vs cryptographic hashes (a clear distinction, never to be confused); examples of simple hash functions for strings (sum of characters — bad; polynomial — better) and why the bad one collides on anagrams; collision as inevitable (pigeonhole).
- **L2:** implementing string hashes: additive, polynomial `h = (h*B + c) mod M` (Horner's rule), FNV-1a style and djb2 style as **named, well-known simple hashes** (write them from first principles, do not claim exact constants unless certain `[VERIFY]`); measuring collision counts and bucket distribution (chi-square-style uniformity check in pure Python, explained simply); the birthday bound (expected collisions among n items in m slots ≈ n²/(2m), derived and checked by simulation); `hashlib` (SHA-256, MD5) for content fingerprints and why MD5/SHA-1 are **not** for security; Python's `hash()` vs `hashlib` (process-randomized vs stable across runs — never persist `hash()` values or use them for sharding across processes).
- **L3:** load factor, resize, and cost trade-offs quantified (time vs memory vs probe length) with a measured sweep; chaining vs open addressing trade-off table (cache behavior, deletion, load tolerance, memory, worst case); universal hashing (definition; a simple family `((a*x + b) mod p) mod m` and the guarantee it provides, stated as a result with a sketch `[VERIFY]`); perfect hashing named; choosing a hash for the job (dict key, sharding, fingerprinting, dedup, integrity, security — a decision table); `__hash__` design for custom classes (hash only immutable fields used in `__eq__`); dataclass `frozen=True`/`unsafe_hash` semantics `[VERIFY]`; false-positive/collision probability for fingerprint-based dedup (derive the 2^(−b) style bound and the birthday limit for b-bit digests, with a worked example of when a 64-bit fingerprint is unsafe at scale).
- **L4:** adversarial settings: hash flooding, why randomization/seeding defends, what it does not defend (e.g., poor `__hash__` on custom keys); stable hashing for sharding across processes/machines (use a fixed-seed or cryptographic hash, never built-in `hash`), consistent hashing named with a forward link to module 18; locality-sensitive hashing and feature hashing named with forward links (module 19); measuring the real cost of hashing long keys and caching hashes; cryptographic hashing for integrity vs HMAC for authentication (awareness, security-accurate statements only); a **hash-quality test harness** (uniformity, avalanche, collision rate) with a regression guard; documenting collision assumptions in a design note.
- **Must include:** implementations of three string hashes with a quality-comparison harness, the birthday-bound derivation and simulation, the cross-process `hash()` instability demonstration (run the same script twice with different `PYTHONHASHSEED`), and the fingerprint-dedup risk calculation.

## Unit 11 — Kadane and maximum-subarray patterns
- **L1:** the problem (maximum sum of a non-empty contiguous subarray); brute force O(n³) → O(n²) with prefix sums; the Kadane insight: the best subarray ending at i either extends the best ending at i−1 or starts fresh at i; hand trace on an example with negatives.
- **L2:** Kadane implementation `best_ending = max(a[i], best_ending + a[i])` and its edge cases (all negative; empty-array policy: spec must say whether empty subarray is allowed); returning the **indices** of the subarray; maximum circular subarray sum (total − minimum subarray, with the all-negative trap); maximum product subarray (track max and min); best time to buy and sell stock as a Kadane variant (running minimum); maximum sum of at most one deletion (preview); variations: max subarray with length ≥ k (prefix-minimum trick); 2-D max rectangle sum named.
- **L3:** **proof of correctness** by induction/loop invariant (state: `best_ending[i]` is the max sum over subarrays ending at i; `best_overall` is the max over all i), and the proof that O(n) time/O(1) space is optimal for the problem (every element must be read: Ω(n)); the DP view (link to module 09): recurrence `f(i) = max(a[i], f(i−1) + a[i])`; divide-and-conquer O(n log n) alternative with the combine step (prefix/suffix/total/best tuple) and a comparison of constants, plus the monoid/associative-combine insight that enables parallel and segment-tree versions (forward link to module 13); proof of the circular case; correctness for products with zeros and negatives.
- **L4:** streaming Kadane with bounded memory and windowed variants; numerical issues (float accumulation); testing against the O(n²)/O(n³) oracles with random and adversarial arrays (all negative, all zero, alternating, large magnitudes); mapping to real tasks (best contiguous period of net gain in a metric time series, anomaly windows); reporting ties deterministically; code-review checklist for the spec ambiguity (empty vs non-empty, tie-breaking).
- **Must include:** Kadane with index tracking, circular and product variants, the divide-and-conquer combine, the induction proof, an oracle-based test suite, and the running example's best contiguous window of net events.

## Unit 12 — Boyer-Moore voting and majority element
- **L1:** the majority element (appears more than ⌊n/2⌋ times); brute force counting O(n²), dict counting O(n)/O(n) space, sorting-based O(n log n) (the middle element); the voting idea: pair off different elements; candidate and counter; hand trace.
- **L2:** the Boyer-Moore voting algorithm (candidate/count) in O(n) time and O(1) space; the **verification pass** (needed when a majority is not guaranteed); majority element II (> ⌊n/3⌋) with two candidates; generalization to > n/k with k−1 counters (Misra-Gries, described and implemented); streaming use; comparing the four approaches on time, space, and assumptions in a decision table.
- **L3:** **proof of correctness**: pairing/cancellation argument (removing a pair of distinct elements preserves the majority; formalize with the invariant "the multiset of (candidate × count) plus the removed distinct pairs equals the processed prefix"), and why the first pass alone only guarantees "if a majority exists, it is the candidate"; proof for the n/3 case (at most 2 elements can exceed n/3); Misra-Gries error guarantee stated precisely (undercount by at most n/(k)) `[VERIFY]`; why O(1) space is possible only because the question is restricted (lower-bound intuition: exact top frequency generally needs more space — forward link to module 17); mergeability of summaries for distributed use (named).
- **L4:** heavy-hitter detection in production streams (windowed, distributed, merged summaries), deciding when approximate answers are acceptable and how to report error; adversarial streams for the algorithm and the importance of verification; testing with oracles and property tests (if a majority exists the output equals the `Counter` result; if not, verification rejects); documenting the "assumes majority exists" precondition in API names and docstrings.
- **Must include:** Boyer-Moore and Misra-Gries implementations with the verification pass, the cancellation proof, a four-approach benchmark, an adversarial-input test set, and the running example's dominant action.

## Unit 13 — Dutch national flag and in-place partitioning
- **L1:** the problem: sort an array containing only 0, 1, 2 (or three categories) in one pass; why `sort` is O(n log n) and counting-sort-then-rewrite is two passes; pointers and swaps; in-place and its meaning.
- **L2:** the three-pointer solution (`low`, `mid`, `high`) with the swap rules and the **reason `mid` does not advance after swapping with `high`**; invariants for the four regions (`[0, low)` = 0s, `[low, mid)` = 1s, `[mid, high]` unknown, `(high, n)` = 2s); two-way partition (move zeros, separate even/odd, partition around a pivot value); remove element in place; partition by predicate with a read/write pointer; stable vs unstable partitioning (the stable version needs O(n) extra space or a more complex algorithm — state the trade-off).
- **L3:** **loop-invariant proof** (initialization, maintenance for each of the three cases, termination when `mid > high`) and the O(n) time, O(1) space bound with the exact swap count bound; Lomuto vs Hoare partition schemes compared (invariants, number of swaps, behavior with duplicates, a measured comparison) and their role inside quicksort (forward link to module 05); **three-way partitioning** for quicksort with many duplicates (and why it fixes the many-duplicates degradation measured in S3-01's adversarial-input style); quickselect (k-th element, expected O(n), worst-case O(n²), median-of-medians named as awareness) with the expected-cost argument; Python note: `list.sort` is Timsort, which is **not** partition-based `[VERIFY]`.
- **L4:** partitioning under adversarial and skewed input; randomized pivot and its expected-time guarantee; in-place algorithms in memory-constrained pipelines; partitioning large data by key (bucketing/radix ideas, forward links to modules 05, 10, 18); property-based tests (permutation preserved, regions correct, idempotence); generalizing to k categories (counting pass + prefix sums for placement positions, tying back to Unit 5) and comparing with the k-pointer approach.
- **Must include:** the Dutch national flag with the full invariant proof, Lomuto and Hoare partitions with a duplicate-heavy benchmark, three-way partitioning, quickselect, and permutation-preservation property tests.

## Unit 14 — Rolling hash and Rabin-Karp
- **L1:** the string-matching problem (find pattern P of length m in text T of length n); naive matching O(n·m) worst case with an example that triggers it; the idea of comparing **hashes** first; what a rolling hash is: update the hash of a window in O(1) when it slides by one.
- **L2:** polynomial rolling hash `H(s) = Σ s[i]·B^(m−1−i) mod M`; the O(1) slide `H' = (H − s[out]·B^(m−1))·B + s[in]  (mod M)` derived step by step with Python's non-negative `%` semantics handled correctly; choosing base B and modulus M (a prime; examples with a small prime for hand tracing and a large one for real use); the Rabin-Karp algorithm: compare hashes, **verify on equality** (to rule out collisions), expected O(n + m) and worst-case O(n·m); implementing it with tests; finding repeated substrings of a fixed length; multiple-pattern search (hash set of pattern hashes).
- **L3:** correctness: the proof that equal strings have equal hashes and the algorithm never misses a match; the collision probability for a random base modulo a prime (the polynomial-identity argument: two distinct strings of length m collide with probability ≤ m/M over a random base, stated as a result with a sketch `[VERIFY]`), and why a fixed, well-known (B, M) is **attackable**; double hashing with two moduli (and what it does and does not guarantee); why verification makes Rabin-Karp **Las Vegas** (always correct, random running time) and skipping verification makes it **Monte Carlo** (fast, small error probability) — define both precisely and measure collisions empirically; 2-D pattern matching named; hashing with a Mersenne-prime modulus (awareness, with `[VERIFY]` on any constant); longest duplicate substring via binary search on length + rolling hash (O(n log n) expected) as a worked advanced problem, with the monotonicity argument for the binary search.
- **L4:** adversarial inputs (anti-hash tests that break a fixed (B, M)), randomizing B at runtime and seeding for reproducible tests; comparison with KMP/Z (deferred to module 15), suffix arrays/automata (deferred), and Python's built-in `str.find` (state that CPython's implementation is an optimized, version-dependent search `[VERSION-SENSITIVE][VERIFY]` and measure it against the pure-Python Rabin-Karp — the built-in will usually win; explain why this is expected); plagiarism/near-duplicate detection and content-defined chunking as real uses (rolling hash for chunk boundaries named with a forward link to module 18; shingling and MinHash named with a forward link to module 19); testing with a naive oracle on random and adversarial strings; handling Unicode and bytes consistently.
- **Must include:** the derivation of the rolling update with a hand-traced example, Rabin-Karp with the verification pass, a collision-rate experiment with small M, the longest-duplicate-substring solution, an anti-hash demonstration (local only), and a benchmark against `str.find`.

# 7. PRACTICE QUESTIONS (UNIT 15) — REQUIREMENTS

Generate a full `practice-questions.md` body with **at least 280 questions**: ≥ 16 for each of Units 1–14, plus ≥ 30 cross-unit integration questions. Required distribution per unit (≥ 16 each):

- 4 × conceptual short-answer
- 3 × multiple choice (4 options; answer + explanation of every distractor)
- 3 × code analysis ("state the output and/or the time and space complexity and justify")
- 2 × proof/derivation (invariant, induction, recurrence, probability bound, formula)
- 2 × coding problems (spec, constraints, examples, model solution with tests, complexity)
- 1 × code review / bug-finding (find ≥ 3 defects, including at least one hidden-complexity or aliasing defect)
- 1 × measurement/benchmark interpretation ("Given this output, what is wrong with the conclusion?")

Every question carries: ID, level (L1–L4), objective it tests, time estimate, difficulty (Easy/Medium/Hard defined by explicit criteria such as insights required and state needed), **model answer**, and **common wrong answers**. Include a difficulty progression and a scoring rubric with pass thresholds (80% proceed; 60–79% remediate; below 60% repeat, consistent with the stage's gate rules). Include 10 "whiteboard / design-review" prompts requiring written trade-off reasoning, and 25 timed interview-style problems (20 minutes each) with model solutions that include the spoken complexity statement and the edge-case list. Include a **pattern-recognition drill**: 30 one-line problem statements where the learner names the technique (and the unit) before solving, with answers. Each question must test only content actually taught in Units 1–14 (plus S3-01).

# 8. SECTION NUMBER INTENTIONALLY UNUSED

(Kept so that section numbers match the other Stage 3 prompts. Nothing to generate here.)

# 9. UNIT 16 — PROJECTS README (REQUIREMENTS)

Include: purpose of the `Projects/` folder; how the two projects relate to Units 1–14 (a mapping table: project deliverable → unit) and to the Stage 3 toolkit (`../../00-Stage-3-Overview/Projects/01-algorithm-toolkit-and-benchmark.md`) and to S3-01's benchmark project; project index table (file, goal, estimated time, prerequisites, outputs); recommended order and dependency (Project 1 informs Project 2's benchmarking); submission and evidence folder structure; the 100-point grading scheme summary and pass thresholds; originality and AI-assistance policy (allowed for explanation and review, not for producing the graded implementations, always disclosed in the evidence log); an evidence-log template; a reproducibility checklist (seed, versions, machine info, command log); a "how to ask for a code review" template.

# 10. UNITS 17 AND 18 — PROJECTS (REQUIREMENTS)

Both follow the four levels and the N.0–N.14 skeleton **plus** the specification below.

## Unit 17 — Project: Build a hash map from scratch
**Scenario:** An engineer must understand exactly what a dictionary does, so they build one, make it correct, make it measurable, and compare it honestly with `dict`.

**Required deliverables (each with acceptance criteria checkable by command):**
1. Repository layout (`src/` layout, `tests/`, `bench/`, `results/`, `docs/`, `pyproject.toml`) and a `Makefile`/`justfile` with targets: `install`, `lint`, `test`, `bench`, `report`, `check`, `clean`, `all`.
2. **Two hash-map implementations** behind one interface (`MutableMapping`-compatible: `__getitem__`, `__setitem__`, `__delitem__`, `__len__`, `__iter__`, `__contains__`, `get`, `pop`, `setdefault`, `update`, `items`, `keys`, `values`): (a) **separate chaining**, (b) **open addressing with linear probing and tombstones**. Documented invariants, load-factor-driven resize (grow and optional shrink), insertion-ordered iteration as an **optional stretch** (compact-dict design).
3. A **hash-function plug-in interface** and at least three hash strategies (built-in `hash`, polynomial string hash, FNV-style) plus a deliberately bad hash used for degradation experiments.
4. **Correctness:** table-driven tests, edge cases (empty map, missing keys, `None` key, unhashable key raises `TypeError`, duplicate inserts, delete-then-reinsert, many collisions, resize boundary, iteration while mutating raises or is documented), **randomized differential testing against `dict`** with seeded operation sequences (insert/get/delete/resize), and a **stateful property test** (optional `hypothesis` stretch) verifying the map equals a model.
5. **Invariant checker:** a `_check_invariants()` method (size equals stored entries, load factor within bounds, no unreachable entries after deletion with tombstones, probe-chain integrity) invoked in tests.
6. **Instrumentation:** probe/comparison counters per operation; average and maximum chain/probe length; histogram of bucket occupancy.
7. **Experiments:** (a) lookup cost vs load factor for both strategies (measured and plotted/tabulated), (b) degradation with the bad hash vs a good hash (bounded sizes, local only), (c) amortized insert latency histogram across resizes, (d) memory per entry vs `dict` (`tracemalloc`), (e) comparison with built-in `dict` with a written, honest explanation of why `dict` is faster (C implementation, compact layout, specialized string-key paths, caching of hashes) tagged `[VERIFY]` where specific.
8. **Documentation:** architecture diagram, ADRs (≥ 3: collision strategy, resize policy, tombstone handling), complexity table (time and space, average and worst, amortized) with proofs or sketches, and a "limits of this implementation" section.
9. A **results template** the learner fills with their own measurements. Do not fabricate results.

## Unit 18 — Project: Array and string problem toolkit
**Scenario:** An engineer keeps re-solving the same array/string problems in interviews and at work. They build a verified, benchmarked, documented toolkit that plugs into the Stage 3 toolkit and covers every technique in this folder.

**Required deliverables:**
1. Repository layout and `Makefile` as above, structured as a package `arraystring_toolkit` with categories matching the units.
2. **At least 40 problems implemented** (≥ 2 per category where listed), each with: problem statement, constraints, **brute-force oracle**, optimized solution, declared time/space (worst/avg/amortized, n defined), invariant or proof note, unit tests, and edge cases. Categories (minimum): arrays and in-place (rotate, dedupe, move zeros, merge sorted), hash patterns (two-sum, group anagrams, longest consecutive, hash join), prefix sums (range sum, subarray-sum-equals-k, product except self, 2-D prefix sum, difference array), frequency (top-k three ways, anagram, ransom note), matrices (rotate, spiral, set zeroes, staircase search), strings (palindrome, compression, atoi with full spec, tokenizer, normalization), subarray/substring (longest substring without repeats, is-subsequence, window with at most k distinct preview), Kadane family (max subarray with indices, circular, product), voting (majority, majority II, Misra-Gries), partitioning (Dutch flag, Lomuto/Hoare, three-way, quickselect), rolling hash (Rabin-Karp, longest duplicate substring).
3. **Differential and property tests:** randomized comparison of every optimized solution with its oracle using seeded generators; adversarial generators per category (all equal, all negative, sorted, many duplicates, long strings with repeated characters, Unicode edge cases, empty and single-element inputs).
4. **Benchmark integration:** register each solution with the Stage 3 toolkit's registry (or provide a compatible interface if the toolkit is not yet built) and benchmark over a size ladder; fit growth exponents; a **regression guard** that fails `make check` if observed growth exceeds the declared class beyond a stated tolerance.
5. **Technique index:** a generated table mapping problem → technique → unit → complexity → recognition signal, and a **pattern decision flowchart** (mermaid) validated by a test that every problem is reachable.
6. **Documentation:** architecture diagram, ADRs (≥ 3: oracle strategy, tolerance policy, API/mutation contract), a "common bugs found by the oracle" log the learner fills in, and a one-page **review checklist for array/string/hash code**.
7. A **results template** (declared vs observed complexity, failures found, time-to-solve log for timed practice). Do not fabricate results.

**For both projects include:** a milestone plan (5–6 milestones with time estimates), a grading rubric (100 points, criterion-level descriptors for Poor / Adequate / Strong / Exemplary), stretch goals, common failure points, a self-review checklist, and the exact evidence folder structure.

**Provide complete, runnable starter code** for each project: package, tests, generators, benchmark scripts, Makefile, `pyproject.toml`. Every code file states its path in a first-line comment. Do not leave `TODO: implement` in required deliverables. Dependencies: standard library plus `pytest` for required parts; everything else optional.

# 11. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: src/hashmap/chaining.py`).
2. **Every command and snippet is paired with expected output** (representative, clearly labeled "example — yours will differ in timings, sizes, and memory addresses") and a short interpretation.
3. **Code must run.** Python 3.10+ syntax only (state if 3.12 is required). Standard library unless marked optional. Type hints on all public functions. Clarity over cleverness. Every solution states its **mutation contract** (does it modify the input?).
4. **Complexity statements must be precise:** worst-case, average-case, expected, or amortized; time **and** space; what n is; hashing cost of keys (O(L) for strings) stated where it matters; proof sketch or invariant for every non-trivial claim; algorithmic complexity separated from CPython constant factors and implementation details.
5. **Every algorithm ships with a brute-force oracle and tests** that pass on the reference code and fail on a deliberately broken variant (show it once per unit).
6. **No unproven performance claims.** Every speed or size claim ties to a measurement the learner can run (warm-up, repeats, statistic stated). Otherwise label it `[ILLUSTRATIVE — measure yours]`. Example outputs are labeled **representative**; never present a measured-looking number that was not measured.
7. **Benchmarks must avoid the usual errors** (see S3-01 Unit 6): reused mutated input, noise-floor timings, one size, single run, GC and caching ignored, measuring setup instead of the operation.
8. **Do not teach CPython implementation details as language guarantees.** Insertion-ordered dict (guaranteed since 3.7) is a guarantee; the compact-dict layout, probing sequence, list over-allocation, string `+=` optimization, interning rules, and small-int caching are implementation details tagged `[VERSION-SENSITIVE]`.
9. **No secrets, no network access, no paid APIs** in any lab. Adversarial demonstrations (hash collisions, anti-hash strings, regex backtracking) run **only locally against the learner's own code**, with bounded size and a timeout, and the text says so. Never present cryptographic claims beyond what is accurate (MD5/SHA-1 are not collision-resistant; non-cryptographic hashes give no security).
10. **Scripts are safe by default:** no deletion outside the project directory; `clean` targets list what they remove; random generators take explicit seeds; experiments have size caps and a `--quick` mode.
11. **Every lab ends with cleanup** and a verification that no stray files or processes remain beyond those documented.
12. **Proofs are written in full** where required (invariant: initialization, maintenance, termination; induction: base and step; probability bounds: assumptions stated). "It is obvious" is not a proof.
13. **Tag Python-version and implementation differences** (CPython vs PyPy, 3.10 vs 3.12) `[VERSION-SENSITIVE]`; call out WSL2 timing-noise sources where they affect a lab.
14. **Python-specific correctness traps are taught explicitly:** `%` with negatives, integer division with negatives, slicing copies, aliasing in `[[0]*n]*m`, mutable default arguments, `NaN` keys, floating-point accumulation, `is` vs `==`, modifying a collection while iterating.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You will act as author, then as an independent auditor of your own work, and you will include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every claim on **authoritative sources**: the official Python documentation (Language Reference "Data model" including `__hash__` and `__eq__`; Library Reference pages for built-in types `list`, `str`, `dict`, `set`, `tuple`, `bytes`, `bytearray`, and for `collections`, `array`, `itertools`, `bisect`, `heapq`, `hashlib`, `unicodedata`, `re`, `timeit`, `tracemalloc`, `sys`; the "What's New" pages for version-sensitive behavior; relevant PEPs such as PEP 393 for the flexible string representation), the Python Wiki **TimeComplexity** page, CPython design notes and source for implementation details (marked `[VERIFY]`), and standard texts cited by **title and chapter topic, not page numbers you cannot confirm**: *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein) — hash tables, universal hashing, string matching (Rabin-Karp), the maximum-subarray problem, quicksort partitioning; *Algorithms* (Sedgewick and Wayne) — hash tables, substring search; *The Algorithm Design Manual* (Skiena) — hashing, string problems; original-paper attributions for named algorithms (Rabin–Karp, Boyer–Moore majority vote, Misra–Gries, Kadane, Dijkstra's Dutch national flag) cited by **author, topic, and year only where you are certain**, otherwise `[VERIFY]`. Provide a URL only if you are certain it is canonical; otherwise cite by name and mark `[VERIFY]`.
- **Distinguish clearly** between the **Boyer–Moore majority vote algorithm** and the unrelated **Boyer–Moore string-search algorithm**, and say so in Unit 12.
- **Do not fabricate:** version numbers, benchmark results, timings, memory sizes presented as universal, CPython constants (growth factors, perturbation constants, hash constants unless certain), incident details, company practices, interview statistics, or quotes. If you need a number, derive it from a stated command or label it illustrative.
- **Mark uncertainty** with: `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[ASSUMPTION]`, `[JUDGEMENT]`.
- Keep a running **Claim Register** (Section 12.3) for every non-trivial claim.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 18 units present, in order, with every required section (Sections 5, 7, 9, 10), every unit-specific topic (Section 6), levels L1–L4. | Any missing section/topic. |
| 2 | **Mathematical correctness** | Every derivation, probability bound, modular-arithmetic step, rolling-hash update, and proof is re-derived independently and checked at small values by hand or by a stated script. | Any wrong formula, invalid proof, or unjustified step. |
| 3 | **Algorithmic correctness** | Every algorithm is traced by hand on at least one normal and one edge case; every invariant holds at initialization, maintenance, and termination; every algorithm is checked against its oracle on small exhaustive inputs. | Any algorithm that fails an edge case (empty, single, all-equal, all-negative, duplicates, Unicode). |
| 4 | **Technical accuracy** | Every Python function, signature, behavior, and complexity attribution is real and correct (e.g., `Counter.most_common`, `itertools.accumulate`, `str.translate`, `hash` semantics). Mentally execute every code block and lab. | Any invented function, misused API, or wrong bound. |
| 5 | **Executability** | Code blocks are syntactically valid; imports resolve; file paths and cross-references resolve; every test passes on the reference code and fails on a deliberately broken variant; every lab has steps, expected evidence, and cleanup. | Any broken, ambiguous, or unrunnable step. |
| 6 | **Complexity labeling audit** | Worst/average/expected/amortized labels are right; "n" is defined; key-hashing cost is accounted for; space includes recursion stack and auxiliary storage; slicing copies are counted; O is never described as "worst case"; amortized is never confused with average. | Any mislabeled or ambiguous bound. |
| 7 | **Guarantee vs implementation audit** | Every CPython statement is classified as language guarantee or implementation detail and tagged; no behavior of `dict`, `list`, `str` internals is stated as universal; PyPy/other differences noted. | Implementation detail presented as guarantee. |
| 8 | **Benchmark validity** | Methodology is sound; no result is presented as measured unless clearly labeled representative or a template; hash experiments have bounded sizes; fitted slopes interpreted with caveats. | Flawed method or fabricated numbers. |
| 9 | **Security accuracy** | Hash/crypto statements are accurate and not overstated; adversarial demos are local and bounded; no guidance that could be used against a third party. | Overclaim or unsafe demonstration. |
| 10 | **Currency** | Version-sensitive claims tagged; no deprecated feature taught as current; 3.10 minimum respected or differences noted. | Stale, untagged, or over-general claims. |
| 11 | **Fabrication scan** | Hunt for invented statistics, fake citations, fabricated benchmark outputs, made-up CPython internals, misattributed algorithms, and invented library features. | Any unsupported specific. |
| 12 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept (modular arithmetic, probability, induction, invariants) used before it is taught; terminology consistent; the running example evolves coherently; forward references are explicit. | Forward dependency without a note; terminology drift. |
| 13 | **Cross-consistency** | Practice questions test only taught content; every project deliverable maps to a unit; the technique index, decision tables, and checklists agree with the lessons; Unit 16 promises nothing Units 17–18 do not deliver; links to S3-00, S3-01, and later modules are correct; the 14 lesson names match Section 2 exactly. | Orphan question, orphan deliverable, or contradiction. |
| 14 | **Adversarial review** | Re-read as a skeptical staff engineer and as a hostile interviewer: "What here is wrong, misleading, or would teach a bad habit?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 15 | **Reproducibility** | Labs run within the 4 CPU / 8 GB / 30 GB baseline, need no paid service or network, are seeded and idempotent, have size caps and a `--quick` mode, and clean up. | Hidden cost, unseeded nondeterminism, or leftover state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendices)

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. Include at least **100 entries**, covering every built-in complexity claim, every CPython behavior claim, every theorem or formula used, every attribution of an algorithm, and every judgement of consequence.

**Appendix B — Audit Report** (table for passes 1–15): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** all `[VERIFY]` / `[VERSION-SENSITIVE]` / `[JUDGEMENT]` items grouped by area (CPython data model and built-ins, `dict`/`set` internals, string representation, standard-library modules, complexity claims, mathematical results, hashing and security, benchmark methodology), each with: *what to check*, *where to check (named source)*, *how to test it locally with one command or small script*. The reviewer must be able to close every item in under 4 hours.

**Appendix D — Known Limitations and Assumptions:** what the module intentionally does not cover (e.g., KMP/Z/suffix structures, Bloom filters and sketches, external hashing, cuckoo/Swiss-table internals beyond awareness, SIMD-accelerated search), assumed Python version, CPython-vs-PyPy caveats, WSL2 timing caveats, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the code, proofs, and benchmarks.

**Appendix F — Formula and Proof Index:** every formula and proof in the syllabus with its unit, statement, and proof technique.

**Appendix G — Executable Verification Bundle:** a `verify_syllabus.py` script (standard library only) that extracts every fenced Python block with a `# File: …` first-line comment, writes them to a scratch directory, byte-compiles them (`py_compile`), runs the test suite in `--quick` mode, and prints a PASS/FAIL list; plus a `verify_math.py` that numerically checks the key identities at small values (prefix-sum telescoping, 2-D prefix-sum inclusion–exclusion, subarray and subsequence counts, expected chain length, birthday-bound simulation with a fixed seed, rolling-hash update equals recomputed hash for random strings, Boyer-Moore candidate equals majority on random majority inputs, Kadane equals brute force on random arrays, Dutch-flag invariants on random arrays).

## 12.4 Trust rules
- If an audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim code "was tested/executed" unless it actually was in your environment. Use "expected output (representative)" instead.
- Never state that content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.
- Statements about **CPython internals** are implementation details: state them as such, tag `[VERSION-SENSITIVE]`, and prefer teaching the learner to **measure or inspect** them over asserting them.
- Attributions of algorithms to people or papers must be correct or marked `[VERIFY]`; never invent a citation.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-Arrays-Strings-and-Hashing.md`.
- Start with: title, one-paragraph abstract, metadata block (`Module: S3-02`, `Stage: 3`, `Language: Python`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 1–18 in order, then Appendices A–G.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons, fenced code blocks for all code, mermaid for diagrams, plain-text math (e.g., `H' = (H − out·B^(m−1))·B + in  (mod M)`) with Unicode symbols where clear; avoid LaTeX that may not render.
- Each unit is **self-contained but cross-linked** (relative links to sibling target files, S3-00, S3-01, and later modules).
- **Depth target:** Units 1–14 each ≥ 2,500 words of teaching text excluding code; practice questions ≥ 280 items; both projects complete with all code. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 1 |
| 2 | Unit 2 |
| 3 | Unit 3 |
| 4 | Unit 4 |
| 5 | Unit 5, Unit 6 |
| 6 | Unit 7 |
| 7 | Unit 8 |
| 8 | Unit 9, Unit 10 |
| 9 | Unit 11, Unit 12 |
| 10 | Unit 13, Unit 14 |
| 11 | Unit 15 part A (units 1–7 questions, drills) |
| 12 | Unit 15 part B (units 8–14 questions, integration, whiteboard, timed interview set) |
| 13 | Unit 16, Unit 17 part A: N.0–N.8 and specification with scaffold code |
| 14 | Unit 17 part B: experiments, tests, N.9–N.14, rubric, results template |
| 15 | Unit 18 part A: N.0–N.8 and specification with scaffold and first half of the problem set |
| 16 | Unit 18 part B: remaining problems, benchmark integration, N.9–N.14, rubric, results template |
| 17 | Appendices A–G (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/17 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–15, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 17 must run the **cross-part** audit (passes 12, 13, 14 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you are approaching the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 17, print the final assembly instruction: "Concatenate Parts 1–17 in order into `SYLLABUS-Arrays-Strings-and-Hashing.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 18 units present, in the specified order; Units 1–14, 17, and 18 each with levels L1–L4 and sections N.0–N.14.
- [ ] Every unit-specific topic in Sections 6, 7, 9, and 10 is taught at its stated level.
- [ ] Every required proof is written in full (invariants for in-place algorithms, Kadane, Dutch flag, voting; telescoping for prefix sums; expected chain length; birthday bound; rolling-hash update and collision bound).
- [ ] Every algorithm has a brute-force oracle, tests, an edge-case list, and a stated mutation contract.
- [ ] The ≥ 280 practice questions have model answers and distractor analysis; the 25 timed interview problems have model solutions; the 30-item pattern-recognition drill has answers.
- [ ] Project 1 has two correct hash-map implementations, differential and stateful tests, an invariant checker, instrumentation, and the five experiments; Project 2 has ≥ 40 problems with oracles, benchmarks, a regression guard, and a technique index; both have rubrics and results templates with **no fabricated results**.
- [ ] Every complexity claim is correctly labeled (worst/average/expected/amortized, time and space, n defined, key-hashing cost where relevant) and every performance claim is tied to a measurement or tagged illustrative.
- [ ] Every CPython implementation detail is tagged `[VERSION-SENSITIVE]` and language guarantees are separated from implementation details.
- [ ] Boyer–Moore majority vote and Boyer–Moore string search are explicitly distinguished.
- [ ] Every lab has steps, expected evidence, cleanup, seeds, and a `--quick` mode; all run within the free local baseline.
- [ ] No fabricated statistics, citations, versions, timings, attributions, or incident details; every uncertain item is tagged.
- [ ] Appendices A–G present; Claim Register ≥ 100 entries; audit passes 1–15 reported candidly.
- [ ] `verify_syllabus.py` and `verify_math.py` are delivered and consistent with the file-path comments in the code.
- [ ] A human can verify every open item in under 4 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/17**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 17 parts so the Claim Register, the running example, and the toolkit interfaces stay consistent. This is the largest prompt in Stage 3 so far (14 lessons and two projects); if a part truncates, type `continue` and it resumes at the stated section boundary.
2. **Do the human verification yourself.** Run `verify_syllabus.py` and `verify_math.py` (Appendix G), re-derive a sample of the proofs by hand (especially the rolling-hash update, the Dutch-flag invariant, and the Boyer-Moore cancellation argument), run the benchmarks on your machine, and close each `[VERIFY]` item against the Python docs.
3. **Spot-check fabrication risk areas first:** CPython `dict`/`set` internals and probing, `hash(-1) == hash(-2)`, PEP 393 memory behavior, `Counter.most_common` implementation and `Counter` arithmetic semantics, `str.find` implementation claims, Misra–Gries error bound, the Rabin-Karp collision-probability statement, dataclass `unsafe_hash` semantics, and any timing number that is not clearly a template.
4. **Scope note:** the folder's `README.md` is intentionally excluded, as it is not in the unit list you gave. Generate it with a separate prompt, or ask me to add it as a Unit 0.
5. **Final file layout:** save the LLM output as `SYLLABUS-Arrays-Strings-and-Hashing.md` in this folder. Later, split it into the 18 target files (`01-…14-…`, `practice-questions.md`, `Projects/README.md`, `Projects/01-build-a-hash-map-from-scratch.md`, `Projects/02-array-and-string-problem-toolkit.md`).
