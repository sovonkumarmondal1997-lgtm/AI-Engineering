# Roadmap — Module 2D.3: Data Architecture Patterns and Reference Architectures

This is the learning roadmap for the third module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Modules 2D.1 and 2D.2 gave you the role, the principles, and a disciplined way
to turn a business request into measurable requirements, constraints and
recorded decisions. This module gives you the **vocabulary of recurring
solutions**: the organising patterns that data architects reuse, and the
judgement to know when each one fits, when it does not, and how several can be
combined without creating a tangle.

> **Repository note.** The seven topic files, `practice-questions.md`, the
> module and project READMEs, and
> `Projects/03-reference-architecture-pattern-comparison.md` currently exist but
> are empty, as are the Stage 2D overview files. This roadmap is therefore the
> first written statement of the module's scope. It defines the learning
> sequence for each topic file; it does not claim that any topic file already
> contains this material. Where the roadmap and a topic file disagree once the
> topic file is written, the topic file's scope governs and this roadmap should
> be updated.
>
> **Directory name.** The prompt that requested this roadmap referred to
> `STAGE 2D - DATA ARCHITECURE/`. The actual directory is
> `Stage 2D — Data Architecture/`, and the actual name is preserved.
>
> **Illustrative values.** Every number, system and organisation in this roadmap
> is an **illustrative assumption** used to teach a method. None is a real
> requirement or a recommended target. Patterns are described at the
> architectural level; named technologies appear only as examples of a category.

---

## 1. Module overview

### 1.1 What this module covers

A **data architecture pattern** is a named, reusable solution structure for a
recurring problem in organising, moving, storing, sharing or governing data,
together with the conditions under which it works and the consequences of using
it. This module teaches seven families of such patterns, then how to choose and
combine them.

### 1.2 Terms that are often confused

| Term | Meaning in this module | Level of abstraction | Example (category only) |
| --- | --- | --- | --- |
| **Architecture pattern** | A reusable solution structure with context, forces and consequences | Concept | Lambda architecture; domain-oriented ownership |
| **Reference model** | An abstract set of concepts and relationships that gives a shared language | Highly abstract | A layered model of data capabilities |
| **Reference architecture** | A reusable, more concrete template for a class of problems, showing components, responsibilities and flows | Logical | A lakehouse reference architecture for analytics |
| **Implementation blueprint** | A concrete design for one organisation: components, boundaries, integration points, sizing, sequence | Specific, still technology-neutral or short-listed | Northbridge's target data platform design |
| **Technology implementation** | Actual products, configuration and code | Physical | A particular streaming engine and table format |

Moving down the table adds specifics and removes generality. A pattern is the
easiest to reuse; an implementation is the easiest to build and the hardest to
transfer.

### 1.3 Why architects use patterns

- They **compress experience:** the forces, failure modes and costs of a
  structure are known before you commit.
- They **provide shared language,** so reviewers can discuss a design quickly.
- They **reduce risk** by starting from structures with a known track record.
- They **make trade-offs explicit,** because each pattern is a bundle of
  advantages and costs.

### 1.4 Patterns address recurring problems

| Recurring problem | Patterns that address it (this module) |
| --- | --- |
| Who owns, governs and changes data across a large organisation? | Centralized, federated, domain-oriented (Topic 1); data mesh (Topic 4) |
| Where do analytical data live, and in what form? | Warehouse, lake, lakehouse (Topic 2) |
| How do historical accuracy and low latency coexist? | Lambda, Kappa (Topic 3) |
| How do consumers find, trust and use data they do not own? | Data products (Topic 4); data fabric (Topic 5) |
| How do we automate repeatable data management at scale? | Metadata-driven architecture (Topic 5) |
| How do systems and domains exchange data without tight coupling? | Event-driven and data-sharing patterns (Topic 6) |
| How do we choose and combine all of the above? | Selection and combination (Topic 7) |

### 1.5 Patterns are decision tools, not answers

> A pattern is a **hypothesis about fit**, not a certificate of quality.

A pattern that is right for one bank can be wrong for another with a different
size, regulatory exposure, skills or budget. The skill taught here is not
knowing patterns but **reasoning about fit**: stating the forces, checking them
against requirements and constraints from Module 2D.2, and accepting the costs
knowingly. Popularity, vendor marketing and fashion are not criteria.

### 1.6 How this module builds on earlier ones

| From | Used here |
| --- | --- |
| 2D.1 Topic 3: capabilities, domains, ownership | Foundation for centralized/federated/domain-oriented choices and data mesh |
| 2D.1 Topic 4: principles and quality attributes | The evaluation criteria for every pattern |
| 2D.1 Topic 5: lifecycle and governance | Governance model implied by each pattern |
| 2D.1 Topic 6: frameworks and reference models | Terminology of reference models and architectures |
| 2D.2 Topics 1–2: stakeholders, requirements | The problem statement for pattern selection |
| 2D.2 Topics 3–4: volume, freshness, availability | Workload facts that decide between patterns |
| 2D.2 Topic 5: constraints, assumptions, risks | Eliminates options and flags dependencies |
| 2D.2 Topics 6–7: trade-offs, ADRs | Method for comparing patterns and recording the choice |

### 1.7 How it supports later modules

| Later module | What it takes from this one |
| --- | --- |
| 2D.4 Conceptual, logical and physical modeling | Domain boundaries and data product scope shape model boundaries |
| 2D.5 Database and storage architecture | The analytical storage pattern decided here |
| 2D.6 Data integration and interoperability | Event-driven and data-sharing patterns |
| 2D.7 Enterprise data platform and lakehouse | The platform operating model and layered structure |
| 2D.8 Cloud, hybrid and multi-cloud | Patterns mapped to cloud services and constraints |
| 2D.9 Streaming and real-time | Lambda/Kappa and event-driven patterns in depth |
| 2D.10 Governance, security, privacy, compliance | Governance model per pattern; federated computational governance |
| 2D.11 Metadata, lineage, quality, master data | Metadata-driven architecture in depth |
| 2D.15 Documentation, reviews, operating model | Reference architectures and pattern ADRs as review inputs |

### 1.8 Expected capabilities after completion

You will be able to:

- Explain each pattern's problem, structure, responsibilities, data flow,
  strengths, limits and failure modes.
- State the organisational conditions that make each pattern viable.
- Map a business scenario's requirements and constraints to candidate patterns
  and eliminate unsuitable ones with reasons.
- Compare patterns on explicit, scenario-justified criteria.
- Combine patterns with a stated purpose, and recognise incompatibilities.
- Produce a defensible reference-architecture-level recommendation with
  rejected alternatives and conditions for revisiting.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

| Prerequisite | Why it matters here |
| --- | --- |
| Module 2D.1 completed (or its gates passed) | Pattern evaluation uses its principles, quality attributes, capability and domain concepts and governance vocabulary |
| Module 2D.2 completed (or its gates passed) | Pattern selection is meaningless without requirements, targets, constraints and a decision method; ADRs record the outcome |
| Stage 2–2C data engineering experience: batch pipelines, warehouse/lakehouse tables, streaming | You must picture how data actually flow to judge patterns; Stage 2C module 08 (data platform architecture) is directly relevant |
| Ability to read and draw logical architecture diagrams | Patterns are communicated as boxes, flows and boundaries |

### 2.2 Helpful prior knowledge

- Experience of a multi-team organisation, to appreciate ownership friction.
- Familiarity with SQL, columnar file formats and table formats.
- Awareness of message brokers and log-based streaming concepts.
- Basic knowledge of data governance terms (policy, classification, lineage).

### 2.3 Concepts you will learn during this module

- Operating-model vocabulary: platform team, domain team, federated governance.
- Layered/zone organisation of analytical data.
- Batch/stream processing paths and reconciliation.
- Data product interfaces and contracts.
- Metadata types and active metadata.
- Event, command and state-transfer messaging.

### 2.4 Using prior knowledge when comparing patterns

For every comparison, work through this order. It prevents choosing a pattern
first and finding reasons afterwards.

1. **Problem:** restate the business problem (2D.2 Topic 1).
2. **Requirements and targets:** list the architecturally significant ones
   (2D.2 Topics 2–4).
3. **Constraints and risks:** identify gates that remove options (2D.2 Topic 5).
4. **Principles and quality attributes:** the criteria and their priority
   (2D.1 Topic 4).
5. **Candidates:** only then list patterns.
6. **Compare, decide, record** (2D.2 Topics 6–7).

---

## 3. Learning strategy and progression

### 3.1 The four levels

| Level | Concepts to study | Recommended order | Questions to answer | Exercises | Practical outputs | Evidence of mastery | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1 — Beginner** | Terminology, purpose, main components, basic flows, typical uses | Definition → problem solved → components → one example flow → one use case | What problem does this pattern solve? What are its parts? | Draw the pattern from memory; label components and flows | Annotated one-page diagram per pattern | Correct unaided explanation | You describe each pattern accurately and distinguish it from its nearest neighbour |
| **2 — Intermediate** | Structures, operating models, comparison, scenario mapping | Compare pairs → map to scenarios → identify ownership and governance model | How does ownership differ? Which workload fits? Who does what? | Comparison tables; map five scenarios to patterns | Pairwise comparisons; scenario-to-pattern map | Correct reasoning on described scenarios | You choose and justify a pattern for a given scenario, naming the conditions that make it fit |
| **3 — Advanced** | Trade-offs, failure modes, organisational implications, operational complexity, cost, constraints | Failure modes → organisational prerequisites → cost and complexity → constraints | What breaks? What does this demand of the organisation? What does it cost to run? | Failure-mode analysis; organisational readiness review; sensitivity test | Trade-off analysis with failure modes and readiness assessment | A defended trade-off analysis that survives challenge | You identify which pattern is the wrong choice for a scenario and why |
| **4 — Industry application** | Selection and combination for an enterprise; explicit criteria; documented alternatives | Requirements → candidates → matrix → combination → recommendation → ADR | Which pattern or combination, under what assumptions, and what would change it? | The project (Section 7) | Reference architecture recommendation with rationale | Reviewer can audit and reproduce the reasoning | Project completion gate (Section 7.7) is met |

### 3.2 What "advanced" means here

Advanced does **not** mean knowing more pattern names. It means being able to
say, for a specific organisation: this pattern fails **here**, it demands
**this** of the organisation, it costs **this** to operate, it conflicts with
**that** constraint, and I would choose differently if **this** assumption
changed.

### 3.3 The pattern study loop (use for every topic)

```text
Name the problem → Describe the structure → Draw the flow → List the forces
→ State the organisational prerequisites → List failure modes → Find the
neighbour and the difference → Test against a scenario → Record the verdict
```

1. **Name the problem** the pattern was created to solve.
2. **Describe the structure:** components and responsibilities.
3. **Draw the flow:** data in, data out, who owns each step.
4. **List the forces:** quality attributes the pattern improves and those it
   costs.
5. **State organisational prerequisites:** skills, roles, funding model.
6. **List failure modes:** how it commonly goes wrong.
7. **Find the neighbour:** the nearest alternative and the difference.
8. **Test against a scenario** from Section 7.2.
9. **Record a verdict:** when I would use it, when I would not.

### 3.4 Suggested schedule

About **4 weeks at 6–8 hours per week.**

| Week | Work |
| --- | --- |
| 1 | Topic 1 (centralized / federated / domain-oriented) · Topic 2 (warehouse / lake / lakehouse) |
| 2 | Topic 3 (Lambda / Kappa) · Topic 4 (data mesh and data products) |
| 3 | Topic 5 (data fabric and metadata-driven) · Topic 6 (event-driven and data sharing) |
| 4 | Topic 7 (selecting and combining) · practice questions · project |

Keep a `module-2d3-notes.md` outside the repository's topic files: one
"pattern card" per pattern (problem, structure, forces, prerequisites, failure
modes, verdict) and open questions. The project uses these cards.

---

## 4. Detailed learning roadmap for each topic file

Each module below uses the same twelve sub-headings. Levels are cumulative.
Examples use the **illustrative** scenario of *Northbridge Bank*, a fictional
mid-sized bank (Section 7.2).

---

### Module 1 — [Centralized, federated and domain-oriented architectures](01-centralized-federated-and-domain-oriented-architectures.md)

#### 1.1 Learning objectives

- Define centralized, federated and domain-oriented architectures.
- Describe how each distributes responsibility and decision authority.
- Explain how ownership, stewardship, governance and standards work across
  organisational boundaries in each.
- Explain cross-domain integration and interoperability under each.
- State benefits, limitations, organisational prerequisites and failure modes.
- Explain how size, maturity, autonomy needs and regulation influence the
  choice, and describe hybrid approaches.

#### 1.2 Why the topic matters in real-world Data Architecture

Before choosing technology you must decide **who is responsible for what**.
Many data programmes fail because the technical design assumed an operating
model the organisation did not have: a central team becomes a bottleneck, or
autonomous domains diverge into incompatible data.

#### 1.3 Prerequisite knowledge

2D.1 Topic 3 (capabilities, domains, ownership); 2D.1 Topic 5 (governance and
decision rights); 2D.2 Topic 5 (organisational constraints).

#### 1.4 Beginner-level learning sequence

1. **Define the three patterns in one sentence each:**
   - *Centralized:* one team and platform own and operate data for the whole
     organisation.
   - *Federated:* a central body sets shared standards and capabilities while
     business units retain defined responsibilities.
   - *Domain-oriented:* business domains own their data and are accountable for
     its quality and availability, supported by shared platform capabilities.
2. **Draw each** as boxes: where does ingestion, modelling, quality, access
   control and consumption sit?
3. **List responsibilities** in a table (decide standards, build pipelines,
   fix quality, grant access, define meaning).
4. **Questions to answer:** Who is called when data are wrong in each model?
   Where is the single point of coordination?
5. **Exercise:** Label an unsigned organisation diagram with the model it
   represents and justify.

**Ability to demonstrate:** describe each model and sketch its responsibility
split without notes.

#### 1.5 Intermediate-level learning sequence

1. **Compare along six dimensions:** decision authority, ownership,
   stewardship, governance, integration burden, operational responsibility.
2. **Study standards across boundaries:** what must be common (identifiers,
   classification, security, interface conventions) and what may vary.
3. **Study cross-domain integration:** how a consumer in one domain obtains
   data from another in each model; where agreements live.
4. **Map each model to benefits and limits:**

   | Model | Typical benefits | Typical limits |
   | --- | --- | --- |
   | Centralized | Consistency, control, economies of scale, simpler governance | Bottleneck, distance from business meaning, slower change |
   | Federated | Balance of standards and local flexibility | Coordination overhead, ambiguous accountability |
   | Domain-oriented | Business proximity, scalable ownership, faster domain change | Needs domain capability, risk of inconsistency, duplicated effort |

5. **Map to scenarios:** which model suits a small firm, a regulated group, a
   fast-growing multi-product company?
6. **Questions to answer:** What would you centralise even in a
   domain-oriented model? What would you devolve in a centralised one?
7. **Exercise:** Describe the ownership and governance model for customer,
   transaction and risk data under each pattern for Northbridge.

**Ability to demonstrate:** a comparison of the three on responsibilities,
governance and integration for a described organisation.

#### 1.6 Advanced-level learning sequence

1. **Trade-offs:** autonomy versus standardisation; speed versus consistency;
   local optimisation versus enterprise optimisation.
2. **Organisational prerequisites:** skills in domains, product thinking,
   platform capability, funding model, decision rights, escalation.
3. **Failure modes:**
   - *Centralised:* queue of requests, culture of "the data team's problem".
   - *Federated:* committee paralysis; standards nobody enforces.
   - *Domain-oriented:* domains lacking skills; duplicated pipelines; unmanaged
     cross-domain dependencies; "ownership" assigned but not resourced.
4. **Influence of context:** size (small organisations seldom justify many
   domain teams), maturity, regulation (some obligations require central
   control or evidence), geography, acquisitions.
5. **Hybrids:** central core data (identity, reference, security) with
   domain-owned analytical data; central platform with domain-owned products;
   differing models for different data classes.
6. **Transition risk:** moving between models, interim states, and the cost of
   a wrong switch.
7. **Questions to answer:** What evidence would show the current model is
   failing? Which responsibilities should never be devolved?
8. **Exercise:** Review a described organisation, identify the model in use,
   find two mismatches between model and context, and propose a hybrid.

**Ability to demonstrate:** a justified model recommendation that names the
organisational conditions required and the failure modes to watch.

#### 1.7 Industry-application exercises

- Recommend an ownership and governance model for Northbridge and justify it
  against its size, regulation and skills.
- Draw a responsibility matrix (RACI-style) for ten data activities under your
  recommended model.
- Define the three standards that must stay central.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* A central team has a six-week backlog; domains are building
   shadow pipelines. Diagnose and propose changes.
2. *Scenario:* After a merger, two units each own a customer dataset. Which
   model, and how do you reach a decision?
3. *Scenario:* A regulator requires one accountable function for sensitive
   customer data. How does that constrain domain ownership?

#### 1.9 Expected outputs and deliverables

- Pattern card for each of the three models.
- Responsibility matrix for the recommended model.
- Hybrid recommendation with justification.
- Answers to Topic 1 practice questions.

#### 1.10 Common mistakes and misconceptions

- Equating a model with a technology.
- Believing domain-oriented means "no central governance".
- Declaring domains owners without resourcing them.
- Assuming centralised is always safer or always slower.
- Ignoring the organisation's actual skills and funding model.

#### 1.11 Mastery criteria

- Explains each model's responsibility split and governance accurately.
- States the organisational conditions that make each viable.
- Identifies failure modes and recommends a justified hybrid where appropriate.

#### 1.12 Completion gate

- [ ] Three pattern cards and the responsibility matrix reviewed.
- [ ] Recommendation names organisational prerequisites and failure modes.
- [ ] Topic 1 practice questions answered and corrected.

---

### Module 2 — [Data warehouse, data lake and lakehouse patterns](02-data-warehouse-data-lake-and-lakehouse-patterns.md)

#### 2.1 Learning objectives

- Explain the purpose and characteristics of warehouses, lakes and lakehouses.
- Relate each to structured, semi-structured and unstructured data.
- Explain schema-on-write and schema-on-read.
- Explain storage and compute responsibilities and data layering.
- Assess quality, governance, security, metadata and lifecycle implications.
- Match patterns to workloads and justify using one or combining several.

#### 2.2 Why the topic matters in real-world Data Architecture

The analytical data architecture decides cost, flexibility, trust and speed of
analysis for years. Poor choices produce either an expensive, rigid store or an
ungoverned "data swamp".

#### 2.3 Prerequisite knowledge

Stage 2 and 2C warehouse/lakehouse experience; 2D.2 Topics 3–4 (volume,
variety, freshness); Module 1 here (who owns the stores).

#### 2.4 Beginner-level learning sequence

1. **Define each pattern:**
   - *Warehouse:* integrated, modelled, governed structured data optimised for
     analytical queries; typically schema-on-write.
   - *Lake:* low-cost storage of raw data in many formats; typically
     schema-on-read.
   - *Lakehouse:* combines lake storage with warehouse-like management features
     (transactions, schema enforcement, performance structures).
2. **Define schema-on-write and schema-on-read** and where each puts the
   modelling effort and the risk.
3. **Learn the data categories:** structured, semi-structured, unstructured.
4. **Learn the layered organisation:** raw/landing → cleaned/standardised →
   curated/consumption (names vary; keep to a neutral naming).
5. **Questions to answer:** Why can a lake become a swamp? What does a
   lakehouse add that a plain lake lacks?
6. **Exercise:** Draw each pattern with its storage, compute, layers and
   consumers.

**Ability to demonstrate:** define the three and place a described dataset in
each.

#### 2.5 Intermediate-level learning sequence

1. **Separate storage from compute** and explain why independent scaling
   matters for cost.
2. **Compare on consumption:** reporting and BI, ad hoc analysis, data science
   and machine learning, regulatory reporting, operational analytics.
3. **Compare on data type:** tabular transactions, logs and events, documents,
   images.
4. **Compare on quality and governance:** where validation occurs, how lineage
   and access control are applied, how metadata is held.
5. **Compare on lifecycle:** retention, archival, deletion, reproducibility.
6. **Map workloads to patterns** with a short table, noting that the map
   depends on the requirements (freshness, concurrency, volume).
7. **Questions to answer:** Which workload would you not put on a plain lake?
   Which data would you not force into a rigid warehouse model?
8. **Exercise:** For five Northbridge workloads (regulatory reporting, fraud
   model training, executive dashboard, document archive search, marketing
   segmentation), propose a storage pattern and justify.

**Ability to demonstrate:** workload-to-pattern mapping with reasons and stated
requirement dependencies.

#### 2.6 Advanced-level learning sequence

1. **Trade-offs:** cost versus performance; flexibility versus consistency;
   openness versus integrated governance; time to ingest versus time to trust.
2. **Operational complexity:** skills, maintenance of table formats and
   metadata, small-file and compaction issues, concurrency control, cost
   management.
3. **Governance and security:** fine-grained access, masking, auditing,
   residency, deletion obligations across layers and copies.
4. **Failure modes:** duplicate truths across warehouse and lake; ungoverned
   zones; uncontrolled copies; pipeline sprawl; tool-driven rather than
   requirement-driven decisions.
5. **Combinations:** lake as landing zone feeding a warehouse; lakehouse
   consolidating both; a warehouse retained for specific governed workloads.
   State the purpose of each combination and the duplication cost.
6. **Migration considerations:** moving between patterns, coexistence periods,
   consistency of definitions.
7. **Avoid universal claims:** no pattern is superior in all conditions;
   explicitly state when each wins.
8. **Questions to answer:** When is a pure warehouse the right answer? When is
   a lakehouse a poor choice?
9. **Exercise:** Evaluate three analytical architecture options for a scenario
   with a decision matrix, risks and a migration note.

**Ability to demonstrate:** a justified choice or combination with cost,
governance and complexity consequences stated.

#### 2.7 Industry-application exercises

- Select and justify an analytical data architecture for Northbridge across its
  workloads, including what is **not** moved.
- Define zone/layer responsibilities and who owns each.
- List the governance controls required at each layer for sensitive customer
  data.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* A lake holds ten years of raw data; analysts distrust it. Which
   forces explain this and what changes?
2. *Scenario:* The finance team needs fully reconciled, auditable monthly
   figures. Which pattern characteristics matter most?
3. *Scenario:* A fraud team needs both historical training data and fresh
   features. How do you reason about storage choices without choosing a
   product?

#### 2.9 Expected outputs and deliverables

- Pattern cards for warehouse, lake and lakehouse.
- Workload-to-pattern map.
- Option comparison with governance and complexity notes.
- Answers to Topic 2 practice questions.

#### 2.10 Common mistakes and misconceptions

- Treating a lake as a warehouse replacement or a lakehouse as a product.
- Assuming schema-on-read removes the need for modelling.
- Ignoring deletion and retention obligations across copies.
- Choosing by vendor claim.
- Forgetting that storage choices carry ownership implications (Module 1).

#### 2.11 Mastery criteria

- Distinguishes the three patterns by structure and purpose.
- Maps workloads to patterns with reasons and acknowledges dependencies.
- Evaluates governance, complexity and cost trade-offs.

#### 2.12 Completion gate

- [ ] Pattern cards and workload map complete.
- [ ] Option comparison contains no "universally best" claim.
- [ ] Topic 2 practice questions answered and corrected.

---

### Module 3 — [Lambda and Kappa architectures](03-lambda-and-kappa-architectures.md)

#### 3.1 Learning objectives

- Explain the problem Lambda and Kappa address.
- Describe batch and stream processing responsibilities and processing paths.
- Compare their implementation and operating models.
- Analyse consistency, reconciliation, reprocessing and replay.
- Assess complexity, duplicated logic, latency, throughput, correctness and
  cost.
- Decide when either, or a simpler alternative, is appropriate.

#### 3.2 Why the topic matters in real-world Data Architecture

Many requirements combine "fresh now" with "correct over history". These
patterns are two classic answers. They are also frequently over-applied: many
workloads need neither.

#### 3.3 Prerequisite knowledge

2D.2 Topic 4 (freshness, latency, throughput targets); Stage 2B streaming
topics; Module 2 here (storage patterns).

#### 3.4 Beginner-level learning sequence

1. **Define batch processing** (bounded data, scheduled, high completeness) and
   **stream processing** (unbounded data, continuous, low latency).
2. **Define Lambda:** a batch layer computes accurate views from the full
   history; a speed layer provides low-latency views of recent data; a serving
   layer merges them for queries.
3. **Define Kappa:** a single stream-processing path over a durable, replayable
   log; reprocessing is done by replaying the log through new logic.
4. **Draw both** data flows.
5. **Questions to answer:** Where does historical correction happen in each?
   What is the "same logic twice" problem?
6. **Exercise:** Label a diagram of each architecture with its paths and the
   place where the answer to a query is assembled.

**Ability to demonstrate:** explain the structure and flow of both.

#### 3.5 Intermediate-level learning sequence

1. **Compare responsibilities:** which path produces which result; which is the
   source of truth.
2. **Compare operating models:** number of codebases, skills, deployment,
   monitoring.
3. **Study consistency:** how batch and speed views may disagree and how they
   are reconciled or superseded.
4. **Study reprocessing and replay:** what is needed (retained log or raw
   store, deterministic logic, versioned code) and what it costs.
5. **Link to requirements:** use freshness targets (2D.2 Topic 4) to decide
   whether seconds, minutes or hours matter.
6. **Consider alternatives:** frequent micro-batch; incremental batch; change
   data capture with a single pipeline; stream plus periodic recomputation.
7. **Questions to answer:** Is "real-time" actually required? Which alternative
   might satisfy the target with less complexity?
8. **Exercise:** For four Northbridge workloads, state the freshness target and
   say whether Lambda, Kappa or a simpler pattern fits.

**Ability to demonstrate:** a table comparing the two on flow, consistency,
reprocessing and operations, plus a simpler-alternative check.

#### 3.6 Advanced-level learning sequence

1. **State and correctness:** exactly-once effects versus at-least-once with
   idempotence; late and out-of-order events; event time versus processing
   time; windowing implications for correctness.
2. **Duplicated logic:** the Lambda burden of maintaining two implementations
   that must agree; strategies to limit it and the residual risk.
3. **Failure recovery:** what happens on a faulty deployment, a lost partition,
   a long outage; how long recovery or replay takes (estimate it with volume
   and rate from 2D.2 Topic 3).

   ```text
   replay_time ≈ retained_volume / sustained_replay_throughput
   ```

   *Illustrative:* 30 TB of retained events at 500 MB/s sustained ≈ 60,000 s
   ≈ 16.7 hours (decimal units). Compare with the recovery target.
4. **Retention of the log:** the log must hold enough history for the replay
   needs, or reprocessing returns to a raw store, blurring the pattern boundary.
5. **Cost and complexity:** compute duplication, storage of history twice,
   operational skill demands.
6. **Governance:** deletion and correction obligations when data exist in a
   log, in batch outputs and in serving views.
7. **Failure modes:** diverging results, unbounded state, "temporary" speed
   layer that becomes permanent, replay that cannot finish within the recovery
   target.
8. **Questions to answer:** What would convince you to keep Lambda rather than
   move to Kappa? Which requirement makes a simple batch design sufficient?
9. **Exercise:** Perform a failure-mode and replay-time analysis for a chosen
   design and compare it with stated recovery targets.

**Ability to demonstrate:** an analysis that quantifies reprocessing effort,
identifies correctness risks and states when a simpler design suffices.

#### 3.7 Industry-application exercises

- Recommend an approach for card-transaction analytics with stated freshness,
  replay and history requirements (all illustrative).
- Write the reconciliation rule between fast and accurate results, including
  who owns the number a regulator sees.
- Estimate replay time for a stated retention and throughput; state your
  assumptions.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* A dashboard needs data within ten minutes, with full accuracy
   by next morning. Which designs satisfy it and which is simplest?
2. *Scenario:* A bug in transformation logic has corrupted three weeks of
   output. Compare recovery under Lambda and under Kappa.
3. *Scenario:* A team proposes Kappa because "everything is a stream", but its
   sources deliver only nightly files. What do you ask?

#### 3.9 Expected outputs and deliverables

- Pattern cards for Lambda and Kappa.
- Comparison table with simpler alternatives.
- Failure-mode and replay-time analysis.
- Answers to Topic 3 practice questions.

#### 3.10 Common mistakes and misconceptions

- Assuming any real-time need implies Lambda or Kappa.
- Believing Kappa removes all batch concerns.
- Underestimating the cost of keeping two code paths correct.
- Ignoring replay duration and log retention.
- Forgetting that correction and deletion must reach every copy.

#### 3.11 Mastery criteria

- Explains both architectures and their trade-offs precisely.
- Quantifies reprocessing effort and checks it against targets.
- Recognises when a simpler pattern is appropriate.

#### 3.12 Completion gate

- [ ] Pattern cards, comparison and replay analysis complete.
- [ ] At least one scenario concludes that neither pattern is required, with
      reasons.
- [ ] Topic 3 practice questions answered and corrected.

---

### Module 4 — [Data mesh principles and domain data products](04-data-mesh-principles-and-domain-data-products.md)

#### 4.1 Learning objectives

- Explain the motivation and the four data mesh principles.
- Define domain ownership, data as a product, self-serve platform and federated
  computational governance.
- Define a data product's responsibilities, interfaces, discoverability,
  quality and service expectations.
- Explain cross-domain consumption and interoperability.
- Assess organisational and operating-model prerequisites, adoption challenges
  and the difference between adopting principles and reorganising teams.

#### 4.2 Why the topic matters in real-world Data Architecture

Data mesh is widely discussed and frequently misunderstood. A data architect
must be able to separate its genuine ideas (ownership, product thinking,
platform enablement, computational governance) from slogans, and judge whether
the organisation can support it.

#### 4.3 Prerequisite knowledge

Module 1 here (domain-oriented architecture); 2D.1 Topic 3 (domains and
ownership); Stage 2C module 08 (data mesh and data products).

#### 4.4 Beginner-level learning sequence

1. **Learn the motivation:** central teams do not scale with the number of data
   sources and consumers; knowledge sits in the domains.
2. **Learn the four principles:**
   1. *Domain-oriented ownership* of analytical data.
   2. *Data as a product,* with a consumer-focused owner.
   3. *Self-serve data platform* that lowers the cost of building products.
   4. *Federated computational governance:* global rules enforced through
      automation, decided by a federation of domain and platform
      representatives.
3. **Define a data product:** data plus the code, metadata, interfaces and
   service commitments needed for others to use it.
4. **Questions to answer:** Why is a table not a data product? Is data mesh a
   product you can buy?
5. **Exercise:** Describe one data product (customer profile) in terms of
   owner, consumers, interface, quality and service expectation.

**Ability to demonstrate:** state the four principles and define a data
product.

#### 4.5 Intermediate-level learning sequence

1. **Apply to domain boundaries** (2D.1 Topic 3): which Northbridge domains
   would own which products; where boundaries overlap.
2. **Define product responsibilities:** owner, documentation, schema and
   contract, quality metrics, service levels, versioning, support.
3. **Study interfaces and discoverability:** how consumers find, understand and
   request access; the minimum metadata a product must publish.
4. **Study cross-domain consumption:** consumer-driven requirements, contracts,
   change notification, deprecation.
5. **Study interoperability:** global identifiers and shared semantics so
   products from different domains can be combined.
6. **Link to service expectations:** express product SLOs using 2D.2 Topic 4
   methods (freshness, availability, quality).
7. **Questions to answer:** Who is accountable when a consumed product is
   late? What are the global standards every product must meet?
8. **Exercise:** Specify three Northbridge data products with owner, interface,
   quality and service targets (illustrative) and one cross-domain dependency.

**Ability to demonstrate:** a data product specification and a cross-domain
consumption agreement.

#### 4.6 Advanced-level learning sequence

1. **Operating-model change:** product-owner roles in domains, funding model,
   platform team as an enabler, decision rights, incentives.
2. **Federated computational governance:** what is decided globally (security,
   classification, interoperability), what locally, and how policies become
   automated checks rather than manual reviews.
3. **Platform capabilities required:** product templates, access control,
   catalog registration, quality checks, lineage, cost transparency.
4. **Accountability and adoption risks:** unclear ownership, domains without
   skills, platform immaturity, inconsistent semantics, duplicated effort,
   governance either too heavy or absent, "mesh-washing" (renaming teams and
   tools).
5. **Readiness assessment:** score the organisation on domain maturity,
   platform maturity, governance capability, leadership support and skills;
   decide a partial adoption (a few products) versus full adoption.
6. **Contrast with reorganisation alone:** distinguish moving people into
   domains from changing responsibility, accountability, platform and
   governance.
7. **Questions to answer:** For which Northbridge data would you not use a
   product model? What would make you stop the programme?
8. **Exercise:** Conduct a readiness assessment for a described organisation
   and recommend a bounded pilot with exit criteria.

**Ability to demonstrate:** a readiness assessment and a pilot recommendation
with explicit adoption risks.

#### 4.7 Industry-application exercises

- Design a conceptual domain data product model for Northbridge: domains,
  products, owners, interfaces, governance and service expectations.
- Define the global policies that would be automated and those requiring human
  decision.
- Write the pilot scope and its success and stop criteria.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* A bank renames its data team "platform" and its analysts
   "domain data owners" without changing funding or accountability. Evaluate.
2. *Scenario:* A product's schema changes and breaks three consumers. What
   mechanisms should have prevented this?
3. *Scenario:* Two domains both claim to own "customer". Use the Module 1 and
   2D.1 ownership methods to resolve it.

#### 4.9 Expected outputs and deliverables

- Pattern card for data mesh.
- Data product specifications.
- Readiness assessment and pilot recommendation.
- Answers to Topic 4 practice questions.

#### 4.10 Common mistakes and misconceptions

- Treating data mesh as a technology or vendor product.
- Assuming it suits every organisation.
- Declaring products without owners, contracts or service levels.
- Removing central governance instead of federating and automating it.
- Equating reorganising teams with adopting the principles.

#### 4.11 Mastery criteria

- Explains the four principles accurately and critically.
- Specifies data products with owners, interfaces and service expectations.
- Assesses readiness and identifies adoption risks.

#### 4.12 Completion gate

- [ ] Product specifications, readiness assessment and pilot plan reviewed.
- [ ] Assessment explicitly considers cases where mesh is unsuitable.
- [ ] Topic 4 practice questions answered and corrected.

---

### Module 5 — [Data fabric and metadata-driven architecture](05-data-fabric-and-metadata-driven-architecture.md)

#### 5.1 Learning objectives

- Explain the purpose of data fabric and metadata-driven architecture.
- Explain the roles of metadata in discovery, integration, governance and
  automation.
- Describe catalogs, lineage, semantic relationships and policy enforcement.
- Describe logical access and integration across distributed environments.
- Assess governance, security, metadata quality and automation limits.
- Distinguish data fabric from data mesh and from traditional integration.

#### 5.2 Why the topic matters in real-world Data Architecture

Data live in many places. Moving everything is expensive and slow. Metadata,
if accurate and active, can make distributed data discoverable, governable and
partly automatable. It can also become another unmaintained inventory.

#### 5.3 Prerequisite knowledge

Modules 1–4 here; 2D.1 Topic 5 (governance); Stage 2C module 08 (metadata-driven
design).

#### 5.4 Beginner-level learning sequence

1. **Define metadata** and its categories: business (meaning, owner), technical
   (schema, location, format), operational (run history, freshness, usage),
   and security/classification.
2. **Define a data fabric:** an architectural approach that uses metadata and
   automation to connect, discover and govern data across distributed sources.
3. **Define metadata-driven architecture:** system behaviour (pipelines,
   access rules, quality checks) driven by metadata and configuration rather
   than hard-coded.
4. **Learn the components:** catalog, lineage, glossary, policy engine,
   integration and access layer.
5. **Questions to answer:** What can metadata automate? What can it never
   supply on its own (for example business meaning that nobody has defined)?
6. **Exercise:** Draw a fabric with sources, a metadata layer and consumers.

**Ability to demonstrate:** define the terms and name the components.

#### 5.5 Intermediate-level learning sequence

1. **Discovery:** how a catalog helps a consumer find and trust data; what
   metadata must be present for that.
2. **Integration:** metadata-driven pipeline generation; schema mapping; logical
   (virtual) access to data left in place versus physical movement.
3. **Governance:** classification propagating through lineage; policies
   attached to classification; audit evidence.
4. **Automation:** repeatable tasks that metadata can drive: onboarding,
   quality rules, access provisioning, documentation.
5. **Semantics:** relationships and shared definitions (glossary, ontology,
   knowledge graph where relevant) at the concept level.
6. **Compare with neighbours:**

   | Concept | Primary concern | Operating model emphasis |
   | --- | --- | --- |
   | Data fabric | Connecting and governing distributed data through metadata and automation | Technology-led, centrally enabled |
   | Data mesh | Ownership and product accountability in domains | Organisation-led, federated |
   | Traditional integration | Moving and transforming data between known systems | Project-led, point solutions |

   They are not mutually exclusive: a mesh can use fabric capabilities.
7. **Questions to answer:** What happens to automation when metadata are wrong
   or missing? Which of the three addresses ownership?
8. **Exercise:** For Northbridge, list which metadata would drive discovery,
   which would drive policy, and which would drive pipeline generation.

**Ability to demonstrate:** explain how metadata supports each function and
distinguish fabric from mesh and integration.

#### 5.6 Advanced-level learning sequence

1. **Metadata quality:** completeness, accuracy, timeliness, ownership of
   metadata; how stale metadata produce wrong decisions at scale.
2. **Interoperability:** metadata standards and exchange across tools;
   consequences of tool-specific metadata stores.
3. **Automation boundaries:** what to automate, what to review; human-in-the-
   loop for classification and policy exceptions; confidence of automated
   inference.
4. **Policy consistency:** the same policy applied across heterogeneous
   systems; enforcement points; drift; evidence.
5. **Implementation complexity:** connector coverage, scanning cost, lineage
   gaps (especially for code-heavy or manual flows), performance of logical
   access, dependency on a central metadata platform.
6. **Security implications:** metadata can itself be sensitive; access to the
   catalog; lineage revealing structure.
7. **Failure modes:** "catalog as a museum", over-reliance on automated
   classification, virtual access that cannot meet latency targets, lock-in to
   a metadata store.
8. **Questions to answer:** Which governance problem would a fabric not solve
   for Northbridge? Where would you refuse virtual access and copy data
   instead?
9. **Exercise:** Assess a proposed fabric design for dependencies and
   limitations and list what must already be true for it to work.

**Ability to demonstrate:** identify dependencies and limits of a proposed
metadata-driven design.

#### 5.7 Industry-application exercises

- Propose a conceptual metadata-driven architecture for Northbridge's lineage
  and accountability problem; state dependencies and limitations.
- Define the minimum metadata every data asset must carry.
- List what would remain manual and why.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* A vendor promises "automatic governance" through a fabric.
   Which questions do you ask?
2. *Scenario:* The catalog reports lineage for 60% of flows; the rest are
   spreadsheets and ad hoc scripts. What follows?
3. *Scenario:* Analysts query a remote system through a virtual layer and
   overload it. What does this tell you about logical access?

#### 5.9 Expected outputs and deliverables

- Pattern card for data fabric / metadata-driven architecture.
- Comparison with mesh and traditional integration.
- Conceptual design with dependencies and limitations.
- Answers to Topic 5 practice questions.

#### 5.10 Common mistakes and misconceptions

- Believing a fabric solves data quality, integration or governance
  automatically.
- Treating a catalog as the same as ownership.
- Assuming metadata are accurate because a tool collects them.
- Treating fabric and mesh as competitors.
- Ignoring that metadata also need an owner and quality targets.

#### 5.11 Mastery criteria

- Explains how metadata supports discovery, integration, governance and
  automation.
- Distinguishes fabric from mesh and from traditional integration.
- Identifies dependencies, quality risks and automation limits.

#### 5.12 Completion gate

- [ ] Pattern card, comparison and conceptual design reviewed.
- [ ] Design states at least three things that must already be true.
- [ ] Topic 5 practice questions answered and corrected.

---

### Module 6 — [Event-driven and data-sharing patterns](06-event-driven-and-data-sharing-patterns.md)

#### 6.1 Learning objectives

- Explain event-driven architecture and the purpose of events.
- Describe producers, consumers and boundaries.
- Compare event-based and request-based integration.
- Explain event contracts, schema compatibility and asynchronous communication.
- Describe data-sharing patterns and consumer access needs.
- Evaluate delivery, ordering, duplication, replay and failure behaviour.
- Assess access control, privacy, ownership, coupling, consistency and
  operational trade-offs, and choose among integration approaches.

#### 6.2 Why the topic matters in real-world Data Architecture

How systems and domains exchange data determines coupling, freshness, resilience
and accountability. Poor choices create brittle point-to-point dependencies or
unmanaged data copies. This module stays at the pattern level; product-specific
streaming engineering belongs to later modules (2D.6 and 2D.9).

#### 6.3 Prerequisite knowledge

Modules 1, 3 and 4 here; 2D.2 Topics 3–5 (volume, targets, dependencies).

#### 6.4 Beginner-level learning sequence

1. **Define an event:** a record that something happened, with a timestamp and
   identity, usually immutable.
2. **Define the roles:** producer (emits), broker/channel (transports and
   retains), consumer (reacts).
3. **Distinguish messages:** *event* (fact: "payment posted"), *command*
   (request: "post payment"), *state transfer* (current record), *change event*
   (a change to a record).
4. **Learn temporal decoupling:** producer and consumer need not be available
   at the same time.
5. **Learn basic data-sharing approaches:** file or batch export; API/query
   access; shared database access (and why it is risky); event publication;
   managed data sharing.
6. **Questions to answer:** What does a producer know about its consumers in an
   event model? Why does sharing a database create hidden coupling?
7. **Exercise:** Diagram a payment-posted event with one producer and three
   consumers.

**Ability to demonstrate:** define events and distinguish them from commands
and state transfer.

#### 6.5 Intermediate-level learning sequence

1. **Compare request-based and event-based integration** on coupling, latency,
   failure behaviour, consistency and debuggability.
2. **Study event contracts:** schema, semantics, versioning, ownership of the
   contract (the producer), and consumer expectations.
3. **Study schema compatibility:** backward, forward and full compatibility at
   a conceptual level; additive versus breaking changes.
4. **Study data-sharing patterns** and consumer access needs: pull versus push,
   batch versus continuous, full versus incremental, curated versus raw.
5. **Study ownership:** who publishes, who may consume, who is notified of
   change.
6. **Compare approaches:**

   | Approach | Coupling | Freshness | Typical fit | Typical risk |
   | --- | --- | --- | --- | --- |
   | Event publication | Low (contract) | Seconds–minutes | Many consumers reacting to changes | Contract drift; replay and ordering concerns |
   | API / query on source | Higher (runtime) | Immediate | Few consumers needing current state | Load on source; availability coupling |
   | Batch / file export | Low runtime, high latency | Hours–days | Bulk, scheduled analytics | Stale data; manual handling |
   | Shared database | Very high (schema) | Immediate | Rarely justified | Hidden coupling; uncontrolled change |
   | Managed data sharing / product interface | Contract-based | Per product | Cross-domain analytical consumption | Needs governance and platform support |

7. **Questions to answer:** Which consumers would break if a field changes?
   Who is informed?
8. **Exercise:** For five Northbridge integrations, choose an approach, state
   the contract owner and justify.

**Ability to demonstrate:** a justified choice of integration approach per
scenario, with contract ownership.

#### 6.6 Advanced-level learning sequence

1. **Delivery semantics (conceptual):** at-most-once, at-least-once,
   effectively-once with idempotent consumers; consequences for correctness.
2. **Ordering and duplication:** ordering guarantees are scoped (per key, per
   partition); duplicates are normal; design consumers to tolerate them.
3. **Replay:** what must be retained; how replay interacts with side effects;
   linking to the Module 3 replay-time estimate.
4. **Failure handling:** poison messages, dead-letter handling, backpressure,
   consumer lag, partial failure across systems, compensating actions.
5. **Schema evolution:** governance of changes; deprecation periods; consumer
   compatibility testing; contract registry at the concept level.
6. **Security, privacy and ownership:** authorisation per topic or product;
   sensitive fields in events; retention of personal data in logs and deletion
   obligations; cross-border sharing.
7. **Consistency:** eventual consistency, ordering across entities, read-your-
   writes expectations, reconciliation (2D.2 and Module 3).
8. **Trade-offs and complexity:** operational burden of brokers, observability,
   debugging asynchronous flows, organisational discipline needed to keep
   contracts honest.
9. **Failure modes:** the distributed monolith (events used as remote calls),
   event sprawl, unversioned changes, hidden dependencies, personal data
   leaking into broadly consumed events.
10. **Questions to answer:** When is a simple scheduled export better? What
    would you require before allowing a new consumer on a sensitive event?
11. **Exercise:** Evaluate a described event design for ordering, duplication,
    schema evolution, privacy and failure risks.

**Ability to demonstrate:** a risk-aware evaluation of an event or sharing
design at pattern level.

#### 6.7 Industry-application exercises

- Design and justify a conceptual event-driven or data-sharing pattern for
  Northbridge's card-transaction path to fraud, risk and finance consumers.
- Specify the event contract fields at the concept level (identity, time,
  type, version, key, payload classification) without choosing a product.
- Define the access and retention rules for the sensitive payload.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* Three teams want customer-change data. One wants every change
   within seconds; two need a daily extract. Design the sharing approach.
2. *Scenario:* A producer removes a field. Which controls would have prevented
   consumer breakage?
3. *Scenario:* A consumer must re-process last week's events but one
   downstream action sends customer notifications. What is the risk?

#### 6.9 Expected outputs and deliverables

- Pattern cards for event-driven integration and each sharing approach.
- Integration-approach comparison.
- Conceptual event/sharing design with contract and risk notes.
- Answers to Topic 6 practice questions.

#### 6.10 Common mistakes and misconceptions

- Treating every integration as an event problem.
- Assuming exactly-once delivery is automatic or free.
- Publishing events without a contract owner.
- Sharing databases directly and calling it integration.
- Ignoring privacy and deletion obligations in logs.
- Confusing event-driven with real-time.

#### 6.11 Mastery criteria

- Chooses among event, API, batch and shared-data approaches with reasons.
- Explains delivery, ordering, duplication and replay implications.
- Addresses contract ownership, evolution, security and privacy.

#### 6.12 Completion gate

- [ ] Integration comparison and conceptual design reviewed.
- [ ] Design states contract owner, compatibility rule and retention rule.
- [ ] Topic 6 practice questions answered and corrected.

---

### Module 7 — [Selecting and combining architecture patterns](07-selecting-and-combining-architecture-patterns.md)

#### 7.1 Learning objectives

- Define the business problem and decision scope.
- Translate requirements into decision criteria.
- Identify viable candidates and eliminate non-viable ones.
- Evaluate organisational, technical, operational, governance and regulatory
  conditions.
- Compare alternatives with explicit criteria; balance quality attributes,
  complexity, risk, effort and cost.
- Identify dependencies, compatibilities and tensions between patterns.
- Combine patterns without unnecessary complexity.
- Record assumptions, trade-offs and rejected alternatives; produce a
  defensible recommendation.

#### 7.2 Why the topic matters in real-world Data Architecture

This is where the previous six topics become a decision. The most common
failure is not choosing the wrong pattern in isolation; it is choosing a
fashionable combination whose parts demand incompatible things of the
organisation.

#### 7.3 Prerequisite knowledge

Modules 1–6 here; all of 2D.2 (especially Topics 5–7).

#### 7.4 Beginner-level learning sequence

1. **Map patterns to problems** with a one-page "problem → pattern" table built
   from Section 1.4.
2. **Learn the selection sequence:** problem → requirements → constraints →
   criteria → candidates → compare → combine → record.
3. **Learn that patterns operate at different levels:** operating model
   (Module 1, 4), storage (Module 2), processing (Module 3), metadata and
   governance (Module 5), interaction (Module 6). They are largely
   **orthogonal** and can be combined along these axes.
4. **Questions to answer:** Which pattern axes does a given requirement touch?
   Why can one organisation use several patterns at once?
5. **Exercise:** For ten short requirement statements, name the pattern axis
   each primarily concerns.

**Ability to demonstrate:** place a requirement on the correct axis and name
candidate patterns.

#### 7.5 Intermediate-level learning sequence

1. **Build a consistent criteria set** from requirements (2D.2) and quality
   attributes (2D.1), with must-have gates first.
2. **Create a compact pattern fit table** per axis: for each pattern, the
   conditions where it fits, the conditions where it does not, and the key
   cost.
3. **Compare several candidates** against the same criteria with evidence for
   each rating.
4. **Use weighted scoring carefully:** fix criteria and weights before scoring,
   state the basis of each weight, treat close scores as ties and look at
   sensitivity (2D.2 Topic 6).
5. **Identify dependencies between patterns,** for example:

   | If you choose | It usually depends on |
   | --- | --- |
   | Domain data products (mesh) | Platform self-service, metadata/catalog, federated governance, contracts |
   | Event-driven sharing | Contract management, replay retention, consumer idempotence |
   | Kappa | Durable, replayable log with adequate retention |
   | Lakehouse | Table management, metadata, compute governance |
   | Fabric | Quality metadata, connector coverage, a metadata owner |

6. **Questions to answer:** Which requirement eliminated each rejected
   candidate? Which two candidates are the close contenders and why?
7. **Exercise:** Compare four candidate combinations for a described scenario
   using a shared criteria table.

**Ability to demonstrate:** an evidence-based comparison with explicit criteria
and visible dependencies.

#### 7.6 Advanced-level learning sequence

1. **Competing constraints:** a regulator wants central control; the business
   wants domain autonomy; the budget limits platform investment. Show how each
   constrains the candidate set.
2. **Mixed approaches:** different patterns for different data classes (for
   example central control for regulated reporting data, domain products for
   exploratory analytics) with an explicit boundary and interface.
3. **Compatible and incompatible combinations:** e.g. a federated operating
   model combines well with a metadata-driven control plane; a Lambda design
   combined with many domain teams multiplies duplicated logic; a lake-only
   store conflicts with a requirement for governed, reconciled reporting.
4. **Architectural tensions:** autonomy versus consistency; freshness versus
   cost; openness versus control; speed of delivery versus long-term
   maintainability.
5. **Operational consequences:** support model, skills, incident handling,
   cost allocation, upgrade paths.
6. **Uncertainty:** use ranges and sensitivity; prefer options that stay
   acceptable across plausible assumptions; consider staged adoption and
   reversibility.
7. **Avoid popularity-driven selection:** require evidence and a stated
   problem for every pattern included; a pattern without a requirement behind
   it is removed.
8. **Parsimony test:** for each pattern in the combination, answer: what
   requirement does this serve, and what is the simplest alternative that would
   do?
9. **Record the decision:** ADR with context, criteria, options, outcome,
   rejected alternatives with reasons, consequences and revisit triggers
   (2D.2 Topic 7).
10. **Questions to answer:** Which pattern would you remove first? What would
    make you reverse the recommendation?
11. **Exercise:** Take an over-engineered proposal that includes five patterns,
    reduce it to the minimum justified set, and document why each removal is
    safe.

**Ability to demonstrate:** a minimal justified combination with conditions for
revisiting.

#### 7.7 Industry-application exercises

- Produce an evidence-based pattern recommendation for Northbridge with a
  comparison matrix and documented rationale (this feeds the project).
- Write the ADR for the main pattern combination.
- Run a parsimony review on your own recommendation.

#### 7.8 Practical scenarios and case-based reasoning

1. *Scenario:* A vendor proposes a platform bundling lakehouse, fabric and
   mesh features. How do you separate the problem each solves from the
   marketing?
2. *Scenario:* The recommended combination requires platform skills the bank
   does not have. What are the options?
3. *Scenario:* A new regulation moves one data class under central control. Which
   parts of an existing domain-oriented design change?

#### 7.9 Expected outputs and deliverables

- Problem-to-pattern table and axis map.
- Candidate comparison matrix with sensitivity notes.
- Combination rationale and parsimony review.
- ADR for the recommendation.
- Answers to Topic 7 practice questions.

#### 7.10 Common mistakes and misconceptions

- Selecting by popularity or vendor positioning.
- Comparing a favoured option with straw men.
- Combining many patterns with no requirement behind each.
- Ignoring organisational prerequisites and dependencies between patterns.
- Treating weighted scores as objective truth.
- Failing to record rejected alternatives and revisit conditions.

#### 7.11 Mastery criteria

- Uses explicit, requirement-derived criteria and consistent comparison.
- Justifies each pattern in a combination and names dependencies and tensions.
- Records assumptions, trade-offs and rejected alternatives and states what
  would change the recommendation.

#### 7.12 Completion gate

- [ ] Comparison matrix, combination rationale and ADR complete.
- [ ] Every pattern in the recommendation traces to a requirement.
- [ ] Parsimony review shows at least one considered-and-removed pattern.
- [ ] Topic 7 practice questions answered and corrected.

---

## 5. Module dependencies and recommended learning order

### 5.1 Dependency table

| # | Topic file | Prerequisite concepts | Main learning outcome | Practical exercise / deliverable | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `01-centralized-federated-and-domain-oriented-architectures.md` | 2D.1 Topics 3, 5; 2D.2 Topic 5 | Choose an ownership and governance model with stated conditions | Pattern cards; responsibility matrix; hybrid recommendation | Reviewed matrix; failure modes and prerequisites named |
| 2 | `02-data-warehouse-data-lake-and-lakehouse-patterns.md` | Topic 1; 2D.2 Topics 3–4 | Match workloads to analytical storage patterns | Workload-to-pattern map; option comparison | Map with reasons; no universal-superiority claim |
| 3 | `03-lambda-and-kappa-architectures.md` | Topic 2; 2D.2 Topic 4 | Judge whether batch/stream patterns are needed and at what cost | Comparison; replay-time analysis | Quantified replay; a "neither required" case |
| 4 | `04-data-mesh-principles-and-domain-data-products.md` | Topic 1; 2D.1 Topic 3 | Specify data products and assess readiness | Product specifications; readiness assessment; pilot plan | Reviewed specs; unsuitability considered |
| 5 | `05-data-fabric-and-metadata-driven-architecture.md` | Topics 1–4; 2D.1 Topic 5 | Explain metadata-driven discovery, governance and automation, and its limits | Conceptual design; comparison with mesh and integration | Design lists dependencies and limits |
| 6 | `06-event-driven-and-data-sharing-patterns.md` | Topics 1, 3, 4; 2D.2 Topics 3–5 | Choose among event, API, batch and shared-data approaches | Integration comparison; conceptual design with contract rules | Contract owner, compatibility and retention rules stated |
| 7 | `07-selecting-and-combining-architecture-patterns.md` | Topics 1–6; 2D.2 Topics 5–7 | Select and combine patterns on explicit criteria | Comparison matrix; combination rationale; ADR | Every pattern traces to a requirement; parsimony review |

### 5.2 Recommended order and why

1. **Topic 1 first: organisational and ownership perspective.** Every pattern
   assumes an operating model. Deciding who is responsible precedes deciding
   what is built.
2. **Topic 2: core analytical data architecture.** Warehouse, lake and
   lakehouse give the most common storage-level choice and the vocabulary of
   layers.
3. **Topic 3: batch and streaming approaches.** Builds on storage and on the
   freshness targets from Module 2D.2.
4. **Topic 4: domain ownership and data product operating models.** Extends
   Topic 1 from a model to a specific, well-known approach.
5. **Topic 5: metadata-driven integration, discovery and automation.**
   Provides the control plane that makes distributed ownership (Topic 4) and
   distributed storage (Topic 2) governable.
6. **Topic 6: cross-system and cross-domain interaction.** Needs the ownership,
   product and processing concepts before choosing how data are exchanged.
7. **Topic 7: integration of all previous modules.** Selection and combination
   are only credible after the individual patterns are understood.

### 5.3 Overlaps and reinforcement

| Overlap | Where to take care |
| --- | --- |
| Domain-oriented (1) and data mesh (4) | Mesh is a specific, opinionated form of domain orientation; do not treat them as synonyms |
| Lakehouse (2) and Kappa (3) | Both can rely on replayable stored history; the log versus table-history distinction matters |
| Data mesh (4) and fabric (5) | Complementary: mesh addresses ownership, fabric addresses metadata and automation |
| Data products (4) and data sharing (6) | A product interface is a data-sharing pattern with ownership and service levels |
| Lambda/Kappa (3) and events (6) | Event logs are the substrate of Kappa; events as integration is a wider idea than Kappa |
| Governance (1, 4, 5) | Central, federated and computational governance must be read together |

### 5.4 Not a rigid order

Revisit earlier topics when a scenario demands it:

| Trigger | Revisit |
| --- | --- |
| Selecting a combination reveals that the operating model cannot support it | Topic 1, Topic 4 |
| A freshness target changes | Topic 3, Topic 6 |
| A governance finding shows metadata gaps | Topic 5 |
| A regulatory change moves a data class | Topics 1, 2, 7 |
| Sensitivity analysis flips the ranking | Topic 7 and 2D.2 Topic 3–4 estimates |

Cross-references: foundations (2D.1), requirements and decisions (2D.2),
modeling (2D.4), storage (2D.5), integration (2D.6), platform (2D.7), cloud
(2D.8), streaming (2D.9), governance (2D.10), metadata (2D.11), documentation
and reviews (2D.15).

---

## 6. Practice questions and knowledge validation

### 6.1 Role of `practice-questions.md`

[`practice-questions.md`](practice-questions.md) is the practice and assessment
resource for this module. It is currently empty. This roadmap defines how to
use it and what it should contain by category; it does not duplicate the
questions. Populate it to match the categories below.

### 6.2 Categories and how to use them

| Category | Purpose | Topics | Typical level |
| --- | --- | --- | --- |
| Conceptual understanding | Definitions and distinctions | 1–7 | Beginner |
| Pattern identification | Recognise the pattern in a described or drawn system | 1–6 | Beginner → intermediate |
| Pattern comparison | Compare two or more on structure and consequences | 1–6 | Intermediate |
| Architecture diagram interpretation | Read a diagram, name patterns, flows, owners, gaps | 1–6 | Intermediate → advanced |
| Organisational and ownership analysis | Responsibility, governance, readiness | 1, 4, 5 | Intermediate → advanced |
| Scenario-based pattern selection | Choose with stated requirements | 2, 3, 6, 7 | Intermediate → advanced |
| Quality-attribute trade-offs | Reason about conflicting attributes | 2, 3, 6, 7 | Advanced |
| Operational and governance risks | Failure modes, controls, evidence | 2–6 | Advanced |
| Combining patterns | Justify compatible combinations and spot conflicts | 7 | Advanced → industry |
| Defending an architecture recommendation | Present and withstand challenge | 7 | Industry |

### 6.3 Strategy

1. Answer each topic's questions after the topic, closed-book first.
2. For diagram questions, state each element, its pattern role, and one thing
   missing or risky.
3. For scenario questions, always write: requirements used, constraints used,
   candidates, elimination reasons, choice, accepted trade-offs.
4. Mark each answer correct / partly correct / wrong with a one-sentence
   reason; re-attempt after several days.
5. Keep selection and defence answers as written text for the project.
6. Have advanced and industry answers reviewed by another person.

### 6.4 Expected performance by level

| Level | Successful performance |
| --- | --- |
| Beginner | Accurate definitions; correct identification of patterns in examples; no confusion between neighbours (for example mesh versus domain-oriented, fabric versus mesh, Lambda versus Kappa) |
| Intermediate | Correct comparisons on ownership, governance, integration and operations; scenarios mapped to patterns with stated reasons |
| Advanced | Answers identify failure modes, organisational prerequisites, operational cost and constraints; state when the pattern is the wrong choice |
| Industry application | Integrated recommendations with explicit criteria, rejected alternatives, assumptions and revisit conditions that a reviewer can audit |

### 6.5 What is assessed beyond recall

| Aspect | Evidence in an answer |
| --- | --- |
| Reasoning | Steps from requirement to conclusion are visible |
| Recognising limitations | Costs, prerequisites and failure modes of the chosen pattern are stated |
| Justifying decisions | Criteria, evidence and alternatives are cited |
| Distinguishing fact from assumption | Assumptions are labelled |
| Concept versus product | Pattern properties are not attributed to specific vendors |

---

## 7. Project — Reference architecture pattern comparison

Project file:
[`Projects/03-reference-architecture-pattern-comparison.md`](Projects/03-reference-architecture-pattern-comparison.md)
(currently empty; this section defines its intended content). The project
index is [`Projects/README.md`](Projects/README.md).

This is an **architecture evaluation project**, not a report listing advantages
and disadvantages. It requires you to compare patterns against requirements,
evaluate organisational and governance consequences, decide whether a single
pattern or a combination is justified, and produce a reference architecture
view.

How it uses the seven topics:

| Project part | Topics |
| --- | --- |
| Operating model and ownership options | 1, 4 |
| Analytical storage options | 2 |
| Batch/stream processing options | 3 |
| Metadata, discovery and control | 5 |
| Cross-system interaction | 6 |
| Selection, combination, recommendation | 7 |

### 7.1 Project objective

You must demonstrate that you can:

- Identify the architecture decisions a scenario requires.
- Describe relevant patterns at a consistent conceptual level.
- Evaluate each against requirements, constraints and explicit criteria.
- Identify trade-offs, failure modes and organisational implications.
- Decide whether one pattern or a combination is justified, and why.
- Produce a defensible recommendation with rejected alternatives and
  conditions for revisiting.

### 7.2 Project scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. It has a core banking system, a cards
platform, a CRM and a loan origination system. Nightly extracts feed an
enterprise data warehouse. A data lake created three years ago holds copies of
some sources and is poorly trusted. Four business domains (retail, lending,
cards, risk) each have analysts and some engineering capability. A central data
team of about 25 people serves the whole bank and has a long backlog.

> All details and numbers below are **illustrative assumptions**, not facts
> about any real organisation. You may substitute a real or realistic
> organisation (observing confidentiality) but must label what you observed
> versus what you assume.

**Business problem.** The bank needs consistent, governed, timely data for
regulatory reporting, fraud detection, risk analytics and customer analytics,
while reducing the central team's bottleneck and improving accountability and
discoverability.

**Stakeholders and data consumers (assumed).** Chief data officer (sponsor);
heads of retail, lending, cards and risk; fraud operations; finance; regulatory
reporting; compliance; security; internal audit; data science; platform and
engineering leads.

**Workload characteristics (illustrative).**

| Workload | Characteristics |
| --- | --- |
| Regulatory reporting | Monthly and quarterly; reconciled, auditable; batch |
| Fraud detection | Card events within seconds–minutes; plus historical features |
| Risk analytics | Daily exposure; large historical volumes |
| Customer analytics | Daily to weekly; mixed structured and semi-structured data |
| Document and interaction data | Unstructured; search and retrieval |

**Required freshness and availability (illustrative).** Fraud path: p95
freshness ≤ 60 s from event to availability to the analyst tool, 08:00–22:00.
Regulatory reporting: complete and reconciled by T+2 business days. Analytical
platform availability: 99.5% monthly on business days. (Each should be
re-derived and justified using the 2D.2 method if you reuse them.)

**Governance and ownership expectations.** Named accountability for sensitive
customer data; end-to-end lineage for regulatory data; policy-based access
control; evidence for audit.

**Constraints and assumptions (illustrative).** Personal data must stay in a
stated jurisdiction; the core banking batch window ends at 02:30; the central
team cannot grow beyond a modest increase; domain teams have uneven engineering
skills; a regulatory milestone date applies; existing identity services must be
used.

**In scope.** Choice among organisational, storage, processing, metadata and
interaction patterns; their combination; the recommended reference
architecture at a conceptual level.

**Out of scope.** Product selection, detailed schema design (2D.4), physical
storage design (2D.5), integration implementation (2D.6), platform build (2D.7),
cloud service mapping (2D.8), detailed streaming design (2D.9), implementation
and migration plans.

### 7.3 Step-by-step project execution

For each step: **Purpose · Inputs · Actions · Questions to answer · Outputs ·
Validation.**

| Step | Purpose | Inputs | Actions | Questions to answer | Outputs | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define problem and assessment scope | Scenario | Write problem statement, scope, exclusions | What is being decided, and what is not? | Scope statement | Sponsor-role reviewer confirms |
| 2 | Identify stakeholders, consumers, outcomes | Scenario | Register; map consumers to workloads | Who decides? Who consumes? What outcome matters? | Stakeholder and consumer table | Each workload has a consumer and an outcome |
| 3 | Gather functional and non-functional requirements | Steps 1–2; 2D.2 method | Write measurable requirements and targets | Which are architecturally significant? | Requirements and targets | Each testable and sourced |
| 4 | Identify constraints, assumptions, dependencies, risks | Steps 1–3 | Classify with the 2D.2 tests | Which constraints eliminate options? | Register | No unclassified item |
| 5 | Determine the architecture decisions required | Steps 3–4 | List decisions by axis: operating model, storage, processing, metadata, interaction | Which are independent, which coupled? | Decision list | Every significant requirement links to a decision |
| 6 | Select candidate patterns | Steps 5; Modules 1–6 | Shortlist per axis, including a minimal baseline | Is each candidate viable for the problem? | Candidate inventory | Each candidate has a reason; non-viable ones removed with cause |
| 7 | Describe each candidate's conceptual architecture | Step 6 | One-page description: components, responsibilities, flow, owners | What does each part do and who runs it? | Candidate descriptions | Consistent level of detail across candidates |
| 8 | Map candidates to requirements and constraints | Steps 3–4, 7 | Matrix of fit/gap | Which requirements does each satisfy, fail or leave open? | Mapping | Gate failures flagged |
| 9 | Compare using explicit criteria | Steps 8; Section 7.5 | Set criteria and weights (if used) before scoring; rate with evidence | Where is evidence weakest? | Comparison matrix | Criteria fixed before scoring |
| 10 | Evaluate organisation and operating-model implications | Module 1, 4 | Readiness, roles, funding, decision rights | What must the organisation become? | Organisational assessment | Prerequisites compared with current state |
| 11 | Evaluate governance, security, interoperability, ownership | Modules 4–6 | Controls, policy enforcement, contracts, lineage | Can accountability be evidenced? | Governance assessment | Each regulatory need has a control |
| 12 | Evaluate reliability, performance, scalability, complexity, cost | 2D.2 estimates | Qualitative and rough quantitative analysis | What does it cost to run and recover? | Quality-attribute assessment | Numbers carry units and are labelled illustrative |
| 13 | Identify failure modes, limitations, uncertainties | Steps 9–12 | Failure-mode list; open questions | How does each candidate fail? | Risk and limitation register | Each item linked to a candidate and a finding |
| 14 | Decide single pattern or combination | Steps 9–13 | Parsimony test per pattern | What requirement does each pattern serve? | Combination decision | Each pattern traces to a requirement |
| 15 | Recommend and explain rejected alternatives | Step 14 | State choice and reasons; record rejections | Why not the runner-up? | Recommendation | Reasons cite criteria and evidence |
| 16 | Document assumptions, trade-offs, revisit conditions | Step 15 | List assumptions, accepted trade-offs, triggers | What would change the answer? | Assumptions and triggers | Each trigger tied to an assumption |
| 17 | Produce a reference architecture view | Steps 14–16 | Conceptual diagram or structured description: layers, domains, flows, control plane, interfaces | Is every element justified? | Reference architecture view | No unexplained element |
| 18 | Validate consistency and traceability | All | Cross-check requirement → criterion → decision → view | Any contradiction? | Review notes | Random traces succeed |
| 19 | Prepare the final recommendation and review summary | All | Short summary for sponsor and review board | What is decided, why, and at what cost and risk? | Final summary | Non-specialist can follow in ten minutes |

**Per-step guidance:**

1. Write exclusions as firmly as inclusions; this project stops at the
   reference architecture.
2. Include control functions (compliance, security, audit).
3. Re-use the 2D.2 requirement template; no technology names in requirements.
4. Mark unknowns as unknown.
5. Separate axes; do not compare "Lambda vs data mesh" as if they were
   alternatives for the same decision.
6. Always include a "minimal change" baseline.
7. Describe patterns at the same level of abstraction.
8. A gate failure removes a candidate; it is not a low score.
9. Fix criteria and weights **before** looking at totals.
10. Be specific about people, roles and funding, not just boxes.
11. Tie each control to a requirement.
12. State formulas and units for every numeric claim.
13. Include at least one "how this fails at 3 a.m." per candidate.
14. Remove any pattern that cannot name a requirement behind it.
15. Rejected alternatives need specific reasons, not "too complex".
16. Triggers should be observable.
17. Label the view's level (reference, not blueprint).
18. Correct the source artefact first, then follow the trace forward.
19. State limits and conditional parts plainly.

### 7.4 Required project deliverables

Deliverables are proportionate; related content is combined rather than
duplicated.

| # | Deliverable | Purpose | Minimum contents |
| --- | --- | --- | --- |
| D1 | Project scope and business problem statement | Fix boundaries | Problem, objectives, in/out of scope, labelled assumptions |
| D2 | Requirements and constraints summary | Basis for evaluation | Key requirements and targets, constraints, assumptions, dependencies, risks (IDs) |
| D3 | Candidate architecture pattern inventory | Show options considered | Pattern, axis, why a candidate, why excluded (if so) |
| D4 | Conceptual architecture description per candidate | Comparable understanding | Components, responsibilities, flow, ownership, operating model |
| D5 | Pattern comparison matrix | Transparent comparison | Criteria, weights and rationale (if used), ratings with evidence |
| D6 | Architecture trade-off analysis | Make costs explicit | Trade-offs per candidate, sensitivity result, reversibility |
| D7 | Organisational and governance implications | Test viability | Roles, readiness, decision rights, controls, evidence needs |
| D8 | Risk and limitation register | Honest limits | Failure modes, limitations, uncertainties, mitigations, owners |
| D9 | Recommended pattern or pattern combination | The decision | Chosen patterns, role of each, dependencies, incompatibilities avoided |
| D10 | High-level reference architecture diagram or structured view | Communicate the design | Layers/domains, flows, control plane, interfaces, legend, version |
| D11 | Decision rationale and rejected alternatives | Defensibility | Why chosen, why others rejected, assumptions, revisit triggers (ADR form from 2D.2 Topic 7) |
| D12 | Final architecture recommendation and review summary | Sponsor/board readout | One to two pages: decision, rationale, trade-offs, conditions, risks, next steps |

### 7.5 Pattern comparison criteria

Use only the criteria relevant to the scenario; justify the choice and relative
importance from the requirements.

| Criterion | What it asks | Typical evidence |
| --- | --- | --- |
| Business and workload fit | Does the pattern serve the stated workloads? | Workload map, requirement mapping |
| Ownership and organisational alignment | Does it match who can own and operate data? | Readiness assessment |
| Integration and interoperability | Can data combine across domains and systems? | Interfaces, shared identifiers, contracts |
| Batch and streaming suitability | Does it handle the processing mode needed? | Freshness and replay needs |
| Freshness and latency | Can targets be met? | Timing budget (2D.2 Topic 4) |
| Scalability and performance | Does it handle volume and growth? | Estimates (2D.2 Topic 3) |
| Governance and security | Can control and evidence be provided? | Control mapping |
| Metadata and discoverability | Can consumers find and trust data? | Metadata requirements |
| Reliability and recoverability | Failure and recovery behaviour | Failure modes, replay time |
| Operational complexity | Skills, tools, runbooks | Operating model |
| Implementation and migration effort | Effort and disruption | Rough effort ranges |
| Cost and long-term maintainability | Run cost, change cost | TCO sketch with ranges |
| Organisational readiness | Capabilities needed versus available | Gap list |

**If using weighted scoring:**

1. Derive criteria from requirements and quality attributes; apply must-have
   **gates** first.
2. Establish weights from a stated rule (for example stakeholder ranking
   converted to weights, or pairwise comparison), record who agreed, and fix
   them **before** scoring.
3. Use a defined rating scale (for example 1–5 with written meaning for each
   level) and rate from evidence.

   ```text
   score(option) = Σ ( weight_i × rating_i(option) ),   Σ weight_i = 1
   ```

4. Perform sensitivity analysis on weights and uncertain inputs; treat close
   scores as ties.
5. Document the limits: weights are subjective, criteria may overlap, scores
   hide gate failures, and numerical totals are **decision support, not
   objective truth.**

### 7.6 Validation and quality assurance

| Check | How to verify |
| --- | --- |
| Candidate patterns are relevant to the problem | Each candidate links to at least one requirement; irrelevant ones removed |
| Requirements and constraints explicitly documented | D2 exists with IDs and sources |
| Each candidate evaluated against consistent criteria | Same criteria and evidence standard for all candidates |
| Important trade-offs acknowledged | D6 states what each candidate gives up |
| Organisational and governance implications considered | D7 compares prerequisites with current state |
| Pattern combinations have a clear purpose | Each pattern in the combination traces to a requirement |
| Recommendation follows from the analysis | Each recommendation cites matrix rows and trade-offs |
| Rejected alternatives have documented reasons | D11 gives specific, evidence-based reasons |
| Assumptions and uncertainties are visible | Assumptions listed with confidence and triggers |
| Architecture description is consistent with the recommendation | Every element of D10 appears in D9 and vice versa |
| Numbers consistent | Units, formulas and illustrative labels checked across documents |

### 7.7 Project completion gate

The project is complete only when **all** hold:

- [ ] D1–D12 exist, version-dated and use consistent IDs.
- [ ] **Requirements:** key requirements are measurable and sourced; no
      requirement embeds a pattern or product.
- [ ] **Candidates:** at least three feasible candidates or combinations are
      evaluated, including a minimal baseline; gate failures are recorded with
      reasons.
- [ ] **Criteria:** criteria and weights (if used) are fixed and dated before
      scoring; sensitivity analysis states whether the ranking changes.
- [ ] **Trade-offs:** each candidate has stated costs, failure modes and
      organisational prerequisites.
- [ ] **Combination:** every pattern in the recommendation traces to a
      requirement; at least one pattern considered and removed is documented
      by the parsimony test.
- [ ] **Governance:** each regulatory or accountability need maps to a control
      and an owner.
- [ ] **Numbers:** any numeric claim has units, formula, assumption and
      illustrative label.
- [ ] **View:** the reference architecture view is consistent with the
      recommendation and has no unexplained element.
- [ ] **Traceability:** a random trace from three recommendation elements back
      to requirements, and from three requirements forward to decisions,
      succeeds.
- [ ] **Defensibility:** you answer two reviewer challenges using recorded
      evidence, and an independent reviewer agrees the conclusion follows from
      the evidence.

Submitting all documents is **not** sufficient.

### 7.8 Connection to subsequent modules

| Later module | How the project supports it |
| --- | --- |
| 2D.4 Conceptual, logical and physical modeling | Domain boundaries and product scope define model boundaries |
| 2D.5 Database and storage architecture | The analytical storage and layer decisions are the input |
| 2D.6 Data integration and interoperability | The interaction pattern and contract rules are the input |
| 2D.7 Enterprise data platform and lakehouse | The platform operating model and control plane are the input |
| 2D.8 Cloud, hybrid and multi-cloud | Patterns and constraints guide service mapping |
| 2D.9 Streaming and real-time | The processing-pattern decision frames detailed design |
| 2D.10 Governance, security, privacy, compliance | The governance model and control mapping are the input |
| 2D.15 Documentation and reviews | The comparison, ADR and view are review artefacts |

Do not add implementation tasks that belong to those modules.

---

## 8. Final learning assessment and completion checklist

Self-reported confidence is not sufficient; each row requires evidence.

| # | You can… | Evidence of mastery |
| --- | --- | --- |
| 1 | Explain the purpose and limitations of major data architecture patterns | Pattern cards for all seven topics with prerequisites and failure modes, reviewed |
| 2 | Compare centralized, federated and domain-oriented architectures | Responsibility matrix and hybrid recommendation with organisational conditions |
| 3 | Evaluate warehouse, lake and lakehouse patterns | Workload-to-pattern map and option comparison with no universal-superiority claim |
| 4 | Explain Lambda and Kappa and their trade-offs | Comparison with replay-time analysis and one case where neither is needed |
| 5 | Apply data mesh principles and reason about domain data products | Product specifications, readiness assessment, pilot with stop criteria |
| 6 | Explain data fabric and metadata-driven architecture | Conceptual design with dependencies and limitations; comparison with mesh and integration |
| 7 | Evaluate event-driven and data-sharing patterns | Integration comparison and conceptual design with contract, evolution, retention and privacy rules |
| 8 | Select and combine patterns based on explicit requirements | Matrix, combination rationale, parsimony review, ADR |
| 9 | Produce a structured pattern comparison | D5 with criteria fixed before scoring and sensitivity analysis |
| 10 | Defend a recommendation using evidence, constraints and trade-off analysis | Challenge round: two reviewer objections answered from recorded evidence |

Module complete when:

- [ ] All seven topic completion gates are signed off.
- [ ] `practice-questions.md` answered; wrong answers corrected and
      re-attempted.
- [ ] The project completion gate (Section 7.7) is met.
- [ ] You have presented the recommendation and answered a reviewer's
      challenges without introducing unsupported claims.
- [ ] Open questions are logged for the next module (2D.4).

---

## 9. Where this module leads

Module 2D.4, **Conceptual, Logical and Physical Data Modeling**, takes the
domain boundaries, data product scope and pattern decisions made here and
gives them structure: entities, relationships, grain and models that implement
the chosen architecture.
