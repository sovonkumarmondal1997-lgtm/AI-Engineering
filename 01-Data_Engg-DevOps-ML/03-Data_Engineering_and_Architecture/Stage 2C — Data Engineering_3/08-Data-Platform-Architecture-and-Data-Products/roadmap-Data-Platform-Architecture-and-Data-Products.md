# Roadmap — Module 2C.8: Data Platform Architecture and Data Products

This is the learning roadmap for the eighth module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about data platform
architecture and data products, **in what order**, **how** to learn each
topic, and **how to prove to yourself** that you have learned it before you
move on.

Up to now you have learned how to build individual pipelines, tables,
streams, and services. A **senior** data engineer is judged on something
else: the shape of the whole platform. Which architecture style fits the
company — batch plus streaming, one team or many domains? Who owns which
data? What promises (SLAs) do data products make to consumers? How do you
keep customer records consistent across ten systems? How do you scale one
platform across tenants and regions? And, most commonly asked in real
organisations: **should we build this or buy it?**

This module is the least code-heavy in Stage 2C and the most
**decision-heavy**. You will write documents, diagrams, and small
reference implementations, and you will practise defending trade-offs.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain **lambda** and **kappa** architectures, their trade-offs, and the
  modern lakehouse/streaming alternatives.
- Explain **data mesh** (domain ownership, data as a product, self-serve
  platform, federated governance) and judge when it helps or hurts.
- Define and operate **data products** with owners, contracts, SLAs/SLOs,
  and versioning.
- Explain **master data management (MDM)** and perform **entity
  resolution** (deterministic and probabilistic matching).
- Design a **metadata-driven** platform where configuration, not code
  copies, creates pipelines.
- Design **multi-tenant** and **multi-region** data platforms with
  isolation, residency, and disaster recovery.
- Run a **build-vs-buy** and vendor selection process and document it in an
  architecture decision record (ADR).

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Batch/streaming, medallion, warehouse vs lakehouse | Stage 2 — Module 2.1 | The vocabulary of architecture |
| Data modelling | Stage 2 — Module 2.8 | Entities, keys, conformed dimensions |
| Data contracts, quality, schema evolution | Stage 2 — Module 2.11 | The mechanics behind data products |
| Metadata and config-driven pipelines | Stage 2 — Module 2.12 | Foundation of Topic 05 |
| Orchestration | Stage 2 — Module 2.13 | How platform workloads run |
| Streaming | Stage 2 — Module 2.16 | Lambda/kappa |
| Governance, catalogues, lineage, IAM, GDPR | Stage 2 — Module 2.20 | Federated governance |
| Cost and performance | Stage 2 — Module 2.21 | Build-vs-buy economics |
| System design interviews | Stage 2B — Module 2B.5 | Your design framework and trade-off catalogue |
| Platforms: AWS, Databricks, Snowflake, GCP, Azure | Stage 2B; Modules 2C.3–2C.5 | The things you choose among |
| Query/OLAP engines | Module 2C.7 | Serving layers in the architecture |
| dbt and semantic layers | Module 2C.6 | The transformation and metrics layer |

**Tools needed:**

- A diagramming tool (draw.io, Excalidraw, or Mermaid/C4 in Markdown) and a
  place to keep **ADRs** in Git (`docs/adr/0001-….md`).
- Python 3.12+ in a `uv` project: `uv add pydantic pyyaml splink
  recordlinkage rapidfuzz duckdb pandas pytest` (Splink for probabilistic
  entity resolution, run on DuckDB).
- Optional: DataHub or OpenMetadata in Docker for data-product metadata.

**A note on versions:** terms such as "data mesh" and "data product" are
used loosely in industry. Learn the original definitions, then notice how
each company adapts them.

---

## 3. How the module is organised

The seven topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Architecture Styles                        (Intermediate)
  01 Lambda vs kappa architecture

Phase B — Organising Data at Scale                   (Intermediate → Advanced)
  02 Data mesh principles and domain ownership
  03 Data products and SLAs
  04 Master data management and entity resolution

Phase C — Building the Platform                      (Advanced)
  05 Metadata-driven platform design
  06 Multi-tenant and multi-region data platforms

Phase D — Decisions                                  (Advanced)
  07 Build vs buy and vendor selection

Consolidate
  Module mini-project: a platform architecture dossier with a working slice
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07
how  who  what  one   config isolate decide
data owns we    true  not   & span   and
moves what promise record code  regions record
```

Why this order:

- Architecture styles (01) set the technical frame; mesh (02) sets the
  organisational frame.
- Data products (03) are the unit mesh produces; MDM (04) keeps shared
  entities coherent across products.
- Metadata-driven design (05) makes the platform self-serve; multi-tenancy
  and regions (06) make it safe at scale.
- Build-vs-buy (07) applies everything and ends with a decision.

---

## 4. Suggested schedule

About **4 weeks at 6–8 hours per week**. This module involves a lot of
writing and discussion.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — lambda vs kappa · Topic 02 — data mesh |
| 2 | Topic 03 — data products and SLAs · Topic 04 — MDM and entity resolution |
| 3 | Topic 05 — metadata-driven platforms · Topic 06 — multi-tenant and multi-region |
| 4 | Topic 07 — build vs buy · mini-project |

---

## 5. How to study every topic (the architect's loop)

```text
Read → State the problem and constraints → Sketch 2–3 options → Compare on
explicit criteria → Choose → Write an ADR → Prototype the riskiest part
→ Review with someone → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **State the problem and constraints**: scale, latency, team size,
   budget, compliance, skills.
3. **Sketch two or three options** as diagrams (C4: context, container).
4. **Compare** on explicit criteria with weights (cost, risk, time to
   value, operability, lock-in).
5. **Choose** one and say what would make you reverse the decision.
6. **Write an ADR**: context, decision, alternatives, consequences.
7. **Prototype the riskiest part** (small, runnable).
8. **Review** with a peer or mentor; defend it aloud.
9. **Write it down** in `module-2c8-notes.md`.
10. **Explain aloud** in two minutes to a non-technical stakeholder.

Keep one `platform_architecture/` project:

```text
platform_architecture/
├── docs/
│   ├── adr/               # architecture decision records
│   ├── diagrams/          # C4 / Mermaid sources
│   ├── data-products/     # product specs (YAML + Markdown)
│   └── vendor-eval/       # scorecards and POC notes
├── product_specs/         # machine-readable data product definitions
├── metadata_platform/     # config-driven pipeline generator (Topic 05)
├── entity_resolution/     # Splink / rules matching experiments (Topic 04)
├── tenancy/               # isolation experiments (Topic 06)
└── tests/
```

---

## 6. Phase A — Architecture Styles (Intermediate)

### Topic 01 — [Lambda vs kappa architecture](01-lambda-vs-kappa-architecture.md)

**Why it comes first:** lambda and kappa are the classic answers to "how do
we combine batch and real-time?" Modern platforms replace both with
unified engines — but you must know what they replaced, because you will
inherit them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The two needs: accurate, complete (batch) and fast, approximate (stream); why one pipeline was hard historically |
| Basics | **Lambda architecture**: batch layer + speed layer + serving layer; merged views |
| Basics | **Kappa architecture**: a single streaming pipeline over a replayable log; reprocessing by replaying |
| Intermediate | Lambda's costs: two codebases that must agree, double operations, and reconciliation bugs |
| Intermediate | Kappa's requirements: long retention (or tiered storage), idempotent processing, state recovery, and reprocessing at scale |
| Intermediate | **Modern unified approaches**: Spark Structured Streaming with Delta/Iceberg, Flink with Iceberg, streaming tables and materialised views (Databricks, Snowflake dynamic tables), and "streaming lakehouse" (links to Modules 2.15, 2.16, 2C.3) |
| Intermediate | Batch vs micro-batch vs continuous: choosing latency by consumer need (SLAs from Module 2.1) |
| Advanced | **Event sourcing and CQRS** as data architecture patterns; the log as the system of record |
| Advanced | Reprocessing and backfills in kappa: shadow pipelines, version switching, and cost |
| Advanced | Correctness: exactly-once, late data, and reconciling streaming with batch truth |
| Advanced | Decision framework: when lambda is still right (legacy, dual SLAs, ML retraining), when kappa works, and when plain batch is enough |
| Advanced | Architecture patterns beyond: data lakehouse, data fabric, medallion, and real-time serving layers (Module 2C.7) |

**How to learn it**

1. Read the topic file.
2. Draw lambda and kappa for the same use case (live revenue dashboard
   plus nightly corrected totals).
3. List what can disagree between batch and speed layers.

**Hands-on exercise — `experiments/01_lambda_kappa/`**

1. Build a tiny lambda: batch totals in DuckDB plus a streaming counter;
   merge in a serving view; show mismatches when late data arrives.
2. Build the kappa version: one streaming job over a replayable log that
   produces corrected totals; reprocess from offset 0.
3. Compare code size, operations, and correctness evidence.
4. Write an ADR choosing an approach for a stated business case.

**Checkpoint — you are ready to move on when you can:**

- [ ] Draw lambda and kappa and name their layers.
- [ ] Explain why unified engines reduce lambda's cost.
- [ ] Decide when batch alone is enough.
- [ ] Write an ADR for an architecture style.

**Common mistakes:** building lambda "because Netflix did"; ignoring the
reconciliation problem; assuming kappa removes the need for batch truth
and backfills.

---

## 7. Phase B — Organising Data at Scale (Intermediate → Advanced)

### Topic 02 — [Data mesh principles and domain ownership](02-data-mesh-principles-and-domain-ownership.md)

**Why here:** as companies grow, one central data team becomes a
bottleneck. Data mesh is the best-known response — and widely
misunderstood. A senior engineer must explain it accurately and decide
whether to adopt it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem: centralised data teams as bottlenecks; source teams without accountability for data quality |
| Basics | The four principles (Dehghani): **domain-oriented ownership**, **data as a product**, **self-serve data platform**, **federated computational governance** |
| Basics | Domain boundaries: source-aligned, aggregate, and consumer-aligned domains |
| Intermediate | What changes organisationally: embedded data engineers, product owners for data, platform team, governance guild |
| Intermediate | What changes technically: domain-owned pipelines on a shared platform, standard interfaces, discoverability, interoperability standards |
| Intermediate | Federated governance in practice: global policies (PII, retention, naming) automated as code, local decisions inside domains |
| Intermediate | Anti-patterns: "mesh in name only", every domain building its own stack, no platform, governance abandoned |
| Advanced | When mesh helps (large, many domains, strong engineering culture) and when it hurts (small company, weak platform, no ownership culture) |
| Advanced | Mesh vs data fabric vs centralised lakehouse with product thinking; hybrid models |
| Advanced | Technology enablers: catalogues (Unity Catalog, DataHub, Purview, Dataplex), contracts, semantic layers, cross-project refs (dbt mesh), data sharing (Snowflake, Delta Sharing) |
| Advanced | Operating model design: team topologies, platform-as-a-product, funding, incentives, and measuring success |
| Advanced | Case studies and critiques; migration from central to federated in stages |

**How to learn it**

1. Read the topic file.
2. Take a fictional company (e-commerce with orders, logistics, marketing,
   finance) and draw its domains and their data products.
3. Write what the platform team provides and what each domain must do.

**Hands-on exercise — `experiments/02_data_mesh/`**

1. Draw a domain map with ownership and upstream/downstream data flows
   for the fictional company.
2. Define the global governance policies and show how each would be
   automated (checks in CI, tags, access rules).
3. Write a one-page assessment: should this company adopt mesh now, later,
   or a lighter alternative? Defend it.
4. Create a staged migration plan from a central team to federated
   domains.

**Checkpoint:**

- [ ] State the four principles accurately.
- [ ] Draw domain boundaries and data flows.
- [ ] Explain federated governance with examples.
- [ ] Judge whether mesh fits a given organisation.

**Common mistakes:** treating mesh as a technology purchase; skipping the
platform; leaving quality ownership unclear; adopting mesh at a company
with five engineers.

---

### Topic 03 — [Data products and SLAs](03-data-products-and-slas.md)

**Why here:** a data product is the unit of value in a mesh — and in any
well-run platform. It makes promises that consumers can rely on.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What makes a dataset a **product**: discoverable, addressable, trustworthy, self-describing, interoperable, secure; has an owner and consumers |
| Basics | Output ports: tables, files, APIs, streams, and metric endpoints |
| Basics | The product spec: name, owner, purpose, schema, sample, lineage, SLAs, access, and support channel |
| Intermediate | **SLIs, SLOs, and SLAs** for data: freshness, completeness, accuracy, availability, latency, and schema stability (links to Modules 2.1, 2.11) |
| Intermediate | **Data contracts** between producers and consumers; the Open Data Contract Standard (ODCS) and tools (datacontract-cli) — awareness |
| Intermediate | Versioning and deprecation: semantic versioning for schemas, compatibility rules, sunset policies, and consumer notification |
| Intermediate | Quality gates in the product pipeline; monitoring SLOs; error budgets; incident process |
| Advanced | Discoverability: catalogue entries, search, documentation, sample queries, and onboarding of consumers |
| Advanced | Cost and value: usage tracking, chargeback/showback, product health scores, and retiring unused products |
| Advanced | Product management for data: roadmaps, user research with consumers, prioritisation, and SLA tiering (gold/silver/bronze) |
| Advanced | Machine-readable product definitions (YAML) enabling automation: provisioning, access, monitoring, docs |
| Advanced | Data products for AI: features, embeddings, and governed context (links to Modules 2.22, 2C.10) |

**How to learn it**

1. Read the topic file.
2. Choose three datasets in your labs and decide which deserve to be
   products and why.
3. Draft a product spec for `customer_360` including SLOs.

**Hands-on exercise — `experiments/03_data_products/`**

1. Write a machine-readable product spec (YAML validated with Pydantic)
   for an `orders` product: schema, owner, freshness SLO, quality rules,
   access, and version.
2. Implement an automated check that measures freshness and completeness
   against the SLOs and reports error-budget burn.
3. Make a breaking schema change; use versioning and a deprecation
   timeline; notify a fake consumer list.
4. Register the product in a catalogue (DataHub/OpenMetadata) from the
   spec.
5. Write a consumer onboarding guide.

**Checkpoint:**

- [ ] Define data product characteristics and a spec.
- [ ] Choose measurable SLIs/SLOs and monitor them.
- [ ] Version and deprecate safely.
- [ ] Measure product usage and value.

**Common mistakes:** calling every table a product; SLOs nobody measures;
no owner on call; breaking changes without versioning.

---

### Topic 04 — [Master data management and entity resolution](04-master-data-management-and-entity-resolution.md)

**Why here:** the same customer, product, or supplier exists in many
systems under different ids and spellings. Without a resolved golden
record, every analysis is subtly wrong. This is also the practical
foundation of "customer 360".

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What master data is (customers, products, suppliers, locations) vs transactional and reference data |
| Basics | The problem: duplicates, conflicting attributes, missing keys across systems |
| Basics | MDM styles: registry, consolidation, coexistence, centralised; trade-offs |
| Intermediate | **Entity resolution** pipeline: standardise/clean → block → compare → classify → cluster → survivorship |
| Intermediate | **Deterministic matching** (exact keys, rules) vs **probabilistic matching** (Fellegi–Sunter, weights, thresholds) |
| Intermediate | Similarity measures: Levenshtein, Jaro–Winkler, token-based, phonetic (Soundex/Metaphone), numeric and date tolerances; address and name normalisation |
| Intermediate | **Blocking** to avoid O(n²) comparisons; recall vs cost; multi-pass blocking |
| Intermediate | **Survivorship rules** (most recent, most complete, source priority) to build the golden record; cross-reference tables and persistent master IDs |
| Advanced | Tools: Splink (on DuckDB/Spark), recordlinkage, dedupe; ML-based and embedding-based matching; LLM-assisted matching — awareness |
| Advanced | Evaluation: precision, recall, F1 on labelled pairs; clerical review queues and active learning |
| Advanced | Operating MDM: incremental matching, ID stability when clusters merge/split, stewardship workflows, and audit trails |
| Advanced | Hierarchies and relationships (household, parent company); graph-based resolution (links to Module 2C.1 graph databases) |
| Advanced | Privacy: matching on PII, hashing, consent, and the right-to-be-forgotten across the golden record (Module 2.20) |
| Advanced | MDM products (Informatica, Reltio, Profisee, Semarchy) vs build with open-source tools — links to Topic 07 |

**How to learn it**

1. Read the topic file.
2. By hand, resolve ten messy customer records from three systems; note
   every decision rule you used.
3. Estimate comparisons without and with blocking for 10 million records.

**Hands-on exercise — `experiments/04_entity_resolution/`**

1. Generate a synthetic customer dataset with typos, missing fields, and
   known true clusters (ground truth).
2. Build a deterministic baseline (rules); measure precision/recall.
3. Build a probabilistic model with Splink on DuckDB; tune blocking and
   thresholds; compare metrics.
4. Implement survivorship to produce a golden customer table and a
   cross-reference table with stable master IDs.
5. Add a clerical review queue for uncertain pairs.
6. Re-run with new records and keep existing master IDs stable.

**Checkpoint:**

- [ ] Describe the entity resolution pipeline.
- [ ] Use blocking and similarity scoring.
- [ ] Measure match quality and set thresholds.
- [ ] Build a golden record with survivorship and stable IDs.

**Common mistakes:** matching without blocking; no ground truth for
evaluation; unstable master IDs; merging records irreversibly with no
audit trail.

---

## 8. Phase C — Building the Platform (Advanced)

### Topic 05 — [Metadata-driven platform design](05-metadata-driven-platform-design.md)

**Why here:** at scale, hand-written pipelines for every source do not
survive. Metadata-driven platforms generate and run pipelines from
configuration, making the platform self-serve (a mesh principle) and
consistent.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The idea: describe **what** (sources, targets, rules) in metadata; a generic engine decides **how** |
| Basics | Config formats (YAML/JSON), validation with schemas (Pydantic/JSON Schema), and the control table pattern (from Module 2.12) |
| Basics | Typical metadata: source system, object, extraction mode, keys, watermark, target layer, quality rules, schedule, owner, classification |
| Intermediate | Generating orchestrator DAGs from config (Airflow dynamic DAG generation, Dagster factories) and dbt models from templates |
| Intermediate | Reusable ingestion frameworks: dlt, Airbyte, ADF metadata pipelines (Module 2C.5), Databricks DLT/Lakeflow (Module 2B.4), custom Python |
| Intermediate | Metadata catalogue as the source of truth: the control plane vs data plane; storing run history and state |
| Intermediate | Self-service onboarding: a PR with a YAML file creates a new ingestion with review, tests, and deployment |
| Advanced | Governance by metadata: classification drives masking, retention drives lifecycle rules, ownership drives alerts and access |
| Advanced | Evolution: config schema versioning, backward compatibility, and migration tooling |
| Advanced | Limits: when configuration becomes a bad programming language; escape hatches for custom logic; testing the generator |
| Advanced | Observability and lineage emitted automatically (OpenLineage) from the framework |
| Advanced | Platform-as-a-product: golden paths, templates, documentation, and measuring adoption (lead time to onboard a new source) |
| Advanced | Platform engineering tools: Backstage portals, Terraform modules, and internal developer platforms for data |

**How to learn it**

1. Read the topic file.
2. List what is identical across your last five ingestion pipelines and
   what differs; the differences are your metadata.
3. Design the YAML schema for an ingestion definition.

**Hands-on exercise — `experiments/05_metadata_platform/`**

1. Define a Pydantic-validated YAML spec for an ingestion (source, mode,
   keys, target, quality checks, schedule, owner, classification).
2. Write a generator that turns specs into Airflow (or Dagster) DAGs and
   a dbt staging model per source.
3. Onboard three different sources by only adding YAML files; time how
   long each takes.
4. Make classification automatically apply a masking policy and retention
   rule.
5. Introduce a config schema version bump and migrate existing specs.
6. Add tests that run the generator on fixtures and assert the output.

**Checkpoint:**

- [ ] Design a metadata schema for pipelines.
- [ ] Generate pipelines from configuration.
- [ ] Apply governance through metadata.
- [ ] Recognise the limits of config-driven design.

**Common mistakes:** configuration that grows into an undocumented
language; no validation; no escape hatch; building the framework before
having three real pipelines to generalise from.

---

### Topic 06 — [Multi-tenant and multi-region data platforms](06-multi-tenant-and-multi-region-data-platforms.md)

**Why here:** SaaS companies serve many customers; global companies serve
many jurisdictions. Both need isolation, residency, and resilience, and
both are classic senior-level design topics.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Tenancy models: **silo** (separate stack per tenant), **pool** (shared with tenant id), **bridge/hybrid**; trade-offs of cost, isolation, and operations |
| Basics | Tenant identification everywhere: tenant id in events, tables, partitions, topics, and logs |
| Basics | Regions, availability zones, latency, and why data may not leave a region |
| Intermediate | Isolation techniques: schema/database/account per tenant, row-level security, per-tenant encryption keys, partitioning by tenant, per-tenant warehouses/queues |
| Intermediate | **Noisy neighbours**: quotas, rate limits, workload management, and fair scheduling (Snowflake warehouses, BigQuery reservations, Kafka quotas) |
| Intermediate | Per-tenant lifecycle: onboarding, offboarding, export, and deletion (GDPR) at scale (Module 2.20) |
| Intermediate | **Data residency** and sovereignty: GDPR, regional laws, and routing data to the right region |
| Intermediate | Cost attribution and chargeback per tenant |
| Advanced | **Multi-region architectures**: active-passive, active-active, regional hubs with global aggregation; replication lag and conflict handling (links to Module 2C.1 consistency) |
| Advanced | Disaster recovery: RPO and RTO, backups, failover drills, cross-region replication for object storage, Kafka (MirrorMaker 2/Cluster Linking), and warehouses (replication groups) |
| Advanced | Global analytics with local data: federated queries, regional aggregation, and privacy-preserving rollups |
| Advanced | Tenant-aware metadata, catalogue, and lineage; per-tenant SLAs and tiers |
| Advanced | Security reviews and compliance evidence (SOC 2, ISO 27001) for multi-tenant data systems |
| Advanced | Migrating a tenant between silo and pool; splitting a hot tenant out |

**How to learn it**

1. Read the topic file.
2. For a B2B analytics SaaS with 5,000 small tenants and 20 enterprise
   tenants, pick tenancy models for each class and justify.
3. Draw a two-region design with data residency for EU and US customers.

**Hands-on exercise — `experiments/06_multi_tenant/`**

1. Implement pool tenancy in DuckDB/Postgres with row-level security and
   show that tenant A cannot read tenant B.
2. Implement a silo variant with a schema per tenant; compare complexity
   of migrations.
3. Simulate a noisy neighbour (one tenant running heavy queries); add
   quotas and show the effect on others.
4. Write a tenant-offboarding job that exports and deletes all tenant data
   including backups metadata and derived tables; produce an audit record.
5. Draw and document a multi-region design with RPO/RTO targets and a
   failover drill checklist.

**Checkpoint:**

- [ ] Choose a tenancy model with reasons.
- [ ] Enforce and test tenant isolation.
- [ ] Control noisy neighbours.
- [ ] Design for residency, RPO, and RTO.

**Common mistakes:** tenant id missing from some tables; isolation tested
only in the happy path; deleting a tenant without checking derived data and
caches; "multi-region" without a failover drill.

---

## 9. Phase D — Decisions (Advanced)

### Topic 07 — [Build vs buy and vendor selection](07-build-vs-buy-and-vendor-selection.md)

**Why it comes last:** this is where architecture meets money, people, and
risk. It is also the skill that most separates senior engineers from
mid-level ones.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The options: build, buy (SaaS), adopt open source (self-host), buy managed open source; and combinations |
| Basics | What is core to your business (build) vs commodity (buy); the cost of undifferentiated heavy lifting |
| Basics | Mapping the data stack: ingestion, storage/compute, transformation, orchestration, quality/observability, catalogue, BI, reverse ETL, ML platform — with typical vendors in each |
| Intermediate | **Total cost of ownership**: licence/usage, infrastructure, engineering time, on-call, upgrades, training, migration, and exit |
| Intermediate | Evaluation criteria with weights: functionality, scalability, security/compliance, integration, operability, ecosystem, support, roadmap, lock-in, and price predictability |
| Intermediate | A selection process: requirements → long list → short list → scorecard → proof of concept with success criteria → reference checks → negotiation |
| Intermediate | Pricing models and traps: per-seat, per-row/MAR, per-credit, committed use, egress, overage; modelling cost at 10× scale |
| Advanced | Lock-in management: open formats (Iceberg/Parquet), standard SQL, portable orchestration, abstraction layers — and the cost of abstracting too early |
| Advanced | Risk assessment: vendor viability, acquisitions, security incidents, SLA credits, and data portability clauses |
| Advanced | Open-source adoption risks: governance of the project, licence changes (e.g., relicensing events), bus factor, and managed alternatives |
| Advanced | Organisational factors: team skills, hiring market, change management, and the "resume-driven development" trap |
| Advanced | Writing and defending an **ADR / RFC**; stakeholder management with finance, security, and legal; revisit dates |
| Advanced | Case studies: warehouse selection (Snowflake/BigQuery/Databricks), orchestration (Airflow/Dagster/managed), ingestion (Fivetran/Airbyte/dlt/custom), streaming (Kafka/Confluent/MSK/Redpanda) |

**How to learn it**

1. Read the topic file.
2. Pick one decision (managed ingestion vs custom code for 40 SaaS
   sources) and list build and buy costs for one year and three years.
3. Write what must be true for each option to win.

**Hands-on exercise — `experiments/07_build_vs_buy/`**

1. Build a weighted scorecard for three real tools in one category (for
   example Airbyte, Fivetran, and a custom dlt framework); score with
   evidence, not opinion.
2. Create a TCO model (spreadsheet or Python) with usage growth scenarios
   at 1×, 5×, and 10×.
3. Run a time-boxed proof of concept for the leading option against
   written success criteria.
4. Write the ADR with context, options, decision, consequences, risks,
   and a review date.
5. Present it in five minutes to a mock CTO and CFO, and answer their
   objections.

**Checkpoint:**

- [ ] Decide what to build and what to buy, with reasons.
- [ ] Model TCO including people and exit costs.
- [ ] Run a vendor evaluation and POC.
- [ ] Write a defensible ADR.

**Common mistakes:** comparing only licence prices; choosing a tool for
its feature list instead of your requirements; building what a vendor does
as a commodity; no exit plan.

---

## 10. Module mini-project — a platform architecture dossier with a working slice

**Goal:** produce the documents a staff engineer would present to
leadership, plus a small running slice proving the riskiest ideas.

**Requirements**

1. A **context and container diagram** (C4) for a fictional company's data
   platform covering batch and streaming, lakehouse, warehouse, a serving
   layer, and governance.
2. A **domain map** with at least four domains and their data products;
   machine-readable product specs for three of them with SLOs.
3. An **entity resolution** slice producing a golden customer table with
   stable master IDs and an evaluation report.
4. A **metadata-driven** generator that onboards three sources from YAML
   and applies classification-driven governance.
5. A **tenancy and region** design with isolation tests, an offboarding
   job, and RPO/RTO targets.
6. At least four **ADRs**: architecture style, mesh vs central, one
   build-vs-buy decision with a TCO model, and one engine choice.
7. A final **review**: risks, open questions, and a staged roadmap.

**Done when** a skeptical reviewer can read the dossier, run the slice,
and find every major decision justified with alternatives and risks.

---

## 11. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Explain lambda, kappa, and modern unified architectures and choose
      among them.
- [ ] Explain data mesh accurately and judge its fit for an organisation.
- [ ] Specify, monitor, version, and deprecate data products with SLOs.
- [ ] Build an entity resolution pipeline and a golden record.
- [ ] Design and test a metadata-driven platform.
- [ ] Design multi-tenant and multi-region platforms with isolation,
      residency, and DR.
- [ ] Run a build-vs-buy decision and defend it in writing.

---

## 12. Recommended reading and references

- *Data Mesh* — Zhamak Dehghani; and the original "How to Move Beyond a
  Monolithic Data Lake" article.
- *Fundamentals of Data Engineering* — Joe Reis and Matt Housley
  (architecture and undercurrents chapters).
- *Designing Data-Intensive Applications* — Martin Kleppmann.
- *Building Evolutionary Architectures*; the C4 model (c4model.com);
  Michael Nygard's ADR article.
- Splink documentation and the Fellegi–Sunter model; the Open Data
  Contract Standard.
- *Team Topologies* (platform teams and enabling teams).

---

## 13. Where this module leads

- **Module 2C.9** covers the analysis and BI consumers of your data
  products.
- **Module 2C.10** hands data products to ML and MLOps.
- **Stage 3 onwards** moves to computer-science and ML foundations, with
  this module's architectural thinking reused in LLMOps and AI system
  design (Stage 14).
