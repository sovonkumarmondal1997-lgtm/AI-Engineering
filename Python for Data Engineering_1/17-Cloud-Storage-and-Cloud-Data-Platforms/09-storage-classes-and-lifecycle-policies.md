# CLAUDE CODE PROMPT — LEARN AND COMPLETE
# 09-storage-classes-and-lifecycle-policies.md

You are a **Senior Data Engineer with 10+ years of production industry experience**, specializing in cloud data platforms, object storage, lakehouse architecture, Data Engineering, cloud cost optimization, data governance, and production-scale data systems.

Your task is to **teach and build the complete learning content for exactly this file**:

`17-Cloud-Storage-and-Cloud-Data-Platforms/09-storage-classes-and-lifecycle-policies.md`

This is **Topic 09 — Storage Classes and Lifecycle Policies**, the final topic of Module 2.17 — **Cloud Storage and Cloud Data Platforms** in Stage 2 — Python for Data Engineering.

This topic is the **advanced cost-control topic** of the module.

---

# 1. ABSOLUTE FILE-SCOPE RULE

You MUST obey these rules:

- Modify/create content ONLY in:
  `09-storage-classes-and-lifecycle-policies.md`
- DO NOT modify `README.md`.
- DO NOT modify:
  - `01-object-storage-s3-gcs-and-adls.md`
  - `02-boto3-and-s3-operations.md`
  - `03-fsspec-and-cloud-agnostic-file-access.md`
  - `04-iam-roles-and-least-privilege-for-pipelines.md`
  - `05-cloud-warehouses-snowflake-bigquery-and-redshift.md`
  - `06-python-warehouse-connectors-and-bulk-loads.md`
  - `07-serverless-data-processing.md`
  - `08-managed-spark-databricks-emr-and-dataproc.md`
  - `practice-questions.md`
- DO NOT modify any file outside the current folder.
- DO NOT modify the roadmap file.
- DO NOT rename any files.
- DO NOT create unrelated files.
- DO NOT update any other Markdown file.
- The final result must be a **single, self-contained, production-quality Markdown learning file**.

Before making changes:

1. Inspect `09-storage-classes-and-lifecycle-policies.md` if it exists.
2. Preserve useful existing content if present.
3. Improve or complete the file according to this prompt.
4. At the end, verify that no other file was modified.

---

# 2. AUTHORITATIVE ROADMAP

Treat the Module 2.17 roadmap as the **source of truth**.

Topic 09 is explicitly an **Advanced — Cost Control** topic.

The roadmap requires the learner to understand:

## Basics

- Storage classes based on access frequency:
  - frequent-access / standard
  - infrequent-access
  - archive tiers
  - automatic tiering
- AWS S3
- Google Cloud Storage
- Azure storage equivalents
- Trade-offs:
  - cheaper storage
  - retrieval fees
  - retrieval delays
  - minimum storage durations
- Lifecycle policies:
  - transition objects after N days
  - expire objects
  - clean up old versions

## Intermediate

- Abort incomplete multipart uploads
- Expire noncurrent object versions
- Delete temporary prefixes
- Delete staging prefixes
- Prefix design for lifecycle policies
- Landing
- Bronze
- Silver
- Gold
- Temp
- Logs
- Per-object charges
- Minimum billable object sizes
- Per-request fees
- Small-object economics

## Advanced

- Lifecycle policies and Delta/Iceberg/table-format data
- Why live table files must not be arbitrarily transitioned or deleted
- VACUUM
- Snapshot expiration
- Table maintenance
- Compliance
- Retention requirements
- Object Lock
- Legal holds
- Deletion deadlines
- GDPR-related deletion considerations
- Storage inventory reports
- Storage analytics
- Finding large/old/unused data
- Storage cost modeling
- Growth rate
- Tiering schedule
- Retrieval patterns
- Projected savings
- Compression
- Duplicate deletion
- Avoiding cross-region transfer

The roadmap's hands-on exercise requires:

1. Lifecycle rules:
   - landing → infrequent access after 30 days
   - archive after 180 days
   - `tmp/` → delete after 7 days
   - noncurrent versions → expire after 30 days
   - incomplete multipart uploads → abort after 7 days
2. Exclude table-format data prefixes from transitions.
3. Build a storage report:
   - size by prefix
   - object count by prefix
   - storage class
   - age
   - small-object counts
4. Calculate projected monthly savings.
5. Include retrieval and per-object costs.
6. Apply rules to a test bucket first.
7. Verify the lifecycle behavior after the provider applies it.

The required checkpoint is:

- Compare storage classes including minimum durations and retrieval costs.
- Write lifecycle rules for transitions, expiry, versions, and multipart cleanup.
- Explain why lifecycle rules must not touch live table files.
- Model and verify storage savings.

These requirements are mandatory.

---

# 3. LEARNING OBJECTIVE

Build the document so the learner progresses through:

```text
Why storage costs matter
        ↓
Object-storage economics
        ↓
Storage classes
        ↓
Standard vs infrequent vs archive
        ↓
Retrieval costs and minimum durations
        ↓
Lifecycle policies
        ↓
Object expiration
        ↓
Version cleanup
        ↓
Multipart cleanup
        ↓
Prefix architecture
        ↓
Small-object economics
        ↓
Table-format safety
        ↓
Delta/Iceberg maintenance
        ↓
Compliance and retention
        ↓
Storage inventory
        ↓
Storage cost model
        ↓
Cost optimization
        ↓
Hands-on implementation
        ↓
Verification
        ↓
Production design
```

The teaching must progress:

**basic → intermediate → advanced → production Data Engineer**

Do not jump directly into provider-specific lifecycle JSON without explaining the underlying storage economics.

---

# 4. IMPORTANT CONTEXT

The learner already studied object storage in:

`01-object-storage-s3-gcs-and-adls.md`

Therefore:

- Do not re-teach the entire object-storage module.
- Briefly refresh only the concepts necessary for this topic.
- Build directly on:
  - buckets
  - objects
  - prefixes
  - versioning
  - multipart uploads
  - storage classes
  - object metadata
  - cloud storage economics

The key question throughout this document should be:

> **How do we reduce cloud storage cost without accidentally making data slower, more expensive to retrieve, non-compliant, or unusable by our lakehouse/table formats?**

---

# 5. TEACH IN SIMPLE TERMS FIRST

For every important concept:

1. Explain it in simple language.
2. Explain why it exists.
3. Explain how it works.
4. Give an example.
5. Show code/configuration where useful.
6. Explain production implications.
7. Explain cost implications.
8. Explain failure modes.
9. Explain when to use it.
10. Explain when NOT to use it.

Use simple analogies when helpful.

For example:

> Storage classes are like choosing different warehouses for your data based on how often you expect to visit it: frequently accessed data stays close and convenient, while rarely accessed data can move to cheaper but slower or more expensive-to-retrieve storage.

Then progressively move into technical and financial reasoning.

---

# 6. RECOMMENDED DOCUMENT STRUCTURE

Create a comprehensive structure such as:

# Storage Classes and Lifecycle Policies

## 1. Why Storage Cost Control Matters

## 2. Cloud Object Storage Economics

## 3. Storage Classes — The Core Concept

## 4. Standard, Infrequent-Access, Archive, and Automatic Tiering

## 5. AWS S3 Storage Classes

## 6. Google Cloud Storage Classes

## 7. Azure Storage Tiering

## 8. Storage-Class Trade-offs

## 9. Retrieval Costs and Minimum Storage Durations

## 10. Lifecycle Policies

## 11. Lifecycle Transitions

## 12. Object Expiration

## 13. Version Cleanup

## 14. Incomplete Multipart Upload Cleanup

## 15. Temporary and Staging Data Cleanup

## 16. Prefix Design for Lifecycle Management

## 17. Small-Object Economics

## 18. Lifecycle Policies for Data-Lake Layers

## 19. Lifecycle Policies and Delta/Iceberg Tables

## 20. VACUUM, Snapshot Expiration, and Table Maintenance

## 21. Compliance, Retention, Object Lock, and Legal Holds

## 22. Storage Inventory and Storage Analytics

## 23. Building a Storage Report with Python

## 24. Storage Cost Modeling

## 25. Projected Savings and Scenario Analysis

## 26. Additional Cost Levers

## 27. Production Lifecycle Architecture

## 28. Hands-On Lifecycle Management Project

## 29. Failure Scenarios

## 30. Common Mistakes

## 31. Knowledge Checkpoints

## 32. Practice Exercises

## 33. Interview Questions

## 34. Final Assessment

## 35. Mastery / Exit Criteria

You may improve the structure if needed, but **every roadmap concept must remain covered**.

---

# 7. CLOUD STORAGE ECONOMICS

Teach the learner that object-storage cost is not simply:

```text
GB stored × price per GB
```

Explain that a realistic cost model can include:

```text
Storage
+ Requests
+ Retrieval
+ Data transfer
+ Versioned objects
+ Incomplete multipart uploads
+ Minimum-duration charges
+ Minimum billable object-size effects
+ Related services
```

Explain each component.

Show why a cheaper storage class can sometimes become **more expensive overall**.

Example reasoning:

```text
Cheap storage
    +
Frequent retrieval
    +
Retrieval charges
    +
Early deletion
    +
Many small objects
    =
Potentially higher total cost
```

This is one of the most important concepts in the module.

---

# 8. STORAGE CLASSES

Explain the general categories first:

### Standard / frequent-access

For:

- actively queried data
- recent data
- frequently accessed datasets

### Infrequent-access

For:

- older data
- occasionally accessed data
- backup-like datasets

### Archive

For:

- long-term retention
- rarely accessed historical data
- compliance archives

### Automatic tiering

Explain the concept of automatically moving data between access tiers according to observed access patterns.

Explain the benefits and trade-offs.

---

# 9. AWS S3 STORAGE CLASSES

Teach the conceptual hierarchy of S3 storage classes.

Cover categories such as:

- Standard
- Intelligent-Tiering
- Standard-IA
- One Zone-IA
- Glacier Instant Retrieval
- Glacier Flexible Retrieval
- Glacier Deep Archive

Explain the **purpose and trade-offs**, not merely the names.

For each relevant class discuss:

- expected access pattern
- retrieval behavior
- latency characteristics
- durability/availability considerations at a conceptual level
- retrieval charges
- minimum storage duration
- typical use cases
- risks

Do NOT invent current exact prices.

If numerical examples are used, clearly label them as illustrative.

Tell the learner to verify current AWS pricing and service documentation.

---

# 10. GOOGLE CLOUD STORAGE

Explain the corresponding GCS concepts.

Cover the relevant storage categories such as:

- Standard
- Nearline
- Coldline
- Archive
- automatic/managed tiering concepts where applicable

Explain:

- access patterns
- retrieval
- minimum storage duration
- lifecycle management
- use cases
- trade-offs

Create a conceptual AWS ↔ GCP mapping.

Do not claim exact equivalence when the services are only approximately equivalent.

---

# 11. AZURE STORAGE

Map the concepts to Azure.

Explain:

- Hot
- Cool
- Cold where applicable
- Archive

Explain:

- access frequency
- retrieval implications
- minimum durations
- lifecycle management
- differences from AWS/GCP

The goal is cross-cloud understanding, not memorization.

---

# 12. CROSS-CLOUD COMPARISON

Create a table:

| Concept | AWS | Google Cloud | Azure |
|---|---|---|---|
| Frequent-access tier | | | |
| Infrequent-access tier | | | |
| Archive tier | | | |
| Automatic tiering | | | |
| Lifecycle policies | | | |
| Version cleanup | | | |
| Archive retrieval trade-off | | | |
| Typical use case | | | |

Clearly mark concepts that are **not exact one-to-one equivalents**.

---

# 13. RETRIEVAL COSTS

Explain:

> Storage price is only one component of total cost.

Teach:

- retrieval fees
- data retrieval volume
- retrieval frequency
- retrieval latency
- early deletion/minimum duration
- data transfer/egress
- repeated access patterns

Give a scenario:

```text
Dataset:
10 TB

Pattern A:
Queried once every six months

Pattern B:
Queried every day

Question:
Should both datasets use the same storage class?
```

Explain the answer using economics rather than memorization.

---

# 14. MINIMUM STORAGE DURATIONS

Explain why providers may charge based on minimum storage duration for certain classes.

Teach:

```text
Stored for 5 days
but minimum billable period = longer
```

Explain the implication:

> Moving data to a cheaper tier immediately is not necessarily cheaper if the data is deleted or transitioned again before the minimum duration is satisfied.

Include examples involving:

- temporary data
- staging data
- frequently rewritten datasets
- table-format files

---

# 15. LIFECYCLE POLICIES

Teach lifecycle policies from first principles.

Explain:

> A lifecycle policy is a set of automated rules that changes or deletes objects based on conditions such as age, prefix, storage class, or version state.

Teach:

- transition
- expiration
- version expiration
- abort incomplete multipart uploads
- prefix/filter-based rules
- object age
- noncurrent versions

Show the conceptual lifecycle:

```text
Landing
   ↓ 30 days
Infrequent Access
   ↓ 180 days
Archive
   ↓ retention period
Delete
```

---

# 16. LIFECYCLE TRANSITIONS

Explain:

- transition based on object age
- transition based on prefix
- transition based on tags where supported
- multiple lifecycle stages
- transition ordering
- interaction with minimum durations

Provide representative lifecycle configuration examples.

Use AWS JSON where useful, but explain that equivalent policies exist on GCS and Azure with provider-specific syntax.

Example conceptual rule:

```json
{
  "prefix": "landing/",
  "transition_after_days": 30,
  "next_class": "infrequent-access"
}
```

Clearly label simplified examples as conceptual when they are not exact provider API schemas.

---

# 17. OBJECT EXPIRATION

Teach:

- delete after N days
- delete by prefix
- delete temporary objects
- retention boundaries
- versioned-bucket implications

Explain why expiration must be designed carefully.

Example:

```text
tmp/
  → 7 days → delete

staging/
  → 14 days → delete
```

Explain why production data should not receive broad expiration rules.

---

# 18. VERSION CLEANUP

Teach why old object versions can continue consuming storage.

Explain:

```text
Version 1
Version 2
Version 3
Current version
```

If the current version is small but historical versions are large, storage cost can continue growing.

Teach:

- current versions
- noncurrent versions
- expiration of noncurrent versions
- version retention
- compliance implications

Use the roadmap requirement:

> Expire noncurrent versions after 30 days.

Explain why this must be tested before production rollout.

---

# 19. INCOMPLETE MULTIPART UPLOAD CLEANUP

Explain:

- what multipart uploads are
- why uploads can remain incomplete
- why incomplete parts can consume storage/resources
- lifecycle cleanup

Use the roadmap requirement:

> Abort incomplete multipart uploads after 7 days.

Show a conceptual lifecycle rule.

---

# 20. PREFIX DESIGN

This is important.

Teach why prefixes should reflect operational lifecycle boundaries.

Example:

```text
bucket/
├── landing/
├── bronze/
├── silver/
├── gold/
├── tmp/
├── staging/
├── logs/
└── table-data/
```

Explain how this enables policies such as:

```text
landing/  → transition after 30 days
tmp/      → delete after 7 days
logs/     → archive after N days
table-data/ → protected from generic lifecycle rules
```

Explain why poor prefix design makes lifecycle management dangerous.

---

# 21. DATA-LAKE LAYERS AND LIFECYCLE

Teach lifecycle decisions for:

### Landing

Often suitable for aggressive retention/tiering.

### Bronze

May require longer retention.

### Silver

Often queried more frequently.

### Gold

May have business-critical retention requirements.

### Temporary

Often safe for short retention.

### Logs

Can often be archived or expired according to operational/compliance needs.

Create a decision matrix.

---

# 22. SMALL-OBJECT ECONOMICS

This must be taught carefully.

Explain why:

> A cheaper storage class does not automatically make millions of tiny files economically efficient.

Discuss:

- per-request charges
- minimum billable object size
- minimum storage duration
- metadata/listing overhead
- retrieval requests
- lifecycle-rule evaluation
- operational overhead
- compaction

Connect to Module 2.5:

- Parquet
- compression
- partitioning
- small-files problem

Do not re-teach Module 2.5 in full.

Explain the economic relationship:

```text
Too many tiny files
        ↓
More objects
        ↓
More requests
        ↓
More metadata/management overhead
        ↓
Potentially worse storage economics
```

---

# 23. CRITICAL SECTION — TABLE FORMATS

This is one of the most important advanced concepts.

Explain why generic object lifecycle rules can be dangerous for:

- Delta Lake
- Apache Iceberg
- Apache Hudi where relevant

The core principle:

> **Do not blindly transition or delete files belonging to active table snapshots.**

Explain why.

A table format may maintain:

```text
Metadata
   ↓
Snapshots / versions
   ↓
Referenced data files
```

If lifecycle management deletes a file still referenced by a table snapshot:

```text
Table metadata
     ↓
Missing data file
     ↓
Broken table
```

Teach this clearly.

---

# 24. VACUUM AND SNAPSHOT EXPIRATION

Explain the difference between:

### Generic object lifecycle

Cloud-storage-level automation.

### Table maintenance

Table-format-aware cleanup.

Explain:

```text
Object storage lifecycle
        ≠
Delta/Iceberg table maintenance
```

Teach the concepts of:

- VACUUM
- snapshot expiration
- retention
- orphan files
- metadata cleanup
- table-aware deletion

Explain that table-format tooling understands table references, while a generic lifecycle policy does not.

Do not re-teach Module 2.15 completely.

---

# 25. SAFE LIFECYCLE DESIGN FOR TABLE DATA

Teach a safe pattern:

```text
Raw landing
    ↓
Lifecycle-managed
    ↓
Bronze
    ↓
Table-format-aware maintenance
    ↓
Silver
    ↓
Table-format-aware maintenance
    ↓
Gold
```

Explain why raw landing/log/temp data is usually easier to lifecycle-manage than active table storage.

Explain how to explicitly exclude table-data prefixes from generic lifecycle policies.

---

# 26. COMPLIANCE AND RETENTION

Teach:

- retention requirements
- legal retention
- deletion deadlines
- immutability
- Object Lock
- legal holds
- governance requirements
- auditability

Explain the difference between:

```text
"Delete old data to save money"
```

and:

```text
"Delete data according to an approved retention policy"
```

The second is a governance decision.

Connect to:

- Module 2.15
- Module 2.20

Do not turn this into a full GDPR module.

---

# 27. OBJECT LOCK

Explain conceptually:

- immutable retention
- retention periods
- preventing deletion/overwrite
- compliance use cases
- interaction with lifecycle policies

Explain why cost optimization must never override legal/compliance retention.

---

# 28. LEGAL HOLDS

Explain:

- what a legal hold means
- why automated deletion may need to be prevented
- how legal holds interact with retention workflows

Use a practical scenario:

> A dataset is normally deleted after 7 years, but a legal investigation requires the relevant records to be retained longer.

Explain how a production data platform should reason about this.

---

# 29. STORAGE INVENTORY

Teach how to answer:

> "What is consuming our storage budget?"

Build toward a storage inventory/report.

The report should identify:

- prefix
- object count
- total bytes
- average object size
- largest objects
- oldest objects
- storage class
- object age
- small-object count
- noncurrent-version storage where available
- temporary/staging data

---

# 30. PYTHON STORAGE REPORT

Build a practical Python example.

Use a cloud-agnostic or AWS-first approach consistent with the roadmap.

Example conceptual interface:

```python
def build_storage_report(objects):
    ...
```

Then show how object metadata can be aggregated by:

- prefix
- class
- age bucket
- size bucket

Example output:

```text
Prefix       Objects   Total GB   Avg MB   Small Files
landing/     120000    850 GB     7.2      93000
bronze/       45000    1200 GB   27.3      21000
silver/       18000    2400 GB  136.5       1200
gold/          5000     700 GB  143.4        150
tmp/          90000      80 GB    0.9      88000
```

Explain what a senior Data Engineer would investigate.

---

# 31. STORAGE COST MODEL

Create a rigorous but understandable cost model.

Use the roadmap scenario:

> **1 TB/month growth over 3 years**

Model:

- monthly growth
- cumulative storage
- access pattern
- standard storage
- tiered storage
- retrieval
- requests
- minimum-duration effects
- projected savings

Use illustrative variables rather than inventing current provider prices.

For example:

```text
monthly_storage_cost
=
standard_gb × standard_rate
+
ia_gb × ia_rate
+
archive_gb × archive_rate
```

Then extend:

```text
total_monthly_cost
=
storage
+ requests
+ retrieval
+ transfer
+ version_storage
+ other applicable charges
```

Explain every term.

---

# 32. COST MODEL WITH ACCESS PATTERNS

Create multiple scenarios.

## Scenario A — Frequently queried data

```text
Access frequency: high
```

## Scenario B — Occasionally queried historical data

```text
Access frequency: low
```

## Scenario C — Compliance archive

```text
Access frequency: almost zero
```

Explain the appropriate storage strategy for each.

---

# 33. PROJECTED SAVINGS

Teach how to calculate:

```text
Baseline cost
        -
Optimized cost
        =
Gross savings
```

Then:

```text
Net savings
=
Gross storage savings
-
additional retrieval cost
-
additional request cost
-
transition cost
-
operational overhead
```

Explain why a storage optimization should be judged by **total cost**, not storage price alone.

---

# 34. OTHER COST LEVERS

Cover the roadmap's additional levers:

## Compression

Connect to Parquet and columnar compression.

## Duplicate deletion

Explain:

- duplicate objects
- duplicate datasets
- redundant exports
- unnecessary snapshots

## Cross-region transfer

Explain why moving data between regions can introduce unnecessary cost.

Teach:

```text
Compute near data
```

as a general architecture principle.

Do not expand into a complete networking course.

---

# 35. HANDS-ON PROJECT

Create a complete hands-on exercise based directly on the roadmap.

Project:

`policies/lifecycle/`

and:

`src/cloud_lab/storage_report.py`

The learning document must explain the exercise step by step.

---

## Step 1 — Create a test bucket

Use a dedicated test bucket.

Do NOT immediately experiment against production data.

Explain:

- naming
- encryption
- versioning
- access control
- budget awareness

---

## Step 2 — Create test prefixes

```text
landing/
bronze/
silver/
gold/
tmp/
logs/
table-data/
```

Populate them with representative test objects.

---

## Step 3 — Configure lifecycle policies

Implement the roadmap requirements:

```text
landing/
    ↓ 30 days
infrequent access

landing/
    ↓ 180 days
archive

tmp/
    ↓ 7 days
delete

noncurrent versions/
    ↓ 30 days
expire

incomplete multipart uploads/
    ↓ 7 days
abort
```

---

## Step 4 — Protect table-format data

Explicitly exclude:

```text
table-data/
```

from generic lifecycle transitions/expiration.

Explain why.

---

## Step 5 — Build storage report

Generate:

- object count
- total bytes
- prefix
- class
- age
- small-object count

---

## Step 6 — Cost calculation

Calculate:

- baseline
- optimized
- retrieval costs
- per-object/request effects
- projected monthly savings

---

## Step 7 — Apply rules

Apply lifecycle policies to the **test bucket first**.

Never instruct the learner to blindly apply destructive policies to production.

---

## Step 8 — Verify

Verification must include:

- lifecycle configuration
- test objects
- object versions
- multipart behavior
- expected transitions
- expected expiration behavior

Explain that some lifecycle actions may be asynchronous and should not be expected to occur immediately.

---

## Step 9 — Tear down

Remove test resources appropriately.

Confirm no unnecessary billable resources remain.

---

# 36. PROVIDER-SPECIFIC CODE

Use practical examples for:

### AWS

- boto3 lifecycle configuration
- listing objects
- reading object metadata
- version information where relevant
- generating storage reports

### Google Cloud

Provide representative lifecycle configuration and concepts.

### Azure

Provide representative lifecycle management concepts/configuration.

Do not make the document three separate tutorials.

AWS should remain the primary hands-on example, consistent with the roadmap.

Cross-cloud mappings should demonstrate transferable knowledge.

---

# 37. REPRESENTATIVE AWS PYTHON EXAMPLE

Include a practical example showing how lifecycle configuration can be applied using boto3.

Use a structure similar to:

```python
import boto3

s3 = boto3.client("s3")

lifecycle = {
    # provider-specific lifecycle configuration
}

s3.put_bucket_lifecycle_configuration(
    Bucket="example-test-bucket",
    LifecycleConfiguration=lifecycle,
)
```

Explain every part.

Use placeholders for bucket names.

Never include credentials.

---

# 38. STORAGE REPORT IMPLEMENTATION

Build a clean Python example.

Suggested structure:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ObjectRecord:
    key: str
    size_bytes: int
    storage_class: str
    last_modified: datetime


def build_storage_report(records):
    ...
```

The report should support aggregation by:

- prefix
- storage class
- age
- object size

Explain the design.

Keep the implementation understandable rather than over-engineered.

---

# 39. FAILURE SCENARIOS

Include realistic production failures.

At minimum:

1. Lifecycle archives frequently queried data.
2. Retrieval charges become larger than storage savings.
3. Minimum-duration charges eliminate expected savings.
4. Millions of tiny files are moved to infrequent storage.
5. Noncurrent object versions continue accumulating.
6. Incomplete multipart uploads consume storage.
7. Lifecycle deletes active Delta files.
8. Lifecycle deletes files still referenced by Iceberg snapshots.
9. Retention policy conflicts with legal hold.
10. Compliance requires data to remain immutable.
11. A lifecycle rule accidentally matches `gold/`.
12. Temporary data was placed under a production prefix.
13. Cross-region retrieval/transfer increases costs.
14. Storage inventory reveals unexpected duplicate datasets.
15. Cost model ignores request/retrieval charges.

For every scenario explain:

- symptom
- root cause
- investigation
- corrective action
- prevention

---

# 40. COMMON MISTAKES

Explicitly include the roadmap mistakes:

- Archiving data that is still queried.
- Lifecycle expiry deleting files that Delta or Iceberg still references.
- Tiering millions of tiny files.
- Forgetting that noncurrent versions continue costing money.

Also include:

- applying lifecycle policies directly to production without testing
- assuming cheaper storage always means cheaper total cost
- ignoring retrieval fees
- ignoring minimum storage durations
- ignoring request costs
- ignoring data-transfer costs
- using broad prefix rules
- mixing temporary and permanent data under the same prefix
- forgetting compliance retention
- treating lifecycle policies as table-format maintenance
- failing to measure actual savings
- failing to verify lifecycle behavior
- failing to document lifecycle ownership

---

# 41. PRODUCTION ARCHITECTURE

Include a production architecture such as:

```text
                    CLOUD OBJECT STORAGE
                           |
          +----------------+----------------+
          |                |                |
       landing/         lakehouse/          tmp/
          |                |                |
     lifecycle        table-aware        aggressive
      policies        maintenance        expiration
          |                |
     IA / archive      Delta/Iceberg
                           |
                     VACUUM / Snapshot
                       expiration
```

Explain the separation of responsibilities:

```text
Cloud lifecycle
    =
Object-level storage management

Table maintenance
    =
Table-aware data-file management

Governance
    =
Retention/compliance management
```

This distinction is critical.

---

# 42. DECISION FRAMEWORK

Create a practical decision framework.

When deciding whether to move data to a cheaper storage class, ask:

1. How often is it read?
2. How quickly must it be retrieved?
3. How much data will be retrieved?
4. How long will it remain in that class?
5. Are there minimum storage durations?
6. Are there retrieval charges?
7. Are there request charges?
8. Are there minimum billable sizes?
9. Is the data referenced by a table format?
10. Are there compliance requirements?
11. Is the data immutable?
12. Is cross-region access involved?
13. Can the data be compressed or deduplicated first?
14. Can the prefix be safely targeted by a lifecycle rule?

Then provide a final decision tree.

---

# 43. TEACH THE SENIOR DATA ENGINEER MINDSET

The learner should understand:

> Storage optimization is not simply "move everything to the cheapest tier."

It is an optimization problem involving:

```text
Cost
+
Access frequency
+
Latency
+
Retrieval
+
Retention
+
Compliance
+
Table integrity
+
Operational complexity
```

Teach the learner to optimize the **whole system**, not one billing line item.

---

# 44. KNOWLEDGE CHECKPOINTS

After each major section, add short checkpoints.

Examples:

### Storage-class checkpoint

Can the learner explain:

- standard vs IA?
- archive?
- automatic tiering?
- retrieval charges?
- minimum durations?

### Lifecycle checkpoint

Can the learner:

- create a transition rule?
- create expiration?
- expire noncurrent versions?
- abort incomplete multipart uploads?

### Table-format checkpoint

Can the learner explain:

- why generic lifecycle rules can break Delta/Iceberg?
- what VACUUM does?
- what snapshot expiration does?
- why table maintenance must be table-aware?

### Cost checkpoint

Can the learner:

- build a storage cost model?
- include retrieval?
- include requests?
- include minimum-duration effects?
- estimate savings?

---

# 45. PRACTICE EXERCISES

Create exercises progressing from beginner to advanced.

## Beginner

1. Explain storage classes.
2. Classify datasets by access frequency.
3. Design a simple lifecycle.
4. Identify data suitable for archive.

## Intermediate

5. Create prefix-based lifecycle policies.
6. Configure noncurrent-version expiration.
7. Configure multipart cleanup.
8. Build a storage inventory.
9. Identify small-object problems.
10. Compare standard vs tiered storage.

## Advanced

11. Build a three-year storage cost model.
12. Calculate projected savings.
13. Include retrieval charges.
14. Protect Delta/Iceberg data from generic lifecycle policies.
15. Design retention/compliance-aware lifecycle rules.
16. Investigate unexpected storage growth.
17. Design a multi-layer lake lifecycle architecture.
18. Audit a production lifecycle policy for safety.

---

# 46. INTERVIEW PREPARATION

Create a substantial interview section.

## Basic

- What is a storage class?
- Why do cloud providers have multiple storage classes?
- What is a lifecycle policy?
- What is automatic tiering?

## Intermediate

- Standard vs IA?
- What are retrieval charges?
- What are minimum storage durations?
- Why expire noncurrent versions?
- Why abort incomplete multipart uploads?
- How should lake prefixes be designed for lifecycle policies?

## Advanced

- Why should generic lifecycle policies not manage active Delta/Iceberg files?
- What is the difference between lifecycle expiration and VACUUM?
- How would you design a lifecycle policy for a 100 TB data lake?
- How would you calculate expected savings?
- How would you detect whether a storage optimization is actually working?
- How would you handle compliance retention?
- How would you handle legal holds?
- How would you optimize millions of small objects?

## Scenario-based

Include realistic senior-level scenarios requiring trade-off reasoning.

Example:

> A company moved 500 TB of historical Parquet data to archive storage and expected a major cost reduction. The next month, analysts repeatedly queried the data and retrieval charges exploded. How would you redesign the storage strategy?

Require the learner to explain:

- investigation
- access-pattern analysis
- class selection
- cost model
- lifecycle policy
- monitoring
- rollback/adjustment

---

# 47. FINAL ASSESSMENT

Create a final assessment with several parts.

## Part A — Concepts

Explain storage classes, lifecycle, retrieval, minimum duration, and version cleanup.

## Part B — Lifecycle Engineering

Write a lifecycle strategy for:

```text
landing/
bronze/
silver/
gold/
tmp/
logs/
table-data/
```

## Part C — Storage Reporting

Build a Python storage report.

## Part D — Cost Modeling

Model:

```text
1 TB/month growth
3 years
```

Compare:

```text
Everything Standard
vs
Tiered Storage
```

Include:

- storage
- retrieval
- requests
- minimum-duration considerations

## Part E — Table Safety

Explain why table-format data needs special treatment.

## Part F — Compliance

Design a retention-aware strategy.

## Part G — Production Design

Design a complete cloud storage lifecycle architecture.

---

# 48. MASTERY / EXIT CRITERIA

At the end of the document include:

## Topic 09 Mastery Checklist

The learner should not consider this topic complete until they can:

- [ ] Explain cloud storage economics.
- [ ] Explain standard/frequent-access storage.
- [ ] Explain infrequent-access storage.
- [ ] Explain archive storage.
- [ ] Explain automatic tiering.
- [ ] Compare AWS, GCP, and Azure storage classes conceptually.
- [ ] Explain retrieval costs.
- [ ] Explain minimum storage durations.
- [ ] Design lifecycle transitions.
- [ ] Design expiration rules.
- [ ] Clean up noncurrent versions.
- [ ] Abort incomplete multipart uploads.
- [ ] Design lifecycle-friendly prefixes.
- [ ] Explain small-object economics.
- [ ] Protect Delta/Iceberg table files from unsafe lifecycle policies.
- [ ] Explain VACUUM and snapshot expiration at the appropriate level.
- [ ] Understand retention requirements.
- [ ] Understand Object Lock.
- [ ] Understand legal holds.
- [ ] Build a storage inventory.
- [ ] Build a Python storage report.
- [ ] Build a storage cost model.
- [ ] Calculate projected savings.
- [ ] Include retrieval/request costs.
- [ ] Account for minimum-duration effects.
- [ ] Understand compression and deduplication as cost levers.
- [ ] Understand cross-region transfer costs.
- [ ] Apply lifecycle rules safely to a test environment.
- [ ] Verify lifecycle behavior.
- [ ] Explain the difference between storage lifecycle management and table maintenance.
- [ ] Design a production-ready storage lifecycle strategy.

---

# 49. VERSION AND PRICING SAFETY

Cloud storage pricing and service capabilities change.

Therefore:

- Do NOT invent current exact prices.
- Do NOT hard-code pricing as permanent facts.
- Use variables for cost models.
- Clearly label numerical examples as illustrative.
- Tell the learner to verify current pricing and service documentation before applying policies.
- Do not invent service limits.
- Do not claim exact cross-cloud equivalence where it does not exist.

The roadmap explicitly treats cloud prices and limits as changeable.

---

# 50. CODING REQUIREMENTS

The document MUST contain useful coding examples.

Primarily use:

- Python
- boto3
- representative GCS/Azure configuration
- JSON lifecycle examples
- cost-model Python calculations

Code should demonstrate:

- lifecycle configuration
- object listing
- metadata collection
- storage report generation
- aggregation
- age calculation
- cost estimation
- projected savings

Use:

- functions
- dataclasses where useful
- type hints where useful
- clear variable names
- error handling
- configuration separation
- no hard-coded credentials

Never put credentials into code.

---

# 51. TEACHING FORMAT

For important concepts use:

```text
Concept
↓
Simple explanation
↓
Why it exists
↓
How it works
↓
Example
↓
Code/configuration
↓
Cost implication
↓
Production implication
↓
Common failure
↓
Checkpoint
```

Use:

- Markdown tables
- diagrams
- Mermaid diagrams where useful
- code blocks
- practical examples
- scenario analysis
- decision matrices
- cost equations

Avoid superficial definitions.

The learner must learn to **reason about cloud storage economics and safety**, not simply memorize storage-class names.

---

# 52. FINAL PRODUCTION PROJECT

End the learning journey with a realistic production scenario:

## Cloud Data Lake Storage Optimization Project

Scenario:

A company has a growing cloud data lake.

Current structure:

```text
landing/
bronze/
silver/
gold/
tmp/
logs/
```

The lake grows:

```text
1 TB/month
```

Historical data reaches:

```text
3 years
```

The company wants:

- lower storage cost
- predictable retrieval costs
- no broken Delta/Iceberg tables
- automated cleanup
- compliance-aware retention
- storage visibility
- measurable savings

The learner must design:

1. Storage-class strategy.
2. Lifecycle policies.
3. Prefix structure.
4. Table-format protection.
5. Version cleanup.
6. Multipart cleanup.
7. Storage inventory.
8. Cost model.
9. Savings estimate.
10. Compliance controls.
11. Monitoring/verification.
12. Rollback/safety strategy.

The learner must explain every design decision.

---

# 53. FINAL VALIDATION

Before finishing the file, verify all of the following:

### Roadmap coverage

- [ ] Storage classes
- [ ] Standard/frequent access
- [ ] Infrequent access
- [ ] Archive
- [ ] Automatic tiering
- [ ] AWS
- [ ] GCP
- [ ] Azure
- [ ] Retrieval costs
- [ ] Minimum storage durations
- [ ] Lifecycle transitions
- [ ] Object expiration
- [ ] Noncurrent-version expiration
- [ ] Multipart cleanup
- [ ] Prefix design
- [ ] Small-object economics
- [ ] Delta/Iceberg lifecycle safety
- [ ] VACUUM/snapshot expiration
- [ ] Compliance
- [ ] Object Lock
- [ ] Legal holds
- [ ] Storage inventory
- [ ] Storage analytics
- [ ] Storage cost model
- [ ] Growth modeling
- [ ] Retrieval modeling
- [ ] Projected savings
- [ ] Compression
- [ ] Deduplication
- [ ] Cross-region transfer
- [ ] Hands-on lifecycle exercise
- [ ] Storage report
- [ ] Verification
- [ ] Cost checkpoint
- [ ] Common mistakes
- [ ] Practice exercises
- [ ] Interview questions
- [ ] Final assessment
- [ ] Mastery checklist

### Quality validation

- [ ] Basics → intermediate → advanced progression exists.
- [ ] Concepts are explained in simple terms first.
- [ ] Coding examples are included.
- [ ] Provider-specific examples are clearly distinguished from general concepts.
- [ ] No fabricated pricing or limits.
- [ ] No unsafe production-destructive instructions without a test-first warning.
- [ ] Table-format safety is clearly emphasized.
- [ ] Cost modeling includes more than storage GB price.
- [ ] The learner can actually perform the roadmap's hands-on exercise.

### File-scope validation

- [ ] Only `09-storage-classes-and-lifecycle-policies.md` was modified.
- [ ] No other file was changed.
- [ ] No unrelated files were created.
- [ ] No roadmap file was modified.

Do not stop at an outline.

**Write the complete, detailed, production-oriented educational content for `09-storage-classes-and-lifecycle-policies.md`.**