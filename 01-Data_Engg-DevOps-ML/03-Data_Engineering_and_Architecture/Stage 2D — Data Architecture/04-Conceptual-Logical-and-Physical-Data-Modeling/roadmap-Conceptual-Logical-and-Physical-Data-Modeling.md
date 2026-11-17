# Roadmap — Module 2D.4: Conceptual, Logical and Physical Data Modeling

This is the learning roadmap for the fourth module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Module 2D.1 gave you the role and principles. Module 2D.2 gave you requirements,
constraints and decision records. Module 2D.3 gave you the organising patterns.
This module gives those decisions **structure**: the entities, relationships,
rules, grain, history and change-handling that turn a business domain into data
that can be stored, integrated, governed and analysed correctly.

> **Repository note.** The eight topic files, `practice-questions.md`, the
> module and project READMEs, and
> `Projects/04-enterprise-conceptual-and-logical-data-model.md` currently exist
> but are empty, as are the Stage 2D overview files. This roadmap is therefore
> the first written statement of the module's scope. It defines the learning
> sequence for each topic file; it does not claim that any topic file already
> contains this material. Where a topic file, once written, covers fewer or
> different normal forms, dimensional structures or Data Vault components than
> described here, the topic file's scope governs and this roadmap should be
> updated.
>
> **Directory name.** The prompt that requested this roadmap referred to
> `STAGE 2D - DATA ARCHITECURE/`. The actual directory is
> `Stage 2D — Data Architecture/`, and the actual name is preserved.
>
> **Illustrative content.** Every entity, rule, attribute and number in this
> roadmap is an **illustrative assumption** used to teach a method. None is a
> real organisational fact. The module is vendor-neutral and is **not** a
> database administration course: physical examples are kept at the level of
> concepts, and no product-specific syntax is required.

---

## 1. Module overview

### 1.1 What data modeling is

A **data model** is a structured, explicit representation of the things an
organisation cares about, the facts recorded about them, how they relate, and
the rules that constrain them. It exists at three levels of abstraction.

| Level | Question it answers | Audience | Typical content | Technology dependence |
| --- | --- | --- | --- | --- |
| **Conceptual** | What business things matter, and how do they relate? | Business and architects | Core entities/concepts, relationships, business definitions, scope | None |
| **Logical** | What data must we hold, precisely, and under which rules? | Architects, analysts, designers | Entities, attributes, identifiers, cardinality, optionality, constraints, normalised structure | Largely none (paradigm-aware, product-neutral) |
| **Physical** | How is it stored and accessed in a chosen technology? | Engineers, DBAs | Tables/files, data types, indexes, partitioning, storage formats, naming per platform | Specific |

### 1.2 Why modeling is a core architect responsibility

- **Consistency:** shared definitions stop "customer" meaning five things.
- **Integrity:** keys and constraints keep data valid by design.
- **Interoperability:** a common model lets systems and domains exchange data.
- **Analytics:** correct grain and relationships make answers trustworthy.
- **Governance:** definitions, ownership and lineage hang off the model.
- **Maintainability:** well-structured models absorb change cheaply.

### 1.3 How models connect requirements to implementation

```text
Business requirement → business concepts and rules → conceptual model
→ logical model (precise, normalised, constrained)
→ physical model (platform-specific) → implemented schema and pipelines
```

Traceability should run both ways: every model element should trace to a
requirement or business rule, and every rule should trace to where it is
represented.

### 1.4 Three different achievements

| Activity | You have achieved it when… |
| --- | --- |
| **Understanding a business domain** | You can state its concepts, rules and vocabulary, and a domain expert agrees |
| **Defining a logical data model** | The model captures those rules precisely, with identifiers, relationships, cardinality, optionality and constraints, independent of technology |
| **Implementing a physical schema** | The logical model is realised on a platform with types, indexes, partitioning and performance choices justified by workload |

Skipping the first produces a precise model of the wrong thing; skipping the
second produces a schema that encodes accidents of one platform.

### 1.5 A diagram is not a model

A **diagram** is a picture. A **model** is a set of definitions and rules that
the picture illustrates. A model is correct when it:

- represents the business rules truthfully (including edge cases),
- states cardinality, optionality and identifiers explicitly,
- uses terms with agreed definitions,
- can reject invalid combinations and express valid ones,
- supports its intended use (transactions, analytics, history, exchange), and
- is traceable and reviewable.

A tidy diagram with ambiguous names, unstated rules and an unstated grain is
not a model; it is decoration.

### 1.6 How this module builds on earlier Stage 2D modules

| From | Used here |
| --- | --- |
| 2D.1 Topic 3: capabilities, domains, ownership | Domain boundaries and the owner of each model |
| 2D.1 Topic 4: principles, quality attributes | Modeling principles (for example single source of definition) and quality targets |
| 2D.1 Topic 5: governance | Review and approval of models |
| 2D.2 Topics 1–2: stakeholders, requirements | The source of business rules and model scope |
| 2D.2 Topic 3: volume, variety, growth | Informs physical choices and denormalisation decisions |
| 2D.2 Topic 5: constraints, assumptions | Open questions and assumptions recorded with the model |
| 2D.2 Topic 7: ADRs | Recording significant modeling decisions |
| 2D.3 Topic 1, 4: domain-oriented, data mesh | Model boundaries and data product schemas |
| 2D.3 Topic 2: warehouse, lake, lakehouse | Which model style suits which layer |
| 2D.3 Topic 6: event-driven and data sharing | Event contracts and schema compatibility |

### 1.7 How it supports later modules

| Later module | What it takes from this one |
| --- | --- |
| 2D.5 Database and storage architecture | The logical model that physical storage must realise |
| 2D.6 Data integration and interoperability | Canonical definitions, keys, and schema compatibility rules |
| 2D.7 Enterprise data platform and lakehouse | Layer-appropriate models (raw history, conformed, consumption) |
| 2D.10 Governance, security, privacy | Classification and ownership attached to attributes |
| 2D.11 Metadata, lineage, quality, master data | Business glossary, data dictionary, keys and identifiers |
| 2D.14 Data access and serving | Dimensional and semantic structures for consumption |
| 2D.15 Documentation and reviews | Model reviews and standards |

### 1.8 Expected capabilities after completion

You will be able to:

- Place any modeling decision at the correct abstraction level and justify it.
- Build and validate an entity-relationship model with explicit cardinality,
  optionality, identifiers and constraints.
- Normalise a relational design, spot anomalies, and justify any denormalisation.
- State the grain of a fact table first and design a dimensional model that
  answers defined business questions.
- Choose and explain a historical modeling approach, including where Data
  Vault concepts help and where they do not.
- Model business events and domain boundaries and distinguish events from state.
- Classify schema changes by compatibility and plan safe rollout.
- Review a model against consistent criteria and produce a data dictionary.
- Deliver a validated enterprise conceptual and logical model with traceability.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

| Prerequisite | Why it matters here |
| --- | --- |
| Module 2D.1 completed (or its gates passed) | You need the vocabulary of capabilities, domains, ownership and principles; model scope follows domain boundaries |
| Module 2D.2 completed (or its gates passed) | Models are built from stakeholder requirements, business rules and recorded assumptions; ADRs capture modeling decisions |
| Module 2D.3 completed (or its gates passed) | Model style depends on the chosen operating model and storage pattern; data product and event concepts reappear here |
| Stage 2 relational and SQL fundamentals (tables, keys, joins, basic DDL reading) | You must be able to read how a logical model would become tables; **advanced database knowledge is not assumed** |
| Ability to draw and read simple box-and-line diagrams | Models are communicated visually and textually |

### 2.2 Helpful prior knowledge

- Experience of a real system's database or data warehouse schema.
- Familiarity with analytical reporting questions.
- Awareness of columnar file formats and table formats (Stage 2 and 2C).
- Awareness of message and event concepts (2D.3 Topic 6).

### 2.3 Concepts you will learn during this module

- Entity-relationship notation and cardinality/optionality conventions.
- Functional dependencies and normal forms.
- Fact table grain, additivity and dimension types.
- Hub, link and satellite concepts for historical modeling.
- Bounded context and ubiquitous language.
- Compatibility classes of schema change.
- Data dictionary and naming-standard practice.

No modeling tool, specific database product or certification is required.

### 2.4 Using prior knowledge when modeling

Before drawing anything, answer, in order:

1. **Whose problem?** stakeholders and consumers (2D.2 Topic 1).
2. **Which domain and boundary?** (2D.1 Topic 3, 2D.3 Topic 1/4).
3. **Which rules?** requirements and constraints (2D.2 Topics 2, 5).
4. **Which use?** transaction, analytics, history, exchange (2D.3 Topic 2).
5. **Which level?** conceptual, logical or physical.

Only then model.

---

## 3. Learning progression

### 3.1 The four levels

| Level | Concepts to study | Recommended sequence | Practical exercises | Questions to answer | Expected outputs | Evidence of mastery | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1 — Beginner** | Modeling terms; abstraction levels; entities, attributes, relationships; reading simple diagrams | Level definitions → entities/attributes → relationships → read a diagram | Label examples by level; identify entities in a description; read a given diagram | What is this thing? What do we know about it? How does it relate? At which level am I? | Glossary; labelled examples; a small entity list | Correct classification and interpretation without notes | 90% of classification items correct; can explain each level to a peer |
| **2 — Intermediate** | Create coherent models; attributes and constraints; normalisation; dimensional design; business-rule documentation | Conceptual → logical → normalise → dimensional → document rules | Model a domain; normalise a flawed schema; design a star from business questions | Is the grain explicit? Is each rule represented? Is there redundancy? | Conceptual and logical models; normalised schema; dimensional model; rules register | A reviewer can read the model and recover the rules | A model that passes scenario tests with no unrepresented rule |
| **3 — Advanced** | Alternative approaches; history; events and domains; schema evolution; justified decisions | Compare approaches → history → domain/event → evolution → decide | Choose between relational/dimensional/vault for a case; classify schema changes; map bounded contexts | Why this approach? What does it cost? What breaks when it changes? | Option analysis; evolution plan; domain/event model | A defended choice with trade-offs and an impact analysis | Choice and plan survive reviewer challenge |
| **4 — Industry application** | Enterprise models; traceability; standards; defensible deliverable | Requirements → models → dictionary → review → package | The project (Section 7) | Can another architect audit and reuse this? | Validated conceptual and logical model package | Independent review finds no unflagged defect | Project completion gate (Section 7.7) met |

### 3.2 Emphasis

The module rewards **correctness, semantic accuracy, architectural reasoning
and traceability**. It does not reward decoration, large diagrams or memorising
normal-form definitions without being able to apply them.

### 3.3 The modeling loop (use for every topic)

```text
Understand the business → State the rules in words → Draw the structure →
Test with real examples (valid and invalid) → Find the ambiguities →
Record assumptions → Review → Revise
```

1. **Understand the business:** concepts, vocabulary, processes.
2. **State the rules in words** before drawing ("An account has exactly one
   primary holder.").
3. **Draw the structure** at the right level.
4. **Test with examples:** at least three valid and three invalid
   data combinations, including edge cases.
5. **Find ambiguities** and ask the domain expert.
6. **Record assumptions and open questions.**
7. **Review** against criteria (Topic 8).
8. **Revise.**

### 3.4 Suggested schedule

About **5 weeks at 6–8 hours per week.**

| Week | Work |
| --- | --- |
| 1 | Topic 1 (levels) · Topic 2 (entities, relationships, cardinality, constraints) |
| 2 | Topic 3 (normalisation and relational modeling) |
| 3 | Topic 4 (dimensional modeling) · Topic 5 (Data Vault and historical modeling) |
| 4 | Topic 6 (event modeling and DDD) · Topic 7 (schema evolution) |
| 5 | Topic 8 (review, naming, dictionaries) · practice questions · project |

Keep a `module-2d4-notes.md` outside the repository's topic files: a rules
register, worked examples with valid and invalid cases, and open questions.

---

## 4. Detailed learning roadmap for each topic file

Each module uses the same twelve sub-headings. Levels are cumulative. Examples
use the **illustrative** domain of *Northbridge Bank* (Section 7.2).

---

### Module 1 — [Conceptual, logical and physical models](01-conceptual-logical-and-physical-models.md)

#### 1.1 Learning objectives

- Explain the purpose of data modeling.
- Distinguish conceptual, logical and physical models by abstraction, detail,
  audience and use.
- Explain how models connect to business requirements and architecture
  decisions.
- Define model boundaries, scope, assumptions and consumers.
- Maintain traceability across levels.
- Recognise common modeling artefacts and their purposes.

#### 1.2 Why the topic matters in real-world Data Architecture

Most modeling disasters are level confusion: business concepts mixed with
column types, platform tricks baked into "logical" models, or physical schemas
with no business meaning. Separating levels allows each audience to
validate the right things and allows the same logical model to be realised on
different platforms.

#### 1.3 Prerequisite knowledge

2D.1 Topic 1 (architecture role); 2D.2 Topics 1–2 (requirements); basic SQL.

#### 1.4 Beginner-level learning sequence

1. **Define data modeling** and why organisations need shared models.
2. **Learn the three levels** using Section 1.1; memorise the question each
   answers.
3. **Learn what belongs where:**

   | Item | Conceptual | Logical | Physical |
   | --- | --- | --- | --- |
   | "Customer" and "Account" exist and relate | Yes | Yes | Realised |
   | Customer identifier is unique and mandatory | Sometimes noted | Yes | Enforced by constraint/index |
   | Data type VARCHAR(100), index, partition key | No | No | Yes |
   | Optional/mandatory, cardinality | Roughly | Precisely | Enforced |
   | Business definition | Yes | Yes | Referenced |

4. **Read a simple three-level example** of the same domain.
5. **Questions to answer:** Which level would a business executive review?
   Why does "data type" not belong in a conceptual model?
6. **Exercise:** Classify twenty statements by level and justify.

**Ability to demonstrate:** classify statements and artefacts by level and
explain the difference to a non-specialist.

#### 1.5 Intermediate-level learning sequence

1. **Transform a conceptual model into a logical model.** Starting from a
   small conceptual model (Customer–Account–Transaction), add: attributes,
   identifiers, cardinality, optionality, relationship resolution (for example
   many-to-many into associative entities), and constraints.
2. **List the decisions still needed before a physical model:** target
   platform, data types, key strategy (natural versus surrogate), indexing,
   partitioning, storage format, performance denormalisation, security
   implementation.
3. **Define scope and boundaries:** what the model includes and excludes;
   assumptions; intended consumers; which domain owns it.
4. **Maintain traceability:** requirement ID → concept → logical element →
   (later) physical object.
5. **Learn the artefacts:** glossary, entity inventory, rules register,
   conceptual diagram, logical diagram, data dictionary, mapping tables.
6. **Questions to answer:** What new information did the logical model require
   from the business? What did you defer to the physical level, and why?
7. **Exercise:** Take a one-page business description, produce a conceptual
   model, then a logical model, with a list of decisions deferred.

**Ability to demonstrate:** produce a consistent conceptual → logical pair and
a list of decisions deferred to the physical level.

#### 1.6 Advanced-level learning sequence

1. **Evaluate modeling choices** against business semantics, implementation
   constraints, integrity, maintainability and intended workloads (transactional
   versus analytical versus historical versus exchange).
2. **Know when to push a decision up or down:** a constraint belongs in the
   logical model if it is a business rule; a physical constraint exists to
   enforce or optimise it.
3. **Handle multiple physical realisations** of one logical model (relational
   tables, document structures, columnar files) and what is preserved or lost.
4. **Identify level violations in review:** logical model with platform types;
   conceptual model with join tables; physical model with unexplained columns.
5. **Link to architecture decisions:** where a modeling choice is architecturally
   significant (for example single customer identifier), record it as an ADR
   (2D.2 Topic 7).
6. **Questions to answer:** Which logical decisions would you refuse to change
   even if a platform made them awkward? Which would you adapt?
7. **Exercise:** Review a supposed "logical" model containing ten level
   violations; list them and reassign each to the correct level.

**Ability to demonstrate:** explain why each decision belongs at a particular
level, and how it would be realised or adapted physically.

#### 1.7 Industry-application exercises

- Produce a coherent conceptual and logical model for the Northbridge
  "customer and account" domain and state what must be resolved before physical
  implementation.
- Draw the traceability table from requirements to model elements.
- Record one architecturally significant modeling decision as a short ADR.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* An engineer shares a schema and calls it the "conceptual model".
   What do you ask, and what would you produce?
2. *Scenario:* A cloud platform lacks enforced foreign keys. Does the logical
   relationship disappear? Where is the rule enforced?
3. *Scenario:* The business redefines "active customer". Which levels change?

#### 1.9 Expected outputs and deliverables

- Level classification exercise with justification.
- Conceptual and logical model pair for a small domain.
- List of decisions deferred to the physical level.
- Answers to Topic 1 practice questions.

#### 1.10 Common mistakes and misconceptions

- Treating conceptual, logical and physical as sizes of the same diagram.
- Putting data types and indexes in conceptual models.
- Assuming the physical schema *is* the logical model.
- Omitting scope, assumptions and consumers.
- No traceability to requirements.

#### 1.11 Mastery criteria

- Distinguishes the levels by question, audience and content.
- Produces a consistent conceptual → logical transformation.
- Explains why each decision belongs at its level.

#### 1.12 Completion gate

- [ ] Level classification exercise correct to 90% or better.
- [ ] Model pair reviewed; no level violations found.
- [ ] Deferred-decision list complete and justified.
- [ ] Topic 1 practice questions answered and corrected.

---

### Module 2 — [Entities, relationships, cardinality and constraints](02-entities-relationships-cardinality-and-constraints.md)

#### 2.1 Learning objectives

- Define entities, attributes and identifiers with business meaning.
- Model one-to-one, one-to-many and many-to-many relationships.
- State cardinality and optionality precisely.
- Choose primary and candidate keys; explain referential integrity.
- Represent business rules and resolve ambiguous relationships.
- Use associative entities.
- Validate a model against real scenarios.

#### 2.2 Why the topic matters in real-world Data Architecture

This is the structural foundation. An error in a relationship or identifier
propagates into every table, interface and report built on it, and is expensive
to correct after data has been loaded.

#### 2.3 Prerequisite knowledge

Module 1 here; 2D.1 Topic 3 (business domains, ownership).

#### 2.4 Beginner-level learning sequence

1. **Define terms:** entity (a thing the business tracks), instance,
   attribute, identifier, relationship.
2. **Identify entities in text:** nouns the business needs to track, as opposed
   to attributes of other things.
3. **Identify attributes** and the one or more that identify an instance.
4. **Learn basic relationship wording:** "A customer *holds* zero or more
   accounts. An account *is held by* one or more customers."
5. **Read basic notation** (crow's-foot or equivalent) for the three
   relationship types.
6. **Questions to answer:** Is "address" an entity or an attribute? What
   uniquely identifies a transaction?
7. **Exercise:** From a short description of a branch network, list entities,
   attributes, identifiers and relationships.

**Ability to demonstrate:** identify entities, attributes, identifiers and
simple relationships in a description.

#### 2.5 Intermediate-level learning sequence

1. **State cardinality and optionality in both directions.** Example:

   | Statement | Minimum | Maximum |
   | --- | --- | --- |
   | A customer holds … accounts | 0 | many |
   | An account is held by … customers | 1 | many |
   | A transaction posts to … account | 1 | 1 |

2. **Resolve many-to-many** with an associative entity that holds the
   relationship's own attributes (for example `AccountHolding` with role,
   start date, end date).
3. **Choose keys:** candidate keys; primary key; natural versus surrogate at a
   conceptual/logical level (surrogate choice is finalised physically but its
   need is a logical question about stability and uniqueness).
4. **Define referential integrity:** a reference must point to an existing
   instance; decide the rule for deletion or change (restrict, cascade,
   nullify) as a business rule.
5. **Document business rules** in plain language and link each to the model
   element that represents it.
6. **Test with edge cases:** optional relationships, an entity playing
   multiple roles (a person who is both customer and guarantor), historical
   relationships (a holder who has left), invalid combinations (a transaction
   with no account).
7. **Questions to answer:** Which rule is represented by structure, and which
   cannot be and must be stated separately?
8. **Exercise:** Model the customer–account–holding–transaction structure with
   explicit cardinality and optionality and write ten test cases (five valid,
   five invalid).

**Ability to demonstrate:** a model whose test cases are accepted or rejected
as the business rules require.

#### 2.6 Advanced-level learning sequence

1. **Resolve ambiguous business rules** by listing the possible
   interpretations, asking the domain expert, and recording the answer.
   *Illustrative:* "A customer has one address" — current only? Several types?
   Over time?
2. **Identify anomalies:** missing identifiers, relationships that hide a
   missing entity, repeating groups, circular dependencies, fan traps and chasm
   traps (joins that silently multiply or lose rows).
3. **Justify identifiers:** stability over time, uniqueness across sources,
   meaning (business key) versus meaninglessness (surrogate), privacy of
   identifiers.
4. **Model supertype/subtype** relationships (for example Party → Person /
   Organisation) when behaviour or attributes differ, and decide when not to.
5. **Model time-dependent relationships** (valid-from/valid-to) and when a
   relationship deserves its own entity.
6. **Constraints beyond structure:** uniqueness across attributes, conditional
   mandatory attributes, cross-entity rules, state-transition rules; where each
   can be enforced.
7. **Questions to answer:** What makes this identifier stable? Which rule can
   the data model not enforce?
8. **Exercise:** Take a model with four deliberately planted ambiguities and
   anomalies; list them, resolve them with assumptions, and re-draw.

**Ability to demonstrate:** identify and resolve ambiguities and anomalies and
defend identifier choices.

#### 2.7 Industry-application exercises

- Build and validate an ER model for the Northbridge customer, account, product
  and transaction domain with a rules register.
- Write a validation set of twenty data examples (valid/invalid) and show how
  the model treats each.
- Document which rules are structural and which require procedural
  enforcement.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* A joint account has two holders, one of whom is a minor with a
   guardian. How do you model parties and roles?
2. *Scenario:* A customer changes legal name; transactions must keep the name
   in force at the time. What does this imply?
3. *Scenario:* A product can be sold in bundles; bundles can contain bundles.
   What anomaly arises and how do you handle it?

#### 2.9 Expected outputs and deliverables

- Entity inventory and relationship inventory.
- ER model with cardinality, optionality and keys.
- Business rules register.
- Test-case set (valid and invalid).
- Answers to Topic 2 practice questions.

#### 2.10 Common mistakes and misconceptions

- Modeling screens or reports instead of the business.
- Leaving cardinality/optionality implicit.
- Resolving many-to-many by duplicating columns instead of an associative
  entity.
- Choosing mutable attributes as identifiers.
- Treating relationships as one-way.
- Not testing with invalid cases.

#### 2.11 Mastery criteria

- States cardinality and optionality in both directions correctly.
- Uses associative entities and supertype/subtype appropriately.
- Justifies identifiers and handles edge cases.
- Records unresolved ambiguities.

#### 2.12 Completion gate

- [ ] ER model reviewed; every relationship has both-direction cardinality and
      optionality.
- [ ] Test set passes; invalid cases are rejected by the model or the rules
      register.
- [ ] Ambiguity log complete.
- [ ] Topic 2 practice questions answered and corrected.

---

### Module 3 — [Normalization and relational modeling](03-normalization-and-relational-modeling.md)

#### 3.1 Learning objectives

- Express a logical model in relational terms (relations, attributes, keys).
- Explain redundancy and insertion, update and deletion anomalies.
- Identify functional dependencies.
- Apply the normal forms covered by the topic file (illustrated here through
  1NF, 2NF, 3NF and BCNF).
- Decompose relations without losing information or dependencies.
- Evaluate denormalisation trade-offs and recognise unnecessary duplication.

#### 3.2 Why the topic matters in real-world Data Architecture

Normalisation is the discipline that makes each fact stored once, so changes
are made once and the data cannot contradict itself. It is the default for
transactional models and the reference point from which deliberate
denormalisation is judged.

#### 3.3 Prerequisite knowledge

Module 2 here; basic SQL (selecting from and joining tables).

> **Scope note.** This roadmap illustrates 1NF–BCNF as the commonly taught
> sequence. If the topic file covers a different set (for example stops at 3NF
> or includes 4NF/5NF), follow the topic file.

#### 3.4 Beginner-level learning sequence

1. **Learn relational terms:** relation/table, tuple/row, attribute/column,
   domain, primary key, foreign key.
2. **Learn redundancy** by example. A single table:

   | order_id | customer_id | customer_name | customer_city | product | qty |
   | --- | --- | --- | --- | --- | --- |
   | 1 | C1 | Asha Rao | Pune | Loan A | 1 |
   | 2 | C1 | Asha Rao | Pune | Card B | 1 |
   | 3 | C2 | Ben Cole | Leeds | Loan A | 2 |

   (Illustrative names.) Customer name and city repeat.
3. **Learn the three anomalies:** *update* (change city in one row only →
   contradiction), *insertion* (cannot record a new customer with no order),
   *deletion* (deleting the last order loses the customer).
4. **Questions to answer:** Which columns depend on which? Why does repetition
   create risk?
5. **Exercise:** Identify the redundancy and the three anomalies in a supplied
   table.

**Ability to demonstrate:** recognise redundancy and name the anomaly each
causes.

#### 3.5 Intermediate-level learning sequence

1. **Functional dependency:** A → B means each value of A determines exactly
   one value of B. Write dependencies for the table above:
   `order_id → customer_id, product, qty`; `customer_id → customer_name, customer_city`.
2. **Apply the normal forms in order, with a worked example:**

   | Form | Rule (informal) | Typical violation | Fix |
   | --- | --- | --- | --- |
   | 1NF | Atomic values, no repeating groups | `products = "Loan A, Card B"` in one cell | One row per fact |
   | 2NF | 1NF + no non-key attribute depends on part of a composite key | `(order_id, product)` key with `product_description` depending on `product` only | Separate `product` relation |
   | 3NF | 2NF + no non-key attribute depends on another non-key attribute | `customer_name` depends on `customer_id`, not on `order_id` | Separate `customer` relation |
   | BCNF | Every determinant is a candidate key | A non-key determinant such as `branch_code → branch_manager` in a table keyed otherwise | Decompose on the determinant |

3. **Worked decomposition** of the table above into `Customer(customer_id PK,
   name, city)`, `Product(product_id PK, …)`, `Order(order_id PK,
   customer_id FK)` and `OrderLine(order_id, product_id, qty)`; show that a join
   reconstructs the original facts.
4. **Verify the decomposition:** it must be *lossless* (join recovers the
   original) and, ideally, *dependency-preserving*.
5. **Define referential integrity** for each foreign key.
6. **Questions to answer:** Which anomaly disappears after each step? What is
   the key of each new relation?
7. **Exercise:** Normalise three supplied tables to 3NF, showing dependencies,
   violations, decomposition and the lossless-join check.

**Ability to demonstrate:** normalise to the specified form with documented
dependencies and a lossless-join check.

#### 3.6 Advanced-level learning sequence

1. **Evaluate decomposition choices:** over-decomposition (too many joins for
   little benefit) versus under-decomposition (anomaly risk); when a
   dependency-preserving decomposition is impossible in BCNF.
2. **Integrity implications:** what is enforced by keys and foreign keys, what
   requires additional constraints; effect of nullable foreign keys.
3. **Query requirements:** read versus write mix, join cost, concurrency,
   reporting needs.
4. **Justified denormalisation:** pre-joined reporting tables, derived or
   cached values, repeated attributes for performance. For each, state: the
   anomaly risk introduced, how consistency is maintained (process or
   constraint), and the measured benefit.
5. **Distinguish logical denormalisation (usually a smell) from physical
   denormalisation (a deliberate, documented optimisation).**
6. **Recognise unnecessary duplication or complexity:** copy-and-paste
   attributes, "flag" columns standing in for relationships, generic key-value
   tables that hide structure.
7. **Questions to answer:** What would you measure before denormalising? Who
   owns the consistency of the duplicate?
8. **Exercise:** Evaluate a performance request to denormalise a customer
   dimension into transactions; produce a recommendation with risks and
   consistency mechanism.

**Ability to demonstrate:** justify a decomposition or denormalisation with
integrity, workload and maintenance reasoning.

#### 3.7 Industry-application exercises

- Review an imperfect relational model of Northbridge accounts and payments,
  list its problems (with the dependency or anomaly behind each), propose a
  revised design and explain the trade-offs.
- Produce the dependency list and decomposition proof for the revised design.
- Identify two places where you would knowingly denormalise physically, and
  document why.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* A reporting table stores customer segment on every transaction.
   When the segment changes, what must happen and what history do you need?
2. *Scenario:* A "generic attributes" table stores any attribute as
   name/value pairs. What integrity is lost?
3. *Scenario:* A team keeps a calculated balance column. Who guarantees it
   equals the sum of transactions?

#### 3.9 Expected outputs and deliverables

- Dependency lists and normalisation worked examples.
- Reviewed and corrected relational model with decomposition proof.
- Denormalisation decision record.
- Answers to Topic 3 practice questions.

#### 3.10 Common mistakes and misconceptions

- Memorising normal forms without identifying dependencies.
- Equating more tables with better design.
- Denormalising by default "for performance" without measurement.
- Ignoring that decomposition must be lossless.
- Treating nullable foreign keys and optional relationships as the same thing
  without thought.

#### 3.11 Mastery criteria

- Identifies functional dependencies and anomalies correctly.
- Normalises to the stated form with a lossless-join check.
- Justifies any denormalisation with evidence and a consistency mechanism.

#### 3.12 Completion gate

- [ ] Three tables normalised with dependencies and proofs.
- [ ] Review exercise lists problems with the dependency or anomaly behind each.
- [ ] Denormalisation record states risk, consistency mechanism and evidence.
- [ ] Topic 3 practice questions answered and corrected.

---

### Module 4 — [Dimensional modeling: facts, dimensions and grain](04-dimensional-modeling-facts-dimensions-and-grain.md)

#### 4.1 Learning objectives

- Explain the purpose of dimensional modeling.
- Define facts, dimensions, measures and dimensional attributes.
- State the grain of a fact table explicitly before anything else.
- Distinguish additive, semi-additive and non-additive measures.
- Design star schemas, conformed dimensions and handle slowly changing
  dimensions as covered by the topic file.
- Understand fact table types (transaction, periodic snapshot, accumulating
  snapshot) as covered.
- Describe the consequences of incorrect grain or joins.

#### 4.2 Why the topic matters in real-world Data Architecture

Analytical users ask business questions, not normalised-schema questions. A
dimensional model makes those questions easy and fast to answer, provided the
grain is explicit. A wrong grain produces wrong numbers silently.

#### 4.3 Prerequisite knowledge

Modules 2–3 here; 2D.3 Topic 2 (warehouse, lakehouse layers); basic aggregation
in SQL.

#### 4.4 Beginner-level learning sequence

1. **Learn the purpose:** a model shaped for analysis: events and amounts
   (facts) described by context (dimensions).
2. **Define terms:** *fact* (measurement of a business event), *measure*
   (numeric value), *dimension* (descriptive context: who, what, where, when),
   *grain* (what one row of the fact table represents).
3. **Use a simple process:** a card purchase.
   - Grain: **one row per card transaction.**
   - Measures: transaction amount, fee.
   - Dimensions: date, customer, card, merchant, channel.
4. **State grain before measures and dimensions** every time.
5. **Questions to answer:** What is one row? Which questions does this grain
   permit and which does it prevent?
6. **Exercise:** For a loan-repayment process, write the grain sentence, then
   list measures and dimensions.

**Ability to demonstrate:** produce a grain statement, measures and dimensions
for a simple process.

#### 4.5 Intermediate-level learning sequence

1. **Follow a design sequence:** (1) choose the business process, (2) declare
   the grain, (3) identify the dimensions, (4) identify the facts/measures.
2. **Collect the business questions** the model must answer (for example
   "monthly card spend by merchant category and customer segment") and check the
   design answers each.
3. **Design dimension tables:** surrogate key, business key, descriptive
   attributes, hierarchies (kept in the dimension), meaningful values rather
   than codes.
4. **Design the fact table:** foreign keys to dimensions, measures, degenerate
   dimensions (identifiers with no table of their own, such as transaction
   number), and no descriptive text.
5. **Learn additivity:**

   | Measure type | Example | Can sum across |
   | --- | --- | --- |
   | Additive | Transaction amount | All dimensions |
   | Semi-additive | Account balance | Accounts, not time |
   | Non-additive | Interest rate, ratio | None (derive from additive parts) |

6. **Introduce slowly changing dimensions (as covered by the topic):**
   overwrite (type 1), add a new row with validity dates (type 2), keep prior
   value in a column (type 3); state which fits which requirement.
7. **Learn fact table types:** transaction (one row per event), periodic
   snapshot (one row per period per entity), accumulating snapshot (one row per
   process instance updated through milestones).
8. **Questions to answer:** What happens to last year's reports if the
   customer's segment changes and the dimension is type 1? type 2?
9. **Exercise:** Design a star schema for card transactions that answers six
   supplied business questions, with grain, keys, additivity notes and the SCD
   choice for each dimension.

**Ability to demonstrate:** a coherent star schema whose grain, measures and
dimensions answer the stated questions.

#### 4.6 Advanced-level learning sequence

1. **Evaluate historical tracking:** which dimensions need history and for which
   reports; cost and complexity of type 2; effective dating and "current
   flag" correctness; late-arriving dimension data.
2. **Check grain consistency:** never mix grains in one fact table; if two
   grains are needed, use two facts.
3. **Detect join problems:** fan-out when joining facts at different grains or
   through many-to-many bridges; double counting; missing rows from inner
   joins on unknown members (use explicit "unknown" dimension rows).
4. **Conformed dimensions** across processes so measures can be compared and
   combined (drill-across); ownership of conformed dimensions.
5. **Handle many-to-many** between facts and dimensions (bridge tables) and
   its effect on additivity.
6. **Fact-less facts** for events with no measure (coverage, eligibility).
7. **Consider the consumption layer:** semantic definitions of measures,
   aggregates, and performance structures without changing the grain.
8. **Relationship to the underlying structures:** dimensional models are
   usually *derived* from integrated or historical data (Topics 3, 5), not a
   replacement for them.
9. **Questions to answer:** What query becomes impossible at this grain?
   Where might a balance be summed wrongly?
10. **Exercise:** Given a flawed dimensional model (mixed grain, unsummable
    measure, missing unknown member), list defects, correct them and show the
    effect on a sample query result.

**Ability to demonstrate:** diagnose grain and additivity defects and show their
numerical consequences.

#### 4.7 Industry-application exercises

- Design a dimensional model for Northbridge card and payment analytics to
  answer a defined set of ten business questions; state the grain of every
  fact table first.
- Validate the model with a small illustrative dataset (a dozen rows) and show
  that each business question returns the expected result.
- Document SCD decisions and the reports each affects.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* The business asks for "average balance by customer segment by
   month". Which fact type, grain and aggregation rule apply?
2. *Scenario:* An analyst sums month-end balances across months. What is wrong
   and what do you provide instead?
3. *Scenario:* A customer belongs to several segments at once. How does this
   affect the fact grain, bridge design and totals?

#### 4.9 Expected outputs and deliverables

- Grain statements for each fact table.
- Star schema(s) with keys, measures, additivity and SCD decisions.
- Business-question coverage matrix.
- Answers to Topic 4 practice questions.

#### 4.10 Common mistakes and misconceptions

- Designing tables before stating the grain.
- Mixing grains in one fact table.
- Summing semi-additive or non-additive measures.
- Putting descriptive text in facts.
- Treating a dimensional model as a replacement for integrated history.
- Ignoring unknown and late-arriving members.

#### 4.11 Mastery criteria

- States grain first, every time, correctly.
- Classifies measures by additivity and handles them correctly.
- Chooses SCD treatment with business justification.
- Demonstrates that the model answers the stated questions.

#### 4.12 Completion gate

- [ ] Every fact table has an explicit grain sentence.
- [ ] Coverage matrix shows each business question answered.
- [ ] Flawed-model exercise correctly diagnosed.
- [ ] Topic 4 practice questions answered and corrected.

---

### Module 5 — [Data Vault and historical modeling](05-data-vault-and-historical-modeling.md)

#### 5.1 Learning objectives

- Explain why historical data and auditability matter.
- Describe Data Vault's purpose and characteristics.
- Describe the Data Vault components covered by the topic file (illustrated
  here through hubs, links and satellites).
- Model business keys, relationships and changing descriptive data.
- Distinguish historical capture from consumer-oriented analytical models.
- Weigh complexity, lineage, auditability and maintainability.
- Decide when a historical modeling approach is suitable.

#### 5.2 Why the topic matters in real-world Data Architecture

Regulators, auditors and analysts need to know what the data said **at the
time**, where it came from, and how it changed. Integration of many sources
with differing keys and rates of change needs a stable core. Data Vault is one
approach to that problem, with real costs.

#### 5.3 Prerequisite knowledge

Modules 2–4 here; 2D.3 Topic 2 (layers) and Topic 6 (change events).

> **Scope note.** This roadmap illustrates hubs, links and satellites. If the
> topic file covers additional constructs (for example reference tables,
> point-in-time or bridge structures), include them; if it covers fewer, follow
> the topic file.

#### 5.4 Beginner-level learning sequence

1. **Learn why history matters:** audit, regulatory evidence, point-in-time
   reporting, reproducibility, error investigation.
2. **Distinguish three ideas:** *current state*, *history of changes*, and
   *as-reported history* (what was believed at the time versus corrected
   later).
3. **Learn the three core constructs:**
   - *Hub:* a unique list of business keys for a core business concept
     (for example customer number) with load metadata.
   - *Link:* a relationship between hubs (for example customer–account),
     recorded as an association.
   - *Satellite:* descriptive attributes of a hub or link, versioned over time
     with load date and record source.
4. **Learn the metadata that accompanies each record:** load timestamp, record
   source.
5. **Questions to answer:** Why separate business keys from descriptive
   attributes? Why store relationships as their own structure?
6. **Exercise:** Place the elements of a customer record (customer number,
   name, address, segment, accounts held) into hub, link or satellite.

**Ability to demonstrate:** classify elements into hub, link and satellite and
explain why.

#### 5.5 Intermediate-level learning sequence

1. **Model a simple scenario:** customers, accounts and holdings from two source
   systems with different attribute sets and change rates.
   - Hubs: `Customer`, `Account`.
   - Link: `CustomerAccount`.
   - Satellites: customer details (per source), account details, link
     attributes (role).
2. **Handle business keys:** keys from different sources mapping to one hub
   record; key collisions; composite business keys.
3. **Split satellites by rate of change and by source** to avoid rewriting
   large rows for small changes.
4. **Track change:** insert a new satellite row when attributes change;
   retain load timestamps; derive end dates in queries or views.
5. **Record source and lineage** on every record.
6. **Contrast with the consumer layer:** show how a dimensional model (Topic 4)
   is derived from the vault structures through transformation.
7. **Questions to answer:** How do you reconstruct the customer as of a past
   date? What query shape does that need?
8. **Exercise:** Model two sources of customer data into hubs, links and
   satellites, then write the logic (in words or pseudo-SQL) for "customer
   address as of 31 March".

**Ability to demonstrate:** a vault model for a small scenario and a correct
point-in-time retrieval description.

#### 5.6 Advanced-level learning sequence

1. **Evaluate historical preservation:** what is preserved (all received
   states), what is not (intent unless captured), treatment of deletions and
   corrections, bi-temporal needs (valid time versus record time).
2. **Business-key stability:** consequences of unstable or reused keys; mapping
   and survivorship (details of master data belong to 2D.11).
3. **Lineage and auditability:** how load metadata give traceability to source
   files and runs.
4. **Complexity and cost:** more tables and joins, specialist skills, query
   complexity for consumers, load orchestration, storage growth.
5. **Downstream consumption:** the vault is rarely the consumption layer; plan
   the consumer-oriented layer and its refresh.
6. **Alternatives:** keeping raw history in a lake/lakehouse layer with
   append-only tables; relational history tables; type 2 dimensions; event
   logs. State what each provides and misses.
7. **Suitability criteria:** many sources, auditability requirement,
   frequent source change, need for parallel load, tolerance for added
   complexity; and when **not** to use it (single stable source, small scale,
   no audit need, small team).
8. **Questions to answer:** Would a simpler history approach meet the
   requirement? What does the consumer pay for the vault's flexibility?
9. **Exercise:** For three scenarios (single-source operational reporting;
   multi-source regulated integration; exploratory analytics), recommend a
   historical approach and justify with criteria.

**Ability to demonstrate:** choose between a vault and simpler alternatives
with evidence, and explain downstream consumption.

#### 5.7 Industry-application exercises

- Design and explain a historical modeling approach for Northbridge's
  integration of core banking, cards and CRM customer data.
- Define the business keys, record sources and load metadata.
- Describe the consumer-layer derivation without modeling it in full.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* A source system reuses customer numbers after closure. What does
   this do to a hub and how do you protect against it?
2. *Scenario:* A regulator asks what the bank knew about a customer on a past
   date. Which structures answer it and which do not?
3. *Scenario:* A team proposes a vault for a single stable system with one
   reporting consumer. Evaluate.

#### 5.9 Expected outputs and deliverables

- Hub/link/satellite model for the scenario.
- Point-in-time retrieval logic.
- Historical approach decision with criteria.
- Answers to Topic 5 practice questions.

#### 5.10 Common mistakes and misconceptions

- Assuming Data Vault is the best choice for every platform.
- Mixing business keys with descriptive attributes.
- Treating the vault as the layer analysts query directly.
- Losing source and load metadata.
- Confusing history of change with history of belief (bi-temporal).
- Ignoring the cost to consumers.

#### 5.11 Mastery criteria

- Classifies elements into the vault constructs correctly.
- Explains history preservation versus consumption.
- Chooses between historical approaches with explicit criteria.

#### 5.12 Completion gate

- [ ] Vault model and point-in-time retrieval reviewed.
- [ ] Decision record includes at least one simpler alternative considered.
- [ ] Topic 5 practice questions answered and corrected.

---

### Module 6 — [Event modeling and domain-driven design](06-event-modeling-and-domain-driven-design.md)

#### 6.1 Learning objectives

- Relate business domains to data models.
- Define domain boundaries and domain language.
- Model business events and meaningful state changes.
- Distinguish entities, state and events.
- Reason about cross-domain ownership and consistency.
- Relate event models to domain-oriented architecture and data products.
- Handle evolution of concepts and event schemas and ambiguous boundaries.

#### 6.2 Why the topic matters in real-world Data Architecture

Models that ignore domain boundaries force one meaning of every word on the
whole enterprise. Models that record only current state discard what happened.
Event and domain thinking addresses both, and underpins data products and event
contracts (2D.3 Topics 4, 6).

#### 6.3 Prerequisite knowledge

Modules 1–5 here; 2D.1 Topic 3; 2D.3 Topics 1, 4 and 6.

#### 6.4 Beginner-level learning sequence

1. **Learn the vocabulary:** domain, subdomain, **bounded context** (the
   boundary within which a model and its terms are consistent), **ubiquitous
   language** (the shared vocabulary within a context), entity, value object,
   aggregate (a cluster treated as a unit for consistency), event.
2. **Define a business event:** something that happened, in the past tense,
   with an identity and a time. *Illustrative:* `PaymentPosted`,
   `AccountOpened`.
3. **Distinguish three things:**

   | Concept | Question it answers | Example |
   | --- | --- | --- |
   | Entity | What exists and has identity? | Account A123 |
   | State | What is true now? | Balance = 500 |
   | Event | What happened? | Deposit of 100 posted at 10:02 |

4. **Questions to answer:** Why is "Customer" in the lending context not the
   same as in the marketing context?
5. **Exercise:** List the events in an account-opening process in past tense.

**Ability to demonstrate:** distinguish entity, state and event and name
events correctly.

#### 6.5 Intermediate-level learning sequence

1. **Identify domains and boundaries** for Northbridge (retail, lending, cards,
   risk) from the capability map (2D.1 Topic 3).
2. **Build a context map:** the relationships between contexts (upstream
   supplier, downstream consumer, shared concepts that translate).
3. **Model entities and aggregates** inside one context, with the invariants
   each aggregate protects.
4. **Model events:** name, identity (event id), time (event time and record
   time), subject (entity key), type, version, payload (the facts that
   changed), and cause (command/correlation id).
5. **Distinguish event kinds:** domain event (business meaning) versus
   change-data record (technical row change).
6. **Link domain model to event model:** each aggregate state change should
   correspond to one or more events; each event should be explainable by a
   business process step.
7. **Questions to answer:** Which context owns `CustomerAddressChanged`?
   Which contexts need to know?
8. **Exercise:** For loan origination, produce a bounded-context sketch, a list
   of events with their attributes, and a table mapping events to the entities
   whose state they change.

**Ability to demonstrate:** a consistent domain model and event model for one
business process.

#### 6.6 Advanced-level learning sequence

1. **Cross-domain ownership and semantic consistency:** the same word with
   different meanings (translate at the boundary); the same fact owned in one
   place and referenced elsewhere; shared kernel versus anti-corruption layer
   at the concept level.
2. **Consistency across contexts:** eventual consistency; compensating
   actions; why a single enterprise-wide transaction across contexts is
   usually not available.
3. **Event design quality:** facts not commands; sufficient context in the
   payload versus reference-only events; sensitive data in events (link to
   2D.3 Topic 6); ordering scope.
4. **Event evolution:** adding fields, deprecating, splitting an event into two;
   semantic change when the business redefines a term (links to Topic 7).
5. **Event models and data products:** which events a domain publishes as part
   of its product interface; the analytical model derived from events.
6. **Ambiguous boundaries:** symptoms (constant translation, circular
   dependencies, "god" entities such as an all-purpose Customer) and
   resolution (split context, introduce a mapping, assign an owner).
7. **Limits:** event modeling does not replace entity modeling; some data are
   best kept as reference state; avoid event-izing everything.
8. **Questions to answer:** Which concept should *not* be shared across
   contexts? Where would you place the boundary and why?
9. **Exercise:** Take a given "enterprise Customer" model, split it into
   context-specific models, define the translations and the events crossing the
   boundaries.

**Ability to demonstrate:** a context split with translations, ownership and
cross-context events, and an explanation of consistency implications.

#### 6.7 Industry-application exercises

- Create a conceptual domain model and an event model for the Northbridge
  card-dispute process and show how they align.
- Specify, at the concept level, the events the Cards domain would publish as
  part of its data product (no product-specific implementation).
- Document two ownership ambiguities and how you resolved them.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* Risk and Retail both claim "customer status". They mean
   different things. What do you do?
2. *Scenario:* A single event is used both to drive operations and to feed
   analytics. What goes wrong if the payload contains only state?
3. *Scenario:* A team publishes row-change records and calls them domain
   events. Evaluate.

#### 6.9 Expected outputs and deliverables

- Context map and glossary per context.
- Event catalogue with attributes and ownership.
- Domain-to-event alignment table.
- Answers to Topic 6 practice questions.

#### 6.10 Common mistakes and misconceptions

- One enterprise-wide definition forced on every context.
- Naming events in the present tense or as commands.
- Treating row-change records as domain events.
- Putting current state in events without the fact of what happened.
- Event-izing everything.
- Ignoring ownership of events and concepts.

#### 6.11 Mastery criteria

- Identifies boundaries and language per context.
- Models events correctly and distinguishes them from state and entities.
- Explains cross-domain consistency and evolution.

#### 6.12 Completion gate

- [ ] Context map, event catalogue and alignment table reviewed.
- [ ] Every event has a past-tense name, owner, identity, time and subject.
- [ ] Topic 6 practice questions answered and corrected.

---

### Module 7 — [Schema evolution and backward compatibility](07-schema-evolution-and-backward-compatibility.md)

#### 7.1 Learning objectives

- Explain why schemas change.
- Classify changes: add, remove, rename, retype, change optionality, change
  constraints, change meaning.
- Define backward and forward compatibility (as defined in the source material;
  conventional meaning given below).
- Perform impact analysis across producers and consumers.
- Plan versioning, migration and safe rollout.
- Test and validate schema changes.
- Link schema evolution to model governance.

#### 7.2 Why the topic matters in real-world Data Architecture

Systems that cannot change are dead; systems that change carelessly break
their consumers. A valid change is not necessarily a safe one: a field's type
may be unchanged while its meaning shifts and every downstream report becomes
wrong.

#### 7.3 Prerequisite knowledge

Modules 1–6 here; 2D.3 Topic 6 (contracts and compatibility).

#### 7.4 Beginner-level learning sequence

1. **Learn why schemas change:** new requirements, regulation, error
   correction, source changes, mergers, optimisation.
2. **Learn terminology (conventional definitions; use the topic file's if
   different):**
   - *Backward compatible:* consumers written for the **new** schema can read
     **old** data (or: new producers do not break old consumers, depending on
     the source definition). **State the definition you are using.**
   - *Forward compatible:* consumers written for the **old** schema can read
     **new** data.
   - *Breaking change:* one that requires a coordinated update.
3. **Learn the change types** and a first-pass classification:

   | Change | Typical safety | Why |
   | --- | --- | --- |
   | Add optional field | Usually safe | Old consumers ignore it |
   | Add required field | Usually breaking for producers/old data | Old data lack it |
   | Remove field | Breaking for consumers using it | Consumer loses data |
   | Rename field | Breaking | Looks like remove + add |
   | Widen type | Often safe | Old values still valid |
   | Narrow type | Breaking | Old values may not fit |
   | Change meaning, same type | **Silently breaking** | No syntactic signal |

4. **Questions to answer:** Why is renaming a field breaking? Why is changing
   meaning the most dangerous change?
5. **Exercise:** Classify twenty changes as compatible or breaking and say who
   is affected.

**Ability to demonstrate:** classify common schema changes and name the
affected parties.

#### 7.5 Intermediate-level learning sequence

1. **Analyse consumers:** list consumers of a model or event, what they read,
   and what they assume (required fields, ordering, enumerations).
2. **Impact analysis procedure:** identify the change; list dependents (using
   lineage and contracts); classify the effect for each; decide required
   actions and owners.
3. **Versioning approaches:** versioned schema identifiers; additive-only
   rules; parallel versions; explicit deprecation.
4. **Safe patterns:** expand-and-contract (add the new, migrate readers, then
   remove the old); default values for new fields; tolerant readers;
   deprecation windows.
5. **Migration considerations:** backfilling, dual writes or dual reads during
   a transition, data volume and time estimates (2D.2 Topic 3), rollback.
6. **Testing:** compatibility checks between old and new schemas; consumer
   contract tests; sample data from each version; reconciliation after
   migration.
7. **Questions to answer:** Who must be told, and by when? What is the rollback
   plan?
8. **Exercise:** For five proposed changes to a payment model, produce an impact
   table (consumer, effect, action, owner, date).

**Ability to demonstrate:** an impact analysis and a transition plan for each
change.

#### 7.6 Advanced-level learning sequence

1. **Coordinated versus independent deployment:** when producers and consumers
   can change independently (additive, tolerant readers) and when a lockstep
   release is unavoidable; the cost of lockstep.
2. **Semantic change management:** definitions that change (for example
   "active customer"); introduce a new field or version rather than silently
   redefine; record the change in the dictionary and notify consumers.
3. **Historical data:** old records keep old shapes; decide on upgrading in
   place versus reading through an adapter; implications for stored history
   (Topic 5).
4. **Dependency risk:** transitive dependents unknown to the producer; shadow
   consumers (spreadsheets, scripts); need for lineage (2D.11).
5. **Constraint evolution:** tightening versus loosening; effect on existing
   invalid data.
6. **Governance link:** change request, review (Topic 8), approval, compatibility
   policy per model class (for example strict for regulatory interfaces,
   flexible for exploratory data), recorded decisions.
7. **Failure modes:** "it compiles" thinking, unannounced renames, enumerations
   extended without consumers handling new values, big-bang migrations.
8. **Questions to answer:** Which compatibility rule would you enforce
   automatically and which by review? What is your policy for removing a
   field?
9. **Exercise:** Design a compatibility policy and a deprecation timeline for a
   widely consumed customer model, including how violations are detected.

**Ability to demonstrate:** a policy and plan that balance independence,
safety and cost.

#### 7.7 Industry-application exercises

- Develop a schema evolution plan for the Northbridge customer model with five
  consumers, and document how compatibility is validated.
- Write the deprecation notice for a renamed attribute, with dates and
  support actions.
- Define the automated checks you would require in a change pipeline (concept
  level).

#### 7.8 Practical scenarios and case-based reasoning

1. *Scenario:* A new regulation requires a new mandatory attribute for new
   accounts only. How do you represent this in the model and for old data?
2. *Scenario:* A producer extends an enumeration with a new status value. Which
   consumers break and why?
3. *Scenario:* A column's type is widened and values are now stored differently
   (units changed). What was missed?

#### 7.9 Expected outputs and deliverables

- Change classification table.
- Impact analysis and transition plan.
- Compatibility and deprecation policy.
- Answers to Topic 7 practice questions.

#### 7.10 Common mistakes and misconceptions

- Treating syntactic validity as safety.
- Allowing silent semantic change.
- Renaming without a transition.
- Ignoring unknown consumers.
- Assuming additive means always safe (new enumeration values, new required
  semantics).
- No rollback plan.

#### 7.11 Mastery criteria

- Classifies changes by compatibility correctly, including semantic changes.
- Produces an impact analysis with owners and dates.
- Designs a transition and validation approach.

#### 7.12 Completion gate

- [ ] Change table, impact analysis and policy reviewed.
- [ ] At least one semantic-change case handled explicitly.
- [ ] Topic 7 practice questions answered and corrected.

---

### Module 8 — [Model review, naming standards and data dictionaries](08-model-review-naming-standards-and-data-dictionaries.md)

#### 8.1 Learning objectives

- Explain the purpose of model review.
- Apply consistent naming standards to entities, attributes, keys and
  relationships.
- Produce business definitions and a data dictionary.
- Review models for completeness, consistency and semantic accuracy.
- Validate keys, relationships, constraints and business rules.
- Run review, issue resolution and approval; maintain models over time.
- Communicate models to technical and business audiences.

#### 8.2 Why the topic matters in real-world Data Architecture

Most defects in models are found by review, not by tools. Consistent naming and
definitions are what make a model usable by someone who did not build it, and
what make governance, lineage and discovery possible later.

#### 8.3 Prerequisite knowledge

Modules 1–7 here; 2D.1 Topic 5 (governance and review).

#### 8.4 Beginner-level learning sequence

1. **Learn why reviews exist:** catch defects early, share understanding,
   enforce standards, record decisions.
2. **Learn naming basics:** a consistent case and word-separation style;
   singular entity names; meaningful full words; standard suffixes for
   identifiers, dates, amounts, flags, codes; no unexplained abbreviations; no
   reuse of one name for two meanings.
3. **Learn the dictionary parts:** name, business definition, technical
   description (where appropriate), data type (only at logical/physical
   level), constraints, allowed values, source, owner/steward.
4. **Learn a good definition:** says what it **is**, not just what it is used
   for; does not use the term in its own definition; states inclusions and
   exclusions.
5. **Questions to answer:** Is "status" a good attribute name? What would make
   it one?
6. **Exercise:** Improve ten poor attribute names and definitions.

**Ability to demonstrate:** write unambiguous names and definitions.

#### 8.5 Intermediate-level learning sequence

1. **Review an existing model** with a structured checklist:

   | Area | Questions |
   | --- | --- |
   | Scope and traceability | Does every element trace to a requirement? Is scope stated? |
   | Entities | Defined, distinct, correctly named? Missing or duplicate? |
   | Attributes | Defined? Atomic? Correctly placed? Mandatory/optional stated? |
   | Keys | Identifier defined, stable, unique? |
   | Relationships | Cardinality and optionality both ways? Verbs? |
   | Constraints and rules | Represented or recorded? |
   | Normalisation | Anomalies? Justified denormalisation? |
   | Naming | Standard followed? Synonyms and homonyms? |
   | Documentation | Dictionary complete? Assumptions and open questions listed? |

2. **Classify defects** by severity (blocking, major, minor) and type (semantic,
   structural, naming, documentation).
3. **Write actionable findings:** location, defect, why it matters, suggested
   correction, owner.
4. **Maintain the dictionary** alongside the model; keep a single source of
   definition.
5. **Questions to answer:** Which findings are cosmetic and which change
   meaning?
6. **Exercise:** Review a supplied small model, list at least ten findings with
   severity and correction, and produce the corrected dictionary entries.

**Ability to demonstrate:** a structured review with actionable, prioritised
findings.

#### 8.6 Advanced-level learning sequence

1. **Establish review criteria:** entry criteria (what must exist before
   review), review checklist, exit criteria (approval conditions), role
   assignments (author, reviewer, domain expert, approver).
2. **Consistency across related models:** shared concepts named and defined the
   same way; conformed attributes; duplicated entities across domains;
   synonym and homonym registers.
3. **Semantic ambiguity:** attributes whose meaning varies by source, by time
   or by context; overloaded codes; "type" and "status" columns with mixed
   meanings.
4. **Maintainability:** how the model will be changed; version history;
   ownership; link to schema evolution (Topic 7) and governance.
5. **Approval practice:** conditional approval, tracked issues, waivers with
   expiry (2D.1 Topic 4 exception practice).
6. **Communication:** a business-readable conceptual view, a designer-readable
   logical view, and an engineer-readable physical view, with agreed
   terminology across all three.
7. **Anti-patterns in review:** cosmetic-only comments, style wars, no
   follow-up on findings, approval by silence.
8. **Questions to answer:** What would make you reject a model outright? Which
   standards are enforced by tools and which by people?
9. **Exercise:** Define a review process and criteria for a bank's data models
   and apply them to two models that share concepts, reporting cross-model
   inconsistencies.

**Ability to demonstrate:** a review process with criteria and a cross-model
consistency analysis.

#### 8.7 Industry-application exercises

- Conduct a structured review of the Northbridge enterprise model produced in
  the project and produce findings, corrections and approval criteria.
- Write the naming standard (one page) and the dictionary template.
- Present the model to a business audience and to an engineering audience;
  list what differs.

#### 8.8 Practical scenarios and case-based reasoning

1. *Scenario:* Two models define `customer_status` with different allowed
   values. What do you do?
2. *Scenario:* A reviewer rejects a model because "the diagram is ugly". How do
   you separate cosmetic from semantic findings?
3. *Scenario:* A model was approved a year ago and the system has changed. How
   do you detect and fix drift?

#### 8.9 Expected outputs and deliverables

- Review checklist and review findings log.
- Naming standard and dictionary template.
- Corrected dictionary entries.
- Answers to Topic 8 practice questions.

#### 8.10 Common mistakes and misconceptions

- Treating naming as cosmetic.
- Writing definitions that restate the name.
- Reviewing only diagrams, not rules and definitions.
- Having no exit criteria.
- Allowing a dictionary to diverge from the model.
- Using one term for two concepts or two terms for one.

#### 8.11 Mastery criteria

- Writes clear definitions and applies naming standards consistently.
- Reviews models against defined criteria and produces actionable findings.
- Identifies semantic ambiguity and cross-model inconsistency.

#### 8.12 Completion gate

- [ ] Review findings are actionable and prioritised.
- [ ] Dictionary entries pass a "no circular definition" check.
- [ ] Naming standard applied consistently across the exercise set.
- [ ] Topic 8 practice questions answered and corrected.

---

## 5. Module dependencies and recommended learning order

### 5.1 Dependency table

| # | Topic file | Prerequisite concepts | Main learning outcome | Practical exercise / deliverable | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `01-conceptual-logical-and-physical-models.md` | 2D.1–2D.2 concepts; basic SQL | Place decisions at the correct abstraction level | Conceptual → logical pair; deferred-decision list | Level exercise ≥ 90%; no level violations |
| 2 | `02-entities-relationships-cardinality-and-constraints.md` | Topic 1 | Build a structurally correct ER model | ER model; rules register; test cases | Test set passes; both-direction cardinality |
| 3 | `03-normalization-and-relational-modeling.md` | Topic 2 | Normalise and justify denormalisation | Worked normalisations; revised schema | Dependency lists and lossless-join proofs |
| 4 | `04-dimensional-modeling-facts-dimensions-and-grain.md` | Topics 2, 3 | Design dimensional models from explicit grain | Star schema; coverage matrix | Grain stated first; questions answered |
| 5 | `05-data-vault-and-historical-modeling.md` | Topics 2–4 | Model and decide on historical approaches | Hub/link/satellite model; point-in-time logic | Decision record with simpler alternative |
| 6 | `06-event-modeling-and-domain-driven-design.md` | Topics 1–5; 2D.3 Topics 1, 4, 6 | Model domains and events | Context map; event catalogue | Events correctly named, owned, aligned |
| 7 | `07-schema-evolution-and-backward-compatibility.md` | Topics 2, 5, 6; 2D.3 Topic 6 | Plan safe change | Impact analysis; compatibility policy | Semantic-change case handled |
| 8 | `08-model-review-naming-standards-and-data-dictionaries.md` | Topics 1–7 | Review and document models | Review log; naming standard; dictionary | Actionable, prioritised findings |

### 5.2 Recommended order and why

1. **Topic 1: abstraction levels.** Everything else depends on knowing which
   level you are working at.
2. **Topic 2: structural foundation.** Entities, relationships, cardinality and
   constraints are the grammar of every later model.
3. **Topic 3: normalisation and relational modeling.** Builds on the structural
   model by making each fact stored once; it is the reference point for
   judging all later denormalisation.
4. **Topic 4: dimensional modeling.** Introduces analytical modeling and fact
   grain; it is learned after normalisation because it is defined in contrast
   to it.
5. **Topic 5: Data Vault and historical modeling.** Addresses historical
   preservation and integration, using the relational and dimensional ideas as
   reference points.
6. **Topic 6: event modeling and domain-driven design.** Introduces domain
   semantics, business events and model boundaries, adding the dimension of
   *meaning and ownership* to structure.
7. **Topic 7: schema evolution.** Safe change requires understanding what was
   modelled, how, and for whom.
8. **Topic 8: review, naming, dictionaries.** Establishes the documentation and
   quality practices that apply to everything before it.

### 5.3 Where the order is not strictly linear

- **Topics 4 and 5 are complementary,** not sequential: dimensional models are
  typically derived from integrated or historical structures. After Topic 5,
  revisit Topic 4's SCD choices.
- **Topic 6 informs Topics 1–2:** domain boundaries may change the entities you
  chose. Revisit Topic 2 after Topic 6.
- **Topic 7 should influence initial design:** design for change from the start
  (stable identifiers, additive evolution). Revisit Topics 2 and 3 after
  Topic 7.
- **Topic 8 loops back to everything:** a review finding often requires
  changing earlier modeling decisions. Treat review as iterative, not final.

| Trigger | Revisit |
| --- | --- |
| Review finds ambiguous entity | Topics 1, 2, 6 |
| Query returns wrong totals | Topic 4 (grain), Topic 2 (relationships) |
| Source adds a new system | Topic 5 (keys, satellites), Topic 7 |
| Domain boundary disputed | Topic 6, 2D.3 Topic 4 |
| Breaking change requested | Topic 7, Topic 8 |

Cross-references: foundations (2D.1), requirements (2D.2), patterns (2D.3),
storage (2D.5), integration (2D.6), platform (2D.7), governance (2D.10),
metadata and master data (2D.11), serving (2D.14), documentation and reviews
(2D.15).

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
| Modeling terminology and abstraction levels | Definitions; level classification | 1 | Beginner |
| Entity and relationship identification | Extract structure from descriptions | 2 | Beginner → intermediate |
| Cardinality, optionality, keys, constraints | Precise structural statements and tests | 2 | Intermediate |
| Normalisation and relational design | Dependencies, decomposition, denormalisation | 3 | Intermediate → advanced |
| Fact-table grain and dimensional modeling | Grain, additivity, SCD, coverage | 4 | Intermediate → advanced |
| Historical modeling and Data Vault | Placement, point-in-time, suitability | 5 | Intermediate → advanced |
| Domain boundaries and event modeling | Contexts, events, ownership | 6 | Intermediate → advanced |
| Schema evolution and compatibility | Classification, impact, plans | 7 | Intermediate → advanced |
| Model review and naming standards | Defect finding, definitions | 8 | Intermediate → advanced |
| Integrated model design and justification | Cross-topic case studies | 1–8 | Industry |

### 6.3 Strategy

1. Answer each topic's questions after the topic, closed-book first.
2. For modeling questions, always provide: the rule in words, the model, and at
   least two test cases (one valid, one invalid).
3. For dimensional questions, state the grain first; for evolution questions,
   state the compatibility definition you use.
4. Mark each answer correct / partly correct / wrong with a one-sentence
   reason; re-attempt after several days.
5. Keep integrated answers as written artefacts; they feed the project.
6. Have advanced and industry answers reviewed by another person.

### 6.4 Expected performance by level

| Level | Successful performance |
| --- | --- |
| Beginner | Correct terminology and level classification; entities, attributes, relationships identified correctly in simple descriptions |
| Intermediate | Coherent models with explicit cardinality, optionality and keys; correct normalisation; dimensional models with stated grain; rules documented |
| Advanced | Alternatives compared with trade-offs; history, event and evolution cases handled; decisions justified and edge cases tested |
| Industry application | Integrated, traceable models with dictionary and review evidence that an independent reviewer can audit |

### 6.5 Evaluation criteria

| Criterion | What to check |
| --- | --- |
| Correctness | Structures, keys, forms and grains are right |
| Business-semantic accuracy | Names and definitions mean what the business means; no unflagged assumptions |
| Relationship consistency | Cardinality/optionality agree in both directions and with the rules |
| Constraint handling | Rules are represented, or recorded as needing enforcement elsewhere |
| Historical requirements | History needs are identified and met by an appropriate approach |
| Documentation quality | Definitions, dictionary, assumptions and open questions are present and clear |
| Justification | The answer explains why, states alternatives and trade-offs |

---

## 7. Project — Enterprise conceptual and logical data model

Project file:
[`Projects/04-enterprise-conceptual-and-logical-data-model.md`](Projects/04-enterprise-conceptual-and-logical-data-model.md)
(currently empty; this section defines its intended content). The project index
is [`Projects/README.md`](Projects/README.md).

This is an **enterprise modeling exercise**, not a diagram-drawing assignment.
The deliverable is a validated, traceable, documented model package whose rules
a domain expert can check and whose definitions another architect can reuse.

How it uses the eight topics:

| Project part | Topics |
| --- | --- |
| Conceptual → logical transformation | 1 |
| Entities, relationships, constraints | 2 |
| Normalisation decisions | 3 |
| Analytical, historical, event needs (where in scope) | 4, 5, 6 |
| Change considerations | 7 |
| Naming, dictionary, review | 8 |

### 7.1 Project objective

**Business objective:** give the organisation a shared, precise understanding of
its core customer, account and transaction data so that reports, integrations
and later platform design start from agreed meanings.

**Modeling objectives:** you must demonstrate that you can analyse a business
domain, identify entities and relationships, define business rules, produce
conceptual and logical models, and validate them.

**What the project deliberately does not require:** a physical schema. No data
types beyond what clarifies meaning, no indexes, partitioning, storage format,
platform selection or DDL. Physical decisions are listed as deferred (and
belong to module 2D.5). A logical model is complete when its rules are precise
and implementable, not when it is deployed.

### 7.2 Project scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. Customer, account and transaction data are
spread across a core banking system, a cards platform and a CRM, each with its
own definition of "customer" and "account". Reports disagree; a regulator has
asked for clearer definitions and accountability for customer and account data.

> All details are **illustrative assumptions**, not facts about any real
> organisation. You may substitute a real or realistic domain (observing
> confidentiality) but must label what you observed versus what you assume.

**Business problem.** No agreed enterprise definition of customer, account,
holding relationship, product and transaction; relationships and rules differ
by system.

**Stakeholders and model consumers (assumed).** Chief data officer (sponsor);
heads of retail, lending and cards; finance; risk; compliance; data
engineering; data governance; downstream report authors.

**Business processes in scope.** Customer onboarding; account opening and
holding; product subscription; payment/transaction posting.

**Entities to investigate (candidates, to be confirmed or rejected):** Party
(person/organisation), Customer role, Account, Account holding, Product,
Branch, Transaction, Address, Contact.

**In scope.** Conceptual and logical models for the above; business rules;
glossary; naming standards; data dictionary; review and validation.

**Out of scope.** Physical design; loan servicing and collections detail; card
authorisation detail; marketing data; security implementation; ETL; reporting
design; full historical and event modeling (only requirements that affect the
logical design are noted).

**Assumptions and unresolved questions (illustrative; refine in step 8).**
A customer can be a person or an organisation; an account can have several
holders with different roles; closed accounts are retained; a customer's legal
name can change; whether a minor can hold an account independently is
unresolved.

**Data quality, ownership and history considerations.** Identify the
authoritative source of each concept (unknown where not known), who is
accountable (unknown where not known), and which attributes need history (for
example name, address, holding role) without designing the historical
structures.

### 7.3 Step-by-step project execution

For each step: **Purpose · Inputs · Actions · Questions · Outputs · Validation.**

| Step | Purpose | Inputs | Actions | Questions to answer | Outputs | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define problem, objectives, modeling scope | Scenario | Write scope statement, exclusions | What is modelled and what is not? | Scope and assumptions | Sponsor-role reviewer confirms |
| 2 | Identify stakeholders and consumers | Scenario | Register; map consumers to uses | Who uses the model and for what? | Stakeholder and consumer list | Each consumer has a stated use |
| 3 | Gather requirements, terms, rules | Stakeholder inputs | Record statements verbatim; extract terms and rules | Which words mean different things? | Requirements summary; term list; draft rules | Each rule has a source |
| 4 | Identify processes and domain boundaries | Steps 1–3; 2D.1 Topic 3 | Map processes to domains/contexts | Where do meanings change? | Process and boundary map | Boundaries explain term conflicts |
| 5 | Identify candidate entities and meanings | Steps 3–4 | Extract and define entities | Is each a thing the business tracks? | Entity inventory | Each has a definition free of circularity |
| 6 | Identify attributes; separate identifiers from descriptors | Step 5 | Define attributes and identifiers | What identifies an instance, and is it stable? | Attribute inventory | Every entity has an identifier |
| 7 | Define relationships, cardinality, optionality, constraints | Steps 5–6 | Write both-direction statements; resolve many-to-many | What are the min and max in each direction? | Relationship inventory; rules register | No relationship lacks both directions |
| 8 | Resolve ambiguities; record assumptions and questions | Steps 3–7 | Interpretations list; ask expert (role-played) or assume and flag | Which ambiguity changes the structure? | Assumption and open-question log | Each item has an owner and a status |
| 9 | Create the conceptual model | Steps 5–8 | Draw core concepts and relationships, no data types | Can a business reader follow it? | Conceptual model | Terms match glossary |
| 10 | Validate the conceptual model | Step 9, requirements | Walk through scenarios with stakeholders | Does it express the rules without distortion? | Validation notes | Findings addressed or logged |
| 11 | Transform to the logical model | Steps 9–10 | Add attributes, identifiers, resolve relationships | What new information is needed? | Logical model draft | Every concept traces forward |
| 12 | Define keys, integrity and normalisation decisions | Step 11 | Keys, foreign keys, dependencies, normal form checks | Is each fact stored once? | Key and constraint definitions; normalisation notes | Lossless-join and dependency checks |
| 13 | Evaluate historical, analytical, event needs affecting scope | Steps 3, 11; Topics 4–6 | Note which attributes/relationships need history, which events matter | What must the logical model allow for? | Needs note and model adjustments | Adjustments do not exceed scope |
| 14 | Define naming conventions and definitions | Steps 5–12 | Write naming standard; finalise definitions | Are terms unique and meaningful? | Naming standard; glossary | Synonym/homonym check clean |
| 15 | Create the data dictionary | Steps 11–14 | Populate entity and attribute entries | Is each entry complete and non-circular? | Data dictionary | Sample audit passes |
| 16 | Review for completeness, consistency, redundancy, semantics | Steps 9–15; Topic 8 | Checklist review; log findings | Any defect that changes meaning? | Review findings | Findings classified by severity |
| 17 | Validate against scenarios and edge cases | Model, test set | Run ≥ 20 scenarios (valid and invalid) | Does the model accept and reject correctly? | Scenario results | All outcomes explained |
| 18 | Revise | Steps 16–17 | Correct models and dictionary; update trace | Do changes ripple? | Revised package; change log | Re-run key scenarios |
| 19 | Prepare final model package and decision summary | All | Assemble; summarise key decisions and deferred items | What must the next module decide? | Final package and summary | Reviewer confirms traceability |

**Per-step guidance:**

1. State exclusions firmly; this project stops at the logical model.
2. Include governance, compliance and data engineering as consumers.
3. Record statements before interpreting them.
4. Boundaries explain why two teams use one word for two things.
5. Define from the business perspective; avoid system table names.
6. Prefer stable business identifiers; flag mutable ones.
7. Write rules as sentences first, then model them.
8. Never fill a gap with an invented rule; mark it assumed or open.
9. No data types, no join tables in the conceptual view.
10. Use real scenarios, not diagram aesthetics.
11. Resolve many-to-many with associative entities carrying their own
    attributes.
12. Show dependencies and the decomposition proof.
13. Note needs; do not design vaults, stars or event streams here.
14. One term, one meaning.
15. Dictionary text must add information beyond the name.
16. Separate cosmetic from semantic findings.
17. Include invalid cases that the model must reject.
18. Update the glossary and dictionary whenever the model changes.
19. List physical decisions explicitly deferred.

### 7.4 Required project deliverables

Deliverables are proportionate; related content is combined.

| # | Deliverable | Purpose | Minimum contents |
| --- | --- | --- | --- |
| D1 | Project scope and assumptions | Fix boundaries | Objective, in/out of scope, labelled assumptions |
| D2 | Stakeholder and requirements summary | Source of rules | Stakeholders, consumers, requirements, success criteria |
| D3 | Business glossary / terminology list | Shared language | Term, definition, context, synonyms, source |
| D4 | Entity inventory | What is modelled | Name, definition, purpose, source, key relationships, owner (if known), open questions |
| D5 | Business rules and constraints register | Rules explicit | ID, rule text, source, where represented (structure/constraint/procedure), test case |
| D6 | Conceptual data model | Business-level view | Entities, relationships, definitions, scope boundary; no data types |
| D7 | Logical data model | Precise structure | Entities, attributes, identifiers, relationships, cardinality, optionality, normalised structure |
| D8 | Relationship and cardinality definitions | Unambiguous links | Each relationship in words, both directions, min/max, optionality, rule, test |
| D9 | Key and integrity constraint definitions | Identification and validity | Primary/candidate/foreign keys, uniqueness, referential rules, other constraints |
| D10 | Modeling decisions and unresolved questions | Honesty and traceability | Decisions with rationale, assumptions, open questions with owners, deferred physical decisions |
| D11 | Naming standards | Consistency | Conventions for entities, attributes, keys, relationships, suffixes, abbreviations |
| D12 | Data dictionary | Reusable documentation | Entity/attribute, definition, constraints, allowed values, source, owner/steward (if known) |
| D13 | Model validation and review findings | Evidence of quality | Checklist results, scenario test results, findings with severity and resolution |
| D14 | Final project summary | Readout | One to two pages: scope, model overview, key decisions, open items, next steps |

### 7.5 Suggested model and documentation fields

Use only fields that serve a purpose. Mark `Unknown` rather than inventing.
Never force physical, platform-specific details into a conceptual model.

**Entity inventory**

| Field | Purpose |
| --- | --- |
| Entity name | Reference |
| Business definition | Meaning, with inclusions/exclusions |
| Business purpose | Why it is tracked |
| Source / stakeholder | Provenance |
| Key relationships | Context |
| Ownership (if known) | Accountability |
| Open questions | Honesty |

**Attribute inventory**

| Field | Purpose |
| --- | --- |
| Attribute name | Reference |
| Business definition | Meaning |
| Data meaning (nature of the value, not the technical type) | Semantics |
| Role (identifier / descriptive) | Structure |
| Required or optional | Optionality |
| Relevant constraints | Validity |
| Related business rule | Traceability |

**Relationship inventory**

| Field | Purpose |
| --- | --- |
| Relationship description (verb phrase, both directions) | Meaning |
| Participating entities | Scope |
| Cardinality (min/max each direction) | Precision |
| Optionality | Precision |
| Business rule | Justification |
| Validation scenario | Test |

**Data dictionary**

| Field | Purpose |
| --- | --- |
| Entity / attribute name | Reference |
| Business definition | Meaning |
| Technical description (where applicable) | Implementation guidance |
| Data type (only where appropriate for the model level) | Logical precision |
| Constraints | Validity |
| Allowed values (where relevant) | Valid domain |
| Ownership / stewardship (where known) | Accountability |

**Business rules register**

| Field | Purpose |
| --- | --- |
| Rule ID and text | Reference |
| Source | Provenance |
| Representation (structure / constraint / process) | Where enforced |
| Valid example, invalid example | Testability |
| Status (confirmed / assumed / open) | Honesty |

### 7.6 Validation and quality assurance

| Check | How to verify |
| --- | --- |
| Models align with scope and requirements | Each element traces to a requirement or rule; nothing outside scope |
| Entity definitions meaningful and unambiguous | Two reviewers independently classify ten sample instances the same way |
| Attributes have clear definitions | No definition restates the name; sample audit passes |
| Relationships and cardinalities reflect business rules | Each relationship has both-direction statements and a rule reference |
| Keys and constraints support identification and integrity | Every entity has a stable identifier; invalid test cases are rejected |
| Normalisation justified at the logical level | Dependency lists and lossless-join check exist; any redundancy explained |
| Conceptual and logical models are consistent | Every conceptual element appears in the logical model and vice versa, with differences explained |
| Naming and definitions consistent | Synonym/homonym check finds no conflict |
| Assumptions and open questions documented | D10 lists each with owner and status; none hidden in the diagram |
| Representative scenarios can be expressed | ≥ 20 scenarios run, including ≥ 8 invalid, all with explained outcomes |
| Stakeholder review findings addressed | Each finding resolved or recorded as accepted/deferred with reason |

### 7.7 Project completion gate

The project is complete only when **all** hold:

- [ ] D1–D14 exist, version-dated, and use consistent names and IDs.
- [ ] **Conceptual model:** every entity has a non-circular definition, every
      relationship is named, and no data types or platform terms appear.
- [ ] **Logical model:** every entity has an identifier; every relationship has
      both-direction cardinality and optionality; many-to-many relationships
      are resolved; no unexplained redundancy.
- [ ] **Business rules:** every confirmed rule has a source, a representation
      and at least one valid and one invalid test case; assumed and open rules
      are labelled.
- [ ] **Data dictionary:** complete for 100% of logical entities and
      attributes; a 20% random sample has no circular or empty definitions.
- [ ] **Validation evidence:** ≥ 20 scenarios executed against the model with
      recorded outcomes; no unexplained disagreement between model and rule.
- [ ] **Traceability:** a random trace from three logical elements back to
      requirements, and from three requirements forward to the model, succeeds.
- [ ] **Consistency:** conceptual and logical models differ only by documented
      refinement.
- [ ] **Final review:** an independent reviewer completes the Topic 8 checklist,
      all blocking and major findings are resolved, and remaining findings are
      logged with owners.
- [ ] **Deferred decisions:** physical decisions are listed, not made.

Producing the diagrams and documents is **not** sufficient; the evidence
criteria must be met.

### 7.8 Connection to subsequent modules

| Later module | Reusable inputs from this project | Decisions that belong to that module |
| --- | --- | --- |
| 2D.5 Database and storage architecture | Logical model, keys, constraints, volume-relevant entities | Engine, data types, indexing, partitioning, storage format, physical denormalisation |
| 2D.6 Data integration and interoperability | Glossary, canonical definitions, identifiers, relationship rules | Interface design, mapping implementation, CDC and batch choices |
| 2D.7 Enterprise data platform and lakehouse | Entity scope, domain boundaries | Layer design, zones, platform components |
| Dimensional and historical modeling (applied later in 2D.5–2D.7 and 2D.14) | Needs note (Step 13), identifiers, relationships | Fact grain, dimensional design, vault structures for the chosen platform |
| 2D.10–2D.11 Governance, metadata, lineage | Glossary, dictionary, ownership gaps | Classification, policy, lineage tooling, stewardship operating model |
| Schema evolution and architecture reviews (2D.15) | Naming standard, compatibility questions, review findings | Change governance, review board process |

Do not add physical design, platform selection or ETL work to this project.

---

## 8. Final learning assessment and completion checklist

Self-reported confidence is not sufficient; each row requires the stated
evidence.

| # | You can… | Evidence required for mastery |
| --- | --- | --- |
| 1 | Explain the differences between conceptual, logical and physical models | Level classification exercise ≥ 90%; model pair with no level violations; deferred-decision list |
| 2 | Identify entities, attributes, relationships, cardinality and constraints | ER model with both-direction cardinality/optionality; valid and invalid test set passes |
| 3 | Create coherent relational models and justify normalisation decisions | Dependency lists, decomposition and lossless-join proof; denormalisation record |
| 4 | Define fact-table grain and create appropriate dimensional models | Grain sentence for each fact; coverage matrix showing all business questions answered |
| 5 | Explain historical modeling and relevant Data Vault concepts | Hub/link/satellite model; point-in-time retrieval; decision record with a simpler alternative |
| 6 | Model business domains and events | Context map; event catalogue with owner, time and identity; alignment table |
| 7 | Evaluate schema changes and compatibility implications | Change classification including a semantic change; impact analysis; compatibility policy |
| 8 | Review models using consistent naming and documentation standards | Review log with prioritised findings; naming standard; dictionary entries pass the circularity check |
| 9 | Produce a validated enterprise conceptual and logical model | D1–D14 and the project completion gate (Section 7.7) met |
| 10 | Explain and defend important modeling decisions | Challenge round: two reviewer objections answered from recorded rules, scenarios and decision records |

Module complete when:

- [ ] All eight topic completion gates are signed off.
- [ ] `practice-questions.md` answered; wrong answers corrected and
      re-attempted.
- [ ] The project completion gate is met.
- [ ] You have presented the model package and answered a reviewer's challenges
      without introducing unsupported claims.
- [ ] Deferred physical decisions and open questions are logged for the next
      module (2D.5).

---

## 9. Where this module leads

Module 2D.5, **Database and Storage Architecture**, takes the logical model,
keys, constraints and volume-relevant entities produced here and makes the
physical decisions: engines, data types, layout, partitioning, formats,
retention and storage tiers.
