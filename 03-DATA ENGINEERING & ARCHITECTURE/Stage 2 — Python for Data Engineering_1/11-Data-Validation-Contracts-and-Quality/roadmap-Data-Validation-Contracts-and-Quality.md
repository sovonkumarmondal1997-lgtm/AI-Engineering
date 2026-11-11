# Roadmap — Module 2.11: Data Validation, Contracts, and Quality

This is the learning roadmap for the eleventh module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about data
validation, data contracts, and data quality, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

A pipeline that runs successfully but publishes wrong data is worse than a
pipeline that fails: nobody notices, decisions are made on bad numbers, ML
models learn from corrupted features, and trust in the data team collapses
the first time a director finds the error before you do. Throughout Stage 2
you have added small checks — row counts, assertion queries, quarantine
folders, freshness checks. This module turns them into a **deliberate,
layered quality system**: validating records at the boundary, validating
DataFrames in transformations, declaring checks on tables, agreeing
contracts with producers, controlling schema change, handling bad records,
detecting anomalies, and reconciling every load.

---

## 1. Module outcome

By the end of this module you will be able to:

- Describe data quality with standard **dimensions** (completeness,
  validity, accuracy, consistency, uniqueness, timeliness, integrity) and
  turn each into measurable checks.
- Validate and serialise records with **Pydantic v2** models, validators,
  and bulk validation at ingestion boundaries.
- Validate **DataFrames** (pandas and Polars) with **Pandera** schemas,
  including lazy validation that reports every failure.
- Declare table-level checks with **Great Expectations** and **Soda**, and
  run them as pipeline gates with readable reports.
- Write and enforce **data contracts** with producers: schema, semantics,
  quality rules, SLAs, ownership, and versioning.
- Classify **schema changes** as compatible or breaking, choose
  compatibility modes, and detect breaking changes automatically.
- Design **quarantine and dead-letter** handling, thresholds, and replay —
  and the **write–audit–publish** pattern.
- Detect **volume, freshness, schema, and distribution anomalies** with
  baselines and statistical tests, without drowning in alerts.
- **Reconcile** loads between systems and layers with counts, sums,
  hashes, and audit tables.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.10. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Preconditions, postconditions, edge cases | Stage 1 — Module 1.1 | Validation rules are preconditions on data |
| Exceptions, validation, useful errors | Stage 1 — Module 1.3 | Clear, actionable validation errors |
| Environment configuration and input validation | Stage 1 — Module 1.5 | Configuration validation is **not** re-taught; this module validates data |
| Semantic versioning | Stage 1 — Module 1.6 | Versioning contracts and schemas |
| pytest, boundary and regression tests | Stage 1 — Module 1.7 | Testing validators and checks |
| Dataclasses and data models, enums | Stage 1 — Modules 1.8–1.9 | Pydantic builds on the same ideas |
| Freshness SLAs, medallion layers | Stage 2 — Module 2.1 | Where each check runs and what it protects |
| pandas and Polars schemas, `validate=` on joins, dtypes | Stage 2 — Modules 2.3–2.4 | Pandera validates these frames |
| Avro schema resolution, nested data, control totals | Stage 2 — Module 2.5 | File-level schema mechanics are **not** re-taught |
| Assertion queries, `EXCEPT` comparisons, constraints | Stage 2 — Module 2.6 | SQL reconciliation techniques are reused, not re-taught |
| Grain, keys, tracking plans | Stage 2 — Module 2.8 | Contracts and uniqueness checks depend on them |
| Source contracts, raw landing, dlt schema contracts | Stage 2 — Module 2.9 | This module formalises and enforces them |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add pydantic "pandera[polars]"
  pandas polars duckdb pyarrow great-expectations scipy pytest`.
- **Soda Core** with the connector for your engine (for example DuckDB or
  PostgreSQL) — check the current package names in the Soda documentation.
- A data contract CLI (for example `datacontract-cli`) for Topic 05.
- PostgreSQL and MinIO in Docker from earlier modules.
- Your **orders pipeline** from earlier modules (bronze → silver → gold) as
  the system you add quality controls to — or a freshly generated one with
  realistic defects.

**A note on tool churn:** data quality tools change quickly (Great
Expectations changed its API substantially at version 1.0; Soda and data
contract tooling evolve every year). Learn the **concepts** from this
roadmap and check the **current syntax** in each tool's documentation.

---

## 3. How the module is organised

The nine topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — What Quality Means                     (Basics)
  01 Data quality dimensions

Phase B — Validation Tools by Layer              (Basics → Intermediate)
  02 Pydantic: models, validators, and serialization      (records)
  03 DataFrame schema validation with Pandera             (DataFrames)
  04 Declarative checks with Great Expectations and Soda  (tables)

Phase C — Agreements and Change                  (Intermediate → Advanced)
  05 Data contracts and producer ownership
  06 Schema evolution and compatibility rules

Phase D — Operating Quality in Production         (Advanced)
  07 Quarantine, dead-letter, and bad-record handling
  08 Volume, freshness, and distribution anomaly checks
  09 Reconciliation and row-count audits

Consolidate
  practice-questions.md
  Module mini-project: a layered data quality system
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09
what    record  frame  table   agree   manage  handle  detect   prove
"good"  checks  checks checks  with    change  failures the      nothing
means                          producers                unknown  was lost
```

Why this order:

- Dimensions (01) give you the language to decide what to check anywhere.
- Tools go from the smallest unit to the largest: a record (02), a
  DataFrame (03), a table or dataset (04).
- Contracts (05) combine those checks into an agreement with the producer;
  schema evolution (06) governs how that agreement changes.
- Once checks exist, you need to decide what happens when they fail (07),
  catch problems no rule anticipated (08), and prove completeness end to
  end (09).

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — quality dimensions · Topic 02 — Pydantic |
| 2 | Topic 03 — Pandera · Topic 04 — Great Expectations and Soda |
| 3 | Topic 05 — data contracts · Topic 06 — schema evolution · Topic 07 — quarantine |
| 4 | Topic 08 — anomaly checks · Topic 09 — reconciliation · practice questions · mini-project |

---

## 5. How to study every topic (the quality loop)

```text
Read → Find the failure mode → Write the rule → Decide severity & action
→ Implement the check → Inject defects → Confirm it catches them
→ Confirm it does not cry wolf → Measure cost → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Find the failure mode** first: what could go wrong with this data, and
   who would be hurt? Every check exists to catch a specific failure.
3. **Write the rule** in plain English ("every order has exactly one
   customer that exists in `dim_customer`").
4. **Decide severity and action**: warn, quarantine the record, fail the
   batch, or block publishing — and who is alerted.
5. **Implement the check** with the topic's tool.
6. **Inject defects** on purpose: nulls, duplicates, wrong types, invalid
   values, missing partitions, late data, schema changes, volume drops.
7. **Confirm it catches them**, with an error message that tells a tired
   on-call engineer what is wrong and where.
8. **Confirm it does not cry wolf** on normal data, including weekends,
   holidays, and month-ends.
9. **Measure the cost**: runtime added to the pipeline and compute used.
10. **Write down** the rule and its rationale in `module-2.11-notes.md`.
11. **Explain aloud** which failure the check prevents and why its severity
    is right.

Keep one `quality_lab/` `uv` project:

```text
quality_lab/
├── contracts/            # data contracts (YAML) per dataset
├── src/quality_lab/      # models, schemas, checks, quarantine, monitors, recon
├── gx/ and soda/         # tool configurations and suites
├── defects/              # scripts that inject each kind of defect
├── metrics/              # history of quality metrics (Parquet or DuckDB)
└── tests/
```

---

## 6. Phase A — What Quality Means (Basics)

### Topic 01 — [Data quality dimensions](01-data-quality-dimensions.md)

**Why it comes first:** "The data is bad" is not actionable. Quality
dimensions turn vague complaints into specific, measurable properties.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Quality as **fitness for use**: the same data can be good enough for one consumer and not for another |
| Basics | Core dimensions: **completeness** (required values present, all records present), **validity** (types, formats, ranges, allowed values), **uniqueness** (no duplicate keys), **consistency** (agreement across fields, tables, and systems), **accuracy** (matches reality), **timeliness / freshness** (available when needed), **integrity** (relationships hold) |
| Basics | Examples of each dimension for orders, customers, and events |
| Intermediate | Turning dimensions into **checks** and **metrics** (e.g. "null rate of `email` < 1%", "0 duplicate `order_id`s") |
| Intermediate | Where checks run: at the source boundary, in bronze → silver, in silver → gold, and on published data — and what each location can and cannot catch |
| Intermediate | **Severity levels** (info, warn, error, critical) and **actions** (log, alert, quarantine, fail, block publish) |
| Intermediate | Known unknowns (rules you can write) vs unknown unknowns (anomalies you cannot predict — Topic 08) |
| Advanced | The cost of bad data vs the cost of checks; prioritising by consumer impact (critical datasets first — dataset tiering from Module 2.1) |
| Advanced | Quality ownership: producers, data engineers, and consumers — who fixes what |
| Advanced | Quality scorecards and SLOs for quality (e.g. "99.5% of daily loads pass all critical checks") |
| Advanced | Accuracy is the hardest dimension: checking against reference data, samples, and business sign-off |

**How to learn it**

1. Read the topic file.
2. Collect ten real data incidents (from your own experience, public
   post-mortems, or invented but realistic ones) and classify each by
   dimension.
3. For your orders dataset, write at least 25 rules covering every
   dimension, each with a severity and action.

**Hands-on exercise — `quality_rules/`**

1. Write a `rules.yaml` catalogue for the orders pipeline: rule id,
   dimension, dataset, column(s), plain-English description, severity,
   action, and owner.
2. Implement the rules as plain pandas/Polars/DuckDB functions (no quality
   frameworks yet) that return pass/fail and a metric value.
3. Run them against clean data and against data with injected defects;
   produce a simple scorecard per dimension.
4. Save results to a `quality_results` table (run id, rule id, metric,
   status, timestamp) — you will reuse it for history in Topic 08.

**Checkpoint — you are ready to move on when you can:**

- [ ] Name and explain seven quality dimensions with examples.
- [ ] Turn a vague requirement into measurable rules.
- [ ] Assign severity and action to a rule and justify them.
- [ ] Explain where in a pipeline each kind of check belongs.

**Common mistakes:** checking only what is easy (not-null) instead of what
matters; every rule at the same severity; checks with no owner or action;
treating "the pipeline succeeded" as "the data is correct".

---

## 7. Phase B — Validation Tools by Layer (Basics → Intermediate)

### Topic 02 — [Pydantic: models, validators, and serialization](02-pydantic-models-validators-and-serialization.md)

**Why here:** The first place to catch bad data is the boundary where it
enters: API responses, webhook payloads, messages, and configuration of
data. Pydantic validates individual records with Python types.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `BaseModel`, type annotations, required vs optional fields, defaults |
| Basics | Validating data: `Model.model_validate(dict)`, `Model.model_validate_json(str)`; reading `ValidationError.errors()` |
| Basics | Constraints with `Field(...)` and `Annotated` types: `gt`, `ge`, `max_length`, `pattern`; `Literal` and `Enum` for allowed values |
| Intermediate | **Coercion**: lax mode (e.g. `"42"` → `42`) vs **strict** mode — and when silent coercion hides source problems |
| Intermediate | Useful types: `Decimal`, `AwareDatetime` (timezone required), `UUID`, `EmailStr`, `HttpUrl`, nested models, lists of models |
| Intermediate | **Validators**: `@field_validator` (one field), `@model_validator` (cross-field rules, e.g. `shipped_at >= ordered_at`), `mode="before"` vs `"after"` |
| Intermediate | `model_config = ConfigDict(extra="forbid" \| "ignore" \| "allow", frozen=True, str_strip_whitespace=True)` — deciding what to do with unexpected fields |
| Intermediate | **Serialisation**: `model_dump()`, `model_dump_json()`, aliases (source names vs internal names), `@field_serializer`, `exclude` for sensitive fields |
| Advanced | **Discriminated unions** for heterogeneous events (`event_type` decides the model) |
| Advanced | **Bulk validation** with `TypeAdapter(list[Model])` and `validate_json` for speed; measuring records per second; when row-level validation is too slow and DataFrame validation (Topic 03) is better |
| Advanced | Collecting errors per record instead of failing the whole batch — feeding the quarantine pattern (Topic 07) |
| Advanced | Generating **JSON Schema** from models (`model_json_schema()`) as a machine-readable contract (Topic 05) |
| Advanced | Separating external payload models from internal domain models and database models (the ORM caveat from Module 2.7) |

**How to learn it**

1. Read the topic file.
2. Write models for three payloads from Module 2.9 (API customers, webhook
   payment events, SFTP records) and validate 100 real or generated
   examples of each, including broken ones.
3. Compare lax and strict mode on the same inputs and list every silent
   coercion.

**Hands-on exercise — `record_validation.py`**

1. Model `Order` with nested `OrderLine` items: positive quantities,
   `Decimal` prices with two decimal places, allowed currencies, a
   timezone-aware `created_at`, and a model validator checking that the
   order total equals the sum of its lines.
2. Model payment webhook events as a discriminated union of
   `PaymentSucceeded`, `PaymentFailed`, and `RefundIssued`.
3. Validate 1 million JSON records in bulk with `TypeAdapter`; route each
   invalid record with its error list to a quarantine file; measure
   records per second.
4. Serialise valid orders to JSON Lines using internal field names,
   excluding a sensitive field.
5. Export the models' JSON Schemas to `contracts/`.
6. Test every rule with valid, boundary, and invalid examples.

**Checkpoint:**

- [ ] Write Pydantic models with constraints, nested models, and
      validators.
- [ ] Explain lax vs strict mode and choose one for a boundary.
- [ ] Validate large batches efficiently and collect per-record errors.
- [ ] Use discriminated unions for multiple event types.
- [ ] Generate JSON Schema from a model.

**Common mistakes:** accepting silent coercion from sources you do not
control; naive datetimes; `extra="allow"` everywhere so new fields go
unnoticed; row-by-row Pydantic validation on 100-million-row tables.

---

### Topic 03 — [DataFrame schema validation with Pandera](03-dataframe-schema-validation-with-pandera.md)

**Why here:** Inside transformations, data lives in DataFrames. Validating
row by row is slow; Pandera validates whole columns at once and fits
naturally into `pipe` chains and function boundaries.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Schemas as code: `DataFrameSchema` with `Column(dtype, checks, nullable, unique)` and the class-based `DataFrameModel` API |
| Basics | Built-in checks: ranges (`ge`, `le`, `in_range`), allowed values (`isin`), patterns (`str_matches`), lengths, uniqueness |
| Basics | `schema.validate(df)` and reading `SchemaError` messages |
| Intermediate | `coerce=True` vs strict dtypes; `strict=True` (no unexpected columns) vs `strict="filter"` |
| Intermediate | **Lazy validation** (`lazy=True`) to collect **all** failures, and `SchemaErrors.failure_cases` as a DataFrame of bad rows and reasons |
| Intermediate | Custom checks: element-wise, column-wise, and DataFrame-wide checks (cross-column rules such as `end_date >= start_date`) |
| Intermediate | Multi-column uniqueness (composite keys) and grouped checks |
| Intermediate | Validating function inputs and outputs: `@pa.check_input`, `@pa.check_output`, `@pa.check_types` with typed DataFrames |
| Advanced | Backends: pandas, **Polars** (`pandera.polars`, including LazyFrames), and PySpark (for Module 2.14) |
| Advanced | Schema inference as a starting point (`infer_schema`) and exporting schemas to YAML — then tightening them by hand |
| Advanced | Using `failure_cases` to split a frame into valid and quarantined rows (Topic 07) |
| Advanced | Performance: validating samples vs full data, the cost of custom Python checks, and where to validate in a long pipeline |
| Advanced | Generating synthetic valid data from schemas for tests (Hypothesis strategies — Module 2.19 goes deeper) |

**How to learn it**

1. Read the topic file.
2. Infer a schema from your silver orders data, then tighten every column
   by hand and write down why.
3. Run the same schema with `lazy=False` and `lazy=True` on defective data
   and compare the outputs.

**Hands-on exercise — `frame_validation.py`**

1. Write `SilverOrders` and `GoldDailyRevenue` as `DataFrameModel`s with
   dtype, range, allowed-value, uniqueness, and cross-column checks.
2. Decorate your silver and gold transformation functions from Module 2.3
   with `@pa.check_types` so inputs and outputs are validated
   automatically.
3. Validate a defective batch lazily; split it into valid rows and a
   quarantine frame with one row per failure (column, check, value).
4. Port the silver schema to Polars and validate a LazyFrame.
5. Benchmark validation time on 10 million rows and decide which checks to
   run on full data and which on samples.
6. Test that each injected defect is caught by the expected check.

**Checkpoint:**

- [ ] Write Pandera schemas with built-in and custom checks.
- [ ] Use lazy validation and interpret `failure_cases`.
- [ ] Validate function inputs and outputs automatically.
- [ ] Validate Polars DataFrames and LazyFrames.
- [ ] Split valid and invalid rows based on validation results.

**Common mistakes:** `coerce=True` hiding type problems from sources;
failing on the first error so on-call sees one problem at a time; schemas
inferred and never reviewed; slow Python-level custom checks on huge
frames.

---

### Topic 04 — [Declarative checks with Great Expectations and Soda](04-declarative-checks-with-great-expectations-and-soda.md)

**Why here:** Pydantic and Pandera live inside Python code. Table-level
checks are often better declared in configuration, run against warehouse
tables or files, reported in human-readable form, and owned by people who
do not write Python.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Declarative checks: describe *what* must be true about a dataset; the tool figures out *how* to check it (usually by generating SQL) |
| Basics | **Great Expectations (GX Core)** concepts: data context, data sources and assets, batches, **expectations**, expectation suites, validation definitions, checkpoints and actions, and **Data Docs** (HTML reports) |
| Basics | **Soda** concepts: data source configuration and **SodaCL** checks in YAML (`row_count > 0`, `missing_count(col) = 0`, `duplicate_count(col) = 0`, `invalid_percent(col) < 1%`, `freshness(col) < 1d`, schema checks) |
| Intermediate | Common expectations/checks for each quality dimension from Topic 01 |
| Intermediate | Running checks against DuckDB, PostgreSQL, Parquet files, and DataFrames |
| Intermediate | Using results in a pipeline: pass/fail with severities, thresholds (warn vs fail), and exit codes |
| Intermediate | Storing results and building a history (and publishing reports like Data Docs for stakeholders) |
| Advanced | Custom expectations or user-defined SQL checks for business rules the built-ins do not cover |
| Advanced | Choosing a tool: GX vs Soda vs Pandera vs dbt tests (Module 2.12) vs plain SQL assertions (Module 2.6) — criteria: who writes checks, where data lives, reporting needs, runtime cost, and maintenance |
| Advanced | Awareness of other tools: Spark-oriented libraries (e.g. Deequ / PyDeequ), data observability platforms, and warehouse-native quality features |
| Advanced | Keeping checks maintainable: one suite per dataset, checks versioned in Git and reviewed like code, no duplicated rules across tools |

**How to learn it**

1. Read the topic file.
2. Implement the same ten checks on the gold orders table three ways: GX,
   Soda, and plain SQL assertions. Compare lines of configuration, output
   readability, runtime, and how failures are reported.
3. Show a GX Data Docs report or Soda scan output to someone
   non-technical and note what they understood.

**Hands-on exercise — `table_checks/`**

1. Create a GX expectation suite for `gold_daily_revenue` (row count
   range, no nulls in keys, unique `(date, country)`, revenue ≥ 0, allowed
   countries, date range) and run it with a checkpoint that fails the
   pipeline on critical failures.
2. Write the equivalent SodaCL checks for the same table plus a freshness
   check, and run a scan against DuckDB or PostgreSQL.
3. Add one custom SQL-based business-rule check to each tool.
4. Store results from both tools in your `quality_results` table.
5. Write a one-page tool decision for your team.

**Checkpoint:**

- [ ] Explain GX's core concepts and run an expectation suite.
- [ ] Write SodaCL checks and run a scan.
- [ ] Wire declarative checks into a pipeline as a gate.
- [ ] Choose between GX, Soda, Pandera, dbt tests, and SQL assertions.

**Common mistakes:** hundreds of low-value expectations nobody reads;
copying 0.x-era Great Expectations tutorials into 1.x projects; running
full-table checks on huge tables every hour when a partition would do;
spreading the same rule across three tools.

---

## 8. Phase C — Agreements and Change (Intermediate → Advanced)

### Topic 05 — [Data contracts and producer ownership](05-data-contracts-and-producer-ownership.md)

**Why here:** Most data quality problems are created upstream — by a
producer changing a field, a type, or a meaning without telling anyone.
Checks catch problems after the fact; **contracts** prevent them by making
expectations explicit and owned by the producer.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a data contract is: an agreement between a data **producer** and its **consumers** about a dataset or event stream |
| Basics | What it contains: schema (fields, types, nullability, keys), **semantics** (meaning, units, allowed values), quality rules, SLAs (freshness, availability), ownership and contacts, version, and change policy |
| Basics | Why ownership belongs with producers: they are the only ones who can prevent breaking changes |
| Intermediate | Contract formats: YAML-based standards such as the **Open Data Contract Standard (ODCS)** and the Data Contract Specification, plus JSON Schema, Avro, and Protobuf schemas as the schema part |
| Intermediate | Tooling: linting contracts, generating checks and documentation from them, and testing a dataset against its contract (e.g. with a data contract CLI) |
| Intermediate | **Enforcement points**: producer CI (block breaking changes before merge), ingestion boundaries (Pydantic, Topic 02), transformation layers (Pandera, Topic 03), published tables (GX/Soda, Topic 04), and schema registries for streams (Module 2.16) |
| Intermediate | Contracts for events: tracking plans (Module 2.8) as event contracts |
| Advanced | Contract **versioning** with semantic versioning (Stage 1): patch, minor (compatible), major (breaking) — and running two versions side by side during migration |
| Advanced | The human side: negotiating contracts, change requests, deprecation notices, and escalation when a producer breaks a contract |
| Advanced | Contracts for **consumers** too: what the data team promises downstream (gold tables, APIs), connected to SLAs from Module 2.1 |
| Advanced | Where contracts fit in data mesh and "data as a product" (Module 2.1) |
| Advanced | Pragmatism: contracts for critical datasets first; lightweight contracts beat perfect contracts nobody maintains |

**How to learn it**

1. Read the topic file.
2. Write a contract for one source you ingested in Module 2.9 and one gold
   table you publish, in a YAML standard.
3. Role-play a contract negotiation: the producer wants to rename a field;
   write the change request, the migration plan, and the deprecation
   notice.

**Hands-on exercise — `contracts/`**

1. Write contracts for three datasets: `crm_customers` (API source),
   `payment_events` (webhook events), and `gold_daily_revenue` (published
   table) — schema, semantics, quality rules, SLAs, owners, version.
2. Generate or write validation from each contract: Pydantic models for the
   two sources, and GX/Soda or contract-CLI checks for the gold table.
3. Build a "producer CI" script that compares a proposed contract with the
   current one and fails on breaking changes (you will refine the rules in
   Topic 06).
4. Break a contract on purpose (a new source version renames a field) and
   show where each enforcement point catches it.
5. Publish the contracts as readable documentation (Markdown generated
   from YAML).

**Checkpoint:**

- [ ] Explain what a data contract contains and who owns it.
- [ ] Write a contract in a standard YAML format.
- [ ] Enforce a contract at several points in a pipeline.
- [ ] Version a contract and plan a breaking change.

**Common mistakes:** contracts written by the data team alone (no
producer commitment); schema-only contracts with no semantics or SLAs;
contracts stored somewhere nobody looks; enforcing contracts only after
data has already landed in gold.

---

### Topic 06 — [Schema evolution and compatibility rules](06-schema-evolution-and-compatibility-rules.md)

**Why here:** Contracts change over time. You need precise rules for which
changes are safe for which consumers, and automation that detects unsafe
changes before they reach production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Additive changes (new optional field) vs breaking changes (removed field, renamed field, changed type, new required field) |
| Basics | Why a "harmless" rename breaks every consumer query |
| Intermediate | **Compatibility modes**: **backward** (new readers can read old data), **forward** (old readers can read new data), **full** (both), and their transitive variants (across all previous versions) — the terms used by schema registries |
| Intermediate | Which modes matter for which situations: upgrading consumers first vs producers first; long-retention data read by many schema versions |
| Intermediate | Type changes: safe widening (e.g. `int32` → `int64`, `float32` → `float64`) vs narrowing and incompatible changes; precision and scale for decimals |
| Intermediate | Nullability changes, default values, and enum changes (adding a value can break consumers with exhaustive logic) |
| Intermediate | **Semantic changes** that no schema tool can detect (units, currency, meaning of a status) — and why contracts need human review |
| Advanced | Detecting changes automatically: diffing JSON Schemas, Arrow schemas, or contract files; classifying each change; failing CI on breaking changes |
| Advanced | Handling evolution in storage: unifying schemas across Parquet files (Module 2.5), expand-and-contract migrations in databases (Module 2.7), dlt schema contracts (Module 2.9), and table-format schema evolution (Module 2.15) |
| Advanced | Migration strategies: dual-writing old and new fields, versioned datasets or topics (`orders_v2`), views that present a stable interface over a changing table |
| Advanced | Drift detection at runtime: a source's actual schema differs from its contract — alert, quarantine, or auto-evolve (and the risks of auto-evolving) |

**How to learn it**

1. Read the topic file.
2. Build a table of 20 schema changes; classify each as backward, forward,
   full, or breaking, then verify your classification with a real tool
   (Avro resolution from Module 2.5 or a schema diff library).
3. For one breaking change, write a full expand-and-contract migration
   plan across producer, pipeline, and consumers.

**Hands-on exercise — `schema_evolution.py`**

1. Write `diff_schemas(old, new) -> list[Change]` that compares two
   contracts (or Arrow schemas) and classifies every change (added,
   removed, renamed candidate, type widened, type narrowed, nullability
   changed, enum values changed) with a compatibility verdict.
2. Wire it into the producer CI script from Topic 05: minor version bumps
   may only contain compatible changes; breaking changes require a major
   version and a migration note.
3. Simulate a source adding a column, widening a type, and renaming a
   field across three daily files; handle each with a policy (accept,
   quarantine, fail) at ingestion.
4. Implement a stable consumer view over a table whose underlying column
   was renamed, using expand and contract.
5. Test the diff tool with at least 20 cases.

**Checkpoint:**

- [ ] Classify schema changes as compatible or breaking.
- [ ] Explain backward, forward, and full compatibility.
- [ ] Detect breaking changes automatically in CI.
- [ ] Plan a breaking change with expand and contract.
- [ ] Explain why semantic changes need human review.

**Common mistakes:** auto-evolving schemas without review; treating enum
additions as always safe; renaming columns in place; checking only names
and types but not meaning.

---

## 9. Phase D — Operating Quality in Production (Advanced)

### Topic 07 — [Quarantine, dead-letter, and bad-record handling](07-quarantine-dead-letter-and-bad-record-handling.md)

**Why here:** Checks now detect bad data. The next decision is what to do
with it: stop everything, drop it, fix it, or set it aside — and how to
bring it back once fixed.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Options for bad records: **fail** the batch, **drop** (almost never silently), **flag** (keep with a quality flag), **fix** (deterministic repair), **quarantine** (set aside for review) |
| Basics | Record-level vs batch-level decisions: one bad row vs a broken file |
| Basics | A **quarantine table** design: raw record, source, run id, rule id(s), error details, first seen time, status (new, fixed, replayed, discarded) |
| Intermediate | **Error thresholds**: quarantine individual bad rows but fail the batch if more than X% are bad (a sign the source itself changed) |
| Intermediate | **Dead-letter queues** in message-based and streaming pipelines: poison messages, retry counts, and moving failures aside so the stream keeps flowing (streaming implementation in Module 2.16) |
| Intermediate | **Replay**: after fixing code or data, re-processing quarantined records idempotently and marking them resolved |
| Intermediate | Alerting and ownership: who looks at quarantine, how often, and with what service level |
| Advanced | The **write–audit–publish (WAP)** pattern: write new data to a staging area or branch, run checks (audit), and publish (swap or merge) only if checks pass — so consumers never see bad data (branching in table formats — Module 2.15) |
| Advanced | Circuit breakers for data: stop downstream jobs when upstream quality fails, instead of propagating bad data |
| Advanced | Partial publishing: publish good partitions and hold back bad ones, with clear status for consumers |
| Advanced | Quarantine hygiene: retention limits, PII in quarantined records (access control and deletion — Module 2.20), and metrics on quarantine volume and age |

**How to learn it**

1. Read the topic file.
2. For ten defect scenarios, choose fail, drop, flag, fix, or quarantine,
   and justify the choice.
3. Draw the WAP flow for your gold table, marking where checks run and
   what consumers see at each step.

**Hands-on exercise — `quarantine.py`**

1. Create a quarantine table in PostgreSQL or DuckDB and a small library
   that writes failures from Pydantic (Topic 02) and Pandera (Topic 03)
   into it with the same structure.
2. Implement thresholds: a batch with 0.5% bad rows loads the good rows and
   quarantines the rest; a batch with 20% bad rows fails completely and
   alerts.
3. Implement `replay(rule_id, since)` that re-validates quarantined records
   after a fix, loads the ones that now pass, and marks them `replayed` —
   idempotently.
4. Implement WAP for `gold_daily_revenue`: write to a staging table, run
   the Topic 04 checks, and publish by atomic swap only on success.
5. Add a quarantine age metric and alert if records older than 3 days are
   unresolved.
6. Test every path: all good, some bad, mostly bad, replay after fix,
   replay twice.

**Checkpoint:**

- [ ] Choose the right action for a bad-record scenario.
- [ ] Design a quarantine table and replay process.
- [ ] Apply error thresholds at batch level.
- [ ] Implement write–audit–publish.
- [ ] Explain dead-letter queues in streaming.

**Common mistakes:** silently dropping bad rows; quarantine tables nobody
looks at; replays that duplicate data; publishing first and checking
afterwards.

---

### Topic 08 — [Volume, freshness, and distribution anomaly checks](08-volume-freshness-and-distribution-anomaly-checks.md)

**Why here:** Rules catch the problems you anticipated. Anomaly checks
catch the ones you did not: a source that quietly sends half the usual
rows, a column whose average doubles, a table that stops updating.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The main signals ("pillars" of data observability): **freshness**, **volume**, **schema**, **distribution**, and lineage (Module 2.20) |
| Basics | Freshness checks: latest event time or load time vs the SLA (Module 2.1) |
| Basics | Volume checks: row counts per run or partition vs expected ranges |
| Intermediate | Collecting **quality metrics history**: row counts, null rates, distinct counts, min/max/mean/percentiles per column per partition — stored in a metrics table |
| Intermediate | **Baselines and thresholds**: static thresholds vs dynamic ones (rolling mean ± k standard deviations, median absolute deviation, IQR) |
| Intermediate | **Seasonality**: comparing Mondays with Mondays, month-ends with month-ends; holidays and promotions |
| Intermediate | Schema change detection at runtime (new, missing, or retyped columns) |
| Advanced | **Distribution drift**: categorical shifts (share of each value, chi-square test), numeric shifts (Kolmogorov–Smirnov test, population stability index), null-rate and cardinality drift |
| Advanced | Statistical significance vs practical significance on large data (tiny shifts are "significant" with millions of rows) |
| Advanced | **Alert fatigue**: severity, grouping related alerts, snoozing known events, and reviewing precision (how many alerts were real) |
| Advanced | Cost-aware monitoring: metadata-based checks (row counts from table metadata, file counts) before expensive full scans |
| Advanced | Commercial and open-source observability tools (awareness) vs building simple monitors yourself |

**How to learn it**

1. Read the topic file.
2. Generate 180 days of daily loads with weekly seasonality, holidays, a
   gradual drift, and five injected incidents (volume drop, late load,
   null spike, category shift, a new column).
3. Try static thresholds, rolling z-scores, and same-weekday baselines, and
   count caught incidents and false alarms for each.

**Hands-on exercise — `monitors.py`**

1. Build a profiler that computes per-run metrics (row count, null rates,
   distinct counts, numeric percentiles, category shares, max event time)
   and appends them to a `quality_metrics` table.
2. Implement monitors: freshness vs SLA, volume vs same-weekday baseline,
   null-rate change, numeric drift (KS test and PSI), and category-share
   drift (chi-square).
3. Evaluate the monitors on your 180-day history: precision, recall, and
   alert count; tune thresholds and seasonality handling.
4. Add metadata-first checks (file counts and sizes on MinIO, or table
   statistics) that run before any full scan.
5. Produce a daily quality summary (Markdown or HTML) listing alerts by
   severity.

**Checkpoint:**

- [ ] Implement freshness, volume, schema, and distribution monitors.
- [ ] Build baselines that respect seasonality.
- [ ] Use KS, chi-square, or PSI for drift and interpret them sensibly.
- [ ] Tune monitors to reduce false alarms.

**Common mistakes:** static thresholds for seasonal data; alerting on every
statistically significant change; monitors without an owner; scanning
entire tables when metadata would do.

---

### Topic 09 — [Reconciliation and row-count audits](09-reconciliation-and-row-count-audits.md)

**Why last:** The final question of data quality is "did everything arrive,
exactly once, and do the totals match?" Reconciliation proves
completeness and correctness across systems and layers — and is often a
regulatory or financial requirement.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What reconciliation is: comparing counts and totals between a source and a target (or between layers) to prove nothing was lost, duplicated, or altered |
| Basics | Row-count reconciliation per run and per partition |
| Basics | **Conservation rules** across layers: `rows_in = rows_out + rows_quarantined + rows_filtered_by_rule` |
| Intermediate | Measure reconciliation: sums of amounts and quantities per day, per currency, per country — with tolerances for rounding |
| Intermediate | **Control totals** from sources (file trailers, manifest files, API totals — from Modules 2.5 and 2.9) checked on every load |
| Intermediate | Hash-based reconciliation: row hashes or aggregated hashes per partition to detect changed values, not just missing rows |
| Intermediate | An **audit table**: run id, dataset, layer, partition, counts, sums, hashes, status, and timestamps for every load |
| Advanced | Timing windows: in-flight data and late arrivals make source and target legitimately differ for a while — reconciling closed periods only, or with known lag |
| Advanced | Cross-system reconciliation: PostgreSQL source vs Parquet lake vs warehouse table, with type and precision differences |
| Advanced | Drilling down: when totals differ, narrowing from month → day → partition → key to find the exact mismatched records (reusing the SQL `EXCEPT` technique from Module 2.6) |
| Advanced | Financial-grade reconciliation: exact decimal arithmetic, sign-off processes, and audit trails that satisfy auditors |
| Advanced | Automating reconciliation as a scheduled job with reports and alerts, and treating unexplained differences as incidents |

**How to learn it**

1. Read the topic file.
2. Write conservation rules for every layer transition in your orders
   pipeline.
3. Inject four problems (a lost partition, a duplicated batch, a rounding
   error, a silently changed amount) and check which reconciliation
   method catches each.

**Hands-on exercise — `reconciliation.py`**

1. Create an `audit_log` table and record counts, sums, and partition
   hashes at every step: source extraction, bronze, silver, quarantine,
   gold.
2. Implement conservation checks between layers and fail the run when they
   do not balance.
3. Reconcile the PostgreSQL source against the Parquet lake and the
   warehouse per day and per currency, with a documented tolerance.
4. Build a drill-down tool that, given a mismatched month, finds the days,
   partitions, and finally the keys that differ.
5. Validate source control totals (file trailers, manifest counts) on
   every file load from Module 2.9.
6. Produce a reconciliation report per run and test each injected problem.

**Checkpoint:**

- [ ] Write conservation rules across pipeline layers.
- [ ] Reconcile counts, sums, and hashes between systems.
- [ ] Handle timing windows and tolerances correctly.
- [ ] Drill down from a total mismatch to the exact records.
- [ ] Maintain an audit table for every load.

**Common mistakes:** reconciling only row counts (duplicates and changed
values slip through); comparing open periods and chasing false
mismatches; float arithmetic for money; reconciliation reports nobody
reads.

---

## 10. Consolidate — practice questions

When all nine topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Identify the consumers and what bad data would cost them.
2. List failure modes and map each to a quality dimension.
3. Decide where each check runs (record, DataFrame, table, contract,
   monitor, reconciliation) and which tool implements it.
4. Assign severity and action (warn, quarantine, fail, block publish).
5. Implement the checks and inject defects to prove they work.
6. Show that normal data, including seasonal peaks, passes without false
   alarms.

---

## 11. Module mini-project — a layered data quality system

This is the proof that you have finished the module.

**Scenario:** The orders platform you built across Stage 2 (API customers,
payment webhooks, SFTP logistics files, PostgreSQL orders → bronze →
silver → gold) is trusted by finance and leadership. Last quarter it
published wrong revenue twice. You are asked to make it trustworthy.

Build `quality_platform/`, a `uv` project with:

1. **Rule catalogue** — at least 40 rules across all quality dimensions,
   each with severity, action, and owner.
2. **Contracts** — ODCS-style contracts for three sources and two
   published gold tables, versioned in Git, rendered as documentation.
3. **Boundary validation** — Pydantic models (strict where appropriate)
   for API and webhook records with bulk validation and quarantine.
4. **Transformation validation** — Pandera schemas on silver and gold
   functions with lazy validation and quarantine splitting (pandas or
   Polars).
5. **Table checks** — a GX or Soda suite per gold table, run as the audit
   step of **write–audit–publish**.
6. **Change control** — a schema-diff tool in CI that blocks breaking
   contract changes without a major version and migration note.
7. **Bad records** — a shared quarantine table, batch-level thresholds,
   replay after fixes, and quarantine age alerts.
8. **Monitoring** — a metrics history table and monitors for freshness,
   volume (seasonal), null rates, and distribution drift, evaluated on 180
   days of history with measured precision.
9. **Reconciliation** — an audit log at every layer, conservation checks,
   source-vs-lake-vs-warehouse reconciliation of revenue per day and
   currency, and a drill-down tool.
10. **Reporting** — a daily quality report (Markdown or HTML) with a
    scorecard per dimension, open alerts, quarantine status, and
    reconciliation status.
11. **Tests** — a defect-injection test suite: for every defect type, a
    test proving the right check catches it with the right severity and
    action.

**Grading yourself:** replaying last quarter's two incidents (a renamed
field upstream and a duplicated batch) is caught before publication; no
bad record is ever silently dropped; clean historical data produces no
false critical alerts; and every published number can be reconciled back
to its source.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.12 when you can tick every box without looking at your
notes:

- [ ] I can express data quality as dimensions, rules, severities, and
      actions.
- [ ] I can validate records with Pydantic, including bulk validation and
      discriminated unions.
- [ ] I can validate DataFrames with Pandera and split out failures.
- [ ] I can run declarative table checks with Great Expectations or Soda
      as pipeline gates.
- [ ] I can write, enforce, and version data contracts with producers.
- [ ] I can classify schema changes and block breaking changes in CI.
- [ ] I can quarantine, threshold, and replay bad records, and implement
      write–audit–publish.
- [ ] I can build seasonal volume, freshness, and drift monitors with few
      false alarms.
- [ ] I can reconcile data across systems and layers with an audit trail.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Pydantic documentation (v2) — models, validators, strict mode, `TypeAdapter`, serialization, JSON Schema | 02 |
| Pandera documentation — DataFrame models, checks, lazy validation, Polars integration | 03 |
| Great Expectations (GX Core) documentation — expectations, validation definitions, checkpoints, Data Docs | 04 |
| Soda documentation — SodaCL reference and data source configuration | 04 |
| Open Data Contract Standard (Bitol project) and the Data Contract Specification / `datacontract-cli` documentation | 05, 06 |
| Confluent documentation — schema evolution and compatibility types | 06 |
| *Data Quality Fundamentals* — Barr Moses, Lior Gavish, Molly Vorwerck (O'Reilly) | 01, 07, 08 |
| *Driving Data Quality with Data Contracts* — Andrew Jones (Packt) | 05, 06 |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, sections on data management and quality | 01, 05 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| dbt tests, idempotent merges, and replayable transformations | 2.12 Transformation Patterns and Pipeline Design |
| Quality gates and circuit breakers between tasks | 2.13 Orchestration and Workflow Management |
| Pandera and quality checks on Spark DataFrames | 2.14 Distributed Processing with PySpark |
| WAP with table branches; table-format schema evolution | 2.15 Lakehouse Table Formats |
| Schema registries and dead-letter topics | 2.16 Streaming and Event-Driven Data |
| Contract and schema-diff checks in CI | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Property-based tests and contract regression tests | 2.19 Testing Data Pipelines |
| Alerting, lineage, catalogs, and PII in quarantined data | 2.20 Observability, Lineage, Governance, and Security |
| Quality of features and training data for ML and AI | 2.22 Serving Data for Analytics, ML, and AI |

Quality is not a tool you install at the end; it is a property you design
into every layer. The habits you build here — name the failure, choose the
action, catch it as early as possible, never drop data silently, and prove
completeness with reconciliation — are what turn a data platform from
"usually right" into something people can bet decisions on.
