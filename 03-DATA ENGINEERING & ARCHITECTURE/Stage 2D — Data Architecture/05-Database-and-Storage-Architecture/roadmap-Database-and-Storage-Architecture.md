# Roadmap — Module 2D.5: Database and Storage Architecture

This is the learning roadmap for the fifth module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Modules 2D.1–2D.4 gave you the role, the decision method, the organising
patterns and the logical models. This module turns those into **storage
decisions**: which kind of store serves which workload, in what format and
layout, with what consistency and durability, and for how long. The aim is not
to memorise products. It is to reason from workload evidence to a defensible
storage architecture.

> **Repository note.** The seven topic files, `practice-questions.md`, the
> module and project READMEs, and
> `Projects/05-storage-technology-selection-and-logical-layout.md` currently
> exist but are empty, as are the Stage 2D overview files. This roadmap is
> therefore the first written statement of the module's scope. It defines the
> learning sequence for each topic file; it does not claim that any topic file
> already contains this material. Where a topic file, once written, covers
> different database categories, file formats or table formats than those used
> here as examples, the topic file's scope governs and this roadmap should be
> updated.
>
> **Directory name.** The prompt that requested this roadmap referred to
> `STAGE 2D - DATA ARCHITECURE/`. The actual directory is
> `Stage 2D — Data Architecture/`, and the actual name is preserved.
>
> **Illustrative content.** Every number, workload and organisation in this
> roadmap is an **illustrative assumption** used to teach a method. None is a
> real requirement, benchmark or recommended target. The module is
> vendor-neutral and is **not** a database administration course: categories
> are named, products are not required, and no product-specific commands are
> taught. Where a product class is mentioned it is only an example of the
> category.

---

## 1. Module overview

### 1.1 What database and storage architecture means

**Database and storage architecture** is the set of decisions about where data
live and how they are held: the kind of store, its data model and access
interface, its physical organisation (formats, partitions, indexes), its
durability, replication and consistency behaviour, and its lifecycle from
creation to deletion. It sits between the logical model (2D.4) and the
implemented platform (2D.7).

### 1.2 Why storage selection is an architectural decision

Choosing a store is not choosing a product. It commits the organisation to:

- a **data model and query model** (what can be asked cheaply),
- a **consistency and transaction model** (what can go wrong, and how),
- a **scaling model** (how it grows, and what that costs),
- an **operating model** (skills, runbooks, upgrades, incident handling),
- a **governance surface** (access control, retention, deletion, audit), and
- a **cost profile** (storage, compute, movement, people).

Those commitments last for years and are hard to reverse. They should therefore
be made from workload evidence and recorded as decisions (2D.2 Topic 7), not
inherited from familiarity or vendor positioning.

### 1.3 The chain from requirement to storage

```text
Business requirement → data model (2D.4) → workload characterisation →
access patterns → storage category → logical layout → physical choices
```

| Link | Question | Evidence |
| --- | --- | --- |
| Requirement → workload | What work must the data support? | Use cases, volumes, targets (2D.2) |
| Workload → access pattern | How is the data read and written? | Query shapes, keys, ranges, concurrency |
| Access pattern → category | Which kind of store serves that cheaply and correctly? | Fit analysis |
| Category → layout | How should the data be organised? | Partitioning, format, lifecycle |
| Layout → validation | Does it perform and behave as assumed? | Tests, measurements |

### 1.4 The landscape in one table

| Category | Primary purpose | Typical strength | Typical limitation |
| --- | --- | --- | --- |
| Transactional (OLTP) database | Many small, concurrent reads and writes with integrity | Correctness, low-latency point access | Poor for large scans and heavy analytics on the same resources |
| Analytical (OLAP) system | Large scans, aggregations, joins over history | Scan efficiency, columnar storage | Poor for high-rate single-row updates |
| Distributed database | Horizontal scale and availability | Capacity, resilience | Consistency and operational complexity |
| Object storage | Durable, cheap, scalable storage of files/objects | Cost, scale, durability | No native transactions or low-latency random update |
| Data warehouse | Governed, modelled analytical store | Performance and governance for modelled data | Cost and rigidity for raw, varied data |
| Lakehouse | Open storage with table-management features | Flexibility with warehouse-like management | Operational and metadata complexity |
| Specialised store (search, graph, time-series, vector, key-value, etc.) | One access pattern done very well | Purpose-fit performance | Narrow scope; another system to run |

No row is "best". Each is the right answer for some workload and the wrong
answer for another.

### 1.5 How storage affects the quality attributes

| Attribute | Storage lever |
| --- | --- |
| Performance | Data model, layout, indexes, format, caching, compute separation |
| Scalability | Partitioning, sharding, storage/compute separation |
| Consistency | Transaction support, replication mode, isolation |
| Reliability and durability | Replication, backup, recovery, failure domains |
| Availability | Redundancy, failover, replica placement |
| Governance | Access control granularity, auditing, retention, deletion support |
| Cost | Storage tier, compression, compute model, data movement |
| Maintainability | Operational skill needs, schema change handling, tooling |

### 1.6 How this module builds on earlier ones

| From | Used here |
| --- | --- |
| 2D.1 Topic 4: principles, quality attributes | Criteria for comparing storage options |
| 2D.2 Topics 2–4: requirements, volume, latency, availability | Workload facts and measurable targets |
| 2D.2 Topic 5: constraints, risks | Eliminates options (residency, skills, budget) |
| 2D.2 Topics 6–7: trade-offs, ADRs | Method and record of storage decisions |
| 2D.3 Topic 2: warehouse, lake, lakehouse patterns | The pattern-level choice that this module makes concrete |
| 2D.3 Topic 3: Lambda and Kappa | Replay and retention needs of stream stores |
| 2D.4 Topics 1–3: logical models, keys, normalisation | What the stores must hold and how entities relate |
| 2D.4 Topic 4–5: dimensional and historical models | Which analytical shapes are stored |
| 2D.4 Topic 7: schema evolution | Format and table-format handling of change |

### 1.7 How it supports later modules

| Later module | What it takes from this one |
| --- | --- |
| 2D.6 Data integration and interoperability | Source and target store capabilities; change capture options |
| 2D.7 Enterprise data platform and lakehouse | Storage layers, zones and table management |
| 2D.8 Cloud, hybrid and multi-cloud | Mapping store categories to services and constraints |
| 2D.9 Streaming and real-time | Stores for logs, state and serving |
| 2D.10 Governance, security, privacy | Retention, deletion, access and encryption at the storage level |
| 2D.12 Reliability, resilience, disaster recovery | Replication, backup and recovery foundations |
| 2D.13 Performance, scalability, cost | Layout, sizing and cost models |
| 2D.14 Data access, serving and AI data | Stores that serve analytics, features and retrieval |

### 1.8 Expected capabilities after completion

You will be able to:

- Classify a workload as transactional, analytical, mixed or specialised from
  evidence about its access pattern.
- Explain when operational and analytical workloads must be separated and when
  separation is unnecessary.
- Select among relational, NoSQL and specialised categories with explicit
  criteria and recorded trade-offs.
- Choose an object-storage organisation and file format for a workload and
  quantify the effect.
- Distinguish a storage system, a table format and a data platform, and design
  an analytical storage approach.
- Propose partitioning, indexing and clustering with stated workload
  assumptions and a validation plan.
- Define replication, consistency and transaction-boundary requirements from
  business correctness needs.
- Design a retention, archival and tiering strategy that reconciles cost,
  retrieval and compliance.
- Deliver a defensible storage technology selection with a logical layout.

> **Principle for the whole module.** No database or storage technology is
> universally best. The correct choice depends on workload characteristics,
> requirements, constraints and operating conditions. A recommendation that
> does not state its workload assumptions is incomplete.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

| Prerequisite | Why it matters here |
| --- | --- |
| Module 2D.2 completed (or its gates passed): requirements, volume and growth estimates, latency/throughput/freshness/availability targets, constraints and risks, trade-off method, ADRs | Storage choices are driven by measured workload facts and measurable targets; without them selection reverts to preference. The estimation formulas are reused throughout |
| Module 2D.4 completed (or its gates passed): logical models, keys, normalisation, dimensional and historical models, schema evolution | The stores must hold these models; layout and format decisions depend on entities, keys, grain and history |
| Module 2D.3 completed (or its gates passed), especially Topic 2 (warehouse, lake, lakehouse patterns) | This module makes those patterns concrete; the pattern decision frames the category choice |
| Module 2D.1 completed (or its gates passed): principles, quality attributes, governance | Criteria and governance vocabulary |
| Stage 2–2C data engineering experience: SQL, batch and streaming pipelines, file formats, warehouse/lakehouse tables | You need practical experience of how data are read and written. **Deep database administration knowledge is not assumed** |

### 2.2 Helpful prior knowledge

- Experience operating or querying a production database.
- Familiarity with how a query planner uses indexes (conceptually).
- Familiarity with cloud object storage and a columnar file format.
- Basic knowledge of failure modes in distributed systems (network partitions,
  node loss).

### 2.3 Concepts you will learn during this module

- Workload characterisation and access-pattern analysis.
- The vocabulary of consistency, isolation and durability.
- Partition-key selection, skew and pruning.
- Table-format concepts (snapshots, manifests, transaction logs) at the
  conceptual level.
- Retention classes, legal holds and tier economics.
- Basic queueing and capacity reasoning for storage.

### 2.4 Using prior knowledge when selecting storage

Work in this order every time. It prevents choosing a technology first and
inventing reasons afterwards.

1. **Workload** — what work, what shape, what rate (2D.2 Topics 3–4).
2. **Data model** — entities, keys, relationships, grain (2D.4).
3. **Requirements and targets** — correctness, freshness, availability,
   retention (2D.2 Topics 2, 4).
4. **Constraints and risks** — residency, skills, budget, dependencies
   (2D.2 Topic 5).
5. **Pattern context** — which architecture pattern applies (2D.3).
6. **Candidates and criteria** — only then name categories and compare
   (2D.2 Topic 6).
7. **Record** — ADR with rejected alternatives (2D.2 Topic 7).

---

## 3. Learning strategy and progression

### 3.1 The four levels

| Level | Concepts to study | Recommended order | Practical exercises | Questions to answer | Expected outputs | Evidence of mastery | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1 — Beginner** | Purpose, terminology, basic characteristics and typical uses of each category | Definition → what problem it solves → typical use → limitation | Define and classify; match a use case to a category; draw a simple data flow | What is this for? What is it poor at? | One-page category cards | Correct unaided explanation and classification | ≥ 90% of classification items correct; can explain each category to a peer |
| **2 — Intermediate** | Workload analysis, category comparison, access patterns, linking requirements to storage design | Characterise workload → derive access pattern → shortlist categories → compare | Profile five workloads; compare formats; map requirements to layout | What is the read/write mix? Which key is used? What latency is needed? | Workload profiles; comparison tables; mapping | A reviewer can recover the workload from your analysis | Workload-to-category mapping with stated assumptions and units |
| **3 — Advanced** | Trade-offs: performance, scalability, consistency, durability, availability, complexity, retention, cost | Quantify → compare → stress with failure → test sensitivity → decide | Capacity and cost estimates; skew analysis; replication-lag scenarios; tier economics | What breaks first? What does this cost to run? What changes the answer? | Trade-off analysis with numbers and failure cases | A defended recommendation that survives challenge | Sensitivity analysis shows how robust the choice is |
| **4 — Industry application** | Defensible selection, logical layout, workload-to-storage mapping, recommendation | Requirements → workloads → candidates → layout → consistency → lifecycle → ADR | The project (Section 7) | Can another architect audit and reproduce this? | Storage selection and logical layout package | Independent review finds no unflagged defect | Project completion gate (Section 7.7) met |

### 3.2 Emphasis

The module rewards **quantitative reasoning, workload analysis, explicit
trade-offs and justified decisions**. Memorising product feature lists or
naming fashionable technologies earns nothing. A short analysis with units,
assumptions and a stated failure mode beats a long catalogue.

### 3.3 The storage-selection loop (use for every topic)

```text
Characterise the workload → State the access pattern → Quantify (rate, size,
latency) → Shortlist categories → Check consistency and failure behaviour →
Estimate cost and effort → Decide and record → Validate with a test or
measurement → Revise
```

1. **Characterise the workload:** reads, writes, scans, point lookups, joins.
2. **State the access pattern:** keys, ranges, filters, concurrency.
3. **Quantify** with formulas and units (Section 3.5).
4. **Shortlist** two or three feasible categories plus a baseline.
5. **Check consistency and failure behaviour.**
6. **Estimate cost and effort,** including people.
7. **Decide and record** (ADR).
8. **Validate** with a representative test or measurement plan.
9. **Revise** when evidence disagrees.

### 3.4 Suggested schedule

About **5 weeks at 6–8 hours per week.**

| Week | Work |
| --- | --- |
| 1 | Topic 1 (OLTP/OLAP separation) · Topic 2 (relational, NoSQL, specialised) |
| 2 | Topic 3 (object storage and file formats) · Topic 4 (warehouse, lakehouse, table formats) |
| 3 | Topic 5 (partitioning, indexing, clustering, layout) |
| 4 | Topic 6 (replication, consistency, transaction boundaries) · Topic 7 (retention, archival, tiers) |
| 5 | Practice questions · project |

Keep a `module-2d5-notes.md` outside the repository's topic files: category
cards, a workload log with worked estimates, and open questions. These feed
the project.

### 3.5 Quantitative toolkit used in this module

All values below are **illustrative**. Use decimal units unless stated
(1 GB = 10⁹ bytes).

```text
daily_volume        = records_per_day × average_record_size
retained_volume     = daily_volume × retention_days × copies × (1 + overhead)
average_write_rate  = writes_per_day / 86,400 s
peak_write_rate     = average_write_rate × peak_factor
compressed_size     = raw_size / compression_ratio
scan_time           ≈ bytes_scanned / scan_throughput
files_per_partition = partition_size / target_file_size
replication_lag_exposure (RPO proxy) = max observed or worst-case lag
monthly_storage_cost = Σ ( tier_volume × tier_price_per_unit_month )
```

Always write units at each step, state the assumption behind each input, and
give a range where the input is uncertain (2D.2 Topic 3).

---

## 4. Detailed learning roadmap for each topic file

Each module below uses the same twelve sub-headings. Levels are cumulative.
Examples use the **illustrative** scenario of *Northbridge Bank*, a fictional
mid-sized bank (Section 7.2).

---

### Module 1 — [OLTP, OLAP and operational-analytical separation](01-oltp-olap-and-operational-analytical-separation.md)

#### 1.1 Learning objectives

- Define OLTP and OLAP and the workloads each serves.
- Contrast query patterns, concurrency, access shape and response expectations.
- Distinguish operational systems from analytical systems.
- Explain what happens when incompatible workloads share resources.
- Describe separating transactional processing from analytical consumption and
  how data move between them.
- Weigh consistency, freshness, performance and cost, and decide when
  separation is necessary.

#### 1.2 Why the topic matters in real-world Data Architecture

The most common storage failure is an analytical query slowing a payment
system. The opposite failure is building a duplicate analytical platform for a
workload that never needed one. Both come from not characterising the
workload.

#### 1.3 Prerequisite knowledge

2D.2 Topics 3–4 (volume, latency, availability); 2D.4 Topics 1–4 (logical,
normalised and dimensional models).

#### 1.4 Beginner-level learning sequence

1. **Define OLTP:** many short transactions that read or modify a small number
   of records, with strict integrity and low latency (for example posting a
   payment).
2. **Define OLAP:** fewer, larger queries that scan and aggregate many records
   over history (for example monthly exposure by segment).
3. **Contrast them** in a table:

   | Dimension | OLTP | OLAP |
   | --- | --- | --- |
   | Typical operation | Insert/update/lookup one entity | Scan, aggregate, join many rows |
   | Rows touched per request | Few | Millions or more |
   | Concurrency | Very high | Lower, but each query heavy |
   | Latency expectation | Milliseconds | Seconds to minutes |
   | Data shape | Normalised | Dimensional / wide / columnar |
   | Data horizon | Current (plus recent) | Long history |
   | Integrity focus | Strict consistency | Consistent as-of view |

4. **Define terms:** operational system, analytical system, workload,
   contention, isolation.
5. **Questions to answer:** Why does a long-running scan hurt a payment system
   sharing the same database? What is a "reporting replica"?
6. **Exercise:** Classify twenty described operations as OLTP, OLAP or mixed.

**Ability to demonstrate:** classify workloads and explain the difference in
two minutes.

#### 1.5 Intermediate-level learning sequence

1. **Profile a workload** using evidence, not labels: read/write ratio,
   rows per request, key vs range access, concurrency, latency target, data
   horizon, peak factor.
2. **Explain why access patterns differ:** row-oriented storage and indexes
   serve point access; column-oriented storage and scan parallelism serve
   aggregation (storage detail follows in Topics 3–5).
3. **Identify workloads that blur the line:** operational dashboards, fraud
   scoring that needs both current state and history, customer service views
   that join recent and historical data. Call these *mixed* and examine each
   half.
4. **Study the separation options at the pattern level:**
   1. Same database, scheduled off-peak analytics (cheap, fragile).
   2. Read replica for reporting (shares the schema, isolates compute).
   3. Extract/replicate to a separate analytical store (batch or change
      capture).
   4. Event-based publication to analytical consumers (2D.3 Topic 6).
5. **Study data movement and synchronisation:** full versus incremental
   transfer, change capture, latency, ordering, reconciliation (detail in 2D.6).
6. **Quantify the data-movement load:**

   ```text
   daily_change_volume = changed_rows_per_day × average_row_size
   required_sync_throughput = peak_change_rate × average_row_size
   ```

   *Illustrative:* 5,000,000 changed rows/day × 400 bytes = 2.0 GB/day
   (decimal), an average of about 23 KB/s; if the peak factor is 10, plan for
   about 230 KB/s plus overhead.
7. **Questions to answer:** Which workload is protected by the separation?
   What freshness does the analytical side actually need?
8. **Exercise:** For five Northbridge workloads (payment posting, balance
   enquiry, fraud scoring, regulatory report, executive dashboard), classify,
   profile, and propose the simplest adequate separation.

**Ability to demonstrate:** a profile for each workload that justifies its
classification and the minimum separation needed.

#### 1.6 Advanced-level learning sequence

1. **Isolation and contention:** shared CPU, memory, I/O, locks and cache;
   how analytical scans evict operational working sets; lock and latch
   contention; how replicas still compete for the primary through replication
   load.
2. **Freshness versus cost:** the synchronisation latency you promise sets the
   cost. Relate target freshness (2D.2 Topic 4) to the mechanism: nightly batch
   (hours), micro-batch (minutes), change capture (seconds), events (seconds).
3. **Consistency of the analytical copy:** point-in-time consistency across
   multiple tables; partial loads; late and out-of-order changes; handling
   deletes; reconciliation checks (row counts and control totals).
4. **Hybrid designs:** operational stores that serve limited analytical queries
   (indexed aggregates, materialised summaries), and systems designed for both
   (mixed-workload databases). State the conditions under which they are
   adequate and the point at which they stop being so.
5. **Where separation is not needed:** low volume, modest concurrency, relaxed
   latency, headroom measured, no regulatory isolation requirement. Show the
   evidence that supports staying together.
6. **Operational cost of separation:** extra system, pipelines, monitoring,
   data duplication, security surface, reconciliation effort.
7. **Failure modes:** reporting replica lag mistaken for truth; pipeline
   failure leaving analytics stale without notice; separation that copies
   sensitive data without equivalent controls.
8. **Questions to answer:** What measurement would prove the shared system is
   still adequate? What is the cheapest separation that meets the freshness
   target?
9. **Exercise:** Take a described mixed workload, quantify the data movement,
   evaluate three separation options on cost, freshness and complexity, and
   recommend one with the evidence that would trigger a change.

**Ability to demonstrate:** a separation recommendation justified by workload
evidence, with a quantified data-movement estimate and revisit trigger.

#### 1.7 Industry-application exercises

- Recommend an operational/analytical separation strategy for Northbridge's
  payment-processing workload and its downstream reporting.
- Produce a one-page contention analysis showing which analytical queries would
  harm the operational system.
- State what you would measure for 30 days before deciding.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* A month-end report doubles the payment API's latency. Diagnose
   and propose options at three cost levels.
2. *Scenario:* A small business-lending team with 20 users and modest data
   asks for its own warehouse. How do you evaluate the request?
3. *Scenario:* Analysts complain that balances on the dashboard differ from
   the app by a few minutes. Which design property explains it and is it a
   defect?

#### 1.9 Expected outputs and deliverables

- Workload classification and profiles.
- Separation options comparison with quantified data movement.
- Recommendation with measurement plan and revisit trigger.
- Answers to Topic 1 practice questions.

#### 1.10 Common mistakes and misconceptions

- Assuming every analytical need requires a separate platform.
- Treating "reporting replica" as a complete analytical architecture.
- Classifying by system name rather than by access pattern.
- Ignoring that replicas still load the primary.
- Promising freshness the mechanism cannot deliver.
- Copying sensitive data to analytics without equivalent controls.

#### 1.11 Mastery criteria

- Classifies workloads from evidence.
- Explains contention and quantifies data movement.
- Justifies separation (or its absence) with measurements and costs.

#### 1.12 Completion gate

- [ ] Workload profiles and classification reviewed.
- [ ] Recommendation includes quantified movement, cost/complexity comparison
      and a revisit trigger.
- [ ] At least one case concludes that separation is not needed.
- [ ] Topic 1 practice questions answered and corrected.

---

### Module 2 — [Relational, NoSQL and specialized database selection](02-relational-nosql-and-specialized-database-selection.md)

#### 2.1 Learning objectives

- Describe relational characteristics and uses.
- Describe the NoSQL categories covered by the topic file (illustrated here by
  key-value, document, wide-column and graph) as **distinct** categories.
- Describe specialised stores (illustrated by search, time-series and vector)
  and the workloads they target.
- Map data models and access patterns to categories.
- Weigh transaction, consistency, query flexibility, relationships, scale,
  availability, operations and cost.
- Apply selection criteria and reason about polyglot persistence.

#### 2.2 Why the topic matters in real-world Data Architecture

The wrong database category forces application workarounds forever: joins in
application code, missing transactions, unqueryable data, or an expensive
specialised store used as a general one. The category should follow the access
pattern.

#### 2.3 Prerequisite knowledge

Module 1 here; 2D.4 Topics 1–3 (entities, relationships, keys, normalisation).

> **Scope note.** The categories above are illustrative. Follow the categories
> the topic file actually names; do not claim coverage of a category the file
> omits.

#### 2.4 Beginner-level learning sequence

1. **Learn the relational model:** tables, keys, SQL, joins, transactions with
   strong integrity guarantees; flexible ad hoc querying; schema-on-write.
2. **Learn the NoSQL families as separate things:**

   | Category | Data model | Natural access pattern | Typical fit |
   | --- | --- | --- | --- |
   | Key-value | Key → opaque value | Get/put by key | Sessions, caches, lookups |
   | Document | Self-describing nested documents | Retrieve/update a document by id or attribute | Variable-structure entities |
   | Wide-column | Rows keyed by partition with flexible columns | High-volume writes, lookups by partition key and range | Large-scale event/time-oriented records |
   | Graph | Nodes and edges | Traverse relationships | Fraud rings, networks, recommendations |

3. **Learn specialised types:** search (inverted indexes), time-series (time-
   ordered, downsampling), vector (similarity search over embeddings), and so
   on, each for one access pattern.
4. **Learn the vocabulary:** schema-on-read, denormalised, partition key,
   secondary index, eventual consistency.
5. **Questions to answer:** Why is "NoSQL" not one thing? What question can a
   key-value store *not* answer cheaply?
6. **Exercise:** Match twenty access patterns to categories and state which
   category would be a poor fit.

**Ability to demonstrate:** describe each category's model, natural access
pattern and a typical limitation.

#### 2.5 Intermediate-level learning sequence

1. **Extract the access patterns first.** List the top queries and updates,
   their keys, filters, ranges, and frequency. Technology follows this list.
2. **Map requirements to categories** along: relationship complexity, need for
   multi-record transactions, ad hoc querying, schema variability, write rate,
   read latency, data size, global distribution.
3. **Understand modelling differences:** relational models normalise and join;
   many NoSQL models are shaped *around the query* (denormalised, duplicated)
   and trade update simplicity for read speed (links to 2D.4 Topic 3).
4. **Understand consistency defaults:** categories differ in what they
   guarantee and what is configurable; check guarantees against requirements
   (detail in Topic 6).
5. **Understand scaling behaviour:** vertical versus horizontal; partition-key
   dependence; hotspots.
6. **Selection criteria table** (use scenario-relevant rows only):

   | Criterion | Question |
   | --- | --- |
   | Data model fit | Does the model match the entity and relationship shape? |
   | Access pattern fit | Are the top queries cheap? |
   | Transactions | Are multi-entity atomic updates required? |
   | Consistency | What staleness is tolerable? |
   | Query flexibility | Are unplanned queries expected? |
   | Scale and growth | What volume and rate over three years? |
   | Availability and distribution | Multi-region needs? |
   | Operations | Do we have the skills and tooling? |
   | Governance | Fine-grained access, audit, deletion support? |
   | Cost | Licence/service, infrastructure, people |

7. **Questions to answer:** What happens when the second most important query
   arrives and the data are shaped for the first?
8. **Exercise:** For six Northbridge workloads (account ledger, customer
   profile, session store, relationship network for fraud, document search,
   metric telemetry), produce an access-pattern list and a category choice with
   a rejected alternative for each.

**Ability to demonstrate:** a category choice per workload justified by listed
access patterns and a named rejected alternative.

#### 2.6 Advanced-level learning sequence

1. **Compare alternatives quantitatively where possible:** estimated request
   rates, item sizes, partition counts, storage per entity, and replication
   overhead.

   ```text
   storage_needed = entities × average_item_size × replication_factor × (1 + index_overhead)
   per-partition_write_rate = total_write_rate / partitions   (assumes uniform keys)
   ```

   *Illustrative:* 20 million customers × 3 KB × 3 replicas × 1.3 ≈ 234 GB
   (decimal). Test the uniform-key assumption; skewed keys concentrate load
   (Topic 5).
2. **Transaction and integrity needs:** where integrity must be enforced by the
   store versus by the application; the cost of moving it to the application.
3. **Query-flexibility cost:** pre-modelled access patterns are fast and rigid;
   adding a new query may require re-modelling or a secondary system.
4. **Operational reality:** upgrades, backup/restore characteristics, tooling,
   monitoring, skills, on-call burden, vendor or community maturity.
5. **Polyglot persistence:** why organisations run multiple stores; the costs
   (consistency between stores, duplicated data, multiple skill sets, more
   incident surface, security consistency). Require a stated reason for each
   additional store, and a data-ownership rule so one store is the system of
   record.
6. **General-purpose versus specialised:** a mature general-purpose store may
   serve a niche need adequately at lower total cost; a specialised store is
   justified when its access pattern dominates and the general store cannot meet
   targets (state the evidence).
7. **Failure modes:** adopting a document store and rebuilding joins in code;
   using a search index as the system of record; treating a cache as durable;
   fashion-driven adoption.
8. **Questions to answer:** What would make you add a second store? What
   evidence would make you retire one?
9. **Exercise:** Evaluate a proposal to introduce a graph database for fraud
   detection: define the access patterns, the volume, the alternative of
   relational recursive queries, and the operational cost; recommend and state
   the conditions for revisiting.

**Ability to demonstrate:** a comparison with numbers, operational reality and a
polyglot-justification rule.

#### 2.7 Industry-application exercises

- Produce a technology-selection matrix for Northbridge's customer profile
  store, with at least three candidate categories and a baseline.
- Write the ADR for the choice (2D.2 Topic 7 structure).
- State which store is the system of record for each core entity.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* A team wants a document store for the account ledger because "the
   schema changes often". What do you ask?
2. *Scenario:* Fraud analysts want to follow chains of related accounts several
   hops deep. Which access pattern is this and which categories suit it?
3. *Scenario:* A cache holds balances and starts serving stale values after a
   failover. What was assumed about durability and consistency?

#### 2.9 Expected outputs and deliverables

- Category cards (relational, key-value, document, wide-column, graph,
  specialised).
- Access-pattern lists and the selection matrix.
- ADR for one selection.
- Answers to Topic 2 practice questions.

#### 2.10 Common mistakes and misconceptions

- Treating NoSQL as a single, interchangeable category.
- Claiming one family is universally superior or obsolete.
- Selecting before listing access patterns.
- Using a store for something outside its guarantees (cache as system of
  record).
- Ignoring operational skills and on-call cost.
- Adding stores without an ownership rule.

#### 2.11 Mastery criteria

- Maps access patterns and requirements to categories with criteria.
- Quantifies capacity and understands consistency and transaction
  implications.
- Justifies (or rejects) additional stores in a polyglot design.

#### 2.12 Completion gate

- [ ] Selection matrix has access-pattern evidence for every row.
- [ ] Every selection names a rejected alternative and reason.
- [ ] System-of-record ownership stated.
- [ ] Topic 2 practice questions answered and corrected.

---

### Module 3 — [Object storage and file format selection](03-object-storage-and-file-format-selection.md)

#### 3.1 Learning objectives

- Explain what object storage is and how it differs from block and file
  storage.
- Describe data lake storage concepts and organisation.
- Compare row-oriented and column-oriented formats and the format
  characteristics covered by the topic file.
- Explain compression, file size, metadata overhead and the small-file
  problem.
- Explain schema representation and evolution in formats.
- Choose a layout and format with stated workload reasons and lifecycle costs.

#### 3.2 Why the topic matters in real-world Data Architecture

Object storage underlies most modern analytical platforms, and the file format
decides scan cost, compatibility and evolution. A poor choice raises cost and
slows every query for the life of the data.

#### 3.3 Prerequisite knowledge

Modules 1–2 here; 2D.2 Topic 3 (volume, growth); 2D.4 Topic 7 (schema
evolution).

> **Scope note.** Formats below are illustrative categories (row-oriented text
> and binary formats; columnar formats). Follow the formats the topic file
> names.

#### 3.4 Beginner-level learning sequence

1. **Define the three storage types:**

   | Type | Unit | Access | Typical use |
   | --- | --- | --- | --- |
   | Block | Fixed-size blocks | Low-latency random read/write via a volume | Databases, boot disks |
   | File | Files in directories | Shared file-system semantics | Shared documents, home directories |
   | Object | Immutable objects with metadata, addressed by key | HTTP-style get/put/list | Data lakes, backups, media, archives |

2. **Learn object-storage properties:** very high durability and scale, low
   cost per unit, whole-object writes (update = rewrite), list and metadata
   operations, eventual or strong listing behaviour depending on the service,
   no native multi-object transactions.
3. **Learn data lake storage concepts:** raw landing, standardised, curated
   areas organised by folder-like prefixes.
4. **Learn the format categories:** row-oriented text (CSV, JSON lines),
   row-oriented binary (schema-embedded record formats), columnar binary
   formats designed for analytics.
5. **Questions to answer:** Why can you not "update one row" in an object? Why
   does a columnar format read less data for a query on three columns?
6. **Exercise:** For six datasets, name the storage type and a candidate format
   with one reason.

**Ability to demonstrate:** distinguish storage types and format categories and
state a use for each.

#### 3.5 Intermediate-level learning sequence

1. **Compare formats against workloads:**

   | Characteristic | Row-oriented text | Row-oriented binary | Columnar binary |
   | --- | --- | --- | --- |
   | Human-readable | Yes | No | No |
   | Read few columns of many rows | Poor (reads everything) | Poor | Good |
   | Write/append single records | Good | Good | Poor (batch-oriented) |
   | Compression | Weak | Moderate | Strong |
   | Schema carried with data | No (CSV) / loose (JSON) | Often yes | Yes |
   | Typical use | Exchange, small data | Streaming/record exchange | Analytics scans |

2. **Understand compression:** trade CPU for storage and I/O; columnar layouts
   compress better because similar values sit together; codec choice trades
   speed against ratio.
3. **Quantify the effect:**

   ```text
   stored_size   = raw_size / compression_ratio
   scan_cost     ≈ bytes_read / scan_throughput        (columnar reads only needed columns)
   ```

   *Illustrative:* 10 TB raw, compression ratio 4 → 2.5 TB stored. A query that
   needs 3 of 30 equally sized columns reads roughly 10% of the column data in a
   columnar layout, before pruning, versus all of it in a row layout.
4. **Understand file size and metadata overhead:** too many small files add
   listing, open and planning overhead; too few large files reduce
   parallelism and make rewrites expensive. Typical guidance is a target file
   size in the range of tens to hundreds of megabytes; **treat any figure as
   workload-dependent and measure.**
5. **Understand layout:** prefix/folder organisation by source, domain,
   layer, and often date; naming that supports lifecycle rules and access
   control.
6. **Understand schema representation and evolution:** whether the schema is
   embedded; handling added/removed/renamed columns; type changes (2D.4
   Topic 7).
7. **Questions to answer:** How many files will a day of streaming data create
   if you write every minute? What does that do to a daily query?
8. **Exercise:** Compare three formats for Northbridge's transaction history
   (analytical scans), a reference-data export (small, human-checked) and an
   event feed (append and replay), with a reason per choice.

**Ability to demonstrate:** a format/layout choice per workload with the
property that drives it.

#### 3.6 Advanced-level learning sequence

1. **Evaluate scan efficiency:** column pruning, predicate pushdown using
   embedded statistics, row-group/stripe sizes, sorting within files to improve
   statistics, and why layout and format interact.
2. **Small-file arithmetic:**

   ```text
   files_per_day = writes_per_day × partitions_written_per_write
   files_per_partition = partition_size / target_file_size
   ```

   *Illustrative:* writing every minute to 10 partitions creates
   1,440 × 10 = 14,400 files per day; at 1 GB per partition per day (10 GB
   in total) that is about 0.7 MB per file, far below any sensible target. State the compaction
   strategy and who owns it.
3. **Metadata overhead and listing cost:** list operations are slow and billed;
   millions of objects stress planners; table formats (Topic 4) address this.
4. **Interoperability:** which engines read which formats; risks of proprietary
   or engine-specific layouts; ability to move data.
5. **Schema evolution in practice:** field matching by name versus position;
   adding columns; incompatible type changes; effect on historical files.
6. **Immutability and updates:** how corrections, deletes and late data are
   handled when objects cannot be modified (rewrite, append-and-reconcile,
   table format, soft delete).
7. **Lifecycle and cost:** storage classes, minimum storage durations, retrieval
   charges, request charges, egress; prefix design for lifecycle rules (Topic
   7).
8. **Security and governance at the storage level:** access control granularity
   (bucket/prefix versus object), encryption, residency, audit logging,
   deletion obligations for personal data in immutable files.
9. **Failure modes:** CSV as the system of record; unpartitioned multi-terabyte
   directories; one file per record; format chosen for the first tool only;
   deletion requests that cannot be honoured.
10. **Questions to answer:** What would make you keep a text format? What is
    your compaction trigger?
11. **Exercise:** Given a streaming source writing every minute, design a
    landing format, a compaction plan and a curated format, with file-count and
    size arithmetic and the cost trade-off.

**Ability to demonstrate:** a layout and format strategy with quantified
file-count, size and scan implications.

#### 3.7 Industry-application exercises

- Recommend a logical object-storage organisation and file-format strategy for
  Northbridge's card-transaction landing and curated data.
- Show the file-count and stored-size arithmetic with stated assumptions.
- Define the prefix structure and which lifecycle and access rules attach to
  which prefix.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* Analysts scan a 40 TB CSV archive for three columns and the cost
   is high. What changes, and what is lost?
2. *Scenario:* A deletion request requires removing one customer's records
   from files that are immutable. What are the options?
3. *Scenario:* Two engines must read the same dataset but support different
   format features. How do you decide?

#### 3.9 Expected outputs and deliverables

- Storage-type and format comparison tables.
- File-count and size worksheet.
- Logical layout (prefix design) with lifecycle and access rules.
- Answers to Topic 3 practice questions.

#### 3.10 Common mistakes and misconceptions

- Treating object storage as a file system with updates.
- Choosing a format because it is popular.
- Writing frequent tiny files and never compacting.
- Ignoring listing and metadata overhead.
- Designing prefixes without lifecycle or access control in mind.
- Forgetting deletion obligations for immutable data.

#### 3.11 Mastery criteria

- Explains why a format and layout fit the workload.
- Quantifies compression, scan and file-count effects.
- Accounts for schema evolution, lifecycle and governance in the layout.

#### 3.12 Completion gate

- [ ] Format comparison cites workload properties for each choice.
- [ ] Worksheet shows units, formulas and assumptions; reviewer reproduces it.
- [ ] Layout lists lifecycle and access rules per prefix.
- [ ] Topic 3 practice questions answered and corrected.

---

### Module 4 — [Warehouse, lakehouse and table format design](04-warehouse-lakehouse-and-table-format-design.md)

#### 4.1 Learning objectives

- Describe warehouse and lakehouse architectural characteristics.
- Distinguish a storage system, a table-management layer (table format) and a
  data platform.
- Explain what analytical table formats provide: metadata, schema management,
  transactions, versions and snapshots.
- Explain catalog and metadata integration and multi-engine interoperability.
- Evaluate governance, complexity and cost, and choose among a warehouse, a
  lakehouse or a combination.

#### 4.2 Why the topic matters in real-world Data Architecture

Plain files in object storage lack transactions, reliable schema management and
efficient discovery. Table formats and warehouses add them in different ways
and with different dependencies. Confusing the layers leads to adopting a
"lakehouse" that is really a folder of files, or to buying a platform when only
a table format was needed.

#### 4.3 Prerequisite knowledge

Modules 1–3 here; 2D.3 Topic 2 (warehouse, lake, lakehouse patterns); 2D.4
Topics 4–5 (dimensional and historical models).

> **Scope note.** This module teaches table-format *concepts* (metadata layer,
> snapshots, manifests, transaction log). Follow the specific table formats the
> topic file names, if any; this roadmap does not assume any.

#### 4.4 Beginner-level learning sequence

1. **Define the three layers explicitly:**

   | Layer | Meaning | Example (category) |
   | --- | --- | --- |
   | Storage system | Where bytes live | Object storage, warehouse-managed storage |
   | Table format / table-management layer | Metadata and rules that turn files into tables | Open table format with a transaction log |
   | Data platform | The whole environment: compute, catalog, governance, tooling | A lakehouse platform; a managed warehouse service |

2. **Define a warehouse:** an integrated, governed analytical store with
   managed storage, a SQL engine and strong optimisation (2D.3 Topic 2).
3. **Define a lakehouse:** open storage plus a table format and engines,
   giving warehouse-like management over lake storage.
4. **Define table-format capabilities:** schema tracking, atomic commits,
   snapshots, partition metadata, time travel, upserts/deletes (varies).
5. **Questions to answer:** Why is a table format not a database? Can a
   platform exist without a particular table format?
6. **Exercise:** Place ten named capabilities in the correct layer.

**Ability to demonstrate:** distinguish the three layers and say what each
contributes.

#### 4.5 Intermediate-level learning sequence

1. **Explain how a table format works conceptually:** data files plus a
   metadata layer (a log of commits or snapshots pointing to files, with
   statistics and partition information). Readers consult the metadata to know
   which files form the table at a point in time.
2. **Explain atomic commits and isolation:** a writer adds files and then
   publishes a new snapshot atomically; readers see a consistent snapshot;
   concurrent writers need conflict detection.
3. **Explain schema management and evolution:** tracked in metadata; adding
   columns; compatibility rules (2D.4 Topic 7).
4. **Explain snapshots and time travel:** query as of a time or version; use
   for audit and rollback; cost of retaining old snapshots and files.
5. **Explain updates, deletes and merges** on immutable files (rewrite or
   delete-marker approaches) and their performance implications; link to
   dimensional type 2 handling (2D.4 Topic 4).
6. **Explain catalog and metadata integration:** how tables are registered and
   discovered; role of a catalog in governance and access control; the
   difference between a storage-level catalog and a business catalog (2D.11).
7. **Explain multi-engine interoperability:** multiple engines reading and
   writing the same tables; dependence on shared catalog and format
   compatibility.
8. **Questions to answer:** What does a reader see if a writer fails halfway?
   How long should snapshots be retained?
9. **Exercise:** Describe, as a sequence of steps, an upsert into a table with a
   transaction log, including what a concurrent reader sees at each step.

**Ability to demonstrate:** explain how a table format provides consistency
and history over immutable files.

#### 4.6 Advanced-level learning sequence

1. **Transaction behaviour:** isolation level provided; behaviour under
   concurrent writers; conflict rates for hot partitions; retry strategies;
   guarantees across *multiple* tables (often none).
2. **Metadata management at scale:** growth of the metadata log; compaction of
   metadata; planning cost with very many files; maintenance jobs (compaction,
   snapshot expiry, orphan-file cleanup) and who owns them.
3. **Maintenance arithmetic:**

   ```text
   retained_storage = live_data + (snapshot_retention_days × daily_rewritten_data)
   ```

   *Illustrative:* 100 TB live; 2 TB rewritten per day by merges; 7-day
   retention keeps about 14 TB of superseded files → about 114 TB stored. State
   the retention assumption and what compliance-driven deletion does to it.
4. **Interoperability and openness:** engine support differences; catalog
   lock-in; portability of metadata; what is lost when moving between formats.
5. **Schema evolution in tables:** safe versus unsafe changes; effect on
   historical snapshots.
6. **Governance:** column/row-level controls where the platform provides them
   versus where storage permissions are the only control; deletion of personal
   data from snapshots (time travel conflicts with erasure).
7. **Cost and complexity:** managed warehouse (simpler, higher unit cost,
   possible lock-in) versus open lakehouse (flexible, more engineering)
   versus both (duplication). Quantify with a TCO sketch (2D.2 Topic 6).
8. **Selection criteria:** workload mix (BI concurrency, data science, ML),
   data variety, governance maturity, team skills, openness requirements,
   latency of ingestion, cost sensitivity.
9. **Failure modes:** small-file explosion; unexpired snapshots inflating
   cost; hot-partition write conflicts; "lakehouse" without a catalog; time
   travel retained past an erasure obligation.
10. **Questions to answer:** Which workload would still be better in a managed
    warehouse? Which maintenance task is most likely to be forgotten?
11. **Exercise:** Evaluate three options (managed warehouse, lakehouse on
    object storage with a table format, hybrid) for a described workload mix
    with a cost sketch, governance analysis and failure-mode list.

**Ability to demonstrate:** an evaluation that separates storage, table format
and platform and quantifies maintenance and retention costs.

#### 4.7 Industry-application exercises

- Propose a logical analytical storage design for Northbridge's risk and
  finance data, and justify the choice of architecture and table-management
  approach.
- Define the maintenance responsibilities (compaction, snapshot expiry) and
  owners.
- State how personal-data erasure interacts with time travel.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* Two teams write to the same table nightly and occasionally fail
   with commit conflicts. What design changes reduce conflicts?
2. *Scenario:* Storage costs double without data growth. What maintenance task
   was likely missed?
3. *Scenario:* A vendor describes its warehouse as a "lakehouse". How do you
   decide whether the label matters?

#### 4.9 Expected outputs and deliverables

- Layer-distinction table and capability placement.
- Table-format workflow description (commit, read, upsert).
- Architecture option evaluation with cost and maintenance sketch.
- Answers to Topic 4 practice questions.

#### 4.10 Common mistakes and misconceptions

- Treating storage, table format and platform as interchangeable.
- Assuming a lakehouse automatically provides governance or performance.
- Forgetting maintenance jobs and their owners.
- Ignoring the conflict between time travel and erasure obligations.
- Assuming multi-table atomicity.
- Selecting by label rather than capabilities.

#### 4.11 Mastery criteria

- Distinguishes the layers and explains table-format mechanics.
- Evaluates transaction, metadata and interoperability trade-offs.
- Quantifies maintenance and retention cost and chooses with criteria.

#### 4.12 Completion gate

- [ ] Layer table and workflow reviewed; no layer confusion.
- [ ] Option evaluation includes maintenance ownership and erasure impact.
- [ ] Topic 4 practice questions answered and corrected.

---

### Module 5 — [Partitioning, indexing, clustering and data layout](05-partitioning-indexing-clustering-and-data-layout.md)

#### 5.1 Learning objectives

- Explain partitioning, indexing and clustering as **different** techniques
  with different roles.
- Select partition keys and understand pruning.
- Identify skew, hotspots and cardinality problems.
- Understand index and layout maintenance costs and ingestion/update effects.
- Map query patterns to layout and measure whether an optimisation helps.

#### 5.2 Why the topic matters in real-world Data Architecture

The same data and hardware can be fast or slow depending on layout. A good
layout prunes most data before reading; a bad one makes every query a full
scan or concentrates load on one node. Layout choices also tax writes and
maintenance.

#### 5.3 Prerequisite knowledge

Modules 1–4 here; 2D.2 Topic 3 (volume, peaks); 2D.4 Topic 4 (grain).

#### 5.4 Beginner-level learning sequence

1. **Define the three techniques:**

   | Technique | Purpose | Mechanism |
   | --- | --- | --- |
   | Partitioning | Divide data into independently managed pieces to skip irrelevant data and spread load | Split by key/range/hash |
   | Indexing | Provide a fast access path to specific records | Auxiliary structure mapping values to locations |
   | Clustering / sorting | Place related data physically near each other | Order or group within storage |

2. **Learn why they are distinct:** partitioning limits *which pieces are read*;
   indexes limit *which records within a piece are located*; clustering improves
   *locality and statistics* so scans skip more.
3. **Learn the vocabulary:** partition key, pruning, selectivity, cardinality,
   hotspot, skew.
4. **Questions to answer:** Why does partitioning by date help a "last 7 days"
   query? Why does it not help a query by customer?
5. **Exercise:** For ten queries, state which technique would help and why.

**Ability to demonstrate:** describe each technique's role and a case where it
does not help.

#### 5.5 Intermediate-level learning sequence

1. **Start from the query patterns.** List the top queries with their filters
   and joins; a layout without this list is a guess.
2. **Choose partition keys** that match common filters, have moderate
   cardinality, and keep pieces in a useful size range.

   ```text
   partitions = distinct_key_values
   avg_partition_size = total_size / partitions
   ```

   *Illustrative:* 5 TB of data partitioned by day over 5 years
   (1,825 partitions) → about 2.7 GB per partition; by hour (43,800) → about
   114 MB per partition, which may create too many small pieces. Compare against
   the target size.
3. **Understand pruning:** the engine skips partitions whose key values cannot
   match the filter; requires the filter to be on the partition column in a
   usable form.
4. **Understand indexing for point and range access:** selective lookups benefit;
   low-selectivity columns rarely benefit; analytical scans often ignore
   indexes.
5. **Understand clustering/sorting:** sort by commonly filtered columns to
   improve data skipping through min/max statistics.
6. **Understand write-side effects:** each index must be maintained on every
   write; partitioning affects insert routing; clustering needs re-organising
   over time.
7. **Map access patterns to techniques** for transactional and analytical
   stores (the same words mean different things in each).
8. **Questions to answer:** What is the selectivity of this filter? Which
   queries does this layout make worse?
9. **Exercise:** For Northbridge transaction history with six listed query
   patterns, propose a layout and show which queries each technique helps.

**Ability to demonstrate:** a layout whose every element is linked to a named
query pattern.

#### 5.6 Advanced-level learning sequence

1. **Skew and hotspots:** uneven key distribution (a few very large customers or
   merchants), time-based keys that send all current writes to one partition,
   monotonically increasing keys in distributed stores. Quantify:

   ```text
   skew_ratio = max_partition_size / mean_partition_size
   ```

   *Illustrative:* a skew ratio of 8 means the busiest partition does eight times
   the average work and bounds query/processing time.
2. **Mitigations:** composite or hashed keys, salting, sub-partitioning of large
   values, adaptive splitting. State what each gives up (for example hashed keys
   defeat range scans).
3. **Cardinality trade-offs:** too low cardinality gives little pruning; too high
   gives many small pieces and metadata overhead.
4. **Competing access patterns:** a layout that favours one query hurts
   another; options: choose the dominant pattern, maintain a second copy
   organised differently, materialised views, or secondary indexes — each with
   cost and consistency implications.
5. **Maintenance cost:** index space and write amplification; re-clustering
   and compaction jobs; rebuilds; online versus offline operations.
6. **Workload drift:** the layout was right for last year's queries; monitor
   query patterns and revisit.
7. **Measure improvement:** define a baseline; a representative query set;
   metrics (bytes scanned, partitions/files read, latency percentiles, CPU,
   cost, write throughput, maintenance time); run before and after; verify
   correctness; keep the layout only if the benefit exceeds its total cost.
8. **Failure modes:** partition per customer; index on every column; layout
   chosen from a tutorial; optimisation validated on a single query; ignoring
   write-side degradation.
9. **Questions to answer:** What workload assumption makes this layout right?
   What observation would tell you it has become wrong?
10. **Exercise:** Take a layout proposal with a skewed key; quantify skew,
    propose two mitigations, and define the validation experiment with pass/fail
    criteria.

**Ability to demonstrate:** a layout with stated workload assumptions, a skew
analysis and a measurable validation plan.

#### 5.7 Industry-application exercises

- Design a logical data layout for Northbridge's transaction history and an
  operational ledger table, with stated workload assumptions for each.
- Define the validation experiment: baseline, query set, metrics, pass/fail
  threshold.
- List the maintenance tasks the layout creates and their owners.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* A table partitioned by customer id has millions of tiny
   partitions. Diagnose and redesign.
2. *Scenario:* An index added to speed one report slows nightly loads by 40%.
   How do you decide whether to keep it?
3. *Scenario:* The business adds a new query by merchant across all dates.
   What happens to the date-partitioned layout?

#### 5.9 Expected outputs and deliverables

- Query-pattern list and layout design.
- Skew and cardinality worksheet.
- Validation experiment plan.
- Answers to Topic 5 practice questions.

#### 5.10 Common mistakes and misconceptions

- Treating partitioning, indexing and clustering as interchangeable.
- Choosing partition keys without query evidence.
- Over-partitioning or over-indexing.
- Ignoring write and maintenance costs.
- Optimising one query and calling it done.
- Assuming layouts remain right as workloads change.

#### 5.11 Mastery criteria

- States the role of each technique and applies it with evidence.
- Quantifies skew, cardinality and partition size.
- Validates optimisations with measurements and decides on total cost.

#### 5.12 Completion gate

- [ ] Every layout element links to a query pattern and a stated assumption.
- [ ] Skew/cardinality arithmetic reproduced by a reviewer.
- [ ] Validation plan has baseline, metrics and pass/fail criteria.
- [ ] Topic 5 practice questions answered and corrected.

---

### Module 6 — [Replication, consistency and transaction boundaries](06-replication-consistency-and-transaction-boundaries.md)

#### 6.1 Learning objectives

- Explain replication and redundancy and their purposes.
- Distinguish synchronous and asynchronous replication and their consequences.
- Define consistency guarantees and transaction boundaries.
- Explain replication lag and its effect on consumers.
- Analyse partial failure, concurrent updates and cross-system consistency
  limits.
- Derive acceptable consistency behaviour from business requirements.
- Distinguish system guarantees from architectural assumptions.

#### 6.2 Why the topic matters in real-world Data Architecture

Money, regulation and trust depend on what a read returns after a write, what
survives a failure, and which updates succeed together. These properties are
defined by explicit guarantees, not by hope.

#### 6.3 Prerequisite knowledge

Modules 1–2 here; 2D.2 Topic 4 (availability targets); 2D.3 Topic 6
(delivery semantics, eventual consistency).

> **Terminology discipline.** Replication is not backup (a replicated deletion
> or corruption is replicated too). Replication is not synchronisation between
> systems (that is integration). A distributed-transaction capability within a
> system does not give automatic consistency across unrelated systems.

#### 6.4 Beginner-level learning sequence

1. **Define replication:** maintaining copies of data on more than one node or
   location, for availability, durability, read scale or locality.
2. **Define a transaction:** a unit of work that is atomic (all or nothing),
   consistent (respects rules), isolated (not visible half-done in the
   ways the isolation level forbids) and durable (survives a crash) — the ACID
   properties.
3. **Define consistency in plain terms:** what a reader can observe after
   writes; strong (latest committed value) versus eventual (converges later).
4. **Define synchronous vs asynchronous replication:**

   | Aspect | Synchronous | Asynchronous |
   | --- | --- | --- |
   | Write acknowledged when | Replica(s) confirm | Primary commits |
   | Data loss on primary failure | None (for acknowledged writes) | Possible (the lag) |
   | Write latency | Higher | Lower |
   | Availability if replica down | May block or degrade | Unaffected |

5. **Define basic failure scenarios:** node crash, network partition, slow
   replica, disk corruption, operator error.
6. **Questions to answer:** Why is a replica not a backup? What does "the
   transaction committed" guarantee?
7. **Exercise:** For three failure scenarios, state what is lost or
   unavailable under synchronous and asynchronous replication.

**Ability to demonstrate:** define the terms and the sync/async trade-off
accurately.

#### 6.5 Intermediate-level learning sequence

1. **Study replication topologies at the concept level:** single-primary with
   replicas, multi-primary, leaderless/quorum-based. State what each implies
   for conflicts and write paths.
2. **Study consistency models in increasing weakness:** strong/linearizable,
   sequential, read-your-writes, monotonic reads, eventual. Match each to a
   business need (balance after a payment, account list on a dashboard).
3. **Study replication lag and its effects:**

   ```text
   lag = time_replica_applies_change − time_primary_commits_change
   RPO_exposure (async) ≈ maximum lag at failure time
   ```

   Consumers reading from a replica may see old data; a user may not see their
   own write; two consumers may disagree.
4. **Study quorum in leaderless systems (concept):** with N replicas, write
   quorum W and read quorum R, overlap (R + W > N) is needed to read the latest
   acknowledged write; state what that costs in latency and availability.
5. **Study transaction boundaries:** what must succeed or fail together; keep
   boundaries as small as correctness allows; entities in one boundary can
   share atomicity, those in different boundaries use eventual consistency or
   compensation (2D.4 Topic 6 aggregates).
6. **Study isolation levels at the concept level** and the anomalies they allow
   (dirty, non-repeatable, phantom reads; write skew).
7. **Study recovery:** write-ahead logging concept; replication versus backup
   and point-in-time recovery; failover and the risk of split-brain.
8. **Questions to answer:** Which reads may tolerate staleness? Which updates
   must be atomic?
9. **Exercise:** For Northbridge's balance enquiry, payment posting and
   transaction history views, state the consistency required for each, with
   the business consequence of violating it.

**Ability to demonstrate:** a requirement-to-guarantee mapping for each
operation.

#### 6.6 Advanced-level learning sequence

1. **Partial failure and concurrent updates:** lost updates, write skew,
   conflicting writes in multi-primary systems; resolution strategies (last
   writer wins and its data loss, merge rules, application-level conflict
   handling).
2. **Cross-system consistency limits:** no atomic commit across independently
   operated systems without a coordination protocol; the costs of distributed
   commit protocols; alternatives: the outbox pattern (write the event in the
   same local transaction, publish asynchronously), idempotent consumers,
   sagas with compensating actions, reconciliation.
3. **Dual-write hazard:** updating a database and a message log in two steps
   can leave them inconsistent after a crash; show how to avoid it.
4. **Replication and derived stores:** caches, search indexes and analytical
   copies are replicas with their own lag and failure modes; define the
   system of record and the staleness contract for each (2D.3 Topic 6).
5. **Availability versus consistency under partition:** state which property
   the system sacrifices during a network partition and whether that is
   acceptable for the data class; avoid treating the trade-off as a product
   feature rather than a requirement.
6. **Durability across failure domains:** replicas in one zone survive a node
   failure but not a zone loss; match replica placement to the target recovery
   point and time (2D.12).
7. **Correctness testing:** failure injection, failover drills, lag
   measurement, reconciliation of counts and balances.
8. **Distinguish system guarantees from architectural assumptions:** read the
   stated guarantees of the chosen category and configuration; do not assume a
   property the documentation does not promise.
9. **Failure modes:** reads from lagging replicas used for decisions; failover
   losing acknowledged data under async replication; "exactly-once" assumed
   across systems; counters updated by read-modify-write without isolation;
   split-brain after failover.
10. **Questions to answer:** What is your maximum tolerable lag per data class?
    What invariant must survive any failure?
11. **Exercise:** Design the consistency strategy for a payment that debits one
    account in a ledger database and notifies downstream systems, covering
    transaction boundary, outbox or alternative, failure at each step, and
    reconciliation.

**Ability to demonstrate:** a strategy with explicit invariants, boundaries,
failure analysis and the guarantee relied on at each step.

#### 6.7 Industry-application exercises

- Define a replication and consistency strategy for Northbridge's account
  ledger with explicit correctness, availability and recovery requirements.
- Produce a table: operation, required consistency, replica use allowed,
  maximum lag, consequence of violation.
- Define the failover test you would run and its pass criteria.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* A customer transfers money and immediately sees the old balance
   from a replica. What are the options?
2. *Scenario:* The primary fails; asynchronous replicas are 2 s behind. What is
   lost and how do you reconcile?
3. *Scenario:* A service writes to the database and publishes an event
   separately; some events are missing after crashes. Fix it.

#### 6.9 Expected outputs and deliverables

- Operation-to-consistency requirements table.
- Replication topology and lag budget.
- Cross-system consistency design with failure analysis.
- Answers to Topic 6 practice questions.

#### 6.10 Common mistakes and misconceptions

- Treating replication as backup.
- Equating replication with synchronisation between systems.
- Assuming a distributed transaction facility guarantees consistency across
  unrelated systems.
- Assuming exactly-once behaviour end to end.
- Reading decisions from lagging replicas.
- Choosing sync/async without stating the loss or latency accepted.

#### 6.11 Mastery criteria

- Maps business correctness requirements to specific guarantees.
- Quantifies lag exposure and explains failure behaviour.
- Designs cross-system consistency without relying on unstated guarantees.

#### 6.12 Completion gate

- [ ] Requirements table links every guarantee to a business consequence.
- [ ] Failure analysis covers each step of the cross-system flow.
- [ ] Guarantees relied upon are separated from assumptions.
- [ ] Topic 6 practice questions answered and corrected.

---

### Module 7 — [Retention, archival and data lifecycle storage tiers](07-retention-archival-and-data-lifecycle-storage-tiers.md)

#### 7.1 Learning objectives

- Describe lifecycle stages and map data classes to them.
- Capture business, operational and regulatory retention requirements.
- Distinguish active, infrequently accessed, archival and deleted data.
- Explain storage tier characteristics: access frequency, retrieval latency,
  cost.
- Design retention policies and lifecycle automation.
- Distinguish backup from archive; handle legal holds and deletion constraints.
- Assign lifecycle ownership and weigh cost, accessibility, compliance and
  recoverability.

#### 7.2 Why the topic matters in real-world Data Architecture

Storing everything forever on the fastest tier is expensive; deleting too early
breaks regulation or investigations; deleting too late breaches privacy
obligations. Lifecycle design reconciles these pressures explicitly.

#### 7.3 Prerequisite knowledge

Modules 1–6 here; 2D.2 Topics 3, 5 (volume, retention estimates, regulatory
constraints).

> **Compliance note.** Retention periods are set by legal, regulatory and
> business sources specific to the organisation and jurisdiction. Figures in
> this roadmap are illustrative and are **not** legal advice. The learner
> records the source and owner of each requirement and treats legal
> confirmation as an input.

#### 7.4 Beginner-level learning sequence

1. **Learn lifecycle stages:** create → active use → infrequent use → archive →
   delete (with legal hold as an interrupt).
2. **Learn retention drivers:** business need, operational need, regulatory or
   legal obligation, contractual obligation, privacy-driven maximum retention.
3. **Learn tier concepts:**

   | Tier | Access frequency | Retrieval latency | Cost per unit stored | Cost to access |
   | --- | --- | --- | --- | --- |
   | Hot / active | Frequent | Milliseconds | Highest | Lowest |
   | Warm / infrequent | Occasional | Milliseconds to seconds | Lower | Higher (often per-retrieval) |
   | Cold / archive | Rare | Minutes to hours | Lowest | Highest, with delays |

4. **Learn the distinction between backup and archive:** backup protects against
   loss and corruption for recovery to a recent state; archive preserves data for
   long-term retention and retrieval of history. Different purposes, different
   retention, different access.
5. **Questions to answer:** Why is a backup not an archive? Why can cheaper
   storage cost more overall?
6. **Exercise:** Classify ten data sets by lifecycle stage and retention driver.

**Ability to demonstrate:** explain stages, drivers, tiers and the
backup/archive distinction.

#### 7.5 Intermediate-level learning sequence

1. **Build a retention schedule** by data class: class, owner, retention driver,
   minimum retention, maximum retention (if privacy-driven), disposition
   (delete/anonymise/archive), source of the requirement, review date.
2. **Map data classes and access patterns to tiers:** use access frequency over
   time (for example heavily used for 90 days, rarely thereafter).
3. **Quantify tier economics:**

   ```text
   monthly_cost = Σ_tier ( volume_tier × storage_price_tier )
                + retrieval_volume × retrieval_price
                + requests × request_price
   ```

   *Illustrative:* 100 TB with 30 TB hot, 40 TB warm, 30 TB cold. Moving 40 TB
   from hot to warm at a lower unit price reduces storage cost but adds
   retrieval charges if warm data are read often; compute the break-even
   retrieval volume (below).

   ```text
   break_even_retrieval = (price_hot − price_warm) × volume / retrieval_price
   ```

4. **Design lifecycle automation:** rules based on age or last access; transition
   and expiry rules; prefix or tag-based selection; testing rules on a copy
   first; audit logging of transitions and deletions.
5. **Preserve historical data appropriately:** which history must remain
   queryable (and in which tier), which can be rehydrated on request, and how
   formats and table metadata survive over years (Topics 3–4).
6. **Understand retrieval and restoration implications:** time to restore,
   minimum storage durations, early-deletion fees, whether archived data are
   queryable in place.
7. **Questions to answer:** Who approves moving a class to archive? How long
   does a regulator-requested retrieval take?
8. **Exercise:** For Northbridge transaction history, card data and call
   recordings, produce a retention schedule and tier plan with cost arithmetic
   (illustrative prices).

**Ability to demonstrate:** a schedule and tier plan with owners, sources and
cost arithmetic.

#### 7.6 Advanced-level learning sequence

1. **Retention conflicts:** a regulation requires keeping records for a minimum
   period while privacy rules limit retention of personal data; both apply to
   the same data. Resolve with data-class separation, pseudonymisation or
   anonymisation of fields, field-level deletion, and documented legal advice.
2. **Legal holds:** suspend deletion for specified data; scope, owner, release
   process; interaction with automated expiry; evidence of the hold.
3. **Deletion in practice:** deleting from immutable files, from table-format
   snapshots, from backups and from replicas and derived stores; cryptographic
   erasure (destroying keys) as an option; verification and certificates of
   deletion (links to 2D.10).
4. **Archive design for retrieval:** archive formats that remain readable
   (open, documented formats), accompanying schema and dictionary, index of
   archived content, test restores on a schedule.
5. **Backup versus archive in operations:** retention of backups should not
   silently become an archive; keep backup retention bounded and justified.
6. **Lifecycle governance and ownership:** policy owner, class owners,
   exception process, review cadence, reporting on compliance (data held past
   retention, holds in force), integration with the catalog (2D.11).
7. **Cost-compliance-accessibility-recoverability trade-offs:** choose the
   cheapest tier that still meets the retrieval target and compliance
   obligations, with an explicit statement of the retrieval delay accepted.
8. **Failure modes:** retention set by default and never reviewed; archive that
   cannot be read after format or schema changes; backups serving as the only
   archive; deletion jobs that miss replicas; legal hold overridden by
   automation; cost shock from retrieval charges.
9. **Questions to answer:** How would you prove that an expired record is gone
   everywhere? What happens to the archive when the schema changes?
10. **Exercise:** Design a lifecycle for a dataset with a seven-year minimum
    retention, a privacy-driven field-level maximum, and a legal-hold
    possibility; describe automation, deletion verification and cost.

**Ability to demonstrate:** a lifecycle design that resolves retention
conflicts, supports holds and verifies deletion, with a quantified cost.

#### 7.7 Industry-application exercises

- Design a logical lifecycle and storage-tier strategy for Northbridge's
  customer-transaction dataset.
- Produce the retention schedule with sources and owners (mark requirements
  needing legal confirmation).
- Define the quarterly test-restore and deletion-verification procedure.

#### 7.8 Practical scenarios and case-based reasoning

1. *Scenario:* An investigation requests data from eight years ago that were
   moved to archive. What determines how fast you can respond?
2. *Scenario:* A customer exercises an erasure right but the data must be kept
   for regulatory reasons. How do you reason about it?
3. *Scenario:* Storage bills fall after tiering but analytics costs rise. What
   happened?

#### 7.9 Expected outputs and deliverables

- Retention schedule and tier plan.
- Tier-economics worksheet.
- Lifecycle automation and deletion-verification design.
- Answers to Topic 7 practice questions.

#### 7.10 Common mistakes and misconceptions

- Treating backup as archive.
- Choosing tiers by storage price alone.
- Setting retention without a source or owner.
- Forgetting replicas, snapshots, backups and derived stores when deleting.
- Archiving in formats that become unreadable.
- Treating retention periods as legal advice instead of inputs to confirm.

#### 7.11 Mastery criteria

- Maps data classes to lifecycle and tier policy with sources.
- Quantifies tier economics including retrieval.
- Resolves retention conflicts and designs verifiable deletion and holds.

#### 7.12 Completion gate

- [ ] Retention schedule has a source and owner for every class.
- [ ] Cost worksheet includes retrieval and break-even.
- [ ] Deletion design covers copies, snapshots, backups and derived stores.
- [ ] Topic 7 practice questions answered and corrected.

---

## 5. Module dependencies and recommended learning order

### 5.1 Dependency table

| # | Topic file | Prerequisite concepts | Main learning outcome | Practical exercise / deliverable | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `01-oltp-olap-and-operational-analytical-separation.md` | 2D.2 Topics 3–4; 2D.4 Topics 1–4 | Classify workloads and justify separation (or its absence) | Workload profiles; separation comparison | Quantified data movement; a "no separation needed" case |
| 2 | `02-relational-nosql-and-specialized-database-selection.md` | Topic 1; 2D.4 Topics 1–3 | Select a database category from access patterns | Selection matrix; ADR | Access-pattern evidence and a rejected alternative per choice |
| 3 | `03-object-storage-and-file-format-selection.md` | Topics 1–2; 2D.4 Topic 7 | Choose storage organisation and format with quantification | Format comparison; file-count worksheet; layout | Reviewer reproduces arithmetic |
| 4 | `04-warehouse-lakehouse-and-table-format-design.md` | Topics 1–3; 2D.3 Topic 2 | Separate storage, table format and platform; design analytical storage | Option evaluation with maintenance cost | No layer confusion; erasure/time-travel impact stated |
| 5 | `05-partitioning-indexing-clustering-and-data-layout.md` | Topics 1–4 | Design and validate layout from query patterns | Layout design; skew worksheet; validation plan | Every element linked to a query pattern |
| 6 | `06-replication-consistency-and-transaction-boundaries.md` | Topics 1–2; 2D.3 Topic 6 | Derive consistency strategy from correctness needs | Requirements table; cross-system failure analysis | Guarantees separated from assumptions |
| 7 | `07-retention-archival-and-data-lifecycle-storage-tiers.md` | Topics 3–6; 2D.2 Topic 5 | Design lifecycle and tiering with compliance | Retention schedule; tier economics; deletion design | Sources, owners, break-even, deletion coverage |

### 5.2 Recommended order and why

1. **Topic 1: workload fundamentals.** Everything else depends on how the work
   is shaped. Technology comes after workload.
2. **Topic 2: technology-selection reasoning.** Builds the habit of mapping
   access patterns to categories for operational data.
3. **Topic 3: data storage and representation.** Introduces object storage and
   file formats, the base of analytical storage.
4. **Topic 4: warehouse, lakehouse and table formats.** Builds on Topic 3 by
   adding the management layer over files.
5. **Topic 5: layout.** Organisation and performance optimisation make sense
   once you know what the stores and formats are.
6. **Topic 6: replication, consistency and transactions.** Addresses
   correctness and failure behaviour across the stores selected so far.
7. **Topic 7: retention, archival, tiers.** Long-term management applies to
   everything above and constrains format, table and replica choices.

### 5.3 Dependencies and revisiting

| Dependency | Explanation |
| --- | --- |
| Database choice (2) ↔ replication capability (6) | A category's replication and transaction features limit the strategy available; revisit Topic 2 after Topic 6 |
| Retention requirements (7) ↔ format and table choice (3, 4) | Long retention, erasure obligations and time travel influence formats and snapshot policy; revisit Topics 3–4 after Topic 7 |
| Layout (5) ↔ table format (4) | Partitioning and clustering are expressed through the table format; revisit Topic 4 after Topic 5 |
| Separation (1) ↔ consistency (6) | The freshness of the analytical copy is a consistency decision |
| Format (3) ↔ schema evolution (2D.4 Topic 7) | Format capabilities limit safe evolution |
| Cost (all) ↔ lifecycle (7) | Cost estimates in earlier topics must be re-run with lifecycle assumptions |

| Trigger | Revisit |
| --- | --- |
| Query performance misses target | Topics 5, 3, 4 |
| Storage cost grows faster than data | Topics 7, 4, 3 |
| Failover test loses acknowledged data | Topic 6, Topic 2 |
| New regulation changes retention | Topic 7, Topics 3–4 |
| New workload with different access pattern | Topics 1, 2, 5 |

Adapt the sequence if the repository, once populated, establishes a more
appropriate order. Cross-references: foundations (2D.1), requirements (2D.2),
patterns (2D.3), modeling (2D.4), integration (2D.6), platform (2D.7), cloud
(2D.8), streaming (2D.9), governance (2D.10), metadata (2D.11), resilience
(2D.12), performance and cost (2D.13), serving (2D.14).

---

## 6. Practice questions and knowledge validation

### 6.1 Role of `practice-questions.md`

[`practice-questions.md`](practice-questions.md) is the module's practice and
assessment resource. It is currently empty. This roadmap defines how to use it
and what it should contain by category; it does not duplicate the questions.
Populate it to match the categories below.

### 6.2 Categories and how to use them

| Category | Purpose | Topics | Typical level |
| --- | --- | --- | --- |
| Database and workload terminology | Definitions and distinctions | 1–7 | Beginner |
| OLTP and OLAP workload classification | Classify from evidence | 1 | Beginner → intermediate |
| Database category selection | Map access patterns to categories | 2 | Intermediate → advanced |
| Object storage and file format comparison | Compare with arithmetic | 3 | Intermediate → advanced |
| Warehouse, lakehouse and table-format concepts | Layer distinction, mechanics, trade-offs | 4 | Intermediate → advanced |
| Data layout and access optimisation | Partition/index/cluster design, skew, validation | 5 | Intermediate → advanced |
| Replication and consistency reasoning | Lag, guarantees, failure behaviour | 6 | Advanced |
| Transaction boundary analysis | Atomicity scope, cross-system flows | 6 | Advanced |
| Retention and lifecycle design | Schedules, tiers, conflicts, deletion | 7 | Intermediate → advanced |
| Integrated storage architecture decisions | Cross-topic case studies | 1–7 | Industry |

### 6.3 Strategy

1. Answer each topic's questions after the topic, closed-book first.
2. For every quantitative question, write the formula, the units, the
   assumptions and a sentence of interpretation, not just the number.
3. For selection questions, write the workload, the access patterns, the
   candidates, the elimination reasons and the accepted trade-offs.
4. For consistency questions, state the guarantee relied on at each step.
5. Mark each answer correct / partly correct / wrong with a one-sentence
   reason; re-attempt after several days.
6. Keep integrated answers as written artefacts; they feed the project.
7. Have advanced and industry answers reviewed by another person.

### 6.4 Expected performance by level

| Level | Successful performance |
| --- | --- |
| Beginner | Accurate definitions; correct classification of workloads, stores and formats; no confusion between replication and backup, or storage system and table format |
| Intermediate | Workload analysis from evidence; category and format comparison with stated criteria; layouts linked to query patterns; correct basic arithmetic with units |
| Advanced | Trade-offs quantified; failure modes identified; consistency strategies derived from business needs; sensitivity considered; recommendations defended |
| Industry application | Integrated, traceable storage selection and logical layout that a reviewer can audit and reproduce |

### 6.5 Evaluation criteria

| Criterion | What to check |
| --- | --- |
| Conceptual correctness | Definitions and mechanisms are accurate |
| Workload fit | The choice follows the stated access pattern |
| Explicit assumptions | Inputs, peaks, growth and prices are stated and labelled illustrative |
| Quantitative reasoning | Formulas, units, conversions and ranges are correct |
| Trade-off analysis | What is gained and given up is stated |
| Defensibility | Alternatives, evidence and revisit conditions are cited |

---

## 7. Project — Storage technology selection and logical layout

Project file:
[`Projects/05-storage-technology-selection-and-logical-layout.md`](Projects/05-storage-technology-selection-and-logical-layout.md)
(currently empty; this section defines its intended content). The project index
is [`Projects/README.md`](Projects/README.md).

This is an **architecture selection and logical design exercise**, not a list
of database products or a physical implementation tutorial. The deliverable is
a defensible, workload-driven storage recommendation with a logical layout,
consistency strategy and lifecycle plan.

How it uses the seven topics:

| Project part | Topics |
| --- | --- |
| Workload characterisation and separation | 1 |
| Operational store selection | 2 |
| Object storage and file formats | 3 |
| Analytical storage and table management | 4 |
| Layout and access strategy | 5 |
| Replication, consistency, transactions | 6 |
| Retention, archival, tiers | 7 |

### 7.1 Project objective

You must demonstrate that you can:

- Characterise workloads and identify storage requirements.
- Compare suitable technology categories on explicit criteria.
- Design a logical storage layout with a data organisation strategy.
- Define replication, consistency and transaction boundaries.
- Explain lifecycle policies and tiering.
- Justify decisions using requirements, quantified estimates and trade-offs.

The project deliberately stays at the **logical architecture level**. It does
not require product configuration, deployment, infrastructure-as-code or
benchmark execution.

### 7.2 Project scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. It runs a core ledger, a cards platform and
a customer profile service. Payment postings are processed continuously; risk,
finance, regulatory reporting and fraud analytics need current and historical
data; call recordings and documents must be retained; a data lake created three
years ago holds poorly organised copies.

> All details and numbers below are **illustrative assumptions**, not facts
> about any real organisation. You may substitute a real or realistic scenario
> (observing confidentiality) but must label what you observed versus what you
> assume. Use decimal units and consistent time bases.

**Business problem.** Storage has grown ad hoc: analytics slow the operational
systems at month-end, history is expensive to query, retention is inconsistent,
and no one can state which store is authoritative for what.

**Workloads and consumers (assumed).**

| ID | Workload | Consumers | Characteristics (illustrative) |
| --- | --- | --- | --- |
| W1 | Payment posting and ledger | Payment services, customer app | ~2,000,000 postings/day average; peak factor 8; p99 < 100 ms; strong consistency |
| W2 | Customer profile lookups | App, branch, contact centre | ~30 million reads/day; point lookups by customer id; sub-50 ms |
| W3 | Regulatory and finance reporting | Finance, compliance | Monthly/quarterly; large scans over 7 years; reconciled |
| W4 | Fraud analytics | Fraud operations, data science | Recent events within ~60 s plus 24 months of history |
| W5 | Risk analytics | Risk | Daily batch over multi-year history |
| W6 | Documents and call recordings | Compliance, customer service | Unstructured; infrequent retrieval; long retention |
| W7 | Operational telemetry | Platform teams | High-rate time-ordered metrics; short retention |

**Data types and approximate volumes (illustrative).**

| Asset | Type | Approx. current size | Growth assumption |
| --- | --- | --- | --- |
| Ledger entries | Structured | 8 TB | +3 TB/year |
| Card events | Semi-structured | 40 TB | +25 TB/year |
| Customer profiles | Structured/semi-structured | 0.6 TB | +10%/year |
| Documents and recordings | Unstructured | 120 TB | +30 TB/year |
| Telemetry | Time-series | 5 TB | steady (30-day retention) |

**Performance, consistency, availability (illustrative).** Ledger availability
99.95% monthly with no loss of acknowledged postings; fraud path freshness
p95 ≤ 60 s; regulatory reports complete by T+2 business days; analytical
platform availability 99.5% on business days.

**Retention and archival (illustrative; legal confirmation required).** Ledger
and transaction records seven years minimum; call recordings five years; card
event detail three years then summarised; telemetry 30 days. Personal-data
fields have a privacy-driven handling requirement.

**Security and governance constraints (illustrative).** Personal data stays in
a stated jurisdiction; encryption at rest and in transit; fine-grained access
control for sensitive attributes; audit of access; existing identity services.

**In scope.** Workload characterisation, category selection, logical storage
architecture, layout, consistency, lifecycle, risks and trade-offs.

**Out of scope.** Product selection, sizing of specific instances, physical
schema and DDL, infrastructure automation, cloud-provider service mapping
(2D.8), pipeline implementation (2D.6), platform build (2D.7), benchmarks.

### 7.3 Step-by-step project execution

For each step: **Purpose · Inputs · Actions · Questions to answer · Outputs ·
Validation.**

| Step | Purpose | Inputs | Actions | Questions to answer | Outputs | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define problem and scope | Scenario | Write problem statement, scope, exclusions | What is decided and what is not? | Scope and assumptions | Sponsor-role reviewer confirms |
| 2 | Identify stakeholders, consumers, workload owners | Scenario | Register; map each workload to owner/consumers | Who is accountable for each workload? | Stakeholder and workload-owner list | Every workload has an owner or "unknown" |
| 3 | Inventory data assets and classify characteristics | Scenario; 2D.4 models | Asset list with category, size, sensitivity (as stated) | What is each asset and where does it come from? | Data asset inventory | Each asset has a category and size with unit |
| 4 | Characterise workloads | Steps 2–3 | Profile each workload: reads/writes, shape, concurrency, horizon | Which are OLTP, OLAP, mixed, specialised? | Workload characterisation | Classification justified by evidence |
| 5 | Document access patterns and requirements | Step 4 | List top queries/updates with keys, filters, concurrency, freshness, performance | What does each workload need to be cheap? | Access-pattern register | Every workload has top-queries listed |
| 6 | Estimate volumes, growth, retention, peaks | Steps 3–5; 2D.2 method | Apply formulas with ranges | Which input dominates? | Volume and growth estimates | Units, formulas, assumptions, ranges present |
| 7 | Record requirements, constraints, assumptions, risks | Steps 1–6 | Classify with the 2D.2 tests | Which constraints eliminate options? | Requirements and constraints register | No unclassified or ownerless item |
| 8 | Identify candidate categories | Steps 4–7; Topics 1–2 | Shortlist per workload plus a baseline | Is each candidate feasible and relevant? | Candidate list | Gate failures removed with reasons |
| 9 | Compare candidates | Steps 5–8; Section 7.5 | Matrix with evidence; criteria fixed before scoring | Where is evidence weakest? | Technology comparison matrix | Same criteria and evidence standard for each |
| 10 | Select operational and analytical approaches | Steps 1, 9 | Decide separation and categories; state system of record | Is separation justified by evidence? | Selection decisions | Each choice cites workload evidence |
| 11 | Determine role of object storage, formats, warehouse, lakehouse, table formats | Steps 9–10; Topics 3–4 | Assign roles and layers; distinguish storage, table format and platform | What does each layer provide? | Analytical storage approach | No layer confusion |
| 12 | Design logical layout and organisation | Steps 10–11 | Zones, prefixes, tables, formats, access rules | Is the organisation traceable to workloads? | Logical storage layout | Each element maps to an asset and workload |
| 13 | Evaluate partitioning, indexing, clustering, layout | Steps 5, 12; Topic 5 | Choose keys; quantify partition size and skew; plan validation | What assumption makes this layout right? | Data layout and access strategy | Every element linked to a query pattern |
| 14 | Define replication, consistency, transaction boundaries | Steps 5, 10; Topic 6 | Operation-to-guarantee table; replica use; cross-system design | What must never be lost or inconsistent? | Consistency strategy; boundary description | Each guarantee tied to a business consequence |
| 15 | Define retention, archival, tier policies | Steps 6, 7; Topic 7 | Retention schedule; tiers; automation; deletion and holds | Who owns each class and its source? | Retention and tier strategy | Source and owner for every class |
| 16 | Evaluate security, governance, complexity, cost | Steps 9–15 | TCO sketch with ranges; operational burden; governance controls | What does it cost to run and operate? | Risk and trade-off register | Numbers with units; ranges; labelled illustrative |
| 17 | Document alternatives, trade-offs, recommendation | Steps 9–16 | Rationale, rejected alternatives, revisit triggers (ADR form) | Why not the runner-up? | Recommendation and ADRs | Reasons cite criteria and evidence |
| 18 | Validate against access patterns and failure scenarios | Step 17 | Walk top queries through the layout; walk failures (node loss, zone loss, lag, corruption, deletion request) | Does the design behave as claimed? | Validation results | Each scenario outcome explained |
| 19 | Produce final selection and summary | All | Assemble; summarise decisions and open items | What is decided and what remains conditional? | Final architecture summary | Non-specialist can follow in ten minutes |

**Per-step guidance:**

1. State exclusions firmly; this project stops at the logical design.
2. Include security, compliance and operations as stakeholders.
3. Mark unknown sizes as unknown; do not invent them.
4. Classify by access pattern, not by system name.
5. Write queries as shapes ("by customer id", "range by date, group by
   segment").
6. Show formulas and units; give low/expected/high where uncertain.
7. Use the 2D.2 tests for constraint versus assumption versus risk.
8. Always include a "minimal change" baseline.
9. Fix criteria before scoring; rate from evidence.
10. Do not separate unless evidence shows contention, freshness or governance
    need.
11. Name each layer explicitly: storage, table format, platform.
12. Prefix/zone design must support lifecycle and access control.
13. State workload assumptions behind every optimisation.
14. Mark guarantees as system-provided or architecture-provided.
15. Retention requirements need a source; flag legal confirmation.
16. Include people and operations in cost.
17. Specific rejection reasons; no "too complex".
18. Include a deletion-request scenario and a lag scenario.
19. State conditional decisions and what evidence would settle them.

### 7.4 Required project deliverables

Deliverables are proportionate; related content is combined.

| # | Deliverable | Purpose | Minimum contents |
| --- | --- | --- | --- |
| D1 | Project scope and assumptions | Fix boundaries | Problem, objectives, in/out of scope, labelled assumptions |
| D2 | Data asset inventory | Know what is stored | Asset, purpose, category, size, growth, owner, retention, consumers |
| D3 | Workload characterisation | Basis of selection | Workload, type, read/write mix, access pattern, concurrency, freshness, consistency, availability |
| D4 | Storage requirements and constraints register | Bound the problem | Requirements with measures; constraints, assumptions, dependencies, risks with owners |
| D5 | Data volume and growth estimates | Quantify capacity | Formulas, units, assumptions, low/expected/high, sensitivity |
| D6 | Technology category comparison matrix | Transparent comparison | Criteria (gates, weights if used), per-candidate evidence and ratings |
| D7 | Storage technology selection rationale | Defend the choice | Chosen categories per workload, system of record, rejected alternatives, revisit triggers |
| D8 | Logical storage architecture diagram or structured view | Communicate | Stores, zones, flows, ownership, legend, version |
| D9 | Data layout and access strategy | Make access cheap | Partitioning, indexing, clustering per asset; assumptions; validation plan |
| D10 | Replication and consistency requirements | Correctness | Operation-to-guarantee table, replica rules, lag budget, recovery objectives |
| D11 | Transaction boundary description | Atomicity scope | Boundaries, cross-system flow, failure handling, reconciliation |
| D12 | Retention and storage-tier strategy | Lifecycle | Retention schedule with sources and owners, tiers, automation, deletion, holds, cost |
| D13 | Risk and trade-off register | Honest limits | Risks, trade-offs, mitigations, owners, triggers |
| D14 | Final architecture recommendation | Sponsor readout | One to two pages: decisions, rationale, trade-offs, cost range, conditional items, next steps |

### 7.5 Suggested templates and fields

Use only fields that serve a purpose. Mark `Unknown` rather than inventing
values, and carry `Source` and `Confidence` where they apply.

**Data asset inventory**

| Field | Purpose |
| --- | --- |
| Asset ID, name | Reference |
| Business purpose | Why it exists |
| Data category (structured / semi-structured / unstructured / time-series) | Store fit |
| Approximate size (with unit) | Capacity |
| Growth assumptions (rate, basis) | Projection |
| Data owner (if known) | Accountability |
| Retention requirement (and source) | Lifecycle |
| Consumers | Access patterns |

**Workload inventory**

| Field | Purpose |
| --- | --- |
| Workload ID, name | Reference |
| Workload type (OLTP / OLAP / mixed / specialised) | Classification |
| Read and write characteristics (rates, sizes) | Load |
| Access pattern (keys, filters, ranges) | Design driver |
| Concurrency | Capacity |
| Freshness or latency requirement (percentile, window) | Targets |
| Consistency requirement | Correctness |
| Availability expectation | Resilience |
| Growth assumptions | Projection |

**Technology comparison**

| Field | Purpose |
| --- | --- |
| Candidate category | Option |
| Workload fit | Match to access pattern |
| Data model suitability | Match to entities |
| Query and access capabilities | Flexibility |
| Scalability considerations | Growth |
| Consistency and transaction characteristics | Correctness |
| Operational complexity | Run cost |
| Governance considerations | Control |
| Cost assumptions (range, units) | Economics |
| Limitations and risks | Honesty |

**Logical storage layout**

| Field | Purpose |
| --- | --- |
| Data asset or logical zone | Subject |
| Storage category | Store type |
| Logical organisation | Structure |
| File or table format (where relevant) | Representation |
| Partitioning / indexing / clustering (where relevant) | Access |
| Retention class | Lifecycle |
| Access pattern | Justification |
| Governance considerations | Control |

**Decision/ADR** — use the structure proposed in module 2D.2 Topic 7.

### 7.6 Validation and quality assurance

| Check | How to verify |
| --- | --- |
| Every in-scope data asset has a documented storage requirement | D2 and D4 cross-checked; no asset without size, category and requirement |
| Workloads characterised before technologies selected | D3 dated before D6/D7; selections cite workload IDs |
| Recommended technologies fit stated access patterns | Each top query is walked through the chosen store and layout (step 18) |
| Quantitative estimates include units and assumptions | Reviewer recomputes at least three figures from D5/D12 |
| Layout choices have a clear rationale | Every layout element cites a query pattern and an assumption |
| Replication and consistency align with correctness requirements | Each guarantee maps to a business consequence; failure scenarios traced |
| Retention and archival align with business and regulatory needs | Each class has a source, owner and legal-confirmation flag |
| Operational complexity and cost accounted for | D13 and cost ranges include people and operations |
| Trade-offs and rejected alternatives documented | D7 and ADRs cite specific reasons |
| Logical architecture internally consistent and traceable | Every store in D8 appears in D6/D7 and vice versa; trace test passes |

### 7.7 Project completion gate

The project is complete only when **all** hold:

- [ ] D1–D14 exist, version-dated, with consistent IDs.
- [ ] **Workload analysis:** every workload has an access-pattern list, a
      classification justified by evidence and a measurable target; no
      technology appears before its workload is characterised.
- [ ] **Technology comparison:** at least three feasible candidates (including a
      baseline) per major decision; criteria and weights (if used) fixed and
      dated before scoring; gate failures recorded with reasons.
- [ ] **Quantification:** all estimates show formula, unit, assumption, range
      and illustrative label; a reviewer reproduces three figures.
- [ ] **Logical layout:** every layout element maps to an asset, a workload and
      a stated assumption; storage, table format and platform are distinguished.
- [ ] **Consistency strategy:** each critical operation has a required guarantee,
      a business consequence, a replica-use rule and a failure analysis;
      system-provided guarantees are separated from assumptions.
- [ ] **Lifecycle plan:** every data class has a retention source and owner, a
      tier plan with retrieval-cost break-even, deletion coverage including
      copies/snapshots/backups, and a legal-hold approach.
- [ ] **Validation:** top access patterns and at least five failure scenarios
      (including lag, zone loss, corruption and a deletion request) are walked
      through the design with explained outcomes.
- [ ] **Recommendation:** states what is decided, assumptions, accepted
      trade-offs, cost range and conditional items; readable by a non-specialist
      in ten minutes.
- [ ] **Traceability:** a random trace from three storage decisions back to
      requirements and workloads, and from three requirements forward to
      decisions, succeeds.
- [ ] An independent reviewer agrees the evidence supports the conclusions.

A diagram or comparison table existing is **not** sufficient.

### 7.8 Connection to subsequent modules

| Later module | How the project supports it | What belongs to that module |
| --- | --- | --- |
| 2D.6 Data integration and interoperability | Source and target store capabilities; synchronisation needs; system-of-record rules | Pipeline and interface design, change-capture mechanisms |
| 2D.7 Enterprise data platform and lakehouse | Storage layers, zones, table management approach | Platform components, service model, tenancy |
| 2D.8 Cloud, hybrid and multi-cloud | Category and constraint set to map onto services | Service selection, networking, identity |
| 2D.9 Streaming and real-time | Log and serving store roles, freshness targets | Stream processing design, state, delivery semantics |
| 2D.10 Governance, metadata and lifecycle management | Retention schedule, deletion design, access requirements | Policy engines, classification, lineage tooling |
| 2D.12 Reliability and disaster recovery | Replication, failure domains, recovery objectives | DR strategies, runbooks, drills |
| 2D.13 Performance, scalability and cost | Layout assumptions, cost sketches | Capacity validation, FinOps |
| 2D.14 Data access, serving and AI data | Stores and layouts that serve analytics and features | Semantic layers, feature and retrieval architecture |

Do not extend this project into implementing or deploying a production system.

---

## 8. Final learning assessment and completion checklist

Self-reported confidence is not sufficient; each row requires the stated
evidence.

| # | You can… | Evidence required for mastery |
| --- | --- | --- |
| 1 | Distinguish transactional and analytical workloads | Workload profiles justified by evidence; classification ≥ 90%; a case where separation is not needed |
| 2 | Select appropriate relational, NoSQL or specialised database categories | Selection matrix with access-pattern evidence, rejected alternatives and an ADR |
| 3 | Explain object storage and file-format trade-offs | Format comparison citing workload properties; reproducible file-count and size arithmetic |
| 4 | Compare warehouse, lakehouse and table-format design choices | Layer-distinction table; option evaluation with maintenance cost and erasure impact |
| 5 | Reason about partitioning, indexing, clustering and data layout | Layout linked to query patterns; skew worksheet; validation plan with pass/fail criteria |
| 6 | Evaluate replication, consistency and transaction boundaries | Operation-to-guarantee table; lag exposure; cross-system failure analysis |
| 7 | Design retention, archival and storage-tier strategies | Retention schedule with sources and owners; break-even calculation; deletion and hold design |
| 8 | Produce a defensible storage technology selection | D6, D7 and ADRs with criteria fixed before scoring and sensitivity considered |
| 9 | Create a logical storage layout aligned with workload requirements | D8, D9 and traceability test passed |
| 10 | Explain architectural decisions using evidence, constraints and trade-offs | Challenge round: two reviewer objections answered from recorded workload evidence and estimates |

Module complete when:

- [ ] All seven topic completion gates are signed off.
- [ ] `practice-questions.md` answered; wrong answers corrected and
      re-attempted.
- [ ] The project completion gate (Section 7.7) is met.
- [ ] You have presented the recommendation and answered a reviewer's challenges
      without introducing unsupported claims.
- [ ] Open questions are logged for the next module (2D.6).

---

## 9. Where this module leads

Module 2D.6, **Data Integration and Interoperability**, takes the stores,
system-of-record rules, freshness needs and consistency strategies decided here
and designs how data move between them: batch and incremental ingestion,
change data capture, APIs and files, event contracts, deduplication and
reconciliation.
