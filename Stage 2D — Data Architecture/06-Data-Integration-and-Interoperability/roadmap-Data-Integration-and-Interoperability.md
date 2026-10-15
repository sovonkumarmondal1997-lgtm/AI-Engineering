# Roadmap — Module 2D.6: Data Integration and Interoperability

This is the learning roadmap for the sixth module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Modules 2D.1–2D.5 gave you the role, the decision method, the patterns, the
models and the stores. This module connects them. It teaches how data move
between systems **correctly**: which mechanism fits which source and consumer,
what agreement governs the data in transit, what happens when something is
repeated, late, missing or broken, and how you prove that what arrived is what
was sent.

> **Repository note.** The eight topic files, `practice-questions.md`, the
> module and project READMEs, and
> `Projects/06-cross-system-data-integration-design.md` currently exist but are
> empty, as are the Stage 2D overview files. This roadmap is therefore the
> first written statement of the module's scope. It defines the learning
> sequence for each topic file; it does not claim that any topic file already
> contains this material. Where a topic file, once written, covers different
> mechanisms (for example a different set of CDC approaches or compatibility
> modes), the topic file's scope governs and this roadmap should be updated.
>
> **Directory name.** The prompt that requested this roadmap referred to
> `STAGE 2D - DATA ARCHITECURE/`. The actual directory is
> `Stage 2D — Data Architecture/`, and the actual name is preserved.
>
> **Illustrative content.** Every number, system and organisation in this
> roadmap is an **illustrative assumption** used to teach a method. None is a
> real requirement, benchmark or recommended target. The module is
> vendor-neutral: mechanisms are named by category, product names are not
> required, and no connector configuration is taught. It is also **not** a
> general distributed-systems course: failure and delivery concepts are taught
> only as far as integration design needs them.

---

## 1. Module overview

### 1.1 What integration and interoperability mean

**Data integration** is the set of mechanisms and agreements by which data
leave one system and become usable in another, with their meaning intact.
**Interoperability** is the property that independently built systems can
exchange data and *understand* it: agreed structure, agreed meaning, agreed
identifiers, agreed behaviour on change and failure.

### 1.2 Integration is more than moving data

Moving bytes is the easy part. The architecture is in the questions around it:

| Question | Where it is answered |
| --- | --- |
| How do we know what changed? | Batch watermarks, CDC (Topics 1–2) |
| How do we read it from that system? | Interfaces: APIs, files, connectors (Topic 3) |
| What is the unit of exchange and its meaning? | Events, messages, contracts (Topics 4–5) |
| Do we need to copy it at all? | Virtualisation, federation, sharing (Topic 6) |
| What if it arrives twice, late or not at all? | Idempotency, deduplication, reconciliation (Topic 7) |
| Which approach is right, and how does it fail? | Selection and failure handling (Topic 8) |

### 1.3 Producers, consumers, contracts, interfaces, mechanisms

```text
Producer system ──(interface)──> Integration mechanism ──(contract)──> Consumer
      │                                  │                                │
   owns data                    moves/captures/exposes             depends on shape,
   and its change                                                  meaning, timing
```

- A **producer** owns the data and decides how it is exposed.
- A **consumer** depends on structure, meaning, timeliness and completeness.
- An **interface** is how data can be obtained (query, API, file, log, event).
- A **mechanism** is how data are moved or exposed (batch, CDC, stream, virtual
  access, share).
- A **contract** is the explicit agreement on structure, semantics, quality and
  delivery.

Most integration failures are contract failures disguised as pipeline failures.

### 1.4 The mechanisms compared at a glance

| Mechanism | Core idea | Typical freshness | Typical strength | Typical weakness |
| --- | --- | --- | --- | --- |
| Batch full load | Copy everything on a schedule | Hours–days | Simple | Cost grows with size; source load |
| Incremental batch | Copy what changed since a mark | Minutes–hours | Efficient | Needs reliable change marker; misses deletes without care |
| Change data capture | Read the source's change log | Seconds–minutes | Low source load; captures deletes | Operational complexity; ordering and schema issues |
| API integration | Request records through a service | Immediate–minutes | Respects source logic and access control | Rate limits; chatty; not for bulk |
| File integration | Exchange files | Hours–days | Universal; decoupled | Completeness and format risks |
| Managed connector | Packaged extraction | Per product | Fast to adopt | Limited control; opaque failure modes |
| Event streaming | Publish facts as they occur | Seconds | Decoupling; many consumers; replay | Contract discipline; ordering; correctness work |
| Virtualisation / federation | Query in place | Immediate | No copy; one view | Source load; availability coupling |
| Data sharing | Grant governed access to a producer's data product | Per product | No duplication; clear ownership | Needs platform and governance support |

No row is "best". The right choice depends on business requirements,
source-system capability, consumer needs, data semantics and operational
constraints.

### 1.5 How integration choices affect the quality attributes

| Attribute | Integration lever |
| --- | --- |
| Freshness and latency | Mechanism, schedule, buffering |
| Correctness | Identity, ordering, idempotency, reconciliation, contract |
| Throughput | Parallelism, batching, partitioning |
| Reliability | Retries, checkpoints, replay, dead-letter handling |
| Governance | Where data are copied, who may read, lineage |
| Cost | Compute, storage of copies, data transfer, people |
| Source impact | Query load, log reading, rate limits |
| Maintainability | Contract clarity, observability, ownership |

### 1.6 Why correctness mechanisms are essential

Distributed delivery is unreliable by nature: retries duplicate, restarts
replay, networks drop, clocks differ. Therefore:

- **Idempotency** makes repetition harmless.
- **Deduplication** removes copies that arrive anyway.
- **Reconciliation** proves the result matches the source.
- **Failure handling** defines what happens when each component fails.

A transport that delivers messages "reliably" does not by itself make the
business outcome correct. This module teaches the difference between
**transport delivery guarantees** and **end-to-end business correctness**.

### 1.7 How this module builds on earlier ones

| From | Used here |
| --- | --- |
| 2D.1 Topic 4: principles, quality attributes | Criteria for comparing mechanisms |
| 2D.1 Topic 3: ownership | Who owns a contract and a feed |
| 2D.2 Topic 4: freshness, throughput, availability targets | The measurable requirements integration must meet |
| 2D.2 Topic 5: constraints, dependencies, risks | Source limits, vendor dependencies, regulatory limits |
| 2D.2 Topics 6–7: trade-offs, ADRs | Method and record for pattern selection |
| 2D.3 Topic 3: Lambda/Kappa | Replay and reprocessing context |
| 2D.3 Topic 5: data fabric, metadata | Metadata-driven integration |
| 2D.3 Topic 6: event-driven and data-sharing patterns | The pattern-level view this module makes operational |
| 2D.4 Topics 1–3: models, keys | Identifiers and mappings |
| 2D.4 Topic 7: schema evolution | Compatibility foundations |
| 2D.5 Topic 1: OLTP/OLAP separation | Why data move at all |
| 2D.5 Topic 6: replication and consistency | Consistency limits across systems |
| 2D.5 Topics 3–4: formats, table formats | Landing formats and upsert behaviour |

### 1.8 How it supports later modules

| Later module | What it takes from this one |
| --- | --- |
| 2D.7 Enterprise data platform and lakehouse | Ingestion zones, contract enforcement, reconciliation |
| 2D.8 Cloud, hybrid, multi-cloud | Connectivity patterns and managed integration services |
| 2D.9 Streaming and real-time | Event backbone design in depth |
| 2D.10 Governance, security, privacy | Access, lineage and retention in transit |
| 2D.11 Metadata, lineage, quality, master data | Contracts, identifiers, entity resolution |
| 2D.12 Reliability, resilience, disaster recovery | Replay, backfill and recovery foundations |
| 2D.14 Data access, serving, AI data | Feeds for features, retrieval and products |

### 1.9 Expected capabilities after completion

You will be able to:

- Design batch and incremental ingestion with explicit change detection,
  repeatability and recovery.
- Explain CDC and replication behaviour, including snapshots, ordering, lag and
  restart, and state what a given mechanism does **not** guarantee.
- Choose among API, file and managed-connector approaches given source limits.
- Design streaming flows and message contracts with identity, time, ordering
  scope and replay.
- Define data contracts and compatibility policy, separating structural from
  semantic compatibility.
- Judge when to virtualise, federate, share, replicate or materialise.
- Design idempotency, deduplication and reconciliation controls.
- Select integration patterns on explicit requirements and design failure
  handling.
- Deliver a cross-system integration design that a reviewer can audit.

> **Principle for the whole module.** Choose the integration pattern from
> business requirements, source-system capabilities, consumer needs, data
> semantics and operational constraints, never from familiarity, fashion or
> vendor positioning. A recommendation that does not state those inputs is
> incomplete.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

| Prerequisite | Why it matters here |
| --- | --- |
| Module 2D.2 completed (or its gates passed): requirements, freshness/throughput/availability targets, constraints and risks, trade-off method, ADRs | Integration choices are driven by measurable freshness and correctness targets and by source constraints; the decision method records them |
| Module 2D.4 completed (or its gates passed), especially Topics 2, 3 and 7 (keys and relationships, normalisation, schema evolution) | Identity, mapping and compatibility depend on keys and on how schemas change |
| Module 2D.5 completed (or its gates passed), especially Topic 1 (OLTP/OLAP separation), Topic 3 (formats) and Topic 6 (replication, consistency, transaction boundaries) | The reason data move, the landing formats, and the consistency limits across systems |
| Module 2D.3 completed (or its gates passed), especially Topics 3, 5, 6 (processing patterns, metadata, event-driven and sharing patterns) | The pattern-level options that this module operationalises |
| Module 2D.1 completed (or its gates passed): ownership, governance | Contracts and feeds need owners |
| Stage 2–2C data engineering experience: SQL, batch pipelines, an API or file ingest, basic streaming | You need practical experience of how data are extracted and loaded. **Product-specific connector knowledge is not assumed** |

### 2.2 Helpful prior knowledge

- Experience running an ingestion job in production, including a failed run.
- Familiarity with REST-style APIs and with delimited and columnar file formats.
- Basic understanding of message brokers and consumer groups.
- Awareness of database transaction logs (conceptually).

### 2.3 Concepts you will learn during this module

- Watermarks, change markers and lookback windows.
- Log-based change capture and checkpointing.
- Pagination, rate limits and backoff.
- Event identity, partitions and consumer offsets.
- Compatibility modes and contract testing.
- Idempotency keys, upserts and merge semantics.
- Control totals, checksums and reconciliation reports.
- Failure boundaries, timeouts, retry budgets and dead-letter handling.

### 2.4 Using prior knowledge when selecting a pattern

Work in this order every time. It prevents choosing a mechanism first and
inventing reasons afterwards.

1. **Business need:** why must the data move or be accessed (2D.2).
2. **Consumer needs:** freshness, completeness, ordering, history (2D.2 Topic 4).
3. **Source capability:** what interfaces exist, what load they tolerate,
   whether changes are identifiable and deletes visible.
4. **Data semantics:** identity, grain, corrections, deletes, sensitivity
   (2D.4).
5. **Constraints and risks:** residency, vendor limits, windows (2D.2 Topic 5).
6. **Candidates and criteria:** only then compare mechanisms (2D.2 Topic 6).
7. **Failure behaviour and correctness controls:** design before approving.
8. **Record:** ADR with rejected alternatives (2D.2 Topic 7).

---

## 3. Learning strategy and progression

### 3.1 The four levels

| Level | Concepts to study | Recommended order | Practical exercises | Questions to answer | Expected outputs | Evidence of mastery | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1 — Beginner** | Terminology, data movement patterns, basic interfaces, purpose of contracts and reliability mechanisms | Definition → what problem it solves → simple flow → one limitation | Define and classify; draw one flow per mechanism; label producer, consumer, contract | What moves, how, and what could go wrong? | Mechanism cards; labelled flow diagrams | Correct unaided explanation and classification | ≥ 90% of classification items correct; can explain each mechanism to a peer |
| **2 — Intermediate** | Compare approaches; map source and consumer requirements to patterns; design basic flows | Source capabilities → requirements → shortlist → compare → draw flow | Profile five sources; map to mechanisms; design a flow with change detection | How do we detect change? What if we run it twice? | Source profiles; comparison tables; flow designs | A reviewer can recover the requirements from your design | Mechanism-to-source mapping with stated assumptions and units |
| **3 — Advanced** | Consistency, replay, ordering, failure recovery, schema compatibility, duplication, reconciliation, trade-offs | Failure-first analysis → correctness controls → compatibility → cost | Failure-mode matrices; backlog and catch-up arithmetic; compatibility classification | What breaks first? What is guaranteed and what is assumed? What proves correctness? | Failure and recovery analysis; reconciliation design | A defended design that survives challenge | Every failure scenario has detection, recovery and evidence |
| **4 — Industry application** | Cross-system architecture with contracts, flows, failure behaviour, controls, validation | Requirements → flows → contracts → controls → failure walk-through → ADR | The project (Section 7) | Can another architect audit and reproduce this? | Integration design package | Independent review finds no unflagged defect | Project completion gate (Section 7.7) met |

### 3.2 Emphasis

The module rewards **correctness, traceability, resilience and defensible
decisions**. A short design that states how it detects change, tolerates
repetition and proves completeness beats a long catalogue of tools.

### 3.3 The integration-design loop (use for every topic)

```text
State the need → Profile the source and consumer → Choose the mechanism →
Define the contract → Walk the normal flow → Break each component in turn →
Add the correctness controls → Prove completeness → Record and review
```

1. **State the need** and the measurable freshness/correctness target.
2. **Profile source and consumer:** interface, volume, change visibility,
   deletes, limits, expectations.
3. **Choose the mechanism** with criteria and a baseline.
4. **Define the contract:** structure, meaning, identity, delivery.
5. **Walk the normal flow** step by step.
6. **Break each component in turn:** source, network, extractor, broker, loader,
   target, scheduler.
7. **Add controls:** idempotency, deduplication, checkpoints, retries.
8. **Prove completeness:** reconciliation design.
9. **Record and review** as an ADR.

### 3.4 Suggested schedule

About **6 weeks at 6–8 hours per week.**

| Week | Work |
| --- | --- |
| 1 | Topic 1 (batch ETL/ELT, incremental) · Topic 2 (CDC and replication) |
| 2 | Topic 3 (APIs, files, connectors) · Topic 4 (streaming events and message contracts) |
| 3 | Topic 5 (data contracts, schema registry, compatibility) |
| 4 | Topic 6 (virtualisation, federation, sharing) · Topic 7 (idempotency, deduplication, reconciliation) |
| 5 | Topic 8 (pattern selection and failure handling) · practice questions |
| 6 | Project |

Keep a `module-2d6-notes.md` outside the repository's topic files: a mechanism
card per topic, a failure-mode log, worked estimates, and open questions.

### 3.5 Quantitative toolkit used in this module

All values are **illustrative**. Use decimal units (1 GB = 10⁹ bytes).

```text
extract_time        = bytes_to_extract / sustained_extract_throughput
changed_volume      = table_rows × change_fraction × average_row_size
api_calls           = ceil(records / page_size)
api_duration        = api_calls / allowed_request_rate
retry_wait_total    = Σ_{i=0..n-1} ( base_wait × factor^i )     (before jitter)
backlog_growth_rate = arrival_rate − processing_rate
catch_up_time       = backlog / (processing_capacity − arrival_rate)
partitions_needed   = ceil( peak_throughput / per_partition_throughput ) × headroom
replay_retention    = event_rate × event_size × retention_period × replication_factor
chain_availability  = A1 × A2 × … × An      (serial dependencies)
reconciliation_delta = source_control_total − target_control_total
```

Always state units, assumptions and ranges (2D.2 Topic 3).

---

## 4. Detailed learning roadmap for each topic file

Each module below uses the same twelve sub-headings. Levels are cumulative.
Examples use the **illustrative** scenario of *Northbridge Bank*, a fictional
mid-sized bank (Section 7.2).

---

### Module 1 — [Batch ETL/ELT and incremental ingestion](01-batch-etl-elt-and-incremental-ingestion.md)

#### 1.1 Learning objectives

- Describe batch ingestion and its use cases.
- Distinguish ETL from ELT and say where transformation happens and why it
  matters.
- Distinguish full and incremental loads.
- Explain change tracking, change markers and watermarks.
- Describe the extract → land → transform → load flow.
- Reason about scheduling, windows, throughput and freshness.
- Handle late-arriving and updated source data, backfills, retries and
  reprocessing, and source-system impact.

#### 1.2 Why the topic matters in real-world Data Architecture

Batch is the most common integration mechanism and the baseline against which
every alternative is judged. Most "streaming" requirements can be met by
well-designed incremental batch at lower cost; most batch failures come from
unclear change detection and unsafe re-runs.

#### 1.3 Prerequisite knowledge

2D.2 Topic 4 (freshness, windows); 2D.4 Topics 2–3 (keys); 2D.5 Topics 1, 3
(separation, formats).

#### 1.4 Beginner-level learning sequence

1. **Define batch ingestion:** collecting data in groups at scheduled times.
2. **Define ETL and ELT:**

   | Aspect | ETL | ELT |
   | --- | --- | --- |
   | Transformation occurs | Before loading, in a separate engine | After loading, in the target |
   | Raw data retained in target | Often not | Yes (landing area) |
   | Suits | Constrained or sensitive targets; heavy pre-cleaning | Scalable analytical targets; reprocessing needs |
   | Reprocessing | Must re-extract | Can re-transform from landed data |

3. **Define full load and incremental load:** full copies everything each time;
   incremental copies only what is new or changed.
4. **Learn the stages:** extract, land (store as received), transform, load.
5. **Questions to answer:** Why keep a landing copy? What happens to rows
   deleted at the source in an incremental load?
6. **Exercise:** Draw ETL and ELT flows for the same customer-extract and mark
   where each transformation occurs.

**Ability to demonstrate:** explain ETL vs ELT and full vs incremental, and
name a limitation of each.

#### 1.5 Intermediate-level learning sequence

1. **Profile the source:** size, change rate, availability window, primary key,
   presence and reliability of a last-modified timestamp or version, delete
   behaviour, query load tolerance.
2. **Quantify full vs incremental** (illustrative): a table of 200 million rows
   at 500 bytes is 100 GB.

   ```text
   full_extract_time        = 100 GB / 50 MB/s = 100,000 MB / 50 MB/s = 2,000 s ≈ 33 min
   changed_volume (2%)      = 200 M × 0.02 × 500 B = 2 GB
   incremental_extract_time = 2,000 MB / 50 MB/s = 40 s
   ```

   State why the 2% figure is an assumption and what happens if it is 20%.
3. **Design change detection** and the stored **watermark**: the highest
   change-marker value successfully processed, persisted only **after** a
   successful load. State what the marker is (timestamp, sequence, version),
   its precision and its trust level.
4. **Design the target load:** append to a landing area; then upsert into the
   curated table by business key (details of safe re-run in Topic 7).
5. **Scheduling and windows:** start time, expected duration, deadline,
   dependency on upstream completion, contention with source batch windows
   (2D.2 Topic 4).
6. **Freshness arithmetic:**

   ```text
   worst_case_staleness = schedule_interval + run_duration + publication_delay
   ```

   *Illustrative:* hourly run, 10-minute duration, 5-minute publication →
   up to 75 minutes.
7. **Questions to answer:** What would make this run unsafe to repeat? What if
   the watermark column is updated without changing the timestamp?
8. **Exercise:** For three Northbridge sources (customer table with reliable
   timestamp, account table with none, transaction table append-only), design
   the ingestion approach and watermark, or justify why a full load is needed.

**Ability to demonstrate:** a flow whose change detection, watermark handling
and rerun behaviour are explicit.

#### 1.6 Advanced-level learning sequence

1. **Incremental pitfalls:** timestamps that are set at statement time but
   committed later (in-flight transactions are missed); clock skew between
   systems; timestamp updated in batches with identical values; no marker on
   child tables. Mitigations: **lookback window** (re-read a small overlap and
   deduplicate), commit-time markers, version columns, or move to CDC.
2. **Deletes and corrections:** incremental extraction misses hard deletes.
   Options: soft-delete flags, periodic full comparison, tombstone feeds, or CDC
   (Topic 2). State which the source permits.
3. **Late-arriving and updated data:** records that arrive after their business
   date; restatements; design target tables (for example effective-dated rows or
   snapshot partitions) so late data land correctly (2D.4 Topics 4–5).
4. **Backfills:** re-running historical windows without double-loading; separate
   backfill from the normal schedule; throttle to protect the source; verify
   against control totals. Estimate duration with the extract formula.
5. **Retries and partial failure:** a run that loads half a batch; atomic
   publication (stage then swap/commit) so consumers never see a partial load;
   watermark advanced only after success.
6. **Source-system impact:** query cost, locks, replicas as extraction sources,
   off-peak windows, throttling, change-feed alternatives.
7. **Failure modes:** watermark stored before load completes (lost data);
   watermark never advances (reprocessing growth); overlapping runs (duplicate
   or conflicting loads); a rename at the source breaking the extract silently.
8. **Cost and complexity trade-offs:** simplicity of full loads at small scale
   versus incremental complexity at large scale; ELT storage of raw data
   versus ETL's smaller footprint.
9. **Questions to answer:** At what size does a full load stop being
   acceptable, and by what evidence? How do you detect that a delete was
   missed?
10. **Exercise:** Take an hourly incremental job with a timestamp watermark,
    list five ways it can lose or duplicate data, and revise the design with a
    lookback window and a missed-delete check.

**Ability to demonstrate:** explain how the design detects changes, tolerates
repeated execution and recovers from partial failure.

#### 1.7 Industry-application exercises

- Design a batch or incremental ingestion strategy for Northbridge's account and
  customer tables with stated freshness, correctness and recovery requirements.
- Calculate full vs incremental extract time and the staleness bound.
- Write the backfill procedure for a 90-day correction, including throttling.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* The nightly job fails at 85% and is restarted from the beginning
   twice, doubling target rows. What design property was missing?
2. *Scenario:* The source updates a customer's address but the last-modified
   column is not updated. What do you do?
3. *Scenario:* The business wants "near real-time" but the source offers only a
   nightly export. What are the options and what do you tell the sponsor?

#### 1.9 Expected outputs and deliverables

- Source profiles and ETL/ELT choice with reasons.
- Ingestion flow with watermark and rerun behaviour.
- Extract-time and staleness worksheet.
- Backfill procedure.
- Answers to Topic 1 practice questions.

#### 1.10 Common mistakes and misconceptions

- Assuming a last-modified column is always reliable.
- Advancing the watermark before the load succeeds.
- Forgetting deletes in incremental loads.
- Treating ELT as "no transformation design".
- Running backfills at full speed against production sources.
- Publishing partial loads to consumers.

#### 1.11 Mastery criteria

- Explains how changes are detected and how repeats are made safe.
- Quantifies extract time and staleness.
- Handles deletes, late data and backfills explicitly.

#### 1.12 Completion gate

- [ ] Flow states change marker, watermark rule and rerun behaviour.
- [ ] Worksheet reproduced by a reviewer.
- [ ] Delete handling and partial-failure behaviour documented.
- [ ] Topic 1 practice questions answered and corrected.

---

### Module 2 — [Change data capture and database replication](02-change-data-capture-and-database-replication.md)

#### 2.1 Learning objectives

- Explain the purpose of CDC and how it differs from periodic extraction.
- Relate database replication to integration, and distinguish both from backup.
- Describe the CDC approaches covered by the topic file (illustrated here by
  log-based, trigger-based and query-based).
- Handle inserts, updates, deletes and ordering.
- Explain the initial snapshot plus ongoing change pattern.
- Reason about lag, schema changes, duplicates, restarts, replay, source load
  and checkpointing.

#### 2.2 Why the topic matters in real-world Data Architecture

CDC offers fresher data and captures deletes without scanning the source, but
it moves complexity into ordering, restart and schema handling. Misjudging
what a CDC mechanism guarantees is a leading cause of silent downstream
inconsistency.

#### 2.3 Prerequisite knowledge

Module 1 here; 2D.5 Topic 6 (replication, consistency); 2D.3 Topic 3 (replay).

> **Scope note.** The approaches below are illustrative. Follow the approaches
> the topic file names. Do not assume every CDC solution has identical delivery
> or ordering guarantees; the roadmap repeatedly requires you to **read the
> stated guarantees** of the mechanism you use.

#### 2.4 Beginner-level learning sequence

1. **Define CDC:** capturing and delivering row-level changes (insert, update,
   delete) from a source as they are committed.
2. **Contrast with periodic extraction:**

   | Aspect | Periodic extraction | CDC |
   | --- | --- | --- |
   | Detects change by | Comparing or filtering | Reading recorded changes |
   | Deletes | Easily missed | Captured |
   | Source load | Queries scale with data | Reading a log scales with changes |
   | Freshness | Interval-bound | Seconds–minutes |
   | Intermediate states | Lost between runs | Can be preserved |

3. **Define the approaches:** *log-based* (reads the database's transaction
   log), *trigger-based* (triggers write to a change table), *query-based*
   (polls using a marker; essentially incremental batch).
4. **Define replication in this context:** maintaining a copy of a database,
   usually by applying a stream of changes. It is **not** backup (a replicated
   mistake is replicated) and is not itself the architecture that consumes the
   data.
5. **Questions to answer:** What can a change stream tell you that a snapshot
   cannot? Why is a replica not a recovery strategy?
6. **Exercise:** For a customer row updated three times between two batch runs,
   show what batch sees versus what CDC emits.

**Ability to demonstrate:** explain CDC vs batch and replication vs backup.

#### 2.5 Intermediate-level learning sequence

1. **Explain the snapshot-then-stream pattern:** take a consistent initial
   snapshot at a recorded position, then apply changes from that position;
   avoid gaps and double-application at the seam.
2. **Describe a change record:** operation type, key, before and after images
   (where provided), transaction or sequence position, commit time, source
   metadata.
3. **Understand downstream consumption:** apply changes to a replica; append all
   changes to a history table; publish as events; merge to a current-state
   table. Each has different needs for ordering and deletes.
4. **Understand ordering:** per-key ordering is usually essential; global
   ordering may not be available; out-of-order application of two updates to the
   same key produces wrong state.
5. **Understand lag:**

   ```text
   end_to_end_lag = commit_time_at_source → time_visible_to_consumer
   ```

   Components: capture delay, transport, apply delay.
6. **Understand schema changes at the source:** adding a column, renaming,
   changing type; whether the capture mechanism adapts, fails or silently drops
   (links to Topic 5).
7. **Understand checkpointing:** the mechanism records the last processed log
   position; after restart it resumes from there, possibly re-delivering recent
   changes.
8. **Questions to answer:** What is the position at which snapshot and stream
   join? What does the consumer do with a change it has already applied?
9. **Exercise:** Describe, step by step, the initial load and cut-over to the
   change stream for a 200 GB account table, including how you avoid losing or
   double-applying changes.

**Ability to demonstrate:** a snapshot-plus-stream design with explicit
position handling.

#### 2.6 Advanced-level learning sequence

1. **Ordering and transaction boundaries:** changes from one source transaction
   may arrive as separate records; consumers can observe intermediate states
   unless grouped by transaction; cross-table consistency needs transaction
   metadata.
2. **Lag as a backlog problem.** *Illustrative:* peak change rate 1,000 per
   second; consumer applies 800 per second.

   ```text
   backlog_growth = 1,000 − 800 = 200 changes/s
   backlog after 600 s = 120,000 changes
   if arrival falls to 400/s: catch_up_time = 120,000 / (800 − 400) = 300 s
   ```

   Relate to the freshness target; decide when to scale the consumer.
3. **Restart and replay:** at-least-once re-delivery after restart; idempotent
   apply by key and position (Topic 7); behaviour if the log has been
   truncated before the consumer resumes (forces a new snapshot); retention of
   source logs as an operational constraint.
4. **Schema evolution at the source:** compatible additions versus breaking
   changes; coordinating capture configuration with change windows; handling
   historical rows with old shapes.
5. **Source impact:** log reading overhead, log retention, replication slots or
   equivalent holding back log cleanup, storage exhaustion if a consumer stops.
6. **Deletes, updates of keys and truncations:** key updates look like delete +
   insert; truncation may not be emitted as row changes; state which the
   mechanism supports.
7. **Guarantees are mechanism-specific.** Document for your chosen mechanism:
   delivery (at-least-once?), ordering scope (per key? per table?), duplicates,
   behaviour on failover of the source, behaviour on schema change. Where
   undocumented, treat as unknown and design controls (reconciliation).
8. **Cost and complexity:** operational burden, specialist skills, licence/
   service cost, versus incremental batch simplicity.
9. **Failure modes:** consumer stalls and source log fills; snapshot/stream gap;
   out-of-order application; silent drop of a changed column; failover of the
   source database changing log positions; applying changes before the schema
   is ready.
10. **Questions to answer:** What evidence shows the replica is complete? When
    would you prefer incremental batch with a lookback window?
11. **Exercise:** For a CDC design, produce a table of ten failure scenarios with
    detection, recovery and the idempotency or reconciliation control that
    covers each.

**Ability to demonstrate:** a CDC design that states guarantees relied on,
failure behaviour and recovery, with quantified lag and backlog.

#### 2.7 Industry-application exercises

- Design a CDC-based integration for Northbridge's core ledger changes to the
  analytical platform and document assumptions, guarantees and failure behaviour.
- Estimate lag and catch-up for a peak scenario.
- State what you would verify about the chosen mechanism before relying on it.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* The CDC consumer was down for two days and the source's log
   retention is one day. What now?
2. *Scenario:* Two updates to the same account arrive in reverse order at the
   target. What control prevents a wrong final state?
3. *Scenario:* A column is dropped at the source on a Friday release. What
   happens downstream and how should it have been coordinated?

#### 2.9 Expected outputs and deliverables

- CDC vs batch comparison for the scenario.
- Snapshot-plus-stream procedure.
- Guarantee table (documented / assumed / unknown) for the mechanism.
- Lag and catch-up worksheet; failure-scenario table.
- Answers to Topic 2 practice questions.

#### 2.10 Common mistakes and misconceptions

- Treating replication as backup.
- Assuming all CDC tools provide identical ordering and delivery.
- Ignoring the snapshot/stream seam.
- Forgetting that a stalled consumer can harm the source.
- Applying changes without per-key ordering.
- Assuming schema changes propagate safely.

#### 2.11 Mastery criteria

- Explains CDC mechanics and what each approach guarantees.
- Designs the snapshot/stream seam and restart behaviour.
- Quantifies lag and plans recovery.

#### 2.12 Completion gate

- [ ] Guarantee table separates documented, assumed and unknown properties.
- [ ] Seam, restart and schema-change behaviour designed.
- [ ] Lag worksheet reproduced by a reviewer.
- [ ] Topic 2 practice questions answered and corrected.

---

### Module 3 — [APIs, files and managed connectors](03-apis-files-and-managed-connectors.md)

#### 3.1 Learning objectives

- Describe API-based and file-based integration and managed connectors.
- Contrast request-response and bulk-transfer patterns.
- Address authentication and authorisation.
- Handle pagination, rate limits, quotas and source constraints.
- Handle file naming, arrival detection, completeness and format.
- Design incremental extraction, checkpointing, retries and partial failure.
- Choose among APIs, files and connectors, and weigh security, observability,
  maintenance and cost.

#### 3.2 Why the topic matters in real-world Data Architecture

Many sources, especially SaaS and legacy systems, offer only an API, a file
drop, or a packaged connector. The architect must know what each interface can
and cannot support and who owns it when it fails.

#### 3.3 Prerequisite knowledge

Modules 1–2 here; 2D.5 Topic 3 (formats); 2D.2 Topic 5 (vendor dependencies).

#### 3.4 Beginner-level learning sequence

1. **Define the three interface types:**

   | Interface | What it is | Natural use |
   | --- | --- | --- |
   | API | A service exposing records by request | Moderate volumes; current state; business-logic-aware access |
   | File | Data exchanged as files (drop, transfer, shared storage) | Bulk exchange; partners; legacy systems |
   | Managed connector | Packaged, configurable extraction maintained by a vendor/platform | Common SaaS and database sources; fast onboarding |

2. **Contrast request-response and bulk transfer:** many small requests versus
   one large movement.
3. **Learn security basics:** authentication (who are you), authorisation (what
   may you do), credential storage and rotation, least privilege.
4. **Learn the vocabulary:** pagination, rate limit, quota, idempotent request,
   file manifest, control file.
5. **Questions to answer:** Why is pulling 50 million records through a
   record-by-record API usually the wrong choice? Why does a file need a
   completeness signal?
6. **Exercise:** For six sources, name the likely interface and one risk of it.

**Ability to demonstrate:** describe each interface and a typical risk.

#### 3.5 Intermediate-level learning sequence

1. **Map source capabilities and consumer needs** to an interface using a table:

   | Consideration | API | File | Managed connector |
   | --- | --- | --- | --- |
   | Volume | Low–moderate | High | Moderate–high (product-dependent) |
   | Freshness | Near current | Interval-bound | Product-dependent |
   | Incremental support | If provided (filters, cursors) | By file generation | Often built-in |
   | Control over logic | High (code) | High | Limited |
   | Failure transparency | Good (you own it) | Good | Can be opaque |
   | Source impact | Request load | Low | Product-dependent |

2. **Design API extraction:** pagination method (offset vs cursor), page size,
   rate-limit compliance, authentication refresh, incremental filter, ordering
   stability during paging.

   ```text
   api_calls     = ceil(12,000,000 / 1,000) = 12,000
   api_duration  = 12,000 / 10 requests/s = 1,200 s = 20 min
   ```

   *Illustrative.* If the limit halves, the duration doubles; add the quota
   check.
3. **Design file exchange:** naming convention including business date and
   sequence; a **control/manifest file** with row count, checksum and file list;
   arrival detection (manifest present, size stable, expected count);
   completeness check; archive of processed files; handling of duplicates,
   re-sends and corrections.
4. **Design connector use:** what is configured, what is owned by the vendor,
   what is observable, how schema drift is handled, how to run a re-sync.
5. **Checkpointing:** persist the cursor or the last processed file only after
   successful load.
6. **Retries:** retry transient failures with backoff and a bounded budget.

   ```text
   retry_wait_total (base 1 s, factor 2, 5 retries) = 1+2+4+8+16 = 31 s  (before jitter)
   ```

   Do not retry non-idempotent requests blindly.
7. **Format and schema compatibility:** agreed format, encoding, delimiters,
   nullability, date formats, and change notification (links to Topic 5).
8. **Questions to answer:** How do you know a file is complete? What happens if
   page 7 fails after pages 1–6 were loaded?
9. **Exercise:** Design the integration for a SaaS CRM that offers a paginated
   API with a rate limit and a daily bulk export file; choose and justify.

**Ability to demonstrate:** an interface choice and flow with pagination, rate
limit, completeness and checkpoint handling.

#### 3.6 Advanced-level learning sequence

1. **Rate limits and quotas at scale:** concurrency versus limits, shared
   quotas across teams, backoff on throttling responses, scheduling around
   daily quotas; estimate whether the required volume fits.
2. **Paging correctness:** records inserted or deleted during paging cause
   skips or duplicates under offset paging; prefer stable cursors/snapshots;
   deduplicate by key.
3. **Completeness and reliability:** partial pages, truncated files, files
   arriving late or out of sequence, duplicate drops, corrupt compression;
   verification by manifest counts and checksums; quarantine of bad files.
4. **Schema and format change:** new columns in files, reordered columns,
   changed delimiters, API versioning and deprecation; contract tests against
   sample payloads.
5. **Security and governance:** secret management, token rotation, network
   path, encryption in transit and at rest, sensitive fields in files left on
   shared storage, retention of landed files, audit of access.
6. **Operational ownership:** who is called when the vendor connector stops;
   monitoring of lag and error rates; alerting on absence (no file arrived is a
   failure); runbooks; vendor SLAs and their limits.
7. **Choosing among the three:** prefer the interface that gives the required
   freshness and completeness at the lowest source impact and operational burden;
   prefer files for bulk and partners, APIs for current state with business
   rules, connectors where control is not needed and supportability is proven.
8. **Cost and lock-in:** connector pricing models (volume-based charges),
   API call charges, egress, hidden maintenance; portability.
9. **Failure modes:** treating an API's first successful page as success;
   silently skipping a missing nightly file; connector re-sync duplicating data;
   credentials expiring over a weekend; vendor changing an API version.
10. **Questions to answer:** What exactly do you do when the API is unavailable,
    a file is incomplete, or the connector stops processing? Who is told, and
    how do you prove the gap was closed?
11. **Exercise:** For each of the three interface types, write the failure
    scenarios (unavailable, incomplete, stalled), the detection method, the
    recovery step and the reconciliation check.

**Ability to demonstrate:** identify what happens when an API is unavailable, a
file is incomplete or a connector stops, and show the detection and recovery
for each.

#### 3.7 Industry-application exercises

- Design an integration flow for a Northbridge partner system exposing
  transactions through a daily file and corrections through an API.
- Define the file manifest fields and the arrival/completeness rules.
- Estimate API extraction duration against the rate limit and quota.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* The nightly file is missing on Monday. Nothing fails. Why is that
   dangerous and what should detect it?
2. *Scenario:* A vendor connector re-syncs after an outage and loads three days
   of data again. What must the target do?
3. *Scenario:* A source API deprecates a version in 90 days. What is your plan?

#### 3.9 Expected outputs and deliverables

- Interface comparison for the scenario.
- API and file design including manifest, pagination, limits and checkpoints.
- Failure scenario table for each interface.
- Answers to Topic 3 practice questions.

#### 3.10 Common mistakes and misconceptions

- Using record-by-record APIs for bulk.
- Treating file arrival as completeness.
- Ignoring that absence of data is also a failure.
- Retrying non-idempotent calls blindly.
- Assuming a managed connector removes ownership responsibility.
- Leaving credentials, landed files and sensitive fields uncontrolled.

#### 3.11 Mastery criteria

- Chooses an interface with criteria tied to source capability and consumer need.
- Designs pagination, rate-limit, completeness and checkpoint handling.
- States detection and recovery for unavailable, incomplete and stalled cases.

#### 3.12 Completion gate

- [ ] Interface choice cites source limits and consumer needs.
- [ ] File manifest and completeness rules defined.
- [ ] Failure table covers unavailable API, incomplete file, stalled connector.
- [ ] Topic 3 practice questions answered and corrected.

---

### Module 4 — [Streaming events and message contracts](04-streaming-events-and-message-contracts.md)

#### 4.1 Learning objectives

- Explain streaming integration and event-driven data movement.
- Define events, messages, producers and consumers.
- Describe topics/channels, partitions and ordering scope.
- Define event payloads and message contracts, including identity and time.
- Explain delivery behaviour, replay, retention and consumer progress.
- Distinguish event time from processing time.
- Handle compatibility, consumer failure and dead-letter/quarantine.

#### 4.2 Why the topic matters in real-world Data Architecture

Streams decouple producers from many consumers and allow replay, but they
transfer the burden of correctness onto contracts, identity and consumer
design. A broker delivers messages; it does not make business outcomes correct.

#### 4.3 Prerequisite knowledge

Modules 1–3 here; 2D.3 Topic 6 (event-driven patterns); 2D.5 Topic 6
(consistency).

> **Scope note.** Keep to the architecture-pattern level. Do not turn this
> into a product-specific streaming course. Follow the structures (topics,
> partitions, consumer groups) that the topic file names.

#### 4.4 Beginner-level learning sequence

1. **Define terms:** message (a unit of data in transit), event (a message
   recording that something happened), producer, consumer, broker, topic/
   channel, partition, offset (a consumer's position).
2. **Learn the flow:** producer publishes to a topic; the broker retains
   messages for a period; consumers read at their own pace and record progress.
3. **Learn event vs command vs state-transfer** (2D.3 Topic 6) and use past
   tense for events.
4. **Learn contract basics:** the fields every event carries — identity, type,
   version, time, subject key, payload.
5. **Questions to answer:** Why can several consumers read the same event
   independently? What does retention allow?
6. **Exercise:** Draw a payment-posted event with one producer and three
   consumers and list its envelope fields.

**Ability to demonstrate:** describe the streaming flow and an event envelope.

#### 4.5 Intermediate-level learning sequence

1. **Define a basic message contract:**

   | Part | Purpose |
   | --- | --- |
   | Event id | Unique identity for deduplication |
   | Event type and version | Interpretation and compatibility |
   | Event time and publish time | Business time vs system time |
   | Subject key | Ordering and partitioning |
   | Payload | The facts of what happened |
   | Classification / source | Governance and lineage |

2. **Understand partitioning and ordering scope:** ordering is guaranteed only
   within a partition (or equivalent); choose the key so that events that must
   be ordered share a partition (for example account id).
3. **Size the stream (illustrative):** 20,000 events/s × 1 KB = 20 MB/s. With a
   per-partition throughput of 5 MB/s:

   ```text
   partitions_needed = ceil(20 / 5) = 4;  with 2× headroom → 8
   ```

   Check key skew before trusting the arithmetic (2D.5 Topic 5).
4. **Understand retention and replay:**

   ```text
   daily_volume = 20 MB/s × 86,400 s = 1,728,000 MB = 1.728 TB/day
   7-day retention = 12.1 TB; with replication factor 3 ≈ 36.3 TB
   ```

   Retention sets how far back a consumer can replay.
5. **Understand consumer progress:** commit position after processing; commit
   too early loses messages on failure; commit too late reprocesses them.
6. **Understand event time vs processing time:** late and out-of-order events
   are normal; consumers that aggregate must define how late is acceptable.
7. **Understand failure handling basics:** retry transient errors; send
   unprocessable messages to a **dead-letter/quarantine** destination with
   context, rather than blocking the stream or dropping them.
8. **Questions to answer:** What does the consumer do with a duplicate? How long
   can a consumer be down before it loses data?
9. **Exercise:** Design a streaming flow for card authorisations to the fraud
   service, with the event contract, partition key, retention and a dead-letter
   rule.

**Ability to demonstrate:** a streaming flow with contract, partition key,
retention arithmetic and failure destination.

#### 4.6 Advanced-level learning sequence

1. **Delivery semantics:** at-most-once (may lose), at-least-once (may
   duplicate), and "effectively once" achieved by idempotent processing.
   **A broker alone does not guarantee end-to-end exactly-once business
   processing**: the producer may publish twice, the consumer may process and
   fail before committing, or the downstream action may have side effects.
   Transport guarantees must be combined with idempotent consumers (Topic 7).
2. **Ordering failures:** cross-partition ordering is not guaranteed;
   repartitioning breaks ordering assumptions; retries can reorder; design
   consumers to tolerate or to reject stale updates using a version or sequence.
3. **Replay:** reprocessing from an earlier position for corrections or new
   consumers; consequences for side effects (notifications, payments); separate
   replay-safe from replay-unsafe consumers; replay time estimation
   (`retained_volume / sustained_throughput`, 2D.3 Topic 3).
4. **Contract evolution:** adding optional fields, deprecating, splitting events;
   multiple versions in flight; consumer tolerance rules (Topic 5).
5. **Consumer failure and lag:** lag grows when consumers fall behind; backlog
   arithmetic as in Module 2; scaling consumers is bounded by partition count;
   poison messages stall a partition if not handled.
6. **Sensitive data in events:** minimise payload; tokenise; control access per
   topic; retention and erasure obligations for logs (2D.10).
7. **Event time handling:** watermarks for aggregation (conceptually), allowed
   lateness, correction events, reprocessing windows.
8. **Operational complexity:** broker capacity, partition management, schema
   management, observability (lag, throughput, errors), multi-consumer
   ownership.
9. **Failure modes:** treating the broker as the system of record; consumers
   that commit before processing; unbounded retry loops blocking a partition;
   changing the partition key; dual writes from services that publish after
   committing (use an outbox, 2D.5 Topic 6).
10. **Questions to answer:** What would make you not use streaming here? How do
    you prove a consumer processed each event exactly once in effect?
11. **Exercise:** For a payment-posted stream, list the failure points from
    publish to downstream effect, and show which control (idempotency key,
    version check, outbox, dead-letter) covers each.

**Ability to demonstrate:** a design that separates transport guarantees from
business correctness, with ordering, replay and contract evolution handled.

#### 4.7 Industry-application exercises

- Design a streaming integration architecture for Northbridge card events to
  fraud, risk and finance consumers, with documented message contracts and
  operational expectations.
- Calculate partitions and retention storage with stated assumptions.
- Define the dead-letter handling and its owner.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* A consumer crashes after charging a customer but before
   committing its offset. What happens on restart?
2. *Scenario:* A new consumer needs six months of history but retention is seven
   days. Options?
3. *Scenario:* A producer changes a field's meaning without changing its name.
   Which control should catch this?

#### 4.9 Expected outputs and deliverables

- Message contract and envelope definition.
- Partitioning, throughput and retention worksheet.
- Failure-point table from publish to effect.
- Answers to Topic 4 practice questions.

#### 4.10 Common mistakes and misconceptions

- Assuming a broker gives exactly-once business processing.
- Assuming global ordering.
- Committing consumer progress before the work is done.
- Dropping poison messages silently.
- Putting sensitive data in broadly consumed events.
- Treating the stream as the permanent store.

#### 4.11 Mastery criteria

- Designs contracts with identity, time, key and version.
- Quantifies partitions and retention and explains ordering scope.
- Separates transport guarantees from business correctness.

#### 4.12 Completion gate

- [ ] Contract complete; partition key justified by ordering need.
- [ ] Throughput and retention arithmetic reproduced by a reviewer.
- [ ] Failure-point table has a control for every failure.
- [ ] Topic 4 practice questions answered and corrected.

---

### Module 5 — [Data contracts, schema registry and compatibility](05-data-contracts-schema-registry-and-compatibility.md)

#### 5.1 Learning objectives

- Explain the purpose of data contracts and producer/consumer responsibilities.
- Describe contract content: structure, semantics, quality, delivery.
- Explain schema definitions and registries.
- Classify schema changes and apply compatibility modes (backward, forward and
  full, as defined by the topic file).
- Handle required/optional fields and changes to names, types and meanings.
- Validate and enforce contracts; version and deprecate.
- Perform consumer impact analysis and assign ownership and change governance.

#### 5.2 Why the topic matters in real-world Data Architecture

Integration succeeds or fails on whether producers and consumers keep their
agreement as both change. A contract makes the agreement explicit, testable and
owned. A registry makes the structural part machine-enforceable. Neither makes
the *meaning* safe automatically.

#### 5.3 Prerequisite knowledge

Modules 1–4 here; 2D.4 Topic 7 (schema evolution); 2D.1 Topic 3 (ownership).

> **Terminology discipline.** Use the compatibility definitions in the topic
> file. The conventional ones used in this roadmap: *backward compatible* —
> consumers using the **new** schema can read data written with the **old**
> schema; *forward compatible* — consumers using the **old** schema can read
> data written with the **new** schema; *full* — both. State which definition
> you use whenever you classify a change.

#### 5.4 Beginner-level learning sequence

1. **Define a data contract:** an explicit agreement between a producer and its
   consumers on what is delivered.
2. **Define the parts:**

   | Part | Content |
   | --- | --- |
   | Structure | Fields, types, optionality, keys |
   | Semantics | Meaning, units, allowed values, time zones, null meaning |
   | Quality | Completeness, validity, uniqueness expectations |
   | Delivery | Freshness, availability, retention, channel |
   | Ownership and change | Owner, contact, versioning, deprecation notice |

3. **Define a schema and a registry:** a schema is a formal description of
   structure; a registry stores versions and checks changes against a
   compatibility mode.
4. **Define compatibility terms** (see terminology note).
5. **Questions to answer:** Why is a schema alone not a contract? Who is
   responsible if a consumer breaks after a compatible change?
6. **Exercise:** Write a one-page contract for a customer-changed event.

**Ability to demonstrate:** list the parts of a contract and define the
compatibility terms.

#### 5.5 Intermediate-level learning sequence

1. **Classify representative changes** and their effect on producers and
   consumers:

   | Change | Backward | Forward | Notes |
   | --- | --- | --- | --- |
   | Add optional field with default | Yes | Yes (old consumers ignore it) | Usually safe structurally |
   | Add required field without default | No (old data lack it) | Yes | Breaks readers of old data |
   | Remove optional field | Yes | No (old consumers may expect it) | Consumer impact depends on use |
   | Remove required field | No | No (typically) | Breaking |
   | Rename field | No | No | Equivalent to remove + add |
   | Widen type | Often yes | Often no | Depends on direction and engine |
   | Narrow type | No | Often yes | Values may not fit |
   | Add enumeration value | Yes structurally | Consumers may mishandle | Semantic impact |
   | Change meaning, same type | Passes structurally | Passes structurally | **Silent breaking** |

   *(Treat entries as illustrative and verify them against the registry's
   documented rules.)*
2. **Choose a compatibility mode per contract** based on who upgrades first:
   consumers first → forward needed; producers first → backward needed; unknown
   or independent → full.
3. **Define required vs optional** deliberately: required fields raise the cost
   of change; prefer optional with explicit defaults for new fields.
4. **Version and deprecate:** version identifier, supported versions,
   deprecation notice period, sunset date.
5. **Validate and enforce:** check at publish time (registry), at ingest
   (schema validation, quarantine of non-conforming records), and in CI
   (contract tests with sample payloads).
6. **Consumer impact analysis:** list consumers (from lineage and subscriptions),
   what each reads, what each assumes; classify the effect; assign actions and
   dates (2D.4 Topic 7).
7. **Questions to answer:** Who approves a breaking change? How do you find
   unregistered consumers?
8. **Exercise:** For eight proposed changes to a payment event, classify each as
   backward/forward/full compatible or breaking, name affected consumers and
   the required action.

**Ability to demonstrate:** a classification table and an impact analysis.

#### 5.6 Advanced-level learning sequence

1. **Structural vs semantic compatibility.** A change can be structurally
   compatible and semantically breaking: a field's type is unchanged but its
   unit changes from cents to units, its time zone changes, a status value is
   reused, "active" is redefined. Registries cannot detect this. Controls:
   semantic descriptions in the contract, change review by the domain owner,
   new field name or new version for new meaning, contract tests with value
   assertions, communication to consumers.
2. **Compatibility strategy for many consumers:** pick the strictest mode the
   slowest consumer requires; use parallel versions during migration; time-box
   the overlap; track consumer migration status.
3. **Evolution mechanics:** expand-and-contract (add new, migrate readers, then
   remove old); tolerant readers (ignore unknown fields); defaults for missing
   fields; handling of historical data stored under older schemas.
4. **Change management process:** change request, compatibility check
   (automatic), impact analysis (manual for semantics), consumer notification,
   approval authority by change class, rollout and rollback plan, post-change
   verification.
5. **Contract ownership and governance:** the producer owns the contract;
   consumers own their expectations; a platform or governance function owns
   tooling and policy (2D.1, 2D.10); disputes are resolved by a stated
   escalation path.
6. **Flexibility vs control trade-off:** strict contracts slow change but protect
   consumers; loose contracts speed change but push breakage downstream;
   choose per data class (regulatory interfaces strict; exploratory feeds
   looser).
7. **Registry limitations and risks:** registry availability as a dependency;
   schema ids embedded in messages; divergence between registry and documented
   contract; compatibility checks that do not cover your engine's behaviour.
8. **Failure modes:** syntactically valid but semantically changed fields;
   enumerations extended without consumer handling; breaking changes pushed
   through "because it compiles"; unversioned files; undocumented consumers.
9. **Questions to answer:** Which changes would you ban outright? What is your
   policy for removing a field and how long is the notice?
10. **Exercise:** Define a contract and schema evolution policy for a widely
    consumed customer event, including compatibility mode, semantic-change
    process, deprecation timeline and enforcement points.

**Ability to demonstrate:** a policy that handles structural and semantic change
for multiple consumers.

#### 5.7 Industry-application exercises

- Define a data contract and schema evolution policy for Northbridge's
  account-changed feed consumed by fraud, risk and finance.
- Write the deprecation notice for a renamed field, with dates and support.
- Define the automated and manual checks in the change pipeline.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* The producer changes "balance" from available balance to ledger
   balance, same name and type. Detect and respond.
2. *Scenario:* A new regulatory field must be mandatory for new records only.
   Represent it and keep old consumers working.
3. *Scenario:* Three consumers upgrade at different speeds. Choose the
   compatibility mode and the migration plan.

#### 5.9 Expected outputs and deliverables

- Data contract template and one completed contract.
- Change classification and impact tables.
- Evolution and deprecation policy.
- Answers to Topic 5 practice questions.

#### 5.10 Common mistakes and misconceptions

- Equating a schema with a contract.
- Assuming a passing compatibility check means a safe change.
- Making fields required "for quality" and blocking all change.
- Renaming without transition.
- Ignoring unregistered consumers.
- Leaving contract ownership unassigned.

#### 5.11 Mastery criteria

- Writes contracts covering structure, semantics, quality, delivery, ownership.
- Classifies changes correctly, including semantic ones.
- Designs a change process matched to consumer diversity.

#### 5.12 Completion gate

- [ ] Contract includes semantics and ownership, not only structure.
- [ ] At least one structurally valid, semantically breaking change identified
      and handled.
- [ ] Policy states mode, notice period and enforcement points.
- [ ] Topic 5 practice questions answered and corrected.

---

### Module 6 — [Data virtualization, federation and data sharing](06-data-virtualization-federation-and-data-sharing.md)

#### 6.1 Learning objectives

- Define virtualisation, federation and data sharing.
- Contrast logical access with physical movement.
- Explain query execution and source dependencies.
- Respect ownership and access boundaries.
- Reason about freshness, consistency, performance, availability and network.
- Address security, governance and troubleshooting.
- Choose among virtualisation, federation, replication and materialisation.

#### 6.2 Why the topic matters in real-world Data Architecture

Copying data creates cost, lag, duplicate ownership and governance burden.
Querying in place avoids copies but couples consumers to source availability and
performance. The architect must know when each trade is worth it.

#### 6.3 Prerequisite knowledge

Modules 1–5 here; 2D.3 Topics 4–6 (data products, fabric, data sharing); 2D.5
Topic 1 (workload separation).

#### 6.4 Beginner-level learning sequence

1. **Define the terms:**

   | Term | Meaning |
   | --- | --- |
   | Data virtualisation | A logical layer presenting data from several sources as one view without copying them (queries are executed against the sources) |
   | Federation | Executing a query across multiple independent data stores and combining results |
   | Data sharing | Granting governed access to a producer's data to another consumer or organisation, ideally without making a separate copy |
   | Materialisation | Persisting a result (copy) for faster, independent access |

2. **Contrast logical access with physical movement:** a virtual view stores no
   data, a replica stores data.
3. **Learn why it is attractive:** speed to expose, fewer copies, single source
   of truth.
4. **Learn why it is risky:** performance and availability depend on sources.
5. **Questions to answer:** What happens to a federated query if one source is
   down? Is a shared dataset a copy?
6. **Exercise:** For six access needs, mark whether virtualisation, replication
   or sharing is plausible and why.

**Ability to demonstrate:** explain the terms and the central trade-off.

#### 6.5 Intermediate-level learning sequence

1. **Compare direct access, federated access and materialised integration:**

   | Dimension | Direct/federated query | Materialised copy |
   | --- | --- | --- |
   | Freshness | Current | As of last refresh |
   | Source load | Each query hits sources | Only refresh hits sources |
   | Consumer performance | Limited by slowest source and network | Local and tunable |
   | Availability | Depends on every source | Independent after load |
   | Data duplication | None | Yes |
   | Cross-source joins | Costly, data moved at query time | Pre-joined |
   | Governance surface | Source controls plus layer | Copy needs its own controls |

2. **Understand query execution:** push-down of filters and aggregation to the
   source; moving large intermediate results across the network; joins across
   sources.
3. **Availability arithmetic:** a query touching three serial sources.

   ```text
   A = 0.999 × 0.995 × 0.999 ≈ 0.993  (≈ 99.3%)
   ```

   *Illustrative.* Compare with the consumer's availability target.
4. **Understand data sharing patterns:** a producer publishes a governed dataset
   that other domains or organisations query in place; the producer keeps
   ownership; the consumer gets access control, not a copy (2D.3 Topic 4, 6).
5. **Understand ownership and access boundaries:** who authorises access, what
   the consumer may see, how usage is audited.
6. **Understand freshness and consistency:** a federated query reads different
   sources at slightly different instants; there is no cross-source snapshot.
7. **Questions to answer:** What load does a dashboard refresh put on a
   production source? Which workloads justify a materialised copy?
8. **Exercise:** For Northbridge, compare three ways to give risk analysts a
   customer-plus-account view: federated query, nightly materialised table, and
   a shared curated data product. Recommend with reasons.

**Ability to demonstrate:** a comparison with freshness, load, availability and
governance stated.

#### 6.6 Advanced-level learning sequence

1. **Performance:** push-down limits; large joins moving data to the layer;
   concurrency multiplying source load; caching and its staleness; query
   planning opacity.
2. **Source-system impact:** analytical queries on operational systems (2D.5
   Topic 1); protect sources with replicas, resource limits or by
   materialising.
3. **Consistency:** no transactional guarantee across sources; time-skew between
   reads; reconciliation of results with a materialised alternative.
4. **Coupling:** consumers become dependent on source schemas and availability;
   a schema change at a source breaks consumers unless the virtual layer
   absorbs it (and then owns the contract, Topic 5).
5. **Security and governance:** authorisation passes through multiple layers;
   row/column controls must be consistent; audit of who accessed what;
   masking; cross-border queries and residency; virtualisation does **not**
   remove the need for governance, it can hide where sensitive data flow.
6. **Operational complexity and troubleshooting:** a slow query has many
   possible causes (source, network, planner, concurrency); need for query
   observability and clear ownership of the virtual layer.
7. **Selection conditions:**
   - *Favour virtualisation/federation:* exploratory or low-frequency access,
     small result sets, need for current data, regulatory reasons to avoid
     copies, temporary integration during migration, sources that are robust.
   - *Favour replication/materialisation:* heavy or frequent queries, large
     joins, strict availability or performance targets, sensitive production
     sources, historical snapshots, independent consumer scaling.
   - *Favour sharing:* a producer with a managed data product and consumers in
     other domains or organisations needing access without copies.
8. **Cost and trade-offs:** query compute charges, data transfer, duplicate
   storage, engineering effort of the virtual layer, vendor lock-in.
9. **Failure modes:** a dashboard on a federated view taking down a production
   database; unknown full-table scans through a view; permissions drift between
   layers; copying shared data "just in case" and losing the single source;
   treating the virtual layer as a long-term replacement for integration.
10. **Questions to answer:** What would force you to materialise? Which controls
    prove no unauthorised copy was made?
11. **Exercise:** Evaluate a proposal to replace a nightly ETL with a federated
    view; quantify source load and availability, and recommend with conditions
    for revisiting.

**Ability to demonstrate:** recommend an access pattern with quantified impact
and an explicit statement of limitations.

#### 6.7 Industry-application exercises

- Recommend a data access and sharing pattern for Northbridge's cross-system
  customer and account view and explain its limitations.
- Estimate the source load of a federated dashboard with stated assumptions.
- Define who authorises access and how usage is audited.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* A federated report slows the core banking database at month-end.
   Options at three cost levels?
2. *Scenario:* A partner organisation needs read access to a dataset without a
   copy leaving the bank. What are the requirements for a sharing pattern?
3. *Scenario:* A business unit wants a virtual layer to avoid building
   pipelines. How do you evaluate the request?

#### 6.9 Expected outputs and deliverables

- Access-pattern comparison.
- Availability and load estimates.
- Recommendation with limitations and revisit triggers.
- Answers to Topic 6 practice questions.

#### 6.10 Common mistakes and misconceptions

- Assuming virtualisation removes source performance constraints.
- Assuming virtualisation or sharing removes the need for governance.
- Ignoring availability multiplication across sources.
- Treating a shared dataset as freely copyable.
- Using virtualisation as a permanent substitute for needed integration.
- Forgetting the layer's own ownership and contract.

#### 6.11 Mastery criteria

- Compares logical access and materialisation on freshness, load, availability,
  governance and cost.
- Quantifies source impact and availability.
- States limits and revisit conditions.

#### 6.12 Completion gate

- [ ] Comparison includes source load, availability and governance.
- [ ] Recommendation states limitations explicitly.
- [ ] At least one case concludes that materialisation is required.
- [ ] Topic 6 practice questions answered and corrected.

---

### Module 7 — [Idempotency, deduplication and reconciliation](07-idempotency-deduplication-and-reconciliation.md)

#### 7.1 Learning objectives

- Define idempotency and explain why repeated execution is normal.
- Distinguish duplicate data from duplicate processing.
- Apply deduplication strategies and choose identity (business keys vs
  technical identifiers).
- Design safe replay, retries and reprocessing.
- Reconcile source and target with counts, totals, checksums and business
  validations.
- Detect missing, duplicated or inconsistent data.
- Handle late, out-of-order data, corrections and deletes.
- Produce operational evidence and handle exceptions.

#### 7.2 Why the topic matters in real-world Data Architecture

Retries, restarts and replays are guaranteed to happen. Without idempotency they
corrupt data; without reconciliation nobody knows. These controls convert an
unreliable pipeline into a trustworthy one.

#### 7.3 Prerequisite knowledge

Modules 1–6 here; 2D.4 Topics 2–3 (keys); 2D.5 Topic 6 (consistency).

#### 7.4 Beginner-level learning sequence

1. **Define idempotency:** performing an operation once or many times has the
   same effect as performing it once.
2. **Give examples:**

   | Operation | Idempotent? | Why |
   | --- | --- | --- |
   | Set balance = 100 | Yes | Same result however often |
   | Insert row without a uniqueness rule | No | Duplicates accumulate |
   | Add 10 to balance | No | Each run changes the result |
   | Upsert by key with same payload | Yes | Final state identical |

3. **Define duplicate data** (the same fact present twice) and **duplicate
   processing** (the same input handled twice, possibly with side effects).
4. **Define reconciliation:** comparing source and target to confirm they agree.
5. **Questions to answer:** Why will a retried job duplicate rows without
   safeguards? What does "agree" mean (count, sum, content)?
6. **Exercise:** Classify ten operations as idempotent or not and say how to
   make the non-idempotent ones safe.

**Ability to demonstrate:** explain idempotency, duplication and reconciliation
with examples.

#### 7.5 Intermediate-level learning sequence

1. **Choose identity:** a business key (for example transaction reference), a
   technical id from the source, or an event id; the identity must be stable,
   unique within scope and available at every stage. Composite keys for
   dimensional or historical targets (2D.4).
2. **Make loads idempotent:**
   1. *Upsert/merge by key:* insert if absent, update if present.
   2. *Replace a partition:* delete-and-insert a whole batch window atomically.
   3. *Insert-if-not-exists* with a uniqueness constraint.
   4. *Idempotency key* for operations with side effects (the second attempt
      with the same key is ignored).
3. **Deduplicate:** keep one record per key by a rule — latest by version or
   event time, first seen, or highest-priority source; deterministic tie-break.
4. **Replay/retry safety:** record processed ids or positions atomically with
   the effect; do not rely on "should not happen".
5. **Reconciliation checks, from cheap to strong:**

   | Check | Detects | Limit |
   | --- | --- | --- |
   | Row counts | Missing/extra rows | Offsetting errors hidden |
   | Control totals (sums) | Value drift | Compensating errors |
   | Key-set comparison | Missing/extra keys | Cost at scale |
   | Checksums/hashes per partition or row | Content differences | Needs identical canonical form |
   | Business-rule checks | Semantic failures (balance = opening + movements) | Needs rules |

6. **Quantify a discrepancy:**

   ```text
   delta = source_count − target_count   e.g. 2,000,000 − 1,999,994 = 6
   ```

   Define a tolerance (often zero for financial data), the response, and the
   owner.
7. **Reconcile per partition/window** so a discrepancy can be located quickly.
8. **Questions to answer:** Which identity is safe if two sources use different
   ids? What does your count check miss?
9. **Exercise:** Design an idempotent daily load for transactions with a merge
   key, a dedup rule and a three-level reconciliation (count, total, key-set).

**Ability to demonstrate:** a repeatable load and a reconciliation that detect
duplicates and gaps.

#### 7.6 Advanced-level learning sequence

1. **Identity problems:** keys reused after deletion; keys that differ across
   sources (entity resolution belongs to 2D.11); surrogate keys regenerated on
   reload (breaks idempotency); natural keys that change; composite keys
   missing a version component.
2. **Ordering, versions and late data:** apply an update only if its version or
   sequence is newer than the stored one, so out-of-order delivery cannot
   overwrite newer state; define the handling of events later than an allowed
   lateness (accept and restate, quarantine, or ignore with a record).
3. **Corrections and deletes:** correction events versus in-place update;
   soft deletes and tombstones; retention of the original (2D.4 Topic 5);
   deletion propagation to copies; reconciling deleted records.
4. **Retries with side effects:** exactly-once effect through an idempotency key
   or the transactional outbox/inbox patterns; payment and notification
   examples; time-limited key retention and its limits.
5. **Reconciliation coverage:** what the checks do **not** cover (a wrong
   transformation that preserves counts and totals; a consistently wrong
   mapping); add independent business-level checks and sampled record-level
   comparisons; reconcile at each hop for critical flows.
6. **Neither deduplication nor idempotency guarantees complete correctness.**
   Idempotency prevents harm from repetition; deduplication removes copies; both
   still allow **missing** data, wrong transformations and wrong identity.
   Completeness and correctness require reconciliation and validation as
   separate controls.
7. **Operational evidence:** reconciliation reports retained, with run id,
   window, counts, totals, results and exceptions; exception queue with owners
   and ageing; sign-off for material breaks; audit trail.
8. **Cost and complexity:** strict per-record verification is expensive; tier the
   controls by criticality (full key comparison for regulatory flows, counts and
   totals for low-risk feeds).
9. **Failure modes:** dedup by a non-unique key silently dropping valid
   records; merge on a changing key; counts matching while values differ;
   reconciliation run against the same faulty extract as the load (not
   independent); exceptions never reviewed.
10. **Questions to answer:** What is independent about your reconciliation? How
    would a wrong mapping survive all your checks?
11. **Exercise:** For a flow, list five defects (lost row, duplicate, wrong
    mapping, late update overwriting newer state, missed delete) and mark which
    controls detect each and which do not.

**Ability to demonstrate:** distinguish idempotency, deduplication and
reconciliation and show which defect each does and does not catch.

#### 7.7 Industry-application exercises

- Create a reliability and reconciliation strategy for Northbridge's
  transaction pipeline with explicit failure scenarios.
- Define the identity, merge rule, version rule and tolerance per flow.
- Write the reconciliation report format and the exception workflow.

#### 7.8 Practical scenarios and case-based reasoning

1. *Scenario:* A retried payment event debits an account twice downstream. What
   control was missing?
2. *Scenario:* Counts and totals match, yet a regulatory report is wrong. What
   class of defect is this and what check would catch it?
3. *Scenario:* An old update arrives after a newer one and overwrites it. Fix.

#### 7.9 Expected outputs and deliverables

- Identity and merge/dedup rules per flow.
- Reconciliation design with coverage matrix.
- Defect-to-control table.
- Answers to Topic 7 practice questions.

#### 7.10 Common mistakes and misconceptions

- Treating deduplication as idempotency.
- Believing either guarantees complete correctness.
- Using unstable or non-unique keys.
- Reconciling with the same logic that produced the data.
- Relying on counts alone.
- Running reconciliation but never reviewing exceptions.

#### 7.11 Mastery criteria

- Selects identity and designs idempotent loads and deduplication.
- Designs layered reconciliation with stated coverage and tolerance.
- States what the controls do not detect.

#### 7.12 Completion gate

- [ ] Identity, merge, version and dedup rules documented per flow.
- [ ] Coverage matrix shows detected and undetected defect classes.
- [ ] Reconciliation independence argued; exception workflow defined.
- [ ] Topic 7 practice questions answered and corrected.

---

### Module 8 — [Integration pattern selection and failure handling](08-integration-pattern-selection-and-failure-handling.md)

#### 8.1 Learning objectives

- Define integration requirements and decision scope.
- Compare batch, incremental, CDC, API, file, streaming, virtualisation and
  sharing patterns.
- Select patterns by freshness, throughput, correctness and availability.
- Evaluate source capabilities and constraints, complexity, cost,
  maintainability and operational ownership.
- Identify failure modes and boundaries.
- Design timeouts, retries, backoff and limits; checkpoints, replay, recovery
  and reprocessing.
- Combine idempotency, deduplication and reconciliation; monitor and alert.
- Handle partial success and downstream failure; address security, governance
  and contracts; document alternatives and trade-offs.

#### 8.2 Why the topic matters in real-world Data Architecture

This is where mechanisms become decisions. Two designs can both work on a good
day; the right one is the one that fails safely, recovers quickly and proves its
own correctness.

#### 8.3 Prerequisite knowledge

Modules 1–7 here; all of 2D.2 (especially Topics 4–7).

#### 8.4 Beginner-level learning sequence

1. **Recap the mechanisms** using the Section 1.4 table.
2. **Learn the failure categories:**

   | Category | Examples |
   | --- | --- |
   | Source failure | Unavailable, slow, schema change, bad data |
   | Transport failure | Network drop, timeout, throttling |
   | Processing failure | Bug, bad record, resource exhaustion |
   | Target failure | Unavailable, constraint violation, full |
   | Control-plane failure | Scheduler down, credentials expired, registry unreachable |
   | Operator failure | Wrong config, premature deployment |

3. **Learn the response vocabulary:** timeout, retry, backoff, circuit breaker
   (conceptually), checkpoint, replay, quarantine, alert, runbook.
4. **Questions to answer:** Which failures are transient and which are
   permanent? Why is "retry forever" dangerous?
5. **Exercise:** Classify twenty failures by category and say whether to retry,
   quarantine or escalate.

**Ability to demonstrate:** name the mechanisms and failure categories and map
failures to responses.

#### 8.5 Intermediate-level learning sequence

1. **Define the integration requirement** in measurable terms: freshness
   (percentile and window), throughput (peak), correctness (tolerance, controls),
   availability, retention/replay needs (2D.2 Topic 4).
2. **Profile the source** (capabilities, limits, change visibility, deletes) and
   the consumer (access pattern, history, ordering needs).
3. **Select a pattern** with a decision table:

   | If… | Consider… | Because |
   | --- | --- | --- |
   | Hours-level freshness, source has reliable change marker | Incremental batch | Simplest adequate |
   | Seconds–minutes freshness, deletes matter, source supports log reading | CDC | Low source load, captures deletes |
   | Source exposes only an API | API extraction | Interface constraint |
   | Partner delivers bulk | File with manifest | Fit to partner |
   | Many consumers need facts as they occur | Event streaming | Decoupling and replay |
   | Occasional exploratory access, small results | Virtualisation/federation | Avoid copies |
   | Producer-owned product consumed by others | Data sharing | Ownership and no duplication |

   Treat the table as a starting point; verify against requirements.
4. **Always include a "simplest adequate" baseline** and say why it is not
   enough, or choose it.
5. **Document the normal flow and the expected failure behaviour** per flow.
6. **Design timeouts and retries:** set timeouts from observed latency
   percentiles; retry transient errors with backoff and a bounded budget;
   never retry non-idempotent operations without an idempotency key.
7. **Design checkpoints and recovery:** where progress is stored; how a run
   resumes; what is replayed.
8. **Design monitoring:** freshness (age of newest data), volume anomalies,
   error and retry rates, lag/backlog, reconciliation results, absence
   detection.
9. **Questions to answer:** What happens if the source is down for a day? What
   tells you before the consumer notices?
10. **Exercise:** Choose patterns for five Northbridge flows (ledger changes to
    analytics, card events to fraud, partner file, CRM API, regulator extract)
    with the failure behaviour of each.

**Ability to demonstrate:** a pattern per flow with measurable requirements,
failure behaviour and monitoring.

#### 8.6 Advanced-level learning sequence

1. **Failure boundaries and blast radius:** isolate flows so one failure does not
   stall others (separate queues, bulkheads); decouple stages with durable
   storage; avoid shared dependencies without fallback.
2. **Interacting failures:** a source slowdown causes timeouts, retries and load
   amplification (retry storm); a downstream outage causes backlog and then
   overload on recovery; a schema change coincides with a replay. Design
   backpressure, jittered backoff and recovery throttling.
3. **Retry budgets and amplification arithmetic.** *Illustrative:* 5 retries per
   call across 3 layers can multiply a single failure into up to
   (1+5)³ = 216 attempts; limit retries to one layer and add jitter.
4. **Recovery strategy by failure class:** transient → retry; poison record →
   quarantine and continue; unavailable source → wait with alert and catch-up
   plan; target outage → buffer and replay; logic bug → fix, replay from
   checkpoint or landed raw, reconcile.
5. **Catch-up and backlog:** recovery capacity must exceed arrival rate by a
   margin; use `catch_up_time = backlog / (capacity − arrival)`; ensure the
   freshness target is renegotiated for recovery periods or capacity sized for
   it.
6. **Partial success:** atomic publication; compensating actions;
   reconciliation to find what landed; communicate partial availability to
   consumers (data freshness markers).
7. **Correctness end to end:** transport guarantees (delivery, ordering) are
   necessary but not sufficient; combine idempotency, deduplication and
   reconciliation (Topic 7); define the correctness claim per flow ("no loss,
   no duplication, eventually consistent within N minutes").
8. **Security and governance:** least-privilege credentials per flow; secrets
   management; encryption in transit; data classification applied in transit and
   landing; audit trails; retention of landed copies and dead-letter content;
   lineage registration (2D.11).
9. **Operational ownership:** an owner per flow; on-call and escalation;
   runbooks; SLOs and error budgets; change windows; vendor dependency
   management.
10. **Cost and maintainability:** engineering effort, run cost, specialist
    skills; prefer the simplest mechanism that meets the target; record the
    complexity you are accepting and why.
11. **Document alternatives and trade-offs** in an ADR (2D.2 Topic 7): context,
    criteria, options, outcome, rejected alternatives, assumptions, revisit
    triggers.
12. **Failure modes of the design process itself:** choosing streaming because
    "real-time" sounds modern; designing only the happy path; designing
    recovery without testing it; accepting vendor claims about guarantees
    without evidence.
13. **Questions to answer:** Which single component failure would hurt most? What
    would you test in a failure drill?
14. **Exercise:** For a chosen design, produce a failure-mode and recovery
    matrix (at least ten rows) covering every component, and a failure-drill
    plan with pass criteria.

**Ability to demonstrate:** explain both the normal data flow and how the
architecture behaves when individual components fail, with correctness claims
and evidence.

#### 8.7 Industry-application exercises

- Produce a complete integration pattern recommendation with failure-handling
  and recovery design for Northbridge's ledger-to-analytics and card-to-fraud
  flows.
- Write the ADR for the main pattern choice with rejected alternatives.
- Define the monitoring and alerting set and the failure drill.

#### 8.8 Practical scenarios and case-based reasoning

1. *Scenario:* The fraud stream backs up after a downstream outage and on
   recovery overloads the fraud service. What design prevents this?
2. *Scenario:* A vendor claims "exactly-once delivery". What do you verify and
   what do you still build?
3. *Scenario:* The business asks for sub-second freshness for a daily
   regulatory report. How do you respond?

#### 8.9 Expected outputs and deliverables

- Pattern selection table with requirement evidence.
- Failure-mode and recovery matrix.
- Monitoring and alerting specification; failure-drill plan.
- ADR for the recommendation.
- Answers to Topic 8 practice questions.

#### 8.10 Common mistakes and misconceptions

- Selecting by fashion or vendor claim.
- Designing only the happy path.
- Unbounded retries and retry storms.
- Assuming delivery guarantees equal business correctness.
- Monitoring errors but not absence or freshness.
- Never testing recovery.

#### 8.11 Mastery criteria

- Selects patterns from measurable requirements and source constraints.
- Designs failure handling, recovery and correctness controls per flow.
- Documents trade-offs, assumptions and revisit conditions.

#### 8.12 Completion gate

- [ ] Every flow has a measurable requirement, a pattern, a baseline comparison
      and a correctness claim.
- [ ] Failure matrix covers every component with detection and recovery.
- [ ] ADR includes rejected alternatives and revisit triggers.
- [ ] Topic 8 practice questions answered and corrected.

---

## 5. Module dependencies and recommended learning order

### 5.1 Dependency table

| # | Topic file | Prerequisite concepts | Main learning outcome | Practical exercise / deliverable | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `01-batch-etl-elt-and-incremental-ingestion.md` | 2D.2 Topic 4; 2D.4 Topics 2–3; 2D.5 Topics 1, 3 | Design batch/incremental ingestion with safe re-runs | Ingestion flow; extract-time and staleness worksheet; backfill procedure | Change detection, watermark rule and rerun behaviour explicit |
| 2 | `02-change-data-capture-and-database-replication.md` | Topic 1; 2D.5 Topic 6 | Explain and design CDC with snapshot seam and recovery | Snapshot-plus-stream design; guarantee table; lag worksheet | Documented/assumed/unknown guarantees separated |
| 3 | `03-apis-files-and-managed-connectors.md` | Topics 1–2; 2D.5 Topic 3 | Choose and design API/file/connector integrations | Interface comparison; manifest design; failure table | Unavailable/incomplete/stalled cases handled |
| 4 | `04-streaming-events-and-message-contracts.md` | Topics 1–3; 2D.3 Topic 6 | Design streaming flows and message contracts | Contract; partition/retention worksheet; failure-point table | Ordering scope and transport-vs-business correctness stated |
| 5 | `05-data-contracts-schema-registry-and-compatibility.md` | Topics 1–4; 2D.4 Topic 7 | Define contracts and compatibility policy | Contract template; change classification; evolution policy | Semantic-change case handled |
| 6 | `06-data-virtualization-federation-and-data-sharing.md` | Topics 1–5; 2D.3 Topics 4–6 | Judge logical access vs movement | Access-pattern comparison; load and availability estimates | Limitations and revisit triggers stated |
| 7 | `07-idempotency-deduplication-and-reconciliation.md` | Topics 1–6; 2D.4 Topics 2–3 | Design idempotent loads and layered reconciliation | Identity rules; coverage matrix; defect-to-control table | Undetected defect classes stated |
| 8 | `08-integration-pattern-selection-and-failure-handling.md` | Topics 1–7; 2D.2 Topics 4–7 | Select patterns and design failure handling | Selection table; failure matrix; monitoring spec; ADR | Every flow has requirement, baseline and recovery |

### 5.2 Recommended order and why

1. **Topic 1: foundational data movement.** Batch and incremental ingestion are
   the baseline all other mechanisms are compared with.
2. **Topic 2: change capture and ongoing synchronisation.** CDC solves the
   weaknesses revealed in Topic 1 (deletes, freshness, source load) and
   introduces ordering and restart concerns.
3. **Topic 3: system interfaces.** Real sources expose APIs, files or
   connectors; learning them early lets the later topics use realistic
   constraints.
4. **Topic 4: event-based integration.** Introduces streaming, ordering and
   replay after the learner understands change capture.
5. **Topic 5: contracts and compatibility.** Controlled producer–consumer
   agreements apply to every mechanism studied so far and become essential once
   several consumers exist.
6. **Topic 6: alternatives to physical movement.** Virtualisation, federation
   and sharing are best judged after the learner knows what copying costs.
7. **Topic 7: correctness and validation.** Idempotency, deduplication and
   reconciliation harden everything before them.
8. **Topic 8: integration into decisions.** Selection and failure handling
   combine all earlier concepts.

### 5.3 Dependencies and iteration

| Relationship | Explanation |
| --- | --- |
| Pattern choice (8) → contract design (5) | The chosen mechanism determines the form and enforcement of the contract |
| Failure analysis (8) → idempotency/reconciliation (7) | Failure scenarios often reveal missing controls; revisit Topic 7 |
| CDC (2) ↔ streaming (4) | CDC output is commonly published as events; ordering and replay concerns overlap |
| Batch (1) ↔ reconciliation (7) | Batch loads are where control totals are easiest and most needed |
| Contracts (5) ↔ every mechanism | Revisit Topic 5 after each mechanism |
| Virtualisation (6) ↔ database selection (2D.5 Topic 2) | Source capability limits what can be federated |
| Replay (2, 4, 8) ↔ retention (2D.5 Topic 7) | Replay needs depend on retention policy |

| Trigger | Revisit |
| --- | --- |
| A load produced duplicates | Topics 7, 1 |
| A consumer broke after a change | Topic 5 (and 4 for events) |
| Freshness target missed | Topics 1, 2, 4, 8 |
| Source complaints about load | Topics 1, 2, 3, 6 |
| Reconciliation break found | Topics 7, 8, then the originating mechanism |
| New regulation changes retention or residency | Topics 6, 8 and 2D.5 Topic 7 |

Adapt the sequence if the repository, once populated, establishes a more
appropriate order. Cross-references: foundations (2D.1), requirements (2D.2),
patterns (2D.3), modeling (2D.4), storage (2D.5), platform (2D.7), cloud
(2D.8), streaming (2D.9), governance (2D.10), metadata (2D.11), resilience
(2D.12), serving (2D.14).

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
| Integration terminology and pattern identification | Definitions; recognise mechanisms in descriptions | 1–8 | Beginner |
| ETL/ELT and incremental ingestion | Change detection, watermarks, reruns, arithmetic | 1 | Beginner → advanced |
| CDC and replication behaviour | Snapshot seam, ordering, lag, restart | 2 | Intermediate → advanced |
| API, file and managed connector selection | Interface fit, limits, completeness | 3 | Intermediate → advanced |
| Streaming and message contract design | Contracts, partitions, retention, replay | 4 | Intermediate → advanced |
| Data contract and schema compatibility analysis | Classify changes, impact, policy | 5 | Intermediate → advanced |
| Virtualisation, federation and data sharing | Trade-offs and selection | 6 | Intermediate → advanced |
| Idempotency and deduplication | Identity, merge rules, safe replay | 7 | Intermediate → advanced |
| Source-to-target reconciliation | Checks, coverage, tolerances | 7 | Intermediate → advanced |
| Failure handling and recovery | Failure matrices, retries, backlog | 8 | Advanced |
| Integrated architecture selection and justification | Cross-topic case studies | 1–8 | Industry |

### 6.3 Strategy

1. Answer each topic's questions after the topic, closed-book first.
2. For every quantitative question, write the formula, the units, the
   assumptions and a sentence of interpretation.
3. For selection questions, write the requirement, source constraints,
   candidates, elimination reasons and accepted trade-offs.
4. For correctness questions, state which control detects which defect class
   and which it does not.
5. For failure questions, state detection, recovery, data impact and evidence.
6. Mark each answer correct / partly correct / wrong with a one-sentence
   reason; re-attempt after several days.
7. Keep integrated answers as written artefacts; they feed the project.
8. Have advanced and industry answers reviewed by another person.

### 6.4 Expected performance by level

| Level | Successful performance |
| --- | --- |
| Beginner | Accurate definitions; correct identification of mechanisms; no confusion between replication and backup, deduplication and idempotency, schema and contract |
| Intermediate | Mechanisms matched to source capability and consumer need; flows with explicit change detection; basic contracts and reconciliation designed |
| Advanced | Ordering, replay, duplication, compatibility and failure interactions analysed; transport guarantees separated from business correctness; trade-offs quantified |
| Industry application | Integrated, traceable cross-system design with contracts, controls, failure behaviour and validation that a reviewer can audit |

### 6.5 Evaluation criteria

| Criterion | What to check |
| --- | --- |
| Conceptual accuracy | Mechanisms and guarantees are described correctly |
| Pattern suitability | The choice follows source capability and consumer requirement |
| Correctness guarantees | Idempotency, deduplication, reconciliation and ordering are addressed and their limits stated |
| Explicit assumptions | Inputs, rates, limits and guarantees are labelled documented/assumed/unknown |
| Failure analysis | Each failure has detection, recovery and data-impact statements |
| Defensibility | Alternatives, evidence and revisit conditions are cited |

---

## 7. Project — Cross-system data integration design

Project file:
[`Projects/06-cross-system-data-integration-design.md`](Projects/06-cross-system-data-integration-design.md)
(currently empty; this section defines its intended content). The project index
is [`Projects/README.md`](Projects/README.md).

This is an **end-to-end integration architecture design exercise**, not a
diagram-drawing task or a connector implementation tutorial. The deliverable is
a defensible design with explicit patterns, contracts, flows, correctness
controls, failure behaviour and validation criteria.

How it uses the eight topics:

| Project part | Topics |
| --- | --- |
| Batch and incremental flows | 1 |
| Change-capture flows | 2 |
| API, file, connector flows | 3 |
| Event flows and message contracts | 4 |
| Data contracts and compatibility | 5 |
| Access and sharing alternatives | 6 |
| Idempotency, deduplication, reconciliation | 7 |
| Pattern selection and failure handling | 8 |

### 7.1 Project objective

You must demonstrate that you can:

- Analyse cross-system requirements and source capabilities.
- Choose suitable integration patterns per flow and justify them.
- Define data contracts with ownership and compatibility expectations.
- Document data flows, ordering, consistency and late-data handling.
- Specify idempotency, deduplication and reconciliation.
- Define failure behaviour, retries, checkpoints, replay and recovery.
- Define security, governance and operational validation.

The project stays at the **architecture design level**. It does not require
connector configuration, code, deployment, infrastructure automation or
benchmark execution.

### 7.2 Project scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. It runs a core ledger database, a cards
platform, a SaaS customer-relationship system, and receives daily files from a
payment-network partner. An analytical platform serves risk, finance and
regulatory reporting; a fraud service needs card events quickly; the compliance
team requires evidence that data in reports match the source.

> All details and numbers below are **illustrative assumptions**, not facts
> about any real organisation. You may substitute a real or realistic scenario
> (observing confidentiality) but must label what you observed versus what you
> assume. Use decimal units and consistent time bases.

**Business problem.** Integrations have grown ad hoc: nightly full copies strain
the ledger, the fraud service sees events hours late, schema changes break
consumers unannounced, duplicates appear after job restarts, and nobody can
prove source and target agree.

**Source systems and capabilities (assumed).**

| ID | System | Interfaces available | Notes |
| --- | --- | --- | --- |
| S1 | Core ledger database | Read replica; transaction log readable; no reliable last-modified on all tables | Peak write ~2,000 changes/s |
| S2 | Cards platform | Event publication; REST API for corrections | ~20,000 auth events/s at peak |
| S3 | SaaS CRM | REST API (paginated, 10 requests/s limit, daily quota); weekly bulk export | ~12 million customer-interaction records |
| S4 | Payment-network partner | Daily file drop with manifest | ~2,000,000 settlement records/day |

**Targets and consumers (assumed).**

| ID | Target / consumer | Needs |
| --- | --- | --- |
| T1 | Analytical platform (risk, finance, regulatory) | Complete, reconciled history; daily/hourly freshness |
| T2 | Fraud service | Card events within p95 ≤ 60 s; ordered per card |
| T3 | Contact-centre view | Current customer view; minutes of staleness acceptable |
| T4 | Regulatory reporting | Reconciled to source; evidence retained |

**Entities / events integrated.** Ledger entries and account changes; card
authorisation events; customer interaction records; settlement records;
customer profile changes.

**Volume and growth assumptions (illustrative).** Ledger changes ~5 million
rows/day; card events ~1 TB/day at peak rate profile; settlement files ~2 GB/day;
CRM ~12 million records with 3% monthly change; growth 20% per year.

**Freshness, latency, throughput (illustrative).** Fraud p95 ≤ 60 s; analytics
hourly for operational dashboards, daily for regulatory; settlement within two
hours of file arrival.

**Consistency and correctness (illustrative).** No loss and no duplication of
ledger and settlement records; per-card ordering for fraud; zero tolerance on
financial control totals.

**Security and governance (illustrative).** Personal data stays in a stated
jurisdiction; least-privilege credentials per flow; encryption in transit and at
rest; classification carried with data; lineage registered.

**Contract and compatibility (illustrative).** Producers own contracts;
consumers notified at least 30 days before breaking changes; compatibility
mode chosen per feed.

**Failure and recovery (illustrative).** Ledger feed recoverable from any
point within seven days; fraud feed tolerates consumer outage up to one hour
without data loss; every flow has an owner and an on-call route.

**In scope.** Pattern selection and design for flows S1→T1, S2→T2/T1, S3→T3/T1,
S4→T1/T4; contracts; correctness and recovery design; monitoring requirements.

**Out of scope.** Product selection, connector configuration, code, infrastructure
sizing, cloud-provider mapping (2D.8), detailed stream-processing design
(2D.9), platform build (2D.7), metadata tooling (2D.11).

### 7.3 Step-by-step project execution

For each step: **Purpose · Inputs · Actions · Questions to answer · Outputs ·
Validation.**

| Step | Purpose | Inputs | Actions | Questions to answer | Outputs | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define problem, scope, outcomes | Scenario | Write scope, objectives, exclusions | What is decided and what is not? | Scope and assumptions | Sponsor-role reviewer confirms |
| 2 | Identify systems, stakeholders, consumers | Scenario | Register sources, targets, owners, consumers | Who owns each system and consumes each feed? | System and stakeholder inventory | Every flow end has an owner or "unknown" |
| 3 | Inventory datasets, entities, events | Step 2; 2D.4 models | List assets with keys, grain, sensitivity | What identifies each record? | Source and target data inventory | Each asset has a key and a source |
| 4 | Characterise source capabilities and constraints | Step 2 | Document interfaces, change visibility, deletes, limits, windows | What can the source support, and at what load? | Source capability profile | Each limit has evidence or "unknown" |
| 5 | Gather integration requirements | Steps 1–3 | Write measurable functional and non-functional requirements | What must each consumer receive, how fast, how correct? | Integration requirements register | Each requirement testable and sourced |
| 6 | Define volume, freshness, latency, throughput, availability | Steps 3–5; 2D.2 method | Quantify with formulas and ranges | Which input dominates? | Workload and freshness requirements | Units, formulas, assumptions present |
| 7 | Identify candidate patterns per flow | Steps 4–6 | Shortlist plus simplest baseline | Is each feasible given the source? | Candidate list | Gate failures removed with reasons |
| 8 | Compare patterns | Steps 5–7; Section 7.5 | Matrix with evidence; criteria fixed first | Where is evidence weakest? | Pattern comparison matrix | Same criteria for every candidate |
| 9 | Select and justify pattern per flow | Step 8 | Decide, record alternatives | What are we accepting? | Pattern selection rationale (ADR form) | Cites criteria and evidence |
| 10 | Define mappings and transformation responsibility | Steps 3, 9 | Source-to-target mappings; where transformation occurs (ETL/ELT) | Who owns each transformation? | Mapping and flow descriptions | Every target field has a source or rule |
| 11 | Define data contracts and schemas | Steps 9–10; Topic 5 | Contract per feed: structure, semantics, quality, delivery, owner, compatibility mode | Who may change what, with what notice? | Data contracts and compatibility plan | Semantics and ownership present |
| 12 | Specify idempotency, deduplication, reconciliation | Steps 3, 9, 11; Topic 7 | Identity, merge, version rules; reconciliation levels and tolerances | What proves completeness and correctness? | Idempotency/dedup strategy; reconciliation plan | Coverage matrix with undetected classes stated |
| 13 | Identify failure modes; define retries, checkpoints, replay, recovery | Steps 9–12; Topic 8 | Failure matrix per component | How does each failure get detected and recovered? | Failure-mode and recovery matrix | Every component has detection and recovery |
| 14 | Document ordering, consistency, late data, partial failure | Steps 9, 12, 13 | State ordering scope, lateness policy, atomic publication | What can a consumer observe mid-failure? | Consistency notes | Each guarantee marked documented/assumed |
| 15 | Define security, access, governance | Steps 9–11 | Credentials, encryption, classification, retention, lineage | Who can access what, and how is it audited? | Security and governance considerations | Each control traced to a requirement |
| 16 | Define operational validation, monitoring, alerting | Steps 13–14 | Freshness, volume, lag, error, absence, reconciliation signals; owners | What tells us before consumers notice? | Operational validation requirements | Each alert has owner and action |
| 17 | Create logical architecture and data flow views | Steps 9–16 | Diagram and per-flow descriptions | Is every element justified? | Logical integration architecture | No unexplained element; legend and version |
| 18 | Validate against normal and failure scenarios | Step 17 | Walk ≥ 5 normal and ≥ 8 failure scenarios | Does the design behave as claimed? | Validation results | Each outcome explained |
| 19 | Document trade-offs, assumptions, questions, rejected alternatives | Steps 8–18 | Risk and trade-off register | What would change the design? | Trade-off and risk register | Each item linked to a finding |
| 20 | Produce final recommendation | All | Assemble; state conditional items | What is decided and what remains open? | Final architecture recommendation | Non-specialist can follow in ten minutes |

**Per-step guidance:**

1. State exclusions firmly; this project stops at design.
2. Include security, compliance and operations as stakeholders.
3. Identity of records is a design input, not an afterthought.
4. Mark unknown limits as unknown; do not invent source capabilities.
5. Write requirements as measurable statements (percentile, window, tolerance).
6. Show formulas and units; give low/expected/high where uncertain.
7. Always include the simplest adequate baseline.
8. Fix criteria and weights before scoring.
9. Specific rejection reasons; no "too complex".
10. Decide where transformation happens and who owns it.
11. Contracts include meaning, not only fields.
12. Say what each control does **not** catch.
13. Walk each component, including scheduler, credentials and registry.
14. Separate transport guarantees from business correctness.
15. Classification travels with data through landing and dead-letter stores.
16. Alert on absence and staleness, not only errors.
17. Label the view's level (logical, not physical).
18. Include a replay, a duplicate delivery, an out-of-order update and a
    schema-change scenario.
19. Record assumptions with owners.
20. State conditional decisions and the evidence that would settle them.

### 7.4 Required project deliverables

Deliverables are proportionate; related content is combined.

| # | Deliverable | Purpose | Minimum contents |
| --- | --- | --- | --- |
| D1 | Project scope and assumptions | Fix boundaries | Problem, objectives, in/out of scope, labelled assumptions |
| D2 | Stakeholder and system inventory | Who and what is involved | Systems, role (source/target), owners, interfaces, constraints, consumers |
| D3 | Source and target data inventory | What moves | Asset/event, key/identity, grain, size, change rate, sensitivity, owner |
| D4 | Integration requirements register | Measurable needs | REQ-n with metric, target, scope, method, source, priority |
| D5 | Workload and freshness requirements | Quantify demand | Volumes, rates, peaks, windows, formulas, units, ranges |
| D6 | Integration pattern comparison matrix | Transparent comparison | Criteria (gates, weights if used), evidence per candidate per flow |
| D7 | Pattern selection rationale per flow | Defend choices | Chosen pattern, rejected alternatives, assumptions, revisit triggers |
| D8 | Logical integration architecture diagram | Communicate | Systems, flows, mechanisms, contracts, control points, legend, version |
| D9 | Source-to-target data flow descriptions | Precise behaviour | Per flow: trigger, extraction, transformation owner, load, ordering, publication |
| D10 | Data contracts and schema compatibility plan | Controlled change | Contract per feed, compatibility mode, versioning, deprecation, enforcement points |
| D11 | Idempotency and deduplication strategy | Safe repetition | Identity, merge/dedup rules, version rules, side-effect handling |
| D12 | Reconciliation and data validation plan | Prove completeness | Levels, windows, tolerances, independence, report format, exception workflow, coverage matrix |
| D13 | Failure-mode and recovery matrix | Defined behaviour | Component/scenario, detection, data impact, recovery, idempotency/reconciliation need, owner, evidence |
| D14 | Security and governance considerations | Control | Credentials, encryption, access, classification, retention, lineage, audit |
| D15 | Operational validation requirements | Run it safely | Signals, thresholds, alerts, owners, runbooks, drills |
| D16 | Architecture trade-off and risk register | Honest limits | Trade-offs, risks, mitigations, owners, triggers |
| D17 | Final architecture recommendation | Sponsor readout | One to two pages: decisions, rationale, trade-offs, correctness claims, conditional items, next steps |

### 7.5 Suggested templates and fields

Use only fields that serve a purpose. Mark `Unknown` rather than inventing
capabilities, and carry `Source` and `Confidence` (documented / assumed /
unknown) where they apply.

**System inventory**

| Field | Purpose |
| --- | --- |
| System ID, name | Reference |
| Business purpose | Context |
| Data owner (if known) | Accountability |
| Source or target role | Direction |
| Available interfaces | Options |
| Data characteristics (volume, change rate, keys) | Sizing and identity |
| Constraints and dependencies (windows, limits, vendor) | Eliminates options |

**Integration flow inventory**

| Field | Purpose |
| --- | --- |
| Flow ID | Reference |
| Source system → target system | Scope |
| Data asset or event | Content |
| Integration pattern | Decision |
| Trigger or schedule | Timing |
| Expected volume (rate and size, with units) | Capacity |
| Freshness requirement (percentile, window) | Target |
| Transformation responsibility | Ownership |
| Contract reference | Agreement |
| Recovery strategy | Resilience |

**Data contract**

| Field | Purpose |
| --- | --- |
| Contract ID | Reference |
| Producer and consumers | Parties |
| Schema or payload definition reference | Structure |
| Field meanings (units, null meaning, allowed values) | Semantics |
| Required and optional attributes | Change cost |
| Compatibility expectations (mode, notice period) | Change control |
| Quality and delivery expectations | Trust |
| Ownership and change-management process | Governance |

**Failure and recovery matrix**

| Field | Purpose |
| --- | --- |
| Failure scenario | What breaks |
| Detection method | How we know |
| Potential data impact | Loss, duplication, delay |
| Retry or recovery approach | What we do |
| Idempotency requirement | Safe repetition |
| Reconciliation requirement | Proof of repair |
| Responsible owner | Accountability |
| Validation evidence | Proof it works (drill, test) |

**Pattern comparison criteria (use those relevant):** freshness fit,
throughput fit, correctness controls available, source impact, change/delete
visibility, ordering support, replay support, operational complexity, cost,
security and governance fit, contract support, vendor/lock-in risk.

### 7.6 Validation and quality assurance

| Check | How to verify |
| --- | --- |
| Every in-scope data flow has a purpose and an owner | D2/D3 cross-checked against D9 |
| Patterns match source capabilities and consumer requirements | D6 cites D4 and the source profile for every row |
| Data contracts are clear and compatible with expected change | Each contract has semantics, mode, notice and an owner; sample change classified |
| Freshness, throughput and correctness requirements are measurable | Each has metric, percentile, window, tolerance, method |
| Duplicate processing and replay considered | D11 covers each flow; replay scenario walked through |
| Reconciliation detects meaningful discrepancies | Inject a missing, a duplicate and a value-drift case on paper and show detection; coverage matrix lists undetected classes |
| Failure scenarios have detection and recovery | D13 covers every component, including scheduler, credentials and registry |
| Security and governance addressed | D14 maps each control to a requirement |
| Architecture is internally consistent | Every flow in D8 appears in D6/D7/D9 and vice versa |
| Recommendations traceable | Trace from three decisions to requirements and from three requirements to decisions |

### 7.7 Project completion gate

The project is complete only when **all** hold:

- [ ] D1–D17 exist, version-dated, with consistent IDs.
- [ ] **Requirements:** every flow has measurable freshness, throughput and
      correctness requirements; no requirement names a product.
- [ ] **Pattern selection:** each flow compares at least three feasible
      candidates including a simplest baseline; criteria and weights (if used)
      fixed and dated before scoring; gate failures recorded; selection cites
      source-capability evidence.
- [ ] **Contracts:** each feed has a contract covering structure, semantics,
      quality, delivery, ownership and compatibility mode; at least one
      structurally valid but semantically breaking change is identified and
      handled.
- [ ] **Correctness:** each flow has an identity definition, an idempotent load
      or processing rule, a dedup rule and a reconciliation design with stated
      tolerance and independence; the coverage matrix lists defect classes not
      detected.
- [ ] **Failure and recovery:** every component has at least one failure
      scenario with detection, data impact, recovery and owner; at least ten
      scenarios overall; recovery capacity checked with catch-up arithmetic for
      one backlog scenario.
- [ ] **Quantification:** all numeric claims carry units, formulas, assumptions
      and an illustrative label; a reviewer reproduces three figures.
- [ ] **Validation:** ≥ 5 normal and ≥ 8 failure scenarios (including duplicate
      delivery, out-of-order update, replay, schema change, source outage,
      incomplete file) are walked through with explained outcomes.
- [ ] **Security and governance:** each control traced to a requirement; no
      sensitive data left unclassified in landing or dead-letter stores.
- [ ] **Operations:** each alert has an owner and an action; absence and
      staleness are monitored; a failure drill with pass criteria is defined.
- [ ] **Traceability and defensibility:** trace tests pass; two reviewer
      challenges are answered from recorded evidence; an independent reviewer
      agrees the evidence supports the conclusions.

The existence of diagrams or documents is **not** sufficient.

### 7.8 Connection to subsequent modules

| Later module | How the project supports it | What belongs to that module |
| --- | --- | --- |
| 2D.7 Enterprise data platform and lakehouse | Ingestion zones, landing and quarantine areas, contract enforcement points, reconciliation hooks | Platform components, tenancy, service model |
| 2D.8 Cloud, hybrid and multi-cloud | Connectivity needs, residency constraints, managed-integration candidates | Service selection, networking, identity design |
| 2D.9 Streaming and real-time | Event contracts, partitioning, retention and replay requirements | Stream-processing design, state, delivery semantics in depth |
| 2D.10–2D.11 Governance, metadata, lineage, quality | Contracts, classification, lineage points, reconciliation evidence, identifier rules | Policy engines, catalogue tooling, entity resolution and master data |
| 2D.12 Reliability and disaster recovery | Failure matrix, replay and backfill procedures | DR strategy, drills, runbook engineering |
| 2D.14 Data access, serving, AI data | Feeds, freshness SLOs and contracts for downstream products | Serving architectures, feature and retrieval pipelines |

Do not extend this project into a production deployment.

---

## 8. Final learning assessment and completion checklist

Self-reported confidence is not sufficient; each row requires the stated
evidence.

| # | You can… | Evidence required for mastery |
| --- | --- | --- |
| 1 | Design batch and incremental ingestion approaches | Flow with change marker, watermark rule, rerun behaviour; extract-time and staleness worksheet reproduced by a reviewer |
| 2 | Explain CDC and database replication behaviour | Guarantee table separating documented/assumed/unknown; snapshot-plus-stream procedure; lag and catch-up worksheet |
| 3 | Choose suitable API, file or managed-connector approaches | Interface comparison citing source limits; failure table for unavailable API, incomplete file, stalled connector |
| 4 | Design streaming integration flows and message contracts | Contract with identity, time, key and version; partition and retention arithmetic; failure-point table |
| 5 | Define data contracts and schema compatibility expectations | Contract with semantics and ownership; change classification including a semantic change; evolution policy |
| 6 | Evaluate virtualisation, federation and data-sharing patterns | Comparison with source load and availability estimates; stated limitations; a case requiring materialisation |
| 7 | Design idempotency, deduplication and reconciliation controls | Identity and merge rules; reconciliation design with tolerance and independence; defect-to-control table |
| 8 | Select integration patterns based on explicit requirements | Selection table with requirement and source evidence, a baseline comparison and an ADR |
| 9 | Define failure handling, recovery and validation strategies | Failure matrix covering every component; monitoring specification; failure-drill plan with pass criteria |
| 10 | Produce and defend a cross-system integration architecture | D1–D17 and the project completion gate (Section 7.7) met; challenge round with two reviewer objections answered from recorded evidence |

Module complete when:

- [ ] All eight topic completion gates are signed off.
- [ ] `practice-questions.md` answered; wrong answers corrected and
      re-attempted.
- [ ] The project completion gate is met.
- [ ] You have presented the design and answered a reviewer's challenges without
      introducing unsupported claims.
- [ ] Open questions are logged for the next module (2D.7).

---

## 9. Where this module leads

Module 2D.7, **Enterprise Data Platform and Lakehouse Architecture**, takes the
ingestion mechanisms, contracts, correctness controls and failure designs
produced here and places them inside a platform: ingestion and storage zones,
medallion-style layers, catalogues and metastores, self-service capabilities,
tenant isolation and platform service levels.
