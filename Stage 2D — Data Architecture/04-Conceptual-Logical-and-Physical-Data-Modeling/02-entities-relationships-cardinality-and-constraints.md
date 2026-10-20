# 02 — Entities, Relationships, Cardinality and Constraints

> **Module:** Stage 2D — Data Architecture / 04-Conceptual-Logical-and-Physical-Data-Modeling  
> **Case domain:** Northbridge Bank (fictional)  
> **Assumption discipline:** Every Northbridge Bank entity, identifier, rule, attribute, and test datum in this lesson is an **illustrative assumption**. It is not a statement about a real bank. Where the business has not confirmed a rule, this lesson marks it as an assumption or open question.  
> **Scope:** Entity-relationship modeling and logical constraints. Physical enforcement mechanisms are discussed only to distinguish the rule from its implementation.

## Introduction

Entity-relationship (ER) modeling turns a business description into an explicit structure of things, facts, and relationships. The quality of this structure matters: a missing relationship can create orphan records; a mutable identifier can split one real-world party into several identities; an ambiguous cardinality can multiply or lose rows in reports.

This lesson follows the roadmap sequence: define the basic terms, identify entities and attributes, state relationship cardinality and optionality in both directions, resolve many-to-many relationships, justify keys, define referential integrity, test edge cases, and then review advanced ambiguities and anomalies.

The Northbridge Bank examples use `Party`, `Customer`, `Account`, `AccountHolding`, `Product`, `Branch`, `Transaction`, `Address`, and `Contact` as **candidate** concepts. A name in this list does not automatically qualify as an entity: its inclusion must be justified by business meaning, identity, lifecycle, relationships, and the need to retain facts about it.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Define entity, entity instance, attribute, identifier, relationship, and constraint.
2. Decide whether a business concept should be modeled as an entity or an attribute.
3. Model one-to-one, one-to-many, and many-to-many relationships.
4. State minimum and maximum cardinality and optionality in both directions.
5. Explain candidate keys, primary keys, natural keys, surrogate keys, and foreign keys.
6. Justify identifiers using uniqueness, stability, cross-source consistency, mutability, and privacy.
7. Resolve Customer–Account many-to-many relationships through `AccountHolding`, including relationship-specific role and validity dates.
8. Define referential integrity and evaluate restrict, cascade, and nullify behavior for deletion or key changes.
9. Model supertype/subtype structures such as `Party` → `Person` and `Organisation` where justified.
10. Model time-dependent relationships using valid-from/valid-to semantics.
11. Distinguish structural constraints from rules requiring database, application, or validation-process enforcement.
12. Detect and resolve ambiguous rules, repeating groups, missing entities, circular dependencies, fan traps, and chasm traps.
13. Validate an ER model using positive and negative test cases and maintain a rules register.

## 2. Why the topic matters in real-world Data Architecture

The entity, relationship, key, and constraint decisions made here propagate into physical schemas, APIs, ingestion pipelines, data products, reports, and governance. A defect can be expensive because it becomes embedded in interfaces and historical data before anyone notices.

| Modeling decision | Consequence if wrong | Illustrative Northbridge Bank risk |
|---|---|---|
| Entity versus attribute | Important lifecycle or relationships cannot be represented | Storing all addresses in one text field loses address history and address type. |
| Cardinality and optionality | Invalid states are accepted or valid states are excluded | A design allowing only one customer per account cannot represent a joint account. |
| Identifier | Duplicate or changing identity | A customer’s legal name is used as the primary identifier and changes later. |
| Associative entity | Relationship facts have nowhere to live | Holder role and validity dates are duplicated or lost. |
| Referential integrity | Orphans and contradictory records | A transaction points to a nonexistent account. |
| Temporal relationship | Past facts are overwritten | A former account holder appears to be the current holder in historical reporting. |
| Enforcement choice | Rules are documented but not actually checked | A platform without native foreign keys accepts orphan transactions without alerting anyone. |
| Join-path design | Analytics silently multiplies or drops rows | Joining two independent one-to-many branches creates a fan trap. |

An ER model is not just a picture of tables. It is a reviewable statement of identity, relationships, valid states, and assumptions. Every relationship should have a clear verb, direction, minimum and maximum cardinality, and a rule for invalid cases.

## 3. Prerequisite knowledge

The module roadmap identifies these prerequisites:

- **Module 1 — Conceptual, logical and physical models:** understand the difference between business concepts, logical structures, and physical implementation.
- **Stage 2D.1, Topic 3:** business capabilities, domains, and ownership.
- Basic SQL and relational concepts: tables, keys, joins, and the ability to read simple schema definitions.

This lesson does not assume prior ER-modeling expertise.

### Vocabulary

| Term | Definition |
|---|---|
| **Entity type** | A category of business thing the model tracks, such as Account. |
| **Entity instance** | One particular member of an entity type, such as illustrative account `ACC-800`. |
| **Attribute** | A fact about an entity or relationship, such as `AccountStatus` or a holder’s `ValidFrom`. |
| **Identifier** | Attribute or attribute combination used to distinguish one instance from others. |
| **Candidate key** | A minimal set of attributes that uniquely identifies each instance under the model’s rules. |
| **Primary key** | The candidate key selected as the principal identifier in a relational design. |
| **Natural key** | An identifier that has meaning in the business or source domain, such as an approved account number. |
| **Surrogate key** | An identifier assigned to distinguish instances without carrying business meaning. |
| **Foreign key/reference** | A value or relationship that points to an identifier in another entity type. The exact enforcement depends on implementation. |
| **Cardinality** | The minimum and maximum number of related instances allowed. |
| **Optionality** | Whether participation or an attribute may be absent. In min/max notation, minimum `0` indicates optional participation and minimum `1` indicates mandatory participation. |
| **Associative entity** | An entity used to represent a relationship, especially a many-to-many relationship, when the relationship needs identity, attributes, or history. |
| **Referential integrity** | The rule that a reference must resolve to a valid referenced instance, subject to an explicitly defined lifecycle policy. |
| **Valid time** | The period during which a fact or relationship is true in the modeled business domain. |
| **Structural constraint** | A rule that can be expressed directly by the model’s structure or a supported declarative constraint, such as uniqueness or mandatory participation. |
| **Procedural rule** | A rule requiring a process, transaction logic, application behavior, or validation workflow because structure alone cannot express it. |
| **Fan trap** | A join-path ambiguity where two independent one-to-many branches can multiply rows and distort aggregates. |
| **Chasm trap** | A join-path ambiguity where an optional or missing relationship causes a query path to lose expected records or makes the intended association unclear. |

## 4. Beginner-level learning sequence

### 4.1 Entity, instance, attribute, and relationship

An **entity** is a business thing the organisation needs to distinguish and retain facts about. An **instance** is one occurrence of that thing. An **attribute** records a fact about an instance. A **relationship** states how instances are connected.

Illustrative examples:

- Entity type: `Account`
- Instance: account `ACC-800`
- Attributes: `AccountType`, `AccountStatus`, `OpenedDate`
- Relationship: Account is held by one or more Parties, through `AccountHolding` in the logical model used here.

A noun is not automatically an entity. Ask:

1. Does the business need to distinguish individual instances?
2. Does it have its own identifier or a defensible way to identify it?
3. Does it have attributes or a lifecycle of its own?
4. Does it participate in relationships?
5. Would treating it as an attribute lose facts, history, integrity, or reuse?

### 4.2 Entity versus attribute: worked decisions

All decisions in this table are illustrative and must be validated for a real implementation.

| Candidate concept | Possible modeling choice | Reasoning and trade-off |
|---|---|---|
| Account status | Attribute of Account | A status value usually describes an account instance. A separate `AccountStatus` reference entity may be justified if status definitions, ownership, localization, or lifecycle metadata must be governed. |
| Legal name | Attribute on a Party/Customer version or a name-history entity | A single current attribute is simpler, but cannot reconstruct historical names. Use a separate history structure if effective-dated names are required. |
| Address | Entity if separately identified, shared, typed, or historized; otherwise a value structure/attribute group may suffice | A single text field is easy but hard to validate, reuse, or historize. Avoid creating an entity solely to make a diagram larger. |
| Contact | Candidate entity if contacts have type, verification, consent, lifecycle, or history | A repeated `Phone1`, `Phone2`, `Email1` group is inflexible. If only one simple value is needed, an attribute may be sufficient. |
| Branch | Entity if accounts/products/operations refer to a branch with its own identity and attributes | If branch identity and lifecycle matter, an attribute such as `BranchName` on Account duplicates meaning and makes change harder. |
| Product | Entity if product definitions are governed, reused, versioned, or related to bundles | A free-text product name in each transaction makes catalog consistency difficult. |
| AccountHolding | Associative entity | The relationship itself has role and valid-time attributes and must represent multiple holders. |
| Transaction | Entity | Each transaction must be individually identified, referenced, and retained for audit/analysis. |

### 4.3 Candidate entity inventory for Northbridge Bank

These are candidates, not mandatory facts. The initial scope below is illustrative.

| Candidate | Include in this lesson’s logical model? | Justification / boundary |
|---|---|---|
| `Party` | Yes, as a supertype candidate | Provides a shared identity for a person or organisation where both may act in customer, holder, or guardian roles. Confirm whether the bank’s domain truly needs both. |
| `Customer` | Yes, as a **subtype in this specific illustrative model** | Customer status and customer-specific lifecycle differ from being a Party in general. This is a modeling choice, not a universal rule. If customer is only a capacity in which a Party acts, or every Party in scope is a customer, a role relationship or a simpler Party model may be more appropriate. Do not use “subtype” and “role” interchangeably. |
| `Account` | Yes | Core business entity with its own identifier, lifecycle, and relationships. |
| `AccountHolding` | Yes | Resolves multiple holders and stores role and valid-time facts about the relationship. |
| `Product` | Yes, as a candidate | Needed to govern product definitions and model nested bundles. A transaction’s product association still needs a business rule. |
| `Branch` | Conditional | Include if accounts are assigned to branches, branches own relationships, or branch identity/history matters. The examples assume an Account has zero or one designated servicing branch. This is not a universal banking rule. |
| `Transaction` | Yes | Individually identified event/record associated with an Account under the illustrative rule. |
| `Address` | Conditional | Include if multiple addresses, address types, shared addresses, or history matter. The temporal-name scenario demonstrates that address modeling must also be decided from requirements. |
| `Contact` | Conditional | Include if contact methods have type, verification, consent, lifecycle, or history. A single contact string may be an attribute in a simpler scope. |

**Scope assumption for worked examples:** this lesson uses Party, Customer, Account, AccountHolding, Product, Transaction, and a conditional Branch relationship. In the primary diagram, `Customer` is modeled as a subtype of `Party`, keyed by the same `PartyID`; that design assumes at most one Customer subtype instance per Party. If the domain instead treats customer status as a role with its own start/end periods or allows multiple customer relationships per Party, model that role explicitly and revise the cardinalities. Address and Contact are discussed as modeling decisions rather than mandatory entities. The model does not assume that all nine candidate concepts must appear in every Northbridge design.

**Illustrative domain for PartyType:** for the examples that use `PartyType`, the allowed conceptual values are `PERSON` and `ORGANISATION`; the model assumes a Party must be exactly one of these types. This assumption is only for the exercises. If other party types exist, or a Party can belong to both types, revise the completeness/disjointness rules rather than silently extending the list.

### 4.4 Relationships: one-to-one, one-to-many, many-to-many

A relationship connects instances of entity types. Read it in both directions; one direction alone is incomplete.

| Relationship type | Typical min/max pattern | Example |
|---|---|---|
| One-to-one (1:1) | Each A relates to at most one B, and each B to at most one A; minimums depend on the rule | One Party may have at most one current Customer profile in this illustrative design, and each Customer profile belongs to exactly one Party. |
| One-to-many (1:M) | One A can relate to many B instances; each B may relate to one A | One Account may have zero or many Transactions; each Transaction belongs to exactly one Account. |
| Many-to-many (M:N) | Many A instances can relate to many B instances | A Customer/Party can hold many Accounts, and an Account can have multiple holders. Resolve through AccountHolding when relationship facts matter. |

### 4.5 Cardinality and optionality in both directions

Use **minimum..maximum** notation. `0..*` means zero or many; `1..1` means exactly one; `0..1` means zero or one; `1..*` means one or many.

For each relationship, state the rule from both ends.

#### Worked relationship table (illustrative assumptions)

| Relationship | From the first entity | Min..max | From the second entity | Min..max |
|---|---|---:|---|---:|
| Party — Customer | A Party may have … Customer profiles | `0..1` | A Customer profile belongs to … Party | `1..1` |
| Party — AccountHolding | A Party may participate in … holdings | `0..*` | Each AccountHolding identifies … Party | `1..1` |
| Account — AccountHolding | An Account has … holdings | `1..*` | Each AccountHolding identifies … Account | `1..1` |
| Account — Transaction | An Account has … Transactions | `0..*` | Each Transaction belongs to … Account | `1..1` |
| Branch — Account | A Branch services … Accounts | `0..*` | An Account is assigned to … designated Branch | `0..1` |
| Product — ProductBundleComponent (parent role) | A Product may contain … component entries | `0..*` | Each component entry has … parent Product | `1..1` |
| Product — ProductBundleComponent (component role) | A Product may appear as a component in … bundle entries | `0..*` | Each component entry refers to … component Product | `1..1` |

These min/max values are not discovered by looking at a diagram; they are business rules. For example, Account–AccountHolding is `1..*` on the Account side only because this lesson assumes every in-scope account has at least one holder. If the business permits accounts to be created before holders are assigned, the minimum must change to `0`.

#### Optionality is not the same as maximum cardinality

- `0..1`: optional, at most one.
- `1..1`: mandatory, exactly one.
- `0..*`: optional participation, potentially many.
- `1..*`: mandatory participation, one or many.

“Many” does not mean “mandatory.” A customer can have zero accounts and still be valid under the illustrative model. Likewise, an Account can have zero transactions if it has not yet been used. Do not infer mandatory participation merely because a relationship is important.

### 4.6 Readable ER diagram

The following is a logical-level diagram. Cardinalities and definitions in the tables are authoritative if a text diagram is visually ambiguous.

```text
                 +------------------+
                 |      Party       |
                 | PK PartyID       |
                 +------------------+
                    1          0..1
                    |            |
                    |            v
                    |      +------------------+
                    |      |     Customer     |
                    |      | PK/FK PartyID    |
                    |      | CustomerStatus   |
                    |      +------------------+
                    |
                    | 1
                    |          0..*
             +------------------------+
             |    AccountHolding      |
             | PK AccountHoldingID    |
             | FK PartyID             |
             | FK AccountID           |
             | HolderRole             |
             | ValidFrom, ValidTo     |
             +------------------------+
                    | 0..*         1..*
                    |                 |
                    v                 v
             +------------------+  +------------------+
             |      Party       |  |      Account     |
             | same Party type  |  | PK AccountID     |
             +------------------+  | FK BranchID?     |
                                   +------------------+
                                           1
                                           |
                                         0..*
                                   +------------------+
                                   |   Transaction    |
                                   | PK TransactionID |
                                   | FK AccountID     |
                                   +------------------+
```

The repeated Party box above is a readability aid to show the two ends of AccountHolding; it is the **same Party entity type**, not a second entity. In a production diagram, draw one Party box with both relationship lines to avoid visual confusion.

A more compact relationship view is:

```text
Party 1 -------- 0..* AccountHolding 1..* -------- 1 Account
Customer 0..1 --- 1 Party
Account 1 ------- 0..* Transaction
Branch 0..* ----- 0..1 Account
```

Read the line labels from both ends and confirm them against the relationship inventory. In these text diagrams, a min/max label printed next to an entity names the number of instances of **that entity** that may be related to one instance at the opposite end. Do not interpret the labels as participation counts for the nearest relationship box without checking the direction table.

#### Beginner exercise — Branch network extraction

**Illustrative description:** A bank operates multiple branches. Each branch has a unique branch code and a name. A branch may service many accounts; an account may have no designated servicing branch while it is being opened, and at most one designated servicing branch at a time. A branch can exist before any account is assigned to it.

1. List the candidate entities and attributes.
2. State the identifier for each entity and explain why `BranchName` is not assumed unique.
3. Write both directional relationship statements with minimum and maximum cardinality.
4. Give one valid case and one invalid case.

**Model answer:** entities are `Branch(BranchID, BranchCode, BranchName)` and `Account(AccountID, …, optional BranchID reference)`; `BranchCode` is a candidate key only if the business guarantees uniqueness and non-reuse within the model scope. Branch → Account is `0..*`; Account → Branch is `0..1`. Valid: an account with no assigned branch during opening. Invalid: an account references a nonexistent non-null BranchID. The logical model states these rules; enforcement must be selected and tested separately.

## 5. Intermediate-level learning sequence

### 5.1 Resolve Customer–Account many-to-many with AccountHolding

A direct relationship between Customer and Account is many-to-many if a customer may hold many accounts and an account may have multiple holders. A simple foreign key on Account that permits only one Customer would fail to represent joint holders. Repeating `CustomerID1`, `CustomerID2`, and `CustomerID3` would impose an arbitrary limit and create repeating groups.

Use an associative entity:

```text
Party 1 -------- 0..* AccountHolding 1..* -------- 1 Account

AccountHolding
- AccountHoldingID (identifier)
- PartyID (reference to Party)
- AccountID (reference to Account)
- HolderRole
- ValidFrom
- ValidTo (optional for a current/open-ended relationship)
```

Each AccountHolding instance represents **one party’s one role on one account for one validity interval**.

Illustrative rows:

| AccountHoldingID | PartyID | AccountID | HolderRole | ValidFrom | ValidTo |
|---|---|---|---|---|---|
| AH-001 | P-101 | A-800 | PRIMARY_HOLDER | 2024-01-01 | null |
| AH-002 | P-102 | A-800 | JOINT_HOLDER | 2024-01-01 | null |
| AH-003 | P-101 | A-801 | SOLE_HOLDER | 2024-05-10 | null |
| AH-004 | P-102 | A-800 | JOINT_HOLDER | 2024-01-01 | 2025-08-31 |

All values are illustrative. Rows AH-002 and AH-004 have overlapping valid-time intervals and therefore violate the illustrative rule that valid-time intervals for the same Party–Account–Role combination must not overlap, even though AH-004 has an end date. The example intentionally exposes a rule that needs explicit definition: can the same role be re-entered, can intervals overlap, and is a new role change a new relationship instance or an update to the prior one?

A defensible illustrative rule set is:

- Every AccountHolding references exactly one existing Party and one existing Account.
- `HolderRole` and `ValidFrom` are mandatory.
- `ValidTo` may be absent to mean “no known end date” under this model’s convention.
- If `ValidTo` is present, it must be later than `ValidFrom`.
- For the same Party, Account, and role, valid-time intervals must not overlap unless a documented business exception permits it.
- Account must have at least one valid holder at each required point in time. Whether this is a continuous invariant or only required at account opening/operational checkpoints must be confirmed by the business.

The associative entity has attributes because the **relationship itself** has facts. `HolderRole` does not describe Party in general; it describes that Party’s role on that particular Account during a period.

### 5.2 Keys and identifiers

#### Candidate keys

A candidate key is a **minimal** attribute set that uniquely identifies each entity instance. “Minimal” means no attribute can be removed while uniqueness still holds.

Illustrative examples:

- `PartyID` is a candidate key for Party if unique and stable in the domain.
- `AccountID` is a candidate key for Account.
- `TransactionID` is a candidate key for Transaction.
- For AccountHolding, a possible alternate candidate key might be `(PartyID, AccountID, HolderRole, ValidFrom)` if the business guarantees no duplicate start for that combination. This is an assumption, not automatically true. A separate `AccountHoldingID` may be selected as primary key, with a uniqueness rule on the natural relationship key if approved.

#### Primary, natural, and surrogate keys

| Key kind | Meaning | Advantages | Risks / trade-offs |
|---|---|---|---|
| Natural key | Business-meaningful identifier, such as an approved account number | May already exist in source systems; recognizable to business users | Can change, be reused, be private, or be inconsistent across sources. |
| Surrogate key | Assigned identifier with no business meaning | Can remain stable when business attributes change; can unify multiple source identities | Requires mapping/governance; may hide duplicate real-world identities; generation is a physical design choice. |
| Primary key | The candidate key selected as the principal identifier in a relational implementation | Gives a consistent reference target | Choice must be justified; it does not replace alternate-key rules. |
| Foreign key | Reference to another entity’s identifier | Supports referential integrity when enforced | Enforcement may be unavailable or incomplete in some platforms; a logical reference rule still exists. |

A surrogate key is not automatically better. Choose based on the actual identity problem and document the trade-off.

#### Identifier decision criteria

Evaluate each proposed identifier against these questions:

1. **Uniqueness:** Is it unique for every instance in the model’s full scope?
2. **Stability:** Will it remain the same when attributes or business status change?
3. **Cross-source consistency:** Can multiple systems refer to the same entity, or do they use different identifiers?
4. **Mutability and reuse:** Can the value change or be recycled for another entity?
5. **Privacy:** Does exposing the identifier reveal sensitive personal or account information?
6. **Lifecycle:** What happens on merge, split, correction, closure, or source migration?
7. **Operational usability:** Can consumers map and reconcile the identifier reliably?

**Invalid identifier example:** use `LegalName` as the primary identifier for Party. A legal-name change can break references, names are not guaranteed unique, and names may be sensitive.

**More defensible illustrative approach:** use a governed `PartyID` for domain identity, preserve source-system identifiers in a mapping structure when required, and define merge/split handling. The physical mechanism that generates or stores `PartyID` is deferred.

### 5.3 Candidate-key and foreign-key examples

Logical examples (not product-specific DDL):

```text
Party
- PartyID             identifier (candidate key)
- PartyType
- CreatedDate

Customer
- PartyID             identifier and reference to Party
- CustomerStatus

Account
- AccountID            identifier (candidate key)
- AccountStatus
- BranchID             optional reference to Branch

AccountHolding
- AccountHoldingID     identifier (candidate key)
- PartyID              mandatory reference to Party
- AccountID            mandatory reference to Account
- HolderRole
- ValidFrom
- ValidTo              optional

Transaction
- TransactionID        identifier (candidate key)
- AccountID            mandatory reference to Account
- PostedAt
- Amount
- Currency
```

The model requires that a reference resolve to an existing instance under the defined lifecycle policy. Whether that is enforced with a native foreign-key constraint, application transaction, or validation/reconciliation process is a physical/operational decision.

### 5.4 Referential integrity and deletion/change policies

Referential integrity means a reference must point to a valid referenced instance. It also requires a lifecycle policy: what should happen when the referenced entity is changed, merged, or proposed for deletion?

| Policy | Meaning | Appropriate only when… | Main risk |
|---|---|---|---|
| **Restrict / reject** | Prevent deletion or change while dependents exist | The referenced entity must remain available while dependent facts require it | May block cleanup or require a deliberate archival workflow |
| **Cascade** | Propagate deletion/change to dependent records | The dependent records have no independent retention or legal/audit value and the business explicitly permits propagation | Can destroy important history or cause unexpectedly broad deletion |
| **Nullify** | Remove the reference from dependent record | The relationship is genuinely optional after the change and losing the link is acceptable | Can create incomplete or misleading history; cannot be used if the relationship is mandatory |
| **Soft close / retire** | Mark the entity inactive/closed instead of physically deleting it | Historical facts and references must remain interpretable | Requires lifecycle and access rules; does not itself solve every correction |
| **Re-key / mapping** | Preserve identity while changing source representation through a mapping | Source keys change or multiple source identifiers must be reconciled | Mapping mistakes can redirect references or create duplicate identity |

**Illustrative Northbridge policies:**

- A referenced Account with Transactions should normally not be physically deleted while those transactions must be retained. A close/retire policy is a candidate, subject to approved retention rules.
- A Party with historical AccountHolding records should not be removed in a way that destroys holder history. A merge/split or retirement process may be needed.
- If `BranchID` is optional on Account, a branch relationship may be nullified only if the business permits an unassigned account; a branch reassignment is usually an update to the relationship, not a reason to erase the account.
- A Transaction’s Account reference is mandatory in this model, so nullifying it is not an acceptable final state. If an upstream transaction arrives before its Account, the pipeline must hold, quarantine, or otherwise handle it under an approved operational rule rather than silently accept it as a valid transaction.

Changing a business key is not the same as changing entity identity. If an account number changes but the same Account remains, preserve the logical identity and update the mapping or natural-key value according to the approved policy.

### 5.5 Supertype/subtype modeling: Party → Person and Organisation

A supertype captures common identity or attributes shared by more specific entity types. A subtype adds attributes or rules that apply only to members of that subtype.

Illustrative model:

```text
                 +----------------------+
                 |        Party         |
                 | PK PartyID           |
                 | PartyType            |
                 | CreatedDate           |
                 +----------------------+
                    /              \
                   /                \
       +------------------+   +---------------------+
       |      Person      |   |     Organisation    |
       | PK/FK PartyID    |   | PK/FK PartyID       |
       | DateOfBirth?     |   | RegisteredName?     |
       +------------------+   +---------------------+
```

This is a **candidate** structure, not a universal rule. It is useful if both people and organisations can be account holders, customers, or guardians/representatives, and they have common identity plus distinct attributes. If the modeled domain only handles individual customers, a Party supertype may add complexity without enough value.

Define subtype constraints explicitly:

- **Disjointness:** can a Party be both Person and Organisation? Usually not under this illustrative model, but confirm.
- **Completeness:** must every Party be either a Person or Organisation? If yes, the subtypes are total; if unknown or other party types exist, the rule must differ.
- **Role versus type:** “Guardian” and “AccountHolder” are roles/relationships in these scenarios, not subtypes of Party. “Customer” may be a subtype only under the specific model assumption stated in Section 4.3; in another domain it may be a role with its own effective dates. A person may be both a customer and a guardian. Avoid creating separate Party copies for each role, and do not assume that a subtype and a role have equivalent identity or lifecycle semantics.

Do not model “guardian” as a subtype of Person if guardianship is a relationship between a guardian Party and a minor Party. The relationship may have attributes such as role, effective dates, authority type, and evidence reference.

### 5.6 Time-dependent relationships and valid-from/valid-to

A relationship can change over time. If the business needs to know who held an account at a past date, storing only the current holder is insufficient.

A common logical pattern is:

- `ValidFrom`: inclusive beginning of the period.
- `ValidTo`: exclusive end of the period, or a different convention if explicitly chosen.
- `ValidTo = null`: open-ended/current relationship under the chosen convention.
- Valid interval: `[ValidFrom, ValidTo)`.

**Important:** the interval convention must be documented. This lesson uses start-inclusive/end-exclusive intervals. Therefore a relationship ending at `2025-09-01` is not valid at `2025-09-01`, and a new relationship starting on that date can begin without overlap.

Example (illustrative):

| AccountHoldingID | PartyID | AccountID | Role | ValidFrom | ValidTo |
|---|---|---|---|---|---|
| AH-100 | P-201 | A-900 | PRIMARY_HOLDER | 2024-01-01 | 2025-09-01 |
| AH-101 | P-202 | A-900 | JOINT_HOLDER | 2024-01-01 | 2025-09-01 |
| AH-102 | P-203 | A-900 | PRIMARY_HOLDER | 2025-09-01 | null |

This records that P-201 and P-202 were holders before the change and P-203 is the current primary holder after the transition. It does not imply that the account may have only one holder; the full rules for roles and joint holders still apply.

Temporal rules to decide explicitly:

- Can two relationship intervals for the same Party–Account–Role overlap?
- Can there be gaps in holder coverage?
- Does a role change close one row and open another?
- Are corrections to historical facts recorded as corrections, or must the original recorded belief also be preserved?
- Does “valid time” mean when the relationship was true in the business, or “recorded time” mean when the system learned it? These are different concepts.

### 5.7 Structural constraints versus procedural enforcement

A model can state a rule without guaranteeing that a platform enforces it. Classify rules by the mechanism needed.

| Rule | Structural/declarative candidate | May require procedural or application enforcement? | Notes |
|---|---|---|---|
| `PartyID` is unique | Candidate key/unique constraint | Yes, if platform cannot enforce uniqueness | Must be validated at write/ingestion boundaries. |
| Each Customer refers to one Party | Mandatory reference/foreign key | Possibly | `Customer.PartyID` as identifier/reference expresses the logical rule. |
| Each Transaction refers to one Account | Mandatory relationship/foreign key | Possibly | A platform without foreign keys needs validation and reconciliation. |
| `ValidTo` is later than `ValidFrom` | Check constraint may express it | May be needed across records or if check constraints are unavailable | Interval overlap often requires more than a simple row-level check. |
| Account has at least one holder | Not always expressible as a simple foreign key | Usually requires transaction/workflow validation or deferred consistency checking | A parent-to-many child minimum is harder to enforce at every intermediate write. |
| Holder must be an eligible adult unless a guardian relationship exists | Cross-entity conditional rule | Yes, typically service/workflow validation and periodic audit | Requires legal/business definition and reliable age/guardian facts. |
| Product bundle must not contain itself, directly or indirectly | Not expressible as a simple row-level foreign key | Recursive validation, cycle detection, and controlled updates | Requires graph traversal or equivalent logic. |
| Customer status transitions follow an approved state machine | A simple allowed-value check is insufficient | Application/workflow rule and audit | “Status is one of the values” differs from “transition is allowed.” |

A **rule register** should identify both the logical rule and the chosen enforcement mechanism. If the platform cannot enforce the rule declaratively, do not claim that the diagram or schema alone enforces it.

### 5.8 Intermediate exercise: ten test cases (five valid, five invalid)

For this exercise, use the illustrative rules above. “Pass” means the case is valid under those rules; “Reject/hold” means it must not be accepted as valid without a documented exception or corrective process.

| # | Test case | Expected outcome | Explanation |
|---:|---|---|---|
| 1 | One Party is linked to two different Accounts through two AccountHolding rows. | Pass | One Party may hold many Accounts. |
| 2 | Two Parties are current holders of the same Account with different permitted roles. | Pass | Joint holding is supported. |
| 3 | AccountHolding references a nonexistent PartyID. | Reject | Mandatory reference must resolve. |
| 4 | AccountHolding references a nonexistent AccountID. | Reject | Mandatory reference must resolve. |
| 5 | Transaction references an existing AccountID. | Pass | Required relationship is satisfied. |
| 6 | Transaction has no AccountID. | Reject/hold | Transaction-to-Account is mandatory in this model. |
| 7 | `ValidTo` is earlier than `ValidFrom`. | Reject | Interval is invalid. |
| 8 | `ValidTo` equals `ValidFrom` under start-inclusive/end-exclusive convention. | Reject | The interval has zero duration; allow only if a distinct business rule explicitly permits instantaneous events. |
| 9 | A holder’s old interval ends on 2025-09-01 and a replacement interval begins on 2025-09-01. | Pass | Intervals do not overlap under `[from, to)` semantics. |
| 10 | An Account has no Transactions because it has not yet been used. | Pass | Account-to-Transaction participation is `0..*`; transactions are not mandatory for every Account. |

## 6. Advanced-level learning sequence

### 6.1 Resolve ambiguity before choosing structure

Ambiguity is a business-definition problem first. Do not silently decide what a phrase means.

Example: “A customer has one address.”

Possible meanings include:

- Exactly one address ever recorded.
- One current residential address, but multiple other address types.
- Multiple addresses, each with a purpose and validity period.
- One preferred address plus address history.
- Address shared by multiple Parties.

Each meaning implies a different model. Record the alternatives, ask the accountable domain owner, and retain the decision in the assumptions/open-question log.

### 6.2 Detect common modeling anomalies

#### Repeating groups

**Bad:** `Phone1`, `Phone2`, `Phone3` on Party.

**Problem:** arbitrary limit, sparse columns, inconsistent validation, difficult querying, and no clean place for type/verification/consent/history.

**Candidate correction:** a Contact entity with `ContactID`, `PartyID`, `ContactType`, `ContactValue`, `ValidFrom`, `ValidTo`, and status—only if the business needs multiple independently managed contacts.

#### Missing entity

**Bad:** store `CustomerID`, `HolderRole`, `HolderStartDate`, and `HolderEndDate` directly on Account when an account may have multiple holders.

**Problem:** one Account row cannot represent multiple holder relationships without repeating columns or duplication.

**Correction:** AccountHolding as an associative entity.

#### Circular dependencies

A cycle is not automatically wrong. For example, Party can be related to another Party as guardian, and Product can contain Product recursively. The problem is an **unresolved dependency cycle** that makes creation, deletion, or validation impossible or ambiguous.

For guardian relationships, do not require a minor Party to have a guardian record before the Party can exist if the guardian is itself a Party and the process creates the minor first. Use a staged lifecycle or transaction workflow that permits a controlled pending state, while ensuring the final state meets the rule. Document the permitted temporary states.

#### Fan trap

A fan trap occurs when two one-to-many relationships branch from the same entity and a query joins both branches at once, multiplying combinations.

Illustrative structure:

```text
              Account
              /     \
             /       \
       Transaction   AccountHolding
             \       /
              joined result
```

If Account A has 3 transactions and 2 holdings, a direct join may produce 3 × 2 = 6 rows. Summing transaction amount after this join can double-count each transaction once per holder.

**Correction:** aggregate each branch to the required grain before joining, or use a query/model structure that preserves the declared grain. State the grain of the result and test totals against independent totals.

#### Chasm trap

A chasm trap occurs when the model or query path implies an association that is not guaranteed, often because one or more optional relationships are missing. A query can lose valid records by using an inner join through an optional path, or make a false association by treating two independent branches as if they were directly related.

Illustrative example: an Account may have no designated Branch (`BranchID` optional), but a report joins Account to Branch using an inner join and then reports only accounts with a branch. The result silently excludes unassigned accounts.

**Correction:** clarify whether the relationship is optional, select join semantics that match the question, and test the count before and after the join. If the business question requires every Account, preserve accounts without a Branch and represent the missing relationship explicitly.

### 6.3 Recursive Product bundles

Illustrative business statement: a product can be sold in bundles, and a bundle can contain other bundles.

Candidate structure:

```text
Product 1 -------- 0..* ProductBundleComponent
Product 1 -------- 0..* ProductBundleComponent
                    (two roles: parent product and component product)

ProductBundleComponent
- ProductBundleComponentID
- ParentProductID
- ComponentProductID
- Quantity
- ValidFrom
- ValidTo
```

Each component row links exactly one parent Product to exactly one component Product. A Product may be a parent in zero or many component rows and may be a component in zero or many rows.

Potential anomaly: **recursive cycles**. For example, Bundle A contains Bundle B and Bundle B contains Bundle A. An unbounded expansion can loop forever or double-count quantities. A self-loop (A contains A) is the simplest cycle, but longer cycles are also invalid under the illustrative rule.

Illustrative rules:
- A ProductBundleComponent references two existing Products.
- Parent and component must differ.
- The recursive containment graph must be acyclic.
- Quantity must be positive.
- Validity intervals for duplicate parent/component relationships must not overlap unless explicitly allowed.
- Only products approved as bundle-capable may act as parent, if that is the chosen business rule.

A foreign key can confirm that both products exist; it cannot by itself prevent a multi-row cycle. Cycle prevention needs recursive validation, controlled updates, or a graph-validation process. The model must state the rule; implementation must enforce it.

### 6.4 Scenario A — Joint account with a minor and guardian

**Situation:** An illustrative joint account has two holders, one of whom is a minor. The minor has a guardian.

Model the roles and relationships separately:

```text
Party (minor) ---- AccountHolding(role=JOINT_HOLDER) ---- Account
Party (guardian) ---- Guardianship relationship ---- Party (minor)
```

Do not represent the guardian as a second holder unless the business says the guardian is also an account holder. Do not represent “guardian” as a subtype of Party merely because it is a role.

Potential `Guardianship` relationship attributes (illustrative candidates): `GuardianshipID`, `GuardianPartyID`, `MinorPartyID`, `AuthorityType`, `ValidFrom`, `ValidTo`, `EvidenceReference`, `Status`.

Open questions for the domain owner:
- Can there be more than one guardian?
- Is guardianship legally verified, and how is revocation represented?
- Must the guardian also be a customer?
- Does the guardian have authority to transact, or only consent/oversight?
- Is an account allowed to be opened before guardianship evidence is verified?
- What does the system do when guardianship expires or is revoked?

Structural constraints can ensure the referenced Party records exist and that required fields are present. The rule “a minor holder must have a verified eligible guardian with the required authority” is conditional and cross-entity; it generally requires workflow/application validation and periodic review, not just an ER line.

### 6.5 Scenario B — Customer legal-name change with historical transactions

**Situation:** A Party’s legal name changes, but transactions must retain the name in force at the legally relevant transaction time.

A single mutable `Party.LegalName` field cannot reliably answer historical “as-of” questions. First clarify which timestamp defines the business event: transaction initiation, execution, effective date, posting, or another approved timestamp. `Transaction.PostedAt` is suitable only if the business confirms that posting time is the required reference time. Consider a name-history entity if the business requires legal names to be valid over time:

```text
Party 1 -------- 0..* PartyNameHistory

PartyNameHistory
- PartyNameHistoryID
- PartyID
- LegalName
- ValidFrom
- ValidTo
```

Under the illustrative `[ValidFrom, ValidTo)` convention, each historical name interval has a defined start and optional end. The business must decide how to handle corrections, overlapping intervals, and whether a transaction stores a snapshot of the name or joins to name history by the transaction’s effective time.

These approaches are not equivalent:

- **Temporal lookup:** derive the name valid at the business-approved transaction timestamp. `Transaction.PostedAt` is one possible timestamp only if posting time is explicitly confirmed as the required reference time. This requires complete, correct name history.
- **Event snapshot:** store the legally relevant name on the transaction/event record at the time it was recorded. Preserves the snapshot but duplicates a fact and requires a clear policy about corrections.
- **Both:** retain a governed history plus an event snapshot where audit requirements justify it.

The correct choice depends on the approved business/legal requirement. Do not assume that a current name plus a timestamp is enough.

### 6.6 Scenario C — Product bundles that contain bundles

Use the recursive `ProductBundleComponent` structure from Section 6.3. Check at least these cases:

- Product A contains Product B: valid if both exist and A is bundle-capable.
- Product A contains Product A: invalid self-cycle.
- A contains B, B contains C, C contains A: invalid indirect cycle.
- A contains B and B contains A only in non-overlapping validity periods: requires an explicit temporal business rule; do not automatically accept or reject without deciding whether cycle validation applies across all history or only simultaneously active bundles.
- Component product is deleted while referenced: apply the approved restrict/retire policy; do not leave an unresolved reference.

The model should make the relationship visible. Recursive cycle detection is a validation/enforcement requirement beyond a simple foreign key.

### 6.7 Rules register: rule → model element → enforcement

All entries below are illustrative rules, not Northbridge Bank policy.

| Rule ID | Illustrative rule | Model element | Constraint category | Enforcement candidate | Evidence/test |
|---|---|---|---|---|---|
| ER-01 | PartyID is unique and mandatory. | Party.PartyID | Structural | Primary/unique constraint or equivalent validation | Duplicate PartyID rejected. |
| ER-02 | A Customer profile belongs to exactly one Party; a Party has at most one Customer profile in this model. | Customer.PartyID | Structural | Identifier/reference and uniqueness | Orphan Customer or duplicate profile rejected. |
| ER-03 | Every AccountHolding references one existing Party and one existing Account. | AccountHolding.PartyID, AccountID | Structural | Foreign keys where supported; otherwise reference validation | Unknown Party/Account rejected or quarantined. |
| ER-04 | An Account has at least one holder during required operational periods. | Account–AccountHolding | Cross-entity invariant | Opening/holder-change workflow and reconciliation | Account with zero holders at required checkpoint flagged. |
| ER-05 | Holder role and ValidFrom are mandatory. | AccountHolding.HolderRole, ValidFrom | Structural | Required-field/domain checks | Missing role/date rejected. |
| ER-06 | ValidTo, when present, is later than ValidFrom. | AccountHolding.ValidFrom, ValidTo | Row-level constraint | Check constraint or application validation | Invalid interval rejected. |
| ER-07 | Valid-time intervals for the same Party–Account–Role do not overlap unless an approved exception permits it. | AccountHolding | Cross-row temporal rule | Transaction/workflow validation plus audit | Any overlapping pair fails the test. |
| ER-08 | Each Transaction refers to exactly one existing Account. | Transaction.AccountID | Structural business rule | Foreign key or ingestion/service validation | Orphan transaction rejected/held. |
| ER-09 | Account may have zero or one designated Branch. | Account.BranchID | Structural | Optional reference/foreign key | Missing Branch is allowed; unknown non-null Branch rejected. |
| ER-10 | A minor holder must have verified guardianship with required authority. | Party, AccountHolding, Guardianship | Conditional cross-entity rule | Application workflow, evidence validation, periodic review | Minor holder without valid authority is blocked or flagged. |
| ER-11 | A Party’s legal name history has non-overlapping validity intervals under the chosen policy. | PartyNameHistory | Cross-row temporal rule | Temporal validation and reconciliation | Overlapping intervals rejected or escalated. |
| ER-12 | Product bundles must not contain recursive cycles. | ProductBundleComponent | Recursive graph rule | Cycle detection on bundle changes and periodic validation | Direct and indirect cycles rejected. |
| ER-13 | Component quantity must be positive. | ProductBundleComponent.Quantity | Row-level constraint | Check/application validation | Zero or negative quantity rejected. |
| ER-14 | Party roles are not duplicated as separate Party identities. | Party and role relationships | Identity/business rule | Domain identity governance and reconciliation | Same Party acting as Customer and Guardian maps to one Party. |

A rules register must say what is required and how it is checked. Writing a rule in a register does not enforce it. The enforcement mechanism must be implemented, tested, monitored, and assigned to an owner.

### 6.8 Twenty illustrative validation cases

The following 20 cases are designed for the Northbridge illustrative rules. The expected outcome is based on the assumptions stated in this lesson. If a real business approves a different rule, update the model and test set together.

| # | Case | Expected outcome | Rule/reason |
|---:|---|---|---|
| 1 | Party `P-101` has a unique PartyID and exactly one allowed illustrative PartyType (`PERSON` or `ORGANISATION`). | Pass | ER-01 plus the stated PartyType domain/completeness assumption. |
| 2 | Two distinct Party instances share PartyID `P-101`. | Reject | ER-01 uniqueness violation. |
| 3 | A Customer profile references existing Party `P-101`. | Pass | ER-02. |
| 4 | A Customer profile references a missing Party. | Reject | ER-02 referential integrity. |
| 5 | One Party has two Customer profiles despite the one-profile-per-Party assumption. | Reject | ER-02 uniqueness rule. |
| 6 | Two Parties hold the same Account through separate AccountHolding records. | Pass | Joint holding is supported. |
| 7 | One Party holds two different Accounts through separate AccountHolding records. | Pass | Party may participate in many holdings. |
| 8 | AccountHolding references a missing Account. | Reject | ER-03. |
| 9 | AccountHolding has no HolderRole. | Reject | ER-05. |
| 10 | AccountHolding has ValidFrom but no ValidTo. | Pass | Open-ended relationship permitted by convention. |
| 11 | ValidTo is earlier than ValidFrom. | Reject | ER-06. |
| 12 | ValidTo equals ValidFrom under `[from, to)` convention. | Reject | Zero-duration interval not allowed by this assumption. |
| 13 | Same Party–Account–Role has overlapping valid-time intervals, including a historical interval overlapping an open-ended interval. | Reject/review | ER-07, unless an approved exception exists. |
| 14 | A transaction references an existing Account. | Pass | ER-08. |
| 15 | A transaction has no Account reference. | Reject/hold | ER-08 mandatory relationship. |
| 16 | Account has no BranchID. | Pass | Branch assignment is optional in this example. |
| 17 | Account references an unknown non-null BranchID. | Reject | Non-null reference must resolve. |
| 18 | Minor is a joint holder and has a verified guardian relationship with required authority; the approved workflow confirms the evidence and eligibility checks. | Pass | ER-10. This is valid only after the stated workflow checks succeed. |
| 19 | Minor is a joint holder but has no verified required guardianship authority. | Reject/block; if the platform cannot block at entry, quarantine and flag as invalid pending resolution—never mark as valid | ER-10 conditional rule. |
| 20 | Product A contains B, B contains C, and C contains A in the active bundle graph. | Reject | ER-12 indirect recursive cycle. |

Additional useful tests include a legal-name interval overlap, a product self-loop, non-positive component quantity, and a delete request for an Account referenced by retained Transactions. The industry exercise should include these if they are in the implemented scope.

### 6.9 Ambiguity and anomaly review method

#### Advanced exercise — Resolve four planted ambiguities/anomalies

For each case, list at least two plausible interpretations where the business rule is ambiguous, identify affected model elements, choose a provisional assumption only when necessary, state the question for the domain owner, and update the diagram, rules register, and tests.

1. **“A customer has one address.”** Determine whether this means one current mailing address, one address of each type, or one address ever recorded. Do not choose an Address entity until multiplicity, reuse, and history needs are clear.
2. **“Every account has a branch.”** Reconcile this statement with accounts that may be unassigned during opening. Decide whether the rule applies at creation, approval, or all times; make the minimum cardinality and workflow invariant agree.
3. **“A customer holds an account.”** Determine whether the relationship needs holder role and validity periods. If so, use `AccountHolding`; do not place `HolderRole` on Party or duplicate holder columns on Account.
4. **“Bundles can contain bundles.”** Decide whether the rule permits historical cycles in non-overlapping validity periods or prohibits cycles across all recorded history. State the validation scope and test direct and indirect cycles.

**Expected output:** four ambiguity records with the statement, interpretations, decision owner, selected or provisional rule, affected model element, valid/invalid test, enforcement candidate, and status. A provisional assumption must remain visibly unapproved until confirmed.

For every ambiguity or anomaly:

1. Quote the ambiguous rule or show the structural symptom.
2. List plausible interpretations without selecting one silently.
3. Identify the affected entity, relationship, key, or constraint.
4. Explain the consequence of each interpretation for valid data, history, and consumers.
5. Ask the domain owner for a decision or label a temporary assumption.
6. Update the entity inventory, relationship inventory, rules register, and tests.
7. Decide how the rule is enforced and how failures are observed.
8. Re-review the diagram and sample joins after the change.

## 7. Industry-application exercises

Build and validate an ER model for the Northbridge customer, account, product, and transaction domain. Use the candidate entities from Section 4.3, but justify each inclusion. Do not add every candidate automatically.

### Exercise 1 — Entity and relationship inventory

Deliver:
- Entity inventory with definitions and rationale for inclusion/exclusion.
- Relationship inventory with a verb, direction, minimum, maximum, optionality, and rule ID for every relationship.
- Identifier inventory with candidate keys, selected logical identifier, and justification.
- List of assumptions and open questions.

### Exercise 2 — Model and rules register

Create an ER diagram for Party, Customer, Account, AccountHolding, Transaction, Product, and ProductBundleComponent. Add Branch, Address, Contact, PartyNameHistory, and Guardianship only where the stated requirements justify them. Use separate relationship roles for recursive Product containment.

For every relationship, write both directional statements. Example:

| Direction | Statement | Min..max |
|---|---|---:|
| Party → AccountHolding | A Party may participate in zero or many AccountHolding records. | `0..*` |
| AccountHolding → Party | Each AccountHolding identifies exactly one Party. | `1..1` |
| Account → AccountHolding | An Account has one or more holders during required periods under the illustrative rule. | `1..*` |
| AccountHolding → Account | Each AccountHolding identifies exactly one Account. | `1..1` |

If you change the assumption about minimum holders, update both the table and test cases.

### Exercise 3 — Twenty-case validation suite

Use the 20 cases in Section 6.8 as the baseline. For each, record:
- Test ID and rule ID.
- Input setup.
- Expected outcome: pass, reject, hold/quarantine, or manual review.
- Actual outcome when implemented.
- Enforcement location.
- Failure evidence and corrective action.

Do not call a case “rejected by the model” unless the chosen model representation or implemented validation actually rejects it. A diagram documents the rule; it does not execute the rule.

### Exercise 4 — Identifier trade-off review

Compare natural and surrogate identifier options for Party, Account, AccountHolding, and Transaction. Score each option against uniqueness, stability, cross-source consistency, mutability/reuse, privacy, merge/split handling, and operational mapping. Explain what remains undecided until physical design.

### Exercise 5 — Anomaly review

Review a deliberately flawed design with:
- `Phone1`, `Phone2`, and `Phone3` on Party.
- Only one `CustomerID` column on Account despite joint accounts.
- `LegalName` used as Party identifier.
- Transaction without a mandatory Account reference.
- ProductBundleComponent with no recursive-cycle check.
- Account report joining Transactions and AccountHolding before aggregation.
- Account report using an inner join to optional Branch.
- No valid-from/valid-to rules for AccountHolding.

For each defect, name the anomaly, the model element affected, the corrected structure/rule, and the validation test needed.

### Exercise 6 — Scenario write-ups

Write concise, explicit responses to:
1. Joint account with a minor and guardian.
2. Legal-name change with historical transactions.
3. Recursively nested product bundles.

Each response must distinguish entity identity, relationship semantics, temporal requirements, business assumptions, structural constraints, procedural enforcement, and unresolved questions.

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — Joint account with a minor and guardian

**Problem:** A joint account has two holders, one a minor, with a guardian.

**Incorrect shortcut:** Add `GuardianName` as an attribute on Account and treat the guardian as a holder. This loses guardian identity, authority, validity period, and the distinction between guardianship and account holding.

**Better candidate model:**
- Party represents the minor, guardian, and other parties.
- AccountHolding represents each holder’s relationship to the account and its role/history.
- Guardianship represents the relationship between guardian Party and minor Party, with authority and effective dates where required.
- The rule that a minor must have an eligible, verified guardian is conditional and usually requires workflow validation, not merely a relationship line.

**Questions to resolve:** Can the guardian also be a holder? Is more than one guardian allowed? What evidence is authoritative? What happens when authority expires? Can the account exist in a pending state?

### Scenario 2 — Legal-name change with historical transactions

**Problem:** Historical transactions must retain the legal name in force at transaction time.

**Incorrect shortcut:** Update `Party.LegalName` and assume the previous name can be recovered.

**Better candidate approaches:** effective-dated PartyNameHistory; event-time lookup; a transaction snapshot; or a combination if the requirement justifies it. Decide the valid-time convention, treatment of corrections, and event timestamp semantics. Validate that a transaction on a boundary date resolves to exactly one intended name.

**Trade-off:** temporal lookup avoids repeating a name on every transaction but depends on complete, non-overlapping history. Snapshotting improves historical self-containment but duplicates data and requires correction rules.

### Scenario 3 — Recursively nested product bundles

**Problem:** A bundle may contain another bundle. Without cycle checks, A → B → C → A can make expansion infinite or double-count component quantities.

**Better candidate structure:** `ProductBundleComponent(ParentProductID, ComponentProductID, Quantity, ValidFrom, ValidTo)`, with each row referencing two Product instances. Add explicit rules for self-containment, indirect cycles, positive quantities, and time-dependent bundle definitions.

**Enforcement:** reference constraints ensure referenced products exist; recursive validation is needed to prevent cycles. Decide whether cycle checking applies to the current bundle graph or to every historical effective-time slice.

### Scenario 4 — Fan trap in account reporting

**Problem:** Account A has three Transactions and two AccountHolding records. Joining both one-to-many branches yields six rows; transaction amounts may be doubled.

**Correction:** establish the report grain, aggregate transactions independently to Account grain before joining holdings, or use a model/query path that avoids cross-multiplying independent relationships. Test the total against the independent transaction total.

### Scenario 5 — Chasm trap from optional Branch

**Problem:** Some Accounts have no designated Branch. An inner join to Branch silently drops them.

**Correction:** clarify whether the report requires all accounts or only branch-assigned accounts; use join semantics that match the question and validate row counts. Do not turn an optional relationship into a mandatory one merely to simplify a report.

## 9. Expected outputs and deliverables

- [ ] Entity inventory with definitions and include/exclude rationale.
- [ ] Relationship inventory with both-direction cardinality and optionality.
- [ ] ER diagram consistent with the inventories and rules register.
- [ ] Candidate-key, primary-key, natural-key, surrogate-key, and foreign-key analysis.
- [ ] Explicit Customer–Account–AccountHolding model with role and valid-time attributes.
- [ ] Supertype/subtype decision for Party, Person, Organisation, and role relationships.
- [ ] Referential-integrity and deletion/change policy for each important reference.
- [ ] Rules register linking business rule → model element → constraint category → enforcement mechanism → test evidence.
- [ ] At least ten intermediate test cases, with expected pass/reject outcomes and explanations.
- [ ] Twenty industry validation cases, with expected outcomes and rule IDs.
- [ ] Written resolution of the joint-account/guardian, legal-name history, and recursive-product-bundle scenarios.
- [ ] An ambiguity log and anomaly-review record.
- [ ] Answers to Module 2 practice questions, corrected after review.

## 10. Common mistakes and misconceptions

1. **Treating every noun as an entity.** Model only what the business needs to identify and manage; a noun may be an attribute or an out-of-scope concept.
2. **Treating an entity as a single row in a screen.** Screens and reports are views, not authoritative entity definitions.
3. **Leaving cardinality implicit.** Every relationship must be read and documented in both directions.
4. **Confusing optionality with “many.”** `0..*` is optional and many; `1..*` is mandatory and many.
5. **Using repeating columns for multiple relationships.** `CustomerID1`, `CustomerID2`, and `CustomerID3` are a repeating-group design, not a scalable joint-account model.
6. **Storing relationship facts on the wrong entity.** Holder role belongs to AccountHolding, not to Party in general.
7. **Using mutable attributes as identifiers.** Names, phone numbers, and addresses can change or be shared.
8. **Assuming a surrogate key solves identity resolution.** It distinguishes modeled instances but does not prove two source records represent the same real-world Party.
9. **Treating guardian as a Party subtype.** Guardianship is generally a role/relationship; one Party can act as customer, guardian, or holder.
10. **Ignoring temporal boundaries.** Without a declared interval convention, adjacent intervals may appear to overlap or leave gaps.
11. **Assuming foreign keys enforce every business rule.** They cannot enforce all temporal, cross-row, conditional, or recursive rules.
12. **Cascading deletes without considering history.** Audit and transaction references may need retention.
13. **Assuming every circular relationship is wrong.** Some cycles represent valid recursive relationships; the issue is whether lifecycle, termination, and validation semantics are defined.
14. **Ignoring fan traps.** Joining two independent one-to-many branches can multiply measures.
15. **Ignoring chasm traps.** An inner join through an optional relationship can silently remove valid entities.
16. **Calling a rule enforced because it is written down.** A rule register is documentation; enforcement and monitoring must be implemented.
17. **Adding Address or Contact as an entity without a requirement.** Use separate entities when identity, multiplicity, reuse, lifecycle, or history justify them; otherwise a value structure may suffice.
18. **Assuming a diagram is sufficient evidence.** Definitions, cardinality, valid/invalid tests, assumptions, and enforcement notes are part of the model package.

## 11. Mastery criteria

You have mastered this topic when you can:

- Identify entities, instances, attributes, identifiers, and relationships from a business description.
- Explain why each candidate entity is included or excluded.
- State min/max cardinality and optionality in both directions for every relationship.
- Model a joint account without repeating columns, using AccountHolding with relationship-specific attributes.
- Justify identifier choices using uniqueness, stability, cross-source consistency, mutability, privacy, and lifecycle.
- Distinguish candidate keys, primary keys, natural keys, surrogate keys, and foreign keys.
- Define a sensible referential-integrity policy for deletion and key change.
- Explain when Party supertype/subtype modeling is useful and when roles should be modeled as relationships instead.
- Model time-dependent relationships with a documented interval convention.
- Distinguish structural/declarative constraints from conditional, temporal, cross-row, and recursive rules needing procedural enforcement.
- Identify repeating groups, missing entities, circular dependency problems, fan traps, and chasm traps.
- Complete all test cases with outcomes that agree with the stated assumptions and rules.
- Maintain an ambiguity log rather than silently choosing business semantics.
- Explain why the model documents rules but does not automatically enforce every rule.

## 12. Completion gate

Do not mark Module 2 complete simply because the ER diagram looks correct. Complete each gate with evidence.

- [ ] **ER model reviewed:** every relationship has correct minimum and maximum cardinality and optionality in both directions.
- [ ] **Entity decisions justified:** each included candidate has business meaning and each excluded candidate has a stated reason or open question.
- [ ] **Keys justified:** candidate keys are minimal and unique under stated assumptions; primary-key selection is explained; natural/surrogate trade-offs and foreign-key references are documented.
- [ ] **Associative entity correct:** Customer/Party–Account many-to-many is resolved through AccountHolding, and role/validity attributes are attached to the relationship.
- [ ] **Referential integrity covered:** deletion, retirement, and key-change behavior are defined for important references.
- [ ] **Temporal semantics explicit:** valid-from/valid-to interval convention and overlap/gap rules are documented.
- [ ] **Enforcement distinction explicit:** each rule is classified as structural/declarative or procedural/conditional/temporal/recursive, with an enforcement candidate and test evidence.
- [ ] **Test set passes:** at least ten intermediate cases and twenty industry validation cases have expected outcomes; invalid cases are rejected, held, or escalated by the actual enforcement mechanism or documented rules process.
- [ ] **Scenarios resolved:** joint account with a minor and guardian, historical legal-name change, and recursively nested product bundles are modeled and reviewed.
- [ ] **Anomalies reviewed:** repeating groups, missing entities, circular dependencies, fan traps, and chasm traps are addressed or documented as not applicable with reasons.
- [ ] **Ambiguity log complete:** unresolved questions have an owner and a next decision; assumptions are not presented as approved policy.
- [ ] **Practice questions answered and corrected:** errors are reviewed and the corrected answers agree with the model.
- [ ] **Independent review:** a reviewer can derive the same valid/invalid outcomes from the model and rules without relying on undocumented explanations.

### Lesson summary

Entity-relationship modeling is the discipline of making identity, relationships, valid states, and constraints explicit. Start with business meaning, justify each entity, and describe every relationship in both directions using minimum and maximum cardinality. Use identifiers that remain defensible through change, associative entities for relationships with their own facts, and temporal structures when history matters. Finally, distinguish what the model states from what a database or application actually enforces—and prove the result with valid and invalid test cases.
