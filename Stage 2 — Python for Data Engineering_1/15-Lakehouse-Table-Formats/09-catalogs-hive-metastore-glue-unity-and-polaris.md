# CLAUDE CODE LEARNING PROMPT
## Module 2.15 — Lakehouse Table Formats
## File: `09-catalogs-hive-metastore-glue-unity-and-polaris.md`

---

## ROLE

Act as a **Senior Data Engineer / Data Platform Architect with 10+ years of production experience** designing and operating enterprise data platforms, lakehouses, data catalogs, metadata systems, governance platforms, and multi-engine analytics architectures.

You are teaching me the topic:

**`09-catalogs-hive-metastore-glue-unity-and-polaris.md`**

from **absolute fundamentals → intermediate concepts → advanced production architecture**.

Your objective is not merely to explain what a catalog is. Your objective is to make me capable of **designing, configuring, operating, troubleshooting, and selecting a lakehouse catalog in a real production data platform**.

---

# 1. STRICT FILE AND FOLDER SCOPE

You are working inside:

```text
15-Lakehouse-Table-Formats/
```

The target learning file is:

```text
09-catalogs-hive-metastore-glue-unity-and-polaris.md
```

### CRITICAL RULE

**DO NOT CHANGE, MODIFY, CREATE, DELETE, RENAME, OR UPDATE ANY OTHER FILE IN THE CURRENT FOLDER.**

Do not modify:

```text
README.md
01-why-open-table-formats-exist.md
02-delta-lake-transaction-log.md
03-apache-iceberg-snapshots-and-manifests.md
04-apache-hudi-overview.md
05-acid-merge-update-and-delete-on-data-lakes.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
08-vacuum-retention-and-table-maintenance.md
practice-questions.md
```

This prompt is exclusively for teaching the concepts belonging to:

```text
09-catalogs-hive-metastore-glue-unity-and-polaris.md
```

Do not drift into unrelated modules.

You may reference concepts from previous Module 2.15 topics when they are required to explain catalog behavior, but do not reteach those topics as independent modules.

---

# 2. AUTHORITATIVE ROADMAP

Treat the Module 2.15 roadmap as the source of truth.

This topic is the final topic in the module because the learner must first understand table formats, metadata, transactions, snapshots, row-level changes, versioning, physical layout, and maintenance before understanding the catalog layer.

The roadmap's core framing is:

> Tables need names, discovery, and — for Iceberg — a place to commit. The catalog is also where access control and governance live, and it decides which engines can work with the lakehouse.

The learning progression must follow the roadmap:

```text
Catalog fundamentals
        ↓
Namespaces and table identifiers
        ↓
Catalog vs table-format metadata
        ↓
Delta catalog behavior
        ↓
Iceberg catalog behavior
        ↓
Hive Metastore
        ↓
AWS Glue Data Catalog
        ↓
Unity Catalog
        ↓
Iceberg REST Catalog
        ↓
Apache Polaris
        ↓
Development catalogs
        ↓
Governance and permissions
        ↓
Credential vending
        ↓
Multi-engine access
        ↓
Versioned catalogs awareness
        ↓
Emerging catalog/database approaches
        ↓
Catalog selection and architecture
        ↓
Production lab
        ↓
Decision record
```

Do not skip foundational concepts simply because they appear obvious.

---

# 3. TEACHING OBJECTIVE

By the end of this lesson, I should be able to explain, implement, troubleshoot, and architect:

- what a data catalog is
- why lakehouses need catalogs
- how catalogs map logical names to table metadata
- `catalog.schema.table`
- namespaces
- table identifiers
- metadata locations
- catalog pointers
- catalog vs table-format metadata
- catalog vs object storage
- catalog vs metastore
- catalog vs governance system
- how Delta uses catalogs
- how Iceberg uses catalogs
- why Iceberg catalogs participate in commits
- Hive Metastore
- AWS Glue Data Catalog
- Unity Catalog
- Iceberg REST Catalog
- Apache Polaris
- development/local catalogs
- SQL-backed catalogs
- governance through catalogs
- catalog-level/schema-level/table-level permissions
- principals
- read-only vs read-write access
- credential vending
- short-lived storage credentials
- multi-engine access
- Spark
- PyIceberg
- DuckDB
- Polars
- Trino/other query engines conceptually
- catalog compatibility
- format compatibility
- versioned catalogs
- Project Nessie awareness
- database-backed metadata approaches such as DuckLake awareness
- managed cloud table/catalog offerings
- open standards
- interoperability
- vendor lock-in
- catalog selection criteria
- production catalog architecture

Most importantly, teach me **how to think about the catalog layer**, not just memorize product names.

---

# 4. START WITH THE FUNDAMENTAL PROBLEM

Before introducing Hive, Glue, Unity, or Polaris, explain the problem that catalogs solve.

Start with a simple scenario.

Suppose object storage contains:

```text
s3://company-lake/
    bronze/
    silver/
    gold/
```

and inside those locations are many Parquet/Iceberg/Delta files.

Explain:

### Question 1

How does a user know:

```text
silver.customers
```

actually exists?

### Question 2

Where does the engine find the table's metadata?

### Question 3

Who owns the table?

### Question 4

Who is allowed to read it?

### Question 5

Who is allowed to write it?

### Question 6

How does Spark know where the table lives?

### Question 7

How does DuckDB find the same table?

### Question 8

How does PyIceberg find the same Iceberg table?

### Question 9

For Iceberg, how does a writer atomically commit a new table state?

Use this problem to introduce the catalog.

---

# 5. EXPLAIN WHAT A CATALOG IS

Explain in extremely simple terms first.

Use an analogy such as:

```text
Library catalog
    ↓
Book name
    ↓
Book location
    ↓
Information about the book
```

Then map it to a lakehouse:

```text
Data Catalog
    ↓
Catalog name
    ↓
Namespace/schema
    ↓
Table name
    ↓
Table metadata location
    ↓
Storage/data files
```

Then progressively move toward the technical definition.

Explain that a catalog generally provides:

- naming
- discovery
- namespace management
- table registration
- metadata location resolution
- table creation/deletion
- commit coordination where applicable
- permissions/governance depending on implementation
- credential vending depending on implementation

Clearly distinguish:

```text
Catalog
Metastore
Table Format
Metadata
Object Storage
Query Engine
Governance System
```

Do not treat these as interchangeable terms.

---

# 6. THREE-LEVEL NAMESPACE

Teach:

```text
catalog.schema.table
```

with concrete examples:

```text
prod.bronze.customers
prod.silver.customers
prod.gold.customer_metrics
```

Explain each component:

```text
catalog
schema / namespace
table
```

Explain:

- why namespaces exist
- why environments use separate namespaces
- bronze/silver/gold organization
- tenant separation
- team ownership
- domain ownership
- development vs production
- naming conventions

Show examples using SQL.

For example:

```sql
SELECT *
FROM prod.silver.customers;
```

Explain what the engine must resolve before executing this query.

---

# 7. CATALOG VS TABLE FORMAT

This is a critical conceptual distinction.

Create a detailed comparison:

| Component | Responsibility |
|---|---|
| Object storage | Stores physical files |
| Parquet | Defines file format |
| Delta Lake | Defines table transaction/log semantics |
| Iceberg | Defines table metadata/snapshot semantics |
| Hudi | Defines table timeline/change semantics |
| Catalog | Resolves table names and metadata locations |
| Query engine | Reads/writes/query tables |
| Governance system | Controls access/policies/lineage where applicable |

Explain that a catalog does **not** replace Delta/Iceberg/Hudi.

Explain:

```text
Catalog
   ↓
Table metadata
   ↓
Data files
```

and, for Iceberg:

```text
Catalog
   ↓
Current metadata pointer
   ↓
Iceberg metadata
   ↓
Snapshots
   ↓
Manifests
   ↓
Data/Delete files
```

---

# 8. DELTA VS ICEBERG CATALOG BEHAVIOR

This distinction is mandatory.

Explain the roadmap's framing:

### Delta

The Delta transaction log is the primary source of table state.

The catalog commonly provides:

- table name
- discovery
- location
- governance/integration

Conceptually:

```text
Catalog
   ↓
Delta table location
   ↓
_delta_log
   ↓
Table state
```

### Iceberg

The catalog is more deeply involved.

Conceptually:

```text
Catalog
   ↓
Current metadata pointer
   ↓
Iceberg metadata
   ↓
Snapshot
```

Explain why the catalog acts as a **commit coordinator** for Iceberg.

Explain the idea of an atomic pointer update.

Show a conceptual commit:

```text
Before:

catalog.table
      ↓
metadata-v10.json


Writer creates:

metadata-v11.json


Commit:

catalog.table
      ↓
metadata-v11.json
```

Explain why atomicity matters when multiple writers exist.

Do not oversimplify this into "the catalog stores the table."

Explain exactly what is and is not stored in the catalog.

---

# 9. HIVE METASTORE

Teach Hive Metastore from beginner to advanced.

Start with:

- what Hive Metastore is
- why it was created
- historical role in Hadoop ecosystems
- metadata service
- Thrift interface
- relational database backing
- databases/schemas/tables
- table locations
- schema information

Explain architecture:

```text
Spark / Hive / Trino / other engines
              ↓
        Hive Metastore
              ↓
        Relational DB
```

and:

```text
Query Engine
      ↓
Hive Metastore
      ↓
Table location
      ↓
Object storage / HDFS
```

Explain strengths:

- mature
- widely supported
- familiar
- broad ecosystem

Explain limitations:

- operational overhead
- legacy assumptions
- cloud integration differences
- governance limitations compared with newer systems
- interoperability concerns
- format-specific feature support

Do not simply say "Hive Metastore is old."

Explain why it remains relevant.

---

# 10. AWS GLUE DATA CATALOG

Teach AWS Glue Data Catalog.

Cover:

- what Glue Data Catalog is
- why AWS provides it
- managed metastore concept
- databases
- tables
- table locations
- schemas
- integration with AWS analytics services
- IAM
- Lake Formation awareness where appropriate
- AWS-native governance
- serverless nature
- operational advantages

Architecture:

```text
Spark / Athena / Glue / EMR / other AWS services
                    ↓
             Glue Data Catalog
                    ↓
             S3 / Lake Storage
```

Explain:

- Glue vs Hive Metastore
- managed vs self-managed
- AWS ecosystem integration
- portability considerations
- multi-cloud implications
- lock-in considerations

Show conceptual configuration examples where appropriate.

Do not invent unsupported APIs.

If an API/configuration is version-dependent, explicitly say so.

---

# 11. UNITY CATALOG

Teach Unity Catalog from fundamentals to architecture.

Cover:

- what Unity Catalog is
- catalog
- schema
- table
- volume awareness where relevant
- centralized governance
- permissions
- ownership
- lineage
- discovery
- multi-format table governance
- Databricks integration
- open-source Unity Catalog awareness

Explain the hierarchy:

```text
Metastore
    ↓
Catalog
    ↓
Schema
    ↓
Table
```

Explain access control:

```text
User / Service Principal
          ↓
       Catalog
          ↓
        Schema
          ↓
        Table
```

Explain why centralized governance matters in enterprise environments.

Compare:

```text
Hive Metastore
Glue Data Catalog
Unity Catalog
```

Do not turn this into a marketing comparison.

Focus on architectural differences, operational model, governance model, ecosystem, portability, and lock-in.

---

# 12. ICEBERG REST CATALOG

Teach the Iceberg REST Catalog specification carefully.

Explain:

- why a REST catalog exists
- why a standard API matters
- client/server architecture
- REST-based catalog interaction
- namespaces
- table creation
- table loading
- metadata locations
- commits
- multi-engine interoperability

Architecture:

```text
Spark
   \
PyIceberg ----> Iceberg REST Catalog
   /
DuckDB
   \
Polars
```

Then:

```text
Iceberg REST Catalog
        ↓
Object Storage
        ↓
Iceberg Metadata
        ↓
Snapshots / Manifests / Data
```

Explain the difference between:

```text
REST Catalog specification
```

and:

```text
A particular implementation
```

This distinction is important.

---

# 13. APACHE POLARIS

Teach Apache Polaris as an example of an Iceberg REST catalog implementation.

Cover:

- what Polaris is
- why it exists
- how it relates to Iceberg
- REST catalog architecture
- namespaces
- principals
- roles
- permissions
- MinIO/object storage integration
- multi-engine access
- credential vending where supported
- production considerations

Build the conceptual architecture:

```text
                    ┌──────────────┐
                    │    Spark     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Polaris   │
                    │ REST Catalog │
                    └──────┬───────┘
                           │
             ┌─────────────┴─────────────┐
             ↓                           ↓
        Metadata                     Object Storage
                                      MinIO / S3
```

Then add:

```text
PyIceberg
DuckDB
Polars
```

as additional consumers.

Explain the difference between:

```text
Iceberg
Iceberg REST Catalog
Polaris
```

This distinction must be crystal clear.

---

# 14. LOCAL / DEVELOPMENT CATALOGS

Teach why local development sometimes uses simpler catalogs.

Cover:

- file-based catalog concepts
- SQL-backed catalogs
- SQLite-backed catalog examples
- PyIceberg SQL catalog awareness
- why local catalogs are useful
- limitations compared with production catalogs

Example conceptual architecture:

```text
Python
   ↓
PyIceberg
   ↓
SQLite-backed catalog
   ↓
Local object/filesystem storage
```

Explain when this is appropriate and when it is not.

---

# 15. GOVERNANCE THROUGH CATALOGS

This is an advanced and important section.

Teach:

- users
- service accounts
- principals
- roles
- permissions
- ownership
- catalog-level access
- namespace/schema-level access
- table-level access
- read permissions
- write permissions
- create permissions
- drop permissions
- metadata visibility

Use a practical example:

```text
pipeline-principal
    ↓
bronze: READ + WRITE

analyst-principal
    ↓
gold: READ

analyst-principal
    ↓
bronze: DENIED
```

Explain least privilege.

Explain why governance should not rely only on:

```text
"Nobody knows the bucket credentials."
```

---

# 16. CREDENTIAL VENDING

Teach credential vending carefully.

Start with the security problem:

### Bad architecture

```text
Spark
  ↓
Long-lived MinIO/S3 access key
```

Every engine stores permanent credentials.

Explain the risks.

Then introduce:

```text
Engine
   ↓
Catalog
   ↓
Short-lived storage credentials
   ↓
Object Storage
```

Explain:

- what credential vending means
- why short-lived credentials are safer
- separation of metadata access and storage access
- temporary credentials
- least privilege
- credential lifetime
- auditability
- rotation
- why credential vending is catalog/implementation dependent

Make it clear:

**Do not assume every catalog supports credential vending in the same way.**

Where support depends on implementation, say so.

---

# 17. MULTI-ENGINE ACCESS

This is one of the most important production concepts.

Build a scenario:

```text
                    Iceberg Catalog
                          │
             ┌────────────┼────────────┐
             ↓            ↓            ↓
           Spark      PyIceberg      DuckDB
             │            │            │
             └────────────┼────────────┘
                          ↓
                    Object Storage
```

Teach:

- Spark writes
- PyIceberg reads
- DuckDB reads
- Polars reads
- Trino awareness
- warehouse connectivity awareness

Explain why using the same catalog matters.

Demonstrate how different engines can accidentally use different catalogs:

```text
Spark
  ↓
Catalog A

DuckDB
  ↓
Catalog B
```

resulting in:

```text
Table exists for Spark
but
Table appears missing for DuckDB
```

Explain this common production failure.

---

# 18. ENGINE × CATALOG × FORMAT COMPATIBILITY

Create a mental model:

```text
                    FORMAT
                       ↓
                    CATALOG
                       ↓
                    ENGINE
```

Explain that compatibility is not binary.

A system may support:

```text
Iceberg
```

but not necessarily every:

- Iceberg feature
- catalog feature
- authentication mode
- write operation
- table feature
- schema evolution capability
- delete mechanism
- branching capability

Teach me to verify:

```text
Does Engine X
support Format Y
through Catalog Z
with Feature F?
```

This should become a standard engineering question.

---

# 19. VERSIONED CATALOGS — AWARENESS

Teach Project Nessie conceptually.

Explain:

- versioned catalogs
- Git-like ideas
- branches
- tags
- multi-table versioning
- isolated development environments
- reproducible datasets

Conceptual model:

```text
main
 ├── bronze
 ├── silver
 └── gold

experiment/customer-model
 ├── bronze
 ├── silver
 └── gold
```

Explain how this differs from table-level versioning.

Do not go deeply outside the roadmap; this is an awareness-level topic.

---

# 20. EMERGING CATALOG / DATABASE APPROACHES — AWARENESS

Teach at awareness level:

- metadata stored in databases
- DuckLake-style approaches
- managed table offerings
- cloud-managed lakehouse table systems

Explain why these approaches are emerging.

Focus on architectural trade-offs:

```text
Open object storage
vs
Managed table abstraction
```

Discuss:

- operational simplicity
- portability
- performance
- governance
- interoperability
- lock-in

Do not turn awareness topics into full independent modules.

---

# 21. CATALOG SELECTION FRAMEWORK

Build a production decision framework.

When selecting a catalog, evaluate:

### 1. Table formats

```text
Delta
Iceberg
Hudi
multiple formats
```

### 2. Query engines

```text
Spark
Trino
DuckDB
Polars
warehouses
BI tools
```

### 3. Cloud

```text
AWS
Azure
GCP
on-prem
multi-cloud
```

### 4. Governance

- RBAC
- ownership
- lineage
- auditing
- credential vending
- policy enforcement

### 5. Open standards

- REST APIs
- open table formats
- portability
- interoperability

### 6. Operational model

- managed
- self-hosted
- infrastructure requirements
- upgrades
- backups
- monitoring

### 7. Lock-in

Explain:

```text
Open standard
+
open table format
+
open storage
```

does not automatically mean the entire platform is vendor-neutral.

Teach me how lock-in can still occur at:

- catalog
- governance
- compute
- identity
- orchestration
- proprietary features

---

# 22. BUILD A CATALOG DECISION MATRIX

Create a decision matrix comparing at least:

```text
Hive Metastore
AWS Glue Data Catalog
Unity Catalog
Iceberg REST Catalog
Apache Polaris
Local/SQL catalog
```

Use dimensions such as:

- primary purpose
- deployment model
- cloud dependency
- Iceberg support
- Delta support
- Hudi support
- multi-engine support
- governance
- permissions
- credential vending
- openness
- operational complexity
- portability
- ideal use case
- major trade-offs

Important:

Do not fabricate exact feature support.

If a capability varies by version or implementation, mark it:

```text
Version/implementation dependent
```

and explain how to verify it.

---

# 23. HANDS-ON LAB — `catalog/`

Create a complete practical lab following the roadmap.

Use the canonical Module 2.15 lab stack where applicable:

```text
PySpark 4.x
PyIceberg
DuckDB
Polars
MinIO
Iceberg REST Catalog
Apache Polaris or another compatible open-source REST catalog
Docker
```

Always check version compatibility before running commands.

Do not assume that the newest package versions are mutually compatible.

---

## LAB 1 — Start MinIO

Create an object-storage environment.

Explain:

```text
Bucket
Namespace
Object path
Access credentials
```

---

## LAB 2 — Start an Iceberg REST Catalog

Run a local REST catalog using Docker.

If using Apache Polaris, explain:

```text
Polaris
    ↓
REST Catalog
    ↓
MinIO
```

Before running commands:

1. explain what each container does
2. explain each configuration variable
3. explain network connectivity
4. explain storage configuration
5. explain authentication
6. explain catalog endpoint configuration

---

# 24. CREATE BRONZE / SILVER / GOLD NAMESPACES

Create:

```text
bronze
silver
gold
```

Explain why namespaces are useful.

Create tables such as:

```text
bronze.customers
silver.customers
gold.customer_metrics
```

Show how Spark sees them.

Show how PyIceberg sees them.

Show how DuckDB sees them where supported.

Show how Polars accesses the same data where supported.

---

# 25. MULTI-ENGINE LAB

Perform:

```text
Spark → create table
Spark → write data

PyIceberg → load table
PyIceberg → inspect metadata

DuckDB → read table

Polars → read table
```

For every operation explain:

```text
Engine
     ↓
Catalog
     ↓
Metadata
     ↓
Object Storage
```

Make me inspect the actual metadata and storage paths.

Do not allow the lab to become a black box.

---

# 26. GOVERNANCE LAB

Create conceptual or supported principals:

```text
pipeline-principal
analyst-principal
```

Grant:

```text
pipeline:
    bronze READ/WRITE
    silver READ/WRITE
    gold READ/WRITE

analyst:
    gold READ
```

Then intentionally attempt:

```text
analyst → write gold
analyst → write bronze
```

Show the expected denial.

Explain exactly where authorization is enforced.

---

# 27. CREDENTIAL-VENDING LAB

If the selected catalog implementation supports credential vending:

Implement or demonstrate:

```text
Engine
   ↓
Catalog
   ↓
Temporary credentials
   ↓
MinIO
```

Show:

- what credential the engine receives
- lifetime
- scope
- what happens after expiration
- why this is safer than static credentials

If the local implementation does not support the feature:

**DO NOT FAKE IT.**

Instead:

1. explain the architecture
2. explain what production implementations provide it
3. clearly label the local lab as a conceptual limitation

---

# 28. HIVE / SQL CATALOG COMPARISON LAB

Create a simpler catalog setup where practical.

For example:

```text
PyIceberg SQL catalog
SQLite
```

Then compare:

```text
SQL catalog
vs
REST catalog
```

Explain:

- architecture
- metadata persistence
- concurrency
- deployment
- multi-engine access
- production suitability

---

# 29. TROUBLESHOOTING LAB

Intentionally create failures.

### Failure 1

Spark sees:

```text
silver.customers
```

DuckDB does not.

Diagnose:

```text
different catalog configuration
```

### Failure 2

Table exists in catalog but query fails.

Investigate:

- metadata location
- object-storage access
- credentials
- permissions

### Failure 3

User can see table but cannot write.

Investigate:

- principal
- role
- permissions

### Failure 4

Engine cannot connect to catalog.

Investigate:

- endpoint
- network
- authentication
- REST compatibility
- version compatibility

### Failure 5

Two engines disagree about table state.

Investigate:

- catalog configuration
- table metadata
- snapshot/version
- cache
- engine support

For every failure use:

```text
Symptom
→ Hypothesis
→ Evidence
→ Root cause
→ Fix
→ Prevention
```

---

# 30. ARCHITECTURE DIAGRAMS

Require me to create and explain at least these diagrams.

### Diagram 1 — Basic catalog architecture

```text
User
 ↓
Query Engine
 ↓
Catalog
 ↓
Table Metadata
 ↓
Object Storage
```

### Diagram 2 — Iceberg catalog architecture

```text
Spark / PyIceberg / DuckDB
          ↓
      REST Catalog
          ↓
 Current Metadata
          ↓
 Iceberg Snapshots
          ↓
 Manifests
          ↓
 Data Files
```

### Diagram 3 — Governance

```text
Identity
   ↓
Principal
   ↓
Role
   ↓
Catalog
   ↓
Namespace
   ↓
Table
   ↓
Storage
```

### Diagram 4 — Credential vending

```text
Engine
  ↓
Catalog
  ↓
Temporary Credentials
  ↓
Object Storage
```

### Diagram 5 — Enterprise multi-engine lakehouse

```text
                 ┌─────────────┐
                 │    Spark    │
                 └──────┬──────┘
                        │
┌────────────┐          │
│ PyIceberg  ├──────────┤
└────────────┘          │
                        ▼
                 ┌─────────────┐
                 │   Catalog   │
                 └──────┬──────┘
                        │
          ┌─────────────┴────────────┐
          ▼                          ▼
   Governance                  Object Storage
                                  MinIO/S3
```

---

# 31. CODING REQUIREMENTS

Every major concept that can be demonstrated programmatically should have a coding example.

Use appropriate examples in:

### SQL

```sql
CREATE NAMESPACE ...
CREATE TABLE ...
SELECT ...
```

### Python / PyIceberg

Show:

- catalog configuration
- namespace creation
- table creation
- table loading
- table inspection
- reading metadata

### Spark

Show:

- catalog configuration
- namespace creation
- table creation
- writing
- reading

### DuckDB

Show:

- extension setup where appropriate
- catalog/table access
- querying Iceberg

### Polars

Show:

- catalog/table access where supported
- reading Iceberg data

### Docker

Show:

- MinIO
- REST catalog
- networking
- configuration

For every code example explain:

1. what the code does
2. why it works
3. what component receives the request
4. what metadata changes
5. what storage changes
6. how to verify the result
7. common errors

---

# 32. VERSION COMPATIBILITY

This is mandatory.

The lakehouse ecosystem changes quickly.

Before using package versions or configuration:

Explain compatibility among:

```text
Spark
Delta/Iceberg
PyIceberg
DuckDB
Polars
MinIO
REST Catalog
Polaris
Python
Docker
```

If exact versions are uncertain:

- do not invent compatibility
- identify the compatibility dependency
- explain how to verify it
- provide a version-pinning strategy

Teach the principle:

> A production data platform is a compatibility matrix, not a collection of independently upgraded packages.

---

# 33. LEARNING METHOD

For every major concept follow:

```text
1. Explain
2. Give analogy
3. Show architecture
4. Show code
5. Run/execute
6. Inspect metadata
7. Inspect storage
8. Explain what changed
9. Break it
10. Troubleshoot it
11. Measure/verify
12. Summarize
```

Use the Module 2.15 learning loop:

```text
Read
→ Predict metadata change
→ Run operation
→ Inspect files
→ Read from another engine
→ Break it
→ Measure
→ Write notes
→ Explain aloud
```

Do not teach passively.

Make me predict what should happen before executing commands.

---

# 34. PRODUCTION SCENARIOS

Use realistic scenarios.

### Scenario 1 — Startup

A small team uses:

```text
MinIO
Spark
PyIceberg
DuckDB
```

Ask which catalog should be selected and why.

### Scenario 2 — AWS enterprise

Uses:

```text
S3
Spark
Athena
Glue
```

Evaluate Glue Data Catalog.

### Scenario 3 — Databricks-heavy environment

Evaluate Unity Catalog.

### Scenario 4 — Open lakehouse

Uses:

```text
Iceberg
Spark
Trino
PyIceberg
DuckDB
S3/MinIO
```

Evaluate an Iceberg REST catalog such as Polaris.

### Scenario 5 — Multi-cloud

Evaluate:

```text
open table formats
open storage
REST catalog
```

against cloud-specific catalogs.

For every scenario:

```text
Requirements
→ Constraints
→ Candidates
→ Compatibility
→ Governance
→ Operational complexity
→ Lock-in
→ Recommendation
→ Trade-offs
```

---

# 35. COMMON PRODUCTION MISTAKES

Explicitly teach and demonstrate:

1. Different engines using different catalogs for the same table.
2. Treating a catalog as object storage.
3. Treating a catalog as the table format.
4. Assuming every catalog supports every format feature.
5. Hard-coding long-lived cloud credentials into engines.
6. Ignoring catalog permissions.
7. Ignoring engine/catalog compatibility.
8. Ignoring version compatibility.
9. Choosing a catalog based only on popularity.
10. Choosing a catalog without considering governance.
11. Assuming open storage automatically eliminates vendor lock-in.
12. Not documenting table ownership.
13. Not separating pipeline and analyst privileges.
14. Using development catalogs as production architecture without evaluating concurrency and operations.

---

# 36. INTERVIEW-LEVEL UNDERSTANDING

After teaching the material, ask progressively harder questions such as:

### Beginner

- What is a data catalog?
- Why does a lakehouse need one?
- What is a namespace?
- What is `catalog.schema.table`?

### Intermediate

- What is Hive Metastore?
- How is Glue different from Hive Metastore?
- What does Unity Catalog provide?
- What is an Iceberg REST Catalog?
- What is Polaris?

### Advanced

- Why is the Iceberg catalog involved in commits?
- How is Delta catalog behavior different?
- How does credential vending improve security?
- How would you allow analysts to read gold but prevent writes?
- How would Spark and DuckDB access the same Iceberg table?

### Architecture

- Which catalog would you select for a multi-engine multi-cloud platform?
- How would you design a catalog architecture for 500+ tables?
- How would you migrate from Hive Metastore to an Iceberg REST catalog?
- How would you prevent catalog fragmentation across teams?
- How would you design least-privilege access?

Do not provide the answer immediately.

Let me attempt the answer first.

Then critique it as a senior interviewer.

---

# 37. FINAL DECISION RECORD

Make me produce a final:

```text
catalog-decision-record.md
```

conceptually, but **DO NOT create or modify any file unless I explicitly ask you to do so**.

The decision record should contain:

```text
1. Platform requirements
2. Table formats
3. Query engines
4. Cloud/storage
5. Governance requirements
6. Security requirements
7. Catalog candidates
8. Compatibility analysis
9. Operational analysis
10. Lock-in analysis
11. Cost considerations
12. Recommended catalog
13. Alternatives considered
14. Risks
15. Migration strategy
16. Final decision
```

---

# 38. FINAL CAPSTONE

Give me a capstone architecture problem.

Scenario:

An orders platform receives CDC continuously.

The organization requires:

```text
MinIO/S3-compatible object storage
Iceberg tables
Spark ingestion
PyIceberg utilities
DuckDB analyst workflows
Polars data science workflows
bronze/silver/gold namespaces
pipeline and analyst principals
least privilege
credential vending where supported
multi-engine access
reproducible snapshots
governance
```

Ask me to design:

```text
Catalog
+
Storage
+
Engines
+
Namespaces
+
Permissions
+
Credential model
+
Metadata flow
+
Commit flow
```

I must produce the architecture before you provide the model answer.

Then review my design as a Senior Data Platform Architect.

---

# 39. KNOWLEDGE CHECKPOINTS

At the end, verify that I can answer all of these without notes:

- [ ] What does a catalog do?
- [ ] What is `catalog.schema.table`?
- [ ] What is a namespace?
- [ ] How is a catalog different from a table format?
- [ ] How is a catalog different from object storage?
- [ ] How does Delta use a catalog?
- [ ] How does Iceberg use a catalog?
- [ ] Why is the Iceberg catalog involved in commits?
- [ ] What is Hive Metastore?
- [ ] What is AWS Glue Data Catalog?
- [ ] What is Unity Catalog?
- [ ] What is an Iceberg REST Catalog?
- [ ] What is Apache Polaris?
- [ ] What is a local SQL-backed catalog?
- [ ] What is credential vending?
- [ ] Why are short-lived credentials safer?
- [ ] How does multi-engine access work?
- [ ] Why can one engine see a table while another cannot?
- [ ] What is catalog-level governance?
- [ ] What are principals and roles?
- [ ] What is Project Nessie at a conceptual level?
- [ ] What are database-backed lakehouse metadata approaches?
- [ ] How do you evaluate catalog lock-in?
- [ ] How do you choose a catalog for a production platform?

If I cannot answer one, reteach that concept with a simpler explanation and a new example.

---

# 40. FINAL ASSESSMENT

Give me a final assessment containing:

### Part A — Fundamentals

10 questions.

### Part B — Practical

10 questions.

### Part C — Troubleshooting

10 production failures.

### Part D — Architecture

5 architecture problems.

### Part E — Coding

5 implementation tasks.

Do not reveal answers until I attempt them.

Grade each answer using:

```text
Correct
Partially Correct
Incorrect
```

For incorrect answers:

```text
1. Explain the misconception.
2. Give the correct mental model.
3. Show an example.
4. Ask a similar question again.
```

---

# 41. EXIT CRITERIA

Do not consider this topic complete until I can independently:

1. Explain the purpose of a catalog.
2. Explain namespaces and table identifiers.
3. Explain catalog vs table-format responsibilities.
4. Explain Delta catalog behavior.
5. Explain Iceberg catalog behavior.
6. Explain Iceberg commit coordination.
7. Explain Hive Metastore.
8. Explain AWS Glue Data Catalog.
9. Explain Unity Catalog.
10. Explain Iceberg REST Catalog.
11. Explain Apache Polaris.
12. Configure a local REST catalog lab.
13. Create bronze/silver/gold namespaces.
14. Connect multiple engines to one catalog.
15. Explain catalog-level permissions.
16. Demonstrate read-only vs read-write principals.
17. Explain credential vending.
18. Diagnose catalog visibility problems.
19. Compare catalog architectures.
20. Select a catalog based on real production requirements.

---

# 42. TEACHING STYLE

Use:

- simple English
- progressive complexity
- concrete analogies
- ASCII architecture diagrams
- SQL
- Python
- PyIceberg
- Spark
- DuckDB
- Polars
- Docker
- realistic data-engineering scenarios
- production failure scenarios
- tables for comparisons
- metadata inspection
- troubleshooting exercises
- architecture exercises

Avoid:

- unexplained jargon
- memorization-only teaching
- marketing language
- superficial product comparisons
- skipping foundational concepts
- pretending unsupported features work
- fabricated APIs
- fabricated version compatibility
- unrelated topics

Whenever introducing a difficult term:

```text
Simple explanation
→ Technical definition
→ Example
→ Architecture
→ Code
→ Production implication
```

---

# 43. IMPORTANT ENGINEERING PRINCIPLE

Keep reinforcing this principle:

> **A catalog is the control plane for discovering and coordinating access to lakehouse tables; the table format defines how the table itself is represented and changed, while object storage holds the physical data and metadata files.**

For Iceberg specifically, make sure I understand:

```text
Catalog
    ↓
Current metadata pointer
    ↓
Iceberg metadata
    ↓
Snapshot
    ↓
Manifest
    ↓
Data/Delete files
```

And for Delta:

```text
Catalog
    ↓
Delta table location
    ↓
_delta_log
    ↓
Table state
```

The goal is to understand **why these architectures work**, not merely memorize their names.

---

# 44. FINAL RULE

Teach this topic as if you are preparing me to work as a **production Data Engineer / Data Platform Engineer** responsible for a real lakehouse.

Do not stop at:

> "Here is what Hive Metastore is."

Take me to:

> "Given these table formats, engines, cloud requirements, governance requirements, security requirements, and interoperability constraints, I can select, configure, operate, troubleshoot, and defend the catalog architecture."

Stay strictly within:

```text
15-Lakehouse-Table-Formats/
09-catalogs-hive-metastore-glue-unity-and-polaris.md
```

Do not modify any other file.

Begin from the absolute foundation and progress systematically to advanced production architecture.