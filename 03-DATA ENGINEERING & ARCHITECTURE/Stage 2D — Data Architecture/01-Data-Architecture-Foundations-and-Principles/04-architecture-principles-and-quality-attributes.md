# Architecture Principles and Quality Attributes

> **Stage 2D — Data Architecture**  
> **Module:** 01 — Data Architecture Foundations and Principles  
> **Lesson file:** `04-architecture-principles-and-quality-attributes.md`  
> **Progression:** Beginner → Intermediate → Advanced → Industry application

## 1. Learning objective

By the end of this lesson, you should be able to:

- Write architecture principles that guide real decisions using a clear **statement, rationale and implications**.
- Translate business drivers, constraints and assumptions into quality attribute priorities and measurable requirements.
- Define a quality requirement with a metric, target, measurement window, scope and verification method.
- Evaluate two candidate architectures against principles and quality requirements using evidence, explicit uncertainty and justified trade-offs.
- Prioritise qualities differently for different data assets and business capabilities.
- Resolve conflicts between principles and document, approve, monitor and expire justified exceptions.
- Recognise principles that are vague, conflicting, unknown to delivery teams or routinely bypassed.

**Expected evidence:** a principles set of no more than eight principles, a measurable quality-target table for the banking scenario, a scorecard comparing two designs, a written trade-off analysis, and a complete exception record.

All numerical targets and candidate scores in this lesson are **illustrative assumptions for learning**, not verified bank requirements, benchmark results or claims about measured systems. In a real architecture decision, replace them with business-approved targets and measured evidence.

## 2. Why this topic matters in real-world Data Architecture

Organisations make many data decisions across teams and projects. Without principles, similar decisions may be made inconsistently; without measurable quality requirements, terms such as “fast,” “secure,” “reliable” and “cost-effective” remain open to interpretation. Teams can then disagree about design while each claims to be meeting the business need.

Architecture principles provide durable decision guidance. Quality attributes make expectations concrete enough to evaluate. A good architecture decision connects the two:

```text
Business driver / obligation
          ↓
Architecture principle
          ↓
Quality attribute and measurable requirement
          ↓
Candidate design and evidence
          ↓
Decision, trade-off, risk and any approved exception
          ↓
Verification in operation and review when evidence changes
```

The chain is not always strictly linear. One business driver may lead to several principles; a principle may affect several quality attributes; and a quality attribute may have different targets for different assets. The point is to make the reasoning visible.

### 2.1 The key distinctions

| Concept | Meaning | Example | Common confusion |
|---|---|---|---|
| **Architecture principle** | A durable rule or direction used to guide decisions, with a rationale and implications. | “Every material shared data asset has an accountable business owner or an explicitly tracked ownership gap.” | Treating a principle as a slogan or a detailed implementation instruction. |
| **Requirement** | A specific condition a solution must satisfy. | “The transaction dashboard shall show data no older than 60 seconds for 99% of refresh checks during the agreed business window.” | Mistaking broad guidance for a testable requirement. |
| **Quality attribute** | A property of a system or data service that matters to stakeholders. | Freshness, availability, reliability, privacy or maintainability. | Treating the quality word itself as a measurable target. |
| **Metric** | The defined measurement used to assess an attribute. | Age of the newest successfully published transaction at dashboard query time. | Using a metric without defining its start/end points or population. |
| **Target** | The desired threshold or outcome for a metric. | p95 freshness ≤ 60 seconds during the business window. | Claiming the target is met without observations. |
| **Observed measurement** | A result collected using the defined method over a stated period. | p95 freshness was 74 seconds over the previous 14 days. | Presenting an intended target as an achieved result. |
| **Constraint** | A condition that restricts the solution space. | A contract requires data to remain in an approved jurisdiction. | Calling a preference or unverified belief a constraint. |
| **Assumption** | A proposition treated as true for planning until validated. | “The source emits a change event within five seconds.” | Building a design on an assumption without assigning validation. |
| **Policy** | A formally adopted organisational rule or obligation, often with defined authority and enforcement. | A policy prohibits exporting a defined class of sensitive data to an unapproved environment. | Treating an informal principle as if it had formal policy authority. |
| **Standard** | An approved, more specific and commonly mandatory way of satisfying a policy or implementing a principle within its stated scope. | A standard specifies the approved encryption baseline for a classified data store. | Confusing a standard's prescriptive control with the broader decision direction of a principle. |
| **Design decision** | A context-specific choice among alternatives, supported by criteria, evidence, trade-offs and an accountable decision. | Choose a scheduled feed or event-driven feed for a defined transaction use case. | Treating a single project choice as a universal principle. |
| **Exception / deviation** | A recorded and authorised departure from a principle or standard under stated conditions. | A time-limited, masked analytical extract approved for a defined experiment. | Treating a violation as approved because a team has already implemented it. |

### 2.2 Why vague principles are expensive

A statement such as “use modern technology” cannot reliably distinguish two options. “Use best-of-breed technology” may encourage a tool that excels in isolation but creates integration, operating, skills or cost problems for the organisation. A principle should help decide between alternatives, explain why the decision matters, and imply observable consequences.

**Purpose:** reduce arbitrary or contradictory decisions, not remove judgement.  
**How it works:** the principle provides a decision direction; requirements and evidence test candidate solutions against the context.  
**When useful:** recurring cross-team choices, high-impact or hard-to-reverse decisions, and areas where inconsistency creates risk.  
**Trade-off:** too few principles may fail to guide decisions; too many or overly prescriptive principles become bureaucracy.  
**Failure mode:** a principle exists in a document but teams cannot explain how it changes a design decision.

### 2.3 Prerequisites

The roadmap expects Modules 1–3 and basic familiarity with non-functional requirements. You should already understand the role of data architecture, the difference between architecture and engineering, and how business capabilities, domains and ownership are described.

This lesson focuses on principles and quality attributes. It does not replace the later detailed modules on requirements and architecture decisions, storage, integration, performance engineering, security implementation or governance.

## 3. Prerequisite knowledge

Before proceeding, confirm that you can:

- Describe a business objective and identify the stakeholders affected by a data architecture decision.
- Distinguish a business capability, domain, system and data asset.
- Explain why a data asset needs an accountable owner.
- Read a basic data-flow diagram.
- Distinguish a business requirement from an implementation choice.

If not, revisit the relevant earlier lessons. The banking examples below use customer, account and transaction data and assume that each asset has a bounded meaning and an accountable owner or an explicitly recorded ownership gap.

## 4. Beginner-level learning sequence

### 4.1 What is an architecture principle?

An **architecture principle** is a durable, shared statement that guides a class of decisions. A useful principle includes:

1. **Statement:** the direction or rule to follow.
2. **Rationale:** why it exists and which business driver or risk it serves.
3. **Implications:** what teams must do, consider, measure or avoid because the principle exists.

A principle should be stable enough to apply across multiple decisions but not so vague that every option can claim compliance. It is not a design specification for one project. A principle can be mandatory or advisory depending on its governance status; its authority should be explicit.

**Example**

- **Statement:** Every material data asset shared across domains must have a named accountable business role, or an explicit `UNKNOWN` ownership record with an action and review date.
- **Rationale:** Data-quality and meaning disputes otherwise remain unresolved, and consumers cannot identify who can authorise a correction.
- **Implications:** Architecture reviews check ownership status; project teams identify the owner before production use; unresolved ownership is visible as a risk rather than silently assumed.

This principle is actionable because it defines a condition, explains why it matters and creates consequences that can be checked.

### 4.2 Actionable principles versus slogans

The following examples rewrite vague statements into decision guidance. The revised principles are illustrative and would still need approval by the organisation that adopts them.

| Vague original | Why it is weak | Revised actionable principle | Rationale and implications |
|---|---|---|---|
| “Use best-of-breed technology.” | “Best” has no agreed criteria and ignores integration, skills, operations and total cost. | **Select technology against documented business and quality criteria, including integration fit, operability, security, skills and lifecycle cost; do not select on feature superiority alone.** | Compare options against the same criteria; record evidence and trade-offs; justify any exception. |
| “Data should be owned by a named domain.” | Does not define what counts as ownership, what happens when no owner exists, or whether the domain has authority. | **Every material data asset has one accountable business owner for its defined meaning and material decisions; if authority is unconfirmed, record `UNKNOWN`, the risk, a resolution action and a review date.** | The owner is accountable, while stewards, producers and consumers have distinct roles. A register can be audited for gaps. |
| “Make data real-time.” | “Real-time” has no time boundary, scope, cost limit or business justification. | **Set freshness targets by use case; require low-latency processing only where a documented decision or control needs it, and measure freshness at the consumer-visible point.** | Avoids paying for unnecessary streaming and gives teams a testable target. |
| “Keep data secure.” | Does not define data scope, threat, access conditions or evidence of compliance. | **Classify data and approve access by business purpose and role; sensitive data must not enter an environment unless its access, protection, retention and deletion controls are approved and verified.** | Makes security review a design condition; detailed controls belong to security standards and implementation work. |
| “Build scalable systems.” | Does not identify workload, growth, limit or response under load. | **Design each critical data service for the forecast workload and growth range approved for its capability, and verify that agreed latency and failure criteria remain within limits under that workload.** | Requires a workload assumption, a target and a verification plan rather than an untestable promise. |
| “Reuse data wherever possible.” | Reuse can spread stale, sensitive or semantically incompatible data. | **Reuse an existing asset when its meaning, quality, permitted use and freshness satisfy the consumer’s requirements; otherwise document why a separate representation is necessary.** | Encourages reuse without pretending every similarly named asset is interchangeable. |
| “Minimise cost.” | May encourage under-provisioning or move costs and risks to other teams. | **Evaluate lifecycle cost alongside agreed reliability, freshness, security and recovery requirements; a lower-cost design is acceptable only when required outcomes remain evidenced.** | Makes cost a trade-off criterion rather than the sole objective. |

### 4.3 Why principles need implications

A principle with no implications is hard to apply. For example, “Data quality matters” sounds reasonable but does not say which quality dimensions matter, who decides, or how a proposal is evaluated.

A usable principle leads to questions such as:

- Which asset and business decision are in scope?
- What quality failure would cause harm?
- Who approves the acceptable risk?
- What must the design demonstrate?
- What evidence will be collected after release?
- What happens if the target cannot be met?

Implications can include a required review, an ownership check, a measurement plan, a minimum control, a design constraint or a requirement to document an exception. They should not dictate low-level implementation unless the principle is intentionally a technical standard.

### 4.4 Quality attributes relevant to data systems

A **quality attribute** describes how well a data system or service behaves, rather than only what function it performs. Quality attributes often interact, and the appropriate priority depends on the asset and its use.

| Attribute | Definition | Example question | Typical measure (not a target by itself) | Trade-off / failure mode |
|---|---|---|---|---|
| **Reliability** | Ability to perform correctly and consistently over time, including under expected faults. | Does the pipeline produce complete, valid outputs or detect failure? | Successful valid runs / eligible runs; data-quality failure rate. | Extra checks and redundancy add cost and latency; “successful job” can hide incorrect output. |
| **Availability** | Ability to provide the required service when needed. | Can authorised users access the required dataset during the critical window? | Available minutes / eligible minutes; successful request rate. | Higher availability may require redundancy and operational effort; availability does not prove correctness. |
| **Scalability** | Ability to handle changing workload or data volume while preserving required outcomes. | Can the service handle forecast peak volume and growth? | Throughput, latency and error rate at a defined workload. | Capacity headroom costs money; a scale test is meaningless without a workload profile. |
| **Performance** | Responsiveness or throughput for a defined workload. | How long does a dashboard query or pipeline stage take? | p50/p95/p99 latency; records processed per second. | Faster response may require more compute, caching or reduced work; averages can hide tail latency. |
| **Freshness** | How current data is when it becomes available to a consumer. | How old is the newest relevant source event at query time? | Event-to-availability age; publication lag. | Lower latency can increase cost and complexity; a pipeline can be fast but incomplete. |
| **Security** | Protection against unauthorised access, alteration, disclosure or destruction. | Can only approved identities perform approved actions? | Access-policy test results; unauthorised access findings; control coverage. | Restrictive access can hinder legitimate work; a successful login test is not a full security assessment. |
| **Privacy** | Appropriate handling of personal or sensitive information according to purpose, rights and obligations. | Is the data necessary and permitted for this use? | Approved-use coverage, minimisation checks, retention/deletion verification. | More data can improve analysis but increase exposure; masking does not automatically make data anonymous. |
| **Interoperability** | Ability of systems and consumers to exchange and interpret data correctly. | Do producers and consumers agree on schema, semantics and units? | Contract-conformance rate; incompatible change count. | Common formats help exchange but do not guarantee shared meaning. |
| **Maintainability** | Ease and safety of understanding, changing, testing and operating the system. | Can a team modify a transformation without breaking consumers? | Change lead time, change failure rate, test coverage (interpreted in context). | Abstraction can reduce duplication but add complexity; raw counts can reward the wrong behaviour. |
| **Cost efficiency** | Ability to deliver the required outcomes at an acceptable lifecycle cost. | What does the required service cost at normal and peak use? | Cost per workload unit; monthly cost; forecast variance. | Cost cuts can degrade quality; unit cost can improve while total spend rises with volume. |
| **Recoverability** | Ability to restore service and data after a failure within an accepted boundary. | How quickly can data be restored, and how much acknowledged data may be lost? | Recovery time; recovery point/data-loss measure. | More frequent protection and replication cost more; untested recovery plans are not evidence. |

Reliability and availability are related but distinct: a service can be available while serving incorrect data. Freshness and performance are also distinct: a query can return quickly over stale data. Always define which property matters to the business outcome.

### 4.5 Business drivers, constraints and assumptions

| Type | Definition | Banking example | How to use it |
|---|---|---|---|
| **Business driver** | A business outcome, risk or obligation motivating a change. | Fraud analysts need to act on recent transaction activity. | Establishes why a quality matters and which capability benefits. |
| **Constraint** | A confirmed boundary the solution must respect. | A binding legal, regulatory, contractual or approved policy requirement restricts where a defined dataset may be processed. | Treat as a hard decision boundary unless an authorised legal/policy process changes it. |
| **Assumption** | A proposition temporarily treated as true because it has not yet been verified. | “The transaction source can publish changes within five seconds.” | Record owner, evidence needed, impact if false and validation date. |
| **Preference** | A desired option that may be traded off. | “The team prefers the current cloud platform.” | Do not mislabel a preference as a constraint; evaluate alternatives if material. |

**Worked distinction:** “The dashboard must be fresh within 60 seconds” is a proposed requirement, not automatically a business driver. “Fraud analysts must investigate suspicious activity before a defined operational deadline” is a driver. “The source currently emits events within five seconds” is an assumption until measured. “The approved data classification forbids an unapproved sandbox” is a constraint only if that rule has been verified as applicable.

### 4.6 Beginner exercise: identify the quality attribute

For each statement, identify the principal quality attribute and what remains unspecified.

1. “Transactions must be visible quickly.”  
   **Worked answer:** freshness and possibly performance; specify event-to-consumer age, percentile/population, window and measurement method.
2. “The service must be up.”  
   **Worked answer:** availability; specify service boundary, eligible time window, exclusions and success definition.
3. “We must never lose data.”  
   **Worked answer:** recoverability/reliability, but the statement is absolute and usually underspecified. Define the protected events, acknowledged-write boundary, acceptable data loss and recovery method.
4. “Only the risk team can use the score.”  
   **Worked answer:** access control and permitted use; define authorised roles, purposes, enforcement and evidence. If marketing is also a legitimate consumer, clarify whether a distinct derived segment is allowed.
5. “The system must support twice as much data.”  
   **Worked answer:** scalability; specify current and target workload, time horizon, latency/error thresholds and test method.

## 5. Intermediate-level learning sequence

### 5.1 From objective to principle to requirement

A useful architecture chain looks like this:

| Step | Banking example | Output |
|---|---|---|
| Business objective | Help fraud analysts act on suspicious transactions promptly. | Outcome and stakeholder |
| Driver / risk | Delayed data may delay investigation; the actual impact and deadline need business evidence. | Documented reason and uncertainty |
| Principle | Freshness targets must reflect the decision supported; high-urgency use cases need a defined, verified freshness objective. | Reusable decision direction |
| Quality attribute | Freshness and reliability; availability may also matter during the investigation window. | Prioritised qualities |
| Requirement | “For the agreed high-priority transaction feed, event-to-availability age shall be at most 60 seconds at p95 during the specified operating window.” | Testable condition; number illustrative |
| Verification | Compare source event timestamps with first consumer-available timestamps over an agreed observation window; report percentiles and missing events. | Evidence of achieved performance |
| Decision | Compare designs and document cost, complexity, failure modes and residual risk. | Defensible selection |

A principle should not be confused with a target. The principle may apply across many systems; the requirement defines the condition for a particular asset or use case.

### 5.2 Make a quality requirement measurable

For each requirement, define at least:

1. **Asset and scope:** which dataset, service, capability and consumer are included.
2. **Metric:** the quantity being measured and the start/end events.
3. **Target:** the acceptable threshold, percentile or proportion.
4. **Measurement window:** the period and operating conditions over which the target applies.
5. **Population and exclusions:** what counts, and what does not.
6. **Verification method:** logs, synthetic checks, reconciliation, recovery exercise or other evidence.
7. **Owner:** who accepts the requirement and who reviews results.
8. **Failure response:** what happens when the target is missed.

**Example — freshness**

- **Metric:** event-to-availability age = consumer-visible availability timestamp − source event timestamp.
- **Target:** p95 ≤ 60 seconds.
- **Window:** each rolling 24-hour period for the defined critical feed.
- **Population:** all valid source events in the agreed feed; missing or untraceable events are reported separately, not silently excluded.
- **Verification:** compare event IDs and timestamps from source and consumer logs; calculate the 95th percentile and missing-event count.
- **Status:** target is illustrative; no observed measurements are supplied here.

The percentile is not a guarantee that every event arrives within 60 seconds. p95 ≤ 60 seconds means at least 95% of the included observations are at or below that threshold under the defined measurement method. The remaining tail and missing events still require an explicit policy.

### 5.3 Measurement definitions and useful formulas

**Availability percentage**

\[
\text{Availability} = \frac{\text{eligible time service met availability definition}}{\text{total eligible time}} \times 100\%
\]

The service boundary and eligible time must be defined. A service may be “up” at the network layer but unavailable for the required dataset or query. Planned maintenance exclusions must be explicit; they should not be introduced after a failure to improve the reported result.

**Freshness / data age**

\[
\text{Data age} = t_{\text{consumer available}} - t_{\text{source event}}
\]

This assumes comparable, trustworthy timestamps and a defined meaning for “available.” Clock skew, late-arriving events and replayed records need to be considered. For periodic snapshots, freshness may instead be the current time minus the snapshot’s effective-as-of time.

**Recovery time**

Recovery time is the elapsed time between the defined start of a disruption and restoration of the agreed service/data state. State whether validation and reconciliation are included. A recovery time objective (RTO) is a target, not an observed result.

**Recovery point / acceptable data loss**

A recovery point objective (RPO) states the maximum tolerable time gap between the last recoverable state and the failure point for a defined workload. For event-driven systems, also define the number and type of acknowledged events that may be lost or duplicated. A time-only RPO may be insufficient for uneven event rates.

**Reliability**

A simple run success rate may be defined as successful valid executions divided by eligible executions. It should not count a job as successful solely because the process exited with status zero. Include completeness, correctness and reconciliation criteria appropriate to the asset.

**Cost efficiency**

Possible metrics include cost per million events processed, cost per successful published dataset, or monthly service cost. State the workload and quality level delivered. Unit-cost improvement does not prove total cost reduction if volume rises.

### 5.4 Worked quality requirements for the banking scenario

The following are **illustrative requirements** to demonstrate measurement design. The roadmap provides the banking context but does not supply these numerical targets or observed results. They must be confirmed against business impact, regulation, source capability, workload, budget and risk appetite before adoption.

| ID | Asset / capability | Quality attribute | Illustrative target | Measurement window and population | Verification method | Proposed accountable reviewer role (confirm locally) | Evidence basis |
|---|---|---|---|---|---|---|---|
| Q1 | Transaction feed for fraud investigation | Freshness | p95 event-to-availability age ≤ 60 seconds | Rolling 24 hours; all valid source events in the agreed feed; missing/untraceable events reported separately | Compare source event IDs/timestamps with first consumer-available timestamps; report p50/p95/p99 and missing count | Fraud capability data owner with data-platform operations | Illustrative target; no observed measurements supplied |
| Q2 | Transaction feed for fraud investigation | Reliability / completeness | ≥ 99.95% of eligible logical source events have one canonical consumer outcome or a documented, reconciled exception under the agreed duplicate/replay policy | Daily measurement with monthly roll-up; denominator is eligible logical source events, not delivery attempts; exclusions documented before measurement | Reconcile source event IDs to canonical consumer outcomes; separately count missing, duplicate, late and reconciled events | Transaction data owner with reconciliation/control owner | Illustrative target; denominator and business exception policy must be approved |
| Q3 | Critical account/balance inquiry dataset | Availability | ≥ 99.9% of eligible service minutes satisfy the defined successful-response contract | Monthly; defined operating window; eligible minutes and maintenance exclusions specified before measurement | Synthetic requests plus production service logs; a response counts only if it returns valid data within the service boundary | Account/balance service owner with operations/SRE reviewer | Illustrative target; no service observations supplied |
| Q4 | Critical account and transaction recovery | Recoverability | RTO ≤ 60 minutes; RPO ≤ 5 minutes for the defined protected-event boundary, with acknowledged-event loss/duplication reconciled to the approved policy | Each scheduled recovery exercise and actual incident; start/end and protected-event boundary fixed in advance | Restore protected state, validate completeness, measure time to usable service and compare last recoverable state with failure point | Business continuity/recovery owner with transaction data owner | Illustrative targets; must be validated through an executed recovery exercise |
| Q5 | Customer information used for approved communications | Privacy / security | 100% of discovered and approved production access paths pass identity, authorisation and purpose-policy tests before release; no unresolved critical unauthorised-access finding at release | Pre-release for every release and each material access-policy change; recurring review of the defined access-path inventory | Access-path inventory, policy tests, access review and independent control evidence; report inventory coverage separately | Customer data owner with authorised privacy/security control reviewer | Illustrative acceptance criteria; inventory completeness and policy applicability must be evidenced |
| Q6 | Shared customer/account datasets | Interoperability | 100% of designated critical consumers pass agreed schema and semantic contract tests before a breaking change is released | Each release and each contract-version change; all designated critical consumers in the registered inventory | Automated compatibility tests plus review of units, status definitions, identifiers, effective dates and null semantics | Shared-data product owner with designated consumer representatives | Illustrative target; consumer inventory and contract tests must be established |
| Q7 | Customer and transaction data pipeline | Maintainability / change safety | Every critical transformation has an accountable owner, documented change path and passing automated tests for agreed business invariants before production release | Every production release; quarterly completeness review of the critical-transformation inventory | Inspect change records, ownership register and test results; sample tests against known valid/invalid cases | Pipeline service owner with engineering quality reviewer | Illustrative control target; criticality inventory and invariant tests require approval |
| Q8 | Analytical workload over customer/transaction data | Cost efficiency | Monthly cost remains within the approved budget at the agreed workload profile while mandatory Q1, Q3 and Q5 criteria remain satisfied | Monthly; record volume, concurrency, retention, compute profile and quality results for the same period | Cost allocation reports, workload-normalised cost and budget variance; compare with Q1/Q3/Q5 verification evidence | Analytical product owner with finance/cost-management reviewer | Budget and workload are not supplied; target must be approved and measured |

**Interpretation cautions**

- Q2’s “exactly once or reconciled” wording does not assume a particular messaging implementation. It defines a business outcome: duplicates or replays must be handled according to an explicit policy and reconciled. A real specification must clarify whether the target counts source events, logical transactions or delivery attempts.
- Q3 availability must not count a quick but stale or invalid response as successful unless the service contract explicitly allows that behaviour.
- Q4 RTO/RPO are example targets only. A recovery exercise must actually be run before anyone claims they are met.
- Q5’s “100%” applies to the defined inventory and test scope. It does not prove that every conceivable access path has been discovered; inventory completeness and test coverage are separate evidence questions.
- Q8 must not permit cost savings to silently violate higher-priority quality or compliance constraints.

### 5.5 Constraints and assumptions change the requirement

A requirement is only defensible in context.

**Example:** the business asks for a transaction dashboard with a 10-second freshness target.

- **Driver:** analysts say they need quicker decisions. The exact decision and deadline are not yet evidenced.
- **Assumption:** the source can publish every transaction change within two seconds. This needs measurement.
- **Constraint:** the source platform cannot be changed during a contractual freeze. Confirm the scope and end date.
- **Potential implication:** end-to-end freshness cannot be guaranteed from downstream processing alone if source publication is slower than the target.
- **Next action:** measure current source-to-consumer lag, validate the business deadline and decide whether to change the source, relax the target, narrow the scope or accept an explicitly documented risk.

Do not set a target by choosing an attractive number first and inventing a rationale afterward. If a requirement depends on an assumption, record the assumption owner, validation method, due date and what decision changes if it is false.

### 5.6 Evaluate candidate architectures with a scorecard

A scorecard makes criteria visible; it does not turn uncertain judgement into objective truth. Separate observed evidence from assumptions and expert judgement. Define the scoring scale before evaluating options, apply it consistently, and explain why a score was assigned.

#### Scenario and candidate designs

**Scenario:** a bank needs transaction data for fraud investigation and also needs analytical access for approved business analysis. The bank wants recent data, controlled access, recoverability and acceptable operating cost. No actual workload measurements, supplier quotations or benchmark results are supplied.

- **Design A — Batch-oriented warehouse feed:** ingest transaction changes on a scheduled interval into a controlled analytical store. Simpler operating model and lower continuous-processing complexity may be plausible, but freshness may be limited by schedule.
- **Design B — Event-driven feed with a continuously updated analytical serving layer:** publish transaction changes through an event pipeline and update a serving dataset continuously. It may support lower latency, but introduces more operational components, replay/ordering concerns and ongoing cost.

These are conceptual alternatives, not vendor-specific designs. Neither is assumed to meet any target without verification.

#### Criteria and illustrative weights

Weights below are a **stakeholder discussion aid**, not a source-derived fact. For this scenario, freshness is important, but privacy/security and correctness are hard constraints. A design that violates a mandatory constraint should not be rescued by a high weighted total.

| Criterion | Weight | Why it matters | Evidence needed |
|---|---:|---|---|
| Freshness fit | 25% | Fraud use may depend on timely events. | Measured source-to-consumer latency under representative peak and failure conditions |
| Reliability / reconciliation | 20% | Missing or duplicated transaction facts can mislead investigations. | Replay, duplicate, late-event and reconciliation tests |
| Security / privacy fit | 20% | Customer and transaction data are sensitive. | Approved data-flow, access and retention controls; test evidence |
| Recoverability | 15% | A failure must not create unacceptable loss or prolonged unavailability. | Recovery design, RTO/RPO approval and executed recovery evidence |
| Maintainability / operational complexity | 10% | On-call capability and safe change matter over the lifecycle. | Support model, failure modes, deployment/recovery procedure and team capability |
| Lifecycle cost | 10% | The service must be affordable at the required workload. | Comparable cost model using the same workload, retention and quality assumptions |
| **Total** | **100%** |  |  |

#### Scoring scale

- **1 — Materially poor fit:** known evidence indicates a major gap or a credible failure to meet the criterion.
- **2 — Weak fit:** significant gap or unresolved risk.
- **3 — Plausible / uncertain:** appears feasible but important evidence is missing, or the trade-off is material.
- **4 — Good fit:** relevant evidence supports the criterion, with manageable residual risk.
- **5 — Strong fit:** strong, directly relevant evidence supports the criterion and few material gaps remain.

A score of 3 does not mean “meets target”; it means the available evidence is inconclusive or the fit is conditional. Any real scoring exercise should attach evidence references to each score.

#### Worked illustrative scorecard

The following scores are **hypothetical initial assessments**, not benchmark results. They demonstrate the method only. Because no test results or quotes are available, scores for both designs remain provisional.

| Criterion | Weight | Design A score | A weighted points | Design B score | B weighted points | Reason for provisional assessment |
|---|---:|---:|---:|---:|---:|---|
| Freshness fit | 25% | 2 | 0.50 | 4 | 1.00 | Scheduled batches may struggle with a very low-latency target; event-driven processing is a plausible fit but must be measured. |
| Reliability / reconciliation | 20% | 4 | 0.80 | 3 | 0.60 | Batch reconciliation may be simpler to reason about; event replay, ordering and duplicates need explicit tests. Neither score is proven. |
| Security / privacy fit | 20% | 3 | 0.60 | 3 | 0.60 | Both can be designed with controls; neither has supplied evidence of approved access, retention or environment boundaries. |
| Recoverability | 15% | 4 | 0.60 | 3 | 0.45 | Batch restart/reprocessing may be more straightforward, while event recovery depends on replay and state restoration. Validate with exercises. |
| Maintainability / complexity | 10% | 4 | 0.40 | 2 | 0.20 | Event-driven design has more moving parts in this simplified assumption; team capability may reverse this judgement. |
| Lifecycle cost | 10% | 4 | 0.40 | 2 | 0.20 | Continuous processing may cost more, but no quotes, workload or utilisation data exist. |
| **Illustrative weighted total** | **100%** |  | **3.30 / 5** |  | **3.05 / 5** | Arithmetic reflects assumptions, not measured performance or an approved decision. |

**Calculation:** weighted total = sum of `(weight as a fraction × score)`. For Design A: `0.25×2 + 0.20×4 + 0.20×3 + 0.15×4 + 0.10×4 + 0.10×4 = 3.30`. For Design B: `0.25×4 + 0.20×3 + 0.20×3 + 0.15×3 + 0.10×2 + 0.10×2 = 3.05`.

**Do not conclude that Design A is objectively better from this total.** The weights and scores are assumptions. If the approved business requirement is a hard p95 freshness limit that Design A cannot meet, Design A may be infeasible regardless of its total. If the business can accept a longer freshness interval, Design A may be more proportionate. The next step is to validate the requirement, collect representative measurements, estimate comparable lifecycle cost and test critical failure modes.

#### How to use the scorecard responsibly

1. Confirm the business objective and whether any criterion is a non-negotiable constraint.
2. Define the criteria and scoring scale before seeing the preferred design.
3. Record the evidence behind each score and label assumptions.
4. Use the same workload, retention, security scope and service boundary for both candidates.
5. Run sensitivity analysis: would the result change if freshness weight or cost estimates changed?
6. Reject or redesign an option that fails a mandatory requirement; do not let an average hide a critical failure.
7. Record uncertainty and the next experiment or evidence needed.

## 6. Advanced-level learning sequence

### 6.1 Trade-offs are contextual decisions

Quality attributes can conflict. There is no universally correct priority order for every data asset. Priorities depend on the business capability, data criticality, use, risk, obligations and cost of failure.

| Tension | Why it occurs | Example decision question | Defensible approach |
|---|---|---|---|
| Performance vs. cost | Lower latency or higher throughput may require more compute, caching or continuous processing. | Does the business decision require near-real-time data, or is a scheduled refresh sufficient? | Measure decision latency need, compare lifecycle cost and state the accepted freshness boundary. |
| Availability vs. consistency | Replicated or distributed systems may trade immediate agreement for continued operation under certain failures. | During a partition, can a consumer act on a temporarily stale account state? | Classify the operation and failure consequence; state the required consistency and availability behaviour rather than choosing a slogan. |
| Openness vs. security | Easier access and reuse increase exposure if access is not bounded. | Can analysts use sensitive transaction data in a sandbox? | Allow only approved purpose, minimum necessary fields, controlled identities, environment protections and reviewable evidence. |
| Agility vs. control | Fast local changes can break shared consumers or bypass required controls. | Can a team change a shared schema without coordination? | Permit low-risk compatible changes locally; require impact review for breaking or high-risk changes. |
| Privacy vs. analytical usefulness | More detailed data may improve analysis but increase exposure and purpose risk. | Does an experiment require raw identifiers, or would masked/aggregated data suffice? | Test the least intrusive data that meets the analytical purpose; record residual risk and legal/policy constraints. |

**Availability versus consistency clarification:** “consistency” can refer to several properties, including agreement among replicas and correctness of business invariants. State which one is relevant. This lesson does not prescribe a universal distributed-systems choice.

### 6.2 Prioritise by asset and use case

Do not assign one quality profile to all bank data.

| Asset / use | Likely high-priority qualities | Why priorities differ | Example of a poor default |
|---|---|---|---|
| Transaction feed for time-sensitive fraud investigation | Freshness, completeness, reliability, access control, recoverability | A delayed or missing event may delay investigation or obscure a pattern. Exact targets require business evidence. | Reusing the daily batch target simply because it already exists. |
| Customer address for statements and service | Accuracy, provenance, privacy, availability for the relevant workflow, correction propagation | Incorrect details can disrupt service; every consumer does not necessarily need sub-second updates. | Paying for continuous processing without a demonstrated business need. |
| Aggregated monthly management report | Reconciliation, semantic consistency, reproducibility, cost efficiency, appropriate freshness | A report may need a reconciled period close more than second-by-second freshness. | Treating “real-time” as universally superior. |
| Analytical sandbox containing sensitive records | Privacy, security, minimisation, retention/deletion, auditability, maintainability | The environment and purpose may increase exposure. | Copying production data because it is convenient, without assessing necessity or controls. |
| Regulatory reporting dataset | Correctness, lineage of calculations, reproducibility, availability by the required deadline, controlled access | An incorrect or late report may have material consequences; exact obligations must be verified. | Optimising query speed while neglecting reconciliation and evidence. |

The table identifies candidate priorities, not final requirements. Confirm the actual use, failure impact, applicable obligations and stakeholder acceptance for each asset.

### 6.3 Resolve conflicts between principles

Principles can conflict or appear to conflict. For example:

- **P1 — Minimise sensitive-data exposure:** only the minimum necessary data may be used for an approved purpose.
- **P2 — Enable timely, useful analysis:** approved analytical work should have access to data with sufficient detail and freshness to answer the business question.

A weak response is to declare one principle always wins. A defensible resolution is to establish the purpose, legal/policy constraints, decision value and least-intrusive data that can meet the requirement. If masked, tokenised or aggregated data is sufficient, P1 and P2 can both be satisfied. If the business claims raw identifiers are necessary, require evidence and a review of alternatives. A mandatory privacy or legal constraint cannot be waived by an ordinary architecture exception.

**Conflict-resolution sequence**

1. Clarify whether the conflict is real or caused by vague wording.
2. Separate mandatory constraints from preferences and principles.
3. Define the use case, asset, threat/failure scenario and business impact.
4. Identify options, including reducing scope or changing the requirement.
5. Evaluate each option against quality requirements and evidence.
6. Decide which principle takes precedence in this context and why.
7. Record residual risk, compensating controls, accountable approval and review trigger.
8. Update the principle or guidance if the same conflict recurs frequently.

### 6.4 A compact principles set

The following is an illustrative set of **seven** principles—within the roadmap’s maximum of eight. An organisation would need to approve their authority, scope and exceptions before treating them as binding.

| ID | Statement | Rationale | Practical implications |
|---|---|---|---|
| P1 — Accountable ownership | Every material shared data asset has one accountable business role for its defined meaning and material decisions; unknown ownership is recorded as a risk with an action and review date. | Decisions and corrections need a clear authority. | Register owner/steward/producers/consumers; do not infer ownership from system custody. |
| P2 — Quality by use | Quality targets are defined according to the business decisions, impact and risk supported by each asset. | Different use cases have different tolerances. | Define metrics, targets, windows and verification; avoid a single target for all data. |
| P3 — Evidence before claims | Claims that a design meets a quality target require evidence from a defined verification method. | Design intent is not observed performance. | Separate assumptions, predictions, test results and production measurements. |
| P4 — Minimise sensitive-data exposure | Use only data necessary for an approved purpose, under verified access, retention and environment controls. | Reduces avoidable privacy and security risk. | Assess data copies, restrict access, record purpose and verify controls. |
| P5 — Explicit contracts for shared data | Material shared assets have documented meaning, quality expectations and a change-communication path. | Prevents silent semantic and compatibility breaks. | Assess consumer impact before breaking changes; test relevant contracts. |
| P6 — Lifecycle value over local optimisation | Select designs against quality needs, operability, skills and lifecycle cost, not isolated feature or initial cost. | Local wins can create enterprise-wide cost and risk. | Compare candidates on the same workload and service boundary; record trade-offs. |
| P7 — Controlled, reviewable deviations | Departure from a principle requires documented justification, risk, compensating controls, accountable approval and expiry/review. | Exceptions should be visible, proportionate and temporary where possible. | Track approvals, conditions, expiry and evidence; refuse prohibited or uncontrolled deviations. |

### 6.5 Complete exception record

A deviation is not approved merely because a team has implemented it. The record below is a **hypothetical example** to demonstrate completeness; it is not an approval for any real bank or environment.

| Field | Example record |
|---|---|
| **Exception ID / status** | EX-AN-017 / Proposed for review — **not approved** |
| **Requesting capability / team** | Fraud analytics pilot (illustrative) |
| **Affected asset / environment** | A limited extract of customer and transaction records copied to an analytical sandbox |
| **Principle violated** | P4 — Minimise sensitive-data exposure; the proposed copy may include fields beyond the demonstrated analytical need. |
| **Request and business justification** | The pilot team claims that a short experiment needs richer event-level data to validate a fraud-detection hypothesis. The actual necessity of each sensitive field is not yet evidenced. |
| **Options considered** | (1) Use masked/pseudonymised or aggregated data; (2) run the analysis in the approved controlled environment without a new copy; (3) create a minimised, time-limited extract; (4) copy the proposed full dataset. |
| **Recommended decision** | Do **not** approve the proposed full copy on current evidence. Rework the request to prove the minimum necessary fields and environment, then resubmit. |
| **Risk if approved as proposed** | Unnecessary exposure, uncontrolled downstream copies, retention/deletion failure, unauthorised reuse and difficulty proving the dataset was removed. |
| **Compensating controls if a narrower exception is later approved** | Data minimisation; masking/tokenisation where compatible with the purpose; approved isolated environment; least-privilege access; logging; prohibited onward export; explicit retention/deletion date; verification of deletion; named technical custodian; owner acceptance of residual risk. Controls must be validated, not assumed effective. |
| **Accountable business owner** | `UNKNOWN` until the authorised owner for the affected customer/transaction assets is confirmed. The requester cannot approve their own exception by default. |
| **Required approvers** | The roles formally authorised by the bank’s policy for the data classification, privacy/security risk and architecture deviation. Names/roles must be confirmed; this record does not invent them. |
| **Expiry / review date** | If a narrowed exception is approved, set expiry no later than 30 days after approval (illustrative proposed limit) or at pilot completion, whichever comes first. A real date must be recorded before approval. |
| **Approval rationale** | No approval rationale exists yet because the request is not approved. Approval requires evidence of necessity, constraint/policy compatibility, effective controls and accountable risk acceptance. |
| **Evidence required before decision** | Field-level data inventory; purpose statement; alternatives analysis; applicable policy/legal review; environment and access test evidence; retention/deletion verification plan; owner and approver confirmation. |
| **Review trigger** | Any new field, consumer, environment, export, purpose or extension of the pilot; a security/privacy incident; failure to verify deletion; or expiry date reached. |
| **Closure evidence** | Confirmation that the exception ended, copies were deleted or retained under an approved rule, access was revoked, and any remaining risk/action was assigned. |

**Exception rules**

- A principle deviation and a legal, regulatory or mandatory policy breach are not the same. Architecture approval cannot override a binding requirement unless the authorised legal/policy process explicitly permits it.
- A compensating control must reduce the identified risk and have verification evidence. “We will be careful” is not a control.
- The accountable owner must be clear. If ownership or approval authority is unknown, do not mark the exception approved.
- Expiry must be a real date or event with an owner and review action. “Until further notice” is not an adequate expiry.
- Refuse an exception when it violates a non-waivable constraint, has no legitimate purpose, exposes more data than necessary without justification, lacks an accountable risk acceptor, or has no credible control/verification plan.

### 6.6 Principle decay and conflict detection

Principles are not self-enforcing. They need to remain understandable, applicable and connected to real decisions.

| Warning sign | What it may mean | How to investigate | Possible response |
|---|---|---|---|
| Delivery teams do not know the principles exist | Communication or onboarding failure; principles may be buried or irrelevant. | Ask teams to explain how principles affect a recent decision; inspect training and decision records. | Publish concise guidance, show examples and integrate principles into design templates/reviews. |
| The same principle is routinely bypassed | It may be impractical, conflicting, poorly governed or not supported by tools/processes. | Review exceptions, incidents, incentives and delivery constraints. | Fix the underlying cause; revise the principle if its rationale no longer holds, or enforce it if risk remains unacceptable. |
| Two principles produce inconsistent recommendations | Wording may be vague or priorities unclear. | Test both against the same scenario and identify the actual conflict. | Clarify scope, priority conditions and escalation; record a precedent. |
| No one can identify a decision affected by a principle | It may be a slogan rather than decision guidance. | Try to use it to distinguish two plausible designs. | Rewrite it with testable implications or retire it. |
| Exceptions never expire | Temporary deviations have become ungoverned defaults. | Review age, risk, control evidence and repeated patterns. | Close, renew with justification or convert the learning into a formally reviewed principle/standard. |
| Metrics improve while outcomes worsen | The metric may be a proxy, have a poor boundary or encourage gaming. | Compare the metric with business outcomes, errors and user experience. | Redefine the metric or add guardrails; preserve the historical definition for comparison. |

### 6.7 When should an exception be refused?

Refuse or pause approval when any of the following holds:

1. The proposed deviation conflicts with a non-waivable legal, regulatory, contractual or approved policy constraint.
2. The business purpose is not legitimate, specific or supported by evidence.
3. The design uses more sensitive data than necessary and has not assessed less intrusive alternatives.
4. The accountable owner or authorised risk-acceptance role is unknown or unwilling to accept the residual risk.
5. The compensating controls are vague, untested or impossible to verify.
6. The exception has no expiry, review trigger or closure plan.
7. The team is trying to retroactively legitimise a violation without addressing exposure or remediation.
8. The same exception recurs because the underlying architecture or operating model is broken, yet no corrective action is planned.

A refusal should identify the failed condition and the evidence needed to reconsider. The goal is defensible risk management, not a reflexive “no.”

## 7. Industry-application exercises

The exercises below use an illustrative bank. Names, targets, scores and design details are assumptions for learning, not verified facts about a particular organisation.

### Exercise 1 — Principles for customer and transaction data

Write a principle set for customer, account and transaction data. For each principle, include statement, rationale and implications. Include at least one principle on ownership, one on quality by use and one on sensitive data.

**Worked solution outline:** P1, P2 and P4 in Section 6.4 are suitable starting points. A strong answer should explain how the principle affects a design review, identify evidence that could demonstrate compliance, and state how uncertainty is handled. A slogan such as “customer data must be high quality” is incomplete until the relevant quality dimensions and decision context are defined.

### Exercise 2 — Define six measurable requirements

Use the table in Section 5.4. Select six requirements and verify that each contains asset/scope, metric, target, window/population and verification method. Label all numerical targets as illustrative unless the business has supplied evidence.

**Worked solution outline:** Q1–Q6 satisfy the structure as examples. Before adopting them, validate the 60-second freshness, 99.95% completeness, 99.9% availability and RTO/RPO assumptions with business stakeholders, source capability, risk assessment and actual measurements. No system is claimed to meet these targets in this lesson.

### Exercise 3 — Real-time dashboards versus cost and complexity

**Situation:** business stakeholders demand a real-time transaction dashboard; platform teams warn that continuous processing increases cost and operational complexity.

**Decision process**

1. Clarify what “real-time” means in seconds and which decision depends on it.
2. Identify the users, operating window, affected transaction population and consequence of stale data.
3. Measure current source-to-consumer freshness and the distribution of decision delay.
4. Compare a scheduled feed and event-driven feed against the same requirements and workload.
5. Include reliability, replay/reconciliation, security, recoverability, maintainability and lifecycle cost—not only latency.
6. If the requirement is not yet evidenced, run a bounded experiment and state what result would justify the additional complexity.
7. Record the decision and revisit it when workload, incident evidence or business need changes.

**Worked conclusion:** neither “real-time is always better” nor “batch is always cheaper” is defensible without evidence. If the business can meet its decision deadline with a scheduled feed, the simpler design may be proportionate. If measured delays cause unacceptable risk and an event-driven design can meet the target with acceptable reliability and cost, the extra complexity may be justified.

### Exercise 4 — Copy sensitive data into an analytics sandbox

**Situation:** a team asks to copy customer and transaction data from a controlled production environment into a sandbox for experimentation.

**Questions to answer**

- What is the specific analytical purpose and which fields are necessary?
- Can masked, pseudonymised, aggregated or synthetic data meet the need?
- What classification and permitted-use constraints apply?
- Who can access the sandbox, and can data be exported or copied onward?
- What retention and deletion rules apply, and how will deletion be verified?
- Who owns the source assets and who can approve the exception?
- What evidence is required before release and at closure?

**Worked conclusion:** do not approve a full sensitive-data copy merely because the sandbox is convenient. Establish necessity, constraints, minimisation, environment controls and accountable approval. If mandatory policy prohibits the copy, an architecture exception cannot make it permissible. The example exception record in Section 6.5 demonstrates a defensible “not approved yet” outcome.

### Exercise 5 — Deviating from a single-system-of-record principle

**Situation:** a project requests a second store of customer/account data for availability or analytical reasons.

**Reasoning:** first identify which asset and attributes are in scope. “Single system of record” may be too broad if it treats source facts, read replicas, caches, analytical snapshots and derived data as identical. Determine whether the proposed store is authoritative for updates, a read-only copy, a time-bounded snapshot or a separately governed derived asset.

**Evidence needed:** write authority, conflict resolution, freshness, reconciliation, lineage/traceability appropriate to the decision, access controls, failure behaviour, owner acceptance and operational cost.

**Worked conclusion:** a second representation is not automatically a violation if the principle permits controlled replicas or derived assets. If the principle prohibits independent authoritative writes, a design that introduces them needs a formal decision or exception. Do not label a copy “the system of record” without specifying the asset and authority.

### Exercise 6 — Audit finds principles are unknown to delivery teams

**Situation:** an audit discovers that teams are unaware of the architecture principles, and recent designs cannot show how they were applied.

**Diagnosis:** this may indicate a communication failure, principles that are not actionable, weak review integration, or incentives that reward bypassing them. Do not assume training alone will fix it.

**Actions:** sample recent decisions; ask teams to apply principles to real options; examine exceptions and repeated violations; check whether principles conflict; revise vague wording; publish short decision examples; integrate principles into proportionate reviews; measure whether decisions become clearer and exception patterns improve.

**Worked conclusion:** a principle that cannot influence a decision or is routinely bypassed needs investigation. If the principle remains justified, improve its operationalisation and accountability. If it is obsolete or contradictory, revise or retire it through an explicit decision rather than leaving a misleading document in place.

### Exercise 7 — Trade-off and exception practice

Choose one conflict from Section 6.1. Write a one-page decision note with:

- Context and business driver.
- Constraints and assumptions.
- Options, including “change the requirement” where appropriate.
- Quality attributes and measurable requirements.
- Evidence available and evidence missing.
- Trade-offs, risks and the chosen priority.
- Exception record if a principle is violated.
- Accountable decision role and review trigger.

**Independent practice:** do not copy the worked conclusions. Defend a different decision if your stated evidence and criteria support it.

## 8. Practical scenarios and case-based reasoning

### Scenario A — “Use best-of-breed technology”

**Challenge:** a proposed platform has more features than the existing option but requires specialist skills, additional integration and a more complex operating model.

**Reasoning:** the original slogan does not define “best.” Compare business fit, required quality targets, integration, security, skills, supportability and lifecycle cost. Ask for representative evidence and document the trade-offs. A feature-rich option can still be a poor architecture fit.

### Scenario B — “Data is owned by a named domain”

**Challenge:** a team names a domain but cannot identify the role that can decide the asset’s definition or correct a defect.

**Reasoning:** domain label alone is not enough. Identify the bounded asset, accountable role, steward, producers and consumers. If authority remains unconfirmed, record `UNKNOWN` and an action rather than treating the principle as satisfied.

### Scenario C — Customer and transaction data need different quality profiles

**Challenge:** a team wants one freshness and availability target for every dataset.

**Reasoning:** identify the business decision each dataset supports. Transaction data used for time-sensitive fraud investigation may need a stricter freshness target than a monthly management aggregate. Customer address data may prioritise verification, privacy and correction propagation rather than sub-second freshness. Define targets per use case and justify them using impact and evidence.

### Scenario D — A target is met on average but misses the tail

**Challenge:** a dashboard team reports a low average latency, while users complain about occasional long delays.

**Reasoning:** averages can conceal tail behaviour. Define the response-time distribution and relevant percentile, workload and observation window. Compare observed measurements with the target and investigate peak/failure conditions. Do not claim the service meets the requirement based only on the average if the requirement concerns p95 or p99.

### Scenario E — A requirement cannot be met under a confirmed constraint

**Challenge:** the business requests a latency target that the source system cannot support during a verified change freeze.

**Reasoning:** distinguish the confirmed constraint from an assumption. Measure the source contribution, confirm the freeze boundary and ask whether the business objective can be met by narrowing scope, changing the decision workflow or changing the target. If not, record the gap and escalate the business risk. Do not pretend a downstream architecture can guarantee a target outside its control.

### Scenario F — The team asks for a permanent exception

**Challenge:** a team repeatedly requests a deviation and wants it approved “until further notice.”

**Reasoning:** recurring exceptions may indicate an impractical principle, a broken architecture or weak control. Require an accountable owner, risk assessment, compensating controls, expiry and review. If the deviation is now the intended standard, revise the principle through a formal decision rather than leaving a permanent exception in the register.

## 9. Expected outputs or deliverables

Produce the following artefacts for the banking scenario:

1. **Principles set:** no more than eight principles, each with statement, rationale and implications.
2. **Measurable quality-target table:** at least six requirements; each has asset/scope, metric, target, measurement window, population, verification method and accountable reviewer. Clearly label assumptions and targets that lack evidence.
3. **Candidate-design scorecard:** two designs, explicit criteria and weights if used, a pre-defined scoring scale, evidence/uncertainty for every score, and a written conclusion that respects hard constraints.
4. **Trade-off analysis:** at least one explicit conflict between quality attributes or principles, with alternatives and rationale.
5. **Exception record:** violated principle, justification, risk, compensating control, accountable owner, expiry/review date and approval rationale/status.
6. **Practice answers:** written responses to the lesson exercises and the module’s practice questions, with corrections for incomplete answers.

A deliverable is not complete merely because a table is filled in. The numbers must be interpretable, the decision logic must be visible, and unsupported claims must be labelled.

### Practice-question answer crosswalk

Use the companion [`practice-questions.md`](practice-questions.md), Section D, as the assessment source. These concise checks align this lesson with D4.1–D4.11; they are answer criteria, not claims that a real bank has approved the example targets.

| Question | Required answer / correction check |
|---|---|
| D4.1 — Rewrite weak principles | Provide five records with statement, rationale and implications. The lesson's examples in §4.2 cover best-of-breed, named-domain ownership, real-time, security and scalability/reuse/cost; for “data must be good,” define dimensions and use-specific acceptance tests; for “single system,” identify authoritative attributes and governed copies. |
| D4.2 — Driver, constraint, assumption | Treat morning-review availability as a business outcome/requirement depending on framing; source freeze as a constraint only when confirmed; feed completeness as an unverified assumption; reconciliation reduction as a driver; retained network path as a constraint only if mandated, otherwise clarify preference/assumption. |
| D4.3 — Objective to principle | Define at least two principles that change design decisions—for example, owned definitions with traceable lineage, and published quality/freshness contracts with verification. |
| D4.4 — Vague quality claims | Specify freshness at a consumer boundary, availability over an eligible window, recovery time and acceptable loss, and defined quality dimensions over a population. Name the method and reviewer; label any proposed number illustrative. |
| D4.5 — Six banking requirements | Select at least six rows from Q1–Q8; preserve scope, metric, target, window/population, method, accountable reviewer and evidence basis. Do not present illustrative values as achieved or industry-standard values. |
| D4.6 — Compare two designs | Use the scorecard in §5.6 with the same criteria and scale; cite evidence or mark it missing, identify hard gates, explain sensitivity and state tests needed before approval. The current numerical scorecard is hypothetical only. |
| D4.7 — Real-time dashboard | Compare batch, micro-batch and event-driven/streaming options; choose using measured decision deadlines, freshness, failure/replay behaviour, operability and lifecycle cost. “Real-time” alone is not a testable requirement. |
| D4.8 — Single-system-of-record exception | Define which attributes are authoritative, whether the second store is read-only or independently writable, and how freshness/conflicts are managed. Record justification, risk, controls, owner, expiry/review and authorised approval; refuse prohibited or uncontrolled deviations. |
| D4.9 — Sensitive sandbox copy | Establish purpose, minimum fields, permitted-use constraints, environment/access controls, retention/deletion evidence and accountable approval. Compare masked/synthetic data, controlled views and minimised extracts; do not assume policy permits or prohibits the copy without evidence. |
| D4.10 — Principles unknown to teams | Investigate communication, ownership, applicability, stale wording and review integration; sample decisions and exceptions, then publish/revise/retire and measure whether teams can apply the principles. Do not assume all principles are wrong. |
| D4.11 — Conflict and exception | Keep the set to eight or fewer principles; resolve a conflict for a named asset/use case with evidence and residual risk; complete a time-limited exception record with accountable owner, compensating controls, expiry/review and approval rationale/status. |

## 10. Common mistakes and misconceptions

1. **Writing slogans instead of principles.** If the statement cannot distinguish plausible options, add scope, rationale and implications.
2. **Treating a principle as a requirement.** Principles guide classes of decisions; requirements define conditions for a specific solution/use case.
3. **Using a quality word without a metric.** “Fast,” “available” and “reliable” need a defined measurement and boundary.
4. **Treating a metric as a target.** A p95 latency metric describes how to measure; the target says what value is acceptable.
5. **Treating a target as an observed result.** A requirement or design estimate does not prove that a system meets it.
6. **Using a percentage without a denominator.** Define the eligible population, exclusions and what counts as success.
7. **Confusing freshness and query latency.** Data may be stale even if the query is fast.
8. **Confusing availability and correctness.** A responsive service can return incomplete or incorrect data.
9. **Setting numbers without evidence.** Mark them as assumptions and validate them against business need, workload and constraints.
10. **Using weighted totals to hide hard failures.** Mandatory constraints and critical requirements should be gates, not merely low-weight criteria.
11. **Scoring alternatives inconsistently.** Define the scale first and use comparable evidence, workload and scope.
12. **Ignoring uncertainty.** A score based on judgement should not be presented as a measured benchmark.
13. **Optimising one quality in isolation.** Faster processing may increase cost or complexity; broader access may increase exposure.
14. **Applying the same target to every asset.** Quality priorities follow use, criticality and risk.
15. **Treating every copy as a second system of record.** Distinguish authoritative writes from read replicas, snapshots and derived assets.
16. **Approving exceptions informally.** A deployed deviation is still unapproved until authorised through the applicable process.
17. **Assuming a compensating control works.** Specify how the control will be tested and evidenced.
18. **Allowing exceptions without expiry.** Revisit or close the exception; repeated requests may signal a deeper design problem.
19. **Failing to communicate principles.** A principle that delivery teams do not know cannot reliably guide their decisions.
20. **Never retiring stale principles.** Review whether principles still serve the business and resolve contradictions explicitly.

## 11. Mastery criteria

You have mastered this lesson when you can demonstrate the following:

- **Principle quality:** write actionable principles with statement, rationale and implications; explain why a slogan is insufficient.
- **Conceptual precision:** distinguish principles, requirements, quality attributes, metrics, targets, observations, constraints, assumptions, policies and exceptions.
- **Measurability:** specify metric, target, measurement window, population, verification method and accountable reviewer for at least six banking requirements.
- **Evidence discipline:** separate illustrative assumptions from observed results; make no unsupported performance or compliance claim.
- **Trade-off reasoning:** analyse the five tensions—performance/cost, availability/consistency, openness/security, agility/control, privacy/analytical usefulness—and justify context-specific priorities.
- **Asset-specific priorities:** explain why customer, transaction, account and aggregated analytical data may need different quality profiles.
- **Fair comparison:** score two candidate designs with consistent criteria, explain the weights and uncertainty, and identify hard constraints that cannot be averaged away.
- **Conflict resolution:** resolve at least one principle conflict using purpose, constraints, evidence, alternatives and residual risk.
- **Exception handling:** complete a record with the violated principle, justification, risk, compensating controls, accountable owner, expiry/review date and approval rationale/status.
- **Principle health:** identify signs of stale, contradictory, unknown or routinely bypassed principles and propose evidence-based responses.

A reviewer should be able to challenge your chosen target, weight, score or exception and understand what evidence supports it, what remains uncertain and what would cause you to change your mind.

## 12. Completion gate

Do not mark this lesson complete until all applicable items are satisfied.

- [ ] Principles set contains no more than eight principles, each with statement, rationale and implications.
- [ ] At least five vague statements have been rewritten as actionable principles, including “use best-of-breed technology” and named domain ownership.
- [ ] Business drivers, constraints and assumptions are correctly distinguished and labelled.
- [ ] At least six banking quality requirements define the asset/scope, metric, target, measurement window, population, verification method, accountable reviewer and evidence basis.
- [ ] Numerical targets are labelled as illustrative assumptions unless supported by supplied or collected evidence.
- [ ] Two candidate designs are evaluated using consistent criteria and a pre-defined scale; scores, weights and uncertainty are explained.
- [ ] The comparison does not claim measured performance or use a weighted total to override a mandatory constraint.
- [ ] Trade-offs cover performance/cost, availability/consistency, openness/security, agility/control and privacy/analytical usefulness.
- [ ] One conflict between principles is resolved with a documented rationale and residual-risk statement.
- [ ] A complete exception record includes principle, justification, risk, compensating controls, accountable owner, expiry/review date and approval rationale/status.
- [ ] Banking scenarios cover sensitive data in a sandbox, real-time dashboards versus cost/complexity, a single-system-of-record deviation and an audit finding that teams do not know the principles.
- [ ] The conditions under which an exception must be refused are explicit.
- [ ] Practice questions D4.1–D4.11 are answered, checked and corrected using the companion assessment and the answer crosswalk in Section 9.
- [ ] A reviewer can trace each major conclusion to a requirement, evidence, assumption or stated judgement.

**Completion standard:** architecture principles guide decisions; measurable quality requirements make those decisions testable; evidence shows what has actually been achieved; and documented exceptions make risk acceptance explicit and reviewable.

---

## Quick reference: quality requirement checklist

Before accepting a quality requirement, ask:

1. What asset, capability, consumer and use case are in scope?
2. Which quality attribute matters, and why?
3. What exact metric will be measured, including start/end events and units?
4. What target and percentile/threshold apply?
5. What measurement window, workload and population are included?
6. How are missing, late, duplicated or invalid data treated?
7. What verification evidence will be collected, by whom and when?
8. Which assumptions or constraints affect feasibility?
9. What happens when the target is missed?
10. What would justify revisiting the target or principle?

If these questions cannot be answered, the requirement is not yet ready to serve as reliable evidence in an architecture decision.
