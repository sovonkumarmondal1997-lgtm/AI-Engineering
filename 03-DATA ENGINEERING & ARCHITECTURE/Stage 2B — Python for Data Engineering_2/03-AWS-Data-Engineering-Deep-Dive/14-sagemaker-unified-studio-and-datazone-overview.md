# Topic 14 — SageMaker Unified Studio and DataZone Overview

> **Production-oriented AWS Data Engineering module**
>
> Focus: Data Catalogs, Business Metadata, Data Products, Amazon DataZone, SageMaker Unified Studio, Governed Discovery, Subscription/Access Workflows, Enterprise Data Platforms, and Architecture Trade-offs.

## Module Navigation

- [Purpose](#1-module-purpose)
- [Learning Outcomes](#2-learning-outcomes)
- [Prerequisites and Scope](#3-prerequisites-and-scope-boundary)
- [Catalog and Metadata Foundations](#4-the-enterprise-data-discovery-problem)
- [Data Products and DataZone](#9-data-products)
- [Governed Access](#20-subscription-requests)
- [AWS Service Relationships](#22-datazone--glue-data-catalog)
- [SageMaker Unified Studio](#27-sagemaker-unified-studio--fundamentals)
- [Platform Comparisons](#39-openmetadata)
- [Adoption Strategy](#44-adoption-framework)
- [Hands-on Labs](#32-hands-on-lab-1--publish-golddaily_revenue)
- [Break/Fix and Runbooks](#61-breakfix--dataset-discoverable-but-inaccessible)
- [Architecture Decision Records](#78-architecture-decision-record--datazone-vs-custom-catalog)
- [Interview and Practice](#83-senior-interview-questions)
- [Roadmap Audit](#90-final-roadmap-coverage-audit)

---

## 1. Module Purpose

This module is the final technical topic of the AWS Data Engineering Deep Dive. It connects the AWS services learned earlier to an enterprise-facing layer for data discovery, business context, governed sharing, and unified analytics/AI work.

The learning progression is:

```text
Data Catalog Fundamentals
→ Business Metadata
→ Business Glossaries
→ Data Products
→ Amazon DataZone
→ Domains and Projects
→ Publishing
→ Subscription Workflow
→ Governed Permissions
→ Glue Data Catalog
→ Lake Formation
→ Athena
→ Redshift
→ SageMaker Unified Studio
→ OpenMetadata / DataHub
→ Unity Catalog
→ Architecture Trade-offs
→ Adoption Strategy
→ Enterprise Data Platform
→ Applied AI
```

The goal is not to memorize product screens. The goal is to understand the architecture underneath a governed data marketplace and to make defensible platform decisions.

**Authoritative scope supplied for this module:** the requested progression, hands-on exercises, break/fix scenarios, runbooks, comparisons, ADRs, security/cost treatment, interview preparation, and roadmap audit are specified in the supplied Topic 14 implementation brief. fileciteturn70file0L164-L172

## 2. Learning Outcomes

By completion, you should be able to:

1. Explain why an enterprise needs a data catalog.
2. Distinguish technical metadata from business metadata.
3. Explain a business glossary and why semantic consistency matters.
4. Explain a data product as a governed, reusable business asset rather than merely a table.
5. Explain Amazon DataZone domains, projects, catalog assets, metadata forms, glossaries, publishing, data products, and subscriptions.
6. Explain the difference between discovery and authorization.
7. Trace a subscription from discovery through approval to underlying data permissions.
8. Explain how DataZone relates to Glue Data Catalog, Lake Formation, Athena, Redshift, and EMR.
9. Explain the role of SageMaker Unified Studio as a broader development experience for data, analytics, AI, and ML.
10. Compare AWS-native governance with composed or open-source approaches.
11. Evaluate DataZone, OpenMetadata, DataHub, and Unity Catalog without claiming they are identical products.
12. Make an adoption recommendation based on team size, governance maturity, AWS footprint, customization, multi-cloud requirements, compliance, cost, and lock-in.
13. Troubleshoot common discovery, subscription, metadata, and authorization failures.
14. Explain why governed metadata is relevant to enterprise AI and agentic systems.

## 3. Prerequisites and Scope Boundary

Prerequisites:

- AWS Data Engineering Topics 01–13.
- AWS Glue Data Catalog fundamentals.
- Lake Formation fundamentals.
- Athena fundamentals.
- Redshift fundamentals.
- IAM and KMS awareness.
- EventBridge awareness.
- Infrastructure-as-code awareness.
- Basic SQL.
- Basic Python/boto3.

This module does **not** repeat the full Lake Formation, Redshift, Athena, Glue, EMR, or SageMaker ML curricula. It connects them.

It is also not a generic machine-learning tutorial. SageMaker Unified Studio is studied from the Data Engineering, governed-data, analytics, platform, and Applied AI perspective.

The central architecture question is:

> How does an enterprise move from "we have data somewhere" to "people and AI systems can discover, understand, request, receive, and safely use governed data"?

## 4. The Enterprise Data Discovery Problem

A traditional environment often looks like this:

```text
Data Engineer → S3 / Glue
Analyst       → Athena / Redshift
ML Engineer   → pipelines / feature workflows
Business User → asks someone where the data is
Governance    → separate documents, tickets, policies
```

The technical systems may work perfectly while the organization still suffers from:

- unknown datasets;
- duplicate definitions;
- unclear ownership;
- stale documentation;
- inconsistent business terminology;
- uncontrolled access requests;
- long approval cycles;
- hidden dependencies;
- poor reuse;
- duplicated pipelines;
- unclear data quality;
- difficulty finding trustworthy data for AI.

A governed discovery layer changes the human workflow:

```text
User
  ↓
Discover
  ↓
Understand
  ↓
Evaluate quality / ownership / meaning
  ↓
Request access
  ↓
Approval / policy decision
  ↓
Underlying authorization
  ↓
Query / consume
```

This is a platform problem, not merely a search problem.

## 5. Data Platform vs Data Catalog

A **data platform** is the broader system that stores, processes, governs, serves, observes, and protects data.

A **data catalog** is primarily the discovery and metadata layer that helps people understand what data exists and how it should be interpreted and accessed.

```text
Data Platform
├── Storage
├── Processing
├── Query
├── Streaming
├── Governance
├── Security
├── Observability
└── Catalog / discovery

Data Catalog
├── Technical metadata
├── Business metadata
├── Ownership
├── Definitions
├── Glossaries
├── Search
├── Classification
└── Discovery context
```

A catalog does not automatically replace S3, Glue, Athena, Redshift, EMR, or Lake Formation.

A useful mental model is:

```text
Catalog = "What exists and what does it mean?"
Platform = "How is it stored, processed, governed, served, and operated?"

## 6. Technical Metadata

Technical metadata describes how a data asset is structured and operated.

For:

```text
gold.daily_revenue
```

technical metadata might include:

```text
Columns:
  date        DATE
  region      STRING
  revenue     DECIMAL
  currency    STRING

Storage:
  S3 / Iceberg

Partition:
  business_date

Format:
  Parquet

Ownering system:
  Glue Data Catalog

Query engine:
  Athena
```

Technical metadata answers:

> How is the data represented?

Typical fields include:

- database;
- schema;
- table;
- columns;
- data types;
- partitions;
- locations;
- table properties;
- source system;
- timestamps;
- technical lineage;
- quality indicators;
- storage format.

## 7. Business Metadata

Business metadata explains what the data means and how the organization should use it.

For `gold.daily_revenue`:

```text
Owner: Finance Data Team
Definition: Daily recognized revenue
Business domain: Finance
Classification: Internal
Refresh: Daily
Quality: Certified
Business criticality: High
SLA: Available by 06:00 UTC
```

Mental model:

```text
Technical metadata
= How the data is structured.

Business metadata
= What the data means.
```

Both are required for enterprise discovery.

A technically perfect catalog can still be operationally weak if users cannot answer:

- What does this metric mean?
- Who owns it?
- Is it trustworthy?
- How often does it refresh?
- Is it sensitive?
- Can I use it for this business purpose?
- Which glossary definition applies?

## 8. Business Glossaries

A business glossary provides shared definitions for business concepts.

Example:

```text
Revenue
= Recognized monetary value associated with completed business transactions.

Customer
= An entity with an active commercial relationship with the organization.
```

Glossaries reduce semantic drift.

Without a glossary:

```text
Team A: Revenue = booked revenue
Team B: Revenue = invoiced revenue
Team C: Revenue = cash collected
```

An analyst may produce a technically correct query that is business-wrong.

Glossaries matter to:

- analysts;
- Data Engineers;
- governance teams;
- finance;
- ML teams;
- AI assistants;
- enterprise search;
- data products.

A glossary is not a replacement for a schema. It is a semantic layer of business meaning attached to discoverable assets.

## 9. Data Products

A data product is a business-consumable, governed data asset or package with an owner, meaning, quality expectations, documentation, discoverability, and an access model.

A useful progression is:

```text
Raw table
  ↓
Curated dataset
  ↓
Business metadata
  ↓
Owner
  ↓
Quality expectations
  ↓
Documentation
  ↓
Governed access
  ↓
Data Product
```

A data product should answer:

- Who owns it?
- Who consumes it?
- What business problem does it solve?
- What does it mean?
- How reliable is it?
- How often is it refreshed?
- What are the access constraints?
- How does it evolve?
- What happens when it is deprecated?

The phrase "data product" is a governance and consumption concept. It is not simply another file format, table type, or database engine.

## 10. Dataset vs Data Product

| Dataset | Data Product |
|---|---|
| Technical data object | Business-consumable governed asset |
| Schema | Schema + meaning |
| Storage/query location | Discoverability + consumption workflow |
| May lack owner | Explicit owner |
| May lack SLA | Quality/SLA expectations |
| Technical metadata | Technical + business metadata |
| May be difficult to find | Designed for reuse |
| May be producer-centric | Consumer-oriented |

A table can be useful without being a mature data product.

A mature data product makes ownership, semantics, quality, access, and lifecycle explicit.

## 11. Amazon DataZone — What Problem Does It Solve?

Amazon DataZone provides a governed discovery and data-sharing experience around organizational data.

Start with the simple explanation:

> DataZone helps people find useful data, understand what it means, publish reusable data assets, and request governed access.

The broader capability set includes:

- business data catalog;
- discovery;
- business metadata;
- glossaries;
- metadata forms;
- projects;
- data products;
- publishing;
- subscriptions;
- approval;
- governed consumption.

AWS documentation describes domains as organizational boundaries for assets, users, and projects, and describes projects as collaboration units for publishing, discovering, subscribing to, and consuming data. citeturn0search4

Do not reduce DataZone to "another catalog." Its value is the workflow around discovery, business context, data products, and governed sharing.

## 12. DataZone Core Concepts

The core vocabulary to master is:

```text
Domain
Project
Asset
Business Catalog
Metadata Form
Glossary
Data Product
Publication
Subscription
Approval
Environment
```

Think of the system as:

```text
Domain
  ├── Projects
  │     ├── Producer
  │     └── Consumer
  ├── Catalog
  │     ├── Assets
  │     └── Data Products
  ├── Glossaries
  └── Metadata Forms
```

The exact product surface evolves, so distinguish stable architectural concepts from current implementation details.

## 13. DataZone Domains

A domain is a major organizational boundary.

It can organize:

- assets;
- users;
- projects;
- business context;
- governance;
- data sources.

A conceptual organization could be:

```text
Enterprise Data Domain
├── Finance
├── Customer
├── Sales
└── Operations
```

But this is an example, not a required AWS organizational pattern.

AWS documents that an organization may use one domain for an enterprise or multiple domains for different business units depending on its data and analytics needs. citeturn0search4

Decision question:

> Does this organization need one governed data community or several independently governed communities?

Avoid creating domains merely because the organization has many teams. Domain design should follow governance, ownership, identity, lifecycle, and operating-model requirements.

## 14. DataZone Projects

A DataZone project is a collaboration unit around a business use case.

A simplified model:

```text
Project A = Producer
Project B = Analyst Consumer
Project C = ML Consumer
```

Projects can participate in:

- publishing;
- discovering;
- subscribing;
- consuming;
- creating assets;
- managing members;
- using project environments.

AWS describes projects as groups of users collaborating around business use cases and identifies roles such as owners, contributors, consumers, stewards, and viewers. citeturn0search4

A key idea:

> A project is not merely a folder. It is part of the collaboration and governed consumption model.

## 15. Business Data Catalog

The business data catalog is the discovery layer where users find and understand published assets.

A conceptual pipeline is:

```text
Technical Dataset
  ↓
Cataloged Asset
  ↓
Business Metadata
  ↓
Data Product
  ↓
Discoverable Data
```

The catalog can expose:

- asset name;
- description;
- schema;
- glossary terms;
- ownership;
- metadata forms;
- quality indicators;
- business context.

AWS documentation states that project inventory assets are not automatically discoverable by all domain users; assets need to be published to the business catalog for broader domain discovery. citeturn0search6turn0search18

Critical distinction:

```text
Discover
≠
Access
```

## 16. Metadata Forms

Metadata forms provide structured fields that augment asset metadata.

Example:

```text
Owner
Domain
Sensitivity
Business Definition
Refresh Frequency
Data Quality
SLA
Classification
```

Structured metadata is preferable to relying exclusively on free-text descriptions because governance teams can standardize fields and make important context consistently searchable.

AWS documents metadata forms as extensible structures for adding business context and improving consistency across assets. Current forms support field types including boolean, date, decimal, integer, string, and business-glossary values. citeturn0search5turn0search8

Design principle:

```text
Free text = useful narrative
Structured metadata = governable information
```

Use both.

## 17. Metadata Enforcement

Enterprise governance often requires more than asking producers to fill out fields.

A stronger pattern is:

```text
Publishing request
  ↓
Required metadata rules
  ↓
Validate required forms
  ↓
Publish only when requirements are satisfied
```

Current AWS documentation describes metadata enforcement rules that can require metadata forms for data asset/product publishing and can also require metadata for subscription requests. citeturn0search19turn0search14

This turns metadata from optional documentation into an operating control.

## 18. Publishing

Publishing creates the transition from project inventory to broader discovery.

Conceptually:

```text
Producer Project
  ↓
Inventory Asset
  ↓
Curate Metadata
  ↓
Add Glossary / Forms
  ↓
Publish
  ↓
Business Catalog
  ↓
Consumer Discovery
```

AWS documentation states that inventory assets are project-scoped until explicitly published and that the latest published version is the active discovery version. citeturn0search6

Operational implication:

> Updating the underlying data or metadata does not automatically mean every consumer sees the intended published version. Understand the publishing lifecycle.

## 19. Data Products in DataZone

Amazon DataZone supports grouping data assets into self-contained data products targeted to business use cases.

Example:

```text
Data Product: Finance Daily Revenue

Assets:
  gold.daily_revenue
  revenue_quality_metrics

Business context:
  Finance
  Daily reporting
  Certified
```

AWS documents data products as packages of assets tailored to business use cases and allows metadata requirements to be enforced for publishing. citeturn0search17

A data product should be treated as a contract-like consumer experience:

```text
Meaning
+ Ownership
+ Quality
+ Metadata
+ Access
+ Lifecycle
= Consumer-ready data product
```

## 20. Subscription Requests

The governed access workflow is central:

```text
Consumer
  ↓
Discover Data Product
  ↓
Inspect Meaning / Owner / Quality
  ↓
Request Subscription
  ↓
Owner / Governance Review
  ↓
Approve or Reject
  ↓
Underlying Access Grant
  ↓
Consumer Uses Data
```

The subscription request can carry business context and may be subject to metadata or governance requirements.

Critical mental model:

```text
Catalog
= Discovery

Subscription
= Governed request

Underlying permissions
= Actual authorization
```

Approval is not conceptually equivalent to "the user can now read everything." The resulting permissions depend on the asset type, target environment, policies, and supported integration.

## 21. What Happens Underneath an Approved Subscription?

Do not imagine DataZone as a separate database that bypasses AWS authorization.

A conceptual flow is:

```text
User
 ↓
DataZone / SageMaker Catalog
 ↓
Subscription request
 ↓
Approval
 ↓
Access-grant workflow
 ↓
Lake Formation / Redshift / supported target
 ↓
Actual authorization
 ↓
Query or consumption
```

Current AWS documentation confirms that DataZone can automatically manage access for supported managed assets, including Lake Formation-managed Glue Data Catalog tables and Redshift tables/views. For unmanaged assets, DataZone can publish an EventBridge event after approval so custom access-grant logic can be invoked. citeturn0search0turn0search2

Therefore:

```text
Discovery layer ≠ authorization layer
```

The exact grant mechanism is asset- and integration-dependent.

## 22. DataZone + Glue Data Catalog

A useful conceptual separation is:

```text
Glue Data Catalog
= Technical metadata foundation

DataZone
= Business discovery + governance + sharing experience
```

Example:

```text
                    DataZone
                       │
          Business discovery / products
                       │
                       ↓
               Glue Data Catalog
                       │
            Technical metadata
                 /      |                      ↓       ↓       ↓
             Athena   Glue     EMR
```

AWS currently documents Glue Data Catalog as a supported source for Unified Studio project catalogs and describes importing technical metadata from Glue databases into a project inventory. citeturn1search9

Do not teach the relationship as a replacement:

> DataZone does not mean "delete Glue Catalog."

It is an experience and governance layer that works with underlying AWS data systems.

## 23. DataZone + Lake Formation

Think:

```text
DataZone
= Who discovers and requests?

Lake Formation
= How is supported data access governed?
```

Lake Formation contributes:

- resource permissions;
- fine-grained access;
- data filters;
- governance;
- cross-account sharing mechanisms;
- data-location controls.

Current DataZone documentation states that approved subscriptions to supported Glue assets can be materialized through Lake Formation, and that row/column filters can be translated into Lake Formation data cell filters. citeturn0search15turn0search1

Do not repeat the entire Lake Formation module here. The objective is architectural integration.

## 24. DataZone + Athena

Athena is the query engine; DataZone is the discovery/governance experience around data.

Typical journey:

```text
Discover in DataZone
  ↓
Understand metadata
  ↓
Request / receive access
  ↓
Query through Athena
  ↓
Read governed S3 / Iceberg data
```

Therefore:

```text
DataZone does not replace Athena.
```

A successful architecture keeps responsibilities clear:

- DataZone: discover, contextualize, request, coordinate governed sharing.
- Lake Formation/IAM: authorize according to the applicable model.
- Athena: execute SQL.
- S3/Iceberg: store the data.

## 25. DataZone + Redshift

For Redshift assets:

```text
DataZone
  ↓
Discover / subscribe
  ↓
Redshift access workflow
  ↓
Query
```

Current AWS documentation says that for supported managed Redshift assets, DataZone can automatically add subscribed assets to project environments and create the required grants/datashares depending on the source and target topology. citeturn0search2

Do not confuse:

- catalog discovery;
- Redshift database permissions;
- datashares;
- project environment configuration.

They are related but distinct layers.

## 26. DataZone + EMR

EMR remains a compute/processing service.

The conceptual relationship is:

```text
DataZone
  ↓
Discover governed data product
  ↓
Project/environment
  ↓
Use approved data
  ↓
EMR processing
```

The catalog does not become the compute engine.

For a data engineer, the important question is:

> How can a governed data product become a trusted input to a Spark workload without bypassing the enterprise access model?

That requires aligning the catalog, identity, permissions, storage/catalog metadata, and compute environment.

## 27. SageMaker Unified Studio — Fundamentals

Amazon SageMaker Unified Studio is a broader development experience for data, analytics, AI, and ML.

AWS currently describes it as a browser-based web application for analytics and AI work, and AWS documentation states that Unified Studio brings together AWS data, analytics, AI, and ML services in a single development experience. citeturn1search2turn1search1

For this roadmap, the correct lens is:

```text
Data Engineering
+
Analytics
+
Data Discovery
+
Governed Data
+
ML / AI
=
Unified working experience
```

This is not a request to learn every SageMaker AI feature.

The Data Engineering questions are:

- Where is governed data discovered?
- How is it accessed?
- How do projects organize work?
- How do data and AI teams collaborate?
- Which underlying AWS services execute the work?

## 28. SageMaker Catalog and Unified Studio

AWS currently documents Amazon SageMaker Catalog as being built on Amazon DataZone and accessible from SageMaker Unified Studio. It describes the catalog as a place where published assets from projects can be discovered and subscribed to. citeturn1search1turn1search2

This gives a modern mental model:

```text
Amazon DataZone
      ↓
SageMaker Catalog
      ↓
SageMaker Unified Studio
      ↓
Data + Analytics + AI/ML workflows
```

Avoid treating DataZone and Unified Studio as unrelated competing products.

A better distinction is:

```text
DataZone
= governance/catalog/data-sharing foundation

Unified Studio
= broader user/developer experience spanning data, analytics, AI, and ML
```

Product naming and capabilities evolve, so verify current AWS documentation before making implementation claims.

## 29. Unified Studio and the AWS Data Stack

Conceptual architecture:

```text
                  SageMaker Unified Studio
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
   Data Engineering    Analytics         AI / ML
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                    Governed Data Layer
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
             S3          Athena       Redshift
              │            │            │
              └────────────┼────────────┘
                           ↓
                  Glue / Catalog Layer
                           ↓
                    Lake Formation
```

This is an architectural model, not a claim that every box is implemented by one product or integrated in exactly the same way in every Region/account.

AWS currently documents an "All capabilities" project profile that can enable analytics and ML/generative-AI workflows involving services including EMR, Glue, Athena, SageMaker AI, Bedrock, and SageMaker Lakehouse. citeturn0search16

## 30. Technical Catalog vs Business Catalog

| Technical Catalog | Business Catalog |
|---|---|
| Schema | Business meaning |
| Columns | Definitions |
| Partitions | Ownership |
| Data types | Glossary |
| Storage location | Business domain |
| Table properties | Data product context |
| Technical metadata | Technical + business metadata |
| Operational details | Consumer interpretation |

Enterprise platforms need both.

A technical catalog answers:

> "What is this object?"

A business catalog answers:

> "Why should I trust or use this object, what does it mean, and who owns it?"

## 31. End-to-End Discovery Example

Suppose a user needs:

```text
Finance daily revenue
```

The desired workflow is:

```text
Search
 ↓
Discover gold.daily_revenue
 ↓
Read business definition
 ↓
Inspect owner
 ↓
Inspect glossary terms
 ↓
Inspect quality information
 ↓
Request subscription
 ↓
Owner / governance approves
 ↓
Underlying permissions are established
 ↓
Query with Athena or another supported consumer
```

This workflow reduces the common enterprise failure mode:

> "I found a table with the right column names, but I do not know whether it represents the business concept I need."

The catalog makes semantic and ownership context part of the discovery process.

## 32. Hands-On Lab 1 — Publish gold.daily_revenue

Objective: turn a curated dataset into a discoverable data product.

Use:

```text
gold.daily_revenue
```

Required business metadata:

```text
Owner: Finance Data Team
Domain: Finance
Definition: Daily recognized revenue
Classification: Internal
Refresh: Daily
Quality: Certified
Business criticality: High
```

Tasks:

1. Create or identify the curated dataset.
2. Register it as project inventory.
3. Add a meaningful business description.
4. Attach glossary terms.
5. Add metadata-form values.
6. Publish the asset/data product.
7. Search for it as a consumer.
8. Record the producer and consumer projects.
9. Record what access path is expected.
10. Document what is discovery metadata versus authorization.

Success criterion:

> Another engineer can understand the asset without asking the producer what it means.

## 33. Hands-On Lab 2 — Publish a Second Data Product

Publish:

```text
gold.customer_lifetime_value
```

Required metadata:

- owner;
- business domain;
- business definition;
- glossary terms;
- sensitivity/classification;
- refresh expectation;
- quality expectation;
- consumer use cases;
- deprecation owner.

Compare it with `gold.daily_revenue`.

Questions:

1. Are the definitions precise?
2. Are ownership fields consistent?
3. Are glossary terms reusable?
4. Could a new analyst discover both products without tribal knowledge?
5. What metadata should be mandatory rather than optional?

## 34. Hands-On Lab 3 — Producer and Consumer Projects

Create the logical model:

```text
Project A
= Finance Data Producer

Project B
= Analytics Consumer
```

Workflow:

```text
Producer
 ↓
Publishes data product

Consumer
 ↓
Discovers product
 ↓
Requests access
 ↓
Producer / governance approves
 ↓
Underlying permissions
 ↓
Consumer queries
```

Record:

- project ownership;
- member roles;
- asset ownership;
- subscription requester;
- approver;
- target environment;
- access grant mechanism;
- verification evidence.

## 35. Hands-On Lab 4 — Subscription Workflow

Run the subscription lifecycle.

```text
1. Search
2. Inspect asset
3. Inspect owner
4. Inspect business metadata
5. Request subscription
6. Provide business justification
7. Approve or reject
8. Verify grant
9. Consume
10. Record audit evidence
11. Revoke or deprecate when appropriate
```

AWS documents subscription requests and approvals as part of the DataZone data-sharing model. Supported managed assets can have access grants automatically managed; unmanaged assets require a custom grant path. citeturn0search0turn0search15

Your lab report must explicitly identify where the DataZone workflow ends and where the underlying authorization system begins.

## 36. Hands-On Lab 5 — Athena Verification

After a successful subscription:

```sql
SELECT *
FROM gold.daily_revenue
LIMIT 10;
```

The learner must explain:

```text
DataZone
= discovery / business context / subscription

Lake Formation / IAM
= authorization, where applicable

Athena
= query execution

S3 / Iceberg
= data storage
```

Verification questions:

- Can the consumer discover the asset?
- Is the subscription approved?
- Is the expected permission present?
- Can Athena resolve the catalog object?
- Can the underlying storage be read?
- Is access broader than intended?

## 37. Hands-On Lab 6 — Governance Inspection

Inspect:

```text
Who owns the dataset?
What metadata exists?
Which glossary terms apply?
What permissions exist?
Which project is the consumer?
Which role or identity executes the query?
Which service enforces authorization?
What audit evidence exists?
```

Compare:

```text
Metadata visibility
vs
Data authorization
```

Do not treat a successful search result as proof of data access.

## 38. Hands-On Lab 7 — Compare with Self-Built Governance

Compare:

```text
Self-built:
Glue Catalog
+ Lake Formation
+ Athena
+ custom portal
+ custom approval workflow

DataZone:
AWS catalog/governance/data-sharing experience
+ AWS data services

Open-source:
OpenMetadata / DataHub
+ AWS data services
```

Score each from 1–5 for:

- discovery;
- metadata;
- glossary;
- data products;
- approval workflow;
- automation;
- AWS integration;
- customization;
- operational burden;
- portability;
- lock-in;
- cost;
- team fit.

## 39. OpenMetadata

OpenMetadata is an open-source metadata platform used for discovery, metadata management, lineage, governance, and integration across data systems.

For this roadmap, study it as an architectural alternative rather than as a full implementation course.

Questions to ask:

- Who operates it?
- Which connectors are required?
- How does metadata ingestion work?
- How does lineage work?
- How are business glossaries managed?
- How are access policies enforced?
- How much AWS-native integration is available?
- How much engineering is required to connect authorization to the catalog?

Potential strengths:

- extensibility;
- open ecosystem;
- cross-platform orientation;
- control over deployment.

Potential trade-offs:

- operational responsibility;
- integration engineering;
- custom governance workflows;
- separate platform lifecycle.

## 40. DataHub

DataHub is another metadata platform used for discovery, metadata, lineage, governance, and data-system integration.

Evaluate it using the same framework:

```text
Metadata
Discovery
Lineage
Glossary
Governance
Connectors
Identity
Authorization integration
Operations
Extensibility
Multi-cloud
Lock-in
Cost
```

Do not compare feature checkboxes without understanding the operating model.

The real question is:

> Who will own the metadata platform and the integrations that make the metadata trustworthy?

## 41. Unity Catalog

Unity Catalog is a governance/catalog layer associated with the Databricks ecosystem.

At overview level, focus on:

- centralized governance;
- catalogs;
- schemas;
- tables;
- permissions;
- discovery;
- cross-workspace/platform governance concepts.

Do not claim:

```text
DataZone = Unity Catalog
```

A better statement is:

> They overlap in data discovery and governance responsibilities, but they sit inside different platform architectures and operating models.

Compare the surrounding platform, not just the catalog UI.

## 42. Comparison Matrix

| Capability | DataZone | Unified Studio / SageMaker Catalog | Glue Catalog | Lake Formation | OpenMetadata | DataHub | Unity Catalog |
|---|---|---|---|---|---|---|---|
| Technical metadata | Yes / integrated | Yes | Core capability | Uses catalog metadata | Yes | Yes | Yes |
| Business metadata | Yes | Yes | Limited compared with governance layer | Not its primary role | Yes | Yes | Yes |
| Business glossary | Yes | Yes | Not primary role | Not primary role | Yes | Yes | Yes |
| Data discovery | Yes | Yes | Technical discovery | Not primary UX | Yes | Yes | Yes |
| Subscription workflow | Yes | Yes | No | Permission layer | Platform-dependent | Platform-dependent | Platform-dependent |
| Fine-grained authorization | Coordinates supported controls | Coordinates supported controls | No by itself | Yes | Usually integrates rather than replaces source authorization | Usually integrates rather than replaces source authorization | Yes within supported platform |
| Data products | Yes | Yes | No | No | Platform-dependent | Platform-dependent | Related governance concepts |
| AWS-native | Yes | Yes | Yes | Yes | Integrates with AWS | Integrates with AWS | Databricks-native |
| Open-source | No | No | No | No | Yes | Yes | No |
| Multi-platform | Strong AWS orientation | AWS-oriented unified experience | AWS-oriented | AWS-oriented | Strong | Strong | Strong within Databricks architecture |
| ML/AI integration | Increasingly integrated | Core part of experience | Not primary | Not primary | Integration-driven | Integration-driven | Strong in Databricks ecosystem |
| Customization | Managed service constraints | Managed experience constraints | Service-level | Service-level | High | High | Managed platform constraints |
| Operational burden | Lower service-management burden | Lower service-management burden | Lower service-management burden | Lower service-management burden | Higher self-managed/integration burden | Higher self-managed/integration burden | Platform-managed |
| Lock-in consideration | AWS service model | AWS/SageMaker ecosystem | AWS | AWS | Lower product lock-in, higher operating burden | Lower product lock-in, higher operating burden | Databricks ecosystem |

**Important:** capability boundaries vary by release, integration, Region, and platform configuration. Treat this matrix as an architecture orientation, not a contract. Verify current product documentation before making procurement or implementation decisions.

## 43. DataZone vs Composed AWS Services

### Option A — Managed unified experience

```text
DataZone / SageMaker Catalog
+
AWS data services
```

Potential benefits:

- integrated discovery;
- business metadata;
- data products;
- subscription workflow;
- less custom portal engineering;
- AWS-native integration.

Potential trade-offs:

- AWS dependency;
- product evolution;
- customization constraints;
- service-specific integration limits.

### Option B — Compose services

```text
Glue Catalog
+
Lake Formation
+
Athena
+
Redshift
+
Custom portal
+
Custom approval workflow
```

Potential benefits:

- maximum control;
- custom UX;
- custom business process;
- explicit architecture.

Trade-offs:

- more engineering;
- more maintenance;
- more governance glue code;
- more operational responsibility;
- custom authorization integration.

Do not declare one universally better.

## 44. Adoption Framework

Evaluate an adoption decision using:

```text
Team Size
Governance Maturity
Data Producers
Data Consumers
AWS Footprint
Multi-cloud Requirement
Open-source Strategy
Customization Requirement
Compliance
Glossary Requirements
Approval Complexity
AI/ML Integration
Operational Capacity
Budget
Vendor Lock-in
```

Score each factor from 1–5 and document the reason.

Example decision record:

```text
AWS footprint: 5
Governance need: 5
Multi-cloud: 1
Customization: 2
Operational capacity: 3
AI/ML integration: 5
Compliance: 4

Recommendation:
Evaluate the AWS managed/unified path first.
Validate missing requirements before committing.
```

The output must be a reasoned decision, not a product preference.

## 45. Small AWS-Native Team

Likely characteristics:

- few producers;
- few consumers;
- strong AWS footprint;
- limited platform engineering capacity;
- moderate governance needs.

A managed AWS experience can reduce custom portal and workflow engineering.

Questions:

- Can the service cover required discovery?
- Is the approval workflow sufficient?
- Are required permissions supported?
- Is the organization comfortable with AWS coupling?

If yes, the managed path is often worth evaluating before building a custom catalog.

## 46. Medium Enterprise

Typical characteristics:

- many producers;
- multiple business domains;
- growing governance requirements;
- increasing data-product adoption;
- moderate platform team.

Evaluate:

- domain boundaries;
- ownership;
- metadata standards;
- approval policies;
- cross-account access;
- cost;
- integration with existing catalog tooling.

A hybrid model may be appropriate: managed AWS capabilities for AWS-native assets plus open metadata/integration where business requirements demand it.

## 47. Large Regulated Enterprise

Priorities may include:

- segregation of duties;
- formal ownership;
- auditability;
- PII classification;
- data residency;
- fine-grained authorization;
- approval evidence;
- policy enforcement;
- lineage;
- retention;
- multi-account governance.

Do not select a catalog because it looks convenient.

Perform:

```text
Control mapping
+
Access-model validation
+
Audit validation
+
Data-residency review
+
Integration testing
+
Operational ownership
```

The catalog itself is only one control in the system.

## 48. Multi-Cloud Enterprise

A multi-cloud organization should explicitly test portability.

Questions:

- Is AWS only one of several major platforms?
- Must users search across clouds?
- Is metadata already centralized elsewhere?
- Are business glossaries enterprise-wide?
- Can authorization remain native to each platform?
- Can metadata be exported?
- How will lineage span platforms?

A common architecture is:

```text
Enterprise Metadata / Governance
          ↓
Cloud-specific enforcement
  ┌───────┼────────┐
 AWS    Azure     GCP
```

A managed AWS catalog may still be useful inside AWS, but it should not automatically be declared the enterprise-wide system of record.

## 49. AI-Heavy Organization

For AI-heavy organizations, the catalog becomes especially important because AI systems need trusted data discovery.

A conceptual flow:

```text
AI Agent
  ↓
Business intent
  ↓
Semantic discovery
  ↓
Business glossary
  ↓
Data product
  ↓
Access policy
  ↓
Approved query
  ↓
Athena / Redshift / other engine
  ↓
Answer
```

Security principle:

> An AI agent should not gain access to data simply because it can discover the dataset.

Discovery and authorization remain separate controls.

Better metadata can support:

- semantic search;
- retrieval;
- enterprise assistants;
- agent tool selection;
- feature discovery;
- analytics automation.

Do not claim that a catalog automatically makes an AI agent trustworthy. The agent still needs identity, authorization, query controls, auditing, validation, and safe execution.

## 50. Lock-In Analysis

Lock-in has multiple dimensions:

```text
API lock-in
Metadata lock-in
Governance workflow lock-in
Identity integration lock-in
Data storage lock-in
User-experience lock-in
```

Mitigation strategies:

- open table formats where appropriate;
- documented metadata standards;
- exportable metadata;
- stable business glossary definitions;
- infrastructure as code;
- clear ownership;
- decoupled authorization where practical;
- integration contracts;
- portability testing.

No managed platform is completely lock-in free.

The correct question is:

> Which dependencies are intentional, valuable, and reversible enough for our business?

## 51. Enterprise Governance Model

A realistic operating model:

```text
Enterprise Data Governance
│
├── Data Domains
│   ├── Finance
│   ├── Customer
│   ├── Sales
│   └── Operations
│
├── Data Products
│   ├── Daily Revenue
│   ├── Customer 360
│   └── Orders
│
├── Owners
│
├── Business Glossary
│
├── Quality Expectations
│
├── Security Policies
│
└── Access Policies
```

Roles:

- **Domain owner:** accountable for a business area.
- **Data product owner:** accountable for a specific product.
- **Data steward:** maintains semantics and governance quality.
- **Platform owner:** operates the data platform.
- **Security team:** establishes security controls.
- **Consumer:** uses the data within approved purposes.

## 52. Data Product Lifecycle

A mature lifecycle is:

```text
Create
 ↓
Document
 ↓
Classify
 ↓
Validate
 ↓
Publish
 ↓
Discover
 ↓
Subscribe
 ↓
Approve
 ↓
Consume
 ↓
Monitor
 ↓
Update
 ↓
Deprecate
```

At each stage ask:

- Who owns it?
- What metadata is required?
- What quality checks apply?
- What changes are allowed?
- How are consumers notified?
- How are permissions revoked?
- What happens to downstream pipelines?

Data products need lifecycle management just like software products.

## 53. Business Metadata + AI

Business metadata is valuable to AI systems because natural-language intent often maps to business concepts rather than physical table names.

Example:

```text
User:
"Show monthly recognized revenue."

        ↓

Business glossary:
"recognized revenue"

        ↓

Data product:
gold.daily_revenue

        ↓

Governed access

        ↓

SQL generation

        ↓

Athena / Redshift

        ↓

Validated answer
```

The metadata layer can help an AI system narrow the search space.

But an AI system must still validate:

- identity;
- authorization;
- business definition;
- freshness;
- quality;
- query correctness;
- sensitive-data policy.

## 54. Current AWS Product Evolution

This topic is unusually sensitive to product evolution.

Before implementing exact behavior, verify current official documentation for:

- DataZone domains;
- projects;
- domain units;
- assets;
- data products;
- metadata forms;
- glossaries;
- subscriptions;
- access grants;
- Glue integration;
- Lake Formation integration;
- Redshift integration;
- SageMaker Catalog;
- Unified Studio;
- project profiles;
- environments;
- regional availability;
- CLI/API operations;
- Terraform provider support;
- pricing.

Use this classification:

```text
Stable architectural concept
= Safe to teach as a durable mental model.

Current implementation
= Verify against current documentation.

Version / Region / configuration dependent
= Verify before deployment.
```

Never fabricate an API, CLI command, Terraform resource, permission, integration, price, or regional capability.

## 55. Verified AWS CLI Examples

The AWS CLI currently exposes the `datazone` service namespace.

Example: list domains.

```bash
aws datazone list-domains   --region <region>
```

AWS documents this as a paginated operation. citeturn1search5

Example: create a domain skeleton.

```bash
aws datazone create-domain   --name "<domain-name>"   --description "<description>"   --region <region>
```

The current CLI reference documents options including single sign-on configuration, KMS key identifier, tags, and domain version. citeturn1search3

Do not copy these commands into production unchanged. First confirm:

- account;
- Region;
- identity;
- IAM permissions;
- SSO configuration;
- KMS policy;
- domain version;
- current CLI version.

For commands not verified in current AWS CLI documentation, use placeholders rather than inventing syntax.

## 56. boto3 Example — List DataZone Domains

Use the verified service client pattern:

```python
import boto3

client = boto3.client("datazone", region_name="<region>")

response = client.list_domains()

for domain in response.get("items", []):
    print(domain["id"], domain["name"], domain["status"])
```

Operational considerations:

- use IAM roles or identity federation;
- do not hard-code credentials;
- handle pagination;
- set the correct Region;
- handle `ClientError`;
- log request context without exposing secrets;
- apply least privilege.

The current DataZone API/CLI exposes domain listing and pagination. citeturn1search5

Before using a method in production, verify the current boto3 service model installed in the environment.

## 57. boto3 Example — Project API Awareness

The current DataZone API includes `CreateProject`.

Conceptual request:

```python
import boto3

client = boto3.client("datazone", region_name="<region>")

response = client.create_project(
    domainIdentifier="<domain-id>",
    name="finance-analytics",
    description="Finance analytics producer/consumer collaboration"
)

print(response["id"])
```

AWS currently documents request fields such as `domainIdentifier`, `name`, `description`, `domainUnitId`, glossary terms, membership assignments, project profile, execution role, and user parameters. citeturn1search7

Treat exact request fields as API-version-sensitive. Validate the installed SDK before execution.

## 58. Terraform / IaC Awareness

Infrastructure as code is part of the G3 operating standard.

Current AWS provider documentation exposes DataZone resources including:

- `aws_datazone_project`;
- `aws_datazone_environment`;
- environment blueprint configuration;
- additional DataZone resource types.

For example, the current provider documents `aws_datazone_project` with a domain identifier and name. citeturn1search0

A minimal pattern is:

```hcl
resource "aws_datazone_project" "finance" {
  domain_identifier = var.datazone_domain_id
  name              = "finance-analytics"
  description       = "Finance analytics project"
}
```

Before applying:

```text
terraform init
terraform validate
terraform plan
```

Then inspect:

- provider version;
- Region;
- account;
- IAM;
- domain dependencies;
- project lifecycle;
- deletion behavior.

Provider support is evolving. Verify current provider documentation before introducing a resource into a production module.

## 59. Security Model

Security must be layered:

```text
Identity
  ↓
Project membership
  ↓
Catalog visibility
  ↓
Subscription policy
  ↓
Underlying authorization
  ↓
Storage / query engine
```

Cover:

- IAM;
- IAM Identity Center;
- Lake Formation;
- Redshift permissions;
- resource policies;
- least privilege;
- PII classification;
- sensitive metadata;
- cross-account access;
- audit logging;
- subscription approval;
- revocation.

Critical principle:

```text
Discoverability
≠
Authorization
```

Also:

```text
Business metadata
can itself be sensitive.
```

For example, the existence of a dataset called `merger_target_companies` may itself be confidential.

## 60. Cost Awareness

Cost has multiple layers:

```text
Catalog / governance service cost
+
Underlying storage
+
Query cost
+
Compute
+
Network
+
Operations
+
Custom engineering
+
Human approval effort
```

Do not use static price numbers in this module.

For exact current pricing:

> Verify AWS pricing for the target Region, account, workload, and product version.

Also compare total cost of ownership:

```text
Managed platform TCO
vs
Custom platform TCO
vs
Open-source platform TCO
```

Custom engineering is not free merely because the catalog software itself is open source.

## 61. Break/Fix — Dataset Discoverable but Inaccessible

**Symptom:** The consumer can find the dataset but cannot query it.

Investigation:

```text
1. Confirm asset is published.
2. Confirm subscription exists.
3. Confirm subscription status.
4. Confirm approval.
5. Identify asset type.
6. Identify managed vs unmanaged path.
7. Inspect Lake Formation / Redshift permissions.
8. Inspect IAM.
9. Inspect query engine.
10. Inspect S3 / network / KMS dependencies.
```

Likely causes:

- approval never completed;
- wrong subscriber project;
- unsupported asset integration;
- missing Lake Formation grant;
- missing Redshift permission;
- IAM denial;
- KMS denial;
- underlying storage issue.

Fix only after identifying the failing layer.

## 62. Break/Fix — Subscription Approved but Query Fails

**Symptom:** Subscription status says approved, but Athena or Redshift returns an authorization or object error.

Check:

```text
DataZone
  ↓
Subscription state
  ↓
Grant materialization
  ↓
Glue Catalog / Redshift object
  ↓
Lake Formation / Redshift permissions
  ↓
IAM
  ↓
S3 / network / KMS
  ↓
Query engine
```

For supported managed Glue assets, current AWS documentation states that DataZone can grant access through Lake Formation after approval. citeturn0search15

For Redshift, current documentation describes creation of necessary grants/datashares depending on topology. citeturn0search2

Do not assume "approved" means every underlying permission is healthy.

## 63. Break/Fix — Missing Business Metadata

**Symptom:** Dataset exists but users cannot understand it.

Check:

- metadata forms;
- required fields;
- publishing process;
- producer ownership;
- glossary assignment;
- publishing metadata rules;
- asset version;
- whether the updated version was republished.

Prevention:

```text
Required metadata
+
Publishing gate
+
Owner accountability
+
Periodic metadata review
```

## 64. Break/Fix — Incorrect Glossary Definition

**Symptom:** Two teams interpret a metric differently.

Investigation:

```text
1. Identify glossary owner.
2. Find conflicting definitions.
3. Identify affected data products.
4. Identify downstream consumers.
5. Correct definition.
6. Review impacted products.
7. Communicate semantic change.
8. Version or document the decision.
```

Prevention:

- domain ownership;
- glossary stewardship;
- change review;
- business approval;
- consumer communication.

## 65. Break/Fix — Producer Rejects Access

A rejection is not automatically a platform failure.

Investigate:

- business purpose;
- data classification;
- purpose limitation;
- regulatory constraints;
- ownership policy;
- data product terms;
- escalation path.

The platform should make the decision auditable.

Do not bypass governance by granting direct storage permissions merely because the subscription was rejected.

## 66. Break/Fix — Feature Differs from Documentation

When behavior differs from expectations:

```text
Check current AWS documentation
        ↓
Verify Region
        ↓
Verify service/domain version
        ↓
Verify account configuration
        ↓
Verify project/environment configuration
        ↓
Verify permissions
        ↓
Reproduce with minimal test
```

Never work around a suspected product difference by inventing an undocumented API or permission path.

## 67. Break/Fix — Unified Studio Adoption Problem

Scenario:

```text
Small Data Engineering team
+
Multi-cloud enterprise
+
Heavy customization
+
Strong governance requirements
```

Question:

> Should the organization adopt the AWS unified experience?

Answer using evidence:

1. AWS footprint.
2. Cross-cloud requirements.
3. Existing catalog.
4. Required custom workflows.
5. Team capacity.
6. Governance controls.
7. AI/ML integration needs.
8. Migration cost.
9. Lock-in.
10. Exit strategy.

The correct answer may be "adopt," "pilot," "hybrid," or "do not adopt yet.

## 68. Runbook — Dataset Cannot Be Discovered

### Symptom
Consumer cannot find the expected asset.

### Impact
Consumer cannot evaluate or request the data product.

### Evidence
- asset ID;
- project;
- publication state;
- domain;
- metadata;
- catalog search;
- current asset version.

### Investigation
1. Confirm asset exists in project inventory.
2. Confirm required metadata.
3. Confirm publication.
4. Confirm domain.
5. Confirm user/project visibility.
6. Confirm asset type and integration.

### Likely causes
- not published;
- wrong domain;
- stale publication;
- incomplete metadata;
- search scope mismatch.

### Verification
Search as the intended consumer identity.

### Prevention
Use publishing gates and metadata standards.

## 69. Runbook — Subscription Unavailable

### Symptom
Consumer sees the asset but cannot complete subscription.

### Investigation
1. Inspect subscription terms.
2. Check required metadata.
3. Check project membership.
4. Check owner configuration.
5. Check asset type.
6. Check environment/subscription target.
7. Check current service documentation.

### Prevention
Document supported subscription paths per asset type and environment.

## 70. Runbook — Subscription Approved but Access Fails

### Evidence
Collect:

- subscription ID/status;
- asset type;
- producer project;
- consumer project;
- target environment;
- Lake Formation grants or Redshift grants;
- IAM identity;
- query error;
- CloudTrail evidence where available.

### Decision
Determine whether the issue is:

```text
Catalog
or
Subscription
or
Grant materialization
or
IAM
or
Data service
or
Storage/network/KMS
```

Fix the first failing layer rather than adding broad permissions.

## 71. Runbook — Permission Mismatch

### Symptom
Consumer has more or less access than intended.

### Investigation
- identify intended scope;
- inspect subscription filters;
- inspect Lake Formation data filters;
- inspect Redshift objects/views;
- inspect IAM;
- inspect direct grants;
- inspect group/project membership.

Current DataZone documentation describes translation of row/column subscription filters into Lake Formation data cell filters or Redshift scoped-down views for supported assets. citeturn0search1

### Prevention
Use least privilege and test both positive and negative access cases.

## 72. Runbook — Data Product Ownership Issue

### Symptom
No clear owner can approve changes or access.

### Investigation
- identify project owner;
- identify domain owner;
- identify business owner;
- inspect product documentation;
- inspect metadata;
- inspect organizational responsibility.

### Prevention
Require owner metadata before publication and establish an escalation path.

## 73. Runbook — Product Deprecation

### Process

```text
Announce deprecation
 ↓
Identify consumers
 ↓
Identify downstream jobs
 ↓
Publish replacement
 ↓
Provide migration guide
 ↓
Monitor remaining consumers
 ↓
Stop new subscriptions
 ↓
Revoke old access
 ↓
Retire product
```

Deprecation is a product-management problem as much as a data-platform problem.

## 74. Runbook — Unified Studio Capability Mismatch

### Symptom
A workflow expected in Unified Studio is unavailable.

### Check
- current documentation;
- Region;
- project profile;
- domain configuration;
- environment;
- service integration;
- account permissions;
- current release.

Do not assume a feature shown in one AWS guide is available identically in every configuration.

## 75. Production Architecture — Governed Data Marketplace

```text
Business Users / Analysts / AI Teams
                 │
                 ↓
        Data Discovery Experience
                 │
        DataZone / SageMaker Catalog
                 │
        ┌────────┴────────┐
        ↓                 ↓
 Business Metadata    Data Products
        │                 │
        └────────┬────────┘
                 ↓
         Subscription Workflow
                 │
        ┌────────┴────────┐
        ↓                 ↓
 Lake Formation      Redshift permissions
        │                 │
        └────────┬────────┘
                 ↓
          Governed Data Access
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
       S3      Athena   Redshift
        │
        ↓
  Glue / technical metadata
```

Unified Studio sits above/beside this as the broader environment for data, analytics, AI, and ML workflows.

Label service integrations as verified or conceptual before implementation.

## 76. Production Architecture — Data Product Operating Model

```text
Domain Owner
    │
    ├── Data Product Owner
    │        │
    │        ├── Dataset
    │        ├── Metadata
    │        ├── Glossary
    │        ├── Quality
    │        └── Access policy
    │
    ↓
Publish
    ↓
Catalog
    ↓
Consumer discovery
    ↓
Subscription
    ↓
Authorization
    ↓
Consumption
    ↓
Quality / usage / lineage monitoring
    ↓
Version / deprecation
```

This architecture makes ownership explicit instead of treating the catalog as a passive database of table names.

## 77. Production Architecture — AI Data Discovery

```text
User / AI Agent
       ↓
Business Intent
       ↓
Catalog Search
       ↓
Glossary / Metadata
       ↓
Candidate Data Products
       ↓
Policy Evaluation
       ↓
Authorized Query
       ↓
Athena / Redshift / Other Engine
       ↓
Validation
       ↓
Answer
```

Security rule:

```text
Search result
≠
Permission to read data
```

For AI agents, enforce authorization at the same or stronger level as for human users.

## 78. Architecture Decision Record — DataZone vs Custom Catalog

### Context
The enterprise needs governed discovery and data-sharing workflows.

### Requirements
- searchable assets;
- business metadata;
- glossary;
- data products;
- subscriptions;
- access governance;
- auditability.

### Alternatives
1. DataZone.
2. Custom portal + AWS services.
3. OpenMetadata/DataHub + AWS services.

### Decision
Complete a weighted evaluation before selecting.

### Security impact
Validate underlying authorization and least privilege.

### Governance impact
Compare ownership and enforcement.

### Cost impact
Include service cost and engineering cost.

### Operational impact
Estimate platform operations.

### Lock-in impact
Document AWS-specific dependencies.

### Consequences
Record what becomes easier and what becomes harder.

## 79. Architecture Decision Record — DataZone vs OpenMetadata/DataHub

### Context
The organization needs enterprise metadata across AWS and potentially non-AWS systems.

### Questions
- How many non-AWS systems?
- Who operates the catalog?
- Is custom connector development acceptable?
- How important is AWS-native subscription workflow?
- Is metadata portability a requirement?

### Decision method
Build a weighted scorecard using:

```text
Discovery 20%
Governance 15%
Integration 15%
Customization 10%
Multi-cloud 15%
Operations 10%
Cost 5%
Lock-in 10%
```

Change weights to match the organization and record why.

## 80. Architecture Decision Record — DataZone vs Unity Catalog

Do not compare only product names.

Compare the surrounding platforms:

```text
AWS data stack
vs
Databricks data stack
```

Evaluate:

- existing cloud footprint;
- existing lakehouse;
- identity;
- governance;
- data sharing;
- workloads;
- AI/ML stack;
- operational model;
- portability.

The decision should follow architecture and organizational reality.

## 81. Architecture Decision Record — Unified Studio Adoption

### Context
The organization wants a common development experience for data, analytics, AI, and ML.

### Requirements
- governed data discovery;
- analytics;
- engineering;
- AI/ML;
- collaboration;
- project isolation;
- security;
- operational simplicity.

### Alternatives
- adopt broadly;
- pilot;
- hybrid;
- continue separate services.

### Decision
Pilot representative workloads before enterprise standardization.

### Consequences
Document benefits, gaps, migration cost, training, lock-in, and operating-model changes.

## 82. Architecture Decision Record — Data Product Governance

Define:

- who can create a product;
- who can publish;
- required metadata;
- required glossary terms;
- quality gates;
- subscription approvers;
- sensitive-data rules;
- deprecation process;
- ownership transfer.

The output should be an operating policy, not only a catalog configuration.

## 83. Senior Interview Questions

1. What problem does DataZone solve that Glue Data Catalog does not?
2. Is DataZone a replacement for Lake Formation?
3. What is the difference between a dataset and a data product?
4. Explain a subscription request.
5. What happens after a subscription is approved?
6. How does DataZone relate to Glue?
7. How does DataZone relate to Lake Formation?
8. How does DataZone relate to Athena?
9. How does DataZone relate to Redshift?
10. What is SageMaker Unified Studio trying to solve?
11. Why is Unified Studio not simply another query engine?
12. DataZone vs OpenMetadata: how would you decide?
13. DataZone vs DataHub: what is the architectural difference that matters?
14. DataZone vs Unity Catalog: why are they not exact equivalents?
15. When would you avoid adopting DataZone?
16. How would you design governed discovery for an enterprise AI platform?
17. How would you prevent an AI agent from using unauthorized data?
18. How would you manage data-product deprecation?
19. How would you prove that a subscription actually grants only intended access?
20. How would you reduce AWS lock-in while still using AWS-native governance?

## 84. Practice Questions — Beginner

1. What is a data catalog?
2. What is technical metadata?
3. What is business metadata?
4. What is a business glossary?
5. What is a data product?
6. What is Amazon DataZone?
7. What is a DataZone domain?
8. What is a DataZone project?
9. What is a metadata form?
10. What is a subscription request?

**Expected outcome:** explain each concept without product jargon first, then with AWS terminology.

## 85. Practice Questions — Intermediate

1. Dataset vs data product?
2. Technical metadata vs business metadata?
3. Why is discovery different from authorization?
4. What happens when a consumer requests a subscription?
5. Why does DataZone integrate with Glue?
6. Why does DataZone integrate with Lake Formation?
7. How does Athena fit into the workflow?
8. How does Redshift fit into the workflow?
9. Why should metadata be structured?
10. Why are data products useful for enterprise reuse?
11. What is the difference between project inventory and published catalog data?
12. Why might an approved subscription still fail at query time?

## 86. Practice Questions — Advanced

1. DataZone vs custom catalog?
2. DataZone vs OpenMetadata?
3. DataZone vs DataHub?
4. DataZone vs Unity Catalog?
5. When should a large enterprise use multiple domains?
6. When should a company remain with composed AWS services?
7. How would you design a governed data marketplace?
8. How would you support AI agents discovering enterprise data?
9. How would you design the authorization boundary?
10. How would you mitigate metadata lock-in?
11. How would you validate a managed subscription workflow?
12. How would you compare total cost of ownership?
13. How would you design data-product ownership?
14. How would you handle a multi-cloud enterprise?
15. How would you design a migration from a custom catalog?

## 87. Reasoning Answers — Selected Advanced Questions

### Q: Is DataZone a replacement for Lake Formation?

**Answer:** No. DataZone provides discovery, metadata, data products, and subscription-oriented workflows. Lake Formation remains an authorization/governance service for supported AWS data-lake resources. Current DataZone documentation explicitly describes approved Glue subscriptions being granted through Lake Formation. citeturn0search15

### Q: Is DataZone a replacement for Glue Data Catalog?

**Answer:** No. Glue provides the technical catalog foundation for many AWS data workflows. DataZone adds business discovery, metadata, data products, and governed sharing around supported assets.

### Q: What happens after subscription approval?

**Answer:** It depends on the asset and integration. For supported managed assets, DataZone can automatically manage grants; for unmanaged assets, it can emit an EventBridge event so custom grant logic can be executed. citeturn0search0

### Q: Are DataZone and Unity Catalog equivalent?

**Answer:** No. They overlap in governance and discovery responsibilities but sit within different platform ecosystems.

### Q: Should every enterprise adopt Unified Studio?

**Answer:** No. Evaluate actual requirements, AWS footprint, governance, customization, multi-cloud needs, operating capacity, and lock-in.

## 88. Decision Tree

```text
Primarily AWS?
│
├── No
│   └── Evaluate enterprise-neutral / multi-platform options
│
└── Yes
    │
    ├── Need governed data discovery?
    │       │
    │       ├── No → Compose only what is required
    │       │
    │       └── Yes
    │            │
    │            ├── Need heavy customization?
    │            │      │
    │            │      ├── Yes → Compare managed + open-source/custom
    │            │      └── No  → Evaluate DataZone / Unified Studio
    │            │
    │            ├── Strong multi-cloud requirement?
    │            │      └── Increase weight for portable metadata
    │            │
    │            └── Strong AI/ML requirement?
    │                   └── Evaluate Unified Studio experience
```

This is a framework, not a hard-coded answer.

## 89. Completion Checklist

### Data Catalog

- [ ] Technical metadata
- [ ] Business metadata
- [ ] Discovery
- [ ] Ownership
- [ ] Glossaries
- [ ] Metadata forms

### DataZone

- [ ] Domains
- [ ] Projects
- [ ] Business catalog
- [ ] Glossaries
- [ ] Metadata forms
- [ ] Data products
- [ ] Publishing
- [ ] Subscription requests
- [ ] Approval
- [ ] Governed access

### AWS Integration

- [ ] Glue Catalog
- [ ] Lake Formation
- [ ] Athena
- [ ] Redshift
- [ ] EMR relationship
- [ ] IAM
- [ ] Governed permissions

### Unified Studio

- [ ] Purpose
- [ ] Data Engineering
- [ ] Analytics
- [ ] ML/AI
- [ ] Catalog/lakehouse relationship
- [ ] Current capability verification

### Platform Strategy

- [ ] DataZone vs custom
- [ ] DataZone vs OpenMetadata
- [ ] DataZone vs DataHub
- [ ] DataZone vs Unity Catalog
- [ ] Lock-in
- [ ] Team size
- [ ] Governance maturity
- [ ] Multi-cloud
- [ ] Cost
- [ ] Operational burden

### Practical

- [ ] Publish `gold.daily_revenue`
- [ ] Publish second dataset
- [ ] Add business metadata
- [ ] Add glossary terms
- [ ] Create producer project
- [ ] Create consumer project
- [ ] Request subscription
- [ ] Approve subscription
- [ ] Inspect permissions
- [ ] Verify Athena access
- [ ] Compare governance approaches
- [ ] Clean up resources

## 90. Final Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---:|---|
| Goal of unified governed data environment | Yes | Sections 1, 4 |
| Amazon DataZone | Yes | Sections 11–20 |
| Domains | Yes | Section 13 |
| Projects | Yes | Section 14 |
| Business data catalog | Yes | Section 15 |
| Glossaries | Yes | Section 8 |
| Metadata forms | Yes | Sections 16–17 |
| Data products | Yes | Sections 9, 19 |
| Publishing | Yes | Section 18 |
| Subscription requests | Yes | Sections 20–21 |
| Approval workflow | Yes | Sections 20, 35 |
| SageMaker Unified Studio | Yes | Sections 27–29 |
| Catalog/lakehouse capabilities | Yes | Sections 28–29 |
| Glue Data Catalog relationship | Yes | Section 22 |
| Lake Formation relationship | Yes | Section 23 |
| Athena relationship | Yes | Section 24 |
| Redshift relationship | Yes | Section 25 |
| EMR relationship | Yes | Section 26 |
| Publishing gold dataset | Yes | Section 32 |
| Business metadata | Yes | Sections 7, 32 |
| Data product ownership | Yes | Sections 9, 51–52 |
| Consumer subscription | Yes | Sections 35 |
| Underlying governed permissions | Yes | Sections 21, 35, 61–72 |
| Lake Formation permissions | Yes | Sections 23, 61–62 |
| Redshift permissions | Yes | Section 25, 62 |
| OpenMetadata comparison | Yes | Section 39 |
| DataHub comparison | Yes | Section 40 |
| Unity Catalog comparison | Yes | Section 41 |
| Adoption decision | Yes | Sections 44–48, 88 |
| Team size | Yes | Sections 44–46 |
| Governance needs | Yes | Sections 44, 51 |
| Lock-in | Yes | Section 50 |
| Current capability tracking | Yes | Section 54 |
| Hands-on project | Yes | Sections 32–38 |
| Security | Yes | Section 59 |
| Cost awareness | Yes | Section 60 |
| Break/fix | Yes | Sections 61–67 |
| Runbooks | Yes | Sections 68–74 |
| ADRs | Yes | Sections 78–82 |
| Interview preparation | Yes | Section 83 |
| Practice questions | Yes | Sections 84–86 |

**Coverage result: 100% of the explicit requirements in the supplied Topic 14 implementation specification are represented in this module.**

The coverage claim is based on a direct requirement-to-section audit of the supplied specification, not on a claim that every AWS implementation detail is permanently stable. AWS product capabilities remain version-, Region-, and configuration-sensitive. fileciteturn70file0L2347-L2392

## 91. Current Documentation Verification Register

Use official AWS documentation as the source of truth before executing labs.

Verified current areas for this module:

1. DataZone terminology and concepts — domains, projects, catalog, glossaries, metadata forms. citeturn0search4turn0search7
2. Business catalog publishing and inventory behavior. citeturn0search6turn0search18
3. Metadata forms. citeturn0search5turn0search8
4. Data products and publishing. citeturn0search17turn0search20
5. Managed Glue subscription access and Lake Formation grants. citeturn0search15
6. Managed Redshift subscription access. citeturn0search2
7. Unmanaged subscription event path. citeturn0search0
8. Row/column filter materialization. citeturn0search1
9. SageMaker Catalog and Unified Studio relationship. citeturn1search1turn1search2
10. Unified Studio data/analytics/AI capabilities. citeturn0search16turn0search10
11. DataZone CLI domain operations. citeturn1search3turn1search5
12. DataZone API project creation. citeturn1search7
13. Current AWS Terraform provider DataZone resources. citeturn1search0turn1search4

Before running any lab, re-check the linked AWS documentation because the service is evolving quickly.

## 92. Production Operating Standard

A production-grade DataZone / Unified Studio implementation should follow:

```text
Discoverability
+
Business Meaning
+
Ownership
+
Quality
+
Security
+
Authorization
+
Auditability
+
Lifecycle
+
Cost Awareness
=
Trusted Data Product Platform
```

Operational rules:

1. Never confuse discovery with authorization.
2. Never use a catalog as the only security boundary.
3. Do not publish critical products without ownership.
4. Prefer structured metadata for governed fields.
5. Treat glossary definitions as business contracts.
6. Test both allowed and denied access.
7. Document the underlying permission path.
8. Monitor subscription failures.
9. Design product deprecation before product proliferation.
10. Record architecture decisions and trade-offs.
11. Keep infrastructure and policy definitions reproducible where practical.
12. Re-verify rapidly changing AWS capabilities before deployment.

## 93. Critical Mental Models

Memorize these:

```text
Data Catalog
= Where do I find data?

Business Metadata
= What does the data mean?

Data Product
= What useful governed data can another team consume?

DataZone
= Discover + understand + publish + request + govern

Glue Data Catalog
= Technical metadata foundation

Lake Formation
= Govern supported data access

Athena
= Query engine

Redshift
= Warehouse analytics

Unified Studio
= Unified working experience across data, analytics, and AI

Discover
≠
Authorize

Catalog
≠
Storage

Data Product
≠
Just a Table

Governance
≠
Documentation Only
```

These mental models are more durable than memorizing console navigation.

## 94. Final Learning Loop

Use this loop for the module:

```text
Read
  ↓
Draw the architecture
  ↓
Publish a data product
  ↓
Add business metadata
  ↓
Search as a consumer
  ↓
Request access
  ↓
Approve
  ↓
Inspect underlying grants
  ↓
Query
  ↓
Break access
  ↓
Diagnose
  ↓
Fix least-privilege
  ↓
Write a runbook
  ↓
Make an ADR
  ↓
Explain the trade-off
```

If you can perform the loop and explain every boundary, you understand the topic at production depth.

## 95. Final Principle

The purpose of this topic is not to teach a catalog UI.

It is to teach the transition:

```text
Data Engineering
      ↓
Governed Data Platform
      ↓
Data Products
      ↓
Discoverable Business Data
      ↓
Controlled Data Sharing
      ↓
Unified Analytics / AI Experience
      ↓
Enterprise AI Systems
```

The senior Data Engineer should be able to answer:

> Where is the data?

> What does it mean?

> Who owns it?

> Is it trustworthy?

> Who may use it?

> How is that access enforced?

> What happens when access changes?

> How does an analyst consume it?

> How does an AI system discover it safely?

> Which platform architecture gives the organization the best balance of capability, control, cost, and lock-in?

That is the production-level objective of Topic 14.

## 96. Source Notes

Primary AWS documentation used for current implementation-sensitive statements:

- Amazon DataZone terminology and concepts: https://docs.aws.amazon.com/datazone/latest/userguide/datazone-concepts.html
- Amazon DataZone business data catalog: https://docs.aws.amazon.com/datazone/latest/userguide/working-with-business-catalog.html
- Amazon DataZone metadata forms: https://docs.aws.amazon.com/datazone/latest/userguide/create-metadata-form.html
- Amazon DataZone data products: https://docs.aws.amazon.com/datazone/latest/userguide/publish-data-product.html
- DataZone managed Glue access: https://docs.aws.amazon.com/datazone/latest/userguide/grant-access-to-glue-asset.html
- DataZone managed Redshift access: https://docs.aws.amazon.com/datazone/latest/userguide/grant-access-to-redshift-asset.html
- DataZone unmanaged access: https://docs.aws.amazon.com/datazone/latest/userguide/grant-access-to-unmanaged-asset.html
- DataZone row/column filters: https://docs.aws.amazon.com/datazone/latest/userguide/grant-access-with-filters.html
- SageMaker Unified Studio concepts: https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/concepts.html
- SageMaker/DataZone relationship: https://docs.aws.amazon.com/datazone/latest/userguide/sagemaker-datazone.html
- DataZone CLI: https://docs.aws.amazon.com/cli/latest/reference/datazone/
- DataZone API: https://docs.aws.amazon.com/datazone/latest/APIReference/
- AWS provider DataZone resources: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/datazone_project

**Documentation policy:** URLs above are navigation references. Exact commands, API parameters, provider resources, pricing, feature availability, and regional support must be re-verified before production use.

## 97. Final Quality Check

### Content
- [x] Simple explanations first
- [x] Professional terminology introduced progressively
- [x] Data catalog fundamentals
- [x] Business metadata
- [x] Business glossary
- [x] Data products
- [x] DataZone
- [x] Unified Studio
- [x] AWS integration
- [x] Open-source comparison
- [x] Unity Catalog comparison
- [x] Adoption strategy
- [x] Security
- [x] Cost
- [x] Break/fix
- [x] Runbooks
- [x] ADRs
- [x] Labs
- [x] Interview preparation
- [x] Practice questions
- [x] Completion checklist
- [x] Coverage audit

### Safety / Accuracy
- [x] No claim that DataZone replaces Lake Formation
- [x] No claim that DataZone replaces Glue Data Catalog
- [x] No claim that DataZone and Unified Studio are identical
- [x] No claim that Unity Catalog is an exact equivalent
- [x] No hard-coded pricing
- [x] No invented permissions
- [x] Current CLI/API examples identified as documentation-sensitive
- [x] Terraform examples identified as provider-sensitive
- [x] Stable concepts separated from changing implementation details

### File Safety
- [x] Only the requested Markdown artifact is created by this generation step.

## 98. Module Exit Criteria

You are ready to exit Topic 14 when you can:

- explain the difference between technical and business metadata;
- explain a business glossary;
- define a data product;
- model a DataZone domain and project structure;
- publish a gold dataset as a data product;
- explain inventory versus published catalog visibility;
- execute or explain a subscription workflow;
- trace authorization into Lake Formation or Redshift;
- explain the relationship between DataZone and Glue;
- explain the relationship between DataZone and Athena;
- explain the relationship between DataZone and Redshift;
- explain the role of EMR;
- explain SageMaker Unified Studio from a data-engineering perspective;
- compare managed AWS governance with open-source catalogs;
- compare AWS and Databricks governance architectures;
- produce a platform adoption recommendation;
- troubleshoot a failed subscription;
- write a production runbook;
- write an ADR;
- explain how governed metadata can support enterprise AI without bypassing authorization.

## 99. Final Roadmap Alignment Statement

This module implements the requested final Phase E transition:

```text
12 → 13 → 14
observe → secure → unify
```

Topic 12 established observability.

Topic 13 established encryption, private networking, and security architecture.

Topic 14 establishes the governed discovery, data-product, data-sharing, and unified data/analytics/AI experience that sits above those operational foundations.

The resulting Applied AI Engineering perspective is:

```text
Reliable Data
   +
Secure Data
   +
Governed Data
   +
Discoverable Data
   +
Reusable Data Products
   +
Controlled Access
   +
Unified Analytics / AI Experience
   =
Production Enterprise AI Data Foundation
```


---

# Appendix A — Coverage Evidence Map

| Requirement cluster | Sections |
|---|---|
| Catalog fundamentals | 4–8 |
| Business metadata | 7–8 |
| Data products | 9–10, 19 |
| DataZone fundamentals | 11–20 |
| Domains/projects | 13–14 |
| Publishing/subscriptions | 18–21 |
| Governed access | 21, 23, 35, 61–74 |
| Glue integration | 22 |
| Lake Formation | 23 |
| Athena | 24 |
| Redshift | 25 |
| EMR | 26 |
| Unified Studio | 27–29 |
| OpenMetadata/DataHub | 39–40 |
| Unity Catalog | 41 |
| Architecture matrix | 42 |
| AWS vs composed | 43 |
| Adoption framework | 44–48, 88 |
| Lock-in | 50 |
| Governance | 51–52 |
| AI | 49, 53, 75–77 |
| CLI / boto3 / Terraform | 55–58 |
| Security | 59 |
| Cost | 60 |
| Break/fix | 61–67 |
| Runbooks | 68–74 |
| Production architectures | 75–77 |
| ADRs | 78–82 |
| Interviews | 83 |
| Practice | 84–87 |
| Completion | 89 |
| Final audit | 90 |
| Current documentation | 91 |
| Operating standard | 92 |
| Mental models | 93 |
| Learning loop | 94 |
| Final principle | 95 |

---

# Appendix B — Lab Deliverable Template

Use this structure for the conceptual lab deliverable described by the roadmap. The roadmap specifies `docs/unified_catalog.md` as a learner deliverable; this generation task intentionally does **not** create that separate file.

```text
# Unified Catalog Lab

## Business Problem

## Data Products

## Producer Project

## Consumer Project

## Metadata Standard

## Business Glossary

## Publishing Workflow

## Subscription Workflow

## Authorization Path

## Athena Verification

## Redshift Verification

## Security Findings

## Cost Considerations

## Self-Built vs DataZone Comparison

## Adoption Recommendation

## Cleanup Evidence
```

---

# Appendix C — Production Review Questions

Before approving a real enterprise implementation, ask:

1. Can a new analyst discover the correct product without tribal knowledge?
2. Can they understand the business definition?
3. Is the owner accountable?
4. Is data quality visible?
5. Is sensitive information classified?
6. Can the consumer request access without a manual email chain?
7. Is approval auditable?
8. Is actual authorization enforced independently of catalog visibility?
9. Can an administrator explain the exact grant path?
10. Can access be revoked?
11. Can product changes be communicated?
12. Can products be deprecated?
13. Can the organization export or reproduce critical metadata?
14. Is the operating model clear?
15. Is the total cost of ownership understood?
16. Has multi-cloud been evaluated?
17. Has lock-in been explicitly accepted or mitigated?
18. Have AI-agent access paths been threat-modeled?
19. Have denied-access test cases been executed?
20. Has current AWS documentation been checked immediately before implementation?

---

# End of Topic 14
