# Stakeholder Discovery and Business Requirements

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Identify stakeholders and document their interests, influence, role, and decision authority without confusing seniority with decision rights.
2. Elicit business goals, business problems, and desired outcomes using interviews, workshops, questionnaires, document analysis, and observation.
3. Separate a stakeholder's stated request from the underlying need, a business requirement, a constraint, an assumption, and a solution preference.
4. Translate business problems into data-related business requirements that have a clear source and a business home.
5. Define scope, exclusions, boundaries, and observable success criteria before architecture choices are made.
6. Record stakeholder disagreements, ambiguity, missing evidence, dependencies, and unresolved questions with accountable owners.
7. Validate requirements with the people authorized to confirm them, record sign-off, maintain traceability from business objectives to requirements and later architecture artefacts, and defend the discovery approach using evidence, explicit assumptions, and clear decision rights.

**Working principle:** discover the problem before selecting the solution. A request is evidence about what someone wants; it is not automatically a complete or valid requirement.

## 2. Why the topic matters in real-world Data Architecture

Data architecture decisions have long-lived consequences: they influence which systems exchange data, who owns definitions, how information can be used, how operational teams support the result, and how later designs meet business needs. If the initial problem is misunderstood, a technically elegant architecture can still deliver the wrong outcome.

Common upstream failures include:

- treating “build a dashboard” or “put all data in one place” as a complete requirement;
- interviewing only the sponsor and missing consumers, source-system owners, operators, or control functions;
- assuming two teams use the same definition of “customer,” “active,” or “current”;
- recording a preferred technology as if it were a business need;
- leaving scope and exclusions implicit;
- using activities (“deliver a data lake”) instead of observable outcomes as success criteria;
- treating silence as agreement or resolving disagreements by hierarchy;
- failing to record who validated a requirement and what evidence supports it.

Discovery reduces these risks by establishing a shared, reviewable account of the problem. It also prevents premature design. For example, inconsistent customer counts might result from different counting rules, different reporting dates, duplicate identities, different population boundaries, or actual data-quality defects. Choosing a new platform before investigating those possibilities risks moving inconsistent definitions into a new platform.

### The discovery-to-requirement chain

```text
Business objective
  → business problem and evidence
  → stakeholder need
  → business requirement
  → observable success criterion
  → traceable requirement ID
  → later analysis and architecture artefacts
```

Every arrow should be explainable. If the chain breaks, record the gap rather than inventing the missing link.

## 3. Prerequisite concepts

The roadmap assumes that you have studied Stage 2D, Module 2D.1, Topics 1–3: stakeholder vocabulary, role boundaries, business capabilities, domains, and data ownership. You should understand that a **business capability** is something an organisation must be able to do, a **business process** is a sequence of activities used to do it, a **domain** groups related business concepts and responsibilities, and **data ownership** identifies who is accountable for definitions, quality, access, or lifecycle decisions. Exact ownership models vary by organisation.

Helpful working knowledge includes:

- the difference between a source system, a data producer, and a data consumer;
- the fact that one business concept may appear in multiple systems with different definitions;
- basic structured prose and tables;
- the ability to distinguish evidence from interpretation.

You do not need a requirements-management tool, formal modelling language, or certification. Markdown tables and a disciplined ID convention are sufficient for this lesson.

### Evidence labels used throughout this lesson

Use explicit labels to avoid accidentally turning a hypothesis into a fact.

| Label | Meaning | Example |
|---|---|---|
| **Verified fact** | Supported by inspected evidence or a confirmed source | “The report contains a field named `customer_id`,” confirmed in the current report specification. |
| **Stakeholder statement** | What a person said; not necessarily independently verified | “Finance says its count excludes closed accounts.” |
| **Illustrative assumption** | A value or condition invented for learning or planning | “Assume approximately 3 million retail customers.” |
| **Inference** | A reasoned interpretation of evidence, open to challenge | “Different population boundaries may explain the count variance.” |
| **Open question** | A matter not yet resolved | “Which date defines the reporting population?” |

A stakeholder statement is evidence that the stakeholder holds a view. It is not, by itself, proof that the view is objectively correct.

## 4. Beginner-level learning sequence

### 4.1 Learn the core terms

| Term | Practical meaning | Example |
|---|---|---|
| **Stakeholder** | A person or group that can affect, is affected by, uses, operates, governs, funds, or approves the work | Finance analysts who rely on a customer count. |
| **Business goal** | A broad result the organisation wants to achieve | Improve confidence in management reporting. |
| **Business problem** | A present difficulty, gap, risk, or unmet need that blocks a goal | Finance and risk publish different customer counts without a reconciled explanation. |
| **Desired outcome** | A result that should be observable if the problem is addressed | Approved reports use a documented population definition and explain differences. |
| **Business requirement** | A statement of what the business needs to be able to achieve, without prematurely prescribing the technical design | “Authorised reporting teams must be able to obtain a reconciled customer count for an agreed population and as-of date.” |
| **Scope** | The work, data, people, processes, and decisions included | Customer, account, and card-transaction data relevant to the initial problem. |
| **Exclusion** | Something explicitly not being solved in this work | Detailed physical schema design. |
| **Success criterion** | Observable evidence used to decide whether the desired outcome has been achieved | Finance and risk approve one population definition and a reconciliation procedure; unresolved differences are documented with owners. |

A goal can be broad; a problem describes the gap; an outcome describes the intended change; a requirement expresses what must be enabled; a success criterion describes how to recognise success. These are related but not interchangeable.

### 4.2 Categorise stakeholders

A person can hold more than one role. Record the role relevant to each decision rather than forcing every person into one exclusive category.

| Category | Typical concern | Questions to ask |
|---|---|---|
| **Sponsor** | Business case, funding, outcomes, major scope | What business outcome justifies the work? What boundary or funding decision can you make? |
| **Decision-maker** | A defined decision within delegated authority | Which decision are you authorised to make? Who must be consulted or approve it? |
| **Business owner** | Meaning and fitness of a business capability, process, or outcome | What does the business term mean? Who accepts the outcome? |
| **Data producer / source owner** | Meaning, quality, availability, and change of source data | What is created, when, under which rules, and what limitations exist? |
| **Data consumer** | How data is used and what decisions depend on it | What decision do you make with the data? What happens when it is late or wrong? |
| **Operator** | Monitoring, support, recovery, handover, and operational workload | Who detects and resolves failure? What runbook or support window is required? |
| **Control function** | Risk, compliance, security, privacy, audit, or other control obligations | What control objective or evidence must be satisfied? What is the source of the obligation? |

Control functions may include risk, compliance, security, privacy, and internal audit. A regulator may be an external stakeholder or source of a requirement, but do not invent a regulatory obligation: capture the actual communication, applicable rule, interpretation owner, and due date when available.

**Influence is not authority.** A senior executive may influence a decision but lack delegated authority over a particular data definition. A control function may have approval or veto rights for a control matter. Record the actual decision right and how it was confirmed.

### 4.3 Use elicitation techniques deliberately

**Elicitation** means drawing out information about goals, needs, current work, constraints, and acceptance. No single technique is sufficient for every stakeholder or question.

| Technique | Good for | Limitations and safeguards |
|---|---|---|
| **Interview** | Exploring a person's goals, terminology, pain points, and reasoning | Memory and personal bias can affect answers; verify important claims and ask for examples. |
| **Workshop** | Surfacing shared definitions, dependencies, disagreements, and decisions across groups | Dominant voices can suppress others; use facilitation, explicit turn-taking, and a decision log. |
| **Questionnaire** | Collecting comparable answers from many people or teams | Weak for follow-up and ambiguity; pilot questions and follow up on inconsistent responses. |
| **Document analysis** | Reviewing policies, report definitions, data dictionaries, process maps, incident records, and existing specifications | Documents may be stale or reflect intended rather than actual practice; record version and owner. |
| **Observation** | Seeing how reports, reconciliations, handoffs, and operational processes actually work | A short observation may miss exceptions or unusual periods; ask about edge cases and observe more than one instance when needed. |

Choose the technique based on the question. To understand why finance's count differs from risk's, interviews alone are unlikely to be enough: inspect both report definitions, observe the reconciliation process, and bring the owners together to compare rules.

### 4.4 Ask open questions and use the why-ladder

An open question invites explanation rather than a yes/no answer. Avoid leading questions such as “Wouldn't a central customer platform solve this?” Prefer “What decision are you unable to make today?”

The **why-ladder** repeatedly asks why a request matters, until the underlying business outcome becomes clear. It is not an interrogation: listen, reflect the answer, and stop when the outcome is sufficiently clear to validate.

**Worked example**

1. Request: “Build a dashboard with all customer data.”
2. Why? “Managers need one customer count.”
3. Why? “Finance and risk reports disagree.”
4. Why does that matter? “Management meetings spend time debating which number to use.”
5. What outcome would help? “The reports should use an agreed population definition and explain any legitimate differences.”

The dashboard is a possible solution preference. The underlying need concerns consistent definitions, explainable counts, and trusted reporting. A dashboard may still be useful, but discovery has not yet shown it to be necessary or sufficient.

Use additional techniques when appropriate:

- **Five-whys / causal probing:** ask successive “why” questions to explore a cause; avoid assuming the first answer is the root cause.
- **Examples and counterexamples:** ask for a record or report that should be included and one that should not.
- **Process walk-through:** ask the stakeholder to demonstrate the current workflow step by step.
- **Boundary questions:** ask what is explicitly included, excluded, or treated differently.
- **Failure questions:** ask “What would make this outcome fail?” and “What happens if the data is late, missing, duplicated, or disputed?”

### 4.5 Worked request-to-requirement example

The following is illustrative, not a verified organisational requirement.

| Stage | Example | Why it matters |
|---|---|---|
| Stated request | “Put all customer data in one place.” | It expresses a preferred shape of solution, but “all,” “customer,” and “one place” are undefined. |
| Underlying need | “Reporting teams need a consistent, explainable customer count.” | Names the capability needed rather than the proposed implementation. |
| Business requirement | “Authorised reporting teams must be able to obtain a customer count for an agreed population and as-of date, using a documented definition.” | States what must be possible without choosing a platform. |
| Candidate success criterion | “Finance and risk owners approve the population definition; a sample reporting period is reconciled; each remaining variance has a documented cause or owner.” | Gives observable evidence. Specific pass thresholds and sample periods still require stakeholder confirmation. |
| Traceability | `BO-01` → `BR-01` → `SC-01` | Allows reviewers to follow the reason for the requirement and its acceptance evidence. |

Do not invent a numerical tolerance just to make a criterion look measurable. If the acceptable tolerance is unknown, record it as an open question and assign an owner.

### 4.6 Beginner exercise: three-sentence request

**Request (fictional and illustrative):** “Our leadership reports show different customer totals. Marketing wants a dashboard containing every customer attribute. The sponsor wants an initial proposal before the next planning meeting.”

Create a list of stakeholders to approach and one open question for each. A reasonable starting answer is:

| Stakeholder group | Open question | Why approach them? |
|---|---|---|
| Sponsor | What decision must the proposal enable, and what is the deadline for that decision? | Clarifies objective and decision boundary. |
| Finance report owner | What population and as-of date does the finance count represent? | Reveals the existing definition. |
| Risk report owner | How is the risk count calculated, and where does it differ from finance's? | Identifies a second definition and comparison points. |
| Marketing consumer | Which business decisions require which customer attributes? | Tests whether “every attribute” is necessary. |
| Source-system/data owner | Which systems are authoritative for the relevant attributes, and what limitations apply? | Establishes provenance and ownership. |
| Operations/support | How are report failures, late data, and count discrepancies detected and resolved today? | Surfaces operational needs often omitted early. |
| Privacy/security/control representative | What access or use boundaries must be considered, and what evidence establishes them? | Identifies control requirements without assuming their details. |

**Beginner check:** explain why “build a dashboard” is not a complete requirement. It does not specify the decision supported, users, population, definitions, required behaviour, boundaries, acceptance evidence, or constraints. A stakeholder often missed from the first list is an operator, downstream consumer, source owner, or control function; which one matters depends on the scenario.

## 5. Intermediate-level learning sequence

### 5.1 Build a stakeholder register

A stakeholder register is a compact working record of who matters to the discovery, why they matter, and how to involve them. Keep it minimal enough to maintain. Do not store sensitive personal commentary that is unnecessary to the work.

**Completed illustrative example**

| ID | Stakeholder / role | Interest | Influence | Decision rights | Attitude / concern | Communication preference | Status |
|---|---|---|---|---|---|---|---|
| ST-01 | Chief data officer; sponsor | Trusted cross-business data and delivery boundaries | High | Confirms business objective and sponsor-level scope; exact authority to verify | Wants a proposal by planning meeting | Short pre-read plus decision workshop | Assumed for scenario; confirm in real work |
| ST-02 | Head of finance; report owner | Reconciled finance count and reporting definitions | High | Confirms finance meaning and acceptance for finance use | Concerned about changing historical figures | Walk-through of existing reports | Assumed |
| ST-03 | Head of risk; report owner | Consistent risk population and explainable differences | High | Confirms risk meaning and acceptance for risk use | Believes risk count is correct | Comparative workshop | Assumed |
| ST-04 | Head of fraud operations; consumer | Timely card-transaction signals for case work | High | Confirms operational need; technical authority to verify | Concerned about data arriving hours late | Process walk-through | Assumed |
| ST-05 | Compliance officer; control function | Evidence of lineage and accountability | High for relevant controls | Clarifies control interpretation; formal approval rights to verify | Needs evidence, not only assurances | Document review and focused interview | Assumed |
| ST-06 | Source-system engineering lead; producer | Feasibility, source semantics, release and batch limitations | Medium–high | Confirms source behaviour and technical constraints | Protects critical batch window | Technical interview | Assumed |
| ST-07 | Operations lead; operator | Supportability, monitoring, recovery, handover | Medium | Confirms operational readiness requirements within remit | Avoids unowned support load | Runbook and incident review | Assumed |
| ST-08 | Security lead; control function | Access boundaries and security controls | High for security decisions | Decision rights to confirm against governance | Avoids uncontrolled broad access | Security review | Assumed |
| ST-09 | Internal audit; assurance stakeholder | Evidence trail and accountability | Medium–high | Defines audit evidence expectations within remit; exact authority to verify | Wants reproducible evidence | Evidence walkthrough | Assumed |

The people and authority shown above are scenario assumptions, not facts about a real bank. In a real engagement, verify names, responsibilities, authority, and availability.

### 5.2 Plan elicitation before scheduling meetings

A good elicitation plan links each question to a stakeholder, method, evidence source, and intended output. It prevents repetitive interviews and reveals who has not yet been consulted.

**Blank reusable template**

| Session ID | Stakeholder(s) | Objective / hypothesis to test | Technique | Questions / evidence requested | Preparation | Output | Owner / date / status |
|---|---|---|---|---|---|---|---|
| `EL-__` |  |  | Interview / workshop / questionnaire / document review / observation |  |  |  |  |

Plan questions around:

- business goals and the decisions that depend on the data;
- current process, workarounds, pain, and frequency of the problem;
- definitions, population boundaries, time boundaries, and exceptions;
- data sources, producers, consumers, and accountability;
- deadlines, volumes, timing expectations, and operational dependencies where relevant;
- risks, control objectives, and evidence required;
- what would make the proposed outcome fail;
- what the stakeholder can confirm, what they cannot confirm, and who can.

**Illustrative elicitation plan for Northbridge Bank**

| Session | Stakeholders | Method | Main questions / evidence | Expected output |
|---|---|---|---|---|
| `EL-01` Objectives and scope | Sponsor, business owners | Interview then scope workshop | Which decisions are failing today? What is in/out? Who approves scope? | Problem statement, objectives, scope draft |
| `EL-02` Customer counts | Finance and risk report owners | Report/document analysis plus joint workshop | Definitions, filters, as-of dates, exclusions, duplicates, source lineage | Comparison of definitions and conflict items |
| `EL-03` Customer data sources | Retail/business owners and source engineering leads | Interviews and data/process walk-through | Which systems create which attributes? What does each identifier mean? | Producer/domain map and evidence list |
| `EL-04` Fraud timeliness | Fraud operations, card-platform owner, operations | Process observation and interview | When is a transaction created, emitted, received, and visible? What is the impact of delay? | Current-state timeline and unanswered timing questions |
| `EL-05` Controls and evidence | Compliance, security, internal audit | Focused interviews and document analysis | What specific control or evidence is required? Who interprets it? What is the source? | Control questions and validation actions |
| `EL-06` Review and validation | All accountable requirement owners and decision-makers | Structured playback workshop | Are statements accurate? Which conflicts remain? Who accepts each item? | Validated requirements, decisions, and open-question log |

### 5.3 Interview records: capture statements before interpreting them

A useful interview record preserves the stakeholder's wording, then separately records the analyst's classification and follow-up. This avoids silently converting a quote into a requirement.

**Completed illustrative record**

| Field | Record |
|---|---|
| Interview ID / date | `INT-02`; illustrative date not specified |
| Interviewee | Head of marketing (assumed scenario role) |
| Purpose | Understand the request for all customer data in one place |
| Verbatim statement | “We need every customer attribute in one place so campaigns stop missing people.” |
| Classification | Request / solution preference: “every attribute in one place.” Stated need: improve campaign coverage. Hypothesis: campaign targeting lacks complete or reliable attributes. |
| Evidence offered | None during this hypothetical interview; report or campaign examples requested. |
| Follow-up questions | Which campaigns failed and how was failure measured? Which attributes are necessary for each decision? What does “customer” include? What access boundary applies? |
| Open items | Attribute list, definition of missed coverage, evidence of current failure, authorised-use boundaries |
| Confirmed by / when | Not yet confirmed; playback required |

**Blank interview-record template**

```markdown
## Interview record: INT-__
- Date / time:
- Interviewee and role:
- Interviewer:
- Purpose:
- Context / documents reviewed:

### Verbatim statements
- “...”

### Analyst classification (do not merge with the quote)
- Goal:
- Problem:
- Need:
- Request / solution preference:
- Constraint (source and fixed/negotiable status):
- Assumption (owner, confidence, validation action):
- Evidence / source:

### Follow-up
- Open questions:
- Conflicts:
- Actions, owner, due date:
- Playback sent? By whom / when?
- Corrections or confirmation received:
```

### 5.4 Distinguish adjacent concepts consistently

| Category | Definition | Test question | Example |
|---|---|---|---|
| **Request** | What a stakeholder asks for, often in solution language | What did they ask us to do? | “Build a customer dashboard.” |
| **Underlying need** | The capability or outcome the stakeholder lacks | What problem or decision makes the request matter? | “Users need an explainable count for a defined population.” |
| **Business requirement** | A business-level statement of what must be possible or achieved | What outcome/capability is necessary, without prescribing a design? | “Finance and risk must be able to obtain counts using an agreed definition and reporting date.” |
| **Constraint** | A boundary that limits feasible options; may be fixed or negotiable | What limits the solution, and who can change it? | “The existing identity provider must be used,” if confirmed as mandatory. |
| **Assumption** | A proposition treated as true temporarily because evidence is incomplete | What are we temporarily relying on, and how will it be checked? | “The card platform emits a file every 15 minutes,” pending source-owner confirmation. |
| **Solution preference** | A favoured implementation or product direction | Is this a means someone prefers rather than an outcome? | “Use a lakehouse,” before alternatives are assessed. |
| **Success criterion** | Observable evidence that indicates an outcome has been achieved | What would a reviewer observe to accept the outcome? | “Named finance and risk owners approve the definition and review a reconciled sample.” |

A statement can contain more than one category. Split it into atomic parts rather than forcing the whole sentence into one label. For example, “We must use Tool X because it is already approved and need all customer data in one dashboard” contains a possible constraint (approval status, which must be verified), a solution preference (Tool X), and a request (dashboard with all data).

### 5.5 Map requirements to capabilities, domains, processes, consumers, and decision-makers

Every requirement needs a business home: the capability or process it supports, the data domain involved, the consumer who uses the outcome, and the person authorised to validate it. This mapping helps find duplicate requests and hidden stakeholders.

**Illustrative mapping**

| Requirement ID | Business objective | Capability / process | Domain(s) | Producer(s) | Consumer(s) | Validator / decision authority to confirm |
|---|---|---|---|---|---|---|
| `BR-01` | Trusted management reporting | Customer reporting and reconciliation | Customer, account | Core banking, CRM, loan origination (scenario assumptions) | Finance, risk | Finance and risk business owners for their respective definitions; sponsor for scope |
| `BR-02` | Timely fraud investigation | Fraud case investigation | Card transaction, customer | Cards platform | Fraud analysts | Head of fraud operations for business acceptance; source owner for source behaviour |
| `BR-03` | Evidence of lineage and accountability | Data governance and assurance | Customer, account, transaction | Relevant source owners | Compliance, internal audit | Appropriate control owner; exact decision rights to verify |

This is a discovery map, not a physical data model or final architecture. Avoid deciding where data will be stored at this stage.

### 5.6 Define scope, exclusions, boundaries, and success criteria

Scope describes the problem boundary; it should specify relevant business concepts, users, processes, systems or sources, and decisions. Exclusions state what this effort will not decide. Boundaries can include organisational, temporal, geographic, data-population, process, or decision boundaries.

**Illustrative Northbridge scope statement**

- **Problem:** customer information is inconsistent across reports, fraud analysts receive card transactions hours after the fact, and evidence of lineage/accountability is weak.
- **Objectives:** establish the business definition and reconciliation approach for a single customer count; clarify the required freshness outcome for fraud use; identify the evidence needed for lineage and accountability.
- **In scope:** customer, account, and card-transaction data; consolidation and timeliness needs; high-level constraints and risks; the business acceptance conditions for the three objectives.
- **Out of scope:** detailed schema design, vendor product selection beyond option categories, implementation, migration plans, detailed cost negotiation, and final decisions belonging to later architecture modules.
- **Boundaries to confirm:** relevant customer populations, as-of date, closed/inactive records, duplicate identities, source ownership, reporting consumers, and applicable jurisdiction.
- **Illustrative initial assumptions from the module scenario:** about 3 million retail customers; about 2 million card transactions per average day; card platform emits batch files every 15 minutes today; seven-year transaction retention; programme budget ceiling set by sponsor. These are teaching assumptions, not verified facts or recommended targets.
- **Illustrative known constraints from the module scenario:** personal data must remain in a stated jurisdiction; the core banking batch window ends at 02:30; the existing identity provider must be used; a regulatory milestone date applies. In a real engagement, the precise jurisdiction, source, authority, and date must be verified.

A good success criterion is observable and linked to an outcome, not merely a deliverable or activity.

| Weak criterion | Why weak | Better candidate criterion (requires validation) |
|---|---|---|
| “Deliver a data lake.” | Describes a solution/activity, not a business outcome. | “Finance and risk approve a shared population definition and review a sample reconciliation with documented differences.” |
| “Make the data accurate.” | “Accurate” has no defined population, measure, threshold, or method. | “For an agreed sample and as-of date, each included/excluded case follows the approved rule; exceptions are counted and reviewed by the named owners.” |
| “Make it real-time.” | “Real-time” is ambiguous and may not be feasible or needed. | “Agree the event start/end points, percentile, target, operating window, and measurement method with fraud operations.” |
| “Improve lineage.” | No evidence standard or acceptance authority. | “For the agreed in-scope fields and reports, reviewers can follow documented source-to-report lineage and identify accountable owners.” |

Do not insert numerical targets without evidence or stakeholder agreement. When the target is not yet known, write a **candidate measure**, name the person who must confirm it, and log the decision date or dependency.

### 5.7 Record conflicts and open questions

A conflict log records incompatible statements or goals without silently selecting a winner. An open-question log records missing information that could affect requirements, scope, feasibility, or decisions. Each entry should have an owner, evidence needed, due date or trigger, and impact if unresolved.

**Completed illustrative conflict log**

| ID | Conflict / competing interests | Evidence needed | Options to examine | Recommended resolution path | Owner / status |
|---|---|---|---|---|---|
| `CF-01` | Marketing asks for broad access to customer attributes; control stakeholders emphasise minimisation and controlled use | Campaign use cases, attribute-level need, applicable policies/control interpretation, access roles | Purpose-based access; curated attributes; separate views; restrict unnecessary attributes | Map each attribute to a purpose, ask control owner to clarify mandatory boundaries, then obtain decision from authorised forum | Business owner + control owner; unresolved |
| `CF-02` | Finance and risk report different customer counts; each says its number is correct | Report definitions, population filters, as-of dates, source lineage, duplicate and closure rules | Shared definition; explicitly distinct purpose-specific counts; reconciliation with documented variance | Compare definitions and use cases jointly; determine whether counts should converge or legitimately differ; decision by accountable business owners | Finance/risk owners; evidence pending |
| `CF-03` | Sponsor has a preferred technology before needs and constraints are validated | Business case, existing commitments, approved standards, cost/operability evidence | Retain as candidate; compare with other feasible option categories; separate mandatory constraint from preference | Sponsor clarifies whether it is mandatory and on what authority; architecture review evaluates alternatives against agreed criteria | Sponsor and architecture decision forum; unresolved |

**Blank conflict / open-question template**

| ID | Type | Statement or question | Affected requirement / objective | Evidence needed | Options / consequence if unresolved | Owner | Due date / trigger | Status / decision reference |
|---|---|---|---|---|---|---|---|---|
| `CF-__ / OQ-__` | Conflict / open question |  |  |  |  |  |  |  |

### 5.8 Intermediate exercise: classify three statements

Classify each statement and produce a structured requirements summary with need, requirement, source, priority, and open question.

1. Finance: “We need the same customer count as risk by Monday.”
2. Marketing: “Put every customer field in Tool X so campaigns are easier.”
3. Source engineering: “The cards platform emits batch files every 15 minutes; we cannot change the interface before the next release.”

**Worked answer**

| Statement | Classification | Underlying need / candidate requirement | Priority | Open question |
|---|---|---|---|---|
| Finance | Request plus deadline; “same count” is ambiguous | Need: comparable, explainable reporting. Candidate BR: Finance and risk must use an agreed population definition for the reporting purpose, or document justified differences. | Provisional high because it affects management reporting; confirm with sponsor and owners. | Which population, as-of date, and reporting decision? Is Monday a fixed business deadline or a preference? |
| Marketing | Solution preference (`Tool X`) plus broad request (`every field`) | Need: support defined campaign decisions with appropriate customer attributes. Candidate BR: authorised campaign users must be able to access the attributes needed for agreed use cases, subject to confirmed controls. | Provisional; assess business value and control constraints. | Which campaign use cases and attributes? Is Tool X mandatory or preferred? What access boundaries apply? |
| Source engineering | Stakeholder statement about current behaviour and a possible constraint | Candidate constraint only after verification: interface cannot change before a named release. Need: establish feasible delivery options given current source behaviour. | Not a business priority by itself; affects feasibility and schedule. | Which release/date? Is the interface limitation fixed, and who can approve an exception? |

Notice that a technical limitation can be a verified fact, a negotiable constraint, or merely a stakeholder belief. Record its source and verify its status before relying on it.

## 6. Advanced-level learning sequence

### 6.1 Resolve conflicting priorities by interests, evidence, options, and authority

A **position** is what someone says they want (“give everyone all fields”). An **interest** is the reason behind the position (“analysts need enough context to make decisions”). Positions can conflict even when interests can be satisfied together.

Use this sequence:

1. **State each position neutrally.** Do not caricature either stakeholder.
2. **Identify interests and outcomes.** Ask what decision, risk, or operational problem each position addresses.
3. **Gather evidence.** Inspect examples, definitions, process records, applicable policies, and source behaviour.
4. **Generate feasible options.** Include the status quo where useful; do not create straw-man alternatives.
5. **Evaluate options against agreed criteria.** For example, business usefulness, control fit, timeliness, operational burden, and cost—only where those criteria are relevant and accepted.
6. **Identify decision authority.** Determine who can decide each issue and which parties must advise, approve, or be consulted.
7. **Record the decision or unresolved disagreement.** Capture rationale, evidence, rejected options, consequences, owner, and review trigger.

**Example: broad marketing access versus data minimisation**

- Marketing position: broad access to customer attributes.
- Marketing interest: improve campaign selection and reduce missed eligible customers.
- Control interest: prevent unnecessary or inappropriate use and maintain evidence of authorised access.
- Evidence to collect: campaign use cases, required attributes, actual access patterns, approved policies, and control-owner interpretation.
- Candidate options: purpose-specific attribute sets, role-based views, or a governed access process. These are options to evaluate, not predetermined solutions.
- Decision path: business owner confirms campaign need; control owner clarifies applicable boundaries; authorised decision forum resolves remaining trade-offs.

Do not say “compliance wins because it is compliance” or “the sponsor wins because they are senior.” Authority and obligations matter, but must be identified specifically. A mandatory control cannot be traded away merely because it is inconvenient; the actual obligation and authorised interpretation must be established.

### 6.2 Handle ambiguity without manufacturing certainty

Words such as “single,” “current,” “complete,” “customer,” “real-time,” “accurate,” and “all” are warning signs. They may be useful shorthand in conversation but are not sufficiently precise for acceptance.

For every ambiguous term:

- write the term as used by the stakeholder;
- identify plausible interpretations;
- show a concrete example and counterexample for each interpretation;
- propose a candidate definition or measure only as a hypothesis;
- ask the accountable owner to confirm or correct it;
- record the accepted version, approver, date, and unresolved exceptions.

**Example: “single customer count”** might mean unique natural persons, customer records, customer relationships, active customers, customers with open accounts, or customers within a particular reporting population. These are different measures. A single count is not necessarily the right answer for every use case. Discovery should determine whether the organisation needs one shared definition, multiple clearly named counts, or a canonical identity plus purpose-specific populations.

### 6.3 Find hidden stakeholders and silent requirements

The first stakeholder list is rarely complete. Search systematically for people who:

- create or change the source data;
- consume reports or use downstream extracts;
- reconcile, correct, or explain discrepancies;
- operate and support systems and pipelines;
- manage access, privacy, security, compliance, risk, or audit;
- approve business definitions or own the affected capability;
- maintain the result after the project team leaves;
- are affected by data corrections, changed definitions, or changed report timing.

A practical technique is to walk through the lifecycle: **create → change → transfer → transform → consume → correct → retain/delete → investigate**. At each step ask who performs the work, who owns the rule, who is affected by failure, and who needs evidence.

“Silent requirements” are needs not stated in the initial request but necessary for a viable outcome—for example, an operator needs to detect failed refreshes, a report owner needs a documented definition, or a downstream team needs advance notice of a changed field meaning. Treat these as hypotheses until validated; do not present them as confirmed requirements merely because they seem sensible.

### 6.4 Validate requirements and record sign-off

Validation checks whether the documented statements accurately represent the need and whether the proposed success criteria would demonstrate the intended outcome. It is not simply asking “Does this look okay?”

A useful playback session:

1. restates the business problem and objectives;
2. shows scope and exclusions;
3. reads each requirement, source, and success criterion;
4. walks through examples and counterexamples;
5. highlights assumptions, conflicts, and open questions;
6. asks the named owner to confirm, correct, reject, or defer each item;
7. records the response, date, version, and follow-up owner.

**Validation record template**

| Item ID / version | Reviewer and role | Review question | Outcome (confirm / correct / reject / defer) | Evidence / comment | Action owner / due date | Date |
|---|---|---|---|---|---|---|
| `BR-__ v__` |  | Does this state the business need accurately? |  |  |  |  |
| `SC-__ v__` |  | Is this criterion observable and acceptable? |  |  |  |  |
| `SCOPE-__ v__` |  | Are the boundaries and exclusions correct? |  |  |  |  |

Sign-off should be proportionate to the significance of the item. Material business definitions, scope boundaries, and acceptance criteria should have explicit validation by the appropriate owner. A meeting invitation, lack of response, or a copied email recipient is not evidence of agreement. If an authorised reviewer is unavailable, mark the item **pending**, record the impact, and make dependent decisions conditional where necessary.

### 6.5 Establish traceability from objective to later artefacts

**Traceability** is the ability to follow a requirement backward to its business reason and source, and forward to the artefacts, decisions, and acceptance evidence that depend on it. Assign stable IDs and version changes rather than relying on informal prose alone.

**Completed illustrative traceability chain**

| ID | Type | Statement | Source / parent | Success evidence / downstream use | Status |
|---|---|---|---|---|---|
| `BO-01` | Business objective | Improve confidence in customer reporting used by finance and risk | Sponsor objective; exact wording to validate | Finance and risk approve the relevant definitions and explain differences | Draft; sponsor confirmation pending |
| `BR-01` | Business requirement | Authorised reporting teams must be able to obtain a customer count for an agreed population and as-of date using a documented definition | `BO-01`; finance and risk discovery | `SC-01`; later requirements register and modelling discussions | Draft |
| `SC-01` | Success criterion | Finance and risk owners confirm the population definition and review a sample reconciliation; each material difference has an explanation or an owner and due date | `BR-01`; finance/risk validation | Review record and sample evidence | Candidate; sample period and materiality definition open |
| `OQ-01` | Open question | Should the agreed count cover all customer records, active relationships, or a defined reporting population? | `BR-01` | Answer updates `BR-01` and `SC-01`; owner is finance/risk business owners | Open |
| `REQ-01` | Later requirement placeholder | To be elaborated in the functional/non-functional requirements topic | `BR-01` | Acceptance criteria and later design trace | Not yet defined; do not invent at this stage |

Traceability must work in both directions. If a requirement has no business objective or source, ask why it exists. If an objective has no requirement or success evidence, ask how the work will achieve it. If a requirement changes, identify affected criteria, scope, stakeholders, and downstream decisions.

### 6.6 Handle a sponsor who has already chosen a technology

Do not dismiss the sponsor's preference, but do not disguise it as a business requirement.

Ask:

- Is the technology mandatory, already contracted, part of an approved standard, or simply preferred?
- What authority or evidence makes it mandatory?
- Which business outcome does the preference serve?
- What alternatives are feasible within verified constraints?
- What would cause the preferred option to fail the business need?

Record it as a **solution preference** unless a verified commitment or constraint establishes otherwise. If it is a genuine fixed constraint, document its source, scope, owner, and consequence. Even with a fixed technology, the business requirements and acceptance criteria still need to be clear.

### 6.7 Advanced exercise: conflicting stakeholder inputs

**Inputs (fictional, illustrative):**

- Marketing: “All analysts need every customer attribute immediately.”
- Compliance: “Customer attributes should only be available for approved purposes.”
- Finance: “The customer count must match the risk count.”
- Risk: “Our count is correct; finance should change its report.”
- Sponsor: “Choose the preferred platform this week.”

Produce a conflict log with options, recommended resolution paths, and evidence needed.

**Worked reasoning**

| Issue | Interests to establish | Evidence to obtain | Options to consider | Resolution path |
|---|---|---|---|---|
| Broad versus controlled access | Campaign usefulness; approved use and minimisation | Use cases, attribute list, policies, control interpretation, access patterns | Purpose-based access, curated views, approved access workflow | Business owner specifies purpose; control owner validates boundaries; authorised forum decides remaining trade-off |
| Finance versus risk counts | Accurate reporting for each business purpose | Definitions, population filters, dates, source lineage, exclusions, reconciliation examples | Shared definition, separate named measures, reconciliation and variance explanation | Joint discovery first; each owner validates their meaning; sponsor/decision forum resolves cross-business standard if authority permits |
| Technology chosen early | Timely decision; fit to need and constraints | Existing commitments, standards, constraints, option evidence | Treat preferred platform as candidate; compare feasible categories; defer irreversible choice | Sponsor clarifies status; architecture decision authority records decision only after criteria and evidence are reviewed |

The correct result may be that some counts should match and others should differ because their business populations differ. Do not force agreement before understanding the definitions.

## 7. Industry-application exercises

Complete these exercises as if you were preparing reviewable discovery artefacts for the fictional Northbridge Bank. All scenario facts and numbers are illustrative assumptions supplied for learning, not facts about a real organisation or recommended targets.

### 7.1 Exercise A — Elicitation plan covering at least six stakeholder groups

Create an elicitation plan covering at least six groups from this set: sponsor, finance, risk, fraud operations, source-system owners/engineering, data consumers, operations, compliance, security, internal audit, marketing. For each, include:

- the business question or hypothesis to test;
- the chosen technique and why it fits;
- evidence to request;
- expected artefact;
- owner and status.

**Acceptance check:** every major objective has a relevant stakeholder, every important question has an evidence path, and no architecture option is assumed to be selected.

### 7.2 Exercise B — One-page business requirements summary for the single-customer-count problem

Write a concise summary with objective, problem, stakeholders, scope, exclusions, candidate success criteria, evidence sources, assumptions, conflicts, and open questions.

**Worked example**

> **Objective:** establish a trusted, explainable customer count for the agreed reporting purpose used by finance and risk.
>
> **Problem statement:** Northbridge Bank's finance and risk reports show different customer totals, and the teams disagree about which is correct. The causes are not yet established.
>
> **Business need:** reporting users need counts whose population, as-of date, and definition are documented, with legitimate differences explained.
>
> **Candidate business requirement `BR-01`:** authorised reporting teams must be able to obtain a customer count for an agreed population and as-of date using a documented definition.
>
> **Scope:** discovery of the customer-count use cases, current report definitions, source lineage, population rules, and business acceptance. Account and transaction data may be relevant where evidence shows they affect the definition; detailed modelling is out of scope.
>
> **Exclusions:** selecting a physical platform, detailed schema design, implementation, and migration planning.
>
> **Candidate success criterion `SC-01`:** finance and risk owners validate the agreed definition and review a sample reconciliation; every material remaining difference has an explanation or an accountable owner and due date. The sample period and meaning of “material” require confirmation.
>
> **Evidence needed:** report specifications, filters and SQL/business rules where available, reporting dates, source ownership, examples of records included/excluded, reconciliation logs, and stakeholder confirmation.
>
> **Illustrative assumptions:** Northbridge has a core banking system, cards platform, CRM, loan origination system, nightly warehouse extracts, and a data lake holding copies of some sources. The scenario assumes roughly 3 million retail customers. These details are not verified real-world facts.
>
> **Open questions:** What does “customer” mean for each report? What is the as-of date? Are closed relationships included? How are duplicates and business customers handled? Should finance and risk counts be identical for this purpose? Who approves the shared definition?

This is a starting summary, not a validated final requirement. The owner must confirm the candidate criteria and resolve open questions.

### 7.3 Exercise C — Validation-session agenda and record template

**Illustrative 60-minute agenda**

| Time | Activity | Intended output |
|---|---|---|
| 0–5 min | Confirm objective, attendees, roles, and decisions in scope | Shared purpose and decision boundaries |
| 5–15 min | Review problem statement, goals, scope, exclusions | Corrections and scope confirmation |
| 15–30 min | Walk through candidate requirements and success criteria | Per-item confirm/correct/reject/defer status |
| 30–40 min | Compare finance and risk definitions using examples | Differences, evidence gaps, candidate resolution options |
| 40–50 min | Review control, operational, source, and downstream stakeholders | Missing needs and constraints to validate |
| 50–57 min | Review conflicts and open questions with owners | Action list, owners, dates, decision forum |
| 57–60 min | Read back decisions and unresolved items | Accurate record of outcomes and next steps |

**Record template**

```markdown
# Requirements validation session
- Session ID / date:
- Facilitator / note-taker:
- Attendees and roles:
- Requirements version reviewed:
- Decision authority present? If not, what remains pending?

## Confirmed items
| ID | Item / version | Confirmed by | Evidence / comments | Date |
|---|---|---|---|---|

## Corrections / rejections / deferrals
| ID | Previous wording | Requested change / reason | Owner | Due date | Status |
|---|---|---|---|---|---|

## Decisions
- Decision:
- Decision-maker / authority basis:
- Options considered:
- Rationale / evidence:

## Open questions and conflicts
| ID | Question / conflict | Owner | Evidence needed | Due date / trigger |
|---|---|---|---|---|

## Follow-up
- Updated version to circulate by:
- Reviewers who must respond:
- Items that remain conditional:
```

### 7.4 Exercise D — Three practical scenarios

**Scenario 1: Marketing asks for “all customer data in one place.”** Identify at least four questions before accepting it as a requirement.

Good questions include:

1. Which decisions or campaign use cases are failing today?
2. What does “customer” mean for those use cases, and which populations are included or excluded?
3. Which specific attributes are needed, and what evidence supports that need?
4. Who will use the data, and what access or approved-use boundaries apply?
5. What does “one place” mean to the stakeholder, and is that a preference or a genuine constraint?
6. What freshness, quality, and availability are needed for the decisions?
7. What observable evidence would show that campaign coverage improved?

**Scenario 2: Risk and finance report different customer counts, and each insists its number is correct.**

Do not decide which team is right based on seniority or confidence. Collect both report definitions, population filters, as-of dates, inclusion/exclusion rules, source lineage, and sample records. Compare like with like. Determine whether the counts are intended to measure the same population. Record the result as a confirmed shared definition, two purpose-specific definitions, or an unresolved conflict with a decision owner. A valid outcome may be that the counts differ for legitimate reasons.

**Scenario 3: A key stakeholder is unavailable until after the design deadline.**

Record the stakeholder, the requirement or decision affected, the reason their input is necessary, the evidence already available, the assumptions temporarily used, the impact of proceeding without confirmation, and the date or event that will trigger review. Make dependent decisions conditional if the missing input could change them. Do not record non-response as sign-off. If a decision must proceed, the authorised decision-maker should explicitly accept the uncertainty and document the basis.

### 7.5 Exercise E — Hidden-stakeholder review

Take the initial sponsor/finance/risk list and trace the data/report lifecycle. For each stage—source creation, source change, transfer, transformation, report consumption, correction, support, and assurance—identify who performs the work, who owns the rule, who is affected by failure, and who needs evidence.

**Expected output:** an updated stakeholder register with new candidates, why each matters, how to contact them, and whether their role/authority is confirmed. Do not assume every candidate has a formal approval right.

### 7.6 Exercise F — Sponsor technology preference

The sponsor says, “We have decided to use Platform X; write the requirements around it.” Write a response plan, not a confrontational reply. It should classify the statement, ask what makes the platform mandatory, identify the business outcomes still to validate, and specify how the preference will be recorded and evaluated.

**Expected reasoning:** Platform X is a solution preference unless a verified commitment, standard, or constraint makes it mandatory. Clarify the authority and evidence, capture the business need separately, and avoid making unexamined technology choices look like requirements.

## 8. Practical scenarios and case-based reasoning

### 8.1 Northbridge Bank: working context

Northbridge Bank is a fictional mid-sized retail and business bank. The supplied roadmap scenario assumes it has a core banking system, a separate cards platform, a CRM, and a loan origination system. Nightly extracts feed an enterprise data warehouse; a data lake created three years ago holds copies of some sources. Risk, finance, marketing, and compliance report different customer counts. Fraud analysts see card transactions hours after the fact. A regulator has requested clearer evidence of data lineage and customer data accountability within a stated period.

The scenario's initial assumptions include about 3 million retail customers, about 2 million card transactions per average day, card-platform batch files every 15 minutes today, seven-year retention for transaction records, and a sponsor-set programme budget ceiling. The scenario's stated illustrative constraints include a required data jurisdiction, a core-banking batch window ending at 02:30, use of the existing identity provider, and a regulatory milestone date. These are all illustrative teaching details. A real project would verify the actual source, authority, definitions, and dates.

For this lesson, focus on discovery and business requirements. Do not drift into detailed schema design, vendor selection, implementation, migration plans, or detailed cost negotiation. Later architecture modules handle those decisions.

### 8.2 Case: why do the customer counts differ?

Start with competing hypotheses, not a conclusion.

| Hypothesis | Evidence that could support or disprove it | Stakeholder / owner to involve |
|---|---|---|
| Different population definitions | Report filters, definitions, inclusion/exclusion rules | Finance and risk report owners |
| Different as-of dates or refresh times | Report timestamps, refresh logs, reporting calendar | Report owners and operations |
| Duplicate identities or different identifiers | Source key definitions, duplicate examples, identity rules | Source owners and business data owners |
| Different treatment of closed or inactive relationships | Business rules and representative records | Finance, risk, retail/business owners |
| Source-data quality defects | Reconciliation records, quality reports, sample records | Source owners and data-quality operators |
| Different purpose-specific meanings of “customer” | Use-case descriptions and approved metric definitions | Business owners and sponsor/decision forum |

**Reasoning procedure:**

1. Capture each report's stated definition verbatim and identify its owner.
2. Collect the report version, run/as-of date, filters, and relevant source references.
3. Compare definitions and run a sample-based reconciliation, if authorised and available.
4. Separate confirmed causes from hypotheses and unknowns.
5. Ask whether the business truly requires one shared count or several clearly named measures.
6. Propose candidate outcomes and success criteria for the relevant owners to validate.
7. Record unresolved differences and the decision authority responsible for the shared business definition, if one is needed.

**Do not conclude:** “Risk is right,” “Finance is wrong,” or “a new platform will fix it” without evidence.

### 8.3 Case: fraud signals arrive hours after the fact

The known scenario says fraud analysts see card transactions hours after the fact, while the current cards platform is assumed to emit batch files every 15 minutes. Do not infer a precise end-to-end delay from that statement: the total delay may include source creation, file creation, transfer, ingestion, processing, and case-tool availability.

Discovery questions include:

- Which fraud decisions depend on the transaction, and what is the consequence of late visibility?
- What event defines the start of the measurement: authorisation, posting, file creation, or another timestamp?
- What event defines availability: receipt, validated ingestion, or visibility in the case tool?
- Which business hours, transaction types, and exceptional conditions are in scope?
- What target and percentile would be useful, and who can approve it?
- What source/interface limitations are verified, and who can confirm whether they are fixed or negotiable?
- What evidence can be collected from timestamps, logs, and analyst workflow?

The outcome of this topic is a validated business need and a measurable candidate requirement, not a premature streaming design. For example, a candidate requirement could state that fraud analysts need a transaction to be visible in the case tool within an agreed interval measured from an agreed source event. The actual interval, percentile, operating window, and acceptance method remain open until confirmed.

### 8.4 Case: a key stakeholder is unavailable

Assume the compliance officer cannot attend until after the design deadline. This is an illustrative scenario, not a claim about a real person.

Document:

- which requirements and decisions depend on the compliance interpretation;
- the specific question and evidence needed;
- what existing documents are available and their version/owner;
- the temporary assumption, confidence, and consequences if it is wrong;
- which decisions can safely proceed and which must remain conditional;
- who is authorised to accept the residual uncertainty, and when the item must be revisited.

Do not claim that the work is compliant based on silence or a second-hand interpretation. A decision can proceed only within the decision-maker's authority and with the uncertainty explicitly accepted; a mandatory obligation cannot be waived by an unauthorised project decision.

### 8.5 Worked example: convert a vague statement into a traceable requirement

**Initial statement:** “We need a single customer view as soon as possible.”

**Step 1 — Record the source statement.** Preserve the exact wording, speaker, role, date, and context. Classify it as a request, not yet a complete requirement.

**Step 2 — Elicit the need.** Ask which decisions are failing, who uses the view, which customer population is meant, and what “as soon as possible” means in business terms.

**Step 3 — Draft the business requirement.**

> `BR-EX-02 (candidate):` Authorised users in the agreed reporting groups must be able to obtain a customer view for the agreed business purpose, with the population definition and as-of time visible to the user.

This remains a candidate because “agreed reporting groups,” “business purpose,” and the population definition need confirmation.

**Step 4 — Draft a success criterion.**

> `SC-EX-02 (candidate):` Named business owners confirm the population definition and intended consumers; a representative set of use cases is reviewed against the resulting view; exceptions and unavailable attributes are recorded with owners.

This is observable but may not yet be sufficient for final acceptance. The owners must specify the representative cases and what level of coverage is acceptable.

**Step 5 — Trace and record open questions.**

| ID | Item | Link | Status |
|---|---|---|---|
| `BO-EX-02` | Improve decision-making using consistent customer information | Source: sponsor/business owner statement; confirm exact objective | Draft |
| `BR-EX-02` | Provide an agreed customer view for authorised users and purpose | `BO-EX-02`; originating request recorded in `INT-__` | Candidate |
| `SC-EX-02` | Owner-confirmed definition and use-case review with exceptions tracked | `BR-EX-02` | Candidate; acceptance detail open |
| `OQ-EX-02` | Which populations, users, attributes, and freshness needs apply? | `BR-EX-02`, `SC-EX-02` | Open; assign business owner |

**Step 6 — Validate.** Playback the wording and ask the named business owner to confirm, correct, reject, or defer it. Update the version and record the response. Do not mark the item approved before that response exists.

## 9. Expected outputs and deliverables

The lesson's required outputs are four primary artefacts plus practice-question answers. Keep them short, current, versioned, and traceable.

### 9.1 Deliverable checklist

- [ ] **Stakeholder register** with role, interest, influence, decision rights, attitude/concern, communication preference, and status of confirmation.
- [ ] **Interview / elicitation plan** that covers the required stakeholder groups and explains method, evidence, and intended output.
- [ ] **Hypothetical interview record** that preserves verbatim statements separately from classification and analysis.
- [ ] **Business requirements summary** with objective, problem, scope, exclusions, observable candidate success criteria, evidence, assumptions, and open questions.
- [ ] **Conflict and open-questions log** with affected items, evidence needs, options or consequences, owners, dates/triggers, and status.
- [ ] **Validation agenda and record template** showing how confirmation, correction, rejection, deferral, and sign-off will be captured.
- [ ] **Traceability chain** linking business objectives to requirements and candidate acceptance evidence.
- [ ] **Answers to Topic 1 practice questions**, corrected after review.

### 9.2 Reusable business requirements summary template

```markdown
# Business Requirements Summary — [Problem / Initiative]
- Document ID / version:
- Owner / last updated:
- Status: Draft / In review / Validated / Superseded

## Business objective(s)
- BO-01:

## Business problem and evidence
- Current situation:
- Evidence reviewed (source, owner, version/date):
- What is verified versus reported or inferred:

## Stakeholders and decision rights
- Sponsor:
- Business owners / validators:
- Producers / consumers / operators:
- Control functions:
- Decision forum and authority basis:

## Needs and candidate business requirements
| ID | Need | Requirement | Source | Priority / rationale | Success criterion | Status |
|---|---|---|---|---|---|---|

## Scope and boundaries
- In scope:
- Out of scope:
- Population / process / time / organisational boundaries:

## Assumptions and constraints
| ID | Type | Statement | Source / confidence | Owner | Validation action / date |
|---|---|---|---|---|---|

## Conflicts and open questions
| ID | Issue | Evidence needed | Owner | Due date / trigger | Impact if unresolved |
|---|---|---|---|---|---|

## Validation and sign-off
| Item / version | Validator / authority | Outcome | Evidence / comments | Date |
|---|---|---|---|---|

## Change history
| Version | Change | Reason / source | Approved or reviewed by | Date |
|---|---|---|---|---|
```

### 9.3 Minimal requirements quality check

Before circulating a requirement, check:

- **Necessary:** can you explain which business objective or need it supports?
- **Source-backed:** is the stakeholder, document, observation, or other evidence recorded?
- **Clear:** are key terms and population boundaries defined or explicitly open?
- **Solution-neutral:** does it state the outcome rather than prematurely prescribe a technology?
- **Observable:** can a reviewer determine whether it is satisfied?
- **Owned:** is there a named person or role responsible for validation?
- **Traceable:** can it be followed to its objective and forward to acceptance evidence or later artefacts?

For this topic, a success criterion can remain a candidate while discovery is in progress, but it must be labelled as such. Do not claim a final validated requirement if important definitions, authority, or acceptance conditions are unresolved.

## 10. Common mistakes and misconceptions

| Mistake | Why it fails | Better practice |
|---|---|---|
| Recording solutions as requirements | It narrows options before the need and constraints are understood | Keep the original request, classify the preference, then state the underlying need separately. |
| Interviewing only the sponsor | Sponsors may not know source semantics, operational failure modes, consumer needs, or control details | Follow the lifecycle and involve producers, consumers, operators, and control functions. |
| Treating silence as agreement | No response may mean absence, overload, disagreement, or lack of authority | Record pending status, follow up, and keep dependent decisions conditional where necessary. |
| Writing success criteria as activities | A completed deliverable does not prove business value | Define observable outcomes, measurement/evidence, scope, and acceptance owner. |
| Resolving conflicts by seniority | Authority may be unclear; the most senior person's view may not settle definitions or controls | Identify interests, evidence, decision rights, feasible options, and the proper forum. |
| Failing to record who confirmed a requirement | Reviewers cannot know whether wording is accepted or merely drafted | Record item/version, validator, role/authority, outcome, evidence, and date. |
| Treating a stakeholder statement as verified fact | Confidence or status does not prove the claim | Label it as a statement and request supporting evidence. |
| Hiding assumptions in prose | Later readers may mistake them for commitments | Maintain an assumption record with owner, confidence, impact, and validation action. |
| Treating every disagreement as a defect | Different business purposes may legitimately require different measures | Compare definitions and use cases before deciding that counts must match. |
| Using vague words without a definition | “All,” “current,” “accurate,” “fast,” and “single” can mean different things | Ask for boundaries, examples, candidate measures, and explicit confirmation. |
| Confusing influence with decision authority | A person may shape a decision without being authorised to approve it | Record the decision right and verify its basis. |
| Over-documenting without analysis | Long notes can still fail to identify the real need or unresolved question | Keep concise records that support a decision, with source and traceability. |
| Treating an assumption as a constraint | A temporary belief can unnecessarily eliminate viable options | Verify who set the boundary and whether it is fixed, negotiable, or merely preferred. |
| Making up a numerical target to look rigorous | An unsupported target creates false precision and may misdirect architecture | Record a candidate metric, owner, evidence needed, and status until validated. |
| Designing before the requirement is understood | Design choices can anchor later discussion and obscure alternatives | Delay irreversible choices until the need, constraints, and acceptance conditions are sufficiently clear. |

## 11. Mastery criteria

You have mastered this topic when you can demonstrate the following without relying on memorised definitions alone.

### 11.1 Conceptual mastery

- [ ] Distinguish a request, underlying need, business requirement, constraint, assumption, solution preference, and success criterion, including when one statement contains multiple categories.
- [ ] Explain why a dashboard or a platform is a solution request rather than a complete business requirement.
- [ ] Identify the roles of sponsors, decision-makers, business owners, data producers, data consumers, operators, and control functions.
- [ ] Explain the strengths and limitations of interviews, workshops, questionnaires, document analysis, and observation.

### 11.2 Practical mastery

- [ ] Produce a stakeholder list and at least five strong open questions from a short request.
- [ ] Produce a stakeholder register and an elicitation plan covering at least six stakeholder groups for Northbridge Bank.
- [ ] Capture a hypothetical interview with verbatim statements separate from analysis.
- [ ] Map requirements to objectives, capabilities/processes, domains, producers, consumers, and validators.
- [ ] Produce a business requirements summary with scope, exclusions, candidate observable success criteria, sources, and explicit open questions.
- [ ] Maintain a conflict/open-question log with owners and evidence needs.
- [ ] Prepare a validation agenda and record who confirmed what, in which version, and when.
- [ ] Trace every important requirement to a business objective and forward to acceptance evidence or a clearly marked later artefact.

### 11.3 Advanced judgement

- [ ] Frame a disagreement by underlying interests rather than taking positions at face value.
- [ ] Identify hidden stakeholders and silent requirements without presenting hypotheses as confirmed facts.
- [ ] Explain which decisions should remain conditional when a key stakeholder is unavailable.
- [ ] Challenge a sponsor's technology preference respectfully and determine whether it is mandatory or negotiable.
- [ ] Defend a recommendation using evidence, options, decision authority, and explicit uncertainty—not seniority or assumption.

### 11.4 Roadmap progression checks

The module roadmap defines these cumulative transitions:

- **Beginner → Intermediate:** classify at least 90% of provided example statements correctly without notes and explain each category in your own words.
- **Intermediate → Advanced:** analyse a scenario and produce a requirements set with units where relevant, assumptions, and sources; a reviewer should find no unmeasurable “must” statements.
- **Advanced → Industry application:** defend one recommendation against two reviewer challenges, citing criteria, evidence, and sensitivity. For this topic, focus the defence on stakeholder evidence, interests, open questions, and decision authority.
- **Industry application → Complete:** meet the completion gate below, and have a reviewer who did not perform the work agree that the evidence supports the conclusions.

## 12. Completion gate

Do not mark this topic complete merely because you have read it. Complete the artefacts, correct the practice questions, and have the work reviewed.

- [ ] Stakeholder register and elicitation plan reviewed; stakeholder coverage and decision rights are explicit, and unverified roles are labelled.
- [ ] Requirements summary includes objectives, source, scope, exclusions, candidate success criteria, and open questions; no solution is presented as a business requirement without being labelled and justified.
- [ ] Success criteria are observable. Any target or definition that is not yet agreed is explicitly marked as a candidate/open question rather than asserted as validated.
- [ ] Conflict log is complete with affected requirements, interests, options or consequences, owners, and evidence needs.
- [ ] Interview record preserves verbatim statements separately from classification and interpretation.
- [ ] Validation record shows who confirmed, corrected, rejected, or deferred each material item and when; silence is not treated as agreement.
- [ ] Traceability is demonstrated from business objective to requirement and success evidence, with unresolved links recorded as open items.
- [ ] Northbridge single-customer-count exercise is complete, including evidence needed to determine why finance and risk counts differ.
- [ ] Industry exercises are complete: six-group elicitation plan, one-page requirements summary, validation agenda/record, and practical scenario responses.
- [ ] Topic 1 practice questions are answered and corrected. If a separate repository `practice-questions.md` is empty or unavailable, use the questions and exercises in this lesson and record that limitation; do not claim to have reviewed absent questions.
- [ ] A reviewer challenges the work; corrections are incorporated and the final version is recorded with its validation status.

**Completion standard:** a reviewer who did not create the artefacts can trace each material requirement to its business reason and source, see what is verified versus assumed or unresolved, understand who has authority to validate it, and determine how success will be observed. If not, keep the topic open and address the evidence gap before moving on.
