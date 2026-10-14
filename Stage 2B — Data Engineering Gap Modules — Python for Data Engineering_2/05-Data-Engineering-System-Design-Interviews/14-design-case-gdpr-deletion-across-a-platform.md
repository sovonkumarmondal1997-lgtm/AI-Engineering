# 14 — Design Case: GDPR Deletion Across a Platform

> **Case:** Design a system that guarantees a user's data is deleted from every relevant data system within 30 days of a request — and proves it.
>
> **Level:** Intermediate → Advanced → Senior/Staff system design
>
> **Scope:** Data Engineering, Data Platform, Distributed Systems, Privacy Engineering, Governance, Reliability, and interview reasoning.
>
> **Legal scope:** This is an engineering/system-design learning module, not legal advice. Exact applicability, retention exceptions, and definitions must come from the organization's approved privacy/legal policy.

---

## 1. Learning Objectives

By completing this module you should be able to:

1. Explain GDPR-related concepts at a high engineering level without turning the design into a legal textbook.
2. Define personal-data scope and deletion semantics.
3. Resolve a person across canonical and historical identifiers.
4. Maintain a data inventory and lineage graph.
5. Design deletion contracts for heterogeneous data systems.
6. Orchestrate distributed deletion with idempotency, retries, timeouts, and escalation.
7. Handle databases, warehouses, lake/lakehouse tables, Kafka/event streams, caches, feature stores, vector stores, logs, backups, and immutable storage.
8. Treat derived data, ML artifacts, and RAG indexes as part of the dependency graph.
9. Verify deletion independently and generate auditable evidence without unnecessarily recreating deleted personal data.
10. Manage the 30-day SLA, observability, security, cost, scale, and disaster recovery.
11. Explain trade-offs rather than choosing technology by preference.
12. Solve the case in a 45-minute system-design interview and defend it under Senior/Staff follow-ups.

The authoritative roadmap defines Case 14 around governance thinking, completeness, immutable-storage challenges, identity resolution, inventory/classification, lineage, per-system deletion, crypto-shredding, verification, audit certificates, SLA management, retries, and escalation. The roadmap places this case in Phase C and expects failure/deep-dive reasoning from Topic 16.

---

# 2. The Core Mental Model

The first principle is:

> **Deletion is a distributed data-lifecycle workflow, not a SQL statement.**

A simplified lifecycle is:

```text
Deletion Request
      |
      v
Authenticate / Validate
      |
      v
Resolve Identity
      |
      v
Discover Systems + Lineage
      |
      v
Build Deletion Plan / DAG
      |
      v
Execute System-Specific Deletions
      |
      +----> Retry / Escalate / Exception
      |
      v
Independent Verification
      |
      v
Generate Evidence
      |
      v
Complete or Escalate
```

Two especially useful mental models:

```text
Identity tells you WHAT to delete.
Lineage tells you WHERE to delete it.
```

and:

```text
Execution says an operation was attempted.
Verification says the expected post-condition holds.
```

---

# 3. GDPR: The Engineering-Level View

## 3.1 What is GDPR?

GDPR is a European privacy framework that establishes rules and rights around personal data and its processing.

For a Data Engineer, the important point is not memorizing legislation. The important point is translating approved privacy/legal requirements into reliable engineering controls.

Use this separation:

```text
Legal / privacy policy
        |
        v
Engineering requirement
        |
        v
Implementation
        |
        v
Evidence
```

Never invent a legal requirement merely because a technical design seems convenient.

## 3.2 Engineering-relevant concepts

| Concept | Engineering interpretation |
|---|---|
| Data subject | The person to whom personal data relates |
| Personal data | Data that the organization treats as relating to an identifiable person under its policy/legal analysis |
| Processing | Operations performed on data, including collection, transformation, storage, retrieval, and deletion |
| Controller / processor | Organizational roles that affect responsibility and contractual/system boundaries |
| Deletion request | A request that enters an approved privacy workflow and is evaluated against policy |
| Retention | A policy defining how long data may or must remain |
| Data minimization | Avoid collecting or retaining data that is not needed |
| Auditability | Ability to reconstruct what the system did and why |
| Access | Controlled ability to inspect or operate on data |

This module does **not** determine whether a particular record legally qualifies for deletion. That decision comes from approved policy.

---

# 4. What Does "Delete User Data" Actually Mean?

Suppose Alice has data in:

```text
PostgreSQL
Data warehouse
Lakehouse
Kafka
Redis
Feature store
Vector database
Application logs
Analytics tables
Backups
```

Then:

```sql
DELETE FROM users WHERE user_id = 'Alice';
```

is only one operation in a much larger system.

A realistic dependency graph is:

```text
                     User
                       |
          +------------+-------------+
          |            |             |
       Source DB     Events       Identity IDs
          |            |             |
          v            v             v
       CDC/Kafka    Raw Storage   Other Systems
          |            |
          v            v
       Lakehouse --> Warehouse
          |            |
          v            v
      Features      Aggregates
          |            |
          v            v
      ML/RAG       Dashboards
          |
          v
     Vector Index
          |
          v
        Cache
```

The design problem is therefore:

> **Find every relevant copy, understand how it was derived, execute the policy-defined deletion action, and prove the required post-condition.**

---

# 5. The Authoritative 30-Day Requirement

The case requirement is:

> **Delete a user's data from every relevant data system within 30 days of the request — and prove it.**

Treat the 30 days as the authoritative case requirement, not as a universal legal statement.

Define:

```text
Request received
      |
      v
SLA clock starts
      |
      v
Deadline = request time + 30 days
```

Track at minimum:

- request ID
- received timestamp
- subject identifier
- policy version
- systems discovered
- systems completed
- systems failed
- systems awaiting verification
- exception state
- remaining time
- escalation state
- final completion timestamp

Operational states:

```text
HEALTHY
AT_RISK
BREACHED
```

A mature system does not wait until day 29 to discover a blocked deletion.

---

# 6. Personal Data Inventory

A deletion platform cannot delete what the organization does not know exists.

A useful inventory contains:

| Field | Purpose |
|---|---|
| System | Registered data system |
| Dataset | Database/table/topic/index |
| Column/field | Location of relevant data |
| Data type | Identifier, event, feature, etc. |
| Personal-data classification | Determines policy treatment |
| User identifier | How a subject is represented |
| Owner | Team accountable for operation |
| Deletion mechanism | API, SQL, rewrite, retention, etc. |
| Verification method | How post-condition is checked |
| Retention policy | Policy-controlled lifecycle |
| Lineage | Upstream/downstream relationships |
| SLA | Expected completion time |

Example:

| System | Dataset | User Data? | Owner | Deletion | Verification |
|---|---|---:|---|---|---|
| PostgreSQL | users | Yes | App | SQL DELETE | Key lookup |
| Warehouse | orders | Yes | Analytics | DELETE/MERGE | Query |
| Lakehouse | events | Yes | Data Platform | Rewrite/DELETE | Scan |
| Redis | sessions | Yes | Platform | Key invalidation | GET |
| Kafka | events | Maybe | Streaming | Policy-specific | Materialization check |
| Vector DB | chunks | Yes | AI Platform | ID delete/reindex | Retrieval test |

### The completeness problem

Avoid:

> "We think we found all systems."

Prefer:

> "We can demonstrate that every registered system was evaluated, and unknown/unregistered systems are detected through governance controls."

That is a materially stronger system-design answer.

---

# 7. Data Classification

Deletion treatment depends on how data is classified.

Useful engineering categories:

- direct identifiers
- personal data
- sensitive data
- pseudonymous identifiers
- device identifiers
- derived data
- aggregated data
- anonymous/non-identifying data
- operational metadata

Example identity chain:

```text
Canonical user
   |
   +--> email
   |
   +--> phone
   |
   +--> device_id
   |
   +--> cookie_id
   |
   +--> account_id
   |
   +--> session_id
   |
   +--> derived feature
```

A hash is not automatically "anonymous." If an identifier remains linkable to a person through available mappings, the organization must apply its approved policy to that data.

---

# 8. Identity Resolution

Identity resolution is one of the hardest parts of the problem.

One person can have:

```text
Customer ID: C123
Email: alice@example.com
Device IDs: D1, D2
Cookie IDs: K1, K2
Account IDs: A9
```

A conceptual identity graph:

```text
                 +------------------+
                 | Canonical C123   |
                 +---------+--------+
                           |
             +-------------+-------------+
             |             |             |
           Email        Devices        Accounts
             |             |             |
             v             v             v
          Data A        Data B         Data C
```

The identity system needs:

- canonical identity
- aliases
- historical identifiers
- merged-account handling
- deleted-account handling
- mapping freshness
- confidence/authority rules
- protection against over-broad matches

### Critical safety principle

A deletion platform must not interpret "find everything that looks similar" as permission to delete it.

Identity resolution should produce a **bounded, explainable subject scope**.

---

# 9. Data Lineage

Lineage answers:

> **Where did this data come from, and where did it go?**

Example:

```text
Application DB
     |
     v
    CDC
     |
     v
   Kafka
     |
     v
 Lakehouse
     |
     v
 Warehouse
     |
     v
 Dashboard
```

Another path:

```text
User data
   |
   v
Feature pipeline
   |
   v
Feature store
   |
   v
Training dataset
   |
   v
Model artifact
```

A deletion platform needs enough lineage to discover downstream copies and derived artifacts.

### Lineage quality checks

Detect:

- missing lineage
- stale metadata
- unknown datasets
- unowned datasets
- broken edges
- undocumented derived datasets

> **Unknown data is a privacy risk.**

---

# 10. Source vs Derived Data

Do not treat every store as an isolated system.

Think in terms of a dependency graph:

```text
Source
  |
  v
CDC / Events
  |
  v
Raw storage
  |
  v
Transformations
  |
  v
Aggregates
  |
  v
Features
  |
  v
Embeddings
  |
  v
Indexes
  |
  v
Caches
```

Deleting the source does not automatically delete every artifact derived from it.

The policy must define which derived artifacts require:

- physical deletion
- correction/recomputation
- invalidation
- retention
- exception handling
- evidence only

---

# 11. System-by-System Deletion Matrix

| System type | Typical mechanism | Core difficulty | Verification |
|---|---|---|---|
| PostgreSQL/MySQL | DELETE/CASCADE | Relationships, locks, scale | Query |
| NoSQL | Key/partition deletion | Secondary indexes, access paths | Key lookup |
| Warehouse | DELETE/MERGE/rebuild | Derived tables, materializations | Query/scan |
| Lakehouse | DELETE/MERGE/rewrite | Files, snapshots, time travel | Table + physical lifecycle checks |
| Kafka | Retention/compaction/tombstone/design | Append-only history and replay | Downstream/materialized-state check |
| Redis | Key deletion/invalidation | Unknown key patterns | GET/scan |
| Memcached | Invalidation/TTL | Ephemeral copies | Key lookup |
| Feature store | Online/offline deletion | Materializations/training data | Point lookup + dataset scan |
| Vector DB | ID/metadata deletion/reindex | Index state and retrieval | Retrieval test |
| Search index | Document/index deletion | Secondary copies | Search test |
| Logs | Redaction/retention/policy strategy | Centralized/immutable stores | Query/retention verification |
| Backups | Policy-specific lifecycle | Historical copies | Backup inventory/policy state |
| Immutable store | Policy/retention mechanism | Physical deletion may be constrained | Retention/exception evidence |

---

# 12. Operational Database Deletion

Basic example:

```sql
DELETE FROM users
WHERE user_id = '123';
```

Real systems introduce:

- child tables
- foreign keys
- soft deletes
- hard deletes
- cascading deletes
- transaction boundaries
- lock contention
- large-table performance
- replication
- CDC propagation
- batch deletion

Example child discovery:

```sql
SELECT o.order_id
FROM orders AS o
WHERE o.user_id = '123';
```

A safer production pattern may be:

1. Resolve the canonical subject.
2. Enumerate affected tables.
3. Preview row counts.
4. Execute bounded deletion batches.
5. Commit.
6. Verify source and child records.
7. Verify downstream CDC/materialization effects.

### Soft vs hard delete

| Approach | Meaning | Benefit | Risk |
|---|---|---|---|
| Soft delete | Record remains with deletion state | Operationally simple | Data still exists |
| Hard delete | Record is physically removed | Stronger removal | More operational risk |
| Tombstone | Deletion event propagates | Useful for distributed systems | Downstream consumers must honor it |

A soft-delete flag is not automatically equivalent to physical deletion.

---

# 13. Lakehouse Deletion

A logical table row and physical object-storage bytes are different layers.

```text
Logical deletion
       |
       v
Table metadata changes
       |
       v
Old files may remain temporarily
       |
       v
Retention / compaction / cleanup
       |
       v
Physical lifecycle
```

Important concepts:

- object storage
- Parquet files
- Delta/Iceberg/Hudi-style tables
- partitions
- DELETE/MERGE
- file rewrites
- compaction
- snapshots
- time travel
- metadata logs
- retention and cleanup

Interview principle:

> **A successful row-level delete does not automatically prove that historical physical bytes are gone.**

The correct treatment depends on policy, table-format lifecycle, retention controls, and evidence requirements.

---

# 14. Warehouse Deletion

Warehouse deletion must consider both source records and derived artifacts.

```text
Raw user data
      |
      v
Daily user metrics
      |
      v
Company dashboard
```

Possible mechanisms:

- DELETE
- MERGE
- partition replacement
- materialized-view refresh/rebuild
- derived-table recomputation
- policy-defined aggregate correction

For aggregates, do not invent a universal legal answer. Instead ask:

> Does approved policy classify this derived result as still attributable to the subject, and what correction strategy does policy require?

Technical options include:

- recompute affected window
- incremental correction
- rebuild aggregate
- retain aggregate if policy explicitly permits
- record the decision and evidence

---

# 15. Kafka and Event Streams

A database row has a direct deletion primitive. An append-only event stream usually does not.

```text
DELETE FROM table WHERE user_id = ...
```

is fundamentally different from:

```text
Delete one historical Kafka record
```

Relevant mechanisms:

- retention
- compaction
- tombstones
- topic replay
- consumer offsets
- downstream materialization
- reprocessing
- event-level privacy architecture

Possible design choices:

1. Minimize personal data in immutable events.
2. Use identifiers that permit controlled downstream invalidation.
3. Propagate deletion tombstones to materialized views.
4. Use retention to age out event copies where policy permits.
5. Rebuild downstream state when required.
6. Avoid pretending a tombstone physically erases every historical byte.

The right choice follows the requirement and event architecture.

---

# 16. Cache Deletion

Caches are copies.

Key problems:

- key discovery
- naming conventions
- aliases
- TTL
- replicas
- stale reads
- cache rebuilds

Educational Redis-style example:

```python
def invalidate_user_cache(redis_client, user_id: str) -> int:
    """
    Educational example.
    Production systems should use an approved, bounded key strategy
    rather than scanning arbitrary production keys.
    """
    keys = [
        f"user:{user_id}",
        f"profile:{user_id}",
        f"session:{user_id}",
    ]

    deleted = 0
    for key in keys:
        deleted += int(redis_client.delete(key))
    return deleted
```

A good platform standardizes cache-key contracts so deletion does not depend on undocumented conventions.

---

# 17. Feature Store Deletion

Consider:

```text
User
  |
  v
Feature pipeline
  |
  +--> Offline features
  |
  +--> Online features
  |
  v
Training datasets
```

Deletion may require:

- online feature removal
- offline feature removal
- historical training-data treatment
- feature materialization cleanup
- point-in-time dataset correction
- backfill/rebuild
- model-training policy decision

Do not claim every model must automatically be retrained after every deletion. The organization's approved policy determines model treatment.

---

# 18. Vector Store and RAG Deletion

A RAG pipeline may look like:

```text
Document
   |
   v
Chunks
   |
   v
Embeddings
   |
   v
Vector index
   |
   v
Retrieval
   |
   v
AI application
```

Deletion must consider:

- source document
- chunks
- embedding records
- metadata
- vector IDs
- secondary indexes
- cached retrieval results
- index rebuilds
- incremental reindexing

Verification should test the actual retrieval path:

```text
Deleted document
      |
      v
Search/retrieval query
      |
      v
Expected result: content is not retrievable
```

A metadata flag saying `deleted=true` is not enough if the serving layer still returns the content.

---

# 19. Log Deletion

Logs are frequently overlooked.

Examples:

```text
Application logs
Access logs
Error logs
Debug logs
Analytics logs
Audit logs
```

Engineering challenges:

- PII embedded in messages
- centralized logging
- retention
- immutable storage
- redaction limits
- replicas and archives
- broad search surfaces

Privacy-by-design principle:

> **The best way to delete sensitive data from logs is often to avoid logging it unnecessarily.**

Where policy requires treatment of existing logs, the system needs a documented retention/redaction/deletion strategy rather than an assumption that logs are disposable.

---

# 20. Backups and Disaster-Recovery Copies

Copies can exist in:

```text
Production
   |
   +--> Full backup
   |
   +--> Incremental backup
   |
   +--> Snapshot
   |
   +--> DR replica
   |
   +--> Archive
```

Backups are especially difficult because they may be immutable, operationally expensive to rewrite, or retained under a policy that differs from primary storage.

The engineering model should represent:

```text
Data item
   |
   v
Retention policy
   |
   v
Deletion eligibility
   |
   +--> Exception?
   |
   v
Expiration / lifecycle
   |
   v
Evidence
```

Do not invent a blanket rule that every backup must be immediately rewritten. Treat backup handling as policy-driven.

---

# 21. Immutable Storage

There is a real design tension:

```text
Deletion requirement
        vs
Immutable retention requirement
```

Relevant concepts:

- append-only stores
- WORM-style storage
- object lock
- compliance archives
- immutable audit logs

The design response is not "delete anyway."

Instead:

1. Identify the policy controlling the immutable copy.
2. Determine whether deletion is technically possible.
3. Represent the exception explicitly.
4. Apply the approved retention/expiration mechanism.
5. Capture evidence.
6. Escalate when policy and system capability conflict.

---

# 22. Crypto-Shredding

Conceptually:

```text
Data
  |
  v
Encryption
  |
  v
Encrypted storage
  |
  v
Controlled encryption key
  |
  v
Key destruction
  |
  v
Encrypted bytes become computationally unusable
```

Potentially useful design dimensions:

- key hierarchy
- tenant-level keys
- per-user keys where operationally appropriate
- key rotation
- key destruction
- KMS/HSM-style key management
- escrow
- backup copies of keys

Crypto-shredding is **not** a universal replacement for deletion. It is a technique whose suitability depends on policy, threat model, key architecture, evidence requirements, and the organization's approved privacy design.

---

# 23. Data Discovery Architecture

A mature deletion platform combines:

```text
Data Catalog
     |
Schema Registry
     |
Application Registry
     |
Ownership Registry
     |
Identity Graph
     |
Lineage Graph
     |
Manual Exceptions
     |
     v
Deletion Discovery Service
```

The goal is not perfect omniscience.

The goal is a defensible control plane that can answer:

- What systems are registered?
- Which datasets contain relevant identifiers?
- Who owns them?
- What deletion contract do they expose?
- What downstream copies exist?
- What systems are unknown?
- Which systems require manual review?

---

# 24. Deletion Contracts

Every registered system should expose a standardized contract.

Example:

```text
System name
Owner
Data categories
Identifier format
Deletion API
Expected completion time
Retry semantics
Verification method
Failure semantics
Retention exceptions
```

This converts the platform from:

```text
100 one-off scripts
```

into:

```text
One orchestration platform
+
standard system contracts
+
system-specific adapters
```

### Contract example

```python
from dataclasses import dataclass
from typing import Protocol


class DeletionAdapter(Protocol):
    def delete(self, subject_id: str, operation_id: str) -> None:
        ...

    def verify(self, subject_id: str, operation_id: str) -> bool:
        ...


@dataclass
class DeletionResult:
    system: str
    success: bool
    verification_passed: bool
    detail: str
```

The actual adapter implementation belongs to the owning system; the central platform should not assume every system shares the same deletion primitive.

---

# 25. Deletion Orchestration

Central workflow:

```text
Request
  |
  v
Validate
  |
  v
Resolve Identity
  |
  v
Discover Systems
  |
  v
Build Deletion Plan
  |
  v
Execute
  |
  +----> Retry
  |
  +----> Escalate
  |
  v
Verify
  |
  v
Evidence
  |
  v
Complete / Exception / Escalate
```

Useful orchestration capabilities:

- state machine
- task dependencies
- parallel branches
- idempotency
- retries
- timeouts
- dead-letter handling
- manual review
- escalation
- deadline awareness

---

# 26. Deletion State Machine

```text
REQUESTED
   |
   v
VALIDATED
   |
   v
IDENTITY_RESOLVED
   |
   v
SYSTEMS_DISCOVERED
   |
   v
DELETION_IN_PROGRESS
   |
   v
VERIFICATION
   |
   v
COMPLETED
```

Exceptional states:

```text
FAILED
RETRYING
BLOCKED
EXCEPTION_REVIEW
ESCALATED
```

Suggested semantics:

| State | Meaning |
|---|---|
| REQUESTED | Request received |
| VALIDATED | Request passed required policy/authentication checks |
| IDENTITY_RESOLVED | Subject scope established |
| SYSTEMS_DISCOVERED | Registered systems evaluated |
| DELETION_IN_PROGRESS | At least one required action remains |
| RETRYING | A transient failure is being retried |
| VERIFICATION | Execution finished for a system and post-condition is being checked |
| BLOCKED | Policy or dependency prevents progress |
| EXCEPTION_REVIEW | Explicit retention or policy exception requires review |
| ESCALATED | Owner/incident path engaged |
| COMPLETED | Required policy-defined post-conditions satisfied |
| FAILED | Workflow cannot progress automatically |

---

# 27. Idempotency

Deletion workers can execute the same operation more than once.

Example:

```text
Delete PostgreSQL data
        |
        v
Database succeeds
        |
        v
Worker crashes before reporting success
        |
        v
Workflow retries
        |
        v
Delete PostgreSQL data again
```

The operation should ideally be safe to repeat.

Educational example:

```python
def delete_user(records: dict[str, dict], user_id: str) -> bool:
    # Safe to call repeatedly: deleting an absent key is not an error.
    records.pop(user_id, None)
    return True
```

For a production system, use:

- request ID
- operation ID
- idempotency key
- durable operation state
- deterministic subject scope
- bounded retry semantics

Do not use "exactly once" as a magic phrase. Design for safe repetition.

---

# 28. Retry Strategy

Classify failures:

```text
Transient
  -> retry

Permanent
  -> fail / escalate

Policy block
  -> exception review

Unknown
  -> contain + investigate
```

A typical retry policy:

```text
attempt 1 -> immediate
attempt 2 -> short delay
attempt 3 -> longer delay
...
maximum attempts
        |
        v
dead-letter / escalation
```

Use exponential backoff and jitter where appropriate.

Retrying can make things worse when:

- the downstream system is overloaded
- the operation is not idempotent
- the failure is permanent
- rate limits are being exceeded
- a deletion has an unintended broad scope

---

# 29. Partial Failure

Example:

```text
PostgreSQL       ✓
Warehouse        ✓
Lakehouse        ✓
Redis            ✓
Kafka            ✗
Feature Store    ✓
Vector DB        ✗
```

The request is **not complete**.

The workflow must retain per-system state:

```text
system
operation_id
attempts
last_error
next_retry
completion
verification
owner
```

This enables:

- failure isolation
- targeted retry
- escalation
- SLA monitoring
- evidence generation

---

# 30. Deletion Plan

A durable deletion plan might conceptually contain:

```json
{
  "request_id": "REQ-123",
  "subject_id": "USER-456",
  "deadline": "2026-11-01T00:00:00Z",
  "policy_version": "v3",
  "systems": [
    "postgres",
    "warehouse",
    "lakehouse",
    "redis",
    "kafka",
    "feature_store",
    "vector_store"
  ]
}
```

Do not expose unnecessary personal data in orchestration metadata.

The plan should reference the subject using a controlled identifier and keep the evidence surface minimized.

---

# 31. Dependency-Aware Deletion DAG

A conceptual DAG:

```text
Identity Resolution
        |
        v
Source Deletion
        |
        v
CDC / Event Propagation
        |
        v
Derived Data
   |          |
   v          v
Features    Aggregates
   |          |
   v          v
Vectors    Search
      \      /
       \    /
     Verification
```

But many operations can run in parallel.

Example:

```text
                  Identity Resolved
                         |
          +--------------+---------------+
          |              |               |
          v              v               v
      PostgreSQL       Redis          Vector DB
          |              |               |
          v              v               v
      Warehouse      Feature Store     Search
          \              |              /
           \             |             /
            +------------+------------+
                         |
                         v
                    Verification
```

Parallelism improves throughput but requires explicit dependency and rate-limit controls.

---

# 32. Verification

> **A delete API returning success is not proof of deletion.**

Verification methods include:

- direct query
- key lookup
- count check
- metadata check
- search query
- vector retrieval test
- downstream materialization check
- object/table scan
- retention-state verification

A useful pattern:

```text
Deletion execution
       |
       v
Independent verification
       |
       v
Expected post-condition?
       |
    +--+--+
    |     |
   Yes    No
    |     |
    v     v
Evidence Retry/Escalate
```

Verification should be as independent as practical from the code path that performed deletion.

---

# 33. Proving Deletion

The case explicitly requires:

> "...and proves it."

A deletion certificate can contain:

```json
{
  "request_id": "REQ-123",
  "completed_at": "2026-10-20T12:30:00Z",
  "systems_checked": 14,
  "systems_deleted": 14,
  "verification_status": "PASSED",
  "exceptions": [],
  "policy_version": "v3"
}
```

Evidence should normally include:

- request ID
- controlled subject reference
- timestamps
- systems discovered
- deletion operations
- operation results
- verification results
- retries
- exceptions
- completion time
- policy version

Avoid placing the deleted personal data back into the certificate merely to "prove" it was deleted.

Protect evidence using:

- access controls
- encryption
- tamper-evident mechanisms where appropriate
- retention policy
- audit logging

---

# 34. Audit Certificate Design

A certificate is an **evidence artifact**, not a second copy of the user's data.

A useful certificate answers:

```text
What request?
Which policy?
Which systems?
Which operations?
Which verifications?
Which exceptions?
When completed?
Who/what performed the operations?
```

A certificate should not become an uncontrolled privacy-data store.

---

# 35. Retention Exceptions

Do not hard-code universal deletion assumptions.

Examples that may require policy evaluation include:

- legal retention
- security/audit obligations
- regulatory retention
- contractual retention

Represent policy state explicitly:

```text
Data item
   |
   v
Retention policy
   |
   v
Deletion eligibility
   |
   +----> Exception
   |
   v
Expiration date
   |
   v
Evidence
```

Engineering must implement the organization's approved policy; it does not decide the policy.

---

# 36. Aggregates and Derived Data

Example:

```text
Daily revenue = ₹10,000
One user contributed ₹100
```

The engineering question is not automatically "subtract ₹100."

Ask:

1. Does policy classify the aggregate as attributable to the user?
2. Can the contribution be isolated?
3. Is recomputation required?
4. Is incremental correction acceptable?
5. Does an immutable aggregate require an exception?

Technical options:

- recompute
- incremental correction
- affected-window rebuild
- policy-defined retention

---

# 37. ML Systems

Conceptual chain:

```text
User data
   |
   v
Training dataset
   |
   v
Features
   |
   v
Model
```

Possible engineering actions:

- delete source training records
- update feature stores
- rebuild affected training datasets
- track model lineage
- retrain where policy requires
- evaluate whether machine unlearning is required by the approved policy

Do not claim that every deletion automatically requires retraining every model.

The key system-design principle is **lineage plus policy-driven treatment**.

---

# 38. RAG and AI Systems

RAG adds another copy chain:

```text
Source
  |
  v
Document
  |
  v
Chunk
  |
  v
Embedding
  |
  v
Vector Index
  |
  v
Retrieval Cache
  |
  v
Application
```

Deletion must consider:

- source document
- chunks
- embeddings
- metadata
- index state
- cache
- retrieval results
- downstream replicas

Verification should test retrieval, not merely storage metadata.

---

# 39. Security and Privilege Model

The deletion platform is itself high-impact.

A compromised service could delete enormous amounts of data.

Use:

- authentication
- authorization
- least privilege
- scoped service identities
- secrets management
- encryption
- audit logs
- separation of duties

Prefer:

```text
Deletion Service
      |
      v
Approved deletion APIs
      |
      v
Scoped system permissions
```

over:

```text
Deletion Service
      |
      v
Arbitrary access to every production database
```

---

# 40. Safety and Blast-Radius Controls

Controls should include:

- request authentication
- scope preview
- dry-run
- allowlists
- maximum batch size
- rate limits
- idempotency
- approval gates where policy requires
- canary execution where appropriate
- kill switch
- audit logging
- verification

Trade-off:

```text
Fast deletion
     vs
Safe deletion
```

For destructive systems, correctness and blast-radius control are part of the SLA story.

---

# 41. Dry-Run Mode

A dry-run should discover what **would** happen without mutating data.

```text
Request
  |
  v
Identity resolution
  |
  v
Discovery
  |
  v
Dry-run
  |
  +--> PostgreSQL
  +--> Warehouse
  +--> Lakehouse
  +--> Redis
  +--> Vector DB
  |
  v
Scope review / approval
  |
  v
Execution
```

Useful dry-run output:

- systems found
- datasets found
- expected record counts
- deletion mechanism
- owner
- estimated cost
- policy exceptions
- verification method

---

# 42. Observability and SLA Management

Track:

- requests received
- requests completed
- completion latency
- P95 completion time
- SLA compliance
- failed tasks
- retry count
- repeated failing systems
- verification failures
- discovery failures
- unknown systems
- exceptions
- backlog
- requests near deadline

A useful dashboard:

```text
Deletion Operations
-------------------
Open requests
At-risk requests
Breached requests
P95 completion time
Top failing systems
Verification failures
Unknown datasets
Exception backlog
```

Alert on **remaining SLA time**, not only task failures.

---

# 43. Scale Estimation

All values below are illustrative assumptions, not roadmap facts.

Suppose:

```text
100,000 deletion requests / month
```

Then approximately:

```text
100,000 / 30
≈ 3,333 / day

3,333 / 24
≈ 139 / hour

139 / 60
≈ 2.3 / minute
```

Now introduce:

```text
20 systems / user
50,000 records / user across all systems
5 verification operations / system
```

The system must distinguish:

```text
Request throughput
vs
System-operation throughput
vs
Verification throughput
```

The multiplication factor can be substantial.

### SLA capacity

If the platform receives `R` requests/day, has `S` system operations/request, and each worker completes `W` operations/hour:

```text
operations/day = R × S
workers_needed ≈ operations/day / (24 × W)
```

Add headroom for:

- retries
- bursts
- maintenance
- rate limits
- verification
- 10× growth

Never present a single worker capacity number as universally true.

---

# 44. 10× Scale

Ask what changes if:

```text
10× requests
10× systems
10× records/user
```

Potential bottlenecks:

- identity service
- metadata catalog
- workflow engine
- database deletion rate
- object-storage scans
- warehouse compute
- vector-index rebuilds
- API rate limits
- verification
- evidence storage

Responses:

- horizontal workers
- partitioned workflow queues
- precomputed identity mappings
- metadata-driven targeting
- bounded parallelism
- incremental deletion
- indexed lookup
- partition pruning
- backpressure
- priority queues for deadline risk

The design should scale the **control plane and data-plane operations independently**.

---

# 45. Cost Engineering

Cost drivers:

- database operations
- storage scans
- lakehouse rewrites
- warehouse queries
- index rebuilds
- verification scans
- orchestration infrastructure
- cross-region transfer

Optimization strategies:

- indexed lookup
- partition pruning
- metadata-driven targeting
- incremental deletion
- batch operations
- bounded parallelism
- precomputed identity mappings
- deletion-aware data architecture

Never optimize cost by weakening correctness.

---

# 46. Failure Scenarios

Use the standard incident loop:

```text
Detect
  ->
Contain
  ->
Diagnose
  ->
Recover
  ->
Verify
  ->
Evidence
  ->
Prevent
```

### 1. Identity service unavailable

**Detection:** identity-resolution task times out.  
**Containment:** do not execute deletion against an uncertain identity scope.  
**Recovery:** retry with bounded backoff; escalate if deadline risk rises.  
**Verification:** confirm identity scope before resuming.  
**Prevention:** redundancy and cached-but-controlled identity mappings.

### 2. Data catalog unavailable

Pause discovery rather than claiming completeness. Use approved cached metadata only if its freshness guarantees satisfy policy.

### 3. PostgreSQL deletion fails

Classify transient vs permanent. Retry only if safe; otherwise escalate to owner.

### 4. Warehouse deletion fails

Check locks, resource limits, query failures, and dependency ordering. Do not close the request because source DB succeeded.

### 5. Lakehouse rewrite fails

Check job state, storage access, table conflicts, partition scope, and cleanup policy.

### 6. Kafka system unavailable

Record unresolved stream state. Do not fabricate successful event deletion.

### 7. Redis unavailable

Track cache deletion as incomplete; do not assume TTL means immediate removal.

### 8. Feature store unavailable

Keep online/offline feature tasks independently visible and retryable.

### 9. Vector store unavailable

Prevent verification from being marked passed. Escalate if retrieval may still expose deleted content.

### 10. Logs unavailable

Record the failure of the deletion evidence path separately from the underlying deletion result.

### 11. Backup deletion impossible

Evaluate approved retention policy and record an explicit exception/expiry path.

### 12. Verification fails

Treat as incomplete even if deletion returned success.

### 13. Duplicate request

Deduplicate using request/subject policy and idempotent workflow semantics.

### 14. Worker crashes

Resume from durable operation state.

### 15. Workflow state is lost

Recover from durable request and system-operation records; never infer completion from absence of an active worker.

### 16. System owner does not respond

Escalate according to ownership hierarchy and deadline risk.

### 17. New system discovered late

Add it to the deletion plan, assess blast radius, execute the deletion contract, and improve inventory governance.

### 18. Schema changes during deletion

Version contracts and fail safely when identifiers or paths change unexpectedly.

### 19. Multiple identities exist

Re-run identity resolution and verify the canonical mapping before broadening scope.

### 20. Request approaches deadline

Promote priority, increase bounded parallelism, notify owners, and escalate before breach.

### 21. Retention exception applied incorrectly

Stop the affected operation, open policy review, and correct the decision before closure.

### 22. Deletion succeeds but evidence generation fails

Do not conflate data deletion with evidence generation. Recover evidence from durable operation state without recreating deleted data.

---

# 47. Break/Fix Labs

## Lab 1 — Missing downstream system

**Broken:** lineage omits a derived table.  
**Symptoms:** certificate says all registered systems passed, but a downstream scan finds data.  
**Investigation:** compare lineage inventory with runtime datasets.  
**Root cause:** incomplete registration.  
**Fix:** add ownership and lineage contract.  
**Verification:** re-run discovery and deletion.  
**Prevention:** lineage-quality monitoring.

## Lab 2 — Duplicate deletion request

**Broken:** same subject/request is submitted twice.  
**Fix:** request deduplication + idempotent operations.

## Lab 3 — Failed database deletion

Inject a transient database error. Verify retry, backoff, eventual success, and audit trail.

## Lab 4 — Lakehouse residual data

Logical deletion succeeds, but historical files remain under policy-controlled retention. Determine whether cleanup is required and document evidence.

## Lab 5 — Kafka downstream copy remains

Source deletion succeeds, but a materialized consumer still contains the user. Trace replay/materialization behavior.

## Lab 6 — Redis cache survives

Invalidate known keys, discover an undocumented key, and fix the cache-key contract.

## Lab 7 — Vector index still returns deleted content

Delete source and metadata but intentionally leave the index stale. Retrieval verification must fail.

## Lab 8 — Feature store residual

Online feature is removed but offline feature remains. Reconcile both planes.

## Lab 9 — Backup contains user data

Apply a mock retention exception and verify the certificate records the policy-controlled outcome.

## Lab 10 — False verification success

Make deletion and verification read the same stale cache. Redesign verification independence.

## Lab 11 — SLA at risk

Artificially slow three system adapters. Prioritize by deadline risk and demonstrate escalation.

## Lab 12 — Identity alias missed

Add a historical device ID not present in the primary mapping. Discovery must detect the incomplete identity graph.

---

# 48. Testing Strategy

A production-quality deletion platform needs:

### Unit tests

- identity mapping
- state transitions
- idempotency
- retry policy
- SLA calculation

### Integration tests

- database adapter
- warehouse adapter
- lakehouse adapter
- cache adapter
- vector adapter

### Contract tests

Every system must satisfy:

```text
delete()
verify()
failure semantics
idempotency semantics
owner metadata
retention metadata
```

### End-to-end tests

Simulate:

```text
Request
 -> Identity
 -> Discovery
 -> Deletion
 -> Verification
 -> Certificate
```

### Failure-injection tests

Inject:

- timeout
- 500 response
- permission failure
- rate limit
- worker crash
- stale metadata
- missing lineage
- verification mismatch

### Safety tests

Verify:

- dry-run does not mutate
- unauthorized request is rejected
- batch limits work
- wrong subject cannot be selected
- kill switch works
- approval gates work

---

# 49. SQL Practice Examples

> These examples are educational. Adapt syntax and transaction semantics to the actual engine.

### Find a user's records

```sql
SELECT *
FROM users
WHERE user_id = '123';
```

### Find child records

```sql
SELECT order_id
FROM orders
WHERE user_id = '123';
```

### Hard deletion

```sql
DELETE FROM orders
WHERE user_id = '123';

DELETE FROM users
WHERE user_id = '123';
```

### Soft deletion

```sql
UPDATE users
SET deleted_at = CURRENT_TIMESTAMP
WHERE user_id = '123';
```

### Residual-data verification

```sql
SELECT COUNT(*) AS remaining_rows
FROM users
WHERE user_id = '123';
```

### Derived-table verification

```sql
SELECT COUNT(*) AS remaining_rows
FROM user_daily_metrics
WHERE user_id = '123';
```

### Reconciliation

```sql
SELECT
    system_name,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status <> 'COMPLETED' THEN 1 ELSE 0 END) AS incomplete
FROM deletion_operations
WHERE request_id = 'REQ-123'
GROUP BY system_name;
```

### SLA monitoring

```sql
SELECT
    request_id,
    deadline,
    CURRENT_TIMESTAMP AS now,
    CASE
        WHEN CURRENT_TIMESTAMP >= deadline THEN 'BREACHED'
        WHEN CURRENT_TIMESTAMP >= deadline - INTERVAL '3 days' THEN 'AT_RISK'
        ELSE 'HEALTHY'
    END AS sla_status
FROM deletion_requests
WHERE status <> 'COMPLETED';
```

---

# 50. Python: Retry and Idempotent Orchestration

```python
from dataclasses import dataclass
from time import sleep
import random


@dataclass
class OperationResult:
    system: str
    success: bool
    detail: str


def retry(operation, attempts=5, base_delay=0.5):
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break

            delay = base_delay * (2 ** (attempt - 1))
            delay *= random.uniform(0.8, 1.2)
            sleep(delay)

    raise last_error
```

The retry policy should be restricted to operations whose semantics are safe to repeat.

### Adapter model

```python
class DeletionAdapter:
    name = "abstract"

    def delete(self, subject_id: str, operation_id: str) -> OperationResult:
        raise NotImplementedError

    def verify(self, subject_id: str, operation_id: str) -> bool:
        raise NotImplementedError
```

### Mock in-memory adapter

```python
class MockAdapter(DeletionAdapter):
    def __init__(self, name, records):
        self.name = name
        self.records = records

    def delete(self, subject_id, operation_id):
        self.records.pop(subject_id, None)
        return OperationResult(self.name, True, "deleted-or-already-absent")

    def verify(self, subject_id, operation_id):
        return subject_id not in self.records
```

This illustrates the important property:

```text
delete(delete(x)) == delete(x)
```

---

# 51. Python: Deletion DAG Concept

```python
from collections import defaultdict, deque


def topological_order(nodes, dependencies):
    graph = defaultdict(list)
    indegree = {node: 0 for node in nodes}

    for node, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(node)
            indegree[node] += 1

    queue = deque(node for node in nodes if indegree[node] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for child in graph[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    if len(order) != len(nodes):
        raise ValueError("Dependency graph contains a cycle")

    return order
```

In production, independent nodes should often execute concurrently with bounded parallelism rather than strictly sequentially.

---

# 52. Python: SLA Tracking

```python
from datetime import datetime, timedelta, timezone


def deletion_deadline(received_at: datetime) -> datetime:
    return received_at + timedelta(days=30)


def sla_status(now: datetime, deadline: datetime) -> str:
    if now >= deadline:
        return "BREACHED"

    remaining = deadline - now

    if remaining <= timedelta(days=3):
        return "AT_RISK"

    return "HEALTHY"


received = datetime.now(timezone.utc)
deadline = deletion_deadline(received)

print(deadline)
print(sla_status(datetime.now(timezone.utc), deadline))
```

---

# 53. PySpark / Distributed Data Example

A simplified distributed dataset might contain multiple user records:

```python
from pyspark.sql import functions as F

user_id = "USER-123"

affected = (
    events
    .filter(F.col("user_id") == user_id)
)

affected_count = affected.count()
print("Rows requiring policy-defined treatment:", affected_count)
```

A conceptual reconstruction pattern:

```python
remaining = events.filter(F.col("user_id") != user_id)

# In a real lakehouse, this could require a table-format-specific
# DELETE/MERGE/rewrite strategy and retention/cleanup policy.
(
    remaining
    .write
    .mode("overwrite")
    .partitionBy("event_date")
    .parquet("/example/output")
)
```

The important engineering lesson is not the toy write. It is that large-scale deletion can become a distributed rewrite problem, with implications for compute, object storage, concurrent writers, table metadata, snapshots, and verification.

---

# 54. Practical Mini-Project — Simplified GDPR Deletion Platform

Build a safe educational implementation entirely as a local/mock system.

## Components

```text
Mock User DB
Mock Warehouse
Mock Lakehouse
Mock Redis
Mock Kafka-derived dataset
Mock Feature Store
Mock Vector Store
Identity Mapping
Data Inventory
Deletion Orchestrator
Verification
Audit Certificate
SLA Monitor
Dry-run Mode
Failure Injection
```

## Suggested data model

```text
users
orders
events
features
vectors
cache_entries
identity_aliases
data_assets
deletion_requests
deletion_operations
verification_results
audit_certificates
```

## Workflow

```text
POST /deletion-request
        |
        v
validate
        |
        v
resolve_identity
        |
        v
discover_assets
        |
        v
dry_run
        |
        v
execute
        |
        v
verify
        |
        v
certificate
```

## Required failure injections

1. Database timeout.
2. Missing identity alias.
3. Vector deletion failure.
4. Verification mismatch.
5. Worker crash simulation.
6. At-risk SLA.

## Expected outputs

A successful run should produce:

```text
Request ID
Subject scope
Assets discovered
Operations attempted
Retries
Verification results
Exceptions
Completion timestamp
Policy version
Certificate status
```

### Extensions

- parallel worker pool
- priority queue
- lineage graph
- system ownership registry
- policy versioning
- signed/tamper-evident evidence
- cost estimator
- 10× load test
- chaos testing

---

# 55. Requirements Clarification for the Interview

Before drawing architecture, ask:

### Policy

1. What does "deleted" mean operationally?
2. Is the 30-day deadline hard for this exercise?
3. What retention exceptions exist?
4. Who defines those exceptions?
5. Are there categories of data with different treatment?

### Identity

6. What identifiers identify a person?
7. Are historical aliases available?
8. Are accounts merged?
9. How reliable is identity resolution?

### Data landscape

10. How many systems?
11. How many datasets per system?
12. How complete is the inventory?
13. How complete is lineage?
14. Are systems centrally managed?

### Operations

15. Do system owners expose deletion APIs?
16. What are expected completion times?
17. Are systems rate-limited?
18. Which systems are immutable?

### Verification

19. What does "prove" mean for the exercise?
20. Is independent verification required?
21. What audit evidence is expected?

### Scale

22. Requests/day?
23. Records/user?
24. Systems/user?
25. Peak/burst rate?

These questions demonstrate that you are defining the problem before selecting technologies.

---

# 56. 45-Minute System-Design Walkthrough

## 0–5 min — Requirements

Say:

> "I will first define the policy boundary, the exact meaning of deletion, the 30-day SLA, retention exceptions, identity scope, and what evidence constitutes proof."

Clarify the legal/policy boundary.

## 5–10 min — Estimation

Estimate:

```text
requests/day
systems/request
operations/request
verification/request
worker throughput
peak backlog
```

Explain assumptions.

## 10–15 min — High-Level Architecture

Draw:

```text
Request
  |
Identity
  |
Inventory + Lineage
  |
Deletion Plan
  |
System Adapters
  |
Verification
  |
Evidence
```

## 15–25 min — Deep Dive #1

Discuss:

- identity graph
- inventory
- lineage
- deletion contracts
- system-specific adapters
- parallelism

## 25–35 min — Deep Dive #2

Discuss:

- idempotency
- retries
- partial failure
- backups
- immutable data
- derived data
- verification

## 35–40 min — Cross-Cutting

Discuss:

- security
- auditability
- SLA monitoring
- cost
- blast radius

## 40–45 min — Trade-Offs

Close with:

```text
Requirement
 -> Constraints
 -> Options
 -> Decision
 -> Trade-off
 -> Failure implications
 -> Conditions that change the decision
```

---

# 57. Interview Pushback and Strong Responses

### "How can you guarantee every copy was found?"

**Strong response:**  
"I would not claim omniscience from a single catalog. I would build completeness from a registered asset inventory, identity mappings, lineage, ownership contracts, automated discovery checks, and explicit unknown-system detection. The certificate can prove the registered inventory was evaluated; unknown assets become a governance exception rather than being silently ignored."

### "What if the data catalog is wrong?"

**Strong response:**  
"Treat catalog freshness as a dependency and a data-quality metric. Cross-check against application registries, schemas, runtime metadata, lineage, and ownership sources. If completeness cannot be established, the request remains unresolved rather than being falsely completed."

### "How do you delete a Kafka event?"

**Strong response:**  
"I would first challenge the premise. Append-only streams do not normally provide the same primitive as row deletion. I would minimize personal data in events, propagate tombstones to materialized state, use retention/compaction where appropriate, and rebuild downstream state when required. The exact treatment follows the approved policy."

### "What if a vector database still returns the document?"

**Strong response:**  
"Verification has failed. I would block completion, inspect source/chunk/vector/index/cache lineage, repair the stale index, and rerun retrieval-based verification."

### "What happens on day 29?"

**Strong response:**  
"The request should already be at-risk. I would prioritize remaining operations, increase bounded parallelism where safe, escalate blocked owners, and continuously track remaining SLA time. The design should detect deadline risk early."

### "How do you prove deletion without retaining the data?"

**Strong response:**  
"Use minimized evidence: request ID, controlled subject reference, system operations, timestamps, verification outcomes, policy version, and exceptions. The certificate proves the workflow and post-conditions without copying the deleted payload into the audit artifact."

### "Why not just delete everything?"

**Strong response:**  
"Because systems have different semantics, dependencies, retention controls, immutable storage, operational risks, and ownership boundaries. A controlled deletion plan provides correctness, blast-radius protection, verification, and evidence."

---

# 58. Technology Trade-Off Catalogue

| Decision | Option A | Option B | Primary trade-off |
|---|---|---|---|
| Orchestration | Central | Federated | Control vs autonomy |
| Deletion | Hard delete | Soft delete | Strong removal vs operational simplicity |
| Propagation | Tombstone | Physical deletion | Distributed compatibility vs direct removal |
| Execution | Sync | Async | Simplicity vs scale/resilience |
| Lookup | Full scan | Indexed/metadata-driven | Cost vs implementation complexity |
| Propagation | Batch | Streaming | Simplicity vs freshness |
| Integration | API adapters | Direct DB access | Governance vs implementation flexibility |
| Storage | Physical deletion | Crypto-shredding | Direct removal vs key-management architecture |
| Execution | Sequential | Parallel | Simplicity vs throughput |
| Lineage | Central | Federated | Consistency vs ownership |
| Aggregates | Recompute | Incremental correction | Simplicity vs cost |

For every choice, ask:

```text
Requirement
→ Constraint
→ Candidates
→ Evaluation criteria
→ Decision
→ Trade-off
→ Failure implications
→ When decision changes
```

---

# 59. Senior vs Staff-Level Reasoning

## Intermediate

Focus on:

- delete records
- basic orchestration
- basic verification

## Senior

Focus on:

- distributed deletion
- identity
- lineage
- deletion contracts
- idempotency
- retries
- partial failures
- verification
- auditability
- SLA

## Staff

Focus on:

- platform architecture
- standardized deletion contracts
- organizational ownership
- governance
- unknown systems
- privacy-by-design
- cost
- global scale
- evolution
- risk management
- data-product lifecycle

The Staff-level answer shifts from:

> "How do I delete this record?"

to:

> "How do I create an organizational capability that makes deletion complete, verifiable, safe, observable, and maintainable as the platform evolves?"

---

# 60. 100+ Deep-Dive Interview Follow-Ups

The following bank is deliberately broad. For challenging questions, answer using:

```text
Strong answer
Engineering reasoning
Common weak answer
Interviewer follow-up
```

## A. GDPR / Privacy Fundamentals

1. What does GDPR mean at an engineering level?
2. What is a data subject?
3. What is personal data?
4. Why is this not a generic SQL-delete problem?
5. What does deletion mean operationally?
6. Who defines retention exceptions?
7. How do you separate legal requirements from engineering controls?
8. What evidence should engineering produce?
9. What is data minimization?
10. Why should privacy requirements be policy-driven?

## B. Personal Data and Classification

11. How do you classify direct identifiers?
12. How do you treat pseudonymous IDs?
13. Is a hash automatically anonymous?
14. How do device IDs affect deletion?
15. What are derived identifiers?
16. How do you classify aggregates?
17. How do you classify embeddings?
18. How do you classify logs?
19. How do you handle unknown data classification?
20. How should classification affect deletion contracts?

## C. Identity Resolution

21. Why is canonical identity required?
22. How do you handle multiple emails?
23. How do you handle merged accounts?
24. How do you handle historical identifiers?
25. What if identity mappings are stale?
26. What if two people share an identifier?
27. How do you prevent over-deletion?
28. How do you version identity mappings?
29. How do you audit identity resolution?
30. What happens if identity resolution is unavailable?

## D. Data Inventory

31. What fields belong in an asset inventory?
32. Who owns each dataset?
33. How do you detect unregistered systems?
34. What if an application creates a database dynamically?
35. How do you measure inventory completeness?
36. How do you handle manual exceptions?
37. How often should metadata be refreshed?
38. What happens when an owner leaves?
39. How do you onboard a new data product?
40. How do you make inventory part of the platform lifecycle?

## E. Lineage

41. Why is lineage necessary?
42. How do you find derived datasets?
43. What if lineage is incomplete?
44. What if lineage is stale?
45. How do you detect broken lineage?
46. How do you trace an embedding back to source data?
47. How do you trace a dashboard to source data?
48. Can lineage alone guarantee completeness?
49. How do you combine lineage with inventory?
50. How do you monitor lineage quality?

## F. Operational Databases

51. What is the difference between soft and hard deletion?
52. How do foreign keys affect deletion?
53. How do you delete from large tables?
54. How do you avoid lock contention?
55. How do you verify child records?
56. What happens to CDC events?
57. How do replicas affect verification?
58. How do you handle a NoSQL store?
59. How do you handle secondary indexes?
60. What if the database is unavailable?

## G. Warehouses

61. How do you delete a user's warehouse records?
62. What about materialized views?
63. What about derived tables?
64. How do aggregates affect deletion?
65. When do you recompute?
66. How do you verify residual rows?
67. How do you control scan cost?
68. What if a warehouse query is blocked?
69. How do you handle multiple warehouse engines?
70. How do you standardize warehouse deletion contracts?

## H. Lakehouses

71. Why is logical deletion different from physical deletion?
72. How do snapshots affect deletion?
73. How does time travel affect the design?
74. What are old Parquet files?
75. How do table metadata and storage interact?
76. When might a rewrite be necessary?
77. How do you verify physical cleanup?
78. How do you handle concurrent writers?
79. What if cleanup is delayed?
80. How do you control lakehouse deletion cost?

## I. Kafka / Streaming

81. Why is deleting one Kafka event different?
82. What is a tombstone?
83. How does compaction help?
84. How does retention help?
85. What if a consumer has already materialized the data?
86. How do you rebuild downstream state?
87. How do you minimize personal data in event streams?
88. What if a topic is immutable?
89. How do you verify downstream materializations?
90. How does replay affect deletion?

## J. Caches

91. How do you find all cache keys?
92. What if key naming is inconsistent?
93. Is TTL sufficient?
94. How do replicas affect invalidation?
95. How do you verify cache deletion?

## K. Feature Stores

96. How do you delete online features?
97. How do you delete offline features?
98. What happens to training datasets?
99. When might a model require retraining?
100. How does point-in-time data affect deletion?
101. How do feature backfills affect privacy?
102. How do you verify feature removal?

## L. Vector Stores / RAG

103. What must be deleted when a document is removed?
104. How do you delete chunks?
105. How do you delete embeddings?
106. What if the vector index is stale?
107. How do you verify retrieval?
108. What about retrieval caches?
109. How do you handle millions of vectors?
110. When do you rebuild an index?
111. How do you maintain embedding lineage?
112. How do ACLs interact with deletion?

## M. Logs and Backups

113. Why are logs difficult?
114. What should never be logged?
115. How do immutable logs affect the design?
116. How do you treat access logs?
117. What if a backup contains the subject?
118. How do snapshots affect deletion?
119. What if a DR copy is offline?
120. How do you prove backup policy compliance?

## N. Immutable Storage and Crypto-Shredding

121. What is WORM-style storage?
122. Why can immutable storage conflict with deletion?
123. What is crypto-shredding?
124. When is per-user keying useful?
125. What happens if keys are backed up?
126. Why is crypto-shredding not a universal solution?
127. How do you evidence key destruction?
128. What happens when policy changes?

## O. Orchestration / Idempotency

129. Why use a state machine?
130. Why use a DAG?
131. Which tasks can run in parallel?
132. What is an idempotency key?
133. How do you recover after a worker crash?
134. How do you prevent duplicate execution?
135. What belongs in durable operation state?
136. How do you handle dead-letter operations?
137. What happens if workflow state is lost?
138. How do you coordinate dependencies?

## P. Retries / Partial Failures

139. What is a transient failure?
140. What is a permanent failure?
141. Why use jitter?
142. When is retry unsafe?
143. How do you handle partial completion?
144. How do you isolate failing systems?
145. When do you escalate?
146. How do you calculate remaining SLA risk?
147. What happens if a system fails on day 29?
148. How do you prevent retry storms?

## Q. Verification / Audit

149. Why is execution result insufficient?
150. What is an independent verification path?
151. How do you verify a vector deletion?
152. How do you verify a Kafka-derived table?
153. How do you verify a lakehouse cleanup?
154. What belongs in a deletion certificate?
155. What should never be placed in the certificate?
156. How do you protect evidence?
157. How do you make evidence tamper-evident?
158. How do you prove every registered system was evaluated?

## R. Security

159. What permissions should the deletion service have?
160. Why is least privilege important?
161. How do you protect deletion APIs?
162. How do you prevent a wrong-user deletion?
163. How do approval gates help?
164. What is separation of duties?
165. How do you secure secrets?
166. How do you audit administrative access?

## S. Observability / SLA

167. What metrics matter?
168. Why monitor P95 completion time?
169. How do you define "at risk"?
170. What alerts matter most?
171. How do you detect a growing backlog?
172. How do you detect repeated owner failures?
173. How do you monitor unknown systems?
174. How do you measure verification failures?

## T. Cost / Scale

175. What is the main cost driver?
176. Why can verification be expensive?
177. How do you reduce lake scans?
178. How do you reduce warehouse cost?
179. How do you scale workers?
180. What changes at 10× request volume?
181. What changes at 10× systems?
182. How do API rate limits affect design?
183. How do you prioritize deadline risk?
184. How do you avoid over-provisioning?

## U. Disaster Recovery / Schema Evolution

185. What happens if the orchestrator region fails?
186. What state must survive disaster recovery?
187. How do you prevent duplicate execution after failover?
188. What if a deletion adapter changes schema?
189. How do you version deletion contracts?
190. How do you handle a renamed identifier?
191. What if lineage changes during a request?
192. How do you test disaster recovery?

## V. Senior Architecture

193. Central orchestration or federated ownership?
194. How do you standardize deletion APIs?
195. How do you onboard a new data system?
196. How do you enforce deletion contracts?
197. How do you measure platform completeness?
198. How do you handle organizational boundaries?
199. How do you handle vendor-managed systems?
200. How do you design global deployment?
201. How do you keep the platform evolvable?
202. What are your top architectural risks?

## W. Staff Architecture

203. How do you make privacy a data-product lifecycle requirement?
204. How do you prevent unknown systems?
205. How do you make deletion contracts part of platform governance?
206. How do you balance central control with team autonomy?
207. How do you design for global scale?
208. How do you make the system auditable without over-retaining evidence?
209. How do you build an executive-level privacy SLO?
210. How do you prioritize privacy engineering investment?
211. How do you quantify risk reduction?
212. What architectural decision would you revisit first as the company grows?

### Model reasoning for challenging follow-ups

**Question:** "Can you guarantee every copy was found?"

**Strong answer:** No system should casually claim omniscience. Build measurable completeness from inventory, lineage, identity mappings, ownership, runtime discovery, and governance controls. Define the boundary of what can be proven.

**Weak answer:** "The catalog has everything."

**Follow-up:** "How do you know the catalog is complete?"

---

# 61. Three Complete Mock Interviews

## Mock 1 — Intermediate

### Prompt

Design the deletion workflow for a company with PostgreSQL, a warehouse, Redis, and a feature store.

### Clarifying questions

- What is the 30-day SLA?
- What identifiers exist?
- What counts as deleted?
- What verification is required?
- Are there retention exceptions?

### Expected architecture

```text
Request
 -> Identity
 -> Inventory
 -> Deletion DAG
 -> DB / Warehouse / Redis / Feature Store
 -> Verification
 -> Certificate
```

### Follow-ups

- What if Redis fails?
- How do you retry?
- What if the user has two identifiers?
- How do you prove completion?

### Pushback

> "Why isn't the PostgreSQL delete enough?"

Expected answer: downstream copies and derived data remain.

### Failure scenario

Warehouse unavailable for six hours.

### Scoring

| Dimension | Points |
|---|---:|
| Requirements | 15 |
| Identity | 15 |
| Inventory | 15 |
| Architecture | 20 |
| Reliability | 15 |
| Verification | 10 |
| Communication | 10 |
| **Total** | **100** |

### Model-answer outline

Define policy → resolve identity → inventory → deletion contracts → parallel execution → retries → verification → evidence → SLA.

---

## Mock 2 — Senior

### Prompt

Design deletion across PostgreSQL, Kafka, lakehouse, warehouse, Redis, feature store, vector database, and backups.

### Clarifying questions

Focus on:

- policy
- 30-day deadline
- identity
- lineage completeness
- immutable systems
- verification semantics
- scale

### Expected architecture

Use:

```text
Request
 -> Identity Graph
 -> Inventory + Lineage
 -> Deletion DAG
 -> System Adapters
 -> Independent Verification
 -> Audit Evidence
```

### Follow-ups

- Kafka history?
- lakehouse snapshots?
- stale vector index?
- backup copy?
- partial failure?
- day-29 escalation?
- 10× load?

### Pushback

> "What if the catalog is wrong?"

Expected answer: treat catalog quality as a monitored control and combine multiple discovery sources.

### Failure scenario

Vector deletion succeeds but retrieval still returns content.

### Scoring

Emphasize distributed reliability, verification, lineage, SLA, and trade-offs.

### Model-answer outline

The strongest answer distinguishes **execution, post-condition verification, and evidence**.

---

## Mock 3 — Staff

### Prompt

Design a global privacy deletion platform for a rapidly growing enterprise with hundreds of data products, multiple clouds, AI systems, immutable archives, and independently owned teams.

### Clarifying questions

Focus on:

- organizational boundaries
- policy differences
- global deployment
- data residency
- ownership
- unknown systems
- vendor systems
- scale
- risk
- cost

### Expected architecture

```text
Privacy Policy / Governance
           |
           v
Global Request Control Plane
           |
     +-----+------+
     |            |
 Identity      Inventory
     |            |
     +-----+------+
           |
        Lineage
           |
           v
Deletion Contract Registry
           |
           v
Distributed Orchestrator
           |
     +-----+------------------+
     |        |       |       |
   Data     AI      Search  Archive
 Products  Systems  Systems Systems
     |        |       |       |
     +--------+-------+-------+
              |
        Independent Verification
              |
        Evidence / Reporting
```

### Follow-ups

- How do you onboard a new data product?
- How do you prevent teams from bypassing contracts?
- How do you handle vendor systems?
- How do you measure unknown-data risk?
- How do you operate across regions?
- What if deletion policy changes?
- How do you contain a bug that could delete millions of users?

### Pushback

> "Why should every team expose an API?"

Answer: standard contracts can support API, SQL job, event, or managed workflow adapters, but ownership and verification semantics must be standardized.

### Failure scenario

Global orchestrator loses a region while 50,000 deletion requests are in flight.

### Scoring

Staff-level evaluation should heavily weight governance, platform evolution, risk management, organizational design, and cost.

### Model-answer outline

Design a **capability**, not a collection of scripts: policy boundary → inventory/lineage → contracts → distributed orchestration → verification → evidence → governance feedback loop.

---

# 62. Self-Scoring Rubric

Score each dimension from 0–5 and normalize to 100.

| Dimension | Weight |
|---|---:|
| Requirements clarification | 5 |
| Legal/policy scope | 5 |
| Identity resolution | 5 |
| Data inventory | 5 |
| Lineage | 5 |
| Architecture | 5 |
| Deletion orchestration | 5 |
| Idempotency | 5 |
| Retry strategy | 5 |
| Failure handling | 5 |
| Verification | 5 |
| Auditability | 5 |
| Backup handling | 5 |
| Derived-data handling | 5 |
| Security | 5 |
| SLA management | 5 |
| Cost | 5 |
| Scaling | 5 |
| Trade-offs | 5 |
| Communication | 5 |
| **Total** | **100** |

Use:

```text
90–100 = Staff-ready
80–89  = Strong Senior
70–79  = Senior with gaps
60–69  = Intermediate
<60    = Revisit fundamentals
```

A high score requires not merely naming concepts but connecting them into a coherent system.

---

# 63. Final Assessment

## Part A — Privacy / Data Governance Fundamentals

Answer at least 25:

1. Define GDPR from an engineering perspective.
2. Define personal data.
3. Define data subject.
4. What is a deletion request operationally?
5. Why must legal policy precede implementation?
6. What is data minimization?
7. What is retention?
8. What is data classification?
9. Why does identity resolution matter?
10. What is lineage?
11. What is an asset inventory?
12. What is pseudonymization?
13. Why is hashing not automatically anonymization?
14. What is a deletion contract?
15. What is an audit certificate?
16. What is an immutable store?
17. What is crypto-shredding?
18. Why are backups difficult?
19. Why are logs difficult?
20. Why are derived datasets important?
21. What is a policy exception?
22. What is verification?
23. What is evidence?
24. What does 30-day SLA mean operationally?
25. Why is unknown data a privacy risk?

**Guidance:** Answers should distinguish policy decisions from engineering mechanisms.

## Part B — SQL: 10 Problems

1. Find all records for a user.
2. Find child records.
3. Implement a bounded deletion.
4. Compare soft and hard delete.
5. Verify residual rows.
6. Reconcile operation results.
7. Identify incomplete systems.
8. Compute request age.
9. Flag at-risk requests.
10. Verify derived-table cleanup.

**Guidance:** Prioritize correctness, transaction safety, indexing, and verification.

## Part C — Python: 10 Problems

1. Implement idempotent deletion.
2. Implement retry with backoff.
3. Add jitter.
4. Build a deletion adapter interface.
5. Build a mock adapter.
6. Implement a deletion state machine.
7. Build dependency ordering.
8. Implement SLA classification.
9. Generate a minimized certificate.
10. Add failure injection.

**Guidance:** Use mocks rather than destructive production integrations.

## Part D — Debugging: 10 Scenarios

1. Identity mapping is stale.
2. Catalog is unavailable.
3. PostgreSQL task times out.
4. Lakehouse residual files remain.
5. Kafka materialization still contains data.
6. Redis key survives.
7. Vector retrieval still returns content.
8. Verification reads stale cache.
9. Owner does not respond.
10. Workflow is near the deadline.

**Guidance:** Use `detect → contain → diagnose → recover → verify → evidence → prevent`.

## Part E — Distributed Deletion: 10 Problems

1. Design a deletion DAG.
2. Define operation state.
3. Handle partial failure.
4. Handle duplicate requests.
5. Design idempotency.
6. Design retry semantics.
7. Design escalation.
8. Design independent verification.
9. Design evidence.
10. Design 10× worker scaling.

## Part F — System Design: 5 Cases

1. PostgreSQL + warehouse + Redis.
2. Add Kafka and lakehouse.
3. Add feature and vector stores.
4. Add immutable backups.
5. Design a global multi-team deletion platform.

## Part G — Deep-Dive Interview Questions

Choose 20 from the follow-up bank and answer each aloud in 2–4 minutes.

## Part H — Production Incidents

Solve 10 incidents using:

```text
Detection
→ Containment
→ Diagnosis
→ Recovery
→ Verification
→ Evidence
→ Prevention
```

---

# 64. Common Interview and Production Mistakes

## Treating deletion as a SQL statement

**Why it fails:** ignores distributed copies.  
**Better:** inventory + lineage + orchestration.  
**Trade-off:** more platform complexity for completeness.

## No data inventory

**Why it fails:** unknown systems cannot be evaluated.  
**Better:** governed asset registry.  
**Trade-off:** ongoing metadata maintenance.

## No identity graph

**Why it fails:** aliases and historical IDs are missed.  
**Better:** canonical identity + controlled mappings.  
**Trade-off:** identity governance complexity.

## No lineage

**Why it fails:** derived copies remain.  
**Better:** lineage plus quality checks.  
**Trade-off:** lineage maintenance cost.

## No ownership

**Why it fails:** failures cannot be escalated.  
**Better:** every asset has an accountable owner.

## No deletion contracts

**Why it fails:** every system becomes a bespoke integration.  
**Better:** standardized contract + adapter.

## No idempotency

**Why it fails:** retries become dangerous.  
**Better:** operation IDs and repeat-safe semantics.

## No verification

**Why it fails:** execution success is mistaken for post-condition success.  
**Better:** independent verification.

## Ignoring backups

**Why it fails:** historical copies remain unaccounted for.  
**Better:** policy-driven backup lifecycle.

## Ignoring Kafka

**Why it fails:** append-only histories and materialized copies remain.  
**Better:** event-aware deletion architecture.

## Ignoring caches

**Why it fails:** serving layer may continue exposing data.  
**Better:** key contracts + invalidation + verification.

## Ignoring vector indexes

**Why it fails:** deleted content may remain retrievable.  
**Better:** index deletion + retrieval verification.

## Ignoring logs

**Why it fails:** PII can survive in operational telemetry.  
**Better:** minimize logging and define retention/deletion controls.

## Ignoring derived datasets

**Why it fails:** source deletion does not automatically propagate.  
**Better:** lineage-driven downstream treatment.

## Treating soft delete as physical deletion

**Why it fails:** data remains.  
**Better:** define the actual required post-condition.

## Assuming hash = anonymization

**Why it fails:** linkability may remain.  
**Better:** follow approved classification/policy.

## No SLA monitoring

**Why it fails:** day-29 surprises become inevitable.  
**Better:** deadline-aware monitoring.

## No dry-run

**Why it fails:** destructive scope errors become expensive.  
**Better:** preview before execution.

## No blast-radius control

**Why it fails:** one bug could affect many users.  
**Better:** scoped identities, batch limits, approvals, kill switch.

## Overpromising legal guarantees

**Why it fails:** engineering cannot determine every legal applicability question.  
**Better:** explicitly separate policy/legal decisions from implementation.

---

# 65. Production Quality Bar

A production-ready design must explicitly consider:

- correctness
- completeness
- reliability
- availability
- idempotency
- retries
- backfills/reprocessing
- lineage
- identity
- verification
- auditability
- security
- privacy
- governance
- cost
- scalability
- disaster recovery
- data quality
- operational simplicity
- blast-radius control

Do not call a design production-ready merely because it has a workflow diagram.

---

# 66. Final Reference Architecture

```text
                    +----------------------+
                    | Deletion Request     |
                    | User / Privacy Team  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Authentication /     |
                    | Policy Validation    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Identity Resolution  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Inventory + Lineage  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Deletion Plan / DAG  |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        +-----------+    +-----------+    +-----------+
        | Source DB |    | Lake /    |    | Event     |
        |           |    | Warehouse |    | Streams   |
        +-----+-----+    +-----+-----+    +-----+-----+
              |                |                |
              v                v                v
          Caches         Derived Data      Materialized
                                             State
              |                |                |
              +--------+-------+--------+-------+
                       |                |
                       v                v
                   Features          Vectors
                       |                |
                       +-------+--------+
                               |
                               v
                        Search / RAG
                               |
                               v
                           Backups
                               |
                               v
                    +----------------------+
                    | Independent          |
                    | Verification         |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Audit Evidence       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Complete / Escalate   |
                    +----------------------+
```

### Architecture principles

1. **Policy before implementation.**
2. **Identity before deletion.**
3. **Inventory before claiming completeness.**
4. **Lineage before claiming downstream coverage.**
5. **Contracts before integration sprawl.**
6. **Idempotency before retries.**
7. **Verification before completion.**
8. **Evidence without recreating unnecessary personal data.**
9. **Safety controls before destructive scale.**
10. **Deadline monitoring from request creation.**
11. **Unknown systems are a governance signal.**
12. **Technology choices follow requirements.**

---

# 67. Roadmap Coverage Audit

The following audit maps the authoritative Case 14 requirements to this module rather than merely marking them "covered."

| Roadmap requirement | Where taught | Depth | Implementation examples |
|---|---|---|---|
| 30-day deletion requirement | §5, §43, §56 | Deep | SQL + Python SLA examples |
| User data deletion | §§4, 12–24 | Deep | SQL, Python, PySpark |
| Data inventory | §§6, 23 | Deep | Inventory schema/table |
| Data classification | §7 | Deep | Classification examples |
| Identity resolution | §§8, 52 | Deep | Identity graph + safety rules |
| Data lineage | §§9–10 | Deep | Lineage graphs + quality checks |
| Operational databases | §12 | Deep | SQL |
| Lake/lakehouse tables | §13 | Deep | PySpark + lifecycle explanation |
| Warehouses | §14 | Deep | SQL + recomputation strategies |
| Kafka/event streams | §15 | Deep | Architecture and deletion strategies |
| Caches | §16 | Intermediate/Advanced | Python Redis-style example |
| Feature stores | §17 | Advanced | Lifecycle + policy treatment |
| Vector stores | §18 | Advanced | Retrieval verification |
| Logs | §19 | Advanced | Retention/redaction architecture |
| Backups | §20 | Advanced | Policy-driven lifecycle |
| Immutable storage | §21 | Advanced | WORM/exception design |
| Crypto-shredding | §22 | Advanced | Key lifecycle model |
| Verification | §32 | Deep | Query/retrieval/scan strategies |
| Audit certificates | §§33–34 | Deep | JSON certificate |
| SLAs | §§5, 43 | Deep | Python + monitoring |
| Retries | §28 | Deep | Python backoff |
| Escalation | §§27–28, 43 | Deep | State model + incident flow |
| Failure handling | §45 | Deep | 22 production scenarios |
| Security | §39 | Deep | Privilege/blast-radius controls |
| Cost | §44 | Advanced | Cost drivers and optimization |
| Scaling | §43 | Advanced | 10× analysis |
| Interview walkthrough | §56 | Deep | Exact 45-minute plan |
| Trade-offs | §58 | Deep | Decision catalogue |
| Diagramming/communication | §§56, 66 | Deep | Mermaid architectures |
| Topic 16 failure reasoning | §§45, 47, 61 | Deep | Incident loop + follow-ups |
| Derived data | §§10, 36–38 | Deep | Aggregates, ML, RAG |
| Auditability | §§33–34, 39 | Deep | Evidence model |
| Testing | §48 | Deep | Unit/integration/contract/E2E |
| Practical project | §49 | Deep | Complete local mock platform |
| Break/fix | §47 | Deep | 12 labs |
| Senior/Staff reasoning | §59–61 | Deep | Level-specific mocks/follow-ups |

### Coverage conclusion

The module covers the Case 14 curriculum from beginner fundamentals through production architecture and Senior/Staff interview reasoning. It deliberately treats GDPR as a **policy input to an engineering system**, not as legal advice.

---

# 68. Completion Checklist

```text
[ ] I understand GDPR at a high engineering level.
[ ] I understand personal data.
[ ] I understand deletion requests.
[ ] I understand the 30-day requirement.
[ ] I understand data inventory.
[ ] I understand data classification.
[ ] I understand identity resolution.
[ ] I understand identity graphs.
[ ] I understand data lineage.
[ ] I understand distributed deletion.
[ ] I understand deletion contracts.
[ ] I understand deletion orchestration.
[ ] I understand deletion DAGs.
[ ] I understand idempotency.
[ ] I understand retries.
[ ] I understand partial failures.
[ ] I understand database deletion.
[ ] I understand warehouse deletion.
[ ] I understand lakehouse deletion.
[ ] I understand Kafka deletion challenges.
[ ] I understand cache deletion.
[ ] I understand feature-store deletion.
[ ] I understand vector-store deletion.
[ ] I understand log deletion.
[ ] I understand backup challenges.
[ ] I understand immutable storage.
[ ] I understand crypto-shredding.
[ ] I understand derived-data deletion.
[ ] I understand ML-data implications.
[ ] I understand RAG/vector deletion.
[ ] I understand verification.
[ ] I understand audit evidence.
[ ] I understand retention exceptions.
[ ] I understand SLA management.
[ ] I understand security controls.
[ ] I understand dry-run and blast-radius controls.
[ ] I can write SQL examples.
[ ] I can implement orchestration logic in Python.
[ ] I understand distributed processing implications.
[ ] I can design the production architecture.
[ ] I can handle partial failures.
[ ] I can design for 10× scale.
[ ] I can explain cost trade-offs.
[ ] I can answer Senior-level questions.
[ ] I can answer Staff-level questions.
[ ] I can complete the case in 45 minutes.
```

---

# 69. Interview Cheat Sheet

```text
1. CLARIFY
   Policy → scope → definition of deletion → SLA → exceptions

2. IDENTIFY
   Canonical user → aliases → historical identifiers

3. DISCOVER
   Inventory → catalog → lineage → ownership → unknown systems

4. PLAN
   Deletion contracts → DAG → dependencies → parallelism

5. EXECUTE
   DB → lake → warehouse → streams → caches → features → vectors → logs → backups

6. RELIABILITY
   Idempotency → retries → timeouts → partial failures → escalation

7. VERIFY
   Query → scan → retrieval → materialization → physical lifecycle

8. PROVE
   Request ID → operations → verification → exceptions → policy version → timestamp

9. OPERATE
   SLA → backlog → at-risk → alerts → ownership → cost

10. DEFEND
    Security → blast radius → trade-offs → 10× scale → failure scenarios
```

### The three sentences to remember

> **Identity tells me what to delete.**

> **Lineage tells me where to delete it.**

> **Verification and evidence tell me whether I can responsibly close the request.**

---

# 70. Final Operating Standard

For this design case, the production operating standard is:

```text
POLICY
  ↓
AUTHENTICATE
  ↓
RESOLVE IDENTITY
  ↓
DISCOVER INVENTORY + LINEAGE
  ↓
CLASSIFY + APPLY POLICY
  ↓
BUILD DELETION PLAN / DAG
  ↓
DRY-RUN / SAFETY CHECK
  ↓
EXECUTE WITH IDEMPOTENT SYSTEM CONTRACTS
  ↓
RETRY TRANSIENT FAILURES
  ↓
ESCALATE BLOCKED OPERATIONS
  ↓
VERIFY INDEPENDENTLY
  ↓
HANDLE RETENTION / IMMUTABLE EXCEPTIONS
  ↓
GENERATE MINIMIZED AUDIT EVIDENCE
  ↓
CHECK 30-DAY SLA
  ↓
COMPLETE OR ESCALATE
  ↓
FEED GAPS BACK INTO INVENTORY, LINEAGE, AND GOVERNANCE
```

The key Staff-level insight is:

> **A reliable deletion platform is not primarily a delete engine. It is a governed, identity-aware, lineage-aware, contract-driven control plane that coordinates heterogeneous data systems, verifies post-conditions, manages exceptions, controls blast radius, and produces defensible evidence under an explicit SLA.**
