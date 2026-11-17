# Practice Questions — Stage 2D: Data Architecture / Database and Storage Architecture

**Controlling syllabus:** `roadmap-Database-and-Storage-Architecture.md`  
**Module location:** `Stage 2D — Data Architecture/05-Database-and-Storage-Architecture/practice-questions.md`  
**Scope:** Topics 1–7 in this module. All organizations, prices, workloads, targets, and numeric values in this question bank are fictional and illustrative unless a question explicitly says to obtain a real requirement from an authoritative source. No product-specific implementation is assumed.

## 1. File purpose and instructions

This bank checks whether you can reason from business requirements and workload evidence to a defensible storage decision. It is not a terminology-only quiz. It tests workload classification, candidate selection, logical layout, quantitative sizing, failure behavior, lifecycle policy, and the quality of the evidence behind a recommendation.

### Closed-book protocol

1. Attempt the question prompts in Sections 3–7 before reading Section 8. Section 7 contains quantitative prompts only; the worked solutions are grouped in Section 8.5. Hide or skip Section 8 until the first attempt is complete.
2. Record assumptions explicitly. If a question lacks information needed for a unique choice, identify the missing input and give a conditional recommendation rather than inventing a fact.
3. For every calculation, write the formula, units, substitutions, arithmetic, assumptions, and a sentence interpreting the result. Use decimal storage units unless a question states otherwise: 1 GB = 10⁹ bytes; 1 TB = 1,000 GB; 1 day = 86,400 seconds.
4. For a selection question, state: workload and access pattern; criteria; at least two candidates plus a baseline where relevant; why alternatives were rejected; accepted trade-offs; validation evidence; and conditions that would trigger reconsideration.
5. For consistency questions, identify the exact system guarantee relied on at each step and distinguish it from an application assumption, monitoring expectation, or compensating mechanism.
6. Mark each answer **Correct**, **Partly correct**, or **Wrong** using Section 8.6. Record errors in Section 9 and re-attempt after a delay without copying the answer key.
7. Open-ended answers can differ from the model answer. A defensible alternative earns credit when assumptions, evidence, risks, and trade-offs are explicit.

## 2. Assessment principles and how to use the question bank

The roadmap's storage-selection loop applies throughout: **characterise workload → state access pattern → quantify → shortlist candidates → test consistency/failure behaviour → estimate cost and effort → decide and record → validate → revise**.

- **Beginner:** accurate concepts, distinctions, and classification.
- **Intermediate:** access-pattern-led choices, comparison, layout, and arithmetic with units.
- **Advanced:** quantified trade-offs, failure analysis, sensitivity, consistency guarantees, and lifecycle interactions.
- **Industry application:** traceable architecture reasoning across multiple topics, with evidence that another reviewer can reproduce.

The bank contains eight core questions for each topic (56 total), distributed across the four levels, plus integrated cases and a separate quantitative set. The answer key is deliberately separated from prompts. Numeric inputs are illustrative, not benchmarks or target recommendations. Where real legal, contractual, privacy, or business requirements matter, name the source and accountable owner; do not infer a universal rule.

### Evaluation dimensions

1. **Conceptual correctness:** terminology and mechanisms are accurate.
2. **Workload fit:** the design follows actual access patterns and measurable targets.
3. **Explicit assumptions:** rates, peaks, growth, prices, retention, and guarantees are identified and sourced or labelled illustrative.
4. **Quantitative reasoning:** formula, units, conversions, arithmetic, and interpretation are correct.
5. **Trade-off analysis:** gains, losses, alternatives, and operational burden are stated.
6. **Defensibility:** claims map to evidence; validation and revisit triggers are clear.

## 3. Beginner questions

### Topic 1 — OLTP, OLAP, and operational-analytical separation

**T1-B1 — Define and distinguish.** Define online transaction processing (OLTP) and online analytical processing (OLAP). Give one typical access pattern and one limitation for each.

**T1-B2 — Classify from evidence.** A service accepts one order at a time, checks inventory, and updates order status under concurrent user requests. Classify the dominant workload and name the correctness concern that matters most.

**T1-B3 — Classify from evidence.** An analyst scans 18 months of sales, groups by product and region, and calculates monthly trends. Classify the dominant workload and explain why its access pattern differs from T1-B2.

### Topic 2 — Relational, NoSQL, and specialized database selection

**T2-B1 — Terminology.** Explain the difference between a relational database, a key-value store, a document store, a graph store, a time-series store, and a search index. State that these are categories, not product recommendations.

**T2-B2 — Access-pattern match.** A service retrieves a customer's profile by a stable customer ID and updates a small set of fields. What access pattern should drive the category decision? Name two plausible candidates and one missing requirement.

**T2-B3 — Critique a claim.** “NoSQL is always faster and scales better than relational databases.” Identify at least three reasons this claim is not a defensible architecture decision.

### Topic 3 — Object storage and file format selection

**T3-B1 — Distinguish.** Explain what an object-storage system stores and why it is not equivalent to a transactional database with low-latency row updates.

**T3-B2 — Format purpose.** Compare a row-oriented text format such as CSV with a columnar analytical format. Name one workload where each can be reasonable and one limitation of each.

**T3-B3 — Basic arithmetic.** A daily export contains 2,000,000 records averaging 500 bytes each before compression. Calculate raw daily volume in decimal GB. State the assumption about record size.

### Topic 4 — Warehouse, lakehouse, and table-format design

**T4-B1 — Layer distinction.** Explain the difference between object storage, a table format, and a data platform. Why is treating them as synonyms a design error?

**T4-B2 — Compare patterns.** Give one reason a governed data warehouse may fit curated reporting and one reason a lakehouse may fit varied, file-based analytical data. State a trade-off for each.

**T4-B3 — Snapshot concept.** Explain why a table format's snapshot or time-travel capability is not automatically the same as an independent backup or a deletion guarantee.

### Topic 5 — Partitioning, indexing, clustering, and data layout

**T5-B1 — Define.** Distinguish partitioning, indexing, and clustering/sorting. For each, state the type of access pattern it may help.

**T5-B2 — Query-driven choice.** A query repeatedly filters a large event table by event date and then aggregates by customer ID. What evidence would you collect before choosing a partition key or clustering columns?

**T5-B3 — Failure symptom.** A table has thousands of tiny files and queries are slower despite pruning many partitions. Name two plausible causes and two measurements to collect before changing layout.

### Topic 6 — Replication, consistency, and transaction boundaries

**T6-B1 — Distinguish.** Explain replication, backup, replication lag, consistency, and transaction atomicity. Why does replication not replace backup?

**T6-B2 — Stale-read classification.** A user updates an account on the primary and immediately reads from a lagging replica, seeing the old value. Name the observed failure mode and one possible architectural control.

**T6-B3 — Transaction boundary.** A process writes an order to a database and then publishes an event in a separate system. Explain the dual-write hazard in plain language.

### Topic 7 — Retention, archival, and data lifecycle storage tiers

**T7-B1 — Lifecycle.** Describe create, active use, infrequent use, archive, and delete as lifecycle stages. Explain how a legal hold can interrupt the normal path to deletion.

**T7-B2 — Archive versus backup.** Distinguish archival from backup by purpose and retrieval expectations. Why does a backup not automatically meet an archival or discovery requirement?

**T7-B3 — Retention drivers.** List four different drivers of retention and identify who should own the source/interpretation of each requirement. Do not invent a legal period.

## 4. Intermediate questions

### Topic 1 — OLTP, OLAP, and operational-analytical separation

**T1-I1 — Mixed workload.** A customer-facing system performs 900 small writes/s at peak and serves operational point reads, while an internal dashboard runs large joins over 24 months of history. Explain the contention risk and compare (a) keeping both on one store and (b) separating the analytical workload. State what evidence would justify either choice.

**T1-I2 — Separation not needed.** A small internal tool has 12 users, low write volume, and a report over a few thousand rows. Propose a minimal-change baseline and explain why a separate analytical platform may be unnecessary. Identify a measurable trigger that would cause you to revisit it.

**T1-I3 — Freshness and consistency.** An operations dashboard must show changes within an agreed short freshness window, but it does not need to participate in transactions. Compare a read replica with a separately ingested analytical projection. What freshness metric, failure behavior, and source-of-truth rule must be specified?

### Topic 2 — Relational, NoSQL, and specialized database selection

**T2-I1 — Selection matrix.** For a ledger-like workload requiring multi-row invariants, unique constraints, and queries by account and date, compare a relational database with a document or key-value design. State the workload assumptions, elimination reasons, trade-offs, and validation evidence.

**T2-I2 — Specialized store.** A support team needs ranked full-text search across ticket descriptions and filters by status. Compare a search index with using only the primary relational database. Explain how the search index should be treated relative to the system of record.

**T2-I3 — Graph versus relational.** A fraud analyst explores multi-hop relationships among accounts, devices, and merchants, while operational writes still require ordinary integrity constraints. Compare a graph-oriented store with relational queries as candidates. State the query evidence, scale, update consistency, and operating-cost measurements needed before introducing a specialized store.

### Topic 3 — Object storage and file format selection

**T3-I1 — Format comparison.** A batch analytics job reads only 5 of 80 columns from a large dataset and filters by date. Compare CSV with a columnar format using scan volume, compression, schema, and interoperability as criteria. State what must be measured in a representative test.

**T3-I2 — File-count design.** A partition contains 1.2 GB of compressed data and the team targets files of approximately 200 MB. Estimate files per partition. Explain why the quotient is a planning estimate rather than a guaranteed physical file count.

**T3-I3 — Object naming and partition metadata.** A team proposes encoding every possible filter, including customer ID, region, event type, and minute, into object prefixes. Explain how high-cardinality prefixes can create operational and query-planning problems. Propose a method to choose prefix/partition columns from observed access patterns and lifecycle needs.

### Topic 4 — Warehouse, lakehouse, and table-format design

**T4-I1 — Choose an analytical pattern.** A team needs governed finance reporting plus exploratory analysis on semi-structured event data. Compare warehouse-only, object files without table management, and lakehouse-style management. State a defensible conditional recommendation and maintenance costs to include.

**T4-I2 — Schema evolution.** An upstream producer adds a nullable field and later changes the meaning of an existing field without changing its name. Distinguish a syntactic schema change from a semantic contract change and explain how storage/table design should respond.

**T4-I3 — Managed table versus plain files.** Two jobs may write to the same analytical dataset while readers need a consistent committed view. Compare plain files with a table format that provides documented commit/snapshot semantics. Name the guarantee you need, the concurrency/failure tests, and the cleanup/erasure implications to validate.

### Topic 5 — Partitioning, indexing, clustering, and data layout

**T5-I1 — Partition choice.** A 4 TB event table is queried mostly for the last 7 days, but 30% of queries also request a single customer across 2 years. Compare partitioning by day with partitioning by customer. State likely benefits, risks, and a validation plan.

**T5-I2 — Index economics.** A frequently used index speeds a query but increases write work and storage. Propose the measurements needed to decide whether to keep it. Explain why a high-cardinality column alone does not prove an index is beneficial.

**T5-I3 — Partition count.** An illustrative 3 TB table is partitioned into 10-minute time windows and produces 2 MB files per partition. Explain why partition count and file size are warning signals but not sufficient alone to select a new layout. Name the query and write evidence needed to compare coarser time partitions with clustering.

### Topic 6 — Replication, consistency, and transaction boundaries

**T6-I1 — Guarantee table.** For (a) reading immediately after a write, (b) reporting from an analytical replica, and (c) recovering after primary loss, state the required business guarantee and which mechanism or evidence would be needed. Separate system guarantee from assumed behavior.

**T6-I2 — Outbox reasoning.** A service commits a payment record and must publish a payment event. Explain how a transactional outbox reduces the dual-write gap, then name remaining duplicate/order/lag risks and how consumers should respond.

**T6-I3 — Transaction scope.** A business operation updates two rows in one database and then invokes a remote service. Which part may be covered by one local ACID transaction, and which part is outside that transaction? Propose a failure/retry/compensation design without claiming atomicity across systems unless an explicit distributed guarantee exists.

### Topic 7 — Retention, archival, and data lifecycle storage tiers

**T7-I1 — Retention schedule.** Create one schedule row for a fictional class of completed support tickets. Include purpose, minimum and maximum retention (or explicitly mark unknown), source, accountable owner, hold rule, tier, deletion method, and verification evidence. Label invented values illustrative and flag unresolved policy.

**T7-I2 — Tier economics.** A cold tier costs less to store but charges for retrieval and has slower access. Explain which workload facts determine whether moving infrequently accessed data is economical. Include retrieval volume, frequency, latency, requests, transition charges, and operational work.

**T7-I3 — Backup expiry and deletion.** A data class reaches its deletion date, but a backup copy is immutable until its configured expiry and a legal hold may apply to some records. Describe the decision gates and audit statuses needed before declaring deletion complete. Distinguish a deletion request, a hold, backup expiry, and verified completion.

## 5. Advanced questions

### Topic 1 — OLTP, OLAP, and operational-analytical separation

**T1-A1 — Quantified separation decision.** An illustrative operational database receives 600 GB/day of new data. An analytical workload scans 4 TB per day and competes with transaction traffic. Compare three options: shared store, read replica, and separate analytical platform. Identify costs beyond storage, freshness/lag consequences, failure coupling, and the measurements required before deciding. Do not assume separation is always best.

**T1-A2 — Critique a flawed design.** “We will copy every operational table nightly to a warehouse, so analytics will be fresh and will never affect transactions.” Identify at least four unsupported assumptions or failure modes and propose a validation plan.

### Topic 2 — Relational, NoSQL, and specialized database selection

**T2-A1 — Hot key and consistency.** A key-value service has very high request volume for a small number of tenant IDs and requires per-tenant counters that must not lose acknowledged increments. Compare a single relational store, a distributed key-value category, and a partitioned design. Identify hot-key risk, correctness requirements, candidate elimination criteria, and failure tests.

**T2-A2 — Category decision under uncertainty.** Propose a decision process for a workload with uncertain growth, flexible document attributes, and occasional multi-entity transactions. Include a baseline, at least two candidates, decision criteria, assumptions, evidence to collect, and triggers to revisit the choice. Do not choose solely from “flexible schema.”

### Topic 3 — Object storage and file format selection

**T3-A1 — Compression and file sizing.** A pipeline produces 480 GB/day of raw data and the measured compression ratio is 4:1. If the design targets 256 MB files, estimate compressed daily volume and file count using decimal MB/GB. State why actual counts can differ and what small-file symptoms to monitor.

**T3-A2 — Format migration critique.** A team wants to convert all historical CSV files to a columnar format because “columnar is always faster.” List the workload, compatibility, schema, operational, and migration risks to test. Define a rollback/verification approach.

### Topic 4 — Warehouse, lakehouse, and table-format design

**T4-A1 — Snapshot and erasure interaction.** A lakehouse table retains historical snapshots for reproducibility. A valid erasure request may require removing a subject's data from current and historical table state. Explain the architectural conflict, identify required policy decisions, and specify how you would validate that cleanup covers snapshots, derived outputs, and retained copies. Do not promise instant deletion if immutable or governed copies constrain it.

**T4-A2 — Layered design critique.** A proposal describes “the lakehouse” as one product that provides object storage, transactions, query engine, catalog, security, backup, and deletion. Explain the distinct layers and responsibilities that must be verified rather than assumed.

### Topic 5 — Partitioning, indexing, clustering, and data layout

**T5-A1 — Skewed hot partition.** A stream table is partitioned by tenant. In this illustrative workload, the system receives 1,000,000 events/hour across 100 tenants; one tenant generates 45% of all events, and assume the remaining events are evenly distributed across the other 99 tenants. Calculate the mean events/hour per tenant and the max-partition-to-mean skew ratio. Then diagnose the hot partition and propose alternatives. Discuss finer partitioning, salting/bucketing or time subdivision where appropriate, query consequences, and correctness/maintenance trade-offs. State tests that would show whether the redesign works.

**T5-A2 — Scan and pruning estimate.** An illustrative table contains 8 TB. A date predicate is expected to prune 87.5% of data, and remaining throughput is assumed to be 400 MB/s. Estimate bytes scanned and idealized scan time. Explain why observed elapsed time can differ substantially.

### Topic 6 — Replication, consistency, and transaction boundaries

**T6-A1 — Failover timeline.** The primary acknowledges writes; asynchronous replicas lag by up to an observed 18 seconds. The primary fails, and a replica is promoted. Analyze the possible acknowledged-write exposure, what can and cannot be inferred from observed lag, and what RPO and recovery tests must establish. Do not treat observed lag as a guaranteed worst-case bound.

**T6-A2 — Event loss and duplication.** A producer commits a database row, crashes before publishing an event, and a retry later publishes twice. Design a failure-aware flow using an outbox or equivalent durable handoff, idempotency key, consumer deduplication, ordering policy, reconciliation, and observable evidence. State exactly which guarantees are provided by each system and which are application-level.

### Topic 7 — Retention, archival, and data lifecycle storage tiers

**T7-A1 — Conflicting retention constraints.** A data class has a proposed long minimum retention period from a compliance stakeholder, a field-level privacy rule that may impose a shorter maximum lifetime, and a possible legal hold. Design the exception workflow. State which facts must be confirmed by legal/privacy authorities, how automation is prevented from deleting held records or retaining fields indefinitely, and how the final decision is audited. Do not invent a legal period.

**T7-A2 — Tier break-even.** A team proposes moving 500 TB to archive based only on a lower monthly storage rate. Build a complete cost comparison including expected retrieval volume/frequency, request and transition charges, restores, retrieval latency, and operations. Derive a break-even condition and identify uncertainty ranges that could reverse the decision.

## 6. Industry-application / integrated case questions

All details in this section are fictional illustrative assumptions. The cases test architectural reasoning, not knowledge of a particular vendor.

### Topic-specific industry-application prompts

**T1-IA1 — Operational and analytical boundary.** A subscription business has a customer-facing account service and a daily executive report. Interview the hypothetical stakeholders by listing the workload facts you need, compare a shared-store baseline with one separated design, and define the measurements that would make you keep or change the baseline.

**T2-IA1 — Category selection memo.** A claims workflow stores structured claim state, flexible attachments metadata, and needs relationship exploration for suspicious claim networks. Recommend a primary system-of-record category and any justified specialized projection. Include at least three candidates, transaction/integrity requirements, rejected alternatives, sync/deletion risks, and validation evidence.

**T3-IA1 — Data exchange design.** A producer sends daily exports to three consumers: spreadsheet users, a large column-selective analytics job, and a long-term archive. Design a file/format strategy, including whether one format should serve all consumers, conversion cost, schema/metadata handling, naming/partitioning, file-size checks, and a validation plan.

**T4-IA1 — Analytical platform decision.** A team has curated finance reports and evolving clickstream events. Produce a warehouse-only, lakehouse-style, or hybrid comparison that distinguishes object storage, table format, catalog, query engine, and platform responsibilities. Include snapshot/time-travel and erasure consequences, maintenance ownership, and a revisit trigger.

**T5-IA1 — Layout review.** A data platform's top three queries are date-range aggregation, point lookup by event ID, and two-year customer history. Propose a logical layout and a benchmark plan. State what would make you reject your own proposal, including skew, tiny files, write amplification, and maintenance overhead.

**T6-IA1 — Payment event incident.** During a fictional payment incident, a database row exists but the downstream event is missing; some other events are duplicated. Write a failure timeline and propose a recovery design. Distinguish local transaction guarantees, publication/delivery guarantees, idempotent effects, ordering, reconciliation, and evidence needed before closing the incident.

**T7-IA1 — Lifecycle exception review.** A fictional dataset is past its normal deletion date, some fields have a privacy-driven maximum lifetime, a longer minimum retention claim is awaiting source confirmation, and a legal hold may cover a subset. Produce a decision table and safe automation behavior. Identify which actions can proceed, which must pause, the authority required to resolve the conflict, and the evidence needed to verify final disposition.

**IA-1 — Northbridge Bank, coherent design across all seven topics.** Northbridge Bank (fictional) operates customer accounts, processes transactions, produces regulatory and management reports, and stores event history. Draft a coherent storage recommendation that includes: (1) minimal-change baseline; (2) assets and workload profiles; (3) access patterns and measurable targets; (4) at least three feasible candidates including the baseline for major choices; (5) logical storage layout and format/table-format distinctions; (6) partition/index/clustering rationale; (7) consistency guarantees and transaction boundaries; (8) retention schedule, tiering, legal-hold handling, and deletion across copies; (9) cost and risk range; (10) validation evidence; and (11) conditional revisit triggers. State assumptions and rejected alternatives. Do not turn this answer into a deployment plan or claim actual legal requirements.

**IA-2 — Separation decision.** A small business has one operational application and a report that scans 20,000 rows once each morning. Compare keeping the workload together with a separate analytical store. What evidence would justify staying with the baseline, and what measurable triggers would justify separation?

**IA-3 — Mixed workload with freshness requirement.** A commerce service handles point updates and also serves near-real-time operational dashboards. Propose two candidate designs and explain how analytical freshness, read isolation, replica lag, transaction contention, and data movement affect the decision.

**IA-4 — Skew plus layout.** A telemetry dataset is partitioned by customer ID, but one customer contributes nearly half of the data. Queries mostly filter by event date and sometimes inspect that customer's full history. Diagnose why the current partitioning is poor, propose alternatives, and specify a before/after benchmark matrix.

**IA-5 — Cross-system event correctness.** An order service writes to its database, publishes an event, and a downstream analytics pipeline updates a table. Trace failure outcomes for crash-before-publish, publish-before-acknowledgement, duplicate delivery, out-of-order delivery, and consumer outage. Identify guarantees, application assumptions, reconciliation evidence, and business-visible consequences.

**IA-6 — Lifecycle, snapshot, and erasure.** An analytical table uses snapshots for rollback and reproducible reporting. A data-subject erasure request arrives while an investigation may place some records under hold. Map current tables, snapshots, replicas, backups, derived stores, exports, and downstream consumers. Define the decision gates, hold precedence handling, approved exceptions, deletion evidence, and limitations on immediate deletion. Route conflicts to the appropriate legal/privacy authority.

**IA-7 — Archive economics under uncertainty.** A historical dataset is large, rarely accessed, and expensive to keep in its active tier. Estimate savings under at least three retrieval scenarios (low/base/high), including request, retrieval, transition, restore, and operational costs. State latency requirements and identify the point at which retrieval charges or operational burden offset storage savings.

**IA-8 — Architecture challenge review.** Review this proposal: “Use a distributed NoSQL database for everything, copy all tables to a lake nightly, partition by every available column, keep all snapshots forever for safety, and delete from the primary table when a user asks.” Identify at least eight independent defects spanning all seven topics. For each defect, state the missing evidence and a concrete validation or governance control.

**IA-9 — Decision record under uncertainty.** A new workload has an unclear growth curve and a team that has limited operating experience with specialized stores. Produce a short architecture decision record (ADR): context, workload facts, candidates, fixed decision criteria, chosen baseline, rejected options, assumptions, risks, validation plan, and revisit triggers. Explain why the recommendation should be conditional rather than falsely precise.

**IA-10 — Traceability challenge.** Pick three requirements from a fictional case and trace each forward to workload, category, logical layout, consistency/lifecycle policy, cost estimate, and validation evidence. Then pick three design decisions and trace them backward to a requirement. Identify any orphan requirement or ungrounded design element.

## 7. Quantitative problems (attempt before the answer key)

All inputs and prices below are illustrative. Use decimal units and retain units through every step. These are prompts only; worked solutions are in Section 8.5. Real systems require measured workload and implementation-specific validation.

### Q1 — Daily and retained volume

**Prompt.** A pipeline receives 3,000,000 records/day, averaging 1,200 bytes/record. Estimate raw daily volume in GB and raw retained volume for 45 days. Assume no compression, one copy, and no overhead.

### Q2 — Average and peak write rate

**Prompt.** A service receives 8,640,000 writes/day. Use 86,400 seconds/day and an illustrative peak factor of 7. Calculate average writes/s and estimated peak writes/s.

### Q3 — Compression and file count

**Prompt.** Raw daily data is 480 GB. Measured compression ratio is 4:1, defined as raw bytes divided by compressed bytes. Target file size is 256 MB, where 1 GB = 1,000 MB. Estimate compressed volume and file count.

### Q4 — Scan time after pruning

**Prompt.** An illustrative table is 8 TB (decimal). A predicate prunes 87.5% of bytes. Assume effective scan throughput of 400 MB/s (decimal) and ignore startup, compute, network, decompression, and concurrency overhead. Estimate remaining bytes and idealized scan time.

### Q5 — Storage, index, and replica overhead

**Prompt.** A primary data set is 12 TB. Indexes add 18% of primary size, and one full replica stores the data plus its own indexes at the same ratio. Ignore backups and other metadata. Calculate total logical stored volume.

### Q6 — Retained volume with copies and overhead

**Prompt.** A dataset generates 25 GB/day and is retained for 90 days. Assume two full copies and additional overhead equal to 15% of the copied data volume. Estimate stored volume.

### Q7 — Replication lag exposure (an RPO planning proxy, not a guarantee)

**Prompt.** A producer commits 2,400 records/s. A replica is observed to lag by 12 seconds. Estimate the number of records corresponding to that lag window. Explain what this estimate does and does not establish.

### Q8 — Monthly storage cost across tiers

**Prompt.** Illustrative monthly storage prices are: active tier $24/TB-month, warm tier $10/TB-month, archive tier $3/TB-month. Volumes are 40 TB active, 80 TB warm, and 200 TB archive. Calculate monthly storage-only cost.

### Q9 — Archive break-even with retrieval and operating cost

**Prompt.** A 100 TB dataset costs $20/TB-month in the active tier and $4/TB-month in archive. Archive incurs an illustrative $0.08/GB of retrieval for data retrieved, plus $120/month in archive-specific request/operations costs. Ignore transition fees for this first calculation. Calculate monthly storage savings, then the retrieval volume at which savings are exactly offset. Use 1 TB = 1,000 GB.

### Q10 — Mixed retrieval scenario comparison

**Prompt.** A 60 TB dataset would save $12/TB-month by moving from warm to archive. Archive also has $90/month in request/operational overhead, and retrieval costs $0.05/GB. Compare low/base/high monthly retrieval assumptions of 500 GB, 5,000 GB, and 15,000 GB. Ignore transition fees for this exercise; state their effect qualitatively.

## 8. Answer key and marking rubric

**Use this section only after a closed-book attempt.** Model answers are concise anchors, not the only acceptable responses. Where the question is open-ended, award credit for a different design if it fits the stated workload and exposes assumptions and trade-offs.

### 8.1 Beginner answer key

**T1-B1 —** OLTP handles many small concurrent transactions, point reads/writes, and integrity-sensitive changes; typical concerns are latency, concurrency, and transaction correctness. OLAP scans and aggregates larger historical sets; it favors scan/aggregation efficiency but is not usually the best place for high-rate single-row transactional updates.

**T1-B2 —** OLTP. The critical concerns are transaction integrity, concurrency control, and keeping inventory/order invariants correct under simultaneous requests.

**T1-B3 —** OLAP. It scans and aggregates broad historical ranges, with a different read shape and resource profile from point transactions.

**T2-B1 —** Relational: structured relations, joins, constraints, and transactions; key-value: lookup by key; document: aggregate/document retrieval; graph: traversals across relationships; time-series: timestamped measurements and time-window access; search index: text retrieval/ranking and filtering. The correct category depends on workload, not label alone.

**T2-B2 —** The access pattern is point lookup by stable ID plus small updates. Relational and key-value/document categories may be plausible; decide based on constraints, query needs, transaction scope, growth, consistency, and operational constraints. Missing facts could include multi-entity transactions, query variability, write rate, or integrity requirements.

**T2-B3 —** It overgeneralizes: “NoSQL” includes different models; performance depends on access pattern and data model; relational systems can scale and optimize many workloads; distributed systems may trade consistency or operational simplicity; schema flexibility does not remove data-quality or contract obligations. Require workload evidence and a comparison.

**T3-B1 —** Object storage stores objects/files with metadata and object-level operations. It scales for durable file storage but usually lacks native low-latency arbitrary row updates and database-style multi-row transactions. Applications often write new objects or replace objects rather than mutate a row in place.

**T3-B2 —** CSV is human-readable and interoperable for simple exchange but often verbose, weakly typed, and expensive to parse for column-selective scans. Columnar formats store values by column and can improve compression/projection for analytics, but may require compatible readers and more deliberate schema/metadata handling.

**T3-B3 —** `2,000,000 records/day × 500 bytes/record = 1,000,000,000 bytes/day = 1.0 GB/day`. Assumes 500 bytes is the average serialized record size before compression and excludes file/metadata overhead.

**T4-B1 —** Object storage is the underlying object/file store; a table format adds table metadata, schema/partition metadata, and snapshot/commit semantics over files; a data platform combines components and operating/governance capabilities. Confusing layers hides who supplies transactions, catalog, query execution, access controls, recovery, and deletion behavior.

**T4-B2 —** A warehouse can suit governed, modeled reporting with controlled schemas and performance management; trade-offs may include rigidity or cost for varied raw data. A lakehouse can combine open file storage with table-management features for varied analytical data; trade-offs include metadata, maintenance, and operational complexity.

**T4-B3 —** Snapshots can preserve prior table states and support rollback/time travel, but depend on the table's storage, metadata, retention, and cleanup rules. They are not automatically independent disaster recovery, and retained snapshots can preserve data that deletion policy expects to remove.

**T5-B1 —** Partitioning divides data into separately addressable groups, often to prune broad ranges; indexing adds access structures for selected lookups/filters; clustering/sorting organizes rows or files by common query columns. Benefit depends on query shape, selectivity, cardinality, write pattern, and implementation.

**T5-B2 —** Collect query frequencies, date-range selectivity, customer cardinality/skew, table growth, partition/file sizes, update behavior, concurrency, latency targets, and representative plans/measurements. A plausible design must explain date pruning and customer-history access rather than choosing from column names alone.

**T5-B3 —** Causes include excessive partition granularity, small writes, over-parallelized writers, or many tiny files creating metadata/open overhead. Measure file-size distribution, file count, bytes scanned, pruning effectiveness, query latency, metadata planning time, and compaction cost.

**T6-B1 —** Replication maintains copies; backup preserves recoverable states; lag is delay between source changes and replica application; consistency describes which states reads may observe; atomicity means a transaction commits all its included changes or none. Replication can copy corruption or accidental deletion and does not by itself provide historical recovery.

**T6-B2 —** A stale read caused by replica lag. Possible controls include read-after-write routing to the primary, session/causal consistency if actually provided, waiting for a verified replication position, or a business-specific freshness guard. State the actual guarantee and cost.

**T6-B3 —** The database commit and event publish are separate operations. A crash between them can leave a row without an event; publishing first can create an event for a transaction that later fails; retries can duplicate events. A transactional outbox or another durable handoff can reduce the gap.

**T7-B1 —** Data is created, used actively, used infrequently, archived for rare retrieval, and eventually deleted under policy. A legal hold suspends normal deletion for scoped data until an authorized release; it should be checked before destructive lifecycle actions.

**T7-B2 —** Backup supports recovery after loss/corruption; archive supports long-term preservation, retrieval, and often evidence/discovery. Backups may have different access, indexing, integrity, immutability, and retention properties, so they do not automatically satisfy archive requirements.

**T7-B3 —** Examples: business purpose (business/data owner); operational support (service owner); legal/regulatory requirement (legal/compliance authority with cited source); contract (contract owner/legal); investigation (authorized investigation owner/legal); privacy-driven maximum retention (privacy/legal authority). Every requirement needs a source, owner, scope, and review date.

### 8.2 Intermediate answer key

**T1-I1 —** Shared resources can let large scans consume I/O, CPU, memory, and cache needed by transactions. A read replica can isolate some reads but introduces lag and still shares replication/operational risks; a separate analytical platform adds movement, cost, and freshness management but can isolate capacity. Choose using measured contention, query latency, transaction SLOs, freshness needs, transfer cost, and failure coupling. Include a no-separation baseline.

**T1-I2 —** Keep the current store as baseline if the report meets its latency target and does not materially affect operational transactions. Measure query duration, resource contention, growth, and user impact. Revisit if reports miss target, transaction latency/error rate degrades, data volume grows materially, or freshness/concurrency requirements change. A fixed threshold must be agreed with owners, not invented as universal.

**T1-I3 —** A read replica may offer a relatively direct copy but has lag/failover coupling; a separately ingested projection may isolate analytical work better but adds pipeline delay, reconciliation, and duplicated storage. Define freshness as a measurable lag distribution/window, identify what the dashboard displays when the target is missed, and keep the operational source authoritative. Validate end-to-end lag, gap recovery, and behavior during source/replica/pipeline outage.

**T2-I1 —** The ledger-like invariants favor a relational candidate as baseline because constraints, multi-row transactions, and account/date queries align with its strengths. Document/key-value options may fit specific access patterns but can complicate multi-entity invariants or query flexibility. Compare at least three feasible candidates, eliminate those that cannot meet correctness/transaction needs, record trade-offs, and test representative concurrency, constraints, latency, and recovery.

**T2-I2 —** A search index is purpose-fit for ranking and text retrieval; a relational database may be simpler but could impose expensive text queries or compete with transactions. Treat the index as a derived/search projection unless it is explicitly the authoritative store. Define index lag, rebuild/reconciliation, access control, deletion propagation, and fallback behavior.

**T2-I3 —** Compare graph traversals over real query shapes and data sizes against relational joins, including latency, update frequency, relationship depth, consistency requirements, and operational skill/cost. Keep the relational candidate where constraints and ordinary transactions dominate. Introduce a graph store only if representative traversals show a material benefit that outweighs synchronization, duplicate state, and operational burden; define how derived graph state is reconciled.

**T3-I1 —** A columnar format may read only required columns and compress analytical data more efficiently; CSV requires parsing text and commonly reads full rows. Compare measured bytes scanned, compressed size, CPU/decode cost, query time, schema evolution, null/type fidelity, interoperability, writer/reader support, and conversion cost on representative data. No format is always best.

**T3-I2 —** `1.2 GB × 1,000 MB/GB ÷ 200 MB/file = 6 files/partition` as a planning estimate. Real output can vary due to partitioning, row groups, parallel writers, compression variability, and file-size targets. Confirm actual file-size distribution and small-file overhead.

**T3-I3 —** Prefix design should reflect common filters, lifecycle boundaries, and access-control needs rather than every possible field. High-cardinality prefixes can create many tiny groups, excessive metadata/listing, uneven writes, and brittle query conventions. Use query logs and retention/access requirements to shortlist low/moderate-cardinality partition keys, then measure pruning, file sizes, request counts, and maintenance cost.

**T4-I1 —** Warehouse-only may simplify governed finance reporting but can be less flexible for varied raw data; unmanaged object files are flexible and cheap but require more work for schema, commits, metadata, and concurrent writes; lakehouse-style management can bridge these needs but adds table maintenance and metadata operations. Conditional recommendation: preserve governed reporting in the warehouse or curated layer and assess managed tables for event exploration if concurrency, schema, governance, and operations justify them. Quantify movement, duplicate storage, people, compute, and erasure effects.

**T4-I2 —** Adding a nullable field can be a compatible syntactic schema evolution if consumers tolerate it. Changing the meaning of an existing field is a semantic contract break even if the schema is unchanged. Use versioned contracts, semantic definitions, compatibility checks, lineage, migration/backfill plans, and consumer validation; a table format alone cannot fix meaning changes.

**T4-I3 —** Plain files alone do not necessarily provide a coordinated committed table view for concurrent writers/readers. A table format may supply documented commit/snapshot semantics, but verify the actual implementation and catalog/query integration. Test concurrent writes, interrupted commits, reader visibility, recovery, schema changes, and cleanup. Check whether old snapshots retain data that deletion policy requires to remove.

**T5-I1 —** Day partitions align with last-seven-day scans and can prune most historical data, but may leave large customer-history queries scanning many partitions. Customer partitions can help customer lookups but can be highly skewed and make date scans expensive. Compare date partitioning plus customer clustering/indexing, composite layout where supported, or separate workload-optimized projections. Test representative query mix, file/partition sizes, skew, writes, and maintenance costs.

**T5-I2 —** Measure query frequency and latency improvement, index size, write amplification/latency, maintenance/rebuild cost, buffer/cache effects, and overall workload impact. High cardinality may improve selectivity in some designs but does not guarantee the optimizer will use the index or that index access beats scanning; predicate distribution, table size, correlation, and query shape matter.

**T5-I3 —** Ten-minute partitions can create a large number of partitions over long retention, while 2 MB files suggest small-file overhead; neither figure alone determines the correct layout. Measure query date ranges, pruning, file/open/metadata overhead, ingest cadence, skew, compaction cost, and update behavior. Compare coarser time partitions plus clustering or compaction using representative queries and peak ingestion tests.

**T6-I1 —** (a) Read-after-write may require primary routing or a documented consistency guarantee; (b) analytical replica reporting requires an explicit freshness/lag budget and observable lag; (c) recovery requires tested backup/replication recovery behavior and agreed recovery point objective (RPO) and recovery time objective (RTO). Do not infer guarantees from topology names; document actual system semantics, failure-domain assumptions, and test evidence.

**T6-I2 —** Write the business row and outbox record in one local transaction; a separate publisher reads durable outbox entries and publishes them, then marks delivery state. This prevents a committed row from having no durable publication intent, assuming the local transaction is atomic. Duplicates remain possible if publish succeeds but acknowledgement/state update fails; use stable event IDs and idempotent consumers. Ordering, lag, retries, poison messages, and reconciliation still need policies and monitoring. Do not claim end-to-end exactly-once without a narrowly defined and demonstrated guarantee.

**T6-I3 —** The two row updates may be atomic if they are in one database transaction supported by the database and isolation level. The remote call is outside that local transaction unless a specifically supported distributed transaction protocol and its operational guarantees are established. Prefer durable intent/outbox, idempotent remote operation, bounded retries, timeout handling, reconciliation, and compensation where business-valid; define what users see in each partial state.

**T7-I1 —** A good row identifies the ticket class, purpose, start event, minimum/maximum duration (or unresolved), cited source, accountable owner, hold behavior, tier/transition trigger, deletion scope, and verification evidence. If values are invented, label them illustrative and require business/legal/privacy confirmation before automation. Backups and derived copies need explicit handling.

**T7-I2 —** Estimate data volume and retrieval distribution, retrieval frequency, latency/restore windows, request counts, transition charges, minimum-duration or early-deletion charges if applicable, operations and support effort, and the active-vs-cold cost delta. Model low/base/high scenarios and break-even; confirm tier semantics from the selected provider before implementation.

**T7-I3 —** Do not equate reaching a policy date with verified deletion. Check source policy and owner, identify hold scope/status, block destructive automation for held data, and follow the approved backup/immutable-copy treatment. Track statuses such as requested, approved, held, deletion-in-progress, deleted-from-active-copies, awaiting governed backup expiry, exception approved, and verified complete. Declare completion only when the defined scope is checked and evidence is retained; unresolved conflicts go to legal/privacy authority.

### 8.3 Advanced answer key

**T1-A1 —** Shared store minimizes movement and operational components but risks contention and may not meet analytical scan latency. A read replica can offload reads but creates replication lag, capacity and failover coupling. A separate analytical platform isolates compute and supports scan-oriented formats but adds ingestion, duplicated storage, freshness management, governance, and failure paths. Compare query/transaction latency distributions, CPU/I/O contention, freshness tolerance, data movement volume, replication lag, cost including people, and failure recovery. Test the representative workload and a failure case before deciding.

**T1-A2 —** Nightly copying is not necessarily fresh; batch failure or late data creates gaps; analytical queries may still affect the source during extraction; copied data can be inconsistent across tables without a coherent cut; deletion and schema changes may not propagate; a warehouse may still contend with its own workloads; “never” is an unsupported absolute. Validate freshness, extraction impact, snapshot consistency, retries/reconciliation, schema compatibility, deletion propagation, and outage behavior.

**T2-A1 —** A single relational baseline may preserve atomic counter invariants but must be load-tested for throughput/hot rows. Distributed key-value may scale key access but must demonstrate atomic increment, acknowledged-write durability, partition/failover behavior, and per-key ordering. Partitioning by tenant alone may concentrate the hot tenant; finer subkeys/sharding can distribute writes but complicates exact aggregation and invariants. Test burst rate, hot-key concentration, concurrent increments, failover, replica lag, and reconciliation. Reject any candidate that cannot meet the stated no-lost-acknowledged-increment requirement under agreed failures.

**T2-A2 —** Characterize reads/writes, entity boundaries, query variability, transaction scope, growth ranges, latency, consistency, and team operating skills. Compare a relational baseline with document/distributed alternatives. Fix criteria before scoring, run representative tests, and document trade-offs. Revisit if measured growth, transaction needs, query shapes, or operational capacity changes. Flexible schema alone is not sufficient evidence.

**T3-A1 —** Compressed volume: `480 GB/day ÷ 4 = 120 GB/day`. In decimal MB: `120 × 1,000 = 120,000 MB/day`. File count estimate: `120,000 MB ÷ 256 MB/file = 468.75`, approximately 469 files/day. Actual count differs due to partitioning, writer parallelism, data skew, compression variance, and target-file behavior. Monitor file-size histogram, file count per partition, metadata planning time, compaction work, and query latency.

**T3-A2 —** “Always faster” ignores workload shape, parser/reader support, schema/type conversion, null semantics, compatibility, row-level access needs, small files, conversion compute, storage duplication during migration, and rollback. Benchmark representative queries and downstream consumers, compare bytes scanned/CPU/latency/cost, validate row counts and aggregates, preserve source until acceptance, and define a reversible cutover and failure threshold.

**T4-A1 —** Snapshots may retain older versions containing the subject's data. Requirements must specify the applicable data scope, maximum retention, snapshot cleanup, derived data, replicas, exports, backups, and any legal hold or retention obligation. Confirm conflicts with legal/privacy authority. Use a deletion workflow with scope inventory, hold check, approved execution, asynchronous cleanup where needed, verification queries/manifests, exception records, and a completion status that distinguishes deleted, pending expiry, held, and legally retained. Validate restoration/rebuild paths too.

**T4-A2 —** Object storage holds objects; table format governs table metadata, commits/snapshots/schema/partition semantics; catalog provides discoverability/metadata; query engine executes reads; platform supplies orchestration, governance, access, monitoring, and operations. Backup, recovery, access control, and deletion guarantees must be assigned and tested for each layer. A marketing label is not evidence of an end-to-end guarantee.

**T5-A1 —** Mean load is `1,000,000 events/hour ÷ 100 tenants = 10,000 events/hour per tenant`. The hot tenant receives `1,000,000 × 0.45 = 450,000 events/hour`; therefore `skew_ratio = max_partition_load ÷ mean_partition_load = 450,000 ÷ 10,000 = 45`. Under the stated even-distribution assumption, each other tenant receives `550,000 ÷ 99 ≈ 5,555.6 events/hour`; the hot tenant is about `81×` one other tenant. These are illustrative workload calculations, not measured capacity. Measure records/bytes by tenant and time, per-partition throughput/latency, file sizes, query filters, and compaction cost. Alternatives include partitioning by time and clustering by tenant, subpartitioning the hot tenant by time or another bounded dimension, or salting keys when queries can tolerate/aggregate across salts. A change may improve write balance but increase query fan-out and metadata. Benchmark the real query mix, peak writes, skew, and maintenance; validate correctness when aggregating salted keys.

**T5-A2 —** Remaining fraction is `1 − 0.875 = 0.125`. Bytes scanned: `8 TB × 0.125 = 1 TB = 1,000,000 MB`. Idealized time: `1,000,000 MB ÷ 400 MB/s = 2,500 s = 41.7 minutes`. Actual elapsed time depends on parallelism, CPU, decode, network, caching, file/partition metadata, concurrency, and whether 400 MB/s is aggregate or per worker. Validate with query plans and repeated measurements.

**T6-A1 —** At 18 seconds of observed lag and a stable write rate `r` records/s, the approximate records represented by the lag window would be `18 × r`; the rate is not supplied, so no record count can be calculated. Asynchronous failover can omit acknowledged writes not yet applied to the promoted replica, but the actual loss depends on acknowledged-write semantics, replication position, failover selection, and whether the original primary can be reconciled. An observed 18-second maximum is not a guaranteed worst-case. Define RPO/RTO, capture replication positions, test primary loss during peak writes, and verify acknowledged-write recovery.

**T6-A2 —** Use a local transaction to write both business state and outbox event; publish from the outbox with retry and stable event ID; consumers persist processed IDs or otherwise make effects idempotent; define ordering by aggregate/key where needed; use retry/backoff and dead-letter/quarantine handling; reconcile source state against published/consumed state. The local database provides atomicity only for the local row and outbox if configured accordingly. Messaging may provide delivery semantics within its documented boundary, but duplicates and cross-system partial completion still require application design. Measure oldest outbox age, publish failures, duplicate rate, consumer lag, reconciliation mismatches, and recovery results.

**T7-A1 —** Record the minimum claim and its source/owner; record the field-level maximum and its source/owner; record the hold's scope, issuing authority, start, release condition, and audit trail. Do not automate deletion or indefinite retention while constraints conflict. Pause the affected rule or quarantine the affected class under a documented exception, prevent hold-scoped records from destructive actions, and escalate to legal/privacy authority for an authoritative interpretation. Separate field-level deletion from record-level preservation where legally and technically valid, but do not assume it is valid without confirmation. Record decision, rationale, approver, expiry/review date, and implementation evidence.

**T7-A2 —** The prompt gives 500 TB but no storage-price delta or retrieval price, so a numeric break-even cannot be calculated without additional inputs. Start with `monthly_storage_savings = 500 TB × (active_price − archive_price)` using compatible TB-month units. Then subtract fixed request/operations charges and transition/restore costs; retrieval break-even volume is the remaining savings divided by the retrieval price per GB (convert TB to GB consistently). Estimate low/base/high retrieval distributions, request counts, latency/restore windows, minimum-duration rules, and service limits. State which inputs are missing, obtain them from provider pricing and measured telemetry, and revisit if actual retrieval exceeds the modeled threshold.

### 8.4 Industry-application model-answer guidance

**T1-IA1 —** Ask for transaction/read/write rates and peaks, query shapes, data volume/growth, concurrency, freshness, latency/availability targets, and current contention. Keep the shared baseline if measured report and transaction targets are met; compare a read replica and separate analytical platform if scans harm transactions or freshness requirements cannot be met. Validate with representative query/load tests, transaction latency distributions, resource use, data freshness, and operating cost.

**T2-IA1 —** A relational category is a reasonable primary candidate for structured claim state and integrity-sensitive transitions; attachments metadata may remain relational or use a document-oriented projection depending on access pattern, while relationship exploration may justify a graph projection only if real multi-hop queries warrant it. Compare at least three candidates and define source-of-truth rules, consistency/lag, rebuild/reconciliation, access controls, and deletion propagation. Validate claim invariants under concurrency and representative relationship queries.

**T3-IA1 —** A human-friendly exchange may remain CSV where simplicity/interoperability dominate; the column-selective analytics consumer may benefit from a typed columnar format; archival choice must prioritize durable readability, schema/metadata preservation, and tested future decoding rather than assuming the cheapest format remains usable. One canonical representation plus controlled derived exports can reduce ambiguity but adds conversion cost. Test row counts, schema/types, nulls, aggregates, file sizes, read compatibility, and restore/read procedures.

**T4-IA1 —** A warehouse may remain the governed finance serving layer; evolving events may be held in object storage with a table format if managed commits/schema evolution and shared analytical access justify the complexity. A hybrid is acceptable only if ownership, data movement, catalog, query execution, access controls, snapshots, backup, and deletion are assigned explicitly. Include maintenance and erasure costs; revisit if workload scale, governance, or team capacity changes.

**T5-IA1 —** A defensible baseline may partition by date for range aggregation, cluster/sort by customer for history queries, and use a suitable index or key access path for event ID where the chosen store supports it. State this as a hypothesis, not a universal layout. Benchmark all three query shapes plus peak writes, skew, file counts, pruning, latency percentiles, index/storage overhead, compaction cost, and workload interference. Reject or revise if gains do not offset write and maintenance costs.

**T6-IA1 —** Reconstruct the timeline from database commit through event publication, broker acknowledgement, consumer processing, and downstream commit. A local outbox can atomically persist the business row and publication intent; stable event IDs and idempotent consumer effects reduce duplicate harm; ordering policy and reconciliation address gaps/late events. Verify local transaction semantics and messaging guarantees from their actual documented boundary; retain evidence of outbox age, publish/consume offsets or IDs, duplicate handling, and source-to-downstream reconciliation.

**T7-IA1 —** Do not run destructive deletion until the hold scope is checked and the conflicting minimum/maximum requirements are resolved by the authorized legal/privacy owners. Record source, owner, unresolved interpretation, affected fields/records, hold status, review deadline, and exception approval. Automation should quarantine/pause only the affected scope, preserve held records, and avoid retaining unrelated fields indefinitely where an approved field-level policy applies. Verify each copy and record pending immutable-backup expiry separately from completed deletion.

**IA-1 — Northbridge Bank.** A strong answer begins with business capabilities and workload profiles, not product names. It keeps an operational baseline for correctness-sensitive account/order transactions, evaluates analytical separation based on measured contention and freshness, and uses a warehouse/lakehouse pattern only where query shapes and governance justify it. It distinguishes object storage, table format, catalog/query/platform responsibilities; maps layout choices to query patterns; states replica-read rules and local/cross-system transaction boundaries; uses an outbox/idempotency/reconciliation pattern where an event crosses systems; and supplies retention classes with source, owner, hold, tier, deletion scope, and verification evidence. Cost estimates include storage, replicas/indexes/snapshots, movement, retrieval, compute, and operating effort. It lists rejected alternatives, testable pass/fail criteria, and revisit triggers. Any legal period must be confirmed by a named authority and source.

**IA-2 — Separation decision.** A shared store is defensible if the small report meets its target without material contention and its cost/operating simplicity beats a separate pipeline. Evidence: transaction latency, report duration, resource use, growth, concurrency, and user impact. Revisit if measured SLOs fail, workload scale changes, or freshness and concurrency demands change.

**IA-3 — Mixed workload.** Candidate A: shared store with resource/query controls and measured contention. Candidate B: read replica or separate analytical projection/platform with explicit freshness budget and reconciliation. Compare read/write isolation, replication lag, data movement, schema changes, cost, and failure modes. The decision must name what dashboard freshness means and what happens when the budget is exceeded.

**IA-4 — Skew plus layout.** Customer partitioning mismatches date-heavy queries and creates one hot partition. Test date partitions with customer clustering, time-subdivision for the hot customer, or another composite layout. Compare bytes scanned, per-partition skew, small-file count, write throughput, query fan-out, maintenance, and correctness. Do not choose a redesign without representative benchmarks.

**IA-5 — Cross-system correctness.** Crash before publish can lose an event without durable handoff; publish-before-ack can cause duplicate publication; out-of-order delivery can corrupt state if consumers assume order; consumer outage grows lag. An outbox, stable event ID, idempotent consumer, per-key ordering policy, retry/quarantine policy, and reconciliation reduce risk. State local transaction guarantees separately from message-system guarantees and application assumptions.

**IA-6 — Lifecycle, snapshot, erasure.** Inventory all copies and transformations. Before deleting, check hold scope and policy conflict; a hold blocks deletion for its covered scope until authorized release. If policy conflicts remain unresolved, route to legal/privacy and prevent automation from making an irreversible choice. Plan snapshot expiration/rewriting, replica and derived-store cleanup, export/downstream notification, backup expiry or approved treatment, and evidence. Report statuses honestly; immutable backups may require controlled expiry rather than immediate mutation.

**IA-7 — Archive economics.** Compute storage savings, then subtract retrieval, request, transition, restore, compute, and operations costs in low/base/high cases. Include restore latency and user-impact cost if relevant. Break-even occurs when incremental retrieval and operating costs consume the storage savings. State source and uncertainty for each input and revisit based on actual retrieval telemetry.

**IA-8 — Flawed design.** Defects include: one database category cannot be assumed to fit all access patterns; no workload characterization; no baseline/candidate comparison; nightly copy freshness is undefined; no extraction/transaction isolation analysis; “partition by every column” can create high cardinality, tiny partitions, and overhead; skew is ignored; snapshots forever create unbounded cost and may conflict with erasure; primary-only deletion misses replicas, snapshots, backups, exports, derived stores, and consumers; no hold check; no transaction boundary/outbox/idempotency/reconciliation; no format/table-format/platform distinction; no validation or failure tests; no owner/source for retention; no operational-cost model. For each, require workload evidence, cost calculation, policy owner, or a representative test.

**IA-9 — ADR.** Strong answers record context, workload/access patterns, measurable targets, constraints, baseline and alternatives, criteria fixed before scoring, assumptions, costs/ranges, risks, guarantees, validation, and revisit triggers. Conditionality is appropriate because unknown growth or operating skills can reverse the decision; unknowns should be logged rather than hidden in a false point estimate.

**IA-10 — Traceability.** Every requirement should map to a workload and then to category/layout/consistency/lifecycle/cost/validation. Every design element should trace backward to a requirement or be explicitly identified as an enabling constraint. Any orphan is either removed, justified, or logged as an assumption requiring approval.

### 8.5 Quantitative worked solutions (Q1–Q10)

### Q1 — Daily and retained volume

**Worked solution.**

- Formula: `daily_volume = records_per_day × average_record_size`.
- Substitution: `3,000,000 records/day × 1,200 bytes/record = 3,600,000,000 bytes/day`.
- Conversion: `3,600,000,000 bytes/day ÷ 10^9 bytes/GB = 3.6 GB/day`.
- Retained volume: `3.6 GB/day × 45 days = 162 GB`.
- **Interpretation:** the baseline is 3.6 GB/day and 162 GB retained before compression, replicas, indexes, snapshots, metadata, or other overhead. It is not a full capacity estimate.

### Q2 — Average and peak write rate

**Worked solution.**

- Average rate: `8,640,000 writes/day ÷ 86,400 s/day = 100 writes/s`.
- Peak estimate: `100 writes/s × 7 = 700 writes/s`.
- **Interpretation:** 100 writes/s is a day-average; 700 writes/s is a planning estimate derived from an assumed peak factor, not a measured peak or capacity guarantee. Validate with time-series load data.

### Q3 — Compression and file count

**Worked solution.**

- Compressed volume: `480 GB ÷ 4 = 120 GB`.
- Convert: `120 GB × 1,000 MB/GB = 120,000 MB`.
- Estimated file count: `120,000 MB ÷ 256 MB/file = 468.75 files`.
- Planning interpretation: approximately 469 files/day on average; actual output is an integer and may be affected by partition boundaries, record sizes, writer parallelism, compression variance, and minimum/maximum file-size behavior.

### Q4 — Scan time after pruning

**Worked solution.**

- Remaining fraction: `100% − 87.5% = 12.5% = 0.125`.
- Remaining bytes: `8 TB × 0.125 = 1 TB = 1,000,000 MB`.
- Idealized time: `1,000,000 MB ÷ 400 MB/s = 2,500 s`.
- Convert to minutes: `2,500 s ÷ 60 s/min = 41.666… min`, approximately **41.7 minutes**.
- **Interpretation:** this is a simplified throughput bound, not a query-latency prediction. Parallelism, caching, metadata, file sizes, CPU, data decoding, and shared resources can change elapsed time.

### Q5 — Storage, index, and replica overhead

**Worked solution.**

- Primary including indexes: `12 TB × (1 + 0.18) = 14.16 TB`.
- Replica including indexes: `12 TB × (1 + 0.18) = 14.16 TB`.
- Total: `14.16 TB + 14.16 TB = 28.32 TB`.
- Equivalent formula: `12 TB × (1 + 0.18) × 2 = 28.32 TB`.
- **Interpretation:** replication plus index overhead yields 2.36× the base data volume under these assumptions. Actual physical capacity may differ due to compression, shared storage, replication format, index differences, and backups.

### Q6 — Retained volume with copies and overhead

**Worked solution.**

- Single-copy retained volume: `25 GB/day × 90 days = 2,250 GB`.
- Two copies: `2,250 GB × 2 = 4,500 GB`.
- Add overhead: `4,500 GB × (1 + 0.15) = 5,175 GB`.
- Convert: `5,175 GB ÷ 1,000 GB/TB = 5.175 TB`.
- **Interpretation:** estimated 5.175 TB, with copies and overhead defined as above. If “15% overhead” were instead intended as a percentage of one copy, the answer would differ; always define the base.

### Q7 — Replication lag exposure (an RPO planning proxy, not a guarantee)

**Worked solution.**

- Estimate: `2,400 records/s × 12 s = 28,800 records`.
- Units cancel correctly: records/s × seconds = records.
- **Interpretation:** approximately 28,800 records may fall within the time window represented by the observed lag if the rate is stable. This is an exposure estimate, not proof that all those records would be lost. Lag may be measured by time or position, rates vary, and observed lag is not necessarily a worst-case guarantee. Establish RPO through defined requirements, replication semantics, acknowledged-write behavior, and failure tests.

### Q8 — Monthly storage cost across tiers

**Worked solution.**

- Active: `40 TB × $24/TB-month = $960/month`.
- Warm: `80 TB × $10/TB-month = $800/month`.
- Archive: `200 TB × $3/TB-month = $600/month`.
- Total: `$960 + $800 + $600 = $2,360/month`.
- **Interpretation:** $2,360/month is storage-only. It excludes retrieval, requests, transitions, restores, compute, network, support, monitoring, and human operations. These prices are illustrative, not market quotes.

### Q9 — Archive break-even with retrieval and operating cost

**Worked solution.**

- Active storage: `100 TB × $20/TB-month = $2,000/month`.
- Archive storage: `100 TB × $4/TB-month = $400/month`.
- Storage savings: `$2,000 − $400 = $1,600/month`.
- Savings after fixed archive-specific cost: `$1,600 − $120 = $1,480/month` available for retrieval charges.
- Break-even retrieval volume: `$1,480/month ÷ $0.08/GB = 18,500 GB/month = 18.5 TB/month`.
- **Interpretation:** under these assumptions, retrieval charges alone consume the remaining storage savings at 18.5 TB/month. Transition fees, minimum storage duration, restore time, requests, and labor would lower the practical break-even point; storage price alone is not enough.

### Q10 — Mixed retrieval scenario comparison

**Worked solution.**

- Storage savings: `60 TB × $12/TB-month = $720/month`.
- Low retrieval: `500 GB × $0.05/GB = $25`; net estimated savings = `$720 − $90 − $25 = $605/month`.
- Base retrieval: `5,000 GB × $0.05/GB = $250`; net estimated savings = `$720 − $90 − $250 = $380/month`.
- High retrieval: `15,000 GB × $0.05/GB = $750`; net estimated savings = `$720 − $90 − $750 = −$120/month` (a net additional cost).
- **Interpretation:** archive is favorable in the low and base scenarios under the stated assumptions, but not in the high scenario. Transition charges, restore time, request counts, service constraints, and operational effort can make archive less favorable; estimate these before a real decision.

### 8.6 Rubric: Correct / Partly correct / Wrong

| Rating | Definition | Feedback guidance |
|---|---|---|
| **Correct** | Concept is accurate; choice fits the stated workload; assumptions and units are explicit; calculations are reproducible; trade-offs, rejected alternatives, and validation/revisit conditions are defensible. | State the strongest evidence-backed reasoning and identify one next sensitivity or failure test that would strengthen it further. |
| **Partly correct** | Core direction is plausible but one or more important assumptions, units, costs, failure modes, trade-offs, guarantees, or validation steps are missing or weakly justified. | Name the exact missing element and ask for a targeted correction, not a complete rewrite. |
| **Wrong** | Definition or mechanism is materially incorrect, workload fit is unsupported, calculation/unit is wrong, guarantee is asserted without basis, or a material risk/policy conflict is ignored. | Explain the specific misconception and assign a related prerequisite question plus a fresh re-attempt. |

Suggested scoring for each response: conceptual correctness 0–2; workload fit 0–2; explicit assumptions 0–2; quantitative accuracy where applicable 0–2; trade-offs and defensibility 0–2. For non-quantitative questions, reallocate the quantitative points to evidence/validation. **Correct:** 9–10; **Partly correct:** 6–8; **Wrong:** 0–5, with critical safety/correctness omissions able to cap the rating. For beginner classification, use the roadmap target of at least 90% correct before advancing.

## 9. Remediation and re-attempt log template

Copy one row per question attempt. Do not erase the first attempt; preserve it so improvement is observable.

| Question ID | Topic | First attempt (date / rating) | Error type | Correction / evidence needed | Re-attempt date | Re-attempt rating | Status / next action |
|---|---|---|---|---|---|---|---|
| T__-__ | Topic __ | YYYY-MM-DD / Correct–Partly correct–Wrong | Concept / workload / assumption / arithmetic / trade-off / guarantee / lifecycle / evidence | State the corrected reasoning and source/test | YYYY-MM-DD | Correct–Partly correct–Wrong | Open / Ready to retry / Passed / Needs review |

### Error-type guide

- **Concept:** confused categories or mechanisms (for example, backup vs replication).
- **Workload:** chose before characterizing reads, writes, scans, keys, ranges, concurrency, or freshness.
- **Assumption:** omitted peak factor, growth, data copies, price unit, policy source, or system guarantee.
- **Arithmetic/units:** incorrect conversion, formula, base, or unit cancellation.
- **Trade-off:** omitted operational burden, retrieval, latency, maintenance, or rejected alternatives.
- **Guarantee/failure:** treated observed behavior as a guarantee or missed a partial-failure state.
- **Lifecycle/governance:** missed holds, copies, snapshots, derived stores, policy ownership, or verification.
- **Evidence:** recommendation lacks reproducible measurement, test, or traceability.

**Re-attempt protocol:** wait several days where practical; answer from a blank page; compare only after completion; explain the correction in your own words; add one new test or changed assumption that could alter the answer. If the same error repeats, return to the relevant topic prerequisite before retrying.

## 10. Module completion self-assessment

Mark each item **Yes / Not yet / Needs review** and attach evidence. Confidence alone is not evidence.

| Capability | Self-check | Evidence to retain |
|---|---|---|
| 1. Classify OLTP and OLAP workloads and justify separation or no separation | Yes / Not yet / Needs review | Workload profiles, contention/freshness analysis, and a no-separation case |
| 2. Select relational, NoSQL, or specialized categories from access patterns | Yes / Not yet / Needs review | Selection matrix, rejected alternative, and architecture decision record (ADR) |
| 3. Choose object storage organization and file format with quantification | Yes / Not yet / Needs review | Format comparison and reproducible file-size/count arithmetic |
| 4. Distinguish storage, table format, warehouse/lakehouse pattern, and platform | Yes / Not yet / Needs review | Layer distinction and maintenance/erasure implications |
| 5. Design partitioning/indexing/clustering from query patterns | Yes / Not yet / Needs review | Query-to-layout map, skew worksheet, and pass/fail validation plan |
| 6. Derive replication and transaction choices from business correctness | Yes / Not yet / Needs review | Operation-to-guarantee table, lag analysis, and cross-system failure timeline |
| 7. Design retention, archive, tiers, holds, and deletion | Yes / Not yet / Needs review | Schedule with sources/owners, tier break-even, copy inventory, hold workflow, deletion evidence |
| 8. Quantify capacity and cost transparently | Yes / Not yet / Needs review | At least three independently reproducible estimates with units, assumptions, and ranges |
| 9. Make an integrated decision traceable to requirements | Yes / Not yet / Needs review | Requirements → workloads → candidates → layout → guarantees/lifecycle → costs → validation trace |
| 10. Defend trade-offs under challenge | Yes / Not yet / Needs review | Responses to at least two reviewer objections, with evidence and revisit triggers |

### Completion gate

Do not mark the module complete until all of the following are true:

- [ ] All seven topic question groups attempted; wrong answers corrected and re-attempted.
- [ ] Beginner classification reaches at least 90% correct.
- [ ] Every quantitative answer includes formula, units, assumptions, arithmetic, and interpretation.
- [ ] Every selection answer names workload/access patterns, candidates, elimination reasons, trade-offs, validation evidence, and revisit triggers.
- [ ] Every consistency answer distinguishes system guarantees from application assumptions and includes a failure case.
- [ ] Integrated case includes a minimal-change baseline, asset/workload characterization, candidates, logical layout, consistency/transaction boundaries, lifecycle/cost/risk, validation, and revisit triggers.
- [ ] Retention schedule names a source and accountable owner for every requirement; unresolved legal/privacy conflicts are explicitly escalated rather than guessed.
- [ ] At least five failure scenarios have been traced through the design, including lag, zone/primary loss, corruption, and deletion request.
- [ ] Another reviewer can reproduce key calculations and trace three decisions backward to requirements and three requirements forward to decisions.
- [ ] Open questions are logged for the next module rather than hidden in the recommendation.

**Final standard:** a defensible answer is not the one with the most technologies or the longest explanation. It is the one another architect can audit from stated requirements, workload evidence, reproducible estimates, explicit guarantees, lifecycle controls, and a validation plan.
