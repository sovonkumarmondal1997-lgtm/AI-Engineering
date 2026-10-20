# Functional and Non-Functional Requirements

**Stage:** 2D — Data Architecture  
**Module:** 02 — Requirements, Constraints and Architecture Decisions  
**Lesson file:** `02-functional-and-non-functional-requirements.md`  
**Scenario:** Northbridge Bank (fictional; all scenario details and numeric targets are illustrative assumptions)

> **Use of examples:** Northbridge Bank is a fictional mid-sized bank used to practise requirements engineering. All numbers, targets, dates, systems, and policy details introduced in examples are illustrative—not verified facts, legal advice, universal industry standards, or requirements for a real bank. In a real engagement, confirm them with accountable stakeholders and authoritative evidence.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Classify statements as business requirements, system/data requirements, functional requirements, non-functional requirements, data requirements, or constraints—and explain when a statement belongs to more than one related level.
2. Translate business outcomes into behaviours a data capability must provide and quality levels it must achieve.
3. Derive functional requirements across ingestion, validation, transformation, storage, access, sharing, retention, and deletion.
4. Identify relevant quality attributes: reliability, availability, scalability, performance, security, privacy, interoperability, maintainability, cost, and auditability.
5. Recognise vague terms such as *fast*, *secure*, *scalable*, *real-time*, and *user-friendly*, then ask questions that turn them into scoped, measurable statements.
6. Write requirements with a capability, behaviour, scope, conditions, metric, target, and verification method where those elements apply.
7. Define acceptance criteria that support an unambiguous pass/fail decision, specify the test scenario or evidence, and identify the accepting role.
8. Prioritise requirements using explicit business criteria rather than labelling everything “must.”
9. Maintain traceability from business objective and source stakeholder through requirement, acceptance criterion, and later architecture decision.
10. Assess requirement quality for being unambiguous, atomic, testable, consistent, feasible, necessary, and traceable.
11. Identify conflicts and dependencies; manage requirement changes through versioning, impact analysis, and revalidation.
12. Identify architecturally significant requirements and explain how they constrain architecture without prematurely selecting a technology.

**Demonstration standard:** you should be able to produce a sourced requirements register and traceability matrix for the Northbridge customer-data problem, defend priorities and conflicts, and review a flawed requirement set for defects.

## 2. Why the topic matters in real-world Data Architecture

A data architecture is not successful merely because data has been copied into a new platform. It is successful when the resulting data capability supports an agreed business outcome at an acceptable level of quality, under real constraints, with evidence that the outcome has been achieved.

Functional requirements describe **what the capability must do**. Non-functional requirements describe **how well it must do it or under what quality conditions**. Business requirements describe the business outcome; system/data requirements express the capability needed to support that outcome; constraints limit the set of feasible solutions. These levels are related but should not be collapsed into one vague sentence.

Consider a fictional bank whose risk and finance teams report different customer counts. “Build a customer lakehouse” names a preferred solution, but it does not define which customer population should be counted, which source is authoritative, how duplicate or linked identities should be treated, who can see sensitive attributes, or what evidence will show that the counts are consistent. A team could deliver the requested technology and still fail the business problem.

Likewise, “the platform must be highly available” does not tell an architect whether a nightly report may be unavailable for an hour, whether a fraud case tool may be unavailable for a few seconds, or whether a maintenance window is acceptable. The answer affects architecture, operating cost, recovery design, data movement, and operational procedures. A measurable requirement gives the architect a defensible basis for evaluating options.

Requirements matter because they:

- establish what “done” means before design and implementation begin;
- expose missing information and stakeholder disagreement while change is still relatively inexpensive;
- make quality trade-offs visible instead of leaving them to accidental implementation choices;
- help compare feasible architecture options against the same criteria;
- make acceptance objective and repeatable;
- preserve the reason behind decisions when stakeholders, systems, or constraints change; and
- prevent technology preferences from being mistaken for business needs.

The aim is not to write the longest possible specification. It is to write the smallest complete set of clear, necessary, measurable statements that lets a delivery team build and a reviewer verify the right capability.

## 3. Prerequisite concepts

### 3.1 Required prerequisites

- **Module 1 of this module:** stakeholder discovery and business requirements. You should understand stakeholders, business objectives, stated requests versus underlying needs, scope, sources, and open questions.
- **Stage 2D.1, Topic 4:** architecture principles and quality attributes. You should understand that quality attributes influence architecture and need explicit targets.
- **Data engineering foundations from Stages 2–2C:** basic awareness of ingestion, batch and streaming, transformation, storage, serving, and operational behaviour. You do not need to be an expert in every platform.
- **Basic arithmetic and unit handling:** rates, percentages, time units, and simple comparisons.
- **Structured writing:** the ability to document a statement, source, status, and rationale in a table.

### 3.2 Helpful prior knowledge

Familiarity with SQL, CSV/JSON/Parquet, percentile terminology, and a small data pipeline helps you understand how requirements are verified. These are helpful, not prerequisites for learning the classification method.

### 3.3 Terms used in this lesson

| Term | Meaning | Example |
|---|---|---|
| Business requirement | An outcome the organisation needs to achieve | Risk and finance can reconcile the customer population used in their reports. |
| System/data requirement | A capability the system or data ecosystem must provide to support a business requirement | A governed customer view exposes an agreed population definition and its source lineage. |
| Functional requirement (FR) | A required behaviour or function | The pipeline shall reject records missing a required source identifier and record the rejection reason. |
| Non-functional requirement (NFR) | A required quality level or operating condition | The published customer view shall meet an agreed freshness target under stated load conditions. |
| Data requirement | A requirement about data meaning, content, quality, structure, lineage, or lifecycle | Each published customer record shall retain a source-system identifier and source timestamp. |
| Constraint | A binding restriction on the solution space | Personal data must remain within a confirmed jurisdiction. |
| Acceptance criterion | A pass/fail condition used to decide whether a requirement is satisfied | Given a test record with a missing mandatory identifier, the pipeline records it in the rejection output with the defined reason code. |
| Verification method | How evidence will be obtained | Automated integration test, controlled load test, audit-log inspection, or business reconciliation. |
| Traceability | A maintained link between a requirement and its origin, verification, and downstream use | Business objective → requirement ID → acceptance criterion → architecture decision. |
| Architecturally significant requirement | A requirement likely to materially influence the structure or choice of architecture | A stringent freshness target, a recovery objective, or a confirmed data-residency constraint. |

A statement can relate to several categories at different levels. For example, “reduce fraud losses” is a business outcome; “make card transactions available to the fraud case tool” is a functional capability; “95% available within 30 seconds” is a quality target only if the metric, population, measurement boundary, and time window are agreed. Do not force a single sentence to carry every level.

## 4. Beginner-level learning sequence

### 4.1 Learn the requirement levels

Use this sequence to reason from business intent toward testable behaviour:

1. **Business requirement — outcome:** What business problem or outcome matters?
2. **System/data requirement — capability:** What capability is needed to support that outcome?
3. **Functional requirement — behaviour:** What must the capability do?
4. **Non-functional requirement — quality:** How well must it perform, or under what quality conditions?
5. **Constraint — boundary:** What limits the feasible options regardless of preference?

Example (illustrative):

- **Business:** Fraud analysts need timely transaction information to investigate suspicious activity.
- **System/data capability:** The fraud case tool can access the relevant card transaction data.
- **Functional:** The data capability shall publish each accepted card transaction to the agreed fraud-case interface.
- **Non-functional:** Under an agreed workload, end-to-end freshness shall meet a stakeholder-approved percentile and time target.
- **Constraint:** The source platform currently emits batch files at a stated interval. This is a current-state fact only if verified; it may limit options but should not be silently treated as permanent.

### 4.2 Functional requirements across the data lifecycle

Walk through the lifecycle to discover missing behaviours. A pipeline is more than ingestion and transformation; access, retention, and deletion are also part of the required capability.

| Lifecycle stage | Questions to ask | Illustrative functional requirement |
|---|---|---|
| Ingestion | Which sources, records, triggers, and failure cases must be handled? | The ingestion capability shall record the source, extraction time, and batch identifier for every ingested source batch. |
| Validation | Which fields, rules, and invalid-record paths are required? | The pipeline shall route records that fail the approved mandatory-field checks to a rejection output with a reason code. |
| Transformation | Which business rules define the output? How are duplicates and conflicting values handled? | The customer consolidation process shall apply the approved matching rules and retain the resulting match status. |
| Storage | Which records and history must be retained, and how must they be retrievable? | The capability shall retain the agreed customer identity mapping and its effective dates. |
| Access | Which roles can perform which actions? | The capability shall allow authorised risk analysts to query the approved customer view. |
| Sharing | Which consumers receive which data, in what form, and through what interface? | The capability shall expose the approved customer attributes to named authorised consumer groups through an agreed interface. |
| Retention | What is retained, for how long, and what event starts the clock? | The capability shall apply the approved retention schedule to the defined record category, with exceptions recorded. |
| Deletion | What must be deleted, when, and what evidence is required? | On an approved deletion instruction, the capability shall apply the agreed deletion workflow to in-scope copies and record the outcome. |

These examples illustrate behaviour, not approved Northbridge requirements. Words such as “approved,” “authorised,” and “agreed” indicate information that must be established before acceptance. The architect should not invent the matching rules, retention period, or access policy.

### 4.3 Understand the ten quality attributes

A quality attribute is a dimension of system behaviour or operation that can influence architecture. It must be defined in the context of the actual business use case.

| Attribute | What it asks | Possible evidence or measure | Common trap |
|---|---|---|---|
| Reliability | Does the capability continue to produce correct service despite faults? | Successful processing rate, failure frequency, recovery behaviour | Treating “reliable” as self-explanatory. |
| Availability | Is the capability usable when needed? | Successful requests divided by eligible requests over a stated window; planned downtime treatment | Confusing availability with correctness or freshness. |
| Scalability | Can it handle growth or changing demand? | Throughput and latency at defined load levels; supported growth range | Saying “scalable” without defining load or growth. |
| Performance | How quickly does a specific operation complete? | Latency percentiles, query duration, processing time | Reporting only an average when tail latency matters. |
| Security | How is the capability protected against unauthorised access or change? | Access-control tests, privileged-action logs, security test evidence | Using “secure” without threat, action, or control scope. |
| Privacy | How is personal data collected, used, disclosed, retained, and minimised? | Approved access/use cases, minimisation checks, retention/deletion evidence | Assuming privacy is identical to security. |
| Interoperability | Can systems exchange and interpret data correctly? | Contract/schema compatibility tests, agreed semantics, successful exchange | Treating a successful file transfer as semantic compatibility. |
| Maintainability | Can the capability be diagnosed, changed, and operated safely? | Change lead time, documented recovery procedure, testability, supportability | Using “easy to maintain” without an observable indicator. |
| Cost | What cost limit or cost behaviour is acceptable? | Cost per workload unit, monthly/annual ceiling, cost under a defined scenario | Quoting cost without workload, scope, or period. |
| Auditability | Can actions, lineage, decisions, and evidence be reconstructed? | Required events and lineage fields present; retrieval test; retention of evidence | Assuming logs alone prove data lineage or business meaning. |

Do not require every attribute at the same level for every system. Identify the attributes relevant to the business outcome, then quantify the ones that matter. Some attributes overlap: a successful availability check does not prove data correctness, and an access-control test does not by itself prove privacy compliance.

### 4.4 Recognise vague words

Vague words are not automatically bad; they are useful starting points in discovery. They are insufficient as final requirements because different stakeholders can interpret them differently.

| Vague statement | What is missing? | Questions that make it specific |
|---|---|---|
| “The report must be fast.” | Operation, population, workload, latency metric, target, measurement point | Which report and users? At what data volume and concurrency? Is p95 or maximum latency relevant? From which start to end timestamp? |
| “The platform must be secure.” | Threats, actors, data classes, actions, controls, evidence | Which roles and data? Which actions must be denied? Which controls are mandatory, and how will they be tested? |
| “The system must scale.” | Current and future load, growth horizon, acceptable quality under load | How many records or requests today and at the target horizon? What peak load must be supported? Which quality target must remain satisfied? |
| “Data must be real-time.” | Business decision, acceptable delay, source event, end point, percentile | What decision is blocked by delay? What is the maximum acceptable age? Where is freshness measured? What fraction of events must meet it? |
| “The interface must be user-friendly.” | User tasks, user groups, success measures, context | Which users and tasks? What task completion rate or error rate is acceptable? What usability test and sample will verify it? |

### 4.5 Is “reports must run quickly” functional or non-functional?

Usually, “run a report” describes a function, while “quickly” describes an intended performance quality. The statement is therefore mixed and incomplete. Split it into two linked requirements if both are needed:

- **FR:** The reporting capability shall generate the defined daily exposure report for the agreed business-date population.
- **NFR:** For the agreed input volume and concurrency, the report shall complete within a stakeholder-approved duration at a defined percentile, measured from request acceptance to result availability.

The actual duration and percentile must come from discovery, baseline measurements, business tolerance, or an accountable decision—not from the writer's intuition.

### 4.6 Beginner exercise: classify twenty statements

Classify each statement using one primary category: **B** business, **S** system/data capability, **F** functional, **N** non-functional, **D** data requirement, **C** constraint. Also mark whether it is measurable/testable as written (**Yes**, **Partly**, or **No**). Some statements are intentionally mixed; identify the dominant issue and explain what is missing.

1. Risk and finance need to reconcile the customer population in their monthly reports.
2. Use Kafka for every customer update.
3. The pipeline shall ingest the agreed daily card transaction extract.
4. The pipeline must be fast.
5. Personal data must remain within the jurisdiction confirmed by the control owner.
6. Each customer record shall carry a source-system identifier.
7. The customer view shall be available 99.9% of the time each calendar month, measured by successful eligible requests. *(Illustrative target; measurement details still need definition.)*
8. The platform should scale as the business grows.
9. The deletion workflow shall record the request ID and completion status for each approved request.
10. Analysts need fewer conflicting customer counts.
11. The report shall complete in under 10 seconds. *(Illustrative; scope and load are missing.)*
12. The capability shall allow the compliance role to retrieve lineage for a selected published customer record.
13. The system shall be secure.
14. The service must use the existing identity provider, if confirmed as a binding constraint by its owner.
15. The transformation shall apply the approved customer matching rule version.
16. Monthly operating cost must be below ₹X. *(X is deliberately unspecified.)*
17. The pipeline shall validate required fields before publishing a record.
18. All data must be correct.
19. The interface shall support the agreed schema contract and reject unsupported schema versions with a documented error.
20. The capability shall be easy to maintain.

#### Answer guidance

| # | Primary classification | Measurability | Reason / missing detail |
|---:|---|---|---|
| 1 | B | Partly | Outcome is clear in direction; define population, reconciliation tolerance, reports, and acceptance owner. |
| 2 | Solution preference, not a valid requirement category by itself | No | Technology is prescribed without evidence of necessity; state the required behaviour or a verified constraint. |
| 3 | F | Partly | “Agreed” extract and completeness/error behaviour must be defined. |
| 4 | N | No | No operation, workload, metric, or target. |
| 5 | C | Partly | The actual jurisdiction and authoritative source must be named. |
| 6 | D | Yes, with details | Identifier presence is testable; define format, nullability, and uniqueness if needed. |
| 7 | N | Partly | Target is numeric, but eligible requests, exclusions, monitoring source, and measurement window need definition. |
| 8 | N | No | Growth, horizon, workload, and preserved quality levels are absent. |
| 9 | F / auditability-related behaviour | Partly | Define approved request, completion meaning, and where the evidence is retained. |
| 10 | B | Partly | Need a baseline and an observable definition of “fewer.” |
| 11 | N | Partly | Duration is numeric but report scope, load, percentile, and measurement boundary are missing. |
| 12 | F | Partly | Define “compliance role,” lineage scope, and successful retrieval criteria. |
| 13 | N | No | Threats, actors, controls, and verification are absent. |
| 14 | C if binding; otherwise preference | Partly | Verify authority and whether alternatives are genuinely prohibited. |
| 15 | F / D | Partly | Link to a versioned, approved rule definition and define how its application is tested. |
| 16 | N / economic constraint | No | Currency, scope, period, workload, included costs, and X are missing. |
| 17 | F | Partly | Define required fields, validation rules, and invalid-record outcome. |
| 18 | N / data quality objective | No | Define correctness dimensions, population, tolerance, and measurement. |
| 19 | F / interoperability | Partly | Identify the contract and version policy; define rejection evidence. |
| 20 | N | No | Replace “easy” with observable maintainability needs and verification evidence. |

**Self-check:** explain why a statement can be directionally useful but not yet testable. Do not mark a statement “measurable” solely because it contains a number; scope and measurement semantics matter too.

## 5. Intermediate-level learning sequence

### 5.1 Use a requirement-writing pattern

Use this pattern as a checklist, not a rigid sentence that must be filled with meaningless values:

> The **[system/data capability]** shall **[behaviour or quality]** for **[scope]** under **[conditions]**, measured by **[metric]** with target **[value and tolerance]**, verified by **[method/evidence]**.

For functional requirements, the behaviour and scope are central; a metric may be a count, state, or rule outcome rather than a performance number. For non-functional requirements, include the quality attribute, measurement boundary, workload/conditions, metric, target, time window, and verification method. Every requirement needs a source and owner even if these are recorded in register columns rather than the sentence itself.

A useful requirement should be:

- **Necessary:** it supports a real business objective or binding constraint.
- **Unambiguous:** one reasonable interpretation in the agreed context.
- **Atomic:** one primary obligation; split statements that require independent pass/fail decisions.
- **Testable:** evidence can determine pass or fail.
- **Feasible:** plausible under known constraints, subject to validation where uncertainty remains.
- **Consistent:** does not contradict another accepted requirement or rule.
- **Traceable:** source and downstream verification/decisions are linked.

### 5.2 Rewrite vague statements into measurable requirements

The roadmap's illustrative example is “The risk report must be fast.” A more useful version is:

> The daily credit-exposure report shall be available to risk analysts by 07:00 local time on every business day, on at least 99% of business days over a rolling quarter, measured by the report-completion timestamp.

The 07:00 and 99% values are **illustrative targets**, not standards. Before treating this as acceptance-ready, clarify the reporting calendar, eligible days, definition of “available,” data completeness, failure handling, clock/time zone, measurement source, exclusions, and who accepts the result. A report that is published by 07:00 but contains incomplete data may not satisfy the underlying business need; freshness and completeness may need separate linked requirements.

Another example:

- **Bad:** “The customer platform shall provide real-time data using Kafka.”
- **Better functional requirement:** “The capability shall make each accepted card transaction available to the fraud case tool after the source event is received, for the agreed transaction population.”
- **Better NFR structure:** “For the agreed transaction population and peak-load profile, p95 end-to-end freshness shall be no greater than [approved target], measured from [authoritative source timestamp] to [case-tool availability timestamp] over [measurement window].”

The placeholders are deliberate. Ask stakeholders for a target and validate it against source capabilities and business tolerance. The requirement does not select Kafka, streaming, or another design; those are options to evaluate later.

### 5.3 Define acceptance criteria and verification

Acceptance criteria state what evidence is sufficient to pass. A criterion should identify the scenario, the expected result, and the verification approach. Where formal acceptance is required, name the accountable accepting role rather than a person whose authority is unknown.

**Worked example (illustrative):**

- **Requirement:** FR-04 — The ingestion capability shall route a record that lacks a mandatory source customer identifier to the rejection output and record the approved reason code.
- **Acceptance criterion AC-FR-04b:** Given a test batch containing one record with the identifier missing and one valid record, when the batch is processed, the invalid record appears once in the rejection output with the configured missing-identifier reason code, and the valid record follows the normal processing path.
- **Verification:** automated integration test using controlled fixtures; inspect output and processing log.
- **Accepting role:** data product/business owner designated for customer data, with engineering evidence reviewed by the technical lead. These roles are illustrative and must be confirmed.
- **Pass:** all expected output and reason-code assertions match; no duplicate rejection is produced for the same input record in the test.
- **Fail:** the invalid record is published as valid, is silently dropped, lacks the reason code, or the valid record is incorrectly rejected.

Avoid criteria such as “works correctly” or “stakeholder is happy.” They do not tell a reviewer what to test or how to resolve disagreement.

### 5.4 Worked Northbridge requirements set: six functional and six non-functional

**Scenario facts supplied by the roadmap, all illustrative:** Northbridge Bank is fictional. It has a core banking system, a separate cards platform, CRM, and loan origination system. Nightly extracts feed an enterprise data warehouse, and a data lake contains copies of some sources. Risk, finance, marketing, and compliance report different customer counts. Fraud analysts see card transactions hours after the fact. A regulator has requested clearer evidence of lineage and customer-data accountability within a stated period. The roadmap's initial assumptions include about 3 million retail customers, about 2 million card transactions per day on average, card batch files every 15 minutes today, seven-year retention for transaction records, and a programme budget ceiling set by the sponsor. These are not verified facts about a real organisation.

The following twelve requirements are **teaching examples**, not approved requirements. Their targets and role assignments must be validated before use.
Each row has a unique acceptance-criterion ID so the traceability matrix can refer to it unambiguously. All IDs, sources, and priorities are illustrative draft entries; confirm them with accountable stakeholders before baselining.

| ID | Type | Requirement statement | Source / objective (illustrative; confirm) | Priority | Acceptance criterion ID, criterion and verification | Status |
|---|---|---|---|---|---|---|
| FR-01 | Functional | The ingestion capability shall ingest the agreed customer and account extracts from each in-scope source and record source name, extraction timestamp, and batch ID. | Risk and finance business owners; customer-count objective; exact source inventory to confirm | Must (provisional) | **AC-FR-01a:** For a controlled test batch from each agreed source, every accepted row is linked to the correct source and batch metadata. Verify with integration tests and reconciliation. | Draft illustrative example; source confirmation pending |
| FR-02 | Functional | The customer consolidation process shall apply the approved, versioned matching rules and retain the resulting match status for each in-scope input record. | Risk and finance business owners; consistent customer-population objective; matching-rule owner to confirm | Must (provisional) | **AC-FR-02a:** Test records covering each approved matching case produce expected match statuses under the recorded rule version. Business owner validates expected results. | Draft illustrative example; rule approval pending |
| FR-03 | Functional | The published customer view shall expose the agreed customer population definition and source lineage to authorised risk and finance consumers. | Risk and finance business owners; compliance/control owner for lineage evidence; exact source definitions to confirm | Must (provisional) | **AC-FR-03a:** A role-based test confirms permitted users can retrieve population definition and lineage for sampled records; an unauthorised test role is denied. Verify with acceptance and access-control tests. | Draft illustrative example; definitions and access policy pending |
| FR-04 | Functional | The ingestion capability shall route records that fail approved mandatory-field checks to a rejection output with a reason code. | Source/data owner and engineering lead; data-quality and diagnosability objective; mandatory-field rules to confirm | Should (provisional) | **AC-FR-04a:** Invalid and valid test fixtures produce the specified rejection and normal paths. Verify with automated integration tests. | Draft illustrative example; validation rules pending |
| FR-05 | Functional | The capability shall publish accepted card transactions to the agreed fraud-case interface and retain a correlation identifier linking source event to published record. | Fraud operations owner; timely fraud-investigation objective; interface and source-event semantics to confirm | Must (provisional) | **AC-FR-05a:** Given test events, each accepted event can be located in the case interface and traced to its source identifier. Verify end-to-end with a controlled test. | Draft illustrative example; interface contract pending |
| FR-06 | Functional | The capability shall apply the approved retention schedule to the defined data categories and record the outcome of each authorised retention action. | Data-governance/policy owner; lifecycle-governance objective; authoritative retention schedule to confirm | Must only if the policy owner confirms a binding obligation; otherwise pending | **AC-FR-06a:** Test a synthetic record through the approved retention-expiry workflow and verify the required action and evidence for each in-scope copy. Acceptance owner confirms policy interpretation. | Draft illustrative example; retention policy pending |
| NFR-01 | Performance / freshness | For the agreed card-transaction population and peak-load profile, p95 end-to-end freshness shall be no greater than **[target to be agreed]**, measured from the authoritative source event timestamp to availability in the fraud case tool over **[window to be agreed]**. | Fraud operations owner; timely fraud-investigation objective; source timestamp and capability to validate | Must candidate; target unresolved | **AC-NFR-01a:** Run a representative load test; calculate p95 from agreed timestamps and sampling window. Pass only if the approved target and completeness conditions are met. | Proposed; not acceptance-ready until target/window are approved |
| NFR-02 | Availability | The fraud-case data capability shall meet **[availability target to be agreed]** over **[measurement window]**, measured using defined successful eligible requests and agreed exclusions. | Fraud operations owner; fraud-case operational need; availability boundary and monitoring source to confirm | Must candidate; target unresolved | **AC-NFR-02a:** Observe the agreed test/operational window, calculate availability from the agreed monitoring source, and review excluded events with the service owner. Pass/fail requires an approved target, window, and exclusions. | Proposed; not acceptance-ready until target/window are approved |
| NFR-03 | Data quality | The published customer view shall meet the business-approved reconciliation tolerance for the defined customer population and reporting date. | Risk and finance business owners; consistent customer-count objective; reference population and tolerance to confirm | Must candidate; tolerance unresolved | **AC-NFR-03a:** Compare against the agreed reference population using a documented reconciliation procedure. Pass/fail threshold and treatment of legitimate population differences must be approved first. | Proposed; not acceptance-ready until definition/tolerance are approved |
| NFR-04 | Security / privacy | Access to sensitive customer attributes shall be restricted according to the approved role-to-attribute policy. | Designated security/privacy control owner; authoritative role-to-attribute policy to confirm | Must candidate; binding policy and scope to confirm | **AC-NFR-04a:** Execute positive and negative role/attribute tests against the approved policy. Pass only when permitted access succeeds and prohibited access is denied; designated control owner accepts the evidence. | Proposed; policy confirmation pending |
| NFR-05 | Auditability | For each published customer record in the sampled scope, the capability shall provide the required source-to-output lineage fields defined by the accountable control owner. | Compliance/control owner; lineage and accountability request; required evidence fields to confirm | Must candidate; field list unresolved | **AC-NFR-05a:** Sample published records and verify every approved lineage field can be retrieved and linked to source. Audit/control owner confirms sufficiency. | Proposed; not acceptance-ready until field list is approved |
| NFR-06 | Cost | For the approved workload and growth scenario, forecast monthly operating cost shall not exceed **[confirmed cost ceiling]**, using agreed cost categories and exclusions. | Sponsor/budget owner; programme cost boundary and growth scenario; ceiling and cost scope to confirm | Must only if the budget owner confirms a binding ceiling | **AC-NFR-06a:** Reconcile a documented cost model against the approved workload, monthly period, cost categories, exclusions, and ceiling. Pass/fail is determined by the confirmed ceiling; quality targets must not be silently relaxed to achieve it. | Proposed; not acceptance-ready until ceiling/scope are approved |

The table intentionally shows unresolved targets instead of fabricating values. A requirement can be sufficiently structured to drive discovery while remaining **not ready for acceptance**. Track the missing decision, owner, evidence, and due date. “Must (provisional)” is not a final priority until the accountable decision-maker confirms it.

### 5.5 Prioritise without making everything “must”

A lightweight Must/Should/Could scheme is useful when its rules are explicit:

- **Must:** failure to meet it prevents the agreed business outcome, violates a confirmed binding constraint, or blocks an essential control. Explain the basis.
- **Should:** materially improves the outcome or reduces risk, but a controlled first release can still meet its purpose without it.
- **Could:** useful if capacity and budget allow, but lower value than higher-priority items.
- **Not now / out of scope:** explicitly deferred or excluded; record the rationale and revisit trigger if relevant.

Do not use “Must” as a synonym for “stakeholder asked for it.” Priority is a decision, not a property of the sentence.

**Worked example (illustrative):**

| Candidate requirement | Initial assessment | Reason and action |
|---|---|---|
| Trace source lineage for sampled published customer records | Must candidate | May be needed for the stated accountability objective; control owner must define evidence required. |
| Publish card transactions to the fraud case tool within a strict low-latency target | Must outcome candidate; target unresolved | Business value may be high, but confirm actual delay tolerance and source feasibility before fixing the target. |
| Provide a custom dashboard theme | Could | No evidence it is necessary to the customer consolidation outcome. |
| Replace the existing identity provider | Out of scope unless constraint changes | Roadmap scenario states the existing identity provider must be used as an illustrative constraint; do not create a replacement requirement. |

Record the prioritisation criteria, who made the decision, and what would cause the priority to change. Where regulatory or policy obligations may apply, confirm them with the responsible control function rather than inferring obligations from the word “regulator.”

### 5.6 Dependencies and conflicts

A **dependency** exists when a requirement or its verification relies on another capability, decision, or input. A **conflict** exists when two requirements cannot both be satisfied as currently stated under the same conditions or available resources.

Examples:

- FR-02 depends on an approved customer-matching definition and an accountable owner for that definition.
- NFR-01 depends on source event timestamps, an agreed measurement boundary, and the fraud case tool's availability and behaviour.
- NFR-04 may constrain which attributes FR-03 can expose to risk and finance.
- A stricter freshness target may conflict with a requirement to wait for all validation or matching evidence before publishing.
- A lower cost ceiling may conflict with a high availability target if redundancy or recovery capacity is needed.

Do not resolve these by silently weakening one requirement. Record the pair, the affected objective, evidence required, options, decision authority, and the acceptance conditions for the chosen resolution.

### 5.7 Intermediate exercise: write twelve requirements

Using the Northbridge scenario, write **six functional and six non-functional requirements**, each with:

- ID and classification;
- source stakeholder or source evidence;
- linked business objective;
- scope and conditions;
- priority and rationale;
- acceptance criterion with pass/fail conditions;
- verification method and accepting role; and
- open questions or dependencies.

**Answer guidance:** the twelve rows in Section 5.4 are one illustrative model. Your requirements need not use identical wording, but every target must be justified or labelled unresolved. Check that the six functional items describe behaviours, while the six NFRs define quality or operating conditions. Do not use a product name as a requirement unless the scenario establishes it as a genuine constraint.

**Intermediate exit condition:** every requirement is classified, sourced, measurable/testable to the extent possible, and accompanied by an explicit open question where evidence or a decision is still missing. A reviewer should find no unmeasurable “must” statement without a recorded justification.

## 6. Advanced-level learning sequence

### 6.1 Review requirements systematically for defects

Use the following review checklist for each requirement and for the set as a whole.

| Quality check | Review question | Typical defect | Correction |
|---|---|---|---|
| Unambiguous | Could two competent readers interpret it differently? | “Current customer” is undefined. | Define the population, effective date, and business rule owner. |
| Atomic | Can it pass one test and fail another independently? | “Ingest, reconcile, secure, and report all customer data within five seconds.” | Split behaviour and quality obligations into linked requirements. |
| Testable | Can evidence produce a repeatable pass/fail result? | “The platform is intuitive.” | Define tasks, user group, test method, and acceptable outcome. |
| Consistent | Does it contradict another requirement or approved rule? | One requirement allows all attributes to all analysts; another restricts sensitive fields. | Record conflict, clarify roles and purposes, and obtain an authorised decision. |
| Feasible | Is it plausible under source, budget, schedule, and operational constraints? | Demand sub-second freshness from a source that only provides daily files, without changing the source. | Verify the constraint, quantify business need, and compare feasible options. |
| Necessary | Does it support an objective or confirmed constraint? | “Use a fashionable technology.” | Remove it or document the business/technical reason as a constraint only if genuinely binding. |
| Traceable | Can it be traced to a source and forward to acceptance and decisions? | Requirement has no source or owner. | Add source, objective, verification, and downstream links. |

**Set-level checks** are also necessary. A set can contain individually good requirements yet omit deletion, access control, failure handling, or a required consumer. Review lifecycle coverage, relevant quality attributes, scope boundaries, duplicates, and interactions.

### 6.2 Identify architecturally significant requirements

An architecturally significant requirement is one likely to change the structure of the solution or eliminate entire classes of options. It is not simply a high-priority requirement. Some high-priority functional requirements are straightforward; some NFRs constrain many design decisions.

Common examples include:

- **Freshness/latency:** a strict end-to-end freshness target may require different ingestion, buffering, processing, and serving choices than a nightly batch target.
- **Availability and recovery:** required availability, recovery time, and acceptable data loss after failure affect redundancy, replication, recovery design, and operations.
- **Data residency:** a confirmed jurisdiction constraint can restrict where data and backups are processed or stored.
- **Security and privacy:** attribute-level access and permitted-use rules can affect data products, views, isolation, and identity integration.
- **Auditability and lineage:** required evidence can affect metadata capture, identifiers, event records, and retention of audit evidence.
- **Scale and growth:** peak throughput and retained history can change storage, partitioning, compute, and cost assumptions.
- **Interoperability:** contracts and compatibility expectations affect interface and schema-evolution choices.

Use a short significance record:

| Requirement ID | Why it may shape architecture | Evidence/uncertainty | Options potentially affected | Reversal condition |
|---|---|---|---|---|
| NFR-01 freshness | Could change ingestion and serving approach | Source cadence and target not yet validated | Batch-only, micro-batch, event-based options | Target relaxed or source capability changes |
| NFR-04 access restrictions | May affect data exposure and isolation | Approved role/attribute policy pending | Shared views, restricted products, separated datasets | Control owner changes permitted access model |
| NFR-05 lineage | May affect metadata capture and record identifiers | Required evidence fields pending | Source metadata and lineage approaches | Control owner accepts a different evidence method |

These are candidate implications, not architecture decisions. The requirement should describe the needed outcome and quality; option comparison belongs to later work.

### 6.3 Resolve conflicting requirements using interests, evidence, and authority

A conflict should be made explicit, not hidden inside compromise wording.

**Example: broad analytical access versus sensitive-data restrictions (illustrative).**

- **Position A:** “Analysts must query every customer attribute.”
- **Position B:** “Sensitive attributes must be restricted by role and purpose.”
- **Underlying interests:** analysts need sufficient information for approved decisions; control functions need to prevent unauthorised exposure and preserve evidence.
- **Evidence to collect:** approved use cases, role definitions, attribute classification, current access patterns, data minimisation policy, and the control owner's interpretation.
- **Options to examine:** purpose-specific views, masking or aggregation where appropriate, role-based attribute access, approved exception workflows, or separating sensitive attributes from general analytical data. These are option categories, not preselected designs.
- **Decision authority:** the business owner determines legitimate business use; the designated security/privacy/control authority confirms control requirements; the architecture decision forum evaluates feasible options and records the trade-off. Exact roles must be confirmed in the organisation.
- **Record:** the conflict, options, evidence, selected resolution, rejected options, residual risks, owner, and revalidation trigger.

The architect should not decide that broad access wins because it is easier, nor that a restrictive policy applies because it sounds safer. Obtain authoritative requirements and make the trade-off visible.

### 6.4 Handle changing requirements with versioning and impact analysis

Requirements change when business priorities, source capabilities, policy interpretation, volume, deadlines, or assumptions change. A change is not simply an edit to a sentence; it can invalidate tests, commitments, and architecture decisions.

For each change:

1. Record the change request, requester, date, reason, and supporting evidence.
2. Identify the affected requirement and create a new version or revision history entry; do not overwrite the approved baseline without a record.
3. Compare old and proposed wording, including scope, metric, target, conditions, and priority.
4. Traverse traceability links to affected business objectives, acceptance criteria, tests, data contracts, dependencies, risks, and architecture decisions.
5. Assess impact on feasibility, cost, delivery date, quality trade-offs, and other requirements. Mark unknown impacts explicitly.
6. Obtain a decision from the correct authority. Record accepted, rejected, deferred, and conditional changes separately.
7. Revalidate affected requirements and acceptance criteria; repeat relevant tests or design reviews.
8. Update downstream artefacts and notify affected owners and consumers.

**Worked impact example (illustrative):** The sponsor changes the card-transaction freshness target from a broad “within minutes” expectation to a much stricter target. Do not immediately choose a streaming technology. First confirm the business reason and precise metric; validate source timestamp quality and source emission capability; identify FR-05 and NFR-01, their acceptance tests, and any architecture decision comparing batch and event-oriented options; estimate the effects on cost, operations, failure recovery, and completeness; then re-open the affected decision if its evidence no longer supports it. Revalidate the end-to-end test and obtain renewed acceptance.

A requirement's version should identify its status (draft, proposed, approved, superseded), owner, approval date, and change history. The exact versioning scheme can be simple; the critical point is preserving which version was used to make a decision and accept a release.

### 6.5 Avoid over-specification

A requirement should state **what must be true**, not prematurely dictate **how it must be implemented**.

| Statement | Assessment | Better formulation |
|---|---|---|
| “Use Kafka for customer changes.” | Technology choice disguised as a requirement unless it is a verified constraint. | Define required event coverage, ordering semantics if needed, freshness, durability, and consumer behaviour; evaluate technology options later. |
| “Store all data in a lakehouse.” | Architecture preference; it does not define use cases, access, quality, or lifecycle. | State the required data access, retention, lineage, quality, and workload outcomes. |
| “The customer view must be queryable by risk analysts.” | Functional need, but scope and authorization may be incomplete. | Name the approved customer population and attributes, permitted role, query use cases, and relevant access criteria. |
| “The service shall recover within four hours.” | Potentially valid NFR if the target is approved and measurement conditions are defined. | Define service boundary, recovery point, failure scenario, recovery-time measurement, data-loss tolerance, and test method. |

Sometimes a technology is a genuine constraint: for example, a contract may mandate an existing identity provider. Verify who owns the constraint, its source, whether it is binding, and whether an exception process exists. Do not elevate a stakeholder preference into a fixed constraint without evidence.

### 6.6 Advanced exercise: review a flawed requirements set

Review the following fictional set. Targets and constraints are deliberately incomplete.

1. “The platform shall be fast and real-time.”
2. “All customer attributes must be available to every analyst, and sensitive data must never be exposed to unauthorised users.”
3. “Use Kafka and a lakehouse because they are industry standard.”
4. “The pipeline shall ingest, validate, transform, publish, and delete all data correctly.”
5. “The system must be 100% available forever.”
6. “The customer count must match finance exactly.”
7. “The platform shall be highly scalable and cost-effective.”
8. “The system shall retain transaction data for seven years.”
9. “The system must satisfy the regulator.”
10. “All requirements are Must priority.”

**Defect review and suggested rewrite direction:**

| # | Defect categories | Why it fails | Correction direction |
|---:|---|---|---|
| 1 | Ambiguous, untestable, non-atomic | No operation, source, endpoint, percentile, target, workload, or time window. | Separate the required behaviour from freshness/performance; obtain approved metrics and conditions. |
| 2 | Potential conflict, ambiguous scope | “Every analyst,” “all attributes,” and “unauthorised” are undefined; the two obligations may conflict. | Define roles, purposes, attributes, and control policy; use a conflict log and authorised decision. |
| 3 | Over-specified solution, unsupported rationale | Technology is asserted without scenario evidence or comparison. | Replace with outcome and quality requirements; treat technologies as options unless a verified constraint exists. |
| 4 | Non-atomic, vague, likely untestable | Many independent lifecycle behaviours are bundled; “correctly” is undefined. | Split by lifecycle behaviour, data scope, rules, failure path, and acceptance criteria. |
| 5 | Infeasible and ambiguous | No finite service can be assumed available without interruption forever; window and exclusions are absent. | Define a realistic approved availability target, measurement window, failure model, and exclusions. |
| 6 | Ambiguous and potentially infeasible | “Finance” may use a different population definition; “exactly” hides semantics and legitimate differences. | Agree population, date, matching rules, exclusions, tolerance, and accountable business definition owner. |
| 7 | Vague NFRs | No load, growth horizon, cost scope, or target. | Define workload and growth scenarios, quality preserved, cost boundary, and verification method. |
| 8 | Incomplete data/lifecycle requirement | Seven years is a scenario assumption, not necessarily an approved policy; start event, record category, copies, and deletion are undefined. | Verify retention authority and define scope, clock start, exceptions, and evidence of expiry/deletion. |
| 9 | Unbounded and unsupported | No specific request, applicable obligation, evidence, scope, or accountable control owner. | Obtain the authoritative requirement and translate it into specific testable obligations. |
| 10 | Poor prioritisation | No trade-off or criteria; all requirements cannot be assumed equally critical. | Apply documented criteria, record decision authority, and distinguish must/should/could/out of scope. |

For each item, record the defect category, severity, rationale, revised wording or open question, source needed, owner, and whether the defect is resolved. Do not invent missing values to make a row look complete.

### 6.7 Which five requirements constrain the architecture most?

There is no universally correct ranking before the missing facts are confirmed. A defensible initial shortlist for Northbridge would be:

1. **Card transaction freshness (NFR-01):** may distinguish batch, micro-batch, or event-oriented options; target and source capabilities remain unknown.
2. **Availability and recovery expectations (NFR-02):** may affect redundancy, operations, and recovery approach; target and failure boundary remain unknown.
3. **Sensitive-attribute access restrictions (NFR-04):** may affect data exposure and isolation; authoritative policy remains to be confirmed.
4. **Lineage and audit evidence (NFR-05):** may require source metadata and evidence capture throughout processing; exact fields and retention are unresolved.
5. **Customer population and matching semantics (FR-02/NFR-03):** determine what “one customer count” means and which data/model approaches are viable; the business definition and reconciliation tolerance remain unresolved.

This is a **candidate shortlist**, not an approved priority order. A confirmed jurisdiction constraint or a binding retention obligation could be equally or more architecture-constraining. The architect should ask: what evidence supports the target, which options does it eliminate, what is the cost of relaxing it, and what new evidence would reverse the conclusion?

### 6.8 Advanced exercise: challenge and defend

Prepare a one-page defence of your requirement set. A reviewer should challenge at least two items—for example, whether the freshness target is necessary, or whether broad access can coexist with sensitive-data restrictions. For each challenge:

- restate the objective and requirement;
- cite source evidence and assumptions separately;
- identify the options and trade-offs;
- state what uncertainty remains;
- name the decision authority; and
- state what evidence would change your recommendation.

**Advanced exit condition:** you can review a requirement set, find and categorise defects, rewrite or defer defective items, identify architecture-driving requirements, and defend the result without hiding uncertainty.

## 7. Industry-application exercises

Complete the following exercises using the Northbridge customer-consolidation scenario. All values not stated by the roadmap must be marked as assumptions or left unresolved.

### Exercise A — Requirements register

Create a register for the customer consolidation problem. Include at least the fields in the blank template in Section 9.1. Include business, functional, non-functional, data, and constraint entries as appropriate. Every entry needs a source or a clearly labelled open question.

**Expected evidence:** a reviewer can tell what each requirement means, why it exists, who owns it, how it will be tested, and what remains unknown.

### Exercise B — Traceability matrix

Create links from each business objective to requirements and acceptance criteria. Include at least one path that continues to an architecture decision or decision question. Mark downstream decisions as “pending” if they have not been made.

**Expected evidence:** no requirement is orphaned, and each business objective has at least one meaningful verification path. A traceability link is not proof that the requirement is correct; it makes the reasoning inspectable.

### Exercise C — Vague-word hunt

Review this paragraph:

> “Northbridge needs a fast, secure, scalable, real-time customer platform. It should be user-friendly, highly available, cost-effective, and fully compliant. Use a modern lakehouse so all analysts can access everything, and make sure the customer count is always correct.”

Mark every vague word or solution preference. For each, write a clarification question and the requirement category it may become.

**Answer guidance:** investigate *fast*, *secure*, *scalable*, *real-time*, *user-friendly*, *highly available*, *cost-effective*, *fully compliant*, *modern lakehouse*, *all analysts*, *everything*, and *always correct*. Ask about the actual business decisions, users, attributes, load, freshness, availability window, cost boundary, approved controls, population definition, and verification evidence. “Lakehouse” is a solution preference unless supported as a genuine constraint.

### Exercise D — Quality review

Use the checklist in Section 6.1 to review at least twelve requirements. Record defects, severity, correction, owner, and status. Include at least one defect each for ambiguity, atomicity, testability, consistency, feasibility, necessity, and traceability.

### Exercise E — Conflict and dependency analysis

Document these conflicts/dependencies:

1. Broad analyst access versus row-level/attribute-level restriction of sensitive data.
2. Low latency versus waiting for strict validation or complete source data.
3. Low cost versus high availability and recovery expectations.
4. A freshness target that depends on a source currently delivering batch files.

For each, record affected requirement IDs, interests, evidence needed, options, decision authority, temporary treatment, and revalidation trigger.

### Exercise F — Change impact

Assume (illustratively) that a new regulator-driven requirement arrives late and requires a specific lineage evidence field. Do not invent the actual regulatory wording. Treat the content as a placeholder pending authoritative confirmation. Trace the potential change to affected data requirements, functional behaviours, auditability NFRs, acceptance tests, data contracts, and architecture decisions. Identify which items are confirmed impacts and which are hypotheses to validate.

## 8. Practical scenarios and case-based reasoning

### 8.1 Scenario: “The platform must be highly available.”

Produce three candidate measurable versions. These are examples of different business needs, not universal targets.

| Candidate | Illustrative statement | Questions required before approval |
|---|---|---|
| A — Scheduled reporting | The daily risk report shall be available by the approved business deadline on at least the approved percentage of business days over a rolling quarter. | What is the deadline, eligible calendar, success definition, and acceptable late-day rate? Is the data complete at publication? |
| B — Interactive analytics | The query service shall successfully complete at least the approved percentage of eligible requests during the defined service window, measured by the agreed monitoring source. | Which requests count? What latency makes a request successful? Are planned maintenance and dependency failures excluded? |
| C — Fraud case workflow | The fraud case data capability shall meet an approved availability target over the agreed operational window and recover from the defined failure scenarios within the approved recovery time and data-loss tolerance. | Which user journeys are critical? What recovery time and point are acceptable? What failover and degraded modes count as available? |

Choose among them by identifying the actual business capability, impact of interruption, operational hours, dependencies, measurement boundary, and recovery expectations. Do not copy a target from another system without validating the need.

### 8.2 Scenario: sensitive-data restrictions versus broad access

Do not start by selecting a tool. First separate the statements into needs and controls, identify their owners, and clarify what “all customer attributes” means. Determine which analytical tasks require which attributes, whether derived or masked data would satisfy them, and which restrictions are binding. Ask the designated control owner to confirm the approved access policy. Then compare options and document the decision and residual risk. If authority or evidence is missing, keep the requirement unresolved and make dependent decisions conditional.

### 8.3 Scenario: a regulator-driven requirement arrives late

Request the authoritative wording, applicability, scope, effective date, evidence expectations, and accountable interpretation owner. Do not infer legal duties from a paraphrase. Create a proposed requirement with source and status; identify affected objectives, requirements, controls, data flows, lineage fields, retention, access, tests, and architecture decisions using traceability. Assess delivery, cost, feasibility, and risk impacts. Obtain the required decision, update versions, and revalidate affected acceptance criteria. If applicability is unresolved, record the uncertainty and avoid claiming compliance.

### 8.4 Scenario: the customer count differs between risk and finance

Treat the counts as evidence of potentially different definitions, populations, or data quality—not immediate proof that one team is wrong. Compare reporting date, inclusion/exclusion rules, legal/customer identity semantics, account relationships, duplicate handling, source authority, and treatment of inactive or linked records. Obtain example records and calculations. Ask each business owner to explain the intended decision and the population needed. Define the shared measure only where there is agreement; if legitimate use cases differ, document separate named measures and their semantics rather than forcing a false single number. Establish a reconciliation criterion and a decision owner.

### 8.5 Scenario: a target is impossible under a known source constraint

Suppose an agreed business request appears to require freshness faster than the source can currently emit data. First verify the source cadence and whether it is fixed or merely current behaviour. Then clarify the business harm caused by delay and whether the target is a hard need or a preference. Options might include changing source capability, using a different source event, accepting a different target, or providing an interim path. Quantify consequences and ask the appropriate decision authority to accept a trade-off. Do not write an impossible target as if the implementation team can solve it without changing any constraints.

### 8.6 Scenario: requirement has a number but is still not testable

“The customer count shall be accurate to 99%” is incomplete. “Accurate” needs a reference population and comparison rule; the denominator and exception handling must be specified; the reporting date and scope must be known; and an accountable owner must approve the acceptance threshold. A numeric value does not compensate for an undefined measurement method.

## 9. Expected outputs and deliverables

The roadmap expects four core outputs: a requirements register with classification, priority, source, and acceptance criteria; a first traceability matrix; a defect review of a flawed requirements set; and corrected answers to Topic 2 practice questions. The following templates support those outputs.

### 9.1 Reusable requirements register template

Copy this table into a project document. Use one requirement per row; split requirements that need independent acceptance decisions.

| Field | What to record |
|---|---|
| Requirement ID | Stable identifier such as FR-01 or NFR-01. |
| Version / status | Version and draft, proposed, approved, superseded, or deferred. |
| Requirement statement | One clear obligation with scope and conditions. |
| Classification | Business, system/data, functional, non-functional, data, or constraint. Note linked types if useful. |
| Quality attribute | For NFRs: performance, availability, privacy, etc. |
| Business objective | Objective supported by the requirement. |
| Source / evidence | Stakeholder, document, observed process, baseline, or confirmed policy; distinguish source from interpretation. |
| Owner / decision authority | Who owns the requirement and who can approve changes. |
| Priority / rationale | Must/Should/Could/Out of scope, criteria, and decision-maker. |
| Scope / conditions | Population, workload, user roles, time window, and exclusions. |
| Metric / target | Metric, unit, threshold, tolerance, window, and measurement boundary; mark unresolved values explicitly. |
| Acceptance criteria | Pass/fail condition and scenario or data set. |
| Verification method | Test, inspection, reconciliation, monitoring, or other evidence. |
| Accepting role | Role accountable for accepting evidence. |
| Dependencies / conflicts | Related IDs and unresolved interactions. |
| Traceability links | Objective, acceptance criteria, and downstream design/decision IDs. |
| Open questions / assumptions | Unknowns and illustrative assumptions, each with owner and due date if known. |
| Change history | What changed, why, who approved it, and impacted artefacts. |

**Blank starter rows:**

| ID | Type | Requirement | Source / objective | Priority | Acceptance / verification | Owner | Open questions / dependencies | Status/version |
|---|---|---|---|---|---|---|---|---|
| FR-01 |  |  |  |  |  |  |  | Draft v0.1 |
| NFR-01 |  |  |  |  |  |  |  | Draft v0.1 |
| DR-01 |  |  |  |  |  |  |  | Draft v0.1 |
| C-01 |  |  |  |  |  |  |  | Draft v0.1 |

### 9.2 Reusable requirement traceability matrix

| Business objective ID / statement | Source | Requirement ID | Acceptance criterion ID | Verification evidence | Architecture decision / artefact | Status / gap |
|---|---|---|---|---|---|---|
| BO-01: Reconcile the agreed customer population | Risk and finance business owners; confirm exact sources | FR-02, NFR-03 | AC-FR-02a, AC-NFR-03a | Matching-rule tests and population reconciliation | Pending: authoritative customer record approach | Population definition and tolerance unresolved |
| BO-02: Improve timely fraud investigation | Fraud operations; validate target | FR-05, NFR-01, NFR-02 | AC-FR-05a, AC-NFR-01a, AC-NFR-02a | End-to-end timestamp test and availability evidence | Pending: freshness-path option comparison | Target and source capability unresolved |
| BO-03: Provide lineage/accountability evidence | Compliance/control owner; authoritative requirement to be confirmed | FR-03, NFR-05 | AC-FR-03a, AC-NFR-05a | Sample-record lineage retrieval and control review | Pending: lineage evidence approach | Required fields and evidence-retention rules unresolved |

This completed matrix is illustrative. IDs and acceptance IDs must match the final register in a real pack. “Pending” is an honest status, not a missing answer to be silently filled in.

### 9.3 Acceptance record template

```markdown
## Acceptance record
- Requirement ID and version:
- Acceptance criterion ID:
- Test scenario / sample / workload:
- Preconditions and environment:
- Expected result:
- Observed result and evidence location:
- Pass/fail and rationale:
- Exceptions or limitations:
- Verified by:
- Accepted/rejected by (role):
- Date:
- Follow-up action / issue ID:
```

### 9.4 Defect-review template

| Requirement ID / text | Defect category | Severity | Evidence / reason | Correction or question | Owner | Status |
|---|---|---|---|---|---|---|
|  | Ambiguous / non-atomic / untestable / inconsistent / infeasible / unnecessary / untraceable |  |  |  |  | Open |

Suggested severity meanings: **Critical** means a material contradiction or missing definition blocks a safe/valid decision; **Major** means a requirement cannot be accepted or could drive a materially wrong design; **Minor** means clarity or traceability is weakened but the current decision is not blocked. Agree severity definitions with the reviewer; this is a practical template, not a mandated standard.

### 9.5 Conflict and dependency record

| Field | What to record |
|---|---|
| IDs and statements | Conflicting or dependent requirements, using exact versions. |
| Business interests | What each stakeholder is trying to achieve or protect. |
| Evidence needed | Baselines, policy, test, source capability, or cost evidence. |
| Options | Feasible approaches and consequences; avoid straw-man alternatives. |
| Decision authority | Confirmed accountable role/forum. |
| Interim treatment | Whether dependent design is paused, conditional, or allowed with a documented assumption. |
| Decision and rationale | Accepted option, trade-off, residual risk, and rejected options. |
| Revalidation trigger | Event or new evidence that should reopen the requirement or decision. |

### 9.6 Validation session checklist

- [ ] Confirm the business objective and the problem being solved.
- [ ] Review each requirement's source, scope, category, priority, and wording.
- [ ] Read the acceptance criterion and ask how a test would pass or fail.
- [ ] Confirm metric, unit, target, measurement boundary, workload, time window, and exclusions where relevant.
- [ ] Review lifecycle completeness and relevant quality attributes.
- [ ] Identify contradictions, dependencies, unresolved assumptions, and out-of-scope items.
- [ ] Confirm decision rights and accepting roles.
- [ ] Record objections and changes; do not treat silence as approval.
- [ ] Record approver, version, date, conditions, and follow-up owners.

## 10. Common mistakes and misconceptions

1. **Mixing functional and non-functional requirements in one sentence.** Split independent behaviours and quality targets so each has a clear acceptance decision; link them through traceability.
2. **Writing a solution as the requirement.** “Use Kafka,” “use a lakehouse,” or “use vendor X” narrows options prematurely unless a verified constraint requires it.
3. **Using adjectives instead of metrics.** “Fast,” “secure,” and “scalable” should trigger clarification, not be accepted as final targets.
4. **Marking everything Must.** Priorities lose meaning when there is no trade-off. State criteria and record who decides.
5. **Treating acceptance criteria as optional.** Without them, acceptance becomes subjective and disputes emerge late.
6. **Ignoring requirement interactions.** Requirements may conflict or depend on source capabilities, access policies, completeness, cost, and availability.
7. **Confusing availability, reliability, correctness, and freshness.** A service can be available but serve stale or incorrect data; measure each needed quality separately.
8. **Treating a numeric target as automatically measurable.** A number without a population, unit, measurement point, workload, window, or source may remain ambiguous.
9. **Overloading a requirement.** “Ingest, validate, secure, transform, and publish everything quickly” combines independent obligations and makes diagnosis difficult.
10. **Assuming a stakeholder statement is authoritative.** Capture its source and status; verify binding constraints with their accountable owner.
11. **Treating current implementation as a permanent constraint.** Verify whether a source limitation is fixed, negotiable, or simply the current state.
12. **Assuming two departments must have one identical metric.** They may need different populations for legitimate purposes; define common semantics only where appropriate and approved.
13. **Treating silence as sign-off.** Record who validated which version and when.
14. **Ignoring change impact.** A changed target can invalidate acceptance tests and architecture decisions; version, trace, and revalidate.
15. **Claiming regulatory compliance from a vague statement.** Obtain the authoritative requirement and accountable interpretation; do not invent legal obligations.
16. **Confusing traceability with correctness.** Links make the reasoning inspectable; they do not prove that a requirement or target is valid.
17. **Hiding assumptions in prose.** Label assumptions, confidence, source, and validation owner. Keep unresolved values visibly unresolved.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on memorised definitions alone:

- Classify business, system/data, functional, non-functional, data, and constraint statements consistently and explain the distinction.
- Write requirements that are measurable, testable, sourced, prioritised, and linked to business objectives.
- Define acceptance criteria with a pass/fail condition, test scenario/evidence, verification method, and accepting role.
- Identify ambiguity, non-atomic statements, contradictions, infeasibility, unnecessary solution choices, and missing traceability.
- Identify requirement conflicts and dependencies, frame them by business interests and evidence, and propose a legitimate decision path.
- Explain which requirements are architecturally significant and why, without prematurely choosing technologies.
- Handle changing requirements through versioning, impact analysis, and revalidation.
- Produce the requirements register, first traceability matrix, and defect review for the Northbridge customer-data scenario.

### Readiness checks by level

| Transition | Required demonstration |
|---|---|
| Beginner → Intermediate | Correctly classify at least 90% of the twenty exercise statements without notes and explain what is missing from each vague statement. This threshold follows the module's general level-transition rule. |
| Intermediate → Advanced | Produce a sourced requirement set with units/conditions where applicable and acceptance criteria; a reviewer finds no unmeasurable “must” statement without an explicit justification. |
| Advanced → Industry application | Defend one recommendation against at least two reviewer challenges using criteria, evidence, uncertainty, and sensitivity; explain what evidence could change the recommendation. |

The aim is defensible reasoning, not a perfect-looking table. A strong answer can explicitly state that a target is unresolved, explain why, name who must decide, and prevent the unresolved point from being mistaken for an approved requirement.

## 12. Completion gate

Do not mark this lesson complete until every applicable item below has been reviewed. If an item cannot be completed because an authoritative target or source is unavailable, record the gap, owner, and evidence needed rather than fabricating an answer.

- [ ] **Classification:** I can classify business, system/data, functional, non-functional, data, and constraint statements and explain the distinction.
- [ ] **Twenty-statement exercise:** I classified all twenty statements and marked measurability; I corrected errors and can explain why each vague statement is incomplete.
- [ ] **Requirement set:** I produced six functional and six non-functional requirements for the Northbridge customer-data problem, each with source, priority, acceptance criteria, and verification method. Unresolved targets are explicitly labelled.
- [ ] **Quality review:** I checked the set for ambiguity, atomicity, testability, consistency, feasibility, necessity, and traceability, and reviewed lifecycle/quality-attribute completeness.
- [ ] **Traceability:** I created the first matrix linking business objective → requirement → acceptance criterion and identified downstream architecture decision links or marked them pending.
- [ ] **Vague-word hunt:** I reviewed the supplied paragraph, identified vague words and solution preferences, and wrote clarification questions.
- [ ] **Conflicts and dependencies:** I documented privacy/access, latency/completeness, cost/availability, and source-capability interactions with evidence needs and decision authority.
- [ ] **Change impact:** I assessed a late-arriving regulator-driven requirement without inventing its content and identified affected requirements, tests, and decisions.
- [ ] **Defect review:** I reviewed the flawed set, recorded defect categories and severity, corrected material defects, and identified architecturally significant requirements.
- [ ] **Practice questions:** I answered the Topic 2 practice questions available in the repository or prepared answers to the roadmap-prescribed exercises if the practice-question file is empty; I corrected my answers after review.
- [ ] **Reviewer challenge:** I defended a recommendation against two challenges and stated what evidence could reverse it.
- [ ] **Final register review:** Every register entry has type, priority, source, and acceptance criterion. No “must” requirement is unmeasurable without an explicit justification.
- [ ] **Version and approval:** The requirement baseline identifies its version/status, owners, approval decisions, and open questions.

**Completion decision:** the lesson is complete when the requirements register, traceability matrix, and defect review are reviewable; all material defects are resolved or explicitly blocked by an owned open question; and the reviewer agrees that the evidence supports the conclusions. Do not proceed by treating unresolved assumptions as facts.

---

**Source alignment note:** This lesson follows the topic-specific roadmap's scope, 12-section order, Northbridge scenario, exercises, deliverables, mastery criteria, and completion gate. The roadmap states that the module's lesson files, `practice-questions.md`, module/project READMEs, and project file are empty; this lesson therefore does not claim to reproduce material from those files. All additional numeric targets and role assignments in examples are explicitly illustrative or unresolved.
