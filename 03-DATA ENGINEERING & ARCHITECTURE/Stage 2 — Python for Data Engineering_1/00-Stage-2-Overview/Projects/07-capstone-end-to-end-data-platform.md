# Project Roadmap — Capstone: End-to-End Data Platform

This is the end-to-end roadmap for **Stage 2 Project 07: the Capstone —
End-to-End Data Platform**. It is the final project of **Python for Data
Engineering**. It brings everything from the 22 modules and Projects 01–06
together into **one coherent, production-grade data platform**: data flows
in from APIs, databases, files, and event streams; it is stored in a
governed lakehouse and warehouse; it is transformed, validated, and served
to dashboards, APIs, ML models, and an AI assistant; and the whole platform
is deployed as code, secured, observed, cost-controlled, recoverable, and
operable by a team.

Earlier projects taught you to build **pipelines**. The capstone teaches you
to build and run a **platform**: to make many components agree on
conventions, share infrastructure and governance, survive failures across
component boundaries, and deliver measurable value to real consumers.

It is written as a sequence of **phases and milestones**. Each milestone has
a goal, tasks, deliverables, and **acceptance criteria**. The final phase
includes a **launch readiness review**, a multi-incident **game day**, and a
period of simulated operation — because a platform is only production grade
once it has been run, broken, and recovered.

---

## 1. Why this capstone matters

Most data platforms fail not inside a single pipeline, but **between**
them:

- two teams use different table formats, catalogs, and naming, so nothing
  joins cleanly;
- the ingestion team, the analytics team, and the ML team each define
  "revenue" and "active customer" differently;
- an upstream failure pages five teams, none of whom own it;
- a GDPR erasure request is honoured in the warehouse but not in Kafka,
  the lake's old snapshots, the feature store, or the vector index;
- infrastructure was created by hand, so staging does not match
  production;
- nobody knows what the platform costs per consumer;
- the catalog database has no backups, and one disk failure loses all
  table metadata.

The capstone makes you design and prove a platform that avoids these
failures — the work of a senior or lead data engineer.

---

## 2. Goal and scope

### Goal

Deliver **ShopLite Data Platform v1.0**: a single, integrated platform that
meets the service levels of six consumer groups (Section 4), built from your
earlier projects plus new platform-wide capabilities, and demonstrated
through a launch review, a game day, and a period of operation.

### What the platform includes

| Capability | Built from | New in the capstone |
| --- | --- | --- |
| API ingestion | Project 01 | Shared conventions, contracts registered centrally |
| Database CDC | Project 02 | Shared catalog and table format, erasure across Kafka and the lake |
| Warehouse ELT and marts | Project 03 | Marts on the platform's chosen SQL engine, semantic layer |
| Lakehouse medallion | Project 04 | Conformed dimensions shared with marts and streaming |
| Real-time streaming | Project 05 | Integrated with lake, serving, and reconciliation |
| Data quality and observability | Project 06 | Applied to **every** dataset, gates everywhere, one incident flow |
| Serving | Module 2.22 | Data API, cached aggregates, semantic metrics, feature store, vector retrieval |
| Cloud, infrastructure, delivery | Modules 2.17–2.18 | Whole platform as code, environments, CI/CD across components |
| Governance and security | Module 2.20 | Classification, access control, encryption, platform-wide erasure, evidence pack |
| Performance and cost | Module 2.21 | Unit economics per consumer, platform budget |
| Reliability | Modules 2.13, 2.16, 2.20 | Platform SLOs, backups, disaster recovery, on-call, game day |

### If you have not built every earlier project

The capstone assumes you completed **at least four of Projects 01–06**. For
any missing project, build a **minimal version** during the relevant
milestone (the milestone lists the minimum needed) — the capstone's focus is
integration, consistency, and operations, not re-implementing every feature
at full depth.

### Delivery options

| Option | Where it runs | When to choose it |
| --- | --- | --- |
| **A — Local "cloud-like"** | Docker Compose and a local Kubernetes cluster (kind/k3d), MinIO, local Kafka, PostgreSQL as warehouse | No cloud budget; all concepts still demonstrated |
| **B — Real cloud** | One cloud provider, managed or self-managed services, created with Terraform, strict budget alerts | Best portfolio value; requires careful cost control and teardown |

You may also mix them: platform in the cloud for a few weeks of operation,
local for development and tests.

---

## 3. Prerequisites

- **Modules 2.1–2.22** completed.
- **At least four of Projects 01–06** completed (see above for gaps).
- A cloud account with budgets and alerts if you choose Option B
  (Module 2.17).

**Estimated effort:** 8–12 weeks at 8–10 hours per week, depending on how
many earlier projects you can reuse and which delivery option you choose.
A scoped **minimum viable platform (MVP)** is defined in M0 so that you can
finish a complete, production-grade core before adding breadth.

---

## 4. The scenario

ShopLite is launching **Data Platform v1.0**. You play the role of the lead
data engineer (and every other role where needed). Six consumer groups have
signed up:

| Consumer | Product they receive | Key service level |
| --- | --- | --- |
| **Finance** | Daily revenue, refunds, and margin marts; month-end close | Published by **07:00**; reconciles with source systems; no silent restatements |
| **Operations** | Live dashboard (orders per minute, active sessions, conversion) | **≤ 10 s** p95 latency |
| **Risk** | Real-time alerts (payment failure bursts, unpaid orders) | **≤ 5 s** p95; no duplicate notifications |
| **Marketing and analysts** | Star schema, certified metrics through a semantic layer, BI dashboards | Metrics identical across every interface; published by 09:00 |
| **Data science** | Churn features (offline and online), reproducible training datasets | Point-in-time correct; online features ≤ 50 ms p95; daily freshness |
| **Customer support (AI assistant)** | Retrieval API over help-centre articles and support tickets | Permission-aware retrieval; deleted content never returned; recall@5 above target |
| **Partners (external)** | Order-status data API | Authenticated, rate-limited, 99.5% availability in business hours |

### Platform-wide non-functional requirements (write them down in M0)

- **Security:** least privilege for every workload and person; no
  long-lived credentials; encryption in transit and at rest.
- **Privacy:** personal data classified and protected; erasure requests
  completed across **every** system within **30 days** (target 7) with
  evidence; data minimisation; relevant regulations considered (e.g. GDPR,
  India's DPDP Act) — with a note that legal interpretation belongs to
  legal and privacy teams.
- **Reliability:** SLOs per data product with error budgets; on-call and
  runbooks; **backups** of every stateful metadata store; recovery point
  objective (RPO) and recovery time objective (RTO) targets per component,
  proven by a restore drill.
- **Delivery:** every component and all infrastructure deployed as code
  through CI/CD with `dev`, `staging`, and `prod`.
- **Observability:** platform health, data quality, lineage, and cost
  visible on dashboards; incidents detected by the platform before
  consumers.
- **Cost:** a monthly budget for the whole platform and a cost per consumer
  product.

---

## 5. Target architecture

```text
                                  ShopLite Data Platform v1.0
 ─────────────────────────────────────────────────────────────────────────────────────────
 SOURCES           Commerce API · Orders DB (PostgreSQL) · Partner files · App & service events
                        │ P01           │ P02 (Debezium)     │ files        │ P05 producers
 INGEST                 ▼               ▼                    ▼              ▼
                   API ingestion     Kafka (CDC topics, event topics, DLQs) + schema registry
                        │               │                                    │
 STORE & PROCESS        ▼               ▼                                    ▼
                   ┌──────────────── Lakehouse (one table format, one catalog) ─────────────────┐
                   │ bronze (raw, lossless) → silver (mirrors, cleaned, conformed, SCD2)        │
                   │                        → gold (facts, aggregates, features, OBT)   [P02,P04]│
                   └──────────────────────────────┬─────────────────────────────────────────────┘
                   Streaming (Spark/Flink): live metrics, alerts, archive, reconciliation [P05]
                                                  │
 TRANSFORM         dbt marts (finance, marketing, core) on the chosen SQL engine + semantic layer [P03]
                                                  │
 SERVE             Data API (partners, support) · cached aggregates · semantic metrics · BI
                   Feature store (offline/online) · Vector store + retrieval API              [2.22]
 ─────────────────────────────────────────────────────────────────────────────────────────
 CROSS-CUTTING     Orchestration (Airflow asset graph) · Quality platform & gates [P06]
                   Catalog & lineage · Classification, access control, encryption, erasure
                   Observability (metrics, traces, logs, SLOs, alerts, on-call)
                   Infrastructure as code · CI/CD · environments · secrets
                   Backups & disaster recovery · FinOps
```

---

## 6. Repository and team structure

Choose a **monorepo** (recommended for a one-person capstone) or several
repositories with a shared conventions package. Record the choice in an ADR.

```text
shoplite-data-platform/
├── README.md                        # the platform's front door
├── docs/
│   ├── product/                     # vision, consumers, data products, SLAs, NFRs, MVP scope
│   ├── architecture/                # diagrams, component catalogue, integration contracts
│   ├── adr/                         # platform-wide decisions (numbered)
│   ├── conventions/                 # naming, metadata columns, tiers, environments
│   ├── governance/                  # classification, access matrix, retention, erasure design, evidence pack
│   ├── reliability/                 # SLOs, error budgets, on-call, backups, DR plan, game-day reports
│   ├── finops/                      # budgets, cost model, monthly reports
│   ├── runbooks/                    # one per component and per alert
│   └── launch/                      # readiness checklist, reviews, go/no-go, operations log, retrospective
├── infra/                           # Terraform modules and environments (dev, staging, prod)
├── platform/                        # shared libraries: config, run context, logging, lineage, contracts client
├── ingestion/                       # P01 API ingestion, file ingestion
├── cdc/                             # P02 connectors, CDC jobs
├── streaming/                       # P05 producers, validators, Spark/Flink jobs
├── lakehouse/                       # P04 medallion jobs, maintenance
├── transformation/                  # P03 dbt project, semantic layer definitions
├── serving/                         # data API, caches, feature store repo, vector pipeline, retrieval API
├── quality/                         # P06 platform, contracts/ for every dataset
├── orchestration/                   # Airflow DAGs spanning the platform
├── tests/                           # platform-level e2e, contract, load, chaos tests
└── .github/workflows/               # CI per component + platform e2e + infra
```

**Roles.** Even if you work alone, write a short **RACI** (who is
responsible, accountable, consulted, informed) for each data product and
component. It drives alert routing, catalog ownership, and approvals.

---

## 7. Phases and milestones overview

```text
Phase 1 — Plan and design
  M0   Programme framing: product, consumers, SLAs, NFRs, MVP, risks
  M1   Target architecture, conventions, and platform-wide decisions
  M2   Foundations: infrastructure as code, environments, identity, CI/CD, observability

Phase 2 — Integrate the data flows
  M3   Unified ingestion layer
  M4   Unified lakehouse and conformed data
  M5   Transformation, marts, and the semantic layer
  M6   Real-time layer integrated with batch
  M7   Platform-wide orchestration

Phase 3 — Trust and serving
  M8   Quality platform everywhere
  M9   Governance, security, and platform-wide privacy
  M10  Serving layer for analytics, partners, ML, and AI

Phase 4 — Production readiness
  M11  Platform-wide testing and the golden path
  M12  Reliability, backups, and disaster recovery
  M13  Performance and FinOps
  M14  Launch readiness review and game day

Phase 5 — Launch, operate, and hand over
  M15  Launch and operate
  M16  Documentation, case study, and presentation
  (M17 Optional stretch goals)
```

---

## 8. Phase 1 — Plan and design

### M0 — Programme framing: product, consumers, SLAs, NFRs, MVP, and risks

**Goal:** A clear definition of the platform as a set of **data products**
with consumers, service levels, and a realistic scope.

**Tasks**

1. Write a one-page **product vision**: what problems the platform solves,
   for whom, and how success is measured (adoption, SLA compliance,
   incidents prevented, cost per consumer).
2. Describe each **data product** (Section 4): owner, consumers, contents,
   interface (table, API, dashboard, feature, retrieval), SLA, tier, and
   support hours.
3. Write the **non-functional requirements** (Section 4) with numbers:
   RPO/RTO per stateful component, availability, security, privacy, cost.
4. Define the **MVP**: the smallest end-to-end slice that is complete and
   production grade (for example: orders CDC + finance marts + one live
   metric + quality gates + one API + governance basics + IaC + DR for
   metadata stores). Everything else is scheduled after the MVP.
5. Write a **risk register** (e.g. cloud cost overrun, hardware limits,
   integration effort, time) with mitigations.
6. Write the **RACI** and a milestone plan with dates.

**Acceptance criteria**

- [ ] Every data product has an owner, consumers, interface, SLA, and tier.
- [ ] NFRs and RPO/RTO targets are numeric.
- [ ] The MVP is small enough to finish within half the planned time.
- [ ] The top risks have mitigations.

---

### M1 — Target architecture, conventions, and platform-wide decisions

**Goal:** One architecture and one set of conventions that every component
follows — reconciling the different choices made in earlier projects.

**Tasks**

1. Draw architecture views: context (systems and consumers), containers
   (components and data stores), and the main data flows; keep them in
   `docs/architecture/`.
2. Write a **component catalogue**: purpose, owner, inputs, outputs,
   state, SLOs, dependencies, runbook link.
3. Write **integration contracts** between components: for each hand-off
   (e.g. CDC → silver, silver → dbt marts, gold → feature store, stream →
   serving), the dataset or topic, schema contract, freshness, and who
   alerts whom when it breaks.
4. Make and record **platform-wide decisions** (ADRs), for example:
   - **one table format** (Iceberg or Delta) — or both with a justified
     interoperability approach — and **one catalog**;
   - the SQL engine for marts (cloud warehouse, or a lakehouse SQL engine
     for dbt) and how warehouse and lakehouse stay consistent;
   - one orchestrator, one schema registry, one quality platform;
   - identity model (workload identity everywhere, no static keys);
   - environment strategy and promotion rules;
   - monorepo vs polyrepo.
5. Write **conventions**: dataset and topic naming, standard metadata
   columns (`_run_id`, `_ingested_at`, `_source`, …), tiers, time zones
   (UTC), key and surrogate key rules, contract format, tagging for cost
   and classification.
6. Build the enterprise **bus matrix** and list **conformed dimensions**
   (customer, product, date, channel, country) shared by batch, streaming,
   marts, features, and serving (Module 2.8).
7. Design **data classification** and the **access matrix** (roles ×
   data products × columns × rows — Module 2.20).

**Acceptance criteria**

- [ ] Every component and every hand-off is documented with an owner and a
      contract.
- [ ] Conflicting choices from earlier projects are resolved in ADRs.
- [ ] Conformed dimensions have one definition used everywhere.
- [ ] The access matrix covers every data product.

---

### M2 — Foundations: infrastructure as code, environments, identity, CI/CD, observability

**Goal:** The shared platform foundation exists **as code** in every
environment before any data flows through it.

**Tasks**

1. **Infrastructure as code** (Terraform — Module 2.18): object storage
   with versioning, encryption, and lifecycle rules; the catalog; Kafka and
   the schema registry; compute (Kubernetes cluster or managed services);
   the warehouse or SQL engine; metadata databases (Airflow, catalog,
   quality platform, feature registry); secrets; networking basics — for
   `dev`, `staging`, and `prod`, with remote locked state and
   `prevent_destroy` on data stores.
2. **Identity:** one role or service account per component and per
   environment with least-privilege policies derived from the access
   matrix; workload identity for runtime; OIDC federation for CI (Module
   2.17).
3. **Secrets:** all credentials in a secrets manager, delivered at runtime
   (Module 2.18).
4. **CI/CD skeleton:** per-component pipelines (lint, test, build, scan,
   deploy) and a platform pipeline that deploys infrastructure changes with
   plans reviewed in pull requests; promotion with approvals to `prod`.
5. **Observability foundation:** metrics, logs, and traces collection;
   dashboards and alert routing skeleton; the shared `platform` library for
   run context, structured logging, metrics, and lineage emission (Module
   2.20).
6. **Budgets and cost tags** on every resource (Module 2.21).
7. A **teardown procedure** for non-production environments.

**Acceptance criteria**

- [ ] `dev` and `staging` can be created and destroyed from code alone;
      `prod` is created only through the approved pipeline.
- [ ] No long-lived credentials exist anywhere.
- [ ] Every resource is tagged with component, environment, and owner.
- [ ] A hello-world job in each runtime (batch, streaming, API) emits logs,
      metrics, traces, and lineage visible on dashboards.

---

## 9. Phase 2 — Integrate the data flows

### M3 — Unified ingestion layer

**Goal:** Every source enters the platform through a consistent, contracted,
observable ingestion path.

**Tasks**

1. Bring in **Project 01** (API ingestion), **Project 02** (CDC), file
   drops, and **Project 05** producers, adapting them to the platform
   conventions: naming, metadata columns, run context, logging, metrics,
   lineage.
2. Register a **contract** for every source dataset and topic in the quality
   platform (M8 will enforce them).
3. Standardise **bronze**: lossless, append-only, provenance columns,
   partitioning, retention — in the chosen table format and catalog.
4. Standardise **state** (watermarks, offsets, file registries, replication
   slots) and document where each lives and how it is backed up (M12).
5. *Minimum if a project is missing:* one API endpoint with incremental
   extraction; CDC for `orders` and `customers`; one event stream.

**Acceptance criteria**

- [ ] All sources land in bronze with identical metadata conventions.
- [ ] Every source has a registered contract and an owner.
- [ ] Every ingestion component appears in lineage and on the platform
      dashboard.

---

### M4 — Unified lakehouse and conformed data

**Goal:** One lakehouse, one catalog, and one version of each business
entity.

**Tasks**

1. Consolidate **Project 02** mirrors and **Project 04** medallion tables
   onto the chosen format and catalog (migrate or use an interoperability
   feature where you chose both).
2. Build **conformed dimensions** (customer SCD Type 2, product, date,
   channel, country) once in silver and use them in every downstream
   product — marts, streaming enrichment, features, and serving.
3. Unify **identity**: customer keys from CDC, API, events, and files map
   to one durable customer key (Modules 2.8, 2.12).
4. Apply the **maintenance policies** (compaction, clustering, snapshot
   expiry, orphan cleanup) platform-wide from one orchestrated job family.
5. *Minimum if a project is missing:* bronze → silver for orders,
   customers, and events; one gold aggregate.

**Acceptance criteria**

- [ ] There is exactly one definition of each conformed dimension, and
      every consumer product uses it.
- [ ] Any silver table is readable by Spark, the SQL engine, and a
      lightweight engine (DuckDB/Polars) through the catalog.
- [ ] Table health stays within targets across all tables.

---

### M5 — Transformation, marts, and the semantic layer

**Goal:** Trusted marts and one set of certified metrics used by every
interface.

**Tasks**

1. Integrate **Project 03**: dbt models on the chosen SQL engine reading the
   lakehouse (or loaded warehouse tables — per your ADR), with staging on
   silver, marts for finance, marketing, and core.
2. Keep **write–audit–publish** for marts, the `data_status` view, and
   month-end closing with restatements.
3. Define **certified metrics** (net revenue, orders, AOV, ROAS, active
   customers, conversion) in the **semantic layer** (Module 2.22) and make
   dashboards, the data API, and the AI assistant's metric questions use it.
4. Build finance and marketing **BI dashboards** with freshness indicators.
5. *Minimum if a project is missing:* staging, a finance mart, two
   certified metrics, and WAP.

**Acceptance criteria**

- [ ] The same metric returns the same number in the BI tool, the API, and
      the semantic layer query.
- [ ] Finance marts reconcile with the source database and are published
      by 07:00 in a normal day.
- [ ] Failing marts are never published.

---

### M6 — Real-time layer integrated with batch

**Goal:** Real-time products that agree with the batch truth.

**Tasks**

1. Integrate **Project 05**: live metrics and risk alerts using the
   platform's topics, schemas, conformed dimensions (for enrichment), and
   observability.
2. Archive every event to bronze (shared with batch) and run **daily
   reconciliation** between final real-time windows and batch gold (Module
   2.16).
3. Feed real-time aggregates to the **serving layer** (M10) and alerts to the
   risk team's notification channel.
4. Decide, per use case, **streaming vs micro-batch** based on the SLA and
   cost (ADR) — keep streaming only where it pays off.
5. *Minimum if a project is missing:* one live metric with watermarks and
   one alert rule, with reconciliation.

**Acceptance criteria**

- [ ] Real-time and batch numbers reconcile for final windows.
- [ ] Latency SLAs for operations and risk are met.
- [ ] Every streaming use case has a written cost/latency justification.

---

### M7 — Platform-wide orchestration

**Goal:** One orchestration model that coordinates the whole platform —
across domains and components — with safe backfills.

**Tasks**

1. Model the platform as an **asset graph** in Airflow (Module 2.13):
   ingestion assets → bronze → silver → gold/marts → serving products;
   downstream work triggered by upstream asset updates rather than timing
   guesses.
2. Define **cross-domain dependencies** explicitly (e.g. the feature store
   depends on silver customers and orders; finance marts depend on refunds
   and FX) with gates between them (M8).
3. Use **pools and priorities** so tier-1 products (finance, risk) are never
   starved by backfills or maintenance.
4. Define a **platform backfill procedure**: which assets to rebuild in which
   order after a logic change or a source correction, with shadow builds,
   data diffs, and publication.
5. Consolidate **maintenance** DAGs (lakehouse tables, Kafka compaction
   checks, warehouse housekeeping, cache refreshes).

**Acceptance criteria**

- [ ] A normal day runs end to end without manual steps and meets every
      batch SLA.
- [ ] A 30-day backfill of one domain completes without breaching any
      daily SLA.
- [ ] The asset graph shows every product's upstream dependencies.

---

## 10. Phase 3 — Trust and serving

### M8 — Quality platform everywhere

**Goal:** Every dataset is covered by contracts, checks, and monitors, and
every publication passes through a gate.

**Tasks**

1. Integrate **Project 06** across all systems: warehouse, lakehouse,
   files, Kafka, feature store, and vector store (freshness and volume
   checks at minimum).
2. Assign every dataset a **tier** and apply the tier's required checks,
   monitors, alert severity, and gate policy.
3. Wire **gates** into every publishing step (marts, gold, features,
   serving caches, vector index updates) and **circuit breakers** between
   domains.
4. Route incidents by the RACI; group them with lineage so one upstream
   failure creates one incident.
5. *Minimum if Project 06 is missing:* contracts for tier-1 datasets,
   freshness and volume monitors, dbt/Spark checks, and gates for marts and
   gold, with alert routing.

**Acceptance criteria**

- [ ] 100% of tier-1 datasets have contracts, checks, monitors, and gates.
- [ ] An upstream incident is detected before any consumer notices,
      produces one grouped incident, and blocks affected publications.

---

### M9 — Governance, security, and platform-wide privacy

**Goal:** The platform is secure by default and can prove how it handles
personal data.

**Tasks**

1. **Catalog and lineage:** every dataset, topic, feature, and API in the
   catalog with owner, description, classification, tier, quality status,
   and end-to-end lineage (Module 2.20).
2. **Classification and protection:** run the PII scanner across all
   stores; apply masking, pseudonymisation, tokenisation, and
   generalisation according to the classification.
3. **Access control:** implement the access matrix with row- and
   column-level controls in the SQL engine and catalog; access tests in CI;
   audit logs reviewed.
4. **Encryption:** TLS on every connection; encryption at rest with managed
   keys; envelope or field-level encryption for the most sensitive fields.
5. **Retention:** retention policies enforced per dataset and topic.
6. **Platform-wide erasure:** one erasure workflow that removes or
   crypto-shreds a person's data in the source database (via application),
   Kafka topics, bronze/silver/gold (including old snapshots), the
   warehouse (including time travel), the feature store (offline and
   online), the vector store and its source documents, caches, logs, test
   data, and **backups** — producing a deletion certificate.
7. Build the **evidence pack** for an auditor: data inventory, retention
   schedule, access matrix, encryption inventory, lineage of personal data,
   deletion certificates, incident post-mortems.

**Acceptance criteria**

- [ ] Access tests prove each role sees only what it should.
- [ ] An erasure request is completed across every system, verified by
      scans, within the target time.
- [ ] The evidence pack is complete and consistent with the running
      platform.

---

### M10 — Serving layer for analytics, partners, ML, and AI

**Goal:** Every consumer gets its product through a governed, tested
interface that meets its SLA.

**Tasks** (Module 2.22)

1. **Data API** for partners and support: order status, authentication,
   rate limits, row-level rules, pagination, freshness metadata, and
   contract-tested OpenAPI schema.
2. **Cached aggregates** for dashboards with version-aware, permission-aware
   caching and event-driven invalidation.
3. **Semantic layer access** for BI and a governed "ask a metric" interface.
4. **Feature store:** churn features from conformed silver/gold data,
   point-in-time-correct training datasets pinned to table versions, online
   materialisation, and an online feature endpoint; skew and drift
   monitoring.
5. **Vector pipeline and retrieval API** for the support assistant:
   incremental ingestion of help articles and tickets, PII scanning,
   chunking, embeddings, hybrid retrieval with permission filtering,
   deletion support, and a retrieval evaluation set with a CI quality gate.
6. A **serving contract** per consumer, load-tested against its SLA.

**Acceptance criteria**

- [ ] Every serving interface meets its latency and availability targets
      under load.
- [ ] Features are reproducible and leak-free; online values match offline
      values.
- [ ] Retrieval respects permissions and deletions and meets its quality
      threshold.

---

## 11. Phase 4 — Production readiness

### M11 — Platform-wide testing and the golden path

**Goal:** Automated proof that the platform works end to end — not just
component by component.

**Tasks**

1. Write the **platform test strategy**: which tests each component owns
   (from Projects 01–06), and which tests the platform owns (integration
   contracts, end-to-end flows, load, chaos) — Module 2.19.
2. Build the **golden-path test**: a synthetic customer's journey — sign-up
   (source DB), browsing events (stream), an order and payment, a refund
   (API), a partner shipment file — traced through ingestion, lakehouse,
   marts, real-time metrics, alerts, features, the data API, and the
   retrieval index; assert every product reflects the journey correctly.
3. Add **contract tests** for every integration contract from M1 (schema,
   freshness, semantics).
4. Add **load tests** for serving interfaces and **scale tests** for batch
   and streaming at projected one-year volumes.
5. Run the golden path in CI on `staging` for every release and on a
   schedule in `prod` (read-only canary checks and a synthetic canary
   customer).

**Acceptance criteria**

- [ ] The golden-path test passes in `staging` and runs as a canary in
      `prod`.
- [ ] Breaking any integration contract fails CI before deployment.
- [ ] Load and scale tests meet SLAs with documented headroom.

---

### M12 — Reliability, backups, and disaster recovery

**Goal:** The platform meets its SLOs and can recover from losing any
single component — within its RPO and RTO.

**Tasks**

1. Define **SLOs and error budgets** per data product and platform
   component; build SLO dashboards and burn-rate alerts (Module 2.20).
2. Set up **on-call**: rotation (even if simulated), escalation, alert
   routing from the RACI, and a runbook index covering every paging alert.
3. **Backups** of every stateful store: source database, Airflow metadata,
   catalog database, quality-platform database, feature registry, schema
   registry, vector store, secrets metadata — with encryption and retention
   aligned with erasure rules; object-storage versioning for the lake.
4. **Disaster recovery plan** with RPO/RTO per component and a recovery
   order (for example: identity and secrets → catalog → metadata DBs →
   Kafka → orchestration → pipelines → serving).
5. **DR drills:**
   - restore the catalog database from backup and verify every table is
     readable;
   - lose the Kafka cluster; rebuild and recover streaming state from the
     archive and replay;
   - restore the Airflow metadata database and resume schedules without
     duplicate runs;
   - rebuild an environment from Terraform and backups.
6. Document the results against RPO/RTO targets and fix gaps.

**Acceptance criteria**

- [ ] Every stateful store has tested backups.
- [ ] DR drills meet RPO/RTO targets (or gaps are documented with a plan).
- [ ] SLO dashboards and burn-rate alerts exist for every data product.

---

### M13 — Performance and FinOps

**Goal:** The platform is fast enough and affordable — and you know exactly
what each product costs.

**Tasks** (Module 2.21)

1. **Cost model:** cost per data product and consumer (storage, compute,
   streaming, warehouse, serving, observability), and unit costs (cost per
   daily finance run, per million events, per 1,000 API calls, per
   retrieval query).
2. **Optimise** the largest costs with evidence: right-sizing, spot capacity
   for retryable batch, auto-suspend, incremental processing instead of
   rebuilds, streaming-to-micro-batch where SLAs allow, lifecycle rules,
   pushdown and clustering fixes.
3. **Performance:** benchmark critical paths (finance daily run, streaming
   latency, API p95, feature lookups, retrieval) and remove bottlenecks.
4. **Budgets and anomaly alerts** per product; a monthly FinOps report.

**Acceptance criteria**

- [ ] The platform runs within its monthly budget with a documented margin.
- [ ] Every product has a known unit cost.
- [ ] At least three evidence-backed optimisations are implemented, with
      measured savings and no SLA regressions.

---

### M14 — Launch readiness review and game day

**Goal:** An honest, evidence-based decision that the platform is ready for
production.

**Tasks**

1. Complete a **production readiness checklist** for every component and
   data product: owner, SLOs, dashboards, alerts, runbooks, tests, backups,
   security review, privacy review, cost, documentation.
2. Hold (or simulate in writing) three **reviews**:
   - **architecture review** — ADRs, single points of failure, scaling;
   - **security review** — identities, secrets, network exposure,
     encryption, access tests;
   - **privacy review** — classification, minimisation, retention, erasure
     evidence.
3. Run a **game day**: several injected incidents at once, for example a
   partner file with amounts ×100, a CDC connector failure during a traffic
   burst, a schema change in the order service, the catalog database
   restarting, and an erasure request arriving during the incident. Measure
   detection, communication, containment, recovery, and verification.
4. Write **post-mortems** for the game day and implement the most important
   action items.
5. Record a **go/no-go decision** with open risks accepted explicitly.

**Acceptance criteria**

- [ ] Every checklist item is complete or has an accepted risk with an
      owner and date.
- [ ] Game-day incidents are detected by the platform before consumers
      would notice, and all products recover to correct states.
- [ ] Post-mortem action items are tracked, and the critical ones are done.

---

## 12. Phase 5 — Launch, operate, and hand over

### M15 — Launch and operate

**Goal:** Prove the platform in operation, not only in tests.

**Tasks**

1. **Launch** (promote to `prod`) with a written launch plan, rollback plan,
   and consumer communication.
2. **Operate for at least two weeks** (real time, or compressed simulated
   days): daily and streaming workloads with realistic change, injected
   routine incidents, erasure requests, a backfill, a month-end close, and
   a release per week through CI/CD.
3. Keep an **operations log**: incidents, SLO compliance, error budget
   consumption, alerts and their precision, costs, releases, and changes.
4. Run a **weekly review**: SLOs, incidents, cost, quality scorecards, and
   actions.
5. Iterate: fix recurring issues and noisy alerts; tune monitors and
   capacity.

**Acceptance criteria**

- [ ] All tier-1 SLOs are met over the operating period (or breaches are
      explained with post-mortems).
- [ ] Every incident has a post-mortem and tracked actions.
- [ ] Releases are deployed through CI/CD without downtime for consumers.
- [ ] The platform stays within budget during operation.

---

### M16 — Documentation, case study, and presentation

**Goal:** Anyone can understand, operate, and evaluate the platform — and
you can present it convincingly.

**Tasks**

1. Finalise the **platform README** (what it is, architecture, products,
   how to run, how to operate, where everything is documented).
2. Finalise the **architecture document**, **ADR log**, **runbooks**,
   **governance evidence pack**, **reliability report** (SLOs, DR drills,
   game day), and **FinOps report**.
3. Write a **case study** (3–5 pages): problem, architecture, key
   decisions and trade-offs, results (SLA compliance, incidents prevented,
   cost per product), lessons learned, and a roadmap for v2.
4. Record a **demo** (15–20 minutes): the golden path, a live dashboard,
   a blocked bad publication, an incident grouped and resolved, an erasure
   request end to end, a DR restore, and the cost dashboard.
5. Write the **retrospective** for the capstone and for Stage 2 as a whole,
   including your personal data engineering principles.

**Acceptance criteria**

- [ ] A reviewer can run the platform and follow one runbook without your
      help.
- [ ] The case study states measurable results.
- [ ] The demo shows correctness, reliability, governance, and cost — not
      only happy paths.

---

### M17 — Optional stretch goals

- **Multi-region or multi-zone resilience** for tier-1 products, with a
  failover drill.
- **Data mesh:** split the platform into domains (orders, marketing,
  support) with their own data products, contracts, and owners on the
  shared platform.
- **Agent-ready data:** expose governed metrics and retrieval as tools for
  an AI agent with strict permission and audit controls (a bridge to the
  Agentic AI stage).
- **Open-table interoperability:** serve the same gold tables to several
  engines and a warehouse through the catalog without copies.
- **Self-service portal:** a simple UI for onboarding datasets, requesting
  access, and viewing data product status.
- **Open-source contribution:** contribute a fix or documentation
  improvement to one tool you used heavily.

---

## 13. Definition of done

**Value delivered**

- [ ] All six consumer groups receive their data products through governed
      interfaces that meet their SLAs.
- [ ] Certified metrics are identical across every interface.

**Correctness and trust**

- [ ] Source-to-product reconciliation, real-time vs batch reconciliation,
      and the golden-path test pass.
- [ ] Every publication passes quality gates; incidents are detected before
      consumers notice.

**Security and privacy**

- [ ] Least privilege, no long-lived credentials, encryption everywhere.
- [ ] Platform-wide erasure proven with certificates; evidence pack
      complete.

**Reliability**

- [ ] SLOs, error budgets, on-call, and runbooks for every product.
- [ ] Backups and DR drills meeting RPO/RTO targets.
- [ ] Launch review passed; game day completed; two weeks of operation
      logged.

**Engineering and cost**

- [ ] Whole platform deployed as code through CI/CD across three
      environments.
- [ ] Cost per product known; platform within budget.

**Documentation**

- [ ] README, architecture, ADRs, conventions, runbooks, evidence pack,
      reliability and FinOps reports, case study, demo, and retrospective.

---

## 14. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade capstone scores **at least
2 in every area** and **3 in Integration, Correctness, Reliability, and
Governance**.

| Area | What a "3" looks like |
| --- | --- |
| Product thinking | Clear data products with consumers, SLAs, tiers, and measured outcomes |
| Architecture and decisions | Coherent architecture; conflicts resolved in ADRs; no hidden single points of failure |
| Integration | One set of conventions, one catalog, conformed dimensions, contracted hand-offs |
| Correctness | Reconciliations and golden path pass; metrics consistent across interfaces |
| Quality and observability | Full tier-1 coverage, gates everywhere, grouped incidents, SLO dashboards |
| Governance and privacy | Classification, access tests, encryption, platform-wide provable erasure, evidence pack |
| Reliability | Tested backups, DR drills within RPO/RTO, game day, operations log |
| Delivery | Everything as code, CI/CD with promotion and rollback across components |
| Serving | APIs, semantic layer, features, and retrieval meeting SLAs under load |
| Cost | Unit economics per product, evidence-based optimisation, within budget |
| Communication | Case study, demo, and documentation that let others operate and evaluate the platform |

---

## 15. Common pitfalls to avoid

- Starting with breadth instead of a complete MVP slice.
- Keeping two catalogs, two table formats, or two definitions of "customer"
  without an explicit, justified reason.
- Integrating projects without integration contracts, so a change in one
  silently breaks another.
- Running timing-based dependencies between domains instead of asset-based
  orchestration with gates.
- Forgetting backups for metadata stores (catalog, Airflow, quality
  platform, registry) — the data is useless if its metadata is lost.
- Erasure that covers tables but not Kafka, snapshots, features, vectors,
  caches, logs, or backups.
- Streaming everything by default instead of where SLAs and costs justify it.
- Declaring the platform "done" without a game day and a period of
  operation.
- Documentation written only at the end — or not at all.
- Letting the cloud bill run unchecked; forgetting to tear down non-prod.

---

## 16. Suggested timeline

| Week | Work |
| --- | --- |
| 1 | M0 programme framing · M1 architecture and conventions |
| 2 | M2 foundations (IaC, identity, secrets, CI/CD, observability) |
| 3 | M3 ingestion · M4 lakehouse and conformed data |
| 4 | M5 marts and semantic layer · M6 real-time integration |
| 5 | M7 orchestration · M8 quality everywhere → **MVP complete** |
| 6 | M9 governance, security, privacy |
| 7 | M10 serving layer |
| 8 | M11 golden path and platform tests · M12 reliability and DR |
| 9 | M13 performance and FinOps · M14 launch review and game day |
| 10–11 | M15 launch and operate (two weeks) |
| 12 | M16 documentation, case study, demo, retrospective |
| Optional | M17 stretch goals |

---

## 17. What to show in a portfolio or interview

This capstone is your strongest portfolio piece. Be ready to discuss:

1. The data products, their consumers, and their SLAs — and how you
   measured success.
2. The platform architecture and three decisions you would defend (and one
   you would change).
3. How you reconciled different choices from earlier projects into one set
   of conventions.
4. How correctness is proven end to end (reconciliations, golden path,
   consistent metrics).
5. How an incident is detected, contained, communicated, and learned from —
   using your game-day results.
6. How a person's data is erased across every system, with evidence.
7. Your DR drills and whether you met RPO/RTO.
8. The cost per data product and the optimisations you made.
9. What version 2 of the platform would look like — and how it would
   support the Applied AI and Agentic AI work that comes next.

A strong capstone presentation shows not only that the platform works, but
that it can be **trusted, operated, evolved, and afforded** — the qualities
that define senior data engineering.
