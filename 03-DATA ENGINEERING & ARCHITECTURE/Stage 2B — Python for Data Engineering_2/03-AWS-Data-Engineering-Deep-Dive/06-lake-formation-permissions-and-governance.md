# 06 — Lake Formation Permissions and Governance

> **Role:** Senior Data Engineer / AWS Data Platform Engineer  
> **Module:** G3 Topic 06 — Lake Formation Permissions and Governance  
> **Path:** `03-AWS-Data-Engineering-Deep-Dive/06-lake-formation-permissions-and-governance.md`  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary services:** AWS Lake Formation, AWS Glue Data Catalog, Amazon S3, Amazon Athena, AWS IAM, AWS KMS, AWS RAM  
> **Core loop:** Read → Draw authorization flow → Configure → Test → Break → Diagnose → Fix → Audit → Write runbook → Explain the trade-off

---

# 0. Module Contract

AWS Lake Formation is the governance and fine-grained authorization layer for an AWS data lake.

This module teaches you to move from:

```text
S3 bucket policies
+
IAM permissions
+
Glue Catalog metadata
```

to a controlled data-lake authorization model:

```text
Identity
   ↓
IAM authentication/API authorization
   ↓
Lake Formation permissions
   ↓
Catalog resource
   ↓
S3 data location
   ↓
Fine-grained data access
   ↓
Athena / Glue / Redshift integrations
```

The central production principle is:

> **IAM and Lake Formation are complementary authorization layers, not interchangeable systems.**

AWS documentation describes Lake Formation as providing central access controls for data-lake resources, while IAM controls access to the Lake Formation/Glue APIs and AWS resources. Requests generally need to satisfy the applicable IAM and Lake Formation checks. citeturn0search11turn0search12

---

# 1. Scope

## 1.1 Covered deeply

This module covers:

1. Lake Formation architecture
2. Data lake administrators and personas
3. IAM vs Lake Formation
4. Data locations
5. S3 registration
6. Lake Formation permissions
7. Glue Data Catalog databases and tables
8. `IAMAllowedPrincipals`
9. Hybrid access mode
10. Named-resource permissions
11. LF-Tag based access control
12. Database/table/column permissions
13. Data filters
14. Row-level security
15. Column-level security
16. Cell-level security concepts
17. `DATA_LOCATION_ACCESS`
18. `DESCRIBE`
19. `SELECT`
20. `INSERT`
21. `ALTER`
22. `DROP`
23. `CREATE_TABLE`
24. Grantable permissions
25. Permission inheritance and boundaries
26. Athena integration
27. Glue integration
28. KMS and encrypted S3 locations
29. Cross-account sharing
30. AWS RAM
31. Resource links
32. Cross-Region awareness
33. LF-Tags and governance taxonomy
34. Hybrid migration strategy
35. Governance operating model
36. Troubleshooting and break/fix
37. Security
38. Cost
39. Auditability
40. Production architecture
41. ADRs
42. Practice questions
43. Interview preparation
44. Final knowledge checks
45. Roadmap and technical-accuracy audits

## 1.2 Awareness rather than full courses

These are integrated but not taught as separate full modules:

- AWS Glue ETL
- Glue Crawlers
- Athena SQL internals
- Redshift internals
- S3 fundamentals
- KMS cryptography internals
- IAM identity federation
- AWS Organizations
- AWS RAM internals
- DataZone
- S3 Access Grants

Those services may appear because production governance requires understanding their boundaries.

---

# 2. Why Lake Formation Exists

A basic data lake can begin as:

```text
Users
  |
  v
IAM
  |
  v
S3
```

As the platform grows:

```text
100+ tables
10+ teams
multiple environments
PII
finance data
customer data
external consumers
cross-account analytics
```

IAM-only management becomes increasingly difficult to express at the data-object level.

You may need policies such as:

```text
Finance:
    full access to finance tables

Marketing:
    customer_id + country
    but not email or phone

Support:
    customer records
    only for their assigned region

Data Science:
    pseudonymized customer data

External Partner:
    selected columns
    selected rows
```

Lake Formation provides a data-lake permission model that can express these requirements at Data Catalog/database/table/column and filtered-data levels. citeturn0search11turn0search12

---

# 3. The Core Mental Model

Think of Lake Formation as a policy layer over the lake:

```text
                    DATA LAKE

                      S3
                       |
                 Data locations
                       |
                Lake Formation
                       |
              +--------+--------+
              |                 |
        Data Catalog        Permissions
              |                 |
        databases/tables    principals/tags
              |                 |
              +--------+--------+
                       |
                    Athena
                       |
                    Results
```

The catalog tells AWS:

```text
What is this data?
```

Lake Formation permissions answer:

```text
Who can do what with it?
```

S3/IAM answer:

```text
Can the identity/API request reach the underlying AWS resources?
```

---

# 4. Authentication vs Authorization

Do not confuse:

```text
Authentication
=
Who are you?
```

with:

```text
Authorization
=
What are you allowed to do?
```

IAM participates heavily in both identity and authorization.

Lake Formation primarily adds data-lake authorization semantics.

Example:

```text
IAM Role
    |
    +-- can call Athena
    +-- can call Lake Formation APIs
    +-- can call Glue APIs
    |
    v
Lake Formation
    |
    +-- SELECT on sales table
    +-- no SELECT on payroll
    +-- SELECT only rows matching region
    +-- SELECT only approved columns
```

---

# 5. Two Doors Mental Model

A useful production mental model is:

```text
                    REQUEST
                       |
              +--------+--------+
              |                 |
           IAM door        Lake Formation door
              |                 |
       API/resource auth    Data permissions
              |                 |
              +--------+--------+
                       |
                    SUCCESS
```

A principal may have:

```text
Lake Formation SELECT
```

but still fail because the identity lacks required IAM permissions.

Conversely, having broad IAM access does not automatically mean a Lake Formation-managed principal has every Lake Formation data permission.

AWS explicitly documents this two-layer model. citeturn0search12

---

# 6. Lake Formation Architecture

```text
                  IAM Identity
                       |
                       v
                AWS IAM Role/User
                       |
                       v
                Lake Formation
                       |
        +--------------+--------------+
        |              |              |
      Catalog       S3 locations     LF-Tags
        |              |              |
        v              v              v
   Database/Table    Data files     Governance
        |
        v
      Athena
        |
        v
      Query
```

Lake Formation does not replace S3.

It governs access to data that is represented in the lake architecture.

---

# 7. Data Lake Administrator

The data lake administrator is a high-privilege governance role.

Responsibilities commonly include:

- configuring Lake Formation
- assigning administrative responsibilities
- registering data locations
- managing governance settings
- configuring permissions
- onboarding data domains
- controlling migration from IAM to Lake Formation
- overseeing cross-account sharing

### Production principle

Do not use the data lake administrator role for ordinary analytics.

Use:

```text
Administrator role
    =
platform governance

Consumer role
    =
data access

Producer role
    =
data publishing
```

Separate responsibilities whenever practical.

---

# 8. Personas

A practical enterprise model:

```text
Platform Admin
    |
    +-- Lake Formation governance
    +-- IAM integration
    +-- KMS integration
    +-- registration
    +-- sharing

Data Producer
    |
    +-- create/publish datasets
    +-- schema management
    +-- quality

Data Steward
    |
    +-- ownership
    +-- classification
    +-- LF-Tags
    +-- access review

Data Consumer
    |
    +-- query approved data
```

This is a governance model, not a requirement that every organization create four separate IAM roles.

---

# 9. Data Lake Locations

A Lake Formation data location represents an Amazon S3 location under Lake Formation management.

Example:

```text
s3://company-data-lake/
```

or:

```text
s3://company-data-lake/finance/
```

When a location is registered, Lake Formation can manage permissions for Data Catalog resources that point to that location and the underlying data access. AWS notes that registering a parent path also registers folders beneath that path. citeturn0search1turn0search3

---

# 10. Location Registration Mental Model

```text
S3
 |
 +-- raw/
 |
 +-- curated/
 |     |
 |     +-- finance/
 |     +-- sales/
 |
 +-- sensitive/
       |
       +-- pii/
```

You might register:

```text
s3://company-data-lake/curated/
```

Then tables beneath it can participate in Lake Formation governance.

### Important

Registration is not merely metadata.

It changes the access-control architecture for the location.

---

# 11. Registering an S3 Location

Conceptually:

```text
Lake Formation
    |
    v
Register location
    |
    +-- S3 path
    +-- registration role
    +-- permission mode
```

AWS currently supports registering locations in:

```text
Lake Formation mode
```

or:

```text
Hybrid access mode
```

Hybrid access mode allows incremental onboarding of principals while existing IAM-based access can continue for non-opted-in principals. citeturn0search0turn0search1

---

# 12. Registration Role

Lake Formation needs an IAM role/service-linked role with appropriate permissions to access registered S3 locations.

The role is part of the data-location trust/control path.

### Production checklist

```text
[ ] correct S3 bucket
[ ] correct prefix
[ ] correct Region
[ ] correct IAM role
[ ] S3 permissions
[ ] KMS permissions if encrypted
[ ] no unintended broader access
[ ] ownership verified
```

Never blindly grant:

```text
s3:*
kms:*
```

across all resources.

---

# 13. Data Location Permission

A common permission is:

```text
DATA_LOCATION_ACCESS
```

This is not the same thing as:

```text
SELECT
```

Think:

```text
DATA_LOCATION_ACCESS
=
permission related to creating/cataloging resources that point to the location
```

while:

```text
SELECT
=
permission to read table data
```

AWS documentation specifically distinguishes data-location permissions from Data Catalog object permissions. citeturn0search5turn0search12

---

# 14. Data Catalog Resources

Lake Formation governs resources such as:

```text
Catalog
  |
  +-- Database
       |
       +-- Table
            |
            +-- Columns
```

You can also encounter:

```text
Views
Resource links
Shared resources
Federated resources
```

The exact supported permission combinations depend on resource type.

---

# 15. Database Permissions

Examples of database-level permissions include:

```text
DESCRIBE
CREATE_TABLE
ALTER
DROP
```

The exact permissions needed depend on the operation.

For example:

```text
Create a table
```

may require:

```text
IAM Glue API permission
+
Lake Formation CREATE_TABLE
+
DATA_LOCATION_ACCESS where applicable
```

The key lesson is:

> A single console checkbox can correspond to multiple underlying authorization requirements.

---

# 16. Table Permissions

Common table-level permissions include:

```text
SELECT
INSERT
DELETE
DESCRIBE
ALTER
DROP
```

The actual availability depends on resource and operation.

A useful mental model:

```text
Table
 |
 +-- Read
 |    └── SELECT
 |
 +-- Modify
 |    ├── INSERT
 |    ├── DELETE
 |    └── ALTER
 |
 +-- Metadata
      └── DESCRIBE
```

---

# 17. Column-Level Permissions

Suppose:

```text
customers
--------------------------------
customer_id
name
email
phone
country
income
```

You can design access such as:

```text
Marketing
    customer_id
    country

Support
    customer_id
    name
    country

Finance
    customer_id
    income

Restricted
    email
    phone
```

The goal is:

```text
least privilege
+
business need
```

rather than:

```text
give table access to everyone
```

---

# 18. Row-Level Security

Suppose a sales table contains:

```text
region
revenue
customer_id
```

Requirement:

```text
India team → India rows
US team → US rows
Global finance → all rows
```

Lake Formation data filters can express row restrictions.

Conceptually:

```text
Table
  |
  +-- Data Filter: region = 'IN'
  |
  +-- Data Filter: region = 'US'
  |
  +-- Global access
```

AWS documents Lake Formation filtering and fine-grained access for Athena and Redshift Spectrum. citeturn0search11

---

# 19. Column + Row Security

The most powerful use case is combining:

```text
rows
+
columns
```

Example:

```text
Marketing:
    rows: country = 'IN'
    columns:
        customer_id
        age_band
        country

Finance:
    rows: all
    columns:
        customer_id
        revenue
        margin

Support:
    rows: assigned_region
    columns:
        customer_id
        name
        ticket_status
```

This is closer to enterprise data-governance requirements than a simple table-level allow/deny model.

---

# 20. Cell-Level Security

Cell-level security means the access policy can restrict data at a finer grain than an entire table.

In practice, Lake Formation data filters can combine row predicates and included/excluded columns to provide fine-grained access patterns.

Example:

```text
Table:
customer_id
country
email
phone
revenue
```

Policy:

```text
country = 'IN'
AND
only customer_id, country, revenue
```

The consumer receives:

```text
selected rows
+
selected columns
```

rather than the full table.

---

# 21. Data Filters

A data filter conceptually contains:

```text
Table
+
Row filter expression
+
Column inclusion/exclusion
```

Example:

```text
Filter name:
india_marketing_filter

Row expression:
country = 'IN'

Columns:
customer_id
country
age_band
```

The filter becomes part of the authorization design.

---

# 22. Data Filter Design Rules

Good filters are:

- simple
- explainable
- testable
- aligned with business policy
- stable
- reviewed
- documented

Bad filters are:

- unnecessarily complex
- based on mutable operational assumptions
- undocumented
- copied across dozens of teams without ownership

---

# 23. Named-Resource Access

The classic Lake Formation approach is:

```text
Principal
   |
   v
Specific database/table
   |
   v
Permission
```

Example:

```text
role/marketing
    SELECT
        on
database/customer_analytics
table/customers
```

Advantages:

- explicit
- easy to reason about
- strong for small environments

Disadvantages:

- permission sprawl
- repetitive grants
- difficult to scale across hundreds of datasets

---

# 24. LF-Tags

LF-Tags provide a tag-based authorization model.

Instead of granting:

```text
role → table A
role → table B
role → table C
...
```

you can classify data:

```text
classification=confidential
domain=finance
pii=true
region=india
```

Then grant access based on those attributes.

AWS calls this LF-Tag based access control (LF-TBAC). citeturn0search17

---

# 25. LF-Tag Mental Model

```text
Data Catalog resource
        |
        +-- LF-Tag:
        |      domain = finance
        |
        +-- LF-Tag:
               sensitivity = confidential
```

Principal:

```text
finance-analyst-role
```

Permission policy:

```text
domain = finance
AND
sensitivity = confidential
```

This scales better than manually maintaining hundreds of table-specific grants when the taxonomy is well designed.

---

# 26. LF-Tag Taxonomy

A practical enterprise taxonomy may include:

```text
domain
    finance
    sales
    marketing
    operations

classification
    public
    internal
    confidential
    restricted

pii
    true
    false

environment
    dev
    test
    prod
```

Do not create dozens of tags merely because the service supports tags.

A tag should represent a stable governance concept.

---

# 27. Good vs Bad LF-Tags

### Good

```text
domain=finance
sensitivity=restricted
pii=true
```

These describe governance-relevant properties.

### Weak

```text
created_by=alice
project=temporary-demo
ticket=INC-19281
```

These are operational metadata, not necessarily durable authorization attributes.

---

# 28. LF-Tag Governance

For each LF-Tag:

```text
Name
Definition
Allowed values
Owner
Meaning
Who can assign
Who can modify
Review frequency
```

Example:

```text
Tag:
sensitivity

Values:
public
internal
confidential
restricted

Owner:
Data Governance Council

Assignment:
Data Steward

Review:
Quarterly
```

---

# 29. LF-Tags and Least Privilege

The goal is:

```text
Identity
   |
   v
Business role
   |
   v
Governance attributes
   |
   v
Allowed data
```

Avoid:

```text
Identity
   |
   v
Everything
```

LF-TBAC should reduce permission maintenance while preserving least privilege.

---

# 30. Multiple LF-Tag Grants

AWS documents that when a principal receives permissions through both LF-TBAC and named-resource grants, the effective permissions are the union of those grants. citeturn0search15

Therefore:

```text
Named grant:
SELECT table A

LF-Tag grant:
SELECT all finance tables
```

Effective access includes both.

### Production lesson

When debugging unexpected access:

```text
Check named grants
+
Check LF-Tag grants
+
Check inherited/shared permissions
```

Do not inspect only one authorization path.

---

# 31. IAMAllowedPrincipals

`IAMAllowedPrincipals` is a virtual group associated with Lake Formation's legacy IAM-compatible permission model.

A common legacy state is:

```text
IAMAllowedPrincipals
        |
        v
Super permissions
        |
        v
Catalog objects
```

This can make IAM-based access continue to work without requiring every principal to be explicitly opted into Lake Formation.

### Critical lesson

Do not remove or modify this group casually in production.

Understand the migration state first.

---

# 32. Why IAMAllowedPrincipals Matters

Suppose an existing environment uses:

```text
IAM
+
Glue
+
S3
```

and you suddenly enforce Lake Formation everywhere.

Existing workloads may fail.

Potentially affected:

- Athena
- Glue jobs
- ETL roles
- BI tools
- notebooks
- applications
- cross-account consumers

Therefore migration must be staged.

---

# 33. Hybrid Access Mode

Hybrid access mode supports two authorization paths for the same resources:

```text
Lake Formation permissions
        OR
IAM-based access
```

depending on whether a principal/resource is opted in.

AWS describes hybrid access mode as an incremental path for adopting Lake Formation without immediately interrupting existing IAM-based access. citeturn0search0turn0search13

---

# 34. Hybrid Access Mental Model

```text
                Registered S3 location
                         |
                  Hybrid access mode
                         |
              +----------+----------+
              |                     |
        Opted-in principal     Not opted-in
              |                     |
        Lake Formation          IAM/S3/Glue
        permissions             policies
```

This is extremely useful for migrations.

---

# 35. Hybrid Access Migration

Recommended pattern:

```text
Existing IAM system
       |
       v
Register S3 location in hybrid mode
       |
       v
Define Lake Formation permissions
       |
       v
Opt in one principal
       |
       v
Test
       |
       v
Observe
       |
       v
Expand
```

Do not migrate 500 production roles in one change.

---

# 36. Hybrid Migration Guardrail

Before opting in:

```text
Inventory:
    principals
    tables
    jobs
    queries
    S3 policies
    Glue policies
    KMS policies
```

Then:

```text
Select one low-risk principal
        ↓
Opt in
        ↓
Test Athena
        ↓
Test Glue
        ↓
Test downstream systems
        ↓
Review CloudTrail
        ↓
Expand
```

AWS specifically warns against changing a location to hybrid mode without correctly opting in the principals that rely on Lake Formation permissions. citeturn0search7

---

# 37. IAM vs Lake Formation

| Concern | IAM | Lake Formation |
|---|---|---|
| Identity | Yes | Uses IAM identities |
| AWS API access | Yes | Uses IAM integration |
| S3 bucket access | Yes | Governs data-lake access |
| Catalog permissions | Glue/IAM | Fine-grained catalog permissions |
| Table-level SELECT | Indirect | Native |
| Column-level access | Not native in the same model | Yes |
| Row filters | Not native in this data-lake model | Yes |
| LF-Tag governance | No | Yes |
| Cross-account data sharing | IAM/resource policies | Lake Formation + RAM |
| Governance taxonomy | Tags elsewhere | LF-Tags |

### Important

Lake Formation does not eliminate IAM.

---

# 38. S3 Policy vs Lake Formation

Suppose:

```text
IAM role
    Allow s3:GetObject
    on
s3://company-data/finance/*
```

This does not by itself express:

```text
SELECT only revenue
WHERE region = 'IN'
```

Lake Formation provides a data-centric authorization model above the storage layer.

---

# 39. KMS Integration

If the underlying S3 data uses SSE-KMS:

```text
Athena/Glue request
      |
      v
Lake Formation
      |
      v
S3
      |
      v
KMS
```

The relevant identities/roles also need the appropriate KMS permissions.

Typical permissions may involve:

```text
kms:Decrypt
kms:Encrypt
kms:GenerateDataKey
kms:DescribeKey
```

depending on the exact operation and encryption architecture.

Never grant KMS permissions more broadly than necessary.

---

# 40. Encryption Failure Pattern

### Symptom

Lake Formation permission appears correct, but Athena cannot read data.

### Investigation

```text
1. IAM
2. Lake Formation
3. S3 bucket policy
4. S3 object permissions
5. KMS key policy
6. KMS IAM permissions
7. Lake Formation registration role
8. Region/account boundaries
```

A data-access request can fail at any of these layers.

---

# 41. Athena Integration

Athena commonly consumes Lake Formation-governed tables.

Conceptually:

```text
User
 |
 v
Athena
 |
 v
Glue Catalog
 |
 v
Lake Formation authorization
 |
 v
S3 data
```

If a user has:

```text
SELECT
```

on an appropriately configured table/data filter, Athena can expose only the authorized data.

---

# 42. Athena Row/Column Security

Example:

```sql
SELECT *
FROM customers;
```

The SQL itself does not need to contain:

```sql
WHERE country = 'IN'
```

if the governance policy supplies the row filter.

The policy layer becomes:

```text
Query
+
identity
+
Lake Formation policy
=
authorized result
```

### Security advantage

The consumer cannot simply remove the governance filter from the SQL.

---

# 43. Glue Integration

Glue jobs can interact with Lake Formation-governed data.

Typical architecture:

```text
Glue Job Role
      |
      +-- IAM permissions
      |
      +-- Lake Formation permissions
      |
      v
Glue Catalog
      |
      v
S3
```

When a Glue workload fails after governance changes, inspect both IAM and Lake Formation permissions.

---

# 44. Data Producer vs Data Consumer

A production platform should distinguish:

### Producer

Needs permissions such as:

```text
CREATE_TABLE
ALTER
INSERT
DATA_LOCATION_ACCESS
```

### Consumer

Usually needs:

```text
DESCRIBE
SELECT
```

The exact set depends on workflow.

Avoid giving consumers:

```text
DROP
ALTER
CREATE_TABLE
```

unless their role genuinely requires it.

---

# 45. Permission Matrix

Example:

| Role | Database | Table | Data |
|---|---|---|---|
| Platform Admin | Admin | Admin | Admin |
| Producer | Create/Alter | Write | Write |
| Analyst | Describe | Select | Read |
| BI | Describe | Select | Filtered |
| External Partner | Describe | Select | Filtered |

This matrix should exist before production grants are implemented.

---

# 46. Permission Design Process

Use:

```text
Business requirement
       ↓
Data classification
       ↓
Dataset ownership
       ↓
Consumer role
       ↓
Required operation
       ↓
Rows
       ↓
Columns
       ↓
LF-Tags / named resource
       ↓
IAM prerequisites
       ↓
Test
       ↓
Audit
```

Never start with:

```text
Which IAM policy should I copy?
```

Start with:

```text
What data should this role be allowed to access?
```

---

# 47. Named Resources vs LF-TBAC

| Dimension | Named Resource | LF-TBAC |
|---|---|---|
| Explicit table grants | Excellent | Moderate |
| Large data estate | Poorer | Excellent |
| Initial learning curve | Low | Moderate |
| Taxonomy required | No | Yes |
| Governance maturity | Lower | Higher |
| Access consistency | Moderate | Strong |
| Permission sprawl | Higher | Lower |
| Best for | Small/simple estates | Enterprise estates |

---

# 48. Hybrid Governance Strategy

A mature organization may use:

```text
Named resource grants
+
LF-Tags
+
data filters
+
hybrid access
```

For example:

```text
Temporary exception
    → named grant

Enterprise classification
    → LF-Tag

Regional restriction
    → data filter

Migration phase
    → hybrid access
```

Use the simplest mechanism that accurately expresses the policy.

---

# 49. Cross-Account Data Sharing

A producer account may own:

```text
S3
+
Glue Catalog
+
Lake Formation
```

A consumer account may need:

```text
Athena
+
selected datasets
```

Architecture:

```text
Producer Account
    |
    | Lake Formation share
    v
AWS RAM
    |
    v
Consumer Account
    |
    v
Resource Link
    |
    v
Athena
```

AWS documents named-resource and LF-Tag based cross-account sharing, with AWS RAM facilitating resource sharing. citeturn0search2

---

# 50. Producer / Consumer Model

```text
             PRODUCER
                 |
          Lake Formation
                 |
          +------+------+
          |             |
        Table          Tags
          |             |
          +------+------+
                 |
             AWS RAM
                 |
                 v
             CONSUMER
                 |
           Resource Link
                 |
               Athena
```

---

# 51. Resource Links

A resource link is a Data Catalog object that points to a shared database/table.

Think:

```text
Producer table
     |
     v
Shared resource
     |
     v
Consumer resource link
     |
     v
Consumer query
```

Resource links are particularly useful for cross-account and cross-Region access patterns. AWS documents them as Data Catalog objects linking to shared databases/tables. citeturn0search9

---

# 52. Cross-Account Sharing Workflow

## Producer

```text
1. Classify data
2. Create/verify table
3. Define permission
4. Share database/table
5. Configure required cross-account settings
```

## Consumer

```text
1. Accept AWS RAM share
2. Create resource link
3. Grant local permissions
4. Test Athena
5. Verify row/column restrictions
```

AWS documents these producer/consumer steps and additional hybrid-mode requirements. citeturn0search8turn0search18

---

# 53. Cross-Account Security

Do not treat cross-account sharing as:

```text
share table
=
done
```

Validate:

```text
Producer IAM
Producer LF
Producer S3
Producer KMS
AWS RAM
Consumer LF
Consumer IAM
Consumer resource link
Consumer Athena
```

---

# 54. Cross-Region Awareness

Lake Formation supports cross-Region table access patterns using resource links and related Data Catalog capabilities.

A simplified model:

```text
Region A
Producer
   |
   v
Shared table
   |
   v
Region B
Consumer resource link
   |
   v
Athena
```

Current AWS documentation describes cross-Region access, LF-Tags, fine-grained permissions, and resource links. citeturn0search16

Treat cross-Region design as an architecture decision because it adds:

- latency
- governance complexity
- data residency considerations
- network/data-transfer implications
- operational complexity

---

# 55. Governance Taxonomy

A production data catalog should classify data.

Example:

```text
domain:
    finance
    sales
    hr
    marketing

sensitivity:
    public
    internal
    confidential
    restricted

pii:
    true
    false

criticality:
    low
    medium
    high

environment:
    dev
    test
    prod
```

Do not confuse taxonomy with authorization.

Taxonomy describes:

```text
What is the data?
```

Authorization determines:

```text
Who may access it?
```

LF-Tags can connect these two concepts.

---

# 56. Data Classification Workflow

```text
New dataset
    |
    v
Owner assigned
    |
    v
Schema reviewed
    |
    v
PII/sensitivity classified
    |
    v
LF-Tags assigned
    |
    v
Access policy defined
    |
    v
Consumers approved
    |
    v
Permissions granted
    |
    v
Audit
```

---

# 57. Governance Ownership

Every production dataset should have:

```text
Business owner
Technical owner
Data steward
Classification
Approved consumers
Retention policy
Quality expectations
Security classification
```

Lake Formation implements access control, but governance ownership remains an organizational responsibility.

---

# 58. Data Lake Zones

A practical structure:

```text
S3
 |
 +-- raw/
 |
 +-- standardized/
 |
 +-- curated/
 |
 +-- restricted/
 |
 +-- sandbox/
```

Lake Formation permissions can then reflect different governance requirements.

Example:

```text
raw:
    limited producer access

curated:
    broad analytics access

restricted:
    strict LF filters/tags

sandbox:
    controlled experimentation
```

---

# 59. Governance Anti-Pattern

Bad:

```text
Everything
   |
   v
One bucket
   |
   v
One IAM role
   |
   v
Everyone
```

Better:

```text
Data domains
   +
classification
   +
ownership
   +
LF-Tags
   +
fine-grained permissions
   +
auditing
```

---

# 60. Lake Formation + S3 Architecture

```text
                       AWS DATA LAKE

 IAM Identity
      |
      v
  IAM Role
      |
      v
Lake Formation
      |
 +----+----+----------------+
 |         |                |
Catalog   LF-Tags       Data Filters
 |         |                |
 +----+----+----------------+
      |
      v
     S3
      |
 +----+----+
 |         |
KMS      Objects
      |
      v
   Athena
```

---

# 61. Lake Formation + Athena Production Architecture

```text
                 Data Consumers
                       |
                       v
                    Athena
                       |
                +------+------+
                |             |
             Workgroup     Identity
                |             |
                +------+------+
                       |
                 Lake Formation
                       |
       +---------------+---------------+
       |               |               |
   Catalog         LF-Tags        Data Filters
       |                               |
       +---------------+---------------+
                       |
                      S3
                       |
                      KMS
```

---

# 62. Lake Formation + Glue ETL Architecture

```text
Source
  |
  v
S3
  |
  v
Glue Catalog
  |
  v
Lake Formation
  |
  v
Glue ETL
  |
  v
Curated S3
  |
  v
Lake Formation
  |
  v
Athena
```

The same data-governance model can span ingestion and consumption, but every execution role still needs the IAM permissions required by its AWS APIs.

---

# 63. Permission Propagation Mental Model

Avoid assuming:

```text
Database permission
=
automatic full access to every operation
```

Instead reason:

```text
Resource
+
Principal
+
Permission
+
Grantable?
+
Data location
+
IAM prerequisite
+
Lake Formation mode
=
Effective access
```

This mental model prevents many production authorization mistakes.

---

# 64. Grantable Permissions

Lake Formation can grant permissions with the ability to pass/grant them onward.

Conceptually:

```text
Admin
  |
  | SELECT + grant option
  v
Data Steward
  |
  | SELECT
  v
Analyst
```

Use grantable permissions sparingly.

They increase the delegation surface.

---

# 65. Permission Delegation Principle

Ask:

```text
Does this role need access?
```

then:

```text
Does this role need to grant access?
```

These are different questions.

Most consumers should receive:

```text
access
```

not:

```text
access + delegation authority
```

---

# 66. Break/Fix Lab 1 — IAM Works, Lake Formation Denies

### Scenario

Athena role has:

```text
s3:GetObject
glue:GetTable
```

but query fails with Lake Formation access denied.

### Investigation

```text
IAM
   ↓
Lake Formation table permissions
   ↓
Data filter
   ↓
Location registration
   ↓
Hybrid mode / opt-in state
```

### Lesson

S3 access alone does not describe fine-grained Lake Formation authorization.

---

# 67. Break/Fix Lab 2 — Lake Formation Grants SELECT, Query Still Fails

### Scenario

You grant:

```text
SELECT
```

but Athena cannot query.

### Check:

```text
1. IAM Athena permissions
2. Glue Catalog permissions
3. S3 access path
4. KMS
5. Lake Formation
6. workgroup
7. table location
```

### Lesson

Use the two-door model.

---

# 68. Break/Fix Lab 3 — Existing Users Lose Access

### Scenario

You register a location and remove broad IAM-compatible permissions.

Existing Glue/Athena users fail.

### Investigation

```text
Who was using IAM access?
Who was opted into Lake Formation?
What was the old IAM policy?
What is the new LF grant?
Is IAMAllowedPrincipals involved?
```

### Correct approach

Use staged migration/hybrid access where appropriate.

---

# 69. Break/Fix Lab 4 — Unexpected Access

### Scenario

A role can read a table that you thought was denied.

### Investigate:

```text
Named grants
+
LF-TBAC grants
+
data filters
+
shared resources
+
IAMAllowedPrincipals
+
hybrid mode
+
IAM/S3 access
```

Remember that multiple Lake Formation grants can combine; AWS documents the union behavior for named-resource and LF-TBAC grants. citeturn0search15

---

# 70. Break/Fix Lab 5 — Filter Does Not Return Expected Rows

### Scenario

Analyst receives no rows.

### Check:

```text
1. filter expression
2. column name
3. data type
4. NULL behavior
5. principal assignment
6. table association
7. Athena identity
8. current table data
```

Do not immediately broaden access.

---

# 71. Break/Fix Lab 6 — Cross-Account Share Invisible

### Check:

```text
Producer:
    share exists
    correct account
    correct resource
    required cross-account settings

Consumer:
    RAM invitation accepted
    resource visible
    resource link created
    permissions granted
```

AWS documents RAM invitation acceptance and resource-link creation in cross-account flows. citeturn0search8turn0search18

---

# 72. Break/Fix Lab 7 — KMS Denial

### Symptom

Lake Formation and Athena permissions look correct.

### Check:

```text
KMS key policy
IAM role KMS permissions
key Region
S3 encryption
registration role
cross-account KMS policy
```

### Lesson

Encryption is an additional authorization boundary.

---

# 73. Break/Fix Lab 8 — Hybrid Mode Migration Failure

### Symptom

Some users work; others fail.

### Investigate:

```text
Location:
    hybrid?

Principal:
    opted in?

Resource:
    opted in?

IAMAllowedPrincipals:
    present?

IAM policy:
    still present?

Lake Formation grant:
    correct?
```

The hybrid state is principal/resource specific. AWS documents that opted-in principals can be governed by Lake Formation while non-opted-in principals continue through IAM-based access. citeturn0search5

---

# 74. Lab 1 — Build a Minimal Governed Lake

## Objective

Create:

```text
S3
+
Glue Catalog
+
Lake Formation
+
Athena
```

### Dataset

```text
customers
orders
```

### Requirements

```text
Analyst:
    SELECT orders

Producer:
    INSERT orders

Admin:
    governance
```

### Evidence

Capture:

- permissions
- query results
- IAM role
- Lake Formation grants
- S3 path
- cleanup evidence

---

# 75. Lab 2 — Column-Level Security

Create:

```text
customers
customer_id
name
email
phone
country
```

Grant:

```text
Marketing:
    customer_id
    name
    country

Restricted:
    email
    phone
```

Test with Athena.

Document:

```text
Expected
Actual
Difference
```

---

# 76. Lab 3 — Row-Level Security

Create:

```text
sales
region
sales_amount
customer_id
```

Grant:

```text
India role:
    region = IN

US role:
    region = US

Finance:
    all
```

Test:

```sql
SELECT *
FROM sales;
```

Do not rely on users adding their own `WHERE` clause.

The governance policy should enforce the restriction.

---

# 77. Lab 4 — Combined Row + Column Security

Create:

```text
customer_id
country
email
phone
revenue
```

Marketing:

```text
country = IN
columns:
    customer_id
    country
    revenue
```

Test unauthorized columns and rows.

---

# 78. Lab 5 — LF-Tag Access Control

Create:

```text
domain=finance
domain=sales
sensitivity=internal
sensitivity=restricted
```

Assign tags to tables.

Grant a role access to:

```text
domain=finance
AND
sensitivity=internal
```

Add a new table with the same tags.

Verify the role can access it without a new table-specific grant.

This demonstrates the scalability advantage of LF-TBAC.

---

# 79. Lab 6 — Hybrid Access Migration

Start with:

```text
IAM-only access
```

Then:

```text
Register location in hybrid mode
        ↓
Create LF permissions
        ↓
Opt in one role
        ↓
Test
        ↓
Opt in second role
        ↓
Test
```

Document every permission change.

---

# 80. Lab 7 — Cross-Account Sharing

Use two AWS accounts if available.

Producer:

```text
table
+
LF grant
```

Consumer:

```text
accept RAM share
+
resource link
+
LF permission
```

Test Athena.

Document:

```text
producer
consumer
resource
permissions
identity
result
```

---

# 81. Lab 8 — KMS-Protected Lake

Create a small encrypted dataset.

Configure:

```text
S3 SSE-KMS
+
Lake Formation
+
Athena
```

Intentionally remove KMS permission.

Observe failure.

Restore permission.

Document the authorization path.

---

# 82. Lab 9 — Governance Incident

Simulate:

```text
Analyst suddenly sees PII
```

Investigate:

```text
LF-Tags
named grants
data filters
IAMAllowedPrincipals
IAM
cross-account grants
```

Write an incident report:

```text
Root cause
Blast radius
Immediate containment
Corrective action
Preventive control
```

---

# 83. Lab 10 — Enterprise Data Domain

Build:

```text
finance
sales
marketing
```

Tag:

```text
domain
sensitivity
pii
```

Create roles:

```text
finance-analyst
sales-analyst
marketing-analyst
platform-admin
```

Apply LF-TBAC.

Add one row-level restriction.

Add one column restriction.

---

# 84. Lab 11 — Permission Audit

For every role:

```text
Role
↓
Database grants
↓
Table grants
↓
LF-Tag grants
↓
Data filters
↓
IAM
↓
S3
↓
KMS
```

Produce an access matrix.

Identify:

```text
excess permissions
unused permissions
unexpected permissions
delegation rights
```

---

# 85. Lab 12 — Production Migration Plan

Write a migration plan from:

```text
IAM/S3/Glue
```

to:

```text
Lake Formation
```

Include:

1. inventory
2. classification
3. tagging
4. permission mapping
5. hybrid registration
6. pilot principal
7. test
8. monitoring
9. staged rollout
10. rollback
11. post-migration audit

---

# 86. Production Governance Architecture

```text
                    GOVERNANCE PLANE

                    Data Governance
                          |
          +---------------+---------------+
          |               |               |
      Taxonomy         Ownership       Policies
          |               |               |
          +---------------+---------------+
                          |
                     Lake Formation
                          |
        +-----------------+-----------------+
        |                 |                 |
      LF-Tags        Named Grants       Data Filters
        |                 |                 |
        +-----------------+-----------------+
                          |
                    Glue Data Catalog
                          |
                          v
                           S3
                          |
                         KMS
                          |
              +-----------+-----------+
              |                       |
            Athena                  Glue
```

---

# 87. Production Permission Architecture

```text
                   Principal
                       |
                       v
                      IAM
                       |
                       v
               Lake Formation
                       |
          +------------+------------+
          |            |            |
       Database      Table       Filter
          |            |            |
          +------------+------------+
                       |
                    S3 Data
```

---

# 88. Domain-Oriented Governance

A mature data lake should map:

```text
Business domain
      |
      v
Data owner
      |
      v
Data products/tables
      |
      v
Classification
      |
      v
LF-Tags
      |
      v
Access policies
```

Example:

```text
Finance
  |
  +-- revenue
  +-- invoices
  +-- budgets
```

The governance model should follow business ownership rather than only technical bucket structure.

---

# 89. Data Product Governance

For every production data product:

```text
Name
Owner
Domain
Description
Schema
Classification
PII status
S3 location
Catalog database
LF-Tags
Approved consumers
Retention
Quality SLA
Access review date
```

This creates a repeatable operating model.

---

# 90. Access Review Process

At least periodically:

```text
List principals
    ↓
List permissions
    ↓
Compare to role/business need
    ↓
Remove stale access
    ↓
Review grantable permissions
    ↓
Review external accounts
    ↓
Review PII access
    ↓
Record evidence
```

Do not treat access review as a one-time migration task.

---

# 91. Auditability

Keep evidence for:

- who granted access
- what was granted
- when
- to whom
- which resource
- which LF-Tag
- which data filter
- which AWS account
- which KMS key
- whether the permission was later revoked

Use AWS audit/logging capabilities such as CloudTrail as part of the wider control plane.

---

# 92. Governance Metrics

Useful platform metrics:

```text
% datasets classified
% datasets with owners
% datasets with LF-Tags
% PII datasets reviewed
% access requests approved within SLA
% stale grants removed
% external shares reviewed
% workloads migrated to Lake Formation
% policy incidents
```

Governance should be measurable.

---

# 93. Security Incident: PII Exposure

Scenario:

```text
Marketing role
     |
     v
Athena
     |
     v
customers
     |
     v
email/phone visible
```

Immediate actions:

```text
1. Identify principal.
2. Identify permission path.
3. Revoke excessive access.
4. Confirm downstream exposure.
5. Preserve audit evidence.
6. Fix grant/filter/tag.
7. Re-test.
8. Review similar roles.
```

Do not only patch the single table if the underlying LF-Tag policy is wrong.

---

# 94. Security Incident: Cross-Account Overexposure

Scenario:

```text
Partner account
     |
     v
Shared table
     |
     v
PII
```

Investigate:

```text
Producer LF grant
Consumer grant
Resource link
LF-Tags
Data filters
IAM
S3
KMS
RAM
```

Contain the share first.

Then perform root-cause analysis.

---

# 95. Security Incident: IAMAllowedPrincipals

Scenario:

```text
Sensitive table
+
IAMAllowedPrincipals = broad access
```

Do not immediately remove it in production.

First:

```text
Inventory consumers
Map IAM access
Create LF grants
Pilot hybrid mode
Test
Migrate
Then tighten legacy permissions
```

---

# 96. Cost Considerations

Lake Formation itself is primarily a governance/control layer, but governance architecture can influence cost indirectly through:

- duplicated data
- cross-account data movement
- cross-Region designs
- repeated queries
- unnecessary copies
- ETL changes
- operational overhead

The goal is:

```text
strong governance
without
unnecessary data duplication
```

---

# 97. Governance vs Performance

Fine-grained governance can affect query behavior and operational complexity.

Always test:

```text
unrestricted baseline
vs
governed workload
```

Measure:

- latency
- failures
- query behavior
- operational complexity
- user experience

Do not remove security controls solely because a workload becomes inconvenient.

Optimize the architecture instead.

---

# 98. Lake Formation + Athena Workgroups

Use both:

```text
Lake Formation
=
data authorization

Athena Workgroup
=
query/workload governance
```

Example:

```text
Finance role
   |
   +-- Lake Formation:
   |      finance data only
   |
   +-- Athena:
          finance-prod workgroup
          encrypted results
          scan controls
```

These controls solve different problems.

---

# 99. Lake Formation + Lakehouse

A production lakehouse can combine:

```text
S3
+
Iceberg
+
Glue Catalog
+
Lake Formation
+
Athena
```

Architecture:

```text
               S3
                |
             Iceberg
                |
          Glue Catalog
                |
         Lake Formation
                |
              Athena
                |
             Consumers
```

This is one of the most important patterns in the G3 AWS track.

---

# 100. Lake Formation + Iceberg

Governance requirements:

```text
Table
 |
 +-- domain
 +-- sensitivity
 +-- PII
 +-- owner
 |
 v
LF-Tags
 |
 v
Access
```

Iceberg requirements:

```text
Table
 |
 +-- snapshots
 +-- manifests
 +-- data files
```

These solve different concerns:

```text
Iceberg
=
table management

Lake Formation
=
data access governance
```

---

# 101. Governance for Raw vs Curated Data

A useful policy:

```text
Raw
    restricted
    producers/platform

Standardized
    controlled engineering access

Curated
    broader analytical access

Restricted
    strict filters/tags
```

Do not expose raw sensitive data merely because it is convenient for analysts.

---

# 102. Governance Maturity Model

## Level 0 — Unmanaged

```text
S3
+
manual IAM
```

## Level 1 — Cataloged

```text
S3
+
Glue Catalog
```

## Level 2 — Centralized permissions

```text
Lake Formation
+
named grants
```

## Level 3 — Attribute-based governance

```text
LF-Tags
+
classification
```

## Level 4 — Fine-grained

```text
row
+
column
+
cross-account
```

## Level 5 — Operating model

```text
policy
+
ownership
+
audit
+
access review
+
automation
+
incident response
```

Target:

```text
Level 4–5
```

for a mature enterprise data platform.

---

# 103. ADR 1 — IAM Only vs Lake Formation

## Decision

Use Lake Formation when:

- multiple data domains exist
- fine-grained access is required
- cross-account data sharing is required
- centralized governance is required
- row/column restrictions are needed

Keep IAM/S3 controls as foundational security layers.

---

# 104. ADR 2 — Named Resources vs LF-TBAC

## Decision

Use named resources for:

- small/simple exceptions
- temporary access
- highly explicit grants

Use LF-TBAC for:

- large catalogs
- stable data classification
- domain-driven governance
- repeatable access patterns

Use both when justified.

---

# 105. ADR 3 — Full Lake Formation Mode vs Hybrid

## Full Lake Formation

Choose when:

- the platform is already governed
- migration is complete
- all relevant consumers are understood
- centralized enforcement is desired

## Hybrid

Choose when:

- migrating existing IAM-based workloads
- multiple consumers cannot migrate simultaneously
- gradual adoption is required

AWS explicitly positions hybrid access mode as an incremental migration path. citeturn0search0turn0search6

---

# 106. ADR 4 — Row Filter vs Separate Table

Use a row filter when:

```text
same logical dataset
+
different authorized subsets
```

Use separate physical/curated datasets when:

```text
different data products
+
different ownership
+
different lifecycle
+
different security boundary
```

Do not create thousands of security-filtered tables merely to avoid thinking about governance.

---

# 107. ADR 5 — LF-Tag vs IAM Tag

Use LF-Tags for:

```text
Lake Formation data governance
```

Use IAM resource tags for:

```text
AWS resource authorization / infrastructure governance
```

They are not interchangeable.

---

# 108. ADR 6 — Centralized vs Domain Governance

### Centralized

```text
One platform team
    |
    v
All grants
```

Advantages:

- consistency
- centralized control

Risks:

- bottleneck
- poor business context

### Federated

```text
Central platform
      +
Domain stewards
```

Advantages:

- domain expertise
- scalable ownership

Risks:

- taxonomy drift
- inconsistent policies

### Recommended

Use centralized guardrails with delegated domain stewardship.

---

# 109. Decision Matrix — Governance

| Requirement | IAM/S3 | Lake Formation |
|---|---:|---:|
| AWS API authorization | Excellent | Not replacement |
| Basic bucket access | Excellent | Integrated |
| Table SELECT | Weak | Excellent |
| Column security | Weak | Excellent |
| Row filters | Weak | Excellent |
| LF-Tag governance | No | Excellent |
| Cross-account data sharing | Possible | Excellent |
| Migration support | IAM native | Hybrid |
| Central data governance | Limited | Strong |

---

# 110. Decision Matrix — Access Strategy

| Scenario | Recommended |
|---|---|
| Small internal dataset | Named resource |
| Enterprise data estate | LF-TBAC |
| Temporary exception | Named resource |
| PII dataset | LF-Tags + fine-grained policy |
| Regional access | Data filter |
| Cross-account share | Lake Formation + RAM |
| IAM migration | Hybrid |
| Highly sensitive data | Fine-grained + strong IAM/KMS |

---

# 111. Decision Matrix — Permission Types

| Need | Permission / mechanism |
|---|---|
| Read table | SELECT |
| See metadata | DESCRIBE |
| Create table | CREATE_TABLE |
| Modify table definition | ALTER |
| Delete table | DROP |
| Write rows | INSERT |
| Delete rows | DELETE |
| Use S3 location for catalog creation | DATA_LOCATION_ACCESS |
| Attribute-based governance | LF-TBAC |
| Row/column restriction | Data filter |
| Cross-account share | LF + RAM |
| Delegation | Grantable permission |

---

# 112. Common Beginner Mistakes

## Mistake 1 — Thinking Lake Formation replaces IAM

It does not.

Correct model:

```text
IAM
+
Lake Formation
```

---

## Mistake 2 — Granting S3 access and assuming SELECT exists

S3 access is not equivalent to Lake Formation table authorization.

---

## Mistake 3 — Removing IAMAllowedPrincipals immediately

This can break existing workloads.

Use migration planning.

---

## Mistake 4 — Treating LF-Tags as ordinary AWS resource tags

They are a Lake Formation governance mechanism.

---

## Mistake 5 — Giving `Super` to everyone

Use least privilege.

---

## Mistake 6 — Giving grantable permissions unnecessarily

Access and delegation are different privileges.

---

## Mistake 7 — Ignoring KMS

Encrypted data introduces another authorization boundary.

---

## Mistake 8 — Creating filters without testing NULLs

Filter semantics matter.

---

## Mistake 9 — Using row filters as an excuse for poor data modeling

Security policy and data architecture are related but distinct.

---

## Mistake 10 — Ignoring cross-account complexity

Sharing involves:

```text
producer
+
RAM
+
consumer
+
resource link
+
permissions
```

---

## Mistake 11 — Mixing up database and table permissions

Always identify the exact resource and operation.

---

## Mistake 12 — Assuming a permission grant is enough

Verify:

```text
IAM
+
LF
+
S3
+
KMS
```

---

## Mistake 13 — No ownership for LF-Tags

Unowned governance metadata becomes unreliable.

---

## Mistake 14 — No access-review process

Permissions accumulate.

---

# 113. Production Checklist — New Dataset

```text
[ ] Business owner assigned
[ ] Technical owner assigned
[ ] S3 location defined
[ ] Data location registered
[ ] Encryption verified
[ ] Glue Catalog database selected
[ ] Table registered
[ ] Classification assigned
[ ] LF-Tags assigned
[ ] PII identified
[ ] Consumer roles identified
[ ] Named/LF-TBAC strategy chosen
[ ] Row filters defined where required
[ ] Column filters defined where required
[ ] Athena tested
[ ] Glue tested
[ ] Cross-account sharing reviewed
[ ] Audit logging verified
[ ] Access review date defined
```

---

# 114. Production Checklist — New Consumer

```text
[ ] Business justification
[ ] Role identified
[ ] Dataset identified
[ ] Required columns identified
[ ] Required rows identified
[ ] Named vs LF-Tag strategy selected
[ ] IAM prerequisites verified
[ ] Lake Formation grant applied
[ ] Data filter applied
[ ] KMS access verified
[ ] Athena query tested
[ ] Excess permissions tested
[ ] Access owner recorded
[ ] Review date recorded
```

---

# 115. Production Checklist — Cross-Account

```text
[ ] Producer identified
[ ] Consumer identified
[ ] Dataset classified
[ ] Sharing approval recorded
[ ] Lake Formation share configured
[ ] Cross-account version verified
[ ] AWS RAM share verified
[ ] Consumer accepted invitation
[ ] Resource link created
[ ] Consumer LF permissions granted
[ ] Consumer IAM verified
[ ] KMS verified
[ ] Athena query tested
[ ] Row/column restrictions tested
[ ] Revocation procedure documented
```

---

# 116. Production Checklist — Hybrid Migration

```text
[ ] Existing IAM consumers inventoried
[ ] S3 policies inventoried
[ ] Glue policies inventoried
[ ] KMS policies inventoried
[ ] Lake Formation grants designed
[ ] Location registered in hybrid mode
[ ] Pilot principal selected
[ ] Pilot opted in
[ ] Athena tested
[ ] Glue tested
[ ] Logs reviewed
[ ] Rollback defined
[ ] Additional principals migrated
[ ] Legacy permissions reduced carefully
[ ] Final access audit completed
```

---

# 117. Troubleshooting Decision Tree

```text
Access denied
    |
    v
Which layer failed?
    |
    +-- IAM?
    |     |
    |     +-- API permission?
    |     +-- role trust?
    |
    +-- Lake Formation?
    |     |
    |     +-- table grant?
    |     +-- filter?
    |     +-- LF-Tag?
    |     +-- opt-in?
    |
    +-- S3?
    |     |
    |     +-- bucket policy?
    |     +-- object access?
    |
    +-- KMS?
    |     |
    |     +-- key policy?
    |     +-- decrypt permission?
    |
    +-- Cross-account?
          |
          +-- RAM?
          +-- resource link?
          +-- consumer grant?
```

---

# 118. Authorization Debugging Method

Never make five permission changes at once.

Use:

```text
Observe
  ↓
Hypothesis
  ↓
One change
  ↓
Test
  ↓
Observe
```

Example:

```text
Hypothesis:
Missing Lake Formation SELECT

Change:
Grant SELECT

Test:
Athena query

Result:
Still denied

Next:
Check IAM/S3/KMS
```

This creates an audit trail and reduces accidental over-permissioning.

---

# 119. Production Runbook — Athena Access Denied

## Symptoms

```text
AccessDeniedException
```

## Procedure

1. Capture principal ARN.
2. Capture Athena query ID.
3. Identify database/table.
4. Identify S3 location.
5. Check Lake Formation grants.
6. Check LF-Tags.
7. Check data filter.
8. Check hybrid opt-in state.
9. Check IAM.
10. Check S3.
11. Check KMS.
12. Check cross-account configuration.
13. Reproduce with a minimal query.
14. Fix the narrowest failing layer.
15. Re-test.
16. Record the incident.

---

# 120. Production Runbook — Unexpected PII Access

1. Identify principal.
2. Disable/revoke excessive permission if necessary.
3. Determine whether access came from:
   - named grant
   - LF-TBAC
   - data filter
   - IAMAllowedPrincipals
   - IAM/S3
   - cross-account share
4. Identify all similarly governed tables.
5. Correct policy.
6. Validate with negative tests.
7. Review CloudTrail/audit evidence.
8. Document root cause.
9. Add preventive control.

---

# 121. Production Runbook — Cross-Account Access Failure

```text
Producer
  |
  +-- share exists?
  +-- correct resource?
  +-- permissions?
  |
  v
AWS RAM
  |
  +-- invitation?
  |
  v
Consumer
  |
  +-- resource link?
  +-- LF permission?
  +-- IAM?
  +-- KMS?
  |
  v
Athena
```

---

# 122. Negative Testing

Security testing must prove both:

```text
Allowed access works
```

and:

```text
Denied access fails
```

Example:

```text
Marketing
    SHOULD see:
        customer_id
        country

    SHOULD NOT see:
        email
        phone
```

Do not consider a governance implementation complete until negative tests pass.

---

# 123. Permission Test Matrix

| Principal | Dataset | Expected | Actual | Status |
|---|---|---|---|---|
| finance | finance | full | | |
| finance | marketing | denied | | |
| marketing | customers | filtered | | |
| support | customers | filtered | | |
| partner | shared_sales | filtered | | |

Store this as test evidence.

---

# 124. Governance CI/CD Concept

For mature platforms, permission definitions should be treated as code.

Conceptual repository:

```text
lake-governance/
├── tags/
├── databases/
├── tables/
├── filters/
├── grants/
├── accounts/
├── tests/
└── docs/
```

Use:

```text
Terraform/OpenTofu
+
AWS CLI
+
boto3
+
automated tests
```

where supported.

Do not rely solely on console clicks for production governance.

---

# 125. Infrastructure-as-Code Principle

A production policy should be reproducible.

Instead of:

```text
Engineer clicks console
```

prefer:

```text
Git
 ↓
Review
 ↓
Plan
 ↓
Apply
 ↓
Test
 ↓
Audit
```

Store:

- permission intent
- tag taxonomy
- data filters
- resource identifiers
- environment differences

Never store secrets.

---

# 126. Governance as Code

Example conceptual Terraform structure:

```hcl
module "finance_governance" {
  source = "./modules/lake-governance"

  domain = "finance"

  classification = "confidential"

  consumers = [
    "finance-analyst",
    "finance-bi"
  ]
}
```

Exact Terraform resource support and provider behavior must be verified against the current AWS provider version before implementation.

---

# 127. AWS CLI Awareness

Lake Formation exposes APIs through the AWS CLI.

Example conceptual command:

```bash
aws lakeformation list-permissions
```

Use CLI for:

- reproducible inspection
- scripting
- automation
- incident response
- evidence collection

Always verify command syntax against the installed AWS CLI version.

---

# 128. boto3 Awareness

Python automation can use:

```python
import boto3

lakeformation = boto3.client("lakeformation")

response = lakeformation.list_permissions()
```

Possible automation:

```text
list permissions
↓
detect stale grants
↓
compare to policy
↓
generate report
```

Do not automatically revoke permissions in production without an approval workflow.

---

# 129. Governance Drift Detection

Drift can occur when:

```text
manual console change
+
IaC
```

diverge.

Detect:

```text
Expected
    vs
Actual
```

for:

- grants
- LF-Tags
- filters
- data locations
- resource links
- cross-account shares

---

# 130. Governance Drift Runbook

```text
Detect drift
    |
    v
Classify:
    approved?
    unauthorized?
    emergency?
    |
    v
If unauthorized:
    contain
    |
    v
Restore expected state
    |
    v
Record incident
```

---

# 131. Practice Questions — Basic

1. What is AWS Lake Formation?
2. What problem does Lake Formation solve?
3. How is Lake Formation different from IAM?
4. What is a data lake location?
5. What is a Data Catalog database?
6. What is a Data Catalog table?
7. What is `SELECT`?
8. What is `DESCRIBE`?
9. What is `DATA_LOCATION_ACCESS`?
10. What is an LF-Tag?

---

# 132. Practice Questions — Moderate

11. Explain the two-door IAM/Lake Formation model.
12. Why does S3 access not automatically express row-level security?
13. What is `IAMAllowedPrincipals`?
14. Why is hybrid access useful?
15. What is named-resource access?
16. What is LF-TBAC?
17. What is a data filter?
18. How does column-level security work conceptually?
19. How does row-level security work conceptually?
20. What is a resource link?

---

# 133. Practice Questions — Hard

21. Design an India-only sales policy.
22. Design marketing access without PII.
23. Explain unexpected access when both named and LF-Tag grants exist.
24. Design an IAM-to-Lake-Formation migration.
25. Diagnose Athena access denied.
26. Diagnose KMS access denied.
27. Design cross-account data sharing.
28. Explain why removing `IAMAllowedPrincipals` can break workloads.
29. Design a governance taxonomy.
30. Compare named resources and LF-TBAC.

---

# 134. Practice Questions — Advanced

31. Design governance for 5,000 tables.
32. Design a multi-account data mesh with Lake Formation.
33. Design cross-Region governance.
34. Design LF-Tags for PII and domain ownership.
35. Design a hybrid migration for 500 IAM roles.
36. Design row + column security for external partners.
37. Design governance as code.
38. Design permission drift detection.
39. Design a PII exposure incident response.
40. Design a data-access review program.

---

# 135. Interview Questions — Fundamentals

## What is Lake Formation?

Strong answer:

```text
A managed AWS data-lake governance and fine-grained authorization layer that integrates with Glue Data Catalog, S3 and analytical consumers such as Athena.
```

Then explain:

```text
IAM
+
Lake Formation
```

rather than claiming Lake Formation replaces IAM.

---

# 136. Interview — IAM vs Lake Formation

A strong answer:

> IAM controls identity and AWS API/resource authorization. Lake Formation adds data-lake-specific permissions for catalog resources, locations and fine-grained data access. A production request may need to satisfy both layers.

AWS explicitly documents this complementary model. citeturn0search12

---

# 137. Interview — IAMAllowedPrincipals

Expected answer:

```text
It represents the legacy IAM-compatible permission path in Lake Formation-managed catalog resources. It can allow broad IAM-based access and therefore must be understood before tightening Lake Formation controls.
```

The important operational point:

```text
Do not remove it blindly.
```

---

# 138. Interview — Hybrid Access

Strong answer:

```text
Hybrid access lets an organization incrementally adopt Lake Formation permissions while existing IAM-based access can continue for principals/resources that have not been opted in.
```

Then discuss:

```text
registration
+
opt-in
+
testing
+
staged migration
```

---

# 139. Interview — LF-TBAC

Strong answer:

```text
LF-TBAC is attribute-based access control using Lake Formation tags. Instead of maintaining grants against every table individually, access can be granted based on governance attributes assigned to databases, tables or columns.
```

Then discuss:

```text
taxonomy
+
ownership
+
tag governance
+
least privilege
```

---

# 140. Interview — Row + Column Security

Strong answer:

```text
Use Lake Formation data filters to combine row predicates with column restrictions, so different principals can query the same logical table while receiving only authorized rows and columns.
```

Then mention:

```text
negative testing
+
filter correctness
+
NULL behavior
+
business policy
```

---

# 141. Interview — Cross-Account

Strong answer:

```text
Producer grants Lake Formation access, AWS RAM facilitates resource sharing, consumer accepts the share and creates a resource link, then consumer-side permissions are applied and Athena is tested.
```

Also discuss:

```text
IAM
+
KMS
+
cross-account settings
+
resource link
+
revocation
```

---

# 142. Interview — Permission Debugging

Strong answer:

```text
I identify the exact principal and resource, then check IAM, Lake Formation grants, LF-Tags, data filters, hybrid opt-in, S3, KMS and cross-account state in that order.
```

The key is:

```text
do not grant more access until the failing authorization layer is identified.
```

---

# 143. Interview — Governance at Scale

A senior answer should include:

```text
central taxonomy
+
domain ownership
+
LF-TBAC
+
exceptions via named grants
+
fine-grained filters
+
IaC
+
automated tests
+
drift detection
+
access reviews
+
audit logging
```

---

# 144. Interview — Data Mesh

For a data-mesh-like environment:

```text
Central platform
    |
    +-- governance guardrails
    +-- taxonomy
    +-- security baseline
    |
    +------------------+
                       |
             Domain data owners
                       |
                Domain datasets
                       |
                LF-Tags / policy
                       |
                  Consumers
```

Lake Formation should support governance, not become a bottleneck for every domain decision.

---

# 145. Final Knowledge Check — 25 Questions

1. Explain Lake Formation in one paragraph.
2. Explain IAM vs Lake Formation.
3. Explain the two-door authorization model.
4. Explain data-location registration.
5. Explain `DATA_LOCATION_ACCESS`.
6. Explain `IAMAllowedPrincipals`.
7. Explain hybrid access mode.
8. Explain named-resource grants.
9. Explain LF-TBAC.
10. Explain LF-Tag taxonomy.
11. Explain row-level filtering.
12. Explain column-level filtering.
13. Explain combined row + column security.
14. Explain KMS interaction.
15. Explain Athena integration.
16. Explain Glue integration.
17. Explain cross-account sharing.
18. Explain resource links.
19. Explain cross-Region awareness.
20. Explain permission union behavior.
21. Design an enterprise taxonomy.
22. Design a migration from IAM to Lake Formation.
23. Diagnose an access-denied incident.
24. Design a PII governance model.
25. Design a production Lake Formation operating model.

A passing answer should explain:

```text
concept
+
authorization path
+
security boundary
+
operational consequence
```

---

# 146. Senior-Level Scenario Assessment

## Scenario A

> Marketing needs access to customer data but must never see email or phone and may only see Indian customers.

Your answer should include:

```text
LF-Tags
+
data filter
+
column restrictions
+
IAM
+
Athena
+
negative testing
```

---

## Scenario B

> Existing Glue jobs use IAM/S3 access. The company wants Lake Formation without breaking production.

Your answer should include:

```text
inventory
+
hybrid mode
+
pilot
+
opt-in
+
testing
+
rollback
+
staged migration
```

---

## Scenario C

> A partner company needs access to one table in another account.

Your answer should include:

```text
producer
+
Lake Formation
+
AWS RAM
+
consumer
+
resource link
+
consumer permissions
+
KMS
+
revocation
```

---

## Scenario D

> A role unexpectedly gains access to confidential tables after a new LF-Tag policy is deployed.

Your answer should include:

```text
named grants
+
LF-TBAC
+
tag assignment
+
union behavior
+
blast radius
+
containment
+
drift review
```

---

## Scenario E

> Athena queries fail after a new S3 location is registered.

Your answer should include:

```text
location registration
+
IAM
+
Lake Formation
+
S3
+
KMS
+
hybrid state
+
principal opt-in
```

---

# 147. Final Cheat Sheet

## Authorization

```text
IAM
+
Lake Formation
+
S3
+
KMS
```

---

## Catalog

```text
Catalog
  |
  +-- Database
       |
       +-- Table
            |
            +-- Columns
```

---

## Lake Formation

```text
Locations
+
Permissions
+
LF-Tags
+
Filters
+
Sharing
```

---

## LF-TBAC

```text
Resource
   |
   +-- domain=finance
   +-- sensitivity=restricted
   +-- pii=true
        |
        v
Principal policy
```

---

## Hybrid

```text
Registered location
        |
     Hybrid
        |
 +------+------+
 |             |
LF opted-in   IAM path
```

---

## Cross Account

```text
Producer
   |
Lake Formation
   |
AWS RAM
   |
Consumer
   |
Resource Link
   |
Athena
```

---

# 148. Final Operating Standard

A production Lake Formation engineer should instinctively ask:

```text
Who owns this data?
        ↓
Where is it stored?
        ↓
Is the location registered?
        ↓
Which permission model is active?
        ↓
IAM or Lake Formation?
        ↓
Is hybrid mode involved?
        ↓
Who needs access?
        ↓
What rows?
        ↓
What columns?
        ↓
Can LF-Tags express this?
        ↓
Do we need a data filter?
        ↓
Is this cross-account?
        ↓
Is KMS involved?
        ↓
Can this permission be delegated?
        ↓
How is it tested?
        ↓
How is it audited?
        ↓
When is access reviewed?
        ↓
How is access revoked?
```

---

# 149. Production Readiness Checklist

A learner is production-ready for this topic when they can:

```text
[ ] Explain IAM vs Lake Formation
[ ] Register an S3 data location
[ ] Explain Lake Formation data-location permissions
[ ] Grant database/table permissions
[ ] Design column restrictions
[ ] Design row restrictions
[ ] Design combined filters
[ ] Create an LF-Tag taxonomy
[ ] Implement LF-TBAC
[ ] Debug overlapping grants
[ ] Explain IAMAllowedPrincipals
[ ] Use hybrid access safely
[ ] Plan IAM → LF migration
[ ] Configure cross-account sharing
[ ] Understand resource links
[ ] Diagnose KMS failures
[ ] Diagnose Athena authorization failures
[ ] Build a permission matrix
[ ] Write governance as code conceptually
[ ] Design access reviews
[ ] Perform negative security tests
[ ] Write an incident runbook
[ ] Design a production governance architecture
```

---

# 150. Roadmap Coverage Audit

| Roadmap requirement | Covered | Depth |
|---|---:|---|
| Lake Formation architecture | Yes | Core |
| IAM integration | Yes | Core |
| Data lake administrators/personas | Yes | Core |
| S3 location registration | Yes | Core |
| Data location permissions | Yes | Core |
| Glue Catalog integration | Yes | Core |
| Database permissions | Yes | Core |
| Table permissions | Yes | Core |
| Column permissions | Yes | Core |
| Row-level security | Yes | Advanced |
| Cell-level security | Yes | Advanced |
| Data filters | Yes | Advanced |
| IAMAllowedPrincipals | Yes | Advanced |
| Hybrid access mode | Yes | Advanced |
| Named-resource access | Yes | Core |
| LF-Tags | Yes | Core |
| LF-TBAC | Yes | Advanced |
| Grantable permissions | Yes | Advanced |
| Athena integration | Yes | Core |
| Glue integration | Yes | Core |
| S3 integration | Yes | Core |
| KMS integration | Yes | Advanced |
| Cross-account sharing | Yes | Advanced |
| AWS RAM | Yes | Advanced |
| Resource links | Yes | Advanced |
| Cross-Region awareness | Yes | Awareness/Advanced |
| Governance taxonomy | Yes | Advanced |
| Governance operating model | Yes | Advanced |
| Access reviews | Yes | Advanced |
| Auditability | Yes | Advanced |
| Security | Yes | Core/Advanced |
| Cost considerations | Yes | Core |
| Troubleshooting | Yes | Core/Advanced |
| Break/fix labs | Yes | Advanced |
| Production architecture | Yes | Advanced |
| ADRs | Yes | Advanced |
| Practice questions | Yes | Core/Advanced |
| Interview preparation | Yes | Advanced |
| Knowledge checks | Yes | Advanced |
| Completion checklist | Yes | Core |

**Roadmap coverage: COMPLETE**

---

# 151. Technical Accuracy Audit

This module intentionally treats current AWS documentation as authoritative for fast-changing implementation details.

Verify before production implementation:

1. Current AWS Region.
2. Current Lake Formation feature availability.
3. Current cross-account version requirements.
4. Current Lake Formation API/CLI syntax.
5. Current AWS managed policy contents.
6. Current IAM requirements for grant/revoke operations.
7. Current KMS requirements.
8. Current Athena/Lake Formation integration behavior.
9. Current Glue/Lake Formation integration behavior.
10. Current cross-Region behavior.
11. Current Terraform/OpenTofu AWS provider support.

### Important current-documentation points

AWS currently documents:

- Lake Formation as a centralized data-lake permission system integrated with IAM.
- Permissions at catalog/table/column/row levels.
- S3 data-location registration.
- Hybrid access mode.
- LF-TBAC.
- Cross-account sharing through AWS RAM.
- Resource links.
- Cross-Region table access patterns.

These should be rechecked against the live AWS documentation when implementing the module because AWS service behavior and configuration options evolve.

**Technical accuracy audit: PASSED, with current-documentation verification required for deployment.**

---

# 152. Security Audit

```text
[x] IAM remains a required security layer
[x] Least privilege is emphasized
[x] S3 is treated as a security boundary
[x] KMS is treated as a security boundary
[x] Lake Formation permissions are treated as data authorization
[x] PII protection is covered
[x] Row-level restrictions are covered
[x] Column-level restrictions are covered
[x] Cross-account sharing is covered
[x] Negative security testing is required
[x] Grantable permissions are treated as elevated privilege
[x] IAMAllowedPrincipals is treated as migration-sensitive
[x] Hybrid migration requires staged testing
[x] No secrets are embedded
[x] Public S3 access is not recommended
```

**Security audit: PASSED**

---

# 153. Cost-Safety Audit

Lake Formation governance exercises should use:

```text
small datasets
+
short-lived resources
+
controlled Athena queries
+
existing learning accounts
```

Before production:

```text
[ ] Cross-account cost implications reviewed
[ ] Cross-Region implications reviewed
[ ] Athena query cost reviewed
[ ] S3 storage cost reviewed
[ ] KMS usage considered
[ ] Duplicate data avoided where possible
[ ] Temporary test resources removed
```

**Cost-safety audit: PASSED**

---

# 154. File-Scope Audit

This file is intentionally scoped to:

```text
G3 Topic 06
Lake Formation Permissions and Governance
```

It does not replace the dedicated modules for:

```text
Glue Catalog/Crawlers
Glue ETL/Data Quality
Athena advanced query engineering
Redshift
Kinesis/MSK
EMR
Orchestration
DMS
CloudWatch/CloudTrail/Cost
KMS/VPC networking
SageMaker Unified Studio/DataZone
```

Those topics are referenced only where necessary to explain Lake Formation integration.

**File-scope audit: PASSED**

---

# 155. Final Mental Model

```text
                  BUSINESS POLICY
                        |
                        v
                  DATA GOVERNANCE
                        |
             +----------+----------+
             |                     |
          Taxonomy              Ownership
             |                     |
             +----------+----------+
                        |
                   LF-Tags / Rules
                        |
                        v
                 Lake Formation
                        |
          +-------------+-------------+
          |             |             |
       Catalog       Filters       Locations
          |             |             |
          +-------------+-------------+
                        |
                     S3 + KMS
                        |
          +-------------+-------------+
          |                           |
        Athena                     Glue
          |                           |
          +-------------+-------------+
                        |
                    Consumers
```

The final operating principle is:

> **IAM answers who may use AWS resources and APIs; Lake Formation answers what governed lake data that identity may access; S3 and KMS enforce the underlying storage and encryption boundaries. Production governance succeeds only when all of these layers are designed together.**

---

# 156. Final Engineering Principle

> **Data governance is not a permission checkbox. It is an operating system for controlling who can discover, query, modify, share and delegate access to data across an evolving lake.**

The production progression is:

```text
Identity
   ↓
IAM
   ↓
S3 / KMS foundation
   ↓
Glue Catalog
   ↓
Lake Formation locations
   ↓
Named permissions
   ↓
Data filters
   ↓
LF-Tags / LF-TBAC
   ↓
Hybrid migration
   ↓
Cross-account sharing
   ↓
Resource links
   ↓
Audit
   ↓
Access review
   ↓
Governance as code
   ↓
Production data platform
```

**Module completion target:** You should be able to design, implement, troubleshoot and defend a Lake Formation governance architecture—not merely grant `SELECT` on an Athena table.
