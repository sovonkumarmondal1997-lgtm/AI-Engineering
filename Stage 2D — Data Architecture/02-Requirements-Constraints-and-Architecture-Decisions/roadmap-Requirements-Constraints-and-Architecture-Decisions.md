# Roadmap — Module 2D.2: Requirements, Constraints and Architecture Decisions

This is the learning roadmap for the second module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Module 2D.1 gave you the role, the vocabulary, the principles and the
governance view. This module teaches the working core of the role: taking an
incomplete business request and turning it into **explicit, measurable,
traceable requirements**, understanding the **constraints and uncertainties**
that bound the problem, **comparing alternatives** on stated criteria, and
**recording decisions** so that they can be reviewed, defended and revisited.

> **Repository note.** The seven topic files, `practice-questions.md`, the
> module and project READMEs, and the project file
> `Projects/02-requirements-and-architecture-decision-pack.md` currently exist
> but are empty, as are the Stage 2D overview files. This roadmap is therefore
> the first written statement of the module's scope. It defines the learning
> sequence for each topic file; it does not claim that any topic file already
> contains this material. The repository mandates **no ADR template**; Section
> 4 (Module 7) proposes a practical structure inside this roadmap.
>
> **Illustrative values.** Every number, system and organisation in this
> roadmap is an **illustrative assumption** used to teach a method. None of it
> is a real requirement or a recommended target.

---

## 1. Module overview

### 1.1 What this module covers

| Term | Meaning in this module |
| --- | --- |
| **Requirements analysis** | Discovering, stating, classifying, prioritising and validating what stakeholders need from data and the systems that hold it |
| **Constraints analysis** | Identifying what limits the solution: fixed constraints, negotiable preferences, assumptions, dependencies and risks |
| **Architecture decision-making** | Choosing among feasible alternatives against explicit criteria, accepting stated trade-offs, and recording the result |

### 1.2 Four activities that are often confused

| Activity | Output | Typical failure |
| --- | --- | --- |
| **Gathering** requirements | A collection of stakeholder statements | Treating requests as requirements |
| **Defining measurable** requirements | Testable statements with metric, target, scope and measurement method | Adjectives instead of numbers ("fast", "real-time") |
| **Evaluating alternatives** | A comparison of feasible options on explicit criteria | Comparing one real option with two straw men |
| **Making an architecture decision** | A recorded choice with rationale, trade-offs and consequences | Deciding first and justifying afterwards |

### 1.3 Why this module exists in Stage 2D

Module 2D.1 told you what an architect is accountable for. This module is where
that accountability turns into evidence-based work. It sits second because
every later module consumes its outputs: you cannot choose a pattern, a model, a
store or a cloud design without requirements, targets, constraints and a
decision method.

### 1.4 How it builds on 2D.1

| From 2D.1 | Used here |
| --- | --- |
| Stakeholder expectations and the decision chain (Topic 1) | Structured stakeholder discovery (Topic 1 here) |
| Quality attributes and measurable targets (Topic 4) | Non-functional requirements and service targets (Topics 2, 4 here) |
| Business drivers, constraints, assumptions (Topic 4) | Full constraints analysis (Topic 5 here) |
| Decision notes and exception records (Topics 1, 4, 5) | ADRs (Topic 7 here) |
| Current-state inventory (project) | Baseline for volume estimates, constraints and gaps |

### 1.5 How it supports later modules

| Later module | What it takes from this one |
| --- | --- |
| 2D.3 Patterns and reference architectures | Requirements and criteria used to select and combine patterns |
| 2D.4 Data modeling | Business requirements, entities and quality needs that shape models |
| 2D.5 Storage architecture | Volume, growth, latency and retention estimates |
| 2D.6 Integration | Freshness, throughput and availability targets |
| 2D.7 Platform and lakehouse | Capacity, service levels and constraints |
| 2D.8 Cloud and hybrid | Regulatory, cost and dependency constraints |
| 2D.10 Governance and compliance | Regulatory constraints and evidence needs |
| 2D.13 Performance and cost | Targets, estimates and sensitivity analysis |
| 2D.15 Documentation and reviews | ADR practice and decision history |

### 1.6 From incomplete request to testable requirement

A Data Architect rarely receives requirements. They receive requests.

```text
Request:       "We need real-time customer data."
   ↓ ask why (Topic 1)
Need:          Fraud analysts must see a card transaction in the case tool
               before the customer's next transaction attempt.
   ↓ classify (Topic 2)
Requirement:   Functional: expose card transactions to the case tool.
               Non-functional: freshness and availability.
   ↓ quantify (Topics 3, 4)
Measurable:    p95 end-to-end freshness ≤ 30 s during business hours,
               measured from authorisation timestamp to availability in the
               case tool. (Illustrative target.)
   ↓ bound (Topic 5)
Constraints:   Card platform emits batch files only today (fixed). Budget
               ceiling set by the programme (fixed). Preferred tool is not
               mandatory (negotiable).
   ↓ decide (Topics 6, 7)
Decision:      Chosen approach, rejected alternatives, trade-offs, ADR.
```

Each arrow is a skill. Each stage must be **traceable** to the one before it.

### 1.7 Expected capabilities after the module

- Elicit and validate requirements from conflicting, vague or incomplete input.
- Write functional and non-functional requirements that are measurable, testable
  and traceable.
- Estimate data volume, arrival rate, retention and growth with formulas, units,
  assumptions and ranges.
- Convert statements such as "real-time" into percentile-based, scoped,
  measurable targets.
- Separate facts, assumptions, constraints, dependencies and risks, and manage
  each properly.
- Define decision criteria, compare real alternatives, test sensitivity to
  assumptions, and explain what is traded away.
- Write and maintain ADRs with real alternatives and traceable evidence.
- Produce an integrated requirements and decision pack that a reviewer can
  audit.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

| Prerequisite | Why it matters here |
| --- | --- |
| Module 2D.1 completed (or its topic gates passed) | This module uses its vocabulary: stakeholders, capabilities, ownership, principles, quality attributes, governance and decision records |
| Stage 2–2C data engineering experience | Estimates and targets need a concrete picture of batch, streaming, storage and serving behaviour |
| Basic arithmetic and unit handling (powers of ten and two, rates, percentages) | Every estimate requires correct units and unit conversion |
| Ability to write structured prose and tables | Requirements, ADRs and recommendations are written artefacts |

### 2.2 Helpful prior knowledge

- Experience of a real delivery project, even a small one, so that
  requirements and constraints attach to something.
- Familiarity with percentiles and simple statistics (median, p95, p99).
- Familiarity with SQL and data formats (CSV, JSON, Parquet, Avro) for size
  estimation.
- Awareness of Stage 2C module 08 (data platform architecture and data
  products), including build-versus-buy reasoning.

### 2.3 Concepts you will learn during this module

- Elicitation techniques and requirement validation.
- Requirement quality criteria and traceability.
- Capacity estimation and workload characterisation.
- Service-level indicators, objectives and error budgets at an introductory
  level.
- Risk assessment, assumption management and dependency mapping.
- Multi-criteria comparison, sensitivity analysis and decision records.

No requirements-management tool, formal modelling language or certification is
required.

---

## 3. Learning progression

### 3.1 The four levels

| Level | You study | You do | You must answer | You must show |
| --- | --- | --- | --- | --- |
| **1. Beginner** | Terminology, purpose, basic techniques, simple examples | Define, classify and label with guided examples | What is this? How does it differ from its neighbour? | Correct, concise explanations and classifications |
| **2. Intermediate** | Elicitation, classification, estimation, realistic scenarios | Interview (hypothetically), classify, calculate, validate | What is missing? What does this imply? What would you measure? | A correct analysis with stated assumptions and units |
| **3. Advanced** | Ambiguity, uncertainty, competing requirements, trade-offs | Resolve conflicts, run sensitivity analysis, defend decisions | What changes the answer? What is traded away? What would reverse this? | A defended recommendation that survives challenge |
| **4. Industry application** | Real-world documentation and review practice | Produce reviewable registers, targets, risk records, ADRs and the decision pack | Can another architect audit and act on this? | The completed project, traceable end to end |

### 3.2 Entry and exit conditions

| Move from → to | Condition |
| --- | --- |
| Beginner → Intermediate | You classify 90% of provided example statements correctly without notes and can explain each category in your own words |
| Intermediate → Advanced | You analyse a described scenario, produce a requirements set with units, assumptions and sources, and a reviewer finds no unmeasurable "must" statements |
| Advanced → Industry | You defend one recommendation against two reviewer challenges, citing criteria, evidence and sensitivity |
| Industry → complete | The project completion gate (Section 7.7) is met and a reviewer who did not do the work agrees the evidence supports the conclusions |

### 3.3 Emphasis

The module rewards **analytical reasoning, traceability, quantification and
decision quality**. It does not reward memorising definitions, producing long
documents or using impressive vocabulary. A short artefact with a correct
number, a stated assumption and a traceable source is worth more than a long
one without them.

### 3.4 The architect's working loop (use for every topic)

```text
Read → Restate → Apply to the shared scenario → Quantify what can be
quantified → Record assumptions → Check traceability → Have it challenged → Revise
```

1. **Read** the topic file once, fully.
2. **Restate** its core ideas in three or four sentences without looking.
3. **Apply** them to the shared scenario in Section 7.2.
4. **Quantify** whatever can be quantified; show formula, units and result.
5. **Record assumptions** with source and confidence.
6. **Check traceability:** can each statement be traced to a source and forward
   to its use?
7. **Challenge:** a peer, mentor or your own sceptical-reviewer role.
8. **Revise** and keep the final version in your notes.

### 3.5 Suggested schedule

About **4 weeks at 6–8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 1 (stakeholders, business requirements) · Topic 2 (functional and non-functional requirements) |
| 2 | Topic 3 (volume, velocity, variety, growth) · Topic 4 (latency, throughput, freshness, availability) |
| 3 | Topic 5 (constraints, assumptions, dependencies, risks) · Topic 6 (trade-offs and criteria) |
| 4 | Topic 7 (ADRs) · practice questions · project |

Keep a `module-2d2-notes.md` outside the repository's topic files: a summary,
one worked scenario and open questions per topic. These feed the project.

---

## 4. Detailed learning roadmap for each topic file

Each module below uses the same twelve sub-headings. Levels are cumulative.
Examples use the **illustrative** scenario of *Northbridge Bank*, a fictional
mid-sized bank (Section 7.2).

---

### Module 1 — [Stakeholder discovery and business requirements](01-stakeholder-discovery-and-business-requirements.md)

#### 1.1 Learning objectives

- Identify stakeholders, their interests, influence and decision authority.
- Elicit business goals, problems and outcomes using appropriate techniques.
- Separate stated requests from underlying needs.
- Translate business problems into data-related requirements.
- Define scope, exclusions and success criteria.
- Record conflicts and unresolved questions.
- Validate requirements and establish traceability from business objectives.

#### 1.2 Why the topic matters in real-world Data Architecture

Most architecture failures originate upstream of design: a request was taken
literally, a stakeholder was missed, a conflict was hidden, or "done" was never
defined. Discovery determines whether the rest of the module's work solves the
right problem.

#### 1.3 Prerequisite concepts

2D.1 Topics 1–3 (stakeholders, role boundaries, capabilities and domains).

#### 1.4 Beginner-level learning sequence

1. **Define the terms:** stakeholder, business goal, business problem, desired
   outcome, business requirement, scope, success criterion.
2. **Categorise stakeholders:** sponsor, decision-maker, business owner, data
   producer, data consumer, operator, control function (risk, compliance,
   security, audit).
3. **Learn the techniques:** interviews, workshops, questionnaires, document
   analysis, observation of existing reports and processes. Learn what each is
   good and poor at.
4. **Distinguish request from need** using the "why" ladder: ask why until a
   business outcome appears.
5. **Questions to answer:** Why is "build a dashboard" not a requirement? Who
   is usually missing from the first stakeholder list?
6. **Exercise:** From a three-sentence request, list the stakeholders you
   would approach and one question for each.

**Ability to demonstrate:** produce a stakeholder list and five good open
questions from a short request.

#### 1.5 Intermediate-level learning sequence

1. **Build a stakeholder register:** stakeholder, role, interest, influence,
   decision rights, attitude, communication preference (keep fields minimal).
2. **Plan elicitation:** choose the technique per stakeholder; prepare
   questions on goals, current process, pain, volumes, deadlines, risks and
   "what would make this fail".
3. **Run a hypothetical interview** (written transcript, role-played or from a
   supplied case): capture statements verbatim, then classify each as goal,
   need, request, constraint, assumption or solution preference.
4. **Map to capabilities, processes, consumers and decision-makers** (2D.1
   Topic 3) so each requirement has a business home.
5. **Define scope:** in scope, out of scope, boundaries, success criteria
   expressed as observable outcomes.
6. **Record conflicts and open questions** in a log with an owner for each.
7. **Questions to answer:** Which statement is a solution disguised as a
   requirement? What information is missing before design can start?
8. **Exercise:** Analyse three supplied stakeholder statements and produce a
   structured requirements summary (need, requirement, source, priority,
   open question).

**Ability to demonstrate:** a structured summary that separates needs from
requests and lists what is still unknown.

#### 1.6 Advanced-level learning sequence

1. **Conflicting priorities:** identify where two stakeholders want
   incompatible outcomes (for example marketing wants broad access to customer
   data; compliance wants strict minimisation). Frame the conflict by interests,
   not positions; propose options and the decision forum.
2. **Ambiguity:** convert vague goals into candidate measures and ask the
   stakeholder to confirm or correct them. Record the version they accept.
3. **Hidden stakeholders and silent requirements:** operations, support,
   internal audit, regulators, downstream teams, future maintainers.
4. **Validation:** play the requirements back; use walk-throughs and sign-off
   for material items; record who validated what and when.
5. **Traceability:** assign IDs so every requirement links up to a business
   objective and down to later artefacts (Section 5.4).
6. **Questions to answer:** Which requirement would you refuse to accept
   without more evidence? How do you handle a sponsor who has already chosen a
   technology?
7. **Exercise:** For a deliberately conflicting set of stakeholder inputs,
   produce a conflict log with options, a recommended resolution path and the
   evidence you would need.

**Ability to demonstrate:** manage conflict and ambiguity without silently
choosing a side.

#### 1.7 Industry-application exercises

- Prepare an elicitation plan for the Northbridge scenario covering at least six
  stakeholder groups.
- Write a one-page business requirements summary for the "single customer
  count" problem: objectives, scope, exclusions, success criteria, open
  questions.
- Prepare a validation session agenda and a record template.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* The head of marketing asks for "all customer data in one
   place". Identify at least four questions before accepting this as a
   requirement.
2. *Scenario:* Risk and finance each state a different customer count and each
   insists theirs is correct. How do you frame the discovery work?
3. *Scenario:* A key stakeholder is unavailable until after the design
   deadline. What do you record, and which decisions do you make conditional?

#### 1.9 Expected outputs and deliverables

- Stakeholder register.
- Interview plan and (hypothetical) interview record.
- Business requirements summary with scope, exclusions and success criteria.
- Conflict and open-questions log.
- Answers to Topic 1 practice questions.

#### 1.10 Common mistakes and misconceptions

- Recording solutions as requirements.
- Interviewing only the sponsor.
- Treating silence as agreement.
- Writing success criteria as activities ("deliver a data lake").
- Resolving conflicts by seniority.
- Not recording who confirmed a requirement.

#### 1.11 Mastery criteria

- Distinguishes request, need, requirement, constraint and solution preference.
- Produces a requirements summary with source, scope, success criteria and
  explicit open questions.
- Frames a stakeholder conflict by interests and proposes a resolution path.

#### 1.12 Completion gate

- [ ] Stakeholder register and elicitation plan reviewed.
- [ ] Requirements summary contains no unlabelled solutions and no
      unmeasurable success criteria.
- [ ] Conflict log complete with owners and evidence needs.
- [ ] Topic 1 practice questions answered and corrected.

---

### Module 2 — [Functional and non-functional requirements](02-functional-and-non-functional-requirements.md)

#### 2.1 Learning objectives

- Classify requirements as business, functional, non-functional, data or
  constraint.
- Write measurable, testable requirement statements with acceptance criteria.
- Prioritise requirements and identify conflicts and dependencies.
- Validate requirements for ambiguity, completeness and consistency.
- Maintain traceability from business requirement to architectural decision.

#### 2.2 Why the topic matters in real-world Data Architecture

Functional requirements say what the data capability must do; non-functional
requirements say how well. Architecture is mostly shaped by the second kind. A
design that meets every functional requirement and none of the non-functional
ones is a failed design.

#### 2.3 Prerequisite concepts

Module 1 here; 2D.1 Topic 4 (quality attributes).

#### 2.4 Beginner-level learning sequence

1. **Define the levels:** business requirement (outcome), system/data
   requirement (capability), functional requirement (behaviour), non-functional
   requirement (quality), constraint (restriction).
2. **Walk through the data lifecycle** to prompt functional requirements:
   ingestion, validation, transformation, storage, access, sharing, retention,
   deletion.
3. **List quality attributes** to prompt non-functional requirements:
   reliability, availability, scalability, performance, security, privacy,
   interoperability, maintainability, cost, auditability.
4. **Recognise vague wording:** "fast", "secure", "scalable", "real-time",
   "user-friendly".
5. **Questions to answer:** Is "reports must run quickly" functional or
   non-functional? What makes a requirement testable?
6. **Exercise:** Classify twenty supplied statements and mark each as
   measurable or not.

**Ability to demonstrate:** classify correctly and identify what is missing from
a vague statement.

#### 2.5 Intermediate-level learning sequence

1. **Use a requirement template:** *the [system/data capability] shall
   [behaviour] for [scope] under [conditions], measured by [metric] with target
   [value], verified by [method].*
2. **Rewrite vague statements into measurable ones.**
   *Illustrative example:* "The risk report must be fast" becomes "The daily
   credit-exposure report shall be available to risk analysts by 07:00 local
   time on every business day, 99% of business days over a rolling quarter,
   measured by the report-completion timestamp."
3. **Write acceptance criteria:** a pass/fail condition, test data or scenario,
   and who accepts it.
4. **Prioritise** with a simple scheme (for example must / should / could) and
   state the criteria used; avoid everything being "must".
5. **Trace** each requirement to its business objective and source
   stakeholder.
6. **Identify dependencies and conflicts** (for example low latency versus
   strict validation).
7. **Questions to answer:** How will this be tested? Who accepts it? Which
   other requirement does it constrain?
8. **Exercise:** Write twelve requirements (six functional, six
   non-functional) for the Northbridge customer-data problem, each with
   acceptance criteria and a source.

**Ability to demonstrate:** a requirements set where every item is classified,
measurable, testable and sourced.

#### 2.6 Advanced-level learning sequence

1. **Quality-check requirements** against: unambiguous, atomic, testable,
   consistent, feasible, necessary, traceable. Review the set for completeness
   across the data lifecycle and across quality attributes.
2. **Resolve conflicts:** identify pairs (strict privacy versus broad
   analytical access; low latency versus completeness; low cost versus high
   availability). State the priority rule and who decides.
3. **Treat requirements as architecture constraints:** identify which
   non-functional requirements are *architecturally significant* because they
   drive structure (for example recovery time, data residency, freshness).
4. **Handle changing requirements:** version, impact analysis, and re-validation
   of dependent decisions.
5. **Avoid over-specification:** requirements should not smuggle in the design.
6. **Questions to answer:** Which five requirements most constrain the
   architecture, and why? Which could be relaxed with the least business harm?
7. **Exercise:** Review a flawed requirements set, list defects by category,
   rewrite it, and identify the architecturally significant items.

**Ability to demonstrate:** review a requirements set for defects and identify
the requirements that drive the design.

#### 2.7 Industry-application exercises

- Produce a requirements register (fields in Section 7.5) for the customer
  consolidation problem.
- Build a first requirement traceability matrix: business objective →
  requirement → acceptance criterion.
- Run a "vague word hunt" over a provided requirements paragraph.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* "The platform must be highly available." Produce three
   candidate measurable versions and the questions that choose between them.
2. *Scenario:* Two requirements conflict: row-level restriction of sensitive
   data and a requirement that analysts can query all customer attributes. How
   do you proceed?
3. *Scenario:* A regulator-driven requirement arrives late. How do you assess
   which existing decisions it affects?

#### 2.9 Expected outputs and deliverables

- Requirements register with classification, priority and acceptance criteria.
- Requirement traceability matrix (first version).
- Defect review of a flawed requirements set.
- Answers to Topic 2 practice questions.

#### 2.10 Common mistakes and misconceptions

- Mixing functional and non-functional requirements in one sentence.
- Writing requirements as designs ("use Kafka").
- Using adjectives instead of metrics.
- Marking everything top priority.
- Treating acceptance criteria as optional.
- Ignoring requirement interactions.

#### 2.11 Mastery criteria

- Classifies requirements correctly and consistently.
- Writes measurable, testable, traceable requirements.
- Identifies conflicts, dependencies and architecturally significant items.

#### 2.12 Completion gate

- [ ] Every requirement in the register has type, priority, source and
      acceptance criterion.
- [ ] No "must" requirement is unmeasurable without an explicit justification.
- [ ] Defect review shows the categories of defects found and fixed.
- [ ] Topic 2 practice questions answered and corrected.

---

### Module 3 — [Data volume, velocity, variety and growth estimation](03-data-volume-velocity-variety-and-growth-estimation.md)

#### 3.1 Learning objectives

- Estimate current and future data volumes with formulas, units and assumptions.
- Characterise arrival rates, bursts and seasonality.
- Distinguish raw, processed, replicated and retained data.
- Classify structured, semi-structured and unstructured data and its size
  implications.
- Express uncertainty as ranges and translate estimates into architecture
  implications.

#### 3.2 Why the topic matters in real-world Data Architecture

Volume and rate shape storage, compute, network, cost and technology fit. A
wrong order of magnitude changes the design; an unlabelled guess presented as a
fact misleads a whole programme. The skill is not precision but a defensible
range with stated assumptions.

#### 3.3 Prerequisite concepts

Modules 1–2 here; basic units and arithmetic.

#### 3.4 Beginner-level learning sequence

1. **Learn the units:** bit, byte, KB/MB/GB/TB/PB. State whether you use
   decimal (10³) or binary (2¹⁰) multiples and keep it consistent (this roadmap
   uses decimal: 1 GB = 10⁹ bytes unless stated).
2. **Learn the "three Vs" plus the quality of each:** volume (how much),
   velocity (how fast it arrives), variety (what forms).
3. **Classify data:** structured (tables), semi-structured (JSON, XML, logs),
   unstructured (documents, images, audio).
4. **Learn the basic formula:**

   ```text
   daily_volume = records_per_day × average_record_size
   ```

5. **Questions to answer:** Why does the same record occupy different sizes in
   a database, a CSV file and a compressed columnar file?
6. **Exercise (illustrative):** 2,000,000 transactions per day × 500 bytes per
   record = 1,000,000,000 bytes/day = 1.0 GB/day. Show the units at each step.

**Ability to demonstrate:** compute a daily volume with correct units and state
the assumptions used.

#### 3.5 Intermediate-level learning sequence

1. **Estimate record, event and file sizes:** field-by-field sizing; account for
   keys, timestamps, nulls and overhead; sample real data where available and
   say so.
2. **Distinguish the data layers:** raw (as received), processed (cleaned,
   modelled), replicated (copies for availability or distribution), retained
   (history kept), archived. Apply a multiplier to each:

   ```text
   total_storage = Σ (layer_volume × copies × (1 + overhead_factor))
   ```

3. **Calculate growth:**

   ```text
   monthly_volume  = daily_volume × days_in_month
   annual_volume   = daily_volume × 365
   volume_at_year_n = V0 × (1 + g)^n          # compound annual growth rate g
   cumulative_n    = Σ annual_volume_i        # with retention policy applied
   ```

4. **Apply retention:** only data inside the retention window is held
   in the primary tier; show the effect of a retention change.
5. **Estimate rates:**

   ```text
   average_rate  = daily_events / 86,400 s
   peak_rate     = average_rate × peak_factor     # state and justify peak_factor
   ```

6. **Characterise workloads:** batch (volume per window, window length),
   streaming (events per second, event size, ordering, retention in the log).
7. **Questions to answer:** Which input has the widest uncertainty? What
   changes if retention doubles? Is storage or ingestion rate the binding
   limit?
8. **Exercise (illustrative):** Estimate three-year storage for transactions,
   card events and customer-profile changes with retention, replication and
   compression assumptions stated.

**Ability to demonstrate:** a worksheet with formulas, units, assumptions and an
interpretation sentence for each result.

#### 3.6 Advanced-level learning sequence

1. **Peaks, bursts, seasonality:** payroll days, month-end close, holiday
   trading, batch catch-up after an outage. Estimate peak factor from
   historical patterns, not intuition.
2. **Uncertainty ranges:** give low / expected / high cases and the assumption
   each depends on; identify the most sensitive input by varying one at a time.

   ```text
   low  = V0 × (1 + g_low)^n
   high = V0 × (1 + g_high)^n
   ```

3. **Capacity versus data size:** distinguish data at rest, data in motion
   (network), and data in processing (memory, shuffle, indexes); do not size
   compute from storage alone.
4. **Variety implications:** semi-structured and unstructured data affect
   parsing cost, schema management, searchability and storage layout.
5. **Evidence quality:** label each input as measured, sampled, vendor-stated,
   estimated or guessed; give lower confidence to the last two.
6. **Sanity checks:** compare against known system capacities or invoices;
   cross-check with an independent method (for example bottom-up versus
   top-down).
7. **Translate to architecture implications:** which technology classes become
   plausible or implausible at this scale, what must be partitioned, what must
   be tiered, and which assumptions must be validated before commitment.
8. **Questions to answer:** Which estimate would change a decision if it were
   10× larger? Which could you leave rough?
9. **Exercise (illustrative):** For a streaming source, produce a peak-load and
   a three-year capacity estimate with a range and a sensitivity ranking.

**Ability to demonstrate:** an estimate with a range, a sensitivity ranking, an
evidence-quality label for each input and architecture implications.

#### 3.7 Industry-application exercises

- Produce a volume and growth worksheet (fields in Section 7.5) for the
  Northbridge platform, marking every figure as illustrative.
- Estimate the effect on cost-driving volume of changing retention from
  seven years to ten years, with all else equal.
- Write a half-page note stating which estimates are good enough to proceed and
  which must be validated first.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* A source team reports "about a million events a day". Identify
   five follow-up questions before using the number.
2. *Scenario:* Month-end volumes are four times the daily average for three
   days. How does this change ingestion design and the way you report the
   requirement?
3. *Scenario:* Two estimates differ by a factor of five. How do you find out
   why before choosing?

#### 3.9 Expected outputs and deliverables

- Volume, velocity, variety and growth worksheet.
- Range and sensitivity analysis.
- Architecture implications note.
- Answers to Topic 3 practice questions.

#### 3.10 Common mistakes and misconceptions

- Mixing GB and GiB, bits and bytes, per-second and per-day.
- Ignoring replication, indexes and retention.
- Using one point estimate and presenting it as certain.
- Forgetting peaks and sizing for the average.
- Treating growth as linear when it is compounding.
- Presenting guessed numbers as facts.

#### 3.11 Mastery criteria

- All estimates show formula, units, assumptions and interpretation.
- Ranges and a sensitivity ranking accompany material estimates.
- Evidence quality is labelled; illustrative values are marked as such.

#### 3.12 Completion gate

- [ ] Worksheet independently recomputed by a reviewer with the same results.
- [ ] Units are consistent throughout; conversions are shown.
- [ ] Each material input has a source label and confidence.
- [ ] Topic 3 practice questions answered and corrected.

---

### Module 4 — [Latency, throughput, freshness and availability targets](04-latency-throughput-freshness-and-availability-targets.md)

#### 4.1 Learning objectives

- Define latency, throughput, freshness and availability precisely, and choose
  the right metric for a requirement.
- Convert statements such as "real-time" into measurable, scoped targets.
- Use percentiles and explain peak versus average.
- Reason about end-to-end pipeline timing and bottlenecks.
- Validate whether targets are measurable, consistent and achievable.

#### 4.2 Why the topic matters in real-world Data Architecture

Operational targets are the strongest drivers of architecture and cost. A
single unexamined word ("real-time", "always on") can multiply cost many times
over or send a design in the wrong direction. Precise targets let you design
for what is needed, no more.

#### 4.3 Prerequisite concepts

Modules 2–3 here; 2D.1 Topic 4 (quality attributes).

#### 4.4 Beginner-level learning sequence

1. **Define each metric:**
   - *Latency:* time between a request or event and its observable result.
   - *Throughput:* amount processed per unit time (records/s, MB/s, jobs/hour).
   - *Freshness:* age of the data visible to the consumer relative to the
     real-world event (or source timestamp).
   - *Availability:* proportion of time a service meets its stated
     expectation.
2. **Learn that they are different:** a system can have low latency and stale
   data; high throughput and high latency.
3. **Learn the availability arithmetic:**

   ```text
   availability = uptime / (uptime + downtime)
   allowed_downtime = (1 − target) × period
   ```

   *Illustrative:* 99.9% over a 30-day month = 0.001 × 43,200 min ≈ 43.2 min.
   99.99% ≈ 4.3 min. 99% ≈ 7.2 h.
4. **Questions to answer:** What is the difference between latency and
   freshness for a dashboard? Why is 100% availability not a sensible target?
5. **Exercise:** Compute allowed monthly and annual downtime for 99%, 99.5%,
   99.9% and 99.99%.

**Ability to demonstrate:** define each metric and compute allowed downtime.

#### 4.5 Intermediate-level learning sequence

1. **Decompose end-to-end timing** for a pipeline:

   ```text
   end_to_end_freshness = t_source_commit + t_extract + t_transport
                        + t_process + t_load + t_publish
   ```

   Identify which stage you control and which you do not.
2. **Batch versus streaming:** batch window (start, duration, deadline);
   streaming latency; micro-batch. State what "within X" means for each.
3. **Use percentiles:** median, p95, p99 and why averages hide tail behaviour.
   Specify the percentile and the measurement window.
4. **Peak versus average throughput:**

   ```text
   required_throughput ≥ peak_rate × safety_factor
   ```

   State the safety factor and basis; connect to Module 3 peak estimates.
5. **Write a service-level objective (SLO)** with: indicator, target,
   measurement window, scope, measurement method, exclusions (for example
   planned maintenance).
6. **Convert vague statements.** From "data must be real-time" ask: for whom,
   for which decision, what delay is harmful, what happens beyond it, at what
   percentile, during which hours? *Illustrative result:* "p95 freshness
   ≤ 30 s from authorisation to availability in the case tool, 08:00–20:00
   local, measured per transaction."
7. **Questions to answer:** Would a 5-minute delay change the decision the
   user makes? What does each additional "nine" of availability cost?
8. **Exercise:** For five Northbridge consumers (fraud analyst, risk reporting,
   regulatory submission, marketing segmentation, executive dashboard), write
   one measurable target each, with a justification.

**Ability to demonstrate:** a table of workload-specific, measurable targets
with indicator, percentile, window, scope and measurement method.

#### 4.6 Advanced-level learning sequence

1. **Interdependence:** latency, throughput, reliability and cost trade against
   one another. Stricter freshness raises cost and operational burden; higher
   availability needs redundancy, more complex failure handling and tested
   recovery.
2. **Compose availability:** for serial dependencies, availability multiplies;
   for redundant parallel components, unavailability multiplies.

   ```text
   serial:   A = A1 × A2 × … × An
   parallel: A = 1 − (1 − A1) × (1 − A2)
   ```

   *Illustrative:* three serial components at 99.9% give ≈ 99.7%. Use this to
   test whether a target is achievable with the proposed dependencies.
3. **Tail latency and queueing:** utilisation near capacity inflates tail
   latency; explain why headroom is part of the target.
4. **Bottlenecks and operational constraints:** slowest stage, single-writer
   limits, source system windows, rate limits, batch dependency chains.
5. **Targets differentiated by data:** not every dataset needs the same
   target; tier by business criticality.
6. **Validate targets:** can it be measured today? By what instrument? Is the
   target achievable given upstream dependencies? Is it internally consistent
   with volume, retention and cost expectations?
7. **Error budget (introductory):** allowed failure under the SLO as a basis for
   deciding how much risk to accept for change.
8. **Questions to answer:** What would you ask the business to relax first?
   Which target is unachievable given a stated dependency?
9. **Exercise:** Take a set of targets, detect two that are mutually
   inconsistent or unachievable given a dependency chain, and propose
   defensible alternatives.

**Ability to demonstrate:** a set of targets that is measurable, consistent and
tested for achievability, with the trade-offs stated.

#### 4.7 Industry-application exercises

- Produce the performance and service-target specification for the Northbridge
  scenario (fields in Section 7.5), marking all values illustrative.
- Build a timing budget for the fraud-case path with a target per stage that
  sums to the end-to-end target.
- Explain to a business stakeholder, in one paragraph, why "real-time" was
  replaced by a percentile target.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* The business asks for 99.99% availability for a reporting
   service used on business days only. Which questions reduce the cost of the
   requirement without harming the business?
2. *Scenario:* The upstream core banking extract is available only after a
   nightly batch at 02:30. How does this constrain freshness targets?
3. *Scenario:* A dashboard meets its average-latency target but users complain.
   What do you measure next?

#### 4.9 Expected outputs and deliverables

- Metric definitions and a vague-to-measurable conversion table.
- Service-target specification with SLOs.
- End-to-end timing budget.
- Availability composition calculation.
- Answers to Topic 4 practice questions.

#### 4.10 Common mistakes and misconceptions

- Equating "real-time" with a single technology.
- Quoting averages instead of percentiles.
- Setting availability targets without examining dependencies.
- Confusing latency with freshness.
- Specifying targets that cannot be measured.
- Giving every dataset the same strict target.

#### 4.11 Mastery criteria

- Defines targets with indicator, percentile, window, scope and measurement
  method.
- Computes allowed downtime and composes availability correctly.
- Validates measurability and achievability of targets and states trade-offs.

#### 4.12 Completion gate

- [ ] Every target is measurable and names its measurement method.
- [ ] Timing budget stages sum to the end-to-end target.
- [ ] Availability composition checked against the dependency chain.
- [ ] Topic 4 practice questions answered and corrected.

---

### Module 5 — [Constraints, assumptions, dependencies and risks](05-constraints-assumptions-dependencies-and-risks.md)

#### 5.1 Learning objectives

- Distinguish facts, constraints, preferences, assumptions, dependencies, risks
  and unknowns.
- Identify technical, business, organisational, regulatory, operational and
  financial constraints.
- Assess risks by probability and impact; plan mitigation and escalation.
- Validate assumptions and assign ownership.
- Trace constraints and risks into architecture decisions and manage change to
  them.

#### 5.2 Why the topic matters in real-world Data Architecture

Most architecture is shaped less by what is desired than by what is fixed,
believed or at risk. Treating an assumption as a fact is among the most
common causes of costly rework. This topic gives the problem its boundaries
and its honesty.

#### 5.3 Prerequisite concepts

Modules 1–4 here; 2D.1 Topic 4 (business drivers, constraints, assumptions)
and Topic 5 (exceptions).

#### 5.4 Beginner-level learning sequence

1. **Define the terms with a one-line test each:**

   | Term | Test |
   | --- | --- |
   | Fact | Evidence exists and can be shown |
   | Constraint | Fixed limit the solution must respect |
   | Preference | Wanted but negotiable |
   | Assumption | Believed true, not yet verified |
   | Dependency | Something the solution needs from outside its control |
   | Risk | Uncertain event that could affect objectives |
   | Unknown | Information missing |

2. **Learn constraint categories:** technical, business, organisational,
   regulatory, operational, financial, time.
3. **Learn that a dependency can become a risk** when it is late or
   unreliable.
4. **Questions to answer:** Is "we will use the existing identity provider" a
   constraint, an assumption or a preference? How do you tell?
5. **Exercise:** Classify twenty statements into the seven categories above.

**Ability to demonstrate:** classify statements correctly and explain the test
used.

#### 5.5 Intermediate-level learning sequence

1. **Separate fixed constraints from negotiable preferences** by asking: who
   can change it, at what cost, by when?
2. **Surface implicit assumptions:** "the source system will provide a change
   feed", "volumes will grow 10% a year", "the team will have two more
   engineers". Write each as a statement with an owner and a validation
   method.
3. **Map dependencies:** internal (teams, platforms, shared services) and
   external (vendors, regulators, data providers); show a simple dependency
   diagram and the critical path.
4. **Assess risks:**

   ```text
   exposure = probability × impact        # use ordinal scales (1–5) if numbers are unavailable
   ```

   State the scales and avoid false precision.
5. **Plan responses:** avoid, mitigate, transfer, accept; name a trigger and an
   owner; define a contingency and an escalation path.
6. **Identify missing information** and decide which unknowns block a decision
   and which do not.
7. **Questions to answer:** Which assumption, if wrong, would invalidate the
   design? Which dependency has no owner?
8. **Exercise:** For the Northbridge scenario, produce a register of at least
   ten items covering all categories, each correctly labelled.

**Ability to demonstrate:** a correctly classified register with owners and
validation methods.

#### 5.6 Advanced-level learning sequence

1. **Interacting risks:** a late source feed (dependency) combined with a fixed
   regulatory date (constraint) raises exposure of several requirements; show
   the interaction explicitly.
2. **Assumption management:** rank assumptions by impact-if-wrong and
   confidence; validate the high-impact, low-confidence ones first; set a date
   by which each must be validated; define what happens if it fails.
3. **Documenting uncertainty:** distinguish "unknown" from "unknowable now";
   give ranges and decision triggers rather than false certainty.
4. **Architectural consequences of change:** when a constraint is relaxed or an
   assumption fails, which decisions must be reopened? Maintain links to
   decisions so impact analysis is possible.
5. **Constraints as design drivers:** show how a regulatory data-residency
   constraint, a legacy batch window or a budget ceiling removes options
   before any comparison begins.
6. **Challenge constraints:** test whether an apparent constraint is really a
   preference; record the outcome and who agreed.
7. **Questions to answer:** Which constraint most limits your options, and who
   can change it? Which risk would you escalate today?
8. **Exercise:** Take a decision from the project, list the constraints and
   assumptions it depends on, and write the triggers that would cause it to be
   revisited.

**Ability to demonstrate:** a register in which each item links to the
decisions it affects, with validation dates and revisit triggers.

#### 5.7 Industry-application exercises

- Build the constraints, assumptions, dependencies and risks register (fields
  in Section 7.5) for the Northbridge scenario.
- Produce a dependency map for the customer-consolidation programme with the
  critical path highlighted.
- Write an escalation note for a high-exposure risk with options and a
  recommended decision.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* The vendor says an API will be available "next quarter".
   Classify the statement and describe how you plan around it.
2. *Scenario:* An internal policy prohibits copying personal data outside the
   production region. Constraint or preference? Who can change it?
3. *Scenario:* A key assumption (stable source schemas) fails during design.
   Which artefacts do you re-open?

#### 5.9 Expected outputs and deliverables

- Constraints, assumptions, dependencies and risks register.
- Dependency map with critical path.
- Assumption validation plan.
- Answers to Topic 5 practice questions.

#### 5.10 Common mistakes and misconceptions

- Using the terms interchangeably.
- Treating preferences as constraints, or the reverse.
- Leaving assumptions unwritten and unowned.
- Rating risks without scales or evidence.
- Recording risks with no mitigation, owner or trigger.
- Not linking constraints and risks to decisions.

#### 5.11 Mastery criteria

- Classifies items correctly and explains the test.
- Assesses risk with stated scales and plans responses with owners.
- Maintains traceability from constraints, assumptions and risks to decisions.

#### 5.12 Completion gate

- [ ] Register complete; no item is unclassified or ownerless.
- [ ] Each high-exposure item has a response, an owner and a trigger.
- [ ] Each high-impact assumption has a validation method and date.
- [ ] Topic 5 practice questions answered and corrected.

---

### Module 6 — [Architecture trade-offs and decision criteria](06-architecture-trade-offs-and-decision-criteria.md)

#### 6.1 Learning objectives

- Define the architecture problem and the decision scope.
- Derive decision criteria from requirements and constraints.
- Identify feasible alternatives and compare them on explicit criteria.
- Use quantitative and qualitative methods, including weighted scoring, and
  state their limits.
- Perform cost-benefit and sensitivity analysis.
- Assess reversibility, lock-in and long-term consequences.
- Recommend and communicate a decision, including what is traded away.

#### 6.2 Why the topic matters in real-world Data Architecture

Architecture is the discipline of choosing under competing demands. The same
requirements can support more than one defensible design; what makes a
recommendation credible is the visible reasoning: criteria, evidence, accepted
trade-offs and conditions under which the answer would change.

#### 6.3 Prerequisite concepts

Modules 1–5 here; 2D.1 Topic 4 (trade-offs between quality attributes) and
Topic 6 (framework suitability criteria).

#### 6.4 Beginner-level learning sequence

1. **Define the decision:** a question, the scope (what is decided and what is
   not), the deadline and the decision-maker.
2. **Learn criteria types:** requirements-based (must), quality-based (how well),
   cost, time, risk, operability, strategic fit.
3. **Distinguish must-have gates from scored criteria.** An option that fails a
   must-have is eliminated, not scored.
4. **Generate real alternatives:** at least three feasible options, including
   "do nothing/minimal change" as a baseline.
5. **Questions to answer:** Why is an option that misses a hard constraint not
   an alternative? Why include the baseline?
6. **Exercise:** For "how should the fraud case tool receive card
   transactions?", state the decision, five criteria and three alternatives.

**Ability to demonstrate:** frame a decision and list feasible alternatives
with criteria.

#### 6.5 Intermediate-level learning sequence

1. **Build a comparison matrix** with criteria as rows, options as columns, and
   evidence in each cell (not just ratings).
2. **Use weighted scoring** with an explicit method:

   ```text
   score(option) = Σ ( weight_i × rating_i(option) )     with Σ weight_i = 1
   ```

   Define the rating scale and what each score means; record where each rating
   comes from.
3. **State the limits of weighted scoring:** weights are subjective, criteria
   may be correlated (double counting), scores hide must-have failures, and
   small score differences are noise.
4. **Quantify where possible:** cost (build, run, people), time to deliver,
   latency, capacity. Keep qualitative judgements qualitative and labelled.
5. **Simple cost model:**

   ```text
   TCO_n_years = build_cost + Σ_{t=1..n} (run_cost_t + support_cost_t) + exit_cost
   ```

   Include people and migration costs, not just licences or cloud charges.
6. **Questions to answer:** Which criteria discriminate between options and
   which are the same for all? Where is the evidence weakest?
7. **Exercise (illustrative):** Compare three options for the fraud path with a
   matrix, weights, evidence and a short written conclusion.

**Ability to demonstrate:** a matrix in which every rating is traceable to
evidence and the conclusion is stated in words.

#### 6.6 Advanced-level learning sequence

1. **Conflicting quality attributes:** show explicitly what each option gives up
   (for example lower latency at higher operational burden).
2. **Sensitivity analysis:** vary each weight and each uncertain input; identify
   the point at which the ranking changes.

   ```text
   for each input x: recompute score(option) for x_low, x_base, x_high
   report: does the preferred option change? at what value?
   ```

3. **Uncertainty across options:** give ranges rather than points; prefer the
   option that is acceptable across the plausible range if the cost of being
   wrong is high (robustness) over the one that is best only under optimistic
   assumptions.
4. **Reversibility and lock-in:** classify decisions as easy to reverse or hard;
   estimate exit and migration cost; consider staged commitment, a pilot or an
   option that preserves choice.
5. **Long-term consequences:** operational burden, skills, upgrade path,
   vendor viability, regulatory change.
6. **Cost-benefit analysis:** state benefits in measurable terms (avoided loss,
   time saved), include the cost of delay and of doing nothing.
7. **Communication:** write the recommendation for two audiences: a technical
   reviewer (criteria, evidence, sensitivity) and a business sponsor (outcome,
   cost, risk, what we are accepting).
8. **Questions to answer:** Under what assumptions is the preferred option
   best? What would make you choose the runner-up? What are we explicitly
   accepting?
9. **Exercise:** Repeat the Intermediate comparison with ranges, run a
   sensitivity analysis, and write both versions of the recommendation.

**Ability to demonstrate:** a recommendation stating why it is preferred, under
which assumptions, what trade-offs are accepted and what would change it.

#### 6.7 Industry-application exercises

- Produce the architecture decision criteria and prioritisation method for the
  Northbridge decision set, including must-have gates.
- Compare alternatives for one major decision and write the trade-off analysis
  (Section 7.4).
- Run a sensitivity analysis on the two least certain inputs.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* The cheapest option misses the freshness target by a small
   margin. How do you handle it: gate, score, or negotiate the target?
2. *Scenario:* Two options score within 3% of each other. What do you do?
3. *Scenario:* The preferred option depends on a vendor commitment not yet
   made. How do you structure a conditional decision?

#### 6.9 Expected outputs and deliverables

- Decision statement with scope and criteria.
- Comparison matrix with evidence.
- Sensitivity analysis.
- Recommendation for technical and business audiences.
- Answers to Topic 6 practice questions.

#### 6.10 Common mistakes and misconceptions

- Constructing straw-man alternatives to make a favourite win.
- Treating scores as precise measurements.
- Choosing weights after seeing the totals.
- Ignoring people, migration and exit costs.
- Ignoring reversibility.
- Omitting what the chosen option gives up.

#### 6.11 Mastery criteria

- Frames a decision with scope, gates and criteria derived from requirements.
- Compares real alternatives with evidence and runs a sensitivity check.
- States assumptions, accepted trade-offs and conditions for reversal.

#### 6.12 Completion gate

- [ ] Every criterion traces to a requirement, constraint or principle.
- [ ] Matrix ratings cite evidence; sensitivity analysis completed.
- [ ] Recommendation states assumptions, trade-offs and reversal conditions.
- [ ] Topic 6 practice questions answered and corrected.

---

### Module 7 — [Architecture decision records (ADRs)](07-architecture-decision-records-adrs.md)

#### 7.1 Learning objectives

- Explain the purpose of ADRs and decide which decisions to record.
- Write ADRs with context, drivers, options, outcome, rationale and
  consequences.
- Record rejected alternatives, uncertainty and unresolved issues.
- Link ADRs to requirements, constraints, assumptions, risks and criteria.
- Manage ADR status and lifecycle, including superseding and revisiting.
- Communicate decisions and maintain a coherent decision history.

#### 7.2 Why the topic matters in real-world Data Architecture

Without a record, decisions are re-argued, rationale is forgotten when people
leave, and no one can tell whether a past decision still holds. An ADR makes the
reasoning durable, reviewable and revisable.

#### 7.3 Prerequisite concepts

Modules 1–6 here; 2D.1 Topic 5 (decision records and exceptions).

#### 7.4 Beginner-level learning sequence

1. **Learn the purpose:** capture one significant decision, its context and
   consequences so a future reader can understand and challenge it.
2. **Learn when to write one:** the decision is hard to reverse, affects
   multiple teams or quality attributes, resolves a real trade-off, or would
   be asked about later. Do not write ADRs for trivial choices.
3. **Learn the basic structure.** The repository mandates no template, so this
   roadmap proposes:

   ```markdown
   # ADR-NNN: <short decision title>

   - Status: Proposed | Accepted | Deprecated | Superseded by ADR-MMM
   - Date: YYYY-MM-DD
   - Decision owner / deciders:
   - Related: REQ-…, CON-…, ASM-…, RSK-…, other ADRs

   ## Context
   ## Decision drivers (criteria)
   ## Considered options
   ## Decision outcome
   ## Rationale
   ## Consequences (positive, negative, accepted trade-offs)
   ## Rejected alternatives and reasons
   ## Assumptions and conditions for revisiting
   ## Open issues and dependencies
   ```

   This is a suggestion for study; keep it only if it serves you.
4. **Questions to answer:** What distinguishes context from rationale? Why
   record rejected options?
5. **Exercise:** Convert a supplied informal decision email into an ADR.

**Ability to demonstrate:** write a complete, readable ADR for a simple
decision.

#### 7.5 Intermediate-level learning sequence

1. **Write context that stands alone:** a reader a year later should
   understand the problem without asking.
2. **List drivers as criteria** linked to requirement IDs and quality targets.
3. **Record options honestly** with a short pros/cons statement each, and the
   evidence behind them.
4. **State the outcome as a decision, not a discussion;** give rationale that
   cites criteria, not preference.
5. **Document consequences:** positive, negative and the trade-offs explicitly
   accepted.
6. **Link everything:** requirement, constraint, assumption and risk IDs; the
   comparison matrix; related ADRs.
7. **Record unresolved issues and dependencies** and who owns each.
8. **Manage status:** Proposed → Accepted → Deprecated / Superseded. An accepted
   ADR is not edited to change its meaning; it is superseded by a new one that
   references it.
9. **Questions to answer:** Could a reader reproduce the reasoning? Which
   assumption is hidden?
10. **Exercise:** Write three ADRs from the Module 6 comparisons.

**Ability to demonstrate:** ADRs that are standalone, linked and honest about
trade-offs.

#### 7.6 Advanced-level learning sequence

1. **High-impact decisions:** record the evidence, sensitivity result and the
   conditions under which the decision would be revisited.
2. **Conditional decisions:** where evidence is missing, record the decision as
   conditional, name the missing evidence, the owner and the date by which it
   will be settled.
3. **Competing options:** where the choice is close, record why the tie-break
   was made and what was learned in the process.
4. **Uncertainty:** state confidence and what would change it.
5. **Decision history and coherence:** keep a log or index showing status,
   supersession chains and conflicts between ADRs; check that new ADRs do not
   contradict accepted ones without superseding them.
6. **Review practice:** peer review checklist: is the problem clear, are
   options real, are criteria traceable, are consequences honest, are
   assumptions listed, is the status correct?
7. **Communication:** summarise for business audiences; announce to affected
   teams; link from places where engineers will look.
8. **Avoid vague rationale:** "industry standard", "best practice", "more
   scalable" must be replaced by evidence or measurable criteria.
9. **Questions to answer:** Which ADR in your set is weakest, and why? Which
   would you supersede first if one named assumption failed?
10. **Exercise:** Review a flawed ADR, list the defects, rewrite it, and
    supersede an earlier ADR with a new one correctly.

**Ability to demonstrate:** a coherent ADR set with a working status and
supersession chain.

#### 7.7 Industry-application exercises

- Write ADRs for the major decisions in the Northbridge decision pack.
- Build a decision log index with status, date, owner and links.
- Run a review of a colleague's (or your own earlier) ADR with the checklist.

#### 7.8 Practical scenarios and case-based reasoning

1. *Scenario:* A decision was made verbally in a meeting. How do you capture it
   without inventing detail?
2. *Scenario:* An accepted ADR rests on a vendor capability that was
   withdrawn. What do you do?
3. *Scenario:* A team asks to skip ADRs "to go faster". How do you respond with
   proportionality rather than ceremony?

#### 7.9 Expected outputs and deliverables

- ADR set with decision log.
- Review checklist and review notes.
- A superseding example.
- Answers to Topic 7 practice questions.

#### 7.10 Common mistakes and misconceptions

- Writing ADRs after the fact to justify a decision already built.
- Recording only the chosen option.
- Rationale made of adjectives.
- Editing accepted ADRs to hide history.
- One ADR covering many unrelated decisions.
- Unlinked ADRs that cannot be traced to requirements or risks.

#### 7.11 Mastery criteria

- Writes standalone, linked ADRs with real alternatives and honest consequences.
- Records conditions for revisiting and handles status and supersession.
- Reviews ADRs against a checklist and finds genuine defects.

#### 7.12 Completion gate

- [ ] ADR set reviewed; no ADR lacks rejected alternatives or consequences.
- [ ] Every ADR links to requirement, constraint, assumption or risk IDs.
- [ ] Decision log shows status and supersession consistently.
- [ ] Topic 7 practice questions answered and corrected.

---

## 5. Module dependencies and learning order

### 5.1 Dependency table

| # | Topic file | Required prior knowledge | Key concepts learned | Practical output | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `01-stakeholder-discovery-and-business-requirements.md` | 2D.1 Topics 1–3 | Stakeholders, elicitation, need vs request, scope, validation | Stakeholder register, requirements summary, conflict log | Reviewed register and summary with no unlabelled solutions |
| 2 | `02-functional-and-non-functional-requirements.md` | 1 | Classification, measurable statements, acceptance criteria, conflicts | Requirements register, first traceability matrix | Every requirement typed, sourced, testable |
| 3 | `03-data-volume-velocity-variety-and-growth-estimation.md` | 1, 2 | Volume/rate formulas, growth, retention, ranges | Estimation worksheet with sensitivity | Reviewer recomputes the results |
| 4 | `04-latency-throughput-freshness-and-availability-targets.md` | 2, 3 | Metrics, percentiles, SLOs, availability arithmetic | Service-target specification, timing budget | Targets measurable and consistent |
| 5 | `05-constraints-assumptions-dependencies-and-risks.md` | 1–4 | Fact/constraint/assumption/dependency/risk, exposure, validation | Register and dependency map | No unclassified or ownerless item |
| 6 | `06-architecture-trade-offs-and-decision-criteria.md` | 1–5 | Criteria, gates, weighted scoring, sensitivity, reversibility | Comparison matrix and recommendation | Ratings cite evidence; sensitivity done |
| 7 | `07-architecture-decision-records-adrs.md` | 1–6 | ADR structure, lifecycle, linking, supersession | ADR set and decision log | Reviewed ADRs, consistent log |

### 5.2 Recommended order and reasons

1. **Topic 1 first.** Stakeholder discovery establishes business context. Every
   later artefact needs a stakeholder source.
2. **Topic 2 next.** Functional and non-functional requirements turn business
   needs into explicit requirements the rest can measure.
3. **Topic 3.** Volume and growth estimates quantify capacity needs and depend
   on the requirements (what data, what retention).
4. **Topic 4.** Latency, throughput, freshness and availability targets define
   the measurable operational expectations; they use Topic 3's peak rates.
5. **Topic 5.** Constraints, assumptions, dependencies and risks establish the
   boundaries and uncertainties; by now you have enough detail to see them.
6. **Topic 6.** Trade-off analysis evaluates alternatives against requirements
   and constraints, so it needs all five earlier topics.
7. **Topic 7.** ADRs document the resulting decisions and their rationale.

### 5.3 This is not a linear process

Decision-making is iterative. New evidence regularly sends you back.

| Trigger | Revisit |
| --- | --- |
| An estimate changes by an order of magnitude (Topic 3) | Targets (4), constraints and risks (5), criteria and ranking (6), related ADRs (7) |
| A target proves unachievable given dependencies (Topic 4) | Requirements (2), stakeholder expectations (1), alternatives (6) |
| An assumption is invalidated (Topic 5) | Estimates (3), targets (4), ranking (6), ADR status (7) |
| Trade-off analysis reveals a missing criterion (Topic 6) | Requirements (2), stakeholder input (1) |
| An ADR review finds an unsupported claim (Topic 7) | The source artefact in Topics 2–6 |
| A stakeholder changes a priority (Topic 1) | Everything downstream via the traceability matrix |

Rule: **change the source artefact first, then follow the trace links forward.**
Never patch the ADR alone.

### 5.4 Traceability chain

```text
Business objective (BO-n)
   → Requirement (REQ-n)  ← Source stakeholder (STK-n)
   → Acceptance criterion / target (TGT-n) ← Estimate (EST-n)
   → Constraint (CON-n), Assumption (ASM-n), Dependency (DEP-n), Risk (RSK-n)
   → Decision criterion (CRIT-n)
   → Alternative comparison
   → ADR (ADR-n)
```

The ID prefixes are a suggested scheme for this module; use any consistent
scheme. The test is that you can walk from any ADR back to a business objective
and from any business objective forward to the decisions it drives.

Cross-references: patterns (2D.3), modeling (2D.4), storage (2D.5),
integration (2D.6), platform (2D.7), cloud (2D.8), governance (2D.10),
performance and cost (2D.13), documentation and reviews (2D.15).

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
| Terminology and conceptual understanding | Check definitions and distinctions | 1–7 | Beginner |
| Stakeholder and requirement analysis | Analyse statements, find gaps, frame conflicts | 1, 2 | Intermediate |
| Requirement classification and validation | Classify, test measurability, find defects | 2 | Beginner → advanced |
| Quantitative estimation and calculation | Compute volumes, rates, growth, downtime | 3, 4 | Intermediate → advanced |
| Performance and service-target interpretation | Convert vague statements, interpret percentiles, check achievability | 4 | Intermediate → advanced |
| Constraint, assumption, dependency and risk classification | Classify and assess | 5 | Beginner → advanced |
| Architecture alternative comparison | Build and critique matrices | 6 | Intermediate → advanced |
| Trade-off justification | Defend a choice, run sensitivity | 6 | Advanced |
| ADR writing and review | Write, review, supersede | 7 | Intermediate → industry |
| Integrated case-study questions | Combine all topics on one scenario | 1–7 | Industry |

### 6.3 Strategy

1. Answer each topic's questions after the topic, closed-book first.
2. For quantitative questions, always write formula, units, assumptions and the
   interpretation, not just the number.
3. Mark each answer correct / partly correct / wrong and write the reason in
   one sentence.
4. Re-attempt wrong and partly correct answers after several days.
5. Keep integrated case-study answers as written artefacts; they become inputs
   to the project.
6. Have advanced and industry-level answers reviewed by another person.

### 6.4 Expected performance by level

| Level | Successful performance |
| --- | --- |
| Beginner | Accurate definitions; correct classification of at least 90% of examples; correct unit handling in simple calculations |
| Intermediate | Scenario answers identify missing information, produce measurable statements and correct estimates with stated assumptions |
| Advanced | Answers resolve conflicts, quantify uncertainty, run sensitivity, and state what is traded away and what would reverse the choice |
| Industry application | Integrated answers produce reviewable, traceable artefacts; a reviewer can audit and reproduce the reasoning |

### 6.5 Answer-quality criteria

| Criterion | What to check |
| --- | --- |
| Correctness | Concepts, classifications and arithmetic are right |
| Clarity | A non-author can follow it without extra explanation |
| Explicit assumptions | Every assumption stated, labelled and, where possible, sourced |
| Quantitative accuracy | Formula, units, conversions, rounding and ranges correct and consistent |
| Traceability | Each claim links to a requirement, constraint, estimate or criterion |
| Defensible reasoning | Alternatives considered, evidence cited, trade-offs and limits stated |

---

## 7. Project — Requirements and architecture decision pack

Project file:
[`Projects/02-requirements-and-architecture-decision-pack.md`](Projects/02-requirements-and-architecture-decision-pack.md)
(currently empty; this section defines its intended content). The project
index is [`Projects/README.md`](Projects/README.md).

This is an **integrated architecture analysis and decision-documentation
project**. It must show that you can turn a business problem into structured,
measurable requirements and defensible, recorded architecture decisions. It
does **not** implement a data platform.

How it uses the seven topics:

| Project part | Topics |
| --- | --- |
| Problem, stakeholders, business requirements | 1 |
| Requirements register, acceptance criteria | 2 |
| Estimation worksheet | 3 |
| Service-target specification | 4 |
| Constraints, assumptions, dependencies, risks | 5 |
| Criteria, alternatives, trade-off analysis | 6 |
| ADRs and decision log | 7 |

### 7.1 Project objective

Produce a decision pack that a reviewing architect can audit end to end. The
architectural problem to solve: **choose, and justify, the high-level approach
for consolidating customer and transaction data so that risk, finance,
compliance and fraud teams can work from a consistent, timely and governed
view** — stopping at decisions and their evidence, not at design detail or
implementation.

### 7.2 Scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. It operates a core banking system, a
separate cards platform, a CRM and a loan origination system. Nightly extracts
feed an enterprise data warehouse; a data lake created three years ago holds
copies of some sources. Risk, finance, marketing and compliance report
different customer counts. Fraud analysts see card transactions hours after the
fact. A regulator has requested clearer evidence of data lineage and customer
data accountability within a stated period.

> All details in this scenario, including every number below, are **illustrative
> assumptions**, not facts about any real organisation. You may substitute a
> real or realistic organisation (observing confidentiality) but must then
> label what you observed versus what you assume. Use consistent units and
> state decimal or binary multiples.

**Business problem.** Inconsistent customer data, slow availability of fraud
signals, and weak ability to evidence lineage and accountability.

**Stakeholders (assumed).** Chief data officer (sponsor), head of retail, head
of risk, head of finance, head of fraud operations, compliance officer,
security lead, engineering leads, operations lead, internal audit.

**In scope.** Customer, account and card-transaction data; consolidation and
timeliness requirements; capacity and service targets at an order-of-magnitude
level; constraints and risks; decisions on high-level approach.

**Out of scope.** Detailed schema design, vendor product selection beyond
option categories, implementation, migration plans, detailed cost
negotiation, and decisions belonging to later modules (patterns in 2D.3,
modeling in 2D.4, storage in 2D.5, integration in 2D.6, platform in 2D.7,
cloud in 2D.8).

**Initial assumptions (illustrative).** About 3 million retail customers;
about 2 million card transactions per day on average; the card platform emits
batch files every 15 minutes today; seven-year retention for transaction
records; the programme budget ceiling is set by the sponsor.

**Known constraints (illustrative).** Personal data must remain in a stated
jurisdiction; the core banking batch window ends at 02:30; the existing
identity provider must be used; a regulatory milestone date applies.

**Required decision boundaries.** The pack must produce decisions on at least:
(a) the freshness path for card transactions to the fraud case tool, (b) the
approach to the authoritative customer record, and (c) the retention and
storage tiering approach — each at option-category level.

### 7.3 Step-by-step project execution

For every step: **Purpose · Inputs · Actions · Questions to answer · Outputs ·
Validation.**

| Step | Purpose | Inputs | Actions | Questions to answer | Outputs | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define problem, objectives, boundaries | Scenario, sponsor goals | Write problem statement, objectives, scope, exclusions | What is being decided and what is not? | Scope and problem statement | Sponsor-role reviewer confirms scope |
| 2 | Identify stakeholders and decision responsibilities | Org context | Build register with roles, interests, decision rights | Who decides, who is affected, who is missing? | Stakeholder register | Every decision in step 13 has a named decision-maker |
| 3 | Gather and document business requirements | Stakeholder inputs | Hypothetical interviews/workshop notes; separate need from request | What outcome is wanted? What does success look like? | Business requirements (BO-n) | Each has source, success criterion, no embedded solution |
| 4 | Identify functional and non-functional requirements | Step 3 | Classify; use template; prioritise | Which are architecturally significant? | Requirements register (REQ-n) | Types distinct; each sourced |
| 5 | Define measurable acceptance criteria | Step 4 | Metric, target, scope, method, acceptor | How will each important requirement be tested? | Acceptance criteria | Every "must" is testable |
| 6 | Estimate volume, rates, variety, retention, growth | Steps 3–5, assumptions | Apply formulas; ranges; sensitivity | Which input matters most? | Estimation worksheet (EST-n) | Reviewer recomputes; units consistent |
| 7 | Define latency, throughput, freshness, availability targets | Steps 4–6 | Convert vague statements; timing budget; availability composition | Is each target measurable and achievable? | Service-target specification (TGT-n) | Stages sum; composition checked |
| 8 | Record constraints, assumptions, dependencies, risks, unknowns | Steps 1–7 | Classify; score; assign owners | What would invalidate a decision? | Register (CON/ASM/DEP/RSK) | No unclassified or ownerless items |
| 9 | Establish decision criteria and priorities | Steps 4–8 | Derive gates and scored criteria; set weights and method | Which criteria discriminate? | Criteria and prioritisation method | Each traces to REQ/CON/principle |
| 10 | Identify plausible alternatives | Steps 4–9 | Generate ≥3 per decision incl. baseline | Is each feasible within scope and constraints? | Alternatives list | Gate failures removed with reason |
| 11 | Compare alternatives | Steps 9–10 | Matrix with evidence; weighted score where useful | Where is evidence weakest? | Alternatives comparison | Ratings cite evidence |
| 12 | Evaluate trade-offs, cost, risk, uncertainty, operations | Step 11 | TCO sketch; sensitivity; reversibility; operational burden | What changes the ranking? | Trade-off analysis | Sensitivity shows ranking stability or flip points |
| 13 | Select and justify preferred alternative | Steps 11–12 | State choice, assumptions, accepted trade-offs; mark conditional vs final | What are we accepting? What would reverse it? | Recommendation | Decision-maker identified; conditions explicit |
| 14 | Write ADRs | Step 13 | One ADR per major decision using the structure in Topic 7 | Could a reader reproduce the reasoning? | ADR set | Checklist passed |
| 15 | Link decisions to evidence | Steps 14, 3–12 | Add IDs and links; build traceability matrix | Can you walk ADR → BO and BO → ADR? | Traceability matrix | Random trace test passes |
| 16 | Review for consistency and traceability | All | Cross-check numbers, targets, constraints; resolve contradictions | Any unresolved contradiction presented as settled? | Review notes and fixes | Reviewer finds none unflagged |
| 17 | Prepare recommendation and summary | All | One to two pages for sponsor | What is decided, why, at what cost and risk? | Final summary | Non-specialist can follow in ten minutes |

**Per-step guidance:**

1. State exclusions as firmly as inclusions.
2. Include control functions (risk, compliance, security, audit).
3. Record statements verbatim before interpreting them.
4. Keep requirements free of technology names.
5. If you cannot write a test, the requirement is not ready.
6. Show formulas and units; label every figure illustrative.
7. Decompose "real-time" into stages with budgets.
8. Mark unknowns as unknown; do not fill them with invented facts.
9. Fix criteria and weights **before** scoring options.
10. Include a "minimal change" baseline.
11. Rate from evidence, not impression.
12. Vary the two most uncertain inputs.
13. **Which decisions can be finalised:** those whose critical inputs are
    measured or confirmed by a stakeholder. **Which remain conditional:**
    those depending on high-impact, low-confidence assumptions (for example an
    unconfirmed vendor commitment or an unmeasured peak factor). Record the
    missing evidence, owner and date.
14. One decision per ADR.
15. Fix the source artefact first if a link reveals a gap.
16. Check unit and number consistency across worksheet, targets and ADRs.
17. State limits and conditional decisions plainly.

### 7.4 Required project deliverables

Deliverables are kept proportionate: related content lives in one artefact
rather than being duplicated.

| # | Deliverable | Purpose | Minimum contents |
| --- | --- | --- | --- |
| D1 | Project scope and business problem statement | Fix boundaries | Problem, objectives, in/out of scope, decision boundaries, labelled assumptions |
| D2 | Stakeholder register | Who matters and who decides | Stakeholder, role, interest, decision rights |
| D3 | Business requirements document | Capture needs | BO-n with source, success criterion, priority, open questions |
| D4 | Functional and non-functional requirements register | Explicit requirements | REQ-n with type, priority, acceptance criterion, source, status |
| D5 | Requirement traceability matrix | Prove linkage | BO → REQ → TGT/EST → CON/ASM/RSK → CRIT → ADR |
| D6 | Data volume and growth estimation worksheet | Quantify capacity | Inputs, formulas, units, assumptions, ranges, sensitivity, interpretation, confidence |
| D7 | Performance and service-target specification | Measurable operations | Per workload: indicator, percentile, target, window, scope, method, timing budget |
| D8 | Constraints, assumptions, dependencies and risks register | Bound the problem | Item, class, owner, status, exposure, response, trigger, linked decisions |
| D9 | Decision criteria and prioritisation method | Make comparison fair | Gates, scored criteria, weights and rationale, scoring scale |
| D10 | Architecture alternatives comparison | Compare real options | Options per decision, matrix with evidence |
| D11 | Trade-off analysis and recommendation | Defend the choice | Sensitivity, cost/benefit sketch, reversibility, accepted trade-offs |
| D12 | Architecture Decision Records | Preserve rationale | One ADR per major decision, linked, with status |
| D13 | Final requirements and architecture decision summary | Sponsor readout | One to two pages: problem, key requirements and targets, decisions, trade-offs, conditional items, risks |

### 7.5 Suggested templates and fields

Use only the fields that serve a purpose. Do not force every field into every
artefact. Mark `Unknown` rather than inventing a value, and carry a `Source` and
`Confidence` (High / Medium / Low) where it applies.

**Requirements register**

| Field | Purpose |
| --- | --- |
| Requirement ID | Reference and traceability |
| Description (template form) | The statement |
| Type (business / functional / non-functional / data / constraint) | Classification |
| Business rationale / linked objective | Why it exists |
| Priority (and rule used) | Ordering |
| Acceptance criteria and validation method | Testability |
| Source stakeholder | Provenance |
| Dependencies, related constraints and risks | Interaction |
| Status (draft / validated / changed) | Lifecycle |

**Quantitative estimation worksheet**

| Field | Purpose |
| --- | --- |
| Item and ID | Reference |
| Input quantity, unit | Basis |
| Formula | Reproducibility |
| Assumptions and evidence label (measured / sampled / stated / estimated / guessed) | Credibility |
| Low / expected / high | Uncertainty |
| Result with unit | Output |
| Sensitivity rank | What matters |
| Interpretation / architecture implication | Use |

**Constraints, assumptions, dependencies and risks register**

| Field | Purpose |
| --- | --- |
| ID and class (CON / ASM / DEP / RSK / UNK) | Classification |
| Statement | Content |
| Source and owner | Accountability |
| Fixed or negotiable (constraints) | Flexibility |
| Probability, impact, exposure (risks; scales stated) | Prioritisation |
| Validation method and due date (assumptions) | Closure |
| Response, trigger, escalation | Action |
| Linked requirements and decisions | Traceability |

**Decision matrix**

| Field | Purpose |
| --- | --- |
| Decision ID and statement | Scope |
| Gate criteria (pass/fail) | Elimination |
| Scored criteria and weights, with rationale | Discrimination |
| Option × criterion rating with evidence | Transparent comparison |
| Weighted total and rank | Summary (with stated limits) |
| Sensitivity result | Robustness |
| Reversibility / lock-in note | Long-term consequence |

**ADR** — use the structure proposed in Module 7 (status, date, deciders,
related IDs, context, drivers, options, outcome, rationale, consequences,
rejected alternatives, conditions for revisiting, open issues).

### 7.6 Validation and quality assurance

| Check | How to verify |
| --- | --- |
| Business requirements traceable to stakeholder needs | Each BO-n cites a stakeholder and a statement; sample five |
| Functional and non-functional requirements distinguishable | Type field present and consistent; no sentence mixes both |
| Important requirements have measurable acceptance criteria | Every "must" has metric, target, method |
| Numerical estimates include units, formulas, assumptions, interpretation | Reviewer recomputes three figures from the worksheet |
| Performance targets measurable and internally consistent | Timing budget sums; availability composition checked against dependencies |
| Constraints, assumptions, dependencies, risks classified correctly | Apply the Topic 5 tests to a sample of ten items |
| Alternatives feasible within scope | Each option passes all gates or is removed with a reason |
| Trade-offs evaluated against explicit criteria | Criteria and weights fixed before scoring (date or version evidence) |
| Recommendations follow from evidence | Each recommendation cites matrix rows and sensitivity result |
| ADRs explain context, decision, rationale, consequences | Checklist from Topic 7 passed |
| No unresolved contradictions presented as settled | Cross-document consistency read; flagged items listed as open |

### 7.7 Project completion gate

The project is complete only when **all** hold:

- [ ] D1–D13 exist, version-dated, and use consistent IDs.
- [ ] **Requirements:** at least 90% of "must" requirements have a measurable
      acceptance criterion; no requirement embeds a technology choice.
- [ ] **Estimates:** every figure carries unit, formula, assumption and
      evidence label; a reviewer recomputes at least three and obtains the
      same results; illustrative values are marked as such.
- [ ] **Targets:** each target names indicator, percentile, window, scope and
      measurement method; timing budget sums correctly.
- [ ] **Risk analysis:** every item is classified; every high-exposure risk has
      an owner, response and trigger; every high-impact assumption has a
      validation method and date.
- [ ] **Alternatives:** each major decision has at least three feasible
      alternatives including a baseline, compared against criteria set before
      scoring.
- [ ] **Sensitivity:** analysis exists for the two least certain inputs, and the
      report states whether the ranking changes.
- [ ] **ADRs:** each major decision has an ADR with rejected alternatives,
      consequences and revisit conditions; conditional decisions are marked and
      name their missing evidence.
- [ ] **Traceability:** a random trace from three ADRs back to business
      objectives, and from three business objectives forward to ADRs, succeeds.
- [ ] **Final recommendation:** states what is decided, assumptions, accepted
      trade-offs and what is still open; readable by a non-specialist in ten
      minutes.
- [ ] An independent reviewer agrees the evidence supports the conclusions.

Finishing every document is **not** sufficient; the evidence criteria must be
met.

### 7.8 Connection to subsequent modules

| Later module | How the pack supports it |
| --- | --- |
| 2D.3 Patterns and reference architectures | Criteria, targets and constraints are the filter for choosing among patterns; ADRs record the pattern decisions |
| 2D.4 Conceptual, logical and physical modeling | Business requirements and the customer-record decision define the entities and quality needs |
| 2D.5 Storage architecture | Volume, retention and growth estimates and the tiering decision feed storage selection |
| 2D.6 Integration | Freshness and throughput targets and source constraints drive integration choices |
| 2D.7 Enterprise platform | Capacity, service levels and dependency map shape platform scope |
| 2D.8 Cloud and hybrid | Residency, cost and dependency constraints bound cloud options |
| 2D.15 Architecture reviews | The decision log and traceability matrix are the review inputs |

Do not extend this project into designing or building the platform.

---

## 8. Final learning assessment and completion checklist

Self-reported confidence is not sufficient; each row requires the stated
evidence.

| # | You can… | Evidence demonstrating mastery |
| --- | --- | --- |
| 1 | Elicit and document stakeholder requirements | Stakeholder register, requirements summary and conflict log reviewed; no unlabelled solutions |
| 2 | Translate business needs into functional and non-functional requirements | Requirements register with types, acceptance criteria and sources; defect-review exercise |
| 3 | Estimate data volumes, growth and workload characteristics | Worksheet with formulas, units, ranges, sensitivity; reviewer reproduces results |
| 4 | Define measurable latency, throughput, freshness and availability targets | Service-target specification with percentile, window, scope, method; timing budget; availability composition |
| 5 | Distinguish constraints, assumptions, dependencies and risks | Correctly classified register; classification test passed on a fresh sample |
| 6 | Establish architecture decision criteria | Gates and weighted criteria derived from requirements, fixed before scoring |
| 7 | Compare alternatives and justify trade-offs | Evidence-based matrix, sensitivity analysis and a recommendation naming what is traded away |
| 8 | Write and maintain ADRs | ADR set with status log, one supersession example and a passed review checklist |
| 9 | Complete the integrated decision pack | D1–D13 and the project completion gate (Section 7.7) met |
| 10 | Defend decisions with evidence and clearly stated assumptions | Live or written challenge round with two reviewer objections answered using recorded evidence |

Module complete when:

- [ ] All seven topic completion gates are signed off.
- [ ] `practice-questions.md` answered; wrong answers corrected and
      re-attempted.
- [ ] The project completion gate is met.
- [ ] You have presented the pack and answered a reviewer's challenges without
      introducing unsupported claims.
- [ ] Open questions are logged for the next module (2D.3).

---

## 9. Where this module leads

Module 2D.3, **Data Architecture Patterns and Reference Architectures**, takes
the requirements, targets, constraints and decision method produced here and
uses them to choose among and combine architecture patterns, with the choices
recorded as ADRs.
