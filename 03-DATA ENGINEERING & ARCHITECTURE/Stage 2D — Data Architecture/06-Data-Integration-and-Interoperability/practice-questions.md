# Practice Questions — Data Integration and Interoperability

**Roadmap location:** Stage 2D — Data Architecture / `06-Data-Integration-and-Interoperability/`  
**Assessment scope:** Topics 1–8, from beginner concepts to integrated industry design  
**Scenario:** Northbridge Bank is fictional. All figures, rates, service targets, and operational conditions in this assessment are illustrative assumptions, not benchmarks or vendor guarantees.

> **How to use this file:** Attempt the questions closed-book after studying each topic. Then compare your work with the answer key, mark each answer **correct / partly correct / wrong**, record the reason, and retry missed questions after several days. For calculations, show formulas, units, assumptions, and interpretation. For architecture questions, state requirements, source/consumer capabilities, alternatives, rejected options, trade-offs, controls, owners, and evidence.

## Contents

- [1. Source basis and scope](#1-source-basis-and-scope)
- [2. Assessment instructions and scoring](#2-assessment-instructions-and-scoring)
- [3. Coverage map](#3-coverage-map)
- [Part I — Question Bank](#part-i--question-bank): Topics 1–8, advanced extensions, and integrated industry cases
  - [Integrated industry case studies](#integrated-industry-case-studies-unscored-practice)
- [Part II — Answer Key and Explanations](#part-ii--answer-key-and-explanations)
- [Part III — Assessment Review and Remediation](#part-iii--assessment-review-and-remediation)
- [Scoring rubric by learning level](#4-scoring-rubric-by-learning-level)
- [Topic-level scorecard](#5-topic-level-scorecard)
- [Remediation map](#6-remediation-map)
- [Final readiness checklist](#7-final-readiness-checklist-and-module-wide-completion-evidence)

## 1. Source basis and scope

The authoritative scope is `roadmap-Data-Integration-and-Interoperability.md`, including its eight topic sequences, Section 6 practice-question categories, Section 7 cross-system project, and Section 8 final learning assessment. The project tree places this file alongside the eight numbered lessons and `Projects/06-cross-system-data-integration-design.md`.

The assessment follows the roadmap's progression:

1. Integration terminology and pattern identification.
2. ETL/ELT and incremental ingestion.
3. CDC and replication behaviour.
4. API, file, and managed-connector selection.
5. Streaming and message contract design.
6. Data contract and schema compatibility analysis.
7. Virtualization, federation, and data sharing.
8. Idempotency, deduplication, and source-to-target reconciliation.
9. Failure handling and recovery.
10. Integrated architecture selection and justification.

The questions are vendor-neutral. Any numbers and named systems are illustrative. Where a source capability is not stated, treat it as **unknown** and explain how you would verify it rather than assuming a guarantee.

## 2. Assessment instructions and scoring

### 2.1 Recommended workflow

1. Complete the questions for a topic after studying that lesson.
2. Attempt the questions without the answer key.
3. Show your working for every calculation and state any assumptions.
4. For a pattern-selection answer, identify the business need, measurable SLOs, source capabilities, consumer requirements, baseline, alternatives, trade-offs, and revisit triggers.
5. For a failure answer, include detection, data/consumer impact, containment, recovery, owner, and correctness evidence.
6. Compare with the answer key. Accept defensible alternatives when their assumptions and evidence are explicit.
7. Reattempt incorrect or incomplete answers after a few days.
8. Use the integrated-design answers as inputs to `Projects/06-cross-system-data-integration-design.md`.

### 2.2 Point model

There are **40 scored questions**: five per topic, for 80 points total. Each topic also has an **unscored Advanced extension** (`T1-A1` through `T8-A1`) so the question bank separately exercises all four roadmap levels: Beginner, Intermediate, Advanced, and Industry Application. The scored questions are weighted to keep the score comparable across topics; the unscored extensions and integrated case studies are required practice but do not change the 80-point total. The Northbridge case and module-wide project requirements are assessed particularly heavily in Topic 8.

| Question type per topic | Number per topic | Points each | Points per topic |
|---|---:|---:|---:|
| Beginner: MCQ / classification | 2 | 1 | 2 |
| Intermediate: short answer / comparison / calculation | 2 | 2 | 4 |
| Industry-application case | 1 | 4 | 4 |
| **Total** | **5** |  | **10** |

**Maximum score:** \(8 \times 10 = 80\) points.

These thresholds are assessment-design choices, not roadmap-mandated requirements:

- **Ready to progress:** at least 64/80 (80%) overall, at least 60% of each topic's 10 points, and a satisfactory Topic 8 integrated-design response.
- **Developing:** 56–63 points, or overall 64+ but below 60% in any topic. Review weak areas and retry them.
- **Not yet ready:** below 56 points. Revisit the relevant lessons and attempt the assessment again.

For open-ended questions, award full credit for a technically sound alternative that states assumptions, trade-offs, limitations, and validation evidence. Do not award full credit for a correct pattern name without reasoning.

### 2.3 Scoring open-ended answers

- **Full points:** technically correct, directly answers the question, states material assumptions, explains trade-offs, and includes relevant controls/evidence.
- **Half points:** broadly correct but omits a significant condition, failure mode, or justification.
- **Zero points:** relies on an unsupported guarantee, ignores a stated requirement, uses incorrect calculations, or does not address the question.
- For multi-part advanced and industry questions, allocate points across the explicitly listed criteria in the answer key.

## 3. Coverage map

| Roadmap objective / required evidence | Question IDs | Answer-key location |
|---|---|---|
| Identify integration mechanisms and distinguish interfaces, mechanisms, contracts, replication and backup | T1-Q1, T1-Q2, T2-Q1, T3-Q1, T4-Q1, T5-Q1, T6-Q1 | Part II → Topics 1–6 |
| Design batch and incremental ingestion; change markers, watermarks, reruns, deletes, extract-time and staleness | T1-Q3, T1-Q4, T1-A1, T1-Q5 | Part II → Topic 1 |
| Explain CDC types, snapshot/stream seam, ordering, lag, restart, retention, and guarantee boundaries | T2-Q2, T2-Q3, T2-Q4, T2-A1, T2-Q5, IC-1 | Part II → Topic 2; IC-1 |
| Choose APIs, files, and managed connectors; handle pagination, limits, completeness, credentials, and stalls | T3-Q2, T3-Q3, T3-Q4, T3-A1, T3-Q5, T8-Drill-1, IC-1 | Part II → Topic 3; Topic 8 drill; IC-1 |
| Design event/message contracts; event identity, time, key, ordering, retention, replay, and consumer recovery | T4-Q2, T4-Q3, T4-Q4, T4-A1, T4-Q5 | Part II → Topic 4 |
| Define contracts; distinguish schema and contract; classify structural vs semantic changes; plan compatibility and migration | T5-Q2, T5-Q3, T5-Q4, T5-A1, T5-Q5, IC-2 | Part II → Topic 5; IC-2 |
| Compare virtualization/federation/sharing with materialization; analyze source load, availability, consistency, governance, and revisit triggers | T6-Q2, T6-Q3, T6-Q4, T6-A1, T6-Q5 | Part II → Topic 6 |
| Define idempotency, deduplication, identity, merge/version rules, safe replay, reconciliation independence and blind spots | T7-Q1, T7-Q2, T7-Q3, T7-Q4, T7-A1, T7-Q5, IC-2 | Part II → Topic 7; IC-2 |
| Classify failures; design bounded retries, timeout semantics, checkpoint/replay, backlog recovery, monitoring and failure evidence | T8-Q1, T8-Q2, T8-Q3, T8-Q4, T8-A1, T8-Q5, T8-Drill-1, IC-1 | Part II → Topic 8; IC-1 |
| Produce pattern-selection table, baseline comparison, contract summary, failure matrix, monitoring spec, failure-drill plan and ADR | T1-Q5, T2-Q5, T3-Q5, T4-Q5, T5-Q5, T6-Q5, T7-Q5, T8-Q5, IC-1, IC-2 | Part II → Topic-specific Q5 rubrics; IC-1/IC-2 |
| Apply Northbridge case context and cross-topic architecture reasoning | All topic Q5 questions; especially T8-Q5, IC-1, IC-2 | Part II → all Topic Q5 answers; IC-1/IC-2 |
| Quantitative work with formulas, units, assumptions, and interpretation | T1-Q4, T1-A1, T2-Q4, T3-Q4, T4-Q4, T6-Q4, T7-Q4, T8-Q3, T8-Q4, T8-A1 | Part II → corresponding topic answers |
| Code reading/writing and failure-boundary reasoning | T7-Q3, T8-Q2, T8-Q3, T8-Drill-1 | Part II → Topic 7; Topic 8 |
| Explicit assumptions, documented/assumed/unknown guarantees, and defensible alternatives | T2-Q5, T3-Q5, T5-Q5, T6-Q5, T8-Q5, IC-1, IC-2 | Part II → corresponding topic answers; IC-1/IC-2 |

### Topic-level objective traceability

| Topic | Roadmap objectives and required evidence | Question IDs | Answer-key location |
|---|---|---|---|
| 1 — Batch ETL/ELT and incremental ingestion | Batch use cases; ETL vs ELT and full vs incremental; change markers/watermarks; extract → land → transform → load; scheduling, throughput and freshness; late updates, safe reruns, deletes, backfills and source impact | T1-Q1–T1-Q5, T1-A1 | Part II → Topic 1 |
| 2 — CDC and database replication | CDC vs periodic extraction; replication vs backup; log/trigger/query capture; inserts, updates, deletes and ordering; snapshot/stream seam; lag, schema changes, duplicates, restarts, replay, retention and checkpoints; documented/assumed/unknown guarantees | T2-Q1–T2-Q5, T2-A1, IC-1 | Part II → Topic 2; IC-1 |
| 3 — APIs, files and managed connectors | Request/response vs bulk; authentication/authorisation; pagination, quotas and source limits; file format, arrival and completeness; manifests and checksums; incremental extraction and checkpoints; retries/partial failures; connector visibility, security, maintenance and ownership | T3-Q1–T3-Q5, T3-A1, T8-Drill-1, IC-1 | Part II → Topic 3; Topic 8 drill; IC-1 |
| 4 — Streaming events and message contracts | Producer/consumer/broker concepts; event identity and contract fields; event vs processing time; key/partition and ordering scope; retention/replay; consumer progress and recovery; poison events/DLQ; transport vs business correctness; partition and storage arithmetic | T4-Q1–T4-Q5, T4-A1 | Part II → Topic 4 |
| 5 — Data contracts, schema registry and compatibility | Producer/consumer responsibilities; structure, semantics, quality and delivery; schema vs registry; backward/forward/full direction; required/optional fields, names, types, enum and meaning changes; transitive scope; validation, ownership, consumer impact, migration, deprecation and rollback | T5-Q1–T5-Q5, T5-A1, IC-2 | Part II → Topic 5; IC-2 |
| 6 — Virtualization, federation and data sharing | Logical access vs physical movement; source/query dependencies; freshness, source load, latency, availability and consistency; governance/access ownership; virtualization vs materialization/replication; availability and query-load estimates; limitations and revisit triggers | T6-Q1–T6-Q5, T6-A1 | Part II → Topic 6 |
| 7 — Idempotency, deduplication and reconciliation | Distinguish duplicate delivery/data/processing; stable identity and namespace; version-aware merge; retry/replay safety; conflicts and late updates; counts/totals/checksums/key-level checks; independent controls, tolerances, blind spots and exception evidence | T7-Q1–T7-Q5, T7-A1, IC-2 | Part II → Topic 7; IC-2 |
| 8 — Pattern selection and failure handling | Requirement-driven candidate selection; simplest adequate baseline and rejected alternatives; timeout/retry/backoff budgets; source/transport/processing/target/control-plane failures; checkpoint/replay/quarantine; backlog and catch-up; monitoring owner/action; failure drills, reconciliation, ADR and revisit triggers | T8-Q1–T8-Q5, T8-A1, T8-Drill-1, IC-1 | Part II → Topic 8; IC-1 |

---

# Part I — Question Bank

## Topic 1 — Batch ETL/ELT and Incremental Ingestion

### T1-Q1 — Beginner, multiple choice (1 point)

A source table contains customer records. A nightly job copies the complete table into an analytical landing area, then transforms it in the analytical platform. Which statement is best?

A. It is incremental ETL because the job runs nightly.  
B. It is full-load ELT if transformation occurs after data land in the target environment.  
C. It is CDC because it copies a database table.  
D. It is database backup because the source table is copied.

### T1-Q2 — Beginner, multiple choice (1 point)

Which is the strongest reason to use an incremental ingestion watermark?

A. It guarantees that no source record can ever be deleted.  
B. It records a progress boundary so the next run can request a limited changed-data scope.  
C. It proves that all downstream business rules are correct.  
D. It removes the need for a stable record identity.

### T1-Q3 — Intermediate, short answer (2 points)

A source table exposes `updated_at`, but updates may arrive late and timestamps have only one-second precision. Explain two risks of using `updated_at > last_watermark` and propose a safer extraction and watermark-advancement approach.

### T1-Q4 — Intermediate, calculation (2 points)

**Illustrative assumptions:** A source has 8,000,000 rows. Average serialized row size is 500 bytes. A full extract reads all rows. An incremental extract reads 4% of rows on a typical day. Ignore protocol and index overhead. Use decimal units: \(1\text{ GB}=10^9\) bytes.

1. Calculate the approximate full-extract volume in GB.
2. Calculate the typical incremental volume in GB.
3. State one reason these figures are not sufficient by themselves to select a pattern.

### T1-A1 — Advanced extension (unscored)

Use the payload estimates from T1-Q4. Assume sustained payload transfer throughput is 100 MB/s (decimal units), the incremental job runs hourly, each run's source cutoff is at its start, and publication follows transfer immediately. Ignore queueing, transformation, retries, and source-query overhead. Estimate (a) ideal full-load transfer time, (b) ideal incremental transfer time, and (c) the approximate worst-case visibility delay for a change that becomes eligible just after a run's cutoff. Explain why this is not an end-to-end freshness guarantee, and name two controls for a 90-day backfill that must protect source workload and preserve correctness.

### T1-Q5 — Industry application (4 points)

Northbridge's ledger has no reliable `last_modified` field on all tables. Nightly full scans strain the source. Analytics requires hourly operational freshness and daily reconciled history. Propose a design decision process. Include a baseline, candidate patterns, what must be verified, how deletes/reversals are handled, safe reruns, and evidence of completeness. Do not assume CDC is available merely because the source is a database.

## Topic 2 — Change Data Capture and Database Replication

### T2-Q1 — Beginner, multiple choice (1 point)

Which statement best distinguishes replication from backup?

A. Replication always provides an immutable historical archive.  
B. Backup and replication are identical because both create copies.  
C. Replication maintains another copy for a stated use; backup is intended to support recovery from loss/corruption and needs its own retention and restore strategy.  
D. A replicated database cannot contain source errors.

### T2-Q2 — Beginner, multiple choice (1 point)

A CDC change record commonly needs which information to support safe downstream application?

A. Only the current wall-clock time.  
B. Operation type, stable key, source ordering/position metadata, and relevant values or change representation.  
C. Only the target table name.  
D. Only a row count per minute.

### T2-Q3 — Intermediate, short answer (2 points)

Explain the snapshot-plus-stream seam in CDC. What can go wrong if a snapshot is taken and ongoing change capture starts independently without a coordinated boundary? Briefly distinguish log-based, trigger-based, and query-based CDC by one important trade-off or limitation each.

### T2-Q4 — Intermediate, calculation (2 points)

**Illustrative assumptions:** A CDC consumer processes 900 changes/second while new changes arrive at 700 changes/second. At the start of recovery, its backlog is 360,000 changes. Assume stable rates and ignore retries, partition skew, and processing variance.

1. Calculate the net catch-up rate.
2. Calculate catch-up time in seconds and minutes.
3. What happens if processing capacity falls to 650 changes/second while arrivals remain 700/second?

### T2-A1 — Advanced extension (unscored)

A CDC consumer is offline for 36 hours, but the source log retains only 24 hours. On restart, the last committed source position has expired. Explain why blindly resuming or skipping to the earliest retained position cannot prove completeness. Propose a recovery plan, including reinitialisation or re-snapshot options, delete handling, reconciliation scope, and evidence required before declaring recovery complete.

### T2-Q5 — Industry application (4 points)

Northbridge can read a transaction log, but the team has not confirmed log retention, delete representation, transaction ordering, snapshot consistency, or failover behaviour. Write a concise CDC go/no-go checklist and recovery plan. Separate documented guarantees, assumptions, and unknowns. Name at least three correctness checks.

## Topic 3 — APIs, Files, and Managed Connectors

### T3-Q1 — Beginner, multiple choice (1 point)

A partner sends a daily bulk settlement export. Which design gives the strongest initial evidence that the delivery is complete?

A. Accept the file as soon as its name appears in a directory.  
B. Check only that the file can be opened.  
C. Use an agreed manifest with expected file identity/counts or control totals, checksum where applicable, schema/version, and an explicit arrival/completion convention.  
D. Retry the file load forever if any row fails.

### T3-Q2 — Beginner, multiple choice (1 point)

Which statement about a managed connector is most accurate?

A. It removes the need for monitoring, schema review, and recovery planning.  
B. It can reduce custom integration code, but its capabilities, checkpoint/retry behaviour, error visibility, upgrades, and ownership still need review.  
C. It guarantees end-to-end exactly-once business effects for every target.  
D. It is always cheaper than a custom integration.

### T3-Q3 — Intermediate, short answer (2 points)

An API returns 500 records per page and limits the client to 10 requests/second. Explain how pagination, rate limits, checkpoints, and changing source data can affect completeness. Name two controls for safe recovery after a partial extraction.

### T3-Q4 — Intermediate, calculation (2 points)

**Illustrative assumptions:** An API export contains 75,000 records, page size is 500, and the sustainable request budget is 5 requests/second. Each page requires one request. Ignore retries and extra metadata requests.

1. How many page requests are required?
2. What is the theoretical lower bound imposed by the rate budget?
3. If each serial request takes 250 ms, what is the approximate serial request-latency total, and why might the actual duration differ?

### T3-A1 — Advanced extension (unscored)

Two independent symptoms occur: (1) the partner's expected daily settlement file has not arrived by its deadline; (2) a managed connector reports “running” but its durable checkpoint has not advanced for 45 minutes. For each, state the detection signal, immediate safe action, likely owner, recovery path, and correctness evidence. Explain why file-name presence or a green connector status alone is insufficient.

### T3-Q5 — Industry application (4 points)

Northbridge's CRM is API-only. It has paginated results and a documented rate limit, but it is not yet known whether the API provides a reliable change token or exposes deletes. Compare incremental API extraction, periodic full snapshot comparison, and a managed connector. Recommend a conditional approach, list unknowns to verify, and specify what happens when the API is unavailable, a page is repeated, credentials expire, or an extraction is incomplete.

## Topic 4 — Streaming Events and Message Contracts

### T4-Q1 — Beginner, multiple choice (1 point)

Which statement is correct?

A. An event and a command are interchangeable terms in every architecture.  
B. A broker acknowledgement proves that a consumer's downstream business effect happened exactly once.  
C. An event records something that happened; a command requests an action; a current-state record describes state at a point in time.  
D. Partitioning guarantees global order across all events.

### T4-Q2 — Beginner, multiple choice (1 point)

If events must be ordered per account, which design principle is most relevant?

A. Use a stable account-related partition key and verify the platform's ordering scope; do not assume global ordering.  
B. Randomize the key so events spread evenly.  
C. Use processing time as the only event identity.  
D. Disable all replay.

### T4-Q3 — Intermediate, short answer (2 points)

List at least six fields or contract properties useful in a production event message. Explain the difference between event time and processing time and why both can matter.

### T4-Q4 — Intermediate, calculation (2 points)

**Illustrative assumptions:** A stream receives 400 events/second. Average retained event size is 2 KB (use 1 KB = 1,000 bytes for this exercise). Retention is 3 days. Ignore replication, indexes, compression, metadata overhead, and storage-system overhead.

1. Estimate raw payload storage for three days in GB.
2. State two reasons real storage requirements could be higher or lower.
3. If replay capacity is 800 events/second while new events continue at 400/second, how long would a backlog of 2,880,000 events take to clear?

### T4-A1 — Advanced extension (unscored)

A stream receives 20,000 events/second overall and can process 25,000 events/second in aggregate, but one hot partition receives 8,000 events/second and its assigned consumer can process only 5,000 events/second. Events must remain ordered per card. If the planning target is no more than 2,500 events/second per partition, calculate the theoretical minimum partition count for aggregate traffic. Then explain the hot-partition backlog, why aggregate capacity is misleading, and two options to investigate without silently breaking the ordering contract. State what metrics would validate the chosen option.

### T4-Q5 — Industry application (4 points)

Design the logical contract and recovery behaviour for Northbridge card-authorisation events consumed by a fraud service. Assume the consumer needs p95 visibility within 60 seconds and per-card ordering. Include identity, key, timestamps, schema/version, duplicate and out-of-order handling, retention/replay, poison events, monitoring, and at least one limitation of any “exactly-once” claim.

## Topic 5 — Data Contracts, Schema Registry, and Compatibility

### T5-Q1 — Beginner, multiple choice (1 point)

Which statement best distinguishes a schema from a data contract?

A. A schema always includes ownership, delivery SLOs, and incident escalation.  
B. A schema describes structure; a contract can also define semantics, quality, delivery expectations, ownership, and change policy.  
C. A schema registry automatically understands all business semantics.  
D. A contract is only a JSON file and has no operational implications.

### T5-Q2 — Beginner, multiple choice (1 point)

A producer changes a field's business meaning from “available balance” to “ledger balance” but keeps the same field name and numeric type. What is the best classification?

A. Guaranteed backward-compatible because the type is unchanged.  
B. A semantic change that requires contract review and consumer-impact analysis even if structural checks pass.  
C. Not a change because the schema is unchanged.  
D. Automatically safe if a schema registry is used.

### T5-Q3 — Intermediate, short answer (2 points)

Explain backward, forward, and full compatibility in terms of old/new readers and writers. State why compatibility direction must be evaluated against the actual format, serializer/deserializer, and registry policy.

### T5-Q4 — Intermediate, classification (2 points)

For each change, classify it as likely **structural risk**, **semantic risk**, or **context-dependent**, and state one required check:

1. Add an optional field with a documented default.
2. Rename a field consumed by downstream reports.
3. Keep a field's type but change its currency unit from dollars to cents.
4. Add a new enum value consumed by a strict parser.

### T5-A1 — Advanced extension (unscored)

A registry's configured policy accepts schema v3 as compatible with v2, but v3 is not compatible with v1. Explain the difference between a non-transitive check against the latest version and a transitive check against earlier versions. State why exact mode names and behaviour must be verified for the chosen registry/format, and identify one consumer-migration risk that structural compatibility does not address.

### T5-Q5 — Industry application (4 points)

Northbridge publishes an `AccountChanged` event to analytics, fraud, and customer-service consumers. Propose a contract and evolution policy. Include ownership, identity, semantics, schema versioning, compatibility checks, a semantic-breaking-change case, consumer impact analysis, migration/deprecation, rollback, and what the registry can and cannot enforce.

## Topic 6 — Data Virtualization, Federation, and Data Sharing

### T6-Q1 — Beginner, multiple choice (1 point)

Which statement is most accurate?

A. Data sharing always means copying a dataset into a new database.  
B. Virtualization/federation can provide query-time access to source data; data sharing describes a governed producer-to-consumer access arrangement and may use different technical mechanisms.  
C. Federation guarantees a consistent point-in-time snapshot across every source.  
D. Materialization never creates freshness lag.

### T6-Q2 — Beginner, multiple choice (1 point)

Which consumer is the strongest initial candidate for virtualization/federation?

A. A high-volume dashboard queried continuously by thousands of users against fragile operational databases.  
B. A regulatory report requiring reproducible source snapshots and exact reconciliation, without any materialized data.  
C. An analyst performing occasional exploratory queries over small result sets where source load, access, latency, and consistency are acceptable.  
D. A real-time fraud system that cannot tolerate source outages.

### T6-Q3 — Intermediate, short answer (2 points)

Compare virtualization/federation with materialized replication on freshness, source load, consumer availability, consistency, storage duplication, and operational responsibility. Give one condition that would trigger a change from query-time access to materialization.

### T6-Q4 — Intermediate, calculation (2 points)

**Illustrative assumptions:** A query requires three serial dependencies with independent availability estimates: source A = 99.9%, source B = 99.5%, and federation layer = 99.8%. Assume the query succeeds only if all three are available.

1. Estimate chain availability by multiplying the probabilities.
2. Express the result as a percentage to two decimal places.
3. State why this is only a simplifying model and how materialization may change the consumer-visible failure mode.

### T6-A1 — Advanced extension (unscored)

Use the simplified chain-availability result from T6-Q4 (about 99.20%). Assume 40 analysts each issue 3 dashboard queries per minute and each query fans out to all 3 sources; estimate source-query requests per minute. The consumer's target is 99.9% availability and it also requires reproducible month-end results, but the source systems cannot provide a shared cross-source snapshot. Recommend an access pattern or combination, state which requirement query-time federation cannot satisfy under the assumptions, and distinguish technical access from governed data-sharing responsibilities. Name the evidence needed to validate the recommendation.

### T6-Q5 — Industry application (4 points)

Northbridge contact-centre staff need a current customer-plus-account view. They run occasional interactive lookups, but account databases are sensitive and have limited query capacity. Recommend whether to start with federation, materialization, governed data sharing, or a combination. Define access controls, audit, consistency/freshness expectations, source-load protection, failure behaviour, assumptions, rejected alternatives, and revisit triggers.

## Topic 7 — Idempotency, Deduplication, and Reconciliation

### T7-Q1 — Beginner, multiple choice (1 point)

Which statement is correct?

A. Deduplication proves that no source records were lost.  
B. Idempotency makes repeating an operation safe within a defined boundary; deduplication identifies repeated logical records; reconciliation compares source, target, and business expectations for a defined scope.  
C. Reconciliation is unnecessary if a broker provides at-least-once delivery.  
D. Matching row counts proves values and business meanings are correct.

### T7-Q2 — Beginner, multiple choice (1 point)

A target receives two events with the same event ID but different payloads. What is the strongest default response?

A. Silently keep whichever arrived last.  
B. Treat the identity conflict as an exception, preserve evidence, and investigate producer identity/contract rules; do not silently merge contradictory payloads.  
C. Delete both records and advance the checkpoint.  
D. Assume the later event is correct because it arrived later.

### T7-Q3 — Intermediate, code reading and repair (2 points)

Review this illustrative Python-like function:

```python
def apply_update(current, incoming):
    # Both records contain account_id, version, and balance.
    if current is None or incoming["account_id"] == current["account_id"]:
        return incoming
    return current
```

1. Identify the correctness defect for an account-update stream.
2. Describe the version/identity rule needed to repair it.
3. Provide a corrected implementation or precise pseudocode, including what to do when the same identity and version have conflicting values.

Treat the snippet as code to reason about; no execution is required.

### T7-Q4 — Intermediate, calculation and diagnosis (2 points)

**Illustrative example:** Source and target each contain 10,000 transaction rows and total $8,500,000. Twenty records have been mapped to the wrong account, preserving the grand count and amount. Account-level controls show:

| Account | Source count | Target count | Source total | Target total |
|---|---:|---:|---:|---:|
| A | 6,000 | 5,980 | $5,100,000 | $5,050,000 |
| B | 4,000 | 4,020 | $3,400,000 | $3,450,000 |

1. Calculate target-minus-source count and amount deltas for A and B, plus the overall deltas.
2. Explain why the grand count and total checks fail to detect the mapping defect.
3. Name two further checks and one limitation of each.

### T7-A1 — Advanced extension (unscored)

A reconciliation report shows equal source/target counts and equal grand totals. A whole-file checksum also matches the landed source file and its archived copy. Name three defect classes these checks still may not detect after transformation, and propose a layered set of partly independent controls. For each control, state at least one blind spot; do not claim any single check proves all business correctness.

### T7-Q5 — Industry application (4 points)

A Northbridge payment event times out after the target may have committed. A retry arrives. Design safe handling. Define identity, idempotency boundary, version/merge behaviour, checkpoint order, reconciliation controls, exception workflow, and evidence proving one intended business effect. Explain why “deduplicate by timestamp” is inadequate.

## Topic 8 — Integration Pattern Selection and Failure Handling

### T8-Q1 — Beginner, multiple choice (1 point)

Which is the best default policy for a deterministic schema-validation error?

A. Retry forever with no delay.  
B. Quarantine or stop the affected scope, alert the contract owner, and retry only after the invalid input or rule is corrected.  
C. Ignore the record and advance progress without recording it.  
D. Increase concurrency until the schema passes.

### T8-Q2 — Beginner, classification (1 point)

Classify each response as **retry with bounded backoff**, **quarantine/stop for correction**, or **investigate outcome before retry**:

1. Temporary network error during a read request.
2. Malformed record that violates the agreed schema.
3. Timeout after a non-idempotent external create may have committed.

### T8-Q3 — Intermediate, calculation and diagnosis (2 points)

Three integration layers each allow five retries after the initial attempt, for six attempts per layer. Under the simplifying assumption that every attempt at one layer can trigger the next layer, calculate (a) attempts at the final layer and (b) total attempts across all three layers. Explain one control that reduces retry amplification.

### T8-Q4 — Intermediate, short answer (2 points)

A consumer is down for 20 minutes. New events arrive at 600 events/second. On recovery, it can process 900 events/second while new events continue arriving.

1. Calculate backlog at recovery.
2. Calculate net catch-up rate and catch-up time.
3. Name two conditions that could make this estimate optimistic in a real system.

### T8-A1 — Advanced extension (unscored)

A client allows six retries after the initial failed attempt. Use capped exponential backoff with no server-provided `Retry-After`: retry number \(n\) has a delay bound \(d_n=\min(30,1\times2^{n-1})\) seconds, and full jitter selects a wait uniformly from zero to that bound. Calculate each retry's maximum delay and the maximum total wait across six retries. Estimate expected total wait if each jitter draw is independent and uniform. Explain why the retry budget still needs a deadline and an idempotency/outcome rule.

### T8-Q5 — Industry application / integrated design (4 points)

Prepare a concise but reviewable integration recommendation for these illustrative Northbridge flows:

- Ledger → analytics: hourly operational freshness, daily reconciled history; source has a readable transaction log but log retention and delete semantics are not yet verified.
- Card events → fraud: event visibility p95 ≤ 60 seconds; per-card ordering; replay required after outages.
- Partner settlement → finance: daily bulk file, complete delivery and audit evidence required.
- CRM → customer domain: API-only, paginated, rate-limited; reliable change token and delete behaviour unknown.

Your response must include:

1. Measurable requirements and assumptions/unknowns.
2. Source and consumer profiles.
3. Selected candidate pattern and simplest adequate baseline for each flow.
4. At least one rejected alternative per flow with rationale.
5. Contract and identity assumptions.
6. Normal flow and key failure boundaries.
7. Retry, checkpoint, replay, quarantine, and reconciliation controls.
8. Monitoring signals with an owner/action.
9. A failure matrix with at least five distinct component/failure rows across the flows.
10. One catch-up calculation or capacity estimate.
11. ADR fields: decision, alternatives, trade-offs, risks, revisit triggers, and validation evidence.
12. A clear separation of known, assumed, and unknown facts.

### T8-Drill-1 — Unscored failure-classification exercise (practice required)

For each failure, classify the primary category (**source, transport, processing, target, control plane, or operator/configuration**) and choose a default response (**bounded retry, quarantine/stop, investigate outcome, or escalate/remediate**). State one detection signal for at least five cases.

1. Source database is unavailable during extraction.
2. Source query latency rises above its normal range.
3. Network connection drops during an API read.
4. API returns a documented throttling response.
5. API token expires and requests return authorization failures.
6. A page cursor repeats and returns overlapping records.
7. A partner file appears before upload completion.
8. File checksum does not match the manifest.
9. A required field is missing from an incoming record.
10. A schema change introduces an unrecognised enum value.
11. Transformation code raises an exception for one poison record.
12. Processing workers exhaust memory during a large batch.
13. Target database is temporarily unavailable.
14. Target constraint rejects a deterministic invalid row.
15. Target write may have committed, but the acknowledgement times out.
16. A checkpoint advances before durable target publication.
17. A schema registry/control-plane dependency is unreachable.
18. A scheduler misses a scheduled run.
19. An operator deploys an incorrect source filter.
20. A replay is launched against the wrong offset/time window.
21. The expected daily settlement file has not arrived by its agreed deadline.
22. A managed connector reports healthy but its checkpoint has not advanced for 45 minutes.
23. The source log retention window has expired before the CDC consumer recovers.

This drill is not included in the 80-point score. It is required practice because the roadmap explicitly asks learners to classify failures and choose retry, quarantine, investigation, or escalation. The three added cases explicitly test missing-file detection, stalled-connector detection, and source-log retention expiry.

## Integrated industry case studies (unscored practice)

### IC-1 — Month-end recovery collision

During month-end close, the ledger CDC consumer has been offline for 36 hours while source-log retention is only 24 hours; the settlement file is missing after its delivery deadline; and the CRM connector status is green but its checkpoint is unchanged. For each flow, classify what is known versus unknown, prioritise the immediate response, state whether simple resume/retry is safe, and list the evidence required before publishing recovered data. Your answer must cover source/transport/control-plane boundaries, owner, data impact, recovery, and reconciliation.

### IC-2 — Compatible schema, incorrect business result

Northbridge's producer changes an `amount` field from minor currency units to major currency units but retains the same numeric type. A registry compatibility check passes, and source/target row counts match after a replay. Explain why neither result proves correctness; propose the contract/change-control response, a safe consumer migration, and reconciliation checks that could expose the semantic error.

These case studies do not add points to the 80-point scored assessment. Their model responses appear in Part II.

---

# Part II — Answer Key and Explanations

## Topic 1 — Batch ETL/ELT and Incremental Ingestion

### T1-Q1 — Answer: B

A full load copies the whole selected scope; ELT describes transformation after landing/loading into the target analytical environment. Nightly scheduling does not make a load incremental. CDC is a change-capture mechanism, not a synonym for any database copy. A copy used for analytics is not automatically a backup: backup has recovery, immutability, retention, and restore objectives that must be designed separately.

### T1-Q2 — Answer: B

A watermark is a persisted progress boundary for selecting a subsequent changed-data scope. It does not inherently reveal hard deletes, guarantee unique identity, or prove transformation correctness. The extraction design must specify marker semantics, precision, overlap/lookback, and when the watermark may advance.

### T1-Q3 — Model answer (2 points)

Risks include:

- **Equal-timestamp collision:** several updates can share one-second precision; `updated_at > last_watermark` can skip records with the same timestamp as the last processed row.
- **Late visibility/backdated updates:** a row may become visible after the watermark has advanced, or its timestamp may not reliably reflect commit/change visibility.
- **Deletes:** hard-deleted rows may no longer be queryable by `updated_at`.
- **Non-atomic target/checkpoint:** advancing progress before target publication can skip data after a crash.

Safer approach: use a stable tie-breaker such as `(updated_at, primary_key)` if the source semantics support it, plus an overlap/lookback window when needed; use deterministic upsert/idempotency for repeated rows; persist the source window/run metadata; stage and validate output; publish/commit the target before advancing the durable watermark; reconcile the extracted scope. If the marker is not reliable, explicitly state the limitation and evaluate CDC, snapshot comparison, or source-side change tracking.

**Scoring:** 1 point for two meaningful risks; 1 point for a safe extraction/checkpoint strategy.

### T1-Q4 — Worked answer (2 points)

Full volume:

\[
8{,}000{,}000 \text{ rows} \times 500 \text{ bytes/row}
=4{,}000{,}000{,}000 \text{ bytes}
\]

Using decimal GB:

\[
4{,}000{,}000{,}000 / 10^9 = 4\text{ GB}
\]

Incremental rows:

\[
8{,}000{,}000 \times 0.04 = 320{,}000 \text{ rows}
\]

Incremental volume:

\[
320{,}000 \times 500 = 160{,}000{,}000 \text{ bytes}
=0.16\text{ GB}
\]

The incremental payload estimate is 4% of the full payload under these assumptions. The figures do not account for source query cost, index scans, network/protocol overhead, row-width variance, deletes, late changes, target merge cost, or extract duration. Those factors may change the choice.

**Scoring:** 1 point for both correct volumes and units; 1 point for a relevant limitation.

### T1-A1 — Worked answer (unscored)

Using T1-Q4's estimates and decimal units:

- Full load: \(4\ \mathrm{GB}/0.1\ \mathrm{GB/s}=40\ \mathrm{s}\).
- Incremental load: \(0.16\ \mathrm{GB}/0.1\ \mathrm{GB/s}=1.6\ \mathrm{s}\).
- A change just after the cutoff may wait nearly one hourly interval, then the next incremental run takes about 1.6 seconds to transfer and publish: approximately \(3,600+1.6=3,601.6\ \mathrm{s}\), or about 60 minutes and 1.6 seconds under the stated idealised assumptions.

This is only a simplified transfer/scheduling estimate. Source query time, transformations, retries, queuing, late visibility, deletes, publication and reconciliation can extend the delay; the watermark semantics may also make the change invisible. It is not an end-to-end freshness guarantee. For a 90-day backfill, use bounded/date-partitioned batches, source-side throttling or off-peak windows, durable run checkpoints, idempotent target merges, and per-window reconciliation before marking each range complete.

### T1-Q5 — Model answer and rubric (4 points)

A strong answer does not immediately prescribe CDC. It treats log readability as an initial clue, not proof that the source's change stream is operationally usable.

1. **Requirements:** confirm hourly operational freshness, daily complete/reconciled history, peak change rate, acceptable source load, recovery window, and regulatory evidence requirements.
2. **Baseline:** measure an incremental or full extract under representative load; nightly full scans are known to strain the source, but the exact bottleneck must be measured.
3. **Candidates:** investigate CDC/log-based capture, a supported incremental marker if available for the relevant tables, and snapshot comparison or source-side change tracking where deletes/updates cannot otherwise be found.
4. **Verify capabilities:** log retention, permissions, transaction ordering, snapshot boundary, delete/reversal representation, failover, schema change, lag observability, and on-call ownership.
5. **Correctness:** stable transaction identity; reversal/correction semantics; idempotent merge; source-to-target key coverage, counts/control totals by business date and currency, selected field checks, and independent business invariants.
6. **Recovery:** durable checkpoint only after target commit/publication boundary is safe; replay from retained log or landed raw input; bounded retries; reconciliation after catch-up; exceptions owned and tracked.
7. **Decision:** choose CDC only if capability and operations are confirmed and it meets the SLO; otherwise document the simpler viable baseline and its limits or make source-interface remediation a prerequisite.

**Scoring:** 1 point requirements/baseline; 1 point source capability checks; 1 point identity/delete/recovery; 1 point reconciliation/evidence and conditional recommendation. Accept other designs if requirements and constraints are explicit.

---

## Topic 2 — Change Data Capture and Database Replication

### T2-Q1 — Answer: C

Replication serves a copy-maintenance use case and can propagate source errors or deletions. Backup serves recovery from loss/corruption and requires independent retention and restore testing. Neither should be assumed to provide the other's guarantees.

### T2-Q2 — Answer: B

Operation type and stable key tell the consumer what logical entity/change is involved; source position/version and ordering metadata help it apply changes in the right order and resume. Exact fields depend on the CDC mechanism, but a wall-clock timestamp alone is not a reliable universal ordering key.

### T2-Q3 — Model answer (2 points)

A snapshot initializes the target from a source view; the ongoing stream captures changes after a defined source position or coordinated boundary. If the snapshot and stream do not share a safe boundary, changes committed during the gap may be missed, or changes represented in both may be applied twice. A correct design coordinates snapshot consistency with the starting position, documents transaction/ordering semantics, makes target application repeat-safe, and validates the initial snapshot plus subsequent changes.

Capture approaches differ: **log-based CDC** reads a source change log and depends on log access/retention and supported log semantics; **trigger-based CDC** records changes through source-side triggers and can add write-path overhead/operational coupling; **query-based CDC** polls tables using a detectable change marker and may miss hard deletes or changes not represented by the marker. Exact behaviour depends on the source and implementation.

**Scoring:** 1 point for the snapshot seam and gap/overlap risk; 1 point for a suitable boundary control and a meaningful distinction among capture approaches.

### T2-Q4 — Worked answer (2 points)

Net catch-up rate:

\[
900 - 700 = 200 \text{ changes/second}
\]

Catch-up time:

\[
360{,}000 \text{ changes} / 200 \text{ changes/second}
=1{,}800\text{ seconds}
\]

\[
1{,}800 / 60 = 30\text{ minutes}
\]

If capacity is 650/s while arrivals remain 700/s, net backlog change is \(650-700=-50\) changes/s: backlog grows by 50 changes/second and never clears under those constant rates.

**Scoring:** 1 point for net rate and 1,800 seconds; 1 point for 30 minutes and correct interpretation of the lower-capacity case.

### T2-A1 — Model answer (unscored)

The consumer cannot safely resume from an expired source position because the missing interval may contain updates and deletes no longer present in the retained log. Starting at the earliest retained position silently skips that interval; restarting blindly from an arbitrary point can also duplicate or misorder effects.

Recovery options are to re-bootstrap from a coordinated consistent snapshot plus a new stream boundary, use an authoritative archive/replica/change export if it covers the gap, or restore from another verified source of record. Define how deletes/tombstones are reconstructed, apply changes idempotently with source versions, and record the interval that was unavailable. Reconcile the rebuilt snapshot and post-boundary stream using key coverage, counts/control totals, delete/correction counts, selected record-level checks, and business invariants. Do not mark complete until the gap is covered by evidence or explicitly declared unresolved with business-owner approval.

### T2-Q5 — Model answer and rubric (4 points)

A defensible checklist separates evidence into:

- **Documented:** verified source-log access and semantics from authoritative documentation or tested source behaviour; supported operation types; ordering scope; checkpoint and failover behaviour.
- **Assumed:** proposed source and consumer rates, target merge capability, and expected recovery window—clearly labelled and validated.
- **Unknown/blocking:** log retention versus maximum outage/recovery time; hard-delete/tombstone representation; snapshot/log starting boundary; transaction ordering; schema evolution; failover continuity; supported permissions; source impact; operational owner.

Go/no-go should require enough log retention for outage plus catch-up, safe snapshot/stream boundary, explicit identity and delete semantics, recoverable checkpoint/offset, and ability to reconcile. If any critical capability is absent, select a documented fallback or block the CDC recommendation until the source contract changes.

Recovery plan: alert on log lag and retention risk; throttle/stop safely if the target is down; resume from a durable position; apply version-aware/idempotent writes; reconcile the affected range before declaring recovery.

Correctness checks could include (a) source-to-target key coverage, (b) counts/control totals by time window or transaction class, (c) delete/reversal counts, (d) selected record-level comparisons, and (e) domain invariants such as debit/credit balance rules where applicable.

**Scoring:** 1 point documented/assumed/unknown separation; 1 point snapshot/retention/delete/order checks; 1 point safe recovery; 1 point at least three meaningful correctness checks.

---

## Topic 3 — APIs, Files, and Managed Connectors

### T3-Q1 — Answer: C

A file's presence or readability does not prove the delivery is complete. A manifest and completion convention can establish the expected scope; checksums can detect byte-level corruption, while counts/control totals and schema validation detect different classes of defects. No single check proves all business correctness.

### T3-Q2 — Answer: B

A connector can reduce custom code but still has boundaries: supported source features, checkpoint state, retry behaviour, dead-letter handling, observability, resync/replay, upgrades, support, cost, and owner. Do not assume an end-to-end guarantee without evidence for the exact connector version, configuration, target, and failure boundary.

### T3-Q3 — Model answer (2 points)

Pagination can be incomplete if a page is skipped, duplicated, or fetched against a changing source where page boundaries shift. Rate limits constrain duration and concurrency. Checkpoints must capture safe page/cursor progress, and a cursor may expire or be invalid after source changes. A repeated page must not duplicate business effects; a missing page must be detectable.

Controls include stable cursor/checkpoint persistence, deterministic upsert/dedup by source identity, extraction run IDs, overlap/re-read where appropriate, expected counts or manifest/control totals, and source-to-target reconciliation. On partial extraction, do not publish the scope as complete; resume or restart a controlled range and validate it.

**Scoring:** 1 point for at least two relevant risks; 1 point for two suitable recovery/completeness controls.

### T3-Q4 — Worked answer (2 points)

Requests:

\[
75{,}000 / 500 = 150 \text{ page requests}
\]

Rate-budget lower bound:

\[
150 \text{ requests} / 5 \text{ requests/second}
=30\text{ seconds}
\]

Serial request-latency total:

\[
150 \times 0.250\text{ seconds} = 37.5\text{ seconds}
\]

The rate limit gives a 30-second lower bound, while 37.5 seconds of serial latency is larger under the stated serial assumption. Actual duration may be longer due to processing, retries, throttling, token refresh, metadata calls, page-size changes, and changing-source pagination semantics. If requests are concurrent, the latency sum is not itself elapsed wall-clock time; the request-rate limit still applies.

**Scoring:** 1 point for 150 requests and 30 seconds; 1 point for 37.5 seconds and a valid caveat.

### T3-A1 — Model answer (unscored)

- **Missing partner file:** detect the absence against the agreed arrival deadline, not just by directory polling. Alert the ingestion/partner owner, keep the expected business window marked missing, request delivery/status, and do not publish the window as complete. When the file arrives, validate its manifest, checksum/schema, counts/control totals, and then reconcile. Evidence includes the expected-run registry, alert, partner acknowledgement, manifest, and accepted/reconciled load record.
- **Stalled connector:** detect checkpoint age/position not advancing despite expected source activity, along with source lag, error counters, and last successful write. Assign the connector/platform owner; inspect logs and source/target health before restart or resync. Resume only from documented durable state; if checkpoint state is ambiguous, reconcile the affected interval and use a controlled resync. A green process status proves only that the process is running, not that data is flowing or complete.

### T3-Q5 — Model answer and rubric (4 points)

A strong conditional design:

- Verify whether the API has a stable `updated_since` token/cursor, consistent pagination semantics, delete/tombstone endpoint, request budget, token expiry, and backfill limits.
- If the change token is reliable and deletes/corrections are represented, prefer incremental API extraction with a persisted cursor, safe overlap if required, identity-based upsert, bounded rate, and key-coverage reconciliation.
- If no reliable change marker exists, compare periodic full snapshots or negotiate a better change interface; state the source load and delete-detection limitations. Do not assume full scans at a short interval are feasible.
- Evaluate a managed connector against the same requirements: incremental capability, deletes, checkpoint visibility, retry/error routing, resync, support, cost, upgrade policy, and ownership.
- API outage: bounded retry with backoff/jitter, alert on freshness, resume from safe checkpoint when possible.
- Repeated page: stable record identity and idempotent merge; compare cursor/page scope and reconcile.
- Expired credential: stop noisy retries, alert, rotate/fix least-privilege credential, resume from safe state.
- Incomplete extract: mark run incomplete, do not publish as complete, resume/restart the affected range, and reconcile before release.

**Scoring:** 1 point source capability/unknowns; 1 point justified conditional pattern/baseline; 1 point failure handling; 1 point completeness/correctness evidence. Alternative choices can earn full credit when assumptions are explicit.

---

## Topic 4 — Streaming Events and Message Contracts

### T4-Q1 — Answer: C

Events describe facts that happened; commands request an action; current-state records describe state at a point in time. A broker's acknowledgement and a partition key do not imply end-to-end exactly-once business effects or global ordering.

### T4-Q2 — Answer: A

A stable account/card key can route related events to the same ordering scope, but the architecture must verify the broker/transport's actual ordering guarantees. Random keys can split related events across partitions. Replay remains a recovery tool and must be safe.

### T4-Q3 — Model answer (2 points)

Useful fields/properties include event ID, event type, schema/contract version, entity/business key, source/producer identity, event time, processing/ingestion time, source sequence/version, payload, classification/sensitivity, correlation/causation ID, and correction/tombstone semantics.

**Event time** is when the business event occurred according to the producer's semantics; **processing time** is when a system handled it. Late arrival, clock skew, replay, and processing backlog can make them differ. Both may be needed for event-time analysis, lag/freshness measurement, and operational diagnosis.

**Scoring:** 1 point for six or more meaningful fields; 1 point for the time distinction and implication.

### T4-Q4 — Worked answer (2 points)

Events over three days:

\[
400\text{ events/s} \times 3 \times 24 \times 60 \times 60
=103{,}680{,}000\text{ events}
\]

Payload bytes:

\[
103{,}680{,}000 \times 2{,}000\text{ bytes}
=207{,}360{,}000{,}000\text{ bytes}
=207.36\text{ GB}
\]

Two reasons real storage differs: replication/metadata/index overhead can increase storage; compression can reduce it; event-size distribution and overhead can also change the result.

Catch-up: net capacity is \(800-400=400\) events/s.

\[
2{,}880{,}000 / 400 = 7{,}200\text{ seconds} = 120\text{ minutes}
\]

**Scoring:** 1 point for 207.36 GB and caveat; 1 point for 7,200 seconds/120 minutes.

### T4-A1 — Model answer (unscored)

The aggregate minimum is \(20,000/2,500=8\) partitions under the stated average-rate target. This is only a theoretical average; key skew can make one partition exceed the target. The hot partition receives 8,000 events/s but processes only 5,000 events/s, so its backlog grows by \(8,000-5,000=3,000\) events/s while those rates persist. The aggregate service has 5,000 events/second of spare capacity, but that does not help if the hot partition is serialised or assigned to a single constrained worker. Investigate skew-aware capacity/partition assignment, consumer processing efficiency, or a contract-approved key redesign. Splitting a card's events across keys may violate per-card ordering and must not be done silently. Validate with per-partition arrival/processing rates, lag/oldest-event age, key skew, rebalance/retry rates, and p95 end-to-end visibility.

### T4-Q5 — Model answer and rubric (4 points)

A good design specifies:

- **Identity:** stable unique event ID scoped by producer/tenant or an equivalent globally unambiguous key; entity/card key for partitioning and per-card ordering.
- **Contract:** event type, schema version, producer, event time, ingestion/processing time, source sequence/version if available, payload semantics, classification, correction/tombstone rules, and compatibility policy.
- **Consumer:** validate contract; persist progress safely; apply effects idempotently; reject or quarantine malformed events; use source version/sequence to avoid stale overwrite; define behaviour for same ID/different payload.
- **Replay:** retention must exceed the agreed recovery horizon; define offset/range replay, code/contract version, and post-replay reconciliation.
- **Operations:** monitor p95 event-to-consumer visibility, age of oldest event, consumer lag/backlog, throughput, retries, DLQ count/age, contract failures, and downstream service health; assign owner/action.
- **Exactly-once caveat:** a transport may make a scoped delivery/processing guarantee, but it does not by itself prove the fraud service's external effect happened once or that all business events were published. Verify the documented boundary and still use identity, idempotent effects, and reconciliation.

**Scoring:** 1 point contract/identity/order; 1 point duplicate/replay/poison handling; 1 point monitoring/retention; 1 point guarantee boundary and evidence.

---

## Topic 5 — Data Contracts, Schema Registry, and Compatibility

### T5-Q1 — Answer: B

A schema describes formal structure. A contract can include structure plus semantics, quality expectations, delivery behaviour, ownership, security/classification, compatibility, and change-management policy. A registry can enforce configured structural rules but does not automatically infer all business meanings.

### T5-Q2 — Answer: B

The field remains structurally valid but changes meaning. Consumers may continue parsing it while silently producing incorrect results. Semantic changes require impact analysis, contract review, versioning/migration where appropriate, and explicit communication.

### T5-Q3 — Model answer (2 points)

Using the common conceptual definitions in the roadmap:

- **Backward compatibility:** a new reader can read data written under an older schema, subject to the format and configured rules.
- **Forward compatibility:** an older reader can handle data written under a newer schema, subject to unknown-field/default/reader behaviour.
- **Full compatibility:** both directions are supported under the applicable policy.

The terms can be implemented differently by formats, serializers/deserializers, registry rules, and consuming engines. State the writer/reader direction explicitly and test the real producer/consumer combination; do not rely only on a label.

**Scoring:** 1 point for correctly explaining directions; 1 point for contextual implementation caveat.

### T5-Q4 — Model answer (2 points)

1. **Add optional field with documented default:** often structurally low-risk, but verify actual reader/default behaviour and semantic contract.
2. **Rename consumed field:** structural risk; assess all consumers, version or migrate, and use an approved deprecation/expand-contract plan.
3. **Dollars to cents, same numeric type:** semantic breaking risk; update units/meaning explicitly, use a versioned migration or new field, and validate downstream calculations.
4. **New enum value with strict parser:** context-dependent structural/consumer risk; test tolerant-reader behaviour and compatibility rules, and ensure unknown values are handled safely.

**Scoring:** 1 point for reasonable classifications; 1 point for meaningful checks. Accept other labels if the reasoning is correct.

### T5-A1 — Model answer (unscored)

A non-transitive compatibility check typically compares a candidate version only with the latest registered version; a transitive check typically compares it with all versions in the relevant history. Here, v3 passing against v2 but failing against v1 means a latest-only policy may accept it while a transitive policy may reject it. Exact policy names, directions, history scope, and behaviour vary by registry, format, and serializer, so verify the selected implementation and test real readers/writers. Even a structurally compatible change can alter field semantics, units, null meaning, event ordering, or business invariants; consumer impact review and contract tests remain necessary.

### T5-Q5 — Model answer and rubric (4 points)

A complete contract should name the producer/domain owner, consumer owners, event purpose/grain, stable account identity, schema version, field semantics/units/nullability, event/source time, ordering/version, delete/correction semantics, data quality constraints, classification, delivery/freshness expectations, retention/replay, compatibility direction, and escalation.

Evolution policy:
- run schema/contract tests in CI and at publication/ingestion;
- classify changes as structural or semantic and assess analytics, fraud, and customer-service consumers;
- for a breaking change, publish a new version or use an approved expand-and-contract/parallel-version migration; announce deprecation and sunset dates, monitor adoption, and keep rollback available;
- do not silently change a field's meaning; add a new field/version or explicitly migrate and reconcile.

A registry may store versions and enforce configured structural compatibility rules; it does not prove business meaning, data quality, event completeness, correct identity, or downstream business effect. Validate actual serializer/reader/consumer behaviour.

**Scoring:** 1 point contract and ownership; 1 point compatibility/evolution; 1 point semantic-break handling and consumer impact; 1 point registry limits and rollback/validation.

---

## Topic 6 — Data Virtualization, Federation, and Data Sharing

### T6-Q1 — Answer: B

Virtualization/federation provide logical/query-time access; data sharing describes governed access and ownership between a producer and consumers. Sharing may use a query endpoint, file, replica, or another mechanism. Federation does not automatically give a consistent cross-source snapshot, and materialized data has refresh lag unless continuously maintained under a defined contract.

### T6-Q2 — Answer: C

Occasional, small exploratory queries can be suitable if source capacity, access controls, latency, and consistency are acceptable. High-volume or high-availability workloads may overload or become tightly coupled to operational sources. A regulatory report may still use materialized, versioned data to support reproducibility and reconciliation.

### T6-Q3 — Model answer (2 points)

Virtualization/federation can expose current source data without creating a new durable copy, but query latency and availability depend on the source/network and query plan. It may create load on operational systems and may not give a single consistent snapshot across sources. Materialization adds storage and refresh lag, but can isolate source load, improve predictable query performance, preserve a reproducible snapshot, and keep consumers available during source outages if the last published copy remains usable.

Revisit toward materialization if query volume/source pressure grows, freshness/availability requirements cannot be met, cross-source consistency/reproducibility becomes mandatory, or source outages frequently block consumers.

**Scoring:** 1 point for balanced comparison across at least four dimensions; 1 point for a concrete revisit condition.

### T6-Q4 — Worked answer (2 points)

\[
A_{\text{chain}}=0.999 \times 0.995 \times 0.998
=0.99201699
\]

As a percentage:

\[
0.99201699 \times 100 = 99.201699\% \approx 99.20\%
\]

This assumes independent availability and a serial path in which all three components must be available. Real failures may be correlated, caches/fallbacks may exist, and availability definitions may differ. Materialization can decouple read availability from source availability, while freshness then depends on the ingestion path and last successful publication.

**Scoring:** 1 point for the product and 99.20%; 1 point for assumptions and materialization implication.

### T6-A1 — Model answer (unscored)

The estimated source-query rate is \(40\times3\times3=360\) source-query requests/minute under the stated fan-out assumption. T6-Q4's simplified availability estimate is about 99.20%, below the stated 99.9% target. A serial federated query cannot meet that availability target under the same assumptions, and without a shared source snapshot it cannot by itself guarantee reproducible month-end results. Prefer a versioned/materialized coordinated extract for month-end reporting, with explicit refresh, snapshot boundaries, reconciliation and a degraded-mode policy. Federation may still serve low-volume current lookups if source load, access controls and latency are acceptable. Governed data sharing defines producer/consumer responsibilities, permissions, purpose, freshness and audit regardless of whether the physical mechanism is federation, files, or materialized data. Validate with measured end-to-end availability, snapshot/reconciliation evidence, source-load tests and access-policy checks.

### T6-Q5 — Model answer and rubric (4 points)

A defensible design might start with tightly scoped federation for occasional low-volume lookups only if measured source capacity and cross-source behaviour are acceptable, while using a materialized view for high-volume or availability-sensitive usage. Governed data sharing can define the producer-owned customer/account product and consumer access policy regardless of the underlying physical pattern.

Controls: least-privilege access per consumer; sensitive-field minimisation; audit logging; encryption; source query concurrency/rate limits; masking where required; explicit freshness and degraded-mode indicators; bounded query timeouts; no silent fallback that changes semantics; source and federation owners; data classification and retention.

Assumptions to verify include query concurrency, latency, source capacity, cross-source consistency, account/customer join identity, access rules, and what “current” means. Rejected alternatives should cite evidence: full materialization may add refresh/ownership cost; unrestricted federation may overload sources; a shared raw copy may violate governance or duplicate semantics. Revisit if load, SLO, consistency, privacy, or source availability changes.

**Scoring:** 1 point pattern selection tied to usage; 1 point security/governance; 1 point failure/consistency/ownership; 1 point alternatives and revisit triggers.

---

## Topic 7 — Idempotency, Deduplication, and Reconciliation

### T7-Q1 — Answer: B

Idempotency, deduplication, and reconciliation are related but different. Idempotency makes repeated operation safe within a defined boundary; deduplication groups repeated representations by identity; reconciliation compares a defined source/target scope and business controls. None alone guarantees complete correctness. Equal counts and totals can conceal mis-mapping, field corruption, or offsetting errors.

### T7-Q2 — Answer: B

Same identity with different payload is a conflict, not an ordinary duplicate. Preserve the evidence and investigate whether the producer reused an ID, identity scope is incomplete, a correction/version rule is missing, or an event was mutated. “Last arrival wins” is unsafe unless the contract explicitly defines a trustworthy version/order rule.

### T7-Q3 — Model answer (2 points)

The condition accepts every incoming update for the same account, even when its version is older; it can overwrite newer state. It also does not distinguish a legitimate duplicate from the same version carrying contradictory values.

A corrected implementation can be:

```python
def apply_update(current, incoming):
    if current is None:
        return incoming

    if incoming["account_id"] != current["account_id"]:
        raise ValueError("identity mismatch")

    if incoming["version"] > current["version"]:
        return incoming

    if incoming["version"] < current["version"]:
        return current  # stale update: record/measure as appropriate

    # Same identity and version
    if incoming["balance"] == current["balance"]:
        return current  # exact logical duplicate
    raise ValueError("conflicting payload for same identity/version")
```

This assumes `account_id` is unique in the relevant scope and `version` is a reliable monotonic source version. If IDs are tenant-local, include tenant/source namespace. In production, conflict handling should create an observable exception rather than silently losing evidence. The illustrative function was syntax-checked and exercised against representative in-memory cases during this audit; this does not test durable state, transactions, or concurrent workers.

**Scoring:** 1 point identifies the stale-overwrite defect and requires a stable key/version; 1 point gives correct newer/equal/older handling, including conflict detection.

### T7-Q4 — Worked answer (2 points)

Target-minus-source deltas are:

| Scope | Count delta | Amount delta |
|---|---:|---:|
| Account A | \(5,980-6,000=-20\) rows | \(5,050,000-5,100,000=-50,000\) dollars |
| Account B | \(4,020-4,000=+20\) rows | \(3,450,000-3,400,000=+50,000\) dollars |
| Overall | \(10,000-10,000=0\) rows | \(8,500,000-8,500,000=0\) dollars |

The opposite account-level deltas cancel at the grand-total level. Count and grand-total checks therefore miss a mis-mapping that preserves row cardinality and total amount. Further checks include comparing stable transaction IDs and account IDs record by record, validating account ownership/reference constraints, and reconciling key coverage. Limitations: aggregate checks can miss offsetting errors; record-level checks can inherit a bad source/key mapping; reference checks can prove an account exists without proving it is the correct account. Use layered, partly independent controls.

**Scoring:** 1 point for correct account-level and overall deltas; 1 point for explaining the aggregate blind spot and proposing at least two useful checks with a limitation.

### T7-A1 — Model answer (unscored)

Possible undetected defects include wrong entity/account mapping that preserves aggregate counts and totals, a semantic unit conversion error that is consistent across all target rows, and a transformation that drops or misinterprets a business status while preserving file bytes/checksum at the landing boundary. A checksum of the landed file proves byte-level equality for the compared copies, not correctness of a later transformation.

Use layered controls: (1) key-level source/target comparison for identity and selected fields; (2) grouped counts/control totals by business dimensions such as account, currency, and window; (3) domain invariants and referential/business-rule checks; (4) schema/semantic contract assertions; and (5) exception sampling or independent source reconciliation. Each has blind spots: aggregate totals can conceal offsetting errors, key comparisons depend on correct keys and independent source data, and domain rules do not detect every valid-looking wrong value.

### T7-Q5 — Model answer and rubric (4 points)

- **Identity:** use a stable payment/event ID scoped to the producer and business operation; include tenant/account context where necessary.
- **Idempotency:** enforce a durable uniqueness/idempotency boundary at the target or operation ledger. A repeated event should return/retain the original result rather than apply the debit twice.
- **Version/merge:** for mutable state, use an authoritative version/sequence; do not let late older data overwrite newer state. Payment events should distinguish new effects from corrections/reversals.
- **Checkpoint:** do not advance progress before the target effect is durable unless the output and checkpoint are atomically coupled. If target commit succeeds but acknowledgement/checkpoint fails, redelivery must be safe.
- **Reconciliation:** compare source and target by time window and stable ID; inspect duplicate effects, missing keys, totals by currency/type, and selected business invariants. Reconcile after replay before closing.
- **Exception workflow:** record event ID, source position, target transaction/result, attempt history, timestamps, code/contract version, owner, and disposition. Query the outcome or use idempotency key before retrying an ambiguous external side effect.
- **Evidence:** one durable business effect per logical payment ID, complete source-to-target key coverage for the scope, no unexplained control-total deltas, and an auditable exception/recovery record.

Timestamp-only deduplication is inadequate because clocks can collide or skew, distinct events can share a timestamp, retries can arrive later, and a timestamp is not a durable business identity.

**Scoring:** 1 point identity/idempotency; 1 point version/checkpoint safety; 1 point reconciliation; 1 point ambiguous outcome/exception evidence.

---

## Topic 8 — Integration Pattern Selection and Failure Handling

### T8-Q1 — Answer: B

A deterministic schema error will generally recur if the same invalid input and code are retried unchanged. Stop or quarantine the affected scope, alert the contract owner, correct the schema/mapping or source data, and then replay under controlled conditions. Do not silently drop the record or advance progress without tracking the gap.

### T8-Q2 — Answer (1 point total)

1. Temporary network error during a read: **retry with bounded backoff** (assuming the read is safe and the request budget permits it).
2. Malformed record violating the agreed schema: **quarantine/stop for correction**; do not retry indefinitely without a change.
3. Timeout after a non-idempotent create may have committed: **investigate outcome before retry** using an idempotency key or status query/reconciliation.

Award the point only if all three categories are assigned correctly or with equivalent safe reasoning.

### T8-Q3 — Worked answer (2 points)

Each layer has one initial attempt plus five retries: \(1+5=6\) attempts. Under the stated multiplicative assumption, final-layer attempts are \(6^3=216\). Counting calls at every layer gives \(6+6^2+6^3=6+36+216=258\) total attempts across the three layers. This is a worst-case amplification model, not a prediction that every production failure will reach every retry. Reduce amplification by owning retries at one clear layer, using bounded shared deadlines/budgets, exponential backoff with jitter, respecting rate limits, and avoiding nested independent retry loops.

**Scoring:** 1 point for 216 final-layer attempts and 258 total calls; 1 point for a suitable control and correct caveat.

### T8-Q4 — Worked answer (2 points)

Outage duration:

\[
20\text{ minutes} \times 60 = 1{,}200\text{ seconds}
\]

Backlog:

\[
1{,}200\text{ s} \times 600\text{ events/s} = 720{,}000\text{ events}
\]

Net catch-up rate:

\[
900 - 600 = 300\text{ events/s}
\]

Catch-up time:

\[
720{,}000 / 300 = 2{,}400\text{ seconds} = 40\text{ minutes}
\]

The estimate may be optimistic if payload size varies, partition skew exists, retries/poison records reduce effective throughput, downstream rate limits restrict catch-up, processing capacity fluctuates, or new events arrive above the assumed rate. If recovery capacity is at or below arrivals, backlog will not clear.

**Scoring:** 1 point for backlog and net rate; 1 point for 40 minutes and two realistic caveats.

### T8-A1 — Worked answer (unscored)

With \(d_n=\min(30,1\times2^{n-1})\) seconds for retry numbers 1 through 6, the retry bounds are 1, 2, 4, 8, 16, and 30 seconds (the sixth exponential value of 32 seconds is capped at 30). The maximum total wait is \(1+2+4+8+16+30=61\) seconds. With independent uniform full-jitter draws from zero to each bound, expected total wait is half the sum: \(0.5\times61=30.5\) seconds. These figures exclude request execution time and any server-directed `Retry-After`. A retry policy also needs a total deadline/budget and a safe operation rule: retry reads or idempotent writes as permitted; for an ambiguous non-idempotent outcome, query status or use an idempotency key before repeating the effect.

### T8-Q5 — Model answer and rubric (4 points)

Answers may vary. A strong submission is internally consistent and separates facts, assumptions, and unknowns. The following is one acceptable direction, not the only possible design.

#### A. Requirements and source/consumer profile

- **Ledger → analytics:** hourly operational freshness and daily reconciled history are stated requirements. Readable log is known from the scenario; retention, delete semantics, snapshot boundary, ordering, failover, and operational support remain unknown.
- **Card events → fraud:** p95 visibility ≤ 60 seconds, per-card ordering, and replay after outage are stated. Confirm source event publication, stable event identity, partition semantics, retention, and fraud-service recovery capacity.
- **Settlement file → finance:** daily bulk delivery with completeness and audit evidence. Confirm manifest, checksum, business-date, schema/version, correction/resend, and secure transfer conventions.
- **CRM → customer domain:** API-only, paginated and rate-limited; reliable change token and delete behaviour are unknown. Confirm quota, page/cursor consistency, token expiry, delete endpoint, and backfill limits.

#### B. Candidate selection and baseline

| Flow | Candidate | Simplest adequate baseline | Rejected/conditional alternatives |
|---|---|---|---|
| Ledger | CDC only after log retention, delete/order/snapshot/failover support are verified; otherwise a supported incremental/snapshot strategy with limitations recorded | Measure an incremental or scheduled extract and its source impact | Rejecting full scans requires measurements; reject CDC until source capabilities and operations are confirmed |
| Card → fraud | Event streaming with stable identity, per-card ordering scope, retention and replay | API/polling or incremental batch is a baseline comparison, likely unable to meet 60-second p95 unless evidence proves otherwise | Reject direct synchronous coupling if it makes producer availability depend on fraud consumer and does not meet replay/fan-out needs |
| Settlement | File with manifest, checksum, schema/version, staging and publication gate | File load using partner's existing delivery contract, strengthened by completeness controls | Reject streaming if the partner only produces a daily bulk file and the business does not need event-level freshness |
| CRM | Incremental API if reliable change token and delete/correction semantics exist; otherwise snapshot comparison or source-contract remediation | Full API extract at a measured feasible cadence | Reject CDC if API-only means no supported log/change interface; reject frequent full scans unless quota, source impact, and duration are acceptable |

#### C. Contract, identity, and normal flow

- Ledger: transaction ID plus source namespace; define reversal/correction semantics, source version/position, business-date/currency, and merge rule.
- Card: event ID plus producer namespace; card key for ordering; event time and processing time; schema version; explicit duplicate, late, out-of-order and correction handling.
- Settlement: partner file/run ID, business date, manifest identity, record count/control totals, checksum, schema version, currency/amount semantics, and resend/correction rule.
- CRM: stable customer identity, API cursor/change token, update/version semantics, delete/tombstone policy, and page/run identity.

A representative flow is: source/interface → durable landing/buffer → contract and identity validation → idempotent transform/merge → reconciliation → atomic or explicitly controlled publication → consumer. Record the checkpoint and commit boundary. Do not mark a partial extract or file complete.

#### D. Failure handling and recovery

- **Ledger log/CDC:** alert on lag and retention risk; resume from durable position; throttle catch-up; apply version-aware merge; reconcile keys, counts/control totals, reversals/deletes, and selected fields before closure.
- **Card stream:** bounded retry and jitter; isolate the fraud consumer; monitor lag/oldest-event age; quarantine poison events with restricted access and named owner; replay retained offsets/ranges; rate-limit catch-up to protect fraud dependencies.
- **Settlement file:** do not ingest until completion convention, manifest and checksum/control totals pass; quarantine mismatches; request resend or follow the agreed correction workflow; publish only validated staging output.
- **CRM API:** obey rate limit; bounded retries on transient errors; fix expired credentials rather than retrying indefinitely; checkpoint safely; use stable identity for duplicate pages; do not advance completion status until required pages/range and reconciliation pass.
- **Cross-cutting:** schema errors stop/quarantine affected scope; target outage buffers within capacity/retention; ambiguous non-idempotent timeout is investigated before retry; partial publication is prevented or explicitly marked.

#### E. Monitoring and ownership

Signals should include:
- freshness and expected-input absence;
- CDC/stream lag and oldest-event age;
- API throttling, page/cursor progress, retry budget and credential failures;
- file arrival, manifest/checksum/count/control-total validation;
- schema/contract violations and identity conflicts;
- target commit/checkpoint mismatch;
- reconciliation deltas and unresolved exception age;
- source pressure and catch-up estimate.

Each signal needs a named producer/integration/consumer owner, an alert route, first diagnostic action, and evidence required to close the incident. A generic “pipeline failed” alert is not sufficient.

#### F. Illustrative catch-up calculation

For the card stream, suppose an outage lasts 20 minutes, arrivals are 600 events/s, and recovery processing capacity is 900 events/s. These are illustrative assumptions.

\[
\text{backlog}=20\times60\times600=720{,}000\text{ events}
\]

\[
\text{net catch-up rate}=900-600=300\text{ events/s}
\]

\[
\text{catch-up time}=720{,}000/300=2{,}400\text{ s}=40\text{ minutes}
\]

This estimate assumes steady arrivals and processing capacity and ignores retries, skew, and downstream throttling. It demonstrates that recovery capacity must exceed ongoing arrivals. During recovery, the 60-second p95 freshness target may be breached; the design should alert, communicate degraded freshness, and avoid overwhelming the fraud service.

#### G. ADR and validation

The ADR should include context, measurable requirements, source/consumer profile, selected patterns, baseline comparison, alternatives and rejection reasons, contract/identity, correctness claim, failure boundaries, retry/checkpoint/replay rules, security, monitoring, ownership, assumptions/unknowns, residual risks, and revisit triggers.

Validation evidence should include contract tests, a duplicate/replay scenario, an out-of-order update, source/target outage, schema change, incomplete file, expired credential, and reconciliation of a controlled range. Mark drills **planned** until executed. A successful retry or restored offset alone is not proof of business correctness.

**Scoring (4 points):**
- 1 point: measurable requirements, source/consumer profiles, and explicit unknowns.
- 1 point: justified patterns, simplest adequate baselines, and rejected alternatives.
- 1 point: contract/identity, retry/checkpoint/replay/reconciliation, and failure controls.
- 1 point: monitoring owner/action, catch-up calculation, ADR/revisit triggers, and validation evidence.

### T8-Drill-1 — Suggested classifications and responses

| # | Primary category | Default response | Detection / reasoning |
|---:|---|---|---|
| 1 | Source | Bounded retry, alert, then wait/escalate | Source health and failed extraction; resume from safe progress when available |
| 2 | Source | Reduce rate/concurrency and investigate; retry only within budget | Latency percentiles and source-load metrics; aggressive retries may worsen load |
| 3 | Transport | Bounded retry for the read, with backoff/jitter | Request error/timeout; verify safe pagination/checkpoint behaviour |
| 4 | Transport/interface limit | Honour documented retry hint and reduce request rate | Throttle response and request-rate metrics |
| 5 | Control plane / credentials | Remediate credential; avoid noisy repeated retries | Authorization failures and credential-expiry alert |
| 6 | Processing/interface semantics | Investigate cursor behaviour; deduplicate safely and reconcile | Cursor/page IDs and repeated source identities |
| 7 | Source/transport delivery | Wait for completion; do not publish | Arrival marker without completion evidence; manifest or size stability |
| 8 | Transport/file integrity | Quarantine and request resend or approved recovery | Checksum mismatch; never treat the file as complete |
| 9 | Processing/contract | Quarantine or reject affected record/scope | Contract-validation failure and record-level exception |
| 10 | Contract/processing | Stop or quarantine affected scope; assess compatibility | Schema/enum validation and consumer impact |
| 11 | Processing | Quarantine poison record if semantics allow; fix and replay | Repeated record-level failure and DLQ age |
| 12 | Processing/resource | Contain, reduce batch size or tune capacity, then resume safely | Worker memory/resource telemetry; verify no partial publication |
| 13 | Target | Buffer within capacity; bounded retry and controlled catch-up | Target health, commit errors, backlog and freshness |
| 14 | Target/data quality | Quarantine/fix invalid row or mapping; do not retry unchanged indefinitely | Constraint violation and exception record |
| 15 | Ambiguous target outcome | Investigate outcome before retry; use idempotency key/status query | Timeout plus target audit/status and duplicate-effect check |
| 16 | Control/progress correctness | Stop progression; determine skipped range and replay/reconcile | Checkpoint versus durable commit evidence |
| 17 | Control plane | Alert, wait/retry within budget, and preserve progress | Registry/metadata dependency health; do not bypass contract policy blindly |
| 18 | Control plane/scheduler | Alert, restore scheduler, run missed scope with unique run ID | Scheduler heartbeat and expected-run absence |
| 19 | Operator/configuration | Roll back/fix config; assess affected scope and controlled backfill | Change audit, anomalous counts, source/target reconciliation |
| 20 | Operator/recovery process | Stop replay, assess target impact, restore correct range and reconcile | Replay run metadata, offset/window record, key coverage and totals |
| 21 | Source/partner delivery | Alert at the delivery deadline; contact partner and keep the target scope unpublished | Arrival SLA, manifest registry, missing-run alert, partner acknowledgement and later control-total reconciliation |
| 22 | Connector/control plane | Treat stalled progress as an incident; inspect source lag, errors and checkpoint state before restart/resync | Checkpoint age/position, source-side change activity, connector logs, alert owner and post-recovery reconciliation |
| 23 | Source retention/recovery boundary | Do not skip forward and claim completeness; re-snapshot/re-bootstrap or use another authoritative recovery source, then reconcile the gap | Retention/position evidence, snapshot boundary, delete handling, key coverage and business control totals for the affected interval |

Categories can overlap because a failure may cross boundaries; award full credit when the learner identifies the primary failure boundary and justifies a safe response. Never blindly retry an operation with an ambiguous non-idempotent outcome, never publish a missing/incomplete scope as complete, and never claim a CDC gap is repaired until the unrecoverable interval has been re-established and reconciled.

### IC-1 — Model response and review criteria (unscored)

| Flow / failure | Immediate response | Recovery path | Correctness evidence before close |
|---|---|---|---|
| Ledger CDC: outage exceeds 24-hour log retention | Declare the source-position gap; do not resume at the earliest retained position and claim completeness | Re-snapshot with a coordinated new stream boundary or use another authoritative archived source; reconstruct deletes/corrections | Snapshot boundary, covered time/position range, key coverage, counts/control totals, delete/correction checks, business invariants |
| Settlement file missing | Mark the expected business window missing and alert partner/finance owner; do not publish as complete | Obtain the file or an approved alternate source; validate manifest/checksum/schema before load | Delivery evidence, manifest, accepted record count/control totals, source-to-target reconciliation |
| CRM connector checkpoint stalled | Treat “running” as insufficient; inspect checkpoint age, source activity, connector logs, target health, and credentials | Resume from proven durable state; if state is ambiguous, controlled resync and reconcile the affected range | Checkpoint progression, source/target range coverage, duplicate/missing-key checks, freshness recovery |

Prioritise financial completeness and unrecoverable retention risk, while communicating degraded freshness for all affected consumers. Each incident needs a named owner, timestamped evidence, a safe publication boundary, and a post-recovery reconciliation. If evidence cannot establish completeness, record the residual gap and obtain explicit business-owner disposition rather than claiming success.

### IC-2 — Model response and review criteria (unscored)

The amount field has a semantic breaking change despite retaining its numeric type. A structural registry check may pass because it cannot infer currency-unit meaning. Equal row counts only show cardinality, not correct amount interpretation. Stop or contain the affected consumer rollout; raise a contract change, define units explicitly, assess all consumers, and publish a new field/version or use an approved expand-and-contract migration. During overlap, retain old semantics for old consumers, migrate readers, monitor adoption, and deprecate only after approval. Validate with contract assertions for units and ranges, sample record comparisons, totals converted into a canonical unit, business invariants, replay/backfill of the affected window, and an independently reviewed reconciliation report.

**Review criteria:** full credit requires the semantic break to be identified, the registry's limit stated, a migration/rollback plan, and reconciliation evidence beyond counts alone.

---

# Part III — Assessment Review and Remediation

## 4. Scoring rubric by learning level

| Level | Primary evidence | How to judge performance |
|---|---|---|
| **Beginner** | Topic Q1–Q2 (scored, 1 point each) | Correctly defines or classifies the mechanism and rejects the key misconception; no unsupported guarantee.
| **Intermediate** | Topic Q3–Q4 (scored, 2 points each) | Explains the mechanism or reproduces the calculation with formula, units, assumptions, interpretation, and a meaningful limitation. For code-reading, identifies the defect and safe rule.
| **Advanced** | Topic A1 extensions (unscored) | Analyses interacting failure boundaries, retention, transitivity, skew, retry budgets, freshness, or reconciliation blind spots; makes assumptions explicit and supports the answer with calculations or controls. Use the model answer as a review rubric.
| **Industry application** | Topic Q5 (scored, 4 points each); IC-1 and IC-2 are unscored review cases | Produces a traceable recommendation: measurable requirements, source/consumer profile, feasible candidates, simplest adequate baseline, rejected alternatives, contracts, correctness controls, failure recovery, owners, evidence, and revisit triggers. Accept multiple defensible solutions.

The A1 extensions and IC cases do not alter the 80-point score. They are deliberate practice for the roadmap's advanced and industry-level expectations, which cannot be represented fully by a single numeric score.

## 5. Topic-level scorecard

Record your score after checking the answer key.

| Topic | Maximum | Your score | Review trigger |
|---|---:|---:|---|
| 1. Batch ETL/ELT and incremental ingestion | 10 |  | Review if below 6 |
| 2. CDC and replication | 10 |  | Review if below 6 |
| 3. APIs, files, managed connectors | 10 |  | Review if below 6 |
| 4. Streaming and message contracts | 10 |  | Review if below 6 |
| 5. Contracts and compatibility | 10 |  | Review if below 6 |
| 6. Virtualization, federation, sharing | 10 |  | Review if below 6 |
| 7. Idempotency, deduplication, reconciliation | 10 |  | Review if below 6 |
| 8. Pattern selection and failure handling | 10 |  | Review if below 6 |
| **Total** | **80** |  | **Target: at least 64 and every topic at least 6** |

The review trigger of 6/10 is the rounded-up minimum for a 60% topic threshold. The recommended overall threshold is 64/80 (80%). These are study-assessment choices and do not replace the roadmap's completion gates.

## 6. Remediation map

| Weakness observed | Revisit | Evidence to produce before retry |
|---|---|---|
| Confuses full, incremental, CDC, replication, and backup | Topic 1 and Topic 2 | Comparison table; watermark rule; snapshot/stream seam diagram |
| Cannot explain API/file completeness or connector limits | Topic 3 | Interface comparison; manifest example; failure table for API outage, missing/incomplete file, and connector stall |
| Assumes partitioning means global order or broker acknowledgement means business correctness | Topic 4 | Message contract; partition/order scope; duplicate/replay walkthrough |
| Treats structural compatibility as semantic correctness | Topic 5 | Change classification; consumer impact matrix; migration/deprecation policy |
| Cannot justify virtualization vs materialization | Topic 6 | Access-pattern comparison with source-load and availability assumptions |
| Treats deduplication as idempotency or trusts counts alone | Topic 7 | Identity/merge rules; reconciliation coverage matrix; defect-to-control table |
| Uses unbounded retries or has no catch-up plan | Topic 8 | Retry budget; failure matrix; backlog/catch-up worksheet |
| Pattern recommendation lacks traceability | Topics 1–8 and cross-system project | ADR with requirements, baseline, alternatives, assumptions, risks, and revisit triggers |

## 7. Final readiness checklist and module-wide completion evidence

This assessment supports, but does not alone replace, the roadmap's topic and project completion gates. Before marking the module complete, retain:

- [ ] Topic 1 flow with change marker, watermark rule, safe rerun behaviour, extract-time/staleness worksheet, and backfill procedure.
- [ ] Topic 2 documented/assumed/unknown guarantee table, snapshot-plus-stream procedure, and lag/catch-up worksheet.
- [ ] Topic 3 interface comparison and failure handling for unavailable API, incomplete file, and stalled connector.
- [ ] Topic 4 event/message contract, partition/retention worksheet, and failure-point table.
- [ ] Topic 5 contract, semantic/structural change classification, compatibility/evolution policy, and consumer-impact analysis.
- [ ] Topic 6 access-pattern comparison with source-load/availability estimates and revisit triggers.
- [ ] Topic 7 identity/merge/version/dedup rules, reconciliation design, coverage matrix, defect-to-control table, and exception workflow.
- [ ] Topic 8 pattern selection table, baseline comparison, failure matrix, monitoring specification, failure-drill plan, and ADR.
- [ ] Cross-system design covers all relevant flows consistently across requirements, source/consumer profiles, contracts, patterns, correctness controls, failures, monitoring, and ADR.
- [ ] At least five normal scenarios and eight failure scenarios are walked through in the project, including duplicate delivery, out-of-order update, replay, schema change, source outage, and incomplete file.
- [ ] All quantitative claims in the project state units, formulas, assumptions, and illustrative status; a reviewer can reproduce at least three figures.
- [ ] Security/governance controls cover classification, least privilege, retention, sensitive landing/quarantine/DLQ data, lineage, and ownership.
- [ ] Every alert has an owner and action; absence and staleness are monitored; a failure drill has explicit pass criteria.
- [ ] Advanced extensions T1-A1–T8-A1 and integrated case studies IC-1/IC-2 are completed and reviewed; wrong answers are corrected and re-attempted, and advanced/industry answers are reviewed by another person where possible.

**Final self-check:** Can you defend each integration choice from a measurable requirement and source evidence, explain the failure path, and show what proves recovery and correctness? If not, keep the design open and record the unknown rather than claiming the pattern is production-ready.
