# Roadmap — Module 2.20: Observability, Lineage, Governance, and Security

This is the learning roadmap for the twentieth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about operating and
protecting a data platform, **in what order**, **how** to learn each topic,
and **how to prove to yourself** that you have learned it before you move
on.

A data platform that works is not the same as a data platform you can
**operate** and **trust**. At scale, the questions change:

- *Is it healthy right now?* Which pipelines are slow, failing, late, or
  expensive — and would anyone notice?
- *Where did this number come from?* Which sources, jobs, and versions
  produced it, and what breaks if a column changes?
- *Who may see what?* Where is personal data, is it protected, and who
  accessed it?
- *Are we allowed to keep it?* How long, for what purpose, and can we
  prove we deleted it when asked?
- *What do we do when it goes wrong?* Who is paged, who decides, who tells
  the stakeholders, and how do we make sure it never happens again?

Earlier modules gave you pieces: run tables, quality checks and anomaly
monitors (Module 2.11), alerts in orchestrators (Module 2.13), catalogs
(Module 2.15), IAM and key management (Module 2.17), secrets (Module 2.18),
and masked test data (Module 2.19). This module assembles them into an
**observable, governed, secure, and compliant** platform — and a way of
responding when things fail.

> **Note:** this module teaches engineering practices for privacy and
> compliance. It is not legal advice. Real compliance decisions must involve
> your organisation's legal, privacy, and security teams.

---

## 1. Module outcome

By the end of this module you will be able to:

- Instrument pipelines with **metrics** and consistent **run metadata**,
  and build dashboards with service-level indicators.
- Trace work across services and pipeline steps with **OpenTelemetry**,
  including context propagation through Kafka.
- Design **alerting and on-call** for data: symptom-based alerts, SLO burn
  rates, routing, runbooks, and low alert fatigue.
- Capture **lineage** with **OpenLineage** from Airflow, Spark, dbt, and
  custom Python jobs, and use it for impact and root-cause analysis.
- Run a **data catalog** with ownership, glossary, classification, quality
  status, and metadata as code.
- **Detect and protect PII** with masking, pseudonymisation, and
  tokenisation.
- Apply **encryption** at rest and in transit correctly, including envelope
  encryption and crypto-shredding.
- Implement **row- and column-level access control** in databases,
  warehouses, and lakehouse catalogs, driven by data classification.
- Implement **retention and deletion** (including data-subject erasure
  requests) across every copy of the data, with proof.
- Lead **data incident response** and write **blameless post-mortems**.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.19. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, networking, permissions | Stage 0 | Collectors, agents, and access control foundations |
| Logging vs print, safe and useful logging | Stage 1 — Modules 1.5 and 1.10 | Logging basics are **not** re-taught; this module adds correlation and structure across systems |
| `contextvars`, async and concurrency | Stage 2 — Module 2.10 | Propagating run and trace context |
| Freshness SLAs, dataset tiers, data as a product | Stage 2 — Module 2.1 | SLOs and ownership |
| Run tables, pipeline state (`pipeline_runs`, ledgers) | Stage 2 — Modules 2.7, 2.9, 2.12 | Consolidated into one run-metadata model |
| Quality dimensions, monitors, quarantine, reconciliation | Stage 2 — Module 2.11 | Data-quality signals feed dashboards and alerts; **not** re-taught |
| Keyed hashing for pseudonymisation | Stage 2 — Module 2.12 | Used in PII protection |
| Orchestrator alerts and callbacks | Stage 2 — Module 2.13 | Routed into the alerting design |
| Spark UI and listeners | Stage 2 — Module 2.14 | Spark metrics and lineage |
| Catalogs, time travel, physical deletion in table formats | Stage 2 — Module 2.15 | Governance and erasure on the lakehouse |
| Kafka headers, consumer lag | Stage 2 — Module 2.16 | Trace propagation and lag alerts |
| IAM, KMS basics, audit trails, lifecycle policies | Stage 2 — Module 2.17 | Access, keys, audit, and retention foundations |
| Secrets management and leak response | Stage 2 — Module 2.18 | Security incidents |
| Masked and synthetic test data, regression tests | Stage 2 — Module 2.19 | Privacy-safe testing and incident follow-up |

**Tools needed:**

- Docker Compose services: **Prometheus**, **Grafana**, **Alertmanager**,
  an **OpenTelemetry Collector**, a tracing backend (e.g. Jaeger or Grafana
  Tempo), **Marquez** (OpenLineage reference backend), and a data catalog
  (**OpenMetadata** or **DataHub** — both are resource-heavy; run them one
  at a time).
- Python: `uv add prometheus-client opentelemetry-sdk
  opentelemetry-exporter-otlp opentelemetry-instrumentation-httpx
  openlineage-python presidio-analyzer presidio-anonymizer cryptography`
  plus instrumentation packages for the libraries you use.
- The OpenLineage integrations for Airflow (provider), Spark, and dbt.
- PostgreSQL (for row-level security), your cloud warehouse and KMS from
  Module 2.17 (for masking policies and envelope encryption), and your
  lakehouse catalog from Module 2.15.
- Your platform code, CI/CD, and tests from Modules 2.9–2.19.

---

## 3. How the module is organised

The ten topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Observability                               (Basics → Intermediate)
  01 Pipeline metrics and run metadata
  02 OpenTelemetry tracing for pipelines
  03 Alerting and on-call for data

Phase B — Metadata and Lineage                        (Intermediate)
  04 Data lineage with OpenLineage
  05 Data catalogs and metadata management

Phase C — Security and Privacy                        (Intermediate → Advanced)
  06 PII detection, masking, and tokenization
  07 Encryption at rest and in transit
  08 Row- and column-level access control

Phase D — Compliance and Response                     (Advanced)
  09 Retention, deletion, and GDPR compliance
  10 Data incident response and post-mortems

Consolidate
  practice-questions.md
  Module mini-project: an observable, governed, secure data platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10
measure trace alert  trace   describe find &  encrypt restrict retain & respond
runs    work  people data    data     protect data    access   delete   & learn
                     flows   assets   PII
```

Why this order:

- You measure (01) and trace (02) before you alert (03), because alerts are
  built on those signals.
- Lineage (04) comes before catalogs (05) because catalogs display lineage,
  and both are needed to know where sensitive data lives.
- PII detection (06) produces the classification that encryption (07) and
  access control (08) act on.
- Retention and erasure (09) need lineage, catalogs, classification, and
  access control to find and remove every copy.
- Incident response (10) uses everything: signals to detect, lineage to
  scope, access logs to investigate, and processes to communicate and learn.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — metrics and run metadata · Topic 02 — OpenTelemetry |
| 2 | Topic 03 — alerting and on-call · Topic 04 — OpenLineage |
| 3 | Topic 05 — data catalogs · Topic 06 — PII detection and protection |
| 4 | Topic 07 — encryption · Topic 08 — access control |
| 5 | Topic 09 — retention and GDPR · Topic 10 — incident response · practice questions · mini-project |

---

## 5. How to study every topic (the operate-and-protect loop)

```text
Read → Ask the operational question → Instrument or enforce it
→ Make it visible (dashboard, catalog, report) → Simulate the bad day
→ Detect it → Respond and prove the outcome → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Ask the operational question** the topic answers (e.g. "Which gold
   tables did yesterday's bad source file affect?").
3. **Instrument or enforce** it: metrics, spans, lineage events, tags,
   policies, retention jobs.
4. **Make it visible** to the people who need it: dashboards, the catalog,
   reports, or audit logs.
5. **Simulate the bad day**: a slow job, a broken source, a leaked column,
   an unauthorised query, an erasure request, a production incident.
6. **Detect it** with what you built — how long did it take?
7. **Respond and prove the outcome**: fix, restrict, delete, or restore —
   and produce evidence that it worked.
8. **Write down** the practice in `module-2.20-notes.md`.
9. **Explain aloud** to an engineer, an analyst, and a privacy officer —
   each needs a different answer.

Keep one `operations/` area in your platform repository:

```text
operations/
├── observability/     # metrics, OTel config, dashboards as code, alert rules
├── lineage/           # OpenLineage configuration and custom emitters
├── catalog/           # metadata as code: owners, glossary, tags, descriptions
├── privacy/           # PII scanners, masking and tokenisation, retention jobs, erasure pipeline
├── security/          # encryption helpers, access policies, policy tests
├── runbooks/          # one per critical pipeline and alert
└── incidents/         # incident templates and post-mortems
```

---

## 6. Phase A — Observability (Basics → Intermediate)

### Topic 01 — [Pipeline metrics and run metadata](01-pipeline-metrics-and-run-metadata.md)

**Why it comes first:** You cannot operate what you cannot see. Metrics
and run metadata answer "is it healthy, is it fast enough, is it getting
worse?" for every pipeline.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Observability signals: **metrics**, **logs**, **traces** — plus data-specific signals (freshness, volume, quality) from Module 2.11 |
| Basics | Metric types: **counters**, **gauges**, **histograms** (and summaries) |
| Basics | Exposing metrics from Python with `prometheus-client`; Prometheus scraping; Grafana dashboards |
| Intermediate | **What to measure for pipelines**: run duration, success and failure counts, retries, rows and bytes in/out, quarantined rows, freshness, consumer lag, queue depth, and cost per run |
| Intermediate | Metrics for batch jobs: pushing final metrics (e.g. via a push gateway) vs recording them in run metadata |
| Intermediate | **Labels and cardinality**: labelling by pipeline, dataset, and environment — never by run id, user id, or key |
| Intermediate | **A consolidated run-metadata model**: run id, pipeline, code version (git SHA), image digest, data interval, inputs and outputs, row counts, status, timings, cost — unifying the run tables from earlier modules |
| Intermediate | **Structured logs** (JSON) correlated by `run_id` using context variables, across pipeline steps |
| Advanced | Service-level indicators and objectives for data (freshness, completeness, success rate, latency) on dashboards (Module 2.1) |
| Advanced | Useful frameworks for choosing metrics: RED (rate, errors, duration) for services, USE (utilisation, saturation, errors) for resources |
| Advanced | Dashboards as code and a standard dashboard per pipeline |
| Advanced | Collecting metrics from tools you did not write: Airflow, Spark, Kafka, and warehouses (exporters, listeners, query history) |

**How to learn it**

1. Read the topic file.
2. For three pipelines, list the questions an on-call engineer asks at 3
   a.m. and the metric that answers each.
3. Deliberately create a high-cardinality metric and observe its effect on
   Prometheus.

**Hands-on exercise — `operations/observability/`**

1. Add a shared `instrumentation` module to your platform: counters for
   rows and errors, histograms for step durations, gauges for freshness —
   all labelled by pipeline, step, and environment.
2. Record every run in a unified `run_metadata` table (replacing ad-hoc run
   tables), including git SHA and image digest.
3. Emit structured JSON logs that carry `run_id` and step names
   automatically.
4. Build a Grafana dashboard per pipeline (runs, durations, rows,
   freshness, lag) and a platform overview with SLO status.
5. Scrape or ingest Airflow and Kafka metrics alongside your own.
6. Answer, from the dashboard alone: "which pipeline got slower this week,
   and since which code version?".

**Checkpoint — you are ready to move on when you can:**

- [ ] Choose metric types and labels correctly.
- [ ] Instrument Python pipelines with metrics and structured logs.
- [ ] Record consistent run metadata including code versions.
- [ ] Build dashboards showing SLIs and SLOs.
- [ ] Avoid high-cardinality labels.

**Common mistakes:** only logging, never measuring; labels with unbounded
values; dashboards nobody looks at; run records without code versions, so
regressions cannot be traced to a change.

---

### Topic 02 — [OpenTelemetry tracing for pipelines](02-opentelemetry-tracing-for-pipelines.md)

**Why here:** Metrics say *that* something is slow; traces say *where*.
When a record travels from an API through Kafka into Spark and a
warehouse, tracing connects the steps into one story.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Traces** and **spans**: a trace is one unit of work; spans are its timed steps, with parent–child relationships |
| Basics | Span attributes, events, status, and errors |
| Basics | The OpenTelemetry SDK for Python: tracer provider, creating spans, and exporting via OTLP |
| Intermediate | **Automatic instrumentation** for common libraries (HTTP clients, database drivers, cloud SDKs) |
| Intermediate | The **OpenTelemetry Collector**: receivers, processors (batching, filtering, attribute redaction), exporters, and why pipelines send to a collector rather than directly to a backend |
| Intermediate | **Context propagation**: W3C trace context across HTTP calls, and in **Kafka message headers** for streaming (Module 2.16) |
| Intermediate | Correlating logs and traces (trace ids in structured logs) and metrics with exemplars |
| Advanced | Tracing batch pipelines: one trace per run, spans per task and step; propagating context between orchestrator tasks (environment or run configuration; orchestrator-native OpenTelemetry support where available) |
| Advanced | **Sampling**: head vs tail sampling; keeping all error traces; cost and volume control |
| Advanced | Semantic conventions for consistent attribute names |
| Advanced | Security of telemetry: no PII or secrets in span attributes and logs; redaction in the collector |
| Advanced | Overhead and when not to trace (per-record spans in high-throughput streams) |

**How to learn it**

1. Read the topic file.
2. Run the collector and a tracing backend with Docker Compose; send a
   trace from a small script and explore it.
3. Instrument one extraction job end to end and find its slowest span.

**Hands-on exercise — `operations/observability/tracing/`**

1. Instrument your Module 2.9 API extractor with automatic HTTP and
   database instrumentation plus manual spans for pagination and landing.
2. Propagate trace context through Kafka headers from producer to consumer
   (Module 2.16) and show one trace spanning both.
3. Create one trace per daily pipeline run with a span per Airflow task,
   passing context between tasks.
4. Add collector processors that drop PII attributes and batch exports;
   test that a PII attribute never reaches the backend.
5. Configure sampling that keeps all errors and a fraction of successful
   traces.
6. Use a trace to find and fix a real slowdown.

**Checkpoint:**

- [ ] Explain traces, spans, and context propagation.
- [ ] Instrument Python code manually and automatically.
- [ ] Propagate context across HTTP, Kafka, and pipeline tasks.
- [ ] Configure the collector for batching, redaction, and sampling.
- [ ] Correlate traces with logs and metrics.

**Common mistakes:** a span per record in high-volume streams; personal
data in span attributes; traces that stop at service boundaries because
context was not propagated; exporting directly to vendors from every job.

---

### Topic 03 — [Alerting and on-call for data](03-alerting-and-on-call-for-data.md)

**Why here:** Signals are useless if nobody acts on them — and harmful if
they wake people up for nothing. Good alerting turns metrics and checks into
the right action by the right person at the right time.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Alerts vs dashboards vs reports: alerts demand action |
| Basics | **Symptom-based alerts** (data late, wrong, or missing for consumers) vs cause-based alerts (CPU high) |
| Basics | Alert rules in Prometheus and routing with Alertmanager (grouping, inhibition, silences) |
| Intermediate | **Severity and routing** by dataset tier (Module 2.1): page for critical data, ticket for important data, digest for the rest |
| Intermediate | **Actionable alert content**: what is wrong, since when, which consumers are affected, dashboards, logs, the runbook, and the owner |
| Intermediate | **Data-specific alerts**: freshness breaches, volume anomalies, failed quality gates (Module 2.11), consumer lag growth (Module 2.16), pipeline failures after retries (Module 2.13), and cost spikes |
| Intermediate | **Runbooks** for every paging alert |
| Advanced | **SLO-based alerting**: error budgets and burn-rate alerts over multiple windows instead of static thresholds |
| Advanced | **Alert fatigue**: measuring alert volume and precision, deleting or demoting noisy alerts, and deduplicating alerts from several tools |
| Advanced | **On-call practices**: rotations, handovers, escalation policies, paging tools (awareness), working hours vs 24/7 for data, and sustainable load |
| Advanced | Stakeholder communication: data status notices to consumers when data is late or wrong |

**How to learn it**

1. Read the topic file.
2. List every alert your platform currently produces across tools, and
   classify each as page, ticket, digest, or delete.
3. Simulate one week of operations with injected failures and count how
   many alerts were useful.

**Hands-on exercise — `operations/observability/alerts/`**

1. Write alert rules for freshness SLO burn, volume anomaly, quality gate
   failure, pipeline failure after retries, lag growth, and warehouse cost
   spike — each with severity, owner, and runbook link.
2. Configure Alertmanager routing by tier and team, with grouping and
   inhibition (e.g. suppress downstream freshness alerts when an upstream
   source is known down).
3. Write runbooks for the three most critical alerts.
4. Implement multi-window burn-rate alerts for one freshness SLO.
5. Run a simulated on-call week: inject failures, respond using runbooks,
   and measure time to acknowledge and resolve.
6. Remove or demote at least one alert that proved noisy.

**Checkpoint:**

- [ ] Write symptom-based, actionable alerts with runbooks.
- [ ] Route alerts by severity and ownership.
- [ ] Use SLO burn-rate alerting.
- [ ] Measure and reduce alert fatigue.
- [ ] Describe a sustainable on-call process for data.

**Common mistakes:** alerting on every task failure (even ones that retry
successfully); alerts with no owner or runbook; the same incident producing
alerts from five tools; paging at night for data nobody needs until noon.

---

## 7. Phase B — Metadata and Lineage (Intermediate)

### Topic 04 — [Data lineage with OpenLineage](04-data-lineage-with-openlineage.md)

**Why here:** When a number is wrong, you need to know where it came from;
when a column changes, you need to know what it breaks. Lineage answers
both — if it is captured automatically from the systems that actually run.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What lineage is: which jobs read which datasets and wrote which datasets; table-level vs **column-level** lineage |
| Basics | Uses: **impact analysis** (what breaks downstream), **root-cause analysis** (what is upstream), compliance (where personal data flows), and deprecation |
| Basics | Design-time lineage (from code, e.g. dbt's graph) vs **runtime lineage** (from actual runs) |
| Intermediate | The **OpenLineage** standard: **jobs**, **runs**, **datasets**, run events (`START`, `COMPLETE`, `FAIL`), and **facets** (schema, data source, SQL, column lineage, data quality, and custom facets) |
| Intermediate | Integrations: Airflow's OpenLineage provider, the Spark integration (listener), dbt integration, and others such as Flink — and what each captures |
| Intermediate | The Python client for **custom jobs** (your extractors and pipeline framework) |
| Intermediate | **Marquez** as a reference backend for storing and exploring lineage |
| Advanced | Consistent dataset naming (namespaces and names) so lineage from different tools connects |
| Advanced | Column-level lineage from SQL parsing and its limits |
| Advanced | Lineage gaps: manual scripts, notebooks, and external systems; finding and closing them |
| Advanced | Attaching run metadata and quality results to lineage (facets) so a single view shows what ran, on what, and whether it passed |

**How to learn it**

1. Read the topic file.
2. Enable OpenLineage for Airflow, Spark, and dbt in your platform and send
   events to Marquez.
3. Pick one gold column and trace it back to its sources in the lineage
   graph; list every gap where lineage is missing.

**Hands-on exercise — `operations/lineage/`**

1. Configure Airflow, Spark, and dbt to emit OpenLineage events with a
   consistent naming scheme for datasets in MinIO, PostgreSQL, and your
   warehouse.
2. Emit OpenLineage events from your custom Python extractors and
   config-driven framework (Module 2.12) using the Python client, including
   schema and row-count facets.
3. Add a custom facet with quality results from Module 2.11.
4. Build an impact-analysis script: given a source column, list every
   downstream dataset, dashboard, and owner.
5. Simulate a bad source file and use lineage to list affected gold tables
   and consumers within minutes.

**Checkpoint:**

- [ ] Explain jobs, runs, datasets, and facets in OpenLineage.
- [ ] Emit lineage from Airflow, Spark, dbt, and custom Python code.
- [ ] Use lineage for impact and root-cause analysis.
- [ ] Find and close lineage gaps.

**Common mistakes:** inconsistent dataset names that break the graph;
lineage only from design-time definitions; ignoring custom scripts; lineage
nobody queries during incidents.

---

### Topic 05 — [Data catalogs and metadata management](05-data-catalogs-and-metadata-management.md)

**Why here:** Lineage says how data flows; a catalog says what data
**means**, who owns it, whether it can be trusted, and whether it is
sensitive. It is the front door of a governed platform.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Technical metadata (schemas, locations, statistics) vs business metadata (descriptions, glossary terms, owners) vs operational metadata (runs, quality, freshness) |
| Basics | Data catalog features: search and discovery, descriptions, ownership, lineage views, usage statistics |
| Basics | Open-source catalogs (e.g. **OpenMetadata**, **DataHub**) and cloud and platform catalogs (e.g. Unity Catalog, cloud data-governance services) — and how they relate to the technical catalogs of Module 2.15 |
| Intermediate | **Metadata ingestion**: connectors that pull from warehouses, databases, dbt, Airflow, Kafka, and lineage backends |
| Intermediate | **Ownership and domains**: every dataset has an owning team and a contact |
| Intermediate | **Business glossary**: agreed definitions ("active customer", "net revenue") linked to columns and metrics |
| Intermediate | **Classification and tags**: sensitivity tags (PII, confidential) applied manually and automatically (Topic 06), feeding access policies (Topic 08) |
| Advanced | **Metadata as code**: descriptions, owners, and tags kept in the repository (e.g. dbt YAML, contract files) and pushed to the catalog in CI |
| Advanced | Trust signals: certified datasets, quality status, freshness, and deprecation notices in the catalog |
| Advanced | Data products in a data-mesh setting (Module 2.1): contracts, owners, SLOs, and documentation published together |
| Advanced | Adoption: making the catalog useful enough that people actually search it |

**How to learn it**

1. Read the topic file.
2. Run one catalog locally and ingest metadata from PostgreSQL, your
   warehouse or DuckDB, dbt, Airflow, Kafka, and Marquez.
3. Ask someone unfamiliar with your platform to find "daily net revenue by
   country" and its owner using only the catalog; note every obstacle.

**Hands-on exercise — `operations/catalog/`**

1. Deploy OpenMetadata or DataHub and configure ingestion for your
   platform's systems and lineage.
2. Define domains and owners for every dataset and write glossary terms for
   ten core business concepts, linked to columns.
3. Keep descriptions, owners, and tags as code (dbt YAML and contracts) and
   publish them to the catalog from CI.
4. Surface quality results and freshness for gold tables in the catalog.
5. Mark one table as deprecated with a replacement and a sunset date.

**Checkpoint:**

- [ ] Explain technical, business, and operational metadata.
- [ ] Ingest metadata and lineage into a catalog.
- [ ] Assign ownership, glossary terms, and classification tags.
- [ ] Manage metadata as code.
- [ ] Publish trust signals and deprecations.

**Common mistakes:** catalogs filled with empty descriptions; no owners;
glossary definitions that disagree with dbt logic; metadata edited only in
the UI and lost on the next ingestion.

---

## 8. Phase C — Security and Privacy (Intermediate → Advanced)

### Topic 06 — [PII detection, masking, and tokenization](06-pii-detection-masking-and-tokenization.md)

**Why here:** You cannot protect personal data you have not found. This
topic finds it — in columns, free text, and events — and chooses the right
protection for each use.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Personal data and **PII**: direct identifiers (name, email, phone, national ids) vs **quasi-identifiers** (postcode, birth date, gender) that identify people in combination; sensitive categories (health, financial, biometric) |
| Basics | Where PII hides: obvious columns, free-text fields, JSON properties, logs, event payloads, quarantine tables (Module 2.11), and test data (Module 2.19) |
| Intermediate | **Detection**: rule-based patterns with validation (e.g. checksums for card numbers), column-name heuristics, sampling data, and NLP-based detectors (e.g. Microsoft Presidio) for free text |
| Intermediate | Turning detection into **classification tags** in the catalog (Topic 05) with human review |
| Intermediate | **Protection techniques**: redaction (remove), **masking** (static masked copies vs dynamic masking at query time), **pseudonymisation** (keyed hashing, Module 2.12), **tokenisation** (replace with a token; the original stored in a secure vault), generalisation (age bands, truncated postcodes) |
| Intermediate | Choosing by use case: analytics usually needs joinable pseudonyms, not raw values; support tools may need reversible tokens under strict access |
| Advanced | **Tokenisation designs**: vault-based vs vaultless (format-preserving encryption), reversibility, and key management |
| Advanced | Re-identification risk: linking attacks, k-anonymity (awareness), and why removing names is not anonymisation; differential privacy (awareness) |
| Advanced | Pseudonymised data is still personal data under laws such as GDPR; truly anonymous data is hard to achieve |
| Advanced | Preventing PII leaks in logs, traces, metrics labels, error messages, and alerts (Topics 01–03) |
| Advanced | Continuous scanning: detecting new PII when schemas change or new sources arrive |

**How to learn it**

1. Read the topic file.
2. Inventory every column and free-text field in your platform and
   classify it (direct identifier, quasi-identifier, sensitive, none).
3. Try to re-identify people in a "de-identified" sample by linking
   quasi-identifiers with another dataset — then fix the release.

**Hands-on exercise — `operations/privacy/pii/`**

1. Build a PII scanner that samples every table in your platform, applies
   pattern rules and Presidio, and proposes classification tags with
   confidence scores.
2. Push reviewed tags to the catalog.
3. Implement protection functions: redaction, static masking, HMAC
   pseudonymisation (with the key in the secrets manager), and a
   tokenisation service with a small token vault and restricted
   detokenisation.
4. Apply them in silver: emails pseudonymised for analytics, phone numbers
   tokenised for the support team, birth dates generalised to year.
5. Scan logs, traces, and quarantine tables for PII and fix any leaks.
6. Add a CI check that fails when a new column matching PII patterns has no
   classification.

**Checkpoint:**

- [ ] Explain direct and quasi-identifiers and re-identification risk.
- [ ] Detect PII in structured and free-text data.
- [ ] Choose between masking, pseudonymisation, tokenisation, and
      generalisation.
- [ ] Keep PII out of logs and telemetry.
- [ ] Continuously classify new data.

**Common mistakes:** unkeyed hashes of emails treated as anonymous;
forgetting free-text and JSON fields; PII in error messages and logs;
detokenisation available to everyone.

---

### Topic 07 — [Encryption at rest and in transit](07-encryption-at-rest-and-in-transit.md)

**Why here:** Encryption protects data when other controls fail — a stolen
disk, an intercepted connection, a misconfigured bucket. It is simple to
turn on and easy to get subtly wrong.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Encryption **at rest** (stored data) vs **in transit** (data moving over networks) |
| Basics | Storage-level encryption in object stores, databases, and warehouses; provider-managed vs **customer-managed keys** (Module 2.17) |
| Basics | TLS for every connection: HTTPS, database connections, Kafka, and internal services |
| Intermediate | **Key management services** and **envelope encryption**: data encrypted with data keys, data keys encrypted with a master key held in the KMS |
| Intermediate | **Key rotation**, key policies, and separation of duties (people who manage keys are not the people who read data) |
| Intermediate | Verifying TLS properly: certificate verification on, database connections with full verification modes, no "disable verification" shortcuts |
| Intermediate | Encrypting Kafka traffic and authenticating clients (TLS and SASL — Module 2.16) |
| Advanced | **Field-level (application-level) encryption** for highly sensitive columns with a well-reviewed library and envelope keys from KMS |
| Advanced | Columnar format encryption (e.g. Parquet modular encryption, Module 2.5) — awareness |
| Advanced | **Crypto-shredding**: encrypting each person's data with their own key and deleting the key to make all copies unreadable (used in Topic 09) |
| Advanced | Private networking (private endpoints, no public database access) as a complement to encryption |
| Advanced | The rule: never invent your own cryptography; use standard algorithms and maintained libraries |

**How to learn it**

1. Read the topic file.
2. Audit every connection in your platform (API clients, PostgreSQL,
   Kafka, object storage, warehouse) for TLS and certificate verification.
3. Draw envelope encryption with a KMS: which component holds which key,
   and what an attacker gets from each.

**Hands-on exercise — `operations/security/encryption/`**

1. Enforce TLS with certificate verification for PostgreSQL (full
   verification mode), Kafka (TLS and SASL in your Compose stack), and
   object storage; show a connection failing when verification fails.
2. Encrypt a sensitive column (e.g. a national id) at the application level
   with envelope encryption: a data key from your KMS (or a local
   substitute), encrypted values stored, the wrapped key stored with them.
3. Rotate the master key and prove existing data remains readable.
4. Implement crypto-shredding for per-customer keys: delete one key and
   prove that customer's encrypted fields are unreadable everywhere,
   including old table versions and backups.
5. Document your platform's encryption inventory: what is encrypted, how,
   with which keys, and who can use them.

**Checkpoint:**

- [ ] Explain at-rest vs in-transit encryption and customer-managed keys.
- [ ] Explain and implement envelope encryption.
- [ ] Enforce verified TLS on every connection.
- [ ] Use field-level encryption and crypto-shredding appropriately.

**Common mistakes:** disabling certificate verification to "make it work";
keys stored next to the data they protect; one key for everything forever;
home-made encryption schemes.

---

### Topic 08 — [Row- and column-level access control](08-row-and-column-level-access-control.md)

**Why here:** With data classified and encrypted, you control **who sees
which rows and columns**. Table-level permissions are rarely enough: sales
managers should see their region, analysts should see pseudonyms, and only
a few people should ever see raw identifiers.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Access-control models: **role-based** (RBAC) and **attribute- or tag-based** (ABAC) |
| Basics | Least privilege for humans and services; role hierarchies and grants in databases and warehouses |
| Basics | Table and schema grants vs finer-grained controls |
| Intermediate | **Column-level security**: column grants, secure views, and **dynamic masking policies** that show raw, masked, or null values depending on the user's role |
| Intermediate | **Row-level security**: PostgreSQL row-level security policies, warehouse row-access policies, and lakehouse catalog row filters (Module 2.15) |
| Intermediate | **Tag-based policies**: classification tags from Topic 06 automatically applying masking and access rules |
| Intermediate | Service accounts vs human users; separate roles for pipelines, analysts, data scientists, and support |
| Advanced | Where enforcement happens: in the database/warehouse, in the lakehouse catalog, in BI tools — and gaps when data is exported |
| Advanced | **Testing access policies** as code (Module 2.19): automated tests that log in as each role and assert what they can and cannot see |
| Advanced | **Auditing access**: query and access logs, reviewing who accessed sensitive data, and periodic access reviews |
| Advanced | Access request and approval workflows, time-bound access, and break-glass procedures |
| Advanced | Performance impact of row and column policies on large queries |

**How to learn it**

1. Read the topic file.
2. Build an access matrix: roles × datasets × columns × row scope.
3. Implement it in PostgreSQL and in your warehouse, then try to bypass it
   (views, joins, exports) as a restricted user.

**Hands-on exercise — `operations/security/access/`**

1. In PostgreSQL, implement row-level security on `orders` so regional
   managers see only their region, and column restrictions so analysts
   cannot read raw emails.
2. In your warehouse (or lakehouse catalog), implement tag-based masking
   policies so any column tagged `pii.email` is masked for all roles except
   an approved one.
3. Write automated access tests: for each role, assert visible rows and
   masked columns; run them in CI.
4. Query the audit logs to list who accessed PII columns in the last week.
5. Implement a time-bound access grant with approval and automatic expiry
   (scripted).
6. Document where your controls stop (e.g. CSV exports) and the mitigating
   controls.

**Checkpoint:**

- [ ] Explain RBAC and tag-based access control.
- [ ] Implement row-level security and column masking.
- [ ] Drive masking from classification tags.
- [ ] Test access policies automatically.
- [ ] Audit and review access to sensitive data.

**Common mistakes:** everyone in one "analyst" role with full access;
masking rules defined per table by hand and forgotten on new tables; no
tests, so a policy change silently exposes data; ignoring exports and
extracts.

---

## 9. Phase D — Compliance and Response (Advanced)

### Topic 09 — [Retention, deletion, and GDPR compliance](09-retention-deletion-and-gdpr-compliance.md)

**Why here:** Keeping data forever is a liability: it costs money, widens
the impact of breaches, and often breaks the law. Deleting data correctly —
everywhere, and provably — is one of the hardest problems in data
engineering, and needs every earlier topic.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | GDPR principles relevant to engineers: lawful basis, purpose limitation, **data minimisation**, **storage limitation**, integrity and confidentiality, and accountability |
| Basics | **Data subject rights**: access, rectification, **erasure**, restriction, portability, and objection — and response deadlines |
| Basics | Other regimes to be aware of (e.g. CCPA/CPRA in California, sector rules such as HIPAA, and India's Digital Personal Data Protection Act) — the engineering patterns are largely shared |
| Intermediate | **Retention policies** per dataset: how long, why, and what happens at the end (delete, anonymise, archive) — recorded alongside the dataset in the catalog |
| Intermediate | Implementing retention: partition drops, table expiry, lifecycle rules (Module 2.17), log and telemetry retention, and Kafka topic retention (Module 2.16) |
| Intermediate | Consent and purpose tracking: storing consent state and filtering processing by it |
| Intermediate | **Erasure (right-to-be-forgotten) pipelines**: find the person's data everywhere via identity keys, catalog classification, and lineage (Topics 04–06) |
| Advanced | Deleting across systems: OLTP sources, bronze/silver/gold lakehouse tables with physical deletion (vacuum and snapshot expiry, Module 2.15), warehouses and their time travel, caches, derived aggregates, ML features and training sets, Kafka topics (tombstones on compacted topics or crypto-shredding), logs, quarantine tables, test data, and backups |
| Advanced | **Crypto-shredding** (Topic 07) for places where physical deletion is impractical (backups, immutable logs) |
| Advanced | **Proof of deletion**: audit records of what was deleted, where, and when — and verification scans |
| Advanced | Legal holds that override retention; data residency constraints |
| Advanced | Records of processing activities and data inventories kept current from the catalog |
| Advanced | Designing for privacy from the start: collect less, pseudonymise early, separate identity data, and keep derived data free of direct identifiers |

**How to learn it**

1. Read the topic file.
2. For one customer, list every place their data exists in your platform —
   use lineage and the catalog, then verify manually. Note what the
   automated view missed.
3. Write retention rules for every dataset with a reason for each.

**Hands-on exercise — `operations/privacy/retention/` and `erasure/`**

1. Record retention periods and legal bases as metadata for every dataset
   in the catalog; implement retention jobs (partition drops, table expiry,
   lifecycle rules, topic retention) orchestrated in Airflow.
2. Build an **erasure pipeline**: accept a request, resolve the person's
   identifiers, find every dataset holding them via tags and lineage,
   delete or crypto-shred in each system, rebuild affected derived data,
   and physically purge old versions.
3. Produce a deletion certificate: a record per system with timestamps and
   verification scan results.
4. Handle a legal hold that blocks deletion for one customer.
5. Implement a data-access (export) request producing the person's data in
   a portable format.
6. Test the whole flow end to end with synthetic people (Module 2.19).

**Checkpoint:**

- [ ] Explain the GDPR principles and data subject rights that affect
      pipelines.
- [ ] Define and implement retention per dataset.
- [ ] Build an erasure pipeline that covers every copy of the data.
- [ ] Prove deletion with audit records and verification.
- [ ] Explain crypto-shredding, legal holds, and privacy by design.

**Common mistakes:** deleting from the source but not from the lake,
warehouse, or ML features; forgetting time travel and backups; retention
defined but never enforced; erasure implemented as a manual script run by
one person.

---

### Topic 10 — [Data incident response and post-mortems](10-data-incident-response-and-postmortems.md)

**Why last:** Despite every control, incidents happen: wrong numbers in a
board report, a pipeline down during month-end, a leaked table. How a team
responds — and learns — decides whether trust in the data survives.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a **data incident** is: wrong, late, missing, or exposed data that affects consumers |
| Basics | **Severity levels** by impact (critical dataset tier, number of consumers, regulatory exposure, financial impact) |
| Basics | Detection sources: alerts (Topic 03), quality checks (Module 2.11), consumers reporting problems, and security signals |
| Intermediate | **Incident roles**: incident commander, operations lead, communications lead, and scribe |
| Intermediate | The response flow: **triage** → **contain** (pause pipelines, block publishing with circuit breakers or WAP, revoke access) → **scope** with lineage (Topic 04) → **fix** → **recover** (backfills from Module 2.12, restores and time travel from Module 2.15) → **verify** with reconciliation (Module 2.11) → **close** |
| Intermediate | **Communication**: status updates to stakeholders at a regular cadence, affected datasets and time ranges, and all-clear notices |
| Advanced | **Security and privacy incidents**: leaked credentials (Module 2.18) or exposed personal data — preserving evidence, involving security and privacy teams, and regulatory notification deadlines (e.g. GDPR's 72-hour notification to the authority for qualifying breaches) |
| Advanced | **Blameless post-mortems**: timeline, impact, root cause and contributing factors (e.g. "5 whys"), what went well, and action items with owners and dates |
| Advanced | Follow-through: action items become tests (Module 2.19), checks (Module 2.11), alerts (Topic 03), and runbook updates |
| Advanced | Metrics: time to detect, time to mitigate, time to resolve, and repeat-incident rate |
| Advanced | **Game days**: rehearsing incidents deliberately to test detection, runbooks, and communication |

**How to learn it**

1. Read the topic file.
2. Read several public post-mortems from well-known companies and extract
   the structure and the action items.
3. Write incident and communication templates before you need them.

**Hands-on exercise — `operations/incidents/`**

1. Write templates: incident declaration, stakeholder update, all-clear,
   and post-mortem.
2. Run a **game day** with at least two scenarios: (a) a source sends
   amounts in cents instead of currency units for two days, inflating
   revenue in gold; (b) a pipeline role accidentally exposes a PII column
   to all analysts.
3. For each: detect with your signals, contain (pause, block publish,
   revoke access), scope with lineage and access logs, fix, recover with
   backfills or restores, verify with reconciliation, and communicate.
4. Write a blameless post-mortem for each with timeline, root causes,
   contributing factors, and action items.
5. Implement at least three action items (a new check, a new test, an
   improved alert or runbook).
6. Record detection, mitigation, and resolution times, and compare them
   with a second run of the drill after your fixes.

**Checkpoint:**

- [ ] Classify incidents by severity and assign roles.
- [ ] Contain, scope, fix, recover, and verify a data incident.
- [ ] Communicate clearly with stakeholders during an incident.
- [ ] Handle privacy and security incidents with the right escalation.
- [ ] Write blameless post-mortems and follow through on actions.

**Common mistakes:** fixing silently without telling consumers; blaming
individuals; post-mortems with no owned action items; restoring data
without verifying it; treating a data exposure as "just a bug".

---

## 10. Consolidate — practice questions

When all ten topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. State the operational, governance, or security question being asked.
2. Identify the signals, metadata, and controls involved.
3. Design the solution across the platform (not in one tool only).
4. Simulate the failure or request and measure detection and response
   time.
5. Produce evidence: dashboards, lineage, audit logs, deletion records, or
   a post-mortem.
6. Explain the answer to an engineer, a data consumer, and a privacy or
   security officer.

---

## 11. Module mini-project — an observable, governed, secure data platform

This is the proof that you have finished the module.

**Scenario:** An upcoming privacy audit and a recent revenue incident have
made leadership ask three questions: *Can you see problems before users
do? Can you show where every number and every piece of personal data comes
from and goes? Can you protect, restrict, and delete personal data on
request — and prove it?*

Extend your platform (Modules 2.9–2.19) with:

1. **Observability** — pipeline metrics and a unified run-metadata table;
   structured logs correlated by run id; OpenTelemetry traces across the
   API extractor, Kafka, and Spark; Grafana dashboards with SLOs.
2. **Alerting** — symptom-based, tiered alerts with runbooks; SLO
   burn-rate alerting for gold freshness; routing, grouping, and
   inhibition; an alert-quality review after a simulated week.
3. **Lineage and catalog** — OpenLineage from Airflow, Spark, dbt, and
   custom jobs into Marquez; a catalog (OpenMetadata or DataHub) with
   owners, domains, glossary, quality status, deprecations, and metadata as
   code published from CI.
4. **Privacy** — a PII scanner feeding reviewed tags; pseudonymisation,
   tokenisation, and generalisation applied in silver; a CI check for
   unclassified PII-like columns; PII-free logs and traces.
5. **Encryption** — verified TLS on every connection; envelope-encrypted
   sensitive fields; key rotation; per-customer crypto-shredding.
6. **Access control** — row-level security and tag-based masking policies
   in PostgreSQL and your warehouse or lakehouse catalog; automated access
   tests in CI; audit-log reports and a time-bound access workflow.
7. **Retention and erasure** — retention metadata and enforcement jobs; an
   automated erasure pipeline covering sources, lakehouse (with physical
   purge), warehouse, Kafka, ML features, logs, and backups (via
   crypto-shredding), producing a deletion certificate; a data-access
   export.
8. **Incident readiness** — templates, a game day with two scenarios,
   blameless post-mortems, implemented action items, and measured
   detection and resolution times.
9. **Evidence pack** — a folder you could hand to an auditor: data
   inventory, retention schedule, access matrix, encryption inventory,
   lineage for PII, deletion certificates, and post-mortems.

**Grading yourself:** injected failures are detected by alerts before any
consumer notices; any gold number can be traced to its sources in minutes;
no role can see personal data it is not approved for, and tests prove it;
an erasure request removes a person from every system with verifiable
evidence; and a data incident can be contained, scoped, recovered, and
explained within your agreed response times.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.21 when you can tick every box without looking at your
notes:

- [ ] I can instrument pipelines with metrics, run metadata, and correlated
      logs.
- [ ] I can trace work across services, Kafka, and pipeline tasks.
- [ ] I can design actionable, tiered, SLO-based alerting and on-call.
- [ ] I can capture and use lineage with OpenLineage.
- [ ] I can run a catalog with ownership, glossary, classification, and
      metadata as code.
- [ ] I can detect PII and apply the right protection technique.
- [ ] I can apply encryption at rest and in transit, including envelope
      encryption and crypto-shredding.
- [ ] I can implement and test row- and column-level access control.
- [ ] I can enforce retention and run provable erasure across the platform.
- [ ] I can lead data incident response and write blameless post-mortems.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Prometheus and Grafana documentation — instrumentation, naming, labels, alerting rules, Alertmanager | 01, 03 |
| OpenTelemetry documentation — Python SDK, instrumentation, Collector, context propagation, semantic conventions | 02 |
| Google's *Site Reliability Engineering* and *The Site Reliability Workbook* (free online) — SLOs, alerting on burn rates, on-call, incident management, post-mortem culture | 01, 03, 10 |
| OpenLineage specification and integration documentation; Marquez documentation | 04 |
| OpenMetadata and DataHub documentation | 05 |
| Microsoft Presidio documentation | 06 |
| NIST SP 800-57 (key management) — overview sections; cloud KMS documentation on envelope encryption | 07 |
| PostgreSQL documentation — row security policies; warehouse documentation on masking and row-access policies | 08 |
| GDPR text (Regulation (EU) 2016/679) and guidance from data protection authorities; India's Digital Personal Data Protection Act, 2023 | 09 |
| *Data Governance: The Definitive Guide* — Evren Eryurek, Uri Gilad, Valliappa Lakshmanan, Anita Kibunguchy-Grant, Jessi Ashdown (O'Reilly) | 04, 05, 08, 09 |
| *Data Quality Fundamentals* — Barr Moses, Lior Gavish, Molly Vorwerck (O'Reilly), chapters on incident management | 03, 10 |
| OWASP cheat sheets — Logging, Cryptographic Storage, Transport Layer Security | 01, 06, 07 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Cost metrics, dashboards, and cost-spike alerts | 2.21 Performance, Scaling, and Cost Optimization |
| Governed serving: semantic layers, feature stores, and access-controlled APIs; PII and lineage in AI data pipelines | 2.22 Serving Data for Analytics, ML, and AI |

Trust in data is earned slowly and lost in one incident. The habits you
build here — measure what consumers feel, alert only when someone must act,
capture lineage automatically, classify and protect personal data from the
moment it arrives, enforce access with tests, delete provably, and learn
from every incident without blame — are what make a data platform not just
powerful, but safe to depend on.
