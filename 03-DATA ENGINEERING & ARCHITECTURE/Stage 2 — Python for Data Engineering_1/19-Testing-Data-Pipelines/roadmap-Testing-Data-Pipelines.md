# Roadmap — Module 2.19: Testing Data Pipelines

This is the learning roadmap for the nineteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about testing data
pipelines, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

You already know how to test software: pytest, fixtures, parametrisation,
arrange–act–assert, boundary and regression tests, and mocking (Stage 1,
Module 1.7). Throughout Stage 2 you also wrote tool-specific tests — Spark
tests, DAG tests, dbt unit tests, Pandera schemas. What is still missing is
a **coherent testing strategy for data systems**, where most bugs are not
crashes but **silently wrong data**: a join that duplicates rows only when
a key repeats, a float that drifts in the third decimal, a time-zone bug
that appears once a year, a schema change that breaks a consumer three
teams away.

This module builds that strategy: small, readable fixture data;
comparisons that are exact where they must be and tolerant where they
should be; integration tests against real services in containers;
property-based tests that find edge cases you never imagined; safe test
data; regression tests for schemas and contracts; and end-to-end smoke
tests that prove the whole pipeline works before and after every
deployment.

> **Tests vs data-quality checks.** Tests (this module) run **before
> deployment** and check that the **code** behaves correctly on known
> inputs. Data-quality checks (Module 2.11) run **in production** and check
> that **real data** meets expectations. A mature platform needs both.

---

## 1. Module outcome

By the end of this module you will be able to:

- Design a **test strategy** for a data platform: which tests exist at
  which level, where they run, and how long they may take.
- Test transformations with small, readable **fixture DataFrames** built by
  test-data builders, across pandas, Polars, DuckDB, and Spark.
- Compare DataFrames correctly: dtypes, order, nulls vs NaN, time zones,
  exact decimals, and float **tolerances** — with useful diff reports.
- Write **integration tests** against real PostgreSQL, object storage, and
  Kafka using **Testcontainers**, with isolated and fast state handling.
- Use **property-based testing** with Hypothesis to prove invariants such
  as idempotency, row conservation, and "incremental equals full rebuild".
- Generate **synthetic** test data and build **sampled, masked** datasets
  from production safely and reproducibly.
- Write **schema, contract, and data-diff regression tests** that catch
  unintended changes before consumers do.
- Build **end-to-end smoke tests** for batch and streaming pipelines, in CI
  and after deployment, without flakiness.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.18. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| pytest, assertions, fixtures, parametrisation, arrange–act–assert, boundary/invalid/regression tests, mocking, debugging | Stage 1 — Module 1.7 | The foundation of everything here; **not** re-taught |
| Pure functions, separating side effects | Stage 1 — Module 1.8 | Testable pipeline design |
| NumPy random generators, float precision, NaN | Stage 2 — Module 2.2 | Seeded data generation and tolerant comparisons |
| pandas, Polars, DuckDB dtypes and nulls | Stage 2 — Modules 2.3–2.4 | Equality semantics differ by engine |
| Transactions, `MERGE`, SCD | Stage 2 — Module 2.6 | Integration-test targets and invariants |
| Alembic, `COPY`, streaming extraction | Stage 2 — Module 2.7 | Database code under integration test |
| API clients, mock APIs, CDC, file registries | Stage 2 — Module 2.9 | Recorded responses and ingestion tests |
| Async code and concurrency | Stage 2 — Module 2.10 | Testing async and concurrent components |
| Pydantic, Pandera, contracts, schema diffs, reconciliation | Stage 2 — Module 2.11 | Contracts under regression test; Pandera strategies |
| Pure steps, run context, idempotent loads, hashing, state, dbt unit tests | Stage 2 — Module 2.12 | The main objects of test |
| DAG tests | Stage 2 — Module 2.13 | Part of the pyramid; **not** re-taught |
| PySpark testing (session fixture, `assertDataFrameEqual`, plan tests) | Stage 2 — Module 2.14 | Spark specifics **not** re-taught; integrated into the strategy |
| Kafka producers/consumers, delivery semantics | Stage 2 — Module 2.16 | Streaming integration and smoke tests |
| MinIO, `moto`, boto3 | Stage 2 — Module 2.17 | Storage tests |
| Docker, Compose, CI workflows, ephemeral environments, promotion | Stage 2 — Module 2.18 | Where these tests run |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add --dev pytest pytest-xdist
  pytest-cov hypothesis "testcontainers[postgres,kafka,minio]" faker
  syrupy time-machine pytest-recording` plus the engines you test
  (`pandas`, `polars`, `duckdb`, `pyspark`, `pandera`).
- Docker (for Testcontainers).
- Your platform repository and CI from Module 2.18.
- Optional: a mutation-testing tool (e.g. `mutmut`) to measure how good
  your tests are.

---

## 3. How the module is organised

The seven topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Unit-Level Data Tests                     (Basics → Intermediate)
  01 Testing transformations with fixture DataFrames
  02 DataFrame equality and tolerance assertions

Phase B — Tests Against Real Services               (Intermediate)
  03 Integration tests with Testcontainers

Phase C — Better Test Inputs                        (Intermediate → Advanced)
  04 Property-based testing with Hypothesis
  05 Synthetic and sampled test data

Phase D — System-Level Protection                   (Advanced)
  06 Schema and contract regression tests
  07 End-to-end pipeline smoke tests

Consolidate
  practice-questions.md
  Module mini-project: a complete test suite for the data platform
```

The data-pipeline **test pyramid** this module builds:

```text
                 ▲  fewer, slower, broader
                 │
     07  End-to-end smoke tests (CI + post-deploy)
     06  Schema / contract / data-diff regression tests
     03  Integration tests (real services in containers)
 01–02  Unit tests of transformations (fixture DataFrames)
   04   Property-based tests across all levels
   05   Test data feeding every level
                 │
                 ▼  more, faster, narrower
```

Why this order:

- Unit tests (01) and correct comparisons (02) are the base of the pyramid
  and are needed by every later topic.
- Integration tests (03) add real I/O once pure logic is covered.
- Hypothesis (04) and test data (05) improve the **inputs** of tests at
  every level.
- Regression (06) and end-to-end smoke tests (07) protect the whole system
  and use everything above.

---

## 4. Suggested schedule

About **3 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — fixture DataFrames · Topic 02 — equality and tolerances · Topic 03 — Testcontainers |
| 2 | Topic 04 — Hypothesis · Topic 05 — synthetic and sampled data |
| 3 | Topic 06 — schema and contract regression · Topic 07 — end-to-end smoke tests · practice questions · mini-project |

---

## 5. How to study every topic (the data-testing loop)

```text
Read → Name the bug you want to catch → Write the smallest failing test
→ Make it pass → Inject the bug on purpose → Confirm the test catches it
→ Check speed and flakiness → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Name the bug** the test exists to catch (for example "join duplicates
   rows when a product id repeats"). A test without a named bug is often
   decoration.
3. **Write the smallest failing test** with the smallest data that exposes
   the bug.
4. **Make it pass** with the correct implementation.
5. **Inject the bug on purpose** (reintroduce the defect, or mutate the
   code) and confirm the test fails with a **clear message**.
6. **Check speed and flakiness**: run the test 20 times and in parallel;
   it must always pass and stay within its time budget.
7. **Write down** the pattern in `module-2.19-notes.md`.
8. **Explain aloud** what the test protects and why it is at that level of
   the pyramid.

Organise the test suite by level so CI can run each level separately
(Module 2.18):

```text
tests/
├── unit/            # fixture DataFrames, pure transformations (seconds)
├── property/        # Hypothesis properties (seconds to a minute)
├── integration/     # Testcontainers: PostgreSQL, MinIO, Kafka (minutes)
├── regression/      # schema snapshots, contracts, golden data diffs
├── e2e/             # end-to-end smoke tests (minutes)
├── builders/        # test-data builders and factories
├── data/            # small versioned fixture files and golden outputs
└── conftest.py      # shared fixtures, markers, Hypothesis profiles
```

---

## 6. Phase A — Unit-Level Data Tests (Basics → Intermediate)

### Topic 01 — [Testing transformations with fixture DataFrames](01-testing-transformations-with-fixture-dataframes.md)

**Why it comes first:** Most business logic in data pipelines lives in
transformations. Tested with tiny, readable DataFrames, it can be checked
in milliseconds — if the fixtures are designed well.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Unit-testing pure transformation functions (`DataFrame → DataFrame`, the Module 2.12 structure) with handwritten input and expected output frames |
| Basics | Minimal fixtures: only the columns and rows the rule needs; explicit schemas so dtypes are never guessed |
| Basics | One behaviour per test, named after the rule (`test_latest_version_wins_when_updated_at_ties_by_sequence`) |
| Intermediate | **Test-data builders / factories**: functions that create valid rows with sensible defaults, so each test overrides only what matters |
| Intermediate | **Table-driven tests**: parametrising many small input/expected pairs for one rule |
| Intermediate | An **edge-case catalogue** for data: empty input, one row, all nulls, duplicates, ties, Unicode and whitespace, extreme values, time-zone and daylight-saving boundaries, month-ends, leap days, late records |
| Intermediate | Inline literal frames vs small fixture files (CSV/JSON/Parquet) — readability vs realism |
| Intermediate | **Controlling time**: passing the run date (Module 2.12) and freezing the clock in tests (e.g. `time-machine`) for code that still reads time |
| Advanced | **Engine-parametrised tests**: the same behaviour test run against pandas, Polars, DuckDB, and Spark implementations via fixtures |
| Advanced | Fixture scope and cost: session-scoped Spark or DuckDB connections, function-scoped data |
| Advanced | Testing multi-step pipelines: testing each step alone vs the chain; avoiding tests that restate the implementation |
| Advanced | Measuring test quality: coverage of branches **and** of the edge-case catalogue; mutation testing (awareness) to see whether tests notice real bugs |

**How to learn it**

1. Read the topic file.
2. Take your Module 2.12 silver steps and list, for each, the edge cases
   from the catalogue that apply.
3. Rewrite one bloated test (large CSV fixture, many assertions) into
   several small builder-based tests.

**Hands-on exercise — `tests/unit/` and `tests/builders/`**

1. Build `order_row(**overrides)` and `orders_frame(*rows)` builders with
   an explicit schema for your orders data.
2. Write table-driven tests for deduplication (ties, out-of-order
   versions), status standardisation, and currency conversion.
3. Cover the edge-case catalogue for your daily revenue aggregation,
   including a daylight-saving day and an empty day.
4. Parametrise one behaviour test across your Polars and DuckDB (and,
   optionally, Spark) implementations.
5. Freeze time for a legacy function that still calls "now" and test it.
6. Inject three bugs and confirm each is caught by a specific, clearly
   named test.

**Checkpoint — you are ready to move on when you can:**

- [ ] Write minimal, readable fixture DataFrames with explicit schemas.
- [ ] Use builders and table-driven tests.
- [ ] Apply the data edge-case catalogue systematically.
- [ ] Run the same behaviour test against several engines.
- [ ] Control time in tests.

**Common mistakes:** huge fixture files copied from production;
fixtures with inferred dtypes; tests that assert on everything at once;
tests that pass only on the author's time zone.

---

### Topic 02 — [DataFrame equality and tolerance assertions](02-dataframe-equality-and-tolerance-assertions.md)

**Why here:** A test is only as good as its comparison. DataFrame equality
is full of traps: row order, column order, dtypes, NaN vs null, float
precision, time zones — and failures on large frames are unreadable
without good diffs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Engine assertions: `pandas.testing.assert_frame_equal`, `polars.testing.assert_frame_equal`, `pyspark.testing.assertDataFrameEqual` (Module 2.14), and `numpy.testing.assert_allclose` |
| Basics | What "equal" means: values, dtypes, column names and order, row order, index (pandas) |
| Basics | Options to relax order and dtype strictness **deliberately**, not by default |
| Intermediate | **Row order**: sorting both frames by a key before comparing, or order-insensitive options |
| Intermediate | **Nulls vs NaN**: pandas `NaN`, `None`, and `pd.NA`; Polars `null` vs `NaN`; SQL `NULL` — and making comparisons explicit |
| Intermediate | **Floats**: relative vs absolute tolerance, choosing tolerances from the computation (sums of millions of values vs a single multiplication), `pytest.approx` for scalars |
| Intermediate | **Exact values**: money as `Decimal` or integer cents must compare exactly; never use tolerances to hide rounding bugs |
| Intermediate | **Timestamps**: units (ns vs µs), time zones, and comparing instants rather than wall-clock strings |
| Advanced | **Readable diffs** for large frames: anti-joins on keys to show missing, extra, and changed rows; per-column mismatch summaries |
| Advanced | Comparing very large outputs: row counts, per-partition checksums or hashes (Module 2.12), and sampled row comparisons |
| Advanced | **Snapshot (golden) tests** for complex outputs (e.g. with `syrupy`): when they help, and the discipline of reviewing snapshot updates |
| Advanced | Cross-engine comparisons: normalising dtypes (e.g. `Int64` vs `int64`, `large_string` vs `string`) before comparing |

**How to learn it**

1. Read the topic file.
2. Create 15 pairs of "equal-looking" frames that differ in one subtle way
   (order, dtype, NaN vs null, time zone, float noise) and note which
   assertion options detect each.
3. Compute a 10-million-row sum in two different orders and measure the
   float difference to choose a justified tolerance.

**Hands-on exercise — `tests/helpers/frames.py`**

1. Write `assert_frames_equal(left, right, keys, float_cols=..., rtol=...,
   exact_cols=...)` that normalises dtypes and order, compares float
   columns with tolerance, compares decimal/key columns exactly, and treats
   nulls explicitly.
2. On failure, print a readable diff: missing keys, extra keys, and changed
   values per column (first N examples).
3. Add `assert_large_outputs_match(path_a, path_b, keys)` using counts and
   per-partition hashes.
4. Add one snapshot test for a complex report and practise reviewing a
   snapshot change.
5. Use the helpers across your unit tests and delete ad-hoc comparisons.

**Checkpoint:**

- [ ] Explain every dimension of DataFrame equality.
- [ ] Choose float tolerances with a justification.
- [ ] Compare money, timestamps, and nulls correctly.
- [ ] Produce readable diffs for large frame mismatches.
- [ ] Use snapshot tests responsibly.

**Common mistakes:** `check_dtype=False` everywhere; tolerances loose
enough to hide real bugs; order-dependent assertions on unordered outputs;
accepting snapshot updates without reading them.

---

## 7. Phase B — Tests Against Real Services (Intermediate)

### Topic 03 — [Integration tests with Testcontainers](03-integration-tests-with-testcontainers.md)

**Why here:** Mocks prove your code calls a database; they do not prove
the SQL works, the `COPY` format is right, or the Kafka consumer commits
offsets correctly. Integration tests run your code against **real**
services in disposable containers.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What integration tests cover that unit tests cannot: SQL dialects, drivers, transactions, file formats, network behaviour, and configuration |
| Basics | **Testcontainers for Python**: starting PostgreSQL, MinIO, and Kafka (or a Kafka-compatible broker) from pytest fixtures; connection details from the container |
| Basics | Readiness: wait strategies so tests start only when the service is ready |
| Intermediate | Fixture scopes: one container per test session for speed, with **isolated state** per test |
| Intermediate | **State isolation strategies**: a transaction rolled back after each test, unique schemas/buckets/topics per test, or truncation — trade-offs |
| Intermediate | Testing database code: Alembic migrations up and down on a real database (Module 2.7), `COPY` loaders, `MERGE` logic, and SCD Type 2 loads |
| Intermediate | Testing storage code against MinIO vs mocks (`moto`) — when each is appropriate (Module 2.17) |
| Intermediate | Testing Kafka producers and consumers: produce, consume, commit, and rebalance behaviour (Module 2.16) |
| Advanced | Recorded HTTP interactions for API extractors (e.g. `pytest-recording` / VCR-style cassettes) and your mock API from Module 2.9 as a container |
| Advanced | Speed: parallel test workers with separate resources, container reuse, and slim images |
| Advanced | Running Testcontainers in CI (Docker on runners) and the choice between Testcontainers and a Compose stack (Module 2.18) |
| Advanced | Testing failure paths with real services: killed connections, timeouts, constraint violations, and broker restarts |

**How to learn it**

1. Read the topic file.
2. List every piece of I/O code in your platform and decide: unit test with
   a fake, integration test with a container, or both.
3. Run your integration suite serially and with parallel workers; fix any
   interference between tests.

**Hands-on exercise — `tests/integration/`**

1. Create session-scoped fixtures for PostgreSQL, MinIO, and Kafka with
   wait strategies.
2. Test Alembic migrations (upgrade to head, downgrade to base, upgrade
   again) on a real database.
3. Test the staging → validate → `MERGE` loader (Module 2.7) with
   per-test isolation, including an idempotent re-run.
4. Test Parquet writes and reads on MinIO through your fsspec helpers
   (Module 2.17).
5. Test a Kafka consumer's at-least-once behaviour: kill it mid-batch and
   assert no lost events and an idempotent sink (Module 2.16).
6. Test an API extractor with recorded responses, including a `429` and a
   token refresh.
7. Keep the whole integration suite under a time budget (e.g. 5 minutes)
   with parallel workers.

**Checkpoint:**

- [ ] Start real services in tests with Testcontainers.
- [ ] Isolate state between tests while keeping them fast.
- [ ] Integration-test database, storage, and Kafka code.
- [ ] Choose between containers, mocks, and recorded responses.
- [ ] Run integration tests reliably in CI.

**Common mistakes:** mocking the database for SQL-heavy code; tests that
depend on each other's data; a new container per test (slow); `sleep`
instead of readiness checks.

---

## 8. Phase C — Better Test Inputs (Intermediate → Advanced)

### Topic 04 — [Property-based testing with Hypothesis](04-property-based-testing-with-hypothesis.md)

**Why here:** Example tests check the cases you thought of. Property-based
tests generate hundreds of inputs you did not think of and check
**invariants** that must hold for all of them — ideal for data
transformations, where edge cases are endless.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Properties vs examples: stating what must always be true |
| Basics | Hypothesis essentials: `@given`, strategies (`integers`, `floats`, `text`, `datetimes` with time zones, `lists`, `builds`, `composite`), and **shrinking** to minimal failing examples |
| Basics | Settings and profiles: `max_examples`, deadlines, and faster CI profiles vs thorough nightly profiles |
| Intermediate | **Generating DataFrames**: Hypothesis's pandas extras, Polars' parametric testing helpers, and **Pandera schema strategies** (generate data that satisfies a schema — Module 2.11) |
| Intermediate | **Data-pipeline properties**: idempotency (`f(f(x)) == f(x)`), round trips (write → read returns the same data), row conservation (`rows_in = rows_out + quarantined`), key uniqueness after deduplication, totals preserved by enrichment joins |
| Intermediate | **Metamorphic properties**: shuffling input rows does not change the output; processing in chunks equals processing all at once; **incremental equals full rebuild** (Module 2.12) |
| Intermediate | **Model-based (oracle) testing**: comparing an optimised implementation with a simple reference (e.g. Polars vs a plain DuckDB SQL version) |
| Advanced | Cross-language consistency: Python hash keys equal SQL hash keys for any generated input (Module 2.12) |
| Advanced | **Stateful testing** (rule-based state machines) for merge loads, SCD Type 2, watermarks, and checkpoints: random sequences of operations must keep invariants |
| Advanced | Pitfalls: over-filtering with `assume`, slow strategies, non-deterministic code, and floats generating NaN/infinity unless constrained |
| Advanced | The example database and reproducing failures in CI; turning found failures into permanent regression examples |

**How to learn it**

1. Read the topic file.
2. For five transformations, write down every property they should
   satisfy before writing any test.
3. Run your first property tests and study the shrunk failing examples
   Hypothesis finds.

**Hands-on exercise — `tests/property/`**

1. Property-test deduplication: output keys are unique; every output row
   exists in the input; running it twice changes nothing; shuffled input
   gives the same output.
2. Property-test the merge loader with a Hypothesis state machine: random
   batches of inserts, updates, deletes, and replays must leave the target
   equal to a simple dictionary model.
3. Property-test that incremental daily revenue equals a full rebuild for
   random change sequences, including late records.
4. Property-test that Python and DuckDB hash keys match for random
   strings, nulls, Unicode, and timestamps.
5. Generate DataFrames from a Pandera schema and property-test a silver
   step end to end.
6. Record every bug Hypothesis finds as an explicit regression example.

**Checkpoint:**

- [ ] Express transformations as properties.
- [ ] Generate DataFrames with Hypothesis, Polars helpers, or Pandera.
- [ ] Write metamorphic and model-based tests.
- [ ] Use stateful testing for load and state logic.
- [ ] Keep property tests fast and reproducible in CI.

**Common mistakes:** properties that re-implement the function; filtering
away most generated inputs; forgetting to constrain floats and time zones;
ignoring a shrunk failure because "real data never looks like that".

---

### Topic 05 — [Synthetic and sampled test data](05-synthetic-and-sampled-test-data.md)

**Why here:** Unit fixtures are tiny; integration, end-to-end, and
performance tests need **realistic** data — but real production data
contains personal information and is too big. You need data that behaves
like production without being production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why not copy production: privacy and legal risk, size, instability, and missing edge cases |
| Basics | **Synthetic data**: generated from code with seeded randomness (NumPy generators from Module 2.2) and libraries such as Faker for realistic names, addresses, and texts |
| Basics | Determinism: seeds and versioned generators so the same test data can be recreated exactly |
| Intermediate | **Realistic structure**: skewed key distributions, seasonality, lateness, duplicates, nulls, and bad records — the generators you built in Modules 2.9 and 2.16 as reusable packages |
| Intermediate | **Relational consistency**: generating customers, products, orders, and events that reference each other correctly (and deliberately incorrectly, for orphan tests) |
| Intermediate | **Sampling production safely**: random, stratified, and **key-consistent sampling** (hash-based selection so related rows across tables stay together — hashing from Module 2.12) |
| Intermediate | **Masking and pseudonymisation** before data leaves production: dropping, generalising, keyed hashing, and format-preserving fakes — with rules per column (PII governance in Module 2.20) |
| Advanced | **Edge-case mining**: extracting real unusual records (anonymised) that broke pipelines before, and adding them to fixtures |
| Advanced | Statistical synthetic data generators that learn distributions from real data — awareness, and their privacy limits |
| Advanced | Data tiers: tiny (unit), small (integration and end-to-end), large (performance), each with a documented purpose and size |
| Advanced | Versioning and storing test datasets (in object storage or data-versioning tools — awareness), and refreshing them without breaking golden tests |
| Advanced | Test data for dbt (seeds and unit-test fixtures) and for non-production environments (Module 2.18) |

**How to learn it**

1. Read the topic file.
2. Profile a real or realistic dataset (distributions, null rates, key
   skew, lateness) and write a specification your generator must match.
3. Design masking rules for every column that could identify a person.

**Hands-on exercise — `testdata/`**

1. Build a `testdata` package that generates consistent customers,
   products, orders, payments, and click events from a seed and a size
   tier, with configurable skew, lateness, duplicates, and bad records.
2. Validate generated data against its specification (distribution checks
   using the monitors from Module 2.11).
3. Build a key-consistent sampler that takes 1% of customers and all their
   related rows from a larger dataset.
4. Build a masking step: keyed hashing for ids, fake names and emails,
   generalised birth dates and postcodes; verify no original PII remains.
5. Add three mined edge-case records (anonymised) as permanent fixtures.
6. Publish tiny, small, and large versions to MinIO with a manifest and
   seed.

**Checkpoint:**

- [ ] Generate reproducible, realistic, relationally consistent data.
- [ ] Sample production data with key consistency.
- [ ] Mask and pseudonymise data before it leaves production.
- [ ] Maintain versioned test-data tiers.

**Common mistakes:** unseeded random data (tests that fail once a month);
uniform distributions that never exercise skew; "anonymised" data with
unkeyed hashes of emails; production personal data in developer laptops
and CI logs.

---

## 9. Phase D — System-Level Protection (Advanced)

### Topic 06 — [Schema and contract regression tests](06-schema-and-contract-regression-tests.md)

**Why here:** The most expensive data bugs are changes that are valid for
the producer but break someone downstream: a renamed column, a changed
type, a metric that silently shifts. Regression tests make every such
change visible and deliberate.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Regression tests for data: once a behaviour or schema is agreed, any change must be intentional and reviewed |
| Basics | **Schema snapshot tests**: the output schema (column names, types, nullability) of each published table stored in the repository; tests fail when the schema changes without an updated snapshot |
| Basics | **Bug regression tests**: every production incident becomes a test with the minimal data that reproduced it |
| Intermediate | **Contract tests**: validating produced outputs against their data contracts (Module 2.11) and event schemas (Module 2.16) in CI |
| Intermediate | **Breaking-change checks**: running your schema-diff tool (Module 2.11) and schema-registry or Protobuf checks (Module 2.16) against the main branch |
| Intermediate | dbt model contracts and unit tests (Module 2.12) as part of the regression layer |
| Intermediate | API contract tests for extractors: validating recorded source responses against the source's documented schema, and failing clearly when the source changes |
| Advanced | **Consumer-driven contract tests**: consumers declare the fields and guarantees they rely on; the producer's CI verifies them (awareness of the idea and tooling) |
| Advanced | **Golden-data diff tests**: running the new pipeline version and the current version on the same fixed inputs and diffing outputs row by row — failing on unexpected differences, documenting expected ones |
| Advanced | **Metric regression tests**: key business totals (revenue, active users) on a fixed dataset must stay within agreed bounds unless a change is approved |
| Advanced | Keeping regression suites maintainable: clear ownership, fast updates for intended changes, and review rules for snapshot and golden-data changes |

**How to learn it**

1. Read the topic file.
2. List every published dataset and event in your platform and its
   consumers; decide which regression test protects each.
3. Replay two past incidents from earlier modules (a renamed source field,
   a duplicated batch) and write the tests that would have caught them.

**Hands-on exercise — `tests/regression/`**

1. Add schema snapshot tests for every gold table and published topic,
   with a command to update snapshots intentionally.
2. Validate pipeline outputs against their data contracts and event schemas
   in CI.
3. Wire the schema-diff and Protobuf breaking-change checks into the
   regression suite.
4. Build a golden-data diff test: run `main` and the pull request's
   pipeline on the same fixed dataset and report added, removed, and
   changed rows.
5. Add metric regression bounds for revenue and order counts on the fixed
   dataset.
6. Turn three past bugs from your notes into permanent regression tests.

**Checkpoint:**

- [ ] Write schema snapshot and contract tests.
- [ ] Detect breaking changes automatically.
- [ ] Build golden-data and metric regression tests.
- [ ] Turn incidents into regression tests.
- [ ] Explain consumer-driven contract testing.

**Common mistakes:** snapshots updated blindly to make CI green; contracts
checked only in production; golden datasets nobody can regenerate;
regression tests with no owner.

---

### Topic 07 — [End-to-end pipeline smoke tests](07-end-to-end-pipeline-smoke-tests.md)

**Why last:** Every component can pass its tests while the whole pipeline
still fails — a wrong configuration, a missing permission, a DAG wired to
the wrong table. Smoke tests run the **whole** pipeline on small data and
check that it works end to end, before and after deployment.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Smoke tests vs full end-to-end tests: quick "does it work at all?" checks vs exhaustive scenarios |
| Basics | A batch smoke test: run ingest → bronze → silver → gold on a tiny dataset in an ephemeral environment (Compose, Testcontainers, or a per-PR environment from Module 2.18) |
| Basics | Assertions: the pipeline completes, outputs exist, row counts are within expected ranges, key invariants hold, and quality checks pass |
| Intermediate | Running orchestrated pipelines in tests (e.g. `airflow dags test`, Dagster in-process materialisation, Prefect flow calls — Module 2.13) |
| Intermediate | **Streaming smoke tests**: produce known events, then **poll** the sink with a timeout until expected results appear (never fixed sleeps) |
| Intermediate | **Post-deployment smoke tests** in staging and production: read-only canary queries, freshness checks, and a synthetic **canary record** flowing through the pipeline |
| Intermediate | Where they run: on merge, before promotion to staging and production (gates from Module 2.18), and on a schedule |
| Advanced | **Flakiness**: causes (timing, shared state, random data, external services, time zones) and fixes (deterministic data, readiness checks, isolation, frozen time); retrying only infrastructure failures, never assertions |
| Advanced | Time budgets and parallelism for end-to-end suites |
| Advanced | Chaos variants: killing a component mid-run and asserting recovery (Modules 2.12 and 2.16) |
| Advanced | Reporting: clear failure messages pointing to the failed stage, logs and artefacts saved by CI for debugging |
| Advanced | Where smoke tests end and production monitoring begins (Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Draw your platform end to end and choose the smallest dataset that
   touches every stage.
3. Run the smoke test 20 times in a row; fix every source of flakiness you
   find.

**Hands-on exercise — `tests/e2e/`**

1. Build a batch smoke test: start the stack (Compose or Testcontainers),
   load the tiny test-data tier, run the full daily DAG for one date, and
   assert outputs, row counts, invariants, and quality results.
2. Build a streaming smoke test: produce 100 known events, poll the
   lakehouse sink until results appear (with a timeout), and compare with
   expected aggregates.
3. Build a post-deployment smoke test for staging: read-only checks plus a
   canary record traced from source to gold.
4. Add the smoke tests as CI gates before promotion (Module 2.18) and as a
   nightly job.
5. Make the suite deterministic: 20 consecutive green runs, within a time
   budget.
6. Save logs and output samples as CI artefacts when a smoke test fails.

**Checkpoint:**

- [ ] Build end-to-end smoke tests for batch and streaming pipelines.
- [ ] Run orchestrated pipelines inside tests.
- [ ] Design post-deployment smoke tests and canary records.
- [ ] Diagnose and eliminate flaky tests.
- [ ] Place smoke tests correctly in CI/CD.

**Common mistakes:** end-to-end tests on large data that take an hour;
fixed `sleep` waits; retrying failed assertions until they pass; smoke
tests that write to production tables; no artefacts to debug CI failures.

---

## 10. Consolidate — practice questions

When all seven topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Name the bugs that matter for the component or pipeline in question.
2. Place each test at the right level of the pyramid and justify it.
3. Choose inputs: fixture builders, Hypothesis strategies, synthetic tiers,
   or masked samples.
4. Choose comparisons: exact, tolerant, order-insensitive, or diff-based.
5. Implement the tests and inject the bugs to prove they are caught.
6. Check speed and flakiness, and decide where each test runs in CI/CD.

---

## 11. Module mini-project — a complete test suite for the data platform

This is the proof that you have finished the module.

**Scenario:** Your platform (Modules 2.9–2.18) is deployed through CI/CD,
but its tests grew piecemeal. After a silent revenue error slipped into
production, leadership asks for a test strategy that would have caught it
— and a suite that proves the platform works on every change.

Build `tests/` (and a `testdata` package) for your platform with:

1. **Strategy document** — the test pyramid for your platform: levels,
   what each protects, where each runs (pre-commit, pull request, merge,
   nightly, pre-promotion, post-deploy), and time budgets.
2. **Unit tests** — builders, table-driven tests, the edge-case catalogue,
   frozen time, and engine-parametrised tests for key transformations.
3. **Assertion helpers** — a shared DataFrame comparison library with
   justified tolerances, exact money comparisons, and readable diffs.
4. **Integration tests** — Testcontainers for PostgreSQL, MinIO, and Kafka
   covering migrations, bulk loads with `MERGE`, storage helpers, consumer
   semantics, and recorded API interactions.
5. **Property tests** — idempotency, conservation, uniqueness, "incremental
   equals full rebuild", Python-vs-SQL hash consistency, and a stateful
   test of the merge loader.
6. **Test data** — a seeded generator with size tiers and realistic
   defects, a key-consistent sampler, and a masking step with verification.
7. **Regression tests** — schema snapshots, contract validation,
   breaking-change checks, golden-data diffs, metric bounds, and
   incident-based tests (including the silent revenue error).
8. **End-to-end smoke tests** — batch and streaming smoke tests in CI and a
   post-deployment canary check in staging.
9. **CI integration** — each level as a separate CI job with the right
   triggers, parallelism, artefacts on failure, and required checks.
10. **Quality of the tests themselves** — branch coverage, edge-case
    catalogue coverage, 20 consecutive green runs (no flakiness), and
    optionally a mutation-testing report for one critical module.

**Grading yourself:** re-introducing each past bug (join duplication,
time-zone error, renamed source field, duplicated batch, silent revenue
error) makes at least one test fail with a clear message; the full
pull-request suite runs within its time budget; no test depends on
production data or network access outside its containers; and the suite
never fails randomly.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.20 when you can tick every box without looking at your
notes:

- [ ] I can design a test pyramid for a data platform and explain tests vs
      data-quality checks.
- [ ] I can write readable fixture-based unit tests across engines.
- [ ] I can compare DataFrames correctly with justified tolerances and
      clear diffs.
- [ ] I can write fast, isolated integration tests with Testcontainers.
- [ ] I can express and test data invariants with Hypothesis, including
      stateful tests.
- [ ] I can generate synthetic data and produce safe, masked samples.
- [ ] I can protect schemas, contracts, and metrics with regression tests.
- [ ] I can build non-flaky end-to-end and post-deployment smoke tests.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| pytest documentation — fixtures, parametrisation, markers, and plugins such as `pytest-xdist` | 01, 03, 07 |
| pandas, Polars, and PySpark testing API documentation | 01, 02 |
| Testcontainers for Python documentation | 03 |
| Hypothesis documentation — strategies, settings, stateful testing, and the pandas extra; Polars parametric testing; Pandera data synthesis | 04 |
| Faker documentation | 05 |
| `syrupy` and `pytest-recording` documentation | 02, 03, 06 |
| *Python Testing with pytest*, 2nd edition — Brian Okken (Pragmatic Bookshelf) | 01, 03, 07 |
| *Unit Testing: Principles, Practices, and Patterns* — Vladimir Khorikov (Manning) | 01, 06 |
| Martin Fowler — articles on the test pyramid, contract tests, and eradicating non-determinism in tests | 06, 07 |
| *Data Quality Fundamentals* — Barr Moses, Lior Gavish, Molly Vorwerck (O'Reilly), sections on testing vs monitoring | Overview, 06 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Post-deployment checks, canaries, and the boundary with monitoring; masking and PII rules | 2.20 Observability, Lineage, Governance, and Security |
| Performance and benchmark tests with large test-data tiers | 2.21 Performance, Scaling, and Cost Optimization |
| Testing data APIs, feature pipelines, and AI data pipelines | 2.22 Serving Data for Analytics, ML, and AI |

In data engineering, the worst bugs do not crash — they quietly produce
believable numbers. The habits you build here — name the bug before
writing the test, keep fixtures tiny and explicit, compare exactly where it
matters, test invariants instead of examples, never use real personal data,
turn every incident into a test, and refuse to tolerate flaky tests — are
what let a team change a data platform daily and still trust its numbers.
