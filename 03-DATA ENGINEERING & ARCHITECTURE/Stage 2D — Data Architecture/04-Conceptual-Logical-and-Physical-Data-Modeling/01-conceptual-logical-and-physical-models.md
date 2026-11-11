# 01 — Conceptual, Logical and Physical Models

> **Module:** Stage 2D — Data Architecture / 04-Conceptual-Logical-and-Physical-Data-Modeling  
> **Case domain:** Northbridge Bank (fictional)  
> **Status of case details:** Every entity, attribute, rule, identifier, requirement, value, and example below is an **illustrative assumption**, not a fact about a real bank.  
> **Scope:** This lesson establishes the three modeling levels and a reviewed conceptual/logical model pair. It does not teach database administration or require product-specific DDL.

## Introduction

Data architecture needs more than a diagram or a collection of tables. It needs a precise account of what the business means, which facts it must represent, how those facts relate, and how the resulting structure can be implemented without confusing business rules with technology choices.

This lesson uses one fictional domain—Northbridge Bank—to follow the same subject through three distinct levels:

- **Conceptual:** which business things matter and how they relate.
- **Logical:** what information must be represented, with explicit identifiers, attributes, relationship rules, cardinality, optionality, and constraints.
- **Physical:** how a chosen platform stores and accesses that logical information.

The levels are connected, but they are not interchangeable. A logical rule can remain valid even when a particular platform cannot enforce it declaratively. A physical implementation can change while the logical meaning remains stable.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain data modeling and its business value.
2. Distinguish conceptual, logical, and physical models by abstraction, questions answered, audience, contents, and technology dependence.
3. Explain how requirements and business rules flow into model elements and later into implementation.
4. Define model scope, boundaries, assumptions, intended consumers, and domain ownership.
5. Transform a conceptual Customer–Account–Transaction model into a logical model with attributes, identifiers, cardinality, optionality, and constraints.
6. Explain why some decisions belong in logical design while platform, data type, index, partitioning, storage, optimization, and security-enforcement decisions are deferred to physical design.
7. Use a glossary, entity inventory, rules register, diagrams, data dictionary, and mapping/traceability tables.
8. Explain how one logical model may have multiple physical realizations and identify what must remain semantically consistent.
9. Detect modeling-level violations and document architecturally significant decisions using an Architecture Decision Record (ADR).
10. Review a model with valid and invalid examples rather than trusting a diagram’s appearance.

**Success standard:** prioritize semantic correctness, explicit rules, traceability, and reviewability over diagram size or visual polish.

## 2. Why the topic matters in real-world Data Architecture

A data model is a structured, explicit representation of the things an organisation cares about, the facts recorded about them, how they relate, and the rules that constrain them. It provides a shared contract between business stakeholders, architects, analysts, engineers, governance teams, and data consumers.

### Business value

| Value | What modeling contributes | Example in Northbridge Bank (illustrative) |
|---|---|---|
| Consistency | Shared definitions prevent the same term from meaning different things in different systems. | “Customer” has an agreed definition rather than three incompatible CRM/core-banking meanings. |
| Integrity | Identifiers, relationships, and constraints make invalid states visible and preventable. | A transaction must reference an existing account. |
| Interoperability | A common structure supports mapping between systems and data products. | CRM customer references can be mapped to the bank’s governed customer identity. |
| Trustworthy analytics | Explicit grain and relationships reduce duplicate counting and missing joins. | Transaction totals do not multiply when customer and account data are joined. |
| Governance | Definitions, ownership, classification, and lineage can attach to model elements. | An owner is accountable for the meaning of `CustomerStatus`. |
| Maintainability | Separating business meaning from implementation reduces the cost of change. | A storage platform can change without redefining “account holder.” |

### The three levels

| Level | Main question | Primary audience | Typical contents | Technology dependence |
|---|---|---|---|---|
| **Conceptual** | What business concepts matter, and how do they relate? | Business stakeholders and architects | Core concepts/entities, relationships, business definitions, scope, boundaries | None |
| **Logical** | What data must we represent precisely, and under which rules? | Architects, analysts, designers, domain experts | Entities, attributes, identifiers, cardinality, optionality, business constraints, normalized structure | Largely technology-independent; may reflect the chosen modeling paradigm |
| **Physical** | How will a chosen technology store and access it? | Engineers, platform specialists, DBAs | Tables/files/document structures, physical data types, indexes, partitions, storage formats, platform naming, enforcement and access mechanisms | Specific to the selected platform and workload |

These are not simply small, medium, and large versions of one diagram. Each level answers a different question and carries a different kind of decision.

### How the levels connect

```text
Business need / requirement
          |
          v
Business vocabulary + explicit rules
          |
          v
CONCEPTUAL MODEL
Business concepts, scope, and relationships
          |
          v
LOGICAL MODEL
Attributes, identifiers, cardinality, optionality, constraints
          |
          v
PHYSICAL MODEL
Platform objects, data types, access paths, partitions, storage, enforcement
          |
          v
Implemented schema, pipelines, interfaces, and tests
```

Traceability must work **both ways**: every requirement/rule should point to the model element and eventual implementation that represents it; every model element should have a business justification or be explicitly marked as a technical/supporting element.

### A diagram is not the model

A diagram is a picture. The model is the set of definitions, rules, assumptions, identifiers, relationship semantics, and constraints that the picture illustrates. A tidy diagram with ambiguous names, unstated cardinality, or no definition of “active” is not a complete model. Textual definitions and test cases are necessary because diagrams cannot express every condition, temporal rule, or exception clearly.

## 3. Prerequisite knowledge

The roadmap identifies these prerequisites:

- Stage 2D.1: architecture role, principles, domains, ownership, and governance.
- Stage 2D.2: stakeholder discovery, requirements, constraints, assumptions, and ADRs.
- Stage 2D.3: architecture patterns, domain-oriented design, data products, storage patterns, and event/data-sharing concepts.
- Basic relational and SQL fundamentals: tables, keys, joins, and the ability to read simple DDL.
- Ability to read and draw simple box-and-line diagrams.

Advanced database administration is **not** assumed. No particular modeling tool, database product, or certification is required.

Before modeling, ask these questions in order:

1. **Whose problem is this?** Identify stakeholders and consumers.
2. **Which domain and boundary?** Establish ownership and what is in or out of scope.
3. **Which requirements and rules?** Record source, definition, owner, and unresolved ambiguity.
4. **Which use?** Transaction processing, analytics, history, exchange, or more than one?
5. **Which level?** Conceptual, logical, or physical?

If you cannot answer these, pause and record the unknowns. Do not fill gaps with unmarked assumptions.

### Glossary

| Term | Meaning in this lesson |
|---|---|
| **Model** | Explicit representation of concepts, facts, relationships, and rules. |
| **Entity** | A business thing about which the organisation needs to retain facts. |
| **Attribute** | A fact recorded about an entity or relationship. |
| **Identifier** | Attribute or combination of attributes that distinguishes one instance from others. |
| **Candidate key** | A minimal attribute set that uniquely identifies an entity instance. |
| **Cardinality** | Minimum and maximum number of related instances permitted. |
| **Optionality** | Whether a relationship or attribute may be absent; often expressed through minimum cardinality or nullability. |
| **Constraint** | A rule that valid data must satisfy. |
| **Business rule** | A policy or definition grounded in business meaning, not merely a platform limitation. |
| **Physical object** | An implementation element such as a table, file, field, index, or partition. |
| **Traceability** | Ability to follow a requirement to its model representation and implementation, and back again. |
| **Domain owner** | Accountable role or team responsible for the meaning and governance of the domain’s data. |
| **ADR** | Architecture Decision Record: concise record of context, decision, alternatives, consequences, and status. |
| **Illustrative assumption** | A teaching example that must be validated before being treated as a real business rule. |

## 4. Beginner-level learning sequence

### 4.1 Define data modeling

Data modeling makes business meaning explicit before implementation choices harden into systems. It helps answer: What is the thing? What facts do we need to know? How do things relate? Which combinations are valid? What does a term mean?

For example, “account” may mean a bank account in a core system, a customer login, or a ledger account in another context. A model must state which meaning and boundary it uses.

### 4.2 Understand the three levels with one domain

The examples below are all illustrative assumptions for Northbridge Bank.

#### Conceptual model: business meaning

**Question:** What major business concepts matter and how do they relate?

```text
[Customer]  ---- holds / is holder of ----  [Account]
                                              |
                                              | records
                                              v
                                        [Transaction]
```

At this level, the model communicates the business concepts and relationships. It does not need columns, database types, indexes, join tables, or a storage technology.

**Illustrative scope statement:** This model covers customers, accounts, and transactions relevant to the customer-and-account domain. It excludes loan underwriting, payment-network settlement, branch operations, and the full general ledger. Those exclusions are scope boundaries, not claims that those concepts do not exist in the bank.

#### Logical model: precise information and rules

**Question:** What data must be represented, and what must be true?

The logical model expands the conceptual model with attributes, identifiers, explicit cardinality and optionality, and business constraints. It remains independent of a particular database product.

Illustrative entities:

| Entity | Identifier | Illustrative attributes | Meaning |
|---|---|---|---|
| `Customer` | `CustomerID` | `LegalName`, `CustomerStatus`, `CreatedDate` | A party recognized as a customer in this domain. |
| `Account` | `AccountID` | `AccountType`, `AccountStatus`, `OpenedDate`, `ClosedDate` | An account tracked by the bank. |
| `AccountHolding` | `AccountHoldingID` | `HolderRole`, `ValidFrom`, `ValidTo` | A customer’s holding relationship to an account. Resolves multiple holders and relationship history. |
| `Transaction` | `TransactionID` | `PostedAt`, `Amount`, `Currency`, `TransactionStatus` | A recorded transaction associated with one account. |

All names and attributes are illustrative. The identifier labels above describe logical identity, not a physical datatype or key-generation mechanism.

#### Physical model: implementation

**Question:** How will a chosen platform store, validate, secure, and access the logical information?

A relational realization might use separate tables for Customer, Account, AccountHolding, and Transaction; physical data types; primary and foreign-key mechanisms where available; indexes; partitioning; and access controls. A lakehouse realization might use governed tables or files with logical identifiers, validation pipelines, and table-format metadata. These are examples of possible implementations, not requirements to select either.

Do **not** put details such as `VARCHAR(100)`, a specific index, or a platform partition key into the conceptual model. Those choices answer a different question.

### 4.3 What belongs at each level?

| Item | Conceptual | Logical | Physical |
|---|---|---|---|
| Customer and Account are important business concepts | Yes | Retained precisely | Realized as objects/structures |
| A customer may hold zero or more accounts | Broad relationship may be shown | Exact min/max cardinality | Represented/enforced through implementation where feasible |
| Every transaction belongs to exactly one account | May be noted as a business rule | Explicit relationship and mandatory participation | Enforced through keys, validation, or other controls |
| `CustomerID` uniquely identifies a customer | May be mentioned informally | Identifier/candidate-key rule | Physical key/index strategy selected |
| `Amount` must be represented with exact monetary semantics | Business meaning may be named | Required fact and business precision/scale requirements clarified as applicable | Physical numeric/decimal type selected |
| `VARCHAR(100)` | No | No | Yes |
| Index on transaction posting time | No | No | Yes |
| Data retention policy | Business requirement may be referenced | Relevant rule and required history captured | Storage lifecycle, deletion, and access mechanisms selected |
| Domain ownership and model boundary | Yes | Documented and carried forward | Ownership metadata/process implemented |

A logical constraint and its physical enforcement are different things. The rule “a transaction must refer to an existing account” belongs in the logical model. A foreign key, pipeline test, service validation, or reconciliation process is an implementation mechanism.

### 4.4 Beginner exercise: classify statements

Classify each statement as **C** (conceptual), **L** (logical), **P** (physical), or **M** (cross-level/mixed; split it into separate decisions). Then check the answer key.

| # | Statement | Your answer |
|---:|---|---|
| 1 | Northbridge Bank tracks customers and accounts. | |
| 2 | The customer-and-account domain excludes loan underwriting. | |
| 3 | A customer may hold no accounts or many accounts. | |
| 4 | `CustomerID` uniquely identifies a customer. | |
| 5 | `CustomerStatus` has a governed business definition. | |
| 6 | `CustomerID` is stored as a 36-character text field. | |
| 7 | The Account table is partitioned by opening month. | |
| 8 | Every transaction belongs to exactly one account. | |
| 9 | Account holding has a role and a validity period. | |
| 10 | A physical foreign-key constraint is used where supported. | |
| 11 | The model is owned by the Customer and Account domain owner. | |
| 12 | Transaction history must be available to approved analysts. | |
| 13 | Transaction amounts use an exact decimal representation in the chosen store. | |
| 14 | The platform uses a composite index on account and posting time. | |
| 15 | An account can have multiple customers as holders. | |
| 16 | `AccountHolding` resolves the many-to-many Customer–Account relationship. | |
| 17 | The logical model includes `ClosedDate`, which may be absent while an account is open. | |
| 18 | The lakehouse stores transactions in a columnar file format. | |
| 19 | A shared definition of “active customer” is required by reporting consumers. | |
| 20 | A pipeline rejects transactions whose account identifier is unknown. | |
| 21 | Customer legal name must be preserved as of the time a regulated event occurred. | |
| 22 | The implementation encrypts sensitive fields at rest. | |
| 23 | A model diagram shows Customer connected to Account. | |
| 24 | The model’s rule register defines the meaning of “closed account.” | |

#### Answer key and reasoning

| # | Answer | Why |
|---:|---|---|
| 1 | C | Names core business concepts. |
| 2 | C | Defines scope/boundary. |
| 3 | L | States precise minimum and maximum cardinality. |
| 4 | L | Defines logical identity/uniqueness. |
| 5 | C/L | The existence of a governed definition is cross-level; the definition is conceptual, while its application to a logical attribute is logical. Split the statement. |
| 6 | P | Specifies physical representation. |
| 7 | P | Partitioning is an implementation decision. |
| 8 | L | Business relationship rule; physical enforcement is separate. |
| 9 | L | Defines relationship facts and temporal attributes. |
| 10 | P | Names a physical enforcement mechanism. |
| 11 | C/L | Ownership and accountability are domain/model metadata carried across levels; document the owner explicitly. |
| 12 | M | The access requirement is a business/security requirement; physical permissions and serving mechanisms are implementation decisions. |
| 13 | P | “Chosen store” and its representation are physical; the requirement for correct monetary semantics should be captured logically. Split the requirement from the chosen type. |
| 14 | P | Index design is physical. |
| 15 | L | Exact relationship cardinality. |
| 16 | L | Logical resolution of a many-to-many relationship. |
| 17 | L | Attribute and optionality rule. |
| 18 | P | Storage format is implementation-specific. |
| 19 | C | Shared business definition and consumer need. The exact status rule also needs logical representation where relevant. |
| 20 | P | Pipeline rejection is an enforcement mechanism; the unknown-account rule itself is logical. |
| 21 | M | The sentence is a business requirement, not itself a model element. Preserve the requirement and time semantics in the logical model; select the physical history mechanism later. Split requirement, logical representation, and physical implementation. |
| 22 | P | Security implementation detail. |
| 23 | M | The diagram is a representation, not itself a level. Its level depends on the content and explicit semantics. |
| 24 | C/L | A definition is business vocabulary; the associated rule should be linked to logical elements if it constrains data. |

For mixed statements, do not force a single label if doing so hides two decisions. Split the business requirement from its physical implementation.

## 5. Intermediate-level learning sequence

### 5.1 Set scope, boundaries, consumers, assumptions, and ownership

Before adding attributes, write a short model charter.

| Charter field | Northbridge Bank illustrative entry |
|---|---|
| Model name | Customer and Account Core Domain Model |
| Purpose | Establish consistent customer, account, holding, and transaction semantics for operational exchange and downstream analysis. |
| In scope | Customer, Account, AccountHolding, Transaction and their stated relationships. |
| Out of scope | Loan underwriting, payment-network settlement internals, complete general ledger, customer authentication credentials. |
| Intended consumers | Core banking integration, customer/account reporting, data governance, approved analytics teams. |
| Domain owner | Customer and Account domain owner (role assumed for this example; actual owner must be assigned). |
| Source requirements | Illustrative requirements NB-R01 to NB-R05 below; replace with approved business requirements in a real project. |
| Assumptions | Each transaction in this model is associated with one account; account holders may be multiple; holding relationships can change over time. |
| Open questions | Are pending and reversed transactions in scope? What is the authoritative customer identity across systems? Which historical names must be retained, and for how long? |

**Why this matters:** without a boundary, model scope expands indefinitely. Without consumers, the model may omit important history or represent the wrong grain. Without ownership, definitions and changes have no accountable decision-maker.

### 5.2 Convert requirements into concepts and rules

The following requirements are **illustrative assumptions**, invented for this lesson.

| Requirement ID | Illustrative requirement | Business concept/rule |
|---|---|---|
| NB-R01 | The bank needs one governed representation of each customer in this domain. | Customer identity must be stable and unique within the agreed boundary. |
| NB-R02 | A customer may hold accounts jointly with other customers. | Customer–Account is potentially many-to-many. |
| NB-R03 | The bank must know each customer’s role and the period during which the holding relationship applied. | Holding is a relationship with attributes and history. |
| NB-R04 | Each recorded transaction must be attributable to one account. | Transaction has exactly one Account relationship. |
| NB-R05 | Reporting must apply an agreed definition of “active customer.” | “Active” needs an approved definition, not an undocumented query filter. |

Do not jump directly from a requirement to a table. First determine the business concept and rule. Then decide how the rule is represented logically. Only after that should implementation mechanisms be chosen.

### 5.3 Transform Customer–Account–Transaction into a logical model

#### Step A — Begin with the conceptual structure

```text
[Customer] -------------- holds ---------------- [Account]
                                                   |
                                                   | records
                                                   v
                                             [Transaction]
```

This shows the main concepts, but it leaves important questions unanswered: Can an account have joint holders? Does the holding relationship have a role? Can it change over time? Is a transaction ever associated with more than one account? Those questions must be resolved or recorded as open assumptions.

#### Step B — Resolve relationship semantics

For this worked example, assume:

- **A customer may hold zero or many accounts.**
- **An account has one or more holders** in the model’s defined scope.
- **A customer–account holding relationship has a role and a validity period.**
- **Each transaction is associated with exactly one account.**
- **An account may have zero or many transactions.**

These are illustrative assumptions; a real bank must confirm them with domain experts. If accounts can exist before a holder is assigned, or if transaction records include unposted items with different semantics, the model must be adjusted rather than quietly forcing these assumptions.

Customer and Account therefore have a many-to-many relationship, resolved logically by the associative entity `AccountHolding`.

#### Step C — Logical relationship diagram

```text
Customer (1) ----< AccountHolding >---- (1) Account
                    |        |
                    |        +-- HolderRole
                    +----------- ValidFrom / ValidTo

Account (1) --------------------< Transaction
```

Read the relationship in both directions:

- One Customer can participate in zero or many AccountHolding records.
- Each AccountHolding record refers to exactly one Customer.
- One Account can have one or many AccountHolding records under the illustrative rule.
- Each AccountHolding record refers to exactly one Account.
- One Account can have zero or many Transactions.
- Each Transaction refers to exactly one Account.

The diagram communicates structure, but the definitions and constraints below remain authoritative. In particular, “one or many AccountHolding records per Account” must be tested against the business’s rules for opening, dormant, closed, or temporarily restricted accounts.

#### Step D — Logical entity definitions

| Entity | Identifier | Attribute | Requirement/meaning | Optionality or constraint |
|---|---|---|---|---|
| Customer | `CustomerID` | `LegalName` | Current legal name in the domain | Mandatory under this illustrative model; temporal preservation is a separate requirement and may need history structures. |
| Customer | `CustomerID` | `CustomerStatus` | Status under an agreed definition | Mandatory; allowed values and transitions require an approved rule. |
| Customer | `CustomerID` | `CreatedDate` | Date customer entered this domain | Mandatory if the domain’s event history supports it; definition must be confirmed. |
| Account | `AccountID` | `AccountType` | Business classification of account | Mandatory; valid types governed by reference definitions. |
| Account | `AccountID` | `AccountStatus` | Account lifecycle status | Mandatory; allowed states/transitions must be defined. |
| Account | `AccountID` | `OpenedDate` | Date account opened | Mandatory under the illustrative rule. |
| Account | `AccountID` | `ClosedDate` | Date account closed | Optional while not closed; if present, must be consistent with status and chronology. |
| AccountHolding | `AccountHoldingID` | `CustomerID` reference | Customer participating in the holding | Mandatory; must identify an existing Customer. |
| AccountHolding | `AccountHoldingID` | `AccountID` reference | Account held | Mandatory; must identify an existing Account. |
| AccountHolding | `AccountHoldingID` | `HolderRole` | Role of the holder | Mandatory; permitted values must be governed. |
| AccountHolding | `AccountHoldingID` | `ValidFrom` | Start of relationship validity | Mandatory. |
| AccountHolding | `AccountHoldingID` | `ValidTo` | End of relationship validity | Optional for an open-ended/current relationship; if present, later than `ValidFrom` under this illustrative convention. |
| Transaction | `TransactionID` | `AccountID` reference | Account to which transaction belongs | Mandatory; must identify an existing Account. |
| Transaction | `TransactionID` | `PostedAt` | Posting timestamp/instant | Mandatory for a posted transaction; time-zone and event semantics must be specified. |
| Transaction | `TransactionID` | `Amount` | Signed or otherwise explicitly defined monetary amount | Mandatory; sign convention and meaning must be defined. |
| Transaction | `TransactionID` | `Currency` | Currency of amount | Mandatory; valid codes governed by a reference standard. |
| Transaction | `TransactionID` | `TransactionStatus` | Lifecycle state of transaction | Mandatory; allowed states and transitions must be defined. |

The logical model defines the required meaning and constraints. It does not yet choose whether an identifier is generated by a database, assigned by a service, or mapped from an upstream source. It also does not specify a physical field type.

#### Step E — Logical constraints and tests

| Rule ID | Illustrative rule | Valid example | Invalid example | Why invalid |
|---|---|---|---|---|
| NB-BR01 | `CustomerID` identifies one Customer only. | One Customer record for `CUS-104`. | Two different Customer records with `CUS-104`. | Identifier collision. |
| NB-BR02 | Each AccountHolding refers to one existing Customer and one existing Account. | Holding refers to `CUS-104` and `ACC-800`. | Holding refers to unknown `CUS-999`. | Referential rule violated. |
| NB-BR03 | Holding has a role and `ValidFrom`. | Role `JOINT_HOLDER`, start date present. | Role missing. | Required relationship fact absent. |
| NB-BR04 | If `ValidTo` exists, it is later than `ValidFrom` under this illustrative date convention. | Start 2025-01-01, end 2025-12-31. | Start 2025-12-31, end 2025-01-01. | Invalid interval. |
| NB-BR05 | Each Transaction refers to exactly one existing Account. | Transaction `TX-900` references `ACC-800`. | Transaction references no account or an unknown account. | Relationship is mandatory and singular. |
| NB-BR06 | `ClosedDate` is absent for an open account and consistent with closure status. | Open account has no ClosedDate. | Open account has a ClosedDate but no documented exception. | Status/date contradiction under the assumption. |
| NB-BR07 | Transaction amount and currency are interpreted under an approved sign/currency rule. | `-25.00`, currency `INR`, meaning debit per agreed convention. | Amount is treated as debit in one system and credit in another without mapping. | Semantic inconsistency. |

A model cannot by itself settle every business policy. For example, whether an account may have no holder during a controlled operational state is a domain question. Record it as an open question until an accountable owner resolves it.

### 5.4 Maintain requirement-to-model-to-implementation traceability

The table below demonstrates the chain from requirement to concept, logical element, and a **possible future** physical object. Physical names are illustrative placeholders, not a selected platform schema.

| Requirement | Concept/rule | Logical element | Possible physical object (deferred) | Validation evidence |
|---|---|---|---|---|
| NB-R01 | One governed customer identity in this domain | `Customer.CustomerID` is a unique identifier | Customer table key, document identifier, or governed key in a curated dataset | Duplicate-identity test; source-to-canonical mapping review |
| NB-R02 | Joint holdings are permitted | `AccountHolding` links Customer and Account | Relationship table/collection or equivalent representation | Two customers validly linked to one account; no duplicated relationship facts |
| NB-R03 | Holder role and history matter | `HolderRole`, `ValidFrom`, `ValidTo` | Fields/columns or nested relationship records | Temporal interval tests; role vocabulary validation |
| NB-R04 | Every transaction belongs to one account | Mandatory Transaction–Account relationship | Foreign key where supported, or pipeline/service validation | Orphan transaction test returns zero accepted orphans |
| NB-R05 | “Active customer” has one approved meaning | Governed `CustomerStatus` definition and documented derivation rule | Status field, derived view, semantic-layer expression, or curated attribute | Golden test cases approved by business owner |

Traceability must not stop at the logical model. When physical design begins, update the mapping with actual objects, enforcement mechanisms, lineage, and tests. If one requirement has no model element, it may be omitted. If a model element has no requirement or justified technical purpose, it may be unnecessary.

### 5.5 Modeling artefacts and what each contributes

| Artefact | Purpose | Minimum useful contents |
|---|---|---|
| Business glossary | Aligns vocabulary | Term, definition, owner, synonyms, scope/context |
| Model charter | Defines scope and accountability | Purpose, boundaries, consumers, owner, assumptions, open questions |
| Entity inventory | Lists entities consistently | Entity name, definition, owner, source/consumer notes |
| Relationship inventory | Makes relationships reviewable | From/to entities, verb, min/max in both directions, optionality |
| Rules register | Keeps business rules explicit | Rule ID, rule text, owner, affected elements, valid/invalid examples, enforcement notes |
| Conceptual diagram | Communicates core concepts | Main concepts and business relationships, without implementation clutter |
| Logical diagram | Communicates precise structure | Entities, identifiers, attributes as needed, relationship cardinality/optionality |
| Data dictionary | Defines fields/attributes | Name, definition, type category or domain, mandatory status, allowed values, sensitivity, lineage |
| Mapping/traceability table | Connects requirements and model to implementation | Requirement ID, concept, logical element, physical object, test/evidence, status |
| Assumption/open-question log | Prevents guesses from becoming facts | Statement, reason, impact, owner, decision needed, status |
| ADR | Records a consequential architectural choice | Context, decision, alternatives, consequences, status |

Diagrams are important communication tools, but they do not replace the glossary, rules register, data dictionary, assumptions, or traceability table.

### 5.6 Decisions to defer to physical design

A **deferred-decision register** records what is not yet decided, why it is deferred, and what evidence is needed. “Deferred” does not mean “forgotten.”

| Decision ID | Decision area | Why it is physical/deferred | Evidence needed before deciding |
|---|---|---|---|
| PD-01 | Target platform and deployment pattern | Depends on workload, operational constraints, governance, and platform standards | Consumer needs, volume/growth, latency, availability, platform constraints |
| PD-02 | Physical data types and precision | Logical semantics must be known first; physical types depend on the target store | Amount precision/range, timestamp semantics, encoding, platform capabilities |
| PD-03 | Physical key strategy and generation | Logical uniqueness/stability is required now; generation/storage mechanism may vary | Source identity quality, cross-system uniqueness, lifecycle, privacy, scale |
| PD-04 | Indexes/access paths | Workload and query patterns determine whether an index is beneficial | Query shapes, selectivity, latency goals, write cost, measured plans |
| PD-05 | Partitioning/clustering | Depends on data volume, access patterns, retention, and platform behavior | Growth estimates, common filters, skew, maintenance cost |
| PD-06 | Storage format and layout | Depends on transactional, analytical, exchange, and history requirements | Read/write patterns, interoperability, compression, schema evolution |
| PD-07 | Denormalization/materialization | Logical correctness comes first; duplication may improve performance but creates consistency costs | Measured bottleneck, refresh tolerance, update patterns, reconciliation strategy |
| PD-08 | Physical security enforcement | Business classification and access requirement must be known; enforcement is platform-specific | Data classification, identities, threat model, access use cases, audit needs |
| PD-09 | Declarative versus procedural rule enforcement | The business rule remains required even if a platform lacks a matching constraint | Platform capabilities, failure modes, reconciliation, ownership, observability |
| PD-10 | Retention, deletion, and history implementation | Business/legal retention and history requirements must be translated into platform operations | Approved retention rules, legal requirements, consumers, recovery needs |

Some decisions begin logically and finish physically. For example, identifier uniqueness and stability are logical requirements; whether a key is generated by a service, allocated from a sequence, or mapped from an external identity is an implementation choice. Keep the business requirement stable while allowing implementation options to be evaluated.

## 6. Advanced-level learning sequence

### 6.1 Evaluate choices against semantics and workloads

A model should be evaluated against:

- Business meaning and rule correctness.
- Integrity and ability to represent invalid states.
- Intended use: transaction processing, analytics, history, exchange, or several.
- Maintainability, evolution, and interoperability.
- Workload, volume, latency, growth, operational capability, and cost.
- Governance, ownership, privacy, security, and audit requirements.

A design that performs well but changes the meaning of “customer” is not an acceptable optimization. Conversely, a logically correct model may have multiple valid physical realizations with different performance and operational trade-offs.

### 6.2 Separate business constraints from enforcement mechanisms

Consider the rule: **Every Transaction must reference exactly one existing Account.**

- **Logical rule:** a transaction has a mandatory relationship to one account; the reference must identify a valid account.
- **Possible physical enforcement:** a foreign-key constraint in a relational store.
- **Alternative physical enforcement:** ingestion validation, service-level validation, reconciliation, quarantine, and monitoring where the target platform does not enforce foreign keys.
- **Required outcome:** the accepted data must satisfy the business rule, and failures must be observable and handled.

The relationship does not disappear because a platform lacks declarative foreign keys. What changes is the enforcement mechanism and the operational risk. If validation is procedural, design for race conditions, retries, late-arriving account records, quarantine, replay, reconciliation, and alert ownership. Do not claim the rule is enforced merely because a diagram contains a line.

### 6.3 Multiple physical realizations of one logical model

The logical model is a semantic contract. It may be realized in different ways, provided that the meaning, required facts, identity rules, relationship semantics, and constraints are preserved or explicitly transformed with documented loss.

| Logical concept | Relational realization | Document realization | Analytical/lakehouse realization |
|---|---|---|---|
| Customer | Customer table with logical identifier | Customer document keyed by identifier | Customer dataset/table with governed identifier |
| AccountHolding | Relationship table with references | Embedded or separate holding records, depending on access and history needs | Relationship dataset/table, possibly conformed for analytical use |
| Transaction belongs to Account | Transaction table with account reference | Transaction document with account identifier | Transaction fact/dataset with account key |
| Mandatory relationship | Referential constraint where supported | Application/validation rule | Data quality tests and pipeline checks, possibly catalog/contract rules |
| History of holding | Effective-dated relationship rows | Versioned or separate relationship records | Historical relationship dataset or temporal columns |

Trade-offs:

- **Relational:** explicit relationships and constraints are natural, but some platforms or configurations may limit enforcement or impose scaling/partitioning trade-offs.
- **Document:** aggregate-oriented access can be convenient, but embedding relationships may duplicate facts or complicate history and cross-aggregate integrity.
- **Analytical/lakehouse:** columnar and distributed layouts can suit large scans, but data quality and referential rules may need pipeline tests and reconciliation rather than transactional constraints.

These are general patterns, not universal performance claims. Measure actual workloads and evaluate platform capabilities.

### 6.4 Review level violations

A **level violation** occurs when a decision is represented at the wrong abstraction level or when one artifact is mislabeled as another.

- Conceptual model containing `VARCHAR(100)` or an index definition: physical detail in a conceptual artifact.
- Conceptual model containing a join table such as `CustomerAccountXref` without business meaning: likely logical/physical implementation detail; model the business relationship first.
- Logical model tied to a vendor-specific datatype or partition clause: physical implementation has leaked into logical design.
- Physical schema with unexplained fields: implementation has lost traceability to business meaning or technical purpose.
- A line between boxes with no cardinality or definition: incomplete semantics, not necessarily a level violation but a model-quality defect.

### 6.5 Ten-item level-violation review exercise

Assume a reviewer receives a document titled “Northbridge Conceptual and Logical Model.” Identify the defect, assign the proper level or artefact, and state the correction.

| # | Statement in the reviewed document | Your diagnosis |
|---:|---|---|
| 1 | Conceptual Customer box says `CustomerID VARCHAR(36)`. | |
| 2 | Conceptual diagram includes an index on `PostedAt`. | |
| 3 | Conceptual model contains a `CustomerAccountJoin` box solely because an engineer created a join table. | |
| 4 | Logical model says `AccountStatus` is `ENUM('OPEN','CLOSED')` using a named platform syntax. | |
| 5 | Logical model says transactions are partitioned by month. | |
| 6 | Logical model says each Transaction belongs to exactly one Account. | |
| 7 | Physical table contains `flag_7` with no definition or lineage. | |
| 8 | The diagram labels a relationship “has” without cardinality, optionality, or an agreed definition. | |
| 9 | Physical implementation lacks foreign-key support, so the document deletes the transaction-to-account rule. | |
| 10 | A logical attribute `CustomerStatus` is defined as “whatever the current report query returns.” | |

#### Answer key

| # | Diagnosis and correction |
|---:|---|
| 1 | **Physical detail in conceptual model.** Keep the business concept/definition in conceptual view; place identifier uniqueness in logical model and field representation in physical model. |
| 2 | **Physical detail in conceptual model.** Move index choice to the physical design and justify it with workload evidence. |
| 3 | **Implementation structure masquerading as business concept.** Model Customer–Account as a business relationship conceptually. Introduce `AccountHolding` in the logical model because joint holders, role, and validity period require it—not merely because a table exists. |
| 4 | **Platform-specific syntax in logical model.** Define the allowed status domain and transition rules logically; choose the platform’s representation physically. |
| 5 | **Physical partitioning in logical model.** Move partition strategy to the deferred-decision/physical register. |
| 6 | **Correct logical-level rule**, assuming it is an approved business rule. Ensure cardinality is explicit in both directions and physical enforcement is separately documented. |
| 7 | **Physical object without traceability.** Identify its business/technical purpose, add dictionary and lineage entries, or remove it if unnecessary. |
| 8 | **Incomplete model semantics.** Define the verb and minimum/maximum cardinality in both directions; document optionality and business rule. |
| 9 | **Business rule incorrectly discarded due to platform limitation.** Restore the logical rule; choose and test an alternative enforcement design such as pipeline validation and reconciliation. |
| 10 | **Undefined business semantics.** Obtain an owner-approved definition and test cases; represent the attribute/derivation rule logically. A report query may implement a definition but cannot be its only definition. |

### 6.6 Three required practical scenarios

#### Scenario A — An engineer calls a schema the “conceptual model”

**Situation:** An engineer shares a database schema containing tables, fields, physical data types, indexes, and foreign-key definitions and labels it “the conceptual model.”

**Ask:**
1. Which business concepts and boundaries does it represent?
2. Who approved the definitions and rules?
3. Which elements are business concepts versus implementation objects?
4. What are the intended consumers and use cases?
5. Where are cardinality, optionality, assumptions, and business definitions recorded?

**Response:** Do not merely rename the schema. Create or recover the conceptual model from business concepts and relationships, then create a logical model with attributes and explicit rules. Keep the schema as a physical artifact and map it to the logical model. Existing schema details are evidence of implementation, not proof of correct business semantics.

#### Scenario B — The chosen cloud platform does not enforce foreign keys

**Situation:** The platform stores data but does not enforce foreign-key constraints.

**Answer:** The logical rule remains: each Transaction must reference one valid Account. Document the platform limitation as a physical constraint. Define enforcement controls—validation at ingestion, handling of late-arriving account records, quarantine, reconciliation, monitoring, and operational ownership. Test orphan cases. A model line alone does not enforce anything, and a missing native constraint does not make an invalid relationship valid.

#### Scenario C — The business changes the definition of “active customer”

**Situation:** Reporting previously counted a customer as active when any account was open. The business now proposes “active means at least one eligible account with qualifying activity in the previous 90 days.” Both definitions are illustrative examples, not bank policy.

**Which levels change?**

- **Conceptual:** The business term and definition must be reviewed and approved; scope or relationships may change only if the meaning of the domain concepts changes.
- **Logical:** The rule register, derivation semantics, required facts, and possibly required activity/history attributes must be updated. If required data is not represented, the logical model may need extension.
- **Physical:** The implementation of the rule may change—such as a derived attribute, view, semantic expression, or pipeline—plus tests, lineage, backfill, and rollout. The chosen optimization is physical.
- **Governance/traceability:** Update the glossary, owner approval, affected consumers, requirement mapping, versioning, and impact analysis.

Do not silently change a SQL filter and assume the model is unchanged. A changed definition is a business semantic change and must be traceable to affected data products and reports.

### 6.7 Record an architecturally significant choice in an ADR

Use an ADR when a choice has meaningful cross-system impact, constrains future design, or needs an explicit trade-off record. Do not create an ADR for every field.

#### ADR-NB-001 — Governed customer identifier

- **Status:** Proposed (illustrative).
- **Context:** Northbridge Bank’s CRM and core platform may use different customer identifiers. Consumers need consistent identity across the Customer and Account domain.
- **Decision:** The logical model will expose one governed `CustomerID` as the domain identifier. Source-system identifiers will be retained as mappings/alternate identifiers where required. The physical generation, storage, and mapping mechanism remains open for platform design.
- **Alternatives considered:** (1) Use a single source-system identifier directly; (2) use different identifiers in each consumer; (3) expose a governed domain identifier and maintain source mappings.
- **Consequences:** Improves cross-system traceability and gives consumers a stable reference; requires identity-resolution governance, mapping maintenance, and a process for merges/splits. It does not, by itself, prove that two source records represent the same real-world party.
- **Traceability:** NB-R01 → Customer identity concept → `Customer.CustomerID` logical identifier → physical key/mapping objects to be named after platform decision.
- **Review trigger:** Revisit if identity-resolution rules, domain boundaries, privacy constraints, or source integration architecture change.

### 6.8 How to decide what stays stable and what can adapt

A useful rule of thumb:

- Preserve **business meaning, approved definitions, identity semantics, cardinality, required facts, and valid-state rules** unless the business explicitly changes them.
- Adapt **physical data types, indexes, partitioning, file layout, platform naming, enforcement mechanisms, and performance materialization** when platform or workload evidence supports a change.
- If a physical constraint forces a logical rule to be weakened, treat that as a business/architecture decision requiring explicit approval and risk acceptance—not as an invisible implementation detail.

## 7. Industry-application exercises

Complete these exercises using Northbridge Bank and clearly label any additional assumptions.

### Exercise 1 — Conceptual and logical model pair

Produce:
1. A model charter with scope, exclusions, consumers, owner, assumptions, and open questions.
2. A conceptual diagram with Customer, Account, and Transaction.
3. A logical model including AccountHolding and explicit relationship cardinality/optionality.
4. A glossary with definitions for Customer, Account, AccountHolding, Transaction, holder role, and active customer.
5. A rules register with at least six rules and at least three valid and three invalid test combinations.

### Exercise 2 — Traceability

Use requirements NB-R01 to NB-R05. For every requirement, show:
- Business concept/rule.
- Logical entity, attribute, relationship, or constraint.
- Deferred physical object/mechanism.
- Test evidence and owner.
- Status: approved, assumed, open, or implemented.

### Exercise 3 — Deferred decisions

Complete the register in Section 5.6. For each decision, record:
- Why it is not a conceptual/logical decision.
- What evidence is needed.
- Who should decide or approve it.
- What risk arises if the decision is postponed too long.

### Exercise 4 — Review and correct

Complete the 20+ classification exercise and the ten-item level-violation review. Correct your own answers and explain any mixed-level statement by splitting it into separate business/logical and physical decisions.

### Exercise 5 — Scenario response

Write a short review response for each scenario in Section 6.6. Each response must distinguish business meaning, logical rule, physical enforcement, and required documentation.

### Exercise 6 — ADR

Write one ADR for an architecturally significant choice. Include context, decision, alternatives, consequences, traceability, status, and a review trigger.

### Exercise answer guide — reference criteria

These are review criteria, not the only acceptable model. Different designs are acceptable when they preserve the stated business rules, document assumptions, and explain trade-offs.

| Exercise | Minimum defensible answer | Common answer failure |
|---|---|---|
| 1 — Model pair | Scope and exclusions are explicit; conceptual view shows Customer, Account, Transaction and business relationships without implementation details; logical view adds `AccountHolding`, identifiers, attributes, min/max cardinality, optionality, constraints and tests. The assumed rule is that each Transaction references exactly one Account; an Account has zero or many Transactions. An Account has one or more holders only under the stated illustrative assumption. | Putting platform types or indexes in the conceptual/logical model; leaving the holder rule implicit; presenting assumptions as approved facts. |
| 2 — Traceability | NB-R01 maps to governed Customer identity and `Customer.CustomerID`, with a duplicate-identity test; NB-R02 maps to the Customer–Account many-to-many relationship via `AccountHolding`, tested with two holders; NB-R03 maps to `HolderRole`, `ValidFrom`, and `ValidTo`, tested for missing roles and invalid intervals; NB-R04 maps to the mandatory Transaction–Account relationship, tested with unknown accounts; NB-R05 maps to an owner-approved active-customer definition and golden test cases. Physical objects remain marked deferred until selected. | Inventing physical table names as if already selected, or failing to give a requirement a test and owner. |
| 3 — Deferred decisions | For each PD-01–PD-10 item, name the evidence needed and decision owner. Examples: workload and platform constraints for platform choice; precision/range and timestamp semantics for physical types; query shapes and measured plans for indexes; volume, skew and retention for partitioning; approved retention requirements for lifecycle implementation. | Treating a deferred choice as resolved, or deferring a business rule such as identifier uniqueness. |
| 4 — Review and correct | Classification exercise: at least 22 of 24 correct for the roadmap's 90% threshold (22/24 = 91.7%); explain every missed or mixed-level item. For the ten-item review, correct items 1, 2, 4 and 5 by moving implementation details to physical design; item 3 by modeling business semantics before any associative implementation; item 6 is a valid logical rule if approved; item 7 needs purpose/lineage or removal; item 8 needs explicit relationship semantics; item 9 retains the rule and adds tested enforcement; item 10 needs an owner-approved definition. | Scoring only labels without explaining mixed-level statements, or calling a valid logical rule a violation. |
| 5 — Scenario response | Scenario A: derive conceptual/logical artifacts from approved business meanings and retain the schema as physical. Scenario B: preserve the mandatory Transaction–Account rule and add observable validation/reconciliation if no native foreign key exists. Scenario C: approve and version the changed active-customer definition, update logical derivation facts and downstream traceability, and plan physical backfill/rollout/tests. | Renaming a schema without recovering semantics; dropping a rule due to platform limits; changing a report query without governance or impact analysis. |
| 6 — ADR | ADR-NB-001 is a valid reference pattern: context, governed identifier decision, alternatives, consequences, traceability to NB-R01, proposed status, and a review trigger. A defensible alternative may retain source identifiers plus an explicit crosswalk if the domain owner rejects a single exposed identifier; justify identity and consumer implications. | Treating the ADR as a substitute for the logical model, leaving alternatives/consequences unstated, or assuming a governed ID alone performs identity resolution. |

**Partial credit:** award credit for correct semantics and reasoning even when an alternative model is chosen. Deduct for unstated assumptions, missing cardinality/optionality, inconsistent identifiers, missing tests, unsupported claims of approval, or physical decisions presented as logical requirements. For mixed-level statements, full credit requires splitting the business requirement, logical representation, and physical mechanism.

## 8. Practical scenarios and case-based reasoning

Use the following cases to test whether your model is useful beyond the happy path.

### Case 1 — Joint account

**Illustrative situation:** Customer A and Customer B hold Account X, with different roles and different start dates.

- A simple direct Customer-to-Account foreign key on Account would fail to represent two holders without duplication or loss.
- The conceptual model should show that customers hold accounts.
- The logical model uses `AccountHolding` because the relationship has attributes and history.
- The physical design decides whether the relationship is stored in a table, separate collection, or analytical dataset.
- Test that both holders are represented once per valid relationship and that role and dates are retained.

### Case 2 — Customer changes legal name

**Illustrative situation:** A customer’s legal name changes, but the bank must interpret a historical transaction using the name valid at the time of the event.

A single current `LegalName` attribute is not sufficient to reconstruct past names. Clarify the temporal requirement and whether it applies to legal, operational, audit, or reporting use. The logical model may need a name-history entity or effective-dated attributes. Physical storage and retention mechanisms are later choices. Do not claim that adding a timestamp automatically defines which version is valid for every use case.

### Case 3 — Orphan transaction in a platform without foreign keys

**Illustrative situation:** A transaction arrives before the corresponding Account record due to asynchronous ingestion.

The logical model still requires the account relationship. The physical ingestion design must decide whether to defer the transaction, quarantine it, retry after account arrival, or use a governed unresolved-reference state if the business approves one. Monitor the age and count of unresolved references, define replay/reconciliation, and avoid silently treating an unknown account as valid.

### Case 4 — “Active customer” changes

Before changing a field or query, compare old and new definitions using approved test cases. Determine which reports, data products, and downstream models change. Version the definition if consumers require a controlled transition. The physical implementation may be a derived dataset, but the definition must remain discoverable and owned.

### Case 5 — Diagram appears correct but the rules are absent

A Customer–Account line does not tell a reviewer whether joint holders are permitted, whether an account may temporarily have no holder, whether a holder role is required, or how a former holder is represented. The model is incomplete until these are defined, assumed explicitly, or listed as open questions. A diagram cannot substitute for a rule register and valid/invalid examples.

## 9. Expected outputs and deliverables

A complete lesson/practice package for this topic should contain:

- [ ] A concise glossary and model charter.
- [ ] A conceptual model for the Northbridge Bank customer/account domain.
- [ ] A logical model that consistently transforms the conceptual model.
- [ ] Explicit entity definitions, identifiers, attributes, cardinality, optionality, and constraints.
- [ ] A business rules register with valid and invalid examples.
- [ ] A requirement-to-concept-to-logical-element-to-physical-object traceability table.
- [ ] A list of physical decisions deferred with rationale and required evidence.
- [ ] A data dictionary and mapping/traceability table.
- [ ] Completed 20+ item level-classification exercise with corrected answers.
- [ ] Completed ten-item level-violation review with corrections.
- [ ] Written responses to the three required scenarios.
- [ ] One concise ADR for an architecturally significant modeling choice.
- [ ] Answers to the module’s Topic 1 practice questions, corrected after review.

Keep working notes and unresolved questions outside the topic file if useful, but do not let informal notes replace the reviewed deliverables.

## 10. Common mistakes and misconceptions

1. **Treating the three levels as diagram sizes.** They differ by the decisions they answer, not the number of boxes.
2. **Putting data types, indexes, partition keys, or storage formats in a conceptual model.** These are physical decisions.
3. **Assuming a physical schema is the logical model.** A schema may contain platform accidents, unexplained columns, or missing business rules.
4. **Omitting scope, assumptions, consumers, or domain ownership.** This makes it difficult to know what the model promises.
5. **Failing to trace requirements.** Requirements can disappear during implementation, and unexplained model elements accumulate.
6. **Leaving cardinality and optionality implicit.** A line does not specify whether the relationship is one-to-one, one-to-many, or many-to-many.
7. **Modeling a many-to-many relationship by duplicating columns.** Use an associative entity when the relationship needs explicit identity, attributes, or history.
8. **Treating a business rule as a database feature.** A foreign key may enforce a rule physically, but the rule exists independently of that feature.
9. **Assuming a diagram proves correctness.** Definitions, constraints, edge cases, and tests are necessary.
10. **Calling invented assumptions “requirements.”** Label them and seek owner confirmation before production use.
11. **Using an unstable or ambiguous identifier.** State uniqueness and stability expectations; choose physical generation separately.
12. **Confusing a current value with history.** If the business needs “as of the event,” model the required time semantics.
13. **Defining “active customer” only inside a report query.** Govern the definition and trace it to logical facts and physical implementation.
14. **Optimizing before workload evidence exists.** Defer indexes, partitioning, and denormalization until query patterns, scale, and service objectives are understood.
15. **Deleting a logical rule because the platform cannot enforce it declaratively.** Retain the rule and design a testable enforcement and reconciliation approach.
16. **Assuming a logical model is entirely independent of all modeling paradigms.** It should be product-neutral, but a relational, document, event, or analytical paradigm can influence its structure; record the chosen paradigm and its consequences.
17. **Overstating what an ADR does.** An ADR records a decision and trade-offs; it does not replace a model, requirements, or implementation tests.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on diagram appearance alone:

- Explain each modeling level by question, audience, contents, and technology dependence.
- Classify at least 90% of the classification items correctly and justify the choices.
- Produce a coherent conceptual-to-logical model pair for Customer–Account–Transaction.
- Resolve the many-to-many Customer–Account relationship with `AccountHolding` because the relationship has role/history semantics, not merely because a physical join table exists.
- State relationship cardinality and optionality in both directions.
- Identify attributes, identifiers, business rules, assumptions, and open questions.
- Trace each illustrative requirement to a concept, logical element, potential physical object, and validation evidence.
- Explain which decisions are deferred to physical design and what evidence would justify each decision.
- Explain how the same logical model can be realized in relational, document, or analytical storage without silently changing semantics.
- Correct all ten level violations and explain why each was a violation or a valid logical rule.
- Explain the three required scenarios, including the platform without enforced foreign keys and the changed “active customer” definition.
- Produce one defensible ADR for an architecturally significant choice.
- Correct practice answers after review and ensure no rule is unrepresented.

## 12. Completion gate

Do not mark this topic complete merely because you read it or drew a diagram. Mark each item only after you have evidence.

- [ ] **Classification:** at least **90% correct** on the level-classification exercise, with explanations for every incorrect or mixed-level answer.
- [ ] **Reviewed model pair:** the conceptual and logical models have been reviewed; no unresolved level violations remain. Every relationship has explicit semantics, cardinality, and optionality where required.
- [ ] **Rules and tests:** the rules register contains approved rules or clearly marked assumptions/open questions; valid and invalid cases are tested, including edge cases.
- [ ] **Traceability:** each requirement maps to a business concept/rule, logical element, and later physical object or a documented pending decision.
- [ ] **Deferred decisions:** the physical-decision register is complete and each deferral is justified by the evidence still needed.
- [ ] **Scenarios:** the schema-mislabeled-as-conceptual, missing-foreign-key-enforcement, and changed-active-customer scenarios are answered with level separation and operational consequences.
- [ ] **Level-violation review:** all ten items are corrected and the reasoning is recorded.
- [ ] **ADR:** one architecturally significant modeling decision is documented with context, alternatives, consequences, traceability, and a review trigger.
- [ ] **Practice questions:** Topic 1 practice questions are answered and corrected; errors are not left unreviewed.
- [ ] **Independent review:** another learner or reviewer can read the model package and recover the business meanings and rules without needing you to explain hidden assumptions.

### Lesson summary

Conceptual modeling establishes **what the business means**. Logical modeling states **what information and rules must be represented**. Physical modeling determines **how a chosen technology stores, accesses, enforces, and secures that information**. Keep the levels connected through bidirectional traceability, explicit definitions, a rules register, and tests. Preserve logical business rules even when physical platforms cannot enforce them natively; document implementation choices and consequential trade-offs rather than allowing them to rewrite the business model silently.
