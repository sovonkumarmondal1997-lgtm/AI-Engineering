# Roadmap — Gap Module G5: Data Engineering System Design Interviews

This is the learning roadmap for the fifth gap module, **Data Engineering
System Design Interviews**. It tells you **what** to learn to perform well
in data engineering system design, behavioural, and take-home interviews,
**in what order**, **how** to practise each topic, and **how to prove to
yourself** that you are ready.

**When to take it:** after completing Stage 2 (Modules 2.1–2.22), ideally
while or after building the **Capstone** (Project 07) and one depth track
(Gap Module G3 AWS or G4 Databricks). This module does not teach new
technology; it teaches you to **use everything you already know under
interview conditions** — clearly, quickly, and with good judgement.

**What this module is not:** it does **not** repeat the technical content of
Stage 2 or the question banks that already exist: SQL interview practice
(Module 2.6), pandas (Module 2.3), data-modelling design rounds (Module
2.8), transformation-pipeline design questions (Module 2.12), Spark (Module
2.14), and streaming (Module 2.16) interview practice, or the Python coding
interview practice from Stage 1 (Module 1.4). Here you learn the **method**
for end-to-end system design, a **library of full design cases**, how to
handle **deep-dive and failure follow-ups**, **behavioural** interviews,
**take-home and live pipeline coding** rounds, and a **practice system**.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain how data engineering interview loops are structured and how system
  design rounds are evaluated at different seniority levels.
- Clarify ambiguous problems into precise requirements and a clear scope
  within the first minutes of an interview.
- Estimate volumes, throughput, storage, compute, and cost quickly and
  sanity-check them.
- Apply a **repeatable design framework** that covers ingestion, storage,
  processing, serving, and the cross-cutting concerns interviewers look
  for.
- Justify every major choice with explicit **trade-offs**.
- Draw clear diagrams and communicate a design while collaborating with the
  interviewer.
- Design nine common data platform problems end to end.
- Handle **failure scenarios** and **deep-dive follow-ups** calmly and
  concretely.
- Tell compelling, specific **behavioural stories** from your projects.
- Deliver strong **take-home assignments** and **live pipeline coding**
  sessions.
- Run a **mock-interview practice system** that measurably improves your
  performance.

---

## 2. Prerequisites

| Earlier knowledge | Where you learned it | How it is used here |
| --- | --- | --- |
| The whole data engineering lifecycle | Stage 2 — Modules 2.1–2.22 | The raw material of every design |
| Estimation and cost | Module 2.21 | Fast interview estimation builds on it |
| Reference architectures of a cloud | Gap Module G3 or G4 | Concrete service choices in designs |
| End-to-end platform experience | Stage 2 Projects 01–07 | Examples, stories, and credibility |
| Existing interview banks (SQL, modelling, Spark, streaming, pipelines) | Modules 2.6, 2.8, 2.12, 2.14, 2.16 | Used alongside this module; **not** repeated |

**Tools needed:**

- A diagramming tool you can use fast (e.g. Excalidraw, draw.io, or a
  virtual whiteboard) — plus paper and pen for in-person practice.
- A timer, a screen recorder (for self-review), and a notebook or document
  for your **error log** and **story bank**.
- At least one practice partner (a peer, mentor, or study group) for mock
  interviews.

---

## 3. How the module is organised

The nineteen topics are grouped into six phases. Work through them **in
order**, then keep practising with Phase F.

```text
Phase A — Understand the Interview                      (Basics)
  01 System design interview format and evaluation rubric

Phase B — The Core Method                               (Basics → Intermediate)
  02 Requirements clarification and scoping
  03 Back-of-the-envelope estimation for data systems
  04 A reusable design framework for data platforms
  05 Trade-off catalogue: batch, streaming, storage, and engines
  06 Diagramming and communicating designs

Phase C — The Design Case Library                        (Intermediate → Advanced)
  07 Batch analytics platform
  08 Real-time clickstream analytics
  09 CDC replication to the lakehouse
  10 ML feature platform
  11 Log and metrics analytics at scale
  12 Ad attribution and deduplication
  13 IoT telemetry ingestion
  14 GDPR deletion across a platform
  15 RAG and vector data platform

Phase D — Depth Under Pressure                          (Advanced)
  16 Failure scenarios and deep-dive follow-up questions

Phase E — Beyond the Design Round                        (Intermediate → Advanced)
  17 Behavioural interviews for data engineers
  18 Take-home assignments and live pipeline coding

Phase F — The Practice System                            (Ongoing)
  19 Mock interview plans and self-review

Consolidate
  practice-questions.md
  Module mini-project: your interview portfolio (→ Projects/05-system-design-interview-portfolio.md)
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07…15 ──► 16 ──► 17 ──► 18 ──► 19
know   ask    size   structure justify show  apply to  survive tell    deliver  practise
the    the    it     the       choices  it    real       follow- your    work     until it
game   right         design                   problems   ups     stories samples  is natural
       questions
```

Why this order:

- You must know how you are judged (01) before practising anything.
- The method (02–06) is applied to every case; cases without a method
  become memorised answers that fall apart under follow-up questions.
- The case library (07–15) builds breadth; failure scenarios (16) build
  depth on the same cases.
- Behavioural (17) and take-home/live coding (18) complete a typical loop.
- The practice system (19) turns knowledge into performance.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**, followed by **ongoing mock
interviews** (two to three per week) until your interviews.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — format and rubric · Topics 02–04 — requirements, estimation, framework |
| 2 | Topics 05–06 — trade-offs and communication · Cases 07–09 |
| 3 | Cases 10–15 (two per session, time-boxed) |
| 4 | Topic 16 — failure scenarios · Topic 17 — behavioural · Topic 18 — take-homes and live coding · Topic 19 — mock plan · portfolio |
| Ongoing | Weekly mocks, error-log review, case re-runs, company-specific preparation |

---

## 5. How to study every topic (the interview practice loop)

```text
Learn the method → Attempt under time pressure → Record yourself
→ Compare with a reference design → Score with the rubric → Log mistakes
→ Re-attempt later → Mock with a partner → Update your notes
```

1. **Learn** the method or case material in the topic file.
2. **Attempt** the exercise under realistic time limits (e.g. 45 minutes
   for a design case), speaking aloud and drawing as you would in an
   interview.
3. **Record** yourself (audio and screen) whenever possible.
4. **Compare** your design with the reference design and notes in the topic
   file — and with your Stage 2 projects.
5. **Score** yourself with the rubric from Topic 01.
6. **Log mistakes** in your **error log**: what you missed, why, and the
   one change you will make next time.
7. **Re-attempt** the same case a week later without notes (spaced
   repetition).
8. **Mock** the case with a partner who plays interviewer and pushes back.
9. **Update** your personal cheat sheets (framework, trade-offs, estimation
   numbers, story bank).

Keep one `interview_prep/` folder:

```text
interview_prep/
├── framework.md          # your one-page design framework and checklists
├── estimation.md         # numbers and templates you know by heart
├── tradeoffs.md          # your trade-off catalogue in your own words
├── cases/                # one file per case: your design, diagram, follow-ups
├── diagrams/             # exported diagrams
├── story-bank.md         # behavioural stories (Topic 17)
├── take-home-template/   # reusable repository template (Topic 18)
├── error-log.md          # every mistake and the fix
└── mocks/                # recordings, scores, and feedback per mock
```

---

## 6. Phase A — Understand the Interview (Basics)

### Topic 01 — [System design interview format and evaluation rubric](01-system-design-interview-format-and-evaluation-rubric.md)

**Why it comes first:** Many strong engineers fail design interviews not
from lack of knowledge but from misunderstanding what is being assessed and
how time should be used.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Typical data engineering interview loops: recruiter and hiring-manager screens, SQL and coding, data modelling, **system design**, behavioural, and sometimes a take-home or live pipeline exercise |
| Basics | The shape of a design round: problem statement, clarification, high-level design, deep dives, trade-offs, wrap-up — usually 45–60 minutes |
| Basics | What "data engineering system design" means compared with general software system design: data flows, correctness over time, late data, backfills, quality, governance, and cost |
| Intermediate | **The evaluation rubric** most interviewers use (explicitly or not): requirement gathering, estimation, architecture, depth in chosen areas, trade-off reasoning, reliability and data quality, security and privacy, cost awareness, communication and collaboration |
| Intermediate | **Levelling**: what is expected at mid-level (a sound design), senior (depth, trade-offs, operations), and staff (organisation-wide concerns, evolution, cross-team impact) |
| Intermediate | Common failure patterns: jumping to tools, silent drawing, over-designing, ignoring requirements, no numbers, no failure handling, running out of time |
| Advanced | Reading the interviewer: hints, redirections, and "what would you do if…" as signals of what they want to explore |
| Advanced | Company and domain differences (product analytics, ad tech, fintech, IoT, AI platforms) and how to prepare for them |

**How to learn it**

1. Read the topic file.
2. Write your own **self-scoring rubric** (a table of the evaluation areas
   with what 1, 2, and 3 look like) — you will use it after every practice
   session.
3. Watch or read two example design interviews and score them with your
   rubric.

**Hands-on exercise — `interview_prep/rubric.md`**

1. Create the rubric and a one-page "time plan" for a 45-minute round (e.g.
   5 min requirements, 5 min estimates, 15 min high-level design, 15 min
   deep dives, 5 min trade-offs and wrap-up).
2. Describe, in your own words, the difference between a mid-level, senior,
   and staff answer to the same question.
3. List your five biggest risks in interviews (e.g. rambling, weak on
   estimation) — they become the first entries of your error log.

**Checkpoint — you are ready to move on when you can:**

- [ ] Describe a typical data engineering interview loop.
- [ ] List the rubric areas and what strong performance looks like in each.
- [ ] Plan the time of a design round.

**Common mistakes:** preparing only technology; ignoring communication as
an evaluation area; treating the interviewer as an examiner instead of a
collaborator.

---

## 7. Phase B — The Core Method (Basics → Intermediate)

### Topic 02 — [Requirements clarification and scoping](02-requirements-clarification-and-scoping.md)

**Why here:** Every good design starts with the right questions. Clarifying
requirements shows seniority and prevents designing the wrong system.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Functional requirements**: sources, consumers, what questions or products the data must support |
| Basics | **Non-functional requirements**: freshness/latency, volume and growth, correctness (duplicates, late data, exactly-once needs), availability, retention, security and privacy, cost limits |
| Basics | Stating **assumptions** explicitly when the interviewer does not specify |
| Intermediate | A **clarifying-question checklist** for data systems: who consumes, how fresh, how big, how correct, how long kept, who may see it, what already exists, what must not break |
| Intermediate | **Scoping**: agreeing an MVP and naming extensions you will discuss if time allows |
| Intermediate | Turning answers into **measurable** SLAs (Module 2.1) and writing them on the board |
| Advanced | Recognising hidden requirements (e.g. "billing" implies exactness and auditability; "users in the EU" implies privacy obligations) |
| Advanced | Time-boxing clarification (about 5 minutes) and returning to requirements when trade-offs arise |

**How to learn it**

1. Read the topic file.
2. For every case in Phase C, write your clarifying questions **before**
   reading the case notes.
3. Practise with a partner who answers vaguely — learn to propose sensible
   assumptions.

**Hands-on exercise — `interview_prep/framework.md` (requirements section)**

1. Build your clarifying-question checklist (no more than one page).
2. For five one-line prompts (e.g. "design analytics for a food delivery
   app"), write the requirements you would agree, with numbers and
   assumptions, in under 5 minutes each.
3. Identify one hidden requirement in each prompt.

**Checkpoint:**

- [ ] Separate functional and non-functional requirements.
- [ ] Turn vague prompts into measurable requirements in 5 minutes.
- [ ] Scope an MVP and name extensions.

**Common mistakes:** asking dozens of low-value questions; asking none;
forgetting correctness and privacy; not writing requirements down.

---

### Topic 03 — [Back-of-the-envelope estimation for data systems](03-back-of-the-envelope-estimation-for-data-systems.md)

**Why here:** Numbers drive design: whether data fits on one machine, how
many partitions a topic needs, whether streaming is affordable. Interviewers
expect quick, reasonable estimates — not precision.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Powers of ten, bytes per record, and converting between per-second, per-day, and per-year volumes |
| Basics | Deriving event rates from users (e.g. daily active users × events per user ÷ seconds per day) and applying a **peak factor** |
| Basics | Storage per day and per year, with compression ratios for columnar formats (Module 2.5) and replication factors |
| Intermediate | Throughput-based sizing: partitions or shards from per-partition throughput, consumers from per-consumer processing rate (Module 2.16) |
| Intermediate | Compute sizing: data scanned per job, cluster throughput, run time estimates (Modules 2.14, 2.21) |
| Intermediate | Serving estimates: queries per second, cache hit rates, and latency budgets (Module 2.22) |
| Intermediate | **Cost** estimates: storage, compute hours, scans, and data transfer at order-of-magnitude level (Modules 2.17, 2.21) |
| Advanced | Reference numbers you should know approximately (memory and disk bandwidth, network throughput, object-storage request latency, typical Kafka partition throughput) — and saying clearly that they are approximations |
| Advanced | Sanity checks: does the answer make sense? Would it fit in memory? Is it a laptop, a cluster, or a warehouse problem? |
| Advanced | Using estimates to **drive decisions** out loud ("at 50 GB per day, a single-node engine suffices; at 50 TB, we need distributed processing") |

**How to learn it**

1. Read the topic file.
2. Memorise a small set of reference numbers and write them in
   `estimation.md`.
3. Do ten timed estimation drills (3 minutes each) and check them with a
   calculator afterwards.

**Hands-on exercise — `interview_prep/estimation.md`**

1. Create estimation templates for event volume, storage, partitions,
   cluster size, serving load, and monthly cost.
2. Estimate each case in Phase C before designing it.
3. Revisit Stage 2 projects: compare your estimates with the measured
   numbers from those projects.

**Checkpoint:**

- [ ] Estimate event rates, storage, partitions, compute, and cost in
      minutes.
- [ ] Sanity-check estimates and use them to justify decisions.

**Common mistakes:** skipping estimation; precise arithmetic that wastes
time; forgetting peaks, compression, or replication; estimates that are
never used in the design.

---

### Topic 04 — [A reusable design framework for data platforms](04-a-reusable-design-framework-for-data-platforms.md)

**Why here:** A framework keeps you structured under pressure and ensures
you never forget areas interviewers value, such as data quality or
backfills.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | A step-by-step framework: **requirements → estimates → high-level data flow → data model and storage → processing → serving → cross-cutting concerns → failure handling → evolution** |
| Basics | The high-level flow: sources → ingestion → storage layers (bronze/silver/gold) → processing (batch/streaming) → serving → consumers (Module 2.1) |
| Intermediate | For each step, the key decisions and what to say: ingestion mode, storage format and layout, table format and catalog, processing engine, orchestration, serving interface |
| Intermediate | **Cross-cutting checklist**: data quality and contracts, idempotency and backfills, late data, schema evolution, orchestration and SLAs, observability and alerting, security, privacy and governance, cost |
| Intermediate | Time allocation and **when to go deep**: choosing the one or two areas where the problem is truly hard |
| Advanced | Adapting the framework to the problem type (analytics, streaming, ML, AI, compliance) |
| Advanced | Designing for **evolution**: what changes at 10× scale, with new sources, or new consumers |

**How to learn it**

1. Read the topic file.
2. Write your framework on one page, in your own words.
3. Apply it to your Capstone and check that every part of the capstone maps
   to a framework step.

**Hands-on exercise — `interview_prep/framework.md`**

1. Finalise your one-page framework and cross-cutting checklist.
2. Practise the framework on two simple prompts in 30 minutes each.
3. After each attempt, tick which checklist items you covered.

**Checkpoint:**

- [ ] Apply a structured framework from requirements to evolution.
- [ ] Cover cross-cutting concerns without prompting.
- [ ] Choose where to go deep.

**Common mistakes:** reciting the framework mechanically; spending all the
time on the high-level diagram; never reaching failure handling or cost.

---

### Topic 05 — [Trade-off catalogue: batch, streaming, storage, and engines](05-trade-off-catalogue-batch-streaming-storage-and-engines.md)

**Why here:** "It depends" is only a good answer when followed by *on
what*. Strong candidates compare options against the stated requirements
in one or two sentences each.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | How to present a trade-off: option A vs option B, the deciding criteria, and your choice **for these requirements** |
| Basics | Processing: batch vs micro-batch vs streaming; ETL vs ELT (Module 2.1) |
| Basics | Storage: warehouse vs lake vs lakehouse; row vs columnar; table formats (Modules 2.1, 2.5, 2.15) |
| Intermediate | Ingestion: pull vs push; full vs incremental vs CDC; managed connectors vs custom code (Module 2.9) |
| Intermediate | Engines: single-node (DuckDB/Polars) vs Spark vs Flink vs warehouse SQL (Modules 2.4, 2.14, 2.16) |
| Intermediate | Messaging: Kafka vs managed streams vs queues (Module 2.16, Gap Module G3) |
| Intermediate | Modelling: normalised vs dimensional vs wide tables (Module 2.8) |
| Intermediate | Correctness: at-least-once + idempotency vs transactional exactly-once; dedupe strategies (Modules 2.12, 2.16) |
| Advanced | Serving: direct queries vs pre-aggregation vs caches vs specialised stores (Module 2.22) |
| Advanced | Platform: managed vs self-hosted; build vs buy; one engine vs several; cost vs freshness vs complexity |
| Advanced | Organisational trade-offs: team skills, operational load, vendor lock-in, time to market |

**How to learn it**

1. Read the topic file.
2. Write each trade-off in your own words as a two-sentence answer ending
   with "…so for requirement X, I would choose Y."
3. Practise explaining five trade-offs aloud in under a minute each.

**Hands-on exercise — `interview_prep/tradeoffs.md`**

1. Build your trade-off catalogue (at least 20 entries) with deciding
   criteria and examples from your projects.
2. For each Phase C case, note which trade-offs matter most.

**Checkpoint:**

- [ ] Explain the main trade-offs across processing, storage, engines,
      ingestion, correctness, and serving.
- [ ] Tie every choice back to stated requirements.

**Common mistakes:** listing pros and cons without choosing; tool
preferences instead of criteria; ignoring cost and operational burden.

---

### Topic 06 — [Diagramming and communicating designs](06-diagramming-and-communicating-designs.md)

**Why here:** A design the interviewer cannot follow does not score well,
however good it is. Clear diagrams and narration are skills you can
practise.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Diagram conventions: left-to-right data flow, boxes for components, cylinders for stores, arrows labelled with data, format, volume, and latency |
| Basics | Starting with a simple end-to-end diagram, then zooming into components |
| Basics | Narrating while drawing: saying what you are drawing and why |
| Intermediate | **Checking in** with the interviewer: confirming direction, asking which area to explore deeper |
| Intermediate | Writing requirements, assumptions, and estimates in a corner of the board and referring back to them |
| Intermediate | Handling pushback and hints gracefully: acknowledge, reconsider, adjust, explain |
| Intermediate | **Summarising**: a 60-second recap of the design, key trade-offs, and next steps at the end |
| Advanced | Remote interviews: tool fluency, screen layout, and verbal clarity when you cannot point |
| Advanced | Managing time visibly: "I'll spend five minutes on storage, then move to failure handling" |

**How to learn it**

1. Read the topic file.
2. Redraw your Capstone architecture in 10 minutes with the conventions
   above and narrate it to a recording.
3. Watch the recording and note unclear moments.

**Hands-on exercise — `interview_prep/diagrams/`**

1. Practise drawing each Phase C case's high-level diagram in under 8
   minutes.
2. Practise a 60-second summary for three designs.
3. Do one mock where the partner interrupts often and changes a requirement
   midway.

**Checkpoint:**

- [ ] Draw clear, labelled diagrams quickly.
- [ ] Narrate, check in, and summarise.
- [ ] Handle interruptions and changing requirements.

**Common mistakes:** silent drawing; unlabelled arrows; a single enormous
diagram; defensive reactions to hints.

---

## 8. Phase C — The Design Case Library (Intermediate → Advanced)

### How to work through every case (07–15)

Each case file contains a problem statement, requirements, estimates, a
reference design, deep-dive areas, trade-offs, failure modes, and follow-up
questions. For each case:

1. Read **only the problem statement**.
2. Attempt it in **45 minutes**, aloud, with a diagram, using your
   framework.
3. Compare with the reference design; score yourself with the rubric.
4. Answer the case's follow-up questions in writing.
5. Log mistakes; re-attempt in a week; later, do it as a mock with a
   partner.
6. Link the case to the Stage 2 project or module where you built something
   similar — this gives you real stories to tell.

---

### Case 07 — [Batch analytics platform](07-design-case-batch-analytics-platform.md)

**Prompt type:** "Design the analytics platform for a company with several
operational systems and SaaS tools; finance needs daily reports by 07:00."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| End-to-end ELT thinking, modelling, SLAs, backfills, cost | Sources and ingestion (incremental, CDC, connectors); lakehouse or warehouse choice; layers; dimensional modelling; dbt-style transformations; orchestration with dependencies; quality gates and write–audit–publish; late data and month-end restatements; consumers and semantic layer; cost controls |

**Deep dives to prepare:** incremental models and late data; SCD Type 2;
backfill of two years; metric consistency across dashboards.
**Related work:** Modules 2.8, 2.12, 2.13; Project 03.

---

### Case 08 — [Real-time clickstream analytics](08-design-case-real-time-clickstream-analytics.md)

**Prompt type:** "Design live product analytics for a web and mobile app
with 50 million daily users."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Streaming fundamentals, event time, scale, serving | Event design and collection; Kafka topics, keys, partitions; validation and dedupe; watermarks and windows; sessionisation; stateful processing; serving store and dashboards; raw archive and batch reconciliation; bot filtering; lag and backpressure |

**Deep dives to prepare:** late mobile events; exactly-once counting; hot
keys; streaming vs micro-batch cost.
**Related work:** Module 2.16; Project 05.

---

### Case 09 — [CDC replication to the lakehouse](09-design-case-cdc-replication-to-lakehouse.md)

**Prompt type:** "Replicate 200 production database tables into the
lakehouse with minutes of latency and full history."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Log-based CDC, ordering, correctness, source safety | Logical decoding and connectors; initial snapshot and handoff; topics and keys; bronze change log; ordered, idempotent merges into mirrors; SCD history; deletes; schema evolution policy; replication slot monitoring; reconciliation; table maintenance |

**Deep dives to prepare:** out-of-order events; adding tables without
re-snapshotting; source failover; schema changes.
**Related work:** Modules 2.9, 2.15, 2.16; Project 02.

---

### Case 10 — [ML feature platform](10-design-case-ml-feature-platform.md)

**Prompt type:** "Design a feature platform for fraud and churn models,
with batch and real-time features."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Point-in-time correctness, online/offline consistency | Feature definitions and ownership; offline store on the lakehouse; online store and latency; batch and streaming feature pipelines; point-in-time training sets; training–serving skew prevention; backfills of new features; freshness and drift monitoring; access control |

**Deep dives to prepare:** leakage; streaming aggregations as features;
feature backfills; online store sizing.
**Related work:** Modules 2.8, 2.22; Gap Module G4 Topic 14.

---

### Case 11 — [Log and metrics analytics at scale](11-design-case-log-and-metrics-analytics-at-scale.md)

**Prompt type:** "Collect and analyse application logs and metrics from
10,000 servers; engineers need search within minutes; keep one year."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Very high volume, retention tiers, query patterns, cost | Collection agents and buffering; a streaming backbone; parsing and structuring; hot storage for recent data (search or columnar OLAP) vs cheap storage for history; partitioning by time and service; high-cardinality problems; sampling and aggregation (downsampling); retention and tiering; cost per GB; access control and PII in logs |

**Deep dives to prepare:** handling 10× bursts during incidents; indexing vs
columnar storage; label cardinality; lifecycle tiers.
**Related work:** Modules 2.5, 2.16, 2.17, 2.20, 2.21.

---

### Case 12 — [Ad attribution and deduplication](12-design-case-ad-attribution-and-deduplication.md)

**Prompt type:** "Attribute conversions to ad clicks within a 7-day window,
dedupe events, and produce billing-grade numbers."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Joins across time windows, dedupe at scale, exactness, privacy | Impression, click, and conversion streams; event ids and dedupe windows; attribution models (last touch, multi-touch); stream–stream joins vs batch recomputation; late conversions and restatements; billing correctness and reconciliation; fraud and bot filtering; privacy and consent; auditability |

**Deep dives to prepare:** dedupe at billions of events per day; the
7-day join state problem; real-time estimates vs final billing numbers.
**Related work:** Modules 2.12, 2.16, 2.8 (events and attribution).

---

### Case 13 — [IoT telemetry ingestion](13-design-case-iot-telemetry-ingestion.md)

**Prompt type:** "Ingest telemetry from 5 million devices every 10 seconds;
detect anomalies and keep history for analysis."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Massive fan-in, unreliable devices, time series | Device protocols and gateways; buffering at the edge; bursty and out-of-order data; device identity and security; partitioning by device; time-series storage and downsampling; real-time anomaly detection with state; device state tables; late data and clock skew; retention tiers; cost |

**Deep dives to prepare:** reconnect storms; clock skew; hot devices;
storing years of high-resolution data cheaply.
**Related work:** Modules 2.2, 2.5, 2.16, 2.21.

---

### Case 14 — [GDPR deletion across a platform](14-design-case-gdpr-deletion-across-a-platform.md)

**Prompt type:** "Design a system that guarantees a user's data is deleted
from every data system within 30 days of a request — and proves it."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Governance thinking, completeness, immutable storage challenges | Request intake and identity resolution; data inventory and classification; lineage to find copies; deletion per system type (databases, lake tables with snapshots, warehouses with time travel, Kafka, caches, features, vectors, logs, backups); crypto-shredding; verification scans; audit certificates; SLAs, retries, and escalation |

**Deep dives to prepare:** deleting from immutable logs and backups;
deleting from lakehouse history; proving deletion to auditors.
**Related work:** Modules 2.15, 2.20; Capstone M9.

---

### Case 15 — [RAG and vector data platform](15-design-case-rag-and-vector-data-platform.md)

**Prompt type:** "Build the data platform behind a company-wide AI
assistant that answers questions from documents, tickets, and databases."

| What the interviewer tests | Key design points to cover |
| --- | --- |
| Data engineering for AI: freshness, permissions, evaluation | Source connectors and document parsing; chunking strategy; metadata including access control lists; embedding pipelines and cost; incremental updates and deletions; vector index choice and hybrid search; permission-aware retrieval; evaluation sets and quality monitoring; model and index versioning; PII handling; serving latency and caching |

**Deep dives to prepare:** re-embedding millions of documents after a model
change; keeping permissions in sync; measuring retrieval quality.
**Related work:** Module 2.22; Capstone M10.

---

## 9. Phase D — Depth Under Pressure (Advanced)

### Topic 16 — [Failure scenarios and deep-dive follow-up questions](16-failure-scenarios-and-deep-dive-follow-up-questions.md)

**Why here:** Senior interviews are decided in the follow-ups. After the
high-level design, interviewers probe: "what happens when…?". Calm,
concrete answers show real experience.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | A structure for follow-ups: **detect → contain → recover → prevent**, and the effect on consumers and SLAs |
| Basics | The standard follow-up families: scale (10×, 100×), failures (component, region, source), data problems (late, duplicate, malformed, schema change), operations (backfill, reprocessing, upgrades), cost (cut by half), security (leak, access) |
| Intermediate | **Component deep dives** you should be able to explain on demand: Kafka partitions and consumer groups, Spark shuffles and skew, table-format commits and compaction, merge performance, watermarks and state, orchestration retries and idempotency, cache invalidation |
| Intermediate | **Exactly-once** questions: what exactly-once means end to end and how your design achieves the effect (Module 2.16) |
| Intermediate | **Backfill** questions: rebuilding two years of data without breaking daily SLAs (Modules 2.12, 2.13) |
| Advanced | **Disaster recovery**: losing a metadata store, a cluster, or a region; RPO and RTO (Capstone M12) |
| Advanced | **Evolution** questions: new consumers, new regions, new regulations, merging with another company's platform |
| Advanced | Answering "I don't know" well: reasoning from first principles and stating how you would find out |

**How to learn it**

1. Read the topic file.
2. For each Phase C case, write answers to at least five follow-ups using
   the detect → contain → recover → prevent structure.
3. Practise with a partner who asks only follow-ups for 30 minutes.

**Hands-on exercise — `interview_prep/cases/*` (follow-ups sections)**

1. Build a follow-up question bank (at least 40 questions) across all cases.
2. Answer each in writing in 5 sentences or fewer.
3. Record a 30-minute "follow-up only" mock and score it.

**Checkpoint:**

- [ ] Answer scale, failure, data, operations, cost, and security
      follow-ups with structure.
- [ ] Go deep on core components on demand.
- [ ] Reason from first principles when you do not know an answer.

**Common mistakes:** vague answers ("we'd add monitoring"); ignoring
consumer impact; answers without numbers; bluffing.

---

## 10. Phase E — Beyond the Design Round (Intermediate → Advanced)

### Topic 17 — [Behavioural interviews for data engineers](17-behavioural-interviews-for-data-engineers.md)

**Why here:** Behavioural rounds often decide seniority and hiring
outcomes. Data engineers are asked about incidents, stakeholders, quality,
and impact — you need specific, well-structured stories.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Story structures: **STAR** (situation, task, action, result) or similar; keeping stories to about 2–3 minutes |
| Basics | Common themes: ownership, dealing with ambiguity, conflict and disagreement, failure and learning, influence without authority, prioritisation, mentoring |
| Intermediate | **Data-engineering-specific themes**: a data quality incident, a metric dispute between teams, a pipeline you made reliable, a cost reduction, a migration, a trade-off you pushed back on, working with analysts or ML teams |
| Intermediate | **Quantifying results**: SLA improvements, incidents reduced, hours saved, cost cut, adoption numbers |
| Intermediate | Building a **story bank** mapped to themes, using real experience and your Stage 2 projects (honestly labelled as projects) |
| Advanced | Seniority signals: scope of impact, decisions under uncertainty, influencing across teams, raising the bar for others |
| Advanced | Questions to ask interviewers about the team's data platform, practices, and challenges |
| Advanced | Honesty and integrity: never inventing experience; describing personal contributions precisely ("I" vs "we") |

**How to learn it**

1. Read the topic file.
2. Draft 10–12 stories covering all themes; each with a measurable result.
3. Tell each story aloud to a timer and a partner; tighten it.

**Hands-on exercise — `interview_prep/story-bank.md`**

1. Build the story bank: theme, story title, STAR outline, metrics, lessons,
   and which questions it answers.
2. Include at least three stories from Stage 2 projects (e.g. a chaos-drill
   finding, a cost optimisation, a quality gate that caught a defect).
3. Prepare five thoughtful questions to ask interviewers.

**Checkpoint:**

- [ ] Tell structured, specific, quantified stories within 3 minutes.
- [ ] Cover all common and data-specific themes.
- [ ] Show seniority signals honestly.

**Common mistakes:** vague stories without results; talking only about the
team; overly long context; stories that do not answer the question asked.

---

### Topic 18 — [Take-home assignments and live pipeline coding](18-take-home-assignments-and-live-pipeline-coding.md)

**Why here:** Many companies assess data engineers with a take-home
pipeline or a live coding session building a small data transformation.
These reward production habits — within strict time limits.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Typical take-homes: build an ingestion pipeline from an API or files into a database; clean and model a dataset; answer analytical questions; design and partially implement a small platform |
| Basics | Reading the brief carefully: requirements, time limit, evaluation criteria, and what not to build |
| Intermediate | **Delivering a strong take-home**: clear README (how to run, assumptions, design decisions, trade-offs, what you would do with more time), a simple and correct solution, tests, idempotent runs, basic data validation, and reproducible set-up (e.g. `uv` and Docker Compose) |
| Intermediate | Time management: a plan with checkpoints, and stopping on time |
| Intermediate | **Live pipeline coding**: implementing a small transformation (deduplication, sessionisation, incremental merge, aggregation) in Python or SQL while thinking aloud, starting with a correct simple version and tests |
| Intermediate | Collaborative coding etiquette: clarifying, narrating, testing edge cases, and accepting hints |
| Advanced | Production touches that impress without over-engineering: logging, configuration, error handling, a small data-quality check, and a note on scaling |
| Advanced | Presenting a take-home in a follow-up interview: walking through decisions and discussing how it would change at 100× scale |
| Advanced | Ethics: respecting time limits and confidentiality; not using others' solutions |

**How to learn it**

1. Read the topic file.
2. Build a reusable **take-home template repository** (project layout,
   `uv` configuration, Compose file for PostgreSQL/MinIO, test set-up,
   README template).
3. Complete two practice take-homes within their time limits.

**Hands-on exercise — `interview_prep/take-home-template/`**

1. Create the template and a README template with sections for
   assumptions, design, trade-offs, testing, and next steps.
2. Complete a 4-hour take-home: ingest paginated API data incrementally into
   PostgreSQL, deduplicate, model two tables, answer three SQL questions,
   with tests and a README.
3. Do three 45-minute live coding drills (dedupe latest record per key,
   sessionise events, incremental upsert) while recording yourself.
4. Present your take-home to a partner in 15 minutes and handle scaling
   questions.

**Checkpoint:**

- [ ] Deliver a clean, tested, well-documented take-home on time.
- [ ] Code small pipelines live while communicating clearly.
- [ ] Present and defend your solution.

**Common mistakes:** over-engineering beyond the time limit; no README or
tests; silent live coding; ignoring edge cases (nulls, duplicates, empty
input).

---

## 11. Phase F — The Practice System (Ongoing)

### Topic 19 — [Mock interview plans and self-review](19-mock-interview-plans-and-self-review.md)

**Why last:** Knowing the material is not the same as performing it. A
deliberate practice system — mocks, recordings, scoring, and an error log —
is what turns preparation into offers.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | A weekly practice plan: design cases, follow-up drills, behavioural stories, SQL/coding practice (from existing modules), and rest |
| Basics | Mock formats: solo recorded, peer mocks, mentor mocks, and paid or community mock platforms |
| Intermediate | **Self-review** with the rubric: scoring every mock, watching recordings for filler, silence, time management, and missed checklist items |
| Intermediate | The **error log**: recurring mistakes, their fixes, and tracking whether they recur |
| Intermediate | **Spaced repetition** of cases and numbers |
| Intermediate | Company-specific preparation: researching the company's products, data scale, stack, and engineering blog; adapting designs to their domain |
| Advanced | Being a good mock interviewer for peers (you learn as much from interviewing as from being interviewed) |
| Advanced | Final-week plan and interview-day checklist (environment, tools, energy, notes you may and may not use) |
| Advanced | Post-interview reflection and handling rejections constructively |

**How to learn it**

1. Read the topic file.
2. Create a 4-week practice calendar and follow it.
3. Track scores over time to see improvement.

**Hands-on exercise — `interview_prep/mocks/`**

1. Complete at least **six design mocks** (three with partners), **two
   follow-up-only mocks**, and **two behavioural mocks**; record and score
   each.
2. Maintain the error log and show at least three recurring mistakes
   eliminated.
3. Interview a peer at least twice using your rubric.
4. Prepare one company-specific brief (their likely data problems and how
   your designs adapt).

**Checkpoint:**

- [ ] Follow a practice plan with measurable improvement.
- [ ] Review mocks honestly with the rubric and error log.
- [ ] Prepare for a specific company and for interview day.

**Common mistakes:** only reading solutions; never practising aloud;
avoiding recordings; stopping practice once comfortable.

---

## 12. Consolidate — practice questions

When all topics are done, open
[`practice-questions.md`](practice-questions.md). It mixes short prompts
(requirements, estimation, trade-offs, follow-ups) and full design prompts
beyond the nine cases. For every question:

1. Set a timer appropriate to the prompt.
2. Answer aloud (and draw, for design prompts).
3. Score with your rubric.
4. Log mistakes and schedule a re-attempt.

---

## 13. Module mini-project — your interview portfolio

This mini-project is expanded in
[`../00-Gap-Modules-Overview/Projects/05-system-design-interview-portfolio.md`](../00-Gap-Modules-Overview/Projects/05-system-design-interview-portfolio.md).
The short version:

**Goal:** Build a complete, reusable interview portfolio that proves your
readiness and helps you prepare quickly for any company.

1. **Method sheets:** one-page framework, clarifying-question checklist,
   estimation templates and reference numbers, trade-off catalogue, and
   diagram conventions.
2. **Case portfolio:** written designs with clean diagrams for all nine
   cases, each with estimates, trade-offs, failure handling, follow-up
   answers, and links to the Stage 2 work that backs it up.
3. **Follow-up bank:** at least 40 follow-up questions with concise
   answers.
4. **Story bank:** 10–12 quantified behavioural stories mapped to themes.
5. **Take-home kit:** a template repository and one completed take-home with
   README and tests.
6. **Practice evidence:** mock recordings (or notes), rubric scores over
   time, and the error log showing improvement.
7. **Public artefact (optional):** one design write-up or case study from
   your Capstone published as a blog post or portfolio page (without any
   confidential information).

**Grading yourself:** you can design any of the nine cases in 45 minutes
with a rubric score of at least "strong" in every area; your scores improved
across mocks; each story has a measurable result; and a peer interviewer
would recommend you at your target level.

---

## 14. Module self-assessment — exit criteria

Tick every box without looking at your notes:

- [ ] I understand how data engineering interviews are run and scored.
- [ ] I clarify requirements and scope within about 5 minutes.
- [ ] I estimate volumes, sizes, and costs quickly and use them in
      decisions.
- [ ] I apply my design framework and cover cross-cutting concerns
      unprompted.
- [ ] I justify every choice with requirement-based trade-offs.
- [ ] I draw and communicate designs clearly and collaboratively.
- [ ] I can design all nine cases end to end in 45 minutes.
- [ ] I answer failure and deep-dive follow-ups with structure and numbers.
- [ ] I tell quantified behavioural stories for every common theme.
- [ ] I deliver strong take-homes and live coding sessions.
- [ ] I run a practice system and my mock scores have improved.
- [ ] I have completed the portfolio mini-project.

---

## 15. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| *Designing Data-Intensive Applications* — Martin Kleppmann (O'Reilly) | 04, 05, 16, all cases |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley (O'Reilly) | 04, 05, 07 |
| *System Design Interview* volumes 1 and 2 — Alex Xu (and co-author) — for general system design technique | 01–06 |
| *Streaming Systems* — Akidau, Chernyak, Lax (O'Reilly) | 08, 12, 13 |
| *The Data Warehouse Toolkit* — Kimball and Ross (Wiley) | 07, 12 |
| *Designing Machine Learning Systems* and *AI Engineering* — Chip Huyen (O'Reilly) | 10, 15 |
| Engineering blogs of data-heavy companies (e.g. architecture posts on analytics, streaming, and ML platforms) | All cases, company research |
| Google's *Site Reliability Engineering* (free online) — incident response and SLOs | 16 |
| Your own Stage 2 projects, ADRs, and post-mortems | All topics |

---

## 16. Where this module leads

| This module's outcome | What comes next |
| --- | --- |
| Interview readiness for data engineering roles | Applying for roles; company-specific preparation |
| Portfolio of designs and stories | Your résumé, portfolio site, and interview conversations |
| Design thinking for data platforms | Applied AI and Agentic AI stages, where the same method is used for AI systems |

Good system design interviews look like good engineering: understand the
problem, size it, choose deliberately, explain clearly, and plan for
failure. The habits you build here — ask before you build, put numbers on
everything, tie every choice to a requirement, narrate your thinking, and
practise until it is natural — will serve you long after the interviews,
every time you design a real data platform.
