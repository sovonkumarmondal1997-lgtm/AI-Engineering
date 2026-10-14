# 19 — Mock Interview Plans and Self-Review

> **Phase F — The Practice System (Ongoing)**
>
> This is the final topic of G5 — Data Engineering System Design Interviews. Its purpose is to turn Topics 01–18 into repeatable interview performance.
>
> **Core operating loop:**  
> **Prepare → Attempt → Record → Score → Diagnose → Correct → Re-attempt → Mock Again → Measure Progress → Become Interview Ready**

---

## 1. Module Overview

Topic 19 is not a question bank. It is a **complete practice and readiness system** for Senior and Staff Data Engineering interviews.

The authoritative G5 roadmap places Topic 19 after interview format, requirements, estimation, design framework, trade-offs, diagramming, nine design cases, failure/deep-dive practice, behavioural interviews, and take-home/live coding. Its purpose is to turn that knowledge into measurable performance through mocks, recordings, scoring, error logs, re-attempts, peer practice, and company-specific preparation. fileciteturn186file3

### What this module teaches

You will learn how to:

- build a realistic mock-interview schedule
- select and rotate cases
- simulate real interview conditions
- time-box answers
- record and review yourself
- score performance with a consistent rubric
- distinguish knowledge gaps from execution gaps
- maintain an error log
- design corrective actions
- re-attempt weak areas using spaced repetition
- run system-design, failure, behavioural, coding, and full-loop mocks
- handle interviewer pushback
- track improvement objectively
- prepare for a specific company/domain
- determine whether your performance is Senior-ready
- identify the additional evidence required for Staff readiness

### The central principle

> **Do not practice randomly. Build a measurable interview-training system.**

The roadmap recommends a 4-week preparation period at roughly 8–10 hours per week, followed by ongoing mocks—typically two to three per week—until interviews. fileciteturn186file3

---

# 2. Why Mock Interviews Matter

Knowing Data Engineering is not the same as demonstrating Data Engineering under interview conditions.

There are at least four different capabilities:

```text
Knowledge
    ↓
Problem Solving
    ↓
Execution Under Time Pressure
    ↓
Communication Under Pressure
```

A candidate can know:

- Kafka
- Spark
- CDC
- lakehouses
- warehouses
- data quality
- distributed systems

and still perform poorly because they:

- start designing before clarifying requirements
- cannot estimate scale
- spend 20 minutes on one detail
- cannot explain trade-offs
- freeze during follow-ups
- cannot recover after a wrong assumption
- write code without testing
- give weak behavioural evidence

### Studying vs practicing

| Activity | What it develops |
|---|---|
| Reading | Knowledge |
| Watching solutions | Pattern recognition |
| Solving casually | Problem solving |
| Timed practice | Execution |
| Recording | Communication awareness |
| Mock interview | Integrated performance |
| Self-review | Diagnosis |
| Re-attempt | Skill correction |
| Repeated mocks | Consistency |

### The important distinction

> **Knowing the answer and being able to communicate the answer under interview pressure are different skills.**

---

# 3. Topic 19 Position in G5

Topic 19 integrates:

| Earlier topic | Capability reused here |
|---|---|
| 01 | Interview format and evaluation rubric |
| 02 | Requirements clarification |
| 03 | Estimation |
| 04 | Reusable design framework |
| 05 | Trade-offs |
| 06 | Diagramming and communication |
| 07 | Batch analytics |
| 08 | Real-time analytics |
| 09 | CDC |
| 10 | ML feature platform |
| 11 | Logs and metrics |
| 12 | Attribution and deduplication |
| 13 | IoT telemetry |
| 14 | GDPR deletion |
| 15 | RAG/vector platform |
| 16 | Failures and deep dives |
| 17 | Behavioural interviews |
| 18 | Take-home/live coding |
| **19** | **Practice, self-review, readiness** |

The dependency is therefore:

```text
Learn the method
      ↓
Apply to cases
      ↓
Survive deep dives
      ↓
Tell evidence-based stories
      ↓
Implement under pressure
      ↓
Practice repeatedly
      ↓
Measure improvement
```

---

# 4. Interview Readiness Model

Use this model:

```text
Knowledge
+
Problem Solving
+
System Design
+
Technical Depth
+
Communication
+
Behavioural Evidence
+
Coding
+
Time Management
+
Failure Handling
+
Interview Presence
=
Interview Readiness
```

### 4.1 Knowledge

Can you explain the underlying concepts?

### 4.2 Problem solving

Can you turn an ambiguous prompt into a tractable problem?

### 4.3 System design

Can you build an architecture from requirements, estimates, storage, processing, serving, and cross-cutting concerns?

### 4.4 Technical depth

Can you answer:

> "Why?"

and then:

> "What happens if that fails?"

### 4.5 Communication

Can the interviewer follow your reasoning?

### 4.6 Behavioural evidence

Can you prove ownership, judgment, influence, conflict management, and learning using real examples?

### 4.7 Coding

Can you implement a correct solution rather than merely describe one?

### 4.8 Time management

Can you finish the important parts before the interview ends?

### 4.9 Failure handling

Can you reason from symptom → evidence → recovery → prevention?

### 4.10 Interview presence

Can you stay composed, listen, adapt, and collaborate?

---

# 5. Interview Types to Practice

Topic 19 should cover ten practice modes.

1. Data Engineering system design
2. Failure/deep-dive interviews
3. Behavioural interviews
4. Python coding
5. SQL coding
6. PySpark coding
7. Live pipeline coding
8. Take-home assignments
9. Technical deep dives
10. Full interview loops

These modes should **not** be practiced identically.

| Mode | Primary skill |
|---|---|
| System design | Structured architecture reasoning |
| Failure | Diagnosis and recovery |
| Behavioural | Evidence-based communication |
| Python | Implementation |
| SQL | Data reasoning |
| PySpark | Distributed implementation |
| Live pipeline | Coding + communication |
| Take-home | End-to-end engineering |
| Deep dive | Technical depth |
| Full loop | Integrated performance |

---

# 6. Realistic Mock Interview Environment

A mock becomes useful when its conditions resemble the real interview.

## Reproduce

- realistic time limit
- no notes unless the real interview permits them
- whiteboard/diagramming
- screen sharing when relevant
- coding environment
- interviewer prompts
- follow-up questions
- interruptions
- pushback
- incomplete information
- changing requirements
- time pressure

### Poor practice environment

```text
Unlimited time
+
Open documentation
+
Pause whenever uncomfortable
+
Read the solution immediately
+
No recording
```

This produces **false confidence**.

### Better environment

```text
Prompt
  ↓
Timer
  ↓
Think aloud
  ↓
Draw / code
  ↓
Interviewer pushback
  ↓
Finish
  ↓
Record
  ↓
Score
  ↓
Review
```

---

# 7. Mock Interview Rules

## During the mock

- Treat it as real.
- Do not search the web unless the interview permits it.
- Do not look at notes unless explicitly permitted.
- Clarify ambiguous requirements.
- State assumptions.
- Think aloud.
- Track time.
- Draw architecture.
- Explain trade-offs.
- Test code.
- Respond to follow-ups.
- Recover from mistakes.
- Do not become defensive when challenged.

## After the mock

Do **not** immediately read the reference solution.

Instead:

1. write down what you remember
2. score yourself
3. identify failures
4. identify root causes
5. define corrective actions
6. compare against the reference
7. update the error log
8. schedule a re-attempt

This creates useful diagnostic evidence.

---

# 8. Master Practice Loop

Use this loop for every major practice session:

```text
Learn
  ↓
Attempt
  ↓
Record
  ↓
Score
  ↓
Compare
  ↓
Identify Gaps
  ↓
Log Mistakes
  ↓
Study Weak Area
  ↓
Re-attempt
  ↓
Timed Mock
  ↓
Full Mock
  ↓
Measure Improvement
  ↓
Repeat
```

### Step 1 — Learn

Understand the method, not merely the answer.

### Step 2 — Attempt

Solve without looking at the reference.

### Step 3 — Record

Record audio and screen when practical.

### Step 4 — Score

Use the same rubric every time.

### Step 5 — Compare

Compare your reasoning with:

- Topic 01 rubric
- reference designs
- your prior work
- interviewer feedback

### Step 6 — Diagnose

Ask:

> What specifically failed?

### Step 7 — Correct

Study only the weak capability.

### Step 8 — Re-attempt

Return after a delay.

### Step 9 — Mock

Have someone challenge your assumptions.

### Step 10 — Measure

Track whether the same error recurs.

The roadmap explicitly recommends this Learn → Attempt → Record → Compare → Score → Log → Re-attempt → Mock → Update cycle. fileciteturn186file3

---

# 9. Self-Review Framework

After every mock, review five dimensions.

## 9.1 Technical reasoning

- Did I understand the problem?
- Did I clarify requirements?
- Did I estimate scale?
- Did I identify bottlenecks?
- Did I choose an appropriate architecture?
- Did I define data grain?
- Did I discuss data quality?
- Did I discuss reliability?
- Did I discuss security?
- Did I discuss cost?
- Did I handle failures?
- Did I explain trade-offs?

## 9.2 Communication

- Was I structured?
- Did I think aloud?
- Did I answer the actual question?
- Did I ramble?
- Were assumptions explicit?
- Did I summarize decisions?

## 9.3 Interview behaviour

- Did I listen?
- Did I respond to pushback?
- Did I accept hints productively?
- Did I recover from mistakes?
- Did I collaborate rather than argue?

## 9.4 Time

- Where did time go?
- Did I over-invest in one detail?
- Did I reach deep dives?
- Did I leave time for failures and trade-offs?
- Did I provide a final summary?

## 9.5 Outcome

- What was strong?
- What was weak?
- What was missing?
- What should change next time?

---

# 10. Standard 1–5 Self-Scoring System

Use the same scale repeatedly.

| Score | Meaning | Observable evidence |
|---:|---|---|
| 1 | Poor / major gap | Cannot perform the capability independently |
| 2 | Weak | Partial understanding; frequent errors |
| 3 | Acceptable | Handles common cases but has gaps |
| 4 | Strong | Consistent and defensible |
| 5 | Excellent | Clear, deep, adaptable, and robust under pushback |

### Do not score based on feelings

Bad:

> "That felt like a 5."

Better:

> "I gave myself 4 because I clarified requirements, estimated scale, covered reliability and cost, and handled two follow-ups without losing structure."

---

# 11. Master Scorecard

Use this after system-design/full-loop mocks.

| Category | Score 1–5 | Evidence | Next action |
|---|---:|---|---|
| Requirements | | | |
| Estimation | | | |
| Architecture | | | |
| Data modelling | | | |
| Trade-offs | | | |
| Failure handling | | | |
| Reliability | | | |
| Data quality | | | |
| Security | | | |
| Cost | | | |
| Observability | | | |
| Technical depth | | | |
| Coding | | | |
| Debugging | | | |
| Behavioural | | | |
| Leadership | | | |
| Communication | | | |
| Time management | | | |
| Interview presence | | | |

### Evidence rule

Every score below 4 should have:

```text
Observed problem
→ Root cause
→ Corrective action
→ Re-attempt date
```

---

# 12. Senior vs Staff Scoring

## Senior-level evidence

A strong Senior candidate should consistently demonstrate:

- technically correct designs
- structured requirements clarification
- credible estimation
- practical trade-offs
- reliable implementation
- effective debugging
- production awareness
- ownership
- clear communication
- strong follow-up handling

## Staff-level evidence

Staff-level performance additionally demonstrates:

- ambiguity reduction
- architecture leverage
- organizational impact
- cross-team influence
- systemic risk identification
- long-term trade-offs
- simplification
- prioritization
- technical strategy
- cost/reliability balance
- ability to challenge an initial direction constructively

### Comparison

| Capability | Senior | Staff |
|---|---|---|
| Requirements | Clarifies | Reframes ambiguity |
| Architecture | Designs system | Shapes durable direction |
| Trade-offs | Explains | Connects to strategy |
| Reliability | Handles failure | Reduces systemic failure modes |
| Cost | Estimates | Optimizes unit economics/organizational cost |
| Influence | Collaborates | Aligns teams/stakeholders |
| Scope | Owns solution | Owns problem boundary |
| Technical depth | Strong | Strong + broad/systemic |
| Communication | Clear | Aligning and persuasive |
| Leadership | Delivers | Creates leverage |

These are **practice/readiness guidelines**, not universal hiring rules.

---

# 13. System Design Mock Program

Use the nine G5 design cases.

| Case | Difficulty | Core pressure |
|---|---|---|
| 07 Batch analytics | Intermediate | Data lifecycle + cost |
| 08 Clickstream | Advanced | Streaming + freshness |
| 09 CDC lakehouse | Advanced | Ordering + correctness |
| 10 ML features | Advanced | Point-in-time correctness |
| 11 Logs/metrics | Advanced | High volume + serving |
| 12 Attribution | Advanced | Dedup + restatement |
| 13 IoT telemetry | Advanced | Fan-in + skew |
| 14 GDPR deletion | Advanced | Deletion guarantees |
| 15 RAG/vector | Advanced | Retrieval + permissions |

The case library is the core breadth component of G5; Topic 19 should force the learner to solve these without memorizing a fixed architecture. fileciteturn186file4

---

# 14. Case Mock Template

Use this template for every design mock.

```text
Case:
Date:
Difficulty:
Time limit:
Interviewer:
Recording:

Requirements:
Estimated scale:
High-level architecture:
Data model:
Storage:
Processing:
Serving:
Cross-cutting concerns:
Failure scenarios:
Trade-offs:
Follow-ups:

Score:
Strongest area:
Weakest area:
Top 3 corrections:
Re-attempt date:
```

### Rule

Do not memorize:

> "Case 12 always uses Kafka + Spark + warehouse."

Instead memorize the **reasoning framework**:

```text
Requirements
→ Estimates
→ Data flow
→ Storage
→ Processing
→ Serving
→ Cross-cutting concerns
→ Failure handling
→ Evolution
```

---

# 15. 45-Minute System Design Mock

A realistic baseline:

```text
0–5 min
Requirements + clarification

5–10 min
Scale estimation

10–20 min
High-level architecture

20–30 min
Deep dive

30–35 min
Trade-offs

35–40 min
Failures + reliability

40–45 min
Follow-ups + summary
```

This is a practical variation of the G5 design-round timing taught earlier.

### 0–5: Clarify

Ask:

- Who are the users?
- What are the sources?
- What is the expected volume?
- What freshness is required?
- What correctness is required?
- What are retention/privacy requirements?

### 5–10: Estimate

Calculate:

- events/sec
- peak events/sec
- bytes/event
- storage/day
- retention
- throughput
- rough compute
- cost implications

### 10–20: Design

Draw:

```text
Sources
  ↓
Ingestion
  ↓
Raw
  ↓
Processing
  ↓
Curated
  ↓
Serving
  ↓
Consumers
```

### 20–30: Deep dive

Choose the highest-risk component.

### 30–35: Trade-offs

Explain alternatives.

### 35–40: Failures

Use:

```text
Detect
→ Isolate
→ Contain
→ Recover
→ Validate
→ Prevent
```

### 40–45: Follow-ups

Answer directly and adapt the design.

---

# 16. Advanced 60-Minute Senior/Staff Mock

Use when practicing difficult interviews.

```text
0–7     Requirements
7–14    Estimates
14–25   Architecture
25–38   Deep dive
38–45   Reliability/security/data quality
45–52   Cost + trade-offs
52–57   Pushback/follow-ups
57–60   Summary
```

### Advanced pressure

Introduce:

- contradictory requirements
- multiple consumers
- changing scale
- cost constraint
- stricter SLA
- regional failure
- security/privacy requirement
- organizational constraint

The candidate should adapt without abandoning structure.

---

# 17. System Design Mock — Case 07: Batch Analytics Platform

### Prompt

> Design a platform that ingests daily business data and provides reliable analytical datasets for BI users.

### Interviewer expects

- source identification
- volume/freshness
- object storage/lake/warehouse reasoning
- batch processing
- data quality
- orchestration
- backfills
- cost
- security

### Pushbacks

1. The daily file arrives twice.
2. A partition is late.
3. A transformation bug affected seven days.
4. Analysts need a backfill.
5. Volume becomes 20× larger.

### Common mistakes

- no grain
- no backfill strategy
- no idempotency
- no quality gate
- adding streaming without a requirement

### Self-review

Ask:

> Did I design for correction, not only the happy path?

---

# 18. System Design Mock — Case 08: Real-Time Clickstream

### Prompt

> Design a clickstream platform that supports near-real-time dashboards and historical analytics.

### Pressure points

- event volume
- partitioning
- consumer lag
- event time
- duplicates
- late events
- retention
- hot keys
- replay

### Follow-ups

- What if consumers fall behind?
- What if one customer produces 1,000× more events?
- What if the stream is unavailable?
- How do you replay?
- Why streaming instead of micro-batch?

### Strong signal

You distinguish:

```text
transport durability
≠
processing correctness
≠
serving freshness
```

---

# 19. System Design Mock — Case 09: CDC Replication

### Prompt

> Replicate operational database changes into a lakehouse for analytics.

### Must discuss

- snapshot + incremental boundary
- insert/update/delete
- source positions
- ordering
- deduplication
- replay
- schema evolution
- auditability

### Pushback

> "The target has missing updates."

Strong reasoning:

```text
Detect gap
→ identify source position
→ compare source/target
→ replay affected range
→ reconcile
→ prevent recurrence
```

---

# 20. System Design Mock — Case 10: ML Feature Platform

### Pressure points

- offline/online consistency
- point-in-time correctness
- training/serving skew
- feature freshness
- backfills
- lineage
- feature ownership
- monitoring

### Follow-up

> "A model's offline metrics are excellent but online performance collapses."

Investigate:

- training-serving skew
- feature freshness
- leakage
- point-in-time joins
- distribution shift

---

# 21. System Design Mock — Case 11: Logs and Metrics

### Pressure points

- ingestion volume
- high-cardinality dimensions
- retention
- query latency
- hot partitions
- downsampling
- cost

### Follow-up

> "Storage cost doubled without a corresponding traffic increase."

Reason through:

```text
volume
→ cardinality
→ retention
→ replication
→ compression
→ indexing
→ query/storage policy
```

---

# 22. System Design Mock — Case 12: Ad Attribution

### Pressure points

- event identity
- deduplication
- attribution windows
- late events
- restatement
- billing correctness
- reconciliation
- fraud
- privacy

### Follow-up

> "Finance says yesterday's attribution changed."

Do not immediately declare a bug.

First ask:

- Were late events received?
- Was the window still open?
- Was a model/rule changed?
- Was duplicate filtering corrected?
- Was fraud filtering updated?
- Was a source restated?

---

# 23. System Design Mock — Case 13: IoT Telemetry

### Pressure points

- massive fan-in
- device identity
- reconnect storms
- unreliable networks
- clock skew
- out-of-order events
- partition hotspots
- edge buffering

### Follow-up

> "10% of devices reconnect at the same time."

Discuss:

- burst capacity
- admission control
- partition distribution
- backpressure
- durable buffering
- recovery

---

# 24. System Design Mock — Case 14: GDPR Deletion

### Pressure points

- identity mapping
- raw data
- curated data
- derived tables
- feature stores
- vector indexes
- caches
- backups
- deletion evidence

### Follow-up

> "The primary table is deleted, but a vector index still contains personal information."

A strong answer traces the entire data lineage rather than treating the primary database as the whole system.

---

# 25. System Design Mock — Case 15: RAG/Vector Platform

### Pressure points

- document identity
- versions
- chunking
- embeddings
- ANN index
- metadata
- ACLs
- hybrid retrieval
- reranking
- deletion
- freshness
- evaluation

### Follow-up

> "A user retrieves a document they are not authorized to see."

Strong reasoning:

```text
Contain
→ disable unsafe retrieval path
→ identify ACL enforcement failure
→ invalidate affected index/cache
→ repair authorization filtering
→ audit exposure
→ add regression tests
```

---

# 26. Failure/Deep-Dive Mock Program

Topic 16 should become a pressure-testing layer.

Use:

```text
Normal design
      ↓
Interviewer injects failure
      ↓
Candidate detects
      ↓
Candidate diagnoses
      ↓
Candidate contains
      ↓
Candidate recovers
      ↓
Candidate validates correctness
      ↓
Candidate prevents recurrence
```

---

# 27. Failure Mock 1 — Kafka Consumer Lag

### Prompt

> Consumer lag has increased continuously for two hours.

### Expected reasoning

Ask:

- Is lag on all partitions?
- Is input traffic higher?
- Is processing slower?
- Is one partition hot?
- Is downstream blocked?
- Are retries increasing?
- Is consumer capacity saturated?

### Strong response

Do not immediately say:

> "Add more consumers."

Explain why additional consumers may or may not help.

---

# 28. Failure Mock 2 — CDC Missing Updates

### Prompt

> Analytics shows stale customer records.

Investigate:

- source position
- CDC gaps
- consumer offsets
- ordering
- dedupe
- schema changes
- target merge
- checkpoint semantics

### Strong signal

Separate:

```text
capture correctness
→ transport correctness
→ application correctness
→ target correctness
```

---

# 29. Failure Mock 3 — Duplicate Batch Output

### Prompt

> Yesterday's partition contains exactly 2× the expected records.

Investigate:

- rerun
- duplicate input
- join multiplication
- non-idempotent write
- partial commit
- bad checkpoint

Do not immediately delete half the rows.

---

# 30. Failure Mock 4 — Spark 10× Slowdown

### Prompt

> A job that normally completes in 20 minutes now takes 200 minutes.

Investigate:

- input volume
- partition distribution
- skew
- shuffle
- plan change
- data statistics
- join strategy
- executor failures
- spill
- file count

### Strong answer

Use evidence from the execution plan and metrics rather than guessing.

---

# 31. Failure Mock 5 — RAG Authorization Leak

### Prompt

> A user retrieved a document from another department.

Expected sequence:

```text
Contain exposure
→ identify authorization boundary
→ inspect retrieval/index metadata
→ repair filtering
→ invalidate affected results
→ audit access
→ add regression tests
→ verify deletion/reindex behavior
```

---

# 32. Failure Mock 6 — GDPR Deletion Gap

### Prompt

> A deletion request completed in the primary table but not in derived data.

Trace:

```text
source
→ raw
→ curated
→ aggregates
→ feature data
→ vector index
→ cache
→ backup
```

The interview is testing whether you understand **data lineage as an operational dependency graph**.

---

# 33. Failure Mock 7 — IoT Reconnect Storm

### Prompt

> A regional outage causes millions of devices to reconnect.

Discuss:

- connection throttling
- durable queues
- admission control
- partitioning
- edge buffering
- backpressure
- recovery ordering
- duplicate telemetry

---

# 34. Failure Mock 8 — Attribution Restatement

### Prompt

> Billing attribution changes after finance has already reviewed the report.

Discuss:

- attribution window
- late events
- correction policy
- versioning
- reconciliation
- restatement
- downstream notification
- auditability

---

# 35. Behavioural Mock Program

Use Topic 17's story bank.

Practice:

- ownership
- failure
- conflict
- leadership
- influence
- ambiguity
- stakeholder management
- mentoring
- technical judgment
- cost optimization
- production incidents
- migration
- project failure

### Answer durations

| Mode | Target |
|---|---:|
| Direct answer | 30 sec |
| Compact STAR | 60–90 sec |
| Full STAR | 2–3 min |
| Follow-up | 15–45 sec |

Do not force every answer into exactly the same length.

---

# 36. Behavioural Mock — Ownership

### Prompt

> Tell me about a data project where you personally owned a difficult outcome.

### Review

Did you establish:

- situation
- responsibility
- constraints
- decision
- actions
- measurable result
- learning

### Weak answer

> "We built a pipeline and it worked."

### Stronger answer

Shows:

```text
Problem
→ personal responsibility
→ decision
→ trade-off
→ measurable result
→ lesson
```

---

# 37. Behavioural Mock — Failure

### Prompt

> Tell me about a production incident you were responsible for.

Follow-ups:

- What did you miss?
- Why did the system allow it?
- What did you do first?
- How did you communicate?
- What changed afterward?
- What would you do differently?

The goal is not to appear flawless.

The goal is to demonstrate:

- ownership
- diagnosis
- judgment
- learning
- prevention

---

# 38. Behavioural Mock — Conflict

### Prompt

> Tell me about a disagreement with another engineer over architecture.

Follow-ups:

- What did they believe?
- What did you believe?
- What evidence did you use?
- Did you change your mind?
- What happened?

Avoid turning the story into:

> "I was right and they were wrong."

---

# 39. Behavioural Mock — Influence

### Prompt

> Tell me about a technical decision you influenced without direct authority.

Look for:

- stakeholder mapping
- evidence
- communication
- alternatives
- compromise
- outcome

Staff-level answers should demonstrate leverage beyond a single task.

---

# 40. Coding Mock Program

Integrate Topic 18.

## Python

Practice:

- transformations
- deduplication
- parsing
- validation
- incremental logic

## SQL

Practice:

- windows
- joins
- aggregation
- reconciliation
- incremental merge

## PySpark

Practice:

- distributed transformations
- deduplication
- partitioning
- skew
- execution plans

## Live pipeline

Practice:

```text
clarify
→ inspect
→ implement
→ test
→ debug
→ productionize
```

---

# 41. Coding Mock Template

```text
Problem:
Time:
Language:
Input:
Output:
Clarifying questions:
Approach:
Implementation:
Tests:
Edge cases:
Complexity:
Production follow-ups:
Score:
```

### Coding scoring

| Category | 1 | 3 | 5 |
|---|---|---|---|
| Requirements | Missed | Basic | Precise |
| Correctness | Broken | Happy path | Robust |
| Data reasoning | Weak | Adequate | Strong |
| Code quality | Poor | Readable | Clean/testable |
| Testing | None | Basic | Purposeful |
| Edge cases | Missed | Some | Prioritized |
| Complexity | Unknown | Basic | Explicit |
| Debugging | Random | Structured | Evidence-driven |
| Communication | Silent | Adequate | Clear |
| Productionization | None | Mentions | Prioritizes |

---

# 42. Full Interview Loop

A realistic full loop can look like:

```text
Round 1
SQL / Python
        ↓
Round 2
Data Engineering System Design
        ↓
Round 3
Behavioural
        ↓
Round 4
Failure / Deep Dive
        ↓
Round 5
Live Pipeline Coding
        ↓
Round 6
Hiring Manager / Staff-level
```

The exact loop varies by company.

The purpose of simulation is to practice **switching cognitive modes**.

---

# 43. Full Loop Mock 1 — Senior Data Engineer

### Schedule

| Round | Time |
|---|---:|
| SQL/Python | 45 min |
| System design | 60 min |
| Behavioural | 45 min |
| Failure | 45 min |
| Live coding | 45 min |

### Focus

- correctness
- practical architecture
- production judgment
- ownership

### Pass evidence

Consistent ≥4 performance in core areas with no major correctness failure.

---

# 44. Full Loop Mock 2 — Streaming/Distributed Senior

### Round 1

SQL + event processing.

### Round 2

Real-time clickstream.

### Round 3

Kafka/Spark failure deep dive.

### Round 4

Behavioural production incident.

### Round 5

Streaming aggregation coding.

### Round 6

Scale/cost discussion.

---

# 45. Full Loop Mock 3 — Cloud/Lakehouse Senior

### Round 1

SQL.

### Round 2

Lakehouse architecture.

### Round 3

CDC failure.

### Round 4

Migration story.

### Round 5

Pipeline implementation.

### Round 6

Cloud cost/security.

---

# 46. Full Loop Mock 4 — Senior/Staff

### Pressure

- ambiguous requirements
- multiple stakeholders
- cost constraint
- 10× scale
- reliability requirement
- organizational constraints

### Evaluation

Not merely:

> "Can you design it?"

But:

> "Can you decide what should be designed?"

---

# 47. Full Loop Mock 5 — Staff

### Round themes

1. Strategy and architecture
2. Complex system design
3. Failure and organizational risk
4. Behavioural/influence
5. Coding/deep technical review
6. Hiring-manager discussion

### Staff signal

The candidate connects:

```text
technical decision
→ operational impact
→ team impact
→ organizational impact
→ long-term architecture
```

---

# 48. Final Interview Readiness Simulation

Complete without notes.

### Round 1 — SQL/Python

45 minutes.

### Round 2 — System design

60 minutes.

### Round 3 — Failure/deep dive

45 minutes.

### Round 4 — Behavioural

45 minutes.

### Round 5 — Live pipeline coding

45 minutes.

### Round 6 — Staff/hiring manager

45–60 minutes.

### Recovery rule

Do not redo an entire round because one answer was weak.

Continue.

Real interviews contain imperfect moments.

The skill being tested is **recovery and consistency**, not perfection.

---

# 49. Four-Week Mock Plan

The roadmap recommends approximately 4 weeks at 8–10 hours/week, then ongoing mocks. fileciteturn186file3

## Week 1 — Foundation and calibration

**8–10 hours**

- Topic 01 rubric review
- 2 × 30-minute design drills
- 2 coding drills
- 1 behavioural session
- 1 recorded failure drill
- establish baseline score
- create error log

### Goal

Discover weaknesses rather than chase high scores.

---

## Week 2 — Breadth

**8–10 hours**

- 2 system-design mocks
- 1 failure mock
- 1 behavioural mock
- 2 coding sessions
- 1 self-review session

Cases:

- batch
- streaming
- CDC
- feature platform

### Goal

Improve breadth and timing.

---

## Week 3 — Depth

**8–10 hours**

- 2 advanced system-design mocks
- 2 failure/deep-dive mocks
- 1 behavioural mock
- 2 coding sessions
- peer interviewer session

Cases:

- logs/metrics
- attribution
- IoT
- GDPR
- RAG

### Goal

Improve follow-up resilience.

---

## Week 4 — Full loops

**8–10 hours**

- 2 full-loop simulations
- 1 follow-up-only mock
- 1 behavioural mock
- 1 live coding mock
- final readiness review

### Goal

Demonstrate consistency.

---

# 50. Extended 6–8 Week Plan

Use this when preparing for a difficult Senior/Staff process.

## Weeks 1–2

Baseline + fundamentals.

## Weeks 3–4

Design breadth + failure.

## Weeks 5–6

Senior/Staff deep dives + full loops.

## Weeks 7–8

Company-specific preparation + final simulations.

### Weekly cadence

```text
2 design mocks
1 failure mock
1 behavioural mock
1 coding mock
1 peer interview
1 self-review session
```

Reduce volume when performance quality deteriorates.

---

# 51. Daily Practice Plans

## 30 minutes

```text
5 min  Review one weak concept
15 min Timed drill
5 min  Self-score
5 min  Error-log action
```

## 60 minutes

```text
10 min Review
35 min Timed mock
10 min Score
5 min Corrective action
```

## 90 minutes

```text
10 min Warm-up
45 min Mock
15 min Review
10 min Reference comparison
10 min Error log
```

## 2–3 hours

```text
45–60 min Full mock
20 min Review
30 min Targeted weak-area drill
20 min Re-attempt
15 min Error log
```

---

# 52. Weekly Practice Plan

A balanced week:

| Day | Practice |
|---|---|
| Monday | System design |
| Tuesday | SQL/Python |
| Wednesday | Failure/deep dive |
| Thursday | Behavioural |
| Friday | Rest/light review |
| Saturday | Full mock |
| Sunday | Self-review + weak-area correction |

The exact schedule should adapt to work and interview timing.

---

# 53. Difficulty Levels

## Level 1 — Foundation

- clear requirements
- moderate scale
- limited follow-ups

## Level 2 — Intermediate

- some ambiguity
- meaningful trade-offs
- basic failures

## Level 3 — Senior

- multiple constraints
- deep dives
- production concerns

## Level 4 — Senior+

- failure pressure
- cost constraints
- changing requirements
- adversarial follow-ups

## Level 5 — Staff

- ambiguous scope
- multiple stakeholders
- organizational constraints
- strategic trade-offs
- 10× scale
- reliability/cost tension
- long-term architecture

### Progression rule

Do not jump permanently to Level 5.

Build enough Level 2/3 consistency that advanced pressure exposes weaknesses rather than overwhelming fundamentals.

---

# 54. Interviewer Pushback System

Practice responses to:

> "Why Kafka?"

> "Why not batch?"

> "What happens if Kafka is unavailable?"

> "What happens at 10× scale?"

> "Your approach costs too much."

> "Your architecture violates the freshness SLA."

> "The source schema changes."

> "We cannot afford another storage system."

> "The business requires deletion within 30 days."

> "Your system produces duplicates."

> "Your RAG retrieval violates permissions."

## Response framework

```text
1. Acknowledge
2. Clarify the new constraint
3. Re-evaluate the assumption
4. Explain the trade-off
5. Adapt the design
6. State the impact
```

### Example

Interviewer:

> "Kafka is too expensive."

Candidate:

> "Under that constraint, I'd revisit whether continuous streaming is actually required. If the freshness target is relaxed from seconds to five minutes, micro-batching may provide the required SLA at lower operational complexity and cost."

That is stronger than defending Kafka automatically.

---

# 55. Mock Interview Error Log

Keep the log inside your practice system.

| Date | Interview | Category | Mistake | Root Cause | Correct Approach | Re-attempt | Result |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

### Categories

- knowledge
- reasoning
- communication
- estimation
- architecture
- trade-off
- failure
- coding
- SQL
- Python
- PySpark
- behavioural
- time management
- pressure
- leadership

### Error-log rule

> **Do not record only what went wrong. Record why it went wrong and what will change.**

---

# 56. Mistake Taxonomy

## Knowledge gap

> "I did not know the concept."

**Action:** study and explain from first principles.

## Reasoning gap

> "I knew the concept but applied it incorrectly."

**Action:** solve adjacent scenarios.

## Communication gap

> "I knew the answer but could not explain it."

**Action:** practice concise spoken explanations.

## Execution gap

> "I could explain it but could not implement it."

**Action:** coding drills.

## Time-management gap

> "I knew the material but ran out of time."

**Action:** stricter section timers.

## Pressure gap

> "I can solve this alone but freeze during follow-ups."

**Action:** partner mocks with pushback.

## Integration gap

> "I know each topic independently but cannot combine them."

**Action:** full-loop simulations.

---

# 57. Gap Analysis

Distinguish five major gap types.

| Gap | Symptom | Corrective action |
|---|---|---|
| Knowledge | Cannot answer concept | Study |
| Practice | Slow/inconsistent | Repetition |
| Communication | Correct but unclear | Record + explain |
| Pressure | Good alone, weak live | Mock |
| Integration | Individual topics strong, full loop weak | Full-loop practice |

This prevents a common mistake:

> Studying more when the real problem is execution.

---

# 58. Re-Attempt Strategy

Do not immediately repeat the same question after seeing the answer.

Use:

```text
Attempt 1
↓
Review
↓
Study
↓
Attempt 2 — 2 days later
↓
Attempt 3 — 1 week later
↓
Attempt 4 — under mock conditions
```

### Why spacing helps

Immediate repetition can create:

> recognition ≠ retrieval

The delayed attempt tests whether the reasoning is actually available without the reference.

### Re-attempt rule

On the second attempt, do not merely reproduce the previous architecture.

Ask:

> "What did I miss last time?"

---

# 59. Progress Tracking

Track each mock:

| Mock | Date | Design | Estimation | Failure | Coding | Behavioural | Communication | Overall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |

Track:

- average score
- weakest category
- strongest category
- trend
- recurring errors
- number of re-attempts
- successful follow-ups
- full-loop performance

---

# 60. Python Example — Score Aggregation

```python
scores = {
    "system_design": 4,
    "estimation": 3,
    "tradeoffs": 4,
    "failure_handling": 2,
    "coding": 4,
    "behavioral": 3,
}

overall = sum(scores.values()) / len(scores)

print(f"Overall score: {overall:.2f}")
```

### What this does

- `scores.values()` gets the numerical scores.
- `sum(...)` adds them.
- `len(scores)` counts categories.
- The result is a simple average.

This is a practice aid, not a hiring algorithm.

---

# 61. Python Example — Weak-Area Detection

```python
threshold = 3

weak_areas = {
    category: score
    for category, score in scores.items()
    if score < threshold
}

for category, score in weak_areas.items():
    print(f"{category}: {score}/5")
```

Example output:

```text
failure_handling: 2/5
```

### Corrective action

A weak category should produce a concrete next action.

```text
failure_handling = 2
        ↓
5 failure drills
        ↓
2 timed failure mocks
        ↓
record
        ↓
re-score
```

---

# 62. Python Example — Progress Tracking

```python
history = {
    "mock_1": {
        "system_design": 3,
        "failure": 2,
        "coding": 3,
    },
    "mock_2": {
        "system_design": 4,
        "failure": 3,
        "coding": 4,
    },
    "mock_3": {
        "system_design": 4,
        "failure": 4,
        "coding": 4,
    },
}

for mock, categories in history.items():
    average = sum(categories.values()) / len(categories)
    print(f"{mock}: {average:.2f}")
```

Use this to identify trends, not to manufacture confidence.

---

# 63. Python Example — Random Case Selection

```python
import random

cases = [
    "Batch Analytics",
    "Clickstream",
    "CDC",
    "ML Feature Platform",
    "Logs and Metrics",
    "Ad Attribution",
    "IoT Telemetry",
    "GDPR Deletion",
    "RAG and Vector Platform",
]

selected_case = random.choice(cases)

print(f"Today's system-design case: {selected_case}")
```

Randomization reduces memorization of case-specific answer sequences.

---

# 64. Python Example — Readiness Report

```python
scores = {
    "system_design": 4,
    "estimation": 4,
    "failure_handling": 3,
    "coding": 4,
    "behavioral": 4,
    "communication": 4,
}

average = sum(scores.values()) / len(scores)
weak = [name for name, score in scores.items() if score < 4]

print(f"Average: {average:.2f}/5")

if weak:
    print("Focus areas:")
    for name in weak:
        print(f"- {name}")
else:
    print("No category is currently below 4.")
```

A useful readiness report should show **evidence and weaknesses**, not merely say "ready."

---

# 65. Readiness Thresholds

These are practical self-assessment guidelines, **not universal hiring rules**.

### Not ready

- multiple core categories below 3
- frequent major correctness errors
- cannot complete within time
- cannot handle follow-ups

### Developing

- most categories around 3
- understands concepts
- performance is inconsistent

### Interview ready

- core categories consistently ≥4
- no major recurring correctness failures
- can complete timed mocks
- can handle follow-ups

### Strong Senior

- core categories consistently ≥4
- strong failure handling
- strong implementation
- strong communication
- consistent behavioural evidence

### Staff-oriented readiness

In addition to Senior-level consistency:

- ambiguity handling
- organizational reasoning
- strategic trade-offs
- influence
- simplification
- systemic risk identification

---

# 66. System Design Self-Review Rubric

Score 1–5.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Requirements | Missed | Basic | Precise |
| Estimates | Missing | Reasonable | Fast + defensible |
| Architecture | Fragmented | Works | Clear + extensible |
| Data model | Weak | Adequate | Explicit grain/contracts |
| Storage | Arbitrary | Reasonable | Requirement-driven |
| Processing | Arbitrary | Appropriate | Well-justified |
| Reliability | Missing | Basic | Failure-aware |
| Data quality | Missing | Some checks | Explicit invariants |
| Security | Missing | Mentioned | Integrated |
| Cost | Missing | Mentioned | Quantified trade-offs |
| Observability | Missing | Basic | Operationally useful |
| Trade-offs | Weak | Some | Explicit and balanced |
| Failure handling | Weak | Basic | Structured |
| Communication | Confusing | Clear | Highly structured |
| Diagram | Poor | Understandable | Simple + precise |
| Time | Poor | Finished | Well-paced |

---

# 67. Behavioural Self-Review Rubric

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Relevance | Off-topic | Related | Direct |
| Context | Vague | Adequate | Clear |
| Ownership | "We" only | Mixed | Explicit ownership |
| Technical depth | Shallow | Adequate | Specific |
| Decision | Missing | Present | Well-reasoned |
| Trade-off | Missing | Mentioned | Explicit |
| Collaboration | Weak | Adequate | Strong |
| Conflict | Avoided | Described | Constructively resolved |
| Metrics | None | Some | Quantified |
| Result | Vague | Clear | Measurable |
| Learning | Generic | Present | Specific |
| Reflection | None | Basic | Deep |
| Communication | Rambling | Clear | Concise |
| Follow-ups | Weak | Adequate | Resilient |

---

# 68. Coding Self-Review Rubric

Score:

- requirements clarification
- correctness
- data reasoning
- code quality
- testing
- edge cases
- complexity
- debugging
- communication
- productionization
- time management

### Critical rule

A coding solution that passes the happy path but cannot explain:

> "What happens if this runs twice?"

has a reliability gap.

---

# 69. Failure-Scenario Self-Review Rubric

Score:

- detection
- diagnosis
- blast radius
- containment
- recovery
- correctness validation
- prevention
- observability
- trade-offs
- communication

### Strong failure response

```text
What happened?
      ↓
How do I know?
      ↓
What is affected?
      ↓
How do I contain it?
      ↓
How do I recover?
      ↓
How do I validate correctness?
      ↓
How do I prevent recurrence?
```

---

# 70. Recording Review

Review recordings for patterns.

## Verbal

Look for:

- filler words
- excessive speed
- excessive pauses
- unclear sentences
- repetition

## Structure

Ask:

- Did the answer have a beginning, middle, and end?
- Were assumptions explicit?
- Were decisions clear?
- Did the conclusion follow the reasoning?

## Technical

Ask:

- Was the reasoning correct?
- Did I justify decisions?
- Did I handle constraints?

## Behavioural

Ask:

- Did I show ownership?
- Did I quantify impact?
- Did I explain learning?

## Presence

Look for:

- composure
- responsiveness
- confidence without defensiveness

### Important boundary

Recording review should identify recurring patterns, not become compulsive analysis of every word.

---

# 71. Mock Interview Observer Sheet

Use this when interviewing a peer.

```text
Candidate:
Date:
Interviewer:
Interview type:
Prompt:
Difficulty:

Strengths:
1.
2.
3.

Weaknesses:
1.
2.
3.

Follow-ups attempted:
1.
2.
3.

Technical score:
Communication score:
Time-management score:
Overall score:

Evidence:
-

Top 3 improvement actions:
1.
2.
3.

Recommended re-attempt date:
```

---

# 72. Peer Mock Interviews

The roadmap explicitly expects the learner to become a mock interviewer as well as a candidate. fileciteturn186file5

## Interviewer responsibilities

- select an appropriate prompt
- state the time limit
- avoid rescuing too early
- ask realistic follow-ups
- track time
- record evidence
- avoid unnecessary hints
- score independently

## Candidate responsibilities

- clarify
- reason aloud
- respond to the prompt
- adapt to new information
- manage time
- summarize

## Reviewer responsibilities

- score based on evidence
- identify top three improvements
- separate technical from communication issues
- avoid vague feedback

### Peer-interview learning effect

Interviewing someone else teaches you to notice:

- missing requirements
- weak trade-offs
- unclear diagrams
- shallow failure reasoning
- communication problems

This makes you a better candidate.

---

# 73. Solo Mock Interviews

Solo practice is useful when a partner is unavailable.

Use:

- timer
- prompt card
- voice recording
- whiteboard
- written follow-ups
- delayed answer checking

### Solo design

```text
Read prompt
→ Start timer
→ Speak aloud
→ Draw
→ Record
→ Stop
→ Score
→ Write errors
→ Compare later
```

### Limitation

Solo practice cannot fully reproduce interviewer interaction.

Therefore use it for volume, then use peer/mentor mocks for realism.

---

# 74. Mock Interview Scheduling

Do not practice only comfortable topics.

Use a rotation:

```text
System Design
↓
Coding
↓
Behavioural
↓
Failure
↓
System Design
↓
Coding
↓
Full Mock
```

The roadmap specifically recommends ongoing case re-runs, error-log review, and company-specific preparation. fileciteturn186file3

---

# 75. Case Rotation

## Week 1

- Batch
- Streaming

## Week 2

- CDC
- ML Feature Platform

## Week 3

- Logs/Metrics
- Attribution
- IoT

## Week 4

- GDPR
- RAG

## After Week 4

Random mixed cases.

### Why randomize?

Because memorization can produce:

> "I know this case."

Interview readiness requires:

> "I can reason through an unfamiliar problem."

---

# 76. Randomization Strategy

Randomize:

- case
- failure
- interviewer follow-up
- behavioural theme
- coding task
- scale
- freshness requirement
- cost constraint

### Example

A CDC case can randomly add:

```text
10× volume
+
strict deletion requirement
+
source outage
```

This forces adaptation rather than memorization.

---

# 77. Interview Pressure Simulation

Introduce controlled pressure:

### Requirement change

> "Freshness must now be under 30 seconds."

### Cost pressure

> "The proposed design exceeds budget."

### Failure

> "The primary region is unavailable."

### Scale

> "Traffic increases 10×."

### Security

> "Some users cannot access all data."

### Stakeholder conflict

> "Analytics wants historical correctness; operations wants lowest latency."

### Candidate response

Never panic and redraw everything immediately.

Use:

```text
New constraint
→ Identify affected assumptions
→ Identify affected components
→ Explain trade-off
→ Change only what must change
→ Recalculate impact
```

---

# 78. Five Complete Full-Loop Simulations

The following five loops provide the required final practice set.

## Loop 1 — Senior Data Engineer

**Round 1:** SQL/Python  
**Round 2:** Batch system design  
**Round 3:** Behavioural  
**Round 4:** Failure scenario  
**Round 5:** Live pipeline coding

### Core competencies

- practical correctness
- production awareness
- ownership
- communication

---

## Loop 2 — Streaming Senior

**Round 1:** SQL/event data  
**Round 2:** Clickstream system design  
**Round 3:** Kafka/Spark failure  
**Round 4:** Production incident behavioural  
**Round 5:** Streaming aggregation coding

### Core competencies

- event time
- partitioning
- state
- reliability
- scale

---

## Loop 3 — Cloud/Lakehouse Senior

**Round 1:** SQL  
**Round 2:** Lakehouse architecture  
**Round 3:** CDC failure  
**Round 4:** Migration behavioural  
**Round 5:** Pipeline implementation

### Core competencies

- platform architecture
- governance
- migration
- reliability
- cost

---

## Loop 4 — Senior/Staff

**Round 1:** Complex system design  
**Round 2:** Deep failure analysis  
**Round 3:** Behavioural/influence  
**Round 4:** Coding/deep technical review  
**Round 5:** Architecture strategy

### Core competencies

- ambiguity
- technical leadership
- influence
- architecture leverage

---

## Loop 5 — Staff

**Round 1:** Strategy/system design  
**Round 2:** Complex distributed system  
**Round 3:** Failure + organizational risk  
**Round 4:** Leadership/behavioural  
**Round 5:** Technical implementation review  
**Round 6:** Hiring manager

### Core competencies

- strategic reasoning
- organizational impact
- cost/reliability
- long-term architecture
- technical leadership

---

# 79. Final Readiness Report

Complete this after a full-loop simulation.

```text
Overall Score:

System Design:
Estimation:
Trade-offs:
Failure Handling:
Coding:
SQL:
Python:
PySpark:
Behavioural:
Communication:
Leadership:
Time Management:
Staff-Level Reasoning:

Strongest Areas:

Weakest Areas:

Recurring Errors:

Top 3 Risks:
1.
2.
3.

Top 3 Improvement Actions:
1.
2.
3.

Next Mock Date:

Readiness Level:
```

### Evidence requirement

Do not mark:

> "Interview ready"

unless you can point to repeated performance evidence.

---

# 80. Personalized Improvement Plan

Convert a score into an action.

## Failure handling = 2

```text
Review Topic 16
      ↓
5 failure drills
      ↓
2 timed failure mocks
      ↓
Record
      ↓
Re-score
      ↓
Repeat if <4
```

## Estimation = 2

```text
Review Topic 03
      ↓
10 estimation drills
      ↓
5 timed drills
      ↓
2 design mocks
      ↓
Re-score
```

## Communication = 2

```text
Record 5 answers
      ↓
Review structure
      ↓
Practice concise summaries
      ↓
3 peer mocks
      ↓
Re-score
```

## Coding = 2

```text
5 Python/SQL drills
+
2 pipeline mocks
+
2 debugging drills
→ Re-score
```

## Staff reasoning = 2

```text
Practice ambiguity
→ strategic trade-offs
→ organizational constraints
→ influence stories
→ 3 Staff-level mocks
→ peer review
→ re-score
```

---

# 81. Weakness-First Practice

A useful starting heuristic is:

```text
70% weak areas
20% maintenance
10% strengths
```

This is a practical guideline, not a universal rule.

### Change the ratio when

- an interview is within days
- a previously weak category is now stable
- a company has an unusually strong focus on one capability
- fatigue is reducing performance
- you need maintenance rather than remediation

The objective is **balanced readiness**, not permanent weakness fixation.

---

# 82. Sustainable Practice

More practice is not always better.

Watch for:

- declining performance
- repeated mistakes without diagnosis
- inability to concentrate
- practicing only because of anxiety
- excessive repetition without spacing

Use:

```text
High-intensity mock
→ review
→ recovery
→ targeted practice
→ rest
→ next mock
```

Quality matters more than raw mock count.

---

# 83. Final Interview Strategy

## Before the interview

- review the framework
- review estimation numbers
- review trade-offs
- review story themes
- review recent error-log items
- perform light practice
- prepare environment
- confirm allowed tools
- avoid last-minute cramming

## During the interview

```text
Listen
→ Clarify
→ Structure
→ Reason
→ Communicate
→ Adapt
→ Summarize
```

## After the interview

Record:

- questions
- uncertain areas
- follow-ups you struggled with
- timing issues
- technical gaps
- behavioural gaps

Then update the error log.

---

# 84. Common Mock-Practice Mistakes

| Mistake | Correction |
|---|---|
| Only easy questions | Add progressive difficulty |
| Memorizing solutions | Randomize cases |
| Never timing | Always use a timer |
| Never recording | Record key mocks |
| Ignoring follow-ups | Add pushback |
| Ignoring failures | Run failure-only mocks |
| Repeating immediately | Use spaced re-attempts |
| No error log | Record root causes |
| Studying instead of practicing | Increase timed attempts |
| Ignoring communication | Review recordings |
| Overestimating ability | Use peer evidence |
| Underestimating ability | Use objective repeated results |
| Practicing endlessly | Use sustainable cadence |
| Avoiding weak areas | Weakness-first practice |

---

# 85. Mental Models

### Practice loop

> **Attempt → Score → Diagnose → Correct → Re-attempt**

### Readiness

> **Knowledge × Execution × Communication**

A severe weakness can dominate overall performance.

### Senior progression

> **Solve → Explain → Defend → Improve**

### Staff progression

> **Solve → Simplify → Influence → Scale**

### Error-log principle

> **Do not repeat an uncorrected mistake.**

### Mock principle

> **Practice should become progressively less comfortable and more realistic.**

### Readiness principle

> **Confidence should come from evidence, not repetition alone.**

### Failure principle

> **Detect → Diagnose → Contain → Recover → Validate → Prevent**

---

# 86. Final Pre-Interview Cheat Sheet

## 45-minute design

```text
5   requirements
5   estimates
10  architecture
10  deep dive
5   trade-offs
5   failure/follow-up
5   summary
```

## Requirements

- Who?
- What?
- Sources?
- Consumers?
- Volume?
- Freshness?
- Correctness?
- Retention?
- Security?
- Cost?

## Estimation

- events/sec
- peak
- bytes/event
- storage/day
- retention
- throughput
- compute
- cost

## Architecture

```text
Source
→ Ingestion
→ Storage
→ Processing
→ Serving
→ Consumers
```

## Trade-offs

- batch vs streaming
- ETL vs ELT
- warehouse vs lakehouse
- managed vs custom
- latency vs cost
- reliability vs complexity

## Failure

```text
Detect
→ Isolate
→ Contain
→ Recover
→ Validate
→ Prevent
```

## Behavioural

```text
Situation
→ Task
→ Action
→ Result
→ Learning
```

## Coding

```text
Clarify
→ Grain
→ Approach
→ Implement
→ Test
→ Edge cases
→ Complexity
→ Production
```

## Final question

> **What did I deliberately choose not to build, and why?**

---

# 87. Final Assessment

## Section A — Practice Methodology

**Task:** Build a one-week mock schedule.

Must include:

- system design
- failure
- behavioural
- coding
- self-review
- rest/recovery

**Pass:** schedule has deliberate progression and measurable outputs.

---

## Section B — System Design

Complete one 45-minute case without notes.

**Pass:**

- requirements
- estimates
- architecture
- trade-offs
- failures
- summary

---

## Section C — Failure

Complete one 30-minute failure mock.

**Pass:**

- detection
- diagnosis
- containment
- recovery
- validation
- prevention

---

## Section D — Behavioural

Answer:

1. ownership
2. failure
3. conflict
4. influence
5. ambiguity

**Pass:** evidence-based, specific, measurable stories.

---

## Section E — Coding

Complete one 45-minute pipeline problem.

**Pass:**

- correct implementation
- tests
- edge cases
- clear communication
- production follow-ups

---

## Section F — Self-Review

Score the session.

**Pass:** every score has evidence.

---

## Section G — Improvement Plan

Identify the weakest two categories and create a correction plan.

**Pass:** actions are measurable and time-bound.

---

## Section H — Full Loop

Complete one complete simulation from §78.

**Pass:** no major recurring weakness and no catastrophic time-management failure.

---

# 88. Objective Evidence of Readiness

Readiness should be based on:

- repeated successful mocks
- consistent scores
- fewer recurring errors
- successful follow-ups
- successful time management
- coding completion
- strong behavioural stories
- strong system-design performance
- ability to handle unfamiliar problems

### Important

> **One excellent mock does not prove readiness.**

Look for consistency.

A better evidence statement is:

> "Across six design mocks, my architecture score remained 4+, failure handling improved from 2 to 4, and I completed the last three within time."

That is more meaningful than:

> "I feel ready."

---

# 89. Interview-Ready Criteria

These are **practice/readiness guidelines**, not universal hiring standards.

## Senior Data Engineer readiness

The learner should consistently:

- clarify requirements
- estimate scale
- design complete systems
- explain trade-offs
- handle failures
- write correct code
- debug
- communicate clearly
- demonstrate ownership
- complete timed exercises

## Staff Data Engineer readiness

The learner should additionally consistently:

- handle ambiguity
- identify systemic risks
- simplify complex problems
- reason about organizational impact
- influence through technical reasoning
- balance cost and reliability
- discuss long-term architecture
- handle strategic pushback
- demonstrate technical leadership
- create leverage beyond the immediate implementation

---

# 90. Company-Specific Preparation

The roadmap requires company-specific preparation. fileciteturn186file5

Create a one-page company brief.

```text
Company:
Product:
Business model:
Primary data domains:
Likely data scale:
Likely freshness requirements:
Likely compliance:
Likely architecture:
Cloud/platform:
Warehouse/lakehouse:
Streaming:
Orchestration:
Likely interview focus:
Relevant company engineering posts:
Likely system-design cases:
Relevant personal stories:
Likely trade-offs:
Questions to ask interviewer:
```

### Adapt designs, not principles

Do not force a company's stack into every answer.

Instead:

```text
Business requirements
→ likely architecture
→ company context
→ justified technology choices
```

---

# 91. Peer Interviewer Development

Interviewing others is part of the practice system.

A good peer interviewer:

- chooses an appropriate prompt
- maintains realistic time pressure
- asks high-value follow-ups
- does not over-hint
- records evidence
- scores against the rubric
- gives actionable feedback

### Peer interviewer exercise

Complete at least **two peer interviews** using the rubric, matching the roadmap's hands-on requirement. fileciteturn186file5

After each, ask:

> "What did interviewing another person teach me about my own interview performance?"

---

# 92. Required Mock Evidence

The roadmap's Topic 19 hands-on exercise requires at least:

- **six design mocks**
- **three with partners**
- **two follow-up-only mocks**
- **two behavioural mocks**
- recordings and scoring
- an error log
- evidence of at least three recurring mistakes eliminated
- at least two peer interviews
- one company-specific brief. fileciteturn186file5

Use this completion tracker:

| Requirement | Target | Completed | Evidence |
|---|---:|---:|---|
| Design mocks | 6 | | |
| Partner design mocks | 3 | | |
| Follow-up-only mocks | 2 | | |
| Behavioural mocks | 2 | | |
| Recurring mistakes eliminated | 3 | | |
| Peer interviews | 2 | | |
| Company brief | 1 | | |

---

# 93. Final G5 Integration Audit

Because Topic 19 is the final topic, assess whether each capability can be demonstrated **under time pressure**.

| Topic | Capability | Can I demonstrate it under time pressure? | Score | Weakness |
|---|---|---|---:|---|
| 01 | Interview format | | | |
| 02 | Requirements clarification | | | |
| 03 | Estimation | | | |
| 04 | Design framework | | | |
| 05 | Trade-offs | | | |
| 06 | Diagramming | | | |
| 07 | Batch design | | | |
| 08 | Streaming design | | | |
| 09 | CDC design | | | |
| 10 | Feature platform | | | |
| 11 | Logs/metrics | | | |
| 12 | Attribution | | | |
| 13 | IoT | | | |
| 14 | GDPR deletion | | | |
| 15 | RAG/vector platform | | | |
| 16 | Failure/deep dives | | | |
| 17 | Behavioural | | | |
| 18 | Take-home/live coding | | | |
| 19 | Mock/self-review | | | |

### Final integration question

> **Can I demonstrate the capability without relying on memorized case-specific answers?**

If not, continue practice.

---

# 94. G5 Exit Criteria

The G5 roadmap establishes the following final capability set. fileciteturn186file6

- [ ] Explain the interview format and evaluation model.
- [ ] Clarify ambiguous requirements.
- [ ] Estimate system scale.
- [ ] Apply the reusable system-design framework.
- [ ] Explain major Data Engineering trade-offs.
- [ ] Draw and communicate architectures.
- [ ] Design batch analytics platforms.
- [ ] Design streaming platforms.
- [ ] Design CDC systems.
- [ ] Design ML feature platforms.
- [ ] Design log/metrics platforms.
- [ ] Design attribution systems.
- [ ] Design IoT platforms.
- [ ] Design GDPR deletion systems.
- [ ] Design RAG/vector data platforms.
- [ ] Handle failure scenarios.
- [ ] Handle deep-dive follow-ups.
- [ ] Answer behavioural questions.
- [ ] Complete take-home assignments.
- [ ] Perform live pipeline coding.
- [ ] Run realistic mocks.
- [ ] Self-review objectively.
- [ ] Track and eliminate recurring weaknesses.
- [ ] Demonstrate Senior-level readiness.
- [ ] Demonstrate Staff-level readiness where applicable.

---

# 95. Topic 19 Completion Checklist

- [ ] I understand how to conduct a mock interview.
- [ ] I can simulate realistic interview conditions.
- [ ] I can practice system design under time pressure.
- [ ] I can practice failure scenarios.
- [ ] I can practice behavioural interviews.
- [ ] I can practice Python.
- [ ] I can practice SQL.
- [ ] I can practice PySpark.
- [ ] I can practice live pipeline coding.
- [ ] I can run full interview loops.
- [ ] I can record my answers.
- [ ] I can self-review.
- [ ] I can score myself consistently.
- [ ] I maintain an error log.
- [ ] I can identify knowledge gaps.
- [ ] I can identify reasoning gaps.
- [ ] I can identify communication gaps.
- [ ] I can identify pressure gaps.
- [ ] I can re-attempt weak areas.
- [ ] I can track improvement over time.
- [ ] I can handle interviewer pushback.
- [ ] I can manage interview time.
- [ ] I can distinguish Senior vs Staff expectations.
- [ ] I can complete a full interview loop.
- [ ] I can produce a final readiness report.
- [ ] I know my weakest interview areas.
- [ ] I have a targeted improvement plan.
- [ ] I can demonstrate G5 capabilities under time pressure.
- [ ] I have completed the required mock evidence.
- [ ] I have prepared a company-specific brief.

---

# 96. Roadmap Coverage Audit

| Roadmap requirement | Covered? | Evidence |
|---|---|---|
| Weekly practice plan | Yes | §§49–52 |
| Design cases | Yes | §§13–25, 74 |
| Follow-up drills | Yes | §§26–34, 54 |
| Behavioural stories | Yes | §§35–39 |
| SQL/coding practice | Yes | §§40–41 |
| Rest/recovery | Yes | §82 |
| Solo recorded mocks | Yes | §73 |
| Peer mocks | Yes | §72 |
| Mentor/community concept | Yes | §72 and practice framework |
| Self-review rubric | Yes | §§9–12, 66–69 |
| Recording review | Yes | §70 |
| Error log | Yes | §§55–57 |
| Spaced repetition | Yes | §58 |
| Company-specific preparation | Yes | §90 |
| Peer interviewer practice | Yes | §72, §91 |
| Final-week plan | Yes | §83 |
| Interview-day preparation | Yes | §83 |
| Post-interview reflection | Yes | §83 |
| Rejection/feedback handling | Yes | §83 and §89 evidence model |
| Six design mocks | Yes | §92 |
| Three partner mocks | Yes | §92 |
| Two follow-up-only mocks | Yes | §92 |
| Two behavioural mocks | Yes | §92 |
| Three recurring mistakes eliminated | Yes | §92 |
| Two peer interviews | Yes | §91–92 |
| Company-specific brief | Yes | §90, §92 |
| Progress measurement | Yes | §§59–65 |
| Full interview loops | Yes | §§42–48 |
| Senior/Staff readiness | Yes | §§12, 65, 89 |
| G5 integration | Yes | §93 |
| G5 exit criteria | Yes | §94 |

---

# 97. Final Operating Standard

The complete Topic 19 operating loop is:

```text
SELECT
  ↓
TIME-BOX
  ↓
ATTEMPT
  ↓
RECORD
  ↓
SCORE
  ↓
COMPARE
  ↓
DIAGNOSE
  ↓
LOG ROOT CAUSE
  ↓
CORRECT
  ↓
SPACE
  ↓
RE-ATTEMPT
  ↓
PARTNER MOCK
  ↓
FULL LOOP
  ↓
MEASURE
  ↓
ADAPT
```

### The standard

Do not ask:

> "Have I studied enough?"

Ask:

> "Can I repeatedly demonstrate the required capability under realistic conditions?"

That is the difference between **knowledge preparation** and **interview readiness**.

---

# 98. Final Cheat Sheet — One Page

```text
BEFORE
────────────────────────────────────────
Review framework
Review recent errors
Review stories
Choose practice target
Set timer
Prepare recording

DURING
────────────────────────────────────────
Clarify
Estimate
Structure
Think aloud
Draw / code
Test
Handle pushback
Manage time
Summarize

AFTER
────────────────────────────────────────
Score
Record evidence
Identify root cause
Compare reference
Choose corrective action
Schedule re-attempt

SYSTEM DESIGN
────────────────────────────────────────
Requirements
→ Estimates
→ Architecture
→ Data model
→ Processing
→ Serving
→ Quality
→ Reliability
→ Security
→ Cost
→ Trade-offs
→ Failures
→ Evolution

FAILURE
────────────────────────────────────────
Detect
→ Diagnose
→ Blast radius
→ Contain
→ Recover
→ Validate
→ Prevent

BEHAVIOURAL
────────────────────────────────────────
Situation
→ Task
→ Action
→ Result
→ Learning

CODING
────────────────────────────────────────
Clarify
→ Grain
→ Approach
→ Implement
→ Test
→ Edge cases
→ Complexity
→ Production

READINESS
────────────────────────────────────────
Consistency
+
Evidence
+
Follow-up resilience
+
Time management
+
Communication
=
Credible readiness
```

---

# 99. Final Principle

The purpose of G5 is not to make you memorize nine architectures.

It is to make you capable of entering an unfamiliar Data Engineering interview and reliably doing the following:

```text
Understand the problem
        ↓
Clarify ambiguity
        ↓
Estimate the system
        ↓
Structure the design
        ↓
Choose appropriate technology
        ↓
Explain trade-offs
        ↓
Handle failures
        ↓
Communicate clearly
        ↓
Implement when required
        ↓
Defend decisions
        ↓
Adapt to pushback
        ↓
Learn from mistakes
        ↓
Repeat until consistent
```

### Senior standard

> **Solve the problem correctly, communicate the reasoning clearly, and demonstrate practical production judgment.**

### Staff standard

> **Solve the right problem, simplify ambiguity, make durable architectural trade-offs, influence the direction, and demonstrate systemic technical leadership.**

### Final G5 principle

> **Confidence should be the result of repeated evidence—not the substitute for it.**
