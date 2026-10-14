# Roadmap — Module 1.13: Standard Library Toolkit

This is the learning roadmap for the thirteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
from the Python standard library, **in what order**, **how** to practise
each topic, and **how to prove to yourself** that you have learned it.

"Batteries included" is one of Python's biggest strengths. Before adding a
dependency, a senior engineer asks: *does the standard library already do
this, safely, with no install and no supply-chain risk?* Data engineers and
AI engineers use `itertools`, `shutil`, `tempfile`, `subprocess`, `sqlite3`,
`hashlib`, `uuid`, `random`, `statistics`, `tomllib` and `urllib` every week —
for ingestion scripts, deterministic sampling, test fixtures, file hashing,
local caches, config loading and tooling glue.

Modules 1.5, 1.9 and 1.10 already taught `pathlib`, `csv`, `json`, `argparse`,
`logging`, `datetime`, `collections` and `functools`. This module **does not
repeat them**; it covers the remaining high-value modules.

> Target version: **Python 3.12+**; notes on 3.13/3.14 are flagged inline.

---

## 1. Module outcome

By the end of this module you will be able to:

- Build lazy data pipelines with `itertools` and `operator`, using the standard recipes.
- Move, copy, archive and clean files safely with `shutil`, `tempfile`, `zipfile` and `tarfile`.
- Run external programs with `subprocess` safely (no shell injection, with timeouts, exit-code checks and captured output).
- Use `sqlite3` as an embedded database with parameterised queries, transactions, row factories and sensible pragmas.
- Hash files, sign messages and generate tokens correctly with `hashlib`, `hmac`, `secrets` and `uuid`.
- Use `random` reproducibly and `statistics` for quick descriptive analysis, and know when to move to NumPy.
- Load configuration with `tomllib` and `configparser`.
- Make HTTP requests with `urllib`, understand sockets and start a throwaway HTTP server for tests.
- Use `weakref`, `contextvars` and `copy` correctly.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Iterators and generators | Module 1.9 (01, 04) | `itertools` is lazy iteration |
| Higher-order functions, `functools` | Modules 1.8 (06), 1.9 (09), 1.24 (05) | `operator` and composition |
| Files, `pathlib`, encodings | Module 1.5 (01–05) | `shutil`, `tempfile`, archives |
| Exit codes, standard streams | Module 1.5 (07) | `subprocess` |
| Environment variables, config | Modules 1.5 (09), 1.10 (01) | `tomllib`, `configparser` |
| Safe file writes, idempotency | Module 1.10 (04, 05) | Atomic moves and temp files |
| Mutability, copying | Modules 1.2 (05, 10), 1.11 (11) | `copy`, `weakref` |
| Testing with pytest | Module 1.7 | `tmp_path`, mocks around `subprocess` |

**Tools:** Python 3.12+, `uv`, `pytest`, `ruff`; a Unix-like shell
(WSL2/Linux/macOS) for the `subprocess` exercises.

---

## 3. How the module is organised

```text
Phase A — Iteration and Functional Tools           (Basics)
  01 itertools and iteration recipes
  02 operator and functional composition
Phase B — Files, Processes and Local Data          (Intermediate)
  03 shutil, tempfile, zipfile, tarfile
  04 subprocess
  05 sqlite3
Phase C — Security Primitives and Numbers          (Intermediate)
  06 hashlib, hmac, secrets, uuid
  07 random and statistics
Phase D — Config, Network and Runtime Utilities    (Advanced)
  08 tomllib and configparser
  09 urllib, sockets, http.server
  10 weakref, contextvars, copy
```

Pace: about 3 weeks part-time. Each lesson ends with a tested script.

---

## Lesson 01 — `01-itertools-and-iteration-recipes.md`

**Why it matters.** `itertools` provides fast, memory-efficient building
blocks for streaming data: chunking records, merging streams, windowing,
grouping, cartesian products for test grids. It is the vocabulary of
lazy pipelines.

### Basic — what to learn

- Infinite iterators: `count`, `cycle`, `repeat`.
- Finite: `chain`, `chain.from_iterable`, `islice`, `zip_longest`,
  `accumulate`, `compress`, `takewhile`, `dropwhile`, `filterfalse`, `starmap`.
- Iterators are **single-use**: once exhausted they are empty.

```python
from itertools import islice, chain, count, accumulate

print(list(islice(count(10, 5), 4)))              # [10, 15, 20, 25]
print(list(chain([1, 2], (3,), "ab")))            # [1, 2, 3, 'a', 'b']
print(list(accumulate([1, 2, 3, 4])))             # [1, 3, 6, 10]
```

### Intermediate — what to learn

- Combinatorics: `product`, `permutations`, `combinations`,
  `combinations_with_replacement` — parameter grids for experiments.
- `groupby(iterable, key)`: groups **consecutive** items, so sort first;
  groups are lazy iterators that become invalid when you advance.
- `tee` (and why it buffers), `pairwise` (3.10+), `batched` (3.12+).
- Chunking a large file or API result set with `batched`.
- Combining `islice` with generators for "first N" and pagination.

```python
from itertools import groupby, batched, pairwise, product
from operator import itemgetter

rows = sorted([{"k": "a", "v": 1}, {"k": "b", "v": 2}, {"k": "a", "v": 3}],
              key=itemgetter("k"))
for key, grp in groupby(rows, key=itemgetter("k")):
    print(key, [r["v"] for r in grp])

print(list(batched(range(7), 3)))                 # [(0,1,2),(3,4,5),(6,)]
print(list(pairwise([1, 4, 9])))                  # [(1,4),(4,9)]
grid = list(product([0.1, 0.01], [16, 32]))       # hyper-parameter grid
```

### Advanced — what to learn

- The **itertools recipes** (docs): `take`, `nth`, `flatten`, `unique_everseen`,
  `sliding_window`, `roundrobin`, `partition`, `powerset` — implement and test them.
- Memory behaviour: what is materialised, what streams; avoiding `list(...)`
  on huge iterables; `tee` memory growth when consumers diverge.
- `more-itertools` as the next step (awareness): when a third-party helper is justified.
- Building a streaming ETL pipeline: read lines → parse → filter → batch →
  write, all lazy, with constant memory; measure with `tracemalloc`.
- Pitfalls: `groupby` without sorting, reusing exhausted iterators, late binding in
  generator expressions, `zip` truncation vs `zip(strict=True)` (3.10+).
- Performance: C-implemented `itertools` vs Python loops; when readability beats cleverness.

### Common mistakes

- Using `groupby` on unsorted data.
- Consuming `tee` copies unevenly.
- Replacing a clear loop by an unreadable chain.

### Self-check

1. Why does `groupby` need sorted input?
2. Implement `sliding_window(iterable, n)` using `islice` and `deque`.
3. Which function chunks an iterable into tuples of fixed size in 3.12+?

---

## Lesson 02 — `02-operator-and-functional-composition.md`

**Why it matters.** `operator` turns operators into functions, so you can
pass `+`, `itemgetter` or `attrgetter` as arguments instead of writing
lambdas. Faster, clearer, picklable, and the foundation of key functions.

### Basic — what to learn

- `operator.add`, `mul`, `eq`, `lt`, `not_`, `contains`, `getitem`.
- `itemgetter(key[, key...])` and `attrgetter("a.b")` for `sorted`, `max`,
  `groupby`, `map`.
- `methodcaller("strip")`.

```python
from operator import itemgetter, attrgetter, methodcaller
people = [("ana", 31), ("bo", 25), ("cy", 31)]
print(sorted(people, key=itemgetter(1, 0)))        # by age, then name
print(list(map(methodcaller("upper"), ["a", "b"])))
```

### Intermediate — what to learn

- `functools.reduce` with `operator.mul`/`add`; when `sum`, `math.prod`,
  `any`, `all` are clearer.
- Function composition: a hand-written `compose(*fns)` and `pipe(value, *fns)`;
  `functools.partial` to fix arguments.
- In-place operators (`iadd`) and the difference from `add` on mutable vs
  immutable types.
- `operator.index`, `length_hint`, `call` (3.11+).
- Building multi-key sorts: sort by several keys with mixed ascending/descending
  using stable sort twice or key transforms.

```python
from functools import reduce, partial
import math

def compose(*fns):
    return reduce(lambda f, g: lambda x: g(f(x)), fns)

clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "_"))
print(clean("  Hello World "))        # hello_world
```

### Advanced — what to learn

- Point-free style: benefits and limits for readability.
- Performance comparison of `lambda`, `itemgetter`, and comprehension on 10⁶ items
  with `timeit`.
- Operator functions with NumPy/pandas objects (they dispatch to `__add__`, so
  work for arrays too).
- Typing function pipelines (`Callable`, `ParamSpec`) and keeping them checkable.
- Pickling: `itemgetter` and `partial` are picklable; lambdas are not — matters for
  `multiprocessing`.
- Designing a small transformation pipeline library from composable pure functions.

### Common mistakes

- `reduce` for things `sum`/`any` already do.
- Composition order confusion (left-to-right vs right-to-left).
- Over-clever point-free code.

### Self-check

1. Sort a list of dicts by `("dept", -salary)` without lambdas.
2. Why can `itemgetter` be sent to a process pool but a lambda cannot?
3. Write `pipe(value, *fns)` and test it.

---

## Lesson 03 — `03-shutil-tempfile-zipfile-and-tarfile.md`

**Why it matters.** Data jobs move, copy, archive, unpack and clean up
files constantly. Doing it incorrectly causes partial files, leaked temp
data, path-traversal vulnerabilities and disk-full surprises.

### Basic — what to learn

- `shutil.copy`, `copy2` (metadata), `copyfile`, `copytree`, `move`, `rmtree`,
  `disk_usage`, `which`, `make_archive`, `unpack_archive`.
- `tempfile.TemporaryDirectory()`, `NamedTemporaryFile`, `mkstemp`, `mkdtemp`;
  automatic cleanup with context managers.
- `zipfile.ZipFile` read/write/list; `tarfile.open("r:gz")`.

```python
import tempfile, shutil
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp, "a.txt"); src.write_text("hi")
    shutil.copy2(src, Path(tmp, "b.txt"))
    print(sorted(p.name for p in Path(tmp).iterdir()))
```

### Intermediate — what to learn

- **Atomic writes**: write to a temp file in the *same directory/filesystem*,
  `flush` + `os.fsync`, then `os.replace` (ties to Module 1.10 lesson 05).
- `shutil.copytree(..., dirs_exist_ok=True, ignore=shutil.ignore_patterns(...))`.
- `shutil.move` across filesystems = copy + delete (not atomic).
- Reading files in a zip/tar **streamingly** (`ZipFile.open`) without extracting.
- Compression levels, `ZIP_DEFLATED`, tar `w:gz`/`w:xz`/`w:zst` (zstd in tar from 3.14 via `compression.zstd`).
- Cleaning up on failure: `try/finally`, `contextlib.ExitStack`, `pytest tmp_path`.

```python
import os, tempfile
from pathlib import Path

def atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp); raise
```

### Advanced — what to learn

- **Archive extraction security**: zip-slip / path traversal; `tarfile`
  `extraction_filter` (`filter="data"`, default in 3.14), symlink and device-file
  attacks; validating member paths before extraction.
- Zip bombs: check `file_size` and compression ratio; extract with limits.
- `tempfile` security: `mktemp` is unsafe (race); permissions `0o600`; temp dir location (`TMPDIR`).
- Large-file strategies: `shutil.copyfileobj` with buffer size, `os.sendfile`,
  progress reporting, resumable copies, checksums after copy.
- Cross-platform issues: Windows file locking, long paths, case-insensitive filesystems.
- Testing file code: `tmp_path`, never touching real directories.

### Common mistakes

- Writing temp files on a different filesystem than the target, then `os.replace` fails.
- `extractall` on untrusted archives.
- Leaving temp files behind after exceptions.

### Self-check

1. Why must the temp file be in the same directory as the target for an atomic replace?
2. How would you detect a zip-slip entry like `../../etc/passwd`?
3. Write `safe_extract(zip_path, dest)` with size and path limits, plus a test with a malicious zip.

---

## Lesson 04 — `04-subprocess-and-running-external-commands-safely.md`

**Why it matters.** Pipelines call `git`, `ffmpeg`, `psql`, `docker`,
`pdftotext`, `kubectl`. `subprocess` is the correct tool — and `shell=True`
with user input is a classic remote-code-execution bug.

### Basic — what to learn

- `subprocess.run([...], check=True, capture_output=True, text=True)`.
- `CompletedProcess`: `returncode`, `stdout`, `stderr`; `CalledProcessError`.
- Pass arguments as a **list**; avoid building command strings.

```python
import subprocess
r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                   text=True, check=True, timeout=10)
print(r.stdout.strip())
```

### Intermediate — what to learn

- `timeout=` and `TimeoutExpired` (the child is killed; `communicate` semantics).
- `cwd=`, `env=` (copy `os.environ` then modify), `input=` for stdin.
- Pipes between processes: `Popen(stdout=PIPE)` chained; deadlocks when both
  stdout and stderr fill the pipe buffer → use `communicate()` or threads.
- Streaming output line by line from a long-running process.
- Encoding: `text=True`, `encoding=`, `errors=`; binary mode for non-text output.
- `shlex.split` and `shlex.quote` — when you truly must build a shell string.
- Exit codes and signals: negative `returncode` = killed by signal.

```python
with subprocess.Popen(["ping", "-c", "3", "localhost"],
                      stdout=subprocess.PIPE, text=True) as p:
    for line in p.stdout:
        print("→", line.rstrip())
```

### Advanced — what to learn

- **Command injection**: demonstrate `shell=True` + user input, then fix with a
  list and allow-lists; why quoting is a last resort; PATH hijacking
  (use absolute paths for privileged tools).
- Process groups and cleanup: `start_new_session`, `os.killpg`, avoiding zombie
  and orphan processes; `terminate()` vs `kill()`.
- Resource limits (`resource` module on Unix), restricting environment, dropping
  privileges (awareness).
- `asyncio.create_subprocess_exec` for concurrent commands (preview of async modules).
- Testing code that shells out: wrap in a small function and mock it
  (`monkeypatch`), or use fake executables on `PATH` in `tmp_path`.
- Windows differences (`CREATE_NEW_PROCESS_GROUP`, quoting rules, `.cmd` files).
- Logging commands without leaking secrets in arguments.

### Common mistakes

- `shell=True` with interpolated input.
- Ignoring `returncode`, or `check=True` with no handling.
- Reading `stdout` then `stderr` sequentially and deadlocking.

### Self-check

1. Why is `subprocess.run(f"ls {user_dir}", shell=True)` dangerous? Provide an exploit string.
2. What does a `returncode` of `-9` mean?
3. Write `run_tool(args, timeout)` returning a typed result and raising a custom error with stderr.

---

## Lesson 05 — `05-sqlite3-embedded-database.md`

**Why it matters.** SQLite is the most deployed database in the world and
ships with Python. It is ideal for local caches, job state, de-duplication
keys, small catalogs, test fixtures and offline tools — and it is the best
sandbox for practising SQL before using PostgreSQL (Stage 2 covers
PostgreSQL via `psycopg`).

### Basic — what to learn

- `sqlite3.connect(path or ":memory:")`, `execute`, `executemany`, `fetchone`,
  `fetchall`, iteration over cursors.
- **Parameterised queries** (`?` placeholders): never f-string values.
- `commit()` / `rollback()` and the connection as a context manager
  (commits or rolls back — it does **not** close).

```python
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT UNIQUE)")
with con:
    con.executemany("INSERT INTO users(email) VALUES (?)",
                    [("a@x.io",), ("b@x.io",)])
print(con.execute("SELECT id, email FROM users WHERE email = ?",
                  ("a@x.io",)).fetchone())
```

### Intermediate — what to learn

- `row_factory = sqlite3.Row` for dict-like rows; custom factories.
- Types and affinity: SQLite is dynamically typed; `STRICT` tables (3.37+);
  adapters/converters and `detect_types`; storing timestamps as ISO-8601 text or UTC epoch.
- Constraints: `PRIMARY KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, `FOREIGN KEY`
  (**enable with `PRAGMA foreign_keys = ON`** per connection).
- Upserts: `INSERT ... ON CONFLICT DO UPDATE` and `INSERT OR IGNORE`.
- Indexes and `EXPLAIN QUERY PLAN`.
- Transactions: `isolation_level`, `autocommit` attribute (3.12), `BEGIN IMMEDIATE`.
- Window functions, CTEs, JSON functions (`json_extract`) available in SQLite.

```python
con.execute("PRAGMA foreign_keys = ON")
con.execute("""INSERT INTO users(email) VALUES (?)
               ON CONFLICT(email) DO UPDATE SET email = excluded.email""", ("a@x.io",))
```

### Advanced — what to learn

- **Concurrency**: `PRAGMA journal_mode = WAL`, `busy_timeout`, `synchronous`;
  one writer at a time; connection-per-thread rules (`check_same_thread`); retry on
  `database is locked`.
- Schema migration approaches with `PRAGMA user_version`; why you later adopt Alembic.
- Custom SQL functions (`create_function`), aggregates, collations.
- Performance: batch inserts in one transaction (100× faster), `executemany`, prepared statement reuse, indexes, `VACUUM`, `ANALYZE`.
- Backups with `Connection.backup()`; read-only connections via URI (`file:...?mode=ro`).
- Using SQLite as an idempotency / checkpoint store for pipelines (Module 1.10 lesson 04).
- Limits: not for high write concurrency or multi-host access; know when to move to PostgreSQL.
- SQL injection demo and the safe fix; identifier quoting for dynamic table names (allow-list).

### Common mistakes

- Forgetting `commit` and losing data, or committing per row.
- Assuming foreign keys are enforced by default.
- Sharing one connection across threads without care.

### Self-check

1. Why does `with con:` not close the connection?
2. Show how WAL mode changes reader/writer behaviour.
3. Build a `seen_ids` table that makes a batch job idempotent, with an upsert and a test.

---

## Lesson 06 — `06-hashlib-hmac-secrets-and-uuid.md`

**Why it matters.** Checksums verify downloads, stable hashes de-duplicate
records, HMACs authenticate webhooks, `secrets` creates tokens, and UUIDs
identify entities. Using the wrong primitive (e.g. `random` for tokens,
`md5` for passwords) is a real security flaw.

### Basic — what to learn

- `hashlib.sha256(data).hexdigest()`; `md5`/`sha1` are broken for security
  but fine for non-adversarial checksums.
- Hash a file in chunks (constant memory); `hashlib.file_digest` (3.11+).
- `uuid.uuid4()` (random), `uuid.uuid5` (deterministic from namespace + name),
  `uuid.uuid7` (3.14, time-ordered).
- `secrets.token_hex`, `token_urlsafe`, `choice`.

```python
import hashlib, uuid, secrets
with open("data.csv", "rb") as f:
    print(hashlib.file_digest(f, "sha256").hexdigest())
print(uuid.uuid5(uuid.NAMESPACE_DNS, "example.com"))
print(secrets.token_urlsafe(32))
```

### Intermediate — what to learn

- `hmac.new(key, msg, "sha256")` and **`hmac.compare_digest`** for
  constant-time comparison (verify webhook signatures).
- Choosing keys; key rotation; replay protection with timestamps/nonces.
- Stable record fingerprints: canonical serialisation (sorted JSON keys,
  normalised whitespace/case) before hashing.
- Password hashing: use `hashlib.scrypt`/`pbkdf2_hmac` or, better, a dedicated
  library (`argon2-cffi`, `bcrypt`); never plain SHA.
- UUID versions and trade-offs: random vs deterministic vs time-ordered
  (index locality in databases).
- `blake2b`, `sha3_*`, `shake`; speed vs security.

```python
import hmac, hashlib

def verify(secret: bytes, body: bytes, signature_hex: str) -> bool:
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_hex)
```

### Advanced — what to learn

- Timing attacks and why `==` on secrets leaks information.
- Hash collisions, length-extension attacks (why HMAC, not `sha256(key+msg)`).
- Content-addressable storage: store files by hash, de-duplicate, verify integrity.
- Merkle-style change detection for incremental pipelines (hash partitions).
- Entropy and randomness sources: `os.urandom`, `secrets` vs `random`.
- Salting, peppering, key derivation parameters; password storage policy.
- Data protection: hashing PII is **not** anonymisation (rainbow tables, low-entropy inputs); tokenisation vs hashing (link to governance in Stage 2).
- Cryptography beyond the stdlib: use `cryptography`; never invent your own (preview of Module 1.22).

### Common mistakes

- Using `random` for tokens or session IDs.
- Comparing signatures with `==`.
- Believing a hash of an email address is anonymous.

### Self-check

1. Why is `hmac.compare_digest` required for signature checks?
2. Which UUID version would you use as a deterministic key from `(source, record_id)`?
3. Write a fingerprint function for a dict that is stable across key order and whitespace.

---

## Lesson 07 — `07-random-and-statistics.md`

**Why it matters.** Reproducible sampling, train/test splits, simulations,
test data and quick summaries all need controlled randomness and basic
statistics. Knowing `random`'s limits tells you when NumPy (Stage 2) and
statistics libraries (Stage 4) take over.

### Basic — what to learn

- `random.random`, `randint`, `choice`, `choices` (with replacement, weights),
  `sample` (without replacement), `shuffle`, `uniform`, `gauss`.
- Seeding: `random.seed(42)` for reproducibility.
- `statistics.mean`, `median`, `mode`, `multimode`, `stdev`, `variance`, `quantiles`.

```python
import random, statistics as st
random.seed(7)
data = [random.gauss(100, 15) for _ in range(1000)]
print(round(st.mean(data), 1), round(st.stdev(data), 1))
print(st.quantiles(data, n=4))
```

### Intermediate — what to learn

- Independent generators: `rng = random.Random(seed)` instead of the global
  state, so components do not interfere (and tests are deterministic).
- Reproducible splits and sampling in pipelines; seeding per partition.
- Population vs sample statistics: `pstdev` vs `stdev`; `fmean`, `geometric_mean`,
  `harmonic_mean`; `correlation`, `covariance`, `linear_regression` (3.10+).
- `statistics.NormalDist` for quick distribution maths (CDF, inverse CDF, overlap).
- Weighted sampling with `choices(cum_weights=...)`; reservoir sampling for streams.
- Floating-point accuracy: `statistics` uses exact fractions internally and is slower than NumPy.

```python
rng = random.Random(42)
sample = rng.sample(range(10_000), k=5)
nd = st.NormalDist(mu=0, sigma=1)
print(nd.cdf(1.96))
```

### Advanced — what to learn

- Mersenne Twister: period, state size, **not cryptographically secure**; use
  `secrets`/`SystemRandom` for security.
- Reproducibility across Python versions and platforms (algorithm changes);
  recording seeds with results; deterministic data generators for tests.
- Reservoir sampling (Algorithm R) implementation for unbounded streams; stratified sampling.
- Monte-Carlo estimation example (π, A/B test power simulation) with error bars.
- Hypothesis testing basics deferred to Stage 4; recognising when summary
  statistics mislead (Simpson's paradox, outliers, skew).
- When to switch to NumPy `Generator` (`default_rng`) for vectorised, parallel-safe, higher-quality random streams.
- Property-based test data generation (preview of Hypothesis in Stage 2).

### Common mistakes

- Using the global RNG in libraries.
- Using `random` for secrets.
- Reporting `stdev` of tiny samples without caveats.

### Self-check

1. Why prefer `random.Random(seed)` over `random.seed()` in a library?
2. Implement reservoir sampling and verify uniformity empirically.
3. Which function gives the sample standard deviation and which the population one?

---

## Lesson 08 — `08-tomllib-and-configparser.md`

**Why it matters.** `pyproject.toml`, tool configs, application settings and
legacy `.ini` files are everywhere. Parsing config safely, validating it and
layering sources (defaults → file → environment → CLI) is a daily task.

### Basic — what to learn

- `tomllib.load(f)` / `loads(text)`; **read-only** (writing needs `tomli-w`).
  Files must be opened in binary mode: `open(path, "rb")`.
- TOML types: strings, ints, floats, bools, datetimes, arrays, tables, arrays of tables.
- `configparser.ConfigParser`: sections, `get`, `getint`, `getboolean`, fallbacks, interpolation.

```python
import tomllib
doc = tomllib.loads("""
[db]
host = "localhost"
port = 5432
[[jobs]]
name = "daily"
""")
print(doc["db"]["port"], doc["jobs"][0]["name"])
```

### Intermediate — what to learn

- Reading `pyproject.toml` programmatically (project name, version, dependencies, tool tables).
- Error handling: `tomllib.TOMLDecodeError` with line info; friendly messages.
- Layered configuration: defaults < file < environment variables < CLI flags;
  merge dictionaries deeply; type conversion and validation.
- `configparser` specifics: case-insensitive keys, `DEFAULT` section,
  `ExtendedInterpolation`, `allow_no_value`, multiple files with `read([...])`.
- Mapping config into typed objects (dataclasses; `Pydantic` preview in Stage 2).
- Config file location conventions: XDG paths, `platformdirs` (third-party).

```python
import os, tomllib
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    host: str; port: int

def load(path) -> Settings:
    with open(path, "rb") as f:
        raw = tomllib.load(f).get("db", {})
    return Settings(os.getenv("DB_HOST", raw.get("host", "localhost")),
                    int(os.getenv("DB_PORT", raw.get("port", 5432))))
```

### Advanced — what to learn

- Security: never put secrets in committed config; secret references (env var
  names, secret manager IDs); file permissions; no `eval` in config.
- Validation & schema: required keys, unknown-key detection, helpful errors with
  the key path; versioned configs and migrations between versions.
- Comments and round-tripping: `tomllib` drops comments; use `tomlkit` when you
  must edit TOML preserving formatting.
- Comparing formats: TOML vs YAML vs JSON vs INI vs `.env` — decision table;
  YAML pitfalls (Norway problem, implicit typing, unsafe loaders).
- Hot reload and caching of config; immutability after load.
- Testing: config fixtures in `tmp_path`, monkeypatching environment variables.
- Reproducibility: record the **effective** merged config in run logs (without secrets).

### Common mistakes

- Opening TOML in text mode.
- Silently ignoring unknown or misspelled keys.
- Logging full config including secrets.

### Self-check

1. Why does `tomllib.load` require a binary file object?
2. Implement the precedence chain defaults → file → env → CLI with tests.
3. When would you choose `tomlkit` over `tomllib`?

---

## Lesson 09 — `09-urllib-sockets-and-http-server-basics.md`

**Why it matters.** Even if you use `httpx` (Stage 2) day to day, knowing the
layer below helps you debug timeouts, DNS failures, proxy problems and TLS
errors, and the stdlib is enough for small scripts, health checks and
local test servers.

### Basic — what to learn

- `urllib.request.urlopen(url, timeout=...)`, reading bytes and decoding;
  `urllib.parse` (`urlparse`, `urlencode`, `quote`, `urljoin`, `parse_qs`).
- HTTP status handling: `HTTPError` (has a status) vs `URLError` (network problem).
- Always set a **timeout**.

```python
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

url = "https://httpbin.org/get?" + urlencode({"q": "python"})
req = Request(url, headers={"User-Agent": "demo/1.0"})
with urlopen(req, timeout=10) as resp:
    print(resp.status, json.load(resp)["args"])
```

### Intermediate — what to learn

- POST with JSON body and headers; handling redirects; basic auth headers.
- Sockets: `socket.socket`, `AF_INET`/`SOCK_STREAM`, `connect`, `sendall`,
  `recv`, `bind`/`listen`/`accept`; TCP is a **byte stream**, not messages —
  framing (length prefix or delimiter).
- DNS and addressing: `socket.getaddrinfo`, IPv4/IPv6, `ipaddress` module.
- `http.server.ThreadingHTTPServer` with a custom `BaseHTTPRequestHandler` to
  build a **local fake API** for tests and demos.
- `http.client` for lower-level control.
- Timeouts at each stage: connect vs read; `socket.setdefaulttimeout`.

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, threading

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"ok": True}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers()
        self.wfile.write(body)

srv = ThreadingHTTPServer(("127.0.0.1", 0), H)      # port 0 = pick a free port
threading.Thread(target=srv.serve_forever, daemon=True).start()
```

### Advanced — what to learn

- TLS with `ssl`: default context, certificate verification (never disable it),
  custom CA bundles, SNI, TLS errors and how to read them.
- Partial reads, buffering and framing bugs; non-blocking sockets, `selectors`
  and how `asyncio` builds on them (preview).
- Proxies, environment variables (`HTTP_PROXY`, `NO_PROXY`), corporate TLS interception.
- SSRF: validating user-supplied URLs (scheme allow-list, resolve and block
  private/link-local ranges, redirect handling) — Module 1.22 lesson 06.
- Why `http.server` is for testing only (no hardening, limited concurrency).
- Retries, backoff and idempotency belong to the next level up (`httpx` + Stage 2).
- Using the fake server in pytest fixtures to test client code end-to-end.
- Debugging tools: `curl -v`, `tcpdump`/Wireshark basics, `ss`/`lsof` (links to Stage 0 networking).

### Common mistakes

- No timeouts (hung jobs).
- Treating `recv(n)` as returning a full message.
- Disabling certificate verification "to make it work".

### Self-check

1. What is the difference between `HTTPError` and `URLError`?
2. Why must a TCP protocol define message framing?
3. Write a pytest fixture that starts a local server on a free port and tears it down.

---

## Lesson 10 — `10-weakref-contextvars-and-copy.md`

**Why it matters.** Three small modules that solve hard problems: caches
that don't leak memory (`weakref`), per-request/per-task context without
globals (`contextvars`, essential for `asyncio` logging and tracing), and
precise copy semantics (`copy`).

### Basic — what to learn

- `weakref.ref(obj)`: does not keep the object alive; call it to dereference
  (returns `None` if collected). Not all built-ins are weak-referenceable
  (`list`, `dict`, `int` are not; user classes are).
- `weakref.WeakValueDictionary` / `WeakKeyDictionary` / `WeakSet` for caches and registries.
- `contextvars.ContextVar("request_id", default=None)`, `.get()`, `.set()`, `.reset(token)`.
- `copy.copy` vs `copy.deepcopy` recap (Module 1.11 lesson 11).

```python
import weakref
class Big: ...
cache = weakref.WeakValueDictionary()
b = Big(); cache["k"] = b
del b
print(len(cache))      # 0 once collected
```

### Intermediate — what to learn

- Why `contextvars` instead of `threading.local`: each `asyncio` task gets its own
  context copy; thread-locals are shared by all tasks in a thread.
- Using `ContextVar` for request IDs and structured logging (a logging
  `Filter` reading the variable), user identity, tracing spans.
- `contextvars.copy_context().run(fn)` and how `asyncio.create_task` /
  `loop.run_in_executor` / `to_thread` propagate context.
- `weakref.finalize(obj, callback, *args)` for cleanup that runs once at collection or exit.
- `weakref.proxy` and `WeakMethod` for observer/callback lists that don't create cycles.
- `copy` hooks: `__copy__`, `__deepcopy__(memo)`; `copy.replace` (3.13).

```python
import contextvars, logging
request_id = contextvars.ContextVar("request_id", default="-")

class RequestFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True

token = request_id.set("req-123")
try: ...        # work happens, logs carry the id
finally: request_id.reset(token)
```

### Advanced — what to learn

- Reference cycles, the cyclic GC and why weak references break cycles
  (links to Module 1.9 lesson 10 and Module 1.17 lesson 06).
- Cache design with weak references vs `functools.lru_cache` (strong refs keep
  objects alive → memory leaks); `lru_cache` on methods retains `self`.
- Callbacks and observers: bound methods hold strong refs to instances; use `WeakMethod`.
- `contextvars` in multi-threaded/executor code (context is **not** propagated
  to threads automatically except via `asyncio.to_thread`); free-threaded builds (3.13+/3.14).
- Python 3.14 per-interpreter and thread contexts (awareness); `threading.Thread(context=...)` (3.14).
- Testing leaks: `gc.collect()`, `weakref` probes in tests; `tracemalloc` snapshots.
- Pitfalls: token misuse (`reset` in the wrong context), mutable context values,
  hidden global state through `ContextVar`.
- Deep copy cost and cycles: structural sharing, immutable data as an alternative.

### Common mistakes

- Using `threading.local` in async code.
- `lru_cache` on instance methods causing leaks.
- Expecting `WeakValueDictionary` entries to survive when no strong reference exists.

### Self-check

1. Why do `asyncio` tasks need `ContextVar` instead of thread-local storage?
2. Write an object cache that never prevents garbage collection of its values, and test it with `gc.collect()`.
3. How does `weakref.finalize` differ from `__del__`?

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**, grouped by phase:

| Phase | Question types |
| --- | --- |
| A | Replace loops by `itertools`; sort with `itemgetter`/`attrgetter`; explain `groupby` bugs |
| B | Safe extract, atomic write; `subprocess` timeout + error handling; idempotent SQLite loader |
| C | HMAC verification; deterministic UUID keys; reproducible sampling with independent RNGs |
| D | Layered config loader; local HTTP test server; context-propagating logger; weak-ref cache |

Add 6 **"find the security bug"** questions (zip-slip, `shell=True`, `random` for tokens, `==` on signatures, f-string SQL, `verify=False`).

---

## 5. Module mini-project

**Build `datadrop`**, a small command-line "ingest and archive" tool:

1. Reads a TOML config (with env and CLI overrides), validated into a frozen dataclass.
2. Downloads files from a URL list via `urllib` (timeouts, retries by hand, size limits)
   into a temp directory, verifying SHA-256 against a manifest.
3. Streams, batches and normalises CSV rows with `itertools.batched`.
4. Writes results to SQLite with an idempotent upsert, tracking processed file hashes.
5. Archives raw files into a `tar.gz` safely, writing atomically.
6. Calls an external compressor (`gzip`/`zstd`) through `subprocess` with
   timeouts and exit-code handling.
7. Logs with a request/run ID provided by `contextvars`.
8. Tests use a local `http.server` fixture, `tmp_path`, and a fixed seed.

Acceptance: re-running with the same input changes nothing (idempotent), ≥ 90 %
coverage, `ruff` + type checker clean, README with a runbook.

---

## 6. Completion checklist

- [ ] I can build lazy pipelines with `itertools` and explain memory behaviour.
- [ ] I replace lambdas with `operator` helpers where clearer.
- [ ] I write atomic file replacements and extract archives safely.
- [ ] I run subprocesses without shell injection, with timeouts and error handling.
- [ ] I use `sqlite3` with parameters, transactions, foreign keys and WAL.
- [ ] I verify signatures with HMAC and constant-time comparison; I use `secrets` for tokens.
- [ ] I create reproducible randomness with independent generators.
- [ ] I load, layer and validate configuration safely.
- [ ] I make HTTP requests with timeouts and run a local test server.
- [ ] I can use `weakref` and `contextvars` and explain when each is needed.
- [ ] I completed the `datadrop` mini-project.

**Next:** Module 1.14 — Bytes, Binary Data and Advanced Text Processing.
