# 03 — Glue Data Catalog, Crawlers and Schema Management

> **G3 Topic 03 — AWS Data Engineering Deep Dive**
>
> **Learning path:** Simple foundation → mental model → AWS concepts → hands-on → CLI/API/code → architecture → schema management → production operations → troubleshooting → governance → advanced patterns

---

## 1. Module Overview

This module teaches how to turn files in an AWS data lake into **discoverable, understandable, governed metadata** using the AWS Glue Data Catalog, Glue Crawlers, explicit schema management, partition management, and Iceberg catalog integration.

The central idea is simple:

```text
S3
 ↓
Physical data
 ↓
Metadata
 ↓
Glue Data Catalog
 ↓
Tables / schemas / partitions
 ↓
Athena / Glue / EMR / other consumers
```

Amazon S3 answers:

> **Where does the data live?**

The Glue Data Catalog answers:

> **What is this data, what is its schema, where is it located, and how should compatible engines interpret it?**

AWS describes the Data Catalog as a centralized metadata repository for datasets, including location, schema, and related metadata. It can be populated by crawlers or by manually defining metadata. citeturn0search4turn0search18

### Why this matters

A production data lake is not just an S3 bucket full of files. Without reliable metadata, consumers struggle to answer:

- What does this dataset contain?
- Which columns exist?
- What are their types?
- Which S3 location is authoritative?
- Which folders are partitions?
- Has the schema changed?
- Can a query engine discover the relevant data efficiently?
- Who owns and controls the metadata?
- Which changes are safe?

### Relationship to the surrounding roadmap

**Previous Topic 02 — S3 Tables, Access Points and Batch Operations**

- physical object storage
- S3 access patterns
- S3 Tables and Iceberg-managed table storage
- operational S3 capabilities

**This Topic 03**

- Glue Data Catalog
- crawlers
- schema discovery
- schema governance
- partition metadata
- Iceberg catalog integration

**Later Topic 04 — Glue ETL and Data Quality**

- transformation execution
- Glue ETL jobs
- data quality execution

**Later Topic 05 — Athena Advanced**

- advanced query optimization
- partition projection
- CTAS/UNLOAD
- advanced Iceberg querying

This module introduces relationships to those services without re-teaching their later topics.

### Prerequisites

You should already be comfortable with:

- S3 buckets, prefixes and objects
- CSV/JSON/Parquet
- basic SQL
- Python fundamentals
- IAM fundamentals
- basic AWS CLI usage
- basic Terraform concepts

You do **not** need prior Glue Data Catalog expertise.

### Expected outcomes

By the end, you should be able to:

1. Explain the Glue Data Catalog mental model.
2. Create and inspect databases and tables.
3. Understand columns, storage descriptors, table properties and partitions.
4. Create catalog metadata with Athena, CLI, boto3 and Terraform.
5. Explain what Glue Crawlers do and do not guarantee.
6. Choose between crawlers and explicit schema management.
7. Diagnose schema drift and unsafe schema changes.
8. Manage Hive-style partitions and understand partition pruning.
9. Explain MSCK REPAIR TABLE, partition indexes and partition projection at the correct level.
10. Explain Glue as a catalog for Iceberg.
11. Design a production metadata architecture.
12. troubleshoot catalog, crawler, schema, partition and permission failures.
13. reason about security, cost, quotas and operational ownership.

---

# 2. Why a Data Catalog Exists

Imagine an S3 data lake:

```text
s3://company-data/

bronze/
  orders/
  customers/
  events/

silver/
  orders/
  customers/

gold/
  sales/
  customer_metrics/
```

An S3 listing can tell you that objects exist.

It does not, by itself, give an analytics engine a durable relational-style understanding such as:

```text
Table: orders

order_id      bigint
customer_id   bigint
order_date    date
amount        decimal
status        string

Location:
s3://company-data/silver/orders/

Partitions:
year, month, day
```

A catalog supplies that metadata layer.

```text
Raw Storage
    ↓
Metadata
    ↓
Data Catalog
    ↓
Query / Processing Engines
```

### Metadata is part of the data platform

Treat metadata as production infrastructure.

Bad metadata can cause:

- incorrect query results
- failed queries
- excessive scans
- slow partition discovery
- schema incompatibilities
- broken consumers
- security mistakes
- difficult incident response
- duplicated manual work

A useful production principle is:

> **Data tells you what happened. Metadata tells your platform how to understand and operate on what happened.**

---

# 3. Data Catalog Mental Model

Start with this hierarchy:

```text
Glue Data Catalog
│
├── Database
│     │
│     └── Table
│           ├── Columns
│           ├── Partitions
│           ├── Properties
│           └── Storage Descriptor
│
└── Other metadata and catalog-level configuration
```

### Database

A Glue database is primarily a **logical metadata namespace**.

It is not the same concept as:

- a PostgreSQL database
- a MySQL database
- a transactional application database
- a warehouse compute boundary

Example namespaces:

```text
analytics
finance
marketing
operations
```

### Table

A Glue table is a metadata definition describing a logical dataset.

It can describe:

- table name
- columns
- data types
- S3 location
- input/output formats
- serialization/deserialization
- partition keys
- table parameters
- table type
- format-specific properties

### Columns

A column definition typically includes:

```text
name
type
comment / metadata
```

Common analytical types include:

```text
string
boolean
int
bigint
double
float
date
timestamp
decimal
array
map
struct
```

The exact type vocabulary depends on the catalog/API and consuming engine.

### Partitions

A partition represents a logical subdivision of a dataset.

Example:

```text
orders/
  year=2026/
    month=10/
      day=06/
```

The partition metadata tells compatible query engines how partition values map to physical locations.

### Table properties

Table parameters/properties can carry metadata such as:

- classification
- format indicators
- compression-related information
- serialization settings
- application metadata
- Iceberg-related properties where applicable

Do not assume every parameter is interpreted uniformly by every engine.

### Storage Descriptor

For traditional Glue table definitions, the storage descriptor can describe:

- columns
- S3 location
- input format
- output format
- SerDe information
- additional storage metadata

This is important because consumers need both **logical schema** and **physical interpretation**.

---

# 4. Glue Data Catalog Fundamentals

## 4.1 Catalog

The Data Catalog is a managed metadata repository.

It is not the physical data lake.

Think:

```text
S3
=
physical data

Glue Data Catalog
=
metadata about physical data
```

A catalog can be consumed by multiple compatible analytics and processing services.

---

## 4.2 Database

Example:

```text
analytics
├── orders
├── customers
├── products
└── payments
```

The database gives you a namespace for tables.

A useful organizational strategy is to align namespaces with:

- domain
- environment
- lifecycle
- ownership
- governance boundary

Avoid creating hundreds of arbitrary databases merely because a team needs a temporary table.

---

## 4.3 Table

Example:

```text
orders
├── order_id
├── customer_id
├── order_date
├── amount
└── status
```

The table is a **logical contract for interpreting a dataset**.

It does not imply that Glue stores the actual Parquet/CSV/JSON records.

---

## 4.4 Columns

Column metadata establishes:

```text
Name → Type → Meaning
```

For example:

```text
order_id       bigint
customer_id    bigint
amount         decimal(18,2)
status         string
order_date     date
```

Do not treat the type as merely documentation. A type influences:

- query semantics
- serialization
- joins
- filtering
- aggregation
- compatibility
- downstream contracts

---

## 4.5 Partitions

Suppose:

```text
s3://company-data/orders/
  year=2026/
    month=10/
      day=01/
      day=02/
      day=03/
```

The table can describe partition keys:

```text
year
month
day
```

A query such as:

```sql
SELECT *
FROM orders
WHERE year = 2026
  AND month = 10
  AND day = 03;
```

can allow the query engine to eliminate irrelevant partitions when the table and query structure support partition pruning.

---

## 4.6 Table Properties

Properties are key/value metadata associated with a table.

Example conceptually:

```text
classification = parquet
compression = snappy
owner = data-platform
```

Do not blindly copy parameters from one table format to another. Some properties are service-, format-, or engine-specific.

---

## 4.7 Storage Descriptor

For traditional Hive-compatible Glue tables, the storage descriptor connects logical metadata to physical storage interpretation.

Conceptually:

```text
Table
 |
 +-- Columns
 |
 +-- Partition Keys
 |
 +-- Storage Descriptor
       |
       +-- S3 Location
       +-- Input Format
       +-- Output Format
       +-- SerDe
```

The exact API shape is versioned and service-defined. Use the current AWS API reference when building production automation.

---

# 5. Glue Data Catalog and S3

The core relationship:

```text
S3
 |
 | physical data
 v
Parquet / JSON / CSV / Avro / other formats
 |
 v
Glue Data Catalog
 |
 | metadata
 v
Athena / Glue / EMR / compatible consumers
```

A practical distinction:

| Layer | Primary responsibility |
|---|---|
| S3 | Store objects/data |
| Glue Catalog | Describe datasets and metadata |
| Crawler | Discover/infer metadata |
| Query engine | Read/query data using metadata |
| Data pipeline | Produce and validate data |

This separation is fundamental to AWS data-platform architecture.

---

# 6. Creating Tables in the Glue Data Catalog

There is no single correct mechanism.

Common approaches:

```text
Athena DDL
AWS CLI
boto3
Terraform
Iceberg/table-aware writers
Crawler
```

The right choice depends on:

- ownership
- schema stability
- governance
- discovery needs
- deployment model
- table format
- operational scale

---

## 6.1 Method 1 — Athena DDL

A conventional external table can be created with SQL:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS analytics.orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_date DATE,
    amount DECIMAL(18,2),
    status STRING
)
PARTITIONED BY (
    year INT,
    month INT,
    day INT
)
STORED AS PARQUET
LOCATION 's3://example-data/orders/';
```

The exact SQL syntax and supported properties depend on the engine and table format. Verify the current Athena documentation before production use.

### When useful

Athena DDL is attractive when:

- SQL is the team's normal interface.
- analysts/data engineers need to create metadata quickly.
- the catalog is used primarily by Athena.
- the table definition is relatively stable.

### Production concern

If production metadata is managed through ad-hoc SQL from multiple people, you can lose:

- version control
- review
- reproducibility
- ownership

For governed production infrastructure, consider IaC or pipeline-managed metadata.

---

## 6.2 Method 2 — AWS CLI

The AWS CLI exposes Glue catalog APIs.

For example, inspect a database:

```bash
aws glue get-database \
  --name analytics
```

List tables:

```bash
aws glue get-tables \
  --database-name analytics
```

Get one table:

```bash
aws glue get-table \
  --database-name analytics \
  --name orders
```

The current AWS CLI supports `glue create-table` and its document-style `--table-input` structure. citeturn0search13

A practical rule:

> Use `aws glue help` and the current AWS CLI reference to verify nested JSON structures before automating complex catalog definitions.

---

## 6.3 Method 3 — boto3

AWS Glue's Python client provides APIs such as:

- `create_database`
- `get_database`
- `create_table`
- `get_table`
- `update_table`
- `get_tables`
- `get_partitions`
- `batch_create_partition`
- `batch_delete_partition`
- crawler APIs such as `start_crawler` and `get_crawler`

AWS's current boto3 reference documents `create_table` as creating a table definition in the Data Catalog. citeturn0search8

Example:

```python
import boto3

glue = boto3.client("glue", region_name="us-east-1")

glue.create_database(
    DatabaseInput={
        "Name": "analytics",
        "Description": "Production analytics metadata",
    }
)
```

Create a simple table:

```python
import boto3

glue = boto3.client("glue")

glue.create_table(
    DatabaseName="analytics",
    TableInput={
        "Name": "orders",
        "Description": "Orders stored as Parquet in S3",
        "StorageDescriptor": {
            "Columns": [
                {"Name": "order_id", "Type": "bigint"},
                {"Name": "customer_id", "Type": "bigint"},
                {"Name": "amount", "Type": "decimal(18,2)"},
                {"Name": "status", "Type": "string"},
            ],
            "Location": "s3://example-data/orders/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            },
        },
        "PartitionKeys": [
            {"Name": "year", "Type": "int"},
            {"Name": "month", "Type": "int"},
            {"Name": "day", "Type": "int"},
        ],
        "TableType": "EXTERNAL_TABLE",
    },
)
```

### Exception handling

```python
import boto3
from botocore.exceptions import ClientError

glue = boto3.client("glue")

try:
    response = glue.get_table(
        DatabaseName="analytics",
        Name="orders",
    )
except glue.exceptions.EntityNotFoundException:
    print("Table does not exist")
except ClientError as exc:
    print(f"AWS API error: {exc}")
```

AWS's current `get_table` API retrieves the table definition and also exposes Iceberg-related retrieval options in the current API surface. citeturn0search9

### Credential rule

Never hardcode:

```python
AWS_ACCESS_KEY_ID = "..."
AWS_SECRET_ACCESS_KEY = "..."
```

Prefer:

```text
IAM role
IAM Identity Center
temporary credentials
instance/task role
```

---

## 6.4 Method 4 — Terraform

Terraform can define catalog infrastructure as code.

A simplified example:

```hcl
resource "aws_glue_catalog_database" "analytics" {
  name        = "analytics"
  description = "Production analytics metadata"
}
```

A catalog table can be represented using the AWS provider's Glue catalog table resource.

Conceptual pattern:

```hcl
resource "aws_glue_catalog_table" "orders" {
  name          = "orders"
  database_name = aws_glue_catalog_database.analytics.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://example-data/orders/"
    input_format  = "..."
    output_format = "..."

    ser_de_info {
      name                  = "orders-serde"
      serialization_library = "..."
    }

    columns {
      name = "order_id"
      type = "bigint"
    }

    columns {
      name = "amount"
      type = "decimal(18,2)"
    }
  }
}
```

**Important:** provider schemas evolve. Treat the example as an IaC pattern and verify the current AWS provider resource schema before applying it.

Deployment lifecycle:

```bash
terraform init
terraform plan
terraform apply
terraform destroy
```

Production rule:

> If metadata is part of a production platform's desired state, version it like infrastructure.

---

## 6.5 Method 5 — Iceberg Writers

A table-aware Iceberg engine can maintain table metadata according to Iceberg semantics while using a catalog to make the table discoverable.

This differs from:

```text
Manually define table metadata
```

versus:

```text
Use an Iceberg-aware writer/table engine
to create and evolve a table
```

Do not manually mutate Iceberg metadata files unless you understand the table format and engine contract. Prefer supported Iceberg APIs and engines.

---

# 7. Explicit Schema vs Inferred Schema

This is one of the most important design decisions.

| Dimension | Explicit Schema | Inferred Schema |
|---|---|---|
| Control | High | Lower |
| Speed to discovery | Moderate | High |
| Flexibility | Moderate | High |
| Schema drift detection | Easier to control | Easier to accidentally absorb |
| Production safety | High with governance | Depends on controls |
| Automation | High | High |
| Governance | Strong | Requires guardrails |
| Best use | Stable/contracted data | Discovery/exploration |

### Explicit schema

You say:

```text
order_id = bigint
amount = decimal(18,2)
status = string
```

The platform does not guess the intended schema.

### Inferred schema

A discovery process examines source data and derives a likely schema.

Inference is useful because it reduces manual metadata work.

But:

> **Inference is a discovery mechanism, not proof that the inferred schema is semantically correct.**

Production schemas need ownership and validation.

---

# 8. Glue Crawlers

AWS Glue Crawlers are programs that inspect data sources, use classifiers to infer structure, and write metadata to the Data Catalog. AWS documents crawler behavior as classification, grouping into tables/partitions, and writing metadata to the catalog. citeturn0search6turn0search17

A simple mental model:

```text
S3 Data
   ↓
Glue Crawler
   ↓
Classify / inspect
   ↓
Infer schema
   ↓
Detect partitions
   ↓
Create/update catalog metadata
```

## Why crawlers exist

Without automated discovery:

```text
New data
   ↓
Engineer inspects it
   ↓
Engineer updates metadata
```

With a crawler:

```text
New data
   ↓
Crawler
   ↓
Metadata discovery
   ↓
Catalog update
```

Automation reduces manual effort.

It does **not** eliminate the need for schema governance.

---

# 9. Crawler Targets

A crawler target defines what the crawler should inspect.

Common data-lake patterns include S3 prefixes.

Example:

```text
s3://company-data/raw/orders/
```

Better than:

```text
s3://company-data/
```

for a narrowly scoped crawler.

### Why scope matters

An enterprise lake may contain:

```text
raw/
bronze/
silver/
gold/
temporary/
quarantine/
logs/
exports/
```

A crawler should not automatically scan everything.

Scope crawlers according to:

- ownership
- dataset boundaries
- schema compatibility
- lifecycle
- data format
- expected partitioning
- change frequency

---

# 10. Classifiers

A classifier determines whether and how input data can be recognized.

AWS Glue provides built-in classifiers and supports custom classifiers. The classifier output includes format/classification and schema information. AWS documents formats including JSON and CSV and supports custom classifier mechanisms such as Grok, XML and JSON-path based approaches. citeturn0search10

Conceptually:

```text
Crawler
   ↓
Classifier
   ↓
Recognize format
   ↓
Infer schema
```

Examples:

```text
JSON
CSV
Parquet
Avro
database sources
```

### Classifier ordering matters

A crawler can have an ordered set of custom classifiers. A classifier that successfully recognizes a source can determine the schema used for that data. citeturn0search6

### Production lesson

If a crawler generates surprising metadata, investigate:

1. input files
2. classifier
3. crawler target
4. crawler grouping behavior
5. inferred schema
6. resulting catalog definition

Do not immediately blame Athena.

---

# 11. Schema Inference

Given:

```json
{
  "order_id": 101,
  "customer_id": 22,
  "amount": 499.50
}
```

A discovery process might infer:

```text
order_id      integer
customer_id   integer
amount        double
```

That inference can be useful.

But consider:

```json
{"amount": 100}
```

and later:

```json
{"amount": "100.50"}
```

The platform now faces conflicting evidence.

The important question is not:

> "What type did the crawler choose?"

It is:

> "Why did the source contract allow the type to change, and what should the production platform do about it?"

---

# 12. Schema Inference Problems

## Problem 1 — Numeric type changes

File A:

```text
amount = 100
```

File B:

```text
amount = "100.50"
```

Potential outcomes include:

- inferred type changes
- incompatible records
- consumer failures
- coercion differences
- query errors

The correct response is investigation, not blind acceptance.

---

## Problem 2 — Missing column

File A:

```text
customer_id
```

File B:

```text
(no customer_id)
```

Is that:

- a valid optional field?
- a producer bug?
- a new version?
- an incomplete file?

The schema system cannot answer the business meaning automatically.

---

## Problem 3 — Numeric to string

```text
price: 49.99
```

becomes:

```text
price: "49.99"
```

This may look harmless but can affect:

- arithmetic
- sorting
- joins
- downstream schemas
- validation
- partition expressions

---

## Problem 4 — Structural change

Before:

```json
{
  "customer": {
    "id": 123
  }
}
```

After:

```json
{
  "customer": 123
}
```

This is a much deeper schema change than adding a field.

---

# 13. Schema Drift

Distinguish two concepts:

```text
Schema Evolution
=
controlled structural change

Schema Drift
=
unexpected structural change
```

### Examples of drift

- API changes an integer to string.
- JSON object becomes scalar.
- CSV header changes unexpectedly.
- CDC source changes column type.
- Event producer adds incompatible fields.
- A partition contains files with incompatible schemas.

### Production response

Treat drift as an operational event:

```text
Detect
 ↓
Classify
 ↓
Assess impact
 ↓
Quarantine / reject / adapt
 ↓
Update contract if intentional
 ↓
Validate consumers
 ↓
Deploy controlled change
```

---

# 14. Crawler Schema Change Policies

Crawler behavior can be configured so that schema changes are either incorporated into the Data Catalog or logged rather than automatically changing the existing schema.

AWS currently documents:

```text
UpdateBehavior:
  UPDATE_IN_DATABASE
  LOG

DeleteBehavior:
  LOG
  DELETE_FROM_DATABASE
  DEPRECATE_IN_DATABASE
```

citeturn0search1turn0search12

AWS also documents crawler configurations that can merge new columns, ignore schema changes, and make partitions inherit the table schema. citeturn0search3

### Why this matters

A production crawler should not have unrestricted authority to rewrite a critical table's schema simply because a source file changed.

A safer pattern for governed data is often:

```text
Crawler
 ↓
Discovery
 ↓
Review / validation
 ↓
Controlled catalog update
```

rather than:

```text
Crawler
 ↓
Automatic production contract rewrite
```

### Example CLI pattern

AWS documents a crawler configuration pattern for allowing only new columns to be merged:

```bash
aws glue update-crawler \
  --name myCrawler \
  --configuration '{"Version": 1.0, "CrawlerOutput": {"Tables": {"AddOrUpdateBehavior": "MergeNewColumns"}}}'
```

For a crawler that should log schema changes rather than modify the existing table:

```bash
aws glue update-crawler \
  --name myCrawler \
  --schema-change-policy UpdateBehavior=LOG \
  --configuration '{"Version": 1.0, "CrawlerOutput": {"Partitions": {"AddOrUpdateBehavior": "InheritFromTable"}}}'
```

These are documented AWS patterns; verify current CLI/API behavior for your account and CLI version before production automation. citeturn0search3

---

# 15. When NOT to Use Crawlers

Do not make "crawler everywhere" your default architecture.

Consider explicit metadata management when you have:

- stable production schemas
- strict data contracts
- high consumer criticality
- deterministic deployments
- regulated metadata
- frequent ingestion where crawling adds unnecessary work
- predictable table definitions
- strong schema ownership

Alternatives include:

```text
Terraform
Athena DDL
boto3
explicit schema definitions
pipeline-managed catalog updates
Iceberg-aware table writers
```

### Crawler sweet spot

Crawlers are particularly valuable for:

- discovery
- exploratory data
- heterogeneous source environments
- initial cataloging
- datasets whose physical layout changes in manageable ways

The correct architecture is usually **selective**, not ideological.

---

# 16. Crawler Scheduling

Crawler execution can be:

- manual
- scheduled
- triggered by workflow automation
- configured for incremental/recrawl behavior

AWS exposes crawler schedule, recrawl policy and crawler state through its API. Current crawler APIs also support incremental recrawl concepts. citeturn0search7

### Scheduling principle

If metadata changes once per day:

```text
daily crawler
```

may be sensible.

If data arrives every minute:

```text
crawler every minute
```

is usually not the first design you should reach for.

Consider:

- explicit partition registration
- event-driven discovery
- incremental crawls
- table-aware ingestion
- catalog updates as part of the pipeline

AWS documents incremental crawls as a way to add only new partitions in suitable scenarios and also documents S3-event-based crawl acceleration. citeturn0search5

---

# 17. Crawler Costs and Operational Considerations

Cost and operational drivers include:

- crawler runtime
- crawler frequency
- amount of data/location being inspected
- repeated inference
- partition discovery
- unnecessary metadata updates
- operational debugging

Do not use a crawler schedule simply because it is easy to configure.

Use:

```text
Metadata change frequency
+
dataset scale
+
consumer criticality
+
governance
+
cost
```

to determine the strategy.

Always verify current AWS Glue pricing before production budgeting.

---

# 18. Partition Management

Partitioning is both a physical layout decision and a metadata decision.

Example:

```text
s3://orders/
  year=2026/
    month=10/
      day=06/
```

Each partition has:

```text
partition key
partition value
partition location
catalog metadata
```

For example:

```text
year = 2026
month = 10
day = 06

location =
s3://orders/year=2026/month=10/day=06/
```

---

# 19. Hive-Style Partitions

Hive-style layout:

```text
year=2026/month=10/day=06/
```

is useful because both humans and compatible tools can understand:

```text
key=value
```

The partition structure can be represented in catalog metadata.

A common pattern:

```text
orders/
  year=2026/
    month=09/
    month=10/
```

### Production rule

Choose partition keys based on actual query access patterns and data volume.

Do not partition every column.

---

# 20. MSCK REPAIR TABLE

`MSCK REPAIR TABLE` is a mechanism available in Athena/Hive-compatible workflows for discovering Hive-style partitions that exist in storage but are not registered in the catalog.

Conceptually:

```sql
MSCK REPAIR TABLE orders;
```

Think:

```text
S3 layout
   ↓
discover partition directories
   ↓
update partition metadata
```

### Useful when

- partitions are Hive-style
- files/directories were added outside the normal registration path
- you need a simple repair/discovery operation

### Limitations

Do not treat MSCK as a universal partition management strategy.

It does not replace:

- good partition design
- controlled ingestion
- schema governance
- partition indexing
- projection strategies
- explicit metadata pipelines

For very large partition counts, repeatedly scanning/discovering the storage layout can become operationally unattractive.

---

# 21. Explicit Partition Registration

Partitions can be managed explicitly through catalog APIs and supported SQL workflows.

Boto3 provides partition APIs such as:

```python
glue.get_partitions(
    DatabaseName="analytics",
    TableName="orders",
)
```

and batch operations such as:

```python
glue.batch_create_partition(...)
glue.batch_delete_partition(...)
```

### Why explicit registration can be better

Your ingestion pipeline already knows:

```text
New partition:
year=2026
month=10
day=06
```

Instead of discovering it later, the pipeline can register it as part of the ingestion transaction/workflow.

This creates a deterministic flow:

```text
Write data
   ↓
Validate
   ↓
Register partition
   ↓
Publish metadata
   ↓
Query
```

---

# 22. Partition Indexes

Partition indexes address a catalog lookup scaling problem.

AWS documents that when a table has hundreds of thousands of partitions, a `GetPartitions` request without an index may require loading all partitions before filtering; an index can allow a subset of matching partitions to be retrieved instead. citeturn0search2

Mental model:

```text
Without index:

GetPartitions
   ↓
Load many/all partition metadata
   ↓
Filter

With index:

GetPartitions
   ↓
Index lookup
   ↓
Candidate partitions
```

### Example

Partition keys:

```text
country
category
year
month
creationDate
```

An index can be built over a selected subset/permutation of partition keys.

### When useful

Partition indexes are useful when:

- partition counts are high
- catalog partition lookups become a bottleneck
- queries/consumers use selective partition expressions

They are not a replacement for good partition design.

AWS documents current integration and usage constraints; verify the latest documentation before relying on specific engine behavior. citeturn0search2

---

# 23. Partition Projection Awareness

Partition projection is primarily an Athena-side concept for reducing dependence on explicitly stored partition metadata in appropriate datasets.

Mental model:

```text
Traditional:

Catalog stores partitions
        ↓
Engine looks them up

Projection:

Engine derives possible partitions
        ↓
Query-time calculation
```

It can help avoid metadata explosion for predictable partition schemes.

Example conceptual partition domain:

```text
year = 2020..2030
month = 1..12
day = 1..31
```

The engine can derive candidate partitions from the projection configuration.

### Important boundary

This module only establishes the architectural relationship.

Advanced Athena query behavior, projection configuration details and query optimization belong primarily to the later Athena topic.

---

# 24. Partition Pruning

Suppose the table has:

```text
year
month
day
```

Query:

```sql
SELECT *
FROM orders
WHERE year = 2026
  AND month = 10;
```

Without effective pruning:

```text
scan many partitions
```

With effective pruning:

```text
select relevant partitions
        ↓
scan less data
```

Relationship:

```text
Catalog metadata
      ↓
Partition structure
      ↓
Query predicate
      ↓
Partition pruning
      ↓
Less data scanned
      ↓
Lower latency / potentially lower query cost
```

This is why partition design is not merely an organizational preference.

---

# 25. Partition Design Mistakes

## Mistake 1 — Too many partitions

Example:

```text
customer_id=1
customer_id=2
...
customer_id=50000000
```

Potential consequence:

- huge metadata volume
- slow catalog operations
- operational complexity

## Mistake 2 — Very low-value partition key

Example:

```text
country
```

if only two countries exist and most queries scan both.

## Mistake 3 — Extremely high-cardinality key

A unique identifier usually makes a poor partition key.

## Mistake 4 — Tiny files inside partitions

Even good partition pruning cannot rescue a dataset with millions of tiny files.

## Mistake 5 — Poor date layout

If consumers constantly filter by date but the layout does not reflect that access pattern, pruning opportunities can be poor.

## Mistake 6 — Partitioning by columns rarely used for filtering

Partition keys should serve real access patterns.

---

# 26. Schema Evolution

Schema evolution means allowing data structure to change over time without unnecessarily breaking consumers.

### Generally lower-risk change

```text
Add a nullable column
```

### Potentially breaking changes

```text
Rename column
Remove column
Change type
Change semantics
Change nested structure
```

Decision matrix:

| Change | Typical risk | Strategy |
|---|---:|---|
| Add optional column | Low/Medium | Controlled rollout |
| Remove column | High | Deprecation period |
| Rename column | High | Compatibility layer or versioned field |
| int → string | High | Contract review |
| string → int | High | Validation + migration |
| Meaning changes | Very High | New field/version |

The critical distinction is:

```text
Technical compatibility
≠
Business semantic compatibility
```

A field can retain the same physical type while its meaning changes.

---

# 27. Schema Drift

Schema evolution:

```text
Producer intentionally changes schema
```

Schema drift:

```text
Producer changes schema unexpectedly
```

Examples:

```text
API:
amount: 100
→
amount: "100.00"

CSV:
customer_id
→
client_id

CDC:
status VARCHAR
→
status JSON

Event:
customer object
→
customer scalar
```

Production systems should detect drift rather than silently normalize it.

---

# 28. Production Schema Management Strategy

A robust pattern:

```text
Producer
   ↓
Schema Contract
   ↓
Validation
   ↓
Ingestion
   ↓
Catalog
   ↓
Consumers
```

### Ownership

Define:

- producer owner
- platform owner
- consumer owner
- schema approval owner

### Versioning

Example:

```text
orders.v1
orders.v2
```

or compatible field evolution within one logical contract.

### Compatibility

Ask:

- Can old consumers still read new data?
- Can new consumers read old data?
- Is the change additive?
- Does the meaning change?
- Does physical type change?
- Is migration required?

### Rollback

A schema change should have a rollback plan.

For high-criticality datasets:

```text
Proposed schema
 ↓
Compatibility validation
 ↓
Consumer impact assessment
 ↓
Approval
 ↓
Deploy
 ↓
Observe
```

---

# 29. Data Contracts Awareness

A data contract is a producer-consumer agreement covering things such as:

- schema
- semantics
- quality expectations
- ownership
- delivery expectations
- compatibility

Do not confuse:

```text
Glue Catalog
=
metadata registry
```

with:

```text
Data Contract
=
organizational/technical agreement
```

The catalog can represent part of a contract, but it does not automatically enforce the full contract.

---

# 30. Glue Data Catalog + Apache Iceberg

A key roadmap concept is:

> **Glue Data Catalog can act as a catalog for Iceberg tables.**

Conceptually:

```text
S3
 |
 | Iceberg data + metadata
 v
Iceberg Table
 |
 v
Glue Catalog
 |
 +── Athena
 +── EMR
 +── other compatible engines
```

The catalog's role is to make table identity and metadata discoverable to compatible consumers.

### Iceberg mental model

Iceberg is a table format.

It manages concepts such as:

- snapshots
- manifests
- data files
- schema
- partition specification
- table properties

The catalog answers:

```text
Where is the table?
How do I identify it?
How do compatible engines locate its current metadata?
```

Do not conflate:

```text
Iceberg metadata
```

with:

```text
Glue Catalog metadata
```

They are related layers.

---

# 31. Glue Catalog vs S3 Tables

Topic 02 introduced S3 Tables.

Conceptually compare:

```text
General-purpose S3 + Glue Catalog
```

with:

```text
S3 Tables
```

| Dimension | S3 + Glue Catalog | S3 Tables |
|---|---|---|
| Physical storage | General-purpose S3 | Managed table-bucket model |
| Catalog | Glue Catalog commonly used | S3 Tables integrates table management |
| Operational control | High | More managed |
| Flexibility | Very high | More opinionated |
| Maintenance | More responsibility on platform | Managed table maintenance capabilities |
| Best fit | Broad data-lake architectures | Managed tabular lakehouse patterns |

The key lesson:

> S3 Tables and a general-purpose S3 + Glue Catalog architecture solve overlapping lakehouse problems with different management boundaries.

Do not re-learn the entire S3 Tables topic here.

---

# 32. Glue Schema Registry Awareness

Do not confuse these two services:

```text
Glue Data Catalog
=
metadata about datasets/tables
```

versus:

```text
Glue Schema Registry
=
versioned schemas for supported event/streaming use cases
```

A schema registry is useful when producers and consumers exchange structured events.

Concepts include:

- schema versions
- compatibility
- producer/consumer contracts
- event serialization
- schema evolution

Streaming architecture is covered later in the AWS roadmap. Here, understand the distinction and why both metadata systems can exist.

---

# 33. Column Statistics

Statistics provide information that can help query/optimization systems reason about data.

Examples include:

- minimum
- maximum
- null-related information
- cardinality/distinctness awareness
- distribution-related information

The Glue API exposes operations for updating and deleting column statistics. citeturn0search11

Mental model:

```text
Table
 |
 +-- Schema
 |
 +-- Partitions
 |
 +-- Statistics
        |
        +-- information about data distribution
```

Do not assume that merely having statistics guarantees a specific optimizer decision. Actual behavior depends on the consuming engine and current service implementation.

---

# 34. Permissions and Security

A production catalog architecture needs layered authorization.

Think:

```text
Catalog permission
        +
Underlying data permission
        +
Additional governance controls
```

For a traditional S3-backed table, a successful query may require the principal to have:

- permission to discover/use catalog metadata
- permission to access the underlying S3 data
- any additional governance authorization

Lake Formation can introduce additional governance controls and is covered later in the roadmap.

### Security checklist

```text
[ ] IAM least privilege
[ ] No long-lived credentials in code
[ ] S3 Block Public Access
[ ] Encryption
[ ] KMS where required
[ ] Controlled crawler roles
[ ] Controlled catalog permissions
[ ] Cross-account access reviewed
[ ] Audit logging
[ ] Schema changes controlled
[ ] Metadata changes tracked
```

---

# 35. Cross-Account Catalog Access

A common enterprise architecture:

```text
Account A
Data Lake
   |
   v
Glue Catalog
   |
   v
Account B
Analytics
```

Cross-account access requires coordinated authorization.

Consider:

- IAM
- resource policies where supported
- S3 bucket policy
- catalog/resource sharing model
- Lake Formation
- organizational boundaries
- encryption/KMS
- auditability

Do not copy an old cross-account policy from a blog and assume it is correct for today's AWS environment.

The correct approach is:

```text
Identify resource
 ↓
Identify principal
 ↓
Identify owning account
 ↓
Identify sharing mechanism
 ↓
Grant minimum required permissions
 ↓
Test
 ↓
Audit
```

---

# 36. Catalog Federation Awareness

Large organizations rarely have only one metadata system.

They may have:

```text
Operational databases
Data warehouses
S3 data lakes
External catalogs
SaaS data platforms
Multiple AWS accounts
```

Catalog federation means exposing/discovering metadata across systems through a common access or discovery model.

The goal is:

```text
Many metadata sources
        ↓
Unified discovery experience
```

This is an awareness topic here, not a full federation implementation course.

---

# 37. Service Limits and Quotas

Do not design a platform around assumed limits.

Watch:

- catalog table counts
- partition counts
- crawler limits
- API request rates
- API throttling
- regional service availability
- partition-index constraints
- table-format-specific constraints

Use this reasoning loop:

```text
Expected scale
      ↓
Current AWS quota
      ↓
Headroom
      ↓
Architecture decision
```

Always verify current AWS Service Quotas and Glue documentation before production design. Never hardcode remembered quota numbers into architecture documents.

---

# 38. Production Metadata Architecture

A realistic architecture:

```text
                    DATA SOURCES
                 /              \
              Batch           Streaming
                 \              /
                  \            /
                       S3
                        |
                 +------+------+
                 |             |
              Bronze         Silver
                 |             |
                 +------+------+
                        |
                 Glue Data Catalog
                        |
              +---------+---------+
              |         |         |
           Athena      Glue      EMR
              |         |         |
              +---------+---------+
                        |
                       Gold
```

### Responsibilities

**S3**

```text
physical data
```

**Glue Catalog**

```text
metadata
schemas
table definitions
partition metadata
```

**Crawler**

```text
metadata discovery
```

**Explicit schema pipeline**

```text
controlled metadata
```

**Consumers**

```text
query / transform / analytics
```

---

# 39. Realistic Production Scenario — E-Commerce

Datasets:

```text
orders
customers
products
payments
clickstream
```

Possible strategy:

```text
S3
 ↓
Raw
 ↓
Discovery
 ↓
Controlled metadata
 ↓
Silver
 ↓
Gold
```

Not every dataset needs the same catalog mechanism.

### Example

**Raw clickstream**

```text
Crawler
```

because discovery is useful.

**Production orders table**

```text
Explicit schema
+
controlled schema evolution
```

because consumers depend on stable semantics.

**Iceberg silver table**

```text
Iceberg-aware writer
+
Glue catalog
```

because the table format itself manages table semantics.

The architecture is intentionally hybrid.

---

# 40. Hands-On Labs

## Lab 1 — Create a Glue Database

### Goal

Create:

```text
analytics
```

### CLI

```bash
aws glue create-database \
  --database-input '{"Name":"analytics","Description":"Analytics metadata"}'
```

Verify:

```bash
aws glue get-database \
  --name analytics
```

### boto3

```python
import boto3

glue = boto3.client("glue")

glue.create_database(
    DatabaseInput={
        "Name": "analytics",
        "Description": "Analytics metadata",
    }
)

print(glue.get_database(Name="analytics"))
```

### Break it

Try creating the same database again.

Observe the error.

### Lesson

Understand idempotency expectations and exception handling rather than blindly retrying.

---

## Lab 2 — Create an Explicit Table

Create a small Parquet dataset in S3.

Register:

```text
analytics.orders
```

Verify:

```text
schema
location
columns
partitions
```

Use:

```bash
aws glue get-table \
  --database-name analytics \
  --name orders
```

---

## Lab 3 — Run a Crawler

Create:

```text
s3://de-lab/orders/
```

Put sample files underneath it.

Create a crawler targeting that prefix.

Run it.

Inspect:

```text
database
table
columns
classification
location
partitions
```

---

## Lab 4 — Crawler Schema Change

Start with:

```text
order_id
amount
status
```

Add:

```text
currency
```

Run the crawler.

Compare:

```text
Before
vs
After
```

Document:

```text
What changed?
Why?
Was the change expected?
Would production accept it automatically?
```

---

## Lab 5 — Schema Drift Incident

Start with:

```text
amount = 100
```

Then introduce:

```text
amount = "100.50"
```

Run discovery.

Document:

```text
Symptom
Evidence
Root cause
Catalog result
Consumer impact
Remediation
Preventive control
```

---

## Lab 6 — Partition Discovery

Create:

```text
orders/
  year=2026/
    month=10/
      day=01/
      day=02/
```

Use crawler discovery or explicit registration.

Verify partition metadata.

Then query only:

```text
year=2026
month=10
day=02
```

Reason about pruning.

---

## Lab 7 — Partition Scaling

Create a controlled high-partition-count test dataset.

Investigate:

- catalog lookup behavior
- partition indexes
- `GetPartitions`
- partition projection awareness
- query planning

Do not create millions of real AWS partitions in a learning account merely to prove a point. Use synthetic/local modeling when possible.

---

## Lab 8 — Iceberg Catalog

Using a currently supported Iceberg-compatible engine/tool:

1. Create a small Iceberg table.
2. Store it in S3.
3. Use Glue as the catalog where supported.
4. Verify discovery.
5. Inspect table metadata through supported APIs.
6. Query it with a compatible engine.

Do not manually edit Iceberg metadata files.

---

## Lab 9 — Production Schema Management

Design:

```text
Producer
   ↓
Validation
   ↓
Catalog
   ↓
Consumers
```

Test an additive schema change.

Then test a breaking type change.

For each, record:

```text
Compatibility
Consumer impact
Approval requirement
Rollback
```

---

# 41. Break/Fix Scenarios

## Incident 1 — Crawler Creates Incorrect Schema

### Symptom

```text
amount
```

is cataloged as:

```text
string
```

instead of:

```text
decimal
```

### Investigation

```text
Source files
 ↓
Classifier
 ↓
Crawler target
 ↓
Inference
 ↓
Catalog definition
```

### Questions

- Are all files compatible?
- Are some records quoted?
- Is there a mixed-format dataset?
- Did a source producer change?
- Was the crawler schema-change policy too permissive?

### Production lesson

Never fix only the catalog if the source contract is still broken.

---

## Incident 2 — New Partition Not Visible

### Symptom

S3 contains:

```text
year=2026/month=10/day=06/
```

but the query engine does not see it.

### Investigation

```text
S3 path
 ↓
Partition layout
 ↓
Crawler / registration
 ↓
Catalog
 ↓
Permissions
 ↓
Query engine
```

Commands:

```bash
aws s3 ls s3://example/orders/year=2026/month=10/
```

```bash
aws glue get-partitions \
  --database-name analytics \
  --table-name orders
```

### Root causes

Possible causes include:

- partition not registered
- wrong prefix
- wrong table location
- schema incompatibility
- permission issue
- query predicate mismatch

---

## Incident 3 — Query Scans Too Much Data

Investigate:

```text
Partition layout
Partition keys
Catalog metadata
Query predicates
File organization
```

Ask:

> Is the query filtering on the partition keys?

Then ask:

> Is the physical layout actually aligned with access patterns?

---

## Incident 4 — Schema Drift Breaks Consumer

```text
Producer
 ↓
Source schema
 ↓
Catalog
 ↓
Consumer
```

Determine whether:

- producer changed intentionally
- crawler changed metadata
- consumer expected old schema
- a data contract was missing

---

## Incident 5 — Millions of Partitions

Ask:

1. Why were there so many partitions?
2. Is the partition key too high-cardinality?
3. Are partitions actually used for filtering?
4. Would partition indexes help?
5. Would projection be appropriate?
6. Should the table design change?
7. Are tiny files contributing to the problem?

Do not immediately add more metadata infrastructure to compensate for a bad physical model.

---

## Incident 6 — Catalog Access Denied

Investigate:

```text
IAM
 ↓
Glue permissions
 ↓
S3 permissions
 ↓
KMS permissions if applicable
 ↓
Lake Formation controls if enabled
 ↓
Cross-account configuration
```

Separate:

```text
Can I discover the table?
```

from:

```text
Can I read the underlying data?
```

---

# 42. Troubleshooting Framework

Use:

```text
Symptom
  ↓
Check Source Data
  ↓
Check Catalog
  ↓
Check Schema
  ↓
Check Partitions
  ↓
Check Permissions
  ↓
Check Query Engine
  ↓
Root Cause
  ↓
Fix
  ↓
Verify
```

Every incident report should contain:

```text
Symptom
Evidence
Commands
Interpretation
Root Cause
Fix
Verification
Production Lesson
```

### Evidence-first debugging

Bad:

> "The crawler is broken."

Good:

```text
Crawler succeeded.
S3 contains the new partition.
GetPartitions does not return it.
Therefore investigate partition registration/discovery.
```

Production engineers use evidence to eliminate hypotheses.

---

# 43. AWS CLI Operational Examples

## List databases

```bash
aws glue get-databases
```

## Inspect one database

```bash
aws glue get-database \
  --name analytics
```

## List tables

```bash
aws glue get-tables \
  --database-name analytics
```

## Get a table

```bash
aws glue get-table \
  --database-name analytics \
  --name orders
```

## Get partitions

```bash
aws glue get-partitions \
  --database-name analytics \
  --table-name orders
```

## Start a crawler

```bash
aws glue start-crawler \
  --name orders-crawler
```

## Inspect crawler

```bash
aws glue get-crawler \
  --name orders-crawler
```

## List crawlers

```bash
aws glue list-crawlers
```

These are current AWS CLI command patterns. Verify options against the installed CLI version and current AWS reference before scripting complex JSON input. The AWS CLI currently exposes `glue create-table`, including document-style table input and partition-index related options. citeturn0search13

---

# 44. Python / boto3 Operational Examples

## List tables

```python
import boto3

glue = boto3.client("glue")

paginator = glue.get_paginator("get_tables")

for page in paginator.paginate(DatabaseName="analytics"):
    for table in page["TableList"]:
        print(table["Name"])
```

## Get table safely

```python
import boto3
from botocore.exceptions import ClientError

glue = boto3.client("glue")

try:
    table = glue.get_table(
        DatabaseName="analytics",
        Name="orders",
    )
    print(table["Table"])
except glue.exceptions.EntityNotFoundException:
    print("orders does not exist")
except ClientError as exc:
    raise RuntimeError(f"Glue API call failed: {exc}") from exc
```

## Start crawler

```python
import boto3

glue = boto3.client("glue")

glue.start_crawler(Name="orders-crawler")
```

## Inspect crawler state

```python
crawler = glue.get_crawler(
    Name="orders-crawler"
)

state = crawler["Crawler"]["State"]
print(state)
```

### Production rules

- Use paginators for list APIs where available.
- Handle throttling and transient errors.
- Log request context.
- Do not print secrets.
- Use IAM roles/temporary credentials.
- Make metadata mutations auditable.
- Avoid unbounded retry loops.

---

# 45. Terraform Examples

## Glue database

```hcl
resource "aws_glue_catalog_database" "analytics" {
  name        = "analytics"
  description = "Production analytics metadata"
}
```

## Conceptual crawler

```hcl
resource "aws_glue_crawler" "orders" {
  name          = "orders-crawler"
  database_name = aws_glue_catalog_database.analytics.name
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://example-data/orders/"
  }

  schema_change_policy {
    update_behavior = "LOG"
    delete_behavior = "LOG"
  }
}
```

### Why `LOG` can be attractive for governed production tables

It reduces the crawler's authority to rewrite an established schema automatically.

That does not mean the source change disappears. It means the change becomes something the platform must investigate/control.

### IaC lifecycle

```text
Terraform
   ↓
Plan
   ↓
Review
   ↓
Apply
   ↓
Observe
   ↓
Version state
```

Do not blindly mix:

```text
Terraform-managed metadata
```

with:

```text
unreviewed manual catalog mutations
```

unless you have an explicit reconciliation strategy.

---

# 46. Production Design Patterns

## Pattern 1 — Crawler for Discovery

Use when:

- source structure is exploratory
- discovery is valuable
- schemas are not yet stabilized
- manual metadata is expensive

```text
S3
 ↓
Crawler
 ↓
Catalog
```

---

## Pattern 2 — Explicit Schema

Use when:

- production contract exists
- schema is stable
- governance matters
- consumer impact is high

```text
Schema definition
 ↓
Validation
 ↓
Catalog
```

---

## Pattern 3 — Hybrid

```text
Raw Zone
   ↓
Crawler
   ↓
Discovery
   ↓
Validation
   ↓
Controlled Silver/Gold Metadata
```

This is often an effective enterprise pattern.

---

## Pattern 4 — Iceberg Catalog

```text
S3
 ↓
Iceberg table
 ↓
Glue Catalog
 ↓
Athena / EMR / compatible engines
```

Use a table-aware writer/engine and supported catalog integration.

---

# 47. Crawler vs Explicit Catalog Management

| Requirement | Crawler | Explicit Management |
|---|---|---|
| Rapid discovery | Excellent | Moderate |
| Stable production schema | Conditional | Excellent |
| Strong schema governance | Needs controls | Excellent |
| Unpredictable files | Useful | Harder |
| Large-scale lake | Needs careful scoping | Often more deterministic |
| Deterministic deployments | Weak by default | Strong |
| Schema contracts | Needs guardrails | Strong |
| Operational simplicity | High initially | Higher engineering effort |
| Version-controlled metadata | Indirect | Excellent with IaC |
| Discovery of new partitions | Strong | Strong if pipeline-managed |

### Recommendation

Use a crawler when:

```text
Discovery value > inference risk
```

Use explicit management when:

```text
Governance + determinism + consumer criticality
>
discovery convenience
```

---

# 48. Schema Management Decision Framework

```text
Is the source schema stable?
        |
        +── YES
        |     ↓
        |  Explicit schema
        |
        +── NO
              ↓
        Need automated discovery?
              |
          +---+---+
          |       |
         YES      NO
          |       |
       Crawler   Contract /
                 validation
```

Then adjust for:

```text
ownership
governance
change frequency
source quality
scale
consumer criticality
```

### Better question

Do not ask:

> "Should we use Glue Crawlers?"

Ask:

> "What mechanism gives us the required discovery, determinism, governance and operating cost for this dataset?"

---

# 49. Common Beginner Mistakes

## Mistake 1 — Treating the Catalog as the database

Why:

```text
"table" sounds like stored data.
```

Correct:

```text
Glue table = metadata definition.
```

---

## Mistake 2 — Assuming the Catalog stores the records

Correct:

```text
S3 stores objects.
Glue stores metadata.
```

---

## Mistake 3 — Assuming crawler = ETL

A crawler discovers metadata.

It is not a replacement for a transformation pipeline.

---

## Mistake 4 — Assuming inference is always correct

Inference is evidence.

It is not business semantics.

---

## Mistake 5 — Crawling the entire bucket

Broad crawling increases:

- discovery scope
- runtime
- complexity
- potential schema collisions

---

## Mistake 6 — Running crawlers too frequently

New data arrival does not automatically imply that full discovery must run at the same frequency.

---

## Mistake 7 — Relying on crawlers for strict production contracts

Critical schemas should generally have explicit ownership and controlled change processes.

---

## Mistake 8 — Ignoring schema drift

A type change can break downstream consumers even when the files still look readable.

---

## Mistake 9 — Creating millions of partitions

Partitioning is an access optimization, not a requirement to encode every dimension into the path.

---

## Mistake 10 — Assuming MSCK solves every partition problem

It is one discovery mechanism, not a universal metadata architecture.

---

## Mistake 11 — Ignoring permissions

Metadata access and data access are separate concerns.

---

## Mistake 12 — Hardcoding credentials

Use:

```text
IAM roles
IAM Identity Center
temporary credentials
```

---

## Mistake 13 — Manual production changes without auditability

If someone manually changes a production schema, the platform may drift away from the intended configuration.

---

# 50. Cost Optimization

Conceptual cost drivers include:

```text
Crawler runtime
Crawler frequency
Large discovery targets
Repeated metadata operations
Partition explosion
Query scan volume
Operational overhead
```

A useful chain:

```text
Bad metadata design
      ↓
Bad partition design
      ↓
More data scanned / more metadata work
      ↓
Higher latency
      ↓
Potentially higher cost
```

Metadata is therefore part of cost architecture.

### Cost safety

For every lab:

```text
Resource created
 ↓
Potential cost
 ↓
Monitoring
 ↓
Cleanup
 ↓
Cleanup verification
```

Never assume a service or configuration is free.

Verify current AWS pricing before budgeting.

---

# 51. Security Best Practices

Production checklist:

```text
[ ] IAM least privilege
[ ] No long-lived credentials
[ ] S3 Block Public Access
[ ] Encryption enabled
[ ] KMS where required
[ ] Crawler role scoped to required resources
[ ] Catalog permissions scoped
[ ] Cross-account access reviewed
[ ] Audit logging enabled
[ ] Schema changes controlled
[ ] Production metadata changes tracked
[ ] Learning resources isolated from production
```

### Crawler role

A crawler needs enough permission to:

- inspect its target
- interact with the required catalog resources
- perform its configured function

Do not grant:

```text
AdministratorAccess
```

merely because it makes the lab easier.

---

# 52. Advanced Topics

## Core

- Glue Data Catalog fundamentals
- databases/tables/columns
- storage descriptors
- crawlers
- classifiers
- schema inference
- schema change controls
- partitions
- explicit metadata
- schema evolution/drift
- troubleshooting

## Advanced

- partition indexes
- catalog-as-code
- enterprise crawler strategy
- cross-account metadata architecture
- Iceberg catalog integration
- metadata ownership
- production change management
- metadata observability

## Awareness

- Glue Schema Registry
- catalog federation
- Lake Formation governance
- advanced statistics behavior
- DataZone
- advanced Athena projection behavior

---

# 53. Architecture Trade-Off Matrix

## 53.1 Metadata Creation

| Mechanism | Use case | Advantages | Disadvantages | Determinism |
|---|---|---|---|---|
| Crawler | Discovery | Automated | Inference risk | Medium/Low |
| Athena DDL | SQL-driven metadata | Simple | Manual/versioning burden | Medium |
| boto3 | Pipeline automation | Programmatic | Must build controls | High |
| Terraform | Platform infrastructure | Versioned/reproducible | More setup | Very High |
| Iceberg writer | Iceberg tables | Table-aware | Format/engine dependent | High |

---

## 53.2 Schema Management

| Strategy | Strength | Risk |
|---|---|---|
| Inference | Discovery | Incorrect inference |
| Explicit schema | Control | More maintenance |
| Data contract | Governance | Organizational overhead |
| Hybrid | Balanced | More moving parts |

---

## 53.3 Partition Management

| Strategy | Best use | Main trade-off |
|---|---|---|
| Crawler | Discovery | Runtime/inference |
| MSCK REPAIR | Simple Hive-style repair | Not ideal at extreme scale |
| Explicit registration | Pipeline-owned partitions | More engineering |
| Partition projection | Predictable partition domains | Engine-specific design |
| Partition index | Large partition metadata | Additional metadata/index management |

---

# 54. Interview Preparation

## Basic

1. What is AWS Glue Data Catalog?
2. What is a Glue database?
3. What is a Glue table?
4. What is a Glue crawler?
5. What is schema inference?
6. What is a partition?
7. Does Glue Data Catalog store the actual S3 records?
8. What is a storage descriptor?
9. Why do query engines need metadata?
10. What is schema drift?

## Intermediate

1. When would you use a crawler?
2. When would you avoid a crawler?
3. What is schema evolution?
4. How does Glue Catalog interact with S3?
5. What is MSCK REPAIR TABLE?
6. Why can excessive partition counts become a problem?
7. What is partition pruning?
8. What is a partition index?
9. What is explicit partition registration?
10. What is the difference between Data Catalog and Schema Registry?

## Advanced

1. Design a production Glue Catalog strategy for a 10-TB/day lake.
2. Would you use crawlers for every dataset?
3. How would you handle schema evolution?
4. How would you manage millions of partitions?
5. How would you troubleshoot a missing partition?
6. How would you integrate Iceberg with Glue Catalog?
7. How would you manage cross-account catalog access?
8. How would you prevent a crawler from changing a critical production schema?
9. When would you choose Terraform over crawler-managed metadata?
10. How would you design metadata ownership across data domains?

### Advanced-answer standard

Your answer should include:

```text
Requirements
Architecture
Trade-offs
Security
Cost
Operations
Failure modes
```

---

# 55. Practice Questions

## Basic

1. Explain the difference between S3 and Glue Data Catalog.
2. What is a Glue database?
3. What is a Glue table?
4. What is a partition?
5. What is a crawler?
6. What is a classifier?
7. What is schema inference?
8. What is a storage descriptor?
9. Why are table properties useful?
10. Why is metadata important?

## Intermediate

11. When should you use a crawler?
12. When should you avoid a crawler?
13. What is schema drift?
14. What is schema evolution?
15. What is partition pruning?
16. What does MSCK REPAIR TABLE do conceptually?
17. What problem do partition indexes solve?
18. What is explicit partition registration?
19. How does Glue Catalog support Iceberg?
20. What is the difference between a Data Catalog and Schema Registry?

## Advanced

21. A crawler infers `amount` as string. How do you investigate?
22. A new partition exists in S3 but is not queryable. Diagnose it.
23. A production crawler changed a table schema unexpectedly. What controls would you add?
24. A table has hundreds of thousands of partitions. What questions do you ask?
25. When is partition projection worth considering?
26. When is a partition index useful?
27. How do you make catalog metadata reproducible?
28. How do you design cross-account metadata access?
29. How do you control schema evolution?
30. How do you distinguish technical compatibility from semantic compatibility?

## Scenario

31. Design metadata for orders, customers and payments.
32. Design a crawler strategy for a raw zone.
33. Design explicit metadata for a silver zone.
34. Design a hybrid raw-to-silver approach.
35. Design an Iceberg catalog architecture.

## Troubleshooting

36. Catalog table exists but query fails.
37. Partition exists in S3 but not in catalog.
38. Crawler creates two unexpected tables.
39. Crawler changes a column type.
40. Query scans much more data than expected.

## Architecture

41. Design metadata for a multi-account data lake.
42. Design a 10-TB/day metadata strategy.
43. Design a schema-change approval workflow.
44. Design catalog-as-code.
45. Design a production partition strategy.

## Schema Design

46. Is adding a nullable column safe?
47. Why is renaming a field risky?
48. Why can an int-to-string change break consumers?
49. When should a new schema version be created?
50. How should producers communicate breaking changes?

## Production Operations

51. What should be monitored for crawlers?
52. What should be logged for metadata changes?
53. How should crawler schedules be selected?
54. How do you control metadata costs?
55. How do you roll back an unsafe schema change?

---

# 56. Cheat Sheets

## Glue Catalog

```text
Catalog
  ↓
Database
  ↓
Table
  ↓
Columns
  ↓
Partitions
  ↓
Properties
  ↓
Storage Descriptor
```

## Crawler

```text
Source
  ↓
Crawler
  ↓
Classifier
  ↓
Schema Inference
  ↓
Partition Discovery
  ↓
Catalog Update
```

## Schema

```text
Schema
  ↓
Evolution
  ↓
Compatibility
  ↓
Validation
  ↓
Consumer Impact
```

## Partition

```text
S3 Layout
  ↓
Partition Metadata
  ↓
Partition Pruning
  ↓
Query Performance
  ↓
Potential Query Cost
```

## Troubleshooting

```text
Symptom
  ↓
Source
  ↓
Catalog
  ↓
Schema
  ↓
Partitions
  ↓
Permissions
  ↓
Engine
  ↓
Root Cause
  ↓
Fix
  ↓
Verify
```

---

# 57. Final Mental Model

Remember:

```text
S3
=
Where data lives

Glue Data Catalog
=
What the data is

Crawler
=
Automated metadata discovery

Schema
=
Structure of the data

Schema Evolution
=
Controlled structural change

Schema Drift
=
Unexpected structural change

Partition
=
Organization of data for efficient access

Partition Metadata
=
Information that lets engines locate relevant data

Iceberg + Glue Catalog
=
Table format + catalog metadata
```

Full platform model:

```text
                    DATA PLATFORM

                         S3
                          |
                    Physical Data
                          |
                          v
                  Glue Data Catalog
                          |
                +---------+---------+
                |                   |
             Schema             Partitions
                |                   |
                +---------+---------+
                          |
                          v
                  Athena / Glue / EMR
```

The most important production principle is:

> **Do not optimize for automatic discovery alone. Optimize for trustworthy metadata.**

---

# 58. Final Knowledge Check

## 20 Concept Questions

1. Why does a data lake need a catalog?
2. What does a Glue database represent?
3. What does a Glue table represent?
4. Where does the physical data reside?
5. What is a storage descriptor?
6. Why are partitions metadata as well as physical layout?
7. What does a crawler do?
8. What does a classifier do?
9. Why is schema inference imperfect?
10. What is schema drift?
11. What is schema evolution?
12. Why is metadata ownership important?
13. How does catalog metadata help query engines?
14. What is an Iceberg catalog?
15. What is the difference between Data Catalog and Schema Registry?
16. Why should schemas be versioned?
17. Why can partition count become an operational problem?
18. What is partition pruning?
19. What does a partition index help with?
20. Why should metadata be treated as production infrastructure?

## 10 Schema Management Questions

1. Is adding a nullable field always safe?
2. Why is a type change risky?
3. Why is renaming a column potentially breaking?
4. What is the difference between evolution and drift?
5. When should inference be replaced by explicit schema?
6. What should happen when a crawler discovers a breaking change?
7. What is a data contract?
8. Who should own a production schema?
9. How should breaking changes be rolled out?
10. How would you roll back a bad schema change?

## 10 Partition Questions

1. What is a Hive-style partition?
2. Why partition by date?
3. Why is customer ID usually a poor partition key?
4. What is partition pruning?
5. What does MSCK REPAIR TABLE do?
6. What is explicit partition registration?
7. What problem do partition indexes solve?
8. What is partition projection?
9. What causes partition explosion?
10. How would you redesign a table with millions of partitions?

## 10 Troubleshooting Questions

1. A crawler succeeds but the schema is wrong. Diagnose it.
2. A partition exists in S3 but not the catalog. Diagnose it.
3. A table exists but queries fail. What layers do you inspect?
4. A crawler creates multiple tables unexpectedly. Why?
5. A producer changes a numeric field to string. What happens?
6. Query scan volume increases suddenly. What metadata/partition questions do you ask?
7. A crawler changes a production column type. How do you stop recurrence?
8. A cross-account consumer gets access denied. What do you inspect?
9. `GetPartitions` becomes slow. What scaling questions do you ask?
10. Metadata changes cannot be traced. What operational controls are missing?

## 5 Architecture Questions

1. Design a catalog for a multi-zone S3 lake.
2. Design a crawler strategy for raw data.
3. Design explicit schema management for silver data.
4. Design an Iceberg + Glue Catalog architecture.
5. Design metadata governance for multiple AWS accounts.

## 5 Production Decision Questions

1. Crawler or Terraform?
2. Inferred schema or explicit schema?
3. MSCK REPAIR or explicit partition registration?
4. Partition index or projection?
5. Automatic schema update or controlled approval?

For every answer, explain:

```text
Why
Trade-offs
Failure modes
Security
Cost
Operational ownership
```

---

# 59. Module Completion Checklist

## Glue Data Catalog

- [ ] I understand the Glue Data Catalog.
- [ ] I understand databases.
- [ ] I understand tables.
- [ ] I understand columns.
- [ ] I understand partitions.
- [ ] I understand table properties.
- [ ] I understand storage descriptors.
- [ ] I can create catalog metadata.
- [ ] I can inspect catalog metadata.
- [ ] I can explain catalog vs physical storage.

## Crawlers

- [ ] I understand crawlers.
- [ ] I understand crawler targets.
- [ ] I understand classifiers.
- [ ] I understand schema inference.
- [ ] I understand partition discovery.
- [ ] I understand crawler scheduling.
- [ ] I understand recrawl strategies.
- [ ] I understand schema-change policies.
- [ ] I know when not to use crawlers.
- [ ] I can troubleshoot crawler output.

## Schema Management

- [ ] I understand explicit schemas.
- [ ] I understand inferred schemas.
- [ ] I understand schema evolution.
- [ ] I understand schema drift.
- [ ] I understand compatibility.
- [ ] I understand data contracts.
- [ ] I understand producer ownership.
- [ ] I can design a controlled schema-change workflow.
- [ ] I can diagnose an incompatible type change.

## Partitions

- [ ] I understand Hive partitions.
- [ ] I understand partition registration.
- [ ] I understand MSCK REPAIR TABLE.
- [ ] I understand partition indexes.
- [ ] I understand partition projection awareness.
- [ ] I understand partition pruning.
- [ ] I understand partition explosion.
- [ ] I can diagnose partition problems.
- [ ] I can select a partition strategy.

## Iceberg

- [ ] I understand Glue as an Iceberg catalog.
- [ ] I understand table registration/discovery.
- [ ] I understand Iceberg metadata conceptually.
- [ ] I understand the distinction between Iceberg metadata and catalog metadata.
- [ ] I can compare general-purpose S3 + Glue Catalog with S3 Tables.

## Operations

- [ ] I can use AWS CLI for catalog inspection.
- [ ] I can use boto3 for catalog automation.
- [ ] I understand Terraform-based metadata infrastructure.
- [ ] I can troubleshoot permissions.
- [ ] I can reason about cost.
- [ ] I can reason about quotas.
- [ ] I can document a metadata incident.

---

# 60. Final Roadmap Coverage Audit

The authoritative Topic 03 requirements are checked below.

| Requirement | Covered? | Explanation | Example | Production context |
|---|---|---|---|---|
| Glue Data Catalog | Yes | Fundamentals + architecture | Catalog hierarchy | Yes |
| Databases | Yes | Namespace model | `analytics` | Yes |
| Tables | Yes | Logical metadata | `orders` | Yes |
| Partitions | Yes | Metadata + physical layout | `year/month/day` | Yes |
| Columns | Yes | Schema/type model | `order_id`, `amount` | Yes |
| Properties | Yes | Table parameters | classification/owner | Yes |
| Storage descriptors | Yes | Location/format/SerDe | Parquet table | Yes |
| Athena DDL | Yes | Table creation example | `CREATE EXTERNAL TABLE` | Yes |
| AWS CLI | Yes | Inspection/operations | `get-table`, crawler APIs | Yes |
| boto3 | Yes | CRUD/inspection/crawlers | `create_table`, `get_table` | Yes |
| Terraform | Yes | IaC examples | Glue DB/crawler | Yes |
| Iceberg writers | Yes | Table-aware metadata model | Iceberg integration | Yes |
| Crawlers | Yes | Purpose/workflow | S3 crawler | Yes |
| Classifiers | Yes | Built-in/custom model | JSON/CSV | Yes |
| Schema inference | Yes | Inference + risks | numeric/string example | Yes |
| Schema-change policies | Yes | `LOG`/update/delete concepts | CLI/config examples | Yes |
| Crawler schedules | Yes | Manual/scheduled/recrawl | scheduling strategy | Yes |
| Crawler limitations | Yes | inference/scope/cost | avoid production overreach | Yes |
| Partition management | Yes | discovery/registration | S3 paths | Yes |
| MSCK REPAIR TABLE | Yes | conceptual use/limits | SQL example | Yes |
| Partition indexes | Yes | scaling lookup | high partition counts | Yes |
| Partition projection | Yes | awareness | query-time derivation | Yes |
| Partition pruning | Yes | performance model | filtered date query | Yes |
| Iceberg catalog | Yes | Glue catalog model | S3 + Iceberg + Glue | Yes |
| Glue Schema Registry awareness | Yes | distinction | event schemas | Yes |
| Column statistics | Yes | purpose/API awareness | stats concepts | Yes |
| Permissions | Yes | IAM/S3/KMS/LF awareness | layered access | Yes |
| Cross-account access | Yes | architecture + controls | account A/B | Yes |
| Federation awareness | Yes | multi-catalog model | enterprise metadata | Yes |
| Quotas/limits | Yes | planning model | scale/headroom | Yes |
| Cost | Yes | crawler/partition/query drivers | cost loop | Yes |
| Production architecture | Yes | complete lake model | bronze/silver/gold | Yes |
| Hands-on labs | Yes | 9 labs | catalog/crawler/Iceberg | Yes |
| Troubleshooting | Yes | framework + incidents | six incidents | Yes |
| Common mistakes | Yes | production mistakes | crawler/partition/IAM | Yes |

**Roadmap coverage: COMPLETE**

---

# 61. Technical Accuracy Audit

The module was written to avoid fabricated AWS limits, prices, API names and undocumented guarantees.

Current AWS documentation was used to validate key areas:

- Data Catalog purpose and manual/crawler population. citeturn0search4turn0search18
- Crawler classification, grouping and catalog updates. citeturn0search6turn0search17
- Crawler schema-change policies. citeturn0search0turn0search1
- Preventing crawler schema changes and documented configuration examples. citeturn0search3
- Crawler recrawl/scheduling/configuration capabilities. citeturn0search5turn0search7
- boto3 `create_table` and `get_table`. citeturn0search8turn0search9
- AWS CLI `create-table`. citeturn0search13
- Glue partition indexes. citeturn0search2
- Glue crawler partition-index behavior. citeturn0search16
- Glue table/column statistics API surface. citeturn0search11

### Accuracy rules applied

- No hardcoded AWS pricing.
- No hardcoded quota numbers.
- No hardcoded secret credentials.
- Current API names were checked against AWS documentation.
- Version-sensitive Terraform syntax is explicitly marked for provider verification.
- Advanced service behavior is framed as awareness where the roadmap requires awareness only.
- MSCK REPAIR TABLE is not presented as a universal solution.
- Crawlers are not presented as schema governance.
- Glue Catalog is not presented as physical storage.
- Iceberg metadata and Glue Catalog metadata are distinguished.
- Exact production permissions are not fabricated.

**Technical accuracy audit: PASSED**

---

# 62. File-Scope Audit

This artifact is intended to modify/create only:

```text
03-AWS-Data-Engineering-Deep-Dive/03-glue-data-catalog-crawlers-and-schema-management.md
```

No project source files are required by this learning module.

**Other files modified: NONE**

**File-scope audit: PASSED**

---

# 63. Final Execution Summary

```text
Target file updated:
03-AWS-Data-Engineering-Deep-Dive/03-glue-data-catalog-crawlers-and-schema-management.md

Other files modified:
NONE

Roadmap coverage:
COMPLETE

Topic 03 audit:
PASSED

Technical accuracy audit:
PASSED

File-scope audit:
PASSED
```

---

# 64. Operating Standard

The final standard for this module is:

```text
Read
 ↓
Understand the metadata model
 ↓
Create
 ↓
Inspect
 ↓
Break
 ↓
Diagnose
 ↓
Fix
 ↓
Govern
 ↓
Automate
 ↓
Measure
 ↓
Document
```

The goal is not merely to know what a Glue Crawler is.

The goal is to be able to answer, in production:

> **Who owns this schema, where did this metadata come from, why did it change, which partitions are valid, which consumers depend on it, what will break if it changes, and how can we recover safely?**
