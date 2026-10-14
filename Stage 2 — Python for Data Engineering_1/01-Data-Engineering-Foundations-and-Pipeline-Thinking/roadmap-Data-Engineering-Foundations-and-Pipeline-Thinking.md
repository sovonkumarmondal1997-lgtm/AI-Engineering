# Roadmap — Module 2.1: Data Engineering Foundations and Pipeline Thinking

This is the learning roadmap for the first module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn in this module, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

This module is mostly about *thinking*, not libraries. Before you touch
pandas, Spark, Kafka, or Airflow in later modules, you need a clear mental
map of what a data platform is, where data comes from, how it moves, who
consumes it, and what "good" looks like. Every tool you learn later slots
into this map. Engineers who skip this module end up knowing many tools but
unable to explain *why* a pipeline is designed the way it is.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain, in plain English, what a data engineer builds and why the
  business pays for it.
- Draw the full lifecycle of a piece of data, from the system that creates
  it to the dashboard, model, or application that consumes it.
- Choose between **batch**, **micro-batch**, and **streaming** for a given
  requirement and defend the choice with latency, cost, and complexity
  trade-offs.
- Choose between **ETL**, **ELT**, and **reverse ETL** for a given flow.
- Tell an **OLTP** workload from an **OLAP** workload and explain why they
  need different storage and query engines.
- Compare **warehouse**, **lake**, and **lakehouse** architectures and pick
  one for a scenario.
- Design a **medallion** (bronze → silver → gold) layout for a new dataset,
  including what rules belong in each layer.
- Write measurable **SLIs, SLOs, and SLAs** for freshness, latency,
  completeness, and correctness, and map them to real data consumers.
- Produce a one-page **pipeline design document** for a realistic scenario
  — the core deliverable of this module.

---

## 2. Prerequisites

You should already be comfortable with everything from the earlier stages
of this curriculum. In particular, this module leans on:

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, files, filesystems, storage vs RAM | Stage 0 — Computer & Digital Foundation | Storage and compute trade-offs drive every architecture decision |
| Input → Process → Output, state modelling | Stage 1 — Module 1.1 | A pipeline *is* input → process → output with state (watermarks, checkpoints) |
| CSV, JSON, text files, pathlib | Stage 1 — Module 1.5 | All the hands-on exercises read and write files |
| Idempotency and repeatable jobs, safe file writes | Stage 1 — Module 1.10 | The foundation of reliable pipelines; reused in layers and reruns |
| Logging, exit codes, configuration | Stage 1 — Modules 1.5 and 1.10 | Every exercise script must behave like a production job |
| datetime, time zones, timestamps | Stage 1 — Module 1.9 | Freshness, latency, and event-time reasoning depend on correct timestamps |

If any of these feel shaky, revisit them first. This roadmap does **not**
re-teach them; it builds on them.

**Tools needed:** Python 3.12+ managed with `uv`, the standard library only
(`csv`, `json`, `sqlite3`, `pathlib`, `datetime`, `logging`), a text editor,
and a way to draw diagrams (pen and paper, Excalidraw, or Mermaid in
Markdown). No third-party data libraries are needed in this module — they
begin in Module 2.2.

---

## 3. How the module is organised

The eight topics are grouped into four phases. Each phase builds directly on
the one before it, so work through them **in order**.

```text
Phase A — The Big Picture            (Basics)
  01 What data engineers build
  02 Data lifecycle from sources to consumers

Phase B — How Data Moves             (Basics → Intermediate)
  03 Batch, micro-batch, and streaming
  04 ETL, ELT, and reverse ETL

Phase C — Where Data Lives           (Intermediate → Advanced)
  05 OLTP vs OLAP workloads
  06 Warehouse, lake, and lakehouse architectures
  07 Medallion bronze / silver / gold layers

Phase D — What "Good" Means          (Advanced)
  08 SLAs, freshness, latency, and data consumers

Consolidate
  practice-questions.md
  Module mini-project: pipeline design document
```

The dependency chain is deliberate:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08
roles   flow   timing  where    workload  platform  layering  guarantees
                       to       shape     choice    inside    to
                       transform                    platform  consumers
```

Topic 08 is last because you cannot promise a consumer "data will be at
most 2 hours old" until you understand how data moves (03, 04), where it is
stored (05, 06), and how many hops it takes through the layers (07).

---

## 4. Suggested schedule

About **3 weeks at 8–10 hours per week**. Adjust freely; finishing each
checkpoint matters more than the calendar.

| Week | Days | Work |
| --- | --- | --- |
| 1 | 1–2 | Topic 01 — What data engineers build |
| 1 | 3–4 | Topic 02 — Data lifecycle |
| 1 | 5 | Topic 03 — Batch, micro-batch, streaming |
| 2 | 1 | Topic 03 (finish) + Topic 04 — ETL / ELT / reverse ETL |
| 2 | 2–3 | Topic 05 — OLTP vs OLAP |
| 2 | 4–5 | Topic 06 — Warehouse, lake, lakehouse |
| 3 | 1–2 | Topic 07 — Medallion layers |
| 3 | 3 | Topic 08 — SLAs, freshness, latency |
| 3 | 4 | `practice-questions.md` |
| 3 | 5 | Mini-project and module self-assessment |

---

## 5. How to study every topic (the pipeline-thinking loop)

Stage 1 taught you the engineering loop for code. For data engineering
topics, use this extended loop for every idea:

```text
Read → Draw → Relate to a real system → Build a tiny version in Python
→ Break it on purpose → Measure → Decide → Write it down → Explain aloud
```

1. **Read** the topic file once, fully, without taking notes.
2. **Draw** the idea as a diagram: boxes for systems, arrows for data
   movement, labels for format, frequency, and volume.
3. **Relate** it to a real system you know (a shopping app, a bank, a
   ride-sharing app, a hospital). Name the source systems and consumers.
4. **Build a tiny version** in plain Python with only the standard library.
   Tiny means 30–150 lines.
5. **Break it on purpose** — rerun it twice, feed it a late record, a
   duplicate, a malformed row, or an empty file, and watch what happens.
6. **Measure** — how long did it take, how many rows went in and out, how
   old is the newest record in the output?
7. **Decide** — write down which option you would pick in production and
   why, including what you are giving up.
8. **Write it down** in a short decision note (the format of an
   Architecture Decision Record: context, options, decision, consequences).
9. **Explain aloud** as if to a new teammate. If you cannot, reread.

Keep one running file, `module-2.1-notes.md`, outside this folder (for
example in your own workspace). All diagrams and decision notes go there.
It becomes your mini-project input at the end.

---

## 6. Phase A — The Big Picture (Basics)

### Topic 01 — [What Data Engineers Build](01-what-data-engineers-build.md)

**Why it comes first:** You need to know the job before you learn its
tools. This topic sets the vocabulary used in every later file.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a data engineer is; the difference between data engineering, data analysis, data science, ML engineering, analytics engineering, and platform engineering; what a *pipeline*, *dataset*, *table*, and *job* are |
| Basics | The main deliverables: ingestion pipelines, transformation pipelines, curated datasets, data models, data platforms, data APIs, and internal tooling |
| Intermediate | Data as a product: owners, consumers, documentation, versioning, and quality guarantees |
| Intermediate | The "undercurrents" that run across all work: security, data management, DataOps, architecture, orchestration, and software engineering |
| Advanced | Organisational models: central data team, embedded engineers, and data mesh (domain ownership, self-serve platform, federated governance); the trade-offs of each |
| Advanced | How a data engineer's work supports ML and AI: feature pipelines, training datasets, and retrieval / embedding pipelines for LLM applications |

**How to learn it**

1. Read the topic file.
2. Pick three companies you know. For each, list five datasets they almost
   certainly have (orders, clicks, payments, …) and who would consume them.
3. Draw a one-page "data team map" showing which role owns which part of
   the flow from app database to executive dashboard.

**Hands-on exercise**

Write `role_matcher.py`: a small CLI that reads a JSON file of task
descriptions (e.g. "build a churn model", "load Stripe payments nightly",
"fix a slow dashboard query") and prints which role usually owns each task,
with a one-line reason. The point is not the code — it is forcing yourself
to make precise distinctions.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the difference between a data engineer and a data scientist
      in two sentences.
- [ ] List at least six things a data engineer builds.
- [ ] Explain "data as a product" and give one example.
- [ ] Describe one advantage and one risk of data mesh.

**Common mistakes:** thinking data engineering is "just writing SQL";
treating pipelines as one-off scripts instead of maintained products.

---

### Topic 02 — [Data Lifecycle from Sources to Consumers](02-data-lifecycle-from-sources-to-consumers.md)

**Why it comes next:** Once you know what a data engineer builds, you need
the end-to-end path every dataset follows. Topics 03–08 each zoom into one
part of this path.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The lifecycle stages: **generation → ingestion → storage → transformation → serving → consumption**, plus archival and deletion |
| Basics | Source system types: operational databases, SaaS APIs, event streams, logs, files, IoT/sensors, third-party data |
| Basics | Consumer types: BI dashboards, analysts, data scientists, ML models, applications, operational tools, regulators, LLM/RAG systems |
| Intermediate | Source characteristics that shape design: volume, velocity, variety, schema stability, update pattern (append-only vs mutable), deletes, and access method (pull vs push) |
| Intermediate | Structured, semi-structured, and unstructured data |
| Intermediate | Data contracts at the source boundary (introduced here, deepened in Module 2.11) |
| Advanced | Metadata along the lifecycle: lineage, ownership, classification (PII), and retention |
| Advanced | Where data gets lost or corrupted at each stage, and where to place checks |

**How to learn it**

1. Read the topic file.
2. Choose one scenario (for example, an e-commerce company). Draw the full
   lifecycle for **orders**: where an order is created, every hop it takes,
   and every consumer that reads it.
3. For every hop in your drawing, label: format, frequency, approximate
   volume, and who owns it.

**Hands-on exercise**

Write `lifecycle_sim.py` using only the standard library:

1. **Generate** — write 1,000 fake orders to an SQLite database
   (`source.db`) to act as the operational source.
2. **Ingest** — export them to a raw CSV or JSON file in a `landing/`
   folder, stamped with an ingestion timestamp.
3. **Transform** — read the raw file, clean it, and compute daily revenue.
4. **Serve** — write the result to `serving/daily_revenue.csv`.
5. Log the row counts at each stage and fail with a non-zero exit code if
   any stage loses rows unexpectedly.

Keep this script. You will extend it in Topics 03, 04, 07, and 08.

**Checkpoint:**

- [ ] Name the six lifecycle stages in order without looking.
- [ ] Give three source types and three consumer types, with an example of
      each.
- [ ] Explain why "does the source allow updates and deletes?" changes the
      pipeline design.
- [ ] Point to the stage in your simulation where you would add a
      row-count check, and explain why there.

**Common mistakes:** forgetting deletes and updates at the source;
designing a pipeline without asking who the consumer is.

---

## 7. Phase B — How Data Moves (Basics → Intermediate)

### Topic 03 — [Batch, Micro-Batch, and Streaming](03-batch-micro-batch-and-streaming.md)

**Why here:** The lifecycle tells you *what* hops exist; this topic decides
*how often* data moves across them. Freshness (Topic 08) depends entirely
on this choice.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Batch processing: bounded data, scheduled runs, typical latencies (minutes to days) |
| Basics | Streaming: unbounded data, continuous processing, typical latencies (milliseconds to seconds) |
| Basics | Micro-batch: small, frequent batches (seconds to minutes) — how Spark Structured Streaming works by default |
| Intermediate | Bounded vs unbounded datasets; event time vs processing time (introduction only — Module 2.16 goes deep) |
| Intermediate | Cost and complexity trade-offs: always-on compute, state management, ordering, and on-call burden |
| Intermediate | How to choose: "what decision is made with this data, and how fast must it be made?" |
| Advanced | Lambda architecture (batch layer + speed layer) and Kappa architecture (stream only, replay for reprocessing), and why many teams now avoid Lambda's duplicated logic |
| Advanced | Hybrid designs: streaming ingestion with batch transformation; unified batch/stream engines |

**How to learn it**

1. Read the topic file.
2. For ten real use cases (fraud detection, monthly finance report,
   recommendation refresh, stock ticker, payroll, website analytics, IoT
   alerts, ML training set, inventory sync, marketing email list), decide
   batch, micro-batch, or streaming. Justify each in one line.
3. Draw a Lambda and a Kappa architecture side by side.

**Hands-on exercise**

Extend `lifecycle_sim.py` with three ingestion modes selected by an
`argparse` flag:

- `--mode batch` — process everything once.
- `--mode micro-batch --interval 5` — every 5 seconds, process only rows
  newer than the last processed timestamp.
- `--mode stream` — a generator yields one order at a time, and each is
  processed immediately.

For each mode, log **end-to-end latency** (processing time minus order
creation time). Compare the latency and the number of runs per mode.

**Checkpoint:**

- [ ] Define bounded and unbounded data.
- [ ] Explain why micro-batch is not "real" streaming, and when that does
      not matter.
- [ ] Pick the right mode for five new use cases and defend each choice.
- [ ] Explain the main weakness of Lambda architecture.

**Common mistakes:** choosing streaming because it sounds modern; ignoring
the operational cost of always-on systems.

---

### Topic 04 — [ETL, ELT, and Reverse ETL](04-etl-elt-and-reverse-etl.md)

**Why here:** Now that you know *when* data moves, decide *where* the
transformation happens — before loading, after loading, or back out to
operational tools.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | ETL: transform before loading into the target |
| Basics | ELT: load raw data first, transform inside the warehouse or lakehouse with SQL (the modern default; tools like dbt, Module 2.12) |
| Basics | Reverse ETL: push modelled data from the warehouse back into operational tools (CRM, ads, support tools) |
| Intermediate | Why ELT became dominant: cheap cloud storage, elastic compute, and the value of keeping raw data for replay |
| Intermediate | When ETL is still right: PII must be removed before landing, heavy parsing of binary formats, strict target schemas |
| Intermediate | EtLT: light cleaning (dedupe, masking) before load, heavy modelling after |
| Advanced | Replayability and backfills: why keeping raw data lets you fix logic bugs later |
| Advanced | Reverse ETL risks: syncing wrong data into customer-facing systems, API rate limits, sync conflicts; the "operational analytics" pattern |

**How to learn it**

1. Read the topic file.
2. Draw the same order flow three times: as ETL, as ELT, and with a reverse
   ETL step that sends "high-value customers" to a CRM.
3. Write a decision note: "For our company, ELT by default, ETL only when
   …".

**Hands-on exercise**

Build two versions of the same pipeline with SQLite as the "warehouse":

- `etl_pipeline.py` — clean and aggregate in Python, then load only the
  final table.
- `elt_pipeline.py` — load raw rows into a `raw_orders` table, then run the
  transformation as SQL inside SQLite.

Then introduce a bug in the transformation logic, fix it, and try to
rebuild history. Note which version could recover without re-extracting
from the source. Add a `reverse_etl.py` that writes the top customers to a
JSON file that stands in for a CRM API.

**Checkpoint:**

- [ ] Explain the difference between ETL and ELT in terms of *where* the T
      runs.
- [ ] Give two reasons to still use ETL today.
- [ ] Explain why keeping raw data makes backfills possible.
- [ ] Name one risk of reverse ETL and how to reduce it.

**Common mistakes:** throwing away raw data after transformation; treating
reverse ETL as harmless "just a sync".

---

## 8. Phase C — Where Data Lives (Intermediate → Advanced)

### Topic 05 — [OLTP vs OLAP Workloads](05-oltp-vs-olap-workloads.md)

**Why here:** You know data moves from sources to analytical systems. This
topic explains *why* the two sides are different systems at all, which is
the basis for every architecture in Topic 06.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | OLTP: many small reads and writes, single-row lookups, strict consistency (orders, payments, user accounts) |
| Basics | OLAP: few, large, read-heavy queries that scan and aggregate millions of rows (reports, dashboards, ML features) |
| Intermediate | Row-oriented vs column-oriented storage and why columnar wins for analytics (read only needed columns, better compression) — Module 2.5 goes deeper into formats |
| Intermediate | Normalised models for OLTP vs denormalised / dimensional models for OLAP (Module 2.8 goes deeper) |
| Intermediate | Why running analytics directly on the production database is dangerous: lock contention, slow customer-facing queries, outages |
| Advanced | Read replicas, CDC-based replication, and HTAP systems that try to serve both workloads |
| Advanced | Workload characteristics as numbers: queries per second, rows scanned per query, latency targets, concurrency |

**How to learn it**

1. Read the topic file.
2. Classify twenty example queries as OLTP or OLAP.
3. Draw how a single order record appears in an OLTP table versus an OLAP
   fact table.

**Hands-on exercise**

Write `oltp_vs_olap_bench.py`:

1. Create an SQLite table with 1,000,000 generated orders.
2. Time 10,000 single-row lookups by primary key (OLTP pattern).
3. Time a full-table aggregation such as revenue per country per month
   (OLAP pattern).
4. Add an index on `country` and rerun both. Note which pattern benefits
   and which does not.
5. Store the same data as one CSV file per column (a toy columnar layout)
   and compare how many bytes you must read to sum one column.

Record timings in your notes. You do not need precise benchmarks — you need
intuition for why the two workloads want different engines.

**Checkpoint:**

- [ ] Give three differences between OLTP and OLAP workloads.
- [ ] Explain why columnar storage speeds up analytical queries.
- [ ] Explain why analysts should not query the production database
      directly, and name two safer alternatives.

**Common mistakes:** thinking an index fixes every slow analytical query;
calling any database a "data warehouse".

---

### Topic 06 — [Warehouse, Lake, and Lakehouse Architectures](06-warehouse-lake-and-lakehouse-architectures.md)

**Why here:** Once you understand OLAP workloads, you can compare the three
main platform designs that serve them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Data warehouse: structured, schema-on-write, SQL-first, managed storage and compute (Snowflake, BigQuery, Redshift) |
| Basics | Data lake: cheap object storage holding any format, schema-on-read (S3, GCS, ADLS with Parquet/JSON/CSV files) |
| Basics | Lakehouse: lake storage plus open table formats (Delta Lake, Apache Iceberg, Apache Hudi) that add ACID transactions, schema enforcement, and time travel |
| Intermediate | Schema-on-write vs schema-on-read trade-offs |
| Intermediate | Separation of storage and compute; why it changed cost models |
| Intermediate | The "data swamp" failure mode of lakes without governance |
| Advanced | Open formats and engine independence: one copy of data read by Spark, Trino, DuckDB, and warehouses |
| Advanced | Catalogs and governance layers (introduced here; Modules 2.15 and 2.20 go deep) |
| Advanced | Choosing an architecture: team skills, data types (tables, images, text, embeddings), ML needs, cost, and vendor lock-in |

**How to learn it**

1. Read the topic file.
2. Build a comparison table with rows for storage cost, query speed,
   supported data types, ACID support, ML friendliness, governance, and
   lock-in. Fill it from memory, then check against the topic file.
3. For three company profiles (a 10-person startup, a mid-size retailer
   with an ML team, a bank with strict regulation), recommend an
   architecture and write a decision note for each.

**Hands-on exercise**

Simulate all three on your laptop with the standard library:

- **Warehouse** — SQLite database with typed tables and constraints; a bad
  row is rejected at write time.
- **Lake** — a `lake/` folder of raw CSV and JSON files; a bad row is
  accepted and only fails when someone reads it.
- **Lakehouse (toy)** — the `lake/` folder plus a `_log.json` file that
  records every committed file and its schema. Readers only trust files
  listed in the log. Write a new file, "crash" before updating the log, and
  show that readers never see the half-written data.

This toy transaction log is the core idea behind Delta Lake and Iceberg,
which you will use for real in Module 2.15.

**Checkpoint:**

- [ ] Explain schema-on-write vs schema-on-read with an example.
- [ ] Explain what problem open table formats solve for data lakes.
- [ ] Recommend an architecture for a new scenario and justify it.
- [ ] Explain why separating storage from compute reduces cost.

**Common mistakes:** believing a lakehouse is "just a lake with a new
name"; picking an architecture by brand instead of by requirement.

---

### Topic 07 — [Medallion Bronze, Silver, Gold Layers](07-medallion-bronze-silver-gold-layers.md)

**Why here:** Topic 06 picks the platform; this topic organises data
*inside* it. It is the most directly practical topic in the module.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Bronze**: raw data as received, append-only, with ingestion metadata (source, load time, file name, batch id) |
| Basics | **Silver**: cleaned, typed, deduplicated, conformed data at a clear grain; joins to reference data |
| Basics | **Gold**: business-level aggregates and models built for specific consumers (dashboards, features, reports) |
| Intermediate | Which rules belong in which layer; why business logic must not leak into bronze |
| Intermediate | Rebuilding silver and gold from bronze (replayability, connecting back to Topic 04) |
| Intermediate | Naming conventions, folder or schema layout, and ownership per layer |
| Advanced | Relationship to older layering names: raw/staging/marts and landing/curated/consumption |
| Advanced | When medallion is overkill, and when you need extra layers (e.g. a quarantine area for bad records) |
| Advanced | Cost of each layer: storage duplication vs debuggability and reuse |

**How to learn it**

1. Read the topic file.
2. Take your orders scenario and write a table: for each column, what it
   looks like in bronze, silver, and gold.
3. List ten transformation rules (trim strings, cast types, drop test
   orders, convert currency, compute daily revenue, …) and assign each to a
   layer.

**Hands-on exercise**

Refactor `lifecycle_sim.py` into `medallion_pipeline.py` with three
separate, individually rerunnable steps:

- `bronze.py` — copy source rows unchanged, adding `_ingested_at`,
  `_source`, and `_batch_id`.
- `silver.py` — cast types, standardise time zones to UTC, drop duplicates
  by order id keeping the latest version, and send invalid rows to a
  `quarantine/` folder.
- `gold.py` — build `daily_revenue_by_country` and `customer_lifetime_value`.

Then change a business rule in `silver.py` and rebuild silver and gold from
bronze **without touching the source**. Run each step twice and confirm the
output does not change (idempotency from Stage 1).

**Checkpoint:**

- [ ] State the purpose of each layer in one sentence.
- [ ] Assign ten new rules to the correct layer.
- [ ] Explain why bronze is append-only and keeps raw values.
- [ ] Rebuild gold after a logic change without re-extracting.

**Common mistakes:** cleaning data in bronze; building gold tables nobody
consumes; skipping silver and joining raw data directly into gold.

---

## 9. Phase D — What "Good" Means (Advanced)

### Topic 08 — [SLAs, Freshness, Latency, and Data Consumers](08-slas-freshness-latency-and-data-consumers.md)

**Why last:** This topic ties everything together. It turns an
architecture into a set of promises to real consumers, and tells you when
you are breaking them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Consumers and their needs: the CFO's monthly report, a live operations dashboard, a fraud model, an ML training job, a RAG system |
| Basics | Freshness (how old the newest data is), latency (how long data takes to travel end to end), completeness, accuracy, and availability |
| Intermediate | **SLI** (what you measure), **SLO** (the internal target), **SLA** (the agreement with consequences); how they relate |
| Intermediate | Writing measurable targets, e.g. "`daily_revenue` is complete for yesterday by 07:00 UTC on 99% of days" |
| Intermediate | Latency budgets: splitting an end-to-end target across ingestion, each layer, and serving |
| Advanced | Error budgets and what to do when you burn them |
| Advanced | Upstream dependencies: your SLA can never be better than your sources' SLAs; negotiating with producers |
| Advanced | Tiering datasets (critical, important, best effort) and matching on-call and alerting effort to the tier |

**How to learn it**

1. Read the topic file.
2. Interview-style exercise: for five consumers in your scenario, write
   what they need, the SLI you would measure, and a realistic SLO.
3. Build a latency budget diagram for one gold table from source to
   dashboard.

**Hands-on exercise**

Add a `freshness_check.py` to your medallion pipeline:

1. After each run, write a `run_metadata.json` with start time, end time,
   rows in and out per layer, and the maximum event timestamp in gold.
2. Compute freshness (now minus max event time) and end-to-end latency.
3. Compare against SLOs read from a config file (for example: freshness
   under 2 hours, completeness at least 99.5%).
4. Exit with a non-zero code and log a clear message when an SLO is
   breached.
5. Simulate a late upstream source and show the check catching it.

**Checkpoint:**

- [ ] Explain the difference between SLI, SLO, and SLA.
- [ ] Write a measurable freshness SLO for a real dataset.
- [ ] Split a 60-minute end-to-end latency target into a budget per stage.
- [ ] Explain why your SLA depends on your sources' SLAs.

**Common mistakes:** promising SLAs with no measurement; one SLA for every
dataset regardless of importance; confusing freshness with latency.

---

## 10. Consolidate — practice questions

When all eight topics are done, open
[`practice-questions.md`](practice-questions.md). Solve every question in
this order:

1. Restate the scenario in your own words.
2. Identify sources, consumers, volume, and freshness needs.
3. Draw the design (sources → ingestion → layers → serving → consumers).
4. Write a decision note for every choice: batch vs streaming, ETL vs ELT,
   platform, layer rules, and SLOs.
5. Only then write code, if the question asks for it.

Do not look at answers until you have a written attempt. Being wrong on
paper is cheap; being wrong in production is not.

---

## 11. Module mini-project — pipeline design document

This is the proof that you have finished the module. Pick one scenario:

- **Ride-sharing:** trips, driver locations, payments, and ratings.
- **Online learning platform:** enrolments, video events, quiz results.
- **Hospital clinic:** appointments, billing, and lab results (with PII).

Produce a design document (3–5 pages of Markdown) containing:

1. **Context** — business, consumers, and what decisions the data supports.
2. **Sources** — type, volume, update pattern, access method, owner.
3. **Lifecycle diagram** — every hop from generation to consumption.
4. **Processing mode** — batch, micro-batch, or streaming per flow, with
   reasons.
5. **Transformation pattern** — ETL, ELT, EtLT, and any reverse ETL.
6. **Workload analysis** — which parts are OLTP and which are OLAP.
7. **Platform choice** — warehouse, lake, or lakehouse, with a decision
   note.
8. **Medallion design** — tables per layer, grain, and the rules in each.
9. **SLOs** — freshness, latency, and completeness per gold dataset, with a
   latency budget.
10. **Risks and open questions** — PII, late data, source changes, cost.

Also include a working, standard-library Python prototype of one flow
(bronze → silver → gold with freshness checks), reusing your exercise code.

**Grading yourself:** ask a peer (or reread after two days) and check that
every design decision has a written reason, and that every SLO has an SLI
you know how to measure.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.2 when you can tick every box without looking at your
notes:

- [ ] I can explain the full data lifecycle and name examples for every
      stage.
- [ ] I can pick batch, micro-batch, or streaming for a scenario and defend
      it with latency, cost, and complexity.
- [ ] I can explain ETL, ELT, and reverse ETL and when each fits.
- [ ] I can explain OLTP vs OLAP and row vs column storage.
- [ ] I can compare warehouse, lake, and lakehouse and recommend one.
- [ ] I can design bronze, silver, and gold tables and assign rules to
      layers.
- [ ] I can write measurable SLIs and SLOs and a latency budget.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

Use these alongside the topic files. They are optional deep dives, not
replacements.

| Resource | Relevant topics |
| --- | --- |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley (O'Reilly) | 01, 02, 03, 04, 06 — the lifecycle and undercurrents framing |
| *Designing Data-Intensive Applications* — Martin Kleppmann (O'Reilly) | 03, 05, 06 — storage engines, batch and stream processing |
| *The Data Warehouse Toolkit* — Ralph Kimball and Margy Ross (Wiley) | 05, 07 — dimensional thinking behind OLAP and gold layers |
| *Site Reliability Engineering* — Google (free online), chapter on Service Level Objectives | 08 — SLIs, SLOs, SLAs, and error budgets |
| Official documentation for Delta Lake and Apache Iceberg (overview pages only) | 06, 07 — lakehouse and medallion context |

---

## 14. Where this module leads

Every later module in Stage 2 is one deeper layer of the map you built
here:

| This module's idea | Where it goes deeper |
| --- | --- |
| Lifecycle ingestion stage | 2.9 Data Ingestion and Extraction Patterns |
| Batch vs streaming | 2.13 Orchestration, 2.16 Streaming and Event-Driven Data |
| ELT and transformation logic | 2.6 SQL, 2.12 Transformation Patterns (dbt) |
| OLTP vs OLAP, row vs column | 2.5 Data Formats, 2.7 Database Connectivity, 2.8 Data Modelling |
| Warehouse, lake, lakehouse | 2.14 PySpark, 2.15 Lakehouse Table Formats, 2.17 Cloud Platforms |
| Medallion layers and quarantine | 2.11 Data Validation and Quality, 2.12 Transformation Patterns |
| SLAs, freshness, and consumers | 2.20 Observability, 2.22 Serving Data for Analytics, ML, and AI |

The stage-level projects in
[`../00-Stage-2-Overview/Projects/`](../00-Stage-2-Overview/Projects/)
all start from the design-document habit you practise in this module:
think first, draw the flow, write down the promises, then build.
