# Practice Questions — Conceptual, Logical and Physical Data Modeling

> **Scope note:** This assessment is grounded in the Stage 2D module roadmap and the eight lesson files available for this module. Northbridge Bank is fictional; scenario details below are illustrative assumptions, not facts about a real bank. This resource assesses conceptual and logical modeling and the requirements that inform adjacent historical, analytical and event designs. It does not require physical database implementation.

## Section A — Assessment instructions

1. Attempt questions closed-book before consulting the answer key. Record your first answer; do not erase it after checking.
2. For every modeling answer, provide (a) the business rule in words, (b) the model or structure, and (c) at least one valid and one invalid test case. Where a rule is not given, state competing interpretations and mark the assumption or open question.
3. For dimensional questions, state the grain before selecting dimensions or measures. For schema evolution, state the compatibility convention and identify affected consumers.
4. For architectural decisions, compare at least two alternatives, trade-offs, risks and a reasoned recommendation. Do not present taste as evidence.
5. Mark each answer **Correct / Partly correct / Incorrect** and write a one-sentence reason. Correct wrong answers in a different colour or a dated revision. Re-attempt weak questions after several days.
6. Keep integrated answers as project artefacts. Ask a domain expert to review advanced and industry-level answers when possible.
7. Use the answer key only after attempting the relevant question group. Answer criteria allow alternatives where business rules support them; a model answer is not the only acceptable model.

### Tags and scoring

- Every question has a unique ID, category, topic number, difficulty and question type.
- Suggested scoring: beginner 2 points; intermediate 3; advanced 4; industry application 6. Use the per-question criteria and partial-credit guidance in Section G.
- A high score cannot compensate for a critical semantic defect: incorrect grain, false key uniqueness, wrong cardinality, lost required history or a silent semantic contract change is a readiness blocker. This bank has been checked against the supplied roadmap and lesson files; it has not been statistically calibrated or validated on a learner cohort.

## Section B — Beginner questions

Terminology, abstraction levels, foundational entity/attribute identification and simple relationship interpretation.

### C01-01 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Modeling terminology and abstraction levels
- **Question:** Classify these statements as conceptual, logical, or physical: (a) a Customer may hold multiple Accounts; (b) Customer has CustomerID and LegalName; (c) CustomerID is VARCHAR(36) in PostgreSQL.
- **Your answer:**

---

### C01-02 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Beginner
- **Type:** explanation
- **Category:** Modeling terminology and abstraction levels
- **Question:** Explain why a conceptual model should not be treated as a database schema.
- **Your answer:**

---

### C01-03 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Modeling terminology and abstraction levels
- **Question:** A diagram shows Account, Customer and AccountHolding, but no attributes or data types. What level is it likely to represent, and what evidence could change your answer?
- **Your answer:**

---

### C02-01 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Entity and relationship identification
- **Question:** From “a customer may hold several accounts and each account can have several customers,” identify entities and relationship.
- **Your answer:**

---

### C02-02 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Beginner
- **Type:** error-detection
- **Category:** Entity and relationship identification
- **Question:** A proposed model treats LegalName as an entity and Customer as an attribute. Diagnose the likely modeling error.
- **Your answer:**

---

### C03-01 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Beginner
- **Type:** interpretation
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Interpret “each AccountHolding references exactly one Account; an Account has one or more AccountHolding records.” State min/max on both ends.
- **Your answer:**

---

### C03-02 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Beginner
- **Type:** multiple-choice
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Which best enforces uniqueness of a relationship record when one customer may hold one account in several different roles? A) unique CustomerID; B) unique AccountID; C) unique(CustomerID, AccountID); D) define a candidate key including role or holding identifier, based on whether roles may coexist.
- **Your answer:**

---

### C04-01 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Normalization and relational design
- **Question:** Given Account(AccountID, AccountTypeCode, AccountTypeName), with AccountTypeCode→AccountTypeName, identify the likely redundancy.
- **Your answer:**

---

### C04-02 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Beginner
- **Type:** explanation
- **Category:** Normalization and relational design
- **Question:** What is a functional dependency X→Y? Illustrate with Northbridge.
- **Your answer:**

---

### C05-01 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Beginner
- **Type:** definition
- **Category:** Fact-table grain and dimensional modeling
- **Question:** State the grain for a fact table recording posted account transactions.
- **Your answer:**

---

### C05-02 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Fact-table grain and dimensional modeling
- **Question:** Classify transaction amount, transaction count and account balance as additive, semi-additive or non-additive with caveats.
- **Your answer:**

---

### C06-01 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Historical modeling and Data Vault
- **Question:** Distinguish a current-state Customer table, a Type 2 historical dimension and a Data Vault satellite.
- **Your answer:**

---

### C06-02 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Beginner
- **Type:** explanation
- **Category:** Historical modeling and Data Vault
- **Question:** What is point-in-time reconstruction and why does load time alone not prove business validity?
- **Your answer:**

---

### C07-01 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Domain boundaries and event modeling
- **Question:** Classify CustomerAddressChanged as a domain event or technical CDC record and explain the distinction.
- **Your answer:**

---

### C07-02 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Domain boundaries and event modeling
- **Question:** Is “CustomerStatus” an entity, state, or event? Explain.
- **Your answer:**

---

### C08-01 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Schema evolution and compatibility
- **Question:** Using the convention stated here, define backward and forward compatibility: V2 reader with V1 data; V1 reader with V2 data.
- **Your answer:**

---

### C08-02 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Schema evolution and compatibility
- **Question:** A nullable optional field `preferred_contact_method` is added and old readers ignore unknown fields. Is it likely breaking?
- **Your answer:**

---

### C09-01 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Beginner
- **Type:** error-detection
- **Category:** Model review and naming standards
- **Question:** Which is preferable and why: `Cust`, `Customer`, or `customer_info` for a core entity?
- **Your answer:**

---

### C09-02 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Beginner
- **Type:** definition-writing
- **Category:** Model review and naming standards
- **Question:** Write a non-circular definition for Account.
- **Your answer:**

---

### C10-01 — Integrated model design and justification
- **Topics:** 1–2
- **Difficulty:** Beginner
- **Type:** model-construction
- **Category:** Integrated model design and justification
- **Question:** Sketch the conceptual entities and relationships for Northbridge onboarding, account holding and transaction posting. Label assumptions.
- **Your answer:**

---

### C10-02 — Integrated model design and justification
- **Topics:** 1
- **Difficulty:** Beginner
- **Type:** classification
- **Category:** Integrated model design and justification
- **Question:** For the same domain, give one conceptual, one logical and one physical decision and label each.
- **Your answer:**

---

## Section C — Intermediate questions

Model construction, cardinality, constraints, dependencies, dimensional grain, history, events and compatibility.

### C01-04 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Modeling terminology and abstraction levels
- **Question:** A team calls a diagram “logical” but it contains only boxes and unqualified lines. What review questions establish whether it is actually logical?
- **Your answer:**

---

### C01-05 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Intermediate
- **Type:** scenario-analysis
- **Category:** Modeling terminology and abstraction levels
- **Question:** Northbridge needs a shared meaning of Customer before selecting a platform. Which model should be agreed first and what should be deferred?
- **Your answer:**

---

### C02-03 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** model-construction
- **Category:** Entity and relationship identification
- **Question:** Create an entity inventory for onboarding and account opening using only supported scope.
- **Your answer:**

---

### C02-04 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** business-rule
- **Category:** Entity and relationship identification
- **Question:** Write two-direction relationship statements for Customer–AccountHolding–Account.
- **Your answer:**

---

### C02-05 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** ambiguity
- **Category:** Entity and relationship identification
- **Question:** The source says “customers own accounts.” What questions must be answered before using an Ownership relationship?
- **Your answer:**

---

### C03-03 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** model-construction
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Define a candidate key and a primary-key choice for AccountHolding where one customer may have multiple roles on one account over time.
- **Your answer:**

---

### C03-04 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** test-design
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Write one valid and one invalid test for a rule that every AccountHolding must reference an existing Customer and Account.
- **Your answer:**

---

### C03-05 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** A relationship is drawn as one-to-many, but no optionality is shown. What questions and artifacts resolve the defect?
- **Your answer:**

---

### C04-03 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Intermediate
- **Type:** decomposition
- **Category:** Normalization and relational design
- **Question:** Relation R(AccountID, AccountTypeCode, AccountTypeName) has FDs AccountID→AccountTypeCode and AccountTypeCode→AccountTypeName. Decompose and explain.
- **Your answer:**

---

### C04-04 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Normalization and relational design
- **Question:** A Transaction table stores CustomerName and CustomerAddress alongside CustomerID. Explain anomalies and propose a normalized alternative.
- **Your answer:**

---

### C04-05 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Intermediate
- **Type:** calculation
- **Category:** Normalization and relational design
- **Question:** A relation has 1,000 accounts, each with one AccountTypeCode; 10 codes occur. If AccountTypeName averages 30 bytes, how many repeated name copies are present beyond one per code?
- **Your answer:**

---

### C05-03 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Fact-table grain and dimensional modeling
- **Question:** A daily account balance fact is summed across 30 dates to report month-end balance. Diagnose.
- **Your answer:**

---

### C05-04 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Intermediate
- **Type:** model-construction
- **Category:** Fact-table grain and dimensional modeling
- **Question:** Design a minimal dimensional model for monthly posted transaction reporting. State grain first.
- **Your answer:**

---

### C05-05 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Intermediate
- **Type:** scenario-analysis
- **Category:** Fact-table grain and dimensional modeling
- **Question:** One transaction can allocate across several products. Why can joining transaction fact directly to product allocation duplicate amounts?
- **Your answer:**

---

### C06-03 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Intermediate
- **Type:** design-justification
- **Category:** Historical modeling and Data Vault
- **Question:** Northbridge must preserve source-provided customer legal-name changes from CRM and core banking. What historical design questions precede choosing Data Vault?
- **Your answer:**

---

### C06-04 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Historical modeling and Data Vault
- **Question:** A satellite stores customer name but has no source identity or load timestamp, and overwrites previous values. What requirements may be violated?
- **Your answer:**

---

### C06-05 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Intermediate
- **Type:** scenario-analysis
- **Category:** Historical modeling and Data Vault
- **Question:** Which structure is most suitable for current customer-name lookup versus reconstructing what a source reported on a past load date?
- **Your answer:**

---

### C07-03 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Intermediate
- **Type:** model-construction
- **Category:** Domain boundaries and event modeling
- **Question:** Draft a minimal CustomerAddressChanged event contract.
- **Your answer:**

---

### C07-04 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Intermediate
- **Type:** domain-boundary
- **Category:** Domain boundaries and event modeling
- **Question:** CRM says Customer means any prospect; core banking says Customer means an onboarded relationship. How should the model handle this?
- **Your answer:**

---

### C07-05 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Intermediate
- **Type:** error-detection
- **Category:** Domain boundaries and event modeling
- **Question:** A single global Customer table is owned by CRM but used to determine core banking eligibility. Identify the risk and alternative.
- **Your answer:**

---

### C08-03 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Intermediate
- **Type:** impact-analysis
- **Category:** Schema evolution and compatibility
- **Question:** A field `balance_amount` changes from whole currency units to minor units (e.g., 125 becomes 12500). Classify and plan.
- **Your answer:**

---

### C08-04 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Intermediate
- **Type:** scenario-analysis
- **Category:** Schema evolution and compatibility
- **Question:** A new enum value `SUSPENDED` is added. Why can an additive change break consumers?
- **Your answer:**

---

### C08-05 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Intermediate
- **Type:** plan
- **Category:** Schema evolution and compatibility
- **Question:** For a rename from `legal_name` to `registered_name`, create an expand-and-contract plan for five consumers. For each consumer state owner, field use, required action, deadline and validation evidence; draft a dated deprecation notice with the removal gate. Dates are scenario decisions that must be approved by the named owners, not universal defaults. Dates are scenario decisions that must be approved by the named owners, not universal defaults.
- **Your answer:**

---

### C09-03 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Intermediate
- **Type:** dictionary-completion
- **Category:** Model review and naming standards
- **Question:** List minimum useful dictionary fields for AccountStatusCode.
- **Your answer:**

---

### C09-04 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Intermediate
- **Type:** review-exercise
- **Category:** Model review and naming standards
- **Question:** Review `Acct.Bal` with definition “balance”; no currency, timing, source or owner. Identify defects and corrections.
- **Your answer:**

---

### C09-05 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Intermediate
- **Type:** classification
- **Category:** Model review and naming standards
- **Question:** Distinguish synonym, homonym and conformed concept using Customer/Client.
- **Your answer:**

---

### C10-03 — Integrated model design and justification
- **Topics:** 1–2
- **Difficulty:** Intermediate
- **Type:** model-construction
- **Category:** Integrated model design and justification
- **Question:** Write three rules, keys and two test cases for joint accounts.
- **Your answer:**

---

### C10-04 — Integrated model design and justification
- **Topics:** 2–3
- **Difficulty:** Intermediate
- **Type:** normalization
- **Category:** Integrated model design and justification
- **Question:** Given Account(AccountID, AccountTypeCode, AccountTypeName, CustomerID, CustomerName), identify likely decompositions and conditions.
- **Your answer:**

---

### C10-05 — Integrated model design and justification
- **Topics:** 1, 6
- **Difficulty:** Intermediate
- **Type:** trade-off
- **Category:** Integrated model design and justification
- **Question:** Northbridge asks for one “Customer” definition across CRM, cards and core banking. Recommend a semantic strategy.
- **Your answer:**

---

## Section D — Advanced questions

Ambiguity, alternatives, functional dependencies, history, domain boundaries, migration risk and structured review.

### C01-06 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Modeling terminology and abstraction levels
- **Question:** A logical model contains vendor-specific JSON types and index names. Explain the review concern and how to correct it without losing useful information.
- **Your answer:**

---

### C01-07 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Advanced
- **Type:** ambiguity
- **Category:** Modeling terminology and abstraction levels
- **Question:** The phrase “account customer” is used in a requirement. Give two plausible interpretations and the modeling consequence of each.
- **Your answer:**

---

### C02-06 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Advanced
- **Type:** model-construction
- **Category:** Entity and relationship identification
- **Question:** An AccountHolding role can change over time. Propose logical elements without designing a full history platform.
- **Your answer:**

---

### C02-07 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Advanced
- **Type:** error-detection
- **Category:** Entity and relationship identification
- **Question:** A model includes Customer, Person, Organisation, Client and CRMCustomer with no definitions. How do you review this inventory?
- **Your answer:**

---

### C03-06 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Advanced
- **Type:** constraint-analysis
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Requirement: a closed Account remains in the model, but a closed account cannot accept a new posted transaction. Where should this rule be represented?
- **Your answer:**

---

### C03-07 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Advanced
- **Type:** ambiguity
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Can Account have zero holders? Give two defensible rules and the impact on cardinality.
- **Your answer:**

---

### C04-06 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Advanced
- **Type:** dependency-analysis
- **Category:** Normalization and relational design
- **Question:** For R(AccountID, CustomerID, HoldingRole, RoleStartDate, RoleEndDate), propose plausible dependencies and identify what must be confirmed before declaring a key.
- **Your answer:**

---

### C04-07 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Normalization and relational design
- **Question:** A reporting team wants CustomerName duplicated into every transaction row for speed. Evaluate normalized and denormalized options.
- **Your answer:**

---

### C05-06 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Fact-table grain and dimensional modeling
- **Question:** Choose between periodic snapshot and transaction fact for a regulatory question asking month-end balances and all posted movements.
- **Your answer:**

---

### C05-07 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Advanced
- **Type:** SCD
- **Category:** Fact-table grain and dimensional modeling
- **Question:** Customer segment changes from Standard to Premium on 15 June. A report must show transactions attributed to the segment at transaction time. What dimension approach is suitable?
- **Your answer:**

---

### C06-06 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Historical modeling and Data Vault
- **Question:** Compare a Type 2 dimension with Data Vault for a regulated customer-history requirement.
- **Your answer:**

---

### C06-07 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Advanced
- **Type:** ambiguity
- **Category:** Historical modeling and Data Vault
- **Question:** Two systems assign different customer IDs to the same person. What must be resolved before designing a hub?
- **Your answer:**

---

### C07-06 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Domain boundaries and event modeling
- **Question:** A consumer needs immediate account-closure state, while event consumers may process asynchronously. Compare synchronous query and event-driven approaches.
- **Your answer:**

---

### C07-07 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Advanced
- **Type:** event-correctness
- **Category:** Domain boundaries and event modeling
- **Question:** An event stream delivers AccountClosed before AccountOpened due to replay from multiple partitions. What should the model/contract specify?
- **Your answer:**

---

### C08-06 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Advanced
- **Type:** compatibility-analysis
- **Category:** Schema evolution and compatibility
- **Question:** A new regulation makes `risk_review_date` mandatory for accounts opened on or after an announced effective date, but older accounts and older writers may omit it. Classify the change and explain the historical-data, producer, validation and rollout cases that must be resolved.
- **Your answer:**

---

### C08-07 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Advanced
- **Type:** trade-off
- **Category:** Schema evolution and compatibility
- **Question:** Choose between in-place type widening and versioned contract for a financial amount change.
- **Your answer:**

---

### C09-06 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Advanced
- **Type:** review-checklist
- **Category:** Model review and naming standards
- **Question:** Give review checks for keys, cardinality, normalization, history and schema evolution.
- **Your answer:**

---

### C09-07 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Advanced
- **Type:** defect-prioritization
- **Category:** Model review and naming standards
- **Question:** Classify: (a) wrong cardinality permits multiple active primary holders; (b) missing steward; (c) inconsistent capitalization.
- **Your answer:**

---

### C10-06 — Integrated model design and justification
- **Topics:** 1–5, 8
- **Difficulty:** Advanced
- **Type:** model-construction
- **Category:** Integrated model design and justification
- **Question:** Design an integrated model package for customer/account core data and monthly reporting.
- **Your answer:**

---

### C10-07 — Integrated model design and justification
- **Topics:** 3–5
- **Difficulty:** Advanced
- **Type:** architectural-decision
- **Category:** Integrated model design and justification
- **Question:** Compare normalized core model, dimensional mart, and Data Vault as the single solution for all Northbridge needs. Recommend.
- **Your answer:**

---

## Section E — Industry-application case studies

Integrated Northbridge Bank scenarios. Treat all added details as illustrative; label assumptions and unresolved rules.

### C01-08 — Modeling terminology and abstraction levels
- **Topic:** 1
- **Difficulty:** Industry application
- **Type:** design-justification
- **Category:** Modeling terminology and abstraction levels
- **Question:** Produce a short transformation rationale from Northbridge conceptual to logical model for multiple account holders with roles. State what is added at each level.
- **Your answer:**

---

### C02-08 — Entity and relationship identification
- **Topic:** 2
- **Difficulty:** Industry application
- **Type:** design-justification
- **Category:** Entity and relationship identification
- **Question:** Recommend whether Address should be an attribute or separate entity for Northbridge. Give alternatives and decision criteria.
- **Your answer:**

---

### C03-08 — Cardinality, optionality, keys and constraints
- **Topic:** 2
- **Difficulty:** Industry application
- **Type:** review-exercise
- **Category:** Cardinality, optionality, keys and constraints
- **Question:** Review a model where AccountHolding has no key, Account references CustomerID directly, and joint accounts are permitted. Identify defects and corrections.
- **Your answer:**

---

### C04-08 — Normalization and relational design
- **Topic:** 3
- **Difficulty:** Industry application
- **Type:** decomposition
- **Category:** Normalization and relational design
- **Question:** Given Customer(CustomerID, LegalName, AddressLine, City, PostalCode, AccountID, AccountTypeName), normalize it for multiple accounts/customer and multiple holders/account.
- **Your answer:**

---

### C05-08 — Fact-table grain and dimensional modeling
- **Topic:** 4
- **Difficulty:** Industry application
- **Type:** aggregation-test
- **Category:** Fact-table grain and dimensional modeling
- **Question:** Design valid/invalid tests for a fact with grain “one row per posted transaction line.”
- **Your answer:**

---

### C06-08 — Historical modeling and Data Vault
- **Topic:** 5
- **Difficulty:** Industry application
- **Type:** design-justification
- **Category:** Historical modeling and Data Vault
- **Question:** Propose a history approach for CustomerAddress and AccountHoldingRole, including point-in-time and consumer requirements.
- **Your answer:**

---

### C07-08 — Domain boundaries and event modeling
- **Topic:** 6
- **Difficulty:** Industry application
- **Type:** design-justification
- **Category:** Domain boundaries and event modeling
- **Question:** Design boundaries/events for account opening and account holding changes. State which are events and which are entities/state.
- **Your answer:**

---

### C08-08 — Schema evolution and compatibility
- **Topic:** 7
- **Difficulty:** Industry application
- **Type:** migration-design
- **Category:** Schema evolution and compatibility
- **Question:** Northbridge changes Account status semantics: `CLOSED` now includes dormant accounts, previously separate. Define a safe evolution plan.
- **Your answer:**

---

### C09-08 — Model review and naming standards
- **Topic:** 8
- **Difficulty:** Industry application
- **Type:** review-exercise
- **Category:** Model review and naming standards
- **Question:** Perform a compact review of Northbridge Customer–Account model with shared account holders, closed-account retention and name history.
- **Your answer:**

---

### C10-08 — Integrated model design and justification
- **Topics:** 1–8
- **Difficulty:** Industry application
- **Type:** integrated-case
- **Category:** Integrated model design and justification
- **Question:** Prepare an approval-ready design summary for Customer, Account, AccountHolding, Transaction and analytical reporting. Include scope, rules, assumptions, model, tests, history/evolution needs, dictionary and review plan.
- **Your answer:**

---

## Section F — Practical modeling exercises

These are portfolio-style exercises. They overlap intentionally with selected questions but require complete written artefacts rather than short responses. Use the Section G rubric and attach valid/invalid tests.

### F0 — Abstraction-level classification and transformation (Topic 1)

Classify each statement as **conceptual**, **logical**, or **physical**. Use the statement's content, not the diagram or file format. Score one point per correct answer; the roadmap gate is at least **18/20 (90%)**. Then identify which logical decisions still require business confirmation and which implementation decisions should be deferred.

1. The business tracks Customers and Accounts.
2. One Account may have several authorized holders.
3. Customer and Account are connected through an account-holding relationship.
4. The logical model defines `Account(AccountID, AccountStatus, ProductID)`.
5. `AccountID` uniquely identifies an Account in the logical model.
6. `AccountHolding` represents the many-to-many Customer–Account relationship.
7. Each AccountHolding refers to exactly one Account and one Customer, under the stated rule.
8. The logical dependency `AccountTypeCode → AccountTypeName` is recorded after code uniqueness is confirmed.
9. The logical model records a referential-integrity rule from `AccountHolding.AccountID` to `Account.AccountID`.
10. The logical model retains an Account row with `AccountStatus = CLOSED` rather than deleting it when the account closes.
11. The target platform is PostgreSQL.
12. `account_id` is stored as `VARCHAR(36)` in PostgreSQL.
13. A B-tree index is created on `account_holding.account_id`.
14. The transaction table is partitioned by posting month in the selected database.
15. The deployment uses a named tablespace for transaction data.
16. A PostgreSQL `CREATE TABLE` statement defines the physical `account_holding` table.
17. The physical schema uses `NUMERIC(19,4)` for a stored amount after precision and scale are approved.
18. The production workload has a query plan showing an index scan for the account lookup.
19. A physical migration adds an index concurrently to reduce write blocking.
20. The selected storage engine and backup configuration are documented for the deployment.

**Deliverable:** the 20-item answer sheet, score out of 20, a conceptual/logical model pair, and a list of deferred physical decisions.

### F1 — Business-rule register (Topics 1–2, 8)

Create at least 12 business rules for Party/Customer, Account, AccountHolding and Transaction. For each include rule ID, exact rule, source or assumption, model location, owner, test case and status. Include joint holding, lifecycle, identity, and an unresolved minor-holder rule.

### F2 — Entity and relationship inventory (Topics 1–2)

List candidate entities and definitions; mark each Confirm / Reject / Open. For every relationship write min/max in both directions, optionality, a valid case and an invalid case. Explain when an associative entity is required.

### F3 — Dependency and decomposition proof (Topic 3)

Normalize **three** supplied relations, stating assumptions, functional dependencies, candidate keys, normal-form violations, proposed decomposition, lossless-join reasoning, dependency preservation and referential integrity for each:

1. `AccountExample(AccountID, AccountTypeCode, AccountTypeName)` with candidate rules `AccountID → AccountTypeCode` and (only if business-confirmed) `AccountTypeCode → AccountTypeName`.
2. `AccountCustomerExample(AccountID, CustomerID, CustomerName, AccountTypeCode, AccountTypeName)` under confirmed assumptions `CustomerID → CustomerName`, `AccountID → AccountTypeCode`, and `AccountTypeCode → AccountTypeName`; state whether the row grain allows multiple holders.
3. `HoldingExample(AccountID, CustomerID, HoldingRole, EffectiveStartDate, EffectiveEndDate)` where key and uniqueness rules must be proposed rather than assumed; state the temporal/overlap rule needed before claiming a candidate key.

For each, explain the insertion, update or deletion anomaly addressed and supply at least one valid and one invalid test. The first relation is a worked starting point, not permission to assume a dependency the business has not confirmed.

### F4 — Dimensional model with grain (Topic 4)

Design a model for posted transaction reporting and month-end balances. State each fact grain first. Identify dimensions, measures, additive behavior, currency assumptions, snapshot requirements, SCD approach for historical customer segment and reconciliation tests. Create a business-question coverage matrix mapping each required business question to the fact/dimensions/calculation and a test or expected result. Also diagnose this flawed proposal: one fact table combines transaction-line rows and month-end account balances, sums daily balances across dates, and joins transaction amounts to a many-row product-allocation table without allocation grain or weights. Identify each defect and provide corrected structures and reconciliation tests.

### F5 — Historical design decision (Topic 5)

Compare effective-dated relational history, Type 2 dimension and Data Vault for customer legal name and account holding role. Requirements: source lineage, reconstruct source-reported values at load time, and report customer segment at transaction time. Provide a minimal hub/link/satellite sketch (or justify a simpler alternative), a point-in-time retrieval example with the requested valid/record times and expected result, and a decision record that selects one or more structures by requirement and explains why.

### F6 — Domain/event contract (Topic 6)

Define bounded contexts for CRM prospect, core banking customer and cards customer. Produce a context map, event catalogue and domain-to-event alignment table. Draft `AccountHoldingRoleChanged` event semantics, identity, time, producer, versioning, privacy, idempotency and ordering expectations. Distinguish it from a technical CDC record.

### F7 — Compatibility migration plan (Topic 7)

Create a change-classification table for add/remove/rename/retype/optionality/constraint/enum/semantic changes, stating producer and consumer versions and compatibility assumptions. Write a compatibility/deprecation policy with approval, notification, test and removal gates. Then plan a rename and semantic unit change for a financial amount. Inventory producers and consumers, state backward/forward compatibility convention, stage expansion, backfill, reader migration, validation, cutover, deprecation and rollback/forward-fix criteria. For a five-consumer rename, assign owner, required action and deadline to each consumer and draft a dated deprecation notice with a removal gate.

### F8 — Formal model review (Topic 8)

Review an intentionally flawed model with these defects: (1) one CustomerID directly on Account despite joint holding; (2) no AccountHolding key; (3) ambiguous `Bal`; (4) repeated AccountTypeName; (5) no FK constraints; (6) account may be orphaned without an explicit rule; (7) current-only LegalName despite history requirement; (8) status enum undocumented; (9) no source/owner in dictionary; (10) transaction grain unstated; (11) CRM prospect and bank customer conflated; (12) a field is renamed without migration plan. For each record location, defect type, severity, impact, correction, owner, acceptance test and status. Also state the naming standard used and provide corrected, non-circular dictionary entries for at least five affected elements.

### F9 — Integrated enterprise model package (Topics 1–8)

Prepare scope, assumptions/open questions, requirements traceability, glossary, naming standard, conceptual model description, logical entities/attributes/keys, relationship rules, normalization notes, analytical grain, history/event/evolution needs, data dictionary, review log and decision summary. State physical decisions explicitly deferred. Run at least 20 valid/invalid scenarios as the module project requires.

## Section G — Answer key and evaluation rubric

> **Use after attempting Sections B–F.** Answers below provide defensible criteria. Where a rule is unspecified, a good answer identifies the ambiguity instead of inventing a fact. Topic file references are relative to this module folder.

### C01-01 — Answer criteria
- **Model answer:** (a) conceptual relationship/rule; (b) logical attributes and identifier; (c) physical implementation.
- **Reasoning / principle:** Abstraction level depends on implementation specificity, not diagram style.
- **Partial credit:** This beginner question is capped at 2 points: all three classifications correct = 2; two correct = 1; one correct = 0.5; none correct = 0. Do not exceed the difficulty-based question maximum.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-02 — Answer criteria
- **Model answer:** It expresses business concepts and relationships without committing to columns, data types, indexes, storage or DDL.
- **Reasoning / principle:** A conceptual model aligns meaning; a logical model specifies implementable structure; physical design is a later concern.
- **Partial credit:** Credit clear distinction even if examples differ.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-03 — Answer criteria
- **Model answer:** Likely conceptual if entities are business concepts and relationship structure is high-level; it could be logical if AccountHolding is an associative entity with defined identifiers/attributes and precise rules.
- **Reasoning / principle:** Level cannot be inferred from absence of data types alone; inspect purpose and precision.
- **Partial credit:** Award credit for identifying ambiguity.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-04 — Answer criteria
- **Model answer:** Ask for attributes, candidate/primary keys, relationship cardinality and optionality, integrity constraints, resolved many-to-many relationships, and definitions.
- **Reasoning / principle:** A label does not establish model completeness.
- **Partial credit:** Partial credit for at least four criteria.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-05 — Answer criteria
- **Model answer:** Agree the conceptual model and definitions first; then transform to logical structure. Defer DBMS, physical types, indexes, partitioning, storage and DDL.
- **Reasoning / principle:** Avoid allowing platform constraints to prematurely define business meaning.
- **Partial credit:** Credit a justified alternative sequence if it preserves semantic agreement.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-06 — Answer criteria
- **Model answer:** Separate platform-neutral logical attributes/constraints from a physical implementation appendix or later physical model. Record implementation decisions as deferred or linked.
- **Reasoning / principle:** Logical portability and business semantics should remain distinguishable.
- **Partial credit:** Partial credit for separation and traceability.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-07 — Answer criteria
- **Model answer:** Could mean a customer who owns/holds an account (Customer—AccountHolding—Account), or a customer record maintained by the account system (a system-specific representation/role). Clarify domain meaning before modeling.
- **Reasoning / principle:** Ambiguous terms can change entity boundaries and relationship structure.
- **Partial credit:** Credit any two defensible readings and explicit question.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C01-08 — Answer criteria
- **Model answer:** Conceptual: Customer/Party, Account and holding relationship. Logical: stable identifiers, associative AccountHolding with CustomerID, AccountID, HoldingRole, start/end dates if justified, uniqueness and cardinality rules. Physical types remain deferred.
- **Reasoning / principle:** Logical transformation adds precision while preserving business meaning.
- **Partial credit:** Score semantics, keys, constraints and abstraction discipline.
- **Reference:** Topic 1 — `01-conceptual-logical-and-physical-models.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-01 — Answer criteria
- **Model answer:** Customer and Account are entities with a many-to-many holding relationship. At the conceptual level, that can be shown as an M:N relationship; in a relational logical model it must be represented through an associative relation such as `AccountHolding`, even if the relationship has no extra attributes. If role, effective dates or authority are tracked, those are attributes/rules of the association and may make `AccountHolding` a first-class business concept.
- **Reasoning / principle:** Do not model a many-to-many as an unexplained line in a relational logical model.
- **Partial credit:** Credit if association named clearly.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-02 — Answer criteria
- **Model answer:** LegalName is normally an attribute of a person/organization/customer role, while Customer is a business concept/entity. Separate name history only if requirements demand it.
- **Reasoning / principle:** Distinguish tracked things from properties; history can alter the design.
- **Partial credit:** Credit qualification for name history.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-03 — Answer criteria
- **Model answer:** Candidates: Party (person/organization), Customer role if needed by definition, Account, AccountHolding, Product, Branch, Address, Contact; Transaction if payment posting is in scope. Define and validate each rather than accepting every candidate automatically.
- **Reasoning / principle:** Roadmap lists candidates to investigate, not mandatory entities.
- **Partial credit:** Score definitions and explicit candidates to confirm/reject.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-04 — Answer criteria
- **Model answer:** One Customer may have zero or many AccountHolding records; each AccountHolding refers to exactly one Customer. One Account may have one or many holders if the stated illustrative rule is adopted; each AccountHolding refers to exactly one Account. Confirm whether account may temporarily have zero holders.
- **Reasoning / principle:** Both ends, minima and maxima must match business rules.
- **Partial credit:** Credit explicit unresolved assumption on minimum holders.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-05 — Answer criteria
- **Model answer:** Does “own” mean legal ownership, authorized operation, beneficial ownership or a system association? Can joint holders exist? Are roles/time periods tracked? Can a holder be an organization? Are there account types with no holder?
- **Reasoning / principle:** Terms can collapse distinct roles and legal concepts.
- **Partial credit:** Partial credit for semantic questions and structural impact.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-06 — Answer criteria
- **Model answer:** AccountHolding identifier or composite candidate key, CustomerID, AccountID, HoldingRole, effective start/end if requirements require history, constraints on valid interval and current-role uniqueness. Clarify whether each role period is a distinct holding record.
- **Reasoning / principle:** Relationship attributes can justify an associative entity; history requirements shape keys and constraints.
- **Partial credit:** Score key choice, time semantics and stated assumptions.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-07 — Answer criteria
- **Model answer:** Ask whether Party is a shared supertype with Person/Organisation subtypes, Customer a business role, Client a synonym or separate domain term, and CRMCustomer a source-system representation. Define ownership/context and remove or justify duplicates.
- **Reasoning / principle:** Names alone do not prove distinct business entities.
- **Partial credit:** Credit explicit context/ownership and decision log.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C02-08 — Answer criteria
- **Model answer:** Single current mailing address with no reuse/history may be attributes; multiple address types, shared addresses, effective dates, validation or address-level ownership justify Address plus CustomerAddress/association. State scope and history assumptions.
- **Reasoning / principle:** Model to requirements, not a universal rule.
- **Partial credit:** Score alternatives, conditions and trade-offs.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-01 — Answer criteria
- **Model answer:** AccountHolding→Account is exactly 1; Account→AccountHolding is 1..*.
- **Reasoning / principle:** Optionality and cardinality are directional.
- **Partial credit:** Full credit requires both directions.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-02 — Answer criteria
- **Model answer:** D. A stable `AccountHoldingID` is one defensible key; a composite candidate key may include CustomerID, AccountID and role or effective-period attributes if the business uniqueness/temporal rules justify them. A unique CustomerID (A) would incorrectly prevent one customer from holding several accounts. A unique AccountID (B) would incorrectly prevent joint holding. A unique `(CustomerID, AccountID)` pair (C) would prohibit multiple roles for the same pair if those roles may coexist. C is acceptable only if the business explicitly forbids multiple roles per pair and the pair is otherwise unique at the required time grain.
- **Reasoning / principle:** Constraints must encode the actual rule, not a familiar pattern.
- **Partial credit:** Credit C only if the learner states and justifies the no-multiple-roles assumption; otherwise full credit requires identifying why A, B and C are unsafe under the stated scenario.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-03 — Answer criteria
- **Model answer:** Possible candidate key: (AccountID, CustomerID, HoldingRole, EffectiveStartDate) if role-period uniqueness and precision are guaranteed; alternatively stable AccountHoldingID plus a business uniqueness constraint. Document interval overlap rules.
- **Reasoning / principle:** Key selection depends on the business uniqueness rule and temporal granularity.
- **Partial credit:** Score explicit assumptions and alternatives.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-04 — Answer criteria
- **Model answer:** Valid: holding references existing IDs. Invalid: CustomerID or AccountID does not exist; referential integrity must reject or quarantine it according to declared enforcement.
- **Reasoning / principle:** A model rule should be testable.
- **Partial credit:** Credit explicit expected outcome.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-05 — Answer criteria
- **Model answer:** Ask whether either side may exist without the other; write both-direction min/max statements, constraints, examples and test cases; update diagram and dictionary.
- **Reasoning / principle:** A line without min/max hides business rules.
- **Partial credit:** Partial credit for questions and written rules.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-06 — Answer criteria
- **Model answer:** Retain Account and lifecycle/status semantics; express the rule as a business constraint: new posted transaction must reference an eligible/open account at the relevant posting time. Define timing, reversals and exceptions; note enforcement layer if logical model cannot fully express it.
- **Reasoning / principle:** Entity retention and transaction eligibility are distinct rules.
- **Partial credit:** Score temporal precision and exception handling.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-07 — Answer criteria
- **Model answer:** If every opened account must always have at least one holder, Account→AccountHolding is 1..*. If draft/pre-opening or closure transition allows none, it may be 0..* or conditional by lifecycle state. State the lifecycle rule; do not assume.
- **Reasoning / principle:** Optionality follows business lifecycle.
- **Partial credit:** Credit both interpretations and consequences.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C03-08 — Answer criteria
- **Model answer:** Blocking/major: relationship cannot represent many-to-many joint holding; add AccountHolding. Define key/candidate uniqueness, FKs to Customer/Account, role and optional dates if needed, cardinality and tests.
- **Reasoning / principle:** The direct FK encodes at most one customer per account.
- **Partial credit:** Score structural diagnosis, corrected model and test.
- **Reference:** Topic 2 — `02-entities-relationships-cardinality-and-constraints.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-01 — Answer criteria
- **Model answer:** AccountTypeName repeats for each account of a type; separate AccountType(AccountTypeCode, AccountTypeName) and reference its key if the dependency/business semantics hold.
- **Reasoning / principle:** Functional dependencies expose repeated facts and update anomalies.
- **Partial credit:** Credit dependency explicitly.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-02 — Answer criteria
- **Model answer:** For every pair of valid rows, same X value implies same Y. Example AccountID→AccountStatus for a current-state Account relation, assuming one row per account and current status.
- **Reasoning / principle:** FDs are business assertions about uniqueness, not just observed sample data.
- **Partial credit:** Credit assumptions.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-03 — Answer criteria
- **Model answer:** `Account(AccountID, AccountTypeCode)` and `AccountType(AccountTypeCode, AccountTypeName)`. The original candidate key is `AccountID` under the stated FDs. The decomposition removes the transitive dependency and repeated type name. The common attribute `AccountTypeCode` is a key of `AccountType`, so the join is lossless; `AccountID → AccountTypeCode` is preserved in `Account` and `AccountTypeCode → AccountTypeName` in `AccountType`. Both decomposed relations satisfy BCNF under these FDs, provided no additional dependencies are omitted.
- **Reasoning / principle:** Check lossless join and preservation of dependencies.
- **Partial credit:** Partial credit for tables; full for reasoning.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-04 — Answer criteria
- **Model answer:** Names/addresses are customer facts, not transaction facts, unless intentionally snapshotted for transaction-time evidence. Keep Customer facts in Customer/Address structures; retain a snapshot only when required and label its temporal meaning.
- **Reasoning / principle:** Do not blindly normalize away legally required historical snapshots.
- **Partial credit:** Score anomalies and exception condition.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-05 — Answer criteria
- **Model answer:** Repeated copies beyond one canonical name per code = `1,000 account rows − 10 distinct codes = 990 copies`. At 30 bytes per name, the repeated name payload is `990 × 30 = 29,700 bytes` (about 29.0 KiB using 1,024 bytes/KiB), before row/encoding/index overhead. This assumes each of the 10 codes maps to exactly one name and every account has a code.
- **Reasoning / principle:** The arithmetic follows the stated cardinalities; storage savings are not the sole rationale.
- **Partial credit:** Full credit for assumptions and calculation.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-06 — Answer criteria
- **Model answer:** Possible surrogate HoldingID→all attributes. A business key might be (AccountID, CustomerID, HoldingRole, RoleStartDate), but only if start dates are unique at the required precision and overlapping same-role periods are forbidden. Confirm role coexistence, corrections and temporal semantics.
- **Reasoning / principle:** Do not infer keys from column names alone.
- **Partial credit:** Score plausible FD and explicit validation.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-07 — Answer criteria
- **Model answer:** Normalized transaction references Customer; reporting layer may denormalize/materialize a snapshot. Trade-offs: update consistency, query simplicity/performance, storage, historical truth and refresh lag. Define whether name is current or as-at-transaction.
- **Reasoning / principle:** Denormalization is a documented consumer requirement, not accidental duplication.
- **Partial credit:** Score alternatives, risks and temporal semantics.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C04-08 — Answer criteria
- **Model answer:** Separate Customer, Account, AccountHolding, and AccountType if dependencies support it; Address may be separate depending on multiplicity/history. State keys/FKs, FDs and lossless joins. AccountID cannot be a single Customer attribute under many-to-many holding.
- **Reasoning / principle:** Correct decomposition depends on actual business rules.
- **Partial credit:** Partial credit by valid decomposition, FDs and assumptions.
- **Reference:** Topic 3 — `03-normalization-and-relational-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-01 — Answer criteria
- **Model answer:** One row per posted transaction event/transaction line, whichever the source business process actually defines; specify line-level versus header-level explicitly.
- **Reasoning / principle:** Grain is the business definition of what one row represents.
- **Partial credit:** No credit for “transaction data” without row-level detail.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-02 — Answer criteria
- **Model answer:** Transaction amount is additive across valid dimensions/currency rules; count is additive when counting distinct fact rows at declared grain; account balance is generally semi-additive across time, not summed across dates. Currency conversion and duplicates matter.
- **Reasoning / principle:** Aggregation depends on grain and business meaning.
- **Partial credit:** Credit caveat about currencies/row grain.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-03 — Answer criteria
- **Model answer:** Wrong aggregation: balance is semi-additive across time. Select the final snapshot, use a defined period-end rule, or calculate an appropriate average; do not sum daily balances.
- **Reasoning / principle:** The measure type and reporting question determine aggregation.
- **Partial credit:** Credit a valid period-end method.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-04 — Answer criteria
- **Model answer:** Example grain: one row per posted transaction line. Fact has transaction amount and a countable row key; dimensions may include Date, Account, Product, Channel, Branch and TransactionType where valid. Add Customer only if attribution is defined without multiplying the transaction fact: a joint account may have multiple holders, so do not join every holder directly and sum the full transaction amount once per holder. Use a separately grained allocation/bridge with approved weights, report at account grain, or define another explicit attribution rule. Resolve currency and posting semantics.
- **Reasoning / principle:** Dimensions and measures follow the grain, not precede it.
- **Partial credit:** Score grain, measures, dimensions and caveats.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-05 — Answer criteria
- **Model answer:** A one-to-many join repeats the transaction amount for each allocation row. Use allocation-grain fact with allocated amount, or separate facts/bridge and explicit allocation weights; reconcile totals.
- **Reasoning / principle:** Join multiplicity can silently inflate measures.
- **Partial credit:** Full credit requires remedy and reconciliation test.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-06 — Answer criteria
- **Model answer:** Often both are needed: transaction fact captures movements; periodic snapshot captures balance at defined cut-off. They answer different questions and have different grains. Reconcile opening + movements = closing under stated rules.
- **Reasoning / principle:** No single fact table automatically answers both without derivation.
- **Partial credit:** Credit explicit date/cut-off and reconciliation.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-07 — Answer criteria
- **Model answer:** Type 2-style history with effective dates and surrogate version keys, or an equivalent temporal attribution structure. Fact rows reference the dimension version valid at transaction time. Handle late-arriving/corrected history.
- **Reasoning / principle:** Current-value overwrite loses historical attribution.
- **Partial credit:** Credit alternatives with temporal correctness.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C05-08 — Answer criteria
- **Model answer:** Valid: two lines for one transaction produce two fact rows with line identifiers and amounts; totals reconcile to posted lines. Invalid: duplicate same source line causes double count; pending/unposted event included when scope says posted only; aggregation across currencies without conversion is rejected/qualified.
- **Reasoning / principle:** Test the declared grain and inclusion rule.
- **Partial credit:** Score grain fidelity, reconciliation and invalid cases.
- **Reference:** Topic 4 — `04-dimensional-modeling-facts-dimensions-and-grain.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-01 — Answer criteria
- **Model answer:** Current-state table stores current values; Type 2 dimension stores business-facing historical versions with effective periods; satellite stores descriptive history linked to a hub/link and records source/load context according to the vault design.
- **Reasoning / principle:** These structures serve different purposes.
- **Partial credit:** Credit no claim that one universally replaces another.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-02 — Answer criteria
- **Model answer:** Reconstruct the value that was valid for the business time and available in the recorded/source history by the requested record/load time. Illustrative example: source load A recorded legal name `Mira Rao` on 2026-01-10; a correction loaded on 2026-02-05 says the corrected name `Mira R. Rao` was business-valid from 2026-01-01. For business-valid time 2026-01-15 as known on 2026-01-20, return `Mira Rao`; for the same business-valid time as known after 2026-02-05, return `Mira R. Rao`, assuming the source correction and its effective date are retained. Load time alone says when data arrived, not when the fact was business-valid; missing source history prevents a justified reconstruction.
- **Reasoning / principle:** Distinguish valid time and observation/load time.
- **Partial credit:** Partial credit if distinction clear.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-03 — Answer criteria
- **Model answer:** Need source lineage, source key stability, change capture, conflicting definitions, valid vs load time, point-in-time queries, retention, consumers and reconciliation. A hub may represent stable business key; satellites separate descriptive source/history; define source identity and hash/key policy.
- **Reasoning / principle:** Data Vault is a pattern chosen for integration/history needs, not default for every model.
- **Partial credit:** Score requirements before pattern selection.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-04 — Answer criteria
- **Model answer:** Lineage and historical capture are compromised; define source record/context, load timestamp, record source and history/change handling per chosen vault conventions. Overwrite loses history.
- **Reasoning / principle:** Vault implementation conventions must be explicit and fit requirements.
- **Partial credit:** Credit stated design convention.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-05 — Answer criteria
- **Model answer:** Current consumer layer may expose a current-state view; historical source reconstruction needs retained source-attributed history, such as satellites with load timestamps and appropriate PIT/query structures.
- **Reasoning / principle:** Consumer purpose and time semantics determine structure.
- **Partial credit:** Credit alternatives with caveat that PIT is a helper, not historical source itself.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-06 — Answer criteria
- **Model answer:** Type 2 offers direct consumer-friendly historical versions; Data Vault supports source-attributed integration/history and auditability. Choose based on source lineage, integration complexity, query needs, governance, skills and delivery cost; they may coexist.
- **Reasoning / principle:** Not mutually exclusive and not interchangeable in all use cases.
- **Partial credit:** Score trade-offs and downstream layer.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-07 — Answer criteria
- **Model answer:** Determine whether IDs are source keys or enterprise business keys, identity resolution/cross-reference policy, survivorship and matching governance, source lineage and split/merge correction. Avoid assuming a source ID is globally unique.
- **Reasoning / principle:** Stable identity is a business/governance issue, not merely a hash choice.
- **Partial credit:** Credit explicit cross-reference approach.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C06-08 — Answer criteria
- **Model answer:** Define required business and load time, source lineage, corrections, retention and point-in-time queries. Possible normalized effective-dated structures, Type 2 dimensions for analytical attribution, or Vault hub/link/satellite for source history, plus consumer view/PIT where needed.
- **Reasoning / principle:** Select per requirement; identify history source and consumer layer.
- **Partial credit:** Score alternatives, time semantics, lineage and risk.
- **Reference:** Topic 5 — `05-data-vault-and-historical-modeling.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-01 — Answer criteria
- **Model answer:** As phrased it is a candidate domain event if it states a business-significant fact; a CDC record merely says a source row changed. A domain event needs domain semantics, identity, time and contract.
- **Reasoning / principle:** A database mutation does not automatically equal a business event.
- **Partial credit:** Credit conditional wording.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-02 — Answer criteria
- **Model answer:** Usually a state attribute/value on a Customer role or lifecycle model; “CustomerStatusChanged” may be an event. A separate entity is justified only if statuses have independent identity/metadata/lifecycle.
- **Reasoning / principle:** Names and modeling context determine classification.
- **Partial credit:** Credit context-dependent qualification.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-03 — Answer criteria
- **Model answer:** Event ID, event type, occurred/effective time, customer/party identifier, address identity or new address payload per consumer need, producer/domain, schema version, correlation/causation where relevant, privacy classification and semantics. Avoid unnecessary sensitive fields.
- **Reasoning / principle:** Contract includes meaning and evolution expectations, not only JSON shape.
- **Partial credit:** Partial credit for identity/time/meaning/version/privacy.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-04 — Answer criteria
- **Model answer:** Define bounded contexts and distinct concepts/roles (e.g., Prospect and BankCustomer or Party plus lifecycle/relationship), map them explicitly and assign owners. Do not force one enterprise definition without agreed semantics.
- **Reasoning / principle:** Same word can be a homonym across domains.
- **Partial credit:** Credit a conformed Party concept if distinctions remain explicit.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-05 — Answer criteria
- **Model answer:** Ownership and meaning mismatch; CRM prospect data may not satisfy bank-customer eligibility semantics. Define domain ownership, authoritative attributes, conformed identity and explicit integration/eligibility contract.
- **Reasoning / principle:** One table is not proof of one semantic authority.
- **Partial credit:** Credit clear ownership and contract.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-06 — Answer criteria
- **Model answer:** Synchronous authoritative query can provide current decision at cost of coupling/latency/availability; events decouple and support propagation but introduce lag, duplicates and ordering concerns. For critical eligibility, define freshness/consistency SLA and safe fallback.
- **Reasoning / principle:** Architecture must align with business criticality.
- **Partial credit:** Score alternatives, risks and guardrails.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-07 — Answer criteria
- **Model answer:** Define per-account ordering key/partition strategy where required, event time vs processing time, sequence/version or aggregate revision, idempotency, replay semantics and consumer handling of gaps. Do not assume global order.
- **Reasoning / principle:** Ordering guarantees must be explicit and scoped.
- **Partial credit:** Credit mitigation and no global-order assumption.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C07-08 — Answer criteria
- **Model answer:** Entities/state: Account, Party/Customer role, AccountHolding and current status. Events: AccountOpened, AccountHoldingAdded/RoleChanged/Removed when domain-significant. Define owner, payload, time, idempotency, privacy, schema evolution and cross-context mapping.
- **Reasoning / principle:** Events record facts; entities represent things and state is current condition.
- **Partial credit:** Score distinctions, boundaries, contract and risks.
- **Reference:** Topic 6 — `06-event-modeling-and-domain-driven-design.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-01 — Answer criteria
- **Model answer:** Backward compatibility: new reader V2 can read old V1 data. Forward compatibility: old reader V1 can read new V2 data. Full compatibility supports both directions. State the convention because usage varies.
- **Reasoning / principle:** Compatibility is directional and convention-sensitive.
- **Partial credit:** Full credit requires both directions.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-02 — Answer criteria
- **Model answer:** Usually additive/non-breaking under those assumptions, but verify validators, generated clients, strict schemas and consumer behavior.
- **Reasoning / principle:** Compatibility depends on contracts and actual consumers, not field change alone.
- **Partial credit:** Credit conditions.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-03 — Answer criteria
- **Model answer:** Semantic breaking change even if the numeric storage type stays the same. In the stated example, `12,500 minor units ÷ 100 = 125 whole currency units` only under the explicitly implied two-decimal currency convention; do not hard-code a factor of 100 across currencies without a currency-specific exponent rule. Create an explicit new field/version or coordinated migration; identify consumers, conversion, dual-read/write period, reconciliation, cutover and rollback/forward-fix.
- **Reasoning / principle:** Units/meaning are part of the contract.
- **Partial credit:** Score semantic classification and migration.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-04 — Answer criteria
- **Model answer:** Consumers may use exhaustive switches, reject unknown values, or map to unsafe defaults. Test tolerant readers, update code lists/contracts, deploy readers before producers or version if consumers cannot tolerate it.
- **Reasoning / principle:** Syntactic addition does not guarantee operational compatibility.
- **Partial credit:** Credit explicit consumer order.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-05 — Answer criteria
- **Model answer:** Inventory five consumers by name/owner, field use, criticality, required action and deadline. Add `registered_name` while preserving `legal_name`; define one authoritative write path or controlled dual-write with reconciliation; backfill only from an approved mapping; migrate and test each reader; monitor parity and unresolved consumers; publish a dated deprecation notice with support contact/owner, migration instructions, deadline, removal date or decision date, and rollback/extension path. A notice should state: **Published:** `[approved YYYY-MM-DD]`; **Owner/contact:** `[named owner]`; **Deprecated field:** `legal_name`; **Replacement:** `registered_name`; **Consumer action:** update mappings and pass the named contract test; **Migration deadline:** `[approved YYYY-MM-DD]`; **earliest removal:** `[approved YYYY-MM-DD, only after gate]`; **removal gate:** all five consumers migrated or formally waived, parity/reconciliation checks pass, and approver signs off. The submitted exercise must replace all placeholders with dates and named owners agreed for its scenario. Remove the old field only after the gate is approved.
- **Reasoning / principle:** Rename is generally breaking without staged transition.
- **Partial credit:** Credit rollback and ownership.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-06 — Answer criteria
- **Model answer:** The rule applies to accounts opened on/after the effective date; it does not automatically imply older accounts must be backfilled. Confirm how opening date/time is determined, how historical/reopened/migrated accounts are treated, whether old writers can create post-effective-date accounts without the field, and how validation is enforced. Deploy compatible readers/validation first, update all writers before or by the effective date, reject or quarantine non-compliant new accounts according to policy, test boundary dates/time zones, monitor exceptions and define rollback/forward-fix. It is breaking for any producer/consumer or stored-record contract that cannot meet the new requiredness rule; compatibility is conditional on the explicit scope and rollout.
- **Reasoning / principle:** Requiredness is both data and producer contract change.
- **Partial credit:** Score existing data and old producers.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-07 — Answer criteria
- **Model answer:** Widening can preserve numeric values only if units/precision/scale and consumer types remain compatible; versioned contract is safer for semantic/unit change. Compare consumer inventory, accuracy, cost, regulatory traceability and migration complexity.
- **Reasoning / principle:** Type compatibility is not semantic compatibility.
- **Partial credit:** Credit alternative conditions.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C08-08 — Answer criteria
- **Model answer:** Semantic change requires new explicit definition/value or version; assess reports, regulatory extracts, eligibility, history and event consumers; backfill/reclassify only with approved rule; dual mapping/transition; reconcile, test edge cases, document effective date and rollback/forward fix.
- **Reasoning / principle:** Same code with new meaning silently corrupts interpretation.
- **Partial credit:** Score semantics, consumers, history, tests and governance.
- **Reference:** Topic 7 — `07-schema-evolution-and-backward-compatibility.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-01 — Answer criteria
- **Model answer:** Use a consistent singular business noun such as Customer, unless repository standards prescribe another convention. Avoid unexplained abbreviations and vague `_info` suffixes.
- **Reasoning / principle:** Names should be meaningful and consistent, not merely short.
- **Partial credit:** Credit adherence to local standards.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-02 — Answer criteria
- **Model answer:** Example: “A banking arrangement under which the bank records balances and postings for one or more authorized holders under agreed product and lifecycle terms.” State exclusions such as card authorization if out of scope.
- **Reasoning / principle:** Definition explains meaning and scope, not just repeats the name.
- **Partial credit:** Credit inclusion/exclusion clarity.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-03 — Answer criteria
- **Model answer:** Element name, business definition, technical description where needed, level/type where appropriate, constraints, allowed values and meanings, source, owner/steward, history/temporal notes, related entity, sensitivity/quality rules and traceability.
- **Reasoning / principle:** Dictionary completeness is assessed against scope and governance needs.
- **Partial credit:** Partial credit for core definition/values/owner/source.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-04 — Answer criteria
- **Model answer:** Naming/documentation defects: unexplained abbreviation, ambiguous measure, missing currency and as-of/posted semantics, source and ownership. Rename to e.g. `AccountBalanceAmount` only if standard supports; define balance basis, currency, timestamp, source and owner.
- **Reasoning / principle:** A cosmetic rename cannot resolve semantic ambiguity alone.
- **Partial credit:** Score severity based on risk, actionable correction.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-05 — Answer criteria
- **Model answer:** Synonym: two terms same meaning in one context. Homonym: same word different meanings across contexts. Conformed concept: explicitly agreed reusable meaning and mapping across domains, with context and ownership preserved.
- **Reasoning / principle:** Conformance is governed agreement, not forced sameness.
- **Partial credit:** Credit examples and contextual caveat.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-06 — Answer criteria
- **Model answer:** Verify stable/candidate keys and uniqueness; both-direction min/max and optionality; FDs/decomposition/lossless joins; history/valid time/lineage needs; compatibility definitions, affected consumers, migrations and rollback; trace every rule to requirements and tests.
- **Reasoning / principle:** Review is evidence-based and iterative.
- **Partial credit:** Partial credit across categories.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-07 — Answer criteria
- **Model answer:** (a) blocking or major depending legal/operational impact; typically blocking if invalid model could misrepresent legal ownership. (b) major if accountability is required for approval, otherwise minor/open governance item. (c) minor unless it creates machine/tooling ambiguity. State criteria.
- **Reasoning / principle:** Severity depends impact and gate, not defect label alone.
- **Partial credit:** Credit justified conditional severity.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C09-08 — Answer criteria
- **Model answer:** Findings should include association for many-to-many; stable IDs and FKs; holding role/cardinality/optionality; retain closed accounts and define status; name history requirement and valid-time/source; definitions, ownership/source and unresolved minor-holder rule; tests and traceability.
- **Reasoning / principle:** Review should separate confirmed facts from assumptions and reopen earlier modules as needed.
- **Partial credit:** Score actionable findings with location, impact, severity, owner and correction.
- **Reference:** Topic 8 — `08-model-review-naming-standards-and-data-dictionaries.md`; roadmap concepts in the matching topic and Section 6 assessment strategy.

### C10-01 — Answer criteria
- **Model answer:** Candidates Party (person/organisation), Customer role if defined, Account, AccountHolding, Product, Branch, Transaction, Address/Contact where justified. Write rules and identify unresolved terms; no physical types.
- **Reasoning / principle:** Candidates are investigated, not automatically accepted.
- **Partial credit:** Score scope and semantics.
- **Reference:** Integrated assessment — Topics 1–2; relevant source(s): `01-conceptual-logical-and-physical-models.md` and `02-entities-relationships-cardinality-and-constraints.md`. See the detailed traceability matrix below.

### C10-02 — Answer criteria
- **Model answer:** Conceptual: an Account may have several holders. Logical: AccountHolding with identifiers and constraints. Physical: column types/indexes in a named DBMS, explicitly deferred in the project.
- **Reasoning / principle:** Keep levels separate.
- **Partial credit:** Credit clear examples.
- **Reference:** Integrated assessment — Topic 1; relevant source(s): `01-conceptual-logical-and-physical-models.md`. See the detailed traceability matrix below.

### C10-03 — Answer criteria
- **Model answer:** Rules include each holding references one party and one account; account may have multiple holders; roles and optionality explicitly assumed. Keys use stable IDs and association key/business uniqueness. Valid joint holding accepted; nonexistent FK or duplicate prohibited combination rejected.
- **Reasoning / principle:** Model must express and test rules.
- **Partial credit:** Score two-direction rules, key and tests.
- **Reference:** Integrated assessment — Topics 1–2; relevant source(s): `01-conceptual-logical-and-physical-models.md` and `02-entities-relationships-cardinality-and-constraints.md`. See the detailed traceability matrix below.

### C10-04 — Answer criteria
- **Model answer:** Separate AccountType if code determines name; separate Customer if ID determines name; resolve many-to-many holders with AccountHolding if joint accounts allowed. Keep snapshots only if required by transaction-time evidence.
- **Reasoning / principle:** Use FDs and business rules rather than mechanical splitting.
- **Partial credit:** Credit dependency reasoning.
- **Reference:** Integrated assessment — Topics 2–3; relevant source(s): `02-entities-relationships-cardinality-and-constraints.md` and `03-normalization-and-relational-modeling.md`. See the detailed traceability matrix below.

### C10-05 — Answer criteria
- **Model answer:** Define bounded contexts and mappings; establish shared Party identity only where agreement exists; distinguish prospect/customer/account-holder roles; govern conformed concepts and attribute authority.
- **Reasoning / principle:** One global word should not erase domain differences.
- **Partial credit:** Score ownership and mappings.
- **Reference:** Integrated assessment — Topics 1 and 6; relevant source(s): `01-conceptual-logical-and-physical-models.md` and `06-event-modeling-and-domain-driven-design.md`. See the detailed traceability matrix below.

### C10-06 — Answer criteria
- **Model answer:** Core normalized logical model plus a dimensional design with explicit fact grain, dimensions/measures and history attribution; link each design to requirements and consumers; separate history/source integration structures if justified.
- **Reasoning / principle:** Operational model and analytical model serve different questions.
- **Partial credit:** Score separation, grain and traceability.
- **Reference:** Integrated assessment — Topics 1–5 and 8; relevant source(s): `01-conceptual-logical-and-physical-models.md`, `02-entities-relationships-cardinality-and-constraints.md`, `03-normalization-and-relational-modeling.md`, `04-dimensional-modeling-facts-dimensions-and-grain.md`, `05-data-vault-and-historical-modeling.md`, and `08-model-review-naming-standards-and-data-dictionaries.md`. See the detailed traceability matrix below.

### C10-07 — Answer criteria
- **Model answer:** Reject “one structure fits all” without evidence. Normalized model supports operational consistency; dimensional mart supports analytics; Vault can support source-attributed historical integration. Choose layers based on requirements, costs, governance and consumers; they may coexist.
- **Reasoning / principle:** Patterns are complementary, not universal substitutes.
- **Partial credit:** Score alternatives, risks and justified scope.
- **Reference:** Integrated assessment — Topics 3–5; relevant source(s): `03-normalization-and-relational-modeling.md`, `04-dimensional-modeling-facts-dimensions-and-grain.md`, and `05-data-vault-and-historical-modeling.md`. See the detailed traceability matrix below.

### C10-08 — Answer criteria
- **Model answer:** Must include traceable requirements, defined concepts, entities/attributes/keys, relationship min/max, constraints, FDs/normalization, analytical grain, history/event requirements within scope, compatibility plan, dictionary, review findings/owners, open questions and deferred physical decisions.
- **Reasoning / principle:** An approval-ready model is an auditable package, not a diagram alone.
- **Partial credit:** Use rubric in Section G; partial credit requires explicit assumptions and risks.
- **Reference:** Integrated assessment — Topics 1–8; relevant source(s): all eight topic files, as applicable to the proposed package. See the detailed traceability matrix below.

### Practical exercise answer criteria (F0–F9)

#### F0 — Abstraction-level classification and transformation
- **Expected answer key:** 1 conceptual; 2 conceptual business rule; 3 conceptual relationship; 4 logical entity/attribute structure; 5 logical candidate-key rule; 6 logical associative entity; 7 logical relationship constraint; 8 logical functional dependency; 9 logical referential-integrity rule; 10 logical lifecycle/status structure; 11 physical platform choice; 12 physical vendor-specific type; 13 physical index; 14 physical partitioning; 15 physical tablespace; 16 physical DDL; 17 physical storage type/precision choice; 18 physical query-plan evidence; 19 physical deployment/migration technique; 20 physical storage/backup configuration.
- **Scoring:** 1 point per correct item; at least 18/20 is the roadmap gate. If a learner disputes a classification, award an exception only where the statement genuinely admits another level and the learner justifies the context; these 20 statements are deliberately phrased to have one expected classification.
- **Common failure:** Treating a logical key or business constraint as physical solely because a DBMS may enforce it, or putting vendor-specific implementation choices in the conceptual model.

### Practical exercise answer criteria (F1–F9)

#### F1 — Business-rule register
- **Expected answer:** At least 12 atomic, testable rules. Each has a unique ID, traceable source or explicitly labelled assumption, model location, accountable owner, valid/invalid test and status. Joint holding and lifecycle rules must not be left implicit; the minor-holder rule remains open until an authorized business decision is recorded.
- **Common failure:** Writing vague rules such as “accounts are valid” without a condition or test.

#### F2 — Entity and relationship inventory
- **Expected answer:** Candidate entities are defined without circularity and accepted/rejected/open decisions are justified. Relationships have both-direction min/max, optionality, rule source, and tests. AccountHolding resolves the many-to-many customer/account relationship if joint holding is confirmed.
- **Common failure:** Treating every noun as an entity or drawing unqualified lines.

#### F3 — Dependency and decomposition proof
- **Expected answer:** Complete all three relations with explicit assumptions, FDs, candidate keys, normal-form analysis, decomposition, lossless-join reasoning, dependency preservation and FK rules. For `AccountExample`, decompose into `Account(AccountID, AccountTypeCode)` and `AccountType(AccountTypeCode, AccountTypeName)` only if `AccountTypeCode → AccountTypeName` is a confirmed business rule; the shared `AccountTypeCode` is a key of `AccountType`, so the join is lossless, and both stated FDs are preserved. For `AccountCustomerExample`, assuming one row per `(AccountID, CustomerID)` pair, the candidate key is that pair. Decompose to `Account(AccountID, AccountTypeCode)`, `AccountType(AccountTypeCode, AccountTypeName)`, `Customer(CustomerID, CustomerName)` and `AccountHolding(AccountID, CustomerID)`. Under the stated FDs, the joins are lossless because each intersection (`AccountID`, `AccountTypeCode`, or `CustomerID`) is a key of one joined component; each FD is preserved in a component. Under only the stated FDs, the four decomposed components are in BCNF; any additional business dependencies must be checked separately. If the grain includes multiple roles or periods per pair, extend the relation grain and re-derive keys/FDs instead of reusing this key. For `HoldingExample`, do not claim a natural key or normal form until role coexistence, timestamp precision, FD assumptions and interval-overlap rules are specified; a stable `AccountHoldingID` plus validated business uniqueness may be appropriate. Interval non-overlap is a temporal constraint, not automatically an FD. Each relation includes at least one valid and one invalid test.
- **Common failure:** Decomposing without stated FDs/proofs, treating sample data as proof of a dependency, or preserving a single CustomerID on Account despite joint accounts.

#### F4 — Dimensional model with grain
- **Expected answer:** Grain statement comes first (for example, one row per posted transaction line). Include a coverage matrix linking each business question to the relevant fact, dimensions/calculation and validation evidence. Keep transaction movements and month-end balance snapshots at separate grains; measures follow each grain; amount additivity is qualified by currency and posting rules; account balances are not summed across dates; month-end snapshots use a clear cut-off; historical segment attribution uses a suitable effective-dated/SCD approach. Diagnose the mixed-grain fact, daily-balance summation and allocation fan-out, then show corrected structures and reconciliation tests.
- **Common failure:** Choosing dimensions/measures before grain, mixing transaction and snapshot rows, or joining one-to-many allocations in a way that duplicates amounts.

#### F5 — Historical design decision
- **Expected answer:** Compare at least effective-dated relational history, Type 2 dimension and Data Vault against the stated needs. Include a hub/link/satellite model or a reasoned simpler alternative; distinguish valid time from load/record time; show a point-in-time retrieval example with an expected result; preserve source lineage and handle corrections/late arrival; explain transaction-time segment attribution and consumer usability. Example: if a source value `Mira Rao` was loaded on 2026-01-10 and a correction loaded on 2026-02-05 states the corrected name `Mira R. Rao` was valid from 2026-01-01, the query for business time 2026-01-15 as known on 2026-01-20 returns `Mira Rao`; the same business time as known after 2026-02-05 returns `Mira R. Rao`, assuming the source history was retained. A hybrid is acceptable if each layer has a defined purpose.
- **Common failure:** Claiming Data Vault is mandatory, treating load time as business-valid time, or assuming a current-state table preserves history.

#### F6 — Domain/event contract
- **Expected answer:** Provide a context map, event catalogue and domain-to-event alignment table. Define CRM prospect versus bank customer bounded contexts and mappings/ownership. Event contract includes business meaning, event identity/type, entity identity, occurred/effective time as required, producer, version, privacy, idempotency and ordering/replay expectations. Explain how this differs from a raw CDC change record.
- **Common failure:** Treating a database row update as a domain event without semantic validation.

#### F7 — Compatibility migration plan
- **Expected answer:** Provide a compatibility/deprecation policy plus the requested change-classification table with explicit compatibility direction and producer/consumer versions; inventory readers/writers and criticality; for the five-consumer rename assign owner, field use, required action, deadline and validation evidence to each; include a dated deprecation notice with migration instructions and a removal gate. For the unit change, include expand, backfill/conversion, compatible producer/reader migration, parity/reconciliation tests, monitoring, cutover, deprecation and rollback/forward-fix.
- **Common failure:** Calling a unit change non-breaking because the storage type is unchanged, or removing the old field before consumer migration is verified.

#### F8 — Formal model review
- **Expected answer:** Each of the 12 listed defects has location, defect type, severity with impact rationale, correction, owner, acceptance test and status. State the naming conventions applied and provide at least five corrected dictionary entries with non-circular business definitions, source/owner and relevant constraints/history notes. The direct CustomerID-on-Account design is a structural defect for joint holding; missing keys/FKs are structural; ambiguous `Bal` is semantic/documentation; duplicated AccountTypeName suggests normalization concerns; missing history and migration are requirement/evolution defects. Severity must reflect impact and gate criteria.
- **Common failure:** Cosmetic comments without actionable correction or priority.

#### F9 — Integrated enterprise model package
- **Expected answer:** Complete traceability from requirements to rules, conceptual and logical structures, naming standard, dictionary and tests; explicit keys/cardinality/optionality; dependency and normalization rationale; analytical grain where applicable; history/event/evolution implications; assumptions/open questions with owners; review finding closure evidence; physical decisions listed as deferred; at least 20 valid/invalid scenario results.
- **Common failure:** Submitting a diagram without rules, dictionary, tests or unresolved-question log.

### Rubric for practical exercises and integrated answers

| Criterion | 0 — Missing/unsafe | 1 — Partial | 2 — Strong |
|---|---|---|---|
| Semantic correctness | Terms/rules conflict or are invented | Mostly right; ambiguity partly recorded | Definitions, inclusions/exclusions and assumptions are explicit and validated |
| Structural correctness | Keys/cardinality/grain invalid | Structure plausible but important constraints absent | Keys, relationships, min/max, constraints and grain align with rules |
| Normalization and dependencies | No dependency reasoning or lossy design | Some dependencies recognized | Dependencies stated; decomposition justified and join/preservation reasoning supplied |
| History and events | Current state conflated with history/events | Some time/source distinctions | Valid/load time, lineage, state/event and consumer needs explicitly distinguished |
| Evolution and risk | Compatibility asserted without evidence | Some consumers/migration steps | Directional compatibility, consumer inventory, staged migration, tests and rollback considered |
| Traceability/documentation | No source/owner/test links | Partial dictionary or traceability | Rules link to requirements, model, dictionary, owner and test |
| Architectural judgment | One option asserted | Alternatives named without weighing | Alternatives, trade-offs, risks and conditions support recommendation |
| Reviewability | Vague findings; no closure evidence | Findings actionable but ownership/status incomplete | Location, type, severity, impact, correction, owner, acceptance test and status provided |

**Scoring cap and partial credit:** The difficulty-based maximum is a hard cap per question (beginner 2, intermediate 3, advanced 4, industry application 6). If a question has multiple subparts, award partial credit proportionally within that cap; never add per-subpart points on top of the cap. Qualitative partial-credit notes guide the judgement, while explicit numeric rules (such as C01-01) control where supplied. Keep the earned points and the Correct / Partly correct / Incorrect judgement as separate fields. For portfolio exercises F1–F9, score each of the eight rubric criteria 0–2 (maximum 16 per exercise; 144 points total if all nine are completed), then record critical defects separately. F0 is separate: 20 classification items, with at least 18/20 required for the Topic 1 gate. Do not let a numeric score waive a blocking defect. A semantic or structural defect that invalidates the model must be corrected even if the numeric score is high.

### Coverage matrix — assessment item to roadmap topic

| Roadmap topic | Category | Question IDs | Practical exercise | Completion evidence |
|---|---|---|---|---|
| Topic 1: Modeling terminology and abstraction levels | Modeling terminology and abstraction levels | C01-01, C01-02, C01-03, C01-04, C01-05, C01-06, C01-07, C01-08 | F0, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 2: Entity and relationship identification | Entity and relationship identification | C02-01, C02-02, C02-03, C02-04, C02-05, C02-06, C02-07, C02-08 | F2, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 2: Cardinality, optionality, keys and constraints | Cardinality, optionality, keys and constraints | C03-01, C03-02, C03-03, C03-04, C03-05, C03-06, C03-07, C03-08 | F2, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 3: Normalization and relational design | Normalization and relational design | C04-01, C04-02, C04-03, C04-04, C04-05, C04-06, C04-07, C04-08 | F3, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 4: Fact-table grain and dimensional modeling | Fact-table grain and dimensional modeling | C05-01, C05-02, C05-03, C05-04, C05-05, C05-06, C05-07, C05-08 | F4, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 5: Historical modeling and Data Vault | Historical modeling and Data Vault | C06-01, C06-02, C06-03, C06-04, C06-05, C06-06, C06-07, C06-08 | F5, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 6: Domain boundaries and event modeling | Domain boundaries and event modeling | C07-01, C07-02, C07-03, C07-04, C07-05, C07-06, C07-07, C07-08 | F6, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 7: Schema evolution and compatibility | Schema evolution and compatibility | C08-01, C08-02, C08-03, C08-04, C08-05, C08-06, C08-07, C08-08 | F7, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Topic 8: Model review and naming standards | Model review and naming standards | C09-01, C09-02, C09-03, C09-04, C09-05, C09-06, C09-07, C09-08 | F8, F9 | Answers demonstrate topic-specific reasoning; see readiness checklist. |
| Cross-topic: Integrated model design and justification (Topics 1–8) | Integrated model design and justification | C10-01, C10-02, C10-03, C10-04, C10-05, C10-06, C10-07, C10-08 | F1, F9 | A traceable integrated package, supported by relevant topic artefacts and tests; questions alone do not satisfy project gates. |

### Roadmap learning-objective traceability (Section 4)

This matrix maps each Module 1–8 learning-objective group to assessment evidence. The IDs identify relevant questions, not proof that a learner has passed. Topic-specific practical artefacts and independent review remain necessary where the completion gate requires them.

| Roadmap module objective | Assessment questions | Practical evidence / validation |
|---|---|---|
| **1.1 — Explain the purpose of data modeling** | C01-01, C01-02, C01-05, C10-01, C10-08 | F1, F9: scope, consumers, business rules and traceability. |
| **1.1 — Distinguish conceptual, logical and physical models by detail, audience and use** | C01-01–C01-08, C10-02 | F0, F9: reviewed conceptual/logical pair and deferred physical decisions. |
| **1.1 — Connect models to requirements and architecture decisions** | C01-05, C01-06, C10-01, C10-08 | F1, F9: requirement-to-rule-to-model traceability and decision summary. |
| **1.1 — Define boundaries, scope, assumptions and consumers** | C01-05, C01-07, C02-05, C10-08 | F1, F9: assumptions/open-question register with owners. |
| **1.1 — Maintain traceability across levels** | C01-06, C01-08, C09-06, C10-08 | F1, F9: traceability links reviewed. |
| **1.1 — Recognize modeling artefacts and their purposes** | C01-04, C01-06, C09-03, C09-06 | F1, F8, F9: glossary, rules register, dictionary and review log. |
| **2.1 — Define entities, attributes and identifiers with business meaning** | C02-01–C02-03, C02-07, C09-01–C09-03 | F2, F8, F9: entity inventory with definitions and key rationale. |
| **2.1 — Model 1:1, 1:M and M:N relationships** | C02-01, C02-04, C02-05, C03-01–C03-03, C03-08 | F2, F9: relationship inventory and model. |
| **2.1 — State cardinality and optionality precisely** | C03-01, C03-04, C03-05, C03-07, C03-08 | F2, F9: both-direction min/max and valid/invalid cases. |
| **2.1 — Choose candidate/primary keys and explain referential integrity** | C03-02–C03-04, C03-08, C04-06 | F2, F3, F9: candidate-key rationale, FKs and tests. |
| **2.1 — Represent business rules and resolve ambiguity** | C02-05, C03-05–C03-07, C09-06, C09-08 | F1, F2, F8, F9: rule register and ambiguity log. |
| **2.1 — Use associative entities** | C02-01, C02-04, C02-06, C03-02, C03-03, C03-08 | F2, F9: AccountHolding key, role and relationship rules. |
| **2.1 — Validate against real scenarios** | C03-04, C03-06–C03-08, C10-03 | F2, F9: valid/invalid test outcomes. |
| **3.1 — Express logical models in relational terms** | C04-01–C04-04, C04-08 | F3: relations, attributes, keys and FKs. |
| **3.1 — Explain redundancy and insertion/update/deletion anomalies** | C04-01, C04-04, C04-05, C04-07 | F3, F8: anomaly register tied to dependencies. |
| **3.1 — Identify functional dependencies** | C04-02–C04-04, C04-06, C04-08 | F3: explicit FD set and assumptions. |
| **3.1 — Apply 1NF, 2NF, 3NF and BCNF as covered** | C04-03, C04-06–C04-08, C10-04 | F3: normalization steps and dependency analysis. |
| **3.1 — Decompose without losing information or dependencies** | C04-03, C04-06, C04-08 | F3: lossless-join and dependency-preservation reasoning. |
| **3.1 — Evaluate denormalization trade-offs** | C04-04, C04-07, C10-07 | F3, F9: denormalization record, consistency mechanism and evidence. |
| **4.1 — Explain the purpose of dimensional modeling** | C05-04, C05-06, C10-06 | F4: dimensional model with business-question mapping. |
| **4.1 — Define facts, dimensions, measures and dimensional attributes** | C05-01, C05-04, C05-06, C05-08 | F4: dimensional model with business-question mapping. |
| **4.1 — State fact grain before dimensions/measures** | C05-01, C05-04–C05-08, C10-06 | F4, F9: explicit grain sentence for every fact. |
| **4.1 — Classify additive, semi-additive and non-additive measures** | C05-02, C05-03, C05-05, C05-06 | F4: aggregation rules and reconciliation tests. |
| **4.1 — Design star schemas, conformed dimensions and SCDs** | C05-04–C05-07, C10-06 | F4: dimensions, SCD decision and historical attribution. |
| **4.1 — Distinguish transaction, periodic snapshot and accumulating snapshot facts** | C05-01, C05-03, C05-06 | F4: separate grains and appropriate measures. |
| **4.1 — Explain incorrect-grain and join consequences** | C05-03, C05-05, C05-08 | F4: flawed-model diagnosis and fan-out tests. |
| **5.1 — Explain historical data and auditability** | C06-01, C06-02, C06-04–C06-08 | F5: temporal requirements and point-in-time retrieval. |
| **5.1 — Describe Data Vault purpose and characteristics** | C06-01, C06-03, C06-06, C06-08 | F5: justified comparison with simpler alternatives. |
| **5.1 — Describe hubs, links and satellites** | C06-01, C06-03, C06-04, C06-08 | F5: hub/link/satellite model or justified alternative. |
| **5.1 — Model business keys, relationships and changing descriptive data** | C06-03, C06-04, C06-07, C06-08 | F5: source identity, relationships and satellite/history semantics. |
| **5.1 — Distinguish historical capture from consumer models** | C06-01, C06-05, C06-06 | F5, F9: consumer-facing view and source-history design. |
| **5.1 — Weigh complexity, lineage, auditability and maintainability** | C06-03, C06-06–C06-08, C10-07 | F5: decision record with simpler alternative and costs. |
| **5.1 — Decide suitability of a historical approach** | C06-03, C06-05–C06-08 | F5: selection criteria and rationale. |
| **6.1 — Relate business domains to data models** | C07-04, C07-05, C10-05, C10-08 | F6: context map and ownership. |
| **6.1 — Define domain boundaries and domain language** | C07-04, C07-05, C10-05, C10-08 | F6: context map, glossary and ownership. |
| **6.1 — Model business events and meaningful state changes** | C07-01–C07-03, C07-07, C07-08 | F6: event catalogue and contract. |
| **6.1 — Distinguish entities, state and events** | C07-01, C07-02, C07-08 | F6: event-to-entity mapping. |
| **6.1 — Reason about cross-domain ownership and consistency** | C07-04–C07-06, C10-05 | F6: producer/consumer ownership and translation boundary. |
| **6.1 — Relate events to domain architecture and data products** | C07-03–C07-06, C07-08 | F6, F9: event contract, consumers and data-product boundary where applicable. |
| **6.1 — Handle concept/event evolution and ambiguous boundaries** | C07-04–C07-07, C08-08 | F6, F7: ownership decisions and evolution plan. |
| **7.1 — Explain why schemas change** | C08-02, C08-05, C08-06, C08-08 | F7: change classification table and change rationale. |
| **7.1 — Classify add/remove/rename/retype/optionality/constraint/meaning changes** | C08-02–C08-08 | F7: change classification table. |
| **7.1 — Define backward/forward compatibility** | C08-01, C08-02, C08-04, C08-06–C08-08 | F7: compatibility convention and tested producer/consumer directions. |
| **7.1 — Perform producer/consumer impact analysis** | C08-03–C08-08, C09-06 | F7: five-consumer inventory with owners, actions and deadlines. |
| **7.1 — Plan versioning, migration and safe rollout** | C08-03, C08-05–C08-08 | F7: staged transition, backfill, reconciliation and rollback/forward-fix. |
| **7.1 — Test and validate schema changes** | C08-03–C08-08 | F7: compatibility/contract tests and parity evidence. |
| **7.1 — Link evolution to model governance** | C08-05, C08-08, C09-06, C09-07 | F7, F8: approval, deprecation notice and change record. |
| **8.1 — Explain model-review purpose** | C09-04, C09-06–C09-08 | F8: review log with actionable findings. |
| **8.1 — Apply consistent naming standards** | C09-01, C09-04, C09-05, C09-08 | F8: naming standard applied across model and dictionary. |
| **8.1 — Produce business definitions and data dictionary** | C09-02–C09-05, C10-08 | F8, F9: corrected dictionary entries. |
| **8.1 — Review completeness, consistency and semantic accuracy** | C09-04–C09-08 | F8: at least ten defects classified and corrected. |
| **8.1 — Validate keys, relationships, constraints and rules** | C09-06–C09-08, C03-08 | F2, F8, F9: findings linked to rule tests. |
| **8.1 — Run review, issue resolution, approval and maintenance** | C09-06–C09-08 | F8, F9: owner, severity, status, acceptance test and approval evidence. |
| **8.1 — Communicate to business and technical audiences** | C01-04, C09-02, C09-03, C10-08 | F9: business-readable definitions and implementation-neutral logical model. |

### Completion-gate evidence matrix (roadmap Sections 4.12–8.12)

**Important:** The questions and answer key are assessment evidence, not substitutes for the required model artefacts, tests or independent reviews. Mark a gate complete only after its stated evidence exists and has been reviewed.

| Module gate | Relevant questions | Required completion evidence beyond answering questions | Gate status |
|---|---|---|---|
| **1 — Abstraction levels** | C01-01–C01-08, C10-01–C10-02 | F0: 20-item level classification scored ≥18/20; conceptual/logical model pair reviewed with no level violations; complete justified deferred-decision list; topic questions corrected. | ☐ Not assessed |
| **2 — Entities and relationships** | C02-01–C02-08, C03-01–C03-08 | Reviewed ER model; every relationship has both-direction min/max and optionality; valid/invalid tests pass; ambiguity log complete; topic questions corrected. | ☐ Not assessed |
| **3 — Normalization** | C04-01–C04-08, C10-04 | F3: three relations normalized with FDs/proofs; review exercise ties each defect to a dependency/anomaly; denormalization record includes risk, consistency mechanism and evidence; topic questions corrected. | ☐ Not assessed |
| **4 — Dimensional modeling** | C05-01–C05-08, C10-06 | F4: flawed mixed-grain/fan-out proposal diagnosed; every fact has an explicit grain sentence; business-question coverage matrix maps each question to a model/calculation and test; topic questions corrected. | ☐ Not assessed |
| **5 — Historical modeling** | C06-01–C06-08, C10-07 | F5: hub/link/satellite model or justified simpler alternative; worked point-in-time retrieval reviewed; decision record compares at least one simpler alternative; topic questions corrected. | ☐ Not assessed |
| **6 — Event modeling** | C07-01–C07-08, C10-05, C10-08 | F6 context map, event catalogue and domain-to-event alignment table reviewed; every event has past-tense name, owner, identity, time and subject; topic questions corrected. | ☐ Not assessed |
| **7 — Schema evolution** | C08-01–C08-08, C09-06 | F7: change classification table, five-consumer plan with owners/deadlines, dated notice, compatibility/deprecation policy and impact analysis reviewed; at least one semantic-change case explicitly handled; topic questions corrected. | ☐ Not assessed |
| **8 — Model review** | C09-01–C09-08, C10-08 | Findings are actionable/prioritized; at least five corrected dictionary entries pass a non-circularity check; naming standard is documented and applied consistently; topic questions corrected. | ☐ Not assessed |

## Section H — Readiness and remediation checklist

### Performance record

| Assessment category / roadmap topic | Questions attempted | Correct | Partial | Incorrect | Main defect pattern | Remediation action | Re-test date |
|---|---:|---:|---:|---:|---|---|---|
| Topic 1: Modeling terminology and abstraction levels | ____ | ____ | ____ | ____ | ____ | Revisit Topic 1 lesson and redo related exercise | ____ |
| Topic 2: Entity and relationship identification | ____ | ____ | ____ | ____ | ____ | Revisit Topic 2 lesson and redo related exercise | ____ |
| Topic 2: Cardinality, optionality, keys and constraints | ____ | ____ | ____ | ____ | ____ | Revisit Topic 2 lesson and redo related exercise | ____ |
| Topic 3: Normalization and relational design | ____ | ____ | ____ | ____ | ____ | Revisit Topic 3 lesson and redo related exercise | ____ |
| Topic 4: Fact-table grain and dimensional modeling | ____ | ____ | ____ | ____ | ____ | Revisit Topic 4 lesson and redo related exercise | ____ |
| Topic 5: Historical modeling and Data Vault | ____ | ____ | ____ | ____ | ____ | Revisit Topic 5 lesson and redo related exercise | ____ |
| Topic 6: Domain boundaries and event modeling | ____ | ____ | ____ | ____ | ____ | Revisit Topic 6 lesson and redo related exercise | ____ |
| Topic 7: Schema evolution and compatibility | ____ | ____ | ____ | ____ | ____ | Revisit Topic 7 lesson and redo related exercise | ____ |
| Topic 8: Model review and naming standards | ____ | ____ | ____ | ____ | ____ | Revisit Topic 8 lesson and redo related exercise | ____ |
| Integrated model design and justification (Topics 1–8) | ____ | ____ | ____ | ____ | ____ | Revisit weak topic lessons; revise integrated package and retest | ____ |

### Topic mastery and completion gates

### Topic 1
- [ ] **Mastery:** Can distinguish conceptual, logical and physical levels; trace concepts through transformation; keep physical decisions deferred in the module project.
- [ ] **Remediation if unchecked:** Complete F0 and reach ≥18/20; reclassify any missed items and rewrite the conceptual-to-logical rationale.

### Topic 2
- [ ] **Mastery:** Entity definitions, stable identifiers, relationship statements in both directions, cardinality, optionality and constraints are explicit and tested.
- [ ] **Remediation if unchecked:** Rebuild entity/relationship inventory; add valid and invalid tests.

### Topic 3
- [ ] **Mastery:** Functional dependencies, candidate keys, normalization/decomposition and trade-offs are justified; denormalization is intentional.
- [ ] **Remediation if unchecked:** Write FDs and redo decomposition with join/dependency reasoning.

### Topic 4
- [ ] **Mastery:** Every fact has an explicit grain before dimensions/measures; additivity, SCD and snapshot/coverage requirements are correct.
- [ ] **Remediation if unchecked:** Restate grain and test totals against transaction/snapshot examples.

### Topic 5
- [ ] **Mastery:** History requirements, source lineage, valid/load time, point-in-time reconstruction and consumer layer are distinguished; Data Vault use is justified.
- [ ] **Remediation if unchecked:** Compare at least two history approaches against requirements.

### Topic 6
- [ ] **Mastery:** Bounded contexts, ownership, entities/state/events and technical CDC are distinguished; event contracts state semantics and delivery assumptions.
- [ ] **Remediation if unchecked:** Map conflicting terms and rewrite event contract.

### Topic 7
- [ ] **Mastery:** Compatibility direction is stated; consumer impact, semantic changes, staged migration, tests and rollback/forward fix are planned.
- [ ] **Remediation if unchecked:** Reclassify changes and create a consumer-by-consumer migration matrix.

### Topic 8
- [ ] **Mastery:** Naming and definitions are consistent; dictionary complete for scope; findings are actionable, prioritized, owned and closed with evidence.
- [ ] **Remediation if unchecked:** Re-run model checklist and revise glossary/dictionary from findings.

### Suggested readiness thresholds

Calculate each level percentage as earned points divided by the maximum available points for questions attempted at that level; record omitted questions separately rather than treating them as correct. The 80 short questions contain 21 beginner questions, 29 intermediate questions, 20 advanced questions and 10 industry-application questions; at the default caps, the corresponding maximums are 42, 87, 80 and 60 points (269 total). F0 is a separate 20-point completion-gate exercise. F1–F9 have a separate 144-point practical rubric if all nine are completed. These counts and caps are assessment-design choices, not externally validated norms.

- **Beginner readiness:** at least 80% of beginner points and no recurring confusion between conceptual/logical/physical levels or entities/attributes.
- **Intermediate readiness:** at least 75% of intermediate points, with correct relationship min/max, keys, dependency reasoning and grain statements.
- **Advanced readiness:** at least 70% of advanced points and all major architectural recommendations include assumptions, alternatives, risks and tests.
- **Industry-project readiness:** at least 80% of practical rubric points, all eight topic gates checked, and **zero unresolved blocking defects** in semantic meaning, keys/cardinality, fact grain, required history, or breaking schema evolution.
- Thresholds are recommended self-assessment guidance; the module roadmap’s substantive completion gate and reviewer judgment take precedence over a score alone.

### Final enterprise project readiness checklist

- [ ] Scope, exclusions, assumptions and open questions have owners/status; physical design is deferred.
- [ ] Every core entity has a non-circular business definition and stable identifier strategy.
- [ ] Every relationship has both-direction statements, min/max, optionality, constraints and valid/invalid tests.
- [ ] Functional dependencies and decomposition decisions are documented; any denormalization has an explicit rationale.
- [ ] Any dimensional design states grain first and verifies aggregation/additivity.
- [ ] History, lineage, valid/load time, events and domain ownership needs are identified without expanding beyond scope.
- [ ] Schema evolution has a stated compatibility convention, consumer inventory and migration/rollback plan.
- [ ] Glossary, naming standard and dictionary are consistent and traceable to requirements, sources and owners/stewards.
- [ ] Review findings are classified as blocking/major/minor, actionable, assigned, tested and closed or formally accepted.
- [ ] At least 20 valid/invalid scenarios have been run, with outcomes and corrections recorded.
- [ ] Review findings have been propagated back to earlier topics where necessary; glossary, model, dictionary and tests are in sync.
- [ ] Final package contains a decision summary, unresolved items, deferred physical decisions and independent review evidence.

### Final self-assessment decision

- [ ] **Ready:** all critical gates pass; no unresolved blocking defects; remaining issues are minor, owned and documented.
- [ ] **Conditionally ready:** no blocking defects, but major gaps have a named owner and remediation date approved by the reviewer.
- [ ] **Not yet ready:** any critical semantic, structural, grain, history or compatibility defect remains unresolved, or the model cannot be independently reviewed.

Do not mark the module complete solely because every question has an answer. Completion requires a coherent, traceable model package whose rules can be tested and independently reviewed.
