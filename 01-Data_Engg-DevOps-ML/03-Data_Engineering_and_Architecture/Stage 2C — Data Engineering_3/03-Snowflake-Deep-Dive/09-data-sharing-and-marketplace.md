# Topic 09 — Data Sharing and the Marketplace

**Target roadmap path:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/09-data-sharing-and-marketplace.md`  
**Hands-on lab:** `experiments/09_sharing/`  
**Audience:** Data engineers progressing toward production ownership of governed data products.

> **Scope and currency note:** This lesson follows Topic 09 in `roadmap-Snowflake-Deep-Dive.md`. SQL examples are templates for a controlled lab, not commands executed against a live Snowflake account. Snowflake sharing capabilities, account prerequisites, Marketplace availability, and billing details can vary by account configuration and product changes; check the linked official documentation before production rollout.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain provider accounts, consumer accounts, shares, listings, and imported databases.
- Explain why same-region Secure Data Sharing exposes live provider-managed data without a conventional export and copy into the consumer account.
- Create a share, grant supported objects, authorize a consumer account, and consume the share.
- Design a secure view that exposes only a partner's permitted order rows and approved columns.
- Distinguish direct shares, listings, Marketplace products, reader accounts, replication, and physical exports.
- Explain cross-region/cross-cloud requirements, Cross-Cloud Auto-fulfillment, and associated costs.
- Allocate compute, storage, transfer, support, and product-governance responsibilities between provider and consumer.
- Plan approvals, revocation, audit, schema versioning, SLAs, and failure handling.
- Recognize when data clean rooms or Snowflake Native Apps may fit a collaboration or distribution use case.
- Compare Snowflake sharing with Delta Sharing, BigQuery sharing (formerly Analytics Hub), and S3-based exports.

## 2. Prerequisites and lab safety

You should already understand:

- Snowflake databases, schemas, tables, views, warehouses, and SQL.
- Role-based access control and least privilege, including `USAGE`, `SELECT`, and object ownership.
- Secure views and row-level restrictions at a conceptual level.
- Basic cost categories: storage, warehouse compute, and data transfer.

**Use fictional records only.** Do not use production PII or customer data in this lab. The provider and consumer examples below are templates. A real cross-account test requires two eligible Snowflake accounts, the correct region/configuration, a separately authenticated consumer session, and permission to create/import shares. A local simulation is useful for SQL design but does **not** prove cross-account behavior.

## 3. Core mental model

### 3.1 Provider-to-consumer architecture

```text
PROVIDER ACCOUNT                                      CONSUMER ACCOUNT
┌─────────────────────────────┐                      ┌──────────────────────────┐
│ Provider-owned source data  │                      │ Imported shared database │
│  ORDERS_RAW                  │                      │  PARTNER_ORDERS           │
│       │                      │   share metadata     │        │                 │
│       ▼                      │ ───────────────────► │        ▼                 │
│ SECURE VIEW                  │  access is granted   │ Consumer role + warehouse│
│  filter rows + select cols   │                      │ SELECT (read-only)        │
│       │                      │                      └──────────────────────────┘
│       ▼                      │
│ SHARE ── authorized account  │
└─────────────────────────────┘

Provider retains and governs source data. Consumer runs its own queries and
pays for its query compute on a normal consumer account. No consumer-owned
physical table copy is created merely by creating the imported database.
```

Secure Data Sharing uses Snowflake's services layer and metadata to expose provider-managed objects. A consumer creates a read-only database from the share. The shared database does not add a second consumer storage copy of the shared table data. This is not the same as exporting files, replicating data to another region, or a consumer choosing to materialize a local copy.

### 3.2 Terms

| Term | Meaning | Operational consequence |
|---|---|---|
| **Provider** | Account that owns the data objects and offers access | Pays to store and maintain provider data; defines the shared object surface and governance |
| **Consumer** | Eligible account receiving access | Uses its own roles and warehouse to query shared objects; shared objects are read-only |
| **Share** | Named set of database objects and authorized consumer accounts | Defines what objects are available to whom; not a file or physical copy |
| **Imported database** | Consumer-side database created from a share | Read-only access point; consumer grants its own roles access to it |
| **Direct share** | Share offered directly to specific consumer account(s) | Simple for same-region account-to-account sharing; does not itself solve cross-region requirements |
| **Listing** | Discoverable or private data-product offer, including Marketplace listings | Supports product metadata, onboarding, commercial models, and cross-region fulfillment options |
| **Reader account** | Provider-managed account for a consumer without its own Snowflake account | Provider owns/administers it and pays its warehouse credits; it is not a full independent consumer account |
| **Replication** | Copies database/share state to another region/account as configured | Has replication, storage, and data-transfer implications; enables regional availability |
| **Export** | Writes a physical dataset or files to an external destination | Creates a separate data copy whose security, freshness, retention, and deletion must be governed independently |

### 3.3 Secure sharing versus replication versus export

| Dimension | Secure Data Sharing (same region) | Replication / cross-region fulfillment | Physical export (e.g. S3 files) |
|---|---|---|---|
| Data access | Consumer queries provider-managed shared objects | Consumer accesses data fulfilled/replicated to another region according to product design | Consumer receives independently stored files or tables |
| Conventional consumer copy | No copy of shared table data merely from importing the share | A regional copy is maintained to serve the other region | Yes, a physical copy is produced |
| Freshness | Live provider object state, subject to query and object semantics | Depends on replication/fulfillment refresh behavior and configuration | Depends on export schedule and ingestion pipeline |
| Consumer compute | Consumer's warehouse on a standard consumer account | Consumer's query compute plus provider fulfillment/replication costs as applicable | Consumer compute/processing and storage costs in destination systems |
| Provider cost | Provider storage; operational work; potentially listing/product costs | Provider storage plus replication/transfer/auto-fulfillment costs | Export compute/transfer and provider storage until source/export lifecycle ends |
| Revocation | Remove consumer from share or remove object access; future queries lose access | Remove access and manage replicated/listing state; propagation and fulfillment behavior must be checked | Revocation does not erase copies already downloaded; external deletion/retention workflow required |
| Best fit | Governed, near-live Snowflake-to-Snowflake access | Consumers in other regions/clouds or listing fulfillment | Portability, offline processing, non-Snowflake systems, or explicit copy requirements |

**Important:** “No copy” does not mean “no cost,” “no risk,” “no replication,” or “no way to persist data downstream.” A consumer can still extract query results or materialize data outside the shared database if its privileges and tools permit it. Contracts and controls should address permitted downstream use.

## 4. Beginner — how sharing works

### 4.1 Object access and read-only behavior

A provider creates a share, grants required database/schema usage and `SELECT` on supported tables or views, then adds consumer accounts. The consumer creates an imported database from the share and grants local roles access to it. The consumer cannot update or delete provider-owned shared tables or create objects inside the imported database. The consumer can still join shared data with local data in its own queries and can create local objects in a separate database if permitted.

Typical provider workflow:

1. Identify the approved data product and consumer.
2. Create a dedicated, narrow view rather than sharing a broad raw table.
3. Grant only the database/schema/object privileges needed by the share.
4. Add the approved consumer account identifier.
5. Test from the actual consumer account using a least-privilege role.
6. Document ownership, freshness, schema contract, usage rights, costs, and revocation process.

Typical consumer workflow:

1. Receive the share identifier and access authorization.
2. Use a role with the necessary global privileges (commonly `IMPORT SHARE` and `CREATE DATABASE`, or `ACCOUNTADMIN` in a lab if permitted by policy).
3. Create an imported database from the share.
4. Grant the imported database or shared database roles to local consumer roles.
5. Query using the consumer's own warehouse and monitor cost.

### 4.2 Role and privilege assumptions

The examples use a lab role called `SHARE_PROVIDER_ADMIN`. In a real account, `CREATE SHARE` is a global privilege held by `ACCOUNTADMIN` by default but delegable. To grant source objects to a share, the executing role must own the share (or have the documented grant-management authority) and have the required privileges on the source objects and namespace with `GRANT OPTION`, or equivalent ownership/grant authority. To add or remove consumer accounts with `ALTER SHARE`, the role needs `OWNERSHIP` on the share and the account-level `MANAGE SHARE TARGET` privilege; granting `CREATE SHARE` to a role does not necessarily grant `MANAGE SHARE TARGET` automatically. In practice, confirm `USAGE` on the database and schema and `SELECT` on the view are grantable to the share before running the grant statements. Do not routinely use `ACCOUNTADMIN` merely to run data-sharing queries; delegate the narrow privileges and test them in a sandbox.

The exact grants depend on whether the share uses account-level imported privileges or provider-defined database roles, and on the object types being shared. The simplest lab below uses direct grants on a secure view. For production, consider database roles when consumers need different privilege slices within the shared database.

## 5. Intermediate — partner-specific secure views

### 5.1 Example: sharing orders with a partner

Assume a fictional provider has orders for multiple partners. Partner `NORTHSTAR` may see only its own rows, and must not see internal notes or payment tokens. A safe design exposes a view that:

- Selects only approved columns.
- Filters rows using an explicit partner-to-consumer-account mapping.
- Uses a **secure view** for sharing.
- Keeps the mapping table under provider control.
- Is tested in a real consumer account before any sensitive dataset is shared.

```sql
-- Run in the provider account with a role authorized to create objects.
CREATE DATABASE IF NOT EXISTS PARTNER_DATA_LAB;
CREATE SCHEMA IF NOT EXISTS PARTNER_DATA_LAB.SHARING;

CREATE OR REPLACE TABLE PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE (
    ORDER_ID           NUMBER,
    ORDER_DATE         DATE,
    PARTNER_CODE       VARCHAR,
    CUSTOMER_REGION    VARCHAR,
    ORDER_TOTAL        NUMBER(12,2),
    STATUS             VARCHAR,
    INTERNAL_NOTES     VARCHAR,
    PAYMENT_TOKEN      VARCHAR
);

INSERT INTO PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE VALUES
  (1001, '2026-01-02', 'NORTHSTAR', 'NORTH', 125.00, 'SHIPPED', 'internal note A', 'tok_fake_A'),
  (1002, '2026-01-03', 'SOUTHWIND', 'SOUTH',  80.50, 'PENDING', 'internal note B', 'tok_fake_B'),
  (1003, '2026-01-04', 'NORTHSTAR', 'NORTH', 310.00, 'PAID',    'internal note C', 'tok_fake_C');

-- Use the account identifier format returned by the consumer-account onboarding
-- procedure. Validate CURRENT_ACCOUNT() in the consumer account before launch.
CREATE OR REPLACE TABLE PARTNER_DATA_LAB.SHARING.PARTNER_ACCOUNT_MAP (
    CONSUMER_ACCOUNT_ID VARCHAR NOT NULL,
    PARTNER_CODE        VARCHAR NOT NULL,
    ACTIVE              BOOLEAN NOT NULL DEFAULT TRUE
);

-- Replace this fictional placeholder with the actual approved consumer identifier.
INSERT INTO PARTNER_DATA_LAB.SHARING.PARTNER_ACCOUNT_MAP
    (CONSUMER_ACCOUNT_ID, PARTNER_CODE, ACTIVE)
VALUES ('<CONSUMER_ACCOUNT_IDENTIFIER>', 'NORTHSTAR', TRUE);

CREATE OR REPLACE SECURE VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS AS
SELECT
    o.ORDER_ID,
    o.ORDER_DATE,
    o.PARTNER_CODE,
    o.CUSTOMER_REGION,
    o.ORDER_TOTAL,
    o.STATUS
FROM PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE AS o
JOIN PARTNER_DATA_LAB.SHARING.PARTNER_ACCOUNT_MAP AS m
  ON m.PARTNER_CODE = o.PARTNER_CODE
WHERE m.ACTIVE = TRUE
  AND m.CONSUMER_ACCOUNT_ID = CURRENT_ACCOUNT();
```

**Why this design:** the view does not expose `INTERNAL_NOTES` or `PAYMENT_TOKEN`, and it filters rows by the consumer account's identity matched to a provider-maintained mapping. The mapping must be maintained and tested by the provider. The literal placeholder is not runnable; replace it with the actual identifier returned by a test in the intended consumer account. Snowflake account identifier functions and naming formats can differ by context; do not assume a display name and a legacy account locator are interchangeable.

**Security caveats:**

- Do not treat a view filter as a substitute for access control on every other object in the share. Share only the intended view and required namespace privileges.
- Do not add the source table or mapping table to the share unless separately approved and required. A secure view can reference provider-side objects without making those objects directly queryable by the consumer; validate the supported dependency and grant requirements for the actual design.
- Ensure the view predicate is not bypassable through another shared object, another view, or an overly broad listing.
- Account identity is a practical tenant key only when the business relationship is one account per partner. If multiple partner organizations or users share one consumer account, use a different, explicitly designed entitlement model; do not infer a user's identity from `CURRENT_ACCOUNT()`.
- Test unauthorized account behavior and empty/missing/duplicate mapping rows. A missing mapping should return zero rows, not broaden access.
- The view filters what is returned; it does not prevent a partner from retaining results it is legitimately allowed to query.

### 5.2 Grant the view through a share

Replace `ORG_NAME.CONSUMER_ACCOUNT_NAME` with the exact organization/account identifier accepted by the account's current Snowflake syntax. Use the identifier supplied by the consumer's administrator; do not guess it from an email or display name.

```sql
-- Provider account
USE ROLE SHARE_PROVIDER_ADMIN;

-- Fail if this share already exists; inspect and clean up only a confirmed disposable lab share.
CREATE SHARE PARTNER_ORDERS_SHARE;

GRANT USAGE ON DATABASE PARTNER_DATA_LAB
  TO SHARE PARTNER_ORDERS_SHARE;
GRANT USAGE ON SCHEMA PARTNER_DATA_LAB.SHARING
  TO SHARE PARTNER_ORDERS_SHARE;
GRANT SELECT ON VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS
  TO SHARE PARTNER_ORDERS_SHARE;

ALTER SHARE PARTNER_ORDERS_SHARE
  ADD ACCOUNTS = ORG_NAME.CONSUMER_ACCOUNT_NAME;

SHOW GRANTS TO SHARE PARTNER_ORDERS_SHARE;
SHOW GRANTS OF SHARE PARTNER_ORDERS_SHARE;
```

`SHOW GRANTS TO SHARE` inspects the objects/privileges included in the share. `SHOW GRANTS OF SHARE` reports consumer accounts that have actually created a database from that share; it can be empty even when the share has already been made available to a consumer. Use `SHOW SHARES` to inspect the share's authorized account list, and verify the account identifier carefully because adding a nonexistent or mistyped account may not produce the intended sharing relationship.

If the consumer is in a different region or cloud, a direct share may not be sufficient. Use a supported listing with Cross-Cloud Auto-Fulfillment or the documented replication workflow, with the necessary account linking, organization settings, permissions, and cost approvals. Do not attempt to solve a region mismatch by repeatedly changing the account name.

### 5.3 Consumer creates a database from the share

Run the following in the **consumer account**, not the provider account. `ORG_NAME.CONSUMER_ACCOUNT_NAME` in `FROM SHARE` is the provider account identifier as recognized by the consumer. `CREATE DATABASE` from a share requires `CREATE DATABASE` and `IMPORT SHARE` (or an authorized administrative role).

```sql
-- Consumer account
USE ROLE ACCOUNTADMIN; -- lab convenience only; prefer delegated least-privilege roles in production
CREATE DATABASE PARTNER_ORDERS_DB
  FROM SHARE ORG_NAME.PROVIDER_ACCOUNT_NAME.PARTNER_ORDERS_SHARE;

-- Grant access to an ordinary consumer role.
-- For a share that does not use provider-defined database roles, grant access
-- to the imported database's shared objects with IMPORTED PRIVILEGES.
GRANT IMPORTED PRIVILEGES ON DATABASE PARTNER_ORDERS_DB
  TO ROLE PARTNER_ANALYST;

USE ROLE PARTNER_ANALYST;
SELECT ORDER_ID, ORDER_DATE, PARTNER_CODE, ORDER_TOTAL, STATUS
FROM PARTNER_ORDERS_DB.SHARING.V_PARTNER_ORDERS
ORDER BY ORDER_ID;
```

The exact imported schema name follows the shared object's schema. Confirm with `SHOW SCHEMAS IN DATABASE PARTNER_ORDERS_DB` and `SHOW VIEWS IN SCHEMA ...` if the provider uses another schema name. For shares without provider-defined database roles, the consumer grants `IMPORTED PRIVILEGES` on the imported database to an appropriate local role; this grants access to the objects made available through that share, not arbitrary provider objects. If the provider has shared database roles, grant the specific imported database role instead. Follow the provider's documented access model. The role performing the grant must own the imported database or have the required grant-management authority, and `PARTNER_ANALYST` must already be granted to the user who will execute `USE ROLE PARTNER_ANALYST`.

**Expected observation:** the `PARTNER_ANALYST` role sees only rows mapped to the consumer account and only the approved view columns. It cannot modify the imported database. A provider-side mapping change or source-data change can affect subsequent queries because the share is live in the same-region model.

### 5.4 Object revocation and consumer behavior

Provider can revoke the view from the share or remove the consumer account. Removing access blocks future access to the share/object; it does not recall data the consumer previously queried or exported.

```sql
-- Provider: revoke one object while leaving the share itself in place.
REVOKE SELECT ON VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS
  FROM SHARE PARTNER_ORDERS_SHARE;

-- Or remove the consumer from the share (use exact identifier).
ALTER SHARE PARTNER_ORDERS_SHARE
  REMOVE ACCOUNTS = ORG_NAME.CONSUMER_ACCOUNT_NAME;
```

After revocation, test from the consumer session. Depending on whether the database remains imported and whether the object was revoked versus the entire account removed, metadata may remain visible but querying the object should no longer be authorized. Do not promise that all consumer-side metadata disappears instantly in every UI. Verify actual query access and consult current documentation for the precise lifecycle. Regranting is a new authorization decision, not a substitute for an incident review.

## 6. Listings and Snowflake Marketplace

### 6.1 Direct share versus listing

A direct share is a straightforward way to provide data to known Snowflake accounts in the same region. A listing is a data-product wrapper with descriptive metadata and consumer onboarding/discovery; listings may be private or public depending on the product and approval path. Listings are the normal choice when publishing a product for broader discovery, offering paid access, or using cross-region/cross-cloud auto-fulfillment.

A listing should include:

- Product owner and support contact.
- Description, intended use, grain, refresh cadence, and known limitations.
- Data dictionary, sample queries, and versioning policy.
- Classification of sensitive fields and legal/contractual permitted use.
- Pricing or free-access terms, if applicable.
- Regional availability and any data residency constraints.
- Deprecation date and consumer migration guidance for breaking changes.

### 6.2 Consumer workflow for Marketplace data

The consumer discovers a listing, reviews provider terms and data documentation, obtains any required approval/subscription, and uses the shared data product in Snowflake. A listing may be free or paid; free does not mean zero compute cost or zero operational risk. The consumer still pays for query compute in a standard Snowflake account, and should assess quality, freshness, license/usage restrictions, and join keys before production use.

```sql
-- After subscribing through the supported listing workflow, discover imported databases.
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE <IMPORTED_LISTING_DATABASE>;
SHOW TABLES IN SCHEMA <IMPORTED_LISTING_DATABASE>.<SCHEMA_NAME>;

-- Example join with local fictional data. Replace names after inspecting the listing.
SELECT l.PRODUCT_CODE, l.CATEGORY, s.UNITS_SOLD
FROM <IMPORTED_LISTING_DATABASE>.<SCHEMA_NAME>.PRODUCT_LOOKUP AS l
JOIN LOCAL_ANALYTICS.MART.SALES_SUMMARY AS s
  ON s.PRODUCT_CODE = l.PRODUCT_CODE;
```

Marketplace listings can change and availability varies. The lab asks you to subscribe to a free dataset **if one is available to your account and region**. Do not assume a particular dataset will remain free, be present in every region, or require no approval.

### 6.3 Reader accounts

Reader accounts let a provider serve consumers who do not have their own Snowflake account. The provider creates, owns, configures, and supports the reader account; the reader can consume data only from that provider. The provider is responsible for warehouse credits consumed in the reader account, so configure warehouse controls and resource monitors. Reader accounts are restricted compared with standard consumer accounts; for example, they are not a general-purpose environment for loading and modifying arbitrary data. Use a standard consumer account when the partner needs a full Snowflake account to combine shared data with its own datasets.

Creating a reader account typically requires `ACCOUNTADMIN` or a role with the global `CREATE ACCOUNT` privilege and the relevant feature enabled. Do not create one without approval because its compute usage is charged to the provider.

## 7. Cross-region and cross-cloud sharing

### 7.1 Why extra configuration is required

Direct sharing is a same-region pattern. To serve consumers in another region or cloud, use supported cross-region replication or a listing with Cross-Cloud Auto-Fulfillment. These workflows require the relevant accounts and organization settings to be configured, the data product to be eligible, and a plan for regional data transfer and storage. Auto-fulfillment automates parts of the fulfillment process; it does not eliminate transfer or storage costs.

```text
Provider primary region
  ├── source database + share
  └── listing configured for cross-cloud fulfillment
             │
             ▼  supported replication/fulfillment
Consumer region / cloud
  └── fulfilled data product + consumer queries
```

Before enabling it:

1. Confirm the consumer's region and cloud platform.
2. Confirm the account and organization support the required replication/fulfillment features.
3. Review data residency, regulatory, contractual, and customer restrictions.
4. Estimate recurring replication/transfer/storage costs and establish an owner.
5. Decide freshness/refresh requirements and failure alerting.
6. Test region mismatch and revocation scenarios before launch.

For views referencing multiple databases, verify the documented cross-region replication requirements for all dependencies. Do not assume that replicating one database automatically fulfills every dependency in a multi-database secure view.

## 8. Advanced topics

### 8.1 Data clean rooms — awareness

A data clean room is a governed collaboration pattern that allows approved analysis across parties' data while restricting what participants can see or export. It is useful when the goal is joint measurement, audience overlap, or other controlled analysis rather than handing a partner unrestricted row-level data. Clean rooms are not magic anonymization: privacy risk depends on permitted queries, output controls, minimum cohort rules, identifiers, governance, and the threat model. Validate product availability and configuration for the target account and region.

### 8.2 Snowflake Native Apps — awareness

Native Apps allow a provider to package application logic for installation/use by consumer accounts within Snowflake's supported application model. They are appropriate when the product includes logic, workflows, or interfaces in addition to a dataset. Separate the data product's access grants from application permissions, version the app, test upgrade behavior, and document what data the app reads or writes. Native Apps are not interchangeable with a simple share and may have separate packaging, review, security, and distribution requirements.

### 8.3 Monetization and service-level agreements

A data product's commercial model can include free access, paid listings, private contracts, or service arrangements. The product contract should define:

- Scope, allowed purpose, prohibited onward redistribution, and retention expectations.
- Availability and freshness objectives, including how freshness is measured.
- Schema compatibility policy, notification lead time, and deprecation support.
- Data quality expectations, correction windows, and incident notification.
- Support hours, escalation path, and responsibility for query/warehouse costs.
- Pricing basis, billing owner, transfer/fulfillment charges, and usage metrics.
- Privacy, security, residency, and deletion obligations.

An SLA should distinguish platform availability from the provider's data freshness and correctness. Do not promise that the source is always current merely because the share is live.

### 8.4 Shared-schema versioning

Treat shared schemas as APIs. Prefer additive changes first, and do not silently rename or remove columns used by consumers. A practical model:

- `V1` remains stable for existing consumers.
- `V2` introduces incompatible changes with a migration guide.
- Consumer query telemetry and feedback inform deprecation.
- Automated contract tests verify column names, types, nullability assumptions, row-grain, and key uniqueness.
- Deprecation includes a date, contact, and rollback path.

Use secure views as the published contract rather than exposing mutable internal tables. A secure view is not automatically schema-versioned; versioning is an explicit product-design responsibility.

## 9. Governance, security, and operations

### 9.1 Outbound-sharing approval workflow

```text
Request
  ↓
Data owner + privacy/security classification
  ↓
Legal/contract + purpose + region review
  ↓
Design approved view / row scope / column allowlist
  ↓
Peer review grants + test with authorized and unauthorized consumers
  ↓
Approve share/listing and document cost owner
  ↓
Monitor access, freshness, schema changes, and spend
  ↓
Renew, change scope, or revoke access
```

Minimum controls:

- Maintain an inventory of outbound shares, listings, consumers, owners, data classes, purpose, and expiry/review date.
- Require a named data owner and business sponsor.
- Share narrow secure views, not broad base tables, by default.
- Verify row and column restrictions from the consumer context.
- Review consumer account identifiers and regions independently.
- Audit changes to shares, object grants, listing settings, and entitlement mappings.
- Reconcile active shares with contracts and offboarding events.
- Set alerts/monitoring for unusual query volume and costs where supported.
- Have an incident procedure for accidental disclosure, including revoke, evidence preservation, partner notification, and legal/privacy review.

### 9.2 Revocation is not deletion

Removing a consumer from a share prevents future authorized access through that share, but cannot erase query results already downloaded, cached, exported, or incorporated into the consumer's own systems. Contractual deletion requirements therefore need a downstream data inventory and attestation process. For highly sensitive data, minimize fields, apply retention controls, and prefer aggregate or clean-room outputs where appropriate.

### 9.3 Threat scenarios and mitigations

| Threat / failure | Why it happens | Prevention and response |
|---|---|---|
| Base table shared accidentally | Convenience grants expose extra columns/rows | Share a reviewed secure view; inspect `SHOW GRANTS TO SHARE`; test as consumer |
| Wrong partner sees data | Mapping table or tenant predicate is wrong | Fail closed; test missing/duplicate/inactive mapping rows and a second account; peer-review predicate |
| Sensitive columns exposed indirectly | Another view/table in the share reveals the data | Inventory all shared objects and dependencies; grant only approved object set |
| Consumer continues using data after revocation | They already exported or persisted query results | Contractual controls, logging, partner notification, and downstream deletion attestations |
| Region mismatch | Direct share attempted across regions | Use documented replication or listing auto-fulfillment; validate region and transfer cost |
| Consumer query costs spike | Large joins/scans or unbounded workloads | Educate consumer, set budgets/alerts where available, monitor listing/warehouse usage; reader accounts require provider-side controls |
| Breaking schema change | Provider alters a shared view without compatibility plan | Version the product, contract tests, change notice, and deprecation window |
| Stale/poor-quality data | Source pipeline or refresh process fails | Publish freshness metadata, monitor upstream pipeline, define SLA and correction process |
| Legal/region violation | Destination region or use purpose not approved | Pre-sharing legal/privacy/residency review and explicit data-flow inventory |
| Marketplace dataset is unsuitable | Terms, grain, refresh, or join keys misunderstood | Review listing documentation, license, sample data, quality and update cadence before production |

### 9.4 Auditing and revocation operations

Use supported `SHOW` commands to inspect the share and its grants, and account usage views where available to review query and cost behavior. Exact monitoring views, retention, latency, and required privileges vary. Do not assume that one query history view proves every consumer copied or retained data; Snowflake query logs show activity inside the platform, not every downstream use.

```sql
-- Provider-side inspection
SHOW SHARES;
SHOW GRANTS TO SHARE PARTNER_ORDERS_SHARE;
SHOW GRANTS OF SHARE PARTNER_ORDERS_SHARE;

-- Review imported/available shares in the relevant account (visibility is role-dependent)
SHOW SHARES IN ACCOUNT;
```

Interpret these commands differently: `SHOW SHARES` lists shares available to the account and the accounts authorized for an outbound share; `SHOW GRANTS TO SHARE` lists object privileges granted to that share; `SHOW GRANTS OF SHARE` lists accounts that have actually created an imported database from the share. An empty `SHOW GRANTS OF SHARE` result does not by itself prove the share was not authorized for a consumer.

Keep change tickets and query evidence according to your organization's logging policy. If an accidental exposure is suspected, remove the affected account/object access first when safe, preserve relevant evidence, identify the time window and affected objects, and coordinate with security/legal/privacy owners. Do not wait for a perfect root-cause analysis before containing an active exposure.

## 10. Cost model and ownership

| Cost / responsibility | Provider | Standard consumer | Reader-account consumer |
|---|---|---|---|
| Storage of original shared data | Pays | No storage charge for the shared table data merely because it is imported | Provider's underlying storage remains provider responsibility |
| Query warehouse compute | Provider pays for provider's own queries | Consumer pays for its own warehouse queries | Provider pays for reader-account warehouse credits |
| Replication / cross-cloud fulfillment | Typically provider-side fulfillment/replication charges; confirm product configuration and contract | Consumer may have its own regional compute costs; check contract and product terms | Provider-managed environment and charges apply; check configured feature |
| Export/downstream copy | Pays for provider export operations if exporting | Destination owner pays for external storage/compute and ingestion as applicable | Provider or external destination owner pays according to the workflow |
| Support and data quality | Owns source quality and provider-side product support as contracted | Owns consumer-side query patterns and local use | Provider also administers/supports the reader account users |

Secure Data Sharing does not add shared table storage charges to the consumer account, but the provider continues to pay to store its data. Cross-region fulfillment may introduce transfer and storage charges. A free listing can still create compute charges. Reader-account warehouse credits are charged to the provider, so a resource monitor and warehouse policy are essential.

Use current account usage and cost-monitoring views to reconcile actual spend. Do not estimate price from bytes alone without checking region, cloud, service type, currency, contract, and current rates.

## 11. Comparison with alternatives

| Dimension | Snowflake Secure Data Sharing / Listings | Delta Sharing | BigQuery sharing (Analytics Hub) | S3-based exports |
|---|---|---|---|---|
| Primary model | Share Snowflake objects through provider/consumer accounts; listings add discovery/product delivery | Open protocol for sharing data, commonly stored in cloud object storage, with clients using supported connectors | Publisher lists data; subscriber gets a read-only linked dataset in BigQuery | Export files/objects to a bucket and grant destination access or deliver files |
| Physical copy for initial access | No consumer copy of shared table data in same-region sharing; cross-region fulfillment can replicate | Usually accesses provider data through protocol; storage location and connector implementation matter | Linked dataset provides access without a conventional subscriber dataset copy | Yes, export produces separate objects/files |
| Consumer query engine | Snowflake | Compatible client engines/connectors, such as supported Spark/Delta ecosystem | BigQuery | Consumer chooses engine and must parse/ingest files |
| Governance surface | Snowflake grants, secure views, policies, shares, listings, provider controls | Provider/recipient/credential and protocol controls; exact filtering depends on implementation | Google Cloud IAM, Analytics Hub/listing permissions, BigQuery dataset controls | IAM/bucket policies, KMS, manifests, lifecycle policies, contracts, ingestion controls |
| Freshness | Live provider object for same-region sharing; cross-region fulfillment has configured behavior | Depends on provider table and protocol/connector behavior | Linked dataset references shared source; source and service semantics apply | Snapshot at export time until next export |
| Cost emphasis | Provider storage; consumer query compute; transfer/replication/fulfillment where applicable | Cloud storage, request/transfer, provider platform and consumer compute costs depend on deployment | Consumer BigQuery query processing and applicable publisher/service costs | Export/transfer, destination storage, requests, ingestion and query compute |
| Revocation | Remove share/object access, but prior exports remain | Revoke credentials/share access; prior downloaded data remains | Unsubscribe/remove listing access; prior copies or derived outputs require separate governance | Remove bucket access, but already downloaded copies remain |
| Best fit | Snowflake-to-Snowflake governed data products | Cross-platform open sharing for supported Delta/client ecosystems | BigQuery-native sharing and data exchange | Broad portability, offline transfer, non-compatible systems, or explicit snapshot delivery |

No option automatically solves privacy, quality, legal purpose, or downstream retention. Compare operational fit, ecosystem compatibility, row/column controls, consumer needs, regional requirements, cost, and revocation expectations.

## 12. Hands-on lab — `experiments/09_sharing/`

### 12.1 Lab goals and prerequisites

You will create a secure view, share it with a second account, query it from the consumer account, revoke access, and optionally consume a free Marketplace listing.

Required for the full lab:

- Provider Snowflake account with data-sharing enabled and authority to create a share.
- Second eligible consumer account in the **same region** for the direct-share path.
- Correct provider/consumer account identifiers.
- Provider privileges to create lab objects and grant supported objects to the share.
- Consumer role with `IMPORT SHARE` and `CREATE DATABASE`, or authorized account administrator for the lab.
- A consumer warehouse and role with access to the imported database.
- Approval to create resources and incur compute costs.

If you do not have a second account, complete the local preparation and threat-model tests, but mark cross-account steps **NOT EXECUTED**. A local query against the secure view proves the SQL predicate only; it does not prove share grants, consumer identity evaluation, or revocation behavior across accounts.

### 12.2 Suggested repository structure

```text
experiments/09_sharing/
├── README.md
├── 01_provider_setup.sql
├── 02_secure_view_and_share.sql
├── 03_consumer_import_and_query.sql
├── 04_revoke_and_verify.sql
├── 05_marketplace_join.sql
└── expected-observations.md
```

Keep credentials and real account identifiers out of source control. Use placeholders or a protected environment configuration. Do not store secrets in SQL scripts.

### 12.3 Step 1 — setup fictional provider data

Run as a lab role that owns the lab database/schema and can create the table and mapping table. Use a dedicated disposable database; never run `CREATE OR REPLACE` against production objects.

```sql
CREATE DATABASE IF NOT EXISTS PARTNER_DATA_LAB;
CREATE SCHEMA IF NOT EXISTS PARTNER_DATA_LAB.SHARING;

CREATE OR REPLACE TABLE PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE (
  ORDER_ID NUMBER,
  ORDER_DATE DATE,
  PARTNER_CODE VARCHAR,
  CUSTOMER_REGION VARCHAR,
  ORDER_TOTAL NUMBER(12,2),
  STATUS VARCHAR,
  INTERNAL_NOTES VARCHAR,
  PAYMENT_TOKEN VARCHAR
);

INSERT INTO PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE VALUES
  (2001, '2026-02-01', 'NORTHSTAR', 'NORTH', 125.00, 'SHIPPED', 'fake note 1', 'fake_token_1'),
  (2002, '2026-02-02', 'SOUTHWIND', 'SOUTH',  80.50, 'PENDING', 'fake note 2', 'fake_token_2'),
  (2003, '2026-02-03', 'NORTHSTAR', 'NORTH', 310.00, 'PAID',    'fake note 3', 'fake_token_3');

CREATE OR REPLACE TABLE PARTNER_DATA_LAB.SHARING.PARTNER_ACCOUNT_MAP (
  CONSUMER_ACCOUNT_ID VARCHAR NOT NULL,
  PARTNER_CODE VARCHAR NOT NULL,
  ACTIVE BOOLEAN NOT NULL DEFAULT TRUE
);
```

Do not insert the consumer mapping until you have confirmed which identifier function/value will match from the actual consumer account. A bad mapping can cause either empty results or unauthorized disclosure.

### 12.4 Step 2 — create and test the secure view

```sql
CREATE OR REPLACE SECURE VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS AS
SELECT o.ORDER_ID, o.ORDER_DATE, o.PARTNER_CODE,
       o.CUSTOMER_REGION, o.ORDER_TOTAL, o.STATUS
FROM PARTNER_DATA_LAB.SHARING.ORDERS_SOURCE o
JOIN PARTNER_DATA_LAB.SHARING.PARTNER_ACCOUNT_MAP m
  ON m.PARTNER_CODE = o.PARTNER_CODE
WHERE m.ACTIVE
  AND m.CONSUMER_ACCOUNT_ID = CURRENT_ACCOUNT();
```

Test the predicate safely before sharing. In the provider account, `CURRENT_ACCOUNT()` identifies the provider account, not the future consumer; the view may therefore return zero rows unless the provider itself is mapped. That is expected for a consumer-specific view. To simulate a consumer for a secure-view test, Snowflake supports the session parameter `SIMULATED_DATA_SHARING_CONSUMER` for secure views and secure materialized views:

```sql
-- Provider-side preflight only; replace with the consumer's verified account locator.
ALTER SESSION SET SIMULATED_DATA_SHARING_CONSUMER = CONSUMER_ACCOUNT_LOCATOR;
SELECT ORDER_ID, PARTNER_CODE
FROM PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS
ORDER BY ORDER_ID;
ALTER SESSION UNSET SIMULATED_DATA_SHARING_CONSUMER;
```

Use the supported parameter only for preflight validation, and restore the session setting afterward. Alternatively, use a separate **local-only diagnostic query** with an explicit test partner code or a separate lab view that is never granted to a share. Do not temporarily remove the tenant predicate on the object intended for sharing and forget to restore it.

When the consumer account is available, verify `SELECT CURRENT_ACCOUNT()` there, insert the exact matching identifier into the provider's mapping table for `NORTHSTAR`, and test from the actual consumer account. Then test with a second account that is not mapped: it should return zero rows. Simulation helps validate secure-view filtering, but it does **not** prove share grants, imported-database behavior, or revocation across accounts. The real consumer-side negative test is required before production sharing.

### 12.5 Step 3 — create the share and grant the consumer

```sql
-- Provider account
-- Fail if this share already exists; inspect and clean up only a confirmed disposable lab share.
CREATE SHARE PARTNER_ORDERS_SHARE;
GRANT USAGE ON DATABASE PARTNER_DATA_LAB TO SHARE PARTNER_ORDERS_SHARE;
GRANT USAGE ON SCHEMA PARTNER_DATA_LAB.SHARING TO SHARE PARTNER_ORDERS_SHARE;
GRANT SELECT ON VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS
  TO SHARE PARTNER_ORDERS_SHARE;

ALTER SHARE PARTNER_ORDERS_SHARE
  ADD ACCOUNTS = ORG_NAME.CONSUMER_ACCOUNT_NAME;

SHOW GRANTS TO SHARE PARTNER_ORDERS_SHARE;
SHOW GRANTS OF SHARE PARTNER_ORDERS_SHARE;
```

**Verification:** confirm the intended view is the only data object granted. Confirm the intended consumer account identifier and region. Do not add the source table to the share “to make the view work” without reviewing the actual dependency and current sharing requirements; doing so could expose the base table.

### 12.6 Step 4 — import and query from the consumer account

```sql
-- Consumer account. This example assumes an authorized admin role and a disposable lab.
-- A delegated role needs CREATE DATABASE + IMPORT SHARE; creating PARTNER_ANALYST
-- additionally requires role-creation authority. Do not use ACCOUNTADMIN for routine queries.
CREATE DATABASE PARTNER_ORDERS_DB
  FROM SHARE ORG_NAME.PROVIDER_ACCOUNT_NAME.PARTNER_ORDERS_SHARE;

-- The following grants are run by the appropriate consumer-side database owner/admin.
CREATE ROLE IF NOT EXISTS PARTNER_ANALYST;
-- Ensure PARTNER_ANALYST is granted to the lab user before switching to it.
-- GRANT ROLE PARTNER_ANALYST TO USER <CONSUMER_LAB_USER>;
-- This database uses the imported-privileges model. If the provider shared
-- database roles, grant the specific imported database role instead.
GRANT IMPORTED PRIVILEGES ON DATABASE PARTNER_ORDERS_DB
  TO ROLE PARTNER_ANALYST;

USE ROLE PARTNER_ANALYST;
SELECT CURRENT_ACCOUNT();
SELECT * FROM PARTNER_ORDERS_DB.SHARING.V_PARTNER_ORDERS ORDER BY ORDER_ID;
```

Granting privileges on imported data may differ if the provider supplied shared database roles. In that case, inspect the imported database's shared database roles and grant the specific role to the local account role instead of granting `IMPORTED PRIVILEGES` indiscriminately.

**Expected observations:**

- Only the partner's mapped rows are visible.
- `INTERNAL_NOTES` and `PAYMENT_TOKEN` are not columns in the view.
- The consumer cannot mutate the shared view/table.
- Consumer query compute is charged to the consumer's warehouse in a standard account.

### 12.7 Step 5 — revoke and verify

Provider side:

```sql
REVOKE SELECT ON VIEW PARTNER_DATA_LAB.SHARING.V_PARTNER_ORDERS
  FROM SHARE PARTNER_ORDERS_SHARE;
```

Alternatively, to revoke the consumer's entire access:

```sql
ALTER SHARE PARTNER_ORDERS_SHARE
  REMOVE ACCOUNTS = ORG_NAME.CONSUMER_ACCOUNT_NAME;
```

Removing the account invalidates the imported database in the consumer account. If the provider later adds that account back, the consumer must create a new database from the share; the old imported database is not reactivated automatically.

Consumer side: execute the same `SELECT` again and record the actual error/behavior. Record which action you took (object revoke or account removal), whether metadata remains visible, and whether query execution is denied. Do not interpret prior successful results as proof that access remains active; query again after revocation.

### 12.8 Step 6 — Marketplace subscription and join

If a free Marketplace dataset is available to your account and region, review its listing terms and documentation, subscribe using the currently supported consumer workflow, then inspect the imported database and join it with local fictional data. Listing subscription UI and approval steps can change, so use the current Snowflake Marketplace documentation rather than assuming a fixed screen layout.

```sql
CREATE DATABASE IF NOT EXISTS LOCAL_ANALYTICS;
CREATE SCHEMA IF NOT EXISTS LOCAL_ANALYTICS.MART;
CREATE OR REPLACE TABLE LOCAL_ANALYTICS.MART.SALES_SUMMARY (
  PRODUCT_CODE VARCHAR,
  UNITS_SOLD NUMBER
);
INSERT INTO LOCAL_ANALYTICS.MART.SALES_SUMMARY VALUES ('P-100', 4), ('P-200', 9);

-- Replace the placeholders after discovering the subscribed listing's actual schema.
SELECT l.PRODUCT_CODE, l.CATEGORY, s.UNITS_SOLD
FROM <IMPORTED_LISTING_DATABASE>.<SCHEMA_NAME>.PRODUCT_LOOKUP l
JOIN LOCAL_ANALYTICS.MART.SALES_SUMMARY s
  ON s.PRODUCT_CODE = l.PRODUCT_CODE;
```

If no suitable free listing is available, document that the Marketplace step was not performed and use a second fictional local lookup table to practise the join. Clearly label this as a **local SQL alternative**; it does not prove subscription, listing permissions, or third-party data behavior.

### 12.9 Troubleshooting

| Symptom | Likely cause | Safe check |
|---|---|---|
| `CREATE SHARE` denied | Missing global `CREATE SHARE` privilege or provider sharing disabled | Ask the account administrator to verify privilege and feature availability |
| `GRANT ... TO SHARE` denied | Role lacks ownership/grant authority or required namespace access | Inspect ownership and grants; do not solve by granting broad admin rights permanently |
| Consumer cannot find share | Wrong provider identifier, consumer not added, region mismatch, or provider setup issue | Confirm identifiers and region with both account admins |
| Cannot create imported database | Missing `IMPORT SHARE` or `CREATE DATABASE`, or wrong `FROM SHARE` identifier | Use a properly delegated consumer role and check the exact provider account/share name |
| View returns zero rows | Mapping missing/inactive, identifier mismatch, partner code mismatch | Run `SELECT CURRENT_ACCOUNT()` in consumer; compare exact stored identifier and mapping rows |
| Consumer sees another partner's rows | Predicate or mapping flaw, incorrect share scope, or unintended shared object | Revoke access while investigating; inspect the secure view and all grants; run negative tests |
| View fails after source changes | Dependency or schema incompatibility | Review provider query/view compilation and shared product contract; use backward-compatible changes |
| Cross-region consumer cannot connect | Direct share is not the right path or fulfillment is not configured | Check supported replication/listing auto-fulfillment requirements and data residency approval |
| Marketplace dataset not available | Region, account eligibility, listing status, approval, or listing changed | Use current listing docs; complete the clearly labeled local alternative if needed |
| Unexpected cost | Warehouse size, query volume, reader account credits, or replication/fulfillment | Inspect warehouse/query and transfer/replication usage views; apply resource governance |

### 12.10 Cleanup

Perform cleanup only after capturing the observations you need. Run in the provider account with the appropriate ownership/grant authority. Remove the consumer from the share first if access must end immediately, then drop the disposable share and lab objects. Be careful: `DROP` and `CREATE OR REPLACE` are destructive in the named scope.

```sql
-- Provider: if not already revoked, remove the consumer first.
ALTER SHARE PARTNER_ORDERS_SHARE
  REMOVE ACCOUNTS = ORG_NAME.CONSUMER_ACCOUNT_NAME;
DROP SHARE IF EXISTS PARTNER_ORDERS_SHARE;
DROP DATABASE IF EXISTS PARTNER_DATA_LAB;
```

Consumer account, after access is revoked and lab results are recorded:

```sql
DROP DATABASE IF EXISTS PARTNER_ORDERS_DB;
DROP DATABASE IF EXISTS LOCAL_ANALYTICS;
```

Do not drop an imported database that contains other teams' work. Do not drop a Marketplace-provided database unless you own that imported database and have confirmed the effect. If the reader account or auto-fulfillment configuration was created, clean it up under the account's documented lifecycle and cost procedures.

### 12.11 Lab completion record

Record the following in `experiments/09_sharing/expected-observations.md`:

- Provider account/region and consumer account/region (avoid publishing sensitive identifiers in public repositories).
- Which steps were actually executed versus simulated.
- Share grant inspection results.
- Positive and negative row-filter tests.
- Which object/consumer revocation was performed and the consumer's observed result.
- Marketplace listing name and terms if used, or reason the local alternative was used.
- Any unexpected costs, errors, or limitations.

Never state that cross-account behavior was validated if only the local secure view was queried.

## 13. Production rollout checklist

### Before sharing

- [ ] Business purpose, data owner, recipient, and allowed use are documented.
- [ ] Data classification and privacy/legal review are complete.
- [ ] Region/cloud and residency requirements are approved.
- [ ] Only necessary columns and rows are exposed.
- [ ] Secure view and mapping logic have peer review and negative tests.
- [ ] Source tables and internal mapping tables are not unintentionally shared.
- [ ] Provider/consumer grants follow least privilege.
- [ ] Cost owner and monitoring plan are defined.
- [ ] Schema contract, freshness, SLA, support, and deprecation terms are documented.

### After sharing

- [ ] Monitor product usage and provider-side costs.
- [ ] Reconcile active recipients with approvals and contracts.
- [ ] Test revocation during a controlled exercise.
- [ ] Notify consumers before breaking schema changes.
- [ ] Review cross-region replication/fulfillment usage and failures.
- [ ] Reassess purpose and permissions at renewal/offboarding.
- [ ] Maintain a downstream-copy and deletion process for any data consumers may persist.

## 14. Common mistakes

1. **Sharing base tables by convenience.** This can expose extra rows and columns; publish a narrow secure view instead.
2. **Assuming the share is a backup or export.** The consumer's access depends on the provider share and does not create an independent data copy.
3. **Assuming cross-region direct shares work automatically.** Use the documented replication or listing auto-fulfillment path and budget for it.
4. **Confusing no consumer storage charge with no cost.** Provider storage and consumer compute remain real costs; transfer/fulfillment can add cost.
5. **Using an untested tenant predicate.** Test a permitted account and an unauthorized account from their actual consumer sessions.
6. **Treating `CURRENT_ACCOUNT()` as a user identity.** It identifies an account context, not an individual user. Use a different entitlement model when several partners/users share an account.
7. **Revoking access and assuming downstream copies disappear.** Previously exported results need separate contractual and operational handling.
8. **Changing a shared schema without compatibility planning.** Consumers may break; use stable contracts, versions, tests, and notices.
9. **Forgetting reader-account billing.** Provider pays reader-account warehouse credits; configure resource controls.
10. **Assuming a free Marketplace listing is risk-free.** Validate license, quality, freshness, region, and query cost.
11. **Claiming a local test proves cross-account access.** It does not test imported databases, share grants, or consumer identity evaluation.
12. **Ignoring multi-database dependencies.** Cross-region replication and shared secure-view dependencies need deliberate configuration.

## 15. Practice questions with answers

### Q1. Why does Secure Data Sharing avoid a conventional consumer data copy?

**Answer:** The provider grants access to supported provider-owned objects through Snowflake's sharing layer. The consumer creates a read-only imported database that references the shared data. This does not create a consumer storage copy of the shared table data merely by importing the share.

### Q2. Does the consumer pay nothing because the shared data is not stored in its account?

**Answer:** No. A standard consumer pays for the warehouse compute used to query shared data. The provider continues to pay for its storage, and cross-region fulfillment/replication may incur provider-side transfer and storage costs. Reader-account warehouse credits are paid by the provider.

### Q3. Why share a secure view rather than a base table?

**Answer:** The view provides an explicit contract of approved columns and a row predicate. Sharing a base table can expose data that was not intended for the partner. The view still requires careful grants, dependency review, and tests.

### Q4. What does `CURRENT_ACCOUNT()` protect against, and what does it not protect against?

**Answer:** In a properly designed view, it can be used as one input to match the querying account to a provider-maintained entitlement mapping. It does not identify individual users inside the account, prove a legal identity, or compensate for a flawed mapping or another shared path to the base data.

### Q5. What is the difference between a share and a listing?

**Answer:** A share is the access mechanism for objects and consumer accounts. A listing wraps a data product in discovery/onboarding and commercial metadata and supports product distribution workflows, including cross-region auto-fulfillment where configured.

### Q6. Can direct sharing be assumed to work across different regions or cloud platforms?

**Answer:** No. A direct share is a same-region pattern. Use documented replication or a listing with Cross-Cloud Auto-Fulfillment, after validating account configuration, data residency, and costs.

### Q7. What does revocation guarantee?

**Answer:** It removes future authorized access through the revoked share/object. It does not recall previously queried, downloaded, exported, or derived data held by the consumer.

### Q8. What is the difference between a reader account and a standard consumer account?

**Answer:** A reader account is created and managed by the provider, can consume only that provider's data, and its warehouse credits are billed to the provider. A standard consumer account is independently managed and can combine shared data with its own data, paying for its own compute.

### Q9. When might Delta Sharing, BigQuery sharing, or S3 exports be a better fit?

**Answer:** Delta Sharing may fit an open, cross-platform ecosystem supported by its protocol/connectors; BigQuery sharing fits BigQuery-native publisher/subscriber workflows; S3 exports fit portability, offline processing, or explicit physical-copy requirements. The choice depends on governance, recipient tooling, freshness, cost, and downstream-copy risk.

### Q10. Does a secure view make the product automatically versioned and SLA-backed?

**Answer:** No. Versioning, compatibility, support, freshness targets, and SLA commitments must be designed and governed explicitly.

## 16. Topic 09 checkpoint

You are ready to proceed when you can check each item without relying on rote memorization:

- [ ] Explain why same-region Secure Data Sharing involves no conventional consumer copy.
- [ ] Create a share and grant only approved objects.
- [ ] Explain how a consumer creates an imported database and queries it read-only.
- [ ] Design and test a secure view so a partner sees only permitted rows and columns.
- [ ] Explain the difference between direct shares, listings, Marketplace products, and reader accounts.
- [ ] Explain provider storage costs, consumer compute costs, reader-account billing, and cross-region fulfillment costs.
- [ ] Explain why region mismatch requires a supported replication or listing workflow.
- [ ] Revoke object/account access and state what revocation cannot erase.
- [ ] Describe a schema versioning and consumer notification strategy.
- [ ] Compare Snowflake sharing with Delta Sharing, BigQuery sharing, and S3 exports.
- [ ] Distinguish actual cross-account lab results from local simulations.

**Roadmap learning instruction:** Sketch the orders-sharing design, enumerate schema-change, revocation, and region-mismatch failure modes, then complete the `experiments/09_sharing/` lab or clearly document which cross-account steps were unavailable.

## 17. Official references

Use current official documentation for syntax, account eligibility, feature availability, and billing before applying these patterns in production:

1. [About Secure Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro)
2. [Create and configure shares](https://docs.snowflake.com/en/user-guide/data-sharing-provider)
3. [ALTER SHARE syntax, account targets, and revocation behavior](https://docs.snowflake.com/en/sql-reference/sql/alter-share)
4. [Share-management privileges for non-ACCOUNTADMIN roles](https://docs.snowflake.com/en/user-guide/security-access-privileges-shares)
5. [Share secure database objects](https://docs.snowflake.com/en/user-guide/data-sharing-gs)
6. [Use secure objects to control data access, including simulated consumer testing](https://docs.snowflake.com/en/user-guide/data-sharing-secure-views)
7. [Consume imported data](https://docs.snowflake.com/en/user-guide/data-share-consumers)
8. [Manage reader accounts](https://docs.snowflake.com/en/user-guide/data-sharing-reader-create)
9. [Share data across regions and cloud platforms](https://docs.snowflake.com/en/user-guide/secure-data-sharing-across-regions-platforms)
10. [Auto-fulfillment costs](https://docs.snowflake.com/en/collaboration/provider-understand-cost-auto-fulfillment)
11. [Understand data transfer costs](https://docs.snowflake.com/en/user-guide/cost-understanding-data-transfer)
12. [Read Delta Sharing tables](https://docs.delta.io/delta-sharing/)
13. [BigQuery sharing / Analytics Hub](https://cloud.google.com/analytics-hub)
14. [View and subscribe to BigQuery sharing listings](https://cloud.google.com/bigquery/docs/analytics-hub-view-subscribe-listings)

---

**Production principle:** treat every share as an externally consumable data product, not as a casual grant. Minimize the exposed surface, prove row/column restrictions from the consumer context, define cost and schema ownership, and plan revocation and downstream data handling before onboarding the recipient.
