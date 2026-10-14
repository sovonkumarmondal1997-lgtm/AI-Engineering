# Retention, Deletion, and GDPR Compliance

> **Stage 2 → Python for Data Engineering**  
> **Module 2.20 → Observability, Lineage, Governance, and Security**  
> **Topic 09 → Retention, Deletion, and GDPR Compliance**

## 1. Learning Objectives

By completing this module, you should be able to:

- explain the complete data lifecycle from collection through deletion;
- design retention policies by dataset, purpose, owner, classification, residency, and end action;
- implement retention controls across databases, partitions, object storage, Kafka, logs, quarantine systems, caches, warehouses, and derived datasets;
- explain GDPR from a practical Data Engineering and privacy-engineering perspective;
- understand data-subject rights, especially access, rectification, restriction, portability, objection, and erasure;
- resolve a canonical subject identity across multiple systems;
- use catalogs and lineage to discover direct and derived copies of personal data;
- design an idempotent, auditable, end-to-end erasure workflow;
- reason about Bronze/Silver/Gold, warehouse history, caches, Kafka, ML features, training data, test data, replicas, and backups;
- understand legal holds and residency constraints;
- generate technical deletion evidence and deletion certificates without treating them as legal proof by themselves;
- build automated retention and erasure tests;
- inject failures and debug partial deletion;
- design privacy-by-design data platforms.

### Legal and engineering boundary

This is an engineering learning module, **not legal advice**. GDPR, CCPA/CPRA, HIPAA, India's DPDP Act, and other privacy regimes contain jurisdiction- and organization-specific requirements. This module focuses on engineering implications. Where a legal conclusion depends on jurisdiction, contract, policy, or facts, **validate the requirement with the organization's privacy/legal team**.

---

## 2. Why Data Retention Matters

Data retention defines how long data or a governed copy should remain available and what happens when that period ends.

Retention exists for legitimate business, operational, security, analytical, contractual, regulatory, and legal purposes. The engineering mistake is not retention itself; it is **uncontrolled retention**.

### Why indefinite retention is dangerous

Indefinite storage increases:

1. **Security exposure** — every additional copy is another attack surface.
2. **Privacy exposure** — stale personal data can remain after its original purpose has ended.
3. **Cost** — storage, backup, indexing, replication, and observability costs accumulate.
4. **Operational complexity** — old schemas and datasets become harder to govern.
5. **Discovery burden** — deletion requests become harder when the number of copies grows.
6. **Incident impact** — an old forgotten copy can become part of a security incident.
7. **Governance debt** — nobody may know who owns the data or why it still exists.

### Retention is a platform capability

A production platform should not depend on an engineer remembering to run:

```sql
DELETE FROM customers WHERE customer_id = '...';
```

Instead, retention and deletion should be capabilities built into the platform:

```text
Policy
  ↓
Inventory
  ↓
Retention Evaluation
  ↓
Deletion Plan
  ↓
Execution
  ↓
Verification
  ↓
Evidence
```

---

## 3. Data Lifecycle Fundamentals

A useful lifecycle model is:

```text
Create
  ↓
Collect
  ↓
Ingest
  ↓
Store
  ↓
Process
  ↓
Use
  ↓
Share
  ↓
Archive
  ↓
Delete
```

### Why data has a lifecycle

Data changes operational state over time:

- newly collected data may be active;
- processed data may become analytical;
- old data may become archival;
- data whose purpose has ended may become eligible for deletion;
- a legal hold may temporarily prevent normal deletion.

The lifecycle should therefore be explicit rather than accidental.

### Four reasons deletion matters

**Operational:** reduces storage and system complexity.

**Security:** reduces the amount of sensitive information an attacker could obtain.

**Privacy:** supports data minimization and storage-limitation objectives where applicable.

**Compliance/governance:** allows the organization to implement approved retention policies and privacy controls.

---

## 4. Retention Policies

A retention policy answers:

> **What data should exist, for what purpose, for how long, under whose ownership, and what happens when retention ends?**

A useful policy model contains:

| Field | Meaning |
|---|---|
| Dataset | Governed data asset |
| Purpose | Why it is processed |
| Owner | Responsible team |
| Classification | Sensitivity/security classification |
| Retention period | Organization-defined period |
| Retention start | Event from which retention is measured |
| Retention trigger | Condition that starts the clock |
| End action | Delete, archive, anonymize, aggregate, etc. |
| Legal hold allowed | Whether normal deletion can be suspended |
| Residency | Approved geographic constraints |
| Exception | Approved deviation |

### Retention metadata

```yaml
dataset: customer_orders
purpose: order_fulfillment
classification: confidential
retention_period: organization-defined
retention_owner: data-platform
end_action: delete
legal_hold_allowed: true
residency:
  allowed_regions:
    - organization-defined
```

Do not turn an illustrative value into a universal legal requirement. Retention periods are policy decisions based on purpose, legal/business requirements, risk, and governance.

### SQL representation

```sql
CREATE TABLE retention_policies (
    dataset_name         TEXT PRIMARY KEY,
    purpose              TEXT NOT NULL,
    classification       TEXT NOT NULL,
    retention_period_days INTEGER,
    retention_owner      TEXT NOT NULL,
    end_action            TEXT NOT NULL,
    legal_hold_allowed   BOOLEAN NOT NULL DEFAULT FALSE,
    residency_policy      TEXT,
    effective_at         TIMESTAMPTZ NOT NULL
);
```

A production system may store policies in a governance repository and deploy them as policy-as-code.

---

## 5. Retention by Dataset and Purpose

Different datasets can legitimately have different retention behavior.

```text
Raw events
  → organization-defined short operational window

Operational records
  → organization-defined business/legal policy

Application logs
  → short operational window

Audit/security logs
  → organization-defined governance/security requirement

Temporary quarantine
  → short controlled window

Analytics aggregates
  → purpose-dependent
```

There is no universal retention number that applies to every organization or dataset.

### Retention by purpose

The same person's information can participate in different processing purposes:

```text
Customer information
       |
       +-- Billing
       |
       +-- Product analytics
       |
       +-- Fraud investigation
       |
       +-- Marketing
```

Engineering metadata should make purpose explicit because retention, access, downstream use, and deletion planning can depend on it.

### Purpose limitation

A mature platform asks:

- Why was this data collected?
- Is the current processing consistent with the declared purpose?
- Has a new purpose been introduced?
- Is the secondary use governed?
- Is all copied data still necessary?

Purpose metadata should travel with the dataset rather than live only in a document no pipeline can inspect.

---

## 6. Retention End Actions

When retention expires, possible actions include:

```text
Delete
Archive
Anonymize
Aggregate
Destroy encryption keys
Quarantine
```

These are not interchangeable.

### Delete

Remove governed copies according to the approved deletion policy.

### Archive

Move data into a controlled archival system when continued retention is authorized.

### Anonymize

Transform data so that it is no longer treated as identifiable under the organization's applicable privacy analysis. The engineering and legal determination is context-dependent.

### Aggregate

Reduce detailed records into aggregates. Aggregation does **not automatically** mean that privacy obligations disappear.

### Destroy encryption keys

Crypto-shredding can make encrypted data computationally inaccessible, but it is a technique with limitations, not a universal substitute for deletion.

### Quarantine

Temporarily isolate data when an operational or governance workflow requires controlled preservation.

---

## 7. Storage and Lifecycle Controls

Retention has to be enforced where data actually exists.

A platform inventory should identify:

```text
Database
Object storage
Lakehouse
Warehouse
Kafka
Logs
Traces
Metrics
Quarantine
Cache
Feature store
ML training data
Backups
Replicas
Development/Test
BI extracts
```

A retention policy that exists only in a spreadsheet but is not enforced at these boundaries is a governance intention, not a reliable control.

---

## 8. Database Retention

Database retention can use:

- row deletion;
- partition deletion;
- archival tables;
- scheduled deletion jobs;
- TTL-style mechanisms where supported;
- soft deletes;
- hard deletes;
- foreign-key cascades;
- application-level cleanup.

### Soft delete

```sql
UPDATE customers
SET deleted_at = CURRENT_TIMESTAMP
WHERE customer_id = 'customer-123';
```

Soft deletion keeps the row but marks it inactive.

### Hard delete

```sql
DELETE FROM customers
WHERE customer_id = 'customer-123';
```

Hard deletion removes the row from the current logical table, subject to database storage, indexes, replicas, backups, history, and platform-specific behavior.

### When soft delete is insufficient

If a privacy workflow requires actual removal from a governed system, a `deleted_at` flag does not automatically accomplish that. Soft deletion can also leave:

- indexes;
- replicas;
- exports;
- caches;
- analytical copies;
- backups;
- audit artifacts containing personal fields.

The correct design depends on the organization's policy and applicable requirements.

---

## 9. Partition-Based Retention

Partitioning can turn a large deletion problem into a metadata/storage operation.

Example:

```text
events_2026_01
events_2026_02
events_2026_03
```

If an entire partition is eligible for deletion:

```text
Retention expires
       ↓
Check legal hold / exceptions
       ↓
Drop or replace old partition
       ↓
Verify storage reclamation
       ↓
Record evidence
```

Partition deletion is often much more efficient than scanning millions of rows.

### Engineering considerations

- partition key;
- retention boundary;
- indexes;
- vacuum/cleanup behavior;
- storage reclamation;
- replication;
- downstream consumers;
- verification.

A partition should not be deleted merely because its timestamp looks old. Evaluate policy, purpose, holds, and exceptions first.

---

## 10. Object Storage Lifecycle

Object storage adds several complications:

- lifecycle rules;
- expiration;
- archival tiers;
- object versioning;
- delete markers;
- replication;
- retention locks;
- object metadata.

A critical principle is:

> **Deleting the current object does not necessarily mean every version or replica has disappeared.**

### Versioning example

```text
customer.json
customer.json (version A)
customer.json (version B)
delete marker
```

A current listing can appear clean while older versions remain governed storage.

### Lifecycle design

```text
Object Created
   ↓
Active
   ↓
Retention Eligible
   ↓
Check Hold / Exception
   ↓
Expire or Archive
   ↓
Verify
```

Platform-specific semantics differ, so durable architecture should explicitly model versioning and replication rather than assume `DELETE object` means universal physical disappearance.

---

## 11. Kafka and Event Retention

Kafka retention includes concepts such as:

- topic retention;
- time-based retention;
- size-based retention;
- partitions;
- offsets;
- tombstones;
- compaction.

Kafka retention is **not equivalent to data-subject deletion**.

For example:

```text
Customer event
     ↓
Kafka topic
     ↓
Consumer A → warehouse
Consumer B → feature store
Consumer C → cache
```

Deleting or expiring an event from Kafka does not automatically remove copies already consumed downstream.

### Tombstones and compaction

Compaction can help represent the latest state for keyed records, but it is not a general-purpose deletion mechanism for every historical event and every downstream copy.

### Production question

Always ask:

> If this event disappears from Kafka today, which systems have already persisted its contents?

That question exposes the real erasure surface.

---

## 12. Log and Observability Retention

Govern retention for:

- application logs;
- pipeline logs;
- audit logs;
- security logs;
- traces;
- metrics.

### PII in logs

Bad:

```python
logger.info("Customer email=%s failed payment", email)
```

Better:

```python
logger.info(
    "Payment failed",
    extra={"customer_ref": internal_request_id}
)
```

Observability systems should minimize sensitive fields and use approved identifiers.

### Log controls

A production design should include:

- redaction;
- structured logging;
- restricted access;
- retention policy;
- deletion/expiration;
- controlled log aggregation;
- correlation IDs that do not expose unnecessary PII.

Logs can become part of an erasure workflow if they contain governed personal information.

---

## 13. Quarantine and Temporary Data Retention

A common pipeline pattern is:

```text
Pipeline
   ↓
Validation
   ↓
Failed record
   ↓
Quarantine
```

Quarantine data is often forgotten because it is not considered a primary dataset.

It should have:

- limited retention;
- restricted access;
- encryption;
- deletion;
- monitoring;
- ownership.

A quarantine bucket should appear in the data inventory just like a production table.

---

## 14. GDPR Fundamentals

GDPR is a legal framework. Data Engineers should understand its concepts sufficiently to translate approved privacy requirements into technical controls.

Important concepts include:

- personal data;
- processing;
- controller;
- processor;
- data subject;
- purpose limitation;
- data minimization;
- storage limitation;
- integrity/confidentiality awareness;
- accountability.

### Engineering translation

| Privacy concept | Engineering implication |
|---|---|
| Personal data | Classify and discover sensitive fields |
| Purpose limitation | Track processing purpose |
| Data minimization | Avoid unnecessary columns/copies |
| Storage limitation | Implement retention controls |
| Integrity/confidentiality | Protect data and access |
| Accountability | Preserve operational evidence |

The engineering team should not independently make legal determinations.

---

## 15. GDPR Data-Subject Rights

Rights relevant to Data Engineering include awareness of:

- right of access;
- right to rectification;
- right to erasure;
- right to restriction;
- data portability;
- objection.

A technical request workflow can look like:

```text
Data Subject Request
        ↓
Identity Verification
        ↓
Data Discovery
        ↓
Access / Rectification / Erasure
        ↓
Verification
        ↓
Evidence
```

The workflow must distinguish the **request type** because access and erasure have different technical effects.

Do not invent legal deadlines. Where deadlines or exemptions matter, validate them with the privacy/legal team for the applicable jurisdiction and facts.

---

## 16. Right to Erasure

The central engineering insight is:

> **Finding and deleting a row from the primary database is not sufficient if governed copies remain elsewhere.**

Consider:

```text
Customer
  ↓
OLTP
  ↓
CDC
  ↓
Kafka
  ↓
Bronze
  ↓
Silver
  ↓
Gold
  ↓
Warehouse
  ↓
BI Cache
  ↓
ML Features
  ↓
Logs
  ↓
Backups
```

An erasure workflow must therefore operate against the **data graph**, not a single database.

This is why catalogs, lineage, identity resolution, and data inventories are foundational privacy-engineering capabilities.

---

## 17. Consent and Purpose Tracking

Consent can be relevant to certain processing activities, but it is **not the universal legal basis for all processing**.

A conceptual consent record:

```sql
CREATE TABLE consent_events (
    consent_id    TEXT PRIMARY KEY,
    subject_id    TEXT NOT NULL,
    purpose       TEXT NOT NULL,
    status        TEXT NOT NULL,
    effective_at  TIMESTAMPTZ NOT NULL,
    withdrawn_at  TIMESTAMPTZ,
    source        TEXT
);
```

Example states might include:

```text
GRANTED
WITHDRAWN
EXPIRED
SUPERSEDED
```

The exact state model should be defined by the organization's privacy requirements.

### Why purpose metadata matters

Downstream processing can evaluate approved metadata:

```text
Subject
  ↓
Purpose State
  ↓
Allowed Processing
  ↓
Pipeline / Consumer
```

Consent withdrawal may require downstream systems to stop certain processing. The correct response depends on the applicable legal basis and approved policy.

---

## 18. Data Inventory and Records of Processing

A data inventory should answer:

```text
What?
Who owns it?
Why?
Where?
How sensitive?
How long?
Which region?
Who consumes it?
Which systems process it?
What lineage exists?
```

Suggested fields:

| Field | Example |
|---|---|
| Dataset | `customer_orders` |
| Owner | Data Platform |
| Purpose | Order fulfillment |
| Classification | Confidential |
| Location | Approved region |
| Retention | Organization-defined |
| Residency | Policy reference |
| Lineage | OpenLineage metadata |
| Consumers | Warehouse, BI |
| Processing systems | PostgreSQL, Spark |

### Records of Processing Activities

Records of Processing Activities are a governance/legal concept. Engineering systems can provide supporting metadata:

- purpose;
- data categories;
- systems;
- consumers;
- storage locations;
- retention;
- transfers;
- owners.

Engineering evidence should not be represented as a substitute for formal legal records.

---

## 19. Discovering Personal Data

Erasure starts with discovery.

A robust discovery model is:

```text
Identity Key
     ↓
Catalog
     ↓
Lineage
     ↓
Dataset Inventory
     ↓
Data Locations
```

Discovery methods include:

- schema search;
- catalog metadata;
- PII tags;
- column classification;
- lineage;
- data contracts;
- source ownership;
- dataset inventories.

### Direct vs derived data

Direct copy:

```text
customer_id, email
```

Derived copy:

```text
customer_segment
monthly_customer_revenue
feature_vector
```

The derived dataset may not contain the original email, yet can still encode information derived from the subject.

Therefore, discovery cannot be limited to columns named `email`.

---

## 20. Identity Keys and Data Discovery

Identity resolution is one of the hardest parts of erasure.

Potential identifiers:

```text
customer_id
account_id
user_id
email hash
external customer reference
```

### Canonical subject ID

A platform should prefer a stable internal identity:

```text
Canonical Subject ID
       |
       +-- CRM customer_id
       +-- Billing account_id
       +-- Application user_id
       +-- External reference
```

### Why email is a weak universal key

Email can:

- change;
- be shared;
- be normalized differently;
- be represented in multiple forms;
- be absent;
- be transformed into hashes;
- appear in legacy systems under a different identity.

An identity mapping service or governed identity table can make discovery more reliable.

---

## 21. Catalog and Lineage for Erasure

Lineage makes downstream impact visible.

Example:

```text
customer_db
   ↓
CDC
   ↓
Kafka
   ↓
Bronze
   ↓
Silver
   ↓
Gold
```

Lineage answers:

- What is upstream?
- What is downstream?
- Which datasets depend on this dataset?
- Which systems consumed this data?
- Which derived assets may need recomputation or deletion?

### Catalog + lineage

The catalog tells you **what exists and who owns it**.

Lineage tells you **how assets are related**.

Together they provide the foundation for deletion planning.

Lineage is not necessarily complete, however. Dynamic SQL, unmanaged copies, local files, manual exports, and opaque external systems can create blind spots. Erasure systems need explicit completeness controls and exception handling.

---

## 22. End-to-End Deletion Architecture

A robust workflow is:

```text
Deletion Request
       ↓
Validate Request
       ↓
Resolve Identity
       ↓
Find Data
       ↓
Build Deletion Plan
       ↓
Check Legal Holds
       ↓
Delete / Protect Each Copy
       ↓
Verify
       ↓
Generate Evidence
       ↓
Close Request
```

### Step 1 — Validate request

Check request format, authorization, subject identity, and applicable policy.

### Step 2 — Resolve identity

Map the subject to canonical and system-specific identifiers.

### Step 3 — Discover

Use inventory, catalog, lineage, contracts, and approved discovery mechanisms.

### Step 4 — Plan

Create an explicit list of systems and actions.

### Step 5 — Check legal holds

Do not blindly execute ordinary deletion where a governed legal hold requires preservation.

### Step 6 — Execute

Perform system-specific actions with idempotent semantics.

### Step 7 — Verify

Check that required copies are gone, inaccessible, rebuilt, or otherwise handled according to policy.

### Step 8 — Evidence

Record what was attempted, what succeeded, what failed, and what remains subject to a documented exception.

---

## 23. Deleting from OLTP Systems

A production OLTP erasure operation must account for:

- transactions;
- foreign keys;
- cascading deletes;
- child records;
- idempotency;
- retries;
- audit evidence.

Example:

```python
from dataclasses import dataclass
from typing import Protocol


class CustomerStore(Protocol):
    def delete_customer(self, customer_id: str) -> None:
        ...


@dataclass
class ErasureResult:
    customer_id: str
    status: str


def erase_customer(store: CustomerStore, customer_id: str) -> ErasureResult:
    if not customer_id:
        raise ValueError("customer_id is required")

    # A production implementation would execute this inside
    # an appropriate transaction and record an idempotency key.
    store.delete_customer(customer_id)

    return ErasureResult(
        customer_id=customer_id,
        status="deleted",
    )
```

The example is intentionally educational. A production implementation must define transaction boundaries, dependency ordering, retries, observability, authorization, and evidence storage.

### Idempotency

If a request is retried:

```text
REQUEST
  ↓
DELETE
  ↓
FAILURE
  ↓
RETRY
  ↓
SAFE TO REPEAT
```

A second execution should not cause unintended damage.

A common pattern is:

```text
idempotency_key = erasure_request_id
```

and a durable state record:

```text
(request_id, target_system, action, status, attempt_count)
```

---

## 24. Deleting Bronze / Raw Data

Raw data can be difficult because it is frequently:

- immutable;
- append-only;
- stored as files;
- partitioned;
- replicated;
- retained for replay.

Strategies include:

1. delete affected files;
2. rewrite files without the subject;
3. replace affected partitions;
4. use controlled tombstones;
5. compact/rewrite derived storage.

### Trade-off

File rewrite can be expensive:

```text
Small number of affected records
        ↓
Large immutable file
        ↓
Rewrite required
        ↓
Compute + storage cost
```

A platform should therefore design raw-data granularity and retention with future erasure cost in mind.

---

## 25. Deleting Silver Data

Silver data is transformed but generally still record-oriented.

Deletion often requires:

- canonical subject ID;
- deterministic identifiers;
- joins;
- partition handling;
- downstream dependency analysis.

Example:

```sql
DELETE FROM silver_customer_events
WHERE subject_id = :subject_id;
```

For a large partitioned table, a more efficient design may isolate subject records and rebuild affected partitions.

If Silver has been pseudonymized, the deletion workflow must still retain a governed mapping between the canonical subject and the transformed identifier where needed.

---

## 26. Deleting Gold and Derived Data

Gold data frequently contains aggregates:

```text
customer-level aggregate
monthly revenue
customer segmentation
```

A critical point:

> **Deleting a raw record does not automatically remove its contribution from an aggregate.**

Suppose:

```text
January revenue = $10,000
Customer A contributed $500
```

Deleting Customer A from the raw layer does not magically turn the Gold value into `$9,500`.

Possible strategies:

- recomputation;
- affected partition rebuild;
- aggregate correction;
- tombstone/retraction;
- privacy-preserving aggregate design.

The correct strategy depends on the data model and privacy requirements.

---

## 27. Warehouse Deletion and Time Travel

Warehouses and lakehouses can expose historical state through features such as:

- time travel;
- snapshots;
- clones;
- historical versions;
- materialized views.

Therefore:

```text
Current table
     ↓
DELETE row
     ↓
Current query looks clean
```

does not necessarily imply:

```text
Historical versions
Snapshots
Clones
Materialized copies
```

are immediately inaccessible.

Platform behavior differs. The erasure design must explicitly document how historical storage is handled, when it expires, and how verification works.

---

## 28. Cache and Temporary Copy Deletion

Common overlooked copies include:

- query caches;
- BI extracts;
- application caches;
- materialized views;
- temporary tables.

Example:

```text
Warehouse
   ↓
BI Extract
   ↓
Dashboard
```

Deleting the warehouse record while leaving a cached extract can leave stale information visible.

A cache-aware erasure workflow should:

1. identify cache consumers;
2. invalidate/delete relevant cache entries;
3. refresh derived views where required;
4. verify cache absence;
5. record the result.

---

## 29. Kafka and Event Deletion

Kafka adds a fundamental distributed-systems problem.

An event can be:

```text
Produced
  ↓
Retained
  ↓
Consumed
  ↓
Persisted elsewhere
```

Deleting the Kafka record does not undo downstream persistence.

Consider:

```text
Kafka event
   ├── Warehouse
   ├── Feature store
   ├── Search index
   └── Cache
```

Important concepts:

- retention;
- tombstones;
- compaction;
- replay;
- consumer offsets;
- event immutability;
- derived state.

### Production strategy

Treat Kafka as one target in an erasure graph, not as the entire graph.

Depending on architecture, a system may:

- rely on retention expiration;
- use compacted topics and tombstones for state;
- trigger downstream deletion;
- rebuild downstream state;
- maintain subject-level deletion markers.

The exact design must be validated against the Kafka topology and downstream guarantees.

---

## 30. Logs and Quarantine Deletion

A deletion workflow should include:

```text
Application Logs
Pipeline Logs
Audit/Operational Records
Quarantine
```

A log event may contain:

```text
request_id
customer_id
email
IP address
```

The safest architecture minimizes direct PII in logs.

Use:

```text
request_id → internal correlation
```

instead of:

```text
email → correlation
```

where feasible.

Quarantine must also be included in discovery and deletion.

---

## 31. ML Features and Training Data

Personal information can reach:

- feature stores;
- feature tables;
- embeddings;
- derived features;
- recommendation datasets.

Example:

```text
customer_age
customer_segment
purchase_history
```

A feature deletion strategy should identify whether a feature:

- is directly keyed by subject;
- is derived from subject history;
- participates in shared aggregates;
- feeds a model;
- is materialized in multiple stores.

### Training data

Training pipelines can produce:

```text
Source data
   ↓
Snapshot
   ↓
Feature table
   ↓
Training file
   ↓
Experiment dataset
   ↓
Model artifact
```

Deleting the source record does not necessarily mean every trained model has forgotten the information.

Model-specific privacy requirements depend on the use case, model architecture, organizational policy, and applicable law. Do not overstate a universal technical or legal conclusion.

---

## 32. Test and Development Data

Personal data can escape production boundaries into:

- development databases;
- notebooks;
- local files;
- test fixtures;
- CI datasets;
- screenshots;
- debugging artifacts.

Preferred controls include:

- synthetic data;
- masking;
- pseudonymization;
- tokenization;
- automatic cleanup;
- restricted environments.

### Better test pattern

```text
Production PII
      X
      |
Synthetic generator
      ↓
Test dataset
      ↓
CI / Integration tests
```

If production-derived data is genuinely required, it needs explicit governance, access controls, retention, and deletion coverage.

---

## 33. Backups and Immutable Storage

Backups are a major production challenge:

- database backups;
- object-storage backups;
- snapshots;
- immutable backups;
- cross-region replicas;
- disaster-recovery copies.

The difficult question is:

> **What does deletion mean when a backup cannot be modified immediately?**

A defensible engineering strategy can include:

1. document backup retention windows;
2. ensure normal primary copies are deleted;
3. prevent restored backups from silently reintroducing deleted data;
4. allow backups to expire according to policy;
5. preserve evidence of the approved strategy;
6. evaluate encryption/key-management options;
7. involve privacy/legal teams where requirements are ambiguous.

### Restore hazard

```text
Deleted production record
        ↓
Old backup still contains record
        ↓
Backup restored
        ↓
Record reappears
```

Production recovery procedures therefore need deletion-state reconciliation.

---

## 34. Crypto-Shredding

Crypto-shredding can be represented as:

```text
Encrypted backup
       ↓
Encryption key
       ↓
Key destroyed
       ↓
Data becomes computationally inaccessible
```

Potentially useful properties include:

- large backup populations;
- immutable storage;
- key-scoped destruction;
- controlled key hierarchy.

### Limitations

Crypto-shredding is not automatically equivalent to every legal or organizational deletion requirement.

Engineering questions include:

- Is the data encrypted?
- Is the key uniquely scoped?
- Are copies protected by other keys?
- Are keys recoverable?
- What is the evidence of destruction?
- Can restored data be reintroduced?
- What happens to replicated ciphertext?

Use it as one technique in a broader deletion architecture.

---

## 35. Legal Holds

A legal hold may require data that would otherwise be deleted to be preserved.

Conceptually:

```text
Retention expires
       ↓
Check legal hold
       |
    +--+--+
    |     |
   Yes    No
    |     |
 Preserve Delete
```

Useful hold metadata:

```yaml
hold_id: hold-123
scope: customer-order-records
owner: legal-or-approved-owner
start_date: organization-defined
release_date: null
status: active
```

The engineering platform should treat legal holds as policy state, not as an engineer manually remembering an exception.

### Hold lifecycle

```text
Created
  ↓
Scoped
  ↓
Active
  ↓
Reviewed
  ↓
Released
  ↓
Normal retention resumes
```

A legal hold should have:

- scope;
- owner;
- lifecycle;
- audit history;
- affected datasets;
- release state.

Do not make legal determinations in code. The platform should enforce approved hold metadata.

---

## 36. Data Residency

Data residency concerns the geographic location of storage and processing.

Consider:

```text
Primary Storage
Replicas
Backups
Logs
Kafka
Caches
Analytics
Support Systems
```

All may have different locations.

### Residency-aware architecture

```text
Subject / Dataset
       ↓
Residency Policy
       ↓
Allowed Regions
       ↓
Storage / Processing Placement
```

Questions for engineers:

- Where is the primary copy?
- Where are replicas?
- Where are backups?
- Where is Kafka hosted?
- Where are logs exported?
- Where do support tools store data?
- Can disaster recovery move data across regions?
- Which cross-border transfers require governance?

Specific cross-border requirements are jurisdiction-dependent and must be validated with privacy/legal teams.

---

## 37. Proof of Deletion

Deletion should produce technical evidence that the required workflow was attempted and verified.

An evidence record can contain:

```yaml
request_id: erasure-123
subject_id: subject-456
requested_at: organization-defined
completed_at: organization-defined
datasets_targeted:
  - customer_db
  - bronze_customer
  - silver_customer
  - warehouse_customer
systems_processed:
  - postgres
  - object_storage
  - warehouse
verification:
  customer_db: passed
  bronze_customer: passed
  warehouse_customer: passed
legal_hold: false
status: completed
```

### Evidence should answer

- Which request?
- Which subject?
- Which systems?
- Which actions?
- When?
- By which service/operator?
- What succeeded?
- What failed?
- What was verified?
- What exception remained?

Evidence supports governance and auditability; it is not itself a legal conclusion.

---

## 38. Deletion Certificates

A deletion certificate can provide a durable summary:

```yaml
request_id: erasure-2026-001
subject_id: subject-123
requested_at: 2026-01-10T10:00:00Z
completed_at: 2026-01-10T10:07:14Z

datasets_processed:
  - customer_db
  - bronze_customer
  - silver_customer
  - warehouse_customer

verification:
  customer_db: passed
  bronze_customer: passed
  silver_customer: passed
  warehouse_customer: passed

legal_hold: false
status: completed
```

### What a certificate proves

It can prove that the platform recorded:

- the request;
- planned/processed targets;
- execution results;
- verification results;
- relevant policy state.

### What it does not prove

It does not, by itself, prove complete legal compliance or prove that no undiscovered copy exists.

Protect certificates as sensitive governance evidence. Use access controls, integrity protections, and an appropriate retention policy for the evidence itself.

---

## 39. Privacy by Design

Privacy by design starts before data is collected.

Core principles for engineering include:

- data minimization;
- purpose limitation;
- retention by default;
- least data;
- secure defaults;
- deletion by design;
- traceability;
- privacy-aware observability;
- privacy-aware architecture.

> **The cheapest data to delete is data you never collected or copied unnecessarily.**

### Architectural example

Bad:

```text
Source
 ↓
Raw forever
 ↓
Five copies
 ↓
Multiple unmanaged exports
```

Better:

```text
Purpose
 ↓
Minimum required fields
 ↓
Controlled copies
 ↓
Known retention
 ↓
Known lineage
 ↓
Automated expiration
```

---

## 40. Automated Retention Enforcement

Retention should be executable.

Example policy:

```yaml
dataset: events
retention_days: 30
action: delete
owner: data-platform
```

A retention engine can calculate eligibility:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class RetentionPolicy:
    dataset: str
    retention_days: int
    action: str
    owner: str


def expiry_time(created_at: datetime, policy: RetentionPolicy) -> datetime:
    if policy.retention_days < 0:
        raise ValueError("retention_days cannot be negative")

    return created_at + timedelta(days=policy.retention_days)


def is_expired(
    created_at: datetime,
    now: datetime,
    policy: RetentionPolicy,
) -> bool:
    return now >= expiry_time(created_at, policy)


policy = RetentionPolicy(
    dataset="events",
    retention_days=30,
    action="delete",
    owner="data-platform",
)

created = datetime(2026, 1, 1, tzinfo=timezone.utc)
now = datetime(2026, 2, 1, tzinfo=timezone.utc)

print(is_expired(created, now, policy))
```

A production engine additionally checks:

```text
Policy
 ↓
Exception
 ↓
Legal Hold
 ↓
Residency
 ↓
Dependency
 ↓
Deletion Eligibility
```

---

## 41. Automated Erasure Pipeline

A production erasure state machine can be:

```text
REQUESTED
   ↓
VALIDATED
   ↓
PLANNED
   ↓
IN_PROGRESS
   ↓
PARTIALLY_COMPLETED
   ↓
RETRYING
   ↓
VERIFIED
   ↓
COMPLETED
```

Failure states should include at least:

```text
VALIDATION_FAILED
IDENTITY_UNRESOLVED
LEGAL_HOLD_BLOCKED
EXECUTION_FAILED
VERIFICATION_FAILED
MANUAL_REVIEW
```

### State record

```sql
CREATE TABLE erasure_tasks (
    request_id       TEXT NOT NULL,
    target_system    TEXT NOT NULL,
    action           TEXT NOT NULL,
    status           TEXT NOT NULL,
    attempt_count    INTEGER NOT NULL DEFAULT 0,
    last_error       TEXT,
    updated_at       TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (request_id, target_system, action)
);
```

This structure makes retries and reconciliation observable.

---

## 42. End-to-End Python Erasure Example

The following is an **educational implementation**, not a production-ready connector framework.

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ErasureRequest:
    request_id: str
    subject_id: str


@dataclass
class TargetResult:
    target: str
    status: str
    detail: str = ""


@dataclass
class ErasurePlan:
    subject_id: str
    targets: list[str]


def validate_request(request: ErasureRequest) -> None:
    if not request.request_id:
        raise ValueError("request_id is required")
    if not request.subject_id:
        raise ValueError("subject_id is required")


def check_legal_hold(subject_id: str) -> bool:
    # Replace with a governed legal-hold service in production.
    return False


def discover_targets(subject_id: str) -> ErasurePlan:
    # Replace with catalog + lineage + inventory integration.
    return ErasurePlan(
        subject_id=subject_id,
        targets=[
            "customer_db",
            "bronze_customer",
            "silver_customer",
            "warehouse_customer",
            "customer_cache",
            "feature_store",
        ],
    )


def execute_target(
    target: str,
    subject_id: str,
    handlers: dict[str, Callable[[str], None]],
) -> TargetResult:
    try:
        handlers[target](subject_id)
        return TargetResult(target=target, status="deleted")
    except Exception as exc:
        return TargetResult(
            target=target,
            status="failed",
            detail=str(exc),
        )


def verify_target(target: str, subject_id: str) -> bool:
    # Production code would query the target's verification interface.
    return True


def erase_customer(
    request: ErasureRequest,
    handlers: dict[str, Callable[[str], None]],
) -> list[TargetResult]:
    validate_request(request)

    if check_legal_hold(request.subject_id):
        raise RuntimeError("Erasure blocked by legal hold")

    plan = discover_targets(request.subject_id)
    results: list[TargetResult] = []

    for target in plan.targets:
        result = execute_target(target, request.subject_id, handlers)

        if result.status == "deleted" and not verify_target(
            target, request.subject_id
        ):
            result.status = "verification_failed"

        results.append(result)

    return results
```

### Production architecture behind the example

```text
Request API
    ↓
Identity Resolver
    ↓
Inventory / Catalog / Lineage
    ↓
Deletion Planner
    ↓
Task Queue
    ↓
System-specific Workers
    ↓
Verification Workers
    ↓
Evidence Store
    ↓
Certificate
```

The production system should also provide:

- durable state;
- idempotency;
- retry policies;
- authorization;
- legal-hold evaluation;
- timeout handling;
- dead-letter/manual-review state;
- metrics;
- tracing;
- audit records;
- reconciliation.

---

## 43. Retention Automation Lab

### Objective

Build a small retention engine that:

1. loads policy metadata;
2. calculates expiry;
3. identifies expired partitions;
4. creates deletion tasks;
5. records execution;
6. verifies completion.

### Input

```yaml
dataset: events
retention_days: 30
action: delete
owner: data-platform
```

### Lab model

```text
Policy
  ↓
Partition Inventory
  ↓
Expiry Calculation
  ↓
Eligibility Check
  ↓
Deletion Task
  ↓
Execution
  ↓
Verification
```

### Exercise

Create a Python implementation with:

- `RetentionPolicy`;
- `Partition`;
- `DeletionTask`;
- `calculate_expiry()`;
- `is_eligible()`;
- `create_deletion_task()`;
- `record_result()`.

Then add:

- legal-hold support;
- dry-run mode;
- retry count;
- structured execution evidence.

### Production extension

Map the same pattern to an orchestrator:

```text
Scheduled DAG / Workflow
       ↓
Load policy
       ↓
Discover eligible partitions
       ↓
Check holds
       ↓
Delete
       ↓
Verify
       ↓
Emit metrics/evidence
```

---

## 44. Erasure Pipeline Lab

Build a synthetic platform:

```text
Synthetic Customer
       ↓
PostgreSQL
       ↓
Kafka
       ↓
Object Storage
       ↓
Warehouse
       ↓
Cache
       ↓
ML Feature Table
       ↓
Deletion Request
       ↓
Delete Everywhere
       ↓
Verify
       ↓
Deletion Certificate
```

### Required components

- Python;
- SQL;
- synthetic data;
- lineage metadata;
- deletion planner;
- retries;
- failure injection;
- verification;
- evidence generation.

### Suggested repository structure

```text
erasure-lab/
├── app/
│   ├── identity.py
│   ├── inventory.py
│   ├── planner.py
│   ├── executor.py
│   ├── verifier.py
│   └── evidence.py
├── sql/
│   ├── schema.sql
│   └── seed.sql
├── policies/
│   └── retention.yaml
├── tests/
│   ├── test_identity.py
│   ├── test_planner.py
│   ├── test_idempotency.py
│   └── test_end_to_end.py
└── README.md
```

---

## 45. Testing and Verification

Deletion is a safety-critical workflow. Test it like production infrastructure.

### Unit tests

Test:

- retention calculation;
- identity resolution;
- deletion planning;
- legal-hold logic;
- policy evaluation;
- idempotency decisions.

Example:

```python
def test_retention_expires_after_policy_window():
    policy = RetentionPolicy(
        dataset="events",
        retention_days=30,
        action="delete",
        owner="data-platform",
    )

    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = datetime(2026, 1, 31, tzinfo=timezone.utc)

    assert not is_expired(created, now, policy)
```

### Integration tests

Test:

- OLTP deletion;
- object-storage behavior;
- warehouse deletion;
- Kafka behavior;
- cache invalidation;
- lineage/inventory integration.

### End-to-end tests

Use synthetic subjects:

```text
Synthetic Customer A
       ↓
Full Platform
       ↓
Erasure Request
       ↓
Verify No Remaining Governed Copies
```

### Regression tests

Every time a new data destination is added:

```text
New pipeline destination
        ↓
Erasure coverage check
        ↓
Included?
    /       \
  Yes        No
  ↓          ↓
Deploy     Block / Review
```

This prevents privacy coverage from silently regressing as the platform grows.

---

## 46. Failure Injection and Debugging

### Failure 1 — Forgotten Bronze Copy

**Failure:** Customer is deleted from OLTP but remains in raw storage.

**Detection:** Inventory/verification query finds a governed raw copy.

**Investigation:** Inspect lineage and deletion-task results.

**Containment:** Block certificate completion.

**Recovery:** Execute Bronze deletion.

**Verification:** Re-scan the governed location.

**Evidence:** Record the failed verification and successful remediation.

**Prevention:** Add Bronze to mandatory erasure coverage tests.

### Failure 2 — Warehouse Time-Travel Copy

**Failure:** Current table is clean but historical data remains accessible.

**Detection:** Historical query returns the subject.

**Investigation:** Inspect warehouse history/snapshot policy.

**Recovery:** Apply platform-specific history cleanup/expiry process.

**Prevention:** Add historical storage to deletion verification.

### Failure 3 — Kafka Event Still Available

**Failure:** Old event remains within retention.

**Detection:** Subject-aware test finds event.

**Recovery:** Apply the approved Kafka/event strategy and downstream propagation.

**Prevention:** Treat Kafka as an explicit deletion target.

### Failure 4 — BI Cache

**Failure:** Dashboard still exposes deleted data.

**Recovery:** Invalidate/delete cache or regenerate extract.

### Failure 5 — ML Feature

**Failure:** Subject remains in feature storage.

**Recovery:** Delete/recompute affected features.

### Failure 6 — Backup

**Failure:** Backup still contains the original data.

**Recovery:** Apply documented backup retention/expiration strategy and evaluate key-management controls.

### Failure 7 — Legal Hold

**Failure:** Deletion job incorrectly deletes held data.

**Containment:** Stop deletion workers.

**Recovery:** Restore from protected evidence where possible and escalate to the privacy/legal process.

**Prevention:** Evaluate holds before execution and continuously validate policy state.

### Failure 8 — Partial Failure

```text
OLTP       → success
Bronze     → success
Silver     → success
Warehouse  → failure
Cache      → not attempted
```

The request must become:

```text
PARTIALLY_COMPLETED
```

not `COMPLETED`.

---

## 47. Common Production Mistakes

| Mistake | Why it happens | Risk | Correct approach |
|---|---|---|---|
| No retention policy | Focus on ingestion, not lifecycle | Indefinite storage | Define owner/purpose/retention |
| Retention without ownership | Governance is abstract | Nobody maintains it | Assign accountable owner |
| Retention without purpose | Dataset treated as generic | Wrong lifecycle | Track purpose |
| Delete only primary DB | Single-system thinking | Copies remain | Use inventory + lineage |
| Ignore derived data | Focus on raw records | Aggregates retain effects | Recompute/retract |
| Ignore Kafka | Treat stream as transient | Downstream copies persist | Include stream graph |
| Ignore logs | Logs seen as operational only | PII survives | Minimize and govern logs |
| Ignore quarantine | Hidden operational store | Forgotten copies | Inventory quarantine |
| Ignore caches | Cache seen as disposable | Data remains visible | Invalidate and verify |
| Ignore ML features | ML treated separately | Derived PII persists | Include feature store |
| Ignore test data | Non-production assumed safe | PII spreads | Prefer synthetic data |
| Ignore backups | Backup treated as immutable exception | Restore can reintroduce data | Define documented strategy |
| Ignore time travel | Current table looks clean | History remains | Verify historical storage |
| No lineage | Manual discovery | Missing copies | Govern lineage |
| No inventory | Unknown systems | Blind spots | Maintain data inventory |
| Email-only identity | Convenient identifier | Missed aliases/copies | Canonical identity mapping |
| No idempotency | Happy-path workflow | Retries cause errors | Durable request/task keys |
| No verification | Trust execution status | False completion | Independent verification |
| No evidence | Logs scattered | Weak auditability | Structured evidence |
| No legal-hold handling | Retention is automatic | Held data deleted | Policy gate |
| Assume crypto-shredding solves everything | Attractive shortcut | Incomplete controls | Use as one technique |
| Certificate treated as legal proof | Evidence confused with conclusion | Governance risk | Distinguish technical evidence |
| No residency awareness | Cloud defaults | Unauthorized location | Track regions and replicas |

---

## 48. Production Architecture

A complete erasure-capable platform can look like:

```text
                 Data Subject Request
                         |
                         v
                   Request Service
                         |
                         v
                   Identity Resolver
                         |
                         v
                    Data Inventory
                         |
                         v
                      Catalog
                         |
                         v
                     OpenLineage
                         |
                         v
                   Deletion Planner
                         |
              +----------+----------+
              |          |          |
              v          v          v
             OLTP     Lakehouse   Warehouse
              |          |          |
              +----------+----------+
                         |
              +----------+----------+
              |          |          |
              v          v          v
            Kafka      Cache      ML Features
              |          |          |
              +----------+----------+
                         |
                         v
                      Backups
                         |
                         v
                    Verification
                         |
                         v
                  Deletion Evidence
                         |
                         v
                    Certificate
```

### Component responsibilities

**Request service:** accepts and tracks requests.

**Identity resolver:** maps canonical subject identity to system identifiers.

**Data inventory:** identifies governed assets.

**Catalog:** provides ownership, classification, metadata, and discovery.

**Lineage:** exposes upstream/downstream dependencies.

**Deletion planner:** turns discovery into explicit tasks.

**Workers:** execute target-specific deletion operations.

**Verification:** independently checks results.

**Evidence store:** records technical evidence.

**Certificate generator:** summarizes the governed workflow result.

### Production properties

A mature system should provide:

- authorization;
- idempotency;
- durable state;
- retries;
- dead-letter/manual-review paths;
- legal-hold evaluation;
- residency policy;
- observability;
- auditability;
- reconciliation;
- change management;
- regression testing.

---

## 49. Checkpoint Questions

### Questions

1. What is data retention?
2. Why should data not be retained forever?
3. What is retention by purpose?
4. Why is Kafka retention not the same as data-subject deletion?
5. Why can time travel complicate deletion?
6. Why must derived aggregates be considered?
7. Why are backups difficult for erasure?
8. What is crypto-shredding?
9. What is a legal hold?
10. Why is identity resolution important?
11. How does lineage help deletion?
12. What should a deletion certificate contain?
13. Why must deletion workflows be idempotent?
14. Why must deletion be verified?
15. What is privacy by design?

### Model answers

**1. What is data retention?**  
Retention defines how long a dataset or governed copy should exist and what happens when that period ends.

**2. Why not retain forever?**  
Indefinite retention increases security, privacy, cost, operational, and governance risk.

**3. Retention by purpose?**  
Retention is associated with the reason data is processed, so different purposes can have different lifecycle requirements.

**4. Kafka retention vs deletion?**  
Kafka expiry removes/ages out the Kafka copy; consumers may already have persisted the event elsewhere.

**5. Time travel?**  
A current table can be clean while historical versions, snapshots, or clones still expose older state.

**6. Derived aggregates?**  
An aggregate can preserve the subject's contribution even after the source record is removed.

**7. Backups?**  
Backups may be immutable or retained for recovery, making immediate modification impossible and requiring an approved strategy.

**8. Crypto-shredding?**  
Destroying encryption keys so encrypted data becomes computationally inaccessible; it is a technique, not a universal deletion substitute.

**9. Legal hold?**  
A governed instruction to preserve specified data that would otherwise be subject to ordinary deletion.

**10. Identity resolution?**  
It maps one subject to identifiers used by multiple systems so discovery and deletion do not miss copies.

**11. Lineage?**  
Lineage exposes downstream assets that received or derived data, making deletion planning more complete.

**12. Certificate contents?**  
Request identity, subject reference, timestamps, targets, results, verification, hold status, and final state.

**13. Idempotency?**  
Retries are expected in distributed systems; idempotency makes repeated execution safe.

**14. Verification?**  
Execution success does not guarantee that the data is actually absent from every governed target.

**15. Privacy by design?**  
Designing systems so data minimization, purpose limitation, retention, deletion, traceability, and privacy controls exist from the beginning.

---

## 50. Interview Preparation

### Beginner

**Q: What is data retention?**  
A: A policy-controlled period defining how long data should exist and what happens at the end.

**Q: What is GDPR?**  
A: A privacy regulation/framework governing processing of personal data in its scope; engineers focus on translating approved obligations into technical controls.

**Q: What is data deletion?**  
A: Removing governed data or copies according to an approved lifecycle or erasure policy.

**Q: What is data minimization?**  
A: Limiting collection and processing to data that is necessary for the intended purpose.

### Intermediate

**Q: Soft delete vs hard delete?**  
A: Soft delete marks a record as deleted while retaining it; hard delete removes it from the current logical store. Hard delete still requires consideration of history, replicas, backups, and derived copies.

**Q: Why partition deletion?**  
A: It can remove large time-bounded datasets efficiently without scanning every row.

**Q: Why is object storage difficult?**  
A: Versioning, replicas, lifecycle rules, and delete markers can create additional copies.

**Q: Why isn't Kafka deletion enough?**  
A: Consumers may already have persisted the event downstream.

### Advanced

**Q: How do you delete across a lakehouse?**  
A: Start with canonical identity, inventory and lineage, then delete/rewrite relevant Bronze/Silver/Gold assets, account for history/snapshots, and verify each governed target.

**Q: How does lineage support erasure?**  
A: It provides dependency information needed to discover downstream copies and derived assets.

**Q: How do you handle legal holds?**  
A: Treat hold state as a policy gate before deletion, preserve scoped data while the hold is active, and resume normal lifecycle only after authorized release.

**Q: What about backups?**  
A: Define backup retention and restoration controls, document how deletion interacts with immutable copies, and evaluate encryption/key-management strategies.

### Senior / Production

**Q: Design an end-to-end erasure platform.**  
A: Use a request service, canonical identity resolver, catalog/inventory, lineage, deletion planner, target-specific workers, durable state, retries, legal-hold and residency checks, independent verification, and evidence generation.

**Q: How do you discover every copy?**  
A: Combine inventory, catalog metadata, lineage, identity mappings, contracts, PII classification, and controlled exception discovery. No single metadata system should be assumed complete.

**Q: How do you handle derived datasets?**  
A: Determine whether deletion requires direct removal, recomputation, correction, or state rebuild based on the derivation.

**Q: How do you make deletion idempotent?**  
A: Use durable request/target/action keys, explicit task state, safe retry semantics, and reconciliation.

**Q: How do you detect incomplete deletion?**  
A: Independent post-delete verification scans governed systems and compares actual state against the deletion plan.

**Q: How do you prove deletion?**  
A: Preserve technical evidence showing targets, actions, timestamps, identities, failures, and verification results. Do not confuse technical evidence with a legal conclusion.

---

## 51. Final Assessment

This assessment is intentionally architecture-oriented.

### Scenario

An enterprise processes customer data through:

```text
API
 ↓
PostgreSQL
 ↓
CDC
 ↓
Kafka
 ↓
Object Storage / Bronze
 ↓
Spark / Silver
 ↓
Gold
 ↓
Warehouse
 ↓
BI
 ↓
Feature Store
 ↓
ML Training
 ↓
Logs
 ↓
Backups
```

A customer submits an erasure request.

### Tasks

1. Define the retention policy metadata model.
2. Define the canonical subject identity.
3. Explain how you discover every governed copy.
4. Design the catalog/lineage integration.
5. Design the deletion state machine.
6. Explain OLTP deletion and transaction boundaries.
7. Explain Bronze deletion where files are immutable.
8. Explain Silver deletion.
9. Explain Gold aggregate correction/recomputation.
10. Explain warehouse history/time-travel implications.
11. Explain Kafka strategy.
12. Explain cache invalidation.
13. Explain feature-store deletion.
14. Explain training-data considerations.
15. Explain test/development data handling.
16. Explain backup strategy.
17. Explain crypto-shredding limitations.
18. Explain legal-hold handling.
19. Explain residency controls.
20. Define deletion verification.
21. Define deletion evidence.
22. Define deletion certificate.
23. Design failure recovery.
24. Design unit/integration/end-to-end/regression tests.
25. Define monitoring and operational alerts.

### Evaluation rubric

| Area | Excellent answer demonstrates |
|---|---|
| Retention | Purpose-driven, owned, executable policies |
| Discovery | Inventory + catalog + lineage + identity |
| Identity | Canonical and system-specific mappings |
| Deletion | Target-specific, idempotent workflow |
| Lakehouse | Bronze/Silver/Gold reasoning |
| Warehouse | History/time-travel awareness |
| Streaming | Kafka and downstream propagation reasoning |
| ML | Feature and training-data awareness |
| Backups | Explicit restore/retention strategy |
| Legal hold | Policy gate and auditability |
| Residency | Storage/replica/backup awareness |
| Verification | Independent checks |
| Evidence | Structured and protected |
| Reliability | Retry, partial failure, reconciliation |
| Testing | Unit/integration/E2E/regression |
| Privacy | Minimization and privacy-by-design thinking |

---

## 52. Production Challenge

> **Design a production-grade data-retention and data-subject-erasure platform for an enterprise that processes customer data through APIs, PostgreSQL, Kafka, object storage, Spark, a lakehouse, a warehouse, BI tools, feature stores, logs, caches, and backups.**

Your design must include:

- retention policies;
- purpose metadata;
- data inventory;
- identity resolution;
- catalog;
- lineage;
- deletion planner;
- OLTP deletion;
- Bronze/Silver/Gold deletion;
- warehouse deletion;
- Kafka strategy;
- cache deletion;
- ML feature deletion;
- test-data deletion;
- backup strategy;
- crypto-shredding awareness;
- legal holds;
- residency controls;
- verification;
- deletion evidence;
- deletion certificates;
- monitoring;
- auditability;
- failure recovery.

### Required trade-off analysis

For each major decision, explain:

```text
Option A
  ↓
Benefits
  ↓
Risks
  ↓
Operational cost
  ↓
Privacy implications
  ↓
Failure modes
  ↓
Why you selected it
```

A senior answer should explicitly address the hardest case:

```text
One subject
  ↓
Many systems
  ↓
Some copies mutable
  ↓
Some copies immutable
  ↓
Some copies derived
  ↓
Some copies historical
  ↓
Some copies replicated
  ↓
One deletion request
```

---

## 53. Glossary

| Term | Meaning |
|---|---|
| Retention | Controlled period for keeping data |
| Retention policy | Rules defining lifecycle and end action |
| Lifecycle | Stages from collection through deletion |
| Purpose limitation | Processing should remain tied to approved purposes |
| Data minimization | Avoid unnecessary data collection/use |
| Personal data | Information within the applicable privacy definition |
| Data subject | Person to whom personal data relates |
| Controller | Entity determining purposes/means of processing in applicable frameworks |
| Processor | Entity processing on behalf of a controller in applicable frameworks |
| Right of access | Right to obtain applicable information about personal data/processing |
| Right to erasure | Applicable right concerning deletion under defined conditions |
| Rectification | Correction of inaccurate data |
| Restriction | Limitation of processing under applicable conditions |
| Portability | Receiving applicable personal data in a usable form under relevant conditions |
| Consent | A possible legal basis for certain processing |
| Purpose | Reason data is processed |
| Data inventory | Governed list of datasets and metadata |
| Records of processing | Formal governance/legal records of processing activities |
| Identity resolution | Mapping subject identity across systems |
| Lineage | Relationships among data assets/processes |
| Deletion | Removal according to policy |
| Hard delete | Removal from the current logical store |
| Soft delete | Marking data as deleted while retaining the record |
| Partition deletion | Removing an entire partition |
| Time travel | Access to historical table state |
| Tombstone | Marker representing deletion in certain systems |
| Kafka retention | Rules governing Kafka data expiration |
| Compaction | Kafka mechanism for retaining latest keyed state |
| Cache | Temporary/materialized copy used for faster access |
| Quarantine | Isolated storage for failed/suspicious records |
| Backup | Recovery copy of data |
| Legal hold | Preservation requirement that can override ordinary lifecycle actions |
| Data residency | Geographic requirements/constraints for storage or processing |
| Crypto-shredding | Destroying encryption keys to make ciphertext inaccessible |
| Deletion certificate | Structured technical summary of an erasure workflow |
| Proof of deletion | Evidence of execution and verification |
| Idempotency | Safe repeated execution of the same operation |
| Erasure workflow | End-to-end process for handling an erasure request |
| Privacy by design | Building privacy controls into system design |

---

## 54. Retention and Deletion Checklist

```text
[ ] I understand the data lifecycle.
[ ] I understand retention policies.
[ ] I understand retention by dataset.
[ ] I understand retention by purpose.
[ ] I understand retention end actions.
[ ] I can design retention metadata.
[ ] I understand database retention.
[ ] I understand partition-based deletion.
[ ] I understand object-storage lifecycle.
[ ] I understand Kafka retention.
[ ] I understand log retention.
[ ] I understand quarantine retention.
[ ] I understand GDPR fundamentals.
[ ] I understand data-subject rights.
[ ] I understand the right to erasure.
[ ] I understand consent and purpose tracking.
[ ] I understand data inventories.
[ ] I understand records of processing.
[ ] I understand identity resolution.
[ ] I can use catalog and lineage for discovery.
[ ] I can design an end-to-end deletion workflow.
[ ] I can delete OLTP data.
[ ] I can handle Bronze/Silver/Gold deletion.
[ ] I understand warehouse time-travel implications.
[ ] I can handle Kafka deletion challenges.
[ ] I understand cache deletion.
[ ] I understand ML feature deletion.
[ ] I understand test-data deletion.
[ ] I understand backup challenges.
[ ] I understand crypto-shredding.
[ ] I understand legal holds.
[ ] I understand data residency.
[ ] I can generate deletion evidence.
[ ] I understand deletion certificates.
[ ] I can design idempotent deletion workflows.
[ ] I can test deletion workflows.
[ ] I can debug partial deletion.
[ ] I can design privacy-by-design data systems.
```

---

## 55. Roadmap Coverage Audit

The following audit maps the authoritative Topic 09 requirements to this module.

| Roadmap Requirement | Covered? | Section | Code/Example? |
|---|---|---|---|
| GDPR principles | Yes | 14 | Yes |
| Data-subject rights | Yes | 15 | Yes |
| CCPA/CPRA awareness | Yes | 56 | Yes |
| HIPAA awareness | Yes | 56 | Yes |
| India DPDP Act awareness | Yes | 56 | Yes |
| Retention policy by dataset | Yes | 4–5 | Yes |
| Retention by purpose | Yes | 5 | Yes |
| Retention end action | Yes | 6 | Yes |
| Table/partition lifecycle | Yes | 9 | Yes |
| Log retention | Yes | 12 | Yes |
| Kafka retention | Yes | 11 | Yes |
| Consent/purpose tracking | Yes | 17 | Yes |
| Erasure pipeline | Yes | 22, 41–42 | Yes |
| Identity keys | Yes | 20 | Yes |
| Catalog discovery | Yes | 21 | Yes |
| Lineage discovery | Yes | 21 | Yes |
| OLTP deletion | Yes | 23 | Yes |
| Bronze deletion | Yes | 24 | Yes |
| Silver deletion | Yes | 25 | Yes |
| Gold deletion | Yes | 26 | Yes |
| Warehouse deletion | Yes | 27 | Yes |
| Time-travel implications | Yes | 27 | Yes |
| Cache deletion | Yes | 28 | Yes |
| Derived aggregates | Yes | 26 | Yes |
| ML feature deletion | Yes | 31 | Yes |
| Training-data awareness | Yes | 31 | Yes |
| Kafka/event deletion | Yes | 29 | Yes |
| Log deletion | Yes | 30 | Yes |
| Quarantine deletion | Yes | 13, 30 | Yes |
| Test-data deletion | Yes | 32 | Yes |
| Backup handling | Yes | 33 | Yes |
| Crypto-shredding | Yes | 34 | Yes |
| Proof of deletion | Yes | 37 | Yes |
| Legal holds | Yes | 35 | Yes |
| Data residency | Yes | 36 | Yes |
| Records of processing | Yes | 18 | Yes |
| Data inventories | Yes | 18 | Yes |
| Privacy by design | Yes | 39 | Yes |
| Retention automation | Yes | 40 | Yes |
| Verification and auditing | Yes | 37, 45 | Yes |
| Failure handling | Yes | 42 | Yes |
| Testing | Yes | 45 | Yes |
| Production architecture | Yes | 48 | Yes |
| Production challenge | Yes | 52 | Yes |

### Jurisdiction awareness

The roadmap requires awareness of several privacy regimes. Their exact obligations are not interchangeable:

- **GDPR:** central privacy framework for this module; engineering focus is on implementing approved privacy requirements.
- **CCPA/CPRA:** U.S. privacy framework with its own terminology, rights, and organizational applicability.
- **HIPAA:** U.S. health-information framework whose technical implications depend on covered entities, business associates, and regulated information.
- **India DPDP Act:** Indian digital personal-data framework; applicability and operational requirements should be interpreted with current organizational/legal guidance.

These are awareness mappings, not legal advice or a claim that the same retention/erasure design satisfies every regime.

---

## 56. Legal and Technical Accuracy Boundary

This module deliberately avoids unsupported legal conclusions.

### Do not

- invent legal requirements;
- invent GDPR obligations;
- claim a technical control automatically proves legal compliance;
- claim deletion is always legally mandatory;
- claim consent is always required;
- claim crypto-shredding universally satisfies erasure;
- claim a deletion certificate proves legal compliance;
- invent retention periods;
- invent regulatory deadlines.

### Always

- distinguish engineering implementation from legal interpretation;
- identify jurisdiction-specific requirements;
- use organization-defined retention periods where no source requirement is provided;
- treat legal holds as a potential override of ordinary deletion workflows;
- explain that technical evidence supports governance but is not itself legal advice;
- distinguish current-state deletion from historical/backup copies;
- explain limitations and trade-offs.

When a legal conclusion depends on jurisdiction or organizational policy:

> **Validate this requirement with the organization's privacy/legal team.**

---

## 57. Version and API Accuracy

Examples involving PostgreSQL, Kafka, object storage, lakehouses, warehouses, Python, and orchestration systems should be treated as architectural examples unless a specific platform/version is stated.

Platform behavior can differ for:

- historical storage;
- object versions;
- Kafka compaction;
- backup immutability;
- warehouse time travel;
- materialized views;
- retention APIs.

Prefer durable concepts:

```text
Policy
Inventory
Plan
Execute
Verify
Evidence
```

over brittle assumptions about one vendor's implementation.

---

## 58. Production Reasoning Framework

For every retention or deletion decision, ask:

```text
What data are we storing?
Why are we storing it?
What is the purpose?
Who owns the data?
How long should it exist?
Where does it exist?
How many copies exist?
What systems received it?
What derived data depends on it?
What is the identity key?
How do we find every copy?
Is there a legal hold?
Are there residency restrictions?
What happens to backups?
What happens to Kafka events?
What happens to caches?
What happens to ML features?
How is deletion verified?
What evidence is retained?
Can the workflow be retried safely?
What happens if one system fails?
```

This is the core mental model for privacy-aware Data Engineering.

---

## 59. Final Quality Bar

You should finish this module able to discuss retention and deletion architecture professionally with:

- Data Engineers;
- Data Architects;
- Security Engineers;
- Privacy Engineers;
- Governance teams;
- Legal/privacy teams;
- Platform Engineers;
- Cloud Engineers;
- SRE/DevOps teams.

The target capability is not memorizing privacy vocabulary.

The target capability is being able to reason about:

```text
Purpose
  ↓
Collection
  ↓
Storage
  ↓
Copies
  ↓
Lineage
  ↓
Retention
  ↓
Erasure
  ↓
Verification
  ↓
Evidence
```

A production-grade Data Engineer should be able to answer:

> **Where does this person's data exist, why does each copy exist, how long should each copy exist, how do we delete or otherwise govern it, how do we prove what happened, and what happens when a system fails?**

That is the practical foundation of retention, deletion, and privacy-aware Data Engineering.
