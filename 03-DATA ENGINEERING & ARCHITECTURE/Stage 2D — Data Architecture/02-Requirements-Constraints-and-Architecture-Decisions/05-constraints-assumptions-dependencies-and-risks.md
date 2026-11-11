# 05 — Constraints, Assumptions, Dependencies and Risks

> **Scope and source note.** This lesson follows Module 5 of `roadmap-Requirements-Constraints-and-Architecture-Decisions.md`. The roadmap identifies the target topic file, module `practice-questions.md`, module/project READMEs, and `Projects/02-requirements-and-architecture-decision-pack.md` as existing but empty. Their missing contents are not treated as source material here. The topic-specific roadmap is therefore the authority for this lesson's scope and learning sequence. Northbridge Bank and all scenario details and numerical values below are illustrative teaching assumptions, not facts about a real organisation or statements of legal requirements.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Distinguish **facts, constraints, preferences, assumptions, dependencies, risks, and unknowns** using a repeatable test rather than intuition.
2. Identify technical, business, organisational, regulatory, operational, financial, and time constraints that shape a data architecture.
3. Decide whether a stated constraint is genuinely fixed, negotiable, or merely believed to be fixed—and record who has authority to change it.
4. Document assumptions with a clear statement, source, owner, evidence, confidence, validation method, due date, and consequence if wrong.
5. Map internal and external dependencies, their owners, sequencing, upstream/downstream relationships, critical path, and failure consequences.
6. Assess risks using stated probability and impact scales; prioritise them without implying more numerical precision than the evidence supports.
7. Select proportionate responses—avoid, mitigate, transfer, or accept—and record owners, triggers, contingency actions, and escalation paths.
8. Distinguish information that is unknown from information that cannot yet be known; represent uncertainty using evidence labels, ranges, conditions, and decision triggers.
9. Trace constraints, assumptions, dependencies, risks, and unresolved questions to requirements, decision criteria, architecture decision records (ADRs), and follow-up actions.
10. Reassess architecture decisions when an assumption fails, a dependency changes, new evidence appears, or a constraint is formally relaxed.

**Evidence of learning:** you can produce an auditable register and dependency map for the Northbridge scenario, explain the classification test for each item, and show which decisions must be revisited if important inputs change.

## 2. Why the topic matters in real-world Data Architecture

Architecture is not designed in a vacuum. It is bounded by things the organisation must obey, things it believes to be true, services and teams it relies on, and uncertain events that could undermine its objectives. A design may be technically elegant and still fail because a source cannot provide the required data, a delivery date is immovable, a budget is insufficient, a policy was misunderstood, or a key assumption was never validated.

This topic makes the boundaries and uncertainty visible **before** alternatives are ranked. That matters because later architecture trade-off analysis (Topic 6) should compare only feasible options, and ADRs (Topic 7) should preserve the evidence and conditions behind a choice.

### 2.1 The cost of misclassification

- **Assumption treated as fact:** the design is built around an unverified source capability; when the capability is absent, integration and delivery plans must be redesigned.
- **Preference treated as constraint:** viable options are eliminated unnecessarily, potentially increasing cost or lock-in.
- **Real constraint treated as preference:** an option is selected that cannot be approved, operated, funded, or delivered.
- **Dependency left invisible:** a plan assumes another team or vendor will deliver on time without an agreed interface, owner, or commitment.
- **Risk recorded without action:** the register creates an appearance of governance but does not change exposure.
- **Unknown silently filled with a guess:** reviewers cannot tell what is evidenced and what must still be tested.

### 2.2 The working chain

```text
Stakeholder need / requirement
        ↓
Evidence and classification
        ↓
Constraints + assumptions + dependencies + risks + unknowns
        ↓
Feasibility gates and decision criteria (Topic 6)
        ↓
Alternative comparison and architecture decision (Topic 7 ADR)
        ↓
Validation actions, triggers, monitoring, and change control
```

The chain must work in both directions. A requirement should be traceable to the business need; a decision should link back to the requirements and boundaries that justify it; a changed constraint or failed assumption should identify the decisions and deliverables that need review.

### 2.3 Shared Northbridge Bank scenario

Northbridge Bank is a fictional mid-sized retail and business bank. It has a core banking system, a separate cards platform, a CRM, and a loan origination system. Nightly extracts feed an enterprise data warehouse, and a data lake contains copies of some source data. Risk, finance, marketing, and compliance teams report different customer counts. Fraud analysts see card transactions hours after the event. A regulator has requested clearer evidence of lineage and customer-data accountability within a stated period.

For this lesson, the roadmap's initial scenario values remain **illustrative assumptions**: approximately 3 million retail customers; approximately 2 million card transactions per day on average; card-platform batch files every 15 minutes today; seven-year transaction retention; and a programme budget ceiling set by the sponsor. The scenario also lists illustrative constraints: personal data must remain in a stated jurisdiction, the core banking batch window ends at 02:30, and an existing platform or service may be preferred. Do not infer a particular jurisdiction, statute, retention law, budget amount, or regulatory deadline from this fictional description. Confirm those with authorised stakeholders and evidence in a real project.

The architecture problem is to choose a defensible high-level approach for consolidating customer and transaction data so risk, finance, compliance, and fraud teams can work from a consistent, timely, governed view. Detailed schemas, implementation, vendor selection, and migration plans belong to later work and are outside this lesson's decision scope.

## 3. Prerequisite concepts

The roadmap expects Modules 1–4 in this folder and Stage 2D.1 Topic 4 (business drivers, constraints, assumptions) and Topic 5 (exceptions). You should be comfortable with the following:

- **Business need and requirement:** the outcome stakeholders need, expressed as a statement that can be validated.
- **Functional and non-functional requirements:** what the solution must do and the quality/service characteristics it must meet.
- **Estimates and evidence labels:** measured, sampled, stated, estimated, or guessed inputs, with units and confidence.
- **Service targets:** a scoped indicator, target, time window, and measurement method—not an undefined adjective such as “real-time.”
- **Architecture principle and quality attribute:** a guide or desired system property that influences, but does not automatically settle, a decision.
- **ADR and decision traceability:** a record of context, alternatives, decision, rationale, consequences, and revisit conditions.
- **Ownership and governance:** who supplies evidence, who can approve a change, who operates a service, and who accepts residual risk.

### 3.1 A practical rule before you classify

Record the statement as it was said, who said it, when, and in what context. Then separate the **claim** from your **interpretation**. For example:

- Original claim: “The cards API will be ready next quarter.”
- Interpretation: “An external delivery date has been stated, but it is not yet a confirmed commitment.”
- Follow-up: obtain the vendor's written commitment, interface specification, test environment date, and service conditions; until then, treat the date as an unverified dependency and potential risk.

Never silently upgrade a stakeholder statement, vendor forecast, policy summary, or estimate into a verified fact.

## 4. Beginner-level learning sequence

### 4.1 Seven categories and the one-line classification test

| Category | Definition | Test to apply | Typical treatment |
|---|---|---|---|
| **Fact (FACT)** | A claim supported by evidence that can be inspected or independently checked. | What evidence demonstrates it, and is that evidence current and relevant? | Record source, date, scope, and evidence location. Revalidate if the fact can change. |
| **Constraint (CON)** | A limit the solution must respect within the agreed decision scope. | What authority or evidence makes it mandatory, and who can change it? | Record rationale, authority, scope, flexibility, and consequence of violation. |
| **Preference (PREF)** | A desired outcome or option that can be traded off. | Who wants it, and what cost or approval would make it negotiable? | Record the preference, sponsor, priority, and acceptable alternatives. Do not use it as a hard gate unless authorised. |
| **Assumption (ASM)** | A proposition temporarily treated as true despite incomplete verification. | What are we relying on without adequate evidence? | Assign owner, confidence, validation method/date, impact if wrong, and fallback. |
| **Dependency (DEP)** | A capability, decision, input, service, event, or delivery the solution relies on but does not fully control. | What must another party/system/team provide, and when or under what conditions? | Map producer/consumer, owner, interface, timing, sequence, failure mode, and contingency. |
| **Risk (RSK)** | An uncertain event or condition that could affect objectives. | What might happen, why, and what would be the consequence? | State cause–event–effect, assess likelihood and impact, assign response/owner/trigger. |
| **Unknown (UNK)** | Information not currently available or not yet resolved. | What specific question remains unanswered, and what decision depends on it? | Name the question, owner, evidence needed, due date, and whether it blocks a decision. |

These categories are related but not interchangeable. A dependency can be dependable today and still create risk if it becomes late. An assumption can concern a dependency. A constraint may create a risk if it conflicts with a target. An unknown is not automatically a risk; it becomes risk-relevant when the missing information could affect objectives or decisions.

### 4.2 Facts require evidence, not confidence alone

Confidence describes how strongly you believe a statement; it does not prove the statement. A stakeholder saying “I am certain” is evidence that the stakeholder holds that view, not necessarily evidence that the technical claim is true.

Useful evidence labels for estimates and claims include:

- **Measured:** observed using a defined method over a stated period.
- **Sampled:** observed from a sample; representativeness and sample limits are documented.
- **Stated:** asserted by a named stakeholder or supplier, but not independently verified.
- **Estimated:** derived from a model or calculation; inputs and formula are available.
- **Guessed:** an initial placeholder with little supporting evidence; it must not silently become a baseline.
- **Unknown:** no defensible value or answer is currently available.

Evidence quality is contextual. A dated screenshot may prove what a screen displayed at a moment, but not prove a service's long-term availability. A policy document may prove a stated policy exists, but the policy owner may still need to confirm whether it applies to the proposed data flow.

### 4.3 Constraint or preference? Test the authority and flexibility

Ask these questions in order:

1. **Who owns the rule?** Identify the person, policy, contract, board decision, or technical boundary behind the statement.
2. **What is the evidence?** Request the approved policy, contract, measured system limit, signed budget, or documented decision.
3. **Who can change it?** A delivery team cannot waive a legal obligation or another team's service contract merely because it is inconvenient.
4. **What is the change cost and lead time?** A preference may be changeable only with cost, delay, migration, or governance approval.
5. **Is it fixed for this decision, or fixed forever?** Many constraints are hard within the current programme but can be changed through a separate approval path.
6. **What happens if we violate it?** If the consequence is not understood, the classification is not yet sufficiently evidenced.

Example: “We will use the existing identity provider.” If an approved enterprise standard mandates it and the security authority confirms the scope, treat it as a constraint for this decision. If a product team merely prefers it, classify it as a preference. If the team believes it is mandatory but cannot locate the policy or decision owner, record an unresolved question and a provisional assumption—not a verified constraint.

### 4.4 Constraint categories

| Category | Typical example | Evidence to request | Architectural consequence if real |
|---|---|---|---|
| Technical | A source exports only fixed-width files; a legacy database permits a limited extraction window. | Interface documentation, system-owner confirmation, measured limits, test results. | May constrain ingestion method, sequencing, capacity, or recovery design. |
| Business | A risk report must be available before a defined business process starts. | Approved business requirement and acceptance owner. | Shapes service targets and workload prioritisation. |
| Organisational | Only one team can approve source changes; a platform team owns deployment. | RACI, operating model, decision-rights record. | Adds hand-offs, lead time, and ownership boundaries. |
| Regulatory / policy | Personal data must stay within a defined jurisdiction under an applicable, approved rule. | Authoritative legal/compliance interpretation, policy, scope, and data classification. | May eliminate some hosting, replication, access, or support options. Do not invent the rule. |
| Operational | A production source is unavailable for extraction during a critical processing window. | Runbook, schedule, operational owner, observed history. | Constrains ingestion schedule, retry, recovery, and maintenance design. |
| Financial | A sponsor-approved funding ceiling limits programme spend. | Approved budget, scope, currency, time horizon, included costs, and change authority. | May require phased delivery, simpler options, or an explicit scope trade-off. |
| Time | An externally committed milestone is fixed for the current programme. | Approved plan, contract, sponsor decision, dependency dates. | Changes sequencing and may make some alternatives infeasible. |

A category label is not enough. Record the exact statement, source, scope, owner, status, and whether it is fixed or negotiable. A financial “ceiling” without a defined amount or scope is an unresolved item, not a usable numerical gate.

### 4.5 Worked classification examples

| Statement | Initial classification | Why | Next action |
|---|---|---|---|
| “The production database is PostgreSQL 16,” confirmed by a current inventory export. | FACT | Inspectable, scoped evidence exists. | Record inventory location and date; verify version drift before implementation. |
| “Personal data must remain in the approved production jurisdiction,” confirmed by the authorised policy owner. | CON | An authorised rule limits deployment/data movement. | Record the exact jurisdiction, data classes, exceptions process, and approver. |
| “The team would prefer to retain the current warehouse.” | PREF | “Prefer” signals a desired option, not a mandatory rule. | Ask why, rank the preference, and define when another option is acceptable. |
| “The cards platform will support CDC next quarter,” with no written commitment. | ASM + DEP + UNK | The design relies on an unverified external capability and date; the exact delivery state is unknown. | Ask the platform owner/vendor for capability evidence and a committed delivery plan. Track risk if timing matters. |
| “The consolidation programme cannot exceed the approved budget.” | CON, if approved evidence exists | A formal budget ceiling can be a decision boundary. | Verify amount, included costs, time horizon, and who can authorise a change. |
| “The API may be unavailable during month-end close.” | RSK, until verified; possibly an UNK | A potential event and consequence are described, but the actual operating rule is unconfirmed. | Check runbooks and incident history; define failure handling if confirmed. |
| “We do not know whether the source contains a stable customer identifier.” | UNK | The answer is missing. | Assign a data owner, inspect sample data and source documentation, and set a due date. |
| “The source team must approve schema changes.” | CON or DEP, depending on wording/evidence | It may be a governance constraint; approval turnaround is also a dependency. | Verify the change policy, owner, expected lead time, and escalation route. |

The classifications above are provisional when the stated evidence is absent. A statement may legitimately carry more than one relationship: for example, “the vendor API must be delivered by date X” can be a dependency with a date constraint, while late delivery is a risk. Keep each record's primary class clear and link related records instead of forcing all concerns into one label.

### 4.6 Beginner exercise: classify twenty statements

Classify each statement as FACT, CON, PREF, ASM, DEP, RSK, or UNK. Some statements intentionally require a conditional answer: explain what evidence would settle the classification.

1. A current inventory shows that the CRM exports customer records as CSV.
2. “We should use the lakehouse because it is modern.”
3. An approved policy prohibits copying a specified class of personal data outside a named jurisdiction.
4. The architect believes the source will provide a stable customer ID, but no sample or contract has been reviewed.
5. The data pipeline needs the source team's extract before it can begin transformation.
6. The vendor may miss the integration date, delaying the regulatory evidence pack.
7. Nobody has confirmed whether historical account closures are included in the extract.
8. The sponsor has approved a budget ceiling and recorded its scope.
9. “The dashboard should be as fast as possible.”
10. The source owner confirms that a nightly batch finishes by 02:30, based on the runbook and recent runs.
11. The programme assumes two additional engineers will be assigned next month; staffing is not approved.
12. A downstream reporting team must publish its reconciled output before finance can sign off.
13. The organisation prefers a single cloud provider, but the preference may be waived.
14. A source schema change could silently break a parser and corrupt downstream records.
15. The regulator's exact requested evidence date has not been confirmed by compliance.
16. A signed vendor contract specifies an API support window.
17. “We have always kept seven years of transactions.” No policy, contract, or owner has confirmed the reason.
18. The source system will be read-only during a planned upgrade window, according to an approved operations calendar.
19. It is unclear who can accept residual risk for a failed lineage control.
20. A batch-only source cannot provide a record before its next scheduled export, confirmed by a technical test.

**Answer guidance**

| # | Suggested classification | Reason / qualification |
|---:|---|---|
| 1 | FACT | Current inventory is evidence; record its date and scope. |
| 2 | PREF (or unsupported recommendation) | “Modern” is not a requirement or evidence of suitability. Ask for the business reason. |
| 3 | CON | Authorised policy plus defined scope. Do not generalise beyond the policy. |
| 4 | ASM | Belief relied upon without validation. |
| 5 | DEP | Transformation depends on an upstream deliverable. Record owner, timing, and interface. |
| 6 | RSK linked to DEP | The uncertain late-delivery event may affect the milestone. |
| 7 | UNK | Specific unresolved data-scope question. |
| 8 | CON | Provided the approval and scope are authentic and current. |
| 9 | PREF / incomplete requirement | It must be quantified and prioritised before it can become an acceptance target. |
| 10 | FACT and operational constraint | The runbook and recent evidence support the timing; treat the window as a constraint if the architecture must respect it. |
| 11 | ASM + staffing dependency | Assignment is not approved; validate with the resource owner. |
| 12 | DEP | A downstream business process depends on a producer's output. |
| 13 | PREF | The stated ability to waive it means it is not automatically a hard gate. |
| 14 | RSK | Cause–event–effect is plausible; assess likelihood and impact using evidence. |
| 15 | UNK | Confirm with the authorised compliance contact; do not invent a date. |
| 16 | FACT about the contract; possible CON for this design | Inspect the contract and determine whether the support window actually limits the proposed service. |
| 17 | UNK + possible ASM | Past practice does not establish the current legal, business, or policy reason. Verify before treating it as a retention constraint. |
| 18 | FACT and operational constraint | Approved calendar supports a known restriction during the specified window. |
| 19 | UNK / governance gap, potentially a risk | Identify risk-acceptance authority; do not assign acceptance to the architect by default. |
| 20 | FACT and technical constraint | Test evidence supports a source capability boundary. Record whether the boundary is fixed or can be changed at acceptable cost. |

**Self-check:** aim to classify at least 18 of 20 correctly without notes, and explain the evidence and next action for every ambiguous item. The wider module's general learning progression uses 90% correct classification as the beginner-to-intermediate threshold.

## 5. Intermediate-level learning sequence

### 5.1 Build a usable register—not just a list

A register is an operational control, not a glossary. Each record should tell a reviewer what is claimed, why it matters, who is accountable, what evidence exists, what must happen next, and which decisions depend on it.

Use stable IDs:

- `CON-001` — constraint
- `ASM-001` — assumption
- `DEP-001` — dependency
- `RSK-001` — risk
- `UNK-001` — unresolved question
- `FACT-001` — evidenced fact (optional but useful)
- `PREF-001` — preference (optional but useful)

The roadmap's minimum combined-register classes are `CON / ASM / DEP / RSK / UNK`. Facts and preferences may be recorded in the same register or linked source artefacts, as long as they remain visible and traceable. Do not use an ID prefix as a substitute for correct classification.

### 5.2 Reusable constraints register

| Field | What to record | Quality test |
|---|---|---|
| ID / statement | One precise, bounded constraint | Can a reviewer tell what is and is not prohibited? |
| Category | Technical, business, organisational, regulatory/policy, operational, financial, or time | Category is useful and supported; it is not the justification. |
| Source / evidence | Policy, contract, approved decision, system test, runbook, or stakeholder confirmation | Source is accessible, current, and in scope. |
| Authority / owner | Person or role that owns the rule and can clarify it | The owner has authority or can identify the authority. |
| Status | Proposed, verified, challenged, relaxed, superseded | Status reflects evidence, not preference. |
| Fixed for this decision? | Yes / no / conditional, with reason | A “yes” has an authority and a change path. |
| Change route / cost / lead time | Who can change it, required approval, likely impact | A negotiable item has a realistic change path. |
| Consequence if violated | Delivery, control, cost, service, or operational impact | Consequence is explicit and not exaggerated. |
| Linked IDs | Requirements, assumptions, dependencies, risks, criteria, ADRs | Impact analysis can follow the links. |
| Review trigger / date | Policy change, source change, programme gate, or periodic review | The constraint will not become invisible after initial approval. |

**Example (illustrative):**

| ID | Statement | Evidence / owner | Flexibility | Consequence / links |
|---|---|---|---|---|
| CON-001 | Personal data for the defined scope must remain within the approved jurisdiction. | Compliance-approved policy to be attached; compliance owner to confirm exact scope. Until evidence is attached, status is **provisional**, not verified. | Treat as a gate only after authorised confirmation; record approved exception path if one exists. | Could eliminate some hosting/replication options. Links: REQ-data-protection, UNK-001, ADR-001. |
| CON-002 | Core banking extraction must respect the 02:30 batch-window boundary. | Scenario runbook/operations owner; illustrative. | May be changed only if source operations approve a new window. | Constrains sequencing and recovery; links: DEP-001, RSK-001, ADR-002. |
| CON-003 | Programme spend must remain within the sponsor-approved ceiling. | Approved funding record and sponsor; amount not supplied in this scenario. | Sponsor-controlled change route. | Option feasibility cannot be determined until the ceiling and cost scope are known; links: UNK-002, CRIT-cost, ADR-001. |

The first example intentionally distinguishes the scenario's illustrative policy statement from a verified policy artefact. A real project must attach the actual authorised evidence before marking it confirmed.

### 5.3 Reusable assumption register

| Field | What to record | Quality test |
|---|---|---|
| ID / statement | A proposition relied on but not yet verified | Can it be tested or disproved? |
| Reason for reliance | Why planning currently needs a working proposition | Is it a temporary planning aid, not disguised fact? |
| Source / evidence | Who stated it, what evidence exists, and evidence label | “No evidence yet” is allowed and visible. |
| Owner | One accountable role/person to arrange validation | Owner can access the evidence or obtain it. |
| Confidence | High / medium / low, with brief justification | Confidence is not confused with impact or proof. |
| Impact if wrong | Consequence for scope, targets, cost, feasibility, or decisions | The consequence is specific enough to prioritise. |
| Validation method | Test, sample, interview, contract review, policy confirmation, or calculation | Method can answer the actual proposition. |
| Due date / validation gate | Date or decision milestone by which the result is needed | Date precedes the decision that depends on it. |
| Failure response | Fallback, redesign, change request, pause, or scope change | Action is feasible and authorised. |
| Trigger / linked IDs | Event that reopens the assumption; linked requirements, dependencies, risks, ADRs | A failed assumption can identify affected artefacts. |
| Status / last reviewed | Open, validated, failed, superseded; date | Stale assumptions are visible. |

**Example assumptions (all illustrative):**

| ID | Assumption | Confidence / impact if wrong | Owner and validation | Deadline / consequence if false |
|---|---|---|---|---|
| ASM-001 | The cards platform can supply the required transaction fields through its existing 15-minute batch export. | Medium confidence; high impact because field gaps or a different cadence could invalidate the target. | Cards platform owner; inspect schema, sample files, and production schedule. | Before choosing the ingestion pattern; if false, compare a source change, alternate feed, or revised business target. |
| ASM-002 | The source can provide a stable customer identifier across relevant records. | Low confidence; high impact on entity matching and reconciliation. | Customer data owner; profile samples, confirm semantics, quantify nulls/duplicates, and obtain source-owner sign-off. | Before confirming the consolidation approach; if false, assess matching rules, stewardship, and residual reconciliation risk. |
| ASM-003 | Two additional engineers will be available for delivery. | Low confidence until staffing is approved; medium/high delivery impact. | Engineering manager; obtain approved capacity plan. | Before committing the delivery plan; if false, reduce scope, sequence work, or revise schedule. |
| ASM-004 | Transaction retention is seven years for the defined scope. | Low until the policy and data categories are confirmed; potentially high storage, deletion, and compliance impact. | Records-management and compliance owners; validate authoritative retention schedule by record class and jurisdiction. | Before sizing retention and storage decisions; if false, recalculate capacity and revisit relevant ADRs. |

### 5.4 Validate assumptions by impact and confidence

The roadmap specifically calls for ranking assumptions by **impact if wrong** and **confidence**, then validating high-impact, low-confidence assumptions first. Do not collapse these dimensions into a single unexplained number.

A simple prioritisation table is sufficient:

| Impact if wrong | Confidence | Validation priority | Reason |
|---|---|---|---|
| High | Low | Highest | A weakly supported assumption could invalidate a major decision. |
| High | Medium | High | Consequences are large; evidence still needs strengthening. |
| High | High | Verify the evidence quality | High confidence is not proof; independently check critical inputs. |
| Low | Low | Lower unless it blocks a decision | Uncertainty is tolerable if the downside is limited and reversible. |
| Low | High | Routine review | Keep provenance and revisit only when conditions change. |

**Worked example:** if a proposed architecture depends on stable customer identifiers (high impact, low confidence), validate that before spending time scoring storage platforms. If identifiers are unstable, the options may need to include matching and stewardship capabilities; a ranking that assumed stable identifiers is not valid. By contrast, an unconfirmed dashboard colour preference is low impact and can wait.

### 5.5 Reusable dependency register

A dependency describes something needed from outside the immediate solution boundary. It can be internal or external; “external” means outside the team's control, not necessarily outside the organisation.

| Field | What to record |
|---|---|
| ID / dependency statement | What must be supplied, decided, approved, or available |
| Type / boundary | Upstream data, downstream consumer, platform, team, vendor, policy approval, or business process |
| Provider and accountable owner | Named team/role, not only a system name |
| Consumer and purpose | Which component, requirement, or decision needs it |
| Interface / contract | Data schema, API, file, event, approval, service commitment, or agreed output |
| Timing / sequence | Due date, frequency, lead time, prerequisite, and window |
| Evidence / status | Confirmed, provisional, uncommitted, blocked, failed; link to contract/test/decision |
| Failure mode and consequence | Late, missing, malformed, unavailable, changed, or unapproved; impact on objectives |
| Critical-path status | Whether a delay delays a downstream milestone; explain the sequence |
| Contingency / escalation | Fallback, retry, alternate source, manual process, escalation owner and threshold |
| Related IDs | Requirements, constraints, assumptions, risks, ADRs, and action items |

### 5.6 Dependency map and critical path

A dependency map shows the direction of reliance, not just which systems exist. Draw arrows from prerequisite to dependent work and label the interface or decision. Identify the critical path by finding the chain of dependent activities that determines the earliest possible completion; where durations are not known, mark the path **provisional** rather than inventing durations.

**Illustrative Northbridge map:**

```text
Core banking source ──nightly extract / window──┐
                                                ├─> Ingestion & reconciliation
Cards platform ───────transaction feed──────────┘             │
                                                              v
CRM ───────────────customer attributes──────────────> Customer identity resolution
Loan origination ──loan/customer relationships──────>          │
                                                              v
                                              Governed consolidated customer view
                                                   /           |            \
                                                  v            v             v
                                            Risk reporting  Fraud cases  Finance / compliance
```

Cross-cutting dependencies include the identity/access service, security review, data-owner approvals, platform operations, lineage/metadata capture, and compliance interpretation. These are not necessarily serial data-processing stages; show them as governance or platform dependencies where appropriate.

**Provisional critical-path candidate (sequence, not a committed schedule):**

```text
Customer-identifier profiling and owner confirmation
  → identity-resolution approach can be evaluated
  → reconciliation and acceptance rules can be tested
  → governed consolidated view can be accepted
```

This is a **candidate** chain because the roadmap does not provide task durations, confirmed dates, or complete dependency commitments. It becomes the critical path only after the team validates predecessors, durations, calendars, and milestone dependencies. In parallel, source-feed validation and required security/compliance approvals may be critical-path activities; compare their supported sequences rather than assuming the chain above is definitively longest. Record the accountable owner and evidence due date for each unresolved predecessor.

**Critical-path method:**

1. List the activities required for a decision or milestone.
2. Record predecessor activities and their estimated durations only where evidence supports them.
3. Link each activity to its responsible owner and evidence of commitment.
4. Identify the longest dependent chain; flag uncertain durations and uncommitted dates.
5. Determine which dependency delay would move the milestone and define escalation thresholds.
6. Recalculate when dates, durations, scope, or sequencing change.

**Example:** if the customer identifier profile is required before identity-resolution options can be evaluated, and the data owner has not provided a sample, that activity blocks a defensible decision. The map should show the profile as a predecessor, its owner and due date, and a contingency (for example, use a synthetic/sample dataset only for preliminary exploration, while keeping the final decision conditional).

### 5.7 Dependencies can become risks

A dependency is a relationship; a risk is the uncertain event or condition that may harm an objective. Keep the dependency record and risk record linked.

- **Dependency:** the vendor must provide a tested API before integration testing.
- **Risk:** the vendor may deliver the API late or with missing fields, causing the integration milestone to slip.
- **Constraint:** the regulatory evidence milestone cannot move without sponsor/regulatory agreement.
- **Interaction:** the late API risk becomes more severe because the milestone is fixed.

This is a causal chain, not a reason to label every dependency “high risk.” Assess the probability and impact using evidence, and record which objective is exposed.

### 5.8 Risk statement, scoring, and prioritisation

Write risks in cause–event–effect form:

> Because **[cause or condition]**, **[uncertain event]** may occur, resulting in **[effect on an objective]**.

Weak: “API risk.”

Better: “Because the vendor has not confirmed the transaction API schema or delivery date, the required fields may arrive after integration testing starts, delaying the fraud-use-case acceptance milestone and forcing a redesign of the ingestion path.”

#### Illustrative ordinal scoring method

The roadmap gives the formula `exposure = probability × impact` and recommends ordinal 1–5 scales when precise numbers are unavailable. The scales and thresholds below are a **teaching example, not a mandatory enterprise standard**. Agree the scale with the organisation before using it operationally.

**Probability (P)**

Before assigning P, define the **assessment horizon**: the period or milestone during which the risk event could affect the objective (for example, “from now until integration-readiness sign-off”). Scores from different horizons should not be compared as if they were equivalent. The interpretations below are qualitative anchors, not universal numeric probability bands; the project must document the evidence and rationale for the chosen score.

| Score | Qualitative meaning | Illustrative interpretation within the stated horizon |
|---:|---|---|
| 1 | Rare | Credible but unlikely in this horizon, supported by relevant evidence or effective controls. |
| 2 | Unlikely | Possible but not expected in this horizon under current controls. |
| 3 | Possible | A credible event in this horizon; evidence is mixed, limited, or incomplete. |
| 4 | Likely | Evidence or recent history suggests the event is more likely than not in this horizon. |
| 5 | Almost certain | The event is expected in this horizon unless conditions or controls change. |

For every risk, record the horizon, evidence date/source, existing controls, and the rationale for P. If no defensible likelihood estimate is possible, label the score provisional and state what evidence is needed; do not present an ordinal score as a measured probability.

**Impact (I)** — score against the most relevant agreed objective, not a vague overall impression.

| Score | Qualitative meaning | Illustrative consequence |
|---:|---|---|
| 1 | Negligible | Minor, quickly reversible inconvenience; no material objective affected. |
| 2 | Minor | Local rework or short delay within available contingency. |
| 3 | Moderate | Material team-level rework, missed internal milestone, or degraded service. |
| 4 | Major | Major milestone, key service target, material cost, or control objective at risk. |
| 5 | Severe | Critical business objective or authorised control obligation may fail; executive decision required. |

Calculate **exposure score = P × I**, yielding 1–25. Because P and I are ordinal judgements, the product is a prioritisation aid—not a probability, monetary loss, or scientifically precise risk measure. Record the rationale and evidence behind both ratings.

For this lesson only, use the following illustrative response bands:

- **1–4, lower:** monitor or accept with a named owner where appropriate.
- **5–9, moderate:** define proportionate action and review date.
- **10–14, high:** assign a response, owner, trigger, and explicit decision/acceptance authority.
- **15–25, very high:** escalate promptly to the designated decision authority; do not proceed as though the exposure were accepted unless that authority explicitly decides to do so.

These bands are illustrative. A high-severity regulatory, security, or safety-related concern may require escalation regardless of multiplication result; local policy and authorised control functions take precedence. Do not use a low score to override a mandatory constraint.

### 5.9 Risk responses and escalation

| Response | Meaning | Example in data architecture | Evidence of a real response |
|---|---|---|---|
| **Avoid** | Change the plan so the risk source or exposure is removed. | Do not make the first release depend on an uncommitted vendor feature; select an alternative that meets the must-have gate. | Decision and scope change, plus updated alternative comparison. |
| **Mitigate** | Reduce likelihood and/or impact. | Validate schemas early, add contract tests, monitor feed lag, and test recovery. | Named actions, owners, due dates, evidence, and residual-risk rating. |
| **Transfer / share** | Allocate a defined part of the consequence to another party through an agreement or control. | Contractual service commitments, support obligations, or insurance where appropriate. | Signed terms and a clear statement of what is—and is not—transferred. Accountability for architecture and governance is not magically eliminated. |
| **Accept** | An authorised person knowingly retains the risk. | Accept a limited delay for a non-critical consumer when the business owner confirms the consequence is tolerable. | Named acceptance authority, rationale, duration, monitoring, trigger, and review date. |

**Escalation note template**

```text
Subject: [decision needed] — [risk ID and short title]
Decision deadline: [date / milestone]
Risk statement: Because [cause], [event] may occur, resulting in [effect].
Current evidence: [source, date, evidence label, what remains unverified]
Assessment horizon: [period or milestone]
Assessment: P [1–5] × I [1–5] = [score], using [scale version and evidence rationale].
Affected objectives / IDs: [requirements, constraints, dependencies, ADRs]
Options:
  A. [avoid/mitigate option] — benefit, cost, time, residual risk
  B. [alternative] — benefit, cost, time, residual risk
  C. Accept / defer — explicit consequence and monitoring
Recommendation: [option] because [evidence and decision criteria].
Trigger / contingency: [observable event and action]
Decision required from: [role with authority]
Owner and next review: [name/role, date]
```

Escalate when a threshold is crossed, a critical assumption fails, a dependency misses its agreed date, a mandatory constraint may be violated, residual exposure exceeds the owner's authority, or a decision deadline is threatened. Define these triggers before the event where possible.

### 5.10 Unknowns: decision blockers versus manageable gaps

Not every unknown should stop work. Classify each unresolved question by the decision it affects and the cost of waiting.

- **Blocking unknown:** without the answer, an option cannot be shown to pass a mandatory gate or a high-impact decision could be invalid. Example: the authorised jurisdictional rule is not confirmed before selecting a hosting option.
- **Conditionally manageable unknown:** preliminary work can proceed, but the decision must be marked conditional and include a deadline/trigger. Example: the final transaction rate is not yet measured, but early pattern exploration can use a labelled range.
- **Non-blocking unknown:** the answer has low impact on the current decision or can be deferred without meaningful rework. Example: a low-priority dashboard layout preference before architecture selection.

For every unknown, record: the exact question; why it matters; owner; evidence needed; due date; decisions affected; whether it blocks or conditions the decision; and what happens if the answer is not obtained. “TBD” without these details is not a useful control.

### 5.11 Intermediate exercise: Northbridge register with at least ten items

Build the register using the fields above. The sample below demonstrates the minimum quality bar; treat all Northbridge details as illustrative, and treat unprovided evidence as open work rather than fabricated confirmation.

| ID | Class | Statement | Owner / evidence status | Response or validation | Linked consequence / decision |
|---|---|---|---|---|---|
| CON-001 | CON, provisional until verified | Personal data for the defined scope must remain in the approved jurisdiction. | Compliance owner; scenario states this, but no policy artefact is supplied. | Confirm data classes, jurisdiction, exceptions, and authoritative policy. | Hosting/replication options; ADR-001. |
| CON-002 | CON, illustrative | Core banking extraction must respect the 02:30 batch-window boundary. | Core banking operations; verify against current runbook in a real project. | Confirm window, duration, and change path; test schedule feasibility. | Ingestion sequencing; ADR-002. |
| CON-003 | CON if approved | Programme cost must remain under sponsor-approved ceiling. | Sponsor/finance; ceiling amount and included costs are unknown here. | Obtain approved amount, currency, horizon, and scope. | Cost gate; option feasibility cannot yet be finalised. |
| PREF-001 | PREF | Stakeholders prefer to retain the existing warehouse. | Sponsor/platform owner; preference only. | Ask for rationale, priority, and waiver conditions. | Scored criterion only if agreed; not a gate by default. |
| ASM-001 | ASM | Existing card batch exports contain all required fraud fields. | Cards data owner; unverified. | Inspect schema and representative files; map fields to requirements. | If false, revise ingestion options or requirement. |
| ASM-002 | ASM | A stable customer identifier is available across systems. | Customer data owner; low confidence until profiled. | Profile identifiers, duplicates, nulls, and cross-system match rate. | Identity resolution; ADR-003 conditional. |
| ASM-003 | ASM | Two additional engineers will be assigned. | Engineering manager; no approval supplied. | Obtain capacity approval and start date. | Delivery plan and operational capacity. |
| DEP-001 | DEP | Cards platform supplies the required feed to ingestion. | Cards platform owner; delivery commitment not supplied. | Confirm interface, schedule, owner, schema, support, and test environment. | Late or incomplete feed may delay fraud use case. |
| DEP-002 | DEP | Security and compliance review must complete before production data movement. | Security/compliance approvers; confirm governance workflow. | Agree artefacts, lead time, entry criteria, and escalation route. | Critical-path dependency and release gate. |
| DEP-003 | DEP | Finance's reconciled outputs are needed for finance acceptance. | Finance data owner; acceptance criteria unknown. | Define reconciliation evidence, owner, timing, and sign-off. | Downstream acceptance milestone. |
| RSK-001 | RSK | The card feed may be late or incomplete, delaying fraud-case availability. | Fraud product owner + cards owner; likelihood evidence not yet gathered. | Validate delivery history; contract tests; lag alerts; fallback/target revision. | Example P=3, I=4, score 12 under illustrative scale; high. |
| RSK-002 | RSK | Customer identifiers may not support reliable matching, causing inconsistent consolidated records. | Customer data owner; profile evidence pending. | Profile early, test match rules, define stewardship and exception handling. | Example P=3, I=5, score 15; very high under illustrative scale. |
| UNK-001 | UNK | Which exact jurisdiction and personal-data classes are in scope? | Compliance owner; unanswered. | Obtain authoritative interpretation and data classification. | Blocks final hosting/replication choice. |
| UNK-002 | UNK | What is the approved programme budget ceiling? | Sponsor/finance; amount not supplied. | Obtain approved budget and cost inclusions. | Blocks final affordability conclusion. |
| FACT-001 | FACT, scenario-only | The scenario states average card transactions are approximately 2 million/day. | Roadmap scenario; illustrative input, not measured evidence. | Label as stated/illustrative; replace with measured range before sizing. | Capacity estimate and target validation. |

This register has more than ten items and covers all required categories. It is not “complete” for a real project until owners, source evidence, dates, status, and links are confirmed. Example scores are teaching illustrations only; re-score using observed evidence and the organisation's agreed scales.

**Risk-treatment supplement for the two scored examples (illustrative and provisional)**

The summary register intentionally stays compact, but a high/very-high risk must not stop at a score. Complete the following fields before the risk is treated as operationally managed. Calendar dates and numerical thresholds are not supplied by the scenario, so the milestone-relative due points below are prompts to agree and record—not invented commitments.

| Risk ID | Accountable risk owner | Assessment horizon and score rationale | Observable trigger | Contingency / escalation | Residual risk and acceptance authority |
|---|---|---|---|---|---|
| `RSK-001` | Delivery lead is the **proposed accountable closure owner** for this exercise; confirm the real assignment. Cards platform owner supplies source evidence; fraud product owner confirms business impact. | Horizon: now through the agreed fraud-use-case integration-readiness/acceptance milestone. `P=3` is provisional because delivery history and a tested contract have not been reviewed; `I=4` is illustrative because a missed freshness objective or milestone could materially affect the use case; `P×I=12` = high under the illustrative bands. | The feed contract/schema/cadence is not verified by the agreed integration-readiness gate, or observed late/missing-file performance breaches a threshold that the service owner must define and approve. Record the actual gate date and threshold when agreed. | Hold the affected design decision conditional; escalate to the delivery decision authority and fraud business owner; evaluate a source change, alternate feed, scoped fallback, or revised target through formal trade-off review. Do not silently assume the feed will arrive. | Residual exposure is **not yet scored**; reassess after evidence and mitigations. The role authorised to accept residual risk must be confirmed from the programme's governance/operating model before acceptance. |
| `RSK-002` | Customer data owner is the **proposed accountable closure owner** for this exercise; confirm the appointment. Business owner validates acceptable reconciliation outcomes. | Horizon: through the customer-consolidation approach decision and agreed acceptance milestone. `P=3` is provisional pending identifier profiling; `I=5` is illustrative because unreliable identity matching could undermine the core consolidated-customer outcome; `P×I=15` = very high under the illustrative bands. | Identifier profiling is unavailable by the approach-decision gate, or measured match/null/duplicate results fail thresholds that the business/data owners must define from the required reconciliation outcome. Do not invent a universal match-rate threshold. | Pause final approval of options that assume stable identifiers; profile source data; compare matching/stewardship alternatives; define exception handling and a narrower-scope fallback; escalate if the decision deadline is threatened. | Residual exposure is **not yet scored**; reassess after profiling and option analysis. The authorised residual-risk acceptance role/forum must be identified before acceptance; do not presume the data owner alone has that authority. |

**Consistency check:** both examples have a named proposed accountable owner, horizon, rationale for P and I, observable trigger, action/escalation, and an explicit residual-risk/acceptance-authority gap. These remain provisional teaching examples until the organisation supplies actual owners, dates, thresholds, evidence, and delegated authority.

### 5.12 Intermediate questions

1. Which assumption, if wrong, would invalidate the design? Explain the impact and the earliest test that could confirm or disprove it.
2. Which dependency has no confirmed owner or commitment? What decision or milestone depends on it?
3. Which unknowns block a decision, and which allow conditional progress? State the rule you used.
4. What evidence would cause you to reclassify an apparent constraint as a preference—or a preference as a constraint?
5. Which risk should be escalated first, and why? Include scale, evidence, trigger, and authority.

**Answer guidance:** prioritise the stable customer identifier and cards-feed capability when the design depends on them, because either can change integration and consolidation choices. Confirm the jurisdictional rule and budget before finalising options that depend on them. Escalation is justified by exposure and decision urgency, not simply by the loudest stakeholder. State what is unknown, who can resolve it, and the deadline before which the answer is needed.

## 6. Advanced-level learning sequence

### 6.1 Interacting risks: model the chain, not isolated rows

Risks can compound. Consider this illustrative chain:

1. The cards feed arrives late (dependency failure).
2. The fraud-case freshness target remains strict (requirement/target).
3. A regulatory or programme milestone is fixed for the current plan (time constraint, subject to authorised confirmation).
4. Testing time is compressed, increasing the chance that data-quality defects escape detection.
5. A rushed workaround increases operating burden and may undermine lineage or reconciliation.

The combined exposure may be greater than any single row suggests. Record the causal links and affected objectives. Avoid mechanically adding ordinal risk scores; explain the interaction qualitatively and re-evaluate the risk if a mitigation changes the chain.

### 6.2 Prioritise validation by impact, confidence, and decision timing

An assumption is urgent when it has high impact if wrong, low confidence, and must be resolved before a consequential decision. A useful order is:

1. Identify the decision and its latest safe decision date.
2. List every assumption that the decision relies on.
3. Assess impact if each is wrong and confidence in the evidence.
4. Estimate validation lead time and whether the result could change the ranking.
5. Validate the highest-impact, lowest-confidence assumptions first—especially those with long lead times.
6. Record the outcome and update all linked requirements, estimates, risks, criteria, and ADRs.

Do not validate assumptions solely because they are easy to test. A trivial assumption with easy evidence may be less important than a difficult assumption that could invalidate the design.

### 6.3 Unknown versus unknowable now

- **Unknown but knowable:** the information exists or can be obtained through a reasonable test, interview, contract review, data profile, or measurement. Assign an owner and due date.
- **Not yet knowable with available evidence:** the future outcome cannot be established precisely now—for example, future transaction growth or a vendor's performance under an untested peak workload. Use ranges, scenarios, and decision triggers; do not invent certainty.
- **Not necessary for this decision:** the detail may be deferred if it cannot materially change the current choice. Record the deferral and the point when it becomes necessary.

For a future transaction rate, a defensible record might say: “Expected growth is uncertain; use low/base/high scenarios derived from current measured volumes and sponsor-approved planning assumptions. Revisit when the next quarter's measured peak rate is available or when the base estimate is exceeded by the agreed trigger.” The exact range and trigger must be based on project evidence, not borrowed from this example.

### 6.4 Architectural consequences when assumptions or constraints change

A changed input should trigger **impact analysis**, not merely an edit to one row. Trace from the changed item to:

- business objectives and requirements (`BO-*`, `REQ-*`);
- estimates and service targets (`EST-*`, `TGT-*`);
- constraints, assumptions, dependencies, risks (`CON-*`, `ASM-*`, `DEP-*`, `RSK-*`, `UNK-*`);
- decision criteria and option feasibility (`CRIT-*`, gate results, scoring inputs);
- ADRs (`ADR-*`) and accepted trade-offs;
- project plan, tests, operating procedures, approvals, and deliverables.

**Worked example — stable identifier assumption fails:**

- Before: `ASM-002` assumes a stable customer identifier; one consolidation option ranks well because matching is expected to be straightforward.
- New evidence: profiling reveals missing or conflicting identifiers across source systems.
- Required action: change `ASM-002` to **failed**; attach the profiling evidence; create or update a data-quality risk; revise estimates and acceptance criteria; add matching/stewardship capabilities to alternatives and cost/operability criteria; rerun the option comparison; mark the existing ADR conditional or superseded; document the new decision and conditions.
- Invalid action: leave the ADR unchanged and add a note that the data is “messy.”

### 6.5 Challenge constraints without bypassing authority

A constraint can be challenged when its evidence, scope, ownership, or change path is unclear. Challenging does not mean ignoring it.

1. Restate the exact constraint and affected scope.
2. Identify its source and the authority that owns it.
3. Ask whether it is mandatory, temporary, inherited, or a preference presented as a rule.
4. Quantify the cost of retaining it and the benefit/risk of changing it, where feasible.
5. Ask the authorised owner to confirm, relax, or replace it through the proper process.
6. Record the decision, date, conditions, affected requirements, and ADRs.
7. Until the authorised decision is recorded, design against the currently verified constraint or mark the affected choice conditional.

For example, “all workloads must use the existing platform” may be an approved enterprise standard, a temporary migration policy, or an informal preference. The architect should not decide which it is by intuition. Obtain the evidence and record who can approve an exception.

### 6.6 Worked risk assessment

**Illustrative risk:** the cards feed may not arrive in time for the fraud-case freshness target.

- Cause: the source currently emits scheduled batch files; the future feed contract and operational schedule have not been validated.
- Event: a required file arrives late, is incomplete, or misses required fields.
- Effect: fraud analysts see incomplete or stale data, the service target is missed, or integration testing slips.
- P = 3 (possible): provisional rating because no delivery history has been analysed.
- I = 4 (major): illustrative rating because the defined fraud objective and milestone could be materially affected.
- Exposure = 3 × 4 = 12, **high** under this lesson's illustrative bands.
- Response: validate historical file arrival and completeness; agree an interface contract; add schema and freshness tests; monitor lag and missing files; define a fallback and an authorised target/scope decision if the feed cannot meet the target.
- Owner: cards platform owner for source evidence; fraud product owner for business impact; delivery lead for coordination. One role must be explicitly accountable for closing the risk record.
- Trigger: for example, failure to confirm a tested feed by the agreed integration-readiness gate, or a measured late-file rate exceeding a threshold approved by the service owner. Set the actual date and threshold from the project plan and evidence.
- Residual risk: some source outage or malformed data remains possible even after tests and monitoring. Reassess after mitigations and record who may accept the residual exposure.

Do not present the illustrative P and I as measured facts. The example demonstrates a method; the project must replace the ratings with evidence and approved scales.

### 6.7 Advanced exercise: revisit a decision

Choose one real or Northbridge architecture decision. Create a table with:

| Decision / ADR | Supporting constraints | Assumptions | Dependencies | Risks / unknowns | Revisit trigger | Required follow-up |
|---|---|---|---|---|---|---|
| ADR-001: high-level consolidation approach (illustrative placeholder) | CON-001 jurisdiction; CON-003 budget, once verified | ASM-001 feed capability; ASM-002 stable identifiers | DEP-001 cards feed; DEP-002 approvals | RSK-001 late feed; RSK-002 poor matching; UNK-001 jurisdiction details; UNK-002 budget | A critical assumption fails; an authoritative constraint changes; evidence changes option feasibility or ranking | Reopen gate results, estimates, criteria, option comparison, and ADR; obtain required approvals. |

Then answer:

1. Which constraint most limits the options, and who can change it?
2. Which risk would you escalate today, and what evidence or deadline makes escalation timely?
3. What is the earliest observable trigger that would cause you to reopen the decision?
4. Which artefacts and owners must be notified when the trigger fires?

**Ability to demonstrate:** each item links to the decisions it affects, has an owner, and has a validation date or revisit trigger. Conditional decisions name the missing evidence and the authority that will resolve it.

## 7. Industry-application exercises

### 7.1 Exercise A — Northbridge register

Create the combined constraints, assumptions, dependencies, risks, and unknowns register for Northbridge. Include at least ten records and cover all constraint categories relevant to the scenario. Use stable IDs and the fields in Section 5. Mark every scenario value as illustrative. Each record must include:

- class and precise statement;
- source/evidence label and status;
- owner or the explicit fact that ownership is unresolved;
- flexibility for constraints and preferences;
- confidence and validation method/date for assumptions;
- dependency provider, consumer, interface, and timing;
- probability, impact, exposure, scale, and rationale for risks;
- response, trigger, contingency/escalation, and linked requirements/decisions.

**Acceptance test:** a reviewer can identify what is known, what is believed, what is required from another party, what could go wrong, who acts next, and which decision is affected without asking you to explain the table verbally.

### 7.2 Exercise B — customer-consolidation dependency map

Produce a map for the customer-consolidation programme. Include at least the core banking system, cards platform, CRM, loan origination system, ingestion/reconciliation, customer identity resolution, governed consolidated view, and relevant downstream consumers. Add cross-cutting approvals and shared services where relevant. Highlight the critical path, but do not invent durations or committed dates. Where timing is unknown, show the dependency as provisional and identify who must supply the evidence.

**Acceptance test:** each arrow has a clear meaning; each critical dependency has a provider and owner; a delay can be traced to affected work and milestone; a contingency or escalation path exists for material dependencies.

### 7.3 Exercise C — escalation note

Write an escalation note for the highest-exposure risk in your register. It must include:

1. A cause–event–effect statement.
2. Current evidence, missing evidence, and the stated scoring scale.
3. Probability, impact, exposure, and a short rationale for each score.
4. Affected objectives, requirements, constraints, dependencies, and ADRs.
5. At least two feasible options and the consequence of accepting or deferring.
6. A recommendation tied to evidence and decision criteria.
7. Owner, decision authority, decision deadline, trigger, contingency, and next review date.

Do not escalate a risk merely by assigning a large number. Explain the decision needed and the cost of waiting.

### 7.4 Exercise D — traceability and change impact

Select one high-impact assumption and simulate both outcomes: validated and failed. For each outcome, state which estimates, targets, constraints, risk records, criteria, alternatives, ADRs, and follow-up actions change. Keep IDs consistent across the artefacts.

**Acceptance test:** a reviewer can trace the assumption to a decision and can see exactly what reopens if it fails.

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — Vendor says an API will be available “next quarter”

**Question:** How should this be classified, and how do you plan around it?

**Reasoned response:** treat the vendor's statement as a **stated claim** about a **dependency**, not a confirmed fact about availability. If the architecture assumes the API will exist by a needed date, record that proposition as an assumption. The possibility of late or incomplete delivery is a risk if it can affect objectives. Request a written delivery commitment, interface specification, test access date, required fields, support terms, and evidence of capability. Map the dependency to integration testing and downstream milestones. Compare a fallback or alternative that does not require the unconfirmed API. Keep any decision relying on it conditional until the required evidence is obtained. Set an owner, validation date, trigger, and escalation path.

### Scenario 2 — Policy prohibits copying personal data outside production region

**Question:** Is this a constraint or a preference, and who can change it?

**Reasoned response:** if an authorised, applicable policy or legal interpretation establishes the prohibition, treat it as a constraint for the scoped decision. Confirm which data classes, processing, backups, replicas, support access, and environments it covers. The relevant policy/legal/compliance authority—not the delivery team alone—must clarify or approve any exception or change. If the only evidence is an informal statement, mark the constraint as provisional and open an evidence question; do not assume it is false or bypass it. Do not invent the jurisdiction or cite a law not supplied by an authoritative source.

### Scenario 3 — Stable source schemas assumption fails during design

**Question:** Which artefacts must be reopened?

**Reasoned response:** mark the assumption failed and preserve the evidence. Reassess interface dependencies, data-quality and operational risks, ingestion and transformation estimates, service targets, test strategy, acceptance criteria, decision gates, and the alternatives that assumed stable schemas. Review affected ADRs and label them conditional, superseded, or still valid with explicit rationale. Notify the source owner, platform/operations owner, downstream consumers, and decision authority. Create a change action with owner and due date. Do not merely edit the assumption row while leaving dependent decisions untouched.

### Scenario 4 — The source team has no named owner for a required extract

**Question:** Is this a dependency, a risk, or an organisational constraint?

**Reasoned response:** it is at minimum a dependency with an ownership gap; the absence of an accountable provider is also an unresolved governance question and can create a risk of delay or unsupported operation. Ask the data domain owner or governance body to assign accountability. Record the decision deadline and escalation route. Until ownership is assigned, do not present the extract as a committed delivery. If the extract is critical path, escalate based on milestone impact.

### Scenario 5 — A stakeholder insists that every dataset be available in real time

**Question:** Should this be accepted as a constraint?

**Reasoned response:** no, not without clarification and authority. It is an unqualified request or preference until the consumer, decision, harmful delay, required freshness, hours, percentile, and measurement boundary are specified. Use Topic 4 to turn the request into workload-specific targets. Then determine whether the targets are mandatory business requirements, negotiable preferences, or unvalidated assumptions. If targets are incompatible with source capabilities or funding, present explicit alternatives and trade-offs through Topic 6 rather than silently treating the request as feasible.

### Scenario 6 — A high-impact assumption cannot be validated before the decision date

**Question:** Must the programme stop?

**Reasoned response:** it depends on whether the assumption is a feasibility gate and on the cost of an incorrect decision. If the uncertainty could invalidate a mandatory control or make an option infeasible, defer the decision or select a reversible alternative that does not rely on the assumption. If preliminary work can safely proceed, record the decision as conditional, specify the evidence still needed, set an owner and deadline, define a trigger and fallback, and identify what work must not begin until validation. The authority for accepting residual exposure must be explicit.

### Scenario 7 — A “fixed” constraint is challenged as a preference

**Question:** How do you challenge it safely?

**Reasoned response:** ask for the authoritative source and owner; document the scope and consequences; identify the formal change/exception process; and compare the cost and risk of retaining versus changing it. Record the outcome and approver. Until the authorised owner confirms a change, keep the current verified constraint in force. A developer or architect cannot unilaterally waive an organisational, contractual, regulatory, or policy requirement.

## 9. Expected outputs and deliverables

The topic-specific roadmap requires these deliverables:

1. **Constraints, assumptions, dependencies, and risks register.** Each item has a stable ID, class, statement, source/owner, status, relevant exposure, response, trigger, and linked decisions. The register also captures flexibility, validation method/date, and evidence where applicable.
2. **Dependency map with critical path.** It shows upstream and downstream systems, teams and approvals, provider/consumer ownership, sequencing, critical dependencies, and failure consequences. Unknown durations or uncommitted dates are marked, not invented.
3. **Assumption validation plan.** High-impact, low-confidence assumptions are prioritised; each has a validation method, accountable owner, due date, evidence result, and fallback if false.
4. **Answers to Topic 5 practice questions.** The roadmap specifies this deliverable, but the repository's `practice-questions.md` is reported as empty. The exercises and questions in this lesson provide practice; do not claim they are copied from that empty file.

### 9.1 Minimum register quality checklist

- [ ] No item is unclassified; uncertain classifications are explicitly provisional and have a resolution action.
- [ ] No material item is ownerless. If the owner is unknown, an action exists to assign one.
- [ ] Facts have inspectable evidence; assumptions are not described as verified facts.
- [ ] Constraints name their source, scope, authority, and change path.
- [ ] Preferences are not used as hard gates without explicit authorisation.
- [ ] Assumptions have confidence, impact if wrong, validation method, owner, due date, and failure consequence.
- [ ] Dependencies name provider, consumer, interface/commitment, timing, and failure consequence.
- [ ] Risk scores use documented scales, an explicit assessment horizon, evidence and rationale; the score is not represented as precise probability or monetary loss.
- [ ] Every high-exposure risk has one accountable risk owner, response, observable trigger, contingency, escalation path, assessment horizon, and identified authority for any residual-risk acceptance.
- [ ] Linked IDs make requirement-to-decision impact analysis possible.
- [ ] Review dates and triggers are defined for items that can change.

### 9.2 Reusable change-impact record

```text
Change ID:
Date / reporter:
Changed item ID and previous status:
New evidence and source:
Classification change (if any) and rationale:
Affected business objectives / requirements:
Affected estimates / targets:
Affected constraints / assumptions / dependencies / risks:
Affected criteria / alternatives / ADRs:
Options: proceed / revise / pause / revert / escalate
Recommendation and evidence:
Decision authority and approval:
Actions, owners, due dates:
Validation / closure evidence:
```

This record can be kept alongside the register or in the change-management system already used by the programme. No particular tool is required.

### 9.3 Link to later topics

- **Topic 6 — Architecture trade-offs and decision criteria:** constraints become feasibility gates when genuinely mandatory; preferences can become scored criteria when agreed; risk and uncertainty influence comparison and sensitivity analysis.
- **Topic 7 — Architecture Decision Records:** each major decision should link to relevant requirement, constraint, assumption, dependency, risk, and criterion IDs. Record conditional decisions, rejected alternatives, consequences, and revisit conditions.
- **Later Stage 2D modules:** verified residency constraints affect cloud/hybrid options; source-window and feed dependencies affect integration; identity and data-quality assumptions affect data modeling and consolidation; retention constraints affect storage and governance. Do not decide the detailed design here—make the boundary and traceability explicit.

## 10. Common mistakes and misconceptions

1. **Using the terms interchangeably.** Corrective action: apply the one-line tests in Section 4.1 and preserve links between related records.
2. **Treating preferences as constraints, or constraints as preferences.** Corrective action: confirm authority, evidence, change cost, and approval path.
3. **Leaving assumptions unwritten or unowned.** Corrective action: create an assumption record as soon as a decision relies on an unverified proposition.
4. **Calling a stakeholder claim a fact.** Corrective action: label evidence as measured, sampled, stated, estimated, guessed, or unknown; record source and date.
5. **Rating risks without scales or evidence.** Corrective action: define probability and impact scales before scoring, state the rationale, and acknowledge ordinal limitations.
6. **Recording a risk with no mitigation, owner, trigger, or escalation.** Corrective action: make the next action and decision authority explicit; acceptance must be authorised.
7. **Assuming a dependency is safe because it exists today.** Corrective action: verify its service conditions, timing, owner, interface, change process, and failure modes.
8. **Treating every unknown as a blocker.** Corrective action: classify unknowns by impact and decision timing; proceed conditionally only where safe and reversible.
9. **Treating “unknown” as “unknowable.”** Corrective action: determine whether a test, sample, interview, contract review, or measurement can resolve it.
10. **Using a numerical score as objective truth.** Corrective action: treat `P × I` as a ranking aid, retain evidence and rationale, and escalate mandatory-control concerns regardless of score.
11. **Failing to account for interacting risks.** Corrective action: show causal links and common dependencies; reassess combined exposure qualitatively.
12. **Challenging a constraint by simply ignoring it.** Corrective action: use the authorised change or exception process and record its outcome.
13. **Not linking constraints and risks to decisions.** Corrective action: use stable IDs across requirements, estimates, criteria, alternatives, and ADRs.
14. **Failing to reopen a decision when an assumption changes.** Corrective action: define revisit triggers in advance and conduct cross-artefact impact analysis.
15. **Inventing legal or regulatory requirements.** Corrective action: identify the authoritative owner and source, specify the actual scope, and mark unresolved interpretation as open.
16. **Over-documenting low-impact items while high-impact assumptions remain untested.** Corrective action: prioritise by impact if wrong, confidence, validation lead time, and decision deadline.
17. **Calling a dependency “critical path” without sequence evidence.** Corrective action: show predecessors and supported durations; label the path provisional where timing is unknown.
18. **Marking the register complete because every row has text.** Corrective action: check evidence, ownership, action, trigger, and traceability—not word count.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following:

1. **Classification:** classify a fresh sample of ten statements correctly and explain the evidence-based test for each; resolve ambiguity explicitly rather than forcing a false certainty.
2. **Constraint analysis:** identify relevant constraint categories, distinguish fixed limits from preferences, and name the authority and process for changing a constraint.
3. **Assumption management:** rank assumptions by impact if wrong and confidence; assign owners, validation methods and dates; state what happens if an assumption fails.
4. **Dependency analysis:** map upstream/downstream relationships, providers, consumers, owners, sequencing, critical path, and consequences of late or failed delivery.
5. **Risk assessment:** use stated probability and impact scales; justify ratings; choose proportionate responses; identify residual risk, trigger, owner, and escalation/acceptance authority.
6. **Uncertainty handling:** distinguish facts from unverified claims, unknowns from unknowable future outcomes, and blocking unknowns from conditionally manageable gaps.
7. **Traceability:** link records to requirements and decision IDs; show which estimates, criteria, alternatives, and ADRs must be reopened when an input changes.
8. **Industry application:** produce a reviewable Northbridge register, dependency map with a defensible critical path, assumption validation plan, and escalation note.
9. **Decision defence:** explain which decision can be finalised now, which must remain conditional, what evidence is missing, who will obtain it, and by when.

A good artefact is not one in which uncertainty disappears. It is one in which uncertainty is visible, owned, bounded, and connected to a decision or action.

## 12. Completion gate

Do not mark Topic 5 complete until every check below passes:

- [ ] **Register complete:** constraints, assumptions, dependencies, risks, and unknowns are represented; no material item is unclassified or ownerless. Any unresolved owner is accompanied by an assignment action.
- [ ] **Classification test passed:** a fresh sample is classified correctly and the reasoning is stated; target at least 90% accuracy consistent with the module's beginner-to-intermediate progression.
- [ ] **High-exposure risks controlled:** each high/very-high item has one accountable risk owner, response, observable trigger, contingency/escalation route, explicit assessment horizon, and identified authority for any acceptance of residual exposure.
- [ ] **High-impact assumptions scheduled:** each has a validation method, accountable owner, and due date before the decision that depends on it; failure consequences and fallback are explicit.
- [ ] **Dependencies mapped:** upstream/downstream links, providers, consumers, owners, sequencing, and failure consequences are shown; the critical path is supported by known durations or labelled provisional where evidence is missing.
- [ ] **Traceability works:** constraints and risks link to requirements and decisions; the impact of a changed assumption can be followed to estimates, targets, criteria, alternatives, and ADRs.
- [ ] **Uncertainty is honest:** facts have evidence; illustrative values are labelled; unknowns have owners/actions; future uncertainty uses ranges or triggers rather than invented precision.
- [ ] **Practice questions answered and corrected:** complete the classification, Northbridge register, dependency-map, escalation, and change-impact exercises; correct mistakes before proceeding.

**Completion decision:** if any high-impact assumption lacks a validation owner/date, any high-exposure risk lacks a response or trigger, or a material item cannot be traced to the decisions it affects, the gate is **not passed**. Resolve the gap or explicitly escalate it to the authorised decision-maker; do not conceal it by marking the document complete.
