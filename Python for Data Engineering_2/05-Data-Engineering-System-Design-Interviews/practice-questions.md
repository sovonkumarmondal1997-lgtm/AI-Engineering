# G5 --- Data Engineering System Design Interviews

# 40 Practice Questions and Solutions

## How to Use This Practice Bank

Read only the problem first. Start the timer, solve without notes, think
aloud, draw/code as appropriate, stop at time, record when practical,
score yourself, then read the solution and log the root cause of
mistakes.

``` text
Attempt → Record → Score → Diagnose → Correct → Space → Re-attempt → Mock → Measure
```

This is exactly **40 primary questions**: 10 Basic, 10 Moderate, 10 Hard
and 10 Advanced.

## Difficulty Framework

  Level        Questions   Suggested time
  ---------- ----------- ----------------
  Basic            1--10       10--15 min
  Moderate        11--20       15--25 min
  Hard            21--30       25--35 min
  Advanced        31--40      35--45+ min

## Coverage Map

  Question   Difficulty   Primary Topics
  ---------- ------------ ----------------

------------------------------------------------------------------------

| Q1 \| Basic \| Topic 01 \|

------------------------------------------------------------------------

| Q2 \| Basic \| Topic 02, Topic 04 \|

------------------------------------------------------------------------

| Q3 \| Basic \| Topic 03 \|

------------------------------------------------------------------------

| Q4 \| Basic \| Topic 05, Topic 07, Topic 08 \|

------------------------------------------------------------------------

| Q5 \| Basic \| Topic 06, Topic 04 \|

------------------------------------------------------------------------

| Q6 \| Basic \| Topic 07, Topic 16 \|

------------------------------------------------------------------------

| Q7 \| Basic \| Topic 09, Topic 18 \|

------------------------------------------------------------------------

| Q8 \| Basic \| Topic 16, Topic 18 \|

------------------------------------------------------------------------

| Q9 \| Basic \| Topic 17 \|

------------------------------------------------------------------------

| Q10 \| Basic \| Topic 19 \|

------------------------------------------------------------------------

| Q11 \| Moderate \| Topic 03, Topic 04, Topic 07 \|

------------------------------------------------------------------------

| Q12 \| Moderate \| Topic 02, Topic 04, Topic 05, Topic 07 \|

------------------------------------------------------------------------

| Q13 \| Moderate \| Topic 03, Topic 08, Topic 16 \|

------------------------------------------------------------------------

| Q14 \| Moderate \| Topic 09, Topic 16, Topic 04 \|

------------------------------------------------------------------------

| Q15 \| Moderate \| Topic 08, Topic 12, Topic 16 \|

------------------------------------------------------------------------

| Q16 \| Moderate \| Topic 03, Topic 13 \|

------------------------------------------------------------------------

| Q17 \| Moderate \| Topic 10, Topic 03, Topic 16 \|

------------------------------------------------------------------------

| Q18 \| Moderate \| Topic 11, Topic 05 \|

------------------------------------------------------------------------

| Q19 \| Moderate \| Topic 12, Topic 18 \|

------------------------------------------------------------------------

| Q20 \| Moderate \| Topic 18, Topic 19 \|

------------------------------------------------------------------------

| Q21 \| Hard \| Topic 05, Topic 07, Topic 08, Topic 12, Topic 16 \|

------------------------------------------------------------------------

| Q22 \| Hard \| Topic 09, Topic 05, Topic 16 \|

------------------------------------------------------------------------

| Q23 \| Hard \| Topic 16, Topic 18, Topic 04 \|

------------------------------------------------------------------------

| Q24 \| Hard \| Topic 10, Topic 03, Topic 16 \|

------------------------------------------------------------------------

| Q25 \| Hard \| Topic 11, Topic 05, Topic 16 \|

------------------------------------------------------------------------

| Q26 \| Hard \| Topic 13, Topic 16, Topic 03 \|

------------------------------------------------------------------------

| Q27 \| Hard \| Topic 14, Topic 16, Topic 04 \|

------------------------------------------------------------------------

| Q28 \| Hard \| Topic 15, Topic 14, Topic 16 \|

------------------------------------------------------------------------

| Q29 \| Hard \| Topic 12, Topic 16, Topic 05 \|

------------------------------------------------------------------------

| Q30 \| Hard \| Topic 09, Topic 16, Topic 04 \|

------------------------------------------------------------------------

| Q31 \| Advanced \| Topic 02, Topic 03, Topic 04, Topic 05, Topic 07,
  Topic 08, Topic 09, Topic 10, Topic 11, Topic 16 \|

------------------------------------------------------------------------

| Q32 \| Advanced \| Topic 03, Topic 05, Topic 08, Topic 13, Topic 16 \|

------------------------------------------------------------------------

| Q33 \| Advanced \| Topic 15, Topic 14, Topic 16, Topic 03 \|

------------------------------------------------------------------------

| Q34 \| Advanced \| Topic 09, Topic 10, Topic 08, Topic 16, Topic 05 \|

------------------------------------------------------------------------

| Q35 \| Advanced \| Topic 14, Topic 08, Topic 16, Topic 03 \|

------------------------------------------------------------------------

| Q36 \| Advanced \| Topic 13, Topic 03, Topic 16, Topic 05 \|

------------------------------------------------------------------------

| Q37 \| Advanced \| Topic 05, Topic 09, Topic 13, Topic 04, Topic 16 \|

------------------------------------------------------------------------

| Q38 \| Advanced \| Topic 01, Topic 02, Topic 03, Topic 04, Topic 05,
  Topic 06, Topic 16, Topic 19 \|

------------------------------------------------------------------------

| Q39 \| Advanced \| Topic 17, Topic 18, Topic 19 \|

------------------------------------------------------------------------

| Q40 \| Advanced \| Topic 01--19 \|

------------------------------------------------------------------------

# SECTION A --- BASIC

------------------------------------------------------------------------

## Question 1 --- Interview format and scoring

### Difficulty

Basic

### Topics Covered

-   Topic 01
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A 45--60 minute Data Engineering system-design round begins with an
ambiguous platform problem. Explain how you would structure and navigate
it.

### Candidate Tasks

1.  Give a 45-minute plan
2.  name the evaluation dimensions
3.  distinguish system design from SQL/coding
4.  explain how you react to interviewer hints.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use requirements → estimates → architecture → deep dive →
trade-offs/failure → summary. The candidate is evaluated on
requirements, estimation, architecture, technical depth, trade-offs,
reliability/data quality, security/privacy, cost and communication.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if you do not know a technology?
-   What distinguishes Senior from Staff?

### Strong Candidate Answer

> Use requirements → estimates → architecture → deep dive →
> trade-offs/failure → summary. The candidate is evaluated on
> requirements, estimation, architecture, technical depth, trade-offs,
> reliability/data quality, security/privacy, cost and communication.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 2 --- Requirements clarification

### Difficulty

Basic

### Topics Covered

-   Topic 02, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design customer activity analytics when volume, freshness, retention and
consumers are unspecified.

### Candidate Tasks

1.  Ask high-value questions
2.  separate functional/non-functional requirements
3.  define MVP and out-of-scope.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Clarify users, sources, volume/peak, freshness, correctness, retention,
availability, privacy and cost before technology. State assumptions and
measurable SLAs.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   Which unknown would most change the architecture?
-   What would force streaming?

### Strong Candidate Answer

> Clarify users, sources, volume/peak, freshness, correctness,
> retention, availability, privacy and cost before technology. State
> assumptions and measurable SLAs.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 3 --- Daily event estimation

### Difficulty

Basic

### Topics Covered

-   Topic 03
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

50M users generate 20 events/user/day; average event size is 1 KB.
Estimate events/day, raw storage/day, annual storage and average
events/sec.

### Candidate Tasks

1.  Show formulas, units and a sanity check.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

1B events/day; about 1 TB/day raw using 1,000 bytes/KB; about 365
TB/year before compression/replication; about 11.6K average
events/sec. State assumptions and avoid false precision.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if peak is 5×?
-   What if event size doubles?

### Strong Candidate Answer

> 1B events/day; about 1 TB/day raw using 1,000 bytes/KB; about 365
> TB/year before compression/replication; about 11.6K average
> events/sec. State assumptions and avoid false precision.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 4 --- Batch or streaming

### Difficulty

Basic

### Topics Covered

-   Topic 05, Topic 07, Topic 08
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Finance needs a daily report by 7 AM. Source data is complete by 2 AM
and corrections can wait until the next day.

### Candidate Tasks

1.  Choose batch or streaming
2.  justify
3.  state when the choice changes.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Batch is the default because the freshness SLA is daily. Streaming adds
operational complexity without a stated benefit. Revisit if freshness
becomes minutes/seconds or continuous corrections are required.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   Would micro-batch change the answer?
-   What if source completeness is unreliable?

### Strong Candidate Answer

> Batch is the default because the freshness SLA is daily. Streaming
> adds operational complexity without a stated benefit. Revisit if
> freshness becomes minutes/seconds or continuous corrections are
> required.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 5 --- Communicating an architecture

### Difficulty

Basic

### Topics Covered

-   Topic 06, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Draw and explain a simple platform that ingests operational data and
serves curated analytics.

### Candidate Tasks

1.  Create a left-to-right diagram
2.  label stages
3.  explain it in two minutes.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Start Sources → Ingestion → Raw → Processing → Curated → Consumers. Add
quality, security, observability and cost as cross-cutting concerns.
Keep the diagram simple.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   Where is the quality gate?
-   Where would replay be represented?

### Strong Candidate Answer

> Start Sources → Ingestion → Raw → Processing → Curated → Consumers.
> Add quality, security, observability and cost as cross-cutting
> concerns. Keep the diagram simple.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 6 --- Duplicate batch output

### Difficulty

Basic

### Topics Covered

-   Topic 07, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A rerun leaves duplicate business records in yesterday's partition.
Diagnose and recover safely.

### Candidate Tasks

1.  Define target grain
2.  separate source/transformation/write causes
3.  prevent recurrence.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Inspect run history, input, join cardinality and write behavior. Recover
only affected scope, then reconcile. Use deterministic keys and
idempotent writes.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if the first run partially committed?
-   How do you distinguish join multiplication?

### Strong Candidate Answer

> Inspect run history, input, join cardinality and write behavior.
> Recover only affected scope, then reconcile. Use deterministic keys
> and idempotent writes.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 7 --- CDC latest-record SQL

### Difficulty

Basic

### Topics Covered

-   Topic 09, Topic 18
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A CDC table has customer_id, updated_at, operation and event_id. Select
the latest row per customer and explain delete semantics.

### Candidate Tasks

1.  State grain
2.  write SQL
3.  explain tie-breaking and deletes.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use ROW_NUMBER over customer_id ordered by updated_at plus deterministic
event/source-position tie-breaker. Define whether DELETE is a tombstone
or applied to the target.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   What if timestamps tie?
-   What if events arrive out of order?

### Strong Candidate Answer

> Use ROW_NUMBER over customer_id ordered by updated_at plus
> deterministic event/source-position tie-breaker. Define whether DELETE
> is a tombstone or applied to the target.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 8 --- Python data-quality validator

### Difficulty

Basic

### Topics Covered

-   Topic 16, Topic 18
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Write a Python validator for required columns, null customer IDs and
duplicate customer IDs.

### Candidate Tasks

1.  Return actionable errors
2.  distinguish blocking checks
3.  explain scale.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Keep it small and testable. Critical schema/key invariants can block
publication; large-scale implementations should use the processing
engine rather than collecting all data into Python.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   How would you test it?
-   How would you scale it?

### Strong Candidate Answer

> Keep it small and testable. Critical schema/key invariants can block
> publication; large-scale implementations should use the processing
> engine rather than collecting all data into Python.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 9 --- Behavioural ownership story

### Difficulty

Basic

### Topics Covered

-   Topic 17
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Answer: "Tell me about a production problem you owned." Use only a real
experience.

### Candidate Tasks

1.  Use a structured story
2.  show personal ownership
3.  quantify impact without inventing.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use context → problem → ownership → decision → action → result →
learning. Explain prevention and personal contribution.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What did you miss?
-   What would you change?

### Strong Candidate Answer

> Use context → problem → ownership → decision → action → result →
> learning. Explain prevention and personal contribution.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 10 --- Mini mock and self-review

### Difficulty

Basic

### Topics Covered

-   Topic 19
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Run a 15-minute batch-design mini mock and produce a self-review.

### Candidate Tasks

1.  Time-box
2.  record if possible
3.  score with evidence
4.  create one corrective action.

### Interview Constraints

**Time:** 10--15 minutes. **Expected level:** Foundational G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use Attempt → Record → Score → Diagnose → Correct → Re-attempt. Scores
must be evidence-based.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   When will you re-attempt?
-   Which error is recurring?

### Strong Candidate Answer

> Use Attempt → Record → Score → Diagnose → Correct → Re-attempt. Scores
> must be evidence-based.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

# SECTION B --- MODERATE

------------------------------------------------------------------------

## Question 11 --- Daily batch analytics

### Difficulty

Moderate

### Topics Covered

-   Topic 03, Topic 04, Topic 07
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design daily sales analytics for 2,000 stores with 6 AM freshness,
one-year retention and safe reruns.

### Candidate Tasks

1.  Clarify late stores
2.  estimate
3.  design ingestion/storage/processing/serving
4.  explain backfills.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Preserve raw inputs; process incrementally by stable boundaries; gate
publication on completeness/reconciliation; make reruns idempotent and
provide a controlled backfill path.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if 5% of stores are late?
-   What if a seven-day backfill is required?

### Strong Candidate Answer

> Preserve raw inputs; process incrementally by stable boundaries; gate
> publication on completeness/reconciliation; make reruns idempotent and
> provide a controlled backfill path.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 12 --- Incremental processing

### Difficulty

Moderate

### Topics Covered

-   Topic 02, Topic 04, Topic 05, Topic 07
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A historical sales table is too expensive to recompute daily. Design
incremental processing while preserving historical correction.

### Candidate Tasks

1.  Define change boundary
2.  handle old corrections
3.  design backfill.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use a trustworthy change indicator or CDC boundary, preserve raw history
and separate routine incremental processing from controlled backfills.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if the source timestamp is unreliable?
-   How do you prevent duplicate merges?

### Strong Candidate Answer

> Use a trustworthy change indicator or CDC boundary, preserve raw
> history and separate routine incremental processing from controlled
> backfills.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 13 --- Clickstream with late events

### Difficulty

Moderate

### Topics Covered

-   Topic 03, Topic 08, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design clickstream analytics with a two-minute freshness target while
events arrive late/out of order.

### Candidate Tasks

1.  Define event-time semantics
2.  estimate average/peak
3.  design replay and late-data handling.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Separate event, ingestion and processing time. Use durable streaming
plus raw replay; bounded lateness/watermarks or a correction path;
define provisional versus final results.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if consumers fall behind?
-   What if one key is extremely hot?

### Strong Candidate Answer

> Separate event, ingestion and processing time. Use durable streaming
> plus raw replay; bounded lateness/watermarks or a correction path;
> define provisional versus final results.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 14 --- CDC to lakehouse

### Difficulty

Moderate

### Topics Covered

-   Topic 09, Topic 16, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Replicate an operational customer database with inserts, updates and
deletes into a replayable lakehouse.

### Candidate Tasks

1.  Define snapshot/CDC boundary
2.  ordering
3.  duplicates
4.  reconciliation.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Make source position, event identity and raw change retention
first-class. Apply deterministic target merges and reconcile source
versus target.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if CDC lags an hour?
-   What if schema changes mid-stream?

### Strong Candidate Answer

> Make source position, event identity and raw change retention
> first-class. Apply deterministic target merges and reconcile source
> versus target.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 15 --- Streaming deduplication

### Difficulty

Moderate

### Topics Covered

-   Topic 08, Topic 12, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Retries create duplicate events in a stream. Deduplicate without
removing legitimate repeated events.

### Candidate Tasks

1.  Define identity
2.  bound state
3.  explain replay.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use stable event identity and an explicit duplicate-arrival horizon.
Keep raw events for replay and bound state/checkpoint recovery.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   What if event_id is not globally unique?
-   What if a duplicate arrives after the window?

### Strong Candidate Answer

> Use stable event identity and an explicit duplicate-arrival horizon.
> Keep raw events for replay and bound state/checkpoint recovery.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 16 --- IoT rate estimation

### Difficulty

Moderate

### Topics Covered

-   Topic 03, Topic 13
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

5M devices emit one event every 10 seconds. Estimate average events/sec
and a 10× peak.

### Candidate Tasks

1.  Calculate rates
2.  explain burst assumptions
3.  map result to architecture.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Average = 500K events/sec; illustrative 10× peak = 5M/sec. This implies
durable fan-in, partitioning, burst tolerance and backpressure.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if 10% reconnect simultaneously?
-   What if a few devices are much chattier?

### Strong Candidate Answer

> Average = 500K events/sec; illustrative 10× peak = 5M/sec. This
> implies durable fan-in, partitioning, burst tolerance and
> backpressure.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 17 --- Feature platform correctness

### Difficulty

Moderate

### Topics Covered

-   Topic 10, Topic 03, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Offline model metrics are excellent but online performance is poor.
Diagnose the feature platform.

### Candidate Tasks

1.  Check point-in-time correctness, training-serving skew and
    freshness.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Investigate leakage, point-in-time joins, stale online features,
mismatched transformations and feature versions. Validate timestamps and
offline/online parity.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if a feature arrives late?
-   How do you backfill safely?

### Strong Candidate Answer

> Investigate leakage, point-in-time joins, stale online features,
> mismatched transformations and feature versions. Validate timestamps
> and offline/online parity.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 18 --- Logs/metrics cost

### Difficulty

Moderate

### Topics Covered

-   Topic 11, Topic 05
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Centralized logs and metrics need fast operational queries and long
retention. Design and identify cost drivers.

### Candidate Tasks

1.  Separate hot/historical use
2.  discuss cardinality
3.  define observability.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use durable ingestion, hot/queryable data for operations and lower-cost
historical retention. Control cardinality, indexing, retention and
replication.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   Why does cardinality matter?
-   What if storage cost doubles?

### Strong Candidate Answer

> Use durable ingestion, hot/queryable data for operations and
> lower-cost historical retention. Control cardinality, indexing,
> retention and replication.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 19 --- Attribution SQL

### Difficulty

Moderate

### Topics Covered

-   Topic 12, Topic 18
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Using click and conversion events, implement last-touch attribution
within seven days and reconcile results.

### Candidate Tasks

1.  Define grain
2.  select latest eligible touch
3.  handle late-event restatement.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Deduplicate inputs, join within the window, rank by event time, select
one touch per conversion, then reconcile attributed + unattributed
conversions to total conversions.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   What if a late click arrives after billing?
-   How do you make reruns deterministic?

### Strong Candidate Answer

> Deduplicate inputs, join within the window, rank by event time, select
> one touch per conversion, then reconcile attributed + unattributed
> conversions to total conversions.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 20 --- Live pipeline exercise

### Difficulty

Moderate

### Topics Covered

-   Topic 18, Topic 19
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Build an orders pipeline: validate schema, deduplicate order IDs,
calculate daily revenue, test it and explain productionization.

### Candidate Tasks

1.  Clarify grain
2.  implement
3.  test
4.  explain idempotency and recovery.

### Interview Constraints

**Time:** 15--25 minutes. **Expected level:** Intermediate G5 learner.
Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Build the smallest correct solution. Test invalid/duplicate/empty cases.
Make output deterministic and safe to rerun; explain durable storage,
orchestration, retries and observability.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   How would it scale?
-   How would you recover a partial write?

### Strong Candidate Answer

> Build the smallest correct solution. Test invalid/duplicate/empty
> cases. Make output deterministic and safe to rerun; explain durable
> storage, orchestration, retries and observability.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

# SECTION C --- HARD

------------------------------------------------------------------------

## Question 21 --- Real-time plus final correctness

### Difficulty

Hard

### Topics Covered

-   Topic 05, Topic 07, Topic 08, Topic 12, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design two-minute provisional analytics and billing-grade final
attribution after a seven-day correction window.

### Candidate Tasks

1.  Separate provisional/final contracts
2.  estimate
3.  design stream/correction paths
4.  explain restatement.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use durable stream + raw immutable data + fresh aggregates + batch
correction/finalization. Define the business finality boundary and
version/restatement policy.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if a late event arrives after finalization?
-   How are consumers notified?

### Strong Candidate Answer

> Use durable stream + raw immutable data + fresh aggregates + batch
> correction/finalization. Define the business finality boundary and
> version/restatement policy.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 22 --- CDC schema evolution

### Difficulty

Hard

### Topics Covered

-   Topic 09, Topic 05, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A source adds a column while CDC processes 500K changes/sec and
consumers still expect the old schema.

### Candidate Tasks

1.  Define compatibility
2.  handle mixed versions
3.  design detection/recovery.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Prefer compatible additive evolution; version/stage breaking changes;
preserve raw events; quarantine unsafe records and replay after contract
repair.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if a type changes?
-   What if one consumer cannot upgrade?

### Strong Candidate Answer

> Prefer compatible additive evolution; version/stage breaking changes;
> preserve raw events; quarantine unsafe records and replay after
> contract repair.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 23 --- Spark 10× slowdown

### Difficulty

Hard

### Topics Covered

-   Topic 16, Topic 18, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A PySpark job grows from 20 minutes to 200 minutes. Diagnose before
changing code.

### Candidate Tasks

1.  Use evidence
2.  separate input growth from regression
3.  inspect skew/shuffle/joins.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Inspect input volume, Spark stages, task distribution, spills, execution
plan and join strategy. Scale only after identifying the bottleneck,
then validate correctness.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Coding Example

``` python
# Production-thinking prompt:
# implement the smallest correct transformation, then add
# tests for duplicates, nulls, retries or idempotency as relevant.
```

### Interview Follow-Up Questions

-   What if one partition is 20× larger?
-   When would you change the join strategy?

### Strong Candidate Answer

> Inspect input volume, Spark stages, task distribution, spills,
> execution plan and join strategy. Scale only after identifying the
> bottleneck, then validate correctness.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 24 --- Feature backfill without leakage

### Difficulty

Hard

### Topics Covered

-   Topic 10, Topic 03, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Backfill one year of ML features after correcting a transformation bug
without contaminating historical training data.

### Candidate Tasks

1.  Define feature timestamps
2.  estimate
3.  isolate/version backfill
4.  validate.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Compute point-in-time-correct features, isolate the new version,
validate samples/distributions, then promote. Never use information
after prediction time.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if raw history is incomplete?
-   How do you prove unrelated dates were unchanged?

### Strong Candidate Answer

> Compute point-in-time-correct features, isolate the new version,
> validate samples/distributions, then promote. Never use information
> after prediction time.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 25 --- High-cardinality observability cost

### Difficulty

Hard

### Topics Covered

-   Topic 11, Topic 05, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Log storage cost doubles while traffic is flat. Investigate and
remediate without blindly deleting evidence.

### Candidate Tasks

1.  Attribute cost
2.  separate hot/historical needs
3.  preserve operational evidence.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Decompose volume, retention, indexing/cardinality, replication and query
cost. Reduce unnecessary cardinality/indexing and use retention tiers
while preserving required evidence.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if every metric contains a unique request ID?
-   What if compliance requires one-year retention?

### Strong Candidate Answer

> Decompose volume, retention, indexing/cardinality, replication and
> query cost. Reduce unnecessary cardinality/indexing and use retention
> tiers while preserving required evidence.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 26 --- IoT reconnect storm

### Difficulty

Hard

### Topics Covered

-   Topic 13, Topic 16, Topic 03
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A regional outage causes 10% of a 5M-device fleet to reconnect together.

### Candidate Tasks

1.  Estimate burst
2.  identify bottlenecks
3.  design backoff/admission
4.  protect downstream.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

500K devices reconnect. Actual connection rate depends on the retry
window. Use client backoff, admission control, durable buffering and
downstream protection.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if devices retry every second?
-   How do you avoid a thundering herd?

### Strong Candidate Answer

> 500K devices reconnect. Actual connection rate depends on the retry
> window. Use client backoff, admission control, durable buffering and
> downstream protection.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 27 --- GDPR deletion across derived data

### Difficulty

Hard

### Topics Covered

-   Topic 14, Topic 16, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A user must be deleted from raw events, curated tables, aggregates,
features, vector indexes and caches.

### Candidate Tasks

1.  Build identity map
2.  trace derived data
3.  design retries and proof.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Treat deletion as a lineage workflow. Resolve identities, enumerate
derived assets, execute idempotent deletion, verify every target and
record evidence.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if a vector index is stale?
-   What if replay resurrects deleted data?

### Strong Candidate Answer

> Treat deletion as a lineage workflow. Resolve identities, enumerate
> derived assets, execute idempotent deletion, verify every target and
> record evidence.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 28 --- RAG ACL propagation failure

### Difficulty

Hard

### Topics Covered

-   Topic 15, Topic 14, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A document ACL changes but its vector representation remains retrievable
by an unauthorized user.

### Candidate Tasks

1.  Contain exposure
2.  trace authorization
3.  repair index/cache
4.  add regression tests.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Contain first. Current authorization must be enforced at retrieval;
stale derived ACL/index state must be invalidated/rebuilt. Audit and
test.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if a cache contains old results?
-   How do you prove the path is safe?

### Strong Candidate Answer

> Contain first. Current authorization must be enforced at retrieval;
> stale derived ACL/index state must be invalidated/rebuilt. Audit and
> test.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 29 --- Attribution replay changes billing

### Difficulty

Hard

### Topics Covered

-   Topic 12, Topic 16, Topic 05
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A replay after a stream outage changes yesterday's billing attribution.

### Candidate Tasks

1.  Distinguish expected correction from corruption
2.  trace dedup/late events
3.  define restatement.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Compare event-level evidence and replay scope. Use
deterministic/idempotent processing, reconciliation and versioned
restatement. Do not assume every change is a bug.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if finance already invoiced?
-   How do you reconcile before restatement?

### Strong Candidate Answer

> Compare event-level evidence and replay scope. Use
> deterministic/idempotent processing, reconciliation and versioned
> restatement. Do not assume every change is a bug.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 30 --- CDC correctness incident

### Difficulty

Hard

### Topics Covered

-   Topic 09, Topic 16, Topic 04
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

CDC reports successful runs but analysts find missing updates.

### Candidate Tasks

1.  Determine blast radius
2.  trace capture → transport → processing → target
3.  recover and validate.

### Interview Constraints

**Time:** 25--35 minutes. **Expected level:** Senior Data Engineer. Stop
before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

A green orchestration status is not proof of data correctness. Find the
first divergence, contain affected outputs, replay the smallest safe
range and reconcile end-to-end.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if raw CDC is also incomplete?
-   What if target merge is non-idempotent?

### Strong Candidate Answer

> A green orchestration status is not proof of data correctness. Find
> the first divergence, contain affected outputs, replay the smallest
> safe range and reconcile end-to-end.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

# SECTION D --- ADVANCED

------------------------------------------------------------------------

## Question 31 --- Multi-domain platform with conflicting SLAs

### Difficulty

Advanced

### Topics Covered

-   Topic 02, Topic 03, Topic 04, Topic 05, Topic 07, Topic 08, Topic
    09, Topic 10, Topic 11, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

One platform must support batch BI, real-time analytics, CDC and ML
features with different freshness/correctness requirements under a
constrained budget.

### Candidate Tasks

1.  Clarify conflicting SLAs
2.  estimate workloads
3.  choose shared versus specialized layers
4.  defend boundaries.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Standardize durable contracts, governance, observability and recovery.
Specialize execution/serving where requirements differ. Do not force
every workload onto one engine.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What changes at 10×?
-   What if budget falls 30%?

### Strong Candidate Answer

> Standardize durable contracts, governance, observability and recovery.
> Specialize execution/serving where requirements differ. Do not force
> every workload onto one engine.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 32 --- Targeted 10× redesign

### Difficulty

Advanced

### Topics Covered

-   Topic 03, Topic 05, Topic 08, Topic 13, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A working event platform must handle 10× traffic without a total
rewrite.

### Candidate Tasks

1.  Recalculate load
2.  identify first bottlenecks
3.  change only constrained components
4.  quantify cost.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Multiply workload assumptions by 10, locate capacity boundaries, then
scale partitioning, processing, storage or serving only where evidence
shows pressure. Add backpressure and protect correctness.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if one key is hot?
-   What if cost grows faster than traffic?

### Strong Candidate Answer

> Multiply workload assumptions by 10, locate capacity boundaries, then
> scale partitioning, processing, storage or serving only where evidence
> shows pressure. Add backpressure and protect correctness.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 33 --- Enterprise RAG lifecycle

### Difficulty

Advanced

### Topics Covered

-   Topic 15, Topic 14, Topic 16, Topic 03
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design RAG over documents, tickets and databases with ACLs, freshness,
deletion and measurable retrieval evaluation.

### Candidate Tasks

1.  Estimate documents/chunks/query load
2.  design versioned ingestion/indexes
3.  make retrieval permission-aware
4.  define evaluation.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Canonical source data is authoritative; indexes are derived and
rebuildable. Enforce current authorization at retrieval, propagate
deletes, version embeddings/indexes and monitor
quality/freshness/latency/cost.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if ACL changes faster than reindexing?
-   How do you detect retrieval degradation?

### Strong Candidate Answer

> Canonical source data is authoritative; indexes are derived and
> rebuildable. Enforce current authorization at retrieval, propagate
> deletes, version embeddings/indexes and monitor
> quality/freshness/latency/cost.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 34 --- Feature + CDC + streaming consistency

### Difficulty

Advanced

### Topics Covered

-   Topic 09, Topic 10, Topic 08, Topic 16, Topic 05
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A feature depends on CDC and real-time events. A schema change causes
offline and online feature divergence.

### Candidate Tasks

1.  Trace semantic divergence
2.  design versioned contracts
3.  recover both paths
4.  prevent recurrence.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Identify the first semantic mismatch, version the feature contract,
isolate bad outputs, rebuild affected data and validate point-in-time
correctness plus online freshness.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   How do you roll back a feature definition?
-   What if online storage cannot rebuild quickly?

### Strong Candidate Answer

> Identify the first semantic mismatch, version the feature contract,
> isolate bad outputs, rebuild affected data and validate point-in-time
> correctness plus online freshness.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 35 --- GDPR during streaming backlog

### Difficulty

Advanced

### Topics Covered

-   Topic 14, Topic 08, Topic 16, Topic 03
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A deletion request arrives while a large streaming backlog exists. The
user must not remain retrievable after the deletion SLA.

### Candidate Tasks

1.  Define deletion ordering
2.  design immediate protection
3.  prevent replay resurrection
4.  prove completion.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Separate immediate access revocation from physical cleanup. Durable
deletion state must be honored by streaming, replay and serving paths.
Verify every required target.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if replay contains the deleted user's event?
-   What if a cache is unavailable?

### Strong Candidate Answer

> Separate immediate access revocation from physical cleanup. Durable
> deletion state must be honored by streaming, replay and serving paths.
> Verify every required target.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 36 --- IoT clock skew and hot devices

### Difficulty

Advanced

### Topics Covered

-   Topic 13, Topic 03, Topic 16, Topic 05
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Design 5M-device telemetry ingestion with unreliable clocks,
out-of-order data, hot devices and unreliable connectivity.

### Candidate Tasks

1.  Estimate baseline/peak
2.  separate device/event/ingestion time
3.  handle skew/hot keys
4.  design replay.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use device and event identity, preserve ingestion time, validate event
time, use bounded lateness where appropriate, partition to reduce
hotspots and retain raw data.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if one device emits 1M events/hour?
-   What if device time moves backward?

### Strong Candidate Answer

> Use device and event identity, preserve ingestion time, validate event
> time, use bounded lateness where appropriate, partition to reduce
> hotspots and retain raw data.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 37 --- Build vs managed ingestion

### Difficulty

Advanced

### Topics Covered

-   Topic 05, Topic 09, Topic 13, Topic 04, Topic 16
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Choose between custom ingestion and managed connectors. Managed costs
more but reduces operational work.

### Candidate Tasks

1.  Define evaluation criteria
2.  estimate total cost
3.  choose and state exit conditions.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Compare reliability, coverage, freshness, security, support, engineering
effort, incident risk and unit economics. Managed ingestion reduces
plumbing, not responsibility.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What if volume grows 10×?
-   What if the managed connector misses the SLA?

### Strong Candidate Answer

> Compare reliability, coverage, freshness, security, support,
> engineering effort, incident risk and unit economics. Managed
> ingestion reduces plumbing, not responsibility.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 38 --- 45-minute design simulation

### Difficulty

Advanced

### Topics Covered

-   Topic 01, Topic 02, Topic 03, Topic 04, Topic 05, Topic 06, Topic
    16, Topic 19
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Run a full marketplace analytics system-design interview with a 10×
pushback and a late-source failure.

### Candidate Tasks

1.  Clarify in 5m
2.  estimate in 5m
3.  design in 15m
4.  deep dive/failure/trade-offs in 15m
5.  summarize in 5m.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use the G5 interview loop. Do not read the solution until after scoring.
Evaluate structure, timing, technical reasoning, trade-offs, failure
handling and communication.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What changed after 10×?
-   What requirement would switch execution models?

### Strong Candidate Answer

> Use the G5 interview loop. Do not read the solution until after
> scoring. Evaluate structure, timing, technical reasoning, trade-offs,
> failure handling and communication.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 39 --- Full Senior loop and readiness report

### Difficulty

Advanced

### Topics Covered

-   Topic 17, Topic 18, Topic 19
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

Simulate SQL/Python, system design, failure, behavioural and live
pipeline rounds, then produce an evidence-based readiness report.

### Candidate Tasks

1.  Time-box each round
2.  score independently
3.  identify three recurring errors
4.  plan re-attempts.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Use Topic 19: record where possible, score with evidence, log root
causes and re-attempt after a delay. Readiness is consistency across
modes.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   Which weakness is systemic?
-   Which category improved most?

### Strong Candidate Answer

> Use Topic 19: record where possible, score with evidence, log root
> causes and re-attempt after a delay. Readiness is consistency across
> modes.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

## Question 40 --- Capstone multi-modal platform

### Difficulty

Advanced

### Topics Covered

-   Topic 01--19
-   Requirements, estimation, architecture, trade-offs, reliability and
    communication

### Problem Statement

A marketplace grows 10× and now has CDC, clickstream, partner telemetry,
batch finance, ML features and a RAG assistant. It requires analytics,
near-real-time use cases, privacy/deletion, reliable recovery and
controlled cost.

### Candidate Tasks

1.  Clarify SLAs/scope
2.  estimate
3.  design end-to-end
4.  define quality/security/observability/cost
5.  defend trade-offs and Senior/Staff reasoning.

### Interview Constraints

**Time:** 35--45+ minutes. **Expected level:** Senior/Staff Data
Engineer. Stop before reading the solution.

------------------------------------------------------------------------

# Solution

### 1. How to Approach the Problem

Separate shared durable/governed primitives from workload-specific
paths. Use batch where appropriate, streaming where freshness requires
it, replayable CDC, governed feature pipelines, permission-aware RAG and
deletion controls that survive replay.

### 2. Requirements Clarification

Ask about users/consumers, sources, volume and peak, freshness,
correctness, retention, replay/backfill, security/privacy and cost. For
complex questions, identify the unknown with the greatest architectural
impact.

### 3. Estimation

State assumptions, convert units, calculate average and peak load where
relevant, estimate storage/throughput, identify bottlenecks and explain
uncertainty. Illustrative numbers are assumptions, not universal facts.

### 4. Architecture / Design

Use the G5 lifecycle:

``` text
Requirements → Estimates → Data Flow → Storage → Processing → Serving
                         ↘ Quality / Reliability / Security / Cost
```

Choose technology only after requirements. Keep the simplest
architecture that satisfies the stated SLA.

### 5. Data Flow

Source → ingestion → durable/replayable data → processing → validation →
curated/serving → consumers. Put checkpoints, deduplication, backfills,
authorization or deletion controls at explicit boundaries where
relevant.

### Architecture Diagram

``` mermaid
flowchart LR
A[Sources] --> B[Ingestion]
B --> C[Durable Raw]
C --> D[Processing + Quality]
D --> E[Curated / Serving]
E --> F[Consumers]
G[Governance / Observability / Cost] --- B
G --- D
G --- E
```

### 6. Trade-offs

Use:

> **Requirement → Options → Evaluation → Decision → Trade-off → When the
> decision changes**

Use only trade-offs supported by the case: batch/streaming,
full/incremental, managed/custom, hot/cold, synchronous/asynchronous,
stronger guarantees versus cost/complexity.

### 7. Reliability and Failure Handling

Use:

``` text
Detect → Diagnose → Contain → Recover → Validate → Prevent
```

Consider retries, idempotency, replay, late data, schema failure,
consumer lag, partial writes and blast radius where relevant.

### 8. Data Quality / Correctness

Define grain and invariants. Use completeness, uniqueness,
reconciliation, freshness, schema validation, point-in-time correctness
or deletion verification as appropriate. A successful job is not proof
of correct data.

### 9. Security / Privacy

Apply least privilege, governed identities, data minimization,
authorization freshness and deletion/privacy requirements when relevant.
Do not invent requirements; clarify them.

### 10. Observability

Separate system health from data health. Track throughput, lag,
freshness, failures, quality violations, reconciliation, backlog,
serving latency and cost.

### 11. Cost and Scalability

Estimate dominant cost drivers. At 10×, scale the bottleneck rather than
multiplying every component. Consider retention, replication, compute,
indexing and state where relevant.

### Interview Follow-Up Questions

-   What is the first bottleneck?
-   How do you prevent deleted data returning through replay?
-   How do you reconcile provisional/final results?
-   What do you cut if budget falls 30%?

### Strong Candidate Answer

> Separate shared durable/governed primitives from workload-specific
> paths. Use batch where appropriate, streaming where freshness requires
> it, replayable CDC, governed feature pipelines, permission-aware RAG
> and deletion controls that survive replay.

### Common Mistakes

-   Choosing technology before requirements.
-   Giving architecture without assumptions or scale.
-   Ignoring correctness, recovery or backfills.
-   Treating a green pipeline run as proof of correct data.
-   Overengineering when a simpler design satisfies the SLA.
-   Failing to explain trade-offs or change conditions.
-   For behavioural questions, inventing experiences or metrics.

### Senior-Level Insight

A strong Senior candidate makes assumptions explicit, connects
architecture choices to requirements, handles operational failure,
explains trade-offs and protects data correctness.

### Staff-Level Insight

A strong Staff candidate additionally reduces ambiguity, identifies
system-wide and organizational implications, simplifies where possible,
creates platform leverage through contracts/governance, and reasons
about long-term cost, risk and influence.

### Self-Score

Requirements: /5\
Estimation: /5\
Architecture/Approach: /5\
Trade-offs: /5\
Failure handling: /5\
Correctness: /5\
Communication: /5\
Technical depth: /5

------------------------------------------------------------------------

# FINAL COVERAGE AUDIT

## Topic Coverage Audit

  ----------------------------------------------------------------------------
  Source Topic            Questions               Coverage
  ----------------------- ----------------------- ----------------------------
  01                      Q1, Q10, Q38--Q40       interview format, rubric,
                                                  timing, readiness

  02                      Q2, Q11--Q40            requirements, scope,
                                                  ambiguity

  03                      Q3, Q11--Q40            rates, storage, peak,
                                                  capacity

  04                      Q1--Q2, Q5, Q11--Q40    reusable design framework

  05                      Q4, Q11--Q40            trade-offs, execution
                                                  models, cost

  06                      Q5, Q38--Q40            diagramming and
                                                  communication

  07                      Q4, Q6, Q11--Q12, Q21,  batch, reruns, backfills
                          Q40                     

  08                      Q4, Q13, Q15, Q21, Q26, streaming, event time, lag,
                          Q35--Q40                replay

  09                      Q7, Q14, Q22, Q30, Q34, CDC, ordering, schema,
                          Q40                     reconciliation

  10                      Q17, Q24, Q34, Q40      features, point-in-time
                                                  correctness

  11                      Q18, Q25, Q40           logs/metrics, cardinality,
                                                  cost

  12                      Q19, Q29, Q40           attribution, dedup,
                                                  restatement

  13                      Q16, Q26, Q36, Q40      IoT fan-in, skew, bursts

  14                      Q27, Q35, Q40           deletion, lineage, replay

  15                      Q28, Q33, Q40           RAG, vector data, ACLs

  16                      Q6, Q13--Q40            failure and deep-dive
                                                  reasoning

  17                      Q9, Q39--Q40            behavioural evidence

  18                      Q7--Q8, Q19--Q20,       Python/SQL/pipeline
                          Q39--Q40                reasoning

  19                      Q10, Q20, Q38--Q40      mock/self-review/readiness
  ----------------------------------------------------------------------------

## Cross-Cutting Concept Audit

Requirements, scoping, estimation, architecture, batch, streaming, CDC,
storage, processing, partitioning, data quality, correctness,
idempotency, deduplication, backfills, late data, schema evolution,
reliability, failure handling, observability, security, privacy, cost,
scalability, trade-offs, communication, behavioural reasoning, coding,
debugging, testing, productionization, mock interviewing and self-review
are collectively exercised across the bank.

# FINAL PRACTICE STRATEGY

### Pass 1 --- Learning

Solve without time pressure.

### Pass 2 --- Timed

Use the suggested interview time.

### Pass 3 --- No Notes

Repeat weak questions without the roadmap.

### Pass 4 --- Recorded

Record system-design, failure and behavioural answers.

### Pass 5 --- Mock

Use a peer/mentor as interviewer and add pushback.

### Pass 6 --- Re-attempt

Redo weak questions after a delay.

## Topic 19 Practice Evidence

Track at least: - 6 design mocks - 3 partner design mocks - 2
follow-up-only mocks - 2 behavioural mocks - recordings and scoring - an
error log - 3 recurring mistakes eliminated - 2 peer interviews - 1
company-specific brief

# FINAL SCORECARD

  Question        Attempt 1   Attempt 2   Attempt 3   Final Weakness
  ------------- ----------- ----------- ----------- ------- ----------
  Q1                                                        
  Q2                                                        
  Q3                                                        
  Q4                                                        
  Q5                                                        
  Q6                                                        
  Q7                                                        
  Q8                                                        
  Q9                                                        
  Q10                                                       
  Q11                                                       
  Q12                                                       
  Q13                                                       
  Q14                                                       
  Q15                                                       
  Q16                                                       
  Q17                                                       
  Q18                                                       
  Q19                                                       
  Q20                                                       
  Q21                                                       
  Q22                                                       
  Q23                                                       
  Q24                                                       
  Q25                                                       
  Q26                                                       
  Q27                                                       
  Q28                                                       
  Q29                                                       
  Q30                                                       
  Q31                                                       
  Q32                                                       
  Q33                                                       
  Q34                                                       
  Q35                                                       
  Q36                                                       
  Q37                                                       
  Q38                                                       
  Q39                                                       
  Q40                                                       
  **Overall**                                               

Track Basic, Moderate, Hard, Advanced, system-design, coding, failure,
behavioural and communication averages.

# G5 PRACTICE READINESS CHECKLIST

-   [ ] Clarify ambiguous requirements.
-   [ ] Estimate rate, storage, peak and capacity.
-   [ ] Apply the reusable design framework.
-   [ ] Explain trade-offs.
-   [ ] Draw and communicate designs.
-   [ ] Design all nine G5 case domains.
-   [ ] Handle late data, duplicates, schema changes and backfills.
-   [ ] Diagnose failures using evidence.
-   [ ] Address security/privacy and GDPR deletion.
-   [ ] Handle RAG authorization and freshness.
-   [ ] Complete Data Engineering Python/SQL/PySpark/pipeline exercises.
-   [ ] Answer behavioural questions using real experience.
-   [ ] Run realistic mocks.
-   [ ] Self-score using evidence.
-   [ ] Maintain an error log and re-attempt weak areas.
-   [ ] Demonstrate Senior-level reasoning.
-   [ ] Demonstrate Staff-level reasoning where applicable.

# FINAL READINESS INTERPRETATION

These are **practice guidelines, not universal hiring thresholds**.

  -----------------------------------------------------------------------
                                   Average Interpretation
  ---------------------------------------- ------------------------------
                                      1--2 Major gaps

                                      2--3 Developing

                                      3--4 Interview-capable but
                                           inconsistent

                                        4+ Strong practice performance

                 Consistent 4+ on Advanced Strong evidence of
                                           Senior-level interview
                                           readiness
  -----------------------------------------------------------------------

Staff-oriented readiness additionally requires evidence across ambiguity
reduction, influence, strategic trade-offs, organizational impact,
architecture leverage and systemic failure reasoning.

# FINAL OPERATING STANDARD

``` text
Clarify → Estimate → Design → Communicate → Implement
→ Validate → Handle Failure → Explain Trade-offs
→ Scale → Defend → Score → Diagnose → Correct → Re-attempt
```

> **Do not memorize the 40 answers. Use the bank to become capable of
> reasoning through unfamiliar Data Engineering interview problems under
> realistic conditions.**
