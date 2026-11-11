# Practice Questions and Answer Key — Standard Library Toolkit

**Curriculum position:** Stage 1 — Programming & Computational Thinking → Module 1.13 — Standard Library Toolkit  
**Baseline:** Python 3.12+; version-specific behavior is labelled.  
**Assessment:** 35 questions · **Maximum:** 100 points · **Scope:** all ten lessons across Phases A–D.
**Source authority:** `Roadmap_ptree.md` establishes Stage 1 placement and the exact Module 13 tree; `roadmap-Standard-Library-Toolkit.md` defines the learning sequence, prerequisites, lesson outcomes, common mistakes, self-checks, and `datadrop` mini-project. The question bank is scoped to those sources.

## How to use this assessment

Attempt the questions before reading the answer key. Unless stated otherwise, use only the Python standard library and Python 3.12+. For code-writing questions, explain important failure modes and provide tests. Security questions should identify the trust boundary, not merely name an API. Some design questions have multiple valid solutions; the answer key gives one acceptable approach and the criteria for alternatives.

### Coverage and scoring

| Phase | Lessons | Questions | Points |
|---|---|---:|---:|
| A — Iteration and Functional Tools | 01–02 | Q01–Q07 | 16 |
| B — Files, Processes and Local Data | 03–05 | Q08–Q19 | 36 |
| C — Security Primitives and Numbers | 06–07 | Q20–Q26 | 21 |
| D — Config, Network and Runtime Utilities | 08–10 | Q27–Q35 | 27 |
| **Total** | **10 lessons** | **35** | **100** |

| Difficulty | Question IDs | Count | Points |
|---|---|---:|---:|
| Beginner | Q01, Q02, Q04 | 3 | 6 |
| Intermediate | Q03, Q05, Q06, Q07, Q08, Q10, Q12, Q13, Q15, Q18, Q20, Q21, Q23, Q24, Q25, Q27, Q28, Q30, Q32, Q34 | 20 | 58 |
| Advanced | Q09, Q11, Q14, Q16, Q17, Q19, Q22, Q26, Q29, Q31, Q33, Q35 | 12 | 36 |
| **Total** | **Q01–Q35** | **35** | **100** |

### Roadmap-to-question traceability

| Lesson | Roadmap outcomes sampled | Questions |
|---|---|---|
| 01 — `itertools` | Lazy/single-use iteration, `groupby`, batching, adjacent pairs, `zip_longest`, combinatorics, `tee` buffering, streaming | Q01–Q03, Q06–Q07 |
| 02 — `operator` and composition | Key extractors, stable multi-key sorting, transformation order, `partial`, reduction, serialization limits | Q04–Q05 |
| 03 — File/archive toolkit | Copy metadata trade-offs, temporary cleanup, atomic replacement, ZIP/TAR traversal and resource limits | Q08–Q10, Q17, Q19 |
| 04 — `subprocess` | Argument vectors, shell injection, timeout/return-code semantics, pipe deadlocks, descendant cleanup | Q11–Q12, Q18–Q19 |
| 05 — `sqlite3` | Parameters, transactions, uniqueness/upsert, indexes, WAL, bounded retry, idempotency | Q13–Q16, Q19 |
| 06 — Hashing and identifiers | Chunked SHA-256, canonical fingerprints, HMAC, replay/key handling, secure tokens, UUID versions, password KDFs | Q20–Q23, Q26 |
| 07 — Randomness and statistics | Independent RNGs, reservoir sampling, descriptive statistics, sample/population spread, Monte Carlo | Q24–Q25 |
| 08 — Configuration | TOML/INI parsing, source precedence, typed validation, unknown keys, secret handling | Q27–Q28, Q35 |
| 09 — Networking | URL construction, HTTP/network errors, bounds/timeouts, SSRF/TLS, TCP framing, loopback test server | Q29–Q31, Q35 |
| 10 — Runtime/object lifecycle | Context tokens and propagation, weak containers/observers, finalizers, cache retention, shallow/deep copy and memo | Q32–Q35 |

Difficulty labels: **Beginner**, **Intermediate**, **Advanced**. Question formats include output prediction, conceptual explanation, implementation, debugging, security review, test planning, and system design; the bank is not multiple-choice-only. Six explicitly marked **Security bug** questions address archive extraction, shell injection, SQL injection, insecure tokens, signature comparison, and TLS verification.

---

# Phase A — Iteration and Functional Tools

## Q01. Lazy iterators and exhaustion — 2 points
**Difficulty:** Beginner · **Lesson 01 — `itertools`**
**Expected response:** Output prediction + explanation  
**Evaluation focus:** Iterator exhaustion, lazy consumption, `zip` versus `zip_longest`, adjacent pairs, cumulative operations.

Predict the output and explain why the second conversion is empty. Then briefly state when `zip_longest` is preferable to `zip`, what `pairwise` yields, and why `accumulate` is useful for running totals.

```python
from itertools import count, islice
it = islice(count(10, 5), 3)
print(list(it))
print(list(it))
```

## Q02. Consecutive grouping — 2 points
**Difficulty:** Beginner · **Lesson 01 — `groupby`, sorting, streaming**
**Expected response:** Conceptual explanation + corrected code  
**Evaluation focus:** Consecutive-only grouping, key ordering, streaming versus sort materialization.

A log contains `events = [('b', 1), ('a', 2), ('b', 3)]`. Explain why `itertools.groupby(events, key=lambda row: row[0])` produces two groups for key `'b'` rather than one. Write a corrected approach and state its memory trade-off.

## Q03. Bounded batching — 2 points
**Difficulty:** Intermediate · **Lesson 01 — `batched`, laziness**
**Expected response:** Implementation + edge-case explanation  
**Evaluation focus:** Bounded batching, positive-size validation, Python 3.12 API.

Write a Python 3.12+ function that yields tuples of at most `size` items from an iterable without materializing the whole iterable. State behavior for `size <= 0`, show the batches for `range(7)` with size 3, and explain why `itertools.batched` is suitable for streaming ingestion.

## Q04. `operator` helpers and multi-key sorting — 2 points
**Difficulty:** Beginner · **Lesson 02 — `itemgetter`, `attrgetter`, `methodcaller`, stable sorting**
**Expected response:** Runnable code + explanation  
**Evaluation focus:** `operator` helpers, multi-key ordering, sort stability.

Given:

```python
rows = [{'team': 'B', 'score': 8}, {'team': 'A', 'score': 8}, {'team': 'A', 'score': 5}]
```

Sort by `team` ascending, then `score` descending. Use `operator.itemgetter` or another standard-library helper where it improves clarity. Explain sort stability and give one example where `attrgetter` or `methodcaller` is a better fit than a lambda. **Expected response:** runnable code plus a short explanation.

**Evaluation (2):** correct order (1); stable-sort/helper rationale (1).

## Q05. Composition, partial application, reduction, and callable serialization — 3 points
**Difficulty:** Intermediate · **Lesson 02 — functional composition**
**Expected response:** Code + design explanation  
**Evaluation focus:** Composition order, `partial`, reduction trade-offs, pickle limitations.

A record pipeline must (1) discard records whose `bytes` value is zero, (2) extract the byte count, (3) convert it to MiB, and (4) sum the result. Show a readable solution using `operator.itemgetter` and either a comprehension or `map`/`filter`; then show where `functools.partial` could bind a reusable parameter. Explain composition order and why a local lambda or nested function is often unsuitable for standard `pickle` serialization. **Do not introduce third-party packages.**

**Evaluation (3):** correct transformation (1); composition/partial reasoning (1); serialization caveat and readability trade-off (1).

## Q06. Iterator debugging — 3 points
**Difficulty:** Intermediate · **Lesson 01 — `tee`, streaming and consumption**
**Expected response:** Debugging + design alternative  
**Evaluation focus:** `tee` buffering, backpressure, one-pass streaming.

A developer writes:

```python
from itertools import tee
left, right = tee(huge_stream)
for item in left:
    process(item)
for item in right:
    audit(item)
```

Explain the buffering risk and why this may approach the memory cost of materializing the stream. Propose a better design if both actions can be performed per item, and one alternative if consumers must run independently.

## Q07. Cartesian products and combinatorial growth — 2 points
**Difficulty:** Intermediate · **Lesson 01 — `product`**
**Expected response:** Calculation + code sketch  
**Evaluation focus:** Cartesian-product cardinality, lazy enumeration, combinatorial growth.

A test generator combines 8 database backends, 6 serialization formats, and 5 compression settings. How many combinations exist? Show how to iterate lazily with `itertools.product`, and explain why laziness does not make a combinatorial explosion computationally free.

---

# Phase B — Files, Processes and Local Data

## Q08. Atomic file replacement — 3 points
**Difficulty:** Intermediate · **Lesson 03 — `tempfile`, `shutil`, atomic writes**
**Expected response:** Implementation + failure analysis  
**Evaluation focus:** Same-directory temp file, replacement, cleanup, durability and metadata trade-offs.

Design `write_atomically(destination, data: bytes)` for a local filesystem. Write the data to a temporary file in the destination directory, flush it, and replace the destination only after a complete write. Explain cleanup on failure and distinguish atomic replacement from crash durability. State when `fsync` on the file and parent directory may matter. Also compare `shutil.copyfile`, `copy`, and `copy2` at a high level, including why copied metadata is not a complete preservation/backup guarantee.

## Q09. Security bug — unsafe ZIP extraction — 3 points
**Difficulty:** Advanced · **Lesson 03 — archive security**
**Expected response:** Security review + mitigation plan  
**Evaluation focus:** Archive path traversal, links, duplicate paths, resource exhaustion.

The following code extracts an archive uploaded by an external user:

```python
from zipfile import ZipFile
with ZipFile(upload) as archive:
    archive.extractall(output_dir)
```

Identify the security risks and provide a defensive extraction strategy. Explain that supported `zipfile` extraction methods sanitize some absolute and parent-traversal components, so do not falsely assume every `../` entry escapes on current Python; also explain why this normalization is not a complete application-level policy. Discuss links/platform differences, decompressed-size limits, duplicate/colliding names, overwrites, and why merely checking that the archive opens successfully is insufficient.

## Q10. Temporary directories and cleanup — 3 points
**Difficulty:** Intermediate · **Lesson 03 — `tempfile`**
**Expected response:** Runnable example + explanation  
**Evaluation focus:** Temporary-resource lifecycle, secure creation, exception-safe cleanup.

Write a short example that creates a temporary directory, writes a file, uses it, and guarantees cleanup even if processing raises. Explain why predictable temporary filenames in a shared directory are unsafe and when `TemporaryDirectory` is preferable to `mktemp`.

## Q11. Security bug — shell injection — 3 points
**Difficulty:** Advanced · **Lesson 04 — `subprocess`**
**Expected response:** Debugging + corrected implementation  
**Evaluation focus:** Shell injection, argv construction, timeout/exit/start failures.

Review:

```python
import subprocess
subprocess.run(f"grep {user_pattern} {filename}", shell=True, check=True)
```

Identify the trust-boundary failure. Replace it with a safe argument-list approach, add a timeout and captured output, and explain how to handle `TimeoutExpired` and `CalledProcessError`. State why `shell=False` does not eliminate every risk (for example, executable selection and untrusted arguments to the invoked program).

## Q12. Subprocess lifecycle — 3 points
**Difficulty:** Intermediate · **Lesson 04 — timeouts and process cleanup**
**Expected response:** Runnable code + lifecycle analysis  
**Evaluation focus:** `run`, captured output, timeout and descendant-process limitations.

Write a portable Python snippet that invokes the current interpreter with `-c` and a short script, captures text output, checks the exit status, and times out after 2 seconds. Explain why a timeout is not a universal guarantee that every descendant process has been terminated, and describe a platform-aware process-tree cleanup strategy.

## Q13. SQLite parameters and transactions — 3 points
**Difficulty:** Intermediate · **Lesson 05 — parameterized SQL**
**Expected response:** SQL implementation + explanation  
**Evaluation focus:** Bound parameters, unique constraints, transaction semantics, duplicate policy.

Implement a function that inserts `(event_id, status)` into a SQLite table with a unique `event_id`. Use parameterized SQL and a transaction. Explain what can go wrong with f-string SQL and how to choose between rejecting duplicates and an idempotent `ON CONFLICT` policy.

## Q14. Security bug — SQL injection — 3 points
**Difficulty:** Advanced · **Lesson 05 — SQL security**
**Expected response:** Bug diagnosis + code + test  
**Evaluation focus:** SQL injection prevention, parameter binding, quote-containing values.

```python
sql = f"SELECT * FROM users WHERE username = '{username}'"
rows = connection.execute(sql).fetchall()
```

Identify the bug and correct it with placeholders. Explain why quoting/escaping user input manually is inferior to parameter binding. Include a test that uses an input containing a quote and verifies it is treated as data, not SQL syntax.

## Q15. SQLite concurrency and WAL — 3 points
**Difficulty:** Intermediate · **Lesson 05 — transactions and concurrency**
**Expected response:** Architecture explanation + retry policy  
**Evaluation focus:** WAL constraints, lock contention, indexes, idempotent retries.

A local ingestion process has multiple readers and one writer. Explain what WAL mode changes, what it does not change, and why SQLite still has write-contention constraints. Recommend a bounded retry/backoff policy for transient lock errors and explain why retrying an entire non-idempotent operation blindly can duplicate side effects. Include how you would decide whether an index is useful for a frequent lookup, and its write/storage trade-off.

## Q16. Idempotent ingestion — 3 points
**Difficulty:** Advanced · **Lesson 05 — idempotency**
**Expected response:** Schema/transaction design  
**Evaluation focus:** Stable identity, content hashes, uniqueness, atomic idempotent processing.

Design a table and transaction strategy for processing files so re-running the same file does not duplicate its rows. Include a content hash or stable file identity, uniqueness constraints, and a transaction boundary. Explain the difference between “same path” and “same content” as an idempotency key.

## Q17. Archive safety review — 3 points
**Difficulty:** Advanced · **Lesson 03 — TAR/ZIP extraction policy**
**Expected response:** Security checklist + extraction policy  
**Evaluation focus:** TAR path/link/device defenses, resource budgets, staging/promotion.

You need to extract an untrusted `.tar.gz` into a staging directory. List the validation and resource limits you would enforce before promoting the extracted tree. Include absolute paths, `..`, links, device entries, member count, total expanded bytes, and atomic promotion. Mention that safe behavior and available extraction filters can differ by Python version; do not treat a version-specific default as a substitute for explicit policy.

## Q18. `subprocess` error semantics — 3 points
**Difficulty:** Intermediate · **Lesson 04 — return codes**
**Expected response:** API comparison + failure matrix  
**Evaluation focus:** `run` versus `Popen`, return codes, exceptions, pipe deadlocks.

Compare `subprocess.run(..., check=True)`, `check=False`, and `Popen`. Give a case where `Popen` is justified. Explain the difference among a timeout, a non-zero exit status, and failure to start the executable, and name the relevant exception types. Explain how waiting on one pipe while the child fills another can deadlock, and how `communicate()` or concurrent draining avoids that pattern.

## Q19. Testable file/process/database pipeline — 3 points
**Difficulty:** Advanced · **Lessons 03–05 — integrated testing**
**Expected response:** Test plan + failure-path matrix  
**Evaluation focus:** Isolation, real local integration, controlled fault injection, cleanup.

Specify a pytest strategy for a pipeline that downloads or copies input into a temporary directory, invokes a subprocess, and persists results to SQLite. Identify what should be tested with real local resources and what should be mocked. Include at least four failure-path tests and explain why tests must not depend on a system-installed external utility unless that dependency is explicit.

---

# Phase C — Security Primitives and Numbers

## Q20. Streaming hashes, canonical fingerprints, and password storage — 3 points
**Difficulty:** Intermediate · **Lesson 06 — `hashlib`, content identity**
**Expected response:** Runnable implementation + design explanation  
**Evaluation focus:** Incremental digest, canonical fingerprints, trusted digests, password KDFs.

Implement a chunked SHA-256 file digest. Then explain how to create a stable fingerprint for a dictionary when key order should not affect the result, and why hashing a password once with SHA-256 is not an appropriate password-storage design. Distinguish an integrity checksum from authenticated integrity. **Expected response:** runnable file-hash function plus design explanation.

**Evaluation (3):** bounded-memory file hash (1); deterministic canonical representation (1); correct password-hashing/authenticity distinction (1).

## Q21. HMAC verification and protocol boundaries — 3 points
**Difficulty:** Intermediate · **Lesson 06 — `hmac`, key management**
**Expected response:** Runnable verifier + negative tests  
**Evaluation focus:** HMAC construction, strict tag validation, replay/key limitations.

Implement `verify(key: bytes, message: bytes, supplied_hex: str) -> bool` using HMAC-SHA-256 and `hmac.compare_digest`. Reject malformed hex and wrong-length tags. Explain what HMAC does and does not provide, why `sha256(key + message)` is not a substitute, and when timestamps/nonces are needed to prevent replay. **Expected response:** runnable function and two negative tests.

**Evaluation (3):** correct HMAC construction (1); safe tag validation/comparison (1); protocol limitations/replay explanation (1).

## Q22. Security bug — insecure token generation — 3 points
**Difficulty:** Advanced · **Lesson 06 — `secrets` vs `random`**
**Expected response:** Security bug diagnosis + replacement  
**Evaluation focus:** `secrets` versus `random`, token lifecycle and storage.

```python
import random
reset_token = str(random.getrandbits(64))
```

Identify the security issue and replace the code with a cryptographically suitable token generator. Explain the difference between `random.Random` for reproducible simulations and `secrets` for authentication tokens. State why seeding `random` does not make it secure.

## Q23. UUID choices and stable record identity — 3 points
**Difficulty:** Intermediate · **Lesson 06 — `uuid`**
**Expected response:** Decision table + explanation  
**Evaluation focus:** UUID version selection, Python-version boundaries, canonical deterministic names.

Choose an identifier strategy for (a) random unique IDs, (b) deterministic IDs from a namespace and stable name, and (c) roughly time-ordered IDs. State which UUID versions are available in Python 3.12 and how Python 3.14 changes the picture. Explain why UUIDs are not authorization secrets and why deterministic IDs require a well-defined canonical name. **Expected response:** design comparison, not just a list of function names.

**Evaluation (3):** correct versions/selection (1); version-awareness (1); identity/security caveats (1).

## Q24. Independent RNGs and reservoir sampling — 3 points
**Difficulty:** Intermediate · **Lesson 07 — reproducibility and streaming samples**
**Expected response:** Runnable algorithm + complexity explanation  
**Evaluation focus:** Independent RNGs, Algorithm R, O(k) memory, edge cases.

Create two independent `random.Random(2026)` instances and show reproducible sampling without changing module-global random state. Then implement Algorithm R reservoir sampling for an iterable of unknown length, returning up to `k` uniformly selected items with `O(k)` memory. State behavior for `k < 0` and `k == 0`. Explain why `random` is not suitable for security tokens.

**Evaluation (3):** independent reproducible RNG (1); correct bounded-memory reservoir (1); edge/security explanation (1).

## Q25. Descriptive statistics, sample/population variance, and simulation — 3 points
**Difficulty:** Intermediate · **Lesson 07 — `statistics`**
**Expected response:** Calculations + statistical interpretation  
**Evaluation focus:** Mean/median/mode, sample/population standard deviation, Monte Carlo limits.

For `values = [2, 4, 4, 10]`, compute mean, median, and mode. Explain `stdev` versus `pstdev`, define behavior for empty input and multiple modes, and describe a small Monte Carlo experiment that estimates a quantity while recording its seed and trial count. Do not claim that one run proves a mathematical result.

**Evaluation (3):** correct statistics (1); sample/population and edge-case distinction (1); sound simulation/reproducibility explanation (1).

## Q26. Security bug — unsafe signature comparison — 3 points
**Difficulty:** Advanced · **Lesson 06 — HMAC verification**
**Expected response:** Security review + corrected verifier  
**Evaluation focus:** Timing behavior, strict encoding, key/canonicalization/replay risks.

```python
if expected_tag == supplied_tag:
    accept()
```

Assume both values are strings representing HMAC tags. Explain the timing concern, show strict expected-encoding/length validation, and use `hmac.compare_digest`. Explain why constant-time comparison cannot compensate for a leaked key, weak algorithm, inconsistent canonicalization, or missing replay controls.

**Evaluation (3):** identifies the timing issue (1); correct comparison and validation (1); broader protocol limits (1).

# Phase D — Config, Network and Runtime Utilities

## Q27. Layered configuration and validation — 3 points
**Difficulty:** Intermediate · **Lesson 08 — `tomllib`, `configparser`**
**Expected response:** Configuration design + validation code  
**Evaluation focus:** Precedence, typed settings, finite positive timeout, secret/unknown-key policy.

Design configuration precedence for defaults, a TOML file, environment variables, and command-line arguments. State the precedence order and validate a `timeout_seconds` value as finite and positive. Explain that `tomllib` parses TOML but does not write TOML, and discuss how you handle unknown keys and type mismatches.

## Q28. `configparser` interpolation and types — 3 points
**Difficulty:** Intermediate · **Lesson 08 — INI configuration**
**Expected response:** Explanation + parsing example  
**Evaluation focus:** INI string conversion, typed getters, interpolation, validation.

A config contains:

```ini
[service]
base_url = https://example.invalid
retries = 3
timeout = 2.5
```

Explain why values read by `ConfigParser` are strings by default, how to obtain integer/float values, and what interpolation can do. Describe how to avoid surprising interpolation for literal percent signs and why validation should occur after parsing.

## Q29. Security bug — TLS verification disabled — 3 points
**Difficulty:** Advanced · **Lesson 09 — HTTPS and trust**
**Expected response:** Security diagnosis + remediation plan  
**Evaluation focus:** TLS trust chain, hostname checks, custom CA without verification bypass.

A developer adds `context = ssl._create_unverified_context()` to make an HTTPS request “work around” a certificate error. Identify the risk and give a safer diagnosis/fix path. Explain certificate-chain and hostname verification, custom CA configuration, and why disabling verification enables man-in-the-middle attacks.

## Q30. Bounded HTTP JSON client and local test server — 3 points
**Difficulty:** Intermediate · **Lesson 09 — `urllib`, HTTP status, test fixtures**
**Expected response:** Runnable client + test-fixture design  
**Evaluation focus:** Bounded body reads, URL construction, errors, timeout scope, SSRF and local server.

Write a function using `urllib.request` to GET JSON with a positive timeout, read no more than `max_bytes + 1`, handle `HTTPError`, `URLError`, invalid UTF-8/JSON, and oversized responses. Briefly explain safe query construction with `urllib.parse.urlencode` and the distinct purposes of `quote` and `urljoin`. Explain why a socket timeout is not necessarily a total wall-clock deadline and identify the additional controls needed when URLs are user-controlled. Describe a `ThreadingHTTPServer` fixture bound to `127.0.0.1` and port `0` that is always shut down and joined in cleanup.

**Evaluation (3):** bounded client/error handling (1); timeout/SSRF reasoning (1); deterministic local-server lifecycle (1).

## Q31. TCP framing and short reads — 3 points
**Difficulty:** Advanced · **Lesson 09 — sockets**
**Expected response:** Protocol implementation + explanation  
**Evaluation focus:** Exact reads, early EOF, framing, payload caps.

A TCP protocol sends a 4-byte network-order length followed by that many payload bytes. Write or describe `recv_exact(sock, n)` that handles short reads and raises on early EOF. Enforce a maximum payload length before allocation. Explain why one `recv()` call is not guaranteed to return a complete application message and why a length prefix needs limits.

## Q32. ContextVar tokens and explicit thread propagation — 3 points
**Difficulty:** Intermediate · **Lesson 10 — `contextvars`**
**Expected response:** Runnable context scope + propagation explanation  
**Evaluation focus:** Token reset, async task behavior, thread/executor propagation, version notes.

Implement a request-ID `ContextVar` scope that always resets with its token. Explain nested scopes and why resetting to a fixed default is wrong. State how context behaves for `asyncio` tasks, `asyncio.to_thread()`, and arbitrary `ThreadPoolExecutor.submit()` work; show explicit propagation using `contextvars.copy_context()` for executor work. Mention the Python 3.14 `threading.Thread(context=...)` option without assuming it exists in Python 3.12/3.13.

**Evaluation (3):** token-safe reset (1); async/thread distinctions (1); explicit propagation/version note (1).

## Q33. Weak caches, observer lifetimes, and finalization — 3 points
**Difficulty:** Advanced · **Lesson 10 — `weakref`, `WeakMethod`, `finalize`, cache retention**
**Expected response:** Lifecycle analysis + test design  
**Evaluation focus:** Weak containers, `WeakMethod`, `lru_cache`, `finalize` versus `__del__`, GC evidence.

Explain when `WeakValueDictionary`, `WeakKeyDictionary`, and `WeakSet` are appropriate and their eligibility/lifetime constraints. Describe how a bound method can retain its instance, how `weakref.WeakMethod` helps an observer registry, and why `functools.lru_cache()` strongly retains keys/results until eviction or clearing. Compare `weakref.finalize()` with `__del__()` and propose a test using `weakref.ref`, `del`, and `gc.collect()` that does not assume universal collection timing.

**Evaluation (3):** correct weak-container/cache semantics (1); callback/finalizer lifetime analysis (1); evidence-aware test strategy (1).

## Q34. Copy semantics, shared references, cycles, and resources — 3 points
**Difficulty:** Intermediate · **Lesson 10 — `copy.copy`, `copy.deepcopy`, memo**
**Expected response:** Code tracing + identity explanation  
**Evaluation focus:** Shallow/deep copy, shared references, cycles, memo, resource ownership.

Predict the values and identity relationships after:

```python
import copy
shared = []
source = {'left': shared, 'right': shared}
source['self'] = source
shallow = copy.copy(source)
deep = copy.deepcopy(source)
source['left'].append('changed')
```

Explain which references are shared in `shallow` and `deep`, how `deepcopy`'s memo preserves cycles and repeated references, and when a custom `__deepcopy__(memo)` or explicit non-copyable resource policy is appropriate. Do not assume open files, locks, sockets, or database connections can meaningfully be deep-copied.

**Evaluation (3):** correct value/identity predictions (1); memo/cycle explanation (1); resource ownership design (1).

## Q35. Integrated challenge — `datadrop` ingestion tool — 3 points
**Difficulty:** Advanced · **Lessons 01–10 — capstone design**
**Expected response:** System design + acceptance tests  
**Evaluation focus:** End-to-end roadmap integration, safety, idempotency, observability, cleanup.

Design a small CLI that reads TOML configuration with environment/CLI overrides, fetches a list of files over HTTP, verifies SHA-256 against a trusted manifest, streams and batches CSV rows, performs idempotent SQLite upserts, archives raw files safely, and invokes an external compressor with a timeout. Add run IDs with `contextvars`; tests must use a local HTTP server fixture and temporary filesystem/database resources.

Provide component boundaries, failure policy, security controls, transaction/idempotency strategy, and at least six acceptance tests. Require at least 90% line coverage measured with an explicitly named development/test tool (for example, `pytest-cov`), clean `ruff` and type-checker runs, and a README with a practical runbook. No third-party runtime dependencies are required; development tools may be declared separately. Explain why coverage targets do not prove correctness.

**Evaluation (3):** coherent pipeline and safe boundaries (1); idempotency/failure handling (1); tests and operational constraints (1).

---

## Integrated practical challenges (additional practice; scored separately from the 100-point question bank)

These are deliberately larger than a single interview question. Use only the standard library at runtime; `pytest` is a development/test dependency.

### Challenge A — Bounded-memory event pipeline

**Lessons:** 01–02, 07. **Deliverable:** a function that accepts an arbitrary iterable of dictionaries, filters invalid/zero-byte rows, normalizes a key, batches accepted rows, and reports counts without materializing the input. Requirements: reject non-positive batch size; deterministic tie-breaking; document `groupby` ordering; expose a seeded sample option using a dedicated `random.Random`; include tests for empty input, one partial final batch, duplicate keys, and a generator that raises midway. **Acceptance:** memory grows with the current batch and explicit sample, not the full source; no global RNG mutation; error behavior is documented.  **Challenge rubric (10):** streaming/batching (3), correct validation and deterministic ordering (2), isolated sampling (2), edge/failure tests (2), clarity and complexity explanation (1).

### Challenge B — Safe file-to-SQLite ingestion

**Lessons:** 03–06. **Deliverable:** process one local CSV into SQLite with chunked SHA-256, temporary staging, parameterized inserts/upserts, a uniqueness constraint, and a transaction. Write an archive only after validation and use an atomic replace for the finished artifact. **Acceptance:** duplicate reruns are idempotent; malformed input rolls back according to the stated unit of work; temporary files are removed on failure; archive extraction is not performed on untrusted data without explicit validation; no SQL is built from values with string interpolation. Test empty input, hash mismatch, duplicate IDs, injected database failure, and interrupted output writing.  **Challenge rubric (10):** bounded-memory digest/processing (2), safe temp/atomic-output lifecycle (2), parameterized SQL and transaction design (2), idempotency (2), failure tests and cleanup (2).

### Challenge C — Configuration-driven HTTP worker

**Lessons:** 08–10. **Deliverable:** load TOML plus environment and CLI overrides into a validated immutable settings object; fetch JSON from a local test server with timeout and response-size bounds; attach a request ID to logs through `ContextVar`; run one blocking worker through `asyncio.to_thread()` and another through a regular executor with explicit `copy_context()` propagation. **Acceptance:** invalid configuration fails before network access; server fixture always shuts down; context resets after success and exceptions; executor propagation is tested explicitly; TLS verification is never disabled for production traffic; no claim is made that a timeout is a universal end-to-end deadline.  **Challenge rubric (10):** configuration precedence/validation (2), bounded HTTP/error handling (2), safe local-server fixture (2), correct context propagation/reset (2), tests and security reasoning (2).

# Answer Key and Evaluation Guidance

Answers below are model answers, not the only acceptable designs. For open-ended questions, award full credit when the solution meets the stated requirements, explains trade-offs, and handles the important failure cases. Deduct for unsafe shortcuts even if the happy path works.

## Answer 1 — Q01

Output:

```text
[10, 15, 20]
[]
```

`islice` returns an iterator; converting it to a list consumes it. Iterators are generally single-pass. `zip` stops at the shortest input, while `zip_longest` continues to the longest and fills missing values with a sentinel/default. `pairwise` yields overlapping adjacent pairs, and `accumulate` produces running totals (or another cumulative operation). If two consumers need independent traversals, decide whether buffering or materialization is acceptable rather than assuming an iterator can be replayed.

## Answer 2 — Q02

`groupby` groups **consecutive** equal keys, not all equal keys across an arbitrary iterable. Sorting by the same key first gives one group per key:

```python
from itertools import groupby

events = [('b', 1), ('a', 2), ('b', 3)]
for key, group in groupby(sorted(events, key=lambda row: row[0]), key=lambda row: row[0]):
    print(key, list(group))
```

Sorting materializes the data and costs typically `O(n log n)` time and `O(n)` space. If input is already ordered by key, `groupby` can stream. Group iterators should be consumed before advancing to the next group.

## Answer 3 — Q03

```python
from itertools import batched

def batches(iterable, size):
    if size <= 0:
        raise ValueError("size must be positive")
    yield from batched(iterable, size)

assert list(batches(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]
```

`itertools.batched` is available in Python 3.12+. It consumes only enough input to form the next tuple; the caller still controls downstream buffering. Rejecting non-positive sizes makes the API contract explicit.

## Answer 4 — Q04

```python
from operator import itemgetter

rows = [
    {'team': 'B', 'score': 8},
    {'team': 'A', 'score': 8},
    {'team': 'A', 'score': 5},
]
rows.sort(key=itemgetter('score'), reverse=True)
rows.sort(key=itemgetter('team'))
assert rows == [
    {'team': 'A', 'score': 8},
    {'team': 'A', 'score': 5},
    {'team': 'B', 'score': 8},
]
```

Python's sort is stable, so the second sort by `team` preserves the first sort's descending score order within each team. A tuple key such as `(row['team'], -row['score'])` is shorter for numeric scores, but negation does not generalize to arbitrary score types. `attrgetter('name')` is useful for object attributes; `methodcaller('strip')` calls a method with fixed arguments. Use helpers when they clarify intent, not merely to avoid a short lambda.

## Answer 5 — Q05

```python
from functools import partial, reduce
from operator import itemgetter

get_bytes = itemgetter('bytes')
records = [{'bytes': 0}, {'bytes': 1_048_576}, {'bytes': 2_097_152}]
mebibytes = (get_bytes(row) / (1024 * 1024)
             for row in records if get_bytes(row) > 0)
total_mib = sum(mebibytes)
assert total_mib == 3.0

# A module-level function makes the partial picklable when the module is importable.
def divide_by(scale, value):
    return value / scale

to_mib = partial(divide_by, 1024 * 1024)
assert to_mib(1_048_576) == 1.0

# reduce is available, but sum is clearer for numeric addition.
assert reduce(lambda total, value: total + value, [1, 2, 3], 0) == 6
```

A generator expression streams transformed values; `sum` consumes them once. Prefer `sum` over `functools.reduce` for numeric addition and comprehensions/generator expressions when the pipeline is simple. Composition order matters: `compose(f, g)(x)` means `f(g(x))`, while a left-to-right `pipe(x, f, g)` means `g(f(x))`. Standard `pickle` generally serializes top-level functions by qualified name, not arbitrary local lambdas/nested functions; a `partial` of a lambda generally remains unpicklable. Use a module-level callable or a deliberate serialization format for durable jobs. Do not imply that every callable can be pickled.

## Answer 6 — Q06

`tee` creates independent iterators by buffering values consumed by the faster branch until the slower branch catches up. If `left` consumes the entire source before `right` starts, the buffer can grow to `O(n)`, defeating streaming's memory advantage. If both actions can happen together, use one loop:

```python
for item in huge_stream:
    process(item)
    audit(item)
```

If consumers must be independently scheduled, use an explicitly bounded queue with backpressure or persist/replay the stream. `tee` is appropriate only when lag and buffering are bounded/acceptable.

## Answer 7 — Q07

There are `8 × 6 × 5 = 240` combinations:

```python
from itertools import product
for backend, serialization, compression in product(backends, formats, compressions):
    run_case(backend, serialization, compression)
```

`product` yields combinations lazily, so it need not hold all 240 tuples at once. But it still produces 240 cases; if dimensions grow, runtime and total work grow multiplicatively. Validate dimensions and consider representative or pairwise coverage for very large grids.

## Answer 8 — Q08

One acceptable implementation for a local filesystem is:

```python
import os
import tempfile
from pathlib import Path

def write_atomically(destination: str | Path, data: bytes) -> None:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='wb', dir=destination.parent,
            prefix=f'.{destination.name}.', delete=False,
        ) as stream:
            temp_name = stream.name
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())  # stronger durability request on supported filesystems
        os.replace(temp_name, destination)
        temp_name = None
        # For crash durability of the directory entry, some POSIX systems also require
        # opening/fsyncing the parent directory; this is platform/filesystem-specific.
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
```

Creating the temp file in the destination directory helps keep `os.replace` on the same filesystem. Replacement is atomic under the relevant filesystem semantics, but atomic visibility is not the same as durable persistence after power loss. Directory fsync and guarantees differ by OS/filesystem. `shutil.copyfile` copies file contents, `copy` also attempts to preserve permission mode, and `copy2` attempts to preserve additional metadata; platform support and metadata fidelity vary, so none is automatically a complete backup/metadata-preservation strategy. Permissions, ownership, symlink policy, and metadata preservation may need explicit handling for production use.

## Answer 9 — Q09

Archive members can contain traversal-like names such as `../../outside.txt`. Current `zipfile` extraction helpers sanitize some path components, but that behavior is not a substitute for an application policy: collisions, overwrites, symlink/platform behavior, and decompression resource exhaustion still require decisions. Extract into a new private staging directory; inspect every member and resolved destination; reject absolute/parent-traversal names, unexpected link/device entries where relevant, duplicate/colliding normalized paths, excessive member counts, individual sizes, and total expanded bytes; enforce a time/disk budget; then promote only the validated staging tree. Use a well-reviewed extraction policy and version-aware `tarfile` filters for TAR archives. Do not rely on a successful open or string-prefix checks (`/safe/outside` can share a prefix with `/safe/outside-evil`). Tests should include traversal-like names and size-limit violations without writing outside a temporary root.

## Answer 10 — Q10

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix='ingest-') as tmp:
    path = Path(tmp) / 'input.txt'
    path.write_text('sample', encoding='utf-8')
    assert path.read_text(encoding='utf-8') == 'sample'
# directory cleanup occurs on context exit, including exceptional exits
```

`mktemp` only returns a name and does not securely create the file; a race can let another process claim the name. Use `NamedTemporaryFile` or `TemporaryDirectory` to create resources atomically and manage their lifetime. On Windows, open-file semantics can affect whether a temp file can be reopened or removed; design for the target OS.

## Answer 11 — Q11

The interpolated shell command lets `user_pattern` or `filename` alter shell syntax, so attacker-controlled input can execute unintended commands. Avoid the shell and pass an argument vector:

```python
import subprocess

def search(pattern: str, filename: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ['grep', '--', pattern, filename],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=2.0,
    )
    # grep uses 0 = matches, 1 = no matches, >1 = an error.
    if result.returncode not in (0, 1):
        raise subprocess.CalledProcessError(
            result.returncode, result.args, output=result.stdout, stderr=result.stderr
        )
    return result
```

This assumes a Unix-like environment with `grep` available and `--` supported; for a portable implementation, use Python's own file-reading/search logic or declare the executable dependency and control its path. `TimeoutExpired` indicates a timeout; `CalledProcessError` is raised above for an actual grep error, not the normal “no match” result. `FileNotFoundError`/other `OSError` indicates launch failure. `shell=False` prevents shell parsing but does not make an untrusted executable path or every target-program option safe. Validate domain-specific arguments and apply least privilege. A timeout on `run` handles the direct child, not necessarily an arbitrary descendant tree.

## Answer 12 — Q12

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-c', 'print("ok")'],
    capture_output=True, text=True, timeout=2, check=True,
)
assert result.stdout == 'ok\n'
assert result.returncode == 0
```

`TimeoutExpired` means the deadline elapsed; `CalledProcessError` means `check=True` observed a non-zero exit status; `OSError` subclasses such as `FileNotFoundError` indicate launch failure. Use `Popen` when streaming output, interacting over stdin, or coordinating a long-running child is needed. Process-tree cleanup is platform-specific (for example, process groups on POSIX or job objects on Windows); do not claim that a direct-child timeout always terminates descendants.

## Answer 13 — Q13

```python
import sqlite3

def insert_event(con: sqlite3.Connection, event_id: str, status: str) -> None:
    with con:
        con.execute(
            'INSERT INTO events(event_id, status) VALUES (?, ?)',
            (event_id, status),
        )
```

The table needs a `UNIQUE` or primary-key constraint on `event_id`. Parameters keep values separate from SQL syntax and prevent injection through values. A strict insert makes duplicates visible as `sqlite3.IntegrityError`; an idempotent loader may use `ON CONFLICT(event_id) DO NOTHING` or `DO UPDATE`, chosen according to the required semantics. `with con:` commits on successful exit and rolls back on exception; it does not close the connection.

## Answer 14 — Q14

```python
rows = connection.execute(
    'SELECT * FROM users WHERE username = ?', (username,)
).fetchall()
```

The f-string lets input change the SQL grammar. Parameter binding treats the username as a value, even if it contains a quote. Test with a string like `alice' OR '1'='1` and assert the query returns only the row whose username exactly matches that string (or no rows if none exists), not all users. Manual escaping is dialect-sensitive and easy to get wrong; identifiers such as table names generally cannot be supplied as ordinary value parameters and should come from a strict allow-list.

## Answer 15 — Q15

WAL lets readers usually proceed while a writer appends to the write-ahead log, improving reader/writer concurrency. It does not make SQLite a multi-writer database; writers still serialize, checkpoints matter, and locking can still occur. Set a busy timeout and implement bounded retry with jitter/backoff only for known transient lock errors. Ensure the operation is transactional and idempotent before retrying; do not repeat external side effects as part of a database retry. Add an index only when query plans/workload justify it: indexes can reduce lookup cost but consume storage and add write/update overhead. WAL suitability also depends on filesystem and deployment topology.

## Answer 16 — Q16

A robust design stores a stable file identity/hash in an ingestion table with a unique constraint, and writes the identity plus all rows in one transaction. For example, compute SHA-256 while reading the file, then in a transaction insert the hash with a uniqueness constraint and upsert rows keyed by natural/business keys. If the hash is already committed, skip the file; if the transaction fails, both the marker and rows roll back. Same path can refer to changed contents; same content at different paths may intentionally be deduplicated by content hash. Define whether metadata/path are part of identity. For very large inputs, avoid a two-pass read unless necessary; stage the rows or compute the digest while streaming.

## Answer 17 — Q17

Use a private staging directory and reject unsafe names/absolute paths, `..`, unexpected symbolic/hard links, device/FIFO entries, and duplicate or colliding normalized destinations. Bound member count, per-member size, total expanded size, compression ratio, elapsed time, and disk usage. Validate actual extracted sizes as well as metadata; archive metadata is untrusted. Extract under a restrictive policy, verify expected outputs, then atomically rename/promote the staging directory where filesystem semantics allow. Apply cleanup on every failure. `tarfile` extraction filters/defaults changed across Python versions, so explicitly select and test the intended policy on the supported baseline.

## Answer 18 — Q18

`run(check=True)` raises `CalledProcessError` on non-zero exit; `check=False` returns a `CompletedProcess` and leaves interpretation to the caller. `Popen` is justified for streaming, interactive pipes, asynchronous waiting, or explicit process lifecycle control. `TimeoutExpired` represents timeout; `CalledProcessError` represents a non-zero status with `check=True`; `OSError`/`FileNotFoundError` represents launch failure. Always drain or redirect pipes to avoid deadlocks, and define timeout cleanup behavior for descendants.

## Answer 19 — Q19

Use `tmp_path` for isolated files and a temporary SQLite database. Test successful processing, empty input, malformed input, subprocess non-zero exit, timeout, database rollback, duplicate/idempotent rerun, and cleanup after failure. Use a real local subprocess with `sys.executable` for basic integration, but inject the command runner to test controlled timeout/non-zero cases deterministically. Use mocks for failure injection and avoid external network access; use a local HTTP server when HTTP behavior itself is in scope. Do not require an installed `gzip`/`zstd` binary unless the application explicitly declares that system dependency. Assert final state and cleanup, not only that a function returned.

## Answer 20 — Q20

```python
import hashlib
import json
from pathlib import Path

def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    if chunk_size <= 0:
        raise ValueError('chunk_size must be positive')
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b''):
            digest.update(chunk)
    return digest.hexdigest()

def fingerprint_record(record: dict) -> str:
    # This policy handles JSON-compatible data and ignores dictionary key order.
    canonical = json.dumps(
        record, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
        allow_nan=False,
    ).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()
```

File hashing is `O(n)` time and `O(chunk_size)` auxiliary memory. Canonicalization must be defined for the data model: `sort_keys=True` does not normalize semantically equivalent Unicode, whitespace inside string values, decimals, or custom objects. A plain digest detects accidental changes only when the expected digest is trusted; use HMAC/signatures for authenticity. Passwords should use a password-hashing/KDF scheme with salts and appropriate work factors, such as `hashlib.scrypt` or `hashlib.pbkdf2_hmac`, or a reviewed dedicated library; one fast SHA-256 pass is too cheap against offline guessing.

## Answer 21 — Q21

```python
import hashlib
import hmac
import re

def verify(key: bytes, message: bytes, supplied_hex: str) -> bool:
    if not isinstance(supplied_hex, str) or re.fullmatch(r'[0-9a-fA-F]{64}', supplied_hex) is None:
        return False
    supplied = bytes.fromhex(supplied_hex)
    expected = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(expected, supplied)

key, message = b'example-key', b'payload'
tag = hmac.new(key, message, hashlib.sha256).hexdigest()
assert verify(key, message, tag)
assert not verify(key, message, 'not-hex')
assert not verify(key, message, '00')
```

HMAC authenticates message bytes for parties sharing the secret; it does not encrypt the message or automatically prevent replay. `sha256(key + message)` is not a safe substitute because ad hoc constructions can have structural weaknesses, including length-extension issues for Merkle–Damgård hashes. Sign exactly defined/canonical bytes. If a signed request can be replayed, the protocol may need a timestamp, nonce, expiry window, and server-side replay tracking. Rotate and protect keys.

## Answer 22 — Q22

```python
import secrets
reset_token = secrets.token_urlsafe(32)
```

`random` is designed for simulations and reproducible pseudo-random sequences, not adversarial unpredictability. `secrets` draws from the operating system's cryptographically strong source. A fixed or predictable seed enables prediction and must not be used to protect account recovery or authentication. Define token expiry, single-use semantics, storage (prefer a digest when appropriate), and rate limiting as part of the full design.

## Answer 23 — Q23

- **Random identifier:** `uuid.uuid4()` is available in Python 3.12.
- **Deterministic namespace/name ID:** `uuid.uuid5(namespace, canonical_name)` is suitable when the same namespace and name must yield the same ID; UUIDv3 uses MD5 for legacy deterministic IDs, but v5 is generally the preferable choice.
- **Roughly time-ordered ID:** UUIDv7 is standardized and available through the standard `uuid` module starting in Python 3.14, not Python 3.12. Do not call `uuid.uuid7()` on a 3.12 baseline without a compatibility layer.

Define canonical names before `uuid5` (normalization, case rules, separators, and versioning). A UUID is an identifier, not a bearer credential or authorization decision. Enforce uniqueness in the database where required; random collisions are extremely unlikely, not logically impossible. Time/node-based UUID variants can expose timing or node information and should be selected deliberately.

## Answer 24 — Q24

```python
import random

a = random.Random(2026)
b = random.Random(2026)
assert a.sample(range(100), 5) == b.sample(range(100), 5)

def reservoir_sample(iterable, k, *, rng=None):
    if k < 0:
        raise ValueError('k must be non-negative')
    rng = rng if rng is not None else random.Random()
    reservoir = []
    for index, item in enumerate(iterable):
        if index < k:
            reservoir.append(item)
        elif k:
            slot = rng.randrange(index + 1)
            if slot < k:
                reservoir[slot] = item
    return reservoir

assert reservoir_sample(range(5), 0, rng=random.Random(1)) == []
assert len(reservoir_sample(range(1000), 7, rng=random.Random(1))) == 7
```

Algorithm R uses `O(k)` memory and `O(n)` time. Each item has equal final inclusion probability when the algorithm is implemented correctly. `k == 0` returns an empty sample; `k > n` returns all `n` items. A dedicated generator isolates random state, while a recorded seed and algorithm/runtime context improve reproducibility. `random` is deterministic pseudorandom generation, not a cryptographic source; use `secrets` for tokens.

## Answer 25 — Q25

```python
import statistics as st
values = [2, 4, 4, 10]
assert st.mean(values) == 5
assert st.median(values) == 4
assert st.mode(values) == 4
assert st.pstdev([1, 3]) == 1.0
assert st.stdev([1, 3]) == 2 ** 0.5
```

`pstdev` treats the supplied data as the entire population; `stdev` estimates spread from a sample and uses the `n - 1` denominator. Empty inputs should be rejected or represented explicitly by application policy rather than silently interpreted; statistics functions commonly raise `StatisticsError` for undefined operations. `multimode` can report all modes. A Monte Carlo estimate should define the random model, number of trials, seed, estimator, and uncertainty/variation; repeatability is not proof that the estimate equals the exact quantity.

## Answer 26 — Q26

Use a strict wire format and compare bytes of the expected representation:

```python
import hashlib
import hmac
import re

def verify_hex_tag(key: bytes, message: bytes, supplied: str) -> bool:
    if not isinstance(supplied, str) or re.fullmatch(r'[0-9a-fA-F]{64}', supplied) is None:
        return False
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied.lower())
```

The regex validates exactly 32-byte SHA-256 HMAC encoded as 64 hexadecimal characters. `compare_digest` avoids the ordinary content-dependent short-circuit behavior for supported values, but surrounding parsing, network handling, and error paths also need review. This does not protect a compromised key, a weak or improvised algorithm, inconsistent canonicalization, or replay. Use key rotation, protocol versioning, and freshness controls as appropriate.

## Answer 27 — Q27

A common precedence is **defaults < TOML file < environment variables < CLI arguments**, with later sources overriding earlier ones. Parse TOML with `tomllib` (Python 3.11+) and validate the resulting mapping before use. Convert env/CLI strings deliberately and reject invalid values. For a timeout:

```python
import math

def validate_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError('timeout must be numeric')
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError('timeout must be finite and positive')
    return result
```

`tomllib` is read-only. Define whether unknown keys are rejected or logged; silent misspellings can make operators believe a setting took effect when it did not. Keep secrets out of checked-in configuration files.

## Answer 28 — Q28

`ConfigParser` exposes values as strings unless typed accessors are used:

```python
import configparser

config = configparser.ConfigParser()
config.read('service.ini', encoding='utf-8')
retries = config.getint('service', 'retries')
timeout = config.getfloat('service', 'timeout')
base_url = config.get('service', 'base_url')
```

Interpolation can substitute `%(name)s` references, and an unescaped `%` can cause parsing/interpolation errors. Use `ConfigParser(interpolation=None)` when interpolation is not desired, or follow its documented escaping rules. Validate ranges, URL schemes/hosts, required keys, and unknown keys after parsing. Parsing a number is not the same as validating it is safe and meaningful.

## Answer 29 — Q29

Do not disable certificate verification to silence the error. Inspect the certificate chain, hostname, system CA store, clock, proxy interception, and server configuration. If a private CA is intended, configure an `ssl.SSLContext` with the correct trusted CA bundle while retaining hostname and certificate validation. An unverified context permits an active attacker to impersonate the server and read or modify traffic. Tests can use a local test CA; production code should not include a blanket verification bypass.

## Answer 30 — Q30

```python
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

def get_json(url: str, *, timeout: float = 3.0, max_bytes: int = 1_000_000):
    if timeout <= 0 or max_bytes <= 0:
        raise ValueError('timeout and max_bytes must be positive')
    request = Request(url, headers={'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                raise ValueError(f'unexpected HTTP status: {response.status}')
            raw = response.read(max_bytes + 1)
    except HTTPError as exc:
        raise RuntimeError(f'HTTP error: {exc.code}') from exc
    except URLError as exc:
        raise RuntimeError(f'URL/network error: {exc.reason}') from exc
    if len(raw) > max_bytes:
        raise ValueError('response exceeds size limit')
    try:
        return json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('response is not valid UTF-8 JSON') from exc
```

`HTTPError` is a subclass of `URLError` and represents an HTTP response error; catch it first if the status matters. This reads at most `max_bytes + 1` body bytes, not an unlimited response. It is not a complete SSRF defense: validate scheme and destination policy, account for redirects and DNS changes, and prefer an allow-list for user-influenced server-side fetches. `urlopen` timeouts apply to blocking operations, not necessarily a strict overall deadline across DNS, redirects, retries, and processing. Build query strings with `urlencode` rather than string concatenation; `quote` percent-encodes a component, while `urljoin` resolves a reference against a base and can replace the base host if the reference is absolute. Validate before joining when input is untrusted.

For tests, start `ThreadingHTTPServer(('127.0.0.1', 0), Handler)` in a thread, read its assigned port, and in a `finally` block call `shutdown()`, `server_close()`, and `thread.join()`. Test a success response, an HTTP error, malformed JSON, and the size limit without external network access. `http.server` is for controlled tests/demos, not a hardened production server.

## Answer 31 — Q31

```python
import struct

def recv_exact(sock, n: int) -> bytes:
    if n < 0:
        raise ValueError('negative length')
    chunks = bytearray()
    while len(chunks) < n:
        part = sock.recv(n - len(chunks))
        if not part:
            raise EOFError('peer closed before frame was complete')
        chunks.extend(part)
    return bytes(chunks)

def recv_frame(sock, max_payload: int = 1_048_576) -> bytes:
    (length,) = struct.unpack('!I', recv_exact(sock, 4))
    if length > max_payload:
        raise ValueError('frame too large')
    return recv_exact(sock, length)
```

TCP is a byte stream, not a message protocol. `recv(n)` may return fewer than `n` bytes even when the peer has more data to send. Check the length cap before reading/allocating the payload. Also enforce timeouts, connection limits, and protocol error handling in production.

## Answer 32 — Q32

```python
from contextlib import contextmanager
from contextvars import ContextVar, copy_context
from concurrent.futures import ThreadPoolExecutor

request_id: ContextVar[str | None] = ContextVar('request_id', default=None)

@contextmanager
def request_scope(value: str):
    token = request_id.set(value)
    try:
        yield
    finally:
        request_id.reset(token)

with request_scope('outer'):
    assert request_id.get() == 'outer'
    with request_scope('inner'):
        assert request_id.get() == 'inner'
    assert request_id.get() == 'outer'
assert request_id.get() is None

with request_scope('worker-7'):
    ctx = copy_context()
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert pool.submit(ctx.run, request_id.get).result() == 'worker-7'
```

Tokens restore the prior value, including nested values. A token must be reset in the context where it was created and only once. Asyncio tasks inherit a context snapshot when created; `asyncio.to_thread()` propagates the current context, while arbitrary `ThreadPoolExecutor.submit()` work should not be assumed to do so—use a fresh `copy_context()` per submission. Do not reuse one `Context` concurrently across threads. Python 3.14 adds `threading.Thread(context=...)`; that option is not part of Python 3.12/3.13. Context variables isolate bindings, not mutations to a shared mutable object stored as their value. Free-threaded builds available experimentally in Python 3.13 and with evolving support in 3.14 do not make arbitrary shared-state access automatically safe; use documented thread-safe APIs and explicit synchronization where shared mutation requires it.

## Answer 33 — Q33

- `WeakValueDictionary`: keys are held strongly; values must be weak-referenceable and can disappear when no other strong reference keeps them alive.
- `WeakKeyDictionary`: values are strong; keys must be weak-referenceable. Be careful when equality/hash semantics make distinct keys compare equal.
- `WeakSet`: weakly holds weak-referenceable members.

Many built-ins such as `int`, `str`, `list`, and `dict` cannot be weak-referenced directly (some user-defined subclasses can support it). A bound method normally keeps its instance alive through `self`; an observer can store `weakref.WeakMethod(method)` and remove dead subscriptions. A strong callback or closure can still capture and retain an observer. `WeakKeyDictionary` values are strong: if a stored value itself refers back to its weak key, that value-to-key path can keep the key alive and defeat the intended weak-key behavior.

`lru_cache` retains keys and results strongly until eviction or `cache_clear()`, so decorating an instance method can retain `self` through the cache key. `weakref.finalize(obj, callback, ...)` is often easier to reason about than `__del__`, but the callback and its arguments must not strongly retain `obj`; finalization timing and interpreter shutdown ordering are not a substitute for explicit resource management (`with`, `close`). `__del__` can complicate cycles and shutdown.

A lifecycle test can create an object, keep only `weakref.ref(obj)`, delete the strong reference, call `gc.collect()`, and assert the weak reference is dead on the tested CPython runtime. If it remains alive, inspect all other references; do not interpret one `gc.collect()` result as a universal timing guarantee. `tracemalloc` snapshots can help find allocation growth but do not by themselves prove a leak's cause.

## Answer 34 — Q34

```python
import copy
shared = []
source = {'left': shared, 'right': shared}
source['self'] = source
shallow = copy.copy(source)
deep = copy.deepcopy(source)
source['left'].append('changed')

assert shallow['left'] == ['changed']
assert shallow['left'] is source['left']
assert deep['left'] == []
assert deep['left'] is deep['right']
assert deep['self'] is deep
assert shallow['self'] is source
```

A shallow copy creates a new outer mapping but reuses nested references. `deepcopy` uses a memo dictionary keyed by object identity to avoid infinite recursion through cycles and to preserve repeated-reference relationships in the copied graph. A custom `__deepcopy__(memo)` should consult/populate the memo correctly before recursively copying fields. External resources such as open files, sockets, locks, database connections, and clients have ownership/lifecycle semantics; they should generally be shared intentionally, recreated, or explicitly excluded—not blindly duplicated.

## Answer 35 — Q35

A strong answer separates orchestration from adapters and makes the failure policy explicit:

1. **Config:** defaults → TOML → environment → CLI; parse TOML in binary mode; validate schema, types, finite positive timeouts, URL allow-lists, and unknown keys; do not log secrets.
2. **Fetch:** `urllib` with per-operation timeout and bounded response reads; controlled redirects and destination policy; retry only transient, idempotent failures with bounded backoff; write into a private temporary directory.
3. **Integrity:** hash bytes incrementally with SHA-256 and compare to a trusted manifest; reject mismatch before parsing. A digest is not authentication if the manifest is attacker-controlled.
4. **Transform:** stream CSV rows; validate/normalize according to a declared schema; use `itertools.batched`; count accepted/rejected rows without retaining the entire source.
5. **SQLite:** parameterized SQL, unique constraints, stable idempotency key, and a transaction whose boundary covers both the processed-file marker and corresponding row changes. Avoid retrying external side effects as part of a database transaction retry.
6. **Archive/output:** stage files privately, bound size, validate names before any extraction, write final archive to a temporary path, then replace the destination; distinguish atomic replacement from crash durability.
7. **Subprocess:** argument list with `shell=False`, explicit executable path where practical, timeout, captured/limited output, return-code checking, and documented process-tree cleanup limitations. Declare external compressor as an operational dependency.
8. **Context/logging:** set a run ID with a token and reset in `finally`; pass context explicitly to executor work when needed; redact credentials and sensitive payloads.
9. **Tests:** use `tmp_path`, temporary SQLite, deterministic inputs, and a local `ThreadingHTTPServer`; inject subprocess runners for timeout/non-zero cases.

At minimum, acceptance tests should cover: valid fetch/hash; hash mismatch; response-size limit; malformed CSV policy; idempotent rerun; database rollback; subprocess non-zero and timeout; unsafe archive path rejection; context reset after exceptions; and cleanup of temporary artifacts. The roadmap mini-project target is at least 90% line coverage, measured with a declared test tool such as `pytest-cov`; also require clean `ruff` and type-checker runs plus a README/runbook. These are development-tool requirements, not runtime dependencies. Coverage and static checks are useful signals, not proof that security and failure cases are correct.

### Integrated challenge model guidance

- **Challenge A:** use a generator pipeline and `batched`; do not call `list(source)`; consume each `groupby` group before advancing; isolate sampling with `random.Random(seed)`; test empty/partial batches and upstream exceptions.
- **Challenge B:** compute a digest incrementally, use a unique constraint and parameterized SQL, stage output with `NamedTemporaryFile` in the target directory, `os.replace` only after successful completion, and clean the temp path in `finally`. Verify rollback and duplicate rerun behavior.
- **Challenge C:** validate effective config before network I/O; use a local server on a free loopback port; always `shutdown`, `server_close`, and `join`; use `ContextVar` token reset; use `asyncio.to_thread` for its documented propagation or `copy_context().run` for explicit executor propagation. Keep certificate verification enabled.

# Scoring rubric

- **2-point questions:** 1 point for the core answer/output and 1 point for causal reasoning or the key edge case.
- **3-point implementation/debugging questions:** 1 point for correctness; 1 point for constraints/error handling; 1 point for trade-offs, tests, or operational limits.
- **Advanced security/design questions:** award points for identifying the real failure mode, proposing a safe technically correct design, and addressing edge cases/testing/operational limits. The difficulty label does not change the stated point value.
- For code-writing tasks, syntax errors that prevent execution normally lose the correctness point; minor style issues do not. A dangerous security shortcut caps the question at 1 point even if the happy path works.
- For open-ended design, equivalent solutions earn full credit if they satisfy explicit constraints and state assumptions. Do not require a particular implementation detail that the question does not specify.

## Final self-audit checklist

- [ ] Every question ID Q01–Q35 is unique and has one corresponding answer.
- [ ] Every lesson 01–10 is represented and all four phases are covered.
- [ ] Six security-bug questions are present: archive extraction, shell injection, SQL injection, insecure token generation, signature comparison, and TLS verification.
- [ ] Answers use parameterized SQL, argument-list subprocess execution, `secrets` for tokens, HMAC verification, bounded input processing, and explicit network timeouts.
- [ ] Python 3.12+ is the baseline; `itertools.batched` and `tomllib` are versioned correctly.
- [ ] Code examples avoid external network calls and dangerous payload execution.
- [ ] Open-ended challenges have acceptance tests and explicit trade-offs.

