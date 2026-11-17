# Roadmap — Module 2.12: Transformation Patterns and Pipeline Design

This is the learning roadmap for the twelfth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about designing
transformation pipelines, **in what order**, **how** to learn each topic,
and **how to prove to yourself** that you have learned it before you move
on.

You can now ingest data (Module 2.9), model it (Module 2.8), query it
(Module 2.6), and validate it (Module 2.11). This module is about the part
in between: the **transformation layer** that turns bronze into silver and
silver into gold, run after run, day after day, for years. The difference
between a junior and a senior data engineer shows most clearly here. A
junior writes a script that produces the right table today. A senior
designs a pipeline that produces the right table **every** day — after
retries, reruns, late data, duplicated inputs, logic changes, two-year
backfills, and new sources — while staying readable to the next engineer.

These are the patterns that make that possible: clean structure,
merge-based idempotent loads, incremental processing and backfills,
reprocessing windows for late data, deterministic hashing, safe
enrichment, configuration-driven design, resumable state — and dbt, the
most widely used tool for SQL-based transformation.

---

## 1. Module outcome

By the end of this module you will be able to:

- Structure pipeline code into extract, transform, and load layers with
  pure, deterministic, testable transformations and a clear run context.
- Choose a **load strategy** (append, partition overwrite, merge,
  delete-insert, full refresh swap) and deduplicate correctly so every run
  is idempotent.
- Design **incremental** transformations that recompute only what
  changed, and run safe **backfills** after logic changes.
- Handle **late-arriving facts and dimensions** with reprocessing windows
  sized from measured lateness, and manage restatements of published
  numbers.
- Generate **deterministic hash keys** and **hash diffs** that match across
  Python and SQL engines.
- Enrich data with **reference data and lookups** safely — point-in-time,
  without fan-out, with explicit handling of missing matches.
- Build **metadata- and configuration-driven** pipelines that scale to
  hundreds of datasets without becoming unmaintainable.
- Manage **pipeline state and checkpoints** so any multi-step pipeline can
  resume after failure with exactly-once effects.
- Build a **dbt** project with sources, models, incremental
  materialisations, snapshots, tests, unit tests, contracts, and Python
  models.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.11. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Project layout, packages, type hints | Stage 1 — Module 1.6 | Pipeline repositories are Python packages |
| Pure functions, separating side effects, dependency boundaries, layered design | Stage 1 — Module 1.8 | Applied here to pipelines, **not** re-taught |
| Configuration and env files, idempotent repeatable jobs, safe file writes | Stage 1 — Module 1.10 | Foundations of every pattern in this module |
| ETL vs ELT, medallion layers, SLAs | Stage 2 — Module 2.1 | The layers this module builds |
| pandas / Polars / DuckDB transformations, `merge_asof`, `ASOF JOIN` | Stage 2 — Modules 2.3–2.4 | The engines used for Python transformations |
| Partition overwrite, file layout, atomic outputs | Stage 2 — Module 2.5 | Physical side of loads |
| SQL `MERGE`, dedupe with `ROW_NUMBER`, SCD implementation, CTE chains | Stage 2 — Module 2.6 | SQL mechanics are **not** re-taught |
| Bulk loading and staging tables from Python | Stage 2 — Module 2.7 | Loading transformation outputs into databases |
| Grain, keys, SCD types, late-arriving dimensions (concepts), Data Vault hash keys (concepts) | Stage 2 — Module 2.8 | This module implements them |
| Watermarks, incremental extraction, extraction backfills, CDC events | Stage 2 — Module 2.9 | Extraction side is **not** re-taught; this module is the transformation side |
| Bounded parallelism, advisory locks | Stage 2 — Module 2.10 | Parallel backfills and single-run guarantees |
| Pandera, table checks, contracts, quarantine, WAP, reconciliation | Stage 2 — Module 2.11 | Quality gates inside every pattern here |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add polars pandas duckdb pyarrow
  pydantic pandera jinja2 xxhash dbt-core dbt-duckdb pytest`.
- **dbt Core** with the **DuckDB adapter** (`dbt-duckdb`) — a full dbt
  environment on your laptop, no cloud warehouse needed. Optionally the
  PostgreSQL adapter against your Docker database.
- PostgreSQL and MinIO in Docker from earlier modules.
- Your **orders platform** from Modules 2.9–2.11 (bronze data from several
  sources, quality checks) as the input to every exercise.

---

## 3. How the module is organised

The nine topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Pipeline Structure                          (Basics)
  01 Structuring extract–transform–load code

Phase B — Loading Correctly Over Time                 (Intermediate → Advanced)
  02 Deduplication and merge-based loads
  03 Incremental processing and backfills
  04 Late-arriving data and reprocessing windows

Phase C — Transformation Building Blocks              (Intermediate)
  05 Hashing for surrogate keys and change detection
  06 Lookups, enrichment, and reference data

Phase D — Pipeline Engineering at Scale               (Advanced)
  07 Metadata- and config-driven pipelines
  08 Checkpoints, pipeline state, and resumability

Phase E — Transformation Tooling                      (Intermediate → Advanced)
  09 dbt fundamentals: models, tests, and Python models

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: a production-grade transformation layer
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09
shape   load    only    handle  stable  enrich  scale   survive  the same
the     each    what    what    keys &  safely  to many  failure  patterns
code    run     changed arrives change          datasets         in dbt
        safely          late    detection
```

Why this order:

- Structure (01) comes first because every later pattern plugs into a run
  context and pure transformation steps.
- Idempotent loads (02) are required before incremental processing (03),
  and incremental processing is required before reprocessing windows for
  late data (04).
- Hashing (05) and enrichment (06) are building blocks used by the load
  patterns; they come after them so you see why stable keys and safe
  lookups matter.
- Config-driven design (07) and state management (08) are what you need
  when the patterns must run for many datasets, reliably, over time.
- dbt (09) comes last: it implements most of Topics 02–06 in SQL, and you
  will understand exactly what it does for you — and what it does not.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — structuring ETL code · Topic 02 — dedupe and merge loads |
| 2 | Topic 03 — incremental processing and backfills · Topic 04 — late data |
| 3 | Topic 05 — hashing · Topic 06 — lookups and enrichment · Topic 07 — config-driven pipelines |
| 4 | Topic 08 — state and resumability · Topic 09 — dbt (part 1: models, sources, materialisations, tests) |
| 5 | Topic 09 — dbt (part 2: incremental, snapshots, unit tests, contracts, Python models) · practice · interview practice · mini-project |

---

## 5. How to study every topic (the pipeline design loop)

```text
Read → Define the run contract → Build it → Run it twice → Run it for the past
→ Break it (retry, late data, duplicates, crash) → Verify invariants
→ Change the logic and rebuild → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Define the run contract**: inputs, outputs, grain, the **data
   interval** a run is responsible for (e.g. "orders with event date
   2025-03-14"), and the invariants that must hold after it.
3. **Build it** as pure transformation functions or SQL models plus thin
   read/write adapters.
4. **Run it twice** with the same inputs: outputs must be identical
   (idempotency).
5. **Run it for the past**: execute for an earlier interval and confirm it
   does not use "today" anywhere (determinism).
6. **Break it**: retry after a crash, feed duplicates and late records,
   change the source schema, run two copies at once.
7. **Verify invariants** with Module 2.11 checks: grain uniqueness,
   conservation of rows, reconciliation of totals.
8. **Change the logic and rebuild**: apply a business-rule change and
   rebuild history safely.
9. **Write down** the pattern and when to use it in `module-2.12-notes.md`.
10. **Explain aloud** what happens on retry, rerun, backfill, and late
    arrival.

Keep one `transform_lab/` project:

```text
transform_lab/
├── src/transform_lab/
│   ├── core/          # run context, IO adapters, state, hashing, merge utilities
│   ├── pipelines/     # bronze→silver and silver→gold pipelines
│   └── config/        # dataset definitions (from Topic 07)
├── dbt_project/       # dbt-duckdb project (Topic 09)
├── lake/              # local bronze/silver/gold Parquet (git-ignored)
└── tests/
```

---

## 6. Phase A — Pipeline Structure (Basics)

### Topic 01 — [Structuring extract–transform–load code](01-structuring-extract-transform-load-code.md)

**Why it comes first:** Every other pattern depends on a clean shape:
transformations that are pure and deterministic, I/O kept at the edges, and
every run parameterised by the interval it is responsible for.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Separating **extract**, **transform**, and **load**: readers and writers at the edges, transformations in the middle |
| Basics | Transformations as **pure functions** (DataFrame/relation in → DataFrame/relation out) — applying Stage 1's side-effect separation to data |
| Basics | Repository layout for a pipeline project: layers (`bronze`, `silver`, `gold`), shared utilities, configuration, tests |
| Intermediate | The **run context**: `run_id`, **logical date / data interval** (which data this run is for), environment, and configuration — passed in, never read from globals |
| Intermediate | **Determinism**: never calling `now()`, `random()`, or reading "latest" inside transformations; everything time-dependent comes from the data interval |
| Intermediate | Step contracts: input and output schemas validated at step boundaries (Pandera, Module 2.11) |
| Intermediate | Choosing an engine per step: SQL (DuckDB / warehouse), Polars, or pandas — and keeping the interface the same |
| Intermediate | Naming conventions for models and tables (e.g. `stg_`, `int_`, `fct_`, `dim_`) and one output table per step |
| Advanced | **Functional data engineering**: immutable, partitioned outputs; each task a pure function of its inputs and interval; re-running a task overwrites its partition |
| Advanced | Thin CLI entry points (`run --pipeline orders_silver --date 2025-03-14`) that an orchestrator (Module 2.13) can call |
| Advanced | Anti-patterns: one "god script", notebooks as production code, hidden global state, transformations that write files mid-way, mixing environment logic into business logic |
| Advanced | Designing for testability: tiny in-memory inputs for unit tests, sample partitions for integration tests (Module 2.19 goes deeper) |

**How to learn it**

1. Read the topic file.
2. Take your messiest earlier pipeline script and draw its current flow,
   marking every side effect, every hidden global, and every use of
   "now".
3. Refactor it on paper into readers, pure steps, writers, and a run
   context before touching code.

**Hands-on exercise — `pipelines/orders_silver/`**

1. Build a `RunContext` dataclass (`run_id`, `data_interval_start`,
   `data_interval_end`, `env`, `config`).
2. Implement the bronze → silver orders pipeline as: `read_bronze(ctx)` →
   pure steps (`standardise`, `cast_types`, `deduplicate_within_batch`,
   `flag_invalid`) → `write_silver(ctx, df)` that overwrites exactly one
   partition.
3. Validate the input and output of every step with Pandera.
4. Expose a CLI: `orders-silver --date YYYY-MM-DD`.
5. Prove determinism: run for a past date twice, days apart (or with a
   faked clock), and compare outputs byte for byte.
6. Unit-test each pure step on tiny frames; integration-test the full
   pipeline on one sample partition.

**Checkpoint — you are ready to move on when you can:**

- [ ] Structure a pipeline into readers, pure steps, and writers.
- [ ] Explain the data interval / logical date and why it replaces `now()`.
- [ ] Make a pipeline deterministic and partition-scoped.
- [ ] Explain functional data engineering in your own words.

**Common mistakes:** `datetime.now()` inside transformations; steps that
both transform and write; configuration read deep inside business logic;
one script that does everything and cannot be tested.

---

## 7. Phase B — Loading Correctly Over Time (Intermediate → Advanced)

### Topic 02 — [Deduplication and merge-based loads](02-deduplication-and-merge-based-loads.md)

**Why here:** Duplicates are normal in data engineering — at-least-once
delivery, retries, overlapping lookback windows, CDC replays. The load
strategy decides whether a rerun fixes the table or corrupts it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Where duplicates come from: retries, overlapping extraction windows, webhook and CDC redelivery, multiple sources for one entity |
| Basics | Exact duplicates vs business-key duplicates vs several **versions** of the same record |
| Basics | **Load strategies**: append, **partition overwrite** (insert-overwrite), **merge / upsert**, **delete + insert**, **full refresh with swap** |
| Intermediate | Choosing a strategy by data shape: immutable events (append + dedupe, or partition overwrite), mutable entities (merge), small tables (full refresh), aggregates (partition overwrite) |
| Intermediate | Deduplicating **within a batch** vs **against the target** |
| Intermediate | Choosing the winning version: sequence numbers or log positions (best), source `updated_at` (good), load time (last resort), plus deterministic tie-breakers |
| Intermediate | Applying deletes and tombstones in merges (soft vs hard delete in the target) |
| Intermediate | Merges in Python engines (Polars and DuckDB relations, anti-joins + unions) and pushing merges down to the database or warehouse (`MERGE` from Module 2.6) |
| Advanced | **Idempotency proof**: running the same load twice, or the same load after a partial failure, produces an identical table |
| Advanced | Out-of-order updates: an older version arriving after a newer one must not overwrite it (version guards in the merge condition) |
| Advanced | Merge performance: restricting the target side with partition predicates, clustering on merge keys, batching, and why whole-table merges get slower every day |
| Advanced | Deduplication windows for unbounded data (how long to remember seen keys) — the batch view here; streaming in Module 2.16 |

**How to learn it**

1. Read the topic file.
2. For eight datasets (click events, orders with status updates, customer
   profiles, daily FX rates, product catalogue, CDC stream, webhook
   payments, daily aggregates), choose a load strategy and write why.
3. Draw the target table after each of three runs for append, overwrite,
   and merge when run 2 is retried.

**Hands-on exercise — `core/loads.py`**

1. Implement `append_dedup`, `overwrite_partition`, `merge_upsert` (with
   delete handling and a version guard), and `full_refresh_swap` for
   Parquet outputs using Polars or DuckDB.
2. Load 30 days of silver orders where CDC redelivers 3% of events, some
   out of order; choose the strategy and prove the result equals a clean
   reference.
3. Run every load twice and after a simulated crash between write and
   commit; assert identical outputs.
4. Implement the same merge in PostgreSQL with `MERGE` (Module 2.6 syntax)
   and compare results with the Python version.
5. Measure merge time as the target grows; add partition pruning to the
   merge and measure again.

**Checkpoint:**

- [ ] Explain the five load strategies and when to use each.
- [ ] Choose the winning version deterministically, including ties.
- [ ] Prevent out-of-order updates from overwriting newer data.
- [ ] Prove a load is idempotent.

**Common mistakes:** append for mutable entities; deduplicating only
within a batch; "latest by load time" when the source provides a sequence;
merges that scan the whole target every run.

---

### Topic 03 — [Incremental processing and backfills](03-incremental-processing-and-backfills.md)

**Why here:** Rebuilding every table from scratch every run stops working
as data grows. Incremental transformations process only what changed —
and backfills rebuild history when logic changes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Full rebuild vs incremental transformation: cost, simplicity, and correctness |
| Basics | **Partition-based incremental**: each run processes one data interval and overwrites its output partition |
| Basics | **Watermark-based incremental** on the upstream table (e.g. `_loaded_at` in silver) — the transformation-side counterpart of Module 2.9's extraction watermarks |
| Intermediate | **Change propagation**: when upstream rows change, which downstream partitions or aggregate groups must be recomputed? (e.g. an order updated today whose event date is last week) |
| Intermediate | Incremental aggregates: additive measures can be updated incrementally; non-additive ones (distinct counts, medians) need recomputation of affected groups or approximate sketches |
| Intermediate | Dependency-aware incremental processing: silver changes → the set of affected gold partitions |
| Intermediate | **Backfills**: re-running a range of historical intervals — after a bug fix, a new column, a logic change, or a new source |
| Advanced | Safe backfill execution: bounded parallelism (Module 2.10), resource limits, not starving normal runs, writing to a separate target and swapping (blue/green tables) |
| Advanced | Versioned logic: recording which transformation version produced each partition (so you know what needs backfilling) |
| Advanced | Full-refresh escape hatches: when incremental logic is so complex that a periodic full rebuild is the correctness safety net |
| Advanced | Cost and time estimation for a backfill before running it (partitions × time per partition ÷ parallelism) |

**How to learn it**

1. Read the topic file.
2. For your gold tables, write down which upstream changes affect which
   partitions ("an order status change affects the daily revenue partition
   of its **order date**").
3. Estimate the time and cost of a 2-year backfill before running a
   30-day one and comparing.

**Hands-on exercise — `pipelines/orders_gold/`**

1. Build `gold_daily_revenue` incrementally: detect silver rows changed
   since the last run, compute the set of affected order dates, and
   recompute only those partitions.
2. Build `gold_customer_lifetime` where only affected customers are
   recomputed.
3. Write a `backfill --pipeline orders_gold --start ... --end ...
   --parallelism 4` command that processes intervals in bounded parallel,
   writes to a shadow table, validates, then swaps.
4. Record `transform_version` in every output partition's metadata; change
   the revenue logic and list the partitions that need backfilling.
5. Prove incremental output equals a full rebuild after 60 simulated days
   of changes.

**Checkpoint:**

- [ ] Choose partition- vs watermark-based incremental processing.
- [ ] Propagate upstream changes to exactly the affected downstream
      partitions.
- [ ] Run a safe, parallel, validated backfill.
- [ ] Prove incremental output equals a full rebuild.

**Common mistakes:** incremental logic that silently misses updated rows;
recomputing aggregates from only new rows for non-additive metrics;
backfills that overwrite production tables mid-way; no record of which
logic version produced which partition.

---

### Topic 04 — [Late-arriving data and reprocessing windows](04-late-arriving-data-and-reprocessing-windows.md)

**Why here:** Incremental pipelines assume data for a day arrives on that
day. It does not. Mobile events arrive days later, partners resend
corrections, and facts arrive before their dimensions.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Event time** (when it happened) vs **load time** (when you received it) — and why reports usually need event time |
| Basics | **Late-arriving facts**: records for an interval you already processed |
| Basics | **Reprocessing (lookback) windows**: every run recomputes the last N intervals, not just the latest |
| Intermediate | Measuring lateness: distribution of `load_time − event_time`, p95/p99, and choosing N from it and from cost |
| Intermediate | Partitioning by event date vs load date: trade-offs for writing, reprocessing, and querying |
| Intermediate | **Late-arriving dimensions** (implementation of the Module 2.8 concept): inserting **inferred members** for unknown keys and updating them when the real dimension row arrives, then re-keying facts if needed |
| Intermediate | Data after the window: rejecting, parking for a manual reprocess, or triggering a targeted backfill |
| Advanced | **Closing the books**: finalising periods (e.g. a month) after a cutoff; later data triggers an explicit, audited restatement |
| Advanced | **Restatements**: versioning published numbers, telling consumers what changed, and keeping previous versions for audit |
| Advanced | **Bitemporal thinking**: valid time vs transaction (knowledge) time, answering "what did we know on date X?" vs "what is true for date X?" |
| Advanced | The batch view of watermarks and allowed lateness — the streaming equivalents come in Module 2.16 |

**How to learn it**

1. Read the topic file.
2. Generate events with a realistic lateness distribution (most on time, a
   long tail up to 10 days) and plot the lateness histogram.
3. For windows of 1, 3, and 7 days, compute the share of late data
   captured and the extra compute cost.

**Hands-on exercise — `pipelines/events_daily/`**

1. Build `gold_daily_active_users` from event data partitioned by event
   date, recomputing a configurable lookback window each run.
2. Choose N from the measured lateness distribution and document the
   choice.
3. Handle data older than the window by logging it to a "late arrivals"
   table and supporting a targeted reprocess command.
4. Implement inferred members: orders arriving before their customer
   create a placeholder customer row, which is completed when the customer
   arrives; verify facts report correctly afterwards.
5. Implement month closing: after the cutoff, a restatement creates a new
   version of the month's numbers with an audit record and a consumer
   notice.
6. Test with scenarios: on-time data, late within window, late beyond
   window, dimension after fact.

**Checkpoint:**

- [ ] Explain event time vs load time.
- [ ] Size a reprocessing window from a lateness distribution.
- [ ] Handle late facts and late dimensions correctly.
- [ ] Explain closing the books and restatements.
- [ ] Explain bitemporal questions with an example.

**Common mistakes:** partitioning only by load date and reporting by event
date; a fixed "yesterday only" run; silently changing published numbers;
dropping facts whose dimension has not arrived yet.

---

## 8. Phase C — Transformation Building Blocks (Intermediate)

### Topic 05 — [Hashing for surrogate keys and change detection](05-hashing-for-surrogate-keys-and-change-detection.md)

**Why here:** Merges, SCD Type 2, Data Vault, and deduplication all need
stable keys and a cheap way to ask "did this row change?". Hashing provides
both — if done consistently.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Hash functions: deterministic, fixed-size output; cryptographic (SHA-256, SHA-1, MD5) vs non-cryptographic (xxHash, MurmurHash) |
| Basics | **Hash keys**: deterministic surrogate keys computed from business keys (no sequence table, parallel-safe, reproducible across reloads) |
| Basics | **Hash diffs**: one hash of all descriptive columns to detect changes cheaply (SCD Type 2 and Data Vault satellites) |
| Intermediate | **Canonical serialisation** before hashing: column order, delimiters, trimming and case rules, explicit **NULL tokens**, number formatting, timestamp formats and time zones, UTF-8 encoding |
| Intermediate | Getting the **same hash in Python and SQL** (e.g. Python `hashlib` vs DuckDB/PostgreSQL/warehouse functions) — and testing it |
| Intermediate | Storage: hex strings vs binary vs 64-bit integers; join performance and size trade-offs |
| Intermediate | Collision risk: the birthday bound, and choosing hash length for your row counts |
| Advanced | Change detection with hash diffs in merges: update only when the hash changed; which columns to include or exclude (metadata columns never) |
| Advanced | Schema changes and hash diffs: adding a column changes every hash — strategies to avoid mass false "changes" |
| Advanced | Other uses: deterministic sampling, hash partitioning / bucketing (Module 2.14), file and record fingerprints for deduplication |
| Advanced | Keyed hashing (HMAC with a secret) for **pseudonymisation** of identifiers — and why plain hashes of emails or phone numbers are not anonymous (privacy details in Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Hash the same record in Python and in DuckDB; change one detail at a
   time (trailing space, NULL vs empty string, timestamp precision) and
   see which ones change the hash.
3. Compute the expected number of collisions for 10⁹ rows with 32-bit,
   64-bit, and 128-bit hashes.

**Hands-on exercise — `core/hashing.py`**

1. Implement `hash_key(*business_key_parts)` and `hash_diff(row,
   columns)` with a documented canonicalisation spec (normalisation, NULL
   token, delimiter, formats).
2. Implement the same functions as SQL expressions (DuckDB and PostgreSQL)
   and write a test that compares Python and SQL hashes on 100,000 random
   rows, including NULLs, Unicode, and edge timestamps.
3. Use hash keys and hash diffs to load `dim_customer` as SCD Type 2 —
   updating only when `hash_diff` changes.
4. Add a column to the dimension and show how to avoid marking every row
   as changed.
5. Pseudonymise emails with HMAC and show why an unkeyed SHA-256 of an
   email can be reversed by lookup.

**Checkpoint:**

- [ ] Explain hash keys and hash diffs and their uses.
- [ ] Canonicalise values so Python and SQL produce the same hash.
- [ ] Estimate collision risk and choose a hash length.
- [ ] Explain why hashing is not anonymisation.

**Common mistakes:** concatenating values without delimiters (`"ab"+"c"` =
`"a"+"bc"`); NULLs collapsing into empty strings; including load
timestamps in hash diffs; different hashes for the same row in two
engines.

---

### Topic 06 — [Lookups, enrichment, and reference data](06-lookups-enrichment-and-reference-data.md)

**Why here:** Almost every silver and gold table is enriched: codes turned
into labels, amounts converted to one currency, IPs mapped to countries,
records tagged with segments. Enrichment is a join — with all the ways
joins go wrong.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Kinds of reference data: static code lists, slowly changing lookups (product categories), time-varying external data (FX rates, tax rates), calendars and holidays |
| Basics | Managing reference data: versioned files in Git (dbt seeds in Topic 09), master-data systems, and extracted reference tables |
| Basics | Enrichment joins in Polars, DuckDB, and SQL; dictionary lookups for small mappings |
| Intermediate | **Lookup key uniqueness**: validating that each lookup key matches one row, to prevent fan-out (the `validate=` habit from Module 2.3, now as a pipeline check) |
| Intermediate | **Missing matches**: unknown members, default values, flagging, quarantining, or failing — chosen per lookup; **coverage metrics** (share of rows matched) |
| Intermediate | **Point-in-time lookups**: using the reference value valid at event time (as-of joins from Modules 2.3–2.4 as a design rule) |
| Intermediate | Code mapping tables between systems (source status codes → standard statuses) and who owns them |
| Advanced | External enrichment services (geocoding, company data): caching results in a lookup table with time-to-live, rate limits (Module 2.9), and cost control |
| Advanced | Large lookups: broadcast small tables vs partitioned joins (preview of Spark in Module 2.14); lookup ordering in multi-step enrichment |
| Advanced | Entity resolution and fuzzy matching (normalised keys, similarity scores, match thresholds) — awareness and when it becomes its own project |
| Advanced | Reference data changes: effective dates, backfilling enriched history after a mapping fix (Topic 03) |

**How to learn it**

1. Read the topic file.
2. List every lookup in your orders pipeline and, for each, decide: source,
   owner, key, time-varying or not, and missing-match policy.
3. Deliberately introduce a duplicate key in a lookup table and observe the
   effect on revenue.

**Hands-on exercise — `core/enrichment.py`**

1. Build `enrich(df, lookup, key, policy)` that validates lookup-key
   uniqueness, applies the join, applies the missing-match policy
   (`unknown`, `flag`, `quarantine`, `fail`), and reports coverage.
2. Enrich orders with product categories (Type 2 dimension, point-in-time),
   FX rates (as-of join by currency and time), and a status code mapping
   table stored as a versioned CSV.
3. Add a cached "IP → country" enrichment calling your mock API with a TTL
   cache table and rate limiting.
4. Fix a wrong mapping and backfill only the affected partitions.
5. Test: duplicate lookup key (must fail), missing FX rate (per policy),
   unknown status code (per policy), coverage below threshold (alert).

**Checkpoint:**

- [ ] Prevent fan-out by validating lookup keys.
- [ ] Apply a missing-match policy and measure coverage.
- [ ] Enrich point-in-time with time-varying reference data.
- [ ] Cache external enrichment safely.

**Common mistakes:** enriching with current values when historical values
were needed; inner joins that silently drop unmatched rows; duplicate keys
in "small" lookup tables; reference data edited by hand with no history.

---

## 9. Phase D — Pipeline Engineering at Scale (Advanced)

### Topic 07 — [Metadata- and config-driven pipelines](07-metadata-and-config-driven-pipelines.md)

**Why here:** A company rarely has five pipelines; it has hundreds of
similar ones. Writing each by hand does not scale. Describing datasets as
**configuration** and running them through one well-tested engine does —
until it goes too far.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why metadata-driven: many similar datasets (same pattern, different tables, keys, and schedules) |
| Basics | Dataset definitions in YAML: source, target, keys, load strategy, partitioning, schedule, quality rules, owner |
| Basics | Validating configuration with **Pydantic** models (reusing Module 2.11) so bad config fails before any run |
| Intermediate | One generic engine applying the patterns from Topics 02–06 based on configuration |
| Intermediate | **Registry / plugin pattern**: step types registered by name (`dedupe`, `merge`, `enrich`, `hash_key`) and composed from config |
| Intermediate | **SQL templating** with Jinja: generating repetitive SQL safely — identifiers quoted and allowlisted (injection rules from Module 2.7) |
| Intermediate | Environment overlays (dev, staging, prod) and secrets kept out of config |
| Advanced | Code generation (config → generated code or SQL, reviewed in Git) vs runtime interpretation (config read at run time) — trade-offs in debuggability |
| Advanced | Metadata tables as the catalogue of pipelines: dependencies, owners, SLAs, and status (feeding orchestration in Module 2.13) |
| Advanced | Testing config-driven systems: schema validation, dry runs that print the plan, and golden tests of generated SQL |
| Advanced | **When config-driven goes wrong**: YAML becoming a programming language, too many special-case flags, and the "inner platform" effect — keeping escape hatches for custom code |

**How to learn it**

1. Read the topic file.
2. List ten datasets in your platform and find what is the same and what
   differs between them; the differences are your configuration schema.
3. Write the configuration schema before writing the engine.

**Hands-on exercise — `config/` and `core/engine.py`**

1. Define a Pydantic `DatasetConfig` (source, keys, strategy, partitioning,
   dedupe rule, lookups, quality rules, owner, SLA) and YAML files for ten
   datasets.
2. Build an engine that reads a config and runs the right sequence of
   registered steps, reusing your Topic 02–06 functions.
3. Generate repetitive staging SQL for all ten datasets from a Jinja
   template with safe identifier quoting; snapshot-test the generated SQL.
4. Add a `--dry-run` that prints the execution plan for a dataset and date
   without touching data.
5. Add one dataset that genuinely needs custom logic and implement it as a
   custom step plugin instead of adding special flags to the config.
6. Test invalid configurations (unknown strategy, missing key, bad
   identifier) and confirm they fail validation with clear messages.

**Checkpoint:**

- [ ] Design a configuration schema from the variation between datasets.
- [ ] Validate configuration before running.
- [ ] Generate SQL safely from templates.
- [ ] Explain when configuration-driven design becomes harmful.

**Common mistakes:** unvalidated YAML; string-formatted SQL templates;
dozens of boolean flags for special cases; no dry-run, so nobody knows what
a config will do.

---

### Topic 08 — [Checkpoints, pipeline state, and resumability](08-checkpoints-pipeline-state-and-resumability.md)

**Why here:** Multi-step pipelines fail in the middle. Without explicit
state, a retry either repeats expensive work or, worse, skips work that
never completed. This topic generalises the extraction checkpoints from
Modules 2.7 and 2.9 to entire transformation pipelines.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Kinds of pipeline state: watermarks, cursors, processed-file registries, **step status**, **partition status**, run records |
| Basics | Where state lives: a metadata database (preferred), files in object storage, or the orchestrator — and why state must survive the machine that ran the job |
| Basics | Resume vs restart: continuing from the last completed step vs starting over |
| Intermediate | **Step-level checkpoints**: recording each completed step with its output location and version, and skipping completed steps on retry |
| Intermediate | A **partition ledger**: one row per dataset × partition with status, row counts, logic version, and timestamps — the source of truth for "what is done" |
| Intermediate | **Committing state and data together**: update state only after output is durably written; or design steps so that repeating them is harmless |
| Intermediate | **Exactly-once effects** = at-least-once execution + idempotent steps — the practical meaning of "exactly once" in batch pipelines |
| Advanced | Preventing concurrent runs of the same pipeline and partition (advisory locks from Module 2.6, locking from Module 2.10) |
| Advanced | Invalidation: when upstream partitions are reprocessed, downstream ledger entries must become "stale" and be recomputed (connecting to Topic 03) |
| Advanced | Operational tooling: commands to inspect state, reset a watermark, mark a partition for reprocessing, and repair state safely — with an audit record |
| Advanced | State in orchestrators vs in your own metadata (preview of Module 2.13) and avoiding two conflicting sources of truth |

**How to learn it**

1. Read the topic file.
2. Take a five-step pipeline and list what must be true about state after
   a crash at each possible point.
3. Kill a pipeline at every step boundary (and in the middle of steps)
   and verify the next run's behaviour.

**Hands-on exercise — `core/state.py`**

1. Create a `partition_ledger` and a `step_runs` table in PostgreSQL or
   DuckDB.
2. Wrap your config-driven engine so each step records its completion and
   output; a retry skips completed steps and resumes at the failed one.
3. Guard runs with an advisory lock so two runs of the same dataset and
   partition cannot overlap.
4. When a silver partition is reprocessed, mark dependent gold partitions
   stale and recompute them on the next run.
5. Build a `state` CLI: `show`, `reset-watermark`, `invalidate`, and
   `rerun`, each writing an audit record.
6. Chaos test: kill the pipeline at random points 100 times; after the
   final successful run, outputs must equal a clean run.

**Checkpoint:**

- [ ] Design step-level and partition-level state.
- [ ] Commit state only after data is safe.
- [ ] Explain exactly-once effects in batch pipelines.
- [ ] Prevent concurrent runs and invalidate stale downstream partitions.
- [ ] Repair state safely with tooling.

**Common mistakes:** state stored on a local disk; advancing state before
writing data; editing state tables by hand in production; no way to know
which partitions are stale after a backfill.

---

## 10. Phase E — Transformation Tooling (Intermediate → Advanced)

### Topic 09 — [dbt fundamentals: models, tests, and Python models](09-dbt-fundamentals-models-tests-and-python-models.md)

**Why last:** dbt is the most widely used tool for SQL transformations in
warehouses and lakehouses. It implements many patterns from this module —
dependency graphs, incremental loads, snapshots, tests — in SQL. Having
built those patterns yourself, you will understand exactly what dbt does,
and where you still need your own code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What dbt is: SQL `SELECT` statements as **models**, compiled and run in dependency order against a warehouse (the "T" in ELT) |
| Basics | Project structure: `dbt_project.yml`, `profiles.yml`, `models/`, `seeds/`, `snapshots/`, `macros/`, `tests/`; adapters (here `dbt-duckdb`) |
| Basics | `ref()` and `source()`, the **DAG**, and `dbt run`, `dbt test`, `dbt build`, model selection syntax |
| Basics | **Materialisations**: `view`, `table`, `incremental`, `ephemeral` (and materialised views where supported) |
| Intermediate | Layering: **staging** (one model per source table, light cleaning) → **intermediate** → **marts** (facts and dimensions) |
| Intermediate | **Data tests**: generic (`unique`, `not_null`, `accepted_values`, `relationships`), singular SQL tests, custom generic tests, severity and thresholds (`warn_if`, `error_if`), `store_failures` |
| Intermediate | **Source freshness** checks (connecting to SLAs in Module 2.1) |
| Intermediate | **Seeds** for small reference data (Topic 06) |
| Intermediate | Jinja and **macros** for reusable SQL; packages such as `dbt_utils` (e.g. surrogate-key macros — compare with your Topic 05 spec) |
| Advanced | **Incremental models**: `is_incremental()`, `unique_key`, strategies (`append`, `merge`, `delete+insert`, `insert_overwrite`, and time-based `microbatch` in recent versions), lookback windows for late data (Topic 04), `on_schema_change`, and `--full-refresh` |
| Advanced | **Snapshots** for SCD Type 2 (timestamp vs check strategies) — compare with your hand-built versions |
| Advanced | **Unit tests** (testing model logic on mock inputs, in recent dbt versions) vs data tests |
| Advanced | **Model contracts** and model versions — enforcing column names and types on published models (data contracts from Module 2.11) |
| Advanced | **Python models** (`def model(dbt, session)`): when Python beats SQL in a dbt project, adapter support, and limits |
| Advanced | Documentation and lineage (`dbt docs`), exposures, and CI with "slim" runs of modified models only (`state:modified+`, `--defer`) — CI details in Module 2.18 |
| Advanced | What dbt does **not** do for you: extraction, orchestration beyond the DAG, non-SQL side effects, and cross-system state — the reasons you still need Modules 2.9, 2.13, and your own code |
| Advanced | Awareness of the evolving dbt ecosystem (dbt Core, managed dbt offerings, and newer engines); check the version you use against current documentation |

**How to learn it**

1. Read the topic file.
2. Work through the official dbt tutorial concepts using `dbt-duckdb`
   against your own silver Parquet data.
3. For every dbt feature you use, write which pattern from Topics 02–08 it
   implements and what it leaves to you.

**Hands-on exercise — `dbt_project/`**

1. Declare your silver Parquet datasets as **sources** with freshness
   checks; build staging models for each.
2. Build marts: `dim_customer` (via a **snapshot**), `dim_product`,
   `fct_order_lines` (**incremental**, `merge` on the order-line key with a
   3-day lookback), and `fct_daily_revenue`.
3. Add seeds for the status code mapping and country list.
4. Add data tests on every model (keys, relationships, accepted values,
   custom business rules) and **unit tests** for the revenue logic.
5. Enforce a **model contract** on `fct_daily_revenue`.
6. Write one **Python model** (e.g. a customer segmentation that is
   awkward in SQL) using the DuckDB adapter's Python support.
7. Generate docs and lineage; run `dbt build` twice and confirm
   idempotency; change a model and run only it and its descendants.
8. Compare the dbt `fct_daily_revenue` with your hand-built Topic 03
   version — they must reconcile exactly.

**Checkpoint:**

- [ ] Build a layered dbt project with sources, staging, and marts.
- [ ] Use incremental models with lookback windows correctly.
- [ ] Use snapshots for SCD Type 2.
- [ ] Write data tests, unit tests, and model contracts.
- [ ] Explain when to use a Python model and what dbt does not do.

**Common mistakes:** marts built directly on raw sources (no staging);
incremental models with no lookback for late data; tests only on
`not_null`; business logic duplicated across models instead of shared
intermediate models; treating dbt as an orchestrator for everything.

---

## 11. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Write the run contract: inputs, outputs, grain, data interval, and
   invariants.
2. Choose load strategy, incremental approach, and reprocessing window —
   with one sentence of justification each.
3. List what happens on retry, rerun, backfill, late arrival, duplicate
   input, and crash between steps.
4. Implement it (Python or dbt) and prove idempotency and determinism with
   tests.
5. Reconcile the result with a full rebuild.

### [`interview-practice.md`](interview-practice.md)

Pipeline-design questions are central to senior data engineering
interviews. Practise with a **30-minute timer**, out loud, drawing as you
go:

1. Clarify sources, volumes, freshness, consumers, and correctness needs.
2. Sketch layers and the grain of each output.
3. Choose load strategies, incremental logic, and late-data handling.
4. Explain idempotency, state, and failure recovery.
5. Describe quality gates, backfills, and how the design evolves.

Typical prompts: "make this pipeline idempotent", "daily active users with
events arriving up to 7 days late", "backfill two years after a logic bug
without downtime", "SCD Type 2 customer dimension from daily snapshots",
"deduplicate an at-least-once event stream in batch", "generate surrogate
keys across two sources", "design a framework for 300 similar ingestion
tables", "dbt incremental model vs full refresh — when and why?", and
"a job failed at step 4 of 6 — what happens on retry?".

---

## 12. Module mini-project — a production-grade transformation layer

This is the proof that you have finished the module.

**Scenario:** The orders platform ingests from several sources (Modules
2.9–2.11). Leadership wants reliable daily revenue, customer, and product
analytics; finance requires restatement control; analysts want dbt.

Build `transformation_layer/` with two parts:

**Part A — Python bronze → silver framework**

1. Config-driven engine with Pydantic-validated YAML definitions for at
   least eight bronze datasets.
2. Registered steps: standardise, cast, hash keys and hash diffs,
   deduplicate (with version guards), enrich (with missing-match policies
   and coverage metrics), and validate (Pandera).
3. Load strategies per dataset (merge, partition overwrite, append-dedupe,
   full refresh).
4. Run context with data intervals; deterministic, partition-scoped runs;
   CLI with `--date`, `--dry-run`, and `backfill`.
5. Partition ledger, step checkpoints, advisory locks, stale-partition
   invalidation, and a `state` CLI.

**Part B — dbt silver → gold project (`dbt-duckdb`)**

6. Sources with freshness, staging, intermediate, and marts layers.
7. `dim_customer` snapshot (SCD Type 2), `fct_order_lines` incremental with
   a lookback window sized from measured lateness, `fct_daily_revenue` with
   a model contract, and one Python model.
8. Data tests, unit tests, seeds for reference data, and generated docs.

**Cross-cutting**

9. Late data: late facts handled by lookback windows; late dimensions via
   inferred members; month-end closing with audited restatements.
10. Backfill: a logic change to revenue rolled out with a parallel shadow
    backfill of 12 months and an atomic swap.
11. Evidence: a chaos test (random kills), an idempotency test (double
    runs), and a reconciliation proving the incremental results equal a
    full rebuild and match source totals.

**Grading yourself:** any run can be retried, re-run, or backfilled with no
change to correct outputs; late data within the window appears in reports
automatically, and later data appears only via audited restatements; every
partition's origin (logic version, run id) is known; and a new similar
dataset can be added with configuration alone.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.13 when you can tick every box without looking at your
notes:

- [ ] I can structure pipelines with pure, deterministic,
      interval-scoped transformations.
- [ ] I can choose load strategies and prove loads idempotent.
- [ ] I can design incremental transformations and run safe backfills.
- [ ] I can handle late facts and dimensions, closing, and restatements.
- [ ] I can generate consistent hash keys and hash diffs across engines.
- [ ] I can enrich data point-in-time without fan-out and with explicit
      missing-match policies.
- [ ] I can build and test a configuration-driven pipeline engine.
- [ ] I can manage checkpoints and state for resumable, exactly-once-effect
      pipelines.
- [ ] I can build a tested, layered dbt project with incremental models,
      snapshots, contracts, and Python models.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Maxime Beauchemin — "Functional Data Engineering: a modern paradigm for batch data processing" (essay) | 01, 02, 03, 08 |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, chapter on queries, modelling, and transformation | 01, 02, 03 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapter on batch processing | 02, 03, 08 |
| *The Data Warehouse Toolkit* — Kimball and Ross, sections on late-arriving facts and dimensions | 04, 06 |
| dbt documentation — models, materialisations, incremental models and strategies, snapshots, data tests, unit tests, model contracts, Python models | 09 |
| dbt Labs — "How we structure our dbt projects" guide | 01, 09 |
| `dbt-duckdb` adapter documentation | 09 |
| Python `hashlib` / `hmac` documentation and xxHash documentation | 05 |
| Jinja documentation | 07, 09 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Run contexts, data intervals, backfills, and retries as scheduled tasks | 2.13 Orchestration and Workflow Management |
| The same patterns on distributed DataFrames; hash bucketing | 2.14 Distributed Processing with PySpark |
| `MERGE`, partition overwrite, and time travel on lakehouse tables | 2.15 Lakehouse Table Formats |
| Late data, watermarks, and deduplication in streams | 2.16 Streaming and Event-Driven Data |
| dbt on cloud warehouses | 2.17 Cloud Storage and Cloud Data Platforms |
| Slim CI for dbt and pipeline deployments | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Testing transformations and end-to-end pipelines | 2.19 Testing Data Pipelines |
| Lineage from dbt and pipelines; pseudonymisation | 2.20 Observability, Lineage, Governance, and Security |
| Compute cost of incremental vs full processing | 2.21 Performance, Scaling, and Cost Optimization |
| Semantic layers on top of dbt marts | 2.22 Serving Data for Analytics, ML, and AI |

Transformations are where business logic lives, and business logic
changes. The habits you build here — deterministic runs scoped to a data
interval, idempotent loads, explicit state, measured reprocessing windows,
and backfills that never surprise consumers — are what let a pipeline
survive years of change without losing the trust of the people who rely on
it.
