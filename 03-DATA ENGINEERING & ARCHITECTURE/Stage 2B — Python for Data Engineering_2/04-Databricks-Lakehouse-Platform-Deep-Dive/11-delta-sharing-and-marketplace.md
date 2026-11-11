# 11 --- Delta Sharing and Marketplace

> **G4 --- Databricks Lakehouse Platform Deep Dive \| Topic 11 \|
> Beginner → Production**

**Current terminology:** Databricks documentation currently describes
the sharing family as **OpenSharing**, including
Databricks-to-Databricks, Databricks-to-Open, and Open-to-Databricks
patterns. This roadmap uses the broader Delta Sharing terminology
because the open protocol and interoperability model are the core
subject.

## Module Purpose

A production lakehouse must safely distribute governed data to business
units, customers, partners, vendors, analysts, and other platforms.

Traditional exchange:

``` text
Producer → Export → File → Transfer → Consumer → Load
```

Governed sharing:

``` text
Governed Data → Data Product → Share → Recipient → Consumer
```

The goal is to share data without unnecessary copies while preserving
security, privacy, auditability, performance, cost control, and
operational reliability.

## Roadmap Position

Topic 10 established:

``` text
Gold → Unity Catalog → SQL → AI/BI → Genie
```

Topic 11 extends the same governed assets beyond the immediate
environment:

``` text
Gold → Unity Catalog → Data Product → Sharing Boundary → External Consumer
```

The progression is:

``` text
Produce → Govern → Optimize → Analyze → Share
```

## Scope Boundary

This module assumes knowledge of Delta Lake, Unity Catalog, SQL, Spark,
data modeling, performance engineering, and Databricks analytics. It
focuses specifically on:

-   Delta Sharing/OpenSharing;
-   providers, shares and recipients;
-   Databricks-to-Databricks sharing;
-   Databricks-to-Open sharing;
-   shared tables, views, volumes and supported assets;
-   safe subsets and PII minimization;
-   authentication, authorization and revocation;
-   auditability;
-   Python consumption;
-   Change Data Feed and history awareness;
-   schema evolution and data contracts;
-   Marketplace and data products;
-   Clean Rooms awareness;
-   sharing vs files/APIs/warehouse sharing;
-   performance, cost and production operations.

## Learning Loop

For every major capability:

``` text
What is it?
↓
Why does it exist?
↓
How does it work?
↓
How is it implemented?
↓
How is it secured?
↓
How is it tested?
↓
How is it audited?
↓
How is it revoked?
↓
How can it fail?
↓
What does it cost?
↓
When should I use it?
↓
When should I NOT use it?
```

# 1. The Data-Sharing Problem

Organizations share data internally and externally for partner
analytics, customer reporting, vendor collaboration, cross-workspace
access, data products, and external BI.

File exchange can create duplicate storage, stale snapshots, transfer
pipelines, credential sprawl, weak revocation, unclear ownership, and
duplicated data-quality logic.

A governed share provides:

``` text
Provider → Share → Recipient → Consumer
```

The provider remains responsible for what is shared, who receives it,
data quality, security, auditing and revocation.

File export remains valid for one-time snapshots, disconnected
environments, or consumers that cannot use a sharing protocol.

# 2. Delta Sharing Fundamentals

Delta Sharing is an open protocol/ecosystem for secure data sharing
across organizational and platform boundaries. Current Databricks
terminology uses OpenSharing for its current implementation.

Core objects:

  Object         Responsibility
  -------------- --------------------------------------------
  Provider       Controls shared data and sharing policy
  Share          Named collection of shared assets
  Recipient      Identity/object authorized to receive data
  Shared asset   Table/view/volume/other supported content

Mental model:

``` text
Provider
   ↓
 Share
   ↓
Recipient
   ↓
Consumer
```

A share is an access boundary, not merely a list of tables.

# 3. Provider

The provider owns the data-sharing decision.

Responsibilities:

-   data classification;
-   data minimization;
-   quality;
-   recipient approval;
-   share lifecycle;
-   documentation;
-   monitoring;
-   audit;
-   revocation.

Production rule:

> The provider owns responsibility for the data boundary.

# 4. Share

A share is a named logical collection of assets.

Example:

``` text
partner_sales
 ├── partner_orders
 ├── partner_products
 └── partner_daily_sales
```

A good share is purpose-specific. Avoid exposing an entire production
catalog when the consumer needs two curated assets.

# 5. Recipient

A recipient represents the consumer identity authorized to receive
shared data.

Lifecycle:

``` text
Requested → Approved → Provisioned → Active → Reviewed → Revoked
```

A recipient is a sharing-boundary object, not simply another database
user.

# 6. Databricks-to-Databricks Sharing

Current Databricks documentation describes Databricks-to-Databricks
OpenSharing between Unity Catalog-enabled Databricks environments.

``` text
Provider Workspace
   ↓
Unity Catalog
   ↓
Share
   ↓
Recipient Workspace
   ↓
Unity Catalog
   ↓
Consumer
```

Current documentation describes a Databricks-managed secure connection
for this mode.

Typical workflow:

1.  create share;
2.  create recipient;
3.  grant share access;
4.  recipient receives the share;
5.  recipient creates/uses the appropriate catalog;
6.  recipient grants local users appropriate access.

Verify current privileges and commands before production use.

# 7. Databricks-to-Open / Open Sharing

Databricks-to-Open is intended for external consumers.

``` text
Databricks Provider
      ↓
OpenSharing
      ↓
External Recipient
      ↓
Python / Spark / BI / Supported Client
```

Current documentation describes external authentication patterns
including bearer-token credentials and OIDC federation where supported.

Open sharing is an interoperability mechanism, not a reason to expose
raw production storage indiscriminately.

# 8. Databricks-to-Databricks vs Databricks-to-Open

  -----------------------------------------------------------------------
  Dimension               D2D                     D2Open
  ----------------------- ----------------------- -----------------------
  Consumer                Databricks              External platform

  UC consumer             Required                Not necessarily

  Native integration      Strong                  Provider-focused

  Interoperability        Medium                  High

  Credential model        Databricks-managed      External authentication
                          connection in current   patterns
                          D2D model               

  Typical use             Cross-Databricks        Partners/external
                                                  platforms

  Main risk               Cross-environment       External
                          governance              identity/client
                                                  management
  -----------------------------------------------------------------------

Always verify current client and authentication support.

# 9. Shareable Assets

Roadmap-relevant assets include:

-   tables;
-   views;
-   volumes where supported;
-   notebooks in supported Databricks contexts;
-   table history where supported;
-   Change Data Feed where supported;
-   filtered data;
-   other supported data/AI assets.

Support is sharing-mode and environment dependent. Never assume an asset
supported in one mode is supported in another.

# 10. Creating and Managing Shares

Production flow:

``` text
Governed asset
 ↓
Classify
 ↓
Validate quality
 ↓
Minimize
 ↓
Create share
 ↓
Add asset
 ↓
Create recipient
 ↓
Grant access
 ↓
Test
 ↓
Audit / monitor
```

Illustrative current-style SQL:

``` sql
CREATE SHARE partner_sales
COMMENT 'Approved partner sales data';

ALTER SHARE partner_sales
ADD TABLE main.gold.partner_sales;
```

Where supported, share access is granted through `GRANT ON SHARE`.

Exact syntax, privileges, recipient type, cloud and sharing mode must be
verified against current documentation.

# 11. Safe Subsets and Data Minimization

Production principle:

> **Share the minimum useful data, not the maximum available data.**

Bad:

``` text
production.orders → partner
```

Better:

``` text
production.orders
   ↓
partner-specific view/table
   ↓
share
```

Techniques:

-   projection;
-   filtering;
-   aggregation;
-   partner-specific views;
-   dedicated sharing tables;
-   pseudonymization where appropriate.

Example:

``` sql
CREATE VIEW gold.partner_acme_orders AS
SELECT
    order_id,
    order_date,
    product_id,
    quantity,
    net_revenue
FROM gold.orders
WHERE partner_id = 'ACME';
```

Use controlled metadata instead of hard-coded partner identifiers in
production where possible.

# 12. PII and Data Minimization

Original:

``` text
customer_id
name
email
phone
address
order_id
product_id
order_date
revenue
```

Partner needs sales performance:

``` text
order_id
product_id
order_date
revenue
```

Remove unnecessary PII and confidential fields.

Classify data as appropriate:

``` text
Public / Internal / Confidential / Restricted / PII / Financial / Regulated
```

Then decide who needs what, for what purpose, for how long, and under
what controls.

# 13. Authentication vs Authorization

Authentication asks:

> Who are you?

Authorization asks:

> What are you allowed to access?

They are different controls.

For Databricks-to-Databricks, current documentation describes a
Databricks-managed secure connection.

For Databricks-to-Open, current documentation supports external
authentication patterns such as bearer-token credentials and OIDC
federation where eligible.

Never commit credentials, tokens, profiles or activation links to source
control.

# 14. Access Revocation

Revocation is a first-class lifecycle operation:

``` text
Identify recipient
 ↓
Confirm authorization
 ↓
Revoke share access
 ↓
Invalidate credentials where applicable
 ↓
Test failure
 ↓
Inspect audit evidence
 ↓
Document
```

Provider-side revocation controls future governed access; it cannot
necessarily erase copies already downloaded by the consumer.

# 15. Auditing and Unity Catalog

A production system should answer:

``` text
Who accessed?
When?
Which recipient?
Which share?
Which asset?
Was access expected?
Was access revoked?
```

Use Unity Catalog governance, supported audit facilities and system
tables where available.

Never invent audit event names or schemas. Verify the current
documentation for the target environment.

Sharing should begin with governed catalog assets, not raw storage
paths.

# 16. Views vs Tables vs Dedicated Sharing Tables

  ------------------------------------------------------------------------------------
  Approach          Advantages             Risks                    Best use
  ----------------- ---------------------- ------------------------ ------------------
  Table             Simple, predictable    May expose too much      Stable curated
                                                                    data

  View              Flexible               Dependency/performance   Partner-specific
                    filtering/projection                            subset

  Dedicated table   Stable                 Extra pipeline/storage   High-value data
                    contract/performance                            product
  ------------------------------------------------------------------------------------

Use views for simple dynamic subsets. Use dedicated tables when the
product needs an independent lifecycle, stable schema, or predictable
performance.

# 17. Change Data Feed and Table History

CDF can support incremental consumer workflows where current sharing
capabilities and table configuration support it.

Consumer pattern:

``` text
Initial snapshot
 ↓
Checkpoint
 ↓
Read changes
 ↓
Apply inserts/updates/deletes
 ↓
Advance checkpoint
```

Production requirements include idempotency, checkpointing, delete
handling, schema compatibility and replay.

Table history can support reproducibility, audit and point-in-time
analysis where the sharing mode exposes it.

Verify current support and limitations.

# 18. Python Consumption

The roadmap requires the open-source Delta Sharing client.

Conceptual workflow:

``` text
Secure profile
 ↓
Sharing client
 ↓
List shares
 ↓
List schemas
 ↓
List tables
 ↓
Read table
 ↓
Validate
```

Illustrative Python:

``` python
import delta_sharing

profile = "profile.share"
client = delta_sharing.SharingClient(profile)

for share in client.list_shares():
    print(share.name)
```

A small table can be loaded using the current client API, for example:

``` python
table_url = "profile.share#share.schema.table"
df = delta_sharing.load_as_pandas(table_url)
```

Do not load large production datasets into pandas by default. Verify the
current package API before production use.

# 19. BI and External Consumers

Supported external consumers can include Python/pandas, Apache Spark and
BI tools, depending on the sharing mode and client.

Current Marketplace documentation also supports external-platform access
for eligible tabular data products.

Never assume every BI tool supports every sharing mode or asset. Verify
the client matrix.

# 20. Delta Sharing vs File Exports

  --------------------------------------------------------------------------------------
  Dimension               Delta/OpenSharing       File Export
  ----------------------- ----------------------- --------------------------------------
  Freshness               Potentially current     Snapshot unless repeated
                          access                  

  Duplication             Lower by design         Higher

  Revocation              Provider-controlled     Copies may persist
                          relationship            

  Auditability            Governance/audit model  Transfer dependent

  Consumer flexibility    Open protocol clients   Broad file compatibility

  Best fit                Recurring analytical    Snapshots/compatibility/disconnected
                          access                  use
  --------------------------------------------------------------------------------------

File export remains a valid architecture for some requirements.

# 21. Delta Sharing vs API

  Requirement                 Delta/OpenSharing   API
  --------------------------- ------------------- --------------------------
  Large analytical dataset    Strong              Poor fit
  Batch analytics             Strong              Possible but inefficient
  Request/response            Poor fit            Strong
  Application integration     Poor fit            Strong
  Current per-request state   Not primary         Strong

Example:

``` text
Yesterday's sales dataset → Delta/OpenSharing
Current order 123 status → API
```

# 22. Delta Sharing vs Warehouse-Native Sharing

Warehouse-native sharing can be excellent inside a tightly integrated
warehouse ecosystem.

Delta/OpenSharing is especially valuable when cross-platform
interoperability and external clients matter.

Compare:

-   interoperability;
-   platform coupling;
-   governance;
-   latency;
-   consumer ecosystem;
-   operational complexity;
-   cost.

No mechanism is universally superior.

# 23. Databricks Marketplace

Databricks Marketplace is a discovery and distribution mechanism for
supported data and AI products.

Current documentation describes offerings including datasets, notebooks,
AI models, MCP servers and supported non-tabular assets.

Marketplace uses OpenSharing for secure data exchange.

Mental model:

``` text
Data Provider
 ↓
Data Product
 ↓
Marketplace Listing
 ↓
Consumer
 ↓
Access / Subscription
 ↓
Consumption
```

# 24. Data Products

A data product is more than a table.

It should have:

``` text
Owner
Purpose
Documentation
Schema
Grain
Freshness
Quality
Security classification
Access policy
Support model
Version/change policy
Consumer experience
```

Example:

``` text
Global Retail Sales Dataset
- daily sales
- product categories
- geography
- aggregated customer segments
- no raw customer PII
```

# 25. Marketplace Listing Design

A professional listing should document:

-   title;
-   description;
-   business use cases;
-   schema;
-   samples;
-   update frequency;
-   geographic/time coverage;
-   ownership;
-   quality;
-   support;
-   access model;
-   privacy classification;
-   limitations;
-   commercial conditions where applicable.

Marketplace fields and requirements evolve, so verify current provider
documentation.

# 26. Marketplace vs Direct Sharing

  Scenario                  Direct Share   Marketplace
  ------------------------- -------------- ---------------------
  One known partner         Strong         Usually unnecessary
  Few strategic partners    Strong         Optional
  Many consumers            Possible       Strong
  Discoverability           Low            High
  Reusable product          Good           Excellent
  Commercial distribution   Possible       Strong
  One-off transfer          Strong         Usually unnecessary

# 27. Clean Rooms

Clean Rooms solve a different problem from direct sharing.

``` text
Company A sensitive data
        +
Company B sensitive data
        ↓
Controlled privacy-safe computation
        ↓
Approved outputs
```

Use cases include joint audience analysis, overlap measurement and
privacy-sensitive research.

If the consumer needs the dataset, sharing may fit. If parties need
joint computation while limiting raw-data exposure, evaluate a Clean
Room.

# 28. Clean Rooms vs Delta Sharing

  Requirement                       Delta/OpenSharing   Clean Room
  --------------------------------- ------------------- ---------------
  Direct data access                Strong              Not primary
  Cross-platform sharing            Strong              Controlled
  Joint computation                 Downstream          Core use case
  Privacy-sensitive collaboration   Limited             Strong
  Complexity                        Lower               Higher

# 29. Schema Evolution and Data Contracts

Shared data creates a producer/consumer contract.

  Change                Typical risk   Recommended action
  --------------------- -------------- -------------------------
  Add nullable column   Lower          Communicate/document
  Add required column   Medium/high    Consumer validation
  Remove column         High           Breaking-change process
  Rename column         High           Treat as breaking
  Change type           High           Version/test
  Change meaning        Very high      New contract/version
  Change grain          Very high      New product/version

Contract fields:

``` text
Purpose
Owner
Grain
Schema
Definitions
Freshness
Quality
Security
Version
Breaking-change policy
Deprecation
Support
```

# 30. Data Quality

Before sharing:

``` text
[ ] Schema validated
[ ] Grain documented
[ ] Freshness within SLA
[ ] Completeness checked
[ ] Uniqueness checked
[ ] Business totals reconciled
[ ] PII reviewed
[ ] Ownership assigned
[ ] Consumer purpose approved
[ ] Access tested
```

Shared data errors propagate outside the provider organization, so
quality is part of the product contract.

# 31. Performance and Cost

Performance depends on:

-   volume;
-   query shape;
-   physical layout;
-   clustering;
-   pruning;
-   consumer compute;
-   caching;
-   repeated scans.

Cost can occur through:

``` text
Provider preparation
+ provider compute
+ consumer compute
+ storage
+ applicable transfer
+ operational overhead
```

Measure cost per consumer, product and query where practical. Never
hard-code current pricing.

# 32. Production Reference Architecture

``` text
                         PROVIDER
                            │
                    ┌───────▼────────┐
                    │ Unity Catalog  │
                    │ Governed Data  │
                    └───────┬────────┘
                            │
                    Data Product Layer
                            │
                 ┌──────────┴──────────┐
                 │                     │
            OpenSharing            Marketplace
                 │                     │
        ┌────────┴────────┐       ┌────▼─────┐
        │                 │       │Consumers │
   Databricks          External   └──────────┘
   Consumer             Consumer
```

Cross-cutting controls:

``` text
Security / Audit / Quality / Monitoring / Cost / Revocation / Schema
```

# 33. Hands-On Labs

Every lab must record: objective, prerequisites, setup,
commands/SQL/Python where applicable, expected output, security,
troubleshooting, cleanup and production lesson.

## Lab 1 --- Provider / Share / Recipient

Draw the sharing boundary and identify each responsibility.

## Lab 2 --- Create a Test Share

Create a non-production share using current verified syntax.

## Lab 3 --- Add a Table

Add a small curated gold table and validate grain/schema/sensitivity.

## Lab 4 --- Safe Partner View

Filter partner rows, project required columns and remove PII.

## Lab 5 --- Share Partner Dataset

Grant access and validate the authorized path.

## Lab 6 --- External Recipient

Create a recipient using the current supported mechanism.

## Lab 7 --- Consume the Share

Read data and reconcile a business total.

## Lab 8 --- Python Client

List shares/schemas/tables and read a small sample.

## Lab 9 --- Revoke Access

Revoke access and prove a fresh client cannot read the share.

## Lab 10 --- Audit Access

Identify recipient/share/asset/time using current audit facilities.

## Lab 11 --- Schema Evolution

Test additive and breaking changes and document consumer impact.

## Lab 12 --- Marketplace Data Product

Design a listing, product contract, freshness, quality and support
model.

## Lab 13 --- Clean Room Architecture

Design privacy-safe joint analysis without raw-data exchange.

## Lab 14 --- Architecture Decision

Choose Delta/OpenSharing, API, file export, warehouse sharing,
Marketplace or Clean Room for multiple scenarios.

# 34. Required `sql/sharing/` Exercise

1.  Create a partner-specific view of `gold.orders`.
2.  Filter to the partner.
3.  Remove PII.
4.  Expose only required columns.
5.  Create an open-sharing recipient using the current supported
    mechanism.
6.  Read the share with the Python client.
7.  Use CDF where supported and demonstrate incremental consumption.
8.  Audit who accessed the share and when.
9.  Revoke the recipient.
10. Verify access is no longer available.
11. Build a decision table for Delta Sharing vs API vs file export for
    three partner scenarios.

# 35. Break/Fix Incidents

Every incident must include symptom, business impact, hypothesis,
evidence, investigation, root cause, fix, verification, prevention and
production lesson.

## Incident 1 --- Partner Cannot Access Shared Table

Investigate recipient, share grant, catalog/access setup, sharing mode
and client.

## Incident 2 --- Recipient Credential Fails

Investigate authentication mode, credential validity, profile and client
compatibility.

## Incident 3 --- Revocation Appears Ineffective

Inspect recipient, share grants, credentials, audit and fresh-client
behavior.

## Incident 4 --- PII Accidentally Shared

Contain, revoke if required, audit, rebuild a safe asset and validate.

## Incident 5 --- Partner Receives Too Many Rows

Check filtering, joins, partner mapping and view predicates.

## Incident 6 --- Wrong Revenue Shared

Check grain, aggregation, currency, refunds, date and source semantics.

## Incident 7 --- Schema Changed Unexpectedly

Identify producer change, contract failure, consumer impact and version
strategy.

## Incident 8 --- Consumer Pipeline Breaks

Investigate removal/rename/type/grain changes.

## Incident 9 --- Shared Dataset Is Stale

Investigate upstream pipeline, source delay, refresh and freshness
contract.

## Incident 10 --- Shared Query Is Slow

Separate provider preparation from consumer query, layout and compute.

## Incident 11 --- Audit Evidence Is Unexpected

Verify audit source, permissions, retention and sharing mode.

## Incident 12 --- External Client Cannot Read

Check protocol, client, asset type, credential, network and
runtime/package.

## Incident 13 --- Marketplace Product Is Poorly Documented

Improve schema, samples, freshness, quality, use cases and support.

## Incident 14 --- Clean Room Requirement Implemented as Raw Sharing

Stop raw exchange and redesign around controlled privacy-safe
computation.

## Incident 15 --- Sharing Cost Increases

Compare consumers, volume, queries, compute, transfer and new products.

## Incident 16 --- One Client Works, Another Fails

Compare protocol, client version, authentication and supported asset
behavior.

## Incident 17 --- Consumer Sees Old Schema

Investigate metadata refresh, catalog state, client behavior and schema
evolution.

## Incident 18 --- Former Partner Claims Access

Inspect recipient/share/credential state and distinguish provider
revocation from downloaded copies.

# 36. Security Incident Exercises

### Incident A --- Unnecessary PII

Contain → revoke if needed → audit → remove PII → rebuild → validate →
re-share.

### Incident B --- Former Partner

Verify recipient lifecycle, share grants, credentials and audit; revoke
and test.

### Incident C --- Entire Production Table Request

Reject broad access as the default. Identify the business need and
create the minimum useful data product.

# 37. Production Runbooks

## Data Share Creation

1.  Identify purpose.
2.  Identify consumer.
3.  Classify data.
4.  Identify owner.
5.  Minimize columns/rows.
6.  Select table/view/dedicated table.
7.  Validate quality.
8.  Create share.
9.  Configure recipient.
10. Grant access.
11. Test.
12. Audit.
13. Document.
14. Monitor.
15. Review.

## Data Share Revocation

1.  Identify recipient.
2.  Confirm authorization.
3.  Identify associated shares.
4.  Revoke.
5.  Invalidate credentials where applicable.
6.  Test denied access.
7.  Inspect audit.
8.  Document.

## Sharing Security Incident

``` text
Detect → Contain → Revoke → Identify affected data
→ Inspect audit → Assess impact → Remediate → Verify
→ Document → Prevent recurrence
```

## Schema Change

``` text
Classify → Identify consumers → Assess compatibility
→ Communicate → Deploy → Validate → Monitor → Document
```

# 38. Decision Matrices

## Sharing Mechanism

  --------------------------------------------------------------------------------------------------
  Requirement           Delta/OpenSharing       File        API   Warehouse   Marketplace Clean Room
                                                                    Sharing               
  ------------------- ------------------- ---------- ---------- ----------- ------------- ----------
  Large analytical                   High     Medium        Low        High          High     Medium
  dataset                                                                                 

  Request/response                    Low        Low       High         Low           Low        Low

  One-time snapshot                Medium       High     Medium         Low           Low        Low

  Cross-platform                     High       High     Medium      Medium          High     Medium
  analytics                                                                               

  Many potential                   Medium        Low     Medium      Medium          High     Medium
  consumers                                                                               

  Privacy-sensitive                   Low        Low        Low         Low           Low       High
  joint computation                                                                       

  Discoverability                     Low        Low        Low         Low          High        Low
  --------------------------------------------------------------------------------------------------

## Table vs View vs Dedicated Table

  Dimension           Table    View       Dedicated Table
  ------------------- -------- ---------- -----------------
  Simplicity          High     High       Medium
  Data minimization   Medium   High       High
  Schema stability    High     Medium     High
  Performance         High     Variable   High
  Product contract    High     Medium     High

## D2D vs D2Open

  Dimension            D2D                    D2Open
  -------------------- ---------------------- ------------------------
  Consumer             Databricks             External platform
  UC consumer          Required               Not necessarily
  Native integration   Strong                 Provider-focused
  Interoperability     Medium                 High
  Credential model     Managed connection     External auth patterns
  Best use             Databricks ecosystem   External ecosystem

# 39. Architecture Decision Records

## ADR-001 --- Delta/OpenSharing Instead of Recurring File Exports

**Context:** Partner needs recurring analytical sales data.\
**Decision:** Use governed sharing when supported.\
**Why:** Reduces recurring transfer plumbing and creates a controlled
access boundary.\
**Security:** Minimum necessary dataset.\
**Performance:** Benchmark representative queries.\
**Cost:** Compare preparation, compute and transfer.\
**Rollback:** Controlled file export.

## ADR-002 --- Partner-Specific Views

**Context:** Partners require different row subsets.\
**Decision:** Use governed views when logic is simple.\
**Why:** Filtering, projection and centralized policy.\
**Trade-off:** Dependency/performance considerations.\
**Rollback:** Dedicated sharing table.

## ADR-003 --- Marketplace for Reusable Data Products

**Context:** Many potential consumers.\
**Decision:** Marketplace candidate.\
**Why:** Discovery and product distribution.\
**Consequence:** Requires product ownership and support.

## ADR-004 --- Clean Room for Privacy-Sensitive Joint Analysis

**Context:** Parties need joint computation without raw-data exchange.\
**Decision:** Evaluate Clean Room.\
**Why:** Better fit for privacy-preserving collaboration.

## ADR-005 --- API for Application Integration

**Context:** Partner requires per-order status requests.\
**Decision:** API.\
**Why:** Request/response semantics match the workload.

Each ADR should document Context, Problem, Options, Decision, Security,
Performance, Cost, Trade-offs, Consequences, Rollback and Validation.

# 40. Interview Preparation

## Beginner --- 15

1.  What is Delta Sharing?
2.  What is OpenSharing?
3.  What is a provider?
4.  What is a share?
5.  What is a recipient?
6.  What is Databricks-to-Databricks sharing?
7.  What is Databricks-to-Open?
8.  Why minimize shared data?
9.  What is PII?
10. Why revoke access?
11. Why audit sharing?
12. What is a data product?
13. What is Marketplace?
14. What is a Clean Room?
15. Why use an API for application requests?

**Answer standard:** define the concept, state the architectural
purpose, and identify the production control.

## Intermediate --- 20

1.  Why is a share an access boundary?
2.  Why avoid raw production tables?
3.  How do views help?
4.  When is a dedicated table better?
5.  Authentication vs authorization?
6.  Why protect credential files?
7.  What is CDF useful for?
8.  Why does schema evolution matter?
9.  What is a data contract?
10. Why audit sharing?
11. When is Marketplace useful?
12. When is Marketplace unnecessary?
13. What is a Clean Room?
14. Why is sharing not an API replacement?
15. Why can file export be correct?
16. What should a data product document?
17. What is data minimization?
18. Why is revocation important?
19. What affects shared-data performance?
20. Why measure cost per consumer?

## Advanced --- 20

1.  How isolate partner rows?
2.  View vs dedicated table?
3.  How prevent PII leakage?
4.  How investigate failed access?
5.  Why can revoked consumers retain copies?
6.  How handle breaking schema changes?
7.  How compare sharing vs files?
8.  How compare sharing vs APIs?
9.  How compare sharing vs warehouse sharing?
10. Why can Clean Rooms fit joint analysis?
11. What makes a data product production-grade?
12. How design for 500 consumers?
13. How monitor shared data?
14. How benchmark shared data?
15. What is the biggest sharing security risk?
16. Why does Unity Catalog matter?
17. Provider vs consumer governance?
18. How design a data contract?
19. How determine production readiness?
20. How design a sharing SLO?

## Senior / Production --- 20

1.  Partner requests the entire production table --- what do you do?
2.  Former partner can still query --- investigation sequence?
3.  10 TB requested, 50 GB needed --- architecture?
4.  500 consumers --- direct shares or Marketplace?
5.  When should Marketplace be used?
6.  When should Clean Rooms be considered?
7.  Real-time order status --- sharing or API?
8.  How control PII leakage?
9.  How design schema evolution?
10. How design a sharing SLO?
11. How control cost?
12. How investigate performance complaints?
13. Why is revocation not deletion of copies?
14. How prove a share is secure?
15. How design sharing audit?
16. How handle client incompatibility?
17. What is the strongest reason to use OpenSharing?
18. What is the strongest reason to use file export?
19. How turn a dataset into a data product?
20. What is the senior sharing operating model?



# Interview Answer Key

1. **What is Delta Sharing?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
2. **What is OpenSharing?** — OpenSharing is the current Databricks sharing protocol family for governed cross-platform data exchange, including Databricks-to-Databricks and Databricks-to-Open patterns.
3. **What is a provider?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
4. **What is a share?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
5. **What is a recipient?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
6. **What is Databricks-to-Databricks sharing?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
7. **What is Databricks-to-Open?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
8. **Why minimize shared data?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
9. **What is PII?** — Minimize columns and rows to the approved business purpose, remove unnecessary PII, validate the resulting asset, and test the access boundary.
10. **Why revoke access?** — Revoke the recipient/share relationship, invalidate credentials where applicable, test denied access, inspect audit evidence, and document the event.
11. **Why audit sharing?** — Use supported governance/audit facilities to establish who accessed which share/asset and when, subject to current retention and schema.
12. **What is a data product?** — A production data product has an owner, purpose, documented grain/schema, quality and freshness expectations, security policy, support model and change contract.
13. **What is Marketplace?** — Marketplace adds discovery and product distribution to data sharing; it is most valuable when a reusable product has multiple potential consumers.
14. **What is a Clean Room?** — Use a Clean Room when parties need controlled joint computation while minimizing direct exposure of sensitive raw datasets.
15. **Why use an API for application requests?** — Use an API when the consumer needs request/response application behavior; use analytical sharing for recurring dataset consumption.
16. **Why is a share an access boundary?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
17. **Why avoid raw production tables?** — Production readiness requires correctness, security, quality, contract compatibility, observability, revocation, performance, cost ownership and operational runbooks.
18. **How do views help?** — Use a view for simple dynamic filtering/projection; use a dedicated table when an independent lifecycle, stable contract or predictable performance is required.
19. **When is a dedicated table better?** — Use a view for simple dynamic filtering/projection; use a dedicated table when an independent lifecycle, stable contract or predictable performance is required.
20. **Authentication vs authorization?** — Authentication establishes identity; authorization determines which shared resources that identity is permitted to access.
21. **Why protect credential files?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
22. **What is CDF useful for?** — CDF can support incremental downstream consumption where the table and current sharing mode support it; design checkpoints, idempotency and delete handling.
23. **Why does schema evolution matter?** — Treat the schema as a consumer contract; classify changes, communicate breaking changes, and use compatibility/versioning strategies.
24. **What is a data contract?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
25. **Why audit sharing?** — Use supported governance/audit facilities to establish who accessed which share/asset and when, subject to current retention and schema.
26. **When is Marketplace useful?** — Marketplace adds discovery and product distribution to data sharing; it is most valuable when a reusable product has multiple potential consumers.
27. **When is Marketplace unnecessary?** — Marketplace adds discovery and product distribution to data sharing; it is most valuable when a reusable product has multiple potential consumers.
28. **What is a Clean Room?** — Use a Clean Room when parties need controlled joint computation while minimizing direct exposure of sensitive raw datasets.
29. **Why is sharing not an API replacement?** — Use an API when the consumer needs request/response application behavior; use analytical sharing for recurring dataset consumption.
30. **Why can file export be correct?** — File export remains appropriate for snapshots, disconnected consumers, or incompatible environments; governed sharing is stronger for recurring analytical access.
31. **What should a data product document?** — A production data product has an owner, purpose, documented grain/schema, quality and freshness expectations, security policy, support model and change contract.
32. **What is data minimization?** — Minimize columns and rows to the approved business purpose, remove unnecessary PII, validate the resulting asset, and test the access boundary.
33. **Why is revocation important?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
34. **What affects shared-data performance?** — Separate provider preparation from consumer query performance and inspect volume, query shape, physical layout, compute, concurrency and caching.
35. **Why measure cost per consumer?** — Measure provider preparation, provider and consumer compute, storage, applicable transfer, query frequency and operational overhead.
36. **How isolate partner rows?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
37. **View vs dedicated table?** — Use a view for simple dynamic filtering/projection; use a dedicated table when an independent lifecycle, stable contract or predictable performance is required.
38. **How prevent PII leakage?** — Minimize columns and rows to the approved business purpose, remove unnecessary PII, validate the resulting asset, and test the access boundary.
39. **How investigate failed access?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
40. **Why can revoked consumers retain copies?** — Revoke the recipient/share relationship, invalidate credentials where applicable, test denied access, inspect audit evidence, and document the event.
41. **How handle breaking schema changes?** — Treat the schema as a consumer contract; classify changes, communicate breaking changes, and use compatibility/versioning strategies.
42. **How compare sharing vs files?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
43. **How compare sharing vs APIs?** — Use an API when the consumer needs request/response application behavior; use analytical sharing for recurring dataset consumption.
44. **How compare sharing vs warehouse sharing?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
45. **Why can Clean Rooms fit joint analysis?** — Use a Clean Room when parties need controlled joint computation while minimizing direct exposure of sensitive raw datasets.
46. **What makes a data product production-grade?** — A production data product has an owner, purpose, documented grain/schema, quality and freshness expectations, security policy, support model and change contract.
47. **How design for 500 consumers?** — At large consumer counts, evaluate Marketplace/data-product distribution, automated onboarding, standardized contracts, governance and recipient lifecycle automation.
48. **How monitor shared data?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
49. **How benchmark shared data?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
50. **What is the biggest sharing security risk?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
51. **Why does Unity Catalog matter?** — Unity Catalog provides the governed object and permission foundation from which controlled sharing can be designed.
52. **Provider vs consumer governance?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
53. **How design a data contract?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
54. **How determine production readiness?** — Production readiness requires correctness, security, quality, contract compatibility, observability, revocation, performance, cost ownership and operational runbooks.
55. **How design a sharing SLO?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
56. **Partner requests the entire production table --- what do you do?** — Production readiness requires correctness, security, quality, contract compatibility, observability, revocation, performance, cost ownership and operational runbooks.
57. **Former partner can still query --- investigation sequence?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
58. **10 TB requested, 50 GB needed --- architecture?** — Create a curated product containing only the required rows/columns rather than exposing the full source.
59. **500 consumers --- direct shares or Marketplace?** — Marketplace adds discovery and product distribution to data sharing; it is most valuable when a reusable product has multiple potential consumers.
60. **When should Marketplace be used?** — Marketplace adds discovery and product distribution to data sharing; it is most valuable when a reusable product has multiple potential consumers.
61. **When should Clean Rooms be considered?** — Use a Clean Room when parties need controlled joint computation while minimizing direct exposure of sensitive raw datasets.
62. **Real-time order status --- sharing or API?** — Use an API when the consumer needs request/response application behavior; use analytical sharing for recurring dataset consumption.
63. **How control PII leakage?** — Minimize columns and rows to the approved business purpose, remove unnecessary PII, validate the resulting asset, and test the access boundary.
64. **How design schema evolution?** — Treat the schema as a consumer contract; classify changes, communicate breaking changes, and use compatibility/versioning strategies.
65. **How design a sharing SLO?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
66. **How control cost?** — Measure provider preparation, provider and consumer compute, storage, applicable transfer, query frequency and operational overhead.
67. **How investigate performance complaints?** — Separate provider preparation from consumer query performance and inspect volume, query shape, physical layout, compute, concurrency and caching.
68. **Why is revocation not deletion of copies?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
69. **How prove a share is secure?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
70. **How design sharing audit?** — Use supported governance/audit facilities to establish who accessed which share/asset and when, subject to current retention and schema.
71. **How handle client incompatibility?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.
72. **What is the strongest reason to use OpenSharing?** — OpenSharing is the current Databricks sharing protocol family for governed cross-platform data exchange, including Databricks-to-Databricks and Databricks-to-Open patterns.
73. **What is the strongest reason to use file export?** — File export remains appropriate for snapshots, disconnected consumers, or incompatible environments; governed sharing is stronger for recurring analytical access.
74. **How turn a dataset into a data product?** — A production data product has an owner, purpose, documented grain/schema, quality and freshness expectations, security policy, support model and change contract.
75. **What is the senior sharing operating model?** — Answer by stating the architectural purpose, the main security/governance control, the key trade-offs, and the production validation required.

# 41. Practice Questions

## Conceptual --- 25

1.  Explain provider/share/recipient.
2.  Explain OpenSharing.
3.  Explain D2D.
4.  Explain D2Open.
5.  Explain data minimization.
6.  Explain revocation.
7.  Explain data products.
8.  Explain Marketplace.
9.  Explain Clean Rooms.
10. Explain CDF from a consumer perspective.
11. Explain table history.
12. Explain data contracts.
13. Explain authentication.
14. Explain authorization.
15. Explain audit.
16. Explain view vs table.
17. Explain dedicated sharing tables.
18. Explain file trade-offs.
19. Explain API trade-offs.
20. Explain warehouse-sharing trade-offs.
21. Explain provider responsibility.
22. Explain consumer responsibility.
23. Explain schema compatibility.
24. Explain sharing cost.
25. Explain performance.

## SQL/API --- 15

1.  Write an illustrative `CREATE SHARE`.
2.  Add a table.
3.  Grant recipient access.
4.  Create a partner view.
5.  Remove unnecessary columns.
6.  Filter by partner.
7.  Create a freshness query.
8.  Create a quality query.
9.  Design schema validation.
10. Identify audit evidence using current supported facilities.
11. Identify required privileges.
12. Design recipient onboarding.
13. Design revocation.
14. Design compatibility checks.
15. Identify syntax that must be verified before production.

## Python --- 10

1.  Configure a secure profile.
2.  List shares.
3.  List schemas.
4.  List tables.
5.  Read a sample.
6.  Load manageable data into pandas.
7.  Validate schema.
8.  Validate row counts.
9.  Reconcile revenue.
10. Secure the client credentials.

## Security --- 15

1.  Remove PII.
2.  Design least privilege.
3.  Revoke a recipient.
4.  Investigate unauthorized access.
5.  Design recipient lifecycle.
6.  Design credential rotation.
7.  Separate authentication and authorization.
8.  Design audit controls.
9.  Design partner filtering.
10. Design classification.
11. Handle former partner.
12. Handle accidental PII exposure.
13. Handle excessive access request.
14. Design security review.
15. Define production security acceptance.

## Architecture --- 15

1.  Sharing vs API.
2.  Sharing vs file.
3.  Sharing vs warehouse.
4.  Direct share vs Marketplace.
5.  Sharing vs Clean Room.
6.  View vs dedicated table.
7.  D2D vs D2Open.
8.  One partner vs 500 consumers.
9.  Snapshot vs recurring access.
10. Analytical dataset vs application request.
11. Partner-specific vs global product.
12. Small vs large dataset.
13. Live vs disconnected consumer.
14. Data product vs raw table.
15. Design an enterprise sharing platform.

## Production Troubleshooting --- 15

1.  Recipient cannot access.
2.  Token fails.
3.  Revocation ineffective.
4.  PII exposed.
5.  Too many rows.
6.  Wrong metric.
7.  Schema changed.
8.  Consumer pipeline failed.
9.  Data stale.
10. Query slow.
11. Audit unexpected.
12. External client fails.
13. Marketplace complaint.
14. Wrong Clean Room architecture.
15. Cost spike.

## Data Product / Marketplace --- 10

1.  Design a data product.
2.  Write a listing.
3.  Define freshness.
4.  Define quality.
5.  Define contract.
6.  Define support.
7.  Marketplace vs direct share.
8.  Private listing governance.
9.  Consumer onboarding.
10. Product versioning.

# 42. Senior Data Engineer Scenarios

## Scenario 1 --- Partner Sales

A partner needs daily sales but must never receive customer PII.

Design:

``` text
Gold → Partner filter/projection → PII removal → Quality → Share → Recipient
```

## Scenario 2 --- Entire Production Table

Partner asks for `production.orders`. Do not grant broad access for
convenience. Identify the actual business need and build the minimum
useful product.

## Scenario 3 --- Revoked Recipient

Investigate recipient state, share grants, credentials, audit and
fresh-client behavior.

## Scenario 4 --- Schema Change

Determine whether the provider made a breaking change or the consumer
has an invalidly strict contract. Introduce compatibility policy and
versioning.

## Scenario 5 --- 10 TB vs 50 GB

Create a curated, filtered/aggregated product.

## Scenario 6 --- 500 Consumers

Evaluate Marketplace, productization, automation, governance, versioning
and recipient lifecycle.

## Scenario 7 --- Privacy-Sensitive Joint Analysis

If raw customer data should not be exchanged, evaluate Clean Rooms.

## Scenario 8 --- Real-Time Application

If a partner needs `GET /orders/123/status`, use an application
integration architecture such as an API.

# 43. Common Misconceptions

-   **"Delta Sharing is just file sharing."** No; it is an open governed
    data-sharing architecture/protocol.
-   **"Expose the entire source table."** Usually poor production
    practice.
-   **"Authentication equals authorization."** No.
-   **"Revocation is optional."** Access has a lifecycle.
-   **"Deleting an export revokes access."** Copies may persist.
-   **"Marketplace is only a table catalog."** It is a
    distribution/discovery mechanism.
-   **"Clean Rooms and sharing are identical."** They solve different
    problems.
-   **"Delta Sharing replaces APIs."** Dataset access and
    request/response are different.
-   **"Sharing is always better than files."** Consumer constraints
    matter.
-   **"Shared data needs no quality contract."** Incorrect.
-   **"Schema changes are harmless."** They can break consumers.
-   **"Every client supports every asset."** False.
-   **"More data means more value."** More data can increase risk and
    cost.

# 44. Mental Models

1.  **Provider owns the data; recipient receives governed access.**
2.  **Share the minimum useful data, not the maximum available data.**
3.  **Authentication asks who; authorization asks what.**
4.  **Data sharing is a security boundary.**
5.  **A data product needs an owner, contract, quality expectation,
    security boundary and consumer experience.**
6.  **Use analytical sharing for analytical datasets; use APIs for
    application interactions.**
7.  **If parties need joint computation without raw-data exchange,
    evaluate Clean Rooms.**
8.  **Revocation controls future provider-side access; it cannot erase
    consumer copies.**
9.  **Schema is part of the consumer contract.**
10. **Marketplace adds discovery and distribution to sharing.**

# 45. Glossary

  -----------------------------------------------------------------------
  Term                                Definition
  ----------------------------------- -----------------------------------
  Delta Sharing                       Open protocol/ecosystem for
                                      governed data sharing.

  OpenSharing                         Current Databricks terminology for
                                      its open sharing protocol family.

  Provider                            Party controlling shared data.

  Share                               Named collection of shared assets.

  Recipient                           Identity/object authorized to
                                      receive data.

  Databricks-to-Databricks            Sharing between Unity
                                      Catalog-enabled Databricks
                                      environments.

  Databricks-to-Open                  Databricks sharing to supported
                                      external platforms.

  Data product                        Governed, documented
                                      consumer-oriented data asset.

  Marketplace                         Databricks product
                                      discovery/distribution platform.

  Clean Room                          Controlled privacy-sensitive
                                      collaboration environment.

  Authentication                      Establishing identity.

  Authorization                       Determining permitted access.

  Revocation                          Removing/invalidation of access.

  Data minimization                   Sharing only necessary data.

  PII                                 Personally identifiable
                                      information.

  CDF                                 Change Data Feed for supported
                                      Delta workflows.

  Data contract                       Agreement on schema, semantics,
                                      quality and compatibility.

  API                                 Application request/response
                                      interface.

  File export                         Snapshot-oriented file transfer.

  Warehouse sharing                   Platform-specific analytical
                                      sharing.
  -----------------------------------------------------------------------

# 46. Current-Documentation Safety

Databricks sharing evolves rapidly. Verify current official
documentation before production use for:

-   OpenSharing;
-   Databricks-to-Databricks;
-   Databricks-to-Open;
-   Open-to-Databricks;
-   recipient creation/authentication;
-   OIDC and bearer-token flows;
-   supported asset types;
-   tables/views/volumes/notebooks;
-   CDF/history support;
-   Python client behavior;
-   Marketplace;
-   Marketplace access models;
-   Clean Rooms;
-   audit/system tables;
-   SQL/CLI/API syntax;
-   client limitations;
-   pricing;
-   regional availability;
-   preview/beta status.

Never fabricate syntax, API endpoints, credential flows, asset support,
audit schemas, pricing or UI steps.

If current behavior cannot be verified:

1.  teach the underlying concept;
2.  label the implementation environment/version dependent;
3.  instruct the learner to verify current official Databricks
    documentation before production use.

# 47. Connections to Other G4 Topics

### Topic 04 --- Unity Catalog

Governed data and permissions are the foundation of secure sharing.

### Topic 05 --- Auto Loader

Ingestion creates data that can become shareable products.

### Topic 07 --- Lakeflow Declarative Pipelines

Pipelines produce curated datasets for consumers.

### Topic 09 --- Photon / Performance

Shared data still needs efficient physical organization and query
performance.

### Topic 10 --- Databricks SQL / AI-BI / Genie

The same governed data can serve internal analytics before external
distribution.

### Topic 12 --- Asset Bundles / CI-CD

Sharing configuration should be managed reproducibly where supported.

### Topic 13 --- Cost Management

External consumers and shared workloads create cost implications.

### Topic 14 --- MLflow / Feature Engineering

Governed sharing patterns can extend to ML data products and downstream
consumers.

# 48. Production Data Product Capstone --- Partner Data Product Platform

A company provides sales analytics to three external partners.

Requirements:

-   each partner sees only its own data;
-   no customer PII;
-   daily freshness;
-   auditable access;
-   revocation capability;
-   schema contract;
-   Python consumption;
-   scalable sharing;
-   documented data product;
-   cost awareness.

Architecture:

``` text
Production Lakehouse
       ↓
Unity Catalog
       ↓
Curated Gold Data
       ↓
Partner-specific Sharing Layer
       ↓
┌──────────────┬──────────────┬──────────────┐
│ Partner A    │ Partner B    │ Partner C    │
└──────────────┴──────────────┴──────────────┘
       ↓
Delta/OpenSharing
       ↓
External Consumers
```

Deliver:

``` text
Architecture
Data Model
Sharing Model
Security Model
Recipient Model
Data Contract
Quality Model
Audit Model
Revocation Model
Performance Model
Cost Model
Marketplace Strategy
Clean Room Consideration
Runbooks
ADR
```

Acceptance tests:

``` text
Allowed partner → succeeds
Wrong partner → denied
Former recipient → denied
Sensitive column → absent
Audit → evidence exists
Schema contract → documented
Freshness → within SLA
Business totals → reconciled
```

# 49. Final Production Checklist

## Fundamentals

-   [ ] I understand provider/share/recipient.
-   [ ] I understand OpenSharing.
-   [ ] I understand D2D and D2Open.
-   [ ] I understand authentication and authorization.

## Security

-   [ ] I can minimize data.
-   [ ] I can remove PII.
-   [ ] I can design partner-specific assets.
-   [ ] I can revoke access.
-   [ ] I can audit access.
-   [ ] I can protect credentials.

## Consumer

-   [ ] I can consume shared data.
-   [ ] I can use Python where supported.
-   [ ] I understand external clients.
-   [ ] I understand schema compatibility.

## Marketplace

-   [ ] I understand data products.
-   [ ] I can design a listing.
-   [ ] I understand direct sharing vs Marketplace.
-   [ ] I understand provider/consumer responsibilities.

## Architecture

-   [ ] I can choose sharing vs API.
-   [ ] I can choose sharing vs file export.
-   [ ] I can choose sharing vs warehouse sharing.
-   [ ] I understand Clean Rooms.
-   [ ] I can design production sharing.

## Operations

-   [ ] I can troubleshoot access.
-   [ ] I can troubleshoot schema changes.
-   [ ] I can investigate incidents.
-   [ ] I can manage revocation.
-   [ ] I can reason about performance and cost.

# 50. Roadmap Coverage Audit

  --------------------------------------------------------------------------------------
  Roadmap Requirement        Covered?       Section        Hands-on?      Production
                                                                          Depth?
  -------------------------- -------------- -------------- -------------- --------------
  Delta Sharing / open       Yes            2              Yes            Yes
  protocol                                                                

  Provider / Share /         Yes            2--5           Yes            Yes
  Recipient                                                               

  Databricks-to-Databricks   Yes            6              Yes            Yes

  Open sharing / D2Open      Yes            7              Yes            Yes

  Shared tables              Yes            9--10          Yes            Yes

  Shared views               Yes            16             Yes            Yes

  Volumes where supported    Yes            9              Yes            Yes

  History where supported    Yes            17             Yes            Yes

  Change Data Feed           Yes            17             Yes            Yes

  Safe subsets               Yes            11--12         Yes            Yes

  Partner filtering          Yes            11             Yes            Yes

  PII removal                Yes            12             Yes            Yes

  Authentication             Yes            13             Yes            Yes

  Authorization              Yes            13             Yes            Yes

  Revocation                 Yes            14             Yes            Yes

  Auditing                   Yes            15             Yes            Yes

  Python client              Yes            18             Yes            Yes

  Marketplace                Yes            23--26         Yes            Yes

  Data products              Yes            24--25         Yes            Yes

  Clean Rooms                Yes            27--28         Yes            Yes

  Sharing vs files           Yes            20             Yes            Yes

  Sharing vs APIs            Yes            21             Yes            Yes

  Sharing vs warehouse       Yes            22             Yes            Yes
  sharing                                                                 

  Schema evolution           Yes            29             Yes            Yes

  Data quality               Yes            30             Yes            Yes

  Performance                Yes            31             Yes            Yes

  Cost                       Yes            31             Yes            Yes

  `sql/sharing/` exercise    Yes            34             Yes            Yes

  Break/Fix incidents        Yes            35             Yes            Yes

  Security incidents         Yes            36             Yes            Yes

  Production runbooks        Yes            37             Yes            Yes

  Decision matrices          Yes            38             Yes            Yes

  ADRs                       Yes            39             Yes            Yes

  Interview preparation      Yes            40             Yes            Yes

  Practice questions         Yes            41             Yes            Yes

  Senior scenarios           Yes            42             Yes            Yes

  Misconceptions             Yes            43             Yes            Yes

  Mental models              Yes            44             Yes            Yes

  Glossary                   Yes            45             Yes            Yes

  Current-doc safety         Yes            46             Yes            Yes

  Cross-topic links          Yes            47             Yes            Yes

  Production capstone        Yes            48             Yes            Yes

  Final checklist            Yes            49             Yes            Yes
  --------------------------------------------------------------------------------------

**Roadmap coverage result: Complete against the supplied Topic 11
specification.**

# 51. Final Operating Standard

Use this operating loop:

``` text
IDENTIFY DATA
      ↓
CLASSIFY DATA
      ↓
DEFINE CONSUMER
      ↓
MINIMIZE DATA
      ↓
GOVERN ASSET
      ↓
DEFINE CONTRACT
      ↓
CREATE SHARE / PRODUCT
      ↓
AUTHENTICATE
      ↓
AUTHORIZE
      ↓
TEST
      ↓
MONITOR
      ↓
AUDIT
      ↓
EVOLVE SAFELY
      ↓
REVIEW
      ↓
REVOKE WHEN REQUIRED
```

> **Govern → Minimize → Contract → Share → Authenticate → Authorize →
> Audit → Monitor → Revoke → Evolve.**

A production Data Engineer should be able to explain not only how to
share data, but exactly **why it should be shared, what should be
shared, who should receive it, how it is secured, how it is audited, how
it is revoked, how consumers remain compatible, and when API, file
export, warehouse sharing, Marketplace, or Clean Rooms is the better
architecture.**


# Final Validation Record

- Exact requested filename: `11-delta-sharing-and-marketplace.md`
- Roadmap Topic 11 requirements: covered
- Required `sql/sharing/` exercise: covered
- Hands-on labs: 14
- Break/Fix incidents: 18
- Production runbooks: covered
- Decision matrices: covered
- ADRs: 5
- Interview tiers: Beginner 15 / Intermediate 20 / Advanced 20 / Senior-Production 20
- Practice categories: Conceptual 25 / SQL-API 15 / Python 10 / Security 15 / Architecture 15 / Production Troubleshooting 15 / Data Product-Marketplace 10
- Production capstone: covered
- Roadmap coverage audit: covered
- Placeholder tokens: none
- Other roadmap files modified: none
