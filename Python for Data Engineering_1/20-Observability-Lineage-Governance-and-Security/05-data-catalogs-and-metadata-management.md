# 05 — Data Catalogs and Metadata Management

> **Stage 2 — Python for Data Engineering → Module 2.20 — Observability, Lineage, Governance, and Security**

## Learning objective

By the end of this module, you should be able to answer:

> **How do engineers and business users discover trustworthy data, understand what it means, identify its owner, see its lineage and quality, determine whether it is safe to use, and know whether the dataset is still actively supported?**

A **data catalog** is a searchable system for discovering and understanding data assets and their associated metadata.

**Metadata management** is the discipline of collecting, maintaining, governing, and using information about data throughout its lifecycle.

The core progression is:

```text
Metadata
  ↓
Catalog
  ↓
Discovery
  ↓
Ownership
  ↓
Lineage
  ↓
Classification
  ↓
Quality
  ↓
Trust
  ↓
Governance
  ↓
Data Products
```

### Production principle

> **A data catalog is valuable only when the metadata is trustworthy, discoverable, current, and connected to real engineering workflows.**

This module progresses from first principles to production architecture:

```text
Basic → Fundamentals → Practical → Advanced → Production
```

---

## 1. What is data?

Start with the data itself:

```text
customer_id
order_id
amount
order_date
```

A table may contain values, but a consumer still needs to know what those values mean, where they came from, whether they are current, who supports them, and whether they are safe to use.

For example, `orders.amount` is much more useful when accompanied by:

```text
Type: DECIMAL
Description: Order monetary amount
Owner: Finance Data Team
Quality: 99.8% valid
Freshness: 15 minutes
Classification: Confidential
Source: PostgreSQL
Downstream: Revenue Dashboard
```

> **Metadata is information that helps people and systems understand, operate, govern, and use data.**

### Checkpoint

1. **What is data?** — Values representing business or operational facts.
2. **What is metadata?** — Information describing, operating, governing, and contextualizing those values.
3. **Why does metadata matter?** — Without it, consumers cannot reliably interpret or operate data.

---

## 2. Why metadata management matters

Poor metadata creates operational problems:

| Problem | Consequence |
|---|---|
| Nobody knows what a column means | Wrong analytical interpretation |
| No clear owner | Incidents and questions have nowhere to go |
| Similar datasets have different definitions | Conflicting metrics |
| Dashboard uses deprecated table | Fragile reporting |
| Sensitive data is unclassified | Governance and access risk |
| No trust information | Consumers cannot assess fitness for use |
| Existing dataset cannot be discovered | Duplicate pipelines and duplicated cost |

Metadata management addresses these problems by making meaning, ownership, lifecycle, quality, lineage, and governance visible and maintainable.

### Production mental model

```text
Good metadata
   ↓
Discoverability
   ↓
Correct interpretation
   ↓
Safer consumption
   ↓
Better operations
   ↓
Better governance
```

### Checkpoint

If your organization has a catalog but engineers still ask in Slack, “Which table should I use?”, the catalog has not solved the discovery problem yet.

---

## 3. What is a data catalog?

A catalog represents data assets and the metadata associated with them.

Typical assets include:

```text
Database
Schema
Table
Column
Kafka topic
Pipeline
Dashboard
ML feature
Data product
API
Object/file
```

A simple architecture is:

```text
Data Sources
    ↓
Metadata Collection
    ↓
Data Catalog
    ↓
Search / Discovery
    ↓
Users
```

A catalog generally stores **information about data**, not the analytical contents of every underlying dataset.

### Catalog vs warehouse vs lake

| System | Primary purpose |
|---|---|
| Data warehouse | Store and query analytical data |
| Data lake | Store large-scale raw and processed data |
| Data catalog | Discover and understand data and its metadata |

They work together:

```text
Warehouse / Lake / Databases / Kafka
                ↓
        Metadata ingestion
                ↓
             Catalog
                ↓
     Discovery + Governance
```

### Checkpoint

A catalog is not a replacement for a warehouse or lake. Its primary job is to make data assets understandable and discoverable.

---

## 4. Metadata categories

The roadmap requires three major metadata categories.

### 4.1 Technical metadata

Technical metadata describes the structure and physical or logical representation of data.

Examples:

- table and column names
- data types
- schemas
- partitions
- storage locations
- database/schema identifiers
- table size
- technical properties

### 4.2 Business metadata

Business metadata describes what data means to the organization.

Examples:

- business definition
- owner
- domain
- glossary term
- business meaning
- criticality

### 4.3 Operational metadata

Operational metadata describes how the asset behaves and is maintained.

Examples:

- freshness
- pipeline status
- last successful run
- usage
- quality score
- SLO
- update frequency
- deprecation status

| Category | Core question | Examples |
|---|---|---|
| Technical | What is it technically? | schema, type, partition |
| Business | What does it mean? | definition, owner, domain |
| Operational | Is it healthy and supported? | freshness, quality, SLO |

A trustworthy catalog combines all three.

### Checkpoint

For `gold.daily_revenue`, the column type is technical metadata, the Finance owner is business metadata, and “freshness SLO met” is operational metadata.

---

## 5. Metadata lifecycle

Metadata itself has a lifecycle:

```text
Discover
   ↓
Capture
   ↓
Classify
   ↓
Document
   ↓
Validate
   ↓
Publish
   ↓
Use
   ↓
Update
   ↓
Deprecate
   ↓
Archive
```

Metadata becomes dangerous when it becomes stale.

For example:

```text
Actual owner: Data Platform Team
Catalog owner: Former employee
```

The catalog now contains information that looks authoritative but is wrong.

### Production rule

Automate metadata that can be derived from systems. Use human ownership for semantics that systems cannot infer reliably.

### Checkpoint

A catalog is not “finished” after ingestion. Metadata must be maintained throughout the asset lifecycle.

---

## 6. Data discovery and search

**Data discovery** is the ability to find useful data assets quickly.

A useful catalog should support:

- keyword search
- metadata search
- column search
- glossary search
- owner search
- domain search
- classification search
- filtering and facets
- certification
- quality
- freshness
- usage

Example request:

> “Find the trusted daily revenue dataset used by Finance.”

A useful search experience should allow filtering by:

```text
Keyword: revenue
Domain: Finance
Certification: Certified
Quality: Passing
Freshness: Healthy
Status: Active
Owner: Revenue Data Team
```

Search quality strongly influences adoption. If users cannot find assets reliably, they will create duplicates or return to informal channels.

### Checkpoint

A catalog should make the path from **business question → candidate asset → evidence → decision** short and explicit.

---

## 7. Dataset descriptions

Bad:

```text
Orders table.
```

Better:

```text
Contains validated customer orders from production systems.
One row represents one completed order.
Used by Finance and Revenue Analytics.
Updated daily by 06:00 UTC.
Owner: Revenue Data Team.
```

A production description should communicate, where applicable:

1. What the asset represents.
2. Grain.
3. Business purpose.
4. Major consumers.
5. Update frequency.
6. Owner.
7. Important limitations.
8. Related glossary terms or data products.

### Checkpoint

A description is not decoration. It should reduce the number of questions a consumer must ask before using the asset.

---

## 8. Ownership, domains, and stewardship

Every important data asset should have a clear ownership model.

Possible roles:

- **Technical owner** — responsible for implementation and operation.
- **Business owner** — accountable for business meaning and value.
- **Data steward** — maintains definitions, quality, and governance context.
- **Platform owner** — operates shared catalog/platform infrastructure.

One person does not need to fill every role.

Example:

```text
Dataset:
gold.daily_revenue

Technical owner:
Data Platform Team

Business owner:
Finance Analytics

Data steward:
Revenue Data Steward
```

Ownership matters for:

- incidents
- questions
- quality
- changes
- access decisions
- deprecation

### Domains

Common domains include:

```text
Finance
Customer
Marketing
Operations
Risk
Supply Chain
```

A domain hierarchy can look like:

```text
Domain
  ↓
Data Products
  ↓
Datasets
  ↓
Pipelines
```

Central catalog infrastructure can coexist with decentralized domain ownership.

### Checkpoint

Ownership answers **“Who is accountable?”**; a domain answers **“Which business area owns the context?”**

---

## 9. Business glossary

A **business glossary** provides shared definitions for important business concepts.

Examples:

```text
Revenue
Active Customer
Order
Churn
Net Sales
Gross Margin
```

Example glossary term:

```text
Revenue

Definition:
Total recognized sales after applicable adjustments.

Owner:
Finance

Related datasets:
gold.daily_revenue
gold.monthly_revenue
```

A glossary reduces semantic disagreement across teams.

### Glossary term vs column description

A **column description** is specific to a dataset.

A **glossary term** is an enterprise/business definition that can be reused across datasets.

```text
Column:
orders.revenue
      ↓
Glossary:
Revenue
```

The column can describe how the field behaves in that particular table, while the glossary establishes the organization-wide business concept.

### Checkpoint

If two teams use the word “customer” differently, the catalog needs more than column descriptions; it needs governed business terminology.

---

## 10. Classification and tags

Catalogs commonly represent:

- tags
- classifications
- sensitivity
- confidentiality
- PII
- Internal
- Public
- Restricted

Example:

```text
customer.email
    ↓
   PII
    ↓
Confidential
    ↓
Restricted access
```

Classification can become an input to downstream controls.

### PII/confidentiality metadata

Examples of identifiers and sensitive data:

```text
Direct identifiers:
- email
- phone
- government ID

Sensitive attributes:
- financial information
- health-related information

Quasi-identifiers:
- date of birth
- postal code
- location
```

The catalog should represent classification accurately, but do not assume that a catalog tag automatically enforces access.

A useful conceptual chain is:

```text
Classification
    ↓
Access policy
    ↓
Masking
    ↓
Audit
```

### Tag-based governance

For example:

```text
Tag: PII
```

may be consumed by policy systems to require:

```text
Restricted access
Masking
Access auditing
```

> **Catalog metadata and policy enforcement are different systems or responsibilities unless a specific platform/integration explicitly combines them.**

### Checkpoint

A tag is evidence or context. It is not automatically an enforcement mechanism.

---

## 11. Catalog + lineage

A catalog becomes much more useful when connected to lineage.

Example:

```text
gold.daily_revenue
      ↑
silver.orders
      ↑
raw.orders
```

A consumer should be able to navigate:

```text
Dataset
  ↓
Owner
  ↓
Schema
  ↓
Quality
  ↓
Lineage
  ↓
Consumers
```

Lineage supports:

- impact analysis
- root-cause investigation
- migration planning
- safe deprecation
- consumer discovery

This module consumes the lineage concepts from Topic 04 rather than redefining the entire lineage system.

### Checkpoint

A catalog answers **what, who, and meaning**; lineage adds **where it came from and what depends on it**.

---

## 12. Catalog + quality and trust signals

Operational metadata helps consumers answer:

> “Can I trust this asset enough for my use case?”

Example:

```text
Quality status: PASS
Freshness: 12 min
Null rate: 0.2%
Last successful run: 05:58 UTC
```

### Trust signals

Useful signals include:

- Certified
- Trusted
- Quality status
- Freshness
- SLO
- Usage
- Ownership
- Documentation completeness
- Deprecation status
- Lineage availability

Example:

```text
gold.daily_revenue

✓ Certified
✓ Owner assigned
✓ Freshness SLO met
✓ Quality checks passing
✓ Lineage available
```

Trust signals must be **evidence-backed**, not arbitrary badges.

### Certification

Certification means the asset has met explicit organizational standards, for example:

```text
Owner assigned
Description complete
Schema documented
Quality checks configured
Freshness SLO defined
Lineage available
Security classification present
Consumers identified
```

### Freshness

```text
Expected:
Every 15 minutes

Actual:
Updated 11 minutes ago

Status:
Healthy
```

### Usage metadata

Possible signals:

- query frequency
- consumer count
- dashboard usage
- pipeline dependencies
- popularity
- last accessed

Usage can help prioritize support, identify critical assets, plan migrations, support deprecation, and improve adoption. Popularity alone is not proof of business importance.

### Deprecation metadata

A useful record can contain:

```text
Status: ACTIVE
Deprecated: No
Deprecation date: —
Removal date: —
Replacement: —
Migration guide: —
```

When deprecated:

```text
Status: DEPRECATED
Replacement: gold.daily_revenue_v2
Removal date: 2026-12-01
```

### Checkpoint

Trust is a combination of evidence: ownership, documentation, freshness, quality, lineage, usage, SLO compliance, certification, and lifecycle status.

---

## 13. OpenMetadata

**OpenMetadata** is an open-source metadata/catalog platform used to discover, document, govern, and connect data assets.

For this curriculum, focus on concepts rather than product marketing:

- catalog and asset representation
- discovery and search
- metadata ingestion
- ownership
- glossary
- classification
- lineage
- quality
- documentation

Conceptually:

```text
Source Systems
      ↓
Metadata Ingestion
      ↓
OpenMetadata
      ↓
Search / Ownership / Glossary / Lineage / Quality
```

Use a version-compatible local deployment when performing the lab. Exact commands and connector behavior can vary by release; verify them against the installed release documentation rather than treating an example command in this module as universally guaranteed.

---

## 14. DataHub

**DataHub** is a metadata platform for cataloging, discovering, governing, and connecting data assets.

Focus on:

- metadata ingestion
- search
- ownership
- glossary
- tags
- lineage
- governance

Conceptually:

```text
Databases / Warehouses / Pipelines / BI / Streams
                    ↓
              Metadata ingestion
                    ↓
                  DataHub
                    ↓
       Discovery + Governance + Lineage
```

Again, keep version-specific syntax separate from stable architectural concepts.

---

## 15. OpenMetadata vs DataHub

Do not declare one universally superior.

| Dimension | OpenMetadata | DataHub |
|---|---|---|
| Metadata model | Rich catalog-oriented model | Metadata graph/model |
| Discovery | Strong search/discovery concepts | Strong search/discovery concepts |
| Lineage | Integrated lineage representation | Integrated lineage representation |
| Ownership | Supported | Supported |
| Glossary | Supported | Supported |
| Classification/tags | Supported | Supported |
| Ingestion | Connector-oriented | Connector-oriented |
| Metadata-as-code | Possible through supported interfaces/workflows | Possible through supported interfaces/workflows |
| Extensibility | Open-source extensibility | Open-source extensibility |
| Ecosystem | Broad integrations | Broad integrations |

Selection should consider:

1. Existing platform ecosystem.
2. Required connectors.
3. Metadata model fit.
4. Lineage requirements.
5. Search/discovery experience.
6. Governance needs.
7. Operational ownership.
8. Deployment model.
9. Engineering skill set.
10. Long-term adoption.

### Checkpoint

Choose a catalog because it fits your operating model and integrations—not because a feature checklist says it is universally “best.”

---

## 16. Cloud catalog concepts

Cloud platforms can provide catalog/governance capabilities.

Examples include:

- AWS Glue Data Catalog
- Azure data catalog/governance capabilities
- Google Cloud data catalog/governance capabilities

The architectural idea is:

```text
Cloud Catalog
      +
Open Catalog
      +
Lineage
      +
Governance
```

Organizations may combine cloud-native metadata systems with an enterprise catalog or use one as a metadata source for another.

The important engineering question is not “Which product wins?” but:

> **Where is metadata authoritative, how is it synchronized, and which system is responsible for each governance function?**

---

## 17. Metadata ingestion architecture

How does metadata get into a catalog?

```text
Source Systems
    ↓
Metadata Connectors
    ↓
Catalog
```

Possible sources:

```text
PostgreSQL
Warehouse
Object Storage
Kafka
dbt
Airflow
OpenLineage
BI tools
```

Ingestion modes include:

- scheduled
- event-driven
- API-based
- metadata-as-code
- runtime ingestion

### Warehouse/database ingestion

Typical metadata extracted:

- schemas
- tables
- columns
- types
- partitions
- statistics
- ownership
- usage where available

The catalog does not need to copy the underlying analytical data simply to represent this metadata.

### Checkpoint

A production catalog is normally an integration hub: many systems contribute metadata, and the catalog makes the resulting context searchable.

---

## 18. dbt metadata ingestion

dbt can contribute:

- models
- sources
- columns
- descriptions
- tests
- dependencies
- contracts
- documentation

Conceptual YAML:

```yaml
models:
  - name: daily_revenue
    description: "Daily revenue metrics"
    columns:
      - name: revenue
        description: "Total daily recognized revenue"
```

Metadata can flow from dbt into a catalog through supported integrations.

A metadata-as-code extension can look like:

```yaml
models:
  - name: daily_revenue
    description: "Certified daily revenue dataset"
    meta:
      owner: finance-data
      domain: finance
      criticality: tier_0
```

Treat this as a conceptual pattern; exact catalog synchronization depends on the deployed dbt/catalog integration.

---

## 19. Airflow metadata ingestion

Airflow can contribute:

- DAGs
- tasks
- scheduling
- owners
- execution metadata
- pipeline relationships

Distinguish:

```text
Orchestration metadata
```

from:

```text
Dataset metadata
```

For example:

```text
Airflow:
daily_revenue_pipeline
schedule: hourly
owner: revenue-platform
```

is orchestration context.

```text
Dataset:
gold.daily_revenue
schema: ...
owner: Revenue Data Team
freshness SLO: ...
```

is dataset context.

The two should be connected, not confused.

---

## 20. Kafka metadata

Streaming assets should be discoverable alongside batch data.

Represent, where available:

- topics
- partitions
- producers
- consumers
- schemas
- ownership
- retention metadata
- data classification

Example:

```text
Topic: orders.events
Owner: Order Platform
Schema: OrderEvent v3
Partitions: 24
Retention: 7 days
Classification: Internal
Consumers:
  - fraud-service
  - revenue-pipeline
```

This lets users discover event streams as first-class data assets.

---

## 21. Lineage-system integration

Runtime lineage can enrich catalog metadata:

```text
OpenLineage
     ↓
Catalog
```

A useful asset page can expose:

```text
Dataset
  ↓
Owner
  ↓
Schema
  ↓
Quality
  ↓
Freshness
  ↓
Lineage
  ↓
Consumers
```

The catalog should not fabricate lineage when the lineage source has no evidence.

---

## 22. Metadata-as-code

A major production pattern is managing important metadata through version-controlled definitions.

```text
Metadata definition
      ↓
Git
      ↓
Pull Request
      ↓
CI validation
      ↓
Catalog update
```

Common components:

- Git
- YAML
- JSON
- dbt metadata
- contracts
- CI validation
- pull requests
- code review
- deployment

### Why metadata-as-code?

Manual UI editing is useful for exploration, but critical metadata needs:

- reviewability
- auditability
- repeatability
- ownership
- automated validation
- change history

### Example

```yaml
dataset: gold.daily_revenue
owner: finance-data
domain: finance
description: "Certified daily revenue dataset"
classification: confidential
criticality: tier_0
freshness_slo: "<15m"
```

### Checkpoint

Metadata-as-code turns important metadata changes into an engineering workflow rather than an undocumented manual action.

---

## 23. Data contracts and metadata

A data contract can define:

- schema
- semantics
- ownership
- quality expectations
- compatibility
- SLOs

Relationship:

```text
Data Contract
      ↓
Metadata
      ↓
Catalog
      ↓
Consumer trust
```

Do not confuse the contract with the catalog record.

- **Contract** defines expectations between producers and consumers.
- **Catalog** exposes discoverable metadata and context about the asset.
- **Runtime systems** enforce or measure relevant expectations.

### Example

```yaml
dataset: orders.events
owner: order-platform
schema_version: 3
compatibility: backward
freshness_slo: "<5m"
quality:
  invalid_rate: "<0.5%"
```

---

## 24. CI validation for metadata

Critical assets should have explicit metadata requirements.

Example policy:

```text
Every Tier-0 dataset must have:

✓ owner
✓ description
✓ domain
✓ classification
✓ freshness SLO
✓ quality checks
✓ lineage
```

Conceptual Python validation:

```python
REQUIRED = [
    "owner",
    "description",
    "domain",
    "classification",
    "freshness_slo",
]

def validate_metadata(metadata: dict) -> list[str]:
    errors = []
    for field in REQUIRED:
        value = metadata.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing required field: {field}")
    return errors

metadata = {
    "owner": "finance-data",
    "description": "Daily recognized revenue",
    "domain": "finance",
    "classification": "confidential",
    "freshness_slo": "<15m",
}

assert validate_metadata(metadata) == []
```

A pull request can fail when required metadata is missing.

### Example CI rule

```text
Changed dataset definition
        ↓
Parse metadata
        ↓
Validate required fields
        ↓
Validate classification
        ↓
Validate owner/domain
        ↓
Validate contract/SLO
        ↓
Pass → publish
Fail → reject PR
```

---

## 25. Metadata quality

Metadata has quality dimensions just like data.

Core dimensions:

- completeness
- accuracy
- consistency
- freshness
- timeliness
- ownership coverage

Example:

```text
Metadata completeness: 72%
```

That number is meaningful only if the organization has a defined measurement methodology.

A better metric definition might be:

```text
Completeness =
required metadata fields populated
----------------------------------
required metadata fields expected
```

For example:

```text
920 populated required fields
1000 expected required fields
= 92% completeness
```

### Metadata drift

Metadata can become stale even when the data itself is correct.

Examples:

- dataset renamed
- owner left team
- description outdated
- schema changed
- pipeline changed
- quality status stale
- lineage stale
- deprecated dataset still marked active

Detection mechanisms include:

```text
Source schema snapshot
        ↓
Compare catalog state
        ↓
Detect mismatch
        ↓
Create remediation
```

### Checkpoint

Metadata quality requires its own measurement and controls. A catalog can be technically online while its metadata is operationally wrong.

---

## 26. Catalog adoption

> **A technically excellent catalog is useless if engineers and analysts do not use it.**

Measure adoption through meaningful indicators such as:

- search usage
- active users
- dataset views
- metadata completeness
- certified dataset usage
- search success
- unresolved metadata questions
- documentation coverage

Avoid vanity metrics such as “number of catalog page views” when they do not demonstrate successful discovery or reuse.

A useful adoption funnel is:

```text
User has data question
        ↓
Searches catalog
        ↓
Finds candidate
        ↓
Understands meaning
        ↓
Checks trust signals
        ↓
Uses asset
        ↓
Returns for future discovery
```

---

## 27. Data products

A **data product** is more than a table.

Example:

```text
Data Product
├── Dataset
├── Owner
├── Documentation
├── Quality
├── SLO
├── Lineage
├── Contract
├── Access policy
└── Consumers
```

The catalog can expose this product context.

A supported data product should make clear:

- who owns it
- what it means
- what consumers can expect
- how quality is measured
- what SLO applies
- how changes are governed
- how consumers obtain/access it

### Data contract + data product

```text
Data Contract
      ↓
Data Product
      ↓
Catalog
```

The contract defines expectations; the data product is the supported consumable offering; the catalog makes the offering discoverable and understandable.

---

## 28. Data Mesh awareness

Data Mesh is relevant here because metadata and catalogs often need to support decentralized ownership.

Four high-level ideas:

1. **Domain ownership**
2. **Data as a product**
3. **Self-serve platform**
4. **Federated governance**

For catalogs, the key pattern is:

```text
Centralized catalog/platform
           +
Decentralized domain ownership
           +
Federated governance
```

Do not treat Data Mesh as a requirement for every organization.

### Domain ownership

Domains may own:

```text
Data products
Datasets
Definitions
Quality
SLOs
Owners
```

The central platform provides common capabilities; domains remain accountable for their products.

---

## 29. Data product SLOs

Examples:

```text
Freshness: < 15 minutes
Availability: 99.9%
Quality: < 0.5% invalid records
Support: Business-hours response
```

SLOs make a data product operationally meaningful.

Without an SLO:

```text
"Fresh data"
```

is ambiguous.

With an SLO:

```text
Data must be refreshed within 15 minutes.
```

the expectation is testable.

---

## 30. Trusted data product example

Consider:

```text
gold.daily_revenue
```

Catalog view:

```text
Domain:
Finance

Owner:
Revenue Data Team

Description:
Daily recognized revenue

Classification:
Confidential

Quality:
PASS

Freshness:
8 minutes

SLO:
<15 minutes

Lineage:
Available

Certification:
Certified

Status:
Active
```

A consumer can now make a reasoned decision rather than simply choosing the first table whose name contains `revenue`.

---

## 31. Safe deprecation workflow

A catalog-driven deprecation process:

```text
Identify candidate
      ↓
Inspect usage
      ↓
Inspect lineage
      ↓
Identify owners
      ↓
Notify consumers
      ↓
Mark deprecated
      ↓
Provide replacement
      ↓
Track migration
      ↓
Verify zero active consumers
      ↓
Remove
```

The combination is important:

```text
Catalog + Lineage + Usage + Ownership
```

Usage tells you who consumes the asset; lineage tells you dependency paths; ownership tells you who can coordinate the change.

---

## 32. Production catalog architecture

A practical architecture:

```text
                     ┌─────────────────────────┐
                     │ Source Systems           │
                     │ DB / DW / Kafka          │
                     │ dbt / Airflow / BI       │
                     └────────────┬────────────┘
                                  │
                         Metadata ingestion
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │ Data Catalog             │
                     │                         │
                     │ Search                   │
                     │ Ownership                │
                     │ Glossary                 │
                     │ Classification           │
                     │ Lineage                  │
                     │ Quality                  │
                     │ Usage                    │
                     │ Lifecycle                │
                     └────────────┬────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
               Engineers      Analysts     Governance
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| Source systems | Produce authoritative technical state |
| Metadata connectors | Extract and normalize metadata |
| dbt | Supply model, test, documentation, and contract metadata |
| Airflow | Supply orchestration context |
| Kafka | Supply streaming asset/schema context |
| OpenLineage | Supply runtime lineage evidence |
| Catalog | Make metadata searchable and governable |
| Quality systems | Produce quality evidence |
| Governance/policy systems | Enforce controls where applicable |
| Consumers | Discover, evaluate, and use assets |

The catalog is an integration and discovery layer, not necessarily the enforcement point for every policy.

---

## 33. Hands-on catalog lab

Use **OpenMetadata as the primary hands-on platform** for this module. DataHub is the conceptual equivalent.

> **Version note:** Exact installation commands, connector names, configuration fields, and APIs vary by release. Use the release documentation for the version you install. The workflow below is intentionally stable at the architectural level.

### Lab architecture

```text
Local PostgreSQL
      ↓
Metadata ingestion
      ↓
OpenMetadata
      ↓
Search / Documentation / Ownership / Governance
```

### Lab goals

1. Start the catalog locally.
2. Register a database.
3. Discover tables.
4. Inspect schemas.
5. Add descriptions.
6. Add an owner.
7. Assign a domain.
8. Add a glossary term.
9. Add classification.
10. Add tags.
11. Connect lineage.
12. Display quality information.
13. Display freshness.
14. Mark dataset certified.
15. Mark dataset deprecated.
16. Search for assets.

### Suggested local source

Create a small PostgreSQL database:

```sql
CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE finance.daily_revenue (
    business_date DATE NOT NULL,
    revenue NUMERIC(18, 2) NOT NULL,
    order_count INTEGER NOT NULL
);
```

Insert representative test data:

```sql
INSERT INTO finance.daily_revenue
    (business_date, revenue, order_count)
VALUES
    ('2026-10-01', 125000.50, 4300),
    ('2026-10-02', 131200.25, 4475);
```

In the catalog, document:

```text
Owner: Revenue Data Team
Domain: Finance
Classification: Confidential
Description: Daily recognized revenue for official Finance reporting
Freshness SLO: <24h
```

Then verify that a user can discover the asset and understand its purpose without opening the database directly.

### Lab success criteria

```text
[ ] Database registered
[ ] Table discoverable
[ ] Schema visible
[ ] Description present
[ ] Owner present
[ ] Domain present
[ ] Glossary term linked
[ ] Classification present
[ ] Tags present
[ ] Lineage represented
[ ] Quality evidence visible
[ ] Freshness evidence visible
[ ] Certification criteria satisfied
[ ] Deprecation workflow tested
[ ] Search returns the intended asset
```

---

## 34. Metadata-as-code lab

Build:

```text
Git
 ↓
metadata.yaml
 ↓
CI validation
 ↓
catalog update
```

Example:

```yaml
dataset: gold.daily_revenue
owner: finance-data
domain: finance
description: "Certified daily revenue dataset"
classification: confidential
criticality: tier_0
freshness_slo: "<15m"
```

A minimal validation script:

```python
from pathlib import Path
import yaml

REQUIRED = {
    "owner",
    "domain",
    "description",
    "classification",
    "criticality",
    "freshness_slo",
}

metadata = yaml.safe_load(Path("metadata.yaml").read_text())

missing = sorted(REQUIRED - metadata.keys())

if missing:
    raise SystemExit(
        "Metadata validation failed; missing: " + ", ".join(missing)
    )

print("Metadata validation passed")
```

Example CI behavior:

```text
Pull request
     ↓
Load YAML
     ↓
Validate required fields
     ↓
Validate allowed classification
     ↓
Validate criticality rules
     ↓
Validate SLO
     ↓
PASS → merge/publish
FAIL → block change
```

For critical assets, add rules such as:

```text
Tier-0
  → owner required
  → business description required
  → classification required
  → freshness SLO required
  → quality checks required
  → lineage required
```

---

## 35. Failure-injection lab

### Failure 1 — Missing owner

```text
Dataset has no owner.
```

Expected response:

```text
CI validation fails
       ↓
Catalog record rejected/incomplete
       ↓
Owner assigned
       ↓
Validation passes
```

### Failure 2 — Stale description

The schema changes, but the description remains unchanged.

Detection:

```text
Source schema
     vs
Catalog metadata
     ↓
Mismatch detected
```

Remediation: update the description and review the semantic impact.

### Failure 3 — Incorrect classification

A PII column is marked `Internal` rather than `Restricted`.

Risk:

- incorrect access assumptions
- inadequate controls
- governance exposure

Remediation should include correcting metadata, reviewing policy application, identifying affected consumers, and preventing recurrence.

### Failure 4 — Missing lineage

A critical dataset has no lineage.

Impact:

- weak impact analysis
- difficult incident diagnosis
- unsafe deprecation
- lower trust

### Failure 5 — Stale freshness

Catalog says:

```text
Updated 10 minutes ago
```

but actual data is five hours old.

This is a trust failure. Operational metadata must be refreshed from authoritative runtime systems rather than manually trusted indefinitely.

### Failure 6 — Deprecated dataset still heavily used

Use:

```text
Usage + Lineage + Ownership
```

to identify active consumers, notify them, provide a replacement, and track migration.

---

## 36. Catalog adoption exercise

### Scenario

> The organization spent six months building a catalog, but engineers still ask for datasets in Slack.

Diagnose the adoption problem.

Possible causes:

- poor search
- stale metadata
- missing ownership
- no quality signals
- no lineage
- excessive manual documentation
- catalog not integrated into engineering workflows
- low trust
- no metadata-as-code
- no incentives or process integration

### Expert solution

Do not respond by simply adding more catalog features.

First measure the discovery journey:

```text
Question
  ↓
Search
  ↓
Candidate found?
  ↓
Meaning understood?
  ↓
Trust evidence available?
  ↓
Asset used?
```

Then repair the largest failure points.

Typical priorities:

1. Improve search relevance.
2. Ensure critical assets have owners.
3. Automate technical and operational metadata.
4. Add evidence-backed quality/freshness signals.
5. Integrate lineage.
6. Establish certification criteria.
7. Move critical metadata into code and CI.
8. Integrate catalog links into existing workflows.
9. Measure successful discovery rather than page views.

---

## 37. Trust score exercise

A hypothetical transparent trust score may consider:

```text
Ownership
Documentation
Freshness
Quality
Lineage
Certification
Usage
SLO compliance
```

Do not create an opaque score with arbitrary weights.

A better approach is to expose evidence:

```text
Ownership: PASS
Documentation: 95%
Freshness SLO: PASS
Quality: PASS
Lineage: COMPLETE
Certification: CERTIFIED
SLO compliance: 99.7%
```

If an aggregate score is used, publish:

- component definitions
- weighting
- missing-data treatment
- update frequency
- thresholds
- evidence links

The score should support judgment, not replace it.

---

## 38. Testing metadata

Metadata should be testable.

Examples:

```text
[ ] Required owner exists
[ ] Description exists
[ ] Domain exists
[ ] Classification exists
[ ] Glossary reference is valid
[ ] SLO exists for critical datasets
[ ] Lineage exists
[ ] Metadata is not stale
[ ] Deprecated datasets have replacements
[ ] Required PII tags are present
```

Example:

```python
def validate_dataset_metadata(metadata: dict) -> list[str]:
    errors = []

    if not metadata.get("owner"):
        errors.append("owner is required")

    if not metadata.get("description"):
        errors.append("description is required")

    if not metadata.get("domain"):
        errors.append("domain is required")

    if not metadata.get("classification"):
        errors.append("classification is required")

    if metadata.get("criticality") == "tier_0":
        if not metadata.get("freshness_slo"):
            errors.append("tier_0 requires freshness_slo")
        if not metadata.get("lineage"):
            errors.append("tier_0 requires lineage")

    return errors
```

For PII, do not rely only on a manually typed tag. Where possible, combine declared metadata with automated classification, schema inspection, reviews, and policy validation.

---

## 39. Common production mistakes

| Mistake | Why it happens | Why dangerous | Detection | Production fix |
|---|---|---|---|---|
| Catalog treated as documentation website | Feature-first implementation | Stale pages | Low search success | Integrate runtime metadata |
| Everything entered manually | Early prototype | High maintenance cost | Missing/stale fields | Automate ingestion |
| No metadata ownership | Governance unclear | Nobody fixes errors | Unassigned assets | Assign accountable roles |
| No metadata-as-code | UI-only workflow | Poor reviewability | Unreviewed changes | Git + CI |
| Stale metadata | No lifecycle process | Wrong decisions | Drift checks | Refresh from sources |
| Poor search | Weak indexing/model | Users bypass catalog | Search failures | Improve indexing/taxonomy |
| Missing lineage | Integration gap | Weak impact analysis | Critical assets without lineage | Integrate lineage |
| Missing quality signals | Catalog isolated from quality | Low trust | No evidence | Publish quality metadata |
| No classification | Governance omitted | Security risk | Unclassified sensitive fields | Classify + validate |
| No glossary | Semantics fragmented | Metric disagreement | Repeated definition questions | Govern business terms |
| No domain ownership | Centralized ownership | Slow decisions | Assets lack domains | Establish domains |
| No usage information | Catalog disconnected from query/BI systems | Unsafe deprecation | Unknown consumers | Ingest usage |
| No deprecation workflow | Lifecycle ignored | Broken consumers | Active deprecated assets | Define lifecycle |
| No certification criteria | Badges assigned manually | False trust | Inconsistent certification | Evidence-based criteria |
| Treat every dataset equally | No tiering | Too much effort | High maintenance burden | Prioritize critical assets |
| No adoption measurement | Platform-centric thinking | Low ROI | No discovery metrics | Measure outcomes |
| Catalog disconnected from workflows | Separate tool | Users stay in existing tools | Low referrals | Embed catalog links/context |
| Metadata contradicts system state | Manual updates | False authority | Drift detection | Reconcile automatically |
| Tags assumed to enforce policy | Conceptual confusion | Security gap | Policy tests fail | Separate metadata from enforcement |
| No CI validation | No quality gate | Regression | Bad PRs merge | Add automated checks |

---

## 40. Production trade-offs

There is no universally correct architecture.

### Centralized vs decentralized metadata ownership

**Centralized**
- consistent standards
- simpler governance
- can become a bottleneck

**Decentralized**
- domain expertise
- stronger accountability
- requires federation and standards

### Manual vs automated metadata

**Manual**
- useful for business semantics
- expensive at scale
- prone to staleness

**Automated**
- scalable and current for derived fields
- may miss business meaning

### UI-managed vs metadata-as-code

**UI**
- accessible
- good for exploration

**Code**
- reviewable
- repeatable
- auditable

### Rich metadata vs maintenance cost

More metadata is not automatically better. Prefer metadata that materially improves discovery, trust, governance, operations, or decision-making.

### Completeness vs accuracy

A 100% populated catalog with incorrect metadata is worse than a smaller catalog with highly trustworthy metadata.

### Catalog coverage vs catalog trust

Coverage answers:

> “How many assets are represented?”

Trust answers:

> “How much should users rely on the information?”

Trust is more important for critical decisions.

### Open-source vs cloud-native

Evaluate:

- integration requirements
- operating cost
- deployment model
- governance model
- skill set
- ecosystem
- portability

### Central governance vs domain ownership

A strong pattern is:

```text
Central standards/platform
          +
Domain accountability
          +
Federated governance
```

### Certification vs continuous evidence

A static “Certified” badge can become stale. Certification should be backed by continuously refreshed evidence where possible.

---

## 41. Production design principles

A production catalog should follow these principles:

1. **Automate what can be derived.**
2. **Assign explicit ownership.**
3. **Make critical semantics reviewable.**
4. **Connect catalog records to lineage.**
5. **Expose quality and freshness evidence.**
6. **Classify sensitive data.**
7. **Use metadata-as-code for critical metadata.**
8. **Validate metadata in CI.**
9. **Treat metadata as a lifecycle, not a one-time import.**
10. **Measure adoption by successful discovery and reuse.**
11. **Use usage and lineage for safe deprecation.**
12. **Do not confuse metadata with policy enforcement.**
13. **Prefer evidence-backed trust signals.**
14. **Prioritize critical assets.**
15. **Integrate the catalog into normal engineering workflows.**

---

## 42. Senior interview preparation

### 1. What is metadata?

**Answer:** Metadata is information that describes, contextualizes, operates, governs, and helps users understand data assets.

### 2. What is a data catalog?

**Answer:** A searchable system that organizes data assets and their associated metadata so users can discover and understand data.

### 3. What are technical, business, and operational metadata?

**Answer:** Technical describes structure; business describes meaning and accountability; operational describes health, lifecycle, usage, freshness, and runtime context.

### 4. Why does ownership matter?

**Answer:** Without accountability, questions, incidents, quality problems, access decisions, and deprecations have no clear responsible party.

### 5. What is a business glossary?

**Answer:** A governed set of shared business definitions that can be referenced consistently across datasets and teams.

### 6. How is a glossary term different from a column description?

**Answer:** A column description is local to an asset; a glossary term defines a reusable business concept.

### 7. Why integrate lineage into a catalog?

**Answer:** To connect assets to upstream sources and downstream consumers, enabling impact analysis, troubleshooting, and safe change management.

### 8. How should PII classification work?

**Answer:** Sensitive assets should carry explicit classification metadata that can be consumed by governance and policy systems. Classification alone does not guarantee enforcement.

### 9. OpenMetadata vs DataHub?

**Answer:** Both provide catalog, discovery, ownership, governance, and lineage capabilities. Selection should depend on metadata model fit, integrations, operating model, extensibility, and adoption.

### 10. What metadata can dbt provide?

**Answer:** Models, sources, columns, descriptions, tests, dependencies, contracts, and documentation.

### 11. What metadata can Airflow provide?

**Answer:** DAGs, tasks, schedules, ownership, execution context, and orchestration relationships.

### 12. What should a catalog know about Kafka?

**Answer:** Topics, partitions, schemas, producers, consumers, ownership, retention, and classification where available.

### 13. What is metadata-as-code?

**Answer:** Managing important metadata definitions through version-controlled files and engineering workflows such as pull requests and CI.

### 14. How would you validate metadata in CI?

**Answer:** Validate required fields, allowed values, ownership, classification, SLOs, contracts, lineage requirements, and references before accepting the change.

### 15. What is metadata drift?

**Answer:** A mismatch between actual source/runtime state and the metadata represented in the catalog.

### 16. How do you measure catalog adoption?

**Answer:** Search success, active users, asset reuse, certified dataset usage, documentation coverage, and unresolved discovery questions are stronger than raw page views.

### 17. What makes a dataset a data product?

**Answer:** It has accountable ownership, documentation, quality expectations, SLOs, lineage, contract, lifecycle, and supported consumers—not merely a table.

### 18. How does Data Mesh affect catalogs?

**Answer:** It encourages domain ownership and data products while requiring shared self-service capabilities and federated governance.

### 19. How would you safely deprecate a dataset?

**Answer:** Inspect usage and lineage, identify owners and consumers, publish a replacement, communicate, mark deprecated, track migration, verify consumers have moved, then remove.

### 20. What is a production catalog architecture?

**Answer:** An integration layer collecting technical, business, operational, lineage, quality, and usage metadata from source systems into a searchable catalog with governance and lifecycle workflows.

---

## 43. Final assessment

### Basic

1. Define metadata.
2. Define a data catalog.
3. Explain technical metadata.
4. Explain business metadata.
5. Explain operational metadata.
6. Explain why descriptions matter.
7. Explain ownership.
8. Explain a business glossary.
9. Explain classification and tags.
10. Explain discovery.

### Intermediate

11. Design metadata for `gold.daily_revenue`.
12. Distinguish glossary terms from column descriptions.
13. Design a domain ownership model.
14. Design catalog search filters for Finance.
15. Explain catalog + lineage.
16. Explain catalog + quality.
17. Define certification criteria.
18. Design freshness metadata.
19. Design deprecation metadata.
20. Explain usage metadata.

### Advanced

21. Design metadata ingestion from PostgreSQL, dbt, Airflow, Kafka, and OpenLineage.
22. Compare OpenMetadata and DataHub.
23. Design metadata-as-code.
24. Design CI validation.
25. Detect metadata drift.
26. Design PII classification.
27. Design evidence-backed trust signals.
28. Design metadata quality metrics.
29. Design catalog adoption metrics.
30. Explain data contracts and catalog metadata.

### Senior / Production

31. Design an enterprise catalog architecture.
32. Balance centralized standards with domain ownership.
33. Design a Data Mesh-compatible catalog strategy.
34. Design data product SLOs.
35. Design a certification model.
36. Design safe deprecation using catalog + lineage + usage.
37. Design a metadata incident response process.
38. Explain catalog versus policy enforcement.
39. Decide between open-source and cloud-native catalog approaches.
40. Define the operating model for keeping metadata trustworthy.

---

## 44. Production challenge 1 — Choose the official revenue dataset

### Scenario

A Finance analyst asks:

> “Which dataset should I use for official daily revenue reporting?”

Candidates:

```text
finance.daily_revenue_v1
finance.daily_revenue_v2
analytics.revenue_summary
sandbox.revenue_test
```

Evaluate:

- description
- owner
- domain
- classification
- quality
- freshness
- SLO
- lineage
- certification
- usage
- deprecation status

### Example candidate evidence

| Asset | Certification | Freshness | SLO | Status | Owner | Quality |
|---|---|---|---|---|---|---|
| v1 | Certified | 9h | <24h | Deprecated | Revenue Data Team | PASS |
| v2 | Certified | 18m | <1h | Active | Revenue Data Team | PASS |
| summary | Trusted | 2h | <6h | Active | Analytics | PASS |
| sandbox | None | Unknown | None | Active | Analyst | Unknown |

### Expert solution

Choose:

```text
finance.daily_revenue_v2
```

because it is:

- certified
- actively supported
- owned
- fresh within its SLO
- quality-validated
- appropriate for official reporting
- not deprecated

The key lesson is:

> **Never choose a dataset from its name alone. Choose it from evidence.**

---

## 45. Production challenge 2 — Deprecate `daily_revenue_v1`

### Scenario

`finance.daily_revenue_v1` is scheduled for removal in 30 days.

Use:

```text
Catalog
+
Lineage
+
Usage
+
Ownership
+
Metadata-as-code
```

### Expert migration plan

```text
1. Confirm deprecation metadata.
2. Identify replacement dataset.
3. Inspect lineage.
4. Extract current consumers from usage/dependency systems.
5. Group consumers by owner and criticality.
6. Notify consumers.
7. Publish migration guidance.
8. Add deprecation warning to catalog.
9. Track consumer migrations.
10. Update metadata-as-code.
11. Verify zero active consumers.
12. Remove only after validation.
```

Do not remove the table merely because the replacement exists. Prove that supported consumers have migrated.

---

## 46. Production challenge 3 — Metadata incident

### Scenario

A PII dataset is incorrectly classified as `Internal` instead of `Restricted`.

Determine:

1. How should the error be detected?
2. How could CI have prevented it?
3. How should the catalog be corrected?
4. Which downstream datasets are affected?
5. Which access policies need review?
6. How should recurrence be prevented?

### Expert solution

**Detection**

Use a combination of:

```text
Schema inspection
+
Classification rules
+
Metadata CI
+
Periodic reconciliation
```

**Prevention**

Require classification for sensitive datasets and fail CI when classification is inconsistent with policy.

**Correction**

```text
Correct catalog classification
        ↓
Review policy mappings
        ↓
Identify affected consumers
        ↓
Review access
        ↓
Record incident
```

**Impact analysis**

Use lineage to identify downstream assets and policy dependencies.

**Recurrence prevention**

Add automated classification checks, metadata-as-code review, CI policy validation, and periodic source/catalog reconciliation.

---

## 47. Final learning checklist

```text
[ ] Explain metadata
[ ] Explain technical metadata
[ ] Explain business metadata
[ ] Explain operational metadata
[ ] Explain data catalogs
[ ] Explain why catalogs matter
[ ] Explain data discovery
[ ] Explain catalog search
[ ] Write useful dataset descriptions
[ ] Design data ownership
[ ] Explain domains
[ ] Explain business glossary
[ ] Distinguish glossary terms from column descriptions
[ ] Explain classifications
[ ] Explain tags
[ ] Explain PII classification
[ ] Explain tag-based governance
[ ] Integrate lineage with catalog
[ ] Integrate data quality with catalog
[ ] Explain trust signals
[ ] Define certified datasets
[ ] Explain freshness metadata
[ ] Explain usage metadata
[ ] Explain deprecation metadata
[ ] Explain OpenMetadata
[ ] Explain DataHub
[ ] Compare catalog approaches
[ ] Understand cloud catalog concepts
[ ] Understand metadata ingestion
[ ] Ingest database/warehouse metadata
[ ] Ingest dbt metadata
[ ] Ingest Airflow metadata
[ ] Represent Kafka metadata
[ ] Integrate OpenLineage
[ ] Explain metadata-as-code
[ ] Use dbt YAML metadata
[ ] Explain data contracts
[ ] Build CI metadata validation
[ ] Measure metadata quality
[ ] Detect metadata drift
[ ] Design catalog adoption strategy
[ ] Explain data products
[ ] Explain Data Mesh concepts
[ ] Design domain ownership
[ ] Define data product SLOs
[ ] Build a trusted data product
[ ] Design deprecation workflow
[ ] Test metadata
[ ] Design production catalog architecture
```

---

## 48. Roadmap coverage audit

| Roadmap requirement | Covered |
|---|---:|
| Technical metadata | ✓ |
| Business metadata | ✓ |
| Operational metadata | ✓ |
| Data discovery | ✓ |
| Search | ✓ |
| Descriptions | ✓ |
| Ownership | ✓ |
| Lineage | ✓ |
| Usage information | ✓ |
| OpenMetadata | ✓ |
| DataHub | ✓ |
| Cloud catalog concepts | ✓ |
| Metadata ingestion | ✓ |
| Warehouses | ✓ |
| Databases | ✓ |
| dbt | ✓ |
| Airflow | ✓ |
| Kafka | ✓ |
| Lineage systems | ✓ |
| Domains | ✓ |
| Business glossary | ✓ |
| Classification | ✓ |
| Tags | ✓ |
| PII/confidential classifications | ✓ |
| Metadata-as-code | ✓ |
| dbt YAML | ✓ |
| Contracts | ✓ |
| CI validation | ✓ |
| Trust signals | ✓ |
| Certified datasets | ✓ |
| Quality status | ✓ |
| Freshness | ✓ |
| Deprecation | ✓ |
| Data products | ✓ |
| Data contracts | ✓ |
| Data Mesh concepts | ✓ |
| Owners | ✓ |
| SLOs | ✓ |
| Documentation | ✓ |
| Catalog adoption | ✓ |
| Metadata quality | ✓ |
| Metadata drift | ✓ |
| Failure injection | ✓ |
| Testing | ✓ |
| Governance | ✓ |
| Production catalog architecture | ✓ |

### Final mastery statement

You are ready to move forward when you can design a catalog system that answers:

```text
What is this?
Who owns it?
What does it mean?
Can I trust it?
How fresh is it?
Where did it come from?
Who uses it?
Is it sensitive?
Is it certified?
Is it deprecated?
What should I use instead?
```

The deepest production lesson is:

> **A catalog exists to turn unknown data into discoverable, understandable, governable, evidence-backed data products. The catalog itself is not the source of truth for every fact; trustworthy catalog architecture continuously connects metadata to the systems that actually produce, operate, govern, and consume the data.**
