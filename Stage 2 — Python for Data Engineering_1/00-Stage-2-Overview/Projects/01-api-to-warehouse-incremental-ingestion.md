# Project Roadmap — API to Warehouse Incremental Ingestion

This is the end-to-end roadmap for **Stage 2 Project 01: API to Warehouse
Incremental Ingestion**. It takes you from an empty repository to a
**production-grade** ingestion service that extracts data from a
rate-limited, authenticated REST API, lands it in a data lake, and loads it
**incrementally, idempotently, and verifiably** into a warehouse.

It is written as a sequence of **milestones**. Each milestone has a goal,
the tasks to complete, the deliverables to produce, and **acceptance
criteria** you must meet before moving on. Do not skip acceptance criteria —
they are what make the project production grade rather than "a script that
worked once".

---

## 1. Why this project matters

Pulling data from SaaS and partner APIs into a warehouse is one of the most
common tasks a data engineer is hired to do — and one of the most common
sources of silent data problems. A naive implementation works on day one
and then quietly:

- misses records because of late commits and pagination gaps,
- duplicates records after every retry,
- misses deletes entirely,
- breaks when the access token expires mid-run,
- gets throttled or banned for ignoring rate limits,
- fails at 3 a.m. with nobody noticing until a director asks why the
  dashboard is flat.

This project makes you solve every one of those problems properly, once,
so that you can do it confidently for any API afterwards.

---

## 2. Project goal and scope

### Goal

Build `api_ingest`, a service that every hour:

1. Authenticates to a source REST API with OAuth 2.0.
2. Extracts **only new or changed records** for several endpoints, with
   complete pagination, rate-limit compliance, and safe retries.
3. Lands raw responses unchanged in a **bronze** zone of object storage.
4. Validates records and quarantines bad ones.
5. Loads records into warehouse **staging** tables with bulk loading and
   **merges** them idempotently into **core** tables — including deletes and
   a history-keeping (SCD Type 2) customer table.
6. Proves completeness with **reconciliation** and records every run.
7. Alerts a human when data is late, incomplete, or failing.

### In scope

- A realistic **mock source API** you build and control (so every failure
  can be reproduced), plus an optional real public API as a second source.
- Extraction, landing, validation, state management, warehouse loading,
  reconciliation, backfills, testing, packaging, scheduling, monitoring, and
  operations documentation.

### Out of scope (covered by later Stage 2 projects)

- Rich dbt marts and full Airflow + dbt ELT orchestration → **Project 03**.
- CDC from databases → **Project 02**.
- Spark and lakehouse table formats → **Project 04**.
- Streaming → **Project 05**.
- A full data-quality and observability platform → **Project 06**.

This project includes *enough* of each of those to be production grade,
but stays focused on **API ingestion**.

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.12**. The
production-hardening milestones (M10–M13) use ideas from Modules 2.13,
2.17, 2.18, 2.19, and 2.20. If you have not studied those yet, complete the
**Core track** now and return for the **Production track** later.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | Lifecycle, bronze layer, freshness SLAs |
| 2.3 / 2.4 pandas, Polars, DuckDB, Arrow | Parsing and converting records, local analysis |
| 2.5 Data formats | JSON Lines, Parquet, partitioned layouts, atomic writes |
| 2.6 SQL | `MERGE`, deduplication with window functions, SCD Type 2, transactions |
| 2.7 Python DB connectivity | psycopg, connection pools, `COPY`, transactions, Alembic |
| 2.8 Data modelling | Grain, natural and surrogate keys, SCD types |
| 2.9 Ingestion patterns | HTTP, httpx, OAuth2, pagination, rate limits, watermarks, backfills, deletes |
| 2.10 Concurrency | Bounded concurrency across endpoints and date windows |
| 2.11 Validation and quality | Pydantic, quarantine, thresholds, reconciliation |
| 2.12 Pipeline design | Run context, idempotent loads, hashing, state and checkpoints |
| 2.13 Orchestration *(production track)* | Scheduling, retries, backfills |
| 2.17 Cloud *(production track)* | Object storage, IAM, cloud warehouse |
| 2.18 Delivery *(production track)* | Docker, CI/CD, secrets, environments |
| 2.19 Testing | Unit, integration, property, and smoke tests |
| 2.20 Observability *(production track)* | Metrics, alerts, runbooks, PII handling |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M9 | A correct, tested, idempotent, incremental ingestion pipeline running locally |
| **Production track** | M10–M13 | Containerised, scheduled, monitored, CI/CD-deployed, and operable — optionally in the cloud |

**Estimated effort:** Core track 3–4 weeks; Production track 2–3 weeks
(at 8–10 hours per week).

---

## 4. The scenario

You are a data engineer at **ShopLite**, an online retailer. Its commerce
platform is a SaaS product exposing a REST API. Finance and analytics need
hourly-fresh, complete, trustworthy copies of the following in the
warehouse:

| Endpoint | Entity | Behaviour that makes it hard |
| --- | --- | --- |
| `/v1/customers` | Customers | Updated often; addresses and segments change; some customers are deleted (GDPR) |
| `/v1/products` | Products | Small catalogue; prices change; products are archived |
| `/v1/orders` | Orders (with nested line items) | High volume; statuses change for days after creation; late commits; occasional cancellations |
| `/v1/deleted_objects` | Deletion events | Lists ids of hard-deleted records since a timestamp |

### Service-level agreement (write it down in M0)

- **Freshness:** core tables reflect source changes within **2 hours**.
- **Completeness:** reconciled record counts per day match the source
  exactly after the daily reconciliation run.
- **Correctness:** no duplicate business keys in core tables; deletes are
  applied within 24 hours.
- **Availability:** a failed hourly run is retried automatically; two
  consecutive failed runs page the on-call engineer.

---

## 5. Target architecture

```text
             ┌──────────────────────────────────────┐
             │  Source: ShopLite Commerce API       │
             │  OAuth2 · cursor pagination · 429s   │
             └───────────────┬──────────────────────┘
                             │ httpx client (auth, pagination, rate limit, retries)
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ api_ingest (Python package, run per endpoint per data interval)        │
│                                                                        │
│  extract ──► land raw (bronze) ──► validate ──► stage ──► merge core   │
│     │             │                   │           │          │         │
│     │             ▼                   ▼           ▼          ▼         │
│     │     object storage        quarantine    warehouse   warehouse    │
│     │     bronze/…/*.jsonl.gz   table/files   staging.*   core.*       │
│     │                                                                  │
│     └──► state store: watermarks · run records · file manifest ◄──────┘│
└────────────────────────────────────────────────────────────────────────┘
                             │
          reconciliation · run metadata · metrics · alerts
                             │
                   scheduler (cron container or Airflow)
```

### Technology choices (defaults)

| Concern | Default (local) | Production option |
| --- | --- | --- |
| Source API | Your FastAPI mock API in Docker | Same, or a real public API |
| HTTP client | `httpx` + `tenacity` | Same |
| Raw landing | MinIO (S3 API), JSON Lines (gzip) | Amazon S3 / GCS / ADLS |
| Warehouse | PostgreSQL (acting as the warehouse) | Snowflake, BigQuery, or Redshift |
| Loading | psycopg `COPY` into staging + `MERGE` | Warehouse `COPY` / load jobs + `MERGE` |
| Schema migrations | Alembic | Alembic (PostgreSQL) or warehouse-native tooling |
| Validation | Pydantic v2 | Same |
| State store | PostgreSQL `meta` schema | Same |
| Scheduling | Container with cron-style scheduler | Airflow (Module 2.13) or Kubernetes CronJob |
| Packaging | `uv`, Docker, Docker Compose | Same + container registry |
| CI/CD | GitHub Actions | Same, with environments and OIDC |
| Infrastructure | Docker Compose | Terraform (Module 2.18) |
| Observability | Structured logs, run table, Prometheus metrics | + Grafana dashboards and alerts |

Record every choice (and its alternatives) as an **Architecture Decision
Record (ADR)** in `docs/adr/`.

---

## 6. Repository structure

Create this layout in M0 and keep it throughout:

```text
api-to-warehouse-ingestion/
├── README.md                     # what, why, how to run, how to operate
├── pyproject.toml / uv.lock
├── docker-compose.yml            # mock API, MinIO, PostgreSQL, (scheduler, Prometheus, Grafana)
├── .env.example                  # configuration template — never real secrets
├── docs/
│   ├── requirements.md           # scope, consumers, SLA
│   ├── source-contract.md        # the API contract (M1)
│   ├── architecture.md           # diagram and data flow
│   ├── data-model.md             # warehouse tables, grain, keys (M6)
│   ├── adr/                      # one file per decision
│   └── runbook.md                # operations guide (M13)
├── mock_api/                     # FastAPI mock source with failure switches (M1)
├── src/api_ingest/
│   ├── config.py                 # settings (Pydantic), per environment
│   ├── context.py                # RunContext: run_id, endpoint, data interval
│   ├── client/                   # http client, auth, pagination, rate limiting, retries
│   ├── extract/                  # endpoint extractors
│   ├── land/                     # bronze writers, manifests
│   ├── validate/                 # Pydantic models, quarantine
│   ├── load/                     # staging COPY, MERGE, SCD2, deletes
│   ├── state/                    # watermarks, run records, file registry, locks
│   ├── reconcile/                # counts and totals vs source
│   ├── observability/            # logging, metrics
│   └── cli.py                    # entry points: run, backfill, reconcile, state
├── migrations/                   # Alembic migrations for meta, staging, core, quarantine
├── tests/
│   ├── unit/  property/  integration/  e2e/
│   └── fixtures/                 # recorded API pages, builders
└── .github/workflows/            # CI/CD (M11)
```

---

## 7. Milestones overview

```text
Core track
  M0  Project framing and repository set-up
  M1  Build the mock source API and write the source contract
  M2  Build a robust API client (auth, pagination, rate limits, retries)
  M3  Land raw data in bronze (atomic, traceable, replayable)
  M4  Incremental state: watermarks, lookback, backfills
  M5  Validation and quarantine
  M6  Warehouse data model and migrations
  M7  Idempotent loading: staging, MERGE, SCD Type 2, deletes
  M8  Reconciliation and run records
  M9  Testing to production standard

Production track
  M10 Packaging, configuration, secrets, and scheduling
  M11 CI/CD and environments
  M12 Observability and alerting
  M13 Operations: runbook, chaos drills, performance, cost, and hand-over
  (M14 Optional stretch goals)
```

Each milestone builds on the previous one. Commit at the end of every
milestone with a clear message and tag (`m0`, `m1`, …) so you can show your
progress.

---

## 8. Core track

### M0 — Project framing and repository set-up

**Goal:** Know exactly what you are building, for whom, and how "done" is
measured — before writing pipeline code.

**Tasks**

1. Write `docs/requirements.md`: consumers (finance, analytics), questions
   they need answered, the SLA from Section 4, and non-goals.
2. Draw the architecture (Section 5) in `docs/architecture.md`, including
   every system, every data store, and the direction of data flow.
3. Create the repository structure, a `uv` project, Ruff, a type checker,
   pytest, and `pre-commit` hooks (lint, format, secret scanning).
4. Write `docker-compose.yml` with PostgreSQL and MinIO (health checks,
   named volumes) and an idempotent set-up service that creates the bucket
   and database schemas.
5. Write the first ADRs: choice of warehouse, landing format, state store.
6. Create `.env.example` and a `config.py` that loads settings from
   environment variables with validation.

**Deliverables:** requirements, architecture, ADRs, running local stack,
empty but runnable package with `api-ingest --help`.

**Acceptance criteria**

- [ ] `docker compose up` brings the stack to healthy from a clean clone.
- [ ] `uv run pytest` and `pre-commit run --all-files` pass.
- [ ] The SLA is written with measurable numbers.
- [ ] No secret exists in the repository.

---

### M1 — Build the mock source API and write the source contract

**Goal:** A realistic, controllable source that can reproduce every
failure a real SaaS API produces — so every later behaviour can be tested.

**Tasks**

1. Build `mock_api/` with FastAPI and a small database of generated data
   (seeded, reproducible): customers, products, orders with nested line
   items.
2. Implement the endpoints from Section 4 with:
   - **OAuth 2.0 client credentials** (`POST /oauth/token`), tokens expiring
     after a configurable time (e.g. 120 seconds);
   - **cursor pagination** (`next_cursor`, `has_more`) and a maximum page
     size;
   - **incremental filtering** with `updated_since` (and `updated_before`
     for bounded windows);
   - **rate limiting** returning `429` with `Retry-After` and rate-limit
     headers;
   - a `/v1/deleted_objects` endpoint listing hard-deleted ids.
3. Add **failure switches** controlled by an admin endpoint or environment
   variables: random `500`/`503` responses, slow responses, token revocation,
   **late commits** (records appearing with past `updated_at` values),
   duplicate records across pages, schema changes (a new field, a renamed
   field), malformed records, and a change generator that updates and
   deletes records over time.
4. Run the mock API as a container in the Compose stack.
5. Write `docs/source-contract.md`: base URL, authentication, endpoints,
   fields and types, pagination, incremental parameters, limits, how
   updates and deletes appear, expected volumes, and known quirks.

**Deliverables:** mock API container, source contract.

**Acceptance criteria**

- [ ] Every failure switch can be turned on and off and is documented.
- [ ] The generated data is reproducible from a seed.
- [ ] The source contract describes every field and every limit.
- [ ] You can explore every endpoint with `curl` using a real token.

---

### M2 — Build a robust API client

**Goal:** A reusable, well-tested client that is **complete** (never skips
a page), **polite** (never exceeds rate limits), **resilient** (survives
transient failures and token expiry), and **safe** (never logs secrets).

**Tasks**

1. Build `client/http.py`: one `httpx.Client` per run with `base_url`,
   explicit connect/read timeouts, connection limits, a descriptive
   `User-Agent`, and an event hook that logs method, path, status, and
   duration (no tokens, no query secrets).
2. Build `client/auth.py`: an `httpx.Auth` implementation of OAuth 2.0
   client credentials that caches the token, refreshes it proactively
   before expiry, and refreshes once on `401` before failing.
3. Build `client/pagination.py`: a generator yielding pages for cursor
   pagination, with guards against repeated cursors and a maximum page
   count.
4. Build `client/ratelimit.py`: a token-bucket limiter driven by
   configuration and adjusted from rate-limit headers.
5. Build `client/retry.py`: retries with `tenacity` for connection errors,
   timeouts, `429`, `500`, `502`, `503`, `504` only; honour `Retry-After`;
   exponential backoff with jitter otherwise; a maximum total retry time.
6. Add a simple **circuit breaker**: stop the run after N consecutive server
   failures and fail with a clear error.

**Deliverables:** `client/` package with unit tests using `respx` and
recorded fixtures.

**Acceptance criteria**

- [ ] A 30-minute extraction with tokens expiring every 2 minutes
      completes without errors.
- [ ] With `429`s enabled, the client never exceeds the configured rate
      and honours every `Retry-After`.
- [ ] `400`, `401` (after one refresh), `403`, `404`, and `422` are **not**
      retried.
- [ ] No token or secret appears in any log line (tested).
- [ ] Unit tests cover success, timeouts, every retryable and
      non-retryable status, token expiry, and pagination loops.

---

### M3 — Land raw data in bronze

**Goal:** Every byte received from the API is stored unchanged, traceably,
and atomically — so any downstream bug can be fixed by replaying bronze
instead of calling the API again.

**Tasks**

1. Define the bronze layout, for example:
   `s3://lake/bronze/shoplite/{endpoint}/extract_date=YYYY-MM-DD/run_id={run_id}/part-{n}.jsonl.gz`.
2. Write each page's records as JSON Lines with an **envelope**:
   `_run_id`, `_endpoint`, `_extracted_at`, `_request_params`,
   `_page_number`, and the raw record.
3. Write files **atomically**: write to a temporary key, then publish (copy
   or rename) and record the file in a **manifest** at the end of the run
   (file keys, record counts, checksums).
4. Record landed files in a `meta.landed_files` table (path, endpoint,
   run id, record count, checksum, status).
5. Build a **replay** command that re-processes bronze files for a run or
   date range without calling the API.

**Deliverables:** bronze writer, manifest format, `api-ingest replay`.

**Acceptance criteria**

- [ ] Killing a run mid-extraction never leaves a partially written file
      visible in the manifest.
- [ ] Every record in bronze can be traced to the run, endpoint, and
      request that produced it.
- [ ] Replaying a day from bronze produces exactly the same downstream
      result as the original run.

---

### M4 — Incremental state: watermarks, lookback, and backfills

**Goal:** Each run extracts exactly the records that changed — including
late commits — and state is never advanced before data is safe.

**Tasks**

1. Create `meta.watermarks` (endpoint, high-water mark, updated_at,
   run_id) and `meta.runs` (run id, endpoint, data interval, status,
   timings, counts, error).
2. Implement the **run context**: every run is for an explicit
   **data interval** `[start, end)`; no `now()` inside extraction logic.
3. Extract with `updated_since = watermark − lookback` and
   `updated_before = interval_end`; choose the lookback from measured
   lateness in the mock API and document it in an ADR.
4. Advance the watermark **only after** landing, validation, and loading
   have committed successfully.
5. **Deduplicate** overlaps (same id and `updated_at`) later in staging
   (M7) — do not try to avoid duplicates by tightening boundaries.
6. Extract **deletes** from `/v1/deleted_objects` with its own watermark.
7. Implement `api-ingest backfill --endpoint orders --start ... --end ...
   --window 1d`, running windows with **bounded concurrency** (Module 2.10)
   that respects the shared rate limit.
8. Prevent overlapping runs for the same endpoint with a PostgreSQL
   **advisory lock**.

**Deliverables:** state tables, incremental extractors, backfill command.

**Acceptance criteria**

- [ ] With late commits enabled, no record is missed over 7 simulated
      days.
- [ ] Crashing after landing but before the watermark update causes no gap
      and no duplicate in core tables after the next run.
- [ ] A 90-day backfill completes within rate limits and produces the same
      result as 90 daily runs.
- [ ] Two simultaneous runs for the same endpoint cannot both proceed.
- [ ] The first-ever run (no watermark) performs a full initial load.

---

### M5 — Validation and quarantine

**Goal:** Bad records never reach core tables, are never silently dropped,
and can be replayed after a fix.

**Tasks**

1. Write **Pydantic v2** models for customers, products, orders, and line
   items: types, constraints (non-negative amounts, allowed currencies and
   statuses), timezone-aware timestamps, a model validator (order total
   equals the sum of its lines within tolerance).
2. Decide lax vs strict validation per field and record the decision.
3. Decide how to handle **unknown fields** (log and keep in a raw JSON
   column vs reject) and document it in the source contract.
4. Validate in bulk with `TypeAdapter`; write invalid records with their
   errors, run id, and raw payload to `quarantine.records`.
5. Apply **batch thresholds**: load valid records when fewer than, say, 1%
   are invalid; fail the run and alert when more are invalid (a sign the
   source changed).
6. Build `api-ingest quarantine replay --rule ... --since ...` to
   re-validate and load quarantined records after a fix.

**Deliverables:** validation models, quarantine table, threshold logic,
replay command.

**Acceptance criteria**

- [ ] Every malformed record injected by the mock API ends up in
      quarantine with a readable reason.
- [ ] A schema change (renamed field) fails the run clearly instead of
      loading NULLs.
- [ ] `records_extracted = records_valid + records_quarantined` for every
      run.
- [ ] Replaying quarantine after a fix loads the records exactly once.

---

### M6 — Warehouse data model and migrations

**Goal:** A clear, documented warehouse model with known grain and keys for
every table, managed by migrations.

**Tasks**

1. Design schemas and tables in `docs/data-model.md`:

   | Schema.table | Grain | Keys | Notes |
   | --- | --- | --- | --- |
   | `staging.<endpoint>_<run_id>` or `staging.<endpoint>` | one row per extracted record version | none enforced | transient, per run |
   | `core.products` | one row per product | natural key `product_id` | SCD Type 1, `is_deleted` |
   | `core.orders` | one row per order | `order_id` | SCD Type 1, status history optional |
   | `core.order_lines` | one row per order line | `(order_id, line_number)` | replaced per order on change |
   | `core.customers_history` | one row per customer version | surrogate `customer_key`, durable `customer_id` | **SCD Type 2** with `valid_from`, `valid_to`, `is_current` |
   | `core.customers` | one row per customer (current) | `customer_id` | view or table over history |
   | `meta.*`, `quarantine.*` | — | — | state, runs, landed files, quarantine |

2. Add metadata columns to every core table: `_source_updated_at`,
   `_loaded_at`, `_run_id`, `_hash_diff`.
3. Choose types deliberately (`NUMERIC` for money, `TIMESTAMPTZ` for times,
   `BIGINT` ids) and add constraints (primary keys, `NOT NULL`, `CHECK`).
4. Create everything with **Alembic** migrations; test upgrade and
   downgrade.
5. Decide which columns contain **personal data** (names, emails, phone
   numbers, addresses) and how they are protected (for example, a
   pseudonymised email for analytics, raw values restricted — Module 2.20).

**Deliverables:** data model document, migrations, PII classification.

**Acceptance criteria**

- [ ] Every table has a written grain and key.
- [ ] Migrations upgrade from empty and downgrade cleanly.
- [ ] Personal data columns are identified and have a protection decision.

---

### M7 — Idempotent loading: staging, MERGE, SCD Type 2, and deletes

**Goal:** Loading the same data once, twice, or after a crash always
produces the same, correct core tables.

**Tasks**

1. Load validated records into **staging** with `COPY` (psycopg) in one
   transaction per endpoint and run; flatten nested line items into their
   own staging table (Module 2.5).
2. **Deduplicate** in SQL: keep the latest version per business key by
   `updated_at` with a deterministic tie-breaker (`ROW_NUMBER`).
3. Compute `_hash_diff` over business attributes (not metadata) with a
   documented canonical format (Module 2.12).
4. **MERGE** into core tables:
   - products and orders: insert new, update only when `_hash_diff`
     changed **and** the incoming `updated_at` is newer (version guard
     against out-of-order data);
   - order lines: replace the lines of each changed order within the same
     transaction;
   - customers: **SCD Type 2** — expire the current version and insert the
     new version in one transaction, only when tracked attributes change.
5. Apply **deletes** from `deleted_objects`: soft-delete (`is_deleted`,
   `deleted_at`) in core tables, and for GDPR customer deletions remove or
   pseudonymise personal data according to your M6 decision.
6. Wrap staging load, merge, and state update so that a failure at any point
   leaves core tables unchanged or fully updated, never half-updated.
7. Log inserted, updated, unchanged, and deleted counts per run.

**Deliverables:** loader package, SQL for merges, delete handling.

**Acceptance criteria**

- [ ] Running the same run twice leaves core tables byte-for-byte identical
      (checked with a table hash).
- [ ] Out-of-order updates never overwrite newer data.
- [ ] `core.customers_history` has exactly one current row per customer
      and no overlapping validity ranges (assertion queries).
- [ ] Deleted records are marked deleted within one run of appearing in
      `deleted_objects`.
- [ ] Killing the process at any step leaves core tables consistent.

---

### M8 — Reconciliation and run records

**Goal:** Prove, every day, that the warehouse contains exactly what the
source contains — and keep an auditable history of every run.

**Tasks**

1. Record per run in `meta.runs`: records extracted, landed, valid,
   quarantined, inserted, updated, unchanged, deleted, pages, requests,
   retries, `429`s, duration, watermark before and after, code version
   (git SHA).
2. Implement **conservation checks** per run:
   `extracted = valid + quarantined`, `valid = inserted + updated +
   unchanged` (after deduplication counts are accounted for).
3. Implement a **daily reconciliation job**: for each endpoint and closed
   day, compare the source's counts (from a count endpoint, or a full-key
   listing) with the warehouse; for orders, also compare the sum of order
   totals per day and currency.
4. Detect **missing** and **extra** keys and report them; automatically
   trigger a targeted backfill for mismatched days (or report for manual
   action — decide and document).
5. Store results in `meta.reconciliation` and fail the job when mismatches
   exceed tolerance.

**Deliverables:** run records, conservation checks, reconciliation job and
report.

**Acceptance criteria**

- [ ] Every run has a complete record, including failures.
- [ ] Reconciliation detects an injected lost page, a duplicated batch, and
      a missed delete.
- [ ] After reconciliation and any triggered backfill, counts and totals
      match the source exactly for closed days.

---

### M9 — Testing to production standard

**Goal:** A test suite that catches the bugs that matter, runs fast, and
never fails randomly.

**Tasks**

1. **Unit tests**: client (with `respx`), pagination, auth, retry
   classification, validation models, hash canonicalisation, merge-planning
   logic — using builders and table-driven tests.
2. **Property tests** (Hypothesis): deduplication keeps one row per key;
   applying the same batch twice is idempotent; shuffled input gives the
   same result; applying a random sequence of inserts, updates, and deletes
   produces the same core table as a simple in-memory model.
3. **Integration tests** (Testcontainers or Compose): PostgreSQL migrations,
   `COPY` + `MERGE`, SCD Type 2, deletes, advisory locks, and MinIO landing.
4. **Contract tests**: recorded API responses validated against the source
   contract; a test that fails clearly when the source adds or renames a
   field.
5. **End-to-end smoke test**: start the stack, run an initial load and three
   incremental runs with failure switches on, then assert core tables equal
   the mock API's database exactly.
6. **Regression tests** for every bug you fixed during the project.
7. Keep the pull-request test suite under a time budget (for example 5
   minutes) and run it 20 times without a failure.

**Deliverables:** a layered `tests/` suite and a testing section in the
README.

**Acceptance criteria**

- [ ] Re-introducing any of these bugs fails at least one test: a missed
      page, a token not refreshed, a retry on `404`, a watermark advanced too
      early, a duplicate after rerun, an SCD overlap, an ignored delete.
- [ ] The end-to-end test proves core tables equal the source after
      failures.
- [ ] No flaky tests across 20 runs.

**At the end of M9 you have completed the Core track.** Tag the repository
`core-complete` and write a short retrospective in `docs/`.

---

## 9. Production track

### M10 — Packaging, configuration, secrets, and scheduling

**Goal:** The pipeline runs unattended on a schedule, identically on any
machine, without secrets in code.

**Tasks**

1. Build a **multi-stage Docker image** with `uv` and the lock file, a
   non-root user, and an exec-form entrypoint running `api-ingest`
   (Module 2.18).
2. Make the container handle `SIGTERM` gracefully: stop fetching, finish or
   abandon the current page cleanly, and exit non-zero without advancing
   state (Module 2.10).
3. Separate configuration per environment (`dev`, `staging`, `prod`) with
   validated settings; all secrets (API client id/secret, database
   password) read from environment variables locally and from a **secrets
   manager** in the cloud (Module 2.18).
4. **Schedule** hourly incremental runs per endpoint and a daily
   reconciliation run, using either:
   - a minimal Airflow DAG (thin tasks calling the CLI with the data
     interval, retries, pools matching the API rate limit — Module 2.13),
     **or**
   - a Kubernetes CronJob / container scheduler with `concurrencyPolicy:
     Forbid` (Module 2.18).
5. Document how to run a backfill and a quarantine replay through the
   scheduler.

**Acceptance criteria**

- [ ] The image is scanned with no critical vulnerabilities and runs as
      non-root.
- [ ] A scheduled run and a manual backfill both work without manual steps.
- [ ] A `SIGTERM` mid-run leaves no partial state and the next run recovers.
- [ ] No secret appears in the image, the repository, or logs.

---

### M11 — CI/CD and environments

**Goal:** Every change is tested automatically and deployed the same way
every time.

**Tasks**

1. **CI on pull requests** (GitHub Actions): lint, format check, type
   check, unit and property tests, integration tests with services, the
   source-contract tests, Alembic migration check, image build and scan.
2. **CD on merge**: build the image once, tag it with the git SHA, push to
   a registry, deploy to `dev` automatically, run the end-to-end smoke test,
   then promote the **same image** to `staging` and (with manual approval)
   to `prod`.
3. Run **database migrations** as an ordered deployment step before the new
   image runs.
4. Use **OIDC federation** for cloud access from CI (no stored cloud keys)
   if you deploy to the cloud (Module 2.17).
5. Pin third-party actions by commit SHA and enable branch protection with
   required checks.

**Acceptance criteria**

- [ ] A pull request that breaks any test cannot be merged.
- [ ] The exact image running in each environment is identifiable by SHA.
- [ ] A rollback to the previous image takes one action and is documented.

---

### M12 — Observability and alerting

**Goal:** You know the pipeline is healthy — or broken — before anyone
else does.

**Tasks**

1. Emit **structured JSON logs** with `run_id`, endpoint, and data
   interval on every line (Module 2.20).
2. Expose or push **metrics**: run duration, records per stage, quarantine
   rate, requests, retries, `429`s, watermark lag (now − watermark), and
   last successful run time per endpoint.
3. Build a **dashboard** per endpoint and an overview showing the SLA:
   freshness, completeness (reconciliation status), and failure rate.
4. Define **alerts** with severity, owner, and runbook link:
   - freshness SLA breached (watermark lag > 2 hours) → page;
   - two consecutive failed runs → page;
   - quarantine rate above threshold or reconciliation mismatch → ticket;
   - rate-limit exhaustion or unusual request volume → ticket.
5. Optionally add **OpenTelemetry tracing** around extraction and loading
   to see where time goes.
6. Make sure **no personal data** appears in logs, metrics labels, or
   traces (scan for it).

**Acceptance criteria**

- [ ] Every injected failure (API outage, token revocation, schema change,
      mass quarantine, missed delete) triggers the right alert or report.
- [ ] From the dashboard alone you can answer: "Is the data fresh? Is it
      complete? What failed last night and why?"
- [ ] Logs and metrics contain no personal data.

---

### M13 — Operations: runbook, chaos drills, performance, cost, and hand-over

**Goal:** Someone other than you can operate the pipeline confidently.

**Tasks**

1. Write `docs/runbook.md` covering: architecture summary; how to deploy
   and roll back; how to run, re-run, and backfill; how to replay bronze and
   quarantine; how to reset a watermark safely (with an audit record); how
   to handle each alert; how to rotate API credentials; contacts and
   escalation.
2. Run **chaos drills** and record the results:
   - kill the container at random points 20 times;
   - revoke the API token mid-run;
   - take the API down for 3 hours, then recover;
   - introduce a breaking schema change in the source;
   - run two schedulers by mistake at the same time.
   After each drill, the warehouse must equal the source after recovery.
3. **Performance**: measure records per second per endpoint; identify
   whether the API rate limit, the network, validation, or loading is the
   bottleneck; tune page sizes, concurrency, and batch sizes within the
   rate limit (Modules 2.10, 2.21).
4. **Cost** (if in the cloud): estimate monthly cost for storage, compute,
   warehouse, and data transfer; set a budget alert; apply lifecycle rules
   to old bronze files and temporary prefixes (Module 2.17).
5. **Hand-over**: a 10-minute recorded walkthrough or written guide for a
   new engineer, plus the final retrospective.

**Acceptance criteria**

- [ ] All chaos drills end with core tables equal to the source.
- [ ] Another person can run a backfill and handle an alert using only the
      runbook.
- [ ] The bottleneck is identified with evidence, and throughput is
      documented.
- [ ] Cloud costs (if any) are estimated, tagged, and capped by a budget
      alert.

---

### M14 — Optional stretch goals

Pick any that interest you:

- **Cloud warehouse**: load into Snowflake, BigQuery, or Redshift using
  stage-then-`COPY` and `MERGE`, with infrastructure created by
  **Terraform** (buckets, roles, warehouse objects, secrets).
- **Second source**: ingest a real public API (within its terms and
  limits) with link-header or offset pagination using the same framework.
- **Configuration-driven endpoints**: describe each endpoint in YAML
  (path, keys, pagination style, watermark field, load strategy) and run
  them through one engine (Module 2.12).
- **dlt comparison**: rebuild one endpoint with dlt and compare behaviour on
  late commits, deletes, and schema changes (Module 2.9).
- **Webhooks**: add a signed webhook receiver for order events and
  reconcile it with the hourly pull.
- **Lineage**: emit OpenLineage events for each run (Module 2.20).
- **dbt starter**: add dbt staging models and tests on top of the core
  tables — the starting point for Project 03.

---

## 10. Definition of done

The project is complete when **all** of the following are true:

**Correctness**

- [ ] Core tables equal the source data after any sequence of runs,
      failures, retries, backfills, and replays.
- [ ] No duplicate business keys; SCD Type 2 history is valid; deletes are
      applied.
- [ ] Daily reconciliation passes for all closed days.

**Reliability**

- [ ] Every run is idempotent and resumable; state advances only after data
      is safely loaded.
- [ ] Rate limits are respected; transient failures are retried; permanent
      failures fail fast with a clear message.
- [ ] Overlapping runs are impossible.

**Quality and security**

- [ ] Invalid records are quarantined, never silently dropped.
- [ ] No secret in code, images, or logs; personal data classified and
      protected; no personal data in telemetry.

**Engineering**

- [ ] Layered test suite passing in CI, with no flaky tests.
- [ ] Containerised, scheduled, deployed through CI/CD with promotion and
      rollback.
- [ ] Metrics, dashboards, and alerts cover freshness, completeness, and
      failures.

**Documentation**

- [ ] README, requirements, source contract, architecture, data model,
      ADRs, runbook, and retrospective are complete and accurate.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3 (0 = missing, 1 = partial, 2 = solid,
3 = excellent). A production-grade project scores **at least 2 in every
area** and **3 in Correctness and Reliability**.

| Area | What a "3" looks like |
| --- | --- |
| Correctness | Proven equality with the source under failures; reconciliation automated |
| Reliability | Idempotent, resumable, lock-protected runs; correct retry classification |
| Incremental design | Justified lookback from measured lateness; deletes handled; safe backfills |
| Data modelling | Clear grain and keys; correct SCD Type 2; deliberate types and constraints |
| Data quality | Pydantic validation, thresholds, quarantine with replay, conservation checks |
| Testing | Unit, property, integration, contract, and end-to-end tests; bug regression tests |
| Security and privacy | No secrets anywhere; PII classified and protected; least-privilege access |
| Operability | Metrics, dashboards, actionable alerts, runbook, chaos drills passed |
| Delivery | Reproducible images, CI/CD with promotion and rollback, migrations in order |
| Documentation | A new engineer can run, operate, and extend the pipeline from the docs |

---

## 12. Common pitfalls to avoid

- Using `datetime.now()` inside extraction instead of the run's data
  interval.
- Advancing the watermark before data is loaded.
- Strict `>` watermark comparisons with no lookback (loses late and
  same-timestamp records).
- Stopping pagination on a short page when the API does not guarantee full
  pages.
- Retrying `4xx` errors, or retrying without honouring `Retry-After`.
- Requesting a new OAuth token for every request.
- Transforming records before landing the raw response (no replay
  possible).
- Row-by-row `INSERT`s into the warehouse.
- `MERGE` from an undeduplicated staging table.
- Ignoring deletes because "the API only returns active records".
- Logging full request URLs or headers containing tokens.
- Tests that call the real API or depend on timing.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing and set-up · M1 mock API and source contract |
| 2 | M2 API client · M3 bronze landing |
| 3 | M4 incremental state and backfills · M5 validation and quarantine |
| 4 | M6 data model · M7 idempotent loading |
| 5 | M8 reconciliation · M9 testing → **Core track complete** |
| 6 | M10 packaging and scheduling · M11 CI/CD |
| 7 | M12 observability · M13 operations → **Production track complete** |
| 8 (optional) | M14 stretch goals |

---

## 14. What to show in a portfolio or interview

When you present this project, be ready to explain:

1. The SLA and how you measure it.
2. How the client handles token expiry, rate limits, and retries — and
   which errors it deliberately does **not** retry.
3. How you chose the lookback window and why the watermark advances last.
4. How deletes reach the warehouse.
5. How the `MERGE` stays idempotent and resistant to out-of-order data.
6. How reconciliation proved completeness, with an example mismatch you
   caught.
7. The results of your chaos drills.
8. What you would change to support 50 more endpoints (configuration-driven
   extraction, shared rate limiting, per-endpoint SLAs).

A concise README with an architecture diagram, a short demo (initial load,
failure injection, recovery, reconciliation passing), and a link to the
runbook is more convincing than any amount of code.
