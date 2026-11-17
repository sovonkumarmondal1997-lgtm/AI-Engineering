# Business Capabilities, Domains and Data Ownership

> **Stage 2D — Data Architecture**  
> **Module:** 01 — Data Architecture Foundations and Principles  
> **Lesson file:** `03-business-capabilities-domains-and-data-ownership.md`  
> **Learning progression:** Beginner → Intermediate → Advanced → Industry application

## 1. Learning objective

By the end of this lesson, you should be able to identify business capabilities and bounded business domains; explain how capabilities relate to processes, systems and data assets; assign and document accountable ownership and stewardship; map cross-domain production and consumption; and defend ownership decisions when responsibilities overlap or conflict.

You will produce four connected artefacts for an illustrative banking organisation:

1. A two-level business capability map and a domain relationship map.
2. A capability–system–asset matrix that exposes coverage gaps, overlaps and dependencies.
3. An ownership register for ten representative assets, with unknown ownership marked explicitly.
4. An ownership decision log containing three contested cases, evidence, rationale, risks and review triggers.

**The core discipline:** start with what the business must be able to do, then identify the relevant domains, processes, systems and assets. Do not let the current application estate dictate the business model. Assign an accountable owner only when there is a defensible basis; otherwise record `UNKNOWN` and make resolving the gap an explicit action.

## 2. Why this topic matters in real-world Data Architecture

Data architecture must connect business purpose to data structures and decisions. An inventory of applications alone tells you what technology exists; it does not reliably tell you what the organisation needs to do, which business meaning an asset represents, or who is accountable when its meaning or quality is wrong.

Capability and domain views help architecture remain understandable as systems are replaced, teams reorganise or organisations merge. Ownership makes decisions actionable: a data-quality issue, a disputed definition or a proposed change needs an accountable decision-maker, not merely a technical contact.

### 2.1 What each artefact answers

| Artefact | Question it answers | What it does not prove by itself |
|---|---|---|
| Capability map | What must the organisation be able to do? | That the capability is implemented well or has a system |
| Domain map | Which bounded areas of business meaning and responsibility interact? | That a domain must equal one department or application |
| Capability–system–asset matrix | Which systems and assets support each capability, and where are gaps or overlaps? | That a system is authoritative for every asset it stores |
| Ownership register | Who is accountable for the meaning and acceptable use of each asset, and who performs supporting roles? | That the recorded ownership is correct without evidence and acceptance |
| Decision log | Why was a disputed boundary or owner selected, and when should the decision be revisited? | That the decision is permanent regardless of changed evidence |

### 2.2 Why system-centred ownership is weak

“The CRM team owns customer data” may identify a useful operational contact, but it does not answer which business role is accountable for customer identity, contact details, legal name, marketing preferences or a risk-derived attribute. One application can hold multiple kinds of data; one business asset can be created or corrected through several applications. A platform team can operate storage and access controls without being authorised to decide the business meaning of the data.

A sound ownership statement identifies the **asset and its bounded meaning**, names an accountable business role (or explicitly marks ownership unknown), identifies a steward and lists producers and consumers. The application or technical team remains important, but technical custody is not automatically business accountability.

### 2.3 Trade-offs

- **Stable capability view vs. implementation detail:** capabilities survive technology change, but are too abstract to explain operational failure on their own. Link them to systems and assets.
- **Clear domain boundaries vs. real-world overlap:** boundaries clarify authority, but an artificial single-owner model can hide legitimate local meanings. Define the asset’s meaning and context before deciding.
- **Explicit ownership vs. organisational friction:** named accountability accelerates decisions, but a title alone does not establish authority. Confirm decision rights and the ability to act.
- **Detailed maps vs. maintenance cost:** too little detail conceals gaps; too much detail becomes stale. Map at the level needed to make and review decisions.

## 3. Prerequisite knowledge

The roadmap assumes completion of Modules 1 and 2 in Data Architecture Foundations and Principles: what data architecture does, and how data architecture differs from data engineering and solution architecture. It also expects awareness of data mesh and data products from Stage 2C, Module 08. This lesson uses that awareness only as context; it does not teach the data mesh, metadata, master data management or full governance curricula.

Before starting, you should be able to:

- Describe a business need and identify the data required to support it.
- Read a simple system/data-flow diagram.
- Distinguish architecture decisions from implementation tasks.
- Explain why an accountable decision needs a named role and evidence.

If a concept is unfamiliar, use the definitions below as a refresher and then proceed in sequence.

## 4. Beginner-level learning sequence

### 4.1 The essential vocabulary

These terms describe different things. They should not be used interchangeably.

| Term | Definition | Banking example | Why the distinction matters |
|---|---|---|---|
| **Business capability** | What an organisation must be able to do, independent of the systems used to do it. | Assess creditworthiness. | Gives a stable business view when processes and technology change. |
| **Business process** | A sequence of activities, decisions and hand-offs used to achieve an outcome. | Receive an application, validate documents, assess risk, approve or decline. | Describes how work happens; a capability describes what must be possible. |
| **Business domain** | A bounded area of business knowledge, responsibility and vocabulary. | Customer, Account and Servicing; Risk; Payments and Transactions. | Helps locate meaning and accountability without forcing every asset into a single enterprise-wide definition. |
| **System** | An application, service or platform that performs functions or stores/processes data. | Mobile banking application, core banking platform, risk engine. | A system implements or supports capabilities; it is not the capability itself. |
| **Data asset** | A meaningful, identifiable set of data managed for a purpose, with a defined scope and use. | Verified customer contact details; account balance snapshot; customer risk score. | Ownership must attach to a meaningful asset, not vaguely to “all data.” |
| **Data owner** | The accountable business role for the asset’s meaning, acceptable quality, use and material decisions within its remit. | Head of Customer Operations, if formally authorised for verified contact details. | One accountable role prevents unresolved decisions; the role must be verified, not guessed. |
| **Data steward** | The role that maintains definitions, quality rules, issue triage and documentation on behalf of the owner. | Customer Data Steward. | The steward performs ongoing coordination and control; the owner remains accountable. |
| **Data producer** | A process, team or system that creates, captures, changes or publishes data. | Onboarding service captures an address; operations corrects an address. | Producers must follow rules but do not automatically own the meaning. |
| **Data consumer** | A person, process, system or domain that uses the data for a defined purpose. | Fraud analytics consumes transactions; marketing consumes an approved risk segment. | Consumers need agreed meaning and change communication; use does not confer ownership. |

**Important:** “owner” is an accountability role, not necessarily a single person’s job title. A register may identify the accountable role and separately record the currently assigned person. If the role, authority or assignment is not known, write `UNKNOWN` and track the resolution.

### 4.2 Capability versus process

A capability is relatively stable; a process can vary by channel, product, jurisdiction or operating model.

```text
Capability: Manage customer onboarding
    ├── Process: Open an account in a branch
    ├── Process: Open an account through mobile
    └── Process: Onboard a business customer

Systems may support several processes.
A process may cross several systems.
A capability may be supported by multiple systems and data assets.
```

**Why it matters:** if a bank replaces its mobile app, the capability “manage customer onboarding” still exists. If a new regulation changes the onboarding process, the capability may remain while its process, controls, systems and data requirements change.

**Common mistake:** naming “Mobile App Onboarding” as a capability when it is actually a channel-specific process or solution. A capability map should normally avoid embedding a particular product, team or technology unless the business capability itself is explicitly channel-specific.

### 4.3 Capability versus domain

A capability says **what the business must be able to do**. A domain says **where a body of business meaning and responsibility is bounded**. They are related, but they are not interchangeable.

A capability can use information from several domains. For example, “Assess creditworthiness” may use customer identity and contact details, account behaviour, transaction activity and risk policy. It is therefore misleading to insist that the capability belongs exclusively to one data domain just because one team runs the principal application.

A domain can support multiple capabilities. The Customer domain might support onboarding, servicing, fraud investigation and customer communications. The mapping is many-to-many where the business reality requires it.

### 4.4 Capability, process, system and asset relationship

The roadmap uses the chain `capability → process → system → data asset` as a teaching aid. In practice, the relationships are not always a single straight line: systems support multiple processes, data assets support multiple capabilities, and data may move between systems. Treat the chain as a traceability path, not a claim that every relationship is one-to-one.

```text
Business outcome
   ↓
Business capability (what must be possible)
   ↓ supported through
Business process (how work is performed)
   ↓ implemented or enabled by
System(s) and people
   ↓ create / transform / store / publish
Data asset(s)
   ↓ consumed by
Other processes, systems, capabilities and domains
```

A complete architecture view follows these links in both directions: from a capability to the data that supports it, and from a significant data asset back to the capabilities that depend on it.

### 4.5 Roles in a practical workflow

Example: a customer enters an address during onboarding, changes it in the mobile application, and later asks operations to correct a spelling error.

- **Producer:** onboarding service, mobile application and operations correction workflow are all potential producers or change channels.
- **Owner:** the authorised business role accountable for the meaning and acceptable quality of the verified contact-address asset.
- **Steward:** maintains the address definition, validation rules, issue queue and lineage of corrections; coordinates the investigation.
- **Consumers:** account servicing, statements, fraud operations and other approved processes that use the address.
- **System operator:** runs the relevant application or platform. This technical responsibility is distinct from business ownership.

The scenario does not tell us which bank role is formally authorised. Therefore, an architecture assessment should record the proposed owner as a candidate pending confirmation, or mark the owner `UNKNOWN`; it must not present an illustrative title as a verified organisational fact.

### 4.6 Banking exercise: ten capabilities and three domains

The following is an **illustrative model**, not a claim about a particular bank. The prompt provides the banking situations to reason about, but it does not provide a real institution’s authoritative capability map, system inventory, data-flow evidence, ownership policy or assigned role holders. Capability names, domain boundaries, system examples and candidate roles below are therefore modelling assumptions until validated. The domain labels are proposed bounded areas of meaning and responsibility. A real bank may split, combine or rename them after examining its business vocabulary and decision rights.

**Two-level capability map**

| Level 1 capability group | Level 2 capability | Example purpose |
|---|---|---|
| Customer lifecycle | 1. Acquire and onboard customers | Establish identity and complete onboarding |
| Customer lifecycle | 2. Maintain customer information | Maintain contact and identity details |
| Account and product | 3. Open and maintain accounts | Create and maintain account relationships |
| Account and product | 4. Manage balances and statements | Calculate/report balances and statement data |
| Payments and activity | 5. Initiate and execute payments | Accept, validate and execute payment instructions |
| Payments and activity | 6. Record transactions | Record monetary events and their status |
| Risk and control | 7. Assess customer and transaction risk | Assess exposure and suspicious activity |
| Risk and control | 8. Detect and investigate fraud | Identify signals and manage investigations |
| Risk and control | 9. Meet regulatory reporting obligations | Produce required, reconciled reporting from cross-domain facts |
| Relationship management and control | 10. Manage customer communications | Deliver approved service and marketing communications |

This is the required ten-capability exercise. Credit-product activity can be added to a bank-specific extension if the validated scope requires it.

**Three-domain baseline for the beginner exercise**

- **Customer and Servicing:** customer identity/contact meaning, onboarding facts, service interactions and communication preferences.
- **Accounts and Products:** account relationships, product terms, balances and account lifecycle meaning.
- **Transactions and Payments:** payment instructions, transaction events, status and settlement-related activity.

For the required three-domain exercise, keep **Customer and Servicing**, **Accounts and Products**, and **Transactions and Payments** as the baseline domains. For the advanced risk-score and fraud cases only, the lesson uses **Risk and Financial Crime** as an explicitly labelled optional fourth-domain extension because risk policy, model outputs and investigation decisions may warrant distinct ownership. Do not count that extension as one of the three domains required by the beginner exercise. A real bank should validate any additional boundary against its vocabulary, accountability and decision rights.

**Illustrative capability-to-domain relationships**

In this table, any `Risk and Financial Crime` mapping is part of the optional fourth-domain extension. In the required three-domain baseline, represent risk as a cross-domain capability consuming customer, account and transaction facts until a separate risk-domain boundary is justified.

| Capability | Primary domain relationship | Other relevant domain(s) | Why the mapping is not exclusive |
|---|---|---|---|
| Acquire and onboard customers | Customer and Servicing | Accounts and Products; Risk and Financial Crime | Onboarding establishes customer facts, creates an account relationship and may require risk checks. |
| Maintain customer information | Customer and Servicing | Risk and Financial Crime | Customer details may feed risk assessments, but that does not transfer ownership of the underlying address. |
| Open and maintain accounts | Accounts and Products | Customer and Servicing; Risk and Financial Crime | The account relationship references a customer and may be subject to risk controls. |
| Manage balances and statements | Accounts and Products | Transactions and Payments | Balances depend on posted transaction events and account rules. |
| Initiate and execute payments | Transactions and Payments | Accounts and Products; Customer and Servicing; Risk and Financial Crime | Payment execution uses account state, customer instructions and risk checks. |
| Record transactions | Transactions and Payments | Accounts and Products; Risk and Financial Crime | Transaction records affect balances and provide evidence for risk monitoring. |
| Assess customer and transaction risk | Risk and Financial Crime | Customer and Servicing; Accounts and Products; Transactions and Payments | Risk decisions consume customer, account and transaction facts. |
| Detect and investigate fraud | Risk and Financial Crime | Customer and Servicing; Transactions and Payments | Investigators need identity and transaction evidence. |
| Meet regulatory reporting obligations | Cross-domain capability; reporting authority to confirm | Customer and Servicing; Accounts and Products; Transactions and Payments; optional Risk and Financial Crime | Reportable facts originate across domains; the reporting asset's accountable role depends on the institution's decision rights. |
| Manage customer communications | Customer and Servicing | Accounts and Products; optional Risk and Financial Crime | Communications may be triggered by account events or constrained by approved risk decisions. |

**Beginner check:** explain why “Assess customer and transaction risk” uses several domains but does not automatically own the customer address, account balance and transaction record.

## 5. Intermediate-level learning sequence

### 5.1 Build and maintain a two-level capability map

A useful map has at least two levels: a business capability group and the capabilities within it. The map should be independent of the current system inventory.

**Construction method**

1. Start from business outcomes and obligations, not the application catalogue.
2. Name capability groups using stable business language.
3. Decompose each group into capabilities that are meaningful and distinguishable.
4. Check that the map is neither a list of projects nor a list of departments.
5. Link capabilities to processes, systems and data assets in separate views or a matrix.
6. Validate the vocabulary with business stakeholders and record unresolved terms.

**How to detect a weak map**

- A capability name includes a product/vendor name: likely implementation-centred.
- Two capabilities are indistinguishable in purpose or accountability: likely duplication or an unclear boundary.
- A capability has no process, system or people supporting it: it may be a genuine gap, a planned capability, or a modelling omission. Confirm which.
- Several systems support one capability: this may be legitimate channel variation, legacy overlap, duplication or a deliberate resilience strategy. Do not label it a defect without evidence.

### 5.2 Map capabilities to systems and assets

The matrix below is a worked, illustrative slice of the banking scenario. System names are generic placeholders, not verified products or systems from a real institution.

| Capability | Process example | Supporting system(s) | Important data asset(s) | Domain(s) | Observation / follow-up |
|---|---|---|---|---|---|
| Acquire and onboard customers | Digital/branch onboarding | Onboarding service; customer platform | Customer identity record; submitted address; verification result | Customer and Servicing; Risk | Confirm which address status is authoritative and how verification is evidenced. |
| Maintain customer information | Customer self-service and assisted correction | Mobile app; customer platform; operations console | Verified contact-address asset | Customer and Servicing | Three update channels; establish conflict resolution and correction authority. |
| Open and maintain accounts | Account opening and maintenance | Core banking platform; onboarding service | Account record; customer-account relationship | Accounts and Products; Customer and Servicing | Confirm system of record for each account attribute, not simply for the entire account concept. |
| Manage balances and statements | Posting and statement generation | Core banking platform; statement service | Posted transaction facts; balance snapshot; statement | Accounts and Products; Transactions and Payments | Balance is derived under account rules; reconcile to posted events. |
| Initiate and execute payments | Payment initiation and processing | Mobile app; payment service; core banking platform | Payment instruction; payment status | Transactions and Payments; Accounts and Products | Define status meanings and the hand-off to account posting. |
| Record transactions | Posting and transaction history | Core banking platform; transaction ledger | Transaction record | Transactions and Payments; Accounts and Products | Verify authoritative event, correction and reversal semantics. |
| Assess customer and transaction risk | Risk evaluation | Risk engine | Customer risk score; risk decision | Risk and Financial Crime | Risk domain creates score; document model/version and intended use separately if known. |
| Detect and investigate fraud | Alert review and investigation | Fraud case system; risk engine | Fraud alert; investigation case | Risk and Financial Crime; Transactions and Payments | Distinguish alert from confirmed fraud and from underlying transaction facts. |
| Meet regulatory reporting obligations | Prepare and reconcile a return | Reporting platform; warehouse | Regulatory reporting dataset | Reporting accountability to be confirmed | **Owner: UNKNOWN** until a formally accountable reporting role is identified. |
| Manage customer communications | Campaign/service communications | Customer engagement platform | Communication preference; campaign eligibility segment | Customer and Servicing; Risk and Financial Crime | Marketing consumes approved risk-derived data; it does not thereby own the score. |

#### Detecting gaps and overlaps

Use these diagnostics, then validate with evidence:

- **Capability gap:** a required capability has no identified process, system or accountable business role. Distinguish “not implemented” from “not yet mapped.”
- **System overlap:** multiple systems appear to support the same capability. Ask whether they serve distinct channels/products, provide resilience, reflect a migration, or duplicate functionality.
- **Asset duplication:** several copies or representations exist. Determine whether they are separate bounded assets (for example, current address vs. historical address) or competing versions of the same meaning.
- **Accountability gap:** a significant asset has no confirmed owner, or several teams each claim final authority without a decision rule.
- **Hidden dependency:** a capability relies on data owned by another domain, but no consumer contract, change notification or correction path is known.

Do not equate “more than one system” with failure. The risk lies in unexamined duplication, unclear authority and unmanaged change—not multiplicity alone.

### 5.3 Identify domain boundaries from meaning and vocabulary

A domain boundary is useful when it separates concepts that require distinct business rules, decisions or accountability. A boundary is not merely a team boundary, database schema, application boundary or organisational reporting line.

Ask:

1. **Meaning:** does a term mean different things in different contexts?
2. **Rules:** do different rules determine its lifecycle, validity or state?
3. **Authority:** who can make a binding decision about the definition?
4. **Risk:** who is accountable for errors and the consequences of use?
5. **Change:** can the concept change independently, and who needs to know?
6. **Coordination cost:** would combining the concepts make ownership too broad, or splitting them create excessive hand-offs?

**Example — “account”:** Customer service may use “account” to mean the customer-visible banking relationship; the ledger may use it to mean a posting destination; lending may use it to mean a loan facility; a merged legacy bank may use it for a product contract with different lifecycle states. These may be related concepts, but they need not be one identical domain definition. Preserve bounded definitions and map their relationships explicitly rather than forcing one universal definition.

### 5.4 Cross-domain dependencies

A dependency exists when one domain’s process or asset relies on another domain’s data or decisions. At minimum, document:

- **Provider and consumer:** who publishes/provides and who relies on the asset.
- **Purpose and meaning:** what the consumer believes the fields or states mean.
- **Authority:** who decides the source meaning and who decides the consumer’s derived interpretation.
- **Change impact:** which definitions, fields, states or delivery timing could break the consumer.
- **Correction path:** who corrects the source fact and who repairs downstream derived values.
- **Communication:** how consumers learn of changes and how unresolved issues are escalated.

**Three high-risk dependencies in the banking example**

1. **Customer identity/address → account servicing and communications.** Incorrect contact data may affect statements, customer contact and operational handling. Confirm correction authority, verification status and downstream refresh.
2. **Account state/balance ↔ transaction events.** Balance calculations depend on posting, reversal and transaction-state rules. Misaligned definitions can cause reconciliation errors.
3. **Customer + account + transaction data → risk score and fraud decisions.** Risk outputs inherit the quality and semantics of inputs. Consumers need to know score meaning, freshness, limitations and which domain can correct each input.

These rankings are illustrative risk hypotheses. A real prioritisation must use evidence about impact, exposure, regulatory obligations, volumes and actual failure history.

### 5.5 Ownership register: ten representative assets

**Status convention**

- `CONFIRMED` means the responsible organisation has explicitly validated the owner and authority. No real bank is provided here, so the example register intentionally uses `PROPOSED—VALIDATE` or `UNKNOWN`, not fabricated confirmation.
- `PROPOSED—VALIDATE` is an illustrative candidate, not a verified fact. The current ten-row register uses `UNKNOWN` for owner and steward because no accountable role has been evidenced or accepted.
- `UNKNOWN` means there is insufficient evidence to name an accountable owner. It is a valid state and must carry a resolution action.
- A team/system name in the producer or consumer columns is illustrative where stated; it is not an assertion that a real bank uses that arrangement.

| ID / bounded asset | Domain | Accountable owner | Steward | Producers | Consumers | Status / next action | Source / evidence type | Review trigger |
|---|---|---|---|---|---|---|---|---|
| A01 — Verified customer identity and core profile | Customer and Servicing | `UNKNOWN` | `UNKNOWN` | Onboarding service; operations correction workflow (illustrative) | Account opening; servicing; risk | **UNKNOWN:** validate business authority for identity attributes and correction rights. | Assumed illustrative flow; no bank policy or owner acceptance supplied. | Identity-definition or verification-policy change; identity incident; accountable-role confirmation. |
| A02 — Verified customer contact address | Customer and Servicing | `UNKNOWN` | `UNKNOWN` | Onboarding; mobile app; operations (illustrative) | Statements; servicing; approved communications | **UNKNOWN:** confirm authoritative status, correction hierarchy and accountable role. | Assumed illustrative flow; scenario states the three channels but supplies no formal decision-rights evidence. | Address incident; verification-rule change; repeated correction conflict; owner confirmation. |
| A03 — Customer communication preference | Customer and Servicing | `UNKNOWN` | `UNKNOWN` | Mobile app; contact-centre workflow (illustrative) | Service communications; marketing eligibility | **UNKNOWN:** distinguish customer preference from channel delivery settings. | Assumed illustrative asset; no source-of-authority evidence supplied. | Consent/preference definition or channel-use change; complaint; owner confirmation. |
| A04 — Customer-account relationship | Accounts and Products | `UNKNOWN` | `UNKNOWN` | Onboarding; core banking (illustrative) | Servicing; balances; risk; reporting | **UNKNOWN:** confirm authority over relationship lifecycle and identifiers. | Assumed illustrative flow; no actual system-of-record evidence supplied. | Relationship lifecycle or identifier change; merger mapping; reconciliation incident. |
| A05 — Account product terms and lifecycle state | Accounts and Products | `UNKNOWN` | `UNKNOWN` | Core banking/product administration (illustrative) | Servicing; balances; reporting | **UNKNOWN:** confirm attribute-level authority, particularly post-merger. | Assumed illustrative flow; legacy definitions and decision rights not supplied. | Product/lifecycle-rule change; merger milestone; state-mapping defect. |
| A06 — Posted transaction record | Transactions and Payments | `UNKNOWN` | `UNKNOWN` | Core posting/transaction service (illustrative) | Balances; statements; risk; reporting | **UNKNOWN:** validate authoritative event, reversal and correction semantics. | Assumed illustrative flow; ledger/event evidence not supplied. | Posting/reversal rule change; reconciliation failure; correction-control change. |
| A07 — Payment instruction and processing status | Transactions and Payments | `UNKNOWN` | `UNKNOWN` | Mobile/web channels; payment service (illustrative) | Payment operations; account posting; customer servicing | **UNKNOWN:** identify business role accountable for status definitions and exceptions. | Assumed illustrative flow; payment-status contract not supplied. | Status/exception definition change; payment incident; new consumer. |
| A08 — Customer risk score | Optional Risk and Financial Crime extension | `UNKNOWN` | `UNKNOWN` | Risk scoring process/engine (illustrative) | Risk operations; marketing only under an approved use (illustrative) | **UNKNOWN:** identify accountable risk role; record model and use limitations separately. | Scenario-supported existence of a derived score; model, owner and approved-use evidence not supplied. | Model/feature/version change; new use or consumer; source-definition change; material score incident. |
| A09 — Fraud alert and investigation case | Optional Risk and Financial Crime extension | `UNKNOWN` | `UNKNOWN` | Risk engine; investigator workflow (illustrative) | Fraud operations; authorised risk reporting | **UNKNOWN:** distinguish generated alert from adjudicated case outcome. | Illustrative extension; no case workflow or decision-rights evidence supplied. | Alert/case lifecycle change; material incident; investigation-control change. |
| A10 — Regulatory reporting dataset | Cross-domain reporting; lead domain to confirm | `UNKNOWN` | `UNKNOWN` | Reporting transformations; contributing domains (illustrative) | Regulatory reporting and control functions | **UNKNOWN:** identify formally accountable reporting role and source-data sign-offs. | Illustrative asset; report definition, applicable requirements and formal accountability not supplied. | Report-definition/control change; reporting incident; source-domain or ownership change. |

This example deliberately does not invent people, titles or confirmed ownership. The producer/consumer arrangements are illustrative, not verified facts about a real bank. A production register would replace `UNKNOWN` only after evidence is obtained and the relevant role accepts accountability. A steward can also remain unknown; do not silently assume the owner performs stewardship. Evidence labels distinguish assumptions from observations: the scenario gives a few stated facts, but no real bank policy, role assignment or system-of-record proof is supplied.

### 5.6 Trace an asset to an accountable owner

Use this traceability sequence for any significant asset:

```text
Capability using the asset
  → process and decision supported
  → asset definition and boundaries
  → source / producers and transformation history
  → business authority for its meaning
  → risk-bearing accountable owner
  → steward and correction workflow
  → consumers and dependency/change notification
  → evidence, status and next review date
```

If the chain breaks at “business authority” or “risk-bearing accountability,” record the owner as `UNKNOWN` and assign a discovery action. Do not use the system administrator, most frequent producer, or loudest consumer as a proxy for the owner without confirming their authority.

### 5.7 Worked exercise with solution

**Problem:** The mobile application and operations team both change the customer address. The statement service uses the address. The CRM team says it owns the data because it stores a copy.

**Reasoning**

1. The asset must be bounded: for example, “verified customer contact address,” not all fields labelled address in every system.
2. Producers include onboarding, mobile and operations if each can submit or apply changes.
3. A system storing a copy is not evidence of business authority.
4. The accountable owner must be able to decide the address definition, verification requirements, correction priority and acceptable quality.
5. A steward should maintain the rules and coordinate defects; the statement service is a consumer and needs change propagation.
6. If the bank has not established the accountable role, the register remains `UNKNOWN`. A proposed owner may be recommended, but not represented as fact.

**Worked answer:** record `UNKNOWN` until authority is verified; identify the candidate business role through the customer-data decision-rights process; keep the CRM team as a technical custodian/producer where appropriate; document the address definition, correction workflow and consumer impact; revisit once the role is formally accepted.

### 5.8 Independent practice tasks

Complete these without looking at the worked answer first.

1. Choose five capabilities from the map. For each, name one process, two systems or system types, and two assets. Mark every assumption.
2. Find one capability with multiple systems. List three plausible explanations for the overlap and the evidence needed to distinguish them.
3. Choose the word “customer” or “account.” Write two legitimate bounded definitions and explain which decisions each supports.
4. Complete an ownership register row for a transaction asset. If authority is unknown, write `UNKNOWN` and specify a discovery action.
5. Identify three cross-domain dependencies. Rank them using impact, likelihood, and evidence quality rather than intuition alone.

## 6. Advanced-level learning sequence

### 6.1 Ownership is a decision, not a guess

Ownership disputes often arise because several parties have legitimate but different relationships to an asset. A source team may create it; a consumer may depend on it; a platform team may store it; a risk function may be accountable for its interpretation. These are distinct claims.

Use four primary criteria:

1. **Creation:** who originates or materially changes the facts?
2. **Authority over meaning:** who is empowered to define the asset and its valid states?
3. **Risk accountability:** which role is answerable for the consequences of incorrect, incomplete or misused data?
4. **Ability to correct:** who can authorise and carry out correction at the source or cause the authoritative correction to happen?

These criteria are evidence to weigh, not an automatic scoring formula. Creation alone is insufficient; a data-entry channel may capture information without owning the business meaning. Ability to correct matters operationally, but a technical team able to update a database may not have authority to decide the correct value. Risk accountability and authority over meaning are usually strong signals, but they still need to be confirmed in the organisation’s actual decision rights.

### 6.2 Shared, derived, cross-domain and ownerless assets

- **Shared data:** several domains use the same underlying fact. Shared use does not necessarily require shared accountability. One owner may be accountable for the source fact while consumers maintain their own derived representations.
- **Derived data:** a domain applies rules, aggregation or a model to source data. The derived asset needs an owner for its own meaning, calculation, quality and intended use. That owner does not automatically become owner of the source assets.
- **Data produced by one domain for another:** the producing domain may own the published asset’s definition and production quality; the consuming domain owns its local decision or derived interpretation. The contract between them must make meaning, limitations and changes clear.
- **Asset without an obvious owner:** record `UNKNOWN`, the evidence missing, the risk of leaving it unresolved, a person responsible for discovery, and a target review date. Do not disguise a governance gap with an assumed title.
- **Shared ownership:** use only when the decision rights are explicit. If several parties are jointly consulted but nobody can make the final decision, the arrangement is not accountable ownership.

### 6.3 Domain boundaries: too broad, too narrow or misaligned

**Overly broad domain:** “All Bank Data” or “Customer and Everything Related.” The domain becomes too heterogeneous for one role to understand and govern its meanings. Different concepts have different lifecycles, risks and correction paths.

**Overly narrow domain:** a separate domain for each application table or small team. This multiplies interfaces and coordination costs, fragments concepts that share rules, and makes accountability harder to sustain.

**Misaligned with the organisation:** domains are based only on today’s departments. A reorganisation then appears to require redesigning every domain. Prefer business meaning and durable responsibility as the starting point; organisational structure is evidence about authority and operating capacity, not the only determinant.

**Practical test:** a boundary is plausible when the concepts inside it share meaningful vocabulary, lifecycle rules and decision authority, while the interactions with other domains can be described through explicit dependencies. It is not necessary for every term to be globally unique. Multiple bounded definitions are legitimate when context changes the meaning; the architecture should name the contexts and their relationships.

### 6.4 What changes when the organisation changes?

- **Merger:** legacy terms and identifiers may collide. Do not assume identical labels have identical semantics. Preserve source context, compare definitions and lifecycle rules, decide which concepts are aligned, mapped or kept distinct, and document transitional ownership.
- **Reorganisation:** the domain may remain valid while its accountable role changes. Update the role assignment, decision rights and escalation path; do not assume the old team retains authority.
- **Owner departure:** ownership should be assigned to a durable role, not depend entirely on a named individual. Until a successor formally accepts accountability, record the assignment gap and temporary escalation authority.
- **Change in data responsibility:** if another domain takes over creation, correction or business decisions, revisit the ownership decision rather than assuming the producer or owner is unchanged.
- **Evidence changes:** incident history, audit findings, new regulations, product changes or repeated correction failures can invalidate the earlier rationale. The decision log needs a review trigger.

### 6.5 Three worked contested-ownership cases

The cases below are illustrative and show how to reason. The recommended role names are candidates for a hypothetical bank; they are not verified facts about a real organisation.

#### Case 1 — Shared customer identity and address across three channels

**Situation:** onboarding captures an address, the mobile app permits changes, and operations can correct errors. CRM stores a copy and statement generation consumes an address.

| Element | Analysis |
|---|---|
| Competing claims | Onboarding says it collected the original identity/address; mobile says it accepts the latest customer change; operations says it corrects defects; CRM says it stores a profile copy; statements needs reliable contact data. |
| Asset boundary | Treat verified customer identity and verified contact address as related but separately defined assets. One role may own both only if decision-rights evidence supports that assignment. |
| Alternatives considered | Assign ownership to onboarding because it captures the first value; assign it to CRM because it stores a copy; split ownership by channel; or designate one accountable role per bounded asset after validating authority. |
| Decision criteria | Authority over the definition of “verified contact address”; risk of misdirected statements or failed contact; evidence of verification; ability to authorise correction; consistency across channels. |
| Recommended accountability | One formally authorised **Customer Information Owner** (or equivalent business role) accountable for the bounded verified-address asset. Operations and digital channels are producers/change channels; a customer-data steward coordinates rules and defects. CRM is not owner solely because it stores a copy. |
| Rationale | The owner must decide what counts as current and verified, how conflicts are resolved, and which corrections propagate. Multiple producers do not require multiple owners. |
| Risks | Without a confirmed owner, conflicting edits, stale downstream copies and unclear correction responsibility may persist. Over-centralising every correction can also slow operations. |
| Review trigger | A material address-related incident, new verification requirement, repeated correction failures, change in authority, or a change in the customer-data operating model. |
| Evidence still needed | The bank’s actual decision-rights policy, customer-data definition, current correction workflow and accountable-role acceptance. Until verified, the register owner remains `UNKNOWN`. |

**Decision:** recommend a single accountable business role for the defined asset, while keeping the owner `UNKNOWN` in the illustrative register until that role is confirmed. This separates the architectural recommendation from an unsupported claim about current reality.

#### Case 2 — Risk domain creates a customer risk score consumed by marketing

**Situation:** a risk team calculates a score from customer, account and transaction inputs. Marketing uses the score or a segment derived from it to target communications.

| Element | Analysis |
|---|---|
| Competing claims | Risk says it owns the score and model interpretation; marketing says it needs to control segment meaning and campaign use; source domains own the underlying customer/account/transaction facts; platform engineering operates the scoring pipeline. |
| Alternatives considered | Assign the score to a source-data domain because it supplies inputs; assign it to Marketing because Marketing consumes it; assign it to Engineering because Engineering runs the pipeline; or separate score accountability from campaign-segment accountability. |
| Decision criteria | Who defines score meaning and acceptable quality; who bears the risk of a wrong score; who can correct the score calculation; who controls marketing’s derived segment and use; whether the score is suitable for the proposed purpose. |
| Recommended accountability | The authorised **Risk Data Owner** is accountable for the risk-score asset, including its definition, calculation governance and limitations. Marketing is accountable for its own derived campaign segment and campaign decision. Source-data owners remain accountable for their source facts. Engineering is responsible for implementation and operation, not unilateral business interpretation. |
| Rationale | The derived score is a distinct asset. Ownership of its source inputs does not automatically transfer to Risk, and consumption does not transfer ownership to Marketing. Each derived layer has its own meaning and accountable decision. |
| Risks | Misuse outside intended purpose, stale or unexplained scores, source-data defects incorrectly “fixed” in the score, or marketing treating a risk score as a universal customer value label. |
| Review trigger | A model or feature change, a change in score meaning, a material risk incident, a new consumer or use, a source-definition change, or evidence that consumers misunderstand limitations. |
| Evidence still needed | Formal risk decision rights, approved score definition, intended-use restrictions and the role authorised to approve consumer use. Until confirmed, record the owner as `UNKNOWN`. |

**Decision:** recommend Risk as the accountable domain for the score and Marketing for its distinct derived campaign segment, subject to confirmation of formal authority. Record the source dependencies and the permitted-use boundary. Do not call the recommendation a verified assignment until accepted.

#### Case 3 — Merger creates two meanings of “account”

**Situation:** Bank A uses “account” for a customer-facing deposit relationship; Bank B uses it for a product contract or posting destination. A merger programme proposes one enterprise-wide account definition to simplify reporting.

| Element | Analysis |
|---|---|
| Competing claims | Retail servicing wants one customer-friendly definition; ledger operations needs posting semantics; lending uses a facility/contract concept; the merger programme wants a common term; reporting wants comparable measures. |
| Alternatives considered | Force one global “account” definition immediately; retain every legacy concept without mappings; or preserve distinct bounded concepts and create explicit mappings/common reporting semantics where evidence supports them. |
| Decision criteria | Business meaning and lifecycle rules; decisions supported by each definition; consequences of incorrect joins or aggregation; authority over each concept; feasibility and risk of migration; whether a common abstraction preserves required distinctions. |
| Recommended accountability | Do not force a single definition immediately. Keep bounded concepts such as **Customer Account Relationship**, **Ledger Posting Account** and **Credit Facility/Contract** where evidence shows distinct meaning. Assign an accountable owner to each concept through the relevant business authority; appoint a cross-domain decision forum for the mapping and shared reporting definition. |
| Rationale | Identical labels are not proof of semantic identity. A shared reporting view can map the concepts without pretending the underlying concepts are the same. The merger decision should preserve distinctions needed for operations, controls and valid reporting. |
| Risks | Incorrect joins, double counting, invalid balance aggregation, migration errors, confusing customer-facing and ledger meanings, and prolonged ambiguity if no decision date exists. |
| Review trigger | Completion of the account-concept inventory, evidence of common lifecycle semantics, a migration milestone, a reporting/control incident, or a decision to retire one legacy concept. |
| Evidence still needed | Both banks’ data definitions, product/ledger rules, sample lifecycle events, reporting requirements and accountable decision rights. Until reviewed, owner assignments for the merged concept remain `UNKNOWN` where no authority is confirmed. |

**Decision:** preserve bounded definitions where business meaning differs; define mappings and shared reporting semantics explicitly; assign accountable roles per bounded asset. Revisit consolidation only when evidence shows that definitions and decision rules are genuinely compatible.

### 6.6 Record the contested decision

A decision log should be understandable by someone who was not in the meeting. Capture:

- Decision ID and date.
- Asset and the precise meaning/boundary under discussion.
- Context and evidence sources.
- Competing claims and options considered.
- Criteria applied and why those criteria matter.
- Decision, accountable role and any temporary/unknown status.
- Rationale, consequences and accepted risks.
- Producers, consumers and cross-domain dependencies affected.
- Actions, action owner and due date.
- Review trigger and review date/status.

Avoid recording only “Owner: Risk” or “Agreed in meeting.” Those statements omit the asset boundary, authority, rationale and circumstances under which the decision should change.

### 6.7 Worked ownership decision log

| ID | Asset / contested issue | Decision or current status | Rationale | Risks / follow-up | Review trigger |
|---|---|---|---|---|---|
| D-01 | Verified customer contact address | Recommend one Customer Information Owner; current owner `UNKNOWN` pending authority validation. | Several channels can update the same bounded fact; storage location and initial capture do not prove ownership. | Validate role authority, verification rules, correction workflow and downstream propagation. | Address incident, policy change or ownership confirmation. |
| D-02 | Customer risk score and marketing segment | Recommend Risk owns the score; Marketing owns its separately derived campaign segment; both assignments require formal confirmation. | The score and campaign segment have different meanings, decisions and risks. Source facts remain owned by their respective domains. | Confirm score use restrictions, model accountability, source dependencies and campaign controls. | Model/use change, new consumer or material incident. |
| D-03 | “Account” after merger | Preserve bounded account concepts until semantic comparison; owner `UNKNOWN` for any newly proposed unified concept. | Different legacy meanings may be legitimate; a single label cannot justify semantic consolidation. | Compare lifecycle, identifier and reporting semantics; define mappings and accountable roles. | Inventory completion, migration milestone or evidence of semantic equivalence. |

### 6.8 Ownership conflict decision method

For a new dispute, use the following sequence:

1. **Bound the asset.** State what it represents, what is included/excluded, and the business decision it supports.
2. **Separate layers.** Identify source facts, transformed/derived assets, operational copies and consumer-specific interpretations.
3. **List claims.** Record who creates, defines, uses, corrects, operates and bears risk.
4. **Gather evidence.** Definitions, process documentation, decision rights, incidents, controls and actual correction behaviour.
5. **Apply the four criteria.** Creation, authority over meaning, risk accountability and ability to correct.
6. **Choose an accountable role or mark unknown.** Consultations can be many; final accountability must be explicit.
7. **Document dependencies and controls.** Specify change notification, correction paths and downstream impacts.
8. **Record uncertainty and review trigger.** If evidence is incomplete, say so and make the gap actionable.

This method is intentionally not a universal formula. Some organisations have statutory, contractual or formally delegated decision rights that override a simple inference from who creates or corrects the data. The evidence and actual authority must govern the decision.

## 7. Industry-application exercises

Use the banking scenario as a single consistent case. All system names and candidate role names in this lesson are illustrative assumptions, not verified facts about a real institution.

### Exercise A — Build the capability and domain view

1. Use the two-level capability map in Section 4.6.
2. Select at least ten capabilities and map each to a primary domain and any relevant secondary domains.
3. Explain every cross-domain relationship in one sentence.
4. Identify at least one capability gap and one possible overlap; state what evidence is required before calling them actual defects.

**Worked solution outline:** onboarding relates to Customer and Servicing, Accounts and Products, and Risk and Financial Crime because it establishes customer facts, may create an account relationship, and may trigger risk checks. The capability is not exclusively owned by the system that starts the workflow. A missing system in the matrix is a candidate gap only after confirming the capability is required and not delivered manually or through an unmapped service.

### Exercise B — Customer address ownership

Use the three-channel address case. Deliver:

- Bounded asset definition.
- Owner and steward candidates, or `UNKNOWN`.
- Producer and consumer lists.
- Correction and change-notification path.
- Evidence still needed and review trigger.

**Worked solution outline:** use “verified customer contact address” as a candidate bounded asset. Treat onboarding, mobile and operations as producers/change channels. Treat statements and servicing as consumers. Do not infer ownership from CRM storage. If authority has not been confirmed, set owner to `UNKNOWN`; record the role-validation action.

### Exercise C — Risk score ownership

Draw this dependency chain:

```text
Customer facts ─┐
Account facts ──┼──> Risk scoring process ──> Customer risk score
Transaction facts┘                              │
                                                ├──> Risk operations
                                                └──> Marketing segment (derived asset)
```

For each arrow, identify the provider, consumer, meaning and change impact. Explain why the risk score and marketing segment need separate ownership decisions.

**Worked solution outline:** source domains remain accountable for source facts; Risk is the candidate owner for score meaning and calculation; Marketing is the candidate owner for the derived campaign segment and its campaign use. Formal roles must be confirmed. A source correction may require score recomputation and downstream segment refresh, so the change path must be documented.

### Exercise D — Merger and the word “account”

1. Collect both legacy definitions and lifecycle states.
2. List decisions that each definition supports.
3. Identify which attributes or relationships can be mapped safely and which require separate semantics.
4. Recommend a temporary boundary and a review trigger.
5. Mark unknown ownership rather than inventing an owner for the unified concept.

**Worked solution outline:** preserve bounded definitions where meaning differs; map them through explicit relationships for reporting or migration; do not merge semantics merely because the same label is used. Review after the semantic inventory and business authority have been validated.

### Exercise E — Find the three highest-risk dependencies

Start with the three candidates in Section 5.4. Rank them using a transparent method, for example:

- Impact if the dependency fails: low / medium / high, with reason.
- Likelihood based on evidence: low / medium / high; if no evidence exists, label it an assumption.
- Detectability and recovery: easy / moderate / difficult.
- Evidence confidence: verified / reported / assumed.

Do not manufacture numeric risk scores from unsupported precision. Explain what information would change your ranking.

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — “The CRM team owns customer data”

**Question:** Is this sufficient?

**Answer:** No. It names a team and a system context, but does not define the asset, accountable business authority, steward, producers, consumers or correction rights. Replace it with an asset-specific statement and confirm the accountable role. CRM may operate or store the data without owning every business meaning represented in its tables.

### Scenario 2 — A capability has no identified system

**Question:** Is the capability missing?

**Answer:** Not necessarily. It may be performed manually, supported by an unrecorded service, planned but not implemented, or omitted from the mapping. Validate the business need, process, people and system inventory. Record a genuine implementation gap only when evidence supports it.

### Scenario 3 — A data engineer can correct the record directly

**Question:** Does that make the engineer the owner?

**Answer:** No. Technical ability to update a record is not authority to determine the correct business value. The engineer may execute a correction authorised by the owner or steward. Emergency remediation should preserve evidence and use the approved escalation path.

### Scenario 4 — Two domains use different definitions of “customer”

**Question:** Must one definition be selected globally?

**Answer:** Not automatically. Identify each bounded meaning and the decision it supports. If a shared enterprise view is needed, define a mapping and explain what it preserves or loses. Standardise only where the meanings and rules are genuinely compatible or where a deliberate business decision accepts the consequences.

### Scenario 5 — The owner leaves the organisation

**Question:** Does ownership disappear?

**Answer:** The accountable role should be durable, but the assignment may be vacant. Record the vacancy, temporary escalation authority, risk, replacement action and due date. Do not treat a departed individual as an enduring owner. Revalidate after the successor accepts the role.

### Scenario 6 — A consumer disputes a source definition

**Question:** Can the consumer redefine the source asset?

**Answer:** The consumer should raise evidence and can own its own derived interpretation, but should not silently redefine the source asset. The source owner decides the source meaning through the agreed decision process; affected consumers must be consulted and the impact recorded. If the source owner is unknown or authority is contested, escalate and mark the gap explicitly.

### Scenario 7 — A merger team insists on one account definition

**Question:** How should the architect respond?

**Answer:** Ask which business decisions the unified definition must support, compare lifecycle and identifier semantics, and test whether one abstraction preserves required distinctions. A common reporting layer can be useful without claiming that all legacy concepts are identical. Record the decision, risk and review trigger.

## 9. Expected outputs or deliverables

Complete the following artefacts and keep assumptions separate from verified organisational facts.

### 9.1 Capability map

- Two levels: capability group and child capability.
- The ten banking capabilities in Section 4.6 (extensions must be labelled separately).
- Capability names that describe business ability, not application names.
- Links to relevant domains; allow multiple relationships where justified.

### 9.2 Domain relationship map

Use a text diagram or equivalent. The required baseline has three domains; the diagram below shows the optional fourth-domain extension used for the advanced risk-score and fraud cases. The additional domain must not be confused with the three-domain beginner exercise.

```text
                   ┌───────────────────────────┐
                   │ Customer and Servicing    │
                   │ identity, contact, service│
                   └─────────────┬─────────────┘
                                 │ customer facts / requests
               ┌─────────────────┼──────────────────┐
               │                 │                  │
               ▼                 ▼                  ▼
┌────────────────────────┐  ┌──────────────────────┐  ┌───────────────────────┐
│ Accounts and Products  │  │ Transactions and     │  │ Risk and Financial     │
│ relationship, terms,   │◄─►│ Payments             │─►│ Crime                 │
│ balances               │  │ instructions/events  │  │ scores, alerts, cases │
└────────────┬───────────┘  └──────────────────────┘  └───────────┬───────────┘
             │ account facts / balances                          │
             └───────────────────────────────────────────────────┘
                                  risk inputs / decisions

All arrows are illustrative dependencies, not claims about a real bank's current
architecture. Label each relationship with the data or decision being exchanged.
```

### 9.3 Capability–system–asset matrix

Include at least five capability rows and identify the systems, assets, domains and follow-up questions. The worked matrix in Section 5.2 is the baseline.

### 9.4 Ownership register

Include at least ten assets and these exact fields:

- Asset ID and asset definition.
- Domain.
- Accountable owner.
- Steward.
- Producers.
- Consumers.
- Status.
- Evidence or next action.
- Review trigger (recommended for maintainability).

Every asset must have an accountable owner or explicit `UNKNOWN`. Do not use an empty cell when the correct state is unknown.

### 9.5 Ownership decision log

Record at least three contested cases. Each must show:

- Competing claims.
- Decision criteria.
- Recommended accountability or explicit unknown status.
- Rationale.
- Risks and follow-up actions.
- Review trigger.
- Evidence still required.

### 9.6 Practice-question alignment and model-answer crosswalk

The following crosswalk aligns this lesson to Section C of `practice-questions.md` (C3.1–C3.11). These are model-answer criteria, not claims about a real bank. Use them after attempting each question: mark your response `correct`, `partly correct` or `wrong`, give one sentence of justification, and revise any incomplete answer.

| Practice ID | Model answer / evidence expected | Where this lesson supports it |
|---|---|---|
| **C3.1 — Distinguish the building blocks** | A capability is what the bank can do (manage onboarding); a process is how it does it (collect, verify and approve an application); a domain is bounded business meaning/responsibility; a system implements or supports work; a data asset is a bounded meaningful collection such as a verified customer profile. Do not name an application as the capability. | Sections 4.1–4.4; capability map in 4.6. |
| **C3.2 — Owner versus steward** | The owner is accountable for meaning and material decisions; the steward maintains definitions, quality rules and issue coordination; producers create/change/publish data; consumers use it. “CRM team owns customer data” is insufficient because storage or operation does not establish business decision rights. Name a confirmed accountable role or use `UNKNOWN`. | Sections 2.2, 4.1, 4.5 and 5.6. |
| **C3.3 — Capability-to-system-to-asset map** | Use the Section 5.2 matrix as a starting point for onboarding, account servicing (represented through account opening/maintenance and servicing consumers), and credit-risk assessment (represented by risk assessment). It includes more than three system types and five assets. Multiple systems may support one capability. No real capability gap is asserted without evidence; an unmapped system is a candidate gap until process/system discovery confirms it. Owner unknowns remain explicit in Section 5.5. | Sections 4.4, 5.1–5.2 and 5.5. |
| **C3.4 — Domain boundaries** | Compare each “customer” definition’s scope, lifecycle, identifiers, business/legal meaning, rules, decisions and consumers. Preserve distinct or related concepts if meanings differ; map them when needed. Similar labels alone do not prove equivalence. | Sections 5.3 and 8.4. |
| **C3.5 — Ten-asset ownership register** | Section 5.5 contains ten rows and fields for asset, domain, owner, steward, producers, consumers and status, plus source/evidence type, next action and review trigger. All ten owners and stewards are explicitly `UNKNOWN` because no real bank decision-rights evidence was supplied; the illustrative producer/consumer entries are labelled as assumptions. | Section 5.5. |
| **C3.6 — Cross-domain dependencies** | The three illustrative high-risk dependencies are (1) customer identity/address to servicing and communications, (2) account state/balance with transaction events, and (3) customer/account/transaction facts to risk/fraud outputs. For each, document provider, consumer, purpose, impact, correction path and change notification. The ranking is a hypothesis until actual impact/likelihood evidence is collected. | Section 5.4 and Exercise E. |
| **C3.7 — Customer address entered in multiple places** | Define the asset precisely (verified contact address), treat onboarding/mobile/operations as producer or change channels, and do not assign ownership to the first capturer, last editor or CRM. Validate who can define verification/correction rules and bears the risk. Until confirmed, keep owner `UNKNOWN` and track the evidence needed. | Sections 4.5, 5.5, 5.7, 6.5 Case 1 and Exercise B. |
| **C3.8 — Derived customer risk score** | Risk is a plausible candidate owner of the score’s meaning and calculation, but the accountable role must be confirmed. Record definition, inputs, method/version, intended uses, limitations, quality expectations, producers, consumers and change/approval process. Marketing may own its derived campaign segment and campaign decision; it does not thereby own the score or source facts. | Sections 5.2, 6.2, 6.5 Case 2 and Exercise C. |
| **C3.9 — Merger brings a different account definition** | Compare definitions, lifecycle states, identifiers, product/legal context, source rules and consumers. Classify concepts as equivalent, overlapping or distinct; map them where useful; preserve differences when meanings differ; record ownership, unresolved questions and review trigger. Do not force one global definition solely for reporting convenience. | Sections 5.3, 6.4, 6.5 Case 3 and Exercise D. |
| **C3.10 — Ownership changes after reorganisation** | Mark a departed owner’s assignment pending/unknown; use an interim role only if formally authorised; transfer definitions, decisions and open issues; notify consumers; confirm the successor; update the register and related decision logs. | Sections 6.4 and 8.5. |
| **C3.11 — Three contested ownership decisions** | Case 1 separates customer identity/address from channel and storage claims; Case 2 separates the risk score from Marketing’s derived segment and source facts; Case 3 preserves distinct account concepts until semantic evidence supports alignment. Each case records competing claims, alternatives, criteria, decision, rationale, risks, evidence still needed and a review trigger. Recommended roles remain unverified until formally accepted. | Sections 6.5–6.7. |

**Coverage note:** the lesson gives worked reasoning and an answer crosswalk for all eleven C3 questions. Use `practice-questions.md` for the complete prompts and scoring expectations; do not treat these model answers as substitutes for completing the independent exercises or validating real organisational evidence.

## 10. Common mistakes and misconceptions

1. **Mapping systems instead of capabilities.** Start from business abilities and outcomes; then map the systems that support them.
2. **Treating a process as a capability.** A process is a sequence of work; a capability is the ability the organisation needs to retain.
3. **Assuming a capability belongs to exactly one domain.** A capability may depend on several domains; show primary and secondary relationships explicitly.
4. **Assuming one domain must equal one department.** Organisation charts are evidence about accountability, not the only basis for a semantic boundary.
5. **Naming a team or application as the owner.** Identify an accountable business role for a bounded asset. Record technical custodianship separately.
6. **Confusing owner and steward.** The owner is accountable for the asset and material decisions; the steward maintains definitions, quality practices and issue coordination on the owner’s behalf.
7. **Assuming the producer owns the asset.** Creation is one criterion, not the whole decision. A capture channel may not control meaning or risk.
8. **Assuming the consumer owns source data.** Consumption does not transfer source authority. A consumer may own its own derived asset.
9. **Inventing ownership to make a table look complete.** Use `UNKNOWN`, state the missing evidence and create an action to resolve it.
10. **Forcing one global definition.** Bounded definitions can be legitimate. Define contexts and mappings; standardise only when there is a defensible business reason.
11. **Treating every overlap as a defect.** Multiple systems or domains may be intentional. Diagnose the reason before recommending consolidation.
12. **Treating a derived score as the source facts.** Derived data needs its own meaning and owner; source owners remain accountable for their facts.
13. **Treating ownership as permanent.** Mergers, reorganisations, new uses and incidents can change the rationale. Record review triggers.
14. **Making the register a static spreadsheet.** Assign a maintenance responsibility and update it when assets, meanings, owners or dependencies change.
15. **Writing a decision without evidence.** A defensible decision records context, alternatives, criteria, consequences and the basis for the chosen role.
16. **Using “shared ownership” to avoid conflict.** Shared consultation can be useful, but final accountability and escalation must remain explicit.
17. **Confusing technical ability with authority.** The person who can edit the database is not necessarily authorised to decide what the value should be.
18. **Ignoring consumers when source meaning changes.** A source owner can decide the source definition, but affected consumers need impact assessment and change communication.

## 11. Mastery criteria

You have mastered this lesson when you can demonstrate all of the following without relying on memorised slogans:

- **Conceptual accuracy:** distinguish capability, process, domain, system, data asset, owner, steward, producer and consumer, with examples.
- **Capability mapping:** produce a two-level map with the ten required capabilities without turning it into an application inventory or organisation chart.
- **Many-to-many reasoning:** explain why capabilities and domains can have multiple relationships and show them consistently.
- **Traceability:** follow a significant asset from a capability through process, systems and producers to its accountable owner—or mark ownership `UNKNOWN`.
- **Gap and overlap diagnosis:** distinguish a confirmed gap from a mapping omission, and explain why system overlap is not automatically a defect.
- **Domain boundaries:** justify a boundary using meaning, rules, authority, risk, change and coordination cost; preserve legitimate bounded definitions.
- **Register quality:** complete ten asset entries with owner/steward/producers/consumers/status and explicit unknowns.
- **Cross-domain dependencies:** identify provider, consumer, purpose, correction path and change impact for at least three high-risk dependencies.
- **Ownership conflict reasoning:** resolve three contested cases using creation, authority over meaning, risk accountability and ability to correct.
- **Decision quality:** state alternatives, evidence, rationale, risks, actions and a review trigger; separate assumptions from verified facts.
- **Communication:** produce artefacts that a business owner, architect or engineer can use without needing an oral explanation of every row.

A reviewer should be able to challenge the decisions and see how the evidence and criteria lead to the conclusion. A different decision can still be defensible if it uses sound evidence, makes the asset boundary explicit and records the trade-offs.

## 12. Completion gate

Do not mark this lesson complete until each item is satisfied.

- [ ] Capability map has two levels and the ten required banking capabilities; any extension is clearly separated.
- [ ] Domain relationship map shows customer, account and transaction dependencies and labels the exchanged data or decision.
- [ ] Capability–system–asset matrix is complete enough to identify gaps, overlaps and follow-up questions.
- [ ] Ownership register covers ten representative assets and includes asset, domain, owner, steward, producers, consumers and status.
- [ ] Every register entry has an owner or explicit `UNKNOWN`; no unknown is silently filled with an assumed person or team.
- [ ] Three highest-risk cross-domain dependencies are identified with reasons and evidence confidence.
- [ ] Three contested ownership cases are resolved or explicitly left pending evidence, with claims, criteria, recommendation, rationale, risks and review triggers recorded.
- [ ] Banking scenarios cover the address changed during onboarding/mobile/operations, a risk score consumed by marketing, and the merger’s competing definitions of “account.”
- [ ] Independent practice questions are answered, checked and corrected.
- [ ] Assumptions are labelled as illustrative and are not represented as verified facts.
- [ ] A reviewer can trace a significant asset to an accountable owner or see a documented action to resolve `UNKNOWN`.

**Completion standard:** the map, matrix, register and decision log must be internally consistent. The purpose is not to produce a neat diagram at any cost; it is to make business meaning, accountability, dependencies and uncertainty visible enough for informed architecture decisions.

---

## Quick reference: the ownership test

When asked “Who owns this data?”, answer in this order:

1. **Which exact asset and meaning?**
2. **Which capability and decision does it support?**
3. **Which domain has authority over that meaning?**
4. **Who creates or changes it, who consumes it, and who can correct it?**
5. **Who bears accountability for the consequences of error?**
6. **What evidence confirms the accountable role?**
7. **If evidence is insufficient, who will resolve the gap and when will it be reviewed?**

A reliable architecture does not pretend uncertainty has disappeared. It identifies uncertainty, assigns an action to resolve it, and keeps the decision revisitable.
