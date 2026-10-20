# Governance Operating Model and Accountability

**Stage:** 2D — Data Architecture  
**Module:** 10 — Data Governance, Security, Privacy and Compliance  
**Lesson:** 01  
**Target path:** `10-Data-Governance-Security-Privacy-and-Compliance/01-governance-operating-model-and-accountability.md`  
**Learning progression:** Beginner → Intermediate → Advanced

> **Scope and source note.** The module roadmap identifies this lesson as the first topic and sets the learning objectives, prerequisite dependencies, recommended progression, exercises, deliverables, mastery criteria, and completion gate used here. The roadmap explicitly says the topic files were empty when it was written; therefore, the detailed explanations, tables, Northbridge examples, templates, and numeric targets in this lesson are instructional recommendations, not claims about pre-existing requirements. The companion repository tree confirms the target filename under `Stage 2D — Data Architecture/10-Data-Governance-Security-Privacy-and-Compliance/`.
>
> **Educational and legal caution.** This material teaches architecture and control-design skills; it is not legal advice and does not establish that an organisation complies with any law, regulation, contract, or standard. Qualified legal, privacy, security, risk, and compliance specialists must interpret applicable obligations for the relevant organisation and jurisdiction.

---

## 1. Topic overview: why governance needs an operating model

### 1.1 What is data governance?

**Data governance** is the system of decision rights, accountabilities, policies, and processes that determines how an organisation's data are defined, owned, protected, used, shared, and retired. It answers four basic questions:

1. **Who decides?** Which role has authority to make or approve a decision?
2. **Who does the work?** Which role performs the activity and maintains the records?
3. **What rules apply?** Which policies, standards, and constraints govern the activity?
4. **How can we tell it worked?** What observable evidence demonstrates that the decision or control operated?

A **governance operating model** makes these questions operational. It defines roles, decision rights, forums, escalation paths, policy ownership, service expectations, and measures. It is not merely an organisation chart or a committee calendar.

### 1.2 Why it matters in a production data platform

A modern data platform may ingest data from operational systems, transform it into lakehouse or warehouse layers, publish data products, and serve dashboards, machine-learning features, and AI retrieval systems. Many teams may use the same data for different purposes. Without explicit accountability:

- no one may be authorised to decide whether a new use is appropriate;
- a platform engineer may be asked to approve business access without enough context;
- policies may be published but never implemented in access controls or pipelines;
- a dataset may have no owner after a reorganisation;
- an exception may remain open indefinitely;
- audit or incident responders may be unable to determine who decided what, when, and why.

The architecture consequence is direct: **a control needs a defined decision owner, an implementer, a monitoring path, and evidence**. Governance establishes these responsibilities; later lessons translate them into classification, access, encryption, privacy, retention, evidence, and policy-enforcement designs.

### 1.3 Governance and adjacent functions

| Function | Core question | Typical contribution | Example output |
|---|---|---|---|
| Data governance | Who is accountable, and what rules govern data? | Decision rights, role model, policy lifecycle | Operating model, responsibility matrix |
| Information security | How is data protected from unauthorised access, change, or loss? | Security standards, threat and control advice, monitoring | Access-control requirements, incident procedures |
| Privacy | Are personal data used appropriately for stated purposes, with relevant rights and constraints addressed? | Privacy advice and assessments | Purpose records, minimisation requirements |
| Risk management | What could go wrong, how severe is it, and who may accept residual risk? | Risk assessment and risk-acceptance framework | Risk register, acceptance record |
| Legal and compliance | Which obligations or commitments may apply, and how are they interpreted and evidenced? | Specialist interpretation, obligations mapping | Requirement/control mapping, compliance advice |
| Internal audit | Are controls designed appropriately and operating as intended? | Independent assurance within its mandate | Audit findings and test results |
| Data/platform engineering | How are approved requirements implemented and operated? | Technical implementation, monitoring, operational evidence | Policies in code/configuration, runbooks, logs |

These functions collaborate but are not interchangeable. A governance council does not replace legal advice; a security control does not decide whether a business purpose is appropriate; and a policy document does not prove that the control operated.

### 1.4 Learning objectives and expected outcomes

By the end of this lesson, you should be able to:

1. Define data owner, data steward, custodian/platform operator, policy owner, approver, data consumer, governance council, and specialist control functions.
2. Distinguish ownership of a data asset, operation of the platform, access approval, and policy definition.
3. Build a responsibility matrix for governance decisions and identify accountability gaps.
4. Design strategic, tactical, and operational governance structures.
5. Compare centralised, decentralised, and federated models and explain when each is suitable.
6. Define a policy lifecycle, governance forums, decision logs, and time-boxed escalation paths.
7. Apply separation of duties and define risk-acceptance boundaries, records, and expiry.
8. Propose observable governance effectiveness measures and operating-effectiveness evidence.
9. Handle conflicting ownership, orphaned assets, organisational change, and governance scaling.
10. Document an operating model decision in an architecture decision record (ADR).

### 1.5 Prerequisites

The module roadmap identifies P1–P3 as prerequisites for this topic, plus the multi-team isolation and tenant-boundary material from the enterprise data platform module.

| Prerequisite | Why it matters here | Review activity if needed |
|---|---|---|
| Business capabilities, domains, ownership, governance lifecycle, decision rights | Governance must align with business accountability and data domains | Draw a RACI for ten data decisions |
| Architecture principles, quality attributes, exceptions | Governance creates trade-offs and exception paths | Write a bounded exception record |
| Constraints, assumptions, risks, trade-offs, ADRs | Decisions need rationale, consequences, and traceability | Classify 15 statements and write a short ADR |
| Tenant ownership and multi-team isolation | Shared platforms need boundaries between teams and domains | Identify owner, consumer, and platform boundary for a shared data product |

Other useful prerequisites include basic data modelling and dictionaries, storage lifecycle and replication, data contracts and lineage, platform metadata, cloud identity, and streaming retention. They are especially relevant when the operating model is connected to implementation.

### 1.6 Terms to know

| Term | Plain-language definition |
|---|---|
| Data asset | A dataset, table, stream, report, data product, feature set, or other managed data resource |
| Data owner | The role accountable for an asset's business meaning, appropriate use, and specified governance decisions |
| Data steward | The role that maintains definitions, quality rules, metadata, and classification records on an ongoing basis |
| Data custodian / platform operator | The role that operates the systems and implements approved controls |
| Policy owner | The role accountable for maintaining a policy's content, review cycle, and proposed changes |
| Decision right | Explicit authority to make, approve, or resolve a defined class of decision |
| RACI | A responsibility-mapping technique: Responsible, Accountable, Consulted, Informed |
| Exception | A documented, bounded departure from a normal policy or control, approved by an authorised role |
| Residual risk | Risk remaining after controls have been applied |
| Executive risk acceptance authority | The formally designated role permitted to accept specified residual risk within documented limits |
| Evidence | A record that supports a claim that a decision, review, or control activity occurred |
| Orphaned asset | An asset with no current, valid, named owner or accountable delegate |

---

## 2. Beginner level — roles and basic decision rights

### 2.1 The essential roles

Role names vary by organisation. The important part is to define the authority and duties, not to insist on a particular title. A person may hold multiple roles in a small organisation, but the roles and any conflicts must still be explicit.

| Role | What the role does | What the role should not silently absorb |
|---|---|---|
| **Data owner** | Is accountable for the asset's business meaning, approved uses, risk context, quality expectations, and access decisions assigned to the owner | Running the platform; unilaterally redefining enterprise policy; accepting risk beyond delegated authority |
| **Data steward** | Maintains business definitions, metadata, data-quality rules, classification records, lineage context, and issue follow-up | Making high-impact risk decisions without authority; substituting metadata completeness for business approval |
| **Data custodian / platform operator** | Runs storage, pipelines, catalogues, identity integrations, logging, backups, and technical controls; implements approved decisions | Deciding business purpose or granting itself authority to approve all data access |
| **Policy owner** | Drafts and maintains a policy, coordinates review, tracks versions, and proposes revisions | Approving their own policy where an independent approval is required by the organisation's governance design |
| **Access approver** | Determines whether a defined requester, purpose, scope, and duration meet the access criteria; may be the data owner or a formally delegated role | Treating technical ability to grant access as business authority to approve it |
| **Data consumer** | Requests and uses data for an approved purpose, follows handling requirements, and reports misuse or defects | Reusing data for a materially different purpose merely because access exists |
| **Governance council** | Sets cross-domain direction, resolves escalations within its mandate, approves delegated standards or decisions, and monitors governance performance | Becoming the default approver for every routine request |
| **Security function** | Defines or advises on security requirements, threat controls, incident response, and security risk | Owning business meaning or authorising business purpose by itself |
| **Privacy function** | Advises on privacy requirements and assessment, purpose and minimisation questions, and privacy risk | Replacing the accountable business decision-maker or qualified legal interpretation where required |
| **Legal / compliance specialists** | Interpret applicable obligations and contractual commitments within their remit; advise on evidence and control expectations | Being treated as the operational implementer of every technical control |
| **Risk function** | Defines risk methods, challenges assessments, and advises on acceptance authority and limits | Accepting every risk on behalf of the business regardless of delegated authority |
| **Executive risk acceptance authority** | Accepts residual risk only where formally delegated and where the risk is permitted to be accepted | Treating a committee title or RACI assignment as sufficient authority; waiving a non-waivable requirement |
| **Internal audit** | Provides independent assurance according to its mandate | Designing and operating the control it later needs to independently assess |

### 2.2 Four responsibilities that must not be confused

These four concepts are related, but they answer different questions.

| Responsibility | Question | Typical accountable role | Typical execution |
|---|---|---|---|
| **Data ownership** | What does this asset mean, which uses are appropriate, and what business risk is involved? | Data owner | Owner sets expectations; steward maintains metadata and issue records |
| **Platform operation** | Is the system reliable, secure, and configured to implement approved rules? | Platform/service owner under the technology operating model | Platform engineers operate services and deploy controls |
| **Access approval** | May this requester use this asset for this purpose, scope, and period? | Data owner or formally delegated access authority | Approver decides; identity/platform team provisions and records access |
| **Policy definition** | What general rule should apply across a defined scope? | Policy owner for content; designated authority approves it | Policy owner drafts; specialists review; approver authorises; platform teams implement |

**Example:** A platform engineer can create a role that technically permits a user to read a customer table. That technical ability does not prove that the user has a valid business purpose. The data owner or delegated access authority decides whether access is appropriate; the platform team implements the decision; controls log the change; and monitoring checks that access remains appropriate.

### 2.3 Simple mental model

A library analogy is useful:

- The **data owner** is accountable for the content's meaning and permitted uses.
- The **steward** maintains the catalogue entry and helps keep descriptions accurate.
- The **platform operator** maintains the building and its systems.
- The **policy owner** maintains the library's rules for handling material.
- The **access approver** decides whether a particular request meets the rules.
- The **governance council** resolves cross-library conflicts and sets common direction.

The analogy is imperfect: in a data platform, data may be copied, transformed, joined, cached, or embedded in AI systems. The operating model must therefore define how ownership and controls follow derived assets and replicas.

### 2.4 Beginner exercise: assign ten decisions

For each decision below, name the role with authority to decide, the role doing the work, and the role that should be consulted. Do not answer “the team” without naming a role.

1. Approve an analyst's request to read a restricted customer dataset.
2. Define the enterprise classification policy.
3. Maintain the business definition of `customer_status`.
4. Deploy an approved access rule to a production platform.
5. Propose a change to retention rules.
6. Decide whether a business use has an acceptable purpose.
7. Respond to a suspected platform compromise.
8. Review an exception that is about to expire.
9. Resolve a dispute between two domains over a shared attribute.
10. Test whether access reviews actually occurred as scheduled.

**Expected learning result:** your answers should distinguish decision authority from execution and independent assurance. There can be legitimate organisational variants; document the assumptions and delegated authority rather than treating one title as universal.

---

## 3. Intermediate level — operating-model structure

### 3.1 Strategic, tactical, and operational layers

A scalable model separates enterprise direction from domain coordination and day-to-day work.

```text
STRATEGIC
Enterprise Data Governance Council
  - Sets direction and minimum enterprise rules
  - Resolves material cross-domain disputes within delegated authority
  - Reviews risk themes, exceptions, and effectiveness
                |
                v
TACTICAL
Domain governance forums / policy working groups
  - Translate enterprise rules into domain practices
  - Resolve routine cross-team definition and quality issues
  - Propose standards, changes, and exceptions
                |
                v
OPERATIONAL
Data owners, stewards, platform operators, access approvers
  - Maintain asset records and classifications
  - Process requests and issues
  - Implement controls, reviews, and evidence capture
                |
                v
TECHNICAL ENFORCEMENT AND EVIDENCE
Catalogues, metadata, identity/access controls, pipelines, logs, review records
```

The arrows represent escalation and feedback, not a requirement that every decision pass through every layer. Routine, low-risk decisions should be made at the lowest competent level within delegated authority. Enterprise forums should focus on shared rules, material conflicts, and exceptions that exceed local authority.

### 3.2 Governance models: centralised, decentralised, and federated

These are operating patterns, not labels that automatically guarantee good governance.

| Model | Decision pattern | Advantages | Risks / limitations | Suitable conditions |
|---|---|---|---|---|
| **Centralised** | A central governance function makes most policy and domain decisions | Strong consistency, clear enterprise view, easier standardisation | Bottlenecks, distance from business context, slower local delivery, central team becomes overloaded | Small or highly standardised estate; strong need for uniform decisions; limited domain variation |
| **Decentralised** | Each domain defines and operates much of its own governance | Local context, speed, strong domain ownership | Inconsistent definitions, duplicated effort, incompatible controls, disputes over shared data | Domains are genuinely independent, risk is manageable, and interoperability needs are limited |
| **Federated** | Enterprise defines common principles and minimum controls; domains make delegated decisions within those boundaries | Balances consistency with local context; scales across domains | Requires explicit decision boundaries, good metadata, escalation discipline, and periodic conformance checks | Multiple domains share a platform and enterprise-wide interoperability/security requirements coexist with local needs |

**Recommended instructional default for the fictional Northbridge Bank:** a federated model. This is an illustrative design choice, not a roadmap mandate. The enterprise council sets minimum rules and risk boundaries; domains own business meaning and routine decisions; platform teams enforce approved rules; specialist functions advise or approve within their mandates.

#### Selection criteria

Choose a model by examining:

- number of domains, teams, and shared data products;
- regulatory, contractual, security, and privacy risk (as assessed by qualified functions);
- need for consistent enterprise definitions and controls;
- degree of legitimate variation between business domains;
- decision volume and expected turnaround time;
- maturity of metadata, identity, workflow, and monitoring systems;
- staffing and authority available to domain owners and stewards;
- ability to detect and remediate deviations from enterprise rules.

A hybrid is normal. For example, policy definition may be central, while asset-level classification and access decisions are federated within approved rules.

### 3.3 Decision rights: design before drawing the RACI

A **decision right** states who may make a decision and under what conditions. Before building a matrix, define:

1. **Decision object:** what exactly is being decided (e.g., access to a specific dataset for a stated purpose and duration).
2. **Scope:** which domains, assets, users, environments, and risks are covered.
3. **Authority:** which role may approve, reject, or escalate.
4. **Criteria:** which policy, business purpose, classification, and risk criteria apply.
5. **Delegation:** who may act when the primary role is unavailable, and within what limits.
6. **Evidence:** what record captures the request, decision, rationale, approver, and expiry/review date.
7. **Challenge path:** how a disputed or exceptional decision is reviewed.

Without these definitions, a RACI can look complete while authority remains ambiguous.

### 3.4 RACI: meaning and safe use

RACI is a practical responsibility-mapping technique, not a legal requirement and not a substitute for an organisation's formal authority, policy, or delegation framework.

- **R — Responsible:** performs or coordinates the work. More than one role may be responsible if tasks are separable.
- **A — Accountable:** owns the outcome and is the final decision authority for that defined activity. For this lesson's example, each row has **exactly one A** to make accountability unambiguous.
- **C — Consulted:** gives input before the decision or action; communication is usually two-way.
- **I — Informed:** receives the outcome; communication is usually one-way.

RACI is not an automatic approval workflow. The accountable role must have real authority, capacity, and access to the information needed to decide. If an organisation's governance rules require joint approval for a specific matter, document that formal decision rule, quorum, and tie-break route outside the RACI while retaining one named accountable role for coordinating and owning the decision record. For the worked example below, each row has one A; specialist reviews and separate risk-acceptance gates are represented explicitly where required.

### 3.5 Worked RACI example — Northbridge Bank customer domain

**Illustrative assumptions:** Northbridge Bank is fictional. It has six domains using a shared customer data product. The customer dataset contains synthetic contact details and account relationship attributes. The enterprise council has delegated authority to approve enterprise data policies; the Customer Domain Owner is authorised to make routine business-use and access decisions for the customer data product; the Security Lead owns security standards; the Privacy Lead provides privacy review; the Platform Operations Lead owns technical implementation. The matrix is an instructional example, not a claim about any real bank or legal obligation.

**Role abbreviations**

- **GC:** Enterprise Data Governance Council
- **DO:** Customer Domain Data Owner
- **ST:** Customer Data Steward
- **PO:** Enterprise Policy Owner
- **PL:** Platform Operations Lead
- **SEC:** Security Lead
- **PRIV:** Privacy Lead
- **RISK:** Enterprise Risk Lead (risk-method advice and independent challenge; not automatically the risk-acceptance decision-maker)
- **ERA:** Designated Executive Risk Acceptance Authority, explicitly named in the organisation's delegation framework
- **CONS:** Requesting Data Consumer / product team
- **AUD:** Internal Audit

**Authority boundary:** the Enterprise Data Governance Council may approve a policy exception only within its written mandate. That approval does not, by itself, accept residual risk. Where the exception requires risk acceptance, the designated risk owner/authority must separately accept that risk within formally delegated limits; the Risk function advises and challenges but does not automatically accept business risk. No role can waive a non-waivable legal, regulatory, contractual, or policy constraint merely by approving an exception.

| Decision / activity | GC | DO | ST | PO | PL | SEC | PRIV | RISK | ERA | CONS | AUD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Approve enterprise data governance policy | A | C | I | R | C | C | C | C | I | I | I |
| Maintain customer data definitions and metadata | I | A | R | I | C | I | C | I | I | C | I |
| Assign or change classification for a customer asset under policy | I | A | R | C | C | C | C | I | I | I | I |
| Approve routine access for a stated business purpose | I | A | C | I | C | C | C | I | I | R (request) | I |
| Implement approved access in platform controls | I | C | C | I | A/R | C | I | I | I | I | I |
| Approve a time-limited exception within delegated risk limits | I | A | C | C | R (record/implement) | C | C | C | C | I | I |
| Approve a material cross-domain policy exception within council mandate | A | C | C | R (prepare) | C | C | C | C | C | I | I |
| Accept residual risk for an exception where acceptance is permitted | I | R (submit risk case) | I | I | C | C | C | C | A | I | I |
| Define and approve enterprise classification policy | A | C | C | R | C | C | C | C | I | I | I |
| Respond to a suspected platform security incident | I | I | C | I | R | A | C | C | I | I | I |
| Approve a material retention-policy change | A | C | C | R | C | C | C | C | I | I | I |
| Conduct periodic access recertification for the customer domain | I | A | R (coordinate) | I | R (provide access evidence) | C | C | I | I | I | I |
| Independently test the design/operation of selected governance controls | I | I | C | I | C | C | C | C | I | I | A/R |

On the access-approval row, Platform Operations is consulted on technical feasibility but does not approve the business purpose; the consumer's `R (request)` refers only to submitting a complete request. In the separate access-implementation row, Platform Operations is both accountable for the implementation outcome and responsible for carrying out or directing the implementation; the data owner remains accountable for the separate business approval. For the classification-policy row, the council is accountable for the policy decision while the policy owner drafts and maintains the policy. For exception handling, council approval of a policy exception and acceptance of residual risk are separate decisions when both are required. The designated Executive Risk Acceptance Authority (ERA) is accountable for the latter only where the organisation's delegation framework grants that authority. In the final row, Internal Audit is accountable and responsible for its independent test deliverable, not for operating the control being tested.

**Why these assignments are appropriate**

1. **Enterprise policy:** the council is accountable for the enterprise policy decision; the policy owner drafts and maintains it. Specialist functions are consulted because they provide relevant expertise.
2. **Definitions and metadata:** the owner is accountable for business meaning; the steward performs ongoing maintenance. Platform operators support the technical metadata surfaces but do not determine business semantics alone.
3. **Classification:** the owner is accountable for the asset-level decision under the policy; the steward records it and specialists advise where needed. The enterprise policy owner defines the classification framework separately.
4. **Access approval:** the owner decides whether the use is appropriate; the requester supplies the purpose and the platform implements the approved grant. Technical provisioning is not business approval.
5. **Platform implementation:** the platform lead is accountable for correct implementation; security advises on control design and the owner confirms the business intent where needed.
6. **Exceptions:** local exceptions stay within delegated authority; material cross-domain or out-of-limit exceptions escalate to the council. An exception must have scope, rationale, compensating controls, expiry, and a named risk owner.
7. **Incident response:** security leads the response to a platform security incident; platform operations executes technical response tasks. The incident commander and notification obligations must follow the organisation's incident-response plan and specialist advice.
8. **Retention changes:** a material enterprise retention-policy change is approved at enterprise level after owner and specialist input. Implementation and legal interpretation are separate responsibilities.
9. **Access recertification:** the data owner is accountable for deciding whether business access remains justified; the steward coordinates and the platform supplies evidence.
10. **Independent testing:** audit's accountability applies to its independent testing work. Audit should not be assigned operational responsibility for controls it later independently evaluates.

**RACI validation checks**

- Every row has exactly one `A` in this worked example.
- Every activity has at least one `R` that actually performs the work; the platform-implementation and independent-test rows explicitly show `A/R` where the accountable role also performs or directs the work.
- Consulted roles are consulted before a decision, not merely copied after it.
- Informed roles receive the result and do not become shadow approvers.
- A role's authority is documented outside the table in policy, charter, delegation, or job/accountability documentation.
- If one person holds incompatible roles, apply the separation-of-duties rules in Section 6.

The matrix should be revisited when the data domain, organisation, risk profile, or platform changes.

### 3.6 Policy lifecycle

A policy is a documented rule or direction. A control is the mechanism used to implement a requirement. A policy lifecycle keeps the rule owned, approved, communicated, implemented, monitored, and current.

```text
Identify need / obligation / risk
          |
          v
Draft policy (named policy owner)
          |
          v
Review by affected domains and specialists
          |
          v
Approve by delegated authority
          |
          v
Publish version + effective date + owner
          |
          v
Translate into standards, workflows, platform controls, and training
          |
          v
Monitor adoption, exceptions, and violations; retain evidence
          |
          v
Periodic review or event-triggered review
          |                         \
          +---- revise / retire <----+
```

For each policy, record at least: identifier, purpose, scope, owner, approving authority, version, effective date, review date, source requirements or business rationale, affected roles/systems, implementation mappings, exception route, and change history. A policy can be approved but not yet implemented; track that gap rather than treating publication as completion.

**When to use this lifecycle:** for enterprise policies, domain standards, access rules, retention rules, classification schemes, and exceptions. The formality should be proportionate to risk, scope, and impact.

**Trade-off:** rigorous review improves consistency and reduces overlooked consequences but may slow changes. Use defined review windows, delegated authority, reusable templates, and urgent-change paths with retrospective review rather than bypassing ownership entirely.

### 3.7 Governance forums

A forum is useful only when it has a defined mandate and can make or route decisions. A meeting without decision rights, preparation, and follow-up is not an operating model.

Each forum charter should state:

- purpose and decisions in scope;
- decisions explicitly out of scope;
- chair and accountable decision role;
- members and required specialist participation;
- quorum or minimum attendance for decisions, if used;
- cadence and urgent-meeting process;
- inputs and pre-read deadline;
- decision method and tie-break authority;
- minutes, decision log, action owner, and due date;
- escalation route and service-level expectations;
- review date for the charter itself.

#### Example governance forum charter

**Forum:** Northbridge Enterprise Data Governance Council (fictional)  
**Purpose:** Set enterprise data-governance direction, approve delegated enterprise data policies, resolve material cross-domain ownership disputes, and review governance risk and effectiveness.

| Charter element | Definition (illustrative) |
|---|---|
| Chair | Executive Data Governance Sponsor |
| Accountable forum | Enterprise Data Governance Council, acting within written delegated authority |
| Standing members | Domain data-owner representatives, enterprise policy owner, platform operations, security, privacy, risk, legal/compliance when relevant; the designated executive risk acceptance authority participates when its decision is required |
| Advisers / guests | Data stewards, product owners, architecture leads, control operators, subject-matter specialists |
| Cadence | Monthly; urgent session for time-sensitive material decisions |
| Inputs | Decision paper, options, risk/impact summary, affected domains, recommendation, implementation plan, exception details if applicable |
| In-scope decisions | Enterprise policy approval within mandate; material cross-domain ownership disputes; exceptions beyond domain delegation; prioritisation of governance remediation |
| Out-of-scope decisions | Routine dataset access requests; routine metadata updates; technical operations choices already covered by approved standards; legal interpretations reserved for qualified counsel; residual-risk acceptance unless explicitly delegated to the council |
| Decision method | Seek consensus; if not achieved, apply the charter's documented voting/tie-break rule. For this illustrative charter, the Executive Data Governance Sponsor is the named escalation/tie-break authority for matters within that sponsor's written delegation; otherwise escalate to the next formally designated executive authority. Required risk acceptance and mandatory specialist approvals remain separate gates and cannot be overridden by a chair's tie-break |
| Quorum | Chair or delegate plus representatives of affected domains and required specialists for the decision type; no decision if a mandatory specialist review is missing |
| Records | Decision ID, date, decision, accountable authority, rationale, consulted parties, dissent/conditions, action owner, due date, linked ADR/exception, review trigger |
| Follow-up | Secretariat circulates minutes and actions within two business days; overdue actions are escalated at the next forum or sooner for material risk |
| Charter review | Every 12 months or after a major reorganisation (illustrative interval) |

The cadence and timing above are **illustrative assumptions**, not source-mandated targets. An organisation should set values that match its risk, workload, and decision volume.

### 3.8 Escalation paths with time limits

Escalation prevents unresolved decisions from sitting indefinitely in email or chat. Time limits should reflect impact and urgency; urgent security or privacy incidents follow the established incident process immediately rather than waiting for a governance meeting.

#### Example workflow

```text
Issue raised by consumer, steward, or platform monitor
                 |
                 v
Steward logs issue, impact, asset, evidence, and proposed owner
                 |
                 v
Data owner reviews within 3 business days (illustrative)
       /                         \
  Resolved                    Not resolved / cross-domain
     |                                |
     v                                v
Record decision + action       Domain forum within 5 business days
                                      |
                            Still disputed / exceeds authority?
                                      |
                                      v
                         Enterprise council or delegated executive
                         within 10 business days (illustrative)
                                      |
                                      v
                         Record decision, conditions, owner, due date
                                      |
                                      v
                         Implement, monitor, verify, close the issue
```

**Urgent-risk branch:** If an issue suggests active unauthorised access, data exfiltration, material integrity loss, or another incident trigger, the reporter immediately invokes the incident-response process and informs the designated security/privacy contacts. Governance escalation can continue in parallel; it must not delay containment or mandatory notifications as determined by qualified specialists.

#### Escalation record template

- Issue ID and date raised:
- Asset/domain and affected systems:
- Description and decision required:
- Impact, urgency, and known evidence:
- Interim containment or compensating control:
- Current accountable owner:
- Decision deadline and reason:
- Parties consulted:
- Options considered and recommendation:
- Decision, rationale, conditions, and dissent:
- Action owner, due date, verification evidence:
- Escalation trigger if unresolved:

### 3.9 Accountability gaps and conflicts

Common failure modes include:

| Failure mode | Why it happens | Detection signal | Prevention / remediation |
|---|---|---|---|
| “Everyone owns it” | Several teams use the asset but no role has final authority | RACI has multiple A assignments or no A | Name one accountable owner for each defined decision; define delegated roles |
| No owner | Asset created by a pipeline or team that has since changed | Catalogue record lacks a current owner or approval route | Block production publication or apply a controlled quarantine/temporary sponsor process until ownership is assigned |
| Owner without capacity | Accountability is assigned ceremonially | Decisions age; reviews are overdue; steward has no time allocation | Confirm capacity, deputy, service expectations, and escalation route |
| Platform team approves business use | Technical convenience is mistaken for authority | Grants lack purpose or owner decision evidence | Require a business approval signal before provisioning; automate only within approved rules |
| Two domains claim the same asset | Entity and attribute ownership are not defined | Conflicting definitions or access decisions | Use an entity-level accountable owner plus attribute/domain stewards; council resolves residual conflict |
| Policy without an owner | Document was published once and then forgotten | No review date, stale version, or unresolved changes | Assign a policy owner and approving authority; add review triggers and lifecycle metadata |
| Forum without authority | Decisions are discussed but not made | Repeated agenda items, no decision log | State delegated decision rights and tie-break path in charter |
| Exception never expires | Approval is treated as permanent | Old exceptions with no owner or review | Set expiry, reminders, compensating controls, and automatic removal/renewal workflow |
| Audit performs the control | Independence is compromised | Same role operates and independently attests to the control | Separate control operation from independent testing where practicable |

#### Resolving conflicting ownership

For a shared customer-contact dataset, define the **entity owner** accountable for the shared customer entity and the **attribute owners or stewards** responsible for meaning and quality of specific attributes where business domains legitimately differ. The entity owner resolves cross-attribute consistency and consumer expectations; the enterprise council acts as tie-break authority for unresolved cross-domain conflicts within its mandate. Record the rationale and revise the catalogue and contracts so the decision survives staff turnover.

Do not solve every conflict by assigning two accountable owners to one decision. If the decision truly requires joint authority, define a formal joint-decision rule, quorum, and tie-break route, and reflect that rule explicitly in the operating model.

---

## 4. Advanced level — risk, controls, scale, and operating effectiveness

### 4.1 Separation of duties

**Separation of duties (SoD)** divides incompatible responsibilities so one person or role cannot unilaterally request, approve, implement, and independently verify a high-impact action. It reduces the chance of error, misuse, or concealed failure.

Useful examples:

- The person requesting access should not approve their own request.
- The access approver should not be the only person who provisions and verifies the grant.
- A control operator should not be the sole independent tester of that control.
- A policy author should not automatically have unilateral approval authority for a high-impact policy.
- A risk assessor should not be able to accept any level of risk merely because they performed the assessment.

SoD does not mean every task needs a different employee. Small teams may use compensating controls such as independent second-person review, immutable logs, periodic retrospective review, restricted production privileges, or an external reviewer. Document the limitation and compensating control; do not claim independence where it does not exist.

### 4.2 Exception approval and risk acceptance

An **exception** permits a defined deviation from a policy or standard for a bounded period. **Risk acceptance** is a decision by an authorised risk owner to tolerate specified residual risk. These are related but not identical: an exception request may be rejected, may require compensating controls, or may be escalated because the residual risk exceeds the requester's authority.

An exception record should include:

- unique ID and linked policy/control;
- requesting team and accountable business risk owner;
- assets, environments, users, and data classes in scope;
- business justification and alternatives considered;
- risk assessment and affected parties;
- compensating controls and monitoring;
- security, privacy, legal/compliance, or risk reviews required by policy;
- explicit approval authority and decision date;
- start date, **expiry date**, and review checkpoints;
- remediation plan, owner, and target date;
- evidence of implementation and closure.

#### Risk acceptance authority model (illustrative)

| Risk tier (illustrative, organisation-defined) | Example decision boundary | Expected authority pattern |
|---|---|---|
| Low, bounded, reversible | Short-lived deviation with limited scope and effective compensating controls | Delegated domain owner may approve within written limits after required consultation |
| Moderate or cross-team | Broader impact, multiple domains, or meaningful control reduction | The formally designated risk owner/acceptance authority within delegated limits, with risk-function review; council separately decides any cross-domain policy question within its mandate |
| High, restricted data, or beyond delegated tolerance | Material potential harm, major control bypass, or risk beyond local authority | Escalate to the designated executive risk authority and required security/privacy/legal decision gates; do not approve locally |
| Prohibited or non-waivable condition | A rule that the organisation's policy or applicable obligation does not permit to be waived | Reject or redesign; governance cannot create authority to waive a non-waivable requirement |

This is a conceptual pattern, not a universal risk taxonomy. The organisation must define thresholds, delegated authority, and non-waivable constraints with qualified specialists. The business risk owner is accountable for the risk decision only when formally authorised; the Risk function may advise and challenge without becoming the risk owner. A RACI row alone cannot grant legal or executive authority.

**Expiry discipline:** every accepted risk has a date or explicit event that triggers reconsideration. Before expiry, the owner must remediate, renew through a fresh assessment and approval, or allow the exception to lapse. Renewal is not automatic. If access or a configuration must be removed on expiry, the workflow should generate and verify that action.

### 4.3 Governance effectiveness metrics

A metric should have a clear definition, denominator, owner, collection method, cadence, and interpretation. Avoid targets that reward superficial completion while hiding poor decisions. Targets below are **illustrative assumptions** and must be calibrated to baseline, risk, and operational capacity.

| Metric | Definition / calculation | What it reveals | Example target (illustrative) | Evidence source / owner |
|---|---|---|---|---|
| Critical assets with named owner | Critical assets with a current named owner ÷ all identified critical assets × 100% | Ownership coverage | ≥ 98% | Catalogue snapshot; Governance Operations |
| Critical assets with active steward | Critical assets with a named, available steward ÷ all identified critical assets × 100% | Day-to-day stewardship coverage | ≥ 95% | Catalogue and stewardship roster; Domain Leads |
| Classification coverage | In-scope assets with approved classification ÷ all in-scope assets × 100% | Readiness for downstream controls | ≥ 98% before broad production use | Catalogue and review log; Data Owners |
| Access request cycle time | Median business time from complete request to decision; report p90 as well | Decision efficiency and queue outliers | Median ≤ 3 business days for routine requests | Workflow timestamps; Access Governance Owner |
| Timely access recertification | Reviews completed by due date ÷ reviews due × 100% | Whether periodic review operates | ≥ 95% | Review workflow evidence; Data Owners |
| Open exception age | Count and age distribution of active exceptions; separately show overdue exceptions | Accumulated risk debt | No expired exception remains active without reapproval | Exception register; Risk Owner |
| Policy violation remediation time | Median and p90 from validated finding to verified closure | Ability to correct deviations | Risk-tiered SLOs set by policy | Detection and remediation records; Control Owner |
| Policy implementation coverage | Applicable controls implemented and verified ÷ controls required by approved policy × 100% | Gap between policy and platform | 100% for required controls before go-live, or approved transition plan | Control mapping and deployment evidence; Platform Owner |
| Ownership change completion | Ownership changes recorded and accepted within agreed window ÷ detected ownership changes × 100% | Resilience to organisational change | ≥ 95% within 10 business days (illustrative) | Change tickets and catalogue history; Governance Operations |
| Decision-log completeness | Material decisions with authority, rationale, owner, date, and follow-up ÷ material decisions sampled × 100% | Traceability | ≥ 98% | Decision log sample; Council Secretariat |

**Measurement cautions**

- Define the population. “All critical assets” is meaningless until criticality and inventory scope are defined.
- Segment by risk, domain, and asset type; an enterprise average can conceal a high-risk domain.
- Pair speed with quality and risk indicators. A short access cycle time is not good if approvals are careless.
- Do not count a meeting as effective merely because it occurred. Measure whether decisions were recorded and actions completed.
- Keep the evidence source reproducible, time-stamped, and attributable.
- Review whether the metric is being gamed or has become a proxy for the real objective.

### 4.4 Operating-effectiveness evidence

A policy describes expected behaviour. A control implements a requirement. **Operating effectiveness** asks whether the control actually operated as designed over the relevant period. Evidence can include:

- signed or workflow-recorded decisions with approver identity and timestamp;
- complete access request and approval records;
- periodic review completion and revocation evidence;
- versioned policy approvals and publication history;
- configuration or deployment records for technical controls;
- exception approvals, expiry checks, and closure evidence;
- issue and incident records, including remediation verification;
- forum minutes, decision logs, action owners, and due dates;
- sample-based test results from an independent reviewer.

A screenshot or meeting note may be useful, but it is not automatically sufficient. Evidence should answer **what happened, when, under whose authority, against which requirement, with what result, and where the follow-up is recorded**. Evidence design is expanded in the later regulatory-controls-and-evidence topic.

### 4.5 Ownership changes, orphaned assets, and organisational change

Ownership is not permanent merely because a catalogue field contains a name. People leave, teams merge, products are retired, and responsibilities move. A production operating model needs a change process.

#### Recommended ownership-change workflow

1. **Trigger:** HR/organisation change, team transfer, product retirement, owner departure, or periodic owner attestation.
2. **Discover:** query the catalogue and dependency/lineage inventory for assets associated with the affected role or team.
3. **Assign interim accountability:** a designated executive or domain lead accepts temporary sponsorship with a short expiry; do not leave the asset silently unowned.
4. **Assess dependencies:** identify consumers, pipelines, contracts, access approvals, retention commitments, exceptions, and downstream analytics/AI uses.
5. **Transfer formally:** new owner accepts the role and decision rights; steward and platform contacts are updated.
6. **Revalidate:** confirm classifications, access approval routes, policy exceptions, and review dates remain valid.
7. **Update systems:** catalogue, workflow routing, access groups, runbooks, ownership registry, and contact channels.
8. **Verify and close:** capture evidence and ensure pending decisions have an owner.

For an unowned asset, use a defined policy: restrict new high-risk uses, maintain necessary safe operations, assign a temporary accountable sponsor, and set a deadline for permanent ownership or retirement. A temporary sponsor is a containment measure, not a substitute for long-term ownership.

### 4.6 Scaling governance from dozens to thousands of assets

Manual governance can work for a small portfolio but becomes slow and inconsistent at scale. Scale by standardising metadata and automating repeatable checks, while retaining human judgement for ambiguous or high-impact decisions.

| Mechanism | What to automate | What still needs human judgement | Risk / limitation |
|---|---|---|---|
| Mandatory metadata schemas | Required owner, steward, classification, domain, lifecycle, and review fields | Whether a proposed owner has authority and capacity | Complete fields can still contain inaccurate values |
| Catalogue validation | Missing owners, stale reviews, unknown classification, expired exceptions | Resolving disputed ownership or ambiguous semantics | Discovery may miss shadow data stores |
| Workflow routing | Send request to the correct owner, apply deadlines, remind, escalate | Appropriateness of novel or sensitive purposes | Incorrect routing can create false approvals or delays |
| Policy-as-code / platform guardrails | Enforce deterministic rules such as required metadata or blocked unapproved deployment | Interpreting complex business context and exceptions | A coded rule can be consistently wrong; changes need testing and ownership |
| Risk-based review | Increase review frequency for high-impact assets and permissions | Set risk thresholds and decide unusual cases | Bad classification undermines prioritisation |
| Ownership-change integration | Trigger inventory and handover tasks from organisational events | Choose the correct successor and resolve disputes | Source systems may be delayed or incomplete |
| Evidence automation | Capture approval IDs, deployment records, access logs, and review timestamps | Evaluate whether evidence is sufficient for a particular assurance question | Logs may be incomplete, mutable, or disconnected from requirements |

A scalable model should make the safe path the easy path. It should not automate decisions beyond the authority delegated to the system or obscure who is accountable for the rules.

### 4.7 Governance integration with the data platform

The operating model becomes useful when its decisions connect to platform metadata, workflows, controls, and evidence.

```text
Business domain / data owner
          | defines meaning, approved use, accountable decisions
          v
Governance workflow and decision records
          | approved classification, purpose, access, exception, retention
          v
Catalogue + metadata + lineage + data contracts
          | propagate ownership and handling attributes
          v
Platform control plane
  - identity and access enforcement
  - pipeline and publication guardrails
  - encryption / key access configuration
  - masking or tokenization decisions
  - retention, deletion, and legal-hold workflows
  - monitoring and alerting
          |
          v
Operational evidence
  - approvals, configuration history, logs, reviews, remediation records
          |
          v
Governance forums / risk / compliance / independent assurance
```

**Important boundary:** governance approves the policy and decision rights; technical systems enforce deterministic rules; operational teams respond to failures; evidence demonstrates what occurred. A control must have a technical or procedural owner and an accountable role for its expected outcome.

This operating model supports later module topics:

- **Classification:** data owners and stewards determine and maintain labels; platform metadata carries them to relevant assets.
- **Identity and access:** the owner or delegated authority approves a use; the platform provisions least-privilege access and records the grant.
- **Encryption, keys, and secrets:** security and platform roles implement key-access boundaries under approved policy; ownership does not imply unrestricted key access.
- **Masking and tokenization:** owners, privacy, and security functions decide required protections for intended uses; engineers implement and validate them.
- **Consent, purpose, and residency:** business use decisions incorporate specialist interpretation and constraints; data flows and deployment choices must reflect approved boundaries.
- **Retention, deletion, legal holds, and auditability:** policy owners and specialists define requirements; owners identify business scope; platform teams implement lifecycle controls across copies and preserve evidence.
- **Regulatory controls and evidence:** requirements map to a control owner, operator, evidence source, reviewer, and remediation path.
- **Governance by design:** metadata validation, policy checks, access workflows, deployment guardrails, and exception expiry make approved governance repeatable.

### 4.8 Architecture trade-offs and common misconceptions

| Misconception / design choice | Why it fails | Better engineering response |
|---|---|---|
| “Governance means a committee.” | Meetings alone do not create authority, execution, or evidence. | Define roles, decision rights, workflows, controls, and measures. |
| “The platform team owns all data because it stores it.” | Operators may not understand business meaning, purpose, or appropriate use. | Separate data ownership from platform operation. |
| “The data owner can approve anything.” | Authority may be limited by policy, risk thresholds, or non-waivable constraints. | Document delegation and mandatory specialist/enterprise approval gates. |
| “RACI is the policy.” | RACI maps roles but does not establish legal authority or replace formal delegation. | Link RACI to charters, policies, approval workflows, and role definitions. |
| “Every decision must go to the central council.” | The central function becomes a bottleneck and routine work stalls. | Delegate bounded decisions; escalate only material or unresolved issues. |
| “Federated means each domain can do anything.” | Local autonomy without minimum controls causes inconsistency and risk. | Set enterprise guardrails, metadata standards, conformance checks, and escalation. |
| “A named owner is enough.” | A name may be stale, unresourced, or lack authority. | Verify role, capacity, deputy, decision SLA, and change process. |
| “An exception is permanent once approved.” | Risk changes and temporary workarounds become invisible permanent debt. | Require scope, compensating controls, expiry, review, and verified closure. |
| “A policy document proves compliance.” | Publication does not show implementation or operation. | Map policy to controls and retain operating evidence; obtain qualified assessment where required. |
| “All data should receive the highest classification.” | Over-classification increases friction and may make controls unusable. | Apply a defined, risk-based scheme with review and context-sensitive aggregation rules. |

---

## 5. Industry scenarios — Northbridge Bank (fictional)

All organisations, datasets, numbers, roles, and events in this section are synthetic instructional assumptions. Do not use real personal, financial, or confidential information in exercises.

### Scenario A: shared customer data product

Six domains use a shared customer data product. Marketing wants contact fields for campaign analysis; fraud operations needs customer identifiers for investigation; service operations needs contact details to resolve cases. No single domain understands every downstream use.

**Options**

1. One central owner decides every detail. This is simple but may be distant from local context and create a queue.
2. A steward council owns everything jointly. This creates participation but may leave final decisions ambiguous.
3. An entity-level owner is accountable for the shared customer product, while domain stewards or attribute owners maintain field-level semantics and domain quality rules. Enterprise policy defines minimum protections and the council resolves material conflicts.

**Recommended for this illustrative scenario:** option 3, with a named entity-level owner and explicit field-level responsibilities. It balances shared meaning with domain context. It requires a clear rule for disputes and a catalogue that records both entity ownership and attribute stewardship.

**What would change the recommendation?** If the dataset were small, stable, and used by one domain, a simpler central owner might be enough. If the domains were truly independent and there were no shared semantics, more decentralisation might be viable.

### Scenario B: platform team asked to approve all access

A backlog of access requests has formed. The platform team proposes approving all requests because it controls the permissions.

**Analysis:** platform operations can validate technical feasibility and provision permissions, but it usually lacks the business context to determine whether a purpose is appropriate. The data owner or formally delegated access authority should decide; the platform team should enforce that decision. For explicitly defined low-risk cases, policy may permit automated approval based on verified attributes, but the automation must operate within approved rules and log its decision.

**Failure mode:** an engineer grants access based on a manager's informal message; no purpose, duration, or owner approval is recorded. A later review cannot establish why the access was granted.

**Improvement:** a workflow requires requester identity, data asset, purpose, scope, duration, and owner approval (or a permitted automated rule) before provisioning. The system records the approval reference and access grant; review tasks are scheduled according to policy.

### Scenario C: two domains claim customer contact details

Retail and Service both claim ownership of “customer contact details.” Retail maintains campaign preferences; Service maintains contact information used to resolve service cases. The shared field is inconsistently defined and updated.

**Resolution process:**

1. Steward records the conflict and identifies affected fields, definitions, consumers, and downstream contracts.
2. Each domain owner submits its business definition and requirements.
3. The entity owner distinguishes the canonical contact attribute from domain-specific preference or service-contact attributes.
4. The domain forum attempts resolution within its delegated scope.
5. If unresolved, the enterprise council applies the charter's tie-break rule and records the decision.
6. Catalogue entries, data contracts, lineage references, and access routes are updated.
7. A steward validates the change with synthetic test cases and records closure evidence.

**Lesson:** do not use “shared ownership” to hide a missing decision. Define who is accountable for each decision and how overlapping scopes are reconciled.

### Scenario D: owner leaves during a reorganisation

The owner of a high-impact reporting dataset leaves the organisation. Existing pipelines continue running, but a new access request and a pending exception have no valid approver.

**Response:** trigger the ownership-change workflow, assign a temporary accountable sponsor, inventory downstream dependencies and open exceptions, route new high-risk requests through an approved interim path, appoint a permanent owner, update metadata and workflows, and revalidate access and exception records. Record acceptance by the new owner and close the transition only after verification.

**Trade-off:** temporarily restricting new use can reduce risk but may delay business activity. Any interim access route must have explicit authority, narrow scope, compensating controls, and an expiry date.

---

## 6. Example governance operating-model document

The following is a compact example of an operating-model document. It is intentionally written as a reusable template filled with fictional Northbridge assumptions.

### Northbridge Customer Data Governance Operating Model — Example v1.0

**Status:** Illustrative learning artifact; not an approved policy for any real organisation.  
**Scope:** Shared customer data product and its directly managed derived views used by the six fictional Northbridge domains.  
**Purpose:** Make business accountability, access decisions, policy implementation, and escalation explicit.

#### 6.1 Principles

1. Each defined governance decision has one named accountable role.
2. Business owners decide appropriate business use; platform operators implement approved controls.
3. Enterprise policies set minimum controls; domains operate within delegated boundaries.
4. High-impact decisions and exceptions have documented rationale, authority, and review/expiry.
5. Asset ownership and stewardship are recorded in metadata and reviewed after organisational changes.
6. Routine decisions are handled at the lowest competent level; material conflicts escalate through time-boxed paths.
7. Controls produce evidence as part of normal operation wherever practical.

#### 6.2 Role assignment

| Role | Named role in the example | Key duties | Minimum capability / resourcing expectation |
|---|---|---|---|
| Enterprise accountable authority | Enterprise Data Governance Council | Enterprise policy decisions, material disputes, exceptions beyond domain delegation | Charter, quorum, executive sponsor, secretariat |
| Data owner | Customer Domain Data Owner | Business meaning, approved uses, classification accountability, access decisions within authority | Time allocation, deputy, clear decision SLA |
| Data steward | Customer Data Steward | Catalogue, definitions, quality rules, review coordination, issue records | Domain knowledge, access to metadata, capacity for routine work |
| Policy owner | Enterprise Data Policy Owner | Policy drafting, versioning, consultation, periodic review | Authority to maintain policy and coordinate specialist review |
| Platform operator | Platform Operations Lead | Technical implementation, monitoring, access provisioning, lifecycle automation | Operational runbooks, controlled privileges, evidence access |
| Security lead | Enterprise Security Lead | Security standards and incident response input/leadership as defined in incident plan | Escalation channel and defined decision rights |
| Privacy lead | Privacy Function Lead | Privacy review and advice within the function's mandate | Early involvement in relevant use and design decisions |
| Risk lead | Enterprise Risk Lead | Risk-method advice, acceptance framework, challenge | Defined risk thresholds and escalation route |
| Data consumer | Requesting product/analytics team | State purpose, use data as approved, comply with handling requirements | Training and traceable request process |
| Independent assurance | Internal Audit | Independent test work within its mandate | Independence from control operation |

#### 6.3 Decision boundaries

- **Enterprise-wide policies:** approved by the council or other formally delegated enterprise authority after required reviews.
- **Asset meaning and routine classification:** accountable owner decides under policy; steward maintains the record; specialist consultation is required when specified by policy.
- **Routine access:** data owner or delegated access authority approves the purpose, scope, and duration; platform operations provisions only after a valid approval signal.
- **Technical implementation:** platform operations is accountable for implementing approved configurations and documenting evidence.
- **Exceptions:** the domain owner may approve a policy exception only within documented delegated limits. Where residual-risk acceptance is required, the formally designated risk acceptance authority must separately approve it within its mandate. The council decides cross-domain policy questions only within its charter; neither the council nor an executive may waive a non-waivable constraint. Required specialist gates remain mandatory.
- **Security incident:** follow the incident-response plan; security leads or coordinates as defined there; governance forums do not delay containment.
- **Independent testing:** assurance is performed by a role independent of control operation to the extent practicable.

#### 6.4 Operating cadence and service expectations

The council meets monthly; domain forums meet at least monthly or as needed; stewards review missing metadata and overdue actions weekly. These are illustrative starting points. Routine owner decisions target three business days after a request is complete; unresolved domain issues escalate within five business days; material enterprise escalation is scheduled within ten business days unless risk urgency requires immediate handling.

#### 6.5 Required records

- Asset register with owner, steward, domain, classification, lifecycle status, and review date.
- Decision log with decision ID, authority, rationale, date, consultation, action owner, and due date.
- Access approval record linked to the provisioned grant and review/expiry.
- Exception register with scope, risk owner, controls, approval, expiry, and remediation.
- Policy register with owner, approver, version, effective date, implementation mapping, and review date.
- Ownership-change log and orphaned-asset remediation record.
- Governance metrics and evidence references.

#### 6.6 Review and change control

Review the operating model annually and after a material reorganisation, a significant incident, a change in platform architecture, or a repeated governance failure. The policy owner coordinates the review; the council approves changes within its authority; affected domains and specialist functions are consulted; platform workflows and metadata are updated as part of implementation.

---

## 7. Architecture decision record (ADR) example

An **architecture decision record** captures a significant design decision, the context, options, chosen approach, and consequences. It helps future engineers understand not only what was selected but why. This ADR is an instructional example, not a source-mandated requirement beyond the roadmap's recommendation to document the operating model in an ADR.

### ADR-2D10-001: Adopt a federated governance operating model for shared customer data

**Status:** Proposed for the fictional learning scenario  
**Date:** 2026-10-20 (illustrative record date)  
**Decision owner:** Enterprise Data Governance Council  
**Related artifacts:** Northbridge Customer Data Governance Operating Model v1.0; RACI matrix; governance forum charter

#### Context

Six business domains consume a shared customer data product. A central-only model risks slowing routine domain decisions; a fully decentralised model risks inconsistent definitions, access practices, and control implementation. The platform needs a clear separation between business decisions, policy authority, and technical enforcement. The current fictional-state assumption is that domain ownership exists but is inconsistently recorded.

#### Decision drivers

- One accountable role for each defined decision.
- Enterprise consistency for minimum policies and controls.
- Domain-level knowledge for business meaning, data quality, and routine access decisions.
- Traceable approvals, exceptions, and review evidence.
- Scalable operation across a growing data estate.
- Defined escalation and tie-break authority for shared assets.

#### Options considered

| Option | Benefits | Costs / risks |
|---|---|---|
| Fully centralised | Consistency; clear central view | Bottlenecks; weaker domain context; central staffing pressure |
| Fully decentralised | Local speed and autonomy | Divergent policies and metadata; difficult cross-domain access and evidence |
| Federated | Enterprise guardrails plus delegated domain decisions | Needs clear boundaries, catalogue quality, escalation, and conformance monitoring |

#### Decision

Adopt a **federated** model for the fictional Northbridge customer data product:

1. The enterprise council approves enterprise governance policies and resolves material cross-domain disputes within delegated authority.
2. The enterprise policy owner maintains policy lifecycle records and coordinates review.
3. The customer domain owner is accountable for business meaning, appropriate uses, and routine access decisions within the documented delegation.
4. The data steward maintains definitions, classification metadata, and governance issue records.
5. Platform operations implements approved access and policy controls, monitors operation, and retains technical evidence.
6. Security, privacy, risk, and legal/compliance functions participate according to defined review gates and authority.
7. The council approves policy exceptions only within its written mandate. A separately designated risk acceptance authority accepts residual risk where permitted; the Risk function advises and challenges but is not automatically the risk acceptor.
8. Exceptions have a named risk owner, scope, compensating controls, approval authority, expiry, and closure evidence.
9. The model is reviewed after major organisational or platform changes and at the periodic review interval.

#### Consequences

**Positive:** decisions are closer to business context; enterprise minimum controls remain consistent; technical implementation and business approval are separated; ownership and exceptions become observable.

**Negative / costs:** roles and metadata require maintenance; some cross-domain decisions take longer; platform workflows need integration; the council needs a functioning secretariat and decision discipline.

**Risks and mitigations:**

- *Risk:* domains interpret policy differently. *Mitigation:* minimum enterprise definitions, policy-as-code where appropriate, conformance checks, and periodic review.
- *Risk:* owners are named but unavailable. *Mitigation:* deputies, capacity expectations, decision SLAs, and escalation.
- *Risk:* exceptions become permanent. *Mitigation:* mandatory expiry, reminders, renewal reassessment, and verified removal or remediation.
- *Risk:* automation routes requests incorrectly. *Mitigation:* test routing rules, preserve decision logs, and sample decisions.

#### Implementation plan

1. Confirm owner, steward, policy owner, and delegated approvers for in-scope assets.
2. Populate the asset register and identify missing or conflicting ownership.
3. Approve the forum charter and RACI; publish escalation times and tie-break rules.
4. Configure workflow requirements for complete access and exception requests.
5. Connect approved decisions to platform provisioning and evidence records.
6. Establish baseline metrics and review them after an initial operating period.
7. Review the model with an independent reviewer and track findings to closure.

#### Review triggers

Material reorganisation; repeated ownership disputes; sustained access backlog; a significant incident; a material change to the data product or platform; policy or risk-framework change; or metrics showing controls are not operating as intended.

---

## 8. Hands-on exercises and expected deliverables

Use only synthetic data. Keep decisions and examples reproducible so another learner can review the result.

### Exercise A — Build a responsibility matrix

**Scenario:** Northbridge governance is ad hoc across six fictional domains. Use the roles and decision list in this lesson.

**Tasks**

1. Choose 12 governance decisions, including policy creation, asset definition, classification, access approval, access implementation, exception approval, incident response, retention change, ownership transfer, access recertification, metric review, and independent testing.
2. Assign R, A, C, and I for each decision.
3. Ensure each decision has exactly one A in the matrix unless a formally defined joint-decision mechanism is explicitly described outside the RACI.
4. Confirm every decision has a real performer (R) and a role with authority and capacity (A).
5. Add decision criteria, evidence, and escalation route for high-impact rows.
6. Identify gaps, duplicate authority, unresourced roles, and SoD conflicts.

**Deliverables:** responsibility matrix; role glossary; gap log; short explanation of five non-obvious assignments.  
**Validation:** one A per row, at least one R per row, no unexplained conflict, and explicit authority/delegation assumptions.

### Exercise B — Governance forum charter and escalation path

**Tasks**

1. Draft a forum charter with purpose, in-scope/out-of-scope decisions, chair, membership, cadence, decision method, records, and escalation authority.
2. Define an escalation path from steward to data owner to domain forum to enterprise council or designated executive.
3. Assign realistic time limits and an urgent incident branch.
4. Create a decision-log template and one filled synthetic example.
5. State who may break a tie and what happens if the authority is unavailable.

**Deliverables:** forum charter; escalation workflow; decision-log entry.  
**Validation:** every escalation level has a receiving role, deadline, required input, and documented outcome.

### Exercise C — Accountability gap and conflict analysis

**Scenario:** Retail and Service both claim ownership of “customer contact details.” The dataset has no reliable field-level definition; the previous owner left; two access requests are pending; one exception expires soon.

**Tasks**

1. Identify the missing or conflicting decision rights.
2. Separate entity-level ownership from attribute-level stewardship.
3. Propose an interim accountable sponsor and define what may or may not proceed while ownership is resolved.
4. Name a tie-break authority and time-box the decision.
5. Define metadata, workflow, and access updates after the decision.
6. Include exception renewal/removal and ownership handover evidence.

**Deliverables:** gap/conflict log; decision record; ownership-change checklist; remediation plan.  
**Validation:** one accountable owner per decision; clear resolution criteria; no unbounded temporary exception; named action owners and due dates.

### Exercise D — Governance metrics and evidence plan

**Tasks**

1. Select at least six metrics from Section 4.3.
2. Define the population, numerator/denominator, owner, cadence, data source, and target.
3. Identify how the metric could be misleading or gamed.
4. Define a sample-based evidence check for access approval, exception expiry, and policy implementation.
5. Describe what happens when a target is missed.

**Deliverables:** metric dictionary; baseline/target table; evidence plan; remediation escalation.  
**Validation:** another learner can reproduce each calculation from synthetic records.

### Exercise E — ADR and architecture review

**Tasks**

1. Adapt ADR-2D10-001 to a different fictional domain or explain why the decision would change.
2. Compare centralised, decentralised, and federated models using explicit criteria.
3. State assumptions and uncertainties separately from known facts.
4. Identify positive and negative consequences, implementation steps, risks, and review triggers.
5. Have another learner review the RACI, charter, gap analysis, metrics, and ADR for internal consistency.

**Deliverables:** completed ADR and peer-review notes.  
**Validation:** decision follows from stated drivers; all assigned roles match the RACI and charter; every significant risk has a mitigation or explicit acceptance path.

### Recommended repository deliverable set

For this lesson, keep the artifacts together in a learner work area or project folder:

- `governance-role-glossary.md`
- `customer-domain-raci.md`
- `governance-forum-charter.md`
- `escalation-workflow.md`
- `accountability-gap-log.md`
- `governance-metrics-dictionary.md`
- `ADR-2D10-001-federated-governance-operating-model.md`

These filenames are recommendations for organising the exercises, not additional source requirements.

---

## 9. Knowledge review

Answer without looking at the lesson first, then compare your answers to the principles and examples above.

1. What is a governance operating model, and how is it different from a committee structure?
2. Explain the difference between data ownership and platform operation using one production example.
3. Who should normally decide whether a business use of a dataset is appropriate, and who should implement the resulting access grant?
4. What is the difference between a policy owner and the authority that approves the policy?
5. Explain R, A, C, and I. Why is a RACI not a substitute for formal decision authority?
6. Why should each row in the worked example have one accountable role? When might a formal joint-decision rule need to be documented separately?
7. Compare centralised, decentralised, and federated governance. Give one condition that would change your recommendation.
8. Name the stages of a policy lifecycle and one evidence item associated with each of three stages.
9. What minimum information belongs in a governance forum charter?
10. How should a team resolve an ownership dispute over a shared attribute?
11. What is separation of duties? Give one compensating control for a small team that cannot fully separate roles.
12. What makes an exception different from a permanent policy change? Why must expiry be operationally enforced?
13. Define residual risk and explain why an owner cannot accept risk beyond delegated authority.
14. Give three governance metrics and state their denominators or calculation methods.
15. Why does a high classification-coverage metric not by itself prove that data are correctly classified?
16. What should happen when a data owner leaves the organisation?
17. How can governance metadata connect to access controls, retention workflows, and evidence?
18. Give one way automation improves governance and one way it can fail.
19. Why should internal audit not be the sole operator and tester of the same control?
20. What evidence would help establish that an access approval and subsequent provisioning both occurred correctly?

### Suggested answer checkpoints

- A strong answer separates authority, execution, consultation, and assurance.
- It names roles, not vague groups, and describes the limits of each role's authority.
- It connects policy to an implementation mechanism and evidence, not just documentation.
- It describes escalation criteria and deadlines, including a separate urgent incident path.
- It explains trade-offs rather than claiming one governance model is universally best.
- It recognises that metrics need defined populations, reliable sources, and interpretation.

---

## 10. Mastery criteria and completion gate

### 10.1 Mastery criteria

You are ready to progress when you can demonstrate all of the following:

- [ ] Explain data owner, steward, custodian/platform operator, policy owner, access approver, consumer, governance council, and specialist functions in plain language.
- [ ] Clearly distinguish data ownership, platform operation, access approval, and policy definition.
- [ ] Produce a responsibility matrix for at least 12 decisions with exactly one accountable role per row in the worked model, and justify the non-obvious assignments.
- [ ] Identify missing owners, duplicate accountability, unresourced roles, and separation-of-duties conflicts.
- [ ] Compare centralised, decentralised, and federated models with stated selection criteria and trade-offs.
- [ ] Document the policy lifecycle and identify its owner, approving authority, implementation path, review triggers, and evidence.
- [ ] Produce a forum charter and time-boxed escalation path with an urgent incident branch.
- [ ] Define exception and risk-acceptance boundaries, mandatory fields, expiry, renewal, and closure handling.
- [ ] Define observable metrics with denominators, owners, data sources, cadence, and appropriate caveats.
- [ ] Explain how ownership and governance decisions connect to catalogue metadata, access enforcement, policy implementation, and evidence.
- [ ] Complete a gap/conflict analysis and an ADR that are consistent with the RACI and charter.

### 10.2 Completion checklist

- [ ] Responsibility matrix, forum charter, and gap analysis reviewed by one other person.
- [ ] The reviewer confirmed that each decision has one accountable role in the example and that each assignment is consistent across artifacts.
- [ ] You can explain the four distinct responsibilities to a non-specialist.
- [ ] Governance measures are observable and reproducible from defined evidence sources.
- [ ] The escalation path has time limits, a tie-break authority, and a separate urgent incident path.
- [ ] Exceptions have scope, named risk owner, required reviews, compensating controls, expiry, and verified closure or renewal.
- [ ] Ownership-change and orphaned-asset procedures are documented.
- [ ] Weakness caused by collapsing ownership, operation, approval, and policy roles has been addressed by revising the matrix.
- [ ] No real personal or confidential data was used in exercises.
- [ ] Assumptions, recommendations, and organisation-specific decisions are clearly labelled.

### 10.3 Completion gate

Do not move to **Topic 02 — Data Classification, Sensitivity and Criticality** until the matrix, charter, and gap analysis are coherent enough for another person to review, you can explain the separation of responsibilities, and the metrics have observable definitions. Topic 02 depends on Topic 01 because classification needs an accountable owner, a steward who maintains the classification record, and a policy/decision path for disputes and changes.

---

## 11. Final summary

A governance operating model translates data-governance intent into a repeatable way of making and executing decisions. Its core is not a committee; it is **clear decision authority, named accountability, capable execution, bounded exceptions, time-boxed escalation, and evidence that the model operates**.

For production data architecture, keep four responsibilities distinct:

1. **Own the data:** decide its meaning and appropriate business use within delegated authority.
2. **Operate the platform:** implement and maintain the technical environment and approved controls.
3. **Approve access:** decide whether a requester, purpose, scope, and duration meet the applicable criteria.
4. **Define policy:** maintain the rule and ensure it is approved, communicated, implemented, monitored, and reviewed.

Centralised, decentralised, and federated approaches all have trade-offs. A federated pattern often suits a shared enterprise platform, provided enterprise minimum controls, domain decision boundaries, and escalation rules are explicit. RACI helps expose gaps but does not create authority. Risk acceptance requires delegated authority and a time-bounded record. Metrics need reproducible definitions, and policies need implementation and operating evidence. Ownership must survive reorganisations and staff turnover.

The next topic uses this accountability foundation to define classification. That classification then informs access, encryption, masking, purpose and residency constraints, retention, evidence, and policy enforcement. Governance is therefore an architectural dependency, not an administrative afterthought.
