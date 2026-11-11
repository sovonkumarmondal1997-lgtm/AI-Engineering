# Reference Architectures, Standards and Reusable Patterns

**Stage:** Stage 2D — Data Architecture  
**Module:** 15 — Architecture Documentation, Reviews and Operating Model  
**Topic:** 06  
**Learning progression:** Beginner → Intermediate → Advanced  
**Recommended effort:** 6–8 hours (roadmap estimate)  
**Scenario:** Fictional Northbridge Bank; all names, architecture details, requirements, scores, metrics, dates, decisions, and evidence in examples are synthetic and illustrative.

> **Source and status note.** This lesson follows Topic 06 of `roadmap-Architecture-Documentation-Reviews-and-Operating-Model.md` and the target location in `Roadmap_ptree.md`. The roadmap describes exercises, templates, and targets as recommendations, not as proof of existing organizational decisions. No external framework, vendor architecture, standard, certification, control, or governance process is asserted to be formally adopted by this repository or by Northbridge Bank. Named approaches are illustrative options to evaluate. A pattern catalogue or standards process proposed here is a learning aid unless an organization formally approves it.

## Table of contents

1. [Learning objectives](#1-learning-objectives)
2. [Prerequisites and connections](#2-prerequisites-and-connections)
3. [Beginner: vocabulary and purpose](#3-beginner-vocabulary-and-purpose)
4. [Beginner: when reuse helps and when it harms](#4-beginner-when-reuse-helps-and-when-it-harms)
5. [Intermediate: establish applicability before scoring](#5-intermediate-establish-applicability-before-scoring)
6. [Intermediate: compare alternatives fairly](#6-intermediate-compare-alternatives-fairly)
7. [Worked Northbridge comparison](#7-worked-northbridge-comparison)
8. [Intermediate: standards governance and exceptions](#8-intermediate-standards-governance-and-exceptions)
9. [Advanced: adaptation, drift and portfolio governance](#9-advanced-adaptation-drift-and-portfolio-governance)
10. [Relationships to architecture artefacts and operating model](#10-relationships-to-architecture-artefacts-and-operating-model)
11. [Practical exercises with model answers](#11-practical-exercises-with-model-answers)
12. [Reusable templates](#12-reusable-templates)
13. [Common mistakes and corrective practices](#13-common-mistakes-and-corrective-practices)
14. [Practice questions and answer key](#14-practice-questions-and-answer-key)
15. [Deliverables, mastery criteria and completion gate](#15-deliverables-mastery-criteria-and-completion-gate)
16. [Readiness for Topic 07](#16-readiness-for-topic-07)

---

## 1. Learning objectives

After completing this lesson, you should be able to:

1. Distinguish a reference model, reference architecture, design pattern, standard, guideline, blueprint, and implementation-specific design.
2. Explain the intended use, scope, assumptions, authority, and limitations of a candidate reference or pattern.
3. Assess applicability against business requirements, constraints, quality attributes, security, governance, interoperability, reliability, cost, operability, and team capabilities.
4. Compare at least two plausible approaches using criteria defined before evaluating the options, with evidence and uncertainty visible.
5. Explain the costs of reuse, adaptation, bespoke design, and non-reuse, including lifecycle maintenance and lock-in.
6. Document selection rationale and consequences in an ADR linked to requirements, diagrams, threat models, risk registers, and evidence.
7. Record adaptations and deviations from a reference architecture or pattern, including reason, impact, owner, validation, and review trigger.
8. Propose a lightweight standards lifecycle: proposal, review, approval, publication, conformance, exception handling, versioning, and retirement.
9. Create a useful pattern-catalogue entry with context, forces, solution, consequences, owner, version, and review date.
10. Prepare the architecture and decision ownership questions that Topic 07 will resolve.

**Quality target:** reuse should be a reasoned decision, not a default. A reader should be able to reconstruct the context, compare the credible options, understand the evidence and uncertainty, identify what was adapted, and see who owns follow-up.

## 2. Prerequisites and connections

### 2.1 Roadmap prerequisites

The module roadmap identifies **Topic 04**, **Topic 05**, and **P5** as dependencies:

- **Topic 04 — Architecture decision records and decision log:** know how to capture context, criteria, alternatives, rationale, consequences, status, and revisit triggers. Topic 06 uses an ADR to preserve why a pattern or standard was selected or rejected.
- **Topic 05 — Design reviews, threat models and risk registers:** know how to evaluate a design against explicit criteria, anchor threats to data flows and trust boundaries, and assign owners and treatment to risks. Topic 06 uses those findings to test whether a reference fits and whether an adaptation introduces new exposure.
- **P5 — Governance, decision rights, frameworks and reference models:** understand that a reference model organizes concepts, while governance defines who can decide, approve, require, or grant exceptions. The roadmap points to `../01-Data-Architecture-Foundations-and-Principles/05-data-architecture-lifecycle-and-governance.md` and `06-enterprise-data-architecture-frameworks-and-reference-models.md`.

Topic 06 also benefits from the earlier requirements and trade-off material, security and privacy fundamentals, failure-domain analysis, cost/performance evidence, and data-product contracts. These are useful inputs, but this lesson does not claim to replace those topics.

### 2.2 How Topic 04 and Topic 05 feed Topic 06

| Earlier artefact | Question it answers | How Topic 06 uses it |
|---|---|---|
| Requirements, constraints, assumptions and decision criteria | What must be true, and what matters most? | Establishes applicability and comparison criteria before options are scored. |
| ADR and decision log (Topic 04) | Why was a significant option chosen? | Records the selected reference/pattern, alternatives, trade-offs, conditions and revisit triggers. |
| Context, deployment and data-flow diagrams (Topics 01–02) | What systems, flows, boundaries and dependencies are in scope? | Checks whether the reference's topology and trust assumptions match the target context. |
| Threat model and risk register (Topic 05) | How might the design fail or be attacked, and who treats the risk? | Identifies reference gaps, adaptation risks, required controls and residual risks. |
| Review findings and evidence | Which claims are demonstrated, assumed, or unresolved? | Prevents a polished reference diagram from being mistaken for implementation evidence. |

A reference architecture does not override a real requirement, security review, approved governance decision, or implementation evidence. Conversely, a local design should not ignore an applicable, formally approved standard merely because a different pattern seems more convenient.

### 2.3 Source discipline

In this lesson:

- **Roadmap-derived:** the distinctions, applicability assessment, comparison against fixed criteria, deviation and exception records, catalogue entry, standards governance, pilot evidence, vendor-neutrality concerns, and Topic 07 readiness.
- **Illustrative recommendation:** the scoring scales, sample criteria weights, approval workflow, metrics, templates, and Northbridge scenario. Adapt them to actual decision rights and requirements.
- **Not asserted:** formal adoption of any named standard, framework, notation, cloud provider, vendor architecture, regulatory control, or certification.

---

## 3. Beginner: vocabulary and purpose

### 3.1 The key artefacts are not interchangeable

| Concept | What it is | Main question | Typical authority | Example |
|---|---|---|---|---|
| **Reference model** | A conceptual vocabulary, taxonomy, or set of relationships for a domain; it may be technology-neutral and need not prescribe a deployable design. | What concepts and relationships should we reason about? | Explanatory unless adopted into governance | A conceptual model separating ingestion, storage, processing, governance, and consumption capabilities. |
| **Reference architecture** | A reusable architecture-level arrangement for a class of problems, including major components, relationships, boundaries, and sometimes recommended practices. | What broad structure could solve this class of problem? | Guidance unless an organization formally endorses or mandates parts of it | A synthetic governed-lakehouse reference showing ingestion, raw/curated zones, catalog, policy enforcement, and serving. |
| **Design pattern** | A recurring solution structure for a problem in a stated context, including forces, consequences, and known limitations. | What reusable design move addresses this recurring problem? | Usually advisory; context determines fit | Batch landing followed by validated, idempotent transformations. |
| **Standard** | An agreed or required rule, specification, convention, or constraint that defines what is expected. Its authority depends on who adopted it and how it is governed. | What must be followed, and how is conformance determined? | Could be mandatory, comply-or-explain, or voluntary depending on the adopting authority | An organization-approved requirement that every shared data API publishes a versioned schema and compatibility policy. This is an illustrative internal rule, not a repository mandate. |
| **Guideline** | Advice about a preferred practice where judgement remains possible. | What is generally recommended? | Advisory unless incorporated into a binding policy | Prefer explicit schema evolution over undocumented breaking changes. |
| **Blueprint** | A more concrete, implementation-oriented starting design, often with resource choices, configuration, deployment assumptions, and prescribed connections. | What concrete starting implementation can be instantiated? | Specific to its stated environment; authority still depends on adoption | A sample deployment package for a particular platform profile. |
| **Implementation-specific design** | The design for a particular system, environment, version, workload, and organization. | What will this system actually do and how? | Project/system decision authority | Northbridge's selected ingestion service, storage layout, access policies, runbooks, and deployment topology. |
| **Technology choice** | Selection of a specific product, service, library, or technology to implement a capability. | Which technology will implement the design? | A decision within defined procurement and architecture authority | Selecting one managed event broker after evaluating requirements and constraints. |

**Important distinction:** these categories can overlap in an artefact's packaging, but not in their reasoning. A vendor document can be a reference architecture and a product-specific blueprint at the same time. That does not make it a neutral standard. A pattern can be widely used without being mandatory. A standard may constrain several patterns without specifying the whole architecture.

### 3.2 Standard is not the same as “best practice”

A statement such as “use event streaming for low latency” is not automatically a standard. It may be a heuristic, guideline, design decision, or unjustified generalization. To call something a standard in an organization, establish at least:

- the adopting authority and scope;
- the exact normative statement and terms such as *must*, *should*, or *may*;
- the rationale and evidence for the rule;
- applicability conditions and exclusions;
- how conformance is checked;
- who can approve exceptions;
- an owner, version, effective date, and review/retirement path.

A named external publication may have its own scope and status, but do not invent clause numbers, obligations, or certification claims. Verify the primary source before making such claims. This lesson uses no external standard as a mandatory rule.

### 3.3 Why reference architectures exist

A reference architecture helps an organization reason consistently about a recurring class of systems. It can:

- provide a common vocabulary and a starting decomposition;
- make cross-team interfaces and responsibilities easier to discuss;
- surface common quality attributes, risks, and operational needs;
- reduce repeated design effort and support reusable tooling;
- help reviewers recognize omissions and compare proposals;
- establish a baseline for measuring adaptations and learning from delivery.

It cannot prove that a solution is correct for every context. It may encode assumptions about scale, latency, workload shape, regulatory geography, skills, service availability, deployment model, or funding. A reference is useful only when those assumptions are made visible and checked.

### 3.4 A simple data-platform example

Imagine a reference architecture with these logical capabilities:

1. source adapters and ingestion;
2. durable landing and replay;
3. validation and transformation;
4. governed storage zones;
5. catalog, lineage and policy enforcement;
6. serving interfaces and consumer contracts;
7. observability, operations and cost management.

This is a **conceptual example**, not a prescribed topology. It does not specify a vendor, exact number of services, mandatory zone names, or whether processing is batch, streaming, or both. A real design must map the capabilities to requirements and decide which parts are shared, domain-owned, managed, or bespoke.

### 3.5 Classify the statement before acting on it

| Statement | Likely category | Why | What must be clarified? |
|---|---|---|---|
| “All data systems should expose their lineage.” | Guideline or proposed standard | “Should” signals recommendation unless an authority defines it as mandatory. | Scope, minimum lineage, enforcement, exceptions, owner. |
| “A system includes ingestion, storage, governance, and serving capabilities.” | Reference model | Describes concepts, not necessarily deployable components. | Whether it is merely explanatory or adopted. |
| “For replayable event ingestion, persist an immutable source envelope before enrichment.” | Design pattern | A reusable solution to a recurring replay/audit problem. | Context, retention, privacy, cost, ordering, idempotency. |
| “Use this approved event contract format for all shared event interfaces.” | Potential internal standard | It states a common rule, if formally approved and scoped. | Actual authority, permitted exceptions, version and conformance checks. |
| “Deploy these six services with these network rules in account X.” | Blueprint or implementation design | Concrete environment-specific instructions. | Whether assumptions match the target environment and whether it is maintained. |
| “Choose managed streaming service Y.” | Technology choice | Names a specific implementation technology. | Evidence, alternatives, portability, cost, procurement and support. |

**Beginner exercise:** classify each statement above and explain one condition that could change the classification. Model answers appear in Section 11.

---

## 4. Beginner: when reuse helps and when it harms

### 4.1 The benefits and costs are both real

| Dimension | Potential benefit of reuse | Potential cost or failure mode |
|---|---|---|
| Delivery speed | Reuse of proven structures and automation reduces repeated design work. | A poor fit creates extensive exceptions and rework. |
| Consistency | Similar systems have recognizable interfaces and controls. | Over-standardisation can erase legitimate workload or domain differences. |
| Reliability | Known failure modes, runbooks and operational practices can be reused. | A copied pattern may reproduce an unsuitable failure domain or untested assumption. |
| Security and governance | Common control points can be reviewed once and applied consistently. | “The reference says it is secure” can substitute for threat modelling and evidence. |
| Skills and support | Teams can share knowledge, tooling and support practices. | Central expertise becomes a bottleneck or a single point of failure. |
| Cost | Shared components may reduce duplicated engineering and operations. | Shared services can be over-provisioned, misallocated, or expensive for a low-volume workload. |
| Evolution | One maintained pattern can incorporate lessons from many implementations. | A stale catalogue makes obsolete guidance look authoritative. |
| Portability | Technology-neutral patterns can preserve choice. | A product-specific reference may deepen lock-in and make exit costly. |
| Accountability | Standard interfaces clarify ownership and review expectations. | Ambiguous shared ownership creates hand-off gaps and operational friction. |

### 4.2 Reuse is a lifecycle decision

Do not compare only the first implementation sprint. Consider:

- **Initial design and build:** discovery, configuration, integration, migration, tests.
- **Run cost:** infrastructure, licences, support, on-call, monitoring, security operations.
- **Change cost:** schema evolution, upgrades, changing requirements, compatibility, migration.
- **Governance cost:** conformance checks, approvals, exception reviews, catalogue maintenance.
- **Exit cost:** data and metadata portability, retraining, replacement, contract termination, parallel running.
- **Risk cost:** probability and impact of mismatch, concentration, operational complexity, and deferred work.

A reusable component is not free just because another team built it. It has an owner, lifecycle, service expectations, dependency risk, and support cost. A bespoke design is not automatically more expensive; it may be simpler if the reference brings unnecessary components or constraints.

### 4.3 A practical rule

Reuse is a strong candidate when the problem and forces are materially similar, the reference assumptions hold, its known consequences are acceptable, and a capable owner can maintain the shared asset. Adapt or design bespoke when a hard requirement conflicts with the reference, its assumptions fail, the total lifecycle cost is worse, or the reference introduces unacceptable risk. “Bespoke” still requires architecture review; it is not permission to bypass standards or controls.

---

## 5. Intermediate: establish applicability before scoring

### 5.1 Do not start with a score

A weighted matrix can create a false sense of objectivity if options are scored before anyone establishes that they are eligible. First identify hard constraints and disqualifying conditions. For example, an option that cannot meet a mandatory data residency constraint should not win because it scores highly on cost and delivery speed.

Use this sequence:

1. **Define the decision:** the capability and boundary being selected, what is out of scope, and the decision owner.
2. **State requirements and constraints:** separate mandatory requirements from preferences, assumptions and open questions.
3. **Identify the decision drivers:** latency, recovery, security, governance, interoperability, cost, team capability, and other material quality attributes.
4. **Collect candidate options:** at least two plausible patterns/references and a baseline such as the current approach, no adoption of the candidate reference, or a deliberately minimal design.
5. **Read the source carefully:** record version/date, scope, intended context, dependencies, known uses, limitations and product-specific assumptions.
6. **Test eligibility:** determine whether each option satisfies hard constraints or requires an explicitly reviewable exception.
7. **Compare eligible options:** apply consistent criteria, evidence, weights if appropriate, and uncertainty notes.
8. **Run a risk and operational review:** use Topic 05 artefacts; consider failure modes, trust boundaries, blast radius and day-2 ownership.
9. **Select or defer:** explain why the chosen option is preferable under stated assumptions and what evidence is missing.
10. **Record and validate:** create an ADR, adaptation/deviation records, any exception request, and updates to affected architecture artefacts.

### 5.2 Applicability assessment template

| Question | What to inspect | Evidence to capture | Warning sign |
|---|---|---|---|
| Does the reference address the same problem? | Problem statement, target consumers, operating context | Requirement-to-capability mapping | Similar vocabulary but different workload or outcome |
| Are its forces present? | Latency, throughput, ordering, consistency, isolation, retention, availability | Measured workload profile or explicitly labelled assumption | Selection is driven by fashion or a single anecdote |
| Do assumptions hold? | Skills, scale, network, identity, regions, services, support, budget | Assumption register with owner and validation plan | Critical assumptions are unowned or untested |
| Does it satisfy hard constraints? | Security, privacy, residency, recovery, interoperability, procurement | Traceability to actual requirements and evidence | “Compliant by design” without proof |
| Are quality attributes addressed? | Performance, scalability, reliability, maintainability, operability | Test results, operational history, pilot data, or reasoned estimates | Only functional features are compared |
| What are its consequences? | Coupling, failure domains, shared dependencies, lock-in, team load | Risk register and architecture review findings | Consequences are described only as benefits |
| What does adaptation require? | Missing components, altered flows, controls, support model | Work estimate, dependency changes, deviation records | “Small change” with no owner or validation |
| What if we do not use it? | Current state, simpler alternative, bespoke option, delay/no decision | Baseline costs and consequences | No baseline, so reuse benefit is unmeasured |
| Who will own it? | Catalogue owner, runtime owner, standards authority, support team | Named accountable roles and support expectations | Shared asset with no maintenance commitment |
| How will we know it worked? | Acceptance criteria and review date | Pilot plan, metrics, test evidence | No measurable outcome or revisit trigger |

### 5.3 Evidence quality: label what you know

Use a consistent evidence vocabulary in the comparison:

- **Observed/measured:** produced by a stated test, benchmark, inventory, configuration review, or operational record. Include scope, date, environment and limitations.
- **Documented:** stated in an identifiable source with version/date. Documentation may still be incomplete or outdated.
- **Reported:** supplied by a stakeholder or vendor and not independently verified.
- **Assumed:** used for analysis but not yet established. Name an owner and a validation date or trigger.
- **Inferred:** reasoned from other evidence. State the inference and its uncertainty.
- **Unknown:** information needed for a confident decision is missing.

Vendor claims are evidence of what the vendor claims, not automatically evidence of workload fit. A synthetic exercise may use assumptions to demonstrate method, but must label them as synthetic and must not present them as measured production facts.

### 5.4 Build a requirement-to-pattern trace

For every important requirement, record how the candidate handles it and what proof is available.

| Requirement ID | Requirement / constraint | Candidate design element | Evidence or assumption | Gap / adaptation | Owner / next action |
|---|---|---|---|---|---|
| REQ-01 (synthetic) | Curated risk data available within 15 minutes | Streaming or frequent micro-batch path | Assumed target; workload benchmark pending | Validate end-to-end freshness under peak load | Data platform lead / run representative test |
| REQ-02 (synthetic) | Access to sensitive attributes restricted by role | Policy enforcement at serving and storage layers | Design assertion only | Threat-model enforcement and test denial paths | Security owner / add test cases |
| REQ-03 (synthetic) | Reprocessing must not duplicate downstream records | Idempotent sink and replay controls | Pattern documentation plus proposed test | Define stable key and duplicate-handling contract | Pipeline owner / replay test |

These identifiers are illustrative. In a real architecture package, link them to the authoritative requirement and evidence locations rather than creating conflicting copies.

---

## 6. Intermediate: compare alternatives fairly

### 6.1 Fix criteria before evaluating options

A fair comparison uses the same criteria, definitions, scoring anchors, and evidence expectations for every candidate. Include a credible baseline, not just two vendor architectures. Criteria should derive from requirements and context; do not choose weights merely to make a preferred option win.

Possible criteria include:

- **Requirement fit:** functional capabilities and hard constraints.
- **Security and privacy:** identity boundaries, least privilege, data minimisation, secrets, auditability, exposure paths.
- **Governance:** policy enforcement, ownership, metadata, lineage, retention, evidence and exception handling.
- **Scalability and performance:** workload shape, peak throughput, latency, concurrency, backpressure and resource isolation.
- **Reliability and recoverability:** failure domains, replay, idempotency, RPO/RTO fit where specified, dependency resilience.
- **Interoperability and portability:** interfaces, open formats/protocols where relevant, export paths, dependency depth and exit cost.
- **Operability:** deployment, monitoring, alerting, runbooks, upgrades, incident response, testability.
- **Cost:** total lifecycle cost and unit economics under explicit workload assumptions, not only initial service price.
- **Team capability:** skills, support coverage, cognitive load, training, hiring and vendor dependence.
- **Time to value and reversibility:** delivery lead time, migration effort, ability to pilot, and cost of changing later.

Avoid double-counting. For example, if “operability” already includes monitoring and incident response, do not award the same benefit again under three nearly identical criteria without explaining why they are distinct.

### 6.2 Use hard gates and scored preferences separately

**Hard gates** are pass/fail conditions backed by actual requirements or decision authority. Examples might include a defined residency constraint, an approved interface requirement, or a specified recovery objective. Do not invent these as legal requirements. If a candidate fails a hard gate, either exclude it or document a formally authorized exception; do not hide the failure in a weighted average.

**Scored preferences** compare eligible options on relative fit. A simple ordinal scale can be:

| Score | Anchor | Evidence expectation |
|---:|---|---|
| 1 | Poor fit; material gap or high burden | Specific gap and credible evidence/assumption stated |
| 2 | Weak fit; significant adaptation required | Adaptation and residual risk identified |
| 3 | Adequate; requirement can be met with manageable work | Feasible design and validation path described |
| 4 | Strong fit; small, understood adaptations | Relevant evidence or strong contextual rationale |
| 5 | Very strong fit; directly addresses the criterion with limited downside | Evidence and scope of applicability explicit |

A score of 5 does not mean “perfect,” certified, or risk-free. Use **N/A** only when the criterion genuinely does not apply and explain why. Use **Unknown** when evidence is missing; do not convert missing evidence into a neutral or high score.

### 6.3 Weighted scoring: a decision aid, not a verdict

If weights help, normalize them to 100%. For each eligible option:

`Weighted total = sum(weight × score) / sum(weights for scored criteria)`

If weights are percentages and scores run from 1 to 5, the resulting total remains on the 1–5 scale. The arithmetic ranks options under the chosen assumptions; it does not establish objective truth. Show the inputs, scoring anchors, exclusions, confidence, and sensitivity to disputed weights. Do not score hard-gate failures into eligibility.

When evidence is weak, a qualitative comparison may be more honest than a precise-looking decimal. Use scenario analysis or a pilot to reduce uncertainty. If two options are close, explain what would change the choice instead of over-interpreting a small numerical difference.

### 6.4 Make uncertainty visible

A useful matrix has columns for score, evidence, confidence and follow-up. For example, “4 / medium / based on a synthetic benchmark; repeat under peak concurrency” is more informative than “4”. Distinguish:

- **Decision confidence:** how robust the choice is under current knowledge.
- **Evidence confidence:** how strong the evidence for a specific criterion is.
- **Residual risk:** what remains after selected controls or adaptations.

Do not average away a serious security, privacy, reliability, or operational concern. A high total cannot compensate for an unaccepted critical risk or an unmet hard constraint.

---

## 7. Worked Northbridge comparison

### 7.1 Scenario and assumptions

**Fictional scenario:** Northbridge Bank wants a governed self-service lakehouse capability for analytics teams. Sources include scheduled core-system extracts and selected near-real-time events. Consumers need curated datasets with controlled access, discoverability, lineage, reproducible transformations, and an operational support path.

The following are **synthetic exercise assumptions**, not verified requirements or measurements:

- scheduled data can tolerate a delay of up to one hour;
- a subset of fraud-monitoring data has a target freshness of 15 minutes;
- teams need controlled self-service access to curated datasets;
- replay and idempotent processing matter for recoverability;
- the team has moderate batch engineering experience and limited experience operating streaming infrastructure;
- a short pilot can be run before standardising a pattern;
- no actual provider, product, regulatory clause, or formally adopted internal standard is specified.

The first decision is not “which vendor is best?” It is which **architecture approach** best fits the stated workload and operating context. Technology selection can follow after the pattern-level decision or be included as a separate ADR if material.

### 7.2 Candidates

- **Option A — Batch-first governed lakehouse:** scheduled ingestion for most sources, durable landing, validated transformations, catalog/lineage and policy controls, with a separately evaluated path for the freshness-sensitive subset.
- **Option B — Streaming-first lakehouse:** event-oriented ingestion and continuously running transformations for most sources, with batch sources adapted into the event path where appropriate.
- **Option C — Hybrid by workload:** batch path for hourly/daily sources and a narrowly scoped streaming or micro-batch path for the 15-minute subset, using shared governance and serving conventions.
- **Baseline D — Keep current fragmented approaches temporarily:** do not adopt a common reference now; document the existing patterns, their risks, and a time-bounded plan to reassess. This baseline is not presumed acceptable indefinitely.

These are generic architecture patterns, not product claims. Their actual feasibility depends on workload tests, interface details, platform capabilities and support arrangements.

### 7.3 Hard-gate assessment

For this exercise, assume the stated freshness targets and controlled access are requirements. These gates are illustrative; a real project must obtain the actual approved requirements and authority.

| Gate | A: batch-first | B: streaming-first | C: hybrid | D: fragmented baseline |
|---|---|---|---|---|
| Hourly/daily sources supported | Pass | Pass, but may add needless continuous-processing complexity | Pass | Unknown until inventory confirms current paths |
| 15-minute subset feasible | **Needs proof**; a dedicated fast path may be required | Plausible, but end-to-end latency must be measured | Plausible; must validate hand-offs and freshness | Unknown until measured |
| Governed access and lineage | Design required; no option guarantees it by itself | Design required; no option guarantees it by itself | Shared controls required across both paths | Likely inconsistent in this synthetic baseline; inventory required |
| Replay and idempotency | Must be designed and tested | Must be designed and tested | Must be designed across both paths | Unknown until review |

No candidate is declared secure or compliant by label. If Option A cannot meet the freshness gate after a reasonable design and test, it must be revised or excluded for the sensitive subset. If the baseline lacks evidence, that uncertainty is not a pass.

### 7.4 Criteria and weights

The following weights are illustrative and sum to 100. They reflect this synthetic scenario, not universal priorities.

| Criterion | Weight | Why it matters in this scenario |
|---|---:|---|
| Requirement fit and freshness | 20 | Hourly sources and a 15-minute subset both need a credible path. |
| Security and governance integration | 15 | Controlled access, lineage and policy enforcement are explicit goals. |
| Reliability, replay and recoverability | 15 | Data correction and safe reprocessing are important. |
| Operability and team capability | 15 | The team must support the chosen pattern in production. |
| Lifecycle cost | 10 | Continuous infrastructure and shared platform costs must be understood. |
| Interoperability and exit options | 10 | Interfaces and data movement should not create unnecessary lock-in. |
| Scalability and performance | 10 | Peak load and future growth need a validation plan. |
| Delivery speed and reversibility | 5 | A pilot should limit irreversible commitment. |

### 7.5 Worked scoring matrix

Scores are synthetic expert judgements for teaching purposes, **not measured results**. The evidence notes explain the uncertainty. A real review should replace them with workload profiles, pilot results, cost estimates, threat/risk findings and stakeholder-approved criteria.

| Criterion | Weight | A: batch-first | B: streaming-first | C: hybrid | D: fragmented baseline |
|---|---:|---:|---:|---:|---:|
| Requirement fit and freshness | 20 | 3 | 4 | 5 | 2 |
| Security and governance integration | 15 | 4 | 3 | 4 | 2 |
| Reliability, replay and recoverability | 15 | 4 | 3 | 4 | 2 |
| Operability and team capability | 15 | 5 | 2 | 3 | 3 |
| Lifecycle cost | 10 | 4 | 2 | 3 | 3 |
| Interoperability and exit options | 10 | 4 | 3 | 4 | 2 |
| Scalability and performance | 10 | 3 | 5 | 4 | 2 |
| Delivery speed and reversibility | 5 | 4 | 3 | 3 | 4 |
| **Weighted total (1–5)** | **100** | **3.85** | **3.15** | **3.90** | **2.35** |
| **Evidence confidence** | — | Medium-low | Low | Medium-low | Low |

**Arithmetic check:** Option A = (20×3 + 15×4 + 15×4 + 15×5 + 10×4 + 10×4 + 10×3 + 5×4) / 100 = 3.85. Option B = 3.15, Option C = 3.90, and Option D = 2.35 using the same formula. Scores do not prove the result; they make the assumptions and judgement inspectable.

### 7.6 Interpretation and conclusion

**Provisional selection: Option C, hybrid by workload**, with a narrow, reversible pilot. It scores marginally higher than Option A by 0.05 points because it gives a more explicit route to the freshness-sensitive subset while retaining a batch path for workloads that do not need continuous processing. The 0.05 difference is not meaningful precision. The defensible rationale is the fit of the approach to two distinct workload classes—not the arithmetic alone.

Conditions before broad adoption:

1. Benchmark end-to-end freshness and throughput for the sensitive subset under representative peak load.
2. Test replay, deduplication/idempotency, late and out-of-order events, and failure recovery.
3. Threat-model both ingestion paths and shared governance/serving boundaries.
4. Demonstrate that access policies, lineage, retention and audit evidence are consistent across paths.
5. Produce a lifecycle cost model including runtime, support, monitoring, training and shared-service overhead.
6. Assign accountable owners for the shared pattern and each operational path.
7. Review pilot results and the matrix; change the decision if critical assumptions fail.

**Trade-offs accepted provisionally:** two processing modes increase architectural and operational complexity; the design must prevent duplicate governance logic and clarify which path a source uses. The team should not add streaming merely because it is available. If the pilot shows that micro-batch meets the freshness requirement with materially lower operational burden, revisit the streaming component.

**Why not Option B?** It may be appropriate for a predominantly event-driven estate with established streaming skills and compelling latency needs. Under these synthetic assumptions, streaming-first adds operational and cost burden to many sources that do not need it. This is not a general claim that streaming is expensive or unsuitable; actual economics and capabilities vary by implementation.

**Why not Option A alone?** It is the simpler baseline and could win if the 15-minute target can be met reliably by batch or micro-batch. That remains a testable uncertainty, not a settled fact.

**Why not the fragmented baseline?** It avoids immediate standardisation effort but leaves inconsistencies and unknowns. It may be acceptable as a short transitional state only if risks are owned, a review date is set, and the transition plan is credible.

### 7.7 Sensitivity check

Before deciding, ask whether the conclusion changes if a key assumption changes:

- If the 15-minute requirement is removed or relaxed, Option A may be preferable due to operability and cost.
- If nearly all sources become event-driven and the team develops strong streaming operations, Option B becomes more plausible.
- If the team cannot operate two modes safely, a single-path design or managed capability may be preferable even if the matrix score is slightly lower.
- If security or governance controls cannot be applied consistently across the hybrid design, the hybrid option must be redesigned or rejected.
- If measured cost differs materially from estimates, update the score and ADR rather than defend the original answer.

A useful decision is conditional and revisable. Record the triggers that would cause reassessment.

---

### 7.8 Filled decision-record example

The following short ADR illustrates how the comparison becomes a governed decision. All identifiers and details are synthetic. It is **proposed**, not evidence that a real Northbridge decision was approved.

```markdown
# ADR-006 (synthetic): Select a hybrid ingestion profile for the governed lakehouse

- Status: Proposed — pilot required
- Date: 2026-10-21 (illustrative)
- Decision owner: Data Platform Architecture Lead (role is illustrative)
- Scope: Analytics ingestion for scheduled extracts and the identified freshness-sensitive subset
- Related requirements: REQ-01 freshness; REQ-02 governed access; REQ-03 replay correctness (all synthetic)
- Related evidence: COMP-006 worked comparison; pilot evidence not yet available
- Related artefacts: target ingestion DFD; threat model; risk register; pattern catalogue

## Context
Northbridge needs governed self-service analytics for scheduled and selected near-real-time sources. The exercise assumes a 15-minute freshness target for a subset and an hourly tolerance for most scheduled data. Current workload measurements and production evidence are not supplied.

## Alternatives
A. Batch-first: simpler to operate; the freshness-sensitive subset needs proof or a separately designed path.
B. Streaming-first: plausible for low-latency sources; increases operational complexity for sources that do not need continuous processing under the exercise assumptions.
C. Hybrid by workload: separate batch and streaming/micro-batch paths with shared governance; adds cross-path complexity.
D. Keep fragmented patterns temporarily: avoids immediate change but leaves consistency and operational gaps unverified.

## Decision
Provisionally select C for a bounded pilot, not broad rollout. The selection is conditional on the acceptance criteria below. This is a context-specific choice, not a universal recommendation for lakehouses.

## Rationale
The scenario contains materially different freshness needs. A hybrid profile can match processing mode to workload while retaining shared governance. Its small weighted-score advantage over batch-first is not decisive; the main rationale is workload fit, and the pilot must test whether the additional complexity is justified.

## Consequences and risks
- Positive: a clear path for the freshness-sensitive subset without forcing every source into continuous processing.
- Negative: two paths require consistent identity, policy, lineage, observability, replay and support practices.
- Risks: duplicate records, inconsistent controls, unclear ownership, unanticipated cost and missed freshness objectives.
- Controls: representative latency and replay tests; cross-path threat review; shared contract and control checks; named run owners.

## Conditions and acceptance criteria
1. Demonstrate freshness under representative peak load using a defined measurement boundary.
2. Pass replay/idempotency and recovery tests, including late-arriving events where relevant.
3. Demonstrate consistent access policy, lineage and audit evidence across paths.
4. Review lifecycle cost and operational burden with stated workload assumptions.
5. Assign accountable build/run/support owners before production rollout.

## Revisit triggers
Reopen if the freshness target changes, batch/micro-batch meets the requirement with materially less operational burden, controls cannot be applied consistently, pilot cost is outside the approved envelope, or test evidence fails.
```

**Why this ADR is useful:** it records the decision status honestly, includes the baseline, links the rationale to the matrix without treating the score as proof, makes consequences explicit, and defines evidence that could invalidate the choice. A production ADR should replace role labels, synthetic requirement IDs and generic artefact names with actual owners and authoritative links.

### 7.9 Filled adaptation and exception example

Assume a separate, explicitly hypothetical governance review has verified that an internal standard **STD-META-01 v2** is approved, applies to this service, and requires an automated metadata publication event for every production data product. This hypothetical rule is not a repository requirement. A legacy source cannot publish the event until a planned replacement. The authorized approver has authority under the fictional governance model to grant a time-limited exception.

**Adaptation/deviation record — DEV-02 (synthetic)**

| Field | Record |
|---|---|
| Difference | The legacy source path emits a signed extraction manifest and reconciliation result to the catalog integration instead of the normal metadata publication event. |
| Reason | The source cannot emit the required event before replacement; the alternative is limited to one named legacy feed. |
| Expected benefit | Makes ownership, extraction time and reconciliation status discoverable during the transition. |
| Limitations | The manifest is not assumed equivalent to the standard event; lineage granularity and freshness may be lower. |
| Controls | Restrict scope, validate manifest schema, reconcile expected and observed extracts, alert on missing/stale manifests, review access logs, and test the fallback. |
| Owner | Named source-domain owner (placeholder to be replaced in a real record). |
| Validation | Test missing, duplicate, stale and malformed manifests; verify reconciliation and alert response. |
| Closure | Replace the legacy path, demonstrate the required event end-to-end, reconcile metadata, and close the deviation after review. |

**Exception record — EXC-01 (synthetic)**

| Field | Record |
|---|---|
| Rule | Hypothetical STD-META-01 v2, verified as binding and applicable for this exercise. |
| Scope | One named legacy feed and its production environment only; no general waiver. |
| Decision | Approved for a bounded transition period by the fictional authorized approver; actual approval would require the real governance authority. |
| Residual risk | Catalog metadata may be less timely or granular than the required event; investigation and impact analysis may be slower. |
| Compensating controls | Signed manifest, scheduled reconciliation, alerting, restricted consumer access where needed, and tested operational response. |
| Owner and review | Accountable source owner; review before expiry and on any new consumer, sensitivity change, or failed reconciliation. |
| Expiry | 90 days from the illustrative approval date, or earlier if the legacy source is replaced. The date is a teaching assumption. |
| Closure criteria | Required event is emitted and validated; historical metadata reconciles; tests pass; reviewer confirms scope no longer needs the exception. |
| Failure to close | Reassess and escalate through the actual governance authority; do not silently renew or assume approval continues. |

The decision is justified only if the compensating controls actually address the stated risk and the residual risk is accepted by an authorized person. If the rule's authority or applicability cannot be verified, this must remain a proposed deviation—not an approved exception.

## 8. Intermediate: standards governance and exceptions

### 8.1 What makes a standard operationally useful?

A standard should solve a real coordination, quality, safety, interoperability, or lifecycle problem. It should state a requirement that can be understood and checked. If it only says “use good architecture,” it cannot reliably guide design or conformance review.

A lightweight lifecycle may include:

1. **Propose:** state the recurring problem, affected systems, evidence, options, costs and intended scope.
2. **Review:** involve architecture, security/privacy, platform operations, domain teams, procurement or other affected functions as relevant to the proposal.
3. **Pilot:** test the proposed rule on representative workloads; record benefits, failure modes, exceptions and migration cost.
4. **Approve:** the authorized decision-maker records status, scope, effective date and exception authority.
5. **Publish:** provide the normative statement, rationale, examples, validation method, owner, version and support path.
6. **Conform:** use proportionate design review, automated checks where feasible, and evidence-based sampling.
7. **Exception:** permit a bounded deviation only through an explicit decision with compensating controls and expiry.
8. **Review and retire:** measure usefulness, revisit drift and incidents, update or deprecate obsolete rules, and provide a transition period where needed.

This is a proposed governance pattern. Actual roles and approval powers must come from the organization’s governance model, not be inferred from this lesson.

### 8.2 Tiered guidance: must / should / may

A tiered vocabulary can help distinguish obligation from advice, but it must be defined in the policy itself.

| Tier | Intended meaning | Typical handling | Example (illustrative only) |
|---|---|---|---|
| **Must** | Required within the stated scope unless an authorized exception is granted. | Conformance evidence; documented exception path. | “Shared data products must identify an accountable owner.” |
| **Should** | Preferred because it is generally beneficial; deviations require a reasoned explanation if the governance process says so. | Review rationale and consequences; escalation only if policy specifies it. | “Prefer idempotent writes for replayable pipelines.” |
| **May** | Permitted option, not a requirement. | Local decision based on context. | “Teams may use batch or streaming ingestion where the workload supports the choice.” |

The example statements above are teaching examples, not adopted Northbridge or repository standards. Avoid using *must* casually: every mandatory rule needs a defined scope, authority, rationale, conformance approach and exception route.

### 8.3 What an exception is—and is not

An **exception** is an authorized, bounded permission to depart from an applicable rule for a stated context. It is not the same as an undocumented deviation from a non-binding reference. A **deviation** describes a difference from a reference or pattern; it may be acceptable without an exception if no binding rule is violated. An **adaptation** is a deliberate change to make a pattern fit; it can be the right design and need not indicate non-conformance.

| Situation | Record needed | Typical governance question |
|---|---|---|
| Pattern differs from a reference diagram, but no rule is violated | Adaptation/deviation record and ADR link | Is the change justified, safe, and understood? |
| A guideline is not followed | Rationale may be sufficient under local policy | Does the alternative better fit this context? |
| An approved mandatory rule cannot be met | Formal exception request and authorized decision | Who may accept the risk, for how long, with what controls? |
| Many teams repeatedly request the same exception | Exception trend plus standard review | Is the standard too strict, outdated, or poorly scoped? |
| A reference is obsolete or its assumptions no longer hold | Catalogue review and version/retirement decision | Should the reference be updated, replaced, or withdrawn? |

An exception should normally include scope, rationale, risk, compensating controls, accountable owner, approver, start date, expiry date, review trigger, closure criteria and evidence. An expiry date is not cosmetic. It prevents temporary risk acceptance from becoming permanent by neglect.

### 8.4 Compensating controls

A compensating control reduces a specific exposure when the preferred control or standard cannot be applied. It is not automatically equivalent to the original control. State:

- the requirement that cannot be met and why;
- the risk scenario and affected assets/flows;
- the alternative control and the threat it addresses;
- how the control will be tested and monitored;
- remaining gaps and residual risk;
- the person authorized to accept that residual risk;
- the date or event that forces review.

For example, if a synthetic legacy source cannot yet publish the preferred metadata interface, a temporary, monitored extraction manifest and reconciliation process might reduce lineage uncertainty. That would not magically make lineage complete; the residual gap, owner and retirement plan remain explicit.

### 8.5 Exception lifecycle and escalation

A practical state model is:

`Draft → Under review → Approved / Rejected → Active → Renewed / Remediation in progress → Closed / Expired`

A denied request is not “active.” An approved request should not be treated as permanently approved if its expiry or scope is exceeded. Escalate when the owner is missing, controls fail, the scope changes, expiry is near, risk increases, or the same exception pattern suggests a defective standard. Exact thresholds and authorities must be defined locally.

---

## 9. Advanced: adaptation, drift and portfolio governance

### 9.1 Adapt deliberately, not cosmetically

A reference architecture is a starting point. Adaptation should preserve the problem-solving intent while making the changed assumptions and consequences explicit. Ask:

1. Which requirement or contextual force motivates the adaptation?
2. Which reference element, relationship, boundary or control changes?
3. What capability is removed, replaced, added or split?
4. Which quality attributes improve or worsen?
5. Does the change alter trust boundaries, data movement, failure domains, ownership, cost, or recovery?
6. Which ADR, diagram, threat model, risk, interface contract and runbook must change?
7. How will the adaptation be validated, and what result would cause rollback or reconsideration?
8. Who owns the adapted pattern and future maintenance?

An adaptation can be better than the reference for a specific workload, but it weakens the value of reuse if every team independently reinvents core controls, interfaces or support. Distinguish local variation from a reusable improvement worth feeding back into the catalogue.

### 9.2 Architecture drift and conformance

**Conformance** asks whether an implementation meets an applicable rule or declared reference profile. **Drift** is a difference from the expected or recorded architecture over time. Drift is not automatically bad: it may be an approved adaptation, a deliberate evolution, an expired exception, or accidental divergence. The first task is classification and impact assessment.

A proportionate conformance approach may combine:

- automated checks for properties that are machine-verifiable (for example, required metadata fields or deployment policy checks, if supported by actual tooling);
- architecture review for contextual decisions that require judgement;
- periodic evidence sampling and inventory reconciliation;
- exception-age and exception-recurrence reporting;
- review after significant incidents, migrations, new data classes, new trust boundaries, or material changes in workload;
- owner-confirmed status for controls that cannot be observed automatically.

Automation checks only what it encodes. A passing policy check is not proof that every risk is addressed. An architecture diagram that matches the catalogue is not proof that the deployed system matches the diagram; implementation evidence is still required.

### 9.3 Measuring whether standardisation helps

Possible measures (choose only those relevant and define their denominators) include:

- adoption by eligible systems, not raw adoption count;
- percentage of conforming systems and number/age of active exceptions;
- time to approve or reject an exception;
- time from proposal to usable standard;
- recurring defects or incidents associated with a pattern;
- delivery lead time and rework for conforming versus non-conforming implementations;
- cost per workload unit under comparable load and service requirements;
- onboarding time, operational hand-off delays, and support burden;
- number of unmaintained or ownerless catalogue entries;
- percentage of references with current known-use evidence and recent review.

These metrics are diagnostic, not proof of causality. Differences between conforming and deviating systems may reflect workload, maturity or selection bias. Compare like with like, state limitations, and avoid rewarding compliance theatre. A standard that increases conformance but materially increases delivery delay or operational risk deserves review.

### 9.4 Keep a pattern catalogue healthy

A useful catalogue is curated, versioned and searchable. It should not be a dump of vendor diagrams. Every entry needs an owner and a review date; old entries should be marked deprecated or retired rather than silently left as current guidance.

Suggested lifecycle:

`Proposed → Piloted → Recommended → (Approved profile, if formally authorized) → Deprecated → Retired`

“Recommended” and “approved” are distinct states. Approval only has meaning if a named authority and scope exist. A pattern may be useful in one domain profile and inappropriate in another.

Review triggers may include incidents, repeated exceptions, material technology changes, new requirements, changed operating capabilities, cost regressions, or lack of maintenance. Capture **known uses** and the conditions under which they succeeded or failed; do not generalize from a single success story.

### 9.5 Vendor reference architectures and lock-in

A vendor-provided architecture may accelerate design and contain useful product-specific detail. It may also optimize for that vendor’s product set, commercial incentives, or preferred service boundaries. Evaluate it as a source with a perspective, not as a neutral authority.

Review:

- which components are vendor-specific versus conceptual;
- whether equivalent alternatives are possible and at what migration cost;
- data, metadata, identity, policy and observability portability;
- proprietary interfaces, managed-service dependencies, egress and exit costs;
- skills and support dependencies;
- whether the architecture can satisfy existing requirements without unnecessary services;
- whether claims have independent or workload-specific evidence;
- how the design behaves if one service becomes unavailable or a contract changes.

Do not conclude that a vendor architecture is inherently bad or inherently superior. It is a candidate design whose fit and lifecycle consequences must be assessed.

### 9.6 Combining patterns

Real architectures often combine patterns. Examples include batch ingestion for scheduled extracts plus streaming ingestion for selected event feeds, a lakehouse for analytical storage plus a serving API for operational consumers, or a hybrid integration path between on-premises and cloud systems.

Combining patterns can meet diverse requirements but introduces seams. Explicitly define:

- ownership of each path and shared capability;
- data contracts, identity propagation, schema evolution and error handling;
- consistency, deduplication, ordering and replay semantics;
- observability and incident hand-off across boundaries;
- common governance controls and where they are enforced;
- data duplication, retention, deletion and lineage behaviour;
- cost allocation and support responsibility;
- the migration or rollback path if the combination fails.

Do not combine two patterns merely because each is individually popular. Evaluate the composition, including interactions and emergent failure modes.

### 9.7 Revisit and reverse decisions responsibly

A decision should be revisited when evidence or context changes enough to challenge its rationale. Triggers can include workload growth, new data classification, new external dependency, incident trends, cost variance, new skills, changed recovery targets, expired exception, or a material change in a reference version.

Revisit without rewriting history:

1. preserve the original ADR and status;
2. link the new ADR to the old one as superseding or revising it;
3. record what changed and which evidence changed the conclusion;
4. update diagrams, requirements mapping, threat/risk records, standards profiles and catalogue entries;
5. plan migration and coexistence if the change is not instantaneous;
6. assign owners and dates for transition and retirement.

---

## 10. Relationships to architecture artefacts and operating model

### 10.1 Traceability map

| Artefact / governance mechanism | Role in pattern selection | Required link or consistency check |
|---|---|---|
| Requirements and constraints | Defines the problem and hard gates | Each important criterion maps to an authoritative requirement or a labelled assumption. |
| Architecture description and diagrams (Topics 01–03) | Shows current/target structures and stakeholder concerns | Selected pattern must fit the views; update affected diagrams and note limitations. |
| ADR and decision log (Topic 04) | Preserves alternatives, rationale and consequences | Decision ID, criteria, selected option, conditions, owner, status and revisit triggers. |
| Threat model and risk register (Topic 05) | Evaluates threats and residual risk | Link affected flows, trust boundaries, controls, risk owners and treatment actions. |
| Standards and exception register | States the applicable rule and any authorized departure | Standard ID/version, scope, authority, conformance evidence, exception approval and expiry. |
| Pattern/reference catalogue | Makes reusable knowledge discoverable | Entry ID, version, applicability, known uses, limitations, owner and review date. |
| Ownership/operating model (Topic 07) | Assigns build/run/support and decision accountability | One accountable party per relevant asset/decision; shared interfaces and support contracts are explicit. |
| Migration roadmap (Topic 08) | Sequences adoption and retirement | Adaptation work, dependencies, checkpoints, coexistence, rollback and decommissioning are planned. |
| Stakeholder communication (Topic 09) | Explains trade-offs to decision-makers | Business and technical briefs use the same facts and do not overstate evidence. |

### 10.2 Example trace chain

A synthetic selection might be traceable as follows:

`REQ-01 freshness target → comparison matrix row C1 → ADR-006 decision → DFD-02 event path → TM-03 threat scenario → RISK-08 replay integrity → DEV-02 hybrid-path adaptation → EXC-01 (only if a binding rule is actually waived) → owner/interface contract in Topic 07 → pilot checkpoint in Topic 08.`

All IDs in this chain are illustrative. The chain demonstrates traceability, not that the named requirements, threats or exceptions exist in a real environment.

### 10.3 Governance decision rights

Before selecting or standardising a pattern, clarify who can:

- recommend a pattern or propose a standard;
- approve a reference profile or mandatory rule;
- accept residual risk or grant an exception;
- own a shared implementation and its support commitments;
- approve a local adaptation within delegated limits;
- retire a catalogue entry or standard;
- resolve disagreement between domain needs and enterprise consistency.

Do not assume these powers belong to an “architecture board” unless the actual governance model says so. The right process is one that has clear authority, proportional review, documented outcomes, and a way to challenge or revisit the decision.

### 10.4 Lightweight review checklist

- [ ] Decision scope, context and accountable decider are clear.
- [ ] Requirements, hard constraints, assumptions and unknowns are separated.
- [ ] Candidate reference/pattern sources are versioned and their perspective is understood.
- [ ] At least two credible options and a baseline were considered, or a reason is recorded for not doing so.
- [ ] Criteria were defined before scoring and reflect stakeholder needs.
- [ ] Hard gates are evaluated separately from scored preferences.
- [ ] Evidence, confidence and unverified claims are visible.
- [ ] Security, governance, reliability, cost, operability, interoperability and team capability were considered where relevant.
- [ ] Every selected pattern has stated limitations and conditions of applicability.
- [ ] Adaptations/deviations have reasons, consequences, owners and validation plans.
- [ ] Any binding standard departure has an authorized exception with compensating controls and expiry.
- [ ] ADR, threat model, risk register, diagrams, catalogue and ownership records are linked and consistent.
- [ ] A pilot or other evidence-gathering step is defined where uncertainty is material.
- [ ] Revisit triggers, maintenance owner and review date are recorded.

---

## 11. Practical exercises with model answers

All exercises use synthetic Northbridge Bank data. They are designed to test method, not to prescribe a real banking architecture or establish a compliance position.

### 11.1 Beginner exercise — classify the artefact

**Task:** Classify each statement as reference model, reference architecture, pattern, standard, guideline, blueprint/implementation-specific design, or technology choice. More than one label may apply when the statement combines levels; explain the primary role.

1. “A data platform can be described using ingestion, storage, processing, governance and consumption capabilities.”
2. “For replayable ingestion, retain a source envelope and make sink writes idempotent.”
3. “The approved platform rule requires shared data APIs to publish a versioned schema and compatibility policy.”
4. “This diagram shows a generic governed lakehouse with landing, curated storage, catalog, policy enforcement and serving.”
5. “Deploy these named services into these subnets using this exact configuration.”
6. “Use a managed event service from Provider Z.”
7. “Prefer open data formats where they meet the workload requirements.”
8. “The proposed platform has source adapters, transformation workers, catalog integration, and two serving interfaces.”
9. “A taxonomy groups data assets by domain, sensitivity and lifecycle state.”
10. “This reference is mandatory for all workloads without exception.”

#### Model answers

| # | Primary classification | Reasoning / caveat |
|---:|---|---|
| 1 | Reference model | Names capabilities and conceptual relationships; it does not prescribe a deployment. |
| 2 | Pattern | Reusable solution advice for replay integrity. Applicability depends on source semantics, retention and downstream contracts. |
| 3 | Standard, if the approval claim is true | Its status depends on actual adopting authority, scope and conformance process. In this exercise the statement asserts approval; do not generalize it to the repository. |
| 4 | Reference architecture | A reusable structural template; it may still omit context-specific requirements and operational detail. |
| 5 | Blueprint or implementation-specific design | Concrete deployment instructions; their correctness depends on the target environment and maintenance state. |
| 6 | Technology choice | Names a provider/service. It may implement a pattern, but the statement alone is not a full architecture rationale. |
| 7 | Guideline | “Prefer” signals advice. It is not mandatory unless a defined authority makes it a standard. |
| 8 | Implementation-specific design (possibly a blueprint if sufficiently concrete) | It describes a proposed system; the level of detail and environment specificity determine whether it is a blueprint. |
| 9 | Reference model or taxonomy | Organizes concepts; it may inform governance but is not automatically a standard. |
| 10 | Claimed mandatory standard/profile, but suspiciously broad | Verify authority, scope, exception mechanism and evidence. A reference architecture should not become mandatory merely by being called a reference. |

**Validation criteria:** at least 8 of 10 classifications are defensible; the explanation distinguishes content from authority; no learner assumes a vendor choice is a pattern or a reference is automatically mandatory. A reviewer should discuss the reasoning on items 3 and 10 even if the label is correct.

### 11.2 Intermediate exercise — compare two lakehouse approaches

**Scenario:** Northbridge needs governed self-service analytics. Assume (synthetically) most sources are scheduled extracts, one subset needs freshness within 15 minutes, access must be role-controlled, and replay must not create duplicates. The platform team has limited streaming operations experience. Compare a batch-first approach with a hybrid-by-workload approach.

**Tasks:**

1. List hard requirements, assumptions and unknowns separately.
2. Define at least six criteria before scoring.
3. Identify one hard gate and at least two scored preferences.
4. Complete the matrix below with evidence or assumptions, not just numbers.
5. Recommend a pilot or decision and state what evidence could change the outcome.

| Criterion | Weight (example) | Batch-first score | Hybrid score | Evidence / uncertainty |
|---|---:|---:|---:|---|
| Freshness fit | 25 |  |  |  |
| Governance consistency | 15 |  |  |  |
| Replay/recovery | 15 |  |  |  |
| Operability/team capability | 15 |  |  |  |
| Lifecycle cost | 10 |  |  |  |
| Interoperability/exit | 10 |  |  |  |
| Delivery speed/reversibility | 10 |  |  |  |

#### Model answer (one defensible outcome)

- **Hard gate:** demonstrate the 15-minute target for the specified subset with representative workload and failure/recovery behaviour. Neither pattern name is proof of meeting it.
- **Assumptions:** most sources tolerate scheduled processing; team experience is limited; governance controls can be shared across paths. Assign owners and validation dates.
- **Unknowns:** peak throughput, event ordering, late-arrival rates, measured costs, actual operational coverage, and whether micro-batch alone meets the freshness target.
- **Illustrative scores:** batch-first may score higher for operability and cost; hybrid may score higher for freshness fit and still acceptable governance if shared controls are designed deliberately. Score anchors and evidence must be consistent across both options.
- **Recommendation:** run a bounded pilot comparing batch/micro-batch and the hybrid event path. Measure end-to-end freshness, failure recovery, replay correctness, governance consistency, on-call effort and cost per workload unit. Select hybrid only if the measured benefit justifies the added complexity.

**Validation criteria:** criteria are fixed before scoring; hard gates are not hidden in a weighted total; both options receive comparable scrutiny; assumptions and unknowns have owners; the conclusion names trade-offs and a falsifying test. Several answers can be valid if evidence and reasoning support them.

### 11.3 Advanced exercise — selection, adaptation, deviation and exception

**Scenario:** Northbridge has provisionally selected a hybrid ingestion pattern. A synthetic domain team proposes a direct path from a source system to a curated dataset to meet a delivery deadline. The proposal omits the common metadata publication step described by a hypothetical internal standard. The actual standard's authority and scope have not yet been verified. The team claims that a manual runbook is enough.

**Tasks:**

1. Separate what is known from what is assumed or unverified.
2. Determine whether the proposal is an adaptation, deviation, or exception request; explain what evidence is needed to classify it.
3. Identify risks and compensating controls, and state what the runbook does not prove.
4. Write a concise selection ADR and a deviation record.
5. If the rule is confirmed as binding, create a bounded exception request; otherwise do not falsely label the deviation an approved exception.
6. Define the accountable owner, approver, expiry/review trigger and closure criteria.
7. List the diagrams and Topic 05 artefacts that must be updated.

#### Model answer

- **Known from the scenario:** a team proposes a direct path and omits a metadata publication step; the claimed standard authority/scope is unverified; the team proposes a manual runbook.
- **Not established:** whether the rule is mandatory, whether the direct path is technically safe, whether metadata can be captured through another mechanism, and whether the runbook is tested or staffed.
- **Classification:** record a proposed deviation from the reference/profile. Do not call it a formal exception until an applicable binding rule and authorized approval path are established. If the rule is binding, the team must seek an exception or redesign to conform.
- **Risks:** reduced discovery and lineage, missed ownership, delayed incident investigation, inconsistent policy enforcement, fragile manual steps and operator error. Risk severity depends on data sensitivity, consumers, controls and evidence; do not invent a final risk score.
- **Possible compensating controls:** machine-readable extraction manifest, automated metadata reconciliation, explicit owner and alerting, access restrictions, tested rollback, and a time-limited scope. These are candidates to test, not automatic equivalents to the omitted control.
- **ADR outcome:** do not approve broad production use based only on a deadline and an untested runbook. Permit a bounded pilot if the decision authority agrees, risks are acceptable, and measurable closure criteria are defined; otherwise defer or redesign.
- **Expiry/review:** a fixed date or earlier trigger such as metadata reconciliation failure, new consumers, sensitivity change, or the next release gate. Assign an accountable owner and named approving authority from the actual governance model.
- **Updates:** data-flow/deployment views, requirement trace, ADR/decision log, threat model, risk register, standard/exception register if applicable, pattern catalogue known-use entry, operational runbook, and ownership/interface records.

**Validation criteria:** no unsupported assertion that the runbook satisfies the standard; no exception without confirmed authority and approval; controls are testable; residual risk and expiry are explicit; affected artefacts are listed; the decision has a clear owner and revisit trigger.

### 11.4 Advanced exercise — tiered standards framework

**Task:** Propose a lightweight standard for a fictional data platform covering ingestion, storage, security and observability. Define *must/should/may*, approval authority, evidence for new standards, conformance measures, exception handling, and retirement. Apply it to three synthetic proposals:

- **Proposal A:** conforms to the proposed rule and supplies test evidence.
- **Proposal B:** cannot meet one requirement before a legacy source is replaced; proposes a compensating control and a 90-day review.
- **Proposal C:** repeatedly requests the same exception as several other teams, suggesting the rule may not fit a workload class.

#### Model rulings

| Proposal | Illustrative ruling | Required rationale and follow-up |
|---|---|---|
| A | Accept as conforming, subject to normal design review | Verify evidence scope, owner and continued applicability. Conformance is not a blanket security certification. |
| B | Consider a time-bounded exception only if the rule is confirmed binding and the authorized approver accepts residual risk | Document exact scope, compensating control tests, owner, expiry, review trigger and migration/closure plan. If no binding rule exists, record a deviation/adaptation instead. |
| C | Do not blindly renew each exception | Analyse recurrence, risk, costs and workload differences; pilot a revised profile or update the standard if evidence supports it. Maintain controls during review. |

**Validation criteria:** the framework distinguishes guidance from mandatory rules; authority and scope are explicit; conformance measures have denominators and evidence sources; exceptions expire; repeated exceptions trigger review of the standard; no fabricated legal obligation is introduced.

---

## 12. Reusable templates

Copy and adapt these templates. They are recommendations, not pre-existing repository policies. Use stable identifiers and link to authoritative artefacts where available.

### 12.1 Reference/pattern applicability assessment

```markdown
# Applicability assessment — [reference/pattern ID]

- Assessment ID:
- Title and version/date of source:
- Source type: reference model / reference architecture / pattern / standard / guideline / blueprint
- Source owner/publisher and perspective:
- Assessment owner and date:
- Status: draft / reviewed / accepted / rejected / revisit
- Decision scope and exclusions:

## Problem and context
- Problem to solve:
- Business and technical drivers:
- Relevant requirements/constraints:
- Workload and data characteristics:
- Stakeholders and consumers:

## Assumptions and unknowns
| ID | Statement | Type (fact/reported/assumption/inference/unknown) | Evidence | Owner | Validation date/trigger |
|---|---|---|---|---|---|

## Applicability
| Question | Finding | Evidence | Gap / consequence | Action / owner |
|---|---|---|---|---|
| Problem and forces match? | | | | |
| Scope and assumptions hold? | | | | |
| Hard constraints satisfied? | | | | |
| Quality attributes fit? | | | | |
| Security/governance fit? | | | | |
| Operations and skills fit? | | | | |
| Lifecycle cost and exit fit? | | | | |

## Conclusion
- Applicable as-is / adapt / reject / pilot / defer:
- Rationale:
- Known limitations:
- Required adaptations:
- Risks and mitigations:
- Related ADR / threat model / risk register / diagrams:
- Owner, review date and revisit triggers:
```

### 12.2 Alternative comparison matrix

```markdown
# Architecture option comparison

- Decision ID:
- Decision owner / decider:
- Date and status:
- Scope and exclusions:
- Requirements and source links:
- Criteria and weights approved by:

## Hard gates (pass/fail; not included in weighted score)
| Gate ID | Requirement | Option A | Option B | Option C | Evidence / exception needed |
|---|---|---|---|---|---|

## Scored criteria
| Criterion | Definition / scoring anchors | Weight | Option A score / confidence | Option B score / confidence | Option C score / confidence | Evidence / unknowns |
|---|---|---:|---|---|---|---|

## Summary
- Arithmetic method and check:
- Sensitivity to weights/assumptions:
- Material risks and limitations:
- Baseline considered:
- Preferred option and why:
- Conditions, pilot and falsifying evidence:
- Revisit triggers:
```

### 12.3 ADR for selecting a reference or pattern

```markdown
# ADR-[ID]: [decision title]

- Status: proposed / accepted / rejected / superseded / deprecated
- Date:
- Decision owner / approver:
- Related requirements:
- Related reference/pattern/standard IDs and versions:
- Related diagrams, threat model, risk register and prior ADRs:

## Context
Describe the problem, scope, stakeholders, drivers, constraints and current state.

## Requirements, assumptions and unknowns
Separate verified requirements from assumptions, reported claims and unresolved questions.

## Decision criteria
List hard gates separately from scored preferences. Explain criteria and weights.

## Alternatives considered
For each option, state fit, evidence, limitations, costs and why it was not selected (if applicable). Include a credible baseline.

## Decision
State the selected approach and its scope. Avoid claiming it is universally best.

## Rationale and evidence
Explain the decisive trade-offs and confidence level. Link evidence and calculations.

## Consequences
- Benefits:
- Costs and operational burden:
- Security/governance implications:
- Portability/lock-in:
- Risks and compensating controls:
- Team/ownership implications:

## Adaptations, deviations and exceptions
Link records; state any required approvals, expiry and residual risk.

## Validation and follow-up
Actions, owners, due dates, acceptance criteria, pilot and rollback plan.

## Revisit triggers
State what evidence or context change would reopen the decision.
```

### 12.4 Deviation/adaptation record

```markdown
# DEV-[ID]: [difference from reference/pattern]

- Status: proposed / accepted / rejected / closed
- Reference/pattern ID and version:
- Affected system, domain, flow and environment:
- Proposer / accountable owner / reviewer:
- Date and next review:

## Baseline
What does the reference/profile describe? Cite exact version and relevant section/element.

## Difference
What is changed, omitted, added, split or replaced?

## Reason and evidence
Which requirement, force or constraint motivates the change? Separate fact from assumption.

## Impact analysis
| Dimension | Expected effect | Evidence / uncertainty | Mitigation / owner |
|---|---|---|---|
| Security/privacy | | | |
| Governance/lineage | | | |
| Reliability/recovery | | | |
| Performance/scalability | | | |
| Cost/operability | | | |
| Interoperability/exit | | | |
| Ownership/interfaces | | | |

- Related ADR:
- Threat-model / risk-register links:
- Required diagram/catalogue/runbook updates:
- Validation and closure criteria:
- Review trigger/date:
```

### 12.5 Standards exception request

```markdown
# EXC-[ID]: [rule and requested scope]

- Applicable standard/policy ID, version and exact requirement:
- Evidence that it is binding and applies to this scope:
- Requester / accountable risk owner:
- Authorized approver (per actual governance model):
- Affected system, data, interfaces and environments:
- Requested start date:
- Expiry date (required for a time-bounded exception):
- Status: draft / under review / approved / rejected / active / closed / expired

## Reason conformance is not currently feasible
Describe constraints, alternatives considered and why redesign is not selected.

## Risk assessment
Threat/scenario, likelihood/impact rationale, affected assets, existing controls, residual risk and risk-register link.

## Compensating controls
| Control | Threat addressed | Test/monitoring evidence | Owner | Failure response |
|---|---|---|---|---|

## Conditions
- Approved scope and exclusions:
- Restrictions during exception:
- Review trigger and date:
- Remediation / closure plan:
- Consequence if expiry is reached without closure:
- Approval decision and rationale:
```

**Guardrail:** if the rule is not actually binding or does not apply, do not create a fake exception. Use a deviation/adaptation record and clarify the standard's scope with its owner.

### 12.6 Pattern catalogue entry

```markdown
# PAT-[ID]: [pattern name]

- Version / status: proposed / piloted / recommended / approved profile / deprecated / retired
- Pattern owner:
- Created / last reviewed / next review:
- Source and related references:
- Applicable domains and workload classes:

## Problem
What recurring problem does this pattern address?

## Context and forces
Requirements, constraints, scale, latency, trust, skills and operational conditions.

## Solution sketch
Components, relationships, interfaces, flow and control points. Link to diagrams where available.

## Quality attributes
Expected benefits, required controls and validation method.

## Consequences and limitations
Costs, failure modes, lock-in, team skills, known non-fit cases and operational burden.

## Variants and related patterns
When to combine, adapt or choose a different pattern.

## Known uses and evidence
Context, version, outcomes, evidence scope and limitations; label synthetic examples.

## Governance
Applicable standards/profile, exception path, conformance checks and change process.

## Ownership and lifecycle
Maintenance owner, support expectations, deprecation trigger and migration guidance.
```

### 12.7 Lightweight standards proposal

```markdown
# STD-PROP-[ID]: [proposed rule]

- Proposer / sponsor / decision authority:
- Scope and exclusions:
- Proposed tier: must / should / may (define locally)
- Problem and evidence:
- Options considered, including no new standard:
- Proposed normative statement:
- Rationale and expected benefit:
- Implementation and migration cost:
- Pilot scope, success measures and failure criteria:
- Conformance evidence and review method:
- Exception authority, controls and expiry rules:
- Owner, version, effective date and review date:
- Deprecation / retirement plan:
- Approval decision and rationale:
```

### 12.8 Decision log entry

| Decision ID | Date | Title | Status | Selected reference/pattern | Scope/profile | Owner/decider | Linked ADR | Open conditions / revisit trigger |
|---|---|---|---|---|---|---|---|---|
| ADR-006 (synthetic) | 2026-10-21 | Hybrid ingestion for governed lakehouse | Proposed | PAT-HYBRID-01 (synthetic) | Analytics ingestion; pilot only | Platform architecture lead (illustrative) | ADR-006 | Revisit after freshness, replay, governance and cost pilot |

The example row is synthetic and does not represent a real decision. Use a stable ID, status and source links in the actual project.

---

## 13. Common mistakes and corrective practices

| Mistake | Why it fails | Correction |
|---|---|---|
| Treating a reference architecture as mandatory by default | Guidance may not fit the context; authority is assumed rather than established. | Check source status, local adoption, scope, constraints and exception authority. |
| Selecting a pattern because it is popular or fashionable | Popularity does not demonstrate workload fit. | Define criteria first and compare credible alternatives with evidence. |
| Scoring before identifying hard constraints | A high total can hide an unacceptable requirement failure. | Apply eligibility gates before weighted scoring. |
| Comparing one option using detailed evidence and another using marketing claims | Creates an unfair result. | Use the same evidence expectations; label reported claims and unknowns. |
| Treating a reference diagram as implementation proof | A diagram expresses intent, not deployment state. | Verify configuration, tests, inventories, logs and operational evidence as appropriate. |
| Ignoring the baseline or “do nothing” option | Reuse benefits are exaggerated when no alternative is visible. | Compare with the current state or a simple credible alternative, including its risks. |
| Double-counting benefits in a weighted matrix | Produces distorted rankings. | Define non-overlapping criteria and perform sensitivity checks. |
| Treating an ordinal score as a precise measurement | Small numerical differences may be meaningless. | Show evidence confidence, uncertainty and what would change the choice. |
| Ignoring maintenance and lifecycle costs | The initial build looks cheap while support, upgrades and exit costs accumulate. | Model build/run/change/exit cost and assign an owner. |
| Creating standards without authority or conformance method | Teams cannot tell what is required or how compliance is judged. | Define scope, authority, normative wording, evidence, exception process and review. |
| Permanent or unreviewed exceptions | Risk acceptance becomes invisible and can outlive its rationale. | Require owner, controls, expiry, triggers and closure evidence. |
| Repeated exceptions are handled one at a time forever | A systemic mismatch remains hidden. | Review the standard/profile and workload segmentation when exceptions recur. |
| Deviations are undocumented | Reviewers cannot distinguish deliberate adaptation from accidental drift. | Maintain a deviation record linked to ADR, risks and affected views. |
| Vendor reference architecture is accepted uncritically | Product incentives and lock-in may be missed. | Evaluate neutral core, proprietary dependencies, portability and exit costs. |
| Catalogue has no owner or review date | Obsolete guidance remains discoverable and appears current. | Version entries, record known uses and retire stale patterns explicitly. |
| Pattern combination is evaluated only component by component | Interactions can create new failure modes and ownership gaps. | Review seams, data contracts, identity propagation, recovery and cross-team operations. |
| “Compliant by design” is asserted without evidence | A label is mistaken for verified compliance. | State the actual requirement and authority; use qualified review and traceable evidence. |
| A score or ADR is treated as permanent | Workloads, evidence, skills and constraints change. | Define revisit triggers and supersede decisions without rewriting history. |

---

## 14. Practice questions and answer key

### Questions

1. What is the key difference between a reference model and a reference architecture?
2. Why is a pattern not automatically a standard even if many teams use it?
3. What should happen before applying a weighted comparison matrix?
4. Why should a baseline be included?
5. What is the difference between a deviation and an exception?
6. Why should hard constraints be treated separately from weighted preferences?
7. What evidence would strengthen a claim that a hybrid ingestion pattern meets a 15-minute freshness target?
8. Why is a vendor reference architecture not automatically neutral evidence?
9. What should happen if multiple teams repeatedly request the same exception?
10. Which Topic 04 artefact preserves the rationale for a pattern selection?
11. How should the decision package change if a pattern adaptation changes a trust boundary?
12. What information makes an exception meaningfully time-bounded?
13. Can an automated conformance check prove the complete architecture is safe? Explain.
14. Name two conditions that should trigger a pattern catalogue review.
15. What must be assigned before a shared pattern is considered operationally reusable?

### Answers

1. A reference model organizes domain concepts and relationships; a reference architecture proposes a reusable structural arrangement for a class of problems.
2. Usage frequency does not establish authority. A standard requires a defined scope and an adopting authority, plus a conformance and exception process appropriate to its status.
3. Define the decision scope, requirements, assumptions, hard gates, criteria, scoring anchors and credible options. Test eligibility before scoring.
4. A baseline reveals the costs and risks of not adopting the candidate reference and prevents a false comparison in which every alternative is worse by construction.
5. A deviation records a difference from a reference/profile. An exception is authorized permission to depart from a binding rule that applies to the scope.
6. A hard constraint is not a preference that can be compensated by a high score elsewhere. Failure requires exclusion, redesign or a valid authorized exception.
7. Representative end-to-end workload tests covering peak load, source-to-consumer latency, failure/recovery, late events and the actual measurement boundary; record environment, scope and limitations.
8. It may optimize for a vendor's own products, interfaces and commercial model. Evaluate the source's perspective, portability, alternatives and evidence.
9. Analyse recurrence and root cause. The standard may be too broad, stale or poorly profiled; consider revising it based on evidence while controlling existing risks.
10. An ADR, with a corresponding decision-log entry and links to supporting artefacts.
11. Update relevant diagrams/DFDs, threat model, risk register, ADR/deviation record, standards/exception records if applicable, ownership/interface documentation and runbooks.
12. A specific expiry date, owner, authorized approver, scope, review triggers, compensating controls, residual-risk decision and closure plan.
13. No. It proves only the encoded checks passed for the evaluated scope. Unmodelled risks, implementation gaps and operational failures still require appropriate review and evidence.
14. A material incident or recurring exception; a new requirement, workload class, dependency or technology change; cost regression; or a stale review date.
15. An accountable owner, support expectations, lifecycle maintenance, interface and change process, validation approach, and a way to deprecate or replace it.

---

## 15. Deliverables, mastery criteria and completion gate

### 15.1 Expected deliverables

The module roadmap recommends these Topic 06 outputs:

- [ ] Classification of reference models/architectures, patterns, standards and related guidance.
- [ ] Applicability assessment and comparison of alternatives.
- [ ] ADR documenting the selection and consequences.
- [ ] Deviation/adaptation records for every material difference from the chosen reference/profile.
- [ ] Exception records for approved departures from applicable binding rules, with compensating controls and expiry.
- [ ] Pattern catalogue entry and a lightweight standards-governance outline.
- [ ] Links to relevant diagrams, Topic 05 threat/risk artefacts, requirements and ownership records.

These are learning deliverables recommended by the roadmap; they are not claims that a repository policy already mandates this exact format.

### 15.2 Mastery criteria

You have demonstrated mastery when you can:

- assess applicability with evidence rather than assumption alone;
- distinguish mandatory rules from advisory guidance and verify authority/scope;
- compare options with consistent criteria, an explicit baseline and honest uncertainty;
- explain the costs of both reuse and non-reuse across the lifecycle;
- document adaptations, limitations and consequences;
- handle exceptions through the appropriate authority, controls, owner, expiry and review;
- explain why the selected pattern is suitable under stated assumptions and what evidence would cause reconsideration.

### 15.3 Completion gate

Do not move on solely because the document is complete. Confirm all of the following:

- [ ] A reviewer has examined the comparison matrix and ADR.
- [ ] Every selected pattern has stated limitations and applicability conditions.
- [ ] Material deviations/adaptations are recorded with reasons, impacts, owners and validation.
- [ ] Any binding-rule exception has verified scope/authority, approval, compensating controls, expiry and residual-risk ownership; non-binding deviations are not mislabelled as exceptions.
- [ ] The decision is traceable to requirements, diagrams, Topic 05 threats/risks and relevant governance artefacts.
- [ ] The pattern-catalogue entry has an owner and review date.
- [ ] Practice questions are attempted and learning gaps are logged.
- [ ] The conclusion explains both reuse benefits and lifecycle costs, including uncertainty and revisit triggers.
- [ ] **Readiness:** you can align teams, ownership, interfaces and operational responsibilities with the selected architecture in Topic 07.

---

## 16. Readiness for Topic 07

Topic 07 — **Team boundaries, ownership and platform operating model** — moves from the design decision to the people and operating arrangements that build, run, support and evolve it. Before proceeding, answer these questions for your selected pattern:

- Who owns the shared pattern or reference profile and maintains its documentation?
- Which team builds and runs each component, and who is accountable for cross-team interfaces?
- Who approves local adaptations, standards changes and exceptions?
- Who supports the pattern at incident time, and what are the escalation and hand-off paths?
- How do domain teams contribute improvements and report a pattern that no longer fits?
- Who pays for shared capabilities, and how are costs and service expectations made visible?
- How will the organization avoid a central platform team becoming an approval bottleneck while retaining necessary governance?
- What happens to consumers and operational ownership when the pattern is deprecated?

If these questions have no answers, the architecture decision is incomplete from an operating perspective. Record the gaps and carry them into Topic 07 rather than inventing team names or assuming that “the platform team” owns everything.

**Topic 06 in one sentence:** choose reusable architecture with evidence and context, preserve the reasoning, make deviations and exceptions explicit, maintain the catalogue and standards as living assets, and assign ownership so the decision can be operated and evolved.
