# Topic 09 — Dataplex, IAM, and Data Governance

> **Stage:** Stage 2C — Data Engineering_3  
> **Path:** `Stage 2C — Data Engineering_3/04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/09-dataplex-iam-and-governance.md`  
> **Level:** Advanced  
> **Estimated study time:** 8–12 hours, plus optional cloud lab time  
> **Primary platform:** Google Cloud, BigQuery, Dataplex Universal Catalog / Knowledge Catalog, Cloud Logging, Sensitive Data Protection, Terraform

## How to use this lesson

This lesson follows Topic 09 in `roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md`. Governance comes after BigQuery, ingestion, Pub/Sub, Dataflow, Dataproc, and Composer because it must secure the complete data lifecycle, not just one table.

Use synthetic data only in the lab. Read the design sections before running commands, inspect every Terraform plan, and use separate test identities. Never grant broad roles to your everyday identity to make a lab pass.

**Terminology note (checked against current Google Cloud documentation in October 2026):** Google documentation has begun using **Knowledge Catalog** for the product formerly called **Dataplex Universal Catalog**. This lesson uses “Dataplex Universal Catalog / Knowledge Catalog” on first reference and “catalog” thereafter. Some APIs, Terraform resources, URLs, IAM roles, and existing projects retain `dataplex` or `datacatalog` names. API/resource names are not necessarily renamed when a product label changes.

**Execution boundary:** All SQL, commands, Terraform, and expected results below are instructional lab materials. Unless you run them in your own project, no cloud resources have been created, no permissions have been tested against live identities, and no scan, lineage event, or perimeter has been verified in a real environment.

---

## 1. Learning objectives and prerequisites

By the end, you should be able to:

1. Design least-privilege access for analysts, engineers, and a finance team handling synthetic sensitive fields.
2. Distinguish project/folder/org IAM, dataset/table access, policy-tag column access, dynamic masking, and row access policies.
3. Publish a safe BigQuery authorized view without granting direct source-table access.
4. Find administrative and data-access activity in Cloud Audit Logs and query exported logs in BigQuery.
5. Explain catalog discovery, metadata, business glossaries, data products, data quality, profiling, and lineage.
6. Use VPC Service Controls, CMEK, and Sensitive Data Protection as complementary controls, not substitutes for IAM.
7. Manage supported policy resources with Terraform and conduct repeatable access reviews.
8. Define measurable exit criteria for a governed platform spanning BigQuery, Pub/Sub, Dataflow, Dataproc, and Composer.

### Prerequisites

- BigQuery Standard SQL, datasets, tables, views, partitioning, and query-cost guardrails.
- Cloud Storage, Pub/Sub, Dataflow, Dataproc, and Cloud Composer concepts from Topics 04–08.
- Basic IAM and service-account knowledge.
- Terraform workflow: `fmt`, `validate`, `plan`, reviewed `apply`, state protection, and cleanup.
- A Google Cloud project where you are authorized to create isolated lab resources. An organization administrator is needed for organization-scoped controls such as some policy-tag/IAM administration and VPC Service Controls.

### Lab safety contract

- Use a disposable project and synthetic values such as `user_001`, `analyst@example.invalid`, and fake phone numbers.
- Do not copy real customer data into the lab.
- Do not use a personal owner account as the analyst or finance test principal.
- Do not grant `roles/owner`, `roles/editor`, or project-wide `roles/bigquery.admin` to analysts.
- Do not create a VPC Service Controls perimeter in a shared or production organization as a beginner exercise.
- Set a budget alert, keep the table tiny, and delete resources when finished.
- A `403` can be a successful negative test if the principal is intentionally denied. Record the identity, resource, action, error, and timestamp; do not “fix” the test by widening access.

---

## 2. Governance principles and shared-responsibility boundaries

Governance is a set of enforceable technical controls, ownership processes, evidence, and operating procedures. A catalog entry or a policy document is useful, but neither alone prevents a principal from reading data.

### 2.1 The control plane is layered

| Control | Main question answered | What it does **not** guarantee |
|---|---|---|
| IAM | Which principal can perform which action on which resource? | Does not automatically filter individual rows or hide selected column values. |
| Dataset/table permissions | Can a principal discover/read/update this BigQuery object? | Dataset-level access can be broader than intended; it is not a substitute for column/row controls. |
| Policy tags and column-level security | Can the principal read this protected column? | Does not classify all data automatically or remove sensitive values from other copies. |
| Dynamic data masking | What representation can a permitted query return to this principal? | Is not encryption, anonymization, or a guarantee that every derived output is safe. |
| Row access policies | Which rows of a table can the principal see? | Does not replace table-level permission or protect copies exported elsewhere. |
| Authorized views/datasets/routines | Can a principal query a deliberately scoped interface without direct access to underlying tables? | An unsafe view or overly powerful authorized routine can disclose too much. |
| Cloud Audit Logs | What activity did Google Cloud record? | Logging is not prevention; Data Access logs may need explicit enablement and retention/routing decisions. |
| Catalog/metadata/glossary | What does an asset mean, who owns it, and how is it related? | Metadata does not automatically enforce every access policy. |
| Data quality/profiling | Does data satisfy defined expectations and what are its observed characteristics? | A passing scan does not prove confidentiality, correctness outside the rules, or legal compliance. |
| Encryption at rest / CMEK | How is stored data cryptographically protected and who controls key lifecycle? | Encryption at rest alone does not stop an authorized principal from querying readable data. |
| VPC Service Controls | Which service-to-service data paths cross a protected perimeter? | Does not replace IAM, row/column security, endpoint controls, or careful export permissions. |
| Sensitive Data Protection | Where might sensitive data exist, and how can supported workflows de-identify it? | Detection can produce false positives/negatives; findings require triage and remediation. |

### 2.2 Shared responsibility

Google Cloud secures the underlying cloud infrastructure and provides configurable security primitives. Your organization remains responsible for configuring identity, roles, data classification, perimeter boundaries, encryption-key access, retention, monitoring, incident response, and lawful processing.

A service being listed as suitable for a regulated workload does **not** make the workload compliant by itself. Compliance depends on the applicable laws, contracts, jurisdiction, data types, processing purposes, organisational policies, and evidence that the controls operate effectively.

### 2.3 Threat model for this module

Assume:
- an analyst needs regional sales totals but not raw contact details;
- a finance analyst needs a narrow set of finance fields;
- a pipeline service account needs to write curated rows but should not manage users;
- an engineer can deploy a pipeline but should not automatically read all PII;
- a compromised credential may attempt to copy data to an untrusted project;
- an accidental table change may introduce malformed or sensitive values.

Design controls for least privilege, separation of duties, restricted sharing, observable activity, quality gates, and recovery.

---

## 3. Google Cloud IAM and resource hierarchy

### 3.1 Inheritance and scope

Google Cloud IAM policies can be attached at organization, folder, project, and supported resource levels. Permissions inherited from a parent can broaden effective access. Always inspect inherited grants before adding a narrower binding.

For BigQuery, distinguish:
- **Project IAM:** can grant job creation, resource administration, or broad access through roles.
- **Dataset access:** dataset-level permissions and legacy dataset access entries govern operations on datasets and contained resources, subject to BigQuery's permission model.
- **Table/view access:** grants can be made on individual tables and views where supported.
- **Column access:** policy tags and BigQuery data policies control access to tagged columns.
- **Row access:** row access policies filter rows for principals that also have table data access.

A user typically needs `bigquery.jobs.create` in the project where the query job runs and appropriate data permissions on the referenced tables. Job creation permission does not imply permission to read every table. Likewise, permission to query a table does not imply permission to administer the project.

### 3.2 Predefined versus custom roles

Prefer a narrow predefined role when it matches the job. Use custom roles only when no predefined role fits and the permission set is understood, tested, versioned, and reviewed.

| Role example | Typical purpose | Caution |
|---|---|---|
| `roles/bigquery.jobUser` | Create query jobs in a project | Does not itself grant table data access. |
| `roles/bigquery.dataViewer` | Read table data and metadata at granted scope | Too broad if granted project-wide where sensitive tables coexist. |
| `roles/bigquery.dataEditor` | Create/update data objects and data at granted scope | Not a default analyst role. |
| `roles/bigquery.dataOwner` | Broad dataset/data administration | Reserve for trusted dataset owners. |
| `roles/bigquery.admin` | Broad BigQuery administration | High privilege; not for routine analysts or pipeline execution. |
| `roles/bigquery.filteredDataViewer` | System-managed permission used by row access policies | Do not grant directly through ordinary IAM; policy machinery grants it. |
| `roles/dataplex.catalogViewer` | Read catalog metadata where supported | Catalog visibility is not table-data access. |
| `roles/datalineage.viewer` | View data lineage where supported | Does not grant access to the underlying table contents. |
| `roles/datacatalog.categoryFineGrainedReader` | Read raw data in columns protected by policy tags | Grant on the appropriate policy-tag taxonomy/tag scope; this is raw access, not masking. |
| `roles/bigquerydatapolicy.maskedReader` | Read data through configured masking policies | Prefer granting at the specific data-policy resource where supported; do not also grant raw Fine-Grained Reader unless intended. |
| `roles/datacatalog.categoryAdmin` / policy-tag administration roles | Manage taxonomies/policy tags depending on current API/product role naming | Verify exact role names and permissions in the target project; old/new naming can coexist. |

The exact minimum role depends on the operation, resource, API, and product version. Confirm permissions in the current IAM role reference and test using a dedicated principal.

### 3.3 Example persona matrix

| Persona | Job project | Curated dataset | Restricted source | Policy tag | Catalog |
|---|---|---|---|---|---|
| Analyst | Job User | Read approved view/table | No direct read | Masked or denied | Viewer |
| Finance analyst | Job User | Read finance-approved data | No direct read by default | Explicitly approved for required fields only | Viewer |
| Pipeline runtime service account | Job User plus narrow write/read roles | Write only required destination | Read only required input | No automatic raw PII access | Only needed metadata permissions |
| Data steward | No broad job access unless needed | Metadata/quality responsibilities | Data access only if justified | Manage classification as delegated | Metadata and quality permissions |
| Security administrator | Investigation-specific access | No routine query access required | Audit access through approved process | Manage taxonomy IAM | Security/audit permissions |
| Terraform deployment identity | Deployment permissions limited to lab resources | Manage only resources in scope | Avoid routine data reads | Taxonomy/policy permissions if needed | Create/manage lab scans |

### 3.4 Service-account hygiene

- Prefer attached service accounts, Workload Identity Federation, and short-lived credentials over downloaded service-account keys.
- Avoid shared service accounts across unrelated workloads.
- Use separate identities for deployment, pipeline runtime, scan execution, and human access.
- Grant the runtime identity only the source read, destination write, job creation, and secret access it requires.
- Avoid granting service-account impersonation broadly; `iam.serviceAccounts.actAs` and token-creation permissions are sensitive.
- Rotate/revoke credentials and investigate unused keys. Organization policies can restrict key creation.
- Do not put keys in source control, container images, Composer variables, notebooks, or logs.
- Treat Terraform's service account as a privileged identity: a plan can create powerful grants even if the person running it is not directly granted those roles.

### 3.5 Access design exercise

For each requested operation, write the principal, resource, permission, intended scope, and negative test.

| Operation | Scope choice | Negative test |
|---|---|---|
| Analyst runs approved query | Job project + approved view | Analyst cannot query raw source table |
| Pipeline loads daily facts | Runtime identity + target dataset/table | Runtime identity cannot alter project IAM |
| Finance reads selected sensitive field | Policy tag/data policy or approved view, with explicit approval | General analyst cannot read raw field |
| Data steward runs quality scan | Scan execution identity and source read permissions | Steward cannot grant project-wide Editor |
| Security reviews access | Logging/audit scope | Analyst cannot read unrelated security logs |

**Checkpoint:** never decide access by job title alone. Translate each workflow into exact permissions and resource scopes.

---

## 4. BigQuery dataset, table, column, and row access

### 4.1 Dataset access and table IAM

Use the narrowest practical scope. Dataset-level read access is convenient for a coherent data domain, but can accidentally expose every present and future table in that dataset. Put sensitive raw data in a separate dataset from analyst-ready outputs when the risk model warrants it.

Review:
- project IAM and inherited folder/organization grants;
- dataset access entries and IAM policy;
- table/view IAM where used;
- authorized view/dataset/routine configuration;
- policy tags and data policies;
- row access policies;
- job-creation rights in the query project.

Avoid assuming that a table's apparent UI sharing panel shows every effective grant. Use IAM Policy Troubleshooter, policy inspection, and a real query under the intended identity.

### 4.2 Column-level security with policy tags

Policy tags classify a column and can enforce column-level access control. They are backed by a taxonomy in a location compatible with the dataset/table location. The taxonomy must have fine-grained access control activated for this use. The tag is attached to the column schema; access is granted to principals on the policy tag.

Important operational details:
- A table column can have only one policy tag.
- The taxonomy and table must be in the same BigQuery location for a tag to be attached; replicate taxonomies intentionally across locations if needed.
- `CREATE TABLE` DDL does not currently set policy tags in the same way as a table schema API/CLI workflow. Create or update the schema through supported APIs, `bq` schema JSON, or a supported Terraform/API path.
- Tagging alone is not enough: verify enforcement is on, the tag is attached to the intended field, and the principal does not have raw access through another path.
- The Fine-Grained Reader role (`roles/datacatalog.categoryFineGrainedReader`) grants raw access to protected columns. The BigQuery Masked Reader role (`roles/bigquerydatapolicy.maskedReader`) grants access to the masked representation when a masking data policy is configured. Prefer the Masked Reader grant at the specific data-policy resource; do not also grant Fine-Grained Reader to that principal unless raw access is explicitly intended. Verify current role names, supported binding scopes, and effective grants in your environment.
- IAM changes may take time to propagate. A test performed immediately after a grant/revocation may observe propagation delay.

A safe design classifies data before it is broadly published, rather than tagging it after broad access has already been granted.

### 4.3 Dynamic data masking

Dynamic masking is applied through BigQuery data policies associated with a policy tag. Depending on supported masking rules and data types, output can be masked as null, default values, or hashed content. The actual masking rule and principal bindings determine what each user sees.

Masking is useful when an analyst can perform a task using a reduced representation. It is not a replacement for access denial when the user should not see the column at all. Hashing is not automatically irreversible anonymization: low-entropy values may be guessed, linked, or reidentified. Null/default masks can also create misleading downstream analysis if users do not understand the semantics.

Verification must query the same column as:
1. an authorized raw-data identity;
2. a masked-data identity;
3. a denied identity.

Do not infer masking behavior from console configuration alone. Verify returned values and the effective policy/tag bindings. Result caching and IAM propagation can complicate testing; use a controlled test query, unique query text when needed, and an explicit test plan.

### 4.4 Row-level security

A row access policy is a SQL filter plus a grantee list. The querying principal must still have table data access, and the policy grants the special filtered-data permission needed to read the matching rows. Do not grant `roles/bigquery.filteredDataViewer` directly through ordinary IAM; it is system-managed for row-policy use.

Example for a synthetic table `governance_lab.sales`:

```sql
CREATE ROW ACCESS POLICY IF NOT EXISTS region_east_readers
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:region-east@example.invalid")
FILTER USING (region = 'EAST');

CREATE ROW ACCESS POLICY IF NOT EXISTS region_west_readers
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:region-west@example.invalid")
FILTER USING (region = 'WEST');

-- Separate, tightly controlled maintenance/raw-test identity only.
-- Do not add the EAST or WEST test identities to this policy.
CREATE ROW ACCESS POLICY governance_lab_full_access
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:governance-lab-raw@example.invalid")
FILTER USING (TRUE);
```

Replace the example group identities with real test groups in a disposable environment. `.invalid` is intentionally non-routable and is not a real identity. Use the actual test group's principal in a live lab. The `TRUE` policy is for a dedicated maintenance/raw-column test group only; it intentionally grants all rows and must not include regional analysts. Multiple policies are additive for a principal: rows matching any policy granted to that principal are visible.

Key caveats:
- A principal needs table-level read access **and** filtered-data permission through the row access policy.
- Multiple policies can interact; evaluate their combined effect rather than assuming the most restrictive filter wins. In particular, overlapping grants can broaden the rows visible to a principal.
- Table owners and principals with broad administrative privileges may be able to change or remove policies. Separate policy administration from query-only roles.
- Some query operations, features, or preview paths have limitations with row access policies; test the actual downstream use case.
- Row access policies are not a substitute for keeping sensitive data out of exported files, materialized copies, or downstream systems.

### 4.5 Combining controls

The access decision is cumulative: the principal must be able to access the table and query job; row policies filter rows; policy tags/data policies control protected columns; views may narrow fields and rows; VPC Service Controls may block a service request crossing a perimeter. A query can fail even when one layer appears correct.

Build a test matrix and record expected behavior before testing:

| Identity | Raw PII field | Masked field | EAST rows | WEST rows | Approved view |
|---|---|---|---|---|---|
| `raw_reader` (restricted test) | Allowed only if explicitly granted | N/A | Policy-dependent | Policy-dependent | Allowed |
| `masked_analyst` | Denied raw; masked output only if configured | Masked | Only authorized region(s) | Denied unless separately granted | Allowed |
| `region_east` | Denied unless separately granted | Depends on tag policy | Allowed | Denied | Allowed if view policy permits |
| `no_access` | Denied | Denied | Denied | Denied | Denied |

The lab later uses a simple, explicit separation between row and column tests so that a failure can be attributed to one control at a time.

---

## 5. Authorized views and controlled data sharing

### 5.1 Authorized views

An authorized view is a deliberately scoped logical or materialized view whose access to source data is authorized in the source dataset. A consumer can query the view without direct read access to the underlying source dataset. Grant the consumer access to the view/destination dataset and ensure the view SQL exposes only approved columns and rows.

Example:

```sql
CREATE OR REPLACE VIEW `SHARE_PROJECT.approved_sales.v_region_summary` AS
SELECT
  region,
  DATE_TRUNC(sale_date, MONTH) AS sale_month,
  SUM(amount) AS gross_amount,
  COUNT(*) AS order_count
FROM `SOURCE_PROJECT.governance_lab.sales`
GROUP BY region, sale_month;
```

This view intentionally excludes `customer_email` and `customer_token`. The view is not authorized merely because it exists. Configure the authorization entry on the source dataset using the supported BigQuery console, `bq`/API, or Terraform workflow for the provider version you use. Then grant consumer principals access to the destination view/dataset and query-job permission in their job project.

### 5.2 Authorized datasets

An authorized dataset authorizes the views contained in a designated dataset to access a shared source dataset. It is useful when many views form one governed publishing surface. It also increases the trust boundary: current and future views in the authorized dataset can gain access to the shared dataset. Restrict who can create or alter views in that destination dataset.

### 5.3 Authorized routines

Authorized routines can expose computations without granting callers direct access to the underlying tables. Supported types include table functions, UDFs, and stored procedures. A stored procedure can perform DDL/DML and potentially create, modify, or delete objects; only authorize routines whose full behavior is reviewed and whose callers are trusted to execute it.

### 5.4 Cross-project publication checklist

1. Separate source and consumer projects or datasets where appropriate.
2. Create a view that explicitly names permitted columns and rows; avoid `SELECT *`.
3. Test the view's SQL under the source owner identity.
4. Authorize the view/dataset against the source dataset.
5. Grant consumer access only to the published view/dataset.
6. Give consumer query-job creation in the job project.
7. Test that the consumer can query the view but cannot query the source table.
8. Review view changes as security-sensitive code.
9. Audit and periodically revalidate the authorization list.

---

## 6. Audit logging and access investigations

### 6.1 Admin Activity versus Data Access

Cloud Audit Logs distinguish activity categories:
- **Admin Activity:** administrative changes, such as changing IAM policies or creating/deleting resources. These logs are generally always on and cannot be disabled.
- **Data Access:** reads and writes to user data and certain administrative reads. These logs are generally disabled by default for many services and may need to be explicitly enabled for the relevant services and principals. There can be exceptions; consult the current service-specific audit-log matrix.
- **System Event:** Google Cloud system actions.
- **Policy Denied:** requests denied by security policy, where supported and emitted.

Do not assume a missing log proves no access occurred. Confirm that the service emits the event type, Data Access logging is enabled where required, the correct project/folder/organization is covered, the sink includes the log, and retention has not expired.

### 6.2 BigQuery audit event fields

Useful fields often include:
- `timestamp` and `receiveTimestamp`;
- `protoPayload.authenticationInfo.principalEmail` or principal subject;
- `protoPayload.serviceName`;
- `protoPayload.methodName`;
- `protoPayload.resourceName`;
- `protoPayload.status`;
- `protoPayload.metadata` and service-specific job metadata;
- `resource.type`, `logName`, and `severity`.

The exact structure varies by event. Treat logs as evidence that needs interpretation, not as a universal row-level business audit.

### 6.3 Export logs to BigQuery

A common pattern is:
1. Create a Cloud Logging sink that routes selected audit logs to a dedicated BigQuery dataset.
2. Grant the sink's writer identity the permissions required to write to the destination.
3. Define an appropriate retention and access policy for the log dataset.
4. Query the exported log tables after confirming their actual schema.

Example Logs Explorer filter:

```text
logName:"cloudaudit.googleapis.com"
protoPayload.serviceName="bigquery.googleapis.com"
```

Example filter for BigQuery Data Policy activity:

```text
protoPayload.serviceName="bigquerydatapolicy.googleapis.com"
```

### 6.4 Querying exported audit logs

Logging sink schemas and table names can vary by sink configuration and time partitioning. The following is a **schema-adaptation template**, not a guarantee that every exported table has these exact columns:

```sql
-- Replace PROJECT_ID, AUDIT_DATASET, and the table name after inspecting
-- the actual sink output schema in BigQuery.
SELECT
  timestamp,
  protopayload_auditlog.authenticationInfo.principalEmail AS principal,
  protopayload_auditlog.serviceName AS service_name,
  protopayload_auditlog.methodName AS method_name,
  protopayload_auditlog.resourceName AS resource_name,
  protopayload_auditlog.status.message AS status_message
FROM `PROJECT_ID.AUDIT_DATASET.cloudaudit_googleapis_com_data_access_*`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND protopayload_auditlog.serviceName = 'bigquery.googleapis.com'
ORDER BY timestamp DESC
LIMIT 500;
```

**Before running:** inspect `INFORMATION_SCHEMA.TABLES` and a few rows to identify the actual table and field types. The query above assumes the common Logging-to-BigQuery export schema in which `protopayload_auditlog` and its nested members are `STRUCT` fields. If your sink produces a different schema or table naming pattern, adapt the field paths and wildcard to the observed schema; do not wrap scalar/STRUCT members in `JSON_VALUE` unless the actual source field is JSON or JSON text.

A useful investigation joins audit events with `INFORMATION_SCHEMA.JOBS_BY_PROJECT` for job-level context where permissions and retention allow it. The jobs view is not a replacement for Cloud Audit Logs: its retention, fields, and visibility differ. Avoid collecting or broadly exposing query text if it can contain sensitive literals.

### 6.5 Investigation workflow

For a suspected unauthorized read:
1. Preserve the alert and record the time window, project, dataset/table, and principal.
2. Confirm Data Access audit logging and log-sink coverage for the period.
3. Search by service, principal, resource, and job/read methods.
4. Correlate job IDs and `INFORMATION_SCHEMA.JOBS_BY_PROJECT` where available.
5. Check IAM policy history, policy-tag IAM, row-policy changes, view SQL changes, and service-account impersonation.
6. Identify any export or downstream copy paths.
7. Contain the incident by revoking the specific grant/credential or blocking the relevant path; preserve evidence.
8. Assess impact, notify the designated incident owner, and follow the applicable response plan.
9. Add a preventive test and alert to stop recurrence.

---

## 7. Dataplex Universal Catalog / Knowledge Catalog and metadata management

### 7.1 What the catalog is for

The catalog provides a searchable governance and metadata layer across supported data assets. It helps teams discover resources, understand meaning, identify ownership, attach business context, and navigate relationships. Product labels and UI paths may change; APIs and IAM roles can retain `dataplex`, `datacatalog`, or `datalineage` names.

### 7.2 Lakes, zones, assets: understand the model and the evolution

Classic Dataplex Universal Catalog architecture used:
- **Lake:** a logical domain grouping.
- **Zone:** a logical grouping of data, often by processing or trust stage (for example, raw, curated, and published).
- **Asset:** a data resource attached to a zone, such as a Cloud Storage bucket or BigQuery dataset.

Treat these terms as conceptual building blocks when reviewing existing deployments and documentation. Current catalog capabilities increasingly emphasize entries, aspects, metadata, discovery, business glossaries, quality, and lineage across a broader estate. Do not assume every newer catalog workflow requires a classic lake/zone/asset topology or that every cloud resource is automatically governed merely because it is discoverable.

### 7.3 Discovery, metadata, and search

Discovery can extract technical metadata from supported sources. A discovery result is a starting point, not a certification of correctness or permission. Curate:
- business owner and technical owner;
- purpose and permitted use;
- classification and sensitivity;
- source system and refresh cadence;
- data contract and schema expectations;
- retention/deletion class;
- quality SLO and known limitations;
- lineage and downstream dependencies;
- support contact and incident route.

Metadata can itself be sensitive. Avoid embedding secrets, raw PII, access tokens, or sensitive query literals in descriptions, tags, glossary terms, or custom metadata.

### 7.4 Business glossary

A glossary defines a shared vocabulary of terms, categories, synonyms, and relationships, and links business concepts to data assets. Example terms:
- `Net Revenue`: finance-approved definition and exclusion rules.
- `Active Customer`: explicit time window and activity semantics.
- `Sensitive Contact Attribute`: fields classified as restricted.
- `Certified Sales Mart`: owner, refresh SLA, quality threshold, and intended consumers.

A glossary improves discoverability and reduces semantic ambiguity. It does not enforce access by itself.

### 7.5 Data products and data-mesh-style governance

A data product is a maintained interface to data with an owner, contract, quality expectations, access rules, discoverability, support model, and lifecycle. Domains can own products while a platform team supplies shared guardrails. A mesh-style approach decentralizes domain ownership but should not decentralize away security baselines, identity standards, classification, audit, or incident response.

Define for each product:
- accountable domain owner and technical steward;
- consumer personas and access-request process;
- source-of-truth definition and schema contract;
- freshness, completeness, validity, and availability targets;
- versioning and deprecation policy;
- PII classification and approved purpose;
- row/column controls and publication interface;
- lineage, quality scan, and incident contact;
- retention and deletion behavior.

---

## 8. Data-quality rules, scans, and monitoring

### 8.1 Quality rules are executable contracts

A data-quality scan should test meaningful failure modes, not merely whether a query runs. Typical dimensions:
- **Completeness:** required values are present.
- **Validity:** values fall in an allowed range or match a format.
- **Uniqueness:** business keys are unique at the intended grain.
- **Consistency:** related fields agree and reference values are valid.
- **Freshness:** data arrived within the expected window.
- **Volume/anomaly:** row counts or distributions remain within acceptable bounds.

A scan score is a result under a particular rule set and sampling/configuration. It is not a universal truth score. Record the rule version, scan time, sampled population, failure details, and remediation outcome.

### 8.2 Three useful example rules

For a synthetic sales table:
1. `order_id` is unique.
2. `amount` is non-null and non-negative.
3. `region` belongs to an approved set (`EAST`, `WEST`, `CENTRAL`).

Additional rules might check `sale_date` not in the future, `customer_token` non-null, or a relationship between status and cancellation date.

### 8.3 Data quality scans and operational alerts

Catalog data-quality scans can run on demand or on a schedule, publish supported results to the catalog, and use post-scan actions such as notifications when configured. Exact capabilities and Terraform fields depend on scan type and provider version. The lab provides a Terraform `google_dataplex_datascan` example with three table-condition expectations and a reproducible run/inspection path.

For each failed rule:
1. Preserve the scan job and result.
2. Determine whether the issue is source quality, transformation logic, schema drift, late data, or a faulty rule.
3. Quarantine bad records rather than silently dropping them.
4. Correct the source or transformation, then rerun.
5. Track failure rate and repeat incidents.
6. Prevent downstream publication until critical quality gates pass.

Do not assume that a scan automatically blocks a Composer DAG or BigQuery publication. Wire the scan result into an explicit orchestration gate if that behavior is required.

### 8.4 Profiling

Profiling summarizes distributions, null rates, cardinality, ranges, and other column characteristics. Profiles can reveal unexpected sensitive-looking fields or schema drift, but they can also disclose sensitive facts (for example, rare categories or a small group's range). Restrict profile results and avoid publishing detailed profiles to broad audiences.

---

## 9. Lineage, profiling, and data-product governance

### 9.1 Lineage types

- **Table/asset lineage:** relationships between inputs and outputs.
- **Column-level lineage:** supported relationships between source and derived columns.
- **Job/run lineage:** which execution produced a result.
- **Business lineage:** why the data exists and which product/report uses it.

The Data Lineage API and catalog integrations can display lineage from supported Google Cloud services. Coverage is integration-specific and may require APIs, IAM, service/job settings, and supported SDK versions. Dataflow lineage has product-specific source/sink and Beam SDK requirements; Managed Airflow/Composer and Managed Service for Apache Spark have their own support and configuration. Data not captured by built-in integrations may need an OpenLineage producer.

### 9.2 OpenLineage

OpenLineage is an open event standard for jobs, runs, and datasets. Knowledge Catalog can consume supported OpenLineage events through the Data Lineage API, allowing custom pipelines to appear alongside built-in lineage. The endpoint is a consumer of events, not a universal lineage producer. Current documented integration supports OpenLineage major version 1 with limitations on event types and payload/graph scale; check current documentation before relying on advanced facets.

### 9.3 Operational lineage checklist

- Enable the Data Lineage API in the relevant project.
- Confirm service-specific lineage settings and supported versions.
- Grant only the catalog and lineage viewer/producer permissions needed.
- Trigger a small known pipeline from a source table to a target table.
- Wait for ingestion/processing delay, then inspect the graph.
- Compare expected edges with displayed edges.
- Mark unsupported steps or missing edges; do not label lineage “complete” if a transformation is invisible.
- For custom systems, emit supported OpenLineage run events and validate dataset namespace/name mapping.
- Review lineage after renames, dataset moves, or pipeline redesigns.

### 9.4 Tie lineage to access reviews and incident response

When a source table becomes restricted or is scheduled for deletion, lineage identifies downstream consumers and jobs that may break or retain copies. Use lineage as an input to impact analysis, not as proof that all copies are known. External systems, exported files, caches, and manually copied datasets may not appear in the graph.

---

## 10. VPC Service Controls, CMEK, and sensitive-data protection

### 10.1 VPC Service Controls (VPC-SC)

VPC-SC creates a service perimeter around supported Google-managed services to reduce data-exfiltration risk. It complements IAM and can restrict access based on perimeter membership, ingress/egress rules, and access levels.

Use it when the threat model includes a valid credential being used to move data to an unauthorized resource. It is not a firewall for every network packet and is not a replacement for least-privilege IAM.

Operational guidance:
- Inventory every service and integration in the data path before creating a perimeter.
- Review the current supported-products list for BigQuery, BigQuery Data Policy, Cloud Storage, Dataflow, Dataproc, Composer/Airflow, KMS, logging, and related APIs.
- Use dry-run mode and inspect violations before enforcement.
- Plan ingress/egress rules explicitly for CI/CD, administrators, Composer workers, service accounts, data sources, and approved exports.
- Test console and API paths, scheduled transfers, cross-project sharing, and incident-response access.
- Keep break-glass access controlled and audited.
- Be aware that browser-local query results can be outside the service perimeter; remove export permissions such as `bigquery.tables.export` where appropriate if exports to local/Drive destinations violate policy.
- Do not assume every service, interface, connector, or third-party API is supported.

### 10.2 Customer-managed encryption keys (CMEK)

BigQuery encrypts data at rest by default. CMEK lets the customer control Cloud KMS key lifecycle, access, rotation, location, and auditability for supported resources. It introduces operational dependencies:
- the relevant BigQuery service identity needs permission to use the key;
- the KMS key must be in a supported compatible location;
- disabling/destroying the key or revoking access can make data unavailable;
- key use can add cost and operational latency;
- every resource and external source has its own encryption behavior.

CMEK is not column-level authorization. If a principal can query data and the service can decrypt it, that principal can still receive readable values. Use IAM, policy tags/masking, row policies, views, and monitoring for access decisions.

### 10.3 Sensitive Data Protection (formerly Cloud DLP)

Google's Sensitive Data Protection service (often still represented in APIs as `dlp`) can inspect supported storage such as BigQuery tables for configured infoTypes and produce findings. It can also de-identify data using supported transformations, including masking, tokenization, or cryptographic transformations, depending on the workflow.

A safe workflow:
1. Scan a small synthetic table with a documented inspection template.
2. Review findings and likelihoods; validate false positives and missed classes.
3. Classify columns and apply policy tags/access controls.
4. Use a supported de-identification workflow to create a sanitized output table where appropriate.
5. Verify output against re-identification risk and business utility.
6. Restrict access to findings tables; they can themselves contain sensitive metadata.
7. Set retention/deletion policy for scan outputs and temporary tables.

Detection is not automatic prevention. A successful scan does not classify every possible sensitive value, and de-identification is not guaranteed to make data anonymous in every context. Avoid writing raw values into logs or issue trackers.

### 10.4 Retention, deletion, residency, compliance

Define separate policies for:
- source and curated tables;
- streaming dead-letter topics and replay buckets;
- query results and temporary tables;
- audit logs and exported log datasets;
- Sensitive Data Protection findings;
- backups, snapshots, extracts, and downstream copies;
- encryption keys and key backups;
- catalog metadata and lineage.

Deletion must include derived copies and downstream systems where required. Table expiration alone does not delete exported files, log copies, or consumer extracts. Legal holds, regulatory retention duties, contractual obligations, and deletion rights may conflict; route conflicts to legal/privacy/security owners rather than improvising.

Data residency requires checking the actual resource location, replication and transfer paths, service-specific processing locations, log sinks, key locations, and external connectors. A region selected for one dataset does not automatically prove all processing and metadata stay in that jurisdiction. BigQuery Omni allows querying data in supported external cloud environments without first moving all source data into BigQuery managed storage, but supported locations, source systems, features, and cross-cloud control boundaries differ. Treat Omni as an architecture option requiring a separate residency, identity, networking, audit, and cost review.

---

## 11. Terraform-based policy management and access reviews

### 11.1 Policy-as-code operating model

1. Store Terraform in version control; protect the main branch and state.
2. Pin the Google provider version and review provider release notes.
3. Separate deployment identity from runtime identities.
4. Run `terraform fmt -check`, `terraform validate`, security checks, and `terraform plan`.
5. Review every IAM grant as a security change.
6. Apply only through an approved workflow.
7. Detect drift and investigate manual changes.
8. Run identity-level positive and negative tests after deployment.
9. Preserve audit evidence and the reviewed plan.
10. Destroy only lab-owned resources; never blindly apply `terraform destroy` to a shared project.

### 11.2 Terraform coverage and limits

Terraform supports many relevant resources, including project IAM bindings/members, BigQuery datasets/tables, Data Catalog/Dataplex taxonomy and policy-tag resources, and Dataplex data scans. Exact names and coverage depend on the Google provider version. Some fine-grained BigQuery configuration—such as attaching a policy tag to a column schema, creating a data policy/masking rule, or authorizing a view—may require a provider resource that is supported in the chosen version, a BigQuery API/CLI step, or a carefully controlled post-deployment script. Do not claim “all governance is in Terraform” unless the actual resources and state coverage support that claim.

If an API step is needed:
- make it idempotent;
- pin tool versions;
- avoid embedding credentials;
- record desired state;
- add a verification command;
- detect drift between Terraform and API-managed state;
- document teardown and import/adoption behavior.

### 11.3 Terraform example: taxonomy, tag, and scan

The following is an **illustrative partial Terraform baseline** for a disposable lab. It creates a policy-tag taxonomy, column-security and email-masking data policies with scoped IAM members, a dedicated scan service account, and a Dataplex data-quality scan. It does not, by itself, attach the tag to a BigQuery column, create the lab datasets/tables, configure row policies, or authorize a view. Those actions require the additional SQL/schema/API steps below and explicit consumer/table grants.

`experiments/09_governance/terraform/main.tf`:

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 9.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "Disposable Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Same region as the BigQuery dataset and policy-tag taxonomy."
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "Pre-created lab dataset containing synthetic sales."
  type        = string
  default     = "governance_lab"
}

variable "table_id" {
  description = "Synthetic BigQuery table ID."
  type        = string
  default     = "sales"
}

variable "raw_test_group_email" {
  description = "Existing, tightly controlled Google Group for the raw-column test identity."
  type        = string
}

variable "masked_analyst_group_email" {
  description = "Existing Google Group for the masked-only test identity."
  type        = string
}

resource "google_data_catalog_taxonomy" "sensitive" {
  project                = var.project_id
  region                 = var.region
  display_name           = "governance-lab-sensitive"
  description            = "Synthetic training data classification taxonomy."
  activated_policy_types = ["FINE_GRAINED_ACCESS_CONTROL"]
}

resource "google_data_catalog_policy_tag" "contact" {
  taxonomy     = google_data_catalog_taxonomy.sensitive.id
  display_name = "synthetic-contact"
  description  = "Synthetic contact field used to demonstrate column access."
}

# Raw access is deliberately granted only to the dedicated raw-test group.
resource "google_data_catalog_policy_tag_iam_member" "raw_reader" {
  policy_tag = google_data_catalog_policy_tag.contact.name
  role       = "roles/datacatalog.categoryFineGrainedReader"
  member     = "group:${var.raw_test_group_email}"
}

# Explicit column-level security data policy. The tag must be attached to the
# BigQuery column schema; this resource does not attach it by itself.
resource "google_bigquery_datapolicy_data_policy" "column_security" {
  project          = var.project_id
  location         = var.region
  data_policy_id   = "governance-contact-column-access"
  policy_tag       = google_data_catalog_policy_tag.contact.name
  data_policy_type = "COLUMN_LEVEL_SECURITY_POLICY"
}

# Optional masking path for the same policy tag. The tag must also be attached
# to customer_email in the BigQuery table schema before query-time masking applies.
resource "google_bigquery_datapolicy_data_policy" "email_mask" {
  project          = var.project_id
  location         = var.region
  data_policy_id   = "governance-email-mask"
  policy_tag       = google_data_catalog_policy_tag.contact.name
  data_policy_type = "DATA_MASKING_POLICY"

  data_masking_policy {
    predefined_expression = "EMAIL_MASK"
  }
}

resource "google_bigquery_datapolicy_data_policy_iam_member" "masked_reader" {
  project         = var.project_id
  location        = var.region
  data_policy_id  = google_bigquery_datapolicy_data_policy.email_mask.data_policy_id
  role            = "roles/bigquerydatapolicy.maskedReader"
  member          = "group:${var.masked_analyst_group_email}"
}

resource "google_service_account" "scan_runner" {
  project      = var.project_id
  account_id   = "governance-scan-runner"
  display_name = "Governance lab data-quality scan runner"
}

# The scan identity needs to read the source dataset and create BigQuery jobs.
# Keep these grants scoped to the lab dataset and the lab project respectively.
resource "google_bigquery_dataset_iam_member" "scan_data_reader" {
  project    = var.project_id
  dataset_id = var.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.scan_runner.email}"
}

resource "google_project_iam_member" "scan_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.scan_runner.email}"
}

resource "google_dataplex_datascan" "sales_quality" {
  project      = var.project_id
  location     = var.region
  data_scan_id = "governance-sales-quality"

  display_name = "Synthetic sales quality checks"
  description  = "Checks uniqueness, non-negative amounts, and valid regions."

  data {
    resource = "//bigquery.googleapis.com/projects/${var.project_id}/datasets/${var.dataset_id}/tables/${var.table_id}"
  }

  execution_spec {
    trigger {
      on_demand {}
    }
  }

  execution_identity {
    service_account {
      email = google_service_account.scan_runner.email
    }
  }

  data_quality_spec {
    sampling_percent          = 100
    catalog_publishing_enabled = true

    rules {
      name        = "order-id-unique"
      description = "Order IDs must be unique."
      dimension   = "UNIQUENESS"
      column      = "order_id"
      uniqueness_expectation {}
    }

    rules {
      name        = "amount-nonnegative"
      description = "Amount must be non-negative."
      dimension   = "VALIDITY"
      column      = "amount"
      row_condition_expectation {
        sql_expression = "amount IS NOT NULL AND amount >= 0"
      }
    }

    rules {
      name        = "region-approved"
      description = "Region must be one of the approved synthetic values."
      dimension   = "VALIDITY"
      column      = "region"
      row_condition_expectation {
        sql_expression = "region IN ('EAST', 'WEST', 'CENTRAL')"
      }
    }
  }
}
```

**Provider-schema and IAM notes:** Dataplex scan rule blocks and taxonomy resource names evolve. Before applying, compare the configuration with the current Terraform Registry schema for your pinned provider. The example explicitly provisions a scan service account with `roles/bigquery.dataViewer` on the lab dataset and `roles/bigquery.jobUser` on the lab project. The deployer also needs permissions to create the service account, grant those roles, create the taxonomy/tag and data policy, and create/manage the scan; do not solve a permission error by granting project Owner. If `row_condition_expectation` or another field is not accepted by your pinned provider, use the current documented schema rather than forcing an apply. A `terraform validate` pass is necessary but does not prove the cloud API will accept the resource.

`experiments/09_governance/terraform/variables.tfvars.example`:

```hcl
project_id                 = "REPLACE_WITH_DISPOSABLE_PROJECT_ID"
region                     = "us-central1"
dataset_id                 = "governance_lab"
table_id                   = "sales"
raw_test_group_email       = "REPLACE_WITH_EXISTING_RAW_TEST_GROUP"
masked_analyst_group_email = "REPLACE_WITH_EXISTING_MASKED_TEST_GROUP"
```

Commands:

```bash
cd experiments/09_governance/terraform
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file=variables.tfvars
# Review the plan carefully; only then:
terraform apply -var-file=variables.tfvars
```

Do not commit real project IDs if your repository policy forbids it, credentials, Terraform state, plan files, or generated sensitive findings. Terraform state can contain resource identifiers and configuration that should be treated as sensitive.

### 11.4 Policy-tag column attachment

BigQuery's `CREATE TABLE` DDL is not a general mechanism for setting policy tags. Use a supported table schema API or CLI path. One reproducible workflow is:

1. Create the taxonomy and policy tag.
2. Retrieve the policy-tag resource name from Terraform output or the API.
3. Export the table schema to JSON.
4. Add `policyTags.names` to the `customer_email` field's schema entry.
5. Update the table schema using the supported BigQuery API/CLI path.
6. Read the schema back and confirm the exact policy-tag resource is attached.
7. Test raw, masked, and denied identities.

Concrete schema-update workflow (run from an authenticated lab shell after exporting the real policy-tag resource name):

```bash
export TABLE_REF="${PROJECT_ID}:governance_lab.sales"
export POLICY_TAG_NAME="projects/PROJECT_NUMBER/locations/us-central1/taxonomies/TAXONOMY_ID/policyTags/POLICY_TAG_ID"

# Export the full current schema; never hand-build a partial schema for an existing table.
bq show --schema --format=prettyjson "$TABLE_REF" > schema.json
jq --arg tag "$POLICY_TAG_NAME" \
   'map(if .name == "customer_email" then . + {"policyTags":{"names":[$tag]}} else . end)' \
   schema.json > schema.updated.json
# Review the diff to ensure no fields were dropped or altered unexpectedly.
diff -u schema.json schema.updated.json
bq update "$TABLE_REF" schema.updated.json
# Read back and verify the policyTags.names value on customer_email.
bq show --schema --format=prettyjson "$TABLE_REF" > schema.after.json
jq '.[] | select(.name == "customer_email") | .policyTags' schema.after.json
```

Replace `POLICY_TAG_NAME` with the exact resource name returned by the API/Terraform, not a guessed ID. If `jq` is unavailable, use the console's schema editor or BigQuery Tables API. The taxonomy and table must be in the same location. Keep the full schema file and diff as controlled lab evidence, not as a substitute for an access test.

Example **schema fragment** (the full schema JSON must include every field):

```json
[
  {"name":"order_id","type":"STRING","mode":"REQUIRED"},
  {"name":"region","type":"STRING","mode":"REQUIRED"},
  {"name":"amount","type":"NUMERIC","mode":"REQUIRED"},
  {"name":"customer_email","type":"STRING","mode":"NULLABLE",
   "policyTags":{"names":["projects/PROJECT_NUMBER/locations/us-central1/taxonomies/TAXONOMY_ID/policyTags/POLICY_TAG_ID"]}}
]
```

The resource name must be the real name returned by the API, not a guessed ID. For CLI/schema-update details, follow the current BigQuery column-level security guide. Schema update methods can have side effects if the submitted schema omits fields; always export, modify minimally, review the diff, and read back after update.

### 11.5 Access reviews

At a recurring cadence and after role changes, review:
- direct and inherited IAM bindings;
- group membership and external identities;
- service-account keys, impersonation grants, and last use;
- dataset ACLs and table/view grants;
- policy-tag principals and masking policy bindings;
- row access policy grantees and filters;
- authorized views/datasets/routines and who can edit them;
- export permissions, cross-project sharing, VPC-SC exceptions;
- KMS key usage and key administrators;
- scan execution identities and log-sink writers;
- stale users, temporary grants, break-glass access, and exception expiry.

Each review should record reviewer, date, scope, evidence, decision, remediation owner, deadline, and closure evidence.

---

## 12. Cross-cloud, retention, deletion, and residency considerations

### 12.1 Cross-cloud governance

For BigQuery Omni or data held in other clouds, governance must span identity federation, cloud-native IAM, source storage permissions, network paths, query execution location, logging, key management, contractual terms, and support boundaries. A Google Cloud catalog view does not automatically replace the source cloud's access controls.

For each cross-cloud flow, document:
- source and destination ownership;
- identities used in each cloud;
- whether data is copied, cached, queried remotely, or materialized;
- where query execution and logs occur;
- egress paths and costs;
- encryption/key ownership;
- deletion and retention responsibilities;
- how lineage is captured across cloud boundaries;
- incident-response ownership and evidence access.

### 12.2 Retention and deletion

Set retention by data class and purpose, not by convenience. Configure table/partition expiration, Cloud Storage lifecycle, Pub/Sub retention, dead-letter retention, log buckets, scan findings, and derived outputs independently. Verify that expiration settings do not conflict with legal holds or mandatory retention.

A deletion runbook should inventory the source and derived copies, stop further ingestion, delete or expire resources as approved, handle backups/exports, preserve legally required evidence, and validate completion. Cryptographic erasure via key destruction may be appropriate only when all key dependencies and legal obligations are understood; it is not a generic shortcut.

### 12.3 Residency and compliance

Before selecting a location, verify service-specific regional availability, supported feature locations, replication behavior, metadata processing, logs, KMS key region, cross-region transfers, external data sources, and contractual requirements. A regional dataset alone is not sufficient evidence of residency.

Map requirements to controls and evidence. Examples include access review records, audit-log retention, key access logs, data-processing inventories, deletion evidence, quality results, and incident records. Have legal/privacy/security stakeholders determine the applicable obligations; do not state that any single Google Cloud service makes a workload “compliant.”

### 12.4 Mapping to Lake Formation and Unity Catalog

| Governance capability | Google Cloud pattern | AWS Lake Formation / IAM pattern | Databricks Unity Catalog pattern |
|---|---|---|---|
| Identity | Cloud IAM, federated identity, service accounts | IAM + Lake Formation grants | Workspace identity and account groups |
| Dataset/table access | BigQuery IAM and dataset access | Catalog/database/table permissions | Catalog/schema/table grants |
| Column access | Policy tags and data policies | Column-level grants where supported | Column masks and fine-grained controls |
| Row filtering | BigQuery row access policies | Row filters/data filters where supported | Row filters |
| Masking | BigQuery dynamic data masking | Service-specific masking patterns | Column masks |
| Metadata/catalog | Knowledge Catalog / Dataplex capabilities | Glue Data Catalog | Unity Catalog |
| Lineage | Data Lineage API and OpenLineage | Service-specific lineage integrations | Unity Catalog lineage |
| Perimeter | VPC Service Controls plus IAM | VPC/network controls and service policies | Cloud/network controls plus Unity Catalog |
| Key management | Cloud KMS/CMEK | AWS KMS | Cloud-specific KMS integrations |
| Quality | Catalog data-quality scans and pipeline gates | Glue Data Quality / custom checks | Lakehouse quality tools and expectations |

This is a conceptual mapping, not a one-to-one feature equivalence. Validate each platform's current capabilities and limitations.

---

## 13. Hands-on governance lab

The lab uses a small synthetic BigQuery table and demonstrates policy tags, masked/denied access, row filters, authorized views, catalog quality checks, audit evidence, and Sensitive Data Protection inspection. It is intentionally modular because taxonomy creation, policy-tag schema attachment, data-policy configuration, dataset authorization, and data scans can require different APIs and permissions.

### 13.1 Lab directory

```text
experiments/09_governance/
├── README.md
├── sql/
│   ├── 01-create-synthetic-data.sql
│   ├── 02-create-row-policies.sql
│   ├── 03-create-authorized-view.sql
│   ├── 04-validate-access.sql
│   └── 05-quality-diagnostics.sql
├── terraform/
│   ├── main.tf
│   └── variables.tfvars.example
└── evidence/
    └── evidence-template.md
```

The `main.tf` and example variable file are included in Section 11. Create these files in the stated paths if copying this lesson into your repository. The Terraform example is partial and requires provider-schema validation before deployment.

### 13.2 Prerequisites and APIs

Use a disposable project, `gcloud`, `bq`, Terraform, and an identity that is authorized to create only the lab resources. Enable only the APIs needed for the steps you will perform. Depending on the selected workflow, APIs can include:
- BigQuery API (`bigquery.googleapis.com`);
- Cloud Logging API (`logging.googleapis.com`);
- Data Catalog API (`datacatalog.googleapis.com`) for legacy-named taxonomy resources;
- Dataplex API (`dataplex.googleapis.com`) for scans/catalog workflows;
- Data Lineage API (`datalineage.googleapis.com`) if doing the optional lineage extension;
- Sensitive Data Protection API (`dlp.googleapis.com`);
- Cloud KMS API (`cloudkms.googleapis.com`) only for the optional CMEK extension;
- Cloud Resource Manager / IAM APIs needed for setup.

Do not enable every API merely because it appears in this list. Use the APIs required by your chosen lab path and organization policy.

### 13.3 Required roles: grant to dedicated lab identities

The exact minimum permissions vary with resource scope and the workflow. Use the current IAM role reference and the API's “required roles” page. Typical responsibilities:
- **Lab deployer:** narrowly scoped permissions to create/update the lab dataset/table, taxonomy/policy tag, data policies if configured, row policies, view authorization, and scan. This is a privileged setup identity, not an analyst.
- **Pipeline/scan execution identity:** source read and job/scan permissions required to execute the scan; no broad project administration.
- **Raw test identity:** table read plus explicit fine-grained access to the tagged column, only for the test.
- **Masked test identity:** table read plus the applicable masked-reader/data-policy grant; no raw policy-tag access.
- **Column-denied test identity:** table read plus a dedicated `TRUE`-filter row policy, but no policy-tag or masking grant; unprotected columns succeed and protected-column reads fail.
- **No-table-access identity:** no source table access and no row-policy grant; all table queries fail.
- **Region test identities:** table read plus membership in the corresponding row policy grantee list; no grant for the other region.
- **View consumer identity:** query-job permission in the consumer job project and read access to the approved view/destination dataset; no direct source table access.

Do not use the same principal for raw, masked, and denied tests. Otherwise the test does not demonstrate separate access outcomes.

### 13.4 Step A — Create synthetic data

`experiments/09_governance/sql/01-create-synthetic-data.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS `PROJECT_ID.governance_lab`
OPTIONS(location = 'us-central1');

CREATE OR REPLACE TABLE `PROJECT_ID.governance_lab.sales` (
  order_id STRING NOT NULL,
  region STRING NOT NULL,
  sale_date DATE NOT NULL,
  amount NUMERIC NOT NULL,
  customer_email STRING,
  customer_token STRING
);

INSERT INTO `PROJECT_ID.governance_lab.sales`
  (order_id, region, sale_date, amount, customer_email, customer_token)
VALUES
  ('ord_001', 'EAST', DATE '2026-01-05', 125.00, 'person001@example.invalid', 'tok_test_001'),
  ('ord_002', 'WEST', DATE '2026-01-06', 250.00, 'person002@example.invalid', 'tok_test_002'),
  ('ord_003', 'CENTRAL', DATE '2026-01-07', 90.00, 'person003@example.invalid', 'tok_test_003'),
  ('ord_004', 'EAST', DATE '2026-01-08', 75.00, 'person004@example.invalid', 'tok_test_004'),
  ('ord_005', 'WEST', DATE '2026-01-09', 310.00, 'person005@example.invalid', 'tok_test_005'),
  ('ord_006', 'EAST', DATE '2026-01-10', 42.00, 'person006@example.invalid', 'tok_test_006');

-- Create a sanitized source for the authorized-view exercise before row
-- policies are added. It contains no email/token columns and no row policies.
CREATE OR REPLACE TABLE `PROJECT_ID.governance_lab.sales_for_view` AS
SELECT region, sale_date, amount
FROM `PROJECT_ID.governance_lab.sales`;

-- A separate clean copy for deliberately failing data-quality rules.
-- Create it before row policies so it starts with all six synthetic rows.
CREATE OR REPLACE TABLE `PROJECT_ID.governance_lab.sales_quality_negative_test` AS
SELECT *
FROM `PROJECT_ID.governance_lab.sales`;
```

Replace `PROJECT_ID`. Run the script once. `CREATE OR REPLACE` and the insert are not idempotent together: rerunning the full script recreates the table and then inserts six rows, which is acceptable for this disposable lab but should not be copied as a production ingestion pattern.

### 13.5 Step B — Create a taxonomy and attach a policy tag

1. Apply the taxonomy/tag resources from Section 11 after verifying the current Terraform provider schema.
2. Record the returned taxonomy and policy-tag resource names.
3. Update the `customer_email` field schema with the returned tag resource name using the supported BigQuery schema update API/CLI workflow.
4. Read the table schema back and confirm that the policy tag is attached.
5. Confirm fine-grained access control is enforced for the taxonomy. The Terraform example grants `roles/datacatalog.categoryFineGrainedReader` only to the raw-test group and creates an `EMAIL_MASK` data policy with `roles/bigquerydatapolicy.maskedReader` granted to the masked-test group at the data-policy resource. Check that the group memberships are separate and that the masked group is not also a member of the raw group.
6. Attach the policy tag to the column before testing; creating a taxonomy, tag, or data policy alone does not protect an untagged column.

**Expected:** the schema shows the exact tag on `customer_email`; the raw principal can read that column only if explicitly granted; the masked principal receives the configured masked representation; the denied principal cannot read the protected value. If the masked path is not configured, it should fail rather than magically mask.

### 13.6 Step C — Create row access policies

`experiments/09_governance/sql/02-create-row-policies.sql`:

```sql
CREATE ROW ACCESS POLICY IF NOT EXISTS east_only
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:region-east@YOUR_TEST_DOMAIN")
FILTER USING (region = 'EAST');

CREATE ROW ACCESS POLICY IF NOT EXISTS west_only
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:region-west@YOUR_TEST_DOMAIN")
FILTER USING (region = 'WEST');

-- Keep column-security tests independent from regional filtering.
-- This group must contain only the dedicated raw-column test identity
-- and/or explicitly approved lab maintainers, never the EAST/WEST identities.
CREATE ROW ACCESS POLICY IF NOT EXISTS raw_test_full_access
ON `PROJECT_ID.governance_lab.sales`
GRANT TO (
  "group:governance-lab-raw@YOUR_TEST_DOMAIN",
  "serviceAccount:governance-scan-runner@PROJECT_ID.iam.gserviceaccount.com"
)
FILTER USING (TRUE);

-- A separate identity with table read access but no policy-tag grant proves
-- that column-level denial is independent of table/row denial.
CREATE ROW ACCESS POLICY IF NOT EXISTS column_denied_full_rows
ON `PROJECT_ID.governance_lab.sales`
GRANT TO ("group:governance-lab-column-denied@YOUR_TEST_DOMAIN")
FILTER USING (TRUE);
```

Replace the groups with real, separately controlled test groups in your disposable environment. Replace `PROJECT_ID` in the service-account principal with the actual project ID, and ensure Terraform has created that service account before running the SQL. `IF NOT EXISTS` makes first-time/repeated setup safer but does not update a pre-existing policy with a wrong filter; inspect existing policies and use `CREATE OR REPLACE ROW ACCESS POLICY` only after reviewing the security impact. Do not use placeholder identities as actual grants. All grantee identities must exist before the statement runs. Keep raw-test, column-denied, scan-runner, EAST, and WEST identities separate from one another. BigQuery combines multiple row policies additively (a union of rows covered by policies granted to the same principal), so overlapping memberships can broaden access.

Grant the row-test principals table read permission at the narrowest supported scope. Do not separately grant `roles/bigquery.filteredDataViewer`; the row access policy mechanism supplies the special filtered-data permission. A dedicated full-access/maintenance principal needs a `TRUE`-filter row policy if it must query all rows; otherwise it can be denied or see only rows covered by its assigned policies.

`experiments/09_governance/sql/04-validate-access.sql`:

```sql
-- Run separately as the EAST test identity:
SELECT region, COUNT(*) AS rows_visible, SUM(amount) AS amount_visible
FROM `PROJECT_ID.governance_lab.sales`
GROUP BY region;

-- Run separately as the WEST test identity:
SELECT region, COUNT(*) AS rows_visible, SUM(amount) AS amount_visible
FROM `PROJECT_ID.governance_lab.sales`
GROUP BY region;

-- Run as the authorized raw identity only:
SELECT order_id, customer_email
FROM `PROJECT_ID.governance_lab.sales`
ORDER BY order_id;

-- Run as the masked identity only after a masking data policy is configured:
SELECT order_id, customer_email
FROM `PROJECT_ID.governance_lab.sales`
ORDER BY order_id;

-- Run as the column-denied identity, which has table read access and a TRUE
-- row policy but no Fine-Grained Reader or Masked Reader grant:
SELECT order_id, region
FROM `PROJECT_ID.governance_lab.sales`;

-- This query must fail specifically because customer_email is protected:
SELECT customer_email
FROM `PROJECT_ID.governance_lab.sales`;

-- Run as the no-table-access identity, which has no table grant and no row policy:
SELECT order_id
FROM `PROJECT_ID.governance_lab.sales`;
```

**Expected outcomes:**
- EAST identity sees only EAST rows (three rows in the synthetic sample).
- WEST identity sees only WEST rows (two rows in the sample).
- The dedicated raw-column test identity and scan service account are granted the `TRUE` row policy so column testing and data-quality scanning are not confounded by regional filtering; the raw test identity sees all six synthetic rows only because it is a separate, explicitly privileged lab identity.
- The column-denied identity can read unprotected fields but cannot read `customer_email`; the no-table-access identity cannot query the table at all.
- Raw identity sees actual synthetic emails only when tag-level raw access is granted.
- Masked identity sees the configured masked output, if the data policy and masked-reader grant are correctly configured.
- Column-denied identity can query unprotected columns but receives an access error for `customer_email` because it has no Fine-Grained Reader or Masked Reader grant.
- The separate no-table-access identity fails on even an unprotected column because it lacks table access and is not granted a row policy.
- The scan service account is included in a dedicated `TRUE`-filter row policy so data-quality results cover the full table; keep that identity non-human and tightly scoped. If the Sensitive Data Protection workflow uses a separate service identity that is subject to row policies, grant only that scan identity the required row-policy access and verify it in the target project.

Use separate authenticated sessions (`gcloud auth login` with the test identity or approved impersonation) and capture the principal identity before each test. Never “test as” a principal by editing the intended role in the same admin session and assuming it is equivalent.

### 13.7 Step D — Create an authorized view

`experiments/09_governance/sql/03-create-authorized-view.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS `SHARE_PROJECT.approved_sales`
OPTIONS(location = 'us-central1');

CREATE OR REPLACE VIEW `SHARE_PROJECT.approved_sales.v_region_summary` AS
SELECT
  region,
  DATE_TRUNC(sale_date, MONTH) AS sale_month,
  SUM(amount) AS gross_amount,
  COUNT(*) AS order_count
FROM `SOURCE_PROJECT.governance_lab.sales_for_view`
GROUP BY region, sale_month;
```

Replace `SOURCE_PROJECT` and `SHARE_PROJECT`; source and view locations must be compatible for this query. The lab creates `sales_for_view` in Step A before row policies are applied; it contains only `region`, `sale_date`, and `amount`, so the authorized-view exercise is isolated from the row/column-policy tests. Create the view with an identity that can read this sanitized source table.

To add an **authorized-view entry** without overwriting existing dataset permissions, export the source dataset access configuration, append the view entry, inspect the diff, then update the dataset. The following is an illustrative `jq` workflow; preserve all existing access entries and review the output before applying:

```bash
bq show --format=prettyjson "${SOURCE_PROJECT}:governance_lab" > source-dataset.json
jq --arg p "$SHARE_PROJECT" \
   '.access = ((.access // []) + [{"view":{"projectId":$p,"datasetId":"approved_sales","tableId":"v_region_summary"}}])' \
   source-dataset.json > source-dataset.updated.json
# Review source-dataset.updated.json and confirm only the intended entry was added.
bq update --source=source-dataset.updated.json "${SOURCE_PROJECT}:governance_lab"
# Read back the dataset and confirm the authorized-view entry exists.
bq show --format=prettyjson "${SOURCE_PROJECT}:governance_lab" > source-dataset.after.json
```

Do not rerun the append blindly: repeated runs can duplicate entries. Check for an existing matching view entry first, and use the console/API if your `bq` version or dataset configuration differs. For authorized-dataset sharing, the source dataset access entry references the destination dataset rather than an individual view.

Grant the consumer read access to the destination view/dataset and `roles/bigquery.jobUser` in the project where their query job runs. Do **not** grant consumer read access to the source dataset/table.

**Validate as the view consumer:**

```sql
SELECT * FROM `SHARE_PROJECT.approved_sales.v_region_summary`;
```

Then run:

```sql
SELECT * FROM `SOURCE_PROJECT.governance_lab.sales_for_view`;
```

**Expected:** the view query succeeds; the direct source query is denied. If both succeed, investigate inherited IAM, project-wide roles, group membership, and source dataset access entries before considering the test successful.

### 13.8 Step E — Run a Dataplex data-quality scan

The Terraform example creates a scan with three expectations:
- unique `order_id`;
- non-negative/non-null `amount`;
- `region` in the approved set.

Expected clean-table outcome: all three rules pass against the six-row synthetic fixture. Expected negative-test outcome: after the single `amount = -1` update, the `amount-nonnegative` rule fails while the uniqueness and region rules remain passing. If the observed result differs, verify the scan points to the intended table and uses 100% sampling.

After validating and applying the current provider schema, run the on-demand scan and inspect its result:

```bash
gcloud dataplex datascans run governance-sales-quality \
  --location="$REGION" \
  --project="$PROJECT_ID"

# Identify the resulting job ID from the command output or scan job history,
# then replace JOB_ID with that exact ID:
gcloud dataplex datascans jobs describe JOB_ID \
  --location="$REGION" \
  --datascan=governance-sales-quality \
  --view=FULL \
  --project="$PROJECT_ID"
```

The scan resource is created by Terraform; the command above starts a run. Inspect the job in the catalog/Dataplex interface or use the FULL job description. Record total rows, passed/failed rules, score, and timestamp.
4. In the disposable negative-test copy created in Step A, inject one known defect and temporarily point the scan at that table:

   ```sql
   UPDATE `PROJECT_ID.governance_lab.sales_quality_negative_test`
   SET amount = -1
   WHERE order_id = 'ord_001';
   ```

   In the Terraform variables file, temporarily set `table_id = "sales_quality_negative_test"`, review the plan, and apply only in the disposable project. Run the scan again and confirm the `amount-nonnegative` rule fails. Then restore `table_id = "sales"`, apply the reviewed plan, and rerun the clean scan.
5. Delete the negative-test copy during cleanup; do not contaminate the primary lab table.
6. If notifications are required, configure the supported post-scan notification action and test delivery separately.

Do not insert a duplicate into the primary lab table if that would contaminate later access tests. Use a separate `sales_quality_negative_test` copy.

### 13.9 Step F — Inspect synthetic data with Sensitive Data Protection

Use the Sensitive Data Protection console or the following REST workflow to inspect `PROJECT_ID.governance_lab.sales`. This request uses Application Default Credentials via `gcloud` and does not embed a service-account key. Enable `dlp.googleapis.com`; the caller needs a role containing `dlp.jobs.create` (for example, `roles/dlp.user` where appropriate) and permission to use the project, and the inspection workflow must have the required BigQuery source access. Verify the service-specific permission requirements for the chosen execution identity. If exporting findings, create a dedicated restricted findings dataset and grant the DLP service identity the required write permission before enabling `saveFindings`.

Create `inspect-request.json` (replace `PROJECT_ID`):

```json
{
  "inspectJob": {
    "storageConfig": {
      "bigQueryOptions": {
        "tableReference": {
          "projectId": "PROJECT_ID",
          "datasetId": "governance_lab",
          "tableId": "sales"
        },
        "rowsLimit": "100"
      }
    },
    "inspectConfig": {
      "infoTypes": [{"name": "EMAIL_ADDRESS"}],
      "minLikelihood": "POSSIBLE",
      "limits": {"maxFindingsPerItem": 10}
    }
  }
}
```

Submit and capture the returned job name:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://dlp.googleapis.com/v2/projects/${PROJECT_ID}/dlpJobs" \
  --data-binary @inspect-request.json

# Use the exact returned job name, typically projects/PROJECT_ID/dlpJobs/JOB_ID.
curl -sS -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://dlp.googleapis.com/v2/${DLP_JOB_NAME}"
```

The job is asynchronous; poll the returned job resource until it reaches a terminal state, then inspect `inspectDetails.result.infoTypeStats` and any errors. This minimal request does not export raw findings to BigQuery. If you add a findings export, restrict its dataset and delete it according to the lab retention plan.

Because `example.invalid` addresses are synthetic, detector behavior can vary. If the scanner does not classify them, record that as a test limitation; do not replace them with real PII.

**Inspect:**
- job state and completion status;
- configured infoTypes and likelihood thresholds;
- count and location of findings;
- false positives and false negatives from the synthetic fixture;
- permissions on the findings dataset;
- retention/deletion of findings.

**Remediation options:**
- apply a policy tag and deny raw access to the original column;
- use dynamic masking for approved query-time visibility;
- create a sanitized table with a supported de-identification transform;
- remove an unnecessary sensitive column from curated outputs;
- restrict the findings dataset and delete temporary outputs according to the lab plan.

A scan result is not a data protection control until findings are triaged and the chosen remediation is applied and verified.

### 13.10 Step G — Audit evidence

Create a Cloud Logging sink to a restricted BigQuery dataset for relevant BigQuery and policy-tag audit events. Enable Data Access logs for the needed services if not already enabled and permitted by the organization. Query the actual exported schema using the adaptation guidance in Section 6.

Evidence to capture:
- identity used for each positive and negative test;
- policy tag attached to `customer_email`;
- raw/masked/denied query results or error details;
- EAST and WEST row results;
- authorized-view success and source-table denial;
- data-quality scan job and rule-level result;
- Sensitive Data Protection job status and findings summary;
- audit events for the policy and query operations;
- Terraform plan/apply logs with secrets redacted.

Never include raw values, access tokens, service-account keys, or unredacted sensitive findings in the evidence file.

### 13.11 Step H — Cleanup

Before cleanup, preserve only approved, redacted evidence. Then:
1. Remove the row access policies.
2. Remove the authorized view and its dataset authorization.
3. Remove data policies and policy-tag bindings as applicable.
4. Delete the lab tables/datasets and findings dataset.
5. Delete the data scan and taxonomy/tag only if they are lab-owned and no other resource depends on them.
6. Remove temporary IAM grants and test group membership.
7. Remove or disable lab-only log sinks and log buckets only if safe and approved; audit logs may be subject to retention requirements.
8. Run `terraform destroy` only from the lab Terraform directory after reviewing the plan.
9. Verify remaining resources, IAM grants, keys, logs, and storage manually.

Example SQL cleanup (run only in the disposable lab):

```sql
DROP ALL ROW ACCESS POLICIES ON `PROJECT_ID.governance_lab.sales`;
DROP VIEW IF EXISTS `SHARE_PROJECT.approved_sales.v_region_summary`;
DROP TABLE IF EXISTS `PROJECT_ID.governance_lab.sales_quality_negative_test`;
DROP TABLE IF EXISTS `PROJECT_ID.governance_lab.sales_for_view`;
DROP TABLE IF EXISTS `PROJECT_ID.governance_lab.sales`;
```

Delete datasets through the console/`bq`/API after checking that they contain only lab-owned objects. Deleting a dataset with contents may require an explicit recursive-delete option. Do not use broad recursive deletion on a shared dataset.

### 13.12 Cost and security warnings

- BigQuery query charges depend on pricing model, bytes processed, reservations, and region. Keep tables tiny and use dry runs/maximum bytes billed where supported.
- Data scans, Sensitive Data Protection jobs, Cloud Logging ingestion/retention, KMS operations, and VPC-SC configuration/operations may incur costs.
- VPC Service Controls can disrupt console, CI/CD, orchestration, and data transfers if ingress/egress paths are incomplete. Use a dedicated organization sandbox and dry-run first.
- Policy-tag and IAM changes can take time to propagate. Do not treat an immediate stale result as definitive proof.
- A `terraform apply` may create billable resources or broad permissions. Review the plan and provider schema before applying.
- Never use a production project or real PII for this exercise.

---

## 14. Troubleshooting and common security mistakes

| Symptom | Likely cause | Safe investigation |
|---|---|---|
| Analyst can query a tagged column | Taxonomy enforcement off, tag not attached to the actual field, inherited raw grant, wrong identity, or cached/propagating permissions | Read back schema, inspect tag IAM/enforcement, inspect inherited IAM, use a controlled query and verify principal |
| Masked identity receives raw value | Masking data policy not attached/configured, identity has raw access, wrong policy-tag grant, or mask semantics misunderstood | Inspect tag, data policy, bindings, and actual principal; revoke unintended raw access and retest |
| Row policy returns zero rows | Wrong region spelling, group identity mismatch, no table read grant, policy expression mismatch, or identity not in grantee list | Check identity, table access, policy SQL and row values; use admin inspection without granting broader access |
| Row policy returns too many rows | Overlapping row policies/grantees or broad IAM/admin access | Inspect every policy and effective membership; test each identity separately |
| Authorized view returns access denied | View not authorized on source dataset, consumer lacks view access or job creation, incompatible location, or view creator lacks source access | Verify source authorization entry, destination access, job project, and locations |
| Consumer can read source table | Inherited project/dataset grant or group membership grants direct access | Trace effective IAM and dataset access; remove the excessive grant, then rerun negative test |
| No data-access logs found | Data Access logging disabled, sink filter excludes events, wrong project/log scope, wrong retention, or query uses wrong schema | Verify service audit config, sink inclusion, Logs Explorer event first, then inspect exported schema |
| Policy-tag Terraform resource applies but field is unprotected | Taxonomy/tag exists but schema attachment or enforcement not configured | Read back schema and enforcement state; verify actual query behavior |
| Scan fails to start | Missing API, scan execution identity lacks read/metadata permissions, location mismatch, invalid rule schema/provider version | Read scan error details, confirm current Terraform schema and API prerequisites; add only the missing minimum permission |
| Scan passes despite known bad row | Rule not checking intended rows/column, sample omitted bad rows, expression wrong, or scan is a different table | Confirm 100% sampling for tiny lab, inspect rule definition/table resource, inject defect into test copy |
| Lineage is incomplete | Unsupported connector/SDK, API disabled, job-level setting off, ingestion delay, or custom job emits no event | Check integration support, job settings, permissions, event mapping, and wait for processing |
| VPC-SC blocks a legitimate job | Missing ingress/egress/service configuration or unsupported API path | Use dry-run violation logs and supported-product matrix; don't disable the perimeter globally |
| CMEK resource fails | Key location mismatch, BigQuery service identity lacks key access, key disabled, or incompatible resource | Confirm location and KMS IAM for the correct BigQuery service identity |
| Sensitive Data Protection finds nothing | Wrong table/location/infoTypes, low likelihood threshold, synthetic format not detected, or job not complete | Inspect job config and status; use known synthetic fixtures and document detector limits |
| Terraform destroys unrelated resources | Wrong workspace/project/state or overly broad configuration | Stop before apply/destroy, check `terraform workspace show`, provider project, state, and full plan |

### Common mistakes to avoid

- Giving analysts project-wide `roles/editor` or `roles/bigquery.admin`.
- Assuming job creation permission implies data read permission.
- Treating a policy tag as effective before attaching it to the schema and testing enforcement.
- Confusing masked access with raw access, or assuming hashing guarantees anonymity.
- Applying a row policy without separately considering table access and overlapping policies.
- Assuming a view is authorized because it was created.
- Authorizing a whole dataset without controlling who can create future views in it.
- Authorizing stored procedures without reviewing their DDL/DML behavior.
- Assuming audit logs capture every event when Data Access logs are disabled or retention is insufficient.
- Treating catalog metadata as access enforcement.
- Treating a passing data-quality scan as a complete correctness/security proof.
- Assuming lineage covers unsupported services and manual copies.
- Treating VPC-SC as a replacement for IAM or as a control for data already exported to a user's browser.
- Treating CMEK as a way to prevent authorized queries from reading plaintext.
- Running a DLP scan but not triaging findings or protecting the findings dataset.
- Hand-editing IAM in the console without reconciliation to Terraform state.
- Forgetting to clean up keys, grants, scans, findings, datasets, log sinks, or test identities.

---

## 15. Knowledge checks with detailed answers

### Q1. Why does `roles/bigquery.jobUser` not let an analyst read every BigQuery table?

**Answer:** It grants job-creation permission in the relevant project. Data read permissions are evaluated separately on the referenced tables/views, including inherited grants, dataset access, and fine-grained controls. A valid design grants job creation in the job project and data access only to approved resources.

### Q2. What is the difference between policy tags and dynamic data masking?

**Answer:** Policy tags classify columns and support column-level access enforcement. Dynamic masking adds a data policy that controls the representation returned to eligible principals. A tag without the expected access configuration does not automatically produce a mask; a masking rule does not replace table IAM or row filtering.

### Q3. Why must a row-policy grantee also have table data access?

**Answer:** Row access policies filter data for a principal that already has permission to read the table. The policy supplies the special filtered-data permission, but does not independently grant all table access. A principal on the grantee list without table read permission still receives an access error.

### Q4. What is the main risk of authorizing a dataset rather than one view?

**Answer:** All current and future views in the authorized dataset can access the shared dataset. The ability to create or alter views in that dataset becomes security-sensitive. Restrict view-authoring rights and review changes.

### Q5. Which logs are usually needed to investigate a data read?

**Answer:** BigQuery Data Access audit logs, relevant Admin Activity logs for permission/configuration changes, and potentially Policy Denied/VPC-SC violation logs. Data Access logging may need explicit enablement. Confirm the event is emitted, routed, retained, and queryable before relying on it.

### Q6. Does a catalog entry mean that the asset is secured?

**Answer:** No. Catalog metadata supports discovery, semantics, ownership, quality, and lineage. Actual access is enforced by IAM and service-specific controls such as BigQuery policy tags, data policies, row access policies, views, and VPC Service Controls.

### Q7. Why is a data-quality score not a guarantee of good data?

**Answer:** It reflects the rules, population, sampling, and execution at a point in time. Unchecked failure modes, poor rules, sampling, late data, or semantic defects can remain. Define explicit rules, monitor results, and gate downstream publication where necessary.

### Q8. What does VPC Service Controls add beyond IAM?

**Answer:** IAM controls which principals can perform which actions. VPC-SC adds a service perimeter and ingress/egress constraints to reduce data exfiltration across supported Google-managed services. They are complementary; VPC-SC does not replace fine-grained IAM or fix exports already outside the perimeter.

### Q9. Why doesn't CMEK prevent an authorized analyst from reading PII?

**Answer:** CMEK governs encryption-key control and service ability to decrypt stored data. When BigQuery is authorized to decrypt and the principal is authorized to query the column, the query can return plaintext. Column/row controls, masking, views, and IAM are still required.

### Q10. What is the difference between data discovery and Sensitive Data Protection inspection?

**Answer:** Catalog discovery extracts technical metadata and makes assets discoverable. Sensitive Data Protection inspection scans data content for configured sensitive-data patterns/infoTypes. Both can be incomplete; findings need validation, classification, access control, and remediation.

### Q11. Why can a lineage graph be incomplete even if the Data Lineage API is enabled?

**Answer:** Lineage capture depends on supported integrations, job settings, versions, permissions, and processing delays. Custom pipelines may need OpenLineage events. Manual copies, external systems, and unsupported connectors can remain invisible.

### Q12. Why should IAM changes be tested using separate identities?

**Answer:** Testing from an administrator can succeed because of broad inherited privileges, masking a broken least-privilege configuration. Separate principals prove intended positive and negative paths. Record the identity and actual resource/error for every test.

### Q13. What is required before declaring a residency control effective?

**Answer:** Validate actual locations and supported regional capabilities for data, metadata, logs, keys, transfers, external sources, and processing. Document contractual/legal requirements and exceptions. One regional dataset setting is not sufficient evidence.

### Q14. How should a quality failure affect a production pipeline?

**Answer:** Define severity and a gate. Critical failures should quarantine the affected batch or prevent publication, alert the owner, preserve evidence, and support controlled replay after remediation. Do not silently drop bad rows or assume the scan itself blocks downstream tasks.

### Q15. What does policy-as-code actually mean?

**Answer:** Desired access/configuration is reviewed, versioned, reproducibly deployed, tested, and monitored for drift. A Terraform file alone is not proof that every policy is managed or enforced. Identify any API/CLI-managed settings, add verification, and reconcile them with the desired state.

---

## 16. Syllabus checkpoint and module exit criteria

### Topic 09 checkpoint

- [ ] Explain IAM at project, dataset, table, and column level, including inherited permissions.
- [ ] Distinguish predefined roles, custom roles, job creation, data access, and service-account impersonation.
- [ ] Explain dataset access, authorized views, authorized datasets, and authorized routines.
- [ ] Distinguish Admin Activity and Data Access logs; identify how to route and query logs in BigQuery.
- [ ] Create a policy-tag taxonomy and attach a tag to a sensitive synthetic column.
- [ ] Verify raw, masked, and denied access with separate identities.
- [ ] Create a row access policy and demonstrate regional filtering.
- [ ] Publish an authorized view and prove the consumer cannot read the source table directly.
- [ ] Explain Dataplex Universal Catalog / Knowledge Catalog terminology, metadata, search, glossary, and domain/product governance.
- [ ] Configure a data-quality scan with at least three meaningful rules, inspect failures, and describe a quality gate.
- [ ] Explain profiling and Data Lineage API/OpenLineage limitations.
- [ ] Explain VPC-SC, CMEK, and Sensitive Data Protection without conflating their purposes.
- [ ] Describe Terraform-managed policy resources, API-managed gaps, drift, and access reviews.
- [ ] Explain cross-cloud governance, BigQuery Omni, retention, deletion, residency, and compliance caveats.
- [ ] Clean up lab resources and temporary IAM grants.

### Module exit criteria (Topics 01–09)

This topic closes the GCP data-engineering module. The module mini-project should satisfy the roadmap's requirements:
- Batch: GCS → BigQuery → Dataform or scheduled-query transformations.
- Streaming: Pub/Sub → Dataflow/Beam with dead-letter handling → partitioned/clustered BigQuery tables.
- Spark: one Dataproc Serverless enrichment job.
- Orchestration: Composer DAG for the batch path with quality gates.
- Governance: policy tags, row access, catalog quality scan, and lineage.
- Cost: dry-run guardrails, `maximum_bytes_billed`, budget alert, and top-query report.
- Infrastructure: Terraform plus a README and architecture diagram.
- Completion: the platform can be recreated from scratch through a documented workflow, bad data is quarantined, PII is masked for analysts, and the bill is explained.

Do not claim completion based on configuration files alone. Demonstrate the positive and negative access tests, scan result, lineage graph, and cost evidence. Keep a short verification record in `module-2c4-notes.md`.

---

## 17. Official documentation references

Use the current documentation for product labels, API schemas, IAM roles, and Terraform provider behavior. Product names and APIs evolve; recheck these references before deploying.

### BigQuery access controls
- [Column-level access control](https://cloud.google.com/bigquery/docs/column-level-security)
- [Dynamic data masking](https://cloud.google.com/bigquery/docs/column-data-masking)
- [BigQuery tags and data policies](https://cloud.google.com/bigquery/docs/tags)
- [Row-level security overview](https://cloud.google.com/bigquery/docs/row-level-security-intro)
- [Manage row-level security](https://cloud.google.com/bigquery/docs/managing-row-level-security)
- [Authorized views and datasets](https://cloud.google.com/bigquery/docs/authorized-datasets)
- [Authorized routines](https://cloud.google.com/bigquery/docs/authorized-routines)
- [BigQuery access-control troubleshooting](https://cloud.google.com/bigquery/docs/troubleshoot-access-control)

### Audit logging
- [BigQuery audit logs](https://cloud.google.com/bigquery/docs/reference/auditlogs)
- [Audit policy tags](https://cloud.google.com/bigquery/docs/auditing-policy-tags)
- [BigQuery Data Policy audit logging](https://cloud.google.com/bigquery/docs/column-data-masking-audit-logging)
- [Cloud Audit Logs overview](https://cloud.google.com/logging/docs/audit)

### Catalog, quality, lineage
- [Knowledge Catalog documentation (formerly Dataplex Universal Catalog)](https://cloud.google.com/dataplex/docs)
- [Business glossary](https://cloud.google.com/dataplex/docs/create-glossary)
- [Data quality scans](https://cloud.google.com/dataplex/docs/use-auto-data-quality)
- [OpenLineage integration](https://cloud.google.com/dataplex/docs/open-lineage)
- [Dataflow lineage](https://cloud.google.com/dataflow/docs/guides/lineage)
- [Terraform `google_dataplex_datascan`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dataplex_datascan)
- [Terraform `google_data_catalog_taxonomy`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/data_catalog_taxonomy)
- [Terraform `google_data_catalog_policy_tag`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/data_catalog_policy_tag)
- [Terraform BigQuery Data Policy](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_datapolicy_data_policy)
- [Terraform policy-tag IAM](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/data_catalog_policy_tag_iam)
- [Terraform BigQuery Data Policy IAM](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_datapolicy_data_policy_iam)

### Perimeter, encryption, sensitive data
- [VPC Service Controls overview](https://cloud.google.com/vpc-service-controls/docs/overview)
- [VPC Service Controls for BigQuery](https://cloud.google.com/bigquery/docs/vpc-sc)
- [Supported products and limitations](https://cloud.google.com/vpc-service-controls/docs/supported-products)
- [BigQuery CMEK](https://cloud.google.com/bigquery/docs/customer-managed-encryption)
- [Sensitive Data Protection inspection of storage and databases](https://cloud.google.com/sensitive-data-protection/docs/inspecting-storage)
- [Sensitive Data Protection with BigQuery](https://cloud.google.com/sensitive-data-protection/docs/dlp-bigquery)
- [BigQuery de-identification tutorial](https://cloud.google.com/sensitive-data-protection/docs/deidentify-bq-tutorial)

### Operational references
- [Google Cloud IAM overview](https://cloud.google.com/iam/docs/overview)
- [BigQuery INFORMATION_SCHEMA jobs](https://cloud.google.com/bigquery/docs/information-schema-jobs)
- [BigQuery locations](https://cloud.google.com/bigquery/docs/locations)
- [BigQuery Omni](https://cloud.google.com/bigquery/docs/omni-introduction)
- [Google provider Terraform Registry](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

---

## Private verification record (for lesson maintenance; not a learner completion certificate)

**Source alignment checked:** Topic 09 in `roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md` and target path in `Roadmap_ptree.md`. Covered the required basics/intermediate/advanced concepts, learning sequence, hands-on steps, checkpoint, common mistakes, and module mini-project handoff.

**Technical review performed:** Current official Google Cloud documentation and Terraform Registry pages were consulted for column-level security/policy tags, masking, row access policies, authorized datasets/routines, BigQuery audit logs, catalog/data quality/lineage/OpenLineage, Sensitive Data Protection, VPC Service Controls, CMEK, and Terraform scan/taxonomy resources.

**Important limitations:** No live Google Cloud deployment, `terraform apply`, IAM permission test, BigQuery query, DataScan execution, Sensitive Data Protection job, audit-log export, or lineage capture was performed while authoring this file. Terraform schema examples are explicitly marked for validation against the pinned provider because provider/API schemas evolve. The policy-tag schema attachment, masking data-policy creation, dataset authorization, audit-log sink, and DLP scan require separate documented steps and are not implied to be completed by the partial Terraform baseline.

**Pre-delivery self-audit:** all 17 requested lesson sections present; all named syllabus areas addressed; synthetic-only lab and cleanup included; distinction between prevention, masking, encryption, perimeter, metadata, and quality explicit; no claim of live validation or compliance certification made.
